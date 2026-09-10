import bpy
import bmesh
import math
import mathutils
from mathutils import Vector, Matrix, Euler
import random

# ==============================================================================
# 1. Procedural Noise & Voronoi Helpers (岩石断層・ファセット計算)
# ==============================================================================

def pseudo_noise_3d(x, y, z, seed=0):
    """Simple procedural pseudo-noise using trigonometric frequencies."""
    v = (
        math.sin(x * 0.45 + seed * 1.31) * math.cos(y * 0.38 + seed * 2.17) +
        math.sin(y * 0.85 + z * 0.73 + seed * 0.53) * 0.5 +
        math.cos(x * 1.73 + y * 1.61 + z * 1.22 + seed * 3.41) * 0.25 +
        math.sin(x * 3.81 - y * 3.19 + z * 2.71 + seed * 4.97) * 0.125
    )
    return v

def voronoi_cell_noise(x, y, cell_size=3.0, seed=0):
    """Grid-based 2D Voronoi F1 / F2 distance for sharp rock fissures and plateaus."""
    gx = x / cell_size
    gy = y / cell_size
    ix = math.floor(gx)
    iy = math.floor(gy)
    
    d1 = 999.0
    d2 = 999.0
    cell_id = 0.0

    for ox in (-1, 0, 1):
        for oy in (-1, 0, 1):
            cx = ix + ox
            cy = iy + oy
            # Pseudo-random point in cell
            h = math.sin(cx * 127.1 + cy * 311.7 + seed * 53.1) * 43758.5453
            h = h - math.floor(h)
            h2 = math.sin(cx * 269.5 + cy * 183.3 + seed * 19.7) * 43758.5453
            h2 = h2 - math.floor(h2)
            
            px = cx + h
            py = cy + h2
            dist = math.sqrt((gx - px)**2 + (gy - py)**2)
            
            if dist < d1:
                d2 = d1
                d1 = dist
                cell_id = h
            elif dist < d2:
                d2 = dist

    # Sharp ledge feature (F2 - F1)
    fissure = d2 - d1
    return d1, fissure, cell_id


# ==============================================================================
# 2. Cave Centerline / River Path (蛇行曲線パス)
# ==============================================================================

def get_cave_center_x(y, length=35.0, seed=0):
    """Calculates the S-curve horizontal deviation at coordinate y."""
    rng = random.Random(seed)
    ph1 = rng.uniform(0, 6.28)
    ph2 = rng.uniform(0, 6.28)
    freq1 = 2.2 * math.pi / max(10.0, length)
    freq2 = 4.5 * math.pi / max(10.0, length)
    
    x = math.sin(y * freq1 + ph1) * 3.5 + math.sin(y * freq2 + ph2) * 1.2
    return x


# ==============================================================================
# 3. Terraced Cave Floor BMesh Builder (新・岩棚テラス＆水流トレンチ床面)
# ==============================================================================

def build_terraced_cave_floor_bmesh(
    width=18.0,
    length=35.0,
    has_river=True,
    river_width=4.0,
    river_depth=1.4,
    terrace_steps=4,
    step_height=0.6,
    roughness=0.8,
    seed=0,
    subdivisions_x=64,
    subdivisions_y=80
):
    """
    Creates a realistic natural cave floor featuring:
    - Central meandering river gorge (if has_river=True)
    - Terraced rock ledges (walkable flat plateaus with sharp cliff edges)
    - Voronoi fractured slabs and faceted rock strata
    """
    bm = bmesh.new()

    hx = width * 0.5
    hy = length * 0.5
    
    dx = width / float(subdivisions_x)
    dy = length / float(subdivisions_y)

    grid_verts = []

    # 1. Create Grid Vertices with Procedural Heights
    for iy in range(subdivisions_y + 1):
        y_pos = -hy + iy * dy
        center_x = get_cave_center_x(y_pos, length=length, seed=seed)
        row = []

        for ix in range(subdivisions_x + 1):
            x_pos = -hx + ix * dx
            
            # Distance from cave/river center
            dist_to_center = abs(x_pos - center_x)
            norm_dist = dist_to_center / (hx * 0.85)
            
            # Base canyon slope: sides rise up towards cave walls
            base_z = (norm_dist ** 1.8) * (terrace_steps * step_height)

            # River trench (carve valley at the center)
            in_river = False
            river_factor = 0.0
            if has_river:
                half_rw = river_width * 0.5
                if dist_to_center < half_rw:
                    in_river = True
                    # Smooth valley profile (quadratic bowl with flat riverbed)
                    t = dist_to_center / half_rw
                    # Trench profile: deep at center, steep banks
                    depth_curve = math.cos(t * math.pi * 0.5) ** 1.5
                    base_z -= river_depth * depth_curve
                    river_factor = 1.0 - t
                elif dist_to_center < half_rw + 1.2:
                    # Steep bank transition
                    t_bank = (dist_to_center - half_rw) / 1.2
                    base_z -= river_depth * (1.0 - t_bank) * 0.25

            # 2. Rock Terraces (Step quantization for flat walkable ledges)
            if not in_river:
                # Quantize height into discrete terraces
                step_val = base_z / step_height
                stepped_z = math.floor(step_val) * step_height
                frac = step_val - math.floor(step_val)
                # S-curve smoothstep for vertical cliff edges between terraces
                cliff_blend = frac ** 3 * (frac * (frac * 6 - 15) + 10)
                terrace_z = stepped_z + cliff_blend * step_height
                # Blend with base to preserve organic slope
                z_final = terrace_z * 0.7 + base_z * 0.3
            else:
                z_final = base_z

            # 3. Voronoi Rock Fissures & Faceting (Sharp rock slabs)
            d1, fissure, cell_id = voronoi_cell_noise(x_pos, y_pos, cell_size=2.8, seed=seed)
            slab_offset = (cell_id - 0.5) * 0.45 * roughness
            crack_indent = (1.0 - min(1.0, fissure * 3.5)) * -0.35 * roughness

            # 4. Multi-frequency Micro Roughness
            micro_noise = pseudo_noise_3d(x_pos * 0.8, y_pos * 0.8, z_final, seed=seed) * 0.3 * roughness

            # Combine all height layers
            z_total = z_final + slab_offset + crack_indent + micro_noise

            # Slight horizontal jitter for non-grid natural rock feel
            jx = (math.sin(x_pos * 1.7 + y_pos * 2.3 + seed) * 0.15) * roughness
            jy = (math.cos(x_pos * 2.1 - y_pos * 1.8 + seed) * 0.15) * roughness

            vert = bm.verts.new((x_pos + jx, y_pos + jy, z_total))
            row.append((vert, river_factor))

        grid_verts.append(row)

    bm.verts.ensure_lookup_table()

    # 2. Create Faces
    for iy in range(subdivisions_y):
        for ix in range(subdivisions_x):
            v1 = grid_verts[iy][ix][0]
            v2 = grid_verts[iy][ix + 1][0]
            v3 = grid_verts[iy + 1][ix + 1][0]
            v4 = grid_verts[iy + 1][ix][0]
            try:
                bm.faces.new((v1, v2, v3, v4))
            except ValueError:
                pass

    bm.faces.ensure_lookup_table()
    bm.normal_update()

    # Smooth shading
    for f in bm.faces:
        f.smooth = True

    return bm


# ==============================================================================
# 4. Cave River Water Strip Builder (水面メッシュ生成)
# ==============================================================================

def build_cave_water_bmesh(
    length=35.0,
    river_width=4.0,
    water_level=-0.35,
    seed=0,
    segments_y=60,
    segments_x=8
):
    """Creates a flowing river water surface mesh embedded in the cave trench."""
    bm = bmesh.new()

    hy = length * 0.5
    dy = length / float(segments_y)
    # Expand slightly wider than riverbed so edges intersect rock banks cleanly
    w_effective = river_width * 1.15
    dx = w_effective / float(segments_x)

    water_verts = []

    for iy in range(segments_y + 1):
        y_pos = -hy + iy * dy
        center_x = get_cave_center_x(y_pos, length=length, seed=seed)
        row = []

        for ix in range(segments_x + 1):
            offset_x = (-w_effective * 0.5) + ix * dx
            x_pos = center_x + offset_x
            
            # Subtle gentle water ripple displacement
            wave = (
                math.sin(y_pos * 1.5 + x_pos * 0.8) * 0.02 +
                math.cos(y_pos * 3.2 - x_pos * 1.4) * 0.01
            )
            z_pos = water_level + wave

            v = bm.verts.new((x_pos, y_pos, z_pos))
            row.append(v)
        water_verts.append(row)

    bm.verts.ensure_lookup_table()

    for iy in range(segments_y):
        for ix in range(segments_x):
            v1 = water_verts[iy][ix]
            v2 = water_verts[iy][ix + 1]
            v3 = water_verts[iy + 1][ix + 1]
            v4 = water_verts[iy + 1][ix]
            try:
                bm.faces.new((v1, v2, v3, v4))
            except ValueError:
                pass

    bm.faces.ensure_lookup_table()
    bm.normal_update()
    for f in bm.faces:
        f.smooth = True

    return bm


# ==============================================================================
# 5. PBR Materials (濡れ岩・地層スラブ・クリア流水マテリアル)
# ==============================================================================

def get_or_create_cave_floor_material(mat_name="Cave_Floor_Terrace_Mat", has_river=True):
    """Creates procedural PBR material for terraced cave rock with wet shoreline."""
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    tree = mat.node_tree
    nodes = tree.nodes
    links = tree.links
    nodes.clear()

    coord = nodes.new(type='ShaderNodeTexCoord')
    coord.location = (-1200, 200)

    # 1. Base Rock Texture (Noise)
    rock_noise = nodes.new(type='ShaderNodeTexNoise')
    rock_noise.location = (-950, 300)
    rock_noise.inputs['Scale'].default_value = 5.0
    rock_noise.inputs['Detail'].default_value = 8.0
    rock_noise.inputs['Roughness'].default_value = 0.65
    links.new(coord.outputs['Object'], rock_noise.inputs['Vector'])

    # 2. Strata / Layering Texture (Wave texture for horizontal rock bands)
    strata_wave = nodes.new(type='ShaderNodeTexWave')
    strata_wave.location = (-950, 50)
    strata_wave.wave_type = 'BANDS'
    strata_wave.bands_direction = 'Z'
    strata_wave.inputs['Scale'].default_value = 2.5
    strata_wave.inputs['Distortion'].default_value = 4.0
    strata_wave.inputs['Detail'].default_value = 5.0
    links.new(coord.outputs['Object'], strata_wave.inputs['Vector'])

    # Color Ramp for Rock Tone
    ramp_rock = nodes.new(type='ShaderNodeValToRGB')
    ramp_rock.location = (-650, 250)
    ramp_rock.color_ramp.elements[0].position = 0.15
    ramp_rock.color_ramp.elements[0].color = (0.04, 0.04, 0.045, 1.0)
    ramp_rock.color_ramp.elements[1].position = 0.85
    ramp_rock.color_ramp.elements[1].color = (0.16, 0.14, 0.12, 1.0)
    links.new(rock_noise.outputs['Fac'], ramp_rock.inputs['Fac'])

    # Wetness Mask (Height-based)
    sep_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
    sep_xyz.location = (-950, -450)
    links.new(coord.outputs['Object'], sep_xyz.inputs['Vector'])

    ramp_wet = nodes.new(type='ShaderNodeValToRGB')
    ramp_wet.location = (-650, -450)
    ramp_wet.color_ramp.elements[0].position = 0.25
    ramp_wet.color_ramp.elements[0].color = (1.0, 1.0, 1.0, 1.0) # Wet
    ramp_wet.color_ramp.elements[1].position = 0.60
    ramp_wet.color_ramp.elements[1].color = (0.0, 0.0, 0.0, 1.0) # Dry
    links.new(sep_xyz.outputs['Z'], ramp_wet.inputs['Fac'])

    # Darker wet color helper
    dark_wet = nodes.new(type='ShaderNodeMix')
    dark_wet.location = (-450, -100)
    dark_wet.data_type = 'RGBA'
    # Factor is input 0
    dark_wet.inputs[0].default_value = 0.65
    # Color A is input 6, Color B is input 7
    links.new(ramp_rock.outputs['Color'], dark_wet.inputs[6])
    dark_wet.inputs[7].default_value = (0.01, 0.015, 0.02, 1.0)

    # Mix Color (Dry vs Wet)
    mix_color = nodes.new(type='ShaderNodeMix')
    mix_color.location = (-200, 150)
    mix_color.data_type = 'RGBA'
    if has_river:
        links.new(ramp_wet.outputs['Color'], mix_color.inputs[0])
    else:
        mix_color.inputs[0].default_value = 0.0
    links.new(ramp_rock.outputs['Color'], mix_color.inputs[6])
    # dark_wet output color is output 2
    links.new(dark_wet.outputs[2], mix_color.inputs[7])

    # Bump Map
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (-200, -250)
    bump.inputs['Strength'].default_value = 0.45
    bump.inputs['Distance'].default_value = 0.15
    links.new(rock_noise.outputs['Fac'], bump.inputs['Height'])

    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (100, 100)
    links.new(mix_color.outputs[2], bsdf.inputs['Base Color'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    # Roughness
    if has_river:
        rough_mix = nodes.new(type='ShaderNodeMix')
        rough_mix.location = (-50, -150)
        rough_mix.data_type = 'FLOAT'
        links.new(ramp_wet.outputs['Color'], rough_mix.inputs[0])
        rough_mix.inputs[2].default_value = 0.82 # A (Dry)
        rough_mix.inputs[3].default_value = 0.12 # B (Wet glossy)
        links.new(rough_mix.outputs[0], bsdf.inputs['Roughness'])
    else:
        bsdf.inputs['Roughness'].default_value = 0.85

    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 100)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat


def get_or_create_cave_water_material(mat_name="Cave_Water_Mat"):
    """Creates clear, reflective cave river water with subtle caustics/ripples."""
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    tree = mat.node_tree
    nodes = tree.nodes
    links = tree.links
    nodes.clear()

    coord = nodes.new(type='ShaderNodeTexCoord')
    coord.location = (-800, 100)

    # Wave texture for water ripples
    wave = nodes.new(type='ShaderNodeTexWave')
    wave.location = (-550, 100)
    wave.wave_type = 'RINGS'
    wave.inputs['Scale'].default_value = 4.0
    wave.inputs['Distortion'].default_value = 8.0
    wave.inputs['Detail'].default_value = 4.0
    links.new(coord.outputs['Object'], wave.inputs['Vector'])

    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (-250, 0)
    bump.inputs['Strength'].default_value = 0.08
    bump.inputs['Distance'].default_value = 0.05
    links.new(wave.outputs['Fac'], bump.inputs['Height'])

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 100)
    # Deep clear turquoise tint
    bsdf.inputs['Base Color'].default_value = (0.02, 0.12, 0.15, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.03
    bsdf.inputs['IOR'].default_value = 1.333
    bsdf.inputs['Transmission'].default_value = 0.95
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (250, 100)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    # EEVEE settings for refraction/transparency
    mat.blend_method = 'BLEND'
    mat.shadow_method = 'HASHED'

    return mat


# ==============================================================================
# 6. Main Procedural Cave Scene Builder (Step 1 統合)
# ==============================================================================


# ==============================================================================
# 5. Overhanging Cliff & Ceiling Arch BMesh Builder (新・断崖側壁＆天井岩盤アーチ)
# ==============================================================================

def build_cliff_ceiling_bmesh(
    width=18.0,
    length=35.0,
    ceiling_height=6.5,
    overhang=0.85,
    fissure_width=0.3,
    roughness=0.9,
    seed=0,
    subdivisions_arc=40,
    subdivisions_y=80
):
    """
    Creates realistic vertical cliff walls and overhanging rock slabs that arch overhead.
    Features:
    - Vertical layered rock strata on the walls
    - Cantilevered overhanging slabs meeting near the ceiling centerline
    - Central fissure/aperture for dramatic overhead sky lighting
    - Voronoi faceted slabs (no smooth worm-like shapes)
    """
    bm = bmesh.new()

    hx = width * 0.5
    hy = length * 0.5
    dy = length / float(subdivisions_y)

    # Cross-section profile:
    # We parameterize the arch from left floor wall (u=0.0) up to ceiling and down to right floor wall (u=1.0)
    # u in [0, 0.5] is left wall + left ceiling
    # u in [0.5, 1.0] is right ceiling + right wall
    
    grid_verts = []

    for iy in range(subdivisions_y + 1):
        y_pos = -hy + iy * dy
        center_x = get_cave_center_x(y_pos, length=length, seed=seed)
        row = []

        for iu in range(subdivisions_arc + 1):
            u = iu / float(subdivisions_arc)  # 0.0 to 1.0
            
            # Map u to arch coordinates (x_rel, z_base)
            # Left wall (u < 0.25): rises vertically from floor edge
            # Left ceiling (0.25 <= u < 0.5): arches inward towards center
            # Right ceiling (0.5 <= u < 0.75): arches outward
            # Right wall (u >= 0.75): descends vertically to right floor edge
            
            if u < 0.25:
                # Left vertical cliff
                t = u / 0.25
                x_rel = -hx * (1.0 - t * 0.15)
                z_base = t * (ceiling_height * 0.55)
            elif u < 0.5:
                # Left ceiling overhang
                t = (u - 0.25) / 0.25
                # Inward overhang
                x_rel = -hx * 0.85 + t * (hx * 0.85 - fissure_width * 0.5) * overhang
                # Arch up to ceiling height
                arch_t = math.sin(t * math.pi * 0.5)
                z_base = ceiling_height * (0.55 + arch_t * 0.45)
            elif u < 0.75:
                # Right ceiling overhang
                t = (u - 0.5) / 0.25
                x_rel = (fissure_width * 0.5) + t * (hx * 0.85 - fissure_width * 0.5) * overhang
                # Arch down from ceiling height
                arch_t = math.cos(t * math.pi * 0.5)
                z_base = ceiling_height * (0.55 + arch_t * 0.45)
            else:
                # Right vertical cliff
                t = (u - 0.75) / 0.25
                x_rel = hx * (0.85 + t * 0.15)
                z_base = (1.0 - t) * (ceiling_height * 0.55)

            # World X position following cave centerline
            x_pos = center_x + x_rel

            # Voronoi Faceted Rock Slabs (Just The Basics & Kev Binge approach)
            d1, fissure_val, cell_id = voronoi_cell_noise(x_pos, y_pos + z_base * 0.5, cell_size=2.6, seed=seed + 77)
            slab_disp = (cell_id - 0.5) * 0.55 * roughness
            crack_indent = (1.0 - min(1.0, fissure_val * 3.5)) * -0.4 * roughness

            # Horizontal strata steps (Z quantization on walls)
            strata_step = 0.55
            z_quant = math.floor(z_base / strata_step) * strata_step
            z_frac = (z_base / strata_step) - math.floor(z_base / strata_step)
            cliff_blend = z_frac ** 3 * (z_frac * (z_frac * 6 - 15) + 10)
            z_strata = z_quant + cliff_blend * strata_step
            z_final = z_base * 0.5 + z_strata * 0.5

            # Micro roughness
            micro = pseudo_noise_3d(x_pos * 0.7, y_pos * 0.7, z_final * 0.9, seed=seed + 99) * 0.35 * roughness

            # Inward/Outward displacement based on wall normal
            norm_sign = -1.0 if x_rel < 0 else 1.0
            x_disp = norm_sign * (slab_disp + crack_indent) * 0.7
            z_disp = slab_disp + micro

            vert = bm.verts.new((x_pos + x_disp, y_pos, z_final + z_disp))
            row.append(vert)

        grid_verts.append(row)

    bm.verts.ensure_lookup_table()

    # Create Faces
    for iy in range(subdivisions_y):
        for iu in range(subdivisions_arc):
            v1 = grid_verts[iy][iu]
            v2 = grid_verts[iy][iu + 1]
            v3 = grid_verts[iy + 1][iu + 1]
            v4 = grid_verts[iy + 1][iu]
            try:
                bm.faces.new((v1, v2, v3, v4))
            except ValueError:
                pass

    bm.faces.ensure_lookup_table()
    bm.normal_update()

    # Smooth shading
    for f in bm.faces:
        f.smooth = True

    return bm


def get_or_create_cave_ceiling_material(mat_name="Cave_Ceiling_Cliff_Mat"):
    """Creates procedural PBR material for dry, rough cliff walls and ceiling slabs."""
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    tree = mat.node_tree
    nodes = tree.nodes
    links = tree.links
    nodes.clear()

    coord = nodes.new(type='ShaderNodeTexCoord')
    coord.location = (-1000, 100)

    # Base Rock Noise
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-750, 200)
    noise.inputs['Scale'].default_value = 5.5
    noise.inputs['Detail'].default_value = 9.0
    noise.inputs['Roughness'].default_value = 0.68
    links.new(coord.outputs['Object'], noise.inputs['Vector'])

    # Horizontal Strata Banding
    strata = nodes.new(type='ShaderNodeTexWave')
    strata.location = (-750, -50)
    strata.wave_type = 'BANDS'
    strata.bands_direction = 'Z'
    strata.inputs['Scale'].default_value = 2.8
    strata.inputs['Distortion'].default_value = 4.2
    strata.inputs['Detail'].default_value = 6.0
    links.new(coord.outputs['Object'], strata.inputs['Vector'])

    # Color Ramp for Dry Cliff Stone
    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.location = (-450, 150)
    ramp.color_ramp.elements[0].position = 0.2
    ramp.color_ramp.elements[0].color = (0.05, 0.05, 0.055, 1.0)
    ramp.color_ramp.elements[1].position = 0.8
    ramp.color_ramp.elements[1].color = (0.18, 0.16, 0.14, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])

    # Bump Map
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (-200, -100)
    bump.inputs['Strength'].default_value = 0.55
    bump.inputs['Distance'].default_value = 0.18
    links.new(noise.outputs['Fac'], bump.inputs['Height'])

    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (100, 100)
    bsdf.inputs['Roughness'].default_value = 0.86
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 100)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat


def create_procedural_cave_scene(
    context,
    name="Cave",
    seed=0,
    has_river=True,
    floor_width=18.0,
    floor_length=35.0,
    river_width=4.5,
    river_depth=1.3,
    terrace_steps=4,
    step_height=0.6,
    roughness=0.8,
    ceiling_height=6.5,
    ceiling_overhang=0.85,
    ceiling_fissure=0.3,
    ceiling_roughness=0.9,
    generate_ceiling=True,
    target_obj=None,
    **kwargs
):
    """
    Main entry point for Cave System (Step 1 & Step 2).
    Builds:
    - Terraced rock floor with voronoi slabs
    - Optional river trench with water mesh
    - Vertical cliff walls and overhanging ceiling arch (separate object)
    """
    col = context.collection

    # 1. Build Floor BMesh
    bm_floor = build_terraced_cave_floor_bmesh(
        width=floor_width,
        length=floor_length,
        has_river=has_river,
        river_width=river_width,
        river_depth=river_depth,
        terrace_steps=terrace_steps,
        step_height=step_height,
        roughness=roughness,
        seed=seed
    )

    floor_obj_name = name + "_Floor"
    floor_obj = bpy.data.objects.get(floor_obj_name)
    if floor_obj and floor_obj.type == 'MESH':
        bm_floor.to_mesh(floor_obj.data)
        floor_obj.data.update()
    else:
        mesh_floor = bpy.data.meshes.new(floor_obj_name)
        bm_floor.to_mesh(mesh_floor)
        floor_obj = bpy.data.objects.new(floor_obj_name, mesh_floor)
        col.objects.link(floor_obj)

    bm_floor.free()

    mat_floor = get_or_create_cave_floor_material(name + "_Floor_Mat", has_river=has_river)
    if floor_obj.data.materials:
        floor_obj.data.materials[0] = mat_floor
    else:
        floor_obj.data.materials.append(mat_floor)

    # 2. Handle River Water Mesh
    water_obj_name = name + "_Water"
    water_obj = bpy.data.objects.get(water_obj_name)

    if has_river:
        bm_water = build_cave_water_bmesh(
            length=floor_length,
            river_width=river_width,
            water_level=-river_depth * 0.45,
            seed=seed
        )
        if water_obj and water_obj.type == 'MESH':
            bm_water.to_mesh(water_obj.data)
            water_obj.data.update()
            water_obj.hide_viewport = False
            water_obj.hide_render = False
        else:
            mesh_water = bpy.data.meshes.new(water_obj_name)
            bm_water.to_mesh(mesh_water)
            water_obj = bpy.data.objects.new(water_obj_name, mesh_water)
            col.objects.link(water_obj)

        bm_water.free()

        mat_water = get_or_create_cave_water_material(name + "_Water_Mat")
        if water_obj.data.materials:
            water_obj.data.materials[0] = mat_water
        else:
            water_obj.data.materials.append(mat_water)
    else:
        if water_obj:
            bpy.data.objects.remove(water_obj, do_unlink=True)
            water_obj = None

    # 3. Handle Ceiling & Cliff Walls Mesh (Step 2)
    ceiling_obj_name = name + "_Ceiling"
    ceiling_obj = bpy.data.objects.get(ceiling_obj_name)

    if generate_ceiling:
        bm_ceiling = build_cliff_ceiling_bmesh(
            width=floor_width,
            length=floor_length,
            ceiling_height=ceiling_height,
            overhang=ceiling_overhang,
            fissure_width=ceiling_fissure,
            roughness=ceiling_roughness,
            seed=seed
        )
        if ceiling_obj and ceiling_obj.type == 'MESH':
            bm_ceiling.to_mesh(ceiling_obj.data)
            ceiling_obj.data.update()
        else:
            mesh_ceiling = bpy.data.meshes.new(ceiling_obj_name)
            bm_ceiling.to_mesh(mesh_ceiling)
            ceiling_obj = bpy.data.objects.new(ceiling_obj_name, mesh_ceiling)
            col.objects.link(ceiling_obj)

        bm_ceiling.free()

        mat_ceiling = get_or_create_cave_ceiling_material(name + "_Ceiling_Mat")
        if ceiling_obj.data.materials:
            ceiling_obj.data.materials[0] = mat_ceiling
        else:
            ceiling_obj.data.materials.append(mat_ceiling)
    else:
        if ceiling_obj:
            bpy.data.objects.remove(ceiling_obj, do_unlink=True)
            ceiling_obj = None

    context.view_layer.objects.active = floor_obj
    floor_obj.select_set(True)

    return floor_obj, water_obj, ceiling_obj