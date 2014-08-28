'''

Wraps a file or stdin to indicated number of columns.  If number of
columns is not given, it will attempt to get the screen width by
reading the COLUMNS environment variable.  If that's not available, 80
is used.  In the program, 1 is subtracted from the columns value to
allow room for the newline.

Note that the script tries to put two spaces after sentences, but the
algorithm isn't perfect; for example, in the sentence fragment "it is
4 p.m. before we finish", there will be two spaces after the period
after the p.m., where only one is wanted.  If this was fixed, then a
sentence ending with 'p.m.' will then only get one.  Thus, you can see
that semantic analysis is a lot harder than syntactical analysis.

---------------------------------------------------------------------------
Copyright (C) 2012 Don Peterson
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

# Abbreviations that should only get one space after themselves
_abbreviations = set((
    "mr", "mrs", "ms", "mme", "st", "ste", "rev", "col", "esq", "no",
    "so", "ea", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k",
    "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x",
    "y", "z", "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug",
    "sep", "sept", "oct", "nov", "dec",
))

def _out(*v, **kw):
    sep = kw.setdefault("sep", " ")
    nl  = kw.setdefault("nl", True)
    stream = kw.setdefault("stream", sys.stdout)
    stream.write(sep.join([str(i) for i in v]))
    if nl:
        stream.write("\n")

def _Error(msg, status=1):
    _out(msg, stream=sys.stderr)
    exit(status)

def _Usage(d, status=1):
    name = sys.argv[0]
    s = '''
Usage:  {name} [options] [file [outfile]]
  Wrap the indicated file (or stdin) to a specified number of columns.
  Use the -c option to specify the columns; otherwise, the COLUMNS
  environment variable is used; if COLUMNS is not defined, then 80 is
  used.  One is subtracted from the columns to allow room for the
  newline.

Options:
    -c n
        Set the number of columns to wrap at to n.
    -h 
        Show a manpage.
'''[1:-1]
    _out(s.format(**locals()))
    sys.exit(status)

def _ParseCommandLine(d):
    d["-c"] = None
    d["on"] = True
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "2c:h")
    except getopt.GetoptError as str:
        msg, option = str
        _out(msg)
        sys.exit(1)
    for opt in optlist:
        if opt[0] == "-c":
            d["-c"] = abs(int(opt[1]))
        if opt[0] == "-h":
            _Usage(d, status=0)
    # If d["-c"] is not set, then get it from the environment or fall
    # back on a fixed value.
    if d["-c"] is None:
        if "COLUMNS" in os.environ:
            d["-c"] = int(os.environ["COLUMNS"]) - 1
        else:
            d["-c"] = 75
    assert isinstance(d["-c"], int) and d["-c"] > 0
    if 0:
        print "Input to script:"
        print "  args =", args
        print "  Options:"
        for i in d:
            print "   ", i, "=", d[i]
        print "-"*20
    return args

def _IsEndOfSentence(word, d):
    '''Return True if it looks like this word must be at the end of a
    sentence.  Note word will be all lowercase.
    '''
    if word in ("a.m.", "p.m."):
        return False
    elif word[-1] in (".", "?", "!"):
        return True
    elif len(word) > 1 and word[-1] in ("'", '"'):
        if word[-2] in (".", "?", "!"):
            return True
    else:
        return False

def _InsertSpace(word, d):
    '''For the word, decide whether to put one or two space characters
    after it.  
    '''
    w, spc = word.lower(), " "
    if _IsEndOfSentence(w, d):
        # This may be the end of a sentence if it's not an
        # abbreviation.  First look for a leading ' or " and remove it
        # before testing for the abbreviation.
        if w and w[0] in ("'", '"'):
            w = w[1:]
        if w and w[-1] in ("'", '"'):
            w = w[1:]
        if w and w[:-1] in _abbreviations:
            return word + spc*1
        else:
            return word + spc*2
    elif w[-1] == ":":
            return word + spc*2
    else:
        return word + spc*1

def Wrap(line, d):
    '''Line is a single string.  Split it on whitespace and wrap it to
    the indicated number of columns in d["-c"].  Return a list of
    strings that make up the line, properly wrapped.

    If you call this as a library routine, you need to define the
    dictionary d with keys of "-c" for the number of columns to wrap
    to and a Boolean "on" that should be True.
    '''
    s = line.strip()
    if not s:
        return []
    elif s.lower() == ".on":
        d["on"] = True
        return []
    elif s.lower() == ".off":
        d["on"] = False
        return []
    if not d["on"]:
        return [line.rstrip()]  # No wrapping
    results, width = [], d["-c"]
    # Get indentation of line so we can maintain it
    indent = 0
    while line[indent] == " ":
        indent += 1
    s = " "*indent
    words = line.split()
    for word in words:
        t = _InsertSpace(word, d)
        if len(s + t) <= width:
            s += t
        else:
            results.append(s)
            s = " "*indent + t
    s = s.rstrip()  # Ensure no extraneous whitespace at end
    results.append(s)
    return results

def _Process(lines, d):
    s = []
    for line in lines:
        t = Wrap(line, d)
        if t:
            s += t + [""]
    if not s[-1]:
        # Don't end with an empty line
        del s[-1]
    return '\n'.join(s)

def _main():
    d = {} # Options dictionary
    args = _ParseCommandLine(d)
    file, outfile = None, None
    if args:
        if len(args) == 1:
            file = args[0]
        elif len(args) == 2:
            file = args[0]
            outfile = args[1]
        else:
            _Error("Too many command line arguments (use -h for manpage")
    lines = open(file).readlines() if file is not None else sys.stdin.readlines()
    stream = open(outfile, "w") if outfile is not None else sys.stdout
    _out(_Process(lines, d), stream=stream)

if __name__ == "__main__":
    _main()
