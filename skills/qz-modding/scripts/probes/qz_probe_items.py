"""Read-only: item system (SItemDataAsset & friends) - fields, tool item samples, player equipment/inventory components. Writes items_probe.json."""
import json, os, re, traceback
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep", "items_probe.json")
PROP_RE = re.compile(r"^\s*-\s*``(\w+)``\s*\(([^)]*)\):\s*(.*)$")
res = {"classes": {}, "assets": {}, "errors": []}


def props(c):
    return {m.group(1): m.group(2) + " | " + m.group(3)[:120] for m in (PROP_RE.match(l) for l in (c.__doc__ or "").splitlines()) if m}


def short(v, d=0):
    if isinstance(v, unreal.Object):
        return "<%s> %s" % (v.get_class().get_name(), v.get_path_name())
    if isinstance(v, (list, tuple, unreal.Array)):
        return [short(x, d + 1) for x in list(v)[:20]]
    if isinstance(v, (dict, unreal.Map)):
        return {str(short(k, d + 1)): short(x, d + 1) for k, x in list(v.items())[:30]}
    if isinstance(v, unreal.StructBase) and d < 3:
        return {p: short(v.get_editor_property(p), d + 1) for p in props(type(v))}
    return str(v)[:300]


for n in sorted(dir(unreal)):
    if re.match(r"^(SItem|SInventory|SEquipment|SWearable|SWheel|QzToolBase|QzToolDataAsset|QzToolComponent|SItemDataAsset)", n):
        c = getattr(unreal, n)
        if isinstance(c, type):
            res["classes"][n] = {"chain": [x.__name__ for x in c.__mro__[1:5]],
                                 "props": {k: v for k, v in props(c).items() if not re.search(r"replicat|^net_|tick|hlod|data_layer|^on_|content_bundle|custom_time|initial_life|min_net|pivot|ignores_origin|generate_overlap|relevant|replay|migrating|find_camera|enable_auto|external_data|runtime_grid|sprite|spawn_collision|is_editor_only|is_main_world|is_spatially|asset_user_data|update_overlaps|^layers$|block_input|auto_receive|input_priority|can_be_|actor_guid|actor_instance", k)}}
for p in ["/Game/Blueprints/Tools/UVStick/ID_UVStick", "/Game/Data/Tools/DA_UVStick", "/Game/Blueprints/Tools/Scanner/ID_Scanner"]:
    try:
        a = unreal.load_asset(p)
        res["assets"][p] = {"class": a.get_class().get_name(), "values": {k: short(a.get_editor_property(k)) for k in props(type(a))}}
    except Exception:
        res["errors"].append(p + traceback.format_exc()[-300:])
for p in ["/Game/Blueprints/Tools/UVStick/BP_UVStick", "/Game/Blueprints/KPP/Prototyping/BP_TestPlayer"]:
    try:
        bp = unreal.load_asset(p)
        cdo = unreal.get_default_object(unreal.BlueprintEditorLibrary.generated_class(bp))
        res["assets"][p] = {"cdo_class": cdo.get_class().get_name(), "parent_chain": [x.__name__ for x in type(cdo).__mro__[1:6]],
                            "values": {k: short(cdo.get_editor_property(k)) for k in props(type(cdo))
                                       if re.search(r"item|tool|equip|inventor|wheel|slot|tag|set|class|wear|attach|socket", k)}}
    except Exception:
        res["errors"].append(p + traceback.format_exc()[-300:])
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
unreal.log("[qz_probe_items] done")
