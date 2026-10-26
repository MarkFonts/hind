# Toolchain

Everything the 2014 Hind build touched, plus ITF's later build system. Hind now builds with `hindkit/` and current AFDKO (see `../build.py` and the top-level README); the rest is kept for reference.

## Local patches to hindkit

`hindkit/` is a subtree of itfoundry/hindkit with these changes, needed for AFDKO 5 and to match the 2014 fonts:

- `objects/family.py`: the designspace is written with `fontTools.designspaceLib`, with real axes. AFDKO 5's `makeinstancesufo` rejects MutatorMath's axis-less format.
- `objects/font.py`: `updateInstance(path, options)`; AFDKO 5 swapped the arguments.
- `objects/family.py`, `objects/project.py`: two new options, both off by default.
  - `round_like_python2`: interpolate unrounded, then round half away from zero, as the Python 2 FDK did. Widths are re-interpolated from the masters, because `makeinstancesufo` rounds them half to even even with `-r`.
  - `correct_contour_direction`: run defcon's `correctContourDirection` on each instance. The 2014 `checkoutlines` did this; `checkoutlinesufo` does not.

`migrate_ufo_to_glyphs.py` converted the 2014 UFO masters to `masters/Hind.glyphs` (one-time).

## What the original build needs

`../build.py` (Python 2) runs four steps:

| Step | Calls | Where it lives now |
|---|---|---|
| `-g` OpenType classes | `itf.py` + `robofab` | `../itf.py`; robofab is archived ([robotools/robofab](https://github.com/robotools/robofab)), not vendored, replace with fontParts/defcon |
| `-i` instances | `UFOInstanceGenerator.py`, `WriteFeaturesMarkFDK`, `checkoutlines` | `adobe-vintage/`; `checkoutlines` is now AFDKO's `checkoutlinesufo` |
| `-m` matra-i matching | `itf.py` + `robofab` | `../itf.py` |
| `-c` compile | AFDKO `makeotf` | `pip install afdko` |

## Folders

- `hindkit/`: [itfoundry/hindkit](https://github.com/itfoundry/hindkit) at master (2019-09-02, `553654362f`), added as a squashed `git subtree`. This is ITF's Python 3 + AFDKO successor to Hind's `build.py`/`itf.py`, written for the Hind multiscript families. Update with
  `git subtree pull --prefix=toolchain/hindkit https://github.com/itfoundry/hindkit.git master --squash`
- `adobe-vintage/`: Adobe's retired scripts that the 2014 build imports, MIT licensed (license files alongside).
  - From [adobe-type-tools/python-modules](https://github.com/adobe-type-tools/python-modules) `vintage/` @ `9121792ede`: `WriteFeaturesMarkFDK.py`, `WriteFeaturesKernFDK.py`, `AdobeFontLabUtils.py`, `BezChar.py`. Their modern replacements are `markFeatureWriter.py` / `kernFeatureWriter.py` in the same repo.
  - From [adobe-type-tools/python-scripts](https://github.com/adobe-type-tools/python-scripts) `vintage/` @ `a7d66362db`: `UFOInstanceGenerator.py`, `makeinstances.py`, `BuildMMFont.py`, `copyCFFCharstrings.py`, `kernCheck.py`. The modern replacement for instancing is AFDKO's `makeinstancesufo` (designspace based).
- `itf-reference-builds/`: hindkit-era `build.py` files from ITF's later families, to model a new Hind build on.
  - `hind-siliguri/build.py` @ `affb7dbd00` (Bangla, hindkit 0.3)
  - `Poppins/build-GoogleFonts.py`, `build-Latin.py` @ `be5b80d711` (Devanagari + Latin, the closest sibling to Hind)

Teko and Rajdhani ship byte-identical copies of Hind's `build.py`, `itf.py`, and `reference.py`, so there's no newer version of the old scripts to bring over.
