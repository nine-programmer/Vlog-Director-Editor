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
| Speed-up | Travel, running away | `speed` is constant for a whole shot: split the action into two shots of the same clip, the first at `speed: 1.5-2`, the second at 1 from the key moment |
| Transition | Change of place | `transition` cue in the style's variant |

## Three caption layers

1. **Speech:** lets viewers follow. Colour by speaker instead of writing names in front.
2. **Impact words:** the punchline word, big.
3. **Editor comment:** teases or adds to the picture; never repeats what is already heard.

## Real sound and voiceover

Let people deliver their own jokes. Voiceover sets up and links scenes; it never talks over a joke or gives the punchline away.

## Vertical format

A 9:16 crop of a 1080p clip keeps about 32% of the width and needs 1.78x enlargement, so the vertical layout is the horizontal picture in a window with text in the bars. The window (`video_window`) is one setting for the whole episode; it cannot go full-screen for single shots. Get closer on a shot with `zoom` or `punches` inside the window instead. Recommend shooting 4K next time when punch-ins matter.
