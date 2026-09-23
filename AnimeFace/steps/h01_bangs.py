"""H01: 前髪（バング）の大ラフモデリング（3回目の作り直し）。

ユーザー指摘（2回目）:
  1. Mirrorモディファイアを使うのがそもそもおかしい → 髪は左右完全対称ではない（下絵も微妙に非対称）。
     Mirrorモディファイアは使わず、全幅を直接作る（中心のクリッピングによる不自然な折れ目も無くなる）
  2. 動画では髪は1枚の面でなく「房」の集まりで、緩やかなカーブ。ギザギザにしない
     → 房ごとに、根元は隣の房と重なるくらい太く、先端は尖らせず丸めに。中間を少し外側へ膨らませて
       緩やかな曲線にする（Alt+Sの膨らみに相当）
  3. ペラペラな質感 → ひし形断面できちんと厚みを持たせる（前回は板1枚+Solidifyで薄すぎた）
  4. Blenderの参考画像（REF_front/REF_side）が旧下絵（ハゲ頭）のままなので、髪型下絵に差し替える

測定（下絵、全幅。左右対称を仮定しない）:
  - 列ごとの毛→肌境界のピーク検出で、房の先端を全幅で測る（約18個）

設計:
  - 房ごとに、根元(額の上部, 行195)→先端(下絵の測定点)を6駅、ひし形断面（O/F/I/K）でつなぐ
  - 根元の半幅は隣の房との間隔より広く（重なって隙間なし）、先端は40%まで先細り（尖らせない）
  - 中間の駅で、皮膚の法線方向にわずかに追加で膨らませ、緩やかな曲線にする
  - クリースは付けない（Subdivisionだけで滑らかに）。Mirrorモディファイアは使わない

入力: out/face_s17e_gen.blend   出力: out/hair_h01_gen.blend, out/h01_report.json, out/h01_render_*.png
実行: blender --background --factory-startup --python steps/h01_bangs.py
"""
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402

STEP = "h01"
gates = C.Gates(STEP)

Z_TOP = (C.ROW0 - 195) * C.K
N_STATIONS = 6
HALF_W = 0.0280        # ユーザー手直しのサンプル房（幅約56-60mm）に合わせて拡大
TIP_FRAC = 0.70        # 先端でも根元の70%残す（尖らせず丸める。前回の40%はまだ尖りすぎだった）
H_FRONT = 0.0050
H_BACK = 0.0020
OFF_OUT = 0.0075
BULGE = 0.0060         # 中間の駅を追加で外側へ膨らませる量（緩やかな曲線）


def measure_lock_tips():
    img = bpy.data.images.load(str(C.BP_DIR / "chibi_hair_ref_front.png"))
    w, h = img.size
    arr = np.array(img.pixels[:], dtype="float32").reshape(h, w, 4)[::-1]
    px = arr[..., :3] * 255
    bpy.data.images.remove(img)

    def is_hairish(p):
        r, g, b = p
        return not (r > 235 and g > 210 and b > 195)

    us = list(range(260, 760))
    raw = []
    for u in us:
        col = px[:, u]
        trans = None
        for v in range(150, 480):
            if not is_hairish(col[v]):
                trans = v
                break
        raw.append(trans)
    raw = np.array([np.nan if r is None else float(r) for r in raw])
    nanmask = np.isnan(raw)
    idx = np.arange(len(raw))
    if nanmask.any():
        raw[nanmask] = np.interp(idx[nanmask], idx[~nanmask], raw[~nanmask])
    win = 5
    ker = np.ones(win) / win
    sm = np.convolve(np.pad(raw, win // 2, mode="edge"), ker, mode="valid")[:len(raw)]

    peaks = []
    cand = sm.copy()
    for _ in range(30):
        i = int(np.argmax(cand))
        if cand[i] < 0:
            break
        peaks.append(i)
        lo, hi = max(0, i - 22), min(len(cand), i + 22)
        cand[lo:hi] = -1
    peaks.sort()
    return [(us[i], float(sm[i])) for i in peaks]


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s17e_gen.blend"))
    for o in bpy.data.objects:
        if o.type == "MESH" and o.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

    # ---- Blenderの参考画像を、髪型下絵に差し替える（ユーザー指摘④）
    ref_swaps = {"REF_front": "chibi_hair_ref_front.png", "REF_side": "chibi_hair_ref_side.png", "REF_a45": "chibi_hair_ref_45.png"}
    n_swapped = 0
    for name, fname in ref_swaps.items():
        if name in bpy.data.objects:
            newimg = bpy.data.images.load(str(C.BP_DIR / fname), check_existing=True)
            bpy.data.objects[name].data = newimg
            n_swapped += 1
    gates.check("参考画像（REF_front/side/a45）を髪型下絵に差し替えた", n_swapped == 3, n_swapped)

    face = bpy.data.objects["Face"]
    me = face.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    skin_faces = [f for f in bm.faces if f.index < 460 and not all(v.index >= 463 for v in f.verts)]
    skin_polys = [[v.index for v in f.verts] for f in skin_faces]
    fverts = [tuple(v.co) for v in bm.verts]
    bm.normal_update()
    # Faceは半分（X<=0）のメッシュにMirrorモディファイアをかけたもの。今回は房にMirrorを使わず全幅を直接
    # 作るので、レイキャスト用のBVHも「Mirrorを自分で再現」して両側分（ミラーしたコピーを追加）にする
    # （半分のメッシュのままだと、X>0側の房が皮膚に全く届かない）
    n0 = len(fverts)
    fverts_full = fverts + [(-x, y, z) for (x, y, z) in fverts]
    skin_polys_full = skin_polys + [[i + n0 for i in reversed(poly)] for poly in skin_polys]
    bvh_skin = BVHTree.FromPolygons(fverts_full, skin_polys_full)

    def lift(x, z):
        hit = bvh_skin.ray_cast(Vector((x, -0.6, z)), Vector((0, 1, 0)), 2.0)
        return (hit[0], hit[1]) if hit[0] is not None else (None, None)

    tips_px = measure_lock_tips()
    gates.check(f"下絵で房の先端が全幅で測定できた（{len(tips_px)}個）", len(tips_px) >= 10, len(tips_px))

    img = bpy.data.images.load(str(C.BP_DIR / "chibi_hair_ref_front.png"))
    w, h = img.size
    px = np.array(img.pixels[:], dtype="float32").reshape(h, w, 4)[::-1]
    hair_color = tuple(float(c) for c in px[350, 200, :3])
    bpy.data.images.remove(img)
    gates.note("下絵の前髪の色（サンプル点 u=200,v=350）", tuple(round(c, 3) for c in hair_color))

    verts_all, faces_all = [], []
    n_locks = 0
    world_x = Vector((1, 0, 0))
    for u_tip, v_tip in tips_px:
        x_tip, z_tip = C.front_px_to_xz(u_tip, v_tip)
        x_top, z_top = x_tip, Z_TOP
        stations_hit = []
        for k in range(N_STATIONS):
            t = k / (N_STATIONS - 1)
            xk, zk = x_top + (x_tip - x_top) * t, z_top + (z_tip - z_top) * t
            pk, nk = lift(xk, zk)
            stations_hit.append((pk, nk))
        if any(p is None for p, n in stations_hit):
            continue
        base = len(verts_all)
        for k in range(N_STATIONS):
            t = k / (N_STATIONS - 1)
            center, nrm = stations_hit[k]
            nrm = nrm.normalized()
            bulge = BULGE * math_sin_pi(t)
            center = center + nrm * bulge
            w_dir = (world_x - nrm * world_x.dot(nrm))
            if w_dir.length < 1e-6:
                w_dir = Vector((1, 0, 0))
            w_dir.normalize()
            hw = HALF_W * (1 - (1 - TIP_FRAC) * t)
            O = center + w_dir * hw + nrm * OFF_OUT
            F_ = center + nrm * (OFF_OUT + H_FRONT)
            I_ = center - w_dir * hw + nrm * OFF_OUT
            K_ = center + nrm * (OFF_OUT - H_BACK)
            verts_all.extend([O, F_, I_, K_])
        for k in range(N_STATIONS - 1):
            b0, b1 = base + 4 * k, base + 4 * (k + 1)
            for j in range(4):
                faces_all.append([b0 + j, b0 + (j + 1) % 4, b1 + (j + 1) % 4, b1 + j])
        faces_all.append([base + 3, base + 2, base + 1, base])
        faces_all.append([len(verts_all) - 4, len(verts_all) - 3, len(verts_all) - 2, len(verts_all) - 1])
        n_locks += 1

    gates.check(f"下絵で測定した{len(tips_px)}房のうち、皮膚に届いた房でメッシュを作った", n_locks >= len(tips_px) - 2, n_locks)

    hair = bpy.data.meshes.new("Hair_Bangs")
    hair.from_pydata([tuple(v) for v in verts_all], [], faces_all)
    hair.update()
    obj = bpy.data.objects.new("Hair_Bangs", hair)
    bpy.context.collection.objects.link(obj)
    gates.check(f"Hair_Bangs: 頂点{n_locks}房×{N_STATIONS}駅×4、面が想定通り",
                len(hair.vertices) == n_locks * N_STATIONS * 4 and len(hair.polygons) == n_locks * ((N_STATIONS - 1) * 4 + 2))
    for p in hair.polygons:
        p.use_smooth = True

    sub = obj.modifiers.new("Subdivision", "SUBSURF")
    sub.levels = 1
    sub.render_levels = 2
    gates.check("Hair_Bangs: モディファイアは Subdivision(1/2)のみ（Mirrorは使わない）", [m.type for m in obj.modifiers] == ["SUBSURF"])

    mat = bpy.data.materials.new("HairBase")
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*hair_color, 1.0)
    obj.data.materials.append(mat)

    # ---- 検証
    deps = bpy.context.evaluated_depsgraph_get()
    ev_mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(deps))
    bvh_hair = BVHTree.FromPolygons([tuple(obj.matrix_world @ v.co) for v in ev_mesh.vertices], [list(p.vertices) for p in ev_mesh.polygons])
    fverts_all = [tuple(v.co) for v in me.vertices]
    n0f = len(fverts_all)
    fverts_all_full = fverts_all + [(-x, y, z) for (x, y, z) in fverts_all]
    fpolys_full = [list(p.vertices) for p in me.polygons] + [[i + n0f for i in reversed(list(p.vertices))] for p in me.polygons]
    bvh_face_all = BVHTree.FromPolygons(fverts_all_full, fpolys_full)
    hit_face = bvh_hair.overlap(bvh_face_all)
    gates.check("Hair_Bangs（モディファイア適用後）: 顔と交差していない", len(hit_face) == 0, len(hit_face))
    eye = bpy.data.objects["Eye"]
    ev_full = [tuple(eye.matrix_world @ v.co) for v in eye.data.vertices]
    n0e = len(ev_full)
    ev_full2 = ev_full + [(-x, y, z) for (x, y, z) in ev_full]
    ep_full = [list(p.vertices) for p in eye.data.polygons] + [[i + n0e for i in reversed(list(p.vertices))] for p in eye.data.polygons]
    bvh_eye = BVHTree.FromPolygons(ev_full2, ep_full)
    hit_eye = bvh_hair.overlap(bvh_eye)
    gates.check("Hair_Bangs（モディファイア適用後）: 黒目と交差していない", len(hit_eye) == 0, len(hit_eye))
    bpy.data.meshes.remove(ev_mesh)

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "hair_h01_gen.blend"), compress=False)

    # ---- レビュー用レンダリング
    for m in bpy.data.materials:
        if m.use_nodes:
            b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
            if b:
                b.inputs["Roughness"].default_value = 0.9
                b.inputs["Specular IOR Level"].default_value = 0.05
    scene = bpy.context.scene
    world = bpy.data.worlds.new("ReviewWorld")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.9, 0.9, 0.9, 1.0)
    scene.world = world
    sun = bpy.data.lights.new("ReviewSun", type='SUN')
    sun.energy = 1.5
    sun_obj = bpy.data.objects.new("ReviewSun", sun)
    sun_obj.rotation_euler = (0.6, 0.0, 0.0)
    scene.collection.objects.link(sun_obj)
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    keep = {"Face", "Eye", "Eyebrow", "DoubleLid", "Eyelash.001", "Eyelash.002", "Eyelash.003", "Hair_Bangs"}
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.hide_render = o.name not in keep
    for camname, out_name in [("CAM_front", "h01_render_front.png"), ("CAM_a45", "h01_render_45.png"), ("CAM_side", "h01_render_side.png")]:
        scene.camera = bpy.data.objects[camname]
        scene.render.filepath = str(C.OUT / out_name)
        bpy.ops.render.render(write_still=True)

    gates.finish()


def math_sin_pi(t):
    import math
    return math.sin(math.pi * t)


main()
