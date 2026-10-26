# job "py" op (read-only): campaigns (QzCompanyDataAsset or whatever class DA_CompanyChicago is) -> their day lists; who uses the raid days
AR = unreal.AssetRegistryHelpers.get_asset_registry()
c0 = EAS.load_asset("/Game/Data/Companies/Chicago/DA_CompanyChicago")
cls = c0.get_class()
REPORT["company_class"] = cls.get_path_name()
out = {}
for ad in AR.get_assets(unreal.ARFilter(class_paths=[unreal.TopLevelAssetPath(cls.get_outer().get_name(), cls.get_name())], recursive_classes=True)):
    a = ad.get_asset(); rec = {}
    for p in sorted(dir(a)):
        if p.startswith("_"):
            continue
        try:
            v = a.get_editor_property(p)
        except Exception:
            continue
        s = str(v)
        if any(k in p for k in ("day", "tag", "title", "name", "psevdonim", "level", "mode", "hidden", "enable")) or "NewDay" in s:
            rec[p] = s[:1500]
    out[str(ad.package_name)] = rec
REPORT["companies"] = out
