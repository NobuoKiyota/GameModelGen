import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

def create_mesh_object(context, name):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)
    return obj, mesh


def build_telescope_tripod_mesh(context, name="Telescope_Tripod", height=1.0, leg_spread=0.45, seed=0):
    """【三脚部】3本脚、伸縮ロックバックル、三角スプレッダー、丸穴トレイ、センターポスト"""
    obj, mesh = create_mesh_object(context, name)
    bm = bmesh.new()

    # 1. 三脚トップハブ（三叉ヘッド）
    hub_h = 0.06
    hub_r = 0.08
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=12,
        radius1=hub_r, radius2=hub_r * 0.9, depth=hub_h,
        matrix=Matrix.Translation((0, 0, height))
    )

    # 2. センターポスト（中央ロッド）
    post_len = height * 0.45
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=12,
        radius1=0.015, radius2=0.015, depth=post_len,
        matrix=Matrix.Translation((0, 0, height - post_len * 0.5))
    )

    # 3. 3本の2段伸縮レッグ (120度配置)
    leg_len = math.sqrt(height * height + leg_spread * leg_spread)
    tilt_angle = math.atan2(leg_spread, height)

    for i in range(3):
        az_ang = i * (2.0 * math.pi / 3.0)
        
        # レッグの向きマトリクス
        rot_mat = Matrix.Rotation(az_ang, 4, 'Z') @ Matrix.Rotation(tilt_angle, 4, 'Y')
        
        # 上段太レッグ（角丸/2本パイプ）
        up_len = leg_len * 0.55
        up_pos = Matrix.Translation((0, 0, height)) @ Matrix.Rotation(az_ang, 4, 'Z') @ Matrix.Rotation(tilt_angle, 4, 'Y') @ Matrix.Translation((0, 0, -up_len * 0.5))
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=12,
            radius1=0.018, radius2=0.018, depth=up_len,
            matrix=up_pos
        )
        
        # 脚ロックレバー（バックル）
        lock_pos = Matrix.Translation((0, 0, height)) @ Matrix.Rotation(az_ang, 4, 'Z') @ Matrix.Rotation(tilt_angle, 4, 'Y') @ Matrix.Translation((0, 0, -up_len))
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=lock_pos @ Matrix.Diagonal((0.045, 0.035, 0.04, 1.0))
        )
        
        # 下段細レッグ（伸縮ロッド + ゴム足）
        low_len = leg_len * 0.5
        low_pos = Matrix.Translation((0, 0, height)) @ Matrix.Rotation(az_ang, 4, 'Z') @ Matrix.Rotation(tilt_angle, 4, 'Y') @ Matrix.Translation((0, 0, -up_len - low_len * 0.5))
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=12,
            radius1=0.012, radius2=0.012, depth=low_len,
            matrix=low_pos
        )
        # ゴム石突（足先）
        tip_pos = Matrix.Translation((0, 0, height)) @ Matrix.Rotation(az_ang, 4, 'Z') @ Matrix.Rotation(tilt_angle, 4, 'Y') @ Matrix.Translation((0, 0, -leg_len))
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=12,
            radius1=0.014, radius2=0.005, depth=0.03,
            matrix=tip_pos
        )

    # 4. 丸穴付きアイピース・アクセサリトレイ
    tray_z = height * 0.58
    tray_r = leg_spread * 0.42
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=24,
        radius1=tray_r, radius2=tray_r, depth=0.012,
        matrix=Matrix.Translation((0, 0, tray_z))
    )
    # トレイ支えスプレッダー（3本アーム）
    for i in range(3):
        az_ang = i * (2.0 * math.pi / 3.0)
        arm_len = tray_r * 1.05
        arm_pos = Matrix.Translation((0, 0, tray_z)) @ Matrix.Rotation(az_ang, 4, 'Z') @ Matrix.Translation((arm_len * 0.5, 0, -0.008))
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=arm_pos @ Matrix.Diagonal((arm_len, 0.015, 0.008, 1.0))
        )
    # トレイ上に予備アイピース2本を配置
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=12,
        radius1=0.016, radius2=0.014, depth=0.045,
        matrix=Matrix.Translation((tray_r * 0.5, 0.02, tray_z + 0.025))
    )
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=12,
        radius1=0.018, radius2=0.015, depth=0.06,
        matrix=Matrix.Translation((tray_r * 0.35, -0.05, tray_z + 0.032))
    )

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(mesh)
    bm.free()

    return obj


def build_telescope_mount_mesh(context, name="Telescope_Mount", base_z=1.0, seed=0):
    """【架台部】水平360°回転パンベース、フォークアーム、高度微動固定部、オレンジノブ"""
    obj, mesh = create_mesh_object(context, name)
    bm = bmesh.new()

    # 1. 水平パンベース（回転台座）
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=24,
        radius1=0.075, radius2=0.065, depth=0.04,
        matrix=Matrix.Translation((0, 0, 0.02))
    )

    # 2. フォークアーム（片持ち/ヨーク形状）
    fork_h = 0.18
    # アーム支柱
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=Matrix.Translation((0.045, 0, 0.04 + fork_h * 0.45)) @ Matrix.Diagonal((0.04, 0.05, fork_h * 0.9, 1.0))
    )
    # 高度軸受リング（仰角ピボット位置）
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=16,
        radius1=0.035, radius2=0.035, depth=0.05,
        matrix=Matrix.Translation((0, 0, 0.04 + fork_h)) @ Matrix.Rotation(math.pi * 0.5, 4, 'Y')
    )

    # 3. 高度クランプ・オレンジダイヤルノブ
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=12,
        radius1=0.025, radius2=0.022, depth=0.02,
        matrix=Matrix.Translation((0.075, 0, 0.04 + fork_h)) @ Matrix.Rotation(math.pi * 0.5, 4, 'Y')
    )
    # 水平固定オレンジノブ
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=12,
        radius1=0.018, radius2=0.015, depth=0.02,
        matrix=Matrix.Translation((-0.07, 0, 0.02)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
    )

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(mesh)
    bm.free()

    # 原点を三脚ヘッド直上に配置
    obj.location = (0, 0, base_z)
    return obj


def build_telescope_ota_mesh(context, name="Telescope_OTA", tube_len=0.75, aperture_r=0.048, seed=0):
    """【鏡筒部】メインシリンダー、フレア対物フード、オレンジリング、接眼部・天頂プリズム・アイピース、スマホドック、高度微動ロッド"""
    obj, mesh = create_mesh_object(context, name)
    bm = bmesh.new()

    # 鏡筒は Y軸方向（またはZ軸方向）に伸びる構造（原点はマウント取り付け位置）
    # 前方: +Y, 後方: -Y
    front_len = tube_len * 0.65
    rear_len = tube_len * 0.35

    # 1. メイン鏡筒（シルバーアルミ）
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=24,
        radius1=aperture_r, radius2=aperture_r, depth=tube_len,
        matrix=Matrix.Translation((0, (front_len - rear_len) * 0.5, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
    )

    # 2. セレストロン・オレンジアクセントリング
    ring_pos_y = front_len - 0.12
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=24,
        radius1=aperture_r * 1.03, radius2=aperture_r * 1.03, depth=0.012,
        matrix=Matrix.Translation((0, ring_pos_y, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
    )

    # 3. 先太り対物フード (Dew Shield)
    hood_len = 0.14
    hood_pos_y = front_len + hood_len * 0.5 - 0.11
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=24,
        radius1=aperture_r * 1.25, radius2=aperture_r * 1.04, depth=hood_len,
        matrix=Matrix.Translation((0, hood_pos_y, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
    )
    # フード先端の黒リングセル
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=24,
        radius1=aperture_r * 1.26, radius2=aperture_r * 1.26, depth=0.02,
        matrix=Matrix.Translation((0, hood_pos_y + hood_len * 0.5, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
    )
    # 対物ガラスレンズ
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=24,
        radius1=aperture_r * 0.98, radius2=aperture_r * 0.98, depth=0.005,
        matrix=Matrix.Translation((0, front_len - 0.08, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
    )

    # 4. 接眼部 (Focuser Assembly)
    foc_pos_y = -rear_len
    # 黒エンドキャップ
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=24,
        radius1=aperture_r * 1.02, radius2=aperture_r * 0.7, depth=0.05,
        matrix=Matrix.Translation((0, foc_pos_y - 0.025, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
    )
    # ドローチューブ
    tube_r = 0.022
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=16,
        radius1=tube_r, radius2=tube_r, depth=0.08,
        matrix=Matrix.Translation((0, foc_pos_y - 0.08, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
    )
    # フォーカスダイヤルノブ（左右）
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=16,
        radius1=0.022, radius2=0.022, depth=0.09,
        matrix=Matrix.Translation((0, foc_pos_y - 0.05, -tube_r * 1.2)) @ Matrix.Rotation(math.pi * 0.5, 4, 'Y')
    )

    # 5. 90度天頂プリズム (Star Diagonal) & アイピース (Eyepiece)
    diag_pos = Vector((0, foc_pos_y - 0.13, 0))
    # ダイアゴナル本体ボックス
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=Matrix.Translation(diag_pos) @ Matrix.Diagonal((0.042, 0.042, 0.042, 1.0))
    )
    # 上向きアイピース（接眼レンズ）
    ep_h = 0.065
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=16,
        radius1=0.016, radius2=0.018, depth=ep_h,
        matrix=Matrix.Translation((0, foc_pos_y - 0.13, 0.021 + ep_h * 0.5))
    )
    # アイピース上部ラバーアイカップ
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=16,
        radius1=0.022, radius2=0.018, depth=0.015,
        matrix=Matrix.Translation((0, foc_pos_y - 0.13, 0.021 + ep_h))
    )

    # 6. StarSense スマートフォンホルダードック ＆ ファインダー
    dock_pos = Vector((0, 0.08, aperture_r + 0.035))
    # マウント台座
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=Matrix.Translation(dock_pos) @ Matrix.Diagonal((0.055, 0.09, 0.025, 1.0))
    )
    # スマホ固定クランプ（上部の湾曲アーム）
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=Matrix.Translation((0, 0.08, aperture_r + 0.065)) @ Matrix.Diagonal((0.065, 0.045, 0.035, 1.0))
    )
    # ドットサイトファインダースコープ（左側）
    finder_pos = Vector((-aperture_r - 0.025, -0.05, aperture_r * 0.7))
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=12,
        radius1=0.012, radius2=0.012, depth=0.12,
        matrix=Matrix.Translation(finder_pos) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
    )

    # 7. 高度微動調整ロッド (Altitude Slow-Motion Rod)
    rod_len = 0.28
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=8,
        radius1=0.006, radius2=0.006, depth=rod_len,
        matrix=Matrix.Translation((0.04, -0.06, -aperture_r - 0.02)) @ Matrix.Rotation(0.35, 4, 'X') @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
    )
    # オレンジ微動ノブ
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=12,
        radius1=0.014, radius2=0.014, depth=0.02,
        matrix=Matrix.Translation((0.04, -0.18, -aperture_r - 0.06))
    )

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(mesh)
    bm.free()

    return obj


def create_procedural_telescope(context, name="Astronomical_Telescope",
                                elevation_deg=25.0, azimuth_deg=45.0,
                                tripod_height=1.0, tube_length=0.75,
                                seed=0):
    """【完全プロシージャル天体望遠鏡】独立可動パーツ階層（Tripod -> Mount -> OTA）を自動構築"""
    # 1. 三脚の作成
    tripod_obj = build_telescope_tripod_mesh(context, name=f"{name}_Tripod", height=tripod_height, seed=seed)
    
    # 2. 架台（マウント）の作成
    mount_obj = build_telescope_mount_mesh(context, name=f"{name}_Mount", base_z=tripod_height, seed=seed)
    mount_obj.parent = tripod_obj
    mount_obj.rotation_euler.z = math.radians(azimuth_deg)

    # 3. 鏡筒部（OTA）の作成
    ota_obj = build_telescope_ota_mesh(context, name=f"{name}_OTA", tube_len=tube_length, seed=seed)
    # 架台の高度軸位置（フォークアーム上部）に配置
    fork_h = 0.18
    ota_obj.location = (0, 0, 0.04 + fork_h)
    ota_obj.parent = mount_obj
    # 仰角チルト回転（X軸）
    ota_obj.rotation_euler.x = math.radians(-elevation_deg)

    # 4. マテリアルスロットとPBRシェーダーの設定
    from ..materials.nature_shaders import create_procedural_telescope_shader
    mat_silver = create_procedural_telescope_shader(f"{name}_Silver_Mat", "SILVER", seed)
    mat_black = create_procedural_telescope_shader(f"{name}_Black_Mat", "BLACK", seed)
    mat_orange = create_procedural_telescope_shader(f"{name}_Orange_Mat", "ORANGE", seed)
    mat_lens = create_procedural_telescope_shader(f"{name}_Lens_Mat", "LENS", seed)

    tripod_obj.data.materials.append(mat_black)
    mount_obj.data.materials.append(mat_black)
    
    ota_obj.data.materials.append(mat_silver)
    ota_obj.data.materials.append(mat_black)
    ota_obj.data.materials.append(mat_orange)
    ota_obj.data.materials.append(mat_lens)

    # 全体をまとめるルートオブジェクト（親）
    root_obj = bpy.data.objects.new(name, None)
    root_obj.empty_display_type = 'PLAIN_AXES'
    root_obj.empty_display_size = 0.2
    context.collection.objects.link(root_obj)
    tripod_obj.parent = root_obj

    context.view_layer.objects.active = root_obj
    root_obj.select_set(True)

    return root_obj
