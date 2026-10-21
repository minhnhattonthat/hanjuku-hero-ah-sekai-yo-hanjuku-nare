"""Find text hardcoded in code as runs of LDA #tile / STA abs,x (a9 tt 9d lo hi), e.g. the battle command labels
at $03:D5CC. Prints each run with its tiles decoded through tbl/jp.tbl (dakuten tile C4/C5 shown as ゛/゜).

    python -X utf8 tools/immtext.py [ROM] [--min 3]
"""
import argparse
import re
import sys

sys.path.insert(0, __file__.rsplit("tools", 1)[0] + "tools")


def load_tbl(path):
    t = {}
    for line in open(path, encoding="utf8"):
        k, _, v = line.rstrip("\n").partition("=")
        if v and len(k) == 2:
            t[int(k, 16)] = v
    t[0xC4], t[0xC5] = "゛", "゜"
    return t


def runs(rom, min_len):
    # one store: LDA #imm (a9 tt) then STA abs,x (9d lo hi) [repeated], or STA long,x / JSR putchar + INX
    store = re.compile(rb"\xa9(.)((?:\x9d..)+|\x9f...\xe8?|\x20..\xe8?)", re.S)
    pos, cur = 0, []
    for m in store.finditer(rom):
        if cur and m.start() != pos:
            if len(cur) >= min_len:
                yield cur
            cur = []
        g = m.group(2)
        if g[0] == 0x9D:
            offs = [int.from_bytes(g[i + 1:i + 3], "little") for i in range(0, len(g), 3)]
        else:
            offs = [len(cur)]  # sequential writer: order = position
        cur.append((m.start(), m.group(1)[0], offs))
        pos = m.end()
    if len(cur) >= min_len:
        yield cur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom", nargs="?", default="rom/hh.sfc")
    ap.add_argument("--min", type=int, default=3)
    a = ap.parse_args()
    rom = open(a.rom, "rb").read()
    jp = load_tbl("tbl/jp.tbl")
    for run in runs(rom, a.min):
        chars = [(o, v) for _, v, offs in run for o in offs if 0x40 <= v <= 0xC5]
        if len(chars) < a.min:
            continue
        off = run[0][0]
        cpu = ((off >> 15) << 16) | (off & 0x7FFF) | 0x8000
        text = "".join(jp.get(v, "?") for o, v in sorted(chars))
        print(f"{off:06X} ${cpu >> 16:02X}:{cpu & 0xFFFF:04X} {len(chars):2d} {text}")


if __name__ == "__main__":
    main()
