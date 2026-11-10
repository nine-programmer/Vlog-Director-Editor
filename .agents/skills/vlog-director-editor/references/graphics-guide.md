# Graphics (step 6)

Graphics are HTML rendered by `engine.js` plus the chosen style, through headless Chrome, into a transparent MOV. The same code drives the preview page, so the render matches what the user chose.

## Order of work

1. Lock timing from the approved rough cut.
2. Speech and voice subtitles for every line the viewer must follow. Anchor each to its shot with `{"shot": id, "src": <transcript start>}`.
3. Hero graphics: the moments the episode is remembered for (`impact`, `stamp`, `score`, `sticker`). Each one names the joke or event it reacts to.
4. Editor comments, then labels and tags.
5. Transitions only where the place changes.
6. Caption review with the user (`captions.py export` / `apply`).
7. Full render; sounds are placed automatically on each graphic's landing frame from the style's defaults.
8. QA, then open the hero frame sheet yourself.

## How many

Count everything except speech and voice subtitles. These are upper limits per 60 s of video, not targets; fewer is usually better.

| Style | Hero graphics | Comments | Labels and tags | Arrows and rings | Total at once on screen |
|---|---|---|---|---|---|
| variety | 4 | 6 | 4 | 2 | 3 |
| comic | 4 | 4 | 3 | 2 | 3 |
| scrapbook | 3 | 4 | 4 | 2 | 3 |
| journal | 2 | 3 | 3 | 4 | 2 |
| soft | 1 | 2 | 2 | 0 | 1 |

- A sticker or march only when the plan lists an image for it.
- If you cannot say which moment a graphic reacts to, cut it.
- Before a big joke, leave 0.3-0.5 s with nothing new on screen.

## Standards

- Thai text is rendered by the browser. Do not draw Thai with PIL on Windows: without libraqm, vowels and tone marks stack wrongly.
- Fonts load from `05_Shared_Assets/fonts/`; `init_project.py` downloads them.
- Caption length, timing, positions, colours and sounds follow the "Graphics cues" section of [timeline-schema.md](./timeline-schema.md). A caption that is too long for one line is shrunk; QA fails it below 80% size, so split it.
- No graphic over a face. Check the QA sheet.
- Run the "looks AI-made" checklist in [style-library.md](./style-library.md).

## AI images

Use an image only when the story needs something the footage does not show (the animal a joke is about, a map pin, a prop for a running gag). Zero to two per episode; they are stickers, never backgrounds or fake footage.

```bash
python <skill>/scripts/generate_image.py --prompt "..." --out 04_Episodes/EP01_Name/visuals/prop.png --transparent
```

- Always `--transparent` for stickers, and write the prompt in the chosen style's look (paper cut-out for scrapbook, bold outline for comic, pen sketch for journal).
- Describe people in words. Never upload frames of real people, especially children, without the user's explicit consent.
- Each image costs money; tell the user how many you plan to make before making them.
- Open the image before using it. Trim empty margins so `w` matches what is seen:
  ```bash
  python -c "from PIL import Image; im = Image.open('visuals/prop.png'); im.crop(im.getbbox()).save('visuals/prop_trim.png')"
  ```
  Run it from the episode folder, then place the trimmed file with a `sticker` or `march` cue; `w` is its on-screen width in pixels (120-320 is typical).

## QA (automatic, `qa_check.py`)

| Check | Fails when |
|---|---|
| Length | The file differs from the timeline, or passes 90 s vertical / 180 s horizontal |
| Loudness, true peak | Outside -14 LUFS ±1, or peak above -1 dBTP |
| Black frames, silence | Any black stretch of 0.3 s, any silence over 1 s |
| Reading speed | A `speech`, `voice`, `comment`, `label`, `score` or `tag` cue shows more than 18 Thai characters per second |
| Shrunk captions | A text cue was scaled below 80% to fit its line |
| Voiceover over speech | A voiceover overlaps a `full` shot or a `moment` by more than 0.3 s |
| Vertical safe zones | Text sits under the app's top bar, bottom caption area or right-hand buttons |

It also writes a frame sheet of the hero graphics, comments, tags, arrows, and every caption on a full-frame shot, to `qa/<render>_hero.jpg`.

Fix every failed line and render again. If the same line fails twice, stop and show the user the numbers instead of trying a third time. Passing QA is not enough: open the frame sheet, because a graphic left on screen or an icon that reads as something else cannot be caught by numbers.

## Send to the user

The render, a list of highlights with times, QA results, and what you could not check (mix feel, pronunciation, comic timing, how smooth moves and ramps feel).
