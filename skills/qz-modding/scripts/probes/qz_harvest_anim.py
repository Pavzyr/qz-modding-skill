"""Read-only: export AnimGraph/anim-event node examples from game AnimBPs. Writes <Saved>/ModSchema/nodes/node_library_anim.json."""
import json, os, re
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "nodes", "node_library_anim.json")
TMP = OUT + ".tmp.copy"
lib, seen = {}, []
reg = unreal.AssetRegistryHelpers.get_asset_registry()
abps = reg.get_assets(unreal.ARFilter(class_paths=[unreal.TopLevelAssetPath("/Script/Engine", "AnimBlueprint")],
                                      package_paths=["/Game/Blueprints"], recursive_paths=True))
for ad in list(abps)[:80]:
    bp = ad.get_asset()
    if not bp:
        continue
    seen.append(str(ad.package_name))
    pfx = bp.get_path_name() + ":"
    for n in unreal.ObjectIterator(unreal.EdGraphNode):
        if not n.get_path_name().startswith(pfx):
            continue
        k = n.get_class().get_name()
        if not re.search(r"LinkedInputPose|AnimGraphNode_Root|K2Node_Event|SaveCachedPose|UseCachedPose", k):
            continue
        t = unreal.AssetExportTask()
        t.set_editor_property("object", n); t.set_editor_property("filename", TMP)
        t.set_editor_property("automated", True); t.set_editor_property("prompt", False)
        if not unreal.Exporter.run_asset_export_task(t):
            continue
        txt = open(TMP, encoding="utf-8", errors="replace").read()
        if k == "K2Node_Event":
            m = re.search(r'MemberName="([^"]+)"', txt)
            k = "Event:" + (m.group(1) if m else "?")
        if k not in lib:
            lib[k] = {"src": n.get_path_name(), "text": txt}
json.dump({"abps": seen, "lib": lib}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
unreal.log("[qz_harvest_anim] done %s" % sorted(lib))
