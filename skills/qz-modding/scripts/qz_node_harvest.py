"""Harvest real Blueprint graph nodes from the base game as copy/paste text (read-only, commandlet).

  UnrealEditor-Cmd.exe QZSim.uproject -Installed -run=pythonscript -script="<abs>/qz_node_harvest.py" -unattended -nosplash -stdout

Loads Blueprints under ROOTS one by one, exports every graph node of a wanted kind to text (the same format as Ctrl+C in
the graph editor) and keeps the first example per key. Output: <Saved>/ModSchema/nodes/node_library.json
  key examples: "CallFunction:GetPlayerController", "CallArrayFunction:Array_Get", "IfThenElse", "DynamicCast",
                "SwitchEnum", "CustomEvent", "CreateWidget", "SpawnActorFromClass", "EnhancedInputAction", ...
Use with qz_bp_paste.py to compose pasteable graphs from verified nodes.
"""
import json, os, re, time
import unreal

OUT_DIR = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "nodes")
os.makedirs(OUT_DIR, exist_ok=True)
TMP = os.path.join(OUT_DIR, "_tmp.copy")
ROOTS = ["/Game/Blueprints", "/Game/UI", "/Game/MiamiPrototype", "/Game/Dev"]
WANT_FUNCS = set(os.environ.get("QZ_WANT_FUNCS", "").split(",")) - {""} or {
    "GetPlayerController", "GetPlayerCharacter", "GetPlayerPawn", "GetActorOfClass", "EnableInput", "GetActorInFocus", "GetState",
    "K2_SetTimer", "K2_SetTimerDelegate", "AddMappingContext", "AddToViewport", "GetWidgetFromName", "SetVisibility", "SetText",
    "RandomInteger", "RandomIntegerInRange", "GetCurrentCulture", "StartsWith", "IsValid", "Not_PreBool", "K2_DestroyActor",
    "RemoveFromParent", "PrintString", "Conv_StringToText", "Delay", "IsInspecting", "IsAlive", "Array_Length", "Array_Get",
    "Array_Random", "EqualEqual_ObjectObject", "NotEqual_ObjectObject", "BooleanAND", "BooleanOR", "SetTimerByFunctionName"}
WANT_KINDS = {"K2Node_IfThenElse", "K2Node_DynamicCast", "K2Node_SwitchEnum", "K2Node_CustomEvent", "K2Node_CreateWidget",
              "K2Node_SpawnActorFromClass", "K2Node_EnhancedInputAction", "K2Node_GetSubsystemFromPC", "K2Node_GetSubsystem",
              "K2Node_CallParentFunction", "K2Node_Event", "K2Node_VariableGet", "K2Node_VariableSet", "K2Node_EnumEquality",
              "K2Node_ExecutionSequence", "K2Node_MacroInstance", "K2Node_Select", "K2Node_InputKey", "K2Node_Knot",
              "K2Node_MakeStruct", "K2Node_BreakStruct", "K2Node_FormatText", "K2Node_Self", "K2Node_TemporaryVariable"}

lib = {}
_old = os.path.join(OUT_DIR, "node_library.json")
if os.path.exists(_old):          # merge: keep everything harvested before, only look for what is still missing
    try:
        lib = json.load(open(_old, encoding="utf-8")).get("lib", {})
    except Exception:
        lib = {}
stats = {"bps": 0, "nodes": 0, "t0": time.time(), "kept": len(lib)}


def export_text(node):
    t = unreal.AssetExportTask()
    t.set_editor_property("object", node)
    t.set_editor_property("filename", TMP)
    t.set_editor_property("automated", True)
    t.set_editor_property("prompt", False)
    t.set_editor_property("replace_identical", True)
    if not unreal.Exporter.run_asset_export_task(t):
        return None
    return open(TMP, encoding="utf-8", errors="replace").read()


def key_of(kind, txt):
    if kind in ("K2Node_CallFunction", "K2Node_CallArrayFunction", "K2Node_CallParentFunction"):
        m = re.search(r'FunctionReference=\((?:MemberParent="[^"]*",)?MemberName="([^"]+)"', txt)
        return "%s:%s" % (kind[7:], m.group(1) if m else "?")
    if kind == "K2Node_Event":
        m = re.search(r'EventReference=\((?:MemberParent="[^"]*",)?MemberName="([^"]+)"', txt)
        return "Event:%s" % (m.group(1) if m else "?")
    if kind == "K2Node_MacroInstance":
        m = re.search(r"MacroGraph=\S*?:(\w+)'", txt)
        return "Macro:%s" % (m.group(1) if m else "?")
    return kind[7:]


reg = unreal.AssetRegistryHelpers.get_asset_registry()
assets = []
for root in ROOTS:
    flt = unreal.ARFilter(class_paths=[unreal.TopLevelAssetPath("/Script/Engine", "Blueprint"),
                                       unreal.TopLevelAssetPath("/Script/UMGEditor", "WidgetBlueprint")],
                          package_paths=[root], recursive_paths=True)
    assets += list(reg.get_assets(flt))
missing_funcs = set(f for f in WANT_FUNCS if not any(k.endswith(':' + f) for k in lib))
for ad in assets:
    if not missing_funcs and time.time() - stats["t0"] > 120:
        break
    if time.time() - stats["t0"] > 900:
        break
    try:
        bp = ad.get_asset()
    except Exception:
        continue
    if bp is None:
        continue
    stats["bps"] += 1
    pfx = bp.get_path_name() + ":"
    for n in unreal.ObjectIterator(unreal.EdGraphNode):
        p = n.get_path_name()
        if not p.startswith(pfx):
            continue
        kind = n.get_class().get_name()
        if kind not in WANT_KINDS and kind not in ("K2Node_CallFunction", "K2Node_CallArrayFunction"):
            continue
        txt = export_text(n)
        stats["nodes"] += 1
        if not txt:
            continue
        k = key_of(kind, txt)
        fn = k.split(":", 1)[1] if ":" in k else None
        if kind in ("K2Node_CallFunction", "K2Node_CallArrayFunction") and fn not in WANT_FUNCS:
            continue
        if k not in lib:
            lib[k] = {"src": p, "text": txt}
            if fn:
                missing_funcs.discard(fn)

stats["missing_funcs"] = sorted(missing_funcs)
stats["keys"] = sorted(lib)
stats["seconds"] = round(time.time() - stats["t0"])
with open(os.path.join(OUT_DIR, "node_library.json"), "w", encoding="utf-8") as f:
    json.dump({"stats": stats, "lib": lib}, f, ensure_ascii=False, indent=1)
unreal.log("[qz_node_harvest] done bps=%d nodes=%d keys=%d missing=%s" % (stats["bps"], stats["nodes"], len(lib), stats["missing_funcs"]))
