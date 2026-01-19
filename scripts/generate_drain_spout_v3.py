#!/usr/bin/env python3
"""
Generate a flexible drain spout for the coffee grounds compost container.
- Designed for TPU filament printing
- Threaded compression fitting (hand-tighten with hex flange)
- TPU seal ring for watertight fit
- Extends 6cm to reach the sink
"""

import cadquery as cq
from cadquery import Workplane
import math

# Threaded shaft dimensions - MUST MATCH BOX
THREAD_MAJOR_DIAMETER = 16  # M16 thread
THREAD_PITCH = 3  # Coarse thread pitch
THREAD_LENGTH = 18  # Thread engagement depth (slightly less than box for gasket compression)
DRAIN_BORE_DIAMETER = 12  # Must be larger than SPOUT_OUTER_DIAMETER (11.2mm)

# Spout tube dimensions
SPOUT_OUTER_DIAMETER = 11.2  # Tube outer diameter
SPOUT_INNER_DIAMETER = 8  # Inner diameter for liquid flow
SPOUT_LENGTH = 60  # 6cm extension to reach sink

# Compression flange (presses gasket against box wall)
FLANGE_DIAMETER = 24  # Larger than boss for gasket compression
FLANGE_THICKNESS = 4

# Sealing groove (cut into flange underside for gasket)
SEAL_GROOVE_DIAMETER = 19.2  # Sits around boss perimeter
SEAL_GROOVE_WIDTH = 2  # Gasket width
SEAL_GROOVE_DEPTH = 1.5  # Gasket compresses into this

# Sealing ring dimensions (TPU gasket - sits in groove)
SEAL_RING_OUTER_DIAMETER = SEAL_GROOVE_DIAMETER + SEAL_GROOVE_WIDTH
SEAL_RING_INNER_DIAMETER = SEAL_GROOVE_DIAMETER
SEAL_RING_THICKNESS = SEAL_GROOVE_DEPTH + 0.5  # Slightly thicker so it compresses

# Hex grip for hand tightening
HEX_SIZE = 20.8  # Across flats
HEX_THICKNESS = 6

# ============== THREADED COMPRESSION SPOUT ==============

# Coordinate system: Z=0 is where flange contacts wall
# Shaft extends forward (positive Z) into boss
# Tube extends backward (negative Z) away from wall

# Create the hex grip flange (for hand tightening)
hex_flange = (
    Workplane("XY")
    .transformed(offset=(0, 0, -HEX_THICKNESS))
    .polygon(6, HEX_SIZE)
    .extrude(HEX_THICKNESS)
)

# Add circular flange base (compresses gasket)
flange_base = (
    Workplane("XY")
    .transformed(offset=(0, 0, -FLANGE_THICKNESS))
    .circle(FLANGE_DIAMETER / 2)
    .extrude(FLANGE_THICKNESS)
)

# Combine hex and circular flange
flange = hex_flange.union(flange_base)

# Cut gasket groove into underside of flange
gasket_groove = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SEAL_GROOVE_DEPTH))
    .circle((SEAL_GROOVE_DIAMETER + SEAL_GROOVE_WIDTH) / 2)
    .circle(SEAL_GROOVE_DIAMETER / 2)
    .extrude(SEAL_GROOVE_DEPTH)
)

flange = flange.cut(gasket_groove)

# Create the threaded shaft (simplified approach - ridges for thread)
shaft_base = (
    Workplane("XY")
    .circle((THREAD_MAJOR_DIAMETER / 2) - 0.5)  # Slight clearance for smooth threading
    .extrude(THREAD_LENGTH)
)

# Create external threads using helical ridges (simplified)
n_turns = THREAD_LENGTH / THREAD_PITCH

# Build thread ridges
shaft_with_threads = shaft_base
for turn in range(int(n_turns)):
    for segment in range(8):  # 8 segments per turn
        angle = (turn * 8 + segment) * (360.0 / 8)
        z_pos = turn * THREAD_PITCH + (segment / 8.0) * THREAD_PITCH

        if z_pos < THREAD_LENGTH - THREAD_PITCH / 4:
            ridge = (
                Workplane("XY")
                .transformed(offset=(0, 0, z_pos))
                .transformed(rotate=(0, 0, angle))
                .transformed(offset=((THREAD_MAJOR_DIAMETER / 2) - 0.9, 0, 0))
                .box(1.8, 1.0, THREAD_PITCH * 0.4, centered=True)
            )
            shaft_with_threads = shaft_with_threads.union(ridge)

# Create the spout tube (extends backward from flange)
spout_tube = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS))
    .circle(SPOUT_OUTER_DIAMETER / 2)
    .extrude(SPOUT_LENGTH)
)

# Combine all external parts
spout_body = flange.union(shaft_with_threads).union(spout_tube)

# Create the through bore
through_bore = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS - 5))
    .circle(SPOUT_INNER_DIAMETER / 2)
    .extrude(SPOUT_LENGTH + FLANGE_THICKNESS + THREAD_LENGTH + 10)
)

spout_with_bore = spout_body.cut(through_bore)

# Add funnel entrance at the shaft end to catch liquid
funnel = (
    Workplane("XY")
    .transformed(offset=(0, 0, THREAD_LENGTH))
    .circle(SPOUT_INNER_DIAMETER / 2 + 3)
    .workplane(offset=-4)
    .circle(SPOUT_INNER_DIAMETER / 2)
    .loft()
)

spout_with_funnel = spout_with_bore.union(funnel)

# Add drip tip angle at the spout end
drip_cutter = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS))
    .transformed(rotate=(20, 0, 0))
    .rect(SPOUT_OUTER_DIAMETER + 10, SPOUT_OUTER_DIAMETER + 10)
    .extrude(-10)
)

spout_final = spout_with_funnel.cut(drip_cutter)

# ============== SEALING RING (separate TPU part) ==============
# Ring sits in groove on flange underside, compressed against box wall
seal_ring = (
    Workplane("XY")
    .circle(SEAL_RING_OUTER_DIAMETER / 2)
    .circle(SEAL_RING_INNER_DIAMETER / 2)
    .extrude(SEAL_RING_THICKNESS)
)

# ============== ORIENT FOR PRINTING ==============
# Spout prints best standing up (flange on bed, shaft pointing up)
spout_for_printing = spout_final.rotate((0, 0, 0), (1, 0, 0), 180)
spout_for_printing = spout_for_printing.translate((0, 0, SPOUT_LENGTH + FLANGE_THICKNESS + 5))

# ============== EXPORT ==============
spout_for_printing.val().exportStep("/Users/user/dev/3d Models/drain_spout.step")
spout_for_printing.val().exportStl("/Users/user/dev/3d Models/drain_spout.stl", tolerance=0.05)

seal_ring.val().exportStep("/Users/user/dev/3d Models/seal_ring.step")
seal_ring.val().exportStl("/Users/user/dev/3d Models/seal_ring.stl", tolerance=0.05)

# Export assembly reference (spout in installed orientation)
spout_final.val().exportStep("/Users/user/dev/3d Models/drain_spout_assembly.step")

print("✓ drain_spout.stl exported (oriented for printing)")
print("✓ drain_spout.step exported")
print("✓ seal_ring.stl exported (print in TPU)")
print("✓ seal_ring.step exported")
print("✓ drain_spout_assembly.step exported (reference orientation)")
print("\nThreaded Compression Drain Spout for TPU Printing:")
print(f"  Thread: M{THREAD_MAJOR_DIAMETER}×{THREAD_PITCH}")
print(f"  Thread length: {THREAD_LENGTH}mm")
print(f"  Flange diameter: {FLANGE_DIAMETER}mm (hex grip: {HEX_SIZE}mm)")
print(f"  Spout length: {SPOUT_LENGTH}mm")
print(f"  Inner bore: {SPOUT_INNER_DIAMETER}mm")
print(f"\nSeal Ring (TPU):")
print(f"  Outer diameter: {SEAL_RING_OUTER_DIAMETER:.1f}mm")
print(f"  Inner diameter: {SEAL_RING_INNER_DIAMETER:.1f}mm")
print(f"  Thickness: {SEAL_RING_THICKNESS:.1f}mm (compresses into {SEAL_GROOVE_DEPTH}mm groove)")
print(f"\nInstallation:")
print(f"  1. Place TPU seal ring into groove on flange underside")
print(f"  2. Start threading spout into boss by hand")
print(f"  3. Hand-tighten using hex flange")
print(f"     - Gasket compresses as you tighten")
print(f"     - Creates watertight seal")
print(f"  4. Remove: Hand-loosen and unthread")
print(f"\nTPU Print Settings:")
print(f"  - Print spout vertically (flange on bed)")
print(f"  - Layer height: 0.2mm")
print(f"  - Infill: 100% for water-tightness")
print(f"  - Print seal ring flat, 100% infill")
