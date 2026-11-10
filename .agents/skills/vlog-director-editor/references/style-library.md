# Style library

Ten styles ship ready to render. Each is a file in `assets/styles/<key>.js` driven by the shared `engine.js`, with fonts, default SFX and Thai labels in `assets/styles/styles.json`. The preview page and the renderer use the same code, so what the user picks is what renders.

Research notes are marked **From sources** (with links) or **Working defaults** (our own starting points). Learn the grammar of each look; never copy a show's logo, characters or assets.

## Choosing

| Footage is mostly | Offer |
|---|---|
| Jokes from speech and reactions | variety, comic |
| A trip across places, food, family memories | scrapbook, journal |
| Views and places | journal, soft |
| Happiness, warm moments, golden light | soft, scrapbook, filmroll |
| Views and atmosphere with little or no speech | filmroll, magazine, soft |
| Camping, hiking, activities at a place | outdoor, journal |
| Children playing, behind the scenes, handheld phone shots | camcorder, pixel |
| A child's day told as missions, short vertical clips | pixel, variety |

The preview page always shows all ten; recommend the two or three that fit and say why. One timeline renders one style. If the user asks to mix, offer different styles for different episodes; borrowing one element into another style means writing style code, so say that before promising it.

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

Set `"style": "<key>"` and optionally `"font": "<family from font_options>"` in `timeline.json`. Pair the style with its colour grade: `vivid` for variety, comic and pixel; `warm` for scrapbook and outdoor; `film` for soft, journal, filmroll, camcorder and magazine (the full rule is under "Colour grade" in [timeline-schema.md](./timeline-schema.md)). How many graphics each style carries is in the "How many" table of [graphics-guide.md](./graphics-guide.md). All styles accept the same cue types (see [timeline-schema.md](./timeline-schema.md)); positions default sensibly, so most cues need only `type`, text and times. Default SFX per cue type come from `styles.json` and can be overridden per cue with `"sfx"`.

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
- Fonts: Charm (display, default), Anuphan (body), Prompt Medium. Each option keeps its own weight. SFX: chime on transitions only.
- Thin glowing text reads poorly over bright sky; best on evening, indoor or darker footage.

## filmroll: Film roll

**From sources**
- A little grain and a gentle date stamp feel authentic; heavy effects hide faces. The date sits in the lower-right corner in orange or white and should fit the footage's real date. Light leaks are overlays kept at low strength. ([PremiumBeat](https://www.premiumbeat.com/blog/how-to-give-videos-vintage-look), [PerfectCorp](https://www.perfectcorp.com/consumer/blog/photo-editing/y2k-film-look-holiday-photos-2026), [Sickboat](https://sickboat.com/blogs/blog/top-film-textures-for-video))

**Working defaults**
- Very few words, slow fades, no hits. The frame and the date carry the look; the picture tells the story.

**In the engine**
- A thin black frame with rounded corners on every shot, in both formats. Black bars with sprocket holes in vertical. `postmarks` shows as the amber date at the bottom-right.
- Transition `leak`: a warm flash of light.
- Fonts: Trirong italic (default), Charm, Sriracha. SFX: shutter on transitions and stamps only.
- There is no film grain or vignette: a full-frame texture or gradient adds several hundred MB of overlay per minute. Text has no box, so on bright footage place it over darker areas. Footage that is already graded can turn muddy under the `film` grade; check the style test and fall back to `natural`.
- The frame and date are hidden during full-frame (`fill`) shots in vertical.

## camcorder: Home camcorder

**From sources**
- Creators use old camcorders to make travel footage feel like a candid record instead of a highlight reel. The look is scan lines, soft colour and a date-and-time stamp. ([No Garlic No Onions](https://www.nogarlicnoonions.com/why-vintage-camcorders-are-making-a-comeback-in-travel-vlogging), [Captions.ai](https://captions.ai/styles/analog), [TrendHunter](https://www.trendhunter.com/trends/recording-apps))

**Working defaults**
- Best on playful, imperfect footage. The viewfinder stays on screen the whole time, so keep other graphics few.

**In the engine**
- Viewfinder brackets, a blinking REC at the top-right, a tape counter at the bottom-right that counts episode time, and scan lines over the picture. `postmarks` shows as the date at the bottom-left. Text has red and cyan fringes and jitters in.
- Transition `glitch`: a short tape dropout with coloured bars.
- Fonts: Chakra Petch (default), Bai Jamjuree, Mitr. SFX: pop, and rewind on transitions.
- It makes sharp footage look worse on purpose; do not offer it for an episode built on beautiful views.
- The viewfinder is hidden during full-frame (`fill`) shots in vertical.

## magazine: Travel magazine

**From sources**
- Travel reels in this look pair a serif headline with small, soft subtext. Wide tracking on small labels reads as documentary. Titles should move calmly: fades and slides, no bouncing. ([Async](https://async.com/templates/endlessly-golden-aesthetic-reel-template), [Cursa](https://cursa.app/en/page/titles-and-simple-graphics-readable-text-that-supports-the-video))

**Working defaults**
- One large headline at a time; everything else small and quiet. Use `impact` for the headline and `stamp` for a chapter number.

**In the engine**
- Large white serif headlines, labels with a thin rule and wide tracking, text that rises or wipes in. Near-black bars with a hairline in vertical.
- Transition `block`: a paper-coloured panel slides across.
- Fonts: Trirong Bold (default), Chonburi, Charm. SFX: whoosh on transitions only.
- Text has no box, so on bright footage place it over darker areas. A headline covers a lot of picture; move it off people.

## outdoor: Camp badge

**From sources**
- Outdoor and national-park graphics are built as badges, lean on dark green, and are heavy on typography borrowed from trail signs and old park posters. ([Spoon Graphics](https://blog.spoongraphics.co.uk/articles/60-creative-outdoors-adventure-themed-logo-designs), [Anderson Design Group](https://www.andersondesigngroupstore.com/a/collections/61-american-national-parks/badlands-national-park-emblem-print), [Dribbble](https://dribbble.com/stories/2020/04/20/graphic-designers-national-parks))

**Working defaults**
- Three colours only: forest green, cream, orange. Boxes like trail signs, one badge.

**In the engine**
- Cream sign boxes with a green border and hard shadow, impact words with a green outline and orange shadow, pill-shaped stamps. Green bars with contour lines in vertical. `postmarks` shows as a round badge in the top-right corner.
- Transition `badge`: a green disc grows from the centre.
- Fonts: K2D ExtraBold (default), Kanit Black, Mitr. SFX: hit, stamp, pop, whoosh.
- Bold boxes take away the calm of a quiet evening view; use fewer on those shots.

## pixel: Pixel game

**From sources**
- The look is built from game interface parts (dialog boxes, score displays) in a limited palette. A busy overlay on a busy shot reads as clutter. The era's conventions are free to use; a real game's artwork is not. ([Vizard](https://agent.vizard.ai/how-to/make-your-reel-look-like-a-retro-video-game.html), [Filmora](https://filmora.wondershare.com/video-effects/pixel-art-templates.html))

**Working defaults**
- Tell the trip as missions: `label` names the quest, `speech` is the dialog box, `score` keeps count, `stamp` marks a mission done.

**In the engine**
- Navy dialog boxes with a white pixel border, yellow labels, motion in steps at 12 fps. Navy grid bars in vertical.
- Transition `blocks`: the picture is covered by squares, then uncovered.
- Fonts: Chakra Petch (default), Mitr, Bai Jamjuree. Latin letters and digits use Pixelify Sans. SFX: boing, ding, pop.
- Thai text is not pixel-shaped, because the font kit has no Thai pixel font. Never copy the look of one real game.

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
