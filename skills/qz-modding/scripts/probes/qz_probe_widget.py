"""Read-only / in-memory probe: widget blueprint root creation + trees of game widgets. Writes widget_probe.json. Saves nothing."""
import json, os, traceback
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep")
res = {"factory_props": [], "root_test": [], "trees": {}, "misc": []}
L = lambda k, x: res[k].append(str(x)[:500])

fac = unreal.WidgetBlueprintFactory()
for line in (type(fac).__doc__ or "").splitlines():
    if "``" in line:
        L("factory_props", line.strip())

# try to get a root via factory property
for prop in ("root_widget_class", "RootWidgetClass"):
    try:
        fac.set_editor_property(prop, unreal.CanvasPanel)
        L("root_test", "factory %s set ok" % prop)
        break
    except Exception as e:
        L("root_test", "factory %s: %s" % (prop, e))
try:
    fac.set_editor_property("parent_class", unreal.UserWidget)
except Exception as e:
    L("root_test", "parent_class: %s" % e)
at = unreal.AssetToolsHelpers.get_asset_tools()
wbp = at.create_asset("WBP_ZZProbe2", "/Game/ZZ_ProbeMem2", unreal.WidgetBlueprint, fac)
tree = unreal.find_object(wbp, "WidgetTree")


def widgets_of(bp):
    pfx = bp.get_path_name() + ":WidgetTree."
    out = []
    for w in unreal.ObjectIterator(unreal.Widget):
        p = w.get_path_name()
        if p.startswith(pfx):
            par = w.get_parent()
            out.append("%s [%s] parent=%s" % (p[len(pfx):], w.get_class().get_name(), par.get_name() if par else None))
    return out


L("root_test", "new WBP widgets: %s" % widgets_of(wbp))

# trees of candidate game widgets
for path in ["/Game/UI/Quests/WBP_QuestInteractText", "/Game/UI/Tutorial/WBP_NPCSubtitle", "/Game/UI/Tutorial/WBP_MainTutorialMessage",
             "/Game/UI/HUD/Components/Context/WBP_SimpleAction", "/Game/UI/HUD/Components/Context/WBP_Title",
             "/Game/UI/HUD/Components/Context/WBP_ActionsContainer"]:
    try:
        bp = unreal.load_asset(path)
        graphs = []
        try:
            eg = unreal.BlueprintEditorLibrary.find_event_graph(bp)
            graphs.append(str(eg.get_name()) if eg else None)
        except Exception as e:
            graphs.append("eg err %s" % e)
        res["trees"][path] = {"parent": str(unreal.BlueprintEditorLibrary.generated_class(bp).get_super_class().get_name())
                              if hasattr(unreal.BlueprintEditorLibrary.generated_class(bp), "get_super_class") else "",
                              "widgets": widgets_of(bp), "graphs": graphs}
    except Exception:
        res["trees"][path] = traceback.format_exc()[-400:]

# duplicate-a-widget test in memory: duplicate WBP_QuestInteractText into memory path and add a child to its root panel
try:
    src = "/Game/UI/Quests/WBP_QuestInteractText"
    dup = at.duplicate_asset("WBP_ZZDup", "/Game/ZZ_ProbeMem2", unreal.load_asset(src))
    L("misc", "dup %s" % dup)
    L("misc", "dup widgets: %s" % widgets_of(dup))
except Exception:
    L("misc", traceback.format_exc()[-500:])

# can we make BP children of key classes (in memory)?
for name, parent in [("BP_ZZAttach", unreal.QzNPCAttachment), ("GA_ZZ", unreal.SGameplayAbility), ("BP_ZZMgr", unreal.Actor)]:
    try:
        b = unreal.BlueprintEditorLibrary.create_blueprint_asset_with_parent("/Game/ZZ_ProbeMem2/" + name, parent)
        unreal.BlueprintEditorLibrary.compile_blueprint(b)
        L("misc", "%s -> %s" % (name, unreal.BlueprintEditorLibrary.generated_class(b)))
    except Exception:
        L("misc", name + " " + traceback.format_exc()[-300:])
# ability set DA with class
try:
    ga = unreal.load_asset("/Game/ZZ_ProbeMem2/GA_ZZ")
    f = unreal.DataAssetFactory(); f.set_editor_property("data_asset_class", unreal.SAbilitySet)
    aset = at.create_asset("AS_ZZ", "/Game/ZZ_ProbeMem2", unreal.SAbilitySet, f)
    info = unreal.SGameplayAbilityInfo()
    info.set_editor_property("gameplay_ability_class", unreal.BlueprintEditorLibrary.generated_class(ga))
    tag = unreal.GameplayTag()
    try:
        tag = unreal.GameplayTagLibrary.make_gameplay_tag_from_name("Player.Input.Interact")  # may not exist
    except Exception:
        pass
    L("misc", "tag lib: %s" % [m for m in dir(unreal) if "GameplayTag" in m and ("Library" in m or "Request" in m)])
    aset.set_editor_property("abilities", [info])
    L("misc", "aset abilities %s" % aset.get_editor_property("abilities"))
except Exception:
    L("misc", "aset " + traceback.format_exc()[-400:])

# QzNPCAttachment own props
try:
    L("misc", "QzNPCAttachment doc props: " + " ; ".join(l.strip() for l in (unreal.QzNPCAttachment.__doc__ or "").splitlines()
                                                         if "``" in l and not any(s in l for s in ("net_", "replicat", "tick"))) [:3000])
except Exception:
    pass

with open(os.path.join(OUT, "widget_probe.json"), "w", encoding="utf-8") as fh:
    json.dump(res, fh, ensure_ascii=False, indent=1)
unreal.log("[qz_probe_widget] done")
