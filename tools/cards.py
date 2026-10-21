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


if __name__ == "__main__":
    for t in TITLES + LABELS:
        px, n = strip(t)
        print(f"{n:2} {t}")
        print("\n".join("".join(".:?#"[v] for v in r) for r in px[2:14]))
