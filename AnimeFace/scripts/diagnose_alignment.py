import bpy

def inspect_file(filepath):
    print(f"\n==========================================")
    print(f"FILE: {filepath}")
    print(f"==========================================")
    bpy.ops.wm.open_mainfile(filepath=filepath)
    
    # 1. Check BodyBase
    bb = bpy.data.objects.get("BodyBase")
    if bb:
        print(f"[BodyBase]")
        print(f"  hide_viewport: {bb.hide_viewport}, hide_render: {bb.hide_render}, hide_get: {bb.hide_get()}")
        print(f"  location: {bb.location}, rotation: {bb.rotation_euler}, scale: {bb.scale}")
        print(f"  verts: {len(bb.data.vertices)}, polys: {len(bb.data.polygons)}")
        print(f"  modifiers: {[m.name + ' (' + m.type + ')' for m in bb.modifiers]}")
        for m in bb.modifiers:
            if m.type == 'MASK':
                print(f"    Mask: {m.name}, vg={m.vertex_group}, inv={m.invert_vertex_group}, show_vp={m.show_viewport}")
    else:
        print("[BodyBase] NOT FOUND!")

    # 2. Check BodyArm & Armature EditBones
    arm_obj = bpy.data.objects.get("BodyArm")
    armature = bpy.data.objects.get("Armature_Teacher") or bpy.data.objects.get("Armature")
    if arm_obj and armature:
        print(f"\n[BodyArm & Armature alignment]")
        print(f"  BodyArm loc: {arm_obj.location}, scale: {arm_obj.scale}")
        print(f"  Armature loc: {armature.location}, scale: {armature.scale}")
        
        # Check bone heads/tails in world coords vs BodyArm vertex bounds in world coords
        mw_arm = arm_obj.matrix_world
        mw_amt = armature.matrix_world
        
        for bname in ["Shoulder.L", "UpperArm.L", "Forearm.L", "Hand.L"]:
            b = armature.data.bones.get(bname)
            if b:
                head_w = mw_amt @ b.head_local
                tail_w = mw_amt @ b.tail_local
                print(f"  Bone {bname:10s}: head_w={head_w}, tail_w={tail_w}")
                
        # BodyArm vertex bounds per vertex group
        for vg_name in ["Shoulder.L", "UpperArm.L", "Forearm.L", "Hand.L", "Shoulder.R", "UpperArm.R", "Forearm.R", "Hand.R"]:
            vg = arm_obj.vertex_groups.get(vg_name)
            if vg:
                v_cos = [mw_arm @ v.co for v in arm_obj.data.vertices if any(g.group == vg.index and g.weight > 0.1 for g in v.groups)]
                if v_cos:
                    xs = [c.x for c in v_cos]
                    ys = [c.y for c in v_cos]
                    zs = [c.z for c in v_cos]
                    print(f"  Mesh VG {vg_name:10s} ({len(v_cos):2d} v): center=({sum(xs)/len(xs):.3f}, {sum(ys)/len(ys):.3f}, {sum(zs)/len(zs):.3f})")

    # 3. Check Garment alignment: Outfit_Cape, Outfit_Shirt
    for gname in ["Outfit_Cape", "Outfit_Shirt", "Outfit_Sleeves"]:
        g = bpy.data.objects.get(gname)
        if g:
            print(f"\n[{gname}]")
            print(f"  loc: {g.location}, rot: {g.rotation_euler}, scale: {g.scale}")
            print(f"  modifiers: {[m.name for m in g.modifiers]}")
            mw = g.matrix_world
            cos = [mw @ v.co for v in g.data.vertices]
            print(f"  bounds: X=[{min(c.x for c in cos):.3f}, {max(c.x for c in cos):.3f}], Y=[{min(c.y for c in cos):.3f}, {max(c.y for c in cos):.3f}], Z=[{min(c.z for c in cos):.3f}, {max(c.z for c in cos):.3f}]")

inspect_file("Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_face_hair.blend")
inspect_file("Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h04.blend")
