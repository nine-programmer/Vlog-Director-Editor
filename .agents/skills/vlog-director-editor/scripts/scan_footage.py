"""Step 1: scan every clip in 01_Raw_Footage and write a report.

The user has already chosen what goes into 01_Raw_Footage, so this only checks
technical quality and transcribes speech. It reports clips worth removing and
never deletes anything.

It also writes a timestamped contact sheet per clip to 02_Scan_Reports/sheets/, which is
what the story plan is built from: transcripts tell you what is said, sheets show what is seen.

Usage:
  python scan_footage.py --root <project> [--transcribe] [--model large-v3-turbo] [--no-sheets]
"""
import argparse
import json
import statistics
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

VIDEO_EXT = {".mp4", ".mov", ".mxf", ".m4v"}
SAMPLE_WIDTH = 640
SAMPLE_HEIGHT = 360
SAMPLE_EVERY_S = 2.0
BLUR_THRESHOLD = 60.0     # Laplacian variance on a 640x360 frame
DARK_THRESHOLD = 25.0     # mean luma, 0-255
MIN_DURATION_S = 2.0


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,width,height,r_frame_rate:format=duration",
         "-of", "json", str(path)],
        capture_output=True, text=True, encoding="utf-8", check=True).stdout
    data = json.loads(out)
    video = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    has_audio = any(s["codec_type"] == "audio" for s in data["streams"])
    num, den = video["r_frame_rate"].split("/")
    return {
        "width": video["width"],
        "height": video["height"],
        "fps": round(float(num) / float(den), 3),
        "duration": round(float(data["format"]["duration"]), 2),
        "has_audio": has_audio,
    }


def sample_frames(path):
    cmd = ["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:v:0",
           "-vf", f"fps=1/{SAMPLE_EVERY_S},scale={SAMPLE_WIDTH}:{SAMPLE_HEIGHT},format=gray",
           "-f", "rawvideo", "pipe:1"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    frame_size = SAMPLE_WIDTH * SAMPLE_HEIGHT
    count = len(raw) // frame_size
    return np.frombuffer(raw, np.uint8, count * frame_size).reshape(-1, SAMPLE_HEIGHT, SAMPLE_WIDTH)


def assess(path):
    info = probe(path)
    frames = sample_frames(path)
    sharp = [float(cv2.Laplacian(f, cv2.CV_64F).var()) for f in frames]
    bright = [float(f.mean()) for f in frames]
    info["sharpness_median"] = round(statistics.median(sharp), 1) if sharp else 0.0
    info["blurry_ratio"] = round(sum(s < BLUR_THRESHOLD for s in sharp) / len(sharp), 2) if sharp else 1.0
    info["brightness_mean"] = round(statistics.mean(bright), 1) if bright else 0.0

    reasons = []
    if info["sharpness_median"] < BLUR_THRESHOLD:
        reasons.append("เบลอเกือบทั้งคลิป")
    elif info["blurry_ratio"] >= 0.5:
        reasons.append("เบลอมากกว่าครึ่งคลิป")
    if info["brightness_mean"] < DARK_THRESHOLD:
        reasons.append("มืดมาก")
    if info["duration"] < MIN_DURATION_S:
        reasons.append("สั้นเกินไป")
    info["remove_reasons"] = reasons
    return info


def transcribe(paths, model_name):
    from faster_whisper import WhisperModel
    try:
        import ctranslate2
        gpu = ctranslate2.get_cuda_device_count() > 0
    except Exception:
        gpu = False
    try:
        model = WhisperModel(model_name, device="cuda", compute_type="float16") if gpu else None
    except Exception:
        model = None
    if model is None:
        print("no usable NVIDIA GPU: transcribing on the CPU (several times slower)", flush=True)
        model = WhisperModel(model_name, device="cpu", compute_type="int8")
    results = {}
    for path in paths:
        segments, _ = model.transcribe(str(path), language="th", vad_filter=True, word_timestamps=True)
        results[path.name] = [
            {"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
             "words": [{"w": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2)} for w in (s.words or [])]}
            for s in segments
        ]
        print(f"transcribed {path.name}: {len(results[path.name])} segments", flush=True)
    return results


def write_markdown(report, out_path):
    lines = ["# รายงานสแกนฟุตเทจ", ""]
    flagged = {k: v for k, v in report.items() if v["remove_reasons"]}
    lines += ["## คลิปที่ควรพิจารณาเอาออก", ""]
    if flagged:
        lines += [f"- `{k}`: {', '.join(v['remove_reasons'])}" for k, v in flagged.items()]
    else:
        lines.append("ไม่พบคลิปที่มีปัญหา")
    lines += ["", "ระบบรายงานเท่านั้น ไม่ลบไฟล์เอง", "", "## ทุกคลิป", "",
              "| ไฟล์ | ความยาว | ขนาด | fps | เสียง | ความคม | สัดส่วนเบลอ | ความสว่าง |",
              "|---|---|---|---|---|---|---|---|"]
    for name, v in report.items():
        lines.append(f"| `{name}` | {v['duration']}s | {v['width']}x{v['height']} | {v['fps']} | {'มี' if v['has_audio'] else 'ไม่มี'} | "
                     f"{v['sharpness_median']} | {v['blurry_ratio']:.0%} | {v['brightness_mean']} |")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--raw-dir", type=Path, help="default: <root>/01_Raw_Footage")
    ap.add_argument("--out", type=Path, help="default: <root>/02_Scan_Reports")
    ap.add_argument("--transcribe", action="store_true")
    ap.add_argument("--model", default="large-v3-turbo")
    ap.add_argument("--no-sheets", action="store_true")
    args = ap.parse_args()

    raw_dir = args.raw_dir or args.root / "01_Raw_Footage"
    out_dir = args.out or args.root / "02_Scan_Reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    clips = sorted(p for p in raw_dir.rglob("*") if p.suffix.lower() in VIDEO_EXT)
    if not clips:
        sys.exit(f"no clips found in {raw_dir}")
    names = [c.name for c in clips]
    twice = sorted({n for n in names if names.count(n) > 1})
    if twice:
        sys.exit("clips are found by file name, so names must be unique across 01_Raw_Footage. "
                 "Ask the user to rename these: " + ", ".join(twice))

    report = {}
    for clip in clips:
        report[clip.name] = assess(clip)
        print(f"scanned {clip.name}: sharp {report[clip.name]['sharpness_median']}", flush=True)

    (out_dir / "scan_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report, out_dir / "scan_report.md")

    if not args.no_sheets:
        from frames import sheet
        for clip in clips:
            dur = report[clip.name]["duration"]
            every = max(2.0, round(dur / 15, 1))
            sheet(clip, 0.5, max(dur - 0.5, 0.5), every, out_dir / "sheets" / f"{clip.stem}.jpg", width=320, cols=5)
        print(f"sheets written to {out_dir / 'sheets'}")

    if args.transcribe:
        transcript = transcribe([c for c in clips if report[c.name]["has_audio"]], args.model)
        (out_dir / "transcripts.json").write_text(
            json.dumps(transcript, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
