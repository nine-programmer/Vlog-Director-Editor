# งานเสียง

## ใบสั่งงานเสียง (audio_order.md)

ทำให้ผู้ใช้สร้างเสียงได้โดยไม่ต้องเดา ทุกตอนใช้รูปแบบนี้:

````markdown
# EP01: ใบสั่งงานเสียง

## เสียงพากย์: สร้างที่ Google AI Studio (Gemini TTS)
เสียงที่ใช้: [ชื่อเสียงจาก Brief]

### EP01_VO01.wav
ความยาวประมาณ: 8 วินาที
อารมณ์: เล่าให้เพื่อนฟัง กวนนิดๆ
บท: "..."

## เพลง: สร้างที่ Suno (โหมด Advanced ไม่ใส่เนื้อเพลง ใส่แค่ Style)
### EP01_BGM.mp3
Style: ...
ความยาวที่ต้องการ: อย่างน้อย 90 วินาที

## วางไฟล์ที่
- เสียงพากย์: 04_Episodes/EP01_Name/voice/
- เพลง: 04_Episodes/EP01_Name/music/
````

## ให้ AI สร้างเสียงและเพลง (เมื่อผู้ใช้ขอเท่านั้น)

ทางปกติคือผู้ใช้สร้างเสียงบรรยายด้วย Google AI Studio และเพลงด้วย Suno แล้วนำไฟล์มาวางเอง ห้ามเสนอเครื่องมือในหัวข้อนี้เป็นทางเลือก ใช้เฉพาะเมื่อผู้ใช้เป็นฝ่ายขอให้ทำให้

### เสียงบรรยาย: Gemini TTS

สร้าง `voice_lines.json` ในโฟลเดอร์ตอน แล้วสั่ง:

```bash
python scripts/generate_voice.py --lines 04_Episodes/EP01_Name/voice_lines.json
```

```json
{
  "voice": "Aoede",
  "style": "friendly and playful, relaxed pace",
  "lines": [{"file": "EP01_VO01.wav", "text": "..."}]
}
```

- ใช้โมเดล `gemini-3.8-flash-tts` เพราะรุ่น Flash-Lite ไม่รองรับภาษาไทย
- ได้ไฟล์ WAV 24 kHz โมโน และจะข้ามไฟล์ที่มีอยู่แล้ว เพื่อไม่ทับเทคที่ผู้ใช้เลือก
- ถ้า Google เปลี่ยนชื่อโมเดล ให้แก้ค่า `MODEL` ในสคริปต์
- เสียงที่ได้มักยาวกว่าที่ประเมินจากบทราว 1 วินาทีต่อท่อน ให้ใช้ความยาวจริงจากไฟล์ตอนวางไทม์ไลน์
- ให้ผู้ใช้ฟังคำเฉพาะและชื่อสถานที่ทุกครั้ง เพราะเอเจนต์ฟังเองไม่ได้

### เพลง: Lyria (แทน Suno)

```bash
python scripts/generate_music.py --prompt "warm acoustic guitar, soft piano" --seconds 60 --out 04_Episodes/EP01_Name/music/EP01_BGM.mp3
```

- สคริปต์จะสั่งให้เป็นเพลงไม่มีเสียงร้องเสมอ และไม่เขียนทับไฟล์เดิม
- เพลงที่ได้ดังมาก (ทดสอบได้ราว -11.5 LUFS, Peak +0.1 dB) ต้องปรับระดับก่อนมิกซ์เสมอ
- ใส่ `--clip` เพื่อลองทิศทางเพลงแบบ 30 วินาทีก่อน แล้วค่อยสร้างตัวจริง
- เพลงมีลายน้ำ SynthID ที่หูไม่ได้ยิน และต้องตรวจเงื่อนไขการใช้เชิงพาณิชย์ของ Google ก่อนลงช่องที่หารายได้

## การตั้งชื่อ

| ประเภท | รูปแบบ | ตัวอย่าง |
|---|---|---|
| เสียงพากย์ | `EPxx_VOnn.wav` | `EP01_VO02.wav` |
| เพลง | `EPxx_BGM.mp3` | `EP01_BGM.mp3` |
| เพลงหลายท่อน | `EPxx_BGM_A.mp3` | `EP01_BGM_B.mp3` |

ถ้าโหลด WAV จาก Suno ได้ให้ใช้ WAV และเปลี่ยนนามสกุลตามจริง

## Prompt เพลงตั้งต้น

เลือกให้ตรงกับ Style และปรับตามตอน Suno ไม่มีสวิตช์ Instrumental แล้ว ให้เข้าโหมด Advanced ไม่ใส่เนื้อเพลง และใส่แค่ Style จะได้เพลงที่ไม่มีเสียงร้อง ซึ่งจำเป็นเพราะเสียงร้องจะแย่งเสียงพูด

- สนุกโบ๊ะบ๊ะ: `Quirky comedy funk, playful slap bass, cheerful horns, bouncy rhythm, instrumental`
- สดใส: `Acoustic pop, ukulele, light whistling, soft bouncy drum beat, happy travel vlog, instrumental`
- เย็นอบอุ่น: `Warm chillhop, acoustic guitar, soft lofi beat, golden hour, peaceful, instrumental`

## SFX

เก็บที่ `05_Shared_Assets/sfx/` แยกโฟลเดอร์ตามประเภท และบันทึกชื่อแหล่ง ลิงก์ และสัญญาอนุญาตใน `SOURCES.md`

แหล่งที่ใช้ได้ ต้องตรวจเงื่อนไขล่าสุดก่อนดาวน์โหลดทุกครั้ง:

- [Kenney](https://kenney.nl/assets/category:Audio): มีรายงานว่าเป็น CC0
- [Mixkit](https://mixkit.co/free-sound-effects/cartoon/): มีหมวด Cartoon และ Funny ใช้ License ของ Mixkit
- Freesound: เลือกเฉพาะไฟล์ CC0

## เป้าหมายการมิกซ์

วัดระดับต้นทางก่อนมิกซ์ เพราะตัวคูณอย่าง 1.35x ไม่มีความหมายถ้าไม่รู้ว่าไฟล์เดิมดังแค่ไหน ค่าด้านล่างเป็นจุดเริ่มต้น

| เลเยอร์ | เป้าหมาย |
|---|---|
| เสียงพากย์ | ประมาณ -16 LUFS |
| เสียงจริงช่วงมุก | ประมาณ -16 LUFS |
| เสียงบรรยากาศ | หรี่ราว -18 dB หลังคลีนเสียง |
| เพลงตอนไม่มีเสียงพูด | ประมาณ -20 LUFS |
| เพลงตอนมีเสียงพูด | ลดลงอีกราว 11 dB |
| Master | -14 LUFS, True Peak ไม่เกิน -1 dB |

- Ducking สร้างจากตำแหน่งเสียงพูดในไทม์ไลน์ ไม่พิมพ์เวลาเอง
- คลีนเสียงกล้องด้วย `highpass`, `afftdn`, `acompressor`
- จัดน้ำหนัก SFX ตามประเภท: จังหวะกระแทกเด่นสุด ซับปกติเบาหรือไม่มี
