"""Print/compare the node hierarchy (Models + OO connections) of binary FBX files. Plain Python, read-only.
  python -I fbx_tree.py a.fbx [b.fbx]      -> tree of a; with b: differences in parent links / missing nodes
Used to debug UE "Failed to merge bones" (extra/inserted nodes, renamed bones)."""
import struct, sys, zlib


def read_props(d, p, n):
    props = []
    for _ in range(n):
        t = chr(d[p]); p += 1
        if t == "Y":
            props.append(struct.unpack_from("<h", d, p)[0]); p += 2
        elif t == "C":
            props.append(d[p] != 0); p += 1
        elif t == "I":
            props.append(struct.unpack_from("<i", d, p)[0]); p += 4
        elif t == "F":
            props.append(struct.unpack_from("<f", d, p)[0]); p += 4
        elif t == "D":
            props.append(struct.unpack_from("<d", d, p)[0]); p += 8
        elif t == "L":
            props.append(struct.unpack_from("<q", d, p)[0]); p += 8
        elif t in "fdlibc":
            ln, enc, clen = struct.unpack_from("<III", d, p); p += 12
            props.append(("arr", t, ln)); p += clen
        elif t in "SR":
            ln = struct.unpack_from("<I", d, p)[0]; p += 4
            props.append(d[p:p + ln]); p += ln
        else:
            raise ValueError("prop type %r at %d" % (t, p))
    return props, p


def parse(d, p, end, big, out):
    hdr = 25 if big else 13
    while p < end:
        if big:
            eo, np_, pl = struct.unpack_from("<QQQ", d, p); p2 = p + 24
        else:
            eo, np_, pl = struct.unpack_from("<III", d, p); p2 = p + 12
        if eo == 0:
            break
        nl = d[p2]; name = d[p2 + 1:p2 + 1 + nl].decode("latin1")
        pp = p2 + 1 + nl
        props, pe = read_props(d, pp, np_)
        children = []
        if pe < eo:
            parse(d, pe, eo - hdr, big, children)
        out.append((name, props, children))
        p = eo
    return out


def load(fn):
    d = open(fn, "rb").read()
    ver = struct.unpack_from("<I", d, 23)[0]
    top = parse(d, 27, len(d), ver >= 7500, [])
    models, links = {}, []
    for name, props, ch in top:
        if name == "Objects":
            for n, pr, c in ch:
                if n == "Model":
                    nm = pr[1].split(b"\x00\x01")[0].decode("latin1")
                    models[pr[0]] = (nm, pr[2].decode("latin1"))
        if name == "Connections":
            for n, pr, c in ch:
                if n == "C" and pr[0] == b"OO":
                    links.append((pr[1], pr[2]))
    parent = {}
    for c, par in links:   # a bone also links to Pose/Deformer objects: keep only Model->Model or Model->scene(0)
        if c in models and (par in models or par == 0):
            parent[models[c][0]] = models[par][0] if par in models else "<scene>"
    types = {v[0]: v[1] for v in models.values()}
    return parent, types


def tree(parent, types):
    kids = {}
    for c, p in parent.items():
        kids.setdefault(p, []).append(c)
    lines = []

    def rec(n, depth):
        for k in sorted(kids.get(n, [])):
            lines.append("  " * depth + "%s [%s]" % (k, types.get(k, "?")))
            rec(k, depth + 1)
    rec("<scene>", 0)
    return lines


if __name__ == "__main__":
    pa, ta = load(sys.argv[1])
    if len(sys.argv) == 2:
        print("\n".join(tree(pa, ta)))
    else:
        pb, tb = load(sys.argv[2])
        print("A top:", [k for k, v in pa.items() if v == "<scene>"], "| B top:", [k for k, v in pb.items() if v == "<scene>"])
        bones_a = {k for k, t in ta.items() if t == "LimbNode"}
        bones_b = {k for k, t in tb.items() if t == "LimbNode"}
        print("LimbNodes A=%d B=%d" % (len(bones_a), len(bones_b)))
        print("only in A:", sorted(bones_a - bones_b)[:40])
        print("only in B:", sorted(bones_b - bones_a)[:40])
        diff = [(k, pa.get(k), pb.get(k)) for k in sorted(bones_a & bones_b) if pa.get(k) != pb.get(k)]
        print("parent differs (bone, parent in A, parent in B):", diff[:40])
