"""Dump every text system from the ORIGINAL ROM to script/*.json. Never overwrites existing files (no --force).

    python -X utf8 tools/dump.py [--only events,menu,battle,names]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import btltext  # noqa: E402
import events  # noqa: E402
import menutext  # noqa: E402
import names  # noqa: E402
import script  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main():
    rom = script.ORIG.read_bytes()
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    jobs = {
        "events": lambda: events.dump(rom),
        "menu": lambda: menutext.dump(rom),
        "battle": lambda: btltext.dump(rom),
        "names": lambda: names.dump(rom, events.JP),
    }
    for name, fn in jobs.items():
        if only and name not in only:
            continue
        dst = ROOT / "script" / f"{name}.json"
        if dst.exists():
            print(f"skip {dst.name} (exists)")
            continue
        data = fn()
        dst.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
        print(f"wrote {dst.name}: {len(data)} entries")


if __name__ == "__main__":
    main()
