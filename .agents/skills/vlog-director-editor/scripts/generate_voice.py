"""Step 4: generate voiceover WAV files with Gemini TTS.

Reads GEMINI_API_KEY from the project's .env at run time and never prints it.
Existing files are skipped so a take the user already approved is not overwritten.

voice_lines.json:
  {"voice": "Aoede", "style": "friendly, playful", "lines": [{"file": "EP01_VO01.wav", "text": "..."}]}

Usage:
  python generate_voice.py --lines <voice_lines.json> [--out <dir>] [--voice NAME] [--only FILE]
"""
import argparse
import base64
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"
MODEL = "gemini-3.8-flash-tts"  # the Flash-Lite TTS model does not support Thai


def load_key(start, name="GEMINI_API_KEY"):
    for folder in [start, *start.parents]:
        env = folder / ".env"
        if env.is_file():
            for line in env.read_text(encoding="utf-8-sig").splitlines():
                key, sep, value = line.partition("=")
                if sep and key.strip() == name and value.strip():
                    return value.strip().strip("\"'")
            sys.exit(f"{name} is not set in {env}")
    sys.exit("no .env file found above the lines file")


def synthesize(key, text, voice, style):
    content = {"type": "text", "text": text}
    if style:
        content["annotations"] = [{"type": "speech_metadata", "style": style}]
    body = {
        "model": MODEL,
        "input": [{"type": "user_input", "content": [content]}],
        "response_format": {"type": "audio"},
        "generation_config": {"speech_config": [{"voice": voice}]},
    }
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(body).encode("utf-8"), method="POST",
        headers={"x-goog-api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
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
    ap.add_argument("--lines", required=True, type=Path)
    ap.add_argument("--out", type=Path, help="default: voice/ next to the lines file")
    ap.add_argument("--voice", help="override the voice in the lines file")
    ap.add_argument("--only", help="generate a single file name")
    a = ap.parse_args()

    spec = json.loads(a.lines.read_text(encoding="utf-8"))
    out = a.out or a.lines.resolve().parent / "voice"
    out.mkdir(parents=True, exist_ok=True)
    key = load_key(a.lines.resolve().parent)
    voice = a.voice or spec["voice"]

    for line in spec["lines"]:
        if a.only and line["file"] != a.only:
            continue
        target = out / line["file"]
        if target.exists():
            print(f"skip (already exists): {target.name}")
            continue
        target.write_bytes(synthesize(key, line["text"], voice, line.get("style", spec.get("style"))))
        print(f"wrote {target.name} with voice {voice}")


if __name__ == "__main__":
    main()
