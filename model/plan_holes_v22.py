#!/usr/bin/env python3
"""Pure-python mirror of tie_holes()/tie_holes_angled() (issue21/D/push/model/
build_2121_v21.py) with the v22 call parameters from v22/build/apply_v22.py
chunk 4. Verifies the predicted v22 tie-hole total (3,533) before the build.
Usage: python3 plan_holes_v22.py
"""
import math

def count_axis(u_range, v_range, top_fn=None):
    n = 0
    u = u_range[0]
    while u <= u_range[1] + 1e-6:
        v_hi = v_range[1]
        if top_fn is not None:
            v_hi = min(v_hi, top_fn(u) - 0.135)
        v = v_range[0]
        while v <= v_hi + 1e-6:
            n += 1
            v += 0.60
        u += 0.45
    return n

def count_angled(d_range, v_range, top_fn=None):
    return count_axis(d_range, v_range, top_fn)

def roof_z_north(x):
    return 4.85 + (4.50 - 4.85) * ((x + 10.0) / 53.42)

G = {}
# B1
G["ThickWall"] = count_axis((18.5, 39.5), (-5.75, -2.15))
G["NorthWall"] = count_axis((16.2, 26.55), (-3.75, -0.75))
G["Jog"] = 2 * count_axis((-8.23, -7.33), (0.3, 4.5), lambda y: 4.59)
G["G2_Column"] = 6 * count_axis((0.0, 0.0), (-5.75, -2.15))  # (cx,cx) = 1 col x 7 rows
# North walls
G["North_Above"] = 2 * count_axis((-9.45, 29.25), (0.9, 4.5), roof_z_north)
G["NorthEast_A"] = 2 * count_axis((29.70, 40.50), (0.9, 4.5), roof_z_north)
G["NorthEast_B"] = 2 * count_axis((41.40, 43.20), (0.9, 4.5), roof_z_north)
G["North_Slot_W"] = 2 * count_axis((-9.45, 15.30), (0.3, 0.3))
G["North_Slot_Mid"] = 2 * count_axis((27.45, 29.25), (0.3, 0.3))
G["NorthEast_Slot_E"] = 2 * count_axis((41.40, 48.15), (0.3, 0.3))
G["Stair_Parapet"] = count_axis((16.20, 16.65), (0.3, 0.3), lambda x: 1.0 - 0.5 * (x - 15.63))
# G3 north wall (angled, per face x2)
top_g3n = lambda d: 4.90 - 0.08964 * d
G["Cafe_North_Low"] = 2 * count_angled((0.45, 14.40), (0.3, 0.3))
G["Cafe_North_High"] = 2 * count_angled((0.45, 14.40), (2.7, 4.5), top_g3n)
G["Cafe_North_SlotW"] = 2 * count_angled((0.45, 1.35), (1.5, 1.5))
G["Cafe_North_SlotE"] = 2 * count_angled((13.95, 14.40), (1.5, 1.5))
# Entrance (angled, per face x2)
G["Entrance_N"] = 2 * count_angled((0.20, 3.90), (0.3, 4.5))
G["Entrance_S"] = 2 * count_angled((0.20, 3.90), (0.3, 4.5))
G["Entrance_Lintel"] = 2 * count_angled((0.25, 2.95), (3.3, 3.3))
# New walls
G["Museum_SE"] = 2 * count_axis((31.5, 38.7), (0.3, 3.9))
top_g3e = lambda d: 4.90 - 0.0745 * d
G["G3_East"] = 2 * count_angled((0.45, 8.05), (0.3, 4.5), top_g3e)
G["G3_East_Lintel"] = 2 * count_angled((0.25, 2.35), (2.7, 2.7))
top_g3se = lambda d: 4.10 - 0.0882 * d
G["G3_SE"] = 2 * count_angled((0.45, 8.10), (0.3, 4.5), top_g3se)

total = 0
for k, v in G.items():
    print(f"{k:18s} {v}")
    total += v
print(f"{'TOTAL':18s} {total}")
print("v21 total was 3625; v22 delta:", total - 3625)
