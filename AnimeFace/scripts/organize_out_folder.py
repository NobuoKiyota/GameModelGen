import os
import shutil
import re

out_dir = r"Z:\MeshCreator\AnimeFace\out"

# Subdirectories
dirs = {
    "face_steps": os.path.join(out_dir, "history_face_steps"),
    "hair": os.path.join(out_dir, "history_hair"),
    "previews": os.path.join(out_dir, "history_previews"),
    "renders_test": os.path.join(out_dir, "renders_test"),
}

for d in dirs.values():
    os.makedirs(d, exist_ok=True)

# Keep in root:
keep_files = {
    "teacher_ac_merged_h03.blend",
    "teacher_ac_merged_h03.blend1",
    "teacher_ac_merged_h03 - コピー.blend",
    "teacher_ac_merged_face_hair_human.blend",
    "teacher_ac_merged_face_hair.blend",
    "walk_full_facial_f01.png",
    "walk_full_facial_f12.png",
    "walk_face_f01.png",
    "walk_face_f12.png",
}

moved_counts = {k: 0 for k in dirs}

for fname in os.listdir(out_dir):
    fpath = os.path.join(out_dir, fname)
    if not os.path.isfile(fpath):
        continue
    if fname in keep_files:
        continue

    dest_category = None

    # Face steps: starts with face_s or s01..s18
    if re.match(r"^(face_s|s\d{2})", fname):
        dest_category = "face_steps"
    # Hair: starts with hair_ or h0
    elif re.match(r"^(hair_|h0\d)", fname):
        dest_category = "hair"
    # Old preview blends and their specific renders
    elif re.match(r"^(teacher_ac_preview_|teacher_body_outfit_|teacher_full_preview_|teacher_ac_body_|teacher_vest_|teacher_full_)", fname):
        dest_category = "previews"
    # Other teacher_ac old snapshots/renders
    elif re.match(r"^teacher_ac_(a45|side|front|wire|overlay|fitted|human_modified|pose_test|rig_bones|v03)", fname):
        dest_category = "previews"
    # Test renders and walk cycle frames
    elif re.match(r"^(test_|walk_entire_|walk_loop_test_|walk_final_|walk_fullbody_|walk_side_|walk_face_|teacher_ac_anim_|teacher_ac_smooth_walk_|teacher_ac_merged_|teacher_ac_arm_)", fname):
        dest_category = "renders_test"
    else:
        # Check by extension / general test
        if fname.endswith(".json") or fname.endswith(".png"):
            dest_category = "renders_test"

    if dest_category:
        dest_path = os.path.join(dirs[dest_category], fname)
        shutil.move(fpath, dest_path)
        moved_counts[dest_category] += 1

print("Organized files:")
for cat, count in moved_counts.items():
    print(f"  {cat}: {count} files moved to {dirs[cat]}")

root_files = [f for f in os.listdir(out_dir) if os.path.isfile(os.path.join(out_dir, f))]
print(f"\nRemaining in out root ({len(root_files)} files):")
for f in sorted(root_files):
    print(f"  {f}")
