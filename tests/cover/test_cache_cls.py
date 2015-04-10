# -*- coding: utf-8 -*-

"Test new caching classes"

#PyFPDF-cover-test:res=font/DejaVuSansCondensed.ttf
#PyFPDF-cover-test:res=font/DejaVuSans.ttf

import sys, os, shutil, time
import gzip
from hashlib import md5

import common
import fpdf

def testfile(f1, f2, cache):
    # create pdf
    pdf = fpdf.FPDF()
    pdf.set_cache(cache)
    if f1:
        pdf.add_font('DejaVuSansCondensed', '', f1, uni = True)
    if f2:
        pdf.add_font('DejaVuSans', '', f2, uni = True)
        pdf.set_font('DejaVuSans', "", 10)
    return pdf

def trashfile(fn):
    f = open(fn, "w")
    f.write("1234567890")
    f.close()

def hashfn(fn):
    h = md5()
    fn = os.path.abspath(fn)
    if common.PY3K:
        h.update(fn.encode("UTF-8"))
    else:
        h.update(fn)
    return h.hexdigest()

class CacheGzip(fpdf.HashCache):
    # Load cached        
    def load_cache(self, filename, ttf = None):
        if not filename:
            return None
        try:
            fh = gzip.GzipFile(filename + ".gz", "rb")
            try:
                data = fpdf.py3k.pickle.load(fh)
                if ttf:
                    assert data["TTF_PATH"] == ttf
                return data
            finally:
                fh.close()
        except (IOError, ValueError, AssertionError):
            return None

    # Note: if standard cache loaded, then save_cache will not be called
    def save_cache(self, filename, data, ttf = None):
        if not filename:
            return None
        try:
            fh = gzip.GzipFile(filename + ".gz", "wb", compresslevel = 1)
            try:
                if ttf:
                    data["TTF_PATH"] = ttf
                fpdf.py3k.pickle.dump(data, fh)
            finally:
                fh.close()
        except Exception as e:  
            return None

@common.add_unittest
def dotest(outputname, nostamp):
    cachepath = os.path.join(os.path.dirname(__file__), "cache")
    if os.path.exists(cachepath):
        # cleanup dest
        for item in os.listdir(cachepath):
            os.remove(os.path.join(cachepath, item))
    else:
        # create font dir
        os.makedirs(cachepath)
    hashpath = os.path.join(os.path.dirname(__file__), "hash")
    if os.path.exists(hashpath):
        # cleanup dest
        for item in os.listdir(hashpath):
            os.remove(os.path.join(hashpath, item))
    else:
        # create font dir
        os.makedirs(hashpath)
    # copy font files
    shutil.copy(os.path.join(common.basepath, "font", "DejaVuSansCondensed.ttf"), cachepath)
    shutil.copy(os.path.join(common.basepath, "font", "DejaVuSans.ttf"), cachepath)
    f1 = os.path.join(cachepath, "DejaVuSansCondensed.ttf")
    f2 = os.path.join(cachepath, "DejaVuSans.ttf")

    # --- normal cache mode ---
    # first load
    t0 = time.time()
    pdf = testfile(f1, f2, fpdf.StdCache())
    t1 = time.time()
    assert os.path.exists(f1[:-3] + "pkl"), "Pickle for DejaVuSansCondensed not found"
    assert os.path.exists(f2[:-3] + "pkl"), "Pickle for DejaVuSans not found"
    # load cached
    t2 = time.time()
    pdf = testfile(f1, f2, fpdf.StdCache())
    t3 = time.time()
    if not nostamp:
        common.log("Cache fonts:  ", t1 - t0)
        common.log("Reload fonts: ", t3 - t2)
    pdf.add_page()
    # trigger cw127
    #pdf.write(5, "Γειά σου κόσμος")
    pdf.write(5, "Привет!")
    pdf.write(10, "Hello")
    pdf.output(os.path.join(cachepath, "pdf0.pdf"), "F")
    # check cw127
    assert not os.path.exists(f1[:-3] + "cw127.pkl"), "Cw127 for DejaVuSansCondensed not found"
    assert os.path.exists(f2[:-3] + "cw127.pkl"), "Unnecessary cw127 for DejaVuSans"
        
    # --- disable cache reading ---
    # put garbage data to cache files - fpdf should not read pkl
    trashfile(f1[:-3] + "pkl")
    trashfile(f2[:-3] + "pkl")
    trashfile(f2[:-3] + "cw127.pkl")
    # test same file
    t0 = time.time()
    pdf = testfile(f1, f2, fpdf.NoneCache())
    t1 = time.time()
    # remove pkl files
    os.remove(f1[:-3] + "pkl")
    os.remove(f2[:-3] + "pkl")
    os.remove(f2[:-3] + "cw127.pkl")
    # test reload
    t2 = time.time()
    pdf = testfile(f1, f2, fpdf.NoneCache())
    t3 = time.time()
    if not nostamp:
        common.log("No cache 1st: ", t1 - t0)
        common.log("No cache 2nd: ", t3 - t2)
    pdf.add_page()
    pdf.write(5, "Γειά σου κόσμος")
    pdf.write(10, "Hello")
    pdf.output(os.path.join(cachepath, "pdf1.pdf"), "F")
    # test no files created
    assert not os.path.exists(f1[:-3] + "pkl"), "Unnecessary file DejaVuSansCondensed.pkl"
    assert not os.path.exists(f2[:-3] + "pkl"), "Unnecessary file DejaVuSans.pkl"
    assert not os.path.exists(f1[:-3] + "cw127.pkl"), "Unnecessary file DejaVuSansCondensed.127.pkl"
    assert not os.path.exists(f2[:-3] + "cw127.pkl"), "Unnecessary file DejaVuSans.127.pkl"

    # --- hash cache ---
    t0 = time.time()
    pdf = testfile(f1, f2, hashpath)
    t1 = time.time()
    assert not os.path.exists(f1[:-3] + "pkl"), "Misplaced file DejaVuSansCondensed.pkl"
    assert not os.path.exists(f2[:-3] + "pkl"), "Misplaced file DejaVuSans.pkl"
    # load cached
    t2 = time.time()
    pdf = testfile(f1, f2, hashpath)
    t3 = time.time()
    # test reload
    if not nostamp:
        common.log("Hash load 1st:", t1 - t0)
        common.log("Hash load 2nd:", t3 - t2)
    # check hash
    h1 = os.path.join(hashpath, hashfn(f1) + ".pkl")
    h2 = os.path.join(hashpath, hashfn(f2) + ".pkl")
    assert os.path.exists(h1), "Cached pickle for DejaVuSansCondensed not found"
    assert os.path.exists(h2), "Cached pickle for DejaVuSans not found"            
    pdf.add_page()
    pdf.write(5, "Хешировали, хешировали, да выдохешировали.")
    pdf.write(10, "Hello")
    pdf.output(os.path.join(cachepath, "pdf2.pdf"), "F")
    assert not os.path.exists(h1[:-3] + "cw127.pkl"), "Unnecessary cached cw127 for DejaVuSansCondensed "
    assert os.path.exists(h2[:-3] + "cw127.pkl"), "Cached cw127 for DejaVuSans not found"
    

    # --- test gzip ---
    # remove cached files from HashCache
    os.remove(h1)
    os.remove(h2)
    os.remove(h2[:-3] + "cw127.pkl")
    cgz = CacheGzip(cache_dir = hashpath)
    t0 = time.time()
    pdf = testfile(f1, f2, cgz)
    t1 = time.time()
    assert not os.path.exists(h1), "Misplaced hash file DejaVuSansCondensed.pkl"
    assert not os.path.exists(h2), "Misplaced hash file DejaVuSans.pkl"

    # load cached
    t2 = time.time()
    pdf = testfile(f1, f2, cgz)
    t3 = time.time()
    # test reload
    if not nostamp:
        common.log("Gzip hash 1st:", t1 - t0)
        common.log("Gzip hash 2nd:", t3 - t2)
    # check hash
    assert os.path.exists(h1 + ".gz"), "Gzip cached pickle for DejaVuSansCondensed not found"
    assert os.path.exists(h2 + ".gz"), "Gzip cached pickle for DejaVuSans not found"            
    pdf.add_page()
    pdf.write(5, "Сжимай! Сжимаю, сжал")
    pdf.write(10, "Hello")
    pdf.output(os.path.join(cachepath, "pdf3.pdf"), "F")
    assert not os.path.exists(h1[:-3] + "cw127.pkl.gz"), "Unnecessary gzip cached cw127 for DejaVuSansCondensed "
    assert os.path.exists(h2[:-3] + "cw127.pkl.gz"), "Gzip cached cw127 for DejaVuSans not found"

if __name__ == "__main__":
    common.testmain(__file__, dotest)

