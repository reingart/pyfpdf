#!/bin/sh

# prepare fpdf for python3.x setup

mkdir fpdf_py3k

python3 -m lib2to3 -f all -w -o fpdf_py3k -n fpdf

echo Now you can use:
echo    python3 setup.py install


