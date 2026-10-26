# job "py" op (read-only): can Python read/write QzDayModifier_Defense.Data?
c = EAS.load_asset("/Game/Data/Companies/Chicago/DA_CompanyChicago")
d = c.get_editor_property("days")[6]
m = [x for x in d.get_editor_property("modifiers") if x and x.get_class().get_name() == "QzDayModifier_Defense"][0]
REPORT["dir"] = [p for p in dir(m) if not p.startswith("_")][:80]
for name in ("data", "Data", "defense_data", "transition_info"):
    try:
        v = m.get_editor_property(name); REPORT["get_" + name] = str(v)[:400]
    except Exception as e:
        REPORT["get_" + name] = "ERR " + str(e)[:200]
cls = unreal.QzDayModifier_Defense
REPORT["cls_dir"] = [p for p in dir(cls) if not p.startswith("_")][:60]
