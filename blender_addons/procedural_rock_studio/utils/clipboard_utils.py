import os
import subprocess
import time
import bpy

def save_clipboard_image(dest_dir=r"Z:\MeshCreator\textures\Clipboard"):
    """Windowsのクリップボードから画像または画像ファイルパスを取得"""
    os.makedirs(dest_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    out_png_path = os.path.join(dest_dir, f"clip_{timestamp}.png")

    ps_cmd = f"""Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing; if ([System.Windows.Forms.Clipboard]::ContainsImage()) {{ $img = [System.Windows.Forms.Clipboard]::GetImage(); $img.Save('{out_png_path}', [System.Drawing.Imaging.ImageFormat]::Png); Write-Output 'SAVED:{out_png_path}'; }} elseif ([System.Windows.Forms.Clipboard]::ContainsFileDropList()) {{ $files = [System.Windows.Forms.Clipboard]::GetFileDropList(); foreach ($f in $files) {{ if ($f -match '\\.(png|jpg|jpeg|exr|bmp|webp)$') {{ Write-Output ('FILE:' + $f); break; }} }} }} else {{ Write-Output 'NO_IMAGE'; }}"""

    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=5
        )
        out = res.stdout.strip()
        if out.startswith("SAVED:"):
            target_path = out[len("SAVED:"):].strip()
            if os.path.isfile(target_path):
                return target_path
        elif out.startswith("FILE:"):
            target_path = out[len("FILE:"):].strip()
            if os.path.isfile(target_path):
                return target_path
    except Exception as e:
        print(f"[ClipboardUtils] Error: {e}")

    return None


def get_active_or_latest_dropped_image(context):
    """ドラッグ＆ドロップされたEmpty画像、または最新のBlender内部画像を取得"""
    # 1. 選択中のオブジェクトが Empty Image の場合
    active_obj = context.active_object
    if active_obj and active_obj.type == 'EMPTY' and getattr(active_obj, 'empty_display_type', '') == 'IMAGE':
        img = getattr(active_obj, 'data', None)
        if img and img.filepath:
            path = bpy.path.abspath(img.filepath)
            if os.path.isfile(path):
                return path

    # 2. 選択中のオブジェクトが Mesh でテクスチャ画像を持っている場合
    if active_obj and active_obj.type == 'MESH' and active_obj.active_material:
        mat = active_obj.active_material
        if mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image and node.image.filepath:
                    path = bpy.path.abspath(node.image.filepath)
                    if os.path.isfile(path):
                        return path

    # 3. bpy.data.images の中から最新の有効画像を探す（末尾から逆順探索）
    for img in reversed(bpy.data.images):
        if img.name in ("Render Result", "Viewer Node"):
            continue
        if img.filepath:
            path = bpy.path.abspath(img.filepath)
            if os.path.isfile(path):
                return path

    return None
