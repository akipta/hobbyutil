'''
Find the radius of a circle given three points.  You can either give
the distances between the points or their Cartesian coordinates.  The
points will be taken from the datafile given on the command line.  If
you prefer, use the -i option and you'll be prompted for the input
data.

If you install the python uncertainties module from
http://pypi.python.org/pypi/uncertainties/ or
http://packages.python.org/uncertainties/, you'll be able to include
uncertainties in the input numbers and see their effects on the output
radius.

Run the program with no command line parameters to get a manpage.

-----------------------------------------------------------------
Copyright (C) 2013 Don Peterson
Contact:  gmail.com@someonesdad1

The Wide Open License (WOL)

Permission to use, copy, modify, distribute and sell this
software and its documentation for any purpose is hereby granted
without fee, provided that the above copyright notice and this
license appear in all source copies.  THIS SOFTWARE IS PROVIDED
"AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF ANY KIND. See
http://www.dspguru.com/wide-open-license for more information.
'''

import sys, os, getopt
from math import *
from sig import sig


have_unc = False

try:
    from uncertainties import ufloat, AffineScalarFunc
    from uncertainties.umath import acos, sqrt, sin, cos
    have_unc = True
except ImportError:
    from math import acos, sqrt, sin, cos

if sys.version_info[0] == 3:
    Input = input
else:
    Input = raw_input

def Det(a, b, c, d, e, f, g, h, i):
    '''Calculate a 3x3 determinant:

        | a b c |
        | d e f |
        | g h i |
    '''
    return a*(e*i - h*f) - b*(d*i - g*f) + c*(d*h - g*e)

def Circ3Points(x1, y1, x2, y2, x3, y3):
    '''Returns the radius of the circle that passes through the three
    points (x1, y1), (x2, y2), and (x3, y3).
    This is equations 30-34 from
    http://mathworld.wolfram.com/Circle.html.
    '''
    h = lambda x, y:  x**2 + y**2
    h1, h2, h3 = h(x1, y1), h(x2, y2), h(x3, y3)
    a =  Det(x1, y1, 1, x2, y2, 1, x3, y3, 1)
    d = -Det(h1, y1, 1, h2, y2, 1, h3, y3, 1)
    e =  Det(h1, x1, 1, h2, x2, 1, h3, x3, 1)
    f = -Det(h1, x1, y1, h2, x2, y2, h3, x3, y3)
    if not a:
        raise ValueError("Collinear points")
    if have_unc:
        if isinstance(a, AffineScalarFunc) and not a.nominal_value:
            msg = "Collinearity:  an uncertain divisor is %s" % sig(a)
            raise ValueError(msg)
    r = sqrt(h(d, e)/(4*a*a) - f/a)
    return r

def Circ3Dist(a, b, c):
    '''Given a triangle with sides a, b, c, returns the radius of the
    circle which passes through the three points.  This is turned into
    the circle from 3 points problem by putting the longest side on
    the x axis with one point at the origin.  Then use the cosine law
    to find the coordinates of the third point.
    '''
    m = [a, b, c]
    m.sort()
    c, b, a = m
    # Now a is longest, b next, and c shortest
    x1, y1 = 0, 0
    x2, y2 = a, 0
    try:
        B = acos((a*a + c*c - b*b)/(2*a*c))
    except ValueError:
        raise ValueError("The three distances don't make a triangle")
    x3, y3 = c*cos(B), c*sin(B)
    return Circ3Points(x1, y1, x2, y2, x3, y3)


def out(*v, **kw):
    sep = kw.setdefault("sep", " ")
    nl  = kw.setdefault("nl", True)
    stream = kw.setdefault("stream", sys.stdout)
    if v:
        stream.write(sep.join([str(i) for i in v]))
    if nl:
        stream.write("\n")

def err(s, **kw):
    kw["stream"] = sys.stderr
    out(s, **kw)

def Error(msg, status=1):
    out(msg, stream=sys.stderr)
    exit(status)

def Usage(d, status=1):
    name = sys.argv[0]
    s = '''
Usage:  {name} [options] [datafile]
  Print the radius of a circle given three points.  You can either
  give the distances between the three points or their Cartesian
  coordinates.  The points will be taken from the datafile given on
  the command line.  If you prefer, use the -i option and you'll be
  prompted for the input data (you can use assignments and
  uncertainties like in the datafile).
 
  Lines allowed in the datafile (can be expressions):
    a = b           Defines a variable (math symbols in scope)
    x, y            Defines a point in Cartesian coordinates
    a               Defines a distance
 
  If you use a line with a comma, then the program assumes that it and
  the following lines are Cartesian coordinates; there must be three
  such lines.  If there's a line with no comma or '=' character, then
  it's a distance between two points.  There must be three such lines.
 
  Blank lines and lines that begin with a '#' after leading whitespace
  is removed are ignored.

  Points and distances can be followed by [e] where e is an
  expression.  This denotes the uncertainty of that measured value.
  If one or more uncertainties are given, then the calculated radius
  will also have an uncertainty.  The output will be in the usual
  short-hand form:  1.234(5) denotes a measured value 1.234 with an
  uncertainty of 0.005.
 
  You'll have to install the python uncertainties module from
  http://packages.python.org/uncertainties/ in order to use
  uncertainties.  If it's not installed, the uncertainties will just
  be ignored.

Options:
    -d digits
        Set the number of significant digits for the report.
    -i 
        Prompt interactively for the input data.

Examples/checks:
  1.  Enter the three sides 2, sqrt(2), and sqrt(2).  You should get a
      circle of radius 1.

  2.  Enter the points 
        e = 0.1
        1 [e], 0 [e]
        -1 [e], 0 [e]
        0 [e], 1 [e]
      You should get a circle of radius 1.00(7); this means the
      circle's radius is 1 with an uncertainty of 0.07.
'''[1:-1]
    out(s.format(**locals()))
    sys.exit(status)

def ParseCommandLine(d):
    d["-i"] = False
    sig.digits = 4
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "d:i")
    except getopt.GetoptError as e:
        msg, option = e
        out(msg)
        exit(1)
    for opt in optlist:
        if opt[0] == "-d":
            digits = int(opt[1])
            if digits < 1:
                Error("-d option must be integer > 0")
            sig.digits = digits
        if opt[0] == "-i":
            d["-i"] = True
            return None
    if len(args) != 1:
        Usage(d)
    return args[0]

def GetDataInteractively(d):
    __order = [" first", "second", " third"]
    while True:
        __s = Input("Enter distances [d] or points (p)?  ").strip().lower()
        if not __s:
            __s = "d"
            break
        elif __s in set("dpq"):
            break
    if __s == "q":
        exit(0)
    if __s == "d":
        # Distances
        __dist = [0, 0, 0]
        for __i in range(3):
            while True:
                __s = Input("Enter the %s distance:  " % __order[__i]).strip().lower()
                if __s == "q":
                    exit(0)
                elif "=" in __s:
                    try:
                        exec(__s)
                        out("Assignment OK")
                    except Exception as e:
                        out("Assignment failed:  %s" % str(e))
                    continue
                try:
                    x = InterpretNum(__s, Dict(locals()))
                    __dist[__i] = x
                    break
                except Exception:
                    pass
        d["distances"] = __dist
    else:
        # Points
        __coord = [0, 0, 0]
        out("  Note:  enter points as two numbers 'x, y' separated by a comma")
        for __i in range(3):
            while True:
                __s = Input("Enter the %s point:  " % __order[__i]).strip().lower()
                if __s == "q":
                    exit(0)
                elif "=" in __s:
                    try:
                        exec(__s)
                        out("Assignment OK")
                    except Exception as e:
                        out("Assignment failed:  %s" % str(e))
                    continue
                try:
                    __f = __s.split(",")
                    if len(__f) != 2:
                        out("Your input must have only one comma")
                    else:
                        __x = InterpretNum(__f[0], Dict(locals()))
                        __y = InterpretNum(__f[1], Dict(locals()))
                        __coord[__i] = (__x, __y)
                        break
                except Exception:
                    pass
        d["coordinates"] = __coord
    out()

def Dict(vars):
    '''vars is a dictionary of local variables.  Remove all variables
    that begin with two underscores and also remove d.
    '''
    del vars["d"]
    keys = vars.keys()
    for k in keys:
        if len(k) > 2 and k[:2] == "__":
            del vars[k]
    return vars

def InterpretNum(__s, __vars):
    '''__s is a string that can be of the forms e.g. '12.3' or '12.3
    [0.1]' where the second form denotes an uncertainty.  The numbers
    can also be expressions using the variables in the __vars
    dictionary.  Evaluate the string and return either a floating
    point number or a ufloat.
    '''
    # Get vars into our local namespace
    for __k in __vars:
        exec("%s = __vars['%s']" % (__k, __k))
    try:
        if "[" in __s:
            __locl, __locr = __s.find("["), __s.find("]")
            if __locl > __locr:
                raise Exception("Improperly formed uncertainty")
            __mean = float(eval(__s[:__locl]))
            __stddev = float(eval(__s[__locl + 1:__locr]))
            if have_unc:
                return ufloat(__mean, __stddev)
            else:
                return __mean
        else:
            return float(eval(__s))
    except Exception as __e:
        Error("Can't evaluate '%s'\n%s" % (__s, str(__e)))

def ReadDatafile(__datafile, __d):
    __lines = [__i.strip() for __i in open(__datafile).readlines()]
    __dist, __coord = [], []
    __e = Exception("Can't mix distances and coordinates")
    try:
        for __i, __line in enumerate(__lines):
            __linenum = __i + 1
            if not __line or __line[0] == "#":
                continue
            if "=" in __line:
                # Variable definition
                exec(__line)
            elif "," in __line:
                # Coordinates
                __x, __y = __line.split(",")
                __x = InterpretNum(__x, locals())
                __y = InterpretNum(__y, locals())
                __coord.append((__x, __y))
                if __dist:
                    raise __e
            else:
                __dist.append(InterpretNum(__line, locals()))
                if __coord:
                    raise __e
        if __coord:
            __d["coordinates"] = __coord
        elif __dist:
            __d["distances"] = __dist
    except Exception as __e:
        __msg = "Line %d is bad in datafile '%s'\n" % (__linenum, __datafile)
        __msg += "  Line:  '%s'\n" % __line
        __msg += "  Error:  %s" % str(__e)
        Error(__msg)

def Coordinates(d):
    (x1, y1), (x2, y2), (x3, y3) = d["coordinates"]
    try:
        r = Circ3Points(x1, y1, x2, y2, x3, y3)
        s = [(x1, y1), (x2, y2), (x3, y3)]
        return r, s
    except Exception as e:
        X1, Y1 = sig(x1), sig(y1)
        X2, Y2 = sig(x2), sig(y2)
        X3, Y3 = sig(x3), sig(y3)
        err = str(e)
        msg = '''Couldn't calculate radius from coordinates:
            {X1}, {Y1}
            {X2}, {Y2}
            {X3}, {Y3}
  Error:  {err}'''.format(**locals())
        Error(msg)

def Distances(d):
    a, b, c = d["distances"]
    try:
        return Circ3Dist(a, b, c), (a, b, c)
    except Exception as e:
        Error(str(e))

def Report(r, s, d):
    prob_type = "three distances" if isinstance(s, tuple) else "three points"
    out("Circle from {prob_type}:".format(**locals()))
    if isinstance(s, tuple):
        out("  Distances:")
        for i in s:
            out("    ", sig(i))
    else:
        indent, w = " "*4, 15
        out(indent, "{0:^{1}}".format("x", w), "{0:^{1}}".format("y", w))
        h = "{0:>{1}}".format("-"*w, w)
        out(indent, h, h)
        for x, y in s:
            sx = "{0:>{1}}".format(sig(x), w)
            sy = "{0:>{1}}".format(sig(y), w)
            out("    ", sx, sy)
    out("\nRadius of circle   =", sig(r))
    out("Diameter of circle =", sig(2*r))

def main():
    d = {} # Options dictionary
    datafile = ParseCommandLine(d)
    if d["-i"]:
        GetDataInteractively(d)
    else:
        ReadDatafile(datafile, d)
    if "coordinates" in d:
        r, s = Coordinates(d)
    else:
        r, s = Distances(d)
    Report(r, s, d)

if __name__ == "__main__":
    main()
