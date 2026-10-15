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


LIG_CODES = [c for c in range(0x8A, 0xB1) if c != 0xA7]  # free font codes for two-letter tiles


def _merge(txt, ligs, limit=SIZE):
    """Split txt into cells (1 char or a ligature pair) until it fits `limit` cells."""
    cells = list(txt)
    i = 0
    while len(cells) > limit and i < len(cells) - 1:
        if len(cells[i]) == 1 and len(cells[i + 1]) == 1 and cells[i] + cells[i + 1] in ligs:
            cells[i:i + 2] = [cells[i] + cells[i + 1]]
        i += 1
    return cells


LIG_OK = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ")


def choose_ligatures(texts):
    """Pick pairs so that as many texts as possible fit 8 cells (cheapest texts first).
    Returns ({pair: code}, [texts that still don't fit])."""
    freq = {}
    for t in texts:
        for a, b in zip(t, t[1:]):
            if a in LIG_OK and b in LIG_OK and a + b != "  ":
                freq[a + b] = freq.get(a + b, 0) + 1
    ligs, left = {}, []
    budget = len(LIG_CODES)
    for t in sorted(set(texts), key=lambda s: (len(s), s)):
        if len(_merge(t, ligs)) <= SIZE:
            continue
        trial = dict(ligs)
        cand = sorted({a + b for a, b in zip(t, t[1:]) if a in LIG_OK and b in LIG_OK and a + b != "  "} - set(trial),
                      key=lambda k: -freq[k])
        for p in cand:
            if len(_merge(t, trial)) <= SIZE or len(trial) >= budget:
                break
            trial[p] = 0
        if len(_merge(t, trial)) <= SIZE and len(trial) <= budget:
            ligs = trial
        else:
            left.append(t)
    return {p: LIG_CODES[i] for i, p in enumerate(ligs)}, left


def encode(e, table, field="en", ligs=None):
    pad = int(e["pad"], 16)
    txt = e.get(field)
    if ligs and len(txt) > SIZE:
        b = bytes(ligs[c] if len(c) == 2 else table.encode(c)[0] for c in _merge(txt, ligs))
    else:
        b = table.encode(txt)
    if len(b) > SIZE:
        raise ValueError(f"{e['id']}: {txt!r} is {len(b)} bytes > {SIZE}")
    return b + bytes([pad]) * (SIZE - len(b))
