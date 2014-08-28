'''
Prints combinations of gauge blocks that will sum to a desired size.
'''
# Copyright (C) 2012 Don Peterson
# Contact:  gmail.com@someonesdad1
  
#
#

from __future__ import print_function, division
import sys, getopt
from itertools import combinations
from pdb import set_trace as xx

default_set_name = "user"
default_maxnum = 5  # Max number of blocks in combination

# The following dictionary holds the gauge block sets.  You can add or
# delete sets as you see fit.  The structure should be apparent if you
# want to add a new set.  Note the values are integers; this helps
# make the summing of sizes both speedy and exact.
gauge_block_sets = {
    # units, resolution, block_sizes_sequence
    "user" : ("in", "0.0001", ( 
        # This gauge block set is a used set I bought in 2005 and had some
        # missing blocks.
         250,  350,  490,  500, 1000, 1003, 1004, 1005, 1006, 1007,
        1008, 1009, 1040, 1050, 1060, 1070, 1080, 1090, 1110, 1120,
        1140, 1160, 1170, 1180, 1190, 1210, 1220, 1230, 1250, 1260,
        1270, 1290, 1300, 1310, 1320, 1330, 1340, 1350, 1370, 1380,
        1390, 1400, 1420, 1430, 1440, 1450, 1460, 1470, 1500, 2500,
        3500, 4500, 5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000,
        9500, 20000, 30000, 40000,)
    ),
    "metric" : ("mm", "0.001", (
        1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010,
        1020, 1030, 1040, 1050, 1060, 1070, 1080, 1090, 1100, 1110,
        1120, 1130, 1140, 1150, 1160, 1170, 1180, 1190, 1200, 1210,
        1220, 1230, 1240, 1250, 1260, 1270, 1280, 1290, 1300, 1310,
        1320, 1330, 1340, 1350, 1360, 1370, 1380, 1390, 1400, 1410,
        1420, 1430, 1440, 1450, 1460, 1470, 1480, 1490, 1000, 1500,
        2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500,
        7000, 7500, 8000, 8500, 9000, 9500, 10000, 20000, 30000,
        40000, 50000, 60000, 70000, 80000, 90000, 100000,)
    ),
    "inch36" : ("in", "0.0001", (
         500, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009,
        1010, 1020, 1030, 1040, 1050, 1060, 1070, 1080, 1090, 1100,
        1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 1000, 2000,
        3000, 4000, 5000, 10000, 20000, 40000,)
    ),
    "inch81" : ("in", "0.0001", (
         500, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009,
        1010, 1020, 1030, 1040, 1050, 1060, 1070, 1080, 1090, 1100,
        1110, 1120, 1130, 1140, 1150, 1160, 1170, 1180, 1190, 1200,
        1210, 1220, 1230, 1240, 1250, 1260, 1270, 1280, 1290, 1300,
        1310, 1320, 1330, 1340, 1350, 1360, 1370, 1380, 1390, 1400,
        1410, 1420, 1430, 1440, 1450, 1460, 1470, 1480, 1490, 1000,
        1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000,
        6500, 7000, 7500, 8000, 8500, 9000, 9500, 10000, 20000, 30000,
        40000,)
    ),
    "space" : ("in", "0.0005", (
        # This is a "Space Blocks" set I bought in the 1970's.  I
        # remember paying around $70 for it and the same sets are
        # available today for around the same price.  They're
        # cylinders of steel finished to the stamped length and they
        # can be clamped together with set screws because there is a
        # tapped longintudinal hole through each piece.
        500, 625, 600, 700, 800, 900, 1000, 1010, 1020, 1030, 1040,
        1050, 1060, 1070, 1080, 1090, 1100, 1200, 1250, 1300, 1400,
        1500, 1600, 1700, 1800, 1900, 2000, 3000, 4000, 5000, 6000,
        7000, 8000, 9000, 10000, 10000,)
    ),
}

# Dictionary used to get the format string needed to print out the
# sizes.
formats = {
    "0.001"  : "%.3f",
    "0.0001" : "%.4f",
    "0.0005" : "%.4f",
}

# Check to make sure we don't have a new resolution to handle
for name in gauge_block_sets:
    unit, resolution, blocks = gauge_block_sets[name]
    assert resolution in formats

def Usage(status=1):
    name = sys.argv[0]
    dsn = default_set_name
    maxnum = default_maxnum
    s = '''
Usage:  {name} [options] size1 [size2...]
  Prints out the gauge blocks to use to make up the indicated sizes.
  Note the sizes will be rounded to the nearest unit of resolution of
  the gauge block set.  The '{dsn}' gauge block set is used by default.

  There are quite a few different gauge block sets in the world.  If
  you need to use a different set than what's provided in the script,
  it's easy to add a new set to the gauge_block_sets dictionary at the
  beginning of the script.

Options:
    -a
        Show all combinations that make up the desired size, not just
        the first combination found.
    -k num
        Set the maximum subset size of blocks to use in the search.
        The default is {maxnum}.  Making this number too large can
        result in long run times.
    -n set_name
        Choose which gauge block set to use.

'''[1:].format(**locals())
    s += "Allowed gauge block set names and characteristics:\n"
    names = list(gauge_block_sets.keys())
    names.sort()
    for name in names:
        unit, resolution, blocks = gauge_block_sets[name]
        s += ("    %-10s %6s %s (%d blocks)\n" % 
            (name, resolution, unit, len(blocks)))
    print(s)
    exit(status)

def ParseCommandLine(d):
    d["-a"] = False     # Show all combinations, not just the first
    d["-k"] = default_maxnum  # Maximum subset size in search
    d["-n"] = "user"    # Name of default gauge block set
    d["num_blocks"] = (1, 5) # Min and max block combinations to search for
    if len(sys.argv) < 2:
        Usage()
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "ak:n:")
    except getopt.error as str:
        print(str)
        sys.exit(1)
    for opt in optlist:
        if opt[0] == "-a":
            d["-a"] = True
        if opt[0] == "-k":
            d["-k"] = int(opt[1])
            if d["-k"] < 1:
                raise ValueError("Bad subset size")
        if opt[0] == "-n":
            d["-n"] = opt[1]
            if d["-n"] not in gauge_block_sets:
                sys.stderr.write("Unrecognized gauge block set\n")
                exit(1)
    if len(args) < 1:
        Usage()
    return args

def GetIntegerSize(size, d):
    '''Convert the size number (a string in inches or mm) to an integer
    size to search for.  
    '''
    # string, string, list of integer sizes
    unit, resolution, blocks = gauge_block_sets[d["-n"]]
    x, T = abs(float(size)), abs(float(resolution))
    # Using resolution as a template, round the size to an integer
    # number of template units.
    return int(x/T + 0.5)

def PrintResults(integer_size, size, combination, d):
    '''integer_size is the actual size searched for; size is the
    original string the user passed on the command line.
    '''
    # string, string, list of integer sizes
    unit, resolution, blocks = gauge_block_sets[d["-n"]]
    fmt = formats[resolution]
    print(fmt % float(size), ": ", sep="", end="")
    for i in combination:
        print(fmt % (float(i)*float(resolution)), " ", end="")
    print()

def GetBlocks(size, d):
    isz = GetIntegerSize(size, d)
    max_blocks = d["-k"]
    # string, string, list of integer sizes
    set_of_blocks = gauge_block_sets[d["-n"]][2]
    if isz > sum(set_of_blocks):
        print("No solution for size %s" % size)
        return
    for num_blocks in range(1, max_blocks + 1):
        for i in combinations(set_of_blocks, num_blocks):
            if sum(i) == isz:
                PrintResults(isz, size, i, d)
                if not d["-a"]:
                    return

def main():
    d = {}
    for size in ParseCommandLine(d):
        GetBlocks(size, d)

main()
