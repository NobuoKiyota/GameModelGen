"""H03: 髪の UV 展開（頭の中心からの球面投影）＋髪テクスチャ（Unity 向け・茶色系）

入力: out/teacher_ac_merged_face_hair.blend（顔・髪=①、他=②）
UV : U = 方位角（正面=0.5）, V = 頭の中心からの極角（頭頂=1 → 毛先=0）。全房で高さが揃うので
     天使の輪・根元→毛先のグラデーション・毛流れの筋を 1 枚の画像で全房にまたがって描ける。
     面ごとに方位角を巻き取る（頂点ごとではない）。U は [0,1] の外へ出る面がある → 画像は REPEAT。
テクスチャ: 2048x1024。根元=濃、毛先=やや明るい、天使の輪、縦の筋（U 方向に周期的）。
モディファイアは触らない（Apply しない）。UV とマテリアルの接続、画像の追加のみ。
出力: out/teacher_ac_merged_h03.blend, out/hair_tex_h03.png
"""
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.common import Gates

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "out" / "teacher_ac_merged_face_hair.blend"
DST = ROOT / "out" / "teacher_ac_merged_h03.blend"
PNG = ROOT / "out" / "hair_tex_h03.png"
G = Gates("h03_hair_uv_texture")

CENTER = Vector((0.0, 0.0, 0.06))
W, H = 2048, 1024
# 色 (sRGB 0-255)。茶色系・仮。ここを変えれば色味が変わる
ROOT_C = np.array((116, 80, 58), float)     # 根元（頭頂側）
MID_C = np.array((166, 120, 86), float)
TIP_C = np.array((190, 142, 104), float)    # 毛先
RING_C = np.array((232, 198, 164), float)   # 天使の輪
RING_DEG, RING_HALF_DEG = 60.0, 4.5

bpy.ops.wm.open_mainfile(filepath=str(SRC))
hair = [o for o in bpy.data.objects if o.name.startswith(("Hair_Back", "Hair_Bangs"))]
G.check("髪オブジェクト 18", len(hair) == 18, len(hair))
mods_before = {o.name: [(m.type, m.name) for m in o.modifiers] for o in hair}


def sph(p):
    d = p - CENTER
    rho = math.hypot(d.x, d.y)
    az = math.atan2(d.x, -d.y)          # 正面(-Y)=0, +X 側が正
    phi = math.atan2(rho, d.z)          # 頭頂=0
    return az, phi, rho


# ---- 極角の範囲（全髪の頂点から）→ V を決める --------------------------------
phis = []
for o in hair:
    mw = o.matrix_world
    for v in o.data.vertices:
        phis.append(sph(mw @ v.co)[1])
PHI_MIN = min(phis) - 0.02
PHI_MAX = max(phis) + 0.02
G.note("極角の範囲(度)", f"{math.degrees(PHI_MIN):.1f}〜{math.degrees(PHI_MAX):.1f}")
v_of = lambda phi: 1.0 - (phi - PHI_MIN) / (PHI_MAX - PHI_MIN)

# ---- UV（面ごとに方位角を巻き取る） -----------------------------------------
bad_span, n_faces, n_out = 0, 0, 0
max_span = 0.0
for o in hair:
    me = o.data
    uvl = me.uv_layers.get("UVMap") or (me.uv_layers[0] if len(me.uv_layers) else me.uv_layers.new(name="UVMap"))
    me.uv_layers.active = uvl
    mw = o.matrix_world
    wp = [mw @ v.co for v in me.vertices]
    for p in me.polygons:
        n_faces += 1
        cen = sum((wp[i] for i in p.vertices), Vector()) / len(p.vertices)
        ref = sph(cen)[0] / (2 * math.pi) + 0.5
        shift = -math.floor(ref)
        us = []
        for li, vi in zip(p.loop_indices, p.vertices):
            az, phi, rho = sph(wp[vi])
            u = az / (2 * math.pi) + 0.5 if rho > 1e-3 else ref
            while u - ref > 0.5:
                u -= 1.0
            while u - ref < -0.5:
                u += 1.0
            u += shift
            uvl.data[li].uv = (u, v_of(phi))
            us.append(u)
        span = max(us) - min(us)
        max_span = max(max_span, span)
        bad_span += span > 0.45
        n_out += (min(us) < 0.0 or max(us) > 1.0)

G.check("全面に UV（ループ数=UVデータ数）", all(len(o.data.uv_layers.active.data) == len(o.data.loops) for o in hair))
G.check("面内の U の幅が 0.45 未満（巻き取り失敗なし）", bad_span == 0, f"最大{max_span:.3f} 超過{bad_span}/{n_faces}面")
allv = np.array([[l.uv[1] for l in o.data.uv_layers.active.data] for o in hair], dtype=object)
vmin = min(min(a) for a in allv); vmax = max(max(a) for a in allv)
G.check("V が [0,1] 内", -1e-6 <= vmin and vmax <= 1 + 1e-6, f"{vmin:.3f}〜{vmax:.3f}")
G.note("U が [0,1] の外へ出る面（REPEAT で解決）", f"{n_out}/{n_faces}")


# ---- テクスチャ -------------------------------------------------------------
def pnoise(cu, cv, seed):
    """U 方向に周期的な value noise (H,W) 0..1"""
    rng = np.random.default_rng(seed)
    g = rng.random((cv + 1, cu))
    x = np.arange(W)[None, :] / W * cu
    y = np.arange(H)[:, None] / H * cv
    ix = np.floor(x).astype(int); iy = np.floor(y).astype(int)
    tx = x - ix; ty = y - iy
    tx = tx * tx * (3 - 2 * tx); ty = ty * ty * (3 - 2 * ty)
    ix0 = ix % cu; ix1 = (ix + 1) % cu
    a = g[iy, ix0]; b = g[iy, ix1]; c = g[iy + 1, ix0]; d = g[iy + 1, ix1]
    return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty


vv = (np.arange(H) + 0.5) / H                      # 行0=V0(毛先)
vgrid = np.repeat(vv[:, None], W, axis=1)
# 根元(v=1)→中間(v=0.55)→毛先(v=0)
t_root = np.clip((vgrid - 0.55) / 0.45, 0, 1)[..., None]
t_tip = np.clip((0.55 - vgrid) / 0.55, 0, 1)[..., None]
col = MID_C * (1 - t_root) * (1 - t_tip) + ROOT_C * t_root + TIP_C * t_tip

# 縦の筋（明暗の細い流れ）
streak = 0.55 * pnoise(150, 3, 1) + 0.30 * pnoise(48, 2, 2) + 0.15 * pnoise(400, 5, 3)
col = col * (1 + 0.09 * (streak[..., None] - 0.5))
fine = pnoise(520, 8, 4)                            # 細い暗線（毛の束の境目）
col = col * (1 - 0.04 * np.clip((0.30 - fine) / 0.30, 0, 1)[..., None])

# 天使の輪（V から極角へ戻して中心±幅）。縁は U 方向のノイズで揺らして途切れさせる
phi_grid = PHI_MIN + (1 - vgrid) * (PHI_MAX - PHI_MIN)
edge = (pnoise(14, 1, 5)[0:1, :] - 0.5) * math.radians(3.0)     # (1,W) 行に依らない揺れ
dist = np.abs(phi_grid - math.radians(RING_DEG) - edge)
half = math.radians(RING_HALF_DEG)
band = np.clip((half - dist) / (half * 0.9), 0, 1)
band = band * band * (3 - 2 * band)
band *= np.clip(0.75 + 0.5 * pnoise(18, 1, 6)[0:1, :], 0, 1)    # 所々弱める
col = col * (1 - 0.42 * band[..., None]) + RING_C * 0.42 * band[..., None]

rgb = np.clip(col, 0, 255) / 255.0
rgba = np.concatenate([rgb, np.ones((H, W, 1))], axis=2)

if "HairTex_H03" in bpy.data.images:
    bpy.data.images.remove(bpy.data.images["HairTex_H03"])
img = bpy.data.images.new("HairTex_H03", W, H, alpha=True)
img.colorspace_settings.name = "sRGB"
# Blender は sRGB→リニアの変換を保存時に行うので、ここで sRGB 値を入れて PNG に出す
img.pixels.foreach_set(rgba.astype(np.float32).ravel())
img.filepath_raw = str(PNG)
img.file_format = "PNG"
img.save()
img.pack()

# ---- マテリアル接続 ---------------------------------------------------------
mat = bpy.data.materials["HairBase"]
nt = mat.node_tree
bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
tex = nt.nodes.new("ShaderNodeTexImage")
tex.name = "HairTexNode"; tex.image = img
tex.extension = "REPEAT"; tex.interpolation = "Linear"
tex.location = (bsdf.location.x - 400, bsdf.location.y)
nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
bpy.ops.wm.save_as_mainfile(filepath=str(DST))

# ---- 検証 ------------------------------------------------------------------
G.check("画像 2048x1024・32bit・パック済み", tuple(img.size) == (W, H) and img.depth == 32 and img.packed_file is not None,
        f"{tuple(img.size)} depth{img.depth}")
# PNG を読み直して確認（自分の配列ではなく保存物）
chk = bpy.data.images.load(str(PNG), check_existing=False)
arr = np.array(chk.pixels[:], dtype=np.float32).reshape(H, W, 4)
srgb = np.where(arr[..., :3] <= 0.0031308, arr[..., :3] * 12.92, 1.055 * np.power(arr[..., :3], 1 / 2.4) - 0.055)
mean_row = arr[..., :3].mean(axis=(1, 2))
G.check("PNG が一様でない（標準偏差 > 0.02）", float(arr[..., :3].std()) > 0.02, f"std={arr[..., :3].std():.3f}")
G.check("毛先(下)より根元(上)が暗い", mean_row[-40:].mean() < mean_row[:40].mean(),
        f"根元行{mean_row[-40:].mean():.3f} 毛先行{mean_row[:40].mean():.3f}")
v_ring = 1.0 - (math.radians(RING_DEG) - PHI_MIN) / (PHI_MAX - PHI_MIN)
row_ring = int(v_ring * H)
G.check("天使の輪の行が周囲より明るい", mean_row[row_ring] > mean_row[max(0, row_ring - 90)] + 0.02
        and mean_row[row_ring] > mean_row[min(H - 1, row_ring + 90)] + 0.02,
        f"輪{mean_row[row_ring]:.3f} 下{mean_row[max(0,row_ring-90)]:.3f} 上{mean_row[min(H-1,row_ring+90)]:.3f}")
G.check("左右端が繋がる（U 方向の周期性: 端の列差 < 内側の隣接列差の3倍）",
        float(np.abs(arr[:, 0, :3] - arr[:, -1, :3]).mean()) < 3 * float(np.abs(arr[:, 1000, :3] - arr[:, 1001, :3]).mean()) + 0.01)
G.check("髪モディファイアの構成が不変",
        all([(m.type, m.name) for m in o.modifiers] == mods_before[o.name] for o in hair))
G.check("Face 側のマテリアル・UV に触れていない", bpy.data.objects["Face"].data.uv_layers.active is not None
        and "HairBase" not in [s.material.name for s in bpy.data.objects["Face"].material_slots if s.material])
G.finish()
