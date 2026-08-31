import bpy
import bmesh
import math
import mathutils
import random
from .architecture_gen import build_antique_leg_or_column

def build_bookshelf_base(bm, size_x, size_y, size_z, tiers=3, column_style="ORNAMENTAL", seed=0):
    random.seed(seed)
    w = size_x
    d = size_y
    h = size_z
    board_th = 0.04
    col_rad = min(w, d) * 0.06
    
    # Back Plate
    res_back = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w - board_th * 2.0, board_th * 0.5, h), verts=res_back['verts'])
    bmesh.ops.translate(bm, vec=(0, -d * 0.5 + board_th * 0.25, 0), verts=res_back['verts'])
    
    # Side Panels
    res_lside = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(board_th, d, h), verts=res_lside['verts'])
    bmesh.ops.translate(bm, vec=(-w * 0.5 + board_th * 0.5, 0, 0), verts=res_lside['verts'])
    
    res_rside = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(board_th, d, h), verts=res_rside['verts'])
    bmesh.ops.translate(bm, vec=(w * 0.5 - board_th * 0.5, 0, 0), verts=res_rside['verts'])
    
    # Top & Bottom Crown Boards
    res_top = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w * 1.06, d * 1.06, board_th * 1.5), verts=res_top['verts'])
    bmesh.ops.translate(bm, vec=(0, 0, h * 0.5 - board_th * 0.75), verts=res_top['verts'])

    res_bot = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w * 1.04, d * 1.04, board_th * 1.5), verts=res_bot['verts'])
    bmesh.ops.translate(bm, vec=(0, 0, -h * 0.5 + board_th * 0.75), verts=res_bot['verts'])
    
    # Inner Shelves
    shelf_count = max(2, min(4, tiers))
    inner_h = h - board_th * 3.0
    step_z = inner_h / float(shelf_count)
    for s in range(1, shelf_count):
        cur_z = -h * 0.5 + board_th * 1.5 + (s * step_z)
        res_sh = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w - board_th * 2.2, d * 0.94, board_th), verts=res_sh['verts'])
        bmesh.ops.translate(bm, vec=(0, -d * 0.02, cur_z), verts=res_sh['verts'])

    # Columns
    for sign_x in [-1, 1]:
        bm_col = bmesh.new()
        build_antique_leg_or_column(bm_col, height=h * 0.96, radius=col_rad, style=column_style, seed=seed)
        for v in bm_col.verts:
            v.co.x += sign_x * (w * 0.5 - col_rad * 1.2)
            v.co.y += (d * 0.5 - col_rad * 0.8)
        for f in bm_col.faces:
            bm.faces.new([bm.verts.new(v.co) for v in f.verts])
        bm_col.free()
    
    return bm.verts[:]


def build_table_base(bm, size_x, size_y, size_z, shape="RECTANGLE", leg_style="ORNAMENTAL", seed=0):
    random.seed(seed)
    w = size_x
    d = size_y
    h = size_z
    top_th = 0.035 if shape in ("MODERN_DESK", "MONITOR_RISER_DESK", "L_SHAPED_CORNER") else 0.05
    leg_h = h - top_th
    
    if shape == "OVAL":
        res_top = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=32,
            radius1=1.0, radius2=1.0, depth=top_th
        )
        bmesh.ops.scale(bm, vec=(w * 0.5, d * 0.5, 1.0), verts=res_top['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, h * 0.5 - top_th * 0.5), verts=res_top['verts'])
    elif shape == "ROUNDED_RECT":
        res_top = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w, d, top_th), verts=res_top['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, h * 0.5 - top_th * 0.5), verts=res_top['verts'])
        bmesh.ops.bevel(bm, geom=res_top['verts'], offset=min(w, d) * 0.08, segments=3)
    elif shape == "L_SHAPED_CORNER":
        res_main = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w, d * 0.6, top_th), verts=res_main['verts'])
        bmesh.ops.translate(bm, vec=(0, -d * 0.2, h * 0.5 - top_th * 0.5), verts=res_main['verts'])
        res_side = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.45, d * 0.8, top_th), verts=res_side['verts'])
        bmesh.ops.translate(bm, vec=(w * 0.275, d * 0.2, h * 0.5 - top_th * 0.5), verts=res_side['verts'])
    elif shape == "MONITOR_RISER_DESK":
        res_top = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w, d, top_th), verts=res_top['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, h * 0.5 - top_th * 0.5), verts=res_top['verts'])
        shelf_w = w * 0.85
        shelf_d = d * 0.32
        shelf_h = 0.12
        res_riser = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(shelf_w, shelf_d, 0.02), verts=res_riser['verts'])
        bmesh.ops.translate(bm, vec=(0, -d * 0.3, h * 0.5 + shelf_h), verts=res_riser['verts'])
        for sx in [-shelf_w * 0.45, shelf_w * 0.45]:
            for sy in [-d * 0.3 - shelf_d * 0.4, -d * 0.3 + shelf_d * 0.4]:
                res_sleg = bmesh.ops.create_cone(
                    bm, cap_ends=True, cap_tris=False, segments=8,
                    radius1=0.012, radius2=0.012, depth=shelf_h
                )
                bmesh.ops.translate(bm, vec=(sx, sy, h * 0.5 + shelf_h * 0.5), verts=res_sleg['verts'])
    else: # RECTANGLE
        res_top = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w, d, top_th), verts=res_top['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, h * 0.5 - top_th * 0.5), verts=res_top['verts'])

    # Legs
    if leg_style == "STEEL_LOOP" or shape in ("MODERN_DESK", "MONITOR_RISER_DESK") and leg_style != "STEEL_PIPE" and leg_style not in ("ORNAMENTAL", "TWISTED", "REINFORCED"):
        pipe_w = 0.035
        for sx in [-w * 0.42, w * 0.42]:
            res_v1 = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(pipe_w, pipe_w, leg_h), verts=res_v1['verts'])
            bmesh.ops.translate(bm, vec=(sx, -d * 0.38, 0), verts=res_v1['verts'])

            res_v2 = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(pipe_w, pipe_w, leg_h), verts=res_v2['verts'])
            bmesh.ops.translate(bm, vec=(sx, d * 0.38, 0), verts=res_v2['verts'])

            res_b = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(pipe_w, d * 0.8, pipe_w), verts=res_b['verts'])
            bmesh.ops.translate(bm, vec=(sx, 0, -leg_h * 0.5 + pipe_w * 0.5), verts=res_b['verts'])

            res_t = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(pipe_w, d * 0.8, pipe_w), verts=res_t['verts'])
            bmesh.ops.translate(bm, vec=(sx, 0, leg_h * 0.5 - pipe_w * 0.5), verts=res_t['verts'])

        res_cross = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.84, pipe_w * 0.8, pipe_w * 0.8), verts=res_cross['verts'])
        bmesh.ops.translate(bm, vec=(0, -d * 0.38, -leg_h * 0.2), verts=res_cross['verts'])

    elif leg_style == "STEEL_PIPE":
        pipe_rad = 0.02
        for (lx, ly) in [(-w * 0.42, -d * 0.4), (w * 0.42, -d * 0.4), (-w * 0.42, d * 0.4), (w * 0.42, d * 0.4)]:
            res_pipe = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=16,
                radius1=pipe_rad, radius2=pipe_rad, depth=leg_h
            )
            bmesh.ops.translate(bm, vec=(lx, ly, 0), verts=res_pipe['verts'])
        res_uf = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.84, d * 0.8, 0.03), verts=res_uf['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, leg_h * 0.5 - 0.015), verts=res_uf['verts'])

    else:
        apron_h = 0.08
        res_apron_f = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.82, 0.025, apron_h), verts=res_apron_f['verts'])
        bmesh.ops.translate(bm, vec=(0, d * 0.36, h * 0.5 - top_th - apron_h * 0.5), verts=res_apron_f['verts'])
        
        res_apron_b = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.82, 0.025, apron_h), verts=res_apron_b['verts'])
        bmesh.ops.translate(bm, vec=(0, -d * 0.36, h * 0.5 - top_th - apron_h * 0.5), verts=res_apron_b['verts'])

        leg_rad = max(0.03, min(w, d) * 0.055)
        offset_x = (w * 0.5) * 0.78 * (0.82 if shape == "OVAL" else 1.0)
        offset_y = (d * 0.5) * 0.76 * (0.82 if shape == "OVAL" else 1.0)

        for (lx, ly) in [(-offset_x, -offset_y), (offset_x, -offset_y), (-offset_x, offset_y), (offset_x, offset_y)]:
            bm_leg = bmesh.new()
            build_antique_leg_or_column(bm_leg, height=leg_h, radius=leg_rad, style=leg_style, seed=seed)
            for v in bm_leg.verts:
                v.co.x += lx
                v.co.y += ly
                v.co.z += (-top_th * 0.5)
            for f in bm_leg.faces:
                bm.faces.new([bm.verts.new(v.co) for v in f.verts])
            bm_leg.free()

    return bm.verts[:]


def build_chair_base(
    bm, size_x, size_y, size_z,
    chair_type="DINING_CHAIR",
    leg_style="ORNAMENTAL",
    seat_style="CUSHION",
    back_style="SOLID",
    leg_layout="FOUR_LEGS",
    seed=0
):
    random.seed(seed)
    w = size_x
    d = size_y
    h = size_z
    seat_h = h * 0.46
    seat_th = 0.06
    leg_h = seat_h - seat_th
    
    if chair_type == "OFFICE_TASK_CHAIR":
        res_seat = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w, d, seat_th), verts=res_seat['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, seat_h - seat_th * 0.5), verts=res_seat['verts'])
        for v in res_seat['verts']:
            if v.co.z > (seat_h - seat_th * 0.5):
                nx = max(0.0, 1.0 - abs(v.co.x / (w * 0.5)))
                ny = max(0.0, 1.0 - abs(v.co.y / (d * 0.5)))
                v.co.z += (nx * ny + 0.4) * 0.02
        bmesh.ops.bevel(bm, geom=res_seat['verts'], offset=0.02, segments=2)

        back_h = h - seat_h
        res_back = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.88, 0.035, back_h * 0.85), verts=res_back['verts'])
        bmesh.ops.translate(bm, vec=(0, -d * 0.44, seat_h + back_h * 0.45), verts=res_back['verts'])
        for v in res_back['verts']:
            curve = math.sin((v.co.z - seat_h) / back_h * math.pi) * 0.03
            v.co.y += curve
        bmesh.ops.bevel(bm, geom=res_back['verts'], offset=0.015, segments=2)

        res_spine = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(0.06, 0.04, back_h * 0.7), verts=res_spine['verts'])
        bmesh.ops.translate(bm, vec=(0, -d * 0.48, seat_h + back_h * 0.35), verts=res_spine['verts'])

        arm_h = back_h * 0.45
        for sx in [-w * 0.48, w * 0.48]:
            res_apost = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=12,
                radius1=0.018, radius2=0.018, depth=arm_h
            )
            bmesh.ops.translate(bm, vec=(sx, 0, seat_h + arm_h * 0.5), verts=res_apost['verts'])
            res_apad = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(0.06, d * 0.55, 0.025), verts=res_apad['verts'])
            bmesh.ops.translate(bm, vec=(sx, 0, seat_h + arm_h + 0.012), verts=res_apad['verts'])
            bmesh.ops.bevel(bm, geom=res_apad['verts'], offset=0.008, segments=2)

        res_cyl = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=0.03, radius2=0.025, depth=leg_h * 0.8
        )
        bmesh.ops.translate(bm, vec=(0, 0, leg_h * 0.45), verts=res_cyl['verts'])

        base_r = min(w, d) * 0.65
        for i in range(5):
            ang = math.radians(i * 72.0)
            res_leg_bar = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(0.035, base_r, 0.025), verts=res_leg_bar['verts'])
            bmesh.ops.translate(bm, vec=(0, base_r * 0.5, 0.04), verts=res_leg_bar['verts'])
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(ang, 3, 'Z'), verts=res_leg_bar['verts'])
            
            res_caster = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=12,
                radius1=0.025, radius2=0.025, depth=0.02
            )
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(90), 3, 'Y'), verts=res_caster['verts'])
            bmesh.ops.translate(bm, vec=(math.sin(ang) * base_r, math.cos(ang) * base_r, 0.025), verts=res_caster['verts'])

        return bm.verts[:]

    elif chair_type == "MODERN_SHELL_CHAIR":
        res_seat = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w, d * 0.95, 0.025), verts=res_seat['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, seat_h), verts=res_seat['verts'])
        
        back_h = h - seat_h
        res_back = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.88, 0.025, back_h * 0.85), verts=res_back['verts'])
        bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(-10), 3, 'X'), verts=res_back['verts'])
        bmesh.ops.translate(bm, vec=(0, -d * 0.4, seat_h + back_h * 0.45), verts=res_back['verts'])

        leg_rad = 0.016
        for (lx, ly, rot_x, rot_y) in [
            (-w * 0.32, -d * 0.32, 10, -10),
            (w * 0.32, -d * 0.32, 10, 10),
            (-w * 0.32, d * 0.32, -10, -10),
            (w * 0.32, d * 0.32, -10, 10)
        ]:
            res_sleg = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=12,
                radius1=leg_rad * 1.2, radius2=leg_rad * 0.7, depth=leg_h
            )
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(rot_x), 3, 'X'), verts=res_sleg['verts'])
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(rot_y), 3, 'Y'), verts=res_sleg['verts'])
            bmesh.ops.translate(bm, vec=(lx, ly, leg_h * 0.5), verts=res_sleg['verts'])

        res_wire = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.6, d * 0.6, 0.01), verts=res_wire['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, leg_h * 0.8), verts=res_wire['verts'])

        return bm.verts[:]

    # Classic chairs
    if chair_type == "ROUND_STOOL":
        rad = w * 0.46
        res_uf = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=rad * 0.92, radius2=rad * 0.92, depth=0.03
        )
        bmesh.ops.translate(bm, vec=(0, 0, seat_h - seat_th + 0.015), verts=res_uf['verts'])

        if seat_style == "CUSHION":
            res_cushion = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=24,
                radius1=rad, radius2=rad * 0.94, depth=seat_th
            )
            for v in res_cushion['verts']:
                if v.co.z > 0:
                    r_dist = math.sqrt(v.co.x**2 + v.co.y**2) / rad
                    v.co.z += (1.0 - r_dist) * 0.025
            bmesh.ops.translate(bm, vec=(0, 0, seat_h - seat_th * 0.5), verts=res_cushion['verts'])
        else:
            res_seat = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=24,
                radius1=rad, radius2=rad, depth=seat_th
            )
            bmesh.ops.translate(bm, vec=(0, 0, seat_h - seat_th * 0.5), verts=res_seat['verts'])

    else:
        res_uf = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.88, d * 0.88, 0.04), verts=res_uf['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, seat_h - seat_th + 0.02), verts=res_uf['verts'])

        res_seat = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w, d, seat_th), verts=res_seat['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, seat_h - seat_th * 0.5), verts=res_seat['verts'])
        if seat_style == "CUSHION":
            for v in res_seat['verts']:
                if v.co.z > (seat_h - seat_th * 0.5):
                    nx = max(0.0, 1.0 - abs(v.co.x / (w * 0.5)))
                    ny = max(0.0, 1.0 - abs(v.co.y / (d * 0.5)))
                    v.co.z += (nx * ny + 0.5) * 0.02
        bmesh.ops.bevel(bm, geom=res_seat['verts'], offset=0.015, segments=2)

    # Legs
    if leg_layout == "PEDESTAL_ONE":
        col_rad = min(w, d) * 0.12
        bm_col = bmesh.new()
        build_antique_leg_or_column(bm_col, height=leg_h * 0.95, radius=col_rad, style=leg_style, seed=seed)
        for v in bm_col.verts:
            v.co.z += (leg_h * 0.5)
        for f in bm_col.faces:
            bm.faces.new([bm.verts.new(v.co) for v in f.verts])
        bm_col.free()

        foot_len = min(w, d) * 0.42
        for ang in [45, 135, 225, 315]:
            rad_ang = math.radians(ang)
            res_foot = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=8,
                radius1=0.035, radius2=0.02, depth=foot_len
            )
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(75), 3, 'X'), verts=res_foot['verts'])
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(rad_ang, 3, 'Z'), verts=res_foot['verts'])
            bmesh.ops.translate(bm, vec=(math.cos(rad_ang) * (foot_len * 0.45), math.sin(rad_ang) * (foot_len * 0.45), 0.04), verts=res_foot['verts'])

    elif leg_layout == "X_CROSS":
        x_th = min(w, d) * 0.06
        for sx in [-w * 0.36, w * 0.36]:
            res_b1 = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(x_th, 0.04, leg_h * 1.1), verts=res_b1['verts'])
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(28), 3, 'X'), verts=res_b1['verts'])
            bmesh.ops.translate(bm, vec=(sx, 0, leg_h * 0.5), verts=res_b1['verts'])

            res_b2 = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(x_th, 0.04, leg_h * 1.1), verts=res_b2['verts'])
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(-28), 3, 'X'), verts=res_b2['verts'])
            bmesh.ops.translate(bm, vec=(sx, 0, leg_h * 0.5), verts=res_b2['verts'])

        res_str = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=0.02, radius2=0.02, depth=w * 0.72)
        bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(90), 3, 'Y'), verts=res_str['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, leg_h * 0.5), verts=res_str['verts'])

    elif leg_layout == "TRIPOD_THREE":
        leg_rad = min(w, d) * 0.055
        dist_r = min(w, d) * 0.32
        for ang in [90, 210, 330]:
            rad_ang = math.radians(ang)
            lx = math.cos(rad_ang) * dist_r
            ly = math.sin(rad_ang) * dist_r
            bm_leg = bmesh.new()
            build_antique_leg_or_column(bm_leg, height=leg_h, radius=leg_rad, style=leg_style, seed=seed)
            for v in bm_leg.verts:
                v.co.x += lx
                v.co.y += ly
                v.co.z += (leg_h * 0.5)
            for f in bm_leg.faces:
                bm.faces.new([bm.verts.new(v.co) for v in f.verts])
            bm_leg.free()

    else:
        leg_rad = min(w, d) * 0.055
        if chair_type == "ROUND_STOOL":
            offset_x = (w * 0.5) * 0.58
            offset_y = (d * 0.5) * 0.58
        else:
            offset_x = (w * 0.5) * 0.72
            offset_y = (d * 0.5) * 0.72

        for (lx, ly) in [(-offset_x, -offset_y), (offset_x, -offset_y), (-offset_x, offset_y), (offset_x, offset_y)]:
            bm_leg = bmesh.new()
            build_antique_leg_or_column(bm_leg, height=leg_h, radius=leg_rad, style=leg_style, seed=seed)
            for v in bm_leg.verts:
                v.co.x += lx
                v.co.y += ly
                v.co.z += (leg_h * 0.5)
            for f in bm_leg.faces:
                bm.faces.new([bm.verts.new(v.co) for v in f.verts])
            bm_leg.free()

    # Backrest & Armrest
    if chair_type in ("DINING_CHAIR", "ARMCHAIR"):
        back_h = h - seat_h
        post_rad = min(w, d) * 0.045
        
        for sx in [-w * 0.42, w * 0.42]:
            bm_post = bmesh.new()
            build_antique_leg_or_column(bm_post, height=back_h, radius=post_rad, style=leg_style, seed=seed)
            for v in bm_post.verts:
                v.co.x += sx
                v.co.y += (-d * 0.42)
                v.co.z += (seat_h + back_h * 0.5)
            for f in bm_post.faces:
                bm.faces.new([bm.verts.new(v.co) for v in f.verts])
            bm_post.free()

        res_top_rail = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.94, 0.045, 0.08), verts=res_top_rail['verts'])
        bmesh.ops.translate(bm, vec=(0, -d * 0.42, h - 0.04), verts=res_top_rail['verts'])
        bmesh.ops.bevel(bm, geom=res_top_rail['verts'], offset=0.015, segments=2)

        if back_style == "SOLID":
            res_panel = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(w * 0.76, 0.025, back_h * 0.78), verts=res_panel['verts'])
            bmesh.ops.translate(bm, vec=(0, -d * 0.42, seat_h + back_h * 0.45), verts=res_panel['verts'])
            bmesh.ops.bevel(bm, geom=res_panel['verts'], offset=0.01, segments=2)

        elif back_style == "OVAL":
            res_oval = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=24,
                radius1=1.0, radius2=1.0, depth=0.025
            )
            bmesh.ops.scale(bm, vec=(w * 0.36, back_h * 0.38, 1.0), verts=res_oval['verts'])
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(90), 3, 'X'), verts=res_oval['verts'])
            bmesh.ops.translate(bm, vec=(0, -d * 0.42, seat_h + back_h * 0.48), verts=res_oval['verts'])

        else:
            num_spindles = 4
            step = (w * 0.68) / (num_spindles - 1)
            for i in range(num_spindles):
                sp_x = -w * 0.34 + i * step
                res_sp = bmesh.ops.create_cone(
                    bm, cap_ends=True, cap_tris=False, segments=8,
                    radius1=0.014, radius2=0.014, depth=back_h * 0.88
                )
                bmesh.ops.translate(bm, vec=(sp_x, -d * 0.42, seat_h + back_h * 0.46), verts=res_sp['verts'])

        if chair_type == "ARMCHAIR":
            arm_h = back_h * 0.42
            arm_len = d * 0.82
            arm_z = seat_h + arm_h
            
            for sx in [-w * 0.45, w * 0.45]:
                res_arm_post = bmesh.ops.create_cone(
                    bm, cap_ends=True, cap_tris=False, segments=12,
                    radius1=0.02, radius2=0.018, depth=arm_h
                )
                bmesh.ops.translate(bm, vec=(sx, d * 0.28, seat_h + arm_h * 0.5), verts=res_arm_post['verts'])

                res_arm_pad = bmesh.ops.create_cube(bm, size=1.0)
                bmesh.ops.scale(bm, vec=(0.055, arm_len, 0.03), verts=res_arm_pad['verts'])
                bmesh.ops.translate(bm, vec=(sx, -d * 0.06, arm_z), verts=res_arm_pad['verts'])
                bmesh.ops.bevel(bm, geom=res_arm_pad['verts'], offset=0.01, segments=2)

    return bm.verts[:]


def build_chest_base(bm, size_x, size_y, size_z, tiers=3, handle_style="RING", seed=0):
    random.seed(seed)
    w = size_x
    d = size_y
    h = size_z
    leg_h = h * 0.14
    body_h = h - leg_h
    body_z_center = -h * 0.5 + leg_h + body_h * 0.5
    
    res_body = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w * 0.94, d * 0.94, body_h), verts=res_body['verts'])
    bmesh.ops.translate(bm, vec=(0, 0, body_z_center), verts=res_body['verts'])
    
    res_top = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w * 1.04, d * 1.04, 0.05), verts=res_top['verts'])
    bmesh.ops.translate(bm, vec=(0, 0, h * 0.5 - 0.025), verts=res_top['verts'])

    foot_rad = min(w, d) * 0.07
    offset_x = (w * 0.5) * 0.8
    offset_y = (d * 0.5) * 0.8
    for (lx, ly) in [(-offset_x, -offset_y), (offset_x, -offset_y), (-offset_x, offset_y), (offset_x, offset_y)]:
        res_foot = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=foot_rad)
        bmesh.ops.scale(bm, vec=(1.1, 1.1, (leg_h / (foot_rad * 2.0))), verts=res_foot['verts'])
        bmesh.ops.translate(bm, vec=(lx, ly, -h * 0.5 + leg_h * 0.5), verts=res_foot['verts'])

    drawer_count = max(2, min(5, tiers))
    drawer_h = (body_h * 0.88) / float(drawer_count)
    front_y = d * 0.5 * 0.94
    
    for i in range(drawer_count):
        cur_z = (-h * 0.5 + leg_h + (body_h * 0.06)) + (i + 0.5) * drawer_h
        
        res_dp = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.86, 0.025, drawer_h * 0.88), verts=res_dp['verts'])
        bmesh.ops.translate(bm, vec=(0, front_y + 0.012, cur_z), verts=res_dp['verts'])
        
        res_frame = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.8, 0.015, drawer_h * 0.72), verts=res_frame['verts'])
        bmesh.ops.translate(bm, vec=(0, front_y + 0.025, cur_z), verts=res_frame['verts'])

        for hx in [-w * 0.24, w * 0.24]:
            if handle_style == "KNOB":
                res_knob = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.018)
                bmesh.ops.translate(bm, vec=(hx, front_y + 0.045, cur_z), verts=res_knob['verts'])
            elif handle_style == "BAR":
                res_bar = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=0.008, radius2=0.008, depth=0.09)
                bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(90), 3, 'Y'), verts=res_bar['verts'])
                bmesh.ops.translate(bm, vec=(hx, front_y + 0.04, cur_z), verts=res_bar['verts'])
            else:
                res_ring = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12, radius1=0.022, radius2=0.022, depth=0.008)
                bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(90), 3, 'X'), verts=res_ring['verts'])
                bmesh.ops.translate(bm, vec=(hx, front_y + 0.04, cur_z - 0.01), verts=res_ring['verts'])

    return bm.verts[:]


def build_bed_base(bm, size_x, size_y, size_z, bed_size="SINGLE", leg_style="ORNAMENTAL", seed=0):
    random.seed(seed)
    if bed_size == "KING":
        w = 2.0
    elif bed_size == "DOUBLE":
        w = 1.6
    else:
        w = 1.2
        
    d = max(size_y, 2.0)
    h = size_z
    frame_h = 0.35
    head_h = h
    foot_h = h * 0.65
    post_rad = 0.065
    
    offset_x = w * 0.5
    offset_y = d * 0.5
    
    for sx in [-offset_x, offset_x]:
        bm_hp = bmesh.new()
        build_antique_leg_or_column(bm_hp, height=head_h, radius=post_rad, style=leg_style, seed=seed)
        for v in bm_hp.verts:
            v.co.x += sx
            v.co.y += -offset_y
            v.co.z += (head_h * 0.5)
        for f in bm_hp.faces:
            bm.faces.new([bm.verts.new(v.co) for v in f.verts])
        bm_hp.free()

    for sx in [-offset_x, offset_x]:
        bm_fp = bmesh.new()
        build_antique_leg_or_column(bm_fp, height=foot_h, radius=post_rad, style=leg_style, seed=seed)
        for v in bm_fp.verts:
            v.co.x += sx
            v.co.y += offset_y
            v.co.z += (foot_h * 0.5)
        for f in bm_fp.faces:
            bm.faces.new([bm.verts.new(v.co) for v in f.verts])
        bm_fp.free()

    res_hb = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w - post_rad * 1.5, 0.04, head_h * 0.65), verts=res_hb['verts'])
    bmesh.ops.translate(bm, vec=(0, -offset_y, frame_h + (head_h * 0.65) * 0.5), verts=res_hb['verts'])

    res_fb = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w - post_rad * 1.5, 0.04, foot_h * 0.5), verts=res_fb['verts'])
    bmesh.ops.translate(bm, vec=(0, offset_y, frame_h + (foot_h * 0.5) * 0.5), verts=res_fb['verts'])

    res_lrail = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.04, d, 0.12), verts=res_lrail['verts'])
    bmesh.ops.translate(bm, vec=(-offset_x + post_rad * 0.5, 0, frame_h), verts=res_lrail['verts'])
    
    res_rrail = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.04, d, 0.12), verts=res_rrail['verts'])
    bmesh.ops.translate(bm, vec=(offset_x - post_rad * 0.5, 0, frame_h), verts=res_rrail['verts'])

    mat_th = 0.24
    res_mat = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w * 0.88, d * 0.9, mat_th), verts=res_mat['verts'])
    bmesh.ops.translate(bm, vec=(0, 0, frame_h + mat_th * 0.5 + 0.02), verts=res_mat['verts'])
    bmesh.ops.bevel(bm, geom=res_mat['verts'], offset=0.04, segments=2)

    return bm.verts[:]
