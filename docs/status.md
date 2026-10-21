# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9 - release zip built by `tools/release.py` -> `release/hanjuku-hero-ah-sekai-yo-hanjuku-nare_en.zip`.
  Not published: the user's call.
- **Done:**
  - Phases 1-6: all text systems translated + reviewed (fix passes fix01-fix04 in `work/tl`), title screen,
    name entry, castle menu template, password pieces, choice labels (`script/choices.json`), name ligatures.
  - Phase 8: tour2 (all 256 scripts, settled-text sheets reviewed), castle menu / main menu / map popups / battles
    checked; fixes: wrap trailing-space bug, choice-box page widths, speaker names (cmd 36), battle text bank hooks.
- **Next:** QA of the save/load screen and the ending/credits.
- **Open bugs:**
  - Big kanji logo on the title kept as art.
  - 25 long names fall back to 8-char forms.
  - Battle bubble shows 1 line (multi-line quips unverified).
  - Save/load screen and ending/credits not reached in QA.
  - Hero name empty in warps.
- **Waiting on the user:** publishing.
