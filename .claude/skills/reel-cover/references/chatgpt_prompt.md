# ChatGPT image prompt — reference

The primary path (option A): instead of compositing locally, we hand the user a
tailored English prompt they paste into **their own ChatGPT** (image
generation), with one of their face photos attached. Best quality, no extra
cost beyond their existing subscription.

`scripts/build_prompt.py` assembles the prompt from parameters. This file is
the cheat-sheet for filling those parameters well.

## The parameters

| Param | What to put |
|-------|-------------|
| `--headline` | 3–5 word hook, ALL CAPS (a curiosity/number/claim, not a summary) |
| `--highlight` | the single most clickable word (a number, stakes word) |
| `--expression` | describe the face to match the mood (see table) |
| `--scene` | the background/environment based on the video topic (see ideas) |
| `--accent` | color name for the highlight word + mood (see table) |
| `--side` | where the person stands (`right`/`left` opens space for text) |
| `--photo` | filename of the chosen face photo to attach in ChatGPT |

## Expression ↔ mood (for `--expression`)

| Video mood | `--expression` value |
|------------|----------------------|
| Shock / big claim / challenge | `wide eyes, raised eyebrows, mouth slightly open, surprised` |
| Business / money / how-to | `calm, confident, slight smirk, looking straight into the lens` |
| Funny / casual | `relaxed half-smile, playful smirk` |
| Intense / discipline / warning | `serious, jaw set, intense stare into the lens` |
| Story / reflective | `thoughtful, hand near chin, curious` |

## Scene ideas (for `--scene`) — match the topic

- **Fitness / gym** → `dark moody gym, dramatic side lighting, dumbbells blurred in background`
- **Money / business** → `sleek modern office, city skyline through the window at dusk, warm rim light`
- **Tech / AI** → `futuristic dark room with glowing blue screens and neon UI holograms`
- **Travel / lifestyle** → `sunny scenic location matching the destination, vibrant, golden hour`
- **Mindset / motivation** → `moody dramatic studio, single strong spotlight, deep shadows`
- **Food / cooking** → `warm rustic kitchen, shallow depth of field, appetising`
- **Drama / storytime / warning** → `dark background with a red glow, tense cinematic mood`
- **Neutral / clean** → `bold solid color or gradient studio backdrop`

Keep scenes short and concrete. Let the model handle the cinematics.

## Accent color (for `--accent`)

Yellow/orange = energy & general; green = money; cyan/blue = tech; red = danger/intensity;
purple = mindset. Pick whatever pops against the scene.

## Worked example

```bash
python3 scripts/build_prompt.py \
    --headline "I TRIED THIS FOR 30 DAYS" --highlight "30" \
    --expression "wide eyes, raised eyebrows, mouth slightly open, surprised" \
    --scene "dark moody gym, dramatic side lighting, dumbbells blurred behind" \
    --accent "bright yellow" --side center --photo shocked.png
```

## After the user generates it

- ChatGPT's output may not be exactly 1080×1920 — if they send it back, crop/pad
  to 9:16 with `make_thumbnail.py --bg <image>` (no text) or a quick Pillow crop.
- If the face drifts from their likeness, tell them to reply in ChatGPT:
  "keep the face identical to the attached photo" and regenerate.
- If text comes out garbled (image models sometimes misspell), tell them to
  regenerate, or add the headline afterwards with `make_thumbnail.py`.
- Offer 2 prompt variants (different headline / expression / scene) so they can
  try a couple and pick the winner.
