"""Episode title cards: English titles and "Episode N" labels drawn as 16x16 sprite glyphs (2bpp, colour 3 ink on a
colour 1 outline, like the kanji card font). The card builders ($09:F8A8 label, $09:F919 title) copy glyphs from the
blob below instead of the kanji font in $7E:A72E (asm/main.asm CardLabel/CardTitle).

Blob at $3F:8000 (CARDS): 24 entries x 4 bytes (glyph data address in bank $3F, glyph count, 0, 0), titles for
episodes 1-12 then labels for episodes 1-12, then the glyphs (64 bytes each: tiles TL, TR, BL, BR).
A card line holds 16 glyphs (256 px); the label 4 (OAM $0400-$040F, the title's sprites follow at $0410).
"""
from font_en import GLYPHS

CARDS = 0x1F8000  # $3F:8000

# titles as in the "Next time on Hanjuku Hero" previews (script/events.json), shortened to one 256 px line
TITLES = [
    "The Black Egg Smells of Danger",
    "Two Hanjuku Heroes!?",
    "Ah, Love's Flower, Fallen in Battle",
    "Seasons, Return to My Heart!",
    "Farewell, Beloved Eggman",
    "The Distant Egg Homeland",
    "Nightmare of the Dead on the 13th",
    "Hard-Boiled Shogun's Ambition",
    "The Earth Trembles... Not from Cold!",
    "You're the Boss! Mr. President!!",
    "At the End of Love and Hate...",
    "Ah, World, Be Soft-Boiled...!!",
]
LABELS = [f"Episode {i}" for i in range(1, 12)] + ["Finale"]


def strip(text):
    """Text -> 16 rows of pixels (0 blank, 1 outline, 3 ink), centred in whole 16 px cells."""
    cols = []  # ink columns, 8 rows each
    for ch in text:
        rows = ["........"] * 8 if ch == " " else GLYPHS[ch]
        ink = [x for x in range(8) for r in rows if r[x] == "#"]
        w = max(ink) + 1 if ink else 3
        cols += [[rows[y][x] == "#" for y in range(8)] for x in range(w)] + [[False] * 8]
    cols = cols[:-1]
    n = (len(cols) + 2 + 15) // 16
    left = (n * 16 - len(cols)) // 2
    px = [[0] * (n * 16) for _ in range(16)]
    for x, col in enumerate(cols):
        for y, on in enumerate(col):
            if on:
                px[4 + y][left + x] = 3
    for y in range(16):
        for x in range(n * 16):
            if px[y][x] == 0 and any(px[yy][xx] == 3 for yy in range(max(0, y - 1), min(16, y + 2))
                                     for xx in range(max(0, x - 1), min(n * 16, x + 2))):
                px[y][x] = 1
    return px, n


def glyphs(px, n):
    out = bytearray()
    for c in range(n):
        for ty, tx in ((0, 0), (0, 8), (8, 0), (8, 8)):
            for y in range(8):
                row = px[ty + y][c * 16 + tx:c * 16 + tx + 8]
                out += bytes([sum((v & 1) << (7 - x) for x, v in enumerate(row)),
                              sum((v >> 1) << (7 - x) for x, v in enumerate(row))])
    return out


def blob():
    lines = TITLES + LABELS
    head, data = bytearray(), bytearray()
    for i, text in enumerate(lines):
        px, n = strip(text)
        assert n <= (16 if i < 12 else 4), (text, n)
        head += (0x8000 + 4 * len(lines) + len(data)).to_bytes(2, "little") + bytes([n, 0])
        data += glyphs(px, n)
    out = head + data
    assert len(out) <= 0x8000
    return bytes(out)


# curtain call and end screen: BG1 4bpp tiles $104-$173 raw at $02:EE40 (file 0x16E40), loaded with the curtain
# call. Marquee おわり～!! = tiles $106-$10F over $110-$119 (80x16, bulbs in cycling colours C/D/E on F); six
# banners 祝 半 熟 / 終 了 !! = one 8x24 tile column each (ink 1 on 3, rows 0-3 and 20-23 are the banner frame).
CURTAIN = 0x16E40
MARQUEE = "END!!"
BANNERS = [("H", 0x122, 3), ("O", 0x155, 1), ("O", 0x158, 1), ("R", 0x15B, 1), ("A", 0x15E, 1), ("Y", 0x161, 1)]


def tile_px(rom, t):
    b = rom[CURTAIN + 32 * (t - 0x104):][:32]
    return [[sum(((b[(p // 2) * 16 + 2 * y + (p & 1)] >> (7 - x)) & 1) << p for p in range(4)) for x in range(8)]
            for y in range(8)]


def put_tile(rom, t, px):
    b = bytearray(32)
    for y in range(8):
        for x in range(8):
            for p in range(4):
                b[(p // 2) * 16 + 2 * y + (p & 1)] |= ((px[y][x] >> p) & 1) << (7 - x)
    rom[CURTAIN + 32 * (t - 0x104):CURTAIN + 32 * (t - 0x103)] = b


def curtain_patch(rom):
    # marquee: each font pixel is one bulb at (2x, 2y), 16 px per letter
    px = [[0xF] * 80 for _ in range(16)]
    left = (80 - 16 * len(MARQUEE)) // 2
    for i, ch in enumerate(MARQUEE):
        for y, row in enumerate(GLYPHS[ch]):
            for x, on in enumerate(row):
                if on == "#":
                    bx, by = left + 16 * i + 2 * x + 2, 2 * y + 1
                    px[by][bx] = 0xC + (bx // 2 + by // 2) % 3
    for r, base in ((0, 0x106), (1, 0x110)):
        for c in range(10):
            put_tile(rom, base + c, [line[8 * c:8 * c + 8] for line in px[8 * r:8 * r + 8]])
    # banners: the letter doubled in height on rows 4-19, centred in the column
    for ch, top, step in BANNERS:
        tiles = [top, top + step, top + 2 * step]
        col = sum((tile_px(rom, t) for t in tiles), [])
        for y in range(4, 20):
            col[y] = [3] * 8
        for y, row in enumerate(GLYPHS[ch]):
            for x, on in enumerate(row[:7]):
                if on == "#":
                    col[4 + 2 * y][x + 1] = col[5 + 2 * y][x + 1] = 1
        for i, t in enumerate(tiles):
            put_tile(rom, t, col[8 * i:8 * i + 8])


# end screen after the credits (めでたし めでたし): tiles $165-$173 (colour 1 paper, 4 ink), tilemap rows 13-14 raw
# at $1E:FE80 (32 words each, attr $14xx, $1564 = blank tile)
END_TILES, END_MAP = CURTAIN + 32 * (0x164 - 0x104), 0x0F7E80
END = ["And they lived", "happily ever after."]


def end_patch(rom):
    chars = sorted({c for line in END for c in line} - {" "})
    assert len(chars) <= 15, chars
    for i, ch in enumerate(chars):
        t = bytearray(32)
        for y, row in enumerate(GLYPHS[ch]):
            for x, px in enumerate(row):
                v = 4 if px == "#" else 1
                for p in range(4):
                    t[(p // 2) * 16 + 2 * y + (p & 1)] |= ((v >> p) & 1) << (7 - x)
        rom[END_TILES + 32 * (i + 1):END_TILES + 32 * (i + 2)] = t
    for r, line in enumerate(END):
        row = [" "] * 32
        left = (32 - len(line)) // 2
        row[left:left + len(line)] = line
        words = [0x1564 + (chars.index(c) + 1 if c != " " else 0) for c in row]
        rom[END_MAP + 64 * r:END_MAP + 64 * (r + 1)] = b"".join(w.to_bytes(2, "little") for w in words)


if __name__ == "__main__":
    for t in TITLES + LABELS:
        px, n = strip(t)
        print(f"{n:2} {t}")
        print("\n".join("".join(".:?#"[v] for v in r) for r in px[2:14]))
