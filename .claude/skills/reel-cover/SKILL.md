---
name: reel-cover
description: >-
  Turn an uploaded video into a scroll-stopping Instagram Reels cover
  (thumbnail). Watches the video to understand the topic and mood, picks the
  creator's best-matching facial expression from their uploaded face photos,
  and composites a 1080x1920 (9:16) cover with a big bold 3-5 word headline on
  a topic-styled background. Use whenever the user uploads a video/reel and asks
  for a thumbnail, cover, or "make me a thumbnail for this reel."
---

# Reel Cover — video → Instagram Reels thumbnail

This is the master workflow for building Instagram Reels covers. The user
uploads a **video** and one or more **face photos** (their "character" — a set
of expressions). You watch the video, understand what it's about, choose the
expression that matches its energy, and produce a finished 9:16 cover with a
punchy headline.

## The deal (what the user wants every time)

- Aspect ratio: **1080 × 1920, 9:16** (Reels/Stories native). Not 4:3, not 16:9.
- Headline: **3–5 words max**, big and bold, one word optionally highlighted.
- The creator's **face**, cut out and placed on a **topic-styled background**.
- The **expression matches the video's mood** (hype video → wide-eyed/shocked;
  serious/business → straight face; funny → smirk, etc.).

## Setup (run once per session — the container is fresh each time)

```bash
bash .claude/skills/reel-cover/scripts/setup.sh
```

This installs Pillow, a static ffmpeg (`imageio-ffmpeg`), `rembg` +
`onnxruntime` for background removal, the u2net model (from a mirror, because
the default source is usually blocked), and best-effort `faster-whisper`. Fonts
(Anton, Montserrat) are bundled in `assets/fonts/`. If setup partially fails,
the scripts degrade gracefully (see "If something isn't available").

## Workflow

### 1. Understand the video

Run the analyzer to pull keyframes + audio:

```bash
python3 .claude/skills/reel-cover/scripts/analyze_video.py \
    --video <path-to-uploaded-video> --out /tmp/reelwork --frames 9 --transcribe
```

- **Read the extracted keyframes** (`/tmp/reelwork/frames/*.jpg`) to see the
  setting, the creator's look, and any on-screen text.
- If a `transcript` came back, use it to nail the exact topic. If it's `null`,
  rely on the frames and **ask the user for a one-line topic** rather than
  guessing wrong.
- Decide three things and state them back to the user briefly:
  1. **Topic** (one sentence).
  2. **Mood → palette** (see palette table below).
  3. **Headline** — 3–5 punchy words, a hook not a summary. Front-load the
     curiosity/number. Examples: `I QUIT MY 9-5`, `THIS CHANGED EVERYTHING`,
     `STOP DOING THIS`, `HOW I MADE 10K`.

### 2. Pick the matching expression

The user uploads face photos (or keeps a library in `assets/faces/`). **Read
each candidate photo** and choose the one whose expression fits the mood:

| Video mood | Expression to pick |
|------------|--------------------|
| Shock / big claim / challenge | wide eyes, raised brows, mouth open |
| Business / money / "how I did X" | calm, straight, confident |
| Funny / casual | smirk / half-smile |
| Intense / discipline / warning | serious, jaw set, looking into lens |
| Thoughtful / storytime | hand-on-chin / "thinking" |

Front-facing shots composite best. Save the chosen file somewhere concrete
(e.g. `/tmp/reelwork/face.png`).

### 3. Build the cover

```bash
python3 .claude/skills/reel-cover/scripts/make_thumbnail.py \
    --face /tmp/reelwork/face.png \
    --text "HOW I MADE 10K" \
    --highlight "10K" \
    --palette money \
    --font anton \
    --side center \
    --out /tmp/reelwork/cover.png
```

Key flags (`--help` lists all):
- `--text` the headline (keep it 3–5 words; it auto-fits and wraps).
- `--highlight` one word to color in the accent (great for numbers/keywords).
- `--palette` one of: `hype money tech fitness mindset danger clean night`.
- `--font` `anton` (condensed, aggressive) or `montserrat` (cleaner, bold).
- `--side` `left|center|right` — where the subject stands.
- `--subject-scale` 0.6–0.85 — shrink toward 0.6 if the head crowds the text.
- `--bg` optional custom background image (overrides the palette gradient).
- `--text-pos` `top|center|bottom`.

### 4. Review, then deliver

- **Open the output and look at it.** Check: is the head clipping the text? Is
  the cutout clean around the hair? Does the headline fit? If the head crowds
  the headline, lower `--subject-scale` or set `--text-pos top` and re-run.
- Send the finished PNG to the user with `SendUserFile`.
- Offer 1–2 quick variants (different expression, palette, or headline) so they
  can pick. Iterating is cheap — re-run with different flags.

## Palette guide (mood/topic → background)

| Palette | Use for |
|---------|---------|
| `hype` | reactions, challenges, "I tried…", high energy (orange/red, yellow accent) |
| `money` | business, finance, side-hustle (deep green, green accent) |
| `tech` | AI, gadgets, coding (navy/blue, cyan accent) |
| `fitness` | gym, discipline, health (red/black) |
| `mindset` | motivation, psychology, self-improvement (indigo, purple accent) |
| `danger` | mistakes, warnings, drama (red/black, red accent) |
| `clean` | minimal / lifestyle / luxury (light grey, dark text) |
| `night` | versatile dark default (near-black, mint accent) |

Override the accent with `--accent "#RRGGBB"` if the topic wants a specific color.

## Headline rules

- 3–5 words. If a 6th word sneaks the point across, cut a filler word first.
- ALL CAPS reads loudest at thumbnail size (the script uppercases for you).
- It's a **hook**, not a description. Curiosity, a number, a bold claim, or a
  "stop/don't" command beats a neutral title.
- Highlight the single most clickable word (a number, a stakes word) via
  `--highlight`.

## Building a permanent face library (optional, recommended)

If the user wants to stop re-uploading the same photos, save their expression
set once into `assets/faces/` with descriptive names, e.g.
`shocked.png`, `serious.png`, `smirk.png`, `thinking.png`. Then step 2 becomes
"pick the file whose name matches the mood." See `assets/faces/README.md`.

## Design deep-dive

For text sizing, Reels safe zones (keep the headline clear of the bottom ~18%
caption/UI band and top ~8%), contrast, and composition, read
`references/design.md`.

## If something isn't available

- **rembg / u2net missing** → the face is placed uncut. Still works; just less
  clean. Re-run `setup.sh`, or accept the framed look.
- **ffmpeg/analyzer fails** → ask the user to describe the topic and pick an
  expression manually, then go straight to step 3.
- **transcription null** → normal; use the frames + a one-line topic from the user.
- **fonts missing** → the script falls back to a system bold font automatically.
