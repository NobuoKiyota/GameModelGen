import os
import glob
import re

def get_textures_from_folder(folder_path):
    """フォルダ内の画像テクスチャファイル一覧を取得"""
    if not folder_path or not os.path.exists(folder_path):
        return []
    valid_exts = {'.png', '.jpg', '.jpeg', '.tga', '.exr', '.hdr', '.tif', '.tiff', '.webp'}
    tex_files = []
    try:
        for f in os.listdir(folder_path):
            ext = os.path.splitext(f)[1].lower()
            if ext in valid_exts:
                tex_files.append(f)
    except Exception:
        return []
    return sorted(tex_files)


def find_pbr_texture_set(image_path):
    """指定された画像パスから同一セットのPBRテクスチャ（BaseColor, Normal, Roughness, Disp等）を自動検出"""
    if not image_path or not os.path.exists(image_path):
        return {}
    
    dir_name = os.path.dirname(image_path)
    file_name = os.path.basename(image_path)
    base_stem, _ = os.path.splitext(file_name)
    
    # 典型的なサフィックスパターンの除去
    clean_prefix = re.sub(r'[_ -]?(basecolor|albedo|diffuse|diff|col|color|normal|nor|nrm|roughness|rough|disp|displacement|height|heightmap|ao|ambientocclusion|metallic|metalness|specular)$', '', base_stem, flags=re.IGNORECASE)
    
    pbr_set = {}
    valid_exts = {'.png', '.jpg', '.jpeg', '.tga', '.exr', '.hdr', '.tif', '.tiff', '.webp'}
    
    for fname in os.listdir(dir_name):
        ext = os.path.splitext(fname)[1].lower()
        if ext not in valid_exts:
            continue
        full_path = os.path.join(dir_name, fname)
        lower_fname = fname.lower()
        
        # クリーンなプレフィックスで始まるか、または同一ファイル
        if clean_prefix.lower() in lower_fname or fname == file_name:
            if re.search(r'(basecolor|albedo|diffuse|diff|col|_color)', lower_fname):
                pbr_set['base_color'] = full_path
            elif re.search(r'(normal|nor|nrm|_n\b)', lower_fname):
                pbr_set['normal'] = full_path
            elif re.search(r'(roughness|rough|_r\b)', lower_fname):
                pbr_set['roughness'] = full_path
            elif re.search(r'(disp|displacement|height|heightmap)', lower_fname):
                pbr_set['displacement'] = full_path
            elif re.search(r'(metallic|metalness|_m\b)', lower_fname):
                pbr_set['metallic'] = full_path
            elif re.search(r'(ao|ambientocclusion)', lower_fname):
                pbr_set['ao'] = full_path
                
    # fallback
    if 'base_color' not in pbr_set:
        pbr_set['base_color'] = image_path
        
    return pbr_set
