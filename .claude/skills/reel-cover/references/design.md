# Reel cover design notes

Reference for making the covers actually stop the scroll. The
`make_thumbnail.py` engine already encodes most of this; this file explains the
*why* so you can tune flags well.

## Canvas & safe zones

- Canvas is **1080 × 1920 (9:16)**. This is the native Reels cover / feed-post
  crop for vertical video. Don't output square or landscape.
- Instagram overlays UI on the cover:
  - **Top ~8%**: profile row / sound.
  - **Bottom ~18%**: caption, username, action buttons, progress bar.
  - Keep the headline and the subject's face **inside the middle ~74%**. The
    engine places headlines in a band from ~10% to ~40% of the height and
    anchors the subject to the bottom (a little overflow off the edge is fine
    and looks intentional).

## Text

- **3–5 words.** At the size a cover is actually viewed (a thumbnail in a grid
  or the reels tab), more than ~5 words is unreadable.
- **ALL CAPS**, heavy weight, generous stroke/outline. The engine uses a black
  stroke ~1/16 of the font size so text survives on any background.
- **One highlight word** in the accent color pulls the eye to the hook (a
  number, a stakes word: `10K`, `30 DAYS`, `NEVER`).
- Auto-fit: the engine shrinks the font until the text fits the width and the
  height band, wrapping up to 3 lines. If it's coming out small, shorten the
  headline rather than fighting the sizer.
- Font choice: **Anton** = condensed, aggressive, MrBeast-style (default).
  **Montserrat ExtraBold** = cleaner, more premium/business.

## Subject

- Front-facing, eyes toward the lens composites and reads best.
- The cutout (rembg/u2net) is anchored bottom-center by default. Use `--side
  left/right` to open space for text on the opposite side (good for a strong
  side-profile or when text should sit beside the face).
- `--subject-scale` controls how much of the frame the person fills (0.6–0.85).
  If the head overlaps the headline, drop it toward 0.6.
- A soft radial glow + contact shadow (built in) separates the subject from the
  background so they don't look pasted on.

## Background

- Palettes are vertical gradients tuned per mood — dark backgrounds make white
  text and skin tones pop, which is why most palettes are dark.
- Provide `--bg <image>` to drop in a real environment/scene instead (it's
  cover-fitted to fill the frame). Darken busy backgrounds or the text stroke
  does the heavy lifting.

## Expression ↔ mood

Match energy, don't just pick a "good photo":
- Big claim / shock / challenge → wide eyes, raised brows.
- Money / how-to / authority → calm, straight, confident.
- Funny / casual → smirk.
- Intense / discipline → serious, locked-in stare.
- Story / reflective → hand-on-chin thinking pose.

## Quick QA before sending

1. Head not clipping the headline?
2. Cutout clean around hair/hands (no stray background, no leftover letterbox)?
3. Headline fits, ≤5 words, hook not summary?
4. Enough contrast — readable as a small thumbnail (shrink it mentally)?
5. Accent color matches the topic?
