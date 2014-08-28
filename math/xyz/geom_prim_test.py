from __future__ import print_function, division
import sys
from geom_prim import *
from lwtest import run, assert_equal, assert_raises
from pdb import set_trace as xx

py3 = True if sys.version_info[0] == 3 else False

# The following is a "random" matrix that I made up; it has no
# other significance.
rm = [  1,    -7,      3,   17, 
      -47.5,   0.002,  1,   -1, 
       -0.2, -10,     -3.3,  4, 
        1,     0.1,   -0.2,  0.3]
identity = [1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1]
# Make sure we test with Ctm angle measurements in radians
Ctm._angle = 1
Ctm._angle_name = "rad"

# Tolerance for floating point stuff
eps = 1e-15

def test_Ctm():
    # We'll test some of the basic capabilities of Ctm.  We can't
    # test the transformations, as that would use one of the methods
    # which is abstract; they'll be tested in e.g. the tests of the
    # Point object.
    # 
    # Things to test:
    #     - CTM is identity matrix at instantiation
    #     - Rnd()
    #     - Can get and set CTM
    #     - CTM inverse (note it's in separate test)
    #     - reset() sets CTM to identity matrix
    # Verify identity matrices at instantiation
    c = Ctm()
    got = c.GetCTM()
    assert_equal(got, identity[:])
    got = c.GetICTM()
    assert_equal(got, identity[:])
    # Check Rnd
    Ctm.eps = 0.01
    got = c.Rnd(-0.00999)
    expected = 0
    assert_equal(got, expected)
    # Check ability to set CTM
    expected = rm[:]
    c.SetCTM(expected[:])
    got = c.GetCTM()
    assert_equal(got, expected)
    # If reset() is not used here, later tests will fail
    c.reset()
    assert_equal(c.GetCTM(), identity[:])
def test_MatrixInverse():
    # This test uses numpy's matrix inversion as a standard.
    if not have_numpy:
        out("Warning:  Ctm matrix inverse not tested (need numpy)")
        return
    def MakeMatrix(lst):
        A = np.array(lst)
        A.shape = (4, 4)
        return np.matrix(A)
    c, p = Ctm(), Point(0, 0, 0)
    c.SetCTM(rm[:])
    P, n = MakeMatrix(c.GetCTM())*MakeMatrix(c.GetICTM()), 4
    # P should be the identity matrix
    for i in range(n):
        for j in range(n):
            if i == j:
                assert_equal(p.Rnd(P[i, j] - 1), 0)
            else:
                assert_equal(p.Rnd(P[i, j]), 0)
    c.reset()
def test_Det():
    # Determinant.  Check Det4, as it depends on Det3 and Det2.
    # numpy provides the standard determinant.
    if have_numpy:
        A = np.array(rm)
        A.shape = (4, 4)
        A = np.matrix(A)
        p = Point(0, 0, 0)
        assert_equal(p.Rnd(Det4(rm) - npdet(A)), 0)
    else:
        out("Warning:  determinants not tested (need numpy)")
def test_Vector():
    Ctm._compass = False
    Ctm._neg = False
    Ctm._elev = False
    # Initialization
    if True:
        # Three numbers
        i = V(1, 0, 0)
        # A Point object
        j = V(Point(0, 1, 0))
        # A 3-tuple
        k = V((0, 0, 1))
        # A Line object
        v = V(Line(Point(0, 0, 0), Point(1, 1, 1)))
        # Another vector
        w = V(V(1, 2, 3))
    # copy
    a = v.copy
    assert_equal(v, a)
    assert(hash(v) != hash(a))
    # dist
    assert_equal(i.dist(j), sqrt(2))
    # Unary negate
    a = -i
    assert_equal(a._p, Point(-1, 0, 0))
    # Equality
    assert_equal(a == a, True)
    assert_equal(a != i, True)
    # Addition
    assert_equal(i + j + k, v)
    # Subtraction
    assert_equal(i - j, V(1, -1, 0))
    # Multiplication
    assert_equal(2*i, V(2, 0, 0))
    assert_equal(i*2, V(2, 0, 0))
    # Dot product
    assert_equal(i.dot(j), 0)
    assert_equal(i.dot(i), 1)
    assert_equal(v.dot(w), 6)
    # Cross product
    assert_equal(i.cross(j), k)
    assert_equal(j.cross(k), i)
    assert_equal(k.cross(i), j)
    # Magnitude
    assert_equal(v.mag, sqrt(3))
    # Normalize
    a = w.copy
    assert(a.mag != 1.0)
    a.normalize()
    assert_equal(a.Rnd(a.mag - 1), 0)
    # Scalar triple product
    assert_equal(i.STP(j, k), 1)
    # Vector triple product
    assert_equal(i.VTP(j, k), V(0, 0, 0))
    # rect property
    assert_equal(i.rect, (1, 0, 0))
    # dc property
    a = 1/sqrt(3)
    assert_equal(i.dc, (1, 0, 0))
    assert_equal(v.dc, (a, a, a), abstol=eps)
    # u property
    a = 1/sqrt(3)
    assert_equal(v.u, V(a, a, a))
    # cyl property
    assert_equal(v.cyl, (sqrt(2), pi/4, 1))
    rho, theta, z = v.cyl
    assert_equal(v.rho, rho)
    assert_equal(v.theta, theta)
    assert_equal(v.z, z)
    # sph property
    r = hypot(rho, v._p._r[2])
    x, y, z = v._p._r
    assert_equal(v.sph, (r, atan2(y, x), atan2(rho, z)))
    r, theta, phi = v.sph
    assert_equal(r, v.r)
    assert_equal(theta, v.theta)
    assert_equal(phi, v.phi)
def test_Point():
    Ctm._compass = False
    Ctm._neg = False
    Ctm._elev = False
    # Instantiation
    if 1:
        # 3 rectangular coordinates
        p = Point(1, 2, 3)
        assert_equal(p.rect, (1, 2, 3))
        # A 3-tuple
        p = Point((1, 2, 3))
        assert_equal(p.rect, (1, 2, 3))
        # Another point
        p1 = Point(p)
        assert_equal(p.rect, (1, 2, 3))
        assert(hash(p1) != hash(p))
        # A vector V object
        p1 = Point(V(1, 2, 3))
        assert_equal(p1, p)
        assert(hash(p1) != hash(p))
    # Copy
    p1 = p.copy
    assert_equal(p, p1)
    assert(hash(p1) != hash(p))
    # String representations
    i = Point(0, 0, 0)
    assert_equal(str(i), "Origin")
    i = Point(1, 0, 0)
    Ctm._suppress_z = False
    assert_equal(str(i), "Pt(1, 0, 0)")
    Ctm._suppress_z = True
    assert_equal(str(i), "Pt(1, 0)")
    assert_equal(i.__str__(no2d=True), "Pt(1, 0, 0)")
    Ctm._suppress_z = False
    Ctm._coord_sys = "cyl"
    assert_equal(str(i), "Pt<1, 0, 0>")
    Ctm._coord_sys = "sph"
    assert_equal(str(i), "Pt<<1, 0, 1.571>>")
    Ctm._elev = True
    assert_equal(str(i), "Pt<<1, 0, 0 E>>")
    Ctm._angle = 180/pi
    Ctm._angle_name = "deg"
    assert_equal(str(i), "Pt<<1, 0, 0 oE>>")
    # Conversions to cylindrical and spherical coordinates
    Ctm._coord_sys = "rect"
    Ctm._elev = False
    Ctm._suppress_z = False
    Ctm._angle = 1
    Ctm._angle_name = "rad"
    if 1:
        def TestConversions(deg=False):
            '''This will test in radians unless deg is True, in
            which case the angles will be converted to radians.
            '''
            Ctm._compass = False
            Ctm._neg = False
            Ctm._elev = False
            d2r = pi/180 if deg else 1
            # Basics
            p = Point(1, 2, 3)
            assert_equal(p.rect, (1, 2, 3))
            rho, theta, z = p.cyl
            assert_equal(p.Rnd(rho - sqrt(5)), 0)
            assert_equal(p.Rnd(d2r*theta - atan(2)), 0)
            assert_equal(p.Rnd(z - 3), 0)
            r, theta, phi = p.sph
            assert_equal(p.Rnd(r - sqrt(14)), 0)
            assert_equal(p.Rnd(d2r*theta - atan(2)), 0)
            assert_equal(p.Rnd(d2r*phi - atan(sqrt(5)/3)), 0)
            # Compass mode 
            o = Point(0, 0, 0)
            i, j = Line(o, Point(1, 0, 0)), Line(o, Point(0, 1, 0))
            k = Line(o, Point(0, 0, 1))
            Ctm._compass = True
            rho, theta, z = i.q.cyl
            assert_equal(i.Rnd(d2r*theta), pi/2)
            rho, theta, z = j.q.cyl
            assert_equal(i.Rnd(d2r*theta), 0)
            ij = i + j
            rho, theta, z = ij.q.cyl
            assert_equal(i.Rnd(d2r*theta - pi/4), 0)
            # Negative mode
            Ctm._compass = False
            Ctm._neg = True
            rho, theta, z = j.q.cyl
            assert_equal(i.Rnd(d2r*theta - 3*pi/2), 0)
            rho, theta, z = ij.q.cyl
            assert_equal(i.Rnd(d2r*theta - 7*pi/4), 0)
            Ctm._compass = True
            rho, theta, z = ij.q.cyl
            assert_equal(i.Rnd(d2r*theta - 7*pi/4), 0)
            # Elevation mode
            Ctm._compass = False
            Ctm._neg = False
            Ctm._elev = True
            r, theta, phi = ij.q.sph
            assert_equal(i.Rnd(d2r*phi), 0)
            ijk = i + j + k
            r, theta, phi = ijk.q.sph
            assert_equal(i.Rnd(r), sqrt(3), abstol=eps)
            assert_equal(i.Rnd(d2r*theta - pi/4), 0)
            assert_equal(i.Rnd(d2r*phi - atan(1/sqrt(2))), 0)
            ijmk = i + j - k
            r, theta, phi = ijmk.q.sph
            assert_equal(i.Rnd(d2r*phi + atan(1/sqrt(2))), 0)
        Ctm._angle = 1
        TestConversions(deg=False)
        # Check that things work in degrees too
        Ctm._angle = 180/pi
        TestConversions(deg=True)
    # Restore default state
    Ctm._angle = 1
    Ctm._compass = False
    Ctm._neg = False
    Ctm._elev = False
    # Rotate point on x axis about the z axis by 90 deg
    p = Point(1, 0, 0)
    p.rotate(pi/2, (0, 0, 1))
    x, y, z = p.ToCCS()
    assert_equal(p.Rnd(x), 0)
    assert_equal(p.Rnd(y + 1), 0)
    assert_equal(p.Rnd(z), 0)
    # Verify coordinates in default system unchanged
    x, y, z = p.ToDCS()
    assert_equal(p.Rnd(x - 1), 0)
    assert_equal(p.Rnd(y), 0)
    assert_equal(p.Rnd(z), 0)
    # Verify rotation axis and angle as expected
    theta, axis = p.GetRotationAxis()
    assert_equal(p.Rnd(theta - pi/2), 0)
    x, y, z = axis
    assert_equal(p.Rnd(x), 0)
    assert_equal(p.Rnd(y), 0)
    assert_equal(p.Rnd(z - 1), 0)
    # Check dist works
    p1, p2 = Point(0, 0, 0), Point(1, 1, 1)
    assert_equal(p.Rnd(p1.dist(p2) - sqrt(3)), 0)
    # Check equality 
    p1, p2 = Point(0, 0, 0), Point(0, 0, 0)
    assert_equal(p1 == p2, True)
    assert(hash(p1) != hash(p))
    p1, p2 = Point(0, 0, 0), Point((0, 0, 1))
    assert_equal(p1 == p2, False)
    # Point.m can be set to an object (we'll use a function object
    # for this test)
    p = Point(1, 2, 3, Det4)
    assert_equal(p.m, Det4)
    # Collinearity
    p1, p2, p3 = Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0)
    assert_equal(p1.AreCollinear(p2, p3), True)
    # Negation
    p1, p2, p3 = Point(0, 0, 0), Point(1, 1, 1), Point(-1, -1, -1)
    assert_equal(-p1, p1)
    assert_equal(-p2, p3)
    # Intersection
    assert_equal(p1.intersect(p1), p1)
    assert_equal(p1.intersect(p2), None)
    # Attributes
    if 1:
        # Rectangular
        p, a, b, c = Point(1, 0, 0), 2, 3, 4
        p.x = a
        assert_equal(p.x, a)
        assert_equal(p, Point(a, 0, 0))
        p.y = b
        assert_equal(p.y, b)
        assert_equal(p, Point(a, b, 0))
        p.z = c
        assert_equal(p.z, c)
        assert_equal(p, Point(a, b, c))
        # Cylindrical
        a, b, c = 1, 2, 3
        p = Point(a, b, c)
        assert_equal(p.rho, hypot(a, b))
        theta = p.theta
        r = 10
        p.rho = r
        x, y, z = p.rect
        assert_equal(x, r*cos(theta))
        assert_equal(y, r*sin(theta))
        p = Point(a, b, c)
        p.theta = pi/2
        x, y, z = p.rect
        assert_equal(x, 0)
        assert_equal(y, sqrt(5))
        # Spherical
        a, b, c = 1, 2, 3
        p = Point(a, b, c)
        assert_equal(p.Rnd(p.r - hypot(a, hypot(b, c))), 0)
        r, theta, phi = p.sph
        d = 1
        p.r = d
        r, theta, phi = p.sph
        assert_equal(p.Rnd(r - d), 0)
        p.theta = d
        r, theta, phi = p.sph
        assert_equal(p.Rnd(theta - d), 0)
        p.phi = d
        r, theta, phi = p.sph
        assert_equal(p.Rnd(phi - d), 0)
        # Direction cosines
        p = Point(1, 1, 1)
        dc, a = p.dc, 1/sqrt(3)
        assert_equal(dc, (a, a, a), abstol=eps)
        # proj_ang
        pa = p.proj_ang
        a = pi/4
        assert_equal(pa, (a, a))
def test_Line():
    Ctm._compass = False
    Ctm._neg = False
    Ctm._elev = False
    # Get and set attributes
    p0 = Point(0, 0, 0)
    px = Point(1, 0, 0)
    py = Point(0, 1, 0)
    pz = Point(0, 0, 1)
    p  = Point(1, 1, 1)
    # Initialization 
    if True:
        # Use 2 points
        L = Line(px, py)
        assert_equal(L.L, sqrt(2))
        assert_equal(L.p, px)
        assert_equal(L.q, py)
        L.p = p0   # Set attribute
        assert_equal(L.p, p0)
        L.q = px   # Set attribute
        assert_equal(L.L, 1)
        # Use 1 point and direction numbers
        npy = (0, -1, 0)
        L = Line(px, npy)  # Line goes in -y direction
        assert_equal(L.p, px)
        assert_equal(L.dc, (0, -1, 0))
        # Use 1 point and a line
        L = Line(px, Line(p0, Point(*npy)))
        assert_equal(L.p, px)
        assert_equal(L.dc, (0, -1, 0))
    # Check equality
    assert_equal(Line(p0, px), Line(p0, px))
    # Check direction cosines
    assert_equal(Line(p0, px).dc, (1, 0, 0))
    assert_equal(Line(p0, py).dc, (0, 1, 0))
    assert_equal(Line(p0, pz).dc, (0, 0, 1))
    # Check dist
    if True:
        # Line and point
        L = Line(p0, px)
        assert_equal(L.dist(py), 1)
        L = Line(p0, py)
        assert_equal(L.dist(pz), 1)
        L = Line(p0, pz)
        assert_equal(L.dist(px), 1)
        L = Line(px, p0)
        assert_equal(L.dist(p), sqrt(2))
        # Line and line
        L1 = Line(px, p0)   # Line along x axis
        a = sqrt(5)
        L2 = Line(Point(0, 0, a), Point(0, 1, a)) # Along y at z = a
        assert_equal(L1.dist(L2), a)
    # Negation
    L = Line(Point(0, 0, 0), Point(1, 1, 1))
    M = -L
    assert_equal(M.p, L.q)
    assert_equal(M.q, L.p)
    # Copy
    L = Line(Point(0, 0, 0), Point(1, 1, 1))
    M = L.copy
    assert_equal(L, M)
    assert(hash(L) != hash(M))
    assert(hash(L.p) != hash(M.p))
    assert(hash(L.q) != hash(M.q))
    # Intersections
    O, i, j = Point(0, 0, 0), Point(1, 0, 0), Point(0, 1, 0)
    if True:
        # Line and point
        L = Line(O, i)
        assert_equal(L.intersect(O), O)
        assert_equal(L.intersect(j), None)
        L, p = Line(i, j), Point(1/2, 1/2, 0)
        assert_equal(L.intersect(O), None)
        assert_equal(L.intersect(p), p)
        # Line and line
        if True:
            # Coincident parallel lines
            L = Line(O, i)
            assert_equal(L.intersect(L), L)
            # Two intersecting lines in the xy plane
            L1 = Line(i, j)
            L2 = Line(O, Point(1, 1, 0))
            assert_equal(L1.intersect(L2), Point(1/2, 1/2, 0))
    # Check dot product
    Li, Lj, Lk, a = Line(O, i), Line(O, j), Line(O, Point(0, 0, 1)), 3
    L1, L2 = Line(O, Point(a, a, a)), Line(O, Point(-a, -a, -a))
    if True:
        # Simple orthogonal checks
        assert_equal(Li.dot(Lj), 0)
        assert_equal(Li.dot(Li), 1)
        assert_equal(Li.dot(L1), a)
        assert_equal(Lj.dot(L1), a)
        assert_equal(Lk.dot(L1), a)
        assert_equal(Li.dot(L2), -a)
        assert_equal(Lj.dot(L2), -a)
        assert_equal(Lk.dot(L2), -a)
        # Non-orthogonal check
        a, b = Point(1, 2, 3), Point(-4, -5, -6)
        c, d = Point(-7, -8, 9), Point(10, -11, 12)
        L1, L2 = Line(a, b), Line(c, d)
        assert_equal(L1.dot(L2), -91)
    # Check cross product
    assert_equal(Li.cross(Lj), Lk)
    assert_equal(Lj.cross(Lk), Li)
    assert_equal(Lk.cross(Li), Lj)
    # Check locate
    o, i, p = Point(0, 0), Point(1, 0), Point(0, 1)
    ln = Line(o, i)
    ln.locate(p)
    assert_equal(ln, Line(Point(0, 1), Point(1, 1)))
    o.locate(p)
    assert_equal(o, p)
def test_Plane():
    Ctm._compass = False
    Ctm._neg = False
    Ctm._elev = False
    # Plane from 3 points
    O, i, j, k = (Point(0, 0, 0), 
                   Point(1, 0, 0), 
                   Point(0, 1, 0),
                   Point(0, 0, 1))
    xy = Plane(O, i, j)  # Go around polygon ccw
    assert_equal(xy.dc, (0, 0, 1))
    pl = Plane(O, j, i)  # Go around polygon cw
    assert_equal(pl.dc, (0, 0, -1))
    # Plane from point and two lines
    ln1, ln2 = Line(O, i), Line(O, j)
    pl = Plane(k, ln1, ln2)
    assert_equal(pl.dc, (0, 0, 1))
    assert_equal(pl.p, k)
    assert_equal(pl.q, Point(0, 0, 2))
    # Plane from point and plane
    xy = Plane(O, i, j)  # Is xy plane
    pt = Point(0, 0, 1)
    pl = Plane(pt, xy)
    assert_equal(pl.dc, (0, 0, 1))
    assert_equal(pl.dc, (0, 0, 1))
    # Plane from another plane
    pl1 = Plane(pl)
    assert(hash(pl) != hash(pl1))
    assert_equal(pl, pl1)
    # Plane from point and line
    pl = Plane(O, Line(O, k))
    assert_equal(pl.dc, (0, 0, 1))  # Is xy plane
    assert_equal(pl.p, O)
    assert_equal(pl.q, k)
    # Plane from two lines that intersect
    o, i, k = Point(0, 0, 0), Point(1, 0, 0), Point(0, 0, 1)
    pl = Plane(Line(o, k), Line(o, i))
    xz = Plane(o, k, i)
    assert_equal(pl, xz)
    # Plane from two lines that don't intersect.  Plane will
    # contain ln1 and will be parallel to ln2.  Since ln1 is the i
    # unit vector and ln2 runs parallel to j, the plane will
    # contain the x axis and have its normal parallel to k; thus,
    # it will be the xy plane.
    o = Point(0, 0, 0)
    xy = Plane(o, Line(o, Point(0, 0, 1)))
    ln1 = Line(o, Point(1, 0, 0))   # In i direction
    ln2 = Line(Point(0, 0, 1), Point(0, 1, 1)) # In j direction
    pl = Plane(ln1, ln2)
    assert_equal(pl, xy)
    # Copy
    pl = Plane(O, i, j)
    pl1 = pl.copy
    assert_equal(pl, pl1)
    assert(hash(pl) != hash(pl1))
    assert(hash(pl) != hash(pl1))
    # Properties
    if True:
        pl = Plane(O, i, j)
        # Direction cosines of unit normal
        assert_equal(pl.dc, (0, 0, 1))
        # Hessian normal form p value
        pl = Plane(O, i, j)
        assert_equal(pl.dnd, 0)
        pl = Plane(k, Point(1, 0, 1), Point(0, 1, 1))
        assert_equal(pl.dnd, 1)
    # Intersections
    if True:
        # Plane and point
        pl = Plane(O, i, j)
        assert_equal(pl.intersect(O), O)
        assert_equal(pl.intersect(k), None)
        # Plane and line
        if True:
            # No intersection
            p1 = Point(1, 0, 1)
            ln = Line(p1, k)
            assert_equal(pl.intersect(ln), None)
            # Intersects in a point
            ln = Line(O, Point(1, 0, 1))
            assert_equal(pl.intersect(ln), O)
            # Intersects in a line (the line is in the plane)
            ln = Line(i, O)
            assert_equal(pl.intersect(ln), ln)
        # Plane and plane
        if True:
            # xy plane and xz plane
            pl1, pl2 = Plane(O, i, j), Plane(O, i, Point(1, 0, 1))
            ln = Line(O, i)
            assert_equal(pl1.intersect(pl2), ln)
            # Vertical planes through origin at right angles
            pl1 = Plane(O, Point(1, -1, 0), Point(1, -1, 1))
            pl2 = Plane(O, Point(1, 1, 0), Point(1, 1, 1))
            ln = Line(O, k)
            assert_equal(pl1.intersect(pl2), ln)
            # Parallel planes, equal
            assert_equal(pl1.intersect(pl1), pl1)
            # Parallel planes, don't intersect
            pl1 = Plane(O, i, j) # xy plane
            pl2 = Plane(Point(0, 0, 1), Point(1, 0, 1), Point(0, 1, 1))
            assert_equal(pl1.intersect(pl2), None)
    # dist
    if True:
        # Point and plane
        assert_equal(xy.dist(k), 1)
        assert_equal(xy.dist(i), 0)
        # Line and plane
        ln = Line(i, j)
        assert_equal(xy.dist(ln), 0)
        ln = Line(Point(1, 0, 1), Point(0, 1, 1))
        assert_equal(xy.dist(ln), 1)
        # Two planes
        pl = Plane(Point(0, 0, 1), Point(1, 0, 1), Point(0, 1, 1))
        assert_equal(xy.dist(pl), 1)
        pl = Plane(O, i, j)
        assert_equal(xy.dist(pl), 0)

if __name__ == "__main__":
    run(globals())
