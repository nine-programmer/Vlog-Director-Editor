"""Check a timeline.json before rendering and list every problem in plain words.

render_episode.py, captions.py and deliver.py run this check automatically. Run it by
hand after writing or editing a timeline to catch misspelt fields, missing files and
times that point at shots which do not exist.

Usage:
  python validate_timeline.py --timeline 04_Episodes/EP01_Name/timeline.json
"""
import argparse
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
MANIFEST = json.loads((SKILL / "assets" / "styles" / "styles.json").read_text(encoding="utf-8"))

TOP = {"format", "video_window", "style", "font", "shots", "voiceovers", "bgm", "graphics", "sfx",
       "tones", "postmarks", "route", "master_trim", "grade", "music_cuts"}
SHOT = {"id", "src", "in", "out", "speed", "hold", "zoom", "move", "punches", "audio", "fill", "grade"}
GRADE_PRESETS = {"none", "natural", "vivid", "warm", "cool", "film", "bw"}
GRADE = {"preset", "brightness", "contrast", "saturation", "warmth"}
EASES = {"linear", "inout", "in", "out"}
VARIANTS = {"tear", "whip", "burst", "page", "fade"}
CAPTION_CHARS = {"vertical": 26, "horizontal": 48}  # base characters that fit one line without shrinking


def base_chars(text):
    text = re.sub(r"<[^>]+>", "", str(text))
    return sum(1 for c in text if not c.isspace() and unicodedata.category(c) != "Mn")


def clip_length(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return None
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
    raw = {}
    for p in (root / "01_Raw_Footage").rglob("*"):
        if p.is_file():
            if p.name in raw:
                errors.append(f"two clips are both named '{p.name}' in 01_Raw_Footage; clips are found by name, so ask the user to rename one")
            raw[p.name] = p
    sfx_names = {p.stem for p in (root / "05_Shared_Assets" / "sfx").rglob("*.wav")}
    sfx_list = ", ".join(sorted(sfx_names))
    lengths = {}

    def framing_ok(z, where):
        for k in ("cx", "cy"):
            if k in z and not 0 <= z[k] <= 1:
                errors.append(f"{where}: {k} must be between 0 and 1 (a fraction of the source picture)")
        if z.get("scale", 1) < 1:
            errors.append(f"{where}: scale must be 1 or more")

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

    def grade_ok(g, where):
        if isinstance(g, str):
            g = {"preset": g}
        if not isinstance(g, dict):
            errors.append(f"{where}: grade must be a preset name or an object")
            return
        unknown(g, GRADE, f"{where} grade")
        if g.get("preset", "none") not in GRADE_PRESETS:
            errors.append(f"{where}: grade preset '{g.get('preset')}' does not exist (available: {', '.join(sorted(GRADE_PRESETS))})")

    if "grade" in spec:
        grade_ok(spec["grade"], "top level")
    framed = isinstance(win.get("h"), (int, float)) and isinstance(fmt.get("h"), (int, float)) and win["h"] < fmt["h"]

    zoom_limit = 1.8 if framed else 1.4  # the vertical window shows the picture smaller, so it can crop further
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
        else:
            if s["src"] not in lengths:
                lengths[s["src"]] = clip_length(raw[s["src"]])
            if lengths[s["src"]] and s["out"] > lengths[s["src"]] + .05:
                errors.append(f"{where}: 'out' ({s['out']}) is past the end of the clip ({lengths[s['src']]:.2f}s)")
        if s["in"] < 0:
            errors.append(f"{where}: 'in' cannot be negative")
        if s.get("hold", 0) < 0:
            errors.append(f"{where}: hold cannot be negative")
        if s["out"] <= s["in"]:
            errors.append(f"{where}: 'out' ({s['out']}) must be after 'in' ({s['in']})")
        sp = s.get("speed", 1)
        if isinstance(sp, list):
            if len(sp) < 2 or any(not isinstance(p, dict) or set(p) != {"at", "v"} or p["v"] <= 0 for p in sp):
                errors.append(f"{where}: a speed ramp is a list of at least two {{\"at\": source seconds, \"v\": speed above 0}}")
            elif any(not s["in"] <= p["at"] <= s["out"] for p in sp):
                errors.append(f"{where}: speed ramp 'at' times must be source times between in and out")
        elif not isinstance(sp, (int, float)) or sp <= 0:
            errors.append(f"{where}: speed must be a number above 0 or a ramp list")
        elif sp < .5 and s.get("audio", {}).get("mode", "bed") != "mute":
            errors.append(f"{where}: speed below 0.5 needs audio.mode 'mute' (sound cannot be slowed that far)")
        elif sp > 4:
            warnings.append(f"{where}: speed {sp} is very fast; 1.5-4 is the useful range")
        if "move" in s:
            unknown(s["move"], ZOOM | {"ease"}, f"{where} move")
            framing_ok(s["move"], f"{where} move")
            if s["move"].get("ease", "inout") not in EASES:
                errors.append(f"{where}: move.ease must be one of {', '.join(sorted(EASES))}")
            if s.get("punches"):
                errors.append(f"{where}: 'move' and 'punches' cannot be used on the same shot; split it into two shots")
            if s["move"].get("scale", 1) > zoom_limit:
                warnings.append(f"{where}: move ends at {s['move']['scale']}x, which will look soft on 1080p footage")
        if "grade" in s:
            grade_ok(s["grade"], where)
        if "fill" in s and not isinstance(s["fill"], bool):
            errors.append(f"{where}: fill must be true or false")
        if s.get("fill") and not framed:
            warnings.append(f"{where}: 'fill' does nothing here because the video window already covers the whole frame")
        unknown(s.get("zoom", {}), ZOOM, f"{where} zoom")
        framing_ok(s.get("zoom", {}), f"{where} zoom")
        if s.get("zoom", {}).get("scale", 1) > zoom_limit:
            warnings.append(f"{where}: zoom {s['zoom']['scale']}x will look soft on 1080p footage (keep at most {zoom_limit})")
        for p in s.get("punches", []):
            unknown(p, ZOOM | {"at", "dur"}, f"{where} punch")
            framing_ok(p, f"{where} punch")
            if p.get("dur", 1) <= 0:
                errors.append(f"{where}: punch 'dur' must be above 0")
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
            shot = shots_by_id.get(value.get("shot"))
            if shot is None:
                errors.append(f"{where}: time points at shot '{value.get('shot')}', which does not exist")
            elif "src" in value and not shot["in"] - .01 <= value["src"] <= shot["out"] + .01:
                errors.append(f"{where}: source time {value['src']} is outside shot {shot['id']} ({shot['in']}-{shot['out']})")
            unknown(value, {"shot", "offset", "src"}, f"{where} time")
        elif not isinstance(value, (int, float)):
            errors.append(f"{where}: time must be seconds, {{\"shot\": id, \"offset\": seconds}} "
                          f"or {{\"shot\": id, \"src\": source seconds}}")

    shots_by_id = {s["id"]: s for s in spec["shots"] if {"id", "in", "out"} <= set(s)}

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
            errors.append(f"{where}: sound '{e['name']}' is not in 05_Shared_Assets/sfx (available: {sfx_list})")

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
            errors.append(f"{where}: sound '{g['sfx']}' is not in 05_Shared_Assets/sfx (available: {sfx_list})")
        if kind == "tag" and not {"x", "y"} <= set(g):
            warnings.append(f"{where}: a tag without x and y sits in the middle of the frame; place it next to the person")
        if "variant" in g and g["variant"] not in VARIANTS:
            warnings.append(f"{where}: variant '{g['variant']}' is unknown, the style's own transition is used")
        if kind in ("speech", "voice", "comment") and "<br" not in g["text"]:
            limit = CAPTION_CHARS["vertical" if fmt.get("h", 0) > fmt.get("w", 0) else "horizontal"]
            if base_chars(g["text"]) > limit:
                warnings.append(f"{where}: {base_chars(g['text'])} characters will be shrunk to fit one line; "
                                f"split it into two cues (about {limit} at most)")

    for k in ("tones", "postmarks"):
        for x in spec.get(k, []):
            time_ok(x.get("t"), k)
    for x in spec.get("route", {}).get("progress", []):
        time_ok(x.get("t"), "route.progress")
    for i, c in enumerate(spec.get("music_cuts", [])):
        where = f"music_cuts #{i + 1}"
        if set(c) != {"t", "end"}:
            errors.append(f"{where}: needs exactly 't' and 'end'")
        else:
            time_ok(c["t"], where)
            time_ok(c["end"], where)
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
