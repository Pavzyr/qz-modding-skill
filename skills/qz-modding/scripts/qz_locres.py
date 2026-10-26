"""Read / write Unreal .locres and .locmeta (plain Python, no engine).
  python -I qz_locres.py dump <Game.locres> [namespace] [key-regex]          -> entries (ns, key, source_hash, text)
  python -I qz_locres.py build <overrides.json> <out_dir> <Target>          -> <out_dir>/<Target>.locmeta + <culture>/<Target>.locres
overrides.json: {"native": "en", "game_loc_dir": ".../Content/Localization/Game",
                 "entries": [{"ns": "ST_Quests", "key": "01_Chapter_0001_Major", "text": {"ru": "...", "en": "..."}}]}
The source-string hash of every entry is copied from the game's own <culture>/Game.locres (a wrong hash = the engine ignores
the translation). Written locres = version 1 (Compact): no key hashing needed, still loaded by UE 5.x.
"""
import json, os, re, struct, sys

LOCRES_MAGIC = struct.pack("<4I", 0x7574140E, 0xFC034A67, 0x9D90154A, 0x1B7F37C3)
LOCMETA_MAGIC = struct.pack("<4I", 0xA14CEE4F, 0x83554868, 0xBD464C6C, 0x7C50DA70)


class R:
    def __init__(self, b):
        self.b, self.p = b, 0

    def u8(self):
        v = self.b[self.p]; self.p += 1; return v

    def u32(self):
        v = struct.unpack_from("<I", self.b, self.p)[0]; self.p += 4; return v

    def i32(self):
        v = struct.unpack_from("<i", self.b, self.p)[0]; self.p += 4; return v

    def i64(self):
        v = struct.unpack_from("<q", self.b, self.p)[0]; self.p += 8; return v

    def fstr(self):
        n = self.i32()
        if n == 0:
            return ""
        if n < 0:
            s = self.b[self.p:self.p - 2 * n].decode("utf-16-le"); self.p += -2 * n
        else:
            s = self.b[self.p:self.p + n].decode("latin-1"); self.p += n
        return s.rstrip("\x00")


def read_locres(path):
    b = open(path, "rb").read()
    r = R(b)
    ver = 0
    if b[:16] == LOCRES_MAGIC:
        r.p = 16
        ver = r.u8()
    strings = None
    if ver >= 1:
        off = r.i64()
        save = r.p
        r.p = off
        cnt = r.i32()
        strings = []
        for _ in range(cnt):
            strings.append(r.fstr())
            if ver >= 2:
                r.i32()
        r.p = save
    if ver >= 2:
        r.u32()
    out = []
    for _ in range(r.u32()):
        if ver >= 2:
            r.u32()
        ns = r.fstr()
        for _ in range(r.u32()):
            if ver >= 2:
                r.u32()
            key = r.fstr()
            h = r.u32()
            text = strings[r.i32()] if ver >= 1 else r.fstr()
            out.append((ns, key, h, text))
    return ver, out


def fstr_w(s):
    if s == "":
        return struct.pack("<i", 0)
    data = (s + "\x00").encode("utf-16-le")
    return struct.pack("<i", -(len(data) // 2)) + data


def write_locres(path, entries):
    """entries: list of (ns, key, source_hash, text) -> version 1 (Compact)."""
    by_ns = {}
    for ns, key, h, text in entries:
        by_ns.setdefault(ns, []).append((key, h, text))
    strings, idx = [], {}
    body = b""
    body += struct.pack("<I", len(by_ns))
    for ns, keys in by_ns.items():
        body += fstr_w(ns) + struct.pack("<I", len(keys))
        for key, h, text in keys:
            if text not in idx:
                idx[text] = len(strings); strings.append(text)
            body += fstr_w(key) + struct.pack("<Ii", h, idx[text])
    head_len = 16 + 1 + 8
    off = head_len + len(body)
    tail = struct.pack("<i", len(strings)) + b"".join(fstr_w(s) for s in strings)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "wb").write(LOCRES_MAGIC + bytes([1]) + struct.pack("<q", off) + body + tail)


def write_locmeta(path, native, target, cultures):
    # version 2 (as written by UE 5.7 for the game's own Game.locmeta): + trailing uint32 flag (0 in the game's file)
    data = LOCMETA_MAGIC + bytes([2]) + fstr_w(native) + fstr_w("%s/%s.locres" % (native, target))
    data += struct.pack("<i", len(cultures)) + b"".join(fstr_w(c) for c in cultures) + struct.pack("<I", 0)
    open(path, "wb").write(data)


def main():
    cmd = sys.argv[1]
    sys.stdout.reconfigure(encoding="utf-8")
    if cmd == "dump":
        ver, ents = read_locres(sys.argv[2])
        ns = sys.argv[3] if len(sys.argv) > 3 else None
        pat = re.compile(sys.argv[4]) if len(sys.argv) > 4 else None
        print("version", ver, "entries", len(ents))
        for e in ents:
            if (ns is None or e[0] == ns) and (pat is None or pat.search(e[1])):
                print("%s | %s | %08x | %s" % e)
    elif cmd == "build":
        cfg = json.load(open(sys.argv[2], encoding="utf-8"))
        out_dir, target = sys.argv[3], sys.argv[4]
        cultures = sorted({c for e in cfg["entries"] for c in e["text"]})
        game = {}
        for c in cultures:
            _, ents = read_locres(os.path.join(cfg["game_loc_dir"], c, "Game.locres"))
            game[c] = {(ns, k): (h, t) for ns, k, h, t in ents}
        for c in cultures:
            rows = []
            for e in cfg["entries"]:
                if c not in e["text"]:
                    continue
                h, old = game[c][(e["ns"], e["key"])]
                rows.append((e["ns"], e["key"], h, e["text"][c]))
                print("%s %s/%s hash %08x: %r -> %r" % (c, e["ns"], e["key"], h, old[:60], e["text"][c][:60]))
            write_locres(os.path.join(out_dir, c, target + ".locres"), rows)
        write_locmeta(os.path.join(out_dir, target + ".locmeta"), cfg.get("native", "en"), target, cultures)
        # self-check
        for c in cultures:
            ver, ents = read_locres(os.path.join(out_dir, c, target + ".locres"))
            print("check", c, "v%d" % ver, ents)


if __name__ == "__main__":
    main()
