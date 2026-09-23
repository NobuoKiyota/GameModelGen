"""メッシュのエッジを下絵に重ねたレビュー画像を書き出す（bpy + numpy のみ。エンプティは描画されないため自前で描く）。"""
import bpy
import numpy as np

import common as C


def _load_top_origin(path):
    img = bpy.data.images.load(str(path), check_existing=False)
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1].copy()  # 上原点にする
    bpy.data.images.remove(img)
    return px


def _line(arr, p0, p1, color):
    n = int(max(abs(p1[0] - p0[0]), abs(p1[1] - p0[1]))) + 2
    us = np.linspace(p0[0], p1[0], n)
    vs = np.linspace(p0[1], p1[1], n)
    for u, v in zip(us, vs):
        ui, vi = int(round(u)), int(round(v))
        if 0 <= vi < arr.shape[0] and 0 <= ui < arr.shape[1]:
            arr[vi, ui, :3] = color
            arr[vi, ui, 3] = 1.0


def _dot(arr, p, color, r=2):
    ui, vi = int(round(p[0])), int(round(p[1]))
    arr[max(vi - r, 0):vi + r + 1, max(ui - r, 0):ui + r + 1, :3] = color


def write_overlay(mesh, angle_deg, out_path, crop=None, zoom=1, edge_color=(1.0, 0.1, 0.1)):
    """crop=(u0,v0,u1,v1) を zoom 倍（最近傍）に拡大して保存。"""
    bp = C.BLUEPRINTS
    key = {0: "front", 45: "a45", 90: "side"}[angle_deg]
    arr = _load_top_origin(C.BP_DIR / bp[key]["file"])
    pts = [C.project(v.co, angle_deg) for v in mesh.vertices]
    for e in mesh.edges:
        _line(arr, pts[e.vertices[0]], pts[e.vertices[1]], edge_color)
    for p in pts:
        _dot(arr, p, (1.0, 1.0, 0.0), r=1)
    if crop:
        u0, v0, u1, v1 = crop
        arr = arr[v0:v1, u0:u1]
    if zoom > 1:
        arr = np.repeat(np.repeat(arr, zoom, axis=0), zoom, axis=1)
    h, w = arr.shape[:2]
    img = bpy.data.images.new("overlay_tmp", w, h, alpha=False)
    img.pixels.foreach_set(arr[::-1].ravel())  # 書き込みは下原点
    img.filepath_raw = str(out_path)
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def write_wire_top(mesh, out_path, zoom=2, crop=(112, 112, 912, 912)):
    """真上(Numpad 7)から見たワイヤー: 画像の中心が X=0,Y=0、上が +Y（後ろ）。下絵は無し（灰色の背景に辺と頂点）。"""
    arr = np.ones((C.IMG_PX, C.IMG_PX, 4), dtype=np.float32)
    arr[..., :3] = 0.8
    for gx in range(0, C.IMG_PX, 64):                      # 0.045m ごとの目盛り線
        arr[:, gx, :3] = 0.72
        arr[gx, :, :3] = 0.72
    arr[C.IMG_PX // 2, :, :3] = (0.55, 0.55, 0.9)
    arr[:, C.IMG_PX // 2, :3] = (0.55, 0.9, 0.55)
    pts = [(C.COL0 + v.co.x / C.K, C.COL0 - v.co.y / C.K) for v in mesh.vertices]
    for e in mesh.edges:
        _line(arr, pts[e.vertices[0]], pts[e.vertices[1]], (1.0, 0.1, 0.1))
    for p in pts:
        _dot(arr, p, (1.0, 1.0, 0.0), r=1)
    u0, v0, u1, v1 = crop
    arr = arr[v0:v1, u0:u1]
    if zoom > 1:
        arr = np.repeat(np.repeat(arr, zoom, axis=0), zoom, axis=1)
    h, w = arr.shape[:2]
    img = bpy.data.images.new("top_tmp", w, h, alpha=False)
    img.pixels.foreach_set(arr[::-1].ravel())
    img.filepath_raw = str(out_path)
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def write_wire_angle(mesh, angle_deg, out_path, zoom=1, crop=(112, 112, 912, 912)):
    """任意の視点角（0=正面, 90=左から, 135=左後ろ, 180=後ろ）のワイヤー。下絵は無し。C.project の視点角に従う。"""
    arr = np.ones((C.IMG_PX, C.IMG_PX, 4), dtype=np.float32)
    arr[..., :3] = 0.8
    for gx in range(0, C.IMG_PX, 64):
        arr[:, gx, :3] = 0.72
        arr[gx, :, :3] = 0.72
    pts = [C.project(v.co, angle_deg) for v in mesh.vertices]
    for e in mesh.edges:
        _line(arr, pts[e.vertices[0]], pts[e.vertices[1]], (1.0, 0.1, 0.1))
    for p in pts:
        _dot(arr, p, (1.0, 1.0, 0.0), r=1)
    u0, v0, u1, v1 = crop
    arr = arr[v0:v1, u0:u1]
    if zoom > 1:
        arr = np.repeat(np.repeat(arr, zoom, axis=0), zoom, axis=1)
    h, w = arr.shape[:2]
    img = bpy.data.images.new("wire_tmp", w, h, alpha=False)
    img.pixels.foreach_set(arr[::-1].ravel())
    img.filepath_raw = str(out_path)
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)
