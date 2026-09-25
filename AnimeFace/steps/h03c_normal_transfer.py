"""H03c: 髪の法線を「頭＋首の筒」形状から転写（房ごとの陰影のゴツゴツを弱め、面の流れをなだらかにする）

入力: out/teacher_ac_merged_h03b.blend
方法: 頭の楕円体（上半分）＋垂直の筒（下）のプロキシ Hair_NormalProxy を作る（頭の位置に追従するよう
      Head 100%＋Armature を付け、ビューポートでは非表示・レンダー除外）。
      髪 18 個に Data Transfer モディファイア(Custom Normal, POLYINTERP_NEAREST, Mix 1.0（中間値は標準シェーダーで斑点が出る）)を Armature の直前に追加。
      Apply はしない。プロキシは Unity 書き出し時は除外すること。
出力: out/teacher_ac_merged_h03c.blend
"""
import math
import sys
from pathlib import Path

import bpy
import numpy as np
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.common import Gates

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "out" / "teacher_ac_merged_h03b.blend"
DST = ROOT / "out" / "teacher_ac_merged_h03c.blend"
G = Gates("h03c_normal_transfer")

MIX = 1.0
N_AZ, N_CAP, N_TUBE = 32, 10, 8
ZC = 0.06                                   # 頭の中心 Z (CENTER と同じ)

bpy.ops.wm.open_mainfile(filepath=str(SRC))
hair = [o for o in bpy.data.objects if o.name.startswith(("Hair_Back", "Hair_Bangs"))]
arm = bpy.data.objects["Armature_Teacher"]
pose_before = arm.data.pose_position
arm.data.pose_position = "REST"
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
mods_before = {o.name: [(m.type, m.name) for m in o.modifiers] for o in hair}

# ---- 評価後の髪のワールド範囲（頭の部分 z>=ZC で楕円体、全体の最低 z で筒の下端） ----
pts = []
for o in hair:
    ev = o.evaluated_get(dg); me = ev.to_mesh()
    pts += [tuple(ev.matrix_world @ v.co) for v in me.vertices]
    ev.to_mesh_clear()
P = np.array(pts)
head = P[P[:, 2] >= ZC]
rx = float(np.abs(head[:, 0]).max())
cy = float((head[:, 1].max() + head[:, 1].min()) / 2)
ry = float((head[:, 1].max() - head[:, 1].min()) / 2)
z_top = float(P[:, 2].max()); z_bot = float(P[:, 2].min())
rz = z_top - ZC
G.note("プロキシ寸法(m)", f"rx={rx:.3f} ry={ry:.3f} cy={cy:.3f} rz={rz:.3f} 下端z={z_bot:.3f}")

# ---- プロキシ生成: 頭頂→赤道(楕円体)→筒→下端(閉じる)。外向き法線 --------------
bm = bmesh.new()
rings = []
top = bm.verts.new((0, cy, z_top))
for i in range(1, N_CAP + 1):                       # 赤道(i=N_CAP)まで
    phi = (math.pi / 2) * i / N_CAP
    z, s = ZC + rz * math.cos(phi), math.sin(phi)
    rings.append([bm.verts.new((rx * s * math.sin(2 * math.pi * k / N_AZ), cy - ry * s * math.cos(2 * math.pi * k / N_AZ), z))
                  for k in range(N_AZ)])
for j in range(1, N_TUBE + 1):
    z = ZC + (z_bot - ZC) * j / N_TUBE
    rings.append([bm.verts.new((rx * math.sin(2 * math.pi * k / N_AZ), cy - ry * math.cos(2 * math.pi * k / N_AZ), z))
                  for k in range(N_AZ)])
bot = bm.verts.new((0, cy, z_bot))
for k in range(N_AZ):
    bm.faces.new((top, rings[0][k], rings[0][(k + 1) % N_AZ]))
for a, b in zip(rings[:-1], rings[1:]):
    for k in range(N_AZ):
        bm.faces.new((a[k], b[k], b[(k + 1) % N_AZ], a[(k + 1) % N_AZ]))
for k in range(N_AZ):
    bm.faces.new((rings[-1][k], bot, rings[-1][(k + 1) % N_AZ]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new("Hair_NormalProxy")
bm.to_mesh(me); bm.free()
proxy = bpy.data.objects.new("Hair_NormalProxy", me)
guides = bpy.data.collections["Guides"]
guides.objects.link(proxy)
proxy.display_type = "WIRE"
vg = proxy.vertex_groups.new(name="Head")
vg.add(list(range(len(me.vertices))), 1.0, "REPLACE")
am = proxy.modifiers.new("Armature", "ARMATURE"); am.object = arm; am.use_vertex_groups = True
proxy.hide_render = True
bpy.context.view_layer.update()
proxy.hide_set(True)          # 目のアイコンで非表示（評価は残る）

# 外向き法線の確認（凸形状なので、各面で 法線・(面の重心 - 内部の点) > 0）
inner = Vector((0, cy, ZC))
out_ok = all(p.normal.dot(p.center - inner) > 0 for p in me.polygons)
G.check("プロキシの面が外向き", out_ok, f"{len(me.vertices)}頂点/{len(me.polygons)}面")

# ---- 転写前の評価（プロキシ最寄り面の法線とのズレ） -----------------------------
pv = [proxy.matrix_world @ v.co for v in me.vertices]
pbvh = BVHTree.FromPolygons(pv, [tuple(p.vertices) for p in me.polygons])


def mean_angle(hair_objs):
    dg2 = bpy.context.evaluated_depsgraph_get(); dg2.update()
    angs = []
    for o in hair_objs:
        ev = o.evaluated_get(dg2); m = ev.to_mesh()
        m3 = ev.matrix_world.to_3x3()
        cn = m.corner_normals
        for li, l in enumerate(m.loops):
            pw = ev.matrix_world @ m.vertices[l.vertex_index].co
            loc, nor, idx, dist = pbvh.find_nearest(pw)
            if nor is None:
                continue
            n = (m3 @ Vector(cn[li].vector)).normalized()
            angs.append(math.degrees(n.angle(nor)))
        ev.to_mesh_clear()
    return float(np.mean(angs)), len(angs)


before, n_l = mean_angle(hair)

# ---- Data Transfer を Armature の直前に追加 -----------------------------------
for o in hair:
    m = o.modifiers.new("HairNormalTransfer", "DATA_TRANSFER")
    m.object = proxy
    m.use_loop_data = True
    m.data_types_loops = {"CUSTOM_NORMAL"}
    m.loop_mapping = "POLYINTERP_NEAREST"
    m.mix_mode = "MIX"
    m.mix_factor = MIX
    o.modifiers.move(len(o.modifiers) - 1, len(o.modifiers) - 2)      # Armature の直前へ
after, _ = mean_angle(hair)

G.check("全 18 個で Armature の直前に Data Transfer（最後は ARMATURE）",
        all(o.modifiers[-1].type == "ARMATURE" and o.modifiers[-2].name == "HairNormalTransfer" for o in hair))
G.check("元のモディファイア構成は保たれる（追加分を除く）",
        all([(m.type, m.name) for m in o.modifiers if m.name != "HairNormalTransfer"] == mods_before[o.name] for o in hair))
G.check("法線がプロキシへ近づいた（平均角度が 25% 以上減少）", after <= before * 0.75,
        f"{before:.1f}° → {after:.1f}°（{n_l}ループ）")
G.check("プロキシに Head 100%＋Armature、非表示・レンダー除外",
        proxy.hide_render and proxy.hide_get() and proxy.modifiers[-1].type == "ARMATURE" and len(proxy.vertex_groups) == 1)

arm.data.pose_position = pose_before
G.check("ポーズ設定を元に戻して保存", arm.data.pose_position == pose_before, pose_before)
bpy.ops.wm.save_as_mainfile(filepath=str(DST))
G.finish()
