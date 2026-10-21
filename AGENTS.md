# Hanjuku Hero - Ah, Sekai yo Hanjuku Nare...!! (SNES, 1992, Square) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `<SKILL_DIR>/SKILL.md`; `$SKILL` = the directory holding its SKILL.md, here `C:/Users/Nathan/.claude/plugins/marketplaces/retro-translation/skills/translate-retro-game`). Read it before ROM, text or QA work. Batch brief: H:\translation\batch\projects\BATCH_BRIEF.md.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py`           -> build/hanjuku_en.sfc (checks the dump against `rom.sha1` first)
- Check:    `python -X utf8 tools/check.py`     (tests + lint; the pre-commit hook runs this)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/hanjuku_en.sfc --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 $SKILL/scripts/emu.py build/hanjuku_en.sfc --out work/qa/warp --route tools/routes/boot.txt --script tools/debug/warp.lua --var SCENE=0x35 --frames 3000 --mash 45` (SCENE = event script id; never ask the user to play to a scene)
- Tour:     `python -X utf8 tools/debug/tour.py build/hanjuku_en.sfc --all --jobs 6 --out work/qa/tour` (sheets per script id)
- Release:  `python -X utf8 tools/release.py` (patch + verify; never publish without the user) -> `release/hanjuku-hero-ah-sekai-yo-hanjuku-nare_en.zip` (patch + README from `docs/README_release.txt`)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original ROM: `rom/Hanjuku Hero - Ah, Sekai yo Hanjuku Nare...!! (Japan).sfc` (1 MiB LoROM; gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`; copy `rom/hh.sfc` for the peek/scan tools). Reference-only earlier partial patch: `rom/ref/... (patched).sfc` (never build from it).
- Emulator: this repo's own copy in `tools/mesen/` (MesenCE 2.2.1, https://github.com/nesdev-org/MesenCE/releases/download/2.2.1/Mesen_2.2.1_Windows.zip; gitignored). Assembler: `tools/asar/asar.exe` (1.91, github.com/RPGHacker/asar). Savestates: `work/states/`.
- Text: `script/` (JSON; choice labels `script/choices.json`). Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md` (text systems + hooks: `docs/re/text.md`). Fonts and their licences: `docs/fonts.md`.
- Translate: `tools/batches.py split|check|merge|pairs|status`; briefs `docs/translator-brief.md`, `docs/reviewer-brief.md`; style `docs/style-reference.md`. Extract: `tools/dump.py` (never overwrites). Wrap/limits: `tools/layout.py`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- Savestates come from the ORIGINAL rom (`work/states/castle_menu.mss`, `battle1.mss`, `map1.mss`, `early.mss`); they load fine in builds since the original text data stays in place. Regenerate: `tools/routes/to_castle.txt` (+ mash) from cold boot.
- Hero name is empty in warps (no name entry ran).

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
