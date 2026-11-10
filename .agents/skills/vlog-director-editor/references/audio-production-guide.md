# Audio

## Order sheet (audio_order.md, written in Thai)

The user should be able to make every file without guessing:

````markdown
# EP01: ใบสั่งงานเสียง

## 1. เสียงพากย์: สร้างที่ Google AI Studio
เปิด https://aistudio.google.com แล้วเลือกโหมดสร้างเสียงพูด (Gemini TTS) ใช้เสียงเดิมของคุณ
คำสั่งอารมณ์: พูดภาษาไทยแบบเล่าให้เพื่อนฟัง น้ำเสียงเป็นกันเอง

| บันทึกเป็นชื่อ | บท | ความยาวประมาณ |
|---|---|---|
| `EP01_VO01.wav` | ... | 4 วินาที |

**วางไฟล์ที่:** `04_Episodes/EP01_Name/voice/`

## 2. เพลง: สร้างที่ Suno
เข้าโหมด Advanced แล้วไม่ต้องใส่เนื้อเพลง ใส่แค่ข้อความในช่อง Style จะได้เพลงที่ไม่มีเสียงร้อง

### `EP01_BGM_A.mp3`: ใช้ 0:00–0:41
```text
<Suno style>
```
**วางไฟล์ที่:** `04_Episodes/EP01_Name/music/`

## 3. เช็กก่อนส่ง
- [ ] ชื่อเฉพาะออกเสียงถูก
- [ ] เพลงไม่มีเสียงร้อง
- [ ] ชื่อไฟล์ตรงทุกตัวอักษร
````

Suno no longer has an Instrumental switch: Advanced mode, empty lyrics, style only. Vocals would fight the speech.

## Naming

| Kind | Pattern | Example |
|---|---|---|
| Voiceover | `EPxx_VOnn.wav` | `EP01_VO02.wav` |
| Music | `EPxx_BGM.mp3`, several cues `EPxx_BGM_A.mp3` | `EP01_BGM_B.mp3` |

If Suno offers WAV, use it and change the extension.

## Starter Suno styles

- Playful comedy: `Playful pizzicato strings, ukulele, light woodblock, sneaky comedy, cartoon mischief, 110 BPM, instrumental`
- Bright: `Acoustic pop, ukulele, light whistling, soft bouncy drum beat, happy travel vlog, instrumental`
- Warm evening: `Warm acoustic guitar, soft piano, gentle golden hour, nostalgic travel diary, 80 BPM, instrumental`

## SFX

`init_project.py` generates a licence-free synth kit in `05_Shared_Assets/sfx/synth/` (paper slap, tear, tape, stamp, shutter, pen, pop, rewind, hit, boing, ding, whoosh, boom, chime). Real recorded sounds can be added under `05_Shared_Assets/sfx/<source>/` with a `SOURCES.md`; a file name becomes the SFX name. Check each site's current terms before downloading:
- [Kenney](https://kenney.nl/assets/category:Audio): reported CC0
- [Mixkit](https://mixkit.co/free-sound-effects/cartoon/): Mixkit licence
- Freesound: CC0 files only

The agent cannot hear the kit; ask the user whether it sounds cheap.

## Mix (automatic in render_episode.py)

Levels are measured first, because a multiplier like 1.35x means nothing without knowing the source level.

| Layer | Target |
|---|---|
| Voiceover and speech | about -16 LUFS |
| Ambience (`bed`) | about -18 dB after cleaning |
| Music without speech | about -20 LUFS |
| Music under speech | 11 dB lower, with look-ahead ramps |
| Master | -14 LUFS, true peak at most -1 dB (limiter at -2.6 dBFS covers AAC overshoot) |

Camera audio is cleaned with `highpass`, `afftdn` and `acompressor`.

## AI voice and music (only when the user asks)

Never offer these. Use them only when the user asks the agent to make the voice or music.

### Voice: Gemini TTS

Write `voice_lines.json` in the episode folder, then:

```bash
python scripts/generate_voice.py --lines 04_Episodes/EP01_Name/voice_lines.json
```

```json
{"voice": "Aoede", "style": "friendly and playful, relaxed pace",
 "lines": [{"file": "EP01_VO01.wav", "text": "..."}]}
```

- Model `gemini-3.8-flash-tts` (the Flash-Lite TTS does not support Thai). WAV 24 kHz mono. Existing files are skipped.
- Generated lines ran about 1 s longer than estimated in the pilot; use real lengths.
- Ask the user to listen to names and places; Whisper checks are not proof.

### Music: Lyria (instead of Suno)

```bash
python scripts/generate_music.py --prompt "warm acoustic guitar, soft piano" --seconds 60 --out 04_Episodes/EP01_Name/music/EP01_BGM.mp3
```

- Always instrumental; never overwrites. `--clip` makes a cheaper 30 s draft.
- Output is loud (about -11.5 LUFS, peak +0.1 dB in tests); the mix levels it.
- Carries an inaudible SynthID watermark; check Google's commercial terms before a monetised channel.

If a model name changes, edit `MODEL` in the script.
