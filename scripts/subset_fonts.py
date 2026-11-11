#!/usr/bin/env python3
"""
One-time tool: trim the two open-license fonts down to the characters the cards
use and save them as WOFF files in fonts/, small enough to embed in every SVG.

Usage:  python scripts/subset_fonts.py <folder with the downloaded fonts>

The folder must contain ArchivoBlack-Regular.ttf, JetBrainsMono-wght.ttf
(the variable font, "JetBrainsMono[wght].ttf" from github.com/google/fonts)
and their OFL-ArchivoBlack.txt / OFL-JetBrainsMono.txt licence files.
Needs fontTools (pip install -r scripts/requirements.txt).
"""
import json
import os
import shutil
import sys

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "fonts")

# Printable ASCII plus the middle dot and the curly apostrophe.
UNICODES = list(range(0x20, 0x7F)) + [0x00B7, 0x2019]


def advances(font):
    """Advance width of every subset character, in em, for text measuring at render time."""
    upm = font["head"].unitsPerEm
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    return {chr(u): round(hmtx[cmap[u]][0] / upm, 4) for u in UNICODES if u in cmap}


def save_subset(font, out_path, features):
    opts = subset.Options()
    opts.flavor = "woff"
    opts.layout_features = features
    opts.hinting = False
    opts.desubroutinize = True
    opts.name_IDs = [1, 2, 4, 6]
    opts.notdef_outline = True
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=UNICODES)
    sub.subset(font)
    font.flavor = "woff"
    font.save(out_path)
    print(f"wrote {os.path.relpath(out_path, ROOT)} ({os.path.getsize(out_path):,} bytes)")
    return advances(font)


def main(src):
    os.makedirs(OUT, exist_ok=True)
    metrics = {}
    metrics["display"] = save_subset(
        TTFont(os.path.join(src, "ArchivoBlack-Regular.ttf")),
        os.path.join(OUT, "archivo-black.woff"),
        features=["kern"],
    )
    for weight, key in ((400, "mono"), (700, "mono-b")):
        var = TTFont(os.path.join(src, "JetBrainsMono-wght.ttf"))
        static = instancer.instantiateVariableFont(var, {"wght": weight})
        # No layout features: JetBrains Mono's code ligatures would merge "//".
        metrics[key] = save_subset(
            static, os.path.join(OUT, f"jetbrains-mono-{weight}.woff"), features=[]
        )
    with open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(metrics, f, ensure_ascii=False, sort_keys=True, indent=0)
        f.write("\n")
    print("wrote fonts/metrics.json")
    for name in ("OFL-ArchivoBlack.txt", "OFL-JetBrainsMono.txt"):
        shutil.copy(os.path.join(src, name), os.path.join(OUT, name))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
