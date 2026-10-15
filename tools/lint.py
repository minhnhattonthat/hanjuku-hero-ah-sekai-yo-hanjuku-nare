"""Text lint over script/*.json (the hard gate): every entry translated, encodable, tokens match the JP,
wrapped width/lines within the measured budget. Prints errors + a count; exit 1 on errors.
Known, reviewed exceptions: script/lint_allow.txt (one id per line, with a reason).
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import batches  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
JPRE = re.compile(r"[぀-ヿ一-鿿！-～]")


def main():
    allow = set()
    p = ROOT / "script" / "lint_allow.txt"
    if p.exists():
        allow = {ln.split()[0] for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")}
    errs, n = [], 0
    for f, e, form, lim in batches.units():
        n += 1
        en = e.get("en") or ""
        if e["id"] in allow:
            continue
        if not en:
            errs.append(f"{e['id']}: untranslated")
            continue
        if JPRE.search(en):
            errs.append(f"{e['id']}: Japanese left in English")
        for msg in batches.check_entry(form, lim, e["jp"], en, e.get("codes", ()), e.get("choice_after"),
                                         e.get("name_before")):
            errs.append(f"{e['id']}: {msg}")
    for x in errs[:60]:
        print(x)
    print(f"lint: {n} entries, {len(errs)} errors")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
