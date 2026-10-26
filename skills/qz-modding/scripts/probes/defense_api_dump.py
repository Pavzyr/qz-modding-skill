# job "py" op (read-only): Blueprint-callable surface around the defence (raid) phase and the day flow
import inspect
out = {}
names = sorted(n for n in dir(unreal) if any(k in n for k in ("Defen", "GameFlow", "NewDay", "DayManager", "Campaign", "Raid", "Wave")))
names += [n for n in ("QzGameInstance", "SGameInstance", "QzGameMode", "SGameModeBase", "QzPlayerController", "SGameState", "QzGameState") if hasattr(unreal, n)]
for n in names:
    c = getattr(unreal, n, None)
    if c is None or not inspect.isclass(c):
        continue
    own = []
    for m in sorted(set(dir(c)) - set(dir(unreal.Actor)) - set(dir(unreal.Object))):
        if m.startswith("_"):
            continue
        a = getattr(c, m, None)
        if callable(a):
            doc = (a.__doc__ or "").strip().split("\n")[0][:160]
            own.append("%s :: %s" % (m, doc))
    out[n] = own
REPORT["api"] = out
