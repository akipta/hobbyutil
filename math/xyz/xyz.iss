# Is the ISS visible from San Francisco when it is over Salt Lake City?

# Define variables
r = 6378.14     # Radius of Earth in km
alt = 415       # Altitude in km of ISS above mean sea level

# Define the north pole point as a check at the end to see that the
# coordinates in SF's topocentric coordinates make sense.
. 0, 0, r, np
sph
! out("North pole at start:")
indent 2
print np

# Latitude and longitude of San Francisco.  We'll choose SF's longitude
# as the azimuthal zero angle and SLC's will be a positive polar theta
# angle from SF when the Earth's center is the origin and the north
# pole points up the +z axis.  In other words, at the start, the
# origin is at the center of the Earth and the x axis passes through
# the equator with the same longitude as San Francisco.
sf_phi  = 90 - (37 + 47/60)

# Latitude and longitude of Salt Lake City 
slc_phi  = 90 - (40 + 45/60)
slc_long = (122 + 25/60) - (111 + 53/60)

! out("Longitude difference between SF and SLC =", sig(slc_long), "deg")

# Define points
<< r      , 0       ,  sf_phi, sf
<< r      , slc_long, slc_phi, slc
<< r + alt, slc_long, slc_phi, iss
! out("\nPoint definitions:")
print sf, slc, iss

# We can make an estimate of the altitude angle of the ISS using an
# approximate right triangle whose base is the chordal distance
# distance between SF and SLC and the triangle's height is the
# height above sea level of the ISS.  This will overestimate the
# true elevation because the Earth curves under SF's tangent plane.
dist sf, slc, dist
elev_estimate = atan(alt/dist)*180/pi
! out("\nChordal distance =", sig(dist), "km")
! out("Elevation estimate =", sig(elev_estimate), "deg")
dist sf, np, dist
! out("North pole to SF distance =", sig(dist), "km")

# Translate the origin to San Francisco
translate sf

# Rotate about the y axis by San Francisco's phi to make the z axis be
# normal to SF's tangent plane.
ijk         # Need unit vectors in the translated system
rotate sf_phi, j

# Change to spherical coordinates and print out the ISS' coordinates
# in SF's topocentric coordinate system.  The third coordinate will be
# the elevation above or below the tangent plane.
! out("\nISS coordinates in SF's topocentric system (elevation mode on)")
elev on
print iss

! out("\nNorth pole in SF's topocentric coordinates")
print np

off 
----------------------------------------------------------------------
You should get the following results:

North pole at start:
  np : Pt<<6378, 0, 0 o>>
Longitude difference between SF and SLC = 10.53 deg

Point definitions:
  sf  : Pt<<6378, 0, 52.22 o>>
  slc : Pt<<6378, 10.53, 49.25 o>>
  iss : Pt<<6793, 10.53, 49.25 o>>

Chordal distance = 964.3 km
Elevation estimate = 23.28 deg
North pole to SF distance = 5614 km

ISS coordinates in SF's topocentric system (elevation mode on)
  iss : Pt<<1078, 113.3, 18.23 oE>>

North pole in SF's topocentric coordinates
  np : Pt<<5614, 180, -26.11 oE>>
