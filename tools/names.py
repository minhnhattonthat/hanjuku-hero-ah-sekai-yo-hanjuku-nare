"""Fixed-length name tables (8 bytes per record). Dumped to script/names.json.

Table "A" (bank $17, file 0xB8000-0xB9707, 00-padded): monsters 000-07F, generals 080-0FF, attacks 100-1DF?,
commands/status/hobbies/eggs/attitudes after (see docs/re/text.md). Table "C" (file 0xC5E00, FF-padded): castles.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = {  # name: (file offset, count, pad byte)
    "A": (0xB8000, 737, 0x00),
    "C": (0xC5E00, 117, 0xFF),
}
SIZE = 8


def dump(rom, table):
    out = []
    for name, (base, count, pad) in TABLES.items():
        for i in range(count):
            o = base + SIZE * i
            raw = rom[o:o + SIZE]
            n = len(raw.rstrip(bytes([pad]))) if pad == 0xFF else (raw.index(0) if 0 in raw else SIZE)
            text = table.decode(raw, 0, n)[0] if n else ""
            out.append({"id": f"{name}{i:03X}", "off": f"{o:06X}", "jp": text, "en": "", "max": SIZE,
                        "pad": f"{pad:02X}"})
    return out


def encode(e, table, field="en"):
    pad = int(e["pad"], 16)
    txt = e.get(field)
    b = table.encode(txt)
    if len(b) > SIZE:
        raise ValueError(f"{e['id']}: {txt!r} is {len(b)} bytes > {SIZE}")
    return b + bytes([pad]) * (SIZE - len(b))
