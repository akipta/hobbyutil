'''
Script to print out volume calibration marks for a bucket.  See the
associated document for a derivation of the formula used.
 
19 Feb 2012 Validation data using Nalgene 1000 ml graduated cylinder:

    * Ropak 4 gallon square bucket:  (inches) D=9.10, d=8.16, h=13, r=1.25,
      offset=0.12.  Measured 5 liters into bucket, water level at 118 mm
      from bottom; program calculates 117.3.  Measured 9 liters into
      bucket, water level at 201 mm from bottom; program calculates 202.8
      mm.

    * Rheem 5 gallon round bucket:  (inches) D=11.34, d=10.42, h=14,
      offset=0.47.
        Measured, liters    Actual distance, mm     Program calculates, mm
        ----------------    -------------------     ----------------------
               5                    103.5                   100.9
              10                    186.5                   186.2
              15                   267-268                  268.1
      Note:  the 15 liter actual distance was a bit hard to measure, as a
      rib of the bucket was in the way, disguising where the water level
      was.

    I used a flashlight inside the bucket to illuminate the water level and
    then measured the height of the water level up the side from the
    countertop.
    
---------------------------------------------------------------------------
Copyright (C) 2012 Don Peterson
Contact:  gmail.com@someonesdad1
  
                         The Wide Open License (WOL)
  
Permission to use, copy, modify, distribute and sell this software and its
documentation for any purpose is hereby granted without fee, provided that
the above copyright notice and this license appear in all copies.
THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF
ANY KIND. See http://www.dspguru.com/wide-open-license for more
information.
'''

from __future__ import division  # Make sure 1/3 == a float, not 0
from math import pi, sqrt, acos
from pdb import set_trace as xx


# Instructions:  set the variables for the bucket you have.  The following
# variables are set in inches; if you want to use different units, use some
# conversion factors to change them to inches.

r = 0           # Radius of bucket corners
sigma = None    # D/d - 1 (calculate it if it's None)
mm2in = 1/25.4

case = "Dixie cup, 8 oz."
case = "Rheem"
case = "Rheem NRC-90"

if case == "ropak":
    # Ropak cat litter bucket, inches
    D = 9.10        # Top width of bucket
    d = 8.16        # Bottom width of bucket
    h = 13          # Height of bucket
    r = 1.25        # Radius of bucket corners
    offset = 0.12   # Bottom plane of bucket to inside bottom
    # Define the shape of the bucket.  You can add shapes as needed.
    # "round" and "square" are currently supported.
    shape = "square"
elif case == "Rheem NRC-90":
    # Rheem gray plastic 5 gallon round bucket, inches
    D = 11.15       # Top width of bucket
    d = 10.35       # Bottom width of bucket
    h = 13.95       # Height of bucket
    offset = 0.53   # Bottom plane of bucket to inside bottom
    # Define the shape of the bucket.  You can add shapes as needed.
    # "round" and "square" are currently supported.
    shape = "round"
elif case == "Rheem":
    # Rheem gray plastic 5 gallon round bucket, inches
    D = 11.34       # Top width of bucket
    d = 10.42       # Bottom width of bucket
    h = 14          # Height of bucket
    offset = 0.47   # Bottom plane of bucket to inside bottom
    # Define the shape of the bucket.  You can add shapes as needed.
    # "round" and "square" are currently supported.
    shape = "round"
elif case == "square":
    # Test case:  square with no taper.  The square's side is sqrt(231),
    # which means the area is 231 square inches.  Thus, each inch of height
    # is 1 gallon (231 cubic inches).
    D = sqrt(231)   # Top width of bucket
    d = D           # Bottom width of bucket
    h = 10          # Height of bucket
    offset = 0      # Bottom plane of bucket to inside bottom
    # Define the shape of the bucket.  You can add shapes as needed.
    # "round" and "square" are currently supported.
    shape = "square"
elif case == "arbitrary area":
    # Test case:  arbitrary shaped bucket where we just give the top and
    # bottom areas and the relevant width at the top so the slope of the
    # side can be calculated.  The numbers here should cause the output to
    # duplicate that of the Rheem round bucket.
    D = 11.34       # Top width of bucket
    h = 14          # Height of bucket
    offset = 0.47   # Bottom plane of bucket to inside bottom
    sigma = 11.34/10.42 - 1
    A0g = 85.2757
    A1g = 100.9987
    shape = "arbitrary area"
elif case == "Dixie cup, 8 oz.":
    # Test case:  tapered 8 oz. Dixie cup.  Dimensions in mm.
    D = 73*mm2in    # Top width of bucket
    d = 51*mm2in    # Bottom width of bucket
    h = 89*mm2in    # Height of bucket
    offset = 5*mm2in# Bottom plane of bucket to inside bottom
    shape = "round"

#---------------------------------------------------------------------------
# Don't change anything below here

if sigma is None:
    sigma = D/d - 1

# Steps for marking volume units
steps = {
    "gallon" : 0.5,
    "liter" : 1,
    "cuft" : 0.05,
    "fraction" : 0.1,
}

# Conversion factors
in2mm = 25.4
gal2cuin = 231
liter2cuin = 61.0237
cuft2cuin = 1728
cuin2gal = 1/gal2cuin
cuin2liter = 1/liter2cuin
rad2deg = 180/pi

def sig(x, digits=None, low=1e-3, high=1e6, dp=".", idp=True, edigits=1,
        fit=0, sign=False):
    '''Return a string representing x to a specified number of  significant
    figures.  x must be an object that can be converted to a float.  
 
        digits  Number of significant figures
        low     Number at which display shifts to scientific notation
        high    Number at which display shifts to scientific notation
        dp      String used for the decimal point.
        idp     If True, then numbers that look like integers will have a 
                trailing decimal point.  
        edigits Number of digits to use in the exponent.
        fit     If nonzero, then digits is adjusted downward until the 
                returned string consumes no more than abs(fit) spaces.  If
                fit is positive, the string is right-justified; if
                negative, left justified.  If the string cannot be fit,
                None is returned.
        sign    If True, the sign of the number is always shown.  If False,
                the sign is only shown for negative numbers.
 
    You can also set sig.digits to an appropriate number of digits.  This
    number will be used if the digits keyword isn't used.  To resort to the
    default value again, use 'del sig.digits'.
    '''
    try:
        if digits is None:
            digits = sig.digits
    except AttributeError:
        digits = 3  # Default value
    digits = int(digits)  # Allows digits to be a float
    if digits < 1:
        raise AttributeError("digits must be >= 1")
    def append_zeros(z, num_zeros):
        while num_zeros:
            z.append("0")
            num_zeros -= 1
    def justify(s, spaces):
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
    def _sig(x, digits=digits, low=low, high=high, dp=dp, idp=idp, 
             edigits=edigits, sign=sign):
        if sign:
            sgn = "+" if x >= 0 else "-"
        else:
            sgn = "" if x >= 0 else "-"
        x = abs(float(x))
        ndigits = max(1, int(abs(digits)))
        # The following line breaks when ndigits reaches 114 in python
        # 2.6.5; this is probably a buffer overflow issue.
        s = "%.*e" % (ndigits - 1, float(x))
        if "e" not in s:
            msg = ('''x = '%s' cannot be displayed using %%e (digits = %d)
s = '%s\'''' % (x, digits, s))
            raise ValueError(msg)
        mantissa, exponent = s.split("e")
        exponent = int(exponent)
        exp = "%+0*d" % (edigits + 1, exponent)  # Add 1 for sign character
        if exponent == 0:
            if idp and "." not in mantissa:
                mantissa += "."
            return sgn + mantissa.replace(".", dp)
        if abs(x) <= low or abs(x) >= high:
            s = sgn + mantissa + "e" + exp
            return s.replace(".", dp)
        mantissa = mantissa.replace(".", "")
        z = [("0" + dp) if exponent < 0 else mantissa]
        if exponent < 0:   # Shift decimal point left
            num_zeros = abs(exponent) - 1
            append_zeros(z, num_zeros)
            z.append(mantissa)
            return sgn + ''.join(z)
        else:       # Shift decimal point right
            num_zeros = exponent - len(mantissa) + 1
            if num_zeros < 0:
                return sgn + mantissa[:num_zeros] + dp + mantissa[num_zeros:]
            append_zeros(z, num_zeros)
            if idp:
                z.append(dp)
            return sgn + ''.join(z)
    if fit:
        d, s = digits, _sig(x)
        has_dp = dp in s
        if len(s) <= abs(fit):
            return justify(s, fit)  # More spaces than needed
        while len(s) > abs(fit):
            if "e" in s:
                return None # We won't muck with exponential notation
            # Need to chop off some significant digits
            d -= 1
            if d == 0:
                break
            if has_dp and dp not in s:
                return None # Cannot be made to fit
            s = _sig(x, digits=d)
        if not d:
            return None     # Cannot be made to fit
        else:
            return s        # Fit was OK
    else:
        return _sig(x)

# Used for output formatting
S = sig
S.digits = 4    # Number of significant figures to output

def RoundArea(d):
    return pi*d*d/4

def SquareArea(d, r):
    return d*d - r*r*(4 - pi)

def Volume(A1, A2, h):
    return h/3.*(A1 + A2 + sqrt(A1*A2))

def secant(sigma, D, h):
    return sqrt(1 + (sigma*D/(2*h))**2)

def CalibrationMark(D, h, offset, vx, A0):
    try:
        x = ((1 + 3*sigma*vx/(A0*h))**(1/3.) - 1)/sigma
    except ZeroDivisionError:
        x = vx/(A0*h)   # sigma is zero; use the limit
    return (x*h + offset)*secant(sigma, D, h)

def mm(inches, prepend="= "):
    return prepend + S(inches*in2mm) + " mm"

def PrintHeader(A0, A1):
    '''A0 is area in square inches of bottom of bucket; A1 is area of top.
    '''
    print "Volume calibration for", shape, 
    print_r = False
    if shape == "square":
        print "bucket with rounded corners"
        print_r = True
    elif shape == "round":
        print "bucket"
    elif shape == "arbitrary area":
        print
    print "  Case = %s" % case
    print '''
  Measure from outside bottom of bucket to calibrate.  Note that the distance 
    you measure is the slant height along the side of the bucket.'''[1:]
    print "  D = width at top of bucket =", S(D), "in", mm(D)
    if shape != "arbitrary area":
        print "  d = width at bottom of bucket =", S(d), "in", mm(d)
    print "  h = height of bucket =", S(h), "in", mm(h)
    print "  offset = distance from bucket bottom to inside bottom =", \
            S(offset), "in", mm(offset)
    if print_r:
        print "  r = radius of corners =", S(r), "in", mm(r)
    angle = acos(1/secant(sigma, D, h))*rad2deg
    print "  Angle off vertical of bucket side =", S(angle, digits=3), "degrees"
    print "  sigma = D/d - 1 =", S(sigma)
    print "  Area of top =", S(A1), "in2 =", S(A1*in2mm**2), "mm2"
    print "  Area of bottom =", S(A0), "in2 =", S(A0*in2mm**2), "mm2"
    # Get volume
    V = Volume(A0, A1, h)
    print "  Calculated volume of bucket =", S(V), "in3 =", \
            S(V*cuin2gal), "gal =", S(V*cuin2liter), "liter"
    print

def PrintGallonCalibrations(A0, V):
    step_size = steps["gallon"]
    print "  Divisions for gallons:"
    print "      gallons    inches        mm"
    print "      -------    ------      ------"
    fmt, gal = " %10s "*3, 0
    while True:
        gallons = gal*step_size
        gal += 1
        vx = gallons*gal2cuin
        if vx >= V:
            break
        mark = CalibrationMark(D, h, offset, vx, A0)
        g, i, m = "%6.1f" % gallons, "%8.2f" % mark, "%8.1f" % (mark*in2mm)
        print fmt % (g, i, m)
    print

def PrintLiterCalibrations(A0, V): 
    step_size = steps["liter"]
    print "  Divisions for liters:"
    print "      liters     inches        mm"
    print "      ------     ------      ------"
    fmt, lit = " %10s "*3, 0
    while True:
        liters = lit*step_size
        lit += 1
        vx = liters*liter2cuin
        if vx >= V:
            break
        mark = CalibrationMark(D, h, offset, vx, A0)
        l, i, m = "%6.0f" % liters, "%8.2f" % mark, "%8.1f" % (mark*in2mm)
        print fmt % (l, i, m)
    print

def PrintCubicFootCalibrations(A0, V): 
    step_size = steps["cuft"]
    print "  Divisions for cubic feet:"
    print "      cu ft      inches        mm"
    print "      ------     ------      ------"
    fmt, ft3 = " %10s "*3, 0
    while True:
        cuft = ft3*step_size
        ft3 += 1
        vx = cuft*cuft2cuin
        if vx >= V:
            break
        mark = CalibrationMark(D, h, offset, vx, A0)
        cf, i, m = "%6.2f" % cuft, "%8.2f" % mark, "%8.1f" % (mark*in2mm)
        print fmt % (cf, i, m)
    print

def PrintPercentCalibrations(A0, V): 
    '''Print the calibration points that represent the fraction of the
    total bucket volume when filled to the brim.

    V is total bucket volume in in3.
    '''
    step_size = steps["fraction"]
    print "  Divisions for fraction of total volume"
    print "      Fraction     inches        mm"
    print "      --------     ------      ------"
    fmt, count = " %10s "*3, 0
    while True:
        fraction = count*step_size
        count += 1
        vx = V*fraction
        if fraction > 1:
            break
        mark = CalibrationMark(D, h, offset, vx, A0)
        f, i, m = "%6.2f" % fraction, "%8.2f" % mark, "%8.1f" % (mark*in2mm)
        print fmt % (f, i, m)
    print

def main():
    if not 1/3:
        raise RuntimeError("Use python's -Qnew command line option")
    # Get A0, area of the bucket bottom
    if shape == "square":
        A0 = SquareArea(d, r)
        A1 = SquareArea(D, r)
    elif shape == "round":
        A0 = RoundArea(d)
        A1 = RoundArea(D)
    elif shape == "arbitrary area":
        A0 = A0g
        A1 = A1g
    else:
        raise ValueError("Unknown shape")
    # Note we use the sig() function to print results to a specified number
    # of significant digits.  You can change this in the line S.digits
    # above.
    PrintHeader(A0, A1)
    V = Volume(A0, A1, h)
    PrintGallonCalibrations(A0, V)
    PrintLiterCalibrations(A0, V)
    PrintCubicFootCalibrations(A0, V)
    PrintPercentCalibrations(A0, V)

main()
