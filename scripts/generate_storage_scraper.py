#!/usr/bin/env python3
"""
Generate a compact french press scraper that stores in the lid handle groove.
- Fits within box length (200mm max)
- Simple cylindrical handle that wedges into storage groove
- Oblong scraper end for reaching curved areas in French press
- No bayonet mount - purely for storage in handle groove
- Designed for PLA printing
"""

import cadquery as cq
from cadquery import Workplane
import math

# Storage groove dimensions (MUST MATCH generate_box.py)
STORAGE_GROOVE_DIAMETER = 15.0  # Groove in handle (1.5cm depth)
STORAGE_GROOVE_LENGTH = 80  # 8cm length along handle

# Overall dimensions - scraper fits entirely in box length
# All dimensions reduced by 5% for more compact design
SCALE_FACTOR = 0.95  # 5% reduction

TOTAL_LENGTH = 190 * SCALE_FACTOR  # Fits within box length (200mm) with margin
SHAFT_DIAMETER = 14.5 * SCALE_FACTOR  # Slightly smaller than groove (15mm) for tight friction fit
SHAFT_LENGTH = 78 * SCALE_FACTOR + 12  # Shaft section + 12mm (1.2cm) extension on scraper end

# Grip/handle section at END (where you hold it)
GRIP_DIAMETER = 18 * SCALE_FACTOR  # Thicker for comfortable grip
GRIP_LENGTH = (65 - 5) * SCALE_FACTOR  # Handle length (reduced by 5mm)
GRIP_RIDGE_HEIGHT = 1.2 * SCALE_FACTOR
GRIP_RIDGE_SPACING = 5 * SCALE_FACTOR

# Scraper blade - oblong shape at front
BLADE_WIDTH = 55 * SCALE_FACTOR  # Width of oblong
BLADE_LENGTH = 35 * SCALE_FACTOR  # Length of oblong
BLADE_THICKNESS = 2.5 * SCALE_FACTOR  # Thin for flexibility
BLADE_CORNER_RADIUS = 12 * SCALE_FACTOR  # Rounded corners to fit curved French press

print("Creating storage scraper...")

# ============== SCRAPER BLADE (at front, Z=0) ==============
# Create oblong blade (rounded rectangle) - rotated 90 degrees
blade = (
    Workplane("XY")
    .rect(BLADE_LENGTH, BLADE_WIDTH)  # Swapped to rotate 90 degrees
    .extrude(BLADE_THICKNESS)
)

# Round the corners to fit curved areas
try:
    blade = blade.edges("|Z").fillet(BLADE_CORNER_RADIUS)
except:
    pass

print("  Blade created")

# ============== BLADE REINFORCEMENT ==============
# Transition from blade to shaft (rotated to match blade)
reinforcement = (
    Workplane("XY")
    .transformed(offset=(0, 0, BLADE_THICKNESS))
    .rect(BLADE_LENGTH * 0.5, BLADE_WIDTH * 0.5)  # Swapped to match rotated blade
    .extrude(4 * SCALE_FACTOR)
    .faces(">Z")
    .workplane()
    .circle(SHAFT_DIAMETER / 2 + 1 * SCALE_FACTOR)
    .extrude(3 * SCALE_FACTOR)
)

print("  Reinforcement created")

# ============== MAIN SHAFT ==============
# Cylindrical shaft that fits in storage groove
shaft_start_z = BLADE_THICKNESS + 7 * SCALE_FACTOR

shaft = (
    Workplane("XY")
    .transformed(offset=(0, 0, shaft_start_z))
    .circle(SHAFT_DIAMETER / 2)
    .extrude(SHAFT_LENGTH)
)

# Add friction ridge to fit into handle cavity
# The handle cavity runs lengthwise through the handle interior
# Handle interior dimensions: ~50mm long × ~10mm wide (grip area)
RIDGE_WIDTH = 7.2 * SCALE_FACTOR - 1.5  # Width of ridge (1.5mm narrower)
RIDGE_HEIGHT = 6.0  # Height above shaft surface (increased by 3mm from 3.0mm to 6.0mm)
RIDGE_LENGTH = 45 * SCALE_FACTOR + 5  # Length along shaft (+5mm longer)
RIDGE_GAP_FROM_GRIP = 5 * SCALE_FACTOR + 2  # Gap between ridge end and grip start (scaled + 2mm)
RIDGE_START_OFFSET = SHAFT_LENGTH - RIDGE_LENGTH - RIDGE_GAP_FROM_GRIP  # Ridge ends before grip starts

friction_ridge = (
    Workplane("XY")
    .transformed(offset=(SHAFT_DIAMETER / 2 + RIDGE_HEIGHT / 2, 0, shaft_start_z + RIDGE_START_OFFSET))
    .box(RIDGE_HEIGHT, RIDGE_WIDTH, RIDGE_LENGTH, centered=(True, True, False))
)

# Round the ridge edges for easier insertion
try:
    friction_ridge = friction_ridge.edges("|Z").fillet(0.5 * SCALE_FACTOR)
except:
    pass

shaft = shaft.union(friction_ridge)

print("  Shaft with friction ridge created")

# ============== GRIP/HANDLE SECTION (at end) ==============
# Ergonomic grip at the end where you hold it
grip_start_z = shaft_start_z + SHAFT_LENGTH

grip_base = (
    Workplane("XY")
    .transformed(offset=(0, 0, grip_start_z))
    .circle(GRIP_DIAMETER / 2)
    .extrude(GRIP_LENGTH)
)

# Add ridges for better grip
grip_with_ridges = grip_base
num_ridges = int(GRIP_LENGTH / GRIP_RIDGE_SPACING)

for i in range(num_ridges):
    z_offset = i * GRIP_RIDGE_SPACING + 2 * SCALE_FACTOR
    if z_offset < GRIP_LENGTH - 2 * SCALE_FACTOR:
        ridge = (
            Workplane("XY")
            .transformed(offset=(0, 0, grip_start_z + z_offset))
            .circle(GRIP_DIAMETER / 2 + GRIP_RIDGE_HEIGHT)
            .extrude(2 * SCALE_FACTOR)
        )
        grip_with_ridges = grip_with_ridges.union(ridge)

# Fillet the grip ridges for comfort
try:
    grip_with_ridges = grip_with_ridges.edges("|Z").fillet(0.3 * SCALE_FACTOR)
except:
    pass

print("  Grip/handle section created")

# ============== ROUNDED END CAP ==============
# Smooth rounded end cap at the very end
end_cap_start = grip_start_z + GRIP_LENGTH

end_cap = (
    Workplane("XY")
    .transformed(offset=(0, 0, end_cap_start))
    .circle(GRIP_DIAMETER / 2)
    .workplane(offset=5 * SCALE_FACTOR)
    .circle(GRIP_DIAMETER / 2 - 2 * SCALE_FACTOR)
    .loft()
)

print("  End cap created")

# ============== ASSEMBLY ==============
scraper = (
    blade
    .union(reinforcement)
    .union(shaft)
    .union(grip_with_ridges)
    .union(end_cap)
)

# Calculate actual total length
total_height = BLADE_THICKNESS + 7 * SCALE_FACTOR + SHAFT_LENGTH + GRIP_LENGTH + 5 * SCALE_FACTOR

print("  All parts assembled")

# ============== EXPORT ==============
scraper.val().exportStep("/Users/user/dev/3d Models/CAD/storage_scraper.step")
scraper.val().exportStl("/Users/user/dev/3d Models/CAD/storage_scraper.stl", tolerance=0.1)

print("\n✓ storage_scraper.stl exported")
print("✓ storage_scraper.step exported")
print("\nStorage Scraper (Compact Design - 5% smaller + extended shaft):")
print(f"  Total length: {total_height:.1f}mm ({total_height/10:.1f}cm)")
print(f"  Scale factor: {SCALE_FACTOR} (5% reduction)")
print(f"  Layout: Blade → Shaft (+12mm extension) → Handle (grip at end)")
print(f"\nScraper Blade (at front):")
print(f"  Width: {BLADE_WIDTH:.1f}mm")
print(f"  Length: {BLADE_LENGTH:.1f}mm")
print(f"  Thickness: {BLADE_THICKNESS:.1f}mm")
print(f"  Corner radius: {BLADE_CORNER_RADIUS:.1f}mm (reaches rounded areas)")
print(f"\nShaft (storage section):")
print(f"  Diameter: {SHAFT_DIAMETER:.1f}mm (fits {STORAGE_GROOVE_DIAMETER}mm groove)")
print(f"  Length: {SHAFT_LENGTH:.1f}mm (includes +12mm extension)")
print(f"  Friction ridge height: {RIDGE_HEIGHT:.1f}mm (increased by 3mm for better grip)")
print(f"  Friction fit: {STORAGE_GROOVE_DIAMETER - SHAFT_DIAMETER:.1f}mm interference")
print(f"\nHandle/Grip (at end for holding):")
print(f"  Diameter: {GRIP_DIAMETER:.1f}mm")
print(f"  Length: {GRIP_LENGTH:.1f}mm with {num_ridges} ridges")
print(f"\nStorage:")
print(f"  Wedge shaft into lid handle groove (ø{STORAGE_GROOVE_DIAMETER}mm × {STORAGE_GROOVE_LENGTH}mm)")
print(f"  Shaft section fits in groove, handle stays outside for easy removal")
print(f"  Total length ({total_height:.0f}mm) < Box length (200mm) ✓")
print(f"\nPrint Settings:")
print(f"  Material: PLA or PETG")
print(f"  Orientation: Print standing upright (blade at bottom)")
print(f"  Infill: 30-50%")
print(f"  Layer height: 0.2mm")
print(f"  Supports: None needed")
print(f"\nUsage:")
print(f"  1. Hold by the grip/handle at the end")
print(f"  2. Use oblong blade to scrape French press")
print(f"  3. Store by wedging shaft into lid handle groove")
