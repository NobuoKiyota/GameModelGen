"""S17b: 目のハイライト（後編 動画 24:09〜27:41）。

字幕との対応:
  24:09〜24:46 ハイライト以外を先に塗っておく                        → S17で黒目を塗り済み（このステップでは触らない）
  24:46〜25:29 目のメッシュを複製（編集モードでA→Shift+D）、Yで少し手前へ  → Eyeオブジェクトの全面を複製し、法線方向（-Y、手前）へ0.4mm押し出した「ハイライト用の面」を同じオブジェクトに追加
  25:29〜25:51 複製面のUVを、他と被らない場所へ移動（GX）                → 既存8オブジェクトのUV占有範囲を調べ、空いている区画へ複製面のUVを再配置
  25:51〜26:15 バケツ塗りのブレンドを「リリースアルファ」にして、複製面を透明化 → 複製面のUV区画を、アルファ0（透明）で埋める
  26:15〜26:28 メンマスクモードでハイライト部分だけ選択してから透明化        → （このステップは複製面のUV区画がすでに他と独立しているため、区画ごと透明にするだけで安全。マスク不要）
  26:28〜27:00 ハイライトっぽいものを塗る                              → 透明にした区画の中に、白っぽい丸を2つ（大小）、不透明で描く
  27:00       ミックスを「アド」にしてもいいかも                       → 今回は見送り（アルファブレンドのみ。加算合成は下絵の色見本が無く判断材料が薄いため）

設計:
  - 複製面は Eye オブジェクトの同じメッシュに追加する（動画と同じく、別オブジェクトにはしない）
  - 透明表現には、共有テクスチャ `BaseColor` にアルファチャンネルを追加する。**共有マテリアル自体のブレンド方式は変更しない**
    （最初、共有マテリアルを`BLEND`にしたところ、頭頂部などで深度書き込みが無くなり、光源計算が破綻して不自然に光る
    不具合が出た。ユーザーには見せる前に自分で気づいて直した）。代わりに、複製面（ハイライト）だけに使う別マテリアル
    （同じ画像を使うが`HASHED`）を新設し、Eyeオブジェクトの2枚目のマテリアルスロットとして複製面にだけ割り当てる
  - ハイライトの位置・大きさは下絵に無いため暫定（人間が後で調整する前提）。黒目の左上に大きめ、右下に小さめの2つ

入力: out/face_s17_gen.blend   出力: out/face_s17b_gen.blend, out/s17b_report.json, out/s17b_render_*.png
実行: blender --background --factory-startup --python steps/s17b_highlight.py
"""
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402

STEP = "s17b"
gates = C.Gates(STEP)

W = H = 2048
PUSH_M = 0.0004          # 手前(-Y)への押し出し量
OBJECTS = ["Face", "Eye", "Eyelash", "Eyebrow", "DoubleLid", "Eyelash.001", "Eyelash.002", "Eyelash.003"]


def px_of(u, v):
    return u * (W - 1), (1 - v) * (H - 1)


def fill_poly_mask(mask, pts):
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
            x0i, x1i = int(max(xs[j], 0)), int(min(xs[j + 1], W - 1))
            mask[y, x0i:x1i + 1] = True


def uv_bounds_obj(obj):
    uv = obj.data.uv_layers.active.data
    xs = [l.uv.x for l in uv]
    ys = [l.uv.y for l in uv]
    return min(xs), min(ys), max(xs), max(ys)


def find_free_box(occupied, size, pad=0.01):
    """occupied: [(x0,y0,x1,y1)]。size四方の空き区画を、左下から走査して探す。"""
    step = 0.01
    y = pad
    while y + size < 1.0 - pad:
        x = pad
        while x + size < 1.0 - pad:
            cand = (x, y, x + size, y + size)
            if not any(not (cand[2] <= o[0] or o[2] <= cand[0] or cand[3] <= o[1] or o[3] <= cand[1]) for o in occupied):
                return cand
            x += step
        y += step
    return None


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s17_gen.blend"))
    objs = {n: bpy.data.objects[n] for n in OBJECTS}
    gates.check("入力: 対象の8オブジェクトが揃っている", all(o is not None for o in objs.values()))

    eye = objs["Eye"]
    me = eye.data
    n_v0, n_f0 = len(me.vertices), len(me.polygons)

    # ---- 1) 複製面を作る（全頂点を-Y方向へ押し出したコピー）
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    uv_layer = bm.loops.layers.uv.active
    orig_faces = list(bm.faces)
    orig_verts = list(bm.verts)          # 複製前のスナップショット（bm.verts.new()中にbm.vertsが伸びるのでイテレート対象を固定する）
    vmap = {}
    for v in orig_verts:
        nv = bm.verts.new(v.co + Vector((0, -PUSH_M, 0)))
        vmap[v] = nv
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()
    new_faces = []
    for f in orig_faces:
        nf = bm.faces.new([vmap[v] for v in f.verts])
        # bmesh は新しい面のUVを自動で引き継がない（デフォルト0,0になる）ので、元の面から明示的にコピーする
        for lo, lno in zip(f.loops, nf.loops):
            lno[uv_layer].uv = lo[uv_layer].uv
        new_faces.append(nf)
    bm.faces.ensure_lookup_table()
    bm.faces.index_update()
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    me.update()
    gates.check(f"Eye: 頂点・面が複製された分だけ増えた（{n_v0}→{len(me.vertices)}, {n_f0}→{len(me.polygons)}）",
                len(me.vertices) == n_v0 * 2 and len(me.polygons) == n_f0 * 2)
    for p in me.polygons:
        p.use_smooth = True
    for p in me.polygons:
        if p.index >= n_f0:
            p.material_index = 1

    # ---- 2) 複製面のUVを、既存8オブジェクトと被らない区画へ
    occupied = [uv_bounds_obj(objs[n]) for n in OBJECTS]
    box = find_free_box(occupied, size=0.08)
    gates.check("ハイライト用の空き区画が見つかった", box is not None, box)
    bx0, by0, bx1, by1 = box

    uv = me.uv_layers.active.data
    orig_x0, orig_y0, orig_x1, orig_y1 = uv_bounds_obj(eye)   # 複製前のEye全体のUV範囲（=元の黒目の範囲）
    new_poly_start = n_f0
    pad = 0.06
    s = min((bx1 - bx0) * (1 - 2 * pad) / max(orig_x1 - orig_x0, 1e-6), (by1 - by0) * (1 - 2 * pad) / max(orig_y1 - orig_y0, 1e-6))
    ox = bx0 + (bx1 - bx0) / 2 - (orig_x0 + (orig_x1 - orig_x0) / 2) * s
    oy = by0 + (by1 - by0) / 2 - (orig_y0 + (orig_y1 - orig_y0) / 2) * s
    for p in me.polygons:
        if p.index < new_poly_start:
            continue
        for li in range(p.loop_start, p.loop_start + p.loop_total):
            u0, v0 = uv[li].uv
            uv[li].uv = (u0 * s + ox, v0 * s + oy)
    gates.check("複製面のUVがハイライト区画に収まっている",
                all(bx0 - 1e-4 <= uv[li].uv.x <= bx1 + 1e-4 and by0 - 1e-4 <= uv[li].uv.y <= by1 + 1e-4
                    for p in me.polygons if p.index >= new_poly_start for li in range(p.loop_start, p.loop_start + p.loop_total)))

    # ---- 3) テクスチャにアルファチャンネルを追加。ハイライト区画を透明地にし、丸2つだけ不透明で塗る
    img = bpy.data.images["BaseColor"]
    old_rgb = np.array(img.pixels[:], dtype="float32").reshape(H, W, 4)[::-1, :, :3].copy()
    alpha = np.ones((H, W), dtype="float32")

    hbox_mask = np.zeros((H, W), dtype=bool)
    p0, p1 = px_of(bx0, by0), px_of(bx1, by1)
    x0i, x1i = int(min(p0[0], p1[0])), int(max(p0[0], p1[0]))
    y0i, y1i = int(min(p0[1], p1[1])), int(max(p0[1], p1[1]))
    hbox_mask[y0i:y1i + 1, x0i:x1i + 1] = True
    alpha[hbox_mask] = 0.0

    def draw_circle_opaque(cx_frac, cy_frac, r_frac):
        cx = bx0 + (bx1 - bx0) * cx_frac
        cy = by0 + (by1 - by0) * cy_frac
        cxpx, cypx = px_of(cx, cy)
        rpx = r_frac * (x1i - x0i)
        yy, xx = np.mgrid[0:H, 0:W]
        d = np.sqrt((xx - cxpx) ** 2 + (yy - cypx) ** 2)
        m = d <= rpx
        alpha[m] = 1.0
        old_rgb[m] = (0.98, 0.98, 1.0)
        return int(m.sum())

    n1 = draw_circle_opaque(0.30, 0.66, 0.06)
    n2 = draw_circle_opaque(0.60, 0.32, 0.03)
    gates.check("ハイライトの丸2つを不透明で描いた", n1 > 0 and n2 > 0, (n1, n2))

    img_rgba = np.ones((H, W, 4), dtype="float32")
    img_rgba[:, :, :3] = old_rgb
    img_rgba[:, :, 3] = alpha

    # 既存の `BaseColor` は S16 で `alpha=False`（24bit、実質アルファ無し）で作られており、
    # foreach_set でアルファを書いても保存後は必ず1.0に戻ってしまう不具合があった（実際に保存→再読込して発覚。
    # 自分の検証コードが、書き込んだ直後のnumpy配列自身を読んでいて、保存後の実データを確認していなかったのも原因）。
    # そのため、アルファ有りの画像を新規に作り直し、既存の全マテリアルのImage Textureノードを付け替える
    old_name = img.name
    new_img = bpy.data.images.new(old_name + "_rgba", W, H, alpha=True)
    new_img.pixels.foreach_set(img_rgba[::-1].ravel())
    new_img.filepath_raw = str(C.OUT / "s17b_texture.png")
    new_img.file_format = "PNG"
    new_img.alpha_mode = 'STRAIGHT'
    new_img.pack()
    new_img.save()
    gates.check("新しい画像はアルファ有り（32bit）", new_img.depth == 32, new_img.depth)
    for m in bpy.data.materials:
        if not m.use_nodes:
            continue
        for n in m.node_tree.nodes:
            if n.type == "TEX_IMAGE" and n.image is img:
                n.image = new_img
    bpy.data.images.remove(img)
    new_img.name = old_name
    img = new_img

    # ---- 4) ハイライト専用マテリアル（同じ画像・アルファ有効）を新設し、複製面だけに割り当てる
    #      共有の`CharacterBase`は`OPAQUE`のまま変更しない（BLENDにすると頭頂部などで深度書き込みが無くなり、
    #      光源計算が破綻して不自然に光る不具合が出たため、影響範囲をハイライトの面だけに限定する）
    base_mat = bpy.data.materials["CharacterBase"]
    base_img = next(n for n in base_mat.node_tree.nodes if n.type == "TEX_IMAGE").image
    hi_mat = bpy.data.materials.new("CharacterHighlight")
    hi_mat.use_nodes = True
    hi_mat.blend_method = 'HASHED'
    nt = hi_mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = base_img
    tex.location = (bsdf.location.x - 300, bsdf.location.y)
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])

    eye.data.materials.append(hi_mat)
    gates.check("Eye: マテリアルスロットが2つになった（0=共有の不透明、1=ハイライト専用）", len(eye.data.materials) == 2)
    gates.check("共有マテリアルのブレンド方式は変更していない（BLENDにはしていない）", base_mat.blend_method != 'BLEND', base_mat.blend_method)

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s17b_gen.blend"), compress=False)

    # ---- 検証: 保存された画像データブロック自身（自分のnumpy配列ではなく）を読み直して確認する。
    #      これを`img_rgba`という自分の作業用配列で済ませていたため、24bit画像がアルファを保持していない
    #      不具合を検出できなかった（保存後に再読込して初めて発覚）。今回は`img.pixels`を直接読む
    real = np.array(img.pixels[:], dtype="float32").reshape(H, W, 4)[::-1]  # Blender は行0=下(v=0)。px_of()は上下反転(行0=上)前提なので合わせる

    def alpha_at(u, v):
        x, y = px_of(u, v)
        return real[int((1 - v) * (H - 1)), int(x), 3]

    gates.check("画像は32bit（アルファ保持）のまま保存された", img.depth == 32, img.depth)
    gates.check("ハイライト区画・丸の外側はアルファ0（保存データを直接確認）", alpha_at(bx0 + 0.005, by0 + 0.005) < 0.05, alpha_at(bx0 + 0.005, by0 + 0.005))
    gates.check("ハイライト区画・丸1の中心はアルファ1（保存データを直接確認）", alpha_at(bx0 + (bx1 - bx0) * 0.30, by0 + (by1 - by0) * 0.66) > 0.95)
    skin_sample = objs["Face"].data.polygons[0]
    su = objs["Face"].data.uv_layers.active.data[skin_sample.loop_start].uv
    gates.check("肌の区画はアルファ1のまま（保存データを直接確認）", alpha_at(su.x, su.y) > 0.95)

    # ---- レビュー用レンダリング（確認をしやすくするため、一時的に全マテリアルの光沢を弱める。保存はしない）
    for m in bpy.data.materials:
        if m.use_nodes:
            b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
            if b:
                b.inputs["Roughness"].default_value = 0.9
                b.inputs["Specular IOR Level"].default_value = 0.05
    scene = bpy.context.scene
    world = bpy.data.worlds.new("ReviewWorld")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.6, 0.6, 1.0)
    scene.world = world
    sun = bpy.data.lights.new("ReviewSun", type='SUN')
    sun.energy = 3.0
    sun_obj = bpy.data.objects.new("ReviewSun", sun)
    sun_obj.rotation_euler = (1.0, 0.0, 0.6)
    scene.collection.objects.link(sun_obj)
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    scene.render.resolution_x = 900
    scene.render.resolution_y = 900
    keep = set(OBJECTS)
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.hide_render = o.name not in keep
    for camname, out_name in [("CAM_front", "s17b_render_front.png"), ("CAM_a45", "s17b_render_45.png")]:
        scene.camera = bpy.data.objects[camname]
        scene.render.filepath = str(C.OUT / out_name)
        bpy.ops.render.render(write_still=True)

    gates.finish()


main()
