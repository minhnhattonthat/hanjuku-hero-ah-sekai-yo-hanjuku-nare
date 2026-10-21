# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9 - release zip built by `tools/release.py` -> `release/hanjuku-hero-ah-sekai-yo-hanjuku-nare_en.zip`.
  Not published: the user's call. Rebuild the zip after the playtest fixes below.
- **Done:**
  - Phases 1-6: all text systems translated + reviewed (fix passes fix01-fix04 in `work/tl`), title screen,
    name entry, castle menu template, password pieces, choice labels (`script/choices.json`), name ligatures.
  - Phase 8: tour2 (all 256 scripts, settled-text sheets reviewed), castle menu / main menu / map popups / battles
    checked; fixes: wrap trailing-space bug, choice-box page widths, speaker names (cmd 36), battle text bank hooks.
  - 2026-10-21 playtests (boot, castle, map, credits, ending; reports in `docs/bugs.md`): hardcoded battle/panel
    labels (`tools/immtext.py`, asm `Labels`), battle name inserts, bubble quips, episode title cards
    (`tools/cards.py`, debug `tools/debug/card_ep.lua --var EP=n` from `work/playtest/s_boot/0040.mss`),
    menu fits, wording; curtain-call banners/marquee and end screen (`cards.curtain_patch` / `end_patch`: raw tiles
    at file 0x16E40, loaded when the curtain call starts, so savestates from inside the credits show the old art).
  - 2026-10-22 final title logo (D7-D13): `tools/title_logo.py:stone` draws HANJUKU HERO as
    positive yellow stone strokes, with hand-shaped polygons, chipped edges and tight seams.
    Open notches remove the shared yellow foot/sign face; a wider full-height crack separates the
    words. Pass 8 varies fracture lengths, angles and density, mixing full-face splits, Y branches,
    hairlines and nearly clean faces. Salmon highlights, chips and lower notches remain. Only plain
    stems share tiles; no visible cracked tile repeats. Tests guard this, underlying letter shapes,
    counters and word gap; narrow cracks may split the faces into chunks as requested.
    SOFTBOILED HERO is centered by distance along the ribbon's front arch, excluding the folded tail.
    Original palette and egg/globe/ribbon positions retained. 192/193 logo/ribbon tiles;
    `build.py` generates it and `TitlePatch` uploads its 32x11 Mode 7 map.
    Original compressed source and shared stage art are untouched. RE: `docs/re/graphics.md`.
    Final touch-up removes only the O's top fracture and its highlight, reconnecting the accent-like
    chip: 11 changed pixels in the settled screenshot; all other artwork is identical to pass 8.
    Build SHA-1 prefix f9d08599d836; 18 tests pass, lint 3028 entries / 0 errors, cold-boot smoke passes.
    Settled title: `work/qa/logo-final/f001200.png`; comparison against pass 8:
    `work/qa/logo-final/comparison-sheet.png`. Inspected at native size and zoomed.
    Pass 8's original comparison, VRAM/palette verification and dense animation samples remain in
    `work/qa/logo-v8/`; final title smoke also captures the entrance every 60 frames.
    Final cold-boot warps recheck audition $35, merchant $8D and monthly bumper-harvest report $05:
    `work/qa/logo-final/audition/`, `merchant/`, `monthly-report/` (each has `sheet.png`).
    All three stage backdrops render without garbage tiles; the smaller Japanese curtain logo remains
    intact. Other stage variants have not all been replayed.
    Independent title/backdrop visual review and QA gate pass (four sheets;
    `work/qa/logo-final-manifest.tsv`, `work/qa/logo-final-verdicts/`).
    No commit or release script run; both are left to the user as requested.
- **Next:** release zip rebuilt 2026-10-22 with the logo (patched SHA-1 a0470ba7); a fresh full playtest of the ending path (the curtain-call art was checked by
  copying the block into VRAM, the end screen by a replay from `work/playtest/s_credits/0000.mss`).
- **Open bugs:**
  - Smaller Japanese logo artwork on stage backdrops remains; only the title-screen logo was replaced in D7.
  - 25 long names fall back to 8-char forms; 8-letter castle names touch the code-drawn level digit ("Almamoon2").
  - Hobby label "Fun", stat labels War/Rule/Pay (small windows) vs Combat/Domestic/Wage: width-bound, kept.
  - Hero name empty in warps.
- **Waiting on the user:** publishing.
