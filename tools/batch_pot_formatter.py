"""
Game Texture POT (Power of Two) Batch Formatter
Usage:
  blender.exe --background --python batch_pot_formatter.py -- [input_folder] [target_size]

Examples:
  blender --background --python batch_pot_formatter.py -- "Z:\MeshCreator\textures\Rock" 512
"""

import sys
import os

# Target POT sizes
POT_SIZES = [64, 128, 256, 512, 1024, 2048, 4096]

def get_nearest_pot(w, h):
    avg = (w + h) / 2.0
    return min(POT_SIZES, key=lambda x: abs(x - avg))

def format_textures_in_folder(folder_path, fixed_size=None):
    import bpy
    
    if not os.path.exists(folder_path):
        print(f"Error: Folder not found: {folder_path}")
        return

    valid_exts = ('.png', '.jpg', '.jpeg', '.tga', '.tif', '.bmp', '.webp')
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_exts)]
    
    print(f"=== Formatting {len(files)} textures in: {folder_path} ===")
    
    out_folder = os.path.join(folder_path, "formatted_pot")
    os.makedirs(out_folder, exist_ok=True)

    for f in files:
        full_path = os.path.join(folder_path, f)
        try:
            img = bpy.data.images.load(full_path, check_existing=False)
            orig_w, orig_h = img.size[0], img.size[1]
            
            target = fixed_size if fixed_size else get_nearest_pot(orig_w, orig_h)
            
            # Scale image in Blender
            img.scale(target, target)
            
            base_name, ext = os.path.splitext(f)
            out_file_name = f"{base_name}_{target}x{target}{ext}"
            out_full_path = os.path.join(out_folder, out_file_name)
            
            img.filepath_raw = out_full_path
            img.file_format = 'PNG' if ext.lower() == '.png' else 'JPEG'
            img.save()
            
            print(f"-> Formatted: {f} ({orig_w}x{orig_h}) ===> {out_file_name} ({target}x{target})")
            
            bpy.data.images.remove(img)
        except Exception as e:
            print(f"Error processing {f}: {e}")

    print(f"=== All formatted textures saved to: {out_folder} ===")

if __name__ == "__main__":
    args = sys.argv
    input_folder = r"Z:\MeshCreator\textures\Rock"
    target_size = None
    
    if "--" in args:
        user_args = args[args.index("--") + 1:]
        if len(user_args) >= 1:
            input_folder = user_args[0]
        if len(user_args) >= 2:
            target_size = int(user_args[1])
            
    format_textures_in_folder(input_folder, target_size)
