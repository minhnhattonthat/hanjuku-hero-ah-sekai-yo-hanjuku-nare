import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import title_logo  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ORIG = ROOT / "rom/Hanjuku Hero - Ah, Sekai yo Hanjuku Nare...!! (Japan).sfc"


def test_title_decompression_matches_cold_boot_wram():
    # Captured at $09:F288 in work/qa/logo-trace/logo-ram.bin (original ROM).
    block = title_logo.unpack(ORIG.read_bytes())
    assert len(block) == 26596
    assert hashlib.sha256(block).hexdigest() == "f2e4fa8b80e1e55193df55a586fc94194b4a8434abedbbf309559f600ebaf737"


def test_letter_shapes_and_negative_spaces_survive_surface_fractures():
    px = [[0] * 256 for _ in range(88)]
    title_logo.stone(px, texture=False)
    # Pass 8 permits one-pixel cracks to split a face into stone chunks. Guard
    # the underlying letter shapes and ensure texture cannot fill their holes.
    for left, right in ((33, 49), (51, 66), (68, 84), (85, 99), (101, 116),
                        (118, 134), (135, 150), (157, 173), (175, 190),
                        (191, 208), (209, 223)):
        unseen = {(x, y) for y, row in enumerate(px) for x in range(left, right + 1)
                  if row[x] in (2, 4)}
        start = next((x, y) for x, y in unseen if px[y][x] == 2)
        unseen.remove(start)
        pending = [start]
        while pending:
            x, y = pending.pop()
            for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    pending.append(neighbor)
        assert not {(x, y) for x, y in unseen if px[y][x] == 2}, (left, right)
    textured = [[0] * 256 for _ in range(88)]
    title_logo.stone(textured)
    assert all(textured[y][x] == v for y, row in enumerate(px) for x, v in enumerate(row)
               if v not in (2, 4))
    assert all(textured[y][x] not in (2, 4) for y in range(46, 84) for x in range(151, 157))
    # H's notches and J's open left side must not turn back into sign-face fill.
    assert all(textured[y][x] != 2 for x, y in ((42, 52), (41, 75), (88, 62)))


def test_surface_crack_tiles_do_not_repeat():
    plain, textured = ([[0] * 256 for _ in range(88)] for _ in range(2))
    title_logo.stone(plain, texture=False)
    title_logo.stone(textured)
    cracked = set()
    for ty in range(11):
        for tx in range(32):
            coords = [(tx * 8 + x, ty * 8 + y) for y in range(8) for x in range(8)]
            if any(plain[y][x] == 2 and textured[y][x] == 1 for x, y in coords):
                tile = bytes(textured[y][x] for x, y in coords)
                assert tile not in cracked, "A visible surface fracture tile repeats"
                cracked.add(tile)


def test_logo_fits_and_preserves_shared_source_subtitle_and_copyright():
    rom = bytearray(ORIG.read_bytes()) + bytearray(0x100000)
    tiles = (ROOT / "assets/title_m7_en.bin").read_bytes()
    rom[title_logo.TILES:title_logo.TILES + len(tiles)] = tiles
    before = bytes(rom)
    count = title_logo.patch(rom)
    assert 0 < count <= 193
    assert len(rom) == len(before)
    assert rom[:title_logo.TILES] == before[:title_logo.TILES]
    assert rom[title_logo.TILES + 193 * 64:title_logo.MAP] == before[title_logo.TILES + 193 * 64:title_logo.MAP]
    assert rom[title_logo.MAP + 352:] == before[title_logo.MAP + 352:]
    tilemap = rom[title_logo.MAP:title_logo.MAP + 352]
    assert max(tilemap) <= count
    new_px = title_logo.render(rom[title_logo.TILES:title_logo.TILES + len(tiles)], tilemap)
    old_map = title_logo.unpack(before)[0x3E0:0x540]
    old_px = title_logo.render(tiles, old_map)
    # Wording changes inside the arch, but neither the ribbon silhouette nor the egg ornament moves.
    assert [[v != 0 for v in row] for row in new_px[:24]] == [[v != 0 for v in row] for row in old_px[:24]]
    for y, row in enumerate(old_px):
        for x, v in enumerate(row):
            if v in (6, 7, 8):
                assert new_px[y][x] == v
    assert all(0 <= v <= 12 for row in new_px for v in row)  # unchanged CGRAM palette
