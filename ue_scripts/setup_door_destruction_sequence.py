"""
Blender(procedural_rock_studio) が出力した扉破壊アニメ用FBX 3点を、Unreal Engine 5 のエディタへ
自動セットアップするスクリプト。

    <FBX_DIR>/<NAME>_Frame.fbx         石枠 (Static Mesh)
    <FBX_DIR>/<NAME>_LeavesIntact.fbx  無傷の扉 (Static Mesh)  ← 破壊前の見た目
    <FBX_DIR>/<NAME>_Destruction.fbx   破壊アニメ (Skeletal Mesh + ボーンアニメ)  ← 破壊後

実行内容:
  1. 3つのFBXをインポート
  2. レベルにアクターを配置
  3. レベルシーケンスを作成し、破壊開始時刻に
       - Destruction のアニメーショントラックを開始
       - LeavesIntact を非表示 / Destruction を表示 に切り替え
     を設定

使い方:
  UEエディタで  Edit > Plugins > "Python Editor Script Plugin" を有効化(要再起動)。
  Output Log の Cmd を「Python」にして  py "<このファイルのフルパス>"  を実行、
  もしくは  File > Execute Python Script...  から選択。

【重要】このスクリプトは作成環境にUEが無いため、実機では未検証です。UEのPython APIは
バージョン差が大きいので、各ステップを個別に try/except で囲み、失敗したステップと
手動での代替手順を Output Log に出力します。エラー内容(Output Log)を共有してもらえれば修正します。
手動手順は docs/UE_DoorDestruction_Guide.md にあります。
"""
import math
import os
import traceback

import unreal

# ============================ 設定（ここを編集） ============================
FBX_DIR = r"Z:\MeshCreator\exports\Western_Door_UE"   # Blenderが出力したフォルダ
NAME = "Western_Door"                                   # FBXの接頭辞（<NAME>_Frame.fbx の <NAME>）
CONTENT_DIR = "/Game/DoorDestruction"                   # UE内の保存先
SEQUENCE_NAME = "LS_DoorDestruction"
DESTROY_TIME_SEC = 2.0                                  # 破壊を開始する時刻(秒) ← 任意に変更
FPS = 24                                                # Blenderのシーンfps（既定24）に合わせる
TAIL_SEC = 3.0                                          # 破壊後にシーケンスを延長する秒数（最終姿勢を保持）
ACTOR_LOCATION = unreal.Vector(0.0, 0.0, 0.0)           # 扉の配置位置(cm)
ACTOR_ROTATION = unreal.Rotator(0.0, 0.0, 0.0)
# ============================================================================

_failed = []


def log(msg):
    unreal.log(f"[DoorDestruction] {msg}")


def step(title, manual_hint):
    """ステップ実行用デコレータ。失敗しても後続を続け、最後に手動対応をまとめて表示する。"""
    def deco(fn):
        def wrapper(*args, **kwargs):
            try:
                log(f"--- {title}")
                return fn(*args, **kwargs)
            except Exception as e:  # noqa
                _failed.append((title, manual_hint, str(e)))
                unreal.log_warning(f"[DoorDestruction] 失敗: {title}: {e}")
                unreal.log_warning(traceback.format_exc())
                return None
        return wrapper
    return deco


def _list_assets(path):
    return unreal.EditorAssetLibrary.list_assets(path, recursive=True, include_folder=False)


def _find_asset(path, class_name):
    for p in _list_assets(path):
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
    ui.set_editor_property("import_materials", True)      # スロット名どおりの空マテリアルが作られる
    ui.set_editor_property("import_as_skeletal", bool(skeletal))
    ui.set_editor_property("import_animations", bool(skeletal))
    ui.set_editor_property("create_physics_asset", False)  # 破片数ぶんの物理ボディは不要
    if skeletal:
        ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
        sk = ui.get_editor_property("skeletal_mesh_import_data")
        sk.set_editor_property("import_morph_targets", False)
        sk.set_editor_property("update_skeleton_reference_pose", False)
    else:
        ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
        st = ui.get_editor_property("static_mesh_import_data")
        st.set_editor_property("combine_meshes", True)
    task.options = ui
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    imported = list(task.get_editor_property("imported_object_paths"))
    log(f"imported {os.path.basename(fbx_path)} -> {imported}")
    return imported


def _spawn(asset, label):
    try:
        sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        actor = sub.spawn_actor_from_object(asset, ACTOR_LOCATION, ACTOR_ROTATION)
    except Exception:
        actor = unreal.EditorLevelLibrary.spawn_actor_from_object(asset, ACTOR_LOCATION, ACTOR_ROTATION)
    actor.set_actor_label(label)
    return actor


def _asset_length_sec(anim):
    for getter in ("get_play_length", "get_editor_property"):
        try:
            if getter == "get_play_length":
                return float(anim.get_play_length())
            return float(anim.get_editor_property("sequence_length"))
        except Exception:
            continue
    raise RuntimeError("アニメーション長を取得できませんでした")


@step("FBXインポート", "Content Browserへ3つのFBXを手動でインポート（Destructionは Skeletal Mesh + Import Animations）。docs/UE_DoorDestruction_Guide.md 参照")
def import_all():
    dest = CONTENT_DIR
    _import_fbx(os.path.join(FBX_DIR, f"{NAME}_Frame.fbx"), dest + "/Frame", skeletal=False)
    _import_fbx(os.path.join(FBX_DIR, f"{NAME}_LeavesIntact.fbx"), dest + "/LeavesIntact", skeletal=False)
    _import_fbx(os.path.join(FBX_DIR, f"{NAME}_Destruction.fbx"), dest + "/Destruction", skeletal=True)


@step("インポート結果の寸法チェック", "扉が極端に大きい/小さい場合は、FBXインポート時の Import Uniform Scale を調整（100倍ずれる場合は 0.01 / 100）")
def check_sizes():
    for sub, cls in (("Frame", "StaticMesh"), ("LeavesIntact", "StaticMesh"), ("Destruction", "SkeletalMesh")):
        a = _find_asset(f"{CONTENT_DIR}/{sub}", cls)
        if a:
            b = a.get_bounds()
            log(f"{sub}: bounds extent(cm) = {b.box_extent}  （扉の高さは 約 2*Z 。300〜400cm前後になっていれば単位OK）")
        else:
            unreal.log_warning(f"[DoorDestruction] {sub} の {cls} が見つかりません")


@step("アクター配置", "Content Browserから Frame / LeavesIntact(StaticMesh) と Destruction(SkeletalMesh) をレベルへドラッグ配置（位置は全て同じ）")
def spawn_actors():
    frame = _find_asset(CONTENT_DIR + "/Frame", "StaticMesh")
    intact = _find_asset(CONTENT_DIR + "/LeavesIntact", "StaticMesh")
    destruct = _find_asset(CONTENT_DIR + "/Destruction", "SkeletalMesh")
    return {
        "frame": _spawn(frame, "Door_Frame"),
        "intact": _spawn(intact, "Door_LeavesIntact"),
        "destruct": _spawn(destruct, "Door_Destruction"),
    }


def _frames(sec):
    return int(round(sec * FPS))


@step("レベルシーケンス作成", "Content Browserで Cinematics > Level Sequence を作成し、3つのアクターを追加")
def create_sequence():
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    seq = asset_tools.create_asset(SEQUENCE_NAME, CONTENT_DIR, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
    seq.set_display_rate(unreal.FrameRate(FPS, 1))
    return seq


def _add_visibility_track(seq, actor, hidden_before, switch_frame, end_frame, title):
    """actorを switch_frame 以前は hidden_before、以降は反転 にする（Actor Hidden In Game トラック）"""
    binding = seq.add_possessable(actor)
    track = binding.add_track(unreal.MovieSceneVisibilityTrack)
    try:
        track.set_property_name_and_path("bHidden", "bHidden")
    except Exception:
        pass
    section = track.add_section()
    section.set_range(0, end_frame)
    ch = section.get_channels()[0]
    ch.set_default(hidden_before)
    ch.add_key(unreal.FrameNumber(switch_frame), not hidden_before)
    log(f"{title}: 表示切替を frame {switch_frame} に設定")
    return binding


@step("破壊タイミングのトラック設定",
      "レベルシーケンスで Destruction に Animation トラックを追加し、アニメを破壊時刻に配置。"
      "LeavesIntact と Destruction に「Actor Hidden In Game」(Visibility)トラックを追加して破壊時刻で切替")
def build_tracks(seq, actors):
    destroy_f = _frames(DESTROY_TIME_SEC)
    anim = _find_asset(CONTENT_DIR + "/Destruction", "AnimSequence")
    if anim is None:
        raise RuntimeError("Destruction の AnimSequence が見つかりません（FBX内アニメが取り込めていない可能性）")
    anim_frames = int(math.ceil(_asset_length_sec(anim) * FPS))
    end_frame = destroy_f + anim_frames + _frames(TAIL_SEC)
    seq.set_playback_start(0)
    seq.set_playback_end(end_frame)

    # 静的アクター（枠と無傷の扉）と破壊メッシュをシーケンスに追加
    seq.add_possessable(actors["frame"])

    # 破壊メッシュ: アニメを破壊時刻から配置（末尾までセクションを伸ばして最終姿勢を保持）
    d_binding = seq.add_possessable(actors["destruct"])
    a_track = d_binding.add_track(unreal.MovieSceneSkeletalAnimationTrack)
    a_section = a_track.add_section()
    a_section.set_range(destroy_f, end_frame)
    params = a_section.get_editor_property("params")
    params.set_editor_property("animation", anim)
    a_section.set_editor_property("params", params)
    log(f"Destruction アニメを frame {destroy_f} ({DESTROY_TIME_SEC}s) から配置（セクション終端 {end_frame}）")

    # 破壊前: LeavesIntact表示 / Destruction非表示 → 破壊時刻で反転
    _add_visibility_track(seq, actors["intact"], hidden_before=False, switch_frame=destroy_f, end_frame=end_frame,
                          title="LeavesIntact(破壊後に非表示)")
    # Destruction は上で d_binding を作成済みなので、同じバインディングへVisibilityトラックを追加
    track = d_binding.add_track(unreal.MovieSceneVisibilityTrack)
    try:
        track.set_property_name_and_path("bHidden", "bHidden")
    except Exception:
        pass
    section = track.add_section()
    section.set_range(0, end_frame)
    ch = section.get_channels()[0]
    ch.set_default(True)
    ch.add_key(unreal.FrameNumber(destroy_f), False)
    log("Destruction: 破壊時刻まで非表示 → 以降表示")


def main():
    log("=== 扉破壊アニメ セットアップ開始 ===")
    import_all()
    check_sizes()
    actors = spawn_actors()
    seq = create_sequence()
    if seq is not None and actors:
        build_tracks(seq, actors)
    try:
        unreal.EditorAssetLibrary.save_directory(CONTENT_DIR)
    except Exception:
        pass
    if _failed:
        unreal.log_warning("=" * 60)
        unreal.log_warning("[DoorDestruction] 一部のステップが失敗しました。以下を手動で対応してください:")
        for title, hint, err in _failed:
            unreal.log_warning(f"  ✗ {title}\n      原因: {err}\n      手動手順: {hint}")
        unreal.log_warning("詳細手順: docs/UE_DoorDestruction_Guide.md")
        unreal.log_warning("=" * 60)
    else:
        log("=== 完了。Content Browser の " + f"{CONTENT_DIR}/{SEQUENCE_NAME} を開き、Destruction のアニメーションセクションを"
            "左右にドラッグすると破壊タイミングを変更できます ===")


main()
