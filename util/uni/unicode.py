'''
ToDo
    * Add -s option to search text files
    * Add -n option to sort output by codepoint

Script to look up Unicode characters and launch PDFs showing the
symbols.  It requires the contents of the index file at
http://www.unicode.org/charts/charindex.html to be saved as a text
file that is named in the global variable 'datafile'.

Should you wish to use this script to launch the various PDFs
containing the symbols, download as many of the PDFs as you need from
http://www.unicode.org/charts/.  

    You can also use this web page to search for the PDF that contains
    a particular codepoint; type the codepoint's hex value in the box
    at the top and you'll get the relevant PDF.

Give these PDF files names such as
arrows_supplemental_A_U27F0-27FF.pdf, where the two pairs of hex
numbers after the U indicate the number ranges.  Warning:  don't trust
the file names you download from the above site, as they may not have
the right numbers in the file name.  Open the file up and the first
page will tell you the proper range of the code point numbers (the
numbers are called code points, a synonym for the unique integer
representing a particular symbol).

If you are on a system that e.g. has the program pdftotext
(/usr/bin/pdftotext on Linux), you can use it to convert the PDF files
to associated text files.  If a corresponding .txt file is present,
then you can use the -s option to search this file for the code point
and it will print out the associated text.  This works well in a
Unicode-aware terminal (such as /usr/bin/uxterm) because the output
contains some Unicode characters.  And it's still somewhat useful in a
non-Unicode terminal.  However, I found that I had to manually edit
each of the 40 or so files I had to remove the beginning cruft (search
down for the formfeed character that immediately precedes the
beginning of the useful text; with an editor macro, this only takes
a few minutes to edit all the files).

Set the global variables 'pdf_dir' and 'launch' to appropriate strings
for your system.

On a UNIX system, you can do a 'man -k unicode' and you'll find some
things that might be of interest.  For example, on my Linux box, I
came across the gnome-character-map utility (charmap(1) that was
useful to look at different Unicode characters.  Suppose you want to
look at the euro symbol, codepoint U+20ac.  Press ctrl-F to open the
find dialog, type in 20ac, and hit return.  You'll be shown the euro
character.  Click on the tab "Character Details" and you'll see useful
information about the character, such as:  name, symbol, how long it's
been in Unicode, Unicode category, encodings such as UTF-8, UTF-16, C
octal escaped UTF-8, and XML decimal; annotations and cross
references.  

'''
# Copyright (C) 2014 Don Peterson
# Contact:  gmail.com@someonesdad1

#
#

from __future__ import print_function, division
import getopt
import glob
import os
import re
import sys
import subprocess
from pdb import set_trace as xx

# Global variables you'll need to set
pdf_dir = "/doc/unicode"                # Where PDFs are located
launch = "/usr/bin/exo-open"            # Program to launch a file
datafile = "/doc/unicode/symbols.txt"   # Index text file

def Error(msg, status=1):
    print(msg, file=sys.stderr)
    exit(status)

def Usage(d, status=1):
    name = sys.argv[0]
    num = len(d["symbols"])
    s = '''
Usage:  {name} [options] regexp [regexp ...]
  Search the Unicode symbol index for a particular symbol.  There are
  {num} symbols in the index.  The searches are case-independent.

  If regexp looks like a hex number, then it's interpreted as a
  Unicode code point and a PDF is opened showing the symbol if there
  is a file in scope.
  
  Reference:  http://www.unicode.org/charts/charindex.html, which is 
  for Unicode 7, and was last updated 9 Jun 2014.  For an index to
  various PDFs, see http://www.unicode.org/charts/.

Example:
  Suppose you want the Unicode symbol for a steaming pile of poo.
  Run the script as
    {name} poo
  and you'll get a list of candidates.  The desired symbol ("poo, pile
  of") has a hex number of 1f4a9, so run the command
    {name} 1f4a9
  and the relevant PDF will be opened (assuming you have downloaded
  the proper file entitled "Miscellaneous Symbols and Pictographs",
  which covers the code point range of U+1F300 to U+1F5FF).

Options:
    -b      Show codepoint in binary
    -d      Codepoints on command line are in decimal (hex is default)
    -i      Don't ignore case.
    -n      Sort output by codepoint order (alphabetical is default).
    -t      Search the corresponding *.txt file instead of launching
            the PDF.
'''[1:-1]
    print(s.format(**locals()))
    sys.exit(status)

def ParseCommandLine(d):
    d["-b"] = False     # Print codepoint in binary
    d["-d"] = False     # Codepoints on command line in decimal
    d["-i"] = True      # Ignore case
    d["-n"] = False     # Sort by codepoint
    d["-t"] = False     # Search the *.txt file
    data = open(datafile).read()
    d["symbols"] = [i for i in data.split("\n") if i and i[0] != "#"]
    try:
        opts, args = getopt.getopt(sys.argv[1:], "bdint")
    except getopt.GetoptError as e:
        print(str(e))
        exit(1)
    for o, a in opts:
        if o in ("-b",):
            d["-b"] = True
        elif o in ("-i",):
            d["-i"] = False
        elif o in ("-d",):
            d["-d"] = True
        elif o in ("-n",):
            d["-n"] = True
        elif o in ("-t",):
            d["-t"] = True
    if not args:
        Usage(d)
    if d["-i"]:
        d["symbols"] = [i.lower() for i in d["symbols"]]
    return args

def IsHexNumber(regexp, d):
    chars = set(regexp.lower())
    digits, letters = "0123456789", "abcdef"
    if d["-d"]:
        return chars.issubset(set(digits))
    else:
        return chars.issubset(set(digits + letters))

def GetNumberRanges(d):
    '''Read all the PDF files and return a list of tuple pairs
    encoding their range.
    '''
    ranges = []
    for filename in glob.iglob(pdf_dir + "/*.[pP][dD][fF]"):
        loc = filename.rfind("U")
        if loc == -1:
            continue
        s = filename[loc + 1:]
        dp = s.find(".")
        if dp == -1:
            continue
        s = s[:dp]
        x = s.split("-")
        if len(x) != 2:
            continue
        low, high = [int(i, 16) for i in x]
        if low >= high:
            low, high = high, low
        ranges.append((low, high, filename))
    return ranges

def Normalize(num):
    '''num is an integer Unicode codepoint to look for.  Ensure its
    string representation is at least four characters long.  For
    example, the space character is 0x20; return 0020 because the 
    Unicode text file uses that string to begin a line that describes
    the symbol.  Return it in uppercase, as that's what the Unicode
    files use.
    '''
    s = hex(num)[2:]
    while len(s) < 4:
        s = "0" + s
    return s.upper()

def OpenTextFile(num, filename, d):
    '''filename is the name of a PDF file.  num is the codepoint to
    search for.  Open the text file, search down to the first form
    feed, then start searching for a line that begins with that
    codepoint number.  Continue to print lines until the next
    codepoint line is reached.
    '''
    # Get the text from the text file corresponding to the PDF
    name, ext = os.path.splitext(filename)
    textfile = name + ".txt"
    if not os.path.isfile(textfile):
        Error("Could not find '%s'" % textfile)
    text = open(textfile, "rb").read().decode("UTF-8")
    # Keep only the text after the second formfeed character
    for i in range(1, 3):
        loc = text.find(chr(0x0c))
        if loc == -1:
            Error("'%s' missing formfeed number %d" % (textfile, i))
        text = text[loc + 1:]
    # Now split on newlines
    lines = text.split("\n")
    # Search down until regexp is found
    codepoint, show = Normalize(int(num, 16)), False
    r = re.compile(r"^[0-9a-f]{4,5}", re.I)
    for line in lines:
        if line.startswith(codepoint):
            show = True
        else:
            mo = r.search(line)
            if show and mo:
                break  # Found next codepoint's line
        if show:
            print(line)

def OpenPDF(regexp, d):
    ''''''
    u = int(regexp, 16)
    ranges = GetNumberRanges(d)
    for low, high, filename in ranges:
         if low <= u <= high:
            if d["-t"]:
                # Open the text file instead
                rc = OpenTextFile(regexp, filename, d)
            else:
                rc = subprocess.call("%s %s" % (launch, filename), shell=True)
            exit(rc)
    print("No appropriate file found for %s" % regexp)
    exit(1)

def GetCodepoint(line):
    f = line.split()
    return int(f[-1], 16)

def GetCodepointBinary(line):
    '''Return a string representing the codepoint in binary.  Since
    the largest codepoint is 0x10ffff, the binary form of this number
    is 0b100001111111111111111; hence the width of 21 digits.
    '''
    cp = GetCodepoint(line)
    s = list(reversed(bin(cp)[2:]))
    while len(s) < 21:
        s.append("0")
    return ''.join(list(reversed(s)))

def PutCodepointFirst(line, d):
    f = line.split()
    if d["-b"]:
        b = GetCodepointBinary(line)
        return "{0} {1}".format(b, ' '.join(f[:-1]))
    else:
        # 6 is used because the largest codepoint's hex form is 10ffff
        return "{0:6} {1}".format(f[-1], ' '.join(f[:-1]))

def Search(regexp, d):
    if IsHexNumber(regexp, d):
        if d["-d"]:
            # Convert decimal number to hex
            regexp = hex(int(regexp))[2:]
        OpenPDF(regexp, d)
        return
    r, results = re.compile(regexp), []
    for line in d["symbols"]:
        mo = r.search(line)
        if mo:
            # Store with codepoint so can be sorted if desired
            results.append((GetCodepoint(line), line))
    if d["-n"]:
        results.sort()
    results = [(cp, PutCodepointFirst(line, d)) for cp, line in results]
    for cp, line in results:
        print(line)

def main():
    d = {} # Options dictionary
    regexps = ParseCommandLine(d)
    for regexp in regexps:
        Search(regexp, d)

main()
