# -*- coding: utf-8 -*-

# common utilities for pyfpdf tests
# Note: 1) this file imported from both 2 and 3 version of python
#       2) import this file before import fpdf
#       3) assert this file in tests/cover folder

from __future__ import with_statement

import sys, os, subprocess
import unittest, inspect

PY3K = sys.version_info >= (3, 0)

basepath = os.path.abspath(os.path.join(__file__, "..", ".."))

RESHASH = "d911ffb184e1cc4dd47162e8c5465109"
PACKHASH = "66dd5dc66e3ee282cd96da47b269624a"

# if PYFPDFTESTLOCAL is not set - use installed pyfpdf version
PYFPDFTESTLOCAL = ("PYFPDFTESTLOCAL" in os.environ)
if PYFPDFTESTLOCAL:
    sys.path = [os.path.join(basepath, "fpdf_local")] + sys.path

if PY3K:
    #import common3 as _common
    def tobytes(value):
        return value.encode("latin1")
    def frombytes(value):
        return value.decode("latin1")
    from hashlib import md5
    unicode = str

else:
    #import common2 as _common
    def tobytes(value):
        return value
    def frombytes(value):
        return value
    try:
        from hashlib import md5
    except ImportError:
        import md5

def exec_cmd(cmd):
    "Execute command and return console output (stdout, stderr)"
    obj = subprocess.Popen(cmd, \
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)
    std, err = obj.communicate()
    return (frombytes(std), frombytes(err))

def start_by_ext(fn):
    "Open file in associated progrom"
    try:
        try:
            os.startfile(fn)
        except WindowsError:
            os.system("start " + fn)
    except:
        subprocess.call(["xdg-open", fn])

def writer(stream, items):
    sep = ""
    for item in items:
        stream.write(sep)
        sep = " "
        if not isinstance(item, str):
            item = str(item)
        if not PY3K:
            if not isinstance(item, unicode):
                item = str(item)
        stream.write(item)
    stream.write("\n")

def log(*kw):
    writer(sys.stdout, kw)

def err(*kw):
    writer(sys.stderr, kw)

def test_putinfo(self):
    "Replace info stamp with defaults for all automated test objects"
    self._out('/Producer '+self._textstring('PyFPDF TEST http://pyfpdf.googlecode.com/'))
    if hasattr(self,'title'):
        self._out('/Title '+self._textstring(self.title))
    if hasattr(self,'subject'):
        self._out('/Subject '+self._textstring(self.subject))
    if hasattr(self,'author'):
        self._out('/Author '+self._textstring(self.author))
    if hasattr (self,'keywords'):
        self._out('/Keywords '+self._textstring(self.keywords))
    if hasattr(self,'creator'):
        self._out('/Creator '+self._textstring(self.creator))
    self._out('/CreationDate '+self._textstring('D:19700101000000'))

def file_hash(fn):
    "Calc MD5 hash for file"
    md = md5()
    with open(fn, "rb") as f:
        md.update(f.read())
    return md.hexdigest()

def read_cover_info(fn):
    "Read cover test info"
    with open(fn, "rb") as f:
        da = {"res": []}
        mark = "#PyFPDF-cover-test:"
        encmark = "# -*- coding:"
        enc = None
        hdr = False
        for line in f.readlines():
            if enc is None:
                if line.decode("latin-1")[:len(encmark)] == unicode(encmark):
                    enc = line.decode("latin-1")[len(encmark):].strip()
                    if enc[-3:] == unicode("-*-"):
                        enc = enc[:-3].strip()
                        try:
                            line.decode(enc)
                        except:
                            enc = None
            line = line.decode(enc or "UTF-8").strip()
            if line[:len(mark)] == mark:
                hdr = True
                kv = line[len(mark):].split("=", 1)
                if len(kv) == 2:
                    if kv[0] == "res":
                        da["res"].append(kv[1])
                    else:
                        da[kv[0]] = kv[1]
            else:
                if hdr and len(line) == 0:
                    break
    return da

def parse_test_args(args, deffn):
    "Parse test args, return (fn, autotest)"
    args = args[1:]
    da = {}
    da["fn"] = deffn
    da["autotest"] = False
    da["check"] = False
    while len(args) > 0:
        arg = args[0]
        if arg == "--help":
            log("Test usage: [--auto] [--check] [<outputname>]")
            log("  --auto - no version and timestamp in file, do not open")
            log("  --check - compare new file with stock")
            log("  <outputname> - output filename, default \"%s\"" % deffn)
            sys.exit(0)
        if arg == "--auto":
            da["autotest"] = True
        elif arg == "--check":
            da["check"] = True
        else:
            da["fn"] = arg
        args = args[1:]
    return da

def load_res_file(path):
    items = {}
    res = None
    with open(path) as file:
        for line in file:
            line = line.strip()
            if line[:1] == "#":
                continue
            kv = line.split("=", 1)
            if len(kv) != 2:
                continue
            if kv[0] == "res":
                res = kv[1]
                if res not in items:
                    items[res] = ["", [], ""]
            elif res is None:
                continue
            elif kv[0] == "hash":
                items[res][0] = kv[1]
            elif kv[0] == "tags":
                items[res][1] += [kv[1].split(",")]
            elif kv[0] == "pack":
                items[res][2] = kv[1]
    return items

def load_res_packs():
    path = os.path.join(basepath, "respacks.txt")
    if file_hash(path) != PACKHASH and PACKHASH != "{IGNORE}":
        err("File respacks.txt damaged (hash mismatch)")
        return {}
    packs = {}
    pack = None
    with open(path) as file:
        for line in file:
            line = line.strip()
            if line[:1] == "#":
                continue
            kv = line.split("=", 1)
            if len(kv) != 2:
                continue
            if kv[0] == "pack":
                pack = kv[1]
                if pack not in packs:
                    packs[pack] = ["", "", "", [], ".*", 0]
            elif pack is None:
                continue
            elif kv[0] == "name":
                packs[pack][0] = kv[1]
            elif kv[0] == "url":
                packs[pack][1] = kv[1]
                if not packs[pack][2]:
                    packs[pack][2] = kv[1].split('/')[-1]
            elif kv[0] == "filename":
                packs[pack][2] = kv[1]
            elif kv[0] == "dest":
                packs[pack][3] = kv[1].split("/")
            elif kv[0] == "valid":
                packs[pack][4] = kv[1]
            elif kv[0] == "strip":
                packs[pack][5] = int(kv[1], 10)
    return packs

def load_res_list():
    path = os.path.join(basepath, "resources.txt")
    if file_hash(path) != RESHASH and RESHASH != "{IGNORE}":
        err("File resources.txt damaged (hash mismatch)")
        return {}
    return load_res_file(path)

def skip_reason(settings):
    "Check if test should be skipped"
    # check python version
    if PY3K:
        if settings.get("python3", "yes") == "no":
            # python 3 inacceptable
            return "Python 3.x unsupported %s" % repr(sys.version_info)
    else:
        if settings.get("python2", "yes") == "no":
            # python 2 inacceptable
            return "Python 2.x unsupported %s" % repr(sys.version_info)
    plat = settings.get("platform", "*")
    if plat == "":
        plat = "*"
    if plat != "*":
        plats = plat.split(",")
        accept = False
        for plat in plats:
            if sys.platform == plat:
                accept = True
                break
        if not accept:
            return "not for \"" + sys.platform + "\""
    if settings.get("pil", "no") == "yes":
        # import PIL
        try:
            try:
                import Image
            except:
                from PIL import Image
        except ImportError:
            Image = None
        if Image is None:
            return "PIL or Pillow module is required"
    return None

def check_res(settings, verbose):
    reslst = None
    for res in settings.get("res", []):
        if reslst is None:
            # check
            respath = os.path.join(basepath, "resources.txt")
            if file_hash(respath) != RESHASH:
                err("File resources.txt damaged (hash mismatch)")
                if not verbose:
                    log("RESHASH")
                return False
            # load data
            reslst = load_res_file(respath)
        if res not in reslst:
            err("Resource \"" + res + "\" not in list")
            if not verbose:
                log("NORES")
            return False
        # check hash
        respath = os.path.join(basepath, res)
        if not os.path.exists(respath):
            err("Resource \"" + res + "\" not found")
            if not verbose:
                log("NORES")
            return False
        hs = file_hash(respath)
        if hs != reslst[res][0]:
            err("Resource \"" + res + "\" damaged")
            err("      read = %s" % hs)
            err("  required = %s" % reslst[res][0])
            if not verbose:
                log("RESERR")
            return False

    return True

def check_hash(settings, fn):
    check = True
    if settings.get("fn"):
        # compare with hash
        hs = file_hash(fn)
        fhs = settings.get("hash", "")
        if fhs != "" and hs != fhs:
            check = False
            err("Hash mismatch:")
            err("       new = %s" % hs)
            err("  required = %s" % fhs)
    return check

def check_result(settings, args):
    check = not args["check"] or check_hash(settings, args["fn"])
    if args["autotest"]:
        if check:
            log("OK")
        else:
            log("HASHERROR")
    else:
        if settings.get("fn"):
            start_by_ext(args["fn"])
        else:
            log("Test passed")

def add_unittest(testfunc):
    """Decorator to add "unittest" test case class"""

    class Test(unittest.TestCase):
        def setUp(self):
            self.assertTrue(check_res(self.settings, verbose=True))

        def runTest(self):
            outputname = self.settings.get("fn")
            testfunc(outputname, nostamp=True)
            hash_okay = check_hash(self.settings, outputname)
            self.assertTrue(hash_okay, "Hash mismatch")

    name = testfunc.__name__ + "_unittest"
    Test.__name__ = name
    Test.__module__ = testfunc.__module__

    Test.settings = read_cover_info(inspect.getsourcefile(testfunc))
    reason = skip_reason(Test.settings)
    if reason is not None and sys.version_info >= (2, 7):
        Test = unittest.skip(reason)(Test)  # No skip() in Python 2.6

    setattr(inspect.getmodule(testfunc), name, Test)
    return testfunc

def testmain(fn, testfunc):
    si = read_cover_info(fn)
    da = parse_test_args(sys.argv, si.get("fn"))

    verbose = not da["autotest"]
    reason = skip_reason(si)
    if reason is not None:
        if verbose:
            err(reason)
        else:
            log("SKIP")
        return
    if not check_res(si, verbose=verbose):
        return

    testfunc(da["fn"], da["autotest"] or da["check"])
    check_result(si, da)

