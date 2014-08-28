'''
Root Finding Routines (should work with python 2 or 3)

The following functions find real roots of functions.  Note you can
call them using e.g. mpmath numbers and find roots to arbitrary
precision.  The functions QuadraticEquation, CubicEquation, and
QuarticEquation use functions from the math and cmath library, so they
can't be used with other floating point implementations.

Note that the fp keyword arguments let you perform these root-finding
calculations with any floating point type that can convert strings
like "1.5" to a floating point number.  Python's float type is the
default.

The following calls may be abbreviated; see the actual function
definitions for details.  

Bisection(f, x1, x2, tol=1.0e-9, switch=False)
    Finds a root by bisection.  Slow but reliable if the root is
    bracketed in [x1, x2].

Brent(f, x1, x2, tol=1e-6, maxit=100)
    Brent's method.  The root must be in [x1, x2].  

FindRoots(f, n, x1, x2, eps=epsilon, itmax=100)
    This is a general-purpose root finding routine.  It uses 
    SearchIntervalForRoots to divide the interval [x1, x2] into n
    intervals and look for roots in each subinterval.  If a subinterval has
    a root, the RootFinder routine is used to find the root to precision
    eps.  If more than itmax iterations are done in any interval, an
    exception is raised.  Returns a tuple of the roots found. 

Pound(x, adjust, eps=float(epsilon))
    Utility function to reduce complex numbers with small real or
    imaginary components to pure imaginary or pure real numbers,
    respectively.

Ridders(f, a, b, tol=1.0e-9, itmax=100)
    Finds a root via Ridder's method if the root is bracketed.
    Converges quadratically with two function evaluations per
    iteration.

RootFinder(x0, x2, f, eps=epsilon, itmax=100)
    Finds a root with quadratic convergence that lies between x0 and
    x2.  x0 and x2 must bracket the root.  The function whose root is
    being found is f(x).  The root is found when successive estimates
    differ by less than eps.  The routine will throw an exception if
    the number of iterations exceeds itmax.  The returned value is the
    root.  Based on a C algorithm by Jack Crenshaw.

NewtonRaphson(f, fd, x, tolerance=1e-9, maxit=200, show=False)
    Quadratically-converging root-finding method; you need to supply the
    function f, its derivative fd, and an initial guess x.

SearchIntervalForRoots(f, n, x1, x2)
    Given a function f of one variable, divide the interval [x1, x2]
    into n subintervals and determine if the function crosses the x
    axis in each subinterval.  Return a tuple of the intervals where
    there is a zero crossing (i.e., there's at least one root in each
    intervale in the tuple).

The following functions find real and complex roots and use the math
library, so are only for calculations with floats.  If adjust is True,
any root where Im/Re < epsilon is converted to a real root.  epsilon is a
global variable.  Set adjust to False, to have the roots returned as
complex numbers.

QuadraticEquation(a, b, c, adjust=True)
    Returns the two roots of a*x^2 + b*x + c = 0.  If adjust is true,
    any root where Im/Re < eps is converted to a real root.  Set 
    adjust to zero to have all roots returned as complex numbers.

CubicEquation(a, b, c, d, adjust=True)
    Returns the three roots of a*x^3 + b*x^2 + c*x + d = 0.  If adjust
    is true, any root where Im/Re < eps is converted to a real root.
    Set adjust to zero to have all roots returned as complex numbers.

QuarticEquation(a, b, c, d, e, adjust=True)
    Returns the four roots of a*x^4 + b*x^3 + c*x^2 + d*x + e = 0.
    If adjust is true, any root where Im/Re < eps is converted to a
    real root.  Set adjust to zero to have all roots returned as
    complex numbers.
'''

# Copyright (c) 2006, 2010 Don Peterson
# Contact:  gmail.com@someonesdad1

#
#

from __future__ import division, print_function
import sys, math, cmath, unittest, numbers

class TooManyIterations(Exception): pass

# Ratio of imag/real to decide when something is a real root (or
# real/imag to decide when something is pure imaginary).  Also used as
# the default tolerance for root finding.  Note it's a string because
# it will be converted to a floating point type inside the function
# it's used in (some of the functions can allow other numerical types
# besides floating point).
epsilon = "2.5e-15"

def FindRoots(f, n, x1, x2, eps=epsilon, itmax=100, fp=float, args=[], kw={}):
    '''This is a general-purpose root finding routine that returns a
    tuple of the roots found of the function f on the interval 
    [x1, x2].
    
    It uses SearchIntervalForRoots to divide the interval into n
    intervals and look for roots in each subinterval.  If a
    subinterval has a root, the RootFinder routine is used to find the
    root to precision eps.  If more than itmax iterations are used in
    any interval, an exception is raised.  
 
    Parameters
        f       Function to search for roots
        n       Number of subintervals
        x1      Start of overall interval to search
        x2      End of overall interval to search
        eps     Precision to find roots
        itmax   Maximum number of iterations
        fp      Floating point type to use for calculations
        args    Extra parameters for f()
        kw      Extra keyword arguments for f()
    
    Example:  Find the roots of sin(x)/x = 0 on the interval [1, 10]:
        import math
        for i in FindRoots(lambda x: math.sin(x)/x, 1000, 1, 10):
            print(i)
    which prints
        3.14159265359
        6.28318530718
        9.42477796077
    Note these are integer multiples of pi.
    '''
    if not f:
        raise ValueError("f must be defined")
    if not isinstance(n, numbers.Integral):
        raise TypeError("n must be integer")
    if x1 >= x2:
        raise ValueError("Must have x1 < x2")
    intervals = SearchIntervalForRoots(f, n, x1, x2, fp=fp, args=args, kw=kw)
    if not intervals:
        return tuple()
    roots = []
    for x1, x2 in intervals:
        try:
            x, numits = RootFinder(x1, x2, f, eps=eps, itmax=itmax, 
                                   args=args, kw=kw)
        except TooManyIterations:
            pass
        else:
            roots.append(x)
    return tuple(roots)

def RootFinder(x0, x2, f, eps=epsilon, itmax=100, fp=float, args=[], kw={}):
    '''Root lies between x0 and x2.  f is the function to evaluate; it
    takes one parameter and returns a number.  eps is the precision to find
    the root to and itmax is the maximum number of iterations allowed.
    fp is the number type to use in the calculation.  args is a
    sequence of any extra arguments that need to be passed to f; kw is
    a dictionary of keywords that will be passed to f.
 
    Returns a tuple (x, numits) where 
        x is the root.
        numits is the number of iterations taken.
    The routine will throw an exception if it receives bad input
    data or it doesn't converge.
 
    ----------------------------------------------------------------
    A root finding routine.  See "All Problems Are Simple" by Jack
    Crenshaw, Embedded Systems Programming, May, 2002, pg 7-14,
    jcrens@earthlink.com.  Can be downloaded from
    www.embedded.com/code.htm.
 
    Originally translated from Crenshaw's C code and modified by Don
    Peterson 20 May 2003.  
 
    The method is called "inverse parabolic interpolation" and will
    converge rapidly as it's a 4th order algorithm.  The routine works
    by starting with x0, x2, and finding a third x1 by bisection.  The
    ordinates are gotten, then a horizontally-opening parabola is
    fitted to the points.  The abcissa to the parabola's root is
    gotten, and the iteration is repeated.
 
    The root value is returned.
    '''
    zero, half, one, two, eps = fp("0"), fp("0.5"), fp("1"), fp("2"), fp(eps)
    assert x0 < x2 and eps > zero and itmax > 0 
    x1 = y0 = y1 = y2 = b = c = temp = y10 = y20 = y21 = xm = ym = zero
    xmlast = x0
    if args:
        y0, y2 = ((f(x0, *args, **kw), f(x2, *args, **kw)) if kw else
            (f(x0, *args), f(x2, *args)))
    else:
        y0, y2 = (f(x0, **kw), f(x2, **kw)) if kw else (f(x0), f(x2))
    if y0 == zero:
        return x0, 0
    if y2 == zero:
        return x2, 0
    if y2 * y0 > zero:
        raise ValueError("Root not bracketed: y0 = %f, y2 = %f\n"% (y0, y2))
    for i in range(itmax):
        x1 = half*(x2 + x0)
        if args:
            y1 = f(x1, *args, **kw) if kw else f(x1, *args)
        else:
            y1 = f(x1, **kw) if kw else f(x1)
        if (y1 == zero) or (abs(x1 - x0) < eps):
            return x1, i + 1
        if y1*y0 > zero:
            x0, x2, y0, y2 = x2, x0, y2, y0
        y10, y21, y20 = y1 - y0, y2 - y1, y2 - y0
        if y2*y20 < two*y1*y10:
            x2, y2 = x1, y1
        else:
            b, c = (x1 - x0)/y10, (y10 - y21)/(y21 * y20)
            xm = x0 - b*y0*(one - c*y1)
            if args:
                ym = f(xm, *args, **kw) if kw else f(xm, *args)
            else:
                ym = f(xm, **kw) if kw else f(xm)
            if ((ym == zero) or (abs(xm - xmlast) < eps)):
                return xm, i + 1
            xmlast = xm
            if ym*y0 < zero:
                x2, y2 = xm, ym
            else:
                x0, y0, x2, y2 = xm, ym, x1, y1
    raise TooManyIterations("No convergence in RootFinder()")

def NewtonRaphson(f, fd, x, tolerance=1e-9, maxit=200, show=False,
                  fp=float, args=[], kw={}): 
    '''Newton-Raphson algorithm for solving f(x) = 0.
        f         = the function (must be a function object)
        fd        = the function's derivative (must be a function object)
        x         = initial guess of the root's location
        tolerance = number used to determine when to quit
        maxit     = the maximum number of iterations.
        fp        = type of numbers to calculate with
        args      = extra arguments for f
        kw        = keyword arguments for f
        show      = print intermediate values
 
    The iteration is
 
        xnew = x - f(x)/f'(x) 
 
    until 
 
        |dx|/(1+|x|) < tolerance 
 
    is achieved.  Here, dx = f(x)/fd(x).  This termination condition
    is a compromise between |dx| < tolerance, if x is small and 
    |dx|/|x| < tolerance, if x is large.
 
    Newton-Raphson converges quadratically near the root; however, its
    downfalls are well-known:  i) near zero derivatives can send it into
    the next county; ii) ogive-shaped curves can make it oscillate and not
    converge; iii) you need to have an expression for both the function and
    its derivative.
 
    Adapted from
    http://www.phys.uu.nl/~haque/computing/WPark_recipes_in_python.html
    '''
    count, one = 0, fp("1.")
    while True: 
        if args:
            dx = f(x, *args, **kw)/fd(x) if kw else f(x, *args)/fd(x) 
        else:
            dx = f(x, **kw)/fd(x) if kw else f(x)/fd(x) 
        if abs(dx) < tolerance * (one + abs(x)): 
            return x - dx 
        x = x - dx 
        count += 1 
        if count > maxit:
            raise TooManyIterations("Too many iterations in NewtonRaphson()")
        if show:
            print("NewtonRaphson[%d]: x = %s" % (count, x))

def BracketRoots(f, x1, x2, maxit=100, fp=float, args=[], kw={}):
    '''Given a function f and an initial interval [x1, x2], expand the
    interval geometrically until a root is bracketed or the number of
    iterations exceeds maxit.  Return (x3, x4), where the interval
    definitely brackets a root.  If the maximum number of iterations
    is exceeded, an exception is raised.  
    
    fp      Floating point type to use
    args    Sequence of extra arguments to be passed to f
    kw      Dictionary of keywords that will be passed to f
  
    Adapted from zbrac in chapter 9 of Numerical Recipes in C, page 352.
    '''
    assert f and x1 != x2
    zero = fp("0")
    if x1 > x2:
        x1, x2 = x2, x1
    if args:
        f1, f2 = ((f(x1, *args, **kw), f(x2, *args, **kw)) if kw else
                  (f(x1, *args), f(x2, *args)))
    else:
        f1, f2 = (f(x1, **kw), f(x2, **kw)) if kw else (f(x1), f(x2))
    factor, count = fp("1.6"), 0
    while True:
        if f1*f2 < zero:
            return (x1, x2)
        if abs(f1) < abs(f2):
            x1 += factor*(x1 - x2)
            if args:
                f1 = f(x1, *args, **kw) if kw else f(x1, *args)
            else:
                f1 = f(x1, **kw) if kw else f(x1)
        else:
            x2 += factor*(x2 - x1)
            if args:
                f2 = f(x2, *args, **kw) if kw else f(x2, *args)
            else:
                f2 = f(x2, **kw) if kw else f(x2)
        count += 1
        if count > maxit:
            raise TooManyIterations("No convergence in BracketRoots()")

def SearchIntervalForRoots(f, n, x1, x2, fp=float, args=[], kw={}):
    '''Given a function f of one variable, divide the interval [x1,
    x2] into n subintervals and determine if the function crosses the
    x axis in each subinterval.  Return a tuple of the intervals where
    there is a zero crossing.  fp is the floating point type to use.
    args is a sequency of any extra parameters needed by f; kw is a
    dictionary of any keyword parameters needed by f.
 
    Idea from Numerical Recipes in C, zbrak, chapter 9, page 352.
    '''
    assert f and n > 0 and x1 < x2 
    if args:
        y0 = f(x1, *args, **kw) if kw else f(x1, *args)
    else:
        y0 = f(x1, **kw) if kw else f(x1)
    x0, delta, intervals = x1, (x2 - x1)/(n + fp("1.")), []
    for i in range(1, n + 1):
        x = x1 + i*delta
        if args:
            y = f(x, *args, **kw) if kw else f(x, *args)
        else:
            y = f(x, **kw) if kw else f(x)
        if y0*y < 0:
            intervals.append((x0, x))
        x0, y0 = x, y
    return tuple(intervals)

# For the following Bisection and Ridders methods, note these
# algorithms are in scipy DLLs, so they are probably implemented in
# C/C++ and will be faster.

def Bisection(f, x1, x2, tol=1.0e-9, switch=False):
    '''Returns (root, num_it) (the root and number of iterations) by
    finding a root of f(x) = 0 by bisection.  The root must be
    bracketed in [x1,x2].  The iteration is done when the root is
    found to less than the indicated relative tolerance tol.
 
    If switch is true, an exception will be raised if the function
    appears to be increasing during bisection.  Be careful with this,
    as the polynomial test case converges just fine with bisection,
    but will cause an exception if switch is True.
 
    If the root is bracketed, bisection is guaranteed to converge,
    either on some root in the interval or a singularity within the
    interval.  It's also conceptually simple to understand:  draw a
    line between the two bracketing points and look at the midpoint.
    Choose the new interval containing the midpoint and the other
    point that evaluates to the opposite sign.  Repeat until you find
    the root to the required accuracy.  Each iteration adds a
    significant digit to the answer.
 
    The number of iterations and function evaluations will be
    log2(abs(x2 - x1)/tol).
 
    Adapted slightly from the book "Numerical Methods in Engineering
    with Python" by Jaan Kiusalaas, 2nd ed.  You can get the book's
    algorithms from http://www.cambridge.org/us/download_file/202203/.
    '''    
    f1, f2 = f(x1), f(x2)
    if not f1:
        return x1, 0
    if not f2:
        return x2, 0
    if f1*f2 > 0.0: 
        raise ValueError("Root is not bracketed")
    # Get the number of iterations we'll need
    num_iterations = int(math.ceil(math.log(abs(x2 - x1)/tol)/math.log(2)))
    for i in range(num_iterations):
        x3 = 0.5*(x1 + x2)  # Abscissa of interval midpoint
        f3 = f(x3)          # Ordinate of interval midpoint
        if f3 == 0.0: 
            return x3, i + 1
        if switch and abs(f3) > abs(f1) and abs(f3) > abs(f2):
            msg = "f(x) increasing on interval bisection (i.e., a singularity)"
            raise ValueError(msg)
        # Choose which half-interval to use based on which one continues to
        # bracket the root.
        if f2*f3 < 0.0: 
            x1, f1 = x3, f3  # Right half-interval contains the root
        else:
            x2, f2 = x3, f3  # Left half-interval contains the root
    return (x1 + x2)/2.0, num_iterations

def Ridders(f, a, b, tol=1.0e-9, itmax=100):
    '''Returns (root, num_it) (root and the number of iterations)
    using Ridders' method to find a root of f(x) = 0 to the specified
    relative tolerance tol.  The root must be bracketed in [a,b].  If
    the number of iterations exceeds itmax, an exception will be
    raised.
 
    Wikipedia states:  Ridders' method is a root-finding algorithm
    based on the false position method and the use of an exponential
    function to successively approximate a root of a function f.
 
    Ridders' method is simpler than Brent's method but Press et al.
    (1988) claim that it usually performs about as well. It converges
    quadratically, which implies that the number of additional
    significant digits doubles at each step; but the function has to
    be evaluated twice for each step so the order of the method is
    2**(1/2). The method is due to Ridders (1979).
 
    Adapted slightly from the book "Numerical Methods in Engineering
    with Python" by Jaan Kiusalaas, 2nd ed.  You can get the book's
    algorithms from http://www.cambridge.org/us/download_file/202203/.
    '''
    fa, fb = f(a), f(b)
    if fa == 0.0: 
        return a, 0
    if fb == 0.0:
        return b, 0
    if fa*fb > 0.0:
        raise ValueError("Root is not bracketed")
    for i in range(itmax):
        # Compute the improved root x from Ridder's formula
        c = 0.5*(a + b)
        fc = f(c)
        s = math.sqrt(fc**2 - fa*fb)
        if s == 0.0: 
            if not fc:
                return c, i + 1
            raise ValueError("No root")
        dx = (c - a)*fc/s
        if (fa - fb) < 0.0:
            dx = -dx
        x = c + dx
        fx = f(x)
        # Test for convergence
        if i > 0 and abs(x - x_old) < tol*max(abs(x), 1.0):
            return x, i + 1
        x_old = x
        # Re-bracket the root as tightly as possible
        if fc*fx > 0.0:
            if fa*fx < 0.0: 
                b, fb = x, fx
            else:
                a, fa = x, fx
        else:
            a, b, fa, fb = c, x, fc, fx
    raise TooManyIterations("Too many iterations in Ridders()")

def Pound(x, adjust, eps=float(epsilon)):
    '''Turn x into a real if the imaginary part is small enough
    relative to the real part and adjust is True.  The analogous thing
    is done for a nearly pure imaginary number.  
 
    This function's name was orginally IfReal, but I enlarged its
    abilities to handle complex numbers whose direction was nearly
    parallel to either the real or imaginary axis.  The name comes
    from imagining the complex number is a nail which a light tap from
    a hammer makes it lie parallel to the axis.
    '''
    # Handle the "pure" cases first.
    if not x.real and not x.imag:
        return 0
    elif x.real and not x.imag:
        return x.real
    elif not x.real and x.imag:
        return x.imag*1j
    if adjust and x.real and abs(x.imag/x.real) < eps:
        return x.real
    elif adjust and x.imag and abs(x.real/x.imag) < eps:
        return x.imag*1j
    return x

def QuadraticEquation(a, b, c, adjust=True, force_real=False):
    '''Return the two roots of a quadratic equation.  Equation is
    a*x^2 + b*x + c = 0.  Note this works with float types only.
    Set force_real to True to force the returned values to be real.
 
    Here's a derivation of the method used.  Multiply by 4*a and
    complete the square to get
 
        (2*a*x + b)**2 = (b**2 - 4*a*c)
        x = (-b +/- sqrt(b**2 - 4*a*c))/(2*a)           (1)
 
    Next, multiply the equation by 1/x**2 to get
 
        a + b*(1/x) + c*(1/x**2) = 0
 
    Complete the square to find
 
        1/x = (-b -/+ sqrt(b**2 - 4*a*c))/(2*c)
 
    or 
        
        x = 2*c/(-b -/+ sqrt(b**2 - 4*a*c))             (2)
 
    Equations 1 or 2 may provide more accuracy for a particular root.
    Note there can be loss of precision in the discriminant when a*c
    is small compared to b**2.  This happens when the roots vary
    greatly in absolute magnitude.  Suppose they are x1 and x2; then 
    (x - x1)*(x - x2) = x**2 - (x1 + x2)*x + x1*x2 = 0.  Here,
 
        a = 1
        b = -(x1 + x2)
        c = x1*x2
 
    Suppose x1 = 1000 and x2 = 0.001.  Then b = -1000.001 and c = 1.
    The square root of the discriminant is 999.999 and the subtraction
    b - sqrt(D) results in 0.0001, with a loss of around 6 significant
    figures.
 
    The algorithm is to use two equations depending on the sign of b
    (D = b**2 - 4*a*c):
 
    b >= 0:
        x1 = -b - sqrt(D))/(2*a)    and     x2 = 2*c/(-b - sqrt(D))
    b < 0:
        x1 = 2*c/(-b + sqrt(D))     and     x2 = -b + sqrt(D))/(2*a)
 
    '''
    if not a:
        raise ValueError("a cannot be zero")
    if isinstance(b, numbers.Complex):
        p = b/a
        q = c/a
        d = cmath.sqrt(p*p/4 - q)
        if force_real:
            return tuple([i.real for i in (-p/2 + d, -p/2 - d)])
        return Pound(-p/2 + d, adjust), Pound(-p/2 - d, adjust)
    else:
        # More stable numerical method
        D = cmath.sqrt(b*b - 4*a*c)
        if b >= 0:
            x1, x2 = (-b - D)/(2*a), 2*c/(-b - D)
        else:
            x1, x2 = 2*c/(-b + D), (-b + D)/(2*a)
        if force_real:
            return tuple([i.real for i in (x1, x2)])
        return Pound(x1, adjust), Pound(x2, adjust)

# The following Mathematica commands were used to generate the code for
# the cubic and quartic routines.  
#
# (* Cubic *)
#   f = a*x^3 + b*x^2 + c*x + d;
#   g = Solve[f == 0, x];
#   FortranForm[g]
# 
# (* Quartic *)
#   f = a*x^4 + b*x^3 + c*x^2 + d*x + e;
#   g = Solve[f == 0, x];
#   FortranForm[g]
#
# The output was edited with the following changes:
#
#   1. Change (0,1) to 1j
#   2. Remove extra parentheses and comma at end of expression
#   3. Substitute (1/3.) for 0.3333333333333333
#   4. Substitute (2/3.) for 0.6666666666666666
#   5. Put backslashes on lines as appropriate
#
# After this manipulation, common terms were looked for and set up as
# single variables to avoid recalculation.  This removed a lot of
# duplication.
#
# The special case where we're finding the third or fourth root of a
# real or complex number, we use De Moivre's theorem:  Let z be a
# complex number written in polar form z = r*(cos(x) + i*sin(x)).
# Then
#
#   z^(1/n) = r^(1/n)*(cos((x + 2*k*pi)/n) + i*sin((x + 2*k*pi)/n))
#
# where k varies from 0 to n-1 to give the n roots of z.

def CubicEquation(a, b, c, d, adjust=True, force_real=False):
    '''Returns the roots of a cubic with complex coefficients: a*z**3
    + b*z**2 + c*z + d.  
 
    You can set force_real to True to make all the returned roots be
    real (this causes the real part of the calculated roots to be
    returned).  This may be of use e.g. when solving cubic equations
    of state like the Peng-Robinson or Redlich-Kwong equations.  You
    must exercise caution, as you might be throwing a true complex
    root away.
 
    If adjust is True and the roots have imaginary parts small enough
    relative to the real part, they are converted to real numbers.
 
    Example:
        for i in CubicEquation(1, 1, 1, 1):
            print(i)
    prints
        -1.0
        (-6.93889390391e-17+1j)
        (-6.93889390391e-17-1j)
    However,
        for i in CubicEquation(1, 1, 1, 1, adjust=True):
            print(i)
    prints
        -1.0
        1j
        -1j
    Note
        for i in CubicEquation(1, 1, 1, 1, force_real=True):
            print(i)
    prints
        -1.0
        -6.93889390391e-17
        -6.93889390391e-17
    which is probably *not* what you want.
    '''
    if not a:
        raise ValueError("a must not be zero")
    if b == 0 and c == 0 and d == 0:
        return 0, 0, 0
    if b == 0 and c == 0:
        # Find the three cube roots of (-d) using De Moivre's theorem.
        r = abs(-d)  # Magnitude
        # Get the argument
        if isinstance(-d, numbers.Complex):
            x = math.atan2((-d).imag, (-d).real)
        else:
            x = 0
            if (-d) < 0:
                x = math.pi
        n = 3
        rn = r**(1./n)
        def f(x, k):
            return (rn*(math.cos((x + 2*k*math.pi)/n) + 
                    1j*math.sin((x + 2*k*math.pi)/n)))
        roots = f(x, 0), f(x, 1), f(x, 2)
        if force_real:
            return tuple(i.real for i in roots)
        return tuple(Pound(i, adjust) for i in roots)
    u = -2*b**3 + 9*a*b*c - 27*a**2*d
    D = -b**2 + 3*a*c
    v = cmath.sqrt(4*D**3 + u**2)
    w = 2**(1./3)
    y = (u + v)**(1./3)
    st = 1j*math.sqrt(3)
    z = -b/(3.*a)
    t = 3*2**(2./3)*a*y
    x = 6*w*a
    x1 = z - w*D/(3.*a*y) + y/(3.*w*a)
    x2 = z + ((1 + st)*D)/t - ((1 - st)*y)/x
    x3 = z + ((1 - st)*D)/t - ((1 + st)*y)/x
    if force_real:
        return tuple(i.real for i in (x1, x2, x3))
    return tuple(Pound(i, adjust) for i in (x1, x2, x3))

def QuarticEquation(a, b, c, d, e, adjust=True, force_real=False):
    '''Returns the roots of a quartic with complex coefficients:
    a*x**4 + b*x**3 + c*x**2 + d*x + e.  Note this works with float
    types only.  Set force_real to make all the returned roots be
    real.
 
    You can set force_real to True to make all the returned roots be
    real (this causes the real part of the calculated roots to be
    returned).  You must exercise caution, as you might be throwing a
    true complex root away.
 
    If adjust is True and a root has an imaginary part small enough
    relative to the real part, it is converted to a real number.
    Analogously, if the real parts are small enough relative to the
    imaginary parts, the root is converted to a pure imaginary.
 
    Example 1:
        for i in QuarticEquation(1, 1, 1, 1, 1):
            print(i)
    prints
        (-0.809016994375-0.587785252292j)
        (-0.809016994375+0.587785252292j)
        (0.309016994375-0.951056516295j)
        (0.309016994375+0.951056516295j)
 
    Example 2:  (x-1)*(x-2)*(x-3)*(x-4) is a quartic polynomial with 
    a = 1, b = -10, c = 35, d = -50, and e = 24.  Then
        for i in QuarticEquation(1, -10, 35, -50, 24):
            print(i)
    prints
    '''
    if not a:
        raise ValueError("a must not be zero")
    if b == 0 and c == 0 and d == 0 and e == 0:
        return 0, 0, 0, 0
    if b == 0 and c == 0 and d == 0:
        # Find the four fourth roots of (-e) using De Moivre's theorem.
        r = abs(-e)  # Magnitude
        # Get the argument
        if isinstance(-e, numbers.Complex):
            x = math.atan2((-e).imag, (-e).real)
        else:
            x = 0
            if (-e) < 0:
                x = math.pi
        n = 4
        rn = r**(1./n)
        def f(x, k):
            return (rn*(math.cos((x + 2*k*math.pi)/n) + 
                    1j*math.sin((x + 2*k*math.pi)/n)))
        roots = f(x, 0), f(x, 1), f(x, 2), f(x, 3)
        if force_real:
            return tuple([i.real for i in roots])
        return tuple([Pound(i, adjust) for i in roots])
    cr3 = 2**(1./3)
    p = -b/(4.*a)
    q = (c**2 - 3*b*d + 12*a*e)
    r = 2*c**3 - 9*b*c*d + 27*a*d**2 + 27*b**2*e - 72*a*c*e
    s = cmath.sqrt(-4*q**3 + r**2)
    t = (3*a*(r + s)**(1./3))
    u = (r + s)**(1./3)/(3.*cr3*a)
    v = (-(b**3./a**3) + (4.*b*c)/a**2 - (8.*d)/a)
    w = cmath.sqrt(b**2/(4.*a**2) - (2*c)/(3.*a) + (cr3*q)/t + u)
    x = b**2/(2.*a**2) - (4*c)/(3.*a) - (cr3*q)/t - u
    y = cmath.sqrt(x - v/(4.*w))/2
    z = cmath.sqrt(x + v/(4.*w))/2
    roots = p - w/2. - y, p - w/2. + y, p + w/2. - z, p + w/2. + z
    if force_real:
        return tuple([i.real for i in roots])
    return tuple(Pound(i, adjust) for i in roots)

def Brent(f, x1, x2, args=[], kw={}, tol=1e-6, maxit=100):
    '''Return (r, numits) where r is the root of the function f that
    is known to lie in the interval [x1, x2].  The root will be found
    within the absolute tolerance tol.  numits is the number of
    iterations it took.
 
    args is a sequence of extra arguments for f(); kw is a dictionary
    of keyword arguments for f().
 
    The is essentially the zbrent routine from "Numerical Recipes in
    C", translated into python.
    '''
    def F(x):
        if args:
            return f(x, *args, kw=kw) if kw else f(x, *args)
        else:
            return f(x, kw=kw) if kw else f(x)
    a, b, c = x1, x2, x2
    i, EPS = 0, 3.0e-8
    fa, fb = F(a), F(b)
    fc = fb
    if (fa > 0.0 and fb > 0.0) or (fa < 0.0 and fb < 0.0):
        raise ValueError("Root must be bracketed")
    while i < maxit:
        i += 1
        if (fb > 0.0 and fc > 0.0) or (fb < 0.0 and fc < 0.0):
            c, fc = a, fa
            e = d = b - a
        if abs(fc) < abs(fb):
            a = b
            b = c
            c = a
            fa = fb
            fb = fc
            fc = fa
        tol1 = 2.0*EPS*abs(b) + 0.5*tol
        xm = 0.5*(c - b)
        if abs(xm) <= tol1 or fb == 0.0:
            return (b, i) # *** Found the root ***
        if abs(e) >= tol1 and abs(fa) > abs(fb):
            s = fb/fa
            if a == c:
                p, q = 2.0*xm*s, 1.0 - s
            else:
                q, r = fa/fc, fb/fc
                p = s*(2.0*xm*q*(q - r) - (b - a)*(r - 1.0))
                q = (q - 1.0)*(r - 1.0)*(s - 1.0)
            if p > 0.0:
                q = -q
            p = abs(p)
            min1 = 3.0*xm*q - abs(tol1*q)
            min2 = abs(e*q)
            if 2.0*p < (min1 if min1 < min2 else min2):
                e = d
                d = p/q
            else:
                d = xm
                e = d
        else:
            d = xm  # Bounds decreasing too slowly, use bisection.
            e = d
        a, fa = b, fb
        if abs(d) > tol1: # Evaluate new trial root.
            b += d
        else:
            b += tol1 if xm >= 0 else -tol1
        fb = F(b)
    raise ValueError("Maximum number of iterations exceeded")
