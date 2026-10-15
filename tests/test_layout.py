import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import layout  # noqa: E402


def test_wrap_basic():
    assert layout.wrap("aaa bbb ccc", 7) == "aaa bbb{n}ccc"
    assert layout.wrap("  centred", 20) == "  centred"


def test_autowrap_drops_break_after_full_line():
    t = "x" * 26 + " next"
    assert layout.wrap(t, 26, autowrap=True) == "x" * 26 + "next"
    assert layout.wrap(t, 26) == "x" * 26 + "{n}next"


def test_trailing_space_not_counted():
    t = "y" * 25 + " longs"
    assert layout.wrap(t, 26, autowrap=True) == "y" * 25 + "{n}longs"


def test_tokens_kept():
    assert layout.wrap("Hi {hero}, go{w}{p}Next page", 26) == "Hi {hero}, go{w}{p}Next page"
