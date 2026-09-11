import bpy
import bmesh
import math
import mathutils
from mathutils import Vector, Matrix, Euler
import random
from .rock_gen import build_convex_hull_rock

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

def get_cave_profile_at_y(y, length=35.0, path_type='S_CURVE', seed=0):
    """
    Calculates dynamic horizontal deviation (center_x), width scale (width_mult),
    and ceiling height scale (height_mult) at longitudinal coordinate y.
    Prevents repetitive worm-like identical widths.
    """
    rng = random.Random(seed)
    ph1 = rng.uniform(0, 6.28)
    ph2 = rng.uniform(0, 6.28)
    
    t = (y / (length * 0.5)) * 0.5  # -0.5 to +0.5
    dist_from_center = abs(t) # 0.0 at center, 0.5 at ends

    # 1. Path Horizontal Deviation
    if path_type == 'STRAIGHT':
        # Mostly straight with subtle natural rock meandering
        center_x = math.sin(y * 0.15 + ph1) * 0.8 + math.sin(y * 0.4 + ph2) * 0.4
    elif path_type == 'Z_CRANK':
        # Sharp angular turns like a defensive gorge or tectonic fracture
        k = math.tanh(t * 6.0) # Sharp S transition
        center_x = k * 7.5 + math.sin(y * 0.3 + ph1) * 1.0
    elif path_type == 'CHAMBER_HALL':
        # Gentle curve entering a grand central cavern
        center_x = math.sin(t * math.pi) * 3.0 + math.sin(y * 0.3 + ph1) * 0.8
    else: # S_CURVE or default
        freq1 = 2.2 * math.pi / max(10.0, length)
        freq2 = 4.5 * math.pi / max(10.0, length)
        center_x = math.sin(y * freq1 + ph1) * 4.0 + math.sin(y * freq2 + ph2) * 1.5

    # 2. Dynamic Width Modulation (Pinching bottlenecks vs Grand expansions)
    # Natural breathing variation:
    natural_pinch = 1.0 + math.sin(y * 0.35 + ph1) * 0.25 + math.cos(y * 0.7 + ph2) * 0.15
    
    if path_type == 'CHAMBER_HALL':
        # Central cavern expands up to 2.2x wide, with narrow entrance/exit (0.7x)
        if dist_from_center < 0.35:
            chamber_bell = math.cos((dist_from_center / 0.35) * math.pi * 0.5) ** 1.5
            width_mult = (0.75 + chamber_bell * 1.35) * natural_pinch
            height_mult = 1.0 + chamber_bell * 0.85 # Ceiling arches up in the dome
        else:
            width_mult = 0.75 * natural_pinch
            height_mult = 0.9
    elif path_type == 'Z_CRANK':
        # Narrow choke points at the corners, wider in between
        width_mult = natural_pinch * (0.85 + math.cos(t * math.pi * 2.0) * 0.3)
        height_mult = 1.0 + math.sin(y * 0.2 + ph1) * 0.2
    else:
        width_mult = natural_pinch
        height_mult = 1.0 + math.sin(y * 0.2 + ph1) * 0.15

    # Clamp safety
    width_mult = max(0.45, min(2.5, width_mult))
    height_mult = max(0.65, min(2.2, height_mult))

    return center_x, width_mult, height_mult

def get_cave_center_x(y, length=35.0, seed=0):
    """Backward-compatible helper returning center_x."""
    cx, _, _ = get_cave_profile_at_y(y, length=length, path_type='S_CURVE', seed=seed)
    return cx



# ==============================================================================
# 3. Terraced Cave Floor BMesh Builder (新・岩棚テラス＆水流トレンチ床面)
# ==============================================================================

def build_terraced_cave_floor_bmesh(
    width=18.0,
    length=35.0,
    path_type='S_CURVE',
    has_river=True,
    river_width=4.0,
    river_depth=1.4,
    terrace_steps=4,
    step_height=0.6,
    roughness=0.8,
    seed=0,
    subdivisions_x=64,
    subdivisions_y=80,
    puddle_locations=None
):
    """
    Creates a realistic natural cave floor featuring:
    - Central meandering river gorge (if has_river=True)
    - Terraced rock ledges (walkable flat plateaus with clean cliff edges, NO sinusoidal ripple artifacts)
    - Clean hollowed depressions for natural puddle basins
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
        center_x, w_mult, h_mult = get_cave_profile_at_y(y_pos, length=length, path_type=path_type, seed=seed)
        effective_hx = hx * w_mult
        effective_dx = (effective_hx * 2.0) / float(subdivisions_x)
        effective_rw = river_width * (0.65 + w_mult * 0.35)
        row = []

        for ix in range(subdivisions_x + 1):
            offset_x = -effective_hx + ix * effective_dx
            x_pos = center_x + offset_x
            
            # Distance from cave/river center (strictly relative to cave centerline)
            dist_to_center = abs(offset_x)
            norm_dist = min(1.3, dist_to_center / max(1.0, effective_hx * 0.85))
            
            # Base canyon slope: continuous smooth curve rising up towards cave walls
            base_z = (norm_dist ** 1.45) * 1.5

            # River trench (carve valley at the center)
            in_river = False
            river_factor = 0.0
            if has_river:
                half_rw = effective_rw * 0.5
                if dist_to_center < half_rw:
                    in_river = True
                    t = dist_to_center / half_rw
                    depth_curve = math.cos(t * math.pi * 0.5) ** 1.5
                    base_z -= river_depth * depth_curve
                    river_factor = 1.0 - t
                elif dist_to_center < half_rw + 1.2:
                    t_bank = (dist_to_center - half_rw) / 1.2
                    base_z -= river_depth * (1.0 - t_bank) * 0.25

            # 2. Localized Subtle Rock Ledges (Smooth Hermite blend, only in certain zones)
            if not in_river:
                shelf_noise = pseudo_noise_3d(x_pos * 0.15, y_pos * 0.15, 0.0, seed=seed + 77) * 0.5 + 0.5
                terrace_blend = 0.12 + shelf_noise * 0.18 # 12~30% subtle plateau, mostly continuous smooth slope
                step_val = base_z / step_height
                stepped_z = math.floor(step_val) * step_height
                frac = step_val - math.floor(step_val)
                cliff_blend = frac ** 2 * (3.0 - 2.0 * frac) # Smoothstep Hermite
                terrace_z = stepped_z + cliff_blend * step_height
                z_final = base_z * (1.0 - terrace_blend) + terrace_z * terrace_blend
            else:
                z_final = base_z

            # 3. Carve Natural Hollow Basins for Puddles (Depressions into rock)
            if puddle_locations:
                for (px_p, py_p, pz_p, p_rad_p, aspect_p, rot_p) in puddle_locations:
                    dx_p = x_pos - px_p
                    dy_p = y_pos - py_p
                    cos_r = math.cos(-rot_p)
                    sin_r = math.sin(-rot_p)
                    lx = dx_p * cos_r - dy_p * sin_r
                    ly = (dx_p * sin_r + dy_p * cos_r) / max(0.1, aspect_p)
                    dist_p = math.sqrt(lx**2 + ly**2)
                    rim_outer = p_rad_p * 1.35
                    rim_inner = p_rad_p * 0.95
                    if dist_p < rim_outer:
                        if dist_p < rim_inner:
                            # Bowl basin depression (hollow inside)
                            t_bowl = dist_p / rim_inner
                            # Deepest at center (-0.22m), smoothly rising up
                            bowl_drop = (1.0 - t_bowl ** 2) * 0.22
                            z_final -= bowl_drop
                        else:
                            # Natural rimstone lip (slight raised edge holding the water)
                            t_lip = (dist_p - rim_inner) / (rim_outer - rim_inner)
                            lip_height = math.sin(t_lip * math.pi) * 0.07
                            z_final += lip_height

            # 4. Organic Rock Slabs (Natural multi-scale noise, NO geometric Voronoi grid cracks)
            macro_noise = pseudo_noise_3d(x_pos * 0.35, y_pos * 0.35, 0.0, seed=seed + 101) * 0.18 * roughness
            micro_noise = pseudo_noise_3d(x_pos * 1.25, y_pos * 1.25, 0.0, seed=seed + 202) * 0.06 * roughness
            z_total = z_final + macro_noise + micro_noise

            vert = bm.verts.new((x_pos, y_pos, z_total))
            row.append((vert, river_factor))

        grid_verts.append(row)

    bm.verts.ensure_lookup_table()

    # 2. Create Faces for Surface Grid
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

    # 3. Diorama Solid Base (Skirts and Bottom Slab)
    # Extrude perimeter edges downward to Z = -1.2m to give earth/rock thickness
    base_bottom_z = -1.2
    
    # Boundary vertex rings:
    # Bottom edge (iy = 0): ix from 0 to subdivisions_x
    # Right edge (ix = subdivisions_x): iy from 0 to subdivisions_y
    # Top edge (iy = subdivisions_y): ix from subdivisions_x down to 0
    # Left edge (ix = 0): iy from subdivisions_y down to 0
    boundary_top_verts = []
    for ix in range(subdivisions_x):
        boundary_top_verts.append(grid_verts[0][ix][0])
    for iy in range(subdivisions_y):
        boundary_top_verts.append(grid_verts[iy][subdivisions_x][0])
    for ix in range(subdivisions_x, 0, -1):
        boundary_top_verts.append(grid_verts[subdivisions_y][ix][0])
    for iy in range(subdivisions_y, 0, -1):
        boundary_top_verts.append(grid_verts[iy][0][0])

    # Create corresponding bottom perimeter vertices
    boundary_bot_verts = []
    for bv in boundary_top_verts:
        bot_v = bm.verts.new((bv.co.x, bv.co.y, base_bottom_z))
        boundary_bot_verts.append(bot_v)

    bm.verts.ensure_lookup_table()

    # Create skirt wall faces
    num_b = len(boundary_top_verts)
    for i in range(num_b):
        i_next = (i + 1) % num_b
        t1 = boundary_top_verts[i]
        t2 = boundary_top_verts[i_next]
        b1 = boundary_bot_verts[i]
        b2 = boundary_bot_verts[i_next]
        try:
            bm.faces.new((t1, t2, b2, b1))
        except ValueError:
            pass

    # Create bottom cap face (fan from center or polygon)
    center_bot = bm.verts.new((0.0, 0.0, base_bottom_z))
    for i in range(num_b):
        i_next = (i + 1) % num_b
        b1 = boundary_bot_verts[i]
        b2 = boundary_bot_verts[i_next]
        try:
            bm.faces.new((center_bot, b2, b1)) # Normal facing downward
        except ValueError:
            pass

    bm.faces.ensure_lookup_table()
    bm.normal_update()

    for f in bm.faces:
        f.smooth = True

    return bm


# ==============================================================================
# 4. Cave River Water Strip Builder (水面メッシュ生成)
# ==============================================================================

def build_cave_water_bmesh(
    length=35.0,
    river_width=4.0,
    path_type='S_CURVE',
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
        center_x, w_mult, _ = get_cave_profile_at_y(y_pos, length=length, path_type=path_type, seed=seed)
        effective_rw = river_width * (0.65 + w_mult * 0.35)
        curr_w_effective = effective_rw * 1.15
        curr_dx = curr_w_effective / float(segments_x)
        row = []

        for ix in range(segments_x + 1):
            offset_x = (-curr_w_effective * 0.5) + ix * curr_dx
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


def get_cave_puddle_locations(
    width=18.0,
    length=35.0,
    path_type='S_CURVE',
    terrace_steps=4,
    step_height=0.6,
    puddle_count=6,
    puddle_scale=2.4,
    seed=0
):
    """
    Calculates deterministic center coordinates (px, py, pz, radius, aspect, rot)
    shared between floor basin carving and water surface generation.
    Places puddles naturally along the gentle slope hollows, perfectly level with carved basins.
    """
    if puddle_count <= 0:
        return []

    locations = []
    rng = random.Random(seed + 9999)
    y_range = length * 0.72
    y_start = -y_range * 0.5
    y_step = y_range / float(max(1, puddle_count))

    for i in range(puddle_count):
        py = y_start + (i + 0.5) * y_step + rng.uniform(-length * 0.04, length * 0.04)
        cx, wm, _ = get_cave_profile_at_y(py, length=length, path_type=path_type, seed=seed)
        eff_hx = (width * 0.5) * wm

        # Alternate left and right ledges with organic scatter
        side = 1.0 if (i % 2 == 0) else -1.0
        dist_ratio = rng.uniform(0.18, 0.62)
        offset_x = side * (dist_ratio * eff_hx * 0.85)
        px = cx + offset_x
        norm_dist = dist_ratio

        # Continuous smooth slope height at this position
        ground_z = (norm_dist ** 1.45) * 1.5
        puddle_z = ground_z - 0.04 # Snugly seated 4cm below lip

        max_rad = (eff_hx * 0.28)
        p_rad = min(max_rad, puddle_scale * 0.42) * rng.uniform(0.85, 1.15)
        aspect = rng.uniform(0.80, 1.30)
        rot = rng.uniform(0, math.pi * 2.0)

        locations.append((px, py, puddle_z, p_rad, aspect, rot))

    return locations


def build_cave_puddles_bmesh(puddle_locations=None):
    """
    Creates organic water puddle meshes neatly embedded inside carved rock basins.
    Each puddle sits flush below the terrace ledge, preventing any floating paper look.
    """
    bm = bmesh.new()
    if not puddle_locations:
        return bm

    for i, (px, py, puddle_z, p_rad, aspect, rot) in enumerate(puddle_locations):
        segments = 24
        rings = 3

        ring_verts = []
        center_v = bm.verts.new((px, py, puddle_z))
        water_scale = 0.94

        for r in range(1, rings + 1):
            t_r = r / float(rings)
            current_verts = []
            for s in range(segments):
                ang = s * (2.0 * math.pi / segments)
                # Gentle natural oval lobe
                lobe = 1.0 + 0.10 * math.cos(ang * 3.0 + i) + 0.05 * math.sin(ang * 5.0 + i * 2)
                local_x = math.cos(ang) * p_rad * water_scale * t_r * lobe
                local_y = math.sin(ang) * p_rad * water_scale * t_r * aspect * lobe
                rx = local_x * math.cos(rot) - local_y * math.sin(rot)
                ry = local_x * math.sin(rot) + local_y * math.cos(rot)

                # Micro ripple
                wave = (
                    math.sin((px + rx) * 3.0 + (py + ry) * 2.0) * 0.005 +
                    math.cos((px + rx) * 4.5 - (py + ry) * 3.5) * 0.003
                )

                vx = px + rx
                vy = py + ry
                vz = puddle_z + wave
                current_verts.append(bm.verts.new((vx, vy, vz)))
            ring_verts.append(current_verts)

        # Center fan faces
        for s in range(segments):
            s_next = (s + 1) % segments
            try:
                bm.faces.new((center_v, ring_verts[0][s], ring_verts[0][s_next]))
            except ValueError:
                pass

        # Ring quads
        for r in range(rings - 1):
            r1 = ring_verts[r]
            r2 = ring_verts[r + 1]
            for s in range(segments):
                s_next = (s + 1) % segments
                try:
                    bm.faces.new((r1[s], r2[s], r2[s_next], r1[s_next]))
                except ValueError:
                    pass

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    bm.normal_update()
    for f in bm.faces:
        f.smooth = True

    return bm


# ==============================================================================
# 5. PBR Materials (濡れ岩・地層スラブ・クリア流水マテリアル)
# ==============================================================================


ROCK_PALETTES = {
    'SLATE': {
        'rock_dark': (0.04, 0.04, 0.045, 1.0),
        'rock_light': (0.16, 0.14, 0.12, 1.0),
        'roughness_dry': 0.84,
        'water_color': (0.02, 0.12, 0.15, 1.0)
    },
    'LIMESTONE': {
        'rock_dark': (0.32, 0.29, 0.24, 1.0),
        'rock_light': (0.58, 0.54, 0.46, 1.0),
        'roughness_dry': 0.72,
        'water_color': (0.03, 0.26, 0.22, 1.0)
    },
    'SANDSTONE': {
        'rock_dark': (0.42, 0.18, 0.09, 1.0),
        'rock_light': (0.68, 0.42, 0.24, 1.0),
        'roughness_dry': 0.92,
        'water_color': (0.04, 0.18, 0.14, 1.0)
    },
    'BASALT': {
        'rock_dark': (0.02, 0.022, 0.028, 1.0),
        'rock_light': (0.09, 0.10, 0.12, 1.0),
        'roughness_dry': 0.80,
        'water_color': (0.015, 0.06, 0.14, 1.0)
    }
}

def get_or_create_cave_floor_material(mat_name="Cave_Floor_Terrace_Mat", has_river=True, rock_style='SLATE', add_moss=True, moss_amount=0.6):
    """Creates procedural layered sedimentary rock with velvety moss on upward shelves and wetness near river."""
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

    # 1. Base Multi-Scale Geological Rock Textures (NO Voronoi honeycomb cracks)
    # 1A. Macro Geological Form & Folded Crevices
    macro_noise = nodes.new(type='ShaderNodeTexNoise')
    macro_noise.location = (-1000, 500)
    macro_noise.inputs['Scale'].default_value = 1.4
    macro_noise.inputs['Detail'].default_value = 5.0
    macro_noise.inputs['Roughness'].default_value = 0.52
    macro_noise.inputs['Distortion'].default_value = 0.0 # Solid isotropic rock grain, no swirls
    links.new(coord.outputs['Object'], macro_noise.inputs['Vector'])

    ramp_crevice = nodes.new(type='ShaderNodeValToRGB')
    ramp_crevice.location = (-750, 500)
    ramp_crevice.color_ramp.elements[0].position = 0.22
    ramp_crevice.color_ramp.elements[0].color = (0.55, 0.55, 0.55, 1.0) # Gentle crevice shadow
    ramp_crevice.color_ramp.elements[1].position = 0.78
    ramp_crevice.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    links.new(macro_noise.outputs['Fac'], ramp_crevice.inputs['Fac'])

    # 1B. Natural Medium Rock Noise
    rock_noise = nodes.new(type='ShaderNodeTexNoise')
    rock_noise.location = (-1000, 150)
    rock_noise.inputs['Scale'].default_value = 4.5
    rock_noise.inputs['Detail'].default_value = 6.0
    rock_noise.inputs['Roughness'].default_value = 0.60
    links.new(coord.outputs['Object'], rock_noise.inputs['Vector'])

    # 1C. Micro Mineral Grain
    micro_noise = nodes.new(type='ShaderNodeTexNoise')
    micro_noise.location = (-1000, -150)
    micro_noise.inputs['Scale'].default_value = 24.0
    micro_noise.inputs['Detail'].default_value = 8.0
    micro_noise.inputs['Roughness'].default_value = 0.70
    links.new(coord.outputs['Object'], micro_noise.inputs['Vector'])

    pal = ROCK_PALETTES.get(rock_style, ROCK_PALETTES['SLATE'])

    # Color Ramp for Rock Tone
    ramp_rock = nodes.new(type='ShaderNodeValToRGB')
    ramp_rock.location = (-750, 0)
    ramp_rock.color_ramp.elements[0].position = 0.15
    ramp_rock.color_ramp.elements[0].color = pal['rock_dark']
    ramp_rock.color_ramp.elements[1].position = 0.85
    ramp_rock.color_ramp.elements[1].color = pal['rock_light']
    links.new(rock_noise.outputs['Fac'], ramp_rock.inputs['Fac'])

    # Natural Crevice Shading
    mix_cracked_rock = nodes.new(type='ShaderNodeMix')
    mix_cracked_rock.data_type = 'RGBA'
    mix_cracked_rock.location = (-420, 150)
    mix_cracked_rock.blend_type = 'MULTIPLY'
    mix_cracked_rock.inputs[0].default_value = 0.60
    links.new(ramp_rock.outputs['Color'], mix_cracked_rock.inputs[6])
    links.new(ramp_crevice.outputs['Color'], mix_cracked_rock.inputs[7])

    # Wetness Mask (Only low river trench and puddle basins are wet, NOT entire floor)
    sep_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
    sep_xyz.location = (-950, -450)
    links.new(coord.outputs['Object'], sep_xyz.inputs['Vector'])

    ramp_wet = nodes.new(type='ShaderNodeValToRGB')
    ramp_wet.location = (-650, -450)
    ramp_wet.color_ramp.elements[0].position = -0.35
    ramp_wet.color_ramp.elements[0].color = (1.0, 1.0, 1.0, 1.0) # Wet in basins
    ramp_wet.color_ramp.elements[1].position = 0.05
    ramp_wet.color_ramp.elements[1].color = (0.0, 0.0, 0.0, 1.0) # Dry on terraces
    links.new(sep_xyz.outputs['Z'], ramp_wet.inputs['Fac'])

    # Darker wet color helper
    dark_wet = nodes.new(type='ShaderNodeMix')
    dark_wet.location = (-450, -300)
    dark_wet.data_type = 'RGBA'
    dark_wet.inputs[0].default_value = 0.72
    links.new(mix_cracked_rock.outputs[2], dark_wet.inputs[6])
    dark_wet.inputs[7].default_value = (0.01, 0.015, 0.02, 1.0)

    # Mix Color (Dry vs Wet Rock)
    mix_rock_wet = nodes.new(type='ShaderNodeMix')
    mix_rock_wet.location = (-150, 150)
    mix_rock_wet.data_type = 'RGBA'
    links.new(ramp_wet.outputs['Color'], mix_rock_wet.inputs[0])
    links.new(mix_cracked_rock.outputs[2], mix_rock_wet.inputs[6])
    links.new(dark_wet.outputs[2], mix_rock_wet.inputs[7])

    # Geometry Normal for Upward Slopes (Moss on terraces)
    geom = nodes.new(type='ShaderNodeNewGeometry')
    geom.location = (-1200, -700)
    sep_norm = nodes.new(type='ShaderNodeSeparateXYZ')
    sep_norm.location = (-950, -700)
    links.new(geom.outputs['Normal'], sep_norm.inputs['Vector'])

    ramp_upward = nodes.new(type='ShaderNodeValToRGB')
    ramp_upward.location = (-700, -700)
    ramp_upward.color_ramp.elements[0].position = 0.35
    ramp_upward.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp_upward.color_ramp.elements[1].position = 0.75
    ramp_upward.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    links.new(sep_norm.outputs['Z'], ramp_upward.inputs['Fac'])

    # Moss Micro Noise & Color
    moss_noise = nodes.new(type='ShaderNodeTexNoise')
    moss_noise.location = (-950, -900)
    moss_noise.inputs['Scale'].default_value = 7.5
    moss_noise.inputs['Detail'].default_value = 5.0
    links.new(coord.outputs['Object'], moss_noise.inputs['Vector'])

    ramp_moss_col = nodes.new(type='ShaderNodeValToRGB')
    ramp_moss_col.location = (-700, -900)
    ramp_moss_col.color_ramp.elements[0].position = 0.20
    ramp_moss_col.color_ramp.elements[0].color = (0.04, 0.13, 0.02, 1.0)
    ramp_moss_col.color_ramp.elements[1].position = 0.80
    ramp_moss_col.color_ramp.elements[1].color = (0.16, 0.32, 0.08, 1.0)
    links.new(moss_noise.outputs['Fac'], ramp_moss_col.inputs['Fac'])

    moss_mult = nodes.new(type='ShaderNodeMath')
    moss_mult.operation = 'MULTIPLY'
    moss_mult.location = (-450, -750)
    links.new(ramp_upward.outputs['Color'], moss_mult.inputs[0])
    links.new(moss_noise.outputs['Fac'], moss_mult.inputs[1])

    moss_fac = nodes.new(type='ShaderNodeMath')
    moss_fac.operation = 'MULTIPLY'
    moss_fac.location = (-250, -750)
    moss_fac.use_clamp = True
    links.new(moss_mult.outputs['Value'], moss_fac.inputs[0])
    moss_fac.inputs[1].default_value = (moss_amount * 1.8) if add_moss else 0.0

    # Final Surface Color: Mix Rock with Moss
    final_color = nodes.new(type='ShaderNodeMix')
    final_color.data_type = 'RGBA'
    final_color.location = (100, 150)
    links.new(moss_fac.outputs['Value'], final_color.inputs[0])
    links.new(mix_rock_wet.outputs[2], final_color.inputs[6])
    links.new(ramp_moss_col.outputs['Color'], final_color.inputs[7])

    # 3-Tier Chained Geological Bump Stack (Macro Form -> Meso Facets -> Micro Grain)
    bump_macro = nodes.new(type='ShaderNodeBump')
    bump_macro.location = (-150, -50)
    bump_macro.inputs['Strength'].default_value = 0.35
    bump_macro.inputs['Distance'].default_value = 0.12
    links.new(macro_noise.outputs['Fac'], bump_macro.inputs['Height'])

    bump_medium = nodes.new(type='ShaderNodeBump')
    bump_medium.location = (50, -50)
    bump_medium.inputs['Strength'].default_value = 0.25
    bump_medium.inputs['Distance'].default_value = 0.04
    links.new(bump_macro.outputs['Normal'], bump_medium.inputs['Normal'])
    links.new(rock_noise.outputs['Fac'], bump_medium.inputs['Height'])

    bump_micro = nodes.new(type='ShaderNodeBump')
    bump_micro.location = (250, -50)
    bump_micro.inputs['Strength'].default_value = 0.20
    bump_micro.inputs['Distance'].default_value = 0.015
    links.new(bump_medium.outputs['Normal'], bump_micro.inputs['Normal'])
    links.new(micro_noise.outputs['Fac'], bump_micro.inputs['Height'])

    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (400, 100)
    links.new(final_color.outputs[2], bsdf.inputs['Base Color'])
    links.new(bump_micro.outputs['Normal'], bsdf.inputs['Normal'])

    # Roughness: blend wet rock / dry rock / velvety moss
    rough_rock = nodes.new(type='ShaderNodeMix')
    rough_rock.data_type = 'FLOAT'
    rough_rock.location = (-50, -400)
    links.new(ramp_wet.outputs['Color'], rough_rock.inputs[0])
    rough_rock.inputs[2].default_value = pal['roughness_dry']
    rough_rock.inputs[3].default_value = 0.12

    rough_final = nodes.new(type='ShaderNodeMix')
    rough_final.data_type = 'FLOAT'
    rough_final.location = (150, -400)
    links.new(moss_fac.outputs['Value'], rough_final.inputs[0])
    links.new(rough_rock.outputs[0], rough_final.inputs[2])
    rough_final.inputs[3].default_value = 0.94
    links.new(rough_final.outputs[0], bsdf.inputs['Roughness'])

    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (650, 100)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat


def get_or_create_cave_water_material(mat_name="Cave_Water_Mat", rock_style='SLATE'):
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

    pal = ROCK_PALETTES.get(rock_style, ROCK_PALETTES['SLATE'])
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 100)
    bsdf.inputs['Base Color'].default_value = pal['water_color']
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
# 6. Procedural Cave Interior Lighting Rig (洞窟内部ライティング自動配置)
# ==============================================================================

def setup_cave_interior_lights(
    context,
    base_name="Cave_Dungeon",
    length=35.0,
    ceiling_height=6.5,
    seed=0,
    intensity_mult=1.0,
    enable_lights=True
):
    """
    Sets up or updates dedicated cinematic lighting inside the cave so the user
    can clearly see the floor, cliffs, water, and ceiling immediately upon generation.
    Supports in-place updates (Zero accumulation).
    """
    col = context.collection

    light_configs = [
        {
            "suffix": "_Light_Front",
            "type": 'POINT',
            "y_rel": -0.32,
            "x_offset": -3.5,
            "z_offset": 2.2,
            "color": (1.0, 0.72, 0.42),
            "energy": 3500.0 * intensity_mult,
            "radius": 0.8
        },
        {
            "suffix": "_Light_Mid",
            "type": 'POINT',
            "y_rel": 0.02,
            "x_offset": 3.2,
            "z_offset": 2.0,
            "color": (1.0, 0.65, 0.35),
            "energy": 3000.0 * intensity_mult,
            "radius": 0.8
        },
        {
            "suffix": "_Light_Back",
            "type": 'POINT',
            "y_rel": 0.34,
            "x_offset": -1.8,
            "z_offset": 2.4,
            "color": (0.35, 0.75, 1.0), # Deep cavern bioluminescent / cyan rim
            "energy": 2800.0 * intensity_mult,
            "radius": 1.0
        },
        {
            "suffix": "_Light_SkySun",
            "type": 'SUN',
            "y_rel": 0.0,
            "x_offset": 0.0,
            "z_offset": ceiling_height + 2.0,
            "color": (0.6, 0.78, 1.0), # Cool skylight through ceiling fissure
            "energy": 2.2 * intensity_mult,
            "rotation": (0.35, -0.22, 0.4)
        }
    ]

    created_lights = []

    for cfg in light_configs:
        obj_name = base_name + cfg["suffix"]
        light_obj = bpy.data.objects.get(obj_name)

        if not enable_lights:
            if light_obj:
                bpy.data.objects.remove(light_obj, do_unlink=True)
            continue

        # Calculate position following cave centerline
        y_pos = length * cfg["y_rel"]
        cx = get_cave_center_x(y_pos, length=length, seed=seed)
        x_pos = cx + cfg["x_offset"]
        z_pos = cfg["z_offset"]

        if light_obj and light_obj.type == 'LIGHT':
            light_data = light_obj.data
            light_obj.location = (x_pos, y_pos, z_pos)
        else:
            light_data = bpy.data.lights.new(name=obj_name, type=cfg["type"])
            light_obj = bpy.data.objects.new(name=obj_name, object_data=light_data)
            col.objects.link(light_obj)
            light_obj.location = (x_pos, y_pos, z_pos)

        light_data.color = cfg["color"]
        light_data.energy = cfg["energy"]
        if cfg["type"] == 'POINT':
            light_data.shadow_soft_size = cfg["radius"]
        elif cfg["type"] == 'SUN' and "rotation" in cfg:
            light_obj.rotation_euler = cfg["rotation"]

        created_lights.append(light_obj)

    return created_lights


# ==============================================================================
# 6. Main Procedural Cave Scene Builder (Step 1 統合)
# ==============================================================================


# ==============================================================================
# 5. Overhanging Cliff & Ceiling Arch BMesh Builder (新・断崖側壁＆天井岩盤アーチ)
# ==============================================================================

def build_cliff_ceiling_bmesh(
    width=18.0,
    length=35.0,
    path_type='S_CURVE',
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
        center_x, w_mult, h_mult = get_cave_profile_at_y(y_pos, length=length, path_type=path_type, seed=seed)
        effective_hx = hx * w_mult
        effective_h = ceiling_height * h_mult
        effective_fissure = fissure_width * w_mult
        row = []

        for iu in range(subdivisions_arc + 1):
            u = iu / float(subdivisions_arc)  # 0.0 to 1.0
            
            # Map u to arch coordinates (x_rel, z_base)
            # Left wall (u < 0.25): rises vertically from floor edge
            # Left ceiling (0.25 <= u < 0.5): arches inward towards center
            # Right ceiling (0.5 <= u < 0.75): arches outward
            # Right wall (u >= 0.75): descends vertically to right floor edge
            
            if u < 0.25:
                # Left vertical cliff (starts at -1.8m deep below floor to eliminate all seam gaps)
                t = u / 0.25
                x_rel = -effective_hx * (1.0 - t * 0.15)
                z_base = -1.8 + t * (effective_h * 0.55 + 1.8)
            elif u < 0.5:
                # Left ceiling overhang
                t = (u - 0.25) / 0.25
                # Inward overhang
                x_rel = -effective_hx * 0.85 + t * (effective_hx * 0.85 - effective_fissure * 0.5) * overhang
                # Arch up to ceiling height
                arch_t = math.sin(t * math.pi * 0.5)
                z_base = effective_h * (0.55 + arch_t * 0.45)
            elif u < 0.75:
                # Right ceiling overhang
                t = (u - 0.5) / 0.25
                x_rel = (effective_fissure * 0.5) + t * (effective_hx * 0.85 - effective_fissure * 0.5) * overhang
                # Arch down from ceiling height
                arch_t = math.cos(t * math.pi * 0.5)
                z_base = effective_h * (0.55 + arch_t * 0.45)
            else:
                # Right vertical cliff (penetrates to -1.8m below floor for seamless closure)
                t = (u - 0.75) / 0.25
                x_rel = effective_hx * (0.85 + t * 0.15)
                z_base = -1.8 + (1.0 - t) * (effective_h * 0.55 + 1.8)

            # World X position following cave centerline
            x_pos = center_x + x_rel

            # 1. Sedimentary Strata Steps (Natural horizontal bedded rock layers, NO Voronoi honeycomb)
            strata_thickness = 0.85
            layer_val = (z_base + 3.0) / strata_thickness
            layer_idx = math.floor(layer_val)
            layer_frac = layer_val - layer_idx
            shelf_blend = layer_frac ** 3 * (layer_frac * (layer_frac * 6 - 15) + 10)
            z_strata = (layer_idx + shelf_blend) * strata_thickness - 3.0

            # Deterministic shelf overhang per geological stratum
            layer_rand = math.sin(layer_idx * 17.13 + seed * 3.71)
            strata_ledge = layer_rand * 0.65 * roughness

            # 2. Multi-Octave Fractal Cliff & Crag Form (Macro bulges + Meso block facets)
            macro_crag = pseudo_noise_3d(x_pos * 0.22, y_pos * 0.22, z_base * 0.30, seed=seed + 41) * 0.85 * roughness
            meso_crag = pseudo_noise_3d(x_pos * 0.65, y_pos * 0.65, z_base * 0.65, seed=seed + 83) * 0.38 * roughness
            micro_crag = pseudo_noise_3d(x_pos * 1.6, y_pos * 1.6, z_base * 1.6, seed=seed + 127) * 0.12 * roughness

            # 3. Smooth Directional Displacement (Rock shelves on walls, hanging masses on ceiling)
            norm_sign = -1.0 if x_rel < 0 else 1.0
            wall_jut = norm_sign * (strata_ledge + macro_crag * 0.8 + meso_crag)
            ceiling_hang = -abs(macro_crag) * 0.75 + meso_crag

            ceiling_weight = math.sin(u * math.pi) ** 1.5
            wall_weight = 1.0 - ceiling_weight

            x_disp = wall_jut * wall_weight + (meso_crag + micro_crag) * ceiling_weight * 0.4
            z_disp = (z_strata - z_base) * 0.5 + ceiling_hang * ceiling_weight + (meso_crag * 0.4 + micro_crag) * wall_weight

            vert = bm.verts.new((x_pos + x_disp, y_pos, z_base + z_disp))
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


def get_or_create_cave_ceiling_material(mat_name="Cave_Ceiling_Cliff_Mat", rock_style='SLATE', add_moss=True, moss_amount=0.6):
    """Creates procedural PBR material for cliff walls, ceiling, pillars, and debris with moss support."""
    return get_or_create_cave_floor_material(mat_name=mat_name, has_river=False, rock_style=rock_style, add_moss=add_moss, moss_amount=moss_amount * 0.6)

def get_or_create_cave_water_material(mat_name="Cave_Water_Mat", rock_style='SLATE'):
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

    pal = ROCK_PALETTES.get(rock_style, ROCK_PALETTES['SLATE'])
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 100)
    bsdf.inputs['Base Color'].default_value = pal['water_color']
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
# 5. Speleothem & Debris Helpers (Step 3: 岩柱・鍾乳石・石筍・崩落巨石)
# ==============================================================================

def create_speleothem_cone_bmesh(bm, base_pos, tip_pos, base_radius=0.35, tip_radius=0.04, segments=16, rings=14, noise_seed=0):
    """Creates an organic stalactite or stalagmite with rounded bulbous tip, flanged base, and rib drapery."""
    rng = random.Random(noise_seed)
    diff = tip_pos - base_pos
    length = diff.length
    if length < 0.08:
        return
    
    dir_vec = diff.normalized()
    up = Vector((0, 0, 1))
    if abs(dir_vec.dot(up)) > 0.95:
        up = Vector((1, 0, 0))
    side1 = dir_vec.cross(up).normalized()
    side2 = dir_vec.cross(side1).normalized()

    wobble_dx = rng.uniform(-0.06, 0.06) * length
    wobble_dy = rng.uniform(-0.06, 0.06) * length

    ring_verts_list = []
    for r in range(rings):
        t = r / float(rings)
        
        # Base flare blending into rock ceiling/floor
        flare = math.exp(-t * 5.0) * 0.95

        # Middle rhythmic drip nodes
        drip_node = 0.12 * math.sin(t * math.pi * 4.5 + noise_seed) * (1.0 - t * 0.5)

        # Teardrop water bulge near tip (smooth bulb instead of sharp cone)
        bulb = 0.0
        if t > 0.80:
            bulb = 0.40 * math.sin(((t - 0.80) / 0.20) * math.pi)

        rad = (base_radius * ((1.0 - t)**0.95) + tip_radius) * (1.0 + flare + drip_node + bulb)

        center = base_pos + dir_vec * (length * t)
        center += side1 * (wobble_dx * (t**1.3))
        center += side2 * (wobble_dy * (t**1.3))

        ring_verts = []
        for s in range(segments):
            ang = s * (2.0 * math.pi / segments)
            # Organic drapery ribs
            rib = 1.0 + 0.20 * math.sin(ang * 4.0 + noise_seed) + 0.09 * math.cos(ang * 6.0)
            nv = pseudo_noise_3d(center.x + math.cos(ang) * 0.5, center.y + math.sin(ang) * 0.5, center.z + t * 3.0, noise_seed)
            r_final = max(0.012, rad * rib * (1.0 + nv * 0.12))

            px = center.x + (side1.x * math.cos(ang) + side2.x * math.sin(ang)) * r_final
            py = center.y + (side1.y * math.cos(ang) + side2.y * math.sin(ang)) * r_final
            pz = center.z + (side1.z * math.cos(ang) + side2.z * math.sin(ang)) * r_final
            ring_verts.append(bm.verts.new((px, py, pz)))
        ring_verts_list.append(ring_verts)

    # Rounded dome tip (bulbous droplet end)
    tip_cap_center = base_pos + dir_vec * length + side1 * wobble_dx + side2 * wobble_dy
    tip_cap_vert = bm.verts.new(tip_cap_center + dir_vec * (tip_radius * 0.7))

    for r in range(rings - 1):
        rv1 = ring_verts_list[r]
        rv2 = ring_verts_list[r + 1]
        for s in range(segments):
            s_next = (s + 1) % segments
            f = bm.faces.new((rv1[s], rv1[s_next], rv2[s_next], rv2[s]))
            f.smooth = True

    # Base cap
    f_base = bm.faces.new(reversed(ring_verts_list[0]))
    f_base.smooth = True

    # Rounded dome tip fan
    for s in range(segments):
        s_next = (s + 1) % segments
        f = bm.faces.new((ring_verts_list[-1][s], ring_verts_list[-1][s_next], tip_cap_vert))
        f.smooth = True


def build_stalactites_on_ceiling_bmesh(bm, length, width, ceiling_height, path_type, cluster_count=35, seed=0):
    """Sprouts clusters of stalactites hanging downwards from the cave ceiling."""
    rng = random.Random(seed + 1234)
    for c in range(cluster_count):
        cy = rng.uniform(-length * 0.44, length * 0.44)
        cx, wm, hm = get_cave_profile_at_y(cy, length, path_type, seed)
        eff_w = (width * 0.5) * wm
        eff_h = ceiling_height * hm

        offset_x = rng.uniform(-eff_w * 0.78, eff_w * 0.78)
        px = cx + offset_x
        lat_ratio = abs(offset_x) / max(1.0, eff_w)
        arch = max(0.0, 1.0 - (lat_ratio ** 1.8))
        pz = eff_h * (0.65 + 0.35 * arch) + 0.2

        sub_count = rng.randint(2, 5)
        for sc in range(sub_count):
            sp_x = px + rng.uniform(-0.7, 0.7)
            sp_y = cy + rng.uniform(-0.7, 0.7)
            base_z = pz + rng.uniform(-0.1, 0.3)
            
            s_len = rng.uniform(0.9, 2.6) if (sc == 0) else rng.uniform(0.35, 1.3)
            base_r = rng.uniform(0.20, 0.42) if (sc == 0) else rng.uniform(0.09, 0.22)
            tip_r = rng.uniform(0.02, 0.04)

            base_pos = Vector((sp_x, sp_y, base_z))
            tip_pos = Vector((sp_x, sp_y, base_z - s_len))
            create_speleothem_cone_bmesh(
                bm, base_pos, tip_pos,
                base_radius=base_r, tip_radius=tip_r,
                segments=12, rings=8,
                noise_seed=seed + c * 50 + sc
            )


def build_stalagmites_on_floor_bmesh(bm, length, width, path_type, cluster_count=26, seed=0):
    """Sprouts clusters of stalagmites standing upwards from the cave floor/terraces."""
    rng = random.Random(seed + 5678)
    for c in range(cluster_count):
        cy = rng.uniform(-length * 0.42, length * 0.42)
        cx, wm, hm = get_cave_profile_at_y(cy, length, path_type, seed)
        eff_w = (width * 0.5) * wm

        side = 1.0 if rng.random() > 0.5 else -1.0
        offset_x = side * rng.uniform(2.3, eff_w * 0.82)
        px = cx + offset_x
        pz = rng.uniform(0.1, 0.6)

        sub_count = rng.randint(1, 4)
        for sc in range(sub_count):
            sp_x = px + rng.uniform(-0.6, 0.6)
            sp_y = cy + rng.uniform(-0.6, 0.6)
            base_z = pz - 0.35

            s_len = rng.uniform(0.7, 2.0) if (sc == 0) else rng.uniform(0.3, 0.9)
            base_r = rng.uniform(0.25, 0.50) if (sc == 0) else rng.uniform(0.12, 0.25)
            tip_r = rng.uniform(0.04, 0.09)

            base_pos = Vector((sp_x, sp_y, base_z))
            tip_pos = Vector((sp_x, sp_y, base_z + s_len))
            create_speleothem_cone_bmesh(
                bm, base_pos, tip_pos,
                base_radius=base_r, tip_radius=tip_r,
                segments=12, rings=8,
                noise_seed=seed + c * 40 + sc
            )


def build_cave_pillars_bmesh(length, width, ceiling_height, path_type, count=4, seed=0):
    """
    Builds massive, multi-lobed organic speleothem rock pillars connecting floor to ceiling.
    Features fused stalactite/stalagmite lobes, flanged skirts at connections, and banded drip rings.
    """
    bm = bmesh.new()
    rng = random.Random(seed + 777)
    if count <= 0:
        return bm

    y_step = (length * 0.72) / max(1, count)
    y_start = -length * 0.36

    for i in range(count):
        py = y_start + (i + 0.5) * y_step + rng.uniform(-length * 0.06, length * 0.06)
        cx, wm, hm = get_cave_profile_at_y(py, length, path_type, seed)
        eff_w = (width * 0.5) * wm
        eff_h = ceiling_height * hm

        side = 1.0 if (i % 2 == 0) else -1.0
        min_dist = max(2.5, eff_w * 0.48)
        max_dist = max(min_dist + 1.2, eff_w * 0.78)
        offset_x = side * rng.uniform(min_dist, max_dist)
        px = cx + offset_x

        pz_floor = -0.8
        lat_ratio = abs(offset_x) / max(1.0, eff_w)
        arch = max(0.0, 1.0 - (lat_ratio ** 1.8))
        pz_ceiling = eff_h * (0.65 + 0.35 * arch) + 0.8

        pillar_h = pz_ceiling - pz_floor
        if pillar_h < 1.5:
            continue

        # Substantially thicker base radius (massive stalactite/stalagmite column)
        base_radius = rng.uniform(1.6, 2.6)
        segments = 32
        rings = 28

        ring_verts_list = []
        p_seed = seed + i * 37
        for r in range(rings + 1):
            t = r / float(rings)
            z = pz_floor + t * pillar_h

            # Organic flanged skirt at floor (t->0) and ceiling (t->1)
            flare_bottom = math.exp(-t * 5.5) * 1.5
            flare_top = math.exp(-(1.0 - t) * 5.5) * 1.4
            waist_factor = 0.82 + flare_bottom + flare_top

            # Natural gentle spine meander
            lx = math.sin(t * math.pi + p_seed) * 0.22
            ly = math.cos(t * math.pi + p_seed * 1.5) * 0.22

            ring_verts = []
            for s in range(segments):
                ang = s * (2.0 * math.pi / segments)

                # Multi-lobed profile: multiple fused stalactite columns growing together
                lobe = (
                    math.cos(ang * 3.0 + p_seed) * 0.28 +
                    math.sin(ang * 5.0 + p_seed * 1.6) * 0.14 +
                    math.cos(ang * 7.0 - p_seed * 2.1) * 0.06
                )

                r_final = max(0.40, base_radius * waist_factor * (1.0 + lobe))

                vx = px + lx + math.cos(ang) * r_final
                vy = py + ly + math.sin(ang) * r_final
                vz = z
                ring_verts.append(bm.verts.new((vx, vy, vz)))
            ring_verts_list.append(ring_verts)

        for r in range(rings):
            rv1 = ring_verts_list[r]
            rv2 = ring_verts_list[r + 1]
            for s in range(segments):
                s_next = (s + 1) % segments
                f = bm.faces.new((rv1[s], rv1[s_next], rv2[s_next], rv2[s]))
                f.smooth = True

        f_bottom = bm.faces.new(reversed(ring_verts_list[0]))
        f_top = bm.faces.new(ring_verts_list[-1])
        f_bottom.smooth = True
        f_top.smooth = True

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def build_cave_debris_bmesh(length, width, path_type, count=18, seed=0):
    """Builds fallen boulders and rock debris scattered along riverbanks and terraces."""
    bm = bmesh.new()
    rng = random.Random(seed + 999)

    for i in range(count):
        py = rng.uniform(-length * 0.44, length * 0.44)
        cx, wm, hm = get_cave_profile_at_y(py, length, path_type, seed)
        eff_w = (width * 0.5) * wm

        side = 1.0 if rng.random() > 0.5 else -1.0
        dist = rng.uniform(1.6, eff_w * 0.75)
        px = cx + side * dist
        pz = rng.uniform(-0.15, 0.40)

        sx = rng.uniform(0.65, 1.9)
        sy = rng.uniform(0.65, 1.9)
        sz = rng.uniform(0.45, 1.3)

        bm_rock = bmesh.new()
        build_convex_hull_rock(bm_rock, sx, sy, sz, point_count=18, is_crag=(i % 2 == 0), seed=seed + i * 19)

        rot_mat = Euler((
            rng.uniform(-0.4, 0.4),
            rng.uniform(-0.4, 0.4),
            rng.uniform(0, math.pi * 2)
        ), 'XYZ').to_matrix().to_4x4()
        trans_mat = Matrix.Translation((px, py, pz))
        bm_rock.transform(trans_mat @ rot_mat)

        vert_map = {}
        for v in bm_rock.verts:
            vert_map[v] = bm.verts.new(v.co)
        for f in bm_rock.faces:
            nf = bm.faces.new([vert_map[v] for v in f.verts])
            nf.smooth = True
        bm_rock.free()

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def attach_cave_modifiers(obj, subsurf_levels=1, displace_strength=0.16, texture_scale=2.0):
    """
    Attaches non-destructive modifiers (Subsurf and Displace) to cave objects.
    Preserves existing modifiers if already present. Does NOT apply them.
    Allows user to toggle On/Off and tweak strength in Blender UI anytime.
    """
    if not obj or obj.type != 'MESH':
        return

    # Clean legacy modifier if present
    legacy_disp = obj.modifiers.get("Cave_Displace")
    if legacy_disp:
        obj.modifiers.remove(legacy_disp)

    # 1. Subdivision Surface (Smooths angular facets)
    subsurf = obj.modifiers.get("Cave_Subsurf")
    if not subsurf:
        subsurf = obj.modifiers.new("Cave_Subsurf", 'SUBSURF')
    subsurf.levels = subsurf_levels
    subsurf.render_levels = max(subsurf_levels + 1, 2)

    # 2. Chuck CG Multi-Displace Stack (Macro bulges + Micro faceted crags)
    # Tier A: Macro Cliff Ledges & Rock Form
    disp_macro = obj.modifiers.get("Cave_Disp_Macro")
    if not disp_macro:
        disp_macro = obj.modifiers.new("Cave_Disp_Macro", 'DISPLACE')

    tex_macro_name = "Cave_Tex_Disp_Macro"
    tex_macro = bpy.data.textures.get(tex_macro_name)
    if not tex_macro:
        tex_macro = bpy.data.textures.new(tex_macro_name, type='CLOUDS')
        tex_macro.noise_scale = 0.65
        tex_macro.noise_depth = 2
        tex_macro.noise_type = 'SOFT_NOISE'

    disp_macro.texture = tex_macro
    disp_macro.texture_coords = 'GLOBAL'
    disp_macro.mid_level = 0.5
    disp_macro.strength = displace_strength * 0.70

    # Tier B: Micro Faceted Crags & Rock Roughness
    disp_micro = obj.modifiers.get("Cave_Disp_Micro")
    if not disp_micro:
        disp_micro = obj.modifiers.new("Cave_Disp_Micro", 'DISPLACE')

    tex_micro_name = "Cave_Tex_Disp_Micro"
    tex_micro = bpy.data.textures.get(tex_micro_name)
    if not tex_micro:
        tex_micro = bpy.data.textures.new(tex_micro_name, type='CLOUDS')
        tex_micro.noise_scale = 0.18
        tex_micro.noise_depth = 3
        tex_micro.noise_type = 'SOFT_NOISE'

    disp_micro.texture = tex_micro
    disp_micro.texture_coords = 'GLOBAL'
    disp_micro.mid_level = 0.5
    disp_micro.strength = displace_strength * 0.30


def create_procedural_cave_scene(
    context,
    name="Cave",
    seed=0,
    path_type='S_CURVE',
    rock_style='SLATE',
    water_type='PUDDLES',
    has_river=True,
    puddle_count=6,
    puddle_scale=2.4,
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
    generate_pillars=True,
    pillar_count=4,
    generate_stalactites=True,
    stalactite_density=1.0,
    generate_boulders=True,
    boulder_count=16,
    add_moss=True,
    moss_amount=0.6,
    target_obj=None,
    **kwargs
):
    """
    Main entry point for Cave System (Step 1, Step 2, Step 3, Water & Realism Overhaul).
    Builds:
    - Terraced rock floor with voronoi slabs and organic depressions
    - Water features (Puddles & Pools, Subterranean River, or Both)
    - Vertical cliff walls and overhanging ceiling arch (separate object)
    - Massive multi-lobed speleothem columns, rounded bulb stalactites, boulders
    """
    col = context.collection

    # Determine effective river & puddle flags
    # If caller specifically passed water_type, respect it; otherwise fallback to has_river
    if water_type in ('RIVER', 'BOTH'):
        has_river_effective = True
    elif water_type == 'NONE':
        has_river_effective = False
    elif water_type == 'PUDDLES':
        has_river_effective = False
    else:
        has_river_effective = has_river

    has_puddles_effective = water_type in ('PUDDLES', 'BOTH')

    # 0. Sanitize base name (prevent _Floor_Floor accumulation)
    import re
    clean_name = re.sub(r'(_Floor|_Water|_Puddles|_Ceiling|_Pillars|_Debris)+$', '', name).strip() or "Cave_Dungeon"

    floor_obj_name = clean_name + "_Floor"
    river_obj_name = clean_name + "_Water"
    puddles_obj_name = clean_name + "_Puddles"
    ceiling_obj_name = clean_name + "_Ceiling"
    pillar_obj_name = clean_name + "_Pillars"
    debris_obj_name = clean_name + "_Debris"

    # 0B. Calculate puddle locations upfront so floor can carve basins
    puddle_locations = None
    if has_puddles_effective and puddle_count > 0:
        puddle_locations = get_cave_puddle_locations(
            width=floor_width,
            length=floor_length,
            path_type=path_type,
            terrace_steps=terrace_steps,
            step_height=step_height,
            puddle_count=puddle_count,
            puddle_scale=puddle_scale,
            seed=seed
        )

    # 1. Build Floor BMesh with puddle basin carving
    bm_floor = build_terraced_cave_floor_bmesh(
        width=floor_width,
        length=floor_length,
        path_type=path_type,
        has_river=has_river_effective,
        river_width=river_width,
        river_depth=river_depth,
        terrace_steps=terrace_steps,
        step_height=step_height,
        roughness=roughness,
        seed=seed,
        puddle_locations=puddle_locations
    )
    if generate_stalactites:
        stalagmite_clusters = int(24 * stalactite_density)
        build_stalagmites_on_floor_bmesh(
            bm=bm_floor,
            length=floor_length,
            width=floor_width,
            path_type=path_type,
            cluster_count=stalagmite_clusters,
            seed=seed
        )
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

    mat_floor = get_or_create_cave_floor_material(
        clean_name + "_Floor_Mat",
        has_river=(has_river_effective or has_puddles_effective),
        rock_style=rock_style,
        add_moss=add_moss,
        moss_amount=moss_amount
    )
    if floor_obj.data.materials:
        floor_obj.data.materials[0] = mat_floor
    else:
        floor_obj.data.materials.append(mat_floor)

    # Attach non-destructive modifiers (On/Off toggleable by user in modifier panel)
    attach_cave_modifiers(floor_obj, subsurf_levels=1, displace_strength=0.14)

    # 2A. Handle River Water Mesh
    river_obj = bpy.data.objects.get(river_obj_name)
    if has_river_effective:
        bm_water = build_cave_water_bmesh(
            length=floor_length,
            river_width=river_width,
            path_type=path_type,
            water_level=-river_depth * 0.45,
            seed=seed
        )
        if river_obj and river_obj.type == 'MESH':
            bm_water.to_mesh(river_obj.data)
            river_obj.data.update()
            river_obj.hide_viewport = False
            river_obj.hide_render = False
        else:
            mesh_water = bpy.data.meshes.new(river_obj_name)
            bm_water.to_mesh(mesh_water)
            river_obj = bpy.data.objects.new(river_obj_name, mesh_water)
            col.objects.link(river_obj)
        bm_water.free()

        mat_water = get_or_create_cave_water_material(clean_name + "_Water_Mat", rock_style=rock_style)
        if river_obj.data.materials:
            river_obj.data.materials[0] = mat_water
        else:
            river_obj.data.materials.append(mat_water)
    else:
        if river_obj:
            bpy.data.objects.remove(river_obj, do_unlink=True)
            river_obj = None

    # 2B. Handle Scattered Puddles & Pools Mesh
    puddles_obj = bpy.data.objects.get(puddles_obj_name)
    if has_puddles_effective and puddle_locations:
        bm_puddles = build_cave_puddles_bmesh(puddle_locations=puddle_locations)
        if puddles_obj and puddles_obj.type == 'MESH':
            bm_puddles.to_mesh(puddles_obj.data)
            puddles_obj.data.update()
            puddles_obj.hide_viewport = False
            puddles_obj.hide_render = False
        else:
            mesh_puddles = bpy.data.meshes.new(puddles_obj_name)
            bm_puddles.to_mesh(mesh_puddles)
            puddles_obj = bpy.data.objects.new(puddles_obj_name, mesh_puddles)
            col.objects.link(puddles_obj)
        bm_puddles.free()

        mat_puddles = get_or_create_cave_water_material(clean_name + "_Water_Mat", rock_style=rock_style)
        if puddles_obj.data.materials:
            puddles_obj.data.materials[0] = mat_puddles
        else:
            puddles_obj.data.materials.append(mat_puddles)
    else:
        if puddles_obj:
            bpy.data.objects.remove(puddles_obj, do_unlink=True)
            puddles_obj = None

    # Primary water reference for operator reporting
    water_obj = puddles_obj or river_obj

    # 3. Handle Ceiling & Cliff Walls Mesh (Step 2)
    # ceiling_obj_name already set to clean_name + "_Ceiling"
    ceiling_obj = bpy.data.objects.get(ceiling_obj_name)

    if generate_ceiling:
        bm_ceiling = build_cliff_ceiling_bmesh(
            width=floor_width,
            length=floor_length,
            path_type=path_type,
            ceiling_height=ceiling_height,
            overhang=ceiling_overhang,
            fissure_width=ceiling_fissure,
            roughness=ceiling_roughness,
            seed=seed
        )
        if generate_stalactites:
            stalactite_clusters = int(35 * stalactite_density)
            build_stalactites_on_ceiling_bmesh(
                bm=bm_ceiling,
                length=floor_length,
                width=floor_width,
                ceiling_height=ceiling_height,
                path_type=path_type,
                cluster_count=stalactite_clusters,
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

        mat_ceiling = get_or_create_cave_ceiling_material(clean_name + "_Ceiling_Mat", rock_style=rock_style, add_moss=add_moss, moss_amount=moss_amount)
        if ceiling_obj.data.materials:
            ceiling_obj.data.materials[0] = mat_ceiling
        else:
            ceiling_obj.data.materials.append(mat_ceiling)

        # Attach non-destructive modifiers (Chuck CG 2-tier displacement stack)
        attach_cave_modifiers(ceiling_obj, subsurf_levels=1, displace_strength=0.28)
    else:
        if ceiling_obj:
            bpy.data.objects.remove(ceiling_obj, do_unlink=True)
            ceiling_obj = None

    # 4. Handle Cave Interior Lights (見えやすくするための自動ライティング)
    enable_lights = kwargs.get('setup_lights', True)
    light_intensity = kwargs.get('light_intensity', 1.0)
    setup_cave_interior_lights(
        context=context,
        base_name=clean_name,
        length=floor_length,
        ceiling_height=ceiling_height,
        seed=seed,
        intensity_mult=light_intensity,
        enable_lights=enable_lights
    )

    # 5. Handle Cave Pillars Object (天地貫通の岩柱)
    pillar_obj = bpy.data.objects.get(pillar_obj_name)
    if generate_pillars and pillar_count > 0:
        bm_pillars = build_cave_pillars_bmesh(
            length=floor_length,
            width=floor_width,
            ceiling_height=ceiling_height,
            path_type=path_type,
            count=pillar_count,
            seed=seed
        )
        if pillar_obj and pillar_obj.type == 'MESH':
            bm_pillars.to_mesh(pillar_obj.data)
            pillar_obj.data.update()
        else:
            mesh_pillars = bpy.data.meshes.new(pillar_obj_name)
            bm_pillars.to_mesh(mesh_pillars)
            pillar_obj = bpy.data.objects.new(pillar_obj_name, mesh_pillars)
            col.objects.link(pillar_obj)
        bm_pillars.free()

        mat_rock = get_or_create_cave_ceiling_material(clean_name + "_Rock_Mat", rock_style=rock_style, add_moss=add_moss, moss_amount=moss_amount)
        if pillar_obj.data.materials:
            pillar_obj.data.materials[0] = mat_rock
        else:
            pillar_obj.data.materials.append(mat_rock)

        # Attach non-destructive modifiers
        attach_cave_modifiers(pillar_obj, subsurf_levels=1, displace_strength=0.14)
    else:
        if pillar_obj:
            bpy.data.objects.remove(pillar_obj, do_unlink=True)
            pillar_obj = None

    # 6. Handle Cave Debris Object (崩落巨石・瓦礫)
    debris_obj = bpy.data.objects.get(debris_obj_name)
    if generate_boulders and boulder_count > 0:
        bm_debris = build_cave_debris_bmesh(
            length=floor_length,
            width=floor_width,
            path_type=path_type,
            count=boulder_count,
            seed=seed
        )
        if debris_obj and debris_obj.type == 'MESH':
            bm_debris.to_mesh(debris_obj.data)
            debris_obj.data.update()
        else:
            mesh_debris = bpy.data.meshes.new(debris_obj_name)
            bm_debris.to_mesh(mesh_debris)
            debris_obj = bpy.data.objects.new(debris_obj_name, mesh_debris)
            col.objects.link(debris_obj)
        bm_debris.free()

        mat_rock = get_or_create_cave_ceiling_material(clean_name + "_Rock_Mat", rock_style=rock_style, add_moss=add_moss, moss_amount=moss_amount)
        if debris_obj.data.materials:
            debris_obj.data.materials[0] = mat_rock
        else:
            debris_obj.data.materials.append(mat_rock)

        # Attach non-destructive modifiers
        attach_cave_modifiers(debris_obj, subsurf_levels=1, displace_strength=0.10)
    else:
        if debris_obj:
            bpy.data.objects.remove(debris_obj, do_unlink=True)
            debris_obj = None

    context.view_layer.objects.active = floor_obj
    floor_obj.select_set(True)

    return floor_obj, water_obj, ceiling_obj, pillar_obj, debris_obj