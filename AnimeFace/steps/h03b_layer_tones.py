"""H03b: 層ごとの色差（奥・下に隠れた面ほど暗く）

入力: out/teacher_ac_merged_h03.blend（H03 の UV＋テクスチャ）
方法: 髪の各ベース面について、外向きの円錐 9 本のレイを他の房へ飛ばし、当たった割合(AO)を出す。
      外向きの面の平均 AO を房ごとに出し、3 段階（0=そのまま / 1=やや暗 / 2=暗）に分ける（面ごとだと低ポリで
      四角いパッチになるため、房単位）。房の全面の UV を縦 3 帯のアトラスの該当帯へ移す。
      アトラス = H03 の画像 ×(1, 影1, 影2)。マテリアルは 1 つのまま（Unity では 1 枚の画像）。
      頭の中心へ向いた面(内向き)は最も暗い帯。
モディファイアは触らない。ポーズは評価のためだけに REST にして、保存前に戻す。
出力: out/teacher_ac_merged_h03b.blend, out/hair_tex_h03b.png (2048x3072)
"""
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.common import Gates

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "out" / "teacher_ac_merged_h03.blend"
DST = ROOT / "out" / "teacher_ac_merged_h03b.blend"
PNG = ROOT / "out" / "hair_tex_h03b.png"
G = Gates("h03b_layer_tones")

CENTER = Vector((0.0, 0.0, 0.06))
AO_T1, AO_T2 = 0.30, 0.55          # 房ごとの平均 AO がこれ以上で 影1 / 影2
RAY_LEN, RAY_OFF, CONE_DEG = 0.06, 0.002, 12.0
TINT = [np.array((1.0, 1.0, 1.0)), np.array((0.84, 0.79, 0.80)), np.array((0.66, 0.60, 0.64))]

bpy.ops.wm.open_mainfile(filepath=str(SRC))
hair = [o for o in bpy.data.objects if o.name.startswith(("Hair_Back", "Hair_Bangs"))]
arm = bpy.data.objects["Armature_Teacher"]
pose_before = arm.data.pose_position
arm.data.pose_position = "REST"
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
mods_before = {o.name: [(m.type, m.name) for m in o.modifiers] for o in hair}

# ---- 評価後のワールド形状で BVH（オブジェクトごと） -------------------------
bvh = {}
for o in hair:
    ev = o.evaluated_get(dg)
    me = ev.to_mesh()
    vs = [ev.matrix_world @ v.co for v in me.vertices]
    bvh[o.name] = BVHTree.FromPolygons(vs, [tuple(p.vertices) for p in me.polygons], epsilon=0.0)
    ev.to_mesh_clear()


def cone_dirs(d0):
    t = Vector((0, 0, 1)) if abs(d0.z) < 0.9 else Vector((1, 0, 0))
    a = d0.cross(t).normalized(); b = d0.cross(a).normalized()
    out = [d0]
    s, c = math.sin(math.radians(CONE_DEG)), math.cos(math.radians(CONE_DEG))
    for k in range(8):
        th = 2 * math.pi * k / 8
        out.append((d0 * c + (a * math.cos(th) + b * math.sin(th)) * s).normalized())
    return out


def occluded(o_self, origin, d):
    for name, t in bvh.items():
        if name == o_self:
            continue
        if t.ray_cast(origin, d, RAY_LEN)[0] is not None:
            return True
    return False


# ---- 面ごとの AO → 段階 -----------------------------------------------------
tone_of = {}          # (obj name, poly index) -> 0/1/2
ao_stat = {}
for o in hair:
    mw = o.matrix_world
    m3 = mw.to_3x3()
    me = o.data
    aos = []
    for p in me.polygons:
        c = mw @ p.center
        n = (m3 @ p.normal).normalized()
        r = (c - CENTER).normalized()
        if n.dot(r) < -0.2:
            continue                                  # 頭側を向いた面は平均に入れない
        d0 = (n + r).normalized() if n.dot(r) >= 0 else r
        dirs = cone_dirs(d0)
        hit = sum(occluded(o.name, c + d * RAY_OFF, d) for d in dirs)
        ao = hit / len(dirs)
        aos.append(ao)
    ao_stat[o.name] = sum(aos) / max(1, len(aos))
    t = 2 if ao_stat[o.name] >= AO_T2 else (1 if ao_stat[o.name] >= AO_T1 else 0)
    for p in me.polygons:
        tone_of[(o.name, p.index)] = t

cnt = [sum(1 for v in tone_of.values() if v == t) for t in range(3)]
tot = sum(cnt)
G.check("全面に段階を付与", tot == sum(len(o.data.polygons) for o in hair), f"{tot}面")
G.check("3 段階すべてに面がある（各 8% 以上）", all(c / tot >= 0.08 for c in cnt), f"0:{cnt[0]} 1:{cnt[1]} 2:{cnt[2]}")
G.note("オブジェクトごとの平均AO(小=露出)", {k: round(v, 2) for k, v in sorted(ao_stat.items(), key=lambda x: x[1])})

# ---- UV を帯へ移す（V' = (段階 + V) / 3） -----------------------------------
for o in hair:
    me = o.data
    uv = me.uv_layers.active.data
    for p in me.polygons:
        t = tone_of[(o.name, p.index)]
        for li in p.loop_indices:
            u, v = uv[li].uv
            assert -1e-6 <= v <= 1 + 1e-6
            uv[li].uv = (u, (t + v) / 3.0)

# ---- アトラス画像 -----------------------------------------------------------
old = bpy.data.images["HairTex_H03"]
W, H = old.size
a = np.array(old.pixels[:], dtype=np.float32).reshape(H, W, 4)
bands = []
for t in range(3):
    b = a.copy()
    lin = b[..., :3]
    # 画像は sRGB 値を入れて出している(H03)ので、ここも sRGB 値へ色を掛ける
    b[..., :3] = np.clip(lin * TINT[t].astype(np.float32), 0, 1)
    bands.append(b)
atlas = np.concatenate(bands, axis=0)          # 行0=V'0=段階0の毛先
img = bpy.data.images.new("HairTex_H03b", W, 3 * H, alpha=True)
img.colorspace_settings.name = "sRGB"
img.pixels.foreach_set(atlas.ravel())
img.filepath_raw = str(PNG)
img.file_format = "PNG"
img.save()
img.pack()

nt = bpy.data.materials["HairBase"].node_tree
tex = nt.nodes["HairTexNode"]
tex.image = img
bpy.data.images.remove(old)
arm.data.pose_position = pose_before
bpy.ops.wm.save_as_mainfile(filepath=str(DST))

# ---- 検証 ------------------------------------------------------------------
chk = bpy.data.images.load(str(PNG), check_existing=False)
arr = np.array(chk.pixels[:], dtype=np.float32).reshape(3 * H, W, 4)
means = [float(arr[t * H:(t + 1) * H, :, :3].mean()) for t in range(3)]
G.check("アトラス 2048x3072・32bit・パック済み", tuple(img.size) == (W, 3 * H) and img.depth == 32 and img.packed_file is not None,
        f"{tuple(img.size)}")
G.check("帯の明るさ 0 > 1 > 2", means[0] > means[1] > means[2] > 0.05, [round(m, 3) for m in means])
allv = [l.uv[1] for o in hair for l in o.data.uv_layers.active.data]
G.check("V' が [0,1] 内", min(allv) >= -1e-6 and max(allv) <= 1 + 1e-6, f"{min(allv):.3f}〜{max(allv):.3f}")
G.check("各面の V' が 1 つの帯内に収まる", all(
    int(min(o.data.uv_layers.active.data[li].uv[1] for li in p.loop_indices) * 3 + 1e-6)
    == int(max(o.data.uv_layers.active.data[li].uv[1] for li in p.loop_indices) * 3 - 1e-6)
    for o in hair for p in o.data.polygons))
G.check("マテリアルは HairBase の1つ・画像は HairTex_H03b のみ（旧画像を削除）",
        [i.name for i in bpy.data.images if i.name.startswith("HairTex")] == ["HairTex_H03b"]
        and tex.image.name == "HairTex_H03b")
G.check("髪モディファイアの構成が不変", all([(m.type, m.name) for m in o.modifiers] == mods_before[o.name] for o in hair))
G.check("ポーズ設定を元に戻して保存", arm.data.pose_position == pose_before, pose_before)
G.finish()
