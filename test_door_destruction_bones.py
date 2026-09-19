"""
ボーン方式(UE向け)の破壊アニメ焼き付けの検証:
 1. 評価済み(ボーン変形後)メッシュ頂点が、記録した剛体運動 Mf @ M0^-1 @ basis と一致するか
 2. ルートボーンが1本・破片ごとに1ボーンか
 3. Door_Frameを移動+回転させて配置しても(ローカル空間変換)正しく一致するか
 4. FBX出力→新規シーンへ再インポートして、構造(アーマチュア/ボーン/頂点グループ/アニメ/寸法)を確認
"""
import bpy
import sys
import os
import math
from mathutils import Matrix, Vector, Euler

addon_parent = r"z:\MeshCreator\blender_addons"
if addon_parent not in sys.path:
    sys.path.insert(0, addon_parent)

from procedural_rock_studio import rock_studio_addon
from procedural_rock_studio.generators import generate_procedural_prop_mesh
from procedural_rock_studio.generators.door_destruction_gen import generate_door_destruction
from procedural_rock_studio.utils.anim_baker import export_door_destruction_fbx, export_door_static_fbx

OUT_DIR = r"Z:\MeshCreator\exports\_bone_test"
os.makedirs(OUT_DIR, exist_ok=True)
for f in os.listdir(OUT_DIR):
    if f.endswith(".fbx"):
        os.remove(os.path.join(OUT_DIR, f))

bpy.ops.wm.read_factory_settings(use_empty=True)
rock_studio_addon.register()

door_frame = generate_procedural_prop_mesh(
    context=bpy.context, target_obj=None, category="DOOR", name="BoneDoor", seed=3,
    size_x=2.2, size_y=0.5, size_z=2.6,
    door_arch_style='ROMAN_ROUND', door_pillar_shape='SQUARE_PIER',
    door_pillar_width=0.42, door_column_height=1.7, door_has_keystone=True,
    door_strap_style='CROSS_Z', door_stud_pattern='GRID', door_handle_style='RING_PULL',
    door_has_hinges=True, door_has_edge_trim=True, door_edge_trim_width=0.05,
    door_wood_material='WEATHERED_OAK', door_iron_style='BLACK_FORGED',
    door_damage=0.35, door_weathering=0.55, door_moss_amount=0.20,
    door_open_angle=0.0, door_open_direction='OUTWARD', door_combine=False,
)
# ローカル空間変換の検証のため、扉を移動+回転させて配置
door_frame.location = (3.0, 2.0, 0.0)
door_frame.rotation_euler = (0.0, 0.0, math.radians(30))
bpy.context.view_layer.update()

leaf_l, leaf_r = None, None
for c in door_frame.children:
    if c.name.endswith("_Leaf_L"):
        leaf_l = c
    elif c.name.endswith("_Leaf_R"):
        leaf_r = c

dbg = {}
combined, action = generate_door_destruction(
    context=bpy.context, leaf_obj_l=leaf_l, leaf_obj_r=leaf_r, frame_obj=door_frame,
    shard_count=8, frame_count=24, sample_step=3, impact_strength=1.0, impact_frames=4,
    subdivide_cuts=1, seed=7, name="BoneDoor_Destruction", bake_mode='BONES', debug_out=dbg,
)
arm = combined.parent
print("armature:", arm.name, "type:", arm.type, "bones:", len(arm.data.bones))
roots = [b for b in arm.data.bones if b.parent is None]
print("root bones:", [b.name for b in roots])
n_ranges = len(dbg["vertex_ranges"])
print("shard ranges:", n_ranges, " vertex groups:", len(combined.vertex_groups))
assert len(roots) == 1 and roots[0].name == "root", "ルートボーンは1本('root')であること"
assert len(arm.data.bones) == n_ranges + 1, "破片数+root のボーン数であること"
assert len(combined.vertex_groups) == n_ranges

# --- 1./3. 評価済み頂点 vs 記録した剛体運動 ---
sampled = dbg["sampled"]
vranges = dbg["vertex_ranges"]
F = dbg["frame_world"]
scene = bpy.context.scene
rest_local = [v.co.copy() for v in combined.data.vertices]   # rest(=破壊前)のDoor_Frameローカル座標
basis = sampled[0]
max_err = 0.0
frames_checked = sorted(sampled.keys())
for rel in frames_checked:
    scene.frame_set(1 + rel)
    dg = bpy.context.evaluated_depsgraph_get()
    eo = combined.evaluated_get(dg)
    em = eo.to_mesh()
    mw_eval = eo.matrix_world
    for obj, start, end in vranges:
        delta_world = sampled[rel][obj] @ basis[obj].inverted()
        for i in (start, (start + end) // 2, end - 1):
            expected = delta_world @ (F @ rest_local[i])
            actual = mw_eval @ em.vertices[i].co
            max_err = max(max_err, (expected - actual).length)
    eo.to_mesh_clear()
print(f"max error over {len(frames_checked)} sampled frames: {max_err:.6f} m")
assert max_err < 1e-3, "ボーン変形後の頂点が記録した剛体運動と一致しない"

# frame0は組み上がり姿勢(rest)と一致
scene.frame_set(1)
dg = bpy.context.evaluated_depsgraph_get()
eo = combined.evaluated_get(dg)
em = eo.to_mesh()
err0 = max((em.vertices[i].co - rest_local[i]).length for i in range(0, len(rest_local), 7))
eo.to_mesh_clear()
print(f"frame1 deviation from rest: {err0:.8f}")
assert err0 < 1e-5

# --- 2. FBX出力 ---
fbx_destruct = os.path.join(OUT_DIR, "BoneDoor_Destruction.fbx")
fbx_frame = os.path.join(OUT_DIR, "BoneDoor_Frame.fbx")
fbx_leaves = os.path.join(OUT_DIR, "BoneDoor_LeavesIntact.fbx")
export_door_destruction_fbx(combined, fbx_destruct)
export_door_static_fbx([door_frame], fbx_frame, origin_matrix=door_frame.matrix_world)
export_door_static_fbx([leaf_l, leaf_r], fbx_leaves, origin_matrix=door_frame.matrix_world)
# 出力後、元オブジェクトの名前・位置が壊れていないこと
assert arm.name.endswith("_Armature"), f"Armature名が復元されていない: {arm.name}"
assert (arm.matrix_world.translation - door_frame.matrix_world.translation).length < 1e-6
assert door_frame.name == "BoneDoor_Frame" and leaf_l.name.endswith("_Leaf_L")
expected_height = max(v.co.z for v in combined.data.vertices)
print("expected destruction mesh height (m):", round(expected_height, 3))
print("EXPORT OK:", [os.path.getsize(p) for p in (fbx_destruct, fbx_frame, fbx_leaves)])

# --- 3. FBXの中身検査（UEはArmatureノードのスケールを骨位置に反映しないため、頂点と骨が同単位・ノードスケール1であること）---
from io_scene_fbx import parse_fbx
_root, _ver = parse_fbx.parse(fbx_destruct)
_objs = [e for e in _root.elems if e.id == b'Objects'][0]
_geo_zmax = None
_shard_t = []
for _o in _objs.elems:
    if _o.id == b'Geometry':
        for _c in _o.elems:
            if _c.id == b'Vertices' and _geo_zmax is None:
                _geo_zmax = max(_c.props[0][2::3])
    if _o.id == b'Model':
        _p70 = [c for c in _o.elems if c.id == b'Properties70']
        _props = {}
        for _pp in (_p70[0].elems if _p70 else []):
            if _pp.id == b'P' and _pp.props:
                _k = _pp.props[0]
                _props[_k.decode() if isinstance(_k, bytes) else _k] = _pp.props[4:]
        _s = _props.get("Lcl Scaling") or [1.0, 1.0, 1.0]
        assert all(abs(v - 1.0) < 1e-6 for v in _s), f"ノードにスケールが残っている: {_o.props[1]} {_s}"
        if _o.props[1].startswith(b"Shard_"):
            _t = _props.get("Lcl Translation") or [0.0, 0.0, 0.0]
            _shard_t.append(max(abs(v) for v in _t))
assert abs(_geo_zmax - expected_height * 100.0) < expected_height * 100.0 * 0.02, f"頂点がcm単位になっていない: {_geo_zmax}"
assert 0.4 * _geo_zmax < max(_shard_t) < 1.1 * _geo_zmax, f"骨位置が頂点と同単位(cm)でない: bone max {max(_shard_t)} / geo {_geo_zmax}"
print(f"fbx units OK: node scales==1, geometry zmax {_geo_zmax:.1f} cm, bone offset max {max(_shard_t):.1f} cm")

# --- 4. 新規シーンへ再インポートして構造確認 ---
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=fbx_destruct)
arms = [o for o in bpy.data.objects if o.type == 'ARMATURE']
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
print("reimport: armatures", [a.name for a in arms], "meshes", [m.name for m in meshes])
assert len(arms) == 1 and len(meshes) == 1
a = arms[0]
m = meshes[0]
bones = a.data.bones
rroots = [b.name for b in bones if b.parent is None]
print("reimport: bones", len(bones), "root bones", rroots, " vertex groups", len(m.vertex_groups))
assert len(rroots) == 1, "再インポート後もルートボーンは1本であること"
assert len(bones) == n_ranges + 1
assert len(m.vertex_groups) == n_ranges
act = a.animation_data.action if a.animation_data else None
assert act is not None, "アニメーションが再インポートされていない"
print("reimport: action", act.name, "fcurves", len(act.fcurves), "frame_range", tuple(act.frame_range))
assert len(act.fcurves) >= n_ranges * 7
# 寸法(高さ): 再インポート後のメッシュ高さが元(m)とほぼ一致
zs = [(m.matrix_world @ v.co).z for v in m.data.vertices]
h = max(zs) - min(zs)
print("reimport: mesh height", round(h, 3), "(orig max z", round(expected_height, 3), ")")

# 静的FBX: 原点基準・直立で出ているか
for label, path in (("frame", fbx_frame), ("leaves", fbx_leaves)):
    before = set(bpy.data.objects.keys())
    bpy.ops.import_scene.fbx(filepath=path)
    new = [bpy.data.objects[k] for k in bpy.data.objects.keys() if k not in before]
    mo = [o for o in new if o.type == 'MESH'][0]
    ws = [mo.matrix_world @ v.co for v in mo.data.vertices]
    cx = (max(w.x for w in ws) + min(w.x for w in ws)) / 2
    cy = (max(w.y for w in ws) + min(w.y for w in ws)) / 2
    print(f"static {label}: bbox center x={cx:.3f} y={cy:.3f} zmin={min(w.z for w in ws):.3f} zmax={max(w.z for w in ws):.3f} "
          f"mats={[mm.name for mm in mo.data.materials]}")
    assert abs(cx) < 0.6, "ローカル原点基準で出力されていない(Door_Frameの配置位置が焼き込まれている)"

# --- 5. UV: 3つのFBXすべてにUVがあり、同じ規則(1UV=1m のボックス投影)で連続すること ---
uv_info = {}
for label, path in (("destruction", fbx_destruct), ("frame", fbx_frame), ("leaves", fbx_leaves)):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path)
    mo = [o for o in bpy.data.objects if o.type == 'MESH'][0]
    uvl = mo.data.uv_layers.active
    assert uvl is not None, f"{label}: FBXにUVがない"
    us = [d.uv[0] for d in uvl.data]
    vs = [d.uv[1] for d in uvl.data]
    uv_info[label] = (min(us), max(us), min(vs), max(vs))
    print(f"UV {label}: u {min(us):.2f}..{max(us):.2f}  v {min(vs):.2f}..{max(vs):.2f}  loops {len(us)}")
    # 1UV=1m: vの最大値は扉の高さ(m)程度、面ごとに0..1へ潰れていない(=実寸)こと
    assert max(vs) > 1.5, f"{label}: UVが実寸(1UV=1m)になっていない"
# 破壊メッシュと無傷の扉は同じ高さ範囲(=同じ座標系・同じ投影規則)
assert abs(uv_info["destruction"][3] - uv_info["leaves"][3]) < 0.05, "破壊メッシュと無傷の扉でUVの高さ範囲が食い違う"

print("BONES TEST DONE: PASS")
