#!/usr/bin/env python3
"""
Generate a drain spout with bayonet lock mechanism for horizontal insertion.
Features:
- 5cm external extension
- Bayonet lock with radial tabs and J-slots (works for horizontal insertion)
- TPU gasket seal for watertight fit
- Removable threaded cap with tether attachment
"""

import cadquery as cq
from cadquery import Workplane
import math

# ============== BAYONET SHAFT DIMENSIONS ==============
# These MUST match the boss socket in the box
SPOUT_SHAFT_DIAMETER = 16  # Shaft that inserts into boss
SPOUT_SHAFT_LENGTH = 20  # Insertion depth (must fit in boss cavity)

# Bayonet tab dimensions (radial protrusions for J-slot engagement)
TAB_COUNT = 3  # Tabs at 0°, 120°, 240°
TAB_HEIGHT = 2.5  # Radial protrusion from shaft
TAB_WIDTH = 5  # Circumferential width
TAB_THICKNESS = 2  # Axial thickness
TAB_POSITION = 16  # Distance from shaft tip (near end for lock engagement)

# ============== SPOUT TUBE DIMENSIONS ==============
SPOUT_OUTER_DIAMETER = 12  # External tube diameter
SPOUT_INNER_DIAMETER = 9  # Internal bore for liquid flow
SPOUT_LENGTH = 50  # 5cm extension to reach sink

# ============== FLANGE DIMENSIONS ==============
# Flange stays outside box, compresses gasket against wall
FLANGE_DIAMETER = 28  # Large enough for gasket seal
FLANGE_THICKNESS = 4  # Thick enough for hex grip
HEX_SIZE = 22  # Hex grip for installation (across flats)

# ============== GASKET DIMENSIONS ==============
SEAL_RING_OUTER = 26  # Fits under flange
SEAL_RING_INNER = 17  # Clears hole in wall
SEAL_RING_THICKNESS = 2  # Uncompressed TPU thickness

# ============== CAP DIMENSIONS ==============
CAP_THREAD_DIAMETER = 14  # External thread on spout tip
CAP_THREAD_PITCH = 2  # Thread pitch
CAP_THREAD_LENGTH = 10  # Thread engagement length
CAP_OUTER_DIAMETER = 18  # Cap outer size
CAP_HEIGHT = 15  # Cap total height
CAP_WALL_THICKNESS = 2  # Cap wall thickness

# Tether attachment
TETHER_HOLE_DIAMETER = 3  # Hole for cord/wire tether
TETHER_POSITION_FROM_CAP = 8  # Distance from cap to tether hole on spout

# ============== CREATE SPOUT BODY ==============

# Coordinate system: Z=0 is where flange contacts wall
# Shaft extends forward (positive Z) into box
# Tube extends backward (negative Z) away from wall

# Hex flange for hand tightening
hex_flange = (
    Workplane("XY")
    .transformed(offset=(0, 0, -FLANGE_THICKNESS))
    .polygon(6, HEX_SIZE)
    .extrude(FLANGE_THICKNESS)
)

# Circular flange base (sealing surface for gasket)
flange_base = (
    Workplane("XY")
    .transformed(offset=(0, 0, -FLANGE_THICKNESS))
    .circle(FLANGE_DIAMETER / 2)
    .extrude(FLANGE_THICKNESS)
)

flange = hex_flange.union(flange_base)

# Create bayonet shaft (inserts into boss)
shaft = (
    Workplane("XY")
    .circle(SPOUT_SHAFT_DIAMETER / 2 - 0.15)  # Slight clearance
    .extrude(SPOUT_SHAFT_LENGTH)
)

# Add bayonet tabs (3 tabs at 0°, 120°, 240°)
tab_angles = [0, 120, 240]
shaft_with_tabs = shaft

for angle in tab_angles:
    # Create radial tab (rectangular protrusion)
    tab = (
        Workplane("XY")
        .transformed(offset=(0, 0, TAB_POSITION))
        .transformed(rotate=(0, 0, angle))
        .transformed(offset=(SPOUT_SHAFT_DIAMETER / 2 - 0.15, 0, 0))
        .box(TAB_HEIGHT, TAB_WIDTH, TAB_THICKNESS, centered=(False, True, True))
    )
    shaft_with_tabs = shaft_with_tabs.union(tab)

# Add alignment mark on flange (shows where first tab points)
alignment_mark = (
    Workplane("XY")
    .transformed(offset=(0, 0, -FLANGE_THICKNESS / 2))
    .transformed(rotate=(0, 0, 0))
    .transformed(offset=(FLANGE_DIAMETER / 2 - 2, 0, 0))
    .box(4, 1.5, FLANGE_THICKNESS + 0.5, centered=True)
)

flange = flange.cut(alignment_mark)

# Create the spout tube (extends backward from flange)
spout_tube = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS))
    .circle(SPOUT_OUTER_DIAMETER / 2)
    .extrude(SPOUT_LENGTH)
)

# Add external thread on spout tip for cap
thread_base = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS))
    .circle(CAP_THREAD_DIAMETER / 2)
    .extrude(CAP_THREAD_LENGTH)
)

# Create thread ridges
n_turns = CAP_THREAD_LENGTH / CAP_THREAD_PITCH
thread_with_ridges = thread_base

for i in range(int(n_turns * 16)):  # 16 segments per turn for smooth thread
    angle = (i / 16) * 360
    z_pos = -SPOUT_LENGTH - FLANGE_THICKNESS + (i / 16) * CAP_THREAD_PITCH

    if z_pos < -SPOUT_LENGTH - FLANGE_THICKNESS + CAP_THREAD_LENGTH - CAP_THREAD_PITCH / 2:
        ridge = (
            Workplane("XY")
            .transformed(offset=(0, 0, z_pos))
            .transformed(rotate=(0, 0, angle))
            .transformed(offset=(CAP_THREAD_DIAMETER / 2 - 0.8, 0, 0))
            .box(1.6, 1.2, CAP_THREAD_PITCH * 0.4, centered=True)
        )
        thread_with_ridges = thread_with_ridges.union(ridge)

spout_tube = spout_tube.union(thread_with_ridges)

# Add tether hole on shaft (for cap retention cord)
tether_hole = (
    Workplane("YZ")
    .workplane(offset=TETHER_POSITION_FROM_CAP)
    .circle(TETHER_HOLE_DIAMETER / 2)
    .extrude(SPOUT_SHAFT_DIAMETER + 2)
)

# Combine all external parts
spout_body = flange.union(shaft_with_tabs).union(spout_tube)

# Cut tether hole through shaft
spout_body = spout_body.cut(tether_hole)

# Create the through bore for liquid drainage
through_bore = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS - 5))
    .circle(SPOUT_INNER_DIAMETER / 2)
    .extrude(SPOUT_LENGTH + FLANGE_THICKNESS + SPOUT_SHAFT_LENGTH + 10)
)

spout_with_bore = spout_body.cut(through_bore)

# Add funnel entrance at shaft end to catch liquid
funnel = (
    Workplane("XY")
    .transformed(offset=(0, 0, SPOUT_SHAFT_LENGTH))
    .circle(SPOUT_INNER_DIAMETER / 2 + 4)
    .workplane(offset=-5)
    .circle(SPOUT_INNER_DIAMETER / 2)
    .loft()
)

# Cut funnel cavity
funnel_cut = (
    Workplane("XY")
    .transformed(offset=(0, 0, SPOUT_SHAFT_LENGTH - 5))
    .circle(SPOUT_INNER_DIAMETER / 2 + 4)
    .extrude(6)
)

spout_final = spout_with_bore.cut(funnel_cut).union(funnel).cut(through_bore)

# Add drip tip angle at the spout end
drip_cutter = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS))
    .transformed(rotate=(25, 0, 0))
    .rect(SPOUT_OUTER_DIAMETER + 10, SPOUT_OUTER_DIAMETER + 10)
    .extrude(-10)
)

spout_final = spout_final.cut(drip_cutter)

# ============== CREATE THREADED CAP ==============

cap_body = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS - CAP_HEIGHT))
    .circle(CAP_OUTER_DIAMETER / 2)
    .extrude(CAP_HEIGHT)
)

# Cut internal bore for thread
cap_bore = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS - CAP_HEIGHT + CAP_WALL_THICKNESS))
    .circle(CAP_THREAD_DIAMETER / 2 + 0.3)  # Thread clearance
    .extrude(CAP_HEIGHT)
)

cap = cap_body.cut(cap_bore)

# Add internal thread ridges to cap
cap_thread = None
for i in range(int(n_turns * 16)):
    angle = (i / 16) * 360
    z_pos = -SPOUT_LENGTH - FLANGE_THICKNESS - CAP_HEIGHT + CAP_WALL_THICKNESS + (i / 16) * CAP_THREAD_PITCH

    if z_pos < -SPOUT_LENGTH - FLANGE_THICKNESS - CAP_HEIGHT + CAP_WALL_THICKNESS + CAP_THREAD_LENGTH - CAP_THREAD_PITCH / 2:
        ridge = (
            Workplane("XY")
            .transformed(offset=(0, 0, z_pos))
            .transformed(rotate=(0, 0, angle))
            .transformed(offset=(CAP_THREAD_DIAMETER / 2 - 0.5, 0, 0))
            .box(1.6, 1.2, CAP_THREAD_PITCH * 0.4, centered=True)
        )
        cap_thread = ridge if cap_thread is None else cap_thread.union(ridge)

if cap_thread is not None:
    cap = cap.cut(cap_thread)

# Add tether hole on cap
cap_tether_hole = (
    Workplane("YZ")
    .workplane(offset=0)
    .transformed(offset=(0, -SPOUT_LENGTH - FLANGE_THICKNESS - CAP_HEIGHT / 2, 0))
    .circle(TETHER_HOLE_DIAMETER / 2)
    .extrude(CAP_OUTER_DIAMETER + 2)
)

cap = cap.cut(cap_tether_hole)

# Add grip ridges on cap exterior
for i in range(8):
    angle = i * 45
    ridge = (
        Workplane("XY")
        .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS - CAP_HEIGHT / 2))
        .transformed(rotate=(0, 0, angle))
        .transformed(offset=(CAP_OUTER_DIAMETER / 2 - 0.5, 0, 0))
        .box(1, 2, CAP_HEIGHT - 4, centered=True)
    )
    cap = cap.union(ridge)

# ============== CREATE TPU SEAL RING ==============

seal_ring = (
    Workplane("XY")
    .circle(SEAL_RING_OUTER / 2)
    .circle(SEAL_RING_INNER / 2)
    .extrude(SEAL_RING_THICKNESS)
)

# ============== ORIENT FOR PRINTING ==============

# Spout prints vertically (flange on bed, shaft pointing up)
spout_for_printing = spout_final.rotate((0, 0, 0), (1, 0, 0), 180)
spout_for_printing = spout_for_printing.translate((0, 0, SPOUT_LENGTH + FLANGE_THICKNESS + CAP_THREAD_LENGTH + 2))

# Cap prints upside down (open end on bed)
cap_for_printing = cap.rotate((0, 0, 0), (1, 0, 0), 180)
cap_for_printing = cap_for_printing.translate((35, 0, CAP_HEIGHT))

# ============== EXPORT ==============

spout_for_printing.val().exportStep("/Users/user/dev/3d Models/drain_spout_v2.step")
spout_for_printing.val().exportStl("/Users/user/dev/3d Models/drain_spout_v2.stl", tolerance=0.05)

cap_for_printing.val().exportStep("/Users/user/dev/3d Models/spout_cap_v2.step")
cap_for_printing.val().exportStl("/Users/user/dev/3d Models/spout_cap_v2.stl", tolerance=0.05)

seal_ring.val().exportStep("/Users/user/dev/3d Models/seal_ring_v2.step")
seal_ring.val().exportStl("/Users/user/dev/3d Models/seal_ring_v2.stl", tolerance=0.05)

# Export assembly reference (spout in installed orientation)
spout_final.val().exportStep("/Users/user/dev/3d Models/drain_spout_assembly_v2.step")

print("✓ drain_spout_v2.stl exported (oriented for printing)")
print("✓ drain_spout_v2.step exported")
print("✓ spout_cap_v2.stl exported (print with threads)")
print("✓ spout_cap_v2.step exported")
print("✓ seal_ring_v2.stl exported (print in TPU)")
print("✓ seal_ring_v2.step exported")
print("✓ drain_spout_assembly_v2.step exported (reference orientation)")
print("\nBayonet Drain Spout System:")
print(f"  Shaft diameter: {SPOUT_SHAFT_DIAMETER}mm")
print(f"  Shaft length: {SPOUT_SHAFT_LENGTH}mm")
print(f"  Bayonet tabs: {TAB_COUNT}× at 0°, 120°, 240°")
print(f"  Tab dimensions: {TAB_HEIGHT}mm × {TAB_WIDTH}mm × {TAB_THICKNESS}mm")
print(f"  Tab position: {TAB_POSITION}mm from shaft tip")
print(f"  Flange diameter: {FLANGE_DIAMETER}mm (hex grip: {HEX_SIZE}mm)")
print(f"  Spout extension: {SPOUT_LENGTH}mm (5cm)")
print(f"  Inner bore: {SPOUT_INNER_DIAMETER}mm")
print(f"\nThreaded Cap:")
print(f"  Thread: M{CAP_THREAD_DIAMETER} × {CAP_THREAD_PITCH}mm pitch")
print(f"  Cap outer diameter: {CAP_OUTER_DIAMETER}mm")
print(f"  Cap height: {CAP_HEIGHT}mm")
print(f"  Tether holes: {TETHER_HOLE_DIAMETER}mm (on spout and cap)")
print(f"\nTPU Seal Ring:")
print(f"  Outer diameter: {SEAL_RING_OUTER}mm")
print(f"  Inner diameter: {SEAL_RING_INNER}mm")
print(f"  Thickness: {SEAL_RING_THICKNESS}mm (compresses ~30% for seal)")
print(f"\nInstallation:")
print(f"  1. Place seal ring on wall exterior around drain hole")
print(f"  2. Align spout - alignment mark points to J-slot entries")
print(f"  3. Push spout straight in (20mm insertion depth)")
print(f"  4. Rotate ~30° clockwise to lock bayonet tabs")
print(f"  5. Gasket compresses for watertight seal")
print(f"  6. Attach tether cord through holes (prevents cap loss)")
print(f"\nRemoval:")
print(f"  Rotate ~30° counter-clockwise, pull out")
