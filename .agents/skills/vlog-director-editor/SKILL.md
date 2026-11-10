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
- **Say what you cannot check.** You cannot hear audio or judge comedy reliably; tell the user which parts need their ears. If you cannot view images either, say so at step 0, still produce every contact sheet and QA frame sheet, and ask the user to check them at each point where this skill says to look at frames.
- **Voice and music are the user's job.** The user records voice in Google AI Studio and makes music in Suno. Never offer AI voice or music; use `generate_voice.py` and `generate_music.py` only when the user asks.
- **Folders stay tidy.** Follow [folder-structure.md](./references/folder-structure.md). Temporary files go to `_temp/`.
- **Secrets.** `.env` is read by scripts only; never open or print it. `.env.example` may be read and edited.

**Running scripts.** Run every command from the project folder. `<skill>` in the commands below is this skill's folder, normally `.agents/skills/vlog-director-editor`. Scripts take `--root <project>` (use `.`) or `--timeline <file>`, work the same in bash and PowerShell, and print UTF-8 without extra settings.

**Read before you act.** The reference files hold the details the scripts expect. Read the ones named in a step before doing that step, every time; do not work from memory of this page.

## Workflow

| Step | Work | User approval |
|---|---|---|
| 0 | Set up project, ask what kind of video | Answers the brief |
| 1 | Scan footage | Decides which flagged clips to remove |
| 2 | Choose a style | Picks one style per episode |
| 3 | Plan every episode | Pass or revise |
| 4 | Voice and music, one episode at a time | Creates and drops files |
| 5 | Rough cut | Checks pacing |
| 6 | Captions review, graphics, full render | Fixes captions, then passes each episode |
| 7 | Ask before the master | Confirms or declines |
| 8 | Deliver | Receives files |

Step 3 covers all episodes at once. Steps 4-6 run one episode at a time: finish the first episode through step 6 before writing the next episode's order sheet, so one mistake is not repeated in every episode and the user does not make audio for a plan that later changes.

### Step 0: set up and brief

```bash
python <skill>/scripts/init_project.py --root .   # folders, AGENTS.md, CLAUDE.md, .gitignore, .env.example, fonts, SFX
python <skill>/scripts/check_env.py --root .      # what is missing on this machine
```

Then ask the user and write the answers into `00_Project/Brief.md`:
- what kind of video (funny, scenery, people's happiness, review, a mix)
- format: vertical up to 60-90 s or horizontal up to 1-3 min. One timeline renders one format. If the user wants both, agree which is the main one; the other is made afterwards as its own episode folder with an `H` or `V` after the number (`EP01H_Name`), with its own timeline, because framing, text positions and length all change
- reference clips they like (local files are best; you can analyse their frames)
- who appears, and the narrator's pronouns and polite particles

### Step 1: scan footage

The user has already chosen the clips in `01_Raw_Footage/`, so only technical quality is checked.

```bash
python <skill>/scripts/scan_footage.py --root . --transcribe
```

Outputs `02_Scan_Reports/scan_report.md` (clips worth removing, with reasons, and each clip's size and frame rate), `transcripts.json` and a contact sheet per clip in `sheets/`. Report the flagged clips; the user removes them, you never delete anything.

### Step 2: choose a style

Read first: [style-library.md](./references/style-library.md).

1. Choose 3-7 moments from the footage (one funny, one scenic, one emotional when possible).
2. Write `03_Style/preview_moments.json` (format in the "Preview moments" section of style-library.md) and build the page:
   ```bash
   python <skill>/scripts/make_style_preview.py --root .
   ```
3. Send the user `03_Style/preview/index.html`. It plays all 5 styles on the real clips with the same engine the renderer uses, in both formats, with font options.
4. Record the choice (style key, font, format) in `03_Style/Style_Selected.md`.
5. Render a 10-15 s test with the chosen style before planning, because a preview page and a real video feel different. Write a small timeline (2-3 shots, 4-6 cues, no voice or music) at `03_Style/style_test/timeline.json`, then:
   ```bash
   python <skill>/scripts/render_episode.py --timeline 03_Style/style_test/timeline.json --stage full
   ```
   The result is `03_Style/style_test/renders/style_Full_v01.mp4`. Send it to the user and confirm the style.

One timeline renders one style. If the user asks to mix styles, offer different styles for different episodes; blending two looks inside one episode means writing a new style file, so say that before agreeing.

### Step 3: plan every episode

Read first: [episode-plan-template.md](./references/episode-plan-template.md) and [variety-editing-grammar.md](./references/variety-editing-grammar.md).

Plan all episodes in one pass into `00_Project/Story_Plan.md`, then ask the user to pass it. Every shot names its clip and source minutes. Check action timing with:

```bash
python <skill>/scripts/frames.py --root . --src <clip> --start 11.5 --end 19.5 --every 0.4
```

List any AI images the plan needs under "ภาพเสริม"; they are made in step 6 (see "AI images" in [graphics-guide.md](./references/graphics-guide.md)).

### Step 4: voice and music

Read first: [audio-production-guide.md](./references/audio-production-guide.md).

For the episode you are about to cut, write `04_Episodes/EPxx_Name/audio_order.md`: where to make each file, settings, exact file name and folder. When the user has dropped the files, check that all exist, names match and lengths are sensible; use real file lengths in the timeline.

### Step 5: rough cut

Read first: [timeline-schema.md](./references/timeline-schema.md) and `assets/examples/timeline_example.json`.

Write `04_Episodes/EPxx_Name/timeline.json`, check it, then render:

```bash
python <skill>/scripts/validate_timeline.py --timeline 04_Episodes/EPxx_Name/timeline.json
python <skill>/scripts/render_episode.py --timeline 04_Episodes/EPxx_Name/timeline.json --stage rough
```

The check lists misspelt fields, missing files and times that point at shots which do not exist; the renderer runs it too and stops on errors.

540p, no graphics: cuts, punch-ins, replays, freezes, J/L cuts and a first mix. Look at frames of every shot before sending.

### Step 6: captions, graphics and full render

Read first: [graphics-guide.md](./references/graphics-guide.md) and the chosen style's section in [style-library.md](./references/style-library.md).

1. Add `graphics` to the timeline, and make any AI images the plan lists.
2. Caption review, because Thai speech-to-text is often wrong:
   ```bash
   python <skill>/scripts/captions.py export --timeline <timeline>   # user edits captions.md
   python <skill>/scripts/captions.py apply  --timeline <timeline>
   ```
3. Full render with overlay, SFX, mastering (-14 LUFS, true peak at most -1 dB) and QA:
   ```bash
   python <skill>/scripts/render_episode.py --timeline <timeline> --stage full
   ```
4. Read `qa/QA_<render>.md` and open `qa/<render>_hero.jpg`. Fix anything wrong before the user sees it, then send the render with highlights, QA results and what you could not check.

### Step 7: ask before the master

When every episode has passed, ask whether to assemble one. If yes:

```bash
python <skill>/scripts/master_vlog.py --root . --inputs <EP01 render> <EP02 render> ... --trim
```

`--trim` drops each episode's own hook and outro via `master_trim` in its timeline.

### Step 8: deliver

```bash
python <skill>/scripts/deliver.py --timeline <timeline>
```

Copies the render to `07_Delivery/` with cover-frame candidates and an upload sheet; write the Thai titles, description and hashtags into it. Update `00_Project/Status.md`.

## Tools

| Script | Purpose |
|---|---|
| `init_project.py` | Create folders, context files, the Claude Code pointer in `.claude/skills/`, fonts and SFX; never overwrites |
| `check_env.py` | Check packages, ffmpeg, NVENC, Chrome, fonts, SFX and which API keys are set |
| `scan_footage.py` | Quality scan, transcripts, contact sheets |
| `frames.py` | Timestamped contact sheet of any clip section |
| `make_style_preview.py` | Interactive style page on real footage |
| `validate_timeline.py` | Check a timeline for misspelt fields, missing files and bad times |
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
