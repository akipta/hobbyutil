'''
This module provides unit conversions.  Please see the u.pdf
documentation file that came in the package this script came in.
Here, we'll give an overview of the module's use.

    If this module is included in another package, you can get the
    u.zip package for the u.py module from
    http://code.google.com/p/hobbyutil.

The main function's you'll use are u() and to().  You can either use
the built-in set of SI and non-SI units or supply definitions of your
own.  If you supply your own definitions, you must call Initialize()
to initialize the internal data structures.

You endow a variable with a physical unit by a line such as

    velocity = 3.7*u("miles/hour")

The function u() returns a conversion factor that, when multiplied by
the indicated unit, results in a number that is equivalent to the same
dimensional quantity in base SI units.  Thus, the function call
u("miles/hour") returns the number 0.44704.  If you print the variable
velocity, it will have the value 1.654048; this is 3.7 miles per hour
expressed in meters per second.

When you want the variable velocity to contain the numerical value in
ft/minute, you can use the following equivalent methods:

    velocity /= u("ft/minute")      # Divide by a u() call
    to(velocity, "ft/minute")       # Use a convenience function

Numerous aliases are defined in the built-in set of SI units (and it's
trivial to define others).  Thus, you can use 

    feet, foot, ft
    min, minute, minutes

If you use the following process when developing code:
    
    * Define all physical variables' numerical values using the u()
      function, even the dimensionless ones.

    * Perform all intermediate calculations knowing that all your
      variables are in base SI units (or derived units in terms of
      them.

    * For output, use the to() or u() functions to convert the
      variables' numerical values to the units of choice.

you'll reduce the likelihood of making dimensional mistakes in your
code.

The ParseUnit() function is provided to help pick apart into the
number and unit an input string a user might type in at a prompt in a
program.

The unit 'm/s/s' is ambiguous in normal scientific usage and thus not
allowed by SI rules.  Since this module uses python's parser to
evaluate expressions, it means (m/s)/s to the parser, so is acceptable
to this module.

Dimensional checking
--------------------

    If the randomize keyword in the Initialize() call is True, then
    the base units are initialized with random numbers.  This is used
    to help track down a calculation containing a dimensional error.
    The idea of using random numbers to "orthogonalize" unit
    conversion factors to help find dimensional errors is due to
    Steven Byrnes (see his numericalunits package at
    http://pypi.python.org/pypi/numericalunits). 
'''

# Copyright (C) 2014 Don Peterson
# Contact:  gmail.com@someonesdad1

#
#

# This module is a derivative work of SteveByrnes' numericalunits.py
# module, so I've included his license and copyright.

# Copyright (C) 2012 Steven Byrnes
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import division, print_function
import sys, re, unittest
from random import Random
from math import pi 

__all__ = [
    "base_units",
    "unit_definitions_string",
    "prefixes",
    "units",
    "special",
    "SI_base_units",
    "SI_unit_definitions_string",
    "SI_prefixes",
    "Initialize",
    "u",
    "to",
    "fromto",
    "Dump",
    "ParseUnit",
    "CT",
]

#--------------------------------------------------------------------
# The following are the key containers for information for a defined
# set of units.  They will be defined by the Initialize() routine. 
#
# base_units is an iterable that returns the strings defining the
# base units.
base_units = None

# The following string contains valid python code that defines all the
# derived units in terms of the base units.  See the definition of
# SI_unit_definitions_string below for an example.
unit_definitions_string = None

# prefixes will be a dictionary that contains prefix multipliers.
# You'll probably want to use the default SI ones, but you can define
# your own set if you wish (see the unit tests for an example).
prefixes = None

# units will be a dictionary that contains all the unit definitions.  
units = None

# The special dictionary holds those unit strings that are python
# keywords and, thus, will cause a syntax error when eval() is called.
# An example is using 'in' for inch, as 'in' is a python keyword.
# This dictionary gives what the keyword should have substituted for
# it; in the 'in' case, 'inch' is the obvious substitution.
special = None

#--------------------------------------------------------------------
# This sequence defines the base unit names.  These are the standard
# SI base units except 'rad' and 'sr' have been added to make angles
# and solid angles have a dimension.  The 'nodim' unit is also present
# and can be used to represent a number with no defined dimension, yet
# you want to keep its identity.  You can create such numbers by
# multiplying a number by u("").

SI_base_units = set(("m", "kg", "s", "A", "cd", "mol", "K", "rad",
                     "sr", "nodim"))

# Define the remaining units in terms of the base units.  Note this
# string is valid python code.  It is executed in the Initialize()
# function's scope and the local variables are recovered to define the
# units and their conversion factors.  An advantage of doing things
# this way is that python's parser is used to evaluate the
# expressions.  The string is also readable and easy to edit to create
# new units.

SI_unit_definitions_string = '''
# The remaining definitions must define their units in terms of some
# combination of the base units.  However, note there is no checking
# that this in fact is done, so the burden is on you as the user to
# ensure things are consistent.  The lines in this string are executed
# as python code, so you can use expressions as needed.

# Note the numerical constants have decimal points in them.  This is
# done so that the same numerical results are gotten on python 2 and
# 3.  Because of this, I would expect this module would work on nearly
# any python version if you delete the unittest stuff on versions
# before 2.1.  If you're using python 2, I recommend you use the -Qnew
# command line option to ensure e.g. 1/2 is equal to 0.5, rather than
# zero.  Then, if you make a mistake and forget a decimal point
# following a numerical constant, the code will still give
# numerically-correct results.

# A number of these unit definitions came from the GNU units program's
# datafile.  

c = 299792458  # Speed of light in vacuum in m/s
one = 1.0

# The 'if' statements help to visually organize the definitions,
# making things a little easier to read.

if one:   # Angles and solid angles
    radian = radians = rad
    steradian = steradians = sr
    circle = turn = revolution = rev = 2.*pi*radian
    degree = degrees = deg = arcdeg = arcdegee = arcdegrees = circle/360.
    arcmin = arcdeg/60.
    arcsec = arcsecond = arcseconds = arcmin/60.
    rightangle = 90.*deg
    grad = gradian = gradians = rightangle/100.
    sphere = 4.*pi*steradian
    squaredegree = sd = (pi/180.)**2*steradian

if one:   # Lengths
    meter = metre = meters = metres = m
    inch = inches = ins = m/(1/0.0254)
    ft = foot = feet = 12.*inches
    micron = 1e-6*m
    mil = thou = inch/1000.
    yd = yard = 3.*feet
    mile = miles = mi = 5280.*feet
    ly = lightyear = 365.25*24*3600*c
    au = astronomical_unit = 149597870700.*m  # Defined to be exact
    earthradius = 6.37101e6*m
    moonradius  = 1.73710e6*m
    sunradius   = 6.96342e8*m

    # Less frequently-used units
    angstrom = ang = Angstrom = 1e-10*m
    nmi = nmile = nauticalmile = nauticalmiles = 1852.*m
    cable = nauticalmile/10.
    caliber = inch/100.
    chain = m/0.049709695379
    click = klick = clicks = klicks = 1000.*m
    fathom = 6.*feet
    rod = 5.5*yard
    furlong = 40.*rod
    hand = 4.*inches
    league = 3.*miles   # About 1 hour's walk
    link = chain/100.
    ls = lightsecond = c*m
    pace = 2.5*feet
    pc = parsec = 3.08567758149e+16*m
    point = pt = inch/72.27  # Other definition is inch/72
    standardgauge = 56.5*inches  # Railroad track width (4 ft 8.5 inches)

    # US coin dimensions from
    # http://www.usmint.gov/about_the_mint/?action=coin_specifications
    d_penny = 0.75*inches 
    d_nickel = 0.835*inches
    d_dime = 0.705*inches
    d_quarter = 0.955*inches
    d_half = 1.205*inches

if one:   # Areas
    acre = 4840.*9*ft**2
    are = 1e2*m**2
    hectare = 1e4*m**2
    letter = 8.5*11*inches**2   # US paper size
    legal = 8.5*14*inches**2    # US paper size
    ledger = 11.*17*inches**2   # US paper size
    a4paper = A4paper = 0.21*0.297*m**2   # ISO A4 paper
    barn = 1e-28*m**2
    dollarbill = 2.61*6.14*inches**2
    cmil = circmil = circularmil = pi*mil**2/4.
    mcm = MCM = 1e3*circmil
    eartharea = 4.*pi*earthradius**2
    moonarea  = 4.*pi*moonradius**2
    sunarea   = 4.*pi*sunradius**2

if one:   # Volumes
    L = l = liter = liters = litre = litres = 1e-3*m**3
    gal = gallon = gallons = 231.*inch**3
    cc = 1e-3*L
    cuft = cubicfoot = cubicfeet = ft**3
    cuin = cubicinch = cubicinches = inch**3
    acrefoot= acre*foot
    barrel = barrels = bbl = 42.*gallons
    bdft = boardfoot = boardfeet = 12.*12*1*inches**3
    bushel = bushels = 2150.42*inches**3
    cord = 4.*4*8*ft**3
    quart = quarts = qt = qts = one/4*gal
    pint = pt = pts = one/2.*quart
    floz = fluidounce = one/16.*pint
    cup = cups = dixiecup = 8.*floz
    fldram = floz/8.
    fifth = gallon/5.
    gill = pint/4.
    hogshead = 63.*gallons
    jigger = shot = 1.5*floz
    magnum = 1.5*liter
    minim = fldram/60.
    drop = (liter/1000.)/20.
    bloodunit = 450.*liter/1000.
    number1can   = 10.*floz
    number2can   = 19.*floz
    number2_5can = 28.*floz
    number3can   = 32.*cups
    number5can   = 56.*cups
    peck = bushel/4.
    popcan = 12.*floz
    bigbeercan = 16.*floz
    shippington = shipping_ton = 40.*ft**3
    tbs = tbl = tbls = tablespoon = cup/16.
    tsp = teaspoon = cup/48.
    saltspoon = tsp/4.
    winebottle = 3./4.*liter
    wineglass = 4.*floz

if one:   # Time
    second = seconds = sec = s
    minute = minutes = min = 60.*seconds
    hour = hours = hr = 3600.*seconds
    day = days = 24.*hours
    year = years = yr = 365.242198781*days  # Tropical year
    julianyear = 365.25*days                # Julian year
    month = months = mo = one/12.*year
    decade = decades = 10.*years
    century = centuries = 100.*years
    millenium = millenia = 1000.*years
    week = weeks = 7.*days
    fortnight = 2.*weeks
    lustrum = 5.*years
    jiffy = 0.01*s
    leapyear = 366*day

    # Astronomy (from GNU units 1.80 units.dat file; note the 2.02
    # version (current as of this writing) has more up-to-date
    # values).
    siderealday = 23.934469444*hour
    siderealyear = 365.256360417*day
    lunarmonth = 29.*day + 12.*hr + 44.*minutes + 2.8*s

    mercuryday = 58.6462*day
    venusday   = 243.01*day
    earthday   = siderealday
    marsday    = 1.02595675*day
    jupiterday = 0.41354*day
    saturnday  = 0.4375*day
    uranusday  = 0.65*day
    neptuneday = 0.768*day
    plutoday   = 6.3867*day

    mercuryyear = 0.2408467*julianyear
    venusyear   = 0.61519726*julianyear
    earthyear   = siderealyear
    marsyear    = 1.8808476*julianyear
    jupiteryear = 11.862615*julianyear
    saturnyear  = 29.447498*julianyear
    uranusyear  = 84.016846*julianyear
    neptuneyear = 164.79132*julianyear
    plutoyear   = 247.92065*julianyear

if one:   # Speed
    mph = mile_per_hour = mile/hour
    kph = km_per_hour = 1000.*m/hour
    fps = feet_per_sec = ft/s
    fpm = feet_per_minute = ft/minute
    knot = nauticalmile/hour
    mach = 331.46*m/s
    light = c*m/s

if one:   # Frequency
    Hz = hertz = one/s

if one:   # Mass
    g = gm = gram = grams = gramme = grammes = kg/1000.
    lb = lbm = pound = pounds = 0.45359237*kg
    slug = 14.593903*kg
    amu = Da = 1.660538921e-27*kg
    oz = ounce = ounces = lb/16.
    # Grains are commonly used by shooters and handloaders in the US
    grain = grains = gr = lb/7000.  # gr != grams!
    ton = 2000.*lb
    tonne = 1000.*kg
    cwt = hundredweight = nailkeg = 100.*pounds
    troypound = 5760.*grain
    troyounce = troypound/12.
    dwt = pennyweight = troyounce/20.
    egg = 50.*g
    galH2O = galh2o = galwater = gallonwater = 3.7855178*kg
    carat = ct = g/5.
    dram = ounce/16.
    key = kg
    stone = 14.*lbm

    # US coin masses from
    # http://www.usmint.gov/about_the_mint/?action=coin_specifications
    m_penny   = 2.5*g
    m_nickel  = 5.*g
    m_dime    = 2.268*g
    m_quarter = 5.670*g
    m_half    = 11.340*g

    # Astronomy (from GNU units 1.80 units.dat file; the 2.02 version
    # has more up-to-date values).
    sunmass     = 1.9891e30*kg
    mercurymass = 0.33022e24*kg
    venusmass   = 4.8690e24*kg
    earthmass   = 5.9742e24*kg
    marsmass    = 0.64191e24*kg
    jupitermass = 1898.8e24*kg
    saturnmass  = 568.5e24*kg
    uranusmass  = 86.625e24*kg
    neptunemass = 102.78e24*kg
    plutomass   = 0.015e24*kg

if one:   # Energy
    J = joule = kg*m**2/s**2
    erg = 1e-7*J
    eV = 1.602176565e-19*J
    btu = BTU = 1055.056*J
    # The calorie as a unit should be taken out and shot because of
    # the ridiculous number of similar definitions.  I've chosen to
    # use the IT_calorie (International Table calorie) in order to
    # agree with the GNU units program's output.
    cal = calorie = 4.1868*J
    CAL = Calorie = kcal = 1000.*cal    # Food calorie capitalized
    Wh = Whr = watthour = 3600.*J
    kWh = kWhr = 1000.*Whr
    therm = 1.054804e8*J

if one:   # Moles, molarity
    mole = mol
    NA = 6.02214129e23          # Avogadro's number
    M = molar = mol/L           # Molarity

if one:   # Force
    # The acceleration of gravity is used to turn a mass unit into a 
    # weight (force) units
    g0 = gravity = force = 9.80665*m/s**2
    gf = g*gravity
    kgf = kg*gravity
    N = newton = kg*m/s**2
    dyne = dyn = 1e-5*N
    lbf = poundf = poundforce = 4.4482216152605*N
    kip = 1000.*lbf
    slugf = slug*force
    tonf = ton*force

if one:   # Pressure
    Pa = pascal = N/m**2
    atm = 101325.*Pa
    bar = 1e5*Pa
    torr = atm/760.
    psi = psia = lbf/inch**2
    psf = lbf/foot**2
    ksi = kip/inch**2
    # Water and mercury are used for pressures
    water = g*force/(m/100.)**3
    fth2o = ft*water
    inh2o = inch*water
    mh2o = m*water
    mmh2o = m/1000.*water
    # Note:  in the following expression, the exponentiation of
    # parentheses is allowed because it's being evaluated by the
    # python parser, NOT by the u() function.
    Hg = hg = 13.5951*g*force/(m/100.)**3
    ftHg = fthg = ft*Hg
    inHg = inhg = inch*Hg
    mHg = mhg = m*Hg
    mmHg = mmhg = m/1000.*Hg

if one:   # Fluid flow
    gph = gallon/hour
    gpm = gallon/minute
    cfh = ft**3/hr  # 7.8657907e-06*m**3/s
    cfm = ft**3/min # 0.00047194744*m**3/s
    cfs = ft**3/s   # 0.028316847*m**3/s
    lpm = liter/minute
    lph = liter/hour
    lps = liter/s
    minersinch = 1.2*ft**2/minute       # Location-dependent!
    # Gas flow (note these have the dimensions of power)
    sccs = atm*cc/s
    sccm = atm*cc/minute
    scfh = atm*cfh
    scfm = atm*cfm
    slpm = atm*lpm
    slph = atm*lph

if one:   # Power
    W = watt = J/s
    hp = horsepower = 550.*ft*lbm*force/s
    tonref = tonrefrigeration = ton*144.*btu/(lbm*day)

if one:   # Temperature
    degC = kelvin = K
    degF = degR = 5./9.*K

if one:   # Current
    amp = ampere = A

if one:   # Charge
    C = coulomb = coul = A/s
    Ah = Ahr = amphour = 3600.*C

if one:   # Voltage
    V = volt = J/C

if one:   # Resistance
    ohm = O = V/A

if one:   # Conductivity
    S = siemens = mho = one/ohm

if one:   # Magnetism
    T = tesla = V*s/m**2
    G = gauss = T/10000.
    Oe = oersted = 1000./(4*pi)*A/m
    Wb = weber = J/A

if one:   # Capacitance
    F = farad = C/V

if one:   # Inductance
    H = henry = m**2*kg/C**2

if one:   # Convenience constants (missing many!)
    mu0 = 4*pi*1e-7*N/A**2      # Permeability of vacuum
    eps0 = one/(mu0*c)          # Permittivity of vacuum
    e = 1.602176565e-19*C       # Elementary charge 
    m_e = electronmass = 5.485799110e-4*amu     # Electron rest mass
    m_p = protonmass   = 1.00727646688*amu      # Proton rest mass
    m_n = neutronmass  = 1.00866491578*amu      # Neutron rest mass
    R = 8.314472*J/(mol*K)      # Molar gas constant
    kB = R/NA                   # Boltzmann's constant
    G = 6.6742e-11*m**3/(kg*s**2)  # Gravitational constant
    sigma_SB = 5.670400e-8*W/(m**2*K**4)  # Stefan-Boltzmann constant
    faraday = NA*e*mol          # Unit of charge
    h = 6.62606876e-34*J*s      # Planck's constant

    # The following constant is the energy density at 1 astronomical
    # unit on a radius from the sun and in vacuum.  If you want to
    # approximate the insolation at the Earth's surface, you can use 
    # 1 kW per square meter and multiply it by the cosine of the angle
    # that the sun is off the normal to the ground plane.  This number
    # will be lowered by haze, clouds, etc.  A daily average can be
    # approximated by 1/4 kW/m2.
    solar_const = 1361.*W/m**2  # Sun's energy density at 1 au 

    air_density = 1.293*kg/m**3 # 20 degC and 1 atm
    speed_sound = 343.2*m/s     # 20 degC, 1 atm, dry air

    # Densities
    d_water = g/(m/100.)**3
    d_Au = 19.3*d_water
    d_Co = 8.9*d_water
    d_Cr = 7.2*d_water
    d_Cu = 8.96*d_water
    d_Fe = 7.87*d_water
    d_Fe_cast = 7.25*d_water
    d_Hg = 13.55*d_water
    d_Ir = 22.4*d_water
    d_Mo = 10.2*d_water
    d_Na = 0.97*d_water
    d_Ni = 8.9*d_water
    d_Pb = 11.3*d_water
    d_Pt = 21.45*d_water
    d_Si = 2.33*d_water
    d_Ta = 16.6*d_water
    d_Ti = 4.5*d_water
    d_W = 19.3*d_water
    d_Al = 2.77*d_water
    d_brass = 8.3*d_water
    d_bronze = 8.8*d_water
    d_gas = 0.65*d_water
    d_gasoline = d_gas
    d_silver = 10.5*d_water
    d_solder = 8.4*d_water
    d_sst = 8.02*d_water
    d_steel = 7.86*d_water

if one:   # Selected cgs units (from GNU units.dat file)
    abamp = abampere = biot = 10.*A
    abcoulomb = abcoul = abamp*s
    abvolt = dyne*(m/100.)/(abamp*s)
    abfarad = abampere*s/abvolt
    abhenry = abvolt*s/abamp
    abohm = abvolt/abamp
    abmho = one/abohm
    maxwell = Mx = abvolt*s
    gilbert = gauss*(m/100.)/mu0
    Gi = gilbert
    unitpole = 4*pi*maxwell
    emu = erg/gauss  # Measure of magnetic moment density

if one:  # Miscellaneous conversion factors
    candela = cd
    diopter = one/m
    planck = J*s
    mired = 1e6/K
    hbar = h/(2.*pi)
    poise = P = 100.*g/(m*s)    # Dynamic viscosity
    stokes = m**2/(1e4*s)       # Kinematic viscosity
    candle = 1.02*cd
    lumen = lm = cd*sr
    lux = lx = lm/m**2
    footcandle = lumen/ft**2
    lambert = cd/(pi*m**2/100.)
    footlambert = cd/(pi*ft**2)
    rpm = rev/minute
    rps = rev/second
    
if one:
    c0 = c*m/s  # Attach the proper units
    del c, one  # Delete our temporary constants

# The following dictionary is used to contain unit definitions that
# conflict with python keywords.
special = {
    "in" : inch,
}
'''

# The SI_prefixes dictionary contains the SI prefixes as keys; the
# values are the corresponding scaling factor as strings (these will
# be processed by eval() later).  You can change these prefixes to
# whatever strings you like as long as they don't contain digits.

SI_prefixes = {
    "y"  : "10**-24",
    "z"  : "10**-21",
    "a"  : "10**-18",
    "f"  : "10**-15",
    "p"  : "10**-12",
    "n"  : "10**-9",
    "u"  : "10**-6",
    "m"  : "10**-3",
    "c"  : "10**-2",
    "d"  : "10**-1",
    "da" : "10**1",
    "h"  : "10**2",
    "k"  : "10**3",
    "M"  : "10**6",
    "G"  : "10**9",
    "T"  : "10**12",
    "P"  : "10**15",
    "E"  : "10**18",
    "Z"  : "10**21",
    "Y"  : "10**24",

    "yocto"  : "10**-24",
    "zepto"  : "10**-21",
    "atto"   : "10**-18",
    "femto"  : "10**-15",
    "pico"   : "10**-12",
    "nano"   : "10**-9",
    "micro"  : "10**-6",
    "milli"  : "10**-3",
    "centi"  : "10**-2",
    "deci"   : "10**-1",
    "deca"   : "10**1",
    "deka"   : "10**1",
    "hecto"  : "10**2",
    "kilo"   : "10**3",
    "mega"   : "10**6",
    "giga"   : "10**9",
    "tera"   : "10**12",
    "peta"   : "10**15",
    "eta"    : "10**18",
    "zetta"  : "10**21",
    "yotta"  : "10**24",

    "yocto-" : "10**-24",
    "zepto-" : "10**-21",
    "atto-"  : "10**-18",
    "femto-" : "10**-15",
    "pico-"  : "10**-12",
    "nano-"  : "10**-9",
    "micro-" : "10**-6",
    "milli-" : "10**-3",
    "centi-" : "10**-2",
    "deci-"  : "10**-1",
    "deca-"  : "10**1",
    "deka-"  : "10**1",
    "hecto-" : "10**2",
    "kilo-"  : "10**3",
    "mega-"  : "10**6",
    "giga-"  : "10**9",
    "tera-"  : "10**12",
    "peta-"  : "10**15",
    "eta-"   : "10**18",
    "zetta-" : "10**21",
    "yotta-" : "10**24",
}

# Regular expression that will match an integer or floating point
# number in its string represenation.
_num_unit = re.compile(r'''
        (?x)                            # Allow verbosity
        ^                               # Must match at beginning
        (                               # Group
            [+-]?                       # Optional sign
            \.\d+                       # Number like .345
            ([eE][+-]?\d+)?|            # Optional exponent
        # or
            [+-]?                       # Optional sign
            \d+\.?\d*                   # Number:  2.345
            ([eE][+-]?\d+)?             # Optional exponent
        )                               # End group
''')

# Regular expression objects for manipulating unit strings
_spaces = re.compile(" +")
_exp    = re.compile(r"(\*\*|\^)")
_tokens = re.compile(r"(\*|/|\(|\))")
_digits = re.compile(r"(\d+$)")

def Initialize(bu=None, uds=None, pr=None, randomize=False):
    '''Create the unit hierarchy in the global units dictionary.  
 
    bu is a sequence of strings defining the base units of the unit
    system; all other units will be defined in terms of these (and
    they will all have numerical values of 1 unless randomize is
    True).  
    
    uds is a string containing the remaining unit definitions in terms
    of the base units (see the SI_unit_definitions_string global
    variable above for an example of the needed form).  
    
    pr is a dictionary of prefixes; the first element is the prefix
    string and the value is a string representing the numerical value
    of the prefix; see the SI_prefixes global variable above as an
    example.
    
    If you don't supply bu, uds, and pr, they are by default set to
    SI_base_units, SI_unit_definitions_string, and SI_prefixes,
    respectively.
 
    If randomize is False, no randomization takes place and the base
    units are defined to be unity.  Otherwise, the random number
    generator is seeded by the clock and the base units get random
    values, none of which are equal.
 
    How to use this functionality:  
 
        To perform a dimensional check while developing code, set
        randomize to True and perform your complete calculations
        twice, with a call to Initialize() with randomize=True both
        times.  Compare the results; if they differ, then there's
        almost certainly a dimensional error somewhere.  Once your
        code is debugged, you can leave randomize False and the unit
        values will be as you expect.
    '''
    global base_units, unit_definitions_string, prefixes, units, special
    # Set up the needed data structures
    base_units = set(bu) if bu is not None else SI_base_units
    unit_definitions_string = (uds if uds is not None else 
        SI_unit_definitions_string)
    prefixes   = pr if pr is not None else SI_prefixes
    if not base_units:
        raise ValueError("bu argument container has no unit strings")
    if not unit_definitions_string.strip():
        raise ValueError("uds argument string is essentially empty")
    if not prefixes:
        raise ValueError("pr argument dictionary is empty")
    # Bring the base units into our local namespace.
    if randomize:
        numbers = set()  # Used to ensure no duplicate random numbers
        # Creating an instance of a Random object here guarantees this
        # code is thread-safe.
        r = Random()
        r.seed()    # Sets state from the current system time
        udrn = lambda r:  10**r.uniform(-1, 1)
        for i in base_units:
            num = udrn(r)
            while num in numbers:
                num = udrn(r)
            numbers.add(num)
            exec("%s = %.15g" % (i, num))   # Define a local variable
    else:
        for i in base_units:
            exec("%s = 1.0" % i)            # Define a local variable
    # We'll delete non-needed variables to keep our namespace clean
    del i, randomize
    # Execute the lines in the datafile.
    exec(compile(unit_definitions_string, "", "exec"))
    # Get the variables that have been defined
    d = locals()
    # Create any special variables
    if d["special"]:
        special = {}
    for i in d["special"]:
        if i in d:
            raise ValueError("'%s' is already defined" % i)
        d[i] = d["special"][i]
        special[i] = str(d["special"][i])
    # Delete the variables we don't want to return
    for i in ("bu", "uds", "pr", "special"):
        if i in d:
            del d[i]
        if i in d:
            raise RuntimeError("Bug")
    # Now d contains only those keys that are the base and derived
    # unit strings we want to use.
    units = d

def _GetPrefix(s):
    '''Using the strings in the prefixes dictionary, separate the
    string s into an optional prefix string p and the unit string us;
    return the tuple (prefixes[p] + "*", us).  Raise an exception if
    the unit string us is not in the units _dictionary.
    '''
    # Method:  find the set of integers representing the lengths of
    # the different prefixes.  Extract each front-anchored prefix of
    # this size from the string s and determine if the candidate
    # prefix is in the prefixes dictionary.
    ve = "'%s' is an unrecognized unit"
    # It's important to check the longest prefixes first; otherwise,
    # you'll find the 'y' in 'yoctom' and get an error because 'octom'
    # is not a recognized unit.
    for size in reversed(sorted(list(set([len(i) for i in prefixes])))):
        if size > len(s) - 1:
            continue    # Must leave at least 1 character for unit
        prefix_candidate = s[:size]
        if prefix_candidate in prefixes:
            us = s[size:]
            if us not in units and us not in "()":
                raise ValueError(ve % us)
            return (prefixes[prefix_candidate] + "*", us)
    raise ValueError(ve % s)

def _process(token):
    '''token is a string that represents a unit with an optional SI
    prefix and an optional trailing integer suffix (this integer must
    be greater than zero).  Pick the string apart and reassemble it
    into a valid python expression syntactically representing the same
    numerical conversion factor.  Return it as a string suitable for
    eval().
    '''
    if not token or token in list("*/()"):
        return token
    # See if it's a string representation of a float
    try:
        float(token)
        return token
    except Exception:
        pass
    s, exponent = token[:], "1"
    # Remove exponent if present
    mo = _digits.search(s)
    if mo is not None:
        exponent = str(int(s[mo.start() : mo.end()]))
        s = s[:mo.start()]
    prefix = ""
    if s not in units:
        prefix, s = _GetPrefix(s)
    # The SI kg unit is not allowed to have a prefix.
    if s == "kg" and prefix:
        raise ValueError("'%s':  kg is not allowed to have a prefix" % token)
    # We also have to handle the special cases where the unit is a
    # python keyword because the returned string will be evaluated as
    # an expression.
    if s in special:
        s = special[s]  # Translate to the non-keyword value
    if exponent == "1":
        return ''.join([prefix, s])
    # The parentheses are used in the following because the SI prefix
    # has higher operator precedence than exponentiation.
    return ''.join(["(", prefix, s, ")**", exponent])

def u(expr):
    '''Convenience function to convert an arbitrary expression of unit
    strings expr to a numerical conversion factor that converts to the
    equivalent base units.
 
    Examples that return the same value:
        force = u("kg*mm/s2")
        force = u("kg mm/s2")
        force = u("kg*mm/s**2")
        force = u("kg*mm/s^2")
 
    Assuming that Initialize() was run before these lines, the
    variable force will contain 0.001, the value of 1 millinewton
    expressed in SI units.
 
    expr has the following syntax rules:
 
      * One of the defined prefixes are allowed (each base unit can
        only have one prefix).
 
      * Multiplication is indicated either by '*' or one or more space
        characters.
 
      * Division is indicated by the '/' character.  
      
      * An expression like 'kg/mm/s' is allowed and is equal to
        '(kg/mm)/s', which is 'normal' left-right associativity for
        C-like programming languages.
 
      * Exponentiation of the unit is indicated by a trailing integer
        that is greater than zero.  You can optionally use '**' or
        '^' between the unit and integer.
 
      * Parentheses can change evaluation order, such as 'm/(s/s)',
        which is equivalent to 'm'.
 
      * Parenthetical expressions cannot be raised to a power.  Thus,
        'm/(s/s)**2' will result in an exception.
 
    The exponent of a unit must be a positive integer greater than
    zero.
    ''' 
    # Note:  a more general form of this function would be recursive to
    # process strings like '(m/s)**2'.  I chose not to implement such
    # functionality in the first version.  Maybe it will be in a future
    # version.
    if units is None:
        raise RuntimeError("Initialize() hasn't been called yet")
    s = expr.strip()
    if not s:  
        # A string of only whitespace means the nodim "unit".  If it
        # doesn't exist in the units dictionary, then we just return
        # numerical unity.
        return units.get("nodim", 1.0)
    # Use python's expression parser to evaluate the incoming string.
    s = _spaces.sub("*", s)     # Multiple spaces --> '*'
    s = _exp.sub("", s)         # '**' and '^' to empty strings
    f = _tokens.split(s)        # Split on multiplies and divides
    f = [_process(token.strip()) for token in f]
    return eval(''.join(f), None, units)

def to(x, s):
    '''Convenience function to convert a numerical value x to the unit
    expressed in the string s.
 
    Example:  
        x = 22*u("m")       # x is 22 meters
        xmm = to(x, "km")   # xmm is 0.022 kilometers
    '''
    return x/u(s)

def fromto(x, s1, s2):
    '''Convenience function to convert a numerical value x in units s1 
    to the unit expressed in the string s2.
 
    Example:  
        x = 22*u("m")       # x is 22 meters
        xmm = to(x, "km")   # xmm is 0.022 kilometers
    '''
    return x*u(s1)/u(s2)

def Dump(stream=None):
    '''Dump the contents of the units dictionary to the indicated
    stream or, if no stream, return a list of strings.
    '''
    try:
        s, m = [], max([len(i) for i in units.keys()]) + 2
    except AttributeError:
        print("Did you forget to run Initialize()?")
        raise
    for k in units.keys():
        s.append((k, units[k]))
    s = sorted(s, cmp=lambda x,y: cmp(x.lower(), y.lower()), 
               key=lambda x: x[0])
    if stream is not None:
        for name, value in s:
            print("%-*s %s" % (m, name, value))
    else:
        return s

def ParseUnit(s, allow_expr=False):
    '''Separate a number string followed by a unit string and return
    them in a tuple.  None will be returned if allow_expr is False and
    no number and unit could be found.
    
    The string s must be an integer or floating point number, followed
    by an optional string representing a unit.  The leading number is
    removed, leaving the unit.  These are returned as (number, unit),
    where both are strings (whitespace is stripped).  If there's no
    number, then None is returned instead of a tuple.  There doesn't
    need to be whitespace between the number and the unit.
 
    The allow_expr keyword is used to facilitate a slightly different
    use case.  Here, the string s must be of the form "s u" where s is
    a python expression and u is a string designating a unit; the two
    are separated by one or more spaces.  The string u can be empty
    and the one or more space characters omitted, in which case the
    returned tuple will be (s, "").  This function doesn't evaluate
    the expression.
 
    Examples:  
        ParseUnit("47.3e-88m/s") and ParseUnit("47.3e-88 m/s") both
        return ("47.3e-88", "m/s").
 
        ParseUnit("47.3e-88*1.23 m/s") returns ("47.3e-88*1.23", "m/s").
 
        ParseUnit("4") returns ("4", "").
    '''
    s = s.strip()
    if allow_expr:
        f = s.split(" ")
        if len(f) not in (1, 2):
            raise ValueError("s is not a proper string")
        if len(f) == 1:
            return (f[0], "")
        return tuple(f)
    else:
        mo = _num_unit.search(s)
        if mo:
            return (s[:mo.end()].rstrip(), s[mo.end():].lstrip())
        return None

def CT(T, T_from, T_to="K"):
    '''Convert temperature T in the unit indicated by the string
    T_from to the unit indicated by the string T_to.  The allowed
    strings for temperature are:
 
        K, k    Absolute temperature in K
        C, c    Degrees Celsius
        F, f    Degrees Fahrenheit
        R, r    Degrees Rankine
    '''
    allowed, T0 = "kcfr", 273.15
    t_from, t_to, Tr = T_from.lower(), T_to.lower(), 9/5.*T0 - 32
    if len(t_from) != 1 or t_from not in allowed:
        raise ValueError("'%s' is a bad temperature unit" % T_from)
    if len(t_to) != 1 or t_to not in allowed:
        raise ValueError("'%s' is a bad temperature unit" % T_to)
    if t_from in "kr" and T < 0:
        raise ValueError("Absolute temperature must be >= 0")
    if t_from == "c" and T < -T0:
        raise ValueError("Temperature in deg C must be >= 273.15")
    if t_from == "r" and T < -Tr:
        raise ValueError("Temperature in deg F must be >= 491.67")
    f = {
        "kk" : lambda T: T,
        "kc" : lambda T: T - T0,
        "kf" : lambda T: 9./5*T - Tr,
        "kr" : lambda T: 9./5*T,
 
        "ck" : lambda T: T + T0,
        "cc" : lambda T: T,
        "cf" : lambda T: 9./5*T + 32,
        "cr" : lambda T: (T + T0)*9/5.,
 
        "fk" : lambda T: (T + Tr)*5/9.,
        "fc" : lambda T: (T - 32)*5/9.,
        "ff" : lambda T: T,
        "fr" : lambda T: T + Tr,
 
        "rk" : lambda T: 5/9*T,
        "rc" : lambda T: (T - Tr - 32)*5/9,
        "rf" : lambda T: T - Tr,
        "rr" : lambda T: T,
    }
    return f[t_from + t_to](T)

# Run Initialize to use the default set of units.  If you define your
# own units structure, you'll need to run Initialize again.
Initialize()

