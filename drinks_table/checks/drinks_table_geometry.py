"""Measured checks for the drinks table's saved STEP.

Run from anywhere: `python checks/drinks_table_geometry.py`.

Everything here is measured off the saved document, not recomputed from the
model's constants, so a drifting model shows up as a failing number rather than
a matching pair of assumptions. Units are mm, mm^2, mm^3, kg.

Two kinds of result, kept apart on purpose:

FAULTS   the geometry is wrong — it does not stand, a part breaks a surface it
         should not, bodies interfere, topology is invalid. These are bugs.
FINDINGS a measured design criterion is not met. These are the author's call,
         not something a check should quietly design around.
"""

from __future__ import annotations

import math
from itertools import combinations
from pathlib import Path

from build123d import GeomType
from cadgen import read_scene
from cadgen.geometry import mass_properties, overlap_volume, topology_errors

DOCUMENT = Path(__file__).resolve().parent.parent / "STEP" / "drinks_table.step"

# Acceptance criteria for this design, chosen here rather than in the model.
TARGET_WORKING_HEIGHT = 400.0
TARGET_TOP_DIAMETER = 440.0
HEIGHT_TOLERANCE = 0.5
MIN_JOINT_OVERLAP_MM3 = 100.0

# A tumbler should stand flat in the channel; a laptop should not be usable.
TUMBLER_BASE_DIAMETER = 65.0
LAPTOP_FOOTPRINT = (300.0, 220.0)

# A lean on the rim should not put the table over. This number is a judgement
# about how the table will be used, not a fact about the geometry.
MIN_RIM_TIP_LOAD_KG = 20.0

STEEL = 7.85e-6
OAK = 0.75e-6
STONE = 2.65e-6
SCHEMES = {
    "all steel": {"top": STEEL, "dome": STEEL, "spoke": STEEL},
    "oak top, steel spokes, stone dome": {"top": OAK, "dome": STONE, "spoke": STEEL},
}


def _planar_faces_facing_up(shape):
    return [
        face
        for face in shape.faces()
        if face.geom_type == GeomType.PLANE and abs(face.normal_at(None).Z - 1.0) < 1e-6
    ]


def main() -> int:
    scene = read_scene(DOCUMENT)
    leaves = list(scene.leaves())
    labels = [leaf.label for leaf in leaves]
    parts = {leaf.label: leaf.shape() for leaf in leaves}

    faults: list[str] = []
    findings: list[str] = []

    inventory = ", ".join(
        f"{sum(1 for name in labels if name.startswith(kind))} {kind}"
        for kind in ("top", "dome", "spoke")
        if any(name.startswith(kind) for name in labels)
    )
    print(f"document      {scene.document_hash}")
    print(f"occurrences   {len(leaves)}  ({inventory})")

    # --- envelope -----------------------------------------------------------
    boxes = [shape.bounding_box() for shape in parts.values()]
    span_x = max(box.max.X for box in boxes) - min(box.min.X for box in boxes)
    span_y = max(box.max.Y for box in boxes) - min(box.min.Y for box in boxes)
    min_z = min(box.min.Z for box in boxes)
    max_z = max(box.max.Z for box in boxes)
    print(f"envelope      {span_x:.2f} x {span_y:.2f} x {max_z - min_z:.2f}")
    print(f"floor / crown z={min_z:.2f} .. z={max_z:.2f}")

    if abs(span_x - TARGET_TOP_DIAMETER) > HEIGHT_TOLERANCE:
        faults.append(f"top diameter {span_x:.2f} != {TARGET_TOP_DIAMETER}")
    if abs(min_z) > 1e-6:
        faults.append(f"table does not sit on z=0 (lowest point {min_z:.3f})")

    # --- the floor contact --------------------------------------------------
    contact = [
        (name, face)
        for name, shape in parts.items()
        for face in shape.faces()
        if face.geom_type == GeomType.PLANE and abs(face.center().Z) < 1e-6
    ]
    if contact:
        foot_area = sum(face.area for _, face in contact)
        foot_radius = math.sqrt(foot_area / math.pi)
        standing_on = sorted({name for name, _ in contact})
        print(f"foot          flat contact {2.0 * foot_radius:.2f} mm diameter "
              f"({foot_area:,.0f} mm2) at z=0 on {', '.join(standing_on)}")
    else:
        foot_radius = 0.0
        faults.append("no flat face at z=0: the table would rock on a point")

    # --- the ring top -------------------------------------------------------
    top = parts["top"]
    up_faces = _planar_faces_facing_up(top)
    by_height: dict[float, list] = {}
    for face in up_faces:
        by_height.setdefault(round(face.center().Z, 3), []).append(face)
    working_z = max(by_height) if by_height else float("nan")

    top_box = top.bounding_box()
    # The hole is measured from the innermost circular edge on the band, so it
    # is the real opening rather than a constant read back from the model.
    band_radii = sorted(
        edge.radius
        for face in by_height.get(working_z, [])
        for edge in face.edges()
        if edge.geom_type == GeomType.CIRCLE
    )
    channel_inner = band_radii[0] if band_radii else 0.0
    channel_outer = band_radii[-1] if band_radii else 0.0
    channel_width = channel_outer - channel_inner

    # Only circles centred on the table's axis describe the bore; a lip torus
    # also contributes small seam circles out at the tube.
    hole_radius = min(
        (
            edge.radius
            for edge in top.edges()
            if edge.geom_type == GeomType.CIRCLE
            and math.hypot(edge.arc_center.X, edge.arc_center.Y) < 1e-6
        ),
        default=0.0,
    )
    lip_crown = top_box.max.Z

    print(f"working face  z={working_z:.2f}, flat channel r {channel_inner:.1f} .. "
          f"{channel_outer:.1f} ({channel_width:.1f} mm wide)")
    print(f"lip crowns    {lip_crown - working_z:.2f} above the channel "
          f"(overall height {lip_crown:.2f})")
    print(f"open centre   {2.0 * hole_radius:.1f} mm hole, "
          f"band {(TARGET_TOP_DIAMETER / 2.0) - hole_radius:.1f} mm wide overall")

    if abs(working_z - TARGET_WORKING_HEIGHT) > HEIGHT_TOLERANCE:
        faults.append(f"working surface at {working_z:.2f}, wanted {TARGET_WORKING_HEIGHT}")
    if hole_radius <= 0.0:
        faults.append("the top has no open centre")

    nests = channel_width >= TUMBLER_BASE_DIAMETER
    print(f"tumbler       a {TUMBLER_BASE_DIAMETER:.0f} mm base "
          f"{'stands flat in the channel' if nests else 'rides the lip crowns'}, "
          f"captive between lips {lip_crown - working_z:.1f} mm proud")
    if not nests:
        findings.append(
            f"a {TUMBLER_BASE_DIAMETER:.0f} mm tumbler does not fit the "
            f"{channel_width:.1f} mm channel; widen the band or thin the lips"
        )

    # --- the anti-laptop claim, measured rather than asserted ---------------
    half_diagonal = math.hypot(*LAPTOP_FOOTPRINT) / 2.0
    bridges = half_diagonal > hole_radius
    print(f"laptop        {LAPTOP_FOOTPRINT[0]:.0f}x{LAPTOP_FOOTPRINT[1]:.0f} mm "
          f"half-diagonal {half_diagonal:.0f} mm vs {hole_radius:.0f} mm hole radius: "
          f"{'spans the hole, resting only on lip crowns' if bridges else 'falls through'}")
    if bridges and channel_width >= LAPTOP_FOOTPRINT[1]:
        findings.append("a laptop could sit flat on the band; the hole is not doing its job")

    # --- joints are real, and nothing breaks the working face ---------------
    dome = parts["dome"]
    spokes = {name: shape for name, shape in parts.items() if name.startswith("spoke")}
    top_solid = top.solids()[0]
    dome_solid = dome.solids()[0]
    weak_joints = []
    for name, spoke in sorted(spokes.items()):
        spoke_solid = spoke.solids()[0]
        into_top = overlap_volume(spoke_solid, top_solid)
        into_dome = overlap_volume(spoke_solid, dome_solid)
        if into_top < MIN_JOINT_OVERLAP_MM3 or into_dome < MIN_JOINT_OVERLAP_MM3:
            weak_joints.append((name, round(into_top), round(into_dome)))
        if spoke.bounding_box().max.Z > working_z - 1e-6:
            faults.append(f"{name} breaches the working face")
    sample = sorted(spokes)[0]
    print(f"spoke joints  {len(spokes)} spokes; {sample} buried "
          f"{overlap_volume(spokes[sample].solids()[0], top_solid):,.0f} mm3 into the top and "
          f"{overlap_volume(spokes[sample].solids()[0], dome_solid):,.0f} mm3 into the dome")
    if weak_joints:
        faults.append(f"spokes with a joint under {MIN_JOINT_OVERLAP_MM3} mm3: {weak_joints}")

    touching = [
        (a, b)
        for (a, sa), (b, sb) in combinations(sorted(spokes.items()), 2)
        if overlap_volume(sa.solids()[0], sb.solids()[0]) > 0.0
    ]
    print(f"spoke fouling {len(touching)} interfering spoke pairs")
    if touching:
        faults.append(f"spokes interfere: {touching[:4]}")

    # --- topology -----------------------------------------------------------
    bad_topology = []
    negative = []
    for name, shape in parts.items():
        if topology_errors(shape):
            bad_topology.append((name, [issue.code for issue in topology_errors(shape)]))
        for solid in shape.solids():
            if solid.volume <= 0.0:
                negative.append(name)
    print(f"topology      {len(parts)} parts checked, "
          f"{len(bad_topology)} with issues, {len(negative)} non-positive volumes")
    if bad_topology:
        faults.append(f"topology issues: {bad_topology}")
    if negative:
        faults.append(f"non-positive solid volume: {negative}")

    # --- stability ----------------------------------------------------------
    print()
    print(f"{'scheme':36} {'mass kg':>8} {'CoM z':>7} {'tip deg':>8} {'rim load kg':>12}")
    for scheme, densities in SCHEMES.items():
        bodies = [
            (solid, densities["spoke" if name.startswith("spoke") else name])
            for name, shape in parts.items()
            for solid in shape.solids()
        ]
        props = mass_properties(bodies)
        com_z = props.center_of_mass.Z
        tip_angle = math.degrees(math.atan(foot_radius / com_z)) if com_z else float("nan")
        lever = (TARGET_TOP_DIAMETER / 2.0) - foot_radius
        rim_load = props.mass * foot_radius / lever if lever > 0 else float("inf")
        print(f"{scheme:36} {props.mass:8.1f} {com_z:7.1f} {tip_angle:8.1f} {rim_load:12.1f}")
        if rim_load < MIN_RIM_TIP_LOAD_KG:
            findings.append(
                f"{scheme}: {rim_load:.1f} kg on the rim tips it, under the "
                f"{MIN_RIM_TIP_LOAD_KG:.0f} kg criterion"
            )

    print()
    if faults:
        print(f"FAULTS ({len(faults)}) — the geometry is wrong")
        for fault in faults:
            print(f"  - {fault}")
    else:
        print("No geometry faults.")
    if findings:
        print(f"FINDINGS ({len(findings)}) — for the designer to rule on")
        for finding in findings:
            print(f"  - {finding}")
    return 1 if faults else 0


if __name__ == "__main__":
    raise SystemExit(main())
