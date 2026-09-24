import os
import subprocess
import concurrent.futures

# 1. ストリームURL取得
cmd = ['python', '-m', 'yt_dlp', '-g', '-f', 'bestvideo[ext=mp4]/bestvideo/best', 'https://www.youtube.com/watch?v=pueKgjxwIyI']
res = subprocess.run(cmd, capture_output=True, text=True)
stream_url = res.stdout.strip().split('\n')[0]
print('Stream URL obtained:', bool(stream_url))

out_dir = 'docs/fusako_26_uv_outer_screenshots'
os.makedirs(out_dir, exist_ok=True)

timestamps = [
    (1, '00:00:20', 'fusako26_01_outer_overview.jpg'),
    (2, '00:00:50', 'fusako26_02_hood_seam_marking.jpg'),
    (3, '00:01:30', 'fusako26_03_hood_unwrap_check.jpg'),
    (4, '00:02:10', 'fusako26_04_string_rectify.jpg'),
    (5, '00:02:45', 'fusako26_05_string_pin_relax.jpg'),
    (6, '00:03:30', 'fusako26_06_body_shoulder_side_seam.jpg'),
    (7, '00:04:15', 'fusako26_07_sleeve_seam_unwrap.jpg'),
    (8, '00:05:00', 'fusako26_08_material_color_assign.jpg'),
    (9, '00:05:45', 'fusako26_09_rib_cuff_unwrap.jpg'),
    (10, '00:06:30', 'fusako26_10_solidify_distortion_check.jpg'),
    (11, '00:07:15', 'fusako26_11_solidify_rim_seam.jpg'),
    (12, '00:08:00', 'fusako26_12_pocket_seam_marking.jpg'),
    (13, '00:08:45', 'fusako26_13_pocket_unwrap_relax.jpg'),
    (14, '00:09:30', 'fusako26_14_inner_shrink_pin_unwrap.jpg'),
    (15, '00:10:15', 'fusako26_15_uv_island_rotation_align.jpg'),
    (16, '00:11:00', 'fusako26_16_zipper_seam_unwrap.jpg'),
    (17, '00:11:45', 'fusako26_17_zipper_straighten_grid.jpg'),
    (18, '00:12:30', 'fusako26_18_hood_lining_unwrap.jpg'),
    (19, '00:13:15', 'fusako26_19_textools_rectify_relax.jpg'),
    (20, '00:14:00', 'fusako26_20_average_island_scale.jpg'),
    (21, '00:14:45', 'fusako26_21_uv_pack_layout_init.jpg'),
    (22, '00:15:30', 'fusako26_22_symmetry_overlap_prep.jpg'),
    (23, '00:16:30', 'fusako26_23_symmetry_overlap_align.jpg'),
    (24, '00:17:30', 'fusako26_24_final_outer_uv_layout.jpg')
]

def extract_shot(item):
    idx, ts, fname = item
    target = os.path.join(out_dir, fname)
    ffmpeg_cmd = [
        'ffmpeg', '-y', '-ss', ts, '-i', stream_url,
        '-vframes', '1', '-q:v', '2', target
    ]
    sub = subprocess.run(ffmpeg_cmd, capture_output=True)
    return idx, fname, os.path.exists(target) and os.path.getsize(target) > 0

with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    results = list(executor.map(extract_shot, timestamps))

for idx, fname, success in sorted(results):
    status = "OK" if success else "FAILED"
    print(f"[{idx:02d}] {fname}: {status}")
