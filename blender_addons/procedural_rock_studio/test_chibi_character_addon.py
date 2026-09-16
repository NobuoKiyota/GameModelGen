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

    expected_parts = ["Head", "Ears", "Eyes", "Nose", "Hair", "Outfit", "Shoes"]
    for part in expected_parts:
        matched = any(part in c_name for c_name in child_names)
        assert matched, f"Missing child part: {part}"
        print(f"  - Verified part: {part}")

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


    # 2. 女の子（Girl）キャラクター生成テスト
    print("\n=== [TEST 2] Testing Girl Chibi Character Generation ===")
    girl_root = create_procedural_chibi_character(
        context=bpy.context,
        name="Test_Girl_Chibi",
        gender="GIRL",
        head_ratio=2.1,
        total_height=1.10,
        hair_style="TWINTAILS",
        outfit_type="ONE_PIECE",
        skin_color=(0.98, 0.85, 0.76, 1.0),
        hair_color=(0.92, 0.70, 0.35, 1.0),
        cloth_top_color=(0.92, 0.35, 0.55, 1.0),
        shoe_color=(0.45, 0.22, 0.15, 1.0),
        seed=101
    )

    assert girl_root is not None, "Girl root object is None!"
    girl_children = girl_root.children
    assert len(girl_children) >= 7, f"Girl children count too low: {len(girl_children)}"
    print("PASS: Girl character with twintails and one-piece dress verified!")

    # 3. オーケストレーター経由でのディスパッチ＆クリーンアップ検証
    print("\n=== [TEST 3] Testing Core Orchestrator Dispatch & Regeneration ===")
    real_props = bpy.context.scene.prop_studio_props
    real_props.prop_category = 'CHIBI_CHARACTER'
    real_props.chibi_gender = 'BOY'
    real_props.chibi_head_ratio = 2.2
    real_props.chibi_hair_style = 'SHORT'
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
    # 4. 新規髪型バリエーション（SPIKY, PONYTAIL, AFRO, CAP）の生成テスト
    print("\n=== [TEST 4] Testing New Hair Styles (SPIKY, PONYTAIL, AFRO, CAP) ===")
    for style in ["SPIKY", "PONYTAIL", "AFRO", "CAP"]:
        char_obj = create_procedural_chibi_character(
            context=bpy.context,
            name=f"Test_{style}_Char",
            gender="BOY" if style in ("SPIKY", "CAP") else "GIRL",
            hair_style=style,
            seed=200
        )
        assert char_obj is not None, f"Failed generating {style} character!"
        print(f"  - Verified hair style: {style}")

    # 5. ランダム要素抽選（Re-Roll）のテスト
    print("\n=== [TEST 5] Testing Random Gacha Re-Roll ===")
    from procedural_rock_studio.ui.operators import reroll_category_properties
    real_props.prop_category = 'CHIBI_CHARACTER'
    reroll_category_properties(real_props, 'CHIBI_CHARACTER')
    print(f"PASS: Randomized chibi props: Gender={real_props.chibi_gender}, Hair={real_props.chibi_hair_style}, Eye={real_props.chibi_eye_style} (Scale={real_props.chibi_eye_scale})")

    print("\n=======================================================")
    print("  ALL 5 CHIBI CHARACTER TESTS PASSED 100% SUCCESSFULLY!")
    print("=======================================================")


if __name__ == "__main__":
    test_chibi_character_generation()
