# Folder structure

Everything for one episode lives in one folder, so work can be revised, moved or archived without hunting for files. `init_project.py` creates this tree.

```text
<project>/
├── .env                 API keys, read by scripts only, never committed
├── .env.example         Key names with what each is for
├── .gitignore           Keeps only the skill and context files in Git
├── AGENTS.md            Project rules (CLAUDE.md imports it)
├── .claude/skills/      Pointer so Claude Code finds the skill in .agents/skills/
├── 00_Project/          Brief.md, Story_Plan.md, Status.md
├── 01_Raw_Footage/      Clips the user chose, one subfolder per camera, file names unique (read-only)
├── 02_Scan_Reports/     scan_report.md, transcripts.json, sheets/
├── 03_Style/            preview_moments.json, preview/, Style_Selected.md, style_test/ (timeline.json, renders/, qa/)
├── 04_Episodes/
│   └── EP01_Name/           a second format of the same episode is EP01H_Name or EP01V_Name
│       ├── timeline.json    edit decision list for the episode
│       ├── audio_order.md   voice and music order sheet
│       ├── captions.md      caption review table
│       ├── voice/           EP01_VO01.wav
│       ├── music/           EP01_BGM_A.mp3
│       ├── visuals/         AI images and other supporting visuals
│       ├── renders/         EP01_Rough_v01.mp4, EP01_Full_v01.mp4
│       └── qa/              QA reports and frame sheets
├── 05_Shared_Assets/
│   ├── fonts/           fonts in use, with SOURCES.md
│   └── sfx/             SFX with SOURCES.md (synth/ is made by sfx_kit.py)
├── 06_Master/           only after the user confirms a master
├── 07_Delivery/         upload-ready files, covers, upload sheets
└── _temp/               caches and scratch work, safe to delete
```

## Rules

1. Temporary files, frame checks and experiments go in `_temp/` only.
2. `01_Raw_Footage/` is read-only. Report problems; never edit or delete.
3. Never overwrite a render; versions go up (`_v02`). The scripts do this automatically.
4. File names are English and start with the episode code, which avoids tool problems with Thai names.
5. Fonts and SFX in use are kept in `05_Shared_Assets/` with source and licence notes.
6. `05_Shared_Assets/` is not committed: `init_project.py` downloads the fonts and regenerates the SFX on any machine.
