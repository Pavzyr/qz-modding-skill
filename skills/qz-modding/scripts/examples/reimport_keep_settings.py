# Job "py" op: re-import a skeletal mesh + textures OVER existing mod assets (same paths), keeping their settings.
# args: {"mesh": "/MyMod/SK_MyChar", "fbx": "C:/.../SK_MyChar.fbx",
#        "textures": {"/Mod/T_X_BaseColor": "C:/.../T_X_BaseColor.jpg", ...}}
# Before: snapshot texture settings (sRGB, compression, flip green, LOD group), mesh skeleton/materials/physics asset.
# Import with replace_existing (legacy FBX path, existing skeleton, no new materials/textures). After: restore snapshot.
# Report: REPORT["reimport"] = {before, after}.
import unreal

A = ARGS
TEX_PROPS = ("srgb", "compression_settings", "flip_green_channel", "lod_group", "mip_gen_settings")


def tex_info(t):
    d = {}
    for p in TEX_PROPS:
        try:
            d[p] = t.get_editor_property(p)
        except Exception:
            pass
    d["size"] = [t.blueprint_get_size_x(), t.blueprint_get_size_y()]
    try:
        d["source"] = [str(f.get_editor_property("relative_filename")) for f in
                       t.get_editor_property("asset_import_data").get_editor_property("source_data").get_editor_property("source_files")]
    except Exception:
        d["source"] = "?"
    return d


def mesh_info(m):
    d = {"skeleton": m.get_editor_property("skeleton").get_path_name() if m.get_editor_property("skeleton") else None}
    pa = m.get_editor_property("physics_asset")
    d["physics_asset"] = pa.get_path_name() if pa else None
    d["materials"] = [(str(sm.get_editor_property("material_slot_name")),
                       sm.get_editor_property("material_interface").get_path_name() if sm.get_editor_property("material_interface") else None)
                      for sm in m.get_editor_property("materials")]
    try:
        lod = unreal.SkeletalMeshEditorSubsystem
        d["verts_lod0"] = unreal.get_editor_subsystem(lod).get_num_verts(m, 0)
    except Exception as ex:
        d["verts_lod0"] = "?%s" % ex
    bb = m.get_bounds()
    d["bounds_box_extent_cm"] = [round(x, 1) for x in (bb.box_extent.x, bb.box_extent.y, bb.box_extent.z)]
    return d


def jsonable(d):
    return {k: (str(v) if not isinstance(v, (int, float, str, list, type(None), bool)) else v) for k, v in d.items()}


unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX false")
rep = {"before": {}, "after": {}}
mesh = EAS.load_asset(A["mesh"])
mb = mesh_info(mesh)
rep["before"][A["mesh"]] = jsonable(mb)
skel = mesh.get_editor_property("skeleton")
mats_before = [sm.get_editor_property("material_interface") for sm in mesh.get_editor_property("materials")]
pa_before = mesh.get_editor_property("physics_asset")
tex_before = {}
for path in A["textures"]:
    t = EAS.load_asset(path)
    tex_before[path] = {p: t.get_editor_property(p) for p in TEX_PROPS if t is not None}
    rep["before"][path] = jsonable(tex_info(t))

# --- mesh
pkg, name = A["mesh"].rsplit("/", 1)
t = unreal.AssetImportTask()
t.set_editor_property("filename", A["fbx"])
t.set_editor_property("destination_path", pkg)
t.set_editor_property("destination_name", name)
t.set_editor_property("automated", True)
t.set_editor_property("replace_existing", True)
t.set_editor_property("save", False)
ui = unreal.FbxImportUI()
ui.set_editor_property("import_mesh", True)
ui.set_editor_property("import_as_skeletal", True)
ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
ui.set_editor_property("import_materials", False)
ui.set_editor_property("import_textures", False)
ui.set_editor_property("import_animations", False)
ui.set_editor_property("create_physics_asset", False)
ui.set_editor_property("skeleton", skel)
t.set_editor_property("options", ui)
tasks = [t]
# --- textures
for path, f in A["textures"].items():
    tp, tn = path.rsplit("/", 1)
    tt = unreal.AssetImportTask()
    tt.set_editor_property("filename", f)
    tt.set_editor_property("destination_path", tp)
    tt.set_editor_property("destination_name", tn)
    tt.set_editor_property("automated", True)
    tt.set_editor_property("replace_existing", True)
    tt.set_editor_property("save", False)
    tasks.append(tt)
TOOLS.import_asset_tasks(tasks)
for tk in tasks:
    got = [str(p) for p in tk.get_editor_property("imported_object_paths")]
    log("imported %s -> %s" % (tk.get_editor_property("filename"), got))
    if not got:
        raise RuntimeError("import produced nothing: " + tk.get_editor_property("filename"))

# --- restore settings
mesh = EAS.load_asset(A["mesh"])
if mesh.get_editor_property("skeleton") != skel:
    raise RuntimeError("skeleton changed on reimport: %s" % mesh.get_editor_property("skeleton"))
sms = mesh.get_editor_property("materials")
for i, sm in enumerate(sms):
    if i < len(mats_before) and mats_before[i] is not None:
        sm.set_editor_property("material_interface", mats_before[i])
mesh.set_editor_property("materials", sms)
if pa_before is not None:
    mesh.set_editor_property("physics_asset", pa_before)
EAS.save_loaded_asset(mesh, False)
for path, props in tex_before.items():
    tx = EAS.load_asset(path)
    for p, v in props.items():
        tx.set_editor_property(p, v)
    EAS.save_loaded_asset(tx, False)

rep["after"][A["mesh"]] = jsonable(mesh_info(mesh))
for path in A["textures"]:
    rep["after"][path] = jsonable(tex_info(EAS.load_asset(path)))
REPORT["reimport"] = rep
log("reimport done")
