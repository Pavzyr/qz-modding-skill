"""Headless Blender: fit an arbitrary (AI-generated) T/A-pose character mesh onto a QZ staff skeleton and export a
UE-ready FBX. Run:
  blender.exe --background --factory-startup --python auto_fit_skin.py -- <config.json>
config: {"ref_fbx": ".../D2_Zheka.FBX", "model": ".../x.glb", "out_dir": ".../auto", "out_fbx": ".../SK_MyChar.fbx",
         "mesh_name": "SK_MyChar", "stage": "fit" | "all", "material_name": "<slot name of the previous import, optional>",
         "textures_dir": "<optional: extract GLB textures here>", "texture_prefix": "T_MyChar"}
Steps: import reference (UE-exported mesh+skeleton, keep LOD0, armature object -> 'root'), import model, weld,
scale to reference height, align by knees; detect model arm direction/length and pose the reference arm chain onto it,
stretch model arms to the skeleton's arm length; freeze reference mesh, apply pose as rest; bind model (empty groups),
copy weights (Data Transfer), move gear-bone weights to nearest body bone, clean/limit/normalize; renders for checking;
export FBX (root -> pelvis ...). Writes report.json + PNG renders into out_dir.
"""
import json, math, os, re, sys, traceback
import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.geometry import intersect_point_line

CFG = json.load(open(sys.argv[sys.argv.index("--") + 1], encoding="utf-8"))
OUT = CFG["out_dir"]
os.makedirs(OUT, exist_ok=True)
REP = {"steps": [], "warnings": []}
BODY = re.compile(r"^(pelvis|spine_0[1-3]|neck_01|head|clavicle_[lr]|upperarm_[lr]|lowerarm_[lr]|hand_[lr]|"
                  r"(thumb|index|middle|ring|pinky)_0[1-3]_[lr]|thigh_[lr]|calf_[lr]|foot_[lr]|ball_[lr])$")
TARGETS = ("pelvis", "spine_01", "spine_02", "spine_03", "neck_01", "head", "clavicle_l", "clavicle_r",
           "upperarm_l", "upperarm_r", "thigh_l", "thigh_r", "calf_l", "calf_r")


def step(msg, **kw):
    kw["msg"] = msg
    REP["steps"].append(kw)
    print("[auto_fit]", msg, kw)
    json.dump(REP, open(os.path.join(OUT, "report.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)


def activate(o, *others):
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    for x in others:
        x.select_set(True)
    o.select_set(True)
    bpy.context.view_layer.objects.active = o


def world_verts(o):
    mw = o.matrix_world
    dg = bpy.context.evaluated_depsgraph_get()
    ev = o.evaluated_get(dg)
    me = ev.to_mesh()
    pts = [mw @ v.co for v in me.vertices]
    ev.to_mesh_clear()
    return pts


def bbox(pts):
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))


def median(vals):
    vals = sorted(vals)
    return vals[len(vals) // 2] if vals else 0.0


def bone_w(arm, name, tail=False):
    pb = arm.pose.bones[name]
    return arm.matrix_world @ (pb.tail if tail else pb.head)


# ------------------------------------------------------------------ scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.object.select_all(action="DESELECT")
try:
    bpy.ops.import_scene.fbx(filepath=CFG["ref_fbx"])
except Exception:
    bpy.ops.wm.fbx_import(filepath=CFG["ref_fbx"])
imp = list(bpy.context.selected_objects)
arm = next(o for o in imp if o.type == "ARMATURE")
ref = next(o for o in imp if o.type == "MESH" and "LOD0" in o.name)
for o in imp:
    if o not in (arm, ref):
        bpy.data.objects.remove(o, do_unlink=True)
arm.name = "root"
ref.name = "REF"
step("reference imported", bones=len(arm.data.bones), ref_verts=len(ref.data.vertices))

# textures straight from the SAME model file (a GLB re-exported under the same name after a manual extraction gave
# the mesh one UV layout and the textures another -> patchwork texture in game). config "textures_dir" + "texture_prefix".
if CFG.get("textures_dir") and CFG["model"].lower().endswith(".glb"):
    import struct
    raw = open(CFG["model"], "rb").read()
    jl = struct.unpack_from("<I", raw, 12)[0]
    gj = json.loads(raw[20:20 + jl])
    boff = 20 + jl + 8
    m0 = gj["materials"][0]
    roles = {"BaseColor": m0.get("pbrMetallicRoughness", {}).get("baseColorTexture", {}).get("index"),
             "RoughMetal": m0.get("pbrMetallicRoughness", {}).get("metallicRoughnessTexture", {}).get("index"),
             "Normal": m0.get("normalTexture", {}).get("index")}
    os.makedirs(CFG["textures_dir"], exist_ok=True)
    written = []
    for role, ti in roles.items():
        if ti is None:
            continue
        im = gj["images"][gj["textures"][ti]["source"]]
        bv = gj["bufferViews"][im["bufferView"]]
        o = boff + bv.get("byteOffset", 0)
        fn = os.path.join(CFG["textures_dir"], "%s_%s%s" % (CFG.get("texture_prefix", "T_Model"), role,
                                                          ".jpg" if im.get("mimeType") == "image/jpeg" else ".png"))
        open(fn, "wb").write(raw[o:o + bv["byteLength"]])
        written.append(fn)
    step("textures extracted", files=written)

bpy.ops.object.select_all(action="DESELECT")
ext = os.path.splitext(CFG["model"])[1].lower()
if ext in (".glb", ".gltf"):
    bpy.ops.import_scene.gltf(filepath=CFG["model"])
else:
    bpy.ops.import_scene.fbx(filepath=CFG["model"])
sel = list(bpy.context.selected_objects)
meshes = [o for o in sel if o.type == "MESH"]
for o in sel:
    if o.type != "MESH":
        for m in meshes:
            if m.parent is o:
                mw = m.matrix_world.copy()
                m.parent = None
                m.matrix_world = mw
        bpy.data.objects.remove(o, do_unlink=True)
if len(meshes) > 1:
    activate(meshes[0], *meshes[1:])
    bpy.ops.object.join()
model = meshes[0]
model.name = CFG.get("mesh_name", "SK_MyChar")
for m in list(model.modifiers):
    model.modifiers.remove(m)
activate(model)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bm = bmesh.new()
bm.from_mesh(model.data)
n0 = len(bm.verts)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
bm.to_mesh(model.data)
n1 = len(bm.verts)
bm.free()
for p in model.data.polygons:
    p.use_smooth = True
# hair = texture colour: light and grey (no hue). Per vertex: mean base colour over its UV loops, then a 2-pass
# neighbour majority filter removes specks on skin/clothes. Config "hair": false disables.
HAIR = set()
img = next((i for i in bpy.data.images if "basecolor" in i.name.lower() or "base_color" in i.name.lower()), None)
if CFG.get("hair", True) and img is not None and model.data.uv_layers:
    import numpy as np
    W, H = img.size
    px = np.empty(W * H * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    px = px.reshape(H, W, 4)
    me = model.data
    nl = len(me.loops)
    uvs = np.empty(nl * 2, dtype=np.float32)
    me.uv_layers.active.data.foreach_get("uv", uvs)
    uvs = uvs.reshape(nl, 2)
    lv = np.empty(nl, dtype=np.int32)
    me.loops.foreach_get("vertex_index", lv)
    col = px[np.clip((uvs[:, 1] % 1.0) * H, 0, H - 1).astype(int), np.clip((uvs[:, 0] % 1.0) * W, 0, W - 1).astype(int), :3]
    nv = len(me.vertices)
    acc = np.zeros((nv, 3))
    cnt = np.zeros(nv)
    np.add.at(acc, lv, col)
    np.add.at(cnt, lv, 1)
    c = acc / np.maximum(cnt, 1)[:, None]
    mx, mn = c.max(1), c.min(1)
    hair = (mx > 0.35) & ((mx - mn) / np.maximum(mx, 1e-4) < 0.15)
    nb = [[] for _ in range(nv)]
    for e in me.edges:
        a, b = e.vertices
        nb[a].append(b)
        nb[b].append(a)
    for _ in range(2):
        hair = np.array([(hair[i] + sum(hair[j] for j in nb[i])) * 2 > len(nb[i]) + 1 for i in range(nv)])
    HAIR = set(np.nonzero(hair)[0].tolist())
step("model imported", hair_verts=len(HAIR), verts=n1, welded=n0 - n1, tris=sum(len(p.vertices) - 2 for p in model.data.polygons))

# ------------------------------------------------------------------ scale + align (height, knees)
rp = world_verts(ref)
r0, r1 = bbox(rp)
U = (r1.z - r0.z) / 1.85      # scene units per metre (FBX import may give cm or m)
mp = [model.matrix_world @ v.co for v in model.data.vertices]
m0, m1 = bbox(mp)
k = (r1.z - r0.z) / (m1.z - m0.z)
for v in model.data.vertices:
    v.co = v.co * k
mp = [model.matrix_world @ v.co for v in model.data.vertices]
m0, m1 = bbox(mp)
knee_g = (bone_w(arm, "calf_l") + bone_w(arm, "calf_r")) / 2
kz = m0.z + (knee_g.z - r0.z)
band = [p for p in mp if abs(p.z - kz) < 0.06 * U and abs(p.x - knee_g.x) < 0.35 * U]
off = Vector((knee_g.x - median([p.x for p in band]), knee_g.y - median([p.y for p in band]), r0.z - m0.z))
for v in model.data.vertices:
    v.co = v.co + model.matrix_world.inverted().to_3x3() @ off
step("scaled+aligned", units_per_m=round(U, 3), scale=round(k, 4), height=round(r1.z - r0.z, 3), knee_band=len(band), offset=[round(x, 3) for x in off])


# ------------------------------------------------------------------ arms: pose skeleton onto model arms, stretch model arms
def chain_dir_rotate(pairs, d_world):
    """rotate each (bone, next_joint_bone) so the joint->next-joint vector points along d_world.
    Bone tails of UE-imported skeletons do not follow the limb, so directions use child joints (heads)."""
    inv3 = arm.matrix_world.inverted().to_3x3()
    d_arm = (inv3 @ d_world).normalized()
    for n, child in pairs:
        bpy.context.view_layer.update()
        pb = arm.pose.bones[n]
        cur = (arm.pose.bones[child].head - pb.head).normalized()
        q = cur.rotation_difference(d_arm)
        h = pb.head.copy()
        pb.matrix = Matrix.Translation(h) @ q.to_matrix().to_4x4() @ Matrix.Translation(-h) @ pb.matrix
    bpy.context.view_layer.update()


def finger_tip(side):
    a, b = bone_w(arm, "middle_02_" + side), bone_w(arm, "middle_03_" + side)
    return b + (b - a)


arm_report = {}
ARM_LINES = {}   # side -> (shoulder point P, direction d, length after stretch, skeleton shoulder |x|)
verts = model.data.vertices
mwi3 = model.matrix_world.inverted().to_3x3()
pts = [(i, model.matrix_world @ v.co) for i, v in enumerate(verts)]
xs = [p.x for i, p in pts]
mid = (max(xs) + min(xs)) / 2
pel = bone_w(arm, "pelvis")
dx = pel.x - mid
for v in verts:
    v.co = v.co + mwi3 @ Vector((dx, 0, 0))
arm_report["center_shift_x_m"] = round(dx / U, 3)
pts = [(i, model.matrix_world @ v.co) for i, v in enumerate(verts)]
for side in ("l", "r"):
    sh = bone_w(arm, "upperarm_" + side)
    s = 1.0 if sh.x > 0 else -1.0
    X0 = abs(sh.x)
    side_pts = [(i, p) for i, p in pts if s * p.x > 0]
    maxx = max(s * p.x for i, p in side_pts)
    tip_pts = [p for i, p in side_pts if s * p.x > maxx - 0.04 * U]
    tip = sum(tip_pts, Vector()) / len(tip_pts)
    near = [p for i, p in side_pts if X0 + 0.10 * U < s * p.x < X0 + 0.25 * U and abs(p.z - tip.z) < 0.12 * U]
    if len(near) < 10:
        REP["warnings"].append("arm %s: too few verts near shoulder (%d)" % (side, len(near)))
        continue
    pn = Vector((median([p.x for p in near]), median([p.y for p in near]), median([p.z for p in near])))
    d = (tip - pn).normalized()
    P = pn - d * ((s * pn.x - X0) / max(abs(d.x), 1e-6))     # point on the arm line at the skeleton shoulder x
    Lm = (tip - P).length
    arm_pts = []
    for i, p in side_pts:
        if s * p.x < X0 - 0.02 * U:
            continue
        q, f = intersect_point_line(p, P, tip)
        if -0.05 <= f <= 1.1 and (p - q).length < 0.13 * U:
            arm_pts.append((i, p))
    cl = bone_w(arm, "clavicle_" + side)
    chain_dir_rotate([("clavicle_" + side, "upperarm_" + side)], (P - cl).normalized())
    chain_dir_rotate([("upperarm_" + side, "lowerarm_" + side), ("lowerarm_" + side, "hand_" + side), ("hand_" + side, "middle_01_" + side)], d)
    tipg = finger_tip(side)
    shg = bone_w(arm, "upperarm_" + side)
    Lg = (tipg - shg).length
    kk = Lg / Lm
    ARM_LINES[side] = (P.copy(), d.copy(), Lg, X0, s)
    for i, p in arm_pts:
        t = (p - P).dot(d)
        if t <= 0:
            continue
        w = min(max((s * p.x - (X0 - 0.02 * U)) / (0.08 * U), 0.0), 1.0)
        verts[i].co = verts[i].co + mwi3 @ (d * t * (kk - 1.0) * w)
    arm_report[side] = {"arm_verts": len(arm_pts), "near": len(near), "dir": [round(x, 3) for x in d],
                        "model_len_m": round(Lm / U, 3), "skel_len_m": round(Lg / U, 3), "stretch": round(kk, 3),
                        "arm_z_vs_shoulder_m": round((P.z - shg.z) / U, 3)}

# legs: point the skeleton's thigh->calf chain at the model's ankles (model legs may be spread wider)
pts = [(i, model.matrix_world @ v.co) for i, v in enumerate(verts)]
zmin = min(p.z for i, p in pts)
for side in ("l", "r"):
    hip = bone_w(arm, "thigh_" + side)
    s = 1.0 if hip.x > 0 else -1.0
    ank_g = bone_w(arm, "foot_" + side)
    za = ank_g.z
    ring = [p for i, p in pts if s * p.x > 0.01 * U and abs(p.z - za) < 0.03 * U]
    if len(ring) < 10:
        REP["warnings"].append("leg %s: ankle ring not found" % side)
        continue
    ank_m = Vector((median([p.x for p in ring]), median([p.y for p in ring]), za))
    d = (ank_m - hip).normalized()
    chain_dir_rotate([("thigh_" + side, "calf_" + side), ("calf_" + side, "foot_" + side)], d)
    arm_report["leg_" + side] = {"ankle_shift_m": round((ank_m - ank_g).length / U, 3), "ring": len(ring)}
step("arms fitted", **arm_report)


# ------------------------------------------------------------------ renders for checking
def setup_render():
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.render.resolution_x, sc.render.resolution_y = 900, 1100
    sh = sc.display.shading
    sh.light = "STUDIO"
    sh.color_type = "OBJECT"
    sh.show_xray = True
    sh.xray_alpha = 0.55
    if "CAM" not in bpy.data.objects:
        cam = bpy.data.objects.new("CAM", bpy.data.cameras.new("CAM"))
        sc.collection.objects.link(cam)
        sc.camera = cam
    return bpy.data.objects["CAM"]


def render(name, view, objs):
    cam = setup_render()
    pts = []
    for o in objs:
        pts += world_verts(o)
    a, b = bbox(pts)
    c = (a + b) / 2
    size = max(b.z - a.z, b.x - a.x, b.y - a.y) * 1.08
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = size
    if view == "front":
        cam.location = Vector((c.x, a.y - 10, c.z))
        cam.rotation_euler = (math.radians(90), 0, 0)
    else:
        cam.location = Vector((b.x + 10, c.y, c.z))
        cam.rotation_euler = (math.radians(90), 0, math.radians(90))
    for o in bpy.data.objects:
        if o.type == "MESH":
            o.hide_render = o not in objs
    bpy.context.scene.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)


ref.color = (1.0, 0.25, 0.2, 1.0)
model.color = (0.85, 0.85, 0.95, 1.0)
bpy.context.view_layer.update()
render("1_fit_front", "front", [ref, model])
render("2_fit_side", "side", [ref, model])
step("fit renders written")
if CFG.get("stage") == "fit":
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "fit_stage.blend"))
    step("stopped after fit (stage=fit)")
    sys.exit(0)

# ------------------------------------------------------------------ freeze reference in new pose, pose -> rest
activate(ref)
for m in list(ref.modifiers):
    if m.type == "ARMATURE":
        bpy.ops.object.modifier_apply(modifier=m.name)
activate(arm)
bpy.ops.object.mode_set(mode="POSE")
bpy.ops.pose.select_all(action="SELECT")
bpy.ops.pose.armature_apply(selected=False)
bpy.ops.object.mode_set(mode="OBJECT")
step("pose applied as rest")

# ------------------------------------------------------------------ bind + weights
activate(arm, model)
bpy.ops.object.parent_set(type="ARMATURE_NAME")
activate(model)
dt = model.modifiers.new("W", "DATA_TRANSFER")
dt.object = ref
dt.use_vert_data = True
dt.data_types_verts = {"VGROUP_WEIGHTS"}
dt.vert_mapping = "POLYINTERP_NEAREST"
bpy.ops.object.datalayout_transfer(modifier=dt.name)
bpy.ops.object.modifier_move_to_index(modifier=dt.name, index=0)
bpy.ops.object.modifier_apply(modifier=dt.name)

segs = {n: (arm.matrix_world @ arm.data.bones[n].head_local, arm.matrix_world @ arm.data.bones[n].tail_local)
        for n in TARGETS if n in arm.data.bones}


def nearest_body(p):
    best, bd = "pelvis", 1e30
    for n, (h, t) in segs.items():
        q, f = intersect_point_line(p, h, t)
        f = min(max(f, 0.0), 1.0)
        dd = (p - (h + (t - h) * f)).length
        if dd < bd:
            best, bd = n, dd
    return best


# arm bones may drive only the real arm: flood-fill over mesh edges from the hand, staying inside the arm tube.
# Long hair/frills hang next to the arm but are not edge-connected to it inside the tube -> they lose arm weights.
mw = model.matrix_world
wp = [mw @ v.co for v in model.data.vertices]
adj = [[] for _ in wp]
for e in model.data.edges:
    a, b = e.vertices
    adj[a].append(b)
    adj[b].append(a)
arm_mask = {}
for side, (P, d, L, X0, s) in ARM_LINES.items():
    tip = P + d * L
    def in_tube(i):
        p = wp[i]
        if s * p.x < X0 - 0.02 * U:
            return False
        q, f = intersect_point_line(p, P, tip)
        return -0.05 <= f <= 1.1 and (p - q).length < 0.13 * U
    seeds = [i for i in range(len(wp)) if in_tube(i) and (wp[i] - P).dot(d) > 0.8 * L]
    seen = set(seeds)
    stack = list(seeds)
    while stack:
        a = stack.pop()
        for b in adj[a]:
            if b not in seen and in_tube(b):
                seen.add(b)
                stack.append(b)
    arm_mask[side] = seen

vgs = model.vertex_groups

gear = {vg.index: vg.name for vg in vgs if not BODY.match(vg.name) and vg.name in arm.data.bones}
for n in segs:
    if n not in vgs:
        vgs.new(name=n)
idx = {vg.name: vg.index for vg in vgs}
moved = 0
for v in model.data.vertices:
    w = sum(g.weight for g in v.groups if g.group in gear)
    if w > 0:
        vgs[idx[nearest_body(model.matrix_world @ v.co)]].add([v.index], w, "ADD")
        moved += 1
for n in list(gear.values()):
    vgs.remove(vgs[n])
# (after the gear move: gear weights near the shoulders were landing on upperarm_*)
# Limb bones may drive only their own limb. Distances use joint->child-joint lines (UE bone tails are unreliable).
def jw(n):
    return arm.matrix_world @ arm.data.bones[n].head_local


def seg_dist(p, a, b):
    q, f = intersect_point_line(p, a, b)
    f = min(max(f, 0.0), 1.0)
    return (p - (a + (b - a) * f)).length


def flood(seeds, ok):
    seen = set(seeds)
    stack = list(seeds)
    while stack:
        a = stack.pop()
        for b in adj[a]:
            if b not in seen and ok(b):
                seen.add(b)
                stack.append(b)
    return seen


leg_mask, thigh_zone, clav_zone = {}, {}, {}
for side in ("l", "r"):
    hip, knee, ank, ball = jw("thigh_" + side), jw("calf_" + side), jw("foot_" + side), jw("ball_" + side)
    toe = ball + (ball - ank) * 0.6
    def in_leg(i, hip=hip, knee=knee, ank=ank, ball=ball, toe=toe):
        p = wp[i]
        if p.z < ank.z + 0.03 * U:     # whole shoe incl. high-heel spikes (they reach the floor behind the ankle)
            flat = Vector((p.x, p.y, ank.z))
            if min(seg_dist(flat, ank, toe), (flat - ank).length) < 0.15 * U:
                return True
        return min(seg_dist(p, hip, knee), seg_dist(p, knee, ank), seg_dist(p, ank, ball), seg_dist(p, ball, toe)) < 0.12 * U
    seeds = [i for i in range(len(wp)) if (wp[i] - ank).length < 0.08 * U]
    leg_mask[side] = flood(seeds, in_leg)
    thigh_zone[side] = {i for i in range(len(wp)) if seg_dist(wp[i], hip, knee) < 0.20 * U} | leg_mask[side]
    cl, ua = jw("clavicle_" + side), jw("upperarm_" + side)
    clav_zone[side] = {i for i in range(len(wp)) if seg_dist(wp[i], cl, ua) < 0.20 * U} | arm_mask.get(side, set())

LIMB = re.compile(r"^(upperarm|lowerarm|hand|(thumb|index|middle|ring|pinky)_0[1-3]|calf|foot|ball|thigh|clavicle)_([lr])$")


def allowed_set(name):
    mm = LIMB.match(name)
    part, side = mm.group(1), mm.group(3)
    if part == "thigh":
        return thigh_zone[side]
    if part in ("calf", "foot", "ball"):
        return leg_mask[side]
    if part == "clavicle":
        return clav_zone[side]
    return arm_mask.get(side, set())


limb_groups = {vg.index: allowed_set(vg.name) for vg in vgs if LIMB.match(vg.name)}
stripped = 0
for v in model.data.vertices:
    bad = [g.group for g in v.groups if g.group in limb_groups and v.index not in limb_groups[g.group]]
    if bad:
        stripped += 1
        for gi in bad:
            vgs[gi].remove([v.index])
json.dump({k: sorted(m) for k, m in arm_mask.items()}, open(os.path.join(OUT, "arm_mask.json"), "w"))
step("limb masks", arm_verts={k: len(m) for k, m in arm_mask.items()}, leg_verts={k: len(m) for k, m in leg_mask.items()},
     stripped_verts=stripped)
activate(model)
bpy.ops.object.vertex_group_clean(group_select_mode="ALL", limit=0.01)
bpy.ops.object.vertex_group_limit_total(group_select_mode="ALL", limit=8)
bpy.ops.object.vertex_group_normalize_all(lock_active=False)
# verts left without weights (hair/frills that only had limb weights) -> nearest torso joint line
TORSO = [("pelvis", "spine_01"), ("spine_01", "spine_02"), ("spine_02", "spine_03"), ("spine_03", "neck_01"),
         ("neck_01", "head")]
tl = [(n, jw(n), jw(c)) for n, c in TORSO]
hd = jw("head")
tl.append(("head", hd, hd + (hd - jw("neck_01")) * 1.5))
empty = [v.index for v in model.data.vertices if not any(g.weight > 0 for g in v.groups)]
for i in empty:
    best = min(tl, key=lambda t: seg_dist(wp[i], t[1], t[2]))[0]
    vgs[best].add([i], 1.0, "REPLACE")
unweighted = sum(1 for v in model.data.vertices if not any(g.weight > 0 for g in v.groups))
step("refilled empty verts", count=len(empty))

# hair: only head -> neck -> spine_03 -> spine_02 by height (no arms/legs/pelvis: long hair must not follow the hips)
if HAIR:
    chain = [("head", jw("head").z), ("neck_01", jw("neck_01").z), ("spine_03", jw("spine_03").z), ("spine_02", jw("spine_02").z)]
    for i in HAIR:
        v = model.data.vertices[i]
        for g in list(v.groups):
            vgs[g.group].remove([i])
        z = wp[i].z
        if z >= chain[0][1]:
            ws = {chain[0][0]: 1.0}
        elif z <= chain[-1][1]:
            ws = {chain[-1][0]: 1.0}
        else:
            for (na, za), (nb_, zb) in zip(chain, chain[1:]):
                if zb <= z <= za:
                    t = (za - z) / max(za - zb, 1e-6)
                    ws = {na: 1.0 - t, nb_: t}
                    break
        for n, w in ws.items():
            if w > 0.001:
                vgs[n].add([i], w, "REPLACE")
    step("hair weights", verts=len(HAIR))

# skirt (verts near the thighs that are not the leg itself / hair): thigh weight is procedural, not copied - front and
# sides follow the thigh partly, the back stays with the pelvis (copied weights pulled the back of the skirt into
# spikes when the thigh lifted, e.g. sitting). Smoothed over mesh neighbours so there are no single-vertex jumps.
skirt = {}
for side in ("l", "r"):
    hip, knee = jw("thigh_" + side), jw("calf_" + side)
    zone = (thigh_zone[side] - leg_mask[side]) - HAIR
    crotch_z = hip.z - 0.08 * U       # only cloth hanging BELOW the crotch; hips/buttocks keep copied weights
    for i in zone:
        p = wp[i]
        if p.z > crotch_z:
            continue
        d = seg_dist(p, hip, knee)
        f_d = min(max((0.20 * U - d) / (0.10 * U), 0.0), 1.0)
        f_h = min(max((hip.z - p.z) / (0.15 * U), 0.0), 1.0)
        f_front = min(max(0.5 + (hip.y - p.y) / (0.12 * U), 0.0), 1.0)    # model faces -Y
        skirt.setdefault(i, {})[side] = 0.6 * f_d * f_h * f_front
for _ in range(4):
    nxt = {}
    for i, w in skirt.items():
        nn = [j for j in adj[i] if j in skirt]
        nxt[i] = {sd: (w.get(sd, 0.0) + sum(skirt[j].get(sd, 0.0) for j in nn)) / (1 + len(nn)) for sd in ("l", "r")}
    skirt = nxt
for i, w in skirt.items():
    v = model.data.vertices[i]
    t = {sd: w.get(sd, 0.0) for sd in ("l", "r")}
    tot = min(t["l"] + t["r"], 0.8)
    others = [(g.group, g.weight) for g in v.groups if vgs[g.group].name not in ("thigh_l", "thigh_r")]
    osum = sum(x for _, x in others)
    for g in list(v.groups):
        vgs[g.group].remove([i])
    if osum <= 1e-6:
        others, osum = [(vgs["pelvis"].index, 1.0)], 1.0
    for gi, x in others:
        vgs[gi].add([i], x / osum * (1.0 - tot), "REPLACE")
    if tot > 0:
        sc_ = tot / max(t["l"] + t["r"], 1e-6)
        for sd in ("l", "r"):
            if t[sd] * sc_ > 0.002:
                vgs["thigh_" + sd].add([i], t[sd] * sc_, "REPLACE")
step("skirt weights", verts=len(skirt))

# legs below the crotch: weights along the leg's own chain (thigh -> calf -> foot -> ball, smooth at joints), blended
# into the copied weights between the crotch and 10 cm below it. Copied weights there were unreliable: legs that touch
# got the OTHER leg's bones, inner thighs got pelvis 0.99 from the reference skin's crotch shield -> torn sheets when walking/sitting.
def smooth01(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


grp = {vg.name: vg.index for vg in vgs}
legs_done = 0
for side in ("l", "r"):
    hip, knee, ank, ball = jw("thigh_" + side), jw("calf_" + side), jw("foot_" + side), jw("ball_" + side)
    other = "r" if side == "l" else "l"
    crotch_z = hip.z - 0.08 * U
    fwd = -1.0 if (ball - ank).y < 0 else 1.0           # toes direction along y
    for i in leg_mask[side] - HAIR:
        p = wp[i]
        v = model.data.vertices[i]
        cur = {vgs[g.group].name: g.weight for g in v.groups}
        for n in [n for n in cur if n.endswith("_" + other) and n.split("_")[0] in ("thigh", "calf", "foot", "ball")]:
            cur.pop(n)
        alpha = smooth01(crotch_z, crotch_z - 0.10 * U, p.z)
        if alpha > 0:
            s_k = smooth01(knee.z + 0.05 * U, knee.z - 0.05 * U, p.z)
            s_a = smooth01(ank.z + 0.04 * U, ank.z - 0.02 * U, p.z)
            s_b = smooth01(-0.03 * U, 0.03 * U, (p.y - ball.y) * fwd)
            proc = {"thigh_" + side: 1 - s_k, "calf_" + side: s_k * (1 - s_a),
                    "foot_" + side: s_k * s_a * (1 - s_b), "ball_" + side: s_k * s_a * s_b}
            tot = sum(cur.values()) or 1.0
            new = {n: (1 - alpha) * w / tot for n, w in cur.items()}
            for n, w in proc.items():
                new[n] = new.get(n, 0.0) + alpha * w
        else:
            tot = sum(cur.values()) or 1.0
            new = {n: w / tot for n, w in cur.items()}
        for g in list(v.groups):
            vgs[g.group].remove([i])
        for n, w in new.items():
            if w > 0.002:
                if n not in grp:
                    grp[n] = vgs.new(name=n).index
                vgs[grp[n]].add([i], w, "REPLACE")
        legs_done += 1

# hip region smoothing (pelvis/thigh/spine_01 border): 4 neighbour-averaging passes, then normalize
hl, hr = jw("thigh_l"), jw("thigh_r")
zone = [i for i in range(len(wp)) if i not in HAIR and min((wp[i] - hl).length, (wp[i] - hr).length) < 0.22 * U]
zs = set(zone)
W = {i: {vgs[g.group].name: g.weight for g in model.data.vertices[i].groups} for i in zone}
for _ in range(4):
    nxt = {}
    for i in zone:
        acc = dict(W[i])
        nn = [j for j in adj[i] if j in zs]
        for j in nn:
            for n, w in W[j].items():
                acc[n] = acc.get(n, 0.0) + w
        k = 1 + len(nn)
        nxt[i] = {n: w / k for n, w in acc.items()}
    W = nxt
for i in zone:
    v = model.data.vertices[i]
    for g in list(v.groups):
        vgs[g.group].remove([i])
    tot = sum(W[i].values()) or 1.0
    for n, w in sorted(W[i].items(), key=lambda x: -x[1])[:8]:
        if w / tot > 0.002:
            vgs[grp[n]].add([i], w / tot, "REPLACE")
activate(model)
bpy.ops.object.vertex_group_normalize_all(lock_active=False)
step("leg chain weights", leg_verts=legs_done, hip_smoothed=len(zone))
step("weights", gear_names=sorted(gear.values()), gear_groups=len(gear), gear_verts=moved, unweighted=unweighted, groups=len(model.vertex_groups))

# ------------------------------------------------------------------ test pose render (arms down, elbow bend, head turn)
bpy.data.objects.remove(ref, do_unlink=True)
render("3_bind_front", "front", [model])
activate(arm)
bpy.ops.object.mode_set(mode="POSE")
for side, s in (("l", 1), ("r", -1)):
    pb = arm.pose.bones["upperarm_" + side]
    pb.rotation_mode = "XYZ"
    pb.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()
    d = bone_w(arm, "lowerarm_" + side) - bone_w(arm, "upperarm_" + side)
    axis_w = Vector((0, 1, 0))
    ang = math.radians(60) * (1 if d.x > 0 else -1)    # arms DOWN (like in game)
    h = pb.head.copy()
    inv3 = arm.matrix_world.inverted().to_3x3()
    q = Matrix.Rotation(ang, 4, (inv3 @ axis_w).normalized())
    pb.matrix = Matrix.Translation(h) @ q @ Matrix.Translation(-h) @ pb.matrix
    bpy.context.view_layer.update()
pbh = arm.pose.bones["head"]
pbh.rotation_mode = "XYZ"
pbh.rotation_euler = (0, 0, math.radians(35))
bpy.context.view_layer.update()
bpy.ops.object.mode_set(mode="OBJECT")
render("4_testpose_front", "front", [model])
render("5_testpose_side", "side", [model])
activate(arm)
bpy.ops.object.mode_set(mode="POSE")
bpy.ops.pose.select_all(action="SELECT")
bpy.ops.pose.transforms_clear()
bpy.ops.object.mode_set(mode="OBJECT")
step("test renders written")

# ------------------------------------------------------------------ export
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "auto_result.blend"))
# Headless FBX import of the UE reference gives armature scale 1 with centimetre data; a GUI import (the flow that
# is known to work in UE) has armature scale 0.01 -> metres. Match it, or UE gets a 100x giant.
if U > 10:
    arm.scale = arm.scale * (1.0 / 100.0)
    arm.location = arm.location * (1.0 / 100.0)
    bpy.context.view_layer.update()
    # mesh: metre data + scale 1 like the GUI export (keeps the Armature modifier; FBX writes the mesh top-level anyway)
    activate(model)
    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    model.parent = arm
    model.matrix_parent_inverse = arm.matrix_world.inverted()
    bpy.context.view_layer.update()
if CFG.get("material_name") and model.data.materials:
    model.data.materials[0].name = CFG["material_name"]   # keep the UE material slot name of the previous import
activate(arm, model)
bpy.ops.export_scene.fbx(filepath=CFG["out_fbx"], use_selection=True, object_types={"ARMATURE", "MESH"},
                         add_leaf_bones=False, bake_anim=False, use_armature_deform_only=False,
                         mesh_smooth_type="FACE", path_mode="COPY", embed_textures=True)
step("exported", fbx=CFG["out_fbx"], size=os.path.getsize(CFG["out_fbx"]))
