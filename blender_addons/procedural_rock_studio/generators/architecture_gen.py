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


def build_procedural_stone_arch_bmesh(
    bm,
    size_x=3.2,
    size_y=0.8,
    size_z=3.8,
    style='ROMAN_ROUND',
    structure_type='SINGLE',
    span_count=3,
    pillar_shape='SQUARE_PIER',
    pillar_width=0.55,
    column_height=2.2,
    damage=0.35,
    has_keystone=True,
    keystone_scale=1.25,
    molding_tiers=2,
    has_spandrel=True,
    has_pedestal=True,
    seed=0,
    **kwargs
):
    """
    Builds an architecturally authentic classical stone arch based on hbitproject's tutorial:
    - Watertight solid mesh topology with zero missing outer rim faces
    - Seamless gapless spandrel wall generation using vertical quad strips (no triangular voids)
    - Full customization for pillar width (thickness) and column height (length)
    - Natural chipping, edge damage, and voussoir block depth offsets (damage parameter)
    - Authentic semicircular, pointed (Gothic), segmental, or horseshoe arch ring with tiered stepped moldings
    - Trapezoidal Keystone firmly wedged at the crown
    - Clean rectangular boundary box for seamless modular tiling in Unreal Engine / Unity
    - Multi-span Colonnade / Arcade and Vault ceiling support
    """
    import mathutils
    import random

    rng = random.Random(seed)

    spans = span_count if structure_type == 'COLONNADE' else 1
    depth = size_y
    if structure_type == 'VAULT_CEILING':
        depth = max(size_y, size_x * 1.8)

    span_w = size_x
    total_w = span_w * spans
    half_d = depth * 0.5

    # 1. 柱とアーチの幾何学設計（ユーザー指定の太さ・長さを直接反映）
    pillar_w = max(0.15, min(pillar_width, span_w * 0.45))
    col_h = max(0.4, column_height)

    plinth_h = min(0.35, col_h * 0.12) if has_pedestal else 0.0
    capital_h = min(0.35, col_h * 0.13)
    spring_z = plinth_h + col_h + capital_h

    opening_w = max(0.6, span_w - pillar_w)
    r_in = opening_w * 0.5
    ring_thick = min(0.42, pillar_w * 0.65)
    r_out = r_in + ring_thick

    # Rise (アーチの盛り上がり高さ)
    if style == 'GOTHIC_POINTED':
        arch_rise = r_in * 1.30
    elif style == 'SEGMENTAL':
        arch_rise = r_in * 0.55
    elif style == 'HORSESHOE':
        arch_rise = r_in * 1.15
    else: # ROMAN_ROUND
        arch_rise = r_in

    attic_h = 0.25
    wall_top_z = spring_z + arch_rise + ring_thick * 0.4 + attic_h
    cornice_h = 0.28
    segments = 24
    m_step = 0.03 # モールディング段差

    def add_box(center, dims, chip=True):
        v_res = bmesh.ops.create_cube(
            bm, size=1.0, matrix=mathutils.Matrix.Translation(center) @ mathutils.Matrix.Diagonal((*dims, 1.0))
        )['verts']
        if damage > 0.05 and chip:
            noise_amt = damage * 0.014
            for v in v_res:
                v.co.x += rng.uniform(-noise_amt, noise_amt)
                v.co.y += rng.uniform(-noise_amt, noise_amt)
                v.co.z += rng.uniform(-noise_amt, noise_amt)
        return v_res

    start_cx = -total_w * 0.5 + span_w * 0.5

    # ── A. 柱（ピアー・カラム）の生成（全スパンで均等配置） ──
    for p_idx in range(spans + 1):
        px = -total_w * 0.5 + p_idx * span_w

        # 柱脚 (Plinth Base)
        if has_pedestal:
            add_box((px, 0.0, plinth_h * 0.5), (pillar_w * 1.25, depth * 1.15, plinth_h))
            add_box((px, 0.0, plinth_h * 0.85), (pillar_w * 1.12, depth * 1.08, plinth_h * 0.3))

        # 柱身 (Shaft)
        s_cz = plinth_h + col_h * 0.5
        if pillar_shape == 'ROUND_COLUMN':
            rad = pillar_w * 0.46
            res = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=18,
                radius1=rad, radius2=rad, depth=col_h
            )
            bmesh.ops.translate(bm, vec=(px, 0.0, s_cz), verts=res['verts'])
        elif pillar_shape == 'OCTAGONAL':
            rad = pillar_w * 0.48
            res = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=8,
                radius1=rad, radius2=rad, depth=col_h
            )
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(22.5), 3, 'Z'), verts=res['verts'])
            bmesh.ops.translate(bm, vec=(px, 0.0, s_cz), verts=res['verts'])
        else: # SQUARE_PIER
            add_box((px, 0.0, s_cz), (pillar_w, depth, col_h))

        # 柱頭 (Impost Capital) - 上面を spring_z に完全密着
        c1_h = capital_h * 0.45
        c2_h = capital_h * 0.55
        add_box((px, 0.0, plinth_h + col_h + c1_h * 0.5), (pillar_w * 1.12, depth * 1.08, c1_h))
        add_box((px, 0.0, spring_z - c2_h * 0.5), (pillar_w * 1.25, depth * 1.15, c2_h))

    # ── B. 各スパンのアーチリング＆隙間ゼロスパンドレル壁 ──
    for ispan in range(spans):
        cx = start_cx + ispan * span_w

        # 2D正面プロファイル点
        inner_pts = []
        outer_pts = []

        if style == 'GOTHIC_POINTED':
            d_center = r_in * 0.45
            for s in range(segments // 2 + 1):
                t = s / float(segments // 2)
                x_val = -r_in + t * r_in
                z_val = spring_z + math.sqrt(max(0.01, (r_in + d_center)**2 - (x_val - d_center)**2))
                inner_pts.append((x_val, z_val))
                z_out = z_val + ring_thick * (1.0 - t * 0.15) if s > 0 else spring_z
                outer_pts.append((x_val * (1.0 + ring_thick / r_in), z_out))
            for s in range(1, segments // 2 + 1):
                idx = (segments // 2) - s
                inner_pts.append((-inner_pts[idx][0], inner_pts[idx][1]))
                outer_pts.append((-outer_pts[idx][0], outer_pts[idx][1]))
        elif style == 'SEGMENTAL':
            h_sag = arch_rise
            r_seg = (r_in**2 + h_sag**2) / (2.0 * h_sag)
            c_seg_z = spring_z - (r_seg - h_sag)
            half_angle = math.asin(min(0.99, r_in / r_seg))
            for s in range(segments + 1):
                t = s / float(segments)
                ang = (math.pi * 0.5 - half_angle) + t * (2.0 * half_angle)
                x_in = -r_seg * math.cos(ang)
                z_in = c_seg_z + r_seg * math.sin(ang)
                inner_pts.append((x_in, z_in))
                outer_pts.append((x_in * (1.0 + ring_thick / r_in), z_in + ring_thick))
        elif style == 'HORSESHOE':
            ang_start = -math.radians(16)
            ang_range = math.pi + math.radians(32)
            for s in range(segments + 1):
                t = s / float(segments)
                ang = ang_start + t * ang_range
                x_in = -r_in * math.cos(ang)
                z_in = spring_z + r_in * math.sin(ang)
                inner_pts.append((x_in, z_in))
                x_out = -r_out * math.cos(ang)
                z_out = spring_z + r_out * math.sin(ang)
                outer_pts.append((x_out, z_out))
        else: # ROMAN_ROUND
            for s in range(segments + 1):
                t = s / float(segments)
                ang = t * math.pi
                x_in = -r_in * math.cos(ang)
                z_in = spring_z + r_in * math.sin(ang)
                inner_pts.append((x_in, z_in))
                x_out = -r_out * math.cos(ang)
                z_out = spring_z + r_out * math.sin(ang)
                outer_pts.append((x_out, z_out))

        n_arc = len(inner_pts)

        # アーチリングの完全ソリッド面張り
        vf_in, vf_out = [], []
        vb_in, vb_out = [], []

        for i in range(n_arc):
            xi, zi = inner_pts[i]
            xo, zo = outer_pts[i]
            # 迫石（Voussoir）ごとの微小な厚みジッター（石材ブロック感）
            v_jitter = rng.uniform(-0.005, 0.005) * damage if damage > 0.05 else 0.0
            cur_step = m_step + v_jitter

            vfi = bm.verts.new((cx + xi, half_d, zi))
            vfo = bm.verts.new((cx + xo, half_d + cur_step, zo))
            vbi = bm.verts.new((cx + xi, -half_d, zi))
            vbo = bm.verts.new((cx + xo, -half_d - cur_step, zo))

            if damage > 0.05:
                c_noise = damage * 0.010
                vfo.co.z += rng.uniform(-c_noise, c_noise)
                vbo.co.z += rng.uniform(-c_noise, c_noise)

            vf_in.append(vfi)
            vf_out.append(vfo)
            vb_in.append(vbi)
            vb_out.append(vbo)

        bm.verts.ensure_lookup_table()

        for i in range(n_arc - 1):
            # 1. 前面リング
            bm.faces.new((vf_in[i], vf_out[i], vf_out[i+1], vf_in[i+1]))
            # 2. 背面リング
            bm.faces.new((vb_in[i+1], vb_out[i+1], vb_out[i], vb_in[i]))
            # 3. 内周天井 (Soffit)
            bm.faces.new((vf_in[i+1], vb_in[i+1], vb_in[i], vf_in[i]))
            # 4. 外周上面 (Outer Rim)
            bm.faces.new((vf_out[i], vf_out[i+1], vb_out[i+1], vb_out[i]))

        # ── ★ 隙間ゼロ・完全ポリゴン密閉スパンドレル壁 ──
        if has_spandrel:
            # 1. アーチ外周の各点 (xo, zo) から天面 (wall_top_z) までの垂直クアッドストリップ
            vf_top = []
            vb_top = []
            for i in range(n_arc):
                xo, _ = outer_pts[i]
                vf_top.append(bm.verts.new((cx + xo, half_d, wall_top_z)))
                vb_top.append(bm.verts.new((cx + xo, -half_d, wall_top_z)))

            bm.verts.ensure_lookup_table()

            # 前面・背面・天面の面張り（三角形の穴を完全に無くす）
            for i in range(n_arc - 1):
                # 前面スパンドレル面
                bm.faces.new((vf_out[i], vf_top[i], vf_top[i+1], vf_out[i+1]))
                # 背面スパンドレル面
                bm.faces.new((vb_out[i+1], vb_top[i+1], vb_top[i], vb_out[i]))
                # 天板上面
                bm.faces.new((vf_top[i], vf_top[i+1], vb_top[i+1], vb_top[i]))

            # 2. 左側柱の上の壁ブロック (cx - span_w*0.5 〜 cx + outer_pts[0][0])
            left_w = (cx + outer_pts[0][0]) - (cx - span_w * 0.5)
            if left_w > 0.001:
                add_box(
                    (cx - span_w * 0.5 + left_w * 0.5, 0.0, (spring_z + wall_top_z) * 0.5),
                    (left_w, depth, wall_top_z - spring_z)
                )

            # 3. 右側柱の上の壁ブロック (cx + outer_pts[-1][0] 〜 cx + span_w*0.5)
            right_w = (cx + span_w * 0.5) - (cx + outer_pts[-1][0])
            if right_w > 0.001:
                add_box(
                    (cx + span_w * 0.5 - right_w * 0.5, 0.0, (spring_z + wall_top_z) * 0.5),
                    (right_w, depth, wall_top_z - spring_z)
                )

        # 要石（Keystone）
        if has_keystone:
            mid = n_arc // 2
            k_in_z = inner_pts[mid][1]
            k_out_z = outer_pts[mid][1]
            k_top_z = min(wall_top_z, k_out_z + ring_thick * 0.28 * keystone_scale)
            k_bot_z = k_in_z - ring_thick * 0.08
            k_h = k_top_z - k_bot_z
            k_w = ring_thick * 0.85 * keystone_scale
            add_box((cx, 0.0, (k_top_z + k_bot_z) * 0.5), (k_w, depth + m_step * 2.8, k_h))

    # ── C. 連続コーニス天板 ──
    if has_spandrel:
        c_cz = wall_top_z + cornice_h * 0.5
        c_w = total_w + 0.12
        add_box((0.0, 0.0, c_cz - cornice_h * 0.2), (c_w, depth + 0.08, cornice_h * 0.6))
        add_box((0.0, 0.0, c_cz + cornice_h * 0.25), (c_w + 0.14, depth + 0.18, cornice_h * 0.5))

    bm.verts.ensure_lookup_table()
    bm.normal_update()
    for f in bm.faces:
        f.smooth = False

    return bm.verts[:]


def build_beam_arch_base(bm, size_x, size_y, size_z, **kwargs):
    """Backward compatibility wrapper redirecting to the new procedural stone arch."""
    return build_procedural_stone_arch_bmesh(
        bm,
        size_x=size_x,
        size_y=size_y,
        size_z=size_z,
        **kwargs
    )


def build_modular_relief_wall_mesh(
    bm,
    size_x=3.0,
    size_y=0.4,
    size_z=3.5,
    bays=1,
    relief_style='ROSETTE',
    relief_depth=0.035,
    pilaster_width=0.40,
    pilaster_depth=0.08,
    frame_bevel=0.12,
    damage=0.35,
    weathering=0.50,
    moss_amount=0.30,
    custom_image="",
    seed=0,
    **kwargs
):
    """
    Builds an architecturally authentic classical Modular Relief Wall:
    - Modular seamless tiling: Halved pilasters at boundary ends merge seamlessly into full pilasters when snap-placed side-by-side.
    - Multi-bay array support (1 to 10 bays) with unified horizontal cornice, plinth, and rhythmic bays.
    - Flat, gapless boundary snapping surfaces (X = ±TotalWidth/2) with zero seam gaps.
    - True 3D relief carvings:
        * ROSETTE: Concentric molded medallion rings with quatrefoil/octofoil floral ribs and central boss.
        * FRIEZE: Classical continuous Greek Key / Meander geometric fretwork band.
        * RUNIC: Authentic deep-chiseled sacred elder futhark rune glyphs and ceremonial geometric channels.
        * CUSTOM: Subdivided planar panel ready for procedural / image displacement.
    - Classical architectural anatomy: Heavy plinth base (moss accumulation), fluted pilasters, tiered architrave frame, and projecting cornice.
    - Selective procedural damage chipping on exposed outer edges while strictly protecting boundary snap faces.
    """
    import mathutils
    import random

    rng = random.Random(seed)

    spans = max(1, int(bays))
    span_w = max(1.0, float(size_x))
    total_w = span_w * spans
    depth = max(0.15, float(size_y))
    height = max(1.0, float(size_z))
    half_d = depth * 0.5
    half_total_w = total_w * 0.5

    # 1. 建築プロポーションの計算
    p_w = max(0.15, min(pilaster_width, span_w * 0.35))
    p_proj = max(0.02, min(pilaster_depth, depth * 0.5))
    r_depth = max(0.008, min(relief_depth, depth * 0.4))
    f_bevel = max(0.04, min(frame_bevel, (span_w - p_w) * 0.25))

    plinth_h = height * 0.12      # 下部台座の高さ
    cornice_h = height * 0.09     # 上部コーニス天板の高さ
    attic_h = height * 0.04       # コーニス直下のフリーズ小帯
    field_h = height - plinth_h - cornice_h - attic_h # レリーフパネルの有効高さ
    field_z_min = plinth_h
    field_z_max = plinth_h + field_h
    field_cz = (field_z_min + field_z_max) * 0.5

    # 境界保護チッピング付きボックス追加ヘルパー
    def add_box(center, size, chip=True):
        hw = size[0] * 0.5
        hd = size[1] * 0.5
        hh = size[2] * 0.5
        cx, cy, cz = center

        v_res = bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=mathutils.Matrix.Translation((cx, cy, cz)) @ mathutils.Matrix.Diagonal((size[0], size[1], size[2], 1.0))
        )['verts']

        if damage > 0.05 and chip:
            noise_amt = damage * 0.012
            for v in v_res:
                # 左右のモジュラー接合境界（X = ±half_total_w）に接する頂点は絶対にX移動させない（スナップ保護）
                is_boundary_x = abs(abs(v.co.x) - half_total_w) < 1e-4
                if not is_boundary_x:
                    v.co.x += rng.uniform(-noise_amt, noise_amt)
                
                # 背面（Y < 0）の壁貼り合わせ面も保護
                is_back_y = abs(v.co.y - (-half_d)) < 1e-4
                if not is_back_y:
                    v.co.y += rng.uniform(-noise_amt, noise_amt)
                
                # 底面（Z = 0）も地面スナップのため保護
                if v.co.z > 0.01:
                    v.co.z += rng.uniform(-noise_amt, noise_amt)
        return v_res

    # ── 1. 主壁コア（バックウォール） ──
    # 全スパンを貫通する堅牢な石壁本体
    add_box((0.0, 0.0, height * 0.5), (total_w, depth, height), chip=True)

    # ── 2. 下部台座（Plinth / Dado） ──
    # 地面に接する重厚な土台（前面に突出）
    add_box(
        (0.0, p_proj * 0.6, plinth_h * 0.45),
        (total_w, depth + p_proj * 1.2, plinth_h * 0.9),
        chip=True
    )
    # 台座上部の面取りモールディング小段
    add_box(
        (0.0, p_proj * 0.4, plinth_h - plinth_h * 0.1),
        (total_w, depth + p_proj * 0.8, plinth_h * 0.2),
        chip=True
    )

    # ── 3. 上部コーニス＆アティック天板（Cornice & Entablature） ──
    c_base_z = field_z_max
    # アティック小帯
    add_box(
        (0.0, p_proj * 0.3, c_base_z + attic_h * 0.5),
        (total_w, depth + p_proj * 0.6, attic_h),
        chip=True
    )
    # コーニス下段モールディング
    c1_h = cornice_h * 0.4
    add_box(
        (0.0, p_proj * 0.7, c_base_z + attic_h + c1_h * 0.5),
        (total_w, depth + p_proj * 1.4, c1_h),
        chip=True
    )
    # コーニス上段天板（最も前にせり出し、雨垂れの起点となる）
    c2_h = cornice_h * 0.6
    add_box(
        (0.0, p_proj * 1.0, c_base_z + attic_h + c1_h + c2_h * 0.5),
        (total_w, depth + p_proj * 2.0, c2_h),
        chip=True
    )

    # ── 4. ピラスター（付け柱） ──
    # 各スパン境界（0 〜 spans）に配置。端点は半幅にしてモジュラー結合時に合体する設計。
    for p_idx in range(spans + 1):
        is_left_end = (p_idx == 0)
        is_right_end = (p_idx == spans)

        if is_left_end:
            cur_pw = p_w * 0.5
            px = -half_total_w + cur_pw * 0.5
        elif is_right_end:
            cur_pw = p_w * 0.5
            px = half_total_w - cur_pw * 0.5
        else:
            cur_pw = p_w
            px = -half_total_w + p_idx * span_w

        p_cz = (field_z_min + field_z_max) * 0.5
        p_front_y = half_d + p_proj * 0.5

        # 柱脚ベース (Pilaster Base)
        pb_h = field_h * 0.08
        add_box(
            (px, half_d + p_proj * 0.6, field_z_min + pb_h * 0.5),
            (cur_pw, p_proj * 1.2, pb_h),
            chip=True
        )

        # 柱頭キャピタル (Pilaster Capital)
        pc_h = field_h * 0.09
        add_box(
            (px, half_d + p_proj * 0.65, field_z_max - pc_h * 0.5),
            (cur_pw, p_proj * 1.3, pc_h),
            chip=True
        )

        # 柱身シャフト (Pilaster Shaft)
        ps_h = field_h - pb_h - pc_h
        ps_cz = field_z_min + pb_h + ps_h * 0.5
        add_box(
            (px, half_d + p_proj * 0.5, ps_cz),
            (cur_pw, p_proj, ps_h),
            chip=True
        )

        # 柱身のフルート装飾（中央柱身の縦リブ）
        if not is_left_end and not is_right_end and cur_pw > 0.25:
            # 2本のフルートスリットリブ
            flute_w = cur_pw * 0.22
            flute_proj = p_proj * 0.35
            add_box((px - cur_pw * 0.25, half_d + p_proj + flute_proj * 0.5, ps_cz), (flute_w, flute_proj, ps_h * 0.88), chip=False)
            add_box((px + cur_pw * 0.25, half_d + p_proj + flute_proj * 0.5, ps_cz), (flute_w, flute_proj, ps_h * 0.88), chip=False)

    # ── 5. 各ベイの中央額縁フレーム＆レリーフ彫刻 ──
    for ispan in range(spans):
        cx = -half_total_w + (ispan + 0.5) * span_w
        panel_w = span_w - p_w  # ピラスター間の正味幅
        panel_h = field_h

        # 額縁モールディング枠（四方を囲む立体ステップフレーム）
        # 下枠
        add_box((cx, half_d + p_proj * 0.35, field_z_min + f_bevel * 0.5), (panel_w, p_proj * 0.7, f_bevel), chip=True)
        # 上枠
        add_box((cx, half_d + p_proj * 0.35, field_z_max - f_bevel * 0.5), (panel_w, p_proj * 0.7, f_bevel), chip=True)
        # 左右枠
        side_frame_h = panel_h - f_bevel * 2.0
        add_box((cx - panel_w * 0.5 + f_bevel * 0.5, half_d + p_proj * 0.35, field_cz), (f_bevel, p_proj * 0.7, side_frame_h), chip=True)
        add_box((cx + panel_w * 0.5 - f_bevel * 0.5, half_d + p_proj * 0.35, field_cz), (f_bevel, p_proj * 0.7, side_frame_h), chip=True)

        # 彫刻有効領域
        inner_w = panel_w - f_bevel * 2.0
        inner_h = panel_h - f_bevel * 2.0
        r_y = half_d + r_depth * 0.5

        if relief_style == 'ROSETTE':
            # ── 🌹 ゴシック・円形薔薇ロゼット彫刻 ──
            # 外径・内径
            r_max = min(inner_w, inner_h) * 0.42
            r_mid = r_max * 0.72
            r_inner = r_max * 0.35

            # 1. 外円形モールディングリング (16角形リング)
            n_seg = 20
            ring_th = r_max * 0.12
            for s in range(n_seg):
                ang1 = (s / n_seg) * 2.0 * math.pi
                ang2 = ((s + 1) / n_seg) * 2.0 * math.pi
                mid_ang = (ang1 + ang2) * 0.5
                rx = cx + math.cos(mid_ang) * (r_max - ring_th * 0.5)
                rz = field_cz + math.sin(mid_ang) * (r_max - ring_th * 0.5)
                seg_len = 2.0 * math.sin(math.pi / n_seg) * r_max
                # 各セグメントボックス
                res = bmesh.ops.create_cube(
                    bm, size=1.0,
                    matrix=mathutils.Matrix.Translation((rx, r_y, rz)) @
                           mathutils.Matrix.Rotation(mid_ang + math.pi*0.5, 4, 'Y') @
                           mathutils.Matrix.Diagonal((seg_len * 1.05, r_depth, ring_th, 1.0))
                )

            # 2. 四つ葉 / 八つ葉飾り (Quatrefoil / Octofoil Ribs)
            # 8方向に花弁状の立体リブを放射
            n_petals = 8
            for p in range(n_petals):
                ang = (p / n_petals) * 2.0 * math.pi
                petal_len = r_mid - r_inner * 0.5
                petal_cx = cx + math.cos(ang) * (r_inner + petal_len * 0.5)
                petal_cz = field_cz + math.sin(ang) * (r_inner + petal_len * 0.5)
                w_petal = r_max * 0.16
                bmesh.ops.create_cube(
                    bm, size=1.0,
                    matrix=mathutils.Matrix.Translation((petal_cx, r_y + r_depth * 0.2, petal_cz)) @
                           mathutils.Matrix.Rotation(ang, 4, 'Y') @
                           mathutils.Matrix.Diagonal((petal_len, r_depth * 1.4, w_petal, 1.0))
                )

            # 3. 内円リング
            for s in range(12):
                ang1 = (s / 12) * 2.0 * math.pi
                ang2 = ((s + 1) / 12) * 2.0 * math.pi
                mid_ang = (ang1 + ang2) * 0.5
                rx = cx + math.cos(mid_ang) * r_inner
                rz = field_cz + math.sin(mid_ang) * r_inner
                seg_len = 2.0 * math.sin(math.pi / 12) * r_inner
                bmesh.ops.create_cube(
                    bm, size=1.0,
                    matrix=mathutils.Matrix.Translation((rx, r_y + r_depth * 0.3, rz)) @
                           mathutils.Matrix.Rotation(mid_ang + math.pi*0.5, 4, 'Y') @
                           mathutils.Matrix.Diagonal((seg_len * 1.05, r_depth * 1.6, r_inner * 0.2, 1.0))
                )

            # 4. 中央ボス（円形突起）
            add_box((cx, r_y + r_depth * 0.6, field_cz), (r_inner * 0.6, r_depth * 2.2, r_inner * 0.6), chip=False)

        elif relief_style == 'FRIEZE':
            # ── 🏛️ 古代神殿・雷文フリーズ彫刻 ──
            # ギリシャ雷文（Greek Key / Meander）の立体幾何リブを上下3段に配置
            n_frieze_rows = 3
            row_spacing = inner_h / (n_frieze_rows + 1)
            frieze_th = min(0.045, inner_w * 0.04)

            for row in range(n_frieze_rows):
                row_z = field_z_min + f_bevel + (row + 1) * row_spacing
                # 雷文ユニットの幅
                unit_w = inner_w / 4.0
                unit_h = row_spacing * 0.7
                for u in range(4):
                    ux = cx - inner_w * 0.5 + (u + 0.5) * unit_w
                    # メアンダーの折り返しリブ（外周枠 + 内部スパイラル）
                    # 上辺
                    add_box((ux, r_y, row_z + unit_h * 0.4), (unit_w * 0.9, r_depth, frieze_th), chip=False)
                    # 下辺
                    add_box((ux, r_y, row_z - unit_h * 0.4), (unit_w * 0.9, r_depth, frieze_th), chip=False)
                    # 右外縦
                    add_box((ux + unit_w * 0.45 - frieze_th * 0.5, r_y, row_z), (frieze_th, r_depth, unit_h * 0.8), chip=False)
                    # 左折り返し縦
                    add_box((ux - unit_w * 0.45 + frieze_th * 0.5, r_y, row_z + unit_h * 0.1), (frieze_th, r_depth, unit_h * 0.6), chip=False)
                    # 中心のフック横
                    add_box((ux - unit_w * 0.1, r_y, row_z), (unit_w * 0.5, r_depth, frieze_th), chip=False)

        elif relief_style == 'RUNIC':
            # ── ᚱ 古代ルーン・神聖グリフ石刻 ──
            # 深く彫り込まれたルーン文字（主柱幹 + 幾何学斜め枝）
            glyph_cols = 3
            glyph_rows = 2
            dx = inner_w / (glyph_cols + 1)
            dz = inner_h / (glyph_rows + 1)
            groove_w = min(0.035, inner_w * 0.03)

            rune_types = ['FEHU', 'ALGIZ', 'TIWAZ', 'THURISAZ', 'SOWILO', 'ANSUZ']
            r_idx = 0

            for gr in range(glyph_rows):
                for gc in range(glyph_cols):
                    gx = cx - inner_w * 0.5 + (gc + 1) * dx
                    gz = field_z_min + f_bevel + (gr + 1) * dz
                    g_h = dz * 0.65
                    rtype = rune_types[r_idx % len(rune_types)]
                    r_idx += 1

                    # 1. 垂直主幹（すべてのルーンの基本軸）
                    add_box((gx, r_y + r_depth * 0.1, gz), (groove_w, r_depth * 1.5, g_h), chip=False)

                    # 2. ルーンごとの斜め枝・幾何学リブ
                    if rtype == 'FEHU': # ᚠ 上向き2本斜め枝
                        bmesh.ops.create_cube(
                            bm, size=1.0,
                            matrix=mathutils.Matrix.Translation((gx + g_h * 0.22, r_y + r_depth * 0.1, gz + g_h * 0.28)) @
                                   mathutils.Matrix.Rotation(math.radians(35), 4, 'Y') @
                                   mathutils.Matrix.Diagonal((g_h * 0.5, r_depth * 1.5, groove_w, 1.0))
                        )
                        bmesh.ops.create_cube(
                            bm, size=1.0,
                            matrix=mathutils.Matrix.Translation((gx + g_h * 0.20, r_y + r_depth * 0.1, gz - g_h * 0.02)) @
                                   mathutils.Matrix.Rotation(math.radians(35), 4, 'Y') @
                                   mathutils.Matrix.Diagonal((g_h * 0.45, r_depth * 1.5, groove_w, 1.0))
                        )
                    elif rtype == 'ALGIZ': # ᛉ 鹿の角状の左右斜め枝
                        bmesh.ops.create_cube(
                            bm, size=1.0,
                            matrix=mathutils.Matrix.Translation((gx - g_h * 0.20, r_y + r_depth * 0.1, gz + g_h * 0.25)) @
                                   mathutils.Matrix.Rotation(math.radians(-45), 4, 'Y') @
                                   mathutils.Matrix.Diagonal((g_h * 0.5, r_depth * 1.5, groove_w, 1.0))
                        )
                        bmesh.ops.create_cube(
                            bm, size=1.0,
                            matrix=mathutils.Matrix.Translation((gx + g_h * 0.20, r_y + r_depth * 0.1, gz + g_h * 0.25)) @
                                   mathutils.Matrix.Rotation(math.radians(45), 4, 'Y') @
                                   mathutils.Matrix.Diagonal((g_h * 0.5, r_depth * 1.5, groove_w, 1.0))
                        )
                    elif rtype == 'TIWAZ': # ᛏ 矢印型上部枝
                        bmesh.ops.create_cube(
                            bm, size=1.0,
                            matrix=mathutils.Matrix.Translation((gx - g_h * 0.18, r_y + r_depth * 0.1, gz + g_h * 0.38)) @
                                   mathutils.Matrix.Rotation(math.radians(-35), 4, 'Y') @
                                   mathutils.Matrix.Diagonal((g_h * 0.4, r_depth * 1.5, groove_w, 1.0))
                        )
                        bmesh.ops.create_cube(
                            bm, size=1.0,
                            matrix=mathutils.Matrix.Translation((gx + g_h * 0.18, r_y + r_depth * 0.1, gz + g_h * 0.38)) @
                                   mathutils.Matrix.Rotation(math.radians(35), 4, 'Y') @
                                   mathutils.Matrix.Diagonal((g_h * 0.4, r_depth * 1.5, groove_w, 1.0))
                        )
                    elif rtype == 'THURISAZ': # ᚦ 棘型三角
                        bmesh.ops.create_cube(
                            bm, size=1.0,
                            matrix=mathutils.Matrix.Translation((gx + g_h * 0.18, r_y + r_depth * 0.1, gz + g_h * 0.12)) @
                                   mathutils.Matrix.Rotation(math.radians(40), 4, 'Y') @
                                   mathutils.Matrix.Diagonal((g_h * 0.38, r_depth * 1.5, groove_w, 1.0))
                        )
                        bmesh.ops.create_cube(
                            bm, size=1.0,
                            matrix=mathutils.Matrix.Translation((gx + g_h * 0.18, r_y + r_depth * 0.1, gz - g_h * 0.12)) @
                                   mathutils.Matrix.Rotation(math.radians(-40), 4, 'Y') @
                                   mathutils.Matrix.Diagonal((g_h * 0.38, r_depth * 1.5, groove_w, 1.0))
                        )
                    elif rtype == 'SOWILO': # ᛋ 稲妻型ジグザグ
                        bmesh.ops.create_cube(
                            bm, size=1.0,
                            matrix=mathutils.Matrix.Translation((gx, r_y + r_depth * 0.1, gz)) @
                                   mathutils.Matrix.Rotation(math.radians(-50), 4, 'Y') @
                                   mathutils.Matrix.Diagonal((g_h * 0.65, r_depth * 1.5, groove_w, 1.0))
                        )

        else: # CUSTOM
            # ── 🖼️ カスタム画像ハイトマップ彫刻パネル ──
            # 中央パネルを密閉ボックスとして配置
            add_box((cx, r_y, field_cz), (inner_w * 0.96, r_depth * 1.2, inner_h * 0.96), chip=False)

    bm.verts.ensure_lookup_table()
    bm.normal_update()
    for f in bm.faces:
        f.smooth = False

    return bm.verts[:]


def build_western_window_mesh(
    bm,
    size_x=1.6,
    size_y=0.35,
    size_z=2.5,
    frame_style='ROMAN_ROUND',
    grille_style='SUNBURST',
    arch_style='MOLDED_FRENCH',
    jamb_style='ENGAGED_FLUTED',
    column_flutes=8,
    column_pedestal=True,
    has_keystone=True,
    wire_density=6,
    wire_thickness=0.012,
    frame_width=0.18,
    has_sill=True,
    has_hood=True,
    damage=0.15,
    seed=0,
    **kwargs
):
    """
    Builds a stylish, architecturally authentic Western Classical / French / Gothic Window.
    - True solid spandrel wall without stepped slices or bumpy artifacts.
    - True radial voussoirs & keystone OR smooth French concentric molded archivolts.
    - Sunburst Fanlight grille (radiating spokes & concentric semicircular arc) for stylish mansions.
    - Sharp, crisp architectural stone blocks with restrained micro-chisel displacement.
    """
    import mathutils
    import random
    import math

    rng = random.Random(seed)

    total_w = max(0.8, float(size_x))
    depth = max(0.15, float(size_y))
    total_h = max(1.2, float(size_z))
    f_w = max(0.08, min(frame_width, total_w * 0.28))
    half_w = total_w * 0.5
    half_d = depth * 0.5
    inner_w = total_w - f_w * 2.0
    r_in = inner_w * 0.5

    sill_h = total_h * 0.08 if has_sill else 0.0
    sill_proj = depth * 0.35

    # 1. 開口部とスプリングラインの幾何学計算
    if frame_style == 'RECTANGLE':
        spring_z = total_h - f_w
        arch_rise = 0.0
        opening_h = spring_z - sill_h
    elif frame_style == 'ROMAN_ROUND':
        arch_rise = r_in
        spring_z = max(sill_h + 0.4, total_h - f_w - arch_rise)
        opening_h = total_h - f_w - sill_h
    elif frame_style == 'TUDOR':
        arch_rise = r_in * 0.55
        spring_z = max(sill_h + 0.4, total_h - f_w - arch_rise)
        opening_h = total_h - f_w - sill_h
    else: # GOTHIC_POINTED
        arch_rise = r_in * 1.35
        spring_z = max(sill_h + 0.4, total_h - f_w - arch_rise)
        opening_h = total_h - f_w - sill_h

    def add_box(center, size, mat_idx=0, chip=True, subdiv=0):
        """直方体ブロックを生成し、マテリアルを割り当て"""
        cx, cy, cz = center
        sx, sy, sz = size
        res = bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=mathutils.Matrix.Translation((cx, cy, cz)) @ mathutils.Matrix.Diagonal((sx, sy, sz, 1.0))
        )
        v_res = res['verts']

        if subdiv > 0:
            edges_to_sub = [e for e in bm.edges if all(v in v_res for v in e.verts)]
            if edges_to_sub:
                sub_res = bmesh.ops.subdivide_edges(bm, edges=edges_to_sub, cuts=subdiv, use_grid_fill=True)
                new_verts = [g for g in sub_res.get('geom_inner', []) if isinstance(g, bmesh.types.BMVert)]
                v_res = list(set(v_res + new_verts))

        for f in bm.faces:
            if any(v in v_res for v in f.verts):
                f.material_index = mat_idx

        return v_res

    # ── アーチ高さ関数 ──
    def get_arch_z(x):
        """任意X座標におけるアーチ開口部の上端Z高さを返す"""
        x_c = max(-r_in, min(r_in, x))
        if frame_style == 'RECTANGLE':
            return spring_z
        elif frame_style == 'GOTHIC_POINTED':
            d_c = r_in * 0.42
            R = r_in + d_c
            if x_c <= 0:
                rad_sq = max(0.0, R**2 - (x_c - d_c)**2)
            else:
                rad_sq = max(0.0, R**2 - (x_c + d_c)**2)
            return spring_z + math.sqrt(rad_sq)
        elif frame_style == 'TUDOR':
            t = math.sqrt(max(0.0, 1.0 - (x_c / r_in)**2))
            return spring_z + arch_rise * t
        else: # ROMAN_ROUND
            rad_sq = max(0.0, r_in**2 - x_c**2)
            return spring_z + math.sqrt(rad_sq)

    # ── A. 外枠（石造フレーム / 窓台 / 上部コーニス） [mat_idx = 0] ──
    # 1. 窓台 (Window Sill) - 重厚でシャープな2段水切り台座
    if has_sill:
        # 下段の台座（Plinth Base）
        add_box(
            (0.0, sill_proj * 0.35, sill_h * 0.35),
            (total_w + 0.14, depth + sill_proj * 0.7, sill_h * 0.7),
            mat_idx=0, chip=False, subdiv=1
        )
        # 上段の水切り天板（Sill Nose）
        add_box(
            (0.0, sill_proj * 0.45, sill_h * 0.85),
            (total_w + 0.10, depth + sill_proj, sill_h * 0.3),
            mat_idx=0, chip=False, subdiv=1
        )

    # 2. 左右の縦枠・支柱 (Jambs & Columns)
    jamb_h = spring_z - sill_h
    lx_c = -half_w + f_w * 0.5
    rx_c = half_w - f_w * 0.5

    if jamb_style == 'ENGAGED_FLUTED':
        # 🏛️ 附設古典円柱 (Engaged Classical Fluted Column)
        # カミワダ テル氏動画（0:20-1:30）準拠：U字フルート溝 + ベベルハイライト + アティックベース + クラシカル柱頭
        col_r = f_w * 0.52
        col_cy = half_d * 0.85 # 壁の前面近くを中心として、半円柱が前方に堂々と突出

        # A. 台座（Pedestal / Plinth Base）
        if column_pedestal:
            ped_h = min(0.32, jamb_h * 0.16)
            ped_w = f_w * 1.18
            ped_d = depth * 0.80
            for cx in (lx_c, rx_c):
                # 壁から前方にせり出す台座
                add_box((cx, col_cy - ped_d * 0.35, sill_h + ped_h * 0.25), (ped_w, ped_d, ped_h * 0.5), mat_idx=0, chip=False, subdiv=1)
                add_box((cx, col_cy - ped_d * 0.35, sill_h + ped_h * 0.65), (ped_w * 0.90, ped_d * 0.90, ped_h * 0.3), mat_idx=0, chip=False, subdiv=1)
                add_box((cx, col_cy - ped_d * 0.35, sill_h + ped_h * 0.90), (ped_w * 1.05, ped_d * 1.05, ped_h * 0.2), mat_idx=0, chip=False, subdiv=1)
                # 正面の額縁彫り込みパネル段差
                add_box((cx, col_cy + ped_d * 0.15 + 0.01, sill_h + ped_h * 0.5), (ped_w * 0.65, 0.02, ped_h * 0.45), mat_idx=0, chip=False, subdiv=1)
            base_z = sill_h + ped_h
        else:
            base_z = sill_h

        # B. 柱頭インポスト（Capital & Impost）
        cap_h = min(0.14, jamb_h * 0.11)
        shaft_end_z = spring_z - cap_h

        # C. アティックベース & 柱頭天板
        attic_h = 0.05
        for cx in (lx_c, rx_c):
            # 四角形ベースプレート
            add_box((cx, col_cy - 0.02, base_z + 0.015), (col_r * 2.3, col_r * 1.8, 0.03), mat_idx=0, chip=False, subdiv=1)
            # 2段トーラスリング（円錐台座）
            res_t1 = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=24,
                radius1=col_r * 1.25, radius2=col_r * 1.15, depth=0.018,
                matrix=mathutils.Matrix.Translation((cx, col_cy, base_z + 0.038))
            )
            for f in res_t1.get('faces', []): 
                f.material_index = 0
                f.smooth = True
            res_t2 = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=24,
                radius1=col_r * 1.12, radius2=col_r * 1.02, depth=0.012,
                matrix=mathutils.Matrix.Translation((cx, col_cy, base_z + 0.052))
            )
            for f in res_t2.get('faces', []): 
                f.material_index = 0
                f.smooth = True

            # 柱身後方の壁面ソリッドバック（奥側のみを埋めて円柱前面を邪魔しない）
            back_d = depth * 0.60
            add_box((cx, -half_d + back_d * 0.5, sill_h + jamb_h * 0.5), (f_w * 0.98, back_d, jamb_h), mat_idx=0, chip=False, subdiv=1)

            # 柱頭（Capital: アストラガル首輪 + エキヌス曲面 + 多段アバクス天板）
            res_ast = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=24,
                radius1=col_r * 1.08, radius2=col_r * 1.02, depth=0.016,
                matrix=mathutils.Matrix.Translation((cx, col_cy, shaft_end_z + 0.01))
            )
            for f in res_ast.get('faces', []): 
                f.material_index = 0
                f.smooth = True
            res_ech = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=24,
                radius1=col_r * 1.00, radius2=col_r * 1.35, depth=cap_h * 0.45,
                matrix=mathutils.Matrix.Translation((cx, col_cy, shaft_end_z + cap_h * 0.35))
            )
            for f in res_ech.get('faces', []): 
                f.material_index = 0
                f.smooth = True
            # 多段アバクス天板（スプリングライン直下でアーチを受ける）
            add_box((cx, col_cy - 0.02, spring_z - cap_h * 0.25), (f_w * 1.20, f_w * 1.20, cap_h * 0.25), mat_idx=0, chip=False, subdiv=1)
            add_box((cx, col_cy - 0.02, spring_z - cap_h * 0.06), (f_w * 1.32, f_w * 1.32, cap_h * 0.14), mat_idx=0, chip=False, subdiv=1)

        shaft_start_z = base_z + attic_h

        # D. 左右のU字フルート柱身（Fluted Shaft with Bevel）
        def build_fluted_engaged_shaft(cx):
            h_s = shaft_end_z - shaft_start_z
            if h_s <= 0.05:
                return
            n_fl = max(4, min(14, column_flutes))
            # 正面半円（0度から180度）
            ang_start = 0.0
            ang_end = math.pi
            tot_ang = ang_end - ang_start
            ang_step = tot_ang / float(n_fl)
            fl_depth = (tot_ang * col_r / float(n_fl)) * 0.52

            prof = []
            for fi in range(n_fl):
                a0 = ang_start + fi * ang_step
                prof.append((math.cos(a0) * col_r, math.sin(a0) * col_r))
                t1 = a0 + ang_step * 0.22
                t2 = a0 + ang_step * 0.50
                t3 = a0 + ang_step * 0.78
                r_sh = col_r - fl_depth * 0.40
                r_bt = col_r - fl_depth
                prof.append((math.cos(t1) * r_sh, math.sin(t1) * r_sh))
                prof.append((math.cos(t2) * r_bt, math.sin(t2) * r_bt))
                prof.append((math.cos(t3) * r_sh, math.sin(t3) * r_sh))
            prof.append((math.cos(ang_end) * col_r, math.sin(ang_end) * col_r))
            
            # 壁面への閉鎖アンカー（Y=0方向へ直角に落とす）
            prof.append((math.cos(ang_end) * col_r, -0.04))
            prof.append((math.cos(ang_start) * col_r, -0.04))

            n_pts = len(prof)
            n_zc = 12
            rings = []
            for zi in range(n_zc + 1):
                zf = zi / float(n_zc)
                zc = shaft_start_z + h_s * zf
                ent = 1.0 + 0.02 * math.sin(math.pi * zf) - 0.04 * (zf ** 1.5)
                r_verts = [bm.verts.new((cx + px * ent, col_cy + py * ent, zc)) for px, py in prof]
                rings.append(r_verts)

            for zi in range(n_zc):
                r0 = rings[zi]
                r1 = rings[zi + 1]
                for pi in range(n_pts):
                    p_next = (pi + 1) % n_pts
                    # 外向き（+Y正面）のワインディング順序
                    f = bm.faces.new([r0[pi], r1[pi], r1[p_next], r0[p_next]])
                    f.material_index = 0
                    f.smooth = True

        build_fluted_engaged_shaft(lx_c)
        build_fluted_engaged_shaft(rx_c)

        # 全メッシュの法線を外向きに統一再計算
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    elif jamb_style == 'PILASTER_PANEL':
        # 🏛️ 額縁彫り込みピラスター (Recessed Inset Panel Pilaster)
        p_thick = 0.045 # 壁からの突出量
        p_front_y = half_d + p_thick

        if column_pedestal:
            ped_h = min(0.32, jamb_h * 0.16)
            for cx in (lx_c, rx_c):
                add_box((cx, p_front_y * 0.5, sill_h + ped_h * 0.25), (f_w * 1.15, depth + p_thick * 1.5, ped_h * 0.5), mat_idx=0, chip=False, subdiv=1)
                add_box((cx, p_front_y * 0.5, sill_h + ped_h * 0.70), (f_w * 0.98, depth + p_thick * 1.2, ped_h * 0.4), mat_idx=0, chip=False, subdiv=1)
                add_box((cx, p_front_y * 0.5, sill_h + ped_h * 0.92), (f_w * 1.10, depth + p_thick * 1.4, ped_h * 0.16), mat_idx=0, chip=False, subdiv=1)
            body_start_z = sill_h + ped_h
        else:
            body_start_z = sill_h

        cap_h = min(0.12, jamb_h * 0.10)
        body_end_z = spring_z - cap_h
        body_h = body_end_z - body_start_z
        body_cz = body_start_z + body_h * 0.5

        for cx in (lx_c, rx_c):
            # 主柱身（壁から突出）
            add_box((cx, p_front_y * 0.5, body_cz), (f_w, depth + p_thick, body_h), mat_idx=0, chip=False, subdiv=1)
            # 正面額縁外枠段差
            add_box((cx, p_front_y + 0.015, body_cz), (f_w * 0.88, 0.03, body_h * 0.96), mat_idx=0, chip=False, subdiv=1)
            # 正面額縁インセット彫り込みパネル（一段奥まったリブ）
            add_box((cx, p_front_y + 0.005, body_cz), (f_w * 0.62, 0.02, body_h * 0.86), mat_idx=0, chip=False, subdiv=1)
            # 柱頭インポストコーニス
            add_box((cx, p_front_y * 0.5, spring_z - cap_h * 0.35), (f_w * 1.18, depth + p_thick * 1.4, cap_h * 0.3), mat_idx=0, chip=False, subdiv=1)
            add_box((cx, p_front_y * 0.5, spring_z - cap_h * 0.10), (f_w * 1.28, depth + p_thick * 1.6, cap_h * 0.2), mat_idx=0, chip=False, subdiv=1)

    else: # ASHLAR_QUOIN
        # 🧱 従来の切石ブロック (Ashlar Quoin Stones)
        n_blocks = max(4, min(8, int(jamb_h / 0.32)))
        block_h = jamb_h / float(n_blocks)
        grout = 0.006

        for bi in range(n_blocks):
            b_cz = sill_h + (bi + 0.5) * block_h
            eff_bh = block_h - grout
            is_long = (bi % 2 == 0)
            w_factor = 1.08 if is_long else 0.96
            cur_fw = f_w * w_factor

            # 左柱
            add_box((lx_c, 0.0, b_cz), (cur_fw, depth, eff_bh), mat_idx=0, chip=False, subdiv=1)
            add_box((lx_c, half_d + 0.015, b_cz), (cur_fw * 0.5, 0.03, eff_bh), mat_idx=0, chip=False, subdiv=1)
            # 右柱
            add_box((rx_c, 0.0, b_cz), (cur_fw, depth, eff_bh), mat_idx=0, chip=False, subdiv=1)
            add_box((rx_c, half_d + 0.015, b_cz), (cur_fw * 0.5, 0.03, eff_bh), mat_idx=0, chip=False, subdiv=1)

        # 柱頭インポスト台座
        imp_h = 0.07
        imp_cz = spring_z - imp_h * 0.5
        add_box((lx_c, half_d * 0.05, imp_cz - 0.01), (f_w * 1.10, depth * 1.05, imp_h * 0.6), mat_idx=0, chip=False, subdiv=1)
        add_box((rx_c, half_d * 0.05, imp_cz - 0.01), (f_w * 1.10, depth * 1.05, imp_h * 0.6), mat_idx=0, chip=False, subdiv=1)
        add_box((lx_c, half_d * 0.08, imp_cz + 0.02), (f_w * 1.22, depth * 1.10, imp_h * 0.4), mat_idx=0, chip=False, subdiv=1)
        add_box((rx_c, half_d * 0.08, imp_cz + 0.02), (f_w * 1.22, depth * 1.10, imp_h * 0.4), mat_idx=0, chip=False, subdiv=1)

    # 開口部側の内枠面取りリブ（Reveal Chamfer）
    in_chamfer_w = f_w * 0.22
    add_box((-r_in - in_chamfer_w * 0.5, half_d * 0.1, sill_h + jamb_h * 0.5), (in_chamfer_w, depth * 0.65, jamb_h), mat_idx=0, chip=False, subdiv=1)
    add_box((r_in + in_chamfer_w * 0.5, half_d * 0.1, sill_h + jamb_h * 0.5), (in_chamfer_w, depth * 0.65, jamb_h), mat_idx=0, chip=False, subdiv=1)

    # 4. 上部コーニス天板 (Top Cornice Beam)
    top_beam_h = max(0.12, f_w)
    add_box((0.0, 0.0, total_h - top_beam_h * 0.5), (total_w, depth, top_beam_h), mat_idx=0, chip=False, subdiv=1)
    if has_hood:
        hood_w = total_w + 0.14
        add_box((0.0, half_d + 0.025, total_h - top_beam_h * 0.5), (hood_w, 0.06, top_beam_h * 1.12), mat_idx=0, chip=False, subdiv=1)

    # 5. 上枠・スパンドレル壁（完全ソリッド平面壁：階段状スライスの完全撤廃）
    top_limit = total_h - top_beam_h
    if frame_style == 'RECTANGLE':
        mid_h = top_limit - spring_z
        if mid_h > 0.01:
            add_box((0.0, 0.0, spring_z + mid_h * 0.5), (total_w, depth, mid_h), mat_idx=0, chip=False, subdiv=1)
    else:
        # アーチ両脇の完全直立壁（左右柱の上部延長）
        side_wall_h = top_limit - spring_z
        side_wall_cz = spring_z + side_wall_h * 0.5
        add_box((-half_w + f_w * 0.5, 0.0, side_wall_cz), (f_w, depth, side_wall_h), mat_idx=0, chip=False, subdiv=1)
        add_box((half_w - f_w * 0.5, 0.0, side_wall_cz), (f_w, depth, side_wall_h), mat_idx=0, chip=False, subdiv=1)

        # 中央上部（アーチ頂点から天板コーニスまで）の矩形壁
        apex_z = get_arch_z(0.0)
        apex_gap = top_limit - apex_z
        if apex_gap > 0.005:
            add_box((0.0, 0.0, apex_z + apex_gap * 0.5), (2.0 * r_in, depth, apex_gap), mat_idx=0, chip=False, subdiv=1)

        # 左右スパンドレル壁面（三角形の隙間を塞ぐ正面・背面ソリッド板）
        n_w_seg = 24
        arch_pts = []
        for i in range(n_w_seg + 1):
            xp = -r_in + (2.0 * r_in) * (i / float(n_w_seg))
            zp = get_arch_z(xp)
            arch_pts.append((xp, zp))

        # 正面壁・背面壁・内周天井面
        vf_list = [bm.verts.new((xp, half_d, zp)) for xp, zp in arch_pts]
        vb_list = [bm.verts.new((xp, -half_d, zp)) for xp, zp in arch_pts]

        # 内周天井面（Intrados）
        for k in range(n_w_seg):
            f_ceil = bm.faces.new([vf_list[k], vf_list[k+1], vb_list[k+1], vb_list[k]])
            f_ceil.material_index = 0

        # 正面・背面の左右肩スパンドレル（アーチ曲線から top_limit への四角形/三角形フィル）
        v_top_f = [bm.verts.new((xp, half_d, apex_z)) for xp, zp in arch_pts]
        v_top_b = [bm.verts.new((xp, -half_d, apex_z)) for xp, zp in arch_pts]
        for k in range(n_w_seg):
            f_sf = bm.faces.new([vf_list[k], vf_list[k+1], v_top_f[k+1], v_top_f[k]])
            f_sf.material_index = 0
            f_sb = bm.faces.new([vb_list[k+1], vb_list[k], v_top_b[k], v_top_b[k+1]])
            f_sb.material_index = 0

        # 6. スタイリッシュ・アーチ額縁（MOLDED_FRENCH vs RADIAL_ASHLAR）
        if arch_style == 'MOLDED_FRENCH':
            # 🏛️ 洋館風多段額縁モールディング（参考画像4, 5準拠：連続Quad Stripによる100%滑らかな同心円面）
            n_m_seg = 32
            tier_w1 = f_w * 0.35 # 第1段幅
            tier_w2 = f_w * 0.30 # 第2段幅
            d_proj1 = 0.030      # 第1段突出厚
            d_proj2 = 0.018      # 第2段突出厚

            # 共通モールディング帯生成関数
            def build_molding_tier(r_start, r_end, y_proj):
                yf_out = half_d + y_proj
                pts_in_f = []
                pts_out_f = []
                pts_in_b = []
                pts_out_b = []

                for i in range(n_m_seg + 1):
                    t = i / float(n_m_seg)
                    ang = math.pi * (1.0 - t)
                    if frame_style == 'GOTHIC_POINTED':
                        # 尖頭アーチの左右円弧
                        xc = -r_in + 2.0 * r_in * t
                        zc = get_arch_z(xc)
                        # 法線方向にオフセット
                        norm_factor = (zc - spring_z) / max(0.01, math.hypot(xc, zc - spring_z))
                        x_in = xc * (r_start / r_in)
                        z_in = spring_z + (zc - spring_z) * (r_start / r_in)
                        x_out = xc * (r_end / r_in)
                        z_out = spring_z + (zc - spring_z) * (r_end / r_in)
                    else:
                        x_in = r_start * math.cos(ang)
                        z_in = spring_z + r_start * math.sin(ang)
                        x_out = r_end * math.cos(ang)
                        z_out = spring_z + r_end * math.sin(ang)

                    v_inf = bm.verts.new((x_in, yf_out, z_in))
                    v_outf = bm.verts.new((x_out, yf_out, z_out))
                    v_inb = bm.verts.new((x_in, half_d, z_in))
                    v_outb = bm.verts.new((x_out, half_d, z_out))

                    pts_in_f.append(v_inf)
                    pts_out_f.append(v_outf)
                    pts_in_b.append(v_inb)
                    pts_out_b.append(v_outb)

                for i in range(n_m_seg):
                    # 前面フェイス
                    f1 = bm.faces.new([pts_in_f[i], pts_out_f[i], pts_out_f[i+1], pts_in_f[i+1]])
                    f1.material_index = 0
                    # 外周エッジフェイス
                    f2 = bm.faces.new([pts_out_f[i], pts_out_b[i], pts_out_b[i+1], pts_out_f[i+1]])
                    f2.material_index = 0
                    # 内周エッジフェイス
                    f3 = bm.faces.new([pts_in_f[i+1], pts_in_b[i+1], pts_in_b[i], pts_in_f[i]])
                    f3.material_index = 0

            # 第1段モールディング
            build_molding_tier(r_in, r_in + tier_w1, d_proj1)
            # 第2段モールディング
            build_molding_tier(r_in + tier_w1, r_in + tier_w1 + tier_w2, d_proj2)

        else: # RADIAL_ASHLAR
            # 🧱 真の放射状迫石＆要石（参考画像3準拠：本物の楔形台形切石ブロック群）
            n_voussoirs = 15 # 奇数個で真上に堂々たる要石
            v_thick = f_w * 0.92
            gap_ang = 0.008 # 迫石同士の目地スリット (Grout Joint)

            for vi in range(n_voussoirs):
                is_keystone = (vi == n_voussoirs // 2)
                k_scale = 1.38 if (is_keystone and has_keystone) else 1.0
                k_proj = 0.045 if (is_keystone and has_keystone) else 0.020

                t_start = vi / float(n_voussoirs)
                t_end = (vi + 1) / float(n_voussoirs)
                ang_start = math.pi * (1.0 - t_start) - gap_ang
                ang_end = math.pi * (1.0 - t_end) + gap_ang

                r1 = r_in
                r2 = r_in + v_thick * k_scale
                yf = half_d + k_proj
                yb = -half_d - k_proj

                # 前面4頂点
                vf1 = bm.verts.new((r1 * math.cos(ang_start), yf, spring_z + r1 * math.sin(ang_start)))
                vf2 = bm.verts.new((r2 * math.cos(ang_start), yf, spring_z + r2 * math.sin(ang_start)))
                vf3 = bm.verts.new((r2 * math.cos(ang_end), yf, spring_z + r2 * math.sin(ang_end)))
                vf4 = bm.verts.new((r1 * math.cos(ang_end), yf, spring_z + r1 * math.sin(ang_end)))

                # 背面4頂点
                vb1 = bm.verts.new((r1 * math.cos(ang_start), yb, spring_z + r1 * math.sin(ang_start)))
                vb2 = bm.verts.new((r2 * math.cos(ang_start), yb, spring_z + r2 * math.sin(ang_start)))
                vb3 = bm.verts.new((r2 * math.cos(ang_end), yb, spring_z + r2 * math.sin(ang_end)))
                vb4 = bm.verts.new((r1 * math.cos(ang_end), yb, spring_z + r1 * math.sin(ang_end)))

                # 6面を生成
                f_front = bm.faces.new([vf1, vf2, vf3, vf4])
                f_back = bm.faces.new([vb4, vb3, vb2, vb1])
                f_top = bm.faces.new([vf2, vb2, vb3, vf3])
                f_bot = bm.faces.new([vf4, vb4, vb1, vf1])
                f_left = bm.faces.new([vf1, vb1, vb2, vf2])
                f_right = bm.faces.new([vf3, vb3, vb4, vf4])

                for f in (f_front, f_back, f_top, f_bot, f_left, f_right):
                    f.material_index = 0

    # ── B. 透過ガラス板 (Glass Pane) [mat_idx = 1] ──
    glass_th = 0.008
    n_g_samples = 32
    g_pts_2d = []
    g_pts_2d.append((-r_in * 0.99, sill_h))
    g_pts_2d.append((r_in * 0.99, sill_h))
    for i in range(n_g_samples, -1, -1):
        x = -r_in * 0.99 + (2.0 * r_in * 0.99) * (i / float(n_g_samples))
        z = get_arch_z(x) - 0.004
        g_pts_2d.append((x, z))

    v_front = [bm.verts.new((x, glass_th * 0.5, z)) for x, z in g_pts_2d]
    v_back = [bm.verts.new((x, -glass_th * 0.5, z)) for x, z in g_pts_2d]
    f_front = bm.faces.new(v_front)
    f_front.material_index = 1
    f_back = bm.faces.new(list(reversed(v_back)))
    f_back.material_index = 1
    n_pts = len(g_pts_2d)
    for i in range(n_pts):
        next_i = (i + 1) % n_pts
        f_side = bm.faces.new([v_front[i], v_front[next_i], v_back[next_i], v_back[i]])
        f_side.material_index = 1

    # ── C. 格子・針金 (Grille / Wire / Mullion) [mat_idx = 2] ──
    wire_y = half_d * 0.10 # ガラスの直前面
    w_th = max(0.004, wire_thickness)
    w_dp = w_th * 1.5

    def add_wire_segment(p1, p2, thickness, depth_dim, mat_index=2):
        """2点間を結ぶ角柱バーを生成"""
        dx = p2[0] - p1[0]
        dz = p2[1] - p1[1]
        length = math.hypot(dx, dz)
        if length < 0.005:
            return
        cx = (p1[0] + p2[0]) * 0.5
        cz = (p1[1] + p2[1]) * 0.5
        ang = math.atan2(dz, dx)
        res = bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=mathutils.Matrix.Translation((cx, wire_y, cz)) @
                   mathutils.Matrix.Rotation(-ang, 4, 'Y') @
                   mathutils.Matrix.Diagonal((length, depth_dim, thickness, 1.0))
        )
        for f in bm.faces:
            if all(v in res['verts'] for v in f.verts):
                f.material_index = mat_index

    if grille_style == 'SUNBURST':
        # ── ☀️ 洋館サンバースト・ファンライト (参考画像4, 5準拠：西洋建築の決定版) ──
        # 1. 水平トランサム（スプリングラインの区切り横桟）
        add_wire_segment((-r_in - 0.02, spring_z), (r_in + 0.02, spring_z), w_th * 2.2, w_dp * 1.5)

        # 2. 下部サッシグリッド（端正な縦横格子）
        # 垂直中央マリオン
        add_wire_segment((0.0, sill_h - 0.01), (0.0, spring_z), w_th * 2.2, w_dp * 1.5)
        # 左右の垂直小桟
        for sign in (-0.5, 0.5):
            add_wire_segment((r_in * sign, sill_h - 0.01), (r_in * sign, spring_z), w_th * 1.5, w_dp * 1.2)
        # 水平小桟（2〜3段）
        h_sub = spring_z - sill_h
        for frac in (0.33, 0.66):
            tz = sill_h + h_sub * frac
            add_wire_segment((-r_in - 0.01, tz), (r_in + 0.01, tz), w_th * 1.5, w_dp * 1.2)

        # 3. 上部ファンライト（同心半円アーチ ＋ 放射状スポーク）
        # 同心円アーチ（半径 0.55 * r_in）
        sub_arc_r = r_in * 0.55
        n_sa = 20
        sa_pts = []
        for s in range(n_sa + 1):
            ang = math.pi * (1.0 - s / float(n_sa))
            sx = sub_arc_r * math.cos(ang)
            sz = spring_z + sub_arc_r * math.sin(ang)
            sa_pts.append((sx, sz))
        for k in range(len(sa_pts) - 1):
            add_wire_segment(sa_pts[k], sa_pts[k+1], w_th * 1.8, w_dp * 1.3)

        # 放射状スポーク（中央から同心円、および同心円から外周アーチへ）
        n_spokes = 5
        for sp in range(n_spokes):
            sp_ang = math.pi * (sp + 1) / float(n_spokes + 1)
            # 内側スポーク（中心から同心円まで）
            p_center = (0.0, spring_z)
            p_inner = (sub_arc_r * math.cos(sp_ang), spring_z + sub_arc_r * math.sin(sp_ang))
            # 外側スポーク（同心円から外枠アーチまで）
            p_outer = (r_in * 0.98 * math.cos(sp_ang), spring_z + r_in * 0.98 * math.sin(sp_ang))
            add_wire_segment(p_center, p_inner, w_th * 1.6, w_dp * 1.2)
            add_wire_segment(p_inner, p_outer, w_th * 1.6, w_dp * 1.2)

    elif grille_style == 'CROSS':
        # ── ✝️ 十字の窓枠・十字棧 (Cross Mullion) ──
        top_z = get_arch_z(0.0) + 0.015
        add_wire_segment((0.0, sill_h - 0.015), (0.0, top_z), w_th * 2.8, w_dp * 1.8)
        t_z = sill_h + (spring_z - sill_h) * 0.52
        add_wire_segment((-r_in - 0.02, t_z), (r_in + 0.02, t_z), w_th * 2.8, w_dp * 1.8)

    elif grille_style == 'DIAMOND_WIRE':
        # ── 🔷 X字の針金・菱形鉛線ガラス (Diamond Leaded Glass) ──
        n_wires = max(3, int(wire_density))
        grid_step = inner_w / float(n_wires)
        embed = 0.025
        
        def trace_and_add_lines(m_slope):
            z_min = sill_h
            z_max = get_arch_z(0.0)
            c_min = int((z_min - m_slope * (r_in + embed)) / grid_step) - 2
            c_max = int((z_max + abs(m_slope) * (r_in + embed)) / grid_step) + 2

            for c_idx in range(c_min, c_max + 1):
                c_val = c_idx * grid_step
                samples = 200
                valid_pts = []
                x_start = -r_in - embed
                x_end = r_in + embed
                for si in range(samples + 1):
                    x = x_start + (x_end - x_start) * (si / float(samples))
                    z = m_slope * x + c_val
                    x_clamped = max(-r_in, min(r_in, x))
                    arch_limit_z = get_arch_z(x_clamped) + embed
                    sill_limit_z = sill_h - embed
                    if sill_limit_z <= z <= arch_limit_z:
                        valid_pts.append((x, z))

                if len(valid_pts) >= 2:
                    p_start = valid_pts[0]
                    p_end = valid_pts[-1]
                    add_wire_segment(p_start, p_end, w_th, w_dp)

        trace_and_add_lines(1.0)
        trace_and_add_lines(-1.0)

    elif grille_style == 'IRON_BARS':
        # ── ⛓️ 縦鉄格子 (Vertical Iron Bars) ──
        n_bars = max(3, int(wire_density))
        bar_spacing = inner_w / float(n_bars + 1)
        b_rad = w_th * 1.8

        for i in range(n_bars):
            bx = -r_in + (i + 1) * bar_spacing
            top_z = get_arch_z(bx) + 0.015
            add_wire_segment((bx, sill_h - 0.015), (bx, top_z), b_rad, b_rad)

        h_range = spring_z - sill_h
        for frac in (0.25, 0.70):
            tz = sill_h + h_range * frac
            add_wire_segment((-r_in - 0.02, tz), (r_in + 0.02, tz), b_rad * 0.9, b_rad * 1.4)

    elif grille_style == 'GOTHIC_TRACERY':
        # ── 🌹 ゴシック窓飾り (Gothic Lancet & Trefoil) ──
        add_wire_segment((0.0, sill_h - 0.015), (0.0, spring_z + 0.01), w_th * 2.5, w_dp * 1.6)
        sub_r = r_in * 0.5
        n_sub = 16
        for side in (-sub_r, sub_r):
            sub_pts = []
            for s in range(n_sub + 1):
                ang = math.pi * (1.0 - s / float(n_sub))
                xv = side + sub_r * 0.98 * math.cos(ang)
                zv = spring_z - 0.02 + (arch_rise * 0.58) * math.sin(ang)
                sub_pts.append((xv, zv))
            for k in range(len(sub_pts) - 1):
                add_wire_segment(sub_pts[k], sub_pts[k+1], w_th * 1.8, w_dp * 1.4)

        tref_cz = spring_z + arch_rise * 0.62
        tref_r = sub_r * 0.45
        n_t = 20
        tref_pts = []
        for s in range(n_t + 1):
            ang = (s / float(n_t)) * math.pi * 2.0
            rx = math.cos(ang) * tref_r
            rz = tref_cz + math.sin(ang) * tref_r
            tref_pts.append((rx, rz))
        for k in range(len(tref_pts) - 1):
            add_wire_segment(tref_pts[k], tref_pts[k+1], w_th * 1.6, w_dp * 1.4)

    # ── D. プロシージャル微細チゼル変位（石材表面の適正質感化） ──
    # マシュマロ化を防ぎ、シャープな建築エッジを保ったまま微細なノミ痕（2mm）のみを付与
    bm.verts.ensure_lookup_table()
    bm.normal_update()

    disp_strength = 0.0025 # 2.5mmの微細ノミ痕（建築プロポーションを厳密保持）
    s_seed = (seed % 1000) * 17.31
    stone_verts_set = set()
    for f in bm.faces:
        if f.material_index == 0:
            for v in f.verts:
                stone_verts_set.add(v)

    for v in stone_verts_set:
        if abs(v.co.y - (-half_d)) < 0.005:
            continue

        x, y, z = v.co.x, v.co.y, v.co.z
        f1 = math.sin(x * 12.0 + s_seed) * math.cos(z * 11.0 + s_seed * 1.3)
        f2 = math.sin(y * 18.0 + z * 16.0 + s_seed * 2.1) * 0.5
        disp_val = (f1 + f2) / 1.5

        vn = v.normal
        if vn.length > 0.1:
            v.co += vn * (disp_val * disp_strength)

    bm.verts.ensure_lookup_table()
    bm.normal_update()
    for f in bm.faces:
        f.smooth = False

    return bm.verts[:]


