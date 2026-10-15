"""Warp tour: boot ROM cold, replace the first event script by each id, mash A, shoot, one sheet per id.

    python -X utf8 tools/debug/tour.py [ROM] [--ids 00,34,D3 | --all] [--jobs 4] [--frames 3600] [--out work/qa/tour]
Writes OUT/<id>/sheet.png (changed frames only). Exit 1 if any run failed (emulator error / smoke).
"""
import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = Path(r"H:\translation\batch\.claude\skills\translate-retro-game\scripts")


def run(rom, sid, out, frames, every, mash):
    d = out / f"{sid:02X}"
    cmd = [sys.executable, "-X", "utf8", str(SKILL / "emu.py"), str(rom), "--out", str(d), "--route",
           str(ROOT / "tools/routes/boot.txt"), "--script", str(ROOT / "tools/debug/warp.lua"), "--var",
           f"SCENE=0x{sid:02X}", "--frames", str(frames), "--mash", str(mash), "--shot-every", str(every),
           "--timeout", "600"]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    s = subprocess.run([sys.executable, "-X", "utf8", str(SKILL / "sheet.py"), str(d), "--changed", "0.01",
                        "--from", "900", "--div", "2"], capture_output=True, text=True, cwd=ROOT)
    return sid, r.returncode, (r.stdout + r.stderr)[-300:] if r.returncode else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom", nargs="?", default=str(ROOT / "build" / "hanjuku_en.sfc"))
    ap.add_argument("--ids", default="")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--frames", type=int, default=3600)
    ap.add_argument("--every", type=int, default=45)
    ap.add_argument("--mash", type=int, default=50)
    ap.add_argument("--out", default=str(ROOT / "work" / "qa" / "tour"))
    a = ap.parse_args()
    ids = list(range(256)) if a.all else [int(x, 16) for x in a.ids.split(",") if x]
    out = Path(a.out)
    bad = 0
    with ThreadPoolExecutor(a.jobs) as ex:
        for sid, rc, msg in ex.map(lambda i: run(a.rom, i, out, a.frames, a.every, a.mash), ids):
            if rc:
                bad += 1
                print(f"{sid:02X} rc={rc} {msg}")
    print(f"{len(ids)} runs, {bad} failed; sheets in {out}/<id>/sheet.png")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
