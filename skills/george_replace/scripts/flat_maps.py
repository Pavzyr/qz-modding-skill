"""Neutral maps for a GLB that only has a base colour: flat normal (128,128,255) and RoughMetal (R 255, G=roughness, B=0).
  python -I flat_maps.py <textures_dir> [prefix=T_MyChar] [roughness=0.7]"""
import os, sys
from PIL import Image

out = sys.argv[1]
prefix = sys.argv[2] if len(sys.argv) > 2 else "T_MyChar"
rough = float(sys.argv[3]) if len(sys.argv) > 3 else 0.7
os.makedirs(out, exist_ok=True)
Image.new("RGB", (256, 256), (128, 128, 255)).save(os.path.join(out, prefix + "_Normal.jpg"), quality=100)
Image.new("RGB", (256, 256), (255, int(round(rough * 255)), 0)).save(os.path.join(out, prefix + "_RoughMetal.jpg"), quality=100)
print("written", prefix + "_Normal.jpg", prefix + "_RoughMetal.jpg", "roughness", rough)
