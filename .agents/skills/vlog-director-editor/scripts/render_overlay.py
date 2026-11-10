"""Render an HTML overlay composition to a transparent MOV.

The HTML page must define:
  window.init(comp)  async setup, receives the composition object
  window.seek(t)     draw the frame for time t in seconds

The composition JSON needs format {w, h, fps, dur} and may set hold_fps, which
reuses frames between animation steps for stop-motion styles.

Usage:
  python render_overlay.py --comp comp.json --html overlay.html --fonts <dir> --out overlay.mov
Requires: playwright (uses the installed Chrome) and ffmpeg.
"""
import argparse
import json
import math
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright


def render(comp_path, html_path, fonts_dir, out_path):
    comp = json.loads(Path(comp_path).read_text(encoding="utf-8"))
    comp["fonts_uri"] = Path(fonts_dir).resolve().as_uri()
    fmt = comp["format"]
    total = round(fmt["dur"] * fmt["fps"])
    hold = comp.get("hold_fps")

    encoder = subprocess.Popen(
        ["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-framerate", str(fmt["fps"]),
         "-c:v", "png", "-i", "pipe:0", "-c:v", "qtrle", "-pix_fmt", "argb", str(out_path)],
        stdin=subprocess.PIPE)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True, args=["--force-color-profile=srgb"])
        page = browser.new_page(viewport={"width": fmt["w"], "height": fmt["h"]})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(Path(html_path).resolve().as_uri())
        page.evaluate("c => window.init(c)", comp)

        last_key, png = None, None
        for n in range(total):
            t = n / fmt["fps"]
            key = math.floor(t * hold + 1e-6) if hold else n
            if key != last_key:
                page.evaluate("t => window.seek(t)", t)
                png = page.screenshot(omit_background=True, type="png")
                last_key = key
            encoder.stdin.write(png)
        browser.close()

    encoder.stdin.close()
    if encoder.wait() != 0:
        raise SystemExit("ffmpeg failed to encode overlay")
    if errors:
        raise SystemExit(f"page errors: {errors}")
    print(f"overlay written: {out_path} ({total} frames)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--comp", required=True)
    ap.add_argument("--html", required=True)
    ap.add_argument("--fonts", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    render(a.comp, a.html, a.fonts, a.out)


if __name__ == "__main__":
    main()
