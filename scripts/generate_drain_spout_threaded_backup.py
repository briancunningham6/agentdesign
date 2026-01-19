#!/usr/bin/env python3
"""
Generate a flexible drain spout for the coffee grounds compost container.
- Designed for TPU filament printing
- Screws horizontally into the threaded boss on the box
- Has a compression flange with sealing ring for watertight fit
- Extends 6cm to reach the sink
"""

import cadquery as cq
from cadquery import Workplane
import math

# Thread dimensions - MUST MATCH BOX
THREAD_MAJOR_DIAMETER = 16  # Outer diameter of thread (20% smaller)
THREAD_PITCH = 3  # mm per revolution
THREAD_LENGTH = 18  # Slightly shorter than box thread (20mm) for compression
DRAIN_BORE_DIAMETER = 12  # Inner hole - must accommodate spout tube and liquid flow

# Spout dimensions
SPOUT_OUTER_DIAMETER = 11.2  # 20% smaller
SPOUT_INNER_DIAMETER = 8  # Inner diameter for liquid flow
SPOUT_LENGTH = 60  # 6cm extension to reach sink
SPOUT_END_THREAD_DIAMETER = 12  # External thread on spout tip
SPOUT_END_THREAD_PITCH = 2
SPOUT_END_THREAD_LENGTH = 8

# Compression flange (presses against box wall for seal)
FLANGE_DIAMETER = 24  # Larger than thread for grip and sealing (20% smaller)
FLANGE_THICKNESS = 4

# Sealing ring groove (for O-ring or printed TPU seal)
SEAL_GROOVE_DIAMETER = 19.2  # 20% smaller
SEAL_GROOVE_WIDTH = 2
SEAL_GROOVE_DEPTH = 1.5

# Hex grip for tightening
HEX_SIZE = 20.8  # Across flats (20% smaller)
HEX_THICKNESS = 6

# Twist-close cap + gasket
CAP_WALL_THICKNESS = 2
CAP_HEIGHT = 10
CAP_CLEARANCE = 0.3
GASKET_THICKNESS = 2
GASKET_OUTER_DIAMETER = SPOUT_END_THREAD_DIAMETER + 4
GASKET_INNER_DIAMETER = DRAIN_BORE_DIAMETER + 1

# ============== THREADED SPOUT ==============

# Create the main flange with hex grip - extends backward (negative Z)
hex_flange = (
    Workplane("XY")
    .transformed(offset=(0, 0, -HEX_THICKNESS))
    .polygon(6, HEX_SIZE)
    .extrude(HEX_THICKNESS)
)

# Add circular flange base - extends backward from Z=0 (thread start)
flange_base = (
    Workplane("XY")
    .transformed(offset=(0, 0, -FLANGE_THICKNESS))
    .circle(FLANGE_DIAMETER / 2)
    .extrude(FLANGE_THICKNESS)
)

# Combine hex and circular flange
flange = hex_flange.union(flange_base)

# Create sealing ring groove on the face that contacts the box (at Z=0)
seal_groove = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SEAL_GROOVE_DEPTH))
    .circle(SEAL_GROOVE_DIAMETER / 2 + SEAL_GROOVE_WIDTH / 2)
    .circle(SEAL_GROOVE_DIAMETER / 2 - SEAL_GROOVE_WIDTH / 2)
    .extrude(SEAL_GROOVE_DEPTH)
)

flange_with_groove = flange.cut(seal_groove)

# Create the threaded section (screws into box) - starts at Z=0, extends forward
thread_base = (
    Workplane("XY")
    .circle(THREAD_MAJOR_DIAMETER / 2 - 0.5)  # Increased clearance for better fit
    .extrude(THREAD_LENGTH)
)

# Add external thread ridges
n_turns = THREAD_LENGTH / THREAD_PITCH
thread_section = thread_base

for i in range(int(n_turns * 12)):  # 12 segments per turn
    angle = (i / 12) * 360
    z_pos = (i / 12) * THREAD_PITCH

    if z_pos < THREAD_LENGTH - THREAD_PITCH / 2:
        # Create thread ridge
        ridge = (
            Workplane("XY")
            .transformed(offset=(0, 0, z_pos))
            .transformed(rotate=(0, 0, angle))
            .transformed(offset=(THREAD_MAJOR_DIAMETER / 2 - 1.7, 0, 0))
            .box(2.3, 1.6, THREAD_PITCH * 0.5, centered=True)
        )
        thread_section = thread_section.union(ridge)

# Add lead-in chamfer to threads for easy starting
thread_chamfer = (
    Workplane("XY")
    .transformed(offset=(0, 0, THREAD_LENGTH))
    .circle(THREAD_MAJOR_DIAMETER / 2)
    .workplane(offset=-2)
    .circle(THREAD_MAJOR_DIAMETER / 2 - 2)
    .loft()
)

thread_section = thread_section.cut(thread_chamfer)

# Create the spout tube (extends backward from flange rear face)
spout_tube = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS))
    .circle(SPOUT_OUTER_DIAMETER / 2)
    .extrude(SPOUT_LENGTH)
)

# Add external thread on spout tip for twist-close cap
spout_tip_base = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS))
    .circle(SPOUT_END_THREAD_DIAMETER / 2 - 0.4)
    .extrude(SPOUT_END_THREAD_LENGTH)
)

n_tip_turns = SPOUT_END_THREAD_LENGTH / SPOUT_END_THREAD_PITCH
spout_tip_thread = spout_tip_base
for i in range(int(n_tip_turns * 12)):
    angle = (i / 12) * 360
    z_pos = -SPOUT_LENGTH - FLANGE_THICKNESS + (i / 12) * SPOUT_END_THREAD_PITCH
    if z_pos < -SPOUT_LENGTH - FLANGE_THICKNESS + SPOUT_END_THREAD_LENGTH - SPOUT_END_THREAD_PITCH / 2:
        ridge = (
            Workplane("XY")
            .transformed(offset=(0, 0, z_pos))
            .transformed(rotate=(0, 0, angle))
            .transformed(offset=(SPOUT_END_THREAD_DIAMETER / 2 - 1.0, 0, 0))
            .box(2.0, 1.6, SPOUT_END_THREAD_PITCH * 0.5, centered=True)
        )
        spout_tip_thread = spout_tip_thread.union(ridge)

spout_tube = spout_tube.union(spout_tip_thread)

# Combine all external parts
spout_body = flange_with_groove.union(thread_section).union(spout_tube)

# Create the through bore
through_bore = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS - 5))
    .circle(SPOUT_INNER_DIAMETER / 2)
    .extrude(SPOUT_LENGTH + FLANGE_THICKNESS + THREAD_LENGTH + 10)
)

spout_with_bore = spout_body.cut(through_bore)

# Add funnel entrance at the threaded end to catch liquid
funnel = (
    Workplane("XY")
    .transformed(offset=(0, 0, THREAD_LENGTH))
    .circle(SPOUT_INNER_DIAMETER / 2 + 3)
    .workplane(offset=-4)
    .circle(SPOUT_INNER_DIAMETER / 2)
    .loft()
)

# Cut funnel into the bore
funnel_cut = (
    Workplane("XY")
    .transformed(offset=(0, 0, THREAD_LENGTH - 4))
    .circle(SPOUT_INNER_DIAMETER / 2 + 3)
    .extrude(5)
)

spout_with_funnel = spout_with_bore.cut(funnel_cut).union(funnel).cut(through_bore)

# Add drip tip angle at the spout end
drip_cutter = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS))
    .transformed(rotate=(20, 0, 0))
    .rect(SPOUT_OUTER_DIAMETER + 10, SPOUT_OUTER_DIAMETER + 10)
    .extrude(-10)
)

spout_final = spout_with_funnel.cut(drip_cutter)

# ============== TWIST-CLOSE CAP + GASKET ==============
cap_outer_diameter = SPOUT_END_THREAD_DIAMETER + 2 * CAP_WALL_THICKNESS + 2
cap = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS - CAP_HEIGHT))
    .circle(cap_outer_diameter / 2)
    .extrude(CAP_HEIGHT)
)

cap_bore = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS - CAP_HEIGHT + 1))
    .circle((SPOUT_END_THREAD_DIAMETER / 2) + CAP_CLEARANCE)
    .extrude(CAP_HEIGHT)
)

cap = cap.cut(cap_bore)

# Add internal thread ridges to cap
n_cap_turns = SPOUT_END_THREAD_LENGTH / SPOUT_END_THREAD_PITCH
cap_thread = None
for i in range(int(n_cap_turns * 12)):
    angle = (i / 12) * 360
    z_pos = -SPOUT_LENGTH - FLANGE_THICKNESS - CAP_HEIGHT + 1 + (i / 12) * SPOUT_END_THREAD_PITCH
    if z_pos < -SPOUT_LENGTH - FLANGE_THICKNESS - CAP_HEIGHT + 1 + SPOUT_END_THREAD_LENGTH - SPOUT_END_THREAD_PITCH / 2:
        ridge = (
            Workplane("XY")
            .transformed(offset=(0, 0, z_pos))
            .transformed(rotate=(0, 0, angle))
            .transformed(offset=(SPOUT_END_THREAD_DIAMETER / 2 - 0.8, 0, 0))
            .box(2.0, 1.6, SPOUT_END_THREAD_PITCH * 0.5, centered=True)
        )
        cap_thread = ridge if cap_thread is None else cap_thread.union(ridge)

if cap_thread is not None:
    cap = cap.cut(cap_thread)

gasket = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS - GASKET_THICKNESS))
    .circle(GASKET_OUTER_DIAMETER / 2)
    .circle(GASKET_INNER_DIAMETER / 2)
    .extrude(GASKET_THICKNESS)
)

# ============== SEALING RING (separate part) ==============
# A TPU O-ring that sits in the groove for watertight seal
seal_ring = (
    Workplane("XY")
    .circle(SEAL_GROOVE_DIAMETER / 2 + SEAL_GROOVE_WIDTH / 2 - 0.2)
    .circle(SEAL_GROOVE_DIAMETER / 2 - SEAL_GROOVE_WIDTH / 2 + 0.2)
    .extrude(SEAL_GROOVE_DEPTH + 0.5)  # Slightly proud to compress
)

# ============== ORIENT FOR PRINTING ==============
# Spout prints best standing up (flange on bed, threads pointing up)
spout_for_printing = spout_final.rotate((0, 0, 0), (1, 0, 0), 180)
spout_for_printing = spout_for_printing.translate((0, 0, SPOUT_LENGTH + FLANGE_THICKNESS + 5))

# ============== EXPORT ==============
spout_for_printing.val().exportStep("/Users/user/dev/3d Models/drain_spout.step")
spout_for_printing.val().exportStl("/Users/user/dev/3d Models/drain_spout.stl", tolerance=0.05)

seal_ring.val().exportStep("/Users/user/dev/3d Models/seal_ring.step")
seal_ring.val().exportStl("/Users/user/dev/3d Models/seal_ring.stl", tolerance=0.05)

# Export twist-close cap and gasket
cap.val().exportStep("/Users/user/dev/3d Models/spout_cap.step")
cap.val().exportStl("/Users/user/dev/3d Models/spout_cap.stl", tolerance=0.05)
gasket.val().exportStep("/Users/user/dev/3d Models/spout_gasket.step")
gasket.val().exportStl("/Users/user/dev/3d Models/spout_gasket.stl", tolerance=0.05)

# Export assembly reference (spout in installed orientation)
spout_final.val().exportStep("/Users/user/dev/3d Models/drain_spout_assembly.step")

print("✓ drain_spout.stl exported (oriented for printing)")
print("✓ drain_spout.step exported")
print("✓ seal_ring.stl exported (print in TPU)")
print("✓ seal_ring.step exported")
print("✓ drain_spout_assembly.step exported (reference orientation)")
print("\nThreaded Drain Spout for TPU Printing:")
print(f"  Thread diameter: {THREAD_MAJOR_DIAMETER}mm")
print(f"  Thread pitch: {THREAD_PITCH}mm")
print(f"  Thread length: {THREAD_LENGTH}mm")
print(f"  Flange diameter: {FLANGE_DIAMETER}mm (hex grip: {HEX_SIZE}mm)")
print(f"  Spout length: {SPOUT_LENGTH}mm")
print(f"  Inner bore: {SPOUT_INNER_DIAMETER}mm")
print(f"\nSeal Ring:")
print(f"  Diameter: {SEAL_GROOVE_DIAMETER}mm")
print(f"  Width: {SEAL_GROOVE_WIDTH}mm")
print(f"\nAssembly:")
print(f"  1. Place seal ring in groove on spout flange")
print(f"  2. Insert threaded end into box fitting from outside")
print(f"  3. Turn clockwise to tighten (hex grip for wrench)")
print(f"  4. Compression creates watertight seal")
print(f"\nTPU Print Settings:")
print(f"  - Print spout vertically (flange on bed)")
print(f"  - Layer height: 0.2mm")
print(f"  - Infill: 100% for threads and water-tightness")
print(f"  - Print seal ring flat, 100% infill")
