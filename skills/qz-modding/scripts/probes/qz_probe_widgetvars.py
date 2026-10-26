"""In-memory: do script-created widgets become BP variables (bIsVariable) of the widget class? Writes widgetvars_probe.json."""
import json, os, traceback
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep", "widgetvars_probe.json")
res = []
L = lambda x: res.append(str(x)[:400])
BEL = unreal.BlueprintEditorLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()
try:
    dup = at.duplicate_asset("WBP_ZZVars", "/Game/ZZ_ProbeMem5", unreal.load_asset("/Game/UI/Quests/WBP_QuestInteractText"))
    BEL.remove_graph(dup, BEL.find_event_graph(dup))
    BEL.reparent_blueprint(dup, unreal.UserWidget)
    tree = unreal.find_object(dup, "WidgetTree")
    root = [w for w in unreal.ObjectIterator(unreal.Widget) if w.get_path_name().startswith(dup.get_path_name() + ":WidgetTree.") and w.get_parent() is None][0]
    tm = unreal.find_object(tree, "Text_Main")
    L("Text_Main %s" % tm)
    canvas = unreal.new_object(unreal.CanvasPanel, tree, "VT_Canvas")
    root.set_content(canvas)
    b = unreal.new_object(unreal.Border, tree, "VT_Panel")
    canvas.add_child_to_canvas(b)
    tb = unreal.new_object(unreal.TextBlock, tree, "VT_Text")
    vb = unreal.new_object(unreal.VerticalBox, tree, "VT_VBox")
    b.set_content(vb)
    vb.add_child_to_vertical_box(tb)
    vb.add_child_to_vertical_box(tm)
    BEL.compile_blueprint(dup)
    gc = BEL.generated_class(dup)
    cdo = unreal.get_default_object(gc)
    for n in ("VT_Canvas", "VT_Panel", "VT_Text", "VT_VBox", "Text_Main", "SizeBox_0"):
        try:
            L("%s -> %s" % (n, cdo.get_editor_property(n)))
        except Exception as e:
            L("%s -> ERR %s" % (n, str(e)[:150]))
    L("doc props: " + " | ".join(l.strip() for l in (gc.__doc__ or "").splitlines() if "``" in l)[:800])
    # try the editor-only flag through any exposed path
    for attr in ("is_variable", "bIsVariable", "b_is_variable"):
        try:
            L("%s get %s" % (attr, tb.get_editor_property(attr)))
        except Exception as e:
            L("%s: %s" % (attr, str(e)[:120]))
except Exception:
    L(traceback.format_exc()[-800:])
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
unreal.log("[qz_probe_widgetvars] done")
