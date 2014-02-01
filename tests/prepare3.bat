
rem prepare fpdf for python3.x tests

mkdir fpdf_py3k

python.exe -m lib2to3 -f all -W -w -o fpdf_py3k/fpdf -n ../fpdf

