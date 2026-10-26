"""Read UFunction flags (pure/const/callable) and parameter names straight from an UnrealEditor-*.dll (plain Python).

  python -I ufunc_flags.py <dll> FuncName [FuncName ...]

How: UHT emits FFunctionParams { OuterFunc*, SuperFunc*, const char* NameUTF8, PropertyArray*, uint16 NumProperties,
uint16 StructureSize, uint32 ObjectFlags, uint32 FunctionFlags, ... }. We find the ASCII name, compute its virtual address,
find 8-byte pointers to it, and read the struct around each hit. Params: PropertyArray -> FPropertyParamsBase* -> NameUTF8 (first field).
Several hits = same-named functions in different classes (owner is not resolved; compare param lists).
"""
import struct, sys

FLAGS = {0x00000001: "Final", 0x00000400: "Native", 0x00002000: "Static", 0x00400000: "HasOutParms",
         0x04000000: "BlueprintCallable", 0x08000000: "BlueprintEvent", 0x10000000: "BlueprintPure",
         0x40000000: "Const", 0x00020000: "Public"}


def pe_sections(data):
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, pe + 6)[0]
    optsz = struct.unpack_from("<H", data, pe + 20)[0]
    image_base = struct.unpack_from("<Q", data, pe + 24 + 24)[0]
    secs = []
    off = pe + 24 + optsz
    for i in range(nsec):
        name, vsize, va, rawsize, rawptr = struct.unpack_from("<8sIIII", data, off + 40 * i)
        secs.append((name.rstrip(b"\0").decode(), va, vsize, rawptr, rawsize))
    return image_base, secs


def off2va(off, ib, secs):
    for _, va, vs, rp, rs in secs:
        if rp <= off < rp + rs:
            return ib + va + (off - rp)


def va2off(v, ib, secs):
    r = v - ib
    for _, va, vs, rp, rs in secs:
        if va <= r < va + max(vs, rs):
            return rp + (r - va)


def cstr(data, off):
    e = data.find(b"\0", off)
    return data[off:e].decode("ascii", "replace")


def lookup(data, name, ib, secs):
    out = []
    needle = name.encode() + b"\0"
    pos = 0
    while True:
        i = data.find(needle, pos)
        if i < 0:
            break
        pos = i + 1
        if i > 0 and data[i - 1] != 0:
            continue
        va = off2va(i, ib, secs)
        if not va:
            continue
        p = struct.pack("<Q", va)
        j = 0
        while True:
            k = data.find(p, j)
            if k < 0:
                break
            j = k + 1
            try:
                base = k - 16
                outer, sup, nameptr, proparr = struct.unpack_from("<QQQQ", data, base)
                nprops, ssize, oflags, fflags = struct.unpack_from("<HHII", data, base + 32)
            except struct.error:
                continue
            if nameptr != va or nprops > 64:
                continue
            params = []
            po = va2off(proparr, ib, secs) if proparr else None
            for n in range(nprops if po else 0):
                pp = struct.unpack_from("<Q", data, po + 8 * n)[0]
                ppo = va2off(pp, ib, secs)
                if ppo is None:
                    break
                pn = struct.unpack_from("<Q", data, ppo)[0]
                pno = va2off(pn, ib, secs)
                params.append(cstr(data, pno) if pno else "?")
            out.append({"flags": hex(fflags), "flag_names": [v for k2, v in FLAGS.items() if fflags & k2],
                        "pure": bool(fflags & 0x10000000), "params": params})
    return out


if __name__ == "__main__":
    data = open(sys.argv[1], "rb").read()
    ib, secs = pe_sections(data)
    for fn in sys.argv[2:]:
        print(fn, lookup(data, fn, ib, secs))
