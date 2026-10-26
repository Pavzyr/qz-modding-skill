"""List file paths stored in an IoStore .utoc directory index (unencrypted).
Usage: python -I utoc_list.py <file.utoc> [...]"""
import struct, sys


def read_fstring(d, p):
    n, = struct.unpack_from('<i', d, p); p += 4
    if n == 0:
        return '', p
    if n > 0:
        s = d[p:p + n - 1].decode('latin-1'); p += n
    else:
        n = -n
        s = d[p:p + 2 * (n - 1)].decode('utf-16le'); p += 2 * n
    return s, p


def list_utoc(path):
    d = open(path, 'rb').read()
    mp = d.find(b'../../../')
    if mp < 0:
        raise SystemExit(f'{path}: no mount point found (encrypted index?)')
    p = mp - 4
    mount, p = read_fstring(d, p)
    nd, = struct.unpack_from('<I', d, p); p += 4
    dirs = [struct.unpack_from('<4I', d, p + 16 * i) for i in range(nd)]; p += 16 * nd
    nf, = struct.unpack_from('<I', d, p); p += 4
    files = [struct.unpack_from('<3I', d, p + 12 * i) for i in range(nf)]; p += 12 * nf
    ns, = struct.unpack_from('<I', d, p); p += 4
    strings = []
    for _ in range(ns):
        s, p = read_fstring(d, p); strings.append(s)
    NONE = 0xFFFFFFFF
    out = []

    def walk(di, prefix):
        name, child, sib, ffile = dirs[di]
        here = prefix + (strings[name] + '/' if name != NONE else '')
        f = ffile
        while f != NONE:
            out.append(here + strings[files[f][0]])
            f = files[f][1]
        c = child
        while c != NONE:
            walk(c, here)
            c = dirs[c][2]

    walk(0, '')
    return mount, sorted(out)


if __name__ == '__main__':
    for path in sys.argv[1:]:
        mount, out = list_utoc(path)
        print(f'### {path}\nmount: {mount}  files: {len(out)}')
        for o in out:
            print(o)
