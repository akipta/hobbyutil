import sys, os, glob, getopt, os.path


usage = '''
Usage:  {sys.argv[0]} [options] dir1 [dir2...]
Replace spaces in filenames with underscores.  Note this tool operates on
whole directories.

Options
    -e      Process directory names too.
    -r      Act recursively.
    -n      Show what will happen, but don't do actual renaming.
    -u      Change underscores to spaces.
'''[1:-1].format(**globals())

show      = 0   # Show what will be done
sp, us = " ", "_"

def out(*v, **kw):
    sep = kw.setdefault("sep", " ")
    nl  = kw.setdefault("nl", True)
    stream = kw.setdefault("stream", sys.stdout)
    if v:
        stream.write(sep.join([str(i) for i in v]))
    if nl:
        stream.write("\n")

def Usage():
    out(usage)
    sys.exit(2)

def ParseCommandLine(d):
    d["-d"] = False     # Process directory names too
    d["-n"] = False     # Show what will happen
    d["-r"] = False     # Act recursively
    d["-u"] = False     # Change underscores to spaces
    if len(sys.argv) < 2:
        Usage()
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "nru")
    except getopt.error as str:
        out(str)
        sys.exit(1)
    for opt in optlist:
        if opt[0] == "-d":
            d["-d"] = True
        if opt[0] == "-n":
            d["-n"] = True
        if opt[0] == "-r":
            d["-r"] = True
        if opt[0] == "-u":
            d["-u"] = True
    if len(args) < 1:
        Usage()
    return args

def ProcessFile(root, file, d):
    if root is ".":
        root = ""
    oldfile = os.path.join(root, file)
    if d["-u"]:
        if us not in file:
            return
        newfile = os.path.join(root, file.replace(us, sp))
    else:
        if sp not in file:
            return
        newfile = os.path.join(root, file.replace(sp, us))
        assert sp not in newfile
    if d["-n"]:
        out(oldfile.replace("\\", "/"), "-->", newfile.replace("\\", "/"))
        return
    try:
        os.rename(oldfile, newfile)
    except Exception:
        out("Couldn't rename '%s' to '%s'; continuing" % (oldfile, newfile))

def ProcessDirectory(dir, d):
    if dir is not ".":
        head, tail = os.path.split(dir)
        if not tail:
            if sp in head:
                head = head.replace(" ", "_")
        else:
            if sp in tail:
                tail = tail.replace(" ", "_")
        newdir = os.path.join(head, tail)
        if d["-n"]:
            out(dir.replace("\\", "/"), "-->", newdir.replace("\\", "/"))
        else:
            try:
                os.rename(dir, newdir)
            except Exception:
                out("Couldn't rename '%s' to '%s'; continuing" % (dir, newdir))
    if d["-r"]:
        for root, dirs, files in os.walk(dir):
            if root not in d["visited_directories"]:
                d["visited_directories"].add(root)
                ProcessDirectory(root, d)
            for file in files:
                ProcessFile(root, file, d)
    else:
        dirglob = os.path.join(dir, "*")
        for file in glob.glob(dirglob):
            if os.path.isfile(file):
                ProcessFile(dir, file, d)

if __name__ == "__main__":
    d = {"visited_directories" : set()}
    for dir in ParseCommandLine(d):
        ProcessDirectory(dir, d)
