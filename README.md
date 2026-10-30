# Hanjuku Hero: Ah, World, Be Soft-Boiled...!! English translation

Unofficial English fan translation of **Hanjuku Hero - Ah, Sekai yo Hanjuku Nare...!!** (Super Famicom, Square, 1992):
the source text and tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Dialogue / story (event scenes, opening crawl, episode title cards) | Translated |
| Menus, battle messages, names, system messages | Translated (about 25 long names shortened to 8 letters) |
| Name entry | Translated (English letters) |
| Title screen | Translated (logo redrawn as HANJUKU HERO) |
| Stage backdrops | Partly translated (smaller Japanese logos left as art) |
| Ending, curtain call, staff roll | Translated (less tested than the rest) |
| Save/load screens | Not checked in play |

Known issues: names and the date bar ("yr"/"mo.") are shortened in 8-tile fields; small map pop-ups use condensed
wording; start a new game, since Japanese saves keep Japanese names.

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `build.py`, `tools/` | Python build chain: extract, insert, lint, release. |
| `asm/` | SNES engine patches (asar). |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |

## Build your own patched ROM

Needs Python 3.12+, [asar 1.91](https://github.com/RPGHacker/asar) in `tools/asar/asar.exe`, and your own dump of the
Japanese game.

```sh
git clone https://github.com/minhnhattonthat/hanjuku-hero-ah-sekai-yo-hanjuku-nare
cd hanjuku-hero-ah-sekai-yo-hanjuku-nare
# copy your dump to: rom/Hanjuku Hero - Ah, Sekai yo Hanjuku Nare...!! (Japan).sfc
#   (1,048,576 bytes, SHA-1 4edad4a8a8e3ab6117171c48ce2a332757ed3e2f; the build refuses any other dump, see rom.sha1)
python -X utf8 build.py                                # -> build/hanjuku_en.sfc
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Square's and is included only so
the translation can be checked against it. Hanjuku Hero is (c) 1992 Square (now Square Enix); this project is not
affiliated with them. Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
