"""H02: サイド〜後ろ髪の大ラフモデリング（H01の手作り版から学んだ手法の試し）。

H01で、人間が手作りした前髪（`hair_h01_human.blend`）が自動生成版より圧倒的に良かった。そこから学んだこと:
  - 房は「幅広で薄い長方形の断面（4頂点）×数駅」の細い箱に、Subdivision（レベル1）だけをかける。ひし形断面・多頂点は使わない
  - 全幅を直接作る（Mirrorは使わない）。オブジェクトの位置・回転・拡大は単位のまま
  - 房どうしは重ねて隙間を作らない

作り直し（2回目）でユーザー指摘「頭頂部が禿げている・変な隙間・毛先が丸い・ウェーブ感が足りない」に対応:
  - 頭の全方向から光線を飛ばし、髪に覆われない場所（禿げ）を数値で検出し、無くなるまで、頭の曲面に沿った房を足す
    （頭頂も、この隙間埋めの房で覆う。ゲート: 禿げの割合 < 2%）
  - 毛先は下絵通り尖らせる（先端の断面を極小に）。房の中心線にS字のウェーブ（左右・前後、房ごとに位相と振幅を変える）と、
    毛先の外向きの跳ね上げを付ける
  - 外形のはみ出しゲートは「頭の曲面で説明できない（頭から30mm以上離れている）はみ出し」だけを数える

設計（下絵から測る）:
  - 正面の髪の外形の半幅 X_out(z)（左端の非背景画素）と、側面の髪の後ろの外形 Y_back(z) を、行ごとに測る
  - 髪の外形を楕円の帯 (x, y) = (X_out(z)·sinθ, Y_back(z)·cosθ)（θ=0が真後ろ、±90°が真横）とみなし、
    θを一定間隔に振った主の房を、頭の上（Z=0.24）から先端（下絵の髪の下端付近）へ垂らす
  - 房の断面: 幅 W（外形の接線方向）×厚み T（外形の法線方向）の長方形
  - 頭・黒目と交差する房は、外形より外へ逃がす

入力: out/hair_h01_human.blend（ユーザー手作りの前髪を含む）  出力: out/hair_h02_gen.blend, out/h02_report.json, out/h02_render_*.png
実行: blender --background --factory-startup --python steps/h02_back_side_hair.py
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402

STEP = "h02"
gates = C.Gates(STEP)

THETAS = [-108, -88, -68, -48, -28, -9, 9, 28, 48, 68, 88, 108]
Z_TOP = 0.240
N_ST = 8
W = 0.088
T = 0.016
TIP_ROWS = [925, 975, 940, 985, 955, 990, 975, 945, 985, 935, 970, 930]
CENTER = Vector((0.0, 0.0, 0.06))
BALD_LIMIT = 0.02
MAX_FILL = 40


def load(name):
    im = bpy.data.images.load(str(C.BP_DIR / name))
    w, h = im.size
    a = np.array(im.pixels[:], dtype="float32").reshape(h, w, 4)[::-1][..., :3] * 255
    bpy.data.images.remove(im)
    return a


def envelopes():
    bg = np.array([205, 205, 205])
    f, s = load("chibi_hair_ref_front.png"), load("chibi_hair_ref_side.png")
    mf = np.abs(f - bg).sum(axis=2) > 60
    ms = np.abs(s - bg).sum(axis=2) > 60
    rows = np.arange(100, 990)
    xo, yb = [], []
    for v in rows:
        us = np.where(mf[v, :512])[0]
        xo.append((C.COL0 - us.min()) * C.K if len(us) else np.nan)
        us2 = np.where(ms[v, :])[0]
        yb.append((C.COL0 - us2.min()) * C.K if len(us2) else np.nan)
    xo, yb = np.array(xo), np.array(yb)
    for arr in (xo, yb):
        bad = np.isnan(arr)
        arr[bad] = np.interp(np.where(bad)[0], np.where(~bad)[0], arr[~bad])
    k = np.ones(15) / 15
    xo = np.convolve(np.pad(xo, 7, mode="edge"), k, mode="valid")
    yb = np.convolve(np.pad(yb, 7, mode="edge"), k, mode="valid")

    def X(z):
        v = C.ROW0 - z / C.K
        return float(np.interp(v, rows, xo))

    def Y(z):
        v = C.ROW0 - z / C.K
        return float(np.interp(v, rows, yb))
    return X, Y


def full_bvh(verts, polys):
    n0 = len(verts)
    v2 = list(verts) + [(-x, y, z) for (x, y, z) in verts]
    p2 = [list(p) for p in polys] + [[i + n0 for i in reversed(list(p))] for p in polys]
    return BVHTree.FromPolygons(v2, p2)


def smooth(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def make_box(cs, taus, nrms, ws, ts):
    """駅ごとの (中心, 幅方向, 厚み方向, 幅, 厚み) から、長方形断面×駅の箱を作る。法線は外向きに揃える。"""
    verts, faces = [], []
    for c, tau, nrm, w, t in zip(cs, taus, nrms, ws, ts):
        hw, ht = w / 2, t / 2
        verts += [c + tau * hw + nrm * ht, c - tau * hw + nrm * ht, c - tau * hw - nrm * ht, c + tau * hw - nrm * ht]
    n = len(cs)
    for j in range(n - 1):
        b0, b1 = 4 * j, 4 * (j + 1)
        for k in range(4):
            faces.append([b0 + k, b0 + (k + 1) % 4, b1 + (k + 1) % 4, b1 + k])
    faces.append([3, 2, 1, 0])
    faces.append([4 * (n - 1) + i for i in range(4)])
    cen = sum(verts, Vector()) / len(verts)
    s = 0.0
    for f in faces:
        pts = [verts[i] for i in f]
        nn = (pts[1] - pts[0]).cross(pts[2] - pts[0])
        s += nn.dot(sum(pts, Vector()) / 4 - cen)
    if s < 0:
        faces = [list(reversed(f)) for f in faces]
    return verts, faces


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "hair_h01_human.blend"))
    for o in bpy.data.objects:
        if o.type == "MESH" and o.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
    face, eye = bpy.data.objects["Face"], bpy.data.objects["Eye"]
    n_before = len(bpy.data.objects)
    X, Y = envelopes()

    bm = bmesh.new()
    bm.from_mesh(face.data)
    bm.faces.ensure_lookup_table()
    skin = [[v.index for v in f.verts] for f in bm.faces if f.index < 460 and not all(v.index >= 463 for v in f.verts)]
    fverts = [tuple(v.co) for v in bm.verts]
    bvh_head = full_bvh(fverts, skin)
    ev = [tuple(eye.matrix_world @ v.co) for v in eye.data.vertices]
    bvh_eye = full_bvh(ev, [list(p.vertices) for p in eye.data.polygons])

    mat = bpy.data.materials.get("HairBase") or bpy.data.materials.new("HairBase")
    hair_coll = bpy.data.collections.get("Hair") or bpy.data.collections.new("Hair")
    if hair_coll.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(hair_coll)

    def eval_hits(verts, faces):
        b = BVHTree.FromPolygons([tuple(v) for v in verts], faces)
        return len(b.overlap(bvh_head)), len(b.overlap(bvh_eye))

    def add_object(name, verts, faces):
        me = bpy.data.meshes.new(name)
        me.from_pydata([tuple(v) for v in verts], [], faces)
        me.update()
        for p in me.polygons:
            p.use_smooth = True
        o = bpy.data.objects.new(name, me)
        hair_coll.objects.link(o)
        sub = o.modifiers.new("Subdivision", "SUBSURF")
        sub.levels, sub.render_levels = 1, 2
        me.materials.append(mat)
        bpy.context.view_layer.update()   # 追加直後のオブジェクトが評価済みメッシュに反映されるよう更新（しないと、隙間埋めの房が禿げ判定に入らない）
        return o

    def build_main(i, theta_deg, tip_row, push):
        th = math.radians(theta_deg)
        z_tip = (C.ROW0 - tip_row) * C.K
        amp_a = 0.013 + 0.007 * ((i * 37) % 5) / 4
        amp_b = 0.007 + 0.004 * ((i * 53) % 5) / 4
        ph_a, ph_b = i * 1.31, i * 2.07 + 0.8
        cs, taus, nrms, ws, ts = [], [], [], [], []
        for j in range(N_ST):
            t = j / (N_ST - 1)
            z = Z_TOP + (z_tip - Z_TOP) * t
            xo, yb = X(z), Y(z)
            cx, cy = xo * math.sin(th), yb * math.cos(th)
            tx, ty = xo * math.cos(th), -yb * math.sin(th)
            nx, ny = yb * math.sin(th), xo * math.cos(th)
            tl, nl = math.hypot(tx, ty), math.hypot(nx, ny)
            tau, nrm = Vector((tx / tl, ty / tl, 0)), Vector((nx / nl, ny / nl, 0))
            amp = smooth(0.12, 0.55, t)
            wav_t = amp_a * amp * math.sin(2 * math.pi * 1.3 * t + ph_a)
            wav_n = -amp_b * amp * (1 + math.sin(2 * math.pi * 1.3 * t + ph_b)) / 2 * 2   # 外形より外へは出さない（内向きのウェーブ）
            flick = 0.010 * smooth(0.72, 1.0, t)
            sw = 1 - 0.25 * t if t < 0.7 else 0.825 - 0.705 * ((t - 0.7) / 0.3)
            st = 1 - 0.55 * t
            wd, th_ = W * sw, T * st
            push_t = push * (1 - smooth(0.35, 0.75, t))     # 頭と交差しやすいのは上側なので、逃がし量は毛先に向けて0へ（外形から大きくはみ出さない）
            cs.append(Vector((cx, cy, z)) + nrm * (push_t - th_ / 2 + wav_n + flick) + tau * wav_t)
            taus.append(tau)
            nrms.append(nrm)
            ws.append(wd)
            ts.append(th_)
        return make_box(cs, taus, nrms, ws, ts)

    made, report = [], []
    for i, (th, tr) in enumerate(zip(THETAS, TIP_ROWS)):
        push = 0.0
        for _ in range(24):
            verts, faces = build_main(i, th, tr, push)
            hh, he = eval_hits(verts, faces)
            if hh == 0 and he == 0:
                break
            push += 0.004
        report.append((th, round(push, 3), hh, he))
        made.append(add_object(f"Hair_Back.{i + 1:03d}", verts, faces))
    gates.note("主の房 (θ°, 外向き押し出し[m], 頭との交差, 黒目との交差)", report)

    # ---- 頭の全方向から光線を飛ばして、髪に覆われない場所（禿げ）を数える
    n_dirs = 6000
    idx = np.arange(n_dirs) + 0.5
    phi_g = math.pi * (1 + 5 ** 0.5) * idx
    cosg = 1 - 2 * idx / n_dirs
    sample_pts = []
    for c, p_ in zip(cosg, phi_g):
        sn = math.sqrt(max(0.0, 1 - c * c))
        d = Vector((sn * math.cos(p_), sn * math.sin(p_), c))
        hit = bvh_head.ray_cast(CENTER, d, 1.0)
        if hit[0] is None:
            continue
        p = hit[0]
        if (p.z > 0.14) or (p.y > -0.02 and p.z > -0.12):
            sample_pts.append((d, p, hit[1]))

    def hair_bvh():
        deps = bpy.context.evaluated_depsgraph_get()
        deps.update()
        vs, ps = [], []
        for o in bpy.data.objects:
            if o.type != "MESH" or not o.name.startswith("Hair_") or o.name == "Hair_Bangs" or o.hide_get():
                continue
            em = bpy.data.meshes.new_from_object(o.evaluated_get(deps))
            base = len(vs)
            vs += [tuple(o.matrix_world @ v.co) for v in em.vertices]
            ps += [[base + i for i in p.vertices] for p in em.polygons]
            bpy.data.meshes.remove(em)
        return BVHTree.FromPolygons(vs, ps)

    def find_bald():
        hb = hair_bvh()
        return [(d, p, n) for d, p, n in sample_pts if hb.ray_cast(p + d * 0.0005, d, 0.15)[0] is None]

    bald = find_bald()
    frac0 = len(bald) / max(len(sample_pts), 1)
    gates.note("隙間埋め前: 髪に覆われない（禿げの）割合", f"{frac0 * 100:.1f}%（サンプル{len(sample_pts)}点）")

    fills = []
    skip = []

    def near_skip(p_):
        return any((p_ - q).length < 0.03 for q in skip)

    def build_fill(gamma0, phi0, extra):
        cs, taus, nrms, ws, ts = [], [], [], [], []
        m = 7
        for j in range(m):
            t = j / (m - 1)
            gamma = min(gamma0 - math.radians(16) + math.radians(62) * t, math.radians(112))   # 負の角度＝頭頂を越えて反対側へ
            dj = Vector((math.sin(gamma) * math.cos(phi0), math.sin(gamma) * math.sin(phi0), math.cos(gamma)))
            hit = bvh_head.ray_cast(CENTER, dj, 1.0)
            if hit[0] is None:
                return None
            pj, nj = hit[0], hit[1].normalized()
            vol = 0.010 + (0.006 if gamma0 < 0.6 else 0.0) + extra
            wav = 0.010 * smooth(0.1, 0.6, t) * math.sin(2 * math.pi * 1.2 * t + len(fills) * 1.9)
            tau = Vector((-math.sin(phi0), math.cos(phi0), 0))
            tau = (tau - nj * tau.dot(nj)).normalized()
            sw = 1 - 0.2 * t if t < 0.75 else 0.8 - 0.68 * ((t - 0.75) / 0.25)
            cs.append(pj + nj * (0.007 + vol) + tau * wav)
            taus.append(tau)
            nrms.append(nj)
            ws.append(0.092 * sw)
            ts.append(0.014 * (1 - 0.4 * t))
        return make_box(cs, taus, nrms, ws, ts)

    while len(bald) / max(len(sample_pts), 1) >= BALD_LIMIT and len(fills) < MAX_FILL:
        cand = [b for b in bald if not near_skip(b[1])]
        if not cand:
            break
        d0, p0, n0 = max(cand, key=lambda b: b[1].z) if len(fills) % 2 == 0 else cand[len(cand) // 2]
        gamma0 = math.acos(max(-1, min(1, d0.z)))
        phi0 = math.atan2(d0.y, d0.x)
        res = None
        for extra in (0.0, 0.004, 0.008, 0.012, 0.016, 0.022):
            r = build_fill(gamma0, phi0, extra)
            if r is None:
                break
            hh, he = eval_hits(*r)
            if hh == 0 and he == 0:
                res = (r, 0, 0)
                break
            res = (r, hh, he)
        if res is None:
            skip.append(p0)
            continue
        (verts, faces), hh, he = res
        n_before_bald = len(bald)
        add_object(f"Hair_Fill.{len(fills) + 1:03d}", verts, faces)
        fills.append((round(math.degrees(gamma0)), round(math.degrees(phi0)), hh, he))
        bald = find_bald()
        if len(bald) >= n_before_bald:
            skip.append(p0)
    frac1 = len(bald) / max(len(sample_pts), 1)
    gates.note("隙間埋めの房 (極角°, 方位角°, 頭との交差, 黒目との交差)", fills)
    gates.check("隙間埋め後: 髪に覆われない割合が2%未満", frac1 < BALD_LIMIT, f"{frac0 * 100:.1f}% → {frac1 * 100:.1f}%（隙間埋め{len(fills)}房）")

    allhair = [o for o in bpy.data.objects if o.name.startswith("Hair_Back") or o.name.startswith("Hair_Fill")]
    gates.check("生成した房が、頭・黒目と交差していない", all(r[2] == 0 and r[3] == 0 for r in report) and all(f[2] == 0 and f[3] == 0 for f in fills),
                [r for r in report if r[2] or r[3]] + [f for f in fills if f[2] or f[3]])
    gates.check("全ての房の位置・回転・拡大が単位", all(tuple(o.location) == (0, 0, 0) and tuple(o.rotation_euler) == (0, 0, 0) and tuple(o.scale) == (1, 1, 1) for o in allhair))
    gates.check("モディファイアは Subdivision のみ（Mirrorなし）", all([m.type for m in o.modifiers] == ["SUBSURF"] for o in allhair))
    gates.check("既存のオブジェクトは変更していない（増えたのは房のみ）", len(bpy.data.objects) == n_before + len(allhair))

    deps = bpy.context.evaluated_depsgraph_get()
    unexplained, worst = 0, 0.0
    for o in made:
        em = bpy.data.meshes.new_from_object(o.evaluated_get(deps))
        for v in em.vertices:
            over = max(abs(v.co.x) - X(v.co.z), v.co.y - Y(v.co.z))
            if over > 0.015 and bvh_head.find_nearest(v.co)[3] > 0.03:
                unexplained += 1
                worst = max(worst, over)
        bpy.data.meshes.remove(em)
    gates.check("外形（下絵）からのはみ出しのうち、頭で説明できないもの（頭から30mm超）が無い", unexplained == 0, (unexplained, round(worst * 1000, 1)))

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "hair_h02_gen.blend"), compress=False)

    for m in bpy.data.materials:
        if m.use_nodes:
            b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
            if b:
                b.inputs["Roughness"].default_value = 0.9
                b.inputs["Specular IOR Level"].default_value = 0.05
    scene = bpy.context.scene
    if scene.world is None:
        w = bpy.data.worlds.new("ReviewWorld")
        w.use_nodes = True
        w.node_tree.nodes["Background"].inputs[0].default_value = (0.9, 0.9, 0.9, 1.0)
        scene.world = w
    if bpy.data.objects.get("ReviewSun") is None:
        ld = bpy.data.lights.new("ReviewSun", type="SUN")
        ld.energy = 1.5
        sun = bpy.data.objects.new("ReviewSun", ld)
        sun.rotation_euler = (0.6, 0, 0)
        scene.collection.objects.link(sun)
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
    scene.render.resolution_x = scene.render.resolution_y = 1024
    for o in bpy.data.objects:
        if o.type == "MESH":
            o.hide_render = o.name in ("Eyelash", "Hair_Bangs")

    def temp_cam(name, loc, rot):
        cd = bpy.data.cameras.new(name)
        cd.type = "ORTHO"
        cd.ortho_scale = bpy.data.objects["CAM_front"].data.ortho_scale
        co = bpy.data.objects.new(name, cd)
        co.location, co.rotation_euler = loc, rot
        scene.collection.objects.link(co)
    temp_cam("TMP_top", (0, 0, 2.0), (0, 0, 0))
    temp_cam("TMP_back", (0, 2.0, 0.0046), (math.pi / 2, 0, math.pi))
    for cam, name in [("CAM_front", "h02_render_front.png"), ("CAM_a45", "h02_render_45.png"), ("CAM_side", "h02_render_side.png"),
                      ("TMP_top", "h02_render_top.png"), ("TMP_back", "h02_render_back.png")]:
        scene.camera = bpy.data.objects[cam]
        scene.render.filepath = str(C.OUT / name)
        bpy.ops.render.render(write_still=True)
    gates.finish()


main()
