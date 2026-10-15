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
        if not (autowrap and col == width and not var):
            out.append("{n}")
        col, var, soft = 0, False, auto

    for p in TOKEN.split(text):
        if not p:
            continue
        if p.startswith("{"):
            if p == "{n}":
                newline(False)
                continue
            w = NAME_W if p in wide else token_width(p)
            if w and col + w > width and col > 0:
                if out and out[-1] == " ":
                    out.pop()
                newline(True)
            out.append(p)
            if p in PAGE_BREAKS:
                col, var = 0, False
            if w:
                var = True
                col += w
            continue
        for w in re.split(r"( )", p):
            if not w:
                continue
            if w == " ":
                if col == 0 and soft:
                    continue
                if col + 1 > width:
                    newline(True)
                    continue
                out.append(" ")
                col += 1
                continue
            if col + len(w) > width and col > 0:
                newline(True)
            out.append(w)
            col += len(w)
            soft = False
    return "".join(out)


def name_tokens(codes):
    """{#k} tokens whose command prints a general's name (command 36, $04:9D13)."""
    return {"{#%d}" % k for k, c in enumerate(codes) if c[:2] == "36"}


def wrap_event(text, codes=()):
    return wrap(text, EVENT_W, autowrap=True, wide=name_tokens(codes))


def wrap_menu(text):
    return wrap(text, MENU_W, autowrap=True)


def wrap_battle(text):
    return wrap(text, BATTLE_W)


def wrap_system(text, entry=None):
    return wrap(text, SYSTEM_W)
