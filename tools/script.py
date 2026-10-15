"""Event-script VM parser (bank $04 interpreter at $04:897B). See docs/re/text.md.

Script ids 0x00-0xFF: <0x40 bank $1A table $1A:8000; 0x40-0x6A bank $1B $1B:8000 (id-0x40); 0x6B-0xA9 bank $1C
$1C:8000 (id-0x6B); 0xAA-0xFF bank $1F $1F:C000 (id-0xAA). Pointers are 16-bit within the bank.

Byte classes: 00/F7 end; 01-0F select actor (n-1); 10-39 and F8-FE commands (ARGS); 3A-FE (not F7-FE) and FF text.
"""
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIG = ROOT / "rom" / "Hanjuku Hero - Ah, Sekai yo Hanjuku Nare...!! (Japan).sfc"

BANKS = [  # (first id, count, bank, table cpu addr)
    (0x00, 0x40, 0x1A, 0x8000),
    (0x40, 0x2B, 0x1B, 0x8000),
    (0x6B, 0x3F, 0x1C, 0x8000),
    (0xAA, 0x56, 0x1F, 0xC000),
]
# argument bytes read by each command's init handler (table $04:FC3F)
ARGS = {0x10: 0, 0x11: 0, 0x12: 0, 0x13: 2, 0x14: 1, 0x15: 0, 0x16: 0, 0x19: 12, 0x24: 1, 0x25: 1, 0x26: 1,
        0x27: 1, 0x28: 0, 0x29: 0, 0x2A: 0, 0x2B: 1, 0x2C: 1, 0x2D: 1, 0x2F: 2, 0x30: 1, 0x31: 1, 0x32: 1,
        0x33: 24, 0x35: 0, 0x37: 1, 0xF8: 1}
# command 14 sub-ops (table $04:FD1B): extra argument bytes after the sub-op byte
SUB14 = {0x00: 1, 0x01: 1, 0x02: 1, 0x04: 2, 0x10: 1, 0x13: 1, 0x14: 1, 0x15: 1, 0x16: 1, 0x17: 1, 0x19: 1,
         0x1B: 1, 0x1C: 1, 0x1D: 1, 0x1E: 2, 0x21: 1, 0x24: 1, 0x2A: 1, 0x2B: 1, 0x2D: 1, 0x2E: 1}


def cmdlen(rom, pos):
    b = rom[pos]
    if b == 0x14:
        s = rom[pos + 1]
        if s == 0x1A:  # random goto: n, then n script ids
            return 3 + rom[pos + 2]
        return 2 + SUB14.get(s, 0)
    return 1 + ARGS.get(b, 0)


def off(bank, addr):
    return (bank << 15) | (addr & 0x7FFF)


def script_ptrs(rom):
    out = {}
    for first, n, bank, tab in BANKS:
        for i in range(n):
            p = struct.unpack_from("<H", rom, off(bank, tab) + 2 * i)[0]
            out[first + i] = (bank, p)
    return out


def parse(rom, pos, limit=0x4000):
    """Yield (kind, offset, bytes) items from file offset pos until end. kind: text/cmd/actor/end."""
    start = pos
    while rom[pos] != 0xFF:  # actor records (sprite, x, y, flags) until FF ($04:8915)
        pos += 4
    yield ("head", start, rom[start:pos + 1])
    pos += 1
    while pos - start < limit:
        b = rom[pos]
        if b in (0x00, 0xF7):
            yield ("end", pos, rom[pos:pos + 1])
            return
        if 1 <= b <= 0x0F:
            yield ("actor", pos, rom[pos:pos + 1])
            pos += 1
        elif 0x10 <= b <= 0x39 or 0xF8 <= b <= 0xFE:
            if b == 0x2E:  # 2E n, then n sub-items (commands or one text char each)
                n = rom[pos + 1]
                q = pos + 2
                for _ in range(n):
                    c = rom[q]
                    while 1 <= c <= 0x0F:
                        q += 1
                        c = rom[q]
                    if c in (0x00, 0xF7):
                        break
                    q += cmdlen(rom, q) if (0x10 <= c <= 0x39 or 0xF8 <= c <= 0xFE) else 1
                yield ("cmd", pos, rom[pos:q])
                pos = q
                continue
            n = cmdlen(rom, pos)
            yield ("cmd", pos, rom[pos:pos + n])
            pos += n
        else:
            q = pos
            while q < len(rom) and (rom[q] >= 0x3A and rom[q] not in range(0xF7, 0xFF)):
                q += 1
            yield ("text", pos, rom[pos:q])
            pos = q
    raise ValueError(f"no end within {limit:#x} of {start:#x}")
