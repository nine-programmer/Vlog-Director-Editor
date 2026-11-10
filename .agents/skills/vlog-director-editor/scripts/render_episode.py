"""Cut and mix one episode from its timeline.json.

Stage "rough" gives a 540p review file with no graphics.
Stage "full" adds the style overlay, SFX, mastering and QA at full resolution.

A shot is a stretch of a clip or a photo; a photo always moves slowly. A shot with "dissolve"
fades in over the end of the shot before it.

Shots are encoded to cached segments in _temp, so changing one shot only
re-encodes that shot. Output versions are never overwritten.

Usage:
  python render_episode.py --timeline 04_Episodes/EP01_Name/timeline.json --stage rough
"""
import argparse
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.signal import lfilter

import stills

SR = 48000
SPEECH_LUFS = -16.0
BGM_OPEN_LUFS = -20.0
BGM_DUCK_DB = -11.0
MASTER_LUFS = -14.0
LIMIT = 0.74  # about -2.6 dBFS: the limiter is sample-peak and AAC overshoot measured about 1.4 dB
CLEAN = "highpass=f=90,afftdn=nr=10:nf=-35:tn=1,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120"
STYLES_DIR = Path(__file__).resolve().parent.parent / "assets" / "styles"
MANIFEST = json.loads((STYLES_DIR / "styles.json").read_text(encoding="utf-8"))
SFX_PEAK_DB = {"hit": -8, "boom": -8, "stamp": -9, "ding": -12, "paper_slap": -13, "boing": -13, "rewind": -12,
               "paper_tear": -12, "whoosh": -14, "shutter": -15, "pop": -16, "chime": -16, "tape": -18, "pen": -18}
NO_OFFSET = {"tear", "transition", "arrow", "ring", "label"}  # sound starts with the motion, not on a landing frame
BAR_COLOR = "0x2b2a28"
GRADES = {
    "none": "",
    "natural": "eq=contrast=1.04:saturation=1.08",
    "vivid": "eq=contrast=1.08:saturation=1.28",
    "warm": "colorbalance=rm=0.06:bm=-0.06:rh=0.03:bh=-0.03,eq=saturation=1.08",
    "cool": "colorbalance=rm=-0.05:bm=0.06:rh=-0.02:bh=0.03,eq=saturation=1.04",
    "film": "curves=all='0/0.05 0.5/0.5 1/0.95',eq=saturation=0.88,colorbalance=rm=0.03:bm=-0.03",
    "bw": "hue=s=0,eq=contrast=1.1",
}
EASES = {"linear": "P", "inout": "P*P*(3-2*P)", "out": "(1-(1-P)*(1-P))", "in": "P*P"}
_ENCODER = None


def grade_filter(grade):
    """ffmpeg filter chain for a grade given as a preset name or an object."""
    if not grade:
        return ""
    g = {"preset": grade} if isinstance(grade, str) else grade
    parts = [GRADES[g.get("preset", "none")]]
    eq = [f"{k}={g[k]}" for k in ("brightness", "contrast", "saturation") if k in g]
    if eq:
        parts.append("eq=" + ":".join(eq))
    if g.get("warmth"):
        w = g["warmth"] * .12
        parts.append(f"colorbalance=rm={w:.3f}:bm={-w:.3f}:rh={w / 2:.3f}:bh={-w / 2:.3f}")
    return ",".join(p for p in parts if p)


def speed_points(shot):
    """Speed ramp key points [(source time, speed)], or None for a constant speed."""
    sp = shot.get("speed", 1.0)
    return None if isinstance(sp, (int, float)) else sorted((float(p["at"]), float(p["v"])) for p in sp)


def _ramp_piece(ta, va, tb, vb, e):
    """Output seconds spent going from source time ta to e while speed moves linearly va -> vb."""
    if abs(vb - va) < 1e-9:
        return (e - ta) / va
    k = (vb - va) / (tb - ta)
    return math.log((va + k * (e - ta)) / va) / k


def warp(points, T):
    """Output time (seconds, relative to the first key point) at source time T."""
    t0, v0 = points[0]
    if T <= t0:
        return (T - t0) / v0
    out = 0.0
    for (ta, va), (tb, vb) in zip(points, points[1:]):
        out += _ramp_piece(ta, va, tb, vb, min(T, tb))
        if T <= tb:
            return out
    return out + (T - points[-1][0]) / points[-1][1]


def warp_expr(points, X):
    """The same mapping as warp() written as an ffmpeg expression of X (source seconds)."""
    t0, v0 = points[0]
    tn, vn = points[-1]
    total = warp(points, tn)
    expr = f"({total:.6f}+({X}-{tn:.6f})/{vn:.6f})"
    for (ta, va), (tb, vb) in reversed(list(zip(points, points[1:]))):
        base = warp(points, ta)
        if abs(vb - va) < 1e-9:
            piece = f"({base:.6f}+({X}-{ta:.6f})/{va:.6f})"
        else:
            k = (vb - va) / (tb - ta)
            piece = f"({base:.6f}+log(({va:.6f}+{k:.6f}*({X}-{ta:.6f}))/{va:.6f})/{k:.6f})"
        expr = f"if(lt({X},{tb:.6f}),{piece},{expr})"
    return f"if(lt({X},{t0:.6f}),({X}-{t0:.6f})/{v0:.6f},{expr})"


def video_args(kind):
    """Encoder arguments. Uses NVENC when it works on this machine, otherwise libx264."""
    global _ENCODER
    if _ENCODER is None:
        probe = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=s=256x256:d=0.1",
                                "-c:v", "h264_nvenc", "-f", "null", "-"], capture_output=True)
        _ENCODER = "nvenc" if probe.returncode == 0 else "x264"
    if _ENCODER == "nvenc":
        return {"segment": ["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "16", "-b:v", "0", "-g", "25", "-bf", "0"],
                "rough": ["-c:v", "h264_nvenc", "-preset", "p4", "-rc", "vbr", "-cq", "25", "-b:v", "0"],
                "final": ["-c:v", "h264_nvenc", "-preset", "p6", "-tune", "hq", "-rc", "vbr", "-cq", "19", "-b:v", "14M",
                          "-maxrate", "24M", "-bufsize", "28M", "-profile:v", "high", "-spatial-aq", "1", "-temporal-aq", "1"]}[kind]
    return {"segment": ["-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-g", "25", "-bf", "0"],
            "rough": ["-c:v", "libx264", "-preset", "veryfast", "-crf", "25"],
            "final": ["-c:v", "libx264", "-preset", "slow", "-crf", "19", "-maxrate", "24M", "-bufsize", "28M", "-profile:v", "high"]}[kind]


VOICE_CHAIN = "highpass=f=70,acompressor=threshold=-20dB:ratio=2:attack=8:release=120"


def db(x):
    return 10.0 ** (x / 20.0)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode:
        sys.exit("ffmpeg failed:\n" + r.stderr.decode("utf-8", "replace")[-1500:])
    return r.stdout


def clip_seconds(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return 0.0


def probe_size(path):
    out = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
               "stream=width,height", "-of", "csv=p=0", str(path)]).decode()
    w, h = out.strip().split(",")[:2]
    return int(w), int(h)


def decode(path, ss=None, dur=None, af=None):
    cmd = ["ffmpeg", "-v", "error"]
    if ss is not None:
        cmd += ["-ss", f"{ss:.3f}"]
    if dur is not None:
        cmd += ["-t", f"{dur:.3f}"]
    cmd += ["-i", str(path), "-map", "0:a:0"]
    if af:
        cmd += ["-af", af]
    cmd += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "pipe:1"]
    return np.frombuffer(run(cmd), np.float32).reshape(-1, 2).copy()


def loudness(x):
    """Integrated loudness per BS.1770 (48 kHz)."""
    y = lfilter([1.53512485958697, -2.69169618940638, 1.19839281085285],
                [1.0, -1.69065929318241, 0.73248077421585], x, axis=0)
    y = lfilter([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621], y, axis=0)
    block, hop = int(.4 * SR), int(.1 * SR)
    if len(y) < block:
        powers = np.array([(y ** 2).mean(axis=0).sum()])
    else:
        cum = np.cumsum((y ** 2).sum(axis=1))
        ends = np.arange(block, len(y) + 1, hop)
        powers = (cum[ends - 1] - np.concatenate([[0.0], cum[ends[1:] - block - 1]])) / block
    powers = powers[powers > 10 ** ((-70 + .691) / 10)]
    if powers.size == 0:
        return -70.0
    gate = 10 ** ((-.691 + 10 * np.log10(powers.mean()) - 10 + .691) / 10)
    kept = powers[powers > gate]
    return -.691 + 10 * np.log10((kept if kept.size else powers).mean())


def trapezoid(n, windows, attack, release):
    w = np.zeros(n)
    t = np.arange(n) / SR
    for s, e in windows:
        rise = np.clip((t - (s - attack)) / max(attack, 1e-3), 0, 1)
        fall = np.clip(((e + release) - t) / max(release, 1e-3), 0, 1)
        w = np.maximum(w, np.minimum(rise, fall))
    return w


def merge(windows, gap):
    out = []
    for s, e in sorted(windows):
        if out and s - out[-1][1] < gap:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


def edge_fade(x, fade_in, fade_out):
    n = len(x)
    env = np.ones(n, np.float32)
    a, b = min(int(fade_in * SR), n), min(int(fade_out * SR), n)
    if a:
        env[:a] = np.linspace(0, 1, a)
    if b:
        env[-b:] = np.minimum(env[-b:], np.linspace(1, 0, b))
    return x * env[:, None]


_HAS_AUDIO = {}


def has_audio(path):
    if path not in _HAS_AUDIO:
        out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                              "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout
        _HAS_AUDIO[path] = bool(out.strip())
    return _HAS_AUDIO[path]


def add(bus, x, t):
    start = int(round(t * SR))
    if start < 0:  # sound that would begin before the episode starts loses its head, it is not delayed
        x, start = x[-start:], 0
    end = min(start + len(x), len(bus))
    if end > start:
        bus[start:end] += x[:end - start]


class Episode:
    def __init__(self, path):
        self.path = Path(path).resolve()
        self.dir = self.path.parent
        from validate_timeline import require_valid
        require_valid(self.path)
        self.root = next(p for p in self.dir.parents if (p / "01_Raw_Footage").is_dir())
        self.spec = json.loads(self.path.read_text(encoding="utf-8"))
        self.fmt = self.spec["format"]
        self.fps = self.fmt["fps"]
        self.cache = self.root / "_temp" / self.dir.name
        (self.cache / "segments").mkdir(parents=True, exist_ok=True)
        self.raw = {p.name: p for p in (self.root / "01_Raw_Footage").rglob("*") if p.is_file()}
        self.resolve()

    def resolve(self):
        frame = 0
        self.by_id = {}
        for shot in self.spec["shots"]:
            if shot["src"] not in self.raw:
                sys.exit(f"missing source: {shot['src']}")
            shot["path"] = self.raw[shot["src"]]
            shot["photo"] = stills.is_image(shot["path"])
            if shot["photo"]:
                shot["in"], shot["out"] = 0.0, float(shot["dur"])
                shot.setdefault("move", stills.default_move(shot.get("zoom", {})))
                shot["move"].setdefault("ease", "linear")
            cuts = sorted({shot["in"], shot["out"], *[p["at"] for p in shot.get("punches", [])]})
            zoom = dict(scale=1.0, cx=.5, cy=.5, **{}) | shot.get("zoom", {})
            # A punch keeps the fields it does not set. With "dur" it snaps back afterwards.
            framing, state = {}, zoom
            for p in sorted(shot.get("punches", []), key=lambda p: p["at"]):
                hit = {**state, **{k: p[k] for k in ("scale", "cx", "cy") if k in p}}
                framing[p["at"]] = hit
                if "dur" in p and p["at"] + p["dur"] < shot["out"]:
                    framing[round(p["at"] + p["dur"], 4)] = state
                else:
                    state = hit
            cuts = sorted({*cuts, *framing})
            segs, done = [], 0
            for a, b in zip(cuts, cuts[1:]):
                if a in framing:
                    zoom = framing[a]
                target = round(self.smap(shot, b) * self.fps)
                segs.append({"in": a, "dur": b - a, "frames": target - done, "hold": 0, **zoom})
                done = target
            hold = round(shot.get("hold", 0) * self.fps)
            if "move" in shot:
                segs[0]["move"] = {**{k: segs[0][k] for k in ("scale", "cx", "cy")}, **shot["move"]}
            segs[-1]["frames"] += hold
            segs[-1]["hold"] = hold / self.fps
            shot["segments"] = segs
            shot["start"] = frame / self.fps
            frame += done + hold
            shot["end"] = frame / self.fps
            self.by_id[shot["id"]] = shot
        self.frames = frame
        self.duration = frame / self.fps
        for prev, shot in zip([None] + self.spec["shots"], self.spec["shots"]):
            n = round(shot.get("dissolve", 0) * self.fps)
            if not n:
                continue
            first = shot["segments"][0]
            if n > first["frames"] - round(first["hold"] * self.fps):
                sys.exit(f"shot {shot['id']}: dissolve {shot['dissolve']}s is longer than the shot (or than its part before the first punch)")
            shot["dissolve_frames"] = n
            prev["tail"] = self.tail_segment(prev, n)
            prev["fade_after"] = n / self.fps

    def tail_segment(self, shot, n):
        """The n frames a shot goes on for under the dissolve into the next shot."""
        last = shot["segments"][-1]
        end = {k: last.get("move", last)[k] for k in ("scale", "cx", "cy")}
        if shot["photo"]:
            # The move carries on through the dissolve, so the picture never stops before it is gone.
            last["move_total"] = last["frames"] + n
            return {**last, "frames": n, "move_at": last["frames"], "hold": 0}
        pts = speed_points(shot)
        v = pts[-1][1] if pts else shot.get("speed", 1.0)
        need = n / self.fps * v
        if shot.get("hold") or shot["out"] + need > clip_seconds(shot["path"]) - .1:
            # Nothing left to play: freeze the last frame.
            step = v / self.fps
            return {"in": max(shot["out"] - step, 0), "dur": step, "frames": n, "hold": n / self.fps, "speed": v, **end}
        return {"in": shot["out"], "dur": need, "frames": n, "hold": 0, "speed": v, **end}

    def at(self, value):
        if isinstance(value, dict):
            shot = self.by_id[value["shot"]]
            if "src" in value:  # a source time inside the shot, e.g. from a transcript
                return self.to_timeline(shot, value["src"]) + value.get("offset", 0.0)
            return shot["start"] + value.get("offset", 0.0)
        return float(value)

    def manual_sfx(self):
        return [{**e, "t": self.at(e["t"])} for e in self.spec.get("sfx", [])]

    def smap(self, shot, src_t):
        """Seconds from the start of the shot at which source time src_t plays."""
        pts = speed_points(shot)
        if pts:
            return warp(pts, src_t) - warp(pts, shot["in"])
        return (src_t - shot["in"]) / shot.get("speed", 1.0)

    def to_timeline(self, shot, src_t):
        return shot["start"] + self.smap(shot, src_t)

    @property
    def framed(self):
        return self.spec["video_window"]["h"] < self.fmt["h"]

    @property
    def has_fill(self):
        """True when some shot fills the whole frame, so every segment is encoded full-frame."""
        return self.framed and any(s.get("fill") for s in self.spec["shots"])

    def encode_segment(self, shot, seg):
        win = self.spec["video_window"]
        fill = bool(shot.get("fill")) and self.framed
        vw, vh = (self.fmt["w"], self.fmt["h"]) if fill else (self.fmt["w"], win["h"])
        grade = grade_filter(shot.get("grade", self.spec.get("grade")))
        boxed = f",pad={self.fmt['w']}:{self.fmt['h']}:0:{win['y']}:color={BAR_COLOR}" if self.has_fill and not fill else ""
        if shot["photo"]:
            return self.encode_photo(shot, seg, vw, vh, (("," + grade) if grade else "") + boxed)
        W, H = probe_size(shot["path"])
        ar = vw / vh
        cw0 = min(W, H * ar)
        pts = None if "speed" in seg else speed_points(shot)
        if pts:
            g0 = warp(pts, seg["in"])
            retime = f"setpts=PTS-STARTPTS,setpts='({warp_expr(pts, f'(T+{seg['in']:.6f})')}-{g0:.6f})/TB'"
        else:
            retime = f"setpts=(PTS-STARTPTS)/{seg.get('speed', shot.get('speed', 1.0))}"
        move = seg.get("move")
        if move:
            # Animated zoom: zoompan on an enlarged canvas so the motion is sub-pixel smooth.
            ss = 1 if W >= 3000 else 2 if W > 1920 else 3
            cw_, ch_ = (W, W / ar) if W / H > ar else (H * ar, H)
            cw_, ch_ = int(round(cw_ / 2)) * 2, int(round(ch_ / 2)) * 2
            ox, oy = (cw_ - W) // 2, (ch_ - H) // 2
            n = max(seg["frames"] - round(seg["hold"] * self.fps) - 1, 1)
            ease = EASES[move.get("ease", "inout")].replace("P", f"min(on/{n},1)")
            lerp = lambda a, b: f"({a:.5f}+({b - a:.5f})*{ease})"
            r = cw_ / cw0
            z = f"{r:.5f}*{lerp(seg['scale'], move['scale'])}"
            px = f"({ox}+{W}*{lerp(seg['cx'], move['cx'])})*{ss}"
            py = f"({oy}+{H}*{lerp(seg['cy'], move['cy'])})*{ss}"
            zx = f"max({ox * ss},min({px}-iw/zoom/2,{(ox + W) * ss}-iw/zoom))"
            zy = f"max({oy * ss},min({py}-ih/zoom/2,{(oy + H) * ss}-ih/zoom))"
            framing = (f"fps={self.fps},pad={cw_}:{ch_}:{ox}:{oy},scale={cw_ * ss}:{ch_ * ss}:flags=bicubic,format=yuv444p,"
                       f"zoompan=z='{z}':x='{zx}':y='{zy}':d=1:s={vw}x{vh}:fps={self.fps},unsharp=5:5:0.4")
        else:
            cw = cw0 / seg["scale"]
            ch = cw / ar
            x = min(max(seg["cx"] * W - cw / 2, 0), W - cw)
            y = min(max(seg["cy"] * H - ch / 2, 0), H - ch)
            cw, ch, x, y = [int(v) // 2 * 2 for v in (cw, ch, x, y)]
            sharpen = ",unsharp=5:5:0.4" if seg["scale"] > 1 or fill else ""
            framing = f"crop={cw}:{ch}:{x}:{y},scale={vw}:{vh}:flags=lanczos{sharpen},fps={self.fps}"
        if grade:
            framing += "," + grade
        framing += boxed
        vf = (f"trim=duration={seg['dur']:.4f},{retime},{framing},"
              f"tpad=stop_mode=clone:stop_duration={seg['hold'] + 2:.3f},format=yuv420p,setsar=1")
        key = hashlib.sha1(json.dumps([str(shot["path"]), seg["in"], vf, seg["frames"]]).encode()).hexdigest()[:16]
        out = self.cache / "segments" / f"{key}.mp4"
        if not out.exists():
            run(["ffmpeg", "-y", "-v", "error", "-ss", f"{seg['in']:.4f}", "-t", f"{seg['dur'] + .5:.4f}",
                 "-i", str(shot["path"]), "-map", "0:v:0", "-an", "-vf", vf, "-frames:v", str(seg["frames"]),
                 *video_args("segment"), "-colorspace", "bt709", "-color_primaries", "bt709",
                 "-color_trc", "bt709", str(out)])
        return out

    def encode_photo(self, shot, seg, vw, vh, after):
        geo = stills.prepare(shot["path"], self.cache / "stills", vw, vh)
        start = {k: seg[k] for k in ("scale", "cx", "cy")}
        vf = stills.move_filter(geo, vw, vh, self.fps, start, {**start, **seg["move"]}, seg["move"]["ease"], seg["frames"],
                                seg.get("move_total", seg["frames"]), seg.get("move_at", 0)) + after + ",format=yuv420p,setsar=1"
        key = hashlib.sha1(json.dumps([geo["path"].name, vf, seg["frames"]]).encode()).hexdigest()[:16]
        out = self.cache / "segments" / f"{key}.mp4"
        if not out.exists():
            run(["ffmpeg", "-y", "-v", "error", "-i", str(geo["path"]), "-vf", vf, "-frames:v", str(seg["frames"]), "-an",
                 *video_args("segment"), "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", str(out)])
        return out

    def dissolve(self, tail, head, n, frames):
        """The first n frames of segment `head` fade in over `tail`, the end of the shot before it."""
        key = hashlib.sha1(f"{tail.name}|{head.name}|{n}".encode()).hexdigest()[:16]
        out = self.cache / "segments" / f"x{key}.mp4"
        if not out.exists():
            norm = f"fps={self.fps},settb=AVTB,setpts=PTS-STARTPTS,format=yuv420p"
            fc = (f"[0:v]{norm}[a];[1:v]{norm}[b];"
                  f"[a][b]xfade=transition=fade:duration={n / self.fps:.4f}:offset=0,format=yuv420p,setsar=1[v]")
            run(["ffmpeg", "-y", "-v", "error", "-i", str(tail), "-i", str(head), "-filter_complex", fc, "-map", "[v]",
                 "-frames:v", str(frames), *video_args("segment"), "-colorspace", "bt709", "-color_primaries", "bt709",
                 "-color_trc", "bt709", str(out)])
        return out

    def build_base(self):
        parts = []
        for prev, s in zip([None] + self.spec["shots"], self.spec["shots"]):
            segs = [self.encode_segment(s, seg) for seg in s["segments"]]
            if s.get("dissolve_frames"):
                segs[0] = self.dissolve(self.encode_segment(prev, prev["tail"]), segs[0], s["dissolve_frames"], s["segments"][0]["frames"])
            parts += segs
        listing = self.cache / "segments.txt"
        listing.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
        base = self.cache / "base.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(base)])
        return base

    def style(self):
        name = self.spec.get("style", "scrapbook")
        if name not in MANIFEST["styles"]:
            sys.exit(f"unknown style '{name}', available: {', '.join(MANIFEST['styles'])}")
        return name, MANIFEST["styles"][name]

    def resolve_graphics(self):
        """Turn timeline graphics into an overlay composition and a list of SFX events."""
        name, st = self.style()
        cues, sfx = [], []
        bad = []
        for i, g in enumerate(self.spec.get("graphics", [])):
            cue = dict(g)
            cue["t"], cue["end"] = self.at(g["t"]), self.at(g["end"])
            label = f"graphic {g.get('id', '#' + str(i + 1))} ({g['type']})"
            if cue["end"] <= cue["t"]:
                bad.append(f"{label}: 'end' ({cue['end']:.2f}s) is not after 't' ({cue['t']:.2f}s)")
            elif cue["t"] >= self.duration or cue["end"] < 0:
                bad.append(f"{label}: plays at {cue['t']:.2f}-{cue['end']:.2f}s, outside the {self.duration:.2f}s episode")
            if "src" in cue:
                cue["src"] = (self.dir / cue["src"]).resolve().as_uri()
            kind = "transition" if g["type"] == "tear" else g["type"]
            sound = g.get("sfx", st["sfx"].get(kind))
            if sound:
                offset = 0 if g["type"] in NO_OFFSET else st["hit_offset"]
                starts = [cue["t"] + k * g.get("stagger", .22) for k in range(len(g["words"]))] if g["type"] == "impact" else [cue["t"]]
                sfx += [{"name": sound, "t": s + offset} for s in starts]
            cues.append(cue)
        if bad:
            sys.exit("timeline has problems, fix these first:\n  - " + "\n  - ".join(bad))
        sfx += self.manual_sfx()
        fonts = list(st["fonts"])
        font = self.spec.get("font")
        if font:
            # The same family can be listed at another weight by another style, so this style's own option wins.
            options = [f for f in st["font_options"] if f["family"] == font]
            if not options:
                sys.exit(f"font '{font}' is not a font option of style '{name}' in styles.json")
            fonts.append(options[0])
        comp = {"style": name, "format": {**self.fmt, "dur": self.duration}, "hold_fps": st["hold_fps"],
                "video_window": self.spec["video_window"], "fonts": fonts, "cues": cues}
        if self.has_fill:
            comp["fills"] = [{"t": s["start"], "end": s["end"]} for s in self.spec["shots"] if s.get("fill")]
        if font:
            comp["font"] = font
        for k in ("tones", "postmarks"):
            if k in self.spec:
                comp[k] = [{**x, "t": self.at(x["t"])} for x in self.spec[k]]
        if "route" in self.spec:
            r = dict(self.spec["route"])
            r["progress"] = [{"t": self.at(x["t"]), "p": x["p"]} for x in r["progress"]]
            comp["route"] = r
        return comp, sfx

    def build_overlay(self, comp):
        from render_overlay import render
        code = "".join(p.read_text(encoding="utf-8") for p in sorted(STYLES_DIR.glob("*.js")))
        text = json.dumps(comp, ensure_ascii=False, sort_keys=True)
        key = hashlib.sha1((text + code).encode()).hexdigest()[:16]
        out = self.cache / f"overlay_{key}.mov"
        if not out.exists():
            comp_path = self.cache / "comp.json"
            comp_path.write_text(text, encoding="utf-8")
            render(comp_path, self.root / "05_Shared_Assets" / "fonts", out)
        return out

    def build_mix(self, sfx=()):
        n = round(self.duration * SR)
        camera, speech = np.zeros((n, 2)), []

        voices = []
        for v in self.spec.get("voiceovers", []):
            x = decode(self.dir / v["file"], af=VOICE_CHAIN)
            x = x * db(SPEECH_LUFS - loudness(x) + v.get("gain_db", 0))
            t = self.at(v["t"])
            voices.append((x, t))
            speech.append((t, t + len(x) / SR))

        for shot in self.spec["shots"]:
            a = shot.get("audio", {})
            mode = a.get("mode", "bed")
            if mode == "mute" or shot["photo"]:
                continue
            if not has_audio(shot["path"]):
                print(f"warning: {shot['src']} has no sound; shot {shot['id']} is treated as mute")
                continue
            pts = speed_points(shot)
            speed = 1.0 if pts else shot.get("speed", 1.0)
            fade_in, fade_out = shot.get("dissolve", 0.0), shot.get("fade_after", 0.0)
            lead, tail = a.get("lead", 0.0), max(a.get("tail", 0.0), fade_out)
            start_src = max(shot["in"] - lead, 0.0)
            lead = shot["in"] - start_src
            af = CLEAN + (f",atempo={speed}" if speed != 1.0 else "")
            x = decode(shot["path"], start_src, (shot["out"] - start_src) + tail, af)
            if pts:
                x = self.warp_audio(x, start_src, pts)
            t0 = shot["start"] + self.smap(shot, start_src)
            if mode == "full":
                x = x * db(np.clip(SPEECH_LUFS - loudness(x), -6, 14))
                speech.append((max(t0, 0.0), shot["end"] + tail))
            else:
                env = np.full(len(x), db(a.get("bed_db", -18.0)), np.float32)
                for s, e in a.get("moments", []):
                    ms, me = [int((self.smap(shot, v) - self.smap(shot, start_src)) * SR) for v in (s, e)]
                    gain = db(np.clip(SPEECH_LUFS - loudness(x[ms:me]), -6, 14))
                    w = trapezoid(len(x), [(ms / SR, me / SR)], .15, .3)
                    env = np.maximum(env, env + (gain - env) * w)
                    speech.append((self.to_timeline(shot, s), self.to_timeline(shot, e)))
                x = x * env[:, None]
            add(camera, edge_fade(x, max(.12 if lead else .02, fade_in), max(.25 if tail else .03, fade_out)), t0)

        vo_windows = merge([(t, t + len(x) / SR) for x, t in voices], .5)
        bus = camera * (1 - .5 * trapezoid(n, vo_windows, .15, .3))[:, None]
        for x, t in voices:
            add(bus, x, t)

        duck = trapezoid(n, merge(speech, 1.2), .25, .6)
        stops = [(self.at(c["t"]), self.at(c["end"])) for c in self.spec.get("music_cuts", [])]
        keep = 1 - trapezoid(n, stops, .02, .12)  # music drops out for a beat, then slams back
        for b in self.spec.get("bgm", []):
            t = self.at(b.get("t", 0))
            end = self.at(b["end"]) if "end" in b else self.duration
            x = decode(self.dir / b["file"], b.get("in", 0.0), end - t)
            if len(x) < (end - t) * SR - SR:
                print(f"warning: {b['file']} is shorter than its slot")
            x = x * db(BGM_OPEN_LUFS - loudness(x))
            x = edge_fade(x, b.get("fade_in", .3), b.get("fade_out", 1.0))
            i = int(round(t * SR))
            slice_duck = duck[i:i + len(x)]
            x = x[:len(slice_duck)] * (db(BGM_DUCK_DB * slice_duck) * keep[i:i + len(slice_duck)])[:, None]
            add(bus, x, t)

        sfx_dir = self.root / "05_Shared_Assets" / "sfx"
        library = {p.stem: p for p in sfx_dir.rglob("*.wav")}
        for e in sfx:
            if e["name"] not in library:
                sys.exit(f"missing SFX: {e['name']} (looked in {sfx_dir})")
            x = decode(library[e["name"]])
            peak = float(np.abs(x).max()) + 1e-9
            add(bus, x * (db(SFX_PEAK_DB.get(e["name"], -14) + e.get("gain_db", 0)) / peak), e["t"])

        wav = self.cache / "mix.wav"
        driven = bus.astype(np.float32) * db(MASTER_LUFS - loudness(bus))
        for _ in range(2):
            driven = driven * db(MASTER_LUFS - loudness(self.limit(driven)))
        master = self.limit(driven)
        run_input(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "pipe:0",
                   "-c:a", "pcm_s24le", str(wav)], master.tobytes())
        print(f"mix: {loudness(master):.1f} LUFS, peak {20 * math.log10(float(np.abs(master).max()) + 1e-9):.1f} dBFS")
        return wav

    @staticmethod
    def warp_audio(x, start_src, pts):
        """Follow a speed ramp with the sound (pitch moves with speed, like tape)."""
        src = start_src + np.arange(0, len(x) + SR // 100, SR // 100) / SR
        out = np.array([warp(pts, t) for t in src])
        out -= out[0]
        pos = np.interp(np.arange(int(out[-1] * SR)) / SR, out, (src - start_src) * SR)
        idx = np.arange(len(x))
        return np.stack([np.interp(pos, idx, x[:, c]) for c in range(x.shape[1])], axis=1).astype(np.float32)

    @staticmethod
    def limit(x):
        out = run_input(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "pipe:0",
                         "-af", f"alimiter=limit={LIMIT}:attack=3:release=80:level=0:latency=1",
                         "-f", "f32le", "pipe:1"], x.astype(np.float32).tobytes())
        y = np.frombuffer(out, np.float32).reshape(-1, 2).copy()
        return y[:len(x)] if len(y) >= len(x) else np.vstack([y, np.zeros((len(x) - len(y), 2), np.float32)])

    def fades(self):
        """Filters for the episode's fade from black and fade to black (they cover the graphics too)."""
        i, o = self.spec.get("fade_in", 0), self.spec.get("fade_out", 0)
        return (f",fade=t=in:st=0:d={i}" if i else "") + (f",fade=t=out:st={self.duration - o:.3f}:d={o}" if o else "")

    def next_output(self, stage):
        ep = self.dir.name.split("_")[0]
        renders = self.dir / "renders"
        renders.mkdir(exist_ok=True)
        v = 1
        while (renders / f"{ep}_{stage.capitalize()}_v{v:02d}.mp4").exists():
            v += 1
        return renders / f"{ep}_{stage.capitalize()}_v{v:02d}.mp4"

    def render_rough(self):
        base, mix = self.build_base(), self.build_mix(self.manual_sfx())
        out = self.next_output("rough")
        win = self.spec["video_window"]
        W, H = self.fmt["w"], self.fmt["h"]
        fc = (f"color=c={BAR_COLOR}:s={W}x{H}:r={self.fps}:d={self.duration:.3f}[bg];"
              f"[bg][0:v]overlay=0:{0 if self.has_fill else win['y']}:shortest=1,scale={W // 2}:{H // 2}{self.fades()},format=yuv420p[v]")
        run(["ffmpeg", "-y", "-v", "error", "-i", str(base), "-i", str(mix), "-filter_complex", fc,
             "-map", "[v]", "-map", "1:a", "-t", f"{self.duration:.3f}", *video_args("rough"), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)])
        print(f"rough written: {out} ({self.duration:.2f}s)")


    def render_full(self):
        comp, sfx = self.resolve_graphics()
        base, overlay, mix = self.build_base(), self.build_overlay(comp), self.build_mix(sfx)
        out = self.next_output("full")
        win = self.spec["video_window"]
        W, H = self.fmt["w"], self.fmt["h"]
        fc = (f"color=c={BAR_COLOR}:s={W}x{H}:r={self.fps}:d={self.duration:.3f}[bg];"
              f"[bg][0:v]overlay=0:{0 if self.has_fill else win['y']}:shortest=1[b];"
              f"[1:v]scale=out_color_matrix=bt709:out_range=tv,format=yuva420p[g];"
              f"[b][g]overlay=0:0:eof_action=pass:format=yuv420{self.fades()},format=yuv420p[v]")
        run(["ffmpeg", "-y", "-v", "error", "-i", str(base), "-i", str(overlay), "-i", str(mix),
             "-filter_complex", fc, "-map", "[v]", "-map", "2:a", "-t", f"{self.duration:.3f}",
             *video_args("final"),
             "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
             "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(out)])
        print(f"full written: {out} ({self.duration:.2f}s)")
        from qa_check import check
        check(out, self, comp, str(overlay) + ".layout.json")


def run_input(cmd, data):
    r = subprocess.run(cmd, input=data, capture_output=True)
    if r.returncode:
        sys.exit("ffmpeg failed:\n" + r.stderr.decode("utf-8", "replace")[-1500:])
    return r.stdout


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeline", required=True)
    ap.add_argument("--stage", choices=["rough", "full"], default="rough")
    a = ap.parse_args()
    ep = Episode(a.timeline)
    ep.render_rough() if a.stage == "rough" else ep.render_full()


if __name__ == "__main__":
    main()
