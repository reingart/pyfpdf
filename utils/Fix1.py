# Updates the unique, final XREF table
# Usage: Fix1 in.pdf [out.pdf]
import sys
from PDFRUUtils import *

def Fix1(inPDF, outPDF):
	buf=UpdateStreamLengths(file(inPDF,'rb').read())
	newbuf=ReplaceXRefsTable(buf, BuildXRefsTable(FindXRefs(buf)))
	file(outPDF,'wb').write(newbuf)

if __name__=='__main__':
	inPDF=outPDF=sys.argv[1]
	if len(sys.argv) > 2:
		outPDF=sys.argv[2]
	Fix1(inPDF, outPDF)
