'''
Calculate shaft/hole fits.  Adapted from Marv Klotz's fits.c program.

Comments from Marv's data file:
    Entries are:   fit name,constant,allowance
    constant is measured in thousandths of an inch
    allowance is measured in thousandths of an inch per inch of shaft diameter

    Example:  For a push fit on a nominal 1" shaft, machine the hole
    to exactly 1.0000", and machine the shaft to -0.35*(1.0)-0.15 =
    -0.5 thou less than the nominal size (0.9995").

    You can add your personal data to this file using any ascii text editor
    Program can handle up to 100 entries - if you need more contact me
    via email at: mklotz@alum.mit.edu
'''

import sys, os, getopt
from math import *

from pdb import set_trace as xx

fits = (
    # Class of fit, c, m
    # For a given hole diameter d, machine the shaft diameter D to
    # D = m*d/1000 + c/1000.  c is in mils and m is in mils per inch
    # of diameter.
    ("Shrink",             0.5,   1.5),
    ("Force",              0.5,   0.75),
    ("Drive",              0.3,   0.45),
    ("Push",              -0.15, -0.35),
    ("Slide",             -0.3,  -0.45),
    ("Precision running", -0.5,  -0.65),
    ("Close running",     -0.6,  -0.8),
    ("Normal running",    -1.0,  -1.5),
    ("Easy running",      -1.5,  -2.25),
    ("Small clearance",   -2.0,  -3.0),
    ("Large clearance",   -3.0,  -5.0),
)

in2mm = 25.4

# The following can be either in for inches or mm for millimeters.
# This lets you choose the default units used for calculations.
basic_unit = "inches"

# Conversion factors to inches.  If you add to this dictionary, make
# sure to add the unit string to the following search_units sequence.
allowed_units = {
    "in"        : float(1),
    "inch"      : float(1),
    "inches"    : float(1),
    "mil"       : float(1)/1000,
    "mils"      : float(1)/1000,
    "feet"      : float(12),
    "ft"        : float(12),
    "yard"      : float(36),
    "yd"        : float(36),
    "m"         : float(1000/in2mm),
    "cm"        : float(1)/(10*in2mm),
    "mm"        : float(1)/in2mm,
}

# To avoid ambiguities, the units of the allowed units are searched
# for in the following order on the command line.  The reason is e.g.
# that searching for "m" first will also find "mm".
search_units = (
    "cm",
    "mm",
    "m",
    "inches",
    "inch",
    "in",
    "mils",
    "mil",
    "feet",
    "ft",
    "yard",
    "yd",
)

def out(*v, **kw):
    sep = kw.setdefault("sep", " ")
    nl  = kw.setdefault("nl", True)
    stream = kw.setdefault("stream", sys.stdout)
    stream.write(sep.join([str(i) for i in v]))
    if nl:
        stream.write("\n")

def Check():
    '''Make sure our global variables are consistent.
    '''
    if basic_unit not in ("in", "inch", "inches", "mm"):
        msg = "basic_unit = '%s', which isn't allowed" % basic_unit
        out(msg, stream=sys.stderr)
        exit(1)
    msg = '''
allowed_units and search_units not compatible (you need to fix these
global variables).
'''[1:-1]
    if len(search_units) != len(allowed_units):
        out(msg, stream=sys.stderr)
        exit(1)
    if set(search_units) != set(allowed_units.keys()):
        out(msg, stream=sys.stderr)
        exit(1)

def Usage(d, status=1):
    path, name = os.path.split(sys.argv[0])
    basic = basic_unit
    units = allowed_units.keys()
    units.sort()
    units = str(units).replace("[", "").replace("]", "").replace("'", "")
    out('''
Usage:  {name} [options] diameter [unit]
  For a given diameter, print a table showing fits for both basic hole
  size and basic shaft size (here, "basic" means you've got the hole
  or shaft size you want and you want to calculate the size of the
  mating part to get a desired fit).  The diameter is measured in
  {basic} by default.  You can include a unit on the command line; 
  allowed units are:
    {units}.

  The command line can include python expressions; the math module's
  symbols are all in scope.  This, for example, lets you use fractions
  for input; suppose you needed a hole for a sliding fit with a shaft
  of diameter in feet of 3/4*cos(80 degrees).  You'd use the command
  line arguments

      3/4*cos(80*pi/180) ft

  and the needed hole diameter would be 1.5638 inches (39.721 mm); it
  would have 1 mil of clearance (25 um).
 
  The script is based on Tubal Cain's table of fit allowances and
  software written by Marv Klotz.
 
Options
    -m
        The dimensions given on the command line will be assumed to be
        mm.
'''.strip().format(**locals()))
    exit(status)

def ParseCommandLine(d):
    d["-m"] = False         # Use mm on command line by default
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "hm")
    except getopt.GetoptError as str:
        msg, option = str
        out(msg + nl)
        sys.exit(1)
    for opt in optlist:
        if opt[0] == "-h":
            Usage(d, 0)
        if opt[0] == "-m":
            d["-m"] = not d["-m"]
    if len(args) < 1:
        Usage(d)
    return args

def HoleBasic(D, d):
    '''D is hole size in inches.
    '''
    shaft_size_in = D
    shaft_size_mm = D*in2mm
    out("\nHole size is basic:")
    hole_size_in = float(D)
    hole_size_mm = in2mm*D
    out('''
                            Shaft size          Clearance
                           in        mm        mils     mm
                        -------   --------    -----   ------
'''[1:-1])
    for name, constant, allowance in fits:
        correction = (allowance*hole_size_in + constant)/1000
        shaft_size_in = hole_size_in + correction
        shaft_size_mm = shaft_size_in*in2mm
        clearance_mils = (hole_size_in - shaft_size_in)*1000
        clearance_mm   = clearance_mils*in2mm/1000
        s = "  %-18s %10.4f %10.3f %8.2f %8.3f" % \
            (name, shaft_size_in, shaft_size_mm, clearance_mils, clearance_mm)
        out(s)

def ShaftBasic(D, d):
    '''D is hole size in inches.
    '''
    shaft_size_in = float(D)
    shaft_size_mm = in2mm*D
    out("\nShaft size is basic:")
    out('''
                             Hole size          Clearance
                           in        mm        mils     mm
                        -------   --------    -----   ------
'''[1:-1])
    for name, constant, allowance in fits:
        correction = -(allowance*shaft_size_in + constant)/1000
        hole_size_in = shaft_size_in + correction
        hole_size_mm = hole_size_in*in2mm
        clearance_mils = (hole_size_in - shaft_size_in)*1000
        clearance_mm   = clearance_mils*in2mm/1000
        s = "  %-18s %10.4f %10.3f %8.2f %8.3f" % \
            (name, hole_size_in, hole_size_mm, clearance_mils, clearance_mm)
        out(s)

def GetDiameter(args, d):
    '''Given the command line arguments, return the command and the 
    diameter in inches that the user requested data for.
    '''
    cmdline = ' '.join(args)
    s = ''.join(args).replace(" ", "")
    unit = None
    for u in search_units:
        loc = s.find(u)
        if loc != -1:
            # This unit was found.  Verify it's at the end of the
            # string.
            if loc + len(u) != len(s):
                # It can't be an ending suffix
                continue
            else:
                # Get diameter in inches
                diam = float(eval(s[:loc]))*allowed_units[u]
                return (cmdline, diam)
    # No units were found.  Try to convert to a float.  Note the eval
    # allows expressions.
    try:
        diam = float(eval(s))
        return (cmdline, diam/in2mm) if d["-m"] else (cmdline, diam)
    except ValueError:
        out("Can't figure out diameter from command line:\n  '%s'" % s,
            stream=sys.stderr)
        exit(1)

def CalculateFit(cmdline, D, d):
    '''hole_size_inches is diameter of hole in inches.  d is the
    settings dictionary.
    '''
    Dmm = D*in2mm
    out("Diameter = " + cmdline)
    out("         = %.4f" % D, "inches")
    out("         = %.3f" % Dmm, "mm")
    HoleBasic(D, d)
    ShaftBasic(D, d)

def main():
    Check()
    d = {} # Options dictionary
    args = ParseCommandLine(d)
    cmdline, D = GetDiameter(args, d)
    CalculateFit(cmdline, D, d)

main()
