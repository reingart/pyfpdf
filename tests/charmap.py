"Print all charters"

from fpdf import FPDF, FPDF_VERSION, TTFontFile

print FPDF_VERSION

class MyTTFontFile(TTFontFile):
    def getCMAP4(self, unicode_cmap_offset, glyphToChar, charToGlyph):
        TTFontFile.getCMAP4(self, unicode_cmap_offset, glyphToChar, charToGlyph)
        self.saveChar = charToGlyph
        
    def getCMAP12(self, unicode_cmap_offset, glyphToChar, charToGlyph):
        TTFontFile.getCMAP12(self, unicode_cmap_offset, glyphToChar, charToGlyph)
        self.saveChar = charToGlyph


pdf=FPDF()
pdf.compression = True
pdf.add_page()

fontpath = "DroidSansFallback.ttf"
pdf.add_font("font", '', fontpath, uni = True)
ttf = MyTTFontFile()
ttf.getMetrics(fontpath)


pdf.set_font("font", '', 10)

# create PDF with first 999 charters in font
cnt = 0
for char in ttf.saveChar:
    cnt += 1
    pdf.write(8, u"%03d) %06x - " % (cnt, char) + unichr(char))
    pdf.ln()
    if cnt >= 999:
        break

fn = 'charmap.pdf'
pdf.output(fn,'F')

import os

try:
    os.startfile(fn)
except:
    os.system("evince %s" % fn)

