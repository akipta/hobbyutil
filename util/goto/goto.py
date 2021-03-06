'''
Python module to select items from a configuration file.  See the
Usage() function for how to use it.

26 Jun 2014: this script has been edited significantly  to work in a
Linux environment.  I haven't tested it under Windows/cygwin.

----------------------------------------------------------------------
Copyright (C) 2008, 2014 Don Peterson
Contact:  gmail.com@someonesdad1

                         The Wide Open License (WOL)

Permission to use, copy, modify, distribute and sell this software and its
documentation for any purpose is hereby granted without fee, provided that
the above copyright notice and this license appear in all source copies.
THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF
ANY KIND. See http://www.dspguru.com/wide-open-license for more
information.
'''
 
import sys
import getopt
import os
from collections import OrderedDict

#xx
from pdb import set_trace as xx #xx
if 1: #xx
    import debug #xx
    debug.SetDebugger() #xx

# Stream function for error messages.  Note that this stream is also
# used for the selection messages because stdout is used to return the
# user's choice.
err = sys.stderr.write

# The selected directory will be printed to this stream.
out = sys.stdout.write

# The following character is used to separate fields in the
# configuration file.  It should be a character string that won't 
# show up in file names.  Note Linux allows any characters in
# filenames except '/' and the null character, so your safest choice
# is the null character if you want to use only one character.  
sep_string = ";"

max_num_width = 2       # Maximum width of prompt numbers
max_alias_width = 8     # Maximum width of aliases
nl = "\n"

def Usage():
    name = sys.argv[0]
    err('''Usage:  %(name)s [-c] [-t] goto_file  num_or_alias
  Prints a list of directory choices read from the goto_file and
  prompts you to pick one (set num_or_alias to 0 to be prompted;
  otherwise, the translation of the number or alias is made directly).
  Your choice is returned, printed to stdout.  Lines in the goto_file
  are of the form
        # Comments
        path
        name | path
        name ! short_alias | path
  The first form is just the path; this is printed verbatim.  The
  second form shows the path with a shorter string describing the
  location; the shorter (more descriptive) string is printed in the
  list.  The third shows a short text alias after the ! that can be
  used instead of a choice number (intended for directories you go to
  a lot).  If you pass the short_alias on the command line, you'll get
  that directory immediately rather than being prompted with a list of
  directories.  You can also pass the choice number (> 0) on the
  command line and go to that choice immediately.

Options
  -c
    Changes the cygwin form of a path to a Windows style path.  For
    example, /cygdrive/c/something --> c:/something.
  -t
    Print out files in the config file that don't exist.
''' % locals())
    exit(1)

def FixPath(path, d):
    '''If d["-c"] is True, change strings like /cygdrive/c/windows
    into c:/windows.  Note this routine will NOT fix up strings like /
    or /cygdrive, as they have no portable meaning under Windows.
    '''
    if not d["-c"]:
        return path
    path = path.replace("\\", "/")  # Use forward slashes
    import re
    if path == "/" or path == "/cygdrive" or path == "/cygdrive/":
        raise RuntimeError("Improper path for fixup")
    # Handle cases like '/c' and '/c/'
    r = re.compile(r"/(\w)/?$")
    mo = r.match(path)
    if mo:
        return mo.groups()[0] + ":/"
    # Cases like /cygdrive/c
    r = re.compile(r"^/cygdrive/(\w)$")
    mo = r.match(path)
    if mo:
        return mo.groups()[0] + ":/"
    # Cases like /cygdrive/c/something
    r = re.compile(r"^/cygdrive/(\w)(/.*)$")
    mo = r.match(path)
    if mo:
        return mo.groups()[0] + ":" + mo.groups()[1]
    return path

def StripComments(line):
    position = line.find("#")
    if position != -1:
        line = line[:position]
    return line.strip()

def Error(msg):
    err(msg)
    if msg[-1] != nl:
        err(nl)
    exit(1)

def ConstructGotoDictionary(goto_file, d):
    '''Build the following data structures.  dir_map translates a
    number or a name into a directory.  aliases translates an alias
    into a name.
    dir_map = {
        # Note key can be an integer or string.  If it's a string, the
        # user provided a name for the path.
        number1 : "path1",
        "name1" : "path2"
        ...
    }
    aliases = {
        "alias1" : "name1",
        ...
    {
    '''
    # We used OrderedDicts to print out the items in the order the
    # user put them into the file.
    dir_map, aliases, choice = OrderedDict(), OrderedDict(), 0
    for i, Line in enumerate(file(goto_file)):
        line = StripComments(Line)
        if not line:
            continue
        fields = [j.strip() for j in line.split(sep_string)]
        name, alias, path = "", "", ""
        choice += 1  # Number displayed to user
        if len(fields) == 1:  # Only directory path given
            path = fields[0]
            if path:
                dir_map[choice] = path
            else:
                msg = "Empty path on line %d in '%s'"
                msg += "  '%s'" % Line
                Error(msg % (i + 1, goto_file))
        elif len(fields) == 2: # Had a name and a directory path
            name, path = fields
            if name and path:
                dir_map[name] = path
            else:
                msg = "Empty name or path on line %d in '%s'"
                msg += "  '%s'" % Line
                Error(msg % (i + 1, goto_file))
        elif len(fields) == 3:  # Had a name, alias, and path
            name, alias, path = fields
            if name and alias and path:
                dir_map[name] = path
                aliases[alias] = name
            else:
                msg = "Empty name, alias, or path on line %d in '%s'"
                msg += "  '%s'" % Line
                Error(msg % (i + 1, goto_file))
        else:
            Error("Too many fields on line %d in '%s'" % (i + 1, goto_file))
    d["dir_map"] = dir_map
    d["aliases"] = aliases

def PrintAlias(alias_tuple):
    assert len(alias_tuple) == 2 and isinstance(alias_tuple, tuple)
    maxlen = 8
    alias, path = alias_tuple
    if len(alias) > maxlen:
        Error("Alias '%s' is longer than %d characters" % (alias, maxlen))
    err("%-8s %s\n" % alias_tuple)

def CheckFiles(od):
    '''od is an ordered dictionary with values (msg, filename).  Check
    that each filename item is a valid file.
    '''
    bad = False
    for msg, filename in od.values():
        if not filename:
            continue
        if not os.path.isfile(filename):
            err("'%s' doesn't exist%s" % (filename, nl))
            bad = True
    return bad

def ParseCommandLine(d):
    d["-c"] = False     # Convert cygwin-style paths to Windows-style
    d["-t"] = False     # Check paths
    d["prompt_func"] = input if sys.version_info[0] >= 3 else raw_input
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "ct")
    except getopt.GetoptError as e:
        msg, option = e
        Error(msg)
    for opt in optlist:
        if opt[0] == "-c":
            d["-c"] = True
        if opt[0] == "-t":
            d["-t"] = True
    if d["-t"]:
        args = [args[0], 0]
    else:
        if len(args) != 2:
            Usage()
    return args

def PromptUser(dm, aliases, d):
    '''The choices are in the directory dictionary; its keys are
    either integers for unnamed directories or strings for named
    directories.  aliases is a dictionary of strings that translate to
    names.
    '''

def GetDict(goto_file):
    '''Construct an ordered dictionary whose keys are the responses
    the user is allowed to type in.  The values are a tuple of (msg,
    path) where msg is the string to show the user in the selection
    list and path is the directory to change to.
 
    An example is
        od = OrderedDict{
            # Integer responses
            "1" : ("1   /doc/phalanges", "/doc/phalanges"),
            "2" : ("2   Treatise on phalanges", "/doc/treatise"),
            ...
            ""  : (None, None),  # Line separator & null response
            # Alias responses
            "ph" : ("ph       Phalanges index", /doc/phalanges/index"),
            ...
        }
    '''
    # First we must build a list of the numbered items and the aliased
    # items.
    numbered, aliases = [], []
    lines = open(goto_file).readlines()
    for linenum, Line in enumerate(lines):
        line = StripComments(Line)
        if not line:
            continue
        name, alias, path = "", "", ""
        fields = line.split(sep_string)
        if len(fields) == 1:  # Only directory path given
            path = fields[0].strip()
            if path:
                numbered.append((path, path))
            else:
                msg = "Empty path on line %d in '%s'"
                msg += "  '%s'" % Line
                Error(msg % (linenum + 1, goto_file))
        elif len(fields) == 2: # Had a name and a directory path
            name, path = [i.strip() for i in fields]
            if name and path:
                numbered.append((name, path))
            else:
                msg = "Empty name or path on line %d in '%s'"
                msg += "  '%s'" % Line
                Error(msg % (linenum + 1, goto_file))
        elif len(fields) == 3:  # Had a name, alias, and path
            name, alias, path = [i.strip() for i in fields]
            if name and alias and path:
                aliases.append((alias, name, path))
            else:
                msg = "Empty name, alias, or path on line %d in '%s'"
                msg += "  '%s'" % Line
                Error(msg % (linenum + 1, goto_file))
        else:
            Error("Too many fields on line %d in '%s'" % (i + 1, goto_file))
    od, choice = OrderedDict(), 0
    # Construct numbered items
    for i, (name, path) in enumerate(numbered):
        choice = i + 1
        msg = "%-*d  %s" % (max_num_width, choice, name)
        od[str(choice)] = (msg, path)
    # Empty string that indicates to just return with no string
    od[""] = ("", "")
    # Construct aliased items
    aliases.sort()
    for alias, name, path in aliases:
        msg = "%-*s  %s" % (max_alias_width, alias, name)
        od[alias] = (msg, path)
    return od

def main():
    d = {}  # Options dictionary
    # choice is the number/alias the user supplied on the command line
    # (use "0" to be prompted for your choice).
    goto_file, choice = ParseCommandLine(d)
    # Construct an ordered dictionary of choices.  The keys will be
    # the allowed strings the user can type in at the command line.
    od = GetDict(goto_file)
    if d["-t"]:
        exit(CheckFiles(od))
    if choice == "0":
        # Prompt the user for the desired choice.  We print messages
        # to stderr because the selected directory will be printed to
        # stdout.  
        for prompt_string, path in od.values():
            err(prompt_string + nl)
        err("Selection? ")
        while True:
            selection = d["prompt_func"]().strip()
            if selection in od:
                msg, path = od[selection]
                out(FixPath(path, d) + nl)
                break
            else:
                msg = "'%s' is not valid choice.  Try again.%s"
                err(msg % (selection, nl))
    else:
        if choice in od:
            msg, path = od[choice]
            out(FixPath(path, d) + nl)
        else:
            Error("'%s' is not a valid choice" % choice)
main()

