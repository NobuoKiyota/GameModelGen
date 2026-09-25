"""b02_ac_teacher.py
どうぶつの森（あつ森）スタイルの完全2頭身デフォルメ体型：
- 寸胴でコロンとした愛らしいボディ（くびれなし、ぽてっとした円筒〜洋梨型）
- 短い手足、丸い球状の手（あつ森の村人の手）
- コロンとした丸いショートブーツ
- 魔法学園女性教師のカジュアルフォーマル衣装（襟付きシャツ、ショートケープ、Aラインプリーツスカート、ポーション瓶付きベルト）
- 下絵（ac_magic_teacher_ref_front/side.png）を頭部メッシュの頭頂〜首位置に1ミリの狂いもなく厳密にスケール・位置合わせ

実行方法:
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --python AnimeFace/steps/b02_ac_teacher.py
"""

import math
import os
import sys
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector, Matrix

BASE_DIR = Path(r"Z:\MeshCreator")
OUT_DIR = BASE_DIR / "AnimeFace" / "out"
HEAD_BLEND = OUT_DIR / "hair_h02_human.blend"
BODY_ONLY_BLEND = OUT_DIR / "teacher_ac_body_v02.blend"
FULL_PREVIEW_BLEND = OUT_DIR / "teacher_ac_preview_v02.blend"

REF_FRONT = BASE_DIR / "textures" / "human" / "ac_magic_teacher_ref_front.png"
REF_SIDE = BASE_DIR / "textures" / "human" / "ac_magic_teacher_ref_side.png"

# ==============================================================================
# 1. マテリアル定義（どうぶつの森風の温かみのあるトゥーンカラー）
# ==============================================================================
def create_toon_mat(name, base_rgb, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            if "Base Color" in bsdf.inputs:
                bsdf.inputs["Base Color"].default_value = (*base_rgb, 1.0)
            if "Roughness" in bsdf.inputs:
                bsdf.inputs["Roughness"].default_value = roughness
            if "Metallic" in bsdf.inputs:
                bsdf.inputs["Metallic"].default_value = metallic
    return mat

def setup_materials():
    materials = {
        "M_Skin": create_toon_mat("M_Skin", (1.0, 0.886, 0.831)),
        "M_Tights_Black": create_toon_mat("M_Tights_Black", (0.12, 0.11, 0.12)),
        "M_Shirt_White": create_toon_mat("M_Shirt_White", (0.96, 0.97, 0.98)),
        "M_Cape_Navy": create_toon_mat("M_Cape_Navy", (0.12, 0.18, 0.32)),
        "M_Skirt_Grey": create_toon_mat("M_Skirt_Grey", (0.22, 0.23, 0.27)),
        "M_Gold_Clasp": create_toon_mat("M_Gold_Clasp", (0.92, 0.72, 0.22), roughness=0.2, metallic=0.8),
        "M_Leather_Brown": create_toon_mat("M_Leather_Brown", (0.32, 0.18, 0.10)),
        "M_Leather_Dark": create_toon_mat("M_Leather_Dark", (0.20, 0.12, 0.08)),
        "M_Potion_Glass": create_toon_mat("M_Potion_Glass", (0.75, 0.85, 0.90), roughness=0.1),
        "M_Potion_Red": create_toon_mat("M_Potion_Red", (0.85, 0.20, 0.30), roughness=0.1),
        "M_Parchment": create_toon_mat("M_Parchment", (0.88, 0.80, 0.65)),
        "M_Drawers_White": create_toon_mat("M_Drawers_White", (0.95, 0.95, 0.95)),
    }
    return materials

def add_mirror_and_subsurf(obj, use_subsurf=True, subsurf_level=1):
    bpy.context.view_layer.objects.active = obj
    mod_mirror = obj.modifiers.new(name="Mirror", type='MIRROR')
    mod_mirror.use_axis[0] = True
    mod_mirror.use_clip = True
    mod_mirror.merge_threshold = 0.001
    
    if use_subsurf:
        mod_sub = obj.modifiers.new(name="Subsurf", type='SUBSURF')
        mod_sub.levels = subsurf_level
        mod_sub.render_levels = subsurf_level

def set_smooth_shading(mesh):
    for poly in mesh.polygons:
        poly.use_smooth = True

# ==============================================================================
# 2. どうぶつの森風 素体（Body_Base）の生成
# ==============================================================================
def create_ac_body_mesh(materials):
    """
    どうぶつの森風の2頭身デフォルメでありながら、解剖学的骨格系を無視しないトポロジー：
    - 脊柱・胸郭・骨盤のアライメント（S字重心バランス）
    - 肩関節（鎖骨〜肩峰）、肘関節（3本ループ屈曲対応）、手首、親指の突起を持つミトン調ハンド
    - 骨盤・股関節（大転子）、膝関節（膝蓋骨・3本ループ）、足首（くるぶし・踵接地）
    """
    mesh = bpy.data.meshes.new("Body_Base_Mesh")
    obj = bpy.data.objects.new("Body_Base", mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    # 首の接合ループ（12頂点、半分7頂点。hair_h02_human.blendに完全合致）
    neck_ring_base = [
        Vector((0.0, -0.0924, -0.3076)),
        Vector((-0.0497, -0.0791, -0.3076)),
        Vector((-0.0861, -0.0427, -0.3076)),
        Vector((-0.0994, 0.0070, -0.3076)),
        Vector((-0.0861, 0.0567, -0.3076)),
        Vector((-0.0497, 0.0931, -0.3076)),
        Vector((0.0, 0.1064, -0.3076)),
    ]
    
    # 骨格対応トルソー（頸椎〜胸郭〜腰椎〜骨盤）
    # 寸胴でありながら、胸郭の丸み、腰椎の前弯、仙骨・臀部の後方カーブを骨格的に反映
    torso_levels = [
        # 1. 頸椎下部・首の根元
        {"z": -0.335, "rx": 0.105, "ry": 0.105, "cy": 0.007},
        # 2. 鎖骨〜肩甲骨・胸郭上部
        {"z": -0.375, "rx": 0.130, "ry": 0.118, "cy": 0.005},
        # 3. 肩関節・胸部（大胸筋・胸郭最大幅）
        {"z": -0.425, "rx": 0.150, "ry": 0.130, "cy": 0.002},
        # 4. 胸郭下縁（みぞおち）
        {"z": -0.475, "rx": 0.155, "ry": 0.135, "cy": 0.004},
        # 5. 腰椎部（腹部・自然な前方カーブ）
        {"z": -0.525, "rx": 0.158, "ry": 0.138, "cy": 0.007},
        # 6. 骨盤上部（腸骨稜）
        {"z": -0.575, "rx": 0.160, "ry": 0.140, "cy": 0.010},
        # 7. 股関節（大転子・仙骨・臀部）
        {"z": -0.620, "rx": 0.152, "ry": 0.135, "cy": 0.012},
    ]
    
    rings = []
    v_neck = [bm.verts.new(p) for p in neck_ring_base]
    rings.append(v_neck)
    
    angles = [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0]
    for lev in torso_levels:
        r_verts = []
        for deg in angles:
            rad = math.radians(deg)
            x = -lev["rx"] * math.sin(rad)
            y = lev["cy"] - lev["ry"] * math.cos(rad)
            z = lev["z"]
            if deg == 0.0 or deg == 180.0:
                x = 0.0
            r_verts.append(bm.verts.new(Vector((x, y, z))))
        rings.append(r_verts)
        
    for i in range(len(rings) - 1):
        r1 = rings[i]
        r2 = rings[i+1]
        for j in range(len(r1) - 1):
            bm.faces.new([r1[j], r1[j+1], r2[j+1], r2[j]])
            
    # 骨盤底面（股下）を四角面で閉じる
    torso_bot = rings[-1]
    bm.faces.new([torso_bot[0], torso_bot[1], torso_bot[5], torso_bot[6]])
    bm.faces.new([torso_bot[1], torso_bot[2], torso_bot[4], torso_bot[5]])
    bm.faces.new([torso_bot[2], torso_bot[3], torso_bot[4]])

    # --- 骨格対応 脚（大腿骨〜膝関節〜脛骨〜足根骨） ---
    # 膝関節と足首に関節曲げ用のエッジループ（3本ループ構造）を配置
    leg_levels = [
        # 股関節（大腿骨頭）
        {"z": -0.60, "cx": -0.075, "cy": 0.012, "rx": 0.062, "ry": 0.062},
        # 大腿中央
        {"z": -0.66, "cx": -0.075, "cy": 0.011, "rx": 0.057, "ry": 0.057},
        # 膝上（曲げサポートループ1）
        {"z": -0.71, "cx": -0.075, "cy": 0.010, "rx": 0.053, "ry": 0.053},
        # 膝蓋骨（膝関節中心ループ2）
        {"z": -0.74, "cx": -0.075, "cy": 0.008, "rx": 0.052, "ry": 0.052},
        # 膝下（曲げサポートループ3）
        {"z": -0.77, "cx": -0.075, "cy": 0.008, "rx": 0.050, "ry": 0.050},
        # 下腿・ふくらはぎ（腓腹筋）
        {"z": -0.81, "cx": -0.075, "cy": 0.009, "rx": 0.048, "ry": 0.048},
        # 足首上（内果・外果サポート1）
        {"z": -0.84, "cx": -0.075, "cy": 0.007, "rx": 0.045, "ry": 0.045},
        # 足首関節中心（距骨）
        {"z": -0.86, "cx": -0.075, "cy": 0.005, "rx": 0.046, "ry": 0.052},
        # 足底（踵骨・中足骨・接地フラット面）
        {"z": -0.89, "cx": -0.075, "cy": -0.005, "rx": 0.048, "ry": 0.068},
    ]
    leg_rings = []
    leg_angles = [0, 45, 90, 135, 180, 225, 270, 315]
    for lev in leg_levels:
        lr = []
        for deg in leg_angles:
            rad = math.radians(deg)
            x = lev["cx"] + lev["rx"] * math.sin(rad)
            y = lev["cy"] + lev["ry"] * math.cos(rad)
            z = lev["z"]
            lr.append(bm.verts.new(Vector((x, y, z))))
        leg_rings.append(lr)
        
    for i in range(len(leg_rings) - 1):
        r1 = leg_rings[i]
        r2 = leg_rings[i+1]
        n = len(r1)
        for j in range(n):
            bm.faces.new([r1[j], r1[(j+1)%n], r2[(j+1)%n], r2[j]])
            
    top_leg = leg_rings[0]
    bm.faces.new([top_leg[0], top_leg[7], top_leg[2], top_leg[1]])
    bm.faces.new([top_leg[7], top_leg[6], top_leg[3], top_leg[2]])
    bm.faces.new([top_leg[6], top_leg[5], top_leg[4], top_leg[3]])
    
    bot_leg = leg_rings[-1]
    bm.faces.new([bot_leg[0], bot_leg[1], bot_leg[6], bot_leg[7]])
    bm.faces.new([bot_leg[1], bot_leg[2], bot_leg[5], bot_leg[6]])
    bm.faces.new([bot_leg[2], bot_leg[3], bot_leg[4], bot_leg[5]])

    # --- 骨格対応 腕（上腕骨〜肘関節〜前腕〜手首〜ミトン手） ---
    # 肘関節の曲げ3本ループ、手首の絞り、親指の付け根（母指球）を持たせたデフォルメハンド
    arm_levels = [
        # 1. 肩関節（上腕骨頭）
        {"x": -0.13, "cy": 0.002, "cz": -0.425, "ry": 0.052, "rz": 0.052},
        # 2. 上腕二頭筋・上腕骨中央
        {"x": -0.18, "cy": 0.001, "cz": -0.435, "ry": 0.048, "rz": 0.048},
        # 3. 肘関節上（曲げサポートループ1）
        {"x": -0.22, "cy": 0.000, "cz": -0.440, "ry": 0.045, "rz": 0.045},
        # 4. 肘関節中心（尺骨肘頭・関節軸ループ2）
        {"x": -0.24, "cy": 0.000, "cz": -0.442, "ry": 0.044, "rz": 0.044},
        # 5. 肘関節下（曲げサポートループ3）
        {"x": -0.26, "cy": 0.000, "cz": -0.445, "ry": 0.043, "rz": 0.043},
        # 6. 前腕（橈骨・尺骨）
        {"x": -0.30, "cy": 0.000, "cz": -0.448, "ry": 0.042, "rz": 0.042},
        # 7. 手首関節（手根部・くびれ）
        {"x": -0.33, "cy": 0.000, "cz": -0.450, "ry": 0.038, "rz": 0.038},
        # 8. 手のひら・母指球（親指付け根のふくらみ）
        {"x": -0.37, "cy": -0.008, "cz": -0.450, "ry": 0.048, "rz": 0.046},
        # 9. 手先先端（丸みのあるコロンとした先端）
        {"x": -0.42, "cy": -0.005, "cz": -0.450, "ry": 0.026, "rz": 0.026},
    ]
    arm_rings = []
    for idx, lev in enumerate(arm_levels):
        ar = []
        for deg in [0, 45, 90, 135, 180, 225, 270, 315]:
            rad = math.radians(deg)
            # レベル7（手のひら）の前方（親指側）を少しふくらませて母指球（親指）の骨格を表現
            thumb_bonus = 0.012 if (idx == 7 and deg in [315, 0, 45]) else 0.0
            
            x = lev["x"]
            y = lev["cy"] + (lev["ry"] + thumb_bonus) * math.cos(rad)
            z = lev["cz"] + (lev["rz"] + thumb_bonus) * math.sin(rad)
            ar.append(bm.verts.new(Vector((x, y, z))))
        arm_rings.append(ar)
        
    for i in range(len(arm_rings) - 1):
        r1 = arm_rings[i]
        r2 = arm_rings[i+1]
        n = len(r1)
        for j in range(n):
            bm.faces.new([r1[j], r1[(j+1)%n], r2[(j+1)%n], r2[j]])
            
    top_arm = arm_rings[0]
    bm.faces.new([top_arm[0], top_arm[7], top_arm[2], top_arm[1]])
    bm.faces.new([top_arm[7], top_arm[6], top_arm[3], top_arm[2]])
    bm.faces.new([top_arm[6], top_arm[5], top_arm[4], top_arm[3]])

    hand_tip = arm_rings[-1]
    bm.faces.new([hand_tip[0], hand_tip[1], hand_tip[6], hand_tip[7]])
    bm.faces.new([hand_tip[1], hand_tip[2], hand_tip[5], hand_tip[6]])
    bm.faces.new([hand_tip[2], hand_tip[3], hand_tip[4], hand_tip[5]])

    bm.to_mesh(mesh)
    bm.free()
    
    obj.data.materials.append(materials["M_Skin"])
    add_mirror_and_subsurf(obj, use_subsurf=True, subsurf_level=2)
    set_smooth_shading(mesh)
    return obj

# ==============================================================================
# 3. どうぶつの森風 Aラインプリーツスカート（Outfit_Skirt）
# ==============================================================================
def create_ac_skirt_mesh(materials):
    """
    寸胴ボディに合わせたふんわり広がるAラインプリーツスカート。
    Z=-0.50 から Z=-0.75 まで、コンパクトでコロンとしたフォルム。
    """
    mesh = bpy.data.meshes.new("Outfit_Skirt_Mesh")
    obj = bpy.data.objects.new("Outfit_Skirt", mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    num_half = 12
    levels = [
        {"z": -0.50, "rx": 0.160, "ry": 0.140, "cy": 0.005, "pleat": 0.003},
        {"z": -0.58, "rx": 0.190, "ry": 0.165, "cy": 0.008, "pleat": 0.008},
        {"z": -0.67, "rx": 0.230, "ry": 0.200, "cy": 0.010, "pleat": 0.014},
        {"z": -0.74, "rx": 0.265, "ry": 0.230, "cy": 0.012, "pleat": 0.018},
        {"z": -0.75, "rx": 0.260, "ry": 0.226, "cy": 0.012, "pleat": 0.016},
    ]
    skirt_rings = []
    for lev in levels:
        sr = []
        for i in range(num_half + 1):
            deg = (i / num_half) * 180.0
            rad = math.radians(deg)
            p = lev["pleat"] if (i % 2 == 1) else -lev["pleat"]
            if i == 0 or i == num_half:
                p = 0.0
            rx = lev["rx"] + p
            ry = lev["ry"] + p
            x = -rx * math.sin(rad)
            y = lev["cy"] - ry * math.cos(rad)
            z = lev["z"]
            if i == 0 or i == num_half:
                x = 0.0
            sr.append(bm.verts.new(Vector((x, y, z))))
        skirt_rings.append(sr)
        
    for i in range(len(skirt_rings) - 1):
        r1 = skirt_rings[i]
        r2 = skirt_rings[i+1]
        for j in range(num_half):
            bm.faces.new([r1[j], r1[j+1], r2[j+1], r2[j]])
            
    bm.to_mesh(mesh)
    bm.free()
    
    obj.data.materials.append(materials["M_Skirt_Grey"])
    mod_solid = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod_solid.thickness = 0.005
    add_mirror_and_subsurf(obj, use_subsurf=True, subsurf_level=1)
    set_smooth_shading(mesh)
    return obj

# ==============================================================================
# 4. どうぶつの森風 白ブラウス（Outfit_Shirt）
# ==============================================================================
def create_ac_shirt_mesh(materials):
    """
    清潔な白の丸襟ブラウスとふんわり袖。
    """
    mesh = bpy.data.meshes.new("Outfit_Shirt_Mesh")
    obj = bpy.data.objects.new("Outfit_Shirt", mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    # 胴体部分（Z=-0.32 〜 -0.52）
    shirt_levels = [
        {"z": -0.315, "rx": 0.100, "ry": 0.100, "cy": 0.007},
        {"z": -0.360, "rx": 0.120, "ry": 0.112, "cy": 0.005},
        {"z": -0.420, "rx": 0.148, "ry": 0.128, "cy": 0.003},
        {"z": -0.480, "rx": 0.158, "ry": 0.138, "cy": 0.005},
        {"z": -0.520, "rx": 0.162, "ry": 0.142, "cy": 0.006},
    ]
    num_half = 7
    s_rings = []
    for lev in shirt_levels:
        r = []
        for i in range(num_half):
            deg = (i / (num_half - 1)) * 180.0
            rad = math.radians(deg)
            x = -lev["rx"] * math.sin(rad)
            y = lev["cy"] - lev["ry"] * math.cos(rad)
            z = lev["z"]
            if i == 0 or i == num_half - 1:
                x = 0.0
            r.append(bm.verts.new(Vector((x, y, z))))
        s_rings.append(r)
        
    for i in range(len(s_rings) - 1):
        r1 = s_rings[i]
        r2 = s_rings[i+1]
        for j in range(num_half - 1):
            bm.faces.new([r1[j], r1[j+1], r2[j+1], r2[j]])
            
    # 白の丸襟（Collar）
    c1 = bm.verts.new(Vector((0.0, -0.102, -0.310)))
    c2 = bm.verts.new(Vector((-0.045, -0.095, -0.315)))
    c3 = bm.verts.new(Vector((-0.060, -0.108, -0.345)))
    c4 = bm.verts.new(Vector((0.0, -0.105, -0.345)))
    bm.faces.new([c1, c2, c3, c4])

    # 袖（ふんわりカフス袖）
    sleeve_levels = [
        {"x": -0.14, "cy": 0.000, "cz": -0.43, "ry": 0.058, "rz": 0.058},
        {"x": -0.21, "cy": 0.000, "cz": -0.44, "ry": 0.062, "rz": 0.062},
        {"x": -0.28, "cy": 0.000, "cz": -0.45, "ry": 0.052, "rz": 0.052},
        {"x": -0.30, "cy": 0.000, "cz": -0.45, "ry": 0.044, "rz": 0.044}, # カフス
    ]
    sl_rings = []
    for lev in sleeve_levels:
        sr = []
        for deg in [0, 45, 90, 135, 180, 225, 270, 315]:
            rad = math.radians(deg)
            x = lev["x"]
            y = lev["cy"] + lev["ry"] * math.cos(rad)
            z = lev["cz"] + lev["rz"] * math.sin(rad)
            sr.append(bm.verts.new(Vector((x, y, z))))
        sl_rings.append(sr)
        
    for i in range(len(sl_rings) - 1):
        r1 = sl_rings[i]
        r2 = sl_rings[i+1]
        n = len(r1)
        for j in range(n):
            bm.faces.new([r1[j], r1[(j+1)%n], r2[(j+1)%n], r2[j]])

    bm.to_mesh(mesh)
    bm.free()
    
    obj.data.materials.append(materials["M_Shirt_White"])
    mod_solid = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod_solid.thickness = 0.004
    add_mirror_and_subsurf(obj, use_subsurf=True, subsurf_level=1)
    set_smooth_shading(mesh)
    return obj

# ==============================================================================
# 5. どうぶつの森風 ショートケープ（Outfit_Cape）
# ==============================================================================
def create_ac_cape_mesh(materials):
    """
    肩を包むコロンとしたネイビーケープ。胸元に金の留め具。
    Z=-0.30 から Z=-0.48 まで。
    """
    mesh = bpy.data.meshes.new("Outfit_Cape_Mesh")
    obj = bpy.data.objects.new("Outfit_Cape", mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    levels = [
        {"z": -0.300, "rx": 0.104, "ry": 0.104, "cy": 0.007},
        {"z": -0.340, "rx": 0.130, "ry": 0.122, "cy": 0.005},
        {"z": -0.400, "rx": 0.185, "ry": 0.160, "cy": 0.002},
        {"z": -0.450, "rx": 0.230, "ry": 0.195, "cy": 0.000},
        {"z": -0.480, "rx": 0.250, "ry": 0.210, "cy": 0.000},
    ]
    num_half = 9
    c_rings = []
    for idx, lev in enumerate(levels):
        r = []
        for i in range(num_half):
            deg = (i / (num_half - 1)) * 180.0
            rad = math.radians(deg)
            x = -lev["rx"] * math.sin(rad)
            y = lev["cy"] - lev["ry"] * math.cos(rad)
            z = lev["z"]
            if i == 0 and idx >= 1:
                x = -0.020 - 0.010 * idx # 正面のスリット
            elif i == 0 or i == num_half - 1:
                x = 0.0
            r.append(bm.verts.new(Vector((x, y, z))))
        c_rings.append(r)
        
    for i in range(len(c_rings) - 1):
        r1 = c_rings[i]
        r2 = c_rings[i+1]
        for j in range(num_half - 1):
            bm.faces.new([r1[j], r1[j+1], r2[j+1], r2[j]])
            
    # 金の留め具（Clasp）
    bmesh.ops.create_cube(bm, size=0.015, matrix=Matrix.Translation(Vector((-0.025, -0.125, -0.355))))
    # 水平のバー
    bar_v1 = bm.verts.new(Vector((0.0, -0.127, -0.352)))
    bar_v2 = bm.verts.new(Vector((-0.025, -0.127, -0.352)))
    bar_v3 = bm.verts.new(Vector((-0.025, -0.127, -0.358)))
    bar_v4 = bm.verts.new(Vector((0.0, -0.127, -0.358)))
    bm.faces.new([bar_v1, bar_v2, bar_v3, bar_v4])

    bm.to_mesh(mesh)
    bm.free()
    
    obj.data.materials.append(materials["M_Cape_Navy"])
    obj.data.materials.append(materials["M_Gold_Clasp"])
    
    for poly in mesh.polygons:
        avg_y = sum(mesh.vertices[v].co.y for v in poly.vertices) / len(poly.vertices)
        if avg_y < -0.120:
            poly.material_index = 1
            
    mod_solid = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod_solid.thickness = 0.005
    add_mirror_and_subsurf(obj, use_subsurf=True, subsurf_level=1)
    set_smooth_shading(mesh)
    return obj

# ==============================================================================
# 6. どうぶつの森風 ショートブーツ（Outfit_Boots）
# ==============================================================================
def create_ac_boots_mesh(materials):
    """
    丸みのあるコロンとした愛らしいレザーショートブーツ。
    Z=-0.78 から Z=-0.96 まで。
    """
    mesh = bpy.data.meshes.new("Outfit_Boots_Mesh")
    obj = bpy.data.objects.new("Outfit_Boots", mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    levels = [
        # 履き口（少し外に開く）
        {"z": -0.78, "cx": -0.075, "cy": 0.008, "rx": 0.058, "ry": 0.058},
        {"z": -0.84, "cx": -0.075, "cy": 0.008, "rx": 0.052, "ry": 0.054},
        # 甲の丸み
        {"z": -0.90, "cx": -0.075, "cy": -0.010, "rx": 0.055, "ry": 0.072},
        # ソール上部
        {"z": -0.94, "cx": -0.075, "cy": -0.015, "rx": 0.058, "ry": 0.082},
        # ソール底面（床面接地）
        {"z": -0.96, "cx": -0.075, "cy": -0.015, "rx": 0.060, "ry": 0.084},
    ]
    num_pts = 8
    angles = [0, 45, 90, 135, 180, 225, 270, 315]
    rings = []
    for lev in levels:
        r = []
        for deg in angles:
            rad = math.radians(deg)
            x = lev["cx"] + lev["rx"] * math.sin(rad)
            y = lev["cy"] + lev["ry"] * math.cos(rad)
            z = lev["z"]
            r.append(bm.verts.new(Vector((x, y, z))))
        rings.append(r)
        
    for i in range(len(rings) - 1):
        r1 = rings[i]
        r2 = rings[i+1]
        for j in range(num_pts):
            bm.faces.new([r1[j], r1[(j+1)%num_pts], r2[(j+1)%num_pts], r2[j]])
            
    bot = rings[-1]
    bm.faces.new([bot[0], bot[1], bot[6], bot[7]])
    bm.faces.new([bot[1], bot[2], bot[5], bot[6]])
    bm.faces.new([bot[2], bot[3], bot[4], bot[5]])

    bm.to_mesh(mesh)
    bm.free()
    
    obj.data.materials.append(materials["M_Leather_Brown"])
    obj.data.materials.append(materials["M_Leather_Dark"])
    for poly in mesh.polygons:
        avg_z = sum(mesh.vertices[v].co.z for v in poly.vertices) / len(poly.vertices)
        if avg_z < -0.94:
            poly.material_index = 1
            
    mod_solid = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod_solid.thickness = 0.004
    add_mirror_and_subsurf(obj, use_subsurf=True, subsurf_level=1)
    set_smooth_shading(mesh)
    return obj

# ==============================================================================
# 7. どうぶつの森風 ベルト＆小物（Belt & Accessories）
# ==============================================================================
def create_ac_accessories(materials):
    mesh = bpy.data.meshes.new("Outfit_Belt_Mesh")
    obj = bpy.data.objects.new("Outfit_Belt", mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    belt_pts = 16
    for i in range(belt_pts):
        deg = (i / belt_pts) * 360.0
        rad = math.radians(deg)
        rx = 0.165
        ry = 0.145
        x = rx * math.sin(rad)
        y = 0.006 - ry * math.cos(rad)
        z_top = -0.510
        z_bot = -0.535
        bm.verts.new(Vector((x, y, z_top)))
        bm.verts.new(Vector((x, y, z_bot)))
        
    bm.verts.ensure_lookup_table()
    for i in range(belt_pts):
        i1 = i * 2
        i2 = i1 + 1
        i3 = ((i + 1) % belt_pts) * 2
        i4 = i3 + 1
        bm.faces.new([bm.verts[i1], bm.verts[i3], bm.verts[i4], bm.verts[i2]])
        
    # バックル（正面中央）
    bmesh.ops.create_cube(bm, size=0.030, matrix=Matrix.Translation(Vector((0.0, -0.142, -0.522))))
    
    # ポーション瓶（丸フラスコ）
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.022, matrix=Matrix.Translation(Vector((-0.14, -0.06, -0.53))))
    # 巻物ホルダー
    bmesh.ops.create_cube(bm, size=0.035, matrix=Matrix.Translation(Vector((-0.16, 0.01, -0.53))))

    bm.to_mesh(mesh)
    bm.free()
    obj.data.materials.append(materials["M_Leather_Brown"])
    obj.data.materials.append(materials["M_Gold_Clasp"])
    set_smooth_shading(mesh)
    return obj

# ==============================================================================
# 8. 下絵リファレンスの厳密な自動配置（頭部メッシュの頭頂〜首に100%整合）
# ==============================================================================
def setup_strict_references_and_cameras():
    for obj in bpy.data.objects:
        if obj.type in {'CAMERA', 'LIGHT', 'EMPTY'}:
            bpy.data.objects.remove(obj, do_unlink=True)
            
    # 頭部メッシュ寸法基準:
    # 頭頂: Z = 0.35, 首最下端: Z = -0.3076 -> 高さ 0.6576m
    # 新下絵（ac_magic_teacher_ref_front.png）画像サイズ 480x1200:
    # 頭頂ピクセル = 80px, 首付け根ピクセル = 450px -> 頭部高さ 370px
    # 厳密なスケール: S = 0.6576 / (370 / 1200) = 2.1328m
    # 厳密なZ位置: 頭頂 80px が Z = 0.35 に一致するように配置
    # 1px あたりの長さ = 0.6576 / 370 = 0.0017773m
    # 画像中心（600px）の Z = 0.35 - (600 - 80) * 0.0017773 = 0.35 - 0.9242 = -0.5742m
    
    scale_val = 2.1328
    loc_z = -0.5742
    
    # 1. 正面下絵（背後に配置）
    if REF_FRONT.exists():
        empty_front = bpy.data.objects.new("REF_Front", None)
        empty_front.empty_display_type = 'IMAGE'
        img_f = bpy.data.images.load(str(REF_FRONT))
        empty_front.data = img_f
        empty_front.location = (0.0, 0.8, loc_z)
        empty_front.scale = (scale_val, scale_val, scale_val)
        empty_front.show_in_front = False
        bpy.context.scene.collection.objects.link(empty_front)
        print(f"[REF OK] Setup Front Ref at loc_z={loc_z}, scale={scale_val}")

    # 2. 側面板下絵（背後に配置）
    if REF_SIDE.exists():
        empty_side = bpy.data.objects.new("REF_Side", None)
        empty_side.empty_display_type = 'IMAGE'
        img_s = bpy.data.images.load(str(REF_SIDE))
        empty_side.data = img_s
        empty_side.location = (0.8, 0.0, loc_z)
        empty_side.rotation_euler = (0.0, 0.0, math.radians(90.0))
        empty_side.scale = (scale_val, scale_val, scale_val)
        empty_side.show_in_front = False
        bpy.context.scene.collection.objects.link(empty_side)
        print(f"[REF OK] Setup Side Ref at loc_z={loc_z}, scale={scale_val}")

    # カメラ配置（2頭身キャラクター全体を美しく収める）
    # 正面
    cam_f = bpy.data.cameras.new("CAM_Front")
    cam_f.type = 'ORTHO'
    cam_f.ortho_scale = 1.6
    cam_f_obj = bpy.data.objects.new("CAM_Front", cam_f)
    cam_f_obj.location = (0.0, -3.0, -0.32)
    cam_f_obj.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    bpy.context.scene.collection.objects.link(cam_f_obj)
    
    # 側面
    cam_s = bpy.data.cameras.new("CAM_Side")
    cam_s.type = 'ORTHO'
    cam_s.ortho_scale = 1.6
    cam_s_obj = bpy.data.objects.new("CAM_Side", cam_s)
    cam_s_obj.location = (-3.0, 0.0, -0.32)
    cam_s_obj.rotation_euler = (math.radians(90.0), 0.0, math.radians(-90.0))
    bpy.context.scene.collection.objects.link(cam_s_obj)

    # 斜め45度
    cam_45 = bpy.data.cameras.new("CAM_Persp45")
    cam_45.lens = 75
    cam_45_obj = bpy.data.objects.new("CAM_Persp45", cam_45)
    cam_45_obj.location = (-1.8, -1.8, 0.0)
    cam_45_obj.rotation_euler = (math.radians(80.0), 0.0, math.radians(-45.0))
    bpy.context.scene.collection.objects.link(cam_45_obj)
    
    # ライティング
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.82, 0.84, 0.86, 1.0)
        bg_node.inputs["Strength"].default_value = 1.0

    light_data = bpy.data.lights.new("Sun_Main", 'SUN')
    light_data.energy = 3.0
    light_obj = bpy.data.objects.new("Sun_Main", light_data)
    light_obj.rotation_euler = (math.radians(50.0), math.radians(15.0), math.radians(-35.0))
    bpy.context.scene.collection.objects.link(light_obj)
    
    fill_data = bpy.data.lights.new("Sun_Fill", 'SUN')
    fill_data.energy = 1.5
    fill_obj = bpy.data.objects.new("Sun_Fill", fill_data)
    fill_obj.rotation_euler = (math.radians(45.0), math.radians(-30.0), math.radians(140.0))
    bpy.context.scene.collection.objects.link(fill_obj)

# ==============================================================================
# 9. メイン処理
# ==============================================================================
def main():
    print("=== Step b02: Generating Animal Crossing Style Chibi Body & Outfit ===")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    materials = setup_materials()
    
    print("-> Creating AC Body Base...")
    body = create_ac_body_mesh(materials)
    
    print("-> Creating AC Shirt...")
    shirt = create_ac_shirt_mesh(materials)
    
    print("-> Creating AC Skirt...")
    skirt = create_ac_skirt_mesh(materials)
    
    print("-> Creating AC Cape...")
    cape = create_ac_cape_mesh(materials)
    
    print("-> Creating AC Boots...")
    boots = create_ac_boots_mesh(materials)
    
    print("-> Creating AC Accessories...")
    belt = create_ac_accessories(materials)
    
    print("-> Setting up Strict References and Cameras...")
    setup_strict_references_and_cameras()
    
    # 保存1: 身体・衣装のみのブレンドファイル
    BODY_ONLY_BLEND.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BODY_ONLY_BLEND))
    print(f"[OK] Saved AC Body & Outfit scene to: {BODY_ONLY_BLEND}")
    
    # 保存2: 頭部モデルをアペンドして全体合体プレビューブレンドを作成
    if HEAD_BLEND.exists():
        print(f"-> Appending head objects from {HEAD_BLEND}...")
        with bpy.data.libraries.load(str(HEAD_BLEND), link=False) as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects if not name.startswith("CAM_") and not name.startswith("REF_") and not name.startswith("ReviewSun")]
            
        for obj in data_to.objects:
            if obj:
                bpy.context.scene.collection.objects.link(obj)
                
        bpy.ops.wm.save_as_mainfile(filepath=str(FULL_PREVIEW_BLEND))
        print(f"[OK] Saved Full AC Preview scene to: {FULL_PREVIEW_BLEND}")
        
        # レンダリング画像出力
        scene = bpy.context.scene
        scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
        scene.render.resolution_x = 1000
        scene.render.resolution_y = 1200
        scene.render.image_settings.file_format = 'PNG'
        
        cams = [
            ("teacher_ac_front.png", "CAM_Front"),
            ("teacher_ac_side.png", "CAM_Side"),
            ("teacher_ac_a45.png", "CAM_Persp45"),
        ]
        for fname, cname in cams:
            cam_obj = bpy.data.objects.get(cname)
            if cam_obj:
                scene.camera = cam_obj
                out_path = OUT_DIR / fname
                scene.render.filepath = str(out_path)
                bpy.ops.render.render(write_still=True)
                print(f"[RENDER OK] {out_path}")

    print("=== Step b02 Completed Successfully! ===")

if __name__ == "__main__":
    main()
