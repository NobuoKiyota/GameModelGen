def get_mix_input(node, name_candidates):
    """Mixノードから指定の候補名の入力ソケットを取得（Blender 3.x / 4.x / 5.x 互換）"""
    for name in name_candidates:
        if name in node.inputs:
            return node.inputs[name]
    for inp in node.inputs:
        if inp.enabled:
            return inp
    return node.inputs[0] if len(node.inputs) > 0 else None


def get_mix_output(node):
    """Mixノードから出力ソケットを取得（Blender 3.x / 4.x / 5.x 互換）"""
    if 'Result' in node.outputs:
        return node.outputs['Result']
    if 'Color' in node.outputs:
        return node.outputs['Color']
    return node.outputs[0] if len(node.outputs) > 0 else None
