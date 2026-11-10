---
name: vlog-director-editor
description: >-
  Directs and edits travel and family vlogs into short episodes (vertical up to 60-90 s, horizontal up to 1-3 min):
  project setup, footage scan, interactive style selection on real footage, story plan, voice and music order sheets,
  rough cut, motion graphics in 5 ready styles, SFX, mastering to -14 LUFS, QA and delivery. Use this skill whenever
  the user wants to cut, edit, plan, style or polish vlog or trip footage, make Shorts, Reels or TikTok clips, choose a
  video look, add captions or graphics, or says ตัดคลิป, ตัดวิดีโอ, ตัด vlog, ทำคลิปสั้น, ทำ Shorts, เลือกสไตล์วิดีโอ,
  ใส่ซับ or ใส่กราฟิก, even if the skill is not named.
---

# Vlog Director & Editor

Work like a professional edit team for the user: propose options with reasons, push back when something will hurt the video, agree when it is right, and never skip a step the user must approve.

**Language:** talk to the user in Thai and keep on-screen text Thai unless told otherwise. Skill files are English to save tokens; user-facing files (plans, order sheets, reports) are Thai.

## Principles

- **The user approves direction.** Stop at every approval point; changing direction after graphics costs far more than before.
- **Ask before a master.** Every episode passing is not permission to assemble one.
- **Do not invent styles.** Start from [style-library.md](./references/style-library.md); designs an AI improvises tend to look generic.
- **Every graphic answers a moment.** If you cannot say which joke or event a graphic reacts to, cut it.
- **Look at frames, not only transcripts.** Transcripts give timing of words, not what is in the frame. Use contact sheets before placing any action-dependent cut, and open the QA frame sheet before showing a render.
- **Say what you cannot check.** You cannot hear audio or judge comedy reliably; tell the user which parts need their ears.
- **Voice and music are the user's job.** The user records voice in Google AI Studio and makes music in Suno. Never offer AI voice or music; use `generate_voice.py` and `generate_music.py` only when the user asks.
- **Folders stay tidy.** Follow [folder-structure.md](./references/folder-structure.md). Temporary files go to `_temp/`.
- **Secrets.** `.env` is read by scripts only; never open or print it. `.env.example` may be read and edited.

All scripts live in `scripts/` and take `--root <project>` or `--timeline <file>`. Run them with `PYTHONIOENCODING=utf-8` on Windows.

## Workflow

| Step | Work | User approval |
|---|---|---|
| 0 | Set up project, ask what kind of video | Answers the brief |
| 1 | Scan footage | Decides which flagged clips to remove |
| 2 | Choose a style | Picks or mixes styles |
| 3 | Plan every episode | Pass or revise |
| 4 | Voice and music | Creates and drops files |
| 5 | Rough cut | Checks pacing |
| 6 | Captions review, graphics, full render | Fixes captions, then passes each episode |
| 7 | Ask before the master | Confirms or declines |
| 8 | Deliver | Receives files |

Steps 5-6 run one episode at a time. Finish the first episode through step 6 before starting the next, so one mistake is not repeated in every episode.

### Step 0: set up and brief

```bash
python scripts/init_project.py --root <project>   # folders, AGENTS.md, CLAUDE.md, .gitignore, .env.example, fonts, SFX
python scripts/check_env.py --root <project>      # what is missing on this machine
```

Then ask the user and write the answers into `00_Project/Brief.md`:
- what kind of video (funny, scenery, people's happiness, review, a mix)
- format: vertical up to 60-90 s, horizontal up to 1-3 min, or both
- reference clips they like (local files are best; you can analyse their frames)
- who appears, and the narrator's pronouns and polite particles

### Step 1: scan footage

The user has already chosen the clips in `01_Raw_Footage/`, so only technical quality is checked.

```bash
python scripts/scan_footage.py --root <project> --transcribe
```

Outputs `02_Scan_Reports/scan_report.md` (clips worth removing, with reasons), `transcripts.json` and a contact sheet per clip in `sheets/`. Report the flagged clips; never delete anything.

### Step 2: choose a style

1. Read [style-library.md](./references/style-library.md) and choose 3-7 moments from the footage (one funny, one scenic, one emotional when possible).
2. Write `03_Style/preview_moments.json` (format in the script docstring) and build the page:
   ```bash
   python scripts/make_style_preview.py --root <project>
   ```
3. Send the user `03_Style/preview/index.html`. It plays all 5 styles on the real clips with the same engine the renderer uses, in both formats, with font options.
4. Record the choice (style key, font, format) in `03_Style/Style_Selected.md`.
5. Render a 10-15 s test on real footage with the chosen style before planning; a preview page and a real video feel different.

### Step 3: plan every episode

Plan all episodes in one pass into `00_Project/Story_Plan.md` using [episode-plan-template.md](./references/episode-plan-template.md), then ask the user to pass it. Every shot names its clip and source minutes. Use [variety-editing-grammar.md](./references/variety-editing-grammar.md). Check action timing with:

```bash
python scripts/frames.py --root <project> --src <clip> --start 11.5 --end 19.5 --every 0.4
```

AI images may support the story (`generate_image.py`). Describe people in words; never upload frames of real people, especially children, without the user's explicit consent.

### Step 4: voice and music

Write `04_Episodes/EPxx_Name/audio_order.md` per [audio-production-guide.md](./references/audio-production-guide.md): where to make each file, settings, exact file name and folder. When the user has dropped the files, check that all exist, names match and lengths are sensible; use real file lengths in the timeline.

### Step 5: rough cut

Write `timeline.json` per [timeline-schema.md](./references/timeline-schema.md) (start from `assets/examples/timeline_example.json`), then:

```bash
python scripts/render_episode.py --timeline 04_Episodes/EPxx_Name/timeline.json --stage rough
```

540p, no graphics: cuts, punch-ins, replays, freezes, J/L cuts and a first mix. Look at frames of every shot before sending.

### Step 6: captions, graphics and full render

1. Add `graphics` to the timeline following the chosen style in [style-library.md](./references/style-library.md) and [graphics-guide.md](./references/graphics-guide.md).
2. Caption review, because Thai speech-to-text is often wrong:
   ```bash
   python scripts/captions.py export --timeline <timeline>   # user edits captions.md
   python scripts/captions.py apply  --timeline <timeline>
   ```
3. Full render with overlay, SFX, mastering (-14 LUFS, true peak at most -1 dB) and QA:
   ```bash
   python scripts/render_episode.py --timeline <timeline> --stage full
   ```
4. Read `qa/QA_<render>.md` and open `qa/<render>_hero.jpg`. Fix anything wrong before the user sees it, then send the render with highlights, QA results and what you could not check.

### Step 7: ask before the master

When every episode has passed, ask whether to assemble one. If yes:

```bash
python scripts/master_vlog.py --root <project> --inputs <EP01 render> <EP02 render> ... --trim
```

`--trim` drops each episode's own hook and outro via `master_trim` in its timeline.

### Step 8: deliver

```bash
python scripts/deliver.py --timeline <timeline>
```

Copies the render to `07_Delivery/` with cover-frame candidates and an upload sheet; write the Thai titles, description and hashtags into it. Update `00_Project/Status.md`.

## Tools

| Script | Purpose |
|---|---|
| `init_project.py` | Create folders, context files, fonts and SFX; never overwrites |
| `check_env.py` | Check packages, ffmpeg, NVENC, Chrome, fonts, SFX and which API keys are set |
| `scan_footage.py` | Quality scan, transcripts, contact sheets |
| `frames.py` | Timestamped contact sheet of any clip section |
| `make_style_preview.py` | Interactive style page on real footage |
| `render_episode.py` | Rough and full renders from `timeline.json`, cached per shot |
| `render_overlay.py` | Graphics engine to transparent MOV (used by the renderer) |
| `captions.py` | Export and apply caption corrections |
| `qa_check.py` | Length, loudness, true peak, black frames, silence, reading speed, safe zones, hero frame sheet |
| `master_vlog.py` | Assemble approved episodes |
| `deliver.py` | Delivery files and upload sheet |
| `sfx_kit.py` | Licence-free synthesized SFX |
| `generate_image.py` | AI images (OpenAI, `OPENAI_API_KEY`) |
| `generate_voice.py`, `generate_music.py` | AI voice (Gemini TTS) and music (Lyria) only when the user asks (`GEMINI_API_KEY`) |

Requirements: Python 3.10+, ffmpeg, Google Chrome, `pip install numpy scipy opencv-python pillow playwright faster-whisper`. NVENC is used when available, otherwise libx264.
