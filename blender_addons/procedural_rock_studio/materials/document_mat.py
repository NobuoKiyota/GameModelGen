import bpy

def create_document_stack_materials(prefix="DocStack"):
    """
    書類の束（コピー紙、クラフト紙、黄ばみ古紙、フォルダー）のマルチマテリアル生成
    """
    # 1. M_Paper_White (コピー用紙・事務書類)
    mat_white = bpy.data.materials.get(f"{prefix}_Paper_White") or bpy.data.materials.new(name=f"{prefix}_Paper_White")
    mat_white.use_nodes = True
    bsdf_w = mat_white.node_tree.nodes.get("Principled BSDF")
    if bsdf_w:
        bsdf_w.inputs['Base Color'].default_value = (0.92, 0.91, 0.88, 1.0) # わずかな温かみのある白
        bsdf_w.inputs['Roughness'].default_value = 0.85

    # 2. M_Paper_Kraft (クラフト紙・茶封筒・厚紙)
    mat_kraft = bpy.data.materials.get(f"{prefix}_Paper_Kraft") or bpy.data.materials.new(name=f"{prefix}_Paper_Kraft")
    mat_kraft.use_nodes = True
    bsdf_k = mat_kraft.node_tree.nodes.get("Principled BSDF")
    if bsdf_k:
        bsdf_k.inputs['Base Color'].default_value = (0.68, 0.48, 0.28, 1.0) # クラフトブラウン
        bsdf_k.inputs['Roughness'].default_value = 0.90

    # 3. M_Paper_Aged (黄ばみ古書類・酸化セピア紙)
    mat_aged = bpy.data.materials.get(f"{prefix}_Paper_Aged") or bpy.data.materials.new(name=f"{prefix}_Paper_Aged")
    mat_aged.use_nodes = True
    bsdf_a = mat_aged.node_tree.nodes.get("Principled BSDF")
    if bsdf_a:
        bsdf_a.inputs['Base Color'].default_value = (0.84, 0.74, 0.52, 1.0) # セピア黄ばみ紙
        bsdf_a.inputs['Roughness'].default_value = 0.88

    # 4. M_Paper_Folder (書類フォルダー・厚紙バインダー)
    mat_folder = bpy.data.materials.get(f"{prefix}_Paper_Folder") or bpy.data.materials.new(name=f"{prefix}_Paper_Folder")
    mat_folder.use_nodes = True
    bsdf_f = mat_folder.node_tree.nodes.get("Principled BSDF")
    if bsdf_f:
        bsdf_f.inputs['Base Color'].default_value = (0.45, 0.40, 0.32, 1.0) # マニラフォルダー
        bsdf_f.inputs['Roughness'].default_value = 0.78

    return [mat_white, mat_kraft, mat_aged, mat_folder]
