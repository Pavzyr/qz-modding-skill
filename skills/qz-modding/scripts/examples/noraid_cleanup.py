# job "py" op: drop the unused test wave config B (nothing references it - checked before deleting)
p = "/NoRaid/Data/DA_NoRaid_EmptyWavesB"
refs = unreal.AssetRegistryHelpers.get_asset_registry().get_referencers(p.rsplit("/", 0)[0], unreal.AssetRegistryDependencyOptions())
REPORT["refs_B"] = [str(r) for r in (refs or [])]
if not REPORT["refs_B"]:
    REPORT["deleted_B"] = EAS.delete_asset(p)
