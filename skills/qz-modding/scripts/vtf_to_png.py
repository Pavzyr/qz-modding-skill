# Source engine .vtf -> .png (uncompressed BGRA8888/BGR888/RGBA8888 only; single frame/face). 2026-10-21.
# python -I vtf_to_png.py in.vtf out.png [max_size]   -- the largest mip is stored LAST in the file; alpha kept.
import struct
import sys

import numpy as np
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
mx = int(sys.argv[3]) if len(sys.argv) > 3 else 0
b = open(src, "rb").read()
assert b[:4] == b"VTF\x00", "not a VTF"
w, h, flags, frames = struct.unpack("<HHIH", b[16:26])
fmt = struct.unpack("<i", b[52:56])[0]
bpp, order = {0: (4, "RGBA"), 2: (3, "RGB"), 3: (3, "BGR"), 12: (4, "BGRA"), 16: (4, "BGRX")}[fmt]
assert frames == 1, "animated VTF not supported"
px = np.frombuffer(b[len(b) - w * h * bpp:], np.uint8).reshape(h, w, bpp)
idx = [order.index(c) for c in ("RGBA" if "A" in order else "RGB")]
img = Image.fromarray(px[:, :, idx].copy(), "RGBA" if "A" in order else "RGB")
if mx and max(w, h) > mx:
    img = img.resize((min(w, mx), min(h, mx)), Image.LANCZOS)
img.save(dst)
print("vtf", src, w, h, order, "->", dst, img.size)
