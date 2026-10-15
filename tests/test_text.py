import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import btltext  # noqa: E402
import events  # noqa: E402
import menutext  # noqa: E402
import names  # noqa: E402
import script  # noqa: E402

ROM = script.ORIG.read_bytes()


def load(name):
    return json.loads((ROOT / "script" / f"{name}.json").read_text(encoding="utf-8"))


def test_battle_roundtrip():
    t = btltext.table(ROOT / "tbl" / "jp.tbl")
    for e in load("battle"):
        o = int(e["off"], 16)
        n = btltext.strlen(ROM, o)
        assert t.encode(e["jp"]) + b"\x00" == ROM[o:o + n], e["id"]


def test_menu_roundtrip():
    for e in load("menu"):
        o = int(e["off"], 16)
        b = menutext.encode_entry(ROM, dict(e, en=e["jp"]), events.JP)
        assert b == ROM[o:o + len(b)], e["id"]


def test_names_roundtrip():
    for e in load("names"):
        o = int(e["off"], 16)
        assert names.encode(e, events.JP, field="jp") == ROM[o:o + 8], e["id"]
