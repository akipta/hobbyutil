'''
Given a textfile of circle diameters (separated by whitespace), space
these circles equally around a circle whose diameter is given on the
command line.

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

from pdb import set_trace as xx #xx
import debug #xx


have_g = False
try:
    from g import *
    have_g = True
except ImportError:
    pass

r2d = 180/pi

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
    digits = sig.digits
    s = '''
Usage:  {name} [options] datafile diameter
  Will print a table of positions (Cartesian, angles, and chords) of
  the centers of the circles whose diameters are given in the datafile
  (one number per line) so that the angle between each of the circles
  is a constant.
 
  The datafile may contain lines of the form 'a = b' which causes a
  variable named a to be defined.  This variable can then be used in
  subsequent lines.  b is a valid python expression; note that all the
  symbols from the math module are also in scope.  These assignment
  lines must be one per line.  The diameter of the main circle is
  defined to be the symbol D.
 
  If you have the optional graphics library from
  http://code.google.com/p/pygraphicsps/, the script can generate a
  scaled drawing of the layout.
 
Options:
    -d digits
        Number of significant figures in results.  Default = {digits}.
    -g file
        Generate a Postscript drawing file of the layout.
    -r
        Lay out the circles in a clockwise direction (the default
        direction is counterclockwise).

Example:  suppose the datafile contains
    1/4
    5/16
    3/8
    7/16
    1/2
Running the script with the diameter 2 gives the output

Main circle diameter = 2.000
                                       Polar ang.,                Ang. width,
    Dia           x             y        degrees       chord        degrees
-----------------------------------------------------------------------------
     0.2500       1.000        0.           0.           1.097       14.36   
     0.3125       0.3982       0.9173      66.53         1.149       17.98   
     0.3750      -0.7277       0.6859     136.7          1.201       21.61   
     0.4375      -0.8616      -0.5075     210.5          1.252       25.27   
     0.5000       0.3086      -0.9512     288.0          1.176       28.96   

Angle subtended by all circles = 108.2 deg = 1.888 rad
Gap angle between each circle  = 50.36 deg = 0.8790 rad
'''[1:-1]
    out(s.format(**locals()))
    sys.exit(status)

if have_g:
    def SetUp(file, orientation=landscape, units=inches):
        '''Convenience function to set up the drawing environment and return a
        file object to the output stream.
        '''
        ofp = open(file, "w")
        ginitialize(ofp, wrap_in_PJL=0)
        setOrientation(orientation, units)
        return ofp

def ParseCommandLine(d):
    d["-d"] = 4         # Number of significant figures in results
    sig.digits = d["-d"]
    d["-g"] = None      # Construct a Postscript drawing of output
    d["-r"] = False     # Go in clockwise direction
    d["warn_ratio"] = 0.9 # When to warn about a circle's diameter
    if len(sys.argv) < 2:
        Usage(d)
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "d:Dg:r")
    except getopt.GetoptError as e:
        msg, option = e
        out(msg)
        exit(1)
    for opt in optlist:
        if opt[0] == "-a":
            d["-a"] = True
        if opt[0] == "-D":
            debug.SetDebugger()
        if opt[0] == "-b":
            d["-b"] = opt[1]
        if opt[0] == "-d":
            d["-d"] = int(opt[1])
            if d["-d"] < 1:
                Error("-d option must be integer > 0")
            sig.digits = d["-d"]
        if opt[0] == "-g":
            d["-g"] = opt[1]
        if opt[0] == "-h":
            Usage(d, status=0)
        if opt[0] == "-r":
            d["-r"] = True
    if len(args) == 1:
        Error("Need a diameter as a second argument")
    if len(args) != 2:
        Usage(d)
    return args

def ReadDatafile(__datafile, __d):
    '''Return the variables the user defined along with the diameters
    of the circles.
    '''
    __lines = [__i.strip() for __i in open(__datafile).readlines()]
    __diameters = []
    __msg = "Error in line %d:\n"
    __msg += "  Line:  '%s'"
    __msg += "  Error:  %s"
    D = __d["diameter"]
    for __num, __line in enumerate(__lines):
        __linenum = __num + 1
        __line = __line.strip()
        if not __line or __line[0] == "#":
            continue
        if "=" in __line:
            # An assignment statement -- put into the local namespace
            try:
                exec(__line)
            except Exception as __e:
                Error(__msg % (__linenum, __line, str(__e)))
        else:
            # It's an expression for a diameter
            try:
                __x = eval(__line)
                __diameters.append(__x)
            except Exception as __e:
                Error(__msg % (__linenum, __line, str(__e)))
    # Get the locals dictionary, delete the items that begin with two
    # underscores, and return it.
    vars, rm = locals(), []
    for i in vars:
        if len(i) > 2 and i[:2] == "__":
            rm.append(i)
    for i in rm:
        del vars[i]
    __d["vars"] = vars
    __d["diameters"] = __diameters
    return __diameters

def Fmt(x, d):
    '''Return string representation of the number x.  If it's an
    integer, just return its string.  If it's a float, then use sig.
    '''
    if isinstance(x, (int, long)):
        return str(x)
    else:
        return sig(x)

def SolveProblem(diameters, vars, d):
    '''diameters is a list of the circle diameters desired to be
    placed evenly spaced on a circle of diameter d["diameter"].
    Compute the gap angle in radians, then return a list of tuples of
    the form
        (diameter, x, y, polar_angle, chord_to_next, angle_subtended)
    where diameter is the circle diameter, (x, y) are the Cartesian
    coordinates of the center of the circle (will be on the main
    circle), angle is the polar angle of the circle's center (the
    first circle is defined to have zero polar angle), and
    chord_to_next is the distance to the center of the next circle.
    '''
    R, results, n, theta_total = d["vars"]["D"]/2, [], len(diameters), 0
    neg = -1 if d["-r"] else 1
    # Calculate angular widths 
    for dia in diameters:
        r = dia/2
        a = (R/r)**2
        if a < 1:
            msg = "Circle with diameter %s too large" % sig(dia)
            Error(msg)
        # Angular width of this circle.
        thetai = neg*2*atan(1/sqrt(a - 1))
        theta_total += abs(thetai)
        results.append([dia, 0, 0, 0, 0, thetai])
    if theta_total > 2*pi:
        Error("No solution possible")
    # Number of gaps is equal to the number of circles
    gap = (2*pi - theta_total)/n
    d["gap"] = gap
    d["theta_total"] = theta_total
    # Calculate polar angle of each circle center.  The first circle
    # will always be on the x axis.
    results[0][3] = 0
    for i in range(1, len(diameters)):
        theta = abs(results[i - 1][5]/2) + abs(gap) + abs(results[i][5]/2)
        results[i][3] = neg*(theta + abs(results[i - 1][3]))
    # Calculate the Cartesian coordinates of the circles' centers
    for i in range(len(results)):
        theta = results[i][3]
        results[i][1] = R*cos(theta)
        results[i][2] = R*sin(theta)
    # Calculate chords
    for i in range(len(results)):
        # j is index of next circle (note it has to wrap around if i
        # is the last circle in the list).
        j = i + 1 if i != len(results) - 1 else 0
        x1, y1 = results[i][1], results[i][2]
        x2, y2 = results[j][1], results[j][2]
        chord = hypot(x1 - x2, y1 - y2)
        results[i][4] = chord
    return results

def PrintReport(results, diameters, d):
    R = d["vars"]["D"]/2
    out("Main circle diameter =", sig(2*R))
    for dia in diameters:
        r = dia/2
        if r/R > d["warn_ratio"]:
            out("  Warning:  large diameter circle: ", Fmt(dia, d))
    sig.fit = w = 12
    sig.dp_position = sig.fit//2
    out("                                       Polar ang.,                Ang. width,")
    out("    Dia           x             y        degrees       chord        degrees")
    out("-"*77)
    for item in results:
        dia, x, y, theta, chord, thetai = item
        sdia = sig(dia)
        sx = sig(x)
        sy = sig(y)
        stheta = sig(theta*r2d)
        schord = sig(chord)
        sangle = sig(abs(thetai*r2d))
        s = "{sdia:{w}} {sx:{w}} {sy:{w}} {stheta:{w}} {schord:{w}} {sangle:{w}}"
        out(s.format(**locals()))
    sig.fit = 0
    out()
    out("Angle subtended by all circles =", Fmt(d["theta_total"]*r2d, d), 
        "deg", "=", Fmt(d["theta_total"], d), "rad")
    gap = abs(d["gap"])
    out("Gap angle between each circle  =", Fmt(gap*r2d, d), "deg", 
        "=", Fmt(gap, d), "rad")
    out()

def Plot(results, diameters, d):
    # We'll assume US letter-size paper.  Change the width W and the
    # height H if you wish to plot to another paper size.
    SetUp(d["-g"], orientation=landscape, units=inches)
    W, H, n = 11, 8.5, len(diameters)
    margin = 0.5
    # Put origin at center of page
    translate(W/2, H/2)
    # Draw coordinate axes
    r = 0.45*H
    LineType(little_dash)
    LineColor(gray(0.5))
    line(-r, 0, r, 0)
    line(0, -r, 0, r)
    LineType(solid_line)
    LineColor(black)
    # Text characteristics
    T = 0.15
    t = T/3
    TextSize(T)
    TextName(SansBold)
    # Dimensions of plotting viewport
    w, h = W - 2*margin, H - 2*margin
    r = max(diameters)/2
    R = d["vars"]["D"]/2
    # Scale things so that all circles will fit on page
    S = h/(2*(r + R))
    scale(S, S)
    move(0, 0)
    # Draw main circle
    circle(2*R)
    x, y = -w/2, h/2 - margin
    move(x/S, y/S)
    TextLines((
        "Main circle dia = " + sig(2*R),
        "Chords in red",
        "Gap angle = " + sig(d["gap"]*r2d) + " deg",
    ))
    # Plot small circles
    sig.rtz = True
    for i in range(len(results)):
        dia, x, y, theta, chord, thetai = results[i]
        move(x, y)
        line(0, 0, x, y)
        circle(dia)
        # Label with diameter
        push()
        rotate(theta*r2d)
        x = R + dia/2 + t/S
        move(x, -t/S)
        text(sig(dia))
        move(R/2, t/(2*S))
        ctext(sig(theta*r2d))
        TextName(Symbol)
        text(chr(176))
        pop()
        # Label with chord
        push()
        next = results[(i + 1) % n][3] + 2*pi*(not ((i + 1) % n))
        current = results[i][3]
        dtheta = (next - current)/2
        rotate((theta + dtheta)*r2d)
        x = R*0.75 
        TextColor(red)
        move(x, -t/S)
        text(sig(chord))
        pop()

def main():
    d = {} # Options dictionary
    datafile, diameter = ParseCommandLine(d)
    try:
        d["diameter"] = float(eval(diameter))
    except Exception as e:
        msg = "Command line diameter '%s' couldn't be evaluated:\n"
        msg += "  Error:  %s"
        Error(msg % (diameter, str(e)))
    diameters = ReadDatafile(datafile, d)
    results = SolveProblem(diameters, vars, d)
    PrintReport(results, diameters, d)
    if d["-g"]:
        Plot(results, diameters, d)

main()
