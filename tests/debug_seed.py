import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
import sys
sys.path.insert(0, r"z:\MeshCreator\blender_addons")
from procedural_rock_studio.generators.telescope_gen import _rng, build_telescope_tripod_mesh, build_telescope_ota_mesh

# SMART_DIGITAL / TACTICAL_COMPACT で seed 1001,2002,3003 の rng 呼び出しをトレース
for style in ["SMART_DIGITAL","TACTICAL_COMPACT"]:
    for seed in [1001,2002,3003]:
        r = _rng(seed + 1)   # tripod
        hub_r = r.uniform(0.055, 0.085)
        hub_h = r.uniform(0.045, 0.075)
        upper_ratio = r.uniform(0.50, 0.65)
        leg_len_factor = r.uniform(0.9, 1.1)
        upper_r = r.uniform(0.018, 0.026)
        lower_r = upper_r * r.uniform(0.55, 0.75)
        if style == "TACTICAL_COMPACT":
            n_tiers = r.randint(2, 3)
        else:
            n_tiers = None
        print(f"[{style}] seed={seed}+1: hub_r={hub_r:.4f} upper_ratio={upper_ratio:.4f} n_tiers={n_tiers}")
