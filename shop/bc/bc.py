'''
Calculate the Cartesian coordinates of bolt holes on a circle.

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
from sig import sig
from getnumber import GetNumber
from math import sin, cos, pi


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

    out(s.format(**locals()))
    sys.exit(status)

def GetParameters(d):
    out("Print a table of the Cartesian coordinates of holes on a circle.")
    digits = GetNumber("How many significant digits?", numtype=int, default=4,
        low=1, high=15)
    n = GetNumber("How many holes to place?", numtype=int, default=6,
        low=0, low_open=True)
    dia = GetNumber("Bolt circle diameter? ", low=0, low_open=True,
        default=1)
    theta_offset = GetNumber("Angle offset of first hole (degrees)? ",
        default=0)
    x0 = GetNumber("x position of origin? ", default=0)
    y0 = GetNumber("y position of origin? ", default=0)
    return n, dia, theta_offset, x0, y0, digits

if __name__ == "__main__":
    d = {} # Options dictionary
    N, Diameter, theta_offset, X0, Y0, digits = GetParameters(d)
    #N, Diameter, theta_offset, X0, Y0, digits = 17,10,8.33,0,0,4
    sig.digits = digits
    dia = sig(Diameter)
    r = sig(Diameter/2)
    ang = sig(theta_offset)
    x0 = sig(X0)
    y0 = sig(Y0)
    nh = "Number of holes"
    bc = "Bolt circle diameter"
    ao = "Angle offset"
    org = "Origin"
    w = 25
    out('''
Bolt circle placement
---------------------
  {nh:{w}} {N}
  {bc:{w}} {dia}   radius = {r}
  {ao:{w}} {ang} deg
  {org:{w}} {x0}, {y0}
'''.format(**locals()))
    r = Diameter/2
    w = 15
    eps = 1e-14
    sig.fit = w
    sig.dp_position = w//2
    X, Y, T = "x", "y", "theta, deg"
    out("Hole {X:^{w}} {Y:^{w}} {T:^{w}}".format(**locals()))
    X = "-"*(w - 4)
    out("---- {X:^{w}} {X:^{w}} {X:^{w}}".format(**locals()))
    r2d = 180/pi
    for i in range(N):
        hn = i + 1
        theta = 2*pi/N*i + theta_offset*pi/180
        X, Y = r*cos(theta) + X0, r*sin(theta) + Y0
        x = "{0:^{1}}".format(0, w) if abs(X) < eps else sig(X)
        y = "{0:^{1}}".format(0, w) if abs(Y) < eps else sig(Y)
        t = "{0:^{1}}".format(0, w) if abs(theta) < eps else sig(theta*r2d)
        out("{hn:4} {x:^{w}} {y:^{w}} {t:^{w}}".format(**locals()))

