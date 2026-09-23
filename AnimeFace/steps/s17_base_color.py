"""S17: ベースカラーの塗り分け（後編 動画 18:11〜23:49、色の一部）。ハイライト・まつ毛の切れ込み・口の形調整・
オブジェクト整理は別ステップ（S17b〜S17e）。

字幕との対応:
  18:11〜18:39 肌をバケツで全塗り（ブリード8px）                  → テクスチャ全体を肌色で塗る（ブリードの代わりに、各区画に余白を持たせてある）
  18:57〜19:11 目の白目をLで選択してS（スポイト）で塗る            → Face の眼窩内側の面（socket面）を白めの色で塗る
  19:29〜19:43 口の中をLで選択して塗る                            → Face の口の中の面（mouth cavity面）を暗い赤で塗る
  19:57〜20:36 眉毛・二重線を選択して紫っぽい色で塗る               → Eyebrow・DoubleLid を紫がかった色で塗る
  20:49〜21:10 頬を弱いブラシで塗る                                → Face 前面の頬にあたる面を中心に、距離に応じた柔らかい縁取りでピンクを重ねる
  21:10〜21:45 目の中の影を塗る                                    → Eye の上側（まぶた寄り）に、暗めの色をグラデーションで重ねる
  22:16〜22:31 鼻先を塗る                                          → 鼻先の頂点付近に、小さく柔らかい色を重ねる
  23:07〜23:49 まつ毛にマテリアルをリンクして紫に塗る               → Eyelash・Eyelash.001/.002/.003 を紫がかった暗い色で塗る
  27:22〜27:41 首下・顎の境目も塗ると分かりやすい                   → 今回は見送り（保留。効果が小さく、範囲の根拠が薄いため）

設計:
  - 下絵に色の参照が無いため、配色（肌・目・眉/二重線・まつ毛・頬・口内の色）は暫定（人間が後で調整する前提の仮塗り。
    動画本編も「仮なので雰囲気を見るために適当にやっておきます」と明言している段階）
  - `bpy.ops.paint.*`（ブラシ）は、UV演算子と同様 `--background` では機能しない前提で使わず、S16で計算済みのUV座標から、
    テクスチャのピクセルへ直接書き込む（対象の面は3D座標や頂点番号で選ぶ）
  - 頬・鼻先・目の影は、単色ベタ塗りではなく、中心からの距離に応じた柔らかい重ね（アルファブレンド）にする

入力: out/face_s16_gen.blend   出力: out/face_s17_gen.blend, out/s17_report.json, out/s17_*.png
実行: blender --background --factory-startup --python steps/s17_base_color.py
"""
import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402

STEP = "s17"
gates = C.Gates(STEP)

W = H = 2048

SKIN = (0.98, 0.83, 0.74)
EYE_WHITE = (0.96, 0.96, 0.97)
MOUTH = (0.55, 0.12, 0.18)
BROW = (0.42, 0.28, 0.42)
LASH = (0.15, 0.10, 0.20)
IRIS = (0.20, 0.12, 0.10)
IRIS_SHADOW = (0.05, 0.03, 0.03)
BLUSH = (0.98, 0.55, 0.55)

RIBBONS = ["Eyelash", "Eyebrow", "DoubleLid", "Eyelash.001", "Eyelash.002", "Eyelash.003"]


def px_of(u, v):
    return u * (W - 1), (1 - v) * (H - 1)


def poly_px(obj, p):
    uv = obj.data.uv_layers.active.data
    return [px_of(*uv[li].uv) for li in range(p.loop_start, p.loop_start + p.loop_total)]


def scan_rows(pts):
    P = np.array(pts, dtype=float)
    y0 = int(max(P[:, 1].min(), 0))
    y1 = int(min(P[:, 1].max(), H - 1))
    for y in range(y0, y1 + 1):
        xs = []
        for k in range(len(P)):
            a, b = P[k], P[(k + 1) % len(P)]
            if (a[1] <= y + 0.5 < b[1]) or (b[1] <= y + 0.5 < a[1]):
                xs.append(a[0] + (y + 0.5 - a[1]) * (b[0] - a[0]) / (b[1] - a[1]))
        xs.sort()
        for j in range(0, len(xs) - 1, 2):
            yield y, int(max(xs[j], 0)), int(min(xs[j + 1], W - 1))


def fill_poly_color(arr, pts, color):
    for y, x0, x1 in scan_rows(pts):
        arr[y, x0:x1 + 1] = color


def fill_poly_mask(mask, pts):
    for y, x0, x1 in scan_rows(pts):
        mask[y, x0:x1 + 1] = True


def fill_object_flat(arr, obj, color):
    n = 0
    for p in obj.data.polygons:
        fill_poly_color(arr, poly_px(obj, p), color)
        n += 1
    return n


def soft_blend_radial(arr, mask, color, center_px, radius_px, strength, power=1.4):
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return 0
    d = np.sqrt((xs - center_px[0]) ** 2 + (ys - center_px[1]) ** 2) / radius_px
    a = (np.clip(1 - d, 0, 1) ** power) * strength
    col = np.array(color)
    arr[ys, xs] = arr[ys, xs] * (1 - a)[:, None] + col[None, :] * a[:, None]
    return int((a > 0.02).sum())


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s16_gen.blend"))
    objs = {n: bpy.data.objects[n] for n in ["Face", "Eye"] + RIBBONS}
    gates.check("入力: 対象の8オブジェクトが揃っている", all(o is not None for o in objs.values()))
    gates.check("入力: 全オブジェクトにUVがある", all(len(o.data.uv_layers) == 1 for o in objs.values()))

    img = bpy.data.images["BaseColor"]
    gates.check("入力: BaseColor 画像は2048x2048", tuple(img.size) == (W, H))
    arr = np.array(img.pixels[:], dtype="float32").reshape(H, W, 4)[::-1, :, :3].copy()  # 上が行0（top-down）に変換

    face = objs["Face"]
    me = face.data

    # ---- 眼窩内側（白目）: 面index<460（口の中を作る前）で、全頂点が index>=463（S14の判定を踏襲）
    socket_faces = [p for p in me.polygons if p.index < 460 and all(vi >= 463 for vi in p.vertices)]
    gates.check("Face: 眼窩内側（白目）の面が20枚見つかった", len(socket_faces) == 20, len(socket_faces))
    # ---- 口の中: S12で追加した面（index 460〜479の20枚）
    mouth_faces = [me.polygons[i] for i in range(460, 480)]
    gates.check("Face: 口の中の面が20枚（index 460-479）", all(len(p.vertices) in (3, 4) for p in mouth_faces))

    # ---- 1) 肌をテクスチャ全体に敷く（動画のバケツ全塗りに相当。他の区画は後で上から塗り重ねる）
    arr[:, :] = SKIN

    # ---- 2) 白目・口の中
    for p in socket_faces:
        fill_poly_color(arr, poly_px(face, p), EYE_WHITE)
    for p in mouth_faces:
        fill_poly_color(arr, poly_px(face, p), MOUTH)

    # ---- 3) 眉・二重線（同じ紫系の色）
    n_brow = fill_object_flat(arr, objs["Eyebrow"], BROW)
    n_dlid = fill_object_flat(arr, objs["DoubleLid"], BROW)

    # ---- 4) まつ毛（主＋房3つ、同じ暗い紫）
    n_lash = 0
    for name in ["Eyelash", "Eyelash.001", "Eyelash.002", "Eyelash.003"]:
        n_lash += fill_object_flat(arr, objs[name], LASH)

    # ---- 5) 黒目（Eye）: ベタ塗り＋上側（まぶた寄り）に影のグラデーション
    eye = objs["Eye"]
    n_eye = fill_object_flat(arr, eye, IRIS)
    eye_uv = eye.data.uv_layers.active.data
    us = [l.uv.x for l in eye_uv]
    vs = [l.uv.y for l in eye_uv]
    ebx0, ebx1 = min(us), max(us)
    eby0, eby1 = min(vs), max(vs)
    eye_mask = np.zeros((H, W), dtype=bool)
    for p in eye.data.polygons:
        fill_poly_mask(eye_mask, poly_px(eye, p))
    ys, xs = np.where(eye_mask)
    vtop_px, vbot_px = px_of(0, eby1)[1], px_of(0, eby0)[1]  # v=eby1(上) -> 小さいy、v=eby0(下) -> 大きいy
    t = np.clip((vbot_px - ys) / max(vbot_px - vtop_px, 1e-6), 0, 1)  # 0=下, 1=上
    a = np.clip((t - 0.55) / 0.45, 0, 1) * 0.55
    col = np.array(IRIS_SHADOW)
    arr[ys, xs] = arr[ys, xs] * (1 - a)[:, None] + col[None, :] * a[:, None]

    # ---- 6) 頬（柔らかいピンク、距離に応じて薄く）
    cheek_faces = [p for p in me.polygons
                   if p.index not in {q.index for q in socket_faces} and p.index not in range(460, 480)
                   and p.normal.y < 0
                   and -0.115 < me.polygons[p.index].center.x < -0.03
                   and -0.10 < me.polygons[p.index].center.z < -0.035]
    gates.note("Face: 頬の候補面の数（3D座標のバウンディングで選択、下絵に色見本が無いための目分量）", len(cheek_faces))
    cheek_mask = np.zeros((H, W), dtype=bool)
    for p in cheek_faces:
        fill_poly_mask(cheek_mask, poly_px(face, p))
    ys, xs = np.where(cheek_mask)
    n_blush = 0
    if len(xs):
        cx, cy = xs.mean(), ys.mean()
        r = max(float(np.percentile(np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2), 90)), 1.0)
        n_blush = soft_blend_radial(arr, cheek_mask, BLUSH, (cx, cy), r, strength=0.35, power=1.4)

    # ---- 7) 鼻先（頂点0近傍・最前方の頂点を鼻先とみなす）
    nose_cand = [v for v in me.vertices if abs(v.co.x) < 0.015 and -0.10 < v.co.z < -0.01]
    nose_v = min(nose_cand, key=lambda v: v.co.y)
    gates.note("鼻先とみなした頂点", f"index={nose_v.index} co={tuple(round(c,4) for c in nose_v.co)}")
    nose_faces = [p for p in me.polygons if nose_v.index in p.vertices]
    nose_mask = np.zeros((H, W), dtype=bool)
    for p in nose_faces:
        fill_poly_mask(nose_mask, poly_px(face, p))
    ys, xs = np.where(nose_mask)
    n_nose = 0
    if len(xs):
        cx, cy = xs.mean(), ys.mean()
        r = max(float(xs.std()) + float(ys.std()), 6.0)
        n_nose = soft_blend_radial(arr, nose_mask, BLUSH, (cx, cy), r, strength=0.22, power=1.6)

    # ---- 検証: 各領域の代表点の色が、意図した色に近い
    def sample_color(pts):
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        return arr[int(cy), int(cx)]

    def close(c1, c2, tol=0.03):
        return all(abs(a - b) <= tol for a, b in zip(c1, c2))

    excluded_idx = {p.index for p in socket_faces + mouth_faces + cheek_faces + nose_faces}
    forehead = [p for p in me.polygons if p.index not in excluded_idx and p.normal.y < 0 and p.center.z > 0.05]
    gates.check("肌の代表点用に、白目/口/頬/鼻先と重ならない額の面が見つかった", len(forehead) > 0, len(forehead))
    skin_far = forehead[0]
    far_ok = skin_far.index not in excluded_idx
    gates.check("肌の代表点（面0、特別領域と重複しない）が SKIN 色に近い",
                far_ok and close(sample_color(poly_px(face, skin_far)), SKIN), (far_ok, list(np.round(sample_color(poly_px(face, skin_far)), 3))))
    gates.check("白目の代表点が EYE_WHITE 色に近い", close(sample_color(poly_px(face, socket_faces[0])), EYE_WHITE))
    gates.check("口の中の代表点が MOUTH 色に近い", close(sample_color(poly_px(face, mouth_faces[0])), MOUTH))
    gates.check("眉の代表点が BROW 色に近い", close(sample_color(poly_px(objs['Eyebrow'], objs['Eyebrow'].data.polygons[len(objs['Eyebrow'].data.polygons)//2])), BROW))
    gates.check("まつ毛の代表点が LASH 色に近い", close(sample_color(poly_px(objs['Eyelash'], objs['Eyelash'].data.polygons[len(objs['Eyelash'].data.polygons)//2])), LASH))
    gates.check("黒目・下側の代表点が IRIS 色に近い（上側は影で暗くなる想定なので下側で確認）",
                close(sample_color([px_of((ebx0 + ebx1) / 2, eby0 + (eby1 - eby0) * 0.15)]), IRIS, tol=0.05))
    gates.note("塗った面の数", {"白目": len(socket_faces), "口の中": len(mouth_faces), "眉": n_brow, "二重線": n_dlid,
                              "まつ毛(4つ計)": n_lash, "黒目": n_eye, "頬(柔らかい重ね)": n_blush, "鼻先(柔らかい重ね)": n_nose})

    # ---- 書き戻し・保存
    out = np.ones((H, W, 4), dtype="float32")
    out[:, :, :3] = arr
    img.pixels.foreach_set(out[::-1].ravel())
    img.filepath_raw = str(C.OUT / "s17_texture.png")
    img.file_format = "PNG"
    img.pack()
    img.save()

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s17_gen.blend"), compress=False)

    # ---- レビュー用レンダリング(Eevee, 既存の正面カメラ)。ライト・ワールドは確認用の一時追加で、.blend には保存しない（上で保存済み）
    scene = bpy.context.scene
    scene.camera = bpy.data.objects["CAM_front"]
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    scene.render.resolution_x = 800
    scene.render.resolution_y = 800
    scene.render.filepath = str(C.OUT / "s17_render_front.png")
    for o in [objs['Face'], objs['Eye']] + [objs[n] for n in RIBBONS]:
        o.hide_render = False
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.name not in objs:
            o.hide_render = True
    world = bpy.data.worlds.new("ReviewWorld")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.6, 0.6, 1.0)
    scene.world = world
    sun = bpy.data.lights.new("ReviewSun", type='SUN')
    sun.energy = 3.0
    sun_obj = bpy.data.objects.new("ReviewSun", sun)
    sun_obj.rotation_euler = (1.0, 0.0, 0.6)
    scene.collection.objects.link(sun_obj)
    bpy.ops.render.render(write_still=True)

    gates.finish()


main()
