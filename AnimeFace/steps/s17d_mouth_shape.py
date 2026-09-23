"""S17d: 口の形を調整する（後編 動画 28:31〜29:54）。オメガ形にする細部は見送り、大きさ・位置のみ調整。

字幕との対応:
  28:31〜28:53 口の形をオメガっぽくする、口全体を少し小さく          → オメガ形の細部は下絵に無く判断材料が薄いため見送り（保留）。
                                                                    大きさの調整のみ実施
  28:53〜29:25 少し上に、真上ではなく顎と鼻をつなぐ線に沿って斜めに移動 → 口の縁・口の中の全頂点を、上＋やや手前（-Y）へ移動
  29:25〜29:54 ピボットをアクティブ要素にしてSXで横幅を縮める          → X座標を中心線(X=0)に対して85%へスケール（半分メッシュなので、
                                                                    外側の頂点ほど中心へ寄る＝口の幅が狭くなる）

設計:
  - 対象頂点は、口の縁（P: index [26,203,27,28,29,30,31,218,32]、S12で確認済みの9頂点）と、
    口の中の空洞（R1・R2、index 495-512、S12で追加した18頂点）の合計27頂点。座標のしきい値ではなく、
    S12で確定した頂点indexで選ぶ（人間の手直しで座標がしきい値の外に出ていても安定して選べる）
  - 移動後、皮膚（既存の面）との交差が増えていないことを確認する（S15c以来の「基準値と比べる」方式）

入力: out/face_s17c_human.blend   出力: out/face_s17d_gen.blend, out/s17d_report.json, out/s17d_render_*.png
実行: blender --background --factory-startup --python steps/s17d_mouth_shape.py
"""
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402

STEP = "s17d"
gates = C.Gates(STEP)

MOUTH_RIM = [26, 203, 27, 28, 29, 30, 31, 218, 32]
MOUTH_CAVITY = list(range(495, 513))
MOVE = Vector((0.0, -0.0010, 0.0025))   # 手前へ1.0mm・上へ2.5mm
SCALE_X = 0.85


def bvh_world(obj):
    me = obj.data
    mw = obj.matrix_world
    return BVHTree.FromPolygons([tuple(mw @ v.co) for v in me.vertices], [list(p.vertices) for p in me.polygons])


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s17c_human.blend"))
    face = bpy.data.objects["Face"]
    me = face.data
    n_v0, n_f0 = len(me.vertices), len(me.polygons)

    gates.check("口の縁9頂点が、X=0の両端を持つ（想定通りの並び）",
                abs(me.vertices[MOUTH_RIM[0]].co.x) < 1e-6 and abs(me.vertices[MOUTH_RIM[-1]].co.x) < 1e-6)
    corner = me.vertices[MOUTH_RIM[4]]
    gates.check("口角（4番目）が最もXが小さい（外側）", corner.co.x == min(me.vertices[i].co.x for i in MOUTH_RIM))

    others = {n: bpy.data.objects[n] for n in ["Eye", "Eyelash", "Eyebrow", "DoubleLid", "Eyelash.001", "Eyelash.002", "Eyelash.003"]}
    bvh_others = {n: bvh_world(o) for n, o in others.items()}
    bvh_face_before = bvh_world(face)
    self_before = len([1 for a, b in bvh_face_before.overlap(bvh_face_before) if a < b
                        and not (set(me.polygons[a].vertices) & set(me.polygons[b].vertices))])
    cross_before = {n: len(bvh_face_before.overlap(bv)) for n, bv in bvh_others.items()}
    gates.note("修正前: Faceの自己交差数・他オブジェクトとの重なり数（基準値）", (self_before, cross_before))

    all_idx = MOUTH_RIM + MOUTH_CAVITY
    gates.check("対象は27頂点（口の縁9＋口の中18）", len(set(all_idx)) == 27, len(set(all_idx)))
    for i in all_idx:
        v = me.vertices[i]
        v.co = v.co + MOVE
        v.co.x *= SCALE_X
    me.update()
    gates.note("適用した変更", f"上+手前へ {tuple(round(c*1000,2) for c in MOVE)}mm 移動、X方向を{SCALE_X}倍に縮小")

    gates.check("正中線の頂点は、移動後もX=0のまま", all(abs(me.vertices[i].co.x) < 1e-9 for i in (MOUTH_RIM[0], MOUTH_RIM[-1])))

    bvh_face_after = bvh_world(face)
    self_after = len([1 for a, b in bvh_face_after.overlap(bvh_face_after) if a < b
                       and not (set(me.polygons[a].vertices) & set(me.polygons[b].vertices))])
    cross_after = {n: len(bvh_face_after.overlap(bv)) for n, bv in bvh_others.items()}
    gates.check("修正後、自己交差が増えていない", self_after <= self_before, (self_before, self_after))
    worse = {n: (cross_before[n], cross_after[n]) for n in cross_after if cross_after[n] > cross_before[n]}
    gates.check("修正後、他オブジェクトとの重なりが増えていない", not worse, worse)

    gates.check("頂点・面の数は変わっていない", len(me.vertices) == n_v0 and len(me.polygons) == n_f0)

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s17d_gen.blend"), compress=False)

    # ---- レビュー用レンダリング（光沢を弱めて確認しやすくする。保存はしない）
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
    keep = {"Face", "Eye", "Eyelash", "Eyebrow", "DoubleLid", "Eyelash.001", "Eyelash.002", "Eyelash.003"}
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.hide_render = o.name not in keep
    for camname, out_name in [("CAM_front", "s17d_render_front.png"), ("CAM_a45", "s17d_render_45.png"), ("CAM_side", "s17d_render_side.png")]:
        scene.camera = bpy.data.objects[camname]
        scene.render.filepath = str(C.OUT / out_name)
        bpy.ops.render.render(write_still=True)

    gates.finish()


main()
