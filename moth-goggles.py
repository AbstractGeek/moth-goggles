import solid
import solid.utils as sutil
import numpy as np

# Output file settings
filename = "moth-goggles.scad"
SEGMENTS = 20
# Model settings
outer_sphere_radius = 50  # mm
inner_sphere_radius = 10  # mm
ommatidum_angle = 5  # deg
ommatidum_radius = np.tan(ommatidum_angle * np.pi / 180) * outer_sphere_radius
thickness = 0.5


def sph2cart(radius, azimuth, elevation):
    """Convert spherical coordinates to cartesian coordinates."""
    x = radius * np.cos(elevation * np.pi / 180) * \
        np.cos(azimuth * np.pi / 180)
    y = radius * np.cos(elevation * np.pi / 180) * \
        np.sin(azimuth * np.pi / 180)
    z = radius * np.sin(elevation * np.pi / 180)
    return x, y, z


def create_ommatidum(outer_sphere_radius,
                     inner_sphere_radius, ommatidum_radius):
    """Create an hexagonal based pyramid."""
    # Outer shell
    outer_shell = [tuple(np.round(sph2cart(ommatidum_radius, az, 0), 2))
                   for az in np.arange(0, 359, 60)]
    outer_points = [[0, 0, 0]] + [[outer_sphere_radius, x, y]
                                  for x, y, _ in outer_shell]
    # Inner shell
    inner_shell = [tuple(np.round(
        sph2cart(ommatidum_radius - thickness, az, 0), 2))
        for az in np.arange(0, 359, 60)]
    inner_points = [[0, 0, 0]] + [[outer_sphere_radius, x, y]
                                  for x, y, _ in inner_shell]

    # Define Faces
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [0, 3, 4],
        [0, 4, 5],
        [0, 5, 6],
        [0, 6, 1],
        [1, 2, 3, 4, 5, 6]]

    # Create ommatidum
    ommatidum = solid.difference()(
        solid.hull()(solid.polyhedron(outer_points, faces)),
        solid.hull()(solid.polyhedron(inner_points, faces)),
        solid.sphere(inner_sphere_radius)
    )
    return ommatidum


def create_moth_eye(ommatidum, ommatidum_angle):
    """Create moth eye using ommatidia."""
    azimuth = np.arange(0, 180, 2 * ommatidum_angle)
    elevation = np.arange(-45, 45, 2 * ommatidum_angle)
    moth_eye = solid.union()

    for el in elevation:
        for az in azimuth:
            moth_eye.add(solid.rotate([0, el, az])(ommatidum))

    return moth_eye


ommatidum = create_ommatidum(outer_sphere_radius,
                             inner_sphere_radius, ommatidum_radius)
moth_eye = create_moth_eye(ommatidum, ommatidum_angle)
solid.scad_render_to_file(moth_eye, filename,
                          file_header='$fn = %s;' % SEGMENTS)
