"""Leftover-Japanese check on a BUILT ROM, following the pointers the game uses (this game's English letters share
codes 0x40-0x89 with kana, so a plain byte scan can't tell them apart). A reachable string fails when it holds a
glyph code outside the English table: kana-only codes (0x8A-0xF6 except ligatures in names, B0-C3 digits ok).

    python -X utf8 tools/jpcheck.py build/hanjuku_en.sfc     (exit 1 on any hit)
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import btltext  # noqa: E402
import mktbl  # noqa: E402
import names  # noqa: E402
import rawtext  # noqa: E402
import script  # noqa: E402
import systext  # noqa: E402

EN_OK = set(mktbl.EN) | set(range(0xB0, 0xC4))  # English glyphs + digits/letters tiles


def lorom(bank, p):
    return (bank << 15) | (p & 0x7FFF)


def tab(rom, at, n):
    return [lorom(rom[at + 3 * i + 2], struct.unpack_from("<H", rom, at + 3 * i)[0]) for i in range(n)]


def bad_text(bs, extra=()):
    return [b for b in bs if b >= 0x3A and b not in EN_OK and b not in extra]


def main():
    rom = Path(sys.argv[1]).read_bytes()
    hits = []
    for i, o in enumerate(tab(rom, 0x100800, 256)):
        if i in (0x2C, 0x44, 0x46, 0x48, 0x4A):  # no text: dummy / "14 04" battle starts that never return
            continue
        try:
            for k, pos, b in script.parse(rom, o):
                if k == "text" and bad_text(b):
                    hits.append(f"script {i:02X} @{pos:06X}: {bytes(b)[:16].hex()}")
        except Exception as ex:  # noqa: BLE001
            hits.append(f"script {i:02X}: parse error {ex}")
    for i, o in enumerate(tab(rom, 0x100B00, 72)):
        for k, pos, b in script.parse(rom, o, header=False):
            if k == "text" and bad_text(b):
                hits.append(f"menu {i:02X}: {bytes(b)[:16].hex()}")
    for i, o in enumerate(tab(rom, 0x101000, btltext.COUNT)):
        n = btltext.strlen(rom, o)
        s = rom[o:o + n]
        q, txt = 0, []
        while q < len(s) - 1:
            if s[q] == 0x2B:
                q += 2
                continue
            txt.append(s[q])
            q += 1
        if bad_text(txt, (0x3C,)):
            hits.append(f"battle {i:03X}: {s[:16].hex()}")
    for o, n in systext.strings(script.ORIG.read_bytes()):
        s = rom[o:o + max(n, 4)]
        if s[0] == 0x01:
            t = lorom(s[3], s[1] | s[2] << 8)
            s = rom[t:rom.index(0, t)]
        else:
            s = s[:n]
        txt, q = [], 0
        while q < len(s) and s[q] != 0:
            if s[q] == 0x1D:
                q += 2
                continue
            txt.append(s[q])
            q += 1
        if bad_text(txt, (0x3C,)):
            hits.append(f"system {o:06X}: {bytes(s)[:16].hex()}")
    ligs = set(names.LIG_CODES)
    for base, count, pad in names.TABLES.values():
        for i in range(count):
            o = base + 8 * i
            if bad_text(rom[o:o + 8], ligs):
                hits.append(f"name {o:06X}: {rom[o:o + 8].hex()}")
    for off, n, _ in rawtext.ENTRIES:
        if bad_text(rom[off:off + n]):
            hits.append(f"raw {off:06X}")
    for h in hits[:80]:
        print(h)
    print(f"jpcheck: {len(hits)} reachable strings with Japanese-only glyph codes")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
