'''
Contains functions to set screen color for console applications.  

There are 16 colors given by names:  black, blue, green, cyan, red,
magenta, brown, white, gray, lblue, lgreen, lcyan, lred, lmagenta,
yellow, and lwhite.

The primary function is fg(), which can be used in the following ways
to set the foreground and background colors:

    fg(white)
        Sets the foreground color to white and leaves the background
        unchanged.
    fg(white, black)
        Sets the foreground color to white and the background to
        black.
    fg((white, black))
        Same as previous call.
    fg(color_byte)
        Sets the foreground and background colors by using the number
        color_byte.  The low nibble gives the foreground color and the
        high nibble gives the background color.  

The normal() function sets the foreground and background colors back
to their normal values.  Call with arguments the same as fg() to
define the normal foreground and background colors.

These functions should work on both Windows and an environment that
uses ANSI escape sequences (e.g., an xterm).  

The code for Windows console colors was taken from Andre Burgaud's work at
http://www.burgaud.com/bring-colors-to-the-windows-console-with-python/,
downloaded Wed 28 May 2014.

---------------------------------------------------------------------------
Some ANSI control codes for attributes that have an effect in xterms:
    Esc[0m  Attributes off
    Esc[1m  Bold
    Esc[3m  Italics
    Esc[4m  Underline
    Esc[5m  Blinking 
    Esc[7m  Reverse video 
'''

# Copyright (C) 2014 Don Peterson
# Contact:  gmail.com@someonesdad1

#
#

from __future__ import print_function
import sys
from collections import Iterable
from itertools import combinations, permutations

if sys.version_info[0] == 3:
    String = (str,)
    Int = (int,)
else:
    String = (str, unicode)
    Int = (int, long)

_win = True if sys.platform == "win32" else False
_ii = isinstance

if _win:
    from ctypes import windll

# Foreground colors; shift left by 4 bits to get background color.
(
    black,
    blue,
    green,
    cyan,
    red,
    magenta,
    brown,
    white,
    gray,
    lblue,
    lgreen,
    lcyan,
    lred,
    lmagenta,
    yellow,
    lwhite
) = range(16)

# Set the default_colors global variable to be the defaults for your system.
default_colors = (white, black)

# Dictionary to translate between color numbers/names and escape
# sequence.
_cfg = { 
    black    : "0;30",
    blue     : "0;34",
    green    : "0;32",
    cyan     : "0;36",
    red      : "0;31",
    magenta  : "0;35",
    brown    : "0;33",
    white    : "0;37",
    gray     : "1;30",
    lblue    : "1;34",
    lgreen   : "1;32",
    lcyan    : "1;36",
    lred     : "1;31",
    lmagenta : "1;35",
    yellow   : "1;33",
    lwhite   : "1;37",
}
_cbg = {
    black    : "40m",
    blue     : "44m",
    green    : "42m",
    cyan     : "46m",
    red      : "41m",
    magenta  : "45m",
    brown    : "43m",
    white    : "47m",
    gray     : "40m",
    lblue    : "44m",
    lgreen   : "42m",
    lcyan    : "46m",
    lred     : "41m",
    lmagenta : "45m",
    yellow   : "43m",
    lwhite   : "47m",
}

def _is_iterable(x):
    '''Return True if x is an iterable that isn't a string.
    '''
    return _ii(x, Iterable) and not _ii(x, String)

STD_OUTPUT_HANDLE = -11
_hstdout = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE) if _win else None

def DecodeColor(*c):
    '''Return a 1-byte integer that represents the foreground and
    background color.  c can be 
        * An integer
        * Two integers
        * A sequence of two integers
    '''
    if len(c) == 1:
        # It can either be a number or a tuple of two ingeters
        if _is_iterable(c[0]):
            if len(c[0]) != 2:
                raise ValueError("Must be a sequence of two integers")
            color = ((c[0][1] << 4) | c[0][0]) & 0xff
        else:
            if not _ii(c[0], Int):
                raise ValueError("Argument must be an integer")
            color = c[0] & 0xff
    elif len(c) == 2:
        color = ((c[1] << 4) | c[0]) & 0xff
    else:
        raise ValueError("Argument must be one or two integers")
    return color

def GetNibbles(c):
    assert 0 <= c < 256
    return (0x0f & c, (0xf0 & c) >> 4)

def normal(*p):
    '''If the argument is None, set the foreground and background
    colors to their default values.  Otherwise, use the argument to
    set the default colors.
    '''
    global default_colors
    if p:
        one_byte_color = DecodeColor(*p)
        default_colors = GetNibbles(one_byte_color)
    else:
        fg(default_colors)

def fg(*p, **kw):
    '''Set the color.  p can be an integer or a tuple of two
    integers.  If it is an integer that is greater than 15, then it
    also contains the background color encoded in the high nibble.
    fgcolor can be a sequence of two integers of length two also.

    Style can be:
        normal
        italic
        underline
        blink
        reverse
    '''
    style = kw.setdefault("style", "normal")
    one_byte_color = DecodeColor(*p)
    if _win:
      windll.kernel32.SetConsoleTextAttribute(_hstdout, one_byte_color)
    else:
        # Use ANSI escape sequences
        cfg, cbg = GetNibbles(one_byte_color)
        f, b = _cfg[cfg], _cbg[cbg]
        print("\x1b[%s;%s" % (f, b), end="")

def style(s="normal"):
    if _win:
        raise Exception("Not implemented")
    st = {
        "normal" : 0, "bold" : 1, "italic" : 3, "underline" : 4, 
        "blink" : 5, "reverse" : 7,
    }[s]
    print("\x1b[%sm" % st, end="")

if __name__ == "__main__":
    # Display a table of the color combinations. 
    names = {
        black    : "black",
        blue     : "blue",
        green    : "green",
        cyan     : "cyan",
        red      : "red",
        magenta  : "magenta",
        brown    : "brown",
        gray     : "gray",
        white    : "white",
        lblue    : "lblue",
        lgreen   : "lgreen",
        lcyan    : "lcyan",
        lred     : "lred",
        lmagenta : "lmagenta",
        yellow   : "yellow",
        lwhite   : "lwhite",
    }
    low = [black, blue, green, cyan, red, magenta, brown, white]
    high = [gray, lblue, lgreen, lcyan, lred, lmagenta, yellow, lwhite]
    # Print title
    fg(yellow)
    msg = ("%s Text Colors" % __file__).center(79)
    print(msg)
    back = "Background --> "
    msg = " black   blue    green   cyan    red    magenta  brown   white"
    fg(lcyan)
    print(back + msg)
    def Table(bgcolors):
        for fgcolor in low + high:
            normal()
            s = names[fgcolor] + " (" + str(fgcolor) + ")"
            print("%-15s" % s, end="")
            for bgcolor in bgcolors:
                fg(fgcolor, bgcolor)
                c = (0xf0 & (bgcolor << 4)) | (0x0f & fgcolor)
                print("wxyz %02x" % c, end="")
                normal()
                print(" ", end="")
            normal()
            print()
    Table(low)
    msg = " gray    lblue   lgreen  lcyan   lred  lmagenta yellow  lWhite"
    fg(lcyan)
    print("\n" + back + msg)
    Table(high)
    # Print in different styles
    print("Styles:  ", end="")
    for i in ("normal", "bold", "italic", "underline", "blink", "reverse"):
        fg(white)
        style(i)
        print(i, end="")
        style("normal")
        print(" ", end="")
    fg(white)
    style("normal")
    print()
