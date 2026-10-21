"""Build the gold HANJUKU HERO logo in the title's existing Mode 7 budget.

The $0A:8000 LZSS block supplies palette/map/packed pixels; $09:F288 expands
low then high nibbles into 226 chunky 8bpp tiles. See docs/re/graphics.md.
Only the title replacement in bank $3E is changed, never the shared source.

Preview: python -X utf8 tools/title_logo.py work/qa/logo-preview.png
"""
from pathlib import Path
from math import hypot

from font_tiny import TINY

TILES = 0x1F0000
MAP = 0x1F3C00  # $3E:BC00, after copyright tiles ($B880-$BBFF)
NT = 0xE2
LOGO_NT = 0xC1  # subtitle keeps tiles $C2-$E2 and its original map

RIBBON = "SOFTBOILED HERO"


def unpack(rom):
    """The game's $03:F977 LZSS, including its prefilled 4 KiB dictionary."""
    ring = bytearray(v for v in range(256) for _ in range(13))
    ring += bytes(range(256)) + bytes(range(255, -1, -1)) + bytes(128) + b" " * 110
    ring += bytes(4096 - len(ring))
    start = 0x50000
    size = int.from_bytes(rom[start + 4:start + 6], "little")
    pos, cursor, out = start + 8, 0xFEE, bytearray()
    while len(out) < size:
        flags = rom[pos]
        pos += 1
        for bit in range(8):
            if flags & (1 << bit):
                values = [rom[pos]]
                pos += 1
                source = None
            else:
                lo, hi = rom[pos:pos + 2]
                pos += 2
                source = lo | ((hi & 0xF0) << 4)
                values = range((hi & 15) + 3)
            for value in values:
                if source is not None:
                    value = ring[source]
                    source = (source + 1) & 0xFFF
                out.append(value)
                ring[cursor] = value
                cursor = (cursor + 1) & 0xFFF
                if len(out) == size:
                    return bytes(out)
    return bytes(out)


def render(tiles, tilemap):
    return [[tiles[(tilemap[(y // 8) * 32 + x // 8] - 1) * 64 + (y % 8) * 8 + x % 8]
             if tilemap[(y // 8) * 32 + x // 8] else 0 for x in range(256)] for y in range(88)]


def polygon(points):
    """Integer scanline fill; no antialiasing or extra palette colours."""
    result = set()
    for y in range(min(p[1] for p in points), max(p[1] for p in points) + 1):
        cuts = []
        for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1]):
            if min(y1, y2) <= y < max(y1, y2):
                cuts.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
        cuts.sort()
        for left, right in zip(cuts[::2], cuts[1::2]):
            result.update((x, y) for x in range(round(left), round(right) + 1))
    return result


def draw(px, points, color):
    for x, y in points:
        assert 0 <= x < 256 and 0 <= y < 88, (x, y)
        px[y][x] = color


def stroke(px, points, color=1):
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        n = max(abs(x2 - x1), abs(y2 - y1))
        draw(px, {(round(x1 + (x2 - x1) * i / n), round(y1 + (y2 - y1) * i / n))
                  for i in range(n + 1)}, color)


def ribbon(px):
    """Center lettering by distance along the front band, excluding its folded right tail."""
    centers = {}
    for x in range(84, 168):
        ys = [y for y in range(40) if px[y][x] in (9, 10)]
        if ys:
            top, bottom = min(ys), max(ys)
            centers[x] = (top + bottom) / 2
            for y in range(top, bottom + 1):
                if px[y][x] in (1, 10):
                    px[y][x] = 9
    # The usable front band is x84..160. Beyond x160 the rising folded tail
    # contaminates the centre estimate. Smooth out holes left by the old ink.
    path = [(x, sum(centers[xx] for xx in range(max(84, x - 2), min(160, x + 2) + 1))
             / len(range(max(84, x - 2), min(160, x + 2) + 1))) for x in range(84, 161)]
    distances = [0.0]
    for (x0, y0), (x1, y1) in zip(path, path[1:]):
        distances.append(distances[-1] + hypot(x1 - x0, y1 - y0))
    advance = 5
    start = (distances[-1] - (len(RIBBON) - 1) * advance) / 2
    for i, ch in enumerate(RIBBON):
        j = min(range(len(path)), key=lambda k: abs(distances[k] - start - i * advance))
        cx, cy = path[j]
        x0, top = cx - 1, round(cy - 3)
        for y, row in enumerate(TINY[ch][:7]):
            for x, on in enumerate(row):
                if on == "#":
                    assert px[top + y][x0 + x] == 9, (ch, x0 + x, top + y)
                    px[top + y][x0 + x] = 1


def stone(px, *, texture=True):
    """Hand-hewn positive letter strokes, packed with one/two-pixel seams.

    Open notches reach the silhouette: there is no yellow sign face or shared
    yellow foot. Only the mass's outer bottom/right edge carries salmon depth.
    """
    blocks = [
        [(35, 46), (41, 45), (40, 60), (44, 60), (44, 44), (49, 45),
         (49, 78), (44, 79), (44, 66), (39, 67), (39, 80), (33, 79)],  # H
        [(51, 80), (53, 49), (58, 46), (64, 48), (66, 80), (61, 79),
         (60, 68), (56, 68), (56, 80)],  # A
        [(68, 79), (68, 48), (73, 48), (80, 65), (79, 49), (84, 49),
         (84, 79), (79, 78), (73, 63), (74, 80)],  # N
        [(86, 50), (99, 49), (99, 73), (96, 80), (88, 80), (85, 75),
         (86, 68), (91, 68), (91, 74), (94, 74), (94, 56), (86, 56)],  # J
        [(101, 48), (106, 48), (106, 72), (109, 74), (111, 72),
         (111, 47), (116, 48), (116, 75), (112, 80), (104, 79), (101, 75)],  # U
        [(118, 46), (124, 45), (123, 59), (128, 48), (133, 47),
         (127, 63), (134, 79), (127, 79), (123, 68), (123, 80), (118, 79)],  # K
        [(135, 48), (141, 47), (140, 72), (143, 74), (145, 71),
         (145, 46), (150, 47), (150, 75), (146, 79), (138, 80), (135, 75)],  # U
        [(158, 45), (164, 44), (163, 59), (168, 59), (168, 44),
         (173, 45), (173, 79), (167, 80), (167, 66), (163, 66),
         (163, 79), (157, 78)],  # H
        [(175, 44), (189, 43), (188, 50), (181, 50), (180, 59),
         (188, 58), (188, 65), (181, 65), (181, 73), (189, 73),
         (190, 79), (175, 80)],  # E
        [(191, 44), (202, 43), (207, 48), (206, 60), (202, 64),
         (208, 79), (201, 79), (197, 68), (197, 80), (191, 79)],  # R
        [(209, 47), (213, 42), (219, 41), (222, 47), (223, 73),
         (220, 80), (212, 79), (209, 74)],  # O
    ]
    face = set().union(*(polygon(points) for points in blocks))
    for hole in ([(57, 53), (60, 53), (61, 62), (56, 62)],
                 [(197, 50), (201, 50), (201, 58), (197, 59)],
                 [(215, 49), (218, 48), (219, 71), (215, 73)]):
        face -= polygon(hole)
    # Small silhouette chips vary in position and depth; no uniform bevel.
    face -= {(35, 53), (35, 54), (49, 70), (54, 50), (68, 57),
             (84, 74), (99, 61), (102, 74), (118, 54), (119, 46),
             (136, 58), (150, 68), (158, 51), (173, 72), (176, 44),
             (189, 76), (192, 53), (207, 76), (222, 56), (223, 72)}
    face -= {(36, 78), (37, 78), (37, 79), (63, 78), (64, 79),
             (71, 78), (72, 79), (89, 79), (90, 79), (111, 78),
             (112, 79), (129, 78), (130, 78), (142, 79),
             (159, 77), (160, 78), (179, 79), (180, 79),
             (195, 78), (203, 78), (214, 78), (215, 78),
             (39, 45), (73, 49), (123, 46), (162, 45), (201, 44)}
    side = polygon([(33, 78), (49, 78), (56, 80), (66, 78), (82, 79),
                    (98, 78), (113, 79), (130, 78), (148, 78), (162, 78),
                    (180, 79), (198, 78), (215, 79), (222, 73), (224, 78),
                    (226, 83), (178, 83), (178, 81), (176, 82), (176, 83),
                    (130, 83), (130, 81), (128, 82), (128, 83), (98, 83),
                    (98, 81), (96, 82), (96, 83), (66, 83), (66, 81),
                    (64, 82), (64, 83), (33, 83)])
    border = {(x + dx, y + dy) for x, y in face | side
              for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1))}
    draw(px, border, 1)
    draw(px, side, 3)
    draw(px, face, 2)
    # The word crack runs through the depth as well as the yellow faces.
    draw(px, polygon([(152, 46), (155, 46), (155, 60), (156, 69),
                      (155, 84), (151, 84), (152, 69), (151, 61)]), 1)
    # Share plain stone rather than repeated cracks. Distinct fractures spend
    # tiles only where the letter geometry is already unique. Mode 7 map bytes
    # contain tile indices only: there are no per-tile H/V flip flags.
    quiet_tiles = {(18, 6), (18, 7), (26, 8), (21, 7), (21, 6),
                   (14, 8), (14, 7), (15, 7), (15, 8)}
    for chip in ([(36, 74), (37, 76), (36, 78)],
                 [(63, 49), (63, 52)], [(120, 49), (121, 51)],
                 [(178, 46), (180, 46)], [(220, 75), (219, 77)]):
        stroke(px, chip, 4)
    if not texture:
        return
    # Asymmetric damage: H/J/E/O have broad splits; A, the first U and the
    # second H stay mostly clean. Some full-face cracks divide stone chunks,
    # but are only one pixel wide so the letter's overall stroke still reads.
    scratch = [[0] * 256 for _ in range(88)]
    for crack in ([(34, 56), (37, 55), (40, 56)],
                  [(35, 64), (39, 63), (43, 64), (48, 62)], [(40, 63), (40, 61)],
                  [(63, 72), (64, 73)],
                  [(68, 65), (72, 64), (76, 66), (81, 64), (84, 65)],
                  [(78, 65), (79, 68)],
                  [(86, 53), (90, 52), (95, 53), (99, 52)], [(92, 53), (93, 55)],
                  [(96, 57), (95, 61), (97, 64), (96, 69), (98, 72)],
                  [(104, 77), (107, 76)],
                  [(124, 54), (127, 53), (131, 54)],
                  [(125, 72), (129, 73), (132, 72)], [(129, 73), (130, 76)],
                  [(135, 59), (138, 60), (140, 59)],
                  [(138, 60), (137, 63), (138, 66), (136, 69)],
                  [(159, 73), (161, 74)],
                  [(178, 44), (179, 47), (182, 49)], [(179, 47), (176, 48)],
                  [(175, 62), (180, 63), (184, 61), (188, 62)],
                  [(177, 71), (179, 73), (178, 76), (181, 78)],
                  [(192, 58), (195, 60), (196, 64)], [(195, 60), (193, 62)],
                  [(200, 73), (204, 72), (206, 73)],
                  [(210, 56), (213, 58), (214, 62)], [(219, 68), (222, 66)]):
        stroke(scratch, crack)
    draw(px, {(x, y) for y, row in enumerate(scratch) for x, v in enumerate(row)
              if v and (x, y) in face and (x // 8, y // 8) not in quiet_tiles}, 1)
    # A few warm lit lips, rather than a second thick line along every crack.
    draw(px, {(x, y) for x, y in ((36, 57), (42, 65), (75, 67), (94, 54),
                                (96, 62), (128, 74), (139, 62), (182, 64),
                                (195, 62), (212, 60))
              if px[y][x] == 2}, 3)
    draw(px, {(46, 72), (54, 76), (70, 52), (143, 77), (170, 68), (221, 75)}, 4)


def artwork(tiles, tilemap):
    old = render(tiles, tilemap)
    ribbon(old)
    decoration = {(x, y) for y, row in enumerate(old) for x, v in enumerate(row) if 6 <= v <= 12}
    keep = decoration | {(x, y) for y, row in enumerate(old) for x, v in enumerate(row)
                         if v == 1 and (y < 24 or any((x + dx, y + dy) in decoration
                                                     for dx in (-1, 0, 1) for dy in (-1, 0, 1)))}
    px = [[0] * 256 for _ in range(88)]
    # A chipped concave crown and broad foot echo the original four stone kanji.
    slab = polygon([(33, 81), (48, 61), (61, 49), (76, 34), (86, 39), (98, 48),
                    (115, 52), (137, 51), (151, 44), (171, 26), (179, 28),
                    (186, 46), (200, 65), (215, 84), (209, 87), (37, 87)])
    draw(px, slab, 3)
    rim = {(x, y) for x, y in slab if any((x + dx, y + dy) not in slab
                                        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)))}
    draw(px, rim, 1)
    # A few short fractures in the exposed mountain; none is applied to letter faces.
    for crack in ([(76, 38), (75, 41), (77, 43)],
                  [(172, 31), (171, 34), (173, 36)],
                  [(191, 84), (195, 83), (197, 84)]):
        stroke(px, crack)

    stone(px)
    # Bottle/egg ornament and ribbon stay at their original coordinates, in front of the stone.
    for x, y in keep:
        px[y][x] = old[y][x]
    return px


def patch(rom):
    """Replace the title asset and its 32x11 map, staying within tiles $01-$C1."""
    block = unpack(rom)
    tilemap = block[0x3E0:0x540]
    tiles = bytes(rom[TILES:TILES + NT * 64])  # existing English ribbon/subtitle
    px = artwork(tiles, tilemap)
    unique = {bytes(64): 0}
    data, new_map = bytearray(), bytearray()
    for ty in range(11):
        for tx in range(32):
            tile = bytes(px[ty * 8 + y][tx * 8 + x] for y in range(8) for x in range(8))
            if tile not in unique:
                unique[tile] = len(unique)
                data += tile
            new_map.append(unique[tile])
    count = len(unique) - 1
    assert count <= LOGO_NT, f"title logo needs {count} tiles; budget {LOGO_NT}"
    rom[TILES:TILES + LOGO_NT * 64] = data + bytes((LOGO_NT - count) * 64)
    rom[MAP:MAP + len(new_map)] = new_map
    return count


if __name__ == "__main__":
    import sys
    from PIL import Image

    root = Path(__file__).resolve().parents[1]
    rom = bytearray((root / "rom/hh.sfc").read_bytes()) + bytearray(0x100000)
    base = (root / "assets/title_m7_en.bin").read_bytes()
    rom[TILES:TILES + len(base)] = base
    block = unpack(rom)
    px = artwork(base, block[0x3E0:0x540])
    pal = [int.from_bytes(block[0x3A0 + 2*i:0x3A2 + 2*i], "little") for i in range(16)]
    im = Image.new("RGB", (256, 88))
    im.putdata([tuple(((pal[v] >> s) & 31) * 255 // 31 for s in (0, 5, 10)) for row in px for v in row])
    im.resize((1024, 352), Image.Resampling.NEAREST).save(sys.argv[1])
    print(f"logo: {patch(rom)}/{LOGO_NT} tiles")
