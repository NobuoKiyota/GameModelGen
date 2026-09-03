import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix

def get_or_load_image(image_path):
    """画像の読み込みまたはキャッシュ取得"""
    if not image_path or not os.path.isfile(image_path):
        return None
    # 既存チェック
    fname = os.path.basename(image_path)
    for img in bpy.data.images:
        if img.filepath == image_path or img.name == fname:
            return img
    try:
        return bpy.data.images.load(image_path)
    except Exception as e:
        print(f"[ImageDisplace] Failed to load image: {e}")
        return None


def create_base_displace_grid(bm, shape_type="SLAB_RELIEF", aspect=1.0, size=2.0, resolution=96):
    """アスペクト比を維持した均一細分化ベースメッシュ（四角スラブまたは円形メダル）の生成"""
    uv_layer = bm.loops.layers.uv.verify()

    if shape_type == "COIN_MEDAL":
        # 完璧な同心円クワッドディスク (Concentric Rings Disc)
        radius = size * 0.5
        rings_count = max(8, int(resolution * 0.45))
        segments = max(24, int(resolution * 0.75))
        step_ang = (math.pi * 2.0) / segments

        # 中心頂点
        center_v = bm.verts.new((0.0, 0.0, 0.0))
        rings = []

        for ri in range(1, rings_count + 1):
            rf = ri / rings_count
            cur_r = radius * rf
            ring_verts = []
            for si in range(segments):
                ang = si * step_ang
                vx = math.cos(ang) * cur_r
                vy = math.sin(ang) * cur_r
                ring_verts.append(bm.verts.new((vx, vy, 0.0)))
            rings.append(ring_verts)

        bm.verts.ensure_lookup_table()

        # 最内周の三角面張り (Fan)
        inner_ring = rings[0]
        for si in range(segments):
            s_next = (si + 1) % segments
            bm.faces.new((center_v, inner_ring[si], inner_ring[s_next]))

        # 外側リングの四角面張り (Quads)
        for ri in range(rings_count - 1):
            r0 = rings[ri]
            r1 = rings[ri + 1]
            for si in range(segments):
                s_next = (si + 1) % segments
                bm.faces.new((r0[si], r1[si], r1[s_next], r0[s_next]))

        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        # 円形 UV マッピング (0.5 中心, 半径 0.5)
        for face in bm.faces:
            for loop in face.loops:
                co = loop.vert.co
                u = (co.x / (radius * 2.0)) + 0.5
                v = (co.y / (radius * 2.0)) + 0.5
                loop[uv_layer].uv = (max(0.0, min(1.0, u)), max(0.0, min(1.0, v)))

    else: # SLAB_RELIEF (標準四角スラブ)
        w = size
        h = size / max(0.01, aspect)
        res_x = max(8, resolution)
        res_y = max(8, int(resolution / max(0.01, aspect)))

        # グリッド頂点生成
        grid_verts = []
        for yi in range(res_y + 1):
            yf = yi / res_y
            py = (yf - 0.5) * h
            row = []
            for xi in range(res_x + 1):
                xf = xi / res_x
                px = (xf - 0.5) * w
                v = bm.verts.new((px, py, 0.0))
                row.append(v)
            grid_verts.append(row)
        bm.verts.ensure_lookup_table()

        # 面生成 & 正確な 0.0〜1.0 UV アサイン
        for yi in range(res_y):
            for xi in range(res_x):
                v00 = grid_verts[yi][xi]
                v10 = grid_verts[yi][xi + 1]
                v11 = grid_verts[yi + 1][xi + 1]
                v01 = grid_verts[yi + 1][xi]
                f = bm.faces.new((v00, v10, v11, v01))

                u0, u1 = xi / res_x, (xi + 1) / res_x
                v0, v1 = yi / res_y, (yi + 1) / res_y

                for loop in f.loops:
                    if loop.vert == v00:
                        loop[uv_layer].uv = (u0, v0)
                    elif loop.vert == v10:
                        loop[uv_layer].uv = (u1, v0)
                    elif loop.vert == v11:
                        loop[uv_layer].uv = (u1, v1)
                    elif loop.vert == v01:
                        loop[uv_layer].uv = (u0, v1)

    bm.normal_update()


def get_or_create_cutout_node_group():
    """同階層型抜き（Cutout）用の Geometry Nodes グループを取得または新規作成"""
    group_name = "PRS_RealtimeCutoutTree"
    if group_name in bpy.data.node_groups:
        return bpy.data.node_groups[group_name]

    tree = bpy.data.node_groups.new(name=group_name, type='GeometryNodeTree')

    # Blender 3.6 / 4.x の互換性吸収
    if hasattr(tree, "interface"):
        tree.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
        sock_th = tree.interface.new_socket("Threshold", in_out='INPUT', socket_type='NodeSocketFloat')
        sock_th.default_value = 0.02
        sock_inv = tree.interface.new_socket("Invert", in_out='INPUT', socket_type='NodeSocketBool')
        sock_inv.default_value = False
        tree.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    else:
        tree.inputs.new('NodeSocketGeometry', "Geometry")
        sock_th = tree.inputs.new('NodeSocketFloat', "Threshold")
        sock_th.default_value = 0.02
        sock_inv = tree.inputs.new('NodeSocketBool', "Invert")
        sock_inv.default_value = False
        tree.outputs.new('NodeSocketGeometry', "Geometry")

    nodes = tree.nodes
    links = tree.links
    nodes.clear()

    n_in = nodes.new('NodeGroupInput')
    n_in.location = (-450, 0)
    n_out = nodes.new('NodeGroupOutput')
    n_out.location = (450, 0)

    # Position ➔ Separate XYZ (Z)
    n_pos = nodes.new('GeometryNodeInputPosition')
    n_pos.location = (-450, -180)

    n_sep = nodes.new('ShaderNodeSeparateXYZ')
    n_sep.location = (-250, -180)
    links.new(n_pos.outputs['Position'], n_sep.inputs['Vector'])

    # Compare (Z < Threshold)
    n_cmp = nodes.new('FunctionNodeCompare')
    n_cmp.data_type = 'FLOAT'
    n_cmp.operation = 'LESS_THAN'
    n_cmp.location = (-50, -180)
    links.new(n_sep.outputs['Z'], n_cmp.inputs['A'])
    links.new(n_in.outputs['Threshold'], n_cmp.inputs['B'])

    # Invert は Boolean Math (XOR) で一元制御
    n_xor = nodes.new('FunctionNodeBooleanMath')
    n_xor.operation = 'XOR'
    n_xor.location = (150, -180)
    links.new(n_cmp.outputs['Result'], n_xor.inputs[0])
    links.new(n_in.outputs['Invert'], n_xor.inputs[1])

    # Delete Geometry (Face)
    n_del = nodes.new('GeometryNodeDeleteGeometry')
    n_del.domain = 'FACE'
    n_del.location = (300, 0)
    links.new(n_in.outputs['Geometry'], n_del.inputs['Geometry'])
    links.new(n_xor.outputs['Boolean'], n_del.inputs['Selection'])
    links.new(n_del.outputs['Geometry'], n_out.inputs['Geometry'])

    return tree


def setup_or_update_cutout_modifier(obj, enable=True, threshold=0.02, invert=False):
    """オブジェクトの Cutout モディファイアをリアルタイム設定・更新"""
    if not obj or obj.type != 'MESH':
        return

    mod_name = "Cutout_Realtime"
    mod = obj.modifiers.get(mod_name)

    if not enable:
        if mod:
            mod.show_viewport = False
            mod.show_render = False
        return

    if not mod:
        mod = obj.modifiers.new(name=mod_name, type='NODES')
        tree = get_or_create_cutout_node_group()
        mod.node_group = tree

    mod.show_viewport = True
    mod.show_render = True

    # 型抜きモード時は外枠マスクを解除して全体を型抜き対象に
    mod_disp = obj.modifiers.get("Displace_Relief")
    if mod_disp:
        mod_disp.vertex_group = "" if enable else "Displace_Mask"

    # パラメーター代入
    if hasattr(mod.node_group, "inputs"):
        for inp in mod.node_group.inputs:
            if inp.name == "Threshold":
                mod[inp.identifier] = threshold
            elif inp.name == "Invert":
                mod[inp.identifier] = invert
    elif hasattr(mod.node_group, "interface"):
        for item in mod.node_group.interface.items_tree:
            if item.name == "Threshold":
                mod[item.identifier] = threshold
            elif item.name == "Invert":
                mod[item.identifier] = invert

    obj.data.update()


def solidify_and_close_mesh(obj, depth=0.15):
    """表面の境界エッジを下方に押し出し、底面を張って完全密閉（クローズド）立体化（複数アイランド対応）"""
    if bpy.context.mode != 'OBJECT':
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass

    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    # 1. 境界エッジ（1つの面しか隣接していない外周エッジ）を収集
    boundary_edges = [e for e in bm.edges if len(e.link_faces) == 1]
    if not boundary_edges:
        bm.free()
        return

    # 2. 外周エッジを下方に押し出し（Extrude）
    res_ext = bmesh.ops.extrude_edge_only(bm, edges=boundary_edges)
    new_geom = res_ext['geom']
    new_verts = [ele for ele in new_geom if isinstance(ele, bmesh.types.BMVert)]

    # 押し出した頂点を -Z (depth) に移動
    for v in new_verts:
        v.co.z -= depth

    # 3. 底面エッジループを収集して連結アイランドごとに蓋を張る
    bottom_edges = [e for e in new_geom if isinstance(e, bmesh.types.BMEdge) and all(v in new_verts for v in e.verts)]
    if bottom_edges:
        adj = {}
        for e in bottom_edges:
            adj.setdefault(e.verts[0], []).append(e)
            adj.setdefault(e.verts[1], []).append(e)

        visited_edges = set()
        for start_edge in bottom_edges:
            if start_edge in visited_edges:
                continue
            loop_edges = []
            queue = [start_edge]
            visited_edges.add(start_edge)
            while queue:
                curr_e = queue.pop()
                loop_edges.append(curr_e)
                for v in curr_e.verts:
                    for neighbor_e in adj.get(v, []):
                        if neighbor_e not in visited_edges:
                            visited_edges.add(neighbor_e)
                            queue.append(neighbor_e)

            try:
                bmesh.ops.edgeloop_fill(bm, edges=loop_edges)
            except Exception:
                loop_verts = list({v for e in loop_edges for v in e.verts})
                if loop_verts:
                    c_pos = sum((v.co for v in loop_verts), Vector((0, 0, 0))) / len(loop_verts)
                    c_v = bm.verts.new(c_pos)
                    for le in loop_edges:
                        try:
                            bm.faces.new((le.verts[0], le.verts[1], c_v))
                        except Exception:
                            pass

    # 法線の再計算と重複除去
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def create_image_displace_material(name, img=None, style="ORIGINAL_COLOR"):
    """画像立体化アセット用マテリアル生成（元画像カラーまたはプロシージャル石材）"""
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (600, 0)
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (300, 0)
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    if style == "ORIGINAL_COLOR" and img:
        # 元画像をそのまま表面テクスチャとしてアサイン
        node_tex = nodes.new(type='ShaderNodeTexImage')
        node_tex.location = (0, 0)
        node_tex.image = img
        links.new(node_tex.outputs['Color'], node_bsdf.inputs['Base Color'])
        node_bsdf.inputs['Roughness'].default_value = 0.65
    elif style == "MARBLE":
        # 大理石
        from ..materials.nature_shaders import create_procedural_pillar_shader
        return create_procedural_pillar_shader(name, mat_type="MARBLE")
    elif style == "MOSSY_RUINS":
        from ..materials.nature_shaders import create_procedural_pillar_shader
        return create_procedural_pillar_shader(name, mat_type="MOSSY_RUINS")
    else: # ANCIENT_STONE
        from ..materials.nature_shaders import create_procedural_pillar_shader
        return create_procedural_pillar_shader(name, mat_type="ANCIENT_STONE")

    return mat


def generate_image_displace_asset(
    context,
    image_path="",
    name="Image_Displace_Asset",
    shape_type="SLAB_RELIEF",
    depth=0.15,
    height=0.08,
    strength=0.20,
    midlevel=0.50,
    enable_cutout=False,
    cutout_threshold=0.02,
    cutout_invert=False,
    resolution=96,
    close_mesh=True,
    decimate_ratio=0.5,
    material_style="ORIGINAL_COLOR",
    auto_apply=False
):
    """2D画像から3D立体メッシュ（レリーフ/コイン/スラブ）を半自動生成する統合関数"""
    img = get_or_load_image(image_path)
    aspect = 1.0
    if img:
        w, h = img.size[0], img.size[1]
        if h > 0:
            aspect = w / h

    # 1. メッシュ作成
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    create_base_displace_grid(bm, shape_type=shape_type, aspect=aspect, size=2.0, resolution=resolution)
    bm.to_mesh(mesh)
    bm.free()

    for f in mesh.polygons:
        f.use_smooth = True

    # 2. 外周保護ウェイトグループ (Border Protection Mask)
    vg = obj.vertex_groups.new(name="Displace_Mask")
    bm_v = bmesh.new()
    bm_v.from_mesh(mesh)
    bm_v.verts.ensure_lookup_table()
    bm_v.edges.ensure_lookup_table()
    boundary_v_indices = set()
    for e in bm_v.edges:
        if len(e.link_faces) == 1:
            boundary_v_indices.add(e.verts[0].index)
            boundary_v_indices.add(e.verts[1].index)
    bm_v.free()

    for v in mesh.vertices:
        weight = 0.0 if v.index in boundary_v_indices else 1.0
        vg.add([v.index], weight, 'REPLACE')

    # 3. Displace Modifier のセットアップ (Strength & Midlevel)
    if img:
        tex = bpy.data.textures.new(f"{name}_DispTex", type='IMAGE')
        tex.image = img
        try:
            img.colorspace_settings.name = 'Non-Color'
        except Exception:
            pass

        mod_disp = obj.modifiers.new(name="Displace_Relief", type='DISPLACE')
        mod_disp.texture = tex
        mod_disp.texture_coords = 'UV'
        mod_disp.vertex_group = "" if enable_cutout else "Displace_Mask"
        mod_disp.strength = strength if abs(strength) > 0.0001 else height
        mod_disp.mid_level = midlevel

    # 4. 同階層型抜き (Cutout) のセットアップ
    if enable_cutout:
        setup_or_update_cutout_modifier(obj, enable=True, threshold=cutout_threshold, invert=cutout_invert)

    # 5. マテリアルの適用
    mat = create_image_displace_material(f"{name}_Mat", img=img, style=material_style)
    obj.data.materials.append(mat)

    # 6. 確定（Bake / Apply & Solidify）
    if auto_apply:
        finalize_game_ready_displace(obj, depth=depth, decimate_ratio=decimate_ratio, close_mesh=close_mesh)

    return obj


def finalize_game_ready_displace(obj, depth=0.15, decimate_ratio=0.5, close_mesh=True):
    """ゲーム用確定処理: モディファイア適用 ➔ クローズド密閉化 ➔ スマート軽量化 ➔ ベベル"""
    if bpy.context.mode != 'OBJECT':
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # 1. 既存モディファイアを適用
    for mod in list(obj.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except Exception:
            pass

    # 2. 裏面・側面押し出しによるクローズド密閉化
    if close_mesh:
        solidify_and_close_mesh(obj, depth=depth)

    # 3. スマート軽量化 (Decimate)
    if decimate_ratio < 0.99:
        dec_mod = obj.modifiers.new(name="Decimate_Opt", type='DECIMATE')
        dec_mod.ratio = max(0.05, min(1.0, decimate_ratio))
        try:
            bpy.ops.object.modifier_apply(modifier=dec_mod.name)
        except Exception:
            pass

    # 4. 輪郭エッジの保護ベベル
    bev_mod = obj.modifiers.new(name="Edge_Bevel", type='BEVEL')
    bev_mod.width = 0.012
    bev_mod.segments = 2
    bev_mod.limit_method = 'ANGLE'
    bev_mod.angle_limit = math.radians(35.0)

    # 5. 原点を底面にスナップ
    mesh = obj.data
    min_z = min((v.co.z for v in mesh.vertices), default=0.0)
    for v in mesh.vertices:
        v.co.z -= min_z
    mesh.update()

    return obj
