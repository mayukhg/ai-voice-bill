#!/usr/bin/env bash
# Build black-background E2E slideshow MP4 from dark mockup screenshots.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 << PY
from pathlib import Path
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow", "-q"])
    from PIL import Image, ImageDraw, ImageFont

root = Path(r"""$ROOT""")
shots = root / "assets/screenshots"
tmp = root / "video/_frames"
out = root / "video/voicebill-e2e-demo.mp4"
tmp.mkdir(parents=True, exist_ok=True)

def fit_black(src, dest, size=(1920, 1080)):
    im = Image.open(src).convert("RGB")
    im.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (0, 0, 0))
    canvas.paste(im, ((size[0] - im.width) // 2, (size[1] - im.height) // 2))
    canvas.save(dest)

files = [
    "01-landing.png", "02-due-bills.png", "03-voice-reminders.png",
    "04-pay-initiate.png", "05-otp.png", "06-confirmed.png",
]
for i, f in enumerate(files, 1):
    src = shots / f
    if not src.exists():
        raise SystemExit(f"Missing {src}")
    fit_black(src, tmp / f"frame-{i:02d}.png")

canvas = Image.new("RGB", (1920, 1080), (0, 0, 0))
draw = ImageDraw.Draw(canvas)
try:
    font_lg = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 72)
    font_sm = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 28)
except Exception:
    font_lg = font_sm = ImageFont.load_default()
t1, t2 = "VoiceBill", "PM case study  ·  mockup + Flask API  ·  Alexa on roadmap"
b1 = draw.textbbox((0, 0), t1, font=font_lg)
b2 = draw.textbbox((0, 0), t2, font=font_sm)
draw.text(((1920 - (b1[2] - b1[0])) // 2, 440), t1, fill=(92, 255, 176), font=font_lg)
draw.text(((1920 - (b2[2] - b2[0])) // 2, 540), t2, fill=(255, 255, 255), font=font_sm)
canvas.save(tmp / "frame-07.png")
print("frames ready")
PY
ffmpeg -y -loglevel error \
  -framerate 1/3.5 \
  -i "$ROOT/video/_frames/frame-%02d.png" \
  -c:v libx264 -pix_fmt yuv420p -r 30 \
  "$ROOT/video/voicebill-e2e-demo.mp4"
rm -rf "$ROOT/video/_frames"
ls -lh "$ROOT/video/voicebill-e2e-demo.mp4"
echo "Wrote $ROOT/video/voicebill-e2e-demo.mp4"
