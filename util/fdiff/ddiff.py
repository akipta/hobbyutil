manual = '''
NAME
    ddiff -- Show file differences between two directory trees.

SYNOPSIS
    ddiff [options] [comp_op] srcdir destdir

DESCRIPTION
    This program compares two directory trees and generates a list to 
    stdout that contains the files that meet the logic of the specified 
    comparison operator(s).

    The comparison operators (comp_op) are:

        ois          File is only in srcdir tree
        oid          File is only in destdir tree
        com          File is common to both trees
        !com         File is in one tree but not the other

        stn          srcdir tree's file is newer
        sto          srcdir tree's file is older
        t=           Identical time stamps
        t!=          Time stamps are different

        ==           Files are identical
        !=           Files are different

        z=           Same sizes
        z!=          Don't have same sizes
        zslt         src size less than dest
        zsgt         src size greater than dest

    You can have more than one comp_op on the command line; the effect is 
    to OR them together.  This is used for the default output when no 
    comp_op is specified:  the default behavior is as if you gave the two 
    comp_ops 'ois' and 'stn'.  This prints out files that are only in 
    srcdir or where the srcdir version is newer.

    The program will recursively descend all subdirectories of both srcdir
    and destdir.

    Comparing timestamps is fast, as is comparing sizes.  Probably the
    best method for detecting differences, however, is using the ==
    and != operators.  However, these will be slow on large directory
    trees because all of the bytes of the files will be compared.

    Note that Mercurial and RCS directories are ignored by default;
    use the -R option to make sure they're not ignored if you need to
    see their files.

    One example use of the tool is to identify files that are
    potentially links to the same file.  For example, you could use
    the == operator to identify equal files, then use 'ls -i' to look
    at the inodes of the matching files.

OPTIONS
    -c  Produce the output in "copy" format.  For each file that meets the
        comparison criteria, two strings are printed on each line.  The first
        string is the source file and the second string is the destination
        file.  Both are absolute path names.  The path names are separated by a
        tab character.  This format is suitable for input to a script to copy 
        the files; for example, a Bourne shell script might do the following:

            while read line ; do
                cp -f $line
            done

        This would force the destdir to have the same copies of the files 
        that the srcdir had that met the criterion.  This is meant to be 
        easy to use, not fast.  If you want to copy a large amount of 
        data, it would be more efficient to write a C program that reads 
        the file names from the standard input and performs the copy.

    -d  DOS format.  Makes the output pathnames have backslashes instead
        of forward slashes.

    -R  Don't ignore revision control system directories.

    -h  Print a copy of the man page to stdout.

    -q  Puts double quotes around the filenames when the -c option is used.
        This allows the output to be used on systems that allow spaces in the 
        file name.

    -Q  Same as -q, but the quotes are escaped.

EXAMPLES
    I developed this script to allow me to synchronize the contents of two 
    different directory trees.  Here's an example of how I use it to 
    synchronize my home and work PCs using a read/write CD.  Suppose I have
    two directories c:/working on both home and work PCs (I use forward slashes
    because I work in the Korn shell).  Also assume there's a directory 
    d:/working on the writable CD that I use for transporting the files.  
    Suppose I was on my home machine and I wanted to make sure the writable CD
    and my home /working directory contained the identical files.  I'd perform
    the following tasks:
        
        1.  Identify those files that are on the CD, but not on my home
            PC:

                python ddiff.py oid c:/working d:/working

            I'd then copy these files to the c:/working directory on my PC.

        2.  Identify those files that are on the PC but not on the CD
            or that the CD copy is not the same as the PC copy:

                python ddiff.py ois != c:/working d:/working

            These files would then get copied to the CD.  These first two steps
            ensure that the PC and CD have identical files (although the
            modification times of corresponding files might be different).

        3.  When I got to work, I'd use the following command to identify
            those files on the CD that are different from my work PC
            c:/working directory's files or are only on the CD:

                python ddiff.py ois != d:/working c:/working

            I'd copy these files from the CD to c:/working.

        4.  Finally, I'd identify those files that are in the c:/working
            directory tree of my work PC, but that are not on the CD.  The
            following command would do this:
                
                python ddiff.py ois c:/working d:/working

            These files would then be copied to the CD so that I could copy
            them to my home PC when I got home.

    Of course, if you don't mind wiping out the /working directory on one
    of the PCs, then it's a simple matter to just make a complete copy to the
    CD and copy it to the destination PC.  This script is intended to handle
    the more complicated case when both directory trees may contain files
    of value that you don't want to lose.

    Once I have the directory trees synchronized by using the actual file
    comparisons (which ensures that I have the same binary copies), I ensure
    that the files have the same modification times (using the touch command).
    This then lets me use ddiff.py with the stn comparison operator to keep
    things synchronized -- this is faster than using a binary compare of 
    corresponding files.  The only constraint is that the systems must have
    their system clock times agree within less than the time it takes me to
    travel between the two systems.

    A word of caution:  you'll want to be cognizant of the case where the
    two different computers might have two different versions of the
    same program and both versions have content you want to keep.  In
    this case, you'd want to merge the files rather than copy one over 
    the other.  There's no easy way for the program to identify this
    situation, so you may want to develop the habit of using ddiff to
    identify files that are different, then examine the files in detail.
    Otherwise, blindly copying one over the other will lose some changes.

NOTES
    June 2014 update:  there are numerous GUI tools out there that can
    compare the files in two directories.  Microsoft shipped
    windiff.exe with their C++ compiler and there's an excellent
    WinDiff project on Sourceforge (I used WinDiff for many years on
    my Windows computer and it was my favorite differencing tool).
    kdiff3 is another difference/merge tool that can be found on
    multiple platforms.  On Linux, meld is an uncluttered, easy-to-use
    tool that also knows how to deal with modern version control
    systems.  I was surprised to see that kdiff3 required 100 MB to
    install on my Linux system and it is pretty sluggish.  I'll have
    to compare meld to kdiff3 on some merges, but if meld handles
    merges OK, it will be my tool of choice.

    That said, I still find myself using this 15-year-old python
    script because I know how it works and trust its output.  I just
    used it to check a 6 GB backup of my key datafiles and it found
    all the changes I'd made.  It did take 10 minutes, but that was
    38,000 files to process.

ENVIRONMENT VARIABLES
     ddiff uses no environment variables.

DIAGNOSTICS
     Possible exit status values are:

     0  Successful completion.

     1  Failure.  A message describing the problem will be printed to stderr.

WARNINGS
    If the filenames can contain tab characters, you may want to go into
    the source and modify the separation character.

    This has been tested running under Windows NT 4.0 with the MKS Toolkit 
    version 5.2 and python 1.5.1.  It should work unchanged on any UNIX system,
    but you'd better test it yourself to be sure.  

    If you are using this script to synchronize two directories on different 
    systems, you'll want to make sure that the system times are equal to within
    the travel time between the systems.  Otherwise, the time stamps could be
    wrong.  In this case, you could use the != comparison operator instead of
    using time stamps.

SEE ALSO
    ddiffcp.py -- a python script that can perform the updating for you based
    on the output of the ddiff.py script.
'''[1:-1]

import sys, os, string

pyver = sys.version_info[0]
if pyver == 3:
    walk = os.walk
else:
    walk = os.path.walk
    
retvalG        = 0   # Place that collects the exit status
debug          = 0   # Turns on debug printing
comp_opsG      = []  # Comparison operators passed on the command line.
srcdirG        = ""  # Source directory passed in on the command line.
                     # (Will be converted to a full path name.)
src_dictG      = {}  # Will hold set of src files
destdirG       = ""  # Destination directory passed in on the command line.
                     # (Will be converted to a full path name.)
dest_dictG     = {}  # Will hold set of dest files
copy_formatG   = 0   # -c option flag
dos_slashesG   = 0   # -d option flag
quotesG        = 0   # -q option flag
incl_rcs       = 0   # -R option flag Include rev control directories
escape_quotesG = 0   # -Q option flag
out_dictG      = {}  # Will contain the output filenames that meet the
                     # comparison conditions
only_in_srcG   = {}  # Set Src - Dest
only_in_destG  = {}  # Set Dest - Src
common_filesG  = {}  # Set Src * Dest
size_indexG    = 0   # Index for dictionary lists
time_indexG    = 1   # Index for dictionary lists

# This list contains the allowed comparison operators.
allowed_comp_opsG = ( 
    "ois", "oid", "com", "!com", "stn", "sto", "t=", "t!=", "==",
    "!=", "z=", "z!=", "zslt", "zsgt",
)

# The following strings are used to identify revision control
# directories that should be ignored
rcs_dirs = ("RCS", ".hg")

def out(*v, **kw):
    sep = kw.setdefault("sep", " ")
    nl  = kw.setdefault("nl", True)
    stream = kw.setdefault("stream", sys.stdout)
    stream.write(sep.join([str(i) for i in v]))
    if nl:
        stream.write("\n")

def err(s, **kw):
    kw["stream"] = sys.stderr
    out(s, **kw)

def Error(msg, status=1):
    out(msg, stream=sys.stderr)
    exit(status)

def Usage():
    out('''Usage:  ddiff [options] [comparison_operators] srcdir destir
Recursively compares files in two directory trees.
The comparison_operators are:
    ois          File is only in srcdir tree
    oid          File is only in destdir tree
    com          File is common to both trees
    !com         File is in one tree but not the other
    stn          srcdir tree file newer
    sto          srcdir tree file older
    t=           Identical time stamps
    t!=          Different time stamps
    ==           Files are identical
    !=           Files are different
    z=           Same sizes
    z!=          Don't have same sizes
    zslt         src size less than dest
    zsgt         src size greater than dest
Options:
    -c      Output in "copy" format
    -d      DOS format:  output has backslashes
    -h      Print man page to stdout
    -q      Escape the double quotes in -c mode
    -Q      Same as -q, but the quotes are escaped.''')
    sys.exit(2)

def PrintManual():
    out(manual)
    sys.exit(0)

def PutForwardSlashes(dir):
    return string.replace(dir, '\\', '/')

def GetAbsoluteDirectory(dir):
    '''Return a string that is an absolute path that is derived from
    dir.  Exit if dir is not a valid directory.  Note we will cd to
    the directory, use os.getcwd() to get a valid absolute path, then
    cd back to where we were.
    '''
    if dir == "":
        raise "Empty directory string"
    fulldir = dir
    if not os.path.isabs(dir):
        fulldir = PutForwardSlashes(os.getcwd() + os.sep + dir)
    if not os.path.isdir(fulldir):
        out("'%s' is not a directory" % dir)
        sys.exit(1)
    fulldir = PutForwardSlashes(fulldir)
    curdir = os.getcwd()
    os.chdir(fulldir)
    fulldir = os.getcwd()
    os.chdir(curdir)
    return PutForwardSlashes(fulldir)

def ParseCommandLine():
    '''Get options, then qualify the passed in directories and
    change them to full path names.  Also store the comparison
    operators.
    '''
    import getopt
    global copy_formatG, escape_quotesG, dos_slashesG, quotesG
    global srcdirG, destdirG, comp_opsG, incl_rcs 
    if len(sys.argv) < 2:
        Usage()
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "cdhqQR")
    except getopt.error, str:
        out(str)
        sys.exit(1)
    for opt in optlist:
        if opt[0] == "-c":
            copy_formatG = 1
        if opt[0] == "-d":
            dos_slashesG = 1
        if opt[0] == "-h":
            PrintManual()
        if opt[0] == "-q":
            quotesG = 1
        if opt[0] == "-Q":
            quotesG = 1
            escape_quotesG = 1
        if opt[0] == "-R":
            incl_rcs = 1
    if len(args) < 2:
        Usage()
    srcdirG  = GetAbsoluteDirectory(args[-2])
    destdirG = GetAbsoluteDirectory(args[-1])
    if len(args) > 2:
        for op in args[:-2]:
            comp_opsG.append(op)
            if op not in allowed_comp_opsG:
                out("%s is not an allowed comparison operator" % op)
                sys.exit(1)
    else:
        # Set the default comparison operators
        comp_opsG = [ "ois", "stn" ]
    if debug:
        out("Command line   =", sys.argv)
        out("copy_formatG   =", copy_formatG)
        out("quotesG        =", quotesG)
        out("escape_quotesG =", escape_quotesG)
        out("srcdirG        =", srcdirG)
        out("destdirG       =", destdirG)
        out("comp_opsG      =", comp_opsG)

def files_have_same_bytes(src, dest):
    '''Read in the bytes from these files and compare them.  We can
    assume that the files are the same sizes.
    '''
    buffer_size = 100000
    def CloseFiles(a, b):
        a.close()
        b.close()
    try:
        ifp_src  = open(src, "rb")
    except:
        sys.stderr.write("Couldn't open %s\n" % src)
        retvalG = 1
        return
    try:
        ifp_dest = open(dest, "rb")
    except:
        sys.stderr.write("Couldn't open %s\n" % dest)
        retvalG = 1
        return
    try:
        srcbuf  = ifp_src.read(buffer_size)
        destbuf = ifp_dest.read(buffer_size)
        if len(srcbuf) == 0 and len(destbuf) == 0:
            # At EOF; return 1 since they're equal
            CloseFiles(ifp_src, ifp_dest)
            return 1
        if len(srcbuf) != len(destbuf):
            raise "Internal error:  buffers unequal size"
        if srcbuf != destbuf:
            CloseFiles(ifp_src, ifp_dest)
            return 0
    except:
        sys.stderr.write("Error in comparing %s to %s\n" % (src, dest))
        CloseFiles(ifp_src, ifp_dest)
        return 0
    CloseFiles(ifp_src, ifp_dest)
    return 1

# In the following functions, not that the src or dest directory
# gets appended to the key, so all that's needed at the end is
# to just print a sorted list of the keys in the dictionary.

def OnlyInSource(dict):
    for key in only_in_srcG.keys():
        dict[srcdirG + "/" + key] = ""

def OnlyInDestination(dict):
    for key in only_in_destG.keys():
        dict[destdirG + "/" + key] = ""

def CommonFiles(dict):
    for key in src_dictG.keys():
        dict[srcdirG + "/" + key] = ""

def NotCommonFiles(dict):
    OnlyInSource(dict)
    OnlyInDestination(dict)

def SourceNewer(dict):
    for key in src_dictG.keys():
        if src_dictG[key][time_indexG] > dest_dictG[key][time_indexG]:
            dict[srcdirG + "/" + key] = ""

def SourceOlder(dict):
    for key in src_dictG.keys():
        if src_dictG[key][time_indexG] < dest_dictG[key][time_indexG]:
            dict[srcdirG + "/" + key] = ""

def EqualModTime(dict):
    for key in src_dictG.keys():
        if src_dictG[key][time_indexG] == dest_dictG[key][time_indexG]:
            dict[srcdirG + "/" + key] = ""

def NotEqualModTime(dict):
    for key in src_dictG.keys():
        if src_dictG[key][time_indexG] != dest_dictG[key][time_indexG]:
            dict[srcdirG + "/" + key] = ""

def BytesAreEqual(dict):
    '''We'll first check to see if they are the same size.  If they're
    not, they don't need to be checked.
    '''
    for key in src_dictG.keys():
        if src_dictG[key][size_indexG] != dest_dictG[key][size_indexG]:
            continue
        src  = srcdirG + "/" + key
        dest = destdirG + "/" + key
        if files_have_same_bytes(src, dest):
            dict[srcdirG + "/" + key] = ""

def BytesAreNotEqual(dict):
    '''We'll first check to see if they are not the same size.  If they're
    not, then they can immediately be added to the out dictionary.
    '''
    for key in src_dictG.keys():
        if src_dictG[key][size_indexG] != dest_dictG[key][size_indexG]:
            dict[srcdirG + "/" + key] = ""
            continue
        src  = srcdirG + "/" + key
        dest = destdirG + "/" + key
        if not files_have_same_bytes(src, dest):
            dict[srcdirG + "/" + key] = ""

def SameSize(dict):
    for key in src_dictG.keys():
        if src_dictG[key][size_indexG] == dest_dictG[key][size_indexG]:
            dict[srcdirG + "/" + key] = ""

def DifferentSize(dict):
    for key in src_dictG.keys():
        if src_dictG[key][size_indexG] != dest_dictG[key][size_indexG]:
            dict[srcdirG + "/" + key] = ""

def SourceIsSmaller(dict):
    for key in src_dictG.keys():
        if src_dictG[key][size_indexG] < dest_dictG[key][size_indexG]:
            dict[srcdirG + "/" + key] = ""

def SourceIsBigger(dict):
    for key in src_dictG.keys():
        if src_dictG[key][size_indexG] > dest_dictG[key][size_indexG]:
            dict[srcdirG + "/" + key] = ""

def ProcessDictionaries():
    '''This routine will go through the two dictionaries src_dictG
    and dest_dictG and produce the two dictionaries only_in_srcG and
    only_in_destG.  The common files will remain in src_dictG and
    dest_dictG.
    '''
    global only_in_srcG, only_in_destG, common_filesG
    global src_dictG, dest_dictG
    for key in src_dictG.keys():
        element = src_dictG[key]
        if key not in dest_dictG:
            only_in_srcG[key] = element
            del src_dictG[key]
    for key in dest_dictG.keys():
        element = dest_dictG[key]
        if key not in src_dictG:
            only_in_destG[key] = element
            del dest_dictG[key]
    assert(len(src_dictG) == len(dest_dictG))
    if debug:
        out("only_in_srcG  =", only_in_srcG)
        out("only_in_destG =", only_in_destG)
        out("src_dictG     =", src_dictG)
        out("dest_dictG    =", dest_dictG)

def DirectoryAction(file_dict, dirname, names):
    '''This function gets called in a directory walk for each directory.
    The names list contains the contents of the directory we are in,
    which is named dirname.  stat each file (ignore the directories)
    and put the size and modification time in the dictionary file_dict.
    The first two letters of the name will begin with './', so strip
    those off.
    '''
    # If it's a revision control directory, return if we're ignoring
    # them.
    S = set(dirname.replace("\\", "/").split("/"))
    if not incl_rcs:
        for i in rcs_dirs:
            if i in S:
                return
    for filename in names:
        file = string.replace(dirname + "/" + filename, "\\", "/")
        if os.path.isdir(file):
            continue
        try:
            s = os.stat(file)
        except:
            continue
        # Save just the file size (6) and modification time (8)
        file_dict[file[2:]] = [s[6], s[8]]  # Remove the leading "./"

def WalkDir(dir):
    '''Return a dictionary containing all the files in the directory
    tree rooted at dir.  The relative path name from dir will be 
    the dictionary key and a list of the size and modification time
    will be the value.
    '''
    curdir = os.getcwd()
    os.chdir(dir)
    file_dict = {}
    walk(".", DirectoryAction, file_dict)
    os.chdir(curdir)
    return file_dict

def PrintOut(file):
    q = ""
    if os.path.isdir(file):
        raise "Illegal directory '%s'" % file
        sys.exit(1)
    if copy_formatG and (quotesG or escape_quotesG):
        if escape_quotesG:
            q = "\\\""
        else:
            q = "\""
    src  = file
    dest = string.replace(file, srcdirG, "")
    dest = destdirG + dest  # Note the separating '/' is already there
    if copy_formatG:
        str = q + src + q + "\t" + q + dest + q
    else:
        str = src
    if dos_slashesG:
        str = string.replace(str, '/', '\\')
    out(str)

def main():
    global src_dictG, dest_dictG, out_dictG
    ParseCommandLine()
    src_dictG  = WalkDir(srcdirG)
    dest_dictG = WalkDir(destdirG)
    ProcessDictionaries()
    # Now process for each comparison operator on command line
    for op in comp_opsG:
        if op == "ois":
            OnlyInSource(out_dictG)
        elif op == "oid":
            OnlyInDestination(out_dictG)
        elif op == "com":
            CommonFiles(out_dictG)
        elif op == "!com":
            NotCommonFiles(out_dictG)
        elif op == "stn":
            SourceNewer(out_dictG)
        elif op == "sto":
            SourceOlder(out_dictG)
        elif op == "t=":
            EqualModTime(out_dictG)
        elif op == "t!=":
            NotEqualModTime(out_dictG)
        elif op == "==":
            BytesAreEqual(out_dictG)
        elif op == "!=":
            BytesAreNotEqual(out_dictG)
        elif op == "z=":
            SameSize(out_dictG)
        elif op == "z!=":
            DifferentSize(out_dictG)
        elif op == "zslt":
            SourceIsSmaller(out_dictG)
        elif op == "zsgt":
            SourceIsBigger(out_dictG)
        else:
            out("Internal error:  illegal operator allowed")
            sys.exit(1)
    if len(out_dictG) > 0:
        if debug:
            out("-" * 75)
        list = out_dictG.keys()
        list.sort()
        for file in list:
            PrintOut(file)

if __name__ == "__main__":
    main()
    sys.exit(retvalG)
