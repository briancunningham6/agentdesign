# Nail Hole Design Fix - Technical Details

## Issue Identified
The original nail hole design had three problems:
1. Nail holes could overlap with the bayonet shaft (14mm diameter)
2. Bayonet tabs (1.5mm protrusion) didn't provide clearance for nail heads (3.5mm socket)
3. Nail holes might not pass completely through the base

## Solutions Implemented

### 1. Bayonet Tab Clearance
**Change:** Reduced bayonet tab protrusion by 0.15mm
- **Old value:** `BAYONET_TAB_PROTRUSION = 1.5mm`
- **New value:** `BAYONET_TAB_PROTRUSION = 1.35mm`
- **Reason:** Provides 0.15mm additional clearance for nail heads in countersunk sockets

**Impact:**
- Tabs still engage securely in bayonet slots
- Additional clearance prevents nail heads from interfering with tab rotation
- Reduces risk of nail heads catching on tabs during insertion/removal

### 2. Nail Hole Placement (No Shaft Overlap)
**Change:** Increased minimum radius to clear bayonet shaft
- **Old value:** `min_radius = SCRAPER_BASE_DIAMETER / 6` → ~4.67mm
- **New value:** `min_radius = SCRAPER_SHAFT_DIAMETER / 2 + 1.5` → 8.5mm
- **Reason:** Bayonet shaft is 14mm diameter (7mm radius), so holes must start at >7mm

**Calculation:**
```
Shaft radius:     7.0mm  (14mm diameter ÷ 2)
Safety margin:  + 1.5mm  (clearance)
─────────────────────────
Min nail radius:  8.5mm
```

**Impact:**
- Nail holes now positioned in a ring from 8.5mm to 11.2mm radius
- No overlap with central bayonet shaft
- All 8 nail holes remain visible and accessible
- Still provides good coverage across capsule area

### 3. Through-Hole Verification
**Change:** Ensured nail holes pass completely through base
- **Old calculation:** `nail_hole_length = PIN_REINFORCEMENT_HEIGHT - NAIL_SOCKET_DEPTH - NAIL_TAPER_LENGTH + 1`
- **New calculation:** Uses total base thickness with extra margin

**New Code:**
```python
total_base_thickness = SCRAPER_BASE_HEIGHT + PIN_REINFORCEMENT_HEIGHT  # 3mm + 10mm = 13mm
remaining_thickness = total_base_thickness - NAIL_SOCKET_DEPTH - NAIL_TAPER_LENGTH  # 13 - 8 - 2 = 3mm
nail_hole_length = remaining_thickness + 2  # 3 + 2 = 5mm (extra margin ensures through-hole)
```

**Depth Breakdown:**
```
Z = 0mm       ← Top surface (scraper base)
Z = -8mm      ← Socket bottom (countersink for nail head)
Z = -10mm     ← Taper bottom (transition to shaft hole)
Z = -13mm     ← Base bottom (3mm base + 10mm reinforcement)
Z = -15mm     ← Hole extends 2mm beyond (ensures through-hole)
```

**Impact:**
- Nail holes guaranteed to pass completely through
- Nails can be pushed all the way through if needed
- No blind holes that could trap nails partway
- Extra 2mm margin accounts for any printing variations

## Geometry Summary

### Scraper Base Structure:
```
                    ┌─ Bayonet shaft (14mm ø)
                    │
        ┌───────────●───────────┐
        │           │           │  ← Base surface (28mm ø)
        │  ○     ○  │  ○     ○  │  ← Nail sockets (3.5mm ø)
        │           │           │     8 holes in ring pattern
        │  ○     ○  │  ○     ○  │     Radius: 8.5mm to 11.2mm
        │           │           │
        └───────────┴───────────┘
              3mm base
        ┌─────────────────────┐
        │   PIN REINFORCEMENT  │  ← 10mm thick
        │    (solid cylinder)   │     For nail hole strength
        └─────────────────────┘
```

### Nail Hole Cross-Section:
```
        3.5mm ø socket
            ┌───┐
            │   │ 8mm deep
            │   │
            ├─┬─┤
             \│/  2mm taper
              │
              │   1.4mm ø shaft
              │   (friction fit for 1.5mm nail)
              │
              │   5mm length
              │   (passes through remaining 3mm + 2mm extra)
              ▼
```

## Verification Checklist

After regenerating, verify:

- [ ] No nail holes visible in center (within 7mm radius)
- [ ] All 8 nail holes positioned in outer ring (8.5-11.2mm radius)
- [ ] Bayonet tabs have clearance for nail head sockets
- [ ] Each hole passes completely through base (can see light through)
- [ ] Nail heads sit flush or recessed when installed
- [ ] Bayonet mechanism still functions smoothly

## Files Modified

**scripts/generate_box.py:**
- Line 89: `BAYONET_TAB_PROTRUSION = 1.35` (reduced from 1.5)
- Line 414-415: Updated min_radius calculation to clear shaft
- Line 453-461: Fixed nail hole depth calculation for through-holes

## Testing Recommendations

1. **Visual inspection:**
   - Open lid.step in CAD viewer
   - Check nail hole positions don't overlap shaft
   - Verify holes exit bottom surface

2. **Print test:**
   - Print lid
   - Check nail holes are open (not blocked)
   - Test nail insertion (should press-fit smoothly)
   - Verify bayonet shaft fits in lid socket

3. **Assembly test:**
   - Install 8× 1.5mm brad nails
   - Check nail heads sit flush in sockets
   - Attach scraper to lid using bayonet
   - Rotate to lock - should clear nail heads
   - Remove and reattach several times

## Expected Behavior

**Correct design:**
- Nail holes form a ring around the central shaft
- All holes visible and accessible from top
- Nails press-fit securely without bottoming out
- Bayonet tabs clear nail heads with 0.15mm margin
- Smooth insertion/removal of scraper from lid

**If issues persist:**
- Check SCRAPER_SHAFT_DIAMETER matches actual shaft (14mm)
- Verify min_radius calculation: should be >7mm
- Confirm total_base_thickness = 13mm
- Inspect for modeling errors in CAD viewer
