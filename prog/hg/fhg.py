'''
Find all Mercurial directories at and under the current directory.
'''

from __future__ import print_function
import sys, os, getopt, subprocess
from color import *
from pdb import set_trace as xx

# Set to the Mercurial command's location
hg = "d:/bin/TortoiseHg104/hg.exe"
hg = "/usr/bin/hg"

# Colors used to indicate various Mercurial states
states = {
    "M" : yellow,           # Modified
    "A" : lgreen,           # Added
    "R" : (lwhite, red),    # Removed
    "!" : lcyan,            # Missing
    "?" : lmagenta,         # Not tracked
    "dirty" : lred,
    "clean" : (white, black),
}

def Usage(status=0):
    name = sys.argv[0]
    s = '''
Usage:  {name} [options] dir1 [dir2...]
  Show directories at and below the indicated directories that
  contain a Mercurial repository and indicate the directories'
  state.

Options
    -c 
        Don't show clean directories.
'''[1:-1]
    print(s.format(**locals()))
    sys.exit(status)

def ProcessDir(dir, d):
    level = 0
    for root, dirs, files in os.walk(dir):
        if ".hg" in dirs:
            Report(root.replace("\\", "/"), d)

def Line(indent, letter, text):
    print(indent, end="")
    fg(states[letter])
    print(letter, end="")
    print(" ", text, end="")
    normal()
    print()

def Header(d):
    '''Show key to interpret report.
    '''
    sp = " "*2
    print("Color key:  (M:n means there are n files of type M)")
    Line(sp, "M", "Modified")
    Line(sp, "A", "Added")
    Line(sp, "R", "Removed")
    Line(sp, "!", "Missing")
    Line(sp, "?", "Not tracked")
    print(sp, end="")
    fg(states["dirty"])
    print("Dirty repository")
    normal()
    print(sp, end="")
    if not d["-c"]:
        # Only show clean color-coding if -c option was used because
        # no clean directories will be shown otherwise.
        fg(states["clean"])
        print("Clean repository")
    normal()
    print()

def Int(letter, count):
    '''Print the indicated count in the associated color.
    '''
    fg(states[letter])
    s = "%s:%d" % (letter, count)
    print(s, end="")
    normal()
    print(" ", end="")

def Status(dir, status, d):
    '''Report as if this was a colorized 'hg st' command for this
    directory (which, in fact, is exactly what it is.

    status will be a list of the lines from an 'hg st' command.
    '''
    # Only display dirty repositories
    if not status:
        return
    fg(states["dirty"])
    print(dir)
    normal()
    for i in status:
        print("  ", end="")
        letter = i.split()[0]
        fg(states[letter])
        print(i)
        normal()

def Report(dir, d):
    '''dir is a Mercurial directory.  Find out if its status indicates
    the repository has changed; if so, print out the name in color.
    Note:  the status command prints out the following prefixes:
 
        M = modified
        A = added
        R = removed
        C = clean
        ! = missing (deleted by non-hg command, but still tracked)
        ? = not tracked
        I = ignored
          = origin of the previous file listed as A (added)
    The color is printed only for prefixes of M, A, R, and ?.
    '''
    cwd = os.getcwd()
    os.chdir(dir)
    p = subprocess.PIPE
    s = subprocess.Popen((hg, "status"), stdout=p)
    results = [i.strip().replace("\\", "/") for i in s.stdout.readlines()]
    if d["-s"]:
        Status(dir, results, d)
        return
    # Now just extract the letters
    results = [i.split()[0] for i in results]
    # Count each type
    count = {}
    for letter in results:
        if count.has_key(letter):
            count[letter] += 1
        else:
            count[letter] = 1
    # Print results
    if results:
        # The repository is dirty
        fg(states["dirty"])
        print(dir, end="")
        normal()
        print("  ", end="")
        for i in "MAR!?":
            if i in results:
                Int(i, count[i])
        print()
    else:
        # The repository is clean
        fg(states["clean"])
        if not d["-c"]:
            print(dir)
        normal()
    os.chdir(cwd)

def ParseCommandLine(d):
    d["-c"] = True      # Don't show clean directories
    d["-s"] = False     # Show 'hg st' type listing
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "chs")
    except getopt.GetoptError as e:
        msg, option = e
        print(msg)
        exit(1)
    for opt in optlist:
        if opt[0] == "-c":
            d["-c"] = False
        if opt[0] == "-h":
            Usage()
        if opt[0] == "-s":
            d["-s"] = True
    if not args:
        args = ["."]
    return args

def main():
    d = {} # Options dictionary
    dirs = ParseCommandLine(d)
    print('''
Search for dirty Mercurial repositories.  Options:
    -c      Show both clean and dirty repositories
    -s      Display the same information as 'hg st' but in color
'''[1:])
    Header(d)
    for dir in dirs:
        ProcessDir(dir, d)
main()
