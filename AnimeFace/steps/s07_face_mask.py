"""S07: 顔のマスクを後ろへ広げる（動画 13:42〜15:05）。

動画の操作: 目の横から顎までの外側のラインを Ctrl+クリック（最短経路）でまとめて選ぶ → E Y で後ろへ押し出す
            → 一番下が首の付け根の近くに来るまで持っていく → 顎の側から延長して面を貼り、顔のマスクを広げる
            → 一番上のおでこのラインは、真上から見てなだらかなカーブになるように整える
            → 「このくらいまでできたところでサブディビジョンサーフェイスを追加」（ここまでが S07。Subsurf は S08）
ここでは同じ構造（外側のライン 15頂点を後ろへ押し出した新しい列＋四角面14枚、おでこのラインの整形）を bmesh で構築する。

  外側のライン: 目尻の頂点12 → 頬の帯の外側の縦の辺（分割で増えた頂点を含む）→ 耳の下の端50 → 顎の列 → 顎先44（Xの絶対値が小さくなる）
  押し出し先の Y: 帯の外側の縦の列は、側面下絵の耳の前縁（u最大の黒画素）。顎の列は、耳の下の端の Y から
                  顎先では首の前（側面の輪郭が顎の下から首へ落ちる線）へ、X の2乗で滑らかに変化。X・Z は変えない（E Y と同じ）
  おでこのライン（上辺 17→t2→t1→N0）: 鼻根 N0 で傾き0の放物線 Y = Y_N0 + (Y_17 − Y_N0)·(X/X_17)² に整える（真上から見て滑らか）

入力: out/face_s06_human.blend   出力: out/face_s07_gen.blend, out/s07_report.json, out/s07_*_overlay.png
実行: blender --background --factory-startup --python steps/s07_face_mask.py
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402
import measure as M  # noqa: E402
import overlay  # noqa: E402

STEP = "s07"
gates = C.Gates(STEP)

EYE_OUTER, EAR_END, CHIN = 12, 50, 44                     # 目尻の頂点、耳の下の端（顎の列の外端）、顎先
EYE_CORNER, NOSE_ROOT = 17, 40
HEAD_CENTER = Vector((0.0, 0.0, -0.03))                   # 面が「外向き」かの判定用（頭の中心付近）
SIL_INSET_PX = 3


def ang_range(pts):
    lo, hi = 180.0, 0.0
    for k in range(4):
        a, b, c = pts[k - 1], pts[k], pts[(k + 1) % 4]
        v1, v2 = (a - b).normalized(), (c - b).normalized()
        ang = math.degrees(math.acos(max(-1, min(1, v1.dot(v2)))))
        lo, hi = min(lo, ang), max(hi, ang)
    return lo, hi


def newell(pts):
    n = Vector((0, 0, 0))
    for k in range(len(pts)):
        a, b = pts[k], pts[(k + 1) % len(pts)]
        n += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
    return n


def outward(ids, pos):
    """頭の中心から見て外向きの法線になる巻き順にそろえる。"""
    pts = [pos[k] for k in ids]
    n = newell(pts)
    c = sum(pts, Vector()) / len(pts)
    return ids if n.dot(c - HEAD_CENTER) > 0 else ids[::-1]


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s06_human.blend"))
    obj = bpy.data.objects["Face"]
    if obj.mode != "OBJECT":
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="OBJECT")
    mesh = obj.data
    before = [v.co.copy() for v in mesh.vertices]
    n_v, n_f = len(mesh.vertices), len(mesh.polygons)
    gates.check("入力: 119頂点・面92・全面四角形・Mirror のみ",
                (n_v, n_f) == (119, 92) and all(len(p.vertices) == 4 for p in mesh.polygons) and [m.type for m in obj.modifiers] == ["MIRROR"],
                (n_v, n_f))

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    def refresh():
        bm.verts.index_update()
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

    # --- 外側のライン: 境界の辺を 目尻の頂点12 → 顎先44 までたどる（Ctrl+クリックの最短経路選択に相当）---
    adj = {}
    for e in bm.edges:
        if len(e.link_faces) == 1:
            a, b = (v.index for v in e.verts)
            adj.setdefault(a, []).append(b)
            adj.setdefault(b, []).append(a)
    chain = [EYE_OUTER]
    cur = min(adj[EYE_OUTER], key=lambda i: bm.verts[i].co.z)            # 目の外輪の上側ではなく、帯の外側（下向き）へ
    seen = {EYE_OUTER}
    while True:
        chain.append(cur)
        seen.add(cur)
        if cur == CHIN:
            break
        nxt = [i for i in adj[cur] if i not in seen]
        if not nxt:
            break
        cur = nxt[0]
    gates.check("外側のライン: 目尻の頂点12から顎先44まで、境界の辺で15頂点", chain[0] == EYE_OUTER and chain[-1] == CHIN and len(chain) == 15,
                (len(chain), chain))
    i_ear = chain.index(EAR_END) if EAR_END in chain else -1
    gates.check("外側のライン: 耳の下の端50が列の外側の縦の部分と顎の列の境目（先頭から9番目）", i_ear == 8, i_ear)
    xs = [bm.verts[i].co.x for i in chain]
    gates.check("外側のライン: 顎の列（50→顎先）は X の絶対値が単調に減り、顎先は X=0", all(abs(a) > abs(b) for a, b in zip(xs[8:], xs[9:])) and xs[-1] == 0.0,
                [round(x, 3) for x in xs[8:]])

    # --- 押し出し先の Y（側面下絵から）---
    sil = M.side_silhouette()
    ear_u = M.side_ear_front_u()
    neck_u, neck_row = M.side_neck_front_u()
    y_ear = -(ear_u - SIL_INSET_PX * 0 - C.COL0) * C.K                   # 耳の前縁の外側の縁を、そのまま顔のマスクの後ろの縁にする
    y_neck = -(neck_u - SIL_INSET_PX - C.COL0) * C.K
    x_ear_end = bm.verts[EAR_END].co.x
    targets = []
    for k, i in enumerate(chain):
        v = bm.verts[i].co
        if k <= 8:
            y = y_ear
        else:
            t = (v.x / x_ear_end) ** 2                                   # 顎先 0 → 耳の下の端 1
            y = y_neck + (y_ear - y_neck) * t
        targets.append((v.x, y, v.z))

    # --- 押し出し（E Y）: 新しい列を作り、四角面を貼る ---
    new_ids = []
    for p in targets:
        nv = bm.verts.new(p)
        new_ids.append(nv)
    refresh()
    new_idx = [v.index for v in new_ids]
    pos = {i: bm.verts[i].co.copy() for i in chain + new_idx}
    for k in range(len(chain) - 1):
        q = outward([chain[k], chain[k + 1], new_idx[k + 1], new_idx[k]], pos)
        bm.faces.new([bm.verts[j] for j in q])

    # --- おでこのライン（上辺 17→t2→t1→N0）を放物線に整える ---
    z17 = bm.verts[EYE_CORNER].co.z
    top = sorted([v for v in bm.verts if abs(v.co.z - z17) < 1e-4 and bm.verts[EYE_CORNER].co.x < v.co.x < 0 and v.index not in (EYE_CORNER, NOSE_ROOT)],
                 key=lambda v: v.co.x)
    gates.check("おでこのライン: 17 と鼻根 N0 の間に頂点が2つ（t2, t1）", len(top) == 2, [v.index for v in top])
    x17, y17, yN0 = bm.verts[EYE_CORNER].co.x, bm.verts[EYE_CORNER].co.y, bm.verts[NOSE_ROOT].co.y
    y_before = [v.co.y for v in top]
    top_idx = [v.index for v in top]                       # free() 後は BMVert を参照できないため番号を控える
    for v in top:
        v.co.y = yN0 + (y17 - yN0) * (v.co.x / x17) ** 2

    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    # --- ソースのトポロジー ---
    n_new_v, n_new_f = len(mesh.vertices) - n_v, len(mesh.polygons) - n_f
    moved = [i for i in range(n_v) if (mesh.vertices[i].co - before[i]).length > 0]
    gates.check("既存の頂点は、おでこのライン（t2・t1）の Y 以外動いていない",
                sorted(moved) == sorted(top_idx) and all(abs(mesh.vertices[i].co.x - before[i].x) < 1e-9 and abs(mesh.vertices[i].co.z - before[i].z) < 1e-9 for i in moved),
                moved)
    gates.check("新しい頂点15個（押し出した列）・四角面14枚", n_new_v == 15 and n_new_f == 14 and all(len(p.vertices) == 4 for p in mesh.polygons),
                (n_new_v, n_new_f))
    at0 = [i for i in range(n_v, len(mesh.vertices)) if mesh.vertices[i].co.x == 0.0]
    gates.check("X=0 の新しい頂点は、顎先を押し出した1つだけ", len(at0) == 1, at0)
    gates.check("モディファイアは Mirror のみ（Apply なし）", [m.type for m in obj.modifiers] == ["MIRROR"])

    # --- 押し出し先の一致（画像から再測定した値と比べる）---
    ys_col = [mesh.vertices[i].co.y for i in new_idx[:9]]
    gates.check("列の外側の縦の部分9頂点: Y が側面の耳の前縁（再測定）に一致 ±1px", all(abs(-(y / C.K) + 0 - (ear_u - C.COL0)) <= 1 for y in ys_col),
                (round(ys_col[0], 4), ear_u))
    y_chin_new = mesh.vertices[new_idx[-1]].co.y
    gates.check("顎先の押し出し先: Y が側面の首の前の輪郭（再測定、行%d〜%d）の内側に一致 ±1px" % neck_row,
                abs(-(y_chin_new / C.K) - (neck_u - SIL_INSET_PX - C.COL0)) <= 1, round(y_chin_new, 4))
    ys_jaw = [mesh.vertices[i].co.y for i in new_idx[8:]]
    gates.check("顎の列の押し出し先は、耳の下→顎先で単調に前へ（首の前へ）", all(a > b for a, b in zip(ys_jaw, ys_jaw[1:])),
                [round(y, 3) for y in ys_jaw])
    gates.check("押し出し先の X・Z は元と同じ（E Y と同じ、後ろへ動かすだけ）",
                all(abs(mesh.vertices[c].co.x - mesh.vertices[n].co.x) < 1e-9 and abs(mesh.vertices[c].co.z - mesh.vertices[n].co.z) < 1e-9
                    for c, n in zip(chain, new_idx)))

    # --- おでこのライン ---
    tops = [mesh.vertices[EYE_CORNER].co] + [mesh.vertices[i].co for i in top_idx] + [mesh.vertices[NOSE_ROOT].co]
    curve_ok = all(abs(p.y - (yN0 + (y17 - yN0) * (p.x / x17) ** 2)) < 1e-6 for p in tops)
    slopes = [(tops[k + 1].y - tops[k].y) / (tops[k + 1].x - tops[k].x) for k in range(3)]
    gates.check("おでこのライン: 放物線（鼻根で傾き0）に乗っていて、傾きが鼻根に向かって単調に0へ近づく",
                curve_ok and all(abs(a) > abs(b) for a, b in zip(slopes, slopes[1:])), [round(s, 3) for s in slopes])
    gates.note("おでこのライン t2・t1 の Y の変化: %s mm（前が正）" % [round(-(v.co.y - y0) * 1000, 1) for v, y0 in zip([mesh.vertices[i] for i in top_idx], y_before)])

    # --- Mirror 後 ---
    dg = bpy.context.evaluated_depsgraph_get()
    ev = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    Vn, En, Fn = len(ev.vertices), len(ev.edges), len(ev.polygons)
    pairs = [tuple(sorted(e.vertices)) for e in ev.edges]
    gates.check("Mirror 後: 頂点254（+29）・辺468（+57）・面212（+28）", (Vn, En, Fn) == (254, 468, 212), (Vn, En, Fn))
    gates.check("Mirror 後: 辺の重複なし", len(set(pairs)) == len(pairs), f"E={En}")
    share = {}
    for p in ev.polygons:
        vs = list(p.vertices)
        for k in range(4):
            a, b = vs[k], vs[(k + 1) % 4]
            share.setdefault(tuple(sorted((a, b))), []).append((a, b))
    gates.check("Mirror 後: 3枚以上の面が共有する辺がない", max(len(v) for v in share.values()) <= 2, max(len(v) for v in share.values()))
    bad_wind = [e for e, d in share.items() if len(d) == 2 and d[0] != (d[1][1], d[1][0])]
    gates.check("Mirror 後: 隣り合う面の巻き順が一貫している", not bad_wind, len(bad_wind))
    bad_out = [p.index for p in ev.polygons if p.normal.dot(p.center - HEAD_CENTER) <= 0]
    gates.check("Mirror 後: 全面の法線が頭の外側を向いている", not bad_out, bad_out[:10])
    coords = {(round(v.co.x, 6), round(v.co.y, 6), round(v.co.z, 6)) for v in ev.vertices}
    gates.check("Mirror 後: 左右対称・頂点の重複なし", all((round(-x, 6), y, z) in coords for (x, y, z) in coords) and len(coords) == Vn)
    adj2 = {}
    for e, d in share.items():
        if len(d) == 1:
            adj2.setdefault(e[0], []).append(e[1])
            adj2.setdefault(e[1], []).append(e[0])
    seen2, loops = set(), []
    for s in adj2:
        if s in seen2:
            continue
        stack, comp = [s], 0
        while stack:
            x = stack.pop()
            if x in seen2:
                continue
            seen2.add(x)
            comp += 1
            stack += adj2[x]
        loops.append(comp)
    gates.check("Mirror 後: 境界のループは4つ（目の穴2・口の穴1・外周1）", len(loops) == 4, sorted(loops))
    gates.check("Mirror 後: オイラー数 -2", Vn - En + Fn == -2, f"V={Vn} E={En} F={Fn}")

    # --- 四角形の歪み（今回貼った14枚）---
    new_pts = [[mesh.vertices[i].co for i in p.vertices] for p in list(mesh.polygons)[n_f:]]
    lo = min(ang_range(p)[0] for p in new_pts)
    hi = max(ang_range(p)[1] for p in new_pts)
    gates.check("今回貼った四角形14枚: 内角が 25°〜155° の範囲", lo >= 25 and hi <= 155, f"最小{lo:.0f}° 最大{hi:.0f}°")

    for ang, tag, crop, zoom in [(90, "side", (300, 100, 900, 900), 1), (45, "a45", (150, 100, 850, 900), 1)]:
        overlay.write_overlay(ev, ang, C.OUT / f"s07_{tag}_overlay.png", crop=crop, zoom=zoom)
    overlay.write_wire_top(ev, C.OUT / "s07_top_wire.png", zoom=1, crop=(112, 112, 912, 912))
    gates.check("レビュー画像3枚（側面・45°・真上）を出力", all((C.OUT / f).exists() for f in ("s07_side_overlay.png", "s07_a45_overlay.png", "s07_top_wire.png")))

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s07_gen.blend"), compress=False)
    gates.finish()


main()
