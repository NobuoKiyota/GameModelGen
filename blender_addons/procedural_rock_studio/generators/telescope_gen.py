import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix


def _rng(seed):
    r = random.Random(seed)
    return r


def create_mesh_object(context, name):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)
    return obj, mesh


def build_telescope_tripod_mesh(context, name="Telescope_Tripod",
                                height=1.0, leg_spread=0.45,
                                style="MODERN_REFRACTOR", seed=0):
    r = _rng(seed + 1)
    obj, mesh = create_mesh_object(context, name)
    bm = bmesh.new()

    if style == "ANTIQUE_BRASS":
        col_h = height * r.uniform(0.38, 0.52)
        col_r_top  = r.uniform(0.018, 0.025)
        col_r_base = r.uniform(0.032, 0.042)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=col_r_base, radius2=col_r_top, depth=col_h,
            matrix=Matrix.Translation((0, 0, height - col_h * 0.5)))
        ring_count = r.randint(2, 4)
        for ri in range(ring_count):
            rz = height - col_h * (0.2 + ri * 0.2)
            rw = r.uniform(0.012, 0.022)
            bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
                radius1=col_r_base + rw, radius2=col_r_base + rw, depth=0.014,
                matrix=Matrix.Translation((0, 0, rz)))
        base_z  = height - col_h
        spread  = r.uniform(0.38, 0.62)
        seg_count = r.randint(5, 8)
        for i in range(3):
            az = i * (2.0 * math.pi / 3.0)
            for s in range(seg_count):
                t1 = s / seg_count
                t2 = (s + 1) / seg_count
                r1 = math.sin(t1 * math.pi * 0.5) * spread
                z1 = base_z - t1 * base_z
                r2 = math.sin(t2 * math.pi * 0.5) * spread
                z2 = base_z - t2 * base_z
                mid_r = (r1 + r2) * 0.5
                mid_z = (z1 + z2) * 0.5
                seg_len = math.sqrt((r2 - r1) ** 2 + (z2 - z1) ** 2)
                ang_p = math.atan2(r2 - r1, z1 - z2)
                thick = r.uniform(0.009, 0.016)
                p = Matrix.Rotation(az, 4, "Z") @ Matrix.Translation((mid_r, 0, mid_z)) @ Matrix.Rotation(ang_p, 4, "Y")
                bmesh.ops.create_cube(bm, size=1.0,
                    matrix=p @ Matrix.Diagonal((thick, thick * 1.5, seg_len * 1.05, 1.0)))

    elif style == "CASSEGRAIN_POP":
        hub_r = r.uniform(0.038, 0.055)
        hub_h = r.uniform(0.03, 0.05)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=hub_r, radius2=hub_r * 0.85, depth=hub_h,
            matrix=Matrix.Translation((0, 0, height)))
        spread_ratio = r.uniform(0.55, 0.85)
        leg_len = math.sqrt(height * height + (leg_spread * spread_ratio) ** 2) * r.uniform(0.65, 0.85)
        tilt_angle = math.atan2(leg_spread * spread_ratio, height)
        leg_r = r.uniform(0.006, 0.011)
        for i in range(3):
            az = i * (2.0 * math.pi / 3.0)
            lp = Matrix.Translation((0,0,height)) @ Matrix.Rotation(az,4,"Z") @ Matrix.Rotation(tilt_angle,4,"Y") @ Matrix.Translation((0,0,-leg_len*0.5))
            bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=10,
                radius1=leg_r, radius2=leg_r, depth=leg_len, matrix=lp)
            tp = Matrix.Translation((0,0,height)) @ Matrix.Rotation(az,4,"Z") @ Matrix.Rotation(tilt_angle,4,"Y") @ Matrix.Translation((0,0,-leg_len))
            bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=10,
                radius1=leg_r*1.8, radius2=leg_r, depth=0.018, matrix=tp)

    elif style == "SMART_DIGITAL":
        hub_segs = r.randint(12, 20)
        hub_r = r.uniform(0.055, 0.085)
        hub_h = r.uniform(0.045, 0.075)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=hub_segs,
            radius1=hub_r, radius2=hub_r * 0.85, depth=hub_h,
            matrix=Matrix.Translation((0, 0, height)))
        # 補強リング（有無ランダム）
        if r.random() > 0.45:
            ring_r = hub_r * r.uniform(1.1, 1.2)
            bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=hub_segs,
                radius1=ring_r, radius2=ring_r, depth=0.012,
                matrix=Matrix.Translation((0, 0, height - hub_h * 0.3)))
        upper_ratio = r.uniform(0.50, 0.65)
        leg_len = math.sqrt(height*height + leg_spread*leg_spread) * r.uniform(0.9, 1.1)
        tilt_angle = math.atan2(leg_spread, height)
        upper_r = r.uniform(0.018, 0.026)
        lower_r = upper_r * r.uniform(0.55, 0.75)
        leg_segs = r.randint(10, 18)
        for i in range(3):
            az = i * (2.0 * math.pi / 3.0)
            ul = leg_len * upper_ratio
            up = Matrix.Translation((0,0,height)) @ Matrix.Rotation(az,4,"Z") @ Matrix.Rotation(tilt_angle,4,"Y") @ Matrix.Translation((0,0,-ul*0.5))
            bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=leg_segs,
                radius1=upper_r, radius2=upper_r, depth=ul, matrix=up)
            lock_r = upper_r * r.uniform(1.15, 1.35)
            lp = Matrix.Translation((0,0,height)) @ Matrix.Rotation(az,4,"Z") @ Matrix.Rotation(tilt_angle,4,"Y") @ Matrix.Translation((0,0,-ul))
            bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=leg_segs,
                radius1=lock_r, radius2=lock_r, depth=0.03, matrix=lp)
            ll = leg_len * (1 - upper_ratio)
            lp2 = Matrix.Translation((0,0,height)) @ Matrix.Rotation(az,4,"Z") @ Matrix.Rotation(tilt_angle,4,"Y") @ Matrix.Translation((0,0,-ul-ll*0.5))
            bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=leg_segs,
                radius1=lower_r, radius2=lower_r, depth=ll, matrix=lp2)
        # センターブレース（有無ランダム）
        if r.random() > 0.5:
            br = r.uniform(0.006, 0.010)
            for i in range(3):
                az = i * (2.0 * math.pi / 3.0)
                brace_pos = Matrix.Translation((0,0,height)) @ Matrix.Rotation(az,4,"Z") @ Matrix.Rotation(tilt_angle * 0.4,4,"Y") @ Matrix.Translation((0,0,-leg_len*0.55))
                bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8,
                    radius1=br, radius2=br, depth=leg_len*0.25, matrix=brace_pos)


    elif style == "TACTICAL_COMPACT":
        hub_segs = r.randint(12, 20)
        hub_r = r.uniform(0.065, 0.092)
        hub_h = r.uniform(0.055, 0.082)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=hub_segs,
            radius1=hub_r, radius2=hub_r*0.9, depth=hub_h,
            matrix=Matrix.Translation((0, 0, height)))
        elev_len = height * r.uniform(0.4, 0.6)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=hub_segs,
            radius1=0.018, radius2=0.018, depth=elev_len,
            matrix=Matrix.Translation((0, 0, height - elev_len * 0.4)))
        crank_len = r.uniform(0.032, 0.055)
        bmesh.ops.create_cube(bm, size=1.0,
            matrix=Matrix.Translation((hub_r + 0.02, 0, height - 0.02)) @ Matrix.Diagonal((crank_len, 0.015, 0.015, 1.0)))
        leg_len = math.sqrt(height*height + leg_spread*leg_spread) * r.uniform(0.9, 1.1)
        tilt_angle = math.atan2(leg_spread, height)
        n_tiers = r.randint(2, 4)  # 2〜4段で変化
        base_r = r.uniform(0.016, 0.024)
        leg_segs = r.randint(8, 14)
        for i in range(3):
            az = i * (2.0 * math.pi / 3.0)
            for tier in range(n_tiers):
                t_len = leg_len / n_tiers
                t_r = max(0.006, base_r - tier * 0.003)
                oz = -t_len * (tier + 0.5)
                pp = Matrix.Translation((0,0,height)) @ Matrix.Rotation(az,4,"Z") @ Matrix.Rotation(tilt_angle,4,"Y") @ Matrix.Translation((0,0,oz))
                bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=leg_segs,
                    radius1=t_r, radius2=t_r, depth=t_len, matrix=pp)
                if tier < n_tiers - 1:
                    lp = Matrix.Translation((0,0,height)) @ Matrix.Rotation(az,4,"Z") @ Matrix.Rotation(tilt_angle,4,"Y") @ Matrix.Translation((0,0,-t_len*(tier+1)))
                    bmesh.ops.create_cube(bm, size=1.0,
                        matrix=lp @ Matrix.Diagonal((0.042, 0.032, 0.028, 1.0)))
            # ゴムフットパッド（確率的）
            if r.random() > 0.4:
                foot_pos = Matrix.Translation((0,0,height)) @ Matrix.Rotation(az,4,"Z") @ Matrix.Rotation(tilt_angle,4,"Y") @ Matrix.Translation((0,0,-leg_len))
                bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8,
                    radius1=base_r * 2.0, radius2=base_r * 1.2, depth=0.016, matrix=foot_pos)


    else:
        hub_r = r.uniform(0.065, 0.095)
        hub_h = r.uniform(0.048, 0.072)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12,
            radius1=hub_r, radius2=hub_r*0.9, depth=hub_h,
            matrix=Matrix.Translation((0, 0, height)))
        post_len = height * r.uniform(0.38, 0.52)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12,
            radius1=0.014, radius2=0.014, depth=post_len,
            matrix=Matrix.Translation((0, 0, height - post_len * 0.5)))
        leg_len = math.sqrt(height*height + leg_spread*leg_spread) * r.uniform(0.9, 1.05)
        tilt_angle = math.atan2(leg_spread, height)
        upper_r = r.uniform(0.015, 0.022)
        lower_r = upper_r * r.uniform(0.55, 0.75)
        upper_ratio = r.uniform(0.48, 0.62)
        for i in range(3):
            az = i * (2.0 * math.pi / 3.0)
            ul = leg_len * upper_ratio
            up = Matrix.Translation((0,0,height)) @ Matrix.Rotation(az,4,"Z") @ Matrix.Rotation(tilt_angle,4,"Y") @ Matrix.Translation((0,0,-ul*0.5))
            bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12,
                radius1=upper_r, radius2=upper_r, depth=ul, matrix=up)
            lkp = Matrix.Translation((0,0,height)) @ Matrix.Rotation(az,4,"Z") @ Matrix.Rotation(tilt_angle,4,"Y") @ Matrix.Translation((0,0,-ul))
            bmesh.ops.create_cube(bm, size=1.0,
                matrix=lkp @ Matrix.Diagonal((0.042, 0.032, 0.038, 1.0)))
            ll = leg_len * (1 - upper_ratio)
            lp2 = Matrix.Translation((0,0,height)) @ Matrix.Rotation(az,4,"Z") @ Matrix.Rotation(tilt_angle,4,"Y") @ Matrix.Translation((0,0,-ul-ll*0.5))
            bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12,
                radius1=lower_r, radius2=lower_r, depth=ll, matrix=lp2)
        tray_z = height * r.uniform(0.5, 0.65)
        tray_r = leg_spread * r.uniform(0.35, 0.48)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=tray_r, radius2=tray_r, depth=0.010,
            matrix=Matrix.Translation((0, 0, tray_z)))

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(mesh)
    bm.free()
    return obj


def build_telescope_mount_mesh(context, name="Telescope_Mount",
                               base_z=1.0, style="MODERN_REFRACTOR", seed=0):
    r = _rng(seed + 2)
    obj, mesh = create_mesh_object(context, name)
    bm = bmesh.new()

    if style == "ANTIQUE_BRASS":
        pivot_r = r.uniform(0.028, 0.040)
        pivot_h = r.uniform(0.04, 0.065)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=pivot_r, radius2=pivot_r, depth=pivot_h,
            matrix=Matrix.Translation((0, 0, pivot_h * 0.5)))
        quad_r = r.uniform(0.055, 0.08)
        quad_h = r.uniform(0.008, 0.016)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12,
            radius1=quad_r, radius2=quad_r, depth=quad_h,
            matrix=Matrix.Translation((0, 0, pivot_h + 0.04)) @ Matrix.Rotation(math.pi * 0.5, 4, "Y"))
        for side in (-1, 1):
            kp = Matrix.Translation((side * (quad_r * 0.55), 0, pivot_h + 0.04)) @ Matrix.Rotation(math.pi * 0.5, 4, "Y")
            knob_r = r.uniform(0.012, 0.018)
            bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12,
                radius1=knob_r, radius2=knob_r, depth=0.025, matrix=kp)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12,
            radius1=0.006, radius2=0.006, depth=quad_r * 0.9,
            matrix=Matrix.Translation((0, 0, pivot_h + 0.04)) @ Matrix.Rotation(math.pi * 0.5, 4, "Y"))

    elif style == "SMART_DIGITAL":
        base_r = r.uniform(0.060, 0.080)
        base_h = r.uniform(0.022, 0.038)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=base_r, radius2=base_r*0.9, depth=base_h,
            matrix=Matrix.Translation((0, 0, base_h * 0.5)))
        fork_h = r.uniform(0.18, 0.28)
        fork_w = r.uniform(0.038, 0.055)
        fork_d = r.uniform(0.065, 0.092)
        offset_x = r.uniform(0.04, 0.06)
        bmesh.ops.create_cube(bm, size=1.0,
            matrix=Matrix.Translation((offset_x, 0, base_h + fork_h * 0.5)) @ Matrix.Diagonal((fork_w, fork_d, fork_h, 1.0)))
        btn_r = r.uniform(0.010, 0.016)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=btn_r, radius2=btn_r, depth=0.007,
            matrix=Matrix.Translation((offset_x, -(fork_d * 0.5 + 0.004), base_h + fork_h * r.uniform(0.30, 0.45))) @ Matrix.Rotation(math.pi * 0.5, 4, "X"))
        gear_sz = r.uniform(0.025, 0.040)
        bmesh.ops.create_cube(bm, size=1.0,
            matrix=Matrix.Translation((offset_x, fork_d * 0.5 + gear_sz * 0.5, base_h + fork_h * 0.72)) @ Matrix.Diagonal((gear_sz * 1.5, gear_sz, gear_sz * 1.2, 1.0)))

    elif style == "CASSEGRAIN_POP":
        base_r = r.uniform(0.030, 0.042)
        base_h = r.uniform(0.022, 0.036)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=base_r, radius2=base_r * 0.9, depth=base_h,
            matrix=Matrix.Translation((0, 0, base_h * 0.5)))
        ball_r = r.uniform(0.018, 0.028)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=ball_r,
            matrix=Matrix.Translation((0, 0, base_h + ball_r)))
        lev_ang = r.uniform(0, math.pi * 2)
        lev_len = r.uniform(0.025, 0.045)
        lp = Matrix.Rotation(lev_ang, 4, "Z") @ Matrix.Translation((base_r + lev_len * 0.5, 0, base_h * 0.55))
        bmesh.ops.create_cube(bm, size=1.0,
            matrix=lp @ Matrix.Diagonal((lev_len, 0.010, 0.010, 1.0)))
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12,
            radius1=0.008, radius2=0.008, depth=0.018,
            matrix=Matrix.Translation((0, base_r * 0.9, base_h + ball_r * 0.5)) @ Matrix.Rotation(math.pi * 0.5, 4, "X"))

    elif style == "TACTICAL_COMPACT":
        base_r = r.uniform(0.038, 0.050)
        base_h = r.uniform(0.028, 0.042)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=base_r, radius2=base_r*0.92, depth=base_h,
            matrix=Matrix.Translation((0, 0, base_h * 0.5)))
        plate_sz = r.uniform(0.048, 0.068)
        plate_h = r.uniform(0.012, 0.020)
        bmesh.ops.create_cube(bm, size=1.0,
            matrix=Matrix.Translation((0, 0, base_h + plate_h * 0.5)) @ Matrix.Diagonal((plate_sz, plate_sz, plate_h, 1.0)))
        handle_len = r.uniform(0.14, 0.22)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12,
            radius1=0.007, radius2=0.007, depth=handle_len,
            matrix=Matrix.Translation((0, -(base_r + handle_len * 0.5), base_h * 0.55)) @ Matrix.Rotation(math.pi * 0.5, 4, "X"))
        grip_len = r.uniform(0.055, 0.085)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12,
            radius1=0.013, radius2=0.011, depth=grip_len,
            matrix=Matrix.Translation((0, -(base_r + handle_len + grip_len * 0.5), base_h * 0.55)) @ Matrix.Rotation(math.pi * 0.5, 4, "X"))

    else:
        base_r = r.uniform(0.060, 0.082)
        base_h = r.uniform(0.030, 0.050)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=base_r, radius2=base_r*0.88, depth=base_h,
            matrix=Matrix.Translation((0, 0, base_h * 0.5)))
        fork_h = r.uniform(0.15, 0.22)
        fork_w = r.uniform(0.032, 0.050)
        fork_d = r.uniform(0.042, 0.060)
        offset_x = r.uniform(0.035, 0.055)
        bmesh.ops.create_cube(bm, size=1.0,
            matrix=Matrix.Translation((offset_x, 0, base_h + fork_h * 0.45)) @ Matrix.Diagonal((fork_w, fork_d, fork_h * 0.9, 1.0)))
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=0.032, radius2=0.032, depth=0.048,
            matrix=Matrix.Translation((0, 0, base_h + fork_h)) @ Matrix.Rotation(math.pi * 0.5, 4, "Y"))
        knob_r = r.uniform(0.020, 0.028)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12,
            radius1=knob_r, radius2=knob_r * 0.85, depth=0.018,
            matrix=Matrix.Translation((base_r * 0.85, 0, base_h + fork_h)) @ Matrix.Rotation(math.pi * 0.5, 4, "Y"))

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(mesh)
    bm.free()
    obj.location = (0, 0, base_z)
    return obj


def build_telescope_ota_mesh(context, name="Telescope_OTA",
                             tube_len=0.75, aperture_r=0.048,
                             style="MODERN_REFRACTOR", seed=0):
    r = _rng(seed + 3)
    obj, mesh = create_mesh_object(context, name)
    bm = bmesh.new()

    if style == "ANTIQUE_BRASS":
        ap = aperture_r * r.uniform(0.85, 1.12)
        length = tube_len * r.uniform(0.85, 1.15)
        front_len = length * r.uniform(0.55, 0.65)
        rear_len  = length - front_len
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=ap, radius2=ap, depth=length,
            matrix=Matrix.Translation((0, (front_len - rear_len) * 0.5, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, "X"))
        n_rings = r.randint(3, 5)
        for ri in range(n_rings):
            ry = (front_len - rear_len) * 0.5 - length * (ri / (n_rings + 1)) + length * 0.5
            bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
                radius1=ap * 1.06, radius2=ap * 1.06, depth=0.010,
                matrix=Matrix.Translation((0, ry, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, "X"))
        hood_w = r.uniform(0.08, 0.14)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=ap * r.uniform(1.06, 1.12), radius2=ap * r.uniform(1.06, 1.12), depth=hood_w,
            matrix=Matrix.Translation((0, front_len - hood_w * 0.5, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, "X"))
        finder_len = length * r.uniform(0.38, 0.52)
        f_z = ap + r.uniform(0.035, 0.055)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=r.uniform(0.012, 0.020), radius2=r.uniform(0.012, 0.020), depth=finder_len,
            matrix=Matrix.Translation((0, 0, f_z)) @ Matrix.Rotation(math.pi * 0.5, 4, "X"))
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=ap * 0.62, radius2=ap * 0.62, depth=r.uniform(0.14, 0.22),
            matrix=Matrix.Translation((0, -rear_len - r.uniform(0.07, 0.12), 0)) @ Matrix.Rotation(math.pi * 0.5, 4, "X"))

    elif style == "SMART_DIGITAL":
        s_r = aperture_r * r.uniform(1.15, 1.45)
        s_len = tube_len * r.uniform(0.55, 0.75)
        front_len = s_len * r.uniform(0.55, 0.65)
        rear_len  = s_len - front_len
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=32,
            radius1=s_r, radius2=s_r, depth=s_len,
            matrix=Matrix.Translation((0, (front_len - rear_len) * 0.5, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, "X"))
        f_y = front_len
        spider_w = r.uniform(0.007, 0.012)
        bmesh.ops.create_cube(bm, size=1.0,
            matrix=Matrix.Translation((0, f_y, 0)) @ Matrix.Diagonal((s_r * r.uniform(1.75, 2.05), spider_w, spider_w, 1.0)))
        bmesh.ops.create_cube(bm, size=1.0,
            matrix=Matrix.Translation((0, f_y, 0)) @ Matrix.Diagonal((spider_w, spider_w, s_r * r.uniform(1.75, 2.05), 1.0)))
        sub_r = s_r * r.uniform(0.28, 0.38)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=sub_r, radius2=sub_r, depth=0.013,
            matrix=Matrix.Translation((0, f_y, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, "X"))
        dom_r = s_r * r.uniform(0.55, 0.70)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=dom_r,
            matrix=Matrix.Translation((0, -rear_len - dom_r * 0.5, 0)))

    elif style == "CASSEGRAIN_POP":
        c_r   = aperture_r * r.uniform(1.30, 1.60)
        c_len = tube_len * r.uniform(0.40, 0.56)
        front_len = c_len * r.uniform(0.50, 0.60)
        rear_len  = c_len - front_len
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=c_r, radius2=c_r, depth=c_len,
            matrix=Matrix.Translation((0, (front_len - rear_len) * 0.5, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, "X"))
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=c_r * 0.95, radius2=c_r * 0.95, depth=r.uniform(0.004, 0.008),
            matrix=Matrix.Translation((0, front_len - 0.010, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, "X"))
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=c_r * r.uniform(0.28, 0.40), radius2=c_r * r.uniform(0.28, 0.40), depth=0.007,
            matrix=Matrix.Translation((0, front_len - 0.008, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, "X"))
        ey_sz = c_r * r.uniform(0.55, 0.80)
        bmesh.ops.create_cube(bm, size=1.0,
            matrix=Matrix.Translation((0, -rear_len - ey_sz * 0.5, 0)) @ Matrix.Diagonal((ey_sz, ey_sz, ey_sz, 1.0)))
        ep_h = r.uniform(0.04, 0.07)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=r.uniform(0.014, 0.022), radius2=r.uniform(0.016, 0.024), depth=ep_h,
            matrix=Matrix.Translation((0, -rear_len - ey_sz * 0.5, ey_sz * 0.5 + ep_h * 0.5)))

    elif style == "TACTICAL_COMPACT":
        t_r   = aperture_r * r.uniform(1.05, 1.25)
        t_len = tube_len * r.uniform(0.52, 0.70)
        front_len = t_len * r.uniform(0.55, 0.65)
        rear_len  = t_len - front_len
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=t_r, radius2=t_r, depth=t_len,
            matrix=Matrix.Translation((0, (front_len - rear_len) * 0.5, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, "X"))
        hood_len = r.uniform(0.09, 0.16)
        hood_r   = t_r * r.uniform(1.08, 1.18)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=hood_r, radius2=hood_r, depth=hood_len,
            matrix=Matrix.Translation((0, front_len - hood_len * 0.5, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, "X"))
        foc_y = -rear_len - r.uniform(0.02, 0.06)
        dial_r = r.uniform(0.022, 0.032)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=dial_r, radius2=dial_r, depth=r.uniform(0.08, 0.14),
            matrix=Matrix.Translation((0, foc_y, -t_r * 0.9)) @ Matrix.Rotation(math.pi * 0.5, 4, "Y"))
        ey_sz = r.uniform(0.038, 0.058)
        bmesh.ops.create_cube(bm, size=1.0,
            matrix=Matrix.Translation((0, foc_y - ey_sz * 0.5, 0)) @ Matrix.Diagonal((ey_sz, ey_sz, ey_sz, 1.0)))
        ep_h = r.uniform(0.045, 0.075)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=r.uniform(0.018, 0.026), radius2=r.uniform(0.020, 0.028), depth=ep_h,
            matrix=Matrix.Translation((0, foc_y - ey_sz * 0.5, ey_sz * 0.5 + ep_h * 0.5)))

    else:
        ap    = aperture_r * r.uniform(0.88, 1.10)
        length = tube_len * r.uniform(0.88, 1.12)
        front_len = length * r.uniform(0.60, 0.70)
        rear_len  = length - front_len
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=ap, radius2=ap, depth=length,
            matrix=Matrix.Translation((0, (front_len - rear_len) * 0.5, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, "X"))
        ring_y = (front_len - rear_len) * 0.5 + r.uniform(-length * 0.2, length * 0.2)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=ap * 1.03, radius2=ap * 1.03, depth=0.011,
            matrix=Matrix.Translation((0, ring_y, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, "X"))
        hood_len = r.uniform(0.11, 0.18)
        hood_r   = ap * r.uniform(1.18, 1.32)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=hood_r, radius2=ap * r.uniform(1.02, 1.06), depth=hood_len,
            matrix=Matrix.Translation((0, front_len + hood_len * 0.45, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, "X"))
        foc_y  = -rear_len
        tube_r = r.uniform(0.018, 0.026)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=tube_r, radius2=tube_r, depth=r.uniform(0.06, 0.10),
            matrix=Matrix.Translation((0, foc_y - 0.08, 0)) @ Matrix.Rotation(math.pi * 0.5, 4, "X"))
        diag_sz = r.uniform(0.034, 0.050)
        bmesh.ops.create_cube(bm, size=1.0,
            matrix=Matrix.Translation((0, foc_y - r.uniform(0.10, 0.16), 0)) @ Matrix.Diagonal((diag_sz, diag_sz, diag_sz, 1.0)))
        ep_h = r.uniform(0.050, 0.080)
        ep_r  = r.uniform(0.013, 0.020)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=ep_r, radius2=ep_r * r.uniform(1.1, 1.3), depth=ep_h,
            matrix=Matrix.Translation((0, foc_y - r.uniform(0.10, 0.16), diag_sz * 0.5 + ep_h * 0.5)))
        if r.random() > 0.4:
            dock_w = r.uniform(0.045, 0.068)
            dock_h = r.uniform(0.018, 0.028)
            dock_y = r.uniform(-0.05, 0.12)
            bmesh.ops.create_cube(bm, size=1.0,
                matrix=Matrix.Translation((0, dock_y, ap + r.uniform(0.025, 0.05))) @ Matrix.Diagonal((dock_w, dock_w * 1.4, dock_h, 1.0)))

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
    from ..materials.nature_shaders import create_procedural_telescope_shader

    rng = _rng(seed)
    t_height = tripod_height * rng.uniform(0.88, 1.12)
    if style in ("ANTIQUE_BRASS", "CASSEGRAIN_POP"):
        t_height = min(t_height, 0.55)
    spread = rng.uniform(0.38, 0.55)
    t_tube  = tube_length * rng.uniform(0.85, 1.15)
    ap_r    = rng.uniform(0.040, 0.060)

    tripod_obj = build_telescope_tripod_mesh(
        context, name=f"{name}_Tripod",
        height=t_height, leg_spread=spread, style=style, seed=seed)

    mount_obj = build_telescope_mount_mesh(
        context, name=f"{name}_Mount",
        base_z=t_height, style=style, seed=seed)
    mount_obj.parent = tripod_obj
    mount_obj.rotation_euler.z = math.radians(azimuth_deg)

    ota_obj = build_telescope_ota_mesh(
        context, name=f"{name}_OTA",
        tube_len=t_tube, aperture_r=ap_r, style=style, seed=seed)

    fork_h_map = {
        "ANTIQUE_BRASS":    rng.uniform(0.07, 0.12),
        "SMART_DIGITAL":    rng.uniform(0.18, 0.28),
        "CASSEGRAIN_POP":   rng.uniform(0.04, 0.07),
        "TACTICAL_COMPACT": rng.uniform(0.04, 0.08),
    }
    fork_h = fork_h_map.get(style, rng.uniform(0.14, 0.22))
    ota_obj.location = (0, 0, fork_h)
    ota_obj.parent   = mount_obj
    ota_obj.rotation_euler.x = math.radians(-elevation_deg)

    if style == "ANTIQUE_BRASS":
        mat_brass = create_procedural_telescope_shader(f"{name}_Brass_Mat", "BRASS", seed)
        mat_lens  = create_procedural_telescope_shader(f"{name}_Lens_Mat",  "LENS",  seed)
        tripod_obj.data.materials.append(mat_brass)
        mount_obj.data.materials.append(mat_brass)
        ota_obj.data.materials.append(mat_brass)
        ota_obj.data.materials.append(mat_lens)
    elif style == "SMART_DIGITAL":
        mat_silver = create_procedural_telescope_shader(f"{name}_Silver_Mat", "SILVER",       seed)
        mat_carbon = create_procedural_telescope_shader(f"{name}_Carbon_Mat", "CARBON",       seed)
        mat_led    = create_procedural_telescope_shader(f"{name}_LED_Mat",    "EMISSION_LED", seed)
        mat_lens   = create_procedural_telescope_shader(f"{name}_Lens_Mat",   "LENS",         seed)
        tripod_obj.data.materials.append(mat_carbon)
        mount_obj.data.materials.append(mat_carbon)
        mount_obj.data.materials.append(mat_led)
        ota_obj.data.materials.append(mat_silver)
        ota_obj.data.materials.append(mat_carbon)
        ota_obj.data.materials.append(mat_lens)
    elif style == "CASSEGRAIN_POP":
        mat_teal   = create_procedural_telescope_shader(f"{name}_Teal_Mat",   "TEAL",   seed)
        mat_silver = create_procedural_telescope_shader(f"{name}_Silver_Mat", "SILVER", seed)
        mat_black  = create_procedural_telescope_shader(f"{name}_Black_Mat",  "BLACK",  seed)
        mat_lens   = create_procedural_telescope_shader(f"{name}_Lens_Mat",   "LENS",   seed)
        tripod_obj.data.materials.append(mat_silver)
        mount_obj.data.materials.append(mat_black)
        ota_obj.data.materials.append(mat_teal)
        ota_obj.data.materials.append(mat_silver)
        ota_obj.data.materials.append(mat_lens)
    elif style == "TACTICAL_COMPACT":
        mat_black  = create_procedural_telescope_shader(f"{name}_Black_Mat",  "BLACK",  seed)
        mat_silver = create_procedural_telescope_shader(f"{name}_Silver_Mat", "SILVER", seed)
        mat_lens   = create_procedural_telescope_shader(f"{name}_Lens_Mat",   "LENS",   seed)
        tripod_obj.data.materials.append(mat_black)
        mount_obj.data.materials.append(mat_black)
        ota_obj.data.materials.append(mat_black)
        ota_obj.data.materials.append(mat_silver)
        ota_obj.data.materials.append(mat_lens)
    else:
        mat_silver = create_procedural_telescope_shader(f"{name}_Silver_Mat", "SILVER", seed)
        mat_black  = create_procedural_telescope_shader(f"{name}_Black_Mat",  "BLACK",  seed)
        mat_orange = create_procedural_telescope_shader(f"{name}_Orange_Mat", "ORANGE", seed)
        mat_lens   = create_procedural_telescope_shader(f"{name}_Lens_Mat",   "LENS",   seed)
        tripod_obj.data.materials.append(mat_black)
        mount_obj.data.materials.append(mat_black)
        ota_obj.data.materials.append(mat_silver)
        ota_obj.data.materials.append(mat_black)
        ota_obj.data.materials.append(mat_orange)
        ota_obj.data.materials.append(mat_lens)

    root_obj = bpy.data.objects.new(name, None)
    root_obj.empty_display_type = "PLAIN_AXES"
    root_obj.empty_display_size = 0.2
    context.collection.objects.link(root_obj)
    tripod_obj.parent = root_obj

    context.view_layer.objects.active = root_obj
    root_obj.select_set(True)
    return root_obj
