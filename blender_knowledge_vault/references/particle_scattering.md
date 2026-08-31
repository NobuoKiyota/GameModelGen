# 🌾 パーティクル ＆ 散布システム (Particle Scattering & Baking)

## 1. Hair Particle ＋ Collection Render 散布
Mdesign 草原動画 09:00 準拠。

```python
def setup_grass_particle_system(terrain_obj, grass_col, density=5000, blade_height=0.6):
    ps_mod = terrain_obj.modifiers.new("GrassHair", 'PARTICLE_SYSTEM')
    ps = ps_mod.particle_system
    pset = ps.settings
    pset.type = 'HAIR'
    pset.count = density
    pset.hair_length = blade_height * 1.8
    pset.render_type = 'COLLECTION'
    pset.instance_collection = grass_col
    pset.use_collection_pick_random = True
    pset.particle_size = 1.0
    pset.size_random = 0.30             # Scale Random
    pset.use_rotations = True
    pset.rotation_mode = 'GLOB_Z'
    pset.rotation_factor_random = 1.0  # Phase Random (全方位ランダム回転)
    pset.phase_factor_random = 2.0
    pset.use_scale_instance = True
    return ps
```

---

## 2. ノイズ数式による頂点グループ（ウェイト）の自動ペイント
Mdesign 草原動画 14:06 準拠。

```python
def apply_procedural_weight_paint(terrain_obj, noise_scale=2.5, seed=42):
    vg = terrain_obj.vertex_groups.new(name="Grass_Density")
    terrain_obj.data.update()
    for v in terrain_obj.data.vertices:
        x, y = v.co.x, v.co.y
        w_raw = (math.sin(x * noise_scale + seed * 0.17)
                 * math.cos(y * noise_scale + seed * 0.23) * 0.5 + 0.5)
        weight = max(0.05, min(1.0, w_raw))
        vg.add([v.index], weight, 'REPLACE')
    
    # パーティクルの密度マップにバインド
    for m in terrain_obj.modifiers:
        if m.type == 'PARTICLE_SYSTEM':
            m.particle_system.vertex_group_density = "Grass_Density"
```

---

## 3. Unity / ゲーム用実メッシュ変換 (Baking to Real Mesh)
Blender 3.6 対応。

```python
def convert_particles_to_real_game_mesh(obj):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.particle.disconnect_hair()
    bpy.ops.object.convert(target='MESH')
```
