# Editing grammar

These rules apply to every style. Numbers are working defaults: follow them unless the user or the footage gives a reason not to, and say so when you depart from them.

## Length and pace

| | Vertical | Horizontal |
|---|---|---|
| Target length | 45-60 s | 60-150 s |
| Hard maximum (QA fails above) | 90 s | 180 s |
| Average shot | 2-4 s | 3-5 s |
| Longest shot without a punch, move, graphic or cut inside it | 5 s | 7 s |
| Shots in the episode | 15-25 | 20-40 |

- Something must change on screen at least every 3 s: a cut, a punch, a move, or a graphic arriving.
- There is no minimum length. A 35 s episode that lands is better than a padded 60 s one.
- Scenic and emotional episodes (soft, journal, filmroll, magazine) may run slower: average shot 4-6 s, longest 8 s.

## Structure

1. **Hook, 0-3 s.** The best moment of the episode, cut before its payoff, with a short line of on-screen text (a question or a tease, at most 12 characters) inside the first second, because most viewers start with the sound off. Never open with a title card, an arrival shot or a greeting. Hook shots are at most 2 s each.
2. **Build.** Set up who, where and what the mission is in one or two shots with a `label`, then the story in order. One running gag per episode (a `score`, a repeated comment) is enough.
3. **Payoff.** The moment the hook promised, played in full. This is where the full-frame shot, the punch, the music stop and the replay go.
4. **Ending.** Stop on the payoff or a reaction to it, held 0.5-1 s. No sign-off card and no "subscribe". When it can be done honestly, end on a picture or line that leads back into the hook, so the loop replays smoothly.

## Techniques

| Technique | When | How (timeline) |
|---|---|---|
| J-cut | Pull viewers into the next scene | `audio.lead` on the next shot |
| L-cut | Hold a feeling or show a reaction | `audio.tail` on the shot |
| Punch-in | Land a joke or a word | `punches` with `dur`, `scale` 1.2-1.4, at the source time of the word |
| Slow push-in | Tension before a reveal, emotion, scenery | `move` with `scale` 1.08-1.15 over 3-6 s |
| Pan or pull-out | Show a wide place, reveal what is next to the subject | `zoom` as the start framing, `move` as the end |
| Instant replay | A moment worth seeing twice; once per episode | repeat shot, `speed: 0.5`, tighter `zoom`, `mute`, `rewind` SFX, a label |
| Freeze frame | Introduce someone, hold a funny face | `hold: 1` with a `tag` or `stamp` |
| Reaction insert | After a joke | cut to the listener for 1-1.5 s |
| Beat before the punchline | Before a reveal | 0.3-0.5 s with no graphic and no voiceover |
| Music stop | The biggest joke or reveal; once or twice per episode | `music_cuts` for 0.3-0.8 s around the line |
| Speed ramp | Travel, running, getting to the point | `speed` as key points; `mute` or `bed` and a `whoosh` |
| Full-frame shot (vertical) | The one to three peak moments | `fill: true` |
| Transition | Change of place only; at most 3 per episode, never in the first 3 s | `transition` cue |
| Colour grade | One mood for the episode, matching clips from different cameras | top-level `grade`, per-shot `grade` to fix mismatches |

A trick repeated too often stops working. Apart from punch-ins and J/L cuts, use each technique at most the number of times given above.

## Three caption layers

1. **Speech:** lets viewers follow with the sound off. Colour by speaker (palette in [timeline-schema.md](./timeline-schema.md)) instead of writing names in front. Highlight at most one key word per caption.
2. **Impact words:** the punchline word or two, big.
3. **Editor comment:** teases or adds to the picture; never repeats what is already heard or seen.

## Real sound and voiceover

Let people deliver their own jokes. Voiceover sets up and links scenes; it never talks over a joke or gives the punchline away. Keep voiceover to at most a third of the episode's length.

## Vertical format

A 9:16 crop of a 1080p clip keeps about 32% of the width and needs 1.78x enlargement, so the vertical layout is the horizontal picture in a window with text in the bars. The window (`video_window`) is one setting for the whole episode. Single shots can break out of it with `fill: true`, which covers the whole frame and hides the bars; keep that for close-ups and peak moments, because the crop is soft on 1080p footage and loses the sides of the picture. Otherwise get closer with `zoom`, `move` or `punches` inside the window. Recommend shooting 4K next time when punch-ins matter.
