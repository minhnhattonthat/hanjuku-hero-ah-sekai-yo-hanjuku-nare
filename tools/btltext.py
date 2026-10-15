"""Battle messages: pointer table $1D:F400 (file 0xEF400, 1152 x 16-bit), strings in bank $17 (reader $03:CD1E).

Codes: 00 end; 01-07, 09, 0A inserts; 08?; 0B-0F; 1A newline; 1B; 1C; 2B xx (1 arg); 3C quote mark; others glyphs.
"""
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLE = 0xEF400
COUNT = 1152
BANK = 0x17


def ptrs(rom):
    return [struct.unpack_from("<H", rom, TABLE + 2 * i)[0] for i in range(COUNT)]


def off(p):
    return (BANK << 15) | (p & 0x7FFF)


CTRL = ["00={end}", "1A={n}", "1B={1B}", "1C={w}", "2B={wait:1}"] + [
    f"{c:02X}={{v{c:02X}}}" for c in range(1, 0x10)]


def table(base):
    """Battle-text table: base glyph table (jp.tbl or en.tbl lines) + battle control codes."""
    from tbl import Table
    lines = [ln for ln in Path(base).read_text(encoding="utf-8").splitlines()
             if not ln.startswith(("00=", "1A=", "1B=", "1C=", "2B="))]
    return Table(lines + CTRL)


def dump(rom):
    t = table(ROOT / "tbl" / "jp.tbl")
    out, seen = [], {}
    for i, p in enumerate(ptrs(rom)):
        o = off(p)
        n = strlen(rom, o)
        text, used = t.decode(rom, o, n - 1)
        e = {"id": f"B{i:03X}", "off": f"{o:06X}", "jp": text, "en": ""}
        if o in seen:
            e["same_as"] = seen[o]
        else:
            seen[o] = e["id"]
        out.append(e)
    return out


def strlen(rom, o):
    """Length through the 00 terminator, skipping the 2B argument byte."""
    q = o
    while True:
        b = rom[q]
        if b == 0x00:
            return q + 1 - o
        q += 2 if b == 0x2B else 1
