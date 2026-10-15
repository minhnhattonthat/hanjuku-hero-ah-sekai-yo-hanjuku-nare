# Hanjuku Hero - Ah, Sekai yo Hanjuku Nare...!! (SNES, 1992, Square) English translation

Skill: translate-retro-game (H:\translation\batch\.claude\skills\translate-retro-game\SKILL.md). Read it before ROM, text or QA work. Batch brief: H:\translation\batch\projects\BATCH_BRIEF.md.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py`           -> build/hanjuku_en.sfc
- Check:    `python -X utf8 tools/check.py`     (tests + lint; the pre-commit hook runs this)
- Smoke:    `python -X utf8 H:/translation/batch/.claude/skills/translate-retro-game/scripts/emu.py build/hanjuku_en.sfc --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Release:  `python -X utf8 tools/release.py` (patch + verify; never publish)

## Paths
- Original ROM: `rom/Hanjuku Hero - Ah, Sekai yo Hanjuku Nare...!! (Japan).sfc` (sha1 4edad4a8..., 1 MiB LoROM; copy `rom/hh.sfc`). Reference-only earlier partial patch: `rom/ref/... (patched).sfc` (never build from it).
- Emulator: `tools/mesen/` (MesenCE 2.2.1, https://github.com/nesdev-org/MesenCE/releases/download/2.2.1/Mesen_2.2.1_Windows.zip; gitignored). Assembler: `tools/asar/asar.exe` (1.91, github.com/RPGHacker/asar).
- RE notes: `docs/re/`. Glossary + rulings: `glossary.md`.

## Rulings
- Edit source files only with the file-edit tool; scripts read and analyse, never `.replace()` and write back.
- Honorifics dropped (register instead); given name first. Credits in English. Romanization: official English (Hanjuku Hero 4 / Egg Monster Hero localizations) if any, else earlier fan patch, else modified Hepburn.
- Full names and terms, no abbreviations; engine work before cutting meaning. Graphics text in scope.
- Never push/publish. Release = `release/hanjuku-hero-ah-sekai-yo-hanjuku-nare_en.zip` (patch + README).

## Debug / QA
- Warp to any event script from cold boot: `emu.py ROM --route tools/routes/boot.txt --script tools/debug/warp.lua --var SCENE=0x35 --frames 3000 --mash 45`
- Tour every script: `python -X utf8 tools/debug/tour.py ROM --all --jobs 6 --out work/qa/tour` (sheets per id).
- States (from ORIGINAL rom; load fine in builds since original text data stays in place): work/states/castle_menu.mss,
  battle1.mss, map1.mss, early.mss. Regenerate: tools/routes/to_castle.txt (+ mash) from cold boot.
- Translate: `tools/batches.py split|check|merge|pairs|status`; brief docs/translator-brief.md; style docs/style-reference.md.
- Text systems + hooks: docs/re/text.md. Extract: tools/dump.py (never overwrites). Wrap/limits: tools/layout.py.

## Status
- Done: phases 1-6: all text systems translated + reviewed (fix passes fix01-fix04 in work/tl), title screen,
  name entry, castle menu template, password pieces, choice labels (script/choices.json), name ligatures.
- Next: phase 8 QA tour (tools/debug/tour.py, then tools/debug/textsheet.py per run dir), fix findings, phase 9 release.
- Open: big kanji logo on title kept as art; 25 long names fall back to 8-char forms; battle bubble line limit (3)
  unverified in-game; small system popups fitted to JP window widths (unverified).
