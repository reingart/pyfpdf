# -*- coding: utf-8 -*-

"Test caching"

#PyFPDF-cover-test:res=font/DejaVuSansCondensed.ttf
#PyFPDF-cover-test:res=font/DejaVuSans.ttf

import common
from fpdf import FPDF

import os, shutil, time

def dotest(outputname, nostamp):
    cachepath = os.path.join(os.path.dirname(__file__), "cache")
    if os.path.exists(cachepath):
        # cleanup dest
        for item in os.listdir(cachepath):
            os.remove(os.path.join(cachepath, item))
    else:
        # create font dir
        os.makedirs(cachepath)
    # copy font files    
    shutil.copy(os.path.join(common.basepath, "font", "DejaVuSansCondensed.ttf"), cachepath)
    shutil.copy(os.path.join(common.basepath, "font", "DejaVuSans.ttf"), cachepath)
    f1 = os.path.join(cachepath, "DejaVuSansCondensed.ttf")
    f2 = os.path.join(cachepath, "DejaVuSans.ttf")
    # create pdf
    pdf1 = FPDF()
    # cache files
    t0 = time.time()
    pdf1.add_font('DejaVuSansCondensed', '', f1, uni = True)
    pdf1.add_font('DejaVuSans', '', f2, uni = True)
    t1 = time.time()
    # test pkl
    assert os.path.exists(f1[:-3] + "pkl")
    assert os.path.exists(f2[:-3] + "pkl")
    # load cached
    pdf2 = FPDF()
    t2 = time.time()
    pdf2.add_font('DejaVuSansCondensed', '', f1, uni = True)
    pdf2.add_font('DejaVuSans', '', f2, uni = True)
    t3 = time.time()
    if not nostamp:
        common.log("Cache fonts: ", t1 - t0)
        common.log("Reload fonts:", t3 - t2)
    #     
    
if __name__ == "__main__":
    common.testmain(__file__, dotest)

