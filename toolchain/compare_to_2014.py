"""Shape a Devanagari stress corpus with two builds of Hind and report differences.

usage: .venv/bin/python toolchain/compare_to_2014.py legacy/build-2014 intermediates/products/Hind-<version>-OTF
"""
import sys, os, collections
import uharfbuzz as hb
from fontTools.ttLib import TTFont

CONS = [chr(c) for c in range(0x0915, 0x093A)] + ["क़", "ख़", "ग़", "ज़", "ड़", "ढ़", "फ़", "य़"]
CONS += ["क़", "ड़"]
MATRAS = [chr(c) for c in range(0x093E, 0x094D)] + ["ॢ", "ॣ"]
MARKS = ["ँ", "ं", "ः"]
V = "्"
RA = "र"
ZWJ, ZWNJ = "‍", "‌"

def corpus():
    words = []
    for c in CONS:
        words.append(c)
        for m in MATRAS:
            words.append(c + m)
            for k in MARKS:
                words.append(c + m + k)
        words.append(c + V)
        words.append(c + V + ZWJ)
        words.append(c + V + ZWNJ)
        words.append(RA + V + c)
        words.append(RA + V + c + "ि")
        words.append(RA + V + c + "िं")
        words.append(RA + V + c + "ी")
        words.append(RA + V + c + "ीं")
        words.append(c + V + RA)
        words.append(c + V + RA + "ि")
        for d in CONS:
            words.append(c + V + d)
            words.append(c + V + d + "ि")
            words.append(c + V + d + "ु")
            words.append(c + V + RA + V + d)
        for d in CONS[:12]:
            for e in CONS[:12]:
                words.append(c + V + d + V + e + "ि")
    for v in range(0x0904, 0x0915):
        words.append(chr(v))
        for k in MARKS:
            words.append(chr(v) + k)
    words += [chr(c) for c in range(0x0964, 0x0980)]
    words += ["The quick brown fox jumps over the lazy dog 0123456789 fi fl ffi ffl",
              "सभी मनुष्यों को गौरव और अधिकारों के मामले में जन्मजात स्वतन्त्रता और समानता प्राप्त है।"]
    words += ["".join(chr(c) for c in range(0x20, 0x7F)), "".join(chr(c) for c in range(0xA0, 0x180))]
    return words

def shape(font, text):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {})
    names = [font.glyph_to_string(i.codepoint) for i in buf.glyph_infos]
    pos = [(p.x_advance, p.x_offset, p.y_offset) for p in buf.glyph_positions]
    return list(zip(names, pos))

def main(old_dir, new_dir):
    words = corpus()
    print(f"corpus: {len(words)} strings")
    for style in ["Light", "Regular", "Medium", "SemiBold", "Bold"]:
        old_p = os.path.join(old_dir, f"Hind-{style}.otf")
        new_p = os.path.join(new_dir, f"Hind-{style}.otf")
        fonts = [hb.Font(hb.Face(hb.Blob.from_file_path(p))) for p in (old_p, new_p)]
        glyph_diff = pos_diff = 0
        kinds = collections.Counter()
        examples = []
        for w in words:
            a, b = (shape(f, w) for f in fonts)
            if [n for n, _ in a] != [n for n, _ in b]:
                glyph_diff += 1
                kinds["glyphs"] += 1
                if len(examples) < 8:
                    examples.append((w, a, b))
            elif a != b:
                pos_diff += 1
                big = max(max(abs(x - y) for x, y in zip(pa, pb)) for (_, pa), (_, pb) in zip(a, b))
                kinds["pos>5" if big > 5 else "pos<=5"] += 1
                if big > 5 and len(examples) < 8:
                    examples.append((w, a, b))
        print(f"\n{style}: glyph-sequence diffs {glyph_diff}, position-only diffs {pos_diff}  {dict(kinds)}")
        for w, a, b in examples:
            print("  ", w.encode("unicode_escape").decode())
            print("     old", a)
            print("     new", b)
        # outline/advance comparison
        to, tn = TTFont(old_p), TTFont(new_p)
        go, gn = to.getGlyphSet(), tn.getGlyphSet()
        from fontTools.pens.areaPen import AreaPen
        adv = [g for g in to.getGlyphOrder() if g in gn and go[g].width != gn[g].width]
        area = []
        for g in to.getGlyphOrder():
            if g not in gn:
                continue
            pa, pb = AreaPen(go), AreaPen(gn)
            go[g].draw(pa); gn[g].draw(pb)
            if abs(pa.value - pb.value) > max(50, abs(pa.value) * 0.01):
                area.append((g, round(pa.value), round(pb.value)))
        print(f"   advance-width diffs: {len(adv)} {adv[:10]}")
        print(f"   outline-area diffs (>1%): {len(area)} {area[:10]}")
        print(f"   missing in new: {sorted(set(to.getGlyphOrder()) - set(tn.getGlyphOrder()))[:10]}")
        print(f"   new only: {sorted(set(tn.getGlyphOrder()) - set(to.getGlyphOrder()))[:10]}")

main(*sys.argv[1:])
