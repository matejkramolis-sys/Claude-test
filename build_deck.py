# -*- coding: utf-8 -*-
"""Generate the Praha-Podbaba presentation (Apple-style, image-heavy)."""
import json
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from PIL import Image

# ---------- design system ----------
INK   = RGBColor(0x1D, 0x1D, 0x1F)   # near-black
GRAY  = RGBColor(0x6E, 0x6E, 0x73)   # secondary text
LIGHT = RGBColor(0xF5, 0xF5, 0xF7)   # apple light bg
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLUE  = RGBColor(0x00, 0x71, 0xE3)   # accent
TRAIN = RGBColor(0x58, 0x56, 0xD6)   # violet
TRAM  = RGBColor(0xE0, 0x33, 0x2E)   # red
BUS   = RGBColor(0x00, 0x84, 0x3D)   # green
HAIR  = RGBColor(0xD2, 0xD2, 0xD7)   # hairline

FONT = "Helvetica Neue"

meta = json.load(open("img/meta.json"))

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height
BLANK = prs.slide_layouts[6]

# ---------- helpers ----------
def slide():
    return prs.slides.add_slide(BLANK)

def bg(s, color):
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = color

def cover(s, key, x, y, w, h):
    """Add picture cropped to fill the box (cover)."""
    path = f"img/{key}.jpg"
    iw, ih = Image.open(path).size
    tgt = w / h
    src = iw / ih
    pic = s.shapes.add_picture(path, x, y, w, h)
    if src > tgt:
        c = (1 - tgt / src) / 2
        pic.crop_left = c; pic.crop_right = c
    else:
        c = (1 - src / tgt) / 2
        pic.crop_top = c; pic.crop_bottom = c
    return pic

def _set_alpha(fill_elem, alpha):
    srgb = fill_elem.find(qn('a:srgbClr'))
    a = srgb.makeelement(qn('a:alpha'), {'val': str(int(alpha * 1000))})
    srgb.append(a)

def rect(s, x, y, w, h, color, alpha=None, line=None, line_w=None, shape=MSO_SHAPE.RECTANGLE):
    sp = s.shapes.add_shape(shape, x, y, w, h)
    sp.fill.solid(); sp.fill.fore_color.rgb = color
    if alpha is not None:
        _set_alpha(sp.fill.fore_color._xFill, alpha)
    if line is not None:
        sp.line.color.rgb = line; sp.line.width = line_w or Pt(1)
    else:
        sp.line.fill.background()
    sp.shadow.inherit = False
    return sp

def gradient_scrim(s, x, y, w, h, top_alpha=0, bot_alpha=78, angle=90):
    """Black gradient rectangle, transparent(top) -> dark(bottom)."""
    sp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    sp.line.fill.background(); sp.shadow.inherit = False
    spPr = sp.fill._xPr
    # remove existing fill
    for tag in ('a:noFill','a:solidFill','a:gradFill','a:blipFill','a:pattFill','a:grpFill'):
        e = spPr.find(qn(tag))
        if e is not None: spPr.remove(e)
    grad = spPr.makeelement(qn('a:gradFill'), {})
    gsLst = grad.makeelement(qn('a:gsLst'), {})
    def gs(pos, alpha):
        g = grad.makeelement(qn('a:gs'), {'pos': str(int(pos*1000))})
        c = grad.makeelement(qn('a:srgbClr'), {'val': '000000'})
        a = grad.makeelement(qn('a:alpha'), {'val': str(int(alpha*1000))})
        c.append(a); g.append(c); return g
    gsLst.append(gs(0, top_alpha))
    gsLst.append(gs(100, bot_alpha))
    grad.append(gsLst)
    lin = grad.makeelement(qn('a:lin'), {'ang': str(angle*60000), 'scaled':'1'})
    grad.append(lin)
    # insert grad before line element
    ln = spPr.find(qn('a:ln'))
    if ln is not None: spPr.insert(list(spPr).index(ln), grad)
    else: spPr.append(grad)
    return sp

def text(s, x, y, w, h, runs, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         space_after=None, line_spacing=None, wrap=True):
    """runs: list of paragraphs; each paragraph is list of (txt, size, color, bold, [tracking])."""
    tb = s.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = 0; tf.margin_right = 0
    tf.margin_top = 0; tf.margin_bottom = 0
    for i, para in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if space_after is not None: p.space_after = Pt(space_after)
        p.space_before = Pt(0)
        if line_spacing is not None: p.line_spacing = line_spacing
        for run in para:
            txt, size, color, bold = run[0], run[1], run[2], run[3]
            r = p.add_run(); r.text = txt
            r.font.name = FONT; r.font.size = Pt(size)
            r.font.color.rgb = color; r.font.bold = bold
            if len(run) > 4 and run[4] is not None:
                rPr = r._r.get_or_add_rPr(); rPr.set('spc', str(int(run[4]*100)))
    return tb

def credit(s, key, dark=True):
    m = meta[key]
    art = m['artist'].split('(')[0].strip()
    txt = f"Foto: {art} · {m['license']} · Wikimedia Commons"
    col = RGBColor(0xC9,0xC9,0xCE) if dark else GRAY
    tb = text(s, Inches(0.0), SH-Inches(0.34), SW, Inches(0.3),
              [[(txt, 7, col, False)]], align=PP_ALIGN.RIGHT)
    tb.left = Inches(0); tb.width = SW - Inches(0.25)
    return tb

def line_seg(s, x1, y1, x2, y2, color, w=Pt(2)):
    ln = s.shapes.add_connector(2, x1, y1, x2, y2)
    ln.line.color.rgb = color; ln.line.width = w
    ln.shadow.inherit = False
    return ln

def badge(s, x, y, d, label, color):
    c = rect(s, x, y, d, d, color, shape=MSO_SHAPE.OVAL)
    tf = c.text_frame; tf.word_wrap = False
    tf.margin_left=0; tf.margin_right=0; tf.margin_top=0; tf.margin_bottom=0
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = label
    r.font.name = FONT; r.font.size = Pt(15); r.font.bold = True
    r.font.color.rgb = WHITE
    return c

def eyebrow(s, x, y, txt, color=BLUE):
    return text(s, x, y, Inches(8), Inches(0.4),
                [[(txt.upper(), 12.5, color, True, 2.2)]])

# ============================================================
# SLIDE 1 — TITLE
# ============================================================
s = slide()
cover(s, "title_hero", 0, 0, SW, SH)
gradient_scrim(s, 0, Inches(3.2), SW, SH-Inches(3.2), 0, 82)
text(s, Inches(0.85), Inches(4.55), Inches(11), Inches(0.5),
     [[("PRAHA-PODBABA", 14, RGBColor(0xE7,0xE7,0xEC), True, 3.0)]])
text(s, Inches(0.8), Inches(4.95), Inches(11.7), Inches(1.6),
     [[("Nádraží Podbaba", 60, WHITE, False)]])
text(s, Inches(0.85), Inches(6.15), Inches(11), Inches(0.7),
     [[("Zajímavosti a dopravní význam stanice", 22, RGBColor(0xE7,0xE7,0xEC), False)]])
credit(s, "title_hero")

# ============================================================
# SLIDE 2 — ZÁKLADNÍ INFORMACE
# ============================================================
s = slide(); bg(s, WHITE)
PANEL = Inches(5.55)
cover(s, "station_view", PANEL, 0, SW-PANEL, SH)
eyebrow(s, Inches(0.85), Inches(0.85), "Základní informace")
text(s, Inches(0.83), Inches(1.25), Inches(4.4), Inches(1.0),
     [[("O stanici", 38, INK, False)]])
facts = [
    ("Praha 6 – Bubeneč", "poloha v severozápadní části Prahy"),
    ("Otevřena v roce 2014", "29. srpna 2014"),
    ("Náhrada za Prahu-Bubeneč", "nahradila starší stanici poblíž"),
    ("Síť Esko / PID", "součást příměstské železnice"),
]
yy = Inches(2.5)
for title, sub in facts:
    rect(s, Inches(0.85), yy+Inches(0.06), Inches(0.09), Inches(0.62), BLUE)
    text(s, Inches(1.15), yy, Inches(4.2), Inches(0.8),
         [[(title, 17, INK, True)], [(sub, 12.5, GRAY, False)]],
         space_after=2, line_spacing=1.0)
    yy += Inches(0.92)
# mini locator map drawn with shapes
mx, my, mw, mh = Inches(0.85), Inches(6.25), Inches(4.3), Inches(0.85)
rect(s, mx, my, mw, mh, LIGHT, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
line_seg(s, mx+Inches(0.2), my+Inches(0.62), mx+Inches(2.0), my+Inches(0.15), RGBColor(0x9F,0xC5,0xE8), Pt(5))  # Vltava
text(s, mx+Inches(0.15), my+Inches(0.07), Inches(2), Inches(0.3),
     [[("Vltava", 8, GRAY, False)]])
badge(s, mx+Inches(1.55), my+Inches(0.28), Inches(0.3), "", TRAM)
text(s, mx+Inches(1.95), my+Inches(0.27), Inches(2.3), Inches(0.4),
     [[("Praha-Podbaba", 11, INK, True)],[("Praha 6", 8.5, GRAY, False)]], space_after=0, line_spacing=0.95)
credit(s, "station_view")

# ============================================================
# SLIDE 3 — PROČ JE PODBABA DŮLEŽITÁ?
# ============================================================
s = slide(); bg(s, WHITE)
eyebrow(s, Inches(0.85), Inches(0.7), "Dopravní význam")
text(s, Inches(0.83), Inches(1.1), Inches(11.5), Inches(1.0),
     [[("Proč je Podbaba důležitá?", 38, INK, False)]])
cards = [
    ("train_to_prague", "Přestupní uzel", "Vlak, tramvaj a autobus na jednom místě", TRAIN),
    ("tram", "Brána Prahy 6", "Klíčový dopravní bod pro celou čtvrť", TRAM),
    ("rychlik", "Rychle do centra", "Přímé spojení do středu města", BUS),
]
cw = Inches(3.75); gap = Inches(0.34)
x0 = Inches(0.85); top = Inches(2.3); imgh = Inches(2.95)
for i,(key,title,sub,col) in enumerate(cards):
    x = x0 + i*(cw+gap)
    cover(s, key, x, top, cw, imgh)
    rect(s, x, top+imgh, Inches(0.5), Inches(0.09), col)
    text(s, x, top+imgh+Inches(0.22), cw, Inches(1.3),
         [[(title, 20, INK, True)], [(sub, 13, GRAY, False)]],
         space_after=4, line_spacing=1.05)
credit(s, "rychlik")

# ============================================================
# SLIDE 4 — ZAJÍMAVOSTI (timeline + historical photo)
# ============================================================
s = slide(); bg(s, WHITE)
IMG = Inches(4.95)
cover(s, "former_station", SW-IMG, 0, IMG, SH)
gradient_scrim(s, SW-IMG, Inches(4.6), IMG, SH-Inches(4.6), 0, 70)
text(s, SW-IMG+Inches(0.3), SH-Inches(1.15), IMG-Inches(0.5), Inches(0.9),
     [[("Původní zastávka Praha-Podbaba", 13, WHITE, True)],
      [("provoz pro cestující 1867–1949", 10.5, RGBColor(0xE7,0xE7,0xEC), False)]],
     space_after=2, line_spacing=1.0)
eyebrow(s, Inches(0.85), Inches(0.7), "Zajímavosti")
text(s, Inches(0.83), Inches(1.1), Inches(7.3), Inches(1.0),
     [[("Stanice s dlouhou historií", 34, INK, False)]])
# timeline
tl = [("1867", "první železniční\nzastávka v okolí"),
      ("2011", "otevřena nová\ntramvajová smyčka"),
      ("28. 8. 2014", "poslední vlak\nv Praze-Bubenči"),
      ("29. 8. 2014", "otevření moderní\nstanice Podbaba")]
ty = Inches(3.55); lx = Inches(1.0); rx = Inches(7.7)
line_seg(s, lx, ty, rx, ty, HAIR, Pt(2))
n = len(tl); span = rx-lx
for i,(yr,desc) in enumerate(tl):
    cx = lx + int(span*i/(n-1))
    col = BLUE if i==n-1 else INK
    badge(s, cx-Inches(0.11), ty-Inches(0.11), Inches(0.22), "", col)
    text(s, cx-Inches(0.9), ty-Inches(0.95), Inches(1.8), Inches(0.5),
         [[(yr, 15, col, True)]], align=PP_ALIGN.CENTER)
    for j,ln in enumerate(desc.split("\n")):
        text(s, cx-Inches(0.95), ty+Inches(0.28)+Inches(0.24)*j, Inches(1.9), Inches(0.4),
             [[(ln, 10.5, GRAY, False)]], align=PP_ALIGN.CENTER)
# extra fact
rect(s, Inches(0.85), Inches(5.55), Inches(0.09), Inches(0.95), BLUE)
text(s, Inches(1.15), Inches(5.5), Inches(6.7), Inches(1.2),
     [[("Postavena jako moderní přestupní terminál", 15, INK, True)],
      [("Stanice vznikla přímo u tramvajové smyčky, aby umožnila", 12.5, GRAY, False)],
      [("pohodlný přestup mezi vlakem a městskou dopravou.", 12.5, GRAY, False)]],
     space_after=2, line_spacing=1.05)
credit(s, "former_station")

# ============================================================
# SLIDE 5 — GALERIE
# ============================================================
s = slide(); bg(s, WHITE)
eyebrow(s, Inches(0.6), Inches(0.45), "Galerie")
text(s, Inches(0.58), Inches(0.8), Inches(11), Inches(0.8),
     [[("Jak stanice vypadá", 30, INK, False)]])
gx = Inches(0.6); gy = Inches(1.85); ggap = Inches(0.18)
gw = (SW - gx*2 - ggap*2) / 3
gh = (SH - gy - Inches(0.55) - ggap) / 2
gallery = [
    ("platform_prague", "Nástupiště"),
    ("tram_loop", "Tramvajová smyčka"),
    ("train_to_prague", "Příjezd vlaku"),
    ("underpass_art", "Podchod"),
    ("bus", "Autobusová zastávka"),
    ("platform_2014", "Nástupiště a okolí"),
]
for i,(key,cap) in enumerate(gallery):
    r,c = divmod(i,3)
    x = gx + c*(gw+ggap); y = gy + r*(gh+ggap)
    cover(s, key, x, y, gw, gh)
    gradient_scrim(s, x, y+gh-Inches(0.7), gw, Inches(0.7), 0, 68)
    text(s, x+Inches(0.18), y+gh-Inches(0.42), gw-Inches(0.3), Inches(0.35),
         [[(cap, 12, WHITE, True)]])

# ============================================================
# SLIDE 6 — SPOJENÍ (diagram)
# ============================================================
s = slide(); bg(s, WHITE)
eyebrow(s, Inches(0.85), Inches(0.6), "Spojení")
text(s, Inches(0.83), Inches(1.0), Inches(11), Inches(0.9),
     [[("Přestupní terminál tří druhů dopravy", 32, INK, False)]])
# central node
cnx, cny = Inches(0.95), Inches(3.45)
node = rect(s, cnx, cny, Inches(2.7), Inches(1.5), INK, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
tf = node.text_frame; tf.word_wrap=True
tf.vertical_anchor=MSO_ANCHOR.MIDDLE
p=tf.paragraphs[0]; p.alignment=PP_ALIGN.CENTER
r=p.add_run(); r.text="Praha-Podbaba"; r.font.name=FONT; r.font.size=Pt(19); r.font.bold=True; r.font.color.rgb=WHITE
p2=tf.add_paragraph(); p2.alignment=PP_ALIGN.CENTER
r=p2.add_run(); r.text="přestupní terminál"; r.font.name=FONT; r.font.size=Pt(11); r.font.color.rgb=RGBColor(0xC9,0xC9,0xCE)
rows = [
    (TRAIN, "VLAK", ["S4", "S41"], "Praha Masarykovo n. · Kralupy n. Vlt. · Roztoky u Prahy", "trať 091 Praha – Děčín"),
    (TRAM,  "TRAMVAJ", ["8", "18"], "směr Dejvická a centrum města", "smyčka Nádraží Podbaba"),
    (BUS,   "AUTOBUS", ["116","160","355"], "obsluha Prahy 6 a okolí · noční 902 · 909 · 954", "zastávka Nádraží Podbaba"),
]
bx = Inches(4.45); by0 = Inches(2.55); rh = Inches(1.45)
for i,(col,label,lines,dest,note) in enumerate(rows):
    by = by0 + i*rh
    # connector from node to row
    line_seg(s, cnx+Inches(2.7), cny+Inches(0.75), bx, by+Inches(0.55), HAIR, Pt(1.5))
    rect(s, bx, by, Inches(0.09), Inches(1.1), col)
    text(s, bx+Inches(0.3), by-Inches(0.02), Inches(2.2), Inches(0.4),
         [[(label, 13, col, True, 1.5)]])
    # line badges
    lxx = bx+Inches(0.3)
    for ln in lines:
        w = {1: Inches(0.46), 2: Inches(0.60)}.get(len(ln), Inches(0.74))
        b = rect(s, lxx, by+Inches(0.32), w, Inches(0.44), col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        tf=b.text_frame; tf.word_wrap=False
        tf.margin_left=0; tf.margin_right=0; tf.margin_top=0; tf.margin_bottom=0
        tf.vertical_anchor=MSO_ANCHOR.MIDDLE
        pp=tf.paragraphs[0]; pp.alignment=PP_ALIGN.CENTER
        rr=pp.add_run(); rr.text=ln; rr.font.name=FONT; rr.font.size=Pt(14); rr.font.bold=True; rr.font.color.rgb=WHITE
        lxx += w + Inches(0.16)
    text(s, lxx+Inches(0.1), by+Inches(0.3), Inches(5.4), Inches(0.9),
         [[(dest, 13.5, INK, True)],[(note, 11, GRAY, False)]],
         space_after=1, line_spacing=1.0, anchor=MSO_ANCHOR.MIDDLE)

# ============================================================
# SLIDE 7 — RYCHLE DO CENTRA
# ============================================================
s = slide(); bg(s, WHITE)
eyebrow(s, Inches(0.85), Inches(0.6), "Spojení s centrem")
text(s, Inches(0.83), Inches(1.0), Inches(11), Inches(0.9),
     [[("Rychle do centra Prahy", 34, INK, False)]])
# two route options as clean horizontal "tickets"
routes = [
    (TRAIN, "VLAKEM", "Praha-Podbaba", "Praha Masarykovo nádraží", "≈ 12 min", "přímé spojení do centra (linka S4)"),
    (TRAM, "TRAMVAJÍ", "Praha-Podbaba", "Dejvická  →  metro A", "≈ 8 min", "linky 8 a 18, dále metrem do centra"),
]
ry = Inches(2.45); rh2 = Inches(1.85); rw = Inches(11.6)
for i,(col,mode,a,b,tm,note) in enumerate(routes):
    y = ry + i*(rh2+Inches(0.3))
    rect(s, Inches(0.85), y, rw, rh2, LIGHT, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    rect(s, Inches(0.85), y, Inches(0.14), rh2, col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, Inches(1.25), y+Inches(0.28), Inches(3), Inches(0.4),
         [[(mode, 13, col, True, 1.5)]])
    # route line with two dots
    ax, bxx, ly = Inches(1.3), Inches(7.2), y+Inches(1.15)
    line_seg(s, ax+Inches(0.1), ly, bxx, ly, col, Pt(3))
    badge(s, ax, ly-Inches(0.1), Inches(0.2), "", col)
    badge(s, bxx-Inches(0.1), ly-Inches(0.1), Inches(0.2), "", col)
    text(s, ax-Inches(0.1), ly-Inches(0.62), Inches(3.2), Inches(0.4),
         [[(a, 14, INK, True)]])
    text(s, bxx-Inches(2.5), ly-Inches(0.62), Inches(3.2), Inches(0.4),
         [[(b, 14, INK, True)]], align=PP_ALIGN.RIGHT)
    text(s, ax-Inches(0.1), ly+Inches(0.12), Inches(6), Inches(0.4),
         [[(note, 11.5, GRAY, False)]])
    # time block
    text(s, Inches(9.0), y+Inches(0.45), Inches(3.2), Inches(1.0),
         [[(tm, 30, col, False)]], align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)

# ============================================================
# SLIDE 8 — SHRNUTÍ
# ============================================================
s = slide()
cover(s, "rychlik", 0, 0, SW, SH)
gradient_scrim(s, 0, 0, SW, SH, 30, 88, angle=45)
eyebrow(s, Inches(0.85), Inches(0.85), "Shrnutí", color=RGBColor(0x8F,0xC2,0xFF))
text(s, Inches(0.82), Inches(1.25), Inches(11), Inches(1.0),
     [[("Moderní brána Prahy 6", 44, WHITE, False)]])
points = [
    "Moderní železniční stanice otevřená v roce 2014",
    "Důležitý přestupní uzel vlak – tramvaj – autobus",
    "Rychlé a pohodlné spojení s centrem Prahy",
    "Příklad moderní pražské dopravní infrastruktury",
]
yy = Inches(3.0)
for pt in points:
    rect(s, Inches(0.9), yy+Inches(0.09), Inches(0.34), Inches(0.34), BLUE, shape=MSO_SHAPE.OVAL)
    text(s, Inches(0.9), yy+Inches(0.09), Inches(0.34), Inches(0.34),
         [[("✓", 13, WHITE, True)]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, Inches(1.45), yy, Inches(10.5), Inches(0.6),
         [[(pt, 19, WHITE, False)]], anchor=MSO_ANCHOR.MIDDLE)
    yy += Inches(0.82)
credit(s, "rychlik")

# ---------- speaker notes ----------
NOTES = [
"""Dobrý den, dnes vám představím železniční stanici Nádraží Podbaba, celým názvem Praha-Podbaba. Je to sice menší zastávka, ale dnes uvidíme, že má pro dopravu v Praze docela velký význam. Leží na severozápadě města a je hezkým příkladem toho, jak moderní železnice spolupracuje s tramvajemi a autobusy. V následujících minutách si projdeme základní informace, historii i to, jak se odsud dá rychle dostat do centra Prahy.""",
"""Tady vidíme základní informace o stanici. Praha-Podbaba se nachází v Praze 6, v katastru Bubenče, nedaleko řeky Vltavy. Otevřena byla 29. srpna 2014 a nahradila starší stanici Praha-Bubeneč, která už cestujícím dobře nesloužila. Stanice je součástí pražské příměstské železnice, takzvaného systému Esko, který je zapojený do integrované dopravy PID. Díky tomu na jeden jízdní doklad přestoupíte mezi vlakem, tramvají i autobusem.""",
"""Proč je vlastně Podbaba důležitá? Hlavní výhodou je, že na jednom místě potkáte tři druhy dopravy – vlak, tramvaj i autobus. Pro obyvatele Prahy 6 je to praktická brána do města i ven z něj. Místo aby lidé jezdili autem, mohou rychle přestoupit z tramvaje na vlak a během pár minut být blíž centru. Právě tahle provázanost dělá z malé zastávky důležitý dopravní bod.""",
"""Možná vás překvapí, že železnice tudy vede už velmi dlouho. První zastávka v okolí Podbaby fungovala už od roku 1867, tedy v 19. století. V roce 2011 sem byla prodloužena tramvajová trať a vznikla nová smyčka. A v srpnu 2014 se to celé propojilo – 28. srpna projel poslední vlak stanicí Praha-Bubeneč a hned další den, 29. srpna, byla otevřena moderní stanice Podbaba. Byla postavená záměrně u tramvají, jako přestupní terminál.""",
"""Tady se můžeme podívat, jak stanice a její okolí vlastně vypadají. Vidíme nástupiště, podchod, tramvajovou smyčku i autobusovou zastávku. Architektura je jednoduchá a účelná – prosklené přístřešky, bezbariérový přístup a podchod, který spojuje nástupiště s ulicí. Všimněte si, že všechno je blízko u sebe, takže přestup z vlaku na tramvaj zabere jen pár desítek metrů a chvilku času.""",
"""Teď k samotným spojením. Na nádraží Podbaba zastavují vlaky linek S4 a S41 na trati číslo 091 z Prahy do Děčína – jezdí směrem na Masarykovo nádraží i opačně na Roztoky a Kralupy nad Vltavou. Hned vedle končí tramvajové linky 8 a 18, které míří na Dejvickou a do centra. A doplňují je autobusy, například linky 116, 160 a 355, v noci pak linky 902, 909 a 954. Všechno na jednom místě.""",
"""Jednou z největších výhod Podbaby je rychlost spojení s centrem. Vlakem se z Podbaby dostanete na Masarykovo nádraží přibližně za dvanáct minut – bez popojíždění v koloně a bez čekání na semaforech. Druhá možnost je tramvají číslo 8 nebo 18 na Dejvickou, odkud pokračuje metro linky A přímo do centra. Cestující si tak mohou vybrat, co se jim zrovna hodí. Právě proto je Podbaba oblíbená u lidí dojíždějících do práce a do školy.""",
"""Na závěr to shrňme. Praha-Podbaba je moderní železniční stanice otevřená v roce 2014, která se stala důležitým přestupním uzlem mezi vlakem, tramvají a autobusem. Nabízí rychlé a pohodlné spojení s centrem Prahy a je hezkým příkladem toho, jak má vypadat moderní městská železnice. Děkuji za pozornost a rád zodpovím vaše dotazy.""",
]
for i, sl in enumerate(prs.slides):
    sl.notes_slide.notes_text_frame.text = NOTES[i]

prs.save("Nadrazi-Podbaba.pptx")
print("saved Nadrazi-Podbaba.pptx with", len(prs.slides.__iter__.__self__._sldIdLst), "slides")
