"""Read-only: can we export Blueprint graph nodes to copy/paste text? Writes node_export_probe.json."""
import json, os, traceback, tempfile
import unreal

OUT_DIR = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep")
res = {"exporters": [n for n in dir(unreal) if "Exporter" in n], "tries": [], "nodes": []}
bp = unreal.load_asset("/Game/Blueprints/Gameplay/Clothes/BP_HatBase")
pfx = bp.get_path_name() + ":"
nodes = [n for n in unreal.ObjectIterator(unreal.EdGraphNode) if n.get_path_name().startswith(pfx)]
res["nodes"] = [n.get_path_name()[len(pfx):] + " [" + n.get_class().get_name() + "]" for n in nodes][:60]
tmp = os.path.join(OUT_DIR, "node_export_tmp")
os.makedirs(tmp, exist_ok=True)
for i, n in enumerate(nodes[:3]):
    for ext in ("copy", "t3d", "txt"):
        try:
            t = unreal.AssetExportTask()
            t.set_editor_property("object", n)
            fn = os.path.join(tmp, "n%d.%s" % (i, ext))
            t.set_editor_property("filename", fn)
            t.set_editor_property("automated", True)
            t.set_editor_property("prompt", False)
            t.set_editor_property("replace_identical", True)
            ok = unreal.Exporter.run_asset_export_task(t)
            txt = open(fn, encoding="utf-8", errors="replace").read()[:1500] if os.path.exists(fn) else None
            res["tries"].append({"node": n.get_name(), "ext": ext, "ok": ok, "text": txt})
        except Exception:
            res["tries"].append({"node": n.get_name(), "ext": ext, "err": traceback.format_exc()[-400:]})
json.dump(res, open(os.path.join(OUT_DIR, "node_export_probe.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
unreal.log("[qz_probe_nodeexport] done")
