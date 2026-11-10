# timeline.json

One file per episode drives the rough cut, the full render, QA, captions review and delivery. A complete example is `assets/examples/timeline_example.json`; read it for shape (its clip, voice and music files are placeholders, so it does not render). Paths are relative to the episode folder; source clips are found by file name anywhere under `01_Raw_Footage/`, so clip names must be unique.

`format`, `video_window` and `shots` are required; everything else is optional. One timeline is one format and one style. Run `validate_timeline.py` after every edit. Unknown top-level and shot fields are errors; unknown fields on a graphics cue are warnings, so read the warnings too.

## Times: two clocks

| Clock | Used by |
|---|---|
| **Source seconds** (time inside the original clip, as in transcripts and `frames.py`) | `in`, `out`, `punches.at`, `speed[].at`, `audio.moments` |
| **Episode seconds** (time in the finished video) | every `t` and `end` of graphics, voiceovers, music, SFX, `music_cuts`, `tones`, `postmarks`, `route`, `master_trim` |

Write episode times as an anchor to a shot, never as plain seconds, so they move when shots change:

```json
{"shot": "s5", "src": 10.3}      the moment source second 10.3 of shot s5 plays
{"shot": "s5", "offset": 1.2}    1.2 episode seconds after shot s5 starts
{"shot": "s5"}                   the start of shot s5
```

- Use `src` for anything tied to what happens in the clip (a spoken line, an action). It stays correct on sped-up, slowed and ramped shots. This is how a transcript time becomes a caption time: copy the transcript's `start` into `src`.
- Use `offset` for things tied to the cut itself (a label at the start of a scene, a transition). A negative offset means before the shot starts. A freeze (`hold`) is reached with `offset`, because it comes after the last source frame.
- `src` and `offset` may be combined; the offset is added after the conversion.

## Top level

| Key | Meaning |
|---|---|
| `format` | `{"w": 1080, "h": 1920, "fps": 50}` vertical or `{"w": 1920, "h": 1080, "fps": 50}` horizontal. Set `fps` to the footage's frame rate from `scan_report.md` (25, 30, 50 or 60; round 29.97 to 30 and 59.94 to 60). With mixed footage use the rate of most clips |
| `video_window` | Where the picture sits, full width, for the whole episode. Use exactly `{"y": 640, "h": 760}` for vertical and `{"y": 0, "h": 1080}` for horizontal; the default text positions are tuned to these. In vertical, shots are cropped to fill the window, centred on `zoom.cx`/`cy` |
| `grade` | Colour look for every shot (see "Colour grade"). Always set one |
| `style` | Style key from `assets/styles/styles.json` |
| `font` | Optional display font from that style's `font_options` |
| `shots` | Ordered list of shots (below) |
| `voiceovers` | `[{"file": "voice/EP01_VO01.wav", "t": <time>, "gain_db": 0}]` |
| `bgm` | `[{"file": "music/EP01_BGM_A.mp3", "t": <time>, "end": <time>, "in": 0, "fade_in": .3, "fade_out": 1}]`. `in` is where to start inside the music file. Without `end` it plays to the end of the episode |
| `music_cuts` | `[{"t": <time>, "end": <time>}]`: the music drops to silence for that span and slams back (see "Music stop") |
| `graphics` | Overlay cues (below) |
| `sfx` | Extra sounds: `[{"name": "shutter", "t": <time>, "gain_db": 0}]` |
| `tones`, `postmarks`, `route` | Scrapbook extras (below) |
| `master_trim` | `{"start": <time>, "end": <time>}`: the part kept when building a master with `--trim`. `start` is the first shot after the hook; `end` is the end of the last story shot |

## Shots

```json
{"id": "s5", "src": "CLIP_0003.MP4", "in": 4.4, "out": 12.3,
 "speed": 1.0, "hold": 1.0, "fill": false, "grade": "warm",
 "zoom": {"scale": 1.2, "cx": 0.72, "cy": 0.5},
 "move": {"scale": 1.35, "cx": 0.66, "cy": 0.5, "ease": "inout"},
 "punches": [{"at": 10.3, "scale": 1.3, "cx": 0.66, "cy": 0.5, "dur": 0.8}],
 "audio": {"mode": "full", "lead": 0.5, "tail": 0.5, "bed_db": -18, "moments": [[16.5, 17.5]]}}
```

| Field | Meaning |
|---|---|
| `id`, `src` | Unique shot id used by anchors; source file name |
| `in`, `out` | Source seconds. `out` must not pass the end of the clip |
| `speed` | A number (default 1) for a constant speed, 0.5 to 4: 0.5 for replay slow motion, 1.5-2 to speed up; sound keeps its pitch. Below 0.5 the shot must be `mute`. Slow motion is only smooth when the clip's frame rate is higher than the timeline's `fps` times the speed (a 50 fps clip at 0.5 on a 25 fps timeline); otherwise frames repeat, which is acceptable for a short replay. Or a ramp: a list of at least two key points `[{"at": 11.0, "v": 2.5}, {"at": 12.6, "v": 2.5}, {"at": 13.1, "v": 1}]`, where `at` is source seconds inside the shot and `v` the speed there. Speed glides in a straight line between points and holds the first and last values outside them. Sound follows a ramp with its pitch, like tape, so use `mute` or `bed` and add a `whoosh` in `sfx` |
| `hold` | Freeze the last frame for N seconds. Camera sound stops during the freeze; music and voiceover continue |
| `zoom` | Whole-shot crop: `scale` (1 or more), focus `cx`, `cy` as 0-1 of the source picture. On 1080p footage keep `scale` at most 1.4 in horizontal and 1.8 in the vertical window (the window already shows the picture smaller, so there is room); 4K footage can go to double those |
| `move` | Animated zoom or pan: the framing glides from `zoom` (or the full picture) at the start of the shot to `move` at the end. Fields `scale`, `cx`, `cy` like `zoom`; missing ones keep the starting value. `ease`: `inout` (default), `linear`, `in`, `out`. A freeze stays on the end framing. Not allowed together with `punches`; it renders several times slower than a static shot |
| `punches` | Cut-zooms at source time `at`. A punch keeps any of `scale`, `cx`, `cy` it does not set from the framing before it. With `dur` (seconds of source time, 0.5-1.2 is typical) it snaps back to the earlier framing afterwards; without `dur` it lasts until the next punch or the end of the shot |
| `fill` | `true` makes this shot fill the whole frame in a vertical episode, hiding the style's bars for its duration (see "Full-frame shots"). Ignored in horizontal |
| `grade` | Colour look for this shot only; replaces the top-level `grade` |
| `audio.mode` | See "Choosing the audio mode". Default `bed` |
| `audio.bed_db` | Level of the ambience in `bed` mode, a plain gain on the cleaned camera sound. Default -18 (under voice or music). Use -10 to -6 on a scenery shot where the natural sound is the point |
| `audio.moments` | `[[start, end]]` in source seconds: spans inside a `bed` shot lifted to speech level (a laugh, a shout, one line) |
| `audio.lead` / `tail` | J-cut (sound starts N seconds before the picture) / L-cut (sound runs N seconds into the next shot). 0.3-0.6 is typical. A `lead` on the first shot of the episode has nothing to play over and is cut off |

### Choosing the audio mode

| Mode | Use when | What happens |
|---|---|---|
| `full` | The viewer must hear the speech and it fills most of the shot. Every shot with a `speech` caption is `full`, or `bed` with `moments` over the line | Levelled to speech loudness; music ducks 11 dB for the whole shot |
| `bed` | Nobody says anything that matters | Ambience at `bed_db`; `moments` lift short sounds |
| `mute` | Replays, speed ramps, shots below 0.5 speed | Silent |

Do not make every shot `full`: the music would stay ducked for the whole episode. A clip with no sound track is treated as `mute` and the renderer prints a warning; `scan_report.md` shows which clips have sound. Camera sound is also lowered by about 6 dB while a voiceover plays.

### Motion recipes

- **Slow push-in** (tension, emotion, scenery): `"move": {"scale": 1.12}` over a 3-6 s shot. Keep it gentle: 1.08-1.15 reads as cinematic, more reads as a mistake.
- **Pan across a wide view**: `"zoom": {"scale": 1.25, "cx": 0.3}, "move": {"cx": 0.7}`.
- **Pull-out reveal**: `"zoom": {"scale": 1.35, "cx": 0.6, "cy": 0.45}, "move": {"scale": 1.0}`.
- **Punch on the punchline**: `"punches": [{"at": <source time of the word>, "scale": 1.3, "cx": .., "cy": .., "dur": 0.8}]`, with an `impact` cue and its sound at the same moment.
- **Speed ramp into a moment**: fast until just before the action, then glide to normal over 0.3-0.6 s of source time, as in the `speed` example above.
- **Ramp-matched cut**: shot A ramps up to 3 in its last 0.3 s, shot B starts at 3 and settles to 1 in its first 0.3 s, with a `whoosh` on the cut.
- **Instant replay**: a second shot of the same moment with `speed: 0.5`, a tighter `zoom`, `audio.mode: mute`, a label saying it is a replay and a `rewind` SFX at its start.
- Use moves on a few chosen shots. If every shot drifts, none of them means anything.

### Full-frame shots

In a vertical episode the picture normally sits in `video_window` with the style's bars above and below. A shot with `"fill": true` covers the whole 1080x1920 frame instead: the bars, tape, route line and postmark disappear for that shot and come back at the next cut. Use it for one to three peak moments per episode (a close-up, a reveal).

- The crop keeps only the middle third of a horizontal clip; aim it with `zoom.cx`/`cy`, and check a frame to be sure the subject is inside.
- A 1080p source is enlarged 1.78x and looks soft; prefer 4K clips or tight close-ups, and do not add `zoom.scale` on top.
- Captions keep their usual positions and now sit over the picture. The QA frame sheet includes them; check that no text covers a face.

### Colour grade

`grade` is a preset name or an object:

```json
"grade": "warm"
"grade": {"preset": "natural", "brightness": 0.03, "contrast": 1.05, "saturation": 1.1, "warmth": 0.3}
```

| Preset | Look |
|---|---|
| `none` | Untouched |
| `natural` | A little more contrast and colour |
| `vivid` | Strong colour and contrast |
| `warm` | Golden cast |
| `cool` | Blue cast |
| `film` | Lifted blacks, softer colour, slight warmth |
| `bw` | Black and white |

Choose the episode's grade in this order and record it in `03_Style/Style_Selected.md`:

1. The style's pairing: variety and comic `vivid`; scrapbook `warm`; soft and journal `film`.
2. If frames with that grade look wrong (skin too orange, sky clipped, colours shouting), use `natural`.
3. Use `cool` for a whole episode only when it is about water, rain or early morning. Use `bw` on single shots only (a flashback, a joke beat). Use `none` only when the user says the footage is already graded.

Object fields: `brightness` (-0.1 to 0.1), `contrast` and `saturation` (1 is unchanged, stay within 0.8-1.3), `warmth` (-1 cool to 1 warm). After the top-level grade, give a single shot its own `grade` only when it visibly does not match its neighbours (another camera, shade against sun). Judge by looking at rough-cut frames next to each other, and ask the user to confirm skin tones; never grade from numbers alone. Footage shot in a log or HDR profile looks flat and is not corrected here; tell the user.

## Graphics cues

Every cue needs `type`, `t` and `end`, and `end` must be later than `t`. Text cues get an `id` (`c01`, ...) from `captions.py export`; keep them.

| Type | Fields | Use | On screen |
|---|---|---|---|
| `speech` | `text` | What someone says in the clip | From the line's start to its end plus 0.2 s; at least 1 s |
| `voice` | `text` | Voiceover subtitle | From the voiceover's `t` for the length of the file |
| `comment` | `text` | Editor's joke or remark | 1.5-3 s |
| `label` | `text` | Place or mission tag, top-left | The whole scene, or 2-4 s |
| `score` | `text` | Running gag scoreboard | 1.5-3 s |
| `tag` | `text`, `x`, `y` | Name tag next to a person; always give `x` and `y` | 2-3 s |
| `impact` | `words`, `size`, `stagger` | Big punch words, one piece per word; 1-3 words | 1.2-2.5 s |
| `stamp` | `text` | Rubber-stamp verdict, 1-2 words | To the end of the shot, at least 1.2 s |
| `sticker` | `src`, `w`, `x`, `y`, `flip` | Image (AI art, props) | 2-4 s |
| `march` | `src`, `w`, `y`, `from`, `to`, `count`, `spacing` | A line of stickers crossing the screen | 2-4 s |
| `arrow` | `from`, `to` as `[x, y]` | Hand-drawn arrow drawing itself in 0.5 s | 1.5-3 s |
| `ring` | `x`, `y`, `rx`, `ry` | Hand-drawn circle drawing itself in 0.6 s | 1.5-3 s |
| `transition` | `variant`, `color` | Style transition covering a cut | `t` 0.3 s before the cut, `end` 0.3 s after |

Rules that keep cues from colliding:

- At most one of `impact`, `score` and `stamp` on screen at a time; they share one spot.
- Never a `speech` and a `voice` cue at the same time; they share one spot.
- Leave 0.05-0.1 s between one speech cue and the next.
- Start an `impact` or `stamp` 0.1-0.15 s before the word or action it hits: `t` is when it starts to fly in, and it lands (with its sound) a moment later.

### Text

- One line holds about 22 Thai characters in vertical and 45 in horizontal (count consonants and vowels on the line, not marks above and below). A longer caption is shrunk to fit, the validator warns, and QA fails it below 80% size. Split a long line into two cues one after the other, or break it into two lines with `<br>`.
- Reading speed: at most 18 characters per second (QA fails above); aim for 12.
- Text is HTML. `<br>` starts a second line (two lines at most). `<span class=hl>คำ</span>` shows a word in the style's highlight colour; use it on at most one word or phrase per caption. Write `&lt;` and `&amp;` for a literal `<` or `&`.

### Position and look

Optional on every cue: `x`, `y`, `ax` (0 left-anchored, 0.5 centred, 1 right), `tilt` (degrees), `color`, `sfx`. Coordinates are pixels of the output frame (1080x1920 or 1920x1080).

- Omit `x`/`y` on text cues, `impact` and `stamp`: the style puts them in its own spot, clear of the app's buttons in vertical. Set them only to move a cue off a face.
- `arrow`, `ring`, `sticker`, `march` and `tag` need real positions. Read them from the rough cut, not from the source clip:
  ```bash
  python <skill>/scripts/frames.py --src 04_Episodes/EPxx_Name/renders/EPxx_Rough_v01.mp4 --start 12 --end 14 --every 0.5 --width 540 --grid 100
  ```
  The grid is labelled in rough-cut pixels; the rough cut is half size, so multiply by 2.
- In vertical, keep everything out of the top 110 px, the area below y 1560 and the right-hand column x 960+ between y 900 and 1560 (app interface; estimates).
- Defaults when omitted: `impact.stagger` 0.22 s between words; `impact.size` 160 scrapbook, 170 variety, 180 comic, 130 journal, 120 soft; `stamp` tilt -9; `march.count` 4 and `spacing` 150; `ring.rx` 120, `ry` 90. `march.from` and `to` are x positions of the first sticker and may be off-screen (for example -200 to 1300).
- `transition.variant` is the style's own and can be omitted: `tear` scrapbook, `whip` variety, `burst` comic, `page` journal, `fade` soft. Shots always hard-cut underneath; there is no cross-dissolve. Transitions draw above everything, including full-frame shots.

`color` changes a different part in each style:

| Style | speech, voice | comment, label, score, tag | impact words | Speaker colours to use |
|---|---|---|---|---|
| scrapbook | paper colour | paper colour | ignored | `#f5ebdd`, `#cfe6df`, `#f6d9a0` |
| variety | text colour | box colour | text colour | `#ffffff`, `#ffe14d`, `#8fe3ff` |
| comic | box colour | box colour | text colour | `#ffffff`, `#fff6c8`, `#cfeaff` |
| journal | text colour | text colour (label and score ignore it) | text colour | `#fff8e7`, `#ffe3b8`, `#bfe3ff` |
| soft | text colour | text colour | text colour | `#ffffff`, `#ffe9c9`, `#cfe4ff` |

`stamp` ignores `color` in every style. On `arrow` and `ring` it is the line colour (default dark in scrapbook, variety and comic, so set a light colour over dark footage). On `transition` it is the panel colour. Colour speech by speaker only when two or more people talk in the episode: ask the user who each voice is, give each person one colour from the row above, and keep it for the whole episode.

### Sounds

Each style plays a default sound for most cue types (the table is in `styles.json`). Override it on a cue with `"sfx": "<name>"`, or silence it with `"sfx": ""`. Exact names in the built-in kit:

`paper_slap`, `paper_tear`, `tape`, `stamp`, `pop`, `rewind`, `shutter`, `pen`, `hit`, `boing`, `ding`, `whoosh`, `boom`, `chime`

Repeated small sounds get tiring: when three or more comments, labels or tags come within 10 s, silence all but the first.

## Music

- One or two music files per episode. Change music only at a change of place or mood, overlapping the two by 0.5-1 s (`end` of the first after `t` of the second).
- The last file runs to the end with `fade_out` 1-1.5 s. Music is not looped: a file shorter than its slot leaves silence and the renderer warns.
- A voiceover goes on a `bed` or `mute` shot. QA fails a voiceover that overlaps real speech (`full` shots and `moments`) by more than 0.3 s.

### Music stop

`"music_cuts": [{"t": {"shot": "s9", "src": 31.2}, "end": {"shot": "s9", "src": 31.8}}]` drops the music to silence for 0.3-0.8 s so a line or a reaction lands in the quiet, then brings it straight back. Use it once or twice per episode, on the biggest joke or reveal, starting about 0.2 s before the line.

## Scrapbook extras

Only the scrapbook style draws these; other styles ignore them.

```json
"tones": [{"t": 0, "color": "#dcc9a8"}, {"t": {"shot": "s12"}, "color": "#c3cdd2"}],
"postmarks": [{"t": 0, "lines": ["ชื่อสถานที่", "วันที่"]}],
"route": {"y": 1760, "x1": 150, "x2": 930, "from": "จุดเริ่ม", "to": "จุดหมาย",
          "progress": [{"t": 0, "p": 0}, {"t": {"shot": "s12"}, "p": 0.5}, {"t": {"shot": "s15", "offset": 3}, "p": 1}]}
```

- `tones`: paper colour of the bars from each time on; change it at a change of place. Keep to pale paper colours.
- `postmarks`: a round stamp in the top-right corner with one or two short lines.
- `route`: a dotted trip line with a start dot, an end pin and a marker that moves with `progress` (`p` from 0 to 1). Vertical only, in the bottom bar at `y` 1700-1780. The app's own caption can cover part of it there, so it is decoration: never put information the viewer needs in the route.

## Mixing defaults

These are relative levels before the final master gain: speech -16 LUFS, music -20 LUFS when nobody talks and 11 dB lower under speech (ducking is computed from voiceovers, `full` shots and `moments`), then the whole mix is brought to -14 LUFS with true peak at most -1 dB. SFX levels per sound are set in `render_episode.py` (`SFX_PEAK_DB`); adjust one with `gain_db` on the cue's entry in `sfx`.
