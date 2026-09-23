"""S16: UV展開（後編 動画 13:47〜17:38）。

字幕との対応:
  13:47〜17:29 シームを入れて展開し、まつ毛は投影で展開、全部を1枚のテクスチャ空間に重ならないよう配置する
               → 下の「設計」参照。`bpy.ops.uv.unwrap` / `smart_project` / `pack_islands` は、**このBlenderをバックグラウンド実行（--background）で
                 動かすと、ウィンドウ（3Dビュー）が無いため、これらの UV 演算子が内部で失敗する**（`{'CANCELLED'}` を返し、UVが作られない・詰められない。
                 実際に確認した）。そのため、UV座標を Python の計算で直接求める（頂点の3D位置から、投影・パラメータ化で求める。演算子は使わない）
  16:33〜16:46 目のオブジェクトのスケールが均一でない警告 → スケール適用          → `bpy.ops.object.transform_apply(scale=True)` を Eye に適用
  17:43〜17:57 ベースカラーのテクスチャを追加（2048×2048、生成タイプ「ブランク」） → 新しい画像を作り、Principled BSDF のベースカラーに繋いだマテリアルを、共有で割り当てる

設計:
  - 帯状のオブジェクト（`Eyelash`・`Eyebrow`・`DoubleLid`・`Eyelash.001/.002/.003`）: 頂点が「駅（4頂点: O・F・I・K）× N」の並びなので、
    U = 駅の番号 / (駅数-1)、V = 駅の中の位置（O,F,I,K）/ 4、という、そのままの帯パラメータ化を UV にする
  - `Face`（頭・首）: 動画 14:12 のシーム（①前側／後ろ側を分ける ②首の付け根）と同じく、頂点を「前（Y<0）・後ろ（Y≥0）・首（Z<-0.19）」の3つに分け、
    前・後ろは正面／背面から見た平面投影（X, Z）、首は円柱状の投影（角度, Z）にする。1枚の円柱投影で頭全体を包むと、頭頂・首元の歪みが大きいため
    （1回目はこの3分割をせず円柱投影のみで済ませたが、動画のようにシームで分けていないとユーザーに指摘され、作り直した）
  - `Eye`（黒目）: 正面から見た平面投影（U,V = ローカルの X,Z）。浅いお椀型なので、歪みは小さい
  - 各オブジェクトの UV（それぞれ 0〜1 に正規化）を、3D表面積を重みにした矩形詰め（シェルフ法）で、1つのテクスチャ空間の重ならない区画に配置する

入力: out/face_s15c_gen.blend   出力: out/face_s16_gen.blend, out/s16_report.json, out/s16_*.png
実行: blender --background --factory-startup --python steps/s16_uv_unwrap.py
"""
import sys
from pathlib import Path

import bmesh
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402

STEP = "s16"
gates = C.Gates(STEP)

RIBBONS = ["Eyelash", "Eyebrow", "DoubleLid", "Eyelash.001", "Eyelash.002", "Eyelash.003"]
PROJECTED = ["Face", "Eye"]
OBJECTS = PROJECTED + RIBBONS


def mesh_area(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    a = sum(f.calc_area() for f in bm.faces)
    bm.free()
    return a


def set_uv(obj, per_vertex_uv):
    """per_vertex_uv: 頂点番号 -> (u, v)。各面のループに、対応する頂点の UV を書き込む。"""
    uv_layer = obj.data.uv_layers.new(name="UVMap")
    data = uv_layer.data
    for p in obj.data.polygons:
        for li in range(p.loop_start, p.loop_start + p.loop_total):
            vi = obj.data.loops[li].vertex_index
            u, v = per_vertex_uv[vi]
            data[li].uv = (u, v)


def uv_ribbon(obj):
    """帯状オブジェクト: 頂点が「駅×4（O,F,I,K）」の並びであることを確認し、そのままパラメータ化する。"""
    n = len(obj.data.vertices)
    gates.check(f"{obj.name}: 頂点数が4の倍数（駅×4の帯）", n % 4 == 0, n)
    n_st = n // 4
    per_vertex = {}
    for i in range(n_st):
        u = i / max(n_st - 1, 1)
        for j in range(4):
            per_vertex[4 * i + j] = (u, j / 4.0 + 0.05)
    set_uv(obj, per_vertex)
    return n_st


NECK_Z = -0.19    # これより下は首（動画 14:12「首の付け根にもシームを入れる」に対応する分割）


def project_front_back(v, cx_ignored=None):
    return v.x, v.z


def project_neck(v, cy):
    import math
    ang = math.atan2(v.y - cy, -v.x)
    return (ang + math.pi) / (2 * math.pi), v.z


POCKET_VMIN = 463     # 眼窩内側（白目）の面: index<460 かつ 全頂点 index>=463（S14 以来の判定を踏襲）
MOUTH_FACE_RANGE = range(460, 480)   # 口の中の面（S12で追加した20枚）


def uv_face_islands(obj):
    """Face: 動画（14:12）と同じく、①前側 ②後ろ側 ③首、の3つに分けて（＝シームを入れて切るのと同じ）、
    それぞれ別に投影する。1枚の円柱投影だと、頭頂・首元で歪みが大きいため（ユーザー指摘）。
    前・後は正面／背面から見た平面投影（X, Z）、首は円柱状の投影（角度, Z）。3つを、面積に応じて内部でシェルフ詰めする。
    **面（ポリゴン）ごとに、どの島に属するかを決め、その面の4隅すべてを同じ島の投影式で計算する**（頂点ごとに決めると、
    区画をまたぐ面ができて、UV が画面全体に伸びる線になってしまう。これは実際にやってみて分かった不具合）。
    前・後の境界は、座標の Y=0 面ではなく、**面の法線の Y 成分の符号**で決める（法線が真横を向く場所＝輪郭線で切れるので、
    平面投影の歪みが最小になる。Y=0 面で切ると、耳の前あたりで側面の面まで「前」に混ざり、平面投影で大きく引き伸ばされる
    不具合があった。ユーザー指摘で発見）。
    **眼窩内側（白目）・口の中は、さらに別の2島に分ける**（S17で色を塗った際、目の周り・口の周りに意図しない色が
    にじみ出るとユーザーが指摘。原因は、これらの面が奥（-Y方向）へ折り返しているのに、前面と同じ単純な (X,Z) 平面投影を
    使っていたため、外側の皮膚（頬・顎など）と、ほぼ同じ (X,Z) 座標＝ほぼ同じUV画素を共有してしまっていたこと。
    奥行きで折り返す形は、1枚の平面投影では表せないので、別の島に切り出す必要がある）。"""
    verts = obj.data.vertices
    cy = sum(v.co.y for v in verts) / len(verts)          # 首の円柱投影の中心用（前後の判定には使わない）

    def face_group(p):
        if p.index < 460 and all(vi >= POCKET_VMIN for vi in p.vertices):
            return "eye_socket"
        if p.index in MOUTH_FACE_RANGE:
            return "mouth"
        c = sum((verts[vi].co for vi in p.vertices), verts[p.vertices[0]].co * 0)
        c = c / len(p.vertices)
        if c.z < NECK_Z:
            return "neck"
        return "front" if p.normal.y < 0 else "back"

    GROUPS = ("front", "back", "neck", "eye_socket", "mouth")
    face_groups = {p.index: face_group(p) for p in obj.data.polygons}
    counts = {g: 0 for g in GROUPS}
    for g in face_groups.values():
        counts[g] += 1
    gates.note("Face: 前・後・首・眼窩内側・口の中の面の数（面ごとに区画を決めた。シームで分けた5つの島）", counts)

    # 各面のループに、その面の島の投影式で、そのまま UV を書く（面積の重みでシェルフ詰めする前の、島ごとのローカル座標）。
    # 首（円柱投影）は、角度が -pi/+pi をまたぐ面（首の背中側の継ぎ目）で、4隅のUVが画面の端から端まで
    # 引き伸ばされる不具合があった（実際にUVワイヤーを描いて発見）。**面ごとに、その面の重心の角度に最も近くなるよう
    # 各隅の角度を 2π 単位でずらす**（unwrap）ことで、継ぎ目をまたぐ面だけが変則的に伸びる問題を解消する
    loop_local = {}
    bounds = {g: [1e9, 1e9, -1e9, -1e9] for g in GROUPS}
    for p in obj.data.polygons:
        g = face_groups[p.index]
        if g == "neck":
            raw = [project_neck(verts[vi].co, cy) for vi in p.vertices]
            ref = raw[0][0]
            fixed = []
            for u, v in raw:
                while u - ref > 0.5:
                    u -= 1.0
                while u - ref < -0.5:
                    u += 1.0
                fixed.append((u, v))
            for li, (u, v) in zip(range(p.loop_start, p.loop_start + p.loop_total), fixed):
                loop_local[li] = (u, v)
                b = bounds[g]
                b[0], b[1], b[2], b[3] = min(b[0], u), min(b[1], v), max(b[2], u), max(b[3], v)
            continue
        for li in range(p.loop_start, p.loop_start + p.loop_total):
            vi = obj.data.loops[li].vertex_index
            co = verts[vi].co
            u, v = project_front_back(co)
            loop_local[li] = (u, v)
            b = bounds[g]
            b[0], b[1], b[2], b[3] = min(b[0], u), min(b[1], v), max(b[2], u), max(b[3], v)

    def group_area(name):
        a = 0.0
        for p in obj.data.polygons:
            if face_groups[p.index] != name:
                continue
            pts = [verts[vi].co for vi in p.vertices]
            n = sum(((pts[k] - pts[0]).cross(pts[(k + 1) % len(pts)] - pts[0]) for k in range(1, len(pts) - 1)), pts[0] - pts[0])
            a += n.length / 2
        return a

    weights = sorted([(name, group_area(name)) for name in GROUPS], key=lambda kv: -kv[1])
    boxes = shelf_pack(weights, pad=0.02)
    gates.note("Face: 前・後・首・眼窩内側・口の中の内部区画（面積の重み・シェルフ詰め）", {k: (round(v[0], 3), round(v[1], 3), round(v[2], 3), round(v[3], 3)) for k, v in boxes.items()})

    uv_layer = obj.data.uv_layers.new(name="UVMap")
    data = uv_layer.data
    for p in obj.data.polygons:
        g = face_groups[p.index]
        u0, v0, u1, v1 = bounds[g]
        bx0, by0, bx1, by1 = boxes[g]
        pad = 0.04
        s = min((bx1 - bx0) * (1 - 2 * pad) / max(u1 - u0, 1e-6), (by1 - by0) * (1 - 2 * pad) / max(v1 - v0, 1e-6))
        ox = bx0 + (bx1 - bx0) / 2 - (u0 + (u1 - u0) / 2) * s
        oy = by0 + (by1 - by0) / 2 - (v0 + (v1 - v0) / 2) * s
        for li in range(p.loop_start, p.loop_start + p.loop_total):
            u, v = loop_local[li]
            data[li].uv = (u * s + ox, v * s + oy)
    return boxes


def uv_planar(obj):
    """Eye: 正面から見た平面投影（ローカル X, Z）。"""
    xs = [v.co.x for v in obj.data.vertices]
    zs = [v.co.z for v in obj.data.vertices]
    x0, x1 = min(xs), max(xs)
    z0, z1 = min(zs), max(zs)
    per_vertex = {}
    for i, v in enumerate(obj.data.vertices):
        u = (v.co.x - x0) / max(x1 - x0, 1e-6)
        vv = (v.co.z - z0) / max(z1 - z0, 1e-6)
        per_vertex[i] = (u, vv)
    set_uv(obj, per_vertex)


def uv_bounds(obj):
    uv = obj.data.uv_layers.active.data
    xs = [l.uv.x for l in uv]
    ys = [l.uv.y for l in uv]
    return min(xs), min(ys), max(xs), max(ys)


def remap_uv(obj, box):
    x0, y0, x1, y1 = uv_bounds(obj)
    w, h = max(x1 - x0, 1e-6), max(y1 - y0, 1e-6)
    bx0, by0, bx1, by1 = box
    bw, bh = bx1 - bx0, by1 - by0
    pad = 0.06
    s = min(bw * (1 - 2 * pad) / w, bh * (1 - 2 * pad) / h)
    ox = bx0 + bw / 2 - (x0 + w / 2) * s
    oy = by0 + bh / 2 - (y0 + h / 2) * s
    uv = obj.data.uv_layers.active.data
    for l in uv:
        l.uv.x = l.uv.x * s + ox
        l.uv.y = l.uv.y * s + oy


def shelf_pack(items, pad=0.01):
    """items: [(name, weight)]（降順ソート済み）。返り値: {name: (x0,y0,x1,y1)}。"""
    total = sum(w for _, w in items)
    boxes = {}
    side = {n: (w / total) ** 0.5 for n, w in items}
    x, y, row_h = pad, pad, 0.0
    for name, _ in items:
        s = max(side[name] * 0.92, 0.05)
        if x + s > 1.0 - pad:
            x = pad
            y += row_h + pad
            row_h = 0.0
        boxes[name] = (x, y, x + s, y + s)
        x += s + pad
        row_h = max(row_h, s)
    scale_y = 1.0 / max(y + row_h + pad, 1e-6)
    for name in boxes:
        x0, y0, x1, y1 = boxes[name]
        boxes[name] = (x0, y0 * scale_y, x1, y1 * scale_y)
    return boxes


def box_overlap(a, b):
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return not (ax1 <= bx0 or bx1 <= ax0 or ay1 <= by0 or by1 <= ay0)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s15c_gen.blend"))
    for o in bpy.data.objects:
        if o.type == "MESH" and o.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
    objs = {n: bpy.data.objects[n] for n in OBJECTS}
    gates.check("入力: 対象の8オブジェクトが揃っている", all(o is not None for o in objs.values()))
    gates.check("入力: どのオブジェクトにも、まだ UV レイヤーがない", all(len(o.data.uv_layers) == 0 for o in objs.values()))

    # ---- 目のスケールを適用（動画 16:33 の警告への対処）
    eye = objs["Eye"]
    gates.note("Eye のスケール（適用前）", tuple(round(c, 4) for c in eye.scale))
    bpy.context.view_layer.objects.active = eye
    for o in bpy.context.selected_objects:
        o.select_set(False)
    eye.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    gates.check("Eye: スケールを適用した（1,1,1 になった）", tuple(round(c, 6) for c in eye.scale) == (1.0, 1.0, 1.0), tuple(eye.scale))

    n_flat = sum(1 for p in eye.data.polygons if not p.use_smooth)
    for p in eye.data.polygons:
        p.use_smooth = True
    gates.note("Eye: スムースシェードにした面（それまでフラットだった数）", n_flat)

    # ---- UV を、演算子ではなく座標計算で作る（バックグラウンド実行では uv.unwrap 系が {'CANCELLED'} になるため）
    n_stations = {}
    for name in RIBBONS:
        n_stations[name] = uv_ribbon(objs[name])
    uv_face_islands(objs["Face"])
    uv_planar(objs["Eye"])
    for name, obj in objs.items():
        gates.check(f"{name}: UV レイヤーができた", len(obj.data.uv_layers) == 1)
        x0, y0, x1, y1 = uv_bounds(obj)
        gates.check(f"{name}: UV が 0〜1 の範囲にある", -0.001 <= x0 and x1 <= 1.001 and -0.001 <= y0 and y1 <= 1.001, (round(x0, 3), round(y0, 3), round(x1, 3), round(y1, 3)))

    # ---- 表面積で重みづけて、区画を割り当てる（シェルフ法）
    areas = {name: mesh_area(obj) for name, obj in objs.items()}
    order = sorted(areas.items(), key=lambda kv: -kv[1])
    gates.note("各オブジェクトの3D表面積（mm²）と、割り当ての順序", [(n, round(a * 1e6, 1)) for n, a in order])
    boxes = shelf_pack(order)
    for name, obj in objs.items():
        remap_uv(obj, boxes[name])

    # ---- 検証
    names = list(objs.keys())
    box_hits = [(names[i], names[j]) for i in range(len(names)) for j in range(i + 1, len(names)) if box_overlap(boxes[names[i]], boxes[names[j]])]
    gates.check("割り当てた区画どうしが重なっていない", not box_hits, box_hits)

    all_in = True
    for name, obj in objs.items():
        x0, y0, x1, y1 = uv_bounds(obj)
        bx0, by0, bx1, by1 = boxes[name]
        ok = x0 >= bx0 - 1e-4 and x1 <= bx1 + 1e-4 and y0 >= by0 - 1e-4 and y1 <= by1 + 1e-4
        all_in = all_in and ok
        gates.check(f"{name}: UV が割り当てられた区画に収まっている", ok, f"UV=({x0:.3f},{y0:.3f})-({x1:.3f},{y1:.3f}) 区画=({bx0:.3f},{by0:.3f})-({bx1:.3f},{by1:.3f})")
    gates.check("全オブジェクトが、割り当てられた区画に収まっている（重なりなし）", all_in)

    for name, obj in objs.items():
        x0, y0, x1, y1 = uv_bounds(obj)
        gates.check(f"{name}: 配置後も 0〜1 の範囲内", -0.001 <= x0 and x1 <= 1.001 and -0.001 <= y0 and y1 <= 1.001, (round(x0, 3), round(y0, 3), round(x1, 3), round(y1, 3)))

    for name, obj in objs.items():
        uv = obj.data.uv_layers.active.data
        n_deg = 0
        for p in obj.data.polygons:
            pts = [uv[li].uv for li in range(p.loop_start, p.loop_start + p.loop_total)]
            a2 = 0.0
            for k in range(len(pts)):
                x1_, y1_ = pts[k]
                x2_, y2_ = pts[(k + 1) % len(pts)]
                a2 += x1_ * y2_ - x2_ * y1_
            if abs(a2) < 1e-10:
                n_deg += 1
        if name in PROJECTED:
            gates.check(f"{name}: 面積0のUV面がない", n_deg == 0, n_deg)
        else:
            # 帯の両端のふた（4頂点とも同じ駅なので、UV上では線になる）は、面積0になる。房・帯は根元・先端が
            # 隠れる/ごく小さい部分なので、実害はないと判断し、参考値として記録する（Face・Eye は対象外なので厳密に見る）
            gates.note(f"{name}: 面積0のUV面（帯の両端のふた。見えない/ごく小さい部分）", n_deg)

    # ---- ベースカラーのテクスチャ（2048×2048、単色）とマテリアル
    img = bpy.data.images.new("BaseColor", 2048, 2048, alpha=False)
    img.generated_type = "BLANK"
    img.generated_color = (0.8, 0.8, 0.8, 1.0)
    mat = bpy.data.materials.new("CharacterBase")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.location = (bsdf.location.x - 300, bsdf.location.y)
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    for obj in objs.values():
        obj.data.materials.clear()
        obj.data.materials.append(mat)
    gates.check("ベースカラー画像: 2048×2048・単色（生成タイプ BLANK）", img.size[0] == 2048 and img.size[1] == 2048 and img.generated_type == "BLANK")
    gates.check("全オブジェクトに、同じマテリアル（共有テクスチャ）が割り当たっている", all(len(o.data.materials) == 1 and o.data.materials[0] is mat for o in objs.values()))

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s16_gen.blend"), compress=False)

    # ---- レビュー画像: UV 配置図
    import numpy as np
    arr = np.ones((1024, 1024, 4), dtype="float32")
    arr[..., :3] = 0.92
    colors = {"Face": (0.8, 0.2, 0.2), "Eye": (0.2, 0.4, 0.9), "Eyelash": (0.1, 0.1, 0.1), "Eyebrow": (0.5, 0.3, 0.1),
              "DoubleLid": (0.6, 0.1, 0.5), "Eyelash.001": (0.1, 0.7, 0.7), "Eyelash.002": (0.1, 0.7, 0.3), "Eyelash.003": (0.7, 0.6, 0.1)}
    for name, (bx0, by0, bx1, by1) in boxes.items():
        c = colors[name]
        x0i, x1i = int(bx0 * 1023), int(bx1 * 1023)
        y0i, y1i = int((1 - by1) * 1023), int((1 - by0) * 1023)
        arr[y0i:y1i, x0i:x1i] = (*c, 1.0)
        arr[y0i:y1i, x0i:x0i + 2] = 0
        arr[y0i:y1i, max(x1i - 2, 0):x1i] = 0
        arr[y0i:y0i + 2, x0i:x1i] = 0
        arr[max(y1i - 2, 0):y1i, x0i:x1i] = 0
    im = bpy.data.images.new("layout_tmp", 1024, 1024, alpha=False)
    im.pixels.foreach_set(arr[::-1].ravel())
    im.filepath_raw = str(C.OUT / "s16_uv_layout.png")
    im.file_format = "PNG"
    im.save()
    gates.finish()


main()
