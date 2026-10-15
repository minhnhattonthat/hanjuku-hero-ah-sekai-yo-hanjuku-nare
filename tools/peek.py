"""Decode a ROM range with tbl/jp.tbl for recon: python -X utf8 tools/peek.py START END [ROM]. Control bytes print as [XX]."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tbl import Table  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
rom = Path(sys.argv[3] if len(sys.argv) > 3 else ROOT / "rom" / "hh.sfc").read_bytes()
t = Table.load(ROOT / "tbl" / "jp.tbl")
s, e = int(sys.argv[1], 16), int(sys.argv[2], 16)
for a in range(s, e, 64):
    print(f"{a:06x} {t.decode(rom, a, min(64, e - a))[0]}")
