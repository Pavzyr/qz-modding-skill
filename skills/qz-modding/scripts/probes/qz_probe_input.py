"""Read-only: dump key mappings of all InputMappingContexts under /Game/Data/Input. Writes input_probe.json."""
import json, os, traceback
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep", "input_probe.json")
res = {"imc": {}, "errors": [], "imc_props": []}
reg = unreal.AssetRegistryHelpers.get_asset_registry()
flt = unreal.ARFilter(class_paths=[unreal.TopLevelAssetPath("/Script/EnhancedInput", "InputMappingContext")],
                      package_paths=["/Game"], recursive_paths=True)
for ad in reg.get_assets(flt):
    path = str(ad.package_name)
    try:
        imc = ad.get_asset()
        if not res["imc_props"]:
            res["imc_props"] = [l.strip() for l in (type(imc).__doc__ or "").splitlines() if "``" in l]
        maps = None
        for p in ("default_key_mappings", "mappings"):
            try:
                maps = imc.get_editor_property(p); break
            except Exception:
                continue
        if maps is not None and hasattr(maps, "get_editor_property"):
            maps = maps.get_editor_property("mappings")
        rows = []
        for m in (maps or []):
            try:
                act = m.get_editor_property("action")
                key = m.get_editor_property("key")
                rows.append("%s -> %s" % (act.get_name() if act else None, key.get_editor_property("key_name")))
            except Exception as e:
                rows.append("err %s" % e)
        res["imc"][path] = rows
    except Exception:
        res["errors"].append(path + traceback.format_exc()[-300:])
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
unreal.log("[qz_probe_input] done")
