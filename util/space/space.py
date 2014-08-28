'''
TODO:
    * Add a -m option that makes it ignore Mercurial directories
    * Add a -x option that lets it ignore everything at and below a
      particular directory; more than one -x option allowed.

This module provides a function that constructs a list containing
the sizes of directories under a specified directory.

If you run it as a script and want to see a list of all files >=
a specified size in MB, add a second integer or float parameter to
the command line.

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

import string, os, getopt, sys
from pdb import set_trace as xx


out = sys.stdout.write
err = sys.stderr.write
nl = "\n"

# Contains directory name and total size
DirSizes = []

# Data for finding biggest files
NumBigFiles = 10   # How many to track
BigFiles    = []   # List of (size, filename)
Threshold   = 0    # MB threshold; if nonzero, show all file sizes
                   # that are >= to this value.

# If true, list the sizes of each directory under given directory
directories_only = 0

manual = '''
Usage:  {name} [options] directory 

  Prints a recursive listing of the largest files in and under the given
  directory.

Options
    -d
        Change behavior to print the size of the files underneath each
        directory in the given directory.
    -n num
        How big to make the list of biggest files.  Default = {numbigfiles}.
    -p pct
        Only print directories that are >= pct in percent.  Defaults to
        {threshold}%.  Here, the percentage is of the total number of
        bytes in all the directories.

Hints:
  I use this program to help me see the largest files and directory at and
  below a certain point.  Because it has to walk the whole directory tree,
  it can take significant time to execute.
'''[1:-1]

def Usage(d, status=1):
    '''d is the options dictionary.
    '''
    numbigfiles = NumBigFiles
    name = sys.argv[0]
    threshold = d["-p"]
    print manual.format(**locals())
    exit(status)

def TrimBigFiles():
    '''Trim the container.  If Threshold is nonzero, we keep all
    files larger than the threshold.  Otherwise, just keep the
    specified number.
    '''
    global BigFiles
    BigFiles.sort()
    if Threshold:
        BigFiles = [x for x in BigFiles if x[0] > Threshold*1e6]
    else:
        BigFiles = BigFiles[-NumBigFiles:]

def GetTotalFileSize(dummy_param, directory, list_of_files):
    '''Given a list of files and the directory they're in, add the
    total size and directory name to the global list DirSizes.
    '''
    global DirSizes, BigFiles
    currdir = os.getcwd()
    os.chdir(directory)
    total_size = 0
    if len(list_of_files) != 0:
        for file in list_of_files:
            if file == ".." or file == ".":  continue
            # The following is needed because (apparently) cygwin changed
            # from using nul to /dev/null, yet if there is a file called
            # 'nul', it causes a problem in the os.stat command.
            if file == "nul":  
                continue
            try:
                size = os.stat(file)[6]
            except OSError:
                continue
            total_size = total_size + size
            BigFiles.append((size, os.path.join(directory, file)))
    DirSizes.append([total_size, directory])
    TrimBigFiles()
    os.chdir(currdir)

def GetSize(directory, d):
    '''Returns a list of the form [ [a, b], [c, d], ... ] where
    a, c, ... are the number of total bytes in the directory and
    b, d, ... are the directory names.  The indicated directory 
    is recursively descended and the results are sorted by directory 
    size with the largest directory at the beginning of the list.
    '''
    global DirSizes
    DirSizes = []
    os.path.walk(directory, GetTotalFileSize, "")
    DirSizes.sort()
    DirSizes.reverse()
    return DirSizes

def ParseCommandLine(d):
    d["-d"] = False     # Directories only
    d["-n"] = 20        # Length of big files list
    d["-p"] = 1         # Percent threshold
    if len(sys.argv) < 2:
        Usage(d)
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "dhn:p:")
    except getopt.error as s:
        out(str(s) + nl)
        exit(1)
    for opt in optlist:
        if opt[0] == "-d":
            d["-d"] = True
        if opt[0] == "-n":
            global NumBigFiles
            NumBigFiles = int(opt[1])
        if opt[0] == "-p":
            try:
                d["-p"] = float(opt[1])
            except ValueError:
                msg = "'%s' is not a valid percentage" % opt[1]

    if len(args) < 1:
        Usage(d)
    return args

def DirectoriesOnly(dir, d):
    # Get list of directories under dir
    from glob import glob
    dirs = filter(os.path.isdir, glob(os.path.join(dir, "*")))
    dirs += filter(os.path.isdir, glob(os.path.join(dir, ".*")))
    Normalize(dirs)
    results = []
    for dir in dirs:
        sizes = GetSize(dir, d)
        bytes = [x[0] for x in sizes]
        results.append((sum(bytes)/1e6, dir))
    results.sort()
    results.reverse()
    out("Size, MB   Directory" + nl)
    out("--------   ---------" + nl)
    total_size_in_MB = 0
    for size, dir in results:
        s = dir.replace("\\", "/")
        out("%8.1f   %s" % (size, s) + nl)
        total_size_in_MB += size
    out("Total size = %.1f MB" % total_size_in_MB + nl)

def Normalize(dirs):
    '''Replace backslashes with forward slashes.
    '''
    for i in xrange(len(dirs)):
        dirs[i] = dirs[i].replace("\\", "/")

def NormalizeDecorated(dirs):
    '''Replace backslashes with forward slashes.  The list dirs contains
    tuples whose second element is the directory name.
    '''
    for i in xrange(len(dirs)):
        dirs[i][1] = dirs[i][1].replace("\\", "/")

def ShowBiggestDirectories(directory, d):
    GetSize(directory, d)
    # Get total number of bytes
    total_size = 0L
    NormalizeDecorated(DirSizes)
    for dir in DirSizes:
        total_size = total_size + dir[0]
    if total_size != 0:
        out("For directory '%s':    " % directory)
        out("[total space = %.1f MB]" % (total_size / 1e6) + nl)
        out("   %     MB   Directory" + nl)
        out("------ -----  " + "-" * 50 + nl)
        not_shown_count = 0
        for dir in DirSizes:
            percent = 100.0 * dir[0] / total_size
            dir[1] = string.replace(dir[1], "\\\\", "/")
            if percent >= d["-p"]:
                out("%6.1f %5d  %s" % (percent, int(dir[0]/1e6), dir[1]) + nl)
            else:
                not_shown_count = not_shown_count + 1
        if not_shown_count > 0:
            msg = nl + "  [%d %s not shown]"
            if not_shown_count > 1:
                out(msg % (not_shown_count, "directories") + nl)
            else:
                out(msg % (not_shown_count, "directory") + nl)

if __name__ == "__main__":
    d = {}
    args = ParseCommandLine(d)
    if d["-d"]:
        DirectoriesOnly(args[0], d)
        exit(0)
    if len(args) == 2:
        Threshold = float(args[1])
    ShowBiggestDirectories(args[0], d)
    if d["-d"]:
        out("\nFiles >= " + args[1] + " MB:" + nl)
    else:
        out("\n%d biggest files in MB:" % NumBigFiles + nl)
    BigFiles.reverse()
    total = 0L
    for size, file in BigFiles:
        out("%8.2f  %s" % (size/1e6, file.replace("\\", "/")) + nl)
        total += size
    out("\n  Total MB of these files = %.1f" % (total/1e6) + nl)
