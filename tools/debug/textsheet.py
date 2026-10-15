"""Contact sheet of the *settled* text-window frames of a tour run: a frame is kept when it equals the next shot
(text finished typing, waiting for a button) and differs from the last kept one.

    python -X utf8 tools/debug/textsheet.py RUN_DIR [OUT.png] [--box 0,120,256,104] [--max 30]
"""
import glob
import os
import sys

from PIL import Image, ImageChops


def main():
    d = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else os.path.join(d, "text.png")
    box = (0, 120, 256, 224)
    if "--box" in sys.argv:
        x, y, w, h = map(int, sys.argv[sys.argv.index("--box") + 1].split(","))
        box = (x, y, x + w, y + h)
    mx = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 30
    fr = int(sys.argv[sys.argv.index("--from") + 1]) if "--from" in sys.argv else 0
    fs = [f for f in sorted(glob.glob(os.path.join(d, "f0*.png"))) if int(os.path.basename(f)[1:7]) >= fr]
    ims = [Image.open(f).convert("RGB").crop(box) for f in fs]
    def changed(a, b):  # pixels that differ (a blinking "more" arrow is ~30 px)
        return sum(ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v > 24 else 0).histogram()[255:])

    keep, last = [], None
    for a, b in zip(ims, ims[1:]):
        if changed(a, b) > 60:
            continue
        if last is not None and changed(a, last) <= 60:
            continue
        keep.append(a)
        last = a
    keep = keep[:mx]
    if not keep:
        print("no settled frames")
        return 1
    w, h = keep[0].size
    cols = 3
    rows = (len(keep) + cols - 1) // cols
    sheet = Image.new("RGB", (w * cols, h * rows))
    for i, im in enumerate(keep):
        sheet.paste(im, ((i % cols) * w, (i // cols) * h))
    sheet.save(out)
    print(out, len(keep))
    return 0


if __name__ == "__main__":
    sys.exit(main())
