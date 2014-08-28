'''
Utility to show details of changes in a Mercurial repository.  Use -h
option to print usage information.  This script doesn't really do
anything you can't do with an 'hg log' command, but it just makes
things a bit more compact and convenient.  

To use this script, you must change the global variable hg to point to
your Mercurial's hg command.

Here are some examples of use that give a flavor for what the script
does.  I keep many of my python utilities and modules that I've
written in d:/p/pylib on my Windows box (currently, this is around 400
python scripts and modules).  When I'm working in a subdirectory,
sometimes I want to see the change history of some of the files in the
respository; this is done by the command

    python delta.py 

which will show a list of the decimal change numbers associated with
each file in the repository in the current directory:

    gen.py: 176
    plot.py: 97
    reg.py: 257 229 218 146 145 144 143 142
    stats.py: 309 108 95
    xfm.odt: 176

This format lets me quickly look at e.g. visual diffs of the various
revisions or the log information to find the changes I'm interested
in.  I can instead get the data with dates:

    python delta.py -d

yields

    gen.py: 26Jan12
    plot.py: 7May11
    reg.py: 26Apr12 15Mar12 27Feb12 9Sep11 9Sep11 9Sep11 9Sep11 9Sep11
    stats.py: 19Nov12 1Jul11 4May11
    xfm.odt: 26Jan12

The listing of the revision numbers or dates is given in most-recent
first; the -e option can reverse this order.

If I instead give one or more file names on the command line, then the
revision information is only printed for those files:

    python delta.py gen.py xfm.test/simple_linear_regression/0readme

yields
    
    gen.py: 176
    xfm.test/simple_linear_regression/0readme: 145

Note the 0th revision is not included in the output (this is usually
the place where the file was introduced into the repository).  If you
want it included, use the -0 option.

The -r and -R options cause output to be given for all the files in
the repository (filenames beginning with '.' are ignored unless the -a
option is used).  The -R option gives the filenames as absolute paths
so e.g. further processing by a script could be done if desired.

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

import sys, os, getopt, functools, time
from collections import defaultdict
import subprocess

from pdb import set_trace as xx
if 0:
    import debug
    debug.SetDebugger()

nl = "\n"

days = set(("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"))
months = set(("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"))

# Set this to the location of your Mercurial command
hg = "d:/bin/TortoiseHg104/hg.exe"
hg = "/usr/bin/hg"

def out(*v, **kw):
    sep = kw.setdefault("sep", " ")
    use_nl  = kw.setdefault("nl", True)
    stream = kw.setdefault("stream", sys.stdout)
    stream.write(sep.join([str(i) for i in v]))
    if use_nl:
        stream.write(nl)

def Usage(d, status=1):
    name = os.path.split(sys.argv[0])[1]
    s = '''
Usage:  {name} [options] [file1 [file2...]]
  Show the revision numbers where changes were made in the files of
  the current directory that are in a Mercurial repository.  With no
  file given on the command line, an alphabetized list of all the
  files in the current directory is given with the revision numbers
  where that file changed.  If one or more files are given, then the
  output is only for those files.

Options:
    -0 
        Don't ignore revision 0.
    -a 
        Print all files (files beginning with '.' are not normally
        included).
    -D  
        Include files that have been deleted (normally these are not
        shown).
    -d 
        Show revision date instead of revision number.
    -e 
        Show earliest revision numbers first.  The normal output is 
        to have the latest revision numbers first.
    -l 
        Long listing for the revisions (date and description).
    -r 
        Show all the files in the Mercurial repository rather than
        just the current directory.  Note the paths given are relative
        to the repository's root directory, not relative to the
        current working directory.
    -R
        Same as -r, but make the paths absolute.
'''[1:-1]
    out(s.format(**locals()))
    sys.exit(status)

def ParseCommandLine(d):
    d["-0"] = False         # Don't ignore revision 0
    d["-a"] = False         # Show filenames starting with '.'
    d["-D"] = False         # Show files that have been deleted
    d["-d"] = False         # Show revision date
    d["-e"] = False         # Earliest revisions first
    d["-l"] = False         # Long listing
    d["-r"] = False         # Output all files in repository
    d["-R"] = False         # Output all files in repository, absolute paths
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "0aDdehlrR")
    except getopt.GetoptError as str:
        msg, option = str
        out(msg + nl)
        sys.exit(1)
    for opt in optlist:
        if opt[0] == "-0":
            d["-0"] = not d["-0"]
        if opt[0] == "-a":
            d["-a"] = not d["-a"]
        if opt[0] == "-D":
            d["-D"] = not d["-D"]
        if opt[0] == "-d":
            d["-d"] = not d["-d"]
        if opt[0] == "-e":
            d["-e"] = not d["-e"]
        if opt[0] == "-h":
            Usage(d, 0)
        if opt[0] == "-l":
            d["-l"] = not d["-l"]
        if opt[0] == "-R":
            d["-R"] = not d["-R"]
        if opt[0] == "-r":
            d["-r"] = not d["-r"]
    d["cwd"] = Normalize(os.getcwd())
    return args

def Normalize(p):
    return p.replace("\\", "/")

def GetRootDirectory(d):
    '''Find the root directory of the Mercurial repository and put it
    in d, the options directory.
    '''
    p = subprocess.PIPE
    s = subprocess.Popen((hg, "root"), stdout=p, stderr=p)
    t = ''.join(s.stdout.readlines()) 
    e = s.stderr.read()
    if e:
        raise Exception("GetLog:  Error in hg command")
    t = Normalize(t.strip())
    d["root"] = t

def GetLog(d):
    '''Run the command 'hg log -v' and parse it, returning a
    dictionary keyed by file name.
    '''
    # Here's how we parse the output.  Read the whole command
    # in as a single string.  Split this string on the character
    # sequence '\n\nchangeset:'; this splits the string into the strings
    # for each change.  Then parse the substring separately.
    p = subprocess.PIPE
    s = subprocess.Popen((hg, "log", "-v"), stdout=p, stderr=p)
    t = ''.join(s.stdout.readlines()) 
    # Split the string up into separate chunks for each checkin
    fields = t.split(nl + nl + "changeset:")
    for i, item in enumerate(fields):
        if i:
            # For all but the first, add the word back in so that the
            # fields can be parsed uniformly.
            fields[i] = "changeset:" + item
    changes = BuildDict(fields, d) 
    e = s.stderr.read()
    if e:
        raise Exception("GetLog:  Error in hg command")
    return changes

def BuildDict(fields, D):
    '''fields is a list of strings from the 'hg log -v' command; an
    example of one of the strings is:

        changeset:   76:6eec7a578384
        user:        abcd
        date:        Tue Jun 26 17:42:26 2012 -0600
        files:       .profile 0todo.odt help.odt i2c/0readme i2c/0todo
        description:
        Tue 26 Jun 2012 05:42:26 PM

    fields contains one string for each checkin.  Parse each
    substring into its fields (i.e., changeset, tag, user, data,
    files, and description) and put into a dictionary keyed by the
    decimal revision number.  D is the options dictionary.  Note we
    also create a new key called files_d which is a list of each of
    the files, but with their absolute path in the repository.
    '''
    changes = dict()
    for i, f in enumerate(fields):
        g, d = f.split(nl), dict()
        for j, item in enumerate(g):
            if item != "description:":
                loc = item.find(":")
                if loc == -1:
                    msg = "Bad field in %dth change record" % i
                    raise ValueError(msg)
                name, value = item[:loc].strip(), item[loc + 1:].strip()
                if name in ("date", "files"):
                    value = value.split()
                    if name == "files":
                        d["files_d"] = [Absolute(i, D) for i in value]
                elif name == "changeset":
                    value = value.split(":")
                d[name] = value
            else:
                d["description"] = g[j + 1:]
                break
        key = int(d["changeset"][0])
        changes[key] = d
    if 0:
        # Dump data to stdout
        for k in changes:
            out(k)
            for i in changes[k]:
                out(" ", i, ":", changes[k][i])
            out()
        exit()
    return changes

def Absolute(file, d):
    '''Turn file into an absolute path starting with the Mercurial
    root directory.
    '''
    return Normalize(os.path.join(d["root"], file))

def StrList(L):
    '''Convert a list to a space-separated string.  If the contents
    are strings, real numbers, or integers, the routine should work.
    '''
    s = str(L).replace("[", "").replace("]", "").replace(",", "")
    s = s.replace("'", "")
    return s

def IsInCwd(file, d):
    '''Return True if the given file is in the current working
    directory.
    '''
    abspath = Normalize(os.path.join(d["root"], file))
    dir, dummy = os.path.split(abspath)
    if dir == d["cwd"]:
        return True
    return False

def GetDate(num, changes):
    '''Given the decimal number num of a change, return a string
    corresponding to the date of that change.
    '''
    dt = changes[num]["date"]
    m, d, y = dt[1], str(int(dt[2])), str(int(dt[4]))
    return d + m + y[2:]

def GetDescription(data):
    '''data is a list of the description strings.  Trim off any empty
    strings at the end and join with newlines.  But first check to see
    if the first line looks like a date string of the form
        Thu 22 Nov 2012 10:50:32 AM
    If so, then just return None, as this duplicates what gets printed
    in the date field.
    '''
    fields, ampm = data[0].split(), ("AM", "PM")
    if fields[0] in days and fields[2] in months and fields[5] in ampm:
        return None
    while not data[-1]:
        del data[-1]
    return nl.join(data)

def ArrangeByFile(changes, D):
    '''Return a dict where the keys are the filenames in the
    repository (the insertion order is in alphabetical order).  Each
    name will contain a list of the keys into the changes dictionary.
    D is the options dictionary.  Example contents for 
    d:/p/pylib (key, value):
        (D:/p/pylib/2up.py, [53, 13])
        (D:/p/pylib/2word.py, [314, 300, 261, 81])
        (D:/p/pylib/3456.py, [314, 300, 152, 112, 111, 110, 10])
        (D:/p/pylib/3456p.py, [314, 300, 107])
        (D:/p/pylib/5_gallon_bucket.py, [205, 196, 195, 184, 168])
        ...
    '''
 
    # Implementation detail:  this implementation uses plain python
    # dictionaries for storing the intermediate data structures.  For
    # python 2.6.5 at least, this results in the dictionary keyed by
    # the revision number to be in numerical order because integers
    # hash to themselves; i.e., when you iterate on the dictionary's
    # keys, you get them ascending in numerical order.  This might not
    # be true for other python versions; if so, use or find an ordered
    # dictionary object and replace the dict() constructor everywhere
    # by odict().  You'll then probably have to switch the sense of
    # the d["-e"] test when printing to get things to work correctly.
 
    # Get a set of the file names
    fn = []
    for revision_number in changes:
        try:
            # Note we're using the files with paths prepended
            fn += changes[revision_number]["files_d"]
        except KeyError:
            pass
    fn = list(set(fn))
    # Now build a dictionary whose keys are the absolute paths to the
    # files and where each value is a list of revisions made to that
    # file.
    changes_by_file = defaultdict(list)
    for revision_number in changes:
        if "files_d" in changes[revision_number]:
            for abspath in changes[revision_number]["files_d"]:
                changes_by_file[abspath] += [revision_number]
    # Sort the data and insert into a dict
    arranged = dict()
    files = changes_by_file.keys()
    files.sort()
    for file in files:
        if 0 in changes_by_file[file] and not D["-0"]:
            changes_by_file[file].remove(0)
        if D["-e"]:  # Earliest first
            arranged[file] = changes_by_file[file]
        else:
            arranged[file] = list(reversed(changes_by_file[file]))
    if 0:
        # Print out arranged
        for i in arranged:
            print i, arranged[i]
        exit()
    return arranged

def PrintItem(file, change_list, changes, d):
    '''Print to stdout according to settings.  file is the file name
    and is an absolute path; change_list is the list of revision
    numbers where revisions were made, and changes is the main
    dictionary of information keyed by revision number.
    '''
    def Print(file):
        if d["-l"]: # Show long listing
            out(file + ":")
            ind = " "*2
            for i in change_list:
                out(ind, ":".join(changes[i]["changeset"]))
                out(ind*2, StrList(changes[i]["date"]))
                de = GetDescription(changes[i]["description"])
                if de is not None:
                    out(ind*2, de)
            return
        if d["-d"]: # Show revision dates
            items = StrList([GetDate(num, changes) for num in change_list])
        else: # Show revision numbers
            items = StrList(change_list)
        s = file + ": " + items
        out(s)
    dir, name = os.path.split(file)
    p = Normalize(os.path.join(d["root"], file))
    if d["-r"] or d["-R"]:
        # Print for all directories
        if not d["-a"]:
            # Don't print this item if the file name begins with a '.'
            if name[0] == ".":
                return
        if not d["-D"] and not os.path.isfile(p):
            # Don't show deleted files
            return
        if not d["-a"] and name[0] == ".":
            # Don't show files beginning with "."
            return
        if d["-r"]:
            Print(Normalize(os.path.relpath(p, d["root"])))
        else:
            Print(file)
    else:
        if d["given"]:
            Print(Normalize(os.path.relpath(p, d["cwd"])))
        else:
            # Only print for files in current directory
            if IsInCwd(file, d):
                if not d["-D"] and not os.path.isfile(p):
                    # Don't show deleted files
                    return
                if not d["-a"] and name[0] == ".":
                    # Don't show files beginning with "."
                    return
                Print(Normalize(os.path.relpath(p, d["cwd"])))

def PrintResults(args, changes, d):
    '''args contains the command line arguments.  changes is a dict
    keyed by the decimal revision number.  Each value is another dict
    containing the data on that particular revision.  Depending on the
    desires of the user, print out the requested information.
    '''
    changes_by_file = ArrangeByFile(changes, d)
    # Now changes_by_file contains entries like:
    # { "D:/p/pylib/2up.py"   : [53, 13], 
    #   "D:/p/pylib/2word.py" : [314, 300, 261, 81], 
    #   "D:/p/pylib/3456.py"  : [314, 300, 152, 112, 111, 110, 10], 
    #   ...
    # }
    d["given"] = False # Flag to process these files even if not in cwd
    if args:
        # Only list for the given files
        f = lambda x: Normalize(os.path.abspath(x))
        files_to_print = [f(i) for i in args]
        d["given"] = True  
    else:
        # Report on all files
        files_to_print = changes_by_file.keys()
        files_to_print.sort()
    for file in files_to_print:
        if os.path.isdir(file):
            # Ignore it if it's a directory
            continue
        try:
            this_files_changes = changes_by_file[file]
        except KeyError:
            # It's a file that isn't in repository
            rp = Normalize(os.path.relpath(file, d["cwd"]))
            out("'%s' is not in repository" % rp, stream=sys.stderr)
        else:
            if this_files_changes:
                PrintItem(file, this_files_changes, changes, d)

def main():
    d = {} # Options dictionary
    args = ParseCommandLine(d)
    GetRootDirectory(d)
    changes = GetLog(d)
    PrintResults(args, changes, d)

if __name__ == "__main__":
    main()
