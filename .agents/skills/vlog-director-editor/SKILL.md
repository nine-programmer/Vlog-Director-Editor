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
- **Do not guess.** When the references give a rule or a number, use it. When they do not and the choice changes what the user sees or hears, ask the user one short question instead of picking at random. When the user asks for something a rule advises against, say why once, then do what they decide.
- **Every graphic answers a moment.** If you cannot say which joke or event a graphic reacts to, cut it.
- **Look at frames, not only transcripts.** Transcripts give timing of words, not what is in the frame. Use contact sheets before placing any action-dependent cut, and open the QA frame sheet before showing a render.
- **Say what you cannot check.** You cannot hear audio or judge comedy reliably; tell the user which parts need their ears. If you cannot view images either, say so at step 0, still produce every contact sheet and QA frame sheet, and ask the user to check them at each point where this skill says to look at frames.
- **Voice and music are the user's job.** The user records voice in Google AI Studio and makes music in Suno. Never offer AI voice or music. Only if the user asks you to make them, read [ai-voice-music.md](./references/ai-voice-music.md).
- **Folders stay tidy.** Follow [folder-structure.md](./references/folder-structure.md). Temporary files go to `_temp/`.
- **Secrets.** `.env` is read by scripts only; never open or print it. `.env.example` may be read and edited.

**Running scripts.** Run every command from the project folder. `<skill>` in the commands below is this skill's folder, normally `.agents/skills/vlog-director-editor`. The commands work the same in bash and PowerShell and print UTF-8 without extra settings.

**Read before you act.** The reference files hold the details the scripts expect. Read the ones named in a step before doing that step, every time; do not work from memory of this page.

## Workflow

| Step | Work | Stop for the user to |
|---|---|---|
| 0 | Set up project, ask what kind of video | Answer the brief |
| 1 | Scan footage | Decide which flagged clips to remove |
| 2 | Choose a style | Pick one style, font and colour grade |
| 3 | Plan every episode | Approve the episode list, then the plan |
| 4 | Voice and music, one episode at a time | Create and drop the files |
| 5 | Rough cut | Approve cuts and pacing |
| 6 | Captions review, graphics, full render | Correct captions, then approve the episode |
| 7 | Ask before the master | Confirm or decline |
| 8 | Deliver | Receive files |

Step 3 covers all episodes at once. Steps 4-6 run one episode at a time: finish the first episode through step 6 before writing the next episode's order sheet, so one mistake is not repeated in every episode and the user does not make audio for a plan that later changes.

Update `00_Project/Status.md` after every approval. Use exactly these status words: `วางแผนแล้ว`, `รอไฟล์เสียง`, `ตัดหยาบ รอตรวจ`, `ใส่กราฟิก รอตรวจ`, `ผ่าน`, `ส่งมอบแล้ว`.

### Step 0: set up and brief

```bash
python <skill>/scripts/init_project.py --root .   # folders, AGENTS.md, CLAUDE.md, .gitignore, .env.example, fonts, SFX
python <skill>/scripts/check_env.py --root .      # what is missing on this machine
```

Fix anything `check_env.py` marks as required before going on. Then ask the user and write the answers into `00_Project/Brief.md`:

- what kind of video (funny, scenery, people's happiness, review, a mix)
- format: vertical or horizontal. One timeline renders one format. If the user wants both, agree which is the main one; the other is made afterwards as its own episode folder with an `H` or `V` after the number (`EP01H_Name`), with its own timeline, because framing, text positions and length all change
- which parts of the trip matter most, and whether they have a number of episodes in mind
- reference clips they like (local files are best; you can analyse their frames)
- who appears, and the narrator's pronouns and polite particles

Ask the user to copy their chosen clips into `01_Raw_Footage/`, one subfolder per camera, and wait until they say it is done.

### Step 1: scan footage

The user has already chosen the clips in `01_Raw_Footage/`, so only technical quality is checked.

```bash
python <skill>/scripts/scan_footage.py --root . --transcribe
```

Outputs in `02_Scan_Reports/`: `scan_report.md` (clips worth removing with reasons; each clip's size, frame rate and whether it has sound), `transcripts.json` (lines with source times, and word times inside each line) and a contact sheet per clip in `sheets/`. Transcription uses an NVIDIA GPU when there is one and the CPU otherwise, which is several times slower; tell the user before a long CPU run. Thai transcripts contain mistakes, which the caption review in step 6 exists to fix.

Clips are found by file name, so the scan stops if two clips share a name; ask the user to rename one. Report the flagged clips; the user removes them, you never delete anything.

### Step 2: choose a style

Read first: [style-library.md](./references/style-library.md).

1. Choose 3-7 moments from the transcripts and contact sheets, each 5-8 s, from different clips: at least one with a spoken line, one wide view, and one reaction or quiet beat. Avoid moments where a face sits at the bottom of the picture, under the captions.
2. Write `03_Style/preview_moments.json` (format in the "Preview moments" section of style-library.md) and build the page:
   ```bash
   python <skill>/scripts/make_style_preview.py --root .
   ```
3. Send the user `03_Style/preview/index.html`. It plays all 5 styles on the real clips with the same engine the renderer uses, in both formats, with font options. Recommend the two or three styles that fit, using the "Choosing" table, and say why.
4. Render a 10-15 s test with the chosen style before planning, because a preview page and a real video feel different. Write a small timeline at `03_Style/style_test/timeline.json`: 2-3 shots, no voice or music, the style's paired colour grade, and exactly one each of `speech`, `impact`, `comment`, `label`, `stamp`, `arrow` and `transition` (no sticker; images come later). Then:
   ```bash
   python <skill>/scripts/render_episode.py --timeline 03_Style/style_test/timeline.json --stage full
   ```
   The result is `03_Style/style_test/renders/style_Full_v01.mp4`. Send it to the user and confirm the style and the colour.
5. Record the choice in `03_Style/Style_Selected.md`: style key, font, format, colour grade.

One timeline renders one style. If the user asks to mix styles, offer different styles for different episodes; blending two looks inside one episode means writing a new style file, so say that before agreeing.

### Step 3: plan every episode

Read first: [episode-plan-template.md](./references/episode-plan-template.md) and [variety-editing-grammar.md](./references/variety-editing-grammar.md).

1. Propose the episode list first: one line per episode with its story and why it stands alone. Get it approved before writing shot tables.
2. Plan all approved episodes in one pass into `00_Project/Story_Plan.md`, then ask the user to pass it. Every shot names its clip and source seconds. Check action timing with:
   ```bash
   python <skill>/scripts/frames.py --root . --src <clip> --start 11.5 --end 19.5 --every 0.4
   ```
3. List any AI images the plan needs under "ภาพเสริม"; they are made in step 6 (see "AI images" in [graphics-guide.md](./references/graphics-guide.md)).

### Step 4: voice and music

Read first: [audio-production-guide.md](./references/audio-production-guide.md).

For the episode you are about to cut, create `04_Episodes/EPxx_Name/` with `voice/`, `music/` and `visuals/` inside, and write `audio_order.md` there: where to make each file, settings, exact file name and folder. Then wait for the user. If they want to see pacing before making audio, render the rough cut without `voiceovers` and `bgm` and say that it has none.

When the user has dropped the files, check each one:

```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 04_Episodes/EPxx_Name/voice/EPxx_VO01.wav
```

- Every file in the order sheet exists with exactly the ordered name.
- A voice line within 1 s of its estimate is fine; use its real length in the timeline. If it is further off, rework the shots under it or ask the user to redo the line.
- A music file must be at least 2 s longer than the stretch it covers. If it is shorter, ask the user for a longer one; music is not looped.

### Step 5: rough cut

Read first: [timeline-schema.md](./references/timeline-schema.md) and `assets/examples/timeline_example.json`.

Write `04_Episodes/EPxx_Name/timeline.json`, check it, then render:

```bash
python <skill>/scripts/validate_timeline.py --timeline 04_Episodes/EPxx_Name/timeline.json
python <skill>/scripts/render_episode.py --timeline 04_Episodes/EPxx_Name/timeline.json --stage rough
```

The check lists misspelt fields, missing files, times outside a clip and times that point at shots which do not exist; the renderer runs it too and stops on errors. Fix warnings as well unless you can say why one does not apply.

The rough cut is half size with no graphics: cuts, punch-ins, animated zooms, speed ramps, full-frame shots, replays, freezes, J/L cuts, the colour grade, music, voice and the sounds listed in `sfx`. Before sending it, look at it yourself:

```bash
python <skill>/scripts/frames.py --src 04_Episodes/EPxx_Name/renders/EPxx_Rough_v01.mp4 --start 0 --end <length> --every 1
```

Check that every shot shows what the plan says, and compare neighbouring shots for colour. You cannot judge how smooth a move or ramp feels from still frames; list the shots that use `move`, a speed ramp, `fill`, `lead` or `tail` and ask the user to watch those.

### Step 6: captions, graphics and full render

Read first: [graphics-guide.md](./references/graphics-guide.md) and the chosen style's section in [style-library.md](./references/style-library.md).

1. Add `graphics` to the timeline, and make any AI images the plan lists.
2. Caption review, because Thai speech-to-text is often wrong:
   ```bash
   python <skill>/scripts/captions.py export --timeline <timeline>   # writes captions.md next to the timeline
   python <skill>/scripts/captions.py apply  --timeline <timeline>   # after the user has edited it
   ```
   Send the user `captions.md` and wait. They correct the text column, or write `ลบ` to remove a caption.
3. Full render with overlay, sounds, mastering (-14 LUFS, true peak at most -1 dB) and QA:
   ```bash
   python <skill>/scripts/render_episode.py --timeline <timeline> --stage full
   ```
4. Read `qa/QA_<render>.md` and open `qa/<render>_hero.jpg`. Fix what failed and render again. If the same QA line fails twice, stop and show the user the numbers. Then send the render with highlights, QA results and what you could not check.

Renders are never overwritten; each run writes the next version (`_v02`). When the user asks for changes, edit the timeline and render again.

### Step 7: ask before the master

When every episode has passed, ask whether to assemble one. If yes:

```bash
python <skill>/scripts/master_vlog.py --root . --inputs <EP01 approved render> <EP02 approved render> ... --trim
```

It writes `06_Master/Master_v01.mp4` and prints its loudness. `--trim` drops each episode's own hook and outro via `master_trim` in its timeline. The master has no automatic QA and its joins cut the music of each episode, so look at frames around every join with `frames.py` and ask the user to listen to the joins.

### Step 8: deliver

```bash
python <skill>/scripts/deliver.py --timeline <timeline> --render <the render the user approved>
```

Always pass `--render`; without it the newest render is used, which may not be the approved one. It copies the file to `07_Delivery/` with cover-frame candidates and an upload sheet (`EPxx_Upload.md`); write three Thai title options, a description and hashtags into the sheet.

## Tools

| Script | Purpose |
|---|---|
| `init_project.py` | Create folders, context files, the Claude Code pointer in `.claude/skills/`, fonts and SFX; never overwrites |
| `check_env.py` | Check packages, ffmpeg, NVENC, Chrome, fonts, SFX and which API keys are set |
| `scan_footage.py` | Quality scan, transcripts, contact sheets |
| `frames.py` | Timestamped contact sheet of any clip or render; `--grid` adds pixel coordinates |
| `make_style_preview.py` | Interactive style page on real footage |
| `validate_timeline.py` | Check a timeline for misspelt fields, missing files and bad times |
| `render_episode.py` | Rough and full renders from `timeline.json`, cached per shot |
| `render_overlay.py` | Graphics engine to transparent MOV (used by the renderer) |
| `captions.py` | Export and apply caption corrections |
| `qa_check.py` | Automatic checks and the hero frame sheet (run by the full render) |
| `master_vlog.py` | Assemble approved episodes |
| `deliver.py` | Delivery files and upload sheet |
| `sfx_kit.py` | Licence-free synthesized SFX (run by `init_project.py`) |
| `generate_image.py` | AI images (OpenAI, `OPENAI_API_KEY`) |
| `generate_voice.py`, `generate_music.py` | Only when the user asks; see [ai-voice-music.md](./references/ai-voice-music.md) |

Requirements: Python 3.10+, ffmpeg, Google Chrome, `pip install numpy scipy opencv-python pillow playwright faster-whisper`. An NVIDIA GPU speeds up encoding and transcription but is not required.
