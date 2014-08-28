'''
Todo:

    * Review tests & release.

----------------------------------------------------------------------
Class WordNum to convert to and from word descriptions of a number.

Features:

    * Singe function interface.
    * Handles integers, fractions, and floating point numbers.
    * Handles short and long scale numbers.
    * '.' radix and ',' digit separator or vice versa.
    * Can convert numbers to ordinals.
    * Tested under python 2.7.6 and 3.4.0.

Comments
--------

    Many people have not come across short and long scale differences
    and are surprised by them -- and, of course, they feel that the
    scale they use is the "right" way and the other scale terms are
    "wrong".  These scale differences aren't important in technical
    work because scientists and engineers don't use them -- they use
    SI and scientific notation, which don't suffer from this
    historical ambiguity.  If you are unfamiliar with the differences,
    read the referenced wikipedia pages for more detail.

    The writing of this script was done mostly as a lark, as I have no
    real need to convert between word and number forms.  I can't
    remember now what triggered me to develop this code -- but once
    started, I felt driven to finish it.  No doubt others of you
    understand where this impulse comes from. :^)  Most of the fun was
    figuring out suitable algorithms, then writing tests to find out
    how I had missed the special cases.

    I don't know if I've gotten the long scale terminology correct, as
    there are no easily-found examples.  Since the distance between a
    billion and a trillion in long scale is 1e6, that implies to me
    that the modifier for terms like 'billion', 'trillion', etc. can
    be a number between 1 and 1e6 - 1.  This means there can be
    multiple occurrences of the word 'thousand' in a legitimate string
    of words describing a number, unlike the short scale.  This made
    the conversion of a long scale set of words to a number a little
    more involved than for short scale numbers.

    The "big" numbers 'commute', so you'll find "nine million six
    billion" and "six billion nine million" are converted to the same
    number.  This is logical but perhaps not conventional grammar.
    Someone might like to add a "strict" keyword to WordNum's
    constructor to outlaw such things, but I'm finished mucking about
    with this code.  The data structure of choice to use for this
    would be an ordered bidict.

Algorithm
---------

    The primary interface is the function call of the WordNum object.
    The single parameter allowed is converted to a string, then
    checked to see if it contains a decimal digit (0, 1, ..., 9).  If
    it does, it's declared to be a number and is converted to a list
    of words describing the number by the WordNum.number() method.
    Otherwise, it's a string containing a set of words describing a
    number; it is converted to the relevant encoded number by the
    WordNum.phrase() method.  If the string contains '/', 'over', or
    'divided by', it's declared to be a fraction.  If it contains the
    radix or 'e', it's a floating point number.  Otherwise, it's an
    integer.

    The conversions between numbers and words are kept in a bidict, a
    data structure derived from a python dictionary, but that requires
    both the keys and values to be unique.  This allows easy access to
    the inverse mapping because the bidict is a one-to-one mapping,
    which is invertible.  These mappings are encapsulated in the Scale
    object, which you can adjust to your tastes, requirements, and
    language.
 
References 
----------
    http://en.wikipedia.org/wiki/Long_and_short_scales
    http://en.wikipedia.org/wiki/Names_of_large_numbers
'''

# Copyright (C) 2014 Don Peterson
# Contact:  gmail.com@someonesdad1

#
#

from __future__ import print_function
import re
import sys
import itertools
import fractions
from bidict import bidict
from string import ascii_letters

class Scale(object):
    '''Provide the facilities to deal with numbers and names in either
    the short or long scale.  For the short scale, 'billion' is equal
    to 1e9; for the long scale, 'billion' is 1e12.  For the short
    scale, trillion/billion is 1e3; for the long scale, it's 1e6.
    '''
    def __init__(self, scale="short"):
        if scale not in ("short", "long"):
            raise ValueError("scale must be 'short' or 'long'")
        self.short = True if scale is "short" else False
        # Dictionaries to do number to word conversions and vice
        # versa.  A bidict makes it easy to get the inverse mapping.
        self.digits2mag = bidict({
            0  : "zero",
            1  : "one",
            2  : "two",
            3  : "three",
            4  : "four",
            5  : "five",
            6  : "six",
            7  : "seven",
            8  : "eight",
            9  : "nine",
        })
        self.mag2digits = self.digits2mag.invert()
        self.small_num2mag = bidict({
            10 : "ten",
            11 : "eleven",
            12 : "twelve",
            13 : "thirteen",
            14 : "fourteen",
            15 : "fifteen",
            16 : "sixteen",
            17 : "seventeen",
            18 : "eighteen",
            19 : "nineteen",
            20 : "twenty",
            30 : "thirty",
            40 : "forty",
            50 : "fifty",
            60 : "sixty",
            70 : "seventy",
            80 : "eighty",
            90 : "ninety",
        })
        self.small_num2mag.update(self.digits2mag)
        self.small_mag2num = self.small_num2mag.invert()
        # Big numbers that depend on the scale.
        self.base = 10**3 if self.short else 10**6
        self.mult = 1000 if self.short else 1
        self.big = {
            2  : "billion",
            3  : "trillion",
            4  : "quadrillion",
            5  : "quintillion",
            6  : "sextillion",
            7  : "septillion",
            8  : "octillion",
            9  : "nonillion",
            10 : "decillion",
        }
        self.big_num2mag = bidict()
        for key, value in self.big.items():
            self.big_num2mag[self.mult*self.base**key] = value
        self.big_num2mag[10**3] = "thousand"
        self.big_num2mag[10**6] = "million"
        self.big_mag2num = bidict(self.big_num2mag).invert()
        # Dictionaries for ordinals
        self.ordinals = {
            1 : "first", 2 : "second", 3 : "third", 4 : "fourth", 5 : "fifth",
            6 : "sixth", 7 : "seventh", 8 : "eighth", 9 : "ninth",
            10 : "tenth", 11 : "eleventh", 12 : "twelfth", 13 : "thirteenth",
            14 : "fourteenth", 15 : "fifteenth", 16 : "sixteenth",
            17 : "seventeenth", 18 : "eighteenth", 19 : "nineteenth",
            20 : "twentieth", 30 : "thirtieth", 40 : "fortieth",
            50 : "fiftieth", 60 : "sixtieth", 70 : "seventieth",
            80 : "eightieth", 90 : "ninetieth",
        }
        self.other_ordinals = {
            "one"      : "first",
            "two"      : "second",
            "three"    : "third",
            "four"     : "fourth",
            "five"     : "fifth",
            "six"      : "sixth",
            "seven"    : "seventh",
            "eight"    : "eighth",
            "nine"     : "ninth",
            "thousand" : "thousandth",
        }
        for i in "mi bi tri quadri quinti sexti septi octi noni deci".split():
            key = i + "llion"
            self.other_ordinals[key] = key + "th"

class WordNum(Scale):
    '''Provides a facility to convert from numbers to their spoken
    English form and back again.
 
    The basic interface is to call the WordNum object as a function
    and pass it an object.  This object will be converted to a string
    and will be interpreted either as an English phrase describing a
    number or as a decimal number.  A phrase is converted to an
    equivalent number (base 10 integer or floating point) and a string
    describing a number is turned into an English phrase.
 
    Examples:
 
        >>> wn = WordNum()
        >>> wm(137)
        one hundred thirty seven
        >>> wm("one hundred thirty seven")
        137
        >>> wm("one hundred thirty seven point five")
        137.5
 
    The constructor takes some keyword parameters:  
        
 
    This object is written to convert numbers to and from English
    phrases.  It may be usable for conversions in other languages if
    their terms and ordering map one-to-one onto English.  If not, you
    can use a derived object and change the needed methods.
    '''
    def __init__(self, scale="short", radix=".", sep=" ", fltype=float):
        '''Keyword parameters:
 
        scale:   must be 'short' or 'long' and determines how larger
        words like 'billion' are interpreted.  In the short scale, one
        billion is 1e9 and in the long scale it is 1e12.  See
        http://en.wikipedia.org/wiki/Long_and_short_scales for more
        information.
 
        radix:  also called the decimal point; it can be either '.' or
        ','.  For a given radix, the other symbol is interpreted as a
        digits separator and it is removed from the string before
        processing.
 
        sep:  separator; this is a string put between the words used
        to describe a number.
 
        fltype:  a floating point type used to return floating point
        numbers.  Defaults to float, python's built-in floating point
        type.  To help minimize floating point conversion issues, you
        might want to set this to use python's decimal.Decimal class.
        The type object must take a string and convert it to a
        floating point number type.
        '''
        super(WordNum, self).__init__(scale)
        if scale not in set(("short", "long")):
            raise ValueError("scale must be 'short' or 'long'")
        if radix not in set((".", ",")):
            raise ValueError("radix must be '.' or ','")
        self.short = True if scale == "short" else False
        self.radix = radix
        self.sep = sep
        self.fltype = fltype
        # regexp to identify numbers
        self.is_num = re.compile(r"\d")
        # regexp to pick apart floating point numbers
        self.fp = re.compile(r'''
            (?ix)               # Allow verbosity; ignore case
            (?P<sgn>[+-]?)      # Optional sign
            (?P<ip>\d*)         # Integer part
            (?P<rad>\%s?)       # Radix
            (?P<fp>\d*)         # Fractional part
            (?P<e>e?)           # Exponent indicator
            (?P<esgn>[+-]?)     # Optional exponent sign
            (?P<exp>\d*)        # Exponent 
        ''' % self.radix)
    def __str__(self):
        scale = "short" if self.short else "long"
        return "WordNum(scale='%s', radix='%s')" % (scale, self.radix)
    def __call__(self, obj):
        '''obj can be a string, integer, or floating point number.  If
        it's a string, it's either an English description of a number
        or a string form of an integer, float, or fraction.
        '''
        s = str(obj).lower()
        return self.number(s) if self.is_num.search(s) else self.phrase(s)
    def normalize(self, s):
        '''Change non-letters to spaces and return a tuple of the
        words making up the number.
        '''
        c = [chr(i) for i in range(256)]
        t = ''.join([i if i in ascii_letters else " " for i in c])
        u = s.translate(t).lower()
        # Replace synonyms
        t = u.split()
        for word, repl in (("oh", "zero"), ("dot", "point"), ("and", "")):
            while word in t:
                t[t.index(word)] = repl
        return [i for i in t if i]
    def number_type(self, s):
        '''Return a tuple (t, type) where type is one of the number
        types of int, float, or fraction, depending on what the string
        s contains.  t will be a list of the lower case form of the
        words in s.
        '''
        t = self.normalize(s)
        u = ' '.join(t)
        if "point" in t:
            return (t, self.fltype)
        elif "over" in t:
            return (t, fractions.Fraction)
        elif "divided by" in u:
            t = u.replace("divided by", "over").split()
            return (t, fractions.Fraction)
        else:
            return (t, int)
    def words_to_fraction(self, s):
        loc = s.index("over")
        numerator = self.words_to_int(s[:loc])
        denominator = self.words_to_int(s[loc + 1:])
        return fractions.Fraction(numerator, denominator)
    def words_to_float(self, s):
        '''Interpret a floating point number, because s (a list of 
        words) contains 'point'.
        '''
        sign = 1
        if "minus" in s:
            if s[0] != "minus":
                raise ValueError("minus isn't first word")
            sign = -1
            s = s[1:]
        dp = s.index("point")
        if not dp:
            s = ["zero"] + s
            dp = 1
        integer_part = abs(self.phrase(' '.join(s[:dp])))
        # Process decimal part
        t = ["0."]
        for word in s[dp + 1:]:
            t.append(str(self.mag2digits[word]))
        return sign*(integer_part + self.fltype(''.join(t)))
    def words_to_int(self, s):
        '''Interpret s, a list of words, as an integer.  Adapted from
        the code at https://github.com/ghewgill/text2num (downloaded
        5 Aug 2014).
        '''
        n, g, h, negative = 0, 0, 0, False
        # h is only used for long scale numbers when there is
        # 'thousand' to the left of a big name like 'billion'.
        for i, word in enumerate(s):
            if word in self.small_mag2num:
                g += self.small_mag2num[word]
            elif not i and word in set(("minus", "negative")):
                negative = True
            elif word == "hundred":
                g *= 100
            elif word == "thousand" and not self.short:
                h = g*1000
                g = 0
            else:
                if word in self.big_mag2num:
                    n += (g + h)*self.big_mag2num[word]
                    g = h = 0
                else:
                    raise ValueError("'%s' is an unknown number" % word)
        total = n + g + h
        return -total if negative else total
    def phrase(self, string):
        '''Convert an English phrase to a number.
        '''
        try:
            s, numtype = self.number_type(string)
            if numtype is self.fltype:
                return self.words_to_float(s)
            elif numtype is fractions.Fraction:
                return self.words_to_fraction(s)
            else:
                return self.words_to_int(s)
        except ValueError:
            raise
        except Exception:
            msg = "'%s' couldn't be converted to number" % string
            raise ValueError(msg)
    def batch(self, iterable, size):
        '''Generator that returns batches of an iterable of desired size.
        Slightly adapted from Raymond Hettinger's entry in the comments to
        http://code.activestate.com/recipes/303279.
        ''' 
        def counter(x):
            counter.n += 1
            return counter.n//size
        counter.n = -1
        for k, g in itertools.groupby(iterable, counter):
             yield g
    def _int(self, s):
        '''s is a list of 1 to 3 digits; return a list of words for
        these digits.  Note that the empty list is returned for ["0"];
        this is because this routine may have to handle the zeros in
        e.g. 123,000,456.
        '''
        n, words = int(''.join(s)), []
        if not n:
            return []
        if not(0 < n < 10**3):
            raise ValueError("Number '%s' not in [1, 999]" % ''.join(s))
        hundreds, rem = divmod(n, 100)
        tens, ones = divmod(rem, 10)
        if hundreds:
            words += [self.small_num2mag[hundreds], "hundred"]
            if s[1:] == ["0"]*2:
                return words
            if rem in self.small_num2mag:
                words += [self.small_num2mag[rem]]
                return words
        if tens:
            words += [self.small_num2mag[10*tens]]
        if ones:
            words += [self.small_num2mag[ones]]
        return words
    def _small(self, s):
        '''s is a list of 1 to 6 digits; return a list of the words
        for such a number.  Most significant digit is first.  This
        routine handles number up to 999999 for long scale and 999 for
        short scale.
        '''
        n, words = int(''.join(s)), []
        if len(s) > 3:
            low = self._int(s[-3:])
            high = self._int(s[:-3])
            return high + ["thousand"] + low
        else:
            return self._int(s)
    def ordinal(self, number):
        '''Converts a number (string or number form) to an ordinal
        number word expression.  Works for positive nonzero integers
        only.  Returns a list of the words describing the ordinal
        number.  
        '''
        n = int(number)
        if n < 1:
            raise ValueError("number must be integer > 0")
        s = str(n)
        # First look for the number in self.ordinals
        if int(s) in self.ordinals:
            return [self.ordinals[int(s)]]
        # Get word form and convert the last word
        words = self.number(s)
        if words[-1] in self.other_ordinals:
            words[-1] = self.other_ordinals[words[-1]]
        return words
    def number(self, Number):
        '''Convert a number Number (a lower case string) to an English
        phrase returned as a list of words.
        '''
        words = []
        try:
            # Remove any grouping characters
            r = "." if self.radix is "," else ","
            s = Number.replace(r, "")
            if "/" in s:
                # Fraction
                num, denom = s.split("/")
                words += self.number(num)
                words += ["over"]
                words += self.number(denom)
            elif self.radix in s or 'e' in s:
                # Float
                if self.radix == ",":
                    s = s.replace(self.radix, ".")
                words = self._float(s)
            else:
                # Handle the case of zero specially because
                # self._int() handles the more general case of a
                # number of zero digits by returning the empty list.
                if not int(s):
                    return ["zero"]
                # Integer.  Group the number's digits into groups of 3
                # for short scale, 6 for long scale.
                negative = True if s[0] == "-" else False
                if negative or s[0] == "+":
                    s = s[1:]
                r = reversed
                g = 3 if self.short else 6
                t = [list(r(list(i))) for i in self.batch(r(s), g)]
                # Decorate with group's power of 10
                t = list(r([(g*i, list(j)) for i, j in enumerate(t)]))
                words, zero = [], set("0")
                if negative:
                    words = ["minus"]
                for e, digits in t:
                    u = set(digits)
                    if u == zero or digits == ["+"]: 
                        continue
                    words += self._small(digits)
                    if e:
                        words += [self.big_num2mag[10**e]]
            return words
        except Exception as ex:
            msg = "'%s' cannot be converted\n  Error = %r" % (Number, ex)
            raise ValueError(msg)
    def _float(self, s):
        '''Convert a set of digits and possible an 'e' character to a
        floating point number in words; return a list of the words.
        '''
        try:
            float(s)
        except Exception:
            raise ValueError("'%s' is an improper float" % s)
        mo, words = self.fp.match(s), []
        if mo is not None:
            # Get the regexp's named groups
            f = mo.group
            if f("ip"):
                words += self.number(f("sgn") + f("ip"))
            if f("rad") and f("fp"):
                words.append("point")
            if f("fp"):
                for digit in f("fp"):
                    words.append(self.digits2mag[int(digit)])
            if f("e"):
                if not f("exp"):
                    raise ValueError("Exponent missing after 'e'")
                if int(f("exp")):
                    words += ["times", "ten", "to", "the"]
                    if f("esgn") == "-":
                        words.append("minus")
                        words += self.number(f("exp"))
                    else:
                        words += self.ordinal(f("exp"))
            if words[-1] == "point":
                words = words[:-1]
            return words
        else:
            raise ValueError("Not a floating point number")

