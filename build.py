#! /usr/bin/env python3
# Hind, built with hindkit (toolchain/hindkit) and current AFDKO from masters/Hind.glyphs.
# Modeled on ITF's Poppins build-GoogleFonts.py. The 2014 Python 2 build is in legacy/.

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "toolchain", "hindkit", "lib"))

import glyphsLib
from glyphsLib.classes import WEIGHT_CODES
from fontTools.designspaceLib import DesignSpaceDocument
import hindkit

SOURCE = "masters/Hind.glyphs"
EXPORT_DIR = "build/masters"

def export_masters():
    """Hind.glyphs -> UFO masters for hindkit. Anchors are not propagated: the 2014 fonts had none on composites."""
    hindkit.remove(EXPORT_DIR)
    hindkit.makedirs(os.path.dirname(EXPORT_DIR))
    exported = glyphsLib.build_masters(
        SOURCE, EXPORT_DIR,
        designspace_path = os.path.join(EXPORT_DIR, "Hind.designspace"),
        propagate_anchors = False,
        generate_GDEF = False,
    )
    return DesignSpaceDocument.fromfile(exported.designspace_path)

def main():

    source = glyphsLib.GSFont(SOURCE)
    designspace = export_masters()

    family = hindkit.Family(
        trademark = source.familyName,
        script_name = "Devanagari",
        append_script_name = False,
        client_name = "Google Fonts",
        initial_release_year = 2014,
    )
    family.set_masters([(m.name, m.axes[0]) for m in source.masters])
    family.set_styles([(i.name, i.axes[0], WEIGHT_CODES[i.weight]) for i in source.instances if i.exports])

    for master, ds_source in zip(family.masters, designspace.sources):
        master._filename = os.path.splitext(os.path.basename(ds_source.path))[0]

    i = family.info
    i.openTypeNameDesigner = source.designer
    p = source.customParameters
    i.openTypeHheaAscender, i.openTypeHheaDescender, i.openTypeHheaLineGap = p["hheaAscender"], p["hheaDescender"], p["hheaLineGap"]
    i.openTypeOS2TypoAscender, i.openTypeOS2TypoDescender, i.openTypeOS2TypoLineGap = p["typoAscender"], p["typoDescender"], p["typoLineGap"]
    i.openTypeOS2WinAscent, i.openTypeOS2WinDescent = p["winAscent"], p["winDescent"]

    project = hindkit.Project(
        family,
        fontrevision = "2.002",
        options = {
            "prepare_mark_positioning": True,
            "match_mI_variants": 1,
                "position_marks_for_mI_variants": True,
            "round_like_python2": True,
            "correct_contour_direction": True,
            "do_style_linking": True,
            "additional_unicode_range_bits": [0, 1, 2],
            "use_os_2_version_4": True,
                "prefer_typo_metrics": True,
                "is_width_weight_slope_only": True,
        },
    )
    project.build()

# --- Overriding ---

hindkit.Project.directories["masters"] = EXPORT_DIR
hindkit.Project.directories["output"] = ""

hindkit.FeatureMatches.mI_VARIANT_NAME_PATTERN = r"mI\.a\d\d"

def read_glyph_class(path, class_name):
    with open(path) as f:
        content = f.read()
    body = content.partition("@{} = [".format(class_name))[2].partition("];")[0]
    return [i.partition("#")[0].strip() for i in body.splitlines() if i.partition("#")[0].strip()]

# The 2014 build matched mI variants against this hand-made list, not hindkit's name filter.
hindkit.FeatureMatches.BASE_NAMES_ALIVE = read_glyph_class("features/classes_suffixing.fea", "mI_BASES")

def match_mI_variants_2014(self, base):
    """legacy/itf.py match_mI: the nearest variant wins, ties go to the shorter one."""
    matches = self.matches
    tolerance = (self.font["dvVA"].width - self.abvm_right_margin) / 2
    if base.target < matches[0].overhanging:
        return matches[0]
    if base.target >= matches[-1].overhanging:
        if base.target < matches[-1].overhanging + tolerance:
            return matches[-1]
        return None
    for index, match in enumerate(matches):
        if base.target < match.overhanging:
            if match.overhanging - base.target < abs(matches[index - 1].overhanging - base.target):
                return match
            return matches[index - 1]

hindkit.FeatureMatches.match_mI_variants = match_mI_variants_2014

# --- Executing ---

main()
