import inspect
import sys
import os

def relative_path_to(place):
  """Finds Relative Path to a place

  Works by getting the file of the caller module, then joining the directory
  of that absolute path and the place in the argument.
  """
  caller_file = inspect.getfile(sys._getframe(1))
  return os.path.join(os.path.dirname(os.path.abspath(caller_file)), place)

def compare_files_ignoring_CreationDate(new, known, assertEqualFunc):
  """This function compares two files ignoring their /CreationDate line

  It treats binary pdf formatted files as text, splits arbitrarily on "\n" and
  ignores lines containing CreationDate
  """
  predicate = lambda line: '/CreationDate' not in line
  python3 = sys.version_info >= (3, 0)

  if python3:
    with open(new, 'rt', encoding='latin1') as newfile, \
         open(known, 'rt', encoding='latin1') as knownfile:
      newfile     = [line for line in newfile   if predicate(line)]
      knownfile   = [line for line in knownfile if predicate(line)]

      for line_new, line_known in zip(newfile, knownfile):
        assertEqualFunc(line_new, line_known, "all lines equal")

  else:
    with open(new, 'rt') as newfile, open(known, 'rt') as knownfile:
      newfile     = [line for line in newfile   if predicate(line)]
      knownfile   = [line for line in knownfile if predicate(line)]

      for line_new, line_known in zip(newfile, knownfile):
        assertEqualFunc(line_new, line_known, "all lines equal")

def compare_files_ignoring_string(new, known, bad_string, assertEqualFunc):
  """This function compares two files ignoring lines containing a string

  It treats binary pdf formatted files as text, splits arbitrarily on "\n" and
  ignores lines containing CreationDate
  """
  predicate = lambda line: bad_string not in line
  python3 = sys.version_info >= (3, 0)

  if python3:
    with open(new, 'rt', encoding='latin1') as newfile, \
         open(known, 'rt', encoding='latin1') as knownfile:
      newfile     = [line for line in newfile   if predicate(line)]
      knownfile   = [line for line in knownfile if predicate(line)]

      for line_new, line_known in zip(newfile, knownfile):
        assertEqualFunc(line_new, line_known, "all lines equal")

  else:
    with open(new, 'rt') as newfile, open(known, 'rt') as knownfile:
      newfile     = [line for line in newfile   if predicate(line)]
      knownfile   = [line for line in knownfile if predicate(line)]

      for line_new, line_known in zip(newfile, knownfile):
        assertEqualFunc(line_new, line_known, "all lines equal")
