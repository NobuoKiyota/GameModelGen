import bpy
import bmesh
import math
import random
import os

from ..materials.rock_shaders import build_procedural_rock_material
from ..materials.nature_shaders import (
    create_procedural_grass_blade_shader,
    create_procedural_bush_leaf_shader,
    create_procedural_ground_terrain_shader,
    create_procedural_water_shader,
    create_procedural_water_bed_shader,
    create_procedural_pillar_shader,
    create_procedural_cobblestone_shader
)
from ..materials.image_shaders import (
    apply_image_texture_material,
    apply_weathered_stone_arch_material,
    create_window_glass_material,
    create_window_iron_material
)
from ..utils.texture_utils import get_textures_from_folder, find_pbr_texture_set
from ..utils.mesh_utils import apply_geometry_displacement

from .rock_gen import build_rock_base, build_crag_base
from .architecture_gen import (
    build_floor_base,
    build_wall_base,
    build_pillar_base,
    build_beam_base,
    build_beam_arch_base,
    build_procedural_stone_arch_bmesh,
    build_modular_relief_wall_mesh,
    build_western_window_mesh
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
    build_dense_meadow_field_mesh,
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
        elif cat == "BEAM":
            final_sx = round(random.uniform(1.8, 3.5), 2)
            final_sy = round(random.uniform(1.5, 2.5), 2)
            final_sz = round(random.uniform(1.8, 2.8), 2)
        elif cat == "BEAM_ARCH":
            final_sx = round(random.uniform(3.0, 4.2), 2)
            final_sy = round(random.uniform(0.6, 0.9), 2)
            final_sz = round(random.uniform(3.4, 4.4), 2)
        elif cat == "RELIEF_WALL":
            final_sx = round(random.uniform(2.8, 3.6), 2)
            final_sy = round(random.uniform(0.35, 0.45), 2)
            final_sz = round(random.uniform(3.2, 4.0), 2)
        elif cat == "WINDOW":
            final_sx = round(random.uniform(1.2, 2.0), 2)
            final_sy = round(random.uniform(0.28, 0.40), 2)
            final_sz = round(random.uniform(2.0, 3.0), 2)
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
        "cobble_stone_size": props.cobble_stone_size,
        "cobble_grout_depth": props.cobble_grout_depth,
        "cobble_jitter": props.cobble_jitter,
        "grass_mode": props.grass_mode,
        "terrain_type": props.terrain_type,
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
        "bush_include_fiddleheads": getattr(props, "bush_include_fiddleheads", True),
        "water_animate": props.water_animate,
        "water_wind_speed": props.water_wind_speed,
        "water_anim_frames": props.water_anim_frames,
        "pillar_type": props.pillar_type,
        "pillar_mat_type": props.pillar_mat_type,
        "pillar_height": props.pillar_height,
        "pillar_radius": props.pillar_radius,
        "pillar_colonnettes": props.pillar_colonnettes,
        "pillar_flutes": props.pillar_flutes,
        "pillar_entasis": props.pillar_entasis,
        "pillar_include_railing": getattr(props, "pillar_include_railing", True),
        "pillar_railing_length": getattr(props, "pillar_railing_length", 1.6),
        "pillar_pedestal_width": getattr(props, "pillar_pedestal_width", 0.72),
        "pillar_pedestal_height": getattr(props, "pillar_pedestal_height", 1.05),
        "telescope_style": props.telescope_style,
        "telescope_elevation": props.telescope_elevation_angle,
        "telescope_azimuth": props.telescope_azimuth_angle,
        "telescope_tripod_height": props.telescope_tripod_height,
        "telescope_tube_length": props.telescope_tube_length,
        # Castle Wall parameters
        "castle_wall_shape": random.choice(['STRAIGHT', 'BATTLEMENT', 'TOWER_CURVED', 'CORNER_L', 'CRANK_Z', 'GATE_ARCH']) if props.castle_wall_shape == 'RANDOM' else props.castle_wall_shape,
        "castle_wall_style": props.castle_wall_style,
        "castle_wall_stone_aspect": props.castle_wall_stone_aspect,
        "castle_wall_stone_roundness": props.castle_wall_stone_roundness,
        "castle_wall_stone_chipping": props.castle_wall_stone_chipping,
        "castle_wall_length": round(random.uniform(4.0, 9.0), 1) if getattr(props, 'castle_wall_randomize_dimensions', False) else props.castle_wall_length,
        "castle_wall_height": round(random.uniform(2.5, 5.0), 1) if getattr(props, 'castle_wall_randomize_dimensions', False) else props.castle_wall_height,
        "castle_wall_thickness": round(random.uniform(0.9, 1.8), 1) if getattr(props, 'castle_wall_randomize_dimensions', False) else props.castle_wall_thickness,
        "castle_wall_has_crenels": random.choice([True, False]) if getattr(props, 'castle_wall_randomize_dimensions', False) else props.castle_wall_has_crenels,
        "castle_wall_density": props.castle_wall_density,
        "castle_wall_min_dist": props.castle_wall_min_dist,
        "castle_wall_jitter": props.castle_wall_jitter,
        "castle_wall_batter": props.castle_wall_batter,
        "castle_wall_roughness": props.castle_wall_roughness,
        # Cave parameters
        "cave_path_type": random.choice(['S_CURVE', 'STRAIGHT', 'Z_CRANK', 'CHAMBER_HALL']) if props.cave_path_type == 'RANDOM' else props.cave_path_type,
        "cave_rock_style": props.cave_rock_style,
        "cave_has_river": props.cave_has_river,
        "cave_river_width": round(random.uniform(3.0, 6.0), 1) if getattr(props, 'cave_randomize_shape', False) else props.cave_river_width,
        "cave_river_depth": round(random.uniform(0.9, 1.8), 2) if getattr(props, 'cave_randomize_shape', False) else props.cave_river_depth,
        "cave_terrace_steps": random.randint(3, 6) if getattr(props, 'cave_randomize_shape', False) else props.cave_terrace_steps,
        "cave_floor_width": props.cave_floor_width,
        "cave_floor_length": props.cave_floor_length,
        "cave_roughness": props.cave_roughness,
        "cave_generate_ceiling": props.cave_generate_ceiling,
        "cave_ceiling_height": props.cave_ceiling_height,
        "cave_ceiling_overhang": props.cave_ceiling_overhang,
        "cave_ceiling_fissure": props.cave_ceiling_fissure,
        "cave_ceiling_roughness": props.cave_ceiling_roughness,
        "cave_setup_lights": props.cave_setup_lights,
        "cave_light_intensity": props.cave_light_intensity,
        "cave_generate_pillars": getattr(props, 'cave_generate_pillars', True),
        "cave_pillar_count": getattr(props, 'cave_pillar_count', 4),
        "cave_generate_stalactites": getattr(props, 'cave_generate_stalactites', True),
        "cave_stalactite_density": getattr(props, 'cave_stalactite_density', 1.0),
        "cave_generate_boulders": getattr(props, 'cave_generate_boulders', True),
        "cave_boulder_count": getattr(props, 'cave_boulder_count', 16),
        "cave_add_moss": getattr(props, 'cave_add_moss', True),
        "cave_moss_amount": getattr(props, 'cave_moss_amount', 0.6),
        # Arch parameters
        "arch_style": getattr(props, 'arch_style', 'ROMAN_ROUND'),
        "arch_structure_type": getattr(props, 'arch_structure_type', 'SINGLE'),
        "arch_span_count": getattr(props, 'arch_span_count', 3),
        "arch_has_keystone": getattr(props, 'arch_has_keystone', True),
        "arch_keystone_scale": getattr(props, 'arch_keystone_scale', 1.25),
        "arch_molding_tiers": getattr(props, 'arch_molding_tiers', 2),
        "arch_pillar_shape": getattr(props, 'arch_pillar_shape', 'SQUARE_PIER'),
        "arch_pillar_width": getattr(props, 'arch_pillar_width', 0.55),
        "arch_column_height": getattr(props, 'arch_column_height', 2.2),
        "arch_damage": getattr(props, 'arch_damage', 0.35),
        "arch_weathering": getattr(props, 'arch_weathering', 0.50),
        "arch_moss_amount": getattr(props, 'arch_moss_amount', 0.30),
        "arch_has_spandrel": getattr(props, 'arch_has_spandrel', True),
        "arch_has_pedestal": getattr(props, 'arch_has_pedestal', True),
        # Relief Wall parameters
        "relief_style": getattr(props, 'relief_style', 'ROSETTE'),
        "relief_wall_bays": getattr(props, 'relief_wall_bays', 1),
        "relief_depth": getattr(props, 'relief_depth', 0.035),
        "relief_pilaster_width": getattr(props, 'relief_pilaster_width', 0.40),
        "relief_pilaster_depth": getattr(props, 'relief_pilaster_depth', 0.08),
        "relief_frame_bevel": getattr(props, 'relief_frame_bevel', 0.12),
        "relief_damage": getattr(props, 'relief_damage', 0.35),
        "relief_weathering": getattr(props, 'relief_weathering', 0.50),
        "relief_moss_amount": getattr(props, 'relief_moss_amount', 0.30),
        "relief_custom_image": getattr(props, 'relief_custom_image', ""),
        # Western Window parameters
        "window_frame_style": getattr(props, 'window_frame_style', 'GOTHIC_POINTED'),
        "window_grille_style": getattr(props, 'window_grille_style', 'SUNBURST'),
        "window_arch_style": getattr(props, 'window_arch_style', 'MOLDED_FRENCH'),
        "window_jamb_style": getattr(props, 'window_jamb_style', 'ENGAGED_FLUTED'),
        "window_column_flutes": getattr(props, 'window_column_flutes', 8),
        "window_column_pedestal": getattr(props, 'window_column_pedestal', True),
        "window_has_keystone": getattr(props, 'window_has_keystone', True),
        "window_wire_density": getattr(props, 'window_wire_density', 6),
        "window_wire_thickness": getattr(props, 'window_wire_thickness', 0.012),
        "window_frame_width": getattr(props, 'window_frame_width', 0.18),
        "window_has_sill": getattr(props, 'window_has_sill', True),
        "window_has_hood": getattr(props, 'window_has_hood', True),
        "window_damage": getattr(props, 'window_damage', 0.30),
        "window_weathering": getattr(props, 'window_weathering', 0.50),
        "window_moss_amount": getattr(props, 'window_moss_amount', 0.25),
    }


def generate_procedural_prop_mesh(
    context,
    target_obj=None,
    category="ROCK",
    name="Prop_Asset",
    style="FRACTURED",
    floor_shape="SQUARE",
    wall_shape="STRAIGHT",
    cobble_stone_size=0.35,
    cobble_grout_depth=0.035,
    cobble_jitter=0.45,
    grass_mode="MOUND",
    terrain_type="MEADOW",
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
    pillar_type="CLASSIC_FLUTED",
    pillar_mat_type="MARBLE",
    pillar_height=4.0,
    pillar_radius=0.4,
    pillar_colonnettes=6,
    pillar_flutes=16,
    pillar_entasis=0.08,
    telescope_style="MODERN_REFRACTOR",
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
    bush_include_fiddleheads=True,
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
    seed=0,
    **kwargs
):
    if context.mode != 'OBJECT':
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass

    random.seed(seed)

    # 🏰 Castle Wall Preset (中世城壁・石積み壁)
    if category == "CASTLE_WALL":
        from .castle_wall_gen import create_castle_wall_scene
        c_shape = kwargs.get('castle_wall_shape', 'STRAIGHT')
        c_style = kwargs.get('castle_wall_style', 'ASHLAR')
        c_len = kwargs.get('castle_wall_length', 6.0)
        c_h = kwargs.get('castle_wall_height', 3.5)
        c_t = kwargs.get('castle_wall_thickness', 1.2)
        c_crenels = kwargs.get('castle_wall_has_crenels', True)
        c_dens = kwargs.get('castle_wall_density', 22.0)
        c_min_d = kwargs.get('castle_wall_min_dist', 0.22)
        c_jit = kwargs.get('castle_wall_jitter', 0.04)
        c_bat = kwargs.get('castle_wall_batter', 0.18)
        c_rough = kwargs.get('castle_wall_roughness', 0.14)
        c_rnd = kwargs.get('castle_wall_stone_roundness', 0.035)
        c_chip = kwargs.get('castle_wall_stone_chipping', 0.016)
        c_asp = kwargs.get('castle_wall_stone_aspect', 'STANDARD')

        wall_obj, _ = create_castle_wall_scene(
            context=context,
            name=name,
            seed=seed,
            wall_shape=c_shape,
            wall_style=c_style,
            stone_aspect=c_asp,
            stone_roundness=c_rnd,
            stone_chipping=c_chip,
            length=c_len,
            height=c_h,
            thickness=c_t,
            crenels=c_crenels,
            density=c_dens,
            min_dist=c_min_d,
            jitter=c_jit,
            batter=c_bat,
            roughness=c_rough,
            target_obj=target_obj
        )
        return wall_obj

    # 🪨 Cave & Cave Floor Presets (洞窟フロア基盤＆ジオラマ)
    if category in ("CAVE", "CAVE_FLOOR"):
        from .cave_gen import create_procedural_cave_scene
        import re
        # Strip any existing suffixes to strictly prevent object duplication
        prefix = "Cave_Floor" if category == "CAVE_FLOOR" else "Cave_Dungeon"
        cave_clean_name = re.sub(r'(_Floor|_Water|_Puddles|_Ceiling|_Pillars|_Debris)+$', '', name).strip() or prefix
        c_path = kwargs.get('cave_path_type', 'S_CURVE')
        c_style = kwargs.get('cave_rock_style', 'SLATE')
        c_w_type = kwargs.get('cave_water_type', 'PUDDLES')
        c_river = kwargs.get('cave_has_river', True)
        c_p_cnt = kwargs.get('cave_puddle_count', 6)
        c_p_scale = kwargs.get('cave_puddle_scale', 2.4)
        c_r_w = kwargs.get('cave_river_width', 4.5)
        c_r_d = kwargs.get('cave_river_depth', 1.3)
        c_steps = kwargs.get('cave_terrace_steps', 4)
        c_f_w = kwargs.get('cave_floor_width', 18.0)
        c_f_l = kwargs.get('cave_floor_length', 35.0)
        c_rough = kwargs.get('cave_roughness', 0.8)
        
        # In CAVE_FLOOR mode, strictly focus on Floor & Water without ceiling/pillars
        if category == "CAVE_FLOOR":
            c_ceil = False
            c_pillars = False
            c_stalactites = False
            c_boulders = False
        else:
            c_ceil = kwargs.get('cave_generate_ceiling', True)
            c_pillars = kwargs.get('cave_generate_pillars', True)
            c_stalactites = kwargs.get('cave_generate_stalactites', True)
            c_boulders = kwargs.get('cave_generate_boulders', True)

        c_c_h = kwargs.get('cave_ceiling_height', 6.5)
        c_c_o = kwargs.get('cave_ceiling_overhang', 0.85)
        c_c_f = kwargs.get('cave_ceiling_fissure', 0.3)
        c_c_r = kwargs.get('cave_ceiling_roughness', 0.9)
        c_lights = kwargs.get('cave_setup_lights', True)
        c_l_int = kwargs.get('cave_light_intensity', 1.0)
        c_p_count = kwargs.get('cave_pillar_count', 4)
        c_s_dens = kwargs.get('cave_stalactite_density', 1.0)
        c_b_count = kwargs.get('cave_boulder_count', 16)
        c_moss = kwargs.get('cave_add_moss', True)
        c_m_amt = kwargs.get('cave_moss_amount', 0.6)

        floor_obj, water_obj, ceil_obj, pillar_obj, debris_obj = create_procedural_cave_scene(
            context=context,
            name=cave_clean_name,
            seed=seed,
            path_type=c_path,
            rock_style=c_style,
            water_type=c_w_type,
            has_river=c_river,
            puddle_count=c_p_cnt,
            puddle_scale=c_p_scale,
            floor_width=c_f_w,
            floor_length=c_f_l,
            river_width=c_r_w,
            river_depth=c_r_d,
            terrace_steps=c_steps,
            roughness=c_rough,
            ceiling_height=c_c_h,
            ceiling_overhang=c_c_o,
            ceiling_fissure=c_c_f,
            ceiling_roughness=c_c_r,
            generate_ceiling=c_ceil,
            generate_pillars=c_pillars,
            pillar_count=c_p_count,
            generate_stalactites=c_stalactites,
            stalactite_density=c_s_dens,
            generate_boulders=c_boulders,
            boulder_count=c_b_count,
            add_moss=c_moss,
            moss_amount=c_m_amt,
            setup_lights=c_lights,
            light_intensity=c_l_int,
            target_obj=target_obj
        )
        return floor_obj

    # 🔭 Telescope Preset (天体望遠鏡: 三脚・マウント・鏡筒 独立階層)
    if category == "TELESCOPE":
        from .cleanup_helper import cleanup_old_telescope
        cleanup_old_telescope(context, target_obj, name)
        root_obj = create_procedural_telescope(
            context=context,
            name=name,
            style=telescope_style,
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
        h_val = pillar_height if pillar_height > 0.5 else (size_z if size_z > 1.0 else 3.8)
        r_val = pillar_radius if pillar_radius > 0.05 else (min(size_x, size_y) * 0.35 if min(size_x, size_y) > 0.3 else 0.26)
        obj = create_procedural_pillar(
            context=context,
            name=name,
            pillar_type=pillar_type,
            height=h_val,
            radius=r_val,
            colonnettes=pillar_colonnettes,
            flutes=pillar_flutes,
            entasis=pillar_entasis,
            mat_type=pillar_mat_type,
            include_railing=kwargs.get('pillar_include_railing', True),
            railing_length=kwargs.get('pillar_railing_length', 1.6),
            pedestal_width=kwargs.get('pillar_pedestal_width', 0.72),
            pedestal_height=kwargs.get('pillar_pedestal_height', 1.05),
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
            include_fiddleheads=bush_include_fiddleheads,
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
            build_dense_meadow_field_mesh(bm, size_x, size_y, size_z, seed=seed, density_level=detail_level, terrain_type=terrain_type)
    elif category == "FLOOR":
        build_floor_base(bm, size_x, size_y, size_z, shape=floor_shape, seed=seed,
                         stone_size=cobble_stone_size, grout_depth=cobble_grout_depth, jitter=cobble_jitter)
    elif category == "WALL":
        build_wall_base(bm, size_x, size_y, size_z, shape=wall_shape, seed=seed,
                        stone_size=cobble_stone_size, grout_depth=cobble_grout_depth, jitter=cobble_jitter)
    elif category == "PILLAR":
        build_pillar_base(
            bm, size_x, size_y, size_z,
            style=pillar_type, flutes=pillar_flutes,
            colonnettes=pillar_colonnettes, entasis=pillar_entasis, seed=seed
        )
    elif category == "BEAM":
        build_beam_base(bm, size_x, size_y, size_z)
    elif category == "BEAM_ARCH":
        build_procedural_stone_arch_bmesh(
            bm, size_x, size_y, size_z,
            style=kwargs.get('arch_style', 'ROMAN_ROUND'),
            structure_type=kwargs.get('arch_structure_type', 'SINGLE'),
            span_count=kwargs.get('arch_span_count', 3),
            pillar_shape=kwargs.get('arch_pillar_shape', 'SQUARE_PIER'),
            pillar_width=kwargs.get('arch_pillar_width', 0.55),
            column_height=kwargs.get('arch_column_height', 2.2),
            damage=kwargs.get('arch_damage', 0.35),
            has_keystone=kwargs.get('arch_has_keystone', True),
            keystone_scale=kwargs.get('arch_keystone_scale', 1.25),
            molding_tiers=kwargs.get('arch_molding_tiers', 2),
            has_spandrel=kwargs.get('arch_has_spandrel', True),
            has_pedestal=kwargs.get('arch_has_pedestal', True),
            seed=seed
        )
    elif category == "RELIEF_WALL":
        build_modular_relief_wall_mesh(
            bm, size_x, size_y, size_z,
            bays=kwargs.get('relief_wall_bays', 1),
            relief_style=kwargs.get('relief_style', 'ROSETTE'),
            relief_depth=kwargs.get('relief_depth', 0.035),
            pilaster_width=kwargs.get('relief_pilaster_width', 0.40),
            pilaster_depth=kwargs.get('relief_pilaster_depth', 0.08),
            frame_bevel=kwargs.get('relief_frame_bevel', 0.12),
            damage=kwargs.get('relief_damage', 0.35),
            weathering=kwargs.get('relief_weathering', 0.50),
            moss_amount=kwargs.get('relief_moss_amount', 0.30),
            custom_image=kwargs.get('relief_custom_image', ""),
            seed=seed
        )
    elif category == "WINDOW":
        build_western_window_mesh(
            bm, size_x, size_y, size_z,
            frame_style=kwargs.get('window_frame_style', 'GOTHIC_POINTED'),
            grille_style=kwargs.get('window_grille_style', 'SUNBURST'),
            arch_style=kwargs.get('window_arch_style', 'MOLDED_FRENCH'),
            jamb_style=kwargs.get('window_jamb_style', 'ENGAGED_FLUTED'),
            column_flutes=kwargs.get('window_column_flutes', 8),
            column_pedestal=kwargs.get('window_column_pedestal', True),
            has_keystone=kwargs.get('window_has_keystone', True),
            wire_density=kwargs.get('window_wire_density', 6),
            wire_thickness=kwargs.get('window_wire_thickness', 0.012),
            frame_width=kwargs.get('window_frame_width', 0.18),
            has_sill=kwargs.get('window_has_sill', True),
            has_hood=kwargs.get('window_has_hood', True),
            damage=kwargs.get('window_damage', 0.30),
            seed=seed
        )
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
        if category == "BEAM_ARCH":
            bevel_mod.width = 0.008
        elif category in ("BOOKSHELF", "TABLE", "PC_DESK", "CHAIR", "OFFICE_CHAIR", "CHEST", "BED"):
            bevel_mod.width = 0.012
        else:
            bevel_mod.width = min(0.03, (size_z if category != "WALL" else size_y) * 0.15)
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
    
    if category == "GRASS":
        # GRASS は build_dense_meadow_field_mesh / build_grass_blade_with_uv 内で
        # 地面(Slot 0)と草ブレード(Slot 1)のUVが正しく分離生成されているため追加投影不要
        pass
    elif category in ("FLOOR", "WALL", "BEAM", "BEAM_ARCH", "BOOKSHELF", "TABLE", "CHAIR", "CHEST", "BED", "WATER", "FENCE", "BUSH"):
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
        mat_leaf = create_procedural_bush_leaf_shader(name + "_Leaf_Mat", seed)
        mat_stem = create_procedural_pbr_material(name + "_Stem_Mat", seed + 5, is_grass=False)
        if len(obj.data.materials) == 0:
            obj.data.materials.append(mat_leaf)
            obj.data.materials.append(mat_stem)
        else:
            obj.data.materials[0] = mat_leaf
            if len(obj.data.materials) > 1:
                obj.data.materials[1] = mat_stem
            else:
                obj.data.materials.append(mat_stem)

        # 樹冠球状法線転送（ふんわりハイブリッド陰影）
        if bush_foliage_style == "LEAF_CARDS":
            try:
                apply_bush_spherical_normals(obj, leaf_mat_idx=0, blend_factor=0.65)
            except Exception:
                pass
    elif category == "FENCE":
        mat_wood = create_procedural_pbr_material(name + "_Wood_Mat", seed, is_grass=False)
        mat_rope = create_procedural_pbr_material(name + "_Rope_Mat", seed + 10, is_grass=False)
        obj.data.materials.clear()
        obj.data.materials.append(mat_wood)
        obj.data.materials.append(mat_rope)
    elif category == "GRASS":
        obj.data.materials.clear()
        if grass_mode == "TUFT":
            mat = create_procedural_grass_blade_shader(name + "_Blade_Mat", seed)
            obj.data.materials.append(mat)
        else:
            # Slot 0: Ground (PBR or Procedural)
            tex_files = get_textures_from_folder(tex_folder)
            # diffuse / basecolor を優先
            diff_files = [f for f in tex_files if any(k in f.lower() for k in ('diff', 'basecolor', 'albedo', 'col'))]
            candidate_files = diff_files if diff_files else tex_files

            if use_folder_tex and candidate_files:
                chosen_tex = selected_tex if (selected_tex and selected_tex in candidate_files) else random.choice(candidate_files)
                full_tex_path = os.path.join(tex_folder, chosen_tex)
                apply_image_texture_material(
                    obj, full_tex_path,
                    scale=2.0 if uv_mode == "FIT" else tex_tiling,
                    bump_strength=0.35,
                    displacement_strength=disp_strength if enable_disp else 0.0,
                    is_transparent=False,
                    slot_index=0
                )
            else:
                mat_ground = create_procedural_ground_terrain_shader(name + "_Ground_Mat", seed=seed, terrain_type=terrain_type)
                if len(obj.data.materials) > 0:
                    obj.data.materials[0] = mat_ground
                else:
                    obj.data.materials.append(mat_ground)

            # Slot 1: Grass Blades & Weeds (Translucent BSDF)
            mat_blade = create_procedural_grass_blade_shader(name + "_Blade_Mat", seed=seed)
            if len(obj.data.materials) > 1:
                obj.data.materials[1] = mat_blade
            else:
                obj.data.materials.append(mat_blade)
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

            if category in ("BEAM_ARCH", "RELIEF_WALL", "WINDOW"):
                if category == 'RELIEF_WALL':
                    w_val = kwargs.get('relief_weathering', 0.50)
                    m_val = kwargs.get('relief_moss_amount', 0.30)
                elif category == 'WINDOW':
                    w_val = kwargs.get('window_weathering', 0.50)
                    m_val = kwargs.get('window_moss_amount', 0.25)
                else:
                    w_val = kwargs.get('arch_weathering', 0.50)
                    m_val = kwargs.get('arch_moss_amount', 0.30)

                apply_weathered_stone_arch_material(
                    obj, full_tex_path,
                    weathering=w_val,
                    moss_amount=m_val,
                    scale=1.0 if uv_mode == "FIT" else tex_tiling,
                    bump_strength=0.45,
                    slot_index=0
                )
            else:
                apply_image_texture_material(
                    obj, full_tex_path,
                    scale=1.0 if uv_mode == "FIT" else tex_tiling,
                    bump_strength=0.35,
                    displacement_strength=disp_strength if enable_disp else 0.0,
                    is_transparent=False
                )
        else:
            if (category == "FLOOR" and floor_shape == "COBBLESTONE") or (category == "WALL" and wall_shape == "COBBLE_WALL"):
                tile_sc = max(1.2, (1.0 / max(0.1, cobble_stone_size)) * 0.8)
                mat = create_procedural_cobblestone_shader(name + "_Cobble_Mat", seed=seed, tile_scale=tile_sc)
            elif category == "PILLAR":
                mat = create_procedural_pillar_shader(name + "_Pillar_Mat", mat_type=pillar_mat_type, seed=seed)
            elif category in ("BEAM_ARCH", "RELIEF_WALL", "WINDOW"):
                mat = create_procedural_pillar_shader(name + "_Stone_Mat", mat_type="SANDSTONE", seed=seed)
            else:
                mat = build_procedural_rock_material(name + "_Mat", seed)
            obj.data.materials.append(mat)

        # 🪟 WINDOW Multi-material assignments (Slot 1: Glass, Slot 2: Iron)
        if category == "WINDOW":
            mat_glass = create_window_glass_material(f"{name}_Glass_Mat")
            mat_iron = create_window_iron_material(f"{name}_Iron_Mat")
            while len(obj.data.materials) < 2:
                obj.data.materials.append(None)
            obj.data.materials[1] = mat_glass

            while len(obj.data.materials) < 3:
                obj.data.materials.append(None)
            obj.data.materials[2] = mat_iron

        if enable_disp and disp_strength > 0.001 and category in ("WALL", "FLOOR", "PILLAR", "BEAM", "TABLE", "PC_DESK", "CHEST", "GRASS"):
            apply_geometry_displacement(
                obj,
                disp_image_path=disp_img,
                strength=disp_strength,
                midlevel=disp_midlevel,
                subdivisions=disp_subdiv,
                apply_modifier=apply_disp
            )

    return obj
