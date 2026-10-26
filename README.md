# Hind

Hind is an open source typeface supporting the Devanagari and Latin scripts. Developed explicitly for use in User Interface design, the Hind font family includes five styles. Hind’s letterforms have a humanist-style construction, which is paired with seemingly monolinear strokes. Most of these strokes have flat endings: they either terminate with a horizontal or a vertical shear, rather than on a diagonal. This helps create clear-cut counter forms between the characters. In addition to this, Hind’s letterforms feature open apertures. The entire typeface family feels very legible when used to set text.

The Devanagari and Latin script components are scaled in relation to each other so that the Devanagari headline falls just below the Latin capital-height. In other words, the Devanagari base characters are 94% as tall as the Latin uppercase. Text set in the Devanagari script sits nicely alongside the Latin lowercase, too. Hind’s Devanagari vowel marks take forms that tends toward the traditional end of the design spectrum, while the knotted terminals, etc. inside of the base characters feature a treatment that appears more contemporary.

Each font in the Hind family has 1146 glyphs, which include hundreds of unique Devanagari conjuncts. These ensure full support for the major languages written with the Devanagari script. The Latin component’s character set is a basic western one, which enables typesetting in English and the other Western European languages. Hind is a solid choice for UI design, and a wise selection for electronic display embedding.

Manushi Parikh designed Hind for the Indian Type Foundry, who first published the fonts in 2014.

## Sources

`masters/Hind.glyphs` is the source: two masters (Light, Bold) on a Weight axis and five instances. It was converted from the 2014 UFO masters by `toolchain/migrate_ufo_to_glyphs.py`. Those UFOs, the FontLab `.vfb` files, and the rest of the 2014 Python 2 build are kept in `legacy/`.

OpenType features are written by hand in `features/` (`GSUB.fea`, `GSUB_prefixing.fea`, `classes_suffixing.fea`). Mark positioning, the mI variant matching, and the OS/2, hhea, and name tables are generated at build time by hindkit.

## Building

Requires Python 3.10 or newer.

```bash
python3 -m venv .venv
```

```bash
.venv/bin/pip install afdko glyphsLib defcon fontTools
```

```bash
.venv/bin/python build.py
```

The build exports UFO masters from `Hind.glyphs` into `build/masters`, interpolates the five instances with AFDKO's `makeinstancesufo`, and compiles OTFs with `makeotf`. Working files go to `intermediates/`, and the OTFs to `intermediates/products/Hind-<version>-OTF/`. `products/` gets a zip of the OTFs and TTX dumps, as ITF's Google Fonts builds did. `build.py --test` builds only the two master styles, skipping interpolation and overlap removal.

The build system is ITF's [hindkit](https://github.com/itfoundry/hindkit), vendored as a git subtree in `toolchain/hindkit` and patched for current AFDKO. See `toolchain/README.md`.

### Matching the 2014 fonts

This build is version 2.002. Google Fonts serves 2.001, a 2017 hotfix ([google/fonts#890](https://github.com/google/fonts/pull/890)) of the 2014 fonts: TTFs with ttfautohint and vertical metrics of 1055/−546/0 (hhea and typo) and 1055/546 (win). This build keeps the 2014 metrics (1050/−350/100, win 1100/400) for now.

The build reproduces the 2014 release. Across a 19,417-string Devanagari and Latin shaping test, Regular, Medium, SemiBold, and Bold shape identically to the 2014 OTFs, with the same glyph set and advance widths. Outlines match to within overlap-removal rounding, with one exception noted below. Getting there needed three things, all options in `build.py`:

- `round_like_python2`: instances are rounded half away from zero, as the 2014 Python 2 tools did, not half to even.
- `correct_contour_direction`: 33 Latin glyphs are drawn clockwise in the masters. The 2014 `checkoutlines` fixed this after removing overlaps; current `checkoutlinesufo` does not fix it at all. The build corrects direction after overlap removal too.
- The 2014 mI matching rule (nearest variant) and its hand-made base list replace hindkit's defaults.

Known differences: in Regular, न्ध्र (`dvN_DH_RA`) is drawn whole. The 2014 Regular has a gap in the headline and a spur on the ध, which is 10% of the glyph's area.

In Light, क़्फ़ (`dvKx_PHxA`) gets a different mI variant and a positioned ु. That glyph has anchors only in the Light master. The 2014 instancer dropped them; the current one keeps them in Light. Thirteen glyphs have anchors that differ between the masters.
