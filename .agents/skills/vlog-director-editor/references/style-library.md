# Style library

Five styles ship ready to render. Each is a file in `assets/styles/<key>.js` driven by the shared `engine.js`, with fonts, default SFX and Thai labels in `assets/styles/styles.json`. The preview page and the renderer use the same code, so what the user picks is what renders.

Research notes are marked **From sources** (with links) or **Working defaults** (our own starting points). Learn the grammar of each look; never copy a show's logo, characters or assets.

## Choosing

| Footage is mostly | Offer |
|---|---|
| Jokes from speech and reactions | variety, comic |
| A trip across places, food, family memories | scrapbook, journal |
| Views and places | journal, soft |
| Happiness, warm moments, golden light | soft, scrapbook |

The preview page always shows all five; recommend the two or three that fit and say why. One timeline renders one style. If the user asks to mix, offer different styles for different episodes; borrowing one element into another style means writing style code, so say that before promising it.

## Preview moments

`03_Style/preview_moments.json` lists 3-7 short moments from the footage for `make_style_preview.py`:

```json
[
  {"id": "funny1", "name_th": "ตลก: ชื่อเหตุการณ์", "src": "CLIP_0003.MP4", "start": 17.5, "dur": 6,
   "label": "ภารกิจวันนี้",
   "speech":  {"t": 1.2, "end": 3.9, "text": "คำพูดจริงในคลิป"},
   "impact":  {"t": 1.3, "end": 3.5, "words": ["โดน", "แล้ว!"]},
   "comment": {"t": 4.0, "end": 5.8, "text": "คอมเมนต์แซวจากคนตัด"}}
]
```

`id`, `name_th`, `src`, `start` and `dur` are required; `label`, `speech`, `impact` and `comment` are optional. Times inside a moment count from its `start`. The page shows only these four cue types; stamps, stickers, arrows and transitions are first seen in the style test render, so include some in it.

## How every style is used

Set `"style": "<key>"` and optionally `"font": "<family from font_options>"` in `timeline.json`. Pair the style with its colour grade: `vivid` for variety and comic, `warm` for scrapbook, `film` for soft and journal (the full rule is under "Colour grade" in [timeline-schema.md](./timeline-schema.md)). How many graphics each style carries is in the "How many" table of [graphics-guide.md](./graphics-guide.md). All styles accept the same cue types (see [timeline-schema.md](./timeline-schema.md)); positions default sensibly, so most cues need only `type`, text and times. Default SFX per cue type come from `styles.json` and can be overridden per cue with `"sfx"`.

---

## scrapbook: Paper scrapbook collage

**From sources**
- Core look: paper cut-outs, vintage photos, handmade textures, torn edges and stacked layers. ([Videobolt](https://blog.videobolt.net/post/how-to-use-torn-paper-animation-in-your-videos), [Behance](https://www.behance.net/gallery/137725269/Japanese-Animated-Collage-Video-Clips))
- Travel versions use taped photos, hand-drawn route arrows and postmarks; warm light and film grain tie it together.

**Working defaults**
- Stop-motion at 12 fps with a gentle "boil" (pieces jitter slightly), torn-paper text pieces, tape on the video corners.
- A limited palette (cream, mustard, teal, brick red) rather than every pastel.

**In the engine**
- Vertical framing draws torn paper bars around the video. Extras read from the timeline: `tones` (bar colour per scene), `postmarks` (place/date stamp), `route` (bottom trip line with a moving dot).
- Transition `tear`: a paper sheet sweeps across.
- Fonts: Mali (default), Itim, Sriracha. Default sounds: `paper_slap`, `tape`, `stamp`, `paper_tear`, `pen`, `pop`.

## variety: Korean variety captions

**From sources**
- Captions act like "an extra narrator" adding humour or emotion; producers describe it as writing an extra script after filming. Bold, colourful, exaggerated, combined with slow-motion replays, reaction graphics and sound effects. A professor warns the next step may be "learning when to hold back", and some viewers feel told how to feel. ([Korea Herald](https://www.koreaherald.com/article/10410946))

**Working defaults**
- Three caption layers: speech (outlined white), impact words (huge, yellow on red outline), PD comments (pink pills).
- Leave a beat without comments before a big joke so it can land.

**In the engine**
- Bouncy spring pops, wobbling impact words with a star burst, navy dotted bars in vertical.
- Transition `whip`: a yellow panel sweeps across.
- Fonts: Kanit Black (default), Prompt ExtraBold, Mitr Bold. SFX: boing, pop, ding, whoosh.

## comic: Comic impact

**From sources**
- Spider-Verse mixes hand-drawn frames, onomatopoeia and halftone; motion lines on fast objects add speed. In video, speed lines work best when they start and stop with a zoom; starbursts and radiating lines signal impact. ([Spider-Verse techniques](https://marilajane.substack.com/p/into-the-spider-verse-animation-techniques), [FlexClip](https://flexclip.com/learn/anime-speed-lines.html))

**Working defaults**
- It is the loudest style. Choose it for short, high-energy episodes (60 s or less) built around a few big hits, and keep the graphics count low between them so the hits stand out.

**In the engine**
- Impact words slam from 3x with a red starburst and a speed-line flash; boxes with hard black shadows; yellow halftone bars in vertical.
- Transition `burst`: a halftone panel slams in.
- Fonts: Prompt ExtraBold italic (default), Chonburi, Pattaya. SFX: boom, hit, whoosh, pop.

## journal: Field journal annotation

**From sources**
- Documentary map work blends motion graphics with cinematic footage. ([aescripts](https://aescripts.com/learn/how-johnny-harris-makes-maps), [PremiumBeat](https://www.premiumbeat.com/blog/replicating-vox-motion-graphic/))
- The doodle look pairs marker circles, arrow animations and handwriting fonts. ([Captions.ai](https://captions.ai/styles/chalk), [Motion Array](https://motionarray.com/learn/final-cut-pro/final-cut-pro-scribble-effects/))

**Working defaults**
- Handwriting that writes on left to right, pen arrows and circles drawn onto the picture, few words, nothing covering the view.

**In the engine**
- Text reveals like handwriting; use `arrow` and `ring` cues to point at things. Dark grid-paper bars in vertical.
- Transition `page`: a notebook page slides across.
- Fonts: Sriracha (default), Itim, Mali. Default sounds: `pen`, `paper_tear`.
- Text has no box, so on bright daylight footage place it over darker areas or use the vertical bars.

## soft: Soft cinematic

**From sources**
- Minimal title work relies on wide tracking and restraint; small spacing details separate amateur from professional; titles that fade up and away feel ethereal. ([Made Good Designs on Arrival](https://madegooddesigns.com/?p=11486), [Substack on tracking](https://keyavadgama.substack.com/p/a-typographic-commitment-to-the-bit))

**Working defaults**
- Small type, wide letter spacing, slow blur-in, no hard hits; let music and real sound lead.

**In the engine**
- Everything blooms in over 0.9 s and fades out; labels use very wide tracking. Deep navy gradient bars in vertical.
- Transition `fade`: a soft white dip.
- Fonts: Charm (display, default), Anuphan (body), Prompt Medium. SFX: chime on transitions only.
- Thin glowing text reads poorly over bright sky; best on evening, indoor or darker footage.

---

## Motion principles (all styles)

From sources of uneven quality; treat as starting points ([Cursa](https://cursa.app/en/article/from-keyframes-to-kinetics-timing-spacing-and-motion-curves-for-better-video-animations), [Infinite Creation](https://infinitecreation.pages.dev/tutorial-kinetic-text.html)):
- Fast start, soft stop for text entering.
- Springs give overshoot and settle; about 5% overshoot for calm work, more for playful work.
- Keep durations on whole frames; text that must be read should not enter faster than about 0.3 s.

## What makes graphics look AI-made

Check before every delivery:
- many small graphics around the edges and no clear hero
- emoji instead of designed elements
- every element animating the same way
- every colour used with no dominant one
- all captions the same size with no hierarchy

## Adding a new style

1. Copy the closest `assets/styles/<key>.js`, rename the key in `registerStyle`, and change `css`, `text`, `word`, `stamp`, `anim`, `frame` and `transitions`.
2. Add an entry to `styles.json` with Thai labels, fonts, `font_options`, `sfx`, `hit_offset` and `hold_fps` (12 for stop-motion, null for smooth). `hold_fps` must equal `holdFps` in the style's JS file: the JS value drives the animation, the JSON value tells the renderer how often to redraw. Add any new font file to `font_sources` and any new SFX name to `sfx_kit.py`.
3. Rebuild the preview with `make_style_preview.py`, check both formats, then add a section to this file with sources.
