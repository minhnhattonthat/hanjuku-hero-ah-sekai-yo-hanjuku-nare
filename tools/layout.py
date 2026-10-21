"""Line wrapping for English text (fixed 8 px font: 1 char = 1 tile). Budgets measured in-game: docs/re/windows.md.

Translators write running text; {n} forces a break, {w}{p} ends a page. wrap() inserts {n} at spaces.
Event and menu windows auto-wrap at 26 columns themselves, so a full 26-char line followed by {n} would leave a
blank line: for those (autowrap=True) the {n} after a full line is dropped.
"""
import re

TOKEN = re.compile(r"(\{[^}]*\})")
EVENT_W, EVENT_LINES = 26, 4   # dialogue window: 26 cols, 4 visible lines (scrolls), engine auto-wrap at 26
MENU_W, MENU_LINES = 26, 2     # castle-menu message box (VM text): 26 cols, 2 lines, auto-wrap
SYSTEM_W, SYSTEM_LINES = 27, 2  # bank-01 printer message box: 27 cols, no auto-wrap
BATTLE_W, BATTLE_LINES = 26, 3  # battle bubble/box (to confirm in QA)
NAME_W = 8  # {hero}, {nameX}, {str:XX}, {vNN} expand to up to 8 chars
PAGE_BREAKS = ("{p}", "{1B}")


def token_width(t):
    if t.startswith(("{name", "{hero", "{str:")):
        return NAME_W
    if t.startswith("{v0") and t[3] in "1234567":
        return NAME_W  # battle inserts 01-07 (names); 0B-0F are effect/pause codes ($03:CEF4..)
    return 0


def wrap(text, width, autowrap=False, wide=()):
    """wide: extra tokens that print a name (e.g. {#3} when that command is 36)."""
    if not width:
        return text
    out, col, var = [], 0, False   # var: current line holds a variable-width token
    soft = False  # last break was inserted by the wrapper: drop the spaces that follow it

    def newline(auto):
        nonlocal col, var, soft
        while out and out[-1] == " ":
            out.pop()
            col -= 1
        if not (autowrap and col == width and not var):
            out.append("{n}")
        col, var, soft = 0, False, auto

    parts = [p for p in TOKEN.split(text) if p]

    def zero(t):  # a code that prints nothing and doesn't break the line (effects between letters, waits)
        return t != "{n}" and t not in PAGE_BREAKS and not (NAME_W if t in wide else token_width(t))

    def glued_len(k):  # letters that continue the current word after parts[k-1], across zero-width codes
        n = 0
        for q in parts[k:]:
            if q.startswith("{"):
                if not zero(q):
                    break
                continue
            m = re.match(r"[^ ]*", q).group(0)
            n += len(m)
            if len(m) < len(q):
                break
        return n

    glued = False  # inside a word that a zero-width code split ("H{#37}a{#38}r..."): never break here
    for k, p in enumerate(parts):
        if p.startswith("{"):
            if p == "{n}":
                newline(False)
                glued = False
                continue
            w = NAME_W if p in wide else token_width(p)
            if w and col + w > width and col > 0:
                newline(True)
            out.append(p)
            if p in PAGE_BREAKS:
                col, var = 0, False
            if w:
                var = True
                col += w
            if not zero(p):
                glued = False
            continue
        words = [w for w in re.split(r"( )", p) if w]
        for i, w in enumerate(words):
            if w == " ":
                glued = False
                if col == 0 and soft:
                    continue
                if col + 1 > width:
                    newline(True)
                    continue
                out.append(" ")
                col += 1
                continue
            n = len(w) + (glued_len(k + 1) if i == len(words) - 1 else 0)
            if not (i == 0 and glued) and col + n > width and col > 0:
                newline(True)
            out.append(w)
            col += len(w)
            soft = False
        glued = not p.endswith(" ")
    return "".join(out)


def name_tokens(codes):
    """{#k} tokens whose command prints a general's name (command 36, $04:9D13)."""
    return {"{#%d}" % k for k, c in enumerate(codes) if c[:2] == "36"}


CHOICE_W = {"19": 18, "33": 15}  # a yes/no (19) or 3-way (33) box covers the right of the window


def page_widths(text, codes=(), choice_after=None):
    """Width per {p}-page: narrower on the page that shows a choice box."""
    pages = text.split("{p}")
    ws = [EVENT_W] * len(pages)
    for i, pg in enumerate(pages):
        for k, c in enumerate(codes):
            if c[:2] in CHOICE_W and "{#%d}" % k in pg:
                ws[i] = CHOICE_W[c[:2]]
    if choice_after in CHOICE_W:
        ws[-1] = CHOICE_W[choice_after]
    return pages, ws


PFX = "{PFX}"  # stands for a speaker name printed by a command just before the message (wrap-time only)


def speakers(text, codes=(), name_before=False):
    """The game prints a speaker's name with command 36 right before 「. English: add ": " after that name."""
    for t in name_tokens(codes):
        text = re.sub(re.escape(t) + r"(?=[A-Za-z0-9\"'(.])", t + ": ", text)
    if name_before and text[:1] not in (" ", ":", ",", ".", "!", "?", "'", "{"):
        text = PFX + ": " + text
    elif name_before and text.startswith("{") and not text.startswith((" ", ":")):
        text = PFX + ": " + text
    return text


def wrap_event(text, codes=(), choice_after=None, name_before=False):
    text = speakers(text, codes, name_before)
    pages, ws = page_widths(text, codes, choice_after)
    wide = name_tokens(codes) | {PFX}
    out = "{p}".join(wrap(pg, w, autowrap=(w == EVENT_W), wide=wide) for pg, w in zip(pages, ws))
    return out.replace(PFX, "")


def wrap_menu(text):
    return wrap(text, MENU_W, autowrap=True)


BUBBLE_W = 22  # battle speech bubble: one line at a time, ~23 cols visible (tutorial B018 measured)


def wrap_battle(text, jp=""):
    """Quips (one JP line ending in a wait) show in the 1-line speech bubble: wrap them to the bubble and make each
    break a wait + new bubble line, as the JP tutorial (B018) does."""
    if "{wait:" in jp and "{n}" not in jp:
        w = wrap(text, BUBBLE_W)
        return re.sub(r"(?<!\{wait:[0-9A-F]{2}\})\{n\}", "{wait:10}{n}", w)
    return wrap(text, BATTLE_W)


def wrap_system(text, entry=None):
    return wrap(text, SYSTEM_W)
