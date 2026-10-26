# Pure-python (numpy) skin-weight comparison of two .glb files (no Blender/UE). Run: python -I glb_skin_compare.py A.glb B.glb [out.json]
# Per file: vertex count, influences/vertex, weight sums, unweighted verts, joints (names), inverse bind matrices.
# A vs B: vertices matched by position (1e-4 m); per matched vertex compare {bone: weight}; worst bones by error; bind-matrix diff per bone.
import json
import struct
import sys

import numpy as np

CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def load(fn):
    b = open(fn, "rb").read()
    assert b[:4] == b"glTF"
    jl = struct.unpack_from("<I", b, 12)[0]
    g = json.loads(b[20:20 + jl])
    bin_ = b[20 + jl + 8:]
    return g, bin_


def acc(g, bin_, i):
    a = g["accessors"][i]
    bv = g["bufferViews"][a["bufferView"]]
    dt = np.dtype(CT[a["componentType"]])
    n = NC[a["type"]]
    off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = bv.get("byteStride", dt.itemsize * n)
    raw = np.frombuffer(bin_, np.uint8, count=stride * (a["count"] - 1) + dt.itemsize * n, offset=off)
    arr = np.lib.stride_tricks.as_strided(raw, shape=(a["count"], dt.itemsize * n), strides=(stride, 1)).copy()
    out = arr.view(dt).reshape(a["count"], n).astype(np.float64)
    if a.get("normalized"):
        out /= np.iinfo(dt).max
    return out


def info(fn):
    g, bin_ = load(fn)
    sk = g["skins"][0]
    jn = [g["nodes"][j].get("name", str(j)) for j in sk["joints"]]
    ibm = acc(g, bin_, sk["inverseBindMatrices"]).reshape(-1, 4, 4) if "inverseBindMatrices" in sk else None
    P, W = [], []
    meshes = [n for n in g["nodes"] if "mesh" in n and "skin" in n]
    prims = []
    for nd in meshes:
        for pr in g["meshes"][nd["mesh"]]["primitives"]:
            at = pr["attributes"]
            pos = acc(g, bin_, at["POSITION"])
            sets = sorted(k for k in at if k.startswith("JOINTS_"))
            w = [dict() for _ in range(len(pos))]
            for s in sets:
                J = acc(g, bin_, at[s]).astype(int)
                Wt = acc(g, bin_, at["WEIGHTS_" + s[7:]])
                for v in range(len(pos)):
                    for k in range(4):
                        if Wt[v, k] > 0:
                            nm = jn[J[v, k]]
                            w[v][nm] = w[v].get(nm, 0) + Wt[v, k]
            prims.append({"verts": len(pos), "joint_sets": len(sets), "material": pr.get("material")})
            P.append(pos)
            W += w
    P = np.concatenate(P)
    sums = np.array([sum(x.values()) for x in W])
    ninf = np.array([len(x) for x in W])
    return {"file": fn, "nodes_with_skin": len(meshes), "prims": prims, "verts": len(P), "joints": len(jn),
            "max_influences": int(ninf.max()), "infl_hist": {int(k): int(v) for k, v in zip(*np.unique(ninf, return_counts=True))},
            "unweighted": int((sums < 1e-6).sum()), "sum_min": float(sums.min()), "sum_max": float(sums.max()),
            "mesh_node_transform": [{k: nd.get(k) for k in ("translation", "rotation", "scale", "matrix") if k in nd} for nd in meshes]
            }, P, W, dict(zip(jn, ibm)) if ibm is not None else {}


A, PA, WA, IA = info(sys.argv[1])
B, PB, WB, IB = info(sys.argv[2])
R = {"A": A, "B": B}
R["joints_only_A"] = sorted(set(IA) - set(IB))[:50]
R["joints_only_B"] = sorted(set(IB) - set(IA))[:50]
R["ibm_diff_top"] = sorted(([n, float(np.abs(IA[n] - IB[n]).max())] for n in set(IA) & set(IB)), key=lambda x: -x[1])[:15]
# match B vertices to A by position
key = lambda p: tuple(np.round(p / 1e-4).astype(np.int64))
ia = {}
for i, p in enumerate(PA):
    ia.setdefault(key(p), i)
matched, err_bone, bad = 0, {}, []
for j, p in enumerate(PB):
    i = ia.get(key(p))
    if i is None:
        continue
    matched += 1
    wa, wb = WA[i], WB[j]
    e = 0.0
    for n in set(wa) | set(wb):
        d = abs(wa.get(n, 0) - wb.get(n, 0))
        e += d
        if d > 0.05:
            err_bone[n] = err_bone.get(n, 0) + 1
    if e > 0.2:
        bad.append([j, round(e, 3), [round(x, 4) for x in p],
                    sorted(((k, round(v, 3)) for k, v in wa.items()), key=lambda x: -x[1])[:6],
                    sorted(((k, round(v, 3)) for k, v in wb.items()), key=lambda x: -x[1])[:6]])
R["matched_B_in_A"] = matched
R["bad_verts"] = len(bad)
R["bad_bones_top"] = sorted(err_bone.items(), key=lambda x: -x[1])[:25]
R["bad_examples"] = bad[:8]
out = json.dumps(R, ensure_ascii=False, indent=1)
if len(sys.argv) > 3:
    open(sys.argv[3], "w", encoding="utf-8").write(out)
print(out[:6000])
