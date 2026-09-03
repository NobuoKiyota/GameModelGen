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
    """同階層型抜き（Cutout）＆ 色抜き（Color Keying）用の Geometry Nodes グループを取得または新規作成"""
    group_name = "PRS_RealtimeCutoutTree"
    if group_name in bpy.data.node_groups:
        return bpy.data.node_groups[group_name]

    tree = bpy.data.node_groups.new(name=group_name, type='GeometryNodeTree')

    # Blender 3.6 / 4.x の互換性吸収
    if hasattr(tree, "interface"):
        tree.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
        sock_img = tree.interface.new_socket("Image", in_out='INPUT', socket_type='NodeSocketImage')
        sock_th = tree.interface.new_socket("Threshold", in_out='INPUT', socket_type='NodeSocketFloat')
        sock_th.default_value = 0.02
        sock_inv = tree.interface.new_socket("Invert", in_out='INPUT', socket_type='NodeSocketBool')
        sock_inv.default_value = False
        sock_enc = tree.interface.new_socket("Enable_Color", in_out='INPUT', socket_type='NodeSocketBool')
        sock_enc.default_value = False
        sock_col = tree.interface.new_socket("Key_Color", in_out='INPUT', socket_type='NodeSocketColor')
        sock_col.default_value = (1.0, 1.0, 1.0, 1.0)
        sock_tol = tree.interface.new_socket("Color_Tolerance", in_out='INPUT', socket_type='NodeSocketFloat')
        sock_tol.default_value = 0.15
        sock_mode = tree.interface.new_socket("Cutout_Mode", in_out='INPUT', socket_type='NodeSocketInt')
        sock_mode.default_value = 0
        tree.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    else:
        tree.inputs.new('NodeSocketGeometry', "Geometry")
        tree.inputs.new('NodeSocketImage', "Image")
        sock_th = tree.inputs.new('NodeSocketFloat', "Threshold")
        sock_th.default_value = 0.02
        sock_inv = tree.inputs.new('NodeSocketBool', "Invert")
        sock_inv.default_value = False
        sock_enc = tree.inputs.new('NodeSocketBool', "Enable_Color")
        sock_enc.default_value = False
        sock_col = tree.inputs.new('NodeSocketColor', "Key_Color")
        sock_col.default_value = (1.0, 1.0, 1.0, 1.0)
        sock_tol = tree.inputs.new('NodeSocketFloat', "Color_Tolerance")
        sock_tol.default_value = 0.15
        sock_mode = tree.inputs.new('NodeSocketInt', "Cutout_Mode")
        sock_mode.default_value = 0
        tree.outputs.new('NodeSocketGeometry', "Geometry")

    nodes = tree.nodes
    links = tree.links
    nodes.clear()

    n_in = nodes.new('NodeGroupInput')
    n_in.location = (-600, 0)
    n_out = nodes.new('NodeGroupOutput')
    n_out.location = (600, 0)

    # 1. 高さ判定 (Height Mask: Z < Threshold)
    n_pos = nodes.new('GeometryNodeInputPosition')
    n_pos.location = (-600, -180)

    n_sep = nodes.new('ShaderNodeSeparateXYZ')
    n_sep.location = (-400, -180)
    links.new(n_pos.outputs['Position'], n_sep.inputs['Vector'])

    n_cmp_h = nodes.new('FunctionNodeCompare')
    n_cmp_h.data_type = 'FLOAT'
    n_cmp_h.operation = 'LESS_THAN'
    n_cmp_h.location = (-200, -180)
    links.new(n_sep.outputs['Z'], n_cmp_h.inputs['A'])
    links.new(n_in.outputs['Threshold'], n_cmp_h.inputs['B'])

    # 2. 色判定 (Color Mask: Distance(Color, Key_Color) < Tolerance OR Alpha < 0.5)
    n_uv = nodes.new('GeometryNodeInputNamedAttribute')
    n_uv.data_type = 'FLOAT_VECTOR'
    n_uv.inputs['Name'].default_value = 'UVMap'
    n_uv.location = (-600, -360)

    n_tex = nodes.new('GeometryNodeImageTexture')
    n_tex.location = (-400, -360)
    links.new(n_in.outputs['Image'], n_tex.inputs['Image'])
    links.new(n_uv.outputs[0], n_tex.inputs['Vector'])

    n_dist = nodes.new('ShaderNodeVectorMath')
    n_dist.operation = 'DISTANCE'
    n_dist.location = (-200, -360)
    links.new(n_tex.outputs['Color'], n_dist.inputs[0])
    links.new(n_in.outputs['Key_Color'], n_dist.inputs[1])

    n_cmp_col = nodes.new('FunctionNodeCompare')
    n_cmp_col.data_type = 'FLOAT'
    n_cmp_col.operation = 'LESS_THAN'
    n_cmp_col.location = (0, -360)
    links.new(n_dist.outputs['Value'], n_cmp_col.inputs['A'])
    links.new(n_in.outputs['Color_Tolerance'], n_cmp_col.inputs['B'])

    n_cmp_alpha = nodes.new('FunctionNodeCompare')
    n_cmp_alpha.data_type = 'FLOAT'
    n_cmp_alpha.operation = 'LESS_THAN'
    n_cmp_alpha.location = (0, -500)
    links.new(n_tex.outputs['Alpha'], n_cmp_alpha.inputs['A'])
    n_cmp_alpha.inputs['B'].default_value = 0.5

    n_or_col = nodes.new('FunctionNodeBooleanMath')
    n_or_col.operation = 'OR'
    n_or_col.location = (160, -400)
    links.new(n_cmp_col.outputs['Result'], n_or_col.inputs[0])
    links.new(n_cmp_alpha.outputs['Result'], n_or_col.inputs[1])

    # 3. 併用モード合成 (OR / AND / COLOR / HEIGHT)
    n_or_both = nodes.new('FunctionNodeBooleanMath')
    n_or_both.operation = 'OR'
    n_or_both.location = (0, -180)
    links.new(n_cmp_h.outputs['Result'], n_or_both.inputs[0])
    links.new(n_or_col.outputs['Boolean'], n_or_both.inputs[1])

    n_and_both = nodes.new('FunctionNodeBooleanMath')
    n_and_both.operation = 'AND'
    n_and_both.location = (0, -60)
    links.new(n_cmp_h.outputs['Result'], n_and_both.inputs[0])
    links.new(n_or_col.outputs['Boolean'], n_and_both.inputs[1])

    # モード切り替え (Compare Cutout_Mode)
    # mode == 1: AND
    n_cmp_is_and = nodes.new('FunctionNodeCompare')
    n_cmp_is_and.data_type = 'INT'
    n_cmp_is_and.operation = 'EQUAL'
    n_cmp_is_and.location = (160, -60)
    links.new(n_in.outputs['Cutout_Mode'], n_cmp_is_and.inputs['A'])
    n_cmp_is_and.inputs['B'].default_value = 1

    # mode == 2: COLOR_ONLY
    n_cmp_is_col = nodes.new('FunctionNodeCompare')
    n_cmp_is_col.data_type = 'INT'
    n_cmp_is_col.operation = 'EQUAL'
    n_cmp_is_col.location = (160, -200)
    links.new(n_in.outputs['Cutout_Mode'], n_cmp_is_col.inputs['A'])
    n_cmp_is_col.inputs['B'].default_value = 2

    # mode == 3: HEIGHT_ONLY
    n_cmp_is_h = nodes.new('FunctionNodeCompare')
    n_cmp_is_h.data_type = 'INT'
    n_cmp_is_h.operation = 'EQUAL'
    n_cmp_is_h.location = (160, -320)
    links.new(n_in.outputs['Cutout_Mode'], n_cmp_is_h.inputs['A'])
    n_cmp_is_h.inputs['B'].default_value = 3

    # Switch 連鎖でモード選択
    # 1. OR vs AND
    sw_mode1 = nodes.new('GeometryNodeSwitch')
    sw_mode1.input_type = 'BOOLEAN'
    sw_mode1.location = (300, -100)
    links.new(n_cmp_is_and.outputs['Result'], sw_mode1.inputs['Switch'])
    # False: OR, True: AND (BOOLEAN inputs: index 4, 5)
    links.new(n_or_both.outputs['Boolean'], [i for i in sw_mode1.inputs if i.name == 'False' and i.type == 'BOOLEAN'][0])
    links.new(n_and_both.outputs['Boolean'], [i for i in sw_mode1.inputs if i.name == 'True' and i.type == 'BOOLEAN'][0])

    # 2. vs COLOR_ONLY
    sw_mode2 = nodes.new('GeometryNodeSwitch')
    sw_mode2.input_type = 'BOOLEAN'
    sw_mode2.location = (360, -180)
    links.new(n_cmp_is_col.outputs['Result'], sw_mode2.inputs['Switch'])
    links.new([o for o in sw_mode1.outputs if o.type == 'BOOLEAN'][0], [i for i in sw_mode2.inputs if i.name == 'False' and i.type == 'BOOLEAN'][0])
    links.new(n_or_col.outputs['Boolean'], [i for i in sw_mode2.inputs if i.name == 'True' and i.type == 'BOOLEAN'][0])

    # 3. vs HEIGHT_ONLY
    sw_mode3 = nodes.new('GeometryNodeSwitch')
    sw_mode3.input_type = 'BOOLEAN'
    sw_mode3.location = (420, -260)
    links.new(n_cmp_is_h.outputs['Result'], sw_mode3.inputs['Switch'])
    links.new([o for o in sw_mode2.outputs if o.type == 'BOOLEAN'][0], [i for i in sw_mode3.inputs if i.name == 'False' and i.type == 'BOOLEAN'][0])
    links.new(n_cmp_h.outputs['Result'], [i for i in sw_mode3.inputs if i.name == 'True' and i.type == 'BOOLEAN'][0])

    # 4. Enable_Color の切り替え (False なら常に HeightMask)
    sw_final = nodes.new('GeometryNodeSwitch')
    sw_final.input_type = 'BOOLEAN'
    sw_final.location = (480, -100)
    links.new(n_in.outputs['Enable_Color'], sw_final.inputs['Switch'])
    links.new(n_cmp_h.outputs['Result'], [i for i in sw_final.inputs if i.name == 'False' and i.type == 'BOOLEAN'][0])
    links.new([o for o in sw_mode3.outputs if o.type == 'BOOLEAN'][0], [i for i in sw_final.inputs if i.name == 'True' and i.type == 'BOOLEAN'][0])

    # 5. 反転 XOR
    n_xor = nodes.new('FunctionNodeBooleanMath')
    n_xor.operation = 'XOR'
    n_xor.location = (540, -180)
    links.new([o for o in sw_final.outputs if o.type == 'BOOLEAN'][0], n_xor.inputs[0])
    links.new(n_in.outputs['Invert'], n_xor.inputs[1])

    # 6. Delete Geometry
    n_del = nodes.new('GeometryNodeDeleteGeometry')
    n_del.domain = 'FACE'
    n_del.location = (600, 0)
    links.new(n_in.outputs['Geometry'], n_del.inputs['Geometry'])
    links.new(n_xor.outputs['Boolean'], n_del.inputs['Selection'])
    links.new(n_del.outputs['Geometry'], n_out.inputs['Geometry'])

    return tree


def detect_image_corner_color(image_path):
    """画像の左上隅ピクセルから背景色 (R, G, B) を自動サンプリング"""
    img = get_or_load_image(image_path)
    if not img:
        return (1.0, 1.0, 1.0)
    try:
        # 左上ピクセル
        pix = img.pixels
        if len(pix) >= 4:
            return (float(pix[0]), float(pix[1]), float(pix[2]))
    except Exception as e:
        print(f"[DetectColor] Error: {e}")
    return (1.0, 1.0, 1.0)


def setup_or_update_cutout_modifier(
    obj,
    enable=True,
    threshold=0.02,
    invert=False,
    enable_color=False,
    key_color=(1.0, 1.0, 1.0, 1.0),
    color_tolerance=0.15,
    cutout_mode=0,
    img=None
):
    """オブジェクトの Cutout モディファイア（高さ型抜き＆色抜き）をリアルタイム設定・更新"""
    if not obj or obj.type != 'MESH':
        return

    mod_name = "Cutout_Realtime"
    mod = obj.modifiers.get(mod_name)

    if not enable:
        if mod:
            mod.show_viewport = False
            mod.show_render = False
        mod_disp = obj.modifiers.get("Displace_Relief")
        if mod_disp:
            mod_disp.vertex_group = "Displace_Mask"
        return

    if not mod:
        mod = obj.modifiers.new(name=mod_name, type='NODES')
        tree = get_or_create_cutout_node_group()
        mod.node_group = tree

    mod.show_viewport = True
    mod.show_render = True

    # 型抜きモード時は外枠マスクを解除
    mod_disp = obj.modifiers.get("Displace_Relief")
    if mod_disp:
        mod_disp.vertex_group = ""

    # 画像取得
    if not img and mod_disp and mod_disp.texture and getattr(mod_disp.texture, 'image', None):
        img = mod_disp.texture.image

    # パラメーター代入
    if hasattr(mod.node_group, "inputs"):
        for inp in mod.node_group.inputs:
            if inp.name == "Threshold":
                mod[inp.identifier] = threshold
            elif inp.name == "Invert":
                mod[inp.identifier] = invert
            elif inp.name == "Enable_Color":
                mod[inp.identifier] = enable_color
            elif inp.name == "Key_Color":
                mod[inp.identifier] = key_color if len(key_color) == 4 else (*key_color, 1.0)
            elif inp.name == "Color_Tolerance":
                mod[inp.identifier] = color_tolerance
            elif inp.name == "Cutout_Mode":
                mod[inp.identifier] = int(cutout_mode)
            elif inp.name == "Image" and img:
                mod[inp.identifier] = img

    obj.data.update()


def setup_or_update_subdiv_modifier(obj, level=1):
    """細分化モディファイアのリアルタイム設定・更新"""
    if not obj or obj.type != 'MESH':
        return
    mod_name = "Subdiv_Detail"
    mod = obj.modifiers.get(mod_name)
    if level <= 0:
        if mod:
            mod.show_viewport = False
            mod.show_render = False
        return

    if not mod:
        mod = obj.modifiers.new(name=mod_name, type='SUBSURF')
        mod.subdivision_type = 'SIMPLE'
        # スタックの先頭に移動
        try:
            bpy.context.view_layer.objects.active = obj
            while obj.modifiers.find(mod.name) > 0:
                bpy.ops.object.modifier_move_up(modifier=mod.name)
        except Exception:
            pass

    mod.show_viewport = True
    mod.show_render = True
    mod.levels = max(0, min(4, level))
    mod.render_levels = mod.levels
    obj.data.update()


def setup_or_update_smooth_modifier(obj, factor=0.3, iterations=2):
    """スムースモディファイアのリアルタイム設定・更新（ジャギー・等高線段差の除去）"""
    if not obj or obj.type != 'MESH':
        return
    mod_name = "Smooth_Clean"
    mod = obj.modifiers.get(mod_name)
    if factor <= 0.001 or iterations <= 0:
        if mod:
            mod.show_viewport = False
            mod.show_render = False
        return

    if not mod:
        mod = obj.modifiers.new(name=mod_name, type='SMOOTH')
        # Displaceの直後に配置
        try:
            disp_idx = obj.modifiers.find("Displace_Relief")
            if disp_idx >= 0:
                bpy.context.view_layer.objects.active = obj
                cur_idx = obj.modifiers.find(mod.name)
                while cur_idx > disp_idx + 1:
                    bpy.ops.object.modifier_move_up(modifier=mod.name)
                    cur_idx -= 1
        except Exception:
            pass

    mod.show_viewport = True
    mod.show_render = True
    mod.factor = max(0.0, min(1.0, factor))
    mod.iterations = max(1, min(20, iterations))
    obj.data.update()


def setup_or_update_solidify_modifier(obj, thickness=0.15, style='SOLID_SLAB'):
    """面（立方体）化モディファイアのリアルタイム設定・更新"""
    if not obj or obj.type != 'MESH':
        return
    mod_name = "Solidify_Block"
    mod = obj.modifiers.get(mod_name)
    rem_name = "Remesh_Block"
    mod_rem = obj.modifiers.get(rem_name)

    if thickness <= 0.001:
        if mod:
            mod.show_viewport = False
            mod.show_render = False
        if mod_rem:
            mod_rem.show_viewport = False
            mod_rem.show_render = False
        return

    if not mod:
        mod = obj.modifiers.new(name=mod_name, type='SOLIDIFY')
        mod.offset = -1.0
        mod.use_rim = True
        mod.use_rim_only = False

    mod.show_viewport = True
    mod.show_render = True
    mod.thickness = thickness

    if style == 'VOXEL_BLOCKS':
        if not mod_rem:
            mod_rem = obj.modifiers.new(name=rem_name, type='REMESH')
            mod_rem.mode = 'BLOCKS'
            mod_rem.octree_depth = 6
            mod_rem.scale = 0.9
        mod_rem.show_viewport = True
        mod_rem.show_render = True
    else:
        if mod_rem:
            mod_rem.show_viewport = False
            mod_rem.show_render = False

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
    subdiv_level=1,
    smooth_factor=0.30,
    smooth_iter=2,
    solidify_thickness=0.15,
    block_style='SOLID_SLAB',
    enable_cutout=False,
    cutout_threshold=0.02,
    cutout_invert=False,
    enable_color_cutout=False,
    key_color=(1.0, 1.0, 1.0, 1.0),
    color_tolerance=0.15,
    cutout_mode=0,
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

    # 3. 細分化 (Subdiv_Detail) のセットアップ
    if subdiv_level > 0:
        setup_or_update_subdiv_modifier(obj, level=subdiv_level)

    # 4. Displace Modifier のセットアップ (Strength & Midlevel)
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
        mod_disp.vertex_group = "" if (enable_cutout or enable_color_cutout) else "Displace_Mask"
        mod_disp.strength = strength if abs(strength) > 0.0001 else height
        mod_disp.mid_level = midlevel

    # 5. スムース (Smooth_Clean) のセットアップ
    if smooth_factor > 0.001:
        setup_or_update_smooth_modifier(obj, factor=smooth_factor, iterations=smooth_iter)

    # 6. 同階層型抜き＆色抜き (Cutout) のセットアップ
    if enable_cutout or enable_color_cutout:
        setup_or_update_cutout_modifier(
            obj,
            enable=True,
            threshold=cutout_threshold,
            invert=cutout_invert,
            enable_color=enable_color_cutout,
            key_color=key_color,
            color_tolerance=color_tolerance,
            cutout_mode=cutout_mode,
            img=img
        )

    # 7. 面(立方体)化 (Solidify_Block / Remesh) のセットアップ
    if solidify_thickness > 0.001:
        setup_or_update_solidify_modifier(obj, thickness=solidify_thickness, style=block_style)

    # 8. マテリアルの適用
    mat = create_image_displace_material(f"{name}_Mat", img=img, style=material_style)
    obj.data.materials.append(mat)

    # 9. 確定（Bake / Apply & Solidify）
    if auto_apply:
        finalize_game_ready_displace(obj, depth=solidify_thickness, decimate_ratio=decimate_ratio, close_mesh=close_mesh)

    return obj


def optimize_and_smart_uv_clean(obj, planar_angle=2.5, clean_loose=True, top_down_uv=True):
    """
    平坦面・底面・側面の不要頂点を Limited Dissolve で溶解し、
    テクスチャが歪まないスマートUVを再構築する超軽量化処理
    """
    if not obj or obj.type != 'MESH':
        return 0, 0

    mesh = obj.data
    initial_verts = len(mesh.vertices)

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    # 1. 縮退ポリゴン・重複頂点の事前クリーンアップ
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.dissolve_degenerate(bm, dist=0.0005, edges=bm.edges)

    # 2. 平面不要頂点溶解 (Limited Dissolve)
    # angle_limit 以内の同一平面上にある格子頂点・エッジを溶解
    try:
        angle_rad = math.radians(max(0.1, planar_angle))
        bmesh.ops.dissolve_limit(
            bm,
            angle_limit=angle_rad,
            use_dissolve_boundaries=False,
            delimit={'MATERIAL'},
            edges=bm.edges
        )
    except Exception as e:
        print(f"[OptimizeMesh] Dissolve limit warning: {e}")

    # 3. 孤立頂点のクリーンアップ
    if clean_loose:
        loose_verts = [v for v in bm.verts if not v.link_edges]
        if loose_verts:
            bmesh.ops.delete(bm, geom=loose_verts, context='VERTS')

    # 4. スマートUV再構築 (上面: 元画像合致 Top-Down UV, 側面・底面: シームレスUV)
    if top_down_uv:
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        uv_layer = bm.loops.layers.uv.verify()

        if bm.verts:
            xs = [v.co.x for v in bm.verts]
            ys = [v.co.y for v in bm.verts]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            width = max(max_x - min_x, 0.0001)
            height = max(max_y - min_y, 0.0001)

            for f in bm.faces:
                # 法線方向で上面判定 (normal.z > 0.3)
                if f.normal.z > 0.3:
                    for loop in f.loops:
                        vx = loop.vert.co.x
                        vy = loop.vert.co.y
                        u = (vx - min_x) / width
                        v = (vy - min_y) / height
                        loop[uv_layer].uv = (u, v)
                else:
                    # 側面・底面: 側面の角度に応じたシームレスUV
                    for loop in f.loops:
                        vx = loop.vert.co.x
                        vy = loop.vert.co.y
                        vz = loop.vert.co.z
                        u = (math.atan2(vy, vx) / (2.0 * math.pi)) + 0.5
                        v = vz * 2.0
                        loop[uv_layer].uv = (u, v)

    # 5. 法線再計算
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    bm.to_mesh(mesh)
    final_verts = len(bm.verts)
    bm.free()
    mesh.update()

    return initial_verts, final_verts


def finalize_game_ready_displace(obj, depth=0.15, decimate_ratio=0.5, close_mesh=True, planar_angle=2.5):
    """ゲーム用確定処理: モディファイア適用 ➔ クローズド密閉化 ➔ 不要頂点溶解＆スマートUV化 ➔ ベベル"""
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

    # 3. 平坦面の不要頂点溶解 ＆ スマートUV再構築
    optimize_and_smart_uv_clean(obj, planar_angle=planar_angle, clean_loose=True, top_down_uv=True)

    # 4. スマート軽量化 (Decimate)
    if decimate_ratio < 0.99:
        dec_mod = obj.modifiers.new(name="Decimate_Opt", type='DECIMATE')
        dec_mod.ratio = max(0.05, min(1.0, decimate_ratio))
        try:
            bpy.ops.object.modifier_apply(modifier=dec_mod.name)
        except Exception:
            pass

    # 5. 輪郭エッジの保護ベベル
    bev_mod = obj.modifiers.new(name="Edge_Bevel", type='BEVEL')
    bev_mod.width = 0.012
    bev_mod.segments = 2
    bev_mod.limit_method = 'ANGLE'
    bev_mod.angle_limit = math.radians(35.0)

    # 6. 原点を底面にスナップ
    mesh = obj.data
    min_z = min((v.co.z for v in mesh.vertices), default=0.0)
    for v in mesh.vertices:
        v.co.z -= min_z
    mesh.update()

    return obj
