import os
import subprocess
import time

cmd = ['python', '-m', 'yt_dlp', '-g', '-f', 'bestvideo[ext=mp4]/bestvideo/best', 'https://www.youtube.com/watch?v=3a7os-XHBTU']
res = subprocess.run(cmd, capture_output=True, text=True)
stream_url = res.stdout.strip().split('\n')[0]
print('Stream URL obtained:', bool(stream_url))

out_dir = 'docs/fusako_30_sp_hair_paint_screenshots'
os.makedirs(out_dir, exist_ok=True)

timestamps = [
    (1, '00:00:15', 'fusako30_01_hair_paint_intro.jpg'),
    (2, '00:00:30', 'fusako30_02_3d_distance_generator_intro.jpg'),
    (3, '00:00:55', 'fusako30_03_3d_distance_params_adjust.jpg'),
    (4, '00:01:10', 'fusako30_04_top_light_tip_gradient_concept.jpg'),
    (5, '00:01:30', 'fusako30_05_flat_hair_outline_challenge.jpg'),
    (6, '00:02:05', 'fusako30_06_hair_shadow_1_stroke.jpg'),
    (7, '00:02:30', 'fusako30_07_hair_highlight_layer_prep.jpg'),
    (8, '00:02:50', 'fusako30_08_hair_inner_polygon_fill.jpg'),
    (9, '00:03:20', 'fusako30_09_hair_shadow_2_depth.jpg'),
    (10, '00:03:50', 'fusako30_10_shadow_mask_3d_distance_invert.jpg'),
    (11, '00:04:25', 'fusako30_11_shadow_mask_darken_blend.jpg'),
    (12, '00:05:30', 'fusako30_12_flat_hair_uv_border_init.jpg'),
    (13, '00:06:05', 'fusako30_13_uv_border_blur_filter.jpg'),
    (14, '00:06:15', 'fusako30_14_histogram_scan_clean_edge.jpg'),
    (15, '00:07:15', 'fusako30_15_polygon_fill_mask_cleanup.jpg'),
    (16, '00:07:45', 'fusako30_16_multiply_blend_outline_extract.jpg'),
    (17, '00:08:15', 'fusako30_17_hand_painted_line_refinement.jpg'),
    (18, '00:09:30', 'fusako30_18_front_hair_detail_polishing.jpg'),
    (19, '00:10:45', 'fusako30_19_base_hair_3d_distance_gradient.jpg'),
    (20, '00:12:30', 'fusako30_20_front_hair_complete_view.jpg'),
    (21, '00:13:45', 'fusako30_21_back_hair_symmetry_to_asymmetry.jpg'),
    (22, '00:15:30', 'fusako30_22_hair_paint_overall_finishing.jpg'),
    (23, '00:16:50', 'fusako30_23_texture_export_global_settings.jpg'),
    (24, '00:17:50', 'fusako30_24_blender_auto_reload_addon_import.jpg')
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

print("All ep 30 screenshots extracted!")
