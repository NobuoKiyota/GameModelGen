"""S02b: 人間補正版 S02（頂点を追加した 26頂点・6角形面あり）を、頂点を1つも動かさず全面四角形に整える。

追加頂点(index>=16)は、6角形面の向かい合う辺（内輪の辺と外輪の辺）に1つずつ入っている。
その2頂点を結ぶ切り込みで面を2つの四角形に分ける（切り込みの辺が既にあれば再利用、無ければ作る）。

入力: out/face_s02_human.blend   出力: out/face_s02b.blend, out/s02b_report.json
実行: blender --background --factory-startup --python steps/s02b_quadify_human.py
"""
import sys
from pathlib import Path

import bmesh
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402

STEP = "s02b"
gates = C.Gates(STEP)
ORIGINAL_VERTS = 16  # 生成時の頂点数。これ以降が人間の追加頂点


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s02_human.blend"))
    obj = bpy.data.objects["Face"]
    mesh = obj.data
    if obj.mode != "OBJECT":  # 編集モードのまま保存された .blend を開くと編集モードで復元される
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="OBJECT")
    before = [v.co.copy() for v in mesh.vertices]

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()

    plans = []
    for f in list(bm.faces):
        if len(f.verts) == 4:
            continue
        idx = [v.index for v in f.verts]
        ins = [k for k, i in enumerate(idx) if i >= ORIGINAL_VERTS]
        if len(idx) != 6 or len(ins) != 2:
            gates.check(f"想定外の面 {idx}（6角形＋追加頂点2つ以外）", False)
            continue
        i, j = ins
        plans.append((idx, idx[i:j + 1], idx[j:] + idx[:i + 1]))  # 元の巻き順のまま2つの四角形に分ける

    for idx, a, b in plans:
        f = next(f for f in bm.faces if [v.index for v in f.verts] == idx)
        bmesh.ops.delete(bm, geom=[f], context="FACES_ONLY")
        for quad in (a, b):
            bm.faces.new([bm.verts[i] for i in quad])  # 既存の切り込み辺は再利用され、無ければ作られる
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    after = [v.co.copy() for v in mesh.vertices]
    gates.check("頂点の位置を1つも動かしていない", len(before) == len(after) and all((a - b).length == 0 for a, b in zip(before, after)))
    gates.check("頂点数 26（人間の追加分を保持）", len(mesh.vertices) == 26, len(mesh.vertices))
    gates.check("全面が四角形（13枚）", len(mesh.polygons) == 13 and all(len(p.vertices) == 4 for p in mesh.polygons),
                f"{len(mesh.polygons)}面 {sorted({len(p.vertices) for p in mesh.polygons})}")
    bm = bmesh.new()
    bm.from_mesh(mesh)
    counts = {n: sum(1 for e in bm.edges if len(e.link_faces) == n) for n in (0, 1, 2)}
    bm.free()
    gates.check("辺: 境界26（内輪13＋外周13）・内部13・孤立辺0", (counts[1], counts[2], counts[0]) == (26, 13, 0), counts)
    gates.check("面法線がすべて -Y（前）向き", all(p.normal.y < 0 for p in mesh.polygons),
                [round(p.normal.y, 2) for p in mesh.polygons])
    gates.check("モディファイアなし", len(obj.modifiers) == 0)
    gates.check("オイラー数 V-E+F = 0（1つの輪）", len(mesh.vertices) - len(mesh.edges) + len(mesh.polygons) == 0,
                f"V={len(mesh.vertices)} E={len(mesh.edges)} F={len(mesh.polygons)}")

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s02b.blend"), compress=False)
    gates.finish()


main()
