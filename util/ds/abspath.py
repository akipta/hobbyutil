'''
Return the path on the command line as an absolute path.
'''

from __future__ import print_function
import os, sys
from pdb import set_trace as xx

if len(sys.argv) == 1:
    print("Need a path argument", file=sys.stderr)
    exit(1)
s = os.path.abspath(sys.argv[1]).replace("\\", "/")
print(s)
