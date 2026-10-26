"""Export any objects to T3D text (shows ALL serialized properties, incl. ones hidden from Python). Args via env QZ_EXPORT="path1;path2"."""
import os, unreal
OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "t3d")
os.makedirs(OUT, exist_ok=True)
for p in os.environ.get("QZ_EXPORT", "").split(";"):
    if not p:
        continue
    o = unreal.load_object(None, p) or unreal.load_asset(p)
    t = unreal.AssetExportTask()
    t.set_editor_property("object", o)
    fn = os.path.join(OUT, p.strip("/").replace("/", "_").replace(".", "_").replace(":", "_") + ".t3d")
    t.set_editor_property("filename", fn)
    t.set_editor_property("automated", True)
    t.set_editor_property("prompt", False)
    t.set_editor_property("exporter", unreal.ObjectExporterT3D())
    unreal.log("[qz_export_t3d] %s -> %s ok=%s" % (p, fn, unreal.Exporter.run_asset_export_task(t)))
