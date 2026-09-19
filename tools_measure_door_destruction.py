"""
破壊アニメの物理パラメータ調整用の測定スクリプト（blender --background --python で実行）。
扉を生成して generate_door_destruction を各設定で実行し、破片の飛距離・最高速度・静止までの時間を表示する。
引数: -- <impact_strength> [frame_count] [seed]
"""
import bpy
import sys
import math
import statistics

addon_parent = r"z:\MeshCreator\blender_addons"
if addon_parent not in sys.path:
    sys.path.insert(0, addon_parent)

from procedural_rock_studio import rock_studio_addon
from procedural_rock_studio.generators import generate_procedural_prop_mesh
from procedural_rock_studio.generators.door_destruction_gen import generate_door_destruction

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
strength = float(args[0]) if args else 1.0
frame_count = int(args[1]) if len(args) > 1 else 72
seed = int(args[2]) if len(args) > 2 else 7
# 追加引数: NAME=VALUE で door_destruction_gen の調整定数を上書き（例 FORCE_BASE=300 FLOOR_SIZE=200）
import procedural_rock_studio.generators.door_destruction_gen as _gen
for a in args[3:]:
    k, v = a.split("=")
    setattr(_gen, k, float(v))
    print("override", k, "=", v)
FPS = bpy.context.scene.render.fps

bpy.ops.wm.read_factory_settings(use_empty=True)
rock_studio_addon.register()

door_frame = generate_procedural_prop_mesh(
    context=bpy.context, target_obj=None, category="DOOR", name="M", seed=3,
    size_x=2.2, size_y=0.5, size_z=2.6,
    door_arch_style='ROMAN_ROUND', door_pillar_shape='SQUARE_PIER',
    door_pillar_width=0.42, door_column_height=1.7, door_has_keystone=True,
    door_strap_style='CROSS_Z', door_stud_pattern='GRID', door_handle_style='RING_PULL',
    door_has_hinges=True, door_has_edge_trim=True, door_edge_trim_width=0.05,
    door_wood_material='WEATHERED_OAK', door_iron_style='BLACK_FORGED',
    door_damage=0.35, door_weathering=0.55, door_moss_amount=0.20,
    door_open_angle=0.0, door_open_direction='OUTWARD', door_combine=False,
)
leaf_l = next(c for c in door_frame.children if c.name.endswith("_Leaf_L"))
leaf_r = next(c for c in door_frame.children if c.name.endswith("_Leaf_R"))

dbg = {}
generate_door_destruction(
    context=bpy.context, leaf_obj_l=leaf_l, leaf_obj_r=leaf_r, frame_obj=door_frame,
    shard_count=16, frame_count=frame_count, impact_strength=strength, impact_frames=4,
    subdivide_cuts=2, seed=seed, name="M_D", bake_mode='BONES', debug_out=dbg,
)
sampled = dbg["sampled"]
frames = sorted(sampled)
objs = list(sampled[frames[0]].keys())


def pos(f, o):
    return sampled[f][o].translation


start = {o: pos(frames[0], o) for o in objs}
print(f"=== strength={strength} frames={frame_count} fps={FPS} shards={len(objs)} ===")
max_speed = 0.0
settle_frame = None
for i in range(1, len(frames)):
    f0, f1 = frames[i - 1], frames[i]
    dt = (f1 - f0) / FPS
    speeds = [((pos(f1, o) - pos(f0, o)).length / dt) for o in objs]
    max_speed = max(max_speed, max(speeds))
    if settle_frame is None and sorted(speeds)[int(len(speeds) * 0.9)] < 0.3:
        settle_frame = f1
    if f1 in (2, 4, 6, 12, 24, 36, 48, 60, frame_count):
        print(f"  frame {f1:3d}: speed median {statistics.median(speeds):6.2f} m/s  max {max(speeds):6.2f} m/s")
last = frames[-1]
horiz = [math.hypot(pos(last, o).x - start[o].x, pos(last, o).y - start[o].y) for o in objs]
disp = [(pos(last, o) - start[o]).length for o in objs]
below = sum(1 for o in objs if pos(last, o).z < -0.05)
airborne = sum(1 for o in objs if pos(last, o).z > 0.3)
print(f"  max speed over all: {max_speed:.1f} m/s")
print(f"  final horizontal travel  median {statistics.median(horiz):.2f} m  max {max(horiz):.2f} m")
print(f"  final displacement       median {statistics.median(disp):.2f} m  max {max(disp):.2f} m")
print(f"  90% of shards slower than 0.3 m/s from frame: {settle_frame}")
print(f"  below floor (z<-0.05): {below}/{len(objs)}   still high (z>0.3) at end: {airborne}/{len(objs)}")
# 外れ値（最終的に遠くへ飛んだ破片）の内訳
far = sorted(((h, o) for h, o in zip(horiz, objs) if h > 12.0), key=lambda t: -t[0])
vcount = {id(v[0]): v[2] - v[1] for v in dbg["vertex_ranges"]}
order_idx = {id(o): i for i, o in enumerate(objs)}
for h, o in far[:8]:
    f2 = frames[1] if len(frames) > 1 else frames[0]
    v2 = (pos(f2, o) - start[o]).length / ((f2 - frames[0]) / FPS)
    print(f"  FAR idx {order_idx[id(o)]}/{len(objs)}  verts {vcount.get(id(o))}  travel {h:.1f} m  speed@frame{f2} {v2:.1f} m/s  start z {start[o].z:.2f}")
print("  vertex count quantiles:", sorted(vcount.values())[::max(1, len(vcount) // 8)], "max", max(vcount.values()))
