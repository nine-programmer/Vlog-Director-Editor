# Editing grammar

Pick by style and story. One episode does not need every technique; a trick repeated too often stops working.

## Hook

The first 3 seconds must make people curious or smile. Open with the best moment of the episode and cut before the payoff. Never open with a title card or an arrival shot.

## Timing techniques

| Technique | When | How (timeline) |
|---|---|---|
| J-cut | Pull viewers into the next scene | `audio.lead` on the next shot |
| L-cut | Hold a feeling or show a reaction | `audio.tail` on the shot |
| Punch-in | Land a joke or a word | `punches`, 1.15-1.4x on 1080p sources |
| Instant replay | A moment worth seeing twice | repeat shot, `speed: 0.5`, `zoom`, mute, rewind SFX, replay label |
| Freeze frame | Introduce someone, hold a funny face | `hold: 1` |
| Reaction insert | After a joke | cut to the listener |
| Beat before the punchline | Before a reveal | 0.3-0.5 s without graphics or voice |
| Speed ramp | Travel, running away, getting to the point | `speed` as a list of key points: fast, then glide to 1 just before the key moment; mute or bed the sound and add a `whoosh` |
| Slow push-in | Tension before a reveal, emotion, scenery | `move` with `scale` 1.08-1.15 over 3-6 s |
| Pan or pull-out | Show a wide place, reveal what is next to the subject | `zoom` as the start framing, `move` as the end |
| Full-frame shot (vertical) | The one to three peak moments of an episode | `fill: true` |
| Colour grade | Give the episode one mood, match clips from different cameras | top-level `grade`, per-shot `grade` to fix mismatches |
| Transition | Change of place | `transition` cue in the style's variant |

## Three caption layers

1. **Speech:** lets viewers follow. Colour by speaker instead of writing names in front.
2. **Impact words:** the punchline word, big.
3. **Editor comment:** teases or adds to the picture; never repeats what is already heard.

## Real sound and voiceover

Let people deliver their own jokes. Voiceover sets up and links scenes; it never talks over a joke or gives the punchline away.

## Vertical format

A 9:16 crop of a 1080p clip keeps about 32% of the width and needs 1.78x enlargement, so the vertical layout is the horizontal picture in a window with text in the bars. The window (`video_window`) is one setting for the whole episode. Single shots can break out of it with `fill: true`, which covers the whole frame and hides the bars; keep that for close-ups and peak moments, because the crop is soft on 1080p footage and loses the sides of the picture. Otherwise get closer with `zoom`, `move` or `punches` inside the window. Recommend shooting 4K next time when punch-ins matter.
