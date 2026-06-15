#!/usr/bin/env python3
"""Faithful PIL preview of the deck layout (Liberation Sans ~ Arial) to verify
composition & catch overflow. Mirrors build_pptx coordinates."""
from PIL import Image, ImageDraw, ImageFont
import os

PXI = 96  # px per inch
W, H = int(13.333 * PXI), int(7.5 * PXI)
FD = "/usr/share/fonts/truetype/liberation/"
def F(weight, size):
    fn = {"reg": "LiberationSans-Regular.ttf", "bold": "LiberationSans-Bold.ttf",
          "italic": "LiberationSans-Italic.ttf"}[weight]
    return ImageFont.truetype(FD + fn, int(size * PXI / 72))

WHITE=(255,255,255); MIST=(214,218,224); DIM=(161,168,179)
ACCENT=(46,155,255); GREEN=(50,215,75); AMBER=(255,159,10); RED=(255,69,58)

def IN(v): return int(v * PXI)

def track(draw, xy, text, font, fill, spc_pt):
    x, y = xy
    sp = spc_pt * PXI / 7200.0 * 72  # rough
    sp = spc_pt / 100.0 * PXI / 72.0
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + sp
    return x

def center(draw, cx, y, text, font, fill, spc=0):
    # measure with tracking
    sp = spc/100.0*PXI/72.0
    w = sum(draw.textlength(c, font=font)+sp for c in text)-sp if spc else draw.textlength(text,font=font)
    track(draw, (cx - w/2, y), text, font, fill, spc) if spc else draw.text((cx-w/2,y),text,font=font,fill=fill)

def kicker(d, text, color=ACCENT, x=0.95, y=0.85):
    track(d, (IN(x), IN(y)), text.upper(), F("bold",14.5), color, 340)

def title(d, text, x=0.92, y=1.4, size=50, color=WHITE):
    f=F("bold",size); ty=IN(y)
    for line in text.split("\n"):
        d.text((IN(x),ty), line, font=f, fill=color); ty+=int(size*PXI/72*1.02)

def rule(d,x,y,w=0.62,color=ACCENT):
    d.rectangle([IN(x),IN(y),IN(x+w),IN(y)+4], fill=color)

def points(d, items, x=0.95,y=3.5,gap=1.02,dot=ACCENT,hs=21,ss=14.5):
    for i,(head,sub) in enumerate(items):
        cy=y+gap*i
        d.ellipse([IN(x),IN(cy+0.10),IN(x)+12,IN(cy+0.10)+12], fill=dot)
        d.text((IN(x+0.4),IN(cy)), head, font=F("bold",hs), fill=WHITE)
        if sub:
            d.text((IN(x+0.4),IN(cy)+int(hs*PXI/72*1.15)), sub, font=F("reg",ss), fill=MIST)

def bigstat(d,num,label,x=8.7,y=2.5,ns=110,color=WHITE):
    d.text((IN(x),IN(y)), num, font=F("bold",ns), fill=color)
    track(d,(IN(x),IN(y)+int(ns*PXI/72*1.05)), label.upper(), F("bold",14), DIM,260)

def load(name):
    return Image.open(f"assets/bg/{name}.jpg").resize((W,H), Image.LANCZOS).convert("RGB")

slides=[]
def new(name):
    im=load(name); slides.append(im); return im, ImageDraw.Draw(im)

# 1 title
im,d=new("s01_earth")
center(d, W/2, IN(2.35), "PREZENTACE · 2026", F("bold",15),(207,230,255),420)
center(d, W/2, IN(2.7), "Globalizace", F("bold",100), WHITE,-60)
d.rectangle([IN(6.27),IN(4.78),IN(7.07),IN(4.78)+4],fill=ACCENT)
center(d, W/2, IN(4.95), "Tom Častvaj  ·  3.B", F("reg",22), MIST,60)
center(d, W/2, IN(5.6), "Jak se svět propojil v jednu síť", F("italic",15.5), DIM)
# 2
im,d=new("s02_network"); kicker(d,"01 — Definice"); title(d,"Co je globalizace?"); rule(d,0.95,2.62)
points(d,[("Propojování světa v jeden celek","Ekonomiky, kultury a lidé se stále těsněji prolínají."),
("Vzdálenosti přestaly platit","Zboží i informace obletí planetu za hodiny, ne za měsíce."),
("Týká se úplně každého","Od telefonu v kapse až po jídlo na talíři.")],y=3.15,gap=1.12)
# 3
im,d=new("s03_port"); kicker(d,"02 — Mechanismy"); title(d,"Jak to celé funguje"); rule(d,0.95,2.62)
points(d,[("Mezinárodní obchod","Lodě a kontejnery propojují trhy všech kontinentů."),
("Internet","Data a služby putují mezi zeměmi okamžitě."),
("Doprava","Letecká i námořní logistika zkrátila vzdálenosti."),
("Globální komunikace","Spolupracujeme v reálném čase přes časová pásma.")],y=3.05,gap=0.95,hs=19.5)
# 4
im,d=new("s04_tech"); kicker(d,"03 — Příčiny"); title(d,"Co globalizaci pohání"); rule(d,0.95,2.62)
points(d,[("Technologický pokrok","Počítače a chytré telefony spojily celé generace."),
("Rychlejší doprava","Levnější a dostupnější přesun lidí i zboží."),
("Rozmach internetu","Z lokální informace se během chvíle stane globální."),
("Mezinárodní byznys","Firmy hledají trhy a partnery po celém světě.")],y=3.05,gap=0.95,hs=19.5)
# 5
im,d=new("s05_iphone"); kicker(d,"04 — V praxi"); title(d,"Globalizace v jednom\ntelefonu",size=44); rule(d,0.95,3.05)
points(d,[("iPhone je dílem desítek zemí","Design v USA, čipy z Asie, montáž v Číně."),
("Globální značky všude kolem","Stejné logo potkáte v Tokiu i v Brně."),
("Mezinárodní dodavatelské řetězce","Jeden výrobek, stovky propojených dodavatelů.")],
y=3.45,gap=0.95,hs=18.5,ss=13.5)
bigstat(d,"40+","zemí v jednom iPhonu",x=8.85,y=2.7,ns=120)
# 6
im,d=new("s06_market"); kicker(d,"05 — Výhody",GREEN); title(d,"Co nám přináší"); rule(d,0.95,2.62,color=GREEN)
points(d,[("Větší výběr zboží","Produkty z celého světa na dosah ruky."),
("Přístup k informacím","Vědění planety dostupné komukoli online."),
("Ekonomický růst","Obchod vytváří pracovní místa a bohatství."),
("Mezinárodní spolupráce","Společné řešení problémů přesahujících hranice.")],y=3.05,gap=0.95,hs=19.5,dot=GREEN)
# 7
im,d=new("s07_science"); kicker(d,"06 — Výhody II",GREEN,x=6.6); title(d,"Motor pokroku",x=6.55); rule(d,6.6,2.62,color=GREEN)
points(d,[("Inovace","Konkurence i spolupráce ženou nové nápady vpřed."),
("Vědecký pokrok","Objevy se okamžitě sdílejí napříč kontinenty."),
("Vzdělání a znalosti","Kurzy a data otevřené komukoli, kdekoli.")],x=6.6,y=3.2,gap=1.05,hs=20,dot=GREEN)
# 8
im,d=new("s08_local"); kicker(d,"07 — Nevýhody",AMBER); title(d,"Druhá strana mince"); rule(d,0.95,2.62,color=AMBER)
points(d,[("Tlak na místní firmy","Malé obchody těžko soupeří s globálními giganty."),
("Závislost na trzích","Krize v cizině zasáhne ekonomiku i u nás doma."),
("Přesun pracovních míst","Výroba se stěhuje tam, kde je levnější.")],y=3.15,gap=1.12,hs=21,dot=AMBER)
# 9
im,d=new("s09_pollution"); kicker(d,"08 — Nevýhody II",RED); title(d,"Skrytá cena propojení"); rule(d,0.95,2.62,color=RED)
points(d,[("Dopady na životní prostředí","Doprava zboží přes půl světa zvyšuje emise."),
("Stírání kulturních rozdílů","Lokální tradice ustupují globálnímu mainstreamu."),
("Ekonomická nerovnost","Zisky se nerozdělují mezi všechny rovnoměrně.")],y=3.15,gap=1.12,hs=21,dot=RED)
# 10
im,d=new("s10_sunrise")
center(d,W/2,IN(1.5),"09 — ZÁVĚR",F("bold",14.5),(255,224,192),360)
center(d,W/2,IN(2.05),"Svět bez hranic?",F("bold",58),WHITE,-40)
center(d,W/2,IN(3.45),"Globalizace nás spojuje, obohacuje a zrychluje pokrok —",F("reg",18.5),MIST)
center(d,W/2,IN(3.78),"zároveň přináší závislost, nerovnost a tlak na přírodu.",F("reg",18.5),MIST)
d.rounded_rectangle([IN(3.67),IN(4.78),IN(9.67),IN(5.4)],radius=18,fill=ACCENT)
center(d,W/2,IN(4.9),"Nejde ji zastavit — jde ji dělat chytře.",F("bold",16),WHITE)
center(d,W/2,IN(5.85),"Otázka pro vás:  Je globalizace spíš příležitost, nebo hrozba — a pro koho?",F("italic",16.5),WHITE)

os.makedirs("preview",exist_ok=True)
for i,im in enumerate(slides,1): im.save(f"preview/s{i:02d}.png")
# contact sheet
cols,rows=2,5; tw=W//2; th=H//2
sheet=Image.new("RGB",(tw*cols+30, th*rows+60),(18,18,20))
dd=ImageDraw.Draw(sheet)
for i,im in enumerate(slides):
    r,c=divmod(i,cols)
    sheet.paste(im.resize((tw,th),Image.LANCZOS),(c*(tw+10)+10,r*(th+12)+10))
sheet.save("preview/contact.png")
print("rendered",len(slides),"slides")
