"""Generate a supporting image (sticker, prop, background) with the OpenAI Images API.

Reads OPENAI_API_KEY from the project's .env at run time and never prints it.
Describe people in words only; never upload frames of real people, especially
children, unless the user has explicitly agreed.

Usage:
  python generate_image.py --prompt "..." --out 04_Episodes/EP01_Name/visuals/ant.png [--transparent]
"""
import argparse
import base64
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

from generate_voice import load_key

ENDPOINT = "https://api.openai.com/v1/images/generations"
MODELS = ["gpt-image-2", "gpt-image-1.5"]  # fall back when a model rejects an option


def request(key, body):
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(body).encode("utf-8"), method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.load(resp), None
    except urllib.error.HTTPError as e:
        return None, f"{e.code}: {e.read().decode('utf-8', 'replace')[:500]}"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--size", default="1024x1024")
    ap.add_argument("--quality", default="medium")
    ap.add_argument("--transparent", action="store_true")
    a = ap.parse_args()

    if a.out.exists():
        sys.exit(f"already exists, choose a new name: {a.out}")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    key = load_key(a.out.resolve().parent, "OPENAI_API_KEY")

    errors = []
    for model in MODELS:
        body = {"model": model, "prompt": a.prompt, "size": a.size, "quality": a.quality,
                "output_format": "png", "n": 1}
        if a.transparent:
            body["background"] = "transparent"
        data, err = request(key, body)
        if data:
            a.out.write_bytes(base64.b64decode(data["data"][0]["b64_json"]))
            print(f"wrote {a.out.name} with {model}")
            return
        errors.append(f"{model} -> {err}")
    sys.exit("image generation failed:\n" + "\n".join(errors))


if __name__ == "__main__":
    main()
