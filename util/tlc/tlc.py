'''
This python script will rename all of the files on the command line to
lowercase (or uppercase) names.  It will also rename directories if you
give it the -d option.

DP 5/2/98
'''
import os, string, sys


dbg = 0     # Set to nonzero to get debugging printouts
db  = "="   # Debugging string header

# Variables to hold option states
incdirs   = 0
recursive = 0
uppercase = 0

def is_file(file_name):
    mask = 0100000
    try:
        s = os.stat(file_name)
    except:
        return 0
    if (mask & s[0]) == mask:
        return 1
    else:
        return 0

def is_directory(dir_name):
    mask = 040000
    try:
        s = os.stat(dir_name)
    except:
        return 0
    if (mask & s[0]) == mask:
        return 1
    else:
        return 0

def Usage():
    print '''Usage:  tlc [-d] [-r] [-u] file1 [file2...]
    Renames files to all lowercase
    -d   Include directory names
    -r   Perform renaming recursively
    -u   Rename to all uppercase'''
    sys.exit(1)

def Expand(filespec):
    "Glob the files in the list filespec and return a flat list"
    from glob import glob
    list = []
    for arg in filespec:
        expanded = glob(arg)
        if len(expanded) > 0:
            for el in expanded:
                list.append(el)
    return list

def CheckCommandLine():
    global uppercase, recursive, incdirs, dbg, db
    files = []
    if len(sys.argv) < 2:
        Usage
    for arg in sys.argv[1:]:
        if arg == "-d":
            incdirs = 1
        elif arg == "-r":
            recursive = 1
        elif arg == "-u":
            uppercase = 1
        else:
            files.append(arg)
    if dbg:
        print "%s incdirs   = %d" % (db, incdirs)
        print "%s recursive = %d" % (db, recursive)
        print "%s uppercase = %d" % (db, uppercase)
    files = Expand(files)
    if len(files) < 1:
        print "No files given on command line"
        Usage()
    if dbg:
        print "%s Command line files =" % db,  files
    return files

def Rename(filespec):
    "Rename the file filespec to all upper or lower case."
    global uppercase, dbg, db
    if uppercase:
        new_name = string.upper(filespec)
    else:
        new_name = string.lower(filespec)
    #if new_name == filespec:
    #    return
    try:
        if dbg:
            print "%s Renaming '%s' to '%s'" % (db, filespec, new_name)
        os.rename(filespec, new_name)
    except os.error:
        print "Couldn't rename '%s' to '%s'" % (filespec, new_name)

def ProcessDirectory(dir_name):
    '''Rename the directory if the -d option is used.  In addition,
    if the -r (recursive) option is used, generate a list of files
    in this directory and process them too.
    '''
    global dbg, db
    if dbg:
        print "%s Processing directory '%s'" % (db, dir_name)
    if incdirs:
        Rename(dir_name)
    if recursive:
        old_dir = os.getcwd()
        os.chdir(dir_name)
        files = Expand("*")
        ProcessFiles(files)
        os.chdir(old_dir)

def ProcessFiles(file_list):
    '''This is where the renaming is done.  file_list is a list of 
    files to rename.
    '''
    global incdirs, dbg, db
    for file in file_list:
        if file == "":
            continue
        if is_directory(file):
            ProcessDirectory(file)
        else:
            Rename(file)

def FixCygnusNames(files):
    for ix in xrange(len(files)):
        file = files[ix]
        new = string.replace(file, "/cygdrive/", "")
        if len(new) != len(file):
            # It was a Cygnus type filename
            files[ix] = new[0] + ":" + new[1:]
    return files

def main():
    files = []
    files = CheckCommandLine()
    files = FixCygnusNames(files)
    ProcessFiles(files)

main()
