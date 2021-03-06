'''
Dedent a chunk of text, which means to remove the common beginning
space characters.
'''

from __future__ import division, print_function
import sys
import os
import getopt
import textwrap

def Usage(d, status=1):
    name = sys.argv[0]
    s = '''
Usage:  {name} [options] [file1 [file2...]]
  Remove the common space characters from the lines in the
  concatenated files (or stdin if no files given).

Options:
    -h 
        Print a manpage.
'''[1:-1]
    print(s.format(**locals()))
    sys.exit(status)

def ParseCommandLine(d):
    try:
        optlist, filenames = getopt.getopt(sys.argv[1:], "h")
    except getopt.GetoptError as e:
        msg, option = e
        print(msg)
        exit(1)
    for opt in optlist:
        if opt[0] == "-h":
            Usage(d, status=0)
    return filenames

def main():
    opt, text = {}, []
    filenames = ParseCommandLine(opt)
    if not filenames:
        text.append(sys.stdin.read())
    else:
        for filename in filenames:
            with open(filename, "rU") as f:
                text.append(f.read())
    print(textwrap.dedent(''.join(text)))

main()
