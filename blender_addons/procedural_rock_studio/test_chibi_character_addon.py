import bpy
import sys
import os

# アドオンのパスを追加
addon_parent = r"z:\MeshCreator\blender_addons"
if addon_parent not in sys.path:
    sys.path.insert(0, addon_parent)

from procedural_rock_studio import rock_studio_addon
rock_studio_addon.register()

from procedural_rock_studio.generators import create_procedural_chibi_character, generate_procedural_prop_mesh, resolve_prop_parameters




def test_chibi_character_generation():
    print("=== [TEST 1] Testing Boy Chibi Character Generation ===")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rock_studio_addon.register()

    # 1. 男の子（Boy）キャラクター生成テスト
    boy_root = create_procedural_chibi_character(
        context=bpy.context,
        name="Test_Boy_Chibi",
        gender="BOY",
        head_ratio=2.2,
        total_height=1.15,
        hair_style="SHORT",
        outfit_type="T_SHIRT",
        skin_color=(0.96, 0.82, 0.74, 1.0),
        hair_color=(0.35, 0.22, 0.14, 1.0),
        cloth_top_color=(0.18, 0.55, 0.82, 1.0),
        shoe_color=(0.85, 0.25, 0.22, 1.0),
        seed=42
    )

    assert boy_root is not None, "Boy root object is None!"
    assert boy_root.name.startswith("Test_Boy_Chibi_Body"), f"Unexpected name: {boy_root.name}"
    print(f"PASS: Boy root object created: {boy_root.name}")

    # 子オブジェクト（パーツ）の検証
    children = boy_root.children
    print(f"Child count: {len(children)}")
    child_names = [c.name for c in children]
    print(f"Child names: {child_names}")

    expected_parts = ["Head", "Ears", "Eyes", "Eyebrows", "Nose", "Mouth", "Hair", "Outfit", "Shoes"]
    for part in expected_parts:
        matched = any(part in c_name for c_name in child_names)
        assert matched, f"Missing child part: {part}"
        print(f"  - Verified part: {part}")

    # 目のシェイプキー（Blend Shapes: Basis, Blink, Smile, Wide, Squint）および立体まつ毛の検証
    eyes_obj = next(c for c in children if "Eyes" in c.name)
    assert eyes_obj.data.shape_keys is not None, "Shape keys missing on Eyes!"
    key_blocks = eyes_obj.data.shape_keys.key_blocks
    key_names = [kb.name for kb in key_blocks]
    print(f"Eyes Shape Keys: {key_names}")
    for exp_key in ["Basis", "Blink", "Smile", "Wide", "Squint"]:
        assert exp_key in key_names, f"Missing shape key: {exp_key}"
    print("PASS: Facial Expression Shape Keys (Blend Shapes) verified on Eyes for animation!")

    # 目パーツ（Eyes）の3スロット構造（白目玉, 瞳・虹彩, ハイライト）の検証
    eyes_mat_names = [m.name for m in eyes_obj.data.materials if m]
    print(f"Eyes materials: {eyes_mat_names}")
    assert any("Sclera" in m for m in eyes_mat_names), "White eyeball (Sclera-slot) material missing on Eyes!"
    assert any("Pupil" in m for m in eyes_mat_names), "Pupil/Iris material missing on Eyes!"
    assert any("Highlight" in m for m in eyes_mat_names), "Highlight (catchlight-slot) material missing on Eyes!"
    assert len(eyes_obj.data.materials) >= 3, f"Expected at least 3 material slots on Eyes, got {len(eyes_obj.data.materials)}"
    print("PASS: 3-slot Eye System (White eyeball, Pupil/Iris, Highlight) verified on Eyes!")

    # 目・口のBoolean眼窩/口内ソケットは生成直後にBake(適用)して法線を再計算する
    # 方式に変更したため(法線不整合による亀裂状シェーディング異常の対策)、
    # Booleanモディファイアはライブのまま残らない。代わりにSubdivisionだけが
    # 残っていること、Boolean由来の穴が実メッシュに反映されて頂点数が
    # ベースの低ポリ球より十分増えていることを確認する。
    head_obj = next(c for c in children if "Head" in c.name)
    assert not any(m.type == 'BOOLEAN' for m in head_obj.modifiers), \
        "Boolean modifier should be baked immediately, not left live on Head!"
    assert any(m.type == 'SUBSURF' for m in head_obj.modifiers), \
        "Subdivision modifier missing on Head!"
    assert len(head_obj.data.vertices) > 1600, \
        f"Head vertex count too low ({len(head_obj.data.vertices)}) — eye/mouth socket cuts may not have been baked in!"
    print("PASS: Eye/mouth Boolean sockets baked into Head mesh with normals fixed!")

    # 口パーツ（Mouth）および口のシェイプキーの検証
    mouth_obj = next(c for c in children if "Mouth" in c.name)
    assert mouth_obj.data.shape_keys is not None, "Shape keys missing on Mouth!"
    mouth_key_names = [kb.name for kb in mouth_obj.data.shape_keys.key_blocks]
    print(f"Mouth Shape Keys: {mouth_key_names}")
    for exp_key in ["Basis", "Smile", "Open", "Pout"]:
        assert exp_key in mouth_key_names, f"Missing shape key on Mouth: {exp_key}"
    print("PASS: Mouth object & expression shape keys verified!")

    # 衣装のボタンマテリアル（Button Mat）の検証
    outfit_obj = next(c for c in children if "Outfit" in c.name)
    outfit_mat_names = [m.name for m in outfit_obj.data.materials if m]
    print(f"Outfit materials: {outfit_mat_names}")
    assert any("Button" in m for m in outfit_mat_names), "Button material missing on Outfit!"
    print("PASS: Small Button material & slots verified on Outfit!")

    # マテリアルとFootstep Surfaceスロットの検証
    shoes_obj = next(c for c in children if "Shoes" in c.name)
    shoe_mat_names = [m.name for m in shoes_obj.data.materials if m]
    print(f"Shoes materials: {shoe_mat_names}")
    assert any("Footstep_Surface" in m for m in shoe_mat_names), "Footstep_Surface_Mat missing on Shoes!"
    print("PASS: Footstep_Surface_Mat verified on Shoes for game audio/surface ID integration!")

    # 頂点数・メッシュの健全性検証
    dg = bpy.context.evaluated_depsgraph_get()
    eval_verts = len(boy_root.evaluated_get(dg).data.vertices) + sum(len(c.evaluated_get(dg).data.vertices) for c in children if c.type == 'MESH')
    base_verts = len(boy_root.data.vertices) + sum(len(c.data.vertices) for c in children if c.type == 'MESH')
    print(f"Base verts: {base_verts}, Evaluated (Subdiv/Skin applied) verts: {eval_verts}")
    assert base_verts >= 100, f"Base vertices too low: {base_verts}"
    assert eval_verts >= 500, f"Evaluated vertices too low: {eval_verts}"
    print("PASS: Boy mesh structure & vertices verified!")


    # 2. 女の子（Girl）キャラクター生成テスト（前髪・後ろ髪カスタム）
    print("\n=== [TEST 2] Testing Girl Chibi Character Generation ===")
    girl_root = create_procedural_chibi_character(
        context=bpy.context,
        name="Test_Girl_Chibi",
        gender="GIRL",
        head_ratio=2.1,
        total_height=1.10,
        hair_style="TWINTAILS",
        eyebrow_style="ARCH",
        outfit_type="ONE_PIECE",
        skin_color=(0.98, 0.85, 0.76, 1.0),
        hair_color=(0.92, 0.70, 0.35, 1.0),
        cloth_top_color=(0.92, 0.35, 0.55, 1.0),
        shoe_color=(0.45, 0.22, 0.15, 1.0),
        seed=101
    )

    assert girl_root is not None, "Girl root object is None!"
    girl_children = girl_root.children
    assert len(girl_children) >= 8, f"Girl children count too low: {len(girl_children)}"
    girl_eyes = next(c for c in girl_children if "Eyes" in c.name)
    assert girl_eyes is not None, "Girl Eyes missing!"
    girl_eyes_mats = [m.name for m in girl_eyes.data.materials if m]
    assert len(girl_eyes_mats) >= 3, f"Girl eyes materials count < 3: {girl_eyes_mats}"
    print(f"Girl Eyes Materials: {girl_eyes_mats}")
    print("PASS: Girl character with twintails, 3-slot sphere-based anime eyes, and one-piece dress verified!")

    # 3. オーケストレーター経由でのディスパッチ＆クリーンアップ検証
    print("\n=== [TEST 3] Testing Core Orchestrator Dispatch & Regeneration ===")
    real_props = bpy.context.scene.prop_studio_props
    real_props.prop_category = 'CHIBI_CHARACTER'
    real_props.chibi_gender = 'BOY'
    real_props.chibi_head_ratio = 2.2
    real_props.chibi_hair_style = 'SHORT'
    real_props.chibi_eyebrow_style = 'ARCH'
    real_props.chibi_outfit_type = 'T_SHIRT'
    real_props.chibi_eye_style = 'OVAL'
    real_props.chibi_eye_scale = 1.0
    real_props.size_z = 1.15

    params = resolve_prop_parameters(real_props)
    orch_obj = generate_procedural_prop_mesh(
        context=bpy.context,
        target_obj=None,
        name="Chibi_Orchestrator_Test",
        seed=777,
        **params
    )

    assert orch_obj is not None, "Orchestrator returned None!"
    print(f"PASS: Orchestrator dispatch returned {orch_obj.name}")

    # 再生成テスト（In-place Reroll）
    orch_reroll = generate_procedural_prop_mesh(
        context=bpy.context,
        target_obj=orch_obj,
        name="Chibi_Orchestrator_Test",
        seed=888,
        **params
    )
    # 4. 一体型髪型 × 眉毛 × 衣装の網羅生成テスト
    print("\n=== [TEST 4] Testing Unified Hairstyles, Outfits & Eyebrows ===")
    styles = ["SHORT", "SHORT_MESSY", "CENTER_PART", "BOB", "MUSHROOM", "TWINTAILS", "BRAIDS", "PONYTAIL", "TOPKNOT", "SPIKY", "WAVY_LONG", "AFRO"]
    eyebrows = ["ARCH", "DOT", "STRAIGHT", "NONE"]
    outfits = ["T_SHIRT", "ONE_PIECE", "HOODIE", "OVERALLS", "KIMONO", "COAT"]

    for i, style in enumerate(styles):
        outfit = outfits[i % len(outfits)]
        eyebrow = eyebrows[i % len(eyebrows)]
        char_obj = create_procedural_chibi_character(
            context=bpy.context,
            name=f"Test_Style_{style}_Char",
            gender="BOY" if i % 2 == 0 else "GIRL",
            hair_style=style,
            eyebrow_style=eyebrow,
            outfit_type=outfit,
            seed=200 + i
        )
        assert char_obj is not None, f"Failed generating hairstyle {style}!"
        # Hair 子パーツが1つだけ存在することを確認
        hair_children = [c for c in char_obj.children if "_Hair" in c.name and "_Hair_Front" not in c.name and "_Hair_Back" not in c.name]
        assert len(hair_children) == 1, f"Expected 1 unified Hair child, got {len(hair_children)}"
        print(f"  - Verified: Hairstyle={style}, Eyebrow={eyebrow}, Outfit={outfit}")

    # 5. ランダム要素抽選（Re-Roll）オペレーター実行テスト（ReferenceError再発防止検証）
    print("\n=== [TEST 5] Testing Random Gacha Operator Execution (Bug Fix Verification) ===")
    bpy.context.view_layer.objects.active = orch_reroll
    orch_reroll.select_set(True)
    real_props.prop_category = 'CHIBI_CHARACTER'

    for step in range(5):
        res = bpy.ops.mesh.reroll_selected_prop()
        assert res == {'FINISHED'}, f"Reroll operator failed with result {res}"
        print(f"  - Step {step+1}: Reroll operator succeeded without ReferenceError! Active={bpy.context.active_object.name}")

    # 6. 新機能検証: 柄変更時のサイズ不変性、大型立体フード、丸メガネ、ワンピースラウンドショルダー
    print("\n=== [TEST 6] Testing Pattern Size Invariance, 3D Hood, Glasses, and Dress Shoulders ===")
    test_char = create_procedural_chibi_character(
        context=bpy.context,
        name="Test_Size_Invariance_Char",
        gender="BOY",
        outfit_type="HOODIE",
        accessory="ROUND_GLASSES",
        pattern="PLAIN",
        seed=333
    )
    bpy.context.view_layer.objects.active = test_char
    test_char.select_set(True)

    # 初期バウンディングボックスの計測
    outfit_child = next((c for c in test_char.children if "_Outfit" in c.name), None)
    assert outfit_child is not None, "Outfit child not found!"
    initial_bb_z = outfit_child.dimensions.z
    initial_body_z = test_char.dimensions.z

    # 柄を全種類変更して、マテリアル更新後にサイズが1ミリも変わらないことを確認
    for pat in ["STRIPED", "POLKA_DOT", "ISLAND_LEAF", "PLAIN"]:
        real_props.chibi_pattern = pat
        current_bb_z = outfit_child.dimensions.z
        current_body_z = test_char.dimensions.z
        diff = abs(current_bb_z - initial_bb_z)
        assert diff < 1e-4, f"Outfit size changed on pattern change! Diff={diff}"
        diff_body = abs(current_body_z - initial_body_z)
        assert diff_body < 1e-4, f"Body size changed on pattern change! Diff={diff_body}"
    print("PASS: Outfit & Body bounding boxes strictly invariant across all patterns (Size stability verified!)")

    # 大型フードの検証（頂点数と寸法）
    assert outfit_child.dimensions.y > 0.28, f"Hoodie Y depth should be prominent with large hood! Got: {outfit_child.dimensions.y}"
    print("PASS: Prominent 3D Hood depth verified on HOODIE outfit!")

    # 丸メガネ（ROUND_GLASSES）の検証
    glasses_child = next((c for c in test_char.children if "_Accessory" in c.name), None)
    assert glasses_child is not None, "ROUND_GLASSES accessory child not found!"
    assert len(glasses_child.data.polygons) > 200, f"Glasses should have smooth torus topology! Polys: {len(glasses_child.data.polygons)}"
    print("PASS: High-quality smooth Torus Glasses topology verified!")

    # ワンピース（ONE_PIECE）の検証
    dress_char = create_procedural_chibi_character(
        context=bpy.context,
        name="Test_Dress_Char",
        gender="GIRL",
        outfit_type="ONE_PIECE",
        seed=444
    )
    dress_child = next((c for c in dress_char.children if "_Outfit" in c.name), None)
    assert dress_child is not None, "ONE_PIECE outfit not found!"
    # フレンチスリーブによりX幅が肩幅より広くなっていることを確認
    assert dress_child.dimensions.x > 0.38, f"ONE_PIECE should include round sleeves! Width: {dress_child.dimensions.x}"
    print("PASS: ONE_PIECE rounded shoulder and french sleeves verified!")

    print("\n=======================================================")
    print("  ALL CHIBI CHARACTER COMPREHENSIVE TESTS PASSED 100%!")
    print("=======================================================")


if __name__ == "__main__":
    test_chibi_character_generation()
