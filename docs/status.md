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
- **Next:** rebuild the release zip; a fresh full playtest of the ending path (the curtain-call art was checked by
  copying the block into VRAM, the end screen by a replay from `work/playtest/s_credits/0000.mss`).
- **Open bugs:**
  - Big kanji logo on the title kept as art.
  - 25 long names fall back to 8-char forms; 8-letter castle names touch the code-drawn level digit ("Almamoon2").
  - Hobby label "Fun", stat labels War/Rule/Pay (small windows) vs Combat/Domestic/Wage: width-bound, kept.
  - Hero name empty in warps.
- **Waiting on the user:** publishing.
