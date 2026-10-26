# VisitorTalk asset build step. Runs INSIDE the editor via qz_mod_job op {"op":"py","file":"<this>","args":{...}}.
# Carrier = doctor skin (verified in PIE): copy of the doctor mesh with our post-process AnimBP + QzStaticNPCSkinDataAsset(NPC.Skin.Doc).
# Creates: IA_VT_Talk/IMC_VT (Enter, non-consuming), WBP_VT_Hint/WBP_VT_Dialog (copies of a game widget; text = variable Text_Main),
# BP_VT_Manager (variables + defaults; graph pasted by the user), ABP_VT_DocPost (graphs pasted by the user), SK_VT_Doc, DA_VT_DocSkin.
# Idempotent: re-running keeps pasted graphs (BPs are reused); widgets are rebuilt.
import unreal

MOD = "/VisitorTalk"
BEL = unreal.BlueprintEditorLibrary
R = REPORT.setdefault("visitortalk", {})


def exists(p):
    return EAS.does_asset_exist(p)


def data_asset(path, cls):
    if exists(path):
        return EAS.load_asset(path)
    pkg, name = path.rsplit("/", 1)
    fac = unreal.DataAssetFactory()
    fac.set_editor_property("data_asset_class", cls)
    return TOOLS.create_asset(name, pkg, cls, fac)


# ---------------------------------------------------------------- 1. input: IA_VT_Talk on Enter, does not consume Enter
ia = data_asset(MOD + "/Input/IA_VT_Talk", unreal.InputAction)
ia.set_editor_property("consume_input", False)
ia.set_editor_property("value_type", unreal.InputActionValueType.BOOLEAN)
imc = data_asset(MOD + "/Input/IMC_VT", unreal.InputMappingContext)
try:
    imc.unmap_all()
except Exception:
    pass
k = unreal.Key()
k.set_editor_property("key_name", "Enter")
imc.map_key(ia, k)
R["imc"] = [str(m.get_editor_property("key").get_editor_property("key_name")) for m in
            imc.get_editor_property("default_key_mappings").get_editor_property("mappings")]


# ---------------------------------------------------------------- 2. widgets (copy of a game widget; Text_Main stays a BP variable)
def build_widget(name, anchor, align, pos, wrap, text):
    path = MOD + "/UI/" + name
    if exists(path):
        EAS.delete_asset(path)
    wbp = TOOLS.duplicate_asset(name, MOD + "/UI", EAS.load_asset("/Game/UI/Quests/WBP_QuestInteractText"))
    eg = BEL.find_event_graph(wbp)
    if eg:
        BEL.remove_graph(wbp, eg)
    BEL.reparent_blueprint(wbp, unreal.UserWidget)
    tree = unreal.find_object(wbp, "WidgetTree")
    root = unreal.find_object(tree, "SizeBox_0")
    tm = unreal.find_object(tree, "Text_Main")
    for fn in ("clear_width_override", "clear_height_override", "clear_min_desired_width", "clear_min_desired_height",
               "clear_max_desired_width", "clear_max_desired_height", "clear_min_aspect_ratio", "clear_max_aspect_ratio"):
        try:
            getattr(root, fn)()
        except Exception:
            pass
    canvas = unreal.new_object(unreal.CanvasPanel, tree, "VT_Canvas")
    root.set_content(canvas)
    border = unreal.new_object(unreal.Border, tree, "VT_Panel")
    slot = canvas.add_child_to_canvas(border)
    a = unreal.Anchors()
    a.set_editor_property("minimum", unreal.Vector2D(*anchor))
    a.set_editor_property("maximum", unreal.Vector2D(*anchor))
    slot.set_anchors(a)
    slot.set_alignment(unreal.Vector2D(*align))
    slot.set_position(unreal.Vector2D(*pos))
    slot.set_auto_size(True)
    border.set_brush_color(unreal.LinearColor(0.0, 0.0, 0.0, 0.72))
    border.set_padding(unreal.Margin(22, 12, 22, 14))
    border.set_content(tm)
    tm.set_text(unreal.Text(text))
    if wrap:
        try:
            tm.set_editor_property("wrap_text_at", wrap)
        except Exception as e:
            R.setdefault("warn", []).append("wrap %s: %s" % (name, e))
    BEL.compile_blueprint(wbp)
    R[name] = sorted(w.get_path_name().split(":WidgetTree.")[1] for w in unreal.ObjectIterator(unreal.Widget)
                     if w.get_path_name().startswith(wbp.get_path_name() + ":WidgetTree."))
    return BEL.generated_class(wbp)


hint_cls = build_widget("WBP_VT_Hint", (0.5, 0.5), (0.5, 0.0), (0, 56), 0.0, "Enter — Поговорить")
dlg_cls = build_widget("WBP_VT_Dialog", (0.5, 1.0), (0.5, 1.0), (0, -170), 860.0, "Посетитель\n«…»")

# ---------------------------------------------------------------- 3. manager BP (variables + defaults; graph pasted by user)
MGR = MOD + "/BP_VT_Manager"
mgr = EAS.load_asset(MGR) if exists(MGR) else BEL.create_blueprint_asset_with_parent(MGR, unreal.Actor)
T = BEL.get_basic_type_by_name
VARS = [("HintUI", BEL.get_object_reference_type(hint_cls)), ("DialogUI", BEL.get_object_reference_type(dlg_cls)),
        ("FocusedNPC", BEL.get_object_reference_type(unreal.Actor.static_class())),
        ("Initialized", T("bool")), ("DialogOpen", T("bool")),
        ("Phrases", BEL.get_array_type(T("text"))), ("PhrasesRU", BEL.get_array_type(T("text"))),
        ("PhrasesEN", BEL.get_array_type(T("text"))), ("HintRU", T("text")), ("HintEN", T("text"))]
R["mgr_vars_added"] = [n for n, t in VARS if BEL.add_member_variable(mgr, n, t)]
BEL.compile_blueprint(mgr)
cdo = unreal.get_default_object(BEL.generated_class(mgr))
cdo.set_editor_property("PhrasesRU", [unreal.Text("Посетитель\n«%s»" % x) for x in ARGS["phrases_ru"]])
cdo.set_editor_property("PhrasesEN", [unreal.Text("Visitor\n“%s”" % x) for x in ARGS["phrases_en"]])
cdo.set_editor_property("HintRU", unreal.Text("Enter — Поговорить"))
cdo.set_editor_property("HintEN", unreal.Text("Enter — Talk"))
R["mgr_phrases"] = [len(cdo.get_editor_property("PhrasesRU")), len(cdo.get_editor_property("PhrasesEN"))]

# ---------------------------------------------------------------- 4. carrier: doctor mesh copy + post-process AnimBP + skin DA
SRC = "/Game/Art/Characters/PA_Collection/Assets/Characters/Mesh/Zheka/LowPoly/D2_Zheka"
MESH = MOD + "/Carrier/SK_VT_Doc"
ABP = MOD + "/Carrier/ABP_VT_DocPost"
if not exists(MESH):
    TOOLS.duplicate_asset("SK_VT_Doc", MOD + "/Carrier", EAS.load_asset(SRC))
mesh = EAS.load_asset(MESH)
skel = mesh.get_editor_property("skeleton")
if not exists(ABP):
    f = unreal.AnimBlueprintFactory()
    f.set_editor_property("target_skeleton", skel)
    f.set_editor_property("parent_class", unreal.AnimInstance)
    TOOLS.create_asset("ABP_VT_DocPost", MOD + "/Carrier", unreal.AnimBlueprint, f)
abp = EAS.load_asset(ABP)
BEL.compile_blueprint(abp)
mesh.set_editor_property("post_process_anim_blueprint", BEL.generated_class(abp))
skin = data_asset(MOD + "/Carrier/DA_VT_DocSkin", unreal.QzStaticNPCSkinDataAsset)
skin.set_editor_property("npc_tag", tag("NPC.Skin.Doc"))
skin.set_editor_property("mesh", mesh)
R["carrier"] = {"skeleton": skel.get_path_name(), "post_process": str(mesh.get_editor_property("post_process_anim_blueprint")),
                "skin_mesh": str(skin.get_editor_property("mesh"))}
log("visitortalk build done: %s" % R.get("carrier"))
