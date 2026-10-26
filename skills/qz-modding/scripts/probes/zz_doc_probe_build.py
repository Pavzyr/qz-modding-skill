# Build step (qz_mod_job op "py") for ZZDocProbe: copy of the doctor mesh + empty post-process AnimBP + StaticNPCSkin(NPC.Skin.Doc).
import unreal

BEL = unreal.BlueprintEditorLibrary
R = REPORT.setdefault("zz_doc_probe", {})
SRC = "/Game/Art/Characters/PA_Collection/Assets/Characters/Mesh/Zheka/LowPoly/D2_Zheka"
MESH = "/ZZDocProbe/SK_ZZ_Doc"
ABP = "/ZZDocProbe/ABP_ZZ_DocPost"
if not EAS.does_asset_exist(MESH):
    TOOLS.duplicate_asset("SK_ZZ_Doc", "/ZZDocProbe", EAS.load_asset(SRC))
mesh = EAS.load_asset(MESH)
skel = mesh.get_editor_property("skeleton")
R["skeleton"] = skel.get_path_name() if skel else None
R["src_post_process"] = str(EAS.load_asset(SRC).get_editor_property("post_process_anim_blueprint"))
if not EAS.does_asset_exist(ABP):
    f = unreal.AnimBlueprintFactory()
    f.set_editor_property("target_skeleton", skel)
    f.set_editor_property("parent_class", unreal.AnimInstance)
    TOOLS.create_asset("ABP_ZZ_DocPost", "/ZZDocProbe", unreal.AnimBlueprint, f)
abp = EAS.load_asset(ABP)
BEL.compile_blueprint(abp)
cls = BEL.generated_class(abp)
mesh.set_editor_property("post_process_anim_blueprint", cls)
R["mesh_post_process"] = str(mesh.get_editor_property("post_process_anim_blueprint"))
R["mesh_materials"] = [str(m.get_editor_property("material_interface").get_path_name()) if m.get_editor_property("material_interface") else None
                       for m in mesh.get_editor_property("materials")]
DA = "/ZZDocProbe/DA_ZZ_DocSkin"
if not EAS.does_asset_exist(DA):
    fac = unreal.DataAssetFactory()
    fac.set_editor_property("data_asset_class", unreal.QzStaticNPCSkinDataAsset)
    TOOLS.create_asset("DA_ZZ_DocSkin", "/ZZDocProbe", unreal.QzStaticNPCSkinDataAsset, fac)
da = EAS.load_asset(DA)
da.set_editor_property("npc_tag", tag("NPC.Skin.Doc"))
da.set_editor_property("mesh", mesh)
R["skin_da"] = {p: str(da.get_editor_property(p)) for p in ("npc_tag", "mesh", "materials")}
