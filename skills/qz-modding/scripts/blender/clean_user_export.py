# Headless: clean a hand-exported character FBX (keeps the user's weights): drop Blender leaf bones (*_end_end),
# animation, ".001" suffixes; re-export with the pipeline's FBX settings.
# blender --background --factory-startup --python clean_user_export.py -- <in.fbx> <out.fbx> [material_name]
import sys
import bpy
a = sys.argv[sys.argv.index("--") + 1:]
src, dst = a[0], a[1]
mat_name = a[2] if len(a) > 2 else None
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=src)
arm = next(o for o in bpy.context.scene.objects if o.type == "ARMATURE")
mesh = max((o for o in bpy.context.scene.objects if o.type == "MESH"), key=lambda o: len(o.data.vertices))
for o in list(bpy.context.scene.objects):
    if o not in (arm, mesh):
        bpy.data.objects.remove(o, do_unlink=True)
arm.animation_data_clear()
for pb in arm.pose.bones:
    pb.location = (0, 0, 0); pb.rotation_quaternion = (1, 0, 0, 0); pb.rotation_euler = (0, 0, 0); pb.scale = (1, 1, 1)
leaf = [b.name for b in arm.data.bones if b.name.endswith("_end_end")]
weighted = {g.name for g in mesh.vertex_groups} & set(leaf)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
for n in leaf:
    arm.data.edit_bones.remove(arm.data.edit_bones[n])
bpy.ops.object.mode_set(mode="OBJECT")
for n in weighted:
    mesh.vertex_groups.remove(mesh.vertex_groups[n])
arm.name = "root"
arm.data.name = "root"
mesh.name = "SK_MyChar"
if mat_name and mesh.data.materials:
    for mt in bpy.data.materials:
        if mt.name == mat_name and mt is not mesh.data.materials[0]:
            mt.name = mat_name + "_unused"
    mesh.data.materials[0].name = mat_name
# skin link: without an Armature modifier the exporter writes no skin clusters (weights would be lost)
if not any(md.type == "ARMATURE" for md in mesh.modifiers):
    md = mesh.modifiers.new("Armature", "ARMATURE")
    md.object = arm
for md in mesh.modifiers:
    if md.type == "ARMATURE":
        md.object = arm
if mesh.parent is not arm:
    mw = mesh.matrix_world.copy()
    mesh.parent = arm
    mesh.matrix_world = mw
print("CLEAN removed leaf bones:", len(leaf), "weighted leaf groups:", len(weighted), "bones now:", len(arm.data.bones))
bpy.ops.object.select_all(action="DESELECT")
mesh.select_set(True); arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.fbx(filepath=dst, use_selection=True, object_types={"ARMATURE", "MESH"}, add_leaf_bones=False,
                         bake_anim=False, use_armature_deform_only=False, mesh_smooth_type="FACE", path_mode="COPY", embed_textures=True)
print("CLEAN exported", dst)
