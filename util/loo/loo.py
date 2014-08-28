'''
Library routine to find picture files linked or embedded in an Open
Office document.  call GetOOFilePictures(oofile) with the path to an
OO file and you'll get a list of image files in that document.
 
Run as a script to pass OO files on the command line; their picture
files will be printed to stdout.  Missing image files and image files
that aren't relative to the document's location will be flagged.
 
This is done by a heuristic rather than parsing the XML.
'''

# Copyright (C) 2014 Don Peterson
# Contact:  gmail.com@someonesdad1
 
#
#

from __future__ import (absolute_import, division, print_function)
import sys
import getopt
import os
import zipfile

from pdb import set_trace as xx

out = sys.stdout.write
err = sys.stderr.write
broken_link = "[missing]"
notrel_image = "[not relative]"
nl = "\n"

# File extensions that indicate a picture.  This list came from
# https://wiki.openoffice.org/wiki/Documentation/OOo3_User_Guides/Getting_Started/File_formats
_raw_ext = '''
    bmp  gif  pbm  pgm  psd  sgf  tif  wmf
    dxf  jpeg pcd  plt  ras  sgv  tiff xbm
    emf  jpg  pct  png  sda  svm  vor  xpm
    eps  met  pcx  ppm  sdd  tga
'''[:-1]
ext = []
for i in _raw_ext.split(nl):
    ext += ["." + j.lower() for j in i.split()]
_picture_ext = set((ext))
try:
    del ext, i, j
except NameError:  # j will be local on python 3
    pass

# File extensions for Open Office documents.  Add to this list if
# there are additional files you want searched.
_oo_ext = set((
    ".odb",     # OO Base database
    ".odg",     # OO Draw drawing
    ".odp",     # OO Impress presentation
    ".ods",     # OO Calc spreadsheet
    ".odt",     # OO Writer document
    ".ott",     # OO Writer template document
))

# Try to import the color.py module to allow highlighting missing
# files in color to make them easier to see.  If you don't have the
# module, it won't be an error (you'll just get uncolored output).
_have_color = False
try:
    import color as c
    _have_color = True
except ImportError:
    # Make a dummy color object to swallow function calls
    class Dummy:
        def fg(self, *p, **kw): pass
        def normal(self, *p, **kw): pass
        def __getattr__(self, name): pass
    c = Dummy()

class ZipfileError(Exception): pass

def Usage(d, status=1):
    def remove(alist, chars="[]'"):
        alist.sort()
        s = str(alist)
        return s.translate(None, chars)
    name = sys.argv[0]
    shortname = os.path.split(sys.argv[0])[1]
    missing = broken_link
    notrel = notrel_image
    image_extensions = _raw_ext
    oo_extensions = remove(list(_oo_ext))
    out('''
Usage:  {name} [options] file1 [file2...]
  For each Open Office document file given on the command line, print
  out any image files that the document file has links to.  Highlight
  any missing image (mark with '{missing}').
 
  Image files that are not at or below the same directory as the
  document file will be marked '{notrel}'.  This is done so that
  creating a zip file containing one or more Open Office files will
  have the documents display their images properly when the package is
  unzipped.  You may need to create some hard or soft links to the
  image files for this to work properly.
  
  Image files have extensions{image_extensions}
  Open Office document files have extensions
    {oo_extensions}
  
Options
  -e 
    Also print the names of embedded image files.
  -l
    Just list the encountered Open Office files (i.e., don't list
    their image files).
  -m
    Print only missing or not relative image files.
  -r
    Each 'file' on the command line is a directory.  Recursively seach
    it for Open Office files and print the images in the files found.
    If no directories are given on the command line, search the
    current directory tree by default.
 
Examples
    - '{shortname} -r' will show all the OO files and their images at
      and below the current directory.
    - '{shortname} -l' will do the same, but only display the file
      names.
    - '{shortname} -r dir' will show all the OO files and their images
      at below the directory dir.
'''[1:].format(**locals()))
    exit(status)

def ParseCommandLine(d):
    d["-e"] = False     # Don't ignore embedded pictures
    d["-l"] = False     # Only list OO file names
    d["-m"] = False     # Missing pictures only
    d["-r"] = False     # Recursive search
    if len(sys.argv) < 2:
        Usage(d)
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "elmr")
    except getopt.GetoptError as e:
        msg, option = e
        out(msg)
        exit(1)
    for opt in optlist:
        if opt[0] == "-e":
            d["-e"] = True
        if opt[0] == "-l":
            d["-l"] = True
            d["-r"] = True  # Implies a recursive search
        if opt[0] == "-m":
            d["-m"] = True
        if opt[0] == "-r":
            d["-r"] = True
    if d["-r"]:
        if not args:
            args = ["."]
    elif not args:
        out("Need at least one Open Office file" + nl)
        Usage(d)
    return args

def _Extract(filename, s):
    '''_Extract the image tag at the beginning of the string s.
    '''
    k = "href="
    loc = s.find(k)
    if loc == -1:
        raise ZipfileError("Missing href in '%s'" % filename)
    start = loc + 1 + len(k)
    s = s[start:]
    end = s.find('"', 1)
    if loc == -1:
        raise ZipfileError("Missing ending quote in '%s'" % filename)
    path = s[:end]
    dir, file = os.path.split(path)
    name, ext = os.path.splitext(file)
    if ext in _picture_ext:
        # Remove the leading '..'
        if path.startswith("../"):
            path = path[3:]
        return path

def _ProcessZipObject(zipobj, filename):
    '''zipobj is an open ZipFile object.  Open the file filename in
    the zip archive, read in its bytes, and search them for image tags.
    '''
    s = zipobj.open(filename).read()
    tag_begin, tag_end = "<draw:image xlink:href", "/>"
    loc = s.find(tag_begin)
    found_files = []
    while loc != -1:
        s = s[loc:]
        end = s.find(tag_end)
        if end == -1:
            raise ZipfileError("No end for '%s'" % filename)
        o = _Extract(filename, s[:end])
        if o is not None:
            if o.startswith("file:///"):
                o = o[8:]
            found_files.append(o)
        s = s[end:]
        loc = s.find("<draw:image xlink:href")
    return found_files

def IsOOFile(file):
    '''Return True if file has the name of an Open Office document
    file.
    '''
    path, filename = os.path.split(file)
    name, ext = os.path.splitext(filename)
    return ext.lower() in _oo_ext

def GetOOFilePictures(oofile):
    '''Return a sequence of the picture files included in the given
    Open Office file.  If oofile contains a path, it will be made the
    current directory (and the old current directory will be restored
    before exiting).
    
    Each returned item is a tuple of the form
        (path, state)
    where path is either a relative to the oofile's directory or
    an absolute path.
    
    state is a string of one of the following values:  "", "missing",
    "notrel".  "missing" means a link that points to a file that isn't
    present in the file system.  "notrel" means it's a path that is
    not at or below the directory containing the Open Office file.  An
    empty string means it's neither "missing" or "notrel".
    '''
    olddir = os.getcwd()
    path, file = os.path.split(oofile)
    if path:
        os.chdir(path)
    try:
        # This is done by a heuristic that reads the XML text for the tag
        # that precedes an image link.  The routine can't tell the
        # difference between an embedded picture and a linked picture.
        # The files are either relative to the Open Office file's location
        # or will be absolute file system paths.
        z, found_files = zipfile.ZipFile(oofile, "r"), []
        for i in z.namelist():
            # Only search XML files
            if i.lower().endswith(".xml"):
                found_files += _ProcessZipObject(z, i)
        # Examine each file and determine if it's OK, missing, not
        # relative, or embedded.
        found, currdir = [], Normalize(os.getcwd())
        for file in found_files:
            if IsEmbeddedImage(file):
                found.append((file, "embedded"))
            elif not os.path.isfile(file):
                found.append((file, "missing"))
            else:
                relpath = Normalize(os.path.relpath(file, currdir))
                if os.path.isabs(relpath) or relpath.startswith(".."):
                    found.append((file, "notrel"))
                else:
                    found.append((file, ""))
    finally:
        os.chdir(olddir)
    return tuple(found)

_all_chars = set([chr(i) for i in range(256)])

def keep(s, chars_to_keep):
    '''This is specific to 8-bit ASCII, so it will break on Unicode
    file names.
    '''
    delete_chars = ''.join(_all_chars - set(chars_to_keep))
    return s.translate(None, delete_chars)

def J(*p):
    '''Join the components of the sequence p into a path and Normalize
    it to have forward slashes.
    '''
    return Normalize(os.path.join(*p))

def Normalize(path):
    '''Use forward slashes in file names.
    '''
    return path.replace("\\", "/")

def IsEmbeddedImage(path):
    '''If the path is of the form e.g.
    Pictures/1000000000000233000000FE20974D73.png
    then it's probably an embedded image, so return True.  Note we
    ignore the extension.  This is a heuristic.
    '''
    dir, file = os.path.split(path)
    name, ext = os.path.splitext(file)
    k = keep(name, "1234567890abcdefABCDEF")
    if dir == "Pictures" and k == name:
        return True
    return False

def GetImages(file, ignore_embedded=True):
    olddir, image_files = os.getcwd(), []
    path, name = os.path.split(file)
    if path:
        os.chdir(path)
    try:
        try:
            image_files = GetOOFilePictures(name)
        except ZipfileError as e:
            err("Error for file '%s':%s" % (path, nl))
            err("  %s%s" % (e, nl))
            image_files = []
        except zipfile.BadZipfile:
            if not os.path.isdir(file):
                err("Error:  '%s' is not an Open Office file%s" % (file, nl))
            image_files = []
    finally:
        os.chdir(olddir)
        # If d["-e"] is not set (i.e., ignore embedded images), then
        # remove the embedded images.
        if ignore_embedded:
            non_embedded = []
            for i in image_files:
                name, state = i
                if not (state == "missing" and IsEmbeddedImage(name)):
                    non_embedded.append(i)
            image_files = non_embedded
        return image_files

def ProcessFile(oofile, d):
    '''Print out any linked image files in the Open Office file 
    oofile.  d is the options directory.
    '''
    if not os.path.isfile(oofile):
        err("'%s' is not a file%s" % (oofile, nl))
        return
    colors = {
        "missing"  : (c.lwhite, c.red),
        "notrel"   : (c.lwhite, c.magenta),
        "embedded" : c.lgreen,
    }
    image_files = GetImages(oofile, ignore_embedded=not d["-e"])
    if not image_files and not d["-m"]:
        # List the file
        out("%s%s" % (oofile, nl))
        return
    some_missing  = any([i[1] == "missing" for i in image_files])
    some_notrel   = any([i[1] == "notrel"  for i in image_files])
    some_embedded = any([i[1] == "embedded"  for i in image_files])
    if d["-m"] and not (some_missing or some_notrel):
        # If we're only supposed to list missing stuff and this OO
        # file had neither, then return.
        return
    if d["-l"]:
        # Only list the OO files, not their contents.  We'll color
        # code them to indicate missing or notrel content.  "missing"
        # takes precedence over "notrel" and both take precedence over
        # "embedded".
        if some_embedded:
            c.fg(colors["embedded"])
        if some_notrel:
            c.fg(colors["notrel"])
        if some_missing:
            c.fg(colors["missing"])
        out(oofile)
        c.normal()
        out(nl)
        return
    if d["-m"]:
        # image_files can be empty or only contain embedded files, in
        # which case we should return.
        if not image_files:
            return
        if all([IsEmbeddedImage(i[0]) for i in image_files]):
            return
    c.normal()
    out(oofile)
    out(nl)
    for name, state in image_files:
        if IsEmbeddedImage(name) and not d["-e"]:
            continue
        if d["-m"] and not state:
            continue
        out(" "*4)
        out(name)
        out(" ")
        if state in ("missing", "notrel", "embedded"):
            c.fg(colors[state])
            out("[%s]" % state)
            c.normal()
        out(nl)

def ProcessDirectory(directory, d):
    if not os.path.isdir(directory):
        err("'%s' is not a directory%s" % (directory, nl))
        return
    # The loop will visit each directory in directory's tree
    for root, dirs, files in os.walk(directory):
        chunks = Normalize(root).split("/")
        if ".hg" in chunks or "RCS" in chunks or "rcs" in chunks:
            continue  # Ignore Mercurial and RCS directories
        for file in files:
            name, ext = os.path.splitext(file)
            if ext in _oo_ext:
                oofile = J(root, file)
                if oofile[:2] == "./":  # Remove './' prefix
                    oofile = oofile[2:]
                ProcessFile(oofile, d)

def SearchDirectories(directories, d):
    for directory in directories:
        ProcessDirectory(directory, d)

def main():
    d = {} # Options dictionary
    args = ParseCommandLine(d)
    d["start_dir"] = os.getcwd()
    if d["-r"]:
        #dirs = [Normalize(os.path.abspath(i)) for i in args]
        SearchDirectories(args, d)
    else:
        if not args:
            out("Need at least one Open Office file" + nl)
            exit(1)
        try:
            for file in args:
                ProcessFile(file, d)
        finally:
            os.chdir(d["start_dir"])
if __name__ == "__main__": 
    main()
