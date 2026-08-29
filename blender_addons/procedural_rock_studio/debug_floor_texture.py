import bpy
import os

# Test loading Floor textures
tex_folder = r"Z:\MeshCreator\textures\Floor"
files = os.listdir(tex_folder)
print(f"Files found in Floor: {files}")

# Test creating material with Floor_01.png
img_path = os.path.join(tex_folder, "Floor_01.png")
img = bpy.data.images.load(img_path, check_existing=True)
print(f"Loaded image: {img.name}, size={img.size[:]}")

# Test assigning to a mesh cube
mesh = bpy.data.meshes.new("TestFloorMesh")
obj = bpy.data.objects.new("TestFloor", mesh)
bpy.context.collection.objects.link(obj)

mat = bpy.data.materials.new("Floor_01_Mat")
mat.use_nodes = True
nodes = mat.node_tree.nodes
nodes.clear()

node_out = nodes.new(type='ShaderNodeOutputMaterial')
node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
node_img = nodes.new(type='ShaderNodeTexImage')
node_img.image = img
node_coord = nodes.new(type='ShaderNodeTexCoord')
node_map = nodes.new(type='ShaderNodeMapping')

mat.node_tree.links.new(node_coord.outputs['UV'], node_map.inputs['Vector'])
mat.node_tree.links.new(node_map.outputs['Vector'], node_img.inputs['Vector'])
mat.node_tree.links.new(node_img.outputs['Color'], node_bsdf.inputs['Base Color'])
mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

obj.data.materials.append(mat)
print(f"Material successfully assigned to {obj.name}: {[m.name for m in obj.data.materials]}")
