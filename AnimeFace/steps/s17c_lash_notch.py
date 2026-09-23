"""S17c: 主まつ毛に「切れ込み」（分かれ目）を1つ作る（後編 動画 30:18〜30:56）。

字幕との対応:
  30:18〜30:29 このまつ毛の「い」っていう部分、分かれ目みたいなの作ってなかったので作りましょうか
               → まつ毛の帯は、前の稜（F）が滑らかに一続きになっている。個々のまつ毛の束の切れ目を1つ、視覚的に入れる
  30:29〜30:44 コントロールRでループ追加して5Vで切る。ここに面がなくなるのでFで貼る
               → 頂点・面の数を変えずに実装する: 対象駅の前の稜（F）を、内側（I）へ寄せて凹ませることで、
                 同じ見た目の「分かれ目」を作る（帯のパラメータ化・UV・頂点数は変えないので、他ステップへの影響がない）
  30:44〜30:56 ここはシフト入りグリースをかけてあげる                → 対象駅に接する2本の前稜の辺は、既にクリース1.0（S14で設定済み。Eyelashはsharp_edge属性は使っていない）のまま

設計:
  - 対象駅は、内眼角・外眼角の両端を避けた中間あたり（駅13。全22駅中、内側寄りの束と外側寄りの束の境目あたり）
  - 前の稜（F）を、断面の中心方向（F→I方向）へ40%だけ寄せる。O・I・Kは動かさない（帯の外形・UV・頂点数は不変）
  - 皮膚・黒目・他のまつ毛と交差しないことを確認する（S15cと同じく、間引き前＝この操作前の交差数を基準に、悪化していないか比べる）

入力: out/face_s17b_gen.blend（S17bのアルファ不具合を直したものを再生成し、上書きした版）
出力: out/face_s17c_gen.blend, out/s17c_report.json, out/s17c_render_*.png
実行: blender --background --factory-startup --python steps/s17c_lash_notch.py
"""
import sys
from pathlib import Path

import bpy
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402

STEP = "s17c"
gates = C.Gates(STEP)

STATION = 13      # 22駅中、対象の駅
PULL_FRAC = 0.4   # F を I へ寄せる割合


def bvh_world(obj):
    me = obj.data
    mw = obj.matrix_world
    return BVHTree.FromPolygons([tuple(mw @ v.co) for v in me.vertices], [list(p.vertices) for p in me.polygons])


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s17b_gen.blend"))
    for o in bpy.data.objects:
        if o.type == "MESH" and o.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
    lash = bpy.data.objects["Eyelash"]
    me = lash.data
    n_st = len(me.vertices) // 4
    gates.check("入力: Eyelash は22駅の帯（頂点88）", n_st == 22 and len(me.vertices) == 88, n_st)

    others = {n: bpy.data.objects[n] for n in ["Face", "Eye", "Eyebrow", "DoubleLid", "Eyelash.001", "Eyelash.002", "Eyelash.003"]}
    bvh_others_before = {n: bvh_world(o) for n, o in others.items()}
    bvh_lash_before = bvh_world(lash)
    before = {n: len(bvh_lash_before.overlap(bv)) for n, bv in bvh_others_before.items()}
    gates.note("修正前: Eyelashと他オブジェクトの重なり面ペア数（基準値）", before)

    O, F, I, K = [me.vertices[4 * STATION + j] for j in range(4)]
    f0 = F.co.copy()
    F.co = F.co + (I.co - F.co) * PULL_FRAC
    me.update()
    gates.note(f"駅{STATION}の前稜(F)を内側へ{PULL_FRAC*100:.0f}%寄せた", f"{tuple(round(c,4) for c in f0)} -> {tuple(round(c,4) for c in F.co)}")

    cre = me.attributes.get("crease_edge")
    keys = {frozenset((4 * (STATION - 1) + 1, 4 * STATION + 1)), frozenset((4 * STATION + 1, 4 * (STATION + 1) + 1))}
    marked = 0
    for e in me.edges:
        if frozenset(e.vertices) in keys and cre.data[e.index].value >= 1.0:
            marked += 1
    gates.check("駅の前後の前稜の辺は、既にクリース1.0（S14設定を維持。Eyelashはsharp_edge属性は使っていない）", marked == 2, marked)

    bvh_lash_after = bvh_world(lash)
    after = {n: len(bvh_lash_after.overlap(bv)) for n, bv in bvh_others_before.items()}
    worse = {n: (before[n], after[n]) for n in after if after[n] > before[n]}
    gates.check("修正後、他オブジェクトとの重なりが増えていない", not worse, worse)

    self_before = len([1 for a, b in bvh_lash_before.overlap(bvh_lash_before) if a < b])
    self_after = len([1 for a, b in bvh_lash_after.overlap(bvh_lash_after) if a < b])
    gates.check("自己交差が、修正前より増えていない", self_after <= self_before, (self_before, self_after))

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s17c_gen.blend"), compress=False)

    # ---- レビュー用レンダリング（光沢を弱めて確認しやすくする。保存はしない。S17bで気づいた、
    #      既定の光沢のままSunを当てると、黒目が白飛びして薄く見える問題への対処）
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
    for camname, out_name in [("CAM_front", "s17c_render_front.png"), ("CAM_a45", "s17c_render_45.png")]:
        scene.camera = bpy.data.objects[camname]
        scene.render.filepath = str(C.OUT / out_name)
        bpy.ops.render.render(write_still=True)

    gates.finish()


main()
