import os
import subprocess
import time

cmd = ['python', '-m', 'yt_dlp', '-g', '-f', 'bestvideo[ext=mp4]/bestvideo/best', 'https://www.youtube.com/watch?v=RB9jILspXBk']
res = subprocess.run(cmd, capture_output=True, text=True)
stream_url = res.stdout.strip().split('\n')[0]
print('Stream URL obtained:', bool(stream_url))

out_dir = 'docs/fusako_28_sp_basics_screenshots'
os.makedirs(out_dir, exist_ok=True)

timestamps = [
    (1, '00:00:20', 'fusako28_01_blender_rename_lattice.jpg'),
    (2, '00:01:40', 'fusako28_02_eye_highlight_mat_split.jpg'),
    (3, '00:02:45', 'fusako28_03_mouth_eye_offset_duplicate.jpg'),
    (4, '00:04:15', 'fusako28_04_blender_fbx_export.jpg'),
    (5, '00:05:00', 'fusako28_05_sp_new_project_import.jpg'),
    (6, '00:05:40', 'fusako28_06_bake_mesh_maps_settings.jpg'),
    (7, '00:06:40', 'fusako28_07_bake_b_key_world_normal_check.jpg'),
    (8, '00:07:35', 'fusako28_08_project_configuration_reload.jpg'),
    (9, '00:08:45', 'fusako28_09_bake_2k_resolution_setup.jpg'),
    (10, '00:09:15', 'fusako28_10_base_color_only_channels.jpg'),
    (11, '00:09:40', 'fusako28_11_uv_space_neighbor_padding.jpg'),
    (12, '00:10:45', 'fusako28_12_external_window_color_picker.jpg'),
    (13, '00:11:30', 'fusako28_13_fill_layer_black_mask_paint.jpg'),
    (14, '00:13:40', 'fusako28_14_symmetry_l_key_blur_filter.jpg'),
    (15, '00:14:45', 'fusako28_15_mesh_wireframe_display.jpg'),
    (16, '00:16:45', 'fusako28_16_polygon_fill_uv_chunk.jpg'),
    (17, '00:18:40', 'fusako28_17_brush_shortcuts_x_key_toggle.jpg'),
    (18, '00:20:30', 'fusako28_18_lazy_mouse_stabilizer_d_key.jpg'),
    (19, '00:22:50', 'fusako28_19_brush_size_texture_alignment_uv.jpg'),
    (20, '00:28:15', 'fusako28_20_airbrush_custom_preset_save.jpg'),
    (21, '00:30:15', 'fusako28_21_alpha_blending_opacity_channel.jpg'),
    (22, '00:32:45', 'fusako28_22_export_template_color_with_alpha.jpg'),
    (23, '00:34:10', 'fusako28_23_texture_export_execution.jpg'),
    (24, '00:35:30', 'fusako28_24_blender_standard_color_alpha_node.jpg')
]

for idx, ts, fname in timestamps:
    target = os.path.join(out_dir, fname)
    if os.path.exists(target) and os.path.getsize(target) > 50000:
        print(f"[{idx:02d}] {fname}: ALREADY EXISTS")
        continue
    
    success = False
    for attempt in range(3):
        ffmpeg_cmd = [
            'ffmpeg', '-y', '-ss', ts, '-i', stream_url,
            '-vframes', '1', '-q:v', '2', target
        ]
        sub = subprocess.run(ffmpeg_cmd, capture_output=True)
        if os.path.exists(target) and os.path.getsize(target) > 50000:
            success = True
            break
        time.sleep(1.5)
    
    print(f"[{idx:02d}] {fname}: {'OK' if success else 'FAILED'}")
    time.sleep(0.5)

print("All ep 28 screenshots extracted!")
