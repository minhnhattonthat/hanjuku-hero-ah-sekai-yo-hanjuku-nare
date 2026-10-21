"""Raw tile text patched in place (window templates, name-entry grid, labels). Each entry: (file offset, length,
English). English is encoded with tbl/en.tbl and padded with spaces (FF) to the original length.
Dakuten rows of templates (the row above a label) become all spaces.
"""

# fmt: off
ENTRIES = [
    # date/gold bar template ($1F:B441, 18 tiles): year digits end col 2, month col 7, gold cols 11-15
    (0xFB441, 18, "   yr   mo.     G "),
    # castle monthly-command menu template ($1F:B53C), 20 tiles per row, cursors at cols 0 and 8-9: left labels max 7
    (0xFB53C, 20, ""),
    (0xFB55C, 20, " Shop      Recruit"),
    (0xFB57C, 20, ""),
    (0xFB59C, 20, " Troops    Dismiss"),
    (0xFB5BC, 20, ""),
    (0xFB5DC, 20, " Fortify   Bless Egg"),
    (0xFB61C, 20, " Menu      All done!"),
    # general status mini window ($1F:B48D), 10 tiles per row; numbers are drawn by code
    (0xFB499, 10, ""),
    (0xFB4A5, 10, " Egg"),
    (0xFB4B1, 10, " War     §"),
    (0xFB4BD, 10, " Rule    §"),
    (0xFB4C9, 10, " Pay     §"),
    # yes/no box labels ($04:FC35 4 tiles, $04:FC3A 5 tiles; the command table follows at $04:FC3F)
    (0x27C35, 4, "Yes!"),
    (0x27C3A, 5, "No!"),
    # name entry: mode labels ($04:FF9D, 4 x 4) and prompt ($04:FFAE, 18)
    (0x27F9D, 4, "ABC"),
    (0x27FA1, 4, "abc"),
    (0x27FA5, 4, "123"),
    (0x27FA9, 4, "Done"),
    (0x27FAE, 19, "Write your own name"),  # 19 tiles, then the 0x10 terminator
    # recruit audition stat block ($1F:ED76/ED89/ED9D, printed by $04:C1BC): digits drawn over the 0s by code,
    # the egg yes/no from col 17 (LABELS 8/9)
    (0xFED76, 19, " HP    00P Egg"),
    (0xFED89, 20, " War   00P Rule  00P"),
    (0xFED9D, 10, " Pay   00G"),
]

# labels the game wrote with LDA #tile / STA code (tools/immtext.py), now read from $20:9E00 (asm Labels), 16 bytes
# each, 00-terminated. Battle command windows hold 8 tiles.
LABELS_OFF = 0x101E00
LABELS = [
    "Attack",    # 0 こうげき
    "Assault",   # 1 もうこうげき
    "Use Egg",   # 2 たまごをつかう
    "Trump",     # 3 きりふだ
    "Retreat",   # 4 たいきゃく
    "Return",    # 5 たまごにもどれ (egg monster back into its egg)
    "Secret",    # 6 おくのて
    "troops",    # 7 へいし (battle message insert)
    "Yes",       # 8 あり (has an egg)
    "No ",       # 9 なし (same width as 8: the Dismiss panel redraws over the previous general's value)
]
# fmt: on

# name-entry grids ($1F:B100 page 1, $1F:B150 page 2, $1F:B1A0 page 3): groups of 5 cells; groups 0-7 = left
# block rows 1-8, groups 8-15 = right block rows 1-8.
_U = ["ABCDE", "FGHIJ", "KLMNO", "PQRST", "UVWXY", "Z.,'-", "!?&()", ":;/+%",
      "abcde", "fghij", "klmno", "pqrst", "uvwxy", "z\"~*#", "=<>é ", "♪♥   "]
_L = ["abcde", "fghij", "klmno", "pqrst", "uvwxy", "z.,'-", "!?&()", ":;/+%",
      "ABCDE", "FGHIJ", "KLMNO", "PQRST", "UVWXY", "Z\"~*#", "=<>é ", "♪♥   "]
_D = ["01234", "56789", ".,'-!", "?&()/", ":;+%*", "#=<>\"", "~♪♥é ", "     "]
GRIDS = [(0xFB100, "".join(_U)), (0xFB150, "".join(_L)), (0xFB1A0, "".join(_D))]


# password pieces ($1F:B24D, 10 x 8 bytes, 00-padded), shown on the Ovarium password screen; the event texts
# that hand them out (scripts 9B-A4) must use the same words.
PASSWORD = ["Our", "Hardened", "Beings'", "Great", "Mother", "Egg Mama", "Palace", "Ovarium!", "Show me", "the way"]


def apply(rom, table):
    for i, w in enumerate(PASSWORD):
        b = table.encode(w)
        assert len(b) <= 8, w
        rom[0xFB24D + 8 * i:0xFB24D + 8 * i + 8] = b + b"\x00" * (8 - len(b))
    for off, n, en in ENTRIES:
        en = en.replace("§", "")
        b = table.encode(en) if en else b""
        if len(b) > n:
            raise ValueError(f"rawtext {off:#x}: {en!r} > {n}")
        rom[off:off + n] = b + b"\xFF" * (n - len(b))
    for off, cells in GRIDS:
        b = table.encode(cells)
        rom[off:off + len(b)] = b
    for i, w in enumerate(LABELS):
        b = table.encode(w)
        assert len(b) <= 8, w
        o = LABELS_OFF + 16 * i
        rom[o:o + 16] = b + b"\x00" * (16 - len(b))
