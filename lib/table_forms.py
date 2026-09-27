"""Shared geometry factories for the table design studies.

Every dimension is millimetres. Tables stand on the XY plane with +Z up, and
the functional datum is the floor: z=0 is the contact patch, so a model's
total height is the z of its top face.
"""

from __future__ import annotations

from cadgen import build123d as bd


def standing_dome(radius: float) -> bd.Shape:
    """A hemisphere standing on its flat face, curving up to a crown.

    The flat face is the floor contact, so the footprint is the full diameter
    and the form needs nothing underneath it to stand.
    """
    return bd.Sphere(
        radius,
        arc_size1=0,
        arc_size2=90,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )


def dome_surface_height(radius: float, at_radius: float) -> float:
    """Height of `standing_dome`'s surface at a given distance from the axis."""
    if not 0.0 <= at_radius <= radius:
        raise ValueError("at_radius must lie within the dome")
    return (radius**2 - at_radius**2) ** 0.5


def ridged_ring(
    outer_radius: float,
    inner_radius: float,
    thickness: float,
    top_z: float,
    lip_section: float,
) -> bd.Shape:
    """An annular top whose band is a channel between two half-round lips.

    The open centre is the point: there is no surface in the middle to rest
    anything flat on. The lips stand proud of the band at both edges, so a
    glass on the band is captive between them rather than free to slide off
    the rim or into the hole.
    """
    if inner_radius >= outer_radius:
        raise ValueError("inner_radius must be smaller than outer_radius")

    band = bd.Pos(0.0, 0.0, top_z) * bd.Cylinder(
        outer_radius,
        thickness,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX),
    )
    band -= bd.Pos(0.0, 0.0, top_z) * bd.Cylinder(
        inner_radius,
        thickness * 3.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER),
    )

    # Each lip is a torus centred on the band's top face, so exactly its upper
    # half stands proud, and centred on an edge so its inner half overhangs
    # nothing — the section sets both how proud it stands and how far in it
    # reaches.
    band += bd.Pos(0.0, 0.0, top_z) * bd.Torus(outer_radius - lip_section, lip_section)
    band += bd.Pos(0.0, 0.0, top_z) * bd.Torus(inner_radius + lip_section, lip_section)
    return band


def rod(start: tuple[float, float, float], end: tuple[float, float, float], radius: float) -> bd.Shape:
    """A round rod along the segment from `start` to `end`.

    The rod is cut square at both ends: callers bury the ends inside the parts
    they join, so a square cut never shows.
    """
    direction = bd.Vector(*end) - bd.Vector(*start)
    length = direction.length
    if length <= 0.0:
        raise ValueError("start and end must differ")

    axis = bd.Plane(origin=bd.Vector(*start), z_dir=direction)
    return axis * bd.Cylinder(
        radius,
        length,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )


def spoke_fan(
    count: int,
    hub_radius: float,
    hub_z: float,
    rim_radius: float,
    rim_z: float,
    section: float,
) -> list[bd.Shape]:
    """`count` rods splaying out and up from a hub circle to a rim circle.

    Returns the rods as separate labelled shapes rather than one fused solid,
    so each stays selectable in review.
    """
    if count < 3:
        raise ValueError("a fan needs at least three spokes")

    first = rod((hub_radius, 0.0, hub_z), (rim_radius, 0.0, rim_z), section)
    spokes: list[bd.Shape] = []
    for index in range(count):
        spoke = bd.Rot(0.0, 0.0, index * 360.0 / count) * first
        spoke.label = f"spoke_{index + 1:02d}"
        spokes.append(spoke)
    return spokes
