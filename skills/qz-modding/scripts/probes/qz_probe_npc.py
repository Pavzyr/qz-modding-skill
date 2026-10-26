"""Read-only probe: how visitor NPCs, context actions (interaction hints), dialogue/subtitles and widget registry work.
Runs INSIDE Unreal (commandlet). Writes <Saved>/ModSchema/deep/npc_probe.json. Changes nothing."""
import json, os, re, traceback
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep")
os.makedirs(OUT, exist_ok=True)
res = {"classes": {}, "enums": {}, "bps": {}, "assets": {}, "bp_by_parent": {}, "errors": []}
PROP_RE = re.compile(r"^\s*-\s*``(\w+)``\s*\(([^)]*)\):\s*(.*)$")


def class_props(cls):
    props = {}
    for line in (cls.__doc__ or "").splitlines():
        m = PROP_RE.match(line)
        if m:
            props[m.group(1)] = {"type": m.group(2).strip(), "doc": m.group(3).strip()[:300]}
    return props


def short(v, depth=0):
    try:
        if v is None or isinstance(v, (bool, int, float, str)):
            return v if not isinstance(v, str) else v[:400]
        if isinstance(v, unreal.Object):
            return "<%s> %s" % (v.get_class().get_name(), v.get_path_name())
        if isinstance(v, (list, tuple, unreal.Array, set, unreal.Set)):
            items = list(v)
            r = [short(x, depth + 1) for x in items[:25]]
            if len(items) > 25:
                r.append("... +%d more" % (len(items) - 25))
            return r
        if isinstance(v, (dict, unreal.Map)):
            r = {}
            for i, (k, x) in enumerate(v.items()):
                if i >= 40:
                    r["..."] = "+%d more" % (len(v) - 40); break
                r[str(short(k, depth + 1))] = short(x, depth + 1)
            return r
        if isinstance(v, unreal.StructBase) and depth < 4:
            r = {"__struct__": type(v).__name__}
            for p in class_props(type(v)):
                try:
                    r[p] = short(v.get_editor_property(p), depth + 1)
                except Exception:
                    pass
            if len(r) > 1:
                return r
        return str(v)[:400]
    except Exception as e:
        return "<err %s>" % e


NOISE = re.compile(r"replicat|^net_|tick|hlod|data_layer|^on_|content_bundle|custom_time|initial_life|min_net|pivot|"
                   r"ignores_origin|generate_overlap|relevant|replay|migrating|find_camera|enable_auto|external_data|"
                   r"runtime_grid|sprite|spawn_collision|is_editor_only|is_main_world|is_spatially|asset_user_data|"
                   r"update_overlaps|^layers$|block_input|auto_receive|input_priority|can_be_|actor_guid|actor_instance")


def obj_values(o, filt=True):
    vals = {}
    for p in class_props(type(o)):
        if filt and NOISE.search(p):
            continue
        try:
            vals[p] = short(o.get_editor_property(p))
        except Exception as e:
            vals[p] = "<unreadable: %s>" % str(e)[:80]
    return vals


def err(where):
    res["errors"].append(where + ": " + traceback.format_exc()[-600:])


# ---- A. S*-classes of the game module + related enums
try:
    pat = re.compile(r"^(SContext|SFocus|SWidgetRegistry|SGameplayAbility$|SAbilitySet|SAbilitySystem|SCharacter$|SInteract|"
                     r"SHint|SSimpleAction|STitleContext|SAction|SInput|SPlayer|SHud|SHUD|SUI|SGameFlow|SPrompt|SDialog|SSubtitle)")
    for n in sorted(dir(unreal)):
        if pat.match(n):
            cls = getattr(unreal, n)
            if isinstance(cls, type):
                res["classes"][n] = {"chain": [c.__name__ for c in cls.__mro__[1:6]],
                                     "summary": " ".join((cls.__doc__ or "").strip().splitlines()[:2])[:300],
                                     "props": {k: v for k, v in class_props(cls).items() if not NOISE.search(k)}}
    for n in ["QzNPCCharacter", "QzNPCInteractiveAttachment", "QzNPCAttachment", "Qz3DSubtitleComponent", "QzDialogueComponent",
              "QzContextFragment_SimplePlayerAction", "QzSubtitlesWidget", "QzQuestActorV2", "QzCharacterAccessoryOtherDataAsset"]:
        cls = getattr(unreal, n, None)
        if cls:
            res["classes"][n] = {"chain": [c.__name__ for c in cls.__mro__[1:6]],
                                 "props": {k: v for k, v in class_props(cls).items() if not NOISE.search(k)},
                                 "methods": sorted(m for m in dir(cls) if not m.startswith("_") and callable(getattr(cls, m, None))
                                                   and m not in dir(unreal.Actor) and m not in dir(unreal.Object))[:120]}
except Exception:
    err("classes")

try:
    for n in sorted(dir(unreal)):
        if re.match(r"^(QzHintType|SContext\w*Mode|SContext\w*Type|QzGeneratorDataAsset\w*|QzSpeakerRole|QzSubtitlesPriority|QzNpcRole|QzCvNPCState)$", n):
            e = getattr(unreal, n)
            res["enums"][n] = [m for m in dir(e) if m.isupper()]
except Exception:
    err("enums")

# ---- B. Blueprints: CDO values + components
sub = None
try:
    sub = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
except Exception:
    err("subobject subsystem")
BPS = ["/Game/Blueprints/KPP/Prototyping/BP_TestCivilian", "/Game/Blueprints/NPCAccessory/BP_BaggageAttachment",
       "/Game/Blueprints/NPCAccessory/BP_Attachment_Axe", "/Game/Blueprints/Gameplay/Clothes/BP_HatBase",
       "/Game/Blueprints/Quests/StoryActors/BP_QuestInteractable", "/Game/Blueprints/Quests/StoryActors/GA_NPCInteract",
       "/Game/Blueprints/Quests/StoryActors/BP_QuestRoleDialogueActor", "/Game/Blueprints/Quests/StoryActors/GA_QuestInteract",
       "/Game/UI/Tutorial/WBP_NPCSubtitle", "/Game/UI/HUD/Components/Context/WBP_SimpleAction",
       "/Game/UI/HUD/Components/Context/WBP_ActionsContainer", "/Game/UI/Quests/WBP_QuestInteractText",
       "/Game/Blueprints/Gameplay/BP_NPCManager", "/Game/Blueprints/KPP/Prototyping/BP_TestPlayer",
       "/Game/Blueprints/Quests/StoryActors/SideActors/BP_inscriptionWall", "/Game/Blueprints/Quests/StoryActors/SideActors/GA_InscriptionWallInteract",
       "/Game/Blueprints/KPP/Prototyping/Military/BP_Doc", "/Game/Blueprints/KPP/Prototyping/Military/Ability/GA_DocLoveInteract"]
for path in BPS:
    info = {}
    try:
        bp = unreal.load_asset(path)
        if not bp:
            res["bps"][path] = "NOT FOUND"; continue
        gc = bp.generated_class()
        cdo = unreal.get_default_object(gc)
        info["cdo"] = obj_values(cdo)
        comps = []
        if sub:
            try:
                for h in sub.k2_gather_subobject_data_for_blueprint(bp):
                    d = unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h)
                    o = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(d)
                    nm = str(unreal.SubobjectDataBlueprintFunctionLibrary.get_variable_name(d))
                    if o is None:
                        continue
                    cn = o.get_class().get_name()
                    entry = {"name": nm, "class": cn}
                    if re.match(r"^(S|Qz|QZ|Widget|Sphere|Box|Capsule|Audio)", cn) or "Context" in cn or "Interact" in cn:
                        entry["values"] = obj_values(o)
                    comps.append(entry)
            except Exception:
                err("components " + path)
        info["components"] = comps
        try:
            info["functions"] = sorted(str(g.get_name()) for g in unreal.BlueprintEditorLibrary.get_editor_property(bp, "function_graphs")) \
                if False else None
        except Exception:
            pass
    except Exception:
        err("bp " + path)
    res["bps"][path] = info

# ---- C. data assets
for path in ["/Game/Data/DA_ContextGuide", "/Game/Data/UI/DA_WidgetRegistry", "/Game/Data/Common/DA_Voice",
             "/Game/Data/GeneratorApperance/OtherAccessory/DA_Accessory_Camera"]:
    try:
        a = unreal.load_asset(path)
        if a is None:
            # try find by folder
            res["assets"][path] = "NOT FOUND"; continue
        res["assets"][path] = {"class": a.get_class().get_name(), "values": obj_values(a, filt=False)}
    except Exception:
        err("asset " + path)

# registry entries in detail (widget classes)
try:
    a = unreal.load_asset("/Game/Data/UI/DA_WidgetRegistry")
    reg = a.get_editor_property("registry")
    det = {}
    for k, e in reg.items():
        det[str(k.get_editor_property("tag_name"))] = {p: short(e.get_editor_property(p)) for p in class_props(type(e))
                                                        if p != "input_actions_array"}
    res["assets"]["registry_detail"] = det
except Exception:
    err("registry detail")

# ---- D. asset registry: BPs by interesting parents, voice/context assets
try:
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    try:
        ar.search_all_assets(True)
    except Exception:
        pass
    flt = unreal.ARFilter(class_paths=[unreal.TopLevelAssetPath("/Script/Engine", "Blueprint")], recursive_classes=True,
                          package_paths=["/Game"], recursive_paths=True)
    for ad in ar.get_assets(flt):
        try:
            par = str(ad.get_tag_value("ParentClass") or "")
            npar = str(ad.get_tag_value("NativeParentClass") or "")
        except Exception:
            continue
        if re.search(r"ContextFragment|Focus|SGameplayAbility|NPCCustomLogic|SymptomFillingRule|QzNPCInteractiveAttachment|Interactive|"
                     r"QzNPCCharacter|SContext|Subtitle", par + npar):
            res["bp_by_parent"].setdefault(npar.split(".")[-1].strip("'\""), []).append(
                str(ad.package_name) + " <- " + par.split(".")[-1].strip("'\""))
    flt2 = unreal.ARFilter(package_paths=["/Game/Data"], recursive_paths=True)
    for ad in ar.get_assets(flt2):
        cn = str(ad.asset_class_path.asset_name)
        if re.search(r"Voice|Context|Dialog|Subtitle|AbilitySet|Hint|StringTable", cn):
            res["assets"].setdefault("_list_" + cn, []).append(str(ad.package_name))
    flt3 = unreal.ARFilter(class_paths=[unreal.TopLevelAssetPath("/Script/Engine", "StringTable")], package_paths=["/Game"],
                           recursive_paths=True)
    res["assets"]["_string_tables"] = sorted(str(ad.package_name) for ad in ar.get_assets(flt3))
except Exception:
    err("asset registry")

try:
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    for cp in [("/Script/QZSim", "SAbilitySet"), ("/Script/QZSim", "SInputData")]:
        for ad in ar.get_assets(unreal.ARFilter(class_paths=[unreal.TopLevelAssetPath(*cp)], package_paths=["/Game"], recursive_paths=True)):
            a = ad.get_asset()
            res["assets"][str(ad.package_name)] = {"class": cp[1], "values": obj_values(a, filt=False)}
except Exception:
    err("ability sets")

with open(os.path.join(OUT, "npc_probe2.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
unreal.log("[qz_probe_npc] done, errors=%d" % len(res["errors"]))
