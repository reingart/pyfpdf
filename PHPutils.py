# -*- coding: iso-8859-1 -*-

"""
A few rough Python equivalents of PHP internal functions (=lazy port).

NOTE:
1) PHP "array" object is mostly similar to a Python "dictionary", but some
times a "list" (or "array": see Protection.py) may be required!

2) PHP "isset()" tests often wether an array has given key, or a variable
is defined in global/local space;

3) PHP string functions have often different return values from Python (see below);

4) "for (x; a <[=]b; y)" loops become "for i in range(a,b[+1]):" in Python;

5) PHP emits automatically floats quotients when needed, Python don't: so add a
".0" to divisors when PDF expects decimal numbers.

Actually, all FPDF tutorials (even from ported modules) work fine, but bugs
or incompatibilities might be hidden somewhere: so, USE IT AT YOUR OWN RISK!
"""
import sys, os

strlen = len
filesize=os.path.getsize
file_exists=os.path.exists
count=len
SEEK_CUR=1
SEEK_SET=0

def substr(s, start, length=-1):
	if length < 0:
		length=len(s)-start
	return s[start:start+length]

def substr_count(haystack, needle, offset=0, length=None):
	return haystack.count(needle,offset)

def die(s):
	sys.stderr.write(s)
	sys.exit(-1)

def basename(p):
	return os.path.splitext(p)[0]

def is_bool(x):	return type(x)==type(bool())
def empty(s): return len(s)==0
def is_string(s): return isinstance(s,basestring)
def strtolower(s): return s.lower()
def strtoupper(s): return s.upper()
def str_replace(sc, rp, s): return s.replace(sc,rp)
def sprintf(fmt, *args): return fmt % args
def strpos(s, c): return s.find(c) # Python returns -1 instead of FALSE!
def strrpos(s, c): return s.rfind(c) # Python returns -1 instead of FALSE!
def hexdec(x): return int(x,16)
def floor(x): return float(int(x))
def str_repeat(s,t): return s*int(t)
