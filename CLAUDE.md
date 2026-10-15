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

## Status
- Done: Step 0. Next: phase 1 recon. Open bugs: none.
