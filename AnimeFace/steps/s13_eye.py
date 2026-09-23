"""S13: 瞳（黒目）を別オブジェクトで作る（後編 動画 00:00〜02:36）。

字幕との対応:
  00:00〜00:21 UV球を追加し、R X 90 で前を向ける             → 球の極（前）を -Y へ向けた、円盤状の網（32分割）。極は三角形の扇（UV球のまま）
  00:21〜00:46 一番前の頂点から選択を広げ、反転して削除、瞳だけ残す → 極から 5 輪だけ残す（161頂点・面160＝三角形32＋四角形128）
  00:46〜01:02 プロポーショナル編集（スフィア）で、中心を奥へ、凹んだ形に → 中心を、縁の平面より奥へ D だけ、滑らかに（D(1-ρ²)）凹ませる
  01:02〜01:41 縮小して目の位置へ。縦長に S X                    → 大きさ・縦横比は、3つの下絵の黒目の輪郭（楕円）から測る
  01:41〜01:54 上から見て少し外向き、横から見て少し下向き、下絵の位置へ → 向き（外向き・下向き）と位置は、下絵の黒目の楕円に合わせて当てはめる
  01:54〜02:13 少し前へ。Mirror モディファイア（Mirror Object = 顔）      → Mirror（X）、Mirror Object = Face。Subsurf は付けない（動画 31:40: 目は Subsurf を使わない）
  02:13〜02:36 「もう少し下げてもよい」                                  → 好みの判断なので触らない

設計:
  - 黒目の輪郭（外側の黒い線）の楕円を、正面・45°・側面の下絵から測る（`measure.iris_ellipse`）。上側はまつ毛と続くので、下・左右の輪郭点から当てはめる
  - 3次元の黒目: 平面の楕円（水平の半径 A・垂直の半径 B）、外向き yaw・下向き pitch。正面と側面は、中心と半径（4値ずつ）を、45° は半径だけ、重みを付けて当てはめる
    （45° の中心は、下絵どうしの食い違い（鼻・口で 35〜45px）があるので使わない）
  - 凹み D=8mm は仮定（下絵にない）。位置は、下絵の黒目に合わせたまま。皮膚（顔の面）と交差せず 0.5mm 以上離れることを確かめる（離れなければ、世界の +Y へ、正面の位置を変えずに引く）
  - 黒目は、開口（縁）より上下に大きい（下絵でも、上下はまつ毛・まぶたに隠れる）。開口の外にある頂点の数を報告する（S14 のまつ毛・下まぶたで覆う）

入力: out/face_s12_human.blend   出力: out/face_s13_gen.blend, out/s13_report.json, out/s13_*.png
実行: blender --background --factory-startup --python steps/s13_eye.py
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
import measure as M  # noqa: E402
import overlay  # noqa: E402

STEP = "s13"
gates = C.Gates(STEP)

SEEDS = {"front": (348, 517), "a45": (538, 527), "side": (747, 520)}
ANG = {"front": 0, "a45": 45, "side": 90}
N_SEG, N_RING = 32, 5
DEPTH_D = 0.008            # 中心の凹み（仮定）


def rd(v):
    return tuple(round(float(c), 4) for c in v)


def frame(yaw, pitch):
    """黒目の平面の向き。n: 前（外向き・下向き）、h: 水平の面内方向（+X 寄り）、v: 垂直の面内方向（上）。"""
    n = Vector((-math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), -math.sin(pitch)))
    h = Vector((math.cos(yaw), -math.sin(yaw), 0.0))
    v = n.cross(h)
    if v.z < 0:
        v = -v
    return n, h.normalized(), v.normalized()


def proj_stats(c, n, h, v, A, B, view):
    """縁の楕円を下絵の視点へ投影し、中心（外接矩形の中心）と半径を返す。"""
    pts = []
    for t in np.linspace(0, 2 * math.pi, 96, endpoint=False):
        p = c + h * (A * math.cos(t)) + v * (B * math.sin(t))
        pts.append(C.project(p, ANG[view]))
    P = np.array(pts)
    return ((P[:, 0].min() + P[:, 0].max()) / 2, (P[:, 1].min() + P[:, 1].max()) / 2, (P[:, 0].max() - P[:, 0].min()) / 2, (P[:, 1].max() - P[:, 1].min()) / 2)


def nelder_mead(f, x0, step, iters=1500):
    n = len(x0)
    pts = [np.array(x0, dtype=float)]
    for i in range(n):
        x = np.array(x0, dtype=float)
        x[i] += step[i]
        pts.append(x)
    vals = [f(p) for p in pts]
    for _ in range(iters):
        order = np.argsort(vals)
        pts = [pts[i] for i in order]
        vals = [vals[i] for i in order]
        cen = np.mean(pts[:-1], axis=0)
        xr = cen + (cen - pts[-1])
        fr = f(xr)
        if fr < vals[0]:
            xe = cen + 2 * (cen - pts[-1])
            fe = f(xe)
            pts[-1], vals[-1] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < vals[-2]:
            pts[-1], vals[-1] = xr, fr
        else:
            xc = cen + 0.5 * (pts[-1] - cen)
            fc = f(xc)
            if fc < vals[-1]:
                pts[-1], vals[-1] = xc, fc
            else:
                for i in range(1, n + 1):
                    pts[i] = pts[0] + 0.5 * (pts[i] - pts[0])
                    vals[i] = f(pts[i])
    i = int(np.argmin(vals))
    return pts[i], vals[i]


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s12_human.blend"))
    face = bpy.data.objects["Face"]
    if face.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    gates.check("入力: モディファイアは Mirror → Subsurf", [m.type for m in face.modifiers] == ["MIRROR", "SUBSURF"])

    # ---- 下絵の黒目（楕円）
    meas = {}
    for view in ("front", "a45", "side"):
        e = M.iris_ellipse(view, SEEDS[view], out_png=C.OUT / f"s13_iris_{view}.png")
        meas[view] = e
    gates.check("3つの下絵で、黒目の輪郭点が 30 点以上あり、楕円が測れた", all(m is not None and m[4] >= 30 for m in meas.values()), {k: (round(v[0], 1), round(v[1], 1), round(v[2], 1), round(v[3], 1), v[4]) for k, v in meas.items()})
    for view, m in meas.items():
        gates.note(f"黒目の楕円（{view}）", f"中心 u={m[0]:.1f} v={m[1]:.1f}、半径 横{m[2]:.1f}px（{m[2] * C.K * 1000:.1f}mm）・縦{m[3]:.1f}px（{m[3] * C.K * 1000:.1f}mm）")

    # ---- 3次元の当てはめ
    def cost(x):
        cx, cy, cz, yaw, pitch, A, B = x
        n, h, v = frame(yaw, pitch)
        c = Vector((cx, cy, cz))
        tot = 0.0
        for view, w_center, w_size in (("front", 1.0, 1.0), ("side", 1.0, 1.0), ("a45", 0.0, 0.5)):
            cu, cv, ra, rb = proj_stats(c, n, h, v, A, B, view)
            mu, mv, ma, mb = meas[view][0], meas[view][1], meas[view][2], meas[view][3]
            tot += w_center * ((cu - mu) ** 2 + (cv - mv) ** 2) + w_size * ((ra - ma) ** 2 + (rb - mb) ** 2)
        return tot

    fu = meas["front"]
    x0 = [(fu[0] - C.COL0) * C.K, -(meas["side"][0] - C.COL0) * C.K, (C.ROW0 - fu[1]) * C.K, math.radians(22), math.radians(3), 0.040, 0.047]
    x, fval = nelder_mead(cost, x0, [0.005, 0.005, 0.005, 0.1, 0.1, 0.005, 0.005])
    cx, cy, cz, yaw, pitch, A, B = [float(t) for t in x]
    n, h, v = frame(yaw, pitch)
    c0 = Vector((cx, cy, cz))
    gates.note("当てはめ（3次元の黒目）", f"中心 {rd(c0)}、外向き {math.degrees(yaw):.1f}°・下向き {math.degrees(pitch):.1f}°、半径 横{A * 1000:.1f}mm・縦{B * 1000:.1f}mm、残差の二乗和 {fval:.1f}px²")
    errs = {}
    for view in ("front", "side", "a45"):
        cu, cv, ra, rb = proj_stats(c0, n, h, v, A, B, view)
        errs[view] = (round(cu - meas[view][0], 1), round(cv - meas[view][1], 1), round(ra - meas[view][2], 1), round(rb - meas[view][3], 1))
    gates.note("当てはめの誤差（投影 − 測定, px: 中心u・中心v・横半径・縦半径）", errs)
    gates.check("正面・側面の黒目は、中心・半径とも 4px 以内に当てはまった", all(abs(t) <= 4 for view in ("front", "side") for t in errs[view]), {k: errs[k] for k in ("front", "side")})
    gates.note("要確認: 45° の黒目は、半径だけ重み 0.5 で当てはめた。誤差", errs["a45"])

    # ---- 凹んだ円盤（UV球の極の周りを 5 輪）。ρ=0（極）〜 1（縁）
    def dome_points(center):
        pts = [center - n * DEPTH_D]                    # 極（中心）: 縁の平面より奥へ D
        for i in range(1, N_RING + 1):
            rho = i / N_RING
            for k in range(N_SEG):
                psi = 2 * math.pi * k / N_SEG
                p = center + h * (A * rho * math.cos(psi)) + v * (B * rho * math.sin(psi)) - n * (DEPTH_D * (1 - rho * rho))
                pts.append(p)
        return pts

    faces = []
    for k in range(N_SEG):                              # 極の三角形の扇
        faces.append((0, 1 + (k + 1) % N_SEG, 1 + k))
    for i in range(1, N_RING):
        for k in range(N_SEG):
            a = 1 + (i - 1) * N_SEG + k
            b = 1 + (i - 1) * N_SEG + (k + 1) % N_SEG
            cc = 1 + i * N_SEG + (k + 1) % N_SEG
            d = 1 + i * N_SEG + k
            faces.append((a, b, cc, d))

    # 皮膚（顔）との交差・距離: 顔の面（半分）と黒目の面の BVH
    fme = face.data
    fverts = [tuple(vv.co) for vv in fme.vertices]
    fpolys = [list(p.vertices) for p in fme.polygons]
    bvh_face = BVHTree.FromPolygons(fverts, fpolys)

    # 目の開口（縁 R0）を、正面（XZ）へ投影した多角形。クリース・シャープの輪のうち、より前（Y が小さい）ほう
    cre = fme.attributes["crease_edge"]
    ring_edges = [e for e in fme.edges if cre.data[e.index].value > 0 and (fme.vertices[e.vertices[0]].co - Vector((-0.1217, -0.1485, -0.001))).length < 0.09]
    vs_ring = sorted({i for e in ring_edges for i in e.vertices})
    cen_eye = Vector((-0.1217, -0.1485, -0.001))
    n_pocket = Vector((-0.6201, -0.7823, -0.0588))
    ring_a = sorted(vs_ring, key=lambda i: -(fme.vertices[i].co - cen_eye).dot(n_pocket))[:13]      # 縁 R0 は、R1 より外側（皮膚の側）
    order = sorted(ring_a, key=lambda i: math.atan2(fme.vertices[i].co.z - cen_eye.z, fme.vertices[i].co.x - cen_eye.x))
    poly = [(fme.vertices[i].co.x, fme.vertices[i].co.z) for i in order]

    def inside(px, pz):
        ins = False
        for k in range(len(poly)):
            x1, z1 = poly[k]
            x2, z2 = poly[(k + 1) % len(poly)]
            if (z1 > pz) != (z2 > pz) and px < (x2 - x1) * (pz - z1) / (z2 - z1) + x1:
                ins = not ins
        return ins

    gates.check("目の開口（縁 R0）の多角形が取れた（13頂点）", len(poly) == 13, len(poly))

    def build(shift_y):
        c = c0 + Vector((0, shift_y, 0))
        P = dome_points(c)
        fs = [list(f) for f in faces]
        bvh_e = BVHTree.FromPolygons([tuple(p) for p in P], fs)
        hit = bvh_e.overlap(bvh_face)
        dmin = min(bvh_face.find_nearest(p)[3] for p in P)
        # 浮き: 開口の外にあるのに、正面（-Y 方向）に皮膚がない頂点（皮膚の手前に飛び出している）
        floating = 0
        for p in P:
            if not inside(p.x, p.z):
                r = bvh_face.ray_cast(p + Vector((0, -1e-4, 0)), Vector((0, -1, 0)), 1.0)
                if r[0] is None:
                    floating += 1
        return P, fs, len(hit), dmin, floating

    chosen = None
    tried = []
    for s_mm in np.arange(0.0, 40.5, 0.5):
        P, fs, nh, dmin, fl = build(s_mm / 1000)
        tried.append((float(s_mm), nh, round(dmin * 1000, 2), fl))
        if nh == 0 and dmin >= 0.0005:
            chosen = (s_mm / 1000, P, fs)
            break
    gates.note("引き量 mm・交差した面の対の数・最小距離 mm・開口の外で皮膚の手前に飛び出した頂点の数（最初・途中・最後）", [tried[0], tried[len(tried) // 2], tried[-1]])
    gates.check("皮膚（顔）と交差せず、0.5mm 以上離れる位置が見つかった（引き量 0 が最小）", chosen is not None)
    if chosen is None:
        gates.finish()
        return
    shift, P, fs = chosen
    gates.note("採用した引き量（世界の +Y、正面から見た位置は変わらない）", f"{shift * 1000:.1f}mm（側面での位置のずれ: {shift / C.K:.1f}px）")
    P_, fs_, nh_, dmin_, fl_ = build(shift)
    gates.note("開口（縁の輪）の外にある頂点（皮膚の手前に出る部分。上まぶた・下まぶたの側。S14 のまつ毛・下まぶたで覆う）", f"{fl_} / {len(P_)} 頂点")
    gates.note("黒目と皮膚の最小距離", f"{dmin_ * 1000:.1f}mm")
    side_err = cy + shift - (-(meas['side'][0] - C.COL0) * C.K)
    gates.note("側面での黒目の中心の位置の誤差（メッシュ − 下絵）", f"{side_err / C.K:.1f}px（{side_err * 1000:.1f}mm）")

    # ---- Eye オブジェクト
    me = bpy.data.meshes.new("Eye")
    me.from_pydata([tuple(p) for p in P], [], [tuple(f) for f in fs])
    me.update()
    # 向き: 法線が前（+n）へ
    bmm = bmesh.new()
    bmm.from_mesh(me)
    bmm.normal_update()
    flip = sum(1 for f in bmm.faces if f.normal.dot(n) < 0) > len(bmm.faces) / 2
    if flip:
        bmesh.ops.reverse_faces(bmm, faces=list(bmm.faces))
    bmm.normal_update()
    bad = [f.index for f in bmm.faces if f.normal.dot(n) <= 0]
    bmm.to_mesh(me)
    bmm.free()
    for p in me.polygons:
        p.use_smooth = True
    gates.check("黒目の面の法線が、全て前（外向き・下向きの向き）を向く", not bad, bad[:8])
    eye = bpy.data.objects.new("Eye", me)
    (face.users_collection[0] if face.users_collection else bpy.context.scene.collection).objects.link(eye)
    md = eye.modifiers.new("Mirror", "MIRROR")
    md.use_axis[0] = True
    md.mirror_object = face
    md.use_clip = False
    md.use_mirror_merge = False
    gates.check("Eye: Mirror（X、Mirror Object = Face）のみ。Subdivision は付けない", [m.type for m in eye.modifiers] == ["MIRROR"] and eye.modifiers[0].mirror_object is face)
    gates.check("Eye: 頂点161・面160（三角形32＋四角形128）", len(me.vertices) == 1 + N_SEG * N_RING and len(me.polygons) == N_SEG + (N_RING - 1) * N_SEG and sum(1 for p in me.polygons if len(p.vertices) == 3) == N_SEG,
                f"V={len(me.vertices)} F={len(me.polygons)}")
    gates.check("Eye: X<0（左目）の側だけを作り、Mirror で右目", max(vv.co.x for vv in me.vertices) < 0)

    # ---- 見え方: 正面から見える割合（世界の -Y へ光線）と、位置の確認
    face_ev_me = bpy.data.meshes.new_from_object(face.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    fv = [tuple(vv.co) for vv in face_ev_me.vertices]
    fp = [list(p.vertices) for p in face_ev_me.polygons]
    bvh_all = BVHTree.FromPolygons(fv, fp)
    vis = 0
    tot = 0
    hidden_rows = []
    for k, p in enumerate(P):
        tot += 1
        hit = bvh_all.ray_cast(Vector(p) + Vector((0, -1e-4, 0)), Vector((0, -1, 0)), 1.0)
        if hit[0] is None:
            vis += 1
        else:
            hidden_rows.append(round(p.z, 3))
    gates.note("黒目の頂点のうち、正面（-Y 方向）から見える割合", f"{vis}/{tot}（{100 * vis / tot:.0f}%）。隠れる頂点の Z の範囲 {(min(hidden_rows), max(hidden_rows)) if hidden_rows else None}（上まぶた・下まぶたの皮膚に隠れる）")
    bpy.data.meshes.remove(face_ev_me)

    # ---- レビュー画像: 顔（Mirror 後）＋ 黒目 を、正面・45°・側面で重ねる
    face.modifiers["Subdivision"].show_viewport = False
    face_m = bpy.data.meshes.new_from_object(face.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    eye_m = bpy.data.meshes.new_from_object(eye.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    comb = bpy.data.meshes.new("comb")
    verts = [tuple(vv.co) for vv in face_m.vertices] + [tuple(vv.co) for vv in eye_m.vertices]
    off = len(face_m.vertices)
    edges = [tuple(e.vertices) for e in face_m.edges] + [(e.vertices[0] + off, e.vertices[1] + off) for e in eye_m.edges]
    comb.from_pydata(verts, edges, [])
    for view, ang in (("front", 0), ("a45", 45), ("side", 90)):
        u, vv_ = SEEDS[view]
        crop = (int(u - 130), int(vv_ - 110), int(u + 130), int(vv_ + 110))
        overlay.write_overlay(comb, ang, C.OUT / f"s13_overlay_{view}.png", crop=crop, zoom=3)
    face.modifiers["Subdivision"].show_viewport = True
    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s13_gen.blend"), compress=False)
    gates.finish()


main()
