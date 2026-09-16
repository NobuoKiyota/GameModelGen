import bpy

def cleanup_old_telescope(context, target_obj, base_name):
    """望遠鏡の親Root・子パーツ（Tripod, Mount, OTA）を一括完全クリーンアップ"""
    to_delete = set()
    
    # 1. target_obj が子パーツの場合、その最上位ルートを探す
    if target_obj and target_obj.name in context.scene.objects:
        root = target_obj
        while root.parent:
            root = root.parent
        to_delete.add(root)
        for child in root.children_recursive:
            to_delete.add(child)

    # 2. base_name に一致するオブジェクト群（_Tripod, _Mount, _OTA, Empty）も検索して削除
    for o in list(bpy.data.objects):
        if o.name == base_name or o.name.startswith(base_name + "_") or (o.name.startswith("Telescope") and any(k in o.name for k in ("Tripod", "Mount", "OTA"))):
            to_delete.add(o)

    for o in to_delete:
        try:
            if o.name in bpy.data.objects:
                # メッシュデータも削除してメモリリーク防止
                if o.type == 'MESH' and o.data:
                    m = o.data
                    bpy.data.objects.remove(o, do_unlink=True)
                    if m.users == 0:
                        bpy.data.meshes.remove(m)
                else:
                    bpy.data.objects.remove(o, do_unlink=True)
        except Exception:
            pass


def cleanup_old_chibi_character(context, target_obj, base_name):
    """どうぶつの森風キャラクターの親Root・子パーツ（Head, Hair, Outfit, Shoes, Face）を一括完全クリーンアップ"""
    to_delete = set()
    
    if target_obj and target_obj.name in context.scene.objects:
        root = target_obj
        while root.parent:
            root = root.parent
        to_delete.add(root)
        for child in root.children_recursive:
            to_delete.add(child)

    chibi_suffixes = (
        "_Head", "_Hair", "_Hair_Front", "_Hair_Back", "_Eyebrows",
        "_Outfit", "_Shoes", "_Eyes", "_Ears", "_Nose", "_Accessory", "_Root", "_Body"
    )
    for o in list(bpy.data.objects):
        if o.name == base_name or o.name.startswith(base_name + "_") or any(o.name.startswith(base_name + s) for s in chibi_suffixes):
            to_delete.add(o)

    for o in to_delete:
        try:
            if o.name in bpy.data.objects:
                if o.type == 'MESH' and o.data:
                    m = o.data
                    bpy.data.objects.remove(o, do_unlink=True)
                    if m.users == 0:
                        bpy.data.meshes.remove(m)
                else:
                    bpy.data.objects.remove(o, do_unlink=True)
        except Exception:
            pass

