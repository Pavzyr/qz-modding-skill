"""Read-only probe of BP-callable signatures + in-memory (unsaved) widget-tree test. Writes sig_probe.json."""
import json, os, re, traceback
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep")
res = {"sig": {}, "structs": {}, "widget_test": [], "errors": []}

CLASSES = {
    "QzNPCCharacter": r"^(bp_|get_npc|get_state|is_inspect|contains_symptom|get_mark|get_photo|is_inited|get_current_zone|get_allowed)",
    "SFocusComponent": r".",
    "SContextActionsComponent": r".",
    "SContextMonitorComponent": r".",
    "SAbilitySystemComponent": r"(abilit|set|input|tag|give|grant|remove)",
    "SGameplayAbility": r"(get_|focus|target|source|avatar|owner|end_|k2_)",
    "SCharacter": r"(get_|focus|context|abilit)",
    "QzSubtitlesWidget": r"(subtitle|text|role|show|hide|add|set_)",
    "Qz3DSubtitleComponent": r"(subtitle|text|show|hide|play|set_text)",
    "QzDialogueComponent": r"(dialog|subtitle|voice|play_)",
    "SContextFragment": r".",
    "QzContextFragment_SimplePlayerAction": r".",
}
base_obj = set(dir(unreal.Object))
for cn, pat in CLASSES.items():
    c = getattr(unreal, cn, None)
    if c is None:
        res["sig"][cn] = None; continue
    parent_dir = set()
    for b in c.__mro__[1:2]:
        parent_dir = set(dir(b))
    out = {}
    for m in dir(c):
        if m.startswith("_") or m in base_obj:
            continue
        if cn not in ("SFocusComponent", "SContextActionsComponent", "SContextMonitorComponent", "SContextFragment",
                      "QzContextFragment_SimplePlayerAction") and not re.search(pat, m):
            continue
        if cn in ("SFocusComponent", "SContextActionsComponent", "SContextMonitorComponent") and m in dir(unreal.ActorComponent):
            continue
        try:
            a = getattr(c, m)
        except Exception:
            continue
        if callable(a):
            out[m] = (a.__doc__ or "").strip()[:700]
    res["sig"][cn] = out

for sn in ["SGameplayAbilityInfo", "SGameplayEffectInfo", "SContextActionData", "SContextData", "QzNPCDataBP", "QzNPCData",
           "QzNPCInfo", "QzNpcData"]:
    s = getattr(unreal, sn, None)
    res["structs"][sn] = None if s is None else (s.__doc__ or "")[:2500]
# any struct returned by get_npc_data_bp
try:
    d = unreal.QzNPCCharacter.get_npc_data_bp.__doc__ or ""
    for t in re.findall(r"->\s*(\w+)", d):
        s = getattr(unreal, t, None)
        if s is not None:
            res["structs"][t] = (s.__doc__ or "")[:4000]
except Exception:
    res["errors"].append(traceback.format_exc()[-500:])

# ---- in-memory widget blueprint test (NOT saved): can Python build a widget tree?
def wlog(x):
    res["widget_test"].append(str(x)[:400])
try:
    at = unreal.AssetToolsHelpers.get_asset_tools()
    fac = unreal.WidgetBlueprintFactory()
    try:
        fac.set_editor_property("parent_class", unreal.UserWidget)
    except Exception as e:
        wlog("factory parent: %s" % e)
    wbp = at.create_asset("WBP_ZZProbe", "/Game/ZZ_ProbeMem", unreal.WidgetBlueprint, fac)
    wlog("created %s" % wbp)
    tree = None
    for attr in ("widget_tree", "WidgetTree"):
        try:
            tree = wbp.get_editor_property(attr); wlog("get_editor_property(%s) -> %s" % (attr, tree)); break
        except Exception as e:
            wlog("get_editor_property(%s) failed: %s" % (attr, e))
    if tree is None:
        try:
            tree = unreal.find_object(wbp, "WidgetTree"); wlog("find_object WidgetTree -> %s" % tree)
        except Exception as e:
            wlog("find_object failed: %s" % e)
    if tree is not None:
        try:
            canvas = unreal.new_object(unreal.CanvasPanel, tree, "RootCanvas")
            tb = unreal.new_object(unreal.TextBlock, tree, "PhraseText")
            for attr in ("root_widget", "RootWidget"):
                try:
                    tree.set_editor_property(attr, canvas); wlog("set %s ok" % attr); break
                except Exception as e:
                    wlog("set %s failed: %s" % (attr, e))
            slot = canvas.add_child_to_canvas(tb)
            wlog("add_child_to_canvas -> %s" % slot)
            tb.set_text(unreal.Text("probe"))
            unreal.BlueprintEditorLibrary.compile_blueprint(wbp)
            gc = unreal.BlueprintEditorLibrary.generated_class(wbp)
            wlog("compiled, class %s" % gc)
            try:
                wlog("root after compile: %s" % tree.get_editor_property("root_widget"))
            except Exception as e:
                wlog("root read: %s" % e)
            try:
                wlog("is_variable prop: %s" % tb.get_editor_property("is_variable"))
            except Exception as e:
                wlog("is_variable: %s" % e)
        except Exception:
            wlog(traceback.format_exc()[-600:])
except Exception:
    wlog(traceback.format_exc()[-800:])

# ---- in-memory BP: member variable of Array[Text] and default on CDO
try:
    at = unreal.AssetToolsHelpers.get_asset_tools()
    bp = unreal.BlueprintEditorLibrary.create_blueprint_asset_with_parent("/Game/ZZ_ProbeMem/BP_ZZProbe", unreal.Actor)
    t_arr = unreal.BlueprintEditorLibrary.get_array_type(unreal.BlueprintEditorLibrary.get_basic_type_by_name("text"))
    ok = unreal.BlueprintEditorLibrary.add_member_variable(bp, "Phrases", t_arr)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    cdo = unreal.get_default_object(unreal.BlueprintEditorLibrary.generated_class(bp))
    cdo.set_editor_property("Phrases", [unreal.Text("a"), unreal.Text("b")])
    wlog("BP var add=%s, cdo Phrases=%s" % (ok, cdo.get_editor_property("Phrases")))
except Exception:
    wlog("bpvar: " + traceback.format_exc()[-600:])

with open(os.path.join(OUT, "sig_probe.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
unreal.log("[qz_probe_sig] done")
