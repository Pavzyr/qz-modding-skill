"""Shared Blueprint paste-text helpers for the example graph generators (nja_graphs.py etc.).
CB = visitortalk_graphs.B builder + extra node kinds; post_event_graph()/post_anim_graph() = the carrier AnimBP
(BeginPlay -> spawn the manager actor once; AnimGraph = Input Pose only). Set MGR_C / ABP_C before calling them.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import visitortalk_graphs as vt                      # B builder, P/C helpers (paths there are VisitorTalk's, unused)
from qz_bp_paste import Graph, mkpin

MGR_C = None    # "/Script/Engine.BlueprintGeneratedClass'/MyMod/BP_X_Manager.BP_X_Manager_C'"
ABP_C = None    # "/Script/Engine.AnimBlueprintGeneratedClass'/MyMod/Carrier/ABP_X_Post.ABP_X_Post_C'"

P, C, K2 = vt.P, vt.C, vt.K2
T_BOOL, T_TEXT = ("bool", "", None, "None"), ("text", "", None, "None")
T_STR, T_REAL, T_INT = ("string", "", None, "None"), ("real", "double", None, "None"), ("int", "", None, "None")
WCO = lambda: P("WorldContextObject", "in", ("object", "", C("/Script/CoreUObject.Object"), "None"), hidden=True, const=True)
KSL, KML, KTL = "/Script/Engine.KismetStringLibrary", "/Script/Engine.KismetMathLibrary", "/Script/Engine.KismetTextLibrary"
TGT = 'NSLOCTEXT("K2Node", "Target", "Target")'

class CB(vt.B):
    def member(self, owner_cls, owner_t, var, var_t, x, y):
        """Variable of another Blueprint (e.g. MyWidget.InputBox)."""
        return self.g.raw(K2 + "K2Node_VariableGet", ['VariableReference=(MemberParent="%s",MemberName="%s")' % (owner_cls, var),
                                                      "SelfContextInfo=NotSelfContext"],
                          [P(var, "out", var_t), P("self", "in", owner_t, friendly=TGT)], x, y)

    def pure_static(self, lib, func, pins, x, y):
        return self.call(lib, func, pins, x, y, pure=True, static_default=lib.replace(".", ".Default__", 1))

    def wcall(self, parent, func, pins, x, y, pure=False):
        """Member function of a widget class; target pin typed as the declaring class."""
        return self.call(parent, func, pins, x, y, pure=pure, self_type=C(parent))

    def unlink(self, a, apin, b, bpin):
        pa, pb = a.pin(apin, "out"), b.pin(bpin, "in")
        pa["links"] = [l for l in pa["links"] if not l.startswith(b.name + " ")]
        pb["links"] = [l for l in pb["links"] if not l.startswith(a.name + " ")]

    def mset(self, owner_cls, owner_t, var, var_t, x, y, default=None):
        """Set a variable of another Blueprint object (e.g. Obj.Text = ...)."""
        return self.g.raw(K2 + "K2Node_VariableSet", ['VariableReference=(MemberParent="%s",MemberName="%s")' % (owner_cls, var),
                                                      "SelfContextInfo=NotSelfContext"],
                          vt.exec_pins() + [P(var, "in", var_t, default=default), P("Output_Get", "out", var_t),
                                            P("self", "in", owner_t, friendly=TGT)], x, y)

    def break_struct(self, struct, in_name, outs, x, y):
        sp = "/Script/CoreUObject.ScriptStruct'/Script/QZSim.%s'" % struct
        hdr = ['StructType="%s"' % sp, "bMadeAfterOverridePinRemoval=True"]
        for i, (n, _) in enumerate(outs):
            hdr.append('ShowPinForProperties(%d)=(PropertyName="%s",PropertyFriendlyName="%s",bShowPin=True,bCanToggleVisibility=True)' % (i, n, n))
        return self.g.raw(K2 + "K2Node_BreakStruct", hdr, [P(in_name, "in", ("struct", "", sp, "None"))] + [P(n, "out", t) for n, t in outs], x, y)

    def enum_str(self, enum, x, y):
        return self.g.raw(K2 + "K2Node_GetEnumeratorNameAsString", [],
                          [P("Enumerator", "in", ("byte", "", "/Script/CoreUObject.Enum'/Script/QZSim.%s'" % enum, "None")),
                           P("ReturnValue", "out", T_STR)], x, y)

    def gs(self, func, pins, x, y, pure=False):
        """UGameplayStatics static call."""
        return self.call("/Script/Engine.GameplayStatics", func, pins, x, y, pure=pure, static_default="/Script/Engine.Default__GameplayStatics")

    def seq(self, n, x, y):
        return self.g.raw(K2 + "K2Node_ExecutionSequence", [], [P("execute")] + [P("then_%d" % i, "out") for i in range(n)], x, y)



def post_event_graph():
    b = CB(ABP_C)
    g = b.g
    ev = b.event("/Script/Engine.AnimInstance", "BlueprintBeginPlay", 0, 0)
    goc = b.call("/Script/Engine.GameplayStatics", "GetActorOfClass",
                 [P("WorldContextObject", "in", ("object", "", C("/Script/CoreUObject.Object"), "None"), hidden=True, const=True),
                  P("ActorClass", "in", ("class", "", C("/Script/Engine.Actor"), "None"), default_obj=MGR_C.split("'")[1]),
                  P("ReturnValue", "out", ("object", "", MGR_C, "None"))], 300, 0,
                 static_default="/Script/Engine.Default__GameplayStatics")
    vv = b.is_valid(600, 150)
    br = b.branch(850, 0)
    sp = g.raw(K2 + "K2Node_SpawnActorFromClass", ["AdvancedPinDisplay=Hidden"],
               vt.exec_pins() + [P("Class", "in", ("class", "", C("/Script/Engine.Actor"), "None"), default_obj=MGR_C.split("'")[1]),
                                 P("ReturnValue", "out", ("object", "", MGR_C, "None")),
                                 P("SpawnTransform", "in", ("struct", "", "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Transform'", "None")),
                                 P("CollisionHandlingOverride", "in", ("byte", "", "/Script/CoreUObject.Enum'/Script/Engine.ESpawnActorCollisionHandlingMethod'", "None"), default="AlwaysSpawn"),
                                 P("TransformScaleMethod", "in", ("byte", "", "/Script/CoreUObject.Enum'/Script/Engine.ESpawnActorScaleMethod'", "None"), default="MultiplyWithRoot"),
                                 P("Owner", "in", ("object", "", C("/Script/Engine.Actor"), "None")),
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


def post_anim_graph():
    g = Graph()
    g.raw("/Script/AnimGraph.AnimGraphNode_LinkedInputPose", [],
          [mkpin("Pose", "out", "struct", "", "/Script/CoreUObject.ScriptStruct'/Script/Engine.PoseLink'")], -300, 0)
    return g.text()


