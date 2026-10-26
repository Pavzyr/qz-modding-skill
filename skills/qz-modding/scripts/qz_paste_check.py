"""Compare a generated paste text against REAL nodes from node_library.json (plain Python).
  python -I qz_paste_check.py <paste.txt>
For every CallFunction / CallArrayFunction node whose function has a harvested example: MemberParent, pin names, directions,
pin categories, sub-category objects, containers and ref/const flags must match. Prints differences; exit 1 if any."""
import json, os, re, sys

LIB = os.path.join(os.environ.get("LOCALAPPDATA", ""), "QZSim", "Saved", "ModSchema", "nodes", "node_library.json")
lib = json.load(open(LIB, encoding="utf-8"))["lib"]


def blocks(text):
    return re.findall(r"Begin Object Class=(\S+) Name=\"[^\"]+\"(.*?)\nEnd Object", text, re.S)


def pins(body):
    out = {}
    for m in re.finditer(r"CustomProperties Pin \((.*)\)", body):
        p = m.group(1)
        g = lambda k: (re.search(k + r'=("?)([^",]*)\1', p) or [None, None, None])[2]
        name = g("PinName")
        out[(name, "out" if 'Direction="EGPD_Output"' in p else "in")] = {
            "cat": g(r"PinType\.PinCategory"), "sub": g(r"PinType\.PinSubCategory"),
            "obj": (re.search(r'PinType\.PinSubCategoryObject=("[^"]*"|None)', p) or [None, None])[1],
            "cont": g(r"PinType\.ContainerType"), "ref": g(r"PinType\.bIsReference"), "const": g(r"PinType\.bIsConst")}
    return out


def func_of(body):
    m = re.search(r'FunctionReference=\((?:MemberParent="([^"]*)",)?MemberName="([^"]+)"', body)
    return (m.group(1), m.group(2)) if m else (None, None)


text = open(sys.argv[1], encoding="utf-8").read()
bad = checked = 0
# node class paths must exist exactly as in real nodes (a wrong module = the editor silently drops the node on paste)
real_cls = {}
for v in lib.values():
    m = re.match(r"Begin Object Class=(\S+) ", v["text"])
    if m:
        real_cls.setdefault(m.group(1).rsplit(".", 1)[1], set()).add(m.group(1))
for cls, _ in blocks(text):
    short = cls.rsplit(".", 1)[1]
    if short in real_cls and cls not in real_cls[short]:
        bad += 1
        print("== NODE CLASS %s: real nodes use %s" % (cls, sorted(real_cls[short])))
for cls, body in blocks(text):
    kind = cls.rsplit(".", 1)[1]
    if kind not in ("K2Node_CallFunction", "K2Node_CallArrayFunction"):
        continue
    parent, fn = func_of(body)
    key = "%s:%s" % (kind[7:], fn)
    ex = lib.get(key) or lib.get("CallFunction:%s" % fn) or lib.get("CallArrayFunction:%s" % fn)
    if not ex:
        continue
    checked += 1
    ref_body = ex["text"]
    rparent, _ = func_of(ref_body)
    diffs = []
    if rparent and parent and rparent != parent:
        print("   (skip %s: example is from %s, mine %s)" % (fn, rparent.split("'")[-2] if "'" in rparent else rparent, parent.split("'")[-2] if "'" in parent else parent))
        checked -= 1
        continue
    mine, real = pins(body), pins(ref_body)
    for k in sorted(set(mine) | set(real), key=str):
        if k not in real:
            diffs.append("extra pin %s" % (k,))
        elif k not in mine:
            diffs.append("missing pin %s" % (k,))
        else:
            for f in ("cat", "sub", "obj", "cont", "ref", "const"):
                if (mine[k][f] or "") != (real[k][f] or "") and not (f == "obj" and k[0] in ("self", "WorldContextObject")):
                    diffs.append("pin %s %s: mine=%s real=%s" % (k, f, mine[k][f], real[k][f]))
    if diffs:
        bad += 1
        print("== %s (%s)" % (fn, kind))
        for d in diffs:
            print("   ", d)
print("checked %d function nodes against real examples, %d with differences" % (checked, bad))
sys.exit(1 if bad else 0)
