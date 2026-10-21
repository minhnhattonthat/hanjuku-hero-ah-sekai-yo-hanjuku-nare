import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import cards  # noqa: E402


def test_blob_entries_point_at_their_glyphs():
    b = cards.blob()
    end = 4 * 24
    for i in range(24):
        ptr, n = int.from_bytes(b[4 * i:4 * i + 2], "little") - 0x8000, b[4 * i + 2]
        assert ptr == end and 1 <= n <= (16 if i < 12 else 4)
        end += 64 * n
    assert end == len(b)


def test_strip_centres_ink_with_outline():
    px, n = cards.strip("I")
    assert n == 1
    ink = [x for r in px for x, v in enumerate(r) if v == 3]
    assert ink and all(v in (0, 1, 3) for r in px for v in r)
    assert px[3][min(ink)] == 1  # outline above the ink
