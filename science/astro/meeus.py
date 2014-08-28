'''
TODO:

    * Check each function's parameters for both type and value.  While
      this may not be pythonic, it is intended to help you find bugs
      in programs caused by improper values.  Note the checks are
      always done (i.e., they're not asserts).

    * Carefully document all functions to make it easier to use them
      as-is.  This means defining each input variable, its defining
      equation/page, and physical units.  Also make sure the units and
      type of the returned values are given.
    
    * Convert radian/degree conversions to using math.radians and
      math.degrees.  This possibly allows for slightly more
      portability and, allows e.g. d2r() to be a function instead of a
      multiplier.  

    * Ensure there's a test case for each function.  Convert to use
      unittest.

Various formulas from Meeus, "Astronomical Algorithms", 2nd ed.  Run
as a script to execute self tests.

Included functions:
    AngularSeparation(ra1, dec1, ra2, dec2)
    ApparentSiderealTime(month, day, year)
    CheckIntegerDate(month, day, year, decimal_day=False)
    DayOfWeek(month, day, year)
    DayOfYear(month, day, year)
    DayOfYear2MDY(day_of_year, year)
    dms2rad(d, m, s)
    EarthOrbitEccentricity(T)
    EarthSurfaceDistance(lat1, long1, lat2, long2)
    EclipticObliquity(jd)
    EquationOfTime(jd)
    hms2rad(h, m, s)
    hr2hms(hr)
    IsDST(month, day, year)
    IsLeapYear(year)
    IsValidGregorianDate(month, day, year)
    JD(month, day, year)
    JD2MDY(julian_day, year)
    JulianAstro(month, day, year)
    JulianToMonthDayYear(jd)
    KeplerEquation(e, M, reltol=0)
    LagrangeInterpolation(x, X, Y, strict=0)
    LatitudinalDistance(latitude, angle)
    LinearRegression(X, Y)
    LocalCoordinates(latitude, longitude, ra, dec, jd)
    LongitudinalDistance(latitude, angle)
    MDY2ISO(month, day, year)
    MeanSiderealTime(month, day, year)
    Normalize(angle, degrees=0)
    NumDaysInMonth(month, year)
    Nutation(jd)
    Precession(jd, jd0, ra0, dec0, pm_ra=0, pm_dec=0)
    product(X)
    rad2dms(x)
    rad2hms(x)
    SGN(x)
    SunMeanAnomaly(T)
    SunMeanLongitude(T)
    SunPosition(jd, apparent=0)
    SunriseSunset(month, day, year, latitude, longitude)
    TimeOfMoonPhase(year, quarter=0)
    UT2DT(year)
'''

# Copyright (C) 1999, 2014 Don Peterson
# Contact:  gmail.com@someonesdad1

#
#

from __future__ import division, print_function
import sys, operator, datetime
from math import pi, floor, sqrt, sin, cos, tan, asin, acos, atan, atan2
from math import fabs, floor, fmod, radians, degrees, ceil, log10
from pdb import set_trace as xx

pyver = sys.version_info[0]
if pyver == 3:
    long = int
    import functools
    reduce = functools.reduce

# Constants
r2d = 180/pi
d2r = 1/r2d
earth_equatorial_radius_km = 6378.14
earth_flattening = f = 1/298.257
earth_meridian_eccentricity = sqrt(2*f - f*f); del f
minimum_year = -4712

# Days in months (February handled specially because of leap years)
months = {1:31, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}

def MDY2ISO(month, day, year):
    '''Returns an integer in the ISO form YYYYMMDD.  month and year
    must be integers.  day can be a float; it is truncated to an
    integer.
    '''
    day = int(day)
    if not IsValidGregorianDate(month, day, year):
        raise ValueError("Not a valid Gregorian calendar date")
    return int("%d%02d%02d" % (year, month, day))

def IsLeapYear(year):
    '''Page 62.  Returns True if year is a leap year.
    '''
    y = year
    assert y > 0, "year must be >= 0"
    if not isinstance(y, (int, long)):
        raise ValueError("year must be an integer")
    return True if (y % 400 == 0) or (y % 4 == 0 and y % 100 != 0) else False

def NumDaysInMonth(month, year):
    assert year > 0, "year must be >= 0"
    if not isinstance(year, (int, long)):
        raise ValueError("year must be an integer")
    if month == 2:
        return 29 if IsLeapYear(year) else 28
    return months[month]

def DayOfYear(month, day, year):
    '''Page 65.  Returns an integer between 1 and 366 corresponding to
    the day of the year.  1 January is day 1 and 31 December is day
    365 (366 in a leap year).
    '''
    if not isinstance(year, (int, long)):
        raise ValueError("year must be an integer")
    M, D = month, day
    K = 1 if IsLeapYear(year) else 2
    N = int(275*M/9) - K*int((M+9)/12) + D - 30
    assert 1 <= N <= 366, "Illegal day number"
    return N

def DayOfYear2MDY(day_of_year, year):
    '''Page 66.  Returns a tuple of integers (month, day, year) given
    the day number and a year.
    '''
    if not isinstance(year, (int, long)):
        raise ValueError("year must be an integer")
    if not isinstance(day_of_year, (int, long)):
        raise ValueError("day_of_year must be an integer")
    assert 0 <= day_of_year <= 366, "Bad day of year number"
    N = day_of_year
    K = 1 if IsLeapYear(year) else 2
    M = int((9*(K + N)/275.) + 0.98)
    if N < 32:
        M = 1
    D = N - int(275*M/9.) + K*int((M + 9)/12.) + 30
    return (M, D, year)

def CheckIntegerDate(month, day, year, decimal_day=False):
    '''Raises a ValueError if month, day, and year aren't integers and
    properly bounded.  If decimal_day is True, then day can be a
    floating point number.
    '''
    if decimal_day:
        day = int(day)
    e = ValueError("Year, month, or day are bad")
    try:
        datetime.date(year, month, day)
    except ValueError:
        # Year can be less than 1, which is the datetime module's
        # least allowed year.
        if year < 1:
            # Check month and day by using the year 2000.
            try:
                datetime.date(2000, month, day)
            except ValueError:
                raise e
            if year < minimum_year:
                raise e
        else:
            raise e

def DayOfWeek(month, day, year):
    '''Page 65.  Returns a number between 0 (Sunday) and 6 (Saturday)
    for a given date.
    '''
    CheckIntegerDate(month, day, year, decimal_day=True)
    julian = int(JulianAstro(month, int(day), year) + 1.5)
    return julian % 7

def IsDST(month, day, year):
    '''Return True if DST is in effect.  Assumes a location in the US
    that utilizes DST.  Note the rules can change at any time.
    '''
    # Algorithm from
    # http://stackoverflow.com/questions/5590429/calculating-daylight-savings-time-from-only-date
    D, M, Y = [int(i) for i in (day, month, year)]
    dow = DayOfWeek(M, D, Y)
    # Jan, Feb, Dec are not DST
    if M in (1, 2, 12): 
        return False
    if M in range(4, 11): 
        return True
    previous_sunday = D - dow
    # In Mar, we are in DST if our previous Sunday was on or after the
    # 8th.
    if M == 3:
        return previous_sunday >= 8
    # In Nov we must be before the first Sunday to be DST.  That means
    # the previous Sunday must be before the first.
    return previous_sunday <= 0

def IsValidGregorianDate(month, day, year):
    '''Returns True if the year is a valid Gregorian calendar date
    (i.e., year is 1583 or greater) and the month and day numbers
    are valid.  month, day, and year must be integers.

    Note the maximum year allowed is datetime.MAXYEAR.
    '''
    if year < 1583: 
        return False
    try:
        CheckIntegerDate(month, day, year)
    except ValueError:
        return False
    return True

def JulianAstro(month, day, year):
    '''Page 60.  Returns the astronomical Julian day number which is a
    floating point number that is zero at Greenwich mean noon.  The
    Julian() function returns the more usual Julian day as an integer;
    it is gotten from the astronomical form by adding 0.55 and taking
    the integer part.
    '''
    CheckIntegerDate(month, day, year, decimal_day=True)
    assert year >= minimum_year
    M, D, Y = month, day, year  # Meeus' notation
    if M in (1, 2):
        Y -= 1
        M += 12
    A = int(Y/100.0)
    tmp = year + month/100.0 + day/10000.0
    B = 0 if tmp < 1582.1015 else 2 - A + int(A/4) # B==0 ==> Julian cal.
    julian = int(365.25*(Y + 4716)) + int(30.6001*(M+1)) + D + B - 1524.5
    return julian

def JD(month, day, year):
    '''Return the Julian day of the year (a number <= 366).
    '''
    jd  = int(JulianAstro(month, day, year) + 0.55)
    jd0 = int(JulianAstro(1, 1, year) + 0.55)
    return jd - jd0 + 1

def JDToJulianAstro(julian_day, year):
    '''Return the JulianAstro day number corresponding to the given
    day in the given year.  julian_day must be between 1 and 366,
    inclusive.
    '''
    is_leap = IsLeapYear(year)
    if not (0 < julian_day <= 365 + is_leap):
        raise ValueError("'%d' is a bad julian_day argument" % julian_day)
    if julian_day < 1582:
        raise ValueError("'%d' is a bad year argument" % year)

def JD2MDY(julian_day, year):
    '''Return (month, day, year) for the given julian_day and year.
    '''
    # Days in month indexed by (month - 1).
    days_in_month = (31, 28 + IsLeapYear(year), 31, 30, 31, 30, 31,
                     31, 30, 31, 30, 31)
    # Get month and day
    cum_num_days = [sum(days_in_month[:m]) for m in range(1, 13)]
    for i in range(len(cum_num_days)):
        if cum_num_days[i] >= julian_day:
            # It's this month
            month = i + 1
            cum_days = cum_num_days[i]
            day = days_in_month[i] - (cum_days - julian_day)
            return (month, day, year)

def JulianToMonthDayYear(jd):
    '''Page 63.  Returns (month, day, year) given the Julian day jd.
    Month and year are integers; day can be a float.
    '''
    assert jd >= 0, "Julian day must be >= 0"
    jd += 0.5
    Z = int(jd)
    F = jd - Z
    A = Z
    if Z >= 2299161:
        alpha = int((Z - 1867216.25)/36524.25)
        A = Z + 1 + alpha - int(alpha/4)
    B = A + 1524
    C = int((B - 122.1)/365.25)
    D = int(365.25 * C)
    E = int((B - D)/30.6001)
    day = B - D - int(30.6001 * E) + F
    if E < 14:
        month = int(E - 1)
    else:
        month = int(E - 13)
    if month > 2:
        year = int(C - 4716)
    else:
        year = int(C - 4715)
    return month, day, year  # month, year are integers

def SGN(x):
    '''Signum function; returns -1 if x < 0, 0 if x == 0, and 1 if x > 0.
    '''
    return 1 if x > 0 else -1 if x < 0 else 0

def hms2rad(h, m, s):
    '''Converts angular measure in hours, minutes, seconds to radians.
    One hour is equivalent to 360/24 = 15 degrees.
    '''
    assert m >= 0, "m must be >= 0"
    assert s >= 0, "s must be >= 0"
    decimal_hours = abs(h) + abs(m)/60. + abs(s)/3600.
    return SGN(h)*decimal_hours*15*d2r

def dms2rad(d, m, s):
    '''Converts angular measure in degrees, minutes, seconds to radians.
    The result will have the sign of d.
    '''
    assert m >= 0, "m must be >= 0"
    assert s >= 0, "s must be >= 0"
    deg = abs(d) + abs(m)/60. + abs(s)/3600.
    return SGN(d)*deg*d2r

def EarthSurfaceDistance(lat1, long1, lat2, long2):
    '''Page 85.  Returns the distance in km between two points on the
    Earth's surface.  The latitudes and longitudes must be in radians.
    The returned value is in km if the The relative error of the
    result is on the order of 1e-5.
    '''
    assert abs(lat1) <= pi/2, "abs(lat1) must be <= pi/2"
    assert abs(lat2) <= pi/2, "abs(lat2) must be <= pi/2"
    assert abs(long1) <= pi/2, "abs(long1) must be <= pi/2"
    assert abs(long2) <= pi/2, "abs(long2) must be <= pi/2"
    a = earth_equatorial_radius_km
    f = earth_flattening
    F = (lat1 + lat2)/2.
    G = (lat1 - lat2)/2.
    L = (long1 - long2)/2
    S = sin(G)*sin(G)*cos(L)*cos(L) + cos(F)*cos(F)*sin(L)*sin(L)
    C = cos(G)*cos(G)*cos(L)*cos(L) + sin(F)*sin(F)*sin(L)*sin(L)
    omega = atan(sqrt(S/C))
    R = sqrt(S*C)/omega
    D = 2*omega*a
    H1 = (3*R-1)/(2*C)
    H2 = (3*R+1)/(2*S)
    return D*(1 + f*H1*sin(F)*sin(F)*cos(G)*cos(G) - 
                  f*H2*cos(F)*cos(F)*sin(G)*sin(G))

def LongitudinalDistance(latitude, angle):
    '''Page 83.  Returns the distance in km along a circle of constant
    latitude for Earth for an angular longitude distance of angle.
    The angles must be in radians.
    '''
    assert abs(latitude) <= pi/2, "abs(latitude) must be <= pi/2"
    angle = fmod(angle, 2*pi)
    if angle < 0:
        angle += 2*pi
    a = earth_equatorial_radius_km
    e = earth_meridian_eccentricity
    return angle*a*cos(latitude)/sqrt(1 - e*e*sin(latitude)*sin(latitude))

def LatitudinalDistance(latitude, angle):
    '''Page 84.  Returns the distance in km along a circle of constant
    longitude for Earth for an angular distance of angle along the
    latitude.  The angles must be in radians.
    '''
    assert abs(latitude) <= pi/2, "abs(latitude) must be <= pi/2"
    angle = fmod(angle, 2*pi)
    if angle < 0:
        angle += 2*pi
    a = earth_equatorial_radius_km
    e = earth_meridian_eccentricity
    d = 1 - e*e*sin(latitude)*sin(latitude)
    return angle*a*(1-e*e)/pow(d, 3/2.)

def UT2DT(year):
    '''Page 78.  Returns the correction in seconds to add to Universal
    Time to get dynamical time.
    '''
    t = (year - 2000)/100.
    if year < 948:
        return 2177 + 497*t + 44.1*t*t
    if 948 <= year <= 1600 or year >= 2000:
        correction = 0
        if 2000 <= year <= 2100:
            correction = 0.37*(year - 2100)
        return 102 + 102*t + 25.3*t*t + correction
    if 1800 <= year <= 1997:
        # Maximum error <= 2.3 seconds
        t = (year - 1900)/100.
        dt = -1.02 + t*(91.02 + t*(265.90 + t*(-839.16 + t*(-1545.20 
             + t*(3603.62 + t*(4385.98 + t*(-6993.23 + t*(-6090.04 
             + t*(6298.12 + t*(4102.86 + t*(-2137.64 + t*(-1081.51))))))))))))
        return dt
    if int(year + 0.5) == 1998:  
        return 63.0
    if int(year + 0.5) == 1999:  
        return 64.0
    raise ValueError("Year is out of bounds")

def LagrangeInterpolation(x, X, Y, strict=0):
    '''Page 32.  Given x, an abscissa, calculates the interpolated
    value y = f(x) where f(x) is Lagrange's interpolating polynomial.
    X and Y are expected to be iterables of the same size such that
    Y[i] = f(X[i]).  If strict is True, then you'll get an exception
    if you try to interpolate outside the range of abscissas given in
    X.  If strict is True, we'll check to make sure that none of the 
    abscissas in X are the same.
    '''
    n = len(X)
    assert len(Y) == n, "Y's length not the same as X's"
    if strict:
        if x < min(X) or x > max(X):
            raise ValueError("x value is outside of interpolation range")
        if len(set(X)) != len(X):
            raise ValueError("X has one or more duplicated values")
    y = 0
    for i in range(n):
        c = 1
        for j in range(n):
            if i == j:
                continue
            c *= (x - X[j])/(X[i] - X[j])
        y += c*Y[i] 
    return y

def product(X):
    '''Returns the product of the components of the iterable X.
    '''
    return reduce(operator.mul, X)

def LinearRegression(X, Y):
    '''Page 36.  Returns a tuple (slope, intercept, correlation) from
    the linear regression of Y against X.  X and Y are sequences of
    the abscissas and ordinates, respectively; they must be of the same
    size.
    '''
    N, sx, sy = len(X), sum(X), sum(Y)
    sq, prod = lambda x: x*x, lambda x, y: x*y
    sxx, syy, sxy = sum(map(sq, X)), sum(map(sq, Y)), sum(map(prod, X, Y))
    denomx, denomy = N*sxx - sx*sx, N*syy - sy*sy
    if not denomx or not denomy:
        raise ValueError("Regression equation denominator is zero")
    slope = (N*sxy - sx*sy)/denomx
    intercept = (sy*sxx - sx*sxy)/denomx
    r = (N*sxy - sx*sy)/sqrt(denomx*denomy)
    assert -1 <= r <= 1, "Correlation coefficient out of range"
    return (slope, intercept, r)

def Nutation(jd):
    '''Page 143.  Returns the tuple (d_psi, d_eps) in radians where
    d_psi is the nutation in longitude and d_eps is the nutation
    in obliquity.  jd is the Julian astronomical day.  Accuracy is
    2.4 urad for psi and 0.48 urad for eps.
    '''
    T = (jd - 2451545.0)/36525  # Julian centuries
    # Mean elongation of the moon from the sun
    D = 297.85036+ 445267.111480*T - 0.0019142*T*T + T*T*T/189474
    # Mean anomaly of the sun (earth)
    M = 357.52772 + 35999.050340*T - 0.0001603*T*T - T*T*T/300000
    # Mean anomaly of the moon
    m = 134.96298 + 477198.867398*T + 0.0086972*T*T + T*T*T/56250
    # Moon's argument of latitude
    F = 93.27191 + 483202.017538*T - 0.0036825*T*T + T*T*T/327270
    # Longitude of ascending node of moon's mean orbit on ecliptic
    Omega = 125.04452 - 1934.136261*T + 0.0020708*T*T + T*T*T/450000
    # Mean longitude of sun
    L = 280.4665 + 36000.7698*T
    # Mean longitude of moon
    Lm = 218.3165 + 481267.8813*T
    # Note:  I use the formulas on page 144 which give 0.5" accuracy 
    # in d_psi and 0.1" accuracy in d_eps.
    d_psi = (-17.20*sin(Omega*d2r) - 1.32*sin(2*L*d2r) - 
            0.23*sin(2*Lm*d2r) + 0.21*sin(2*Omega*d2r))
    d_eps = (9.20*cos(Omega*d2r) + 0.57*cos(2*L*d2r) + 
            0.10*cos(2*L*d2r) - 0.09*cos(2*Omega*d2r))
    return (d_psi*d2r/3600, d_eps*d2r/3600)

def EclipticObliquity(jd):
    '''Page 147.  Returns the obliquity of the ecliptic in radians
    given the Julian day jd.  This is the angle between the Earth's
    axis of rotation and the ecliptic.  This is the mean obliquity,
    meaning nutation isn't taken into account.  Returns an angle in
    radians.
    '''
    # Convert Julian day to units of 1e4 years
    u = (jd - 2451545.0)/(36525*100)
    assert abs(u) <= 1  # Only to be used for +/- 1e4 years from 2000
    c = dms2rad(23, 26, 21.448)  # Major component constant
    e = u*(-4680.93 + u*(-1.55 + u*(1999.25 + u*(-51.38 + u*(-249.67 + 
        u*(-39.05 + u*(7.12 + u*(27.87 + u*(5.79 + u*(2.45))))))))))
    # e is in arcseconds; convert to radians and add the constant
    e = c + d2r*e/3600.
    return e

def EarthOrbitEccentricity(T):
    '''Returns Earth's orbit eccentricity (dimensionless) for the time
    T in Julian centuries from 1 Jan 2000.  Equation 25.4 on page 163.
    '''
    return 0.016708634 - 0.000042037*T - 0.0000001267*T*T

def SunMeanAnomaly(T):
    '''Return the Sun's mean anomaly in radians.  Equation 25.3 pg
    163.
    '''
    return Normalize(d2r*(357.52911 + 35999.05029*T + 0.0001537*T*T))

def MeanSiderealTime(month, day, year):
    '''Page 87.  The calculation returns the mean sidereal time in
    decimal hours for 0 UT on the given day.
    '''
    jd = JulianAstro(month, day, year)
    T = (jd - 2451545.0)/36525  # Julian centuries
    # Calculate mst = mean sidereal time in degrees using eq. 12.4
    mst = (280.46061837 + 360.98564736629*(jd-2451545.0)+ 
          0.000387933*T*T - T*T*T/38710000)
    mst = fmod(mst, 360)
    if mst < 0:
        mst += 360.
    return mst/15

def ApparentSiderealTime(month, day, year):
    '''Page 88.  The calculation returns the apparent sidereal time 
    in decimal hours for 0 UT on the given day.  
    '''
    jd = JulianAstro(month, day, year)
    T = (jd - 2451545.0)/36525  # Julian centuries
    # Calculate mst = mean sidereal time in degrees using eq. 12.4
    mst = (280.46061837 + 360.98564736629*(jd-2451545.0) +
          0.000387933*T*T - T*T*T/38710000)
    mst = fmod(mst, 360)
    if mst < 0:
        mst += 360.
    # mst is in decimal degrees.  Get the correction for nutation.
    d_psi, d_eps = Nutation(jd)
    d_psi *= r2d                        # Converted to decimal degrees
    eps = EclipticObliquity(jd)         # Leave in radians
    mst += d_psi*cos(eps)               # Correction to apparent sid. time
    return mst/15  # Convert to decimal hours

def hr2hms(hr):
    '''Return a tuple (hours, minutes, seconds) of a decimal hour 
    value hr.  hours will have the sign of hr.
    '''
    sgn = SGN(hr)
    h = int(abs(hr))
    m = 60*(abs(hr) - h)
    s = 60*(m - int(m))
    return sgn*h, int(m), s

def rad2dms(x):
    '''Return a tuple (degrees, minutes, seconds) of a radian value.  
    The degrees value will have the sign of x.
    '''
    sgn = SGN(x)
    x = fabs(x)
    d = x * r2d
    deg = int(d)
    min = 60*(d - deg)
    sec = 60*(min - int(min))
    return sgn*deg, int(min), sec

def rad2hms(x):
    '''Return a tuple (hour, minutes, seconds) of a radian value.
    '''
    return rad2dms(x/15)

def LocalCoordinates(latitude, longitude, ra, dec, jd):
    '''Page 93.  Calculate the local horizontal coordinates for an
    object with right ascension ra and declination dec.  The current
    time is specified in the Julian day jd.  The latitude and
    longitude are of the observer on the surface of the Earth.  The
    tuple (azimuth, altitude) in degrees are returned.  Meeus'
    convention is that longitude is positive when it is west of
    Greenwich.  Units are:
        latitude, longitude, dec:  radians
        ra:  decimal hours
    '''
    # Get the sidereal time at Greenwich
    month, day, year = JulianToMonthDayYear(jd)
    sidereal_time_in_hours = MeanSiderealTime(month, day, year)
    theta0 = sidereal_time_in_hours * 15 * d2r # Convert to radians
    H = theta0 - longitude - ra     # Hour angle in radians
    H = fmod(H, 2*pi)
    if H < 0:
        H += 2*pi
    assert 0 <= H <= 2*pi
    A = atan(sin(H)/(cos(H)*sin(latitude) - tan(dec)*cos(latitude))) * r2d
    h = asin(sin(latitude)*sin(dec) + cos(latitude)*cos(dec)*cos(H)) * r2d
    # Convert A to an attitude reckoned from north
    A = fmod(A + 180., 360)
    assert 0 <= A <= 360
    assert -90 <= h <= 90
    return (A, h)

def AngularSeparation(ra1, dec1, ra2, dec2):
    '''Page 109.  Returns the angular separation in radians between two 
    bodies at (ra1, dec1) and (ra2, dec2).  ra is right ascension and
    dec is declination, both in radians.
    '''
    d = acos(sin(dec1)*sin(dec2) + cos(dec1)*cos(dec2)*cos(ra1-ra2))
    if d < 1/60.:
        # Use an approximation for small angles
        a = (ra1-ra2)*cos((dec1+dec2)/2.)
        b = dec1 - dec2
        d = sqrt(a*a + b*b)
    return d

def Precession(jd, jd0, ra0, dec0, pm_ra=0, pm_dec=0):
    '''Page 134.  Returns (ra, dec) representing a position in
    equatorial coordinates at time Julian day jd for a position (ra0,
    dec0) given at time jd0.  ra and dec mean right ascension and
    declination angles.  This function corrects for the precession of
    the Earth's axis of rotation over time.  All angles (ra and dec)
    are in radians.  pm_ra and pm_dec, if given, are the proper
    motions of the object in radians/year.
    '''
    T = (jd0 - 2451545.0)/36525
    t = (jd - jd0)/36525
    # The following are in seconds of arc
    zeta  = ((2306.2181 + 1.39656*T - 0.000139*T*T)*t + 
             (0.30188 - 0.000344*T)*t*t + 0.017998*t*t*t)
    z     = ((2306.2181 + 1.39656*T - 0.000139*T*T)*t + 
             (1.09468 + 0.000066*T)*t*t + 0.018203*t*t*t)
    theta = ((2004.3109 - 0.85330*T - 0.000217*T*T)*t - 
             (0.42665 + 0.000217*T)*t*t - 0.041833*t*t*t)
    # Convert them to radians
    zeta  *= d2r/3600.
    z     *= d2r/3600.
    theta *= d2r/3600.
    # Adjust for the proper motion
    years = (jd - jd0)/365.25
    ra    = ra0 + pm_ra*years
    dec   = dec0 + pm_dec*years
    # Now calculate the new position
    A = cos(dec)*sin(ra + zeta)
    B = cos(theta)*cos(dec)*cos(ra + zeta) - sin(theta)*sin(dec)
    C = sin(theta)*cos(dec)*cos(ra + zeta) + cos(theta)*sin(dec)
    ra = atan2(A, B) + z
    if fabs(C-1) < .001:
        # It's within a degree or so to the celestial pole, so use a
        # different formula
        dec = acos(sqrt(A*A + B*B))
    else:
        dec = asin(C)
    return (ra, dec)

def Normalize(angle, degrees=0):
    '''Normalize an angle to between 0 and 2*pi radians (0 and 360
    degrees if degrees is true).
    '''
    rotation = 360 if degrees else 2*pi
    new_angle = fmod(angle, rotation)
    if new_angle < 0:
        new_angle += rotation
    return new_angle

def SunPosition(jd, apparent=0):
    '''Page 163.  Returns equatorial coordinates (ra, dec) in radians
    for the true position of the sun at the specified Julian day.  If
    apparent is true, then the position returned is the apparent
    position.
    '''
    T = (jd - 2451545.0)/36525  # Centuries from 2000 Jan 1.5 TD
    # Geometric mean longitude in radians
    L0 = Normalize(d2r*(280.46646 + 36000.76983*T + 0.0003032*T*T))
    # Mean anomaly of sun in radians
    M = Normalize(d2r*(357.52911 + 35999.05029*T + 0.0001537*T*T))
    # Eccentricty of earth's orbit
    e = 0.016708634 - 0.000042037*T - 0.0000001267*T*T
    # Sun's equation of center in radians
    C = d2r*((1.914602 - 0.004817*T - 0.000014*T*T)*sin(M) + 
             (0.019993 - 0.000101*T)*sin(2*M) + 0.000289*sin(3*M))
    C = Normalize(C)
    # Sun's true geometric longitude in radians referred to the mean
    # equinox of the date
    L = Normalize(L0 + C)
    # Sun's true anomaly in radians
    nu = Normalize(M + C)
    # Sun's radius vector in AU
    R = 1.000001018*(1-e*e)/(1 + e*cos(nu*d2r))
    # Calculate the sun's apparent longitude in radians, referred to
    # the true equinox of the date, correcting for nutation and
    # aberration.
    Omega = Normalize((125.04 - 1934.136*T)*d2r)                # In radians
    Lambda = Normalize(L - (0.00569 - 0.00478*sin(Omega))*d2r)  # In radians
    # Mean obliquity of the ecliptic
    eps = EclipticObliquity(jd)  # In radians
    if apparent:
        eps += 0.00256*cos(Omega)*d2r
        ra = Normalize(atan2(cos(eps)*sin(Lambda), cos(Lambda)))
        dec = asin(sin(eps)*sin(Lambda))
    else:
        ra = Normalize(atan2(cos(eps)*sin(L), cos(L)))
        dec = asin(sin(eps)*sin(L))
    return (ra, dec)

def SunriseSunset(month, day, year, latitude, longitude):
    '''Returns a tuple (t_UT_sunrise, t_UT_sunset) of the UT times in
    decimal hours for sunrise and sunset on the indicated day.
    latitude and longitude must be in radians.  If you convert the
    returned times to your local time zone and get a negative time,
    add 24 hours.
    '''
    jd = JulianAstro(month, day, year)
    # Note we convert apparent sidereal time from decimal hours to radians
    ast = ApparentSiderealTime(month, day, year)*15*d2r
    h0 = -0.8333*d2r   # Geometric altitude of center at rising
    ra, dec = SunPosition(jd)
    s = sin(latitude)*sin(dec)
    if s < -1 or s > 1:
        raise "Object doesn't go below horizon"
    H0 = acos((sin(h0) - s)/(cos(latitude)*cos(dec)))
    m0 = (ra + longitude - ast)/(2*pi)
    m1 = m0 - H0/(2*pi)
    m2 = m0 + H0/(2*pi)
    while m1 > 1:
        m1 -= 1
    while m1 < 0:
        m1 += 1
    return 24*m1, 24*m2

def TimeOfMoonPhase(year, quarter=0):
    ''' Returns the time in JDE (Julian Day Ephemeris, which is
    equivalent to Dynamical Time TD).  Note if you want the time in
    UT, you'll have to correct it using the equation of time.
    See Chapter 49 starting on page 349.
 
    year should be a floating point number; quarter should be 0 for
    new moon, 1 for first quarter, 2 for full moon, and 3 for last
    quarter.  k = 0 corresponds to the new moon of 6 Jan 2000.  Use
    negative values of k for phases before 2000.
 
    Maximum error for years between 1980-2020 is less than 18 seconds
    with a mean error of 3.7 s.
    '''
    def norm(x):
        '''Normalize x to a number in [0, 360).
        '''
        while x < 0:
            x += 360
        while x >= 360:
            x -= 360
        return x
    if quarter not in range(4):
        raise ValueError("quarter must be 0, 1, 2, or 3")
    # Calculate the needed value of k
    k = floor((year - 2000)*12.3685) + quarter/4.0
    # T is time in Julian centuries since year 2000
    T = k/1236.85   # Eq 49.3, p 350
    # Time of mean phase of moon in Julian days
    jde = 2451550.09766 + k*29.530588861 + T*T*(0.00015437 +
          T*(-0.000000150 + T*0.00000000073)) # Eq 49.1, p 349
    E = 1 - 0.002516*T - 0.0000074*T*T  # Eq 47.6, pg 338
    # The following four items are in degrees
    M = 2.5534 + 29.10535670*k - 1.4e-6*T*T - 1.1e-7*T*T*T # Sun mean anomaly
    M1 = (201.5643 + 385.81693528*k + 0.0107582*T*T + 1.238e-5*T*T*T - 
        5.8e-8*T*T*T*T)  # Moon's mean anomaly
    F = (160.7108 + 390.67050284*k - 0.0016118*T*T - 2.27e-6*T*T*T + 
        1.1e-8*T*T*T*T) # Moon's argument of latitude
    # Longitude of the ascending node of the lunar orbit
    O = 124.7746 - 1.56375588*k + 0.0020672*T*T + 2.15e-6*T*T*T
    # Normalize
    M, M1, F, O = [norm(i) for i in (M, M1, F, O)]
    # Convert to radians
    M, M1, F, O = [i*d2r for i in (M, M1, F, O)]
    # ----- OK TO HERE ------
    A = (  
        # Planetary arguments in radians p 351
        (299.77 + 0.107408*k - 0.009173*T*T)*d2r,
        (251.88 + 0.016321*k)*d2r, (251.83 + 26.651886*k)*d2r,
        (349.42 + 36.412478*k)*d2r, (84.66  + 18.206239*k)*d2r,
        (141.74 + 53.303771*k)*d2r, (207.14 + 2.453732*k)*d2r,
        (154.84 + 7.306860*k)*d2r, (34.52  + 27.261239*k)*d2r,
        (207.19 + 0.121824*k)*d2r, (291.34 + 1.844379*k)*d2r,
        (161.72 + 24.198154*k)*d2r, (239.56 + 25.513099*k)*d2r,
        (331.55 + 3.592518*k)*d2r,
    )
    # Get correction to true (apparent phase) p 351
    if not quarter:
        # New moon
        corr = (
            -0.40720*sin(M1), +0.17241*E*sin(M), +0.01608*sin(2*M1),
            +0.01039*sin(2*F), +0.00739*E*sin(M1 - M), -0.00514*E*sin(M1 + M),
            +0.00208*E*E*sin(2*M), -0.00111*sin(M1 - 2*F),
            -0.00057*sin(M1 + 2*F), +0.00056*E*sin(2*M1 + M),
            -0.00042*sin(3*M1), +0.00042*E*sin(M + 2*F),
            +0.00038*E*sin(M - 2*F), -0.00024*E*sin(2*M1 - M),
            -0.00017*sin(O), -0.00007*sin(M1 + 2*M), +0.00004*sin(2*M1 - 2*F),
            +0.00004*sin(3*M), +0.00003*sin(M1 + M - 2*F),
            +0.00003*sin(2*M1 + 2*F), -0.00003*sin(M1 + M + 2*F),
            +0.00003*sin(M1 - M + 2*F), -0.00002*sin(M1 - M - 2*F),
            -0.00002*sin(3*M1 + M), +0.00002*sin(4*M1),
        )
    elif quarter == 2:
        # Full moon
        corr = (
            -0.40614*sin(M1), +0.17302*E*sin(M), +0.01614*sin(2*M1),
            +0.01043*sin(2*F), +0.00734*E*sin(M1 - M), -0.00515*E*sin(M1 + M),
            +0.00209*E*E*sin(2*M), -0.00111*sin(M1 - 2*F),
            -0.00057*sin(M1 + 2*F), +0.00056*E*sin(2*M1 + M),
            -0.00042*sin(3*M1), +0.00042*E*sin(M + 2*F),
            +0.00038*E*sin(M - 2*F), -0.00024*E*sin(2*M1 - M),
            -0.00017*sin(O), -0.00007*sin(M1 + 2*M), +0.00004*sin(2*M1 - 2*F),
            +0.00004*sin(3*M), +0.00003*sin(M1 + M - 2*F),
            +0.00003*sin(2*M1 + 2*F), -0.00003*sin(M1 + M + 2*F),
            +0.00003*sin(M1 - M + 2*F), -0.00002*sin(M1 - M - 2*F),
            -0.00002*sin(3*M1 + M), +0.00002*sin(4*M1),
        )
    else:
        # First or last quarter
        pass
        corr = ( # p 352
            -0.62801*sin(M1), +0.17172*E*sin(M), -0.01183*E*sin(M1 + M),
            +0.00862*sin(2*M1), +0.00804*sin(2*F), +0.00454*E*sin(M1 - M),
            +0.00204*E*E*sin(2*M), -0.00180*sin(M1 - 2*F),
            -0.00070*sin(M1 + 2*F), -0.00040*sin(3*M1),
            -0.00034*E*sin(2*M1 - M), +0.00032*E*sin(M + 2*F),
            +0.00032*E*sin(M - 2*F), -0.00028*E*E*sin(M1 + 2*M),
            +0.00027*E*sin(2*M1 + M), -0.00017*sin(O),
            -0.00005*sin(M1 - M - 2*F), +0.00004*sin(2*M1 + 2*F),
            -0.00004*sin(M1 + M + 2*F), +0.00004*sin(M1 - 2*M),
            +0.00003*sin(M1 + M - 2*F), +0.00003*sin(3*M),
            +0.00002*sin(2*M1 - 2*F), +0.00002*sin(M1 - M + 2*F),
            -0.00002*sin(3*M1 + M),
        )
    periodic1 = sum(corr)
    A1 = [
        0.000325, 0.000165, 0.000164, 0.000126, 0.000110, 0.000062, 0.000060,
        0.000056, 0.000047, 0.000042, 0.000040, 0.000037, 0.000035, 0.000023,
    ]
    periodic2 = sum([i*sin(j) for i, j in zip(A1, A)])
    W = (0.00306 - 0.00038*E*cos(M) + 0.00026*cos(M1) - 
         0.00002*cos(M1 - M) + 0.00002*cos(M1 + M) +
         0.00002*cos(2*F))
    if quarter in (1, 3):
        W = W if quarter == 1 else -W
    else:
        W = 0
    jde += periodic1 + periodic2 + W
    if 0:
        print("Debug output from TimeOfMoonPhase:")
        print("  T                                :  %.5f" % T)
        print("  E                                :  %.7f" % E)
        print("  M                                :  %.6f rad" % M)
        print("  M'                               :  %.6f rad" % M1)
        print("  F                                :  %.6f rad" % F)
        print("  O                                :  %.6f rad" % O)
        print("  Correction with harmonics (corr1):  %.5f" % periodic1)
        print("  Correction with A's (corr2)      :  %.5f" % periodic2)
        print("  W                                :  %.5f" % W)
        print("  JDE                              :  %.5f" % jde)
    return jde

def SunMeanLongitude(T):
    '''Returns sun's mean longitude in radians for time T in Julian
    centuries.  Equation 28.2 pg 183.  
    '''
    tau = T/10  # Julian millenia
    L0 = (280.4664567 + 360007.6982779*tau + 0.03032028*tau*tau +
        tau*tau*tau/49931 - tau**4/15300 - tau**5/2000000)
    L0 = fmod(L0, 360)  # In degrees
    if L0 < 0:
        L0 += 360
    return radians(L0)

def EquationOfTime(jd):
    '''Returns the Equation of Time in radians given the Julian day;
    see equation 28.1 pg 183.  The equation of time is the time
    difference between a sundial and the "mean" sun.

    To use month, day, year, calculate Julian day by
    JulianAstro(month, day, year).

    To convert radians to e.g. minutes use 15*degrees(EOT)/60.

    This is Smart's formula 28.3 pg 185.
    '''
    T = (jd - 2451545)/36525            # Time in Julian centuries
    epsilon = EclipticObliquity(jd)     # In radians
    L0 = SunMeanLongitude(T)            # In radians
    y = tan(epsilon/2)**2
    e = EarthOrbitEccentricity(T)
    M = SunMeanAnomaly(T)
    E = (y*sin(2*L0) - 2*e*sin(M) + 4*e*y*sin(M)*cos(2*L0) -
        y*y/2*sin(4*L0) - 5/4*e*e*sin(2*M))
    return E

_n_kepler_eqn = int(ceil(sys.float_info.dig/log10(2)))

def KeplerEquation(e, M, reltol=0):
    '''Returns eccentric anomaly E in radians by solving Kepler's
    equation 30.5 pg 195 via Sinnott's binary search algorithm on page
    206.  e is orbital eccentricity (dimensionless) and M is the mean
    anomaly in radians.  Meeus gives the number of iterations required
    as 3.32*digits, where digits is the platform's number of floating
    point digits.
 
    I've typed the BASIC algorithm in mostly verbatim and translated
    to python.  The numbers in the comments are the line numbers of
    the BASIC code.
 
    I've modified the program by stopping at a desired relative
    tolerance between iterations.  Note if you set e.g. reltol to
    about 1e-15 or less, the algorithm won't get any better -- it will
    just run its normal number of iterations.
    '''
    P1 = pi                                 # 100
    F = SGN(M); M = abs(M)/(2*P1)           # 110
    M = (M - int(M))*2*P1*F                 # 120
    if M < 0:  M += 2*P1                    # 130
    F = 1                                   # 140
    if M > P1:  F = -1                      # 150
    if M > P1:  M = 2*P1 - M                # 160
    E0 = P1/2; D = P1/4                     # 170
    Elast = E0/2
    for J in range(_n_kepler_eqn):          # 180
        M1 = E0 - e*sin(E0)                 # 190
        E0 = E0 + D*SGN(M - M1); D = D/2    # 200
        if reltol and J > 5:
            if abs((E0 - Elast)/Elast) <= reltol:
                break
        Elast = E0
    #NEXT J                                 # 210 
    E0 = E0*F                               # 220
    return E0

