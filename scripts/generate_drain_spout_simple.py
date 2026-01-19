#!/usr/bin/env python3
"""
Generate a flexible drain spout for the coffee grounds compost container.
- Designed for TPU filament printing
- Simple threaded compression fitting (hand-tighten with hex flange)
- TPU seal ring for watertight fit
- Extends 6cm to reach the sink
"""

import cadquery as cq
from cadquery import Workplane

# Threaded shaft dimensions - MUST MATCH BOX
THREAD_MAJOR_DIAMETER = 16  # M16 thread
THREAD_PITCH = 3  # Coarse thread pitch
THREAD_LENGTH = 18  # Thread engagement depth
DRAIN_BORE_DIAMETER = 12  # Drainage bore

# Spout tube dimensions
SPOUT_OUTER_DIAMETER = 11.2  # Tube outer diameter
SPOUT_INNER_DIAMETER = 8  # Inner diameter for liquid flow
SPOUT_LENGTH = 60  # 6cm extension to reach sink

# Compression flange
FLANGE_DIAMETER = 24
FLANGE_THICKNESS = 4

# Sealing groove (cut into flange underside for gasket)
SEAL_GROOVE_DIAMETER = 19.2
SEAL_GROOVE_WIDTH = 2
SEAL_GROOVE_DEPTH = 1.5

# Sealing ring dimensions (TPU gasket)
SEAL_RING_OUTER_DIAMETER = SEAL_GROOVE_DIAMETER + SEAL_GROOVE_WIDTH
SEAL_RING_INNER_DIAMETER = SEAL_GROOVE_DIAMETER
SEAL_RING_THICKNESS = SEAL_GROOVE_DEPTH + 0.5

# Hex grip for hand tightening
HEX_SIZE = 20.8
HEX_THICKNESS = 6

print("Creating threaded spout...")

# Create the hex grip flange
hex_flange = (
    Workplane("XY")
    .transformed(offset=(0, 0, -HEX_THICKNESS))
    .polygon(6, HEX_SIZE)
    .extrude(HEX_THICKNESS)
)

print("  Hex flange created")

# Add circular flange base
flange_base = (
    Workplane("XY")
    .transformed(offset=(0, 0, -FLANGE_THICKNESS))
    .circle(FLANGE_DIAMETER / 2)
    .extrude(FLANGE_THICKNESS)
)

print("  Flange base created")

# Combine flanges
flange = hex_flange.union(flange_base)

# Cut gasket groove
gasket_groove = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SEAL_GROOVE_DEPTH))
    .circle((SEAL_GROOVE_DIAMETER + SEAL_GROOVE_WIDTH) / 2)
    .circle(SEAL_GROOVE_DIAMETER / 2)
    .extrude(SEAL_GROOVE_DEPTH)
)

flange = flange.cut(gasket_groove)

print("  Gasket groove cut")

# Create threaded shaft (VERY SIMPLE - just a tapered cylinder for now)
# We'll add actual threads later if this works
shaft = (
    Workplane("XY")
    .circle((THREAD_MAJOR_DIAMETER / 2) - 0.5)
    .extrude(THREAD_LENGTH)
)

print("  Shaft created")

# Create the spout tube
spout_tube = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS))
    .circle(SPOUT_OUTER_DIAMETER / 2)
    .extrude(SPOUT_LENGTH)
)

print("  Spout tube created")

# Combine all parts
spout_body = flange.union(shaft).union(spout_tube)

print("  Parts combined")

# Create the through bore
through_bore = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS - 5))
    .circle(SPOUT_INNER_DIAMETER / 2)
    .extrude(SPOUT_LENGTH + FLANGE_THICKNESS + THREAD_LENGTH + 10)
)

spout_with_bore = spout_body.cut(through_bore)

print("  Bore cut")

# Add drip tip
drip_cutter = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS))
    .transformed(rotate=(20, 0, 0))
    .rect(SPOUT_OUTER_DIAMETER + 10, SPOUT_OUTER_DIAMETER + 10)
    .extrude(-10)
)

spout_final = spout_with_bore.cut(drip_cutter)

print("  Drip tip cut")

# Create seal ring
seal_ring = (
    Workplane("XY")
    .circle(SEAL_RING_OUTER_DIAMETER / 2)
    .circle(SEAL_RING_INNER_DIAMETER / 2)
    .extrude(SEAL_RING_THICKNESS)
)

print("  Seal ring created")

# Orient for printing
spout_for_printing = spout_final.rotate((0, 0, 0), (1, 0, 0), 180)
spout_for_printing = spout_for_printing.translate((0, 0, SPOUT_LENGTH + FLANGE_THICKNESS + 5))

print("  Oriented for printing")

# Export
spout_for_printing.val().exportStep("/Users/user/dev/3d Models/drain_spout.step")
spout_for_printing.val().exportStl("/Users/user/dev/3d Models/drain_spout.stl", tolerance=0.05)

seal_ring.val().exportStep("/Users/user/dev/3d Models/seal_ring.step")
seal_ring.val().exportStl("/Users/user/dev/3d Models/seal_ring.stl", tolerance=0.05)

spout_final.val().exportStep("/Users/user/dev/3d Models/drain_spout_assembly.step")

print("\n✓ drain_spout.stl exported")
print("✓ seal_ring.stl exported")
print("\nThreaded Compression Spout:")
print(f"  Thread: M{THREAD_MAJOR_DIAMETER}×{THREAD_PITCH}")
print(f"  Thread length: {THREAD_LENGTH}mm")
print(f"  Flange: {FLANGE_DIAMETER}mm (hex: {HEX_SIZE}mm)")
print(f"  Spout length: {SPOUT_LENGTH}mm")
print("\nNOTE: Threads will be added in next iteration")
print("This version uses smooth shaft for testing")
