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


def build_telescope_tripod_mesh(context, name="Telescope_Tripod", height=1.0, leg_spread=0.45, style="MODERN_REFRACTOR", seed=0):
    """【三脚部】スタイル別プロシージャル三脚（アンティーク真鍮卓上脚 / メタルショート脚 / カーボン三脚 / 3段タクティカル脚 / 2段アルミ脚）"""
    obj, mesh = create_mesh_object(context, name)
    bm = bmesh.new()

    if style == "ANTIQUE_BRASS":
        # 🏛️ アンティーク真鍮・優雅なカーブ卓上3本脚スタンド
        col_h = height * 0.45
        # センターテーパー真鍮コラム
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=0.035, radius2=0.02, depth=col_h,
            matrix=Matrix.Translation((0, 0, height - col_h * 0.5))
        )
        # コラムリング装飾
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=0.042, radius2=0.042, depth=0.015,
            matrix=Matrix.Translation((0, 0, height - col_h * 0.3))
        )
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=0.05, radius2=0.05, depth=0.02,
            matrix=Matrix.Translation((0, 0, height - col_h))
        )
        # 3本の優雅なS字カーブ真鍮脚
        base_z = height - col_h
        for i in range(3):
            az_ang = i * (2.0 * math.pi / 3.0)
            # 弧を描くセグメント
            seg_count = 6
            curve_r = leg_spread * 0.6
            for s in range(seg_count):
                t1 = s / seg_count
                t2 = (s + 1) / seg_count
                r1 = math.sin(t1 * math.pi * 0.5) * curve_r
                z1 = base_z - t1 * base_z
                r2 = math.sin(t2 * math.pi * 0.5) * curve_r
                z2 = base_z - t2 * base_z
                
                mid_r = (r1 + r2) * 0.5
                mid_z = (z1 + z2) * 0.5
                seg_len = math.sqrt((r2 - r1)**2 + (z2 - z1)**2)
                ang_pitch = math.atan2(r2 - r1, z1 - z2)
                
                seg_pos = Matrix.Rotation(az_ang, 4, 'Z') @ Matrix.Translation((mid_r, 0, mid_z)) @ Matrix.Rotation(ang_pitch, 4, 'Y')
                bmesh.ops.create_cube(
                    bm, size=1.0,
                    matrix=seg_pos @ Matrix.Diagonal((0.012, 0.018, seg_len * 1.05, 1.0))
                )

    elif style == "CASSEGRAIN_POP":
        # 🎨 メタルショート卓上3本脚（シルバーロッド ＋ ゴム足）
        hub_h = 0.04
        hub_r = 0.045
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=hub_r, radius2=hub_r * 0.9, depth=hub_h,
            matrix=Matrix.Translation((0, 0, height))
        )
        leg_len = math.sqrt(height * height + leg_spread * leg_spread) * 0.7
        tilt_angle = math.atan2(leg_spread * 0.7, height)
        for i in range(3):
            az_ang = i * (2.0 * math.pi / 3.0)
            l_pos = Matrix.Translation((0, 0, height)) @ Matrix.Rotation(az_ang, 4, 'Z') @ Matrix.Rotation(tilt_angle, 4, 'Y') @ Matrix.Translation((0, 0, -leg_len * 0.5))
            bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=12,
                radius1=0.008, radius2=0.008, depth=leg_len,
                matrix=l_pos
            )
            # ゴムキャップ足先
            tip_pos = Matrix.Translation((0, 0, height)) @ Matrix.Rotation(az_ang, 4, 'Z') @ Matrix.Rotation(tilt_angle, 4, 'Y') @ Matrix.Translation((0, 0, -leg_len))
            bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=12,
                radius1=0.012, radius2=0.008, depth=0.02,
                matrix=tip_pos
            )

    elif style == "SMART_DIGITAL":
        # 🚀 プロフェッショナル・カーボン三脚（太い単一カーボンレッグ ＋ 回転ロック）
        hub_h = 0.06
        hub_r = 0.07
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=hub_r, radius2=hub_r * 0.85, depth=hub_h,
            matrix=Matrix.Translation((0, 0, height))
        )
        leg_len = math.sqrt(height * height + leg_spread * leg_spread)
        tilt_angle = math.atan2(leg_spread, height)
        for i in range(3):
            az_ang = i * (2.0 * math.pi / 3.0)
            # カーボン太脚
            up_len = leg_len * 0.55
            up_pos = Matrix.Translation((0, 0, height)) @ Matrix.Rotation(az_ang, 4, 'Z') @ Matrix.Rotation(tilt_angle, 4, 'Y') @ Matrix.Translation((0, 0, -up_len * 0.5))
            bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=16,
                radius1=0.022, radius2=0.022, depth=up_len,
                matrix=up_pos
            )
            # スタイリッシュなツイストロックリング
            lock_pos = Matrix.Translation((0, 0, height)) @ Matrix.Rotation(az_ang, 4, 'Z') @ Matrix.Rotation(tilt_angle, 4, 'Y') @ Matrix.Translation((0, 0, -up_len))
            bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=16,
                radius1=0.026, radius2=0.026, depth=0.035,
                matrix=lock_pos
            )
            # 下段カーボン脚
            low_len = leg_len * 0.5
            low_pos = Matrix.Translation((0, 0, height)) @ Matrix.Rotation(az_ang, 4, 'Z') @ Matrix.Rotation(tilt_angle, 4, 'Y') @ Matrix.Translation((0, 0, -up_len - low_len * 0.5))
            bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=16,
                radius1=0.016, radius2=0.016, depth=low_len,
                matrix=low_pos
            )

    elif style == "TACTICAL_COMPACT":
        # 📸 3段レバーロック太脚三脚 ＋ クランクセンターエレベーター
        hub_h = 0.07
        hub_r = 0.08
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=hub_r, radius2=hub_r * 0.9, depth=hub_h,
            matrix=Matrix.Translation((0, 0, height))
        )
        # センターエレベーターシャフト
        elev_len = height * 0.5
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=0.018, radius2=0.018, depth=elev_len,
            matrix=Matrix.Translation((0, 0, height - elev_len * 0.4))
        )
        # クランクハンドル
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.Translation((hub_r + 0.02, 0, height - 0.02)) @ Matrix.Diagonal((0.04, 0.015, 0.015, 1.0))
        )
        # 3段伸縮脚
        leg_len = math.sqrt(height * height + leg_spread * leg_spread)
        tilt_angle = math.atan2(leg_spread, height)
        for i in range(3):
            az_ang = i * (2.0 * math.pi / 3.0)
            # 3段パイプ
            for tier in range(3):
                t_len = leg_len * 0.36
                t_r = 0.020 - tier * 0.004
                offset_z = -t_len * (tier + 0.5)
                p_pos = Matrix.Translation((0, 0, height)) @ Matrix.Rotation(az_ang, 4, 'Z') @ Matrix.Rotation(tilt_angle, 4, 'Y') @ Matrix.Translation((0, 0, offset_z))
                bmesh.ops.create_cone(
                    bm, cap_ends=True, cap_tris=False, segments=12,
                    radius1=t_r, radius2=t_r, depth=t_len,
                    matrix=p_pos
                )
                # レバーロック
                if tier < 2:
                    l_pos = Matrix.Translation((0, 0, height)) @ Matrix.Rotation(az_ang, 4, 'Z') @ Matrix.Rotation(tilt_angle, 4, 'Y') @ Matrix.Translation((0, 0, -t_len * (tier + 1)))
                    bmesh.ops.create_cube(
                        bm, size=1.0,
                        matrix=l_pos @ Matrix.Diagonal((0.045, 0.035, 0.03, 1.0))
                    )

    else:
        # 🔭 MODERN_REFRACTOR (標準型2段アルミ脚 ＋ 丸穴アイピーストレイ)
        hub_h = 0.06
        hub_r = 0.08
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=12,
            radius1=hub_r, radius2=hub_r * 0.9, depth=hub_h,
            matrix=Matrix.Translation((0, 0, height))
        )
        post_len = height * 0.45
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=12,
            radius1=0.015, radius2=0.015, depth=post_len,
            matrix=Matrix.Translation((0, 0, height - post_len * 0.5))
        )
        leg_len = math.sqrt(height * height + leg_spread * leg_spread)
        tilt_angle = math.atan2(leg_spread, height)
        for i in range(3):
            az_ang = i * (2.0 * math.pi / 3.0)
            up_len = leg_len * 0.55
            up_pos = Matrix.Translation((0, 0, height)) @ Matrix.Rotation(az_ang, 4, 'Z') @ Matrix.Rotation(tilt_angle, 4, 'Y') @ Matrix.Translation((0, 0, -up_len * 0.5))
            bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=12,
                radius1=0.018, radius2=0.018, depth=up_len,
                matrix=up_pos
            )
            lock_pos = Matrix.Translation((0, 0, height)) @ Matrix.Rotation(az_ang, 4, 'Z') @ Matrix.Rotation(tilt_angle, 4, 'Y') @ Matrix.Translation((0, 0, -up_len))
            bmesh.ops.create_cube(
                bm, size=1.0,
                matrix=lock_pos @ Matrix.Diagonal((0.045, 0.035, 0.04, 1.0))
            )
            low_len = leg_len * 0.5
            low_pos = Matrix.Translation((0, 0, height)) @ Matrix.Rotation(az_ang, 4, 'Z') @ Matrix.Rotation(tilt_angle, 4, 'Y') @ Matrix.Translation((0, 0, -up_len - low_len * 0.5))
            bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=12,
                radius1=0.012, radius2=0.012, depth=low_len,
                matrix=low_pos
            )
        # 丸穴付きトレイ
        tray_z = height * 0.58
        tray_r = leg_spread * 0.42
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=tray_r, radius2=tray_r, depth=0.012,
            matrix=Matrix.Translation((0, 0, tray_z))
        )
        for i in range(3):
            az_ang = i * (2.0 * math.pi / 3.0)
            arm_len = tray_r * 1.05
            arm_pos = Matrix.Translation((0, 0, tray_z)) @ Matrix.Rotation(az_ang, 4, 'Z') @ Matrix.Translation((arm_len * 0.5, 0, -0.008))
            bmesh.ops.create_cube(
                bm, size=1.0,
                matrix=arm_pos @ Matrix.Diagonal((arm_len, 0.015, 0.008, 1.0))
            )

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(mesh)
    bm.free()

    return obj


def build_telescope_mount_mesh(context, name="Telescope_Mount", base_z=1.0, style="MODERN_REFRACTOR", seed=0):
    """【架台部】スタイル別架台（半円コドラント真鍮ギア / 片持ちモーターフォーク / ボール自由雲台 / 3ウェイパン雲台 / ヨークマウント）"""
    obj, mesh = create_mesh_object(context, name)
    bm = bmesh.new()

    if style == "ANTIQUE_BRASS":
        # 🏛️ 半円コドラント（扇形刻印ギア）高度マウント ＋ 真鍮固定ネジ
        # 台座ピボット
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=0.035, radius2=0.035, depth=0.05,
            matrix=Matrix.Translation((0, 0, 0.025))
        )
        # 扇形（半円）コドラントスケール
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=0.065, radius2=0.065, depth=0.012,
            matrix=Matrix.Translation((0, 0, 0.09)) @ Matrix.Rotation(math.pi * 0.5, 4, 'Y')
        )
        # 真鍮クランプノブ
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=12,
            radius1=0.016, radius2=0.016, depth=0.03,
            matrix=Matrix.Translation((0.03, 0, 0.09)) @ Matrix.Rotation(math.pi * 0.5, 4, 'Y')
        )

    elif style == "SMART_DIGITAL":
        # 🚀 片持ちモーター駆動フォークマウント ＋ LED電源ボタン
        fork_h = 0.22
        # ベース回転円盤
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=0.07, radius2=0.065, depth=0.03,
            matrix=Matrix.Translation((0, 0, 0.015))
        )
        # スタイリッシュな片持ちフォークアーム
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.Translation((0.05, 0, 0.03 + fork_h * 0.5)) @ Matrix.Diagonal((0.045, 0.08, fork_h, 1.0))
        )
        # 丸型LEDリング電源ボタン（正面）
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=0.014, radius2=0.014, depth=0.008,
            matrix=Matrix.Translation((0.05, -0.042, 0.03 + fork_h * 0.35)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
        )

    elif style == "CASSEGRAIN_POP":
        # 🎨 ボール自由雲台（ボールヘッド ＋ パン固定レバー）
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=0.035, radius2=0.032, depth=0.03,
            matrix=Matrix.Translation((0, 0, 0.015))
        )
        # ボール球体
        bmesh.ops.create_icosphere(
            bm, subdivisions=2, radius=0.022,
            matrix=Matrix.Translation((0, 0, 0.045))
        )
        # 固定ウィングノブ
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.Translation((0.035, 0, 0.025)) @ Matrix.Diagonal((0.03, 0.012, 0.012, 1.0))
        )

    elif style == "TACTICAL_COMPACT":
        # 📸 3ウェイ雲台（チルトパンハンドル ＋ 水平パンハンドル）
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=0.045, radius2=0.04, depth=0.035,
            matrix=Matrix.Translation((0, 0, 0.018))
        )
        # クイックシューベースプレート
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.Translation((0, 0, 0.065)) @ Matrix.Diagonal((0.06, 0.06, 0.02, 1.0))
        )
        # 長いパンハンドル（後方へ伸びる棒）
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=12,
            radius1=0.008, radius2=0.008, depth=0.18,
            matrix=Matrix.Translation((0, -0.10, 0.05)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
        )
        # パンハンドル握りグリップ
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=12,
            radius1=0.014, radius2=0.012, depth=0.07,
            matrix=Matrix.Translation((0, -0.16, 0.05)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
        )

    else:
        # 🔭 MODERN_REFRACTOR (ヨーク片持ちマウント ＋ オレンジノブ)
        fork_h = 0.18
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=0.075, radius2=0.065, depth=0.04,
            matrix=Matrix.Translation((0, 0, 0.02))
        )
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.Translation((0.045, 0, 0.04 + fork_h * 0.45)) @ Matrix.Diagonal((0.04, 0.05, fork_h * 0.9, 1.0))
        )
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=0.035, radius2=0.035, depth=0.05,
            matrix=Matrix.Translation((0, 0, 0.04 + fork_h)) @ Matrix.Rotation(math.pi * 0.5, 4, 'Y')
        )
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=12,
            radius1=0.025, radius2=0.022, depth=0.02,
            matrix=Matrix.Translation((0.075, 0, 0.04 + fork_h)) @ Matrix.Rotation(math.pi * 0.5, 4, 'Y')
        )

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(mesh)
    bm.free()

    obj.location = (0, 0, base_z)
    return obj


def build_telescope_ota_mesh(context, name="Telescope_OTA", tube_len=0.75, aperture_r=0.048, style="MODERN_REFRACTOR", seed=0):
    """【鏡筒部】スタイル別鏡筒（真鍮クラシック / スマートシリンダー / カセグレン太短 / タクティカル溝フード / 近代屈折式）"""
    obj, mesh = create_mesh_object(context, name)
    bm = bmesh.new()

    if style == "ANTIQUE_BRASS":
        # 🏛️ アンティーク真鍮シリンダー ＋ 2本リング並列真鍮ファインダー ＋ 直視型真鍮アイピース
        front_len = tube_len * 0.6
        rear_len = tube_len * 0.4
        # メイン真鍮鏡筒
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=aperture_r, radius2=aperture_r, depth=tube_len,
            matrix=Matrix.Translation((0, (front_len - rear_len) * 0.5, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
        )
        # 真鍮フード＆装飾リング
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=aperture_r * 1.08, radius2=aperture_r * 1.08, depth=0.12,
            matrix=Matrix.Translation((0, front_len - 0.06, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
        )
        # 並列真鍮ファインダースコープ（上部）
        finder_len = tube_len * 0.45
        f_pos = Vector((0, 0, aperture_r + 0.045))
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=0.016, radius2=0.016, depth=finder_len,
            matrix=Matrix.Translation(f_pos) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
        )
        # ファインダー支持リング2本
        for offset_y in (-finder_len * 0.25, finder_len * 0.25):
            bmesh.ops.create_cube(
                bm, size=1.0,
                matrix=Matrix.Translation((0, offset_y, aperture_r + 0.022)) @ Matrix.Diagonal((0.008, 0.015, 0.045, 1.0))
            )
        # 後端ドローチューブ＆真鍮アイピース（直視式）
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=aperture_r * 0.65, radius2=aperture_r * 0.65, depth=0.18,
            matrix=Matrix.Translation((0, -rear_len - 0.09, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
        )
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=aperture_r * 0.75, radius2=aperture_r * 0.5, depth=0.03,
            matrix=Matrix.Translation((0, -rear_len - 0.19, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
        )

    elif style == "SMART_DIGITAL":
        # 🚀 未来派ツートーンシリンダー ＋ 前面十字スパイダーフレーム ＋ センサードーム
        s_len = tube_len * 0.65
        s_r = aperture_r * 1.3
        front_len = s_len * 0.6
        rear_len = s_len * 0.4
        # ミニマル鏡筒
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=32,
            radius1=s_r, radius2=s_r, depth=s_len,
            matrix=Matrix.Translation((0, (front_len - rear_len) * 0.5, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
        )
        # 前面十字スパイダーフレーム
        f_y = front_len
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.Translation((0, f_y, 0)) @ Matrix.Diagonal((s_r * 1.9, 0.01, 0.008, 1.0))
        )
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.Translation((0, f_y, 0)) @ Matrix.Diagonal((0.008, 0.01, s_r * 1.9, 1.0))
        )
        # 中央副鏡/センサーセル
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=s_r * 0.32, radius2=s_r * 0.32, depth=0.015,
            matrix=Matrix.Translation((0, f_y, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
        )

    elif style == "CASSEGRAIN_POP":
        # 🎨 マクストフ・カセグレン太短鏡筒 ＋ 前面補正板＆副鏡マーク ＋ 直角アイピース
        c_len = tube_len * 0.48
        c_r = aperture_r * 1.45
        front_len = c_len * 0.55
        rear_len = c_len * 0.45
        # 丸みを帯びたポップな太短鏡筒
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=c_r, radius2=c_r, depth=c_len,
            matrix=Matrix.Translation((0, (front_len - rear_len) * 0.5, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
        )
        # 前面ガラス補正板
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=c_r * 0.95, radius2=c_r * 0.95, depth=0.006,
            matrix=Matrix.Translation((0, front_len - 0.01, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
        )
        # 中央副鏡シルバー丸マーク
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=c_r * 0.35, radius2=c_r * 0.35, depth=0.008,
            matrix=Matrix.Translation((0, front_len - 0.008, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
        )
        # 後端直角アイピース
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.Translation((0, -rear_len - 0.03, 0)) @ Matrix.Diagonal((0.045, 0.045, 0.045, 1.0))
        )
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=0.018, radius2=0.02, depth=0.05,
            matrix=Matrix.Translation((0, -rear_len - 0.03, 0.045))
        )

    elif style == "TACTICAL_COMPACT":
        # 📸 タクティカル太鏡筒 ＋ ローレット溝フード ＋ クレイフォードフォーカサー
        t_len = tube_len * 0.6
        t_r = aperture_r * 1.15
        front_len = t_len * 0.6
        rear_len = t_len * 0.4
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=t_r, radius2=t_r, depth=t_len,
            matrix=Matrix.Translation((0, (front_len - rear_len) * 0.5, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
        )
        # ローレット（滑り止め溝）フード
        hood_len = 0.12
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=t_r * 1.12, radius2=t_r * 1.12, depth=hood_len,
            matrix=Matrix.Translation((0, front_len - hood_len * 0.5, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
        )
        # 大径デュアルスピードフォーカスダイヤル
        foc_y = -rear_len - 0.04
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=0.028, radius2=0.028, depth=0.11,
            matrix=Matrix.Translation((0, foc_y, -t_r * 0.9)) @ Matrix.Rotation(math.pi * 0.5, 4, 'Y')
        )
        # 90度天頂ミラー ＆ 太口径アイピース
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.Translation((0, foc_y - 0.05, 0)) @ Matrix.Diagonal((0.05, 0.05, 0.05, 1.0))
        )
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=0.022, radius2=0.025, depth=0.06,
            matrix=Matrix.Translation((0, foc_y - 0.05, 0.05))
        )

    else:
        # 🔭 MODERN_REFRACTOR (王道先太りフード ＋ オレンジリング ＋ スマホドック)
        front_len = tube_len * 0.65
        rear_len = tube_len * 0.35
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=aperture_r, radius2=aperture_r, depth=tube_len,
            matrix=Matrix.Translation((0, (front_len - rear_len) * 0.5, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
        )
        ring_pos_y = front_len - 0.12
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=aperture_r * 1.03, radius2=aperture_r * 1.03, depth=0.012,
            matrix=Matrix.Translation((0, ring_pos_y, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
        )
        hood_len = 0.14
        hood_pos_y = front_len + hood_len * 0.5 - 0.11
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=aperture_r * 1.25, radius2=aperture_r * 1.04, depth=hood_len,
            matrix=Matrix.Translation((0, hood_pos_y, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
        )
        foc_pos_y = -rear_len
        tube_r = 0.022
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=tube_r, radius2=tube_r, depth=0.08,
            matrix=Matrix.Translation((0, foc_pos_y - 0.08, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
        )
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=0.022, radius2=0.022, depth=0.09,
            matrix=Matrix.Translation((0, foc_pos_y - 0.05, -tube_r * 1.2)) @ Matrix.Rotation(math.pi * 0.5, 4, 'Y')
        )
        diag_pos = Vector((0, foc_pos_y - 0.13, 0))
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.Translation(diag_pos) @ Matrix.Diagonal((0.042, 0.042, 0.042, 1.0))
        )
        ep_h = 0.065
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=0.016, radius2=0.018, depth=ep_h,
            matrix=Matrix.Translation((0, foc_pos_y - 0.13, 0.021 + ep_h * 0.5))
        )
        dock_pos = Vector((0, 0.08, aperture_r + 0.035))
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.Translation(dock_pos) @ Matrix.Diagonal((0.055, 0.09, 0.025, 1.0))
        )
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.Translation((0, 0.08, aperture_r + 0.065)) @ Matrix.Diagonal((0.065, 0.045, 0.035, 1.0))
        )

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(mesh)
    bm.free()

    return obj


def create_procedural_telescope(context, name="Astronomical_Telescope",
                                style="MODERN_REFRACTOR",
                                elevation_deg=25.0, azimuth_deg=45.0,
                                tripod_height=1.0, tube_length=0.75,
                                seed=0):
    """【完全プロシージャル天体望遠鏡】5大スタイル独立可動パーツ階層（Tripod -> Mount -> OTA）を自動構築"""
    from ..materials.nature_shaders import create_procedural_telescope_shader

    # 1. 三脚の作成
    t_height = 0.45 if style in ("ANTIQUE_BRASS", "CASSEGRAIN_POP") and tripod_height > 0.8 else tripod_height
    tripod_obj = build_telescope_tripod_mesh(context, name=f"{name}_Tripod", height=t_height, style=style, seed=seed)
    
    # 2. 架台（マウント）の作成
    mount_obj = build_telescope_mount_mesh(context, name=f"{name}_Mount", base_z=t_height, style=style, seed=seed)
    mount_obj.parent = tripod_obj
    mount_obj.rotation_euler.z = math.radians(azimuth_deg)

    # 3. 鏡筒部（OTA）の作成
    ota_obj = build_telescope_ota_mesh(context, name=f"{name}_OTA", tube_len=tube_length, style=style, seed=seed)
    
    # 架台に応じた高度ピボットオフセット
    fork_h = 0.09 if style == "ANTIQUE_BRASS" else (0.22 if style == "SMART_DIGITAL" else (0.05 if style in ("CASSEGRAIN_POP", "TACTICAL_COMPACT") else 0.18))
    ota_obj.location = (0, 0, fork_h)
    ota_obj.parent = mount_obj
    ota_obj.rotation_euler.x = math.radians(-elevation_deg)

    # 4. スタイル別 PBR マテリアルの割り当て
    if style == "ANTIQUE_BRASS":
        mat_brass = create_procedural_telescope_shader(f"{name}_Brass_Mat", "BRASS", seed)
        mat_lens = create_procedural_telescope_shader(f"{name}_Lens_Mat", "LENS", seed)
        tripod_obj.data.materials.append(mat_brass)
        mount_obj.data.materials.append(mat_brass)
        ota_obj.data.materials.append(mat_brass)
        ota_obj.data.materials.append(mat_lens)

    elif style == "SMART_DIGITAL":
        mat_silver = create_procedural_telescope_shader(f"{name}_Silver_Mat", "SILVER", seed)
        mat_carbon = create_procedural_telescope_shader(f"{name}_Carbon_Mat", "CARBON", seed)
        mat_led = create_procedural_telescope_shader(f"{name}_LED_Mat", "EMISSION_LED", seed)
        mat_lens = create_procedural_telescope_shader(f"{name}_Lens_Mat", "LENS", seed)
        tripod_obj.data.materials.append(mat_carbon)
        mount_obj.data.materials.append(mat_carbon)
        mount_obj.data.materials.append(mat_led)
        ota_obj.data.materials.append(mat_silver)
        ota_obj.data.materials.append(mat_carbon)
        ota_obj.data.materials.append(mat_lens)

    elif style == "CASSEGRAIN_POP":
        mat_teal = create_procedural_telescope_shader(f"{name}_Teal_Mat", "TEAL", seed)
        mat_silver = create_procedural_telescope_shader(f"{name}_Silver_Mat", "SILVER", seed)
        mat_black = create_procedural_telescope_shader(f"{name}_Black_Mat", "BLACK", seed)
        mat_lens = create_procedural_telescope_shader(f"{name}_Lens_Mat", "LENS", seed)
        tripod_obj.data.materials.append(mat_silver)
        mount_obj.data.materials.append(mat_black)
        ota_obj.data.materials.append(mat_teal)
        ota_obj.data.materials.append(mat_silver)
        ota_obj.data.materials.append(mat_lens)

    elif style == "TACTICAL_COMPACT":
        mat_black = create_procedural_telescope_shader(f"{name}_Black_Mat", "BLACK", seed)
        mat_silver = create_procedural_telescope_shader(f"{name}_Silver_Mat", "SILVER", seed)
        mat_lens = create_procedural_telescope_shader(f"{name}_Lens_Mat", "LENS", seed)
        tripod_obj.data.materials.append(mat_black)
        mount_obj.data.materials.append(mat_black)
        ota_obj.data.materials.append(mat_black)
        ota_obj.data.materials.append(mat_silver)
        ota_obj.data.materials.append(mat_lens)

    else: # MODERN_REFRACTOR
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
