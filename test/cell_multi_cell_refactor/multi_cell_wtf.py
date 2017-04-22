"""metadata_test.py"""

import unittest
import sys
import os
sys.path.insert(0,
  os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    os.path.join('..', '..')
  )
)

import fpdf
import test
from test.utilities import relative_path_to, \
                           set_doc_date_0


doc = fpdf.FPDF(format = 'letter', unit = 'pt')
set_doc_date_0(doc)
doc.add_page()

my_text_size = 36
spacing = 1.15
doc.set_font('Arial', size=my_text_size)
text = ('Lorem ipsum Ut nostrud irure reprehenderit anim nostrud dolore sed '
        'ut Excepteur dolore ut sunt irure consectetur tempor eu tempor '
        'nostrud dolore sint exercitation aliquip velit ullamco esse dolore '
        'mollit ea sed voluptate commodo amet eiusmod incididunt Excepteur '
        'Excepteur officia est ea dolore sed id in cillum incididunt quis ex '
        'id aliqua ullamco reprehenderit cupidatat in quis pariatur ex et '
        'veniam consectetur et minim minim nulla ea in quis Ut in '
        'consectetur cillum aliquip pariatur qui quis sint reprehenderit '
        'anim incididunt laborum dolor dolor est dolor fugiat ut officia do '
        'dolore deserunt nulla voluptate officia mollit elit consequat ad '
        'aliquip non nulla dolor nisi magna consectetur anim sint officia '
        'sit tempor anim do laboris ea culpa eu veniam sed cupidatat in anim '
        'fugiat culpa enim Ut cillum in exercitation magna nostrud aute '
        'proident laboris est ullamco nulla occaecat nulla proident '
        'consequat in ut labore non sit id cillum ut ea quis est ut dolore '
        'nisi aliquip aute pariatur ullamco ut cillum Duis nisi elit sit '
        'cupidatat do Ut aliqua irure sunt sunt proident sit aliqua in '
        'dolore Ut in sint sunt exercitation aliquip elit velit dolor nisi ')


# ln = 0: to the right
# ln = 1: to new line, left margin
# ln = 2: below last item

##
doc.multi_cell(w = 144, h = my_text_size * spacing, border = 1, txt = text[:29], fill = 0, link = '', ln = 0)
doc.multi_cell(w = 180, h = my_text_size * spacing, border = 1, txt = text[29:60], fill = 0, link = '', ln = 2)
doc.multi_cell(w = 144, h = my_text_size * spacing, border = 1, txt = text[60:90], fill = 0, link = '', ln = 1)
doc.cell(w = 72 * 5, h = my_text_size * spacing, border = 1, ln = 1, txt = 'Lorem ipsum Sunt magna eiusmod deserunt in sunt cupidatat tempor eu sed laboris sint aliquip dolor anim.')
doc.cell(w = 72 * 5, h = my_text_size * spacing, border = 1, ln = 1, txt = 'Lorem ipsum Sunt magna eiusmod deserunt in sunt cupidatat tempor eu sed laboris sint aliquip dolor anim.')
doc.cell(w = 72 * 5, h = my_text_size * spacing, border = 1, ln = 1, txt = 'Lorem ipsum Sunt magna eiusmod deserunt in sunt cupidatat tempor eu sed laboris sint aliquip dolor anim.')
doc.cell(w = 72 * 5, h = my_text_size * spacing, border = 1, ln = 1, txt = 'Lorem ipsum Sunt magna eiusmod deserunt in sunt cupidatat tempor eu sed laboris sint aliquip dolor anim.')
doc.cell(w = 72 * 5, h = my_text_size * spacing, border = 1, txt = 'Lorem ipsum Sunt magna eiusmod deserunt in sunt cupidatat tempor eu sed laboris sint aliquip dolor anim.')
# print(doc.get_x(), doc.get_y())
doc.cell(w = 1, h = my_text_size * spacing, border = 0, ln = 2, txt = '')

doc.multi_cell(w = 144, h = my_text_size * spacing, border = 1, txt = text[30:90], fill = 0, link = '', ln = 2)

# 'after multi_cell' + str((doc.get_x(), doc.get_y()))
doc.cell(w = 72 * 2, h = my_text_size * spacing, border = 1, ln = 2, txt = 'Lorem ipsum')
doc.get_x(), doc.get_y()
doc.cell(w = 72 * 2, h = my_text_size * spacing, border = 1, ln = 2, txt = 'Lorem ipsum')
doc.get_x(), doc.get_y()
# print(doc.cell(w = 72 * 2, h = my_text_size * spacing, border = 1, ln = 2, txt = 'Lorem ipsum'))
# print(doc.get_x(), doc.get_y())
# print(doc.cell(w = 72 * 2, h = my_text_size * spacing, border = 1, ln = 2, txt = 'Lorem ipsum'))
# print(doc.get_x(), doc.get_y())


outfile = relative_path_to('output.pdf')
doc.output(outfile)
