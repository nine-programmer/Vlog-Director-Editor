"""Step 0: set up a project folder so the skill works with nothing but the skill installed.

Creates the standard folders, the context files (AGENTS.md, CLAUDE.md, .gitignore,
.env.example), starter documents, the fonts every style needs and the synth SFX kit.
Existing files are never overwritten.

Usage:
  python init_project.py --root <project> [--no-download]
"""
import argparse
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL / "assets" / "project_template"
FOLDERS = ["_temp", "00_Project", "01_Raw_Footage", "02_Scan_Reports", "03_Style", "04_Episodes",
           "05_Shared_Assets/fonts", "05_Shared_Assets/sfx", "06_Master", "07_Delivery"]
CONTEXT = {"AGENTS.md": "AGENTS.md", "CLAUDE.md": "CLAUDE.md", ".gitignore": "gitignore.txt", ".env.example": "env.example.txt"}
STARTERS = {
    "00_Project/Brief.md": "# Brief\n\n- แนววิดีโอ:\n- รูปแบบ: แนวตั้ง / แนวนอน\n- ตัวละคร:\n- ผู้พากย์และหางเสียง:\n- คลิปตัวอย่างที่ชอบ:\n",
    "00_Project/Status.md": "# สถานะทุกตอน\n\n| ตอน | ชื่อ | รูปแบบ | สถานะ | ไฟล์ที่ผ่าน |\n|---|---|---|---|---|\n\nMaster: ยังไม่รวม\n",
}
FONT_REPO = "https://raw.githubusercontent.com/google/fonts/main/"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--no-download", action="store_true", help="skip font downloads")
    a = ap.parse_args()
    root = a.root.resolve()
    created, kept = [], []

    for f in FOLDERS:
        (root / f).mkdir(parents=True, exist_ok=True)
    for name, src in {**CONTEXT}.items():
        dst = root / name
        if dst.exists():
            kept.append(name)
        else:
            shutil.copy2(TEMPLATE / src, dst)
            created.append(name)
    for name, text in STARTERS.items():
        dst = root / name
        if dst.exists():
            kept.append(name)
        else:
            dst.write_text(text, encoding="utf-8")
            created.append(name)

    fonts_dir = root / "05_Shared_Assets" / "fonts"
    import json
    manifest = json.loads((SKILL / "assets" / "styles" / "styles.json").read_text(encoding="utf-8"))
    failed = []
    if not a.no_download:
        for file, path in manifest["font_sources"].items():
            dst = fonts_dir / file
            if dst.exists():
                continue
            try:
                urllib.request.urlretrieve(FONT_REPO + path.replace("[", "%5B").replace("]", "%5D"), dst)
                created.append(f"fonts/{file}")
            except Exception as e:
                failed.append(f"{file}: {e}")
        sources = fonts_dir / "SOURCES.md"
        if not sources.exists():
            sources.write_text("# Fonts\n\nDownloaded by init_project.py from https://github.com/google/fonts "
                               "(SIL Open Font License 1.1).\n", encoding="utf-8")

    synth = root / "05_Shared_Assets" / "sfx" / "synth"
    if not (synth / "SOURCES.md").exists():
        subprocess.run([sys.executable, str(SKILL / "scripts" / "sfx_kit.py"), "--root", str(root)], check=True)
        created.append("sfx/synth")

    print(f"project ready: {root}")
    print("created: " + (", ".join(created) or "nothing new"))
    if kept:
        print("kept existing: " + ", ".join(kept))
    if failed:
        print("font downloads failed (retry later or copy fonts manually):\n  " + "\n  ".join(failed))
    print("next: copy the chosen clips into 01_Raw_Footage/, then run check_env.py and scan_footage.py")


if __name__ == "__main__":
    main()
