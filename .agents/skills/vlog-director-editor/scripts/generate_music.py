"""Generate instrumental background music with Google Lyria (Gemini API).

Use only when the user explicitly asks the agent to make the music. The normal
route is the user creating music in Suno.

Reads GEMINI_API_KEY from the project's .env at run time and never prints it.
An existing output file is never overwritten.

Usage:
  python generate_music.py --prompt "warm acoustic guitar" --seconds 60 --out music/EP01_BGM.mp3
"""
import argparse
import base64
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

from generate_voice import load_key

ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"
API_REVISION = "2026-05-20"
MODEL = "lyria-3.5"
CLIP_MODEL = "lyria-3-clip-preview"  # always 30 seconds, cheaper for trying a direction


def generate(key, model, prompt):
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps({"model": model, "input": prompt}).encode("utf-8"), method="POST",
        headers={"x-goog-api-key": key, "Content-Type": "application/json", "Api-Revision": API_REVISION})
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"Gemini API error {e.code}: {e.read().decode('utf-8', 'replace')[:600]}")
    audio = [c for step in data.get("steps", []) if step.get("type") == "model_output"
             for c in step.get("content", []) if c.get("type") == "audio"]
    if not audio:
        sys.exit("Gemini API returned no audio")
    return base64.b64decode(audio[-1]["data"])


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True, help="music style description")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--seconds", type=int, default=60, help="target length, ignored by --clip")
    ap.add_argument("--clip", action="store_true", help="make a 30-second draft with the clip model")
    a = ap.parse_args()

    if a.out.exists():
        sys.exit(f"already exists, choose a new name: {a.out}")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    key = load_key(a.out.resolve().parent)

    model = CLIP_MODEL if a.clip else MODEL
    length = "" if a.clip else f" Length about {a.seconds} seconds."
    a.out.write_bytes(generate(key, model, f"{a.prompt}.{length} Instrumental only, no vocals."))
    print(f"wrote {a.out.name} with {model}")


if __name__ == "__main__":
    main()
