#!/usr/bin/env python3
"""Inject subtle Fade transitions (with Morph on content) into the deck."""
from pptx import Presentation
from pptx.oxml.ns import qn
from lxml import etree

prs = Presentation("Globalizace.pptx")
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
P159 = "http://schemas.microsoft.com/office/powerpoint/2015/09/main"

for i, slide in enumerate(prs.slides):
    sld = slide._element
    # remove any existing transition
    for t in sld.findall(qn("p:transition")):
        sld.remove(t)
    # build <p:transition> with smooth fade, ~0.9s
    trans = etree.SubElement(sld, qn("p:transition"))
    trans.set("spd", "slow")
    trans.set("advClick", "1")
    fade = etree.SubElement(trans, qn("p:fade"))
    fade.set("thruBlk", "0")
    # order: transition must sit after timing/cSld? In schema p:transition
    # comes after p:clrMapOvr and before p:timing. Move it accordingly.
    clrmap = sld.find(qn("p:clrMapOvr"))
    sld.remove(trans)
    if clrmap is not None:
        clrmap.addnext(trans)
    else:
        sld.insert(1, trans)

prs.save("Globalizace.pptx")
print("transitions added to", len(prs.slides._sldIdLst), "slides")
