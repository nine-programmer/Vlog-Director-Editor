"""Check that this machine can run every step of the skill.

Prints what is missing and how to install it. Never prints API key values.

Usage:
  python check_env.py [--root <project>]
"""
import argparse
import importlib
import shutil
import subprocess
import sys
from pathlib import Path

PACKAGES = [
    ("numpy", "numpy", True), ("scipy", "scipy", True), ("cv2", "opencv-python", True),
    ("PIL", "pillow", True), ("playwright", "playwright", True), ("faster_whisper", "faster-whisper", False),
]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path)
    a = ap.parse_args()
    rows, missing = [], 0

    def row(name, ok, detail, required=True):
        nonlocal missing
        if not ok and required:
            missing += 1
        rows.append(f"{'OK ' if ok else ('MISSING' if required else 'optional')} | {name} | {detail}")

    for mod, pip, req in PACKAGES:
        try:
            importlib.import_module(mod)
            row(pip, True, "installed", req)
        except ImportError:
            row(pip, False, f"pip install {pip}", req)

    ff = shutil.which("ffmpeg")
    row("ffmpeg", bool(ff), ff or "install ffmpeg (https://ffmpeg.org) and add it to PATH")
    if ff:
        nv = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=s=256x256:d=0.1", "-c:v", "h264_nvenc",
                             "-f", "null", "-"], capture_output=True).returncode == 0
        row("NVENC GPU encoding", nv, "available" if nv else "not available, renders fall back to libx264 (slower)", False)

    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            p.chromium.launch(channel="chrome", headless=True).close()
        row("Google Chrome (for graphics)", True, "launches headless")
    except Exception as e:
        row("Google Chrome (for graphics)", False, f"install Google Chrome ({str(e).splitlines()[0][:80]})")

    if a.root:
        root = a.root
        fonts = list((root / "05_Shared_Assets" / "fonts").glob("*.ttf"))
        row("fonts", bool(fonts), f"{len(fonts)} files" if fonts else "run init_project.py")
        sfx = list((root / "05_Shared_Assets" / "sfx").rglob("*.wav"))
        row("SFX", bool(sfx), f"{len(sfx)} files" if sfx else "run init_project.py")
        env = root / ".env"
        names = set()
        if env.is_file():
            for line in env.read_text(encoding="utf-8-sig").splitlines():
                k, sep, v = line.partition("=")
                if sep and v.strip() and not k.strip().startswith("#"):
                    names.add(k.strip())
        for key, use in (("OPENAI_API_KEY", "AI images"), ("GEMINI_API_KEY", "AI voice and music, only when the user asks")):
            row(key, key in names, f"set ({use})" if key in names else f"not set ({use})", False)

    print("\n".join(rows))
    print(f"\n{missing} required item(s) missing" if missing else "\nready")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
