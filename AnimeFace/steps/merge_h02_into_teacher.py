"""顔・髪は ①(hair_h02_human.blend)、それ以外は ②(teacher_ac_preview_v06_animated.blend) のマージ。

方針:
  - ② を開き、② の髪オブジェクト(Hair_Back*/Hair_Bangs*/Hair_Fill*)と空コレクションを削除
  - ① の髪オブジェクトを Append し、01_Head/Hair/{Hair_Back,Hair_Bang} へ配置
  - ② の Face・目・眉・まつ毛(首は体に合わせて詰めてある)はそのまま使う
  - 髪に 頂点グループ "Head"(重み1.0) と Armature モディファイア(最後)を付ける
  - Transform は安全な物だけ焼く（Mirror の対称面が動く物は焼かない）
  - モディファイアは Apply しない
出力: out/teacher_ac_merged_face_hair.blend （①②は上書きしない）
"""
import sys
from pathlib import Path

import bpy
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.common import Gates

ROOT = Path(__file__).resolve().parent.parent
SRC_HAIR = ROOT / "out" / "hair_h02_human.blend"
SRC_BASE = ROOT / "out" / "teacher_ac_preview_v06_animated.blend"
DST = ROOT / "out" / "teacher_ac_merged_face_hair.blend"
ARM = "Armature_Teacher"
G = Gates("merge_h02_into_teacher")

bpy.ops.wm.open_mainfile(filepath=str(SRC_BASE))
arm = bpy.data.objects[ARM]

is_hair = lambda n: n.startswith(("Hair_Back", "Hair_Bangs", "Hair_Fill"))

# ---- 1. ② の髪を削除 -------------------------------------------------
old = [o for o in bpy.data.objects if is_hair(o.name)]
n_old = len(old)
old_meshes = {o.data for o in old}
for o in old:
    bpy.data.objects.remove(o, do_unlink=True)
for me in old_meshes:
    if me.users == 0:
        bpy.data.meshes.remove(me)

head_c = bpy.data.collections["01_Head"]
hair_c = bpy.data.collections["Hair"]
for cn in ("Hair_Fill", "Hair_Back", "Hair_Bang"):
    c = bpy.data.collections[cn]
    for ch in list(c.children):        # 空の子コレクション (HairBack 1 等)
        assert not ch.objects, ch.name
        bpy.data.collections.remove(ch)
    assert not c.objects, cn
bpy.data.collections.remove(bpy.data.collections["Hair_Fill"])
back_c = bpy.data.collections["Hair_Back"]
bang_c = bpy.data.collections["Hair_Bang"]

# ---- 2. ① の髪を Append ---------------------------------------------
with bpy.data.libraries.load(str(SRC_HAIR), link=False) as (df, dt):
    names = [n for n in df.objects if is_hair(n)]
    dt.objects = names
new = [o for o in dt.objects if o is not None]
G.check("① の髪オブジェクトを取り込み", len(new) == len(names) == 18, f"{len(new)}個")

base_mat = bpy.data.materials["HairBase"]
for o in new:
    (back_c if o.name.startswith("Hair_Back") else bang_c).objects.link(o)
    for s in o.material_slots:
        if s.material and s.material.name.startswith("HairBase") and s.material != base_mat:
            dup = s.material
            s.material = base_mat
            if dup.users == 0:
                bpy.data.materials.remove(dup)
bpy.context.view_layer.update()


# ---- 3. Transform を焼く（安全な物だけ） -------------------------------
def bake_safe(o):
    """Mirror が無い、または対称面(ローカルX=0)がワールドX=0のままなら焼ける"""
    mir = [m for m in o.modifiers if m.type == "MIRROR"]
    if not mir:
        return True
    ok_loc = abs(o.location.x) < 1e-6
    ok_rot = abs(o.rotation_euler.y) < 1e-6 and abs(o.rotation_euler.z) < 1e-6
    return ok_loc and ok_rot


baked, kept = [], []
for o in new:
    ident = (o.matrix_world - Matrix.Identity(4)).to_4x4()
    is_id = max(abs(x) for r in ident for x in r) < 1e-7
    if is_id:
        continue
    if bake_safe(o):
        o.data.transform(o.matrix_world)
        o.matrix_world = Matrix.Identity(4)
        baked.append(o.name)
    else:
        kept.append(o.name)
print("焼いた:", baked)
print("焼かず(Mirror対称面が動く):", kept)

# ---- 4. Head ウェイト + Armature ---------------------------------------
for o in new:
    vg = o.vertex_groups.new(name="Head")
    vg.add(list(range(len(o.data.vertices))), 1.0, "REPLACE")
    m = o.modifiers.new("Armature", "ARMATURE")
    m.object = arm
    m.use_vertex_groups = True
    m.use_bone_envelopes = False

bpy.ops.wm.save_as_mainfile(filepath=str(DST))

# ---- 5. 数値ゲート -----------------------------------------------------
names_now = {o.name for o in bpy.data.objects}
G.check("旧髪(Fill/旧Back/旧Bangs)が残っていない",
        not any(is_hair(n) and n not in {o.name for o in new} for n in names_now), f"旧{n_old}個削除")
G.check("髪オブジェクト数 = ①の18", sum(is_hair(n) for n in names_now) == 18)
G.check("全髪の最後のモディファイアが ARMATURE(Armature_Teacher)",
        all(o.modifiers[-1].type == "ARMATURE" and o.modifiers[-1].object == arm for o in new))
G.check("全髪が Head グループ 100%",
        all(len(o.vertex_groups) == 1 and all(v.groups[0].weight == 1.0 and len(v.groups) == 1 for v in o.data.vertices)
            for o in new))
G.check("HairBase が1つだけ・全髪がそれを使用",
        [m.name for m in bpy.data.materials if m.name.startswith("HairBase")] == ["HairBase"]
        and all(o.material_slots and o.material_slots[0].material == base_mat for o in new))
G.check("顔パーツ数(01_Head直下 MESH 7個: Face/Eye/Eyebrow/DoubleLid/Eyelash×3)",
        sum(o.type == "MESH" for o in head_c.objects) == 7)
G.check("体・服のオブジェクトを触っていない(02_Body 4個/03_Outfit 6個)",
        len(bpy.data.collections["02_Body"].objects) == 4 and len(bpy.data.collections["03_Outfit"].objects) == 6)
G.check("アニメ(Action)が残っている", len(bpy.data.actions) >= 3, [a.name for a in bpy.data.actions])
G.note("焼いた", baked)
G.note("焼かなかった", kept)
G.finish()
