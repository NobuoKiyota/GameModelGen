"""S18-2: 素体の頂点グループ・基準点を作る（保留事項②）。目・鼻・口を、後で個別に拡大縮小できるようにする下地。

設計:
  - 頂点グループ（`Face`オブジェクト、重み1.0）:
    - `grp_eye`: 黒目の中心（CEN_EYE）から75mm以内の頂点（眼窩内側R0〜center、まつ毛は対象外）
    - `grp_nose`: 鼻先の頂点（index42）から25mm以内の頂点
    - `grp_mouth`: 口の縁9頂点＋口の中18頂点（S12で確定したindex、S17dで使ったものと同じ）
  - 基準点（`GUIDE`コレクションへ配置する空オブジェクト、Plain Axes、表示サイズ小）:
    - `GUIDE_eye_center`: 黒目の中心
    - `GUIDE_nose_tip`: 鼻先
    - `GUIDE_mouth_center`: 口の中心（口の縁9頂点の平均）
  - Mirrorモディファイア（Face、X軸）は変更しない。半分メッシュの頂点グループを対象にスケール操作をすれば、
    評価時にMirrorが自動でもう半分に反映される（グループをL/R別に分ける必要はない）

入力: out/face_s17e_gen.blend   出力: out/face_s17e_gen.blend（上書き）, out/s18_2_report.json
実行: blender --background --factory-startup --python steps/s18_2_vertex_groups.py
"""
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402

STEP = "s18_2"
gates = C.Gates(STEP)

CEN_EYE = Vector((-0.1217, -0.1485, -0.001))
NOSE_TIP_IDX = 42
MOUTH_RIM = [26, 203, 27, 28, 29, 30, 31, 218, 32]
MOUTH_CAVITY = list(range(495, 513))
EYE_R = 0.075
NOSE_R = 0.025


def make_group(obj, name, indices):
    vg = obj.vertex_groups.new(name=name)
    vg.add(list(indices), 1.0, 'REPLACE')
    return vg


def make_empty(name, loc, collection):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = 'PLAIN_AXES'
    e.empty_display_size = 0.02
    e.location = loc
    collection.objects.link(e)
    return e


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s17e_gen.blend"))
    face = bpy.data.objects["Face"]
    me = face.data
    gates.check("入力: Faceに頂点グループがまだ無い", len(face.vertex_groups) == 0, [g.name for g in face.vertex_groups])

    eye_idx = [v.index for v in me.vertices if (v.co - CEN_EYE).length < EYE_R]
    nose_pos = me.vertices[NOSE_TIP_IDX].co.copy()
    nose_idx = [v.index for v in me.vertices if (v.co - nose_pos).length < NOSE_R]
    mouth_idx = sorted(set(MOUTH_RIM + MOUTH_CAVITY))

    gates.check("grp_eye: 頂点が見つかった（黒目中心から75mm以内）", len(eye_idx) > 0, len(eye_idx))
    gates.check("grp_nose: 頂点が見つかった（鼻先から25mm以内）", len(nose_idx) > 0, len(nose_idx))
    gates.check("grp_mouth: 27頂点（口の縁9＋口の中18）", len(mouth_idx) == 27, len(mouth_idx))

    make_group(face, "grp_eye", eye_idx)
    make_group(face, "grp_nose", nose_idx)
    make_group(face, "grp_mouth", mouth_idx)
    gates.check("Faceに3つの頂点グループができた", [g.name for g in face.vertex_groups] == ["grp_eye", "grp_nose", "grp_mouth"])

    # ---- 検証: 各グループの重みが実際に1.0で入っている
    def weight_ok(vg, idx_list):
        for i in idx_list[:5]:
            w = None
            for g in me.vertices[i].groups:
                if g.group == vg.index:
                    w = g.weight
            if w is None or abs(w - 1.0) > 1e-6:
                return False
        return True
    gv = {g.name: g for g in face.vertex_groups}
    gates.check("grp_eye/grp_nose/grp_mouthの重みは1.0",
                weight_ok(gv["grp_eye"], eye_idx) and weight_ok(gv["grp_nose"], nose_idx) and weight_ok(gv["grp_mouth"], mouth_idx))

    # ---- 基準点（GUIDEコレクション）
    guide = bpy.data.collections["GUIDE"]
    gates.check("入力: GUIDEコレクションはまだ空", len(guide.objects) == 0, len(guide.objects))
    mouth_center = sum((me.vertices[i].co for i in MOUTH_RIM), Vector()) / len(MOUTH_RIM)
    make_empty("GUIDE_eye_center", CEN_EYE, guide)
    make_empty("GUIDE_nose_tip", nose_pos, guide)
    make_empty("GUIDE_mouth_center", mouth_center, guide)
    gates.check("GUIDEコレクションに基準点3つができた", len(guide.objects) == 3, [o.name for o in guide.objects])

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s17e_gen.blend"), compress=False)
    gates.finish()


main()
