"""Translation batches: split / check / merge / pairs / status.

    python -X utf8 tools/batches.py split            -> work/tl/<batch>.tsv (+ build/terms_<batch>.txt), list in work/tl/batches.json
    python -X utf8 tools/batches.py check <batch>    -> validates work/tl/<batch>.out.tsv (exit 1 on errors)
    python -X utf8 tools/batches.py merge <batch>..  -> writes English into script/*.json (refuses failing batches)
    python -X utf8 tools/batches.py pairs <batch>    -> work/tl/<batch>.pairs.txt for the reviewer
    python -X utf8 tools/batches.py status
Input TSV: id<TAB>form<TAB>limit<TAB>jp. Output TSV: id<TAB>english.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import layout  # noqa: E402
from tbl import Table  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / "work" / "tl"
EN = Table.load(ROOT / "tbl" / "en.tbl")
TOK = re.compile(r"\{[^}]*\}")
FILES = ["events", "menu", "system", "battle", "names"]
MANUAL_SYSTEM = set()  # filled from script/system_manual.txt (label/template entries done by hand)
TARGET = 3600  # JP chars per batch


def load(name):
    return json.loads((ROOT / "script" / f"{name}.json").read_text(encoding="utf-8"))


def save(name, data):
    (ROOT / "script" / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8", newline="\n")


def jlen(s):
    return len(TOK.sub("", s))


def manual_system():
    p = ROOT / "script" / "system_manual.txt"
    return set(p.read_text().split()) if p.exists() else set()


def units():
    """Yield (file, entry, form, limit) in story/table order for every translatable entry."""
    for s in load("events"):
        for m in s["msgs"]:
            crawl = "D3" in s["ids"]  # opening crawl (cmd 1D): centred lines, no page breaks
            yield "events", m, "crawl" if crawl else "dlg", "26x40" if crawl else "26x4"
    for e in load("menu"):
        if "same_as" not in e:
            yield "menu", e, "menu", "26x2"
    man = manual_system()
    for e in load("system"):
        if e["jp"] and e["id"] not in man:
            yield "system", e, "sys", "27x2"
    for e in load("battle"):
        if "same_as" not in e and e["jp"]:
            yield "battle", e, "battle", "26x3"
    for e in load("names"):
        if e["jp"]:
            yield "names", e, "name", "8"


def split():
    TL.mkdir(parents=True, exist_ok=True)
    batches, cur, size, kind = [], [], 0, None
    for f, e, form, lim in units():
        if e.get("en"):
            continue
        n = jlen(e["jp"])
        if cur and (size + n > TARGET or f != kind or len(cur) >= 260):
            batches.append((kind, cur))
            cur, size = [], 0
        cur.append((e["id"], form, lim, e["jp"]))
        size += n
        kind = f
    if cur:
        batches.append((kind, cur))
    gl = glossary_rows()
    index = {}
    for i, (kind, rows) in enumerate(batches):
        name = f"b{i:02d}_{kind}"
        index[name] = [r[0] for r in rows]
        (TL / f"{name}.tsv").write_text("".join(f"{a}\t{b}\t{c}\t{d}\n" for a, b, c, d in rows), encoding="utf-8",
                                        newline="\n")
        jp_all = "".join(r[3] for r in rows)
        terms = [r for r in gl if r[0] and r[0] in jp_all]
        (ROOT / "build").mkdir(exist_ok=True)
        (ROOT / "build" / f"terms_{name}.txt").write_text(
            "".join(f"{a} = {b}\n" for a, b, *_ in terms), encoding="utf-8", newline="\n")
    (TL / "batches.json").write_text(json.dumps(index, indent=1), encoding="utf-8", newline="\n")
    print(f"{len(batches)} batches")


def glossary_rows():
    rows = []
    p = ROOT / "glossary.md"
    if not p.exists():
        return rows
    for ln in p.read_text(encoding="utf-8").splitlines():
        if ln.startswith("|") and not ln.startswith("|---") and not ln.startswith("| JP"):
            cells = [c.strip() for c in ln.strip("|").split("|")]
            if len(cells) >= 2 and cells[0]:
                rows.append(cells)
    return rows


def read_out(name):
    p = TL / f"{name}.out.tsv"
    out = {}
    dup = []
    for ln in p.read_text(encoding="utf-8-sig").splitlines():
        if not ln.strip():
            continue
        if "\t" not in ln:
            out.setdefault("__bad__", []).append(ln)
            continue
        k, v = ln.split("\t", 1)
        if k in out:
            dup.append(k)
        out[k] = v
    return out, dup


def seq_ok(jp, en):
    """Non-text token sequence: EN must equal JP after removing {n}; EN may add '{w}{p}' pairs."""
    a = [t for t in TOK.findall(jp) if t != "{n}"]
    b = [t for t in TOK.findall(en) if t != "{n}"]
    from functools import lru_cache

    @lru_cache(None)
    def go(i, j):
        if j == len(b):
            return i == len(a)
        if i < len(a) and a[i] == b[j] and go(i + 1, j + 1):
            return True
        return b[j] == "{w}" and j + 1 < len(b) and b[j + 1] == "{p}" and go(i, j + 2)
    return go(0, 0)


def pages(text):
    return re.split(r"\{p\}|\{1B\}", text)


def check_entry(form, lim, jp, en):
    errs = []
    if not en.strip():
        return ["empty"]
    try:
        EN.encode(TOK.sub("", en))
    except ValueError as ex:
        errs.append(str(ex)[:80])
    if form == "name":
        if len(en) > int(lim):
            errs.append(f"{len(en)} chars > {lim}")
        return errs
    if not seq_ok(jp, en):
        errs.append("control tokens differ from JP")
    w, lines = map(int, lim.split("x"))
    wrapped = layout.wrap(en, w)
    for pg in pages(wrapped):
        ls = pg.split("{n}")
        if len(ls) > lines:
            errs.append(f"page has {len(ls)} lines > {lines}: {pg[:40]!r}")
        for ln in ls:
            n = sum(layout.token_width(t) for t in TOK.findall(ln)) + len(TOK.sub("", ln))
            if n > w:
                errs.append(f"line {n} > {w}: {ln[:40]!r}")
    if re.search(r"\}(st|nd|rd|th)\b", en):
        errs.append("ordinal suffix after a variable")
    return errs


def check(name, quiet=False):
    rows = [ln.split("\t") for ln in (TL / f"{name}.tsv").read_text(encoding="utf-8").splitlines()]
    out, dup = read_out(name)
    errs = []
    if "__bad__" in out:
        errs.append(f"lines without a tab: {out.pop('__bad__')[:3]}")
    ids = [r[0] for r in rows]
    for k in dup:
        errs.append(f"{k}: duplicate")
    for k in out:
        if k not in ids:
            errs.append(f"{k}: not in batch")
    for i, form, lim, jp in rows:
        if i not in out:
            errs.append(f"{i}: missing")
            continue
        for e in check_entry(form, lim, jp, out[i]):
            errs.append(f"{i}: {e}")
    if not quiet:
        for e in errs:
            print(e)
        print("OK" if not errs else f"{len(errs)} errors")
    return errs


def merge(names):
    data = {f: load(f) for f in FILES}
    idx = {}
    for f, d in data.items():
        if f == "events":
            for s in d:
                for m in s["msgs"]:
                    idx[m["id"]] = m
        else:
            for e in d:
                idx[e["id"]] = e
    for name in names:
        if check(name, quiet=True):
            print(f"{name}: check fails; not merged")
            continue
        out, _ = read_out(name)
        for k, v in out.items():
            idx[k]["en"] = v
        print(f"{name}: merged {len(out)}")
    for f, d in data.items():
        save(f, d)


def pairs(name):
    rows = [ln.split("\t") for ln in (TL / f"{name}.tsv").read_text(encoding="utf-8").splitlines()]
    out, _ = read_out(name)
    lines = []
    for i, form, lim, jp in rows:
        lines.append(f">> {i} | {jp}\n   {out.get(i, '')}\n")
    (TL / f"{name}.pairs.txt").write_text("".join(lines), encoding="utf-8", newline="\n")
    print(TL / f"{name}.pairs.txt")


def status():
    idx = json.loads((TL / "batches.json").read_text())
    for name in idx:
        p = TL / f"{name}.out.tsv"
        st = "-" if not p.exists() else ("OK" if not check(name, quiet=True) else "ERR")
        print(name, len(idx[name]), st)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "split":
        split()
    elif cmd == "check":
        sys.exit(1 if check(sys.argv[2]) else 0)
    elif cmd == "merge":
        merge(sys.argv[2:])
    elif cmd == "pairs":
        pairs(sys.argv[2])
    elif cmd == "status":
        status()
