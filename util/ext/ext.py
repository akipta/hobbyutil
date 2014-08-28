'''
Find all the file extensions used in the directories given on the command
line.

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

import sys, os, getopt, functools, time, glob
from collections import defaultdict


def StreamOut(streams, *s, **kw):
    k = kw.setdefault
    # Process keyword arguments
    sep     = k("sep", "")
    auto_nl = k("auto_nl", True)
    prefix  = k("prefix", "")
    convert = k("convert", str)
    # Streams in the following set get their messages prefaced by the time
    timing  = k("timing", set())
    # Convert position arguments to strings
    strings = map(convert, s)
    # Dump them to the streams
    for stream in streams:
        tm = time.strftime("<%d%b%Y:%H%M%S> ") if stream in timing else ""
        stream.write(''.join((prefix, tm, sep.join(strings))))
        # Add a newline if desired
        if auto_nl:
            stream.write("\n")

logstream, envvar = None, "DEBUG_LOG"
# Open logstream if environment variable DEBUG_LOG is defined.  Set it to
# "wb" for overwriting an existing log file, "ab" for appending to an
# existing log file.
if envvar in os.environ:
    logstream = open("log", os.environ[envvar])
streams = [sys.stdout]
if logstream:
    streams.append(logstream)
out  = functools.partial(StreamOut, streams, timing=set([logstream]))

def Usage(status=1):
    name = sys.argv[0]
    if d["-c"]:
        ci = '''
    -c
        Ignore case differences between extensions.  Thus, .png and
        .PNG will be considered the same extension.
'''[1:-1]
    else:
        ci = '''
    -c
        Assume the extensions are case-insensitive (e.g., as on a
        Windows system).  Use of this option will disable this
        behavior (thus, .png and .PNG will be considered different
        file extensions).
'''[1:-1]

    if d["-C"]:
        col ='''
    -C 
        Don't list in columns (i.e., use one extension per line).
'''[1:-1]
    else:
        col ='''
    -C 
        List the output in columns for a more compact report.
'''[1:-1]
    s = '''
Usage:  {name} [options] dir1 [dir2...]
  Prints out file extensions and their counts used in the files contained
  in the given directories.
 
Options:
{ci}
{col}
    -f 
        Consider the strings input on the command line as the file list
        itself and print the report for that set.
    -h 
        Include Mercurial directories (by default, directories with the
        name '.hg' are skipped.
    -r 
        Recurse into each directory given.
    -s 
        Sort the output by counts.  The output is normally sorted by
        extension.
'''[1:-1]
    out(s.format(**locals()))
    sys.exit(status)

def ParseCommandLine(d):
    d["-c"] = True      # Extension names are case-sensitive
    d["-C"] = False     # Print in columns
    d["-f"] = False     # Command line contains files
    d["-h"] = False     # Include .hg directories
    d["-r"] = False     # Recurse into directories
    d["-s"] = False     # Sort output by counts
    if len(sys.argv) < 2:
        Usage(d)
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "Ccfhrs")
    except getopt.GetoptError as str:
        msg, option = str
        out(msg)
        sys.exit(1)
    for opt in optlist:
        if opt[0] == "-c":
            d["-c"] = not d["-c"]
        if opt[0] == "-C":
            d["-C"] = not d["-C"]
        if opt[0] == "-f":
            d["-f"] = not d["-f"]
        if opt[0] == "-h":
            d["-h"] = not d["-h"]
        if opt[0] == "-r":
            d["-r"] = not d["-r"]
        if opt[0] == "-s":
            d["-s"] = not d["-s"]
    if not args:
        Usage(d)
    return args

def ListInColumns(list, col_width=0, num_columns=0, space_betw=0, truncate=0):
    '''Returns a list of strings with the elements of list (must be 
    strings) printed in columnar format.  Elements of list that won't
    fit in a column either generate an exception if truncate is 0
    or get truncated if truncate is nonzero.  The number of spaces 
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
    # Make sure parameters are integers
    col_width   = int(col_width)
    num_columns = int(num_columns)
    space_betw  = int(space_betw)
    truncate    = int(truncate)
    lines = []
    N = len(list)
    # Get the length of the longest line in the list
    maxlen = 0
    for line in list:
        if len(line) > maxlen:
            maxlen = len(line)
    if maxlen == 0:
        return [""]
    if col_width == 0:
        if os.environ.has_key("COLUMNS"):
            columns = int(os.environ["COLUMNS"]) - 1
        else:
            columns = 80 - 1
        col_width = maxlen
    if num_columns == 0:
        try:
            num_columns = int(columns//maxlen)
        except:
            return [""]
        if num_columns < 1:
            raise UtilityException("A line is too long to display")
        space_betw = 1
    if col_width < 1 or num_columns < 1 or space_betw < 0:
        raise ValueError("Error: invalid parameters")
    if N == 0:
        return [""]
    num_rows = int(N//num_columns + (N % num_columns != 0))
    for row in xrange(num_rows):
        str = ""
        for column in xrange(num_columns):
            ix = int(num_rows*column + row)
            if 0 <= ix <= (N-1):
                if len(list[ix]) > col_width:
                    if truncate:
                        str = str + list[ix][:col_width] + " "*space_betw
                    else:
                        raise UtilityException("Error:  element %d too long" % ix)
                else:
                    str = str + list[ix] + " " * (col_width - len(list[ix])) \
                          + " " * space_betw
        lines.append(str) 
    assert(len(lines) == num_rows)
    return lines

def Reverse(seq):
    '''seq is a list of [a, b] type pairs.  Turn each pair into the form
    [b, a].
    '''
    for i in xrange(len(seq)):
        a, b = seq[i]
        seq[i] = [b, a]
    return seq

def PrintReport(data, d):
    '''data is the defaultdict of counts; d is the options dict.
    '''
    if "" in data:
        del data[""]
    v = data.values()
    if not v:
        # No information to report
        return
    widest_integer = max([len(str(i)) for i in v])
    fmt = "%*d %s"
    items = Reverse([list(i) for i in data.items()])
    if d["-s"]:
        # Sort by count.  
        items.sort()
    else:
        # Sort by extension.
        Reverse(items)
        # We want to sort by the extension, but have the sort be
        # case-insensitive.  To do this, decorate the list with the
        # lower case extension, sort, then remove it.
        items = [[i[0].lower()] + i for i in items]
        items.sort()
        items = [i[1:] for i in items]
        Reverse(items)
    output_data = []
    for i in items:
        output_data.append(fmt % tuple([widest_integer] + i))
    if d["-C"]:
        for i in ListInColumns(output_data):
            out(i.rstrip())
    else:
        for i in output_data:
            out(i)

def NormalizePath(path):
    return path.replace("\\", "/")

def ProcessDirectory(dir, data, d):
    assert os.path.isdir(dir)
    if os.path.split(dir)[1] == ".hg" and not d["-h"]:
        # Ignore Mercurial directories
        return
    dir = NormalizePath(dir)
    ProcessFiles(glob.glob(dir + "/*"), data, d)

def ProcessFiles(files, data, d):
    '''For each file in the list files, classify the extension into
    the data container.
    '''
    for file in files:
        if os.path.isfile(file):
            name, ext = os.path.splitext(file)
            if ext:
                if not d["-c"]:
                    ext = ext.lower()
                data[ext] += 1

if __name__ == "__main__":
    d = {} # Options dictionary
    items, data = ParseCommandLine(d), defaultdict(int)
    for item in items:
        if os.path.isdir(item):
            if d["-r"]:
                # Process directories recursively
                for directory, dirnames, files in os.walk(item):
                    directory = NormalizePath(directory)
                    # Don't process Mercurial directories unless -h
                    # was used on command line
                    if "/.hg" in directory and not d["-h"]:
                        continue
                    ProcessDirectory(directory, data, d)
            else:
                ProcessDirectory(item, data, d)
        else:
            ProcessFiles([item], data, d)
    PrintReport(data, d)
