'''
Generate a Postscript plot of the trig relations.  If you wish to run
this script, you'll need to get a copy of the pygraphicsps library at
http://code.google.com/p/pygraphicsps/.  Put the three main python
files g.py, go.py, and gco.py into your pythonpath somewhere.

This script uses the pygraphicsps calls to create a near-copy of the
graph at http://en.wikipedia.org/wiki/File:Circle-trig6.svg.  
As that file was released under the GFDL, this script is released
under the GPL.

---------------------------------------------------------------------------
Copyright (C) 2012 Don Peterson
Contact:  gmail.com@someonesdad1
 
This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your option)
any later version.
 
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.
 
You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc., 59
Temple Place, Suite 330, Boston, MA 02111-1307  USA
'''

from time import strftime
from g import *
from math import sin, cos, tan, pi, sqrt

in2mm = 25.4
d2r = pi/180

# We'll use letter-size paper and us mm for units
W, H = 11*in2mm, 8.5*in2mm

# Text size in mm
t = 0.1
dx = t/2    # For positioning text near a point
dy = t/3    # Correction to center text vertically at a point

# To turn hex integers to color tuple
h2c = lambda r, g, b: (r/255, g/255, b/255)

# Colors taken from original via PSP8
if 0:
    c_sin    = h2c(0xdc, 0x2e, 0x2f)
    c_cos    = h2c(0x27, 0x1b, 0x6f)
    c_tan    = h2c(0xba, 0x86, 0x4d)
    c_csc    = h2c(0xee, 0xa0, 0xd2)
    c_sec    = h2c(0x01, 0xa0, 0xca)
    c_cot    = h2c(0xe2, 0x9d, 0x42)
    c_exsec  = h2c(0xd3, 0x1f, 0x82)
    c_versin = h2c(0x31, 0x8b, 0x45)
else:
    # More basic colors
    c_sin    = red
    c_cos    = blue
    c_tan    = chocolate3
    c_csc    = purple
    c_sec    = aquamarine
    c_cot    = magenta
    c_exsec  = maroon3
    c_versin = limegreen

# Angle that is displayed.  Note it's in degrees.
theta = 55

# Point locations
Ox, Oy = 0, 0
Ax, Ay = cos(theta*d2r), sin(theta*d2r)
A1x, A1y = Ax + 2*t, Ay + 2*t
Bx, By = Ax, -Ay
Cx, Cy = Ax, 0
Dx, Dy = 1, 0
Ex, Ey = 1/cos(theta*d2r), 0
Fx, Fy = 0, 1/sin(theta*d2r)
Gx, Gy = 1, tan(theta*d2r)
One_x, One_y = Ax/2, Ay/2

def SetUp(file, orientation=landscape, units=mm):
    '''Convenience function to set up the drawing environment and return a
    file object to the output stream.
    '''
    ofp = open(file, "w")
    ginitialize(ofp, wrap_in_PJL=0)
    setOrientation(orientation, units)
    return ofp

def Circle():
    push()
    move(0, 0)
    circle(2) # Unit circle
    move(0, 0)
    pop()

def Points():
    push()
    # A
    move(Ax + 2*dx, Ay)
    text("A")
    # B
    move(Bx + dx, By - 2*dx)
    text("B")
    # C
    move(Cx + dx, Cy + dx)
    text("C")
    # D
    move(Dx + dx, Dy - 2*dx)
    text("D")
    # E
    move(Ex + dx, Ey - dy)
    text("E")
    # F
    move(Fx, Fy + dx)
    text("F")
    # G
    move(Gx, Gy + dx)
    text("G")
    # 1
    move(One_x - 2*dx, One_y)
    text("1")
    # O
    move(Ox - 2*dx, Oy - 3*dy)
    text("O")
    pop()

def Cot():
    push()
    SetColor(c_cot)
    line(Ax, Ay, Fx, Fy)
    # Now, draw a line from the top edge of the circle horizontally to
    # the intersection with the angle extension OG.
    line(0, 1, 1/tan(theta*d2r), 1)
    # Label
    x, y = Fx + (Ax - Fx)/2 - dx, Fy - (Fy - Ay)/2 + dx
    translate(x, y)
    rotate(theta - 90)
    move(0, dy)
    ctext("cot")
    pop()

def Tan():
    push()
    SetColor(c_tan)
    line(Ex, Ey, Ax, Ay)
    x, y = Cx + (Ex - Cx)/2, Ay/2
    push()
    translate(x, y)
    rotate(theta - 90)
    move(0, dy)
    ctext("tan")
    pop()
    # Now the vertical tangent
    line(Dx, Dy, Gx, Gy)
    move(Gx + 2*dx, Gy/2)
    ctext("tan")
    pop()

def Csc():
    push()
    SetColor(c_csc)
    line(Ox, Oy, Fx, Fy)
    move(-dx/2, Fy/2 - dy)
    rtext("csc")
    pop()

def Sin():
    push()
    SetColor(c_sin)
    line(Cx, Cy, Ax, Ay)
    move(Cx + 2*dx, Ay/2 - dy)
    ctext("sin")
    pop()

def Cos():
    push()
    SetColor(c_cos)
    line(Ox, Oy, Cx, Cy)
    move(Ox + Cx/2, Oy - t)
    ctext("cos")
    pop()

def Versin():
    push()
    SetColor(c_versin)
    line(Cx, Cy, Dx, Dy)
    move(Cx + (Dx - Cx)/2, Oy - t)
    ctext("versin")
    pop()

def Exsec():
    push()
    SetColor(c_exsec)
    line(Dx, Dy, Ex, Ey)
    move(Dx + (Ex - Dx)/2, Oy - t)
    ctext("exsec")
    pop()

def Sec():
    push()
    dsec = 0.3
    SetColor(c_sec)
    line(Ox, Oy - dsec, Ex, Ey - dsec)
    x = Ex/2 + 2*t
    move(Ox + x, Oy - dsec - t)
    text("sec")
    move(Ox + x, Oy - dsec - 2*t)
    text("OG is also sec")
    # Left arrowhead
    push()
    translate(Ox, -dsec)
    dx, dy = t, t/4
    NewPath()
    PathAdd((0, 0))
    PathAdd((dx, -dy))
    PathAdd((dx, dy))
    PathClose()
    p = GetPath()
    FillOn()
    FillPath()
    line(0, -2*dy, 0, 2*dy)
    pop()
    # Right arrowhead
    push()
    translate(Ex, -dsec)
    dx, dy = t, t/4
    NewPath()
    PathAdd((0, 0))
    PathAdd((-dx, -dy))
    PathAdd((-dx, dy))
    PathClose()
    p = GetPath()
    FillOn()
    FillPath()
    line(0, -2*dy, 0, 2*dy)
    pop()
    pop()

def Lines():
    push()
    line(0, 0, Ax, Ay)      # O to A
    line(0, 0, Bx, By)      # O to B
    line(Bx, By, Cx, 0)     # B to C
    # Right angle marks
    if 1:
        # Origin
        ra = 1.5*dx
        line(-ra, 0, -ra, ra)
        line(-ra, ra, 0, ra)
        # Point A
        push()
        translate(Ax, Ay)
        rotate(theta)
        line(ra, 0, ra, ra)
        line(ra, ra, 0, ra)
        pop()
    # Dashed lines
    dl = 0.25
    if 0:
        push()
        LineType(little_dash)
        line(-dl, 0, 0, 0)
        translate(Ax, Ay)
        rotate(theta)
        line(0, 0, dl, 0)
        pop()
    else:
        push()
        # Line for the secant, but we'll color it as the exsecant
        push()
        SetColor(c_exsec)
        line(Ax, Ay, Gx, Gy) 
        translate(Ax, Ay)
        rotate(theta)
        d = sqrt((Ax - Gx)**2 + (Ay - Gy)**2)
        move(d/2, t/2)
        ctext("exsec")
        pop()
        LineType(little_dash)
        line(-dl, 0, 0, 0)
        pop()
    Cot()
    Tan()
    Csc()
    Sin()
    Cos()
    Versin()
    Exsec()
    Sec()
    pop()

def Theta():
    push()
    move(0, 0)
    arc(0.25, 0, theta)
    move(0.3*Cx, 1.5*dy)
    TextName(Symbol)
    TextSize(1.3*t)
    text("\x71")
    pop()

def Title():
    push()
    move(170, 30)
    TextSize(4)
    day = strftime("%d")
    if day[0] == "0":
        day = day[1]
    date = strftime("%s %%b %%Y" % day)
    TextLines((
        "Trigonometric functions relative to the unit circle",
        "someonesdad1@gmail.com  %s" % date,
        "See http://code.google.com/p/hobbyutil/ and",
        "http://code.google.com/p/pygraphicsps/.",
    ))
    pop()

def main():
    SetUp("images/trig_functions.ps")
    Title()
    translate(W/3, H/2.4)
    move(0, 0)
    # Scale to allow us to use unit dimensions 
    a = 60
    scale(a, a)
    TextSize(t)
    TextName(SansBold)
    LineWidth(0.012)
    Points()
    Lines()
    Circle()
    Theta()
    Title()

main()
