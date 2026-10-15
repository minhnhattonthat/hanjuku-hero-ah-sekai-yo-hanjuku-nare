"""Raw tile text patched in place (window templates, name-entry grid, labels). Each entry: (file offset, length,
English). English is encoded with tbl/en.tbl and padded with spaces (FF) to the original length.
Dakuten rows of templates (the row above a label) become all spaces.
"""

# fmt: off
ENTRIES = [
    # date/gold bar template ($1F:B441, 18 tiles): year digits end col 2, month col 7, gold cols 11-15
    (0xFB441, 18, "   yr   mo.     G "),
    # castle monthly-command menu template ($1F:B53C), 20 tiles per row, cursor at col 0 and col 10
    (0xFB53C, 20, ""),
    (0xFB55C, 20, " Merchant  Recruit"),
    (0xFB57C, 20, ""),
    (0xFB59C, 20, " Troops    Dismiss"),
    (0xFB5BC, 20, ""),
    (0xFB5DC, 20, " Fortify   Bless Egg"),
    (0xFB61C, 20, " Main Menu All done!"),
    # general status mini window ($1F:B48D), 10 tiles per row; numbers are drawn by code
    (0xFB499, 10, ""),
    (0xFB4A5, 10, " Egg"),
    (0xFB4B1, 10, " War     §"),
    (0xFB4BD, 10, " Rule    §"),
    (0xFB4C9, 10, " Pay     §"),
    # name entry: mode labels ($04:FF9D, 4 x 4) and prompt ($04:FFAE, 18)
    (0x27F9D, 4, "ABC"),
    (0x27FA1, 4, "abc"),
    (0x27FA5, 4, "123"),
    (0x27FA9, 4, "Done"),
    (0x27FAE, 19, "Write your own name"),  # 19 tiles, then the 0x10 terminator
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
