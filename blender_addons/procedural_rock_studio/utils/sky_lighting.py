import bpy

def setup_procedural_sky_lighting(context):
    """Blender 3.6 内蔵 Nishita 物理大気散乱スカイ ＆ Eevee 屈折・反射を自動セットアップ"""
    scene = context.scene

    # 1. World 背景ノードの設定
    world = scene.world
    if not world:
        world = bpy.data.worlds.new("Nishita_Sky_World")
        scene.world = world
    world.use_nodes = True
    
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()

    # World Output
    node_out = nodes.new(type='ShaderNodeOutputWorld')
    node_out.location = (400, 0)

    # Background
    node_bg = nodes.new(type='ShaderNodeBackground')
    node_bg.location = (150, 0)
    node_bg.inputs['Strength'].default_value = 1.0
    links.new(node_bg.outputs['Background'], node_out.inputs['Surface'])

    # Sky Texture (Nishita 大気散乱モデル)
    node_sky = nodes.new(type='ShaderNodeTexSky')
    node_sky.location = (-150, 0)
    node_sky.sky_type = 'NISHITA'
    try:
        node_sky.sun_elevation = 0.314  # 約18度（ドラマチックな斜光・美しい反射）
        node_sky.sun_rotation = 0.785   # 約45度
        node_sky.altitude = 0.0
        node_sky.air_density = 1.0
        node_sky.dust_density = 1.0
        node_sky.ozone_density = 1.0
        node_sky.sun_intensity = 1.0
    except Exception:
        pass
    links.new(node_sky.outputs['Color'], node_bg.inputs['Color'])

    # 2. Eevee レンダラーのスクリーンスペース反射・屈折の自動有効化
    try:
        eevee = scene.eevee
        eevee.use_ssr = True
        eevee.use_ssr_refraction = True
        eevee.use_ssr_half_res = False
        eevee.use_gtao = True
        eevee.gtao_distance = 1.0
    except Exception:
        pass

    return world
