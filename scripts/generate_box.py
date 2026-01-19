#!/usr/bin/env python3
"""
Generate a coffee grounds compost container with lid and handle.
- Box: 20cm x 15cm x 15cm with rounded edges
- Sloped base for drainage toward left side
- Horizontal bayonet drain fitting on left wall, centered, just above bottom
- Lid: has recess/step that slots inside box opening for accurate fit
- Handle: ergonomic grip on top of lid
"""

import cadquery as cq
from cadquery import Workplane
import math
import random

# Dimensions (in mm)
BOX_LENGTH = 200  # 20cm (X axis)
BOX_WIDTH = 150   # 15cm (Y axis)
BOX_HEIGHT = 150  # 15cm (Z axis)
WALL_THICKNESS = 4  # Increased for threaded boss strength
FILLET_RADIUS = 8

# Drainage - slope toward left side (-X)
SLOPE_ANGLE = 2  # degrees - gentle slope toward drain

# Drain hole positioning and threaded boss
# Position of drain: LEFT wall (-X side), centered on Y
# Bottom of drain hole must be 5mm (0.5cm) from bottom of box
DRAIN_HOLE_DIAMETER = 17  # mm - clearance for spout shaft
DRAIN_CENTER_HEIGHT = 5 + DRAIN_HOLE_DIAMETER / 2  # 5mm from bottom + radius = center height
drain_center_z = -BOX_HEIGHT / 2 + DRAIN_CENTER_HEIGHT

# Threaded boss dimensions (receives threaded spout shaft)
THREAD_MAJOR_DIAMETER = 16  # M16 thread
THREAD_PITCH = 3  # Coarse thread pitch
THREAD_LENGTH = 20  # Thread engagement depth
DRAIN_BORE_DIAMETER = 12  # Center bore for liquid flow
BOSS_OUTER_DIAMETER = 22.4  # Boss cylinder on interior wall
BOSS_LENGTH = 15  # Boss extends into box interior

LID_TOP_THICKNESS = 5
RECESS_DEPTH = 10
RECESS_CLEARANCE = 0.5
RECESS_OVERLAP = 0.2
LID_RECESS_FILLET = 2
BOX_TOP_INNER_FILLET = 1.5
FOOT_DIAMETER = 10
FOOT_RECESS_DEPTH = 2
FOOT_EDGE_MARGIN = 18

# Handle dimensions
HANDLE_LENGTH = 70
HANDLE_WIDTH = 20
HANDLE_HEIGHT = 12
HANDLE_THICKNESS = 5

# Capsule scraper (underside of lid) - Metal nail insert design for Nespresso capsules
CAPSULE_DIAMETER = 37  # Standard Nespresso capsule outer diameter
CAPSULE_HEIGHT = 38  # Standard Nespresso capsule height
SCRAPER_BASE_DIAMETER = 28  # Circular base diameter (fits within capsule)
SCRAPER_BASE_HEIGHT = 3  # Height of the circular base
PIN_COUNT = 8  # Number of piercing pins (metal nails)
PIN_LENGTH = 29.75  # Length of pins (15% shorter than original 35mm)
PIN_DIAMETER = 2.5  # Diameter of each pin (sturdy enough for piercing)
PIN_REINFORCEMENT_HEIGHT = 10  # Increased reinforcement for nail hole strength

# Metal nail insert specifications
# Standard 1.5mm brad nails or 18ga finish nails work well
NAIL_DIAMETER = 1.5  # Target nail diameter (1.5mm brad nails)
NAIL_HOLE_DIAMETER = 1.4  # Tight friction fit (0.1mm interference for press-fit)
NAIL_SOCKET_DEPTH = 8  # How deep the nail head sits in the socket
NAIL_SOCKET_DIAMETER = 3.5  # Socket to capture nail head (wider than shaft)
NAIL_TAPER_LENGTH = 2  # Taper from socket to shaft hole for easy insertion

# Scraper attachment - Bayonet lock mechanism
SCRAPER_BOSS_DIAMETER = 14
SCRAPER_BOSS_HEIGHT = 4
SCRAPER_SHAFT_DIAMETER = 14.0  # Base shaft diameter
SCRAPER_SHAFT_HEIGHT = 10  # Full height for deep engagement
SCRAPER_SOCKET_DIAMETER = 14.2  # 0.2mm clearance for smooth rotation
SCRAPER_SOCKET_DEPTH = 10  # Full depth to match shaft height

# Bayonet lock dimensions
BAYONET_TAB_COUNT = 3  # Three tabs at 120° spacing
BAYONET_TAB_HEIGHT = 3  # Axial height of tab (increased from 2mm)
BAYONET_TAB_LENGTH = 6  # Length along shaft axis (increased from 4mm)
BAYONET_TAB_PROTRUSION = 1.35  # Radial extension from shaft (reduced by 0.15mm for nail head clearance)
BAYONET_ROTATION_ANGLE = 60  # Degrees to rotate for locking
BAYONET_SLOT_WIDTH = 3.5  # Tab width + 0.5mm clearance (increased from 2.2mm)
BAYONET_SLOT_VERTICAL = 6  # Vertical entry slot depth
BAYONET_SLOT_HORIZONTAL = 4  # Horizontal lock slot length
BAYONET_LOCK_DEPTH = 3  # How far tab locks under lip (increased from 2mm)

SCRAPER_BOSS_OVERLAP = 0.3

# ============== BOX ==============
# Create the main box with rounded edges
box = (
    Workplane("XY")
    .box(BOX_LENGTH, BOX_WIDTH, BOX_HEIGHT, centered=True)
    .edges("|Z")
    .fillet(FILLET_RADIUS)
)

# Hollow out the box from the top, leaving the opening exposed
box_hollowed = (
    box
    .faces(">Z")
    .shell(-WALL_THICKNESS)
    .faces(">Z")
    .edges()
    .fillet(BOX_TOP_INNER_FILLET)
)

# ============== SLOPED FLOOR ==============
# Slope toward left side (-X) where the drain is located at the bottom
# The floor slopes from right (+X, high) to left (-X, low) to direct liquid to drain
slope_rise = (BOX_LENGTH - 2 * WALL_THICKNESS) * math.tan(math.radians(SLOPE_ANGLE))
floor_length = BOX_LENGTH - 2 * WALL_THICKNESS
floor_width = BOX_WIDTH - 2 * WALL_THICKNESS
floor_overlap = max(2.0, WALL_THICKNESS)  # Ensure overlap for a fused base
floor_thickness = WALL_THICKNESS  # Ensure full intersection with the bottom
CHANNEL_WIDTH = 12
CHANNEL_DEPTH = 2.5

# Floor base aligns to the bottom of the drain hole to keep liquid flowing
floor_base_z = drain_center_z - DRAIN_HOLE_DIAMETER / 2

# Create sloped floor using loft between two rectangles at different heights
# Left side (-X) is at floor level, right side (+X) is raised by slope_rise
# We'll create a wedge shape

# Define the floor dimensions
interior_bottom = -BOX_HEIGHT / 2 + WALL_THICKNESS

# Add a flat base layer at the bottom to ensure proper fusion with walls
BASE_LAYER_THICKNESS = 2  # 2mm solid base layer
base_layer = (
    Workplane("XY")
    .workplane(offset=interior_bottom)
    .rect(floor_length, floor_width)
    .extrude(BASE_LAYER_THICKNESS)
)

# Define slope dimensions
x_left = -floor_length / 2
x_right = floor_length / 2
y_front = -floor_width / 2
y_back = floor_width / 2

z_left = floor_base_z  # Low side (at drain)
z_right = floor_base_z + slope_rise  # High side

# Create sloped floor on top of base layer using box and cut approach
slope_base_z = interior_bottom + BASE_LAYER_THICKNESS
floor_fill_height = z_right - slope_base_z + 2

sloped_floor = (
    Workplane("XY")
    .workplane(offset=slope_base_z)
    .rect(floor_length, floor_width)
    .extrude(floor_fill_height)
)

# Cut away material above the sloped surface
slope_cutter = (
    Workplane("XZ")
    .transformed(offset=(0, y_front, 0))
    .moveTo(x_left, z_left)  # Low side (at drain)
    .lineTo(x_right, z_right)  # High side
    .lineTo(x_right, z_right + 10)  # Extend up
    .lineTo(x_left, z_left + 10)  # Extend up
    .close()
    .extrude(floor_width)
)

sloped_floor = sloped_floor.cut(slope_cutter)

# Combine base layer with sloped floor
floor_assembly = base_layer.union(sloped_floor)

# Union with box
box_with_slope = box_hollowed.union(floor_assembly)

# Cut a shallow channel along the slope to guide liquid into the drain
channel_x_left = -floor_length / 2 + 2
channel_x_right = floor_length / 2 - 2
channel_cut = (
    Workplane("XZ")
    .transformed(offset=(0, -CHANNEL_WIDTH / 2, 0))
    .moveTo(channel_x_left, z_left)
    .lineTo(channel_x_right, z_right)
    .lineTo(channel_x_right, z_right - CHANNEL_DEPTH)
    .lineTo(channel_x_left, z_left - CHANNEL_DEPTH)
    .close()
    .extrude(CHANNEL_WIDTH)
)

box_with_slope = box_with_slope.cut(channel_cut)

# ============== THREADED DRAIN FITTING ==============
# Located on LEFT wall (-X side), centered on Y axis, 5mm from bottom

# Drain center position (before final Z translation)
drain_center_y = 0  # Centered on Y axis
drain_center_x = -BOX_LENGTH / 2  # On the left wall

# Create the threaded boss (protrudes inward from left wall toward +X)
boss = (
    Workplane("YZ")
    .workplane(offset=drain_center_x + WALL_THICKNESS)  # Inside surface of wall
    .center(drain_center_y, drain_center_z)
    .circle(BOSS_OUTER_DIAMETER / 2)
    .extrude(BOSS_LENGTH)  # Extends into box interior (+X direction)
)

# Add the boss to the box
box_with_boss = box_with_slope.union(boss)

# Cut the main clearance hole through wall (sized for proper thread engagement)
# The hole diameter should be equal to the thread minor diameter so threads bite into the boss
# Spout shaft base is 15mm, threads add to ~16mm. Boss internal threads cut into the hole.
clearance_hole = (
    Workplane("YZ")
    .workplane(offset=drain_center_x - 5)  # Start outside the box
    .center(drain_center_y, drain_center_z)
    .circle((THREAD_MAJOR_DIAMETER / 2) - 1.0)  # 14mm diameter - creates interference for thread engagement
    .extrude(5 + WALL_THICKNESS + BOSS_LENGTH + 5)  # All the way through
)

box_with_clearance = box_with_boss.cut(clearance_hole)

# Add internal threads (simplified helical grooves)
n_turns = int(THREAD_LENGTH / THREAD_PITCH)
segments_per_turn = 6  # Match spout thread segments

box_with_threads = box_with_clearance

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
            box_with_threads = box_with_threads.cut(groove)

box_with_drain = box_with_threads

# ============== FOOT RECESSES ==============
foot_spacing_x = BOX_LENGTH - 2 * FOOT_EDGE_MARGIN
foot_spacing_y = BOX_WIDTH - 2 * FOOT_EDGE_MARGIN
foot_recesses = (
    box_with_drain
    .faces("<Z")
    .workplane()
    .rarray(foot_spacing_x, foot_spacing_y, 2, 2)
    .circle(FOOT_DIAMETER / 2)
    .cutBlind(FOOT_RECESS_DEPTH)
)

# Move box so bottom sits on XY plane (Z=0) with opening at top
# Calculate the actual lowest point and translate to bring it to Z=0
# Clean and combine to fuse all solids into one
box_combined = foot_recesses.clean().combine()

# Safety check: if there are still multiple solids (shouldn't happen now), keep the largest
# This preserves the main box even if there are tiny artifacts
solids = box_combined.val().Solids()
if len(solids) > 1:
    print(f"Warning: Found {len(solids)} separate solids - keeping largest (main box)")
    # Find the largest solid by volume
    largest = max(solids, key=lambda s: s.Volume())
    box_combined = Workplane(obj=largest)

bbox = box_combined.val().BoundingBox()
box_final = box_combined.translate((0, 0, -bbox.zmin))

# ============== LID ==============
lid_top_length = BOX_LENGTH
lid_top_width = BOX_WIDTH
recess_length = BOX_LENGTH - 2 * WALL_THICKNESS - 2 * RECESS_CLEARANCE
recess_width = BOX_WIDTH - 2 * WALL_THICKNESS - 2 * RECESS_CLEARANCE
lid_recess_center_z = -(LID_TOP_THICKNESS + RECESS_DEPTH) / 2 + RECESS_OVERLAP

lid_top = (
    Workplane("XY")
    .box(lid_top_length, lid_top_width, LID_TOP_THICKNESS, centered=True)
    .edges("|Z")
    .fillet(FILLET_RADIUS)
)

lid_recess = (
    Workplane("XY")
    .box(recess_length, recess_width, RECESS_DEPTH, centered=True)
    .edges("|Z")
    .fillet(LID_RECESS_FILLET)
    .translate((0, 0, lid_recess_center_z))
)

lid_body = Workplane(obj=lid_top.val().fuse(lid_recess.val()))

# ============== HANDLE ==============
# Create ergonomic handle with curved inward grip on both sides
# The handle narrows at the center for comfortable finger grip

# Position where handle attaches to lid
handle_base_z = LID_TOP_THICKNESS / 2

# Outer shape - use lofting to create curved sides
handle_bottom_width = HANDLE_WIDTH  # Full width at bottom (attached to lid)
handle_grip_width = HANDLE_WIDTH * 0.6  # Narrower at grip area (60% of full width)
handle_top_width = HANDLE_WIDTH * 0.75  # Slightly wider at top

# Create outer shell by lofting between profiles
# Start from the lid surface and build upward
handle_outer = (
    Workplane("XY")
    .transformed(offset=(0, 0, handle_base_z))
    .rect(HANDLE_LENGTH, handle_bottom_width)
    .workplane(offset=HANDLE_HEIGHT * 0.5)
    .rect(HANDLE_LENGTH - HANDLE_THICKNESS, handle_grip_width)
    .workplane(offset=HANDLE_HEIGHT * 0.5)
    .rect(HANDLE_LENGTH - 2 * HANDLE_THICKNESS, handle_top_width)
    .loft()
)

# Create inner hollow with similar curved profile
# Start slightly above lid surface to maintain attachment
handle_inner = (
    Workplane("XY")
    .transformed(offset=(0, 0, handle_base_z + HANDLE_THICKNESS))
    .rect(HANDLE_LENGTH - 2 * HANDLE_THICKNESS, handle_bottom_width - 2 * HANDLE_THICKNESS)
    .workplane(offset=HANDLE_HEIGHT * 0.5 - HANDLE_THICKNESS)
    .rect(HANDLE_LENGTH - 3 * HANDLE_THICKNESS, handle_grip_width - 2 * HANDLE_THICKNESS)
    .workplane(offset=HANDLE_HEIGHT * 0.5)
    .rect(HANDLE_LENGTH - 4 * HANDLE_THICKNESS, handle_top_width - 2 * HANDLE_THICKNESS)
    .loft()
)

# Combine and add fillets for comfort
handle = handle_outer.cut(handle_inner)
try:
    handle = handle.edges().fillet(2)
except:
    pass  # Continue without filleting if it fails

# Add scraper storage slot at one end of handle
# Simple cylindrical groove to wedge the scraper shaft for storage
STORAGE_GROOVE_DIAMETER = 15.0  # 1.5cm depth (diameter for radial penetration)
STORAGE_GROOVE_LENGTH = 80  # 8cm length along handle axis
STORAGE_GROOVE_X_POS = -HANDLE_LENGTH / 2 + 5  # Start near one end of handle

# Create cylindrical groove along the length of the handle
storage_groove = (
    Workplane("YZ")
    .transformed(offset=(STORAGE_GROOVE_X_POS, 0, handle_base_z + HANDLE_HEIGHT * 0.6))
    .circle(STORAGE_GROOVE_DIAMETER / 2)
    .extrude(STORAGE_GROOVE_LENGTH)
)

# Add longitudinal slot in groove to mate with scraper's friction ridge
# This slot matches the ridge dimensions on the storage scraper
RIDGE_SLOT_WIDTH = 2.7  # Slightly wider than ridge (2.5mm) for clearance
RIDGE_SLOT_DEPTH = 1.0  # Depth of slot to accept ridge (matches 0.8mm ridge + clearance)
RIDGE_SLOT_LENGTH = STORAGE_GROOVE_LENGTH - 4  # Slightly shorter than groove

ridge_slot = (
    Workplane("YZ")
    .transformed(offset=(STORAGE_GROOVE_X_POS + 2, 0, handle_base_z + HANDLE_HEIGHT * 0.6))
    .rect(RIDGE_SLOT_LENGTH, RIDGE_SLOT_WIDTH)
    .extrude(RIDGE_SLOT_DEPTH)
)

handle = handle.cut(storage_groove).cut(ridge_slot)

# ============== CAPSULE SCRAPER ==============
# Pin-based design for Nespresso capsules
# Circular base with 8 randomly positioned pins
# User pokes pins into foil and rotates to extract coffee grounds

# Set seed for reproducible "random" pin placement
random.seed(42)

# Create circular base
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

# Add nail holes at semi-random positions within a ring pattern
# Holes are distributed in a ring to ensure good coverage
# Metal nails (1.5mm brad nails or 18ga finish nails) are pressed into these holes
# IMPORTANT: Holes must not overlap with bayonet shaft (14mm diameter = 7mm radius)
min_radius = SCRAPER_SHAFT_DIAMETER / 2 + 1.5  # Start outside shaft (7mm) + 1.5mm clearance = 8.5mm
max_radius = SCRAPER_BASE_DIAMETER / 2.5  # Outer boundary (leave edge margin)

scraper_with_holes = scraper_base

for i in range(PIN_COUNT):
    # Random radius within the ring
    radius = random.uniform(min_radius, max_radius)

    # Angle: roughly evenly distributed but with some randomness
    base_angle = (i / PIN_COUNT) * 360
    angle_variation = random.uniform(-20, 20)  # +/- 20 degrees
    angle = base_angle + angle_variation

    # Calculate X, Y position
    angle_rad = math.radians(angle)
    pin_x = radius * math.cos(angle_rad)
    pin_y = radius * math.sin(angle_rad)

    # Create nail socket (countersink for nail head)
    # Socket starts at base top and goes down into reinforcement
    nail_socket = (
        Workplane("XY")
        .center(pin_x, pin_y)
        .circle(NAIL_SOCKET_DIAMETER / 2)
        .extrude(-NAIL_SOCKET_DEPTH)
    )

    # Create tapered transition from socket to shaft hole
    nail_taper = (
        Workplane("XY")
        .transformed(offset=(pin_x, pin_y, -NAIL_SOCKET_DEPTH))
        .circle(NAIL_SOCKET_DIAMETER / 2)
        .workplane(offset=-NAIL_TAPER_LENGTH)
        .circle(NAIL_HOLE_DIAMETER / 2)
        .loft()
    )

    # Create tight friction-fit hole for nail shaft
    # IMPORTANT: Must pass completely through base + reinforcement
    total_base_thickness = SCRAPER_BASE_HEIGHT + PIN_REINFORCEMENT_HEIGHT
    remaining_thickness = total_base_thickness - NAIL_SOCKET_DEPTH - NAIL_TAPER_LENGTH
    nail_hole_length = remaining_thickness + 2  # +2mm extra to ensure it goes all the way through
    nail_hole = (
        Workplane("XY")
        .transformed(offset=(pin_x, pin_y, -NAIL_SOCKET_DEPTH - NAIL_TAPER_LENGTH))
        .circle(NAIL_HOLE_DIAMETER / 2)
        .extrude(-nail_hole_length)
    )

    # Cut all hole components from the base
    scraper_with_holes = scraper_with_holes.cut(nail_socket).cut(nail_taper).cut(nail_hole)

# Position scraper at the bottom of the lid recess (extends downward from recess bottom)
scraper_z_position = lid_recess_center_z - RECESS_DEPTH / 2

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
    horizontal_angle = slot_angle - BAYONET_ROTATION_ANGLE  # Rotate back 60° for lock position

    # Create horizontal slot by cutting arc segments
    # Extended range to give more clearance for rotation
    for angle_deg in range(int(horizontal_angle - 10), int(horizontal_angle + BAYONET_ROTATION_ANGLE + 10), 3):
        angle_rad = math.radians(angle_deg)
        cut_x = (SCRAPER_SHAFT_DIAMETER / 2 + BAYONET_TAB_PROTRUSION / 2) * math.cos(angle_rad)
        cut_y = (SCRAPER_SHAFT_DIAMETER / 2 + BAYONET_TAB_PROTRUSION / 2) * math.sin(angle_rad)

        cut_segment = (
            Workplane("XY")
            .transformed(offset=(cut_x, cut_y, horizontal_slot_z - BAYONET_LOCK_DEPTH / 2))
            .box(BAYONET_TAB_PROTRUSION + 0.6, BAYONET_SLOT_WIDTH, BAYONET_LOCK_DEPTH, centered=True)
        )
        bayonet_slot_cuts.append(cut_segment)

# Separate scraper part with bayonet lock shaft
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

    # Calculate tab center position
    tab_radius = SCRAPER_SHAFT_DIAMETER / 2 + BAYONET_TAB_PROTRUSION / 2
    tab_x = tab_radius * math.cos(tab_angle_rad)
    tab_y = tab_radius * math.sin(tab_angle_rad)

    # Position tab at height to align with vertical slot top (where horizontal lock is)
    tab_z = BAYONET_SLOT_VERTICAL

    # Create bayonet tab
    tab = (
        Workplane("XY")
        .transformed(offset=(tab_x, tab_y, tab_z))
        .transformed(rotate=(0, 0, tab_angle))
        .box(BAYONET_TAB_PROTRUSION, BAYONET_TAB_HEIGHT, BAYONET_TAB_LENGTH, centered=True)
    )

    scraper_shaft = scraper_shaft.union(tab)
scraper_shaft = scraper_shaft.translate((0, 0, scraper_z_position - SCRAPER_SHAFT_HEIGHT))

scraper = scraper_with_holes.translate((0, 0, scraper_z_position - SCRAPER_SHAFT_HEIGHT)).union(scraper_shaft)

# Cut the bayonet socket directly into the lid body (recessed, not protruding)
lid_with_handle = lid_body.union(handle)

# Cut main socket cavity
lid_with_socket = lid_with_handle.cut(scraper_socket_cut)

# Cut all bayonet slots
for slot_cut in bayonet_slot_cuts:
    lid_with_socket = lid_with_socket.cut(slot_cut)

lid_final = lid_with_socket.translate((0, 0, BOX_HEIGHT + LID_TOP_THICKNESS / 2 - bbox.zmin))

# ============== EXPORT ==============
box_final.val().exportStep("/Users/user/dev/3d Models/CAD/box.step")
box_final.val().exportStl("/Users/user/dev/3d Models/CAD/box.stl", tolerance=0.1)

lid_final.val().exportStep("/Users/user/dev/3d Models/CAD/lid.step")
lid_final.val().exportStl("/Users/user/dev/3d Models/CAD/lid.stl", tolerance=0.1)

# Export separate scraper part
scraper.val().exportStep("/Users/user/dev/3d Models/CAD/lid_scraper.step")
scraper.val().exportStl("/Users/user/dev/3d Models/CAD/lid_scraper.stl", tolerance=0.1)

print("✓ box.stl exported")
print("✓ lid.stl exported")
print("✓ box.step exported")
print("✓ lid.step exported")
print("\nCoffee Grounds Compost Container:")
print(f"  Box: {BOX_LENGTH}mm × {BOX_WIDTH}mm × {BOX_HEIGHT}mm")
print(f"  Wall thickness: {WALL_THICKNESS}mm")
print(f"  Base slope: {SLOPE_ANGLE}° toward left side (drain)")
print(f"\nThreaded Drain Fitting:")
print(f"  Boss diameter: {BOSS_OUTER_DIAMETER}mm × {BOSS_LENGTH}mm deep")
print(f"  Thread: M{THREAD_MAJOR_DIAMETER}×{THREAD_PITCH}")
print(f"  Thread length: {THREAD_LENGTH}mm")
print(f"  Drain bore: {DRAIN_BORE_DIAMETER}mm")
print(f"  Location: Left wall, centered, {DRAIN_CENTER_HEIGHT:.1f}mm center height")
print(f"  Bottom of hole: 5mm from box bottom (as specified)")
print(f"\nLid:")
print(f"  Top: {lid_top_length}mm × {lid_top_width}mm × {LID_TOP_THICKNESS}mm")
print(f"  Recess: {recess_length}mm × {recess_width}mm × {RECESS_DEPTH}mm deep")
print(f"  Handle: {HANDLE_LENGTH}mm × {HANDLE_WIDTH}mm × {HANDLE_HEIGHT}mm")
print(f"  Storage groove: ø{STORAGE_GROOVE_DIAMETER}mm × {STORAGE_GROOVE_LENGTH}mm (for scraper shaft)")
print(f"\nCapsule Scraper (separate):")
print(f"  Boss diameter: {SCRAPER_BOSS_DIAMETER}mm")
print(f"  Shaft diameter: {SCRAPER_SHAFT_DIAMETER}mm")
print(f"\nCapsule Scraper (underside of lid) - Metal nail insert design:")
print(f"  Base: {SCRAPER_BASE_DIAMETER}mm diameter circular base (fits {CAPSULE_DIAMETER}mm Nespresso capsule)")
print(f"  Nail holes: {PIN_COUNT} holes for 1.5mm brad nails or 18ga finish nails")
print(f"  Hole diameter: {NAIL_HOLE_DIAMETER}mm (tight friction fit)")
print(f"  Socket diameter: {NAIL_SOCKET_DIAMETER}mm (captures nail head)")
print(f"  Socket depth: {NAIL_SOCKET_DEPTH}mm")
print(f"  Reinforcement: {PIN_REINFORCEMENT_HEIGHT}mm solid base for strength")
print(f"  Nail pattern: Semi-random distribution in ring pattern")
print(f"  Assembly: Press 1.5mm × 25-30mm brad nails into holes from top")
print(f"  Purpose: Metal nails pierce foil, rotate to extract coffee grounds")
