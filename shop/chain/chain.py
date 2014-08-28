'''
Calculate the layout information needed to chain-drill a hole or disk
from some sheet material by chain-drilling.

-----------------------------------------------------------------
Copyright (C) 2013 Don Peterson
Contact:  gmail.com@someonesdad1

The Wide Open License (WOL)

Permission to use, copy, modify, distribute and sell this
software and its documentation for any purpose is hereby granted
without fee, provided that the above copyright notice and this
license appear in all source copies.  THIS SOFTWARE IS PROVIDED
"AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF ANY KIND. See
http://www.dspguru.com/wide-open-license for more information.
'''

import sys, os, pickle
from math import *
from getnumber import GetNumber as getnum
from sig import sig
from pdb import set_trace as xx


def out(*v, **kw):
    sep = kw.setdefault("sep", " ")
    nl  = kw.setdefault("nl", True)
    stream = kw.setdefault("stream", sys.stdout)
    if v:
        stream.write(sep.join([str(i) for i in v]))
    if nl:
        stream.write("\n")

def GetDefaults():
    '''Get persistent information from datafile.  

    Command line arguments of use:

        -d      Ignore persisted data and use defaults without
                prompting (useful for testing).
        -D      Dump persisted information and exit.
        -l      Use the last-entered information in the persistance
                file and do not prompt.
    
    If -d is used on the
    command line, then we ignore the persisted data.
    '''
    path, file = os.path.split(os.path.abspath(sys.argv[0]))
    file = os.path.splitext(file)[0] + ".dat"
    datafile = os.path.join(path, file).replace("\\", "/")
    sig.digits = 4
    d = {}  # Dictionary of configuration information
    d["prompt_for_data"] = False
    d["persist"]  = False
    # Read persisted data
    if os.path.exists(datafile):
        try:
            d = pickle.Unpickler(open(datafile)).load()
            got_persisted_data_OK = True
            if "-D" in sys.argv[1:]:
                out("Debug dump of persisted data:")
                for i in d:
                    out("  %-20s %s" % (i, d[i]))
                exit(0)
        except Exception:
            out("Couldn't read '%s' data file" % datafile, 
                stream=sys.stderr)
            got_persisted_data_OK = False
        d["persist"] = True
    if "-l" in sys.argv[1:]:
        d["prompt_for_data"] = not got_persisted_data_OK
        if not got_persisted_data_OK:
            out("You will be prompted for your input.\n", stream=sys.stderr)
    elif "-d" in sys.argv[1:]:
        # Use default information defined here without prompting
        d = {
            "datafile"          : datafile,
            "desired"           : "hole",
            "chain_drill"       : 1/2,
            "hole_diameter"     : 6,
            "disk_diameter"     : 6,
            "dist_betw_holes"   : 0.1,
            "allowance"         : 0.05,
            "prompt_for_data"   : False,
            "persist"           : True,
        }
    else:
        d["prompt_for_data"] = True
    return d

def Chain(d):
    corr = 2*d["allowance"] + d["chain_drill"]
    desired = d["desired"]  # Will be 'hole' or 'disk'
    key = "%s_diameter" % desired
    D = d[key] - corr if d["desired"] == "hole" else d[key] + corr
    dbh = d["dist_betw_holes"]
    n = int((pi*D - dbh)/(d["chain_drill"] + dbh))
    dia = sig(d[key])
    circ = sig(D)
    angle = 2*pi/n
    theta_deg = fmod(angle*180/pi, 360)
    theta = sig(angle*180/pi)
    chord = D*sin(angle/2)
    chain = sig(d["chain_drill"])
    matl_betw = sig(chord - d["chain_drill"])
    allow = sig(d["allowance"])
    chord = sig(chord)
    betw_hole = sig(d["dist_betw_holes"])
    # Check for reasonableness
    if n < 1:
        out("No acceptable solution.  Try again.")
        exit(1)
    # Print report
    out('''
Chain-drilled {desired} input data:
    Desired {desired} diameter             = {dia}
    Drill diameter                    = {chain}
    Allowance                         = {allow}
    Desired material between holes    = {betw_hole}
  Results:
    Number of holes to drill          = {n}
    Angle between holes               = {theta} deg
    Minimum material between holes    = {matl_betw}
  Information to lay out chain holes:
    Circle diameter for chain holes   = {circ}
    Divider setting for hole layout   = {chord}
'''[1:-1].format(**locals()))

def PersistInformation(d):
    if d["persist"]:
        del d["prompt_for_data"]
        del d["persist"]
        pickle.dump(d, open(d["datafile"], "w"))

def GetUserData(d):
    desired = d["desired"]  # Will be 'hole' or 'disk'
    key = "%s_diameter" % desired
    pm = "What is the %s diameter you want?" % desired
    d[key] = getnum(pm, default=d[key], low=0, low_open=True,
                    allow_quit=True, vars=globals())
    pm = "What drill diameter will be used?"
    d["chain_drill"] = getnum(pm, default=d["chain_drill"], low=0, 
                          low_open=True, allow_quit=True,
                          vars=globals())
    pm = "What is the distance between the hole edges?"
    d["dist_betw_holes"] = getnum(pm, default=d["dist_betw_holes"], low=0, 
                          low_open=True, allow_quit=True,
                          vars=globals())
    pm = "What is the allowance between the final diameter and chain holes?"
    d["allowance"] = getnum(pm, default=d["allowance"], low=0, 
                          low_open=True, allow_quit=True,
                          vars=globals())
    if "-l" not in sys.argv[1:]:
        d["persist"] = True

def GetInfo(d):
    out('''
This script calculates the parameters for chain drilling a hole or a
disk from sheet material.  Type q to exit at any time.  Use -l on the
command line to use the last-entered information (this repeats the 
output of the last run); use -d to use the program's default values.
'''[1:])
    opt = {"d":"disk", "h":"hole"}
    while True:
        out('''
Do you want to chain-drill a hole (h) or a disk (d)? '''[1:], nl=False)
        s = raw_input("[%s] " % d["desired"][0])
        s = s.lower().strip()
        if s in opt:
            d["desired"] = opt[s]
            break
        elif s == "q":
            exit(0)
        elif not s:
            # Use default value
            break
        else:
            out("Unrecognized response\n")
    GetUserData(d)
    out()

if __name__ == "__main__":
    d = GetDefaults()
    if d["prompt_for_data"]:
        GetInfo(d)
    Chain(d)
    PersistInformation(d)
