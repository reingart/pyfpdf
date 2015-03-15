import zlib
import sys
import pdb
import os

print sys.argv[1]
hex = '--hex' in sys.argv
r = open(sys.argv[1], 'rb')
i = 0
length = None
while 1:
    l = r.readline()
    if l == "":
        break
    if "/Length " in l:
        print l
        s = l[l.index("/Length ")+8:]
        if ' ' in s:
            s = s[:s.index(" ")]
        if '>' in s:
            s = s[:s.index(">")]
        length = int(s)
        print l, length
    if l.startswith('stream') and length:
        i += 1
        fn = "stream_%s_%s" % (i, sys.argv[1])
        print "writing ", length, fn
        s = r.read(length)
        w = open(fn, 'wb')
        try:
            s = zlib.decompress(s)
        except zlib.error:
            pass
        if hex:
            s = s.encode('hex')
        w.write(s)
        w.close()
r.close()

os.system("windiff stream_1_ex_php.pdf stream_1_ex.pdf")
