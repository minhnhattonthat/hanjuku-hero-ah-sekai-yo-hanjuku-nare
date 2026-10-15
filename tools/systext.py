"""System strings printed by $00:F086 (bank $01 fixed, Y = pointer from code immediates), file 0xC842-0xD853.

Codes: 00 end; 1D xx raw tile; 18 skip a column; 19 special; 1A newline (2 rows); 1B row down; 1C row up; others glyphs.
English goes to the expanded ROM; each original string start is overwritten with a far jump `01 lo hi bank`
(new printer code 01, asm/main.asm SysFetch). Strings shorter than 4 bytes stay in place (must fit).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START, END = 0xC842, 0xD853
CTRL = ["00={end}", "1A={n}", "18={sk}", "19={19}", "1B={dn}", "1C={up}", "1D={raw:1}"]


def table(base):
    from tbl import Table
    lines = [ln for ln in Path(base).read_text(encoding="utf-8").splitlines()
             if not ln.startswith(tuple(c[:3] for c in CTRL))]
    return Table(lines + CTRL)


def strings(rom):
    """[(offset, length incl. 00)] for every string in the region."""
    out, o = [], START
    while o < END:
        q = o
        while rom[q] != 0:
            q += 2 if rom[q] == 0x1D else 1
        out.append((o, q + 1 - o))
        o = q + 1
    return out


def dump(rom):
    t = table(ROOT / "tbl" / "jp.tbl")
    out = []
    for o, n in strings(rom):
        out.append({"id": f"S{o:05X}", "off": f"{o:06X}", "len": n, "jp": t.decode(rom, o, n - 1)[0], "en": ""})
    return out
