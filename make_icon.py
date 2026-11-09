"""Generates assets/icon.png (and icon_data.py for the window icon). Run: python make_icon.py"""
import base64, io
from PIL import Image, ImageDraw

def draw(size):
    s = size * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.22), fill=(37, 99, 235, 255))
    w = s * 0.12
    cx = s / 2
    d.rectangle([cx - w / 2, s * 0.17, cx + w / 2, s * 0.55], fill="white")
    d.polygon([(s * 0.27, s * 0.48), (s * 0.73, s * 0.48), (cx, s * 0.72)], fill="white")
    d.rounded_rectangle([s * 0.22, s * 0.78, s * 0.78, s * 0.85], radius=int(s * 0.035), fill="white")
    return img.resize((size, size), Image.LANCZOS)

draw(512).save("assets/icon.png")
draw(512).save("android/icon.png")
buf = io.BytesIO()
draw(64).save(buf, "PNG")
open("icon_data.py", "w").write('ICON_PNG_B64 = "%s"\n' % base64.b64encode(buf.getvalue()).decode())
print("icon done")
