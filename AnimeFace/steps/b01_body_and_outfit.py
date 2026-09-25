"""b01_body_and_outfit.py
参考動画（ふさこ氏第2回体の作り方、第5回服編、第39回袖・ドロワーズ構造）に基づき、
頭部モデル（hair_h02_human.blend）の首の12頂点ループに完全合致する素体（ボディ）および
魔法学園女性教師のカジュアルフォーマル衣装（ケープ、ベスト、シャツ、プリーツスカート、ブーツ、ポーチ等）を
プロシージャルに完全自動生成するスクリプト。

実行方法:
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --python AnimeFace/steps/b01_body_and_outfit.py
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
BODY_ONLY_BLEND = OUT_DIR / "teacher_body_outfit_v01.blend"
FULL_PREVIEW_BLEND = OUT_DIR / "teacher_full_preview_v01.blend"
REF_FRONT = BASE_DIR / "textures" / "human" / "magic_teacher_ref_front.png"
REF_SIDE = BASE_DIR / "textures" / "human" / "magic_teacher_ref_side.png"

# ==============================================================================
# 1. ユーティリティ & マテリアル定義
# ==============================================================================
def create_toon_mat(name, base_rgb, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            # Base color
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
        "M_Tights_Black": create_toon_mat("M_Tights_Black", (0.10, 0.09, 0.10)),
        "M_Shirt_White": create_toon_mat("M_Shirt_White", (0.95, 0.96, 0.98)),
        "M_Vest_Charcoal": create_toon_mat("M_Vest_Charcoal", (0.12, 0.12, 0.15)),
        "M_Cape_Navy": create_toon_mat("M_Cape_Navy", (0.08, 0.12, 0.22)),
        "M_Skirt_Grey": create_toon_mat("M_Skirt_Grey", (0.16, 0.17, 0.20)),
        "M_Gold_Trim": create_toon_mat("M_Gold_Trim", (0.95, 0.75, 0.25), roughness=0.3, metallic=0.8),
        "M_Leather_Brown": create_toon_mat("M_Leather_Brown", (0.24, 0.14, 0.08)),
        "M_Leather_Dark": create_toon_mat("M_Leather_Dark", (0.15, 0.09, 0.05)),
        "M_Gem_Cyan": create_toon_mat("M_Gem_Cyan", (0.10, 0.80, 0.92), roughness=0.1, metallic=0.3),
        "M_Tie_Blue": create_toon_mat("M_Tie_Blue", (0.12, 0.16, 0.28)),
        "M_Potion_Red": create_toon_mat("M_Potion_Red", (0.85, 0.15, 0.28), roughness=0.1),
        "M_Parchment": create_toon_mat("M_Parchment", (0.88, 0.80, 0.65)),
        "M_Drawers_White": create_toon_mat("M_Drawers_White", (0.92, 0.92, 0.95)),
    }
    return materials

def add_mirror_and_subsurf(obj, use_subsurf=True, subsurf_level=1):
    bpy.context.view_layer.objects.active = obj
    # Mirror Modifier
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
# 2. 素体（Body_Base）の生成
# ==============================================================================
def create_body_mesh(materials):
    """
    頭部（Face）の最下端12頂点ループ（半分7頂点）に完全合致する首から始まり、
    胸部、ウエスト、ヒップ、脚、足、腕（Tポーズ）を生成。
    すべて四角面（Quad）ベースでミラー構成。
    """
    mesh = bpy.data.meshes.new("Body_Base_Mesh")
    obj = bpy.data.objects.new("Body_Base", mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    # --- 首〜胴体の輪郭リング（Y中心 = 0.007、X<=0の7頂点） ---
    # 角度: 0(前正中), 30, 60, 90(側面), 120, 150, 180(後正中)
    # 首の基本接合ループ（hair_h02_human.blendの測定値に完全一致）
    neck_ring_base = [
        Vector((0.0, -0.0924, -0.3076)),
        Vector((-0.0497, -0.0791, -0.3076)),
        Vector((-0.0861, -0.0427, -0.3076)),
        Vector((-0.0994, 0.0070, -0.3076)),
        Vector((-0.0861, 0.0567, -0.3076)),
        Vector((-0.0497, 0.0931, -0.3076)),
        Vector((0.0, 0.1064, -0.3076)),
    ]
    
    # 胴体の縦方向のリング定義 (z, rad_x, rad_y, center_y)
    torso_levels = [
        # 首下
        {"z": -0.34, "rx": 0.098, "ry": 0.098, "cy": 0.007},
        {"z": -0.38, "rx": 0.115, "ry": 0.105, "cy": 0.005},
        # 肩・鎖骨
        {"z": -0.42, "rx": 0.145, "ry": 0.110, "cy": 0.000},
        # 胸（バストトップ、ふっくらAlt+S）
        {"z": -0.47, "rx": 0.155, "ry": 0.125, "cy": -0.015},
        # アンダーバスト
        {"z": -0.52, "rx": 0.140, "ry": 0.105, "cy": -0.005},
        # ウエスト（くびれ）
        {"z": -0.58, "rx": 0.125, "ry": 0.095, "cy": 0.005},
        # 骨盤・ヒップ上部
        {"z": -0.65, "rx": 0.145, "ry": 0.115, "cy": 0.015},
        # ヒップ最大径（お尻ふくらみ）
        {"z": -0.72, "rx": 0.155, "ry": 0.130, "cy": 0.025},
        # 股下
        {"z": -0.78, "rx": 0.145, "ry": 0.120, "cy": 0.020},
    ]
    
    # 各リングの頂点リスト
    rings = []
    # 最初のリング（首最上端）
    v_neck = [bm.verts.new(p) for p in neck_ring_base]
    rings.append(v_neck)
    
    angles = [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0]
    for lev in torso_levels:
        r_verts = []
        for deg in angles:
            rad = math.radians(deg)
            # 前が -Y, 後が +Y, 左が -X (ミラー)
            x = -lev["rx"] * math.sin(rad)
            y = lev["cy"] - lev["ry"] * math.cos(rad)
            z = lev["z"]
            # 正中線の X を厳密に 0.0 にクリップ
            if deg == 0.0 or deg == 180.0:
                x = 0.0
            r_verts.append(bm.verts.new(Vector((x, y, z))))
        rings.append(r_verts)
        
    # トルソーの四角面張り
    for i in range(len(rings) - 1):
        r1 = rings[i]
        r2 = rings[i+1]
        for j in range(len(r1) - 1):
            # 四角面 (r1[j], r1[j+1], r2[j+1], r2[j])
            bm.faces.new([r1[j], r1[j+1], r2[j+1], r2[j]])
            
    # --- 脚の生成（股下から下へ） ---
    # 股下の底面リングから脚ループを形成
    leg_levels = [
        # 太もも付け根
        {"z": -0.82, "cx": -0.075, "cy": 0.020, "rx": 0.065, "ry": 0.065},
        # 太もも中央
        {"z": -0.90, "cx": -0.075, "cy": 0.015, "rx": 0.060, "ry": 0.060},
        # 膝
        {"z": -0.98, "cx": -0.075, "cy": 0.010, "rx": 0.052, "ry": 0.052},
        # ふくらはぎ
        {"z": -1.06, "cx": -0.075, "cy": 0.012, "rx": 0.055, "ry": 0.055},
        # 足首
        {"z": -1.15, "cx": -0.075, "cy": 0.010, "rx": 0.045, "ry": 0.045},
        # 足底（底面）
        {"z": -1.22, "cx": -0.075, "cy": -0.005, "rx": 0.048, "ry": 0.070},
    ]
    
    leg_rings = []
    # 8角形ループ（脚の断面）
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
            
    # 脚の底面を塞ぐ
    bot_ring = leg_rings[-1]
    # 四角面2つで塞ぐ (8角形 -> 4角形2つ + 4角形1つ)
    bm.faces.new([bot_ring[0], bot_ring[1], bot_ring[6], bot_ring[7]])
    bm.faces.new([bot_ring[1], bot_ring[2], bot_ring[5], bot_ring[6]])
    bm.faces.new([bot_ring[2], bot_ring[3], bot_ring[4], bot_ring[5]])

    # トルソーの底面（股下）を閉じる
    torso_bot = rings[-1]
    # 7頂点の半円底面を四角面で閉じる
    bm.faces.new([torso_bot[0], torso_bot[1], torso_bot[5], torso_bot[6]])
    bm.faces.new([torso_bot[1], torso_bot[2], torso_bot[4], torso_bot[5]])
    bm.faces.new([torso_bot[2], torso_bot[3], torso_bot[4]])

    # --- 脚の生成（股下から下へ） ---
    leg_levels = [
        # 太もも付け根
        {"z": -0.74, "cx": -0.075, "cy": 0.020, "rx": 0.065, "ry": 0.065},
        # 太もも中央
        {"z": -0.84, "cx": -0.075, "cy": 0.015, "rx": 0.060, "ry": 0.060},
        # 膝
        {"z": -0.94, "cx": -0.075, "cy": 0.010, "rx": 0.052, "ry": 0.052},
        # ふくらはぎ
        {"z": -1.04, "cx": -0.075, "cy": 0.012, "rx": 0.055, "ry": 0.055},
        # 足首
        {"z": -1.14, "cx": -0.075, "cy": 0.010, "rx": 0.045, "ry": 0.045},
        # 足底（底面）
        {"z": -1.22, "cx": -0.075, "cy": -0.005, "rx": 0.048, "ry": 0.070},
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
            
    # 脚の上端と下端を閉じる
    top_leg = leg_rings[0]
    bm.faces.new([top_leg[0], top_leg[7], top_leg[2], top_leg[1]])
    bm.faces.new([top_leg[7], top_leg[6], top_leg[3], top_leg[2]])
    bm.faces.new([top_leg[6], top_leg[5], top_leg[4], top_leg[3]])
    
    bot_leg = leg_rings[-1]
    bm.faces.new([bot_leg[0], bot_leg[1], bot_leg[6], bot_leg[7]])
    bm.faces.new([bot_leg[1], bot_leg[2], bot_leg[5], bot_leg[6]])
    bm.faces.new([bot_leg[2], bot_leg[3], bot_leg[4], bot_leg[5]])

    # --- 腕の生成（肩から横へ、Tポーズ） ---
    arm_levels = [
        # 肩付け根
        {"x": -0.13, "cy": 0.000, "cz": -0.42, "ry": 0.055, "rz": 0.055},
        # 上腕中央
        {"x": -0.23, "cy": 0.000, "cz": -0.43, "ry": 0.048, "rz": 0.048},
        # 肘
        {"x": -0.33, "cy": 0.000, "cz": -0.44, "ry": 0.042, "rz": 0.042},
        # 前腕
        {"x": -0.43, "cy": 0.000, "cz": -0.44, "ry": 0.038, "rz": 0.038},
        # 手首
        {"x": -0.50, "cy": 0.000, "cz": -0.44, "ry": 0.035, "rz": 0.035},
        # 手・手のひら（デフォルメのかわいいミトン調）
        {"x": -0.57, "cy": 0.000, "cz": -0.445, "ry": 0.038, "rz": 0.025},
        # 指先
        {"x": -0.62, "cy": -0.005, "cz": -0.445, "ry": 0.025, "rz": 0.015},
    ]
    
    arm_rings = []
    arm_angles = [0, 45, 90, 135, 180, 225, 270, 315]
    for lev in arm_levels:
        ar = []
        for deg in arm_angles:
            rad = math.radians(deg)
            x = lev["x"]
            y = lev["cy"] + lev["ry"] * math.cos(rad)
            z = lev["cz"] + lev["rz"] * math.sin(rad)
            ar.append(bm.verts.new(Vector((x, y, z))))
        arm_rings.append(ar)
        
    for i in range(len(arm_rings) - 1):
        r1 = arm_rings[i]
        r2 = arm_rings[i+1]
        n = len(r1)
        for j in range(n):
            bm.faces.new([r1[j], r1[(j+1)%n], r2[(j+1)%n], r2[j]])
            
    # 肩付け根と手先を閉じる
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
    
    # マテリアル設定（肌 + 下半身タイツ）
    obj.data.materials.append(materials["M_Skin"])
    obj.data.materials.append(materials["M_Tights_Black"])
    
    # 脚部分のポリゴンにタイツマテリアルを割り当て
    for poly in mesh.polygons:
        # Z座標が -0.78 以下の面はタイツ
        center_z = sum(mesh.vertices[v].co.z for v in poly.vertices) / len(poly.vertices)
        if center_z < -0.76:
            poly.material_index = 1
            
    add_mirror_and_subsurf(obj, use_subsurf=True, subsurf_level=1)
    set_smooth_shading(mesh)
    return obj

# ==============================================================================
# 3. プリーツスカート（Outfit_Skirt）の生成
# ==============================================================================
def create_skirt_mesh(materials):
    """
    ウエスト（Z=-0.56）から裾（Z=-0.94）へ広がるフレアプリーツスカート。
    しっかりとした山・谷のプリーツ折り目を成形し、シックなチャコールグレー＋金縁。
    """
    mesh = bpy.data.meshes.new("Outfit_Skirt_Mesh")
    obj = bpy.data.objects.new("Outfit_Skirt", mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    num_half = 16 # 16分割（全周32分割でより細かなプリーツ）
    levels = [
        {"z": -0.56, "rx": 0.138, "ry": 0.108, "cy": 0.005, "pleat_depth": 0.004},
        {"z": -0.63, "rx": 0.160, "ry": 0.128, "cy": 0.010, "pleat_depth": 0.008},
        {"z": -0.73, "rx": 0.198, "ry": 0.162, "cy": 0.012, "pleat_depth": 0.015},
        {"z": -0.84, "rx": 0.245, "ry": 0.205, "cy": 0.015, "pleat_depth": 0.022},
        {"z": -0.93, "rx": 0.285, "ry": 0.240, "cy": 0.015, "pleat_depth": 0.025},
        {"z": -0.95, "rx": 0.282, "ry": 0.237, "cy": 0.015, "pleat_depth": 0.023},
    ]
    
    skirt_rings = []
    for lev in levels:
        sr = []
        for i in range(num_half + 1):
            t = i / num_half
            deg = t * 180.0
            rad = math.radians(deg)
            # はっきりとしたアコーディオンプリーツ
            pleat = lev["pleat_depth"] if (i % 2 == 1) else -lev["pleat_depth"]
            if i == 0 or i == num_half:
                pleat = 0.0
                
            rx = lev["rx"] + pleat
            ry = lev["ry"] + pleat
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
    obj.data.materials.append(materials["M_Gold_Trim"])
    
    for poly in mesh.polygons:
        center_z = sum(mesh.vertices[v].co.z for v in poly.vertices) / len(poly.vertices)
        if -0.95 <= center_z <= -0.89:
            poly.material_index = 1
            
    mod_solid = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod_solid.thickness = 0.005
    mod_solid.offset = 0.0
    
    add_mirror_and_subsurf(obj, use_subsurf=True, subsurf_level=1)
    set_smooth_shading(mesh)
    return obj

# ==============================================================================
# 4. ドロワーズ（Outfit_Drawers / 貫通防止インナー）
# ==============================================================================
def create_drawers_mesh(materials):
    mesh = bpy.data.meshes.new("Outfit_Drawers_Mesh")
    obj = bpy.data.objects.new("Outfit_Drawers", mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    levels = [
        {"z": -0.57, "rx": 0.130, "ry": 0.100, "cy": 0.005},
        {"z": -0.66, "rx": 0.155, "ry": 0.125, "cy": 0.015},
        {"z": -0.76, "rx": 0.165, "ry": 0.140, "cy": 0.020},
        {"z": -0.83, "rx": 0.140, "ry": 0.120, "cy": 0.015},
    ]
    num_half = 8
    rings = []
    for lev in levels:
        r = []
        for i in range(num_half + 1):
            deg = (i / num_half) * 180.0
            rad = math.radians(deg)
            x = -lev["rx"] * math.sin(rad)
            y = lev["cy"] - lev["ry"] * math.cos(rad)
            z = lev["z"]
            if i == 0 or i == num_half:
                x = 0.0
            r.append(bm.verts.new(Vector((x, y, z))))
        rings.append(r)
        
    for i in range(len(rings) - 1):
        r1 = rings[i]
        r2 = rings[i+1]
        for j in range(num_half):
            bm.faces.new([r1[j], r1[j+1], r2[j+1], r2[j]])
            
    bm.to_mesh(mesh)
    bm.free()
    
    obj.data.materials.append(materials["M_Drawers_White"])
    add_mirror_and_subsurf(obj, use_subsurf=True, subsurf_level=1)
    set_smooth_shading(mesh)
    return obj

# ==============================================================================
# 5. トップス（ベスト & シャツ）
# ==============================================================================
def create_top_mesh(materials):
    mesh = bpy.data.meshes.new("Outfit_Top_Mesh")
    obj = bpy.data.objects.new("Outfit_Top", mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    # 立ち襟＆シャツ襟（首元 Z=-0.3076 にぴったり接合）
    collar_levels = [
        {"z": -0.3076, "rx": 0.100, "ry": 0.100, "cy": 0.007},
        {"z": -0.3400, "rx": 0.108, "ry": 0.105, "cy": 0.006},
    ]
    c_rings = []
    for lev in collar_levels:
        cr = []
        for i in range(7):
            deg = (i / 6) * 180.0
            rad = math.radians(deg)
            x = -lev["rx"] * math.sin(rad)
            y = lev["cy"] - lev["ry"] * math.cos(rad)
            z = lev["z"]
            if i == 0 or i == 6:
                x = 0.0
            cr.append(bm.verts.new(Vector((x, y, z))))
        c_rings.append(cr)
    for j in range(6):
        bm.faces.new([c_rings[0][j], c_rings[0][j+1], c_rings[1][j+1], c_rings[1][j]])

    # ベスト本体
    vest_levels = [
        {"z": -0.35, "rx": 0.115, "ry": 0.106, "cy": 0.005},
        {"z": -0.39, "rx": 0.135, "ry": 0.112, "cy": 0.002},
        {"z": -0.44, "rx": 0.158, "ry": 0.125, "cy": -0.010},
        {"z": -0.50, "rx": 0.152, "ry": 0.118, "cy": -0.005},
        {"z": -0.57, "rx": 0.135, "ry": 0.104, "cy": 0.005},
        {"z": -0.62, "rx": 0.145, "ry": 0.112, "cy": 0.008},
    ]
    
    num_half = 7
    v_rings = []
    for idx, lev in enumerate(vest_levels):
        r = []
        for i in range(num_half):
            deg = (i / (num_half - 1)) * 180.0
            rad = math.radians(deg)
            x = -lev["rx"] * math.sin(rad)
            y = lev["cy"] - lev["ry"] * math.cos(rad)
            z = lev["z"]
            
            # Vネックの開き
            if i == 0 and idx <= 2:
                x = -0.030
            elif i == 0:
                x = 0.0
            elif i == num_half - 1:
                x = 0.0
                
            r.append(bm.verts.new(Vector((x, y, z))))
        v_rings.append(r)
        
    for i in range(len(v_rings) - 1):
        r1 = v_rings[i]
        r2 = v_rings[i+1]
        for j in range(num_half - 1):
            bm.faces.new([r1[j], r1[j+1], r2[j+1], r2[j]])
            
    # 白シャツの胸元（Vネック内部インナー）
    shirt_inner = [
        bm.verts.new(Vector((0.0, -0.098, -0.34))),
        bm.verts.new(Vector((-0.030, -0.102, -0.39))),
        bm.verts.new(Vector((-0.030, -0.115, -0.44))),
        bm.verts.new(Vector((0.0, -0.120, -0.47))),
    ]
    bm.faces.new([shirt_inner[0], shirt_inner[1], shirt_inner[2], shirt_inner[3]])
    
    # 襟の折り返し（翼襟）
    lapel1 = bm.verts.new(Vector((-0.050, -0.110, -0.36)))
    bm.faces.new([shirt_inner[0], lapel1, shirt_inner[1]])

    # パフスリーブ（ふんわりした袖）
    sleeve_levels = [
        {"x": -0.15, "cy": 0.000, "cz": -0.42, "ry": 0.065, "rz": 0.065},
        {"x": -0.25, "cy": 0.000, "cz": -0.43, "ry": 0.078, "rz": 0.078},
        {"x": -0.36, "cy": 0.000, "cz": -0.44, "ry": 0.072, "rz": 0.072},
        {"x": -0.46, "cy": 0.000, "cz": -0.44, "ry": 0.052, "rz": 0.052},
        {"x": -0.49, "cy": 0.000, "cz": -0.44, "ry": 0.042, "rz": 0.042},
    ]
    s_rings = []
    for lev in sleeve_levels:
        sr = []
        for deg in [0, 45, 90, 135, 180, 225, 270, 315]:
            rad = math.radians(deg)
            x = lev["x"]
            y = lev["cy"] + lev["ry"] * math.cos(rad)
            z = lev["cz"] + lev["rz"] * math.sin(rad)
            sr.append(bm.verts.new(Vector((x, y, z))))
        s_rings.append(sr)
        
    for i in range(len(s_rings) - 1):
        r1 = s_rings[i]
        r2 = s_rings[i+1]
        n = len(r1)
        for j in range(n):
            bm.faces.new([r1[j], r1[(j+1)%n], r2[(j+1)%n], r2[j]])

    bm.to_mesh(mesh)
    bm.free()
    
    obj.data.materials.append(materials["M_Vest_Charcoal"])
    obj.data.materials.append(materials["M_Shirt_White"])
    obj.data.materials.append(materials["M_Gold_Trim"])
    
    for poly in mesh.polygons:
        pts = [mesh.vertices[v].co for v in poly.vertices]
        avg_x = sum(p.x for p in pts) / len(pts)
        avg_z = sum(p.z for p in pts) / len(pts)
        if avg_x < -0.15 or avg_z > -0.35:
            poly.material_index = 1
            
    mod_solid = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod_solid.thickness = 0.004
    mod_solid.offset = 0.0
    
    add_mirror_and_subsurf(obj, use_subsurf=True, subsurf_level=1)
    set_smooth_shading(mesh)
    return obj

# ==============================================================================
# 6. ショートケープ（Outfit_Cape / 教師用肩羽織り）
# ==============================================================================
def create_cape_mesh(materials):
    """
    肩から胸・背中を包むネイビーのショートケープ。
    首元をコンパクトに整え、フロントの開きを広げてインナーのベスト＆ブローチを見せる。
    """
    mesh = bpy.data.meshes.new("Outfit_Cape_Mesh")
    obj = bpy.data.objects.new("Outfit_Cape", mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    levels = [
        # 首元立ち襟（首の太さにぴったりフィット）
        {"z": -0.295, "rx": 0.098, "ry": 0.098, "cy": 0.007},
        {"z": -0.325, "rx": 0.112, "ry": 0.108, "cy": 0.006},
        {"z": -0.360, "rx": 0.135, "ry": 0.125, "cy": 0.004},
        # 肩
        {"z": -0.410, "rx": 0.185, "ry": 0.155, "cy": 0.000},
        # 腕中間
        {"z": -0.470, "rx": 0.240, "ry": 0.195, "cy": -0.005},
        # ケープ裾
        {"z": -0.520, "rx": 0.275, "ry": 0.225, "cy": -0.005},
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
            
            # フロント前合わせ（V字に開いてブローチとネクタイを露出させる）
            if i == 0 and idx >= 1:
                x = -0.035 - 0.015 * (idx - 1)
            elif i == 0 or i == num_half - 1:
                x = 0.0
            r.append(bm.verts.new(Vector((x, y, z))))
        c_rings.append(r)
        
    for i in range(len(c_rings) - 1):
        r1 = c_rings[i]
        r2 = c_rings[i+1]
        for j in range(num_half - 1):
            bm.faces.new([r1[j], r1[j+1], r2[j+1], r2[j]])
            
    bm.to_mesh(mesh)
    bm.free()
    
    obj.data.materials.append(materials["M_Cape_Navy"])
    obj.data.materials.append(materials["M_Gold_Trim"])
    
    for poly in mesh.polygons:
        avg_z = sum(mesh.vertices[v].co.z for v in poly.vertices) / len(poly.vertices)
        if avg_z < -0.49:
            poly.material_index = 1
            
    mod_solid = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod_solid.thickness = 0.005
    mod_solid.offset = 0.0
    
    add_mirror_and_subsurf(obj, use_subsurf=True, subsurf_level=1)
    set_smooth_shading(mesh)
    return obj

# ==============================================================================
# 7. レザーアンクルブーツ（Outfit_Boots）
# ==============================================================================
def create_boots_mesh(materials):
    """
    ブラウンレザーのアンクルブーツ。
    足首のくびれ、つま先の甲の丸み、ソール＆ヒール、ゴールドバックルベルト。
    """
    mesh = bpy.data.meshes.new("Outfit_Boots_Mesh")
    obj = bpy.data.objects.new("Outfit_Boots", mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    # 足首から靴底までのリング
    levels = [
        # 履き口（Z=-1.02、少しフレア）
        {"z": -1.02, "cx": -0.075, "cy": 0.012, "rx": 0.062, "ry": 0.062},
        # 足首
        {"z": -1.10, "cx": -0.075, "cy": 0.010, "rx": 0.052, "ry": 0.055},
        # 甲・かかと
        {"z": -1.17, "cx": -0.075, "cy": -0.010, "rx": 0.055, "ry": 0.075},
        # ソール上部
        {"z": -1.22, "cx": -0.075, "cy": -0.020, "rx": 0.058, "ry": 0.090},
        # ソール底面（床接地 Z=-1.25）
        {"z": -1.25, "cx": -0.075, "cy": -0.020, "rx": 0.060, "ry": 0.092},
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
            
    # 底面を塞ぐ
    bot = rings[-1]
    bm.faces.new([bot[0], bot[1], bot[6], bot[7]])
    bm.faces.new([bot[1], bot[2], bot[5], bot[6]])
    bm.faces.new([bot[2], bot[3], bot[4], bot[5]])
    
    # 足首のバックルベルト装飾（小リング）
    belt_r = []
    for deg in angles:
        rad = math.radians(deg)
        x = -0.075 + 0.056 * math.sin(rad)
        y = 0.010 + 0.059 * math.cos(rad)
        z = -1.09
        belt_r.append(bm.verts.new(Vector((x, y, z))))
    for deg in angles:
        rad = math.radians(deg)
        x = -0.075 + 0.056 * math.sin(rad)
        y = 0.010 + 0.059 * math.cos(rad)
        z = -1.11
        belt_r.append(bm.verts.new(Vector((x, y, z))))
    for j in range(num_pts):
        bm.faces.new([belt_r[j], belt_r[(j+1)%num_pts], belt_r[num_pts + (j+1)%num_pts], belt_r[num_pts + j]])

    bm.to_mesh(mesh)
    bm.free()
    
    obj.data.materials.append(materials["M_Leather_Brown"])
    obj.data.materials.append(materials["M_Leather_Dark"]) # ソール
    obj.data.materials.append(materials["M_Gold_Trim"])     # 金具
    
    for poly in mesh.polygons:
        avg_z = sum(mesh.vertices[v].co.z for v in poly.vertices) / len(poly.vertices)
        if avg_z < -1.22:
            poly.material_index = 1 # ソール
        elif -1.11 <= avg_z <= -1.09 and len(poly.vertices) == 4:
            poly.material_index = 2 # バックル
            
    mod_solid = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod_solid.thickness = 0.004
    
    add_mirror_and_subsurf(obj, use_subsurf=True, subsurf_level=1)
    set_smooth_shading(mesh)
    return obj

# ==============================================================================
# 8. 装飾小物（ベルト、ポーチ、魔法の巻物、ブローチ）
# ==============================================================================
def create_accessories(materials):
    """
    - 胸元の水色魔法石ブローチ＆リボンタイ
    - ウエストのユーティリティ革ベルト
    - 魔法の巻物ホルダー（羊皮紙スクロール）
    - 小型レザーポーチ
    - ポーション小瓶
    """
    # 1. ブローチ & タイ
    mesh_brooch = bpy.data.meshes.new("Outfit_Brooch_Mesh")
    obj_brooch = bpy.data.objects.new("Outfit_Brooch", mesh_brooch)
    bpy.context.scene.collection.objects.link(obj_brooch)
    
    bm = bmesh.new()
    # 菱形カットの宝石
    gem_verts = [
        bm.verts.new(Vector((0.0, -0.115, -0.355))), # 上
        bm.verts.new(Vector((-0.015, -0.112, -0.370))), # 左
        bm.verts.new(Vector((0.0, -0.115, -0.385))), # 下
        bm.verts.new(Vector((0.015, -0.112, -0.370))), # 右
        bm.verts.new(Vector((0.0, -0.125, -0.370))), # 前頂点
    ]
    bm.faces.new([gem_verts[0], gem_verts[1], gem_verts[4]])
    bm.faces.new([gem_verts[1], gem_verts[2], gem_verts[4]])
    bm.faces.new([gem_verts[2], gem_verts[3], gem_verts[4]])
    bm.faces.new([gem_verts[3], gem_verts[0], gem_verts[4]])
    
    # リボンタイの垂れ
    tie1 = bm.verts.new(Vector((-0.008, -0.110, -0.385)))
    tie2 = bm.verts.new(Vector((-0.025, -0.108, -0.450)))
    tie3 = bm.verts.new(Vector((-0.010, -0.108, -0.455)))
    tie4 = bm.verts.new(Vector((0.0, -0.110, -0.400)))
    bm.faces.new([tie1, tie2, tie3, tie4])
    
    bm.to_mesh(mesh_brooch)
    bm.free()
    obj_brooch.data.materials.append(materials["M_Gem_Cyan"])
    set_smooth_shading(mesh_brooch)
    
    # 2. ウエストベルト & ポーチ
    mesh_belt = bpy.data.meshes.new("Outfit_Belt_Mesh")
    obj_belt = bpy.data.objects.new("Outfit_Belt", mesh_belt)
    bpy.context.scene.collection.objects.link(obj_belt)
    
    bm = bmesh.new()
    # ウエストベルト（斜めがけ風）
    belt_pts = 16
    for i in range(belt_pts):
        deg = (i / belt_pts) * 360.0
        rad = math.radians(deg)
        rx = 0.145
        ry = 0.115
        x = rx * math.sin(rad)
        y = 0.008 - ry * math.cos(rad)
        # 少し斜めに傾ける
        z_top = -0.570 + 0.020 * math.sin(rad)
        z_bot = -0.600 + 0.020 * math.sin(rad)
        v1 = bm.verts.new(Vector((x, y, z_top)))
        v2 = bm.verts.new(Vector((x, y, z_bot)))
        
    bm.verts.ensure_lookup_table()
    for i in range(belt_pts):
        i1 = i * 2
        i2 = i1 + 1
        i3 = ((i + 1) % belt_pts) * 2
        i4 = i3 + 1
        bm.faces.new([bm.verts[i1], bm.verts[i3], bm.verts[i4], bm.verts[i2]])
        
    # 右腰の巻物（シリンダー）
    # 左腰のポーチ（ボックス）
    bmesh.ops.create_cube(bm, size=0.045, matrix=Matrix.Translation(Vector((0.14, 0.02, -0.58))))
    bmesh.ops.create_cube(bm, size=0.035, matrix=Matrix.Translation(Vector((-0.13, 0.03, -0.58))))
    
    bm.to_mesh(mesh_belt)
    bm.free()
    obj_belt.data.materials.append(materials["M_Leather_Dark"])
    obj_belt.data.materials.append(materials["M_Gold_Trim"])
    set_smooth_shading(mesh_belt)
    
    return [obj_brooch, obj_belt]

# ==============================================================================
# 9. 下絵リファレンス配置 & カメラ・ライティング
# ==============================================================================
def setup_scene_references_and_cameras():
    # 既存のカメラ・ライトの整理
    for obj in bpy.data.objects:
        if obj.type in {'CAMERA', 'LIGHT', 'EMPTY'}:
            bpy.data.objects.remove(obj, do_unlink=True)
            
    # 下絵配置（Reference Empty）
    if REF_FRONT.exists():
        empty_front = bpy.data.objects.new("REF_Front", None)
        empty_front.empty_display_type = 'IMAGE'
        img_f = bpy.data.images.load(str(REF_FRONT))
        empty_front.data = img_f
        empty_front.location = (0.0, 0.8, -0.45)
        empty_front.scale = (1.55, 1.55, 1.55)
        bpy.context.scene.collection.objects.link(empty_front)
        
    if REF_SIDE.exists():
        empty_side = bpy.data.objects.new("REF_Side", None)
        empty_side.empty_display_type = 'IMAGE'
        img_s = bpy.data.images.load(str(REF_SIDE))
        empty_side.data = img_s
        empty_side.location = (0.8, 0.0, -0.45)
        empty_side.rotation_euler = (0.0, 0.0, math.radians(90.0))
        empty_side.scale = (1.55, 1.55, 1.55)
        bpy.context.scene.collection.objects.link(empty_side)

    # カメラ配置
    # 1. 正面カメラ
    cam_front_data = bpy.data.cameras.new("CAM_Front")
    cam_front_data.type = 'ORTHO'
    cam_front_data.ortho_scale = 1.7
    cam_front = bpy.data.objects.new("CAM_Front", cam_front_data)
    cam_front.location = (0.0, -3.0, -0.45)
    cam_front.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    bpy.context.scene.collection.objects.link(cam_front)
    
    # 2. 側面カメラ
    cam_side_data = bpy.data.cameras.new("CAM_Side")
    cam_side_data.type = 'ORTHO'
    cam_side_data.ortho_scale = 1.7
    cam_side = bpy.data.objects.new("CAM_Side", cam_side_data)
    cam_side.location = (-3.0, 0.0, -0.45)
    cam_side.rotation_euler = (math.radians(90.0), 0.0, math.radians(-90.0))
    bpy.context.scene.collection.objects.link(cam_side)
    
    # 3. 背面カメラ
    cam_back_data = bpy.data.cameras.new("CAM_Back")
    cam_back_data.type = 'ORTHO'
    cam_back_data.ortho_scale = 1.7
    cam_back = bpy.data.objects.new("CAM_Back", cam_back_data)
    cam_back.location = (0.0, 3.0, -0.45)
    cam_back.rotation_euler = (math.radians(90.0), 0.0, math.radians(180.0))
    bpy.context.scene.collection.objects.link(cam_back)

    # 4. 斜め45度パースカメラ
    cam_p45_data = bpy.data.cameras.new("CAM_Persp45")
    cam_p45_data.lens = 75
    cam_p45 = bpy.data.objects.new("CAM_Persp45", cam_p45_data)
    cam_p45.location = (-2.0, -2.0, 0.1)
    cam_p45.rotation_euler = (math.radians(75.0), 0.0, math.radians(-45.0))
    bpy.context.scene.collection.objects.link(cam_p45)
    
    # ワールド背景（明るいスタジオ背景）
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.75, 0.77, 0.80, 1.0)
        bg_node.inputs["Strength"].default_value = 1.0

    # ライト配置
    # 1. メインサンライト（キーライト）
    light_data = bpy.data.lights.new("Sun_Main", 'SUN')
    light_data.energy = 3.0
    light_obj = bpy.data.objects.new("Sun_Main", light_data)
    light_obj.rotation_euler = (math.radians(50.0), math.radians(15.0), math.radians(-35.0))
    bpy.context.scene.collection.objects.link(light_obj)
    
    # 2. フィルライト（影の黒つぶれ防止）
    fill_data = bpy.data.lights.new("Sun_Fill", 'SUN')
    fill_data.energy = 1.5
    fill_obj = bpy.data.objects.new("Sun_Fill", fill_data)
    fill_obj.rotation_euler = (math.radians(45.0), math.radians(-30.0), math.radians(140.0))
    bpy.context.scene.collection.objects.link(fill_obj)

# ==============================================================================
# 10. メイン実行関数
# ==============================================================================
def main():
    print("=== Step b01: Generating Teacher Body and Outfit ===")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    materials = setup_materials()
    
    # 1. 各メッシュの生成
    print("-> Creating Body Base...")
    body = create_body_mesh(materials)
    
    print("-> Creating Drawers...")
    drawers = create_drawers_mesh(materials)
    
    print("-> Creating Skirt...")
    skirt = create_skirt_mesh(materials)
    
    print("-> Creating Tops (Blouse & Vest)...")
    tops = create_top_mesh(materials)
    
    print("-> Creating Short Cape...")
    cape = create_cape_mesh(materials)
    
    print("-> Creating Boots...")
    boots = create_boots_mesh(materials)
    
    print("-> Creating Accessories (Belt, Brooch, Pouches)...")
    accs = create_accessories(materials)
    
    # 2. カメラとライト・リファレンスのセットアップ
    setup_scene_references_and_cameras()
    
    # 3. 単体blendファイルの保存
    BODY_ONLY_BLEND.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BODY_ONLY_BLEND))
    print(f"[OK] Saved Body & Outfit scene to: {BODY_ONLY_BLEND}")
    
    # 4. 頭部モデルをアペンドして全身プレビューblendを作成
    if HEAD_BLEND.exists():
        print(f"-> Appending head objects from {HEAD_BLEND}...")
        with bpy.data.libraries.load(str(HEAD_BLEND), link=False) as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects if not name.startswith("CAM_") and not name.startswith("REF_") and not name.startswith("ReviewSun")]
            
        for obj in data_to.objects:
            if obj:
                bpy.context.scene.collection.objects.link(obj)
                
        bpy.ops.wm.save_as_mainfile(filepath=str(FULL_PREVIEW_BLEND))
        print(f"[OK] Saved Full Preview scene to: {FULL_PREVIEW_BLEND}")
        
        # レンダリング画像の出力（正面、側面、斜め45度）
        scene = bpy.context.scene
        scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
        scene.render.resolution_x = 1000
        scene.render.resolution_y = 1200
        scene.render.image_settings.file_format = 'PNG'
        
        # 1. ケープあり版（Full Outfit）
        cams = [
            ("teacher_full_front.png", "CAM_Front"),
            ("teacher_full_side.png", "CAM_Side"),
            ("teacher_full_back.png", "CAM_Back"),
            ("teacher_full_a45.png", "CAM_Persp45"),
        ]
        for fname, cname in cams:
            cam_obj = bpy.data.objects.get(cname)
            if cam_obj:
                scene.camera = cam_obj
                out_path = OUT_DIR / fname
                scene.render.filepath = str(out_path)
                bpy.ops.render.render(write_still=True)
                print(f"[RENDER OK] {out_path}")
                
        # 2. ケープ非表示版（ベスト＆ブラウス姿）
        cape_obj = bpy.data.objects.get("Outfit_Cape")
        if cape_obj:
            cape_obj.hide_render = True
            cams_vest = [
                ("teacher_vest_front.png", "CAM_Front"),
                ("teacher_vest_a45.png", "CAM_Persp45"),
            ]
            for fname, cname in cams_vest:
                cam_obj = bpy.data.objects.get(cname)
                if cam_obj:
                    scene.camera = cam_obj
                    out_path = OUT_DIR / fname
                    scene.render.filepath = str(out_path)
                    bpy.ops.render.render(write_still=True)
                    print(f"[RENDER OK (Vest)] {out_path}")

    print("=== Step b01 Completed Successfully! ===")

if __name__ == "__main__":
    main()
