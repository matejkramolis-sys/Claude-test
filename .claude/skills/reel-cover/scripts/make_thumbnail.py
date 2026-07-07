#!/usr/bin/env python3
"""
make_thumbnail.py — Instagram Reels cover generator.

Composites a creator's face cutout onto a topic-styled background with a big
bold headline. Output is a 1080x1920 (9:16) PNG, the native Reels cover ratio.

Pipeline:  background  ->  glow behind subject  ->  face cutout  ->  headline text.

Typical use (called by the reel-cover skill after it has picked the best
expression photo and written the hook):

    python3 make_thumbnail.py \
        --face assets/faces/surprised.png \
        --text "I QUIT MY JOB" \
        --palette hype \
        --out cover.png

Design knobs are documented in --help. Everything degrades gracefully: if
rembg is missing the face is placed uncut; if a bundled font is missing it
falls back to a system bold font.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

W, H = 1080, 1920  # Reels cover canvas (9:16)
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "..", "assets", "fonts")

# Mood/topic -> background gradient (top hex, bottom hex) + accent color.
# Accent is used for the highlight bar / keyword and should pop against text.
PALETTES = {
    "hype":     ("#FF5722", "#7A1500", "#FFD23F"),   # energy, challenges, reactions
    "money":    ("#0B3D2E", "#02120C", "#33D17A"),   # business, finance, hustle
    "tech":     ("#1B2A4A", "#05070F", "#4CC9F0"),   # tech, ai, gadgets
    "fitness":  ("#B00020", "#0A0000", "#FF3B3B"),   # gym, discipline, health
    "mindset":  ("#1A237E", "#04061A", "#7C4DFF"),   # motivation, psychology
    "danger":   ("#7A0000", "#000000", "#FF2A2A"),   # warnings, mistakes, drama
    "clean":    ("#EDEFF3", "#B9C2CF", "#111827"),   # light/minimal, lifestyle
    "night":    ("#12141C", "#000000", "#00E5A0"),   # default dark, versatile
}
DEFAULT_PALETTE = "night"


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load_font(size, family="anton"):
    """Anton (condensed, punchy) by default; Montserrat for a cleaner look.
    Falls back to any system bold font so the script never hard-fails."""
    candidates = {
        "anton": ["Anton-Regular.ttf"],
        "montserrat": ["Montserrat-ExtraBold.ttf"],
    }.get(family, ["Anton-Regular.ttf"])
    for name in candidates:
        p = os.path.join(FONT_DIR, name)
        if os.path.exists(p):
            try:
                font = ImageFont.truetype(p, size)
                # Montserrat ships as a variable font that defaults to a thin
                # weight; force a heavy instance so headlines read as bold.
                if family == "montserrat":
                    for weight in ("ExtraBold", "Bold", "Black"):
                        try:
                            font.set_variation_by_name(weight)
                            break
                        except Exception:
                            continue
                return font
            except OSError:
                pass
    for sysfont in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ):
        if os.path.exists(sysfont):
            return ImageFont.truetype(sysfont, size)
    return ImageFont.load_default()


def make_gradient(top, bottom):
    """Vertical gradient canvas."""
    top, bottom = hex2rgb(top), hex2rgb(bottom)
    base = Image.new("RGB", (1, H))
    px = base.load()
    for y in range(H):
        t = y / (H - 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return base.resize((W, H))


def cover_fit(img, w, h):
    """Scale+crop an image to exactly fill w x h (like CSS background-size:cover)."""
    img = ImageOps.exif_transpose(img).convert("RGB")
    scale = max(w / img.width, h / img.height)
    img = img.resize((int(img.width * scale), int(img.height * scale)))
    x = (img.width - w) // 2
    y = (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


def strip_letterbox(img):
    """Crop uniform near-black bars (top/bottom/sides) left by phone
    video-screenshots, so they don't leak into the cutout."""
    gray = img.convert("L")
    px = gray.load()
    w, h = gray.size

    def row_dark(y):
        return sum(px[x, y] for x in range(0, w, max(1, w // 40))) / (w // max(1, w // 40) + 1) < 18

    def col_dark(x):
        return sum(px[x, y] for y in range(0, h, max(1, h // 40))) / (h // max(1, h // 40) + 1) < 18

    top = 0
    while top < h // 2 and row_dark(top):
        top += 1
    bot = h - 1
    while bot > h // 2 and row_dark(bot):
        bot -= 1
    left = 0
    while left < w // 2 and col_dark(left):
        left += 1
    right = w - 1
    while right > w // 2 and col_dark(right):
        right -= 1
    if right - left > w * 0.3 and bot - top > h * 0.3:
        return img.crop((left, top, right + 1, bot + 1))
    return img


def cutout_subject(face_path):
    """Return an RGBA image of the subject with background removed.
    Uses rembg if available; otherwise returns the original RGBA (no cutout)."""
    src = strip_letterbox(ImageOps.exif_transpose(Image.open(face_path))).convert("RGBA")
    try:
        from rembg import remove
        return remove(src)
    except Exception as e:  # rembg missing or model download failed
        sys.stderr.write(f"[make_thumbnail] rembg unavailable ({e}); using uncut photo\n")
        return src


def trim_alpha(img):
    """Crop transparent padding around a cutout so scaling is tight to the subject."""
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img


def radial_glow(color, strength=170):
    """Soft radial glow to separate the subject from the background."""
    glow = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(glow)
    cx, cy, r = W // 2, int(H * 0.62), int(W * 0.6)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=strength)
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    layer = Image.new("RGB", (W, H), hex2rgb(color))
    out = Image.new("RGB", (W, H))
    return Image.composite(layer, out, glow), glow


def wrap_to_lines(text, font, draw, max_w, max_lines=3):
    """Greedy word wrap to fit max_w; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines[:max_lines]


def draw_headline(canvas, text, accent, position="top", family="anton",
                  highlight=None):
    """Auto-fit a bold uppercase headline into the safe zone with heavy stroke.
    `highlight` (optional word/phrase) is drawn in the accent color."""
    draw = ImageDraw.Draw(canvas)
    text = text.upper()
    margin = 70
    max_w = W - 2 * margin
    # Reels UI (caption, buttons) sits bottom ~18% and top ~8%; keep text clear of it.
    band_top = int(H * 0.10)
    band_h = int(H * 0.30)

    size = 200
    while size > 60:
        font = load_font(size, family)
        lines = wrap_to_lines(text, font, draw, max_w)
        line_h = int(size * 1.06)
        total_h = line_h * len(lines)
        widest = max((draw.textlength(ln, font=font) for ln in lines), default=0)
        if widest <= max_w and total_h <= band_h:
            break
        size -= 6

    font = load_font(size, family)
    lines = wrap_to_lines(text, font, draw, max_w)
    line_h = int(size * 1.06)
    total_h = line_h * len(lines)

    if position == "top":
        y0 = band_top
    elif position == "bottom":
        y0 = int(H * 0.60)
    else:  # center-ish upper third
        y0 = band_top + (band_h - total_h) // 2

    stroke = max(6, size // 16)
    accent_rgb = hex2rgb(accent)
    hl = (highlight or "").upper()
    for i, line in enumerate(lines):
        lw = draw.textlength(line, font=font)
        x = (W - lw) // 2
        y = y0 + i * line_h
        # per-word so the highlight word can be accent-colored
        cx = x
        for word in line.split():
            fill = accent_rgb if (hl and word.strip(".,!?") == hl.strip(".,!?")) else (255, 255, 255)
            draw.text((cx, y), word, font=font, fill=fill,
                      stroke_width=stroke, stroke_fill=(0, 0, 0))
            cx += draw.textlength(word + " ", font=font)
    return canvas


def build(args):
    # 1. Background
    if args.bg and os.path.exists(args.bg):
        canvas = cover_fit(Image.open(args.bg), W, H)
    else:
        pal = PALETTES.get(args.palette, PALETTES[DEFAULT_PALETTE])
        canvas = make_gradient(pal[0], pal[1])
    canvas = canvas.convert("RGB")

    pal = PALETTES.get(args.palette, PALETTES[DEFAULT_PALETTE])
    accent = args.accent or pal[2]

    # 2. Glow behind subject
    glow_rgb, glow_mask = radial_glow(accent, strength=150)
    canvas = Image.composite(
        Image.blend(canvas, glow_rgb, 0.35), canvas, glow_mask)

    # 3. Subject cutout
    subj = trim_alpha(cutout_subject(args.face))
    # Scale subject to a target height and anchor to the bottom.
    target_h = int(H * args.subject_scale)
    scale = target_h / subj.height
    subj = subj.resize((int(subj.width * scale), int(subj.height * scale)))
    if args.side == "left":
        sx = int(W * 0.04)
    elif args.side == "right":
        sx = W - subj.width - int(W * 0.04)
    else:
        sx = (W - subj.width) // 2
    sy = H - subj.height + int(H * 0.02)  # slight overflow off bottom edge
    # soft contact shadow
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", subj.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 160), (0, 0), subj)
    shadow.paste(sh, (sx + 14, sy + 18), sh)
    shadow = shadow.filter(ImageFilter.GaussianBlur(22))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), shadow)
    canvas.paste(subj, (sx, sy), subj)
    canvas = canvas.convert("RGB")

    # 4. Headline
    canvas = draw_headline(canvas, args.text, accent, position=args.text_pos,
                           family=args.font, highlight=args.highlight)

    canvas.save(args.out, "PNG")
    print(f"Saved {args.out} ({W}x{H}) palette={args.palette} font={args.font}")


def main():
    p = argparse.ArgumentParser(description="Generate a 1080x1920 Reels cover.")
    p.add_argument("--face", required=True, help="path to the chosen expression photo")
    p.add_argument("--text", required=True, help="headline (3-5 words works best)")
    p.add_argument("--out", default="cover.png")
    p.add_argument("--palette", default=DEFAULT_PALETTE,
                   choices=list(PALETTES.keys()), help="mood/topic background preset")
    p.add_argument("--accent", help="override accent hex, e.g. #FFD23F")
    p.add_argument("--highlight", help="one word from --text to color with the accent")
    p.add_argument("--bg", help="optional custom background image (overrides palette)")
    p.add_argument("--font", default="anton", choices=["anton", "montserrat"])
    p.add_argument("--text-pos", dest="text_pos", default="top",
                   choices=["top", "center", "bottom"])
    p.add_argument("--side", default="center", choices=["left", "center", "right"],
                   help="which side the subject stands on")
    p.add_argument("--subject-scale", type=float, default=0.72,
                   help="subject height as fraction of canvas (0.6-0.85)")
    build(p.parse_args())


if __name__ == "__main__":
    main()
