import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# ==============================================================================
# 🎨 Procedural Shaders for Spiral Stairs
# ==============================================================================

def get_or_create_material(name):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
    return mat


def create_stairs_wood_shader(name="SpiralStairs_Wood", style='DARK_WALNUT'):
    """プロシージャル高級木目シェーダー（ウォールナット／ナチュラルオーク）"""
    mat = get_or_create_material(name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (600, 0)

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)

    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-600, 0)
    mapping.inputs['Scale'].default_value = (1.0, 1.0, 12.0)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-400, 100)
    noise.inputs['Scale'].default_value = 14.0
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.55
    noise.inputs['Distortion'].default_value = 1.8
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])

    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-150, 100)

    if style == 'DARK_WALNUT':
        color_ramp.color_ramp.elements[0].position = 0.2
        color_ramp.color_ramp.elements[0].color = (0.045, 0.022, 0.012, 1.0)
        color_ramp.color_ramp.elements[1].position = 0.85
        color_ramp.color_ramp.elements[1].color = (0.13, 0.07, 0.038, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.32
    else:
        color_ramp.color_ramp.elements[0].position = 0.25
        color_ramp.color_ramp.elements[0].color = (0.28, 0.18, 0.10, 1.0)
        color_ramp.color_ramp.elements[1].position = 0.8
        color_ramp.color_ramp.elements[1].color = (0.52, 0.38, 0.22, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.40

    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (50, -150)
    bump.inputs['Strength'].default_value = 0.08
    bump.inputs['Distance'].default_value = 0.005
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat


def create_stairs_metal_shader(name="SpiralStairs_Metal", style='CAST_IRON'):
    """鍛造黒鉄、アンティーク真鍮、つや消しスチールのPBRプロシージャルシェーダー"""
    mat = get_or_create_material(name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (600, 0)

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)

    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-400, 0)
    noise.inputs['Scale'].default_value = 35.0
    noise.inputs['Detail'].default_value = 5.0
    noise.inputs['Roughness'].default_value = 0.6
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (0, -150)
    bump.inputs['Distance'].default_value = 0.003
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    if style == 'CAST_IRON':
        bsdf.inputs['Base Color'].default_value = (0.045, 0.045, 0.05, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.90
        bsdf.inputs['Roughness'].default_value = 0.42
        bump.inputs['Strength'].default_value = 0.30
    elif style == 'BRASS':
        bsdf.inputs['Base Color'].default_value = (0.58, 0.42, 0.16, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.94
        bsdf.inputs['Roughness'].default_value = 0.32
        bump.inputs['Strength'].default_value = 0.15
    elif style == 'STAINLESS':
        bsdf.inputs['Base Color'].default_value = (0.75, 0.76, 0.78, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.96
        bsdf.inputs['Roughness'].default_value = 0.25
        bump.inputs['Strength'].default_value = 0.10

    return mat


def create_stairs_stone_shader(name="SpiralStairs_Stone"):
    """風化古城石材のPBRプロシージャルシェーダー"""
    mat = get_or_create_material(name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (600, 0)

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)

    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-400, 0)
    noise.inputs['Scale'].default_value = 16.0
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.7
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-150, 50)
    color_ramp.color_ramp.elements[0].position = 0.2
    color_ramp.color_ramp.elements[0].color = (0.15, 0.14, 0.13, 1.0)
    color_ramp.color_ramp.elements[1].position = 0.8
    color_ramp.color_ramp.elements[1].color = (0.42, 0.40, 0.38, 1.0)
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.82

    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (0, -150)
    bump.inputs['Strength'].default_value = 0.45
    bump.inputs['Distance'].default_value = 0.01
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat


# ==============================================================================
# 🔨 BMesh Modeling Elements
# ==============================================================================

def build_single_step(bm, inner_r, outer_r, start_angle, angle_span, z_base, thickness, nose_overhang=0.03, mat_idx=0):
    """
    1段分の扇形踏み板（ステップ）をBMeshに追加
    前縁にノーズ（張り出し・段鼻）を持たせ、リアルな重なりを演出
    """
    segs = 8
    
    top_inner = []
    top_outer = []
    bot_inner = []
    bot_outer = []
    
    z_top = z_base + thickness
    z_bot = z_base
    
    for s in range(segs + 1):
        frac = s / segs
        ang = start_angle + frac * angle_span
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        
        pt_in_top = bm.verts.new((inner_r * cos_a, inner_r * sin_a, z_top))
        pt_in_bot = bm.verts.new((inner_r * cos_a, inner_r * sin_a, z_bot))
        top_inner.append(pt_in_top)
        bot_inner.append(pt_in_bot)
        
        r_out_actual = outer_r + (nose_overhang if frac < 0.5 else 0.0)
        pt_out_top = bm.verts.new((r_out_actual * cos_a, r_out_actual * sin_a, z_top))
        pt_out_bot = bm.verts.new((r_out_actual * cos_a, r_out_actual * sin_a, z_bot))
        top_outer.append(pt_out_top)
        bot_outer.append(pt_out_bot)

    new_faces = []
    for s in range(segs):
        f_top = bm.faces.new([top_inner[s], top_outer[s], top_outer[s+1], top_inner[s+1]])
        f_bot = bm.faces.new([bot_inner[s], bot_inner[s+1], bot_outer[s+1], bot_outer[s]])
        f_out = bm.faces.new([top_outer[s], bot_outer[s], bot_outer[s+1], top_outer[s+1]])
        f_in  = bm.faces.new([top_inner[s], top_inner[s+1], bot_inner[s+1], bot_inner[s]])
        new_faces.extend([f_top, f_bot, f_out, f_in])

    f_start = bm.faces.new([top_inner[0], bot_inner[0], bot_outer[0], top_outer[0]])
    f_end   = bm.faces.new([top_inner[-1], top_outer[-1], bot_outer[-1], bot_inner[-1]])
    new_faces.extend([f_start, f_end])

    for f in new_faces:
        f.material_index = mat_idx


def build_baluster(bm, x, y, z_bottom, z_top, radius=0.016, style='ORNATE_TURNED', mat_idx=1):
    """
    手すり子（バラスター）の生成
    指定されたスタイル（装飾旋盤・丸棒・角柱）で配置
    """
    height = z_top - z_bottom
    if height <= 0.05:
        return

    bm_temp = bmesh.new()
    segs = 12

    if style == 'SIMPLE_ROUND':
        res = bmesh.ops.create_cone(
            bm_temp, cap_ends=True, cap_tris=False, segments=segs,
            radius1=radius, radius2=radius, depth=height
        )
        bmesh.ops.translate(bm_temp, vec=(0, 0, height * 0.5), verts=res['verts'])

    elif style == 'SQUARE_BAR':
        res = bmesh.ops.create_cube(bm_temp, size=1.0)
        bmesh.ops.scale(bm_temp, vec=(radius * 2.0, radius * 2.0, height), verts=res['verts'])
        bmesh.ops.translate(bm_temp, vec=(0, 0, height * 0.5), verts=res['verts'])

    else:  # ORNATE_TURNED
        shaft_r = radius * 0.65
        res_shaft = bmesh.ops.create_cone(
            bm_temp, cap_ends=True, cap_tris=False, segments=segs,
            radius1=shaft_r, radius2=shaft_r, depth=height
        )
        bmesh.ops.translate(bm_temp, vec=(0, 0, height * 0.5), verts=res_shaft['verts'])

        foot_h = min(height * 0.12, 0.08)
        res_foot = bmesh.ops.create_cube(bm_temp, size=1.0)
        bmesh.ops.scale(bm_temp, vec=(radius * 2.2, radius * 2.2, foot_h), verts=res_foot['verts'])
        bmesh.ops.translate(bm_temp, vec=(0, 0, foot_h * 0.5), verts=res_foot['verts'])

        top_h = min(height * 0.08, 0.05)
        res_top = bmesh.ops.create_cube(bm_temp, size=1.0)
        bmesh.ops.scale(bm_temp, vec=(radius * 2.2, radius * 2.2, top_h), verts=res_top['verts'])
        bmesh.ops.translate(bm_temp, vec=(0, 0, height - top_h * 0.5), verts=res_top['verts'])

        bead_r = radius * 1.55
        res_bead = bmesh.ops.create_icosphere(bm_temp, subdivisions=2, radius=bead_r)
        bmesh.ops.scale(bm_temp, vec=(1.0, 1.0, 1.25), verts=res_bead['verts'])
        bmesh.ops.translate(bm_temp, vec=(0, 0, height * 0.52), verts=res_bead['verts'])

        ring_r = radius * 1.3
        res_ring = bmesh.ops.create_icosphere(bm_temp, subdivisions=2, radius=ring_r)
        bmesh.ops.scale(bm_temp, vec=(1.0, 1.0, 0.6), verts=res_ring['verts'])
        bmesh.ops.translate(bm_temp, vec=(0, 0, height * 0.28), verts=res_ring['verts'])

    for v in bm_temp.verts:
        v.co.x += x
        v.co.y += y
        v.co.z += z_bottom

    for f in bm_temp.faces:
        new_f = bm.faces.new([bm.verts.new(v.co) for v in f.verts])
        new_f.material_index = mat_idx

    bm_temp.free()


def build_helical_handrail(bm, radius, step_height, step_angle_rad, total_steps, rail_height=0.90, rail_r_x=0.032, rail_r_z=0.024, mat_idx=1):
    """
    滑らかに連続する螺旋手すり（チューブスイープ）の生成
    """
    subdiv_per_step = 8
    total_samples = total_steps * subdiv_per_step + 1

    profile_segs = 12
    ring_verts_list = []

    profile_angles = [(p / profile_segs) * 2.0 * math.pi for p in range(profile_segs)]

    for idx in range(total_samples):
        t = (idx / subdiv_per_step)
        theta = t * step_angle_rad
        z_center = t * step_height + rail_height

        cos_t = math.cos(theta)
        sin_t = math.sin(theta)

        P = Vector((radius * cos_t, radius * sin_t, z_center))

        w = step_angle_rad
        T = Vector((-radius * w * sin_t, radius * w * cos_t, step_height))
        T.normalize()

        N = Vector((cos_t, sin_t, 0.0))

        B = T.cross(N)
        B.normalize()

        current_ring = []
        for p_ang in profile_angles:
            dx = rail_r_x * math.cos(p_ang)
            dz = rail_r_z * math.sin(p_ang)
            v_pos = P + N * dx + B * dz
            v = bm.verts.new(v_pos)
            current_ring.append(v)

        ring_verts_list.append(current_ring)

    for idx in range(len(ring_verts_list) - 1):
        ring_a = ring_verts_list[idx]
        ring_b = ring_verts_list[idx + 1]
        for p in range(profile_segs):
            p_next = (p + 1) % profile_segs
            f = bm.faces.new([ring_a[p], ring_b[p], ring_b[p_next], ring_a[p_next]])
            f.material_index = mat_idx

    start_cap = bm.faces.new(list(reversed(ring_verts_list[0])))
    start_cap.material_index = mat_idx
    end_cap = bm.faces.new(ring_verts_list[-1])
    end_cap.material_index = mat_idx


def build_center_pillar(bm, radius, total_height, style='CLASSIC_WOOD', mat_idx=1):
    """
    螺旋階段の中心支柱（センターピラー）を生成
    """
    bm_temp = bmesh.new()
    segs = 24

    res_shaft = bmesh.ops.create_cone(
        bm_temp, cap_ends=True, cap_tris=False, segments=segs,
        radius1=radius, radius2=radius, depth=total_height
    )
    bmesh.ops.translate(bm_temp, vec=(0, 0, total_height * 0.5), verts=res_shaft['verts'])

    base_h = 0.12
    res_base = bmesh.ops.create_cone(
        bm_temp, cap_ends=True, cap_tris=False, segments=segs,
        radius1=radius * 1.35, radius2=radius * 1.15, depth=base_h
    )
    bmesh.ops.translate(bm_temp, vec=(0, 0, base_h * 0.5), verts=res_base['verts'])

    top_h = total_height
    finial_r = radius * 1.25
    res_finial = bmesh.ops.create_icosphere(bm_temp, subdivisions=2, radius=finial_r)
    bmesh.ops.scale(bm_temp, vec=(1.0, 1.0, 1.1), verts=res_finial['verts'])
    bmesh.ops.translate(bm_temp, vec=(0, 0, top_h + finial_r * 0.8), verts=res_finial['verts'])

    for f in bm_temp.faces:
        new_f = bm.faces.new([bm.verts.new(v.co) for v in f.verts])
        new_f.material_index = mat_idx

    bm_temp.free()


# ==============================================================================
# 🚀 Master Generator Entry Point
# ==============================================================================

def generate_spiral_stairs(
    style='CLASSIC_WOOD',
    step_count=20,
    radius=1.2,
    inner_radius=0.15,
    step_height=0.18,
    step_angle=18.0,
    baluster_style='ORNATE_TURNED',
    has_pillar=True,
    has_handrail=True,
    tread_material_style='DARK_WALNUT',
    metal_material_style='CAST_IRON',
    combine_mesh=True,
    location=(0, 0, 0),
    rotation=(0, 0, 0)
):
    """
    完全パラメトリック手すり付き螺旋階段の統合生成
    """
    step_angle_rad = math.radians(step_angle)
    step_angle_span = step_angle_rad * 1.18
    step_thickness = 0.04
    total_height = step_count * step_height

    if style == 'CLASSIC_WOOD':
        tread_mat = create_stairs_wood_shader(f"SpiralStairs_Wood_{tread_material_style}", tread_material_style)
        metal_mat = create_stairs_metal_shader(f"SpiralStairs_Metal_{metal_material_style}", metal_material_style)
    elif style == 'CAST_IRON':
        tread_mat = create_stairs_metal_shader("SpiralStairs_CastIron_Tread", 'CAST_IRON')
        metal_mat = create_stairs_metal_shader("SpiralStairs_CastIron_Rail", 'CAST_IRON')
    elif style == 'CASTLE_STONE':
        tread_mat = create_stairs_stone_shader("SpiralStairs_CastleStone")
        metal_mat = create_stairs_metal_shader("SpiralStairs_CastleIron", 'CAST_IRON')
        step_thickness = 0.08
    else:  # MODERN_STEEL
        tread_mat = create_stairs_metal_shader("SpiralStairs_ModernSteel_Tread", 'STAINLESS')
        metal_mat = create_stairs_metal_shader("SpiralStairs_ModernSteel_Rail", 'STAINLESS')
        baluster_style = 'SIMPLE_ROUND'

    created_objects = []

    if combine_mesh:
        bm = bmesh.new()

        for i in range(step_count):
            start_ang = i * step_angle_rad
            z_b = i * step_height
            build_single_step(
                bm,
                inner_r=inner_radius,
                outer_r=radius,
                start_angle=start_ang,
                angle_span=step_angle_span,
                z_base=z_b,
                thickness=step_thickness,
                nose_overhang=0.025,
                mat_idx=0
            )

        if has_pillar:
            pillar_mat_idx = 0 if style == 'CASTLE_STONE' else 1
            build_center_pillar(bm, inner_radius, total_height + 0.9, style=style, mat_idx=pillar_mat_idx)

        if has_handrail:
            rail_r = radius - 0.05
            build_helical_handrail(
                bm,
                radius=rail_r,
                step_height=step_height,
                step_angle_rad=step_angle_rad,
                total_steps=step_count,
                rail_height=0.90,
                rail_r_x=0.032,
                rail_r_z=0.024,
                mat_idx=1
            )

            for i in range(step_count):
                mid_ang = (i + 0.45) * step_angle_rad
                bx = rail_r * math.cos(mid_ang)
                by = rail_r * math.sin(mid_ang)
                z_bot = i * step_height + step_thickness
                z_top = (i + 0.45) * step_height + 0.90 - 0.024

                build_baluster(
                    bm,
                    x=bx,
                    y=by,
                    z_bottom=z_bot,
                    z_top=z_top,
                    radius=0.014,
                    style=baluster_style,
                    mat_idx=1
                )

        mesh = bpy.data.meshes.new("Spiral_Stairs_Mesh")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new("Spiral_Stairs_Asset", mesh)
        bpy.context.collection.objects.link(obj)

        obj.data.materials.append(tread_mat)   # Index 0
        obj.data.materials.append(metal_mat)   # Index 1

        obj.location = location
        obj.rotation_euler = rotation

        for poly in mesh.polygons:
            poly.use_smooth = True

        created_objects.append(obj)

    else:
        parent_obj = bpy.data.objects.new("Spiral_Stairs_Root", None)
        parent_obj.empty_display_type = 'ARROWS'
        parent_obj.location = location
        parent_obj.rotation_euler = rotation
        bpy.context.collection.objects.link(parent_obj)
        created_objects.append(parent_obj)

        bm_steps = bmesh.new()
        for i in range(step_count):
            start_ang = i * step_angle_rad
            z_b = i * step_height
            build_single_step(
                bm_steps,
                inner_r=inner_radius,
                outer_r=radius,
                start_angle=start_ang,
                angle_span=step_angle_span,
                z_base=z_b,
                thickness=step_thickness,
                nose_overhang=0.025,
                mat_idx=0
            )
        mesh_steps = bpy.data.meshes.new("Spiral_Stairs_Steps")
        bm_steps.to_mesh(mesh_steps)
        bm_steps.free()
        obj_steps = bpy.data.objects.new("Stairs_Steps", mesh_steps)
        obj_steps.data.materials.append(tread_mat)
        obj_steps.parent = parent_obj
        bpy.context.collection.objects.link(obj_steps)
        created_objects.append(obj_steps)

        if has_pillar:
            bm_pil = bmesh.new()
            build_center_pillar(bm_pil, inner_radius, total_height + 0.9, style=style, mat_idx=0)
            mesh_pil = bpy.data.meshes.new("Spiral_Stairs_Pillar")
            bm_pil.to_mesh(mesh_pil)
            bm_pil.free()
            obj_pil = bpy.data.objects.new("Stairs_Pillar", mesh_pil)
            obj_pil.data.materials.append(metal_mat if style != 'CASTLE_STONE' else tread_mat)
            obj_pil.parent = parent_obj
            bpy.context.collection.objects.link(obj_pil)
            created_objects.append(obj_pil)

        if has_handrail:
            bm_rail = bmesh.new()
            rail_r = radius - 0.05
            build_helical_handrail(
                bm_rail,
                radius=rail_r,
                step_height=step_height,
                step_angle_rad=step_angle_rad,
                total_steps=step_count,
                rail_height=0.90,
                rail_r_x=0.032,
                rail_r_z=0.024,
                mat_idx=0
            )
            for i in range(step_count):
                mid_ang = (i + 0.45) * step_angle_rad
                bx = rail_r * math.cos(mid_ang)
                by = rail_r * math.sin(mid_ang)
                z_bot = i * step_height + step_thickness
                z_top = (i + 0.45) * step_height + 0.90 - 0.024
                build_baluster(bm_rail, bx, by, z_bot, z_top, radius=0.014, style=baluster_style, mat_idx=0)

            mesh_rail = bpy.data.meshes.new("Spiral_Stairs_Handrail")
            bm_rail.to_mesh(mesh_rail)
            bm_rail.free()
            obj_rail = bpy.data.objects.new("Stairs_Handrail", mesh_rail)
            obj_rail.data.materials.append(metal_mat)
            obj_rail.parent = parent_obj
            bpy.context.collection.objects.link(obj_rail)
            created_objects.append(obj_rail)

    if created_objects:
        bpy.context.view_layer.objects.active = created_objects[0]
        created_objects[0].select_set(True)

    return created_objects
