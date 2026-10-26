"""Execute a JSON "mod job" inside Unreal: create the mod plugin, import files, create/duplicate assets,
set properties, create child Blueprints, save. Everything lands in /<ModName>/... (the mod plugin).

Run (no window):
  Engine\\Engine\\Binaries\\Win64\\UnrealEditor-Cmd.exe QZSim\\QZSim.uproject -Installed -run=pythonscript
      -script="<abs>/qz_mod_job.py <abs>/job.json" -unattended -nosplash -stdout
  (exit code may be 1 because of unrelated base-game errors in the log — read the job report instead)
Report: <job.json without ext>.report.json  (+ lines tagged [qz_mod_job] in the log)

Job format:
{
  "mod": "MyMod",                                  # plugin name == content root /MyMod/
  "ops": [
    {"op": "create_mod", "description": "...", "author": "...", "template": "BaseTemplate"},
    {"op": "import", "files": ["C:/in/SK_X.fbx"], "dest": "/MyMod/Meshes", "skeleton": "/Game/.../SK_Skel",
                     "static": false, "replace": true},
    {"op": "duplicate", "src": "/Game/Data/Tools/DA_UVStick", "dst": "/MyMod/Tools/DA_MyTool"},
    {"op": "create_asset", "class": "QzStaticNPCSkinDataAsset", "path": "/MyMod/Skins/DA_Skin_Doc",
                           "props": {"npc_tag": {"$tag": "NPC.Skin.Doc"}}},
    {"op": "create_mi", "parent": "/Game/.../M_Base", "path": "/MyMod/Materials/MI_X",
                        "scalars": {"Roughness": 0.5}, "vectors": {"Tint": [1,0,0,1]}, "textures": {"BaseColor": "/MyMod/T_X"}},
    {"op": "create_blueprint", "parent": "/Game/Blueprints/Tools/UVStick/BP_UVStick" | "QzToolComponent",
                               "path": "/MyMod/Tools/BP_MyTool", "cdo": {"prop": value}},
    {"op": "set", "path": "/MyMod/Tools/DA_MyTool", "props": {...}},
    {"op": "py", "file": "build_x.py", "args": {}},   # custom build step, runs with this module's globals (relative = next to the job file)
    {"op": "save"}
  ]
}
Value encoding in "props"/"cdo":
  "/Game/x/y" or "/MyMod/x"     -> loaded asset (object reference)
  {"$tag": "A.B"}               -> GameplayTag;   {"$tags": ["A.B","C"]} -> GameplayTagContainer
  {"$map": {"0": "/Game/M"}}    -> Map (keys converted to int when numeric)
  {"$text": "..."}              -> Text;   {"$name": "..."} -> Name;   {"$enum": "EnumType.VALUE"} -> enum
  {"$struct": "StructType", "fields": {...}}  -> struct
  {"$soft": "/Game/Maps/X"}     -> soft object path string (for TSoftObjectPtr props)
  plain numbers/bools/strings/lists -> as is
"""
import json, os, sys, traceback
import unreal

ARGS = [a for a in sys.argv[1:] if a.lower().endswith(".json")]
JOB_PATH = ARGS[0] if ARGS else os.environ.get("QZ_JOB", "")
REPORT = {"job": JOB_PATH, "ok": [], "errors": [], "created": []}
EAS = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()


def log(msg):
    unreal.log("[qz_mod_job] " + msg)


def tag(name):
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % name)
    if str(unreal.GameplayTagLibrary.get_tag_name(t)) != name:
        raise ValueError("GameplayTag not registered: %s (declare it in Config/Tags/*.ini of the mod)" % name)
    return t


def conv(v):
    if isinstance(v, str) and v.startswith("/") and not v.startswith("//"):
        o = EAS.load_asset(v)
        if o is None:
            raise ValueError("asset not found: " + v)
        return o
    if isinstance(v, list):
        return [conv(x) for x in v]
    if isinstance(v, dict):
        if "$tag" in v:
            return tag(v["$tag"])
        if "$tags" in v:
            return unreal.GameplayTagLibrary.make_gameplay_tag_container_from_array([tag(x) for x in v["$tags"]])
        if "$map" in v:
            return {(int(k) if str(k).lstrip("-").isdigit() else k): conv(x) for k, x in v["$map"].items()}
        if "$text" in v:
            return unreal.Text(v["$text"])
        if "$name" in v:
            return unreal.Name(v["$name"])
        if "$soft" in v:
            return unreal.SoftObjectPath(v["$soft"])
        if "$enum" in v:
            et, ev = v["$enum"].split(".", 1)
            return getattr(getattr(unreal, et), ev)
        if "$struct" in v:
            s = getattr(unreal, v["$struct"])()
            for k, x in v.get("fields", {}).items():
                s.set_editor_property(k, conv(x))
            return s
    return v


def set_props(obj, props):
    for k, v in (props or {}).items():
        obj.set_editor_property(k, conv(v))


def split(path):
    pkg, name = path.rsplit("/", 1)
    return pkg, name


# ------------------------------------------------------------------ ops
MODS_DIR = os.path.abspath(os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()), "Mods"))


def required_game_version():
    """RequiredModGameVersion from QZSim/Config/DefaultGame.ini (fallback 4)."""
    ini = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_config_dir()), "DefaultGame.ini")
    try:
        for line in open(ini, encoding="utf-8-sig"):
            if line.strip().startswith("RequiredModGameVersion="):
                return int(line.split("=", 1)[1])
    except Exception:
        pass
    return 4


def scaffold_plugin(mod, op):
    """Write the plugin skeleton on disk exactly like real mods have it (fields copied from mod.io mods)."""
    root = os.path.join(MODS_DIR, mod)
    os.makedirs(os.path.join(root, "Content"), exist_ok=True)
    os.makedirs(os.path.join(root, "Config", "Tags"), exist_ok=True)
    up = os.path.join(root, mod + ".uplugin")
    if not os.path.exists(up):
        d = {"FileVersion": 3, "Version": 1, "VersionName": op.get("version_name", "1.0"),
             "FriendlyName": op.get("friendly_name", mod), "Description": op.get("description", ""),
             "Category": "UGC", "CreatedBy": op.get("author", ""), "CreatedByURL": "", "DocsURL": "",
             "MarketplaceURL": "", "SupportURL": "", "CanContainContent": True, "IsBetaVersion": False,
             "IsExperimentalVersion": False, "Installed": False,
             # UGCSubsystem refuses to mount without these ("uplugin missing engine version").
             # Package UGC re-stamps them on packaging anyway.
             "ExplicitlyLoaded": True, "EngineVersion": op.get("engine_version", "5.7.0-0+UE5-QZ"),
             "GameVersion": int(op.get("game_version", required_game_version()))}
        with open(up, "w", encoding="utf-8", newline="\n") as f:
            json.dump(d, f, indent="\t", ensure_ascii=False)
    icon_src = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_plugins_dir()),
                            "ModioUGC", "Templates", "BaseTemplate", "Resources", "Icon128.png")
    icon_dst = os.path.join(root, "Resources", "Icon128.png")
    if os.path.exists(icon_src) and not os.path.exists(icon_dst):
        os.makedirs(os.path.dirname(icon_dst), exist_ok=True)
        open(icon_dst, "wb").write(open(icon_src, "rb").read())
    return root


def mount(mod, root):
    lib = unreal.PluginBlueprintLibrary
    if lib.is_plugin_mounted(mod):
        return True
    try:
        ugc = unreal.get_engine_subsystem(unreal.UGCSubsystem)
        ugc.add_ugc_from_path(root)
    except Exception as e:
        log("add_ugc_from_path failed: %s" % e)
    ok = lib.is_plugin_mounted(mod)
    log("mounted=%s search_paths=%s" % (ok, list(lib.get_additional_project_plugin_search_paths())))
    return ok


def op_create_mod(job, op):
    mod = job["mod"]
    lib = unreal.PluginBlueprintLibrary
    if lib.get_plugin_base_dir(mod):
        log("mod plugin already known: %s" % lib.get_plugin_base_dir(mod))
    else:
        created = False
        try:   # the official Create UGC path (works in the full editor; has no templates in commandlet mode)
            sub = unreal.get_editor_subsystem(unreal.UGCTemplateSubsystem)
            templates = list(sub.get_templates() or sub.discover_templates())
            want = op.get("template", "BaseTemplate")
            tinfo = next((t for t in templates if want.lower() in str(t).lower()), templates[0] if templates else None)
            if tinfo is not None:
                created = bool(sub.create_ugc_from_template(mod, tinfo, {}))
                log("create_ugc_from_template(%s) -> %s" % (tinfo, created))
        except Exception as e:
            log("UGC template path failed: %s" % e)
        if not created:
            root = scaffold_plugin(mod, op)
            log("scaffolded plugin at " + root)
    root = lib.get_plugin_base_dir(mod) or os.path.join(MODS_DIR, mod)
    if not mount(mod, str(root)):
        raise RuntimeError("plugin %s exists on disk but is not mounted (run in full editor or restart)" % mod)
    base = lib.get_plugin_base_dir(mod)
    REPORT["plugin_dir"] = str(base)
    # descriptor fields
    if base:
        up = os.path.join(str(base), mod + ".uplugin")
        if os.path.exists(up):
            d = json.load(open(up, encoding="utf-8-sig"))
            for k_json, k_op in (("Description", "description"), ("CreatedBy", "author"), ("VersionName", "version_name"),
                                 ("FriendlyName", "friendly_name")):
                if op.get(k_op):
                    d[k_json] = op[k_op]
            with open(up, "w", encoding="utf-8", newline="\n") as f:   # UTF-8 without BOM
                json.dump(d, f, indent="\t", ensure_ascii=False)
    # metadata asset
    meta = "/%s/UUGC_Metadata" % mod
    if not EAS.does_asset_exist(meta):
        o = TOOLS.create_asset("UUGC_Metadata", "/" + mod, unreal.UGC_Metadata, unreal.DataAssetFactory())
        REPORT["created"].append(meta)
    o = EAS.load_asset(meta)
    if o is not None:
        o.set_editor_property("io_store_enabled", True)
        EAS.save_loaded_asset(o, False)


def op_import(job, op):
    tasks = []
    for f in op["files"]:
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", f)
        t.set_editor_property("destination_path", op["dest"])
        t.set_editor_property("automated", True)
        t.set_editor_property("replace_existing", op.get("replace", True))
        t.set_editor_property("save", True)
        if f.lower().endswith(".fbx"):
            ui = unreal.FbxImportUI()
            static = op.get("static", False)
            ui.set_editor_property("import_mesh", True)
            ui.set_editor_property("import_as_skeletal", not static)
            ui.set_editor_property("mesh_type_to_import",
                                   unreal.FBXImportType.FBXIT_STATIC_MESH if static else unreal.FBXImportType.FBXIT_SKELETAL_MESH)
            ui.set_editor_property("import_materials", op.get("import_materials", True))
            ui.set_editor_property("import_textures", op.get("import_textures", True))
            ui.set_editor_property("import_animations", op.get("import_animations", False))
            if op.get("skeleton"):
                ui.set_editor_property("skeleton", EAS.load_asset(op["skeleton"]))
            t.set_editor_property("options", ui)
        tasks.append(t)
    TOOLS.import_asset_tasks(tasks)
    for t in tasks:
        paths = [str(p) for p in t.get_editor_property("imported_object_paths")]
        REPORT["created"] += paths
        if not paths:
            raise RuntimeError("import produced nothing: " + t.get_editor_property("filename"))


def op_duplicate(job, op):
    o = EAS.duplicate_asset(op["src"], op["dst"])
    if o is None:
        raise RuntimeError("duplicate failed %s -> %s" % (op["src"], op["dst"]))
    set_props(o, op.get("props"))
    EAS.save_loaded_asset(o, False)
    REPORT["created"].append(op["dst"])


def op_create_asset(job, op):
    pkg, name = split(op["path"])
    cls = getattr(unreal, op["class"])
    if EAS.does_asset_exist(op["path"]):
        o = EAS.load_asset(op["path"])
    else:
        factory = unreal.DataAssetFactory() if issubclass(cls, unreal.DataAsset) else None
        o = TOOLS.create_asset(name, pkg, cls, factory)
    if o is None:
        raise RuntimeError("create_asset failed: " + op["path"])
    set_props(o, op.get("props"))
    EAS.save_loaded_asset(o, False)
    REPORT["created"].append(op["path"])


def op_create_mi(job, op):
    pkg, name = split(op["path"])
    mi = EAS.load_asset(op["path"]) if EAS.does_asset_exist(op["path"]) else \
        TOOLS.create_asset(name, pkg, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel = unreal.MaterialEditingLibrary
    mel.set_material_instance_parent(mi, EAS.load_asset(op["parent"]))
    for k, v in op.get("scalars", {}).items():
        mel.set_material_instance_scalar_parameter_value(mi, k, float(v))
    for k, v in op.get("vectors", {}).items():
        mel.set_material_instance_vector_parameter_value(mi, k, unreal.LinearColor(*v))
    for k, v in op.get("textures", {}).items():
        mel.set_material_instance_texture_parameter_value(mi, k, EAS.load_asset(v))
    mel.update_material_instance(mi)
    EAS.save_loaded_asset(mi, False)
    REPORT["created"].append(op["path"])


def op_create_blueprint(job, op):
    parent = op["parent"]
    if parent.startswith("/"):
        parent_cls = EAS.load_blueprint_class(parent)
    else:
        parent_cls = getattr(unreal, parent)
    bp = EAS.load_asset(op["path"]) if EAS.does_asset_exist(op["path"]) else \
        unreal.BlueprintEditorLibrary.create_blueprint_asset_with_parent(op["path"], parent_cls)
    if bp is None:
        raise RuntimeError("create_blueprint failed: " + op["path"])
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    if op.get("cdo"):
        cdo = unreal.get_default_object(unreal.BlueprintEditorLibrary.generated_class(bp))
        set_props(cdo, op["cdo"])
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    EAS.save_loaded_asset(bp, False)
    REPORT["created"].append(op["path"])


def op_set(job, op):
    o = EAS.load_asset(op["path"])
    set_props(o, op.get("props"))
    EAS.save_loaded_asset(o, False)


def op_save(job, op):
    EAS.save_directory("/" + job["mod"], only_if_is_dirty=False, recursive=True)


def _vals(o):
    out = {}
    for line in (type(o).__doc__ or "").splitlines():
        line = line.strip()
        if line.startswith("- ``"):
            p = line[4:line.index("``", 4)]
            try:
                out[p] = _show(o.get_editor_property(p))
            except Exception:
                pass
    return out


def _show(v):
    """str() of GameplayTag/Container prints '{}' — resolve real tag names."""
    if isinstance(v, unreal.GameplayTag):
        return "Tag(%s)" % unreal.GameplayTagLibrary.get_tag_name(v)
    if isinstance(v, unreal.GameplayTagContainer):
        return "Tags(%s)" % [str(unreal.GameplayTagLibrary.get_tag_name(t))
                             for t in unreal.GameplayTagLibrary.break_gameplay_tag_container(v)]
    return str(v)[:400]


def op_inspect(job, op):
    """{"op":"inspect","paths":["/Mod/DA_X", "/Game/..."]} -> report["inspect"][path] = {class, values, skeleton?}"""
    res = REPORT.setdefault("inspect", {})
    for p in op["paths"]:
        o = EAS.load_asset(p)
        if o is None:
            res[p] = "not found"
            continue
        e = {"class": o.get_class().get_name(), "values": _vals(o)}
        if isinstance(o, unreal.SkeletalMesh):
            sk = o.get_editor_property("skeleton")
            e["skeleton"] = sk.get_path_name() if sk else None
            e["materials"] = [str(m.get_editor_property("material_slot_name")) for m in o.get_editor_property("materials")]
        if isinstance(o, unreal.Blueprint):
            try:
                e["cdo"] = _vals(unreal.get_default_object(EAS.load_blueprint_class(p)))
            except Exception:
                pass
        res[p] = e


def op_export(job, op):
    """{"op":"export","paths":["/Game/.../SK_X"],"dir":"C:/out"} -> FBX/PNG files for Blender reference."""
    os.makedirs(op["dir"], exist_ok=True)
    out = REPORT.setdefault("exported", [])
    for p in op["paths"]:
        o = EAS.load_asset(p)
        if o is None:
            raise RuntimeError("not found: " + p)
        ext = "fbx" if isinstance(o, (unreal.SkeletalMesh, unreal.StaticMesh, unreal.AnimSequence, unreal.Skeleton)) else "png"
        fn = os.path.join(op["dir"], "%s.%s" % (o.get_name(), ext))
        t = unreal.AssetExportTask()
        t.set_editor_property("object", o)
        t.set_editor_property("filename", fn)
        t.set_editor_property("automated", True)
        t.set_editor_property("prompt", False)
        t.set_editor_property("replace_identical", True)
        if ext == "fbx":
            opts = unreal.FbxExportOption()
            # LOD export goes through MeshMergeUtilities and crashed on MetaHuman clothes (array OOB)
            for k, v in (("export_morph_targets", False), ("level_of_detail", False), ("collision", False),
                         ("export_preview_mesh", False), ("vertex_color", True)):
                try:
                    opts.set_editor_property(k, v)
                except Exception:
                    pass
            t.set_editor_property("options", opts)
        if not unreal.Exporter.run_asset_export_task(t):
            raise RuntimeError("export failed: " + p)
        out.append(fn)


def op_py(job, op):
    """{"op":"py","file":"build_x.py" (absolute, or relative to the job file), "args": {...}} -> exec the file inside the editor with this module's
    globals (EAS, TOOLS, conv, set_props, log, REPORT, JOB=job, ARGS=op args). For mod-specific builds (widgets, input assets, BPs)."""
    g = dict(globals())
    g["JOB"] = job
    g["ARGS"] = op.get("args", {})
    path = op["file"]
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(os.path.abspath(JOB_PATH)), path)
    exec(compile(open(path, encoding="utf-8").read(), path, "exec"), g)


OPS = {"py": op_py, "create_mod": op_create_mod, "import": op_import, "duplicate": op_duplicate,
       "create_asset": op_create_asset, "create_mi": op_create_mi, "create_blueprint": op_create_blueprint,
       "set": op_set, "save": op_save, "inspect": op_inspect, "export": op_export}


def main():
    job = json.load(open(JOB_PATH, encoding="utf-8"))
    for i, op in enumerate(job["ops"]):
        name = op.get("op")
        try:
            OPS[name](job, op)
            REPORT["ok"].append("%d:%s" % (i, name))
            log("ok %d %s" % (i, name))
            finish()   # incremental: a later crash must not lose what was done
        except Exception as e:
            REPORT["errors"].append({"i": i, "op": name, "error": str(e), "trace": traceback.format_exc()[-1500:]})
            log("FAILED %d %s: %s" % (i, name, e))
            if job.get("stop_on_error", True):
                break
    # what is in the mod now
    try:
        REPORT["mod_assets"] = [str(p) for p in EAS.list_assets("/" + job["mod"], True, False)]
    except Exception as e:
        REPORT["mod_assets"] = "err " + str(e)


def finish():
    rp = os.path.splitext(JOB_PATH)[0] + ".report.json" if JOB_PATH else os.path.join(
        unreal.Paths.project_saved_dir(), "qz_mod_job.report.json")
    with open(rp, "w", encoding="utf-8") as f:
        json.dump(REPORT, f, ensure_ascii=False, indent=1)
    log("report: " + rp)


def run_all():
    try:
        main()
    except Exception:
        REPORT["errors"].append({"fatal": traceback.format_exc()})
    finish()


# Must run in the FULL editor (UnrealEditor.exe ... -ExecutePythonScript="qz_mod_job.py job.json"): in commandlet
# mode the UGC provider is disabled and mods cannot be mounted. -ExecutePythonScript closes the editor by itself
# when the script returns, so everything runs synchronously here; add_ugc_from_path mounts synchronously.
REPORT["commandline"] = unreal.SystemLibrary.get_command_line()[:300]
run_all()
