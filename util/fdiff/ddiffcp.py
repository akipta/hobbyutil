# Copies files as indicated from the output of the ddiff.py script.  You
# must use the -c option with ddiff.py for this script to work.
#
#####################################################################
#                                                                   #
#             WARNING!  this script will overwrite                  #
#                 read-only destination files.                      #
#                                                                   #
#####################################################################

import sys, os, string

err = sys.stderr.write

def RemovedFile(file):
    '''Remove the indicated file and return 1 if successful.  Otherwise
    return 0.
    '''
    try:
        os.stat(file)
    except:
        # It's not there
        return 0
    try:
        os.chmod(file, 0777)
    except:
        err("Warning:  couldn't make '%s' writable\n" % file)
        return 0
    try:
        os.unlink(file)
    except:
        err("Warning:  couldn't remove '%s'\n" % file)
        return 0
    return 1

def MakeDir(dirname):
    '''Make sure the indicated directory exists.  If not, extract the parent
    directory and call ourself recursively.
    '''
    head, dir = os.path.split(dirname)
    if not os.path.isdir(dirname):
        if not os.path.isdir(head):
            MakeDir(head)
        try:
            os.mkdir(dirname)
        except:
            err("Fatal error:  couldn't make directory '%s'\n" % dirname)
            sys.exit(1)

def CopyFile(src, dest):
    '''Makes the assumption that it can write to the destination.
    The buffer size is the number of bytes that are read in for 
    each read.  If we can't copy the file, we just return.
    '''
    buffer_size = 1000000
    try:
        s = os.stat(src)
        stattimes = (s[7], s[8])
    except:
        err("Warning:  couldn't stat '%s'\n" % src)
        return
    try:
        ifp = open(src, "rb")
    except:
        err("Warning:  Couldn't open '%s' for reading\n" % src)
        return
    if RemovedFile(dest):
        dirname, filename = os.path.split(dest)
        MakeDir(dirname)
        try:
            ofp = open(dest, "wb")
        except:
            err("Warning:  couldn't open '%s' for writing\n" % dest)
            ifp.close()
            return
        buffer = ifp.read(buffer_size) 
        while len(buffer) != 0:
            ofp.write(buffer)
            buffer = ifp.read(buffer_size) 
        ifp.close()
        ofp.close()
        print dest
        try:
            # Set mtime and atime same as source file
            os.utime(dest, stattimes)
        except:
            err("Warning:  couldn't set access times for '%s'\n" % dest)

def main():
    files = sys.stdin.readlines()
    if len(files) == 0:
        err("Warning:  no input lines\n")
    else:
        for file in files:
            while file[-1] == '\n' or file[-1] == '\r':
                file = file[:-1]
            list = string.split(file, "\t")
            if len(list) != 2:
                err("Bad input line:  '%s'\n" % file)
                sys.exit(1)
            CopyFile(list[0], list[1])

main()

