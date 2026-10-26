# job "py" op: WidgetBlueprint cook fix. Removing widgets from the tree by script leaves their GUIDs in the WidgetBlueprint
# (WidgetVariableNameToGuidMap) -> cook: "Variable [X] was deleted but still has a GUID referenced" (ensure -> cook fails).
# 1) try to drop the stale names from the map; 2) otherwise put hidden placeholder widgets with the same names back.
# ARGS: {"widget": "/MyMod/UI/WBP_X", "box": "<VerticalBox name>", "stale": ["Old_Spacer1", "Old_Text"],
#        "text_widgets": ["Old_Text"]}   # stale names re-created as CommonRichTextBlock; the rest as Spacer
BEL = unreal.BlueprintEditorLibrary
R = REPORT.setdefault("guidfix", {})
wbp = EAS.load_asset(ARGS["widget"])
tree = unreal.find_object(wbp, "WidgetTree")
alive = set(w.get_name() for w in unreal.ObjectIterator(unreal.Widget) if w.get_path_name().startswith(wbp.get_path_name() + ":WidgetTree."))
R["alive"] = sorted(alive)
STALE = ARGS.get("stale", [])
TEXTS = set(ARGS.get("text_widgets", []))
done = False
try:
    m = wbp.get_editor_property("widget_variable_name_to_guid_map")
    R["map_before"] = sorted(str(k) for k in m.keys())
    for k in list(m.keys()):
        if str(k) not in alive:
            m.pop(k)
    wbp.set_editor_property("widget_variable_name_to_guid_map", m)
    R["map_after"] = sorted(str(k) for k in wbp.get_editor_property("widget_variable_name_to_guid_map").keys())
    done = True
except Exception as e:
    R["map_err"] = str(e)[:200]
if not done:
    vb = unreal.find_object(tree, ARGS["box"])
    for n in STALE:
        if n in alive:
            continue
        w = unreal.new_object(unreal.CommonRichTextBlock if n in TEXTS else unreal.Spacer, tree, n)
        if n not in TEXTS:
            w.set_size(unreal.Vector2D(0, 0))
        w.set_visibility(unreal.SlateVisibility.COLLAPSED)
        vb.add_child(w)
    R["placeholders"] = [unreal.find_object(tree, n) is not None for n in STALE]
BEL.compile_blueprint(wbp)
EAS.save_loaded_asset(wbp, False)
