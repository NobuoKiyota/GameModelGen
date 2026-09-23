"""S18-1: 首のUV投影の歪みを直す（保留事項④）。

原因: 円柱投影（角度, Z）で、首の背中側の継ぎ目（角度が -π/+π をまたぐ場所）にある面は、
4隅の角度が「ほぼ+π」と「ほぼ-π」に分かれてしまい、UV上で画面の端から端まで引き伸ばされていた
（実際にUVワイヤーを描いて発見）。

修正: 面ごとに、4隅の角度を「その面の最初の頂点の角度に最も近くなるよう」2π単位でずらす（unwrap）。
首は現在まだ単色（肌色）のベタ塗りのままなので、UVの区画・並び方を変えても見た目（色）には影響しない。
既存のFace/Eye等・区画配置・塗った色は変更しない（首の内部パラメータ化だけを直す）。

入力: out/face_s17e_gen.blend   出力: out/face_s17e_gen.blend（上書き）, out/s18_1_report.json, out/s18_1_*.png
実行: blender --background --factory-startup --python steps/s18_fix_neck_uv.py
"""
import math
import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402

STEP = "s18_1"
gates = C.Gates(STEP)
NECK_Z = -0.19
POCKET_VMIN = 463
MOUTH_FACE_RANGE = range(460, 480)


def face_group(verts, p):
    if p.index < 460 and all(vi >= POCKET_VMIN for vi in p.vertices):
        return "eye_socket"
    if p.index in MOUTH_FACE_RANGE:
        return "mouth"
    c = sum((verts[vi].co for vi in p.vertices), verts[p.vertices[0]].co * 0) / len(p.vertices)
    if c.z < NECK_Z:
        return "neck"
    return "front" if p.normal.y < 0 else "back"


def project_neck(v, cy):
    ang = math.atan2(v.y - cy, -v.x)
    return (ang + math.pi) / (2 * math.pi), v.z


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s17e_gen.blend"))
    face = bpy.data.objects["Face"]
    me = face.data
    verts = me.vertices
    cy = sum(v.co.y for v in verts) / len(verts)
    groups = {p.index: face_group(verts, p) for p in me.polygons}
    neck_faces = [p for p in me.polygons if groups[p.index] == "neck"]
    gates.check("首の面が見つかった", len(neck_faces) > 0, len(neck_faces))

    uv = me.uv_layers.active.data
    old_u0 = min(uv[li].uv.x for p in neck_faces for li in range(p.loop_start, p.loop_start + p.loop_total))
    old_u1 = max(uv[li].uv.x for p in neck_faces for li in range(p.loop_start, p.loop_start + p.loop_total))
    old_v0 = min(uv[li].uv.y for p in neck_faces for li in range(p.loop_start, p.loop_start + p.loop_total))
    old_v1 = max(uv[li].uv.y for p in neck_faces for li in range(p.loop_start, p.loop_start + p.loop_total))
    gates.note("修正前の首の区画（既存の配置。この矩形の中に収まるよう作り直す）", (round(old_u0, 4), round(old_v0, 4), round(old_u1, 4), round(old_v1, 4)))

    # ---- 修正前: 継ぎ目をまたいで引き伸ばされている面の数を数える（1周= u幅1.0に対し、面の見かけの u幅 > 0.5 のものが該当）
    def face_u_span(p, use_fix):
        raw = [project_neck(verts[vi].co, cy) for vi in p.vertices]
        if not use_fix:
            us = [u for u, v in raw]
        else:
            ref = raw[0][0]
            us = []
            for u, v in raw:
                while u - ref > 0.5:
                    u -= 1.0
                while u - ref < -0.5:
                    u += 1.0
                us.append(u)
        return max(us) - min(us)

    n_stretched_before = sum(1 for p in neck_faces if face_u_span(p, False) > 0.4)
    n_stretched_after = sum(1 for p in neck_faces if face_u_span(p, True) > 0.4)
    gates.check("修正後、継ぎ目で伸びる面が無くなった", n_stretched_after == 0, (n_stretched_before, n_stretched_after))

    # ---- 面ごとにunwrapして書き直し、既存の区画（old_u0..old_v1）に収まるようスケール・平行移動
    new_local = {}
    nb = [1e9, 1e9, -1e9, -1e9]
    for p in neck_faces:
        raw = [project_neck(verts[vi].co, cy) for vi in p.vertices]
        ref = raw[0][0]
        for li, (u, v) in zip(range(p.loop_start, p.loop_start + p.loop_total), raw):
            uu = u
            while uu - ref > 0.5:
                uu -= 1.0
            while uu - ref < -0.5:
                uu += 1.0
            new_local[li] = (uu, v)
            nb[0], nb[1], nb[2], nb[3] = min(nb[0], uu), min(nb[1], v), max(nb[2], uu), max(nb[3], v)

    pad = 0.0
    s = min((old_u1 - old_u0) * (1 - 2 * pad) / max(nb[2] - nb[0], 1e-6), (old_v1 - old_v0) * (1 - 2 * pad) / max(nb[3] - nb[1], 1e-6))
    ox = old_u0 + (old_u1 - old_u0) / 2 - (nb[0] + (nb[2] - nb[0]) / 2) * s
    oy = old_v0 + (old_v1 - old_v0) / 2 - (nb[1] + (nb[3] - nb[1]) / 2) * s
    for li, (u, v) in new_local.items():
        uv[li].uv = (u * s + ox, v * s + oy)

    x0 = min(uv[li].uv.x for p in neck_faces for li in range(p.loop_start, p.loop_start + p.loop_total))
    x1 = max(uv[li].uv.x for p in neck_faces for li in range(p.loop_start, p.loop_start + p.loop_total))
    y0 = min(uv[li].uv.y for p in neck_faces for li in range(p.loop_start, p.loop_start + p.loop_total))
    y1 = max(uv[li].uv.y for p in neck_faces for li in range(p.loop_start, p.loop_start + p.loop_total))
    gates.check("修正後も、首のUVは元の区画の範囲内に収まっている",
                x0 >= old_u0 - 1e-4 and x1 <= old_u1 + 1e-4 and y0 >= old_v0 - 1e-4 and y1 <= old_v1 + 1e-4,
                (round(x0, 4), round(y0, 4), round(x1, 4), round(y1, 4)))

    # ---- 他の区画と重なっていないか（他オブジェクトのUV範囲と比較）
    others = ["Eye", "Eyebrow", "DoubleLid", "Eyelash.001", "Eyelash.002", "Eyelash.003"]
    overlap_any = False
    for n in others:
        o = bpy.data.objects[n]
        ouv = o.data.uv_layers.active.data
        ox0 = min(l.uv.x for l in ouv); ox1 = max(l.uv.x for l in ouv)
        oy0 = min(l.uv.y for l in ouv); oy1 = max(l.uv.y for l in ouv)
        if not (x1 <= ox0 or ox1 <= x0 or y1 <= oy0 or oy1 <= y0):
            overlap_any = True
    gates.check("修正後、他オブジェクトの区画と重なっていない", not overlap_any)

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s17e_gen.blend"), compress=False)

    # ---- UVワイヤーのレビュー画像
    W = H = 1024
    arr = np.ones((H, W, 3), dtype='float32')

    def px(u, v):
        return int(u * (W - 1)), int((1 - v) * (H - 1))

    def line(a, b):
        x0_, y0_ = a
        x1_, y1_ = b
        n = max(abs(x1_ - x0_), abs(y1_ - y0_), 1)
        for i in range(n + 1):
            t = i / n
            x = int(x0_ + (x1_ - x0_) * t)
            y = int(y0_ + (y1_ - y0_) * t)
            if 0 <= x < W and 0 <= y < H:
                arr[y, x] = (0.8, 0.1, 0.1)
    for p in me.polygons:
        pts = [uv[li].uv for li in range(p.loop_start, p.loop_start + p.loop_total)]
        for k in range(len(pts)):
            line(px(*pts[k]), px(*pts[(k + 1) % len(pts)]))
    im = bpy.data.images.new("wire_s18", W, H, alpha=False)
    out = np.dstack([arr, np.ones((H, W, 1), dtype='float32')])[::-1].astype('float32').ravel()
    im.pixels.foreach_set(out)
    im.filepath_raw = str(C.OUT / "s18_1_face_uv_wire.png")
    im.file_format = 'PNG'
    im.save()

    gates.finish()


main()
