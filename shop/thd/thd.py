'''
TODO:
    * Helix angle
    * UN flat on front of cutting tool
    * Change 'Compound feed, DD/cos(29)' to sqrt(3)*P

Calculate thread properties.

Copyright (C) 2005, 2006 Don Peterson
Contact:  gmail.com@someonesdad1

                         The Wide Open License (WOL)

Permission to use, copy, modify, distribute and sell this software and its
documentation for any purpose is hereby granted without fee, provided that
the above copyright notice and this license appear in all source copies.
THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF
ANY KIND. See http://www.dspguru.com/wide-open-license for more
information.
'''

from __future__ import division
import sys, getopt, string, asme
from math import cos, tan, sin, atan, pi, sqrt
from pdb import set_trace as xx

debug = 0

# Global variables
thread_class = 2
mm_per_in = 25.4    # in to mm
tolerance = 0.05    # Tolerance for match in OD or tpi search

# Format strings
spc = 35
vf = "%%-%ss" % spc
fmt  = vf + "%10.4f   %8.2f"
fmt1 = vf + "%7.1f      %8.2f"
fmt3 = vf + "%9.3f    %8.2f"
fmt6 = vf + "%12.6f %8.2f"

# Data for -T option to print out table 4 in 1972's Machinery's
# Handbook.  The fields are:  
#   Size designator
#   Threads per inch
#   Thread series designation (c = coarse, f = fine, e = extra fine, 
#       s = special).
#   Classes to print (each digit means print that Class)
# Note you can comment a line out if desired.
t = '''
    n0 80 f 23
    n1 64 c 23
    n1 72 f 23
    n2 56 c 23
    n2 64 f 23
    n3 48 c 23
    n3 56 f 23
    n4 40 c 23
    n4 48 f 23
    n5 40 c 23
    n5 44 f 23
    n6 32 c 23
    n6 40 f 23
    n8 32 c 23
    n8 36 f 23
    n10 24 c 23
    n10 28 s 2
    n10 32 f 23
    n10 36 s 2
    n10 40 s 2
    n10 48 s 2
    n10 56 s 2
    n12 24 c 23
    n12 28 f 23
    n12 32 e 23
    n12 36 s 2
    n12 40 s 2
    n12 48 s 2
    n12 56 s 2
    1/4 20 c 123
    1/4 24 s 2
    1/4 27 s 2
    1/4 28 f 123
    1/4 32 e 23
'''[1:]
table4 = []
for i in t.split("\n"):
    f = i.strip().split()
    if f and f[0][0] != "#":
        table4.append((f[0], int(f[1]), f[2], f[3]))
table4 = tuple(table4)

# List the taps, dies, etc. that you have on hand.  This string is printed
# out when you use the -l option.
my_sizes = '''                          Thread Sizes on Hand
                          --------------------

Entries are taps unless followed by a letter.  (LH) means left hand.  The
following letters designate die sizes (H means hex):
    A:1, B:13/16, C:1.5, D:2, E:2.25 F:2.5 G:5/8 J:1.25 K:"Little Giant style"
    
Inch
     0:80   2:56,56B   3:48,48B    4:36,36B,40,40AH,48,48B    5:40,40B 
     6:32,32B,32BH,36,40,48    8:32,32BH,40    10:24,24AB,24BH,32,32A,32BH 
     12:24,24AB,28    20:18    3/16:24,32,32A 
     1/4:20,20(LH),20ABCJK,20AH,20BH,20A(LH),28,28A,32,32A 
     5/16:18,18(LH),18A,18A(LH),18C,18AH,24,24(LH),24AD,27,27B,32,32B 
     3/8:16,16(LH),16A,16A(LH),24,24ADJ 
     7/16:14,14AC,20,20J,26A,28C 
     1/2:13,13A,13(LH),13C(LH),20,20AJ,28C        9/16:12,12F,18,18E 
     5/8:11F,18,18E                               11/16:16,16E 
     3/4:10,10F,16,16E                            7/8:9,9F,14,14E,18 
     1:8,14,14E                                   0.406:36   

Metric:
     3:0.5,0.5GH                             4:0.7,0.75,0.7GH, 0.75GH 
     5:0.8,0.9,0.8GH,0.9GH                   6:1,1GH  
     7:1,1AH                                 8:1,1.25,1AH,1.25AH 
     9:1,1.25,1AH,1.25AH                     10:1,1.25,1.5,1.25AH,1.5AH 
     11:1.5,1.5AH                            12:1.5,1.75,1.5AH,1.75AH 
     14:1.25 

Pipe:
     1/8:27,27A   1/4:18,18A   3/8:18   1/2:14   3/4:14 
     1/8:28,28AH (British Std.) 

Lathe Threads (tpi):
    4  4.5  5  5.5  5.75  6  6.5  6.75  7  8  9  10  11  11.5  12  13
    13  13.5  14  16  18  20  22  23  24  26  27  28  32  36  40   44
    46  48  52  54  56  64  72  80

Thread Chasers:
    Inside:  18, 20, 24             Outside:  18, 20
'''[:-1]

# Wire diameters in mils in Pee Dee thread measuring set
wires = [18, 24, 29, 32, 40, 45, 55, 63, 72, 81, 92, 108, 120, 127, 143, 185]
for ix in xrange(len(wires)):
    wires[ix] /= 1000
wires = tuple(wires)

# Common UNC and UNF sizes for -t option
common_sizes = (
    # Descr  Diam  TPI
    ("2-56 UNC", 0.086, 56),
    ("3-48 UNC", 0.099, 48),
    ("4-40 UNC", 0.112, 40),
    ("4-48 UNF", 0.112, 48),
    ("5-40 UNC", 0.125, 40),
    ("6-32 UNC", 0.138, 32),
    ("8-32 UNC", 0.164, 32),
    ("10-24 UNC", 0.190, 24),
    ("10-32 UNF", 0.190, 32),
    ("1/4-20 UNC", 0.250, 20),
    ("1/4-28 UNF", 0.250, 28),
    ("5/16-18 UNC", 0.3125, 18),
    ("5/16-24 UNF", 0.3125, 24),
    ("3/8-16 UNC", 0.375, 16),
    ("3/8-24 UNF", 0.375, 24),
    ("7/16-14 UNC", 0.4375, 14),
    ("7/16-20 UNF", 0.4375, 20),
    ("1/2-13 UNC", 0.5, 13),
    ("1/2-20 UNF", 0.5, 20),
    ("9/16-12 UNC", 0.5625, 12),
    ("9/16-18 UNF", 0.5625, 18),
    ("5/8-11 UNC", 0.625, 11),
    ("5/8-18 UNF", 0.625, 18),
    ("3/4-10 UNC", 0.75, 10),
    ("3/4-16 UNF", 0.75, 18),
    ("7/8-9 UNC", 0.875, 9),
    ("7/8-14 UNF", 0.875, 14),
    ("1-8 UNC", 1, 8),
    ("1-14 UNF", 1, 14)
)

# Fraction, number, and letter size drills; used to select the nearest
# tap and clearance drills.
drills = {
    0.0059 : "#97",
    0.0063 : "#96",
    0.0067 : "#95",
    0.0071 : "#94",
    0.0075 : "#93",
    0.0079 : "#92",
    0.0083 : "#91",
    0.0087 : "#90",
    0.0091 : "#89",
    0.0095 : "#88",
    0.0100 : "#87",
    0.0105 : "#86",
    0.0110 : "#85",
    0.0115 : "#84",
    0.0120 : "#83",
    0.0125 : "#82",
    0.0130 : "#81",
    0.0135 : "#80",
    0.0145 : "#79",
    0.0156 : "1/64",
    0.0160 : "#78",
    0.0180 : "#77",
    0.0200 : "#76",
    0.0210 : "#75",
    0.0225 : "#74",
    0.0240 : "#73",
    0.0250 : "#72",
    0.0260 : "#71",
    0.0280 : "#70",
    0.0293 : "#69",
    0.0310 : "#68",
    0.0313 : "1/32",
    0.0320 : "#67",
    0.0330 : "#66",
    0.0350 : "#65",
    0.0360 : "#64",
    0.0370 : "#63",
    0.0380 : "#62",
    0.0390 : "#61",
    0.0400 : "#60",
    0.0410 : "#59",
    0.0420 : "#58",
    0.0430 : "#57",
    0.0465 : "#56",
    0.0469 : "3/64",
    0.0520 : "#55",
    0.0550 : "#54",
    0.0595 : "#53",
    0.0625 : "1/16",
    0.0635 : "#52",
    0.0670 : "#51",
    0.0700 : "#50",
    0.0730 : "#49",
    0.0760 : "#48",
    0.0781 : "5/64",
    0.0785 : "#47",
    0.0810 : "#46",
    0.0820 : "#45",
    0.0860 : "#44",
    0.0890 : "#43",
    0.0935 : "#42",
    0.0938 : "3/32",
    0.0960 : "#41",
    0.0980 : "#40",
    0.0995 : "#39",
    0.1015 : "#38",
    0.1040 : "#37",
    0.1065 : "#36",
    0.1094 : "7/64",
    0.1100 : "#35",
    0.1110 : "#34",
    0.1130 : "#33",
    0.1160 : "#32",
    0.1200 : "#31",
    0.1250 : "1/8",
    0.1285 : "#30",
    0.1360 : "#29",
    0.1405 : "#28",
    0.1406 : "9/64",
    0.1440 : "#27",
    0.1470 : "#26",
    0.1495 : "#25",
    0.1520 : "#24",
    0.1540 : "#23",
    0.1563 : "5/32",
    0.1570 : "#22",
    0.1590 : "#21",
    0.1610 : "#20",
    0.1660 : "#19",
    0.1695 : "#18",
    0.1719 : "11/64",
    0.1730 : "#17",
    0.1770 : "#16",
    0.1800 : "#15",
    0.1820 : "#14",
    0.1850 : "#13",
    0.1875 : "3/16",
    0.1890 : "#12",
    0.1910 : "#11",
    0.1935 : "#10",
    0.1960 : "#9",
    0.1990 : "#8",
    0.2010 : "#7",
    0.2031 : "13/64",
    0.2040 : "#6",
    0.2055 : "#5",
    0.2090 : "#4",
    0.2130 : "#3",
    0.2188 : "7/32",
    0.2210 : "#2",
    0.2280 : "#1",
    0.234 : "A",
    0.2344 : "15/64",
    0.238 : "B",
    0.242 : "C",
    0.246 : "D",
    0.250 : "E",
    0.2500 : "1/4",
    0.257 : "F",
    0.261 : "G",
    0.2656 : "17/64",
    0.266 : "H",
    0.272 : "I",
    0.277 : "J",
    0.281 : "K",
    0.2813 : "9/32",
    0.290 : "L",
    0.295 : "M",
    0.2969 : "19/64",
    0.302 : "N",
    0.3125 : "5/16",
    0.316 : "O",
    0.323 : "P",
    0.3281 : "21/64",
    0.332 : "Q",
    0.339 : "R",
    0.3438 : "11/32",
    0.348 : "S",
    0.358 : "T",
    0.3594 : "23/64",
    0.368 : "U",
    0.3750 : "3/8",
    0.377 : "V",
    0.386 : "W",
    0.3906 : "25/64",
    0.397 : "X",
    0.404 : "Y",
    0.4063 : "13/32",
    0.413 : "Z",
    0.4219 : "27/64",
    0.4375 : "7/16",
    0.4531 : "29/64",
    0.4688 : "15/32",
    0.4844 : "31/64",
    0.5000 : "1/2"
}

# Weird thread stuff gotten from findthrd.zip on Marv Klotz's site
# http://www.myvirtualnetwork.com/mklotz/

weird_thread_names = {
    "ADM"     : "Admiralty",
    "ASME"    : "ASME Thread",
    "BA"      : "British association",
    "BRASS"   : "Brass thread",
    "BSF"     : "British Standard Fine",
    "BSP"     : "British Standard Pipe Thread",
    "CEI"     : "Cycle Engineers Institute ",
    "CEI20"   : "Cycle Engineers Institute 20",
    "CEI40"   : "Cycle Engineers Institute 40",
    "GAS"     : "Gas (Brass Pipe) Thread",
    "HOLTZ"   : "Holtzapfels Threads",
    "LOEW"    : "Loewenhertz Threads ",
    "M"       : "ISO Metric",
    "PEND"    : "Watch Pendant Thread",
    "PROG"    : "Progress Thread",
    "SPARK"   : "Spark Plug Threads",
    "THURY"   : "Swiss Screw Thread",
    "UNC"     : "Unified National Coarse",
    "UNF"     : "Unified National Fine",
    "UNEF"    : "Unified National Extra Fine",
    "WALTH"   : "Waltham Thread",
    "WHIT"    : "Whitworth",
    "W.INS"   : "Whitworth Instrument",
    "WPIPE"   : "Whitworth Pipe Thread",
    "Coarse"  : "ISO Metric ",
    "Fine"    : "ISO Metric "
}

weird_threads = (
    # Name, diameter in inches, threads per inch
    ("10 W.INS",       0.0100,   400.0),
    ("25 THURY",       0.0100,   353.8),
    ("11 W.INS",       0.0110,   400.0),
    ("24 THURY",       0.0114,   318.3),
    ("12 W.INS",       0.0120,   350.0),
    ("23 THURY",       0.0129,   286.7),
    ("23 BA",          0.0130,   282.2),
    ("13 W.INS",       0.0130,   350.0),
    ("23 WALTH",       0.0138,   254.0),
    ("14 W.INS",       0.0140,   300.0),
    ("22 BA",          0.0146,   259.2),
    ("22 THURY",       0.0146,   257.9),
    ("15 W.INS",       0.0150,   300.0),
    ("4 PROG",         0.0157,   254.0),
    ("16 W.INS",       0.0160,   300.0),
    ("21 BA",          0.0165,   230.9),
    ("21 THURY",       0.0168,   233.0),
    ("17 W.INS",       0.0170,   250.0),
    ("21 WALTH",       0.0177,   240.0),
    ("4 1/2 PROG",     0.0177,   254.0),
    ("18 W.INS",       0.0180,   250.0),
    ("20 THURY",       0.0189,   208.2),
    ("20 BA",          0.0189,   211.7),
    ("19 W.INS",       0.0190,   250.0),
    ("5 PROG",         0.0197,   203.2),
    ("20 W.INS",       0.0200,   210.0),
    ("19 BA",          0.0213,   181.4),
    ("19 THURY",       0.0214,   188.1),
    ("19 WALTH",       0.0217,   220.0),
    ("5 1/2 PROG",     0.0217,   203.2),
    ("22 W.INS",       0.0220,   210.0),
    ("6 PROG",         0.0236,   169.3),
    ("24 W.INS",       0.0240,   210.0),
    ("18 THURY",       0.0243,   169.3),
    ("18 BA",          0.0244,   169.3),
    ("17 WALTH",       0.0256,   200.0),
    ("6 1/2 PROG",     0.0256,   169.3),
    ("26 W.INS",       0.0260,   180.0),
    ("17 THURY",       0.0275,   152.1),
    ("17 BA",          0.0276,   149.4),
    ("7 PROG",         0.0276,   145.1),
    ("28 W.INS",       0.0280,   180.0),
    ("7 1/2 PROG",     0.0295,   145.1),
    ("30 W.INS",       0.0300,   180.0),
    ("16 BA",          0.0311,   133.7),
    ("16 THURY",       0.0313,   137.3),
    ("8 PROG",         0.0315,   127.0),
    ("32 W.INS",       0.0320,   180.0),
    ("15 WALTH",       0.0327,   180.0),
    ("8 1/2 PROG",     0.0335,   127.0),
    ("34 W.INS",       0.0340,   150.0),
    ("15 BA",          0.0354,   121.0),
    ("9 PROG",         0.0354,   112.9),
    ("15 THURY",       0.0355,   123.3),
    ("36 W.INS",       0.0360,   150.0),
    ("9 WALTH",        0.0366,   160.0),
    ("9 1/2 PROG",     0.0374,   112.9),
    ("38 W.INS",       0.0380,   120.0),
    ("1 LOEW",         0.0394,   101.6),
    ("10 PROG",        0.0394,   101.6),
    ("13 WALTH",       0.0394,   180.0),
    ("14 BA",          0.0394,   110.4),
    ("7 WALTH",        0.0394,   140.0),
    ("40 W.INS",       0.0400,   120.0),
    ("11 PROG",        0.0433,   92.4),
    ("5 WALTH",        0.0433,   120.0),
    ("14 THURY",       0.0434,   110.9),
    ("45 W.INS",       0.0450,   120.0),
    ("13 THURY",       0.0457,   100.0),
    ("1.2 LOEW",       0.0472,   101.6),
    ("12 PROG",        0.0472,   84.7),
    ("13 BA",          0.0472,   101.6),
    ("3 WALTH",        0.0472,   110.0),
    ("50 W.INS",       0.0500,   100.0),
    ("12 BA",          0.0510,   90.9),
    ("13 PROG",        0.0512,   78.2),
    ("12 THURY",       0.0520,   90.1),
    ("11 WALTH",       0.0528,   170.0),
    ("55 W.INS",       0.0550,   100.0),
    ("1.4 LOEW",       0.0551,   84.7),
    ("14 PROG",        0.0551,   72.6),
    ("11 THURY",       0.0587,   80.9),
    ("11 BA",          0.0590,   82.0),
    ("1 WALTH",        0.0591,   110.0),
    ("15 PROG",        0.0591,   67.7),
    ("0-80 ASME",      0.0600,   80.0),
    ("60 W.INS",       0.0600,   100.0),
    ("16 PROG",        0.0630,   55.6),
    ("10 THURY",       0.0646,   72.8),
    ("65 W.INS",       0.0650,   80.0),
    ("1.7 LOEW",       0.0669,   72.6),
    ("17 PROG",        0.0669,   52.3),
    ("10 BA",          0.0670,   72.5),
    ("70 W.INS",       0.0700,   80.0),
    ("18 PROG",        0.0709,   49.4),
    ("1-56 ASME",      0.0730,   56.0),
    ("1-64 ASME",      0.0730,   64.0),
    ("1-72 ASME",      0.0730,   72.0),
    ("19 PROG",        0.0748,   46.8),
    ("75 W.INS",       0.0750,   80.0),
    ("9 BA",           0.0750,   64.9),
    ("9 THURY",        0.0756,   65.6),
    ("2 LOEW",         0.0787,   63.5),
    ("20 PROG",        0.0787,   44.5),
    ("80 W.INS",       0.0800,   60.0),
    ("85 W.INS",       0.0850,   60.0),
    ("8 THURY",        0.0858,   59.1),
    ("2-56 ASME",      0.0860,   56.0),
    ("2-64 ASME",      0.0860,   64.0),
    ("8 BA",           0.0870,   59.2),
    ("90 W.INS",       0.0900,   60.0),
    ("95 W.INS",       0.0900,   50.0),
    ("2.3 LOEW",       0.0906,   63.5),
    ("7 THURY",        0.0976,   53.1),
    ("7 BA",           0.0980,   52.9),
    ("3-48 ASME",      0.0990,   48.0),
    ("3-56 ASME",      0.0990,   56.0),
    ("100 W.INS",      0.1000,   50.0),
    ("U HOLTZ",        0.1000,   55.0),
    ("10/0 PEND",      0.1016,   90.0),
    ("2.6 LOEW",       0.1024,   56.4),
    ("6 BA",           0.1100,   47.9),
    ("6 THURY",        0.1106,   47.8),
    ("4-32 ASME",      0.1120,   32.0),
    ("4-36 ASME",      0.1120,   36.0),
    ("4-40 ASME",      0.1120,   40.0),
    ("4-40 UNC",       0.1120,   40.0),
    ("4-48 ASME",      0.1120,   48.0),
    ("M3 Coarse",      0.1180,   50.8),
    ("3 LOEW",         0.1181,   50.8),
    ("T HOLTZ",        0.1200,   55.0),
    ("1/8 BRASS",      0.1250,   26.0),
    ("1/8 CEI",        0.1250,   40.0),
    ("1/8 WHIT",       0.1250,   40.0),
    ("5-36 ASME",      0.1250,   36.0),
    ("5-40 ASME",      0.1250,   40.0),
    ("5-44 ASME",      0.1250,   44.0),
    ("5 THURY",        0.1256,   43.1),
    ("5/0 PEND",       0.1260,   80.0),
    ("5 BA",           0.1260,   43.1),
    ("3.5 LOEW",       0.1378,   42.3),
    ("6-32 ASME",      0.1380,   32.0),
    ("6-32 UNC",       0.1380,   32.0),
    ("6-36 ASME",      0.1380,   36.0),
    ("6-40 ASME",      0.1380,   40.0),
    ("M3.5 Coarse",    0.1380,   42.3),
    ("4 BA",           0.1420,   38.5),
    ("4 THURY",        0.1425,   38.7),
    ("0.148 GAS",      0.1480,   32.0),
    ("R HOLTZ",        0.1500,   55.0),
    ("7-30 ASME",      0.1510,   30.0),
    ("7-32 ASME",      0.1510,   32.0),
    ("7-36 ASME",      0.1510,   36.0),
    ("0 PEND",         0.1535,   66.0),
    ("5/32 CEI",       0.1563,   32.0),
    ("M4 Coarse",      0.1570,   36.3),
    ("4 LOEW",         0.1575,   36.3),
    ("3 BA",           0.1610,   34.8),
    ("3 THURY",        0.1618,   34.8),
    ("Q HOLTZ",        0.1620,   39.9),
    ("8-30 ASME",      0.1640,   30.0),
    ("8-32 ASME",      0.1640,   32.0),
    ("8-32 UNC",       0.1640,   32.0),
    ("8-36 ASME",      0.1640,   36.0),
    ("8-40 ASME",      0.1640,   40.0),
    ("12-6 PEND",      0.1732,   66.0),
    ("9-24 ASME",      0.1770,   24.0),
    ("9-30 ASME",      0.1770,   30.0),
    ("9-32 ASME",      0.1770,   32.0),
    ("M4.5 Coarse",    0.1770,   33.9),
    ("4.5 LOEW",       0.1772,   33.9),
    ("0 HOLTZ",        0.1800,   36.1),
    ("2 THURY",        0.1835,   31.4),
    ("2 BA",           0.1850,   31.4),
    ("S HOLTZ",        0.1850,   55.0),
    ("3/16 CEI",       0.1875,   32.0),
    ("3/16 BSF",       0.1880,   32.0),
    ("3/16 WHIT",      0.1880,   24.0),
    ("10-24 ASME",     0.1900,   24.0),
    ("10-24 UNC",      0.1900,   24.0),
    ("10-28 ASME",     0.1900,   28.0),
    ("10-30 ASME",     0.1900,   30.0),
    ("10-32 ASME",     0.1900,   32.0),
    ("10-32 UNF",      0.1900,   32.0),
    ("P HOLTZ",        0.1900,   39.9),
    ("0.196 GAS",      0.1960,   32.0),
    ("16 PEND",        0.1969,   60.0),
    ("5 LOEW",         0.1969,   31.8),
    ("M5 Coarse",      0.1970,   31.8),
    ("N HOLTZ",        0.2000,   36.1),
    ("1 THURY",        0.2083,   28.2),
    ("1 BA",           0.2090,   28.3),
    ("L HOLTZ",        0.2100,   28.9),
    ("12-24 ASME",     0.2160,   24.0),
    ("12-28 ASME",     0.2160,   28.0),
    ("12-32 ASME",     0.2160,   32.0),
    ("5.5 LOEW",       0.2165,   28.2),
    ("7/32 CEI",       0.2188,   26.0),
    ("7/32 BSF",       0.2190,   28.0),
    ("18 PEND",        0.2323,   50.0),
    ("0 BA",           0.2360,   25.4),
    ("M6 Coarse",      0.2360,   25.4),
    ("0 THURY",        0.2362,   25.4),
    ("6 LOEW",         0.2362,   25.4),
    ("M HOLTZ",        0.2400,   36.1),
    ("14-20 ASME",     0.2420,   20.0),
    ("14-24 ASME",     0.2420,   24.0),
    ("No.4 GAS",       0.2460,   27.0),
    ("1/4 BRASS",      0.2500,   26.0),
    ("1/4 BSF",        0.2500,   26.0),
    ("1/4 CEI",        0.2500,   26.0),
    ("1/4 UNC",        0.2500,   20.0),
    ("1/4 UNF",        0.2500,   28.0),
    ("1/4 WHIT",       0.2500,   20.0),
    ("1/4 SPARK",      0.2500,   24.0),
    ("K HOLTZ",        0.2500,   25.7),
    ("1/4 GAS",        0.2600,   27.0),
    ("16-18 ASME",     0.2680,   18.0),
    ("16-20 ASME",     0.2680,   20.0),
    ("16-22 ASME",     0.2680,   22.0),
    ("-1 THURY",       0.2681,   23.1),
    ("7 LOEW",         0.2756,   23.1),
    ("M7 Coarse",      0.2760,   25.4),
    ("9/32 CEI",       0.2813,   26.0),
    ("J HOLTZ",        0.2900,   25.7),
    ("18-18 ASME",     0.2940,   18.0),
    ("18-20 ASME",     0.2940,   20.0),
    ("-2 THURY",       0.3043,   20.7),
    ("5/16 CEI",       0.3125,   26.0),
    ("5/16 BSF",       0.3130,   22.0),
    ("5/16 UNC",       0.3130,   18.0),
    ("5/16 UNF",       0.3130,   24.0),
    ("5/16 WHIT",      0.3130,   18.0),
    ("8 LOEW",         0.3150,   21.2),
    ("M8 Coarse",      0.3150,   20.3),
    ("M8 Fine",        0.3150,   25.4),
    ("20-16 ASME",     0.3200,   16.0),
    ("20-18 ASME",     0.3200,   18.0),
    ("20-20 ASME",     0.3200,   20.0),
    ("I HOLTZ",        0.3300,   25.7),
    ("5/16 GAS",       0.3420,   27.0),
    ("-3 THURY",       0.3453,   18.5),
    ("22-16 ASME",     0.3460,   16.0),
    ("22-18 ASME",     0.3460,   18.0),
    ("9 LOEW",         0.3543,   19.5),
    ("H HOLTZ",        0.3600,   19.9),
    ("24-16 ASME",     0.3720,   16.0),
    ("24-18 ASME",     0.3720,   18.0),
    ("3/8 ADM",        0.3750,   24.0),
    ("3/8 BRASS",      0.3750,   26.0),
    ("3/8 BSF",        0.3750,   20.0),
    ("3/8 CEI",        0.3750,   26.0),
    ("3/8 UNC",        0.3750,   16.0),
    ("3/8 UNF",        0.3750,   24.0),
    ("3/8 WHIT",       0.3750,   16.0),
    ("3/8 SPARK",      0.3750,   24.0),
    ("1/8 BSP",        0.3830,   28.0),
    ("3/8 GAS",        0.3900,   27.0),
    ("-4 THURY",       0.3917,   16.7),
    ("10 LOEW",        0.3937,   18.1),
    ("M10 Coarse",     0.3940,   16.9),
    ("M10 Fine",       0.3940,   20.3),
    ("26-14 ASME",     0.3980,   14.0),
    ("26-16 ASME",     0.3980,   16.0),
    ("1/8 WPIPE",      0.4063,   28.0),
    ("G HOLTZ",        0.4100,   19.9),
    ("28-14 ASME",     0.4240,   14.0),
    ("28-16 ASME",     0.4240,   16.0),
    ("7/16 ADM",       0.4375,   24.0),
    ("7/16 BSF",       0.4375,   18.0),
    ("7/16 CEI",       0.4375,   26.0),
    ("7/16 CEI20",     0.4375,   20.0),
    ("7/16 UNC",       0.4375,   14.0),
    ("7/16 UNF",       0.4375,   20.0),
    ("7/16 WHIT",      0.4375,   14.0),
    ("-5 THURY",       0.4449,   15.0),
    ("30-14 ASME",     0.4500,   14.0),
    ("30-16 ASME",     0.4500,   16.0),
    ("F HOLTZ",        0.4500,   16.5),
    ("7/16 GAS",       0.4590,   27.0),
    ("M12 Coarse",     0.4724,   14.5),
    ("M12 Fine",       0.4724,   20.3),
    ("12 LOEW",        0.4724,   15.9),
    ("12MM SPARK",     0.4724,   25.4),
    ("1/2 ADM",        0.5000,   20.0),
    ("1/2 BRASS",      0.5000,   26.0),
    ("1/2 BSF",        0.5000,   16.0),
    ("1/2 CEI",        0.5000,   26.0),
    ("1/2 CEI20",      0.5000,   20.0),
    ("1/2 UNC",        0.5000,   13.0),
    ("1/2 UNF",        0.5000,   20.0),
    ("1/2 WHIT",       0.5000,   12.0),
    ("E HOLTZ",        0.5000,   13.1),
    ("-6 THURY",       0.5039,   13.5),
    ("1/2 GAS",        0.5150,   27.0),
    ("1/4 BSP",        0.5180,   19.0),
    ("1/4 WPIPE",      0.5313,   19.0),
    ("M15 Coarse",     0.5512,   12.7),
    ("14 LOEW",        0.5512,   14.1),
    ("14MM SPARK",     0.5512,   20.3),
    ("9/16 ADM",       0.5556,   20.0),
    ("D HOLTZ",        0.5600,   13.1),
    ("9/16 BSF",       0.5625,   16.0),
    ("9/16 CEI",       0.5625,   26.0),
    ("9/16 CEI20",     0.5625,   20.0),
    ("9/16 UNC",       0.5625,   12.0),
    ("9/16 UNF",       0.5625,   18.0),
    ("9/16 WHIT",      0.5625,   12.0),
    ("-7 THURY",       0.5709,   12.2),
    ("9/16 GAS",       0.5780,   27.0),
    ("5/8 ADM",        0.6250,   20.0),
    ("5/8 BRASS",      0.6250,   26.0),
    ("5/8 BSF",        0.6250,   14.0),
    ("5/8 CEI",        0.6250,   26.0),
    ("5/8 CEI20",      0.6250,   20.0),
    ("5/8 UNC",        0.6250,   11.0),
    ("5/8 UNF",        0.6250,   18.0),
    ("5/8 WHIT",       0.6250,   11.0),
    ("DD HOLTZ",       0.6250,   13.1),
    ("M16 Coarse",     0.6299,   12.7),
    ("M16 Fine",       0.6299,   16.9),
    ("16 LOEW",        0.6299,   12.7),
    ("5/8 GAS",        0.6370,   27.0),
    ("-8 THURY",       0.6496,   10.9),
    ("3/8 BSP",        0.6560,   19.0),
    ("11/16 ADM",      0.6875,   20.0),
    ("11/16 CEI",      0.6875,   26.0),
    ("11/16 CEI20",    0.6875,   20.0),
    ("3/8 WPIPE",      0.6875,   19.0),
    ("M18 Coarse",     0.7087,   10.2),
    ("18 LOEW",        0.7087,   11.5),
    ("18MM SPARK",     0.7087,   16.9),
    ("-9 THURY",       0.7362,   9.8),
    ("3/4 ADM",        0.7500,   14.0),
    ("3/4 BRASS",      0.7500,   26.0),
    ("3/4 BSF",        0.7500,   12.0),
    ("3/4 CEI",        0.7500,   26.0),
    ("3/4 CEI20",      0.7500,   20.0),
    ("3/4 UNC",        0.7500,   10.0),
    ("3/4 UNF",        0.7500,   16.0),
    ("3/4 WHIT",       0.7500,   10.0),
    ("C HOLTZ",        0.7500,   9.5),
    ("3/4 GAS",        0.7700,   27.0),
    ("M20 Coarse",     0.7874,   10.2),
    ("M20 Fine",       0.7874,   16.9),
    ("13/16 ADM",      0.8125,   14.0),
    ("1/2 BSP",        0.8250,   14.0),
    ("-10 THURY",      0.8346,   8.9),
    ("1/2 WPIPE",      0.8438,   14.0),
    ("M22 Coarse",     0.8661,   10.2),
    ("7/8 ADM",        0.8750,   14.0),
    ("7/8 BRASS",      0.8750,   26.0),
    ("7/8 BSF",        0.8750,   11.0),
    ("7/8 UNC",        0.8750,   9.0),
    ("7/8 UNF",        0.8750,   14.0),
    ("7/8 WHIT",       0.8750,   9.0),
    ("7/8 SPARK",      0.8750,   18.0),
    ("B HOLTZ",        0.8750,   8.3),
    ("7/8 GAS",        0.8850,   27.0),
    ("5/8 BSP",        0.9020,   14.0),
    ("15/16 ADM",      0.9375,   14.0),
    ("5/8 WPIPE",      0.9375,   14.0),
    ("M24 Coarse",     0.9449,   8.5),
    ("M24 Fine",       0.9449,   12.7),
    ("-11 THURY",      0.9492,   8.0),
    ("1 ADM",          1.0000,   12.0),
    ("1 BRASS",        1.0000,   26.0),
    ("1 BSF",          1.0000,   10.0),
    ("1 UNC",          1.0000,   8.0),
    ("1 UNF",          1.0000,   12.0),
    ("1 WHIT",         1.0000,   8.0),
    ("A HOLTZ",        1.0000,   6.6),
    ("1 GAS",          1.0060,   27.0),
    ("1 1/8 BRASS",    1.0400,   26.0),
    ("3/4 BSP",        1.0410,   14.0),
    ("1 1/16 ADM",     1.0625,   12.0),
    ("3/4 WPIPE",      1.0625,   14.0),
    ("M27 Coarse",     1.0630,   8.5),
    ("-12 THURY",      1.0787,   7.2),
    ("1 1/8 ADM",      1.1250,   12.0),
    ("1 1/8 BSF",      1.1250,   9.0),
    ("1 1/8 UNC",      1.1250,   7.0),
    ("1 1/8 UNF",      1.1250,   12.0),
    ("M30 Coarse",     1.1811,   7.3),
    ("M30 Fine",       1.1811,   12.7),
    ("1 3/16 ADM",     1.1875,   12.0),
    ("7/8 BSP",        1.1890,   14.0),
    ("-13 THURY",      1.2048,   6.5),
    ("7/8 WPIPE",      1.2188,   14.0),
    ("1 1/4 BRASS",    1.2500,   26.0),
    ("1 1/4 BSF",      1.2500,   9.0),
    ("1 1/4 UNC",      1.2500,   7.0),
    ("1 1/4 UNF",      1.2500,   12.0),
    ("1 1/4 WHIT",     1.2500,   7.0),
    ("1 1/4 ADM",      1.2500,   12.0),
    ("M33 Coarse",     1.2992,   7.3),
    ("1 BSP",          1.3090,   11.0),
    ("1 5/16 ADM",     1.3125,   12.0),
    ("1 WPIPE",        1.3438,   11.0),
    ("1 3/8 ADM",      1.3750,   12.0),
    ("1 3/8 BSF",      1.3750,   8.0),
    ("1 3/8 UNC",      1.3750,   6.0),
    ("1 3/8 UNF",      1.3750,   12.0),
    ("-14 THURY",      1.3858,   5.8),
    ("M36 Coarse",     1.4173,   6.4),
    ("M36 Fine",       1.4173,   8.5),
    ("1 7/16 ADM",     1.4375,   12.0),
    ("1 1/2 ADM",      1.5000,   12.0),
    ("1 1/2 BRASS",    1.5000,   26.0),
    ("1 1/2 BSF",      1.5000,   8.0),
    ("1 1/2 UNC",      1.5000,   6.0),
    ("1 1/2 UNF",      1.5000,   12.0),
    ("1 1/2 WHIT",     1.5000,   6.0),
    ("M39 Coarse",     1.5354,   6.4),
    ("-15 THURY",      1.5748,   5.2),
    ("1 5/8 BSF",      1.6250,   8.0),
    ("M42 Coarse",     1.6535,   5.6),
    ("M42 Fine",       1.6535,   8.5),
    ("1 1/4 WPIPE",    1.6875,   11.0),
    ("1 3/4 BSF",      1.7500,   7.0),
    ("1 3/4 UNC",      1.7500,   5.0),
    ("M45 Coarse",     1.7717,   5.6),
    ("-16 THURY",      1.7874,   4.7),
    ("M48 Coarse",     1.8898,   5.1),
    ("M48 Fine",       1.8898,   8.5),
    ("1 1/2 WPIPE",    1.9063,   11.0),
    ("2 BSF",          2.0000,   7.0),
    ("2 UNC",          2.0000,   4.5),
    ("2 WHIT",         2.0000,   4.5),
    ("-17 THURY",      2.0276,   4.2),
    ("M52 Coarse",     2.0472,   5.1),
    ("1 3/4 WPIPE",    2.1563,   11.0),
    ("M56 Coarse",     2.2047,   4.6),
    ("M56 Fine",       2.2047,   6.4),
    ("2 1/4 BSF",      2.2500,   6.0),
    ("-18 THURY",      2.2992,   3.8),
    ("M60 Coarse",     2.3622,   4.6),
    ("2 WPIPE",        2.3750,   11.0),
    ("2 1/2 BSF",      2.5000,   6.0),
    ("M64 Coarse",     2.5197,   4.2),
    ("M64 Fine",       2.5197,   6.4),
    ("-19 THURY",      2.6102,   3.4),
    ("2 1/4 WPIPE",    2.6250,   11.0),
    ("M68 Coarse",     2.6772,   4.2),
    ("2 3/4 BSF",      2.7500,   6.0),
    ("-20 THURY",      2.9606,   3.1),
    ("2 1/2 WPIPE",    3.0000,   11.0),
    ("3 BSF",          3.0000,   5.0),
    ("2 3/4 WPIPE",    3.2500,   11.0),
    ("3 WPIPE",        3.5000,   11.0),
    ("3 1/4 WPIPE",    3.7500,   11.0),
    ("5 1/2 WPIPE",    4.0000,   11.0),
    ("3 3/4 WPIPE",    4.2500,   11.0),
    ("4 WPIPE",        4.5000,   11.0),
    ("4 1/2 WPIPE",    5.0000,   11.0),
    ("5 WPIPE",        5.5000,   11.0),
    ("5 1/2 WPIPE",    6.0000,   11.0),
    ("6 WPIPE",        6.5000,   11.0),
    ("1/4 UNEF",       0.2500,   32.0),
    ("5/16 UNEF",      0.3125,   32.0),
    ("3/8 UNEF",       0.3750,   32.0),
    ("7/16 UNEF",      0.4375,   32.0),
    ("1/2 UNEF",       0.5000,   28.0),
    ("9/16 UNEF",      0.5625,   24.0),
    ("5/8 UNEF",       0.625,    24.0),
    ("11/16 UNEF",     0.6875,   24.0),
    ("3/4 UNEF",       0.75,     20.0),
    ("7/8 UNEF",       0.875,    20.0),
    ("1 UNEF",         1.000,    20.0),
)

manpage = '''Usage:  thd [options] thread_size
 
Prints thread information for the indicated thread.  The thread size
can be specified as decimal inches, a hyphen, and the threads per
inch.  You may also replace the hyphen with a space.  The following
forms are equivalent:
 
    0.25-20
    0.25 20
    1/4-20
    1/4 20
 
You can specify nominal diameters larger than one using fractional
inches as follows:
 
    1 1/2-6
    1 1/2 6
 
Equivalently, 
 
    1.5-6
    1.5 6
 
You can also specify a single number on the command line.  This 
will be interpreted as threads per inch (or pitch in mm if the -m
option was used).  
 
US number size threads can be designated by prefacing the diameter
with the letter 'N' or 'n'.  Example:  Use 'n6-32' for a 6-32 thread.
The number size is converted to a diameter in inches by the formula
dia = 0.060 + N*0.013.  While most of the most common values for N are
in the range 0 to 14, the program will let you enter an N up to a
value of 500.
 
Inch-sized thread dimensions are calculated from the Unified thread
formulas in the ASME B1.1-1989 document, "Unified Inch Screw Threads".
The program uses the same formulas for metric threads; this may or may
not be consistent with other metric standards.
 
Options
 
    -a frac
        Show the minimum and maximum usable wire sizes for this
        thread.  The fraction frac is < 1 and corresponds to the wire
        contacting the flank of the thread at that fraction of the
        radial height of the Unified thread flank, which is 5*H/8,
        where H is sqrt(3)/2 times the pitch.  Since the minimum wire
        has its center on the pitch circle, the fraction must be
        greater than (3/8*H)/(5/8*H) = 0.40.  Default is {frac}.
 
    -b
        Print a table of metric pitches and equivalent Imperial
        threads/feeds on the Clausing 5914 lathe that can be used
        to cut a thread near the desired metric pitch.
 
    -c num
        Specify the Class of the thread.  The number num must be
        1, 2, or 3.  Class 2 is the default.
 
    -h
        Print this help out.
 
    -l 
        List the taps and dies on hand.
    -m
        The command line parameters are to be interpreted in mm.
        The first number is the nominal diameter in mm and the
        second number is the pitch in mm.  Example:
 
            -m 6 1
 
        means a 6 mm diameter thread with a pitch of 1 mm.
 
        If a single parameter is passed in when -m is used, it is
        interpreted as the thread's pitch in mm.
 
    -o 
        Show threads whose outside diameter is within 5%% of the given OD.
 
    -t
        Show threads whose threads per inch is within 5%% of the given tpi.
 
    -u
        Print data for common UNC and UNF sizes.
 
    -w size
        Specify the wire size to use.  Normally, the results will 
        use the best calculated wire size.  See Wire Sizes below.
 
Wire Sizes
    The pitch diameter of threads can be measured using thread wires
    (see e.g. Machinery's Handbook).  The program calculates the
    measurement over wires for the best wire size, which contacts the
    thread flank at the pitch diameter.  You may have a set of thread
    measuring wires on hand, in which case you'd want the program to
    use your wire sizes.
 
    You can enter your wire sizes on hand by editing the wires list.
 
    If a -w option is given on the command line, it will override the
    nearest wire size from the internal list.
 
    For a specified thread pitch, the given value for "const" is the
    number that should be subtracted from the measurement over the
    wires to get the pitch diameter.
 
Warning
    The formulas from the ASME standard will produce numbers that may
    differ from what are published in the tables of that document (or
    Machinery's Handbook, which appears to copy the ASME tables).  It
    is not clear to me which should be considered correct - the
    formulas generating the tables or the tables themselves.  It's
    likely most people will assume the tables are correct, even if
    they do contain errors that don't match the formulas.  Thus, use
    the program's output with this fact in mind.
 
Output Notes
    Allowance is to preclude surface-to-surface fit between mating
    parts for Class 1A threads.  For Class 2A threads, the allowance
    may be used to accomodate plating or coating.
 
    Thread shear areas are geometric and will somewhat overestimate
    the shear strength (see the ASME document).
 
    MOW = measurement over wires
 
    H = sqrt(3)*pitch/2
 
    The minimum wire size is the wire diameter that would contact the
    thread at the root of a geometrically perfect Unified thread and,
    simultaneously, at both flanks of the thread.  The maximum wire
    size is gotten by allowing the wire to touch the flank at a
    specified fraction of the height from the root to the crest, which
    is 5*H/8 in a Unified thread.  If the fraction is 100%%, the
    contact is at the intersection of the flank and the outside flat.
    The fraction is given as a percentage in the description and can
    be changed in the code.  Both of these numbers attempt to give you
    the range of usable wires for measurement; bear in mind that the
    most accurate measurements are made with the best wire size.
 
    cos(29 degrees) is the angle to set the compound feed over for
    cutting threads.  To cut a thread with a vee tool or a formed
    tool, first turn the OD to the specified major diameter.  Then
    touch the tip of the cutting tool to the OD.  When you've fed the
    tool in by the amount given in the "Compound feed" column, you
    should be at the maximum pitch diameter.  If your compound slide
    feeds in half of the indicated distance, use the feed distance in
    the "Half compound feed" column.
 
    A better way to set the cutting tool is to use a thread gauge.
    This will set the flanks of the cutting tool a known distance
    away from the major diameter.  You can measure this known distance
    on your threading gauge with a rod of appropriate size.
 
    The thread depth for a sharp vee thread is H and is the major
    diameter to the root of the thread.  The Unified thread depth is
    5*H/8.
    
    The compound feed is the double depth divided by the cosine of 29
    degrees.
'''

def out(*v, **kw):
    '''Utility output to a stream.  Keywords:
    sep     Separator between *v elements
    nl      Include newline when finished with *v
    stream  Where to output
    rep     How to convert objects to a string 
    '''
    sep = kw.setdefault("sep", " ")
    nl  = kw.setdefault("nl", True)
    stream = kw.setdefault("stream", sys.stdout)
    rep  = kw.setdefault("repr", str)
    if v:
        stream.write(sep.join([rep(i) for i in v]))
    if nl:
        stream.write("\n")

def Usage():
    name = sys.argv[0]
    c = "c"
    out('''Usage:  {name} [options] thread_size
 
Prints thread information for the indicated external thread.  Examples:
 
    thread n6-32
        US numbered machine screw sizes are preceded by an 'n'
    thread 0.25-20
    thread 0.25 20
    thread 1/4-20
    thread 1/4 20
    thread 1 1/2-6
    thread 1 1/2 6
 
Options
    -a frac     Min & max wire sizes for this thread (use -h for details)
    -b          Show lathe threads closest to metric pitches
    -c num      Specify {c}lass 1, 2, or 3 thread (2 is default)
    -h          Detailed help 
    -l          List the taps and dies on hand.
    -m          Metric threads:  dia in mm, pitch in mm
    -o          Show threads within 5% of given OD
    -t          Show threads within 5% of given tpi
    -T          Print table of UNC, UNF, UNEF threads
    -u          Show common UNC and UNF sizes
    -w dia      Specify size of thread wire to use

Use -h for more detailed help.'''.format(**locals()))
    sys.exit(1)

def Error(s):
    sys.stderr.write(s + "\n")
    sys.exit(1)

def ProcessCommandLine():
    d = {}
    d["-a"] = 0.95  # Fraction of 5/8*H for max thread wire diameter
    d["-c"] = None  # Thread Class
    d["-m"] = False # Metric threads (dia & pitch in mm)
    d["-o"] = None  # Show threads within 5% of given OD
    d["-t"] = False # Show threads within 5% of given tpi
    d["-T"] = False # Print table 4 of Machinery's Handbook
    d["-w"] = None  # Size of thread wire to use
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "a:bc:hlmotTuw:")
    except getopt.error as str:
        out("getopt error:  %s\n" % str)
        sys.exit(1)
    for opt in optlist:
        if opt[0] == "-a":
            d["-a"] = float(opt[1])
            if d["-a"] < 0.4 or d["-a"] >= 1:
                Error("Value for -a option must be >= 0.4 and < 1.0.")
        if opt[0] == "-b":
            BestThreadMatches(d)
            exit(0)
        if opt[0] == "-c":
            #global thread_class
            d["-c"] = int(opt[1])
            if d["-c"] < 1 or d["-c"] > 3:
                Error("Thread %slass must be 1, 2, or 3" % "c")
        if opt[0] == "-h":
            mp = {
                "frac" : d["-a"],
            }
            out(manpage.format(**mp))
            exit(0)
        if opt[0] == "-l":
            ListSizes()
            exit(0)
        if opt[0] == "-m":
            d["-m"] = True
        if opt[0] == "-o":
            d["-o"] = True
        if opt[0] == "-T":
            d["-T"] = True
        if opt[0] == "-t":
            d["-t"] = True
        if opt[0] == "-u":
            PrintCommon(d)
            exit(0)
        if opt[0] == "-w":
            d["-w"] = float(opt[1])
            if d["-w"] <= 0:
                Error("Thread wire diameter must be > 0")
    if d["-o"] or d["-t"] or d["-T"]:
        if d["-T"]:
            PrintTable4(d)
        else:
            if len(args) < 1:
                Usage()
            else:
                if d["-o"]:
                    SearchOD(args, d)
                elif d["-t"]:
                    SearchTPI(args, d)
                else:
                    raise ValueError("Unrecognized!")
    if len(args) < 1 or len(args) > 3:
        Usage()
    # If any elements contain a '-', increase the number of arguments
    # by parsing on the '-'.
    new_args = []
    for x in args:
        if string.find(x, "-") != -1:
            new_args += string.split(x, "-")
        else:
            new_args += [x]
    return new_args, d

def ListSizes():
    out(my_sizes)
    exit(0)

def SearchOD(args, d):
    arg, od = args[0], 0.0
    od = 0.0
    try:
        od = float(eval(arg))
        if d["-m"]:
            od /= mm_per_in
            out("Search for threads close to OD", arg, "mm", lf=0, nl=0)
            out(" (%.3f in)" % od)
        else:
            out("Search for threads close to OD", arg, "inches")
    except Exception:
        out("'%s' is not a valid OD" % arg)
        exit(1)
    found = 0
    for name, OD, tpi in weird_threads:
        if abs(od - OD)/od < tolerance:
            found = 1
            long_name = weird_thread_names[name.split()[-1]]
            out("    %-11s  OD = %6.4f\"  tpi = %.1f %s" % 
                (name, OD, tpi, long_name))
    if not found:
        out("  No matches")
    exit(0)

def SearchTPI(args, d):
    arg, tpi = args[0], 0.0
    try:
        tpi = float(eval(arg))
    except Exception:
        out("'%s' is not a valid tpi" % arg)
        exit(1)
    out("Search for threads close to", arg, "tpi")
    found = 0
    for name, OD, TPI in weird_threads:
        if abs(tpi - TPI)/tpi < tolerance:
            found = 1
            long_name = weird_thread_names[name.split()[-1]]
            out("    %-11s  OD = %6.4f tpi = %.1f %s" % 
                (name, OD, TPI, long_name))
    if not found:
        out("  No matches")
    exit(0)

def PrintCommon(d):
    for spec, diameter, tpi in common_sizes:
        out(spec)
        PrintResults(diameter, tpi, d)
        out("-" * 70)
        out()
    exit(0)

def Float(x):
    # Interpret the string x as a float.  Also allow the form "n/d".
    try:
        y = float(x)
    except Exception:
        if "/" in x:
            fields = x.split("/")
            if len(fields) != 2:
                raise "Not a properly formed fraction"
            y = float(fields[0])/float(fields[1])
        else:
            float(x)
    return y

def PrintPitchProperties(arg, d):
    'arg will either be tpi or pitch in mm'
    # We need the pitch in inches
    if d["-m"]:
        p = Float(arg)/mm_per_in
    else:
        p = 1/Float(arg)
    out(" " * spc, "   inches        mm")
    out(" " * spc, "   ------        ---")
    out(fmt1 % ("Threads per inch or mm", 1/p, 1/(mm_per_in*p)))
    out(fmt % ("Pitch", p, p*mm_per_in))
    out("PD = MOW - const")
    PrintBestWire(p, d)
    best_wire_size = p/(2*cos(30*pi/180))
    const = 3*best_wire_size - p*sqrt(3)/2
    out(fmt % ("    const", const, const*mm_per_in))
    if d["-w"]:
        W = d["-w"]
        s = "User-specified wire diameter"
    else:
        # Find the closest matching wire on hand
        W = FindClosestWire(best_wire_size)
        s = "On-hand wire size"
    if W:
        out(fmt3 % (s, W, W*mm_per_in))
        const = 3*W - p*sqrt(3)/2
        out(fmt % ("    const", const, const*mm_per_in))
    out()
    H = p * cos(pi/6)
    ThreadDepths(H)
    exit(0)

def GetDiameter(s, d):
    '''Is either a number sized diameter, a decimal number, or a fraction.
    Return the diameter in decimal inches.
    '''
    if s[0] == 'N' or s[0] == 'n':
        return 0.06 + 0.013*int(s[1:])
    elif string.find(s, "/") != -1:
        numerator, denominator = map(float, string.split(s, "/"))
        return numerator/denominator
    else:
        diameter = float(s)
        if d["-m"]:
            diameter /= 25.4
        return diameter

def M(pitch_diameter, tpi, wire_diameter, starts=1):
    '''Calculate MOW given the PD, pitch, and wire diameter.
    starts is the number of thread starts (here, we only use 1).
    '''
    E = pitch_diameter
    W = wire_diameter
    A = pi/6
    T = 1/(2*tpi)
    L = starts/tpi
    B = atan(L/(pi*E))
    # For formula, see MH, 19th ed., p 1378
    M = E - T/tan(A) + W*(1 + 1/sin(A) + 0.5*tan(B)*tan(B)*cos(A)/tan(A))
    return M

def FindClosestWire(d):
    if d < wires[0] or d > wires[-1]:
        return 0
    for ix in xrange(len(wires)):
        if d < wires[ix]:
            # Found an upper bound
            dlower = abs(d - wires[ix-1])
            dupper = abs(d - wires[ix])
            if dlower < dupper:
                return wires[ix-1]
            else:
                return wires[ix]


# Clausing 5914 lathe threads per inch
lathe_threads = ( 
    "4", "4.5", "5", "5.5", "5.75", "6", "6.5", "6.75", "7", "8", "9", "10",
    "11", "11.5", "12", "13", "13.5", "14", "16", "18", "20", "22", "23",
    "24", "26", "27", "28", "32", "36", "40", "44", "46", "48", "52", "54",
    "56", "64", "72", "80", "88", "92", "96", "104", "108", "112", "128",
    "144", "160", "176", "184", "192", "208", "216", "224"
)

# Clausing 5914 lathe feeds in mils per revolution
lathe_feeds = [
    0.65, 0.68, 0.70, 0.76, 0.79, 0.83, 0.92, 0.94, 1.10, 1.30, 1.36, 1.40,
    1.50, 1.60, 1.70, 1.80, 2.00, 2.20, 2.60, 2.70, 2.80, 3.00, 3.10, 3.30,
    3.60, 4.10, 4.60, 5.20, 5.40, 5.60, 6.10, 6.30, 6.60, 7.30, 8.10, 9.20,
    10.5, 10.9, 11.3, 12.2, 12.7, 13.4, 14.7, 16.3, 18.3, 20.9, 21.8, 22.6,
    24.4, 25.5, 26.7, 29.3, 32.6, 36.7
]

metric_pitches = []
in_to_mm = 25.4

def InitializeThreads(d):
    global lathe_feeds
    lathe_feeds = ["%.5f" % (x/1000) for x in lathe_feeds]
    for ix in xrange(len(lathe_feeds)):
        if lathe_feeds[ix][-1] == "0":
            lathe_feeds[ix] = lathe_feeds[ix][:-1]
    lathe_feeds = tuple(lathe_feeds)
    global metric_pitches
    metric_pitches = (range(25, 101, 5) + range(100, 201, 10) + 
        range(225, 401, 25) + [125, 175])
    metric_pitches.sort()
    metric_pitches = ["%.2f" % (x/100) for x in metric_pitches]
    metric_pitches = tuple(metric_pitches)

def GetBestMatch(pitch_mm):
    closest = ""
    pct_dev = 1e9
    for thread in lathe_threads:
        pitch = 1/float(thread) * in_to_mm
        dev = abs(100*(pitch - pitch_mm)/pitch_mm)
        if dev < pct_dev:
            closest = thread
            pct_dev = dev
    for feed in lathe_feeds:
        pitch = float(feed) * in_to_mm
        dev = abs(100*(pitch - pitch_mm)/pitch_mm)
        if dev < pct_dev:
            closest = feed
            pct_dev = dev
    pct_dev = "%.1f" % pct_dev
    if pct_dev[0] == "0":
        pct_dev = " " + pct_dev[1:]
    return closest, pct_dev

def BestThreadMatches(d):
    InitializeThreads(d)
    out('''How to use Clausing 5914 lathe to cut metric threads:  This table
gives typical metric threads and the nearest thread or feed to the
metric pitch.
''')
    out('''
    Pitch         Closest
  mm    inches    tpi/lead   %Dev
------  ------    --------   ----
'''[1:-1])
    for pitch in metric_pitches:
        closest, pct_dev = GetBestMatch(float(pitch))
        out("%5s   %6.4f      %-8s  %s" % 
            (pitch, float(pitch)/25.4, closest, pct_dev))

def WireSizeLimits(pitch, d):
    'Return the minimum and maximum wire diameters.'
    H = sqrt(3)/2*pitch
    min = H/2
    max = 4/3*(5/8*d["-a"] + 1/4)*H
    return min, max

def PrintBestWire(pitch, d):
    best_wire_size = pitch/(2*cos(30*pi/180))
    min, max = WireSizeLimits(pitch, d)
    out("Measurements over wires")
    out(fmt3 % ("    Min wire size", min, min*mm_per_in))
    s =     "    Max wire size (%d%%)" % (int(100*d["-a"]))
    out(fmt3 % (s, max, max*mm_per_in))
    out(fmt6 % ("    Best wire size", best_wire_size, best_wire_size*mm_per_in))

def GetNearestDrillSize(D, d):
    assert(0 < D <= 1/2)
    if D == 1/2:
        return "1/2"
    sizes = drills.keys()
    sizes.sort()
    for ix in xrange(len(sizes)):
        if D > sizes[ix]:
            continue
        break
    # ix is now the index of the size which is just larger
    larger = sizes[ix]
    smaller = sizes[ix-1]
    size = smaller
    if larger - D <= D - smaller:
        size = larger
    return drills[size]

def GetNearestSixtyFourth(D):
    assert(D <= 1)
    if D == 1:
        return "1"
    denom = 64
    for numer in xrange(1, 64):
        if numer/denom < D:
            continue
        smaller = numer - 1
        larger  = numer
        if D - smaller/denom < larger/denom - D:
            numer = smaller
        else:
            numer = larger
        while numer % 2 == 0:
            numer /= 2
            denom /= 2
        return "%d/%d" % (numer, denom)

def TapDrill(nominal_diameter, percent, pitch, d):
    D = nominal_diameter - 3/4*sqrt(3)*percent/100*pitch
    if D <= 1/2:
        size = GetNearestDrillSize(D, d)
    elif D <= 1:
        size = GetNearestSixtyFourth(D)
    else:
        size = ""
    return D, size

def PrintResults(diameter, tpi, d):
    A = asme.UnifiedThread(diameter, tpi, thread_class)
    p = 1/tpi
    H = p * cos(pi/6)
    out(" " * spc, "   inches        mm")
    out(" " * spc, "   ------        ---")
    out(fmt % ("Nominal diameter", diameter, diameter*mm_per_in))
    out(fmt1 % ("Threads per inch or mm", tpi, tpi/mm_per_in))
    out(vf % ("Thread %slass" % "c"), "  %2d" % thread_class)
    out(fmt % ("Pitch", 1/tpi, mm_per_in/tpi))
    out(fmt % ("Allowance", A.Allowance(), A.Allowance()*mm_per_in))
    # Thread tensile strength area (ASME 1989, Appendix B)
    a = diameter - 0.9743*p
    AS = pi/4*a*a
    out(fmt6 % ("Tensile area, in^2 or mm^2", AS, AS*mm_per_in*mm_per_in))
    # Thread shear area
    # xx Note:  this prints out values that cannot be right.
    if 0:
        out("Min. thread shear area (in^2 or mm^2)")
        ASn = pi/p*A.Dmin()*(p/2 + 0.57735*(A.Dmin() - A.emax()))
        ASs = pi/p*A.dmax()*(p/2 + 0.57735*(A.Emin() - A.dmax()))
        out(fmt % ("    External thread", ASs, ASs*mm_per_in*mm_per_in))
        out(fmt % ("    Internal thread", ASn, ASn*mm_per_in*mm_per_in))
    out()
    out("External thread")
    out("    Major diameter")
    out(fmt % ("        Max", A.Dmax(), A.Dmax()*mm_per_in))
    out(fmt % ("        Min", A.Dmin(), A.Dmin()*mm_per_in))
    out(fmt % ("        Tolerance", A.Dmax()-A.Dmin(), (A.Dmax()-A.Dmin())*mm_per_in))
    out("    Pitch diameter")
    out(fmt % ("        Max", A.Emax(), A.Emax()*mm_per_in))
    out(fmt % ("        Min", A.Emin(), A.Emin()*mm_per_in))
    out(fmt % ("        Tolerance", A.Emax()-A.Emin(), (A.Emax()-A.Emin())*mm_per_in))
    out()
    out("Internal thread")
    out("    Minor diameter")
    out(fmt % ("        Max", A.dmax(), A.dmax()*mm_per_in))
    out(fmt % ("        Min", A.dmin(), A.dmin()*mm_per_in))
    out(fmt % ("        Tolerance", A.dmax()-A.dmin(), (A.dmax()-A.dmin())*mm_per_in))
    out("    Pitch diameter")
    out(fmt % ("        Max", A.emax(), A.emax()*mm_per_in))
    out(fmt % ("        Min", A.emin(), A.emin()*mm_per_in))
    out(fmt % ("        Tolerance", A.emax()-A.emin(), (A.emax()-A.emin())*mm_per_in))
    out()
    PrintBestWire(1/tpi, d)
    best_wire_size = 1/(2*tpi*cos(30*pi/180))
    mow_max = M(A.Emax(), tpi, best_wire_size)
    mow_min = M(A.Emin(), tpi, best_wire_size)
    out(fmt % ("        Meas. over best wires, max", mow_max,
    mow_max*mm_per_in))
    out(fmt % ("        Meas. over best wires, min", mow_min,
    mow_min*mm_per_in))
    if d["-w"]:
        W = d["-w"]  # Wire diameter
        s = "User-specified wire diameter"
    else:
        # Find the closest matching wire on hand
        W = FindClosestWire(best_wire_size)
        s = "    On-hand wire size"
    if W:
        out(fmt3 % (s, W, W*mm_per_in))
        mow_max = M(A.Emax(), tpi, W)
        mow_min = M(A.Emin(), tpi, W)
        out(fmt % ("        Meas. over wires, max", mow_max,
        mow_max*mm_per_in))
        out(fmt % ("        Meas. over wires, min", mow_min,
        mow_min*mm_per_in))
        out()
    out("Tap drills")
    fmtf = fmt + "    %s"
    for percent in xrange(50, 80, 5):
        D, F = TapDrill(diameter, percent, 1/tpi, d)
        out(fmtf % ("    %d%% thread" % percent, D, D*mm_per_in, F))
    out()
    ThreadDepths(H)

def ThreadDepths(H):
    '''These thread depths came from the Atlas manual of lathe operation,
    as the ones used from the standard don't give the correct values.

    Draw a picture of one side of a 60 degree vee thread.  The depth of
    thread D will be sqrt(3)/2*P where P is the pitch = 1/tpi.  For the
    National Form thread, the flat at top and bottom of the thread is 
    f = P/8 wide (along the screw axis).  This translates into a 
    corresponding height of sqrt(3)/2*f.  Thus, the depth of thread Dn
    for the National Form is
            
            Dn = D - 2*(sqrt(3)/2*f)

    or

            Dn = 3*sqrt(3)/8*P = 0.64952*P

    Now, when we're cutting threads on the lathe, we'll use a vee tool
    and cut a vee bottom.  But we'll turn the OD so that the thread has
    the requisite National Form flat.  In this case the depth of thread
    Dl is 

            Dl = D - sqrt(3)/2*f = sqrt(3)/2*P - sqrt(3)/2*(P/8)
               = (7/8) * (sqrt(3)/2) * P
               = 7*sqrt(3)*P/16
    '''
    C = cos(29*pi/180)
    if 1:
        pitch = 2*H/sqrt(3)
        A = 3*sqrt(3)*pitch/8
        B = 7*sqrt(3)*pitch/16
        # These are the values from the Atlas book
        out("Sharp V thread with National Form flat on OD, compound at 29 deg")
        out(fmt3 % ("    Double depth", 2*B, 2*B*mm_per_in))
        out(fmt3 % ("    Compound feed, DD/cos(29)", 2*B/C, 2*B*mm_per_in/C))
        out()
        out("Unified thread, compound at 29 deg")
        out(fmt3 % ("    Flat on form tool", pitch/8, pitch/8*mm_per_in))
        out(fmt3 % ("    Double depth", 2*A, 2*A*mm_per_in))
        out(fmt3 % ("    Compound feed, DD/cos(29)", 2*A/C, 2*A*mm_per_in/C))
    else:
        # These are the values from the standard
        out("Sharp V thread (H = sqrt(3)*pitch/2, C = cos(29 deg) ~ 7/8)")
        out(fmt %  ("    Thread depth H (Sharp vee)", H, H*mm_per_in))
        out(fmt3 % ("    Double depth 2*H", 2*H, 2*H*mm_per_in))
        out(fmt3 % ("    Compound feed 2*H/C", 2*H/C, 2*H/C*mm_per_in))
        out(fmt3 % ("    Double compound feed 4*H/C", 4*H/C, 4*H/C*mm_per_in))
        out()
        out("Unified thread, compound at 29 deg")
        out(fmt3 % ("    Flat on form tool", 1/4*H, 1/4*H*mm_per_in)) 
        h = 5/8*H
        out(fmt %  ("    Thread depth h = 5*H/8", h, h*mm_per_in))
        out(fmt3 % ("    Double depth 2*h", 2*h, 2*h*mm_per_in))
        out(fmt3 % ("    Compound feed 2*h/C", 2*h/C, 2*h/C*mm_per_in))
        out(fmt3 % ("    Double compound feed 4*h/C", 4*h/C, 4*h/C*mm_per_in))

def PrintTable4(d):
    '''Duplicate Table 4 from Machinery's Handbook, 19th ed., pg 1276.
    '''
    out('''
                       External Thread                  Internal Thread
                    Major dia.    Pitch dia.         Minor dia.    Pitch dia.
Thread         Cl  Dmax   Dmin   Emax   Emin    Cl  dmin   dmax   emin   emax
-------------- -- ------ ------ ------ ------   -- ------ ------ ------ ------
'''[1:-1])
    for thd in table4:
        PrintThread(thd, d)
    exit(0)

def PrintThread(thd, d):
    '''thd is a 2- or 3-tuple containing a string designating the OD, the
    tpi, and the thread series.  d contains the options.
    '''
    conv_ser = {"c":"UNC", "f":"UNF", "e":"UNEF", "s":"UNS"}
    series = "UN" if len(thd) == 2 else conv_ser[thd[2]]
    D, tpi, fmt = GetDiameter(thd[0], d), thd[1], "%6.4f "
    for klass in thd[3]:
        Class = int(klass)
        if d["-c"] is not None and d["-c"] != Class:
            continue
        T = asme.UnifiedThread(D, tpi, Class=Class)
        name = thd[0] + "-" + str(thd[1]) + " " + series
        if name[0] == "n":
            name = name[1:]
        # External thread
        allowance = T.Allowance()
        Dmax = T.Dmax()
        Dmin = T.Dmin()
        Emax = T.Emax()
        Emin = T.Emin()
        out("%-14s %dA " % (name, Class) + 4*fmt % (Dmax, Dmin, Emax, Emin), nl=0)
        out("  ", nl=0)
        # Internal thread
        dmax = T.dmax()
        dmin = T.dmin()
        emax = T.emax()
        emin = T.emin()
        out("%dB " % Class + 4*fmt % (dmin, dmax, emin, emax))

def main():
    args, d = ProcessCommandLine()
    diameter_inches = 0.0
    tpi = 0.0
    if len(args) == 1:
        PrintPitchProperties(args[0], d)
    else:
        if len(args) == 2:
            diameter_inches = GetDiameter(args[0], d)
            tpi = float(args[1])
            if d["-m"]:
                tpi = 25.4/tpi
        else:
            assert(len(args) == 3)
            # This is of the form 'i f tpi' where i is an integer and
            # f is the fraction
            if string.find(args[1], "/") == -1:
                Error("Second parameter must have '/' in it")
            numerator, denominator = map(float, string.split(args[1], "/"))
            diameter_inches = float(args[0]) + numerator/denominator
            tpi = float(args[2])
    if debug:
        out("diameter, in = %.4f" % diameter_inches)
        out("tpi          = %.2f" % tpi)
    PrintResults(diameter_inches, tpi, d)

main()
