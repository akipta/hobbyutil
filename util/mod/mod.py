'''
Finds files modified within a specified time frame.

---------------------------------------------------------------------------
Copyright (C) 2011 Don Peterson
Contact:  gmail.com@someonesdad1

                         The Wide Open License (WOL)

Permission to use, copy, modify, distribute and sell this software and its
documentation for any purpose is hereby granted without fee, provided that
the above copyright notice and this license appear in all copies.
THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF
ANY KIND. See http://www.dspguru.com/wide-open-license for more
information.
'''

from __future__ import division
import sys, os, os.path, getopt, functools, time, re


nl = "\n"

picture_extensions = set((
    ".bmp", ".dib", ".emf", ".eps", ".gif", ".ipc", ".ipk", ".j2c", ".j2k",
    ".jif", ".jp2", ".jpeg", ".jpg", ".pbm", ".pct", ".pgm", ".pic", ".png",
    ".ppm", ".ps", ".psp", ".pspframe", ".pspimage", ".pspshape", ".psptube",
    ".svg", ".tif", ".tiff", ".tub", ".xbm", ".xpm",
))

common_files = set((
    "log",
    "tags",
    "z",
    "a",
    "b",
))

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
            stream.write(nl)

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
outs = functools.partial(StreamOut, streams, sep=" ", timing=set([logstream]))
err  = functools.partial(StreamOut, [sys.stderr])

manual = '''\
Usage:  {name} [options] [time [dir [dir2...]]]
  Prints out files that have changed within the specified time.  The time
  specifier is days; if a letter is appended, then that gives the units.
  The units are:
      S   seconds
      M   minutes
      H   hours
      d   days
      w   weeks
      m   months
      y   years
  The search is recursive.  dir defaults to the current directory if not
  given.  time defaults to 1 day if not given.

  Mercurial directories are ignored unless the -m option is given.

Options
    -c
        Ignore commonly-named files (change the script's common_files
        global variable to set the files to ignore).
    -r
        Do not behave recursively.
    -m  
        Do not ignore Mercurial directories.
    -n  
        Negate the sense of the search -- print out files that have NOT
        changed within the indicated period.
    -p
        Ignore picture-type files.
    -x regexp
        Ignore files that match a regexp.  You can have more than one of
        these options.
'''[:-1]

def Usage(status=1):
    name = sys.argv[0]
    out(manual.format(**locals()))
    sys.exit(status)

def ParseCommandLine(d):
    d["-c"] = False
    d["-m"] = False
    d["-n"] = False
    d["-p"] = False
    d["-r"] = False
    d["-x"] = []
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "chmnprx:")
    except getopt.GetoptError as str:
        msg, option = str
        out(msg + nl)
        sys.exit(1)
    for opt in optlist:
        if opt[0] == "-c":
            d["-c"] = True
        if opt[0] == "-h":
            Usage(0)
        if opt[0] == "-m":
            d["-m"] = True
        if opt[0] == "-n":
            d["-n"] = True
        if opt[0] == "-p":
            d["-p"] = True
        if opt[0] == "-r":
            d["-r"] = True
        if opt[0] == "-x":
            d["-x"].append(opt[1])
    if len(args) == 0:
        args = ["1d", "."]
    elif len(args) == 1:
        args.append(".")
    # If we have any regexp's, compile them.
    regexps = d["-x"]
    for i in xrange(len(regexps)):
        try:
            r = re.compile(regexps[i])
            regexps[i] = r
        except Exception:
            msg = "'%s' is a bad regexp" % regexps[i]
            err(msg)
            exit(1)
    return args

def GetTime(timespec):
    '''timespec is a number (integer or floating point) with an optional
    letter suffix.  Convert to seconds.
    '''
    timespec = timespec.strip()
    if not timespec:
        Usage()
    digits = "1234567890"
    suffixes = {"S" : 1, "M" : 60, "H" : 3600, "d" : 24*3600, "w" : 7*24*3600,
        "m" : 365.25/12*24*3600, "y" : 365.25*24*3600}
    last_char = timespec[-1]
    if last_char in digits:
        timespec += "d"
    elif last_char not in suffixes:
        raise ValueError("'%s' is an illegal time suffix" % last_char)
    last_char = timespec[-1]
    t = float(timespec[:-1])*suffixes[last_char]
    return t

def ProcessDirectory(dir, d):
    for root, dirs, files in os.walk(dir):
        root = root.replace("\\", "/")
        components = root.split("/")
        if ".hg" in components and not d["-m"]:
            continue
        ProcessFiles(root, files, d)
        if d["-r"]:
            break

def IgnoreFile(file, d):
    '''If the indicated file is a picture file (indicated by its extension)
    or it matches one of the -x regular expressions, return True.
    Otherwise, return False.

    Note we convert extensions and file names to lower case, so this is
    specific to Windows environments.
    '''
    if d["-c"]:
        name = os.path.split(file)[1].lower()
        if name in common_files:
            return True
    if d["-x"]:
        for r in d["-x"]:
            if r.search(file):
                return True
    if d["-p"]:
        ext = os.path.splitext(os.path.split(file)[1])[1].lower()
        if ext in picture_extensions:
            return True
    return False

def ProcessFiles(root, files, d):
    for file in files:
        file = os.path.join(root, file).replace("\\", "/")
        if file[:2] == "./":
            file = file[2:]
        if IgnoreFile(file, d):
            continue
        try:
            last_change_time = os.stat(file).st_mtime
            if d["-n"]:
                if abs(d["now"] - last_change_time) > d["time sec"]:
                    out(file)
            else:
                if abs(d["now"] - last_change_time) <= d["time sec"]:
                    out(file)
        except Exception:
            pass

def main():
    d = {} # Options dictionary
    args = ParseCommandLine(d)
    d["time sec"] = GetTime(args[0])  # Return time interval in seconds
    d["now"] = time.time()
    for dir in args[1:]:
        ProcessDirectory(dir, d)

main()
