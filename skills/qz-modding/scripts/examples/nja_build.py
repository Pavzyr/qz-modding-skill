# NoJacketsAuto asset build step (2026-10-20). Runs INSIDE the editor via qz_mod_job op {"op":"py","file":"<this>"}.
# Graphs: nja_graphs.py (pasted by the user).
# Creates: BP_NJA_Manager (variables Jacket, Top), ABP_NJA_DocPost (empty, graphs pasted), SK_NJA_Doc (doctor mesh copy with
# post-process AnimBP), DA_NJA_DocSkin (NPC.Skin.Doc). Idempotent: existing BPs are reused (pasted graphs kept).
import unreal

MOD = "/NoJacketsAuto"
BEL = unreal.BlueprintEditorLibrary
R = REPORT.setdefault("nja", {})


def exists(p):
    return EAS.does_asset_exist(p)


MGR = MOD + "/BP_NJA_Manager"
mgr = EAS.load_asset(MGR) if exists(MGR) else BEL.create_blueprint_asset_with_parent(MGR, unreal.Actor)
skmc = BEL.get_object_reference_type(unreal.SkeletalMeshComponent.static_class())
R["mgr_vars_added"] = [n for n in ("Jacket", "Top") if BEL.add_member_variable(mgr, n, skmc)]
BEL.compile_blueprint(mgr)

SRC = "/Game/Art/Characters/PA_Collection/Assets/Characters/Mesh/Zheka/LowPoly/D2_Zheka"
MESH, ABP = MOD + "/Carrier/SK_NJA_Doc", MOD + "/Carrier/ABP_NJA_DocPost"
if not exists(MESH):
    TOOLS.duplicate_asset("SK_NJA_Doc", MOD + "/Carrier", EAS.load_asset(SRC))
mesh = EAS.load_asset(MESH)
skel = mesh.get_editor_property("skeleton")
if not exists(ABP):
    f = unreal.AnimBlueprintFactory()
    f.set_editor_property("target_skeleton", skel)
    f.set_editor_property("parent_class", unreal.AnimInstance)
    TOOLS.create_asset("ABP_NJA_DocPost", MOD + "/Carrier", unreal.AnimBlueprint, f)
abp = EAS.load_asset(ABP)
BEL.compile_blueprint(abp)
mesh.set_editor_property("post_process_anim_blueprint", BEL.generated_class(abp))
DA = MOD + "/Carrier/DA_NJA_DocSkin"
if exists(DA):
    skin = EAS.load_asset(DA)
else:
    fac = unreal.DataAssetFactory()
    fac.set_editor_property("data_asset_class", unreal.QzStaticNPCSkinDataAsset)
    skin = TOOLS.create_asset("DA_NJA_DocSkin", MOD + "/Carrier", unreal.QzStaticNPCSkinDataAsset, fac)
skin.set_editor_property("npc_tag", tag("NPC.Skin.Doc"))
skin.set_editor_property("mesh", mesh)
R["carrier"] = {"skeleton": skel.get_path_name(), "post_process": str(mesh.get_editor_property("post_process_anim_blueprint")),
                "skin_mesh": str(skin.get_editor_property("mesh")), "skin_tag": str(skin.get_editor_property("npc_tag"))}
log("nja build done: %s" % R)
