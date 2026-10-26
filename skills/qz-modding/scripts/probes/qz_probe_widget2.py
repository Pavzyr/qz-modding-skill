"""In-memory (unsaved): duplicate a game widget, strip its graph, rebuild tree, compile, report status."""
import json, os, traceback
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep")
log = []
L = lambda x: log.append(str(x)[:600])
at = unreal.AssetToolsHelpers.get_asset_tools()
BEL = unreal.BlueprintEditorLibrary


def widgets_of(bp):
    pfx = bp.get_path_name() + ":WidgetTree."
    return ["%s [%s] parent=%s" % (w.get_path_name()[len(pfx):], w.get_class().get_name(), w.get_parent().get_name() if w.get_parent() else None)
            for w in unreal.ObjectIterator(unreal.Widget) if w.get_path_name().startswith(pfx)]


def status(bp):
    for p in ("status", "Status"):
        try:
            return str(bp.get_editor_property(p))
        except Exception as e:
            last = str(e)
    return "status n/a: " + last


try:
    for src in ["/Game/UI/Quests/WBP_QuestInteractText", "/Game/UI/Tutorial/WBP_NPCSubtitle"]:
        name = "WBP_ZZ_" + src.split("/")[-1]
        dup = at.duplicate_asset(name, "/Game/ZZ_ProbeMem3", unreal.load_asset(src))
        L("== %s parent=%s status=%s" % (name, BEL.generated_class(dup).__class__, status(dup)))
        try:
            gc = BEL.generated_class(dup)
            L("super: %s" % unreal.SystemLibrary.get_class_display_name(gc))
        except Exception as e:
            L("super err %s" % e)
        # strip graph
        try:
            eg = BEL.find_event_graph(dup)
            BEL.remove_graph(dup, eg)
            L("remove_graph done; event graph now %s" % BEL.find_event_graph(dup))
        except Exception:
            L("remove_graph: " + traceback.format_exc()[-300:])
        try:
            BEL.reparent_blueprint(dup, unreal.UserWidget)
            L("reparented to UserWidget")
        except Exception:
            L("reparent: " + traceback.format_exc()[-300:])
        tree = unreal.find_object(dup, "WidgetTree")
        root = None
        for w in unreal.ObjectIterator(unreal.Widget):
            if w.get_path_name().startswith(dup.get_path_name() + ":WidgetTree.") and w.get_parent() is None and isinstance(w, unreal.PanelWidget):
                root = w
        L("root %s" % root)
        canvas = unreal.new_object(unreal.CanvasPanel, tree, "VT_Canvas")
        root.clear_children() if hasattr(root, "clear_children") else None
        try:
            root.set_content(canvas)
        except Exception:
            root.add_child(canvas)
        border = unreal.new_object(unreal.Border, tree, "VT_Panel")
        slot = canvas.add_child_to_canvas(border)
        a = unreal.Anchors(); a.set_editor_property("minimum", unreal.Vector2D(0.5, 1.0)); a.set_editor_property("maximum", unreal.Vector2D(0.5, 1.0))
        slot.set_anchors(a); slot.set_alignment(unreal.Vector2D(0.5, 1.0)); slot.set_position(unreal.Vector2D(0, -120)); slot.set_auto_size(True)
        border.set_brush_color(unreal.LinearColor(0, 0, 0, 0.75))
        border.set_padding(unreal.Margin(24, 16, 24, 16))
        vb = unreal.new_object(unreal.VerticalBox, tree, "VT_VBox")
        border.set_content(vb)
        tn = unreal.new_object(unreal.TextBlock, tree, "VT_Name")
        tp = unreal.new_object(unreal.TextBlock, tree, "VT_Phrase")
        vb.add_child_to_vertical_box(tn); vb.add_child_to_vertical_box(tp)
        tn.set_text(unreal.Text("Name")); tp.set_text(unreal.Text("Phrase"))
        BEL.compile_blueprint(dup)
        L("after compile status=%s" % status(dup))
        L("widgets: %s" % widgets_of(dup))
        # instantiate CDO-ish check: generated class has widget tree?
        gc = BEL.generated_class(dup)
        L("gen class %s" % gc)
except Exception:
    L(traceback.format_exc()[-800:])

with open(os.path.join(OUT, "widget_probe2.json"), "w", encoding="utf-8") as fh:
    json.dump(log, fh, ensure_ascii=False, indent=1)
unreal.log("[qz_probe_widget2] done")
