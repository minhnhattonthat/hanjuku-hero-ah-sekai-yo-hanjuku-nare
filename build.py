"""Build the English ROM.

    python -X utf8 build.py                 -> build/hanjuku_en.sfc
    python -X utf8 build.py --marker        -> every message replaced by its id (marker build, phase 5)
    python -X utf8 build.py --identity OUT  -> re-insert Japanese in place, no engine (must equal the original)
    python -X utf8 build.py --qa ID=TEXT    -> override one entry's English (width tests)
    python -X utf8 build.py --out PATH
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import btltext  # noqa: E402
import events  # noqa: E402
import font_en  # noqa: E402
import layout  # noqa: E402
import menutext  # noqa: E402
import mktbl  # noqa: E402
import names  # noqa: E402
import script  # noqa: E402
import systext  # noqa: E402
from tbl import Table  # noqa: E402

ASAR = ROOT / "tools" / "asar" / "asar.exe"
FONT = 0xE6000
SCRIPT_TAB, MSG_TAB, BTL_TAB = 0x100800, 0x100B00, 0x101000  # $20:8800, $20:8B00, $20:9000
DATA_FIRST_BANK = 0x21
ROM_SIZE = 0x200000


def load(name):
    return json.loads((ROOT / "script" / f"{name}.json").read_text(encoding="utf-8"))


class Packer:
    """Places blobs in LoROM banks (never crossing a bank), from bank `first` upward."""

    def __init__(self, rom, first, last=0x3F):
        self.rom, self.bank, self.last, self.pos = rom, first, last, 0x8000

    def put(self, blob):
        if len(blob) > 0x8000:
            raise ValueError("blob larger than a bank")
        if self.pos + len(blob) > 0x10000:
            self.bank += 1
            self.pos = 0x8000
            if self.bank > self.last:
                raise ValueError("out of ROM space")
        o = (self.bank << 15) | (self.pos & 0x7FFF)
        self.rom[o:o + len(blob)] = blob
        p = (self.pos, self.bank)
        self.pos += len(blob)
        return p

    def used(self):
        return (self.bank - DATA_FIRST_BANK) * 0x8000 + self.pos - 0x8000


def write_font(rom):
    for code, ch in mktbl.EN.items():
        if ch == " " or code < 0x3C:
            continue
        rows = font_en.GLYPHS.get(ch)
        if rows is None:
            continue  # ♪ ♥ ~ keep the game's glyphs
        o = FONT + code * 16
        for y, r in enumerate(rows):
            bits = int(r.replace("#", "1").replace(".", "0"), 2)
            rom[o + 2 * y] = 0xFF
            rom[o + 2 * y + 1] = bits


def asar(rom_path):
    r = subprocess.run([str(ASAR), "--fix-checksum=off", str(ROOT / "asm" / "main.asm"), str(rom_path)],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit("asar failed:\n" + r.stdout + r.stderr)


def marker_text(e, kind):
    """Marker English: keep every {token} in order; first text run becomes the id."""
    import re
    parts = re.split(r"(\{[^}]*\})", e["jp"])
    out, first = [], True
    for p in parts:
        if p.startswith("{"):
            out.append(p)
        elif p:
            out.append(e["id"].replace("_", "-") if first else "x")
            first = False
    return "".join(out)


def build(args):
    orig = script.ORIG.read_bytes()
    jp = events.JP
    en = Table.load(ROOT / "tbl" / "en.tbl")
    qa = dict(q.split("=", 1) for q in args.qa)

    def text_of(e, kind):
        if e["id"] in qa:
            return qa[e["id"]]
        if args.marker:
            return marker_text(e, kind)
        return e.get("en") or ""

    rom = bytearray(orig) + b"\xFF" * (ROM_SIZE - len(orig))
    out = Path(args.out)
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(rom)
    asar(out)
    rom = bytearray(out.read_bytes())
    write_font(rom)

    pk = Packer(rom, DATA_FIRST_BANK)
    stats = {}

    # event scripts
    evs = load("events")
    placed = {}
    n_en = n_all = 0
    for s in evs:
        for m in s["msgs"]:
            n_all += 1
            t = text_of(m, "event")
            m["_en"] = layout.wrap_event(t) if t else ""
            n_en += bool(t)
        blob = events.rebuild_script(orig, s, en, field="_en")
        placed[s["off"]] = pk.put(blob)
    for s in evs:
        p, b = placed[s["off"]]
        for sid in s["ids"]:
            i = int(sid, 16)
            rom[SCRIPT_TAB + 3 * i:SCRIPT_TAB + 3 * i + 3] = bytes([p & 0xFF, p >> 8, b])
    stats["events"] = (n_en, n_all)

    # menu messages
    menu = load("menu")
    for i, e in enumerate(menu):
        t = text_of(e, "menu")
        e2 = dict(e, en=layout.wrap_menu(t) if t else "")
        blob = menutext.encode_entry(orig, e2, en if t else jp)
        p, b = pk.put(blob)
        rom[MSG_TAB + 3 * i:MSG_TAB + 3 * i + 3] = bytes([p & 0xFF, p >> 8, b])

    # battle messages
    bt_en = btltext.table(ROOT / "tbl" / "en.tbl")
    bat = load("battle")
    cache = {}
    for i, e in enumerate(bat):
        t = text_of(e, "battle")
        key = (e["off"], t)
        if key not in cache:
            if t:
                blob = bt_en.encode(layout.wrap_battle(t)) + b"\x00"
            else:
                o = int(e["off"], 16)
                blob = orig[o:o + btltext.strlen(orig, o)]
            cache[key] = pk.put(blob)
        p, b = cache[key]
        rom[BTL_TAB + 3 * i:BTL_TAB + 3 * i + 3] = bytes([p & 0xFF, p >> 8, b])

    # system strings (bank $01 printer): English elsewhere, original start -> far jump 01 lo hi bank
    sys_en = systext.table(ROOT / "tbl" / "en.tbl")
    for e in load("system"):
        t = text_of(e, "system")
        if not t:
            continue
        o, n = int(e["off"], 16), e["len"]
        blob = sys_en.encode(layout.wrap_system(t, e)) + b"\x00"
        if n < 4:
            if len(blob) > n:
                raise ValueError(f"{e['id']}: in-place string too long")
            rom[o:o + len(blob)] = blob
            continue
        p, b = pk.put(blob)
        rom[o:o + 4] = bytes([0x01, p & 0xFF, p >> 8, b])

    # names (in place)
    for e in load("names"):
        t = text_of(e, "name")
        if args.marker and e["id"] not in qa:
            t = e["id"]
        if t:
            o = int(e["off"], 16)
            rom[o:o + 8] = names.encode(dict(e, en=t), en)

    out.write_bytes(rom)
    print(f"built {out} ({len(rom)} bytes), data {pk.used():#x} bytes from bank ${DATA_FIRST_BANK:02X}, "
          f"events {stats['events'][0]}/{stats['events'][1]} translated, sha1 {hashlib.sha1(rom).hexdigest()[:12]}")


def identity(out):
    """Re-insert every system's Japanese in place; must reproduce the original."""
    orig = script.ORIG.read_bytes()
    rom = bytearray(orig)
    for s in load("events"):
        a, b = int(s["off"], 16), int(s["end"], 16)
        rom[a:b] = events.rebuild_script(orig, s, events.JP, field="jp")
    for e in load("menu"):
        o = int(e["off"], 16)
        blob = menutext.encode_entry(orig, dict(e, en=e["jp"]), events.JP)
        rom[o:o + len(blob)] = blob
    t = btltext.table(ROOT / "tbl" / "jp.tbl")
    for e in load("battle"):
        o = int(e["off"], 16)
        blob = t.encode(e["jp"]) + b"\x00"
        rom[o:o + len(blob)] = blob
    for e in load("names"):
        o = int(e["off"], 16)
        rom[o:o + 8] = names.encode(e, events.JP, field="jp")
    st = systext.table(ROOT / "tbl" / "jp.tbl")
    for e in load("system"):
        o = int(e["off"], 16)
        blob = st.encode(e["jp"]) + b"\x00"
        rom[o:o + len(blob)] = blob
    Path(out).write_bytes(rom)
    return bytes(rom) == orig


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--marker", action="store_true")
    ap.add_argument("--identity")
    ap.add_argument("--qa", action="append", default=[])
    ap.add_argument("--out", default=str(ROOT / "build" / "hanjuku_en.sfc"))
    a = ap.parse_args()
    if a.identity:
        ok = identity(a.identity)
        print("identity:", "identical" if ok else "DIFFERENT")
        return 0 if ok else 1
    build(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
