'''
Script to print moon phase times for a given year, which should be the
single parameter passed on the command line.  The times will be converted
to your local time by the ut_offset value, which gets added to the 
calculated universal time for the phase.  You'll want to modify the
ConvertToLocalTime() function to make its output appropriate for your
location.  You can also make it do nothing, which results in the 
program printing its times in UT.

Converted to python from my moon.c program from June 1995.  Algorithms
from Meeus, Astronomical Formulas for Calculators, 2nd ed., 1982.

----------------------------------------------------------------------

Copyright (C) 2005 Don Peterson
Contact:  gmail.com@someonesdad1

                         The Wide Open License (WOL)

Permission to use, copy, modify, distribute and sell this software and its
documentation for any purpose is hereby granted without fee, provided that
the above copyright notice and this license appear in all source copies.
THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF
ANY KIND. See http://www.dspguru.com/wide-open-license for more
information.
'''

#########################################################################

from __future__ import division
from math import pi, sin, cos, floor
from out import out
from meeus import IsDST
import sys, time

from pdb import set_trace as xx


# The script will correct universal times to your local time zone's
# time.  This time zone is assumed to be in the US so that the
# meeus.IsDST function works correctly.  
UT_correction = 7  # Hours to subtract from UT to get your local time
zone_name = "Mountain"
UT_correction = 0  # Hours to subtract from UT to get your local time xx


NEW   = 0
FIRST = 1
FULL  = 2
LAST  = 3
d2r   = pi/180.0    # Converts degrees to radians
desired_year = 0

# GetJulianFromPhase  Derive the Julian day number corresponding to the 
# number k.  k is the integer corresponding to new moon and phase is 0 
# for new, 1 for first quarter, 2 for full, and 3 for last quarter.
# Returns a float.  From Meeus, pg 159.

def GetJulianFromPhase(k, phase):
    if phase != NEW and phase != FIRST and phase != FULL and phase != LAST:
        raise "Illegal phase value"
    k1 = k + phase/4.0
    T = k1/1236.85
    T2 = T*T
    T3 = T2*T
    # Get time of mean phase
    julian = 2415020.75933 + 29.53058868*k1 + 1.178e-4*T2 - 1.55e-7*T3 \
             +3.3e-4*sin(d2r*(166.56 + 132.87*T - 0.009173*T2))
    # Compute the corrections to get the time of true phase
    M      = 359.2242 + 29.10535608*k - 3.33e-5*T2 - 3.47e-6*T3
    Mprime = 306.0253 + 385.81691806*k + 0.0107306*T2 + 1.236e-5*T3
    F      = 21.2964 + 390.67050646*k - 1.6528e-3*T2 - 2.39e-6*T3
    # Adjust these values to the interval [0, 360] 
    M      = M - 360.0*(floor(M/360.0))
    Mprime = Mprime - 360.0*(floor(Mprime/360.0))
    F      = F - 360.0*(floor(F/360.0))
    # Convert them to radians
    M      = M*d2r
    Mprime = Mprime*d2r
    F      = F*d2r
    # Perform the corrections
    if phase == NEW or phase == FULL:
        correction = (0.1734 - 3.93e-4*T)*sin(M) \
                 + 0.0021*sin(2*M) \
                 - 0.4068*sin(Mprime) \
                 + 0.0161*sin(2*Mprime) \
                 - 0.0004*sin(3*Mprime) \
                 + 0.0104*sin(2*F) \
                 - 0.0051*sin(M+Mprime) \
                 - 0.0074*sin(M-Mprime) \
                 + 0.0004*sin(2*F+M) \
                 - 0.0004*sin(2*F-M) \
                 - 0.0006*sin(2*F+Mprime) \
                 + 0.0010*sin(2*F-Mprime) \
                 + 0.0005*sin(M+2*Mprime)
    else:
        correction = (0.1721 - 0.0004*T)*sin(M) \
                 + 0.0021*sin(2*M) \
                 - 0.6280*sin(Mprime) \
                 + 0.0089*sin(2*Mprime) \
                 - 0.0004*sin(3*Mprime) \
                 + 0.0079*sin(2*F) \
                 - 0.0119*sin(M+Mprime) \
                 - 0.0047*sin(M-Mprime) \
                 + 0.0003*sin(2*F+M) \
                 - 0.0004*sin(2*F-M) \
                 - 0.0006*sin(2*F+Mprime) \
                 + 0.0021*sin(2*F-Mprime) \
                 + 0.0003*sin(M+2*Mprime) \
                 + 0.0004*sin(M-2*Mprime) \
                 - 0.0003*sin(2*M+Mprime)
    julian = julian + correction
    if phase == FIRST:
        julian = julian + 0.0028 - 0.0004*cos(M) + 0.0003*cos(Mprime)
    if phase == LAST:
        julian = julian + -0.0028 + 0.0004*cos(M) - 0.0003*cos(Mprime)
    return julian

# Returns a structure that contains the calendar date associated 
# with a Julian day.  The tuple is (year, month, day) where year
# and month are integers; day is a float.  The Julian parameter
# is expected to be a float.  Ref. Meeus pg 26.

def caldate(julian):
    if julian == "":
        return
    julian = julian + 0.5
    Z = int(julian)
    F = julian - Z
    if Z < 2299161:
        A = Z
    else:
        alpha = int((Z-1867216.25)/36524.25)
        A = Z + 1 + alpha - int(alpha/4)
    B = A + 1524
    C = int((B - 122.1)/365.25)
    D = int(365.25*C)
    E = int((B - D)/30.6001)
    day = B - D - int(30.6001*E) + F
    if E < 13.5:
        month = int(E - 1)
    else:
        month = int(E - 13)
    if month > 2.5:
      year =  int(C - 4716)
    else:
      year =  int(C - 4715)
    return (year, month, day)

# UnivTimeCorrect  Ref. Meeus pg 35.  Calculates the correction to ephemeris
# time to get universal time.  The correction is gotten purely by his 
# approximate formula; the error is a maximum of 1.2 minutes between 1710
# and 1987.  

def UnivTimeCorrect(year):
  T = (year - 1900.0)/100.0
  return (0.41 + 1.2053*T + 0.4992*T*T)/60.0

def GetPhaseData(desired_year, phase):
    # Return a list of the Julian days for the given year of each phase.
    # Start by getting a k that is in the middle of the previous year
    if desired_year < 1900:
        raise "Desired year should be > 1900"
    k1 = (desired_year - .5 - 1900) * 12.3685
    k = int(k1)
    done = 0
    data = []
    while not done:
        julian = GetJulianFromPhase(k, phase)
        year, month, day = caldate(julian)
        if year == desired_year:
            data.append(julian)
        if year > desired_year:
            done = 1
        k = k + 1
    return data

def GetItem(julian):
    '''Return a formatted string that represents the date and time of
    a given Julian day.  The times will be corrected to Mountain time
    and take into account Daylight Saving Time.
    '''
    month_name = ["", "Jan", "Feb", "Mar", "Apr", "May",
           "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    try:
        # Convert to local standard time by subtracting a constant
        # from UT.
        if UT_correction:
            j = julian - UT_correction/24.0
            year, month, day = caldate(j)
            if IsDST(month, day, year):
                # It's Daylight Saving Time, so add 1 hour
                j = julian + 1/24.0
                year, month, day = caldate(j)
        else:
            year, month, day = caldate(julian)
    except Exception:
        return " " * 14
    Day = int(day)
    fraction = day - Day
    hours = 24.0*fraction
    decimal_time = hours + 12.0 + UnivTimeCorrect(year)
    if decimal_time > 24.0:
        day = day + 1
        decimal_time = decimal_time - 24.0
    minutes = int((decimal_time - int(decimal_time))*60)
    return "  %2d %s %02d:%02d " % \
        (Day, month_name[month], int(decimal_time), minutes)

def FixArrays(new, first, full, last):
    '''Make the arrays the same length as the longest by appending
    null strings.
    '''
    max_lines = max(len(new), len(first), len(full), len(last))
    def Adjust(array, numlines):
        while len(array) < numlines:
            array.append("")
    Adjust(new, max_lines)
    Adjust(first, max_lines)
    Adjust(full, max_lines)
    Adjust(last, max_lines)

def main():
    desired_year = time.gmtime()[0]  # Default to current year
    if len(sys.argv) > 1:
        desired_year = int(sys.argv[1])
    # Get a list of the phase times in Julian days.  Each element of the
    # list is another list containing the Julian day and the phase number.
    results, zn = [], zone_name
    new   = GetPhaseData(desired_year, NEW)
    first = GetPhaseData(desired_year, FIRST)
    full  = GetPhaseData(desired_year, FULL)
    last  = GetPhaseData(desired_year, LAST)
    FixArrays(new, first, full, last)
    indent = " " * 12
    out('''
                    Moon phases for {desired_year}
          (Times are {zn} time corrected for DST)'''[1:].format(**locals()))
    out('''
      New             Full          First Qtr       Last Qtr
  ------------    ------------    ------------    ------------
'''[:-1])
    fmt = "%-15s "
    for i in range(len(new)):
        out(fmt % GetItem(new[i]), nl=0)
        out(fmt % GetItem(full[i]), nl=0)
        out(fmt % GetItem(first[i]), nl=0)
        out(fmt % GetItem(last[i]))

main()
'''
Test data from USNO:

                       2014 Phases of the Moon
                            Universal Time

        New Moon   First Quarter       Full Moon    Last Quarter    

         d  h  m         d  h  m         d  h  m         d  h  m

    Jan  1 11 14    Jan  8  3 39    Jan 16  4 52    Jan 24  5 20
    Jan 30 21 38    Feb  6 19 22    Feb 14 23 53    Feb 22 17 15
    Mar  1  8 00    Mar  8 13 27    Mar 16 17 08    Mar 24  1 46
    Mar 30 18 45    Apr  7  8 31    Apr 15  7 42    Apr 22  7 52
    Apr 29  6 14    May  7  3 15    May 14 19 16    May 21 12 59
    May 28 18 40    Jun  5 20 39    Jun 13  4 11    Jun 19 18 39
    Jun 27  8 08    Jul  5 11 59    Jul 12 11 25    Jul 19  2 08
    Jul 26 22 42    Aug  4  0 50    Aug 10 18 09    Aug 17 12 26
    Aug 25 14 13    Sep  2 11 11    Sep  9  1 38    Sep 16  2 05
    Sep 24  6 14    Oct  1 19 32    Oct  8 10 51    Oct 15 19 12
    Oct 23 21 57    Oct 31  2 48    Nov  6 22 23    Nov 14 15 15
    Nov 22 12 32    Nov 29 10 06    Dec  6 12 27    Dec 14 12 51
    Dec 22  1 36    Dec 28 18 31                            

Script's output for 2014 with no conversion from UT:

                    Moon phases for 2014
                        Times are UT

      New             Full          First Qtr       Last Qtr
  ------------    ------------    ------------    ------------
   1 Jan 23:17    16 Jan 17:39     8 Jan 09:45    23 Jan 03:59  
  30 Jan 09:43    14 Feb 04:05     7 Feb 17:31    21 Feb 11:45  
   1 Mar 20:05    16 Mar 14:27     8 Mar 01:39    23 Mar 19:53  
  30 Mar 06:50    14 Apr 01:12     6 Apr 11:03    21 Apr 05:17  
  29 Apr 18:20    14 May 12:42     6 May 22:18    21 May 16:32  
  28 May 06:45    12 Jun 01:07     4 Jun 11:30    19 Jun 05:43  
  27 Jun 20:12    12 Jul 14:35     4 Jul 02:30    19 Jul 20:44  
  26 Jul 10:45    10 Aug 05:07     3 Aug 19:04    18 Aug 13:18  
  25 Aug 02:15     9 Sep 20:37     2 Sep 12:45    16 Sep 06:59  
  24 Sep 18:15     9 Oct 12:37     1 Oct 06:45    16 Oct 01:00  
  23 Oct 09:58     7 Nov 04:20    31 Oct 23:59    15 Nov 18:14  
  22 Nov 00:34     7 Dec 18:56    30 Nov 15:16    14 Dec 09:31  
  22 Dec 13:38                    29 Dec 03:55                  

Conclusion:  the times are off
'''
