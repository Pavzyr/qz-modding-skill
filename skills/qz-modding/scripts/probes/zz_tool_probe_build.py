# Build step (qz_mod_job op "py") for mod ZZToolProbe: two auto-granted tools whose wearable actor is our own SWearable child.
# A = normal item (with SInventoryItemFragment), B = without inventory fragment (hidden from wheel?).
import unreal

BEL = unreal.BlueprintEditorLibrary
R = REPORT.setdefault("zz_tool_probe", {})
src = EAS.load_asset("/Game/Blueprints/Tools/UVStick/ID_UVStick")
R["src_fragments"] = []
for f in src.get_editor_property("fragments"):
    R["src_fragments"].append({"class": f.get_class().get_name(),
                               "props": [l.strip() for l in (type(f).__doc__ or "").splitlines() if "``" in l]})
    for l in (type(f).__doc__ or "").splitlines():
        pass

wear_cls = {}
for name in ("BP_ZZWearA", "BP_ZZWearB"):
    p = "/ZZToolProbe/" + name
    bp = EAS.load_asset(p) if EAS.does_asset_exist(p) else BEL.create_blueprint_asset_with_parent(p, unreal.SWearable)
    BEL.compile_blueprint(bp)
    wear_cls[name] = BEL.generated_class(bp)


def frag_set_actor(frag, cls):
    done = []
    for l in (type(frag).__doc__ or "").splitlines():
        if "``" in l and "Class" in l:
            pname = l.split("``")[1]
            try:
                frag.set_editor_property(pname, cls)
                done.append(pname)
            except Exception as e:
                done.append("%s FAILED %s" % (pname, e))
    return done


for letter, keep_inv in (("A", True), ("B", False)):
    ip = "/ZZToolProbe/ID_ZZTool" + letter
    if not EAS.does_asset_exist(ip):
        TOOLS.duplicate_asset("ID_ZZTool" + letter, "/ZZToolProbe", src)
    item = EAS.load_asset(ip)
    frs = list(item.get_editor_property("fragments"))
    newf = []
    for f in frs:
        cn = f.get_class().get_name()
        if cn == "SInventoryItemFragment":
            if not keep_inv:
                continue
            f.set_editor_property("title", unreal.Text("ZZ Probe " + letter))
        if cn == "SWearableItemFragment":
            R["set_" + letter] = frag_set_actor(f, wear_cls["BP_ZZWear" + letter])
        newf.append(f)
    item.set_editor_property("fragments", newf)
    R["fragments_" + letter] = [f.get_class().get_name() for f in item.get_editor_property("fragments")]
    dp = "/ZZToolProbe/DA_ZZTool" + letter
    if not EAS.does_asset_exist(dp):
        fac = unreal.DataAssetFactory()
        fac.set_editor_property("data_asset_class", unreal.QzToolDataAsset)
        TOOLS.create_asset("DA_ZZTool" + letter, "/ZZToolProbe", unreal.QzToolDataAsset, fac)
    da = EAS.load_asset(dp)
    da.set_editor_property("item_data_asset", item)
    da.set_editor_property("tag", tag("Tool.ZZ.Probe" + letter))
    R["da_" + letter] = str(da.get_editor_property("tag"))
