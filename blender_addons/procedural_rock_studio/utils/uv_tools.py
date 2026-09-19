from mathutils import Matrix

DEFAULT_TILE_METERS = 1.0   # UV 1.0 = 1m（タイリングテクスチャ向け）


def assign_box_uv(mesh, matrix=None, tile=DEFAULT_TILE_METERS, uv_name="UVMap"):
    """
    メッシュにボックス投影のUVを付ける（各面を法線の主軸方向へ投影）。
    matrix を渡すと「その空間での座標・法線」で投影する（既定は単位行列=メッシュのローカル座標）。
    扉の破壊メッシュ(破片)・無傷の扉・石枠のすべてを「組み上がった姿勢のDoor_Frameローカル空間」で
    同じ規則で投影するため、破片に割れても木目・石目が連続し、無傷の扉との継ぎ目も出ない。
      前後面(±Y)=(X, Z) / 左右面(±X)=(Y, Z) / 上下面(±Z)=(X, Y)。裏面は鏡像にならないよう向きを反転。
    """
    uv_layer = mesh.uv_layers.get(uv_name) or mesh.uv_layers.new(name=uv_name)
    mesh.uv_layers.active = uv_layer
    m = matrix if matrix is not None else Matrix.Identity(4)
    m3 = m.to_3x3()
    verts = mesh.vertices
    loops = mesh.loops
    inv_tile = 1.0 / tile
    for poly in mesh.polygons:
        n = m3 @ poly.normal
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        for li in poly.loop_indices:
            co = m @ verts[loops[li].vertex_index].co
            if ay >= ax and ay >= az:
                u, v = (co.x if n.y < 0.0 else -co.x), co.z
            elif ax >= az:
                u, v = (co.y if n.x > 0.0 else -co.y), co.z
            else:
                u, v = co.x, (co.y if n.z > 0.0 else -co.y)
            uv_layer.data[li].uv = (u * inv_tile, v * inv_tile)
    return uv_layer
