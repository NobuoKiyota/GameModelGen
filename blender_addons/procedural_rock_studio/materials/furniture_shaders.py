import bpy

def create_procedural_pbr_material(mat_name, seed=0, is_grass=False):
    """基本プロシージャルPBRマテリアル（木材・土・汎用）"""
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (650, 0)

    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (350, 0)
    node_bsdf.inputs['Roughness'].default_value = 0.85
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    node_coord = nodes.new(type='ShaderNodeTexCoord')
    node_coord.location = (-900, 0)
    
    node_map = nodes.new(type='ShaderNodeMapping')
    node_map.location = (-700, 0)
    node_map.inputs['Location'].default_value = (float((seed * 17) % 50), float((seed * 31) % 50), float((seed * 47) % 50))
    links.new(node_coord.outputs['Object'], node_map.inputs['Vector'])

    node_noise = nodes.new(type='ShaderNodeTexNoise')
    node_noise.location = (-450, 0)
    node_noise.inputs['Scale'].default_value = 4.0
    node_noise.inputs['Detail'].default_value = 6.0
    node_noise.inputs['Roughness'].default_value = 0.7
    links.new(node_map.outputs['Vector'], node_noise.inputs['Vector'])

    node_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_ramp.location = (-150, 0)
    
    if is_grass:
        node_ramp.color_ramp.elements[0].position = 0.2
        node_ramp.color_ramp.elements[0].color = (0.08, 0.22, 0.05, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.8
        node_ramp.color_ramp.elements[1].color = (0.28, 0.48, 0.12, 1.0)
    else:
        node_ramp.color_ramp.elements[0].position = 0.25
        node_ramp.color_ramp.elements[0].color = (0.15, 0.11, 0.08, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.75
        node_ramp.color_ramp.elements[1].color = (0.42, 0.32, 0.24, 1.0)
        
    links.new(node_noise.outputs['Fac'], node_ramp.inputs['Fac'])
    links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])

    node_bump = nodes.new(type='ShaderNodeBump')
    node_bump.location = (100, -150)
    node_bump.inputs['Strength'].default_value = 0.35
    node_bump.inputs['Distance'].default_value = 0.08
    links.new(node_noise.outputs['Fac'], node_bump.inputs['Height'])
    links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    return mat
