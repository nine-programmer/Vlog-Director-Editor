"""Cut and mix one episode from its timeline.json.

Stage "rough" gives a 540p review file with no graphics.
Stage "full" adds the style overlay, SFX, mastering and QA at full resolution.

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

SR = 48000
SPEECH_LUFS = -16.0
BGM_OPEN_LUFS = -20.0
BGM_DUCK_DB = -11.0
MASTER_LUFS = -14.0
LIMIT = 0.74  # about -2.6 dBFS: the limiter is sample-peak and AAC overshoot measured about 1.4 dB
CLEAN = "highpass=f=90,afftdn=nr=10:nf=-35:tn=1,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120"
HOLD_FPS = 12
HIT_OFFSET = 2 / HOLD_FPS  # pieces land on the second stop-motion step
SFX_PEAK_DB = {"hit": -8, "stamp": -9, "paper_slap": -13, "rewind": -12, "paper_tear": -12,
               "shutter": -15, "pop": -16, "tape": -18, "pen": -18}
DEFAULT_SFX = {"impact": "paper_slap", "stamp": "stamp", "score": "stamp", "label": "tape", "comment": "paper_slap",
               "sticker": "pop", "tag": "pop", "tear": "paper_tear", "arrow": "pen"}
VOICE_CHAIN = "highpass=f=70,acompressor=threshold=-20dB:ratio=2:attack=8:release=120"


def db(x):
    return 10.0 ** (x / 20.0)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode:
        sys.exit("ffmpeg failed:\n" + r.stderr.decode("utf-8", "replace")[-1500:])
    return r.stdout


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


def add(bus, x, t):
    start = max(int(round(t * SR)), 0)
    end = min(start + len(x), len(bus))
    if end > start:
        bus[start:end] += x[:end - start]


class Episode:
    def __init__(self, path):
        self.path = Path(path).resolve()
        self.dir = self.path.parent
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
            speed = shot.get("speed", 1.0)
            cuts = sorted({shot["in"], shot["out"], *[p["at"] for p in shot.get("punches", [])]})
            zoom = dict(scale=1.0, cx=.5, cy=.5, **{}) | shot.get("zoom", {})
            punches = {p["at"]: p for p in shot.get("punches", [])}
            segs, done = [], 0
            for a, b in zip(cuts, cuts[1:]):
                if a in punches:
                    zoom = {**zoom, **{k: punches[a][k] for k in ("scale", "cx", "cy") if k in punches[a]}}
                target = round((b - shot["in"]) / speed * self.fps)
                segs.append({"in": a, "dur": b - a, "frames": target - done, "hold": 0, **zoom})
                done = target
            hold = round(shot.get("hold", 0) * self.fps)
            segs[-1]["frames"] += hold
            segs[-1]["hold"] = hold / self.fps
            shot["segments"] = segs
            shot["start"] = frame / self.fps
            frame += done + hold
            shot["end"] = frame / self.fps
            self.by_id[shot["id"]] = shot
        self.frames = frame
        self.duration = frame / self.fps

    def at(self, value):
        if isinstance(value, dict):
            return self.by_id[value["shot"]]["start"] + value.get("offset", 0.0)
        return float(value)

    def to_timeline(self, shot, src_t):
        return shot["start"] + (src_t - shot["in"]) / shot.get("speed", 1.0)

    def encode_segment(self, shot, seg):
        vw, vh = self.fmt["w"], self.spec["video_window"]["h"]
        W, H = probe_size(shot["path"])
        ar = vw / vh
        cw = min(W, H * ar) / seg["scale"]
        ch = cw / ar
        x = min(max(seg["cx"] * W - cw / 2, 0), W - cw)
        y = min(max(seg["cy"] * H - ch / 2, 0), H - ch)
        cw, ch, x, y = [int(v) // 2 * 2 for v in (cw, ch, x, y)]
        speed = shot.get("speed", 1.0)
        sharpen = ",unsharp=5:5:0.4" if seg["scale"] > 1 else ""
        vf = (f"trim=duration={seg['dur']:.4f},setpts=(PTS-STARTPTS)/{speed},crop={cw}:{ch}:{x}:{y},"
              f"scale={vw}:{vh}:flags=lanczos{sharpen},fps={self.fps},"
              f"tpad=stop_mode=clone:stop_duration={seg['hold'] + 1:.3f},format=yuv420p,setsar=1")
        key = hashlib.sha1(json.dumps([str(shot["path"]), seg["in"], vf, seg["frames"]]).encode()).hexdigest()[:16]
        out = self.cache / "segments" / f"{key}.mp4"
        if not out.exists():
            run(["ffmpeg", "-y", "-v", "error", "-ss", f"{seg['in']:.4f}", "-t", f"{seg['dur'] + .5:.4f}",
                 "-i", str(shot["path"]), "-map", "0:v:0", "-an", "-vf", vf, "-frames:v", str(seg["frames"]),
                 "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "16", "-b:v", "0",
                 "-g", "25", "-bf", "0", "-colorspace", "bt709", "-color_primaries", "bt709",
                 "-color_trc", "bt709", str(out)])
        return out

    def build_base(self):
        parts = [self.encode_segment(s, seg) for s in self.spec["shots"] for seg in s["segments"]]
        listing = self.cache / "segments.txt"
        listing.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
        base = self.cache / "base.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(base)])
        return base

    def resolve_graphics(self):
        """Turn timeline graphics into an overlay composition and a list of SFX events."""
        cues, sfx = [], []
        for g in self.spec.get("graphics", []):
            cue = dict(g)
            cue["t"], cue["end"] = self.at(g["t"]), self.at(g["end"])
            if "src" in cue:
                cue["src"] = (self.dir / cue["src"]).resolve().as_uri()
            name = g.get("sfx", DEFAULT_SFX.get(g["type"]))
            if name:
                offset = 0 if g["type"] in ("tear", "arrow", "label") else HIT_OFFSET
                starts = [cue["t"] + k * g.get("stagger", .25) for k in range(len(g["words"]))] if g["type"] == "impact" else [cue["t"]]
                sfx += [{"name": name, "t": s + offset} for s in starts]
            cues.append(cue)
        for e in self.spec.get("sfx", []):
            sfx.append({**e, "t": self.at(e["t"])})
        comp = {"format": {**self.fmt, "dur": self.duration}, "hold_fps": HOLD_FPS,
                "video_window": self.spec["video_window"], "cues": cues}
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
        style = self.spec.get("style", "scrapbook")
        html = Path(__file__).resolve().parent.parent / "assets" / "styles" / style / "overlay.html"
        text = json.dumps(comp, ensure_ascii=False, sort_keys=True)
        key = hashlib.sha1((text + html.read_text(encoding="utf-8")).encode()).hexdigest()[:16]
        out = self.cache / f"overlay_{key}.mov"
        if not out.exists():
            comp_path = self.cache / "comp.json"
            comp_path.write_text(text, encoding="utf-8")
            render(comp_path, html, self.root / "05_Shared_Assets" / "fonts", out)
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
            if mode == "mute":
                continue
            speed = shot.get("speed", 1.0)
            lead, tail = a.get("lead", 0.0), a.get("tail", 0.0)
            start_src = max(shot["in"] - lead, 0.0)
            lead = shot["in"] - start_src
            af = CLEAN + (f",atempo={speed}" if speed != 1.0 else "")
            x = decode(shot["path"], start_src, (shot["out"] - start_src) + tail, af)
            t0 = shot["start"] - lead / speed
            if mode == "full":
                x = x * db(np.clip(SPEECH_LUFS - loudness(x), -6, 14))
                speech.append((shot["start"], shot["end"] + tail))
            else:
                env = np.full(len(x), db(a.get("bed_db", -18.0)), np.float32)
                for s, e in a.get("moments", []):
                    ms, me = int((s - start_src) / speed * SR), int((e - start_src) / speed * SR)
                    gain = db(np.clip(SPEECH_LUFS - loudness(x[ms:me]), -6, 14))
                    w = trapezoid(len(x), [(ms / SR, me / SR)], .15, .3)
                    env = np.maximum(env, env + (gain - env) * w)
                    speech.append((self.to_timeline(shot, s), self.to_timeline(shot, e)))
                x = x * env[:, None]
            add(camera, edge_fade(x, .12 if lead else .02, .25 if tail else .03), t0)

        vo_windows = merge([(t, t + len(x) / SR) for x, t in voices], .5)
        bus = camera * (1 - .5 * trapezoid(n, vo_windows, .15, .3))[:, None]
        for x, t in voices:
            add(bus, x, t)

        duck = trapezoid(n, merge(speech, 1.2), .25, .6)
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
            x = x[:len(slice_duck)] * db(BGM_DUCK_DB * slice_duck)[:, None]
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
    def limit(x):
        out = run_input(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "pipe:0",
                         "-af", f"alimiter=limit={LIMIT}:attack=3:release=80:level=0:latency=1",
                         "-f", "f32le", "pipe:1"], x.astype(np.float32).tobytes())
        y = np.frombuffer(out, np.float32).reshape(-1, 2).copy()
        return y[:len(x)] if len(y) >= len(x) else np.vstack([y, np.zeros((len(x) - len(y), 2), np.float32)])

    def next_output(self, stage):
        ep = self.dir.name.split("_")[0]
        renders = self.dir / "renders"
        renders.mkdir(exist_ok=True)
        v = 1
        while (renders / f"{ep}_{stage.capitalize()}_v{v:02d}.mp4").exists():
            v += 1
        return renders / f"{ep}_{stage.capitalize()}_v{v:02d}.mp4"

    def render_rough(self):
        base, mix = self.build_base(), self.build_mix()
        out = self.next_output("rough")
        win = self.spec["video_window"]
        W, H = self.fmt["w"], self.fmt["h"]
        fc = (f"color=c=0xdcc9a8:s={W}x{H}:r={self.fps}:d={self.duration:.3f}[bg];"
              f"[bg][0:v]overlay=0:{win['y']}:shortest=1,scale={W // 2}:{H // 2},format=yuv420p[v]")
        run(["ffmpeg", "-y", "-v", "error", "-i", str(base), "-i", str(mix), "-filter_complex", fc,
             "-map", "[v]", "-map", "1:a", "-t", f"{self.duration:.3f}", "-c:v", "h264_nvenc", "-preset", "p4",
             "-rc", "vbr", "-cq", "25", "-b:v", "0", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)])
        print(f"rough written: {out} ({self.duration:.2f}s)")


    def render_full(self):
        comp, sfx = self.resolve_graphics()
        base, overlay, mix = self.build_base(), self.build_overlay(comp), self.build_mix(sfx)
        out = self.next_output("full")
        win = self.spec["video_window"]
        W, H = self.fmt["w"], self.fmt["h"]
        fc = (f"color=c=0x2b2a28:s={W}x{H}:r={self.fps}:d={self.duration:.3f}[bg];"
              f"[bg][0:v]overlay=0:{win['y']}:shortest=1[b];"
              f"[1:v]scale=out_color_matrix=bt709:out_range=tv,format=yuva420p[g];"
              f"[b][g]overlay=0:0:eof_action=pass:format=yuv420,format=yuv420p[v]")
        run(["ffmpeg", "-y", "-v", "error", "-i", str(base), "-i", str(overlay), "-i", str(mix),
             "-filter_complex", fc, "-map", "[v]", "-map", "2:a", "-t", f"{self.duration:.3f}",
             "-c:v", "h264_nvenc", "-preset", "p6", "-tune", "hq", "-rc", "vbr", "-cq", "19", "-b:v", "14M",
             "-maxrate", "24M", "-bufsize", "28M", "-profile:v", "high", "-spatial-aq", "1", "-temporal-aq", "1",
             "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
             "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(out)])
        print(f"full written: {out} ({self.duration:.2f}s)")
        from qa_check import check
        check(out, self, comp)


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
