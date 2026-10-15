"""Menu/system messages: VM text run by $04:E40B from table $1F:B663 (72 x 16-bit, bank $1F), end 00.

Dumped to script/menu.json with the event-message token syntax (tools/events.py).
"""
import struct
from pathlib import Path

import events
import script

TABLE = 0xFB663
COUNT = 72
BANK = 0x1F


def ptrs(rom):
    return [struct.unpack_from("<H", rom, TABLE + 2 * i)[0] for i in range(COUNT)]


def items(rom, o):
    out = []
    for it in script.parse(rom, o, header=False):
        out.append(it)
    return out


def dump(rom):
    out = []
    seen = {}
    for i, p in enumerate(ptrs(rom)):
        o = script.off(BANK, p)
        its = items(rom, o)
        text, codes = events.render([it for it in its if it[0] != "end"])
        e = {"id": f"M{i:02X}", "off": f"{o:06X}", "jp": text, "en": "", "codes": codes}
        if o in seen:
            e["same_as"] = seen[o]
        else:
            seen[o] = e["id"]
        out.append(e)
    return out


def encode_entry(rom, e, table, field="en"):
    o = int(e["off"], 16)
    its = items(rom, o)
    txt = e.get(field) or ""
    if not txt:
        return b"".join(bytes(it[2]) for it in its)
    return events.encode(txt, e["codes"], table) + b"\x00"
