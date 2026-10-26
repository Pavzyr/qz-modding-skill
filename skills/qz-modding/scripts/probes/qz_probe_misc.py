"""Read-only: enum C++ names, QzDocument fields, random-pool hats/glasses. Writes misc_probe.json."""
import json, os, traceback
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep", "misc_probe.json")
res = {"enums": {}, "structs": {}, "pool": [], "errors": []}
for en in ["QzCvNPCState", "QzNpcRole"]:
    try:
        e = getattr(unreal, en).static_enum()
        names = []
        for i in range(64):
            try:
                n = str(unreal.KismetNodeHelperLibrary.get_enumerator_name(e, i))
                if n in ("None", "") and i > 0:
                    pass
                names.append((i, n, str(unreal.KismetNodeHelperLibrary.get_enumerator_user_friendly_name(e, i))))
                if "MAX" in n.upper() and i > 0:
                    break
            except Exception:
                break
        res["enums"][en] = {"path": e.get_path_name(), "names": names[:40]}
    except Exception:
        res["errors"].append(en + ": " + traceback.format_exc()[-400:])
for sn in ["QzDocument", "QzStaticProfile"]:
    s = getattr(unreal, sn, None)
    res["structs"][sn] = [l.strip() for l in (s.__doc__ or "").splitlines() if "``" in l] if s else None
reg = unreal.AssetRegistryHelpers.get_asset_registry()
for folder in ["/Game/Data/GeneratorApperance/Hats", "/Game/Data/GeneratorApperance/Glasses"]:
    for ad in reg.get_assets(unreal.ARFilter(package_paths=[folder], recursive_paths=True)):
        try:
            a = ad.get_asset()
            if not hasattr(a, "get_editor_property"):
                continue
            row = {"path": str(ad.package_name), "class": a.get_class().get_name()}
            for p in ("use_only_custom_profile", "selection_weight", "spawn_probability", "allowed_campaign_tags", "key_tag_data",
                      "runtime_actor_class", "generator_data_source", "required_tags", "blocked_tags", "gender_tag"):
                try:
                    v = a.get_editor_property(p)
                    row[p] = v.get_path_name() if isinstance(v, unreal.Object) else str(v)
                except Exception:
                    pass
            res["pool"].append(row)
        except Exception:
            res["errors"].append(str(ad.package_name) + traceback.format_exc()[-200:])
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
unreal.log("[qz_probe_misc] done")
