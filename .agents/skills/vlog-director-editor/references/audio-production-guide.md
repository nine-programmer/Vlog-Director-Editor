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

## Writing the sheet

- **Voice line length:** Thai narration runs about 12-14 characters per second (count consonants and vowels on the line). Estimate each line from that and add 1 s, then plan the shots under it to be at least that long.
- **How much voiceover:** at most a third of the episode, in lines of 2-6 s. Never over a `full` shot or a `moment`.
- **Music length to ask for:** the stretch it covers plus 10 s. One or two music files per episode; a second one only when the place or mood changes.
- **Music style:** start from the starter styles below, change the instruments and tempo to fit the episode, and always end the style text with `instrumental`.

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

`init_project.py` generates a licence-free synth kit in `05_Shared_Assets/sfx/synth/`. Use these exact names in the timeline: `paper_slap`, `paper_tear`, `tape`, `stamp`, `pop`, `rewind`, `shutter`, `pen`, `hit`, `boing`, `ding`, `whoosh`, `boom`, `chime`.

Real recorded sounds can be added under `05_Shared_Assets/sfx/<source>/` with a `SOURCES.md`. They must be WAV files (convert with `ffmpeg -i in.ogg -ar 48000 out.wav`), and the file name without `.wav` becomes the SFX name, so names must be unique across the whole `sfx/` folder. Add recorded sounds only when the user asks for better ones. Check each site's current terms before downloading:
- [Kenney](https://kenney.nl/assets/category:Audio): reported CC0
- [Mixkit](https://mixkit.co/free-sound-effects/cartoon/): Mixkit licence
- Freesound: CC0 files only

The agent cannot hear the kit; ask the user whether it sounds cheap.

## Mix (automatic in render_episode.py)

Speech, voiceover and music are measured and levelled to the targets below, so files of any loudness can be dropped in. These are levels relative to each other before the final master gain.

| Layer | Target |
|---|---|
| Voiceover and speech | about -16 LUFS |
| Ambience (`bed`) | the cleaned camera sound turned down by `bed_db` (default -18 dB); not measured |
| Camera sound under a voiceover | a further 6 dB down |
| Music without speech | about -20 LUFS |
| Music under speech | 11 dB lower, with look-ahead ramps |
| Master | -14 LUFS, true peak at most -1 dB (limiter at -2.6 dBFS covers AAC overshoot) |

Camera audio is cleaned with `highpass`, `afftdn` and `acompressor`.
