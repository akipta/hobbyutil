'''
Make a words file from the index.sense file included in the WordNet
3.0 release.

---------------------------------------------------------------------------
Copyright (C) 2012 Don Peterson
Contact:  gmail.com@someonesdad1
  
                         The Wide Open License (WOL)
  
Permission to use, copy, modify, distribute and sell this software and its
documentation for any purpose is hereby granted without fee, provided that
the above copyright notice and this license appear in all copies.
THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF
ANY KIND. See http://www.dspguru.com/wide-open-license for more
information.
'''

import sys, os, getopt

def out(*v, **kw):
    sep = kw.setdefault("sep", " ")
    nl  = kw.setdefault("nl", True)
    stream = kw.setdefault("stream", sys.stdout)
    if v:
        stream.write(sep.join([str(i) for i in v]))
    if nl:
        stream.write("\n")

def Usage(d, status=1):
    name = sys.argv[0]
    s = '''
Usage:  {name} input_file output_words_file
  Make an ASCII text file that is the list of words in the index.sense
  file of the WordNet 3.0 distribution.
'''[1:-1]
    out(s.format(**locals()))
    sys.exit(status)

def ParseCommandLine(d):
    if len(sys.argv) < 3:
        Usage(d)
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "h")
    except getopt.GetoptError as str:
        msg, option = str
        out(msg)
        sys.exit(1)
    for opt in optlist:
        if opt[0] == "-h":
            Usage(d, status=0)
    if len(args) != 2:
        Usage(d)
    return args

def GetWords(infile):
    # Note underscores are NOT replaced with space characters
    words = set()
    for line in open(infile).readlines():
        if line[:2] == " "*2:
            # Ignore license lines 
            continue
        words.add(line[:line.find("%")].lower())
    return words

def WriteOutput(words, outfile):
    w = list(words)
    w.sort()
    ofp = open(outfile, "w")
    for word in w:
        ofp.write(word + "\n")

def main():
    d = {} # Options dictionary
    infile, outfile = ParseCommandLine(d)
    words = GetWords(infile)
    WriteOutput(words, outfile)

main()
