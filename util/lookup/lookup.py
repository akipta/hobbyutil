'''
TODO:
    * Figure out how to add in the information from
      words_syllables.py.

Script to look up words in various dictionaries.  For a demo of
capabilities, try

    python lookup.py "heav"
        Find all words with the string "heav" in them
    python lookup.py -dc "^mother$|^motherless$|^motherly$"
        Show all words/definitions/synonyms/type for the indicated
        regexps.  Note this produces colored output on a DOS/cygwin
        shell.  You can make it colored on e.g. a UNIX box if you're
        willing to write suitable escape-code stuff analogous to
        what's in the color module.
'''

import sys, re, os, getopt, subprocess, string

# The following are non-standard python modules that can be gotten
# from http://code.google.com/p/hobbyutil/; however, they should have
# been included in the zip file for this package.
from wrap import Wrap
import color

dbg = False   # Turn on for debug printing

# This script uses a grep-like tool to perform the searches.  The grep
# variable must point to a grep executable.  Use the grep_options to
# customize behavior.
grep = "c:/cygwin/bin/egrep.exe"
grep_options = [
    "-i",
    "--color=auto",   # GNU grep option
]

# You need to make the following variables point to the needed WordNet
# ASCII database files.  See the words.pdf file for details.
dir, W = "d:/p/pylib/", "types_of_words/WordNet/"
pj = os.path.join
wordnet_files = {
    "index" : pj(dir + W, "index.sense"),
    "adj"   : pj(dir + W, "data.adj"),
    "adv"   : pj(dir + W, "data.adv"),
    "noun"  : pj(dir + W, "data.noun"),
    "verb"  : pj(dir + W, "data.verb"),
    "dict"  : pj(dir, "words.wordnet"),
}

# Make the following dictionary point to the dictionary files you wish
# to use.
dir = "d:/p/pylib/"  # Directory where dictionaries are
dictionary_files = {
    0: pj(dir, "words.ogden"),          # Ogden's 851 word list
    1: pj(dir, "words.2of12"),          # 42 kwords
    2: pj(dir, "words"),                # 93 kwords
    3: pj(dir, "words.2005.wayne"),     # Big dictionary 274 kwords
    4: wordnet_files["dict"],           # WordNet words, 155 kwords
}
del dir, pj, W

# The following dictionary contains the open streams to the WordNet
# data files.
streams = {
    "a" : open(wordnet_files["adj"]),
    "r" : open(wordnet_files["adv"]),
    "n" : open(wordnet_files["noun"]),
    "v" : open(wordnet_files["verb"]),
}
streams["s"] = streams["a"]

# Get the number of columns in the screen.  Use the COLUMNS
# environment variable if it is defined; otherwise use 79.
columns = int(os.environ["COLUMNS"]) - 1 if "COLUMNS" in os.environ else 79

# Color-related stuff.  Note:  the color module is a python module
# that uses WConio to generate color for shells under Windows such as
# a DOS window and bash under cygwin.  If you're on a different
# platform (e.g., UNIX-like), you'll probably have to modify the
# functions accordingly to get things to work.  This shouldn't be too
# onerous with something like ncurses -- or just look at the output of
# e.g. GNU grep to capture the needed escape sequences for your
# terminal.
black    = color.black
blue     = color.blue
green    = color.green
cyan     = color.cyan
red      = color.red
magenta  = color.magenta
brown    = color.brown
white    = color.white
gray     = color.gray
lblue    = color.lblue
lgreen   = color.lgreen
lcyan    = color.lcyan
lred     = color.lred
lmagenta = color.lmagenta
yellow   = color.yellow
lwhite   = color.lwhite
fg = color.fg
normal = color.normal

# WordNet uses letters to identify the types of words; we'll use more
# conventional abbreviations.  This also allows us to set the color
# for these types of words.
abbr = {
    "a" : ("adj.", yellow),
    "s" : ("adj.", yellow),
    "n" : ("n.",   lwhite),
    "v" : ("v.",   lgreen),
    "r" : ("adv.", lmagenta),
}

def out(*v, **kw):
    sep = kw.setdefault("sep", " ")
    nl  = kw.setdefault("nl", True)
    stream = kw.setdefault("stream", sys.stdout)
    if v:
        stream.write(sep.join([str(i) for i in v]))
    if nl:
        stream.write("\n")

def err(s, **kw):
    kw["stream"] = sys.stderr
    out(s, **kw)

def Error(msg, status=1):
    out(msg, stream=sys.stderr)
    exit(status)

def Usage(d, status=1):
    name = sys.argv[0]
    s = '''
Usage:  {name} [options] regexp
  Look up a regular expression in a dictionary of words.  The search
  tool is grep, so you should use grep's regular expressions.  You'll
  have to make sure the grep variable in the program points to a
  suitable grep program.  If you search the WordNet dictionary, use an
  underscore for the space character.

  The WordNet options provide the ability to search the list of words
  from WordNet and see synonyms and definitions.  Note that the
  WordNet dictionary also includes combinations of words connected by
  hyphens and space (underscore) characters (use -c to exclude them).

Options:
    -0      Use a simple English dictionary (850 words)
    -1      Use the default dictionary      (42 kwords)
    -2      Use a larger ubuntu dictionary  (98 kwords)
    -3      Use a large dictionary         (274 kwords)
    -C n    Set the number of columns in output to n
    -i      Make search case-sensitive
    -w      Use a dictionary from WordNet  (155 kwords)

WordNet search options (causes -w option to be set):
    -a      Limit to adjectives
    -c      Do not show compound or hyphenated words
    -d      Show definitions/synonyms for all words that match
    -n      Limit to nouns
    -r      Limit to adverbs
    -v      Limit to verbs

Acknowledgements:
  1.  Thanks to Alan Beale for his 12dicts (I use his 2of12.txt
      file for my default dictionary):
      http://wordlist.sourceforge.net/12dicts-readme.html.
  2.  Thanks to the folks at Princeton who provide WordNet:
      http://wordnet.princeton.edu/.
'''[1:-1]
    out(s.format(**locals()))
    sys.exit(status)

def ParseCommandLine(d):
    # Define the dictionaries we'll use.  1 is the default.
    d["dict"] = dictionary_files;
    d["-a"] = False
    d["-C"] = None
    d["-c"] = False
    d["-d"] = False
    d["-i"] = "-i"
    d["-n"] = False
    d["-r"] = False
    d["-s"] = False     # Used for satellite adjectives
    d["-v"] = False
    d["-w"] = False
    d["which_dict"] = 1
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "0123aC:cdinrvw")
    except getopt.GetoptError as str:
        msg, option = str
        out(msg)
        sys.exit(1)
    for opt in optlist:
        if opt[0] == "-0": 
            d["which_dict"] = 0
        if opt[0] == "-1": 
            d["which_dict"] = 1
        if opt[0] == "-2": 
            d["which_dict"] = 2
        if opt[0] == "-3": 
            d["which_dict"] = 3
        if opt[0] == "-a": 
            d["-a"] = not d["-a"]
            d["-w"] = True
            # We also set -s to True because of the special case of
            # satellite adjectives.
            d["-s"] = True
        if opt[0] == "-C": 
            d["-C"] = abs(int(opt[1]))
            global columns
            columns = d["-C"]
        if opt[0] == "-c": 
            d["-c"] = not d["-c"]
            d["-w"] = True
        if opt[0] == "-d": 
            d["-d"] = not d["-d"]
            d["-w"] = True
        if opt[0] == "-i": 
            d["-i"] = ""
        if opt[0] == "-n": 
            d["-n"] = not d["-n"]
            d["-w"] = True
        if opt[0] == "-r": 
            d["-r"] = not d["-r"]
            d["-w"] = True
        if opt[0] == "-v": 
            d["-v"] = not d["-v"]
            d["-w"] = True
        if opt[0] == "-w": 
            d["-w"] = True
            d["which_dict"] = 4
    if not args:
        Usage(d)
    return args[0]

def ParseIndexLine(line):
    '''A typical index line is:
        airheaded%5:00:00:frivolous:00 02120828 1 0
    '''
    f = line.split()
    key, offset = f[0], int(f[1])
    f = key.split(":")
    p = f[0].split("%")
    head_word = f[3]
    word, sense = p[0], int(p[1])
    # Translate sense number to a letter
    letter = " nvars"[sense]
    # Note that head_word is only non-empty if letter is "s"
    return word, letter, head_word, offset

def ParseDataLine(line):
    '''The five typical lines' contents (shown wrapped):
 
    adjective:
 
        00001740 00 a 01 able 0 005 = 05200169 n 0000 = 05616246 n
        0000 + 05616246 n 0101 + 05200169 n 0101 ! 00002098 a 0101 |
        (usually followed by `to') having the necessary means or skill
        or know-how or authority to do something; "able to swim"; "she
        was able to program her computer"; "we were at last able to
        buy a car"; "able to get a grant for the project"  
 
    adjective satellite:
 
        02120828 00 s 08 airheaded 0 dizzy 0 empty-headed 0
        featherbrained 0 giddy 0 light-headed 0 lightheaded 0 silly 0
        004 & 02120458 a 0000 + 04648440 n 0802 + 04894444 n 0701 +
        04648440 n 0501 | lacking seriousness; given to frivolity; "a
        dizzy blonde"; "light-headed teenagers"; "silly giggles"  
 
    adverb:
 
        00002436 02 r 03 horseback 0 ahorse 0 ahorseback 0 000 | on
        the back of a horse; "he rode horseback to town"; "managed to
        escape ahorse"; "policeman patrolled the streets ahorseback"  
 
    noun:
 
        00001740 03 n 01 entity 0 003 ~ 00001930 n 0000 ~ 00002137 n
        0000 ~ 04424418 n 0000 | that which is perceived or known or
        inferred to have its own distinct existence (living or
        nonliving)  
 
    verb:
 
        00001740 29 v 04 breathe 0 take_a_breath 0 respire 0 suspire 3
        021 * 00005041 v 0000 * 00004227 v 0000 + 03110322 a 0301 +
        00831191 n 0303 + 04080833 n 0301 + 04250850 n 0105 + 00831191
        n 0101 ^ 00004227 v 0103 ^ 00005041 v 0103 $ 00002325 v 0000 $
        00002573 v 0000 ~ 00002573 v 0000 ~ 00002724 v 0000 ~ 00002942
        v 0000 ~ 00003826 v 0000 ~ 00004032 v 0000 ~ 00004227 v 0000 ~
        00005041 v 0000 ~ 00006697 v 0000 ~ 00007328 v 0000 ~ 00017031
        v 0000 02 + 02 00 + 08 00 | draw air into, and expel out of,
        the lungs; "I can breathe better when the air is clean"; "The
        patient is respiring"  
  
    Note the definition ("gloss") is after the vertical bar, so that's
    parsed out first.  Then the remainder is parsed; the description
    is in the wndb.5.pdf file.  Note we only keep the word type letter
    and the synonyms.
    '''
    head, definition = line.split("|")
    definition = definition.strip()
    if definition[0] in string.ascii_lowercase:
        definition = definition[0].upper() + definition[1:]
    f = head.split()
    letter, syn_cnt = f[2], int("0x" + f[3], 16)
    synonyms = f[4:4 + 2*syn_cnt:2]
    word = synonyms[0]
    synonyms = synonyms[1:] if len(synonyms) > 1 else []
    return word, letter, synonyms, definition

def PrintWord(word, letter, head_word, offset, d):
    '''word is the word as found in the index.sense file but
    displayable (the underscores are removed).  letter is one of
    "nvars".  head_word is not empty if letter is "s".  offset is an
    integer to read the relevant line from the stream after performing
    a seek to that offset.  
    '''
    stream = streams[letter]
    stream.seek(offset)
    line = stream.readline()
    main_word, letter, synonyms, definition = ParseDataLine(line)
    key = word + "%" + letter
    indent = " "*2
    if d["-d"] or d["-" + letter]:
        if d["-c"] and ("_" in word or "-" in word or " " in word):
            return
        fg(lred)
        out(word)
        normal()
        fg(abbr[letter][1])
        out(indent, abbr[letter][0], nl=False, sep="")
        if synonyms:
            D = {"-c" : columns - len(indent) - 6, "on": True}
            t = Wrap(', '.join(synonyms), D)
            for i, s in enumerate(t):
                out(indent*(3 if i else 0), s.strip().replace("_", " "))
        else:
            out()
        D = {"-c" : columns - len(indent) - 2, "on": True}
        t = Wrap(definition, D)
        for i in t:
            out(indent*2, i.strip())
        normal()

def PrintWordNet(word, d):
    '''word is a word in the WordNet index, so find its line(s) in the
    index.sense file.  Then dereference each synset reference and
    send the data to stdout.
    '''
    Word = word.strip().replace("_", " ")
    # Note:  it's important to use double quotes around the regexp;
    # otherwise the command will hang when word contains an
    # apostrophe.
    cmd = (grep + ' "^' + word.strip() + '%" ' +
           wordnet_files["index"].replace("\\", "/"))
    p = subprocess.PIPE
    s = subprocess.Popen(cmd, bufsize=0, stdout=p, stderr=p,
        universal_newlines=True)
    # Get results of grep
    lines = s.stdout.readlines()
    if dbg:
        print "xx2 cmd =", cmd
        print "xx3 lines =", lines
    error   = s.stderr.readlines()
    if error:
        err("PrintWordNet() grep error:")
        for e in error:
            err(e)
        exit(1)
    # lines now contains those words in the WordNet index.sense file
    # that matched the word passed in.
    for line in lines:
        found_word, letter, head_word, offset = ParseIndexLine(line)
        if dbg:
            print "xx4 word from index line =", found_word, letter
        if d["-d"] or d["-" + letter]:
            # Note we use Word instead of word or found_word!
            PrintWord(Word, letter, head_word, offset, d)

def WordNet(regexp, d):
    '''Given the regexp 
    '''
    # If none of the WordNet-related options are True, just do a
    # regular lookup.
    no_wn = (
        not d["-a"] and 
        not d["-d"] and 
        not d["-n"] and 
        not d["-r"] and 
        not d["-s"] and 
        not d["-v"]
    )
    if no_wn:
        LookUp(regexp, d)
    # Get the word matches from the dictionary file
    cmd = grep + " " + d["-i"] + " --color=auto " 
    cmd += "'" + regexp + "' "
    wd = wordnet_files["dict"].replace("\\", "/")
    cmd += wd
    p = subprocess.PIPE
    s = subprocess.Popen(cmd, bufsize=0, stdout=p, stderr=p)
    # Get results of grep
    results = [i.strip() for i in s.stdout.readlines()]
    error   = [i.strip() for i in s.stderr.readlines()]
    if error:
        err("WordNet() grep error:")
        for e in error:
            err(e)
        exit(1)
    # We have the full words that matched in results, so print out
    # what the user has requested.
    results.sort()
    if dbg:
        print "xx1 results =", results
    for word in results:
        PrintWordNet(word, d)
    exit(0)

def LookUp(regexp, d):
    cmd = grep + " " + d["-i"] + " --color=auto " 
    cmd += "'" + regexp + "' "
    wd = d["dict"][d["which_dict"]].replace("\\", "/")
    cmd += wd
    rc = subprocess.call(cmd, bufsize=0)
    exit(rc)

def main():
    d = {} # Options dictionary
    regexp = ParseCommandLine(d)
    if d["-w"]:
        WordNet(regexp, d)
    else:
        LookUp(regexp, d)

main()
