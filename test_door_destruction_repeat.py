"""
回帰テスト: 同じBlenderセッション内で generate_door_destruction() を2回連続で呼んでも
（例: 生成→タイムラインをスクラブして確認→パラメータを変えてもう一度生成、という
実際の使い方をした場合でも）2回目が「衝撃フレーム以降だけ元の姿勢に固まって動かない」
不具合を再現しないことを確認する。

原因は cur_frame を scene.frame_current（呼び出し時点でユーザーが見ていた・スクラブした
フレーム）から取っていたこと。Rigid Body シミュレーションは point_cache.frame_start から
連続してステップしないと正しく評価されないため、frame_start以外の値から急に
frame_set() すると物理演算の評価結果が初期値のまま固まる。修正後は cur_frame を
常に point_cache.frame_start から取るようにしている。
"""
import bpy
import sys

addon_parent = r"z:\MeshCreator\blender_addons"
if addon_parent not in sys.path:
    sys.path.insert(0, addon_parent)

from procedural_rock_studio import rock_studio_addon
from procedural_rock_studio.generators import generate_procedural_prop_mesh
from procedural_rock_studio.generators.door_destruction_gen import generate_door_destruction

bpy.ops.wm.read_factory_settings(use_empty=True)
rock_studio_addon.register()

door_frame = generate_procedural_prop_mesh(
    context=bpy.context, target_obj=None, category="DOOR", name="RepDoor", seed=1,
    size_x=2.2, size_y=0.5, size_z=2.6,
    door_arch_style='ROMAN_ROUND', door_pillar_shape='SQUARE_PIER',
    door_pillar_width=0.42, door_column_height=1.7, door_has_keystone=True,
    door_strap_style='CROSS_Z', door_stud_pattern='GRID', door_handle_style='RING_PULL',
    door_has_hinges=True, door_has_edge_trim=True, door_edge_trim_width=0.05,
    door_wood_material='WEATHERED_OAK', door_iron_style='BLACK_FORGED',
    door_damage=0.35, door_weathering=0.55, door_moss_amount=0.20,
    door_open_angle=0.0, door_open_direction='OUTWARD', door_combine=False,
)
leaf_l, leaf_r = None, None
for c in door_frame.children:
    if c.name.endswith("_Leaf_L"):
        leaf_l = c
    elif c.name.endswith("_Leaf_R"):
        leaf_r = c


def check_and_report(combined_obj, label):
    scene = bpy.context.scene
    positions = []
    for f in (1, 3, 5, 7, 9, 15):
        scene.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        eo = combined_obj.evaluated_get(dg)
        em = eo.to_mesh()
        vlast = em.vertices[len(em.vertices) - 1].co.copy()
        positions.append((f, vlast))
        eo.to_mesh_clear()
    print(f"--- {label}: {combined_obj.name} ---")
    for f, v in positions:
        print(f"  frame={f:2d} vlast={v}")
    # frame5以降がframe1(basis)と同一のままなら「固まって動かない」不具合が再発している
    basis = positions[0][1]
    frozen_after_impact = all((p[1] - basis).length < 0.01 for p in positions[2:])
    if frozen_after_impact:
        print(f"  !!! REGRESSION DETECTED in {label}: fragments never move after the impact frame !!!")
    else:
        print(f"  OK: {label} fragments keep moving after the impact frame")
    return not frozen_after_impact


print("=== RUN 1 (fresh) ===")
combined1, action1 = generate_door_destruction(
    context=bpy.context, leaf_obj_l=leaf_l, leaf_obj_r=leaf_r, frame_obj=door_frame,
    shard_count=10, frame_count=20, sample_step=2, impact_strength=1.0, impact_frames=4,
    subdivide_cuts=1, seed=5, name="RepDoor_Destruction_Run1",
)
ok1 = check_and_report(combined1, "RUN1")

print("=== RUN 2 (same door, same session, after scrubbing the timeline like a real user would) ===")
# RUN1のcheck_and_report()がタイムラインを frame=15 までスクラブしたままなのが実際の
# 使用シナリオ（生成→確認→もう一度生成）を再現している
combined2, action2 = generate_door_destruction(
    context=bpy.context, leaf_obj_l=leaf_l, leaf_obj_r=leaf_r, frame_obj=door_frame,
    shard_count=10, frame_count=20, sample_step=2, impact_strength=1.0, impact_frames=4,
    subdivide_cuts=1, seed=5, name="RepDoor_Destruction_Run2",
)
ok2 = check_and_report(combined2, "RUN2")

print("REPEAT TEST DONE:", "PASS" if (ok1 and ok2) else "FAIL")
