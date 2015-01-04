import zlib
import sys
import pdb
import os
from binascii import hexlify

print(sys.argv[1])
hex = '--hex' in sys.argv
r = open(sys.argv[1], 'rb')
i = 0
length = None
while True:
    l = r.readline().decode("ascii", "replace")  # Avoid byte strings in 2.5
    if not l:
        break
    if "/Length " in l:
        print(l)
        s = l[l.index("/Length ")+8:]
        if ' ' in s:
            s = s[:s.index(" ")]
        if '>' in s:
            s = s[:s.index(">")]
        length = int(s)
        print("%s%s" % (l, length))
    if l.startswith('stream') and length:
        i += 1
        fn = "stream_%s_%s" % (i, sys.argv[1])
        print("writing  %s %s" % (length, fn))
        s = r.read(length)
        w = open(fn, 'wb')
        try:
            s = zlib.decompress(s)
        except zlib.error:
            pass
        if hex:
            s = hexlify(s)
        w.write(s)
        w.close()
r.close()

os.system("windiff stream_1_ex_php.pdf stream_1_ex.pdf")
