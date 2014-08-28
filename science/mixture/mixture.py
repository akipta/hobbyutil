'''
Program to calculate mixtures.

Adapted from a C program at http://www.geocities.com/mklotz.geo/
'''

from __future__ import division
import sys, string


def InputFloat(prompt, default=""):
    val = 0.0
    while 1:
        s = "[%s] -> " % default
        if s == "[]":
            s = " -> "
        s = raw_input(prompt + " " + s)
        if not s:
            return float(default)
        try:
            val = float(s)
            return val
        except:
            print "Bad input -- try again"

def InputConcentration(prompt, default=""):
    val = 0.0
    while 1:
        val = InputFloat(prompt, default)
        if val < 0.0 or val > 100.0:
            print "Concentration should be between 0 and 100%.  Try again."
        else:
            return val

def PrintResults(VolA, VolB, VolMixture, ConcA, ConcB, ConcMixture):
    pa = ConcA/100
    pb = ConcB/100
    pm = ConcMixture/100
    if VolA and VolB:
        VolMixture = VolA+VolB
        ConcMixture = 100.*(VolA*pa+VolB*pb)/(VolA+VolB)
    elif VolA and ConcMixture:
        VolMixture = VolA*(pa-pb)/(pm-pb)
        VolB = VolMixture-VolA
    elif VolA and VolMixture:
        VolB = VolMixture-VolA
        ConcMixture = 100.*(VolA*pa+VolB*pb)/(VolA+VolB)
    elif VolB and ConcMixture:
        VolMixture = VolB*(pb-pa)/(pm-pa)
        VolA = VolMixture-VolB
    elif VolB and VolMixture:
        VolA = VolMixture-VolB
        ConcMixture = 100.*(VolA*pa+VolB*pb)/VolMixture
    elif VolMixture and ConcMixture:
        VolA = VolMixture*(pm-pb)/(pa-pb)
        VolB = VolMixture-VolA
    else:
        print "Not enough information"
        sys.exit(1)
    # Print results
    f = "= %.4g"
    p = "= %.4g%%"
    print
    print ("Amount of solution A        " + f) % VolA
    print ("Amount of solution B        " + f) % VolB
    print ("Amount of mixture           " + f) % VolMixture
    print ("Concentration of solution A " + p) % ConcA
    print ("Concentration of solution B " + p) % ConcB
    print ("Concentration of mixture    " + p) % ConcMixture

def main():
    print "Specify concentrations of both solutions.  If one solution is a"
    print "dilutant (e.g., pure water), enter its concentration as 0%.\n"
    ConcA = InputConcentration("Concentration of solution A in %?", 0)
    ConcB = InputConcentration("Concentration of solution B in %?", 0)
    print "Enter what you know; press return if not known.  You must enter"
    print "two data items to obtain a solution.\n"
    data_items_entered = 0
    VolA = VolB = VolMixture = ConcMixture = 0
    while 1:
        VolA = InputFloat("Amount of solution A?", VolA)
        if VolA: 
            data_items_entered += 1
        VolB = InputFloat("Amount of solution B?", VolB)
        if VolB: 
            data_items_entered += 1
        if data_items_entered != 2:
            VolMixture = InputFloat("Amount of mixture?", VolMixture)
            if VolMixture: 
                data_items_entered += 1
            if data_items_entered != 2:
                ConcMixture = InputConcentration("Concentration of mixture in %?", \
                                                 ConcMixture)
                if ConcMixture: 
                    data_items_entered += 1
                if data_items_entered != 2:
                    print "Insufficient data.  Try again."
                break
            else:
                break
        else:
            break
    PrintResults(VolA, VolB, VolMixture, ConcA, ConcB, ConcMixture)

main()
