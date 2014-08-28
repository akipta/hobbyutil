from __future__ import division, print_function
import sys
from pdb import set_trace as xx

pyver = sys.version_info[0]
if pyver == 3:
    long = int
    unicode = str

__doc__ = '''
Represent a number to a specified number of significant figures

Please see the sig.pdf document for more details; it's in the package
sig.zip from http://code.google.com/p/hobbyutil/.

sig is a convenience instance of SigFig.  Set the attributes for the
behavior you want.  sig(x) will return a string with x given to a
stated number of significant figures.  x can be ints and floats,
fractions, floats as strings, sequences, strings of floats or integers
separated by whitespace, python complex numbers, python Decimal
objects, mpmath floating point and complex numbers, any sequence of
such objects, and ufloat() objects from the python uncertainties
module.

If you get import exceptions when loading this module, it may be
because it's trying to load a nonexistent module such as numpy.
Change the _default global variable below to reflect the libraries
you want to import and support.  The current optional modules
supported are:
    mpmath              http://code.google.com/p/mpmath/
    numpy               http://numpy.scipy.org/
    uncertainties       http://pypi.python.org/pypi/uncertainties/

sig(x) returns a string representation of x to a user-specified
number of significant figures.  x can be a number object or various
types of sequences (possibly nested) that can be iterated over.
Various attributes tailor the behavior.  Note:  sig is a convenience
instance of the SigFig object; it is intended for most programs where
you only need one SigFig object for formatting your numbers.  You can
instantiate multiple objects if you need a variety of behaviors.

Tested on python 2.6.5, 2.7.2, and 3.2.2.

Summary of attributes (see sig.pdf):
    
digits              Controls number of sig. digits in output
dp                  String to represent decimal point
dp_position         Location of decimal point from left edge
echar               Character for indicating an exponent
edigits             Minimum number of digits in exponent
esign               If True, include + for a positive exponent
fit                 Adjust 'digits' to get a fit
high                If x > high, use scientific notation
idp                 If True, ints will have trailing decimal point
ignore_none         True:  None == 0
integer             How to format integers
lead_zero           If True, leading 0 for abs(x) < 1 is included
low                 If x < low, use scientific notation
mixed               True = mixed fractions in template rounding
rtz                 True = remove trailing zeros
separator           Separator for sequences
sign                True = always show sign of number
zero_limit          x is 0 if abs(x) < zero_limit

Complex number attributes:

imag_before         True = imag unit before imag part
imag_deg            True = use degrees for polar angle
imag_deg_sym        String to represent degrees
imag_limit          Analogous to zero_limit but for Im(x)
imag_polar          True = display in polar
imag_polar_sep      String to separate |x| and Arg(x)
imag_post           String after the sign combining Re(x) and Im(x)
imag_pre            String before the sign combining Re(x) and Im(x)
imag_sep            String that separates Im(x) from 'i' or 'j'
imag_unit           String for imaginary unit

For complex number pairs:

imag_pair           True = display in pair form
imag_pair_left      String for left part of the pair
imag_pair_right     String for right part of the pair
imag_pair_sep       String separating Re(x) and Im(x)

For ufloats:

unc_short           True = use shorthand 1.234(5); else 1.234+/-0.005
unc_digits          Num of sig fig in uncertainty
unc_sep             String separating value & uncertainty in long form
unc_pre             String separating value & uncertainty in short form
unc_post            String that follows uncertainty in short form
'''.strip()

# Copyright (C) 2012 Don Peterson
# Contact:  gmail.com@someonesdad1

#
#

_defaults = {
    # If you want sig to support the associated library, set these to
    # True.  If you don't have them installed, set them to False.
    "use_numpy"  : True,
    "use_mpmath" : True,
    "use_uncertainties" : True,
}

from fractions import Fraction
import decimal, os, sys, unittest, traceback as tb, random, math, string
import re, locale

Dec = decimal.Decimal

# Import the optional libraries
_have_numpy = False
if _defaults["use_numpy"]:
    try:
        import numpy as np
        _have_numpy = True
    except ImportError:
        pass

_have_mpmath = False
if _defaults["use_mpmath"]:
    try:
        import mpmath as mp
        _have_mpmath = True
    except ImportError:
            pass

_have_uncertainties = False
if _defaults["use_uncertainties"]:
    try:
        import uncertainties as unc
        _have_uncertainties = True
    except ImportError:
            pass

class SigFig(object):
    # Default settings for the class.  For Boolean settings, the
    # description is for when the setting is True.
    _digits         = 3         # Significant figures (see doc)
    _dp             = locale.localeconv()["decimal_point"]
    _dp_position    = 0         # Decimal point position (need sig.fit too)
    _echar          = "e"       # Exponent character
    _edigits        = 1         # Exponent number of digits
    _esign          = True      # Include exponent sign even if +
    _fit            = 0         # Width to fit returned string into and justify
    _high           = "1e6"     # Above this value use scientific notation
    _idp            = False     # Show decimal point after integers
    _ignore_none    = False     # An x value of None results in zero
    _integer        = 0         # If > 0, format as int, not float
    _lead_zero      = True      # Include 0 before dp for abs(x) < 1
    _low            = "1e-3"    # Below this value use scientific notation
    _mixed          = True      # Template round to mixed fraction
    _rtz            = False     # Remove trailing zeros
    _separator      = ", "      # Separates sequence elements
    _sign           = False     # Include sign even if +
    _zero_limit     = 0         # Threshold to call a number zero
    # Complex number options
    _imag_before    = False     # True: 3.0-i8.4, False:  3.0-8.4i
    _imag_deg       = True      # Display angle in degrees
    _imag_deg_sym   = "*"       # Denotes angle in degrees
    _imag_full      = True      # Show as x+iy even if component is 0
    _imag_limit     = 0         # Threshold to call Im zero
    _imag_polar     = False     # Display in polar form 3.0/_8.4*
    _imag_polar_sep = "/_"      # Polar form separator
    _imag_post      = ""        # String immediately before abs(Im)
    _imag_pre       = ""        # String immediately after Re
    _imag_sep       = ""        # String to separate unit from Im
    _imag_unit      = "i"       # String for imaginary unit
    # The following are for displaying complex numbers as pairs of
    # numbers.  The usual convention is (x, y), but this wouldn't be
    # distinguishable from a tuple, so some alternative method is
    # necessary.  The form of the complex number x+iy will be
    # _imag_pair_left + sig(x) + _imag_pair_sep + sig(y) + _imag_pair_right
    _imag_pair      = False     # If True, use this pair display
    _imag_pair_sep  = "|"
    _imag_pair_left = "<"
    _imag_pair_right = ">"
    # (The physicists will now complain this is confused with bra/ket
    # notation... :^)
    # The following are for uncertainties and determine the string
    # that surrounds the uncertainty after the significand.
    _unc_short      = True      # Use 1.23(4) form; otherwise 1.23+-0.04
    _unc_digits     = 1         # Default sig fig in uncertainty
    _unc_sep        = "+/-"     # Separator for long form
    _unc_pre        = "("       # Left separator for short form
    _unc_post       = ")"       # Right separator for short form

    def __init__(self):
        '''Set our instance attributes from the class attributes.
        '''
        self.stack = []  # Keeps track of pushed states
        # Regular expression objects for recognizing numbers with
        # uncertainty and units.
        self.r_number = re.compile(r'''(?x)
            # Use to recognize a float or int.  The first group is the
            # number; the fourth is the unit; the second and third are
            # ignored.
            ^
            (                       # Group
                [+-]?               # Optional sign
                \.\d+               # Number like .345
                ([eE][+-]?\d+)?|    # Optional exponent
            # or
                [+-]?               # Optional sign
                \d+\.?\d*           # Number:  2.345
                ([eE][+-]?\d+)?     # Optional exponent
            )                       # End group
            (.*)                    # Optional unit string
            $
        ''')
        # Used to recognize numbers with short-form uncertainties and
        # units.
        self.r_short = re.compile(r'''(?x)
            # There are seven groups in this regular expression to
            # allow picking apart a floating point number or integer
            # with a short-form uncertainty and optional unit.  The
            # groups are:
            #   0   Sign
            #   1   Digits before decimal point
            #   2   Decimal point
            #   3   Digits after decimal point
            #   4   Uncertainty in parenteses
            #   5   Exponent
            #   6   Unit string
            ^               # Must be at beginning of string
            ([+-]?)         # Sign
            (\d*)           # Leading digits
            ([\.,]?)        # Decimal point
            (\d*)           # Trailing digits
            (\(\d+\))       # Uncertainty
            ([eE][+-]?\d+)? # Optional exponent
            (.*)$           # Optional ending unit string
        ''')

        self.reset()

    def reset(self):
        '''Set the object's attributes to their default values.
        '''
        # The attributes that begin with underscores are properties
        # (i.e., they have getters and setters).
        self._digits         = SigFig._digits
        self.dp              = SigFig._dp
        self.dp_position     = SigFig._dp_position
        self.echar           = SigFig._echar
        self.edigits         = SigFig._edigits
        self.esign           = SigFig._esign
        self._fit            = SigFig._fit
        self._high           = SigFig._high
        self.idp             = SigFig._idp
        self.ignore_none     = SigFig._ignore_none
        self.integer         = SigFig._integer
        self.lead_zero       = SigFig._lead_zero
        self._low            = SigFig._low
        self.mixed           = SigFig._mixed
        self.rtz             = SigFig._rtz 
        self.separator       = SigFig._separator
        self.sign            = SigFig._sign
        self.zero_limit      = SigFig._zero_limit
        # Complex number attributes
        self.imag_before     = SigFig._imag_before
        self.imag_deg        = SigFig._imag_deg
        self.imag_deg_sym    = SigFig._imag_deg_sym
        self.imag_full       = SigFig._imag_full
        self.imag_limit      = SigFig._imag_limit
        self.imag_polar      = SigFig._imag_polar
        self.imag_polar_sep  = SigFig._imag_polar_sep
        self.imag_post       = SigFig._imag_post
        self.imag_pre        = SigFig._imag_pre
        self.imag_sep        = SigFig._imag_sep
        self.imag_unit       = SigFig._imag_unit
        # Complex number pair form
        self.imag_pair       = SigFig._imag_pair
        self.imag_pair_sep   = SigFig._imag_pair_sep
        self.imag_pair_left  = SigFig._imag_pair_left
        self.imag_pair_right = SigFig._imag_pair_right
        # Uncertainties
        self.unc_short       = SigFig._unc_short
        self.unc_digits      = SigFig._unc_digits
        self.unc_sep         = SigFig._unc_sep
        self.unc_pre         = SigFig._unc_pre
        self.unc_post        = SigFig._unc_post
        self.check()

    def __call__(self, *par):
        '''This method is the user's primary interface with the
        object.  There can be one or two parameters.  The first
        parameter is the number or sequence to be formatted.  The
        second argument, if present, is the number of significant
        digits to format the object to; if not present, the _digits
        attribute is used (i.e, the second parameter overrides the
        _digits attribute when desired).  If digits is not an integer,
        the behavior is to use it as a template for rounding instead.
        '''
        if not len(par):
            raise ValueError("Need an argument")
        elif len(par) == 1:
            x, digits = par[0], self._digits
        elif len(par) == 2:
            if isinstance(par[1], Fraction):
                x, digits = par
            else:
                x, digits = par[0], self._convert_number(par[1], 
                        "Second parameter (digits)")
        else:
            raise ValueError("Too many arguments")
        if self._is_iterable(x): 
            return self._seq(x, digits)
        ary = self._convert_to_array(x)
        if ary is not None:
            return self._seq(ary, digits)
        else:
            if (isinstance(x, (complex, _Complex)) or 
                (_have_mpmath and isinstance(x, mp.mpc))):
                x = _Complex(x)
            else:
                if _have_uncertainties and isinstance(x, unc.UFloat):
                    return self._sig_uncertainty(x, digits, len(par)==2)
                x = self._convert_number(x, name="x")
            return self._sig(x, digits)

    def _sig_uncertainty(self, x, digits, digits_override=False):
        '''Handle the case where x is a ufloat from the uncertainties
        module.  If digits_override is True, then use the digits
        parameter for the number of significant figures in the
        standard deviation in the short form; otherwise, use the
        self.unc_digits attribute.
        '''
        assert isinstance(x, unc.UFloat)
        # Because the uncertainties module uses the built-in python
        # floating point numbers, I'll assume that the number of
        # digits is 15 or less.  This will cause a bug on a system
        # that has more digits in floats, but hopefully should be easy
        # to find and fix.  I doubt many people would want to see an
        # uncertainty to more than 15 significant figures anyway.
        # 3 Mar 2013:  I changed this to 14 to avoid a bug where the
        # number ufloat("38.850000000000001+/-0.099999999999999992")
        # gets printed as 38.85(1) instead of 38.9(1), as it should.
        nd = 14
        if not (isinstance(digits, int) and 1 <= digits <= nd):
            msg = "For an uncertainty, digits must be an integer >= 1 and <= %d"
            raise ValueError(msg % nd)
        # Get the regular form of m+-u
        fit = self.fit
        self.fit = 0
        m = self._sig(Dec(str(x.nominal_value)), digits)
        u = self._sig(Dec(str(x.std_dev)), self.unc_digits)
        self.fit = fit
        U = m + self.unc_sep + u
        if self.unc_short:
            # Return in short form such as 1.23(6)
            M, S = x.nominal_value, x.std_dev
            if abs(S) > abs(M):
                # It's impossible to represent this number in short form
                return U
            if not M and not S:
                return "0.(0)"
            if not digits_override and S:
                digits = self.unc_digits
            u_significand, u_exponent = ("%.*e" % (nd, S)).split("e")
            u_exponent = int(u_exponent)
            u_significand = self._remove_decimal_point(u_significand)
            dbg = False
            if dbg:
                print("digits = " + str(digits))
                print("M = " + str(M))
                print("S = " + str(S))
                print("u_significand = " + str(u_significand))
                print("u_exponent = " + str(u_exponent))
            # u_significand is a string that represents a large
            # integer.  Convert it to a float and use self._sig()
            # to ensure it is rounded to digits significant digits.
            if S:
                # Turn off fitting if it is on
                fit = self.fit
                self.fit = 0
                u_significand = self._sig(float(u_significand), digits)
                self.fit = fit
                # Keep the indicated number of digits in the uncertainty
                u_significand = self._remove_decimal_point(u_significand)[:digits]
            else:
                u_significand = "0"
            if dbg:
                print("u_significand to num places = " + str(u_significand))
            # Template round the significand of x to the last
            # significant figure of the uncertainty.
            d = u_exponent - digits 
            m_significand, m_exponent = ("%.*e" % (nd, M)).split("e")
            m_exponent = int(m_exponent)
            if dbg:
                print("d = " + str(d))
                #print("Rounded significand of mean = " + str(m))
                print("m_significand = " + str(m_significand))
                print("m_exponent = " + str(m_exponent))
            # Get the number of significant digits in the significand.
            if S:
                significand_digits = m_exponent - d 
                # Handle a special case where the significand is 1 and
                # we have a rounding issue.  This was exhibited as a
                # bug by sig(unc.ufloat(1*e, 0.005*e) giving
                # 1.00(5)e-88 instead of 1.000(5)e-88.
                if float(m_significand) >= 9.999999999999999:
                    significand_digits += 1
            else:
                significand_digits = digits
            if significand_digits < 1:
                # In the following, the original method was to
                # generate an error if the uncertainty was too large.
                # I've decided to change this to always limit the
                # number of significand digits to 1 to avoid getting
                # errors in some applications.  However, it should be
                # noted that these large uncertainties are probably
                # outside of the assumptions made by the uncertainties
                # module (i.e., that uncertainties are small and that
                # the linear part is much larger than higher-order
                # terms).
                if 0:
                    msg = "Uncertainty %s is too large for significand %s" % (S, M)
                    raise ValueError(msg)
                else:
                    significand_digits = 1
            # Turn off fitting if it is on
            fit = self.fit
            self.fit = 0
            significand = self._sig(float(M), significand_digits)
            self.fit = fit
            if dbg:
                print("significand_digits = " + str(significand_digits))
                print("significand = " + str(significand))
            # If the significand is expressed in scientific notation,
            # insert the uncertainty.  Otherwise, just append it.
            if "e" in significand.lower():
                u = self.unc_pre + u_significand + self.unc_post
                if "e" in significand:
                    s, e = significand.split("e")
                    exp = "e"
                else:
                    s, e = significand.split("E")
                    exp = "E"
                answer = s + u + exp + e
                if dbg:
                    return "Answer = " + answer
                return answer
            else:
                # We can have that u_significand is a number to the
                # left of the decimal point.  If so, we must add 0's
                # to the right until u_significand has the correct
                # exponent.
                d = u_exponent - digits + 1
                if d > 0 and S:
                    u_significand += "0"*d
                u = self.unc_pre + u_significand + self.unc_post
                answer = significand + u
                if dbg:
                    return "Answer =" + answer
                return answer
        else:
            return U

    def _fmt_int(self, x):
        '''Format the integer x.  If you have sig.integer set to 2 and
        you want to see commas in the output, you'll have to set a
        locale.  One such command could be: 
 
            locale.setlocale(locale.LC_ALL, '')
 
        You could also put the above line in this function; I didn't
        do this because I didn't want the sig module changing the
        locale.
        '''
        return format(x, "n")

    def _remove_decimal_point(self, s):
        '''Remove the decimal point.  Hopefully, this will work
        correctly in any locale, but it could be a bug if the decimal
        point representation is not a period or a comma and self.dp
        isn't set correctly.
        '''
        s = s.replace(".", "").replace(",", "")
        s = s.replace(self.dp, "")
        return s

    def _sig_complex(self, x, digits):
        '''Handle the case where x is a complex number.
        '''
        if not isinstance(x, _Complex):
            raise TypeError("x must be a _Complex object")
        if self._fit:
            return self._sig_complex_fit(x, digits)
        return self._sig_complex_no_fit(x, digits)

    def _sig_complex_fit(self, x, digits):
        '''The string needs to be fit into self._fit spaces.
        '''
        if not isinstance(digits, (int, long)):
            raise ValueError("digits must be int if fit != 0")
        assert digits > 0
        old_fit = self._fit
        self._fit = 0
        s = self._sig_complex_no_fit(x, digits)
        while digits > 1 and len(s) > abs(old_fit):
            digits -= 1
            s = self._sig_complex_no_fit(x, digits)
        if digits == 1 and len(s) > abs(old_fit):
            s = "None"[:abs(old_fit)]
        # Now justify appropriately
        if len(s) < abs(old_fit):
            if old_fit < 0:
                s = s.ljust(abs(old_fit))
            else:
                s = s.rjust(abs(old_fit))
        self._fit = old_fit
        return s

    def _sig_complex_no_fit(self, x, digits):
        '''Format a complex that doesn't need to be fitted into a
        specified number of spaces.
        '''
        s = []
        if self.imag_polar:
            # Polar form
            r = self._sig((x.real**2 + x.imag**2).sqrt(), digits)
            s.append(r)
            s.append(self.imag_pre)
            s.append(self.imag_polar_sep)
            s.append(self.imag_post)
            # 0+0i will be 0/_0
            if not x.real and not x.imag:
                theta = D(0)
            else:
                theta = atan2(x.imag, x.real)
            if self.imag_deg:
                theta *= 180/pi()
                s.append(self._sig(theta, digits))
                s.append(self.imag_deg_sym)
            else:
                s.append(self._sig(theta, digits))
        elif self.imag_pair:
            # Pair display
            s.append(self.imag_pair_left)
            s.append(self._sig(x.real, digits))
            s.append(self.imag_pair_sep)
            s.append(self._sig(x.imag, digits))
            s.append(self.imag_pair_right)
        else:
            # Rectangular form
            ignore_real, ignore_imag = False, False
            if not self.imag_full and (abs(x.real) < self.zero_limit or 
                    not x.real):
                ignore_real = True
            if not self.imag_full and (abs(x.imag) < self.imag_limit or 
                    not x.imag):
                ignore_imag = True
            if not ignore_real:
                if not ignore_imag:
                    # It's a full complex number
                    s.append(self._sig(x.real, digits))
                    s.append(self.imag_pre)
                    s.append("+" if x.imag >= 0 else "-")
                    s.append(self.imag_post)
                    if self.imag_before:
                        # Imaginary unit before number
                        s.append(self.imag_unit)
                        s.append(self.imag_sep)
                        s.append(self._sig(abs(x.imag), digits))
                    else:
                        # Imaginary unit after number
                        s.append(self._sig(abs(x.imag), digits))
                        s.append(self.imag_sep)
                        s.append(self.imag_unit)
                else:
                    # It's a real number
                    s.append(self._sig(x.real, digits))
            else:
                # Real part is effectively zero
                if not ignore_imag:
                    # It's pure imaginary
                    # Put the sign first if it's needed
                    if self.sign:
                        s.append("+" if x.imag > 0 else "-")
                    else:
                        if x.imag < 0:
                            s.append("-")
                    if self.imag_before:
                        # Imaginary unit before number
                        s.append(self.imag_unit)
                        s.append(self.imag_sep)
                        s.append(self._sig(abs(x.imag), digits))
                    else:
                        # Imaginary unit after number
                        s.append(self._sig(abs(x.imag), digits))
                        s.append(self.imag_sep)
                        s.append(self.imag_unit)
                else:
                    # It's zero
                    s.append(self._sig(0, digits))
        return ''.join(s)

    def _sig(self, x, digits):
        '''Format the number x to digits significant figures.  
        digits can be an int, Decimal, Fraction, or a float (if a
        float, it is first converted to a Fraction; then
        _TemplateRound will convert it to a Decimal.  If digits is not
        an int, then digits is used for the method _TemplateRound.
        '''
        x_types = [Dec, Fraction, int, long, float, _Complex]
        # The following is an attribute so _sig_complex can use it too
        self.digits_types = [Dec, Fraction, int, float]
        if _have_mpmath:
            x_types.append(mp.mpf)
            self.digits_types.append(mp.mpf)
        x_types, self.digits_types = tuple(x_types), tuple(self.digits_types)
        # Check types
        if isinstance(x, complex):
            x = _Complex(x)
        elif isinstance(x, (int, long)) and self.integer > 0:
            if self.integer > 1:
                return self._fmt_int(x)
            else:
                return str(x)
        elif self._is_iterable(x):
            raise ValueError("Bug:  x is an iterable")
        elif digits <= 0:
            raise ValueError("digits must be > 0")
        elif not isinstance(x, x_types):
            raise ValueError("Bad type for x")
        elif not isinstance(digits, self.digits_types):
            raise ValueError("Bad type for digits")
        # If x is complex, another function handles it
        if isinstance(x, _Complex):
            return self._sig_complex(x, digits)
        # If we're fitting to a given space, digits must be an int
        if self._fit and not isinstance(digits, int):
            msg = "digits must be an integer if fit is nonzero"
            raise ValueError(msg)
        # If digits is not an integer, then use template rounding
        if not isinstance(digits, (int, long)):
            return self._TemplateRound(x, digits)
        # Make sure x is a Decimal object
        if isinstance(x, float):
            if x == float("-0.0"):
                x = Dec("0.0").normalize()
            else:
                x = Fraction.from_float(x)
        if isinstance(x, (int, long)):
            x = Dec(x)
        elif _have_mpmath and isinstance(x, mp.mpf):
            x = Dec(str(x))
        elif isinstance(x, Fraction):
            x = Dec(x.numerator)/Dec(x.denominator)
        assert isinstance(x, Dec)
        # From here on, x is a Decimal object
        if self._fit:
            absfit = abs(self._fit)
            dgts, s, none = digits, self._format(x, digits), "None"
            if self._fit and self.dp_position:
                return self.AlignDP(x, width=self._fit, 
                    position=self.dp_position, digits=digits)
            if self._fit < 0:
                none = none.ljust(absfit)
            else:
                none = none.rjust(absfit)
            if len(none) > absfit:
                none = none[:absfit]
            has_dp = self.dp in s
            if len(s) <= absfit:
                return self._justify(s, self._fit)  # More spaces than needed
            while len(s) > absfit:
                # Need to chop off some significant digits
                dgts -= 1
                if dgts == 0:
                    break
                if has_dp and self.dp not in s:
                    return none # Cannot be made to fit
                s = self._format(x, dgts)
                # The following is needed when dgts is 1 because the
                # decimal point may be removed.
                s = self._justify(s, self._fit)
            if not dgts:
                return none     # Cannot be made to fit
            else:
                # Fit was OK
                return s
        else:
            return self._format(x, digits)

    def _format(self, x, digits):
        '''This method does the actual formatting.
        '''
        if _have_mpmath:
            if not isinstance(x, (Dec, mp.mpf)):
                raise ValueError("x must be a Decimal or mpmath.mpf")
        else:
            if not isinstance(x, Dec):
                raise ValueError("x must be a Decimal")
        if not isinstance(digits, (int, long)):
            raise ValueError("digits must be an integer")
        # Handle the special case of None
        if x is None and not self.ignore_none:
            msg = "Argument cannot be None (use 'ignore_none' keyword?)"
            raise ValueError(msg)
        # See if this number is less than our zero threshold
        if self.zero_limit and abs(float(x)) <= self.zero_limit:
            x = Dec(0)
        # Handle the special case of 0.  Note we don't distinguish
        # between +0 and -0, even though this is possible for Decimal
        # objects (mpmath 0.12 ignores negative zeros).
        if not x or x is None:
            s = "0" + self.dp 
            if digits > 1:
                for i in range(digits - 1):
                    s += "0"
            if s == "0" + self.dp and not self.idp:
                s = s[:-1]
            if self.sign:
                s = "+" + s
            return self._Rtz(s)
        # Remember the sign of x
        if self.sign:
            sgn = "+" if (x >= 0) else "-"
        else:
            sgn = "" if (x >= 0) else "-"
        ndigits = max(1, int(digits))
        # Get x displayed in exponential format as a string.  The form
        # must be X.XXXXXesDDD where X's are the usual digits of the
        # mantissa, s is +, -, or empty, and DDD represents an integer.
        if _have_mpmath and isinstance(x, mp.mpf):
            # This is an undocumented way of getting an mpmath number in
            # scientific notation.  It works on mpmath 0.12, but it may
            # not work on later versions.
            s = mp.libmpf.to_str(abs(x)._mpf_, ndigits, min_fixed=2, 
                    max_fixed=1, show_zero_exponent=True)
        else: # It's a Decimal number
            e = "{0:.%de}" % (ndigits - 1)
            # Note:  string interpolation is broken in python 2.6.5;
            # this exponential expression will fail when you ask for
            # around 113 digits; this happens both in the .format()
            # method and C-style string interpolation.  Thus, we will
            # raise an exception if we're using a python version less
            # than 2.7 (it works in 2.7 and python 3.2.2).
            if sys.version < "2.7" and digits > 112:
                raise ValueError("Can't format because of python %%e bug")
            s = str(e.format(abs(x)))
        # Now s is in the X.XXXesDDD form; split it apart and process
        # the pieces separately.
        mantissa, exponent = s.split("e")
        exponent = int(exponent)
        if self.esign:
            exp = "%+0*d" % (self.edigits + 1, exponent)  # Add 1 for sign character
        else:
            exp = "%0*d" % (self.edigits, exponent)
        if exponent == 0:
            # This is needed for mpmath's buggy to_str
            dig = ndigits + 1 if ("." in mantissa) else ndigits
            while len(mantissa) < dig:
                mantissa += "0"
            if self.idp and "." not in mantissa:
                mantissa += "."
            return self._Rtz(sgn + mantissa.replace(".", self.dp))
        if abs(x) <= self._low or abs(x) >= self._high:
            s = sgn + mantissa + self.echar + exp
            return self._Rtz(s.replace(".", self.dp))
        mantissa = mantissa.replace(".", "")
        # Add extra 0's if our length isn't proper (this is needed
        # sometimes for mpmath numbers, as their to_str
        # routine has a bug).
        while len(mantissa) < ndigits:
            mantissa += "0"
        if self.lead_zero:
            z = [("0" + self.dp) if (exponent < 0) else mantissa]
        else:
            z = [self.dp if (exponent < 0) else mantissa]
        if exponent < 0:   # Shift decimal point left
            num_zeros = abs(exponent) - 1
            self._append_zeros(z, num_zeros)
            z.append(mantissa)
            return self._Rtz(sgn + ''.join(z))
        else:       # Shift decimal point right
            num_zeros = exponent - len(mantissa) + 1
            if num_zeros < 0:
                return self._Rtz(sgn + mantissa[:num_zeros] + self.dp + 
                        mantissa[num_zeros:])
            self._append_zeros(z, num_zeros)
            if self.idp:
                z.append(self.dp)
            return self._Rtz(sgn + ''.join(z))

    def push(self):
        '''Push the current attributes onto a stack.  Remove and use
        them with the pop() method.
        '''
        self.stack.append(self.__dict__.copy())

    def pop(self, n=1):
        '''Note it's not an error to pop past the end of the stack.
        '''
        if isinstance(n, (str, unicode)) and n == "all":
            n = len(self.stack)
        for i in range(n):
            try:
                self.__dict__ = self.stack.pop()
            except IndexError:
                pass

    def _Rtz(self, s):
        '''Remove trailing zeros from the string s if self.rtz is
        True and s contains a decimal point (so we don't mess
        up integers).
        '''
        if not self.rtz:
            return s
        while s[-1] == "0" and self.dp in s:
            s = s[:-1]
        return s

    def AlignDP(self, num, width=None, position=None, digits=None):
        '''Fit the string into a stated width with the decimal point
        at the 0-based position starting from the left.  width
        overrides the self.fit setting; position overrides the
        self.dp_position setting.  Note the number significant figures
        in the result may be reduced to get it to fit into the given
        space.
        
        The intent is to let you have a field of known width where the
        decimal points line up -- this is useful when displaying
        information that varies over a few orders of magnitude.  The
        routine will display "-.-" for numbers outside the displayable
        range.
        
        Algorithm:
 
            0 1 2 3 4 5 6 7 8 9
           +-------------------+
           | | | | | |.| | | | |
           +-------------------+
                      ^
                      |
                      dp
           |<----------------->| = w
 
        String index of decimal point = dp
        Width of whole string = w
        Number of spots to left of decimal place  = dp
        Number of spots to right of decimal place = r = w - dp - 1
 
        Allowed forms:
            1.  sig with a decimal point
            2.  sig with no decimal point
        Scientific format isn't allowed, so if the number can't fit
        in the given space, "-.-" is displayed.
 
        Numbers displayable are:
            if x < 1:
                abs(x) > 10**r
            else:
                x < 10**dp - 10**(-r)
                and
                x > -(10**(dp - 1) - 10**(-r)
        '''
        # Check parameters
        if width is None:
            if not self.fit:
                raise ValueError("fit must be > 0")
            w = self.fit
        else:
            w = width
        if position is None:
            if not self.dp_position:
                raise ValueError("dp_position must be > 0")
            dp = self.dp_position
        else:
            dp = position
        bad = "0. " if num == Dec(0) else "-.-"
        if not isinstance(num, Dec):
            # Convert to a Decimal number
            if isinstance(num, (int, long)):
                num = Dec(num)
            elif isinstance(num, float):
                num = Dec(repr(num))
            elif isinstance(num, mp.mpf):
                num = Dec(str(num))
            else:
                raise ValueError("Number num must be convertible to Decimal")
        assert isinstance(num, Dec)
        r, displayable = w - dp - 1, True
        # Determine if number is displayable
        ten = Dec(10)
        q = ten**(-r)
        if num < 1:
            if abs(num) < q:
                displayable = False
        else:
            if not (-(ten**(dp - 1) - q) <= num <= (ten**dp - q)):
                displayable = False
        if not displayable:
            s = " "*(dp - 1) + bad + " "*(r - 1)
            if len(s) <= w:
                return s
            raise ValueError("width of %d too small" % w)
        digits = digits if digits is not None else self.digits
        # Number is displayable, so find a number of digits that allow
        # self.sig() to be displayed in the given space.
        decimal_point = locale.localeconv()["decimal_point"]
        exponent_character = self.echar
        for dgts in range(digits, 0, -1):
            s = self._format(num, dgts)
            loc = s.find(decimal_point)
            if loc == -1:
                s = s + decimal_point
                loc = s.find(decimal_point)
            while loc < dp:
                s = " " + s
                loc = s.find(decimal_point)
            right = len(s) - loc - 1
            while right < r:
                s += " "
                right = len(s) - loc - 1
            if exponent_character in s:
                raise ValueError("Number %s requires sci()" % num)
            if len(s) == w:
                # We've found the proper expression, so just return it
                return s
        # Not displayable
        s = " "*(dp - 1) + bad + " "*(r - 1)
        if len(s) <= w:
            return s
        raise ValueError("width of %d too small" % w)

    def _convert_to_array(self, x):
        '''Return None if x isn't a string and can't be converted to
        an array of numbers.  Otherwise return a list of the numbers.
        '''
        def clean(x):
            sp = " "
            x = x.lower().strip()
            x = x.replace("i", "j")
            x = x.replace(",", sp)
            x = x.replace(";", sp)
            x = x.replace("\n", sp)
            return x.strip()
        if not isinstance(x, (str, unicode)):
            return None
        x = clean(x)
        if " " in x:
            s = []
            for i in x.split():
                n = self._convert_number(i, name="string_array")
                s.append(n)
            return s
        return None

    def _append_zeros(self, z, num_zeros):
        while num_zeros:
            z.append("0")
            num_zeros -= 1

    def _justify(self, s, spaces):
        '''While len(s) < spaces, add space characters until len(s) ==
        spaces.  If spaces > 0, prepend; otherwise, append.
        '''
        if spaces > 0:
            while len(s) < spaces:
                s = " " + s
        else:
            while len(s) < abs(spaces):
                s += " "
        return s

    def _seq(self, x, digits):
        '''x is an iterable and should contain number objects.  We'll
        recursively process the contained components.  Since this
        method can be called recursively, the stopping point is when x
        is not an iterable and is thus a string that can be converted
        to a number or an acceptable number type.
        '''
        # Stop recursion:  if x is not an iterable, let _sig() handle it.
        if not self._is_iterable(x):
            if _have_uncertainties and (isinstance(x, unc.Variable) or 
                    isinstance(x, unc.AffineScalarFunc)):
                return self._sig_uncertainty(x, digits)
            else:
                return self._sig(self._convert_number(x, "x in _seq"), digits)
        # It's an iterable, so call ourself recursively
        if self._fit:
            raise ValueError("fit can't be used with sequence")
        s = [self._seq(i, digits) for i in x]   # Recursive call
        if isinstance(x, tuple):
            s = tuple(s)
        s = str(s).replace("'", "") # Remove apostrophes from strings
        s = s.replace(", ", self.separator)
        if isinstance(x, dict):
            s = s.replace("[", "{")
            s = s.replace("]", "}")
        return s

    def check(self):
        '''Check our attributes for allowed values and types.  This
        method is run in the constructor, but isn't used after that
        (this was done intentionally to avoid a performance overhead).
        If you are getting an exception while using sig or SigFig, run
        this method and it may point you to the cause of the problem.
        '''
        #---------------------------------------------------------
        # Check types
        # _digits is special because it can be either an integer or a
        # float type.
        try:
            self._check_float(self._digits, "digits")
        except TypeError:
            pass
        else:
            if not isinstance(self._digits, int):
                msg = "_digits attribute is not an integer or float"
                raise TypeError(msg)
        # Floats
        for var, name, none_allowed in (
            (self._digits,    "digits",     False),
            (self._high,      "high",       False),
            (self._low,       "low",        False),
            (self.zero_limit, "zero_limit", False),
            (self.imag_limit, "imag_limit", True),
        ):
            self._check_float(var, name, none_allowed=none_allowed)
        # Integers
        for var, name in (
            (self.dp_position, "dp_position"),
            (self.edigits,     "edigits"),
            (self._fit,        "fit"),
            (self._integer,    "integer"),
            (self.unc_digits,  "unc_digits"),
        ):
            if not isinstance(var, (int, long)):
                msg = "{0} attribute is not an integer".format(name)
                raise TypeError(msg)
        # Booleans
        for var, name in (
            (self.esign,       "esign"),
            (self.idp,         "idp"),
            (self.ignore_none, "ignore_none"),
            (self.lead_zero,   "lead_zero"),
            (self.imag_before, "imag_before"),
            (self.imag_polar,  "imag_polar"),
            (self.imag_deg,    "imag_deg"),
            (self.imag_pair,   "imag_pair"),
            (self.mixed,       "mixed"),
            (self.rtz,         "rtz"),
            (self.unc_short,   "unc_short"),
        ):
            if not isinstance(var, bool):
                msg = "{0} attribute is not a Boolean".format(name)
                raise TypeError(msg)
        # Strings
        for var, name in (
            (self.dp,              "dp"),
            (self.echar,           "echar"),
            (self.imag_deg_sym,    "imag_deg_sym"),
            (self.imag_pair_left,  "imag_pair_left"),
            (self.imag_pair_right, "imag_pair_right"),
            (self.imag_pair_sep,   "imag_pair_sep"),
            (self.imag_polar_sep,  "imag_polar_sep"),
            (self.imag_post,       "imag_post"),
            (self.imag_pre,        "imag_pre"),
            (self.imag_sep,        "imag_sep"),
            (self.imag_unit,       "imag_unit"),
            (self.separator,       "separator"),
            (self.unc_sep,         "unc_sep"),
            (self.unc_pre,         "unc_pre"),
            (self.unc_post,        "unc_post"),
        ):
            if not isinstance(var, (str, unicode)):
                msg = "{0} attribute is not a string".format(name)
                raise TypeError(msg)
        #---------------------------------------------------------
        # Check constraints on values.  Float objects will be
        # converted to Decimal or Fraction objects.
        self._digits = self._convert_number(self._digits, "digits")
        if self._digits <= 0:
            raise ValueError("digits attribute must be > 0")
        self._high = self._convert_number(self._high, "high")
        self._low = self._convert_number(self._low, "low")
        # Other attributes
        if self.edigits < 1:
            raise ValueError("edigits attribute must be > 0")
        # Use absolute values
        self.zero_limit = abs(self._convert_number(self.zero_limit))
        self.imag_limit = abs(self._convert_number(self.imag_limit))
        #---------------------------------------------------------
        # Final inspection
        # Booleans
        assert isinstance(self.esign,       bool)
        assert isinstance(self.idp,         bool)
        assert isinstance(self.ignore_none, bool)
        assert isinstance(self.lead_zero,   bool)
        assert isinstance(self.mixed,       bool)
        assert isinstance(self.rtz,         bool)
        assert isinstance(self.sign,        bool)
        assert isinstance(self.unc_short,   bool)
        # Floats, Fractions, or integers
        flt = [float, Dec, Fraction, int]
        if _have_mpmath:
            flt += [mp.mpf]
        flt = tuple(flt)
        assert isinstance(self._digits,     flt)
        assert isinstance(self._high,       flt)
        assert isinstance(self._low,        flt)
        assert isinstance(self.imag_limit,  flt)
        assert isinstance(self.zero_limit,  flt)
        # Integers
        assert isinstance(self.edigits,     (int, long))
        assert isinstance(self._fit,        (int, long))
        assert isinstance(self._integer,    (int, long))
        assert isinstance(self.unc_digits,  (int, long))
        # Strings
        assert isinstance(self.dp,          (str, unicode))
        assert isinstance(self.echar,       (str, unicode))
        assert isinstance(self.imag_post,   (str, unicode))
        assert isinstance(self.imag_pre,    (str, unicode))
        assert isinstance(self.imag_sep,    (str, unicode))
        assert isinstance(self.imag_unit,   (str, unicode))
        assert isinstance(self.separator,   (str, unicode))
        assert isinstance(self.unc_sep,     (str, unicode))
        assert isinstance(self.unc_pre,     (str, unicode))
        assert isinstance(self.unc_post,    (str, unicode))

    def _is_iterable(self, x):
        '''Identify an iterable by its behavior.  Note:  we define a
        string as a non-iterable because it's not a container of number
        objects.
        '''
        try:
            for i in x:
                break
            if isinstance(x, (str, unicode)):
                return False
            return True
        except TypeError:
            return False

    def __str__(self):
        s = ["SigFig object at 0x" + hex(id(self)) + ":"]
        d = self.__dict__.copy()
        keys = d.keys()
        maxlen = max([len(i) for i in keys])
        # Remove names with underscores
        for key in keys:
            if key[0] == "_":
                old = key
                key = key[1:]
                d[key] = d[old]
                del d[old]
        # Build output array
        keys = list(d.keys())
        keys.sort()
        maxlen = max([len(i) for i in keys])
        for key in keys:
            s.append("  {0:{1}} = {2}".format(key, maxlen, repr(d[key])))
        return '\n'.join(s)

    def _check_float(self, val, name, none_allowed=False):
        '''Raise a TypeError exception if val is not an object type
        that can be converted to a Decimal or Fraction object.  Note
        we do not do the conversion here.  If none_allowed is True, we
        accept a value of None.
        '''
        if none_allowed and val is None:
            return
        if _have_mpmath and isinstance(val, mp.mpf):
            return
        if not isinstance(val, (float, int, long, str, unicode, Dec, Fraction)):
            msg = "{0} attribute is improper type".format(name)
            raise TypeError(msg)

    def _convert_fraction(self, val):
        '''val is a Fraction object; convert it to a Decimal object.
        '''
        if not isinstance(val, Fraction):
            raise TypeError("Argument must be a Fraction")
        return Dec(val.numerator)/Dec(val.denominator)

    def _convert_number(self, val, name=""):
        '''Return val as a Decimal, int, or _Complex.
        '''
        def FloatToDec(value):
            # Conversion of a float to a Decimal number isn't
            # trivial.  I've provided a number of different
            # algorithms; pick which one you want to use or write
            # your own.
            algorithm = "strip zeros" 
            if algorithm == "fraction":
                # First convert to a fraction, then the fraction to a
                # Decimal.  Can result in lots of digits.
                retval = Fraction.from_float(val)
                retval = Dec(retval.numerator)/Dec(retval.denominator)
            elif algorithm == "Decimal FAQ":
                # Recipe from python 2.6.5 Decimal FAQ.  Can
                # result in lots of digits.
                n, d = val.as_integer_ratio()
                numerator, denominator = Dec(n), Dec(d)
                with decimal.localcontext() as ctx:
                    ctx.prec = 60
                    retval = ctx.divide(numerator, denominator)
                    while ctx.flags[decimal.Inexact]:
                        ctx.flags[decimal.Inexact] = False
                        ctx.prec *= 2
                        retval = ctx.divide(numerator, denominator)
                retval = +retval
            elif algorithm == "easy":
                # This is the easiest to program
                retval = Dec(str(val))
            elif algorithm == "strip zeros":
                # Use a context of 16 digits to roughly match that
                # of floats (assuming IEEE-754 numbers).  Then
                # remove any trailing zeros.
                n, d = val.as_integer_ratio()
                with decimal.localcontext() as ctx:
                    prec = 16
                    ctx.prec = prec
                    retval = Dec(n)/Dec(d)
                    while ctx.prec > 1 and str(retval)[-1] == "0":
                        ctx.prec -= 1
                        retval = +retval
                retval = +retval
            else:
                raise ValueError("Bad algorithm choice")
            return retval
        #
        retval = val
        if isinstance(val, (str, unicode)):
            if "/" in val:  
                # Allow proper AND mixed fractions (otherwise we'd
                # just use the Fraction() constructor).
                retval = self._ConvertFractionToDecimal(val)
            elif "j" in val:  
                retval = _Complex(complex(val))
            else:
                try:
                    retval = Dec(val)
                except decimal.InvalidOperation:
                    msg = "'{0}' can't be converted to Decimal"
                    raise ValueError(msg.format(name))
        elif isinstance(val, _Complex):
            pass
        elif isinstance(val, complex):
            retval = _Complex(val)
        else:
            if val is None:
                if self.ignore_none:
                    retval = Dec(0)
                else:
                    msg = "x can't be None (use ignore_none attribute?)"
                    raise ValueError(msg)
            elif isinstance(val, float):
                retval = FloatToDec(val)
            elif isinstance(val, (Dec, int, long)):
                pass
            elif isinstance(val, Fraction):
                retval = Dec(val.numerator)/Dec(val.denominator)
            elif _have_uncertainties and isinstance(val, unc.Variable):
                retval = Dec(str(val.nominal_value))
            else:
                msg = '''
Bug:  unrecognized type for {0}
  Value = {1}
'''[1:-1]
                msg = msg.format(name, repr(val))
                if _have_mpmath:
                    if isinstance(val, mp.mpf):
                        retval = Dec(str(val))
                    elif isinstance(val, mp.mpc):
                        # Take real part
                        retval = Dec(str(val.real))
                    else:
                        raise RuntimeError(msg.format(name, repr(val)))
                else:
                    raise RuntimeError(msg.format(name, repr(val)))
        if not isinstance(retval, (Dec, int, long, _Complex)):
            raise TypeError("Bug:  not Decimal, int, long, or _Complex")
        return retval
    
    def _ConvertFractionToDecimal(self, x):
        '''x is a string that contains '/'.  Convert it to a Decimal
        floating point type (Decimal is used to not lose any
        precision).  fraction.  It must be one of the following forms:
     
            a/b         Improper fraction
            a-b/c       Mixed fraction
            a+b/c       Mixed fraction
     
        Note the + or - signs are NOT interpreted as arithmetic
        operators; they are just used to separate the integer and
        fractional parts.
        '''
        x = x.strip()
        if not x:
            raise ValueError("Empty string")
        if "/" not in x:
            raise RuntimeError("Bug:  '/' expected in the string x")
        msg = "'%s' is not a proper fractional form" % x
        try:
            sign = 1
            if x[0] == "-":
                sign = -1
                x = x[1:]
            elif x[0] == "+":
                x = x[1:]
            if "-" in x:
                intpart, fracpart = x.split("-")
            elif "+" in x:
                intpart, fracpart = x.split("+")
            else:
                # It's an improper fraction
                intpart, fracpart = "0", x
            num, denom = [int(i) for i in fracpart.split("/")]
            return sign*(Dec(int(intpart)) + Dec(num)/Dec(denom))
        except ValueError:
            raise ValueError(msg)

    def _set_digits(self, digits):
        if isinstance(digits, (int, long)): 
            if digits < 1:
                raise ValueError("If an integer, digits must be >= 1")
            else:
                self._digits = digits
        else:
            types = (str, float, Dec, Fraction)
            types_s = "(str, float, Dec, Fraction)"
            if _have_mpmath:
                types = (str, float, Dec, mp.mpf, Fraction)
                types_s = "(str, float, Dec, mpmath.mpf, Fraction)"
            if not isinstance(digits, types):
                msg = "digits must be one of: {0}"
                raise TypeError(msg.format(types_s))
            else:
                self._digits = self._convert_number(digits, "digits")
            if self._digits <= 0:
                raise ValueError("digits must be > 0")

    def _get_digits(self):
        return self._digits

    digits = property(_get_digits, _set_digits, doc='''
Set number of significant digits.  Must be a number that can be
converted to an integer > 0.
'''.strip())

    def _set_low(self, low):
        self._low = self._convert_number(low, "low")

    def _get_low(self):
        return self._low

    low = property(_get_low, _set_low, doc="Set low")

    def _set_high(self, high):
        self._high = self._convert_number(high, "high")

    def _get_high(self):
        return self._high

    high = property(_get_high, _set_high, doc="Set high")

    def _set_fit(self, fit):
        if not isinstance(fit, (int, long)):
            raise ValueError("fit must be an integer")
        self._fit = fit

    def _get_fit(self):
        return self._fit

    fit = property(_get_fit, _set_fit, doc="Set fit")

    def _get_decimal(self, x, name=""):
        '''Convert x to a Decimal type.
        '''
        T = x
        if isinstance(x, (str, unicode)):
            if "/" in x:
                T = self._ConvertFractionToDecimal(x)
            else:
                T = Dec(x)
        elif isinstance(x, Dec):
            pass
        elif isinstance(x, float):
            T = self._convert_number(x, name)
        elif isinstance(x, (int, long)):
            T = Dec(x)
        elif isinstance(x, Fraction):
            T = Dec(x.numerator)/Dec(x.denominator)
        else:
            if _have_mpmath and isinstance(x, mp.mpf):
                T = Dec(str(x))
            else:
                msg = "'{0}' is an unsupported type"
                raise TypeError(msg.format(name))
        return T

    def _TemplateRound(self, x, template):
        '''Rounds a number x to the nearest value specified by template.
        Example:  if x = 1.234 and template = 0.05, the rounded value
        will be 1.25.
 
        We allow template to be an integer, although the _sig routine
        will never call us with an integer template because the
        integer will be specifying the number of significant figures.
 
        template can also be a fraction.  If you change how the string
        is displayed, be aware that you might want the fraction to
        represent a valid python expression.  Thus, "1+3/16" will
        evaluate to what you expect.
        '''
        # Note there's an apparent bug in the Decimal objects.  This
        # occurs under python 2.6.5, 2.7.2, and 3.2.2.  Use the
        # following code to demonstrate it:
        # x = 50.465
        # for i in range(4, 10):
        #     print i, sig(x, 10**(-i))
        #
        # The results are:
        #   4 50.4650
        #   5 50.46500
        #   6 50.465000
        #   7 50.4650000000000000000000
        #   8 50.46500000000000000000000
        #   9 50.465000000000000000000000
        #
        # Note the disparity in the difference between the 6 and 7
        # case.
        x = self._get_decimal(x, name="x")
        sign = 1 if x >= 0 else -1
        if isinstance(template, Fraction):
            xf = template.from_decimal(x)  # x as a fraction
            numer = Fraction(int(abs(xf)/template + Fraction(1, 2)), 1)
            if self.mixed:
                n = numer*template
                integer, remainder = divmod(n.numerator, n.denominator)
                if not remainder:
                    s = "%d" % integer
                else:
                    # This is where the fraction's display is
                    # determined
                    if integer:
                        s = "%d+%s" % (integer, Fraction(remainder, n.denominator))
                    else:
                        s = "%s" % Fraction(remainder, n.denominator)
                if sign == -1:
                    # If x is negative, we'll put parentheses around
                    # it, as this is a bit less confusing.
                    s = "-(" + s + ")"
                return s
            else:
                return str(sign*numer*template)
        else:
            T = self._get_decimal(template, name="template")
            return str(sign*int(abs(x)/T + Dec("0.5"))*T)

    def Interpret(self, S, fp_type=float, 
                  glo=None, loc=None, strict=True):
        '''This is a general routine to interpret a string S as a
        number or an assignment.  Examples of the allowed forms for S
        are:
 
            34 u            Integer
            3.4u            Floating point
            3.4[0.1]u       Mean 3.4 with uncertainty of 0.1
            3.4+-0.1 u      Mean 3.4 with uncertainty of 0.1
            3.4+/-0.1u      Mean 3.4 with uncertainty of 0.1
            3.4(1) u        Short form uncertainty 3.4+-0.1
            3 = 4           Assignment (strict = False), no unit
            a = 4           Assignment (strict = True), no unit
            a = b*c/d       Assignment (strict = True) w/ expr, no unit
            b*c/d           Expression (no unit allowed)
 
        All whitespace is removed from S before processing, so
        "number" forms like "3 . 4" or "3. 4 (  1 ) e- 4 m/s" would be
        evaluated as expected.
 
        The numbers can include an optional string u that will be
        interpreted as the physical units of the number.  A number
        will first be interpreted as an integer; if that fails, then
        it will be interpreted as a floating point type of fp_type.
        Numbers with uncertainties will become ufloats from the
        uncertainties module if it is present; otherwise, the
        uncertainty is ignored.  Note the units string u can have 
        optional whitespace between it and the number part of the
        string.
 
        The units string u should not contain any of the characters
        "()[]"; if it does, then this routine may fail to properly
        interpret the whole string.  No units are allowed in
        assignments or expressions because they are evaluated by the
        python interpreter.
 
        The routine returns a tuple (x, u) where
 
            1.  x is an int, u is unit
            2.  x is an fp_type, u is unit
            3.  x is a ufloat, u is unit
            4.  x is assigned name, u is value
            5.  x is None, u is an error message
 
        The assignment is interpreted and if the loc dictionary is not
        None, this assignment is put into that dictionary.  If strict
        is True, then assignment can only be to names that are valid
        python identifiers; this allows them to be used e.g. in
        subsequent expression evaluations because the expressions are
        evaluated with the glo dictionary as globals and the loc
        dictionary as locals.
 
        If you use the uncertainty notation but the uncertainties
        module isn't installed, the uncertainty portion will just be
        ignored.
 
        This routine may look like a "kitchen sink" utility, but I
        wrote it because it captures the behaviors I need for getting
        input from users in my programs.  The ability to define
        variables, evaluate python expressions, and define numbers
        with uncertainty covers virtually all of the cases I need for
        numerical input from a user (except for complex numbers).
 
        Note there's a "cost" associated with this routine:  some
        things that are not valid numbers can be interpreted as
        numbers with units.  For example, the string "3.4.4" will be
        interpreted as the floating point number 3.4 with an
        uncertainty string of ".4".
 
        Here's an outline of the algorithm used.  If the string s
        contains "[", "]", "(", ")", "+-", or "+/-", then it is picked
        apart as an uncertainty.  If it has an "=" sign in
        it, it is evaluated as an assignment.  Otherwise, a conversion 
        to an int or fp_type is attempted.  If that fails, then it is
        interpreted as an expression.
        '''
        # Remove all whitespace from S
        s = re.sub(r"\s", "", S)
        # Check to see if it's an expression, as it could contain the
        # characters "()[]=" which we'll subsequently use to identify
        # uncertainties or an assignment.  Note we evaluate s, not S.
        # Also, we won't try to interpret it as an expression unless
        # fp_type is float; this is because passing in a string like
        # "3.4" would evaluate correctly as an expression, but if
        # fp_type was decimal.Decimal, it would be evaluated here, not
        # further down the food chain like it should.
        if fp_type == float:
            try:
                val = eval(s, glo, loc)  # Evaluate the input string verbatim
                return (val, "")
            except Exception:
                pass
        if "=" in S:
            # It's an assignment.  Split the string at the location of
            # the first '=' character.  Note we use the input string
            # verbatim rather than s with the whitespace removed.
            L = S.find("=")
            name, valstring = S[:L].strip(), S[L + 1:].strip()
            if not name:
                return (None, "Assignment to empty name")
            if not valstring:
                return (None, "Assignment with empty right-hand side")
            try:
                val = eval(valstring, glo, loc)
                if strict:
                    # Make sure name is a valid python identifier by
                    # trying to make it a local variable.
                    try:
                        t = compile("%s = val" % name, "", "single")
                        exec(t)
                    except Exception:
                        msg = "'%s' not a valid python name" % name
                        return (None, msg)
                # Add to the loc dictionary if it is present
                if loc is not None:
                    loc[name] = val
                return (name, val)
            except Exception as e:
                msg = "Could not interpret expression '%s':" % valstring
                msg += "\n  Error:  %s" % str(e)
                return (None, msg)
        elif re.search(r"\(\d+\)", s):
            # It's a number with a short-form uncertainty
            mo = self.r_short.match(s)
            if mo:
                g = list(mo.groups())
                if not g[1]:
                    g[1] =  "0"
                sgn    = -1 if g[0] == "-" else 1
                lead   = g[1]
                dp     = g[2]
                trail  = g[3]
                uncert = g[4].replace("(", "").replace(")", "")
                expon  = g[5][1:] if g[5] is not None else "0"
                unit   = g[6]
                if 0:
                    # The older method was to pick apart the incoming
                    # string.  I've replaced this with the algorithm
                    # of just grabbing the unit string, then letting
                    # the uncertainties module interpret the number.
                    # This code is left here in case a bug in the
                    # uncertainty module's parsing is discovered
                    # later.
                    if not lead and not trail:
                        return (None, "No digits on either side of decimal point")
                    # We need to multiply the uncertainty integer by the
                    # number representing the least significant digit of the
                    # significand.  This is actually easy, as it's
                    # 1/10**len(trail).
                    significand = lead + dp + trail
                    power = 10**int(expon)
                    uncertainty = int(uncert)/10**len(trail)
                    if _have_uncertainties:
                        mean = sgn*float(significand)*power
                        x = unc.ufloat(mean, uncertainty*power)
                    else:
                        sgn = g[0] if g[0] is not None else ""
                        expon = g[5] if g[5] is not None else ""
                        x = fp_type(''.join([sgn, significand, expon]))
                else:
                    # Change any Nones to empty strings
                    s = ''.join([i for i in g[:6] if i is not None])
                    x = unc.ufloat_fromstr(s)
                return (x, unit.strip())
            else:
                return (None, "Improper short-form uncertainty number")
        elif s.find("[") != -1 or s.find("]") != -1:
            # It's a number with an uncertainty in square brackets
            ll, lr = s.find("["), s.find("]")
            if ll == -1:
                return (None, "Missing left bracket [")
            if lr == -1:
                return (None, "Missing right bracket ]")
            if ll > lr:
                return (None, "Right bracket ] is before left [")
            if lr - ll == 1:
                return (None, "Nothing between brackets")
            try:
                # Pick out what's between the brackets.  Note we allow
                # '%' and 'u' inside the brackets; % means the standard
                # deviation is a given percentage of the mean and u
                # means the standard deviation is a given parts per
                # million of the mean.
                ex, fraction = s[ll + 1:lr].strip(), None
                if ex[-1] == "%":
                    fraction = 1e-2
                    ex = ex[:-1]
                elif ex[-1] == "u":
                    fraction = 1e-6
                    ex = ex[:-1]
#yy
                uncertainty = float(eval(ex, glo, loc))
                if _have_uncertainties and uncertainty < 0:
                    return (None, "Uncertainty can't be < 0")
                remainder = s[:ll] + s[lr + 1:]
                # Interpret remainder as a number and unit
                mo = self.r_number.match(remainder)
                if mo:
                    g = mo.groups()
                    mean = eval(g[0], glo, loc)
                    unit = g[3].strip()
                    if _have_uncertainties:
                        if fraction is not None:
                            uncertainty *= mean*fraction
                        x = unc.ufloat(float(mean), uncertainty)
                    else:
                        x = fp_type(mean)
                    return (x, unit)
                else:
                    # It could be an expression, but it must
                    # be without a unit.
                    mean = float(eval(remainder, glo, loc))
                    if fraction is not None:
                        uncertainty *= mean*fraction
                    if _have_uncertainties:
                        x = unc.ufloat(mean, uncertainty)
                    else:
                        x = mean
                return (x, "")
            except ValueError:
                return (None, "Can't interpret '%s'" % S)
        elif s.find("+-") != -1 or s.find("+/-") != -1:
            t = s.replace("+/-", "+-") if s.find("+/-") != -1 else s
            f = t.split("+-")
            if len(f) != 2:
                return (None, "Can't interpret '%s'" % S)
            mean, remainder = f
            try:
                # Interpret remainder as a number and unit
                mo = self.r_number.match(remainder)
                if mo:
                    g = mo.groups()
                    uncertainty = g[0]
                    unit = g[3].strip()
                    if _have_uncertainties:
                        x = unc.ufloat(float(mean), float(uncertainty))
                    else:
                        x = fp_type(mean)
                    return (x, unit)
                return (None, "Can't interpret '%s'" % S)
            except ValueError:
                return (None, "Can't interpret '%s'" % S)
        else:
            # It's either an integer or float with optional unit.
            # Note it could also be a string like "1(.1)", which would
            # not have been recognized by the r_short regular
            if "(" in s or ")" in s:
                # Note this means you can't use parentheses in the
                # units string.
                return (None, "Can't interpret '%s'" % S)
            mo = self.r_number.match(s)
            if mo:
                g = mo.groups()
                value = g[0]
                unit = g[3].strip()
                try:
                    return (int(value), unit)
                except ValueError:
                    return (fp_type(value), unit)
            return (None, "Can't interpret '%s'" % S)

#---------------------------------------------------------------------------
class _Complex(object):
    '''Container class for complex numbers.  We handle python complex
    numbers and mpmath complex numbers.
    '''
    def __init__(self, *par):
        s = SigFig()
        if len(par) == 1:   # Single number object
            x = par[0]
            if _have_mpmath and isinstance(x, mp.mpc):
                # mpmath complex number
                self._real = s._convert_number(x.real)
                self._imag = s._convert_number(x.imag)
            elif isinstance(x, complex):
                self._real = s._convert_number(x.real)
                self._imag = s._convert_number(x.imag)
            elif isinstance(x, _Complex):
                self._real = x._real
                self._imag = x._imag
            else:
                raise TypeError("Argument must be a complex number")
        elif len(par) == 2:  # Re & Im components
            self._real = s._convert_number(par[0])
            self._imag = s._convert_number(par[1])
    def _get_real(self):
        return self._real
    def _get_imag(self):
        return self._imag
    real = property(_get_real, None, doc="Returns real part")
    imag = property(_get_imag, None, doc="Returns imag part")
    def __str__(self):
        s = []
        s.append(str(self.real))
        if self.imag:
            if self.imag < 0:
                s.append("-")
            else:
                s.append("+")
            t = str(abs(self.imag))
            s.append(t)
            s.append("i")
        return ''.join(s)
    def __repr__(self):
        return "_Complex(" + self.__str__() + ")"

# This definition has to be after _Complex is defined
sig = SigFig()

def nsf(x, rrhz=False, dp="."):
    '''Return an integer counting the number of significant figures in
    the number represented by the string x.  If rrhz is True, then
    also remove any right-hand zeros from the significand before
    counting.  dp is the string used for the decimal point.
 
    Note we allow short-hand uncertainty notation in x also, such
    as 1.234(5)e6 or 1.234[5]e6.
    '''
    # The implementation takes a bit more work than one might
    # think initially.  The basic method is to get the
    # significand, then pick it apart into components around the
    # decimal point.
    def NotOnlyDigits(s):
        '''Return True if s doesn't contain only digits.  Note s
        can be an empty sequence.
        '''
        for i in s:
            if i not in string.digits:
                return True
        return False
    e = ValueError("'%s' is not a proper number" % str(x))
    if not isinstance(x, (str, unicode)):
        raise e
    # Remove leading and trailing whitespace, convert to all lower
    # case, and remove any internal space characters.
    significand = x.strip().lower().replace(" ", "")
    # Get significand (part of number to left of "e" if it's present)
    f = significand.split("e")
    if len(f) > 1:
        exponent = list(f[1])
        if exponent and exponent[0] in "+-":
            del exponent[0]
        if not exponent or NotOnlyDigits(exponent):
            raise e
    significand = f[0]
    if not significand:
        raise e
    # Handle short-hand uncertainty by removing everything to the
    # right of '(' or '[' inclusive.
    loc = significand.find("(")
    significand = significand[:loc] if loc != -1 else significand
    loc = significand.find("[")
    significand = significand[:loc] if loc != -1 else significand
    # Convert to a list to make removals a little easier
    significand = list(significand)
    # Remove leading sign
    if significand[0] in "+-":
        del significand[0]
    # Remove any left-hand zeros
    while (len(significand) > 1 and significand[0] == "0" and
           significand[1] != dp):
        del significand[0]
    # Turn back into a string
    significand = ''.join(significand)
    # Split on the decimal point and process each part separately
    f = significand.split(dp)
    if f == ["", ""]:
        raise e
    if len(f) == 1:
        if NotOnlyDigits(f[0]):
            raise e
        # There was no decimal point, so it's an integer. Remove
        # any right-hand zeros
        significand = list(f[0])
        while len(significand) > 1 and significand[-1] == "0":
            del significand[-1]
        significand = ''.join(significand)
    elif len(f) == 2:
        if NotOnlyDigits(f[0]) or NotOnlyDigits(f[1]):
            raise e
        # There was a decimal point.
        if f[0] == "0":
            # It's of the form 0.dddd...  Remove any leading zeros
            # from the sequence of digits after the decimal point.  We
            # also set f[0] to "" because the leading zero won't be
            # significant.  Note we'll have to specially handle the
            # case where the number was e.g.  "0.0000".
            f[0] = ""
            s = list(f[1])
            while len(s) and s[0] == "0":
                del s[0]
            f[1] = ''.join(s)
            if f == ["", ""]:
                f = ["0", ""]
        # If user requested it, remove right-hand zeros.
        if rrhz:
            s = list(f[1])
            while len(s) and s[-1] == "0":
                del s[-1]
            significand = f[0] + ''.join(s)
        else:
            significand = ''.join(f)
    else:
        raise e
    if not significand:
        raise RuntimeError("Bug in nsf() routine for x = '%s'" % x)
    return len(significand)

# Note:  the polar display of complex numbers needs the atan2 function
# for Decimal numbers.  The following chunk of code is used to provide
# an atan2; it's taken from Amin Al-Juffali's code with some minor
# modifications.  See
# http://pypi.python.org/pypi/AJDecimalMathAdditions/0.2.0.
#
# ---------------------------------------------------------------------------
# AJDecimalMathAdditions V0.2.0
#
# This is a math module to complement the decimal module with additional
# math functions.
#
# Copyright (c) 2007-2008 Amin Al-Juffali.
# All rights reserved.
# Written by Amin Al-Juffali <ajuffali@mac.com>
#
# This software is provided 'as is', without warranty/liability of any kind
# and type that arises from the use of this software.
#
# This module includes the pi() function taken from dmath v0.9.1 module
# and applied some modifications. The copyright for dmath is listed below.
#
# You are licensed to use, copy, modify, merge, publish, distribute,
# sub-license copies of the Software, and to permit persons to whom the Software
# is furnished to do so, subject to the following conditions:
#
# 1- Include the above copyright, liability, license, and conditions in all
# your software.
#
# 2- Include the functional description/documentation, in full, in all your
# software.  functional description/documentation are located above each
# function.
#
# 3- Any of the functions below that will be rewritten in any other language
# (computer or human) shall adhere to the above copyright with all its
# conditions in full.
#
##-------------------------------------------------------------------------------
##dmath v0.9.1
##
##Python math module for Decimal numbers.  All functions should return Decimal
##numbers.  Probably only works with real numbers.
##
##pi, exp, cos, sin from Decimal recipes:
##    http://docs.python.org/lib/decimal-recipes.html
##
##float_to_decimal from Decimal FAQ:
##    http://docs.python.org/lib/decimal-faq.html
##
##Copyright (c) 2006 Brian Beck <exogen@gmail.com>,
##                   Christopher Hesse <christopher.hesse@gmail.com>
##
##Permission is hereby granted, free of charge, to any person obtaining a copy of
##this software and associated documentation files (the "Software"), to deal in
##the Software without restriction, including without limitation the rights to
##use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
##of the Software, and to permit persons to whom the Software is furnished to do
##so, subject to the following conditions:
##
##The above copyright notice and this permission notice shall be included in all
##copies or substantial portions of the Software.
##
##THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
##IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
##FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
##AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
##LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
##OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
##SOFTWARE.
#--------------------------------- Revisions ------------------------------------
# Second version 0.2.0     July 01, 2008
# First  version 0.1.0     May  16, 2007
#--------------------------------------------------------------------------------

D = Dec
_zero, _one, _two, _three, _four = [D(_i) for _i in range(5)]
_nan, _inf = D("NaN"), D("inf")
_precision_increment = 2

#--------------------------------------------------------------------------------
# pi() a modified version of pi() in dmath.py v0.9.1 and
# at http://docs.python.org/lib/decimal-recipes.html
#--------------------------------------------------------------------------------

def pi():
    '''Compute pi to the current precision.
    '''
    with decimal.localcontext() as ctx:
        ctx.prec += _precision_increment
        (lasts, t, s, n, na, d, da, eight, thirty_two) = (_zero,
            _three, _three, _one, _zero, _zero, D(24), D(8), D(32))
        while s != lasts:
            lasts = s
            n, na = n + na, na + eight
            d, da = d + da, da + thirty_two
            t = (t*n)/d
            s += t
    return +s

#--------------------------------------------------------------------------------
# atan() uses the Maclaurin series (nested form) to evaluate the ArcTan of
# a number.
#
#                  x^3      x^5     x^7
# arctan(x) = x - -----  + ----- - ----- ......    (standard series)
#                   3        5       7
#
# if:
#  a = (2K-1)
#  b = (2K+1)
# then:
#  arctan(x) = x * Nested(1- (x^2)*a/b) for k=0 to infinity and abs(x) < 1
#
# The following identities have been used:
#
#   arctan(-x) = -arctan(x)
#   arctan(x)  = Pi/2 - arctan(1/x)
#   arctan(x)  = Pi/6 + arctan(y)    //see note 1
#                  where  y = (x*sqrt(3)-1) / (sqrt(3)+x) and abs(x) < 1
# References:
#  The above formulas and identity were taken from:
#
#     Calculus with Analytic Geometry
#       by Howard Anton
#       1980 Edition
#
#     Engineering Mathematics Handbook 3rd edition
#       by Jan J. Tuma
#
#     Computer Approximations
#      by John Fraser Hart
#      ISBN: 0-88275-642-7
#
#     http://en.wikipedia.org/wiki/List_of_trigonometric_identities
#--------------------------------------------------------------------------------
# Note 1:
#
#  This identity is not in the references above.
#  Here is the proof by Amin Al-Juffali:
#
#  From the following two identities:
#  atan(x) = atan(x) + nPi , where n = 0,[+-]1, [+-]2,.....
#  atan(x) [+-] atan(y) = atan(t) [+-]pi , where t = (x[+-]y)/(1[-+]x*y)
#
#  Rearranging:
#  atan(x) = atan(y) + atan(t) ,  where t = (x-y)/(1+x*y)
#
#  Assume:
#  pi/6 = atan(y)
#
#  Then:
#  y = 1/sqrt(3)
#
#  Substitute y in t:
#  t = (x - 1/sqrt(3)) / (1 + x/sqrt(3))
#  t = (x*sqrt(3) - 1)/sqrt(3)) / (sqrt(3) + x)/sqrt(3))
#  t = (x*sqrt(3) - 1) / (sqrt(3) + x)
#
#  The limit of abs(x) < 1 is the limit imposed by the Maclaurin series used
#  to evaluate the atan below. If you want to test t instead of x, substitute
#  one in above t formula for x and work the algebra. Your final answer should
#  be abs(t) < (2-sqrt(3))
#--------------------------------------------------------------------------------

def _atan(x):
    '''Returns the inverse tangent of x.  x must be a Decimal.
    Returns an angle in radians from -pi/2 to pi/2.
    '''
    if not isinstance(x, Dec):
        raise ValueError("x must be a Decimal number")
    with decimal.localcontext() as ctx:
        ctx.prec += _precision_increment
        if x.is_nan():
            retval = x
        elif x.is_infinite():
            if x < 0:
               retval = -pi()/_two
            else:
               retval = pi()/_two
        else:
            digits = decimal.getcontext().prec
            isNegative, isLargerThenOne = False, False
            temp, Pi = x, pi()
            if temp < +_zero:
                isNegative, temp = True, -temp
            elif temp == +_zero:
                retval = +_zero
            else:
                if temp == _one:
                    fourthPi = Pi/_four
                    retval = fourthPi if isNegative else -fourthPi
                elif temp > _one:
                    isLargerThenOne = True
                    temp  = _one/temp
                temp = (temp*_three.sqrt() - _one)/(temp + _three.sqrt())
                a, d1 = _one, _one
                counter = int((1.0 +
                    (float(-digits)/math.log10(abs(temp))))/2.0)
                dTempSquared = temp*temp
                for i in range(counter, 0, -1):
                    a = d1 - a*dTempSquared*D(i + i - 1)/D(i + i + 1)
                retval = a*temp + Pi/6
                if isLargerThenOne:
                    retval = Pi/2 - retval
                if isNegative:
                    retval = -retval
    return retval

def atan2(y, x):
    '''Returns the inverse tangent of y/x in the proper quadrant.
    x and y are real numbers.
    Returns an angle in radians from -pi/2 to pi/2.
    '''
    if not isinstance(x, Dec):
        raise ValueError("x must be a Decimal number")
    if not isinstance(y, Dec):
        raise ValueError("y must be a Decimal number")
    with decimal.localcontext() as ctx:
        ctx.prec += _precision_increment
        Pi = pi()
        if not isinstance(x, D) or not isinstance(y, D):
            raise ValueError("Arguments must be Decimal numbers")
        elif y.is_nan() or x.is_nan():
            retval = _nan
        elif y.is_infinite() and x.is_infinite():
            if (y < 0 or x < 0)and not (y < 0 and x < 0):
               retval = -_inf
            else:
               retval = _inf
        elif x == _zero and y == _zero:
            raise ValueError("x and y can't both be zero")
        elif y.is_infinite() and not x.is_infinite():
            if y < 0:
               retval = -Pi/_two
            else:
               retval = Pi/_two
        elif x.is_infinite() and not y.is_infinite():
            if x < _zero:
               retval = Pi
            else:
               retval = _zero
        elif x == _zero:
            if y < 0:
               retval = -Pi/_two
            else:
               retval = Pi/_two
        else:
            if y == _zero:
               if x < _zero:
                  retval = Pi
               else:
                  retval = _zero
            else:
               a = _atan(abs(y/x))
               if x > _zero:
                  if y > _zero:
                     retval = a
                  else:
                     retval = -a
               else:
                  if y > _zero:
                     retval = pi() - a
                  else:
                     retval = a - pi()
    return retval

def Examples():
    '''Print some examples of use.
    '''
    out = sys.stdout.write
    sig.reset()
    def P(*args, **kw):
        '''Print a sequence of items by converting them to strings.
        '''
        sep = kw.setdefault("sep", " ")
        nl = kw.setdefault("nl", True)
        out(sep.join([str(i) for i in args]))
        if nl:
            out("\n")
    def f(x, digits, n=7, low=1e-3, high=1e6):
        sig.low = low
        sig.high = high
        P("digits = %d, low = %.1e, high = %.1e:" % (digits, low, high))
        for i in range(n):
            P("  ", sig(x*10**i, digits))
        P()
        for i in range(n):
            P("  ", sig(x*10**-i, digits))
        P()
    def Adjust(x, h=7):
        P("Fit to a stated number of spaces (%d significant digits):" % 
            sig.digits)
        s = "1234567890"*10
        P("   sp ", s[:h], "        x =", x)
        for sp in range(h, 0, -1):
            sig.fit = sp
            P("  %3d '%s'" % (sp, sig(x)))
        for sp in range(1, h + 1):
            sig.fit = -sp
            P("  %3d '%s'" % (-sp, sig(x)))
        P("   sp ", s[:h])
    s = "Examples of sig() behaviors"
    P(s)
    P("-"*len(s))
    Adjust(12.345, h=10)
    x = 1234.56
    sig.fit = 0
    P("")
    P("x =" + str(x))
    P("x to given number of significant figures:")
    for i in range(1, 8):
        P(("  %d:  " % i) + sig(x, i))
    P("Template rounding of x to nearest 0.05")
    P("  (for different template types)")
    P("  float:     " + sig(x, 0.05))
    P("  string:    " + sig(x, "0.05"))
    P("  Decimal:   " + sig(x, Dec("0.05")))
    P("  Fraction:  " + sig(x, "1/20"))
    x = Dec("12.3456789000")
    P("Decimal numbers:  " + repr(x))
    P("  x to 5 sig. fig.:     " + sig(x, 5))
    old, sig.high = sig.high, 10
    P("  scientific notation:  " + sig(x, 5))
    sig.esign = False
    P("  no + in exp:          " + sig(x, 5))
    sig.esign = True
    sig.high = old
    if _have_mpmath:
        x = mp.mpf("12.345")
        x = mp.pi()
        P("mpmath numbers:  " + repr(x))
        P("  x to 4 sig. fig.:  " + sig(x, 4))
    s = "3-13/32"
    P("Fractions -- number is %s" % s)
    P("  to nearest 4th :  " + sig(s, "1/4"))
    P("  to nearest 8th :  " + sig(s, "1/8"))
    P("  to nearest 16th:  " + sig(s, "1/16"))
    P("  to 4 sig. fig. :  " + sig(s, 4))
    re, im = "123.45", "-4567.8"
    s = "123.45-4567.8j"
    P("Complex numbers -- number is %s" % s)
    x = complex(s)
    P("  to 2 sig. fig. :  " + sig(x, 2))
    P("  to 6 sig. fig. :  " + sig(x, 6))
    sig.imag_polar = True
    P("  polar form     :  " + sig(x, 3))
    sig.imag_polar = False
    if _have_mpmath:
        x = mp.mpc(re, im)
        P("  mpmath to 2 sf :  " + sig(x, 2))
    P("Sequence -- sequence is ['2-1/3', (22/7., -3+4.1j)]")
    x = ["2-1/3", (22/7., -3+4.1j)]
    P("  bare python    :  " + str(x))
    P("  to 2 sig. fig. :  " + sig(x, 2))
    if _have_uncertainties:
        x, u = "1.2345678e-6", "0.0026351429e-6"
        P("Uncertainty:  number = %s, uncertainty = %s" % (x, u))
        x = unc.ufloat(float(x), float(u))
        P("  Uncertainties library form:  " + str(x))
        sig.unc_short = True
        P("  Short form 1 figure:         " + sig(x, 1))
        for i in (2, 3, 6):
            P("  Short form %d figures:        " % i + sig(x, i))
        sig.unc_short = False
        sig.unc_digits = 1
        P("  Long, 3 mean, 1 unc :        " + sig(x, 3))
        sig.unc_digits = 2
        P("  Long, 4 mean, 2 unc :        " + sig(x, 4))

if __name__ == "__main__":
    Examples()
