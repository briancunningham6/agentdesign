#!/usr/bin/env python3
"""
Generate assembly animation frames for the coffee grounds compost container.
Shows the sequential assembly of:
1. Box (base)
2. Spout + seal ring being installed
3. Lid being placed
4. Scraper being attached to lid

Exports multiple STEP files representing different stages of assembly.
"""

import cadquery as cq
from cadquery import Workplane
import math
import random

# Import dimensions from main files
BOX_LENGTH = 200
BOX_WIDTH = 150
BOX_HEIGHT = 150
WALL_THICKNESS = 4
SLOPE_ANGLE = 4  # Increased for positive drainage

# Thread dimensions - MUST MATCH generate_box.py
THREAD_MAJOR_DIAMETER = 16
THREAD_PITCH = 3
THREAD_LENGTH = 20
DRAIN_BORE_DIAMETER = 12
BOSS_OUTER_DIAMETER = 22.4
BOSS_LENGTH = 15

# Drain position
DRAIN_HOLE_DIAMETER = 17
DRAIN_CENTER_HEIGHT = 5 + DRAIN_HOLE_DIAMETER / 2
drain_center_x = -BOX_LENGTH / 2
drain_center_y = 0
drain_center_z = -BOX_HEIGHT / 2 + DRAIN_CENTER_HEIGHT

# Spout dimensions - MUST MATCH generate_drain_spout.py
SPOUT_OUTER_DIAMETER = 11.2
SPOUT_LENGTH = 60
FLANGE_DIAMETER = 24
FLANGE_THICKNESS = 4
THREAD_LENGTH_SPOUT = 18  # Thread engagement (slightly less than box for gasket compression)
HEX_SIZE = 20.8
HEX_THICKNESS = 6
SEAL_GROOVE_DIAMETER = 19.2
SEAL_GROOVE_WIDTH = 2
SEAL_GROOVE_DEPTH = 1.5
SEAL_RING_THICKNESS = SEAL_GROOVE_DEPTH + 0.5

# Lid dimensions
LID_TOP_THICKNESS = 5
RECESS_DEPTH = 10
RECESS_CLEARANCE = 0.5
HANDLE_LENGTH = 70
HANDLE_WIDTH = 20
HANDLE_HEIGHT = 18

# Scraper dimensions
SCRAPER_BASE_DIAMETER = 28
SCRAPER_BASE_HEIGHT = 3
PIN_COUNT = 8
PIN_LENGTH = 29.75
PIN_DIAMETER = 2.5
PIN_REINFORCEMENT_HEIGHT = 4
SCRAPER_SHAFT_DIAMETER = 14.0
SCRAPER_SHAFT_HEIGHT = 10

# Bayonet dimensions
BAYONET_TAB_COUNT = 3
BAYONET_TAB_HEIGHT = 2
BAYONET_TAB_LENGTH = 4
BAYONET_TAB_PROTRUSION = 1
BAYONET_SLOT_VERTICAL = 6

print("Generating assembly animation frames...")
print("=" * 70)

# Helper function to create simplified box
def create_simplified_box():
    """Create a simplified box (no internal details for faster rendering)"""
    box_outer = (
        Workplane("XY")
        .box(BOX_LENGTH, BOX_WIDTH, BOX_HEIGHT, centered=True)
        .translate((0, 0, BOX_HEIGHT / 2))
        .edges("|Z")
        .fillet(8)
    )

    box_interior = (
        Workplane("XY")
        .box(
            BOX_LENGTH - 2 * WALL_THICKNESS,
            BOX_WIDTH - 2 * WALL_THICKNESS,
            BOX_HEIGHT - WALL_THICKNESS,
            centered=True
        )
        .translate((0, 0, (BOX_HEIGHT - WALL_THICKNESS) / 2 + WALL_THICKNESS))
    )

    box = box_outer.cut(box_interior)

    # Add boss
    boss = (
        Workplane("YZ")
        .workplane(offset=drain_center_x + WALL_THICKNESS)
        .center(drain_center_y, drain_center_z)
        .circle(BOSS_OUTER_DIAMETER / 2)
        .extrude(BOSS_LENGTH)
    )

    box = box.union(boss)

    # Add drain clearance hole (tighter fit for friction retention)
    drain_hole = (
        Workplane("YZ")
        .workplane(offset=drain_center_x - 5)
        .center(drain_center_y, drain_center_z)
        .circle((THREAD_MAJOR_DIAMETER / 2) - 0.45)  # Tight fit for thread engagement (1.5mm smaller diameter)
        .extrude(5 + WALL_THICKNESS + BOSS_LENGTH + 5)
    )

    box = box.cut(drain_hole)

    return box

# Helper function to create simplified spout
def create_simplified_spout():
    """Create simplified threaded spout with gasket groove"""
    # Hex flange
    hex_flange = (
        Workplane("XY")
        .transformed(offset=(0, 0, -HEX_THICKNESS))
        .polygon(6, HEX_SIZE)
        .extrude(HEX_THICKNESS)
    )

    # Circular flange
    flange_base = (
        Workplane("XY")
        .transformed(offset=(0, 0, -FLANGE_THICKNESS))
        .circle(FLANGE_DIAMETER / 2)
        .extrude(FLANGE_THICKNESS)
    )

    # Combine flanges
    flange = hex_flange.union(flange_base)

    # Cut gasket groove in flange underside
    gasket_groove = (
        Workplane("XY")
        .transformed(offset=(0, 0, -SEAL_GROOVE_DEPTH))
        .circle((SEAL_GROOVE_DIAMETER + SEAL_GROOVE_WIDTH) / 2)
        .circle(SEAL_GROOVE_DIAMETER / 2)
        .extrude(SEAL_GROOVE_DEPTH)
    )

    flange = flange.cut(gasket_groove)

    # Threaded shaft (simplified - just cylinder for animation speed)
    thread = (
        Workplane("XY")
        .circle(THREAD_MAJOR_DIAMETER / 2 - 0.5)
        .extrude(THREAD_LENGTH_SPOUT)
    )

    # Spout tube
    spout_tube = (
        Workplane("XY")
        .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS))
        .circle(SPOUT_OUTER_DIAMETER / 2)
        .extrude(SPOUT_LENGTH)
    )

    spout = flange.union(thread).union(spout_tube)

    # Bore
    bore = (
        Workplane("XY")
        .transformed(offset=(0, 0, -SPOUT_LENGTH - FLANGE_THICKNESS - 5))
        .circle(DRAIN_BORE_DIAMETER / 2 - 1)
        .extrude(SPOUT_LENGTH + FLANGE_THICKNESS + THREAD_LENGTH_SPOUT + 10)
    )

    return spout.cut(bore)

# Helper function to create seal ring
def create_seal_ring():
    """Create TPU seal ring (sits in flange groove)"""
    return (
        Workplane("XY")
        .circle((SEAL_GROOVE_DIAMETER + SEAL_GROOVE_WIDTH) / 2)
        .circle(SEAL_GROOVE_DIAMETER / 2)
        .extrude(SEAL_RING_THICKNESS)
    )

# Helper function to create simplified lid
def create_simplified_lid():
    """Create simplified lid with handle"""
    lid_body = (
        Workplane("XY")
        .box(BOX_LENGTH, BOX_WIDTH, LID_TOP_THICKNESS + RECESS_DEPTH, centered=True)
        .edges("|Z")
        .fillet(8)
    )

    # Recess
    recess_length = BOX_LENGTH - 2 * WALL_THICKNESS - 2 * RECESS_CLEARANCE
    recess_width = BOX_WIDTH - 2 * WALL_THICKNESS - 2 * RECESS_CLEARANCE

    recess = (
        Workplane("XY")
        .box(recess_length, recess_width, RECESS_DEPTH, centered=True)
        .translate((0, 0, -RECESS_DEPTH / 2))
    )

    lid = lid_body.cut(recess)

    # Handle
    handle = (
        Workplane("XY")
        .transformed(offset=(0, 0, LID_TOP_THICKNESS + RECESS_DEPTH))
        .box(HANDLE_LENGTH, HANDLE_WIDTH, HANDLE_HEIGHT, centered=True)
        .edges("|Z")
        .fillet(HANDLE_WIDTH / 4)
    )

    handle_grip = (
        Workplane("XY")
        .transformed(offset=(0, 0, LID_TOP_THICKNESS + RECESS_DEPTH))
        .box(HANDLE_LENGTH - 2 * HANDLE_WIDTH, HANDLE_WIDTH - 6, HANDLE_HEIGHT + 2, centered=True)
    )

    handle = handle.cut(handle_grip)

    return lid.union(handle)

# Helper function to create simplified scraper
def create_simplified_scraper():
    """Create simplified scraper with pins and bayonet shaft"""
    random.seed(42)

    # Base
    scraper_base = (
        Workplane("XY")
        .circle(SCRAPER_BASE_DIAMETER / 2)
        .extrude(-SCRAPER_BASE_HEIGHT)
    )

    # Reinforcement
    reinforcement = (
        Workplane("XY")
        .transformed(offset=(0, 0, -SCRAPER_BASE_HEIGHT))
        .circle(SCRAPER_BASE_DIAMETER / 2)
        .extrude(-PIN_REINFORCEMENT_HEIGHT)
    )

    scraper = scraper_base.union(reinforcement)

    # Pins (simplified - just cylinders, no tips)
    min_radius = SCRAPER_BASE_DIAMETER / 6
    max_radius = SCRAPER_BASE_DIAMETER / 2.5

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

        scraper = scraper.union(pin)

    # Bayonet shaft
    shaft = (
        Workplane("XY")
        .circle(SCRAPER_SHAFT_DIAMETER / 2)
        .extrude(SCRAPER_SHAFT_HEIGHT)
    )

    # Bayonet tabs
    for i in range(BAYONET_TAB_COUNT):
        tab_angle = i * 120
        tab_angle_rad = math.radians(tab_angle)
        tab_radius = SCRAPER_SHAFT_DIAMETER / 2 + BAYONET_TAB_PROTRUSION / 2
        tab_x = tab_radius * math.cos(tab_angle_rad)
        tab_y = tab_radius * math.sin(tab_angle_rad)
        tab_z = BAYONET_SLOT_VERTICAL

        tab = (
            Workplane("XY")
            .transformed(offset=(tab_x, tab_y, tab_z))
            .transformed(rotate=(0, 0, tab_angle))
            .box(BAYONET_TAB_PROTRUSION, BAYONET_TAB_HEIGHT, BAYONET_TAB_LENGTH, centered=True)
        )

        shaft = shaft.union(tab)

    return scraper.union(shaft)

# ============== CREATE COMPONENTS ==============
print("\nCreating components...")

box = create_simplified_box()
spout = create_simplified_spout()
seal_ring = create_seal_ring()
lid = create_simplified_lid()
scraper = create_simplified_scraper()

print("  ✓ Box created")
print("  ✓ Spout created")
print("  ✓ Seal ring created")
print("  ✓ Lid created")
print("  ✓ Scraper created")

# ============== ANIMATION FRAMES ==============
print("\nGenerating animation frames...")

# Frame 0: Box alone
frame_0 = box
frame_0.val().exportStep("/Users/user/dev/3d Models/assembly_frame_0_box.step")
print("  Frame 0: Box alone")

# Frame 1: Box + Seal ring (positioned at spout location, offset)
seal_at_spout_offset = seal_ring.translate((drain_center_x - 30, drain_center_y, drain_center_z))
frame_1 = box.union(seal_at_spout_offset)
frame_1.val().exportStep("/Users/user/dev/3d Models/assembly_frame_1_seal_approaching.step")
print("  Frame 1: Seal ring approaching")

# Frame 2: Box + Seal ring (at spout location)
seal_at_spout = seal_ring.translate((drain_center_x, drain_center_y, drain_center_z))
frame_2 = box.union(seal_at_spout)
frame_2.val().exportStep("/Users/user/dev/3d Models/assembly_frame_2_seal_positioned.step")
print("  Frame 2: Seal ring positioned")

# Frame 3: Box + Seal + Spout (approaching)
spout_approaching = spout.rotate((0, 0, 0), (0, 1, 0), 90).translate((drain_center_x - 30, drain_center_y, drain_center_z))
frame_3 = box.union(seal_at_spout).union(spout_approaching)
frame_3.val().exportStep("/Users/user/dev/3d Models/assembly_frame_3_spout_approaching.step")
print("  Frame 3: Spout approaching")

# Frame 4: Box + Seal + Spout (partially inserted)
spout_partial = spout.rotate((0, 0, 0), (0, 1, 0), 90).translate((drain_center_x - 10, drain_center_y, drain_center_z))
frame_4 = box.union(seal_at_spout).union(spout_partial)
frame_4.val().exportStep("/Users/user/dev/3d Models/assembly_frame_4_spout_inserting.step")
print("  Frame 4: Spout inserting")

# Frame 5: Box + Seal + Spout (fully installed)
spout_installed = spout.rotate((0, 0, 0), (0, 1, 0), 90).translate((drain_center_x, drain_center_y, drain_center_z))
frame_5 = box.union(seal_at_spout).union(spout_installed)
frame_5.val().exportStep("/Users/user/dev/3d Models/assembly_frame_5_spout_installed.step")
print("  Frame 5: Spout fully installed")

# Frame 6: Box + Spout + Lid (approaching)
lid_z_final = BOX_HEIGHT + (LID_TOP_THICKNESS + RECESS_DEPTH) / 2
lid_approaching = lid.translate((0, 0, lid_z_final + 50))
frame_6 = box.union(spout_installed).union(seal_at_spout).union(lid_approaching)
frame_6.val().exportStep("/Users/user/dev/3d Models/assembly_frame_6_lid_approaching.step")
print("  Frame 6: Lid approaching")

# Frame 7: Box + Spout + Lid (partially lowering)
lid_partial = lid.translate((0, 0, lid_z_final + 25))
frame_7 = box.union(spout_installed).union(seal_at_spout).union(lid_partial)
frame_7.val().exportStep("/Users/user/dev/3d Models/assembly_frame_7_lid_lowering.step")
print("  Frame 7: Lid lowering")

# Frame 8: Box + Spout + Lid (fully seated)
lid_installed = lid.translate((0, 0, lid_z_final))
frame_8 = box.union(spout_installed).union(seal_at_spout).union(lid_installed)
frame_8.val().exportStep("/Users/user/dev/3d Models/assembly_frame_8_lid_seated.step")
print("  Frame 8: Lid fully seated")

# Frame 9: Box + Spout + Lid + Scraper (approaching from below)
scraper_z_final = BOX_HEIGHT - RECESS_DEPTH / 2
scraper_approaching = scraper.translate((0, 0, scraper_z_final - 40))
frame_9 = box.union(spout_installed).union(seal_at_spout).union(lid_installed).union(scraper_approaching)
frame_9.val().exportStep("/Users/user/dev/3d Models/assembly_frame_9_scraper_approaching.step")
print("  Frame 9: Scraper approaching from below")

# Frame 10: Box + Spout + Lid + Scraper (aligning)
scraper_aligning = scraper.translate((0, 0, scraper_z_final - 20))
frame_10 = box.union(spout_installed).union(seal_at_spout).union(lid_installed).union(scraper_aligning)
frame_10.val().exportStep("/Users/user/dev/3d Models/assembly_frame_10_scraper_aligning.step")
print("  Frame 10: Scraper aligning")

# Frame 11: Box + Spout + Lid + Scraper (inserted, before rotation)
scraper_inserted = scraper.translate((0, 0, scraper_z_final))
frame_11 = box.union(spout_installed).union(seal_at_spout).union(lid_installed).union(scraper_inserted)
frame_11.val().exportStep("/Users/user/dev/3d Models/assembly_frame_11_scraper_inserted.step")
print("  Frame 11: Scraper inserted (before rotation)")

# Frame 12: Box + Spout + Lid + Scraper (rotating 30°)
scraper_rotating = scraper.rotate((0, 0, scraper_z_final), (0, 0, 1), 30).translate((0, 0, scraper_z_final))
frame_12 = box.union(spout_installed).union(seal_at_spout).union(lid_installed).union(scraper_rotating)
frame_12.val().exportStep("/Users/user/dev/3d Models/assembly_frame_12_scraper_rotating_30.step")
print("  Frame 12: Scraper rotating 30°")

# Frame 13: Box + Spout + Lid + Scraper (fully locked at 60°)
scraper_locked = scraper.rotate((0, 0, scraper_z_final), (0, 0, 1), 60).translate((0, 0, scraper_z_final))
frame_13 = box.union(spout_installed).union(seal_at_spout).union(lid_installed).union(scraper_locked)
frame_13.val().exportStep("/Users/user/dev/3d Models/assembly_frame_13_scraper_locked.step")
print("  Frame 13: Scraper fully locked (60° rotation)")

print("\n" + "=" * 70)
print("✓ Assembly animation complete!")
print("\nGenerated 14 frames:")
print("  - Frame 0: Box alone")
print("  - Frames 1-2: Seal ring installation")
print("  - Frames 3-5: Spout installation")
print("  - Frames 6-8: Lid placement")
print("  - Frames 9-13: Scraper bayonet lock attachment")
print("\nAll frames exported as STEP files for viewing/rendering.")
print("=" * 70)
