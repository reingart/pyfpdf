# -*- coding: utf-8 -*-

"Test core fonts widths"

from __future__ import with_statement

import common # common set of utilities
import fpdf.fonts

#PyFPDF-cover-test:res=adobe-agl/glyphlist.txt
#PyFPDF-cover-test:res=adobe-agl/zapfdingbats.txt
#PyFPDF-cover-test:res=adobe-afm/Courier.afm
#PyFPDF-cover-test:res=adobe-afm/Courier-Bold.afm
#PyFPDF-cover-test:res=adobe-afm/Courier-BoldOblique.afm
#PyFPDF-cover-test:res=adobe-afm/Courier-Oblique.afm
#PyFPDF-cover-test:res=adobe-afm/Helvetica.afm
#PyFPDF-cover-test:res=adobe-afm/Helvetica-Bold.afm
#PyFPDF-cover-test:res=adobe-afm/Helvetica-BoldOblique.afm
#PyFPDF-cover-test:res=adobe-afm/Helvetica-Oblique.afm
#PyFPDF-cover-test:res=adobe-afm/Symbol.afm
#PyFPDF-cover-test:res=adobe-afm/Times-Roman.afm
#PyFPDF-cover-test:res=adobe-afm/Times-Bold.afm
#PyFPDF-cover-test:res=adobe-afm/Times-BoldItalic.afm
#PyFPDF-cover-test:res=adobe-afm/Times-Italic.afm
#PyFPDF-cover-test:res=adobe-afm/ZapfDingbats.afm

import sys
import os
import traceback

if common.PY3K:
    unichr = chr

NONPRINTABLE = {
    "\x00": "NUL",
    "\x01": "SOH",
    "\x02": "STX",
    "\x03": "ETX",
    "\x04": "EOT",
    "\x05": "ENQ",
    "\x06": "ACK",
    "\x07": "BEL",
    "\x08": "BS",
    "\x09": "HT",
    "\x0a": "LF",
    "\x0b": "VT",
    "\x0c": "FF",
    "\x0d": "CR",
    "\x0e": "SO",
    "\x0f": "SI",
    "\x10": "DLE",
    "\x11": "DC1",
    "\x12": "DC2",
    "\x13": "DC3",
    "\x14": "DC4",
    "\x15": "NAK",
    "\x16": "SYN",
    "\x17": "ETB",
    "\x18": "CAN",
    "\x19": "EM",
    "\x1a": "SUB",
    "\x1b": "ESC",
    "\x1c": "FS",
    "\x1d": "GS",
    "\x1e": "RS",
    "\x1f": "US",
    "\x20": "SP",
    "\x7F": "DEL",
    "\x81": "UNUSED_81",
    "\x8D": "UNUSED_8D",
    "\x8F": "UNUSED_8F",
    "\x90": "UNUSED_90",
    "\x9D": "UNUSED_9D",
    "\xA0": "NBSP",
    "\xAD": "SHY"
}

def read_afm(fn):
    curr = ""
    curr_opt = ""
    curr_data = {}
    level = 0
    stack = []
    with open(fn, "rb") as f:
        for line in f.readlines():
            line = line.decode("latin-1").strip()
            if line[:5] == "Start":
                # enter section
                stack.append([curr, curr_opt, curr_data])
                level += 1
                data = line[5:].split(" ", 1)
                curr = data[0]
                curr_opt = ""
                curr_data = {}
                if len(data) > 1:
                    curr_opt = data[1]
            elif line[:3] == "End":
                # end section
                data = line[3:]
                if data != curr:
                    raise Exception("End without start " + line + 
                        ", expected " + curr + ", file " + fn)
                nested = curr_data
                curr, curr_opt, curr_data = stack[-1:][0]
                curr_data[data] = nested
                stack = stack[:-1]
            else:
                if curr == "CharMetrics":
                    data = line.split(";")
                    c = None
                    wx = None
                    name = None
                    box = None
                    for item in data:
                        item = item.strip()
                        if not item: continue
                        if item[:2] == "C ":
                            c = int(item[2:].strip(), 10)
                        elif item[:2] == "N ":
                            name = item[2:].strip()
                        elif item[:3] == "WX ":
                            wx = int(item[3:].strip(), 10)
                        elif item[:2] == "B ":
                            bbox = [int(x, 10)
                                for x in item[2:].strip().split(" ")]
                        elif item[:2] == "L ":
                            pass
                        else:
                            print(name, "=", item)
                    curr_data[name] = (wx, c, bbox)
                else:
                    data = line.split(" ", 1)
                    if len(data) > 1:
                        k, v = data
    assert curr == "", "AFM structure mismatch, file " + fn
    return curr_data

def readglyphlist(fn):
    data = {}
    with open(fn, "rb") as f:
        for line in f.readlines():
            line = line.decode("latin-1").strip()
            if line[:1] == "#":
                continue
            line = line.split(";",1)
            try:
                data[line[0]] = "".join([unichr(int(x, 16)) 
                    for x in line[1].split(" ")])
            except Exception:
                traceback.print_exc()
                raise Exception("Can't decode code for " + line[0] + 
                    " = " + line[1])
    return data

def conv1252(names):
    chars = {}
    for name in names:
        u = names[name]
        try:
            c = u.encode("windows-1252").decode("latin-1")
            if not common.PY3K: # fix to avoid unicode charters
                c = c.encode("latin-1")
            if c in chars:
                chars[c].append(name)
            else:
                chars[c] = [name]
        except Exception:
            pass
    return chars

@common.add_unittest
def dotest(outputname, nostamp):
    cw = fpdf.fonts.fpdf_charwidths
    fonts = list(cw.keys())
    fonts.sort()
    names = readglyphlist(os.path.join(common.basepath, 
        "adobe-agl", "glyphlist.txt"))
    c1252 = conv1252(names)

    for font in fonts:
        afm = font[:1].upper() + font[1:]
        iname = "Italic" if afm[:5] == "Times" else "Oblique"
        if afm == "Zapfdingbats":
            afm = "ZapfDingbats"
        elif afm == "Times":
            afm += "-Roman"
        elif afm[-2:] == "BI":
            afm = afm[:-2] + "-Bold" + iname
        elif afm[-1:] == "I":
            afm = afm[:-1] + "-" + iname
        elif afm[-1:] == "B":
            afm = afm[:-1] + "-Bold"
        if not nostamp:
            common.log("Test AFM: " + afm)
        afmdata = read_afm(os.path.join(common.basepath, "adobe-afm", afm + ".afm"))
        unames = names
        ucw = afmdata["FontMetrics"]["CharMetrics"]
        defmap = True
        if font in ("symbol", "zapfdingbats"):
            defmap = False
            usedmap = {}
            for name, (wx, c, _) in ucw.items():
                if c >= 0:
                    usedmap[chr(c)] = [name]
        else:
            usedmap = c1252
        # PDF 1.7, page 1000, all unused codes greater than 0o40 map to bullet
        spwx, _, _ = ucw["space"]
        if "bullet" in ucw: 
            bulwx, _, _ = ucw["bullet"]
        if "hyphen" in ucw:
            shywx, _, _ = ucw["hyphen"]
        keys = list(cw[font].keys())
        keys.sort()
        # enum charters in PyFPDF
        allk = []
        for ordc in range(256):
            c = chr(ordc)
            assert c in keys, "Charter 0x%02x is absent in \"%s\"" % (ordc, 
                font)
            if defmap:
                if ordc <= 0o40 or ordc == 0xA0: # control and nbsp
                    wx = spwx
                elif ordc == 0xAD: # shy
                    wx = shywx
                else:
                    wx = bulwx
            else:
                if ordc <= 0o40 and font == "symbol":
                    # Note: pdf with chars 00..1f from Symbol font may have
                    #  wrong glyphs in non-adobe viewers
                    wx = spwx
                else:
                    wx = 0
            gname = "NONAME_%02X" % ordc
            pdfwx = cw[font][c]
            if c in usedmap:
                namelst = usedmap[c]
                for name in namelst:
                    if name in ucw:
                        wx, _, _ = ucw[name]
                        gname = name
                        break
            assert pdfwx == wx, "Charter width \"%s\" "\
                "(0x%02x) mismatch with AFM (%d != %d) in \"%s\"" % (gname,
                ordc, pdfwx, wx, font)


def main():
    return common.testmain(__file__, dotest)

if __name__ == "__main__":
    main()

