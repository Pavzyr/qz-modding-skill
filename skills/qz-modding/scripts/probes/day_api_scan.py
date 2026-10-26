# job "py" op (read-only): every callable that returns or takes QzNewDayData / mentions defence in the QZSim module
import inspect
hits = []
for n in dir(unreal):
    c = getattr(unreal, n, None)
    if not inspect.isclass(c) or not (n.startswith("Qz") or n.startswith("S")):
        continue
    for m in dir(c):
        if m.startswith("_"):
            continue
        try:
            a = getattr(c, m)
        except Exception:
            continue
        doc = (getattr(a, "__doc__", "") or "").split("\n")[0]
        if "QzNewDayData" in doc or ("defen" in m.lower() and callable(a)) or ("day_data" in m.lower() and callable(a)):
            hits.append("%s.%s :: %s" % (n, m, doc[:200]))
REPORT["hits"] = sorted(set(hits))[:300]
