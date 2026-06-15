#!/usr/bin/env python3
"""Process raw HD photos into cinematic 16:9 backgrounds with gradient scrims
so white text stays legible — Apple-Keynote style."""
import os
from PIL import Image, ImageEnhance, ImageFilter

SRC = "assets/photos"
OUT = "assets/bg"
os.makedirs(OUT, exist_ok=True)

W, H = 2560, 1440  # 16:9 master

def cover(im, w, h):
    """Scale + center-crop to fill w x h."""
    sr, tr = im.width / im.height, w / h
    if sr > tr:  # source wider -> match height, crop width
        nh = h
        nw = round(im.width * h / im.height)
    else:
        nw = w
        nh = round(im.height * w / im.width)
    im = im.resize((nw, nh), Image.LANCZOS)
    left = (nw - w) // 2
    top = (nh - h) // 2
    return im.crop((left, top, left + w, top + h))

def vignette(im, strength=0.55):
    """Radial darkening toward edges."""
    mask = Image.new("L", (im.width, im.height), 0)
    px = mask.load()
    cx, cy = im.width / 2, im.height / 2
    maxd = (cx**2 + cy**2) ** 0.5
    # build coarse then blur for speed
    small = Image.new("L", (im.width // 8, im.height // 8), 0)
    sp = small.load()
    for y in range(small.height):
        for x in range(small.width):
            X, Y = x * 8, y * 8
            d = ((X - cx) ** 2 + (Y - cy) ** 2) ** 0.5 / maxd
            sp[x, y] = int(min(1, d) ** 2 * 255 * strength)
    mask = small.resize((im.width, im.height), Image.BILINEAR).filter(
        ImageFilter.GaussianBlur(60)
    )
    black = Image.new("RGB", im.size, (0, 0, 0))
    return Image.composite(black, im, mask)

def linear_scrim(im, side="left", base=0.80, span=0.62):
    """Dark gradient overlay fading across the frame for text legibility."""
    grad = Image.new("L", (im.width, 1))
    gp = grad.load()
    for x in range(im.width):
        t = x / im.width
        if side == "left":
            a = base * max(0.0, 1 - t / span)
        elif side == "right":
            a = base * max(0.0, (t - (1 - span)) / span)
        else:  # bottom handled separately
            a = 0
        gp[x, 0] = int(a * 255)
    grad = grad.resize(im.size)
    black = Image.new("RGB", im.size, (0, 0, 0))
    return Image.composite(black, im, grad)

def bottom_scrim(im, base=0.85, span=0.55):
    grad = Image.new("L", (1, im.height))
    gp = grad.load()
    for y in range(im.height):
        t = y / im.height
        a = base * max(0.0, (t - (1 - span)) / span)
        gp[0, y] = int(a * 255)
    grad = grad.resize(im.size)
    black = Image.new("RGB", im.size, (0, 0, 0))
    return Image.composite(black, im, grad)

def topbottom_scrim(im, top_a=0.5, bot_a=0.85):
    grad = Image.new("L", (1, im.height))
    gp = grad.load()
    for y in range(im.height):
        t = y / im.height
        a = top_a * max(0.0, 1 - t / 0.35) + bot_a * max(0.0, (t - 0.5) / 0.5)
        gp[0, y] = int(min(1, a) * 255)
    grad = grad.resize(im.size)
    black = Image.new("RGB", im.size, (0, 0, 0))
    return Image.composite(black, im, grad)

# scrim plan per slide
PLAN = {
    "s01_earth":     ("center", 0.30),  # title - centered, gentle global darken
    "s02_network":   ("left", 0.0),
    "s03_port":      ("left", 0.0),
    "s04_tech":      ("left", 0.0),
    "s05_iphone":    ("both", 0.0),
    "s06_market":    ("left", 0.0),
    "s07_science":   ("right", 0.0),
    "s08_local":     ("left", 0.0),
    "s09_pollution": ("left", 0.0),
    "s10_sunrise":   ("center", 0.0),  # conclusion - centered
}

for name, (side, extra) in PLAN.items():
    im = Image.open(os.path.join(SRC, name + ".jpg")).convert("RGB")
    im = cover(im, W, H)
    # cinematic grade: slightly cooler, lower brightness, gentle contrast
    im = ImageEnhance.Color(im).enhance(0.92)
    im = ImageEnhance.Brightness(im).enhance(0.86)
    im = ImageEnhance.Contrast(im).enhance(1.06)
    im = vignette(im, 0.5)
    if side == "both":
        # strong left (text column) + softer right (stat), phone stays bright
        im = linear_scrim(im, side="left", base=0.84, span=0.52)
        im = linear_scrim(im, side="right", base=0.70, span=0.40)
        im = bottom_scrim(im, base=0.40, span=0.35)
    elif side in ("left", "right"):
        im = linear_scrim(im, side=side, base=0.82, span=0.66)
        im = bottom_scrim(im, base=0.45, span=0.4)
    elif side == "center":
        # title / conclusion: even darken top+bottom for centered text
        im = topbottom_scrim(im, top_a=0.45, bot_a=0.75)
        # overall slight darken for global feel
        if extra:
            black = Image.new("RGB", im.size, (0, 0, 0))
            im = Image.blend(im, black, extra)
    im.save(os.path.join(OUT, name + ".jpg"), quality=88)
    print("processed", name)
print("done")
