'''
This module defines the Tree() function.  This function will return 
a list of strings that represent the directory tree for the directory
passed into the function.  The calling syntax is:

    Tree(dir, indent, leading_char)

The variable indent controls how much each subdirectory is indented
on each line.  The variable leading_char sets the leading character
in the list; '|' might not be a bad choice.

If you call the module as a script, it will print the tree to stdout
for the directory you pass in on the command line (defaults to '.').

---------------------------------------------------------------------------
Copyright (C) 2005 Don Peterson
Contact:  gmail.com@someonesdad1

                         The Wide Open License (WOL)

Permission to use, copy, modify, distribute and sell this software and its
documentation for any purpose is hereby granted without fee, provided that
the above copyright notice and this license appear in all source copies.
THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF
ANY KIND. See http://www.dspguru.com/wide-open-license for more
information.
'''

import sys, os, os.path, re

d = {}  # Options dictionary

pyver = sys.version_info[0]
if pyver == 3:
    raise RuntimeError("This script won't work under python 3")

def GetSizesInMB(dirname, files):
    size, error, scale = 0, False, 1e6
    for file in files:
        try:
            s = os.stat(os.path.join(dirname, file))
            size += s.st_size
        except Exception:
            error = True
    ratio = size/scale
    if ratio >= d["-t"]:
        s = ("%.2g" % ratio) + "M"
        if s[0] == "0":
            s = s[1:]
        s = "\t" + s 
        if error:
            s += "*"
    else:
        s = ""
    return s

def visit(mydirlist, dirname, files):
    # Append the directory name to the list mydirlist if appropriate
    if d["-s"]:
        # Decorate this directory with the sizes of its files in MB
        dirname += GetSizesInMB(dirname, files)
    if not (d["-m"] and "\\.hg" not in dirname):
        return
    else:
        mydirlist.append(dirname.replace("\\", "/"))

def Tree(dir, indent=4, leading_char="|"):
    mydirlist = []
    # walk calls visit with args (mydirlist, dirname, name) for each
    # directory in the tree encountered at dir.  visit appends the
    # directory name if not a Mercurial directory and decorates it
    # with size in MB if appropriate.  mydirlist will return as a list of
    # directories visited in depth-first order.
    os.path.walk(dir, visit, mydirlist)
    mydirlist.sort()
    head = re.compile("^" + dir)
    indent_str = leading_char +  " " * (indent - 1)
    # Decorate the directory list by indenting according to how many
    # '/' characters are in the name.  Leave first entry alone because 
    # it's the original directory we entered (i.e., the parameter
    # dir).
    decorations = []
    for directory in mydirlist[1:]: 
        if directory == ".":
            continue
        # Remove the leading dir string
        normalized = head.sub("", directory)
        # Split the directory path into components; we only want the
        # last directory, as that's what gets decorated.
        fields = normalized.split("/")
        count = len(fields) - 1 if dir != "/" else len(fields)
        name_to_decorate = fields[-1]
        if name_to_decorate and (not d["-d"] or count <= d["-d"]):
            decorations.append(indent_str*count + name_to_decorate)
    return [dir] + decorations

if __name__ == "__main__":
    import sys, getopt, functools
    nl = "\n"

    def StreamOut(stream, *s, **kw):
        k = kw.setdefault
        # Process keyword arguments
        sep     = k("sep", "")
        auto_nl = k("auto_nl", True)
        prefix  = k("prefix", "")
        convert = k("convert", str)
        # Convert position arguments to strings
        strings = map(convert, s)
        # Dump them to the stream
        stream.write(prefix + sep.join(strings))
        # Add a newline if desired
        if auto_nl:
            stream.write(nl)
    out  = functools.partial(StreamOut, sys.stdout)

    def Usage(status=1):
        name = sys.argv[0]
        char = d["-c"]
        size = d["-t"]
        s = '''Usage:  {name} [options] dir [dir2...]
  Print a directory tree for each directory given on the command line.
  Mercurial directories are ignored by default.

  Options:
    -c x    Set the leading character for the trees.  Defaults to 
            '{char}'.
    -d n    Limit tree depth to n (default is to show all of tree).
    -m      Include Mercurial directories (.hg).
    -s      Decorate each directory with the size of its files in MB.
            The separation character is a tab.
    -t n    Threshold size is n MB (default {size}).  Directories with
            a total size less than this won't have the size number printed.
'''
        out(s.format(**locals()))
        sys.exit(status)

    def ParseCommandLine():
        global d
        d["-c"] = "|"       # Leading character
        d["-d"] = 0         # Depth limit
        d["-m"] = True      # Ignore Mercurial directories
        d["-s"] = False     # Decorate with size in MB
        d["-t"] = 0.1       # Threshold in MB for printing size
        if len(sys.argv) < 2:
            Usage()
        try:
            optlist, args = getopt.getopt(sys.argv[1:], "c:d:hmst:")
        except getopt.GetoptError as str:
            msg, option = str
            out(msg + nl)
            sys.exit(1)
        for opt in optlist:
            if opt[0] == "-c":
                d["-c"] = opt[1]
            if opt[0] == "-d":
                d["-d"] = int(opt[1])
            if opt[0] == "-h":
                Usage(0)
            if opt[0] == "-m":
                d["-m"] = False
            if opt[0] == "-s":
                d["-s"] = True
            if opt[0] == "-t":
                try:
                    d["-t"] = float(opt[1])
                except ValueError:
                    err("'%s' is not a valid floating point number" % opt[1])
                    exit(1)
        if not len(args):
            Usage()
        return args

    def main():
        args = ParseCommandLine()
        char = d["-c"]
        for dir_to_process in args:
            for dir in Tree(dir_to_process, leading_char=char):
                out(dir)

    main()
