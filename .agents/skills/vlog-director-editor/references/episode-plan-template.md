# Story plan template (00_Project/Story_Plan.md)

Plan every episode in one pass, then ask the user to pass it. The plan is written in Thai. Every time comes from transcripts and from looking at contact sheets (`02_Scan_Reports/sheets/`, `frames.py`), never from transcripts alone.

## Episodes

One episode is one story that stands alone: one place, one activity or one running joke, with its own hook and payoff. Count the stories in the footage, not the minutes. Before writing any shot table, send the user the episode list (a name and one line each) and get it approved.

## Length

- Vertical: aim for 45-60 s; 90 s is the hard maximum.
- Horizontal: aim for 60-150 s; 180 s is the hard maximum.
- There is no minimum. Pacing numbers are in [variety-editing-grammar.md](./variety-editing-grammar.md).

If the user wants both formats, plan the main format here and note the second (`EP01H_Name` or `EP01V_Name`) as a follow-up episode; it gets its own timeline after the main one passes.

Each episode must stand alone with its own hook and ending. Mark which shots are the hook in the "เทคนิคตัด" column so a master can drop them later (`master_trim`).

Write source times as seconds from the start of the clip, exactly as they go into the timeline (`65.2`, not `01:05.2`).

## Template (fill in Thai)

```markdown
## EP01: ชื่อตอน
- รูปแบบ: แนวตั้ง ประมาณ 70 วินาที
- Style: <key> (ฟอนต์ ..., โทนสี ...)
- แก่นเรื่อง: ...
- Hook: ...
- มุกที่ใช้วนทั้งตอน: ...
- ปิดตอน: ...

| ลำดับ | ในคลิป | ไฟล์ | จาก | ถึง | ภาพที่เห็น | เสียงจริง | บทพากย์ | เทคนิคตัด | กราฟิกและเหตุการณ์ที่รับ | SFX |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0:00–0:03.7 | `CLIP_0003.MP4` | 18.7 | 21.4 | ... | "..." | - | Hook, Freeze | ... | ... |

## บทพากย์
| ไฟล์ | บท | ความยาวประมาณ |

## เพลง
| ไฟล์ | ใช้ช่วง | อารมณ์ | Style สำหรับ Suno |

## ภาพเสริม
...

## จุดที่ต้องให้ผู้ใช้ตรวจ
Every line whose transcript is unclear (garbled words, names, places, anything in Latin letters), so the user can listen and correct it.
```
