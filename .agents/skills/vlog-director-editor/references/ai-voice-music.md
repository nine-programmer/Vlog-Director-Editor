# AI voice and music

Read this file only when the user has asked the agent to make the voice or the music. Never offer these tools; the normal route is the order sheet in [audio-production-guide.md](./audio-production-guide.md). Both scripts spend the user's API credit, so say what you are about to generate before running them.

## Voice: Gemini TTS

Write `voice_lines.json` in the episode folder, then:

```bash
python <skill>/scripts/generate_voice.py --lines 04_Episodes/EP01_Name/voice_lines.json
```

```json
{"voice": "Aoede", "style": "friendly and playful, relaxed pace",
 "lines": [{"file": "EP01_VO01.wav", "text": "..."}]}
```

- Model `gemini-3.8-flash-tts` (the Flash-Lite TTS does not support Thai). WAV 24 kHz mono. Existing files are skipped.
- Generated lines often run about 1 s longer than estimated; use real lengths.
- Ask the user to listen to names and places; Whisper checks are not proof.

## Music: Lyria (instead of Suno)

```bash
python <skill>/scripts/generate_music.py --prompt "warm acoustic guitar, soft piano" --seconds 60 --out 04_Episodes/EP01_Name/music/EP01_BGM.mp3
```

- Always instrumental; never overwrites. `--clip` makes a cheaper 30 s draft.
- Output is loud (around -11.5 LUFS with peaks at full scale); the mix levels it.
- Carries an inaudible SynthID watermark; check Google's commercial terms before a monetised channel.

Model names change. If a script reports an unknown model, tell the user and ask before editing `MODEL` in the script.
