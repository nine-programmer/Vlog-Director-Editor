"""Timestamped contact sheet of a clip section.

Transcripts tell you when words are spoken, not what is in the frame. Look at a sheet
before placing any cut that depends on an action (a jump, a reaction, a pan).

Labels are drawn with Pillow because ffmpeg drawtext can crash when fontconfig is missing.

Usage:
  python frames.py --root <project> --src DJI_0021.MP4 --start 11.5 --end 19.5 --every 0.4
  python frames.py --src path/to/video.mp4 --start 0 --end 60 --every 3 --out sheet.jpg
"""
import argparse
import io
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def grab(src, t, width):
    png = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(src), "-map", "0:v:0", "-frames:v", "1",
                          "-vf", f"scale={width}:-2", "-f", "image2pipe", "-c:v", "png", "pipe:1"],
                         capture_output=True).stdout
    return Image.open(io.BytesIO(png)).convert("RGB") if png else None


def sheet(src, start, end, every, out, width=360, cols=5):
    times, t = [], start
    while t <= end + 1e-6:
        times.append(round(t, 2))
        t += every
    frames = [(t, grab(src, t, width)) for t in times]
    frames = [(t, im) for t, im in frames if im]
    if not frames:
        sys.exit(f"no frames decoded from {src}")
    w, h = frames[0][1].size
    rows = (len(frames) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * (w + 4), rows * (h + 4)), "black")
    font = ImageFont.load_default(size=max(16, width // 14))
    for i, (t, im) in enumerate(frames):
        d = ImageDraw.Draw(im)
        label = f"{t:.1f}s"
        box = d.textbbox((8, 6), label, font=font)
        d.rectangle((box[0] - 4, box[1] - 3, box[2] + 4, box[3] + 3), fill=(0, 0, 0))
        d.text((8, 6), label, font=font, fill=(255, 220, 0))
        canvas.paste(im, ((i % cols) * (w + 4), (i // cols) * (h + 4)))
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=88)
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="video path, or a file name inside <root>/01_Raw_Footage")
    ap.add_argument("--root", type=Path)
    ap.add_argument("--start", type=float, default=0)
    ap.add_argument("--end", type=float, required=True)
    ap.add_argument("--every", type=float, default=0.5)
    ap.add_argument("--width", type=int, default=360)
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--out")
    a = ap.parse_args()

    src = Path(a.src)
    if not src.exists() and a.root:
        found = [p for p in (a.root / "01_Raw_Footage").rglob(a.src)]
        if not found:
            sys.exit(f"not found: {a.src}")
        src = found[0]
    out = a.out or (a.root or Path(".")) / "_temp" / "frames" / f"{src.stem}_{a.start:g}-{a.end:g}.jpg"
    print(f"sheet: {sheet(src, a.start, a.end, a.every, out, a.width, a.cols)}")


if __name__ == "__main__":
    main()
