rem Convert to Python 3.x

mkdir fpdf_py3k
rem c:\python32\tools\Scripts\2to3.py -f all -w -o fpdf_py3k -n fpdf 
c:\Python32\python.exe setup.py install
c:\Python32\python.exe tests\py3k.py