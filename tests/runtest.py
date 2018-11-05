#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement

import os, sys
import cover
import shutil
import traceback

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

def search_python_posix():
    lst = []
    path = os.environ.get("PATH")
    for item in path.split(":"):
        try:
            for interp in os.listdir(item):
                if interp[:6] != "python":
                    continue
                if interp[-7:] == "-config":
                    continue
                fp = os.path.join(item, interp)
                # test if already in list
                same = False
                for lidx, l_interp in enumerate(lst):
                    if os.path.samefile(l_interp, fp):
                        same = True
                        # use shorter name
                        if len(l_interp) < len(fp):
                            lst[lidx] = fp
                        break
                if same:
                    continue
                lst.append(fp)
        except OSError:
            pass
    return lst

def search_python_win():
    lst = []
    try:
        try:
            import _winreg as winreg
        except ImportError:
            import winreg
        def findreg(key, lst):
            PATH = "SOFTWARE\\Python\\PythonCore"
            try:
                rl = winreg.OpenKey(key, PATH)
            except WindowsError:
                return lst
            try:
                for i in range(winreg.QueryInfoKey(rl)[0]):
                    ver = winreg.EnumKey(rl, i)
                    rv = winreg.QueryValue(key, PATH + "\\" + ver + "\\InstallPath")
                    fp = os.path.join(rv, "python.exe")
                    #print(fp)
                    if os.path.exists(fp) and not fp in lst:
                        lst.append(fp)
            except WindowsError:
                pass
            return lst
        lst = findreg(winreg.HKEY_LOCAL_MACHINE, lst)
        lst = findreg(winreg.HKEY_CURRENT_USER, lst)
    except:
        traceback.print_exc()
        # fallback
        cover.log("Search python at system drive")
        try:
            path = os.environ.get("SystemDrive", "C:")
            for item in os.listdir(path):
                if item[:6].lower() != "python":
                    continue
                fp = os.path.join(path, item, "python.exe")
                if os.path.exists(fp) and not fp in lst:
                    lst.append(fp)
        except:
            traceback.print_exc()

    return lst

def search_python():
    if sys.platform.startswith("linux"):
        lst = search_python_posix()
    elif sys.platform.startswith("win"):
        lst = search_python_win()
    else:
        lst = search_python_posix()
    if len(lst) == 0:
        # fallback
        lst.append(sys.executable)
    return lst

def find_python_version(pylst):
    lst = []
    ids = []
    for interp in pylst:
        try:
            std, err = cover.exec_cmd([interp, "-V"])
            version = err.strip()
            if not version:
                # python 3.4+
                version = std.strip()
            if version[:6] == "Python":
                shver = version[6:].strip().replace(" ", "-")
                nid = shver
                nidn = 0
                while nid in ids:
                    nidn += 1
                    nid = shver + "-%d" % nidn
                ids.append(nid)
                lst.append((interp, nid, version))
            else:
                cover.err("Not a python", version)
                # no python found
                continue
        except:
            traceback.print_exc()
    return lst

def search_tests():
    base = os.path.join(cover.basepath, "cover")
    lst = []
    for item in os.listdir(base):
        if item[:5] != "test_" or item[-3:] != ".py":
            continue
        lst.append(os.path.join(base, item))
    lst.sort()
    return lst

def do_test_one(testfile, interp, info, dest):
    path = interp[0]
    nid = interp[1]
    destpath = dest[0]
    destenv = dest[1]
    tool2to3 = (info.get("2to3", "no") == "yes")
    py2 = (info.get("python2", "yes") == "yes")
    py3 = (info.get("python3", "yes") == "yes")
    copy = False
    if nid[:2] == "3.":
        if not py3:
            return ("skip", "not for python 3")
        if not tool2to3:
            copy = True
        else:
            return ("unimplemented", "todo")
    if nid[:2] == "2.":
        if not py2:
            return ("skip", "not for python 2")
        copy = True

    # check if fpdf installed
    if destenv.get("ver", "None") == "None":
        return ("nofpdf", "")

    # copy files
    testname = os.path.basename(testfile)
    testfmt = info.get("format", "raw")
    newfile = os.path.join(destpath, testname)
    newres = os.path.join(destpath, info.get("fn", testname + "." + testfmt.lower()))
    if copy:
        shutil.copy(testfile, destpath)
    # start execution
    std, err = cover.exec_cmd([path, "-B", newfile, "--check", "--auto", newres])
    with open(os.path.join(destpath, "testlog.txt"), "a") as f:
        f.write("#" * 40 + "\n")
        f.write(testname + "\n")
        f.write("=" * 40 + "\n")
        f.write(std)
        f.write("-" * 40 + "\n")
        f.write(err)

    answ = std.strip()
    if answ.find("\n") >= 0 or len(answ) == 0:
        return ("fail", "bad output")
    else:
        if answ == "HASHERROR":
            # get new hash
            nh = ""
            for line in err.split("\n"):
                line = line.strip()
                if line[:5] == "new =":
                    nh = line[5:].strip()
            return ("hasherror", nh)
        return (answ.lower(), "")

def prepare_dest(interp):
    destpath = os.path.join(cover.basepath, "out-" + interp[1])
    if not os.path.exists(destpath):
        os.makedirs(destpath)
    # copy common set
    src = os.path.join(cover.basepath, "cover")
    shutil.copy(os.path.join(src, "common.py"), destpath)
    shutil.copy(os.path.join(src, "checkenv.py"), destpath)
    with open(os.path.join(destpath, "testlog.txt"), "w") as f:
        f.write("Version: " + interp[1] + "\n")
        f.write("Path: " + interp[0] + "\n")
        f.write(str(interp[2:]) + "\n")

        # run checkenv
        std, err = cover.exec_cmd([interp[0], "-B", os.path.join(destpath, "checkenv.py")])
        env = {}
        if len(err.strip()) == 0:
            # OK
            f.write("Check environment - ok:\n")
            f.write(std)
            lineno = 0
            for line in std.split("\n"):
                lineno += 1
                line = line.strip()
                if lineno == 1:
                    if line != "CHECK":
                        break
                line = line.strip()
                kv = line.split("=", 1)
                if len(kv) == 2:
                    env[kv[0].lower().strip()] = kv[1].strip()
        else:
            f.write("ERROR:\n")
            f.write(err)
    return (destpath, env)

def do_test(testfile, interps, dests, stats, hint = ""):
    cover.log("Test", hint, ":", os.path.basename(testfile))
    info = cover.read_cover_info(testfile)
    resall = ""
    # prepare
    # do tests
    hasherr = []
    for interp in interps:
        if len(interps) < 6:
            resall += (interp[1] + " - ")
        res, desc = do_test_one(testfile, interp, info, dests[interp[1]])
        if res == "hasherror":
            hasherr.append(desc)
            #cover.log("HASH =", desc)
        # update statistic
        stats["_"]["_"] += 1
        stats["_"][res] = stats["_"].get(res, 0) + 1
        stats[interp[1]]["_"] += 1
        stats[interp[1]][res] = stats[interp[1]].get(res, 0) + 1
        resall += (res + " " * 10)[:6].upper()
        resall += "  "
    cover.log(resall)
    # test if all hash
    if len(interps) == len(hasherr):
        cover.err("All hashes wrong")

def print_interps(interps):
    cover.log(">> Interpreters:", len(interps))
    dests = {}
    stats = {"_": {"_": 0}}
    for idx, interp in enumerate(interps):
        cover.log("%d) %s - %s" % (idx + 1, interp[1], interp[0]))
    cover.log()

def do_all_test(interps, tests):
    print_interps(interps)
    dests = {}
    stats = {"_": {"_": 0}}
    for idx, interp in enumerate(interps):
        dests[interp[1]] = prepare_dest(interp)
        stats[interp[1]] = {"_": 0}

    cover.log(">> Tests:", len(tests))
    for idx, test in enumerate(tests):
        do_test(test, interps, dests, stats, "%d / %d" % (idx + 1, len(tests)))
    cover.log()

    cover.log(">> Statistics:")
    def stat_str(stat):
        keys = list(stat.keys())
        keys.sort()
        st = "total - %d" % stat["_"]
        for key in keys:
            if key == "_":
                continue
            st += (", %s - %d" % (key, stat[key]))

        return st
    for interp in interps:
        cover.log(interp[1] + ":", stat_str(stats[interp[1]]))
    cover.log("-"*10)
    cover.log("All:", stat_str(stats["_"]))
    
    # check if no FPDF at all
    total = stats["_"]["_"]
    fpdf = stats["_"].get("nofpdf", 0)
    skip = stats["_"].get("skip", 0)
    if skip == total:
        cover.log("*** All tests skipped. Install some modules (PIL, PyBIDI, " +
            "Gluon, etc)")
    elif fpdf + skip == total:
        hint_prepare()
    # check if NORES
    nores = stats["_"].get("nores", 0)
    if nores > 0:
        items = cover.load_res_list()
        tested = []
        packs = []
        cover.log("*** Some resources are not found")
        for test in tests:
            settings = cover.read_cover_info(test)
            for res in settings.get("res", []):
                if res in tested:
                    continue
                tested.append(res)
                fn = os.path.join(cover.basepath, *res.split("/"))
                if os.path.exists(fn):
                    continue
                print("  not found " + res)
                # check with pack
                if res in items:
                    hs, tags, pack = items[res]
                    if pack and pack not in packs:
                        packs.append(pack)
        if len(packs) > 0:
            cover.log("*** You can download theese resources with:")
            for pack in packs:
                cover.log("  runtest.py --download%s" % pack)

def list_tests():
    tst = search_tests()
    cover.log(">> Tests:", len(tst))
    for idx, test in enumerate(tst):
        test = os.path.basename(test)
        if test[:5].lower() == "test_":
            test = test[5:]
        if test[-3:].lower() == ".py":
            test = test[:-3]
        cover.log("%d) %s" % (idx + 1, test))
    cover.log()

def usage():
    cover.log("Usage: runtest.py [...]")
    cover.log("  --listtests      - list all tests")
    cover.log("  --listinterps    - list all availiable interpreters")
    cover.log("  --test issuexx   - add test issuexx")
    cover.log("  --test @file     - add test from file")
    cover.log("  --interp path    - test against specified interpreters")
    cover.log("  --interp @file   - read interpreters list from file")
    cover.log("  --autodownload   - download used resources automatically")
    try:
        packs = cover.load_res_packs()
        k = list(packs.keys())
        k.sort()
        for p in k:
            cover.log("  --download%s" % p)
            cover.log("             - download %s" % packs[p][0])
    except Exception:
            traceback.print_exc()
    cover.log("  --download_all   - download all resources from all packs")
    cover.log("  --help           - this page")

def hint_prepare():
    if cover.PYFPDFTESTLOCAL:
        if sys.platform.startswith("win"):
            prefix = ""
            suffix = ".bat"
        else:
            prefix = "./"
            suffix = ".sh"
        cover.log("*** Please, prepare local copy for tests")
        cover.log("***   " + prefix + "prepare_local" + suffix)
    else:
        cover.log("*** Please, install PyFPDF with")
        cover.log("***   python setup.py install")
        cover.log("*** or set PYFPDFTESTLOCAL variable to use local copy")
        if sys.platform.startswith("win"):
            cover.log("***   set PYFPDFTESTLOCAL=1")
        else:
            cover.log("***   export PYFPDFTESTLOCAL=1")

def read_list(fn):
    with open(fn, "r") as f:
        return f.readlines()

def hasher(path, args):
    tags = []
    pack = ""
    while len(args):
        arg = args[0]
        args = args[1:]
        if arg == "--tag":
            if len(args) == 0:
                cover.log("Param without value")
                return
            value = args[0]
            args = args[1:]
            if value not in tags:
                tags.append(value)
        elif arg == "--pack":
            if len(args) == 0:
                cover.log("Param without value")
                return
            value = args[0]
            args = args[1:]
            pack = value
        else:
            cover.log("Unknown param")
            return

    lst = []
    if os.path.isdir(path):
        files = [(x.lower(), x) for x in os.listdir(path)]
        files.sort()
        for s, item in files:
            fp = os.path.join(path, item)
            # clear path
            bp = fp
            if sys.platform.startswith("win"):
                bp = fp.replace("\\", "/")
            lst += [[bp, cover.file_hash(fp)]]
    else:
        lst = [[path, cover.file_hash(path)]]
    for item, hs in lst:
        cover.log("res=" + item)
        cover.log("hash=" + hs)
        cover.log("tags=" + ",".join(tags))
        if pack:
            cover.log("pack=" + pack)
        cover.log()

def download_pack(packname):
    if packname[:1] == "-":
        packname = packname[1:]
    packs = cover.load_res_packs()
    if packname == "_all":
        dnpacks = packs.keys()
    else:
        dnpacks = [packname]
        if packname not in packs:
            cover.err("Unknown pack \"%s\"" % packname)
            return
    for pidx, packname in enumerate(dnpacks):
        name, url, filename, dest, valid, strip = packs[packname]
        cover.log("Downloading: %d/%d %s" % (pidx + 1, len(dnpacks), name))
        destdir = os.path.join(cover.basepath, *dest)
        if not os.path.exists(destdir):
            os.makedirs(destdir)
        zippath = os.path.join(cover.basepath, filename)
        if not os.path.exists(zippath):
            u = urlopen(url)
            meta = u.info()
            try:
                file_size = int(meta.get("Content-Length"))
                cover.log("Downloading: %s bytes" % str(file_size))
            except Exception:
                file_size = None
                cover.log("Downloading:")
            with open(zippath, "wb") as f:
                file_size_dl = 0
                while True:
                    buff = u.read(64 * 1024)
                    if not buff:
                        break
                    file_size_dl += len(buff)
                    f.write(buff)
                    if file_size:
                        cover.log("  ", file_size_dl * 100. / file_size, "%")
                    else:
                        cover.log("  ", file_size_dl, "bytes")
        # unpack
        cover.log("Extracting")
        import zipfile, re
        newfiles = []
        with open(zippath, "rb") as fh:
            z = zipfile.ZipFile(fh)
            for name in z.namelist():
                if not re.match(valid, name):
                    cover.log("  skip " + name)
                    continue
                # strip slashes
                ename = name
                ns = strip
                while ns > 0:
                    ns -= 1
                    ps = ename.find("/")
                    if ps > 0:
                        ename = ename[ps + 1:]
                    else:
                        ename = ""
                        break
                if not ename:
                    cover.log("  strip " + name)
                    continue
                if name != ename:
                    cover.log("  ok " + name + " -> " + ename)
                else:
                    cover.log("  ok " + name)
                # extract
                fn = os.path.join(destdir, *ename.split("/"))
                if ename[-1:] == "/":
                    if not os.path.exists(fn):
                        os.makedirs(fn)
                else:
                    base = os.path.dirname(fn)
                    if not os.path.exists(base):
                        os.makedirs(base)
                    with open(fn, "wb") as outfile:
                        outfile.write(z.read(name))
                    newfn = "/".join(dest + ename.split("/"))
                    newfiles.append(newfn)
        # check extracted
        for res, (hs, tags, pack) in cover.load_res_list().items():
            if pack != packname: continue
            fp = os.path.join(cover.basepath, *res.split("/"))
            if not os.path.exists(fp):
                cover.err("Resource \"%s\" not found" % res)
                return
            if cover.file_hash(fp) != hs:
                if cover.common.RESHASH == "{IGNORE}":
                    cover.log("  ignore hash " + res)
                else:
                    cover.err("Resource \"%s\" damaged (hash mismatch)" % res)
                    return
            if res in newfiles:
                newfiles.remove(res)
        # check unchecked
        for fn in newfiles:
            print("  no hash for " + fn)
    cover.log("Done")

def main():
    cover.log("Test PyFPDF")

    testsn = []
    interpsn = []
    autodownloadres = False
    args = sys.argv[1:]
    while len(args):
        arg = args[0]
        args = args[1:]
        if arg == "--hash":
            if len(args) == 0:
                cover.log("Param without value")
                return usage()
            return hasher(args[0], args[1:])
        if arg == "--help":
            print(cover.PACKHASH)
            return usage()
        elif arg == "--test":
            if len(args) > 0:
                value = args[0]
                args = args[1:]
            else:
                cover.log("Param without value")
                return usage()
            if value[:1] == "@":
                # from file
                testsn += read_list(value[1:])
            else:
                testsn.append(value)
        elif arg == "--interp":
            if len(args) > 0:
                value = args[0]
                args = args[1:]
            else:
                cover.log("Param without value")
                return usage()
            if value[:1] == "@":
                # from file
                interpsn += read_list(value[1:])
            else:
                interpsn.append(value)
        elif arg == "--listtests":
            return list_tests()
        elif arg == "--listinterps":
            return print_interps(find_python_version(search_python()))
        elif arg.startswith("--download"):
            return download_pack(arg[10:])
        elif arg == "--ignore-res-hash":
            cover.common.RESHASH = "{IGNORE}"
        elif arg == "--ignore-pack-hash":
            cover.common.PACKHASH = "{IGNORE}"
        elif arg == "--autodownload":
            autodownloadres = True
        else:
            cover.log("Unknown param")
            return usage()

    if len(testsn) == 0:
        tests = search_tests()
    else:
        # cheack all tests
        tests = []
        for test in testsn:
            test = test.strip()
            fn = os.path.join(cover.basepath, "cover", "test_" + test + ".py")
            if os.path.exists(fn):
                tests.append(fn)
            else:
                cover.err("Test \"%s\" not found" % test)
                return

    if len(interpsn) == 0:
        interps = find_python_version(search_python())
    else:
        # cheack all tests
        interps = []
        for interp in interpsn:
            fn = os.path.abspath(interp)
            if os.path.exists(fn):
                interps.append(fn)
            else:
                cover.err("Interpreter \"%s\" not found" % test)
                return
        interps = find_python_version(interps)
    
    # check if need res
    if autodownloadres:
        usedres = []
        usedpacks = []
        for test in tests:
            settings = cover.read_cover_info(test)
            for res in settings.get("res", []):
                if res in usedres:
                    continue
                usedres.append(res)
        allres = cover.load_res_list()
        for ures in usedres:
            if ures in allres:
                hs, tags, pack = allres[ures]
                if pack and pack not in usedpacks:
                    usedpacks.append(pack)
        for pack in usedpacks:
            download_pack(pack)

    do_all_test(interps, tests)


if __name__ == "__main__":
    main()
