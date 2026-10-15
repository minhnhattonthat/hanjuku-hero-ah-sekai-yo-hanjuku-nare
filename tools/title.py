"""Title screen (mode 7) English art: ribbon "HANJUKU HERO" and subtitle "Ah, World, Be Soft-Boiled...!!".

Input (generated once, kept out of git): work/title_ram.bin (WRAM dump at title frame 600: decompressed mode-7
tiles at $7F:8000) and work/title_vram.bin (VRAM at frame 690, for the tilemap). Output: assets/title_m7_en.bin =
tiles $01-$E2 (64 bytes each, 8bpp), copied over $7F:8000 by asm/main.asm (TitlePatch) before the game DMAs them.

    python -X utf8 tools/title.py [--png work/title_en.png]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import font_en  # noqa: E402
import font_tiny  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
NT = 0xE2  # tiles $01..$E2
RIB_BG, INK, SUB, SUB_SH = 9, 1, 12, 11


def main():
    ram = (ROOT / "work" / "title_ram.bin").read_bytes()
    vram = (ROOT / "work" / "title_vram.bin").read_bytes()
    tiles = bytearray(ram[0x18000:0x18000 + NT * 64])
    tm = [vram[2 * i] for i in range(128 * 128)]
    W, H = 256, 120
    img = [[0] * W for _ in range(H)]
    owner = {}
    for ty in range(H // 8):
        for tx in range(32):
            t = tm[ty * 128 + tx]
            if 1 <= t <= NT:
                owner.setdefault(t, (tx, ty))
            for p in range(64):
                img[ty * 8 + p // 8][tx * 8 + p % 8] = tiles[(t - 1) * 64 + p] if 1 <= t <= NT else 0

    # --- ribbon: erase the kana inside the pink band, then write HANJUKU HERO along the band centre
    x0, x1 = 84, 168
    centre = {}
    for x in range(x0, x1):
        ys = [y for y in range(0, 40) if img[y][x] == RIB_BG]
        if not ys:
            continue
        top, bot = min(ys), max(ys)
        centre[x] = (top + bot) / 2
        for y in range(top, bot + 1):
            if img[y][x] in (INK, 10):
                img[y][x] = RIB_BG
    text = "HANJUKU HERO"
    adv = 5
    start = 128 - len(text) * adv // 2
    for i, ch in enumerate(text):
        if ch == " ":
            continue
        rows = font_tiny.TINY[ch]
        lx = start + i * adv
        cx = min(centre, key=lambda x: abs(x - (lx + 3)))
        y0 = int(round(centre[cx] - 3.5))
        for yy, r in enumerate(rows[:7]):
            for xx, c in enumerate(r[:6]):
                if c == "#" and img[y0 + yy][lx + xx] == RIB_BG:
                    img[y0 + yy][lx + xx] = INK

    # --- subtitle: rows 13-14 (y 104-119), clear and write two lines with a drop shadow
    for y in range(104, 120):
        for x in range(64, 200):
            if img[y][x] in (SUB, SUB_SH):
                img[y][x] = 0

    def put(s, x, y):
        for ch in s:
            if ch != " ":
                for yy, r in enumerate(font_en.GLYPHS[ch]):
                    for xx, c in enumerate(r):
                        if c == "#":
                            img[y + yy][x + xx] = SUB
            x += 7
    put("Ah, World,", 97, 104)
    put("Be Soft-Boiled...!!", 66, 112)

    for t, (tx, ty) in owner.items():
        for p in range(64):
            tiles[(t - 1) * 64 + p] = img[ty * 8 + p // 8][tx * 8 + p % 8]
    (ROOT / "assets").mkdir(exist_ok=True)
    (ROOT / "assets" / "title_m7_en.bin").write_bytes(tiles)
    if "--png" in sys.argv:
        from PIL import Image
        pal = open(ROOT / "work" / "qa" / "tram" / "ppu_000690.pal.bin", "rb").read()
        im = Image.new("RGB", (W, H))
        for y in range(H):
            for x in range(W):
                c = pal[2 * img[y][x]] | pal[2 * img[y][x] + 1] << 8
                im.putpixel((x, y), ((c & 31) << 3, (c >> 5 & 31) << 3, (c >> 10 & 31) << 3))
        im.resize((W * 3, H * 3), Image.NEAREST).save(sys.argv[sys.argv.index("--png") + 1])


if __name__ == "__main__":
    main()
