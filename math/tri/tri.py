'''
uuu
Solve a triangle given sufficient information about the sides and
angles.  Use the -h option to see a manpage.

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
from pdb import set_trace as xx


have_unc = False

try:
    # If you wish to add uncertainties to numbers, you'll need to install
    # the uncertainties library from
    # http://pypi.python.org/pypi/uncertainties/.
    from uncertainties import ufloat, AffineScalarFunc
    from uncertainties.umath import asin, acos, sqrt, sin, cos
    have_unc = True
except ImportError:
    from math import acos, sqrt, sin, cos

if sys.version_info[0] == 3:
    py3 = True
    Input = input
else:
    py3 = False
    Input = raw_input

d2r = pi/180    # Constant for converting degrees to radians
r2d = 1/d2r

# Flags a bad numerical condition
class CannotBeZero(Exception):  pass

def out(*v, **kw):
    sep = kw.setdefault("sep", " ")
    nl  = kw.setdefault("nl", True)
    stream = kw.setdefault("stream", sys.stdout)
    if v:
        stream.write(sep.join([str(i) for i in v]))
    if nl:
        stream.write("\n")

def Error(msg, status=1):
    out(msg, stream=sys.stderr)
    exit(status)

def Usage(d, status=1):
    name = sys.argv[0]
    s = '''
Usage:  {name} [options] [datafile]
  Solve a triangle given the requisite sides and angles.  Here,
  "solving" means that the three angles and three sides of the
  triangle will be printed in the report, along with ancillary
  information about the triangle.

  If you don't give a datafile for input, you'll be prompted for the
  problem's details.  The datafile's lines must be of the following
  types:

    deg     # Use degrees for angle measure
    rad     # Use radians for angle measure
    sss     # Solve the side-side-side problem
    ssa     # Solve the side-side-angle problem
    sas     # Solve the side-angle-side problem
    saa     # Solve the side-angle-angle problem
    asa     # Solve the angle-side-angle problem
    var = value     # Variable assignment

  In a variable assignment, you can assign to any legal python
  variable name (don't use names that start with double underscores).
  Any variables you define will be in scope for later expressions.
  For the problem you want solved, you must includes the appropriate
  sides as s1, s2, and s3 and appropriate angles as a1, a2, a3.  Angle
  a1 is opposite side s1, etc.  Example:  specify angle 1 as an
  expression (here, angles are assumed to be measured in degrees):

    a1 = 42*sin(25)

  Blank lines and lines that begin with a '#' after leading whitespace
  is removed are ignored.

  value can be a legal python expression; note that all the symbols of
  the math module are in scope.  You can also include an expression in
  square brackets after the number expression; this represents the
  uncertainty of the number.  The computed values will then display
  the propagated uncertainties.  The output will be in the usual
  short-hand form: 1.234(5) denotes a measured value 1.234 with an
  uncertainty of 0.005.
 
  For uncertainty calculations to work, you'll have to install the
  python uncertainties module from
  http://pypi.python.org/pypi/uncertainties/.  If it's not installed,
  any provided uncertainties will be ignored.

Options:
    -d digits
        Set the number of significant digits for the report.  This
        setting has no effect if the numbers have uncertainties, as
        the number of digits output is determined by the uncertainty.
    -h
        Print a manpage to stdout.
    -t 
        Run self-tests.
'''[1:-1]
    out(s.format(**locals()))
    sys.exit(status)

def ParseCommandLine(d):
    sig.digits = 4
    # Use degrees as the default angle measure.  If you want to use
    # radians as the default, change this to 1.
    d["angle_measure"] = pi/180
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "d:hit")
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
        if opt[0] == "-h":
            Usage(d, 0)
        if opt[0] == "-t":
            Test()
            exit(0)
    if not args:
        return None
    if len(args) != 1:
        Usage(d)
    return args[0]

def Dict(vars):
    '''vars is a dictionary of local variables.  Remove all variable
    names that begin with two underscores and also remove __d.
    '''
    v = vars.copy()
    del v["__d"]
    keys = list(v.keys())
    rm = []
    for k in keys:
        if len(k) > 2 and k[:2] == "__":
            rm.append(k)
    for i in rm:
        del v[i]
    return v

def InterpretNum(__s, __vars):
    '''__s is a string that can be of the forms e.g. '12.3' or '12.3
    [0.1]' where the second form denotes an uncertainty.  The numbers
    can also be expressions using the variables in the __vars
    dictionary.  Evaluate the string and return either a floating
    point number or a ufloat.

    Note we'll raise an exception if the number is 0 or less.
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
            if __mean <= 0:
                raise CannotBeZero("Value must be greater than zero")
            __stddev = float(eval(__s[__locl + 1:__locr]))
            if have_unc:
                return ufloat(__mean, __stddev)
            else:
                return __mean
        else:
            __mean = float(eval(__s))
            if __mean <= 0:
                raise CannotBeZero("Value must be greater than zero")
            return __mean
    except CannotBeZero as __e:
        raise
    except Exception as __e:
        Error("Can't evaluate '%s'\n  Error:  %s" % (__s, str(__e)))

def GetDataInteractively(__d):
    out("** Triangle solving utility **\n")
    while True:
        __v = Input("Number of significant digits to display [%d]: " %
            sig.digits)
        __v = __v.strip()
        if __v in ("q", "Q"):
            exit(0)
        if not __v:
            break
        else:
            try:
                __x = int(__v)
                if not (1 <= __x <= 15):
                    raise Exception()
                sig.digits = __x
                break
            except Exception as e:
                out("Must be an integer between 1 and 15")
        
    while True:
        __v = Input("Degrees [d] or radians (r) for angle measure: ")
        __v = __v.strip()
        if __v in ("q", "Q"):
            exit(0)
        elif __v in ("d", "D", ""):
            __d["angle_measure"] = pi/180
            out("  --> Using degrees")
            break
        elif __v in ("r", "R"):
            __d["angle_measure"] = 1
            out("  --> Using radians")
            break
        else:
            out("Improper response -- must be 'd' or 'r'")
    out('''Enter the type of problem you want solved [sss]:
  sss:  Given three sides are given
  ssa:  Given two sides and an angle not between the two sides
  sas:  Given two sides and angle between the two sides
  saa:  Given one side and one angle opposite and one adjacent
  asa:  Given one side and the two angles on either side''')
    while True:
        __prob = Input("Problem?  ")
        __prob = __prob.strip().lower()
        if __prob in ("q", "Q"):
            exit(0)
        if not __prob:
            __d["problem_type"] = "sss"
            __prob = "sss"
            out("  --> Solving sss problem")
            break
        if __prob not in ("sss", "ssa", "sas", "saa", "asa"):
            out("Improper problem abbreviation")
            continue
        else:
            __d["problem_type"] = __prob
            break
    __need = {
        # Encodes the number of sides and number of angles to prompt for
        "sss" : (3, 0),
        "ssa" : (2, 1),
        "sas" : (2, 1),
        "saa" : (1, 2),
        "asa" : (1, 2),
    }
    # Get sides
    for __i in range(1, __need[__prob][0] + 1):
        while True:
            __v = Input("Enter length of side %d:  " % __i)
            __v = __v.strip()
            if __v in ("q", "Q"):
                exit(0)
            elif "=" in __v:
                try:
                    exec(__v)
                    out("Assignment OK")
                except Exception as e:
                    out("Assignment failed:  %s" % str(e))
            else:
                try:
                    __x = InterpretNum(__v, Dict(locals()))
                    exec("S%d = __x" % __i)
                    break
                except Exception as e:
                    out("Number not correct:  %s" % str(e))
    # Get angles.  Note we'll return the numbers the user typed in.
    for __i in range(1, __need[__prob][1] + 1):
        while True:
            __v = Input("Enter angle %d:  " % __i)
            __v = __v.strip()
            if __v in ("q", "Q"):
                exit(0)
            elif "=" in __v:
                try:
                    exec(__v)
                    out("Assignment OK")
                except Exception as e:
                    out("Assignment failed:  %s" % str(e))
            else:
                try:
                    __x = InterpretNum(__v, Dict(locals()))
                    exec("A%d = __x" % __i)
                    break
                except Exception as e:
                    out("Number not correct:  %s" % str(e))
    __d["vars"] = Dict(locals())
    out()

def ReadDatafile(__datafile, __d):
    __lines = [__i.strip() for __i in open(__datafile).readlines()]
    try:
        for __i, __line in enumerate(__lines):
            __linenum = __i + 1
            if not __line or __line[0] == "#":
                continue
            if "=" not in __line:
                if __line == "deg":
                    __d["angle_measure"] = d2r
                elif __line == "rad":
                    __d["angle_measure"] = 1
                elif __line in ("sss", "ssa", "sas", "asa", "saa"):
                    __d["problem_type"] = __line
                else:
                    raise Exception("Line not an assignment or keyword")
                continue
            __f = [__j.strip() for __j in __line.split("=")]
            if len(__f) > 2:
                raise Exception("Too many '=' signs")
            # Get the variable into our local namespace
            __x = InterpretNum(__f[1], locals())
            exec("%s = __x" % __f[0])
    except Exception as __e:
        __msg = "Line %d is bad in datafile '%s'\n" % (__linenum, __datafile)
        __msg += "  Line:  '%s'\n" % __line
        __msg += "  Error:  %s" % str(__e)
        Error(__msg)
    # Set d["vars"] to the defined variables
    __d["vars"] = Dict(locals())

def SolveProblem(d):
    # Get our needed variables
    for k in d["vars"]:
        if k in set(("S1", "S2", "S3", "A1", "A2", "A3")):
            exec("%s = d['vars']['%s']" % (k, k))
    angle_conv = d["angle_measure"]  # Converts angle measure to radians
    prob = d["problem_type"]
    try:
        if prob == "sss":
            # Law of cosines to find two angles, angle law to find third.
            A1 = acos((S2**2 + S3**2 - S1**2)/(2*S2*S3))
            A2 = acos((S1**2 + S3**2 - S2**2)/(2*S1*S3))
            A3 = pi - A1 - A2
        elif prob == "ssa":
            # Law of sines to find the other two angles and remaining
            # side.  Note it can have two solutions (the second solution's
            # data will be in the variables s1_2, s2_2, etc.).
            A1 *= angle_conv  # Make sure angle is in radians
            A2 = asin((S2/S1*sin(A1)))
            A3 = pi - A1 - A2
            S3 = S2*sin(A3)/sin(A2)
            # Check for other solution
            A1_2 = A1
            A2_2 = pi - A2
            A3_2 = pi - A1_2 - A2_2
            if A1_2 + A2_2 + A3_2 > pi:
                # Second solution not possible
                del A1_2
                del A2_2
                del A3_2
            else:
                # Second solution is possible
                S1_2 = S1
                S2_2 = S2
                S3_2 = S2_2*sin(A3_2)/sin(A2_2)
        elif prob == "sas":
            # Law of cosines to find third side; law of sines to find
            # another angle; angle law for other angle.  Note we rename
            # the incoming angle to be consistent with a solution diagram.
            A3 = A1*angle_conv  # Make sure angle is in radians
            S3 = sqrt(S1**2 + S2**2 - 2*S1*S2*cos(A3))
            A2 = asin(S2*sin(A3)/S3)
            A1 = pi - A2 - A3
        elif prob == "asa":
            # Third angle from angle law; law of sines for other two
            # sides.  Note we rename the sides for consistency with a
            # diagram.
            A1 *= angle_conv  # Make sure angle is in radians
            A2 *= angle_conv  # Make sure angle is in radians
            A3 = pi - A1 - A2
            S3 = S1
            S2 = S3*sin(A2)/sin(A3)
            S1 = S3*sin(A1)/sin(A3)
        elif prob == "saa":
            # Third angle from angle law; law of sines for other two
            # sides. 
            A1 *= angle_conv  # Make sure angle is in radians
            A2 *= angle_conv  # Make sure angle is in radians
            A3 = pi - A1 - A2
            S2 = S1*sin(A2)/sin(A1)
            S3 = S1*sin(A3)/sin(A1)
        else:
            raise ValueError("Bug:  unrecognized problem")
    except UnboundLocalError as e:
        s = str(e)
        loc = s.find("'")
        s = s[loc + 1:]
        loc = s.find("'")
        s = s[:loc]
        Error("Variable '%s' not defined" % s)
    except ValueError as e:
        msg = "Can't solve the problem:\n"
        msg += "  Error:  %s" % str(e)
        Error(msg)
    # Collect solution information
    solution = {}
    vars = set((
        "S1", "S2", "S3", "A1", "A2", "A3",
        "S1_2", "S2_2", "S3_2", "A1_2", "A2_2", "A3_2",
    ))
    for k in vars:
        if k in locals():
            exec("solution['%s'] = %s" % (k, k))
    d["solution"] = solution

def Test():
    '''The following test cases came from the sample problems at
    http://www.mathsisfun.com/algebra/trig-solving-triangles.html
    '''
    eps, r2d, d2r = 1e-14, 180/pi, pi/180
    d = {
        "angle_measure" : d2r,
    }
    # sss
    d["vars"] = {
        "S1" : 6,
        "S2" : 7,
        "S3" : 8,
    }
    d["problem_type"] = "sss"
    SolveProblem(d)
    k = d["solution"]
    assert abs(k["A1"] - acos(77/112)) < eps
    assert abs(k["A2"] - (pi - k["A3"] - k["A1"])) < eps
    assert abs(k["A3"] - acos(1/4)) < eps
    # ssa
    d["vars"] = {
        "S1" : 8,
        "S2" : 13,
        "A1" : 31,  # Angle in degrees
    }
    d["problem_type"] = "ssa"
    SolveProblem(d)
    k = d["solution"]
    a2 = asin(13*sin(31*d2r)/8)
    assert abs(k["A2"] - a2) < eps
    a3 = pi - k["A2"] - k["A1"]
    assert abs(k["A3"] - a3) < eps
    assert abs(k["S3"] - sin(a3)*8/sin(31*d2r)) < eps
    # Check other solution
    a2_2 = pi - asin(13*sin(31*d2r)/8)
    assert abs(k["A2_2"] - a2_2) < eps
    a3_2 = pi - k["A2_2"] - k["A1_2"]
    assert abs(k["A3_2"] - a3_2) < eps
    assert abs(k["S3_2"] - sin(a3_2)*8/sin(31*d2r)) < eps
    # sas
    d["vars"] = {
        "S1" : 5,
        "S2" : 7,
        "A1" : 49,  # Angle in degrees
    }
    d["problem_type"] = "sas"
    SolveProblem(d)
    k = d["solution"]
    # asa
    d["vars"] = {
        "S1" : 9,
        "A1" : 76,  # Angle in degrees
        "A2" : 34,  # Angle in degrees
    }
    d["problem_type"] = "asa"
    SolveProblem(d)
    k = d["solution"]
    assert abs(k["S2"] - 9*sin(34*d2r)/sin(70*d2r)) < eps
    assert abs(k["S1"] - 9*sin(76*d2r)/sin(70*d2r)) < eps
    assert abs(k["A3"] - 70*d2r) < eps
    # saa
    d["vars"] = {
        "S1" : 7,
        "A1" : 62,  # Angle in degrees
        "A2" : 35,  # Angle in degrees
    }
    d["problem_type"] = "saa"
    SolveProblem(d)
    k = d["solution"]
    assert abs(k["A3"] - 83*d2r) < eps
    assert abs(k["S2"] - 7*sin(35*d2r)/sin(62*d2r)) < eps
    assert abs(k["S3"] - 7*sin(83*d2r)/sin(62*d2r)) < eps
    out("Tests passed")

def GetOtherFacts(s1, s2, s3, a1, a2, a3, d):
    '''Calculate the other relevant measures of the triangle.
    '''
    A = s1*s2*sin(a3)/2
    s = (s1 + s2 + s3)/2
    r = A/s
    R = s1*s2*s3/(4*A)
    d["area"] = A
    d["perimeter"] = 2*s
    d["r_inscribed"] = r
    d["R_circumscribed"] = R

def Report(d):
    S, w = d["solution"], 15
    angle_measure = 1/d["angle_measure"]
    if angle_measure == 1:
        dm = "rad"
    else:
        dm = "deg"
    ds = " "*5
    S1, S2, S3, A1, A2, A3 = [S[i] for i in  "S1 S2 S3 A1 A2 A3".split()]
    s1, s2, s3 = [sig(i) for i in (S1, S2, S3)]
    a1, a2, a3 = [sig(i*angle_measure) for i in (A1, A2, A3)]
    GetOtherFacts(S1, S2, S3, A1, A2, A3, d)
    area = sig(d["area"])
    r = sig(d["r_inscribed"])
    R = sig(d["R_circumscribed"])
    di = sig(d["r_inscribed"]*2)
    D = sig(d["R_circumscribed"]*2)
    p = sig(d["perimeter"])
    title = "Triangle solution"
    fmt = '''{title}:
  Sides  {ds}          {s1:{w}} {s2:{w}} {s3:{w}}
  Angles ({dm})          {a1:{w}} {a2:{w}} {a3:{w}}
  Area                  {area}
  Perimeter             {p}
  Inscribed circle      radius = {r}, diameter = {di}   [Note 1]
  Circumscribed circle  radius = {R}, diameter = {D}   [Note 2]'''
    out(fmt.format(**locals()))
    # Check for 2nd solution
    if "S1_2" in S:
        S1, S2, S3, A1, A2, A3 = [S[i] for i in  
            "S1_2 S2_2 S3_2 A1_2 A2_2 A3_2".split()]
        GetOtherFacts(S1, S2, S3, A1, A2, A3, d)
        s1, s2, s3 = [sig(i) for i in (S1, S2, S3)]
        a1, a2, a3 = [sig(i*angle_measure) for i in (A1, A2, A3)]
        title = "Second solution"
        area = sig(d["area"])
        r = sig(d["r_inscribed"])
        R = sig(d["R_circumscribed"])
        di = sig(d["r_inscribed"]*2)
        D = sig(d["R_circumscribed"]*2)
        p = sig(d["perimeter"])
        out(fmt.format(**locals()))
    out('''  
  [1] Center located by angle bisectors.  
  [2] Center located by perpendicular bisectors of the sides.''')

if __name__ == "__main__":
    d = {} # Options dictionary
    datafile = ParseCommandLine(d)
    if datafile is None:
        GetDataInteractively(d)
    else:
        ReadDatafile(datafile, d)
    SolveProblem(d)
    Report(d)
