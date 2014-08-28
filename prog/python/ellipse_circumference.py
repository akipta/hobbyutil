'''
Plot how well Ramanujan's approximate formula predicts the circumference of
an ellipse.

See
http://mathforum.org/dr/math/faq/formulas/faq.ellipse.circumference.html
'''

from __future__ import division
from pylab import *
from scipy.special import ellipe  # Complete elliptical integral of 2nd kind

def eccentricity(a, b): 
    return sqrt((a**2 - b**2)/a)

def Ramanujan(a, b):
    x = (a-b)/(a+b)
    return pi*(a+b)*(1 + 3*x**2/(10 + sqrt(4 - 3*x**2)))

a, n, b_max = 1, 1000, 0.2
a, n, b_max = 1, 1000, 1
delta = b_max/n
b = arange(0, b_max + delta, delta)
e = eccentricity(a, b)
exact = 4*a*ellipe(e**2)
if 1:
    semilogy(b, 1 - Ramanujan(a, b)/exact)
    ylabel(r"$1 - \frac{formula}{exact}$")
else:
    m = 1e4
    plot(b, m*(1 - Ramanujan(a, b)/exact))
    ylabel(r"$10^4 (1 - \frac{formula}{exact})$")
xlim(0, b_max)
xlabel("b")
title("Ramanujan's approximation\na = 1")
grid(True)

if 0:
    show()
else:
    savefig("ellipse_circumference.png", dpi=100)
