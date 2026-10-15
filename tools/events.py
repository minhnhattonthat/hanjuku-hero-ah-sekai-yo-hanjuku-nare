"""Event-script messages: extract (dump) and re-serialize (build). Text format: script/events.json.

A message runs from a text item to the window close (18), a script end or a goto, with inline controls:
  {n} 1A newline   {w} 1C wait for key   {p} 1B clear window   {hero} 34 player name
  {name9}..{nameE} F9-FE name inserts   {str:XX} F8 XX
  {#k} any other command, kept byte-exact (raw bytes in the message's "codes" list), position kept in order.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import script  # noqa: E402
from tbl import Table  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
JP = Table.load(ROOT / "tbl" / "jp.tbl")
INLINE = {0x1A: "{n}", 0x1C: "{w}", 0x1B: "{p}", 0x34: "{hero}", 0xF9: "{name9}", 0xFA: "{nameA}",
          0xFB: "{nameB}", 0xFC: "{nameC}", 0xFD: "{nameD}", 0xFE: "{nameE}"}
INLINE_ENC = {v: k for k, v in INLINE.items()}
STOP = {0x18}


def script_starts(rom):
    """Unique script start offsets per bank -> (sorted list of (off, end, [ids]))."""
    ptrs = script.script_ptrs(rom)
    by = {}
    for sid, (bank, p) in ptrs.items():
        by.setdefault(bank, {}).setdefault(script.off(bank, p), []).append(sid)
    out = []
    for bank, d in by.items():
        offs = sorted(d)
        for i, o in enumerate(offs):
            end = offs[i + 1] if i + 1 < len(offs) else None
            out.append((bank, o, end, d[o]))
    return out


def items_of(rom, off, end):
    items = []
    for it in script.parse(rom, off):
        items.append(it)
        if end is not None and it[1] + len(it[2]) >= end:
            break
    last = items[-1][1] + len(items[-1][2])
    if end is None:
        end = last
    if last > end:  # not a parseable script (e.g. id 2C = one 00 byte): keep raw
        return [("raw", off, rom[off:end])], end
    return items, end


def is_goto(b):
    return b[0] == 0x14 and b[1] in (0x19, 0x1A)


def messages(items):
    """Group items into (start_index, stop_index_exclusive) message spans."""
    spans, i, n = [], 0, len(items)
    while i < n:
        if items[i][0] != "text":
            i += 1
            continue
        j = i
        last_text = i
        while j < n:
            k, pos, b = items[j]
            if k == "end" or (k == "cmd" and (b[0] in STOP or is_goto(b))):
                break
            if k == "text" or (k == "cmd" and b[0] in INLINE) or (k == "cmd" and b[0] == 0xF8):
                last_text = j
            j += 1
        stop = last_text + 1
        # keep trailing wait/clear controls inside the message
        while stop < n and items[stop][0] == "cmd" and items[stop][2][0] in (0x1C, 0x1B, 0x1A):
            stop += 1
        spans.append((i, stop))
        i = stop
    return spans


def render(items, table=JP):
    """Items -> (text, codes)."""
    out, codes = [], []
    for k, pos, b in items:
        if k == "text":
            out.append(table.decode(bytes(b), 0, len(b))[0])
        elif k == "cmd" and b[0] in INLINE and len(b) == 1:
            out.append(INLINE[b[0]])
        elif k == "cmd" and b[0] == 0xF8:
            out.append("{str:%02X}" % b[1])
        else:
            out.append("{#%d}" % len(codes))
            codes.append(bytes(b).hex(" "))
    return "".join(out), codes


TOKEN = re.compile(r"\{[^}]*\}")


def encode(text, codes, table):
    out = bytearray()
    pos = 0
    for m in TOKEN.finditer(text):
        out += table.encode(text[pos:m.start()])
        t = m.group()
        if t in INLINE_ENC:
            out.append(INLINE_ENC[t])
        elif t.startswith("{str:"):
            out += bytes([0xF8, int(t[5:7], 16)])
        elif t.startswith("{#"):
            out += bytes.fromhex(codes[int(t[2:-1])])
        else:
            out += table.encode(t)
        pos = m.end()
    out += table.encode(text[pos:])
    return bytes(out)


def dump(rom):
    scripts = []
    for bank, off, end, ids in sorted(script_starts(rom), key=lambda x: x[1]):
        items, end = items_of(rom, off, end)
        msgs = []
        for a, b in messages(items):
            text, codes = render(items[a:b])
            msgs.append({"id": f"{off:06X}_{items[a][1] - off:04X}", "jp": text, "en": "", "codes": codes})
        scripts.append({"off": f"{off:06X}", "end": f"{end:06X}", "bank": f"{bank:02X}",
                        "ids": [f"{i:02X}" for i in ids], "msgs": msgs})
    return scripts


def choice_mapper(en_table, jp_table=JP):
    """Command bytes -> command bytes with the 19 (2x6) / 33 (3x8) choice labels translated (script/choices.json)."""
    m = json.loads((ROOT / "script" / "choices.json").read_text(encoding="utf-8"))

    def fix(b):
        b = bytes(b)
        if not b or b[0] not in (0x19, 0x33):
            return b
        n = 6 if b[0] == 0x19 else 8
        out = bytearray(b[:1])
        for i in range(1, len(b), n):
            lab = jp_table.decode(b[i:i + n], 0, n)[0].rstrip("　")
            en = m.get(lab) or m.get(jp_table.decode(b[i:i + n], 0, n)[0])
            if en is None:
                out += b[i:i + n]
                continue
            e = en_table.encode(en)
            if len(e) > n:
                raise ValueError(f"choice {en!r} longer than {n}")
            out += e + b"\xFF" * (n - len(e))
        return bytes(out)
    return fix


def rebuild_script(rom, s, table, field="en", fallback_jp=True, cmd_map=None):
    """Return new bytes for one script dict s (from events.json)."""
    off, end = int(s["off"], 16), int(s["end"], 16)
    items, _ = items_of(rom, off, end)
    spans = messages(items)
    assert len(spans) == len(s["msgs"]), s["off"]
    fix = cmd_map or (lambda x: bytes(x))
    out = bytearray()
    i = 0
    for (a, b), m in zip(spans, s["msgs"]):
        for it in items[i:a]:
            out += fix(it[2]) if it[0] == "cmd" else it[2]
        txt = m.get(field) or ""
        if txt:
            codes = [fix(bytes.fromhex(c)).hex(" ") for c in m["codes"]]
            out += encode(txt, codes, table)
        else:
            out += b"".join(bytes(it[2]) for it in items[a:b])
        i = b
    for it in items[i:]:
        out += fix(it[2]) if it[0] == "cmd" else it[2]
    last = items[-1][1] + len(items[-1][2])
    out += rom[last:end]  # tail bytes (padding after F7, data)
    return bytes(out)


if __name__ == "__main__":
    dst = ROOT / "script" / "events.json"
    if dst.exists() and "--force" not in sys.argv:
        sys.exit(f"{dst} exists; refusing to overwrite English (use --force)")
    rom = script.ORIG.read_bytes()
    dst.parent.mkdir(exist_ok=True)
    data = dump(rom)
    dst.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(len(data), "scripts", sum(len(s["msgs"]) for s in data), "messages")
