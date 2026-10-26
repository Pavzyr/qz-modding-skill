"""Read-only commandlet probe: dump every graph node of Blueprints as copy/paste text (all pins, links, defaults).
  env QZ_GRAPH="/Game/Path/BP_A;/Game/Path/BP_B"  ->  Saved/ModSchema/graphs/<BP>.txt (one block per node, graph name in header)
Readable summary: Begin Object Class=<node class> ... FunctionReference / CustomFunctionName / pins (PinName, DefaultValue, LinkedTo)."""
import os, unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "graphs")
os.makedirs(OUT, exist_ok=True)
for p in os.environ.get("QZ_GRAPH", "").split(";"):
    if not p:
        continue
    bp = unreal.load_asset(p)
    if bp is None:
        unreal.log("[qz_graph_dump] not found %s" % p)
        continue
    pfx = bp.get_path_name() + ":"
    try:   # graphs are loaded lazily in commandlets: touch them first
        for gname in ("ubergraph_pages", "function_graphs", "macro_graphs"):
            list(bp.get_editor_property(gname) or [])
    except Exception as e:
        unreal.log("[qz_graph_dump] graphs not readable: %s" % e)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp) if hasattr(unreal, "BlueprintEditorLibrary") else None
    nodes = [n for n in unreal.ObjectIterator(unreal.EdGraphNode) if n.get_path_name().startswith(pfx)]
    open(os.path.join(OUT, "_count.txt"), "a").write("%s %d\n" % (p, len(nodes)))
    blocks = []
    tmp = os.path.join(OUT, "_tmp.copy")
    for n in nodes:
        t = unreal.AssetExportTask()
        t.set_editor_property("object", n)
        t.set_editor_property("filename", tmp)
        t.set_editor_property("automated", True)
        t.set_editor_property("prompt", False)
        t.set_editor_property("replace_identical", True)
        ok = unreal.Exporter.run_asset_export_task(t)
        txt = open(tmp, encoding="utf-8", errors="replace").read() if ok and os.path.exists(tmp) else "<export failed>"
        blocks.append("### %s\n%s" % (n.get_path_name()[len(pfx):], txt))
    fn = os.path.join(OUT, p.strip("/").replace("/", "_") + ".txt")
    open(fn, "w", encoding="utf-8").write("\n".join(blocks))
    unreal.log("[qz_graph_dump] %s nodes=%d -> %s" % (p, len(nodes), fn))
