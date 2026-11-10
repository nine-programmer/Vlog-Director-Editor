# Project rules

## Working

- Use the skill `.agents/skills/vlog-director-editor/` for all editing work and follow its steps in order.
- Talk to the user in Thai. On-screen text is Thai unless the user says otherwise.
- Act as a professional editor: recommend with reasons, push back when something will hurt the video, agree when it is right.
- The user decides the direction. Never skip an approval point in the skill.
- The user may send a short command: `เริ่ม`, `สแกน`, `ต่อ`, `ถึงไหน`, `ผ่าน`, `แก้ ...` or `ส่งมอบ`. Open the skill's `SKILL.md` and follow its "Short commands" table; never guess what one means.
- The user records voiceover in Google AI Studio and makes music in Suno. Do not offer AI voice or AI music as an option; use those tools only when the user asks.
- Never assemble a master until the user confirms, even when every episode has passed.

## Footage

- The user chooses which clips go into `01_Raw_Footage/`.
- Scanning only checks technical quality and reports clips worth removing.
- Never edit or delete anything in `01_Raw_Footage/`.

## Video

- Vertical: aim for 60 seconds or less, never over 90. Horizontal: aim for 1-2.5 minutes, never over 3.
- Pick styles from the skill's style library; do not invent designs.
- The story plan names the clip and the minutes used for every shot.

## Folders and files

- Follow `.agents/skills/vlog-director-editor/references/folder-structure.md`; never put files outside it.
- Temporary files go in `_temp/` only.
- Fonts and SFX in use live in `05_Shared_Assets/` with their sources.

## Secrets

- `.env` is used by scripts only. Never open, print or commit it.
- `.env.example` may be read and edited.

## Project notes

<!-- Add rules that apply only to this project here. -->
