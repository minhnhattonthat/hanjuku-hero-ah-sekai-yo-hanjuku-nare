# Title logo (verified 2026-10-22)

The big title, ribbon and subtitle share a Mode 7 BG, with an animated egg behind it in OBJ.
Addresses below refer to the original ROM pinned by `rom.sha1`.

- `$09:EC07` calls `$03:F977` to decompress the block at **$0A:8000 (file 0x50000)**
  into `$7F:0000`. LZSS: 8-byte header, output length at +4; LSB-first flags (1 = literal),
  12-bit dictionary offset and 4-bit length + 3; 4 KiB prefilled dictionary, cursor $FEE.
  `tools/title_logo.py:unpack` reproduces the game's dictionary initialization. Its 26,596 output bytes
  match the cold-boot WRAM dump byte for byte (`work/qa/logo-trace/logo-ram.bin`).
- Palette: **$7F:03A0**, 16 BGR555 colours copied to CGRAM 0-15. Gold 2, peach depth 3,
  ochre recess 4, dark brown outline/cracks 1; ribbon 9/10 and subtitle 12. No palette edits.
- Map: **$7F:03E0**, 32 columns x 11 rows for logo/ribbon; subtitle rows at `$7F:0540`
  go to map rows 13-14 later. Mode 7 VRAM low bytes, 128-word row stride. Tile 0 is transparent.
  Map bytes are tile indices only, with no per-tile horizontal/vertical flip flags.
- Pixels: **$7F:4A60**, 226 tiles x 32 bytes of packed nibbles. `$09:F288` expands low nibble
  then high nibble into chunky 8bpp tiles at **$7F:8000** (64 bytes/tile). DMA via `$2119`
  uploads tiles $01-$E2 in chunks $1080/$1400/$1400, starting at VRAM word $0040.
  `$01-$C1` cover the main logo/ribbon; `$C2-$E2` cover the subtitle.

## English replacement

`build.py` loads the existing English ribbon/subtitle asset, then calls `title_logo.patch`.
The 2026-10-22 pass 8 keeps the approved **HANJUKU HERO positive yellow stone strokes**.
`stone()` uses individually shaped polygons, with irregular widths, chips and narrow interletter seams.
Open notches reach the silhouette, removing pass 5's yellow sign face and shared yellow foot.
Small counters show dark cutouts or the salmon pyramid; a wider word crack runs through the whole
height and the salmon depth. The mass's bottom/right edge carries the extrusion, with no per-letter
bevels. Pass 8 varies fracture direction, length and density: long full-face splits, angled cracks,
Y branches and short hairlines, with occasional salmon highlights and pits. A, the first U and the
second H stay almost clean; H/J/E/O have broader fractures. Pass 7's silhouette chips and four lower
notches remain. Identical plain stem tiles are shared; cracked tiles are never copied. Every visible
surface-crack tile is unique (regression-tested). Other tests guard underlying letter geometry,
counter/word-gap preservation and the palette; one-pixel cracks may now divide faces into chunks.
The light salmon pyramid and its peaks retain pass 6's geometry.
The main logo uses no font.
The ribbon reads **SOFTBOILED HERO**, using the existing three-pixel-wide font at five-pixel advances
measured along the arch. Text is centered on the visible front band (x84..160), excluding its folded tail.
The egg ornament and ribbon silhouette retain their original coordinates;
the animated globe's sprites are untouched.
The 32x11 image uses **192 of 193 tiles** (the original logo/ribbon budget); the 33 subtitle tiles
remain byte-identical. All drawing is generated in code using the original palette.

Generated pixels replace **$3E:8000-$B03F** (file 0x1F0000, 193 tiles) in the existing title asset.
The new 352-byte map lives at **$3E:BC00-$BD5F** (file 0x1F3C00), after the copyright sprites.
The existing signature-guarded **TitlePatch at $09:F2CE** copies the asset to WRAM and now also
DMAs the map during its vblank, restoring the VRAM increment mode/address for the original tile upload.
The source compressed block, original map, palette, subtitle and stage graphics are not overwritten.

Current evidence: `work/qa/logo-v8/f001200.png` (settled title including NEWGAME),
`work/qa/logo-v8/comparison-sheet.png` (original left, revision right), and
`work/qa/logo-v8/settled-zoom.png`. The original was cold-booted with only the first Start press
(`600 -;6 start;606 -`) so it stays on the title at frame 1200. Both captures have identical Mode 7
scroll, center and matrix values. The generated map and all 226 uploaded tiles match the PPU dump;
CGRAM colours 0-15 match the original. Native-size and zoomed inspection, 18 tests, lint and smoke pass.
Animation was recaptured every two frames from 550 through 690, with changed-frame inspection
in `work/qa/logo-v8/animation-sheet.png`; no garbage tiles observed.
Independent settled/animation review and QA gate pass (`work/qa/logo-v8-manifest.tsv`,
`work/qa/logo-v8-verdicts/`).
Earlier evidence: `work/qa/logo-original` (DMA trace), `work/qa/logo-stage` (cold-boot event $35),
`work/qa/logo-merchant` (event $8D with its smaller Japanese backdrop logo). Those stage checks
predate this artwork revision; they have not been repeated for it.
