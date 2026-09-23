"""S17e: オブジェクト整理（後編 動画 31:00〜32:31）。

字幕との対応:
  31:00〜31:24 まつ毛と顔をJoin（Ctrl+J）して名前をFaceに                → 主まつ毛(`Eyelash`)を`Face`にJoin。目は別オブジェクトのまま
  31:24〜31:40 目はSubdivision使っていないので顔とは別オブジェクトのまま → 何もしない（`Eye`はそのまま）
  31:40〜32:19 コレクションを分ける（作業用／参考用）、参考用を移す      → 既にS01でREF（下絵・カメラ）／MODEL（作業対象）／GUIDEに
                                                                       分かれているため、今回は変更不要（確認のみ）

設計:
  - Joinの対象は動画の言及通り「まつ毛と顔」のみ（房3つ・眉・二重線・黒目は対象外。動画でも触れていない）
  - Joinは、アクティブオブジェクトのモディファイア・オブジェクト名を残す。`Face`をアクティブにし、
    `Eyelash`を選択してJoinすることで、モディファイア（Mirror→Subdivision 1/2）・名前は`Face`のまま
  - Join後、頂点・面の数が「元のFace＋元のEyelash」と一致すること、クリース（前の稜）が保持されていることを確認する

入力: out/face_s17d_gen.blend   出力: out/face_s17e_gen.blend, out/s17e_report.json, out/s17e_render_*.png
実行: blender --background --factory-startup --python steps/s17e_organize.py
"""
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402

STEP = "s17e"
gates = C.Gates(STEP)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s17d_gen.blend"))
    for o in bpy.data.objects:
        if o.type == "MESH" and o.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

    # ---- コレクション構成の確認（S01で既にREF/MODEL/GUIDEに分離済みのはず。動画31:40〜32:19の対応）
    coll_names = {c.name for c in bpy.data.collections}
    gates.check("コレクションは既にREF（下絵・カメラ）/MODEL（作業対象）/GUIDEに分かれている（変更不要）",
                {"REF", "MODEL", "GUIDE"} <= coll_names, sorted(coll_names))
    ref_objs = {o.name for o in bpy.data.collections["REF"].objects}
    model_objs = {o.name for o in bpy.data.collections["MODEL"].objects}
    gates.note("REFコレクションの内容（下絵・カメラ）", sorted(ref_objs))
    gates.note("MODELコレクションの内容（作業対象）", sorted(model_objs))

    # ---- まつ毛(Eyelash)をFaceにJoin
    face = bpy.data.objects["Face"]
    lash = bpy.data.objects["Eyelash"]
    n_v_face, n_f_face = len(face.data.vertices), len(face.data.polygons)
    n_v_lash, n_f_lash = len(lash.data.vertices), len(lash.data.polygons)
    gates.check("入力: FaceとEyelashは、どちらもMirror→Subdivision(1/2)、同じマテリアル1枚（CharacterBase）",
                [m.type for m in face.modifiers] == ["MIRROR", "SUBSURF"] and [m.type for m in lash.modifiers] == ["MIRROR", "SUBSURF"]
                and [m.name for m in face.data.materials] == [m.name for m in lash.data.materials] == ["CharacterBase"])

    for o in bpy.context.selected_objects:
        o.select_set(False)
    lash.select_set(True)
    face.select_set(True)
    bpy.context.view_layer.objects.active = face
    bpy.ops.object.join()

    gates.check(f"Join後: Faceの頂点数・面数が旧Face+旧Eyelashに一致（{n_v_face}+{n_v_lash}={n_v_face+n_v_lash}, {n_f_face}+{n_f_lash}={n_f_face+n_f_lash}）",
                len(face.data.vertices) == n_v_face + n_v_lash and len(face.data.polygons) == n_f_face + n_f_lash,
                (len(face.data.vertices), len(face.data.polygons)))
    gates.check("Join後: モディファイアはMirror→Subdivision(1/2)のまま", [m.type for m in face.modifiers] == ["MIRROR", "SUBSURF"])
    gates.check("Join後: マテリアルは共有のCharacterBase1枚のまま", [m.name for m in face.data.materials] == ["CharacterBase"])
    gates.check("Join後: Eyelashオブジェクトは無くなった（名前はFaceのまま）", "Eyelash" not in bpy.data.objects)

    cre = face.data.attributes.get("crease_edge")
    n_cre = sum(1 for d in cre.data if d.value >= 1.0) if cre else 0
    gates.note("Join後: クリース1.0の辺の数（旧Faceの34＋旧Eyelashの前稜21本前後が保持されているか）", n_cre)

    others_kept = all(n in bpy.data.objects for n in ["Eye", "Eyebrow", "DoubleLid", "Eyelash.001", "Eyelash.002", "Eyelash.003"])
    gates.check("他のオブジェクト（Eye・Eyebrow・DoubleLid・房3つ）はそのまま残っている", others_kept)

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s17e_gen.blend"), compress=False)

    # ---- レビュー用レンダリング
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
    keep = {"Face", "Eye", "Eyebrow", "DoubleLid", "Eyelash.001", "Eyelash.002", "Eyelash.003"}
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.hide_render = o.name not in keep
    for camname, out_name in [("CAM_front", "s17e_render_front.png"), ("CAM_a45", "s17e_render_45.png")]:
        scene.camera = bpy.data.objects[camname]
        scene.render.filepath = str(C.OUT / out_name)
        bpy.ops.render.render(write_still=True)

    gates.finish()


main()
