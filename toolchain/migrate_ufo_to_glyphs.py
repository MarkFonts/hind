#! /usr/bin/env python3
"""One-time migration: the 2014 UFO masters -> Hind.glyphs.

usage: python toolchain/migrate_ufo_to_glyphs.py MASTER_0.ufo MASTER_1.ufo OUTPUT.glyphs

Kept for the record; Hind.glyphs is the source from here on.
"""

import sys
import defcon
import glyphsLib
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor

STYLES = [
    ("Light",       0, 300),
    ("Regular",   210, 400),
    ("Medium",    440, 500),
    ("SemiBold",  700, 600),
    ("Bold",     1000, 700),
]

def main(light_path, bold_path, output_path):

    doc = DesignSpaceDocument()
    axis = AxisDescriptor()
    axis.name, axis.tag = "Weight", "wght"
    axis.minimum, axis.default, axis.maximum = 0, 0, 1000
    doc.addAxis(axis)

    for path, style_name, location in [(light_path, "Light", 0), (bold_path, "Bold", 1000)]:
        font = defcon.Font(path)
        font.info.styleName = style_name
        source = SourceDescriptor()
        source.font = font
        source.path = path
        source.familyName = "Hind"
        source.styleName = style_name
        source.location = {"Weight": location}
        doc.addSource(source)

    for style_name, location, weight_class in STYLES:
        instance = InstanceDescriptor()
        instance.familyName = "Hind"
        instance.styleName = style_name
        instance.location = {"Weight": location}
        instance.postScriptFontName = "Hind-" + style_name
        instance.lib["com.schriftgestaltung.weightClass"] = weight_class
        doc.addInstance(instance)

    gsfont = glyphsLib.to_glyphs(doc, minimize_ufo_diffs=True)
    gsfont.format_version = 3

    # glyphsLib adds a Width axis; Hind has one axis.
    gsfont.axes = gsfont.axes[:1]

    # The vertical metrics legacy/family_tables.fea set over the UFO values.
    metrics = {
        "hheaAscender": 1050, "hheaDescender": -350, "hheaLineGap": 100,
        "typoAscender": 1050, "typoDescender": -350, "typoLineGap": 100,
        "winAscent": 1100, "winDescent": 400,
    }
    # Fields the UFOs carried per style (copied from the Light master) or that the build sets.
    stale = list(metrics) + ["UFO Filename"] + """
        panose fsType unicodeRanges codePageRanges vendorID versionString
        postscriptFullName postscriptFontName postscriptWeightName postscriptUniqueID
        styleMapFamilyName styleMapStyleName weightClass widthClass
        macintoshFONDFamilyID macintoshFONDName
    """.split()
    for master, name, location in zip(gsfont.masters, ["Light", "Bold"], [0, 1000]):
        master.name = name
        master.axes = [location]
        for key in stale:
            del master.customParameters[key]
    for key in stale:
        del gsfont.customParameters[key]
    for key, value in metrics.items():
        gsfont.customParameters[key] = value

    for instance, (style_name, location, weight_class) in zip(gsfont.instances, STYLES):
        instance.axes = [location]
        instance.weight = style_name
        del instance.customParameters["weightClass"]
        del instance.customParameters["postscriptFontName"]

    gsfont.save(output_path)
    # glyphsLib writes floats to five places; keep the masters' exact BlueScale.
    with open(output_path) as f:
        text = f.read()
    with open(output_path, "w") as f:
        f.write(text.replace("value = 0.03963;", "value = 0.039625;"))
    print("[SAVED]", output_path)

main(*sys.argv[1:])
