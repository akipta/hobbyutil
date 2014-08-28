'''
Given a data file containing information about a set of raw materials
that need to be cut into specified lengths and the quantity and
lengths of the number of cut pieces, determine a cutting plan that
indicates how to cut up the raw materials.  See associated
documentation file cut.pdf (get it from
http://code.google.com/p/hobbyutil/ if all you have is the script).

-----------------------------------------------------------------
Copyright (C) 2012 Don Peterson
Contact:  gmail.com@someonesdad1

The Wide Open License (WOL)

Permission to use, copy, modify, distribute and sell this
software and its documentation for any purpose is hereby granted
without fee, provided that the above copyright notice and this
license appear in all source copies.  THIS SOFTWARE IS PROVIDED
"AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF ANY KIND. See
http://www.dspguru.com/wide-open-license for more information.
'''
 
import sys, os, getopt, locale, time
from math import *
from StringIO import StringIO
from collections import namedtuple
from fractions import Fraction
from sig import sig
from odict import odict

    def dbgxx():
        debug.SetDebugger()
except ImportError:
    pass

dbgxx()

class Stock(object):
    '''Act as a stock item.  This is basically an integer, but the
    cut() and use() methods allow the stock to be consumed until it is
    zero.  When cut() and use() are called, the piece to be used is
    added to the self.pieces list.  This allows the Stock object to
    keep track of which pieces were cut from it.
 
    The __cmp__ method is defined to allow these objects to be sorted
    when they're in a list.  Calling len(s) on a stock object returns
    the current length.
    '''
    def __init__(self, length, ikerf=0):
        '''length is an integer length and kerf is an integer width of
        the kerf.
        '''
        if not isinstance(length, (int, long)) or length <= 0:
            raise ValueError("length must be an integer > 0")
        if not isinstance(ikerf, (int, long)) or ikerf < 0:
            raise ValueError("ikerf must be an integer >= 0")
        self.length = length
        self.current_length = length
        self.ikerf = ikerf
        self.pieces = []
    def cut(self, size):
        '''Remove a length of size and the kerf width from our current
        length.
        '''
        if not isinstance(size, (int, long)) or size <= 0:
            raise ValueError("size must be an integer > 0")
        length = self.current_length - size - self.ikerf
        if length < 0:
            raise ValueError("size + ikerf is too large")
        self.current_length = length
        self.pieces.append(size)
    def use(self, size):
        '''Same as cut but does not include a kerf width.  The
        resulting length after subtracting size must be zero.
        '''
        if not isinstance(size, (int, long)) or size <= 0:
            raise ValueError("size must be an integer > 0")
        length = self.current_length - size
        if length:
            raise ValueError("size does not consume remaining length")
        self.current_length = 0
        self.pieces.append(size)
        # Double check that all the pieces and the requisite kerfs
        # sum to the original length (can be different up to one kerf
        # width).
        piece_length = sum(self.pieces) + self.ikerf*(len(self.pieces) - 1)
        diff = self.length - piece_length
        if diff < 0 or diff > self.ikerf:
            raise RuntimeError("Bug in program:  pieces don't sum to length")
    def __str__(self):
        return str(self.current_length)
    def __repr__(self):
        return str(self) + "/" + str(self.length)
    def __cmp__(self, other):
        L = other.current_length if isinstance(other, Stock) else other
        if self.current_length == L:
            return 0
        elif self.current_length < L:
            return -1
        return 1
    def __len__(self):
        return self.current_length

class StockList(list):
    '''Act as a container for stock items; we're basically just a
    list.  The clean() method can be called to remove any stock items
    with a length of zero; they're added to the self.removed list.
    final() will get a list of all the stock items.
    '''
    def __init__(self):
        self.removed = []
    def list(self):
        '''Return as a list of numbers rather than stock objects.
        '''
        return [len(i) for i in self]
    def clean(self):
        '''Find any elements with a len() of zero and move them to the
        self.removed list.
        '''
        for i in range(len(self) - 1, -1, -1):
            if not len(self[i]):
                self.removed.append(self[i])
                del self[i]
    def final(self):
        return self.removed + self
    
    def FindSmallest(self, size, ikerf):
        '''Remove and return the smallest stock item that is either
        equal to size or less than size + ikerf.  If there isn't a
        stock item satisfying this, return None.
 
        To work correctly, this algorithm depends on self being a
        sorted list; the calling routine needs to make sure this is
        true.
 
        The routine returns a tuple (exact, match).  If the match was
        exact, exact is True; otherwise it's false.  If it's None,
        then there was no match.  
        '''
        try:
            # First look for an exact match
            i = self.index(size)
            match = self[i]
            del self[i]
            return True, match
        except ValueError:
            # Not present, so look for the first element that is
            # larger than size + ikerf.
            for i in range(len(self)):
                match = self[i]
                if len(match) >= size + ikerf:
                    del self[i]
                    return False, match
            return None, None

class PiecesList(list):
    '''Act as a container for pieces; we're basically just a
    list.
    '''
    def __init__(self, seq, ikerf):
        self += seq
        self.ikerf = ikerf
    def FindLargest(self, stock_size):
        '''Remove and return the largest piece that is either
        identically equal to stock_size or is the largest in the set
        that is less than stock_size + self.ikerf.  If there isn't a
        piece satisfying this, return (None, None).
 
        To work correctly, this algorithm depends on self being a
        sorted list; the calling routine needs to make sure this is
        true.
 
        The routine returns a tuple (exact, match).  If the match was
        exact, exact is True; otherwise it's False.  If it's None,
        then there was no match.  
        '''
        # First look for an exact match
        try:
            i = self.index(stock_size)
            match = self[i]
            del self[i]
            return True, match
        except ValueError:
            # Not present, so look for the first element that is
            # larger than stock_size + self.ikerf.
            none_found, target_length = -1, len(stock_size) + self.ikerf
            just_over_index, just_equal_index = none_found, none_found
            for i in range(len(self)):
                if self[i] > target_length:
                    just_over_index = i
                    break
                elif self[i] == target_length:
                    just_equal_index = i
                    break
            if just_equal_index != none_found:
                match = self[just_equal_index]
                del self[just_equal_index]
                return False, match
            elif just_over_index != none_found:
                if just_over_index:
                    match = self[just_over_index - 1]
                    del self[just_over_index - 1]
                    return False, match
            return None, None

def ParseCommandLine(d):
    d["-c"] = False
    d["-v"] = False
    d["algorithm"] = 0
    if len(sys.argv) < 2:
        Usage(d)
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "0cdv")
    except getopt.GetoptError as str:
        msg, option = str
        out(msg)
        sys.exit(1)
    for opt in optlist:
        if opt[0] == "-0":
            d["algorithm"] = 0
        if opt[0] == "-c":
            d["-c"] = not d["-c"]
        if opt[0] == "-d":
            dbgxx()
        if opt[0] == "-v":
            d["-v"] = not d["-v"]
    if d["-c"]:
        DumpConfigFileTemplate(d)
        exit(0)
    if len(args) != 1:
        Usage(d)
    return args

def Usage(d, status=1):
    name = sys.argv[0]
    s = '''
Usage:  {name} [options] datafile
  Generate a cutting list for parts that must be cut from lengths of
  raw materials.  The datafile contains the information used to define
  the problem.  The algorithm used is the first fit decreasing
  heuristic, which picks the largest piece which needs to be cut and
  selects the smallest remaining stock piece to cut it from.

  Keywords (x, y are linear dimensions, n, m,... are integers):

    kerf x              Width of kerf
    sigfig n            Number of significant figures in output numbers
    resolution x        Used to convert lengths to integers
    stock = L, n        n pieces of stock with length L are on-hand
    piece = L, n        n pieces of length L need to be cut
    pieces = x, y...    List of lengths to cut

  -c    Print a datafile template to stdout (use in conjunction with 
        -v option to get a verbose template with explanations of each
        item needed).
  -v    Turn verbose printing on (shows the input data).
'''[1:-1]
    out(s.format(**locals()))
    sys.exit(status)

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

def DumpConfigFileTemplate(d):
    if d["-v"]:
        out('''
# Sample configuration file.  Blank lines and content from a '#'
# character to the end of a line are ignored.  You can make
# assignments to convenience variables.  The python math module is in
# scope.  Thus, for example, you could set a variable d2r to a
# constant to convert from degress to radians by the line
#
#    d2r = pi/180
#
# (Note:  all the functions in the math module are in scope, so you
# can write expressions like 29*cos(30*d2r)).  This variable can then
# be used in subsequent lines.  For example, a piece line could
# calculate a length as a function of an angle:
#
#       piece = 2, 29*cos(30*d2r)
#
# Each line must be of the form 'keyword = value'.  The allowed
# keywords are (case is not important):
#
#   * kerf
#   * sigfig
#   * resolution
#   * stock
#   * piece
#   * pieces
#
# The stock and piece lines must be of the form 'keyword = qty, size'.
# qty must be an integer and size can be an expression.  Note that the
# program does not assume anything about the units used to measure the
# pieces, but you'll get meaningful output only if all the keyword
# arguments that are lengths are in consistent units.
#
# In the following items, we'll give a simple problem that should be
# easy to solve mentally.  Run the program on this example data and
# you should see the solution you expect.

    # The kerf keyword is used to define the kerf width of a cut.  It
    # is essentially tacked onto the end of each piece desired as it
    # is cut from a stock piece.  The default value is 0.
kerf = 1

    # The sigfig keyword must define an integer greater than 0.  This
    # determines how many significant figures are given in the decimal
    # output of the script under the "Length" column (it's not used if
    # you specify resolution as a fraction).  It is used to make the
    # interpretation of the lengths straightforward, as the decimal
    # points should all line up when you use the -v option.  The
    # default value is 3.
sigfig = 3

    # The resolution keyword is used to convert the lengths given in
    # the stock and piece lines to integers.  This is done so that the
    # arithmetic is exact and there are no floating point rounding
    # problems.  Each raw length in a piece or stock line is divided
    # by this number and the integer part is taken.  For example,
    # suppose you wanted to work with lengths in inches and you felt
    # that a hundredth of an inch is a sufficient resolution (i.e., a
    # piece length of 1.01 and 1.02 inches are essentially the same in
    # a raw stock context).  Then you'd define resolution to be 0.01.
    # The default value is 1.  The resolution can also be an improper
    # fraction; for example, you could use '1/16' for a one-sixteenth
    # resolution.  If you use a fraction for the resolution, then the
    # lengths will be printed out in appropriate fractions.  Note:  I
    # don't use fractional dimensions, so it's possible that the
    # output isn't as well-tested as it should be.  If you find a bug,
    # please let me know so I can fix it.
resolution = 1

# Note:  kerf, sigfig, and resolution are available as local variables
# after they are defined.

    # The stock keyword defines the length of the raw stock pieces you
    # have on hand.  For our example problem here, we'll assume we
    # have one length of stock that is 100 units long.  The first
    # integer is the number of pieces on-hand and the second number is
    # the length of the stock.
stock = 1, 100

    # The piece keyword's syntax is identical to the stock keyword's.
    # For our example, we'll ask that 9 pieces of length 10 units be
    # cut.  Because the kerf is 1, you can see that we'll wind up
    # cutting 9 pieces 10 units long with a 9 units of kerf wasted.
    # Thus, the total stock consumed will be 9*(10 + 1) = 99 units,
    # leaving a waste of 1 unit.
piece = 9, 10

# The pieces keyword is a convenience for when you have a number of
# different piece lengths.  The form is 
#
#   pieces = n, m, k, ...
#
# n, m, k, etc. can be expressions.
'''[1:].format(**locals()))
    else:
        # Non-verbose form of template
        out('''
sigfig = 3
kerf = 1
resolution = 0.1
stock = 2, 100
piece = 9, 10
pieces = 10, 20, 29, 30

# For this config data, you should get results something like:
# Cutlist ([x] is scrap length for that stock piece)
#   Total scrap = 8.0 (4.0% of total stock)
#   100.0: 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0 [1.0]
#   100.0: 10.0, 20.0, 29.0, 30.0 [7.0]
'''[1:-1].format(**locals()))

def DumpData(data):
    '''Print the contents of the interpreted data file.
    '''
    kerf = sig(data["kerf"])
    ikerf = str(int(data["kerf"]/data["resolution"]))
    resolution = sig(data["resolution"])
    res = float(data["resolution"])
    if "resolution_s" in data and "/" in data["resolution_s"]:
        resolution_s = "= " + data["resolution_s"] + " in original string form"
    else:
        resolution_s = ""
    sigfig = data["sigfig"]
    datafile = data["datafile"]
    tm = time.asctime(time.localtime())
    stock = '''
  %s information:
        Qty           Length          Line number    Integer length
      -------     ---------------     -----------    --------------
'''[1:-1]
    out('''
Input data from file '{datafile}'    
  Time       = {tm}
  kerf       = {kerf} = {ikerf} in integer resolution units
  resolution = {resolution} {resolution_s}
  sigfig     = {sigfig}
'''[1:-1].format(**locals()))
    out(stock % "Stock")
    fmt = "          %-6d  %s    %8d    %18s"
    sig.fit = 15
    sig.dp_position = sig.fit//2
    sl = 0
    for item in data["stock"]:
        linenum, qty, length, ilength = item[:4]
        out(fmt % (qty, sig(length), linenum, format(int(ilength), "n")))
        sl += qty*length
    out(stock % "Piece")
    sm, qt = 0, 0
    for item in data["piece"]:
        linenum, qty, length, ilength = item[:4]
        out(fmt % (qty, sig(length), linenum, format(int(ilength), "n")))
        sm += qty*length
        qt += qty
    sig.fit = 0
    out("  Sum of all stock lengths =", sig(sl, res))
    out("  Sum of all piece lengths = ", sig(sm, res), ", with ", 
        qt, " kerfs = ", sig(sm + data["kerf"]*qt/res, res), sep="")
    di = sl - sm
    dik = di - data["kerf"]*qt/res
    out("  Difference               = ", sig(di*res, res), " (", 
            sig(dik*res, res), " with kerfs)", sep="")

def GetQtyLength(s, vars):
    '''We expect s to be of the form
        qty, length
    or
        qty length
    where both qty and length are python expressions.  vars is a
    dictionary of variables that we'll put into our local namespace;
    note we ignore any exceptions.
    '''
    try:
        for k in vars:
            exec("%s = vars['%s']" % (k, k))
    except Exception:
        pass
    qty, length = s.split(",")
    qty = int(eval(qty, globals(), locals()))
    length = float(eval(length, globals(), locals()))
    return qty, length

def GetPieces(s):
    '''s is of the form 'n, m, ...' or 'n m ...'.  Split into numbers
    and return as a list.
    '''
    f, lengths = s.replace(",", " ").split(), []
    for i in f:
        lengths.append(float(eval(i)))
    return lengths

def ReadDataFile(datafile):
    '''Return a dictionary containing the information in the data
    file.  The stock and piece elements will be lists of named tuples
    containing the following information:
        x.linenum = 1-based line number of data file (integer)
        x.qty     = quantity have or needed of this length
        x.len     = length of piece (float)
        x.ilen    = length of piece in resolution units (integer)
    '''
    nt, localvars = namedtuple("Data", "linenum qty len ilen"), {}
    d = {  # This is the dictionary we'll return.
        "kerf"       : 0,
        "sigfig"     : 4,
        "resolution" : 1,
        "stock"      : [],
        "piece"      : [],
    }
    sig.digits = d["sigfig"]
    for i, line in enumerate(open(datafile).readlines()):
        line, linenum = line.strip(), i + 1
        if not line or line[0] == "#":  # Ignore blank lines & comments
            continue
        # Remove everything from a comment character to the end of
        # line
        loc = line.find("#")
        if loc != -1:
            line = line[:loc].strip()
            if not line:
                continue
        err = ""
        try:
            kw, value = line.split("=")
            kw, value = kw.strip().lower(), value.strip()
            if kw == "kerf":
                d["kerf"] = float(eval(value, globals(), localvars))
                localvars["kerf"] = d["kerf"]
                if d["kerf"] < 0:
                    err = "kerf must be >= 0"
                    raise Exception()
            elif kw == "resolution":
                d["resolution_s"] = value
                # We allow the resolution to be a fraction; if it's
                # used, it must be an improper fraction, not a mixed
                # fraction expression.  However, it wouldn't be very
                # difficult to add this feature if you wanted it.
                if "/" in value:
                    num, denom = value.split("/")
                    d["resolution"] = Fraction(int(num), int(denom))
                    sig.mixed = True  # Force sig to use mixed fractions
                else:
                    d["resolution"] = float(eval(value, globals(), localvars))
                localvars["resolution"] = d["resolution"]
                if d["resolution"] <= 0:
                    err = "resolution must be > 0"
                    raise Exception()
            elif kw == "sigfig":
                d["sigfig"] = int(eval(value, globals(), localvars))
                localvars["sigfig"] = d["sigfig"]
                if d["sigfig"] < 1:
                    err = "sigfig must be integer > 0"
                    raise Exception()
                sig.digits = d["sigfig"]
            elif kw == "stock":
                err = "Needs to have quantity and length"
                qty, length = GetQtyLength(value, localvars)
                if length <= 0:
                    err = "length must be > 0"
                    raise Exception()
                if qty < 0:
                    err = "qty must be > 0"
                    raise Exception()
                L = int(length/d["resolution"])
                d["stock"].append(nt(linenum, qty, length, L))
            elif kw == "piece":
                err = "Needs to have quantity and length"
                qty, length = GetQtyLength(value, localvars)
                if length <= 0:
                    err = "length must be > 0"
                    raise Exception()
                if qty < 0:
                    err = "qty must be > 0"
                    raise Exception()
                L = int(length/d["resolution"])
                d["piece"].append(nt(linenum, qty, length, L))
            elif kw == "pieces":
                pieces = GetPieces(value)
                for piece in pieces:
                    L = int(piece/d["resolution"])
                    if L <= 0:
                        err = "piece length must be > 0"
                        raise Exception()
                    d["piece"].append(nt(linenum, 1, piece, L))
            else:
                # It's a variable definition; add to localvars
                localvars[kw] = eval(value, globals(), localvars)
        except Exception:
            msg = "Line %d in file '%s' improper:\n  '%s'\n  %s" % (linenum, 
                datafile, line, err)
            Error(msg)
    d["ikerf"] = int(d["kerf"]/d["resolution"])
    # Validate the information
    if not d["stock"]:
        Error("No stock lines in data file.")
    if not d["piece"]:
        Error("No piece lines in data file.")
    pieces, stock, total_pieces, total_stock = GetParts(d)
    if max(pieces) > max(stock):
        Error("At least one piece is longer than the longest stock piece")
    # Add the number of pieces times the kerf width to get the total
    # stock length actually needed
    total_pieces += d["kerf"]*len(pieces)
    # If total stock length available is less than the amount needed
    # for the parts, it's a problem that can't be solved.
    if total_pieces > total_stock:
        krf = sig(d["kerf"])
        res = float(d["resolution"])
        ts = total_stock*res
        tp = total_pieces*res
        sl = stock.list()
        sl.sort()
        stk = List([sig(i*res, res) for i in sl])
        pieces.sort()
        pcs = List([sig(i*res, res) for i in pieces])
        psum = sig(sum(pieces)*res, res)
        out('''
Not enough stock to cut the required pieces:
    Pieces = {pcs} (sum = {psum})
    Stock  = {stk}
    Total stock length = {ts}
    Total piece length = {tp} (including kerf {krf} for each piece)
'''[1:-1].format(**locals()))
        exit(1)
    d["localvars"] = localvars
    return d

def GetParts(data):
    '''Return lists of the stock items and pieces needed and their
    sums.
    '''
    ikerf = data["ikerf"]
    pieces = []
    for piece in data["piece"]:
        for i in range(piece.qty):
            # Note we do NOT add in the kerf length
            pieces.append(piece.ilen)
    stocklist = StockList()
    for item in data["stock"]:
        for i in range(item.qty):
            stocklist.append(Stock(item.ilen, ikerf))
    sl = sum([len(i) for i in stocklist])
    return pieces, stocklist, sum(pieces), sl

def List(s):
    '''Convert a list to a string and remove apostrophes and square
    brackets.
    '''
    return str(s).replace("[", "").replace("]", "").replace("'", "")

def FailureReport(algorithm_name, piece, stock, pieces, data):
    S = StringIO()
    out(algorithm_name, "couldn't find solution", stream=S)
    res = float(data["resolution"])
    starting_pieces, starting_stock, tp, ts = GetParts(data)
    starting_pieces.sort()
    starting_stock.sort()
    out("  Total stock len  =", sig(ts*res, res), stream=S)
    out("  Total piece len  =", sig(tp*res, res), stream=S)
    if 0:
        s = [sig(i*res, res) for i in starting_stock.list()]
        out("  Starting stock   =", List(s), stream=S)
        s = [sig(i*res, res) for i in starting_pieces]
        out("  Starting pieces  =", List(s), stream=S)
    s = [sig(i*res, res) for i in stock.list()]
    out("  Remaining stock  =", List(s), stream=S)
    p = pieces + [piece]
    p.sort()
    s = [sig(i*res, res) for i in p]
    out("  Remaining pieces =", List(s), stream=S)
    out("  Kerf =", sig(data["kerf"]*res, res), stream=S)
    return S.getvalue()

def SuccessReport(title, stock, data):
    '''Return a string representing the report.
    '''
    S = StringIO()
    dummy1, dummy2, total_pieces, total_stock = GetParts(data)
    # It's important to have resolution as a float so it can work as a
    # template for rounding (otherwise, having it be an integer like 1
    # you can wind up only showing 1 significant figure).
    res, ikerf = data["resolution"], data["ikerf"]
    sig.fit = 0
    s = " ([x] is scrap length, {n} is count)"
    s += "  Kerf = " + sig(data["kerf"], res)
    out(title + s, stream=S)
    remain = sum([len(i) for i in stock])
    out("  Total scrap =", sig(remain*res, res),
    nl=False, stream=S)
    out(" (", sig(100*remain/total_stock, float(res)), "% of total stock)", 
        sep="", stream=S)
    # Print out the cut list
    indent = " "*2
    d = odict()
    for i in stock.final():
        p = i.pieces
        if not p:
            scrap = sig(i.length*res, res)
            s = indent + scrap + "%s: [" + scrap + "]"
            if s in d:
                d[s] += 1
            else:
                d[s] = 1
        else:
            p.sort()
            pcs = [sig(j*res, res) for j in p]
            pcs = List(pcs)
            # Get the length used by the n pieces and n-1 cuts.  If it
            # exactly equals the stock length, we'll use it.
            # Otherwise, we need to add in one more kerf for the last
            # cut.
            L = sum(p) + ikerf*(len(p) - 1)
            if L != i.length:
                L += ikerf
            scrap = sig((i.length - L)*res, res)
            s = (indent + sig(i.length*res, res) + "%s: " + pcs + 
                 " [%s]" % scrap)
            if s in d:
                d[s] += 1
            else:
                d[s] = 1

    for i in d:
        if d[i] == 1:
            s = i % ""
        else:
            s = i % ("{%d}" % d[i])
        out(s, stream=S)
    return S.getvalue()

def Algorithm0(key, data, incl_name=False):
    '''Get largest needed piece and find the smallest chunk of stock
    that it can be cut from.  Cut and return stock to stocklist and
    resort.  Repeat until all pieces are consumed or no stock piece is
    long enough.
 
    Put the results in a dictionary under the data dictionary.
 
    The re-sorting of the stock array will be fast because only one
    piece is potentially out of place (we put it at the beginning of
    the array, as it will be a short piece).
    '''
    pieces, stock, total_pieces, total_stock = GetParts(data)
    res, ikerf, d = data["resolution"], data["ikerf"], {}
    stock.sort()
    pieces.sort()
    while pieces:
        largest_piece = pieces.pop()
        exact, stockpiece = stock.FindSmallest(largest_piece, ikerf)
        if exact is None:
            d["solved"] = False
            d["report"] = FailureReport(key, largest_piece, stock, 
                pieces, data)
            d["failed_for_piece"] = largest_piece
            d["stock"] = stock
            d["pieces"] = pieces
            data[key] = d
            return
        if exact:
            stockpiece.use(largest_piece)
        else:
            stockpiece.cut(largest_piece)
        stock.insert(0, stockpiece)
        stock.clean()
        stock.sort()
    d["solved"] = True
    title = "Cutlist (%s)" % key if incl_name else "Cutlist"
    d["report"] = SuccessReport(title, stock, data)
    # Get scrap fraction
    remain = sum([len(i) for i in stock])
    d["scrap_fraction"] = remain/total_stock
    data[key] = d

if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, '')
    d = {} # Options dictionary
    datafile = ParseCommandLine(d)[0]
    data = ReadDataFile(datafile)
    data["datafile"] = datafile
    sig.digits = data["sigfig"]
    if d["-v"]:
        DumpData(data)
    key = "algorithm0"
    Algorithm0(key, data)
    out(data[key]["report"], nl=False)
