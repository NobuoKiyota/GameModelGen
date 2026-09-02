import bpy
import bmesh
import math
import mathutils
import random
import os

from ..materials.nature_shaders import (
    create_procedural_bark_material,
    create_procedural_leaf_material,
    create_procedural_grass_blade_shader,
    create_procedural_ground_terrain_shader,
    create_procedural_water_shader,
    create_procedural_water_bed_shader
)
from ..utils.texture_utils import get_textures_from_folder

# =============================================================
# 1. Grass & Terrain Generators
# =============================================================
def _fbm(x, y, seed, octaves=4, lacunarity=2.0, gain=0.5, base_scale=0.55):
    """Fractional Brownian Motion — sin/cos多層重ね合わせ（image不要）"""
    rng = random.Random(seed)
    offsets = [(rng.uniform(0, 100), rng.uniform(0, 100)) for _ in range(octaves)]
    value = 0.0
    amplitude = 1.0
    frequency = base_scale
    norm = 0.0
    for i in range(octaves):
        ox, oy = offsets[i]
        sx = x * frequency + ox
        sy = y * frequency + oy
        # 2D smooth noise via trig
        n = (math.sin(sx * 1.0) * math.cos(sy * 1.0)
           + math.sin(sx * 2.0 + 1.5) * math.cos(sy * 2.0 - 0.7) * 0.5
           + math.sin(sx * 0.5 - 0.3) * math.cos(sy * 0.7 + 1.2) * 0.4)
        value += n * amplitude
        norm  += amplitude
        amplitude *= gain
        frequency *= lacunarity
    return value / norm


def build_grass_terrain_ground(bm, size_x, size_y, seed=0, undulation=0.35,
                                subdivisions=12, terrain_type="MEADOW"):
    """多層FBMによる自然な起伏地面（terrain_type: MEADOW/ROCKY/FLAT_DIRT）"""
    rng = random.Random(seed)

    # terrain_type 別パラメーター
    if terrain_type == "ROCKY":
        oct, lac, gain, base_sc = 5, 2.2, 0.45, 0.85
        micro_amp   = undulation * 0.30
        macro_amp   = undulation * 0.70
        ridge_boost = 0.55   # 稜線シャープ化
        target_subdiv = max(subdivisions, 18)
    elif terrain_type == "FLAT_DIRT":
        oct, lac, gain, base_sc = 3, 2.0, 0.55, 0.30
        micro_amp   = undulation * 0.10
        macro_amp   = undulation * 0.15
        ridge_boost = 0.0
        target_subdiv = max(subdivisions, 14)
    else:  # MEADOW
        oct, lac, gain, base_sc = 4, 2.0, 0.55, 0.55
        micro_amp   = undulation * 0.18
        macro_amp   = undulation * 0.55
        ridge_boost = 0.12
        target_subdiv = max(subdivisions, 16)

    half_x = size_x * 0.5
    half_y = size_y * 0.5
    step_x = size_x / target_subdiv
    step_y = size_y / target_subdiv

    verts = []
    for iy in range(target_subdiv + 1):
        row = []
        for ix in range(target_subdiv + 1):
            x = -half_x + ix * step_x
            y = -half_y + iy * step_y

            # 大スケール起伏（FBM）
            h_macro = _fbm(x, y, seed,
                           octaves=oct, lacunarity=lac, gain=gain,
                           base_scale=base_sc) * macro_amp

            # 中スケール起伏（別seed）
            h_mid = _fbm(x, y, seed + 1000,
                         octaves=3, lacunarity=1.8, gain=0.5,
                         base_scale=base_sc * 2.2) * undulation * 0.22

            # 微細バンプ（高周波小振幅）
            h_micro = _fbm(x, y, seed + 2000,
                           octaves=2, lacunarity=2.5, gain=0.6,
                           base_scale=base_sc * 5.0) * micro_amp

            z = h_macro + h_mid + h_micro

            # ROCKY: 山稜シャープ化（値が高い部分を急峻に）
            if ridge_boost > 0:
                t = max(0.0, (z / max(undulation, 0.001)) - 0.25)
                z += t * t * ridge_boost * undulation

            row.append(bm.verts.new((x, y, z)))
        verts.append(row)

    for iy in range(target_subdiv):
        for ix in range(target_subdiv):
            bm.faces.new((verts[iy][ix], verts[iy][ix+1],
                          verts[iy+1][ix+1], verts[iy+1][ix]))
    bm.verts.ensure_lookup_table()
    return [v for row in verts for v in row]


def build_grass_mound_base(bm, size_x, size_y, size_z, shape="SQUARE",
                            seed=0, terrain_type="MEADOW"):
    """草地丘陵地面テレイン（多層FBM対応）"""
    return build_grass_terrain_ground(
        bm, size_x, size_y, seed=seed,
        undulation=size_z * 0.22,
        subdivisions=16,
        terrain_type=terrain_type
    )


def build_grass_blade_with_uv(bm, uv_layer, height=0.6, base_width=0.04, curve_x=0.0, curve_y=0.08, seed=0):
    """UV付き5点先細りブレード"""
    rng = random.Random(seed)
    h = height * rng.uniform(0.82, 1.18)
    bw = base_width * rng.uniform(0.8, 1.2)
    mid_h = h * 0.55
    mid_curve_x = curve_x * rng.uniform(0.6, 1.0)
    mid_curve_y = curve_y * rng.uniform(0.6, 1.0)
    tip_curve_x = curve_x * rng.uniform(0.9, 1.3)
    tip_curve_y = curve_y * rng.uniform(0.9, 1.4)

    v_bl  = bm.verts.new((-bw * 0.5, 0.0, 0.0))
    v_br  = bm.verts.new(( bw * 0.5, 0.0, 0.0))
    v_ml  = bm.verts.new((-bw * 0.25 + mid_curve_x, mid_curve_y, mid_h))
    v_mr  = bm.verts.new(( bw * 0.25 + mid_curve_x, mid_curve_y, mid_h))
    v_tip = bm.verts.new((tip_curve_x, tip_curve_y, h))

    f_bot = bm.faces.new((v_bl, v_br, v_mr, v_ml))
    f_top = bm.faces.new((v_ml, v_mr, v_tip))
    bm.faces.ensure_lookup_table()

    for face, verts_uv in [(f_bot, [(0.0, 0.0), (1.0, 0.0), (1.0, 0.5), (0.0, 0.5)]),
                           (f_top, [(0.0, 0.5), (1.0, 0.5), (0.5, 1.0)])]:
        for loop, uv in zip(face.loops, verts_uv):
            loop[uv_layer].uv = uv

    return [v_bl, v_br, v_ml, v_mr, v_tip]


def build_grass_tuft_clump(bm, size_x, size_y, size_z, blade_count=5, seed=0):
    """草の株 (Tuft/Clump)"""
    random.seed(seed)
    uv_layer = bm.loops.layers.uv.verify()
    blade_count = max(3, min(8, blade_count))
    angles = [i * (180.0 / blade_count) for i in range(blade_count)]
    for i, ang in enumerate(angles):
        ang_rad = math.radians(ang + random.uniform(-12.0, 12.0))
        height   = size_z * random.uniform(0.82, 1.22)
        base_w   = max(size_x, size_y) * 0.06 * random.uniform(0.8, 1.2)
        cx = math.cos(ang_rad + math.pi * 0.5) * random.uniform(0.01, 0.025)
        cy = math.sin(ang_rad + math.pi * 0.5) * random.uniform(0.01, 0.025)
        blade_verts = build_grass_blade_with_uv(bm, uv_layer, height=height, base_width=base_w,
                                                 curve_x=cx, curve_y=cy, seed=seed + i * 37)
        offset_x = random.uniform(-size_x * 0.06, size_x * 0.06)
        offset_y = random.uniform(-size_y * 0.06, size_y * 0.06)
        bmesh.ops.translate(bm, vec=(offset_x, offset_y, 0.0), verts=blade_verts)
    return bm.verts[:]




# =============================================================
# 2. Water Surface Generators
# =============================================================
def build_water_surface_base(bm, size_x, size_y, size_z, shape="LAKE", seed=0, include_bed=True):
    """水面形状ビルダー (LAKE, POND, SQUARE, CIRCLE, OCEAN)"""
    random.seed(seed)
    subdiv = 16
    half_x = size_x * 0.5
    half_y = size_y * 0.5

    if shape == "SQUARE":
        step_x = size_x / float(subdiv)
        step_y = size_y / float(subdiv)
        verts = []
        for iy in range(subdiv + 1):
            row = []
            for ix in range(subdiv + 1):
                x = -half_x + ix * step_x
                y = -half_y + iy * step_y
                z = (math.sin(x * 1.8 + seed * 0.2) * math.cos(y * 1.5 + seed * 0.3)) * (size_z * 0.05)
                row.append(bm.verts.new((x, y, z)))
            verts.append(row)
        for iy in range(subdiv):
            for ix in range(subdiv):
                bm.faces.new((verts[iy][ix], verts[iy][ix+1], verts[iy+1][ix+1], verts[iy+1][ix]))

    elif shape == "CIRCLE":
        rings = 8
        segments = 24
        center_v = bm.verts.new((0.0, 0.0, 0.0))
        prev_ring = [center_v] * segments
        for r in range(1, rings + 1):
            cur_ring = []
            rad_ratio = r / float(rings)
            for s in range(segments):
                ang = s * (math.pi * 2.0 / segments)
                rx = math.cos(ang) * half_x * rad_ratio
                ry = math.sin(ang) * half_y * rad_ratio
                rz = (math.sin(rx * 2.0 + seed * 0.3) * math.cos(ry * 2.0 + seed * 0.4)) * (size_z * 0.04)
                cur_ring.append(bm.verts.new((rx, ry, rz)))
            
            if r == 1:
                for s in range(segments):
                    s_next = (s + 1) % segments
                    bm.faces.new((center_v, cur_ring[s], cur_ring[s_next]))
            else:
                for s in range(segments):
                    s_next = (s + 1) % segments
                    bm.faces.new((prev_ring[s], cur_ring[s], cur_ring[s_next], prev_ring[s_next]))
            prev_ring = cur_ring

    elif shape == "POND":
        rings = 10
        segments = 28
        center_v = bm.verts.new((0.0, 0.0, 0.0))
        prev_ring = [center_v] * segments
        for r in range(1, rings + 1):
            cur_ring = []
            rad_ratio = r / float(rings)
            for s in range(segments):
                ang = s * (math.pi * 2.0 / segments)
                coast_noise = (1.0 + math.sin(ang * 3.0 + seed * 0.7) * 0.12
                                   + math.cos(ang * 5.0 + seed * 0.3) * 0.08)
                rx = math.cos(ang) * half_x * rad_ratio * coast_noise
                ry = math.sin(ang) * half_y * rad_ratio * coast_noise
                rz = (math.sin(rx * 1.5) * math.cos(ry * 1.5)) * (size_z * 0.03)
                cur_ring.append(bm.verts.new((rx, ry, rz)))

            if r == 1:
                for s in range(segments):
                    s_next = (s + 1) % segments
                    bm.faces.new((center_v, cur_ring[s], cur_ring[s_next]))
            else:
                for s in range(segments):
                    s_next = (s + 1) % segments
                    bm.faces.new((prev_ring[s], cur_ring[s], cur_ring[s_next], prev_ring[s_next]))
            prev_ring = cur_ring

        if include_bed:
            bed_depth = size_z * 0.8
            bed_center = bm.verts.new((0.0, 0.0, -bed_depth))
            prev_bed_ring = [bed_center] * segments
            for r in range(1, rings + 1):
                cur_bed_ring = []
                rad_ratio = r / float(rings)
                for s in range(segments):
                    ang = s * (math.pi * 2.0 / segments)
                    coast_noise = (1.0 + math.sin(ang * 3.0 + seed * 0.7) * 0.12
                                       + math.cos(ang * 5.0 + seed * 0.3) * 0.08)
                    rx = math.cos(ang) * half_x * 1.15 * rad_ratio * coast_noise
                    ry = math.sin(ang) * half_y * 1.15 * rad_ratio * coast_noise
                    rz = -bed_depth * (1.0 - (rad_ratio ** 1.8)) - (size_z * 0.08)
                    cur_bed_ring.append(bm.verts.new((rx, ry, rz)))

                if r == 1:
                    for s in range(segments):
                        s_next = (s + 1) % segments
                        f = bm.faces.new((bed_center, cur_bed_ring[s_next], cur_bed_ring[s]))
                        f.material_index = 1
                else:
                    for s in range(segments):
                        s_next = (s + 1) % segments
                        f = bm.faces.new((prev_bed_ring[s], prev_bed_ring[s_next], cur_bed_ring[s_next], cur_bed_ring[s]))
                        f.material_index = 1
                prev_bed_ring = cur_bed_ring

    elif shape == "OCEAN":
        step_x = size_x / float(subdiv)
        step_y = size_y / float(subdiv)
        verts = []
        for iy in range(subdiv + 1):
            row = []
            for ix in range(subdiv + 1):
                x = -half_x + ix * step_x
                y = -half_y + iy * step_y
                row.append(bm.verts.new((x, y, 0.0)))
            verts.append(row)
        for iy in range(subdiv):
            for ix in range(subdiv):
                bm.faces.new((verts[iy][ix], verts[iy][ix+1], verts[iy+1][ix+1], verts[iy+1][ix]))

    else: # LAKE
        step_x = size_x / float(subdiv)
        step_y = size_y / float(subdiv)
        verts = []
        for iy in range(subdiv + 1):
            row = []
            for ix in range(subdiv + 1):
                x = -half_x + ix * step_x
                y = -half_y + iy * step_y
                z = (math.sin(x * 0.8 + seed * 0.15) * math.cos(y * 0.7 + seed * 0.2)
                     + math.sin(x * 2.1 + seed * 0.4) * math.cos(y * 1.8 + seed * 0.3) * 0.35) * (size_z * 0.12)
                row.append(bm.verts.new((x, y, z)))
            verts.append(row)
        for iy in range(subdiv):
            for ix in range(subdiv):
                bm.faces.new((verts[iy][ix], verts[iy][ix+1], verts[iy+1][ix+1], verts[iy+1][ix]))

    return bm.verts[:]


# =============================================================
# 3. High-Quality Procedural Tree Generator Engine (Pure Bmesh)
# =============================================================
def build_branch_tube(bm, points, radii, segments=6, uv_layer=None, mat_idx=0):
    """ポイント列と半径に沿って滑らかな断面サークル押し出しチューブを生成"""
    if len(points) < 2:
        return []
    
    ring_verts = []
    for i, (p, r) in enumerate(zip(points, radii)):
        if i == 0:
            tangent = (points[1] - p).normalized()
        elif i == len(points) - 1:
            tangent = (p - points[i-1]).normalized()
        else:
            tangent = ((points[i+1] - points[i-1]) * 0.5).normalized()
        
        up = mathutils.Vector((0, 0, 1))
        if abs(tangent.dot(up)) > 0.95:
            up = mathutils.Vector((1, 0, 0))
        side = tangent.cross(up).normalized()
        norm = side.cross(tangent).normalized()

        cur_ring = []
        v_coord = i / float(len(points) - 1)
        for s in range(segments):
            angle = s * (2.0 * math.pi / segments)
            offset = (side * math.cos(angle) + norm * math.sin(angle)) * r
            v = bm.verts.new(p + offset)
            cur_ring.append(v)
        ring_verts.append(cur_ring)

    # 側面ポリゴン構築
    for i in range(len(ring_verts) - 1):
        v_low = i / float(len(ring_verts) - 1)
        v_high = (i + 1) / float(len(ring_verts) - 1)
        for s in range(segments):
            s_next = (s + 1) % segments
            v1 = ring_verts[i][s]
            v2 = ring_verts[i][s_next]
            v3 = ring_verts[i+1][s_next]
            v4 = ring_verts[i+1][s]
            f = bm.faces.new((v1, v2, v3, v4))
            f.material_index = mat_idx
            if uv_layer:
                u_low = s / float(segments)
                u_high = (s + 1) / float(segments)
                f.loops[0][uv_layer].uv = (u_low, v_low)
                f.loops[1][uv_layer].uv = (u_high, v_low)
                f.loops[2][uv_layer].uv = (u_high, v_high)
                f.loops[3][uv_layer].uv = (u_low, v_high)

    # 枝の先端キャップ
    tip_center = bm.verts.new(points[-1])
    for s in range(segments):
        s_next = (s + 1) % segments
        f_cap = bm.faces.new((tip_center, ring_verts[-1][s_next], ring_verts[-1][s]))
        f_cap.material_index = mat_idx

    return [v for r in ring_verts for v in r] + [tip_center]


def build_root_flare(bm, base_pos, base_radius, flare_count=4, flare_reach=1.65, flare_height=0.35, seed=0, uv_layer=None):
    """地面を踏ん張る有機的根張り（Buttress Roots / Root Flare）"""
    rng = random.Random(seed)
    root_verts = []
    flare_angles = [i * (2.0 * math.pi / flare_count) + rng.uniform(-0.25, 0.25) for i in range(flare_count)]
    
    for ang in flare_angles:
        dir_vec = mathutils.Vector((math.cos(ang), math.sin(ang), 0.0))
        pts = [
            base_pos + mathutils.Vector((0, 0, flare_height)),
            base_pos + dir_vec * (base_radius * 0.8) + mathutils.Vector((0, 0, flare_height * 0.45)),
            base_pos + dir_vec * (base_radius * flare_reach) + mathutils.Vector((0, 0, 0.0))
        ]
        radii = [base_radius * 0.45, base_radius * 0.35, base_radius * 0.12]
        rv = build_branch_tube(bm, pts, radii, segments=5, uv_layer=uv_layer, mat_idx=0)
        root_verts.extend(rv)
    return root_verts


def build_cross_billboard_leaf(bm, center_pos, size=0.45, rot_z=0.0, uv_layer=None):
    """十字クロス（X字）ビルボード葉（ゲーム・PBR用）"""
    half_s = size * 0.5
    h_s = size * 0.8
    # 2枚の交差平面
    for angle_offset in (0.0, math.pi * 0.5):
        ang = rot_z + angle_offset
        dx = math.cos(ang) * half_s
        dy = math.sin(ang) * half_s
        
        v1 = bm.verts.new(center_pos + mathutils.Vector((-dx, -dy, 0.0)))
        v2 = bm.verts.new(center_pos + mathutils.Vector(( dx,  dy, 0.0)))
        v3 = bm.verts.new(center_pos + mathutils.Vector(( dx,  dy, h_s)))
        v4 = bm.verts.new(center_pos + mathutils.Vector((-dx, -dy, h_s)))
        
        f = bm.faces.new((v1, v2, v3, v4))
        f.material_index = 1
        if uv_layer:
            f.loops[0][uv_layer].uv = (0.0, 0.0)
            f.loops[1][uv_layer].uv = (1.0, 0.0)
            f.loops[2][uv_layer].uv = (1.0, 1.0)
            f.loops[3][uv_layer].uv = (0.0, 1.0)


def build_canopy_volume_leaf(bm, center_pos, radius=0.65, seed=0, uv_layer=None):
    """CG Geek動画準拠: 有機的ディスプレイス変形されたボリューム樹冠メッシュ"""
    rng = random.Random(seed)
    res = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=radius)
    v_list = res['verts']
    
    # 雲のようなふんわり有機的変形
    scale_x = rng.uniform(0.85, 1.25)
    scale_y = rng.uniform(0.85, 1.25)
    scale_z = rng.uniform(0.75, 1.1)
    
    for v in v_list:
        p = v.co
        noise_val = (math.sin(p.x * 3.5 + seed * 0.4) * math.cos(p.y * 3.5 + seed * 0.5) * 0.15)
        v.co.x = (p.x * scale_x) * (1.0 + noise_val)
        v.co.y = (p.y * scale_y) * (1.0 + noise_val)
        v.co.z = (p.z * scale_z) * (1.0 + noise_val)
    
    bmesh.ops.translate(bm, vec=center_pos, verts=v_list)
    
    # マテリアルインデックス 1 (Leaf)
    for f in bm.faces:
        if all(v in v_list for v in f.verts):
            f.material_index = 1
            if uv_layer:
                for loop in f.loops:
                    loop[uv_layer].uv = (0.5 + loop.vert.co.x * 0.3, 0.5 + loop.vert.co.y * 0.3)


def generate_sapling_real_tree(
    context,
    target_obj=None,
    name="Real_Tree",
    species="OAK",
    has_leaves=True,
    leaf_count=120,
    branch_levels=2,
    leaf_style="QUAD_CROSS",
    mat_mode="PROCEDURAL",
    seed=0,
    size_z=4.5
):
    """5つの動画知見を完全結集した純粋プロシージャル樹木生成エンジン (アドオン非依存・100%安定)"""
    if context.mode != 'OBJECT':
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass

    old_loc = target_obj.location.copy() if target_obj else mathutils.Vector((0, 0, 0))
    old_rot = target_obj.rotation_euler.copy() if target_obj else mathutils.Euler((0, 0, 0))
    old_name = target_obj.name if target_obj else name

    if target_obj and target_obj.type == 'MESH':
        obj = target_obj
        obj.name = old_name
        mesh = obj.data
        mesh.name = old_name + "_Mesh"
        mesh.clear_geometry()
        obj.modifiers.clear()
        obj.data.materials.clear()
    else:
        mesh = bpy.data.meshes.new(old_name + "_Mesh")
        obj = bpy.data.objects.new(old_name, mesh)
        context.collection.objects.link(obj)

    context.view_layer.objects.active = obj
    obj.select_set(True)

    rng = random.Random(seed)
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.verify()

    total_h = max(2.5, size_z)
    trunk_radius_base = total_h * 0.055
    trunk_radius_top = trunk_radius_base * 0.32

    # ── 1. 幹（Trunk）のパス生成
    trunk_segments = 10
    trunk_pts = []
    trunk_radii = []
    curve_factor = rng.uniform(0.08, 0.22)
    curve_dir_ang = rng.uniform(0.0, math.pi * 2.0)
    
    if species == "PALM":
        # ヤシの木: 根元から大きく一方向にしなる弓なり幹
        trunk_radius_base = total_h * 0.045
        trunk_radius_top = trunk_radius_base * 0.55
        for i in range(trunk_segments + 1):
            t = i / float(trunk_segments)
            z = t * total_h
            lean = (t ** 1.6) * total_h * 0.32
            x = math.cos(curve_dir_ang) * lean
            y = math.sin(curve_dir_ang) * lean
            r = trunk_radius_base * (1.0 - t * 0.45)
            # ヤシのフシ（リング）
            r *= (1.0 + math.sin(t * 35.0) * 0.04)
            trunk_pts.append(mathutils.Vector((x, y, z)))
            trunk_radii.append(r)
    else:
        for i in range(trunk_segments + 1):
            t = i / float(trunk_segments)
            z = t * total_h
            # 有機的な幹のうねり
            wiggle_x = math.sin(t * math.pi * 1.8 + seed * 0.5) * (total_h * curve_factor * t)
            wiggle_y = math.cos(t * math.pi * 1.5 + seed * 0.8) * (total_h * curve_factor * t * 0.8)
            r = trunk_radius_base * (1.0 - t * 0.68)
            trunk_pts.append(mathutils.Vector((wiggle_x, wiggle_y, z)))
            trunk_radii.append(r)

    # 幹メッシュ構築
    build_branch_tube(bm, trunk_pts, trunk_radii, segments=8, uv_layer=uv_layer, mat_idx=0)

    # 根張り（Root Flare）
    if species in ("OAK", "JAPANESE_MAPLE", "WILLOW", "BIRCH"):
        build_root_flare(bm, trunk_pts[0], trunk_radius_base, flare_count=rng.randint(3, 5),
                         flare_reach=rng.uniform(1.6, 2.1), flare_height=total_h * 0.12, seed=seed, uv_layer=uv_layer)

    leaf_spawn_points = []

    # ── 2. 枝分かれ（Branching Hierarchy）
    if species == "PALM":
        # ヤシの木: 頂点から放射状に広がる大葉（Fronds）
        top_pos = trunk_pts[-1]
        frond_count = rng.randint(9, 14)
        for fi in range(frond_count):
            ang = fi * (2.0 * math.pi / frond_count) + rng.uniform(-0.15, 0.15)
            frond_len = total_h * rng.uniform(0.38, 0.52)
            f_pts = []
            f_rad = []
            f_segs = 6
            for si in range(f_segs + 1):
                st = si / float(f_segs)
                # 弓なりに外側・下側へ垂れる
                dist_h = st * frond_len
                drop_z = - (st ** 1.8) * (frond_len * 0.55)
                fx = top_pos.x + math.cos(ang) * dist_h
                fy = top_pos.y + math.sin(ang) * dist_h
                fz = top_pos.z + (math.sin(st * math.pi) * frond_len * 0.18) + drop_z
                f_pts.append(mathutils.Vector((fx, fy, fz)))
                f_rad.append(trunk_radius_top * (0.35 * (1.0 - st * 0.7)))
                if st > 0.25:
                    leaf_spawn_points.append(mathutils.Vector((fx, fy, fz)))
            build_branch_tube(bm, f_pts, f_rad, segments=4, uv_layer=uv_layer, mat_idx=0)

    elif species == "PINE":
        # パイン（マツ・針葉樹）: 三角錐状の層状枝（Whorls）
        tier_count = rng.randint(5, 8)
        for ti in range(tier_count):
            t_ratio = 0.25 + (ti / float(tier_count)) * 0.68
            tier_z = total_h * t_ratio
            tier_idx = int(t_ratio * trunk_segments)
            base_pt = trunk_pts[min(tier_idx, len(trunk_pts) - 1)]
            
            # 上段ほど枝が短い（三角錐コーン）
            branch_len = (1.0 - t_ratio * 0.85) * (total_h * 0.38)
            branches_in_tier = rng.randint(4, 6)
            for bi in range(branches_in_tier):
                ang = bi * (2.0 * math.pi / branches_in_tier) + rng.uniform(-0.2, 0.2) + ti * 0.5
                b_pts = []
                b_rad = []
                b_segs = 4
                for si in range(b_segs + 1):
                    st = si / float(b_segs)
                    bx = base_pt.x + math.cos(ang) * (st * branch_len)
                    by = base_pt.y + math.sin(ang) * (st * branch_len)
                    # 先端がやや上向き・自重で少し下がる
                    bz = base_pt.z - (st * branch_len * 0.15) + (math.sin(st * math.pi) * 0.08)
                    b_pts.append(mathutils.Vector((bx, by, bz)))
                    b_rad.append(trunk_radius_base * 0.35 * (1.0 - st * 0.75))
                build_branch_tube(bm, b_pts, b_rad, segments=4, uv_layer=uv_layer, mat_idx=0)
                leaf_spawn_points.append(b_pts[-1])
                leaf_spawn_points.append(b_pts[-2])

    elif species == "WILLOW":
        # シダレヤナギ: 上部に伸びてから下へ長く垂れ下がる優美な枝
        main_branches = rng.randint(4, 7)
        for bi in range(main_branches):
            ang = bi * (2.0 * math.pi / main_branches) + rng.uniform(-0.3, 0.3)
            base_t = rng.uniform(0.6, 0.85)
            base_pt = trunk_pts[int(base_t * trunk_segments)]
            b_len = total_h * rng.uniform(0.35, 0.55)
            
            # 主枝
            b_pts = []
            b_rad = []
            for si in range(6):
                st = si / 5.0
                bx = base_pt.x + math.cos(ang) * (st * b_len * 0.8)
                by = base_pt.y + math.sin(ang) * (st * b_len * 0.8)
                bz = base_pt.z + math.sin(st * math.pi * 0.5) * (b_len * 0.35)
                b_pts.append(mathutils.Vector((bx, by, bz)))
                b_rad.append(trunk_radius_base * 0.4 * (1.0 - st * 0.65))
            build_branch_tube(bm, b_pts, b_rad, segments=5, uv_layer=uv_layer, mat_idx=0)

            # 垂れ下がる細枝（Hanging Vines）
            vine_start = b_pts[-1]
            vine_count = rng.randint(2, 4)
            for vi in range(vine_count):
                v_ang = ang + rng.uniform(-0.6, 0.6)
                v_pts = [vine_start]
                v_rad = [b_rad[-1] * 0.6]
                v_drop = total_h * rng.uniform(0.35, 0.55)
                for vi_s in range(1, 5):
                    vt = vi_s / 4.0
                    vx = vine_start.x + math.cos(v_ang) * (vt * 0.25)
                    vy = vine_start.y + math.sin(v_ang) * (vt * 0.25)
                    vz = vine_start.z - (vt * v_drop)
                    v_pts.append(mathutils.Vector((vx, vy, vz)))
                    v_rad.append(v_rad[0] * (1.0 - vt * 0.7))
                    leaf_spawn_points.append(v_pts[-1])
                build_branch_tube(bm, v_pts, v_rad, segments=3, uv_layer=uv_layer, mat_idx=0)

    else:
        # オーク (OAK), シラカバ (BIRCH), モミジ (JAPANESE_MAPLE)
        main_branches = rng.randint(4, 7) if species != "BIRCH" else rng.randint(3, 5)
        for bi in range(main_branches):
            ang = bi * (2.0 * math.pi / main_branches) + rng.uniform(-0.35, 0.35)
            start_t = rng.uniform(0.42, 0.82) if species != "JAPANESE_MAPLE" else rng.uniform(0.32, 0.72)
            base_pt = trunk_pts[int(start_t * trunk_segments)]
            b_len = total_h * (rng.uniform(0.32, 0.55) if species == "OAK" else rng.uniform(0.25, 0.42))
            
            # Level 1 大枝
            b1_pts = []
            b1_rad = []
            b1_segs = 5
            for si in range(b1_segs + 1):
                st = si / float(b1_segs)
                pitch = 0.55 if species == "OAK" else (0.75 if species == "BIRCH" else 0.35)
                bx = base_pt.x + math.cos(ang) * (st * b_len)
                by = base_pt.y + math.sin(ang) * (st * b_len)
                bz = base_pt.z + (st * b_len * pitch) + (math.sin(st * math.pi) * 0.12)
                b1_pts.append(mathutils.Vector((bx, by, bz)))
                b1_rad.append(trunk_radius_base * 0.45 * (1.0 - st * 0.65))
            build_branch_tube(bm, b1_pts, b1_rad, segments=5, uv_layer=uv_layer, mat_idx=0)

            # Level 2 小枝
            if branch_levels >= 2:
                sub_branches = rng.randint(2, 3)
                for sbi in range(sub_branches):
                    sub_ang = ang + rng.choice([-0.7, 0.7]) + rng.uniform(-0.2, 0.2)
                    sub_start = b1_pts[-2] if sbi == 0 else b1_pts[-1]
                    sub_len = b_len * 0.55
                    b2_pts = [sub_start]
                    b2_rad = [b1_rad[-1] * 0.7]
                    for s2 in range(1, 4):
                        st2 = s2 / 3.0
                        s2_x = sub_start.x + math.cos(sub_ang) * (st2 * sub_len)
                        s2_y = sub_start.y + math.sin(sub_ang) * (st2 * sub_len)
                        s2_z = sub_start.z + (st2 * sub_len * 0.4)
                        b2_pts.append(mathutils.Vector((s2_x, s2_y, s2_z)))
                        b2_rad.append(b2_rad[0] * (1.0 - st2 * 0.7))
                    build_branch_tube(bm, b2_pts, b2_rad, segments=4, uv_layer=uv_layer, mat_idx=0)
                    leaf_spawn_points.append(b2_pts[-1])
            else:
                leaf_spawn_points.append(b1_pts[-1])

    # 頂点にも葉クラスタを追加
    leaf_spawn_points.append(trunk_pts[-1])

    # ── 3. 葉（Foliage）の生成
    if has_leaves and leaf_spawn_points:
        leaf_sz = total_h * 0.09
        canopy_r = total_h * (0.16 if species != "OAK" else 0.24)
        
        for li, pt in enumerate(leaf_spawn_points):
            if leaf_style == "CANOPY_VOLUME":
                build_canopy_volume_leaf(bm, pt, radius=canopy_r * rng.uniform(0.85, 1.25),
                                         seed=seed + li * 29, uv_layer=uv_layer)
            else: # QUAD_CROSS (ゲーム用十字リーフ)
                cluster_count = rng.randint(2, 4)
                for ci in range(cluster_count):
                    offset = mathutils.Vector((
                        rng.uniform(-leaf_sz * 0.8, leaf_sz * 0.8),
                        rng.uniform(-leaf_sz * 0.8, leaf_sz * 0.8),
                        rng.uniform(-leaf_sz * 0.4, leaf_sz * 0.8)
                    ))
                    build_cross_billboard_leaf(bm, pt + offset, size=leaf_sz * rng.uniform(0.9, 1.3),
                                               rot_z=rng.uniform(0, math.pi * 2), uv_layer=uv_layer)

    bm.to_mesh(mesh)
    bm.free()

    # ── 4. 接地点（Z=0）原点の厳密設定
    mesh.update()
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    context.view_layer.objects.active = obj
    
    # 最底面頂点のZ座標を取得してピタリとZ=0に合わせる
    min_z = min((v.co.z for v in mesh.vertices), default=0.0)
    for v in mesh.vertices:
        v.co.z -= min_z
    mesh.update()

    # Smooth Shading
    for p in mesh.polygons:
        p.use_smooth = True

    # ── 5. マテリアルのアサイン
    mat_bark = create_procedural_bark_material(old_name + "_Bark_Mat", seed=seed, species=species)
    obj.data.materials.append(mat_bark)

    if has_leaves:
        mat_leaf = create_procedural_leaf_material(old_name + "_Leaf_Mat", seed=seed, species=species)
        obj.data.materials.append(mat_leaf)

    obj.location = old_loc
    obj.rotation_euler = old_rot

    return obj


# ── 4. Grass Field Scene Builder (動画 09:00 & 14:06 準拠)
def create_grass_field_scene(context, name, seed=0,
                             terrain_size_x=10.0, terrain_size_y=10.0,
                             blade_height=0.6, grass_density=8000,
                             undulation=0.35, weight_noise_scale=2.5):
    """草原シーン一括生成: 地面テレイン + 草ブレードコレクション + Hair Particle System"""
    random.seed(seed)
    col = context.collection

    grass_col_name = name + "_GrassCollection"
    if grass_col_name in bpy.data.collections:
        bpy.data.collections.remove(bpy.data.collections[grass_col_name])
    grass_col = bpy.data.collections.new(grass_col_name)
    context.scene.collection.children.link(grass_col)

    blade_mat = create_procedural_grass_blade_shader(name + "_Blade_Mat", seed)

    blade_defs = [
        ("Straight", 0.0, 0.0),
        ("CurveLeft",  -0.04, 0.06),
        ("CurveRight",  0.04, 0.06),
    ]
    for bname, cx, cy in blade_defs:
        bm_b = bmesh.new()
        uv_l = bm_b.loops.layers.uv.verify()
        build_grass_blade_with_uv(bm_b, uv_l, height=blade_height,
                                   base_width=0.032, curve_x=cx, curve_y=cy, seed=seed)
        mesh_b = bpy.data.meshes.new(name + "_" + bname)
        bm_b.to_mesh(mesh_b)
        bm_b.free()
        obj_b = bpy.data.objects.new(name + "_" + bname, mesh_b)
        grass_col.objects.link(obj_b)
        obj_b.data.materials.append(blade_mat)
        for v in mesh_b.vertices:
            if v.co.z < 0:
                v.co.z = 0.0

    terrain_name = name + "_Terrain"
    if terrain_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[terrain_name], do_unlink=True)

    bm_t = bmesh.new()
    build_grass_terrain_ground(bm_t, terrain_size_x, terrain_size_y,
                                seed=seed, undulation=undulation, subdivisions=16)
    mesh_t = bpy.data.meshes.new(terrain_name)
    bm_t.to_mesh(mesh_t)
    bm_t.free()
    terrain_obj = bpy.data.objects.new(terrain_name, mesh_t)
    col.objects.link(terrain_obj)
    context.view_layer.objects.active = terrain_obj

    ground_mat = create_procedural_ground_terrain_shader(name + "_Ground_Mat", seed)
    terrain_obj.data.materials.append(ground_mat)

    vg = terrain_obj.vertex_groups.new(name="Grass_Density")
    mesh_t.update()
    for v in mesh_t.vertices:
        x, y = v.co.x, v.co.y
        w_raw = (math.sin(x * weight_noise_scale + seed * 0.17)
                 * math.cos(y * weight_noise_scale + seed * 0.23) * 0.5 + 0.5)
        w_raw += (math.sin(x * weight_noise_scale * 2.1 + seed * 0.5)
                  * math.cos(y * weight_noise_scale * 1.9 + seed * 0.6) * 0.25)
        weight = max(0.05, min(1.0, w_raw))
        vg.add([v.index], weight, 'REPLACE')

    ps_mod = terrain_obj.modifiers.new("GrassHair", 'PARTICLE_SYSTEM')
    ps = ps_mod.particle_system
    ps.name = "GrassHair"
    pset = ps.settings
    pset.type = 'HAIR'
    pset.count = grass_density
    pset.hair_length = blade_height * 1.8
    pset.render_type = 'COLLECTION'
    pset.instance_collection = grass_col
    pset.use_collection_pick_random = True
    pset.particle_size = 1.0
    pset.size_random = 0.30
    pset.use_rotations = True
    pset.rotation_mode = 'GLOB_Z'
    pset.rotation_factor_random = 1.0
    pset.phase_factor = 0.0
    pset.phase_factor_random = 2.0
    pset.use_scale_instance = True
    try:
        ps.vertex_group_density = "Grass_Density"
    except Exception:
        pass

    return terrain_obj, grass_col
