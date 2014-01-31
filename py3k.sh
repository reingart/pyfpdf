#!/bin/sh

# prepare fpdf for python3.x

mkdir fpdf_py3k

python3 -m lib2to3 -f all -W -w -o fpdf_py3k/fpdf -n fpdf

