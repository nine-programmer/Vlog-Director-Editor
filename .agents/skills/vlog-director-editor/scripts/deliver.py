"""Step 8: copy an approved render to 07_Delivery with cover-frame candidates and an upload sheet.

Cover frames are taken from the episode's hero graphics (impact, stamp, score).
The upload sheet has empty title and description slots; the agent writes them in Thai.

Usage:
  python deliver.py --timeline 04_Episodes/EP01_Name/timeline.json [--render <file>]
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from render_episode import Episode

HERO = ("impact", "stamp", "score")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeline", required=True, type=Path)
    ap.add_argument("--render", type=Path, help="default: latest Full render of the episode")
    ap.add_argument("--covers", type=int, default=4)
    ap.add_argument("--out-dir", type=Path, help="default: <project>/07_Delivery")
    a = ap.parse_args()

    ep = Episode(a.timeline)
    code = ep.dir.name.split("_")[0]
    render = a.render or max((ep.dir / "renders").glob(f"{code}_Full_v*.mp4"), default=None)
    if not render:
        sys.exit("no Full render found")
    out_dir = a.out_dir or ep.root / "07_Delivery"
    out_dir.mkdir(exist_ok=True)
    video = out_dir / f"{ep.dir.name}.mp4"
    if video.exists():
        sys.exit(f"already delivered: {video} (rename or remove it first)")
    shutil.copy2(render, video)

    heroes = [g for g in ep.spec.get("graphics", []) if g["type"] in HERO]
    step = max(1, len(heroes) // a.covers) if heroes else 1
    times = [ep.at(g["t"]) + .5 for g in heroes[::step]][:a.covers] or [ep.duration / 2]
    covers = []
    for i, t in enumerate(times, 1):
        path = out_dir / f"{code}_cover_{i}.jpg"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", "-q:v", "2", str(path)], check=True)
        covers.append(path.name)

    sheet = out_dir / f"{code}_Upload.md"
    if not sheet.exists():
        sheet.write_text("\n".join([
            f"# {code}: ข้อมูลสำหรับอัปโหลด", "",
            f"- **ไฟล์:** `{video.name}` ({ep.fmt['w']}x{ep.fmt['h']}, {ep.duration:.1f} วินาที)",
            f"- **ภาพปก:** {', '.join(f'`{c}`' for c in covers)}", "",
            "## ชื่อคลิป (เลือก 1)", "", "1. ", "2. ", "3. ", "",
            "## คำอธิบาย", "", "```text", "", "```", "",
            "## เช็กก่อนกดเผยแพร่", "",
            "- ถ้าใช้เสียงหรือเพลงจาก AI และแพลตฟอร์มถามเรื่องเนื้อหาสังเคราะห์ ให้ตัดสินตามกฎล่าสุดของแพลตฟอร์ม",
            "- ตรวจสิทธิ์การใช้เพลงเชิงพาณิชย์ก่อน ถ้าช่องหารายได้",
            "- ถ้าคลิปมีเด็ก ตั้งค่าตามนโยบายเนื้อหาที่มีเด็กของแพลตฟอร์ม", ""]), encoding="utf-8")
    print(f"delivered: {video}\ncovers: {', '.join(covers)}\nupload sheet: {sheet} (fill in titles and description in Thai)")


if __name__ == "__main__":
    main()
