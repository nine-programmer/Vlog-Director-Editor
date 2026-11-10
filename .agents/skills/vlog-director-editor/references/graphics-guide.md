# Graphics (step 6)

Graphics are HTML rendered by `engine.js` plus the chosen style, through headless Chrome, into a transparent MOV. The same code drives the preview page, so the render matches what the user chose.

## Order of work

1. Lock timing from the approved rough cut.
2. Three caption layers (see [variety-editing-grammar.md](./variety-editing-grammar.md)): speech or voice subtitles, impact words on punchlines, editor comments.
3. Style graphics: 1-3 hero moments per episode (impact, stamp, score, sticker), then labels and tags, then small accents.
4. Transitions only where the scene or place changes.
5. Caption review with the user (`captions.py export` / `apply`).
6. Full render; SFX are placed automatically on each graphic's landing frame from the style's defaults.
7. QA, then open the hero frame sheet yourself.

## Standards

- Speech captions at least 44 px tall on a 1080-wide frame; the styles' defaults already exceed this.
- Thai text is rendered by the browser. Do not draw Thai with PIL on Windows: without libraqm, vowels and tone marks stack wrongly.
- Fonts load from `05_Shared_Assets/fonts/`; `init_project.py` downloads them.
- Every graphic names the moment it reacts to; if it reacts to nothing, cut it.
- No hero graphic over a face. Check the QA sheet.
- In vertical, keep text out of the app interface: roughly the top 110 px, the bottom area from y 1560, and the right column x 960+ between y 900 and 1560 (conservative estimates; QA flags overlaps).
- Run the "looks AI-made" checklist in [style-library.md](./style-library.md).

## QA (automatic, `qa_check.py`)

Length vs timeline and format limit, -14 LUFS (±1), true peak at most -1 dB, black frames, silences over 1 s, caption reading speed (at most 18 Thai base characters per second), voiceover over real speech, vertical safe zones, and a hero frame sheet in `qa/`.

Passing QA is not enough. Open the frame sheet: problems such as a graphic left on screen or an icon that reads as something else cannot be caught by numbers.

## Send to the user

The render, a list of highlights with times, QA results, and what you could not check (mix feel, pronunciation, comic timing).
