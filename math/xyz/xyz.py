__doc__ = '''
Utility to use affine transformations on a set of points and print
them out in a Cartesian or other coordinate system.  See xyz.pdf for
details.

If you want to use numbers with uncertainty, you'll have to install
the python uncertainties library
https://pypi.python.org/pypi/uncertainties/.
 
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

import sys, os, getopt, time, traceback
from math import *
from itertools import combinations
from geom_prim import *

from pdb import set_trace as xx
if 0:
    import debug
    debug.SetDebugger()

have_unc = False
try:
    # Note these will replace all of math's symbols except pi and e
    from uncertainties.umath import (
        acos, acosh, asin, asinh, atan, atan2, atanh, ceil, copysign, cos,
        cosh, degrees, exp, fabs, factorial, floor, fmod, frexp, fsum,
        hypot, isinf, isnan, ldexp, log, log10, log1p, modf, pow,
        radians, sin, sinh, sqrt, tan, tanh, trunc)
    from uncertainties import ufloat, UFloat
    have_unc = True
except ImportError:
    pass

pyver = sys.version_info[0]
if pyver == 3:
    long = int

_debug = False

# _test is set to True for test purposes.  It will disable the exit
# from Error() and allow the error message to be put in _test_msg.
_test = False
_test_msg = ""

Sig = sig = Ctm._sig
ii = isinstance

# This is a geometric object that will live for the life of the
# script.  It calls Ctm's constructor and after this point we can set
# Ctm's class variables without fear they'll be destroyed by all of
# the geometric objects going out of scope and garbage collected.
_geom_obj = Point()

class odict(dict):
    '''Bare-bones ordered dictionary that keeps track of the order
    items were entered.
    '''
    def __init__(self):
        self._seq = []
    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._seq.remove(key)
    def __setitem__(self, key, value):
        if key not in self:
            self._seq.append(key)
        dict.__setitem__(self, key, value)
    def __repr__(self):
        s = "odict{"
        t = []
        for i in self._seq:
            t.append(repr(i) + ": " + repr(self[i]))
        s += ", ".join(t)
        s += "}"
        return s
    def __iter__(self):
        return iter(self._seq)
    def keys(self):
        return self._seq[:]

def Rnd(x):
    if not eps:
        return x
    if ii(x, float):
        if abs(x) < eps:
            x = 0
    elif have_unc and ii(x, (AffineScalarFunc, Variable)):
        if x.std_dev > eps and abs(x.nominal_value) < eps:
            x.nominal_value = 0
    return x

def out(*v, **kw):
    sep = kw.setdefault("sep", " ")
    nl  = kw.setdefault("nl", True)
    stream = kw.setdefault("stream", sys.stdout)
    if v:
        stream.write(sep.join([str(i) for i in v]))
    if nl:
        stream.write("\n")

def err(*s, **kw):
    kw["stream"] = sys.stderr
    out(*s, **kw)

def dbg(*s, **kw):
    # If _debug is True, send information to stderr.  Preface each
    # line with a '+' character to make it easier to spot the debug
    # lines in regular output.
    if _debug:
        kw["stream"] = sys.stderr
        out("+", *s, **kw)

def Error(msg, status=1):
    if _test:
        global _test_msg
        _test_msg = msg
    else:
        out(msg, stream=sys.stderr)
        exit(status)

def Usage(d, status=1):
    name = sys.argv[0]
    s = '''
Usage:  {name} [options] [datafile]
  Script to transform points, lines, and planes in 2-dimensional or
  3-dimensional space using translations, rotations, and dilatations.
  See xyz.pdf for usage information.

Options:
    -a
        When the bare 'print' command is used, print variable values
        too; normally, only points, lines, and planes are printed.
    -D 
        When a command is executed, any exceptions are caught.  If
        you're trying to figure out what went wrong, it may be easier
        if the script didn't catch the exception.  The -D option turns
        this exception catching off so that you'll see the backtrace
        of what happened.
    -d 
        Turn debugging output on.  This echoes the lines and their
        results to the screen.
    -r 
        Make radians the default angle measure (degrees are normally
        the default).
    -s sep
        Define the separation string to split lines on.  Defaults
        to ",".  You cannot make it one or more space characters.
    -w 
        Exit with an error message when overwriting an existing
        geometrical object name (this is useful to find accidental
        duplication of names).  Note this won't work for variables
        that are defined in assignment statements (use -W for this).
    -W  
        Same as -w, but will exit with an error if you overwrite
        either an object or a variable.
'''[1:-1]
    out(s.format(**locals()))
    exit(status)

def ParseCommandLine(d):
    # Command line option settings
    d["-a"] = False         # Don't limit print to points, lines, and planes
    d["-d"] = False         # Turn debugging on
    d["-D"] = False         # Don't use try/except on dispatched commands
    d["-s"] = ","           # Line separation string
    d["-w"] = False         # Error when overwriting object names
    d["-W"] = False         # Error when overwriting object or variable names
    d["-@"] = None          # Read datafile from stdin
    # Other settings
    d["lines"] = []         # Will contain datafiles' lines
    d["vars"] = odict()     # Local variables for expressions
    d["coord_sys"] = "rect" # Coordinate system for output
    d["width"] = 15         # Width of report's x, y, mass columns
    d["name_width"] = 15    # Width of report name column
    d["indent"] = ""        # String to indent output by
    d["alphabetical"] = False   # If true, sort output objects by name
    # Set up the default angle units 
    Ctm._angle = 180/pi     # Divide by this to get radians
    Ctm._angle_name = "deg"
    if len(sys.argv) < 2:
        Usage(d)
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "@acDdrs:wW")
    except getopt.GetoptError as e:
        msg, option = e
        out(msg)
        exit(1)
    for opt in optlist:
        if opt[0] == "-@":
            d["-@"] = True
        if opt[0] == "-a":
            d["-a"] = True
        if opt[0] == "-D":
            d["-D"] = True
        if opt[0] == "-d":
            global _debug
            _debug = True
        if opt[0] == "-r":
            Ctm._angle = 1
            Ctm._angle_name = "rad"
        if opt[0] == "-s":
            d["-s"] = opt[1].strip()
            if not d["-s"]:
                Error("-s option cannot be only whitespace")
        if opt[0] == "-W":
            d["-W"] = True
        if opt[0] == "-w":
            d["-w"] = True
    if d["-@"]:
        return ["stdin"]
    elif len(args) != 1:
            Usage(d)
    return [args[0]]

def ReadDatafile(d):
    '''Read in the datafile.  Strip out comments and blank lines.
    Remove trailing whitespace from each line, but leave the leading
    whitespace (may be needed if it's python code).  Return a list of
    lines d["lines"] as (linenum, line_string).
    '''
    file = d["datafile"][-1]
    if file == "stdin":
        lines = sys.stdin.readlines()
    else:
        lines = open(file).readlines()
    L = []
    for i, line in enumerate(lines):
        # Remove comments
        loc = line.find("#")
        if loc != -1:
            line = line[:loc]
        # Remove trailing whitespace (leave the leading whitespace in
        # place for code lines)
        line = line.rstrip()
        if not line.strip():
            continue  # Ignore blank lines
        # If this is an include line, include the indicated file
        sline = line.strip()
        loc = sline.find("include")
        if loc == 0:
            sloc = sline.find(" ")
            if sloc == -1:
                Bad(i + 1, line, "Bad 'include' line", d)
            newfile = sline[sloc:].strip()
            d["datafile"].append(newfile)
            ReadDatafile(d)
            continue
        # Keep the original datafile line number, file, and the line
        L.append((i + 1, file, line))
    d["lines"] += L
    d["datafile"].pop()

def Interp(s, d, linenum=None, line=None):
    '''Interpret the string s as either an expression defining a value
    or as a string with a mean and optional uncertainty and physical
    unit.  The unit is ignored.  The value returned can be an int,
    float, or ufloat.
    '''
    s = s.strip()
    try:
        val = eval(s, None, d["vars"])
    except Exception:
        val, unit = Sig.Interpret(s, loc=d["vars"])
        if val is None:
            if linenum is not None:
                assert line is not None
                msg = "Line %s cannot be interpreted\n" % linenum
                msg += "  Line:  '%s'" % line
                Error(msg)
            else:
                raise ValueError("'%s' can't be interpreted" % s)
    # If val is a ufloat with a standard deviation of 0, we just
    # convert it to a float.
    if ii(val, UFloat):
        if not val.std_dev:
            val = val.nominal_value
    return val

def IsIdentifier(s):
    '''Return True if s is a valid python variable name.
    '''
    try:
        exec("%s = 0" % s)
        return True
    except SyntaxError:
        return False

def GetVar(linenum, line, d):
    '''The line contains an '=' character, so it's an assignment.
    '''
    try:
        loc = line.find("=")
        f = [line[:loc], line[loc + 1:]]
        name, val = f
        # Try to set a local variable using the name; if we get an
        # exception, the name isn't valid.
        exec("%s = 0" % name)
        value = eval(val, globals(), d["vars"])
        return value
    except SyntaxError as e:
        Bad(linenum, line, "bad variable name", d)
    except Exception as e:
        Bad(linenum, line, str(e), d)
        # It's not an expression, so assume it's a number with
        # optional uncertainty and/or unit.
        val, unit = Sig.Interpret(f[1])
        if val is None:
            Error(msg % (linenum, line, unit))
        return val

def Listify(list_):
    '''Return a string representing the list with each element
    separated with commas.
    '''
    return list_.replace("[", "").replace("]", "").replace("'", "")

def Eval(linenum, line, val, d):
    '''If val is an expression, return its value.  Otherwise,
    generate an error message.
    '''
    try:
        value = eval(val, globals(), d["vars"])
        return value
    except Exception as e:
        # It's not an expression, so assume it's a number with
        # optional uncertainty and/or unit.
        value, unit = Sig.Interpret(val)
        if unit or value is None:
            msg = "cannot interpret '%s' as expression or number" % val
            Bad(linenum, line, msg, d)
        return value

def Bad(linenum, line, errmsg, d):
    lines = []
    for i in traceback.extract_stack():
        lines.append(i[1])
    lines.reverse()
    scrlines = Listify(str(lines[1:]))
    msg = "Line %s is bad\n"
    msg += "  Backtrace:  %s\n"
    msg += "  Line '%s'\n"
    msg += "  Error: %s"
    Error(msg % (linenum, scrlines, line, errmsg))

def CheckOverwrite(name, d, linenum, line):
    if name not in d["vars"]:
        return
    o, allowed = d["vars"][name], (Point, Line, Plane)
    ot = "object" if ii(o, allowed) else "variable"
    msg = "Overwriting existing %s '%s'" % (ot, name)
    if d["-w"]:
        Bad(linenum, line, msg, d)
    elif d["-W"]:
        Bad(linenum, line, msg, d)

def GetObj(linenum, line, name, d):
    '''Return the object with the indicated name or print an error
    message.
    '''
    try:
        return d["vars"][name]
    except KeyError:
        # Object with that name isn't defined.  Let's see if we can
        # evaluate it as an expression.
        try:
            x = eval(name, globals(), d["vars"])
            return x
        except Exception:
            msg = "Can't interpret '%s'" % name
            Bad(linenum, line, msg, d)
        msg = "Object '%s' is not defined" % name
        Bad(linenum, line, msg, d)

def GetValues(linenum, line, d, name, x, y=None, z=None):
    '''Return a 3-tuple of numbers from their strings.  If the string
    is None, then it defaults to 0.
    '''
    if not IsIdentifier(name):
        Bad(linenum, line, "Name '%s' is not valid" % name, d)
    x = Eval(linenum, line, x, d)
    if y is not None:
        y = Eval(linenum, line, y, d)
        if z is not None:
            z = Eval(linenum, line, z, d)
            return (x, y, z)
        return (x, y, 0)
    return (x, 0, 0)

def Overwrite(name, obj, d):
    '''Exit if about to overwrite an existing object or variable
    (action depends on -w and -W options).
    '''
    msg = "Tried to overwrite %%s '%s'" % name
    if d["-w"] or d["-W"]:
        if ii(obj, Point) or ii(obj, Line) or ii(obj, Plane):
            # It's a geometrical object
            types = {Point:"point", Line:"line", Plane:"plane"}
            Bad(linenum, line, msg % types[type(obj)], d)
        else:
            if d["-W"]:
                # It's a variable
                Bad(linenum, line, msg % "variable", d)
    CheckOverwrite(name, d, linenum, line)
    d["vars"][name] = obj

def PointRect(linenum, line, kw, args, d, showdbg=True):
    # Note PointCyl and PointSph will use this same code, then convert
    # the received coordinates.
    if len(args) == 3:
        # . x, y, name 
        x, y, name = args
        x, y, z = GetValues(linenum, line, d, name, x, y)
        P = Point(x, y, z)
    elif len(args) == 4:
        if "=" in args[-1]:
            # . x, y, name, m=a
            x, y, name, assign = args
            x, y, z = GetValues(linenum, line, d, name, x, y)
            attr = args[-1].split("=")[0]
            if attr.strip() != "m":
                Bad(linenum, line, "Bad attribute '%s'" % attr, d)
            m = GetVar(linenum, assign, d)
            P = Point(x, y, z, m)
        else:
            # . x, y, z, name 
            x, y, z, name = args
            x, y, z = GetValues(linenum, line, d, name, x, y, z)
            P = Point(x, y, z)
    elif len(args) == 5:
        # . x, y, z, name, m=a
        x, y, z, name, assign = args
        if "=" not in assign:
            Bad(linenum, line, "Last argument should be assignment" % attr, d)
        x, y, z = GetValues(linenum, line, d, name, x, y, z)
        attr = assign.split("=")[0]
        if attr.strip() != "m":
            Bad(linenum, line, "Bad keyword '%s'" % attr, d)
        m = GetVar(linenum, assign, d)
        P = Point(x, y, z, m)
    else:
        Bad(linenum, line, "Improper number of parameters", d)
    if _debug and showdbg:
        dbg("[%s] %s =" % (linenum, name), str(P))
    CheckOverwrite(name, d, linenum, line)
    d["vars"][name] = P
    return (name, P)
    return ("point(rect)", (name, P))

def FixTheta(theta):
    '''Convert an azimuth angle to canonical polar coordinate measure.
    theta is assumed to be in radians.
    '''
    if Ctm._compass:
        if Ctm._neg:
            theta += pi/2
        else:
            theta = pi/2 - theta
    elif Ctm._neg:
        theta *= -1
    if theta < 0:
        theta += 2*pi
    return abs(fmod(theta, 2*pi))

def PointCyl(linenum, line, kw, args, d):
    name, P = PointRect(linenum, line, kw, args, d, showdbg=False)
    R = P.Rnd
    # x and y are actually cylindrical coordinates; convert them to Cartesian.
    rho, theta, z = [R(i) for i in P.rect]
    theta /= Ctm._angle     # Convert to radians
    theta = FixTheta(theta)
    rho = abs(rho)
    if not rho:
        P = Point(0, 0, 0)
    else:
        x, y = rho*cos(theta), rho*sin(theta)
        P = Point(R(x), R(y), R(z))
    CheckOverwrite(name, d, linenum, line)
    d["vars"][name] = P
    if _debug:
        dbg("[%s] %s =" % (linenum, name), str(P))
    return ("point(cyl)", (name, P))

def PointSph(linenum, line, kw, args, d):
    if len(args) not in (4, 5):
        Bad(linenum, line, "Improper number of parameters", d)
    name, P = PointRect(linenum, line, kw, args, d, showdbg=False)
    R = P.Rnd
    # x, y, z are spherical coordinates; convert them to Cartesian.
    # Note we use absolute values except for the azimuth theta.
    r, theta, phi = [R(i) for i in P.rect]
    r, phi = abs(r), abs(phi)
    if not r:
        P = Point(0, 0, 0, P.m)
    else:
        # theta and phi are in the current angular coordinates; convert
        # them to radians.
        theta /= Ctm._angle
        phi /= Ctm._angle
        theta = FixTheta(theta)
        if Ctm._elev:
            phi = pi/2 - phi
        # Note Ctm._neg does not affect phi
        if abs(phi) > pi/2:
            phi = fmod(phi, pi/2)
        rho = r*sin(phi)
        x, y = rho*cos(theta), rho*sin(theta)
        z = r*cos(phi)
        P = Point(R(x), R(y), R(z), P.m)
    CheckOverwrite(name, d, linenum, line)
    d["vars"][name] = P
    if _debug:
        dbg("[%s] %s =" % (linenum, name), str(P))
    return ("point(sph)", (name, P))

def GetLine(linenum, line, kw, args, d):
    '''Three allowed forms:
    pt1, pt2, name
    pt, ln, name [, len=L]
    pl1, pl2, name
    '''
    if len(args) not in (3, 4):
        Bad(linenum, line, "Improper number of parameters", d)
    if len(args) == 3:
        # pt1, pt2, name
        # pt, ln, name
        # pl1, pl2, name
        par1, par2, name = args
        p1 = GetObj(linenum, line, par1, d)
        p2 = GetObj(linenum, line, par2, d)
        if ii(p1, Point) and ii(p2, Point):
            ln = Line(p1, p2)
        elif ii(p1, Point) and ii(p2, Line):
            ln = Line(p1, p2.dc)
        elif ii(p1, Plane) and ii(p2, Plane):
            ln = p1.intersect(p2)
            if ln is None:
                Bad(linenum, line, "Planes are parallel", d)
        else:
            Bad(linenum, line, "Argument types improper", d)
    else:
        # pt, ln, name, len=L
        par1, par2, name, assign = args
        L = GetVar(linenum, assign, d)
        p = GetObj(linenum, line, par1, d)
        ln1 = GetObj(linenum, line, par2, d)
        if not (ii(p, Point) and ii(ln1, Line)):
            Bad(linenum, line, "Argument types improper", d)
        x, y, z = p.rect
        a, b, c = ln1.dc
        p2 = Point(x + L*a, y + L*b, z + L*c)
        ln = Line(p1, p2)
    CheckOverwrite(name, d, linenum, line)
    d["vars"][name] = ln
    if _debug:
        dbg("[%s] %s =" % (linenum, name), str(ln))
    return ("line", (name, ln))

def Intersect(linenum, line, kw, args, d):
    if len(args) not in (2, 3):
        Bad(linenum, line, "Improper number of parameters", d)
    name = ""
    if len(args) == 2:
        par1, par2 = args
    else:
        par1, par2, name = args
    o1 = GetObj(linenum, line, par1, d)
    o2 = GetObj(linenum, line, par2, d)
    o = o1.intersect(o2)
    if name:
        CheckOverwrite(name, d, linenum, line)
        d["vars"][name] = o
    else:
        out(d["indent"] + line.strip(), ":  ", o, sep="")
    if _debug:
        dbg("[%s] intersect = %s" % (linenum, str(o)))
    return ("intersect", (name, o))

def Length(linenum, line, kw, args, d):
    '''length ln, length
    Change the length of a line.
    '''
    if len(args) != 2:
        Bad(linenum, line, "Improper number of parameters", d)
    name, length = args
    ln = GetObj(linenum, line, name, d)
    L = Eval(linenum, line, length, d)
    if L <= 0:
        Bad(linenum, line, "Length must be > 0", d)
    x, y, z = ln.p.rect
    a, b, c = ln.dc
    ln._q = Point(x + L*a, y + L*b, z + L*c)
    if _debug:
        dbg("[%s] %s =" % (linenum, name), str(ln))
    return (name, ln)

def Locate(linenum, line, kw, args, d):
    '''Relocate o1 at o2.
    '''
    if len(args) != 2:
        Bad(linenum, line, "Improper number of parameters", d)
    o1 = GetObj(linenum, line, args[0], d)
    p = o1.copy
    o2 = GetObj(linenum, line, args[1], d)
    o1.locate(o2)
    if _debug:
        dbg("[%s] locate %s to %s:  %s" % (linenum, p, o2, o1))
    return ("locate", (o1, p))

def Stp(linenum, line, kw, args, d):
    '''Scalar triple product.
    '''
    if len(args) not in (3, 4):
        Bad(linenum, line, "Improper number of parameters", d)
    name = args[3] if len(args) == 4 else ""
    o1 = GetObj(linenum, line, args[0], d)
    o2 = GetObj(linenum, line, args[1], d)
    o3 = GetObj(linenum, line, args[2], d)
    stp = o1.dot(o2.cross(o3))
    if name:
        CheckOverwrite(name, d, linenum, line)
        d["vars"][name] = stp
    else:
        out(d["indent"] + "stp ", Listify(str(args[:3])), ":  ",
            Sig(stp), sep="")
    if _debug:
        dbg("[%s] stp = %s" % (linenum, Sig(stp)))
    return ("stp", stp)

def Vtp(linenum, line, kw, args, d):
    '''Vector triple product.
    '''
    if len(args) not in (3, 4):
        Bad(linenum, line, "Improper number of parameters", d)
    name = args[3] if len(args) == 4 else ""
    o1 = GetObj(linenum, line, args[0], d)
    o2 = GetObj(linenum, line, args[1], d)
    o3 = GetObj(linenum, line, args[2], d)
    vtp = o1.cross(o2.cross(o3))
    if name:
        CheckOverwrite(name, d, linenum, line)
        d["vars"][name] = vtp
    else:
        out(d["indent"] + "vtp ", Listify(str(args[:3])), ":  ", vtp, sep="")
    if _debug:
        dbg("[%s] vtp = %s" % (linenum, vtp))
    return ("vtp", vtp)

def Perp(linenum, line, kw, args, d):
    '''Create a line that passes through a given point and is
    perpendicular to the given object.
 
    perp pt, ln [, name]   
    perp pt, pl [, name]
    '''
    if len(args) not in (2, 3):
        Bad(linenum, line, "Improper number of parameters", d)
    o1 = GetObj(linenum, line, args[0], d)
    o2 = GetObj(linenum, line, args[1], d)
    name = args[2] if len(args) == 3 else ""
    C1 = ii(o1, Point) and ii(o2, Line)
    C2 = ii(o1, Line) and ii(o2, Point)
    C3 = ii(o1, Point) and ii(o2, Plane)
    C4 = ii(o1, Plane) and ii(o2, Point)
    if C2 or C4:
        o1, o2 = o2, o1
    if not C1 and not C2 and not C3 and not C4:
        Bad(linenum, line, "Improper types of parameters", d)
    if C1 or C2:
        # Point p and Line L.  Let gamma = direction cosines of L, r1
        # be the position vector of P, and r2 be a position vector of
        # any point on the line L.  Then the vector 
        #   u = gamma X (gamma X (r2 - r1))
        # is perpendicular to the line L.  Get its direction cosines
        # and use them to get the desired perpendicular line.
        gamma = V(o2.dc)
        r2 = V(o2.p)
        A = r2 - V(o1)
        u = gamma.VTP(gamma, A).normalize()  # (vector triple product)
        # u is a unit vector in the desired direction from the point
        # to the line.
        x, y, z = o1.rect
        a, b, c = u.dc
        o = Line(o1, Point(x + a, y + b, z + c))
    else:
        # Point p and plane Q.  This problem is easy because the
        # desired line will pass through p and have the same direction
        # cosines as the plane's normal.
        x, y, z = o1.rect
        a, b, c = o2.dc     # Plane's direction cosines
        o = Line(o1, Point(x + a, y + b, z + c))
    if name:
        CheckOverwrite(name, d, linenum, line)
        d["vars"][name] = o
    else:
        if _debug:
            dbg("[%s] perp =" % linenum, o)
        out(d["indent"] + "Perp of %s & %s:  %s" % (o1, o2, o))
    return ("perp", o)

def GetPlane(linenum, line, kw, args, d):
    '''Five allowed forms:
    1.  pt1, pt2, pt3, name     Through 3 pts
    2.  pt, ln1, ln2, name      Through pt, normal is ln1 X ln2
    3.  pt, ln, name            Through pt with line as normal
    4.  pt, pl, name            Through pt and parallel to plane
    5.  ln1, ln2, name          Through lines w/ norm ln1 X ln2
    '''
    if len(args) not in (3, 4):
        Bad(linenum, line, "Improper number of parameters", d)
    if len(args) == 3:
        par1, par2, name = args
        p1 = GetObj(linenum, line, par1, d)
        p2 = GetObj(linenum, line, par2, d)
        C3a = ii(p1, Point) and ii(p2, Line)
        C3b = ii(p1, Line) and ii(p2, Point)
        C3 = C3a or C3b
        C4a = ii(p1, Point) and ii(p2, Plane)
        C4b = ii(p1, Plane) and ii(p2, Point)
        C4 = C4a or C4b
        C5 = ii(p1, Line) and ii(p2, Line)
        if C3 or C4 or C5:
            try:
                # Note the constructor takes the parameters in any
                # order of types.
                pl = Plane(p1, p2)
            except Exception as e:
                Bad(linenum, line, str(e), d)
        else:
            Bad(linenum, line, "Argument types improper", d)
    else:
        # Form 1 and 2
        par1, par2, par3, name = args
        p1 = GetObj(linenum, line, par1, d)
        p2 = GetObj(linenum, line, par2, d)
        p3 = GetObj(linenum, line, par3, d)
        try:
            pl = Plane(p1, p2, p3)
        except Exception as e:
            Bad(linenum, line, str(e), d)
    CheckOverwrite(name, d, linenum, line)
    d["vars"][name] = pl
    if _debug:
        dbg("[%s] %s =" % (linenum, name), str(pl))
    return (name, pl)

def Dot(linenum, line, kw, args, d):
    '''Calculates the dot product between any objects.  Note points,
    lines, and planes can all be interpreted as vectors.  The first
    two arguments are the vectors and the last argument is the
    variable name to store the results in.
    '''
    if len(args) not in (2, 3):
        Bad(linenum, line, "Improper number of parameters", d)
    name = ""
    if len(args) == 2:
        par1, par2 = args
    else:
        par1, par2, name = args
    o1 = GetObj(linenum, line, par1, d)
    if ii(o1, Point):
        v1 = V(*o1.rect)
    elif ii(o1, Line):
        v1 = V(o1)
    elif ii(o1, Plane):
        v1 = V(Line(Point(o1.p), Point(o1.q)))
    else:
        raise RuntimeError("Bug:  unexpected type")
    o2 = GetObj(linenum, line, par2, d)
    if ii(o2, Point):
        v2 = V(*o2.rect)
    elif ii(o2, Line):
        v2 = V(o2)
    elif ii(o2, Plane):
        v2 = V(Line(Point(o2.p), Point(o2.q)))
    else:
        raise RuntimeError("Bug:  unexpected type")
    dp = v1.dot(v2)
    if _debug:
        dbg("[%s] %s =" % (linenum, name), Sig(dp))
    if name:
        CheckOverwrite(name, d, linenum, line)
        d["vars"][name] = dp
    else:
        out(d["indent"] + "%s dot %s = %s" % (par1, par2, Sig(dp)))
    return (name, dp)

def Ijk(linenum, line, kw, args, d):
    '''Define the usual i, j, k unit vectors and the coordinate planes
    xy, xz, and yz.  Note these are in the current coordinate system!
    '''
    if args:
        Bad(linenum, line, "This command takes no parameters", d)
    v = d["vars"]
    # Origin
    v["o"] = Point(0, 0, 0)
    # Unit vectors. 
    v["i"] = Line(v["o"], Point(1, 0, 0))
    v["j"] = Line(v["o"], Point(0, 1, 0))
    v["k"] = Line(v["o"], Point(0, 0, 1))
    # Coordinate planes
    v["xy"] = Plane(v["o"], v["k"])
    v["xz"] = Plane(v["o"], v["j"])
    v["yz"] = Plane(v["o"], v["i"])

def Cross(linenum, line, kw, args, d):
    '''Calculates the cross product between any objects; note they all
    can be interpreted as vectors.
    '''
    if len(args) not in (2, 3):
        Bad(linenum, line, "Improper number of parameters", d)
    name = ""
    if len(args) == 2:
        par1, par2 = args
    else:
        par1, par2, name = args
    o1 = GetObj(linenum, line, par1, d)
    if ii(o1, Point):
        v1 = V(*o1.rect)
    elif ii(o1, Line):
        v1 = V(o1)
    elif ii(o1, Plane):
        v1 = V(Line(Point(o1.p), Point(o1.q)))
    else:
        raise RuntimeError("Bug:  unexpected type")
    o2 = GetObj(linenum, line, par2, d)
    if ii(o2, Point):
        v2 = V(*o2.rect)
    elif ii(o2, Line):
        v2 = V(o2)
    elif ii(o2, Plane):
        v2 = V(Line(Point(o2.p), Point(o2.q)))
    else:
        raise RuntimeError("Bug:  unexpected type")
    cp = v1.cross(v2)
    ln = Line(Point(0, 0, 0), Point(*cp.rect))
    if name:
        CheckOverwrite(name, d, linenum, line)
        d["vars"][name] = ln
    else:
        msg = "cross %s X %s:  %s"
        out(d["indent"] + msg % (o1, o2, ln))
    if _debug:
        dbg("[%s] %s =" % (linenum, name), ln)
    return (name, ln)

def Pop(linenum, line, kw, args, d):
    if len(args) != 0:
        Bad(linenum, line, "pop takes no arguments", d)
    try:
        c = Ctm()
        ctm = c.pop()
    except Exception as e:
        Bad(linenum, line, msg, d)
    if _debug:
        dbg("[%s] pop:  CTM = " % linenum, Listify(str(ctm)))
    return ("pop", ctm)

def Push(linenum, line, kw, args, d):
    if len(args) != 0:
        Bad(linenum, line, "push takes no arguments", d)
    c = Ctm()
    c.push()
    if _debug:
        dbg("[%s] Pushed CTM" % linenum)
    return ("push", None)

def Reset(linenum, line, kw, args, d):
    if len(args) != 0:
        Bad(linenum, line, "reset takes no arguments", d)
    c = Ctm()
    c.reset()
    if _debug:
        dbg("[%s] Reset CTM to identity and emptied stack" % linenum)
    return ("", None)

def Rotate(linenum, line, kw, args, d):
    if len(args) not in (1, 2):
        Bad(linenum, line, "Improper number of parameters", d)
    axis = Line(Point(0, 0, 0), Point(0, 0, 1))
    if len(args) == 1:
        angle = args[0]
    else:
        angle, axis_name = args
        axis = GetObj(linenum, line, axis_name, d)
    if angle in d["vars"]:
        theta = GetObj(linenum, line, args[0], d)
    else:
        theta = Interp(angle, d, linenum, line)
    theta /= Ctm._angle  # Convert to radians
    axis.rotate(theta, axis)
    s = Sig(theta*Ctm._angle) + " %s" % Ctm._angle_name
    if _debug:
        dbg("[%s] rotate %s about %s" % (linenum, s, str(axis)))
    return ("Rotated", (theta, axis))

def Scale(linenum, line, kw, args, d):
    if len(args) not in (1, 2, 3):
        Bad(linenum, line, "Improper number of parameters", d)
    sx, sy, sz = 1, 1, 1
    if len(args) == 1:
        x = args[0]
        if x in d["vars"]:
            sx = GetObj(linenum, line, x, d)
        else:
            sx = Interp(x, d, linenum, line)
        # Isotropic scaling with one parameter
        sy = sz = sx
    elif len(args) == 2:
        x, y = args
        if x in d["vars"]:
            sx = GetObj(linenum, line, x, d)
        else:
            sx = Interp(x, d, linenum, line)
        if y in d["vars"]:
            sy = GetObj(linenum, line, y, d)
        else:
            sy = Interp(y, d, linenum, line)
    else:
        x, y, z = args
        if x in d["vars"]:
            sx = GetObj(linenum, line, x, d)
        else:
            sx = Interp(x, d, linenum, line)
        if y in d["vars"]:
            sy = GetObj(linenum, line, y, d)
        else:
            sy = Interp(y, d, linenum, line)
        if z in d["vars"]:
            sz = GetObj(linenum, line, z, d)
        else:
            sz = Interp(z, d, linenum, line)
    p = Point(0, 0, 0)
    p.scale(sx, sy, sz)
    s = Listify(str([Sig(i) for i in (sx, sy, sz)]))
    if _debug:
        dbg("[%s] Scaled by %s" % (linenum, s))
    return ("Scaled", (sx, sy, sz))

def Translate(linenum, line, kw, args, d):
    def Get(s):
        if s in d["vars"]:
            return GetObj(linenum, line, s, d)
        else:
            return Interp(s, d, linenum, line)
    if len(args) not in (1, 2, 3):
        Bad(linenum, line, "Improper number of parameters", d)
    x, y, z = 0, 0, 0
    if len(args) == 1:
        # "translate pt" form
        p = GetObj(linenum, line, args[0], d)
        x, y, z = p.rect
    elif len(args) >= 2:
        # "translate x, y" form
        x = Get(args[0])
        y = Get(args[1])
    if len(args) == 3:
        # "translate x, y, z" form
        z = Get(args[2])
    try:
        p = Point(0, 0, 0)
        p.translate(x, y, z)
    except Exception:
        Bad(linenum, line, "Improper type for x, y, or z", d)
    s = Listify(str([Sig(i) for i in (x, y, z)]))
    if _debug:
        dbg("[%s] Translated by %s" % (linenum, s))
    return ("Translated", (x, y, z))

def XY(linenum, line, kw, args, d):
    '''The single argument is a plane.  Rotate the coordinate system
    so that the plane in kw is parallel to the argument plane.
    '''
    if len(args) != 1:
        Bad(linenum, line, "Improper number of parameters", d)
    pl = GetObj(linenum, line, args[0], d)
    if not ii(pl, Plane):
        Bad(linenum, line, "Parameter must be a plane", d)
    # Get normal to desired plane
    o = Point(0, 0, 0)
    if kw == "xy":
        u = Line(o, Point(0, 0, 1))
    elif kw == "xz":
        u = Line(o, Point(0, 1, 0))
    elif kw == "yz":
        u = Line(o, Point(1, 0, 0))
    else:
        raise RuntimeError("Bug in XY():  unexpected keyword")
    # Get axis to rotate around and angle to rotate by
    axis, theta = u.cross(pl), acos(pl.dot(u))
    if theta:
        if not o.Rnd(theta - pi):
            # We need to invert the plane because it's antiparallel to
            # the desired plane.  Note we can rotate about any axis.
            axis = u
        o.rotate(theta, axis)
    if _debug:
        dbg("[%s] %s --> %s" % (linenum, kw, pl))
    return (kw, pl)

def Rotaxis(linenum, line, kw, args, d):
    '''Return in two variables the rotation angle and rotation axis.
    '''
    if len(args) != 2:
        Bad(linenum, line, "Improper number of parameters", d)
    p = Point(0, 0, 0)
    try:
        theta, dc = p.GetRotationAxis()
    except ValueError as e:
        Bad(linenum, line, str(e), d)
    angle_name, dc_name = args
    CheckOverwrite(angle_name, d, linenum, line)
    d["vars"][angle_name] = theta*Ctm._angle
    CheckOverwrite(dc_name, d, linenum, line)
    d["vars"][dc_name] = dc
    t = Sig(d["vars"][angle_name]) + " " + Ctm._angle_name
    if _debug:
        dbg("[%s] rotaxis:  %s about (%s)" % (linenum, t, Sig(dc)))
    return ("rotaxis", (theta, dc))

def Angle(linenum, line, kw, args, d):
    '''Calculate the angle between the two indicated objects.
    '''
    if len(args) not in (2, 3):
        Bad(linenum, line, "Improper number of parameters", d)
    name = ""
    o1 = GetObj(linenum, line, args[0], d)
    o2 = GetObj(linenum, line, args[1], d)
    if len(args) == 3:
        name = args[2]
        if not IsIdentifier(name):
            msg = "'%s' is not a proper variable name" % name
            Bad(linenum, line, msg, d)
    C1 = ii(o1, Line) and ii(o2, Line)
    C2 = (ii(o1, Line) and ii(o2, Plane)) or (ii(o1, Plane) and ii(o2, Line))
    C3 = ii(o1, Plane) and ii(o2, Plane)
    C4 = ii(o1, Point) and ii(o2, Point)
    if not C1 and not C2 and not C3 and not C4:
        Bad(linenum, line, "Bad types for angle command", d)
    v1, v2 = V(o1.dc), V(o2.dc)
    theta = acos(v1.dot(v2))
    if C2:
        # Complement of angle for line and plane (because the angle is
        # for the plane's normal).
        theta = pi/2 - theta
        if theta < 0:
            theta += 2*pi
    assert 0 <= theta <= pi
    theta *= Ctm._angle # Convert to current angle units
    if name:
        CheckOverwrite(name, d, linenum, line)
        d["vars"][name] = theta
    else:
        msg = "Angle between %s and %s = %s %s"
        out(d["indent"] + msg % (args[0], args[1], Sig(theta), Ctm._angle_name))
    if _debug:
        dbg("[%s] %s:  %s %s" % (linenum, line.strip(), Sig(theta),
        Ctm._angle_name))
    return ("angle", theta)

def IsSelfintersecting(obj, d):
    '''obj is a sequence of the names and points making up the
    polygon.  Generate another list called lines that contains a pair
    of points that make up the line of each edge of the polygon.  Then
    examine all of these lines in pairs to see if there are any
    intersections between the two points.  Return True if there are
    any such intersections.
    '''
    lines, n, p = [], len(obj), d["vars"]
    for i, item in enumerate(obj):
        name, o = item
        j = i + 1 if i < n - 1 else 0
        lines.append((obj[i][1], obj[j][1]))
    # lines contains the pairs of points's coordinates defining each
    # side of the polygon, so examine all combinations for
    # intersections.
    for side1, side2 in combinations(lines, 2):
        x1, y1, z1 = side1[0].rect
        x2, y2, z2 = side1[1].rect
        X1, Y1, Z1 = side2[0].rect
        X2, Y2, Z2 = side2[1].rect
        det = (x1 - x2)*(Y1 - Y2) - (y1 - y2)*(X1 - X2)
        if det:
            # A nonzero determinant means lines don't have the same
            # slope.  Get parameter values where the lines intersect.
            t = (X2*(y1 - Y1) + x1*(Y1 - Y2) + X1*(-y1 + Y2))/det
            s = (x2*(y1 - Y1) + x1*(Y1 - y2) + X1*(-y1 + y2))/det
            # They must be interior to the endpoints (adjacent
            # lines will naturally intersect at their
            # endpoints).
            if (0 < t < 1) and (0 < s < 1):
                return True
        else:
            # Lines have same slope.  They are self-intersecting if
            # the points are coincident.
            s = ((X1, Y1), (X2, Y2))
            if (x1, y1) in s or (x2, y2) in s:
                return True
    return False

def Area(linenum, line, kw, args, d):
    '''Calculate the area for the indicated set of points.  It is an
    error if they do not lie in the xy plane.
    '''
    # The area of a polygon is gotten with the "shoelace" algorithm
    # (see the picture at http://mathworld.wolfram.com/PolygonArea.html
    # which makes it obvious why it's named this way).
    if len(args) < 3:
        Bad(linenum, line, "Need at least 3 points", d)
    names = args
    # Get objects and verify they're points in the xy plane
    obj = []
    for name in names:
        o = GetObj(linenum, line, name, d)
        if not ii(o, Point):
            Bad(linenum, line, "'%s' is not a point" % name, d)
        x, y, z = o.rect
        msg = "'%s' is not in the xy plane" % name
        if ii(z, UFloat) and o.Rnd(z.nominal_value):
            Bad(linenum, line, msg, d)
        elif o.Rnd(z):
            Bad(linenum, line, msg, d)
        obj.append((name, o))
    X, Y, n = [], [], len(names)
    for name, o in obj:
        x, y, z = o.rect
        X.append(x)
        Y.append(y)
    area = 0
    for i in range(n):
        j = (i + 1) % n
        area += X[i]*Y[j] - X[j]*Y[i]
    area /= 2
    s = Listify(str(names))
    i = d["indent"]
    out(i + "Area for points:  %s" % s)
    if IsSelfintersecting(obj, d):
        s = Listify(str(names))
        out(i + "  Warning:  the polygon is self-intersecting")
    out(i + "  Area = %s" % Sig(area))
    return ("area", area)


def Centroid(linenum, line, kw, args, d):
    '''Search through the d["vars"] dictionary for Point objects with
    mass and print their total mass and centroid.
    '''
    pts = []
    msg = "Mass must be a number, not %s"
    if args:
        for name in args:
            o = GetObj(linenum, line, name, d)
            if not ii(o, Point):
                Bad(linenum, line, "Argument must be a point", d)
            if ii(o.m, Numbers):
                pts.append(o)
            else:
                Bad(linenum, line, msg % type(o.m), d)
    else:
        # Find all points that have mass
        for name in d["vars"]:
            o = d["vars"][name]
            if ii(o, Point) and o.m is not None:
                if ii(o.m, Numbers):
                    pts.append(o)
                else:
                    Bad(linenum, line, msg % type(o.m), d)
    if not pts:
        Bad(linenum, line, "No points with mass were given", d)
    # Compute the centroid
    xs, ys, zs, M = 0, 0, 0, 0
    try:
        for o in pts:
            x, y, z = o.rect
            m = o.m
            xs += x*m
            ys += y*m
            zs += z*m
            M += m
        C = Point(xs/M, ys/M, zs/M)
    except Exception:
        Bad(linenum, line, "A point had a bad mass", d)
    if _debug:
        dbg("[%s] centroid:  mass = %s at %s" % (linenum, Sig(M), C))
    out(d["indent"] + "Centroid:  mass = %s at %s" % (Sig(M), C))
    # Save the results in the variables 'total_mass' and 'centroid'.
    d["vars"]["total_mass"] = M
    d["vars"]["centroid"] = C
    return ("centroid", (M, C))

def Circ3(linenum, line, kw, args, D):
    '''Calculate the radius and center of a circle formed from three
    points and print the results.
    '''
    # Equations for circumscribed circle from three points from
    # http://mathworld.wolfram.com/Circle.html.
    if len(args) != 3:
        Bad(linenum, line, "Improper number of parameters", D)
    n1, n2, n3 = args
    o1 = GetObj(linenum, line, n1, D)
    o2 = GetObj(linenum, line, n2, D)
    o3 = GetObj(linenum, line, n3, D)
    # Note we'll allow the objects to be points, lines, or planes.  If
    # lines or planes, we use the point that is the p attribute.
    allowed = (Point, Line, Plane)
    if not ii(o1, allowed):
        Bad(linenum, line, "First object must be a point, line, or plane", D)
    if not ii(o2, allowed):
        Bad(linenum, line, "Second object must be a point, line, or plane", D)
    if not ii(o3, allowed):
        Bad(linenum, line, "Third object must be a point, line, or plane", D)
    p1 = o1 if ii(o1, Point) else o1.q
    p2 = o2 if ii(o2, Point) else o2.q
    p3 = o3 if ii(o3, Point) else o3.q
    x1, y1, z1 = p1.rect
    x2, y2, z2 = p2.rect
    x3, y3, z3 = p3.rect
    c = Ctm()
    R = c.Rnd
    if R(z1) or R(z2) or R(z3):
        Bad(linenum, line, "One or more points not in xy plane", D)
    h = lambda x, y:  x**2 + y**2
    h1, h2, h3 = h(x1, y1), h(x2, y2), h(x3, y3)
    a =  Det3((x1, y1, 1, x2, y2, 1, x3, y3, 1))
    d = -Det3((h1, y1, 1, h2, y2, 1, h3, y3, 1))
    e =  Det3((h1, x1, 1, h2, x2, 1, h3, x3, 1))
    f = -Det3((h1, x1, y1, h2, x2, y2, h3, x3, y3))
    if not a:
        Bad(linenum, line, "Collinear points", D)
    if have_unc:
        if isinstance(a, UFloat) and not a.nominal_value:
            msg = "Collinearity:  an divisor with uncertainty is %s" % Sig(a)
            Bad(linenum, line, msg, D)
    # Radius of circle
    Sig.fit = 0
    rho = sqrt(h(d, e)/(4*a*a) - f/a)
    RI = Sig(rho)
    diaI = Sig(2*rho)
    # Header
    s = Listify(str(args))
    out(D["indent"] + "Circles from three points %s:" % s)
    out(D["indent"] + "  %s : %s" % (n1, Point(x1, y1)))
    out(D["indent"] + "  %s : %s" % (n2, Point(x2, y2)))
    out(D["indent"] + "  %s : %s" % (n3, Point(x3, y3)))
    # Center
    cx, cy = -d/(2*a), -e/(2*a)
    CI = Point(cx, cy)
    t = D["indent"]
    t += "  Circumcenter = %s, radius = {RI}, dia = {diaI}" % CI
    out(t.format(**locals()))
    # Now calculate position of inscribed circle.  Formulas from
    # http://en.wikipedia.org/wiki/Inscribed_circle.  First get length
    # of sides.
    a = hypot(x1 - x2, y1 - y2)
    xa, ya = x3, y3
    b = hypot(x1 - x3, y1 - y3)
    xb, yb = x2, y2
    c = hypot(x2 - x3, y2 - y3)
    xc, yc = x1, y1
    P = a + b + c
    s = P/2
    # Location of incenter
    x = (a*xa + b*xb + c*xc)/P
    y = (a*ya + b*yb + c*yc)/P
    CO = Point(x, y)
    rho = sqrt((s - a)*(s - b)*(s - c)/s)  # Radius of incircle
    RO = Sig(rho)
    diaO = Sig(2*rho)
    t = D["indent"]
    t += "  Incenter     = %s, radius = {RO}, dia = {diaO}" % CO
    out(t.format(**locals()))
    return("circ3", (CI, RI, CO, RO))


def Dc(linenum, line, kw, args, d):
    '''Print the direction cosines of the indicated objects.
    '''
    if len(args) < 1:
        Bad(linenum, line, "Improper number of parameters", d)
    for name in args:
        o = GetObj(linenum, line, name, d)
        if not ii(o, (Point, Line, Plane)):
            msg = "'%s' is not a point, line, or plane" % name
            Bad(linenum, line, msg, d)
        if ii(o, Point):
            t = "Pt"
        elif ii(o, Line):
            t = "Ln"
        elif ii(o, Plane):
            t = "Pl"
        dc, ang, an = o.dc, Ctm._angle, Ctm._angle_name
        da = tuple([acos(i)*ang for i in dc])
        s = Sig(o.dc)
        a, b, c = tuple([o.Rnd(i) for i in dc])
        f = " (%s):  dc = "
        if a == 0 and b == 0 and c == 0:
            out(d["indent"] + name, f % t, s)
        else:
            out(d["indent"] + name, f % t, s, ", dir ang = ", Sig(da), " ", an, sep="")
    if _debug:
        dbg("[%s] dc command" % linenum)
    return ("", None)

def Dist(linenum, line, kw, args, d):
    '''Calculate the distance between the two indicated objects.
    '''
    if len(args) not in (2, 3):
        Bad(linenum, line, "Improper number of parameters", d)
    o1 = GetObj(linenum, line, args[0], d)
    o2 = GetObj(linenum, line, args[1], d)
    name = args[2] if len(args) == 3 else ""
    distance = o1.Rnd(o1.dist(o2))
    if _debug:
        dbg("[%s] Distance:  %s to %s = %s" % 
        (linenum, args[0], args[1], Sig(distance)))
    if name:
        CheckOverwrite(name, d, linenum, line)
        d["vars"][name] = distance
    else:
        out(d["indent"] + "Distance: %s to %s = %s" % (args[0], args[1], Sig(distance)))
    return ("dist", distance)

def Trace(linenum, line, kw, args, d):
    '''Calculate the traces for the indicated points.  These are the
    angles that the position vector extends from the positive axes.
    The z trace is the spherical coordinate phi coordinate.
    '''
    if len(args) < 1:
        Bad(linenum, line, "Need at least one point", d)
    results, m, cn = [], Ctm._angle, "trace"
    for name in args:
        o = GetObj(linenum, line, name, d)
        if not ii(o, Point):
            Bad(linenum, line, "Projection angles only defined for points", d)
        x, y, z = o.rect
        a, b, c = atan2(z, x)*m , atan2(z, y)*m, atan2(z, hypot(x, y))*m
        results.append((a, b, c))
        sa, sb, sc = Sig(o.Rnd(a)), Sig(o.Rnd(b)), Sig(o.Rnd(c))
        if _debug:
            dbg("[%s] %s %s %s" % (linenum, cn, name, o))
        msg = "%s %s[%s]:  x: %s, y: %s, z: %s %s"
        out(d["indent"] + msg % (cn, name, o, sa, sb, sc, Ctm._angle_name))
    return (cn, results)

def Make_xy(plane):
    '''Make the point in the plane the origin, then make two rotations
    so that the plane becomes the xy plane.
    '''
    p = plane.p                 # Point in plane
    q = plane.q                 # Tip of normal vector
    plane.translate(*p.rect)    # Origin is now in plane
    r, theta, phi = q._sph()
    k = Line(Point(0, 0, 0), Point(0, 0, 1))
    plane.rotate(theta, k)      # Rotate about z axis
    r, theta, phi = q._sph()
    j = Line(Point(0, 0, 0), Point(0, 1, 0))
    plane.rotate(phi, j)        # Rotate about y axis

def Project(linenum, line, kw, args, d):
    '''Project a set of objects onto a plane.  Note the coordinates of
    the objects are changed!  If Ctm._eye is not None, then use a
    projective transformation.  Otherwise, use an orthogonal
    transformation.
    '''
    if len(args) < 2:
        Bad(linenum, line, "Need a plane and at least one point", d)
    plane_name = args[0]
    pl = GetObj(linenum, line, plane_name, d)
    if not ii(pl, Plane):
        Bad(linenum, line, "First argument needs to be a plane", d)
    objects = []
    for name in args[1:]:
        o = GetObj(linenum, line, name, d)
        if not ii(o, (Point, Line)):
            msg = "Objects must be points or lines"
            Bad(linenum, line, msg, d)
        objects.append((name, str(o), o))
    if Ctm._eye is not None:
        # Given plane pl and eye point E, for each object o draw a
        # line from E to o and change o to where this line intersects
        # with the plane p.
        E = Ctm._eye
        if not ii(E, Point):
            Bad(linenum, line, "Eye point is not a Point object", d)
        for i, item in enumerate(objects):
            name, orig_form, o = item
            if ii(o, Point):
                ln = Line(E, o)
                oi = pl.intersect(ln)
            elif ii(o, Line):
                # Project the line's two points into the plane, then
                # construct a new line.  Note if the line is
                # perpendicular to the plane, it projects to a point.
                ln = Line(E, o.p)
                op = pl.intersect(ln)
                ln = Line(E, o.q)
                oq = pl.intersect(ln)
                if op == oq:
                    oi = op
                else:
                    oi = Line(op, oq)
            elif ii(o, Plane):
                Bad(linenum, line, "Can't project a plane", d)
            else:
                raise RuntimeError("Bug:  unexpected object")
            if oi is None:
                msg = "'%s' is projected to infinity" % name
                Bad(linenum, line, msg, d)
            else:
                objects[i] = name, orig_form, oi
                d["vars"][name] = oi
    else:
        # Orthogonal projections
        # 1.  Push the current CTM.
        # 2.  Translate the origin to a point in the plane.
        # 3.  Apply two rotations to make the plane's normal vector
        #     parallel to the z axis (i.e., the plane is now the same as
        #     the xy plane).
        # 4.  Set each object's z coordinate to 0.
        # 5.  Pop the saved CTM.
        pl.push()
        Make_xy(pl)
        for name, orig_form, o in objects:
            o.ToCCS()  # Make sure transformed coords are in o._r
            if ii(o, Point):
                o._r = list(o._r)
                o._r[2] = 0
                o._r = tuple(o._r)
            else:
                # Check to see if this line goes along the z axis -- if it
                # does, it will project to a point.
                r, theta, phi = V(o.u)._sph()
                p = list(o.p.rect)
                p[2] = 0
                o.p._r = tuple(p)
                if o.Rnd(phi) == 0:
                    o = Point(*o.p.rect)
                else:
                    q = list(o.q._r)
                    q[2] = 0
                    o.q._r = tuple(q)
            o.ToDCS()  # Make sure the ._r0 values change to correct ones
        pl.pop()    # Restore old coordinates
    # Print results
    if _debug:
        dbg("[%s] projected %d objects" % (linenum, len(objects)))
    if Ctm._eye is None:
        out(d["indent"] + "Projection ", plane_name, "[", pl, 
            "] (orthogonal)", sep="")
    else:
        out(d["indent"] + "Projection ", plane_name, "[", pl, 
            "], eye = ", Ctm._eye, sep="")
    w = 0
    # Get width of widest name
    for name, orig, o in objects:
        w = max(w, len(name))
    # Print table of transformed objects
    for name, orig, o in objects:
        out(d["indent"] + "  {name:{w}}: {orig} -->".format(**locals()), o)
    return ("project", objects)

def Reflect(linenum, line, kw, args, d):
    '''Reflect a set of objects about a point, line, or plane.  If the
    object to reflect about is a line, all the objects must be in the
    xy plane.
    
    Note the coordinates of the objects are changed!
    '''
    if len(args) < 2:
        Bad(linenum, line, "Need a plane and at least one point", d)
    reflector = GetObj(linenum, line, args[0], d)
    refl_in_line = True if ii(reflector, Line) else False
    if refl_in_line:
        # The line must be in the xy plane
        p, q = reflector.p, reflector.q
        if p.rect[2] or q.rect[2]:
            msg = "The line to reflect about must by in the xy plane"
            Bad(linenum, line, msg, d)
    if not ii(reflector, (Point, Line, Plane)):
        Bad(linenum, line, "First argument needs to be a point, line, or plane", d)
    # Get the objects to be reflected
    objects = []
    no_plane = "A plane can't be reflected about a line"
    bug = RuntimeError("Bug:  unexpected type")
    for name in args[1:]:
        o = GetObj(linenum, line, name, d)
        if not ii(o, (Point, Line, Plane)):
            msg = "Object must be a point, line, or plane"
            Bad(linenum, line, msg, d)
        not_xy = "'%s' is not in the xy plane" % name
        if refl_in_line:
            if ii(o, Plane):
                Bad(linenum, line, no_plane, d)
            elif ii(o, Line):
                if o.p.z or o.q.z:
                    Bad(linenum, line, not_xy, d)
            elif ii(o, Point):
                if o.z:
                    Bad(linenum, line, not_xy, d)
            else:
                raise bug
        objects.append((name, str(o), o))
    reflector.push()
    if ii(reflector, Point):
        # Method:  translate to the point to be reflected about,
        # reflect each object, return to old coordinate system.
        reflector.translate(*reflector.rect)
        for name, orig, o in objects:
            if ii(o, Point):
                o.x, o.y, o.z = -o.x, -o.y, -o.z
            elif ii(o, (Line, Plane)):
                o.p.x, o.p.y, o.p.z = -o.p.x, -o.p.y, -o.p.z
                o.q.x, o.q.y, o.q.z = -o.q.x, -o.q.y, -o.q.z
            else:
                raise bug
    elif ii(reflector, Line):
        # Method:  since we'll reflect about a line in the xy plane
        # and we know all the objects are either points or lines,
        # we'll just pass a new plane pl perpendicular to the xy plane
        # through the line, translate to a point in this plane, and
        # rotate to make the plane the same as the xy plane.  Then
        # reflection is easy (z --> -z).
        p, q = reflector.p, reflector.q
        r = q.copy
        r.z += abs(reflector)
        pl = Plane(p, q, r)
        reflector.translate(*p.rect)
        Make_xy(pl)
        for name, orig, o in objects:
            if ii(o, Point):
                o.z = -o.z
            elif ii(o, (Line, Plane)):
                o.p.z = -o.p.z
                o.q.z = -o.q.z
            else:
                raise bug
    elif ii(reflector, Plane):
        # Method:  translate to a point in the plane to be reflected
        # about.  Then make two rotations to make the plane the xy
        # plane.  Reflect each object and return to old coordinate
        # system.
        reflector.translate(*reflector.p.rect)
        Make_xy(reflector)
        for name, orig, o in objects:
            if ii(o, Point):
                o.z = -o.z
            elif ii(o, (Line, Plane)):
                o.p.z = -o.p.z
                o.q.z = -o.q.z
            else:
                raise bug
    else:
        raise bug
    reflector.pop()
    # Print results
    if _debug:
        dbg("[%s] reflected %d objects" % (linenum, len(objects)))
    out(d["indent"] + "Reflected about ", reflector, ":", sep="")
    w = 0
    # Get width of widest name
    for name, orig, o in objects:
        w = max(w, len(name))
    # Print table of transformed objects
    for name, orig, o in objects:
        out(d["indent"] + "  {name:{w}}: {orig} -->".format(**locals()), o)
    return ("reflect", objects)

def Angunit(linenum, line, kw, args, d):
    '''Change the constant used to convert angle measure and set the
    name of the unit.
    '''
    if len(args) not in (1, 2):
        Bad(linenum, line, "Improper number of parameters", d)
    name = ""
    try:
        Ctm._angle = eval(args[0], globals(), d["vars"])
        if len(args) == 2:
            name = args[1]
            Ctm._angle_name = name
    except Exception as e:
        Bad(linenum, line, str(e), d)
    Ctm._angle_name = args[1] if len(args) == 2 else ""
    if _debug:
        dbg("[%s] angunit:  %s %s" % (linenum, Sig(Ctm._angle, name)))
    return ("angunit", (Ctm._angle, name))

def Cyl(linenum, line, kw, args, d):
    '''Set output to cylindrical coordinates.
    '''
    if args:
        Bad(linenum, line, "Command doesn't take arguments", d)
    Ctm._coord_sys = "cyl"
    if _debug:
        dbg("[%s] cyl" % linenum)
    return ("cyl", None)

def Date(linenum, line, kw, args, d):
    '''Print the date/time.
    '''
    s = time.asctime()
    if _debug:
        dbg("[%s] Date/time:  %s" % (linenum, s))
    out(d["indent"] + "Date/time:  %s" % s)
    return ("date", s)

def Deg(linenum, line, kw, args, d):
    '''Set output angle measure to degrees.
    '''
    if args:
        Bad(linenum, line, "Command doesn't take arguments", d)
    Ctm._angle = 180/pi
    Ctm._angle_name = "deg"
    if _debug:
        dbg("[%s] deg" % linenum)
    return ("deg", None)

def Del(linenum, line, kw, args, d):
    '''Delete the indicated objects.
    '''
    if not args:
        Bad(linenum, line, "Need at least one object to delete", d)
    vars = d["vars"]
    for name in args:
        if name in vars:
            del vars[name]
        else:
            msg = "'%s' is not a defined object" % name
            Bad(linenum, line, msg, d)
    if _debug:
        dbg("[%s] %s" % (linenum, line.strip()))
    return ("del", None)

def Digits(linenum, line, kw, args, d):
    '''Set the number of significant figures for output.
    '''
    try:
        digits = int(args[0])
        if 1 <= digits <= 15:
            Sig.digits = digits
        else:
            Bad(linenum, line, "Digits must be between 1 and 15", d)
    except Exception as e:
        Bad(linenum, line, str(e), d)

def Eps(linenum, line, kw, args, d):
    '''Set the zero-threshold number.
    '''
    if len(args) != 1:
        Bad(linenum, line, "Improper number of parameters", d)
    try:
        eps = float(eval(args[0], globals(), d["vars"]))
        if eps < 0:
            Bad(linenum, line, "eps must be >= 0", d)
        Ctm.eps = eps
    except Exception as e:
        Bad(linenum, line, str(e), d)
    if _debug:
        dbg("[%s] eps = %s" % (linenum, Sig(eps)))
    return ("eps", eps)

def Exit(linenum, line, kw, args, d):
    if _test:
        global _test_msg
        _test_msg = "Exit"
    else:
        exit(0)

def Eye(linenum, line, kw, args, d):
    '''Set the eye point.
    '''
    if len(args) not in (0, 1):
        Bad(linenum, line, "Improper number of parameters", d)
    if args:
        o = GetObj(linenum, line, args[0], d)
        if ii(o, Point):
            Ctm._eye = o
        else:
            Ctm._eye = o.p
    else:
        o = None
        Ctm._eye = None
    if _debug:
        dbg("[%s] eye %s" % (linenum, o))
    return ("eye", o)

def Print(linenum, line, kw, args, d):
    '''Print the string representation of the indicated objects to
    stdout.  Note, because of some parsing syntax issues, we allow one
    of the args to be '.', '<', or '<<'; these will override the
    global settings for the coordinate system to display in for the
    items printed by this command.
    '''
    allowed = (Point, Line, Plane)
    to_print, sort, coord = [], False, None
    cnames = {".":"rect", "<":"cyl", "<<":"sph"}
    if len(args) == 1 and args[0] in cnames:
        coord = cnames[name]
        del args[0]
    if args:
        # Only print those names given
        for name in args:
            if name in cnames:
                coord = cnames[name]
                continue
            o = GetObj(linenum, line, name, d)
            to_print.append((name, o))
    else:
        for name in d["vars"]:
            o = GetObj(linenum, line, name, d)
            if not d["-a"] and not ii(o, allowed):
                continue
            to_print.append((name, o))
    # Get largest name
    nm = 0
    for name, o in to_print: 
        nm = max(nm, len(name))
    if d["alphabetical"]:
        to_print.sort()
    if coord is not None:
        # Set the temporary output coordinate system
        temp = Ctm._coord_sys
        Ctm._coord_sys = coord
    for name, o in to_print: 
        s = "="
        if ii(o, allowed):
            s = ":"
        out(d["indent"] + "{0:{1}} {2} {3}".format(name, nm, s, str(o)))
    if coord is not None:
        # Restore the global output coordinate system
        Ctm._coord_sys = temp
    return ("print", to_print)

def State(linenum, line, kw, args, d):
    '''Print the script's state to stdout.
    '''
    comp = str(Ctm._compass)
    neg = str(Ctm._neg)
    sz = str(Ctm._suppress_z)
    ang = sig(Ctm._angle)
    an = repr(Ctm._angle_name)
    ssz = str(len(Ctm._stack))
    elev = str(Ctm._elev)
    eps = sig(Ctm.eps, 2)
    rot = str(Ctm._rotations_only)
    cs = Ctm._coord_sys
    no = 0
    v = d["vars"]
    for i in v:
        if ii(v[i], (Point, Line, Plane)):
            no += 1
    nv = len(v) - no
    w, sp, i = 8, "", d["indent"]
    out('''
{i}State:
{i}{comp:>{w}} {sp} Compass mode
{i}{elev:>{w}} {sp} Elevation mode
{i}{neg:>{w}} {sp} Negative mode
{i}{sz:>{w}} {sp} Suppress z
{i}{ang:>{w}} {sp} Angle factor (inverse converts to radians)
{i}{an:>{w}} {sp} Angle unit name
{i}{ssz:>{w}} {sp} Stack size
{i}{eps:>{w}} {sp} eps (zero threshold)
{i}{rot:>{w}} {sp} Rotation transformations only up to this point
{i}{cs:>{w}} {sp} Coordinate system for output
{i}{nv:>{w}} {sp} Number of defined variables
{i}{no:>{w}} {sp} Number of defined geometric objects
'''[1:-1].format(**locals()))
    # Now print the CTM
    c = Ctm._CTM
    r0, r1, r2, r3 = Sig(c[:4]), Sig(c[4:8]), Sig(c[8:12]), Sig(c[12:]),
    out('''
{i}  Coordinate transformation matrix:
{i}    {r0}
{i}    {r1}
{i}    {r2}
{i}    {r3}
'''[1:-1].format(**locals()))

def Rad(linenum, line, kw, args, d):
    '''Set output angle measure to radians.
    '''
    if len(args) > 1:
        Bad(linenum, line, "Command doesn't take arguments", d)
    Ctm._angle = 1
    Ctm._angle_name = "rad"
    if _debug:
        dbg("[%s] rad" % linenum)

def Rev(linenum, line, kw, args, d):
    '''Set output angle measure to revolutions.
    '''
    if len(args) > 1:
        Bad(linenum, line, "Command doesn't take arguments", d)
    Ctm._angle = 1/(2*pi)
    Ctm._angle_name = "rev"
    if _debug:
        dbg("[%s] rev" % linenum)

def Rect(linenum, line, kw, args, d):
    '''Set output to rectangular coordinates.
    '''
    if args:
        Bad(linenum, line, "Command doesn't take arguments", d)
    Ctm._coord_sys = "rect"
    if _debug:
        dbg("[%s] rect" % linenum)
    return ("rect", None)

def Sph(linenum, line, kw, args, d):
    '''Set output to spherical coordinates.
    '''
    if args:
        Bad(linenum, line, "Command doesn't take arguments", d)
    Ctm._coord_sys = "sph"
    if _debug:
        dbg("[%s] sph" % linenum)
    return ("sph", None)

def SetClassVar(varname, linenum, line, kw, args, d):
    if len(args) != 1:
        Bad(linenum, line, "Improper number of parameters", d)
    word = args[0]
    if word == "on":
        exec("Ctm.%s = True" % varname)
    elif word == "off":
        exec("Ctm.%s = False" % varname)
    else:
        try:
            val = eval(args[0], globals(), d["vars"])
            word = "on" if val == True else "off"
            exec("Ctm.%s = %s" % (varname, val == True))
        except Exception:
            msg = "Argument must be 'on', 'off', or Boolean expression"
            Bad(linenum, line, msg, d)
    if _debug:
        dbg("[%s] %s %s" % (linenum, varname, word))
    return ("%s" % varname, word)

def Compass(linenum, line, kw, args, d):
    '''Set output to compass mode.  Angle theta is displayed
    increasing clockwise from the +y axis, just like a compass.
    '''
    return SetClassVar("_compass", linenum, line, kw, args, d)

def Elev(linenum, line, kw, args, d):
    '''Set output to elevation mode.  Instead of printing phi for
    spherical coordinates, phi's complement psi is printed instead;
    this measures the elevation above or below the xy plane.
    '''
    return SetClassVar("_elev", linenum, line, kw, args, d)

def Neg(linenum, line, kw, args, d):
    '''Set output to negative mode.  This means the theta angle is
    shown increasing in the opposite direction to what's customary.  
    '''
    return SetClassVar("_neg", linenum, line, kw, args, d)

def Indent(linenum, line, kw, args, d):
    if len(args) != 1:
        Bad(linenum, line, "Improper number of parameters", d)
    o = GetObj(linenum, line, args[0], d)
    try:
        num = int(o)
    except Exception:
        Bad(linenum, line, "Argument can't be interpreted as an integer", d)
    new_indent = max(0, len(d["indent"]) + num)
    d["indent"] = " "*new_indent if num else ""
    if _debug:
        dbg("[%s] indent %d:  new indent level = %d" % 
            (linenum, num, len(d["indent"])))
    return ("indent", num)

def TwoD(linenum, line, kw, args, d):
    '''Set output to 2D mode.  This means that points with a z
    coordinate of zero will only show the first two coordinates.
    '''
    if len(args) != 1:
        Bad(linenum, line, "Improper number of parameters", d)
    word = args[0]
    if word == "on":
        Ctm._suppress_z = True
    elif word == "off":
        Ctm._suppress_z = False
    else:
        try:
            val = eval(val, globals(), d["vars"])
            word = "on" if val == True else "off"
            Ctm._suppress_z = (val == True)
        except Exception:
            msg = "Argument must be 'on', 'off', or Boolean expression"
            Bad(linenum, line, msg, d)
    if _debug:
        dbg("[%s] 2D = %s" % (linenum, word))
    return ("2D", word)

def Alphabetical(linenum, line, kw, args, d):
    if len(args) != 1:
        Bad(linenum, line, "Improper number of parameters", d)
    word = args[0]
    if word == "on":
        d["alphabetical"] = True
    elif word == "off":
        d["alphabetical"] = False
    else:
        try:
            val = eval(val, globals(), d["vars"])
            word = "on" if val == True else "off"
            d["alphabetical"] = (val == True)
        except Exception:
            msg = "Argument must be 'on', 'off', or Boolean expression"
            Bad(linenum, line, msg, d)
    if _debug:
        dbg("[%s] alphabetical = %s" % (linenum, word))
    return ("2D", d["alphabetical"])

def IsAssignment(linenum, line, d):
    '''Return True if this is an assignment statement.  The logic is
    that the first "=" must occur by itself (i.e., not be followed by
    another "=" character.
    '''
    eqloc, assignment, n = line.find("="), False, len(line)
    if eqloc != -1 and eqloc < n - 1 and line[eqloc + 1] != "=":
        # If there's a token separator before the '=' character, then
        # it's a line with a keyword parameter like '. 1, 2, a, m=3'.
        if d["-s"] not in line[:eqloc]:
            assignment = True # It's a single = sign
    if assignment and d["-W"]:
        # Check for overwriting
        f = line.split("=")
        name = f[0].strip()
        if "." in name:
            g = name.split(".")
            name = g[0]
        CheckOverwrite(name, d, linenum, line)
    return assignment

def CTM(linenum, line, kw, args, d):
    '''Print the CTM.
    '''
    m = Ctm._CTM
    out(d["indent"] + "CTM [")
    out(d["indent"] + "  ", Listify(sig(m[:4])))
    out(d["indent"] + "  ", Listify(sig(m[4:8])))
    out(d["indent"] + "  ", Listify(sig(m[8:12])))
    out(d["indent"] + "  ", Listify(sig(m[12:])))
    out(d["indent"] + "]")

def ProcessLines(d):
    '''In the following code and function calls, we'll set the
    dictionary d up with two main additions.  d["objects"] will be an
    odict that will contain the names of the geometrical objects that
    the user defined in the order they were defined (the values will
    be None).
 
    d["vars"] will be a dictionary of all the defined variables and
    objects.  This is used as the set of local variables when
    evaluating expressions or code.
    '''
    # Set up a function dispatch table for each command
    d["dispatch"] = {
        # Define geometrical objects
        "."             : PointRect,
        "<"             : PointCyl,
        "<<"            : PointSph,
        "|"             : GetLine,
        "intersect"     : Intersect,
        "length"        : Length,
        "perp"          : Perp,
        "plane"         : GetPlane,
        "ijk"           : Ijk,
        # Transformations
        "pop"           : Pop,
        "push"          : Push,
        "reset"         : Reset, 
        "rotate"        : Rotate,
        "scale"         : Scale,
        "translate"     : Translate,
        "xy"            : XY,
        "xz"            : XY,
        "yz"            : XY,
        # Calculated things
        "angle"         : Angle,
        "area"          : Area,
        "centroid"      : Centroid,
        "circ3"         : Circ3,
        "cross"         : Cross,
        "dc"            : Dc,
        "dist"          : Dist,
        "dot"           : Dot,
        "trace"         : Trace,
        "project"       : Project,
        "reflect"       : Reflect,
        "rotaxis"       : Rotaxis,
        "length"        : Length,
        "locate"        : Locate,
        "stp"           : Stp,
        "vtp"           : Vtp,
        # Utility or state-changing
        "2D"            : TwoD,
        "alphabetical"  : Alphabetical,
        "angunit"       : Angunit,
        "compass"       : Compass,
        "cyl"           : Cyl,
        "date"          : Date,
        "deg"           : Deg,
        "del"           : Del,
        "digits"        : Digits,
        "elev"          : Elev,
        "eps"           : Eps,
        "exit"          : Exit,
        "eye"           : Eye,
        "indent"        : Indent,
        "neg"           : Neg,
        "polar"         : Cyl,
        "print"         : Print,
        "rad"           : Rad,
        "rect"          : Rect,
        "rev"           : Rev,
        "sph"           : Sph,
        "state"         : State,
        # Undocumented commands
        "ctm"           : CTM,  # Print the CTM
    }
    # Note all lines have trailing whitespace stripped, but may have
    # leading whitespace, which we'll remove if we're not in a code
    # block.
    off = False     # Flags that interpreting lines is off
    code = False    # Flags that we're in a code section
    for num, file, line in d["lines"]:
        linenum = "%s:%d" % (file, num)
        sline = line.lstrip()
        kw = sline.split()[0]
        if kw == "on":
            off = False
        elif off:
            pass
        elif kw == "off":
            off = True
        elif kw == "{":
            code = True
            codelines = []      # Start a new buffer
        elif kw == "}":
            code = False
            # Execute the buffer
            cmd = '\n'.join(codelines)
            if d["-D"]:
                c = compile(cmd, "", "exec")
                exec(c, globals(), d["vars"])
            else:
                try:
                    c = compile(cmd, "", "exec")
                    exec(c, globals(), d["vars"])
                except Exception as e:
                    msg = "Error in executing the following code:\n"
                    msg += cmd + "\n"
                    msg += "Error:  %s" % str(e)
                    Error(msg)
        elif code:
            codelines.append(line)
        elif kw[0] == "!":
            # Execute line as general python code
            s = sline[1:].strip()
            if _debug:
                dbg("[%s] %s" % (linenum, line.strip()))
            if d["-D"]:
                c = compile(s, "", "single")
                exec(c, globals(), d["vars"])
            else:
                try:
                    c = compile(s, "", "single")
                    exec(c, globals(), d["vars"])
                except Exception as e:
                    Bad(linenum, line, str(e), d)
        elif IsAssignment(linenum, line, d):
            line = line.strip()
            loc = line.find("=")
            if loc != -1 and loc < len(line) - 1:
                name, expr = line[:loc].strip(), line[loc + 1:].strip()
                if d["-D"]:
                    val = Interp(expr, d, linenum, line)
                else:
                    try:
                        val = Interp(expr, d, linenum, line)
                    except Exception as e:
                        msg = "Can't interpret assignment '%s'\n %s"
                        msg = msg % (line, str(e))
                        Bad(linenum, line, msg, d)
                    CheckOverwrite(name, d, linenum, line)
                    d["vars"][name] = val
            else:
                raise RuntimeError("Bug:  isn't an assignment")
            if _debug:
                dbg("[%s] %s" % (linenum, line))
            try:
                exec(line, globals(), d["vars"])
            except Exception as e:
                # If reached this point, then it's probably an
                # assignment using an uncertainty.  Try to
                # interpret this before failing.
                loc = line.find("=")
                if loc != -1 and loc < len(line) - 1:
                    name, expr = line[:loc], line[loc + 1:]
                    if d["-D"]:
                        val = Interp(expr, d, linenum, line)
                    else:
                        try:
                            val = Interp(expr, d, linenum, line)
                        except Exception as e:
                            msg = "Can't interpret assignment '%s'\n %s"
                            msg = msg % (line, str(e))
                            Bad(linenum, line, msg, d)
                        CheckOverwrite(name, d, linenum, line)
                        d["vars"][name] = val
        else:
            # It's a line defining an object or operation.  Since the
            # first token up to the d["-s"] split character can
            # contain space characters (we split on spaces to get the
            # keyword), find if there's such a remnant and prepend it
            # to the fields list if so.
            fields = sline.split(d["-s"])
            if " " in fields[0].strip():
                f = fields[0].strip().split()
                if len(f) > 1:
                    fields[0] = ' '.join(f[1:])
                kw = f[0]
            elif len(fields) == 1:
                kw = fields[0]
                fields = []
            # fields holds the arguments for the command or it's empty
            # if no arguments were supplied.
            fields = [i.strip() for i in fields]
            if d["-D"]:
                # Don't run the dispatched command with a try/except
                # block so that the traceback can be seen.
                d["dispatch"][kw](linenum, line, kw, fields, d)
            else:
                try:
                    d["dispatch"][kw](linenum, line, kw, fields, d)
                except KeyError as e:
                    msg = "%s is an unrecognized command" % str(e)
                    Bad(linenum, line, msg, d)
                except Exception as e:
                    Bad(linenum, line, str(e), d)
    if code:
        Bad(linenum, line, "Missing matching 'endcode' to 'code' command", d)

if __name__ == "__main__":
    d = {} # Options dictionary
    # Note: d["datafile"] is a list used as a stack; this allows us to
    # use the 'include' command and open a new datafile while
    # processing an existing one.
    d["datafile"] = ParseCommandLine(d)
    ReadDatafile(d)
    ProcessLines(d)
