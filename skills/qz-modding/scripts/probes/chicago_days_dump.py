# job "py" op (read-only): each Chicago campaign day -> modifiers (class + defence-related props) and references to QzNewDayData
c = EAS.load_asset("/Game/Data/Companies/Chicago/DA_CompanyChicago")
out = []
for i, d in enumerate(c.get_editor_property("days")):
    rec = {"i": i + 1, "day": d.get_name()}
    for p in sorted(dir(d)):
        if p.startswith("_"):
            continue
        try:
            v = d.get_editor_property(p)
        except Exception:
            continue
        s = str(v)
        if "NewDay" in s or "defen" in p.lower() or "raid" in p.lower() or "CampShort" in s:
            rec[p] = s[:300]
    mods = []
    for m in d.get_editor_property("modifiers"):
        if not m:
            continue
        mrec = m.get_class().get_name()
        extra = []
        for p in dir(m):
            if p.startswith("_"):
                continue
            try:
                v = m.get_editor_property(p)
            except Exception:
                continue
            s = str(v)
            if any(k in p.lower() for k in ("defen", "wave", "level", "zombie", "raid", "convoy")) or "Defense" in s or "Wave" in s:
                extra.append("%s=%s" % (p, s[:200]))
        mods.append(mrec + (" {" + "; ".join(extra) + "}" if extra else ""))
    rec["modifiers"] = mods
    out.append(rec)
REPORT["days"] = out
