import os
import subprocess
import time

cmd = ['python', '-m', 'yt_dlp', '-g', '-f', 'bestvideo[ext=mp4]/bestvideo/best', 'https://www.youtube.com/watch?v=tayBUmjCFt8']
res = subprocess.run(cmd, capture_output=True, text=True)
stream_url = res.stdout.strip().split('\n')[0]
print('Stream URL obtained:', bool(stream_url))

out_dir = 'docs/fusako_29_sp_face_paint_screenshots'
os.makedirs(out_dir, exist_ok=True)

timestamps = [
    (1, '00:00:20', 'fusako29_01_eye_highlight_hybrid_concept.jpg'),
    (2, '00:00:45', 'fusako29_02_blender_highlight_mesh_duplicate.jpg'),
    (3, '00:01:15', 'fusako29_03_blender_dissolve_edges_proportional.jpg'),
    (4, '00:01:45', 'fusako29_04_blender_separate_p_mirror_apply.jpg'),
    (5, '00:02:20', 'fusako29_05_blender_highlight_uv_export.jpg'),
    (6, '00:03:15', 'fusako29_06_sp_project_configuration_reload.jpg'),
    (7, '00:04:10', 'fusako29_07_eye_base_layer_blur_filter.jpg'),
    (8, '00:05:00', 'fusako29_08_eye_gradual_color_stacking.jpg'),
    (9, '00:06:35', 'fusako29_09_uv_border_generator_eye_rim.jpg'),
    (10, '00:07:35', 'fusako29_10_transparent_mat_m_key_view.jpg'),
    (11, '00:08:35', 'fusako29_11_regular_layer_brush_eraser_toggle.jpg'),
    (12, '00:09:45', 'fusako29_12_eye_body_screen_highlight.jpg'),
    (13, '00:10:20', 'fusako29_13_eraser_airbrush_soft_carve.jpg'),
    (14, '00:11:40', 'fusako29_14_eye_lower_screen_glow_adjust.jpg'),
    (15, '00:12:40', 'fusako29_15_environment_map_studio_neutral.jpg'),
    (16, '00:14:05', 'fusako29_16_highlight_mesh_uv_border_rebake.jpg'),
    (17, '00:15:15', 'fusako29_17_eyelash_symmetry_uv_border.jpg'),
    (18, '00:16:30', 'fusako29_18_eyelash_brush_alignment_uv.jpg'),
    (19, '00:17:35', 'fusako29_19_polygon_fill_eyelash_back.jpg'),
    (20, '00:18:25', 'fusako29_20_tongue_shadow_multiply_layer.jpg'),
    (21, '00:19:35', 'fusako29_21_blur_directional_filter_90deg.jpg'),
    (22, '00:21:15', 'fusako29_22_mouth_throat_shadow_directional.jpg'),
    (23, '00:22:30', 'fusako29_23_view_2d_rotate_alt_shift_snap.jpg'),
    (24, '00:25:10', 'fusako29_24_ear_fur_blur_directional_complete.jpg')
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

print("All ep 29 screenshots extracted!")
