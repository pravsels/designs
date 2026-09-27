"""Drinks table: a ring top on a fan of spokes rising from a standing dome.

From the sketch page where the spoked cone resolved into "a weird wheel with
outward spokes", and the paper maquette's open ring top.

The open centre is the brief: there is no surface in the middle, so nothing
flat can be kept on it, and the only place to put anything is the band. That
band is a channel between two half-round lips, which is what makes a glass
safe on it — it cannot slide off the rim or into the hole.

The dome stands on its own flat face, so it needs nothing underneath it.

Millimetres throughout, z=0 is the floor. HEIGHT is the band's working
surface; the lip crowns stand LIP_SECTION above it.
"""

from __future__ import annotations

from cadgen import build123d as bd
from cadgen import glb, step, stl

from lib.table_forms import dome_surface_height, ridged_ring, spoke_fan, standing_dome

HEIGHT = 400.0
TOP_OUTER_DIAMETER = 440.0
# The hole is as large as it can be while the flat channel between the lips
# still takes a 65 mm tumbler base: at 250 the channel is 71 mm, at 280 it
# drops to 56 mm and a glass starts riding the lip crowns instead.
TOP_INNER_DIAMETER = 250.0
TOP_THICKNESS = 18.0
LIP_SECTION = 6.0

DOME_DIAMETER = 190.0

SPOKE_COUNT = 20
SPOKE_DIAMETER = 12.0
SPOKE_HUB_RADIUS = 55.0
SPOKE_RIM_RADIUS = 180.0

_TOP_UNDERSIDE = HEIGHT - TOP_THICKNESS
# Both ends of a spoke sit inside the part they meet, so no cut face shows.
_SPOKE_HUB_Z = dome_surface_height(DOME_DIAMETER / 2.0, SPOKE_HUB_RADIUS) - 12.0
_SPOKE_RIM_Z = _TOP_UNDERSIDE + 7.0


@step(out="../STEP/drinks_table.step")
@glb(out="../GLB/drinks_table.glb")
@stl(out="../STL/drinks_table.stl")
def drinks_table():
    top = ridged_ring(
        outer_radius=TOP_OUTER_DIAMETER / 2.0,
        inner_radius=TOP_INNER_DIAMETER / 2.0,
        thickness=TOP_THICKNESS,
        top_z=HEIGHT,
        lip_section=LIP_SECTION,
    )
    top.label = "top"
    top.color = bd.Color(0.87, 0.85, 0.80)

    dome = standing_dome(radius=DOME_DIAMETER / 2.0)
    dome.label = "dome"
    dome.color = bd.Color(0.28, 0.31, 0.34)

    spokes = spoke_fan(
        count=SPOKE_COUNT,
        hub_radius=SPOKE_HUB_RADIUS,
        hub_z=_SPOKE_HUB_Z,
        rim_radius=SPOKE_RIM_RADIUS,
        rim_z=_SPOKE_RIM_Z,
        section=SPOKE_DIAMETER / 2.0,
    )
    for spoke in spokes:
        spoke.color = bd.Color(0.62, 0.64, 0.66)

    return bd.Compound(children=[top, dome, *spokes], label="drinks_table")


if __name__ == "__main__":
    drinks_table()
