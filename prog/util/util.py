'''Miscellaneous routines in python:

AlmostEqual           Returns True when two floats are nearly equal
AWG                   Returns wire diameter in inches for AWG gauge number
Batch                 Generate to pick n items at a time from a sequence
Binary                Converts an integer to a binary string (see int2bin)
Cfg                   Execute a sequence of text lines for config use
CommonPrefix          Find common prefix in a list of strings
CommonSuffix          Find common suffix in a list of strings
ConvertToNumber       Convert a string to a number
CountBits             Return the number of bits set in an integer
cw2mc                 Convert cap-words naming to mixed-case
cw2us                 Convert cap-words naming to underscore
Debug                 A class that helps with debugging
DecimalToBase         Convert a decimal integer to a base between 2 and 36
Dispatch              Class to aid polymorphism
eng                   Convenience function for engineering format
Engineering           Represent a number in engineering notation
FindDiff              Find the index where two strings first differ.
FindSubstring         Return tuple of indexes where substr is found in string
Flatten               Flattens nested sequences to a sequence of scalars
GetChoice             Return a unique string if possible from a set of choices
GetString             Return a string from a set by prompting the user
GroupByN              Group items from a sequence by n items at a time
grouper               Function to group data
HeatIndex             Effect of temperature and humidity
hyphen_range          Returns list of integers specified as ranges
IdealGas              Calculate ideal gas P, v, T (v is specific volume)
int2base              Convert an integer to a specified base
int2bin               Converts int to specified number of binary digits
InterpretFraction     Interprets string as proper or improper fraction
IsBinaryFile          Heuristic to see if a file is a binary file
IsCygwinSymlink       Returns True if a file is a cygwin symlink
IsIterable            Determines if you can iterate over an object
IsTextFile            Heuristic to see if a file is a text file
Keep                  Keep only specified characters in a string
KeepFilter            Return a function that keeps specified characters
KeepOnlyLetters       Change everything in a string not a letter to spaces
ListInColumns         Returns a list of strings listing a sequence in columns
MostCommon            Return sorted list of most common items & counts
mc2cw                 Convert mixed-case naming to cap-words
mc2us                 Convert mixed-case naming to underscore
NiceRound             Rounds a floating pt to nearest 1, 2, or 5.
partition             Generate a list of the partitions of an iterable
Percentile            Returns the percentile of a sorted sequence
ProperFraction        Converts a Fraction object to proper form
randq                 Simple, fast random number generator
randr                 Random numbers on [0,1) using randq
ReadVariables         Read variables from a file
Remove                Remove a specified set of characters from a string
RemoveFilter          Return a function that removes specified characters
RemoveIndent          Remove leading spaces from a multi-line string
SignificantFigures    Rounds to specified num of sig figures (returns float)
SignificantFiguresS   Rounds to specified num of sig figures (returns string)
SignMantissaExponent  Returns tuple of sign, mantissa, exponent
signum                Signum function
Singleton             Mix-in class to create the singleton pattern
soundex               Returns a string characterizing a word's sound
SoundSimilar          Returns True if two words sound similar
SpeedOfSound          Calculate the speed of sound as a function of temperature
SpellCheck            Checks that a list of words is in a dictionary
SplitOnNewlines       Splits a string on newlines for PC, Mac, Unix.
StringSplit           Split a string on fixed fields or cut at columns
TempConvert           Convert a temperature
Time                  Returns a string giving local time and date
TranslateSymlink      Returns what a cygwin symlink is pointing to
UniqueItems           Return the unique items in a sequence
us2cw                 Convert underscore naming to cap-words naming
us2mc                 Convert underscore naming to mixed-case
US_states             Dictionary of states indexed by e.g. "ID"
WindChillInDegF       Calculate wind chill given OAT & wind speed
WireGauge             Get diameter or number of wire gauge sizes

One of the design goals for this module is that it should be usable
with either python 2.7.6 or 3.4.0, the two versions I currently have
on my system.
'''

# Copyright (C) 2014 Don Peterson
# Contact:  gmail.com@someonesdad1

#
#

from __future__ import print_function, division
import sys
from collections import deque, Iterable, defaultdict
from decimal import Decimal
from fractions import Fraction
from heapq import nlargest
# These iterators are in python 2 and 3
from itertools import chain, combinations, islice, groupby 
from odict import odict
from operator import itemgetter
from out import out
from random import randint, seed
from sig import sig
from string import ascii_letters, digits, punctuation
import cmath
import math
import os
import re
import struct
import tempfile
import unittest

from pdb import set_trace as xx
import debug
if 0:
    debug.SetDebugger()

py3 = True if sys.version_info[0] > 2 else False

if py3:
    Int = (int,)
    String = (str,)
else:
    Int = (int, long)
    String = (str, unicode)
nl = "\n"

# Note:  this choice of a small floating point number may be
# wrong on a system that doesn't use IEEE floating point numbers.
eps = 1e-15

#----------------------------------------------------------------------
# StartCoverage (for checking test coverage)

def KeepOnlyLetters(s, underscore=False):
    '''Replace all non-word characters with spaces.  If underscore is
    True, keep underscores too (e.g., typical for programming language
    identifiers).
    '''
    allowed = ascii_letters + "_" if underscore else ascii_letters
    c = [chr(i) for i in range(256)]
    t = ''.join([i if i in allowed else " " for i in c])
    return s.translate(t)

def StringSplit(fields, string, remainder=True, one_based=False, strict=True):
    '''Pick out the specified fields of the string and return them as
    a tuple of strings.  fields can be either a format string or a
    list/tuple of numbers. 
 
    If one_based is True, then the field numbering is 1-based.  If
    strict is True, then the indicated number of fields must be
    returned or a ValueError exception will be raised.
 
    fields is a format string
        A format string is used to get particular columns of the
        string.  For example, the format string "5s 3x 8s 8s" means to
        pick out the first five characters of the string, skip three
        spaces, get the next 8 characters, then the next 8 characters.
        If remainder is False, this is all that's returned; if
        remainder is True, then whatever is left over will also be
        returned.  Thus, if remainder is False, you'll have a 3-tuple
        of strings returned; if True, a 4-tuple.
 
    fields is a sequence of numbers
        The numbers specify cutting the string at the indicated
        columns.  The numbering can be either 0-based (default) or
        1-based.  Example:  for the input string "hello there", using
            "hello there"
             01234567890
        the fields of [3, 7] will return the tuple of strings 
            ("hel", "lo t", "here").
 
    Derived from code by Raymond Hettinger at 
    From http://code.activestate.com/recipes/65224-accessing-substrings/
    Downloaded Sun 27 Jul 2014 07:52:44 AM
    '''
    if isinstance(fields, String):
        left_over = len(string) - struct.calcsize(fields)
        if left_over < 0:
            raise ValueError("string is shorter than requested format")
        format = "%s %ds" % (fields, left_over)
        result = list(struct.unpack(format, string))
        return result if remainder else result[:-1]
    else:
        pieces = [string[i:j] for i, j in zip([0] + fields, fields) ]
        if remainder:
            pieces.append(string[fields[-1]:])
        num_expected = len(fields) + 1
        if num_expected != len(pieces) and strict:
            raise ValueError("Expected %d pieces; got %d" % (num_expected, 
                             len(pieces)))
        return pieces

def Percentile(seq, fraction):
    '''Return the indicated fraction of a sequence seq of sorted
    values.  fraction must be in [0, 1].
    '''
    # Adapted from
    # http://code.activestate.com/recipes/
    # 511478-finding-the-percentile-of-the-values/
    if not seq:
        return None
    if not (0 <= fraction <= 1):
        raise ValueError("fraction must be in [0, 1]")
    k = (len(seq) - 1)*fraction
    f, c = math.floor(k), math.ceil(k)
    if f == c:
        return seq[int(k)]
    return (seq[int(f)]*(c-k) + seq[int(c)]*(k-f))

def MostCommon(iterable, n=None):
    '''Return a sorted list of the most common to least common elements and
    their counts.  If n is specified, return only the n most common elements.
         
    From http://code.activestate.com/recipes/347615
    downloaded Fri 25 Jul 2014 08:28:22 PM.
    '''
    bag = {}
    for elem in iterable:
        bag[elem] = bag.get(elem, 0) + 1
    if n is None:
        return sorted(bag.items(), key=itemgetter(1), reverse=True)
    it = enumerate(bag.items())
    nl = nlargest(n, ((cnt, i, elem) for (i, (elem, cnt)) in it))
    return [(elem, cnt) for cnt, i, elem in nl]

def cw2us(x):
    '''Convert cap-words naming to underscore naming.
    "Python Cookbook", pg 91.
    '''
    return re.sub(r"(?<=[a-z])[A-Z]|(?<!^)[A-Z](?=[a-z])", 
                  r"_\g<0>", x).lower()

def cw2mc(x):
    '''Convert cap-words naming to mixed-case naming.
    "Python Cookbook", pg 91.  Note book example is wrong.
    '''
    return x[0].lower() + x[1:]

def us2mc(x):
    '''Convert underscore naming to mixed-case.
    "Python Cookbook", pg 91.
    '''
    return re.sub(r"_([a-z])", lambda m: (m.group(1).upper()), x)

def us2cw(x):
    '''Convert underscore naming to cap-words naming.
    "Python Cookbook", pg 91.
    '''
    s = us2mc(x)
    return s[0].upper() + s[1:]

def mc2us(x):
    '''Convert mixed-case naming to underscore naming.
    "Python Cookbook", pg 91.
    '''
    return cw2us(x)

def mc2cw(x):
    '''Convert mixed-case naming to cap-words naming.
    "Python Cookbook", pg 91.  Note book example is wrong.
    '''
    return x[0].upper() + x[1:]

class Singleton(object):
    '''Mix-in class to make an object a singleton.  From 'Python in a
    Nutshell', p 84
    '''
    _singletons = {}
    def __new__(cls, *args, **kw):
        if cls not in cls._singletons:
            cls._singletons[cls] = object.__new__(cls)
        return cls._singletons[cls]

def signum(x, ret_type=int):
    '''Return a number representing the sign of x.
    '''
    if x < 0:
        return ret_type(-1)
    elif x > 0:
        return ret_type(1)
    return ret_type(0)

def InterpretFraction(s):
    '''Interprets the string s as a fraction.  The following are
    equivalent forms:  '5/4', '1 1/4', '1-1/4', or '1+1/4'.  The
    fractional part in a proper fraction can be improper:  thus, 
    '1 5/4' is returned as Fraction(9, 4).
    '''
    if "/" not in s:
        raise ValueError("'%s' must contain '/'" % s)
    t = s.strip()
    # First, try to convert the string to a Fraction object
    try:
        return Fraction(t)
    except ValueError:
        pass
    # Assume it's of the form 'i[ +-]n/d' where i, n, d are
    # integers.
    msg = "'%s' is not of the correct form" % s
    neg = True if t[0] == "-" else False
    fields = t.replace("+", " ").replace("-", " ").strip().split()
    if len(fields) != 2:
        raise ValueError(msg)
    try:
        ip = abs(int(fields[0]))
        fp = abs(Fraction(fields[1]))
        return -(ip + fp) if neg else ip + fp
    except ValueError:
        raise ValueError(msg)

def ProperFraction(fraction, separator=" "):
    '''Return the Fraction object fraction in a proper fraction string
    form.
 
    Example:  Fraction(-5, 4) returns '-1 1/4'.
    '''
    if not isinstance(fraction, Fraction):
        raise ValueError("frac must be a Fraction object")
    sgn = "-" if fraction < 0 else ""
    n, d = abs(fraction.numerator), abs(fraction.denominator)
    ip, numerator = divmod(n, d)
    return "%s%d%s%d/%d" % (sgn, ip, separator, numerator, d)


def RemoveIndent(s, numspaces=4):
    '''Given a multi-line string s, remove the indicated number of
    spaces from the beginning each line.  If that number of space
    characters aren't present, then leave the line alone.
    '''
    if numspaces < 0:
        raise ValueError("numspaces must be >= 0")
    lines = s.split(nl)
    for i, line in enumerate(lines):
        if line.startswith(" "*numspaces):
            lines[i] = lines[i][numspaces:]
    return nl.join(lines)

def Batch(iterable, size):
    '''Generator that gives you batches from an iterable in manageable
    sizes.  Slightly adapted from Raymond Hettinger's entry in the
    comments to
    http://code.activestate.com/recipes/303279-getting-items-in-batches/
 
    Example:
        for n in (3, 4, 5, 6):
            s = tuple(tuple(i) for i in Batch(range(n), 3))
            print(s)
    gives
        ((0, 1, 2),)
        ((0, 1, 2), (3,))
        ((0, 1, 2), (3, 4))
        ((0, 1, 2), (3, 4, 5))

    Another way of doing this is with slicing (but you'll need to have
    the whole iterable in memory to do this):
        def Pick(iterable, size):
            i = 0
            while True:
                s = iterable[i:i + size]
                if not s:
                    break
                yield s
                i += size
    '''
    def counter(x):
        counter.n += 1
        return counter.n//size
    counter.n = -1
    for k, g in groupby(iterable, counter):
         yield g

def GroupByN(seq, n):
    '''Return tuples of n items from the sequence.  If
    missing_None is True, return None for any missing items.

    See Batch() for a recipe that always returns all of the elements
    passed in, even if the last group is of smaller size than
    requested.

    Example:
        t = range(5)
        for i in GroupByN(t, 3, missing_None=False):
            print(i)
    prints
        (0, 1, 2)
        (3, 4, None)
    if missing_None is True and 
        (0, 1, 2)
    if missing_None is False.  In other words, if missing_None is
    False, groups without the full number of elements are discarded.
    '''
    # Adapted from a routine given in a comment to a recipe at 
    # http://code.activestate.com, but I've lost the exact URL.
    return map(None, *([iter(seq)]*n))

def UniqueItems(seq):
    '''Given a sequence, return a list of the unique elements in seq,
    maintaining their original order.
    '''
    d = odict()
    for i in seq:
        if i not in d:  
            d[i] = None
    return d.keys()

def soundex(s):
    '''Return the 4-character soundex value to a string argument.  The
    string s must be one word formed with ASCII characters and with no
    punctuation or spaces.  The returned soundex string can be used to
    compare the sounds of words; from US patents 1261167(1918) and
    1435663(1922) by Odell and Russell.
 
    The algorithm is from Knuth, "The Art of Computer Programming",
    volume 3, "Sorting and Searching", pg. 392:

        1. Retain first letter of name and drop all occurrences
           of a, e, h, i, o, u, w, y in other positions.
        2. Assign the following numbers to the remaining letters 
           after the first:
            1:  b, f, p, v
            2:  c, g, j, k, q, s, x, z
            3:  d, t
            4:  l
            5:  m, n
            6:  r
        3. If two or more letters with the same code were adjacent in
           the original name (before step 1), omit all but the first.
        4. Convert to the form "letter, digit, digit, digit" by adding
           trailing zeroes (if there are less than three digits), or
           by dropping rightmost digits (if there are more than
           three).
    '''
    if not s: 
        raise ValueError("Argument s must not be empty string")
    if set(s) - set(ascii_letters):
        raise ValueError("String s must contain only ASCII letters")
    if not hasattr(soundex, "m"):
        soundex.m = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                             "01230120022455012623010202"))
    # Function to map lower-case letters to soundex number
    getnum = lambda x: [soundex.m[i] for i in x]
    t = s.upper()
    num, keep = getnum(t), []
    # Step 0 (and step 3):  keep only those letters that don't map to
    # the same number as the previous letter.
    for i, code in enumerate(num):
        if not i:
            keep.append(t[0])   # Always keep first letter
        else:
            if code != num[i - 1]:
                keep.append(t[i])
    # Step 1:  remove vowels, etc.
    first_letter = keep[0]
    ignore, process = set("AEHIOUWY"), []
    process += [i for i in keep[1:] if i not in ignore]
    # Step 2:  assign numbers for remaining letters
    code = first_letter + ''.join(getnum(''.join(process)))
    # Step 3:  same as step 0
    # Step 4:  adjust length
    if len(code) > 4:
        code = code[:4]
    while len(code) < 4:
        code += "0"
    return code

def SoundSimilar(s, t):
    '''Returns True if the strings s and t sound similar.
    '''
    return True if soundex(s) == soundex(t) else False

def Cfg(lines, lvars=odict(), gvars=odict()):
    '''Allow use of sequences of text strings to be used for
    general-purpose configuration information.  Each string must be
    valid python code.
    
    Each line in lines is executed with the local variables in lvars
    and global variables in gvars.  The lvars dictionary is returned,
    which will contain each of the defined variables and functions.
 
    Any common leading indentation is removed before processing; this
    allows you to indent your configuration lines as desired.
 
    Example:
        lines = """
                from math import sqrt
                a = 44
                b = "A string"
                def X(a):
                    return a/2
                c = a*sqrt(2)
                d = X(a)
            """[1:-1].split("\n")
 
    The code
        d = Cfg(lines)
        for i in d.keys():
            print(i + " = " + str(d[i]))
 
    results in
        sqrt = <built-in function sqrt>
        a = 44
        b = A string
        X = <function X at 0x00B9C9B0>
        c = 62.2253967444
        d = 22.0
    '''
    # Remove any common indent
    indent = os.path.commonprefix(lines)
    if indent:
        lines = [i.replace(indent, "", 1) for i in lines]
    # Put lines into a temporary file so execfile can be used.  I
    # would have used NamedTemporaryFile(), but it doesn't work
    # correctly on Windows XP, so I used the deprecated mktemp.
    filename = tempfile.mktemp()
    f = open(filename, "wb")
    f.writelines([i + "\n" for i in lines])
    f.close()
    execfile(filename, gvars, lvars)
    os.remove(filename)
    # The things defined in the configuration lines are now in the
    # dictionary lvars.
    return lvars

def RemoveComment(line, code=False):
    '''Remove the largest string starting with '#' from the string
    line.  If code is True, then the resulting line will be compiled
    and an exception will occur if the modified line won't compile.
    This typically happens if '#' is inside of a comment.

    '''
    orig = line
    loc = line.find("#")
    if loc != -1:
        line = line[:loc]
    if code:
        try:
            compile(line, "", "single")
        except Exception:
            msg = "Line with comment removed won't compile:\n  '%s'" % orig
            raise ValueError(msg)
    return line

def bitlength(n):
    '''This emulates the n.bit_count() function of integers in python 2.7
    and 3.  This returns the number of bits needed to represent the
    integer n; n can be any integer.
 
    Note a naive implementation is to take the base two logarithm of
    the integer, but this will fail if abs(n) is larger than the
    largest floating point number.
    '''
    try:
        return n.bit_count()
    except Exception:
        return len(bin(abs(n))) - 2

def CountBits(num):
    '''Return the number of 'on' bits in the integer num.
    '''
    if not isinstance(num, Int):
        raise ValueError("num must be an integer")
    return sum([int(i) for i in list(bin(num)[2:])])

def ReadVariables(file, ignore_errors=False):
    '''Given a file of lines of python code, this function reads in
    each line and executes it.  If the lines of the file are
    assignments to variables, then this results in a defined variable
    in the local namespace.  Return the dictionary containing these
    variables.  
 
    Note that this function will not execute any line that doesn't
    contain an '=' character to cut down on the chance that some
    unforseen error can occur (but, of course, this protection can
    rather easily be subverted).
 
    This function is intended to be used to allow you to have an
    easy-to-use configuration file for a program.  For example, a user
    could write the configuration file
 
        # This is a comment
        doc = """Here's some
        documentation that 
        we'll use."""
        ProcessMean              = 37.2
        ProcessStandardDeviation = 12.1
        NumberOfParts            = 180
 
    When this function returned, you'd have a dictionary with four
    variables in it.
 
    If any line in the input file causes an exception, the offending
    line will be printed to stderr and the program will exit unless
    ignore_errors is True.
    '''
    lines = open(file).readlines()
    for i, line in enumerate(lines):
        if "=" not in line:
            continue
        try:
            exec(line)
        except Exception:
            sys.stderr.write("Line %d of file '%s' bad:\n  '%s'\n" % 
                    (i+1, file, line.rstrip()))
            if not ignore_errors:
                exit(1)
    del line, lines, i
    return locals()

def FindSubstring(string, substring):
    '''Return a tuple of the indexes of where the substring t is found
    in the string s.
    '''
    if not isinstance(string, String):
        raise TypeError("s needs to be a string")
    if not isinstance(substring, String):
        raise TypeError("t needs to be a string")
    d, ls, lsub = [], len(string), len(substring)
    if not ls or not lsub or lsub > ls:
        return tuple(d)
    start = string.find(substring)
    while start != -1 and ls - start >= lsub:
        d.append(start)
        start = string.find(substring, start + 1)
    return tuple(d)

def randq(seed=-1):
    '''The simple random number generator in the section "An Even
    Quicker Generator" from "Numerical Recipes in C", page 284,
    chapter 7, 2nd ed, 1997 reprinting (found on the web in PDF form).  

    If seed is not -1, it is used to initialize the sequence; it can
    be any hashable value.
    '''
    # The multiplicative constant 1664525 was recommended by Knuth and
    # the additive constant 1013904223 came from Lewis.
    a, c = 1664525, 1013904223
    if seed != -1:
        randq.idum = abs(hash(seed))
    randq.idum = (randq.a*randq.idum + randq.c) % randq.maxidum
    return randq.idum
    
# State variables for randq
randq.a = 1664525
randq.c = 1013904223
randq.idum = 0
randq.maxidum = 2**32

def randr(seed=-1):
    '''Uses randq to return a floating point number on [0, 1).
    '''
    n = randq(seed=seed) if seed != -1 else randq()
    return n/float(randq.maxidum)

def IsCygwinSymlink(file):
    '''Return True if file is a cygwin symbolic link.
    '''
    s = open(file).read(20)
    if len(s) > 10:
        if s[2:9] == "symlink":
            return True
    return False

def TranslateSymlink(file):
    '''For a cygwin symlink, return a string of what it's pointing to.
    '''
    return open(file).read()[12:].replace("\x00", "")

def GetString(prompt_msg, default, allowed_values, ignore_case=True):
    '''Get a string from a user and compare it to a sequence of
    allowed values.  If the response is in the allowed values, return
    it.  Otherwise, print an error message and ask again.  The letter
    'q' or 'Q' will let the user quit the program.  The returned
    string will have no leading or trailing whitespace.
    '''
    if ignore_case:
        allowed_values = [i.lower() for i in allowed_values]
    while True:
        out(prompt_msg, " [", default, "]:  ", nl=False, sep="")
        response = raw_input()
        s = response.strip()
        if not s:
            return default
        if s.lower() == "q":
            exit(0)
        s = s.lower() if ignore_case else s
        if s in allowed_values:
            return s
        out("'%s' is not a valid response" % response.rstrip())

def GetChoice(name, names):
    '''name is a string and names is a set or dict of strings.  Find
    if name uniquely identifies a string in names; if so, return it.
    If it isn't unique, return a list of the matches.  Otherwise
    return None.  The objective is to allow name to be the minimum
    length string necessary to uniquely identify the choice.
    '''
    # See self tests below for an example of use
    if not isinstance(name, String):
        raise ValueError("name must be a string")
    if not isinstance(names, (set, dict)):
        raise ValueError("names must be a set or dictionary")
    d, n = defaultdict(list), len(name)
    for i in names:
        d[i[:len(name)]] += [i]
    if name in d:
        if len(d[name]) == 1:
            return d[name][0]
        else:
            return d[name]
    return None

def int2base(x, base):
    '''Converts the integer x to a string representation in a given
    base.  base may be from 2 to 94.
 
    Method by Alex Martelli
    http://stackoverflow.com/questions/2267362/convert-integer-to-a-string-in-a-given-numeric-base-in-python
    Modified slightly by DP.
    '''
    if not (2 <= base <= len(int2base.digits)):
        msg = "base must be between 2 and %d inclusive" % len(int2base.digits)
        raise ValueError(msg)
    if not isinstance(x, Int + String):
        raise ValueError("Argument x must be an integer or string")
    if isinstance(x, String):
        x = int(x)
    sgn = 1
    if x < 0: 
        sgn = -1
    elif not x: 
        return '0'
    x, answer = abs(x), []
    while x:
        answer.append(int2base.digits[x % base])
        x //= base
    if sgn < 0:
        answer.append('-')
    answer.reverse()
    return ''.join(answer)

int2base.digits = digits + ascii_letters + punctuation

def base2int(x, base):
    '''Inverse of int2base.  Converts a string x in the indicated base
    to a base 10 integer.  base may be from 2 to 94.
    '''
    if not (2 <= base <= len(base2int.digits)):
        msg = "base must be between 2 and %d inclusive" % len(base2int.digits)
        raise ValueError(msg)
    if not isinstance(x, String):
        raise ValueError("Argument x must be a string")
    y = list(reversed(x))
    n = 0
    for i, c in enumerate(list(reversed(x))):
        try:
            val = base2int.digits.index(c)
        except Exception:
            msg = "'%c' not a valid character for base %d" % (c, base)
            raise ValueError(msg)
        n += val*(base**i)
    return n

base2int.digits = digits + ascii_letters + punctuation

def IsTextFile(file, num_bytes=100):
    '''Heuristic to classify a file as text or binary.  The algorithm
    is to read num_bytes from the beginning of the file; if there are
    any characters other than the "typical" ones found in plain text
    files, the file is classified as binary.

    Note:  if file is a string, it is assumed to be a file name and
    opened.  Otherwise it is assumed to be an open stream.
    '''
    text_chars = set([ord(i) for i in "\n\r\b\t\v"] + range(32, 127))
    if isinstance(file, String):
        s = open(file, "rb").read(num_bytes)
    else:
        s = file.read(num_bytes)
    for c in s:
        if ord(c) not in text_chars:
            return False
    return True

def IsBinaryFile(file, num_bytes=100):
    return not IsTextFile(file, num_bytes)

class Dispatch:
    '''The Dispatch class allows different functions to be called
    depending on the argument types.  Thus, there can be one function
    name regardless of the argument type.  Due to David Ascher.

    Example:  the following lets us define a function ss which will 
    calculate the sum of squares of the contents of an array, whether
    the array is a python sequence or a NumPy array.
    ss = Dispatch((list_ss, (ListType, TupleType)), 
                            (array_ss, (numpy.ArrayType)))
    '''
    def __init__(self, *tuples):
        self._dispatch = {}
        for func, types in tuples:
            for t in types:
                if t in self._dispatch.keys():
                    raise ValueError("can't have two dispatches on "+str(t))
                self._dispatch[t] = func
        self._types = self._dispatch.keys()
    def __call__(self, arg1, *args, **kw):
        if type(arg1) not in self._types:
            raise TypeError("don't know how to dispatch %s arguments" %
                type(arg1))
        return apply(self._dispatch[type(arg1)], (arg1,) + args, kw)

def IsIterable(x, exclude_strings=False):
    '''Return True if x is an iterable.  You can exclude strings from the
    things that can be iterated on if you wish.
 
    Note:  if you don't care whether x is a string or not, a simpler way
    is:
        try:
            iter(x)
            return True
        except TypeError:
            return False
    '''
    if exclude_strings and isinstance(x, String):
        return False
    return True if isinstance(x, Iterable) else False

def ListInColumns(alist, col_width=0, num_columns=0, space_betw=0, truncate=0):
    '''Returns a list of strings with the elements of alist (if
    components are not strings, they will be converted to strings
    using str) printed in columnar format.  Elements of alist that
    won't fit in a column either generate an exception if truncate is
    0 or get truncated if truncate is nonzero.  The number of spaces
    between columns is space_betw.
 
    If col_width and num_columns are 0, then the program will set them
    by reading the COLUMNS environment variable.  If COLUMNS doesn't
    exist, col_width will default to 80.  num_columns will be chosen
    by finding the length of the largest element so that it is not 
    truncated.
 
    Caveat:  if there are a small number of elements in the list, you
    may not get what you expect.  For example, try a list size of 1 to
    10 with num_columns equal to 4:  for lists of 1, 2, 3, 5, 6, and 9,
    you'll get fewer than four columns.
    '''
    # Make all integers
    col_width   = int(col_width)
    num_columns = int(num_columns)
    space_betw  = int(space_betw)
    truncate    = int(truncate)
    lines = []
    N = len(alist)
    if not N:
        return [""]
    # Get the length of the longest line in the alist
    maxlen = max([len(str(i)) for i in alist])
    if not maxlen:
        return [""]
    if not col_width:
        if "COLUMNS" in os.environ:
            columns = int(os.environ["COLUMNS"]) - 1
        else:
            columns = 80 - 1
        col_width = maxlen
    if not num_columns:
        try:
            num_columns = int(columns//maxlen)
        except Exception:
            return [""]
        if num_columns < 1:
            raise ValueError("A line is too long to display")
        space_betw = 1
    if not col_width or not num_columns or space_betw < 0:
        raise ValueError("Error: invalid parameters")
    num_rows = int(N//num_columns + (N % num_columns != 0))
    for row in range(num_rows):
        s = ""
        for column in range(num_columns):
            ix = int(num_rows*column + row)
            if 0 <= ix <= (N-1):
                if len(str(alist[ix])) > col_width:
                    if truncate:
                        s += str(alist[ix])[:col_width] + " "*space_betw
                    else:
                        raise ValueError("Error:  element %d too long" % ix)
                else:
                    s += (str(alist[ix]) + " " * (col_width -
                    len(str(alist[ix]))) + " " * space_betw)
        lines.append(s) 
    assert(len(lines) == num_rows)
    return lines

def SpeedOfSound(T):
    '''Returns speed of sound in air in m/s as a function of temperature 
    T in K.  Assumes sea level pressure.
    '''
    assert(T > 0)
    return 331.4*math.sqrt(T/273.15)

def WindChillInDegF(wind_speed_in_mph, air_temp_deg_F):
    '''Wind Chill for exposed human skin, expressed as a function of 
    wind speed in miles per hour and temperature in degrees Fahrenheit.

    Here is the old formula gotten from the Snippets collection:
        from math import sqrt
        if wind_speed_in_mph < 4:
            return air_temp_deg_F * 1.0
        return (((10.45 + (6.686112 * sqrt(1.0*wind_speed_in_mph)) \
            - (.447041 * wind_speed_in_mph)) / 22.034 * \
            (air_temp_deg_F - 91.4)) + 91.4)
    The new formula is gotten from
    http://en.wikipedia.org/wiki/Wind_chill.
    '''
    return 35.74 + 0.6215*air_temp_deg_F - 35.75*wind_speed_in_mph**0.16 + \
           0.4275*air_temp_deg_F*wind_speed_in_mph**0.16

def HeatIndex(air_temp_deg_F, relative_humidity_percent):
    '''From http://www.weather.gov/forecasts/graphical/sectors/idaho.php#tabs.
    See also http://www.crh.noaa.gov/pub/heat.php.
 
    Heat Index combines the effects of heat and humidity. When heat and
    humidity combine to reduce the amount of evaporation of sweat from the
    body, outdoor exercise becomes dangerous even for those in good shape.
 
    Example:  for 90 deg F and 50% RH, the heat index is 94.6.
 
    The equation used is a multiple regression fit to a complicated set of
    equations that must be solved iteratively.  The uncertainty with a
    prediction is given at 1.3 deg F.  See
    http://www.srh.noaa.gov/ffc/html/studies/ta_htindx.PDF for details.
 
    If heat index is:
 
        80-90 degF:  Caution:  fatigue possible with prolonged exposure or
                     activity.
        90-105:      Extreme caution:  sunstroke, muscle cramps and/or heat
                     exhaustion possible with prolonged exposure and/or
                     physical activity.
        105-129:     Danger:  sunstroke, muscle cramps and/or heat exhaustion
                     likely.  Heatstroke possible with prolonged exposure
                     and/or physical activity.
        >= 130       Extreme danger:  Heat stroke or sunstroke likely.
    '''
    RH, Tf = relative_humidity_percent, air_temp_deg_F
    HI = -42.379 + 2.04901523*Tf + 10.14333127*RH - 0.22475541*Tf*RH \
         -6.83783e-3*Tf*Tf - 5.481717e-2*RH*RH + 1.22874e-3*Tf*Tf*RH + \
         8.5282e-4*Tf*RH*RH - 1.99e-6*Tf*Tf*RH*RH
    return HI

def SpellCheck(input_list, word_dictionary, case_is_not_important = 1):
    '''The list of words to spell check are in input_list and the
    dictionary word_dictionary (it's a dictionary rather than a list
    to allow fast access; the dictionary values can be null strings --
    all that's important is that the key be there).  It returns any
    words in input_list that are not in word_dictionary.
    '''
    import string
    misspelled = []
    if len(input_list) == 0:
        return []
    if len(word_dictionary) == 0:
        raise ValueError("Word_dictionary parameter is empty")
    for ix in range(len(input_list)):
        word = input_list[ix]
        if case_is_not_important:
            word = input_list[ix].lower()
        if word not in word_dictionary:
            misspelled.append(word)
    return misspelled

def Keep(s, keep):
    '''Keep only items in sequence s that are elements in keep.
    '''
    f = lambda x: x in set(keep)
    return ''.join([f(i) for i in s])

def KeepFilter(keep):
    '''Return a function that takes a string and returns a string
    containing only those characters that are in keep.
    '''
    def func(s):
        return Keep(s, keep)
    return func

def Remove(s, remove):
    '''Remove characters in string s that are in remove.
    '''
    f = lambda x: x not in set(remove)
    return ''.join([f(i) for i in s])

def RemoveFilter(remove):
    '''Return a function that takes a string and returns a string
    containing only those characters that are not in remove.
    '''
    def func(s):
        return Remove(s, remove)
    return func

class Debug:
    '''Implements a debug class that can be useful in printing debugging
    information.
    '''
    def __init__(self, fd=sys.stderr, add_nl=True, prefix="+ "):
        self.fd = fd
        self.on = True
        self.add_nl = add_nl
        self.prefix = prefix
    def print(self, s):
        if self.on:
            s = self.prefix + s
            if self.add_nl:
                s += nl
            self.fd.write(s)

def Time():
    '''Returns the current time in the following format:
        Mon Oct 25 22:05:00 2010
    '''
    import time
    return time.ctime(time.time())

def AWG(n):
    '''Returns the wire diameter in inches given the AWG (American Wire
    Gauge) number (also known as the Brown and Sharpe gauge).  Use negative
    numbers as follows:
 
        00    -1
        000   -2
        0000  -3
 
    Reference:  the units.dat file with version 1.80 of the GNU units
    program gives the following statement:
 
        American Wire Gauge (AWG) or Brown & Sharpe Gauge appears to be the
        most important gauge. ASTM B-258 specifies that this gauge is based
        on geometric interpolation between gauge 0000, which is 0.46 inches
        exactly, and gauge 36 which is 0.005 inches exactly.  Therefore,
        the diameter in inches of a wire is given by the formula 
                1|200 92^((36-g)/39).  
        Note that 92^(1/39) is close to 2^(1/6), so diameter is
        approximately halved for every 6 gauges.  For the repeated zero
        values, use negative numbers in the formula.  The same document
        also specifies rounding rules which seem to be ignored by makers of
        tables.  Gauges up to 44 are to be specified with up to 4
        significant figures, but no closer than 0.0001 inch.  Gauges from
        44 to 56 are to be rounded to the nearest 0.00001 inch.  
 
    An equivalent formula is 0.32487/1.12294049**n where n is the
    gauge number (works for n >= 0).
    '''
    if n < -3 or n > 56:
        raise ValueError("AWG argument out of range")
    diameter = 92.**((36 - n)/39)/200
    if n <= 44:
        return round(diameter, 4)
    return round(diameter, 5)

def WireGauge(num, mm=False):
    '''If num is an integer between 1 and 80, this function will
    return the diameter of the indicated wire gauge size in inches (or
    mm if the mm keyword is True).  This gauge is the one that is
    typically used for number-sized drills in the US.
     
    If num is a floating point number, this function will return an
    integer representing the nearest wire gauge size.  It will throw
    an exception if the floating point number is greater than the
    diameter of #1 or less than #80.
    '''
    # Index number is wire gauge number
    sizes = (0,
         0.2280, 0.2210, 0.2130, 0.2090, 0.2055, 0.2040, 0.2010, 0.1990, 
         0.1960, 0.1935, 0.1910, 0.1890, 0.1850, 0.1820, 0.1800, 0.1770,
         0.1730, 0.1695, 0.1660, 0.1610, 0.1590, 0.1570, 0.1540, 0.1520,
         0.1495, 0.1470, 0.1440, 0.1405, 0.1360, 0.1285, 0.1200, 0.1160, 
         0.1130, 0.1110, 0.1100, 0.1065, 0.1040, 0.1015, 0.0995, 0.0980,
         0.0960, 0.0935, 0.0890, 0.0860, 0.0820, 0.0810, 0.0785, 0.0760,
         0.0730, 0.0700, 0.0670, 0.0635, 0.0595, 0.0550, 0.0520, 0.0465,
         0.0430, 0.0420, 0.0410, 0.0400, 0.0390, 0.0380, 0.0370, 0.0360,
         0.0350, 0.0330, 0.0320, 0.0310, 0.0293, 0.0280, 0.0260, 0.0250,
         0.0240, 0.0225, 0.0210, 0.0200, 0.0180, 0.0160, 0.0145, 0.0135)
    if isinstance(num, Int):
        if num < 1 or num > 80:
            raise ValueError("num must be between 1 and 80 inclusive")
        return sizes[num]*25.4 if mm else sizes[num]
    elif isinstance(num, float):
        if mm:
            num /= 25.4  # Convert to inches
        if num > sizes[1] or num < sizes[80]:
            raise ValueError("num diameter is outside wire gauge range")
        # A binary search would be faster, but this is easier to code
        s = map(lambda x: abs(x - num), sizes)  # Diff from target
        t = [(s[i], i) for i in range(len(s))] # Combine with array position
        t.sort()  # Sort to put minimum diff first in list
        return t[0][1]
    else:
        raise ValueError("num is an unexpected type")

if not py3:
    # This only works in python 2
    def partition(iterable, chain=chain, map=map):
        '''Generates the partitions of an iterable.  For example, if the
        iterable is the string "abc", the partitions returned are:
            [['abc'], ['a', 'bc'], ['ab', 'c'], ['a', 'b', 'c']]
        By Raymond Hettinger.  From 
        http://code.activestate.com/recipes/576795.
        '''
        s = iterable if hasattr(iterable, '__getslice__') else list(iterable)
        n = len(s)
        first, middle, last = [0], range(1, n), [n]
        getslice = s.__getslice__
        return [map(getslice, chain(first, div), chain(div, last))
                for i in range(n) for div in combinations(middle, i)]

def SignMantissaExponent(x, digits=15):
    '''Returns a tuple (sign, mantissa, exponent) of a floating point
    number x.
    '''
    s = ("%%.%de" % digits) % abs(float(x))
    return (1 - 2*(x < 0), float(s[0:digits + 2]), int(s[digits + 3:]))

def SignificantFiguresS(value, digits=3, exp_compress=True):
    '''Returns a string representing the number value rounded to
    a specified number of significant figures.  The number is
    converted to a string, then rounded and returned as a string.
    If you want it back as a number, use float() on the string.
    If exp_compress is true, the exponent has leading zeros 
    removed.
 
    The following types of printouts can be gotten using this function
    and native python formats:
 
           A              B               C               D
       3.14e-12       3.14e-012       3.14e-012       3.14e-012
       3.14e-11       3.14e-011       3.14e-011       3.14e-011
       3.14e-10       3.14e-010       3.14e-010       3.14e-010
        3.14e-9       3.14e-009       3.14e-009       3.14e-009
        3.14e-8       3.14e-008       3.14e-008       3.14e-008
        3.14e-7       3.14e-007       3.14e-007       3.14e-007
        3.14e-6       3.14e-006       3.14e-006       3.14e-006
        3.14e-5       3.14e-005       3.14e-005       3.14e-005
        3.14e-4       3.14e-004        0.000314        0.000314
        3.14e-3       3.14e-003         0.00314         0.00314
        3.14e-2       3.14e-002          0.0314          0.0314
        3.14e-1       3.14e-001           0.314           0.314
        3.14e+0       3.14e+000            3.14            3.14
        3.14e+1       3.14e+001            31.4            31.4
        3.14e+2       3.14e+002             314           314.0
        3.14e+3       3.14e+003       3.14e+003          3140.0
        3.14e+4       3.14e+004       3.14e+004         31400.0
        3.14e+5       3.14e+005       3.14e+005        314000.0
        3.14e+6       3.14e+006       3.14e+006       3140000.0
        3.14e+7       3.14e+007       3.14e+007      31400000.0
        3.14e+8       3.14e+008       3.14e+008     314000000.0
        3.14e+9       3.14e+009       3.14e+009    3140000000.0
       3.14e+10       3.14e+010       3.14e+010   31400000000.0
       3.14e+11       3.14e+011       3.14e+011  314000000000.0
       3.14e+12       3.14e+012       3.14e+012       3.14e+012
 
    A:  SignificantFiguresS(x, 3)
    B:  SignificantFiguresS(x, 3, 0)
    C:  "%.3g" % x
    D:  float(SignificantFiguresS(x, 3))
    '''
    if digits < 1 or digits >15:
        raise ValueError("Number of significant figures must be >= 1 and <= 15")
    sign, significand, exponent = SignMantissaExponent(float(value))
    fmt = "%%.%df" % (digits-1)
    neg = "-" if sign < 0 else ""
    e = "e%+d" % exponent if exp_compress else "e%+04d" % exponent
    return neg + (fmt % significand) + e

def SignificantFigures(value, figures=3):
    '''Rounds a value to specified number of significant figures.
    Returns a float.
    '''
    return float(SignificantFiguresS(value, figures))

def Engineering(value, digits=3):
    '''Return a tuple (m, e, s) representing a number in engineering
    notation.  m is the significand.  e is the exponent in the form of
    an integer; it is adjusted to be a multiple of 3.  s is the SI
    symbol for the exponent; for "e+003" it would be "k".  s is empty
    if there is no SI symbol.
 
    Engineering(1.2345678901234567890e-88, 4) --> ('123.5', -90, '')
    Engineering(1.2345678901234567890e-8, 4)  --> ('12.35', -9, 'n')
    Engineering(1.2345678901234567890e8, 4)   --> ('123.5', 6, 'M')
    Examples:
    '''
    suffixes = {-8:"y", -7:"z", -6:"a", -5:"f", -4:"p", -3:"n",
        -2:"u", -1:"m", 0:"", 1:"k", 2:"M", 3:"G", 4:"T",
        5:"P", 6:"E", 7:"Z", 8:"Y"}
    if digits < 1 or digits >15:
        raise ValueError("Number of significant digits must be >= 1 and <= 15")
    sign, significand, exponent = SignMantissaExponent(float(value))
    s = suffixes[exponent//3] if exponent//3 in suffixes else ""
    m = sign*(("%%.%dg" % digits) % (significand*10**(exponent % 3)))
    if m.find("e") != -1:
        # digits = 1 or 2 can cause e.g. 3e+001, so the following
        # eliminates the exponential notation
        m = str(int(float(m)))
    return m, 3*(exponent//3), s

def eng(value, digits=3, unit=None, width=0):
    '''Convenience function for engineering representation.  If unit is
    given, then the number of digits is displayed in value with the
    prefix prepended to unit.  Otherwise, "xey" notation is used, except if
    y == 0, no exponent portion is given.  Returns a string for printing.
    If width is nonzero, then returns a string right-justified to that
    width.
    '''
    m, e, p = Engineering(value, digits)
    if unit:
        s = m + " " + p + unit
    else:
        s = m if e == 0 else "%se%d" % (m, e)
    if width:
        if len(s) < width:
            p = (" " * (width - len(s)))
            s = p + s
    return s

def IdealGas(P=0, v=0, T=0, MW=28.9):
    '''Given two of the three variables P, v, and T, calculates the
    third for the indicated gas.  The variable that is unknown should
    have a value of zero.  
        P = pressure in Pa
        v = specific volume in m^3/kg
        T = absolute temperature in K
        MW = molecular weight = molar mass in g/mol (defaults to air)  
             Note you can also supply a string; if the lower-case
             version of this string is in the dictionary of gas_molar_mass 
             below, the molar mass for that gas will be used.
    The tuple (P, v, T) will be returned.
 
    WARNING:  NOTE THAT v IS THE SPECIFIC VOLUME, NOT THE VOLUME!
 
    The equation used is P*v = R*T where R is the gas constant for this
    particular gas.  It is the universal gas constant divided by the 
    molecular weight of the gas.
 
    The ideal gas law is an approximation, but a good one for high
    temperatures and low pressures.  Here, high and low are relative
    to the critical temperature and pressure of the gas; these can be
    found in numerous handbooks, such as the CRC Handbook of Chemistry
    and Physics, the Smithsonian Critical Tables, etc.
 
    Some molar masses and critical values for common gases are:
 
                    Tc       Pc     MW
        air        133.3   37.69   28.9 
        ammonia    405.6  113.14   17.03 
        argon      151.0   48.00   39.95
        co2        304.2   73.82   44.0099 
        helium       5.2    2.25    4.003 
        hydrogen    33.3   12.97    2.01594 
        methane    190.6   46.04   16.04298 
        nitrogen   126.1   33.94   28.0134 
        oxygen     154.6   50.43   31.9988 
        propane    369.8   42.49   26.03814 
        water      647.3  221.2    18.01534 
        xenon      289.8   58.00  131.30 
 
    Tc is the critical temperature in K, Pc is the critical pressure
    in bar (multiply by 1e5 to get Pa), and MW is the molecular 
    weight in daltons (1 Da = 1 g/mol).
    '''
    gas_molar_mass = {
        "air"      : 28.9,
        "ammonia"  : 17.03,
        "argon"    : 39.95,
        "co2"      : 44.0099,
        "helium"   : 4.003,
        "hydrogen" : 2.01594,
        "methane"  : 16.04298,
        "nitrogen" : 28.0134,
        "oxygen"   : 31.9988,
        "propane"  : 26.03814,
        "water"    : 18.01534,
        "xenon"    : 131.30,
    }
    if isinstance(MW, String):
        MW = gas_molar_mass[MW.lower()]
    else:
        assert(P >= 0 and v >= 0 and T >= 0 and MW >= 0)
    molar_gas_constant = 8.3145         # J/(mol*K)
    R = molar_gas_constant/(float(MW)/1000)   # 1000 converts g to kg
    if sum([i == 0 for i in (P, v, T)]) != 1:
        raise ValueError("One and only one of P, v, T must be zero")
    if not P:
        return R*T/v
    elif not v:
        return R*T/P
    else:
        return P*v/R

def AlmostEqual(a, b, rel_err=2e-15, abs_err = 5e-323):
    '''Determine whether floating-point values a and b are equal to
    within a (small) rounding error; return True if almost equal and
    False otherwise.  The default values for rel_err and abs_err are
    chosen to be suitable for platforms where a float is represented
    by an IEEE 754 double.  They allow an error of between 9 and 19
    ulps.
 
    This routine comes from the Lib/test/test_cmath.py in the python
    distribution; the function was called almostEqualF.
    '''
    # Special values testing
    if math.isnan(a):
        return math.isnan(b)
    if math.isinf(a):
        return a == b
    # If both a and b are zero, check whether they have the same sign
    # (in theory there are examples where it would be legitimate for a
    # and b to have opposite signs; in practice these hardly ever
    # occur).
    if not a and not b:
        return math.copysign(1., a) == math.copysign(1., b)
    # If a-b overflows, or b is infinite, return False.  Again, in
    # theory there are examples where a is within a few ulps of the
    # max representable float, and then b could legitimately be
    # infinite.  In practice these examples are rare.
    try:
        absolute_error = abs(b-a)
    except OverflowError:
        return False
    else:
        return absolute_error <= max(abs_err, rel_err * abs(a))

def Flatten(L, max_depth=None, ltypes=(list, tuple)):
    ''' Flatten every sequence in "L" whose type is contained in
    "ltypes" to "max_depth" levels down the tree.  The sequence
    returned has the same type as the input sequence.
 
    Written by Kevin L. Sitze on 2010-11-25
    From http://code.activestate.com/recipes/577470-fast-flatten-with-depth-control-and-oversight-over/?in=lang-python
    This code may be used pursuant to the MIT License.

    Note:  itertools has a flatten() recipe that can also be used, but
    every element encountered needs to be an iterable.  This Flatten()
    function works more generally.
    '''
    if max_depth is None: 
        make_flat = lambda x: True
    else: 
        make_flat = lambda x: max_depth > len(x)
    if callable(ltypes): 
        is_sequence = ltypes
    else: 
        is_sequence = lambda x: isinstance(x, ltypes)
    r, s = [], []
    s.append((0, L))
    while s:
        i, L = s.pop()
        while i < len(L):
            while is_sequence(L[i]):
                if not L[i]: 
                    break
                elif make_flat(s):
                    s.append((i + 1, L))
                    L = L[i]
                    i = 0
                else:
                    r.append(L[i])
                    break
            else: 
                r.append(L[i])
            i += 1
    try: 
        return type(L)(r)
    except TypeError: 
        return r

def CommonPrefix(seq):
    '''Return the largest string that is a prefix of all the strings in
    seq.
    '''
    return os.path.commonprefix(seq)

def CommonSuffix(seq):
    '''Return the largest string that is a suffix of all the strings in
    seq.
    Copyright (c) 2002-2009 Zooko Wilcox-O'Hearn, who put it under the GPL.
    '''
    cp = []
    for i in range(min(map(len, seq))):
        c = seq[0][-i-1]
        for s in seq[1:]:
            if s[-i-1] != c:
                cp.reverse()
                return ''.join(cp)
        cp.append(c)
    cp.reverse()
    return ''.join(cp)

def TempConvert(t, in_unit, to_unit):
    '''Convert the temperature in t in the unit specified in in_unit to the
    unit specified by to_unit.
    '''
    allowed, k, r, a, b = "cfkr", 273.15, 459.67, 1.8, 32
    def check(unit, orig):
        if len(unit) != 1 and unit not in allowed:
            raise ValueError("'%s' is a bad temperature unit" % orig)
    inu, tou = [i.lower() for i in (in_unit, to_unit)]
    check(inu, in_unit)
    check(tou, to_unit)
    if inu == tou:
        return t
    d = {
        "cf" : lambda t: a*t + b,
        "ck" : lambda t: t + k,
        "cr" : lambda t: a*(t + k),
        "fc" : lambda t: (t - b)/a,
        "fk" : lambda t: (t - b)/a + k,
        "fr" : lambda t: t + r,
        "kc" : lambda t: t - k,
        "kf" : lambda t: a*(t - k) + b,
        "kr" : lambda t: a*t,
        "rc" : lambda t: (t - r - b)/a,
        "rf" : lambda t: t - r,
        "rk" : lambda t: t/a,
    }
    T = d[inu + tou](t)
    e = ValueError("Converted temperature is too low")
    if ((tou in "kr" and T < 0) or (tou == "c" and T < -k) or
        (tou == "f" and T < -r)):
        raise e
    return T

def SplitOnNewlines(s):
    ''' Splits s on all of the three newline sequences: "\r\n", "\r", or
    "\n".  Returns a list of the strings.
 
    Copyright (c) 2002-2009 Zooko Wilcox-O'Hearn, who put it under the GPL.
    '''
    cr = "\r"
    res = []
    for x in s.split(cr + nl):
        for y in x.split(cr):
           res.extend(y.split(nl))
    return res

# 18 Oct 2010
# The following commented-out version was found on the web.  It's nice and
# compact, but since it uses recursion, it will fail for integers with
# sufficient digits (on Ubuntu 10.4, it failed at just less than 1000
# digits; on Windows 7, it failed at 1202 digits).  Thus, I removed the
# tail recursion and made the routine take positive and negative integers.
#
#def DecimalToBase(num, base, dd=False):
#    '''Convert a decimal integer num to a string in base base.  From
#    http://www.daniweb.com/forums/thread159163.html (scroll down the page
#    to see solsteel's message).
#    '''
#    if not 2 <= base <= 36:
#        raise ValueError, 'The base number must be between 2 and 36.'
#    if not dd:
#        dd = dict(zip(range(36), list(string.digits + string.ascii_lowercase)))
#    if num == 0:
#        return ""
#    num, rem = divmod(num, base)
#    return DecimalToBase(num, base, dd) + dd[rem]

def DecimalToBase(num, base, check_result=False):
    '''Convert a decimal integer num to a string in base base.  Tested with
    random integers from 10 to 10,000 digits in bases 2 to 36 inclusive.
    Set check_result to True to assure that the integer was converted
    properly.
    '''
    if not 2 <= base <= 36:
        raise ValueError('Base must be between 2 and 36.')
    if num == 0: 
        return "0"
    s, sign, n = "0123456789abcdefghijklmnopqrstuvwxyz", "", abs(num)
    if num < 0:
        sign, num = "-", abs(num)
    d, in_base = dict(zip(range(len(s)), list(s))), ""
    while num:
        num, rem = divmod(num, base)
        in_base = d[rem] + in_base
    if check_result and int(in_base, base) != n:
        raise ArithmeticError("Base conversion failed for %d to base %d" %
            (num, base))
    return sign + in_base

def ConvertToNumber(s, handle_i=True):
    '''This is a general-purpose routine that will return a python number
    for a string if it is possible.  The basic logic is:
        * If it contains 'j' or 'J', it's complex
        * If it contains '/', it's a fraction
        * If it contains '.', 'E', or 'e', it's a float
        * Otherwise it's interpreted to be an integer
    Since I prefer to use 'i' for complex numbers, we'll also allow an 'i'
    in the number unless handle_i is False.
    '''
    s = s.lower()
    if handle_i:
        s = s.replace("i", "j")
    if 'j' in s:
        return complex(s)
    elif '.' in s or 'e' in s:
        return float(s)
    elif '/' in s:
        return Fraction(s)
    else:
        return int(s)

class BitVector:
    '''From
    http://stackoverflow.com/questions/147713/how-do-i-manipulate-bits-in-python
    Example will print out
    D
    E
    A
    D

    b = BitVector(0)
    b[3:0]   = 0xD
    b[7:4]   = 0xE
    b[11:8]  = 0xA
    b[15:12] = 0xD

    for i in range(0,16,4):
        print '%X'%b[i+3:i]
    '''
    def __init__(self,val):
        self._val = val

    def __setslice__(self,highIndx,lowIndx,newVal):
        assert math.ceil(math.log(newVal)/math.log(2)) <= (highIndx-lowIndx+1)
        # clear out bit slice
        clean_mask = (2**(highIndx+1)-1)^(2**(lowIndx)-1)
        self._val = self._val ^ (self._val & clean_mask)
        # set new value
        self._val = self._val | (newVal<<lowIndx)

    def __getslice__(self,highIndx,lowIndx):
        return (self._val>>lowIndx)&(2**(highIndx-lowIndx+1)-1)

def hyphen_range(s, sorted=False, unique=False):
    '''Takes a set of range specifications of the form "a-b" and returns a
    list of integers between a and b inclusive.  Also accepts comma
    separated ranges like "a-b,c-d,f".  Numbers from a to b, a to d and f.
    If sorted is True, the returned list will be sorted.  If unique is
    True, only unique numbers are kept and the list is automatically
    sorted.  In "a-b", a can be larger than b, in which case the
    sequence will decrease until b is reached.
 
    Adapted from routine at 
    http://code.activestate.com/recipes/577279-generate-list-of-numbers-from-hyphenated-and-comma/?in=lang-python
    '''
    s = "".join(s.split())    # Removes white space
    r = []
    for x in s.split(','):
        t = [int(i) for i in x.split('-')]
        if len(t) not in (1, 2): 
            raise ValueError("'%s' is bad range specifier" % s)
        if len(t) == 1:
            r.append(t[0])  
        else:
            if t[0] < t[1]:
                r.extend(range(t[0], t[1] + 1))
            else:
                r.extend(range(t[0], t[1] - 1, -1))
    if sorted:
        r.sort()
    elif unique:
        r = list(set(r))
        r.sort()
    return r

US_states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

def Binary(n):
    '''convert an integer n to a binary string.  Adapted
    from http://www.daniweb.com/software-development/python/code/216539.
    Example:  Binary(11549) gives '10110100011101'.  Note python has a
    built-in for this:  bin(n); using 
        return "-" + bin(n)[2:] if n < 0 else bin(n)[2:]
    could do this function with one line.
    '''
    s, m = "", abs(n)
    if not n:
        return "0"
    while m > 0:
        s = str(m % 2) + s
        m >>= 1
    return "-" + s if n < 0 else s

def int2bin(n, numbits=32):
    '''Returns the binary of integer n, using numbits number of
    digits.  Note this is a two's-complement representation.
    From http://www.daniweb.com/software-development/python/code/216539
    '''
    return "".join([str((n >> y) & 1) for y in range(numbits - 1, -1, -1)])

def grouper(data, mapper, reducer=None):
    '''Simple map/reduce for data analysis.
 
    Each data element is passed to a *mapper* function.
    The mapper returns key/value pairs
    or None for data elements to be skipped.
 
    Returns a dict with the data grouped into lists.
    If a *reducer* is specified, it aggregates each list.
 
    >>> def even_odd(elem):                     # sample mapper
    ...     if 10 <= elem <= 20:                # skip elems outside the range
    ...         key = elem % 2                  # group into evens and odds
    ...         return key, elem
 
    >>> grouper(range(30), even_odd)         # show group members
    {0: [10, 12, 14, 16, 18, 20], 1: [11, 13, 15, 17, 19]}
 
    >>> grouper(range(30), even_odd, sum)    # sum each group
    {0: 90, 1: 75}
 
    Note:  from
    http://code.activestate.com/recipes/577676-dirt-simple-mapreduce/?in=lang-python
    I renamed the function to grouper.
    '''
    d = {}
    for elem in data:
        r = mapper(elem)
        if r is not None:
            key, value = r
            if key in d:
                d[key].append(value)
            else:
                d[key] = [value]
    if reducer is not None:
        for key, group in d.items():
            d[key] = reducer(group)
    return d

def FindDiff(s1, s2, ignore_empty=False, equal_length=False):
    '''Returns the integer index of where the strings s1 and s2 first
    differ.  The number returned is the index where the first
    difference was found.  If the strings are equal, then -1 is
    returned, implying one string is a substring of the other (or they
    are the same string).  If ignore_empty is True, an exception is
    raised if one of the strings is empty.  If equal_length is True,
    then the strings must be of equal length or a ValueError exception
    is raised.
    '''
    if not isinstance(s1, String) or not isinstance(s2, String):
        raise TypeError("Arguments must be strings")
    if (not s1 or not s2) and not ignore_empty:
        raise ValueError("String cannot be empty")
    ls1, ls2 = len(s1), len(s2)
    if equal_length and ls1 != ls2:
        raise ValueError("Strings must be equal lengths")
    n = min(len(s1), len(s2))
    if not n:
        return 0
    for i in range(n):
        if s1[i] != s2[i]:
            return i
    # If we get here, every character matched up to the end of the
    # shorter string.
    return -1

# EndCoverage (for checking test coverage)
