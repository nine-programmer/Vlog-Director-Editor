"""Step 2: build the interactive style-selection page from real project footage.

Write 03_Style/preview_moments.json first (3-7 short moments picked from the scan):
[
  {"id": "funny1", "name_th": "ตลก: ชื่อเหตุการณ์", "src": "CLIP_0003.MP4", "start": 17.5, "dur": 6,
   "label": "ภารกิจวันนี้",
   "speech":  {"t": 1.2, "end": 3.9, "text": "คำพูดจริงในคลิป"},
   "impact":  {"t": 1.3, "end": 3.5, "words": ["โดน", "แล้ว!"]},
   "comment": {"t": 4.0, "end": 5.8, "text": "คอมเมนต์แซวจากคนตัด"}}
]
Times inside a moment are relative to its start. speech, impact, comment and label are optional.

Output: 03_Style/preview/index.html (open in Chrome). It uses the same engine and style
files as the renderer, so what the user picks is what gets rendered.

Usage:
  python make_style_preview.py --root <project>
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
STYLES_DIR = SKILL / "assets" / "styles"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--moments", type=Path, help="default: <root>/03_Style/preview_moments.json")
    a = ap.parse_args()

    root = a.root.resolve()
    moments = json.loads((a.moments or root / "03_Style" / "preview_moments.json").read_text(encoding="utf-8"))
    raw = {p.name: p for p in (root / "01_Raw_Footage").rglob("*") if p.is_file()}
    out = root / "03_Style" / "preview"
    (out / "clips").mkdir(parents=True, exist_ok=True)

    for m in moments:
        if m["src"] not in raw:
            sys.exit(f"missing source clip: {m['src']}")
        clip = out / "clips" / f"{m['id']}.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(m["start"]), "-t", str(m["dur"]), "-i", str(raw[m["src"]]),
                        "-map", "0:v:0", "-map", "0:a:0?", "-vf", "scale=960:-2", "-r", "30", "-c:v", "libx264", "-crf", "23",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(clip)], check=True)
        m["src"] = f"clips/{m['id']}.mp4"

    for js in STYLES_DIR.glob("*.js"):
        shutil.copy2(js, out / js.name)
    manifest = json.loads((STYLES_DIR / "styles.json").read_text(encoding="utf-8"))
    styles = [s for s in manifest["styles"] if (STYLES_DIR / f"{s}.js").exists()]
    page = (SKILL / "assets" / "style_preview" / "index.html").read_text(encoding="utf-8")
    page = page.replace("<!--STYLE_SCRIPTS-->", "\n".join(f'<script src="{s}.js"></script>' for s in styles))
    (out / "index.html").write_text(page, encoding="utf-8")
    data = {"fonts_uri": "../../05_Shared_Assets/fonts", "manifest": manifest, "moments": moments}
    (out / "preview_data.js").write_text("window.PREVIEW = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(f"style preview: {out / 'index.html'} ({len(styles)} styles, {len(moments)} moments)")


if __name__ == "__main__":
    main()
