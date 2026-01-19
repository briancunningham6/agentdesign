# Coffee Grounds Compost Container

A 3D-printable modular container system for collecting and draining coffee grounds, designed with CadQuery.

## Overview

This project provides a complete coffee grounds collection system with:

- **Main Container Box** (200×150×150mm) - With sloped floor and threaded drain fitting
- **Lid with Handle** - Includes integrated Nespresso capsule scraper and storage groove
- **Drain Spout** - Threaded compression fitting with TPU gasket seal
- **French Press Scraper** - Bayonet-mount scraper for cleaning French press
- **Storage Scraper** - Compact scraper that stores in the lid handle groove

All parts are designed for FDM 3D printing in PLA or PETG (except TPU gasket).

## Project Structure

```
coffee-grounds-container/
├── CAD/                    # Generated 3D model files (STL/STEP)
│   ├── box.stl
│   ├── lid.stl
│   ├── drain_spout.stl
│   └── ...
├── scripts/                # Python generator scripts
│   ├── generate_all.py
│   ├── generate_box.py
│   ├── generate_drain_spout.py
│   └── ...
├── backend/                # Flask backend (optional web interface)
├── webapp/                 # React frontend (optional web interface)
├── generate_all.sh         # Generate all CAD files
├── start_webapp.sh         # Start web interface
└── README.md
```

## Quick Start

### Generate All Parts

```bash
./generate_all.sh
```

This generates all STL and STEP files in the `CAD/` directory.

### Generate Individual Parts

```bash
# Generate box and lid
/Users/user/miniforge3/envs/cq/bin/python scripts/generate_box.py

# Generate drain spout
/Users/user/miniforge3/envs/cq/bin/python scripts/generate_drain_spout.py

# Generate French press scraper
/Users/user/miniforge3/envs/cq/bin/python scripts/generate_french_press_scraper.py

# Generate storage scraper
/Users/user/miniforge3/envs/cq/bin/python scripts/generate_storage_scraper.py
```

## Parts to Print

### Main Components (PLA/PETG)
1. **box.stl** - Main container with threaded drain boss
2. **lid.stl** - Lid with handle and integrated capsule scraper (requires nail assembly)
3. **lid_scraper.stl** - Nespresso capsule scraper (bayonet mount, alternative design)
4. **drain_spout.stl** - Threaded drain spout with hex flange
5. **french_press_scraper.stl** - French press scraper with bayonet mount
6. **storage_scraper.stl** - Compact scraper for lid storage

### Seal Component (TPU)
7. **seal_ring.stl** - Gasket for drain spout (print in TPU/NinjaFlex)

### Additional Materials Required
8. **Metal brad nails** (for lid capsule scraper)
   - 8× 1.5mm diameter × 25-30mm long brad nails (18ga)
   - See [NAIL_ASSEMBLY_GUIDE.md](NAIL_ASSEMBLY_GUIDE.md) for assembly instructions

## Print Settings

**PLA/PETG parts:**
- Layer height: 0.2mm
- Infill: 30-50%
- Wall thickness: 4 perimeters
- Top/bottom layers: 5 layers
- Supports: None needed (all parts print support-free)

**TPU gasket:**
- Layer height: 0.2mm
- Infill: 100%
- Print slowly (20-30mm/s)

## Assembly

1. **Install nails in capsule scraper (integrated into lid):**
   - Press 8× 1.5mm brad nails into holes on scraper underside
   - Nail heads sit in countersunk sockets
   - See [NAIL_ASSEMBLY_GUIDE.md](NAIL_ASSEMBLY_GUIDE.md) for detailed instructions

2. **Attach drain spout:**
   - Place TPU seal ring in the flange groove
   - Thread spout into box boss from outside
   - Hand-tighten using hex flange

3. **Attach optional scrapers to lid:**
   - **Capsule scraper (separate):** Insert shaft, rotate 60° to lock bayonet
   - **French press scraper:** Same bayonet mechanism

4. **Store scrapers when not in use:**
   - Wedge storage scraper shaft into lid handle groove
   - French press scraper can also store in groove

## Features

### Box
- 200×150×150mm interior volume
- Sloped floor (2°) drains toward left wall
- M16×3 threaded boss for secure spout attachment
- Drainage channel guides liquid to drain
- Four rubber feet recesses for stability

### Lid
- Recessed fit prevents spills
- Integrated handle with tool storage groove
- Metal nail-insert Nespresso capsule scraper (underside, requires 8× brad nails)
- Bayonet socket for attachable scrapers

### Drain Spout
- 60mm extension reaches sink
- M16×3 threaded shaft with hand-tightenable hex flange
- TPU gasket creates watertight seal
- 8mm internal bore for liquid flow

### Scrapers
- **Capsule scraper (integrated):** 8 metal nails pierce foil, rotate to extract grounds
  - Requires assembly: press 1.5mm × 25-30mm brad nails into holes
  - Metal nails are much stronger than plastic pins
- **Capsule scraper (separate, bayonet mount):** Alternative bayonet-attachable version
- **French press:** Oblong blade reaches curved areas, bayonet mount
- **Storage:** Compact design stores in handle, friction ridge locks in place

## Design Files

All scripts generate both STL (for slicing) and STEP (for CAD editing) formats.

### Test Components

Generate fit-test coupons to verify tolerances before printing full parts:

```bash
/Users/user/miniforge3/envs/cq/bin/python scripts/generate_fit_test.py
```

This creates scaled-down test pieces to verify:
- Thread engagement (spout → box)
- Bayonet lock fit (scraper → lid)
- Seal compression

## Optional Web Interface

Start the interactive web designer:

```bash
./start_webapp.sh
```

Access at http://localhost:3000 to customize dimensions and regenerate parts.

## Requirements

- **CadQuery environment:** Python with CadQuery library
- **Conda environment:** `cq` (includes CadQuery)
- **Optional:** Node.js + Flask (for web interface)

## License

Open source - modify and share freely.

## Credits

Designed with CadQuery parametric CAD library.
