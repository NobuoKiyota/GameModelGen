import os
import subprocess
import time

cmd = ['python', '-m', 'yt_dlp', '-g', '-f', 'bestvideo[ext=mp4]/bestvideo/best', 'https://www.youtube.com/watch?v=p4N6kfBLOVc']
res = subprocess.run(cmd, capture_output=True, text=True)
stream_url = res.stdout.strip().split('\n')[0]
print('Stream URL obtained:', bool(stream_url))

out_dir = 'docs/fusako_27_uv_accessories_screenshots'
os.makedirs(out_dir, exist_ok=True)

timestamps = [
    (1, '00:00:30', 'fusako27_01_accessories_material_init.jpg'),
    (2, '00:01:25', 'fusako27_02_ribbon_mirror_seam.jpg'),
    (3, '00:02:25', 'fusako27_03_clip_solidify_single_user.jpg'),
    (4, '00:03:30', 'fusako27_04_clip_shrink_pin_unwrap.jpg'),
    (5, '00:04:30', 'fusako27_05_clip_seam_manual_straighten.jpg'),
    (6, '00:06:40', 'fusako27_06_magic_uv_copy_uv_map.jpg'),
    (7, '00:07:30', 'fusako27_07_magic_uv_paste_uv_map.jpg'),
    (8, '00:08:30', 'fusako27_08_button_tail_seam_unwrap.jpg'),
    (9, '00:09:30', 'fusako27_09_shift_g_select_sharp_edges.jpg'),
    (10, '00:10:45', 'fusako27_10_scale_apply_fix.jpg'),
    (11, '00:11:45', 'fusako27_11_zipper_pin_unwrap.jpg'),
    (12, '00:12:45', 'fusako27_12_zipper_textools_align_join.jpg'),
    (13, '00:14:15', 'fusako27_13_strap_pre_unwrap_straighten.jpg'),
    (14, '00:15:15', 'fusako27_14_strap_solidify_shrink_pin.jpg'),
    (15, '00:16:30', 'fusako27_15_rabbit_pouch_seam_prep.jpg'),
    (16, '00:18:00', 'fusako27_16_rabbit_pouch_shrink_pin_unwrap.jpg'),
    (17, '00:19:40', 'fusako27_17_pouch_strap_rectify_scale.jpg'),
    (18, '00:21:30', 'fusako27_18_pouch_join_inner_s05.jpg'),
    (19, '00:23:30', 'fusako27_19_ribbon_pouch_pack_layout.jpg'),
    (20, '00:25:30', 'fusako27_20_display_stretch_distortion_view.jpg'),
    (21, '00:27:30', 'fusako27_21_shoulder_strap_split_seam.jpg'),
    (22, '00:29:30', 'fusako27_22_canteen_bag_align_orientation.jpg'),
    (23, '00:33:30', 'fusako27_23_scale_match_priority_boost.jpg'),
    (24, '00:38:20', 'fusako27_24_final_all_characters_uv_complete.jpg')
]

# test file cleanup
test_f = os.path.join(out_dir, 'test38.jpg')
if os.path.exists(test_f): os.remove(test_f)

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

print("All done!")
