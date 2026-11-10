"""Automatic QA for a finished episode render.

Writes <episode>/qa/QA_<render name>.md and a contact sheet of every hero
graphic, so the agent can look at the frames before showing the user.
Called by render_episode.py after a full render.
"""
import re
import subprocess
import unicodedata
from pathlib import Path

TARGET_LUFS, MAX_TP = -14.0, -1.0
HERO = {"impact", "stamp", "score", "sticker", "tag", "comment", "arrow"}
TEXT_TYPES = {"speech", "voice", "comment", "label", "score", "tag"}
MIN_FIT = 0.8  # a caption scaled below this to fit its line is too long
MAX_CPS = 18  # Thai base characters per second, ignoring vowel and tone marks
# Areas covered by the Shorts / Reels / TikTok interface on a 1080x1920 frame.
# Conservative estimates, not official numbers: check on a phone when in doubt.
VERTICAL_UNSAFE = {"top bar": (0, 0, 1080, 110), "bottom caption area": (0, 1560, 1080, 1920),
                   "right buttons": (960, 900, 1080, 1560)}


def ffmpeg_log(args):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args, "-f", "null", "-"],
                          capture_output=True, text=True, encoding="utf-8", errors="replace").stderr


def base_chars(text):
    text = re.sub(r"<[^>]+>", "", text)
    return sum(1 for c in text if not c.isspace() and unicodedata.category(c) != "Mn")


def overlaps(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def check(video, ep, comp, layout_path=None):
    video = Path(video)
    qa_dir = ep.dir / "qa"
    qa_dir.mkdir(exist_ok=True)
    rows, fails = [], 0

    def row(name, ok, detail):
        nonlocal fails
        fails += 0 if ok else 1
        rows.append(f"| {name} | {'ผ่าน' if ok else 'ไม่ผ่าน'} | {detail} |")

    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height",
                            "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout.split()
    duration = float(probe[-1])
    row("ความยาว", abs(duration - ep.duration) < .1, f"{duration:.2f}s (ไทม์ไลน์ {ep.duration:.2f}s)")
    fmt = ep.fmt
    vertical = fmt["h"] > fmt["w"]
    limit = (60, 90) if vertical else (60, 180)
    row("ความยาวตามรูปแบบ", duration <= limit[1], f"{'แนวตั้ง' if vertical else 'แนวนอน'} ไม่เกิน {limit[1]} วินาที")

    log = ffmpeg_log(["-i", str(video), "-af", "ebur128=peak=true:framelog=quiet"])
    lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", log)[-1])
    tp = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", log)[-1])
    row("ความดัง", abs(lufs - TARGET_LUFS) <= 1, f"{lufs:.1f} LUFS (เป้า {TARGET_LUFS})")
    row("True Peak", tp <= MAX_TP, f"{tp:.1f} dBTP (ไม่เกิน {MAX_TP})")

    black = re.findall(r"black_start:([\d.]+)", ffmpeg_log(["-i", str(video), "-an", "-vf", "blackdetect=d=0.3"]))
    row("จอดำ", not black, ", ".join(black) or "ไม่พบ")
    silence = re.findall(r"silence_start: ([\d.]+)", ffmpeg_log(["-i", str(video), "-vn", "-af", "silencedetect=n=-45dB:d=1"]))
    row("เสียงเงียบเกิน 1 วินาที", not silence, ", ".join(silence) or "ไม่พบ")

    fast = []
    for c in comp["cues"]:
        if c["type"] in TEXT_TYPES:
            cps = base_chars(c["text"]) / max(c["end"] - c["t"], .1)
            if cps > MAX_CPS:
                fast.append(f"{c['t']:.1f}s ({cps:.0f} ตัว/วิ)")
    row("ความเร็วอ่านซับ", not fast, ", ".join(fast) or f"ทุกซับไม่เกิน {MAX_CPS} ตัวอักษรต่อวินาที")

    speech = [(s["start"], s["end"]) for s in ep.spec["shots"] if s.get("audio", {}).get("mode") == "full"]
    speech += [(ep.to_timeline(s, a), ep.to_timeline(s, b)) for s in ep.spec["shots"]
               for a, b in s.get("audio", {}).get("moments", [])]
    clash = []
    for v in ep.spec.get("voiceovers", []):
        t = ep.at(v["t"])
        length = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(ep.dir / v["file"])], capture_output=True, text=True).stdout.strip()
        end = t + float(length or 1)
        if any(min(end, b) - max(t, a) > .3 for a, b in speech):  # more than 0.3 s on top of real speech
            clash.append(f"{v['file']} ที่ {t:.1f}s")
    row("พากย์ทับเสียงจริง", not clash, ", ".join(clash) or "ไม่พบ")

    import json
    layout = json.loads(Path(layout_path).read_text(encoding="utf-8")) if layout_path and Path(layout_path).exists() else []
    small = [f"{i['t']:.1f}s \"{i['text'][:20]}\" เหลือ {i['fit']:.0%}" for i in layout
             if i["kind"] in TEXT_TYPES and i.get("fit", 1) < MIN_FIT]
    row("ซับยาวจนถูกย่อ", not small, "; ".join(small) or "ไม่มีซับที่ถูกย่อเกินเกณฑ์ (แบ่งซับยาวเป็นสองอัน)")

    if layout and ep.fmt["h"] > ep.fmt["w"]:
        hits = []
        for item in layout:
            for zone, box in VERTICAL_UNSAFE.items():
                if overlaps(item["box"], box):
                    hits.append(f"{item['t']:.1f}s \"{item['text'][:20]}\" ชน{zone}")
        zone_th = {"top bar": "แถบบน", "bottom caption area": "พื้นที่คำบรรยายด้านล่าง", "right buttons": "ปุ่มด้านขวา"}
        hits = [h.replace(k, v) for h in hits for k, v in zone_th.items() if k in h]
        row("โซนปลอดภัยของแนวตั้ง", not hits, "; ".join(hits) or "ตัวหนังสือไม่อยู่ใต้ปุ่มหรือแถบของแอป")

    fills = comp.get("fills", [])  # captions sit over the picture in full-frame shots, so show those too
    heroes = [c for c in comp["cues"] if c["type"] in HERO
              or (c["type"] in TEXT_TYPES and any(f["t"] <= c["t"] < f["end"] for f in fills))]
    sheet = qa_dir / f"{video.stem}_hero.jpg"
    if heroes:
        times = [min(c["t"] + 1.0, (c["t"] + c["end"]) / 2) for c in heroes]  # after slow styles finish entering
        select = "+".join(f"between(t,{t:.2f},{t + .019:.3f})" for t in times)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vf",
                        f"select='{select}',scale=270:-2,tile={min(len(times), 6)}x{(len(times) + 5) // 6}:padding=4",
                        "-vsync", "0", "-frames:v", "1", "-update", "1", str(sheet)])

    report = qa_dir / f"QA_{video.stem}.md"
    report.write_text("\n".join([
        f"# QA: {video.name}", "", f"ผลรวม: {'ผ่านทุกข้อ' if not fails else f'ไม่ผ่าน {fails} ข้อ'}", "",
        "| รายการ | ผล | รายละเอียด |", "|---|---|---|", *rows, "",
        f"ภาพเฟรมกราฟิกหลัก: `{sheet.name}` (เอเจนต์ต้องเปิดดูว่าไม่บังหน้าและอ่านออก)", "",
        "ตรวจเองไม่ได้: ความรู้สึกของเสียงมิกซ์, การออกเสียงคำพากย์, ความตลกของจังหวะ", ""]), encoding="utf-8")
    print(f"QA: {'all passed' if not fails else f'{fails} failed'} -> {report}")
    return fails
