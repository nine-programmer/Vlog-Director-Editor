"""Step 7: assemble approved episodes into one master. Run only after the user confirms.

Each episode can drop its own hook and outro in the master through "master_trim" in its
timeline.json, for example {"start": {"shot": "s2"}, "end": {"shot": "s15", "offset": 3}}.

Usage:
  python master_vlog.py --root <project> --inputs 04_Episodes/EP01_X/renders/EP01_Full_v02.mp4 ... [--trim]
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from render_episode import Episode, video_args


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height:format=duration",
                          "-of", "json", str(path)], capture_output=True, text=True).stdout
    d = json.loads(out)
    v = next(s for s in d["streams"] if "width" in s)
    return v["width"], v["height"], float(d["format"]["duration"])


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--inputs", nargs="+", required=True, type=Path)
    ap.add_argument("--trim", action="store_true", help="apply each episode's master_trim")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()

    clips = []
    for p in a.inputs:
        w, h, dur = probe(p)
        start, end = 0.0, dur
        tl = p.resolve().parent.parent / "timeline.json"
        if a.trim and tl.exists():
            ep = Episode(tl)
            mt = ep.spec.get("master_trim", {})
            start = ep.at(mt["start"]) if "start" in mt else 0.0
            end = ep.at(mt["end"]) if "end" in mt else dur
        clips.append((p, w, h, start, end))
    sizes = {(w, h) for _, w, h, _, _ in clips}
    if len(sizes) > 1:
        sys.exit(f"episodes have different sizes {sizes}; a master needs one format")

    out = a.out
    if not out:
        v = 1
        while (a.root / "06_Master" / f"Master_v{v:02d}.mp4").exists():
            v += 1
        out = a.root / "06_Master" / f"Master_v{v:02d}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd, parts = ["ffmpeg", "-y", "-v", "error"], []
    for i, (p, _, _, s, e) in enumerate(clips):
        cmd += ["-i", str(p)]
        parts.append(f"[{i}:v]trim={s:.3f}:{e:.3f},setpts=PTS-STARTPTS,fade=t=in:st=0:d=0.15[v{i}];"
                     f"[{i}:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st={e - s - .05:.3f}:d=0.05[a{i}]")
    fc = ";".join(parts) + ";" + "".join(f"[v{i}][a{i}]" for i in range(len(clips))) + f"concat=n={len(clips)}:v=1:a=1[v][a]"
    cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", *video_args("final"), "-pix_fmt", "yuv420p",
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-1500:])
    log = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(out), "-af", "ebur128=peak=true:framelog=quiet",
                          "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", log)[-1]
    tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", log)[-1]
    print(f"master written: {out} ({probe(out)[2]:.1f}s, {lufs} LUFS, true peak {tp} dBTP)")
    if float(tp) > -1.0:
        print("warning: true peak is above -1 dBTP; re-render with a lower master level before delivery")


if __name__ == "__main__":
    main()
