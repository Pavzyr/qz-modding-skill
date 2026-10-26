"""Deep schema dump for the qz-modding skill. Runs INSIDE Unreal (PythonScriptPlugin).

Run (commandlet, no window):
  Engine\\Engine\\Binaries\\Win64\\UnrealEditor-Cmd.exe QZSim\\QZSim.uproject -Installed
      -run=pythonscript -script="<abs path to this file>" -unattended -nosplash -stdout
Output: QZSim/Saved/ModSchema/deep/*.json  (+ progress.log)

What it writes:
  classes.json      - every unreal.Qz*/Sim*/Modio*/UGC* class: parent chain + editor properties (name, type, doc)
  blueprints.json   - every Blueprint asset under /Game and /Mods-like plugin roots with its ParentClass tag
  data_assets.json  - every asset under /Game/Data: path + class
  samples.json      - property values of sample data assets (per class / per folder)
  skeletons.json    - Skeleton assets + skeletons used by sampled meshes
  settings.json     - ModioUGC settings (RequiredModGameVersion etc.), engine version
  tags.json         - all registered gameplay tags (if API allows)
"""
import json, os, re, traceback, time
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep")
os.makedirs(OUT, exist_ok=True)
LOG = open(os.path.join(OUT, "progress.log"), "w", encoding="utf-8")


def log(msg):
    LOG.write(time.strftime("%H:%M:%S ") + msg + "\n"); LOG.flush()
    unreal.log("[qz_deep_dump] " + msg)


def dump(name, obj):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    log("wrote " + name)


PROP_RE = re.compile(r"^\s*-\s*``(\w+)``\s*\(([^)]*)\):\s*(.*)$")


def class_props(cls):
    props = {}
    for line in (cls.__doc__ or "").splitlines():
        m = PROP_RE.match(line)
        if m:
            props[m.group(1)] = {"type": m.group(2).strip(), "doc": m.group(3).strip()[:300]}
    return props


def short(v, depth=0):
    """JSON-friendly, size-limited representation of an Unreal value."""
    try:
        if v is None or isinstance(v, (bool, int, float, str)):
            return v if not isinstance(v, str) else v[:500]
        if isinstance(v, unreal.Object):
            return "<%s> %s" % (v.get_class().get_name(), v.get_path_name())
        if isinstance(v, (list, tuple, unreal.Array, set, unreal.Set)):
            items = list(v)
            r = [short(x, depth + 1) for x in items[:15]]
            if len(items) > 15:
                r.append("... +%d more" % (len(items) - 15))
            return r
        if isinstance(v, (dict, unreal.Map)):
            r = {}
            for i, (k, x) in enumerate(v.items()):
                if i >= 15:
                    r["..."] = "+%d more" % (len(v) - 15); break
                r[str(short(k, depth + 1))] = short(x, depth + 1)
            return r
        if isinstance(v, unreal.StructBase) and depth < 3:
            r = {"__struct__": type(v).__name__}
            for p in class_props(type(v)):
                try:
                    r[p] = short(v.get_editor_property(p), depth + 1)
                except Exception:
                    pass
            if len(r) > 1:
                return r
        return str(v)[:500]
    except Exception as e:
        return "<err %s>" % e


def obj_values(o):
    vals = {}
    for p in class_props(type(o)):
        try:
            vals[p] = short(o.get_editor_property(p))
        except Exception as e:
            vals[p] = "<unreadable: %s>" % str(e)[:80]
    return vals


reg = unreal.AssetRegistryHelpers.get_asset_registry()
try:
    reg.search_all_assets(True)
except Exception:
    pass

# ---------------------------------------------------------------- 1. classes
try:
    names = sorted(n for n in dir(unreal) if re.match(r"^(Qz|QZ|Sim|Modio|UGC|ModioUGC)", n))
    classes = {}
    for n in names:
        cls = getattr(unreal, n)
        if not isinstance(cls, type):
            continue
        chain = [c.__name__ for c in cls.__mro__[1:6]]
        doc = (cls.__doc__ or "").strip().splitlines()
        classes[n] = {"chain": chain, "summary": " ".join(doc[:3])[:400], "props": class_props(cls)}
    dump("classes.json", classes)
except Exception:
    log("classes FAILED\n" + traceback.format_exc())

# ---------------------------------------------------------------- 2. data assets + blueprints
try:
    rows = []
    for a in reg.get_assets_by_path("/Game/Data", recursive=True):
        rows.append({"path": str(a.package_name), "class": str(a.asset_class_path.asset_name)})
    dump("data_assets.json", rows)
except Exception:
    log("data_assets FAILED\n" + traceback.format_exc())

try:
    bps = []
    for cls_name in ("Blueprint", "WidgetBlueprint", "AnimBlueprint"):
        pkg = "/Script/UMGEditor" if cls_name == "WidgetBlueprint" else "/Script/Engine"
        for a in reg.get_assets_by_class(unreal.TopLevelAssetPath(pkg, cls_name), True):
            path = str(a.package_name)
            if not path.startswith("/Game/") or "/MetaHumans/" in path:
                continue
            bps.append({"path": path, "type": cls_name,
                        "parent": str(a.get_tag_value("ParentClass")),
                        "native_parent": str(a.get_tag_value("NativeParentClass"))})
    dump("blueprints.json", bps)
except Exception:
    log("blueprints FAILED\n" + traceback.format_exc())

# ---------------------------------------------------------------- 3. settings
try:
    s = {"engine": unreal.SystemLibrary.get_engine_version()}
    for cname in ("ModioUGCSettings", "ModioSettings"):
        c = getattr(unreal, cname, None)
        if c:
            try:
                s[cname] = obj_values(unreal.get_default_object(c))
            except Exception as e:
                s[cname] = "<err %s>" % e
    dump("settings.json", s)
except Exception:
    log("settings FAILED\n" + traceback.format_exc())

# ---------------------------------------------------------------- 4. samples (loads assets)
SAMPLE_FOLDERS = {
    # folder: max assets to load
    "/Game/Data/Tools": 20, "/Game/Data/Levels": 5, "/Game/Data/Symptoms/Sections": 20,
    "/Game/Data/Handbook": 2, "/Game/Data/HiddenContraband": 3, "/Game/Data/InternalContrabands": 3,
    "/Game/Data/BaggageItems": 3, "/Game/Data/GameFlow": 10, "/Game/Data/UI": 10, "/Game/Data/Base": 16,
    "/Game/Data/Common": 5, "/Game/Data/Rewards": 2, "/Game/Data/Military": 6, "/Game/Data/Player": 8,
}
SAMPLE_PER_CLASS = 3          # for everything else in /Game/Data: first N per class
SAMPLE_SUBFOLDERS = ["/Game/Data/GeneratorApperance", "/Game/Data/Symptoms/Items",
                     "/Game/Data/Companies", "/Game/Data/Profiles", "/Game/Data/DaysConfigs"]

samples, skel_used = {}, {}


def note_skeletons(path, vals_obj):
    for p in class_props(type(vals_obj)):
        try:
            v = vals_obj.get_editor_property(p)
        except Exception:
            continue
        vs = list(v) if isinstance(v, (unreal.Array, list)) else [v]
        for x in vs:
            if isinstance(x, unreal.SkeletalMesh):
                try:
                    sk = x.get_editor_property("skeleton")
                    skel_used.setdefault(sk.get_path_name() if sk else "None", []).append(
                        "%s.%s -> %s" % (path, p, x.get_path_name()))
                except Exception:
                    pass


def sample(path):
    if path in samples:
        return
    try:
        o = unreal.EditorAssetLibrary.load_asset(path)
        if o is None:
            samples[path] = "<load failed>"; return
        entry = {"class": o.get_class().get_name(), "values": obj_values(o)}
        if isinstance(o, unreal.Blueprint):
            try:
                gen = unreal.EditorAssetLibrary.load_blueprint_class(path)
                entry["cdo"] = obj_values(unreal.get_default_object(gen))
            except Exception:
                pass
        samples[path] = entry
        note_skeletons(path, o)
    except Exception as e:
        samples[path] = "<err %s>" % str(e)[:200]


try:
    all_data = reg.get_assets_by_path("/Game/Data", recursive=True)
    by_folder = {}
    for a in all_data:
        by_folder.setdefault(str(a.package_path), []).append(a)
    # fixed folders
    for folder, n in SAMPLE_FOLDERS.items():
        for a in sorted(by_folder.get(folder, []), key=lambda a: str(a.asset_name))[:n]:
            sample(str(a.package_name))
    # 2 per leaf folder in the big trees
    for folder, assets in sorted(by_folder.items()):
        if any(folder.startswith(r) for r in SAMPLE_SUBFOLDERS):
            for a in sorted(assets, key=lambda a: str(a.asset_name))[:2]:
                sample(str(a.package_name))
    # N per class for everything else
    seen = {}
    for a in sorted(all_data, key=lambda a: str(a.package_name)):
        c = str(a.asset_class_path.asset_name)
        if seen.get(c, 0) < SAMPLE_PER_CLASS:
            seen[c] = seen.get(c, 0) + 1
            sample(str(a.package_name))
        if len(samples) % 50 == 0:
            unreal.SystemLibrary.collect_garbage()
    # base tool blueprints
    for a in reg.get_assets_by_path("/Game/Blueprints/Tools", recursive=True):
        if str(a.asset_class_path.asset_name) == "Blueprint":
            sample(str(a.package_name))
    log("samples: %d" % len(samples))
    dump("samples.json", samples)
except Exception:
    log("samples FAILED\n" + traceback.format_exc())
    dump("samples.json", samples)

# ---------------------------------------------------------------- 5. skeletons
try:
    sks = [str(a.package_name) for a in
           reg.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine", "Skeleton"), True)]
    dump("skeletons.json", {"all_skeletons": sorted(sks), "used_by_sampled_assets": skel_used})
except Exception:
    log("skeletons FAILED\n" + traceback.format_exc())

# ---------------------------------------------------------------- 6. tags
try:
    tags = []
    lib = unreal.BlueprintGameplayTagLibrary
    for fn in ("get_all_gameplay_tags",):
        if hasattr(lib, fn):
            tags = [str(t) for t in getattr(lib, fn)()]
    dump("tags.json", tags)
except Exception:
    log("tags FAILED\n" + traceback.format_exc())

log("DONE")
LOG.close()
