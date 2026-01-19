#!/usr/bin/env python3
"""
Flask backend for Coffee Grounds Container Designer web application.
Generates STL files from user parameters and serves them to the frontend.
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import sys
import uuid
import shutil
import zipfile
import io
import tempfile
from pathlib import Path
import subprocess

app = Flask(__name__)
CORS(app)

# Configuration
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / 'backend' / 'generated'
OUTPUT_DIR.mkdir(exist_ok=True)

# Ensure conda environment is used
CONDA_ENV = 'cq'
PYTHON_PATH = os.path.expanduser(f'~/miniforge3/envs/{CONDA_ENV}/bin/python')


def generate_box_script(params, output_dir):
    """Generate a custom box generation script with user parameters."""

    # Determine drain position and slope direction based on user selection
    spout_position = params.get('spoutPosition', 'left')

    # Configure position-specific parameters
    if spout_position == 'left':
        slope_comment = "# Drainage - slope toward left side (-X)"
        drain_center_x = "-BOX_LENGTH / 2"
        drain_center_y = "0"
        workplane = "YZ"
        workplane_offset = "drain_center_x + WALL_THICKNESS"
        boss_extrude = "BOSS_LENGTH"
        hole_offset = "drain_center_x - 5"
        hole_extrude = "BOSS_LENGTH + WALL_THICKNESS + 10"
        slope_axis = "X"
        slope_low = "x_left"
        slope_high = "x_right"
    elif spout_position == 'right':
        slope_comment = "# Drainage - slope toward right side (+X)"
        drain_center_x = "BOX_LENGTH / 2"
        drain_center_y = "0"
        workplane = "YZ"
        workplane_offset = "drain_center_x - WALL_THICKNESS"
        boss_extrude = "-BOSS_LENGTH"
        hole_offset = "drain_center_x + 5"
        hole_extrude = "-(BOSS_LENGTH + WALL_THICKNESS + 10)"
        slope_axis = "X"
        slope_low = "x_right"
        slope_high = "x_left"
    else:  # rear
        slope_comment = "# Drainage - slope toward rear side (-Y)"
        drain_center_x = "0"
        drain_center_y = "-BOX_WIDTH / 2"
        workplane = "XZ"
        workplane_offset = "drain_center_y + WALL_THICKNESS"
        boss_extrude = "BOSS_LENGTH"
        hole_offset = "drain_center_y - 5"
        hole_extrude = "BOSS_LENGTH + WALL_THICKNESS + 10"
        slope_axis = "Y"
        slope_low = "y_front"
        slope_high = "y_back"

    script = f'''#!/usr/bin/env python3
import cadquery as cq
from cadquery import Workplane
import math
import random

# User-defined parameters
BOX_LENGTH = {params['boxLength']}
BOX_WIDTH = {params['boxWidth']}
BOX_HEIGHT = {params['boxHeight']}
WALL_THICKNESS = {params['wallThickness']}
FILLET_RADIUS = 8
SPOUT_POSITION = "{spout_position}"

{slope_comment}
SLOPE_ANGLE = 2

# Threaded drain fitting dimensions
THREAD_MAJOR_DIAMETER = {params['threadDiameter']}
THREAD_PITCH = 3
THREAD_LENGTH = 20  # Must be >= wall + boss = 19mm
DRAIN_BORE_DIAMETER = 12  # Must be larger than SPOUT_OUTER_DIAMETER (11.2mm)

# Boss that protrudes from box wall
BOSS_OUTER_DIAMETER = THREAD_MAJOR_DIAMETER + 6
BOSS_LENGTH = 15

DRAIN_CENTER_HEIGHT = WALL_THICKNESS + BOSS_OUTER_DIAMETER / 2 + 2 - 5
drain_center_z = -BOX_HEIGHT / 2 + DRAIN_CENTER_HEIGHT

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

# Capsule scraper - Pin-based design
CAPSULE_DIAMETER = 37
CAPSULE_HEIGHT = 38
SCRAPER_BASE_DIAMETER = 28
SCRAPER_BASE_HEIGHT = 3
PIN_COUNT = 8
PIN_LENGTH = 35
PIN_DIAMETER = 2.5

# Create box
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

# Sloped floor - direction depends on spout position
floor_length = BOX_LENGTH - 2 * WALL_THICKNESS
floor_width = BOX_WIDTH - 2 * WALL_THICKNESS
floor_base_z = drain_center_z - DRAIN_BORE_DIAMETER / 2
floor_bottom_z = -BOX_HEIGHT / 2 + WALL_THICKNESS

# Define floor corners - small overlap to fuse with walls
x_left = -floor_length / 2 - 0.5
x_right = floor_length / 2 + 0.5
y_front = -floor_width / 2 - 0.5
y_back = floor_width / 2 + 0.5

if SPOUT_POSITION == "left":
    # Slope from right to left (X axis)
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
elif SPOUT_POSITION == "right":
    # Slope from left to right (X axis)
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
else:  # rear
    # Slope from front to rear (Y axis)
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

box_with_slope = box_hollowed.union(sloped_floor)

# Drain fitting - position depends on user selection
drain_center_x = {drain_center_x}
drain_center_y = {drain_center_y}

if SPOUT_POSITION in ["left", "right"]:
    # Left or right wall - use YZ workplane
    boss = (
        Workplane("{workplane}")
        .workplane(offset={workplane_offset})
        .center(drain_center_y, drain_center_z)
        .circle(BOSS_OUTER_DIAMETER / 2)
        .extrude({boss_extrude})
    )

    drain_hole = (
        Workplane("{workplane}")
        .workplane(offset={hole_offset})
        .center(drain_center_y, drain_center_z)
        .circle(DRAIN_BORE_DIAMETER / 2)
        .extrude({hole_extrude})
    )
else:
    # Rear wall - use XZ workplane
    boss = (
        Workplane("{workplane}")
        .workplane(offset={workplane_offset})
        .center(drain_center_x, drain_center_z)
        .circle(BOSS_OUTER_DIAMETER / 2)
        .extrude({boss_extrude})
    )

    drain_hole = (
        Workplane("{workplane}")
        .workplane(offset={hole_offset})
        .center(drain_center_x, drain_center_z)
        .circle(DRAIN_BORE_DIAMETER / 2)
        .extrude({hole_extrude})
    )

box_with_drain = box_with_slope.union(boss).cut(drain_hole)

# Filter out any disconnected solids (like floor wedge if it didn't fuse)
solids = box_with_drain.val().Solids()
if len(solids) > 1:
    largest = max(solids, key=lambda s: s.Volume())
    box_with_drain = Workplane(obj=largest)

# Move box to origin
box_final = box_with_drain.translate((0, 0, BOX_HEIGHT / 2))

# Create lid
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

# Scraper - Pin-based design
random.seed(42)

scraper_base = (
    Workplane("XY")
    .circle(SCRAPER_BASE_DIAMETER / 2)
    .extrude(-SCRAPER_BASE_HEIGHT)
)

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
scraper = scraper_with_pins.translate((0, 0, scraper_z_position))

lid_with_handle = lid_body.union(handle).union(scraper)
lid_final = lid_with_handle.translate((0, 0, BOX_HEIGHT + LID_TOP_THICKNESS / 2))

# Export
box_final.val().exportStl("{output_dir}/box.stl", tolerance=0.1)
lid_final.val().exportStl("{output_dir}/lid.stl", tolerance=0.1)

print("Generation complete")
'''
    return script


@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate STL files based on user parameters."""
    try:
        params = request.json

        # Generate unique session ID
        session_id = str(uuid.uuid4())
        session_dir = OUTPUT_DIR / session_id
        session_dir.mkdir(exist_ok=True)

        # Create custom generation script
        script_content = generate_box_script(params, session_dir)
        script_path = session_dir / 'generate.py'

        with open(script_path, 'w') as f:
            f.write(script_content)

        # Execute the script using conda environment
        result = subprocess.run(
            [PYTHON_PATH, str(script_path)],
            cwd=session_dir,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': f'Generation failed: {result.stderr}'
            }), 500

        # Verify files were created
        box_file = session_dir / 'box.stl'
        lid_file = session_dir / 'lid.stl'

        if not box_file.exists() or not lid_file.exists():
            return jsonify({
                'success': False,
                'error': 'STL files were not generated'
            }), 500

        return jsonify({
            'success': True,
            'sessionId': session_id,
            'message': 'Models generated successfully'
        })

    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Generation timed out'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/files/<session_id>/<filename>')
def serve_file(session_id, filename):
    """Serve generated STL files."""
    try:
        session_dir = OUTPUT_DIR / session_id
        return send_from_directory(session_dir, filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@app.route('/api/download/<session_id>')
def download_zip(session_id):
    """Download all STL files as a ZIP archive."""
    try:
        session_dir = OUTPUT_DIR / session_id

        # Create ZIP file in memory
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in session_dir.glob('*.stl'):
                zf.write(file, file.name)

        memory_file.seek(0)

        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'coffee_container_{session_id[:8]}.zip'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cleanup/<session_id>', methods=['DELETE'])
def cleanup(session_id):
    """Clean up generated files for a session."""
    try:
        session_dir = OUTPUT_DIR / session_id
        if session_dir.exists():
            shutil.rmtree(session_dir)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5050)
