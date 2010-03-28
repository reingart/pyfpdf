# Compress streams
# Usage: Fix3 in.pdf [out.pdf]
import sys
from PDFRUUtils import *

inPDF=outPDF=sys.argv[1]
if len(sys.argv) > 2:
 outPDF=sys.argv[2]

buf=CompressStreams(file(inPDF,'rb').read())
newbuf=ReplaceXRefsTable(buf, BuildXRefsTable(FindXRefs(buf)))
file(outPDF,'wb').write(newbuf)
