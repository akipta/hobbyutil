'''
Process Quality Simulator

Script to model process quality using the Monte Carlo method.  See the
accompanying documentation ProcessAnalyzer.pdf for details on how to
use.

-------------------------------------------------------------------
Copyright (C) 2006, 2012 Don Peterson
Contact:  gmail.com@someonesdad1
  
                         The Wide Open License (WOL)
  
Permission to use, copy, modify, distribute and sell this software and
its documentation for any purpose is hereby granted without fee,
provided that the above copyright notice and this license appear in
all copies.  THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT EXPRESS OR
IMPLIED WARRANTY OF ANY KIND. See
http://www.dspguru.com/wide-open-license for more information.
'''

import sys, os, getopt, time, numpy as np, hashlib
from sig import sig 
from manufacture import Manufacture, Hash
from numpy.random import normal, seed

def out(*v, **kw):
    sep = kw.setdefault("sep", " ")
    nl  = kw.setdefault("nl", True)
    stream = kw.setdefault("stream", sys.stdout)
    if v:
        stream.write(sep.join([str(i) for i in v]))
    if nl:
        stream.write("\n")

def Usage(d, status=1):
    name = sys.argv[0]
    s = '''
Usage:  {name} [options] data_file
  Runs a simulation of a manufacturing process whose characteristics
  are defined in the file data_file.

Options:
    -c 
        Print a template of what the data_file should contain.
    -s string
        Provide a seed for the random number generator by hashing the
        string seed.
'''[1:-1]
    out(s.format(**locals()))
    sys.exit(status)

def ParseCommandLine(d):
    d["seed"] = None
    if len(sys.argv) < 2:
        Usage(d)
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "cs:")
    except getopt.GetoptError as str:
        msg, option = str
        out(msg)
        sys.exit(1)
    for opt in optlist:
        if opt[0] == "-c":
            PrintTemplate()
        if opt[0] == "-s":
            h = hashlib.md5()
            h.update(opt[1])
            d["seed"] = opt[1]
            num = abs(int(hash(h.hexdigest())))
            seed(num)
    if len(args) != 1:
        Usage(d)
    d["data_file"] = args[0]

def PrintTemplate():
    '''Print to stdout a template of the items needed for a settings
    dictionary.
    '''
    out('''
# This is a template of the initialization file needed for the use of
# the pqs.py process simulation script.  The lines in this file are
# valid python statements and will be run by the simulation script to
# define the simulation's variables.  This file can only have blank
# lines, comments, and assignment statements.

# Process variables

    # The script is set up to use numpy's normal distribution for both
    # the process distribution and the measurement uncertainty
    # distribution.  If you want to use other distributions, you'll
    # need to use or create a function that takes a mean, standard
    # deviation, and number of parts to make and returns a numpy array
    # of the generated random numbers.
    ProcessDistribution = normal
    ProcessDistributionName = "normal"

    # Process mean
    ProcessMu = 0

    # Process standard deviation
    ProcessSigma = 1

    # The measurement uncertainty associated with each measurement is
    # also a random variable.
    MeasurementDistribution = normal
    MeasurementDistributionName = "normal"

    # Measurement uncertainty distribution mean; note this is really a
    # measurement bias (and is so indicated in the report)
    MeasurementMu = 0

    # Measurement uncertainty distribution standard deviation
    MeasurementSigma = 1e-10

    # For speed, make 1 lot and put all the production parts needed
    # into that lot.  The only reason to do otherwise is if you want
    # to change the manufacturing.py script to do sampling inspection.
    NumberOfLots = 1
    PartsPerLot = 100000

    # These two numbers determine the interval within which a good
    # part lies.  Note:  these default values should produce a 
    # report that has no misclassified parts (i.e., no producer's or
    # consumer risk) and a 10% yield loss (-1.64485 is the z-score for
    # 0.05).
    Specification = (-1.64485, 1.64485)

# Financial information.  Note that the simulation and the report
# printed to stdout don't make any assumptions about the monetary
# units.

    # The following cost is the direct manufacturing cost of a single
    # part.  It includes e.g. the raw material, manufacturing cost,
    # and direct labor.
    CostToProducePart = 1

    # The following costs are incurred during the stated action.
    CostToTestPart = 0
    CostToShipPart = 0
    CostToScrapPart = 0

    # The following is a variable overhead cost associated with each
    # part.  The total overhead cost in this category is calculated by
    # multiplying by the number of parts produced.
    CostVariableOverhead = 0

    # The fixed overhead is an amount of money that is needed to make
    # the production run, regardless of the number of parts made.
    # Things that are lumped in this category can be things like
    # floorspace, depreciation, engineering/management salaries,
    # corporate charges, etc.
    CostFixedOverhead = 0

    # The selling price is what the part is sold to the customer for.
    SellingPricePerPart = 2

    # When a bad part is shipped (i.e., a part with its quality
    # parameter outside the specification limits), the part is assumed
    # to fail in the customer's environment and cause the customer to
    # incur the following cost.
    CustomerCostPerBadPart = 0

# General items
    # The Title is a string that will be displayed centered at the
    # beginning of the report.
    Title = ""

    # You can control the number of significant figures that the
    # process characteristics, yields, etc. are printed with.
    SignificantDigits = 3
'''[1:])
    exit(0)

def FmtI(x):
    '''x is an integer; return a string with x formatted with commas
    separating the thousands (uses locale, so it will work with
    '.' in other locales).
    '''
    # To use on python 3, remove 'long'
    if not isinstance(x, (int, long)):
        raise ValueError("x must be an integer")
    import locale
    locale.setlocale(locale.LC_ALL, '') # Set to the default locale
    return format(x, "n")

def ReadDataFile(data_file):
    '''Read in the lines from the data file and execute them in the
    local namespace.  This will define the local variables needed to
    run the simulation.
    '''
    if 0:
        # Default values of the variables
        #
        # Process
        ProcessDistribution = normal
        ProcessDistributionName = "normal (numpy)"
        ProcessMu = 0
        ProcessSigma = 0
        # Measurement
        MeasurementDistribution = normal
        MeasurementDistributionName = "normal (numpy)"
        MeasurementMu = 0
        MeasurementSigma = 0
        Specification = (0, 0)
        # Production
        NumberOfLots = 0
        PartsPerLot = 0
        # Financial
        CostToProducePart = 0
        CostToTestPart = 0
        CostToShipPart = 0
        CostToScrapPart = 0
        CostVariableOverhead = 0
        CostFixedOverhead = 0
        SellingPricePerPart = 0
        CustomerCostPerBadPart = 0
    SignificantDigits = 3
    Title = ""
    Files = [os.path.abspath(sys.argv[0]).replace("\\", "/")]
    for line in open(data_file).readlines():
        line = line.strip()
        if not line or line[0] == "#" or "=" not in line:
            continue
        exec line
    del line
    return locals()

def PrintReport(d):
    S, R, w = d["settings"], d["results"]["parts"], 79
    if S["Title"].strip():
        for line in S["Title"].split("\n"):
            out("{0:^{1}s}".format(line, w))
    tm = time.asctime(time.localtime(time.time()))
    out("{0:^{1}s}".format(tm, w))
    if d["seed"] is not None:
        s = "Seed = " + d["seed"]
        out("{0:^{1}s}".format(s, w))
    out()
    s = "Source files and their hashes"
    out(s)
    out("-"*len(s))
    d["settings"]["Files"].sort()
    for file in d["settings"]["Files"]:
        out(" ", Hash(open(file).read())[0], file)
    out()
    # Process details
    sig.digits = sd = S["SignificantDigits"]
    proc_mean, proc_s = sig(S["ProcessMu"]), sig(S["ProcessSigma"])
    meas_mean, meas_s = sig(S["MeasurementMu"]), sig(S["MeasurementSigma"])
    pdist, mdist = S["ProcessDistributionName"], S["MeasurementDistributionName"]
    N = S["NumberOfLots"]*S["PartsPerLot"]
    nparts = FmtI(N)
    nl, ppl = FmtI(S["NumberOfLots"]), FmtI(S["PartsPerLot"])
    spec = sig(list(S["Specification"]))
    na, nw, nd, sp = ">", 15, 30, " "*10
    out('''
Process characteristics                    ({sd} significant figures)
-----------------------
  Distributions
    Process     = {pdist}
    Measurement = {mdist}
  Process mean                    {sp}{proc_mean:{na}{nw}}
  Process standard deviation      {sp}{proc_s:{na}{nw}} 
  Measurement bias                {sp}{meas_mean:{na}{nw}} 
  Measurement standard deviation  {sp}{meas_s:{na}{nw}}
  Part acceptance interval        {sp}{spec:{na}{nw}}
  Number of lots made             {sp}{nl:{na}{nw}}
  Parts per lot                   {sp}{ppl:{na}{nw}}
'''[1:].format(**locals()))
    # What was actually produced
    good, bad = len(R[0]), len(R[1])
    goodi, badi = FmtI(good), FmtI(bad)
    goodp, badp = sig(100*good/float(N)), sig(100*bad/float(N))
    out('''
True (unknowable) process output
--------------------------------
  Total parts made  {nparts:{na}{nw}}
  Actual good       {goodi:{na}{nw}}    ({goodp}% of total)
  Actual bad        {badi:{na}{nw}}    ({badp}% of total)
'''[1:].format(**locals()))
    # What the measurements said was produced
    gtg, gtb = len(R[2]), len(R[3])
    btg, btb = len(R[4]), len(R[5])
    gtgi, gtbi = FmtI(gtg), FmtI(gtb)
    btgi, btbi = FmtI(btg), FmtI(btb)
    gtgp = sig(100*gtg/float(N))
    gtbp = sig(100*gtb/float(N))
    btgp = sig(100*btg/float(N))
    btbp = sig(100*btb/float(N))
    all = np.concatenate((R[2], R[3], R[4], R[5]))
    mean = sig(np.average(all))
    sdev = sig(np.sqrt(np.cov(all)))
    low, high = sig(np.min(all)), sig(np.max(all))
    out('''
What 100% inspection determined
-------------------------------
  Good tested good  {gtgi:{na}{nw}}  {gtgp:{na}}%
  Good tested bad   {gtbi:{na}{nw}}  {gtbp:{na}}%  <-- Producer's risk
  Bad  tested good  {btgi:{na}{nw}}  {btgp:{na}}%  <-- Consumer's risk
  Bad  tested bad   {btbi:{na}{nw}}  {btbp:{na}}%
  Process mean      {mean:{na}{nw}}
  Process std dev   {sdev:{na}{nw}}
  Min, max measured    [{low}, {high}]
'''[1:].format(**locals()))

    # Production results
    ship  = FmtI(gtg + btg)
    scrap = FmtI(gtb + btb)
    try:
        ship_badp = sig(100*gtb/float(gtg + gtb))
    except ZeroDivisionError:
        ship_badp = sig(0)
    try:
        scrap_goodp = sig(100*btg/float(btg + btb))
    except ZeroDivisionError:
        scrap_goodp = sig(0)
    yieldr = "actual = " + sig(100*good/float(N)) + "%,"
    yieldm = "measured = " + sig(100*(gtg + btg)/float(N)) + "%"
    scrapr = "actual = " + sig(100*bad/float(N)) + "%,"
    scrapm = "measured = " + sig(100*(gtb + btb)/float(N)) + "%"
    ya, ysw = ">", 15
    out('''
Production results
------------------
  Parts shipped     {ship:{na}{nw}}  {ship_badp}% of these are bad parts
  Parts scrapped    {scrap:{na}{nw}}  {scrap_goodp}% of these are good parts
  Yield              {yieldr:{ya}{ysw}} {yieldm}
  Scrapped           {scrapr:{ya}{ysw}} {scrapm}
'''[1:].format(**locals()))
    # Financial results
    # Per part:
    nship, nscrap, n = gtg + btg, gtb + btb, float(N)
    cprodpp    = S["CostToProducePart"]
    ctestpp    = S["CostToTestPart"]
    cshippp    = S["CostToShipPart"]
    cscrappp   = S["CostToScrapPart"]
    cvohpp     = S["CostVariableOverhead"]
    cfohpp     = S["CostFixedOverhead"]/float(N)
    ccustbadpp = S["CustomerCostPerBadPart"]
    # Formatted as integers
    cprod       = FmtI(int(cprodpp*n))
    ctest       = FmtI(int(ctestpp*n))
    cship       = FmtI(int(ctestpp*float(nship)))
    cscrap      = FmtI(int(cscrappp*float(nscrap)))
    cvoh        = FmtI(int(cvohpp*n))
    cfoh        = FmtI(int(float(S["CostFixedOverhead"])))
    ctprod      = (n*(cprodpp + ctestpp + cvohpp + cfohpp)
                  + ctestpp*float(nship) + cscrappp*float(nscrap))
    ctprodi     = FmtI(int(ctprod))
    ctprodpp    = (ctprod/n)
    ppstart     = ctprod/n
    try:
        ppship  = ctprod/float(nship)
    except ZeroDivisionError:
        ppship  = 0
    # Percentages of total production cost
    ppc = 100*cprodpp*n/ctprod
    ptc = 100*ctestpp*n/ctprod
    psc = 100*ctestpp*float(nship)/ctprod
    pcs = 100*cscrappp*float(nscrap)/ctprod
    pvo = 100*cvohpp*n/ctprod
    pfo = 100*float(S["CostFixedOverhead"])/ctprod
    tpc = 100
    # Revenue & customer
    sppp = S["SellingPricePerPart"]
    trev = sppp*float(gtg + btg)
    trevi = FmtI(int(trev))
    gp = FmtI(int(trev - ctprod))
    try:
        gpp = 100*(trev - ctprod)/trev
    except Exception:
        gpp = "--"
    custloss = ccustbadpp*float(btg)
    custlossi = FmtI(int(custloss))
    try:
        custlosspp = custloss/float(nship)
    except ZeroDivisionError:
        custlosspp = 0
    mo = ">15s"
    kd, pp, pt = ">10.1f", ">8.3f", ">5.1f"
    pps  = "per part started"
    ppsh = "per part shipped"
    prp  = "per received part"
    out('''
Money                              Amount   %   Cost per part
-----                           --------- ----- -------------
  Production cost         {cprod:{mo}} {ppc:{pt}} {cprodpp:{pp}}   
  Testing cost            {ctest:{mo}} {ptc:{pt}} {ctestpp:{pp}}   
  Shipment cost           {cship:{mo}} {psc:{pt}} {cshippp:{pp}}   
  Cost to scrap           {cscrap:{mo}} {pcs:{pt}} {cscrappp:{pp}}   
  Variable overhead cost  {cvoh:{mo}} {pvo:{pt}} {cvohpp:{pp}}   
  Fixed overhead cost     {cfoh:{mo}} {pfo:{pt}} {cfohpp:{pp}}   
                                --------- ----- --------
  Total production cost   {ctprodi:{mo}} {tpc:{pt}} {ppstart:{pp}} {pps}
                                                {ppship:{pp}} {ppsh}
  Revenue                 {trevi:{mo}}       {sppp:{pp}} selling price
  Gross profit            {gp:{mo}}       
'''[1:-1].format(**locals()))
    if gpp == "--":
        out('''
  % gross profit                      --%            
  Customer's loss              {custlossi:{mo}}       {custlosspp:{pp}} {prp}
'''[1:-1].format(**locals()))
    else:
        out('''
  % gross profit               {gpp:{kd}}%    
  Customer's loss         {custlossi:{mo}}       {custlosspp:{pp}} {prp}
'''[1:-1].format(**locals()))

def main():
    d = {} # Dictionary to track options, settings, & results
    ParseCommandLine(d)
    d["settings"] = ReadDataFile(d["data_file"])
    d["results"]  = Manufacture(d["settings"])
    PrintReport(d)

main()
