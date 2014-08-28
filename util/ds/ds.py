'''
Open a data sheet file if it's the only match to the regexp on the
command line.  Otherwise print out the matches.

Example:

    ds 3456

  will prompt you for manuals/datasheets/catalogs that contain the
  string 3456.
'''

import sys, os, getopt, re, glob, subprocess
from os.path import join, isfile, split 
import color as c

# app to open a file with registered application
if 1:
    app = "/usr/bin/exo-open"       # Linux
else:
    app = "d:/don/bin/bat/app.exe"  # Windows

# Colors for output; colors available are:
#   black   gray
#   blue    lblue
#   green   lgreen
#   cyan    lcyan
#   red     lred
#   magenta lmagenta
#   brown   yellow
#   white   lwhite

(black, blue, green, cyan, red, magenta, brown, white, gray, lblue,
lgreen, lcyan, lred, lmagenta, yellow, lwhite) = (c.black, c.blue,
c.green, c.cyan, c.red, c.magenta, c.brown, c.white, c.gray, c.lblue,
c.lgreen, c.lcyan, c.lred, c.lmagenta, c.yellow, c.lwhite) 

c_norm      = (white, black)  # Color when finished
c_plain     = (white, black)

# The following variable can be used to choose different color styles
colorstyle = 0
if colorstyle == 0:
    c_dir       = (lred, black)
    c_match     = (yellow, black)
elif colorstyle == 1:
    c_dir       = (lred, black)
    c_match     = (white, blue)
elif colorstyle == 2:
    c_dir       = (lgreen, black)
    c_match     = (black, green)
elif colorstyle == 3:
    c_dir       = (lmagenta, black)
    c_match     = (yellow, black)
elif colorstyle == 4:
    c_dir       = (lgreen, black)
    c_match     = (lwhite, magenta)
elif colorstyle == 5:
    c_dir       = (lred, black)
    c_match     = (black, yellow)

def out(*v, **kw):
    sep = kw.setdefault("sep", " ")
    nl  = kw.setdefault("nl", True)
    stream = kw.setdefault("stream", sys.stdout)
    if v:
        stream.write(sep.join([str(i) for i in v]))
    if nl:
        stream.write("\n")

def Usage(d, status=1):
    name = sys.argv[0]
    s = '''
Usage:  {name} [options] regexp
  Open a data sheet, manual, etc. file if it's the only match to the
  regexp.  Otherwise print out the matches and choose which one to
  display.

Options
    -i  
        Make the search case sensitive.
'''[1:-1]
    out(s.format(**locals()))
    sys.exit(status)

def ParseCommandLine(d):
    d["-i"] = False     # If True, then case-sensitive search
    if len(sys.argv) < 2:
        Usage(d)
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "i")
    except getopt.GetoptError as e:
        msg, option = e
        out(msg)
        exit(1)
    for opt in optlist:
        if opt[0] == "-i":
            d["-i"] = True
    if len(args) != 1:
        Usage(d)
    return args

def PrintMatch(num, s, start, end, d):
    '''For the match in s, print things out in the appropriate colors.
    Note start and end are the indices into just the file part of the
    whole path name.
    '''
    c.fg(c_plain)
    out("%3d  " % num, nl=False)
    dir, file = split(s[len(d["root"]) + 1:])  # Gets rid of leading stuff
    dir += "/"
    out(dir, nl=False)
    out(file[:start], nl=False)
    c.fg(c_match)
    out(file[start:end], nl=False)
    c.fg(c_plain)
    out(file[end:])

def Normalize(dir):
    return dir.replace("\\", "/")

def J(D, other):
    return Normalize(join(D, other))

def GetFiles(d):
    '''Get a list of files to display.
    '''
    files = []
    for dir in d["dir"]:
        f = [Normalize(i) for i in glob.glob(dir + "/*")]
        for file in f:
            if isfile(file):
                files.append(file)
    return files

def main():
    d = {} # Options dictionary
    d["root"] = D = "/manuals"
    # Directories to check
    d["dir"] = (
        J(D, "datasheets"),
        J(D, "datasheets/batteries"),
        J(D, "app_notes"),
        J(D, "app_notes/Tektronix"),
        J(D, "catalogs"),
        J(D, "manuals"),
        J(D, "manuals/RadioShack"),
        J(D, "manuals/agilent"),
        J(D, "manuals/bk"),
        J(D, "manuals/bk/dc_load"),
        J(D, "manuals/bk/dmm"),
        J(D, "manuals/bk/function_generators"),
        J(D, "manuals/bk/misc"),
        J(D, "manuals/bk/power_supplies"),
        J(D, "manuals/bk/scopes"),
        J(D, "manuals/calculators"),
        J(D, "manuals/fluke"),
        J(D, "manuals/Dixon_lawn_mower_ZTR3362"),
        J(D, "manuals/gr"),
        J(D, "manuals/hp"),
        J(D, "manuals/tek"),
    )
    regexp = ParseCommandLine(d)[0]
    r = re.compile(regexp) if d["-i"] else re.compile(regexp, re.I)
    # Get list of data files
    files = GetFiles(d)
    matches = []
    for i in files:
        # Only search for match in file name
        dir, file = split(i)
        mo = r.search(file)
        if mo:
            matches.append((i, mo))
    # Each match item will be (full_filename, match_object) where
    # match_object is the mo for _only_ the actual file name (not the
    # path).
    if len(matches) > 1:
        out("Choose which file to open:")
        for num, data in enumerate(matches):
            file, mo = data
            PrintMatch(num + 1, file, mo.start(), mo.end(), d)
        # Get which one to open
        while True:
            answer = raw_input("? ").strip()
            if not answer or answer == "q":
                exit(0)
            try:
                choice = int(answer) - 1
                if 0 <= choice < len(matches):
                    break
                else:
                    out("Answer must be between 1 and %d" % len(matches))
            except Exception:
                out("Improper number -- try again")
        subprocess.Popen([app, matches[choice][0]])
    elif len(matches) == 1:
        # Open this file
        subprocess.Popen([app, matches[0][0]])
    else:
        out("No matches")

main()
