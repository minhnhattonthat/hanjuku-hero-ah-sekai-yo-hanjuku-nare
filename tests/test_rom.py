import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIG = ROOT / "rom" / "Hanjuku Hero - Ah, Sekai yo Hanjuku Nare...!! (Japan).sfc"


def test_base_rom_hash():
    assert hashlib.sha1(ORIG.read_bytes()).hexdigest() == "4edad4a8a8e3ab6117171c48ce2a332757ed3e2f"
