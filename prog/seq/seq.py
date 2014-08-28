'''
Usage:  {name} [options] n [m [inc]]
  Generate an arithmetical progression from n to m in steps of inc.
  If only n is given, the sequence goes from 1 to int(n).  inc
  defaults to 1.  The arguments n, m, and inc can be integers,
  floating point numbers, or improper fractions such as '5/3'.

  For some floating point inc values, you may get a finishing value in
  the sequence larger than m.

  Use the -t option to see some examples.

Options
    -0 
        Make the sequences 0-based instead of 1-based.
    -d digits
        Change the number of significant digits in the output.  digits
        defaults to {digits}.
    -e
        Don't include the end point of the sequence.
    -n 
        Don't include a newline after the numbers.
    -s 
        Use the sig library to output the specified number of
        significant digits.  Normal output is to use "%g" string
        interpolation, which truncates trailing zeros.
    -t 
        Show some examples.
    -x 
        Allow expressions in n, m, and inc.  The math module's symbols
        are in scope.  Unless the result of an expression is an
        integer, the results will be floating point (i.e., fractions
        will be evaluated away).
'''

# Copyright (C) 2014 Don Peterson
# Contact:  gmail.com@someonesdad1
#   
#                   The Wide Open License (WOL)
#   
# Permission to use, copy, modify, distribute and sell this software and
# its documentation for any purpose is hereby granted without fee,
# provided that the above copyright notice and this license appear in
# all copies.  THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT EXPRESS OR
# IMPLIED WARRANTY OF ANY KIND. See
# http://www.dspguru.com/wide-open-license for more information.

import sys, os, getopt
from out import out
from fractions import Fraction
from frange import frange, Rational as R
from math import *
from sig import sig

from pdb import set_trace as xx


def Error(msg, status=1):
    out(msg, stream=sys.stderr)
    exit(status)

def Usage(d, status=1):
    name = d["name"]
    digits = d["-d"]
    out(__doc__.strip().format(**locals()))
    sys.exit(status)

def ParseCommandLine(d):
    d["-0"] = False     # 0-based sequences
    d["-d"] = 3         # Number of significant digits
    d["-e"] = True      # Include end point
    d["-n"] = True      # If True, include newline after number
    d["-s"] = False     # Use sig if True
    d["-t"] = False     # Run test cases
    d["-x"] = False     # Allow expressions
    d["name"] = os.path.split(sys.argv[0])[1]
    if len(sys.argv) < 2:
        Usage(d)
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "0d:ehnstx")
    except getopt.GetoptError as e:
        msg, option = e
        out(msg)
        exit(1)
    for opt in optlist:
        if opt[0] == "-0":
            d["-0"] = True
        if opt[0] == "-d":
            try:
                d["-d"] = int(opt[1])
                if not (1 <= d["-d"] <= 15):
                    raise ValueError()
            except ValueError:
                msg = "-d option's argument must be an integer between 1 and 15"
                Error(msg)
        if opt[0] == "-e":
            d["-e"] = False
        if opt[0] == "-h":
            Usage(d, status=0)
        if opt[0] == "-n":
            d["-n"] = False
        if opt[0] == "-s":
            d["-s"] = True
        if opt[0] == "-t":
            d["-t"] = True
        if opt[0] == "-x":
            d["-x"] = True
    sig.digits = d["-d"]
    if not d["-t"] and len(args) not in range(1, 4):
        Usage(d)
    return args

def GetParameters(args, d):
    '''Return n, m, inc as strings, suitably processed as
    expressions if the -x option was used.
    '''
    def f(x):
        return repr(eval(x, globals())) if d["-x"] else x
    if len(args) == 1:
        n, m, inc = "0" if d["-0"] else "1", f(args[0]), "1"
    elif len(args) == 2:
        n, m, inc = f(args[0]), f(args[1]), "1"
    else:
        n, m, inc = [f(i) for i in args]
    return (n, m, inc)

def Fractions(n, m, inc, d):
    for i in frange(n, m, inc, impl=R, return_type=R, 
                    include_end=d["-e"]):
        out(i, "", nl=d["-n"])
    if not d["-n"]:
        out()

def FloatingPoint(n, m, inc, d):
    fmt = "%%.%dg" % d["-d"]
    for i in frange(n, m, inc, include_end=d["-e"]):
        if i <= float(m):
            if d["-s"]:
                out(sig(i), "", nl=d["-n"])
            else:
                out(fmt % i, "", nl=d["-n"])
    if not d["-n"]:
        out()

def Integers(n, m, inc, d):
    for i in frange(n, m, inc, return_type=int, include_end=d["-e"]):
        if i <= int(m):
            out(i, "", nl=d["-n"])
    if not d["-n"]:
        out()

def ShowExamples(d):
    '''Print some examples.
    '''
    d["-n"] = False
    f = "%-20s "
    out("Output for various command line arguments:\n")
    #
    out(f % "'-n 8'  ", nl=0)
    Integers(1, 8, 1, d)
    #
    out(f % "'-n -e 8'  ", nl=0)
    d["-e"] = False
    Integers(1, 8, 1, d)
    d["-e"] = True
    #
    out(f % "'-n -0 8'  ", nl=0)
    Integers(0, 8, 1, d)
    #
    d["-e"] = False
    out(f % "'-n -0 -e 8'  ", nl=0)
    Integers(0, 8, 1, d)
    d["-e"] = True
    #
    out()
    out(f % "'-n 0 1 1/8'  ", nl=0)
    Fractions(0, 1, "1/8", d)
    #
    out(f % "'-n -e 0 1 1/8'  ", nl=0)
    d["-e"] = False
    Fractions(0, 1, "1/8", d)
    d["-e"] = True
    #
    out()
    out(f % "'-n 1 6 0.75'  ", nl=0)
    FloatingPoint(1, 6, "0.75", d)
    #
    out(f % "'-n 1 6 3/4'  ", nl=0)
    Fractions(1, 6, "3/4", d)
    #
    out(f % "'-n -e 1 6 0.75'  ", nl=0)
    d["-e"] = False
    FloatingPoint(1, 6, "0.75", d)
    d["-e"] = True
    #
    out(f % "'-n -e 1 6 3/4'  ", nl=0)
    d["-e"] = False
    Fractions(1, 6, "3/4", d)
    d["-e"] = True
    #
    out(f % "'-n -s 1 6 0.75'  ", nl=0)
    d["-s"] = False
    FloatingPoint(1, 6, "0.75", d)
    d["-s"] = True
    exit(0)

def main():
    d = {} # Options dictionary
    args = ParseCommandLine(d)
    if d["-t"]:
        ShowExamples(d)
    n, m, inc = GetParameters(args, d)
    # fp identifies a floating point string
    fp = lambda s:  s.find(".") != -1 or s.lower().find("e") != -1
    # fr identifies a fraction string
    fr = lambda s:  s.find("/") != -1
    if any([fr(s) for s in (n, m, inc)]):   # Fractions
        Fractions(n, m, inc, d)
    elif any([fp(s) for s in (n, m, inc)]): # Floating point
        FloatingPoint(n, m, inc, d)
    else:   # Integers
        Integers(n, m, inc, d)
main()
