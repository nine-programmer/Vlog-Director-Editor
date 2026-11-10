# timeline.json

One file per episode drives the rough cut, the full render, QA, captions review and delivery. A complete working example is `assets/examples/timeline_example.json` (the EP01 pilot). Paths are relative to the episode folder; source clips are found by file name anywhere under `01_Raw_Footage/`.

## Times

Any time field accepts seconds on the episode timeline or a shot anchor:

```json
{"shot": "s5", "offset": 1.2}
```

Prefer anchors: when a shot's length changes, everything anchored to later shots moves with it.

## Top level

| Key | Meaning |
|---|---|
| `format` | `{"w": 1080, "h": 1920, "fps": 50}` vertical or `{"w": 1920, "h": 1080, "fps": 50}` horizontal |
| `video_window` | Where the video sits: vertical `{"y": 640, "h": 760}`; horizontal full frame `{"y": 0, "h": 1080}` |
| `style` | Style key from `assets/styles/styles.json` |
| `font` | Optional display font from that style's `font_options` |
| `shots` | Ordered list of shots (below) |
| `voiceovers` | `[{"file": "voice/EP01_VO01.wav", "t": <time>, "gain_db": 0}]` |
| `bgm` | `[{"file": "music/EP01_BGM_A.mp3", "t": <time>, "end": <time>, "in": 0, "fade_in": .3, "fade_out": 1}]`, may overlap for crossfades |
| `graphics` | Overlay cues (below) |
| `sfx` | Extra sounds: `[{"name": "shutter", "t": <time>, "gain_db": 0}]` |
| `tones`, `postmarks`, `route` | Scrapbook extras (below) |
| `master_trim` | `{"start": <time>, "end": <time>}`: part kept when building a master with `--trim` |

## Shots

```json
{"id": "s5", "src": "DJI_..._0021_D.MP4", "in": 4.4, "out": 12.3,
 "speed": 1.0, "hold": 1.0,
 "zoom": {"scale": 1.2, "cx": 0.72, "cy": 0.5},
 "punches": [{"at": 10.3, "scale": 1.3, "cx": 0.66, "cy": 0.5}],
 "audio": {"mode": "full", "lead": 0.5, "tail": 0.5, "bed_db": -18, "moments": [[16.5, 17.5]]}}
```

| Field | Meaning |
|---|---|
| `in`, `out` | Source seconds |
| `speed` | 0.5 for replay slow motion, 1.5-2 for speed ramps |
| `hold` | Freeze the last frame for N seconds |
| `zoom` | Whole-shot crop: `scale` (keep at most 1.4 on 1080p sources), focus `cx`, `cy` as 0-1 of the source frame |
| `punches` | Cut-zooms at source time `at`; each lasts until the next punch |
| `audio.mode` | `full`: speech, levelled to -16 LUFS and ducks music. `bed`: ambience at `bed_db`, with `moments` (source seconds) lifted to speech level. `mute`: silent (replays) |
| `audio.lead` / `tail` | J-cut (sound starts early) / L-cut (sound runs into the next shot), seconds |

Instant replay = a second shot of the same moment with `speed: 0.5`, a `zoom`, `audio.mode: mute`, a "replay" label and a `rewind` SFX.

## Graphics cues

Common fields: `type`, `t`, `end`, optional `x`, `y`, `ax` (0 left-anchored, 0.5 centred, 1 right), `tilt`, `color`, `sfx`. Omit `x`/`y` to use the style's default spot for that type; in vertical the defaults keep text out of the app's button areas.

| Type | Fields | Use |
|---|---|---|
| `speech` | `text` | What someone says in the clip |
| `voice` | `text` | Voiceover subtitle |
| `comment` | `text` | Editor's joke or remark (variety "PD caption") |
| `label` | `text` | Place or mission tag, usually top-left |
| `score` | `text` | Running gag scoreboard |
| `tag` | `text` | Name tag near a person |
| `impact` | `words`, `size`, `stagger` | Big punch words, one piece per word |
| `stamp` | `text` | Rubber-stamp verdict |
| `sticker` | `src`, `w`, `x`, `y`, `flip` | Image (AI art, props) |
| `march` | `src`, `w`, `y`, `from`, `to`, `count`, `spacing` | A line of stickers crossing the screen |
| `arrow` | `from`, `to` as `[x, y]` | Hand-drawn arrow drawing itself |
| `ring` | `x`, `y`, `rx`, `ry` | Hand-drawn circle around something |
| `transition` | `variant`, `color` | Style transition covering a cut; `t` about 0.3 s before the cut, `end` 0.3 s after. `tear` is an alias for the scrapbook tear |

Coordinates are pixels of the output frame (1080x1920 or 1920x1080).

## Scrapbook extras

```json
"tones": [{"t": 0, "color": "#dcc9a8"}, {"t": {"shot": "s12"}, "color": "#c3cdd2"}],
"postmarks": [{"t": 0, "lines": ["คีรีวง", "31 ต.ค."]}],
"route": {"y": 1760, "x1": 150, "x2": 930, "from": "คีรีวงแคมป์", "to": "ลานนับดาว",
          "progress": [{"t": 0, "p": 0}, {"t": {"shot": "s12"}, "p": 0.5}, {"t": 66.8, "p": 1}]}
```

## Mixing defaults

Speech -16 LUFS, music -20 LUFS when nobody talks and 11 dB lower under speech (ducking is computed from voiceovers, `full` shots and `moments`), master -14 LUFS with true peak at most -1 dB. SFX levels per sound are set in `render_episode.py` (`SFX_PEAK_DB`).
