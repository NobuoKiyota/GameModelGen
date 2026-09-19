"""
扉破壊アニメ用の Blueprint アクター  BP_<NAME>  を自動作成するスクリプト（UE5.1+ / Python Editor Script Plugin）。

    BP_<NAME>
     ├ Frame            (StaticMesh)      石枠。常に表示
     ├ LeavesIntact     (StaticMesh)      無傷の扉。破壊前に表示
     └ Destruction      (SkeletalMesh)    破壊アニメ。最初は非表示・アニメは停止(Single Node, 非ループ)

これ1つをどのレベルにも置けます。破壊は Blueprint の `Break` 関数（手順書のレシピで4ノード）から:
  LeavesIntact を非表示 → Destruction を表示 → Destruction を再生。
レベルシーケンスでは「Event トラック」のキーで Break を呼べば任意のタイミングで破壊できます
（詳細: docs/UE_DoorDestruction_Guide.md の「Blueprintアクター方式」）。

【重要】作成環境にUEが無いため実機未検証です。Blueprintのグラフノードは Python から作れないため
Break 関数は手動です。各ステップは try/except で囲み、失敗時は手動手順を Output Log に出します。
"""
import os
import traceback

import unreal

# ============================ 設定（ここを編集） ============================
FBX_DIR = r"Z:\MeshCreator\exports\Western_Door_UE"   # Blenderが出力したフォルダ
NAME = "Western_Door"                                   # FBXの接頭辞
CONTENT_DIR = "/Game/DoorDestruction"                   # UE内の保存先
BP_NAME = f"BP_{NAME}"
SKIP_IMPORT = False                                     # 既にインポート済みなら True
# ============================================================================

_failed = []


def log(msg):
    unreal.log(f"[DoorBP] {msg}")


def step(title, manual_hint):
    def deco(fn):
        def wrapper(*a, **k):
            try:
                log(f"--- {title}")
                return fn(*a, **k)
            except Exception as e:  # noqa
                _failed.append((title, manual_hint, str(e)))
                unreal.log_warning(f"[DoorBP] 失敗: {title}: {e}")
                unreal.log_warning(traceback.format_exc())
                return None
        return wrapper
    return deco


def _find_asset(path, class_name):
    for p in unreal.EditorAssetLibrary.list_assets(path, recursive=True, include_folder=False):
        a = unreal.EditorAssetLibrary.load_asset(p)
        if a and a.get_class().get_name() == class_name:
            return a
    return None


def _import_fbx(fbx_path, dest_path, skeletal):
    if not os.path.exists(fbx_path):
        raise FileNotFoundError(fbx_path)
    task = unreal.AssetImportTask()
    task.filename = fbx_path
    task.destination_path = dest_path
    task.automated = True
    task.replace_existing = True
    task.save = False
    ui = unreal.FbxImportUI()
    ui.set_editor_property("import_mesh", True)
    ui.set_editor_property("import_textures", False)
    ui.set_editor_property("import_materials", True)
    ui.set_editor_property("import_as_skeletal", bool(skeletal))
    ui.set_editor_property("import_animations", bool(skeletal))
    ui.set_editor_property("create_physics_asset", False)
    if skeletal:
        ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
        ui.get_editor_property("skeletal_mesh_import_data").set_editor_property("import_morph_targets", False)
    else:
        ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
        ui.get_editor_property("static_mesh_import_data").set_editor_property("combine_meshes", True)
    task.options = ui
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    log(f"imported {os.path.basename(fbx_path)}")


@step("FBXインポート", "Content Browserへ3つのFBXを手動インポート（Destructionは Skeletal Mesh + Import Animations）")
def import_all():
    _import_fbx(os.path.join(FBX_DIR, f"{NAME}_Frame.fbx"), CONTENT_DIR + "/Frame", False)
    _import_fbx(os.path.join(FBX_DIR, f"{NAME}_LeavesIntact.fbx"), CONTENT_DIR + "/LeavesIntact", False)
    _import_fbx(os.path.join(FBX_DIR, f"{NAME}_Destruction.fbx"), CONTENT_DIR + "/Destruction", True)


def _add_component(sub, bp, parent_handle, comp_class, comp_name):
    params = unreal.AddNewSubobjectParams(parent_handle=parent_handle, new_class=comp_class, blueprint_context=bp)
    handle, fail_reason = sub.add_new_subobject(params)
    if str(fail_reason).strip():
        raise RuntimeError(f"add_new_subobject failed: {fail_reason}")
    sub.rename_subobject(handle, unreal.Text(comp_name))
    data = sub.k2_find_subobject_data_from_handle(handle)
    template = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(data)
    return handle, template


@step("Blueprint作成とコンポーネント構成",
      "Content Browserで Actor 継承の Blueprint を作成し、コンポーネントを追加: Frame(StaticMesh) / LeavesIntact(StaticMesh) / "
      "Destruction(SkeletalMesh, Visible=OFF, Animation Mode=Use Animation Asset, Anim to Play=インポートしたAnimSequence, Looping=OFF)")
def build_blueprint():
    frame = _find_asset(CONTENT_DIR + "/Frame", "StaticMesh")
    intact = _find_asset(CONTENT_DIR + "/LeavesIntact", "StaticMesh")
    destruct = _find_asset(CONTENT_DIR + "/Destruction", "SkeletalMesh")
    anim = _find_asset(CONTENT_DIR + "/Destruction", "AnimSequence")
    if not (frame and intact and destruct and anim):
        raise RuntimeError(f"インポート済みアセットが不足: frame={bool(frame)} intact={bool(intact)} "
                           f"destruct={bool(destruct)} anim={bool(anim)}")

    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(BP_NAME, CONTENT_DIR, unreal.Blueprint, factory)
    if bp is None:
        raise RuntimeError(f"{BP_NAME} を作成できません（同名アセットが既にある場合は削除してください）")

    sub = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    root = sub.k2_gather_subobject_data_for_blueprint(bp)[0]

    _, t_frame = _add_component(sub, bp, root, unreal.StaticMeshComponent, "Frame")
    t_frame.set_editor_property("static_mesh", frame)

    _, t_intact = _add_component(sub, bp, root, unreal.StaticMeshComponent, "LeavesIntact")
    t_intact.set_editor_property("static_mesh", intact)

    _, t_dest = _add_component(sub, bp, root, unreal.SkeletalMeshComponent, "Destruction")
    try:
        t_dest.set_editor_property("skeletal_mesh_asset", destruct)   # UE5.1+
    except Exception:
        t_dest.set_editor_property("skeletal_mesh", destruct)
    t_dest.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    data = t_dest.get_editor_property("animation_data")
    data.set_editor_property("anim_to_play", anim)
    data.set_editor_property("saved_looping", False)
    data.set_editor_property("saved_playing", False)
    t_dest.set_editor_property("animation_data", data)
    t_dest.set_editor_property("visible", False)   # 破壊前は非表示（Break で表示）
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_loaded_asset(bp)
    log(f"{BP_NAME} を作成: {CONTENT_DIR}/{BP_NAME}")


def main():
    log("=== 扉破壊 Blueprint 作成開始 ===")
    if not SKIP_IMPORT:
        import_all()
    build_blueprint()
    if _failed:
        unreal.log_warning("=" * 60)
        unreal.log_warning("[DoorBP] 一部のステップが失敗しました。手動で対応してください:")
        for title, hint, err in _failed:
            unreal.log_warning(f"  ✗ {title}\n      原因: {err}\n      手動手順: {hint}")
        unreal.log_warning("詳細: docs/UE_DoorDestruction_Guide.md")
        unreal.log_warning("=" * 60)
    else:
        log(f"=== 完了。{BP_NAME} を開き、手順書の「Break関数」のノードを組んでください（4ノード） ===")


main()
