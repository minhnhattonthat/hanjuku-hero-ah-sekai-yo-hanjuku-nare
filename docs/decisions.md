# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-10-16 | Honorifics and name order | keep (-sama), drop; JP or Western order | Drop; convey through register (〜さま -> "my lord"/"sire" as an address). Given name first. |
| D2 | 2026-10-16 | Romanization source for names | official English (Hanjuku Hero 4 / Egg Monster Hero localizations), earlier patch, Hepburn | Official English if any, else the earlier fan patch (Dragoon-X 0.010, menus only), else modified Hepburn; natural English for pun names. |
| D3 | 2026-10-16 | Credits | stay Japanese, translate | English. |
| D4 | 2026-10-16 | Abbreviations | engine work first (default), abbreviate | Default: full names and terms, engine work before cutting meaning. |
| D5 | 2026-10-16 | Graphics text left in Japanese | none (default), list | Graphics text in scope; the big kanji title logo stays as art. **Replaced by D7.** |
| D6 | 2026-10-16 | Specs and plans | need approval, pre-approved | Pre-approved (batch run); never push or publish. |
| D7 | 2026-10-21 | Big title-screen logo | retain kanji art; English HANJUKU HERO (title case if needed) | User explicitly requested an English replacement, superseding D5. Draw HANJUKU / HERO in code, matching the original palette and bold outline within its tile/map budget; preserve the English ribbon/subtitle and check shared stage artwork. No commit. Layout/style refined by D8. |
| D8 | 2026-10-22 | Title logo revisions through pass 4 | user-directed revisions | HANJUKU HERO on one line; centered SOFTBOILED HERO ribbon. Heavier, taller stone letters with chipped edges, short cuts and pits, visible salmon extrusion, open counters and intact strokes. Keep the clear word gap, light salmon pyramid, original palette/ornament positions and 193-tile limit. Native-size legibility takes priority over texture density. No commit. Stone construction refined by D9. |
| D9 | 2026-10-22 | Title logo pass 5 | user-directed revision | One continuous yellow rock mass, with hand-hewn letter shapes cut into it and tight spacing; no separate font-like glyphs. One rough outer silhouette and salmon extrusion only around the whole mass. Retain a readable word groove, open counters, centered ribbon, light pyramid, original palette and 193-tile budget. No commit. **Figure/ground treatment replaced by D10.** |
| D10 | 2026-10-22 | Title logo pass 6 | user-directed correction | Letter strokes must be positive yellow stone, not dark writing cut into a yellow sign. Pack hand-hewn strokes with thin seams and small dark/salmon counters, but make the word crack clearly wider at 1x. Preserve the one-line title, peaked pyramid, centered ribbon, original palette and 193-tile limit. No commit. |
| D11 | 2026-10-22 | Title logo pass 7 | user-approved pass 6 base; surface revision | Keep pass 6's letter shapes, packing, word gap, pyramid, ribbon and palette. Add more branching one-pixel cracks, occasional salmon edge highlights, and broken edges. Preserve native-size legibility and intact strokes; reuse crack tiles within 193 slots. No commit. |
| D12 | 2026-10-22 | Title logo pass 8 | user-directed surface revision | Vary crack length, angle, direction and density; mix long full-face splits, hairlines, Y branches, pits and almost-clean faces. Avoid visibly repeated crack tiles. One-pixel cracks may split strokes into stone chunks while the letters stay legible at 1x. Keep pass 7's shapes/layout/palette and the 193-tile limit. No commit. |
| D13 | 2026-10-22 | Final title touch-up | user-approved pass 8 base | Remove or move only the accent-like chip above the final O. Recheck audition $35, merchant $8D and the monthly-report backdrop if reachable. No commit and do not run tools/release.py; the user will handle both. |
