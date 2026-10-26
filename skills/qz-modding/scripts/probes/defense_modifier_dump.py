# job "py" op (read-only): QzDayModifier_Defense of the Chicago days: all properties; the wave config contents
c = EAS.load_asset("/Game/Data/Companies/Chicago/DA_CompanyChicago")
out = {}
for i in (2, 7, 11, 16, 19):
    d = c.get_editor_property("days")[i - 1]
    for m in d.get_editor_property("modifiers"):
        if m and m.get_class().get_name() == "QzDayModifier_Defense":
            props = {}
            for p in sorted(dir(m)):
                if p.startswith("_"):
                    continue
                try:
                    props[p] = str(m.get_editor_property(p))[:600]
                except Exception:
                    pass
            out["day%02d" % i] = props
REPORT["mods"] = out
wc = unreal.load_asset("/Game/Blueprints/DefenseV2/Data/DA_WaveConfig_02")
REPORT["wave02"] = wc.get_editor_property("spawners").__str__()[:3000] if wc else None
