'''
Provides generators that can produce sequences of floating point and
rational numbers and that are floating point/rational analogs of
range().

frange(start, stop, step)
    Best to initialize with string representations of floating point
    numbers.  You can control the output type and the implementation type,
    allowing use with a variety of number types.  Example:
        for i in frange("0", "1", "0.1"):
            sys.stdout.write(str(i) + " ")
    results in 
        0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 

lrange(start_decade, stop_decade)
    Useful for producing sequences that can be used for log-log plotting.
    Can also return numpy arrays.  Examples:
        for i in lrange(0, 2):
            sys.stdout.write(str(i) + " ")
    results in 
        1 2 3 4 5 6 7 8 9 10 20 30 40 50 60 70 80 90 
    and
        for i in lrange(0, 3, mantissas=[1, 2, 5]):
            sys.stdout.write(str(i) + " ")
    results in
        1 2 5 10 20 50 100 200 500 
'''

# Copyright (C) 2010 Don Peterson
# Contact:  gmail.com@someonesdad1

#
#

# Written and tested 27 Oct 2010
# lrange added 21 Dec 2010

# 22 May 2014:  removed rrange because I added fractional capabilities
# to frange.  Moved all doctests to unittest stuff.  Fixed things to
# work under python 2 & 3.  Tested OK using 2.6.5, 2.7.2, and 3.2.2.

from __future__ import division, print_function
import sys
import itertools
from decimal import Decimal
from numbers import Integral
from fractions import Fraction

from pdb import set_trace as xx
try:
    import debug
    if 0:
        debug.SetDebugger()
except ImportError:
    pass

pyver = sys.version_info[0]
if pyver == 3:
    String = str
else:
    from types import StringTypes as String

try:
    numpy_available = True
    import numpy 
except ImportError:
    numpy_available = False

err = sys.stderr.write

class Rational(Fraction):
    '''The Rational class is a fractions.Fraction object except that
    it has a conventional string representation.
    '''
    def __repr__(self):
        return ''.join((str(self.numerator), "/", str(self.denominator)))

def frange(start, stop=None, step=None, return_type=float, impl=Decimal,
           strict=True, include_end=False):
    '''A floating point generator analog of range.  start, stop, and step
    are either python floats, integers, or strings representing floating
    point numbers (or any other object that impl can convert to an object
    that behaves with numerical semantics).  The iterates returned will be
    of type return_type, which should be a function that converts the impl
    type to the desired type.  impl defines the numerical type to use for
    the implementation.  strict is used to define whether we should try to
    convert an impl object to a string before converting it to a
    return_type.  If strict is True, this is not allowed.  If strict is
    False, the conversion will be tried.  Setting strict to False may allow
    some number types to work with other number types, however, the burden
    is on the user to determine if frange still behaves as expected.
 
    If include_end is True, then the step is added to the stop
    number.  This allows you to get e.g. an inclusive list of
    integers.  However, for floating point values, you may get a
    number one step beyond the stopping point.  Examples:
 
        frange("1", "3", "0.9") returns 1.0, 1.9, 2.8
 
    but
 
        frange("1", "3", "0.9" include_end=True) returns 
        1.0 1.9 2.8 3.7
    
    Python's Decimal class is used for the default implementation, but you
    can choose it to be e.g. floats if you wish (however, you'll then have
    the typical naive implementation seen all over the web).  Consult
    http://www.python.org/dev/peps/pep-0327/ and the decimal module's
    documentation to learn more about why a float implementation is naive.
 
    To help ensure you get the output you want, use strings for start, stop
    and step.  This is the "proper" way to initialize Decimals with
    non-integer values.  start, stop, and step can be python floating point
    numbers if you wish, but you may not get the sequence you expect.  For
    an example, compare the output of frange(9.6001, 9.601, 0.0001) and
    frange("9.6001", "9.601", "0.0001").  Most users will probably expect
    the output from the second form, which excludes the stop value like
    range does.
 
    Examples of use (also look at the unit tests): 
        a = list(frange("0.125", "1", ".125"))
    results in a being
        [0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875]
    
    Alternatively, you can use rational numbers in frange (need python
    2.6 or later) because they have the proper numerical semantics.  A
    convenience class called Rational is provided in this module
    because it allows fractions to be printed in their customary
    improper form.
         R = Rational
         b = list(frange("1/8", "1", "1/8", impl=R, return_type=R))
    results in b being
         [1/8, 1/4, 3/8, 1/2, 5/8, 3/4, 7/8]
    and we also have a == b is True.
 
    The happy accident of a == b being True is only because these decimal
    fractions can be represented exactly in binary floating point.  This is
    not true in general:
        c = list(frange("0.1", "1", "0.1"))
        d = list(frange("1/10", "1", "1/10", impl=R, return_type=R))
    results in c == d being False.
 
    Print out c to see why c and d are not equal (this is practically the
    canonical example of the problems with binary floating point for us
    humans that love decimal arithmetic).

    A convenience for fractions is to use the partial function of the
    functools module:
        from functools import partial
        rrange = partial(frange, impl=Rational, return_type=Rational)
    Then you can make calls like rrange("1/10", "1", "1/10") and not
    have to supply the keywords.
    '''
    def ceil(x):
        i = int(abs(x))
        if x > i:
            i += 1
        return (-1 if x < 0 else 1)*i
    init = lambda x: (impl(repr(x)) if isinstance(x, float) else impl(x))
    start = init(start)
    if stop is not None:
        stop = init(stop)
    else:
        start, stop = impl(0), start
    step = impl(1) if step is None else init(step)
    if include_end:
        stop += step
    if not step and start < stop:
        while True:
            try:
                yield return_type(start)
            except TypeError:
                if strict:
                    raise
                yield return_type(str(start))
    else:
        for i in range(ceil((stop - start)/step)):
            try:
                yield return_type(start)
            except TypeError:
                if strict:
                    raise
                yield return_type(str(start))
            start += step

def lrange(start_decade, end_decade, dx=1, x=1, mantissas=None, use_numpy=False):
    '''Provides a logarithmic analog to the frange function.  Returns a
    list of values with logarithmic spacing (if use_numpy is True, will
    return a numpy array).  
 
    Example:  lrange(0, 2, mantissas=[1, 2, 5]) returns
    [1, 2, 5, 10, 20, 50].
    '''
    msg = "%s must be an integer"
    if not isinstance(start_decade, Integral):
        raise ValueError(msg % "start_decade")
    if not isinstance(end_decade, Integral):
        raise ValueError(msg % "end_decade")
    msg = "%s must lie in [1, 10)"
    if not (1 <= dx < 10):
        raise ValueError(msg % "dx")
    if not (1 <= x < 10):
        raise ValueError(msg % "x")
    if mantissas is None:
        mantissas = []
        while x < 10:
            mantissas.append(x)
            x += dx
    values = []
    for exp in range(start_decade, end_decade):
        values += [i*10**exp for i in mantissas]
    if use_numpy and numpy_available:
        return numpy.array(values)
    return values

