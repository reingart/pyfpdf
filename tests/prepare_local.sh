#!/bin/sh

# prepare local copy for tests

mkdir fpdf_local

ln -s ../fpdf fpdf_local/fpdf

echo Now you can test:
echo    python runtest.py
