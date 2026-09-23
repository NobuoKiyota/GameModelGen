"""S14: 上まつ毛（太いほう）を別オブジェクトで作る（後編 動画 02:36〜07:29、10:37〜11:39）。細いまつ毛（07:43〜10:00）は S14b。

字幕との対応:
  02:41〜03:12 まつ毛になる辺を選び、Shift+D で複製、P で別オブジェクトに    → 顔の目の縁（R0）の上側の辺（内眼角→外眼角、8頂点）を基準の線にして、別オブジェクト `Eyelash`
  03:12〜04:30 E S で外側の線、E S 縮小で内側の線。顔に埋まる分は G Y で手前へ → 外側の点 O・内側の点 I。位置は、下絵の黒い帯の厚みから測る。O は皮膚の表面に沿わせて（皮膚の面へ光線を当てて）少し手前へ
  04:30〜05:16 穴を F で埋める。ループを足して Alt+S で膨らませ、ひし形の断面。膨らませた線にクリース → 断面を 4点（外側 O・前の稜 F・内側 I・後ろ K）のひし形にし、F の線にクリース 1.0。両端は四角形1枚で閉じる
  05:16〜05:51 Subsurf をオン。下端・目頭を S で絞る                       → Subsurf（表示1・レンダー2、顔と同じ）。目頭の端は断面を小さく。Subsurf で 2/3 に縮むので、下絵の帯に合うよう、断面の幅を補正
  05:51〜07:29 目尻の形を下絵に合わせる、目頭の端を絞る                       → 外眼角の先へ、下絵の跳ね上げの先端（黒い楔）まで、1つ延長（先端は断面を絞る）
  10:37〜11:39 面の向きの確認・フリップ、スムースシェード                       → 全ての面の法線が外向きか数値で確認、スムースシェード

設計:
  - まつ毛の帯: 下絵（正面）の黒い帯を、目の縁の上側の各点から、外向きに測る（内側は、黒目の輪郭と続いて測れないので、一定 4px）
  - 断面のひし形: F は皮膚の法線方向へ 2.0mm（手前）、K は 0.4mm（奥）。O は皮膚の表面の 0.6mm 手前
  - 黒目（`Eye`）・顔の面と交差しないように、必要なら、まつ毛全体を手前（皮膚の法線方向）へ 0.5mm ずつ出す

入力: out/face_s13_human.blend   出力: out/face_s14_gen.blend, out/s14_report.json, out/s14_*.png
実行: blender --background --factory-startup --python steps/s14_eyelash.py
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

STEP = "s14"
gates = C.Gates(STEP)

CEN_EYE = Vector((-0.1217, -0.1485, -0.001))
T_IN_PX = 4.0             # 内側の幅（黒目の上にかぶる）
H_FRONT = 0.0020          # 前の稜 F: 皮膚の法線方向へ
H_BACK = 0.0004           # 後ろ K
OFF_OUT = 0.0006          # 外側の点を、皮膚の表面より手前へ
END_SCALE = 0.35          # 内眼角側の端の断面の大きさ
TIP_SCALE = 0.20          # 跳ね上げの先端の断面の大きさ


def rd(v):
    return tuple(round(float(c), 4) for c in v)


def px_to_xz(u, v):
    return (u - C.COL0) * C.K, (C.ROW0 - v) * C.K


def fill_poly(mask, pts):
    """凸・非凸を問わず、多角形の内側を塗る（偶奇規則）。pts は (u, v) の並び。"""
    H, W = mask.shape
    P = np.array(pts, dtype=float)
    v0, v1 = int(max(P[:, 1].min(), 0)), int(min(P[:, 1].max(), H - 1))
    for y in range(v0, v1 + 1):
        xs = []
        for k in range(len(P)):
            a, b = P[k], P[(k + 1) % len(P)]
            if (a[1] <= y + 0.5 < b[1]) or (b[1] <= y + 0.5 < a[1]):
                xs.append(a[0] + (y + 0.5 - a[1]) * (b[0] - a[0]) / (b[1] - a[1]))
        xs.sort()
        for j in range(0, len(xs) - 1, 2):
            mask[y, int(max(xs[j], 0)):int(min(xs[j + 1], W - 1)) + 1] = True


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s13_human.blend"))
    for o in bpy.data.objects:
        if o.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
    face = bpy.data.objects["Face"]
    eye = bpy.data.objects["Eye"]
    me = face.data
    gates.check("入力: Face は Mirror → Subsurf、Eye は Mirror のみ", [m.type for m in face.modifiers] == ["MIRROR", "SUBSURF"] and [m.type for m in eye.modifiers] == ["MIRROR"])
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    cre = me.attributes["crease_edge"]
    ringv = {i for e in me.edges if cre.data[e.index].value > 0 for i in e.vertices if (me.vertices[i].co - CEN_EYE).length < 0.09}
    pocket_min = min(i for i in ringv if any(len(f.verts) >= 3 and all(v.index >= 463 for v in f.verts) for f in bm.verts[i].link_faces)) if False else 463
    R0 = [i for i in ringv if any(all(v.index < pocket_min for v in f.verts) for f in bm.verts[i].link_faces)]
    gates.check("目の縁 R0 は13頂点", len(R0) == 13, len(R0))
    order = sorted(R0, key=lambda i: math.atan2(me.vertices[i].co.z - CEN_EYE.z, me.vertices[i].co.x - CEN_EYE.x))
    ix = max(order, key=lambda i: me.vertices[i].co.x)          # 内眼角
    ox = min(order, key=lambda i: me.vertices[i].co.x)          # 外眼角
    zc = (me.vertices[ix].co.z + me.vertices[ox].co.z) / 2
    up = sorted([i for i in order if me.vertices[i].co.z >= zc - 0.002], key=lambda i: -me.vertices[i].co.x)
    gates.check("上側の基準の線は、内眼角→外眼角の8頂点", len(up) == 8 and up[0] == ix and up[-1] == ox, up)

    # ---- 皮膚の表面（顔の面のうち、眼窩の面を除く）と、黒目
    skin_polys = [[v.index for v in f.verts] for f in bm.faces if all(v.index < pocket_min for v in f.verts)]
    fverts = [tuple(v.co) for v in bm.verts]
    bvh_skin = BVHTree.FromPolygons(fverts, skin_polys)
    all_polys = [[v.index for v in f.verts] for f in bm.faces]
    bvh_face = BVHTree.FromPolygons(fverts, all_polys)
    eme = eye.data
    bvh_eye = BVHTree.FromPolygons([tuple(v.co) for v in eme.vertices], [list(p.vertices) for p in eme.polygons])
    bm.normal_update()

    def skin_normal(vi):
        n = Vector((0, 0, 0))
        for f in bm.verts[vi].link_faces:
            if all(v.index < pocket_min for v in f.verts):
                n += f.normal * f.calc_area()
        return n.normalized()

    def lift(u, v):
        """下絵の画素 (u, v) の位置の皮膚の表面（正面から光線）。点と法線。"""
        x, z = px_to_xz(u, v)
        hit = bvh_skin.ray_cast(Vector((x, -0.6, z)), Vector((0, 1, 0)), 2.0)
        return (hit[0], hit[1]) if hit[0] is not None else (None, None)

    # ---- 下絵の黒い帯（外向きの厚み）
    im = M._px("front")[..., :3]
    val = im.mean(axis=2)

    def is_black(x, y):
        xi, yi = int(round(x)), int(round(y))
        return 0 <= xi < 1024 and 0 <= yi < 1024 and val[yi, xi] < 75

    rim2 = [np.array(C.project(me.vertices[i].co, 0)) for i in up]
    ctr = np.array(C.project(CEN_EYE, 0))
    normals2 = []
    thick = []
    for k in range(len(up)):
        a, b = rim2[max(k - 1, 0)], rim2[min(k + 1, len(up) - 1)]
        t = (b - a) / np.linalg.norm(b - a)
        nn = np.array([t[1], -t[0]])
        if np.dot(nn, rim2[k] - ctr) < 0:
            nn = -nn
        normals2.append(nn)
        end, started = 0.0, False
        for s in np.arange(0, 30, 0.5):                     # 30px まで（外眼角の楔は別に扱う）
            q = rim2[k] + nn * s
            if is_black(*q):
                started, end = True, s
            elif started and s - end > 2.5:
                break
        thick.append(end if started else 0.0)
    thick = [max(t, 3.0) for t in thick]
    thick[-1] = min(thick[-1], 28.0)
    gates.note("下絵の黒い帯の、外向きの厚み（px、内眼角→外眼角）", [round(t, 1) for t in thick])

    # 跳ね上げの先端: 外眼角より外（u が小さい側）で、黒が続く最も外側の点
    tip = None
    for u in range(int(rim2[-1][0]), 190, -1):
        col = [vv for vv in range(478, 512) if is_black(u, vv)]
        if not col:
            tip_u = u + 1
            col2 = [vv for vv in range(478, 512) if is_black(tip_u, vv)]
            tip = (float(tip_u), float(np.mean(col2)) if col2 else float(rim2[-1][1]))
            break
    gates.check("外眼角の跳ね上げの先端が下絵で測れた", tip is not None, tip)
    gates.note("跳ね上げの先端（下絵の画素）", tip)

    # ---- 断面（O・F・I・K）を、各駅で。曲がった皮膚の上で、駅と駅の間の直線が皮膚の内側へ潜らないように、間に駅を足す
    n_up = len(up)
    r3s = [me.vertices[i].co.copy() for i in up]
    base = []          # (rim の画素, 外向きの向き, 厚み, 断面の大きさ, rim の3次元)
    for k in range(n_up):
        base.append((rim2[k], normals2[k], thick[k], END_SCALE if k == 0 else 1.0, r3s[k]))
    dense = []
    for k in range(n_up - 1):
        m = 2 if k >= 1 else 1                     # 内眼角の最初の間は1つ、それ以外は2つ挿入
        for j in range(m):
            t = j / m
            a_, b_ = base[k], base[k + 1]
            nn = a_[1] * (1 - t) + b_[1] * t
            nn = nn / np.linalg.norm(nn)
            dense.append((a_[0] * (1 - t) + b_[0] * t, nn, a_[2] * (1 - t) + b_[2] * t, a_[3] * (1 - t) + b_[3] * t, a_[4] * (1 - t) + b_[4] * t))
    dense.append(base[n_up - 1])
    corner = base[n_up - 1]
    tip2 = np.array(tip)
    for j in range(1, 4):                          # 外眼角→先端 の間に 3 つ
        t = j / 4
        pos = corner[0] * (1 - t) + tip2 * t
        dir_ = corner[1] * (1 - t) + np.array([-1.0, 0.0]) * t
        dir_ = dir_ / np.linalg.norm(dir_)
        thick_j = corner[2] * (1 - t) + 4.0 * t
        rp_, _ = lift(*pos)
        r3_ = rp_ if rp_ is not None and abs(rp_.y - corner[4].y) < 0.08 else corner[4]
        dense.append((pos, dir_, thick_j, (1 - t) + 0.5 * t, r3_))
    stations = []
    bad_lift = 0
    for rim_px, nn, th, scl, r3 in dense:
        o2 = rim_px + nn * th
        ps, ns = lift(*o2)
        if ps is None or abs(ps.y - r3.y) > 0.08:      # 穴を通り抜けて頭の奥へ当たった: 皮膚の最も近い点を使う
            loc = bvh_skin.find_nearest(r3 + Vector((nn[0] * th * C.K, 0, -nn[1] * th * C.K)))
            ps, ns = loc[0], loc[1]
            bad_lift += 1
        O = ps + ns * OFF_OUT
        Tout = (O - r3)
        if Tout.length < 1e-9:
            Tout = Vector((-1, 0, 0))
        Tout.normalize()
        I = r3 - Tout * (T_IN_PX * C.K) + ns * OFF_OUT
        stations.append(dict(O=O, I=I, N=ns, scale=scl, r3=r3.copy()))
    gates.note("光線が皮膚に当たらず、最も近い点で代えた駅", bad_lift)
    ptip, ntip = lift(*tip)
    ptip = ptip + ntip * OFF_OUT
    tdir = (stations[-1]["O"] - stations[-1]["I"]).normalized()
    stations.append(dict(O=ptip + tdir * 0.0015, I=ptip - tdir * 0.0015, N=ntip, scale=0.5, r3=ptip.copy()))
    n_st = len(stations) - 1
    gates.note("駅（断面）の数", f"{len(stations)}（基準の線 {n_up}＋間を補った駅＋先端）")

    def make_ring(st, kf):
        mid = (st["O"] + st["I"]) / 2
        half = (st["O"] - st["I"]) / 2 * kf * st["scale"]
        O = mid + half
        I = mid - half
        N = st["N"]
        hf = H_FRONT * (st["scale"] if st["scale"] < 1 else 1.0)
        F = mid + N * (hf + (0.0004 if st["scale"] < 1 else 0.0))
        K = mid - N * H_BACK
        return [O, F, I, K]

    # ---- メッシュと Subsurf 後の形（下絵の帯との重なり）
    def build_mesh(kf, push=None):
        verts = []
        for si, st in enumerate(stations):
            ring = make_ring(st, kf)
            pu = 0.0 if push is None else push[si]
            verts += [(p + st["N"] * pu) for p in ring]
        faces = []
        for s in range(n_st):
            for j in range(4):
                a, b = s * 4 + j, s * 4 + (j + 1) % 4
                faces.append([a, b, (s + 1) * 4 + (j + 1) % 4, (s + 1) * 4 + j])
        faces.append([3, 2, 1, 0])
        faces.append([n_st * 4, n_st * 4 + 1, n_st * 4 + 2, n_st * 4 + 3])
        return verts, faces

    def orient(verts, faces):
        """全ての面が、断面の中心から外向き（法線が外）になるように、巻き順をそろえる。"""
        cen_s = [sum((Vector(verts[s * 4 + j]) for j in range(4)), Vector()) / 4 for s in range(n_st + 1)]
        out = []
        flips = 0
        for k, f in enumerate(faces):
            pts = [Vector(verts[i]) for i in f]
            nrm = Vector((0, 0, 0))
            for q in range(len(pts)):
                a, b = pts[q], pts[(q + 1) % len(pts)]
                nrm += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
            c = sum(pts, Vector()) / len(pts)
            if k < 4 * n_st:
                s = k // 4
                ref = (cen_s[s] + cen_s[s + 1]) / 2
                good = nrm.dot(c - ref) > 0
            elif k == 4 * n_st:
                good = nrm.dot(cen_s[0] - cen_s[1]) > 0              # 内眼角の端: 軸の外（後ろ）向き
            else:
                good = nrm.dot(cen_s[-1] - cen_s[-2]) > 0
            if not good:
                f = f[::-1]
                flips += 1
            out.append(f)
        return out, flips

    lash_me = bpy.data.meshes.new("Eyelash")
    lash = bpy.data.objects.new("Eyelash", lash_me)
    (face.users_collection[0] if face.users_collection else bpy.context.scene.collection).objects.link(lash)
    mm = lash.modifiers.new("Mirror", "MIRROR")
    mm.use_axis[0] = True
    mm.mirror_object = face
    mm.use_clip = False
    mm.use_mirror_merge = False
    sm = lash.modifiers.new("Subdivision", "SUBSURF")
    sm.levels = 1
    sm.render_levels = 2

    def set_mesh(verts, faces, crease=True):
        faces, _ = orient(verts, faces)
        lash_me.clear_geometry()
        lash_me.from_pydata(verts, [], faces)
        lash_me.update()
        for p in lash_me.polygons:
            p.use_smooth = True
        if crease:
            ca = lash_me.attributes.get("crease_edge") or lash_me.attributes.new("crease_edge", "FLOAT", "EDGE")
            ridge = {frozenset((s * 4 + 1, (s + 1) * 4 + 1)) for s in range(n_st)}
            for e in lash_me.edges:
                if frozenset(e.vertices) in ridge:
                    ca.data[e.index].value = 1.0

    def eval_front_mask(level=2):
        sm.show_viewport = True
        old = sm.levels
        sm.levels = level
        bpy.context.view_layer.update()
        ev = bpy.data.meshes.new_from_object(lash.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        sm.levels = old
        mask = np.zeros((1024, 1024), dtype=bool)
        for p in ev.polygons:
            uv = [C.project(ev.vertices[i].co, 0) for i in p.vertices]
            if max(u for u, _ in uv) < 512:                    # 左目のほうだけ（X<0）
                for a in range(1, len(uv) - 1):
                    fill_poly(mask, [uv[0], uv[a], uv[a + 1]])
        bpy.data.meshes.remove(ev)
        return mask

    # 目標の多角形（下絵の帯）: 外側の線 O_k（外向き thick）と、内側の線（-T_IN_PX）、先端まで
    tgt_out = [tuple(rim2[k] + normals2[k] * thick[k]) for k in range(n_up)] + [tip]
    tgt_in = [tuple(rim2[k] - normals2[k] * T_IN_PX) for k in range(n_up)]
    target = np.zeros((1024, 1024), dtype=bool)
    fill_poly(target, tgt_out + tgt_in[::-1])
    bp_black = (val < 75)
    cover = float((target & bp_black).sum()) / max(int(target.sum()), 1)
    gates.note("目標の帯（下絵の黒い帯から測った多角形）のうち、下絵で黒い画素の割合", f"{cover * 100:.0f}%")

    best = None
    results = []
    for kf in (1.0, 1.2, 1.4, 1.6, 1.8, 2.0):
        v_, f_ = build_mesh(kf)
        set_mesh(v_, f_)
        mask = eval_front_mask()
        inter = (mask & target).sum()
        union = (mask | target).sum()
        iou = float(inter) / max(int(union), 1)
        results.append((kf, round(iou, 3), int(mask.sum()), int(target.sum())))
        if best is None or iou > best[1]:
            best = (kf, iou)
    gates.note("断面の幅の補正 kf ごとの、Subsurf 後の正面の投影と、目標の帯の重なり（IoU）", results)
    kf = best[0]
    gates.check("Subsurf 後の正面の投影が、下絵の帯（目標の多角形）と 60% 以上重なる", best[1] >= 0.60, f"kf={kf} IoU={best[1]:.2f}")

    # 顔・黒目との交差: 交差した面の両端の駅を、皮膚の法線方向へ 0.25mm ずつ出す（交差がなくなるまで）
    def run_push(bvh_e, iters=80):
        push_ = [0.0] * len(stations)
        hist_ = []
        for it in range(iters):
            v_, f_ = build_mesh(kf, push_)
            f2, _ = orient(v_, f_)
            bl = BVHTree.FromPolygons([tuple(p) for p in v_], f2)
            hf = bl.overlap(bvh_face)
            he = bl.overlap(bvh_e)
            hist_.append((it, len(hf), len(he)))
            if not hf and not he:
                break
            bad_faces = {a for a, _ in hf} | {a for a, _ in he}
            for fi in bad_faces:
                if fi < 4 * n_st:
                    sgi = fi // 4
                    for si in (sgi, sgi + 1):
                        push_[si] = min(push_[si] + 0.00025, 0.012)
                elif fi == 4 * n_st:
                    push_[0] = min(push_[0] + 0.00025, 0.012)
                else:
                    push_[-1] = min(push_[-1] + 0.00025, 0.012)
        return push_, hist_

    push, hist = run_push(bvh_eye)
    # 参考: 黒目を世界の +Y（奥）へ動かした場合に、まつ毛の引き出しがどれだけ減るか（黒目の上端が皮膚より手前に出ているため）
    ev_verts = [Vector(v.co) for v in eme.vertices]
    alt = []
    for sh in (0.003, 0.006, 0.009, 0.012):
        bv = BVHTree.FromPolygons([tuple(v + Vector((0, sh, 0))) for v in ev_verts], [list(p.vertices) for p in eme.polygons])
        pp, hh = run_push(bv)
        alt.append((round(sh * 1000), round(max(pp) * 1000, 2), hh[-1][1:]))
    gates.note("参考: 黒目を奥（+Y）へ動かしたときの、まつ毛の最大の引き出し量（黒目を動かす量mm, 最大の引き出しmm, 残る交差）", alt)
    inter_info = (hist[-1][1], hist[-1][2])
    gates.note("交差の推移（繰り返し・顔との交差・黒目との交差）の最初と最後", [hist[0], hist[-1]])
    gates.note("駅ごとの引き出し量（mm）", [round(x * 1000, 2) for x in push])
    gates.check("顔・黒目と交差しない", inter_info == (0, 0), (hist[-1]))
    gates.note("要確認: まつ毛の最大の引き出し量（黒目の上端が、皮膚より手前に出ているため）", f"{max(push) * 1000:.2f}mm")

    v_, f_ = build_mesh(kf, push)
    set_mesh(v_, f_)
    mask = eval_front_mask()
    iou_final = float((mask & target).sum()) / max(int((mask | target).sum()), 1)
    gates.note("採用: 幅の補正・最大の引き出し量・IoU", f"kf={kf} 引き出し 最大{max(push) * 1000:.2f}mm IoU {iou_final:.2f}")
    gates.check("引き出し後も、Subsurf 後の正面の投影が下絵の帯と 60% 以上重なる", iou_final >= 0.60, f"IoU {iou_final:.2f}")

    # ---- 検証
    lash_me.calc_loop_triangles()
    bmL = bmesh.new()
    bmL.from_mesh(lash_me)
    bmL.faces.ensure_lookup_table()
    bmL.edges.ensure_lookup_table()
    gates.check("Eyelash: 頂点%d・面%d（側面 4×%d＋端 2）" % (len(lash_me.vertices), len(lash_me.polygons), n_st), len(lash_me.vertices) == 4 * (n_st + 1) and len(lash_me.polygons) == 4 * n_st + 2, f"V={len(lash_me.vertices)} F={len(lash_me.polygons)}")
    gates.check("非多様体なし・全ての辺が2枚の面（閉じた形）", all(len(e.link_faces) == 2 for e in bmL.edges))
    # 向き: 各面の法線が外向き（断面の中心から）
    bmL.normal_update()
    cen_s = [sum((lash_me.vertices[s * 4 + j].co for j in range(4)), Vector()) / 4 for s in range(n_st + 1)]
    bad = []
    for k, f in enumerate(bmL.faces):
        c = f.calc_center_median()
        if k < 4 * n_st:
            ref = (cen_s[k // 4] + cen_s[k // 4 + 1]) / 2
            ok = f.normal.dot(c - ref) > 0
        elif k == 4 * n_st:
            ok = f.normal.dot(cen_s[0] - cen_s[1]) > 0
        else:
            ok = f.normal.dot(cen_s[-1] - cen_s[-2]) > 0
        if not ok:
            bad.append(k)
    gates.check("全ての面の法線が外向き（動画 10:37 の面の向きの確認）", not bad, bad[:8])
    ca = lash_me.attributes["crease_edge"]
    gates.check("前の稜 F の線（%d辺）にクリース 1.0" % n_st, sum(1 for d in ca.data if d.value > 0) == n_st, sum(1 for d in ca.data if d.value > 0))
    gates.check("Eyelash: Mirror（X・Mirror Object=Face）→ Subdivision（表示1・レンダー2）", [m.type for m in lash.modifiers] == ["MIRROR", "SUBSURF"] and lash.modifiers[0].mirror_object is face and (sm.levels, sm.render_levels) == (1, 2))
    gates.check("X<0（左目）の側だけを作り、Mirror で右目", max(v.co.x for v in lash_me.vertices) < 0)
    bmL.free()

    # ---- レビュー画像
    face.modifiers["Subdivision"].show_viewport = False
    fm = bpy.data.meshes.new_from_object(face.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    face.modifiers["Subdivision"].show_viewport = True
    ev = bpy.data.meshes.new_from_object(lash.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    comb = bpy.data.meshes.new("comb")
    verts = [tuple(v.co) for v in fm.vertices] + [tuple(v.co) for v in ev.vertices]
    off = len(fm.vertices)
    edges = [tuple(e.vertices) for e in fm.edges] + [(e.vertices[0] + off, e.vertices[1] + off) for e in ev.edges]
    comb.from_pydata(verts, edges, [])
    overlay.write_overlay(comb, 0, C.OUT / "s14_overlay_front.png", crop=(200, 400, 480, 620), zoom=3)
    overlay.write_overlay(comb, 90, C.OUT / "s14_overlay_side.png", crop=(620, 400, 820, 620), zoom=3)
    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s14_gen.blend"), compress=False)
    gates.finish()


main()
