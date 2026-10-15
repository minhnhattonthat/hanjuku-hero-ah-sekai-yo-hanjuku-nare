import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import events  # noqa: E402
import script  # noqa: E402

ROM = script.ORIG.read_bytes()
DATA = json.loads((ROOT / "script" / "events.json").read_text(encoding="utf-8"))


def test_scripts_identity():
    """Re-serializing every script with no English gives the original bytes (and via jp text too)."""
    for s in DATA:
        off, end = int(s["off"], 16), int(s["end"], 16)
        assert events.rebuild_script(ROM, s, events.JP, field="none") == ROM[off:end], s["off"]
        assert events.rebuild_script(ROM, s, events.JP, field="jp") == ROM[off:end], s["off"]


def test_coverage():
    """Script regions tile each bank's script area without gaps."""
    by = {}
    for s in DATA:
        by.setdefault(s["bank"], []).append((int(s["off"], 16), int(s["end"], 16)))
    for bank, spans in by.items():
        spans.sort()
        for (a, b), (c, d) in zip(spans, spans[1:]):
            assert b == c, (bank, hex(b), hex(c))
