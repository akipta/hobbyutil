'''
Provides a function GetNumber that continues to prompts the user for a
number until an acceptable number is gotten.  The number can contain
an optional physical unit string if desired.

Also provides a function ParseUnit(s) for getting and returning a
number and its physical unit.
'''
 
# Copyright (C) 2010 Don Peterson
# Contact:  gmail.com@someonesdad1
 
#
#

import sys

from pdb import set_trace as xx
import debug
if 0:
    debug.SetDebugger()

have_unc = False
try:
    from uncertainties import ufloat
    have_unc = True
except ImportError:
    pass

if sys.version_info[0] == 3:
    _get_input = input
    import io
    sio = io.StringIO
else:
    from StringIO import StringIO as sio
    _get_input = raw_input

def GetNumber(prompt_msg, **kw):
    '''General-purpose routine to get a number (integer or float
    [default]) from the user with the prompt msg:
 
        num_float = GetNumber(prompt_msg)
        num_int   = GetNumber(prompt_msg, numtype=int)
   
    If you wish to restrict the allowed values of the number, use the
    following keyword arguments (default values are in square
    brackets):
 
        numtype     Number type [float].  Use int if you want the 
                    number to be an integer.  You can use a number
                    class as long as it obeys the required ordering
                    semantics and the constructor returns a number
                    object that raises a ValueError if the
                    initializing string is of improper form.  For an
                    example, see the use of mpmath's mpf numbers in
                    the unit tests.
 
        default     Default value.  This value will be returned if 
                    the user just presses the return key when prompted.
 
        low         Lowest allowed value.  [None]
 
        high        Highest allowed value.  [None]
 
        low_open    Boolean; if True, then the low end of the acceptance
                    interval is open.  [False]
 
        high_open   Boolean; if True, then the high end of the acceptance
                    interval is open.  [False]
 
        invert      If true, the value must be in the complement interval.
                    This is used to allow numbers except those in a
                    particular range.  See note below.
 
        outstream   Stream to print messages to.  [stdout]
 
        instream    Stream to get input from (intended for unit tests).
 
        prefix      Prefix string for error messages 
                        ["Error:  must have "]
        
        use_unit    If true, allows a unit to be included in the string.
                    The return value will be a tuple of (number,
                    unit_string).  [False]
 
        allow_quit  If true, "Q" or "q" quits the program.  [True]
 
        inspect     If not None, it's a string that should be
                    inspected to see if it meets the requirements.  If
                    it does, True will be returned; otherwise, False
                    is returned.

        vars        Dictionary to use as locals to evaluate
                    expressions.
 
    For programming ease, any errors in the keyword values will cause a
    SyntaxError exception.  Other exceptions are likely because of my
    programming mistakes.
 
    Note:  if you call
 
        GetNumber("", low=a, high=b)
 
    the number returned will be the number in the closed interval [a, b].
    If you make the same call but with invert set to True
 
        GetNumber("", low=a, high=b, invert=True)
 
    then the returned number must lie in the union of the open intervals
    (-inf, a) and (b, inf); this set of numbers is the complement of the
    previous call's.  If you make the call
 
        GetNumber("", low=a, high=b, low_open=True, high_open=True), the
 
    number returned will be in the open interval (a, b).  If this is
    inverted by setting invert to True as in
 
        GetNumber("", low=a, high=b, low_open=True, 
                  high_open=True, invert=True)
 
    then you'll get a number returned in the union of the half-closed
    intervals (-inf, a] and [b, inf).  A programmer might be confused
    by the fact that the intervals were half-closed, even though the
    settings low_open and high_open were used, implying the programmer
    wanted open intervals.  The way to look at this is to realize that
    if invert is True, it changes an open half-interval to a closed
    half-interval.  I chose to make the function behave this way
    because it's technically correct.  However, if this behavior is
    not to your liking, it's easy to change by changing the
    conditional statements in the conditionals dictionary.  (I debated
    as to whether I should make this function an object instead; then
    this could be done by subclassing rather than changing the
    function.  But the convenience of a simple function won out.)
    '''
    outstream  = kw.get("outstream", sys.stdout)
    instream   = kw.get("instream", None)
    numtype    = kw.get("numtype", float)
    default    = kw.get("default", None)
    low        = kw.get("low", None)
    high       = kw.get("high", None)
    low_open   = kw.get("low_open", False)
    high_open  = kw.get("high_open", False)
    inspect    = kw.get("inspect", None)
    invert     = kw.get("invert", False)
    prefix     = kw.get("prefix", "Error:  must have ")
    use_unit   = kw.get("use_unit", False)
    allow_quit = kw.get("allow_quit", True)
    vars       = kw.get("vars", {})
    Debug      = kw.get("Debug", None)
    # If the variable Debug is defined and True, then we
    # automatically return the default value.
    if Debug:
        return default
    if (low is not None) and (high is not None):
        if low > high:
            raise ValueError("low must be <= high")
        if default is not None and not (low <= numtype(default) <= high):
            raise ValueError("default must be between low and high")
    if invert and low is None and high is None:
        raise ValueError("low and high must be defined to use invert")
    if inspect is not None and not isinstance(inspect, str):
        raise ValueError("inspect must be a string")
    out = outstream.write
    # The following dictionary is used to get conditionals for testing the
    # values entered by the user.  If a set of keywords is not in this
    # dictionary's keys, then it is considered a syntax error by the
    # programmer making a call to this function.  This dictionary is used
    # to both check the conditions as well as provide an error message back
    # to the user.
    conditionals = {
      # low     high   low_open  high_open  invert
        (True,  False, False,    False,     False): "x >= low",
        (True,  False, True,     False,     False): "x > low",
        (True,  False, False,    False,     True):  "x < low",
        (True,  False, True,     False,     True):  "x <= low",
        (False, True , False,    False,     False): "x <= high",
        (False, True , False,    True,      False): "x < high",
        (False, True , False,    False,     True):  "x > high",
        (False, True , False,    True,      True):  "x >= high",
        (True,  True , False,    False,     False): "low <= x <= high",
        (True,  True , True,     False,     False): "low < x <= high",
        (True,  True , False,    True,      False): "low <= x < high",
        (True,  True , True,     True,      False): "low < x < high",
        (True,  True , False,    False,     True ): "x < low or x > high",
        (True,  True , True,     False,     True ): "x <= low or x > high",
        (True,  True , False,    True,      True ): "x < low or x >= high",
        (True,  True , True,     True,      True ): "x <= low or x >= high",
    }
    unit_string = ""
    while True:
        if inspect is None:
            out(prompt_msg)
            if default is not None:
                out(" [" + str(default) + "] ")
            if instream is not None:
                s = instream.readline()
                if not s:
                    if default is None:
                        # This should only be seen during testing.
                        raise RuntimeError("Empty input!")
                    else:
                        if use_unit:
                            return (numtype(default), "")
                        else:
                            return numtype(default)
            else:
                s = _get_input().strip()
        else:
            s = inspect
        if not s:
            if default is None:
                raise ValueError("Default value not defined")
            else:
                if inspect is not None:
                    return True
                if use_unit:
                    return (numtype(default), "")
                else:
                    return numtype(default)
        if len(s) == 1 and s in "qQ" and allow_quit:
            exit(0)
        # Check to see if number contains a unit
        if use_unit:
            number_string, unit_string = ParseUnit(s)
            s = number_string
        try:
            # Note the use of eval lets the user type expressions in.
            # The math module's symbols are in scope.
            x = numtype(eval(s, vars))
        except ValueError:
            if inspect is not None:
                return False
            if numtype == int:
                out("'%s' is not a valid integer\n" % s)
            else:
                out("'%s' is not a valid number\n" % s)
        else:
            if low is None and high is None:
                if inspect is not None:
                    return True
                if use_unit:
                    return (x, unit_string)
                else:
                    return x
            # Check if this number meets the specified conditions; if it
            # does, return it.  Otherwise, print an error message on the
            # output stream and re-prompt the user.
            c = (low is not None, high is not None, low_open, high_open, invert)
            if c not in conditionals:
                # Programmer mistake
                raise ValueError('''Bad set of parameters to GetNumber:
    low       = {low}
    high      = {high}
    low_open  = {low_open}
    high_open = {high_open}
    invert    = {invert}
For example, low and high must not be None.'''.format(**locals()))
            condition = conditionals[c]
            if not eval(condition):
                if inspect is not None:
                    return False
                # Test failed, so send error message to user
                condition = condition.replace("x", "number")
                condition = prefix + condition 
                condition = condition.replace("high", "{high}")
                condition = condition.replace("low", "{low}")
                out(condition.format(**locals()) + "\n")
                # If instream is defined, we're testing, so just return.
                if instream is not None:
                    return
                continue
            # Got a good number, so return it
            if inspect is not None:
                return True
            if use_unit:
                return (x, unit_string)
            else:
                return x

def ParseUnit(s):
    '''Assume the string s has a unit and possible SI prefix appended
    to the end, such as '123Pa', '123 Pa', or '1.23e4 Pa'.  Remove the
    unit and prefix and return the tuple (num, unit).  Note that two
    methods are used.  First, if the string contains one or more space
    characters, the string is split on the space and the two parts are
    returned immediately; an exception is thrown if there are more
    than two portions.  The other method covers the case where the
    unit may be cuddled against the number.
    '''
    if " " in s:
        f = s.split()
        if len(f) != 2:
            raise ValueError("'%s' must have only two fields" % s)
        return f
    # The second method is done by reversing the string and looking for
    # unit characters until a character that must be in the number is
    # found.  Note this means that digit characters cannot be in the unit.
    unit, num, num_chars, done = [], [], set("1234567890."), False
    for i in reversed(s):
        if done:
            num.append(i)
            continue
        if i in num_chars:
            num.append(i)
            done = True
        else:
            unit.append(i)
    return (''.join(reversed(num)), (''.join(reversed(unit))).strip())

def ParseUnitString(x, allowed_units, strict=True):
    '''This routine will take a string x and return a tuple (prefix,
    unit) where prefix is a power of ten gotten from the SI prefix
    found in s and unit is one of the allowed_units strings.
    allowed_units must be a sequence or container.  Note things are
    case-sensitive.  prefix will either be a float or an integer.
 
    The typical use case is where ParseUnit() has been used to
    separate a number and unit.  Then ParseUnitString() can be used to
    parse the returned unit string to get the SI prefix actual unit
    string.  Note parsing of composite units (such as m/s) must take
    place outside this function.
 
    If strict is True, then one of the strings in allowed_units must
    be anchored at the right end of s.  If strict is False, then the
    strings in allowed_units do not have to be present in s; in this
    case, (1, "") will be returned.
    '''
    si = {"y"  : -24, "z":-21, "a":-18, "f":-15, "p":-12, "n":-9, "u":-6, 
        "m":-3, "c":-2, "d":-1, "" : 0, "da": 1, "h": 2, "k": 3, "M": 6, 
        "G": 9, "T":12, "P":15, "E":18, "Z":21, "Y":24}
    s = x.strip()  # Remove any leading/trailing whitespace
    # See if s ends with one of the strings in allowed_units
    unit = ""
    for u in allowed_units:
        u = u.strip()
        # The following can be used if a unit _must_ be supplied.
        # However, it's convenient to allow for a default unit, which
        # is handled by the empty string for the unit.
        #if not u:
        #    raise ValueError("Bad unit (empty or all spaces)")
        if u and s.endswith(u):
            unit = u
            break
    if not unit:
        if strict:
            raise ValueError("'%s' did not contain an allowed unit" % x)
        else:
            return (1, "")
    else:
        # Get right index of unit string
        index = s.rfind(unit)
        if index == -1:
            raise Exception("Bug in ParseUnitString() routine")
        prefix = s[:index]
        if prefix not in si:
            raise ValueError("'%s' prefix not an SI prefix" % prefix)
        return (10**si[prefix], unit)

