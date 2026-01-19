# Quick Start Guide

## Coffee Grounds Compost Container

### What You Need

#### To Print:
1. 3D printer (FDM recommended, PLA or PETG)
2. TPU filament (small amount for gasket)

#### To Purchase:
1. **8× Brad nails** - 1.5mm diameter × 25-30mm length (18ga)
   - Available at any hardware store
   - Used for capsule scraper assembly
   - Cost: ~$3-5 for a box of 1000

#### Tools:
- Small hammer or rubber mallet
- Hex wrench or pliers (for spout installation)

---

## Step-by-Step Instructions

### 1. Generate CAD Files

```bash
cd "/Users/user/dev/3d Models"
./generate_all.sh
```

All STL files will be created in the `CAD/` directory.

### 2. Print All Parts

Print the following files from `CAD/`:

**Main parts (PLA/PETG):**
- `box.stl` - Main container (~6-8 hours)
- `lid.stl` - Lid with integrated scraper (~2-3 hours)
- `drain_spout.stl` - Drain fitting (~1 hour)
- `storage_scraper.stl` - Scraper for French press (~1 hour)
- `french_press_scraper.stl` - Alternative scraper (~1 hour)

**Seal (TPU):**
- `seal_ring.stl` - Gasket for drain (~15 minutes)

**Print Settings:**
- Layer height: 0.2mm
- Infill: 30-50%
- Supports: NONE (all parts designed support-free)

### 3. Assemble Capsule Scraper

**The lid has 8 holes on the underside that need metal nails inserted.**

1. Flip lid upside-down
2. Locate the 8 holes on the circular scraper base
3. Take 1.5mm × 25-30mm brad nails
4. Press each nail into a hole (nail head sits in countersunk socket)
5. Tap gently with hammer until nail head is flush
6. Repeat for all 8 nails

**See [NAIL_ASSEMBLY_GUIDE.md](NAIL_ASSEMBLY_GUIDE.md) for detailed instructions with troubleshooting.**

### 4. Install Drain Spout

1. Place TPU seal ring in the groove on the underside of the hex flange
2. From outside the box, thread the spout into the threaded boss
3. Hand-tighten using the hex flange (no tools needed, but can use pliers if desired)
4. Check for watertight seal

### 5. Ready to Use!

**Using the capsule scraper:**
1. Remove used Nespresso capsule from machine
2. Center capsule on scraper (foil side up)
3. Press down firmly - metal nails pierce the foil
4. Rotate capsule 1-2 full turns
5. Lift capsule and tap to release grounds into container

**Using the French press scraper:**
1. Optional: Attach to lid using bayonet mount
2. OR use storage scraper (stores in handle groove)
3. Scrape grounds from French press into container

**Draining:**
1. Position container near sink
2. Open drain spout
3. Liquid drains out through spout
4. Coffee grounds stay in container
5. Close spout when done

---

## Troubleshooting

**Nails won't fit in holes:**
- Verify you're using 1.5mm diameter nails
- May need to pre-drill with 1.4mm bit
- Try different brand of nails (dimensions vary slightly)

**Nails pull out:**
- Use slightly thicker nails (1.6mm)
- Add tiny drop of superglue to shaft before insertion

**Spout leaks:**
- Check TPU seal ring is properly seated in groove
- Tighten spout more (hand-tight should be sufficient)
- Verify threads engaged correctly

**Lid doesn't fit:**
- Check for stringing or printing artifacts
- May need to trim the recess edges slightly
- Ensure clearances printed correctly

---

## Maintenance

**After each use:**
- Rinse container and lid
- Wipe drain spout
- Check nails are still secure

**Weekly:**
- Deep clean with dish soap
- Inspect seal ring for wear
- Check drain spout threads

**Monthly:**
- Verify all nails remain tight
- Replace any bent/damaged nails
- Check bayonet locks on scrapers

---

## Need Help?

- **Assembly issues:** See [NAIL_ASSEMBLY_GUIDE.md](NAIL_ASSEMBLY_GUIDE.md)
- **Design info:** See [README.md](README.md)
- **Changes:** See [DESIGN_CHANGELOG.md](DESIGN_CHANGELOG.md)

---

## Optional Components

The system also includes:

- `lid_scraper.stl` - Separate bayonet-mount capsule scraper (alternative to integrated version)
- `fit_test.stl` - Test coupons to verify tolerances before printing full parts
- Assembly animation frames (for documentation)

These are optional and not needed for basic operation.
