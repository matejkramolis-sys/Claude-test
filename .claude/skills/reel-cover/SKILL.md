---
name: reel-cover
description: >-
  Turn an uploaded video into a scroll-stopping Instagram Reels cover
  (thumbnail). Watches the video to understand the topic and mood, picks the
  creator's best-matching facial expression from their uploaded face photos,
  and produces a ready-to-paste ChatGPT image-generation prompt (plus which
  photo to attach) so the user generates a high-end 9:16 cover inside their own
  ChatGPT subscription. A local Pillow compositor is available as a no-cost
  fallback. Use whenever the user uploads a video/reel and asks for a thumbnail,
  cover, or "make me a thumbnail for this reel."
---

# Reel Cover — video → Instagram Reels thumbnail

Master workflow for building Instagram Reels covers. The user uploads a
**video** and one or more **face photos** (their "character" — a set of
expressions). You watch the video, understand what it's about, choose the
expression that matches its energy, and hand them a **tailored ChatGPT image
prompt** that produces a finished 9:16 cover with their likeness, a
topic-based background, and a punchy headline.

## The deal (what the user wants every time)

- Aspect ratio: **1080 × 1920, 9:16** (Reels native). Not 4:3, not 16:9.
- Headline: **3–5 words max**, big and bold, one word highlighted.
- The creator's **face/likeness**, on a **topic-styled background/scene**.
- The **expression matches the video's mood**.

## Primary path (A): prompt → the user's own ChatGPT  ⭐ default

The user has a ChatGPT subscription but **no OpenAI API key** — and a ChatGPT
subscription does NOT grant API access. So we don't call any API. Instead we
generate a great prompt they paste into their ChatGPT app (image generation),
with a face photo attached. Best quality, no extra cost.

### Steps

1. **Understand the video.** Run the analyzer, then Read the frames:
   ```bash
   bash .claude/skills/reel-cover/scripts/setup.sh   # once per session (fresh container)
   python3 .claude/skills/reel-cover/scripts/analyze_video.py \
       --video <uploaded-video> --out /tmp/reelwork --frames 9 --transcribe
   ```
   Read `/tmp/reelwork/frames/*.jpg`. If `transcript` is null, ask the user for
   a one-line topic. Decide and state back: **topic**, **mood**, **headline**
   (3–5 word hook), and the **scene** + **accent color**.

2. **Pick the matching expression.** Read the user's uploaded face photos and
   choose the one that fits the mood (see `references/chatgpt_prompt.md` for the
   mood→expression table). Note its filename.

3. **Build the prompt:**
   ```bash
   python3 .claude/skills/reel-cover/scripts/build_prompt.py \
       --headline "HOW I MADE 10K" --highlight "10K" \
       --expression "calm, confident, slight smirk, looking into the lens" \
       --scene "sleek modern office, city skyline through the window at dusk" \
       --accent "vivid green" --side right --photo serious.png
   ```
   Fill every parameter from steps 1–2. `references/chatgpt_prompt.md` has the
   scene ideas, expression phrasings, and accent guidance.

4. **Hand it over.** Give the user the printed prompt block and tell them
   clearly: *"Paste this into ChatGPT and attach your `<photo>` photo."* Offer
   **2 variants** (different headline / scene / expression) so they can try a
   couple and pick the best.

5. **Iterate on their result.** If they paste the generated image back:
   - Face drifted from their likeness → tell them to reply "keep the face
     identical to the attached photo" and regenerate.
   - Text garbled → regenerate, or add the headline locally with the fallback
     compositor (`make_thumbnail.py --bg <their-image>` with no cutout).
   - Wrong ratio → crop/pad to 1080×1920.

## Fallback path (C): local compositor (no ChatGPT, no cost)

If the user wants something instantly without leaving the chat, or ChatGPT
isn't handy, composite locally. This looks flatter (designed gradient
background, not an AI scene) but is fully automatic:

```bash
python3 .claude/skills/reel-cover/scripts/make_thumbnail.py \
    --face /tmp/reelwork/face.png --text "HOW I MADE 10K" --highlight "10K" \
    --palette money --font anton --side center --out /tmp/reelwork/cover.png
```

See `references/design.md` for palettes, flags, and safe-zone rules. This path
is also useful to **add a headline onto** an AI image the user generated but
which came out without text.

## Optional path (B): direct API (only if the user provides an OpenAI key)

If the user later sets `OPENAI_API_KEY`, the same prompt from `build_prompt.py`
can be sent to `gpt-image-1` (`/v1/images/edits` with the face photo) to
automate step 4 fully. Costs ~$0.02–0.19/image. Not set up by default because
it requires their paid API billing.

## Headline rules

- 3–5 words, ALL CAPS. A **hook** (curiosity / number / bold claim /
  "stop"-command), not a description. Highlight the single most clickable word.

## Face library (optional)

The user can save their expression set once into `assets/faces/`
(`shocked.png`, `serious.png`, `smirk.png`, `intense.png`, `thinking.png`) so
they don't re-upload each time. See `assets/faces/README.md`.

## References

- `references/chatgpt_prompt.md` — prompt template, scene ideas, expression &
  accent tables (the main reference for path A).
- `references/design.md` — local compositor design + Reels safe zones (path C).
