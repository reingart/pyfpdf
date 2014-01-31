#!/bin/sh

# prepare fpdf for python2.x tests

mkdir fpdf_py2k
mkdir fpdf_py2k/fpdf

cp ../fpdf/*.py fpdf_py2k/fpdf/

echo Now you can test:
echo    python runtest.py


