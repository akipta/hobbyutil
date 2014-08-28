''' 
Script to compare directories using set operations.  Usage:

    dirset operation dir1 dir2

Operations (only first character significant):

    diff        
        dir1 - dir2; i.e., files in dir1 that are not in dir2.

    equal        
        Returns 0 if dir1 and dir2 are the same.

    intersection
        Show the common files.

    union
        Show the union of both sets.

    subset
        Returns 0 if dir2 is a subset of dir1.

    psubset
        Returns 0 if dir2 is a proper subset of dir1.

Note:  this was written for python 1.5.2 before sets existed in
python.  

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

import sys, os, string

allowed_operations = [ "d", "e", "i", "u", "s", "p", "x"]
dirset = set()
err = sys.stderr.write
status_good  = 0
status_bad   = 1
status_error = 2

def Usage():
    print '''
Usage:  %s operation dir1 dir2
  Treats the two directory's file entries as sets and computes various
  set functions on them.  All files underneath each directory are
  included in the respective sets.

Operations (only need to use first character):
  diff          Shows files in dir1 that are not in dir2
  equal         Returns 0 if dir1 and dir2 contain same files
  intersection  Shows files that are common
  union         Shows union of both sets of files
  subset        Returns 0 if dir2 is a subset of dir1
  psubset       Returns 0 if dir2 is a proper subset of dir1
  xor           Show symmetric difference (files in one or other not both)

Example of use
  Suppose you wanted to update two directory trees d1 and d2.  Both
  contain files that the other tree should have if they're not
  present; in addition, you need to decide which way common files
  should be copied, if appropriate.  To get a list of all the files
  that are not common, use
    python dirset.py xor d1 d2
  For the files in d1 that are not in d2, use
    python dirset.py diff d1 d2
  For the files in d2 that are not in d1, use
    python dirset.py diff d2 d1
  To look at the files with the same names that belong to both
  directory trees, use
    python dirset.py intersection d1 d2
  You might want to compare modification times of the last group of
  files before deciding which ones need to be updated.
'''[1:-1] % sys.argv[0]
    sys.exit(status_error)

def CheckDir(dir):
    if not os.path.isdir(dir):
        err("'%s' is not a directory\n" % dir)
        sys.exit(status_error)

def CheckParameters(operation, dir1, dir2):
    first_char = operation[0]
    if first_char not in allowed_operations:
        err("'%s' is bad first character for operation.\n" % first_char)
        Usage()
    CheckDir(dir1)
    CheckDir(dir2)
    return first_char

def GetDirSet(dir):
    '''cd to the directory and recursively get all of its files
    '''
    currdir = os.getcwd()
    if dir != ".":
        if os.path.isdir(dir):
            try:
                os.chdir(dir)
            except:
                err("Couldn't cd to '%s'\n" % dir)
                sys.exit(status_error)
        else:
            err("'%s' is not a directory\n" % dir)
            sys.exit(status_error)
    global dirset
    dirset = set()
    os.path.walk(".", Visit, [])
    os.chdir(currdir)
    return dirset
    
def Visit(arg, dirname, names):
    global dirset
    for name in names:
        dirset.add(dirname + "/" + name)

def main():
    if len(sys.argv) != 4:
        Usage()
    operation = sys.argv[1]
    dir1      = sys.argv[2]
    dir2      = sys.argv[3]
    opcode = CheckParameters(operation, dir1, dir2)
    dirset1 = GetDirSet(dir1)
    dirset2 = GetDirSet(dir2)
    s1 = set(dirset1)
    s2 = set(dirset2)
    if opcode == "d":
        result_set = s1 - s2
    elif opcode == "e": # Equality
        # Negation to match UNIX status conventions
        sys.exit(not (s1 == s2))  
    elif opcode == "i": # Intersection
        result_set = s1 & s2
    elif opcode == "u": # Union
        result_set = s1 | s2
    elif opcode == "s": # Subset
        # Negation to match UNIX status conventions
        sys.exit(not s2 <= s1)
    elif opcode == "p": # Proper subset
        # Negation to match UNIX status conventions
        sys.exit(not s2 < s1)
    elif opcode == "x": # Symmetric difference
        result_set = s1 ^ s2
    # Print out the result set
    files = list(result_set)
    files.sort()
    for file in files:
        print file.replace("\\", "/")

main()
