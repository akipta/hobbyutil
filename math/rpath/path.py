'''
Models parametric curves in n-dimensional space

Provides classes that produce parameterized points on various curves
in n-dimensional space.  The abstract base Class is AbstractPath,
which defines the interface.  Please refer to the documentation
path.pdf supplied in the project's zipfile.
 
Design goals:
 
    * Test with python 2.6.5, 2.7.2, and 3.2.2.
    * Try to derive from one base Class.
    * Intuitive operation.
    * Make it easy to create new path objects.
 
TODO
    - Objects to add
        * Sinusoid 
        * Rectangle
''' 

# Copyright (C) 2014 Don Peterson
# Contact:  gmail.com@someonesdad1
 
#
#

from __future__ import division, print_function
import sys, math
from operator import add, sub, mul
from fractions import Fraction
from decimal import Decimal
from collections import Iterable
from out import out
 
pyver = sys.version_info[0]
if pyver > 2:
    long = int
    String = str
else:
    String = (str, unicode)
 
# The base_number_type is the type used for numerical calculations.
# You probably want this to be the float type, but you can change it
# if needed (for example, you might want to make it the mpf type of
# the mpmath module for arbitrary-precision arithmetic).
base_number_type = float

# Supported number types (edit as needed).  You can use any number
# type that can be converted to base_number_type.
Number = (int, long, base_number_type, Fraction, Decimal)
 
class AbstractMethodError(Exception): pass

class Path(object):
    '''Defines the basic interface of Path objects.
 
    Attributes
    ----------
 
    total_arc_length
        The total arc length of the path.
    parameter
        A 2-sequence of numbers representing the low and high values
        of the parameter.
    eps
        A number that is used to decide when a calculation result
        should be replaced by zero.  Set to zero to have no
        replacements made.
    xfm
        A function object that is used to transform returned points.
        Defaults to None.
    xfm_kw
        A keyword dictionary that is passed to the xfm function.
        Defaults to an empty dictionary.
    '''
    def __init__(self):
        # Attributes that begin with an underscore are not meant to be
        # accessed directly by the user.
        self._xfm = None                # Transformation function
        self._xfm_kw = {}               # Keywords dict for xfms
        self._parameter = (0, 1)        # How to map parameter
        self._eps = base_number_type(0) # Type of floating pt numbers
        self._complex = False           # Return point as complex number
        self._is_closed = False         # Is a closed path
        self._is_2_sequence = False     # Can convert to complex
        self.cw = False                 # Clockwise traversal
    def __call__(self, p):
        '''Return the point corresponding to parameter value p.
        '''
        raise AbstractMethodError()
    def __str__(self):
        raise AbstractMethodError()
    @property
    def total_arc_length(self):
        raise AbstractMethodError()
    #
    def _set_parameter(self, p):
        if not Path.IsNumberSequence(p):
            raise ValueError("Parameter must be a 2-sequence of numbers")
        if p[0] >= p[1]:
            m = "The first parameter must be < the second parameter"
            raise ValueError(m)
        self._parameter = tuple(p)
    def _get_parameter(self):
        return self._parameter 
    parameter = property(_get_parameter, _set_parameter)
    #
    # eps is an attribute used to define when a number is sufficiently
    # close to zero to be set to zero.  Set eps to 0 (the default) if
    # you don't want substitution to occur.
    def _set_eps(self, eps):
        try:
            self._eps = abs(base_number_type(eps))
        except Exception:
            raise ValueError("eps must be a number")
    def _get_eps(self):
        return self._eps 
    eps = property(_get_eps, _set_eps)
    #
    # complex is an attribute that, when True, instructs the __call__
    # method to return a complex number when the Path object is
    # defined in the complex plane.
    def _set_complex(self, complex):
        if not self._is_2_sequence:
            raise ValueError("Range isn't the complex plane")
        try:
            self._complex = bool(complex)
        except Exception:
            raise ValueError("complex must be a Boolean")
    def _get_complex(self):
        return self._complex 
    complex = property(_get_complex, _set_complex)
    # Note that xfm and xfm_kw are implemented here as simple
    # attributes with only basic checking.  Your derived classes may
    # want to check them in more detail (e.g., ensure xfm takes the
    # right number of parameters).
    def _get_xfm(self):
        return self._xfm
    def _set_xfm(self, xfm):
        if xfm and not hasattr(xfm, "__call__"):
            raise ValueError("xfm must be callable")
        self._xfm = xfm
    xfm = property(_get_xfm, _set_xfm)
    #
    def _get_xfm_kw(self):
        return self._xfm_kw
    def _set_xfm_kw(self, xfm_kw):
        if xfm_kw is not None and not isinstance(xfm_kw, dict):
            raise ValueError("xfm_kw must be a dictionary object or None")
        self._xfm_kw = xfm_kw
    xfm_kw = property(_get_xfm_kw, _set_xfm_kw)
    @staticmethod
    def IsNumberSequence(x, length=2):
        '''Return True if x is a sequence of numbers of the proper
        length.  If length is None, then anylength is allowed.
        '''
        if not Path.IsIterable(x, length=length):
            return False
        try:
            [base_number_type(i) for i in x]
            return True
        except Exception:
            return False
    @staticmethod
    def IsIterable(x, length=2):
        '''Return 2 if x is an iterable that is not a string.  It must
        have the indicated length; set length to None to allow any
        length.
        '''
        try:
            # Catches exception when len() doesn't work
            if (isinstance(x, String) or 
               (length is not None and len(x) != length)):
                return False
        except Exception:
            return False
        return True if isinstance(x, Iterable) else False
    def _zero(self, x):
        '''If eps is not zero, then return 0 if abs(x) <= eps.
        '''
        if self.eps:
            if abs(x) <= self.eps:
                return base_number_type(0)
        return x
    @property
    def is_closed(self):
        '''Return True if the path is closed.  This means the point
        returned for the beginning parameter value is the same as the
        point returned for the ending parameter value.
        '''
        return self._is_closed
    def _to_complex(self, *point):
        '''Convert the point to a complex number if it is a point in
        the plane and the complex attribute is True.
        '''
        if self._complex:
            if len(point) != 2:
                return point
            return complex(point[0], point[1])
        else:
            return point

class Ellipse(Path):
    '''Unless you set the e keyword parameter in the constructor to a
    number less than 1, the path will be a circle, not a true ellipse.
 
    The e term is the ratio of b/a (the minor diameter divided by the
    major diameter).  The eccentricity (in the sense of a conic
    section) is sqrt(1 - e*e).
    '''
    def __init__(self, **kw):
        '''
        Keywords                                Default value
        -----------------------------           ----------------
        radius                                  radius = 1
        diameter
        e         (flattening) (0 <= e <= 1)    1 (gives a circle)
        center    2-sequence of numbers         (0, 0)
        parameter 2-sequence of numbers         (0, 1)
        angle_origin (in radians)               0
 
        The flattening ratio e is the ratio of the minor diameter to
        the major diameter.  Note it is *NOT* the same as the
        eccentricity ecc of a conic; the relationship is 
            ecc = sqrt(1 - e*e)
 
        The angle_origin defines the angle off the x axis to use for
        the polar angle.  Example:  if you wanted a path traversed
        like a conventional compass (north at the top and clockwise
        traversal), you'd set the cw attribute to True and
        angle_origin to pi/2 radians.
        '''
        super(Ellipse, self).__init__()
        self._is_closed = True
        self._is_2_sequence = True 
        self._angle_origin = 0
        # Diameter/radius
        if "diameter" in kw and "radius" in kw:
            raise ValueError("Can't set both diameter and radius")
        self._radius = kw.setdefault("radius", 1.0)
        if "diameter" in kw:
            self._radius = kw["diameter"]/2.0
        # Center
        self._center = kw.setdefault("center", (0.0, 0.0))
        e = ValueError("center must be a sequence of 2 numbers")
        if not self.IsNumberSequence(self._center):
            raise e
        # Parameter range (base class does checking)
        self.parameter = kw.setdefault("parameter", (0.0, 1.0))
        # Flattening ratio
        self._e = kw.setdefault("e", 1.0)
        if not (0 <= self._e <= 1):
            raise ValueError("e (flattening) must be between 0 and 1")
        self._name = "Ellipse"
    def __str__(self):
        s = ["%s(" % self._name]
        f, a, e = "  %-16s = %s", 2*self._radius, self._e
        b = e*a
        ecc = math.sqrt(1 - (b/a)**2)
        s.append(f % ("Major diameter a", a))
        s.append(f % ("Minor diameter b", a*e))
        s.append(f % ("Circumference", self.total_arc_length))
        if self._name != "Circle":
            s.append(f % ("Flatness (b/a)", self._e))
            s.append(f % ("Eccentricity", ecc))
        s.append(f % ("Center", str(self._center)))
        s.append(f % ("Parameter", str(self._parameter)))
        s.append(f % ("Using xfm", str(self._xfm is not None)))
        s.append(f % ("epsilon", str(self._eps)))
        s.append(")")
        return '\n'.join(s)
    @property
    def r(self):
        return self._radius
    @property
    def d(self):
        return 2*self._radius
    @property
    def total_arc_length(self):
        a, b = self._radius*2, self._e*self._radius*2
        return self.EllipseCircumference(a, b)
    def _set_angle_origin(self, theta):
        '''Set the angle_origin attribute in radians.
        '''
        try:
            self._angle_origin = base_number_type(theta)
        except Exception:
            raise ValueError("theta is a bad angle origin number")
    def _get_angle_origin(self):
        return self._angle_origin
    angle_origin = property(_get_angle_origin, _set_angle_origin)
    @staticmethod
    def EllipseCircumference(a, b):
        '''Calculate the circumference of an ellipse with major
        diameter a and minor diameter b.  Relative accuracy is about
        0.5^53 (~ 1e-16).  Downloaded Mon 26 May 2014 from
        http://paulbourke.net/geometry/ellipsecirc/python.code
        It's a fast and efficient algorithm that converges
        quadratically.
        '''
        if a < 0 or b < 0:
            raise ValueError("a and b must be >= 0")
        a, b = a/2, b/2  # Bourke's formulation uses the 'semi-axes'
        x, y = max(a, b), min(a, b)
        digits = 53; tol = math.sqrt(math.pow(0.5, digits))
        if digits*y < tol*x: return 4*x
        s = 0; m = 1
        while x - y > tol*y:
            x, y = 0.5*(x + y), math.sqrt(x*y)
            m *= 2
            s += m*math.pow(x - y, 2)
        return math.pi*((a + b)**2 - s)/(x + y)
    def __call__(self, p):
        ''' The parametric equations of an ellipse at the origin are
 
            x = a*cos(2*pi*t)   for t in [0. 1]
            y = b*sin(2*pi*t)
              = a*e*sin(2*pi*t)
        '''
        p0, p1 = self._parameter
        if not (p0 <= p <= p1):
            m = "Parameter must be in [%s, %s]" % self._parameter
            raise ValueError(m)
        # If self.cw, clockwise traversal is wanted, so we'll negate
        # the parameter.
        p = -p if self.cw else p
        # Transform absolute value to [0, 1]
        t = (p - p0)/(p1 - p0)
        # Polar angle of point
        theta, e, r = 2*math.pi*t, self._e, self._radius
        # Correct for desired angle origin
        theta += self._angle_origin
        x = r*math.cos(theta)
        y = e*r*math.sin(theta)
        # Apply transformation
        if self._xfm is not None:
            if self._xfm_kw is not None:
                x, y = self._xfm(x, y, **self._xfm_kw)
            else:
                x, y = self._xfm(x, y)
        x = self._zero(x)
        y = self._zero(y)
        return self._to_complex(x, y)

class Circle(Ellipse):
    def __init__(self, **kw):
        super(Circle, self).__init__(**kw)
        self._ecc = 1
        self._name = "Circle"

class RectilinearPath(Path):
    '''Encapsulates a rectilinear path.  Initialize with a sequence of
    n-sequences and you can interpolate a position on the path with a
    parameter t on [0, 1]:
        
        rp = RectilinearPath(seq)
        position = rp(0.6)
 
    position will be an n-sequence geometrically between two of the
    points in n-dimensional Euclidean space.
 
    Example:
        rp = RectilinearPath(((0, 0), (1, 1), (2, 2))
    represents the line y = x.  Call rp as a function with a parameter
    to perform the interpolation:
        rp(0.5) 
    returns
        (1.0, 1.0)
    '''
    def __init__(self, seq, parameter=(0, 1)):
        '''seq must be a sequence of n-sequences of numbers:
        seq = (
            (a1, a2, ..., an),    # n items
            (b1, b2, ..., bn),    # n items
            ...
            (m1, m2, ..., mn),    # n items
        )
        seq has m items. 
 
        parameter is a 2-sequence of numbers that define the starting
        and ending values of the parameter.  Suppose parameter is set
        to (a, b).  Then if rp is an RectilinearPath object, rp(a)
        returns the first point in seq and rp(b) returns the last
        point in seq.  For a < c < b, rp(c) returns a point on the
        interior of the path.
        '''
        if isinstance(seq, String):
            raise ValueError("seq can't be a string")
        try:
            iter(seq)
        except TypeError:
            raise ValueError("seq must be an iterable")
        # Base class checks parameter
        self.parameter = tuple([base_number_type(i) for i in parameter])
        # Make a mutable copy of seq
        self._seq = list(seq)
        # Process each element and convert to tuples for immutability
        for i, elem in enumerate(self._seq):
            if isinstance(elem, String):
                raise ValueError("seq[%d] can't be a string" % i)
            try:
                iter(elem)
            except TypeError:
                raise ValueError("seq[%d] must be an iterable" % i)
            if not i:
                self._dim = len(elem)
            if len(elem) != self._dim:
                raise ValueError("seq[%d] must have length %d" % (i, self._dim))
            elem = list(elem)
            not_all_numbers = not all([isinstance(j, Number) for j in elem])
            if not_all_numbers:
                m = "One or more elements of seq[%d] are not numbers:\n  " % i
                m += str(elem)
                raise ValueError(m)
            # Convert to a tuple of base_number_types
            self._seq[i] = tuple([base_number_type(j) for j in elem])
        self._seq = tuple(self._seq)
        if len(self._seq) < 2:
            raise ValueError("seq must have at least two elements")
        # Get lengths of each segment
        self._lengths = []
        for i in range(len(self._seq)):
            if not i:
                continue
            d = self._EuclideanDistance(i - 1, i)
            self.lengths.append(d)
        self._lengths = tuple(self._lengths)
        self._total_arc_length = sum(self._lengths)
        # Construct an array of the cumulative lengths
        self._cumul_lengths = []
        for i in range(len(self._lengths) + 1):
            self._cumul_lengths.append(sum(self._lengths[:i]))
        self._is_closed = (seq[0] == seq[-1])
    def __str__(self):
        s = ["RectilinearPath("]
        s.append("  Total length = %s" % self._total_arc_length)
        num = int(math.ceil(math.log10(len(self._seq))))
        for i, elem in enumerate(self._seq):
            s.append("  %*d %s" % (num, i, str(elem)))
        s.append(")")
        return '\n'.join(s)
    def __len__(self):
        return len(self._seq)
    def _EuclideanDistance(self, index1, index2):
        '''Return the Euclidean distance between the two points; the
        indexes are their position in the sequence.
        '''
        try:
            seq1 = self._seq[index1]
            seq2 = self._seq[index2]
        except IndexError:
            raise ValueError("%d or %d is a bad index" % (index1, index2))
        # list() is needed for python 3
        s = list(map(sub, seq1, seq2))
        return math.sqrt(sum(map(mul, s, s)))
    @property
    def dim(self):
        '''Return the length of each point sequence (i.e., the
        dimension of the Euclidean vector space the points are in).
        '''
        return self._dim
    @property
    def seq(self):
        '''Return the sequence of points.
        '''
        # Since it's a tuple of tuples, it doesn't need to be copied
        # because the user can't change the original.
        return self._seq
    @property
    def total_arc_length(self):
        '''Return the total arc length of the path.
        '''
        return self._total_arc_length
    @property
    def lengths(self):
        '''Return a tuple of the length of each subpath.
        '''
        return self._lengths
    def _check_parameter(self, t):
        t0, t1 = self._parameter
        if not (t0 <= t <= t1):
            msg = "Parameter t must be between %s and %s."
            raise ValueError(msg % self._parameter)
    def _get_index(self, t):
        '''Return the index of the two points that bracket t.
        '''
        t0, t1 = self._parameter
        # Must interpolate.  Convert parameter to value u on [0, 1].
        u = (t - t0)/base_number_type(t1 - t0)
        # This is the fraction of the distance along the path.
        tl = self._total_arc_length
        distance = u*self._total_arc_length
        # Find the indexes of the elements in self._cumul_lengths that
        # straddle this distance.
        cl, found = self._cumul_lengths, None
        for i in range(1, len(cl)):
            if cl[i - 1] <= distance < cl[i]:
                found = i
                break
        if found is None:
            raise RuntimeError("Bug:  distance not in self._cumul_lengths")
        return found
    def __call__(self, t):
        '''Return the point corresponding to the parameter value of t.
        If a and b are two vectors, then the parametric equation for
        the line between the two endpoints is (1-t)*a + t*b where t
        is on [0, 1].  
        '''
        self._check_parameter(t)
        t0, t1 = self._parameter
        if t == t0:
            return self._seq[0]
        elif t == t1:
            return self._seq[-1]
        found = self._get_index(t)
        cl = self._cumul_lengths
        distance = self.length(t)
        # Get the two endpoints of the line.
        p0, p1 = self._seq[found - 1:found + 1]
        # Get v, a parameter on [0, 1) that parameterizes the required
        # point between these two endpoints.  
        numer = distance - self._cumul_lengths[found - 1]
        denom = cl[found] - cl[found - 1]
        v = numer/base_number_type(denom)
        # Interpolate between the two points:  the desired point is
        # given by (1 - v)*p0 + v*p1.
        vp0, vp1 = [(1 - v)*i for i in p0], [v*i for i in p1]
        p = tuple(map(add, vp0, vp1))
        return p
    def length(self, t):
        '''Return the path length associated with the parameter t.
        '''
        self._check_parameter(t)
        t0, t1 = self._parameter
        if t == t0:
            return 0.0
        elif t == t1:
            return self._total_arc_length
        return self._total_arc_length*((t - t0)/base_number_type(t1 - t0))

class Rotation(object):
    '''Behaves as a rotation in the plane, so is suitable for the xfm
    attribute of e.g. Ellipse path objects.
    '''
    def __init__(self, theta):
        self._set_angle(theta)
    def __call__(self, x, y):
        X = x*self._c - y*self._s
        Y = x*self._s + y*self._c
        return (X, Y)
    def _set_angle(self, theta):
        self._theta = theta
        self._c = math.cos(theta)
        self._s = math.sin(theta)
    def _get_angle(self, theta):
        return self._theta
    theta = property(_get_angle, _set_angle)

