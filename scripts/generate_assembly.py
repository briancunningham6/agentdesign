#!/usr/bin/env python3
"""
Generate a complete assembly view of the coffee grounds container with all parts.
Shows box, lid, scraper, and drain spout in their assembled positions.
"""

import cadquery as cq
from cadquery import Workplane
import math
import random

# ============== SHARED DIMENSIONS (match main scripts) ==============
# Box dimensions
BOX_LENGTH = 200
BOX_WIDTH = 150
BOX_HEIGHT = 150
WALL_THICKNESS = 4
FILLET_RADIUS = 8
SLOPE_ANGLE = 4  # Increased for positive drainage

# Threaded drain fitting
THREAD_MAJOR_DIAMETER = 16  # M16 thread
THREAD_PITCH = 3
THREAD_LENGTH = 20  # Box side thread length
THREAD_LENGTH_SPOUT = 18  # Spout side (slightly less for gasket compression)
DRAIN_HOLE_DIAMETER = 17
BOSS_OUTER_DIAMETER = 22.4
BOSS_LENGTH = 15
DRAIN_CENTER_HEIGHT = 5 + DRAIN_HOLE_DIAMETER / 2  # 5mm from bottom + radius

# Lid dimensions
LID_TOP_THICKNESS = 5
RECESS_DEPTH = 10
RECESS_CLEARANCE = 0.5
LID_RECESS_FILLET = 2
BOX_TOP_INNER_FILLET = 1.5

# Handle dimensions
HANDLE_LENGTH = 70
HANDLE_WIDTH = 20
HANDLE_HEIGHT = 18
HANDLE_THICKNESS = 5

# Scraper dimensions - Pin-based design
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

# Spout dimensions (threaded compression fitting)
SPOUT_OUTER_DIAMETER = 11.2
SPOUT_INNER_DIAMETER = 8
SPOUT_LENGTH = 60  # 6cm extension
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

# Spout position (default: left)
SPOUT_POSITION = "left"

# ============== BOX ==============
drain_center_z = -BOX_HEIGHT / 2 + DRAIN_CENTER_HEIGHT

box = (
    Workplane("XY")
    .box(BOX_LENGTH, BOX_WIDTH, BOX_HEIGHT, centered=True)
    .edges("|Z")
    .fillet(FILLET_RADIUS)
)

box_hollowed = (
    box
    .faces(">Z")
    .shell(-WALL_THICKNESS)
    .faces(">Z")
    .edges()
    .fillet(BOX_TOP_INNER_FILLET)
)

# Sloped floor
floor_length = BOX_LENGTH - 2 * WALL_THICKNESS
floor_width = BOX_WIDTH - 2 * WALL_THICKNESS
floor_base_z = drain_center_z - DRAIN_HOLE_DIAMETER / 2
floor_bottom_z = -BOX_HEIGHT / 2 + WALL_THICKNESS

# Small overlap to fuse with walls
x_left = -floor_length / 2 - 0.5
x_right = floor_length / 2 + 0.5
y_front = -floor_width / 2 - 0.5
y_back = floor_width / 2 + 0.5

if SPOUT_POSITION == "left":
    slope_rise = (BOX_LENGTH - 2 * WALL_THICKNESS) * math.tan(math.radians(SLOPE_ANGLE))
    z_left = floor_base_z
    z_right = floor_base_z + slope_rise
    sloped_floor = (
        Workplane("XZ")
        .transformed(offset=(0, -floor_width / 2, 0))
        .moveTo(x_left, floor_bottom_z)
        .lineTo(x_right, floor_bottom_z)
        .lineTo(x_right, z_right)
        .lineTo(x_left, z_left)
        .close()
        .extrude(floor_width)
    )
    drain_center_x = -BOX_LENGTH / 2
    drain_center_y = 0
elif SPOUT_POSITION == "right":
    slope_rise = (BOX_LENGTH - 2 * WALL_THICKNESS) * math.tan(math.radians(SLOPE_ANGLE))
    z_left = floor_base_z + slope_rise
    z_right = floor_base_z
    sloped_floor = (
        Workplane("XZ")
        .transformed(offset=(0, -floor_width / 2, 0))
        .moveTo(x_left, floor_bottom_z)
        .lineTo(x_right, floor_bottom_z)
        .lineTo(x_right, z_right)
        .lineTo(x_left, z_left)
        .close()
        .extrude(floor_width)
    )
    drain_center_x = BOX_LENGTH / 2
    drain_center_y = 0
else:  # rear
    slope_rise = (BOX_WIDTH - 2 * WALL_THICKNESS) * math.tan(math.radians(SLOPE_ANGLE))
    z_front = floor_base_z + slope_rise
    z_rear = floor_base_z
    sloped_floor = (
        Workplane("YZ")
        .transformed(offset=(-floor_length / 2, 0, 0))
        .moveTo(y_front, floor_bottom_z)
        .lineTo(y_back, floor_bottom_z)
        .lineTo(y_back, z_rear)
        .lineTo(y_front, z_front)
        .close()
        .extrude(floor_length)
    )
    drain_center_x = 0
    drain_center_y = -BOX_WIDTH / 2

box_with_slope = box_hollowed.union(sloped_floor)

# Threaded drain fitting (simplified - no actual threads in assembly for rendering speed)
if SPOUT_POSITION in ["left", "right"]:
    workplane_offset = drain_center_x + WALL_THICKNESS if SPOUT_POSITION == "left" else drain_center_x - WALL_THICKNESS
    boss_length = BOSS_LENGTH if SPOUT_POSITION == "left" else -BOSS_LENGTH

    boss = (
        Workplane("YZ")
        .workplane(offset=workplane_offset)
        .center(drain_center_y, drain_center_z)
        .circle(BOSS_OUTER_DIAMETER / 2)
        .extrude(boss_length)
    )

    hole_offset = drain_center_x - 5 if SPOUT_POSITION == "left" else drain_center_x + 5
    hole_extrude = BOSS_LENGTH + WALL_THICKNESS + 10 if SPOUT_POSITION == "left" else -(BOSS_LENGTH + WALL_THICKNESS + 10)

    # Clearance hole (tighter fit for friction retention)
    drain_hole = (
        Workplane("YZ")
        .workplane(offset=hole_offset)
        .center(drain_center_y, drain_center_z)
        .circle((THREAD_MAJOR_DIAMETER / 2) - 0.45)  # Tight fit for thread engagement (1.5mm smaller diameter)
        .extrude(hole_extrude)
    )
else:
    boss = (
        Workplane("XZ")
        .workplane(offset=drain_center_y + WALL_THICKNESS)
        .center(drain_center_x, drain_center_z)
        .circle(BOSS_OUTER_DIAMETER / 2)
        .extrude(BOSS_LENGTH)
    )

    drain_hole = (
        Workplane("XZ")
        .workplane(offset=drain_center_y - 5)
        .center(drain_center_x, drain_center_z)
        .circle((THREAD_MAJOR_DIAMETER / 2) - 0.45)  # Tight fit for thread engagement (1.5mm smaller diameter)
        .extrude(BOSS_LENGTH + WALL_THICKNESS + 10)
    )

box_with_drain = box_with_slope.union(boss).cut(drain_hole)

# Filter out any disconnected solids (like the floor wedge if it didn't fuse)
# Keep only the largest solid which is the main box
solids = box_with_drain.val().Solids()
if len(solids) > 1:
    # Find the largest solid by volume
    largest = max(solids, key=lambda s: s.Volume())
    box_with_drain = Workplane(obj=largest)

# Calculate actual lowest point and translate to Z=0
bbox_box = box_with_drain.val().BoundingBox()
box_final = box_with_drain.translate((0, 0, -bbox_box.zmin))

# ============== LID ==============
lid_top = (
    Workplane("XY")
    .box(BOX_LENGTH, BOX_WIDTH, LID_TOP_THICKNESS, centered=True)
    .edges("|Z")
    .fillet(FILLET_RADIUS)
)

recess_length = BOX_LENGTH - 2 * WALL_THICKNESS - 2 * RECESS_CLEARANCE
recess_width = BOX_WIDTH - 2 * WALL_THICKNESS - 2 * RECESS_CLEARANCE

lid_recess = (
    Workplane("XY")
    .box(recess_length, recess_width, RECESS_DEPTH, centered=True)
    .edges("|Z")
    .fillet(LID_RECESS_FILLET)
    .translate((0, 0, -(LID_TOP_THICKNESS + RECESS_DEPTH) / 2))
)

lid_body = lid_top.union(lid_recess)

# Handle
handle_base_z = LID_TOP_THICKNESS / 2
handle_bottom_width = HANDLE_WIDTH
handle_grip_width = HANDLE_WIDTH * 0.6
handle_top_width = HANDLE_WIDTH * 0.75

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

handle = handle_outer.cut(handle_inner)

# Integrated scraper on lid underside - Pin-based design
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

scraper_z_position = -(LID_TOP_THICKNESS / 2 + RECESS_DEPTH)
scraper_integrated = scraper_with_pins.translate((0, 0, scraper_z_position))

lid_with_handle = lid_body.union(handle).union(scraper_integrated)
lid_final = lid_with_handle.translate((0, 0, BOX_HEIGHT + LID_TOP_THICKNESS / 2 - bbox_box.zmin))

# ============== ATTACHABLE SCRAPER ==============
# Use same pin design as integrated scraper
random.seed(42)  # Same seed for consistent design

scraper_attachable_base = (
    Workplane("XY")
    .circle(SCRAPER_BASE_DIAMETER / 2)
    .extrude(-SCRAPER_BASE_HEIGHT)
)

scraper_attachable_pins = scraper_attachable_base

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

    scraper_attachable_pins = scraper_attachable_pins.union(pin).union(pin_tip)

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

scraper_attachable = scraper_attachable_pins.union(scraper_shaft)

# Position attachable scraper next to box (not assembled into lid)
# Position with shaft at top, scraper tip at Z=0
SCRAPER_TOTAL_HEIGHT = PIN_LENGTH + SCRAPER_BASE_HEIGHT
scraper_attachable_positioned = scraper_attachable.translate((BOX_LENGTH / 2 + 50, 0, SCRAPER_TOTAL_HEIGHT + SCRAPER_SHAFT_HEIGHT))

# ============== THREADED COMPRESSION SPOUT ==============
# Coordinate system: Z=0 is where flange contacts wall
# Shaft extends forward (positive Z) into boss
# Tube extends backward (negative Z) away from wall

# Hex flange for hand tightening
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

# Threaded shaft (simplified - no threads for assembly rendering speed)
shaft = (
    Workplane("XY")
    .circle((THREAD_MAJOR_DIAMETER / 2) - 0.5)
    .extrude(THREAD_LENGTH_SPOUT)
)

# Spout tube extends backward from flange rear face
spout_tube = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS))
    .circle(SPOUT_OUTER_DIAMETER / 2)
    .extrude(SPOUT_LENGTH)
)

# Combine spout parts
spout_body = flange.union(shaft).union(spout_tube)

# Cut through bore
through_bore = (
    Workplane("XY")
    .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS - 5))
    .circle(SPOUT_INNER_DIAMETER / 2)
    .extrude(SPOUT_LENGTH + FLANGE_THICKNESS + THREAD_LENGTH_SPOUT + 10)
)

spout = spout_body.cut(through_bore)

# ============== SEAL RING (TPU gasket) ==============
# Ring sits in groove on flange underside, compressed against box wall
seal_ring = (
    Workplane("XY")
    .circle(SEAL_RING_OUTER_DIAMETER / 2)
    .circle(SEAL_RING_INNER_DIAMETER / 2)
    .extrude(SEAL_RING_THICKNESS)
)

# Position spout at drain location (account for box translation)
# Shaft start (Z=0) should align with wall exterior surface
if SPOUT_POSITION == "left":
    spout_positioned = (
        spout
        .rotate((0, 0, 0), (0, 1, 0), 90)
        .translate((drain_center_x, drain_center_y, -bbox_box.zmin + drain_center_z))
    )
elif SPOUT_POSITION == "right":
    spout_positioned = (
        spout
        .rotate((0, 0, 0), (0, 1, 0), -90)
        .translate((drain_center_x, drain_center_y, -bbox_box.zmin + drain_center_z))
    )
else:  # rear
    spout_positioned = (
        spout
        .rotate((0, 0, 0), (1, 0, 0), 90)
        .translate((drain_center_x, drain_center_y, -bbox_box.zmin + drain_center_z))
    )

# Position seal ring at wall exterior surface (sits in flange groove)
if SPOUT_POSITION == "left":
    seal_ring_positioned = (
        seal_ring
        .rotate((0, 0, 0), (0, 1, 0), 90)
        .translate((drain_center_x, drain_center_y, -bbox_box.zmin + drain_center_z))
    )
elif SPOUT_POSITION == "right":
    seal_ring_positioned = (
        seal_ring
        .rotate((0, 0, 0), (0, 1, 0), -90)
        .translate((drain_center_x, drain_center_y, -bbox_box.zmin + drain_center_z))
    )
else:  # rear
    seal_ring_positioned = (
        seal_ring
        .rotate((0, 0, 0), (1, 0, 0), 90)
        .translate((drain_center_x, drain_center_y, -bbox_box.zmin + drain_center_z))
    )

# ============== ASSEMBLE ALL PARTS ==============
# Assembly includes all components in their installed positions
parts = [
    box_final.val(),
    lid_final.val(),
    spout_positioned.val(),
    seal_ring_positioned.val()
]

compound = cq.Compound.makeCompound(parts)

# Export
cq.exporters.export(compound, "../CAD/assembly.step")
cq.exporters.export(compound, "../CAD/assembly.stl", tolerance=0.1)

print("✓ assembly.stl exported")
print("✓ assembly.step exported")
print()
print("Assembly Contents (upright orientation):")
print("  - Box with threaded drain boss (M16×3)")
print("  - Lid with integrated scraper and handle")
print("  - Threaded compression spout (6cm extension)")
print("  - TPU seal ring (sits in flange groove)")
print()
print("Design: Hand-tightenable threaded compression fitting")
print("Orientation: Box upright with opening at top, lid on top")
