import bpy
import bmesh
import math
import random

def build_convex_hull_rock(bm, size_x, size_y, size_z, point_count=18, is_crag=True, seed=0):
    """Convex Hull algorithm (YouTube Sacoche Ito 3D method)"""
    random.seed(seed)
    
    # 1. Distribute Random 3D Points
    points = []
    num_pts = max(12, min(36, point_count))
    rx = size_x * 0.5
    ry = size_y * 0.5
    rz = size_z * 0.5
    
    if is_crag:
        for _ in range(num_pts):
            u = random.random()
            theta = random.uniform(0, math.pi * 2)
            phi = random.uniform(-math.pi * 0.5, math.pi * 0.5)
            rad_scale = u ** 0.5
            px = math.cos(phi) * math.cos(theta) * rx * rad_scale
            py = math.cos(phi) * math.sin(theta) * ry * rad_scale
            pz = math.sin(phi) * rz * rad_scale
            
            px += (random.random() - 0.5) * (rx * 0.35)
            py += (random.random() - 0.5) * (ry * 0.35)
            pz += (random.random() - 0.5) * (rz * 0.35)
            points.append((px, py, pz))

        # Satellite clusters for jagged crags
        sub_clusters = random.randint(2, 4)
        for _ in range(sub_clusters):
            c_center_x = random.uniform(-rx * 0.6, rx * 0.6)
            c_center_y = random.uniform(-ry * 0.6, ry * 0.6)
            c_center_z = random.uniform(-rz * 0.4, rz * 0.2)
            c_rad = min(rx, ry, rz) * random.uniform(0.3, 0.6)
            for _ in range(6):
                ang = random.uniform(0, math.pi * 2)
                p_phi = random.uniform(-math.pi * 0.5, math.pi * 0.5)
                points.append((
                    c_center_x + math.cos(p_phi) * math.cos(ang) * c_rad,
                    c_center_y + math.cos(p_phi) * math.sin(ang) * c_rad,
                    c_center_z + math.sin(p_phi) * c_rad
                ))
    else:
        # 丸岩（BOULDER）のプロシージャル多様化
        flatten_z = random.uniform(0.65, 1.25)
        stretch_x = random.uniform(0.75, 1.35)
        stretch_y = random.uniform(0.75, 1.35)
        asym_x = random.uniform(-0.25, 0.25)
        asym_y = random.uniform(-0.25, 0.25)
        asym_z = random.uniform(-0.15, 0.15)
        
        for _ in range(num_pts):
            u = random.random()
            theta = random.uniform(0, math.pi * 2)
            phi = random.uniform(-math.pi * 0.5, math.pi * 0.5)
            rad_scale = 0.70 + 0.30 * (u ** 0.5)
            
            px = math.cos(phi) * math.cos(theta) * rx * rad_scale * stretch_x
            py = math.cos(phi) * math.sin(theta) * ry * rad_scale * stretch_y
            pz = math.sin(phi) * rz * rad_scale * flatten_z
            
            dist = (px*px + py*py + pz*pz) ** 0.5
            px += asym_x * dist
            py += asym_y * dist
            pz += asym_z * dist
            
            if pz < -rz * 0.45:
                pz = -rz * 0.45 + (pz + rz * 0.45) * 0.35
                
            points.append((px, py, pz))
            
        weathered_facets = random.randint(1, 3)
        for _ in range(weathered_facets):
            n_theta = random.uniform(0, math.pi * 2)
            n_phi = random.uniform(-0.4, 0.7)
            nx = math.cos(n_phi) * math.cos(n_theta)
            ny = math.cos(n_phi) * math.sin(n_theta)
            nz = math.sin(n_phi)
            plane_dist = min(rx, ry, rz) * random.uniform(0.55, 0.85)
            for idx in range(len(points)):
                pt = points[idx]
                dot = pt[0]*nx + pt[1]*ny + pt[2]*nz
                if dot > plane_dist:
                    excess = dot - plane_dist
                    points[idx] = (pt[0] - nx * excess * 0.85, pt[1] - ny * excess * 0.85, pt[2] - nz * excess * 0.85)

    created_verts = [bm.verts.new(p) for p in points]
    bm.verts.ensure_lookup_table()

    # 2. CONVEX HULL
    res_hull = bmesh.ops.convex_hull(
        bm,
        input=created_verts,
        use_existing_faces=False
    )

    internal_verts = [v for v in created_verts if v not in res_hull['geom']]
    bmesh.ops.delete(bm, geom=internal_verts, context='VERTS')

    # 3. Edge Chipping & Bevel
    hull_geom = [e for e in res_hull['geom'] if isinstance(e, bmesh.types.BMEdge)]
    if hull_geom and is_crag:
        try:
            bmesh.ops.bevel(
                bm,
                geom=hull_geom,
                offset=min(rx, ry, rz) * 0.04,
                segments=1,
                profile=0.7
            )
        except Exception:
            pass

    return bm.verts[:]


def build_rock_base(bm, size_x, size_y, size_z, style="BOULDER", seed=0):
    """丸岩・巨石モデリング"""
    return build_convex_hull_rock(bm, size_x, size_y, size_z, point_count=22, is_crag=False, seed=seed)


def build_crag_base(bm, size_x, size_y, size_z, style="JAGGED_CRAG", chisel_cuts=6, seed=0):
    """険岩・断崖モデリング"""
    pts = 16 if style in ("SHARP", "FRACTURED") else 22
    return build_convex_hull_rock(bm, size_x, size_y, size_z, point_count=pts, is_crag=True, seed=seed)
