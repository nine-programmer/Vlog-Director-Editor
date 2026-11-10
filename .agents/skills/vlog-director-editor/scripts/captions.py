"""Caption review: export every on-screen text of an episode for the user to correct,
then apply the corrections back into timeline.json.

Speech-to-text for Thai is often wrong, so captions must be checked by the user before
the full render.

Usage:
  python captions.py export --timeline 04_Episodes/EP01_Name/timeline.json
      -> writes captions.md next to the timeline (the user edits the text column)
  python captions.py apply --timeline 04_Episodes/EP01_Name/timeline.json
      -> copies edited text back into timeline.json
Impact words are written as "word / word / word".
"""
import argparse
import json
import re
import sys
from pathlib import Path

from render_episode import Episode

TEXT_TYPES = {"speech", "voice", "comment", "label", "score", "tag", "stamp", "impact"}
KIND_TH = {"speech": "คำพูด", "voice": "เสียงพากย์", "comment": "คอมเมนต์", "label": "ป้าย", "score": "ตารางคะแนน",
           "tag": "ป้ายชื่อ", "stamp": "แสตมป์", "impact": "คำกระแทก"}


def text_of(g):
    return " / ".join(g["words"]) if g["type"] == "impact" else g["text"]


def export(path):
    spec = json.loads(path.read_text(encoding="utf-8"))
    n = 0
    for g in spec.get("graphics", []):
        if g["type"] in TEXT_TYPES and "id" not in g:
            n += 1
            while any(x.get("id") == f"c{n:02d}" for x in spec["graphics"]):
                n += 1
            g["id"] = f"c{n:02d}"
    path.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    ep = Episode(path)
    rows = []
    for g in spec["graphics"]:
        if g["type"] in TEXT_TYPES:
            t = ep.at(g["t"])
            rows.append(f"| {g['id']} | {int(t // 60)}:{t % 60:04.1f} | {KIND_TH[g['type']]} | {text_of(g)} |")
    out = path.parent / "captions.md"
    out.write_text("\n".join([
        f"# ตรวจซับ {path.parent.name}", "",
        "แก้เฉพาะคอลัมน์ \"ข้อความ\" แล้วบอกเอเจนต์ คำกระแทกให้คั่นแต่ละคำด้วย \" / \"", "",
        "| id | เวลา | ชนิด | ข้อความ |", "|---|---|---|---|", *rows, ""]), encoding="utf-8")
    print(f"captions: {out} ({len(rows)} items)")


def apply(path):
    spec = json.loads(path.read_text(encoding="utf-8"))
    table = (path.parent / "captions.md").read_text(encoding="utf-8")
    edits = {}
    for line in table.splitlines():
        m = re.match(r"\|\s*(c\d+)\s*\|[^|]*\|[^|]*\|(.*)\|\s*$", line)
        if m:
            edits[m[1]] = m[2].strip()
    changed = 0
    for g in spec.get("graphics", []):
        new = edits.get(g.get("id"))
        if new is None or new == text_of(g):
            continue
        if g["type"] == "impact":
            g["words"] = [w.strip() for w in new.split("/") if w.strip()]
        else:
            g["text"] = new
        changed += 1
    path.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"applied {changed} change(s) to {path}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["export", "apply"])
    ap.add_argument("--timeline", required=True, type=Path)
    a = ap.parse_args()
    (export if a.action == "export" else apply)(a.timeline.resolve())


if __name__ == "__main__":
    main()
