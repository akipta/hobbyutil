'''
Provides a thread class that will calculate the dimensions of Unified
National thread forms in inches.  Formulas taken from ASME B1.1-1989.
'''

# Copyright (C) 2007 Don Peterson
# Contact:  gmail.com@someonesdad1

#
#

from __future__ import division
from math import pow, sqrt
from lwtest import run

class UnifiedThread:
    '''Initialize with basic diameter in inches, threads per inch,
    class, and length of engagement in units of the basic diameter.
    You'll need to refer to the ASME standard for lengths of engagement
    greater than 1.5 times the major diameter.
    '''
    sqrt3 = sqrt(3)
    def __init__(self, basic_diameter, tpi, Class=2, length_of_engagement=1):
        if basic_diameter <= 0:
            raise ValueError("Basic diameter must be > 0")
        if tpi <= 0:
            raise ValueError("Threads per inch (tpi) must be > 0")
        if Class not in (1, 2, 3):
            raise ValueError("Invalid value for Class (must be 1, 2, or 3)")
        if not (0.1 <= length_of_engagement <= 1.5):
            msg = "Length of engagement must be between 0.1 and 1.5"
            raise ValueError(msg)
        self.D = basic_diameter
        self.P = 1/tpi
        self.Class = Class
        self.length_of_engagement = length_of_engagement
    def Allowance(self):
        if self.Class == 3:
            return 0.0
        return 0.3*self.Class2PDtol()
    def Class2PDtol(self):
        return 0.0015*(pow(self.D, 1/3) + \
                       sqrt(self.length_of_engagement*self.D) + \
                       10*pow(self.P*self.P, 1/3))
    def Dmax(self):
        'External thread max major diameter'
        return self.D - self.Allowance()
    def Dmin(self):
        'External thread min major diameter'
        c = 0.06
        if self.Class == 1:
            c = 0.09
        return self.Dmax() - c*pow(self.P*self.P, 1/3)
    def Emax(self):
        'External thread max pitch diameter'
        return self.D - self.Allowance() - 0.375*self.sqrt3*self.P
    def Emin(self):
        'External thread min pitch diameter'
        if self.Class == 1:
            c = 1.5
        elif self.Class == 2:
            c = 1
        else:
            c = 0.75
        return self.Emax() - c*self.Class2PDtol()
    def dmax(self):
        'Internal thread max minor diameter'
        if self.Class == 1 or self.Class == 2:
            if self.D < 1/4:
                tol = 0.05*pow(self.P*self.P, 1/3) + 0.03*self.P/self.D - 0.002
                tol = min(tol, 0.394*self.P)
                tol = max(tol, 0.25*self.P - 0.4*self.P*self.P)
            else:
                if 1/self.P >= 4:
                    tol = 0.25*self.P - 0.4*self.P*self.P
                else:
                    tol = 0.15*self.P
        else:
            tol = 0.05*pow(self.P*self.P, 1/3) + 0.03*self.P/self.D - 0.002
            tol = min(tol, 0.394*self.P)
            if 1/self.P >= 13:
                tol = max(tol, 0.23*self.P - 1.5*self.P*self.P)
            else:
                tol = max(tol, 0.120*self.P)
        return tol + self.dmin()
    def dmin(self):
        'Internal thread min minor diameter'
        return self.D - 0.625*self.sqrt3*self.P
    def emax(self):
        'internal thread max pitch diameter'
        if self.Class == 1:
            c = 1.95
        elif self.Class == 2:
            c = 1.3
        else:
            c = 0.975
        return self.emin() + c*self.Class2PDtol()
    def emin(self):
        'internal thread min pitch diameter'
        return self.dmin() + self.sqrt3/4*self.P
    def __str__(self):
        return "UnifiedThread(D=%s, tpi=%s)" % (self.D, 1/self.P)

def Test_asme():
    eps = 0.0001
    # Check the formulas on a 1/4-20 thread
    u = UnifiedThread(1/4, 20, Class=1)
    assert(abs(u.Class2PDtol() - 0.00373) <= eps)
    assert(abs(u.Allowance() - 0.0011) <= eps)
    # Class 1 thread
    assert(abs(u.Dmin() - 0.2367) <= eps)
    assert(abs(u.Dmax() - 0.2489) <= eps)
    assert(abs(u.Emin() - 0.2108) <= eps)
    assert(abs(u.Emax() - 0.2164) <= eps)
    assert(abs(u.dmin() - 0.1959) <= eps)
    assert(abs(u.dmax() - 0.2074) <= eps)
    assert(abs(u.emin() - 0.2175) <= eps)
    assert(abs(u.emax() - 0.2248) <= eps)
    # Class 2 thread
    u.Class = 2
    assert(abs(u.Dmin() - 0.2408) <= eps)
    assert(abs(u.Dmax() - 0.2489) <= eps)
    assert(abs(u.Emin() - 0.2127) <= eps)
    assert(abs(u.Emax() - 0.2164) <= eps)
    assert(abs(u.dmin() - 0.1959) <= eps)
    assert(abs(u.dmax() - 0.2074) <= eps)
    assert(abs(u.emin() - 0.2175) <= eps)
    assert(abs(u.emax() - 0.2223) <= eps)
    # Class 3 thread
    u.Class = 3
    assert(abs(u.Dmin() - 0.2419) <= eps)
    assert(abs(u.Dmax() - 0.2500) <= eps)
    assert(abs(u.Emin() - 0.2147) <= eps)
    assert(abs(u.Emax() - 0.2175) <= eps)
    assert(abs(u.dmin() - 0.1959) <= eps)
    assert(abs(u.dmax() - 0.2067) <= eps)
    assert(abs(u.emin() - 0.2175) <= eps)
    assert(abs(u.emax() - 0.2211) <= eps)

if __name__ == "__main__":
    run(globals())
