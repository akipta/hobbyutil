'''
Treat lines of a file like a set.

Run with no command line arguments to see a usage statement.

---------------------------------------------------------------------------
Copyright (C) 2005, 2009 Don Peterson
Contact:  gmail.com@someonesdad1

                         The Wide Open License (WOL)

Permission to use, copy, modify, distribute and sell this software and its
documentation for any purpose is hereby granted without fee, provided that
the above copyright notice and this license appear in all source copies.
THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF
ANY KIND. See http://www.dspguru.com/wide-open-license for more
information.
'''

import sys, getopt, re


out = sys.stdout.write
err = sys.stderr.write
nl = "\n"

ignore_whitespace = False
ignore_regexps    = []
sort_results      = True
element_string    = None

def Usage(status):
    print '''Usage:  fset.py [options] op file1 file2 [file3 ...]
  where op is the operation:
    ne               Lines in file1 are != to the lines in following files
    eq[ual]          Lines in file1 are == to the lines in following files
    el[ement]        file1 contains the string given as file2 as an element
    di[fference]     Lines in file1 that are not in the following files
    sd[ifference]  * Lines that are in file1 or the remaining files, but 
                        not both (symmetric difference)
    in[tersection]   Lines that are common to all files
    is[subset]     * Determine whether file1 is a proper subset of
                        remaining files
    un[ion]          Lines that are in any of the files
  Performs operations on the lines of a file as if they were members of
  a set.  In the operations marked with '*', file2 and subsequent files
  will be collapsed into one set of lines.

  ne, eq, el, and is return Boolean values and also indicate the state by
  returning 0 for true and 1 for false (i.e., their exit codes).  The other
  operations return the resulting lines.  They will be stripped of leading
  and trailing whitespace if you use the -w option.

  Output is sent to stdout and is sorted; use the -s option if you don't
  want the lines sorted (they will be in an indeterminate order, however,
  as a set has no notion of ordering).
  
Options
    -i regexp
        Ignore lines that contain the regexp.  More than one of these 
        options may be given.
    -s 
        Do not sort the output lines.
    -w 
        ignore leading and trailing whitespace.
'''
    sys.exit(status)

def CheckArgs(args):
    if len(args) < 3:
        Usage(1)
    try:
        op = args[0][:2]
        if op not in ("ne", "eq", "el", "di", "sd", "in", "is", "un"):
            err("'%s' is not a recognized operation" % args[0] + nl)
            exit(1)
    except Exception:
        Usage(1)
    args[0] = op
    if op in ("sd", "is", "el"):
        if len(args) != 3:
            Usage(1)
    return args

def ParseCommandLine():
    if len(sys.argv) < 2:
        Usage(1)
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "i:sw")
    except getopt.GetoptError as e:
        msg, option = e
        out(msg + nl)
        sys.exit(1)
    for opt in optlist:
        if opt[0] == "-i":
            r = re.compile(opt[1])
            ignore_regexps.append(r)
        if opt[0] == "-s":
            global sort_results
            sort_results = False
        if opt[0] == "-w":
            global ignore_whitespace
            ignore_whitespace = True
    if len(args) < 2:
        Usage()
    return CheckArgs(args)

def GetLines(op, files):
    def do_not_ignore(line, r):
        mo = r.search(line)
        if not mo:
            return True
        return False
    lines1 = open(files[0]).readlines()
    lines2 = []
    if op == "el":
        lines2 = []
        global element_string
        element_string = files[1] + nl
    else:
        for file in files[1:]:
            lines2 += open(file).readlines()
        if ignore_regexps:
            for r in ignore_regexps:
                lines1 = [line for line in lines1 if do_not_ignore(line, r)]
                lines2 = [line for line in lines2 if do_not_ignore(line, r)]
        if ignore_whitespace:
            lines1 = [line.strip() for line in lines1]
            lines2 = [line.strip() for line in lines2]
    return frozenset(lines1), frozenset(lines2)

def main():
    args = ParseCommandLine()
    op = args[0]
    del args[0]
    files = args
    lines1, lines2 = GetLines(op, files)
    status = 0
    if op == "di":
        results = lines1 - lines2
    elif op == "sd":
        results = lines1 ^ lines2
    elif op == "in":
        results = lines1 & lines2
    elif op == "un":
        results = lines1 | lines2
    elif op == "ne":
        out(str(lines1 != lines2) + nl)
        if lines1 == lines2:
            status = 1
    elif op == "eq":
        out(str(lines1 == lines2) + nl)
        if lines1 != lines2:
            status = 1
    elif op == "el":
        if element_string in lines1:
            out(str(True) + nl)
        else:
            out(str(False) + nl)
            status = 1
    elif op == "is":
        out(str(lines1 <  lines2) + nl)
        if not lines1 < lines2:
            status = 1
    if op in ("di", "sd", "in", "un"):
        eol = ""
        if ignore_whitespace:
            eol = "\n"
        if sort_results:
            results = list(results)
            results.sort()
        for line in results:
            out(line + eol)

if __name__ == "__main__":
    main()
