# CHECK (Blender): load the final character FBX exactly as the game gets it, put the texture on it and add test poses
# on the timeline (frames 1-120). For VIEWING only - do not export from this scene.
# Run in a NEW Blender window: File -> New -> General, Scripting tab -> New -> paste -> Run Script (Alt+P).
import math
import os
import bpy
from mathutils import Matrix, Vector

FOLDER = r"C:\path\to\your\model"
FBX = os.path.join(FOLDER, "SK_MyChar.fbx")
BASECOLOR = os.path.join(FOLDER, "textures", "T_MyChar_BaseColor.jpg")


def popup(msg, icon="INFO"):
    print(msg)
    if bpy.app.background or not bpy.context.window:
        return
    try:
        bpy.context.window_manager.popup_menu(lambda self, ctx: [self.layout.label(text=l) for l in msg.split("\n")],
                                              title="Проверка модели", icon=icon)
    except Exception:
        pass


if bpy.context.object and bpy.context.object.mode != "OBJECT":
    bpy.ops.object.mode_set(mode="OBJECT")
for o in list(bpy.data.objects):          # only the default cube/camera/light
    if o.type in {"CAMERA", "LIGHT"} or (o.type == "MESH" and o.name == "Cube"):
        bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.object.select_all(action="DESELECT")
bpy.ops.import_scene.fbx(filepath=FBX)
imp = list(bpy.context.selected_objects)
arm = next(o for o in imp if o.type == "ARMATURE")
mesh = next(o for o in imp if o.type == "MESH")

# --- texture (Material Preview shows it)
mat = mesh.data.materials[0] if mesh.data.materials else bpy.data.materials.new("Char_preview")
if not mesh.data.materials:
    mesh.data.materials.append(mat)
mat.use_nodes = True
nt = mat.node_tree
bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None) or nt.nodes.new("ShaderNodeBsdfPrincipled")
for _n in [n for n in nt.nodes if n.type == "TEX_IMAGE"]:   # always show the jpg that goes to UE, not the FBX-embedded one
    nt.nodes.remove(_n)
if os.path.exists(BASECOLOR):
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(BASECOLOR, check_existing=True)
    tex.location = bsdf.location + Vector((-350, 0))
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None) or nt.nodes.new("ShaderNodeOutputMaterial")
if not out.inputs["Surface"].is_linked:
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

# --- test poses: rotations about WORLD axes around the bone joint (model faces -Y, character's left = +X)
X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
inv3 = arm.matrix_world.inverted().to_3x3()
for pb in arm.pose.bones:
    pb.rotation_mode = "QUATERNION"


def side_sign(side):
    return 1.0 if (arm.matrix_world @ arm.data.bones["upperarm_" + side].head_local).x > 0 else -1.0


def rot(bone, axis, deg):
    bpy.context.view_layer.update()
    pb = arm.pose.bones.get(bone)
    if pb is None:
        return
    h = pb.head.copy()
    q = Matrix.Rotation(math.radians(deg), 4, (inv3 @ axis).normalized())
    pb.matrix = Matrix.Translation(h) @ q @ Matrix.Translation(-h) @ pb.matrix


def arms_down(deg=70):
    for s in ("l", "r"):
        rot("upperarm_" + s, Y, deg * side_sign(s))


POSES = [
    (1, "T-поза (как в Blender)", []),
    (15, "Руки вниз (как стоит в игре)", [arms_down]),
    (30, "Руки вниз + локти вперёд + голова повёрнута", [arms_down,
        lambda: [rot("lowerarm_" + s, X, -70) for s in ("l", "r")], lambda: rot("head", Z, 40)]),
    (45, "Шаг", [arms_down, lambda: rot("thigh_l", X, -30), lambda: rot("thigh_r", X, 25),
                 lambda: rot("calf_r", X, 40), lambda: rot("upperarm_l", X, 20), lambda: rot("upperarm_r", X, -20)]),
    (60, "Шаг (другая нога)", [arms_down, lambda: rot("thigh_r", X, -30), lambda: rot("thigh_l", X, 25),
                               lambda: rot("calf_l", X, 40), lambda: rot("upperarm_r", X, 20), lambda: rot("upperarm_l", X, -20)]),
    (75, "Наклон вперёд", [arms_down, lambda: rot("spine_01", X, 15), lambda: rot("spine_02", X, 15),
                           lambda: rot("spine_03", X, 10)]),
    (90, "Присед / сидя", [arms_down, lambda: [rot("thigh_" + s, X, -80) for s in ("l", "r")],
                          lambda: [rot("calf_" + s, X, 85) for s in ("l", "r")]]),
    (105, "Руки вверх (проверка подмышек и груди)", [lambda: [rot("upperarm_" + s, Y, -60 * side_sign(s)) for s in ("l", "r")]]),
    (120, "T-поза", []),
]

arm.animation_data_clear()
for frame, name, ops in POSES:
    for pb in arm.pose.bones:
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)
        pb.scale = (1, 1, 1)
    for f in ops:
        f()
    bpy.context.view_layer.update()
    for pb in arm.pose.bones:
        pb.keyframe_insert("rotation_quaternion", frame=frame)
        pb.keyframe_insert("location", frame=frame)
    m = bpy.context.scene.timeline_markers.new(name, frame=frame)

sc = bpy.context.scene
sc.frame_start, sc.frame_end = 1, 120
sc.frame_set(1)
for area in (bpy.context.screen.areas if bpy.context.screen else []):
    if area.type == "VIEW_3D":
        sp = area.spaces[0]
        sp.shading.type = "MATERIAL"
        sp.shading.show_xray = False
        sp.overlay.show_bones = True
bpy.ops.object.select_all(action="DESELECT")
mesh.select_set(True)
bpy.context.view_layer.objects.active = mesh
popup("Загружено: %s\nВершин: %d, костей: %d.\n"
      "Внизу таймлайн: тяните ползунок кадров (1-120) или Пробел = проиграть.\n"
      "Метки на таймлайне = позы: руки вниз, шаг, наклон, присед, руки вверх.\n"
      "Смотреть: Numpad 1 спереди, Numpad 3 сбоку, колесо = зум, средняя кнопка = вращать.\n"
      "Это сцена ТОЛЬКО для просмотра, экспортировать из неё не нужно." %
      (os.path.basename(FBX), len(mesh.data.vertices), len(arm.data.bones)))
