'''
This is the core "manufacturing" module for the process quality
simulator.  The code below is intended to be easy to understand and is
commented to explain what's going on.  

This module provides one entry point function Manufacture(settings)
that takes a dictionary of settings as input and returns a dictionary
of results.  The calling module is responsible for getting the user's
input and printing the report.

---------------------------------------------------------------------------
Copyright (C) 2006, 2012 Don Peterson
Contact:  gmail.com@someonesdad1
  
                         The Wide Open License (WOL)
  
Permission to use, copy, modify, distribute and sell this software and its
documentation for any purpose is hereby granted without fee, provided that
the above copyright notice and this license appear in all copies.
THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF
ANY KIND. See http://www.dspguru.com/wide-open-license for more
information.
'''

import os, hashlib, numpy as np
from pdb import set_trace as xx

def Hash(thing):
    '''Return an MD5 hash for the string representation of an object.
    It's returned as a tuple so it can't accidentally be modified.
    '''
    h = hashlib.md5()
    h.update(repr(thing))
    return (h.hexdigest(), )

def _CheckSettings(S):
    '''Check basic logical requirements on the numbers in the settings
    dictionary S.  Note we don't check things like a process mean must
    be a float so that we can accomodate cases where the measured
    parameter is a discrete random variable.
    '''
    keys = (
        "ProcessDistribution",
        "ProcessMu",
        "ProcessSigma",
        "MeasurementDistribution",
        "MeasurementMu",
        "MeasurementSigma",
        "NumberOfLots",
        "PartsPerLot",
        "Specification",
    )
    for key in keys:
        if key not in S:
            raise ValueError("settings dictionary missing key '%s'" % key)
    if S["ProcessSigma"] < 0:
        raise ValueError('settings["ProcessSigma"] must be >= 0')
    if S["MeasurementSigma"] < 0:
        raise ValueError('settings["MeasurementSigma"] must be >= 0')
    nl = S["NumberOfLots"]
    if nl < 1 or not isinstance(nl, (int, long)):
        raise ValueError('settings["NumberOfLots"] must be an integer >= 0')
    ppl = S["PartsPerLot"]
    if ppl < 1 or not isinstance(ppl, (int, long)):
        raise ValueError('settings["PartsPerLot"] must be an integer >= 0')
    low, high = S["Specification"]
    if not isinstance(low, (int, long, float)):
        raise ValueError('settings["Specification"][0] must be a number')
    if not isinstance(high, (int, long, float)):
        raise ValueError('settings["Specification"][1] must be a number')
    if low > high:
        raise ValueError("First specification number must be <= second number")

def _AccumulateParts(lot, results):
    '''Accumulate the parts in results["parts"].  numpy's concatenate
    function takes two or more numpy arrays and concatenates them into
    one array:  np.concatenate(([1, 2], [3, 4])) --> [1, 2, 3, 4].
    '''
    for i in range(len(lot)):
        results["parts"][i] = np.concatenate((results["parts"][i], lot[i]))

def _SeparateParts(parts, S):
    '''Separate the parts numpy array into two arrays:  those that
    passed (i.e., are within specifications) and those that didn't.
    Numpy's compress function returns another array whose elements are
    the elements in the original array that satisfy the logical
    condition in the first argument.
    '''
    LowLimit, HighLimit = S["Specification"]
    passed  = np.compress(parts >= LowLimit, parts)
    passed  = np.compress(passed <= HighLimit, passed)
    failed_lo = np.compress(parts < LowLimit, parts)
    failed_hi = np.compress(parts > HighLimit, parts)
    failed  = np.concatenate((failed_lo, failed_hi))
    return passed, failed

def _MakeProductionLot(lot_number, S):
    '''Simulate the production of one lot as instructed by the
    settings dictionary S.
    '''
    # Get a random sample of parts from the production distribution
    mu, sigma = S["ProcessMu"], S["ProcessSigma"]
    distribution, n = S["ProcessDistribution"], S["PartsPerLot"]
    # The distribution function must be called with the mean, standard
    # deviation, and the number of random numbers to return.  There
    # are many types of distributions in tools like numpy and scipy;
    # if the particular random number generator doesn't have the
    # needed syntax, you can wrap it in a function that does.  The
    # following call makes n parts with the desired distribution.
    parts = distribution(mu, sigma, n)
    # Get two arrays that represent the true state of nature
    actual_good, actual_bad = _SeparateParts(parts, S)
    assert len(actual_good) + len(actual_bad) == n
    # Measure each part and classify them again.  First test the good
    # parts.
    mu, sigma = S["MeasurementMu"], S["MeasurementSigma"]
    distribution = S["MeasurementDistribution"]
    uncertainty = distribution(mu, sigma, len(actual_good))
    tested = actual_good + uncertainty
    good_tested_good, good_tested_bad = _SeparateParts(tested, S)
    assert len(good_tested_good) + len(good_tested_bad) == len(actual_good)
    # Test the bad parts
    uncertainty = distribution(mu, sigma, len(actual_bad))
    tested = actual_bad + uncertainty
    bad_tested_good, bad_tested_bad = _SeparateParts(tested, S)
    assert len(bad_tested_good) + len(bad_tested_bad) == len(actual_bad)
    # Return the classified parts representing the lot
    return (
        actual_good,
        actual_bad,
        good_tested_good,
        good_tested_bad,
        bad_tested_good,
        bad_tested_bad,
    )

def Manufacture(S):
    '''Simulate the manufacturing of parts as instructed by the
    numbers in the settings dictionary S.  Return a dictionary of the
    results.  The settings dictionary is not modified.

    The required keys in the settings dictionary S are:

        ProcessDistribution
        MeasurementDistribution  
            These must be functions that take arguments 
            (mean, standard_deviation, sample_size) and return a
            random sample of numbers from a particular distribution.

        Specification
            This is a tuple (a, b) such that if a part's quality
            parameter lies in this interval, then the part is declared
            a good part.

        The remaining keys are numbers:
            ProcessMu           Process mean
            ProcessSigma        Process standard deviation
            MeasurementMu       Measurement mean (i.e., bias)
            MeasurementSigma    Measurement std. deviation (i.e., uncertainty)
            NumberOfLots        How many lots to manufacture
            PartsPerLot         How many parts are in a lot
    '''
    # Add our file name to the list of files
    S["Files"] += [os.path.abspath(__file__).replace("\\", "/")]
    settings_hash = Hash(S)
    _CheckSettings(S)
    results = {
        "parts" : [
            # Note we use numpy's arange to ensure the array's type is
            # a float64.
            np.arange(0),      # Actual good parts made
            np.arange(0),      # Actual bad parts made
            np.arange(0),      # Good parts tested good
            np.arange(0),      # Good parts tested bad
            np.arange(0),      # Bad parts tested good
            np.arange(0),      # Bad parts tested bad
        ],
    }
    for lot_number in range(S["NumberOfLots"]):
        lot = _MakeProductionLot(lot_number, S)
        _AccumulateParts(lot, results)
    if settings_hash != Hash(S):
        raise RuntimeError("settings dictionary was changed")
    return results

if __name__ == "__main__":
    # Print a small test case
    import sys
    from numpy.random import normal, seed
    from sig import sig
    def out(*v, **kw):
        sep = kw.setdefault("sep", " ")
        nl  = kw.setdefault("nl", True)
        stream = kw.setdefault("stream", sys.stdout)
        if v:
            stream.write(sep.join([str(i) for i in v]))
        if nl:
            stream.write("\n")
    def Report():
        S = {
            "Files"                     : [],
            "ProcessDistribution"       : normal,
            "ProcessMu"                 : 10,
            "ProcessSigma"              : 1,
            "MeasurementDistribution"   : normal,
            "MeasurementMu"             : 0,
            "MeasurementSigma"          : 1,
            "NumberOfLots"              : 2,
            "PartsPerLot"               : 10,
            "Specification"             : (9.5, 10.5),
        }
        seed(8353475)  # Make the random number stream repeatable
        results = Manufacture(S)
        p = sig((S["ProcessMu"], S["ProcessSigma"]))
        m = sig((S["MeasurementMu"], S["MeasurementSigma"]))
        s = sig(S["Specification"])
        nl = str(S["NumberOfLots"])
        ppl = str(S["PartsPerLot"])
        out('''
Small manufacturing example:
  Process      (mu, sigma) = {p}
  Measureement (mu, sigma) = {m}
  Spec                     = {s}
  Number of lots           = {nl}
  Parts per lot            = {ppl}
'''[1:].format(**locals()))
        out("Good parts made =\n",        sig(results["parts"][0]))
        out("Bad parts made  =\n",        sig(results["parts"][1]))
        out("Good parts tested good =\n", sig(results["parts"][2]))
        out("Good parts tested bad  =\n", sig(results["parts"][3]))
        out("Bad parts tested good  =\n", sig(results["parts"][4]))
        out("Bad parts tested bad   =\n", sig(results["parts"][5]))
    Report()
