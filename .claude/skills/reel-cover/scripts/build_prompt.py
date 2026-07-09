#!/usr/bin/env python3
"""
build_prompt.py — assemble a ready-to-paste image-generation prompt for
ChatGPT (gpt-image-1 / "the ChatGPT image generator"), so the user can create
the Reels cover inside their own ChatGPT subscription (no API key needed).

The reel-cover skill fills these from the video analysis + chosen expression,
runs this, and hands the user the printed prompt + which photo to attach.

Example:
    python3 build_prompt.py \
        --headline "HOW I MADE 10K" --highlight "10K" \
        --expression "calm, confident, slight smile, looking into the lens" \
        --scene "sleek modern office, city skyline through the window at dusk" \
        --accent "vivid green" --side right --photo serious.png
"""
import argparse
import textwrap


def build(a):
    hl = ""
    if a.highlight:
        hl = (f' Render the word "{a.highlight.upper()}" in {a.accent}; '
              f"keep the rest of the headline white.")
    photo = (f'\n\nATTACH THIS PHOTO in ChatGPT before sending: {a.photo}'
             if a.photo else "")

    prompt = f"""\
Create a vertical 9:16 Instagram Reels cover thumbnail, 1080x1920, ultra sharp and readable even as a small thumbnail.

PERSON: Use the attached photo as the exact same person — keep his face, hair, and likeness identical to the photo. Do not change his identity. His expression should be: {a.expression}. Frame him from roughly chest/shoulders up, positioned on the {a.side} of the frame, sharply lit and clearly separated from the background.

BACKGROUND / SCENE: {a.scene}. Cinematic lighting, strong contrast, slightly darkened behind the text so the headline stays readable. High production value, bold and saturated, YouTube/MrBeast-thumbnail energy.

HEADLINE TEXT: Add the headline "{a.headline.upper()}" in a heavy condensed bold sans-serif (Anton / Impact style), ALL CAPS, white with a thick black outline, placed in the top third of the frame.{hl} Keep the text large, inside the safe area, and NOT covering the person's face.

RULES: No watermarks, no logos, no captions, no extra text besides the headline. Keep the person's face fully visible. Vertical 9:16 only.{photo}"""
    return prompt


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--headline", required=True, help="3-5 word hook")
    p.add_argument("--highlight", help="one word to color with the accent")
    p.add_argument("--expression", default="confident, looking into the lens",
                   help="facial expression matching the video mood")
    p.add_argument("--scene", default="clean gradient studio background",
                   help="background / environment based on the topic")
    p.add_argument("--accent", default="bright yellow", help="accent color name")
    p.add_argument("--side", default="center", choices=["left", "center", "right"])
    p.add_argument("--photo", help="filename of the face photo to attach in ChatGPT")
    a = p.parse_args()

    print("=" * 70)
    print("COPY EVERYTHING BELOW INTO CHATGPT (with the photo attached):")
    print("=" * 70)
    print(build(a))
    print("=" * 70)


if __name__ == "__main__":
    main()
