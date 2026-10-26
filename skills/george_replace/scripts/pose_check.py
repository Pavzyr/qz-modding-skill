"""Gate 3 (headless Blender): import the FINAL FBX, put on the SAME base-colour jpg that goes to UE (embedded FBX textures
are removed - they once hid a texture/UV mismatch), pose it like the game does and measure torn edges.
  blender --background --factory-startup --python pose_check.py -- <final.fbx> <T_..._BaseColor.jpg> <out_dir>
Writes <out_dir>/pose_grid.png (6 poses x front/side) and pose_check.json {pose: stretched_edges}; prints a verdict.
Stretched edge = longer than 2.5x its rest length. Reference (good result, 2026-10-16): walk ~20-80, sit ~160, others < 50."""
import json, math, os, sys
import bpy
import numpy as np
from mathutils import Matrix, Vector

fbx, basecolor, out = sys.argv[sys.argv.index("--") + 1:][:3]
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=fbx)
arm = next(o for o in bpy.context.scene.objects if o.type == "ARMATURE")
mesh = max((o for o in bpy.context.scene.objects if o.type == "MESH"), key=lambda o: len(o.data.vertices))

mat = mesh.data.materials[0]
mat.use_nodes = True
nt = mat.node_tree
for n in [n for n in nt.nodes if n.type == "TEX_IMAGE"]:
    nt.nodes.remove(n)
bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
tex = nt.nodes.new("ShaderNodeTexImage")
tex.image = bpy.data.images.load(basecolor)
nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])

X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
inv3 = arm.matrix_world.inverted().to_3x3()
for pb in arm.pose.bones:
    pb.rotation_mode = "QUATERNION"


def sgn(side):
    return 1.0 if (arm.matrix_world @ arm.data.bones["upperarm_" + side].head_local).x > 0 else -1.0


def rot(bone, axis, deg):
    bpy.context.view_layer.update()
    pb = arm.pose.bones[bone]
    h = pb.head.copy()
    pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(math.radians(deg), 4, (inv3 @ axis).normalized()) @ \
        Matrix.Translation(-h) @ pb.matrix


def arms_down():
    for s in ("l", "r"):
        rot("upperarm_" + s, Y, 70 * sgn(s))


POSES = {
    "arms_down": [arms_down],
    "elbows_head": [arms_down, lambda: [rot("lowerarm_" + s, X, -70) for s in ("l", "r")], lambda: rot("head", Z, 40)],
    "walk": [arms_down, lambda: rot("thigh_l", X, -30), lambda: rot("thigh_r", X, 25), lambda: rot("calf_r", X, 40)],
    "bend": [arms_down, lambda: rot("spine_01", X, 15), lambda: rot("spine_02", X, 15), lambda: rot("spine_03", X, 10)],
    "sit": [arms_down, lambda: [rot("thigh_" + s, X, -80) for s in ("l", "r")], lambda: [rot("calf_" + s, X, 85) for s in ("l", "r")]],
    "arms_up": [lambda: [rot("upperarm_" + s, Y, -60 * sgn(s)) for s in ("l", "r")]],
}


def reset():
    for pb in arm.pose.bones:
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)
    bpy.context.view_layer.update()


def positions():
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh.evaluated_get(dg)
    me = ev.to_mesh()
    p = [mesh.matrix_world @ v.co for v in me.vertices]
    ev.to_mesh_clear()
    return p


sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sc.render.resolution_x, sc.render.resolution_y = 400, 520
sc.display.shading.light = "STUDIO"
sc.display.shading.color_type = "TEXTURE"
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.type = "ORTHO"
cam.data.ortho_scale = 2.3

reset()
rest = positions()
edges = [(e.vertices[0], e.vertices[1], (rest[e.vertices[0]] - rest[e.vertices[1]]).length) for e in mesh.data.edges]
report, tiles = {}, []
for name, ops in POSES.items():
    reset()
    for f in ops:
        f()
    bpy.context.view_layer.update()
    p = positions()
    report[name] = sum(1 for a, b, r in edges if r > 1e-6 and (p[a] - p[b]).length / r > 2.5)
    for view, loc, rt in (("f", (0, -5, 0.95), (math.radians(90), 0, 0)), ("s", (5, 0, 0.95), (math.radians(90), 0, math.radians(90)))):
        cam.location, cam.rotation_euler = loc, rt
        fn = os.path.join(out, "_pose_%s_%s.png" % (name, view))
        sc.render.filepath = fn
        bpy.ops.render.render(write_still=True)
        tiles.append((view, fn))

# grid: row 1 front, row 2 side
W, H = sc.render.resolution_x, sc.render.resolution_y
rows = []
for view in ("f", "s"):
    row = []
    for v, fn in tiles:
        if v == view:
            im = bpy.data.images.load(fn)
            a = np.array(im.pixels[:], dtype=np.float32).reshape(H, W, 4)
            row.append(a)
            bpy.data.images.remove(im)
            os.remove(fn)
    rows.append(np.concatenate(row, axis=1))
grid = np.concatenate([rows[1], rows[0]], axis=0)        # Blender pixels are bottom-up: front row ends on top
img = bpy.data.images.new("grid", grid.shape[1], grid.shape[0], alpha=True)
img.pixels[:] = grid.ravel()
img.filepath_raw = os.path.join(out, "pose_grid.png")
img.file_format = "PNG"
img.save()
json.dump(report, open(os.path.join(out, "pose_check.json"), "w"), indent=1)
bad = {k: v for k, v in report.items() if v > (350 if k == "sit" else 150)}
print("POSE_CHECK", report, "VERDICT:", "CHECK RENDERS: " + ", ".join(bad) if bad else "OK")
