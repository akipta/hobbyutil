from __future__ import division, print_function
import cmath
import math
import numbers
from root import (BracketRoots, Brent, CubicEquation, FindRoots,
                  Bisection, Ridders, NewtonRaphson, epsilon,
                  QuarticEquation, RootFinder, TooManyIterations,
                  Pound, QuadraticEquation, SearchIntervalForRoots)
from lwtest import run, assert_equal, assert_raises

eps = 2e-15    # For testing float equality

def testQuadratic():
    # Exception if not quadratic
    assert_raises(ValueError, QuadraticEquation, *(0, 1, 1))
    # Real roots
    r1, r2 = QuadraticEquation(1, 0, -2)
    assert_equal(r1, -r2)
    assert_equal(abs(r1), math.sqrt(2))
    # Complex roots
    r1, r2 = QuadraticEquation(1, 0, 2)
    assert_equal(r1, -r2)
    assert_equal(r1, cmath.sqrt(-2))
    # Constant term 0
    r1, r2 = QuadraticEquation(1, -1, 0)
    assert_equal(r1, 1)
    assert_equal(r2, 0j)
    # Real, distinct
    r1, r2 = QuadraticEquation(1, 4, -21)
    assert(r1 == 3)
    assert(r2 == -7)
    # Real coefficients, complex roots
    r1, r2 = QuadraticEquation(1, -4, 5)
    assert_equal(r1, 2 + 1j)
    assert_equal(r2, 2 - 1j)
    # Complex coefficients, complex roots
    r1, r2 = QuadraticEquation(1, 3 - 3j, 10 - 54j)
    assert_equal(r1, (3 + 7j))
    assert_equal(r2, (-6 - 4j))

def testCubic():
    # Exception if not cubic
    assert_raises(ValueError, CubicEquation, *(0, 1, 1, 1))
    # Basic equation
    r = CubicEquation(1, 0, 0, 0)
    assert(r == (0, 0, 0))
    # Cube roots of 1
    for r in CubicEquation(1, 0, 0, -1):
        assert_equal(Pound(r**3, eps=eps), 1)
    # Cube roots of -1
    for r in CubicEquation(1, 0, 0, 1):
        assert_equal(r**3, -1)
    # Three real roots:  (x-1)*(x-2)*(x-3)
    for i, j in zip(CubicEquation(1, -6, 11, -6), (3, 1, 2)):
        assert_equal(i, j)
    # One real root:  (x-1)*(x-j)*(x+j)
    for i, j in zip(CubicEquation(1, -1, 1, -1), (1, 1j, -1j)):
        assert_equal(i, j)

def testQuartic():
    # Exception if not cubic
    assert_raises(ValueError, QuarticEquation, *(0, 1, 1, 1, 1))
    # Basic equation
    r = QuarticEquation(1, 0, 0, 0, 0)
    assert(r == (0, 0, 0, 0))
    # Fourth roots of 1
    for r in QuarticEquation(1, 0, 0, 0, -1):
        assert_equal(r**4, 1)
    # Fourth roots of -1
    for r in QuarticEquation(1, 0, 0, 0, 1):
        assert_equal(Pound(r**4, eps=eps), -1)
    # The equation (x-1)*(x-2)*(x-3)*(x-4)
    for i,j in zip(QuarticEquation(1, -10, 35, -50, 24), range(1, 5)):
        assert_equal(i, j)
    # Two real roots: x*(x-1)*(x-j)*(x+j)
    for i, j in zip(QuarticEquation(1, -1, 1, -1, 0), (-1j, 1j, 0j, 1)):
        assert_equal(i, j)

def testRootFinder():
    '''Here's a quick test of the routine.  The function is
    the polynomial x^8 - 2 = 0; we should get as an answer the
    8th root of 2.  You should see the following output if
    show is nonzero:
 
    Calculated root = 1.090507732665258
    Correct value   = 1.090507732665258
    Num iterations  = 9
 
    Calculated root = 1.090507732665257659207010655760707978993
    Correct value   = 1.090507732665258
    Num iterations  = 14
 
    The long answer can be checked with integer arithmetic.
    '''
    def f(x):
        return x**8 - 2
    eps = 1e-10
    itmax = 20
    x0 = 0.0
    x1 = 10.0
    root, numits = RootFinder(x0, x1, f, eps=eps, itmax=itmax)
    assert_equal(root, 1.090507732665258, eps=eps)
    # Now do the same, but with Decimal numbers
    import decimal 
    decimal.getcontext().prec = 50
    eps = decimal.Decimal("1e-48")
    x0, x1 = decimal.Decimal(0), decimal.Decimal(10)
    root, numits = RootFinder(x0, x1, f, eps=eps, itmax=itmax,
                              fp=decimal.Decimal)
    assert_equal(root**8, 2)
    # Call a function that uses extra arguments
    def f(x, a, **kw):
        b = kw.setdefault("b", 8)
        return x**b - a
    eps = 1e-10
    itmax = 20
    x0 = 0.0
    x1 = 10.0
    a, b = 2, 8
    root, numits = RootFinder(x0, x1, f, eps=eps, itmax=itmax, args=[a])
    assert_equal(root, math.pow(a, 1/b))
    # Use keyword argument
    a, b = 3, 7
    root, numits = RootFinder(x0, x1, f, eps=eps, itmax=itmax,
            args=[a], kw={"b":b})
    assert_equal(root, math.pow(a, 1/b))

def testFindRoots():
    # Show that FindRoots can do a reasonable job for a
    # polynomial.  Note the particular results are sensitive to
    # n.
    f = lambda x: (x-1)*(x-2)*(x-3)*(x-4)*(x-5)
    x1, x2, n = 0, 10, 10
    r = FindRoots(f, n, x1, x2, eps=eps)
    assert(r == tuple([1.0*i for i in range(1, 6)]))
    # Roots of sinc function
    f = lambda x: math.sin(x)/x
    x1, x2, n = 1, 10, 100
    r = FindRoots(f, n, x1, x2, eps=eps)
    assert_equal(r[0], 1*math.pi)
    assert_equal(r[1], 2*math.pi)
    assert_equal(r[2], 3*math.pi)
    # Same as previous, but with an extra parameter
    f = lambda x, a: math.sin(a*x)/(a*x)
    r = FindRoots(f, n, x1, x2, args=[1], eps=eps)
    assert_equal(r[0], 1*math.pi)
    assert_equal(r[1], 2*math.pi)
    assert_equal(r[2], 3*math.pi)
    r = FindRoots(f, n, x1, x2, args=[math.pi], eps=eps)
    assert_equal(r[0], 1)
    assert_equal(r[1], 2)
    assert_equal(r[2], 3)
    # Same as previous, but with a keyword parameter
    def f(x, a=1):
        return math.sin(a*x)/(a*x)
    r = FindRoots(f, n, x1, x2, kw={"a":1}, eps=eps)
    assert_equal(r[0], 1*math.pi)
    assert_equal(r[1], 2*math.pi)
    assert_equal(r[2], 3*math.pi)
    r = FindRoots(f, n, x1, x2, kw={"a":math.pi}, eps=eps)
    assert_equal(r[0], 1)
    assert_equal(r[1], 2)
    assert_equal(r[2], 3)

def testPound():
    # No adjustment
    a = 1 + 1j
    x = a
    x = Pound(x, True)
    assert(x == a)
    # Adjustment for positive imaginary part
    a = 1 + 1e-16j
    x = a
    x = Pound(x, True)
    assert(x != a)
    assert(isinstance(x, numbers.Real))
    # Adjustment for negative imaginary part
    a = 1 - 1e-16j
    x = a
    x = Pound(x, True)
    assert(x != a)
    assert(isinstance(x, numbers.Real))
    # Adjustment for zero imaginary part
    a = 1 + 0j
    x = a
    x = Pound(x, True)
    assert(x == a)
    assert(isinstance(x, numbers.Real))

def testNewtonRaphson():
    # Find the root of f(x) = tan(x) - 1 for 0 < x < pi/2.
    f = lambda x: math.tan(x) - 1
    fd = lambda x: 1/math.cos(x)**2
    x = NewtonRaphson(f, fd, 0.5, tolerance=eps)
    assert_equal(x, math.atan(1))

def testSearchIntervalForRoots():
    # Find an interval containing the root of f(x) = tan(x) -
    # 1 for 0 < x < pi/2.
    f = lambda x: math.tan(x) - 1
    answer = math.atan(1)
    x1, x2 = 0, math.pi/2
    intervals = SearchIntervalForRoots(f, 10, x1, x2)
    for start, end in intervals:
        assert(start <= answer <= end)
    intervals = SearchIntervalForRoots(f, 1000, x1, x2)
    for start, end in intervals:
        assert(start <= answer <= end)

def testBracketRoots():
    '''The polynomial p(x) = (x-1)*(x-10)*(x+10) has
    three roots.  Thus f(x) = exp(p(x)) - 1 will be zero when
    p(x) is zero.  Use BracketRoots() to find the x = 1 root.
    Also demonstrate that it will exceed the iteration limit
    if the interval doesn't include any of the roots.
    '''
    r1, r2, r3  = 1000, -500, 500
    f = lambda x: (x - r1)*(x - r2)*(x + r3)
    r = BracketRoots(f, -2, -1)
    assert((r[0] <= r1 <= r[1]) or
                    (r[0] <= r2 <= r[1]) or
                    (r[0] <= r3 <= r[1]))
    # Demonstate iteration limit can be reached
    f = lambda x: x - 1000000
    assert_raises(TooManyIterations, BracketRoots, f, -2, -1, maxit=10)

def testPound():
    eps = 0.99*float(epsilon)
    # Zero
    assert(Pound(0, 0) == 0)
    assert(Pound(0j, 1) == 0)
    assert(Pound(0+0j, 1) == 0)
    # Pure real
    assert(Pound(1, 0) == 1)
    assert(Pound(1, 1) == 1)
    assert(Pound(1 + eps, 1) == 1 + eps)
    # Pure imaginary
    assert(Pound(1j, 0) == 1j)
    assert(Pound(1j, 1) == 1j)
    x = (1 + eps)*1j
    assert(Pound(x, 1) == x)
    # Real with small imaginary part
    x = 1
    y = x + eps*1j
    assert(Pound(y, 0) == y)
    assert(Pound(y, 1) == x)
    # Imaginary with small real part
    y = eps + x*1j
    assert(Pound(y, 0) == y)
    assert(Pound(y, 1) == x*1j)
    # Number that shouldn't be changed
    x = 1 + 1j
    assert(Pound(x, 0) == x)
    assert(Pound(x, 1) == x)

def testBrent():
    # Find the root of f(x) = tan(x) - 1 for 0 < x < pi/2.
    f = lambda x: math.tan(x) - 1
    tol = 1e-8
    x, numits = Brent(f, 0, 1, tol=tol)
    assert(abs(x - math.atan(1)) < 2*tol)
    # Find the roots of a quadratic
    r = 5
    f = lambda x: (x - 1)*(x - r)
    tol = 1e-8
    x, numits = Brent(f, r - 1, r + 1, tol=tol)
    assert(abs(x - r) < tol)

def testBisection():
    # Root of x = cos(x); it's 0.739085133215161 as can be found easily
    # by iteration on a calculator.
    f = lambda x: x - math.cos(x)
    tol = 1e-14
    root, numit = Bisection(f, 0.7, 0.8, tol=tol)
    assert abs(root - 0.739085133215161) <= tol
    # Eighth root of 2:  root of x**8 = 2
    f = lambda x: x**8 - 2
    tol = 1e-14
    root, numit = Bisection(f, 1, 2, tol=tol)
    assert abs(root - math.pow(2, 1/8)) <= tol
    # Simple quadratic equation
    t = 100001
    f = lambda x: (x - t)*(x + 100)
    tol = 1e-10
    root, numit = Bisection(f, 0, 2.1*t, tol=tol)
    assert abs(root - t) <= tol
    # Note setting switch to True will cause an exception for this
    # case.
    assert_raises(ValueError, Bisection, f, 0, 2.1*t, tol=tol, switch=True)

def testRidders():
    # Root of x = cos(x); it's 0.739085133215161 as can be found easily
    # by iteration on a calculator.
    f = lambda x: x - math.cos(x)
    tol = 1e-14
    root, numit = Ridders(f, 0.7, 0.8, tol=tol)
    assert abs(root - 0.739085133215161) <= tol
    # Eighth root of 2:  root of x**8 = 2
    f = lambda x: x**8 - 2
    tol = 1e-14
    root, numit = Ridders(f, 1, 2, tol=tol)
    assert abs(root - math.pow(2, 1/8)) <= tol
    # Simple quadratic equation
    t = 100001
    f = lambda x: (x - t)*(x + 100)
    tol = 1e-10
    root, numit = Ridders(f, 0, 2.1*t, tol=tol)
    assert abs(root - t) <= tol

if __name__ == "__main__":
    run(globals())
