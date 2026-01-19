#!/usr/bin/env python3
"""
Generate a combined fit-test plate for the box drain, spout, lid socket, and scraper.
Outputs a single STL/STEP so it can be printed together.
"""

import cadquery as cq
from cadquery import Workplane
import math
import random

# ============== SHARED DIMENSIONS (match main scripts) ==============
# Box / drain
BOX_LENGTH = 200
BOX_WIDTH = 150
BOX_HEIGHT = 150
WALL_THICKNESS = 4
SLOPE_ANGLE = 4  # Increased for positive drainage

# Threaded drain fitting dimensions
THREAD_MAJOR_DIAMETER = 16  # M16 thread
THREAD_PITCH = 3  # Coarse thread pitch
THREAD_LENGTH = 20  # Thread engagement depth (box side)
THREAD_LENGTH_SPOUT = 18  # Thread length on spout (slightly less for gasket compression)
DRAIN_HOLE_DIAMETER = 17  # Clearance for threaded shaft
DRAIN_BORE = 10  # Internal bore for liquid flow

BOSS_OUTER_DIAMETER = 22.4  # Threaded boss cylinder
BOSS_LENGTH = 15  # Boss extends into box interior

DRAIN_CENTER_HEIGHT = 5 + DRAIN_HOLE_DIAMETER / 2  # 5mm from bottom + radius

# Lid / scraper
LID_TOP_THICKNESS = 5
RECESS_DEPTH = 10
RECESS_CLEARANCE = 0.5
RECESS_OVERLAP = 0.2

CAPSULE_DIAMETER = 37
CAPSULE_HEIGHT = 38
SCRAPER_BASE_DIAMETER = 28
SCRAPER_BASE_HEIGHT = 3
PIN_COUNT = 8
PIN_LENGTH = 29.75  # 15% shorter than original 35mm
PIN_DIAMETER = 2.5
PIN_REINFORCEMENT_HEIGHT = 4  # Solid infill base reinforcement for pins

# Scraper attachment - Bayonet lock mechanism
SCRAPER_BOSS_DIAMETER = 14
SCRAPER_BOSS_HEIGHT = 4
SCRAPER_BOSS_CLEARANCE = 0.2  # Tighter fit
SCRAPER_BOSS_OVERLAP = 0.3

# Bayonet lock dimensions
SCRAPER_SHAFT_DIAMETER = 14.0  # Base shaft diameter
SCRAPER_SHAFT_HEIGHT = 10  # Full height for deep engagement
SCRAPER_SOCKET_DIAMETER = 14.2  # 0.2mm clearance for smooth rotation
SCRAPER_SOCKET_DEPTH = 10  # Full depth to match shaft height

BAYONET_TAB_COUNT = 3  # Three tabs at 120° spacing
BAYONET_TAB_HEIGHT = 2  # Axial height of tab
BAYONET_TAB_LENGTH = 4  # Length along shaft axis
BAYONET_TAB_PROTRUSION = 1  # Radial extension from shaft
BAYONET_ROTATION_ANGLE = 60  # Degrees to rotate for locking

BAYONET_SLOT_WIDTH = 2.2  # Tab width + 0.2mm clearance
BAYONET_SLOT_VERTICAL = 6  # Vertical entry slot depth
BAYONET_SLOT_HORIZONTAL = 4  # Horizontal lock slot width
BAYONET_LOCK_DEPTH = 2  # Depth of horizontal lock groove

# Spout (threaded compression fitting)
SPOUT_OUTER_DIAMETER = 11.2
SPOUT_INNER_DIAMETER = 8
SPOUT_LENGTH = 50  # 5cm extension (shorter for fit test)
FLANGE_DIAMETER = 24
FLANGE_THICKNESS = 4
HEX_SIZE = 20.8  # Hex flange for hand-tightening
HEX_THICKNESS = 6

# Sealing groove and ring dimensions (TPU gasket)
SEAL_GROOVE_DIAMETER = 19.2
SEAL_GROOVE_WIDTH = 2
SEAL_GROOVE_DEPTH = 1.5
SEAL_RING_OUTER_DIAMETER = SEAL_GROOVE_DIAMETER + SEAL_GROOVE_WIDTH
SEAL_RING_INNER_DIAMETER = SEAL_GROOVE_DIAMETER
SEAL_RING_THICKNESS = SEAL_GROOVE_DEPTH + 0.5

# ============== BOX DRAIN COUPON (realistic section) ==============
# Create a minimal but realistic section of the box to test spout fit
# Scaled down to 60% to save filament while testing critical dimensions
COUPON_WIDTH = 48  # Y dimension (60% of 80mm)
COUPON_HEIGHT = 36  # Z dimension (60% of 60mm)
COUPON_DEPTH = 24   # X dimension (60% of 40mm)

# Drain positioning (matching actual box)
drain_center_x = -COUPON_DEPTH / 2  # On the left wall
drain_center_y = 0
drain_center_z = DRAIN_CENTER_HEIGHT

# Create outer box section
coupon_outer = (
    Workplane("XY")
    .box(COUPON_DEPTH, COUPON_WIDTH, COUPON_HEIGHT, centered=True)
    .translate((0, 0, COUPON_HEIGHT / 2))
)

# Hollow out interior (like real box)
interior_depth = COUPON_DEPTH - WALL_THICKNESS
interior_width = COUPON_WIDTH - 2 * WALL_THICKNESS
interior_height = COUPON_HEIGHT - WALL_THICKNESS  # Open top

coupon_interior = (
    Workplane("XY")
    .box(interior_depth, interior_width, interior_height, centered=True)
    .translate((WALL_THICKNESS / 2, 0, interior_height / 2 + WALL_THICKNESS))
)

coupon_hollowed = coupon_outer.cut(coupon_interior)

# Add bayonet boss protruding inward (like real box)
boss = (
    Workplane("YZ")
    .workplane(offset=drain_center_x + WALL_THICKNESS)
    .center(drain_center_y, drain_center_z)
    .circle(BOSS_OUTER_DIAMETER / 2)
    .extrude(BOSS_LENGTH)
)

coupon_with_boss = coupon_hollowed.union(boss)

# Cut shaft clearance hole through wall (tighter fit for friction retention)
clearance_hole = (
    Workplane("YZ")
    .workplane(offset=drain_center_x - 3)
    .center(drain_center_y, drain_center_z)
    .circle((THREAD_MAJOR_DIAMETER / 2) - 0.45)  # Tight fit for thread engagement (1.5mm smaller diameter)
    .extrude(3 + WALL_THICKNESS + BOSS_LENGTH + 3)  # All the way through
)

coupon_with_clearance = coupon_with_boss.cut(clearance_hole)

# Add simplified internal threads (fewer segments for fit test speed)
n_turns = int(THREAD_LENGTH / THREAD_PITCH)
segments_per_turn = 4  # Simplified for fit test

coupon_with_threads = coupon_with_clearance

for turn in range(n_turns):
    for seg in range(segments_per_turn):
        angle = (turn * segments_per_turn + seg) * (360.0 / segments_per_turn)
        z_pos = turn * THREAD_PITCH + (seg / float(segments_per_turn)) * THREAD_PITCH

        if z_pos < THREAD_LENGTH - THREAD_PITCH / 3:
            # Cut thread groove into boss interior
            groove = (
                Workplane("YZ")
                .workplane(offset=drain_center_x + WALL_THICKNESS + z_pos)
                .center(drain_center_y, drain_center_z)
                .transformed(rotate=(angle, 0, 0))
                .transformed(offset=(0, (THREAD_MAJOR_DIAMETER / 2) - 1.5, 0))
                .rect(THREAD_PITCH * 0.4, 1.0)
                .extrude(THREAD_PITCH * 0.35)
            )
            coupon_with_threads = coupon_with_threads.cut(groove)

coupon = coupon_with_threads

# Translate to sit on print bed and position at X=0
coupon_bbox_pre = coupon.val().BoundingBox()
coupon = coupon.translate((
    COUPON_DEPTH / 2,  # Move from centered (-DEPTH/2 to +DEPTH/2) to (0 to DEPTH)
    0,
    -coupon_bbox_pre.zmin  # Sit on print bed (Z=0)
))

# No section cut - keep full hole for complete spout fit testing

# ============== THREADED COMPRESSION SPOUT ==============
# Hex flange for hand-tightening
hex_flange = (
    Workplane("XY")
    .transformed(offset=(0, 0, -HEX_THICKNESS))
    .polygon(6, HEX_SIZE)
    .extrude(HEX_THICKNESS)
)

# Circular flange base
flange_base = (
    Workplane("XY")
    .transformed(offset=(0, 0, -FLANGE_THICKNESS))
    .circle(FLANGE_DIAMETER / 2)
    .extrude(FLANGE_THICKNESS)
)

flange = hex_flange.union(flange_base)

# Cut gasket groove into flange underside
gasket_groove = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SEAL_GROOVE_DEPTH))
    .circle((SEAL_GROOVE_DIAMETER + SEAL_GROOVE_WIDTH) / 2)
    .circle(SEAL_GROOVE_DIAMETER / 2)
    .extrude(SEAL_GROOVE_DEPTH)
)

flange = flange.cut(gasket_groove)

# Threaded shaft (simplified for fit test)
shaft = (
    Workplane("XY")
    .circle((THREAD_MAJOR_DIAMETER / 2) - 0.5)
    .extrude(THREAD_LENGTH_SPOUT)
)

# Add simplified external threads
n_turns_spout = int(THREAD_LENGTH_SPOUT / THREAD_PITCH)
segments_per_turn_spout = 4  # Simplified for fit test

for turn in range(n_turns_spout):
    for seg in range(segments_per_turn_spout):
        angle = (turn * segments_per_turn_spout + seg) * (360.0 / segments_per_turn_spout)
        z_pos = turn * THREAD_PITCH + (seg / float(segments_per_turn_spout)) * THREAD_PITCH

        if z_pos < THREAD_LENGTH_SPOUT - THREAD_PITCH / 3:
            ridge = (
                Workplane("XY")
                .transformed(offset=(0, 0, z_pos))
                .transformed(rotate=(0, 0, angle))
                .transformed(offset=((THREAD_MAJOR_DIAMETER / 2) - 0.8, 0, 0))
                .box(1.5, 0.8, THREAD_PITCH * 0.35, centered=True)
            )
            shaft = shaft.union(ridge)

# Spout tube extends backward from flange rear face
spout_tube = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS))
    .circle(SPOUT_OUTER_DIAMETER / 2)
    .extrude(SPOUT_LENGTH)
)

spout_body = flange.union(shaft).union(spout_tube)

# Bore goes from tube end through flange and shaft
through_bore = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS - 5))
    .circle(SPOUT_INNER_DIAMETER / 2)
    .extrude(SPOUT_LENGTH + FLANGE_THICKNESS + THREAD_LENGTH_SPOUT + 10)
)

spout = spout_body.cut(through_bore)

# ============== SPOUT CAP ==============
# Simple press-fit cap for spout end
CAP_OUTER_DIAMETER = SPOUT_OUTER_DIAMETER + 3  # Fits over spout end
CAP_WALL_THICKNESS = 1.5
CAP_HEIGHT = 8
CAP_CLEARANCE = 0.2

cap = (
    Workplane("XY")
    .circle(CAP_OUTER_DIAMETER / 2)
    .extrude(CAP_HEIGHT)
)

cap_bore = (
    Workplane("XY")
    .circle((SPOUT_OUTER_DIAMETER / 2) + CAP_CLEARANCE)
    .extrude(CAP_HEIGHT - CAP_WALL_THICKNESS)
)

cap = cap.cut(cap_bore)

# ============== LID SOCKET COUPON ==============
# Scaled down to 60% to save filament while testing socket fit
LID_COUPON_SIZE = 42  # 60% of 70mm
lid_total_thickness = LID_TOP_THICKNESS + RECESS_DEPTH

lid_coupon = (
    Workplane("XY")
    .box(LID_COUPON_SIZE, LID_COUPON_SIZE, lid_total_thickness, centered=True)
    .translate((0, 0, lid_total_thickness / 2))
)

recess_length = LID_COUPON_SIZE - 2 * WALL_THICKNESS - 2 * RECESS_CLEARANCE
recess_width = LID_COUPON_SIZE - 2 * WALL_THICKNESS - 2 * RECESS_CLEARANCE
lid_recess_center_z = -(LID_TOP_THICKNESS + RECESS_DEPTH) / 2 + RECESS_OVERLAP

lid_recess = (
    Workplane("XY")
    .box(recess_length, recess_width, RECESS_DEPTH, centered=True)
    .translate((0, 0, lid_total_thickness / 2 + lid_recess_center_z))
)

lid_solid = lid_coupon.val().fuse(lid_recess.val())
lid_coupon = Workplane(obj=lid_solid)

scraper_z_position = lid_total_thickness / 2 + lid_recess_center_z - RECESS_DEPTH / 2

# Create recessed bayonet socket carved directly into lid body (much stronger than hanging boss)
# Main circular socket cavity - extrude upward from recess bottom into lid body
scraper_socket_cut = (
    Workplane("XY")
    .circle(SCRAPER_SOCKET_DIAMETER / 2)
    .extrude(SCRAPER_SOCKET_DEPTH)
    .translate((0, 0, scraper_z_position))
)

# Create L-shaped bayonet slots (3 slots at 60°, 180°, 300° - offset from tab positions)
bayonet_slot_cuts = []

for i in range(BAYONET_TAB_COUNT):
    slot_angle = i * 120 + BAYONET_ROTATION_ANGLE  # 60°, 180°, 300°
    slot_angle_rad = math.radians(slot_angle)

    # Vertical entry slot (allows tab to slide in)
    slot_radius = SCRAPER_SHAFT_DIAMETER / 2 + BAYONET_TAB_PROTRUSION / 2
    slot_x = slot_radius * math.cos(slot_angle_rad)
    slot_y = slot_radius * math.sin(slot_angle_rad)

    # Vertical slot starts at recess bottom and goes up into the lid
    vertical_slot = (
        Workplane("XY")
        .transformed(offset=(slot_x, slot_y, scraper_z_position + BAYONET_SLOT_VERTICAL / 2))
        .transformed(rotate=(0, 0, slot_angle))
        .box(BAYONET_TAB_PROTRUSION + 0.2, BAYONET_SLOT_WIDTH, BAYONET_SLOT_VERTICAL, centered=True)
    )
    bayonet_slot_cuts.append(vertical_slot)

    # Horizontal lock slot (tab slides into this when rotated)
    # Position at top of vertical slot (deeper in the lid)
    horizontal_slot_z = scraper_z_position + BAYONET_SLOT_VERTICAL
    horizontal_angle = slot_angle - BAYONET_ROTATION_ANGLE

    # Create horizontal slot by cutting arc segments
    for angle_deg in range(int(horizontal_angle - 5), int(horizontal_angle + BAYONET_ROTATION_ANGLE + 5), 5):
        angle_rad = math.radians(angle_deg)
        cut_x = (SCRAPER_SHAFT_DIAMETER / 2 + BAYONET_TAB_PROTRUSION / 2) * math.cos(angle_rad)
        cut_y = (SCRAPER_SHAFT_DIAMETER / 2 + BAYONET_TAB_PROTRUSION / 2) * math.sin(angle_rad)

        cut_segment = (
            Workplane("XY")
            .transformed(offset=(cut_x, cut_y, horizontal_slot_z - BAYONET_LOCK_DEPTH / 2))
            .box(BAYONET_TAB_PROTRUSION + 0.4, BAYONET_SLOT_WIDTH, BAYONET_LOCK_DEPTH, centered=True)
        )
        bayonet_slot_cuts.append(cut_segment)

# Cut the bayonet socket directly into the lid body (recessed, not protruding)
# Cut main socket cavity
lid_with_socket = lid_coupon.cut(scraper_socket_cut)

# Cut all bayonet slots
for slot_cut in bayonet_slot_cuts:
    lid_with_socket = lid_with_socket.cut(slot_cut)

lid_coupon = lid_with_socket

# ============== SCRAPER (separate) - Pin-based design ==============
random.seed(42)

scraper_base = (
    Workplane("XY")
    .circle(SCRAPER_BASE_DIAMETER / 2)
    .extrude(-SCRAPER_BASE_HEIGHT)
)

# Add reinforcement cylinder at base of pins (solid infill for strength)
pin_reinforcement = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SCRAPER_BASE_HEIGHT))
    .circle(SCRAPER_BASE_DIAMETER / 2)
    .extrude(-PIN_REINFORCEMENT_HEIGHT)
)

scraper_base = scraper_base.union(pin_reinforcement)

min_radius = SCRAPER_BASE_DIAMETER / 6
max_radius = SCRAPER_BASE_DIAMETER / 2.5
scraper_with_pins = scraper_base

for i in range(PIN_COUNT):
    radius = random.uniform(min_radius, max_radius)
    base_angle = (i / PIN_COUNT) * 360
    angle_variation = random.uniform(-20, 20)
    angle = base_angle + angle_variation
    angle_rad = math.radians(angle)
    pin_x = radius * math.cos(angle_rad)
    pin_y = radius * math.sin(angle_rad)

    pin = (
        Workplane("XY")
        .center(pin_x, pin_y)
        .circle(PIN_DIAMETER / 2)
        .extrude(-PIN_LENGTH)
    )

    pin_tip = (
        Workplane("XY")
        .transformed(offset=(pin_x, pin_y, -PIN_LENGTH))
        .circle(PIN_DIAMETER / 2)
        .workplane(offset=-PIN_DIAMETER)
        .circle(0.5)
        .loft()
    )

    scraper_with_pins = scraper_with_pins.union(pin).union(pin_tip)

# Add attachment shaft with bayonet tabs
scraper_shaft = (
    Workplane("XY")
    .circle(SCRAPER_SHAFT_DIAMETER / 2)
    .extrude(SCRAPER_SHAFT_HEIGHT)
)

# Add bayonet tabs at correct height on shaft (3 tabs at 120° spacing)
# Tabs positioned to align with top of vertical slots and rotate into horizontal locks
for i in range(BAYONET_TAB_COUNT):
    tab_angle = i * 120  # 0°, 120°, 240°
    tab_angle_rad = math.radians(tab_angle)

    tab_radius = SCRAPER_SHAFT_DIAMETER / 2 + BAYONET_TAB_PROTRUSION / 2
    tab_x = tab_radius * math.cos(tab_angle_rad)
    tab_y = tab_radius * math.sin(tab_angle_rad)

    # Position tab at height to align with vertical slot top (where horizontal lock is)
    tab_z = BAYONET_SLOT_VERTICAL

    tab = (
        Workplane("XY")
        .transformed(offset=(tab_x, tab_y, tab_z))
        .transformed(rotate=(0, 0, tab_angle))
        .box(BAYONET_TAB_PROTRUSION, BAYONET_TAB_HEIGHT, BAYONET_TAB_LENGTH, centered=True)
    )

    scraper_shaft = scraper_shaft.union(tab)

scraper = scraper_with_pins.union(scraper_shaft)

# ============== TPU SEAL RING (gasket for spout flange) ==============
seal_ring = (
    Workplane("XY")
    .circle(SEAL_RING_OUTER_DIAMETER / 2)
    .circle(SEAL_RING_INNER_DIAMETER / 2)
    .extrude(SEAL_RING_THICKNESS)
)

# ============== ARRANGE ON BED ==============
# Position all parts to sit flat on Z=0 for 3D printing
# Optimize spacing to fit on 220mm bed while keeping parts separated
gap = 5  # Reduced gap to fit on standard print bed

# Coupon is already at X=0 from earlier positioning
coupon_bbox = coupon.val().BoundingBox()

# Position spout completely separate from coupon, aligned for visual comparison
# Spout should be positioned with shaft pointing toward the boss socket hole
# This allows visual verification of tab/slot alignment

# Rotate 90° around Y so shaft points in +X direction
spout = spout.rotate((0, 0, 0), (0, 1, 0), 90)

# Position spout to the LEFT of the coupon (in negative X), completely separate
# After rotation, the spout extends in +X direction (shaft forward)
# Place it at a negative X position so it's visually separate from coupon at X=0
# Moved 30mm closer to save space on print bed
gap_between = 15 - 30  # mm gap between spout flange and coupon front face (reduced by 30mm)
spout_x_position = -SPOUT_LENGTH - FLANGE_THICKNESS - gap_between

# Align spout vertically with the drain hole center
spout_y_position = 0  # Centered (same as drain hole)
spout_z_position = drain_center_z  # Match drain height

spout = spout.translate((spout_x_position, spout_y_position, spout_z_position))

# Lid coupon - translate up so lowest point (recess bottom) sits at Z=0
lid_bbox = lid_coupon.val().BoundingBox()
lid_z_offset = -lid_bbox.zmin  # Lift by the depth it extends below zero
# Position lid after coupon (spout is now positioned next to coupon, not after it)
lid_x_position = coupon_bbox.xmax + gap + LID_COUPON_SIZE / 2  # Position after coupon
lid_coupon = lid_coupon.translate((lid_x_position, 0, lid_z_offset))

# Scraper - flip upside down so triangular base sits on bed
# Original: base at 0, tip at -14.4, shaft at +10
# After flip: need to calculate new bbox and position
scraper_flipped = scraper.rotate((0, 0, 0), (1, 0, 0), 180)
scraper_flipped_bbox = scraper_flipped.val().BoundingBox()
lid_coupon_bbox = lid_coupon.val().BoundingBox()
scraper_x = lid_coupon_bbox.xmax + gap + 15  # Position after lid coupon with margin
scraper = scraper_flipped.translate((
    scraper_x,
    0,
    -scraper_flipped_bbox.zmin  # Move lowest point to Z=0
))

# TPU seal ring - position flat on bed next to scraper
# Position compactly to fit on 220mm bed
scraper_positioned_bbox = scraper.val().BoundingBox()
seal_ring_diameter = SEAL_RING_OUTER_DIAMETER
seal_ring_x = scraper_positioned_bbox.xmax + gap + seal_ring_diameter / 2  # Center position with gap
seal_ring = seal_ring.translate((seal_ring_x, 0, 0))

# Spout cap - position flat on bed next to seal ring
seal_ring_positioned_bbox = seal_ring.val().BoundingBox()
cap_x = seal_ring_positioned_bbox.xmax + gap + CAP_OUTER_DIAMETER / 2
cap = cap.translate((cap_x, 0, 0))

parts = [coupon.val(), spout.val(), lid_coupon.val(), scraper.val(), seal_ring.val(), cap.val()]
compound = cq.Compound.makeCompound(parts)

cq.exporters.export(compound, "../CAD/fit_test.step")
cq.exporters.export(compound, "../CAD/fit_test.stl", tolerance=0.1)

print("✓ fit_test.stl exported")
print("✓ fit_test.step exported")
print()
print("Fit Test Components (Threaded Compression Fitting):")
print("  1. Box drain coupon with internal threaded boss")
print("  2. Threaded spout with hex flange and gasket groove")
print("  3. Lid socket coupon with bayonet lock slots")
print("  4. Attachable scraper with bayonet tabs")
print("  5. TPU seal ring gasket (fits in flange groove)")
print("  6. Spout cap (press-fit closure)")
print()
print("Thread Spec: M16×3")
print("All parts positioned on X-axis for single-piece printing")
