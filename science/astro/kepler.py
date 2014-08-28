'''
Functions to calculate a solution to Kepler's equation.  Ref. Meeus
"Astronomical Algorithms", pg 206.  


The equation is E = M + e*sin(E).  E is to be solved for given M and
e.  M will be between 0 and 2pi and e >= 0.

The iterative methods include a third parameter precision, which is
what two successive iterations must be less than for the function to
return.

SolveKepler2 and SolveKepler3 return a tuple (E, n) where E is the 
eccentric anomaly and n is the number of iterations to get the answer.
SolveKepler1 just returns E.
'''

# Copyright (C) 2002 Don Peterson
# Contact:  gmail.com@someonesdad1

#
#

from __future__ import division, print_function
from math import sin, cos, pi

too_many_iterations = 10000
d2r = pi/180
r2d = 1/d2r

def SolveKepler1(m, e, precision):
    '''Use simple iteration to the indicated precision.
    '''
    E0 = m/2
    E  = m
    count = 0
    while abs(E-E0) > precision and count <= too_many_iterations:
        E0 = E
        count = count + 1
        E = m + e*sin(E0)
    if count > too_many_iterations:
        raise ValueError("Too many iterations")
    return (E, count)

def SolveKepler2(m, e, precision):
    '''Use Newton's method to solve for the root.
    '''
    E0 = m/2
    E  = m
    count = 0
    while abs(E-E0) > precision and count <= too_many_iterations:
        E0 = E
        count = count + 1
        E = E0 + (m+e*sin(E0)-E0)/(1-e*cos(E0))
    if count > too_many_iterations:
        raise ValueError("Too many iterations")
    return (E, count)

def SolveKepler3(m, e):
    '''SolveKepler3 uses Sinnot's binary search algorithm.
    '''
    sgn = lambda x: 0 if not x else -1 if x < 0 else 1
    f = sgn(m)
    m = abs(m)/(2*pi)
    m = (m - int(m))*2*pi*f
    if m < 0:
        m = m + 2*pi
    f = 1
    if m > pi: 
        f = -1
        m = 2*pi - m
    e0 = pi/2
    d = pi/4
    for j in xrange(1, 54, 1):
        m1 = e0 - e*sin(e0)
        e0 = e0 + d*sgn(m-m1)
        d = d/2
    return e0*f

def Test(m, e, p):
    print("m = %.1f deg, e = %.2f, p = %.1g" % (m, e, p))
    f = "%3.15f"
    fmt = "Method %d = " + f + " n=%3d"
    try:
        E, n = SolveKepler1(m*pi/180., e, p)
        print(fmt % (1, r2d*E, n))
    except ValueError:
        print("Too many iterations in SolveKepler1")
    try:
        E, n = SolveKepler2(m*pi/180., e, float(p))
        print(fmt % (2, r2d*E, n))
    except ValueError:
        print("Too many iterations in SolveKepler2")
    E = SolveKepler3(m*pi/180., e)
    print(("Method 3 = " + f + "\n") % (r2d*E))

if __name__ == "__main__":
    p = 1e-15
    Test(90, 1/2, p)
    Test(80, 1/3, p)
    Test(40, 1/8, p)
