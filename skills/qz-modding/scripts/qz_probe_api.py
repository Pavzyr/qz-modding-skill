"""Probe the editor Python API surface relevant to mod authoring/packaging. Runs INSIDE Unreal.
Writes %LOCALAPPDATA%/QZSim/Saved/ModSchema/deep/api_probe.json
Run as commandlet:  UnrealEditor-Cmd.exe QZSim.uproject -Installed -run=pythonscript -script=<this>
or in editor:       UnrealEditor.exe QZSim.uproject -Installed -ExecutePythonScript=<this> -unattended
"""
import json, os, inspect
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep")
os.makedirs(OUT, exist_ok=True)
res = {"is_commandlet": None, "classes": {}, "plugins": {}, "settings": {}, "misc": {}}

try:
    res["is_commandlet"] = unreal.SystemLibrary.is_commandlet() if hasattr(unreal.SystemLibrary, "is_commandlet") else "n/a"
except Exception as e:
    res["is_commandlet"] = str(e)

NAMES = ["UGCTemplateSubsystem", "UGCLibrary", "UGCSubsystem", "UGCMutatorSubsystem", "QzModioSubsystem",
         "ModioEditorUtilityFunctions", "ModioUGCEditorSettings", "PluginBlueprintLibrary", "EditorAssetLibrary",
         "EditorAssetSubsystem", "AssetToolsHelpers", "AssetTools", "EditorLoadingAndSavingUtils",
         "BlueprintEditorLibrary", "KismetEditorUtilities", "DataAssetFactory", "BlueprintFactory",
         "GameplayTagLibrary", "BlueprintGameplayTagLibrary", "SkeletalMeshEditorSubsystem",
         "InterchangeManager", "AssetImportTask", "FbxImportUI", "EditorUtilityLibrary", "AutomationLibrary"]
for n in NAMES + sorted(x for x in dir(unreal) if "GameplayTag" in x and "Library" in x):
    c = getattr(unreal, n, None)
    if c is None:
        res["classes"][n] = None
        continue
    meths = {}
    for m in dir(c):
        if m.startswith("_"):
            continue
        try:
            a = getattr(c, m)
        except Exception:
            continue
        if callable(a):
            doc = (getattr(a, "__doc__", "") or "").strip().splitlines()
            meths[m] = doc[0][:250] if doc else ""
    res["classes"][n] = meths

# plugin manager view
try:
    lib = getattr(unreal, "PluginBlueprintLibrary", None)
    if lib:
        res["plugins"]["enabled"] = [str(p) for p in lib.get_enabled_plugin_names()]
        for p in ("ModioUGC", "modio", "QZSim"):
            try:
                res["plugins"]["base_dir_" + p] = str(lib.get_plugin_base_dir(p))
            except Exception as e:
                res["plugins"]["base_dir_" + p] = "err " + str(e)
except Exception as e:
    res["plugins"]["err"] = str(e)

# settings CDOs
for path in ("/Script/ModioUGC.Default__ModioUGCSettings", "/Script/ModioUGCEditor.Default__ModioUGCEditorSettings",
             "/Script/QZSim.Default__QzGameSettings"):
    try:
        o = unreal.find_object(None, path)
        if o is None:
            res["settings"][path] = None
            continue
        vals = {}
        for line in (type(o).__doc__ or "").splitlines():
            line = line.strip()
            if line.startswith("- ``"):
                p = line[4:line.index("``", 4)]
                try:
                    vals[p] = str(o.get_editor_property(p))[:300]
                except Exception as e:
                    vals[p] = "err"
        res["settings"][path] = {"class": o.get_class().get_name(), "values": vals}
    except Exception as e:
        res["settings"][path] = "err " + str(e)

res["misc"]["project_dir"] = unreal.Paths.project_dir()
res["misc"]["saved_dir"] = unreal.Paths.project_saved_dir()
res["misc"]["project_plugins_dir"] = unreal.Paths.project_plugins_dir()
res["misc"]["mods_dir_exists"] = os.path.isdir(os.path.join(unreal.Paths.project_dir(), "Mods"))

with open(os.path.join(OUT, "api_probe.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
unreal.log("[qz_probe_api] done")
