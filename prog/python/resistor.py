'''
Select from on-hand resistors to make a voltage divider or a given
resistance value from a pair of resistors in series or parallel.

Change the on_hand global variable to reflect the resistors you have.

---------------------------------------------------------------------------
Copyright (C) 2013 Don Peterson
Contact:  gmail.com@someonesdad1
  
                         The Wide Open License (WOL)
  
Permission to use, copy, modify, distribute and sell this software and its
documentation for any purpose is hereby granted without fee, provided that
the above copyright notice and this license appear in all copies.
THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF
ANY KIND. See http://www.dspguru.com/wide-open-license for more
information.
'''

import sys, os, getopt
from math import *
from itertools import combinations
from sig import sig
from fpformat import FPFormat
from columnize import Columnize
from color import fg, normal, yellow as highlight

from pdb import set_trace as xx
import debug
if 1:
    debug.SetDebugger()



fp = FPFormat()
fp.trailing_dp = False

# On-hand resistor values.  Change these entries to match what you have.
on_hand = '''
0.025 0.2 0.27 0.33

1 2.2 4.6 8.3

10.1 12 14.7 15 17.8 22 27 28.4 30 31.6 33 35 38.4 46.3 50 55.5 61.8 67 75 
78 81

100 110 115 121 150 162 170 178 196 215 220 237 268 270 287 316 330 349 388 
465 500 513 546 563 617 680 750 808 822 980

1k 1.1k 1.18k 1.21k 1.33k 1.47k 1.5k 1.62k 1.78k 1.96k 2.16k 2.2k 2.37k
2.61k 2.72k 3k 3.16k 3.3k 3.47k 3.82k 4.64k 5k 5.53k 6.8k 6.84k 8k 8.3k 9.09k

10k 11.8k 12.1k 13.3k 15k 16.2k 17.8k 18k 19.5k 20k 22k 26.2k 33k 39k 42.4k
46k 51k 55k 67k 75k 82k

100k 120k 147k 162k 170k 180k 220k 263k 330k 390k 422k 460k 464k 560k 674k 820k

1M 1.2M 1.5M 1.7M 1.9M 2.2M 2.4M 2.6M 2.8M 3.2M 4M 4.8M 5.6M 6M 8.7M 10M
16M 23.5M
'''

# The following array is used to define what decades of E-series
# resistors are included.
powers_of_10 = (-1, 0, 1, 2, 3, 4, 5, 6, 7)

# EIA recommended resistor values.  From
# http://www.radio-electronics.com/info/data/resistor/resistor_standard_values.php
EIA = {
     6 : (1.0, 1.5, 2.2, 3.3, 4.7, 6.8),
    12 : (1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2),
    24 : (1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
          3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1),
    48 : (1.00, 1.05, 1.10, 1.15, 1.21, 1.27, 1.33, 1.40, 1.47, 1.54, 
          1.62, 1.69, 1.78, 1.87, 1.96, 2.05, 2.15, 2.26, 2.37, 2.49,
          2.61, 2.74, 2.87, 3.01, 3.16, 3.32, 3.48, 3.65, 3.83, 4.02,
          4.22, 4.42, 4.64, 4.87, 5.11, 5.36, 5.62, 5.90, 6.19, 6.49,
          6.81, 7.15, 7.50, 7.87, 8.25, 8.66, 9.09, 9.53),
    96 : (1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24,
          1.27, 1.30, 1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58,
          1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 1.91, 1.96, 2.00,
          2.05, 2.10, 2.16, 2.21, 2.36, 2.32, 2.37, 2.43, 2.49, 2.55,
          2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09, 3.16, 3.24,
          3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
          4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.91, 5.11, 5.23,
          5.36, 5.49, 5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65,
          6.81, 6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06, 8.25, 8.45,
          8.66, 8.87, 9.09, 9.31, 9.59, 9.76),
}

# These are the SI prefixes likely to be used
prefixes = {
    "n" : -9,
    "u" : -6,
    "m" : -3,
    "k" :  3,
    "M" :  6,
    "G" :  9,
    "T" : 12,
}

def out(*v, **kw):
    sep = kw.setdefault("sep", " ")
    nl  = kw.setdefault("nl", True)
    stream = kw.setdefault("stream", sys.stdout)
    if v:
        stream.write(sep.join([str(i) for i in v]))
    if nl:
        stream.write("\n")

def Error(msg, status=1):
    out(msg, stream=sys.stderr)
    exit(status)

def Usage(d, status=1):
    name = sys.argv[0]
    pmin = "%.1g" % (10**min(powers_of_10))
    pmax = "%.1g" % (10**(max(powers_of_10) + 1))
    num_entries = d["-n"]
    digits = d["-d"]
    s = '''
Usage:  {name} [options] action [parameters]

Actions:
  D[ivider] R1 R2 R3 ...
      Prints out the total resistance and divider ratios of a string of
      resistors used as e.g. a front-end to a voltmeter.
  d[ivider] ratio
      Finds the pairs of resistors that yield the given ratio within the
      desired tolerance (defaults to 1%; use -t to change).
  dd[ivider] total_resistance ratio1 ratio2 [ratio3...]
      Designs a voltage divider that has the indicated total resistance in
      ohms and n ratios.  You'll get a list of n+1 resistors that will make
      the divider.
  r[esistor] resistance
      Finds pairs of resistors that will yield the desired resistance by
      using the pairs in series or parallel.  The default search tolerance
      is 1%; use the -t option to change.
  R[esistor] resistance
      Finds a set of resistors that sums to as close as possible to the
      desired resistance value.  You'd then connect these in series.
  q[uotient] ratio
      Finds pairs of resistors that have the given ratio.
  l[ist]
      List on-hand and EIA resistor values.
  p[airs] file target {{s|p}}
      For the (probably measured) resistance values in file, one value per
      line and a line separating the two groups, calculate the combinations
      of either serial (s) or parallel (p) resistance values.  The output
      will be presented as a % deviation from the target value for all the
      combinations.

Options:
  -c file
       Specifies a set of on-hand resistors to use instead of the
       internally defined ones.  This data file consists of
       whitespace-separated values of the forms 22.3, 22.3k, 22.3M, or
       22.3G.  You can, of course, use the usual floating point exponential
       notation instead such as 22.3e0, 22.3e3, etc.
  -d digits
       Specify the number of significant digits in the output.  The default
       is {digits}.
  -e num
       Specifies that various resistor series should be used for searching
       rather than the on-hand resistors given by the configuration file.
       num is the number from the following allowed series: E6, E12, E24,
       E48, E96 from {pmin} to {pmax} ohms.
  -n num
       Limit output to num entries.  Default is {num_entries}.
  -p
       Only show parallel combinations.
  -r total_resistance:percent_tolerance
       (For voltage divider calculations only) Specifies the total
       resistance of the divider and the tolerance percentage on this
       value.  Only resistor pairs that have this total resistance within
       the specified tolerance will be printed.  
  -s
       Only show series combinations.
  -t percent_tolerance
       Changes the tolerance for searching.  For the voltage divider
       search, gives the ratio tolerance.  For the resistor pair search,
       the total resistances within the tolerance of the desired value will
       be printed.
'''[1:-1]
    out(s.format(**locals()))
    sys.exit(status)

def ParseCommandLine(d):
    d["-c"] = None      # Configuration file
    d["-d"] = 4         # Significant figures
    d["-e"] = None      # Which EIA series to use
    d["-n"] = 30        # How many to show if get lots from search
    d["-p"] = False     # Only show parallel
    d["-r"] = None      # Specify total divider resistance
    d["-s"] = False     # Only show series
    d["-t"] = 0.01      # Tolerance
    if len(sys.argv) < 2:
        Usage(d)
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "c:d:e:n:pr:st:")
    except getopt.GetoptError as e:
        msg, option = e
        out(msg)
        exit(1)
    for opt in optlist:
        if opt[0] == "-c":
            d["-c"] = opt[1]
        if opt[0] == "-d":
            d["-d"] = int(opt[1])
            if d["-d"] < 1 or d["-d"] > 15:
                out("Bad argument for -d option")
                exit(1)
        if opt[0] == "-e":
            d["-e"] = int(opt[1])
            if d["-e"] not in (6, 12, 24, 48, 96):
                Error("-e option's value must be 6, 12, 24, 48, or 96")
        if opt[0] == "-n":
            try:
                d["-n"] = int(opt[1])
                if d["-n"] < 1:
                    raise Exception()
            except Exception:
                Error("-n option must be integer > 0")
        if opt[0] == "-p":
            d["-p"] = True
        if opt[0] == "-r":
            s = opt[1]
            if ":" in s:
                f = s.split(":")
                if len(f) != 2:
                    Error("Bad form for option -r")
                # d["-r"] is (total_resistance, tolerance)
                d["-r"] = (float(f[0]), float(f[1])/100)
                if d["-r"][1] <= 0:
                    Error("-r:  percent tolerance must be > 0")
            else:
                Error("-r option must contain a ':' character")
        if opt[0] == "-s":
            d["-s"] = True
        if opt[0] == "-t":
            d["-t"] = float(opt[1])/100
            if d["-t"] <= 0:
                Error("-t:  percent tolerance must be > 0")
    if not args:
        Usage(d)
    if args[0][:2] == "dd":
        cmd = "dd"
    else:
        cmd = args[0][0]
    if cmd not in ("d", "D", "dd", "l", "p", "q", "r", "R"):
        Error("Command '%s' not recognized" % args[0])
    if cmd in ("d", "q", "r", "R"):
        if len(args) != 2:
            Usage(d)
    elif cmd in ("dd",):
        if len(args) < 3:
            Usage(d)
    elif cmd in ("l",):
        if len(args) != 1:
            Usage(d)
    args[0] = cmd
    return args

def GetResistors(d):
    R, p = [], {"m":1e-3, "k":1e3, "M":1e6, "G":1e9, "T":1e12}
    if d["-e"] is not None:
        # Use EIA resistors
        for p in powers_of_10:
            for i in EIA[d["-e"]]:
                R.append(i*10**p)
    else:
        # Use on-hand resistors
        for line in on_hand[1:-1].split("\n"):
            for i in line.split():
                if i[-1] not in "0123456789":
                    c = i[-1]
                    try:
                        r = float(i[:-1])*p[c]
                    except KeyError:
                        Error("'%s' is unsupported SI prefix" % c)
                else:
                    r = float(i)
                R.append(r)
    d["R"] = R

def Div(d, ratio, R1, R2):
    '''If the divider ratio of R1 and R2 (R1 on top) is within the desired
    tolerance of ratio, then include it in the set d["divider"].
    '''
    s, t = R1 + R2, d["-t"]
    if d["-r"] is not None:
        R, Rt = d["-r"]
        if not ((1 - Rt)*R <= s <= (1 + Rt)*R):
            return
    rat1, rat2 = R1/s, R2/s
    if (1 - t)*ratio <= rat1 <= (1 + t)*ratio:
        d["divider"].add((rat1, R1, R2))
    elif (1 - t)*ratio <= rat2 <= (1 + t)*ratio:
        d["divider"].add((rat2, R2, R1))

def Divider(d, ratio):
    d["divider"] = set()
    # First check using equal resistors
    for R in d["R"]:
        Div(d, float(ratio), R, R)
    for R1, R2 in combinations(d["R"], 2):
        Div(d, float(ratio), R1, R2)
    # Print report
    div = list(d["divider"])
    if not div:
        out("No divider can be made")
        return
    div.sort()
    out("Voltage divider with ratio = ", ratio, ", tolerance = ", 
        sig(d["-t"]*100, 2), "%", sep="")
    out()
    out("% dev from")
    out("desired ratio       R1           R2      Total Res.")
    out("-------------   ----------   ----------  ----------")
    for rat, r1, r2 in div:
        dev = 100*((rat - float(ratio))/float(ratio))
        pct = sig(dev)
        if dev >= 0:
            pct = " " + pct
        R1, R2, R = fp.engsi(r1), fp.engsi(r2), fp.engsi(r1 + r2)
        if not dev:
            fg(highlight)
        out("   {0:10}   {1:^10}   {2:^10}   {3:^10}".format(pct, R1, R2, R))
        normal()

def Resistance(d, resistance):
    d["resistances"] = set()
    # First see if we have an exact match
    if resistance in d["R"]:
        d["resistances"].add((resistance, "e", resistance, 0))
    else:
        # First check using equal resistors
        for R in d["R"]:
            Res(d, resistance, R, R)
        for R1, R2 in combinations(d["R"], 2):
            Res(d, resistance, R1, R2)
    res = list(d["resistances"])
    if not res:
        out("No resistor combinations that meet tolerance")
        return
    # Check if we have too many entries; if so, whittle down the list to
    # the closest N.
    clipped = False
    if len(res) > d["-n"]:
        # Sort by absolute value of tolerance
        tol = lambda tgt, val: abs(val - tgt)/val
        r = [(tol(resistance, i[0]), i) for i in res]   # Decorate with abs val
        r.sort()
        res = [i[1] for i in r[:d["-n"]]]
        clipped = True
    # Print report
    res.sort()
    out("Desired resistance = ", d["desired"], " = ", sig(d["res"]) + 
        ", tolerance = ", sig(d["-t"]*100, 2), "%", sep="")
    if clipped:
        out("Closest %d matches shown" % d["-n"])
    out()
    out("% dev from")
    out("desired res.        R1           R2      Connection")
    out("-------------   ----------   ----------  ----------")
    for val, c, r1, r2 in res:
        dev = 100*((val - resistance)/resistance)
        pct = sig(dev, 2)
        if dev >= 0:
            pct = " " + pct
        R1, R2 = fp.engsi(r1), fp.engsi(r2)
        conn = {"s":"series", "p":"parallel", "e":"exact"}[c]
        if (d["-p"] and c == "s") or (d["-s"] and c == "p"):
            continue
        if not dev:
            fg(highlight)
        if c == "e":
            out("   {0:10}   {1:^10}                {2}".format(pct, R1, conn))
        else:
            out("   {0:10}   {1:^10}   {2:^10}   {3}".format(pct, R1, R2, conn))
        normal()

def Res(d, R, R1, R2):
    '''See if R1 and R2 sum to R within the desired tolerance; if so, 
    include it in the set d["resistances"].
    '''
    t = d["-t"]
    ser = R1 + R2
    if (1 - t)*R <= ser <= (1 + t)*R:
        d["resistances"].add((ser, "s", R1, R2))
    par = 1/(1/R1 + 1/R2)
    if (1 - t)*R <= par <= (1 + t)*R:
        d["resistances"].add((par, "p", R1, R2))

def Quotient(d, ratio):
    # Ignore a requested ratio of 1, as any pair of resistors will work
    if ratio == 1:
        out("Quotient cannot be 1")
        exit(1)
    d["resistances"], t, Ratio = set(), d["-t"], float(ratio)
    for R1, R2 in combinations(d["R"], 2):
        q1 = R1/R2
        q2 = 1/q1
        if (1 - t)*Ratio <= q1 <= (1 + t)*Ratio:
            d["resistances"].add((q1, R1, R2))
        elif (1 - t)*Ratio <= q2 <= (1 + t)*Ratio:
            d["resistances"].add((q2, R2, R1))
    # Print report
    res = list(d["resistances"])
    if not res:
        out("No resistor combinations that meet tolerance")
        return
    res.sort()
    out("Desired ratio = ", ratio, ", tolerance = ",
        sig(d["-t"]*100, 2), "%", sep="")
    out()
    out("% dev from")
    out("desired ratio       R1           R2")
    out("-------------   ----------   ----------")
    for val, r1, r2 in res:
        dev = 100*((val - Ratio)/Ratio)
        pct = sig(dev, 2)
        if dev >= 0:
            pct = " " + pct
        R1, R2 = fp.engsi(r1), fp.engsi(r2)
        if not dev:
            fg(highlight)
        out("   {0:10}   {1:^10}   {2:^10}".format(pct, R1, R2))
        normal()

def List(d):
    out("On-hand resistors:\n")
    out(on_hand[1:-1])
    out("-"*70)
    out("EIA resistance series:")
    for n in (6, 12, 24, 48, 96):
        out("E%d:" % n)
        digits = 2 if n < 48 else 3
        s = []
        for num in EIA[n]:
            s.append(sig(num, digits))
        for i in Columnize(s):
            out(" ", i)

def Pairs(args, d):
    if len(args) != 4:
        Usage(d)
    parallel = True if args[3] == "p" else False
    target_value = float(args[2])
    if target_value <= 0:
        Error("Target value must be > 0")
    # Read file data
    lines = [i.strip() for i in open(args[1]).readlines()]
    # Check that we have only one blank line and an equal number of
    # resistance values on either side of it.
    r1, r2, first = [], [], True
    for line in lines:
        if not line:
            first = False
            continue
        if first:
            r1.append(float(line))
        else:
            r2.append(float(line))
    if not r1 or not r2:
        Error("Missing blank line in resistor file '%s'" % args[1])
    if len(r1) != len(r2):
        Error("Two resistor sets don't have equal number in resistor file '%s'" 
            % args[1])
    # Calculate the set of resultant resistances
    results = []
    for i in r1:
        for j in r2:
            if parallel:
                r = 1/(1/i + 1/j)
            else:
                r = i + j
            pct_dev = 100*(r - target_value)/target_value
            pct_dev = 0 if abs(pct_dev) < 1e-10 else pct_dev
            results.append([pct_dev, r, i, j])
    results.sort()
    model, file = "parallel" if parallel else "series", args[1]
    out('''
Model = {model}
File  = {file}

% dev from
mean value      Resistance          R1               R2
----------      ----------      -------------   -------------
'''[1:-1].format(**locals()))
    sig.digits = d["-d"]
    for i in results:
        r, r1, r2 = i[1:]
        out("%9s%%      " % sig(i[0], 2), nl=False)
        out("%-10s      " % sig(r), nl=False)
        out("%-10s      " % sig(r1), nl=False)
        out("%-10s" % sig(r2))

def GetValue(args):
    '''Convert a number and optional SI prefix on the command line to a
    floating point equivalent.  Note the string with the optional trailing
    suffix removed can be an expression.
    '''
    s, factor = ''.join(args).replace(" ", ""), 1
    if s[-1] in prefixes:
        factor = 10**prefixes[s[-1]]
        s = s[:-1]
    try:
        return float(eval(s))*factor
    except Exception:
        out("'%s' isn't recognized as a resistance value" % ' '.join(args))
        exit(1)

def Series(d, res):
    '''Find a set of resistors that sum to the desired value but remain
    less than or equal to it.
    '''
    resistors = d["R"]
    resistors.sort()
    resistors = list(reversed(resistors))
    used = []
    while resistors and sum(used) <= res:
        if resistors[0] + sum(used) <= res:
            used.append(resistors[0])
        else:
            del resistors[0]
    out("Sum =", fp.engsi(sum(used)))
    out("  Resistor     % of total")
    r = 0
    for i in used:
        r += i
        out("  %-10s" % fp.engsi(i), " ", sig(100*r/res, 6))

def Interpret(s):
    '''Given a string such as '10k', convert it to a floating point value
    in ohms.  Note that the string with the suffix removed can be a valid
    python expression.
    '''
    factor = 1
    s = s.strip()
    if s[-1] in prefixes:
        factor = 10**prefixes[s[-1]]
        s = s[:-1]
    return float(eval(s))*factor

def DividerRatios(d, res):
    r = [Interpret(i) for i in res]
    R = sum(r)
    out("String of voltage dividers:")
    out("  Resistors given:")
    for i in res:
        out("    ", i)
    out("  Total resistance =", fp.engsi(R))
    out("  Divider ratios:")
    for i in range(1, len(r)):
        D = sum(r[i:])/R
        out("  %2d  " % i, sig(D, 4))

def DDivider(args, d):
    '''The arguments are:
        total_resistance_ohms ratio1 ratio2 ...
                              -----------------
                                    n ratios
    Return the n+1 resistors that make up this divider.
 
    The equations are

        R_n = R*rho_{n-1}
        R_i = R*(rho_{i-1} - rho_i), i = 2, 3, ..., n-1
        R_1 = R*(1 - rho_1)

    Note that it's easier to augment the array of ratios with 0 at the
    beginning and 1 at the end; then we can use the indexed formula

        R_i = R*(rho_{i-1} - rho_i), i = 1, 2, 3, ..., n

    to get the n resistances.
    '''
    R = Interpret(args[1])
    if R <= 0:
        Error("Total resistance must be > 0")
    try:
        rho = [float(i) for i in args[2:]]
    except Exception:
        Error("Couldn't get ratios:\n  '%s'" % str(args[1:]))
    if len(rho) < 2:
        Error("Need at least two ratios")
    if min(rho) <= 0:
        Error("Ratios must all be > 0")
    if max(rho) >= 1:
        Error("Ratios must all be < 1")
    rho.sort()
    rho = list(reversed(rho))
    rho = [1] + rho + [0]   # Augment for indexing ease
    n = len(rho)
    out("Resistors                   Ratio")
    out("--------------------        ----------")
    for i in range(1, n):
        Rx = R*(rho[i-1] - rho[i])
        if i == n - 1:
            out("  R%d = %-20s" % (i, fp.engsi(Rx)))
        else:
            out("  R%d = %-20s %s" % (i, fp.engsi(Rx), rho[i]))
    out("Total resistance =", fp.engsi(R))

def main():
    d = {} # Options dictionary
    args = ParseCommandLine(d)
    sig.digits = d["-d"]
    GetResistors(d)
    if args[0] == "dd":
        DDivider(args, d)
    elif args[0] == "d":
        ratio = args[1]
        if float(ratio) <= 0:
            Error("Divider ratio must be > 0")
        Divider(d, ratio)
    elif args[0] == "D":
        res = args[1:]
        if len(res) < 2:
            Error("Need at least two resistances")
        DividerRatios(d, res)
    elif args[0] == "l":
        List(d)
    elif args[0] == "p":
        Pairs(args, d)
    elif args[0] == "q":
        ratio = args[1]
        if float(ratio) <= 0:
            Error("Quotient ratio must be > 0")
        Quotient(d, ratio)
    elif args[0] == "R":
        d["desired"] = ' '.join(args[1:])
        res = d["res"] = GetValue(args[1:])
        if res <= 0:
            Error("Desired resistance must be > 0")
        Series(d, res)
    elif args[0] == "r":
        d["desired"] = ' '.join(args[1:])
        res = d["res"] = GetValue(args[1:])
        if res <= 0:
            Error("Desired resistance must be > 0")
        Resistance(d, res)

if __name__ == "__main__":
    main()
# vim: wm=5
