"""Check a timeline.json before rendering and list every problem in plain words.

render_episode.py, captions.py and deliver.py run this check automatically. Run it by
hand after writing or editing a timeline to catch misspelt fields, missing files and
times that point at shots which do not exist.

Usage:
  python validate_timeline.py --timeline 04_Episodes/EP01_Name/timeline.json
"""
import argparse
import json
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
MANIFEST = json.loads((SKILL / "assets" / "styles" / "styles.json").read_text(encoding="utf-8"))

TOP = {"format", "video_window", "style", "font", "shots", "voiceovers", "bgm", "graphics", "sfx",
       "tones", "postmarks", "route", "master_trim"}
SHOT = {"id", "src", "in", "out", "speed", "hold", "zoom", "punches", "audio"}
AUDIO = {"mode", "lead", "tail", "bed_db", "moments"}
ZOOM = {"scale", "cx", "cy"}
TEXT_CUES = {"speech", "voice", "comment", "label", "score", "tag", "stamp"}
CUE_REQUIRED = {**{k: {"text"} for k in TEXT_CUES}, "impact": {"words"}, "sticker": {"src", "w", "x", "y"},
                "march": {"src", "w", "y", "from", "to"}, "arrow": {"from", "to"}, "ring": {"x", "y"},
                "transition": set(), "tear": set()}
CUE_OPTIONAL = {"id", "type", "t", "end", "x", "y", "ax", "tilt", "color", "sfx", "size", "stagger", "flip",
                "count", "spacing", "rx", "ry", "variant"}


def validate(path):
    """Return (errors, warnings) for the timeline at path."""
    path = Path(path).resolve()
    errors, warnings = [], []
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"not valid JSON: {e}"], []
    root = next((p for p in path.parents if (p / "01_Raw_Footage").is_dir()), None)
    if root is None:
        return ["no 01_Raw_Footage folder above this timeline; it must live inside a project"], []
    raw = {p.name for p in (root / "01_Raw_Footage").rglob("*") if p.is_file()}
    sfx_names = {p.stem for p in (root / "05_Shared_Assets" / "sfx").rglob("*.wav")}

    def unknown(obj, allowed, where):
        for k in sorted(set(obj) - allowed):
            errors.append(f"{where}: unknown field '{k}' (allowed: {', '.join(sorted(allowed))})")

    unknown(spec, TOP, "top level")
    for k in ("format", "video_window", "shots"):
        if k not in spec:
            errors.append(f"top level: '{k}' is required")
    if any(k not in spec for k in ("format", "video_window", "shots")):
        return errors, warnings

    fmt, win = spec["format"], spec["video_window"]
    for k in ("w", "h", "fps"):
        if not isinstance(fmt.get(k), (int, float)):
            errors.append(f"format.{k} must be a number")
    for k in ("y", "h"):
        if not isinstance(win.get(k), (int, float)):
            errors.append(f"video_window.{k} must be a number")
    if all(isinstance(v, (int, float)) for v in (fmt.get("h"), win.get("y"), win.get("h"))) and win["y"] + win["h"] > fmt["h"]:
        errors.append(f"video_window (y {win['y']} + h {win['h']}) is taller than the {fmt['h']} px frame")

    style = spec.get("style", "scrapbook")
    if style not in MANIFEST["styles"]:
        errors.append(f"style '{style}' does not exist (available: {', '.join(MANIFEST['styles'])})")
    elif "font" in spec:
        fonts = [f["family"] for f in MANIFEST["styles"][style]["font_options"]]
        if spec["font"] not in fonts:
            errors.append(f"font '{spec['font']}' is not an option of style '{style}' (options: {', '.join(fonts)})")

    ids = set()
    if not spec["shots"]:
        errors.append("shots: at least one shot is required")
    for i, s in enumerate(spec["shots"]):
        where = f"shot {s.get('id', '#' + str(i + 1))}"
        unknown(s, SHOT, where)
        missing = {"id", "src", "in", "out"} - set(s)
        if missing:
            errors.append(f"{where}: missing {', '.join(sorted(missing))}")
            continue
        if s["id"] in ids:
            errors.append(f"{where}: id is used twice")
        ids.add(s["id"])
        if s["src"] not in raw:
            errors.append(f"{where}: source '{s['src']}' is not in 01_Raw_Footage")
        if s["out"] <= s["in"]:
            errors.append(f"{where}: 'out' ({s['out']}) must be after 'in' ({s['in']})")
        if s.get("speed", 1) <= 0:
            errors.append(f"{where}: speed must be above 0")
        unknown(s.get("zoom", {}), ZOOM, f"{where} zoom")
        if s.get("zoom", {}).get("scale", 1) > 1.4:
            warnings.append(f"{where}: zoom {s['zoom']['scale']}x will look soft on 1080p footage (keep at most 1.4)")
        for p in s.get("punches", []):
            unknown(p, ZOOM | {"at"}, f"{where} punch")
            if "at" not in p or not s["in"] <= p["at"] < s["out"]:
                errors.append(f"{where}: punch 'at' must be a source time between in and out")
        a = s.get("audio", {})
        unknown(a, AUDIO, f"{where} audio")
        if a.get("mode", "bed") not in ("full", "bed", "mute"):
            errors.append(f"{where}: audio.mode must be full, bed or mute")
        for m in a.get("moments", []):
            if len(m) != 2 or not s["in"] <= m[0] < m[1] <= s["out"]:
                errors.append(f"{where}: audio moment {m} must be [start, end] in source seconds inside the shot")

    def time_ok(value, where):
        if isinstance(value, dict):
            if value.get("shot") not in ids:
                errors.append(f"{where}: time points at shot '{value.get('shot')}', which does not exist")
            unknown(value, {"shot", "offset"}, f"{where} time")
        elif not isinstance(value, (int, float)):
            errors.append(f"{where}: time must be seconds or {{\"shot\": id, \"offset\": seconds}}")

    def file_ok(rel, where):
        if not (path.parent / rel).is_file():
            errors.append(f"{where}: file '{rel}' not found in the episode folder")

    for i, v in enumerate(spec.get("voiceovers", [])):
        where = f"voiceover #{i + 1}"
        unknown(v, {"file", "t", "gain_db"}, where)
        if "file" in v and "t" in v:
            file_ok(v["file"], where)
            time_ok(v["t"], where)
        else:
            errors.append(f"{where}: 'file' and 't' are required")
    for i, b in enumerate(spec.get("bgm", [])):
        where = f"bgm #{i + 1}"
        unknown(b, {"file", "t", "end", "in", "fade_in", "fade_out"}, where)
        if "file" not in b:
            errors.append(f"{where}: 'file' is required")
            continue
        file_ok(b["file"], where)
        for k in ("t", "end"):
            if k in b:
                time_ok(b[k], where)
    for i, e in enumerate(spec.get("sfx", [])):
        where = f"sfx #{i + 1}"
        unknown(e, {"name", "t", "gain_db"}, where)
        if "name" not in e or "t" not in e:
            errors.append(f"{where}: 'name' and 't' are required")
            continue
        time_ok(e["t"], where)
        if sfx_names and e["name"] not in sfx_names:
            errors.append(f"{where}: sound '{e['name']}' is not in 05_Shared_Assets/sfx")

    for i, g in enumerate(spec.get("graphics", [])):
        kind = g.get("type")
        where = f"graphic {g.get('id', '#' + str(i + 1))} ({kind})"
        if kind not in CUE_REQUIRED:
            errors.append(f"{where}: unknown type (allowed: {', '.join(sorted(CUE_REQUIRED))})")
            continue
        missing = (CUE_REQUIRED[kind] | {"t", "end"}) - set(g)
        if missing:
            errors.append(f"{where}: missing {', '.join(sorted(missing))}")
            continue
        for k in sorted(set(g) - CUE_OPTIONAL - CUE_REQUIRED[kind]):
            warnings.append(f"{where}: field '{k}' is not used by the engine (misspelt?)")
        time_ok(g["t"], where)
        time_ok(g["end"], where)
        if "src" in g:
            file_ok(g["src"], where)
        if g.get("sfx") and sfx_names and g["sfx"] not in sfx_names:
            errors.append(f"{where}: sound '{g['sfx']}' is not in 05_Shared_Assets/sfx")

    for k in ("tones", "postmarks"):
        for x in spec.get(k, []):
            time_ok(x.get("t"), k)
    for x in spec.get("route", {}).get("progress", []):
        time_ok(x.get("t"), "route.progress")
    for k, v in spec.get("master_trim", {}).items():
        if k not in ("start", "end"):
            errors.append(f"master_trim: unknown field '{k}' (allowed: start, end)")
        else:
            time_ok(v, f"master_trim.{k}")
    if style != "scrapbook":
        for k in ("tones", "postmarks", "route"):
            if k in spec:
                warnings.append(f"'{k}' is only drawn by the scrapbook style; style '{style}' ignores it")
    return errors, warnings


def require_valid(path):
    """Exit with a readable list when the timeline has errors; print warnings otherwise."""
    errors, warnings = validate(path)
    for w in warnings:
        print(f"timeline warning: {w}")
    if errors:
        sys.exit("timeline has problems, fix these first:\n  - " + "\n  - ".join(errors))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeline", required=True, type=Path)
    a = ap.parse_args()
    require_valid(a.timeline)
    print("timeline ok")


if __name__ == "__main__":
    main()
