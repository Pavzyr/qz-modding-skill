# Round trip of a UE glTF export through Blender (headless), unchanged geometry -> FBX + GLB, to test the import back into UE.
# blender.exe --background --factory-startup --python roundtrip.py -- in.glb out_dir [bone_heuristic]
# Writes out_dir/rt.fbx, out_dir/rt.glb, out_dir/rt_report.json (objects, scales, bones, rest matrices of key bones, groups).
import json
import os
import sys
import bpy

args = sys.argv[sys.argv.index("--") + 1:]
src, out = args[0], args[1]
heur = args[2] if len(args) > 2 else "BLENDER"
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src, bone_heuristic=heur)
rep = {"heuristic": heur, "objects": []}
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
mesh = next(o for o in bpy.data.objects if o.type == "MESH" and any(m.type == "ARMATURE" for m in o.modifiers))  # importer also adds a bone-shape Icosphere
for o in bpy.data.objects:
    rep["objects"].append([o.name, o.type, o.parent.name if o.parent else None, [round(v, 4) for v in o.scale],
                           [round(v, 4) for v in o.rotation_euler], [m.type for m in getattr(o, "modifiers", [])]])
rep["bones"] = len(arm.data.bones)
rep["root_bones"] = [b.name for b in arm.data.bones if b.parent is None]
rep["key_bones"] = {n: [[round(x, 4) for x in r] for r in arm.data.bones[n].matrix_local]
                    for n in ("root", "pelvis", "thigh_l", "calf_l") if n in arm.data.bones}
rep["verts"] = len(mesh.data.vertices)
rep["groups"] = len(mesh.vertex_groups)
gi = {g.index: g.name for g in mesh.vertex_groups}
rep["unweighted_verts"] = sum(1 for v in mesh.data.vertices if not any(g.weight > 0 for g in v.groups))
rep["max_influences"] = max(len([g for g in v.groups if g.weight > 0]) for v in mesh.data.vertices)
used = {}
for v in mesh.data.vertices:
    for g in v.groups:
        if g.weight > 0.01:
            used[gi[g.group]] = used.get(gi[g.group], 0) + 1
rep["used_bones"] = sorted(used.items(), key=lambda x: -x[1])[:25]
rep["materials"] = [m.name if m else None for m in mesh.data.materials]
zs = [(mesh.matrix_world @ v.co).z for v in mesh.data.vertices]
rep["mesh_z_world"] = [round(min(zs), 4), round(max(zs), 4)]
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
mesh.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.fbx(filepath=os.path.join(out, "rt.fbx"), use_selection=True, object_types={"ARMATURE", "MESH"},
                         add_leaf_bones=False, bake_anim=False, use_armature_deform_only=False, mesh_smooth_type="FACE",
                         use_tspace=True)
bpy.ops.export_scene.gltf(filepath=os.path.join(out, "rt.glb"), use_selection=True, export_animations=False,
                          export_all_influences=True)   # default keeps only 4 influences per vertex (game mesh has up to 8)
json.dump(rep, open(os.path.join(out, "rt_report.json"), "w"), indent=1)
print("RT done", json.dumps(rep)[:2000])
