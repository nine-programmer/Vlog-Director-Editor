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

## เพลง: สร้างที่ Suno (เปิด Instrumental)
### EP01_BGM.mp3
Style: ...
ความยาวที่ต้องการ: อย่างน้อย 90 วินาที

## วางไฟล์ที่
- เสียงพากย์: 04_Episodes/EP01_Name/voice/
- เพลง: 04_Episodes/EP01_Name/music/
````

## การตั้งชื่อ

| ประเภท | รูปแบบ | ตัวอย่าง |
|---|---|---|
| เสียงพากย์ | `EPxx_VOnn.wav` | `EP01_VO02.wav` |
| เพลง | `EPxx_BGM.mp3` | `EP01_BGM.mp3` |
| เพลงหลายท่อน | `EPxx_BGM_A.mp3` | `EP01_BGM_B.mp3` |

ถ้าโหลด WAV จาก Suno ได้ให้ใช้ WAV และเปลี่ยนนามสกุลตามจริง

## Prompt เพลงตั้งต้น

เลือกให้ตรงกับ Style และปรับตามตอน เปิด Instrumental เสมอ เพราะเสียงร้องจะแย่งเสียงพูด

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
