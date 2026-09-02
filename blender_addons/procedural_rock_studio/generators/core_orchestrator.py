import bpy
import bmesh
import math
import random
import os

from ..materials.rock_shaders import build_procedural_rock_material
from ..materials.nature_shaders import (
    create_procedural_grass_blade_shader,
    create_procedural_ground_terrain_shader,
    create_procedural_water_shader,
    create_procedural_water_bed_shader,
    create_procedural_pillar_shader
)
from ..materials.furniture_shaders import create_procedural_pbr_material
from ..materials.image_shaders import apply_image_texture_material
from ..utils.texture_utils import get_textures_from_folder, find_pbr_texture_set
from ..utils.mesh_utils import apply_geometry_displacement

from .rock_gen import build_rock_base, build_crag_base
from .architecture_gen import (
    build_floor_base,
    build_wall_base,
    build_pillar_base,
    build_beam_base,
    build_beam_arch_base
)
from .furniture_gen import (
    build_chair_base,
    build_table_base,
    build_chest_base,
    build_bed_base,
    build_bookshelf_base
)
from .nature_gen import (
    build_grass_tuft_clump,
    build_grass_mound_base,
    build_water_surface_base,
    generate_sapling_real_tree
)
from .fence_gen import build_wooden_fence_mesh
from .bush_gen import build_bush_mesh, apply_bush_spherical_normals
from .pillar_gen import create_procedural_pillar
from .telescope_gen import create_procedural_telescope
from ..utils.water_anim_utils import setup_water_ocean_animation


def cleanup_old_debris(context, parent_name):
    to_delete = [
        o for o in bpy.data.objects
        if "Debris" in o.name and (parent_name in o.name or (o.parent and o.parent.name == parent_name))
    ]
    for o in to_delete:
        bpy.data.objects.remove(o, do_unlink=True)


def resolve_prop_parameters(props):
    cat = props.prop_category
    types = ['JAGGED_CRAG', 'COLUMNAR_CLIFF', 'VOLCANIC_SPIKE', 'FRACTURED', 'SHARP', 'BOULDER']
    final_type = random.choice(types) if props.rand_type else props.rock_type
    
    if props.rand_dimensions:
        if cat == "CHAIR":
            final_sx = round(random.uniform(0.48, 0.62), 2)
            final_sy = round(random.uniform(0.48, 0.62), 2)
            final_sz = round(random.uniform(0.85, 1.1), 2)
        elif cat == "CHEST":
            final_sx = round(random.uniform(1.2, 1.8), 2)
            final_sy = round(random.uniform(0.5, 0.7), 2)
            final_sz = round(random.uniform(0.9, 1.4), 2)
        elif cat == "BED":
            final_sx = round(random.uniform(1.2, 2.0), 2)
            final_sy = round(random.uniform(2.0, 2.2), 2)
            final_sz = round(random.uniform(1.2, 1.6), 2)
        elif cat == "BOOKSHELF":
            final_sx = round(random.uniform(1.2, 2.0), 2)
            final_sy = round(random.uniform(0.4, 0.65), 2)
            final_sz = round(random.uniform(1.8, 2.4), 2)
        elif cat == "TABLE":
            final_sx = round(random.uniform(1.4, 2.4), 2)
            final_sy = round(random.uniform(0.8, 1.4), 2)
            final_sz = round(random.uniform(0.7, 0.9), 2)
        elif cat == "WATER":
            final_sx = round(random.uniform(4.0, 10.0), 2)
            final_sy = final_sx if props.water_shape in ('CIRCLE', 'POND') else round(random.uniform(4.0, 10.0), 2)
            final_sz = round(random.uniform(0.5, 1.5), 2)
        elif cat == "FENCE":
            final_sx = round(random.choice([3.0, 4.0, 5.0, 6.0]), 2)
            final_sy = round(random.uniform(0.3, 0.5), 2)
            final_sz = round(random.choice([1.0, 1.2, 1.5, 1.8]), 2)
        elif cat == "BUSH":
            if props.bush_type == "HEDGE_ROW":
                final_sx = round(random.uniform(2.0, 4.5), 2)
                final_sy = round(random.uniform(0.6, 1.0), 2)
                final_sz = round(random.uniform(0.8, 1.4), 2)
            else:
                sq = round(random.uniform(0.8, 1.6), 2)
                final_sx = sq
                final_sy = sq
                final_sz = round(sq * random.uniform(0.65, 0.95), 2)
        elif cat in ("FLOOR", "GRASS"):
            if cat == "GRASS" and props.grass_mode == 'TUFT':
                final_sx = round(random.uniform(0.6, 1.2), 2)
                final_sy = final_sx
                final_sz = round(random.uniform(0.6, 1.3), 2)
            else:
                sq = round(random.choice([2.0, 3.0, 4.0]), 2)
                final_sx = sq
                final_sy = sq
                final_sz = round(random.uniform(0.15, 0.35), 2)
        elif cat == "WALL":
            final_sx = round(random.choice([2.0, 3.0, 4.0]), 2)
            final_sy = round(random.uniform(0.8, 1.2), 2)
            final_sz = round(random.choice([2.0, 2.5, 3.0]), 2)
        elif cat in ("BEAM", "BEAM_ARCH"):
            final_sx = round(random.uniform(1.8, 3.5), 2)
            final_sy = round(random.uniform(1.5, 2.5), 2)
            final_sz = round(random.uniform(1.8, 2.8), 2)
        elif cat == "PILLAR":
            final_sx = round(random.uniform(0.8, 1.6), 2)
            final_sy = round(random.uniform(0.8, 1.6), 2)
            final_sz = round(random.uniform(1.8, 3.5), 2)
        else:
            final_sx = round(random.uniform(1.2, 3.5), 2)
            final_sy = round(random.uniform(1.2, 3.5), 2)
            final_sz = round(random.uniform(0.8, 2.5), 2)
    else:
        final_sx, final_sy, final_sz = props.size_x, props.size_y, props.size_z

    tex_files = get_textures_from_folder(props.texture_folder)
    if props.rand_texture and tex_files:
        chosen_tex = random.choice(tex_files)
    else:
        chosen_tex = props.selected_texture if (props.selected_texture in tex_files) else (tex_files[0] if tex_files else "")

    leg_styles = ['STEEL_LOOP', 'STEEL_PIPE', 'SIMPLE', 'REINFORCED', 'ORNAMENTAL', 'TWISTED']
    final_leg_style = random.choice(leg_styles) if props.rand_furniture_style else props.table_leg_style
    final_col_style = random.choice(['SIMPLE', 'REINFORCED', 'ORNAMENTAL', 'TWISTED']) if props.rand_furniture_style else props.column_ornament_style
    table_shapes = ['MODERN_DESK', 'MONITOR_RISER_DESK', 'L_SHAPED_CORNER', 'RECTANGLE', 'ROUNDED_RECT', 'OVAL']
    final_table_shape = random.choice(table_shapes) if props.rand_furniture_style else props.table_shape
    
    chair_backs = ['SOLID', 'SPINDLE', 'OVAL']
    final_chair_back = random.choice(chair_backs) if props.rand_furniture_style else props.chair_back_style
    chair_seats = ['CUSHION', 'WOOD_FLAT']
    final_chair_seat = random.choice(chair_seats) if props.rand_furniture_style else props.chair_seat_style
    chair_legs = ['FOUR_LEGS', 'PEDESTAL_ONE', 'X_CROSS', 'TRIPOD_THREE']
    final_chair_leg = random.choice(chair_legs) if props.rand_furniture_style else props.chair_leg_layout

    return {
        "category": cat,
        "style": final_type,
        "floor_shape": props.floor_shape,
        "wall_shape": props.wall_shape,
        "grass_mode": props.grass_mode,
        "water_shape": props.water_shape,
        "water_color_type": props.water_color_type,
        "water_wave_strength": props.water_wave_strength,
        "water_include_bed": props.water_include_bed,
        "table_shape": final_table_shape,
        "table_leg_style": final_leg_style,
        "chair_type": props.chair_type,
        "chair_seat_style": final_chair_seat,
        "chair_back_style": final_chair_back,
        "chair_leg_layout": final_chair_leg,
        "chest_tiers": props.chest_tiers,
        "chest_handle_style": props.chest_handle_style,
        "bed_size": props.bed_size,
        "shelf_tiers": props.shelf_tiers,
        "column_style": final_col_style,
        "tree_species": props.tree_species,
        "tree_has_leaves": props.tree_has_leaves,
        "tree_leaf_style": props.tree_leaf_style,
        "tree_leaf_count": props.tree_leaf_count,
        "tree_branch_levels": props.tree_branch_levels,
        "tree_curvature": props.tree_curvature,
        "tree_mat_mode": props.tree_material_mode,
        "uv_mode": props.uv_mapping_mode,
        "size_x": final_sx,
        "size_y": final_sy,
        "size_z": final_sz,
        "roughness": props.roughness,
        "chisel_strength": props.chisel_strength,
        "crack_depth": props.crack_depth,
        "big_chunk_cuts": props.big_chunk_cuts,
        "crack_count": props.floor_crack_count,
        "create_debris": False if cat in ("FLOOR", "WALL", "GRASS", "BOOKSHELF", "TABLE", "PC_DESK", "CHAIR", "OFFICE_CHAIR", "CHEST", "BED", "TREE", "WATER", "FENCE", "BUSH") else props.create_debris,
        "debris_count": props.debris_count,
        "detail_level": props.detail_level,
        "tex_folder": props.texture_folder,
        "use_folder_tex": props.use_folder_texture,
        "selected_tex": chosen_tex,
        "tex_tiling": props.texture_tiling,
        "enable_disp": props.enable_displacement,
        "disp_strength": props.displacement_strength,
        "disp_midlevel": props.displacement_midlevel,
        "disp_subdiv": props.displacement_subdiv,
        "apply_disp": props.apply_disp_to_mesh,
        "rock_palette": props.rock_palette,
        "fence_type": props.fence_type,
        "fence_rails_count": props.fence_rails_count,
        "fence_post_spacing": props.fence_post_spacing,
        "fence_decay_jitter": props.fence_decay_jitter,
        "bush_type": props.bush_type,
        "bush_foliage_style": props.bush_foliage_style,
        "bush_density": props.bush_density,
        "bush_leaf_size": props.bush_leaf_size,
        "water_animate": props.water_animate,
        "water_wind_speed": props.water_wind_speed,
        "water_anim_frames": props.water_anim_frames,
        "pillar_type": props.pillar_type,
        "pillar_mat_type": props.pillar_mat_type,
        "pillar_height": props.pillar_height,
        "pillar_radius": props.pillar_radius,
        "pillar_colonnettes": props.pillar_colonnettes,
        "pillar_flutes": props.pillar_flutes,
        "telescope_elevation": props.telescope_elevation_angle,
        "telescope_azimuth": props.telescope_azimuth_angle,
        "telescope_tripod_height": props.telescope_tripod_height,
        "telescope_tube_length": props.telescope_tube_length,
    }


def generate_procedural_prop_mesh(
    context,
    target_obj=None,
    category="ROCK",
    name="Prop_Asset",
    style="FRACTURED",
    floor_shape="SQUARE",
    wall_shape="STRAIGHT",
    grass_mode="MOUND",
    table_shape="RECTANGLE",
    table_leg_style="ORNAMENTAL",
    chair_type="DINING_CHAIR",
    chair_seat_style="CUSHION",
    chair_back_style="SOLID",
    chair_leg_layout="FOUR_LEGS",
    chest_tiers=3,
    chest_handle_style="RING",
    bed_size="SINGLE",
    shelf_tiers=3,
    column_style="ORNAMENTAL",
    pillar_type="GOTHIC_CLUSTERED",
    pillar_mat_type="MARBLE",
    pillar_height=4.0,
    pillar_radius=0.4,
    pillar_colonnettes=6,
    pillar_flutes=18,
    telescope_elevation=25.0,
    telescope_azimuth=45.0,
    telescope_tripod_height=1.0,
    telescope_tube_length=0.75,
    water_shape="LAKE",
    water_color_type="TROPICAL",
    water_wave_strength=0.12,
    water_include_bed=True,
    water_animate=True,
    water_wind_speed=1.0,
    water_anim_frames=60,
    tree_species="OAK",
    tree_has_leaves=True,
    tree_leaf_count=120,
    tree_branch_levels=2,
    tree_leaf_style="QUAD_CROSS",
    tree_curvature=0.6,
    tree_mat_mode="PROCEDURAL",
    fence_type="POST_AND_RAIL",
    fence_rails_count=2,
    fence_post_spacing=1.8,
    fence_decay_jitter=0.03,
    bush_type="ROUND_BUSH",
    bush_foliage_style="LEAF_CARDS",
    bush_density=18,
    bush_leaf_size=0.35,
    uv_mode="FIT",
    size_x=2.0,
    size_y=2.0,
    size_z=1.5,
    roughness=0.7,
    chisel_strength=0.8,
    crack_depth=0.6,
    big_chunk_cuts=2,
    crack_count=5,
    create_debris=True,
    debris_count=6,
    detail_level=2,
    tex_folder=r"Z:\MeshCreator\textures\Rock",
    use_folder_tex=True,
    selected_tex="",
    tex_tiling=1.0,
    enable_disp=False,
    disp_strength=0.15,
    disp_midlevel=0.5,
    disp_subdiv=2,
    apply_disp=True,
    rock_palette="AUTO",
    seed=0
):
    if context.mode != 'OBJECT':
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass

    random.seed(seed)

    # 🔭 Telescope Preset (天体望遠鏡: 三脚・マウント・鏡筒 独立階層)
    if category == "TELESCOPE":
        from .cleanup_helper import cleanup_old_telescope
        cleanup_old_telescope(context, target_obj, name)
        root_obj = create_procedural_telescope(
            context=context,
            name=name,
            elevation_deg=telescope_elevation,
            azimuth_deg=telescope_azimuth,
            tripod_height=telescope_tripod_height,
            tube_length=telescope_tube_length,
            seed=seed
        )
        return root_obj

    # 🏛️ Pillar Preset (ゴシック束ね柱 / ローマ溝彫り円柱 / 遺跡 / 角柱)
    if category == "PILLAR":

        if target_obj:
            try:
                bpy.data.objects.remove(target_obj, do_unlink=True)
            except Exception:
                pass
        obj = create_procedural_pillar(
            context=context,
            name=name,
            pillar_type=pillar_type,
            height=size_z if size_z > 1.0 else pillar_height,
            radius=min(size_x, size_y) * 0.35 if min(size_x, size_y) > 0.3 else pillar_radius,
            colonnettes=pillar_colonnettes,
            flutes=pillar_flutes,
            mat_type=pillar_mat_type,
            seed=seed
        )
        mat = create_procedural_pillar_shader(f"{name}_{pillar_mat_type}_Mat", mat_type=pillar_mat_type, seed=seed)
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        return obj

    # Tree Preset
    if category == "TREE":
        return generate_sapling_real_tree(
            context=context,
            target_obj=target_obj,
            name=name,
            species=tree_species,
            has_leaves=tree_has_leaves,
            leaf_count=tree_leaf_count,
            branch_levels=tree_branch_levels,
            leaf_style=tree_leaf_style,
            mat_mode=tree_mat_mode,
            seed=seed,
            size_z=size_z
        )

    cleanup_old_debris(context, name if not target_obj else target_obj.name)

    if target_obj and target_obj.type == 'MESH':
        obj = target_obj
        obj.name = name
        mesh = obj.data
        mesh.name = name + "_Mesh"
        mesh.clear_geometry()
        obj.modifiers.clear()
        obj.data.materials.clear()
    else:
        mesh = bpy.data.meshes.new(name + "_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        context.collection.objects.link(obj)

    context.view_layer.objects.active = obj
    obj.select_set(True)

    # 1. Base Geometry Construction
    bm = bmesh.new()
    if category in ("CHAIR", "OFFICE_CHAIR"):
        build_chair_base(
            bm, size_x, size_y, size_z,
            chair_type=chair_type,
            leg_style=table_leg_style,
            seat_style=chair_seat_style,
            back_style=chair_back_style,
            leg_layout=chair_leg_layout,
            seed=seed
        )
    elif category == "CHEST":
        build_chest_base(bm, size_x, size_y, size_z, tiers=chest_tiers, handle_style=chest_handle_style, seed=seed)
    elif category == "BED":
        build_bed_base(bm, size_x, size_y, size_z, bed_size=bed_size, leg_style=column_style, seed=seed)
    elif category == "BOOKSHELF":
        build_bookshelf_base(bm, size_x, size_y, size_z, tiers=shelf_tiers, column_style=column_style, seed=seed)
    elif category in ("TABLE", "PC_DESK"):
        build_table_base(bm, size_x, size_y, size_z, shape=table_shape, leg_style=table_leg_style, seed=seed)
    elif category == "BUSH":
        build_bush_mesh(
            bm,
            bush_type=bush_type,
            foliage_style=bush_foliage_style,
            size_x=size_x,
            size_y=size_y,
            size_z=size_z,
            density=bush_density,
            leaf_size=bush_leaf_size,
            seed=seed
        )
    elif category == "FENCE":
        build_wooden_fence_mesh(
            bm,
            fence_type=fence_type,
            length=size_x,
            height=size_z,
            rails_count=fence_rails_count,
            post_spacing=fence_post_spacing,
            decay_jitter=fence_decay_jitter,
            seed=seed
        )
    elif category == "WATER":
        build_water_surface_base(bm, size_x, size_y, size_z, shape=water_shape, seed=seed, include_bed=water_include_bed)
    elif category == "GRASS":
        if grass_mode == "TUFT":
            build_grass_tuft_clump(bm, size_x, size_y, size_z, blade_count=4, seed=seed)
        else:
            build_grass_mound_base(bm, size_x, size_y, size_z, shape=floor_shape, seed=seed)
    elif category == "FLOOR":
        build_floor_base(bm, size_x, size_y, size_z, shape=floor_shape, seed=seed)
    elif category == "WALL":
        build_wall_base(bm, size_x, size_y, size_z, shape=wall_shape, seed=seed)
    elif category == "PILLAR":
        build_pillar_base(bm, size_x, size_y, size_z)
    elif category == "BEAM":
        build_beam_base(bm, size_x, size_y, size_z)
    elif category == "BEAM_ARCH":
        build_beam_arch_base(bm, size_x, size_y, size_z)
    elif category == "CRAG":
        build_crag_base(bm, size_x, size_y, size_z, style=style, chisel_cuts=big_chunk_cuts * 3 + 4, seed=seed)
    else: # ROCK (丸岩・巨石)
        build_rock_base(bm, size_x, size_y, size_z, style=style, seed=seed)

    # Debris (Rock / Crag only)
    if create_debris and debris_count > 0 and category in ("ROCK", "CRAG"):
        max_rad = max(size_x, size_y)
        for i in range(debris_count):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(max_rad * 0.55, max_rad * 0.95)
            dx = math.cos(angle) * dist
            dy = math.sin(angle) * dist
            dz = -size_z * 0.35 + random.uniform(-0.05, 0.08)
            d_rad = random.uniform(0.12, 0.35)
            d_verts = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=d_rad)['verts']
            sx = random.uniform(0.8, 1.4)
            sy = random.uniform(0.8, 1.4)
            sz = random.uniform(0.5, 1.0)
            bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=d_verts)
            bmesh.ops.translate(bm, vec=(dx, dy, dz), verts=d_verts)

    bm.to_mesh(mesh)
    bm.free()

    # 2. Bevel for Furniture, Architecture & Grass Mound
    if category in ("FLOOR", "WALL", "PILLAR", "BEAM", "BEAM_ARCH", "BOOKSHELF", "TABLE", "PC_DESK", "CHAIR", "OFFICE_CHAIR", "CHEST", "BED") or (category == "GRASS" and grass_mode == "MOUND"):
        bevel_mod = obj.modifiers.new(name="Bevel_Chipping", type='BEVEL')
        bevel_mod.width = 0.012 if category in ("BOOKSHELF", "TABLE", "PC_DESK", "CHAIR", "OFFICE_CHAIR", "CHEST", "BED") else min(0.03, (size_z if category != "WALL" else size_y) * 0.15)
        bevel_mod.segments = 2
        try:
            bpy.ops.object.modifier_apply(modifier=bevel_mod.name)
        except Exception:
            pass

    # 3. Ocean Modifier for OCEAN preset
    if category == "WATER" and water_shape == "OCEAN":
        ocean_mod = obj.modifiers.new(name="Ocean_Wave", type='OCEAN')
        ocean_mod.geometry_mode = 'DISPLACE'
        ocean_mod.resolution = 12
        ocean_mod.spatial_size = int(max(size_x, size_y) * 2.0)
        ocean_mod.wind_velocity = 20.0
        ocean_mod.choppiness = 1.4
        ocean_mod.wave_scale = size_z * 0.4
        ocean_mod.use_foam = True
        ocean_mod.foam_coverage = 0.35
        ocean_mod.foam_layer_name = "foam"

    # 4. Subdivision & Displacements (🪨 岩石・険岩専用 - 建築・家具への副作用を完全防止)
    if category in ("ROCK", "CRAG"):
        subsurf = obj.modifiers.new(name="Subsurf_Base", type='SUBSURF')
        subsurf.render_levels = min(4, detail_level + 2)
        subsurf.levels = min(4, detail_level + 2)

        # 4-1. 大まかなうねり (Disp_Large)
        tex_large = bpy.data.textures.new(name + "_Tex_Large", type='VORONOI' if category == "CRAG" else 'CLOUDS')
        if category == "CRAG":
            tex_large.noise_scale = 0.95
            tex_large.distance_metric = 'DISTANCE_SQUARED'
        else:
            tex_large.noise_scale = 1.6 if category in ("BEAM", "BEAM_ARCH") else 1.2
            tex_large.noise_depth = 2 if category in ("BEAM", "BEAM_ARCH") else 3
        
        disp_large = obj.modifiers.new(name="Disp_Large", type='DISPLACE')
        disp_large.texture = tex_large
        disp_large.strength = roughness * (0.35 if category == "CRAG" else 0.42)
        disp_large.mid_level = 0.5

        # 4-2. 微細ディテール (Disp_Small)
        if category in ("ROCK", "CRAG"):
            tex_small = bpy.data.textures.new(name + "_Tex_Small", type='CLOUDS')
            tex_small.noise_scale = 0.12
            tex_small.noise_depth = 4
            
            disp_small = obj.modifiers.new(name="Disp_Small", type='DISPLACE')
            disp_small.texture = tex_small
            disp_small.texture_coords = 'LOCAL'
            disp_small.strength = roughness * 0.15
            disp_small.mid_level = 0.5

        # 4-3. チゼル加工 (Disp_Chisel)
        if chisel_strength > 0.05:
            tex_voronoi = bpy.data.textures.new(name + "_Tex_Chisel", type='VORONOI' if category in ("ROCK", "CRAG") else 'WOOD')
            if category in ("ROCK", "CRAG"):
                tex_voronoi.noise_scale = 0.65 if category == "CRAG" else 0.8
                tex_voronoi.distance_metric = 'DISTANCE'
            else:
                tex_voronoi.noise_scale = 0.8
            disp_voronoi = obj.modifiers.new(name="Disp_Chisel", type='DISPLACE')
            disp_voronoi.texture = tex_voronoi
            disp_voronoi.strength = chisel_strength * (0.35 if category == "CRAG" else 0.5)
            disp_voronoi.mid_level = 0.5

        # 4-4. ひび割れ (Disp_Crack)
        if crack_depth > 0.05:
            tex_crack = bpy.data.textures.new(name + "_Tex_Crack", type='VORONOI')
            tex_crack.noise_scale = 0.4 if category == "CRAG" else 0.5
            tex_crack.distance_metric = 'DISTANCE'
            disp_crack = obj.modifiers.new(name="Disp_Crack", type='DISPLACE')
            disp_crack.texture = tex_crack
            disp_crack.strength = -crack_depth * (0.25 if category == "CRAG" else 0.4)
            disp_crack.mid_level = 0.85

    # 4-5. 水面微風アニメーション (動画 7:58 準拠 Ocean Modifier Timeキーフレーム)
    if category == "WATER" and water_animate:
        setup_water_ocean_animation(obj, wind_speed=water_wind_speed, anim_frames=water_anim_frames)

    # Apply Modifiers
    for p in mesh.polygons:
        p.use_smooth = True

    if not (category == "WATER" and water_animate):
        for mod in list(obj.modifiers):
            try:
                bpy.ops.object.modifier_apply(modifier=mod.name)
            except Exception:
                pass

    if category == "CRAG":
        try:
            mesh.use_auto_smooth = True
            mesh.auto_smooth_angle = math.radians(40.0)
        except Exception:
            pass

    # 5. Smart UV Projection
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    if category == "GRASS" and grass_mode == "TUFT":
        bpy.ops.uv.smart_project(angle_limit=88.0, island_margin=0.0)
    elif category in ("FLOOR", "WALL", "BEAM", "BEAM_ARCH", "GRASS", "BOOKSHELF", "TABLE", "CHAIR", "CHEST", "BED", "WATER", "FENCE", "BUSH"):
        if uv_mode == "FIT":
            max_dim = max(size_x, size_y, size_z)
            bpy.ops.uv.cube_project(cube_size=max_dim, correct_aspect=True, clip_to_bounds=True)
        else:
            bpy.ops.uv.cube_project(cube_size=2.0 / max(0.1, tex_tiling), correct_aspect=True)
    else: # ROCK
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
        
    bpy.ops.object.mode_set(mode='OBJECT')

    # 6. Material Assignment
    if category == "BUSH":
        mat_leaf = create_procedural_grass_blade_shader(name + "_Leaf_Mat", seed)
        mat_stem = create_procedural_pbr_material(name + "_Stem_Mat", seed + 5, is_grass=False)
        obj.data.materials.clear()
        obj.data.materials.append(mat_leaf)
        obj.data.materials.append(mat_stem)

        # 樹冠球状法線転送（ふんわり陰影）
        if bush_foliage_style == "LEAF_CARDS":
            try:
                apply_bush_spherical_normals(obj, leaf_mat_idx=0)
            except Exception:
                pass
    elif category == "FENCE":
        mat_wood = create_procedural_pbr_material(name + "_Wood_Mat", seed, is_grass=False)
        mat_rope = create_procedural_pbr_material(name + "_Rope_Mat", seed + 10, is_grass=False)
        obj.data.materials.clear()
        obj.data.materials.append(mat_wood)
        obj.data.materials.append(mat_rope)
    elif category == "GRASS":
        if grass_mode == "TUFT":
            mat = create_procedural_grass_blade_shader(name + "_Blade_Mat", seed)
        else:
            mat = create_procedural_ground_terrain_shader(name + "_Ground_Mat", seed)
        obj.data.materials.clear()
        obj.data.materials.append(mat)
    elif category == "WATER":
        mat_water = create_procedural_water_shader(
            name + "_Water_Surface_Mat",
            color_type=water_color_type,
            wave_strength=water_wave_strength,
            seed=seed
        )
        obj.data.materials.clear()
        obj.data.materials.append(mat_water)

        if water_shape == "POND" and water_include_bed:
            mat_bed = create_procedural_water_bed_shader(name + "_Water_Bed_Mat", seed=seed)
            obj.data.materials.append(mat_bed)
    elif category in ("ROCK", "CRAG"):
        tex_files = get_textures_from_folder(tex_folder)
        disp_img = None
        if use_folder_tex and tex_files:
            chosen_tex = selected_tex if (selected_tex and selected_tex in tex_files) else random.choice(tex_files)
            full_tex_path = os.path.join(tex_folder, chosen_tex)
            pbr_set = find_pbr_texture_set(full_tex_path)
            disp_img = pbr_set.get('displacement') or full_tex_path

            apply_image_texture_material(
                obj, full_tex_path,
                scale=1.0 if uv_mode == "FIT" else tex_tiling,
                bump_strength=0.35,
                displacement_strength=disp_strength if enable_disp else 0.0,
                is_transparent=False
            )
        else:
            mat = build_procedural_rock_material(name + "_Rock_Mat", seed, palette=rock_palette)
            obj.data.materials.clear()
            obj.data.materials.append(mat)

        if enable_disp and disp_strength > 0.001:
            apply_geometry_displacement(
                obj,
                disp_image_path=disp_img,
                strength=disp_strength,
                midlevel=disp_midlevel,
                subdivisions=disp_subdiv,
                apply_modifier=apply_disp
            )
    else:
        tex_files = get_textures_from_folder(tex_folder)
        disp_img = None
        if use_folder_tex and tex_files:
            chosen_tex = selected_tex if (selected_tex and selected_tex in tex_files) else random.choice(tex_files)
            full_tex_path = os.path.join(tex_folder, chosen_tex)
            pbr_set = find_pbr_texture_set(full_tex_path)
            disp_img = pbr_set.get('displacement') or full_tex_path

            apply_image_texture_material(
                obj, full_tex_path,
                scale=1.0 if uv_mode == "FIT" else tex_tiling,
                bump_strength=0.35,
                displacement_strength=disp_strength if enable_disp else 0.0,
                is_transparent=False
            )
        else:
            mat = create_procedural_pbr_material(name + "_Mat", seed, is_grass=False)
            obj.data.materials.append(mat)

        if enable_disp and disp_strength > 0.001 and category in ("WALL", "FLOOR", "PILLAR", "BEAM", "BEAM_ARCH", "TABLE", "PC_DESK", "CHEST"):
            apply_geometry_displacement(
                obj,
                disp_image_path=disp_img,
                strength=disp_strength,
                midlevel=disp_midlevel,
                subdivisions=disp_subdiv,
                apply_modifier=apply_disp
            )

    return obj
