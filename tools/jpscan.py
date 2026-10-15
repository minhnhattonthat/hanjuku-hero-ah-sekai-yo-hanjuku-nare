"""Static scan for Japanese-looking text runs in the ROM, minus regions covered by script/*.json.

    python -X utf8 tools/jpscan.py [ROM] [--min 4]
A run = maximal span of kana/space/punct codes; reported when it has >= MIN kana and common particles.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tbl import Table  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
KANA = set(range(0x40, 0xA7)) | set(range(0xC4, 0xF7)) | {0xA9, 0xAB, 0xAE}
OK = KANA | {0xFF, 0xA7, 0xA8, 0xAA, 0xAC, 0xAD, 0xAF, 0xB0, 0x3C, 0x3D, 0x3E, 0x3F} | set(range(0xBA, 0xC4))
COMMON = {0x7B, 0x9B, 0x41, 0x75, 0xCF, 0x65, 0x5F, 0x8B, 0x5D, 0x73, 0x6D, 0x69, 0x51, 0x79, 0xA5}


def covered():
    spans = []
    for name in ("events",):
        for s in json.loads((ROOT / "script" / f"{name}.json").read_text(encoding="utf-8")):
            spans.append((int(s["off"], 16), int(s["end"], 16)))
    spans.append((0xB8000, 0xBFE90))  # names + battle text
    spans.append((0xC5E00, 0xC61A8))  # castles
    spans.append((0xFB6F3, 0xC0000 + 0x3C000))  # menu messages (bank 1F b6f3-bfff)
    for extra in json.loads((ROOT / "script" / "_covered.json").read_text()) if (ROOT / "script" / "_covered.json").exists() else []:
        spans.append((int(extra[0], 16), int(extra[1], 16)))
    return spans


def main():
    rom = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else ROOT / "rom" / "hh.sfc").read_bytes()
    mn = int(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 4
    t = Table.load(ROOT / "tbl" / "jp.tbl")
    cov = covered()
    i, n = 0, len(rom)
    hits = []
    while i < n:
        if rom[i] in KANA:
            j = i
            while j < n and rom[j] in OK:
                j += 1
            seg = rom[i:j]
            k = sum(b in KANA for b in seg)
            c = sum(b in COMMON for b in seg)
            if k >= mn and c >= 2 and c / max(k, 1) > 0.15 and not any(a <= i < b for a, b in cov):
                hits.append((i, j))
            i = j + 1
        else:
            i += 1
    for a, b in hits:
        print(f"{a:06X}-{b:06X} {t.decode(rom, a, b - a)[0][:70]}")
    print(len(hits), "runs")


if __name__ == "__main__":
    main()
