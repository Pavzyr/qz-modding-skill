"""Generate paste texts (Ctrl+V into a Blueprint graph) for the VisitorTalk mod.
  python -I visitortalk_graphs.py <out_dir>
Outputs:
  1_BP_VT_Manager__EventGraph.txt   -> BP_VT_Manager, Event Graph
  2_ABP_VT_DocPost__EventGraph.txt  -> ABP_VT_DocPost, Event Graph
  3_ABP_VT_DocPost__AnimGraph.txt   -> ABP_VT_DocPost, AnimGraph (then drag "Input Pose" -> "Output Pose")
Function names/flags/params verified from DLLs (scripts/ufunc_flags.py) and real game nodes (node_library.json).
"""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from qz_bp_paste import Graph, mkpin, retype

MOD = "/VisitorTalk"
BPGC = "/Script/Engine.BlueprintGeneratedClass"
WBGC = "/Script/UMG.WidgetBlueprintGeneratedClass"
MGR_C = "%s'%s/BP_VT_Manager.BP_VT_Manager_C'" % (BPGC, MOD)
HINT_C = "%s'%s/UI/WBP_VT_Hint.WBP_VT_Hint_C'" % (WBGC, MOD)
DLG_C = "%s'%s/UI/WBP_VT_Dialog.WBP_VT_Dialog_C'" % (WBGC, MOD)
ABP_C = "/Script/Engine.AnimBlueprintGeneratedClass'%s/Carrier/ABP_VT_DocPost.ABP_VT_DocPost_C'" % MOD
IA = "/Script/EnhancedInput.InputAction'%s/Input/IA_VT_Talk.IA_VT_Talk'" % MOD
IMC = "/Script/EnhancedInput.InputMappingContext'%s/Input/IMC_VT.IMC_VT'" % MOD
C = lambda p: "/Script/CoreUObject.Class'%s'" % p
VIS = "/Script/CoreUObject.Enum'/Script/UMG.ESlateVisibility'"
STATE = "/Script/CoreUObject.Enum'/Script/QZSim.EQzCvNPCState'"
K2 = "/Script/BlueprintGraph."
OUT = sys.argv[1] if len(sys.argv) > 1 else "."

# pin type helpers: (cat, sub, obj, container)
T_BOOL = ("bool", "", None, "None")
T_TEXT = ("text", "", None, "None")
T_TEXTS = ("text", "", None, "Array")
T_ACTOR = ("object", "", C("/Script/Engine.Actor"), "None")
T_HINT = ("object", "", HINT_C, "None")
T_DLG = ("object", "", DLG_C, "None")


def P(name, d="in", t=("exec", "", None, "None"), **kw):
    return mkpin(name, d, t[0], t[1], t[2], t[3], **kw)


def exec_pins():
    return [P("execute"), P("then", "out")]


class B:
    """Graph builder with typed helpers (self-context = the Blueprint being pasted into)."""

    def __init__(self, self_cls):
        self.g = Graph()
        self.self_cls = self_cls

    # ---- variables of the pasted-into Blueprint
    def get(self, var, t, x, y):
        return self.g.raw(K2 + "K2Node_VariableGet", ['VariableReference=(MemberName="%s",bSelfContext=True)' % var],
                          [P(var, "out", t), P("self", "in", ("object", "", self.self_cls, "None"), hidden=True,
                                               friendly='NSLOCTEXT("K2Node", "Target", "Target")')], x, y)

    def set(self, var, t, x, y, default=None):
        return self.g.raw(K2 + "K2Node_VariableSet", ['VariableReference=(MemberName="%s",bSelfContext=True)' % var],
                          exec_pins() + [P(var, "in", t, default=default), P("Output_Get", "out", t),
                                         P("self", "in", ("object", "", self.self_cls, "None"), hidden=True,
                                           friendly='NSLOCTEXT("K2Node", "Target", "Target")')], x, y)

    # ---- function calls
    def call(self, parent, func, pins, x, y, pure=False, static_default=None, self_type=None, self_hidden=False):
        hdr = ['FunctionReference=(MemberParent="%s",MemberName="%s")' % (C(parent), func)]
        ps = [] if pure else exec_pins()
        if static_default:
            ps.append(P("self", "in", ("object", "", C(parent), "None"), default_obj=static_default, hidden=True,
                        friendly='NSLOCTEXT("K2Node", "Target", "Target")'))
        else:
            ps.append(P("self", "in", ("object", "", self_type or C(parent), "None"), hidden=self_hidden,
                        friendly='NSLOCTEXT("K2Node", "Target", "Target")'))
        return self.g.raw(K2 + "K2Node_CallFunction", hdr, ps + pins, x, y)

    def self_call(self, func, x, y):
        return self.g.raw(K2 + "K2Node_CallFunction", ['FunctionReference=(MemberName="%s",bSelfContext=True)' % func],
                          exec_pins() + [P("self", "in", ("object", "", self.self_cls, "None"),
                                           friendly='NSLOCTEXT("K2Node", "Target", "Target")')], x, y)

    def branch(self, x, y):
        return self.g.raw(K2 + "K2Node_IfThenElse", [], [P("execute"), P("Condition", "in", T_BOOL, default="false"),
                                                         P("then", "out"), P("else", "out")], x, y)

    def is_valid(self, x, y):
        return self.call("/Script/Engine.KismetSystemLibrary", "IsValid",
                         [P("Object", "in", ("object", "", C("/Script/CoreUObject.Object"), "None"), const=True), P("ReturnValue", "out", T_BOOL, default="false")],
                         x, y, pure=True, static_default="/Script/Engine.Default__KismetSystemLibrary")

    def cast(self, target_cls_path, as_name, as_type, x, y):
        return self.g.raw(K2 + "K2Node_DynamicCast", ['TargetType="%s"' % target_cls_path],
                          [P("execute"), P("then", "out"), P("CastFailed", "out"),
                           P("Object", "in", ("object", "", C("/Script/CoreUObject.Object"), "None")),
                           P(as_name, "out", ("object", "", as_type, "None")), P("bSuccess", "out", T_BOOL, hidden=True)], x, y)

    def set_vis(self, widget_type, vis, x, y):
        return self.call("/Script/UMG.Widget", "SetVisibility",
                         [P("InVisibility", "in", ("byte", "", VIS, "None"), default=vis)], x, y, self_type=widget_type)

    def custom_event(self, name, x, y):
        return self.g.raw(K2 + "K2Node_CustomEvent", ['CustomFunctionName="%s"' % name],
                          [P("OutputDelegate", "out", ("delegate", "", None, "None"),
                             member_ref='(MemberParent="%s",MemberName="%s")' % (self.self_cls, name)), P("then", "out")], x, y)

    def event(self, parent, name, x, y):
        return self.g.raw(K2 + "K2Node_Event", ['EventReference=(MemberParent="%s",MemberName="%s")' % (C(parent), name),
                                                "bOverrideFunction=True"],
                          [P("OutputDelegate", "out", ("delegate", "", None, "None"),
                             member_ref='(MemberParent="%s",MemberName="%s")' % (C(parent), name)), P("then", "out")], x, y)

    def timer(self, time, loop, x, y):
        return self.call("/Script/Engine.KismetSystemLibrary", "K2_SetTimerDelegate",
                         [P("Delegate", "in", ("delegate", "", None, "None"), friendly='INVTEXT("Event")',
                            member_ref='(MemberParent="/Script/CoreUObject.Package\'/Script/Engine\'",MemberName="TimerDynamicDelegate__DelegateSignature")'),
                          P("Time", "in", ("real", "float", None, "None"), default="%f" % time),
                          P("bLooping", "in", T_BOOL, default="true" if loop else "false"),
                          P("bMaxOncePerFrame", "in", T_BOOL, default="false"),
                          P("InitialStartDelay", "in", ("real", "float", None, "None"), default="0.000000"),
                          P("InitialStartDelayVariance", "in", ("real", "float", None, "None"), default="0.000000"),
                          P("ReturnValue", "out", ("struct", "", "/Script/CoreUObject.ScriptStruct'/Script/Engine.TimerHandle'", "None"))],
                         x, y, static_default="/Script/Engine.Default__KismetSystemLibrary")

    def text(self):
        return self.g.text()


L = lambda b, *chain: [b.g.link(chain[i][0], chain[i][1], chain[i + 1][0], chain[i + 1][2]) for i in range(0, len(chain) - 1, 2)]


def manager():
    b = B(MGR_C)
    g = b.g
    # ---------------- BeginPlay -> looping timer VT_Update (0.1 s)
    ev = b.event("/Script/Engine.Actor", "ReceiveBeginPlay", 0, 0)
    upd = b.custom_event("VT_Update", 0, 300)
    t1 = b.timer(0.1, True, 350, 0)
    g.link(ev, "then", t1, "execute"); g.link(upd, "OutputDelegate", t1, "Delegate")
    # ---------------- VT_Update: initialized?
    gi = b.get("Initialized", T_BOOL, 250, 420)
    br0 = b.branch(450, 300)
    g.link(upd, "then", br0, "execute"); g.link(gi, "Initialized", br0, "Condition")
    # ---------------- init (else branch)
    pc = b.call("/Script/Engine.GameplayStatics", "GetPlayerController",
                [P("WorldContextObject", "in", ("object", "", C("/Script/CoreUObject.Object"), "None"), hidden=True),
                 P("PlayerIndex", "in", ("int", "", None, "None"), default="0"),
                 P("ReturnValue", "out", ("object", "", C("/Script/Engine.PlayerController"), "None"))],
                700, 760, pure=True, static_default="/Script/Engine.Default__GameplayStatics")
    v_pc = b.is_valid(950, 640)
    br1 = b.branch(1150, 560)
    g.link(br0, "else", br1, "execute"); g.link(pc, "ReturnValue", v_pc, "Object"); g.link(v_pc, "ReturnValue", br1, "Condition")
    en = b.call("/Script/Engine.Actor", "EnableInput",
                [P("PlayerController", "in", ("object", "", C("/Script/Engine.PlayerController"), "None"))], 1400, 560,
                self_type=C("/Script/Engine.Actor"))
    g.link(br1, "then", en, "execute"); g.link(pc, "ReturnValue", en, "PlayerController")
    sub = g.raw(K2 + "K2Node_GetSubsystemFromPC", ['CustomClass="%s"' % C("/Script/EnhancedInput.EnhancedInputLocalPlayerSubsystem")],
                [P("PlayerController", "in", ("object", "", C("/Script/Engine.PlayerController"), "None")),
                 P("ReturnValue", "out", ("object", "", C("/Script/EnhancedInput.EnhancedInputLocalPlayerSubsystem"), "None"))], 1400, 780)
    g.link(pc, "ReturnValue", sub, "PlayerController")
    amc = g.raw(K2 + "K2Node_CallFunction",
                ['FunctionReference=(MemberParent="%s",MemberName="AddMappingContext")' % C("/Script/EnhancedInput.EnhancedInputSubsystemInterface")],
                exec_pins() + [P("self", "in", ("interface", "", C("/Script/EnhancedInput.EnhancedInputSubsystemInterface"), "None"),
                                 friendly='NSLOCTEXT("K2Node", "Target", "Target")'),
                               P("MappingContext", "in", ("object", "", C("/Script/EnhancedInput.InputMappingContext"), "None"), default_obj=IMC.split("'")[1], const=True),
                               P("Priority", "in", ("int", "", None, "None"), default="1"),
                               P("Options", "in", ("struct", "", "/Script/CoreUObject.ScriptStruct'/Script/EnhancedInput.ModifyContextOptions'", "None"),
                                 default="(bIgnoreAllPressedKeysUntilRelease=True,bForceImmediately=False,bNotifyUserSettings=False)", ref=True, const=True)],
                1700, 560)
    g.link(en, "then", amc, "execute"); g.link(sub, "ReturnValue", amc, "self")
    x = 2000
    prev = amc
    made = {}
    for var, cls, typ, z in (("HintUI", HINT_C, T_HINT, 50), ("DialogUI", DLG_C, T_DLG, 51)):
        cw = g.raw("/Script/UMGEditor.K2Node_CreateWidget", [],
                   exec_pins() + [P("Class", "in", ("class", "", C("/Script/UMG.UserWidget"), "None"), default_obj=cls.split("'")[1]),
                                  P("ReturnValue", "out", ("object", "", cls, "None")),
                                  P("OwningPlayer", "in", ("object", "", C("/Script/Engine.PlayerController"), "None"))], x, 560)
        sv = b.set(var, typ, x + 300, 560)
        av = b.call("/Script/UMG.UserWidget", "AddToViewport", [P("ZOrder", "in", ("int", "", None, "None"), default=str(z))], x + 550, 560)
        hv = b.set_vis(C("/Script/UMG.Widget"), "Collapsed", x + 800, 560)
        g.link(prev, "then", cw, "execute"); g.link(pc, "ReturnValue", cw, "OwningPlayer")
        g.link(cw, "then", sv, "execute"); g.link(cw, "ReturnValue", sv, var)
        g.link(sv, "then", av, "execute"); g.link(cw, "ReturnValue", av, "self")
        g.link(av, "then", hv, "execute"); g.link(cw, "ReturnValue", hv, "self")
        prev = hv
        made[var] = cw
        x += 1100
    # language
    cul = b.call("/Script/Engine.KismetInternationalizationLibrary", "GetCurrentCulture",
                 [P("ReturnValue", "out", ("string", "", None, "None"))], x, 760, pure=True,
                 static_default="/Script/Engine.Default__KismetInternationalizationLibrary")
    sw = b.call("/Script/Engine.KismetStringLibrary", "StartsWith",
                [P("SourceString", "in", ("string", "", None, "None"), ref=True, const=True),
                 P("InPrefix", "in", ("string", "", None, "None"), default="ru", ref=True, const=True),
                 P("SearchCase", "in", ("byte", "", "/Script/CoreUObject.Enum'/Script/CoreUObject.ESearchCase'", "None"), default="IgnoreCase"),
                 P("ReturnValue", "out", T_BOOL, default="false")], x + 250, 760, pure=True,
                static_default="/Script/Engine.Default__KismetStringLibrary")
    brl = b.branch(x + 500, 560)
    g.link(prev, "then", brl, "execute"); g.link(cul, "ReturnValue", sw, "SourceString"); g.link(sw, "ReturnValue", brl, "Condition")
    s_init = b.set("Initialized", T_BOOL, x + 2000, 600, default="true")
    for i, (pin, src_ph, src_hint) in enumerate((("then", "PhrasesRU", "HintRU"), ("else", "PhrasesEN", "HintEN"))):
        yy = 460 + i * 420
        gp = b.get(src_ph, T_TEXTS, x + 650, yy + 120)
        sp = b.set("Phrases", T_TEXTS, x + 900, yy)
        gh = b.get("HintUI", T_HINT, x + 900, yy + 220)
        tm = g.raw(K2 + "K2Node_VariableGet", ['VariableReference=(MemberParent="%s",MemberName="Text_Main")' % HINT_C, "SelfContextInfo=NotSelfContext"],
                   [P("Text_Main", "out", ("object", "", C("/Script/CommonUI.CommonRichTextBlock"), "None")),
                    P("self", "in", T_HINT, friendly='NSLOCTEXT("K2Node", "Target", "Target")')], x + 1100, yy + 220)
        gt = b.get(src_hint, T_TEXT, x + 1100, yy + 320)
        st = b.call("/Script/UMG.RichTextBlock", "SetText", [P("InText", "in", T_TEXT, ref=True, const=True)], x + 1400, yy)
        g.link(brl, pin, sp, "execute"); g.link(gp, src_ph, sp, "Phrases")
        g.link(sp, "then", st, "execute"); g.link(gh, "HintUI", tm, "self"); g.link(tm, "Text_Main", st, "self"); g.link(gt, src_hint, st, "InText")
        g.link(st, "then", s_init, "execute")
    # ---------------- focus logic (then branch of br0)
    y0 = -700
    pch = b.call("/Script/Engine.GameplayStatics", "GetPlayerCharacter",
                 [P("WorldContextObject", "in", ("object", "", C("/Script/CoreUObject.Object"), "None"), hidden=True),
                  P("PlayerIndex", "in", ("int", "", None, "None"), default="0"),
                  P("ReturnValue", "out", ("object", "", C("/Script/Engine.Character"), "None"))],
                 650, y0 + 200, pure=True, static_default="/Script/Engine.Default__GameplayStatics")
    c1 = b.cast(C("/Script/QZSim.SCharacter"), "AsSCharacter", C("/Script/QZSim.SCharacter"), 900, y0)
    g.link(br0, "then", c1, "execute"); g.link(pch, "ReturnValue", c1, "Object")
    foc = b.call("/Script/QZSim.SCharacter", "GetActorInFocus", [P("ReturnValue", "out", T_ACTOR)], 1150, y0 + 200, pure=True)
    g.link(c1, "AsSCharacter", foc, "self")
    c2 = b.cast(C("/Script/QZSim.QzNPCCharacter"), "AsQz NPCCharacter", C("/Script/QZSim.QzNPCCharacter"), 1400, y0)
    g.link(c1, "then", c2, "execute"); g.link(foc, "ReturnValue", c2, "Object")
    gs = b.call("/Script/QZSim.QzNPCCharacter", "GetState", [P("ReturnValue", "out", ("byte", "", STATE, "None"), default="None")],
                1650, y0 + 200, pure=True)
    g.link(c2, "AsQz NPCCharacter", gs, "self")
    eqs = []
    for i, val in enumerate(("Inspection", "IdleInspection")):
        eq = g.raw(K2 + "K2Node_EnumEquality", [], [P("ReturnValue", "out", T_BOOL),
                                                     P("A", "in", ("byte", "", STATE, "None")),
                                                     P("B", "in", ("byte", "", STATE, "None"), default=val)], 1900, y0 + 200 + i * 150)
        g.link(gs, "ReturnValue", eq, "A")
        eqs.append(eq)
    bA = b.branch(2150, y0)
    bB = b.branch(2400, y0 + 250)
    g.link(c2, "then", bA, "execute"); g.link(eqs[0], "ReturnValue", bA, "Condition")
    g.link(bA, "else", bB, "execute"); g.link(eqs[1], "ReturnValue", bB, "Condition")
    s_show = b.set("FocusedNPC", T_ACTOR, 2700, y0)
    g.link(bA, "then", s_show, "execute"); g.link(bB, "then", s_show, "execute"); g.link(c2, "AsQz NPCCharacter", s_show, "FocusedNPC")
    gh1 = b.get("HintUI", T_HINT, 2950, y0 + 180)
    v_show = b.set_vis(C("/Script/UMG.Widget"), "HitTestInvisible", 3150, y0)
    g.link(s_show, "then", v_show, "execute"); g.link(gh1, "HintUI", v_show, "self")
    s_hide = b.set("FocusedNPC", T_ACTOR, 2700, y0 + 450)
    for nd, pin in ((bB, "else"), (c1, "CastFailed"), (c2, "CastFailed")):
        g.link(nd, pin, s_hide, "execute")
    gh2 = b.get("HintUI", T_HINT, 2950, y0 + 630)
    v_hide = b.set_vis(C("/Script/UMG.Widget"), "Collapsed", 3150, y0 + 450)
    g.link(s_hide, "then", v_hide, "execute"); g.link(gh2, "HintUI", v_hide, "self")
    # ---------------- Enter (IA_VT_Talk Started)
    y1 = 1500
    ia = g.raw("/Script/InputBlueprintNodes.K2Node_EnhancedInputAction", ['InputAction="%s"' % IA],
               [P("Triggered", "out"), P("Started", "out"), P("Ongoing", "out"), P("Canceled", "out"), P("Completed", "out"),
                P("ActionValue", "out", T_BOOL, default="false"),
                P("ElapsedSeconds", "out", ("real", "double", None, "None"), hidden=True),
                P("TriggeredSeconds", "out", ("real", "double", None, "None"), hidden=True),
                P("InputAction", "out", ("object", "", C("/Script/EnhancedInput.InputAction"), "None"), default_obj=IA.split("'")[1], hidden=True)],
               0, y1)
    gdo = b.get("DialogOpen", T_BOOL, 250, y1 + 150)
    bd = b.branch(450, y1)
    g.link(ia, "Started", bd, "execute"); g.link(gdo, "DialogOpen", bd, "Condition")
    cl = b.self_call("VT_CloseDialog", 700, y1 - 150)
    g.link(bd, "then", cl, "execute")
    gf = b.get("FocusedNPC", T_ACTOR, 450, y1 + 300)
    vf = b.is_valid(650, y1 + 300)
    bf = b.branch(900, y1 + 100)
    g.link(bd, "else", bf, "execute"); g.link(gf, "FocusedNPC", vf, "Object"); g.link(vf, "ReturnValue", bf, "Condition")
    gph = b.get("Phrases", T_TEXTS, 900, y1 + 400)
    alen = b.call("/Script/Engine.KismetArrayLibrary", "Array_Length",
                  [P("TargetArray", "in", T_TEXTS, ref=True, const=True), P("ReturnValue", "out", ("int", "", None, "None"), default="0")],
                  1150, y1 + 500, pure=True, static_default="/Script/Engine.Default__KismetArrayLibrary")
    rnd = b.call("/Script/Engine.KismetMathLibrary", "RandomInteger",
                 [P("Max", "in", ("int", "", None, "None"), default="0"), P("ReturnValue", "out", ("int", "", None, "None"), default="0")],
                 1400, y1 + 500, pure=True, static_default="/Script/Engine.Default__KismetMathLibrary")
    aget = b.call("/Script/Engine.KismetArrayLibrary", "Array_Get",
                  [P("TargetArray", "in", T_TEXTS, ref=True, const=True), P("Index", "in", ("int", "", None, "None"), default="0"),
                   P("Item", "out", T_TEXT)], 1650, y1 + 400, pure=True, static_default="/Script/Engine.Default__KismetArrayLibrary")
    for n_ in (alen, aget):   # array helpers are K2Node_CallArrayFunction in the editor
        n_.header[0] = n_.header[0].replace("Class=/Script/BlueprintGraph.K2Node_CallFunction ", "Class=/Script/BlueprintGraph.K2Node_CallArrayFunction ")
    g.link(gph, "Phrases", alen, "TargetArray"); g.link(alen, "ReturnValue", rnd, "Max")
    g.link(gph, "Phrases", aget, "TargetArray"); g.link(rnd, "ReturnValue", aget, "Index")
    gdl = b.get("DialogUI", T_DLG, 1650, y1 + 250)
    tmd = g.raw(K2 + "K2Node_VariableGet", ['VariableReference=(MemberParent="%s",MemberName="Text_Main")' % DLG_C, "SelfContextInfo=NotSelfContext"],
                [P("Text_Main", "out", ("object", "", C("/Script/CommonUI.CommonRichTextBlock"), "None")),
                 P("self", "in", T_DLG, friendly='NSLOCTEXT("K2Node", "Target", "Target")')], 1850, y1 + 250)
    st2 = b.call("/Script/UMG.RichTextBlock", "SetText", [P("InText", "in", T_TEXT, ref=True, const=True)], 2100, y1 + 100)
    g.link(bf, "then", st2, "execute"); g.link(gdl, "DialogUI", tmd, "self"); g.link(tmd, "Text_Main", st2, "self"); g.link(aget, "Item", st2, "InText")
    gdl2 = b.get("DialogUI", T_DLG, 2350, y1 + 280)
    vs = b.set_vis(C("/Script/UMG.Widget"), "HitTestInvisible", 2550, y1 + 100)
    g.link(st2, "then", vs, "execute"); g.link(gdl2, "DialogUI", vs, "self")
    sdo = b.set("DialogOpen", T_BOOL, 2850, y1 + 100, default="true")
    g.link(vs, "then", sdo, "execute")
    ce = b.custom_event("VT_CloseDialog", 2850, y1 + 500)
    t2 = b.timer(6.0, False, 3150, y1 + 100)
    g.link(sdo, "then", t2, "execute"); g.link(ce, "OutputDelegate", t2, "Delegate")
    # ---------------- VT_CloseDialog
    gdl3 = b.get("DialogUI", T_DLG, 3150, y1 + 700)
    vh = b.set_vis(C("/Script/UMG.Widget"), "Collapsed", 3400, y1 + 500)
    sdc = b.set("DialogOpen", T_BOOL, 3700, y1 + 500, default="false")
    g.link(ce, "then", vh, "execute"); g.link(gdl3, "DialogUI", vh, "self"); g.link(vh, "then", sdc, "execute")
    return b.text()


def doc_event_graph():
    b = B(ABP_C)
    g = b.g
    ev = b.event("/Script/Engine.AnimInstance", "BlueprintBeginPlay", 0, 0)
    goc = b.call("/Script/Engine.GameplayStatics", "GetActorOfClass",
                 [P("WorldContextObject", "in", ("object", "", C("/Script/CoreUObject.Object"), "None"), hidden=True),
                  P("ActorClass", "in", ("class", "", C("/Script/Engine.Actor"), "None"), default_obj=MGR_C.split("'")[1]),
                  P("ReturnValue", "out", ("object", "", MGR_C, "None"))], 300, 0,
                 static_default="/Script/Engine.Default__GameplayStatics")
    vv = b.is_valid(600, 150)
    br = b.branch(850, 0)
    sp = g.raw(K2 + "K2Node_SpawnActorFromClass", ["AdvancedPinDisplay=Hidden"],
               exec_pins() + [P("Class", "in", ("class", "", C("/Script/Engine.Actor"), "None"), default_obj=MGR_C.split("'")[1]),
                              P("ReturnValue", "out", ("object", "", MGR_C, "None")),
                              P("SpawnTransform", "in", ("struct", "", "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Transform'", "None")),
                              P("CollisionHandlingOverride", "in", ("byte", "", "/Script/CoreUObject.Enum'/Script/Engine.ESpawnActorCollisionHandlingMethod'", "None"), default="AlwaysSpawn"),
                              P("TransformScaleMethod", "in", ("byte", "", "/Script/CoreUObject.Enum'/Script/Engine.ESpawnActorScaleMethod'", "None"), default="MultiplyWithRoot"),
                              P("Owner", "in", T_ACTOR),
                              P("Instigator", "in", ("object", "", C("/Script/Engine.Pawn"), "None"))], 1100, 0)
    mt = b.call("/Script/Engine.KismetMathLibrary", "MakeTransform",
                [P("Location", "in", ("struct", "", "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Vector'", "None"), default="0, 0, 0"),
                 P("Rotation", "in", ("struct", "", "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Rotator'", "None"), default="0, 0, 0"),
                 P("Scale", "in", ("struct", "", "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Vector'", "None"), default="1.000000,1.000000,1.000000"),
                 P("ReturnValue", "out", ("struct", "", "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Transform'", "None"))],
                850, 300, pure=True, static_default="/Script/Engine.Default__KismetMathLibrary")
    g.link(mt, "ReturnValue", sp, "SpawnTransform")   # a split SpawnTransform does not survive paste (verified 2026-10-16)
    g.link(ev, "then", goc, "execute"); g.link(goc, "then", br, "execute"); g.link(goc, "ReturnValue", vv, "Object")
    g.link(vv, "ReturnValue", br, "Condition"); g.link(br, "else", sp, "execute")
    return b.text()


def doc_anim_graph():
    g = Graph()
    g.raw("/Script/AnimGraph.AnimGraphNode_LinkedInputPose", [],
          [mkpin("Pose", "out", "struct", "", "/Script/CoreUObject.ScriptStruct'/Script/Engine.PoseLink'")], -300, 0)
    return g.text()


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, txt in (("1_BP_VT_Manager__EventGraph.txt", manager()), ("2_ABP_VT_DocPost__EventGraph.txt", doc_event_graph()),
                    ("3_ABP_VT_DocPost__AnimGraph.txt", doc_anim_graph())):
        open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="\r\n").write(txt)
        print(fn, txt.count("Begin Object"), "nodes", len(txt), "chars")
