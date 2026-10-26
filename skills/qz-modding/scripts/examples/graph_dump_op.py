# job "py" op: dump graph nodes of mod Blueprints (mods are mounted only in the full editor) -> Saved/ModSchema/graphs/<bp>.txt
import os, unreal
OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "graphs")
os.makedirs(OUT, exist_ok=True)
for p in ARGS["bps"]:
    bp = EAS.load_asset(p)
    pfx = bp.get_path_name() + ":"
    nodes = [n for n in unreal.ObjectIterator(unreal.EdGraphNode) if n.get_path_name().startswith(pfx)]
    blocks = []
    tmp = os.path.join(OUT, "_tmp.copy")
    for n in nodes:
        t = unreal.AssetExportTask()
        t.set_editor_property("object", n); t.set_editor_property("filename", tmp)
        t.set_editor_property("automated", True); t.set_editor_property("prompt", False); t.set_editor_property("replace_identical", True)
        ok = unreal.Exporter.run_asset_export_task(t)
        blocks.append("### %s\n%s" % (n.get_path_name()[len(pfx):], open(tmp, encoding="utf-8", errors="replace").read() if ok else "<fail>"))
    fn = os.path.join(OUT, p.strip("/").replace("/", "_") + ".txt")
    open(fn, "w", encoding="utf-8").write("\n".join(blocks))
    REPORT.setdefault("dumped", {})[p] = len(nodes)
