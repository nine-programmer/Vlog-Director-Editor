# timeline.json

One file per episode drives the rough cut, the full render, QA, captions review and delivery. A complete example is `assets/examples/timeline_example.json` (the EP01 pilot; read it for shape, it does not render outside that project). Paths are relative to the episode folder; source clips are found by file name anywhere under `01_Raw_Footage/`.

`format`, `video_window` and `shots` are required; everything else is optional. One timeline is one format and one style. Run `validate_timeline.py` after every edit: unknown or misspelt fields are errors, not silently ignored.

## Times

Any time field accepts seconds on the episode timeline or a shot anchor:

```json
{"shot": "s5", "offset": 1.2}
```

Prefer anchors: when a shot's length changes, everything anchored to later shots moves with it.

## Top level

| Key | Meaning |
|---|---|
| `format` | `{"w": 1080, "h": 1920, "fps": 50}` vertical or `{"w": 1920, "h": 1080, "fps": 50}` horizontal. Set `fps` to the footage's frame rate from `scan_report.md` (25, 30, 50 or 60; round 29.97 to 30 and 59.94 to 60). With mixed footage use the rate of most clips |
| `video_window` | Where the video sits in the frame, full width, for the whole episode: `y` is its top edge and `h` its height in pixels. Vertical `{"y": 640, "h": 760}` (shots are cropped to fill it, centred on `zoom.cx`/`cy`); horizontal full frame `{"y": 0, "h": 1080}` |
| `grade` | Colour look for every shot: a preset name or an object (see "Colour grade"). No grade when omitted |
| `style` | Style key from `assets/styles/styles.json`; `scrapbook` when omitted |
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
 "speed": 1.0, "hold": 1.0, "fill": false, "grade": "warm",
 "zoom": {"scale": 1.2, "cx": 0.72, "cy": 0.5},
 "move": {"scale": 1.35, "cx": 0.66, "cy": 0.5, "ease": "inout"},
 "punches": [{"at": 10.3, "scale": 1.3, "cx": 0.66, "cy": 0.5}],
 "audio": {"mode": "full", "lead": 0.5, "tail": 0.5, "bed_db": -18, "moments": [[16.5, 17.5]]}}
```

| Field | Meaning |
|---|---|
| `in`, `out` | Source seconds |
| `id`, `src` | Unique shot id used by anchors; source file name |
| `speed` | A number (default 1) for a constant speed: 0.5 for replay slow motion, 1.5-2 to speed up; sound keeps its pitch. Or a ramp: a list of key points `[{"at": 11.0, "v": 2.5}, {"at": 12.6, "v": 2.5}, {"at": 13.1, "v": 1}]`, where `at` is source seconds inside the shot and `v` the speed there. Speed glides in a straight line between points and holds the first and last values outside them. Sound follows a ramp with its pitch, like tape, so use `mute` or `bed` and cover it with a `whoosh` |
| `hold` | Freeze the last frame for N seconds |
| `zoom` | Whole-shot crop: `scale` (keep at most 1.4 on 1080p sources), focus `cx`, `cy` as 0-1 of the source frame |
| `move` | Animated zoom or pan: the framing glides from `zoom` (or the full picture) at the start of the shot to `move` at the end. Fields `scale`, `cx`, `cy` like `zoom`; missing ones keep the starting value. `ease`: `inout` (default), `linear`, `in`, `out`. A freeze (`hold`) stays on the end framing. Not allowed together with `punches`; it renders several times slower than a static shot |
| `punches` | Cut-zooms at source time `at`; each jumps to its framing and lasts until the next punch |
| `fill` | `true` makes this shot fill the whole frame in a vertical episode, hiding the style's bars for its duration (see "Full-frame shots"). Ignored when the window already covers the frame |
| `grade` | Colour look for this shot only; replaces the top-level `grade` |
| `audio.mode` | Default `bed`. `full`: speech, levelled to -16 LUFS and ducks music. `bed`: ambience at `bed_db`, with `moments` (source seconds) lifted to speech level. `mute`: silent (replays) |
| `audio.lead` / `tail` | J-cut (sound starts early) / L-cut (sound runs into the next shot), seconds |

### Motion recipes

- **Slow push-in** (tension, emotion, scenery): `"move": {"scale": 1.12}` over a 3-6 s shot. Keep it gentle: 1.08-1.15 reads as cinematic, more reads as a mistake.
- **Pan across a wide view**: `"zoom": {"scale": 1.25, "cx": 0.3}, "move": {"cx": 0.7}`.
- **Pull-out reveal**: `"zoom": {"scale": 1.35, "cx": 0.6, "cy": 0.45}, "move": {"scale": 1.0}`.
- **Speed ramp into a moment**: fast until just before the action, then glide to normal over 0.3-0.6 s of source time, as in the `speed` example above.
- Use moves on a few chosen shots. If every shot drifts, none of them means anything.

### Full-frame shots

In a vertical episode the picture normally sits in `video_window` with the style's bars above and below. A shot with `"fill": true` covers the whole 1080x1920 frame instead: the bars, tape, route line and postmark disappear for that shot and come back at the next cut. Use it for one to three peak moments per episode (a close-up, a reveal).

- The crop keeps only the middle third of a horizontal clip; aim it with `zoom.cx`/`cy`, and check a frame to be sure the subject is inside.
- A 1080p source is enlarged 1.78x and looks soft; prefer 4K clips or tight close-ups, and do not add `zoom.scale` on top.
- Captions keep their usual positions and now sit over the picture, so check the QA frame sheet for text over faces.

### Colour grade

`grade` is a preset name or an object:

```json
"grade": "warm"
"grade": {"preset": "natural", "brightness": 0.03, "contrast": 1.05, "saturation": 1.1, "warmth": 0.3}
```

| Preset | Look | Suits |
|---|---|---|
| `none` | Untouched | Footage that already looks right |
| `natural` | A little more contrast and colour | Safe default for phone and action-camera clips |
| `vivid` | Strong colour and contrast | variety, comic |
| `warm` | Golden cast | scrapbook, soft, evening light |
| `cool` | Blue cast | Water, rain, early morning |
| `film` | Lifted blacks, softer colour, slight warmth | soft, journal |
| `bw` | Black and white | A flashback or a joke beat, one shot at a time |

Object fields: `brightness` (-0.1 to 0.1), `contrast` and `saturation` (1 is unchanged, stay within 0.8-1.3), `warmth` (-1 cool to 1 warm). Set one top-level grade for the episode, then fix single shots that do not match (another camera, shade against sun) with their own `grade`. Judge by looking at frames from the rough cut next to each other, and ask the user to confirm skin tones; never grade from numbers alone.

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
| `transition` | `variant`, `color` | Style transition covering a cut; `t` about 0.3 s before the cut, `end` 0.3 s after. Omit `variant` to get the style's own transition. Shots always hard-cut underneath; there is no cross-dissolve. Transitions draw above everything, including full-frame shots. Type `tear` is an older alias of `transition` |

Coordinates are pixels of the output frame (1080x1920 or 1920x1080).

Every cue needs `type`, `t` and `end`. Text cues get an `id` (`c01`, ...) from `captions.py export`; keep them.

## Scrapbook extras

Only the scrapbook style draws these; other styles ignore them.

```json
"tones": [{"t": 0, "color": "#dcc9a8"}, {"t": {"shot": "s12"}, "color": "#c3cdd2"}],
"postmarks": [{"t": 0, "lines": ["คีรีวง", "31 ต.ค."]}],
"route": {"y": 1760, "x1": 150, "x2": 930, "from": "คีรีวงแคมป์", "to": "ลานนับดาว",
          "progress": [{"t": 0, "p": 0}, {"t": {"shot": "s12"}, "p": 0.5}, {"t": 66.8, "p": 1}]}
```

## Mixing defaults

Speech -16 LUFS, music -20 LUFS when nobody talks and 11 dB lower under speech (ducking is computed from voiceovers, `full` shots and `moments`), master -14 LUFS with true peak at most -1 dB. SFX levels per sound are set in `render_episode.py` (`SFX_PEAK_DB`).
