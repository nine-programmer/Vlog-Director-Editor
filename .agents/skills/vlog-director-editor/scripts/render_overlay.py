"""Render an overlay composition to a transparent MOV with the shared style engine.

The page assets/styles/render.html loads engine.js; this script adds the style file
named by comp["style"], calls window.init(comp) and window.seek(t) per frame, and
saves window.layout() next to the output as <out>.layout.json for QA.

Usage:
  python render_overlay.py --comp comp.json --fonts <dir> --out overlay.mov
Requires: playwright (drives the installed Chrome) and ffmpeg.
"""
import argparse
import json
import math
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright

STYLES_DIR = Path(__file__).resolve().parent.parent / "assets" / "styles"


def render(comp_path, fonts_dir, out_path):
    comp = json.loads(Path(comp_path).read_text(encoding="utf-8"))
    comp["fonts_uri"] = Path(fonts_dir).resolve().as_uri()
    style_js = STYLES_DIR / f"{comp.get('style', 'scrapbook')}.js"
    if not style_js.exists():
        raise SystemExit(f"unknown style file: {style_js}")
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
        page.goto((STYLES_DIR / "render.html").as_uri())
        page.add_script_tag(path=str(style_js))
        page.evaluate("c => window.init(c)", comp)
        Path(str(out_path) + ".layout.json").write_text(
            json.dumps(page.evaluate("() => window.layout()"), ensure_ascii=False), encoding="utf-8")

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
    ap.add_argument("--fonts", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    render(a.comp, a.fonts, a.out)


if __name__ == "__main__":
    main()
