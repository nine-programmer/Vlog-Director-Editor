"""Photos as shots: an upright, right-sized copy of the photo and the slow move over it.

Used by render_episode.py, make_style_preview.py and scan_footage.py. The original in
01_Raw_Footage is only read.
"""
import hashlib
from pathlib import Path

from PIL import Image, ImageOps

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
SUPERSAMPLE = 2.6       # source pixels per output pixel at scale 1, so a slow move stays smooth
MAX_CANVAS = 24e6       # pixels; a larger canvas only makes the render slower
DEFAULT_PUSH = 1.08     # a photo with no "move" still drifts in by this much
EASES = {"linear": "P", "inout": "P*P*(3-2*P)", "out": "(1-(1-P)*(1-P))", "in": "P*P"}


def is_image(path):
    return Path(path).suffix.lower() in IMAGE_EXT


def upright_size(path):
    """Width and height as the photo is meant to be seen (EXIF rotation applied)."""
    with Image.open(path) as im:
        w, h = im.size
        return (h, w) if im.getexif().get(0x0112, 1) in (5, 6, 7, 8) else (w, h)


def prepare(path, cache, vw, vh):
    """Write an upright copy on a canvas shaped like the picture area (vw x vh) and return its geometry.

    The photo sits centred on the canvas; W, H is its size there and ox, oy its corner. A move may
    only look at the photo itself, never at the canvas around it.
    """
    path = Path(path)
    w0, h0 = upright_size(path)
    ar = vw / vh
    f = min(1.0, SUPERSAMPLE * vw / min(w0, h0 * ar))
    for _ in range(2):
        W, H = max(int(round(w0 * f)), 2), max(int(round(h0 * f)), 2)
        cw, ch = (W, W / ar) if W / H > ar else (H * ar, H)
        cw, ch = int(round(cw / 2)) * 2, int(round(ch / 2)) * 2
        if cw * ch <= MAX_CANVAS:
            break
        f *= (MAX_CANVAS / (cw * ch)) ** .5
    ox, oy = (cw - W) // 2, (ch - H) // 2
    st = path.stat()
    key = hashlib.sha1(f"{path}|{st.st_size}|{st.st_mtime_ns}|{cw}x{ch}|{W}x{H}".encode()).hexdigest()[:16]
    out = Path(cache) / f"{key}.png"
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(path) as im:
            im = ImageOps.exif_transpose(im).convert("RGB").resize((W, H), Image.LANCZOS)
        canvas = Image.new("RGB", (cw, ch), (0, 0, 0))
        canvas.paste(im, (ox, oy))
        canvas.save(out, compress_level=1)
    return {"path": out, "W": W, "H": H, "ox": ox, "oy": oy, "cw": cw, "ch": ch}


def default_move(zoom):
    """The move a photo gets when the timeline gives none: a small push-in on the same centre."""
    return {"scale": round(zoom.get("scale", 1.0) * DEFAULT_PUSH, 4), "ease": "linear"}


def move_filter(geo, vw, vh, fps, start, end, ease, frames, total, offset=0):
    """ffmpeg filters that turn the prepared still into `frames` frames of a move.

    start and end are framings {scale, cx, cy}. The move runs over `total` frames and this piece
    begins `offset` frames into it, so a shot and the tail it lends to a dissolve are one move.
    """
    W, H, ox, oy, cw = geo["W"], geo["H"], geo["ox"], geo["oy"], geo["cw"]
    ar = vw / vh
    r = cw / min(W, H * ar)
    p = EASES[ease].replace("P", f"min((on+{offset})/{max(total - 1, 1)},1)")
    lerp = lambda a, b: f"({a:.5f}+({b - a:.5f})*{p})"
    z = f"{r:.5f}*{lerp(start['scale'], end['scale'])}"
    px = f"({ox}+{W}*{lerp(start['cx'], end['cx'])})"
    py = f"({oy}+{H}*{lerp(start['cy'], end['cy'])})"
    zx = f"max({ox},min({px}-iw/zoom/2,{ox + W}-iw/zoom))"
    zy = f"max({oy},min({py}-ih/zoom/2,{oy + H}-ih/zoom))"
    return (f"scale=out_color_matrix=bt709:out_range=tv,format=yuv444p,"
            f"zoompan=z='{z}':x='{zx}':y='{zy}':d={frames}:s={vw}x{vh}:fps={fps},unsharp=5:5:0.3")
