#!/usr/bin/env python3
"""
Generate all parts for the coffee grounds compost container.
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "generate_box.py",
    "generate_drain_spout.py",
    "generate_french_press_scraper.py",
    "generate_storage_scraper.py",
]

def main():
    script_dir = Path(__file__).parent

    print("=" * 50)
    print("Coffee Grounds Compost Container - Generate All")
    print("=" * 50)

    failed = []

    for script in SCRIPTS:
        script_path = script_dir / script
        print(f"\n>>> Running {script}...")
        print("-" * 40)

        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=script_dir
        )

        if result.returncode != 0:
            failed.append(script)
            print(f"✗ {script} failed!")
        else:
            print(f"✓ {script} completed")

    print("\n" + "=" * 50)
    if failed:
        print(f"FAILED: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("All parts generated successfully!")
        print("\nOutput files in CAD/:")
        print("  Box:                  box.stl, box.step")
        print("  Lid:                  lid.stl, lid.step, lid_scraper.stl, lid_scraper.step")
        print("  Drain spout:          drain_spout.stl, drain_spout.step")
        print("  Seal ring:            seal_ring.stl, seal_ring.step")
        print("  French press scraper: french_press_scraper.stl, french_press_scraper.step")
        print("  Storage scraper:      storage_scraper.stl, storage_scraper.step")
        print("=" * 50)

if __name__ == "__main__":
    main()
