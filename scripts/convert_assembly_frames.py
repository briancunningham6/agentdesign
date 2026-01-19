#!/usr/bin/env python3
import sys
from pathlib import Path

import cadquery as cq
from cadquery import exporters, importers


def main() -> int:
    root = Path(__file__).resolve().parent
    stl_dir = root / "assembly_frames_stl"
    stl_dir.mkdir(parents=True, exist_ok=True)

    step_files = sorted(root.glob("assembly_frame_*.step"))
    print(f"Found {len(step_files)} STEP frames in {root}")
    if not step_files:
        return 1

    exported = 0
    for step_path in step_files:
        out_path = stl_dir / (step_path.stem + ".stl")
        if out_path.exists():
            continue
        try:
            shape = importers.importStep(str(step_path))
            exporters.export(shape, str(out_path), tolerance=0.1)
            print(f"Wrote {out_path.name}")
            exported += 1
        except Exception as exc:
            print(f"Failed {step_path.name}: {exc}")
            return 1

    stl_files = sorted(stl_dir.glob("assembly_frame_*.stl"))
    print(f"STL frames present: {len(stl_files)}")
    return 0 if stl_files else 1


if __name__ == "__main__":
    sys.exit(main())
