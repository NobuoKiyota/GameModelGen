import bpy
import inspect
import importlib

lines = []

# 1. どのファイルから読み込まれているか
from procedural_rock_studio.generators import chibi_char_gen
lines.append("=== Loaded module file ===")
lines.append(str(chibi_char_gen.__file__))

# 2. 今のコードに今日の修正が入っているか（文字列存在チェック）
src = inspect.getsource(chibi_char_gen)
lines.append("")
lines.append("=== Fix markers present in the RUNNING module? ===")
lines.append("compute_chibi_body_layout: " + str("compute_chibi_body_layout" in src))
lines.append("place_ellipsoid (new eyes): " + str("place_ellipsoid" in src))
lines.append("OLD ear box-cutoff (should be False): " + str("abs(norm_x) > 0.46" in src))

# 3. 強制リロードしてから、実際に髪メッシュを1個生成して穴のサイズを直接測る
importlib.reload(chibi_char_gen)
test_hair = chibi_char_gen.build_chibi_hair_mesh(
    bpy.context, "DiagnoseHair", "BOY", "SHORT", (0, 0, 0.72), (0.48, 0.42, 0.40)
)

import bmesh
bm = bmesh.new()
bm.from_mesh(test_hair.data)
boundary_edges = [e for e in bm.edges if len(e.link_faces) == 1]
xs = [v.co.x for e in boundary_edges for v in e.verts]
lines.append("")
lines.append("=== Freshly generated test hair mesh (this run) ===")
lines.append("Boundary edge count: " + str(len(boundary_edges)))
lines.append("Boundary vertex X range: " + str((min(xs), max(xs)) if xs else None))

bm.free()
bpy.data.objects.remove(test_hair, do_unlink=True)

# 4. 実際に使われているBlenderの実行ファイルパスも記録
import sys
lines.append("")
lines.append("=== Blender executable / version ===")
lines.append(sys.executable if hasattr(sys, 'executable') else "unknown")
lines.append(bpy.app.version_string)

out_path = r"Z:\MeshCreator\diagnose_result.txt"
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Diagnosis written to:", out_path)
