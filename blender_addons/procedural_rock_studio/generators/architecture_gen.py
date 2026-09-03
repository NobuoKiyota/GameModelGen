import bpy
import bmesh
import math
import mathutils
import random

def build_antique_leg_or_column(bm, height, radius, style="ORNAMENTAL", is_twist=False, seed=0):
    """アンティーク調の脚・柱生成"""
    random.seed(seed)
    all_verts = []
    
    if style == "SIMPLE":
        res = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=radius, radius2=radius, depth=height
        )
        all_verts.extend(res['verts'])
        
    elif style == "REINFORCED":
        shaft_h = height * 0.8
        cap_h = height * 0.1
        res_s = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=radius * 0.85, radius2=radius * 0.85, depth=shaft_h
        )
        all_verts.extend(res_s['verts'])
        
        res_tc = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(radius * 2.4, radius * 2.4, cap_h), verts=res_tc['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, height * 0.45), verts=res_tc['verts'])
        all_verts.extend(res_tc['verts'])
        
        res_bc = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(radius * 2.4, radius * 2.4, cap_h), verts=res_bc['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, -height * 0.45), verts=res_bc['verts'])
        all_verts.extend(res_bc['verts'])

    elif style == "TWISTED" or is_twist:
        res = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=12,
            radius1=radius * 0.9, radius2=radius * 0.9, depth=height * 0.8
        )
        bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=8, use_grid_fill=True)
        
        for v in bm.verts:
            z_fac = (v.co.z / (height * 0.8))
            angle = z_fac * math.pi * 3.0
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            x_new = v.co.x * cos_a - v.co.y * sin_a
            y_new = v.co.x * sin_a + v.co.y * cos_a
            v.co.x = x_new
            v.co.y = y_new
        all_verts.extend(bm.verts[:])
        
        cap_h = height * 0.1
        res_tc = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(radius * 2.2, radius * 2.2, cap_h), verts=res_tc['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, height * 0.45), verts=res_tc['verts'])
        all_verts.extend(res_tc['verts'])
        
        res_bc = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(radius * 2.2, radius * 2.2, cap_h), verts=res_bc['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, -height * 0.45), verts=res_bc['verts'])
        all_verts.extend(res_bc['verts'])

    else: # ORNAMENTAL
        shaft_h = height * 0.76
        cap_h = height * 0.12
        res_s = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=radius * 0.65, radius2=radius * 0.65, depth=shaft_h
        )
        all_verts.extend(res_s['verts'])
        
        res_ub = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=radius * 1.35)
        bmesh.ops.scale(bm, vec=(1.0, 1.0, 0.8), verts=res_ub['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, height * 0.22), verts=res_ub['verts'])
        all_verts.extend(res_ub['verts'])

        res_lb = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=radius * 1.35)
        bmesh.ops.scale(bm, vec=(1.0, 1.0, 0.8), verts=res_lb['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, -height * 0.22), verts=res_lb['verts'])
        all_verts.extend(res_lb['verts'])

        res_mr = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=radius * 1.1, radius2=radius * 1.1, depth=height * 0.05
        )
        all_verts.extend(res_mr['verts'])

        res_tc = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(radius * 2.3, radius * 2.3, cap_h), verts=res_tc['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, height * 0.44), verts=res_tc['verts'])
        all_verts.extend(res_tc['verts'])
        
        res_bc = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(radius * 2.3, radius * 2.3, cap_h), verts=res_bc['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, -height * 0.44), verts=res_bc['verts'])
        all_verts.extend(res_bc['verts'])

    return all_verts


def build_cobblestone_floor_mesh(bm, size_x, size_y, size_z, seed=0,
                                 stone_size=0.35, grout_depth=0.04, jitter=0.4):
    """サコッシュ伊藤氏の動画（-3QuBIoV-B8）技法に基づく立体石畳メッシュ
    - 不規則グリッド（ボロノイ風変形）による自然な石の敷き詰め
    - 各石のインセットによる目地（溝）の形成
    - 各石ごとの個別立体押し出し・ランダム高さ・微小チルト・角の面取り風化
    """
    rng = random.Random(seed)
    
    # 基礎寸法の決定
    cols = max(3, int(round(size_x / max(0.1, stone_size))))
    rows = max(3, int(round(size_y / max(0.1, stone_size))))
    
    step_x = size_x / cols
    step_y = size_y / rows
    half_x = size_x * 0.5
    half_y = size_y * 0.5
    
    # スラブ基底の厚みと石の突出高
    base_h = size_z * 0.35
    extrude_h_base = size_z * 0.65
    
    # ── 1. 不規則ジッター頂点グリッドの作成 ──────────────────
    grid_verts = []
    for r in range(rows + 1):
        row_verts = []
        for c in range(cols + 1):
            bx = -half_x + c * step_x
            by = -half_y + r * step_y
            
            # 外周以外はランダムにジッター（不規則タイル化）
            if 0 < c < cols and 0 < r < rows:
                jx = (rng.uniform(-0.35, 0.35) * step_x) * jitter
                jy = (rng.uniform(-0.35, 0.35) * step_y) * jitter
            else:
                jx, jy = 0.0, 0.0
                
            v = bm.verts.new((bx + jx, by + jy, base_h))
            row_verts.append(v)
        grid_verts.append(row_verts)
        
    # ── 2. 各石の個別生成（目地インセット＋立体押し出し）────
    grout_w = min(step_x, step_y) * (0.08 + jitter * 0.06)
    
    for r in range(rows):
        for c in range(cols):
            v0 = grid_verts[r][c]
            v1 = grid_verts[r][c + 1]
            v2 = grid_verts[r + 1][c + 1]
            v3 = grid_verts[r + 1][c]
            
            # 石の中心
            cx = (v0.co.x + v1.co.x + v2.co.x + v3.co.x) * 0.25
            cy = (v0.co.y + v1.co.y + v2.co.y + v3.co.y) * 0.25
            
            # 石ごとのランダム変位（高さ・チルト）
            stone_h = extrude_h_base * rng.uniform(0.75, 1.25)
            tilt_x = rng.uniform(-0.04, 0.04) * jitter
            tilt_y = rng.uniform(-0.04, 0.04) * jitter
            
            # インセットされた石の底面頂点
            inset_pts = []
            for corner in [v0, v1, v2, v3]:
                dx = corner.co.x - cx
                dy = corner.co.y - cy
                dist = math.hypot(dx, dy)
                scale = max(0.2, (dist - grout_w) / max(0.001, dist))
                ix = cx + dx * scale
                iy = cy + dy * scale
                inset_pts.append((ix, iy, base_h))
                
            iv0 = bm.verts.new(inset_pts[0])
            iv1 = bm.verts.new(inset_pts[1])
            iv2 = bm.verts.new(inset_pts[2])
            iv3 = bm.verts.new(inset_pts[3])
            
            # 目地底面（モルタル面）
            bm.faces.new((v0, v1, iv1, iv0))
            bm.faces.new((v1, v2, iv2, iv1))
            bm.faces.new((v2, v3, iv3, iv2))
            bm.faces.new((v3, v0, iv0, iv3))
            
            # 石の天面頂点（押し出し＋チルト＋角丸め）
            top_pts = []
            for ip in inset_pts:
                tz = ip[2] + stone_h + (ip[0] - cx) * tilt_x + (ip[1] - cy) * tilt_y
                # 表面の微小ノイズ
                noise_z = rng.uniform(-0.01, 0.01) * stone_h
                top_pts.append((ip[0], ip[1], tz + noise_z))
                
            tv0 = bm.verts.new(top_pts[0])
            tv1 = bm.verts.new(top_pts[1])
            tv2 = bm.verts.new(top_pts[2])
            tv3 = bm.verts.new(top_pts[3])
            
            # 石の側面
            bm.faces.new((iv0, iv1, tv1, tv0))
            bm.faces.new((iv1, iv2, tv2, tv1))
            bm.faces.new((iv2, iv3, tv3, tv2))
            bm.faces.new((iv3, iv0, tv0, tv3))
            
            # 石の天面
            bm.faces.new((tv0, tv1, tv2, tv3))
            
    # ── 3. 底面スラブの閉鎖（ゲームモデル用クローズドメッシュ）──
    bot_verts = []
    for r in [0, rows]:
        for c in range(cols + 1):
            bv = bm.verts.new((grid_verts[r][c].co.x, grid_verts[r][c].co.y, 0.0))
            bot_verts.append(bv)
            
    # 側面外壁を下に伸ばす
    for c in range(cols):
        bm.faces.new((grid_verts[0][c], grid_verts[0][c + 1],
                      bm.verts.new((grid_verts[0][c + 1].co.x, grid_verts[0][c + 1].co.y, 0.0)),
                      bm.verts.new((grid_verts[0][c].co.x, grid_verts[0][c].co.y, 0.0))))
        bm.faces.new((grid_verts[rows][c + 1], grid_verts[rows][c],
                      bm.verts.new((grid_verts[rows][c].co.x, grid_verts[rows][c].co.y, 0.0)),
                      bm.verts.new((grid_verts[rows][c + 1].co.x, grid_verts[rows][c + 1].co.y, 0.0))))
    for r in range(rows):
        bm.faces.new((grid_verts[r + 1][0], grid_verts[r][0],
                      bm.verts.new((grid_verts[r][0].co.x, grid_verts[r][0].co.y, 0.0)),
                      bm.verts.new((grid_verts[r + 1][0].co.x, grid_verts[r + 1][0].co.y, 0.0))))
        bm.faces.new((grid_verts[r][cols], grid_verts[r + 1][cols],
                      bm.verts.new((grid_verts[r + 1][cols].co.x, grid_verts[r + 1][cols].co.y, 0.0)),
                      bm.verts.new((grid_verts[r][cols].co.x, grid_verts[r][cols].co.y, 0.0))))
                      
    # 最底面
    b0 = bm.verts.new((-half_x, -half_y, 0.0))
    b1 = bm.verts.new(( half_x, -half_y, 0.0))
    b2 = bm.verts.new(( half_x,  half_y, 0.0))
    b3 = bm.verts.new((-half_x,  half_y, 0.0))
    bm.faces.new((b0, b3, b2, b1))
    
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    return bm.verts[:]


def build_cobblestone_wall_mesh(bm, size_x, size_y, size_z, shape="STRAIGHT",
                                seed=0, stone_size=0.35, grout_depth=0.03, jitter=0.4):
    """古城風立体石積み壁メッシュ生成
    - 互い違い配置（ランニングボンド）の石積みブロック
    - 各ブロックの前後の不揃いな飛び出し・傾き・目地の溝彫り
    """
    rng = random.Random(seed)
    wall_th = size_y * 0.45
    half_th = wall_th * 0.5
    
    courses = max(3, int(round(size_z / max(0.12, stone_size * 0.6))))
    course_h = size_z / courses
    
    half_w = size_x * 0.5
    grout_w = min(stone_size, course_h) * 0.08
    
    # ── 各段ごとの石積みブロック ──────────────────────────
    for ci in range(courses):
        cz_bot = ci * course_h
        cz_top = cz_bot + course_h - grout_w
        
        # 偶数段と奇数段で半ブロックずらす
        is_offset = (ci % 2 == 1)
        row_stone_len = stone_size * rng.uniform(0.85, 1.15)
        num_stones = max(2, int(round(size_x / max(0.1, row_stone_len))))
        actual_stone_w = size_x / num_stones
        
        for si in range(num_stones):
            sx_start = -half_w + si * actual_stone_w + (grout_w * 0.5)
            sx_end   = sx_start + actual_stone_w - grout_w
            
            # 前後の飛び出しジッター（古城の石積みの風合い）
            y_bump_front = rng.uniform(-0.02, 0.035) * jitter * wall_th
            y_bump_back  = rng.uniform(-0.02, 0.035) * jitter * wall_th
            z_tilt       = rng.uniform(-0.015, 0.015) * jitter * course_h
            
            # 直方体ブロックの作成
            bx = (sx_start + sx_end) * 0.5
            by = 0.0
            bz = (cz_bot + cz_top) * 0.5
            bw = (sx_end - sx_start)
            bh = (cz_top - cz_bot)
            
            # 各頂点
            v_flb = bm.verts.new((sx_start, -half_th + y_bump_front, cz_bot))
            v_frb = bm.verts.new((sx_end,   -half_th + y_bump_front, cz_bot))
            v_frt = bm.verts.new((sx_end,   -half_th + y_bump_front, cz_top + z_tilt))
            v_flt = bm.verts.new((sx_start, -half_th + y_bump_front, cz_top - z_tilt))
            
            v_blb = bm.verts.new((sx_start,  half_th + y_bump_back,  cz_bot))
            v_brb = bm.verts.new((sx_end,    half_th + y_bump_back,  cz_bot))
            v_brt = bm.verts.new((sx_end,    half_th + y_bump_back,  cz_top + z_tilt))
            v_blt = bm.verts.new((sx_start,  half_th + y_bump_back,  cz_top - z_tilt))
            
            # 6面
            bm.faces.new((v_flb, v_frb, v_frt, v_flt))  # 前
            bm.faces.new((v_brb, v_blb, v_blt, v_brt))  # 後
            bm.faces.new((v_blb, v_flb, v_flt, v_blt))  # 左
            bm.faces.new((v_frb, v_brb, v_brt, v_frt))  # 右
            bm.faces.new((v_flt, v_frt, v_brt, v_blt))  # 上
            bm.faces.new((v_blb, v_brb, v_frb, v_flb))  # 下
            
    # 目地充填用の内芯（隙間が見えないようにする土台コア）
    core = bmesh.ops.create_cube(bm, size=1.0)['verts']
    bmesh.ops.scale(bm, vec=(size_x * 0.98, wall_th * 0.75, size_z), verts=core)
    bmesh.ops.translate(bm, vec=(0, 0, size_z * 0.5), verts=core)
    
    # 湾曲壁 (CURVED) の場合は円弧状に変形
    if shape == "CURVED":
        radius = size_x * 0.8
        for v in bm.verts:
            ang = (v.co.x / size_x) * 1.1
            orig_y = v.co.y
            v.co.x = math.sin(ang) * (radius + orig_y)
            v.co.y = math.cos(ang) * (radius + orig_y) - radius
            
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    return bm.verts[:]


def build_floor_base(bm, size_x, size_y, size_z, shape="SQUARE", seed=0,
                     stone_size=0.35, grout_depth=0.035, jitter=0.45):
    random.seed(seed)
    if shape == "COBBLESTONE":
        return build_cobblestone_floor_mesh(bm, size_x, size_y, size_z, seed=seed,
                                            stone_size=stone_size, grout_depth=grout_depth, jitter=jitter)
    elif shape == "HEX_PAVER" or shape == "HEXAGON":
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=6,
            radius1=size_x * 0.5, radius2=size_x * 0.5, depth=size_z
        )
        bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2, use_grid_fill=True)
    elif shape == "CIRCLE":
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=32,
            radius1=size_x * 0.5, radius2=size_x * 0.5, depth=size_z
        )
        bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2, use_grid_fill=True)
    else:
        verts = bmesh.ops.create_cube(bm, size=1.0)['verts']
        bmesh.ops.scale(bm, vec=(size_x, size_y, size_z), verts=verts)
        bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2, use_grid_fill=True)
    return bm.verts[:]


def build_wall_base(bm, size_x, size_y, size_z, shape="STRAIGHT", seed=0,
                    stone_size=0.35, grout_depth=0.03, jitter=0.45):
    random.seed(seed)
    if shape == "COBBLE_WALL":
        return build_cobblestone_wall_mesh(bm, size_x, size_y, size_z, shape="STRAIGHT", seed=seed,
                                           stone_size=stone_size, grout_depth=grout_depth, jitter=jitter)
    elif shape == "TRIANGLE":
        th = size_y * 0.35
        half_w = size_x * 0.5
        half_th = th * 0.5
        h = size_z
        v_ft = bm.verts.new((0, -half_th, h * 0.5))
        v_fl = bm.verts.new((-half_w, -half_th, -h * 0.5))
        v_fr = bm.verts.new((half_w, -half_th, -h * 0.5))
        v_bt = bm.verts.new((0, half_th, h * 0.5))
        v_bl = bm.verts.new((-half_w, half_th, -h * 0.5))
        v_br = bm.verts.new((half_w, half_th, -h * 0.5))
        bm.faces.new((v_fl, v_fr, v_ft))
        bm.faces.new((v_bl, v_bt, v_br))
        bm.faces.new((v_fl, v_bl, v_br, v_fr))
        bm.faces.new((v_ft, v_bt, v_bl, v_fl))
        bm.faces.new((v_fr, v_br, v_bt, v_ft))
    elif shape == "L_SHAPE":
        v1 = bmesh.ops.create_cube(bm, size=1.0)['verts']
        bmesh.ops.scale(bm, vec=(size_x, size_y * 0.4, size_z), verts=v1)
        bmesh.ops.translate(bm, vec=(0, -size_x * 0.25, 0), verts=v1)
        v2 = bmesh.ops.create_cube(bm, size=1.0)['verts']
        bmesh.ops.scale(bm, vec=(size_y * 0.4, size_x * 0.5, size_z), verts=v2)
        bmesh.ops.translate(bm, vec=(-size_x * 0.5 + size_y * 0.2, 0, 0), verts=v2)
    elif shape == "CURVED":
        res = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=size_x * 0.8, radius2=size_x * 0.8, depth=size_z
        )
        verts = res['verts']
        bmesh.ops.scale(bm, vec=(1.0, 0.4, 1.0), verts=verts)
    else:
        verts = bmesh.ops.create_cube(bm, size=1.0)['verts']
        bmesh.ops.scale(bm, vec=(size_x, size_y * 0.35, size_z), verts=verts)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2, use_grid_fill=True)
    return bm.verts[:]


def build_fluted_shaft(bm, height, radius_base, flutes=16, entasis=0.08, cuts_z=12):
    """エンタシス（胴張り）と立体フルーティング（縦溝彫り込み）を持つ神殿柱身"""
    all_verts = []
    num_pts = max(8, flutes * 2)
    step_ang = (math.pi * 2.0) / num_pts
    flute_depth = (2.0 * math.pi * radius_base / num_pts) * 0.40
    
    rings = []
    for zi in range(cuts_z + 1):
        zf = zi / cuts_z
        z_pos = (zf - 0.5) * height
        # エンタシス: 中央部が膨らみ、上部が細くなる視覚補正
        ent_factor = 1.0 + math.sin(zf * math.pi) * entasis - (zf * 0.10)
        cur_r = radius_base * ent_factor
        
        ring_v = []
        for pi in range(num_pts):
            ang = pi * step_ang
            # 奇数は溝（凹み）、偶数は山
            r = max(0.01, cur_r - flute_depth) if (pi % 2 == 1) else cur_r
            v = bm.verts.new((math.cos(ang) * r, math.sin(ang) * r, z_pos))
            ring_v.append(v)
            all_verts.append(v)
        rings.append(ring_v)
        
    for zi in range(cuts_z):
        r0 = rings[zi]
        r1 = rings[zi + 1]
        for pi in range(num_pts):
            p_next = (pi + 1) % num_pts
            bm.faces.new((r0[pi], r0[p_next], r1[p_next], r1[pi]))
            
    # 上下キャップ
    top_cap = bm.faces.new(reversed(rings[-1]))
    bot_cap = bm.faces.new(rings[0])
    return all_verts


def build_classical_capital_and_base(bm, height, radius):
    """クラシック多段柱頭（エキノス・アバクス）と基壇（トロス・プリンス）"""
    all_verts = []
    cap_h = height * 0.08
    base_h = height * 0.09
    
    # ── 基壇 (Base) ──────────────────────────────────────
    # 方形台座 (Plinth)
    res_plinth = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(radius * 2.6, radius * 2.6, base_h * 0.5), verts=res_plinth['verts'])
    bmesh.ops.translate(bm, vec=(0, 0, -height * 0.5 - base_h * 0.75), verts=res_plinth['verts'])
    all_verts.extend(res_plinth['verts'])
    
    # 円形トロスリング (Torus)
    res_torus = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=24,
        radius1=radius * 1.35, radius2=radius * 1.15, depth=base_h * 0.5
    )
    bmesh.ops.translate(bm, vec=(0, 0, -height * 0.5 - base_h * 0.25), verts=res_torus['verts'])
    all_verts.extend(res_torus['verts'])
    
    # ── 柱頭 (Capital) ───────────────────────────────────
    # 湾曲受皿 (Echinus)
    res_echinus = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=24,
        radius1=radius * 0.95, radius2=radius * 1.32, depth=cap_h * 0.5
    )
    bmesh.ops.translate(bm, vec=(0, 0, height * 0.5 + cap_h * 0.25), verts=res_echinus['verts'])
    all_verts.extend(res_echinus['verts'])
    
    # 方形上板 (Abacus)
    res_abacus = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(radius * 2.5, radius * 2.5, cap_h * 0.5), verts=res_abacus['verts'])
    bmesh.ops.translate(bm, vec=(0, 0, height * 0.5 + cap_h * 0.75), verts=res_abacus['verts'])
    all_verts.extend(res_abacus['verts'])
    
    return all_verts


def build_stone_drum_pillar(bm, height, radius, drums=7, seed=0):
    """古代遺跡のドラム石積み柱（円盤状の石ブロック積み重ね＆目地溝）"""
    rng = random.Random(seed)
    all_verts = []
    drum_h = height / drums
    grout_gap = drum_h * 0.08
    actual_drum_h = drum_h - grout_gap
    
    for di in range(drums):
        z_center = -height * 0.5 + (di + 0.5) * drum_h
        
        # 各ドラムのわずかなランダムサイズ・中心ズレ（遺跡の風化感）
        d_rad = radius * rng.uniform(0.96, 1.04)
        ox = rng.uniform(-0.015, 0.015) * radius
        oy = rng.uniform(-0.015, 0.015) * radius
        
        res = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=20,
            radius1=d_rad, radius2=d_rad * rng.uniform(0.98, 1.02),
            depth=actual_drum_h
        )
        bmesh.ops.translate(bm, vec=(ox, oy, z_center), verts=res['verts'])
        
        # 表面の微小ジッターノイズ
        for v in res['verts']:
            v.co.x += rng.uniform(-0.008, 0.008) * radius
            v.co.y += rng.uniform(-0.008, 0.008) * radius
            v.co.z += rng.uniform(-0.005, 0.005) * drum_h
        all_verts.extend(res['verts'])
        
    # 上下に石積みの素朴な四角い台座と笠石
    cap_v = bmesh.ops.create_cube(bm, size=1.0)['verts']
    bmesh.ops.scale(bm, vec=(radius * 2.3, radius * 2.3, height * 0.06), verts=cap_v)
    bmesh.ops.translate(bm, vec=(0, 0, height * 0.5 + height * 0.03), verts=cap_v)
    all_verts.extend(cap_v)
    
    base_v = bmesh.ops.create_cube(bm, size=1.0)['verts']
    bmesh.ops.scale(bm, vec=(radius * 2.4, radius * 2.4, height * 0.08), verts=base_v)
    bmesh.ops.translate(bm, vec=(0, 0, -height * 0.5 - height * 0.04), verts=base_v)
    all_verts.extend(base_v)
    
    return all_verts


def build_gothic_clustered_pillar(bm, height, radius, colonnettes=6):
    """ゴシック大聖堂の束ね柱（主柱＋周囲の小柱クラスタ＋結束リング）"""
    all_verts = []
    shaft_h = height * 0.84
    
    # ── 1. 中央大主柱 ────────────────────────────────────
    main_r = radius * 0.65
    res_m = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=16,
        radius1=main_r, radius2=main_r, depth=shaft_h
    )
    all_verts.extend(res_m['verts'])
    
    # ── 2. 周囲の束ね小柱 (Colonnettes) ──────────────────
    sub_r = radius * 0.22
    orbit_r = radius * 0.78
    step_ang = (math.pi * 2.0) / colonnettes
    
    for ci in range(colonnettes):
        ang = ci * step_ang
        cx = math.cos(ang) * orbit_r
        cy = math.sin(ang) * orbit_r
        res_sub = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=12,
            radius1=sub_r, radius2=sub_r, depth=shaft_h
        )
        bmesh.ops.translate(bm, vec=(cx, cy, 0), verts=res_sub['verts'])
        all_verts.extend(res_sub['verts'])
        
    # ── 3. 結束リングカラー (Ring Collars: 1/3 と 2/3 高さ) ──
    for zf in [-0.18, 0.18]:
        res_ring = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=radius * 1.08, radius2=radius * 1.08, depth=height * 0.04
        )
        bmesh.ops.translate(bm, vec=(0, 0, shaft_h * zf), verts=res_ring['verts'])
        all_verts.extend(res_ring['verts'])
        
    # ── 4. ゴシック多段基壇＆柱頭 ────────────────────────
    cap_h = height * 0.08
    base_h = height * 0.08
    
    res_base = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=colonnettes * 2,
        radius1=radius * 1.35, radius2=radius * 1.15, depth=base_h
    )
    bmesh.ops.translate(bm, vec=(0, 0, -shaft_h * 0.5 - base_h * 0.5), verts=res_base['verts'])
    all_verts.extend(res_base['verts'])
    
    res_cap = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=colonnettes * 2,
        radius1=radius * 1.12, radius2=radius * 1.35, depth=cap_h
    )
    bmesh.ops.translate(bm, vec=(0, 0, shaft_h * 0.5 + cap_h * 0.5), verts=res_cap['verts'])
    all_verts.extend(res_cap['verts'])
    
    return all_verts


def build_solomonic_twisted_pillar(bm, height, radius):
    """バロック・ソロモン螺旋柱（優美なツイストヘリックス）"""
    all_verts = []
    shaft_h = height * 0.82
    cuts = 20
    
    res = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=16,
        radius1=radius * 0.85, radius2=radius * 0.85, depth=shaft_h
    )
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=cuts, use_grid_fill=True)
    
    # Z座標に応じた回転（螺旋ねじれ）
    twist_rot = math.pi * 3.0 # 540度
    for v in bm.verts:
        zf = (v.co.z / shaft_h) # -0.5 〜 0.5
        ang = zf * twist_rot
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        # 螺旋の波状うねり
        wave = math.sin(zf * math.pi * 4.0) * (radius * 0.18)
        nx = v.co.x * cos_a - v.co.y * sin_a + math.cos(ang) * wave
        ny = v.co.x * sin_a + v.co.y * cos_a + math.sin(ang) * wave
        v.co.x = nx
        v.co.y = ny
    all_verts.extend(bm.verts[:])
    
    # クラシック柱頭と基壇
    cap_v = build_classical_capital_and_base(bm, shaft_h, radius)
    all_verts.extend(cap_v)
    return all_verts


def build_pillar_base(bm, size_x, size_y, size_z, style="CLASSIC_FLUTED",
                      flutes=16, colonnettes=6, entasis=0.08, seed=0):
    """建築柱の総合生成エンジン（ギリシャ神殿、ゴシック束ね柱、ドラム石積み、ソロモン螺旋）"""
    radius = (size_x + size_y) * 0.25 # 平均半径
    height = size_z
    
    if style == "GOTHIC_CLUSTERED":
        return build_gothic_clustered_pillar(bm, height, radius, colonnettes=colonnettes)
    elif style == "STONE_DRUM":
        return build_stone_drum_pillar(bm, height, radius, drums=7, seed=seed)
    elif style == "TWISTED_SOLOMONIC":
        return build_solomonic_twisted_pillar(bm, height, radius)
    else: # CLASSIC_FLUTED (デフォルト)
        shaft_h = height * 0.83
        verts = build_fluted_shaft(bm, shaft_h, radius, flutes=flutes, entasis=entasis)
        cap_verts = build_classical_capital_and_base(bm, shaft_h, radius)
        return verts + cap_verts


def build_beam_base(bm, size_x, size_y, size_z):
    rad = min(size_y, size_z) * 0.35
    length = size_x * 2.2
    res = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=16,
        radius1=rad, radius2=rad, depth=length
    )
    verts = res['verts']
    bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(90), 3, 'Y'), verts=verts)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2, use_grid_fill=True)
    return bm.verts[:]


def build_beam_arch_base(bm, size_x, size_y, size_z):
    all_verts = []
    rad = min(size_x, size_y) * 0.14
    res_top = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=16,
        radius1=rad, radius2=rad, depth=size_x * 2.2
    )
    top_verts = res_top['verts']
    bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(90), 3, 'Y'), verts=top_verts)
    bmesh.ops.translate(bm, vec=(0, 0, size_z * 1.0), verts=top_verts)
    all_verts.extend(top_verts)
    
    res_lp = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=16,
        radius1=rad * 1.1, radius2=rad * 1.1, depth=size_z * 2.0
    )
    lp_verts = res_lp['verts']
    bmesh.ops.translate(bm, vec=(-size_x * 0.85, 0, 0), verts=lp_verts)
    all_verts.extend(lp_verts)
    
    res_rp = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=16,
        radius1=rad * 1.1, radius2=rad * 1.1, depth=size_z * 2.0
    )
    rp_verts = res_rp['verts']
    bmesh.ops.translate(bm, vec=(size_x * 0.85, 0, 0), verts=rp_verts)
    all_verts.extend(rp_verts)
    
    res_lb = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=12,
        radius1=rad * 0.85, radius2=rad * 0.85, depth=size_z * 0.8
    )
    lb_verts = res_lb['verts']
    bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(-45), 3, 'Y'), verts=lb_verts)
    bmesh.ops.translate(bm, vec=(-size_x * 0.55, 0, size_z * 0.7), verts=lb_verts)
    all_verts.extend(lb_verts)

    res_rb = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=12,
        radius1=rad * 0.85, radius2=rad * 0.85, depth=size_z * 0.8
    )
    rb_verts = res_rb['verts']
    bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(45), 3, 'Y'), verts=rb_verts)
    bmesh.ops.translate(bm, vec=(size_x * 0.55, 0, size_z * 0.7), verts=rb_verts)
    all_verts.extend(rb_verts)
    return all_verts
