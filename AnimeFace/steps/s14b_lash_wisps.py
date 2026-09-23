"""S14b: 細いまつ毛の房（ピョコ毛）を、主まつ毛にぶっ刺す形で追加する（後編 動画 07:43〜10:00）。

字幕との対応:
  07:43〜07:58 房になる辺を複製、クリースを外す、E Y で前へ、S で縮小            → 房ごとに、主まつ毛の面から根元の輪を作り、前（皮膚の法線方向）へ縮小して伸ばす
  07:58〜08:16 Ctrl+R でループを横に追加、G Z でくるんと（横幅も縮小）           → 中間の輪を1つ挟み、横（面内で左右）へ少しずらして曲げる（くるみ）
  08:16〜08:27 真ん中にもう1本ループ追加、下にもくるんと                         → 先端に向けて、もう一度、別の向き（下寄り）へ曲げる
  08:41       横端を F で面張り、クリースをかける                               → 根元・先端を閉じ、中間の輪の稜にクリース1.0（主まつ毛の前の稜と同じ扱い）
  08:58〜09:40 位置・回転を調整し、太いまつ毛にぶっ刺す配置                       → 根元は主まつ毛の内側（表面より奥）に埋める。房の数・場所は、下絵の目じり寄りの小さい房状の跳ねに合わせる（厳密な一致は求めない。動画も「だいたいの位置」）
  09:40〜10:00 L で選択、Shift+D で複製、他の場所にも配置                        → 主まつ毛の外眼角寄りの3か所（リング9・11・13相当）に、向き・長さを変えて複製

設計（1回目の生成は、まっすぐな針のようになって不自然だったため、作り直した。反省は LEARNINGS.md）:
  - 房は、S14c と同じ「別の閉じた管をぶっ刺す」方式。ただし断面4点・5輪（根元・1/4・2/3・3/4・先端）を、根元→先端の2次ベジエでなだらかに曲げ、根元から先端へ滑らかに細くする（直線3点の「く」の字ではなく、曲がった毛に見えるように）
  - 出す向きは、主まつ毛の断面（リング）に接する面の法線の平均（上＋やや手前を向く）。房どうしが重ならないよう、間を大きく空けた2か所（リング4・9）にした
  - 房の向き・長さ・くるみは、下絵にある房状の跳ねの見た目に合わせた目安（下絵から厳密に測っていない。要確認）。大きさは、主まつ毛・顔・黒目のどれとも交差しない組み合わせを探索して選ぶ

入力: out/face_s14c_gen.blend   出力: out/face_s14b_gen.blend, out/s14b_report.json, out/s14b_*.png
実行: blender --background --factory-startup --python steps/s14b_lash_wisps.py
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402
import overlay  # noqa: E402

STEP = "s14b"
gates = C.Gates(STEP)

# 房を置く主まつ毛の輪の番号（S14c のリング番号）。間を大きく空け、房どうしが重ならないようにする。大きさ（長さ・太さ・くるみ）は、交差しない組み合わせを探索して決める（下）
WISP_RINGS = [4, 9]
EMBED = 0.006        # 根元を、主まつ毛の面の内側へ埋め込む深さ
N_SEG = 4            # 房の分割数（根元・1/3・2/3・先端の4輪。曲がりを滑らかにする）


def rd(v):
    return tuple(round(float(c) * 1000, 1) for c in v)


def make_wisp(base_c, out_dir, side_dir, length, base_w, curl_mm):
    """根元 base_c（主まつ毛の面の上）から、ほぼ真上（out_dir。世界の +Z 寄り）へ伸び、途中でお辞儀のように前へ曲がる、細い毛。
    中心線は、根元→先端を2次ベジエ（制御点は途中で curl_mm だけ前へ）でなだらかに曲げる。4輪（根元・1/3・2/3・先端）、四角形だけ、閉じた形。
    戻り値: 頂点リスト・面リスト（ローカル添字）・稜（前側）の頂点添字。"""
    out_dir = out_dir.normalized()
    up2 = out_dir.cross(side_dir)
    up2.y = 0.0                                  # 曲げは正面から見た平面（X-Z）内だけで行う（奥行きへ曲げると、正面から見て輪に見える）
    if up2.length < 1e-6:
        up2 = Vector((1, 0, 0))
    up2.normalize()
    side = up2.cross(out_dir).normalized()       # 房の「横」（幅の向き）

    def ring(center, hw, ht):
        return [center + side * hw, center + up2 * ht, center - side * hw, center - up2 * ht]

    ctrl = base_c + out_dir * (length * 0.5) + up2 * curl_mm      # ベジエの制御点（前へ、くるっと曲げる）
    tip_anchor = base_c + out_dir * length
    verts, ridge = [], []
    for i in range(N_SEG + 1):
        t = i / N_SEG
        center = (1 - t) ** 2 * (base_c - out_dir * (EMBED if i == 0 else 0.0)) + 2 * (1 - t) * t * ctrl + t ** 2 * tip_anchor
        w = base_w * (1.0 - 0.82 * t)                                # 根元から先端へ、なだらかに細くする
        h = w * 0.55
        rr = ring(center, max(w, 1e-5), max(h, 1e-5))
        base_idx = len(verts)
        verts.extend(rr)
        ridge.append(base_idx + 1)
    faces = []
    for i in range(N_SEG):
        a, b = i * 4, (i + 1) * 4
        for j in range(4):
            faces.append([a + j, a + (j + 1) % 4, b + (j + 1) % 4, b + j])
    faces.append([3, 2, 1, 0])                     # 根元を閉じる
    faces.append([N_SEG * 4, N_SEG * 4 + 1, N_SEG * 4 + 2, N_SEG * 4 + 3])   # 先端を閉じる
    return verts, faces, ridge


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s14c_gen.blend"))
    for o in bpy.data.objects:
        if o.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
    face, eye, lash = bpy.data.objects["Face"], bpy.data.objects["Eye"], bpy.data.objects["Eyelash"]
    me = lash.data
    gates.check("入力: Eyelash は Mirror → Subdivision（表示1・レンダー2）、頂点88・面84",
                [m.type for m in lash.modifiers] == ["MIRROR", "SUBSURF"] and len(me.vertices) == 88 and len(me.polygons) == 84)
    n_v0, n_f0 = len(me.vertices), len(me.polygons)
    P = [v.co.copy() for v in me.vertices]

    def ring_of(k):
        return [P[4 * k + j] for j in range(4)]

    def face_normal(poly_idx):
        vs = [P[i] for i in me.polygons[poly_idx].vertices]
        n = Vector((0, 0, 0))
        for q in range(len(vs)):
            a, b = vs[q], vs[(q + 1) % len(vs)]
            n += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
        area = n.length / 2.0
        return n.normalized(), area

    def ring_normal(k):
        """主まつ毛の、リング k の断面に接する面の法線の平均（前へ張り出す向き）。bpy のメッシュから直接（bmesh は使わない）。"""
        c = sum(ring_of(k), Vector()) / 4
        idxs = {4 * k + j for j in range(4)}
        nrm = Vector((0, 0, 0))
        for pi in range(n_f0):
            vs = set(me.polygons[pi].vertices)
            if len(idxs & vs) >= 2:
                n, a = face_normal(pi)
                nrm += n * a
        return nrm.normalized(), c

    fverts0 = [tuple(v.co) for v in me.vertices]
    main_polys0 = [list(p.vertices) for p in me.polygons]
    bvh_main0 = BVHTree.FromPolygons(fverts0, main_polys0)
    fverts_face = [tuple(v.co) for v in face.data.vertices]
    bvh_face0 = BVHTree.FromPolygons(fverts_face, [list(p.vertices) for p in face.data.polygons])
    fverts_eye = [tuple(v.co) for v in eye.data.vertices]
    bvh_eye0 = BVHTree.FromPolygons(fverts_eye, [list(p.vertices) for p in eye.data.polygons])
    VPW = (N_SEG + 1) * 4                          # 房1つあたりの頂点数（5輪×4）
    FPW = N_SEG * 4 + 2                             # 房1つあたりの面数（帯16＋端2）
    VIS_LOCAL = set(range(4, N_SEG * 4)) | {N_SEG * 4 + 1}   # 根元→1/4の帯（埋め込み区間）と根元のふたを除く

    def visible_polys(faces):
        return [faces[i] for i in range(len(faces)) if i in VIS_LOCAL]

    # 候補: (長さmm, 太さの倍率, くるみ＝長さに対する割合)。くるみは正負どちらも試す
    cand_params = []
    for length_mm in (11, 9, 7, 5):
        for wmul in (0.26, 0.20, 0.15):
            for curl_frac in (0.0, 0.15, -0.15, 0.3, -0.3):
                cand_params.append((length_mm / 1000, wmul, curl_frac))

    new_verts, new_faces, all_ridge = [], [], []
    base_offset = len(P)
    wisp_bases, chosen_log = [], []
    for k in WISP_RINGS:
        nrm, c = ring_normal(k)
        w0 = (ring_of(k)[0] - ring_of(k)[2]).length / 2
        side_ref = Vector((0, 0, 1))
        chosen = None
        for length, wmul, curl_frac in cand_params:
            base_w = w0 * wmul
            curl_mm = length * curl_frac
            verts, faces, ridge = make_wisp(c, nrm, side_ref, length, base_w, curl_mm)
            vis = visible_polys(faces)
            allv = fverts0 + verts
            offv = len(fverts0)
            vis_g = [[offv + i for i in f] for f in vis]
            bl = BVHTree.FromPolygons(allv, vis_g)
            h_main = len(bl.overlap(bvh_main0))
            allv2 = fverts_face + verts
            bl2 = BVHTree.FromPolygons(allv2, [[len(fverts_face) + i for i in f] for f in vis])
            h_face = len(bl2.overlap(bvh_face0))
            allv3 = fverts_eye + verts
            bl3 = BVHTree.FromPolygons(allv3, [[len(fverts_eye) + i for i in f] for f in vis])
            h_eye = len(bl3.overlap(bvh_eye0))
            if h_main == 0 and h_face == 0 and h_eye == 0:
                chosen = (length, wmul, curl_frac, verts, faces, ridge)
                break
        if chosen is None:                                                       # どれも交差しないものが見つからないときは、房を作らない（安全側）
            chosen_log.append((k, "交差せずに置けなかったので、この房は作らない"))
            continue
        length, wmul, curl_frac, verts, faces, ridge = chosen
        chosen_log.append((k, round(length * 1000, 1), wmul, curl_frac))
        b = len(new_verts) + base_offset
        new_verts.extend(verts)
        new_faces.extend([[b + i for i in f] for f in faces])
        all_ridge.extend(b + i for i in ridge[1:])   # 根元の稜は主まつ毛に埋まるので、見える分だけ
        wisp_bases.append((b, c, nrm))
    n_wisps_made = len(wisp_bases)
    gates.note("各房で採用した大きさ（リング番号, 長さmm, 太さの倍率, くるみ＝長さに対する割合）", chosen_log)
    gates.check("交差せずに置けた房が2つ以上", n_wisps_made >= 2, n_wisps_made)
    gates.check("作った房は、いずれも%d頂点・%d面（帯%d＋端2）" % (VPW, FPW, N_SEG * 4),
                len(new_verts) == n_wisps_made * VPW and len(new_faces) == n_wisps_made * FPW, f"{len(new_verts)}頂点 {len(new_faces)}面")

    # ---- メッシュへ追加
    bm2 = bmesh.new()
    bm2.from_mesh(me)
    vmap = list(bm2.verts)
    for v in new_verts:
        vmap.append(bm2.verts.new(v))
    bm2.verts.ensure_lookup_table()
    bm2.verts.index_update()
    added_faces = []
    for f in new_faces:
        added_faces.append(bm2.faces.new([vmap[i] for i in f]))
    bm2.faces.ensure_lookup_table()
    bm2.faces.index_update()
    bm2.normal_update()
    # 向き: 各房（成分）の符号付き体積が正になるように
    for k in range(n_wisps_made):
        idx0 = base_offset + k * VPW
        comp_faces = [f for f in added_faces if all(v.index >= idx0 and v.index < idx0 + VPW for v in f.verts)]
        vol = 0.0
        for f in comp_faces:
            p0 = f.verts[0].co
            for q in range(1, len(f.verts) - 1):
                vol += p0.dot(f.verts[q].co.cross(f.verts[q + 1].co)) / 6.0
        if vol < 0:
            bmesh.ops.reverse_faces(bm2, faces=comp_faces)
    bm2.faces.ensure_lookup_table()
    bm2.faces.index_update()
    bm2.edges.ensure_lookup_table()
    bm2.edges.index_update()
    bm2.verts.ensure_lookup_table()
    bm2.verts.index_update()

    share = {}
    for f in bm2.faces:
        vs = list(f.verts)
        for j in range(len(vs)):
            a, b = vs[j], vs[(j + 1) % len(vs)]
            share.setdefault(frozenset((a.index, b.index)), []).append((a.index, b.index))
    gates.check("巻き順が一貫・3枚以上が共有する辺なし", all(len(d) <= 2 and (len(d) < 2 or d[0] == (d[1][1], d[1][0])) for d in share.values()))
    gates.check("価数2の頂点がない（房も含めて）", all(len(v.link_edges) >= 3 for v in bm2.verts), sorted({len(v.link_edges) for v in bm2.verts}))

    # 符号付き体積（各房）
    vols = []
    for k in range(n_wisps_made):
        idx0 = base_offset + k * VPW
        fl = [f for f in bm2.faces if all(idx0 <= v.index < idx0 + VPW for v in f.verts)]
        vol = 0.0
        for f in fl:
            p0 = f.verts[0].co
            for q in range(1, len(f.verts) - 1):
                vol += p0.dot(f.verts[q].co.cross(f.verts[q + 1].co)) / 6.0
        vols.append(vol)
    gates.check("各房の面の向きが外向き（符号付き体積が正）", all(v > 0 for v in vols), [f"{v * 1e9:.2f}mm³" for v in vols])

    # 自己交差（房どうし・房と主まつ毛。根元の埋め込み部分は主管と重なるので、根元の輪だけは除く）
    # 生成時の Python のデータ（P・new_verts・new_faces）から直接、確認しなおす（bm2 の .index に頼らない）
    all_pts = P + new_verts
    all_pts_t = [tuple(p) for p in all_pts]
    bvh_main_final = BVHTree.FromPolygons(all_pts_t, [list(P_i) for P_i in [me.polygons[i].vertices for i in range(n_f0)]])
    wisp_hits_total = 0
    for k in range(n_wisps_made):
        base_face = k * FPW
        polys = [new_faces[base_face + q] for q in VIS_LOCAL]
        if k == 0:
            gates.note("房0: 主管との交差の確認に使う面（可視部分）の数", len(polys))
        bvh_w = BVHTree.FromPolygons(all_pts_t, polys)
        wisp_hits_total += len(bvh_w.overlap(bvh_main_final))
    gates.check("房（主管に埋まる根元を除く、可視部分）が、主まつ毛と交差していない", wisp_hits_total == 0, wisp_hits_total)
    wisp_self = 0
    for k in range(n_wisps_made):
        base_face = k * FPW
        polys = [new_faces[base_face + q] for q in range(FPW)]
        bvh_w = BVHTree.FromPolygons(all_pts_t, polys)
        wisp_self += len([1 for x, y in bvh_w.overlap(bvh_w) if x < y and not (set(polys[x]) & set(polys[y]))])
    gates.check("各房の中で、面どうしが交差していない", wisp_self == 0, wisp_self)

    # クリース: 房の前の稜（埋め込み区間を除く、隣り合う輪をつなぐ帯の辺）。
    # all_ridge には、房ごとに（根元を除いた）N_SEG 個の頂点番号が、房の出現順に並んでいる
    ridge_keys = set()
    idx = 0
    for k in range(n_wisps_made):
        seg = all_ridge[idx:idx + N_SEG]
        idx += N_SEG
        for a, b in zip(seg[:-1], seg[1:]):
            ridge_keys.add(frozenset((a, b)))
    bm2.to_mesh(me)
    bm2.free()
    me.update()
    ca = me.attributes["crease_edge"]
    marked = 0
    for e in me.edges:
        if frozenset(e.vertices) in ridge_keys:
            ca.data[e.index].value = 1.0
            marked += 1
    gates.check("房の前の稜（房の数×%d辺）にクリース1.0を追加" % (N_SEG - 1), marked == n_wisps_made * (N_SEG - 1), marked)
    for p in me.polygons:
        p.use_smooth = True
    gates.check("頂点・面: %d→%d・%d→%d" % (n_v0, len(me.vertices), n_f0, len(me.polygons)), len(me.vertices) == n_v0 + n_wisps_made * VPW and len(me.polygons) == n_f0 + n_wisps_made * FPW)
    gates.check("既存の頂点（主まつ毛）は動かしていない", all((me.vertices[i].co - P[i]).length < 1e-9 for i in range(n_v0)))
    gates.check("X<0（左目）の側だけ", max(v.co.x for v in me.vertices) < 0)
    gates.check("モディファイア（Mirror → Subdivision 1/2）のまま", [m.type for m in lash.modifiers] == ["MIRROR", "SUBSURF"] and (lash.modifiers[1].levels, lash.modifiers[1].render_levels) == (1, 2))

    # ---- 顔・黒目との交差（房だけ）
    fverts = [tuple(v.co) for v in face.data.vertices]
    bvh_face = BVHTree.FromPolygons(fverts, [list(p.vertices) for p in face.data.polygons])
    everts = [tuple(v.co) for v in eye.data.vertices]
    bvh_eye = BVHTree.FromPolygons(everts, [list(p.vertices) for p in eye.data.polygons])
    lverts = [tuple(v.co) for v in me.vertices]
    wisp_polys_visible = []
    for k in range(n_wisps_made):
        base_face = n_f0 + k * FPW
        wisp_polys_visible.extend([list(p.vertices) for p in me.polygons if p.index - base_face in VIS_LOCAL])
    bvh_wisps = BVHTree.FromPolygons(lverts, wisp_polys_visible)
    gates.check("房（可視部分）が、顔・黒目と交差していない", len(bvh_wisps.overlap(bvh_face)) == 0 and len(bvh_wisps.overlap(bvh_eye)) == 0,
                (len(bvh_wisps.overlap(bvh_face)), len(bvh_wisps.overlap(bvh_eye))))

    # ---- Mirror 後の検証
    sub = [m for m in lash.modifiers if m.type == "SUBSURF"][0]
    old_show = sub.show_viewport
    sub.show_viewport = False
    bpy.context.view_layer.update()
    ev = bpy.data.meshes.new_from_object(lash.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bme = bmesh.new()
    bme.from_mesh(ev)
    Vn, En, Fn = len(bme.verts), len(bme.edges), len(bme.faces)
    share2 = {}
    for f in bme.faces:
        vs = list(f.verts)
        for j in range(len(vs)):
            a, b = vs[j], vs[(j + 1) % len(vs)]
            share2.setdefault(frozenset((a.index, b.index)), []).append((a.index, b.index))
    gates.check("Mirror 後: 3枚以上が共有する辺なし・巻き順が一貫", max(len(v) for v in share2.values()) <= 2 and all(len(d) < 2 or d[0] == (d[1][1], d[1][0]) for d in share2.values()), f"V={Vn} E={En} F={Fn}")
    coords = {(round(v.co.x, 6), round(v.co.y, 6), round(v.co.z, 6)) for v in bme.verts}
    gates.check("Mirror 後: 左右対称・頂点の重複なし", all((round(-x, 6), y, z) in coords for (x, y, z) in coords) and len(coords) == Vn)
    bme.free()

    overlay.write_overlay(ev, 0, C.OUT / "s14b_front_wisps.png", crop=(190, 420, 340, 520), zoom=6)
    overlay.write_overlay(ev, 90, C.OUT / "s14b_side_wisps.png", crop=(640, 420, 800, 520), zoom=6)

    # 塗りつぶしのシルエット（ワイヤーの重なりで判断しづらいため、真の輪郭を見る）
    import numpy as np

    def fill_silhouette(mesh, view, crop, zoom, out_path):
        u0, v0, u1, v1 = crop
        arr = np.ones((v1 - v0, u1 - u0), dtype=bool)
        arr[:] = False
        for p in mesh.polygons:
            if max(mesh.vertices[i].co.x for i in p.vertices) > 1e-6:
                continue
            uv = [C.project(mesh.vertices[i].co, view) for i in p.vertices]
            for a in range(1, len(uv) - 1):
                tri = [uv[0], uv[a], uv[a + 1]]
                P_ = np.array(tri)
                yy0, yy1 = int(max(P_[:, 1].min() - v0, 0)), int(min(P_[:, 1].max() - v0, arr.shape[0] - 1))
                for y in range(yy0, yy1 + 1):
                    xs = []
                    for k2 in range(3):
                        pa, pb = P_[k2], P_[(k2 + 1) % 3]
                        yb = y + v0 + 0.5
                        if (pa[1] <= yb < pb[1]) or (pb[1] <= yb < pa[1]):
                            xs.append(pa[0] + (yb - pa[1]) * (pb[0] - pa[0]) / (pb[1] - pa[1]))
                    if len(xs) >= 2:
                        x0, x1 = sorted(xs)[:2]
                        xi0, xi1 = int(max(x0 - u0, 0)), int(min(x1 - u0, arr.shape[1] - 1))
                        arr[y, xi0:xi1 + 1] = True
        rgb = np.ones((arr.shape[0], arr.shape[1], 4), dtype=np.float32)
        rgb[arr, :3] = 0.0
        rgb = np.repeat(np.repeat(rgb, zoom, axis=0), zoom, axis=1)
        img = bpy.data.images.new("sil_tmp", rgb.shape[1], rgb.shape[0], alpha=False)
        img.pixels.foreach_set(rgb[::-1].ravel())
        img.filepath_raw = str(out_path)
        img.file_format = "PNG"
        img.save()
        bpy.data.images.remove(img)

    fill_silhouette(ev, 0, (190, 420, 340, 520), 6, C.OUT / "s14b_front_silhouette.png")
    sub.show_viewport = old_show
    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s14b_gen.blend"), compress=False)
    gates.finish()


main()
