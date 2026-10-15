# Translator brief - Hanjuku Hero: Ah, Sekai yo Hanjuku Nare...!! (SFC, Square, 1992)

You translate part of the Japanese script of Hanjuku Hero into English for a fan patch. It is a comic real-time
strategy game: the player is the young, lazy lord of the kingdom of Almamoon, nagged by his old Minister, fighting
egg-themed armies (generals summon Egg Monsters from eggs). Tone: broad comedy, puns, Square self-parody (Final
Fantasy jokes), egg puns everywhere (soft-boiled = the hero's side, hard-boiled = the enemy).
Work only on the batch named in your dispatch. Do all translation yourself; do not dispatch subagents.
Repo root: H:\translation\batch\projects\hanjuku-hero-ah-sekai-yo-hanjuku-nare

## Read first
1. `docs/style-reference.md` - approved example pairs and voices. Match this voice.
2. `build/terms_<batch>.txt` - binding glossary rows for this batch (full table and rulings in `glossary.md`).

## Input: `work/tl/<batch>.tsv`
`id<TAB>form<TAB>limit<TAB>Japanese`. Lines are in game order (one scene follows another): use neighbours for context.
- form `dlg`: event dialogue. limit `26x4` = the window is 26 characters wide and shows 4 lines; the build wraps
  your text automatically at spaces. A page ends at `{w}{p}` (wait for button, then clear the window).
- form `crawl`: the opening text crawl, lines separated by `{n}`, 26 chars max per line, centre with spaces; never
  use the digit 9 there.
- form `menu`: castle-menu message, `26x2` = at most 2 lines of 26, no page breaks possible.
- form `sys`: system message box, `27x2` = at most 2 lines of 27 (use `{n}` to break where you want).
- form `battle`: battle message/quip, `26x3` = up to 3 lines of 26 per bubble; `{1B}` starts a new bubble.
- form `name`: a name/label in a fixed 8-character field (limit `8`). Count every character incl. spaces.

## Tokens (copy exactly, same order)
- `{w}` wait for button, `{p}` clear window (page), `{n}` line break, `{1B}` new bubble (battle).
- `{#0}`, `{#1}`.. = opaque game commands (animations, pauses, sounds) that fire at that point of the text. Keep them
  in the same order, at the matching point of your sentence (e.g. a pause `{#2}` between dramatic words).
- `{hero}` = the player's name (up to 8 letters). `{nameA}`..`{nameE}`, `{name9}` = a general/castle name inserted by
  the game; `{str:XX}` another inserted string. `{v02}`, `{v03}`.. (battle) = attacker/target names and numbers.
  Treat names as up to 8 characters wide. Never glue a suffix to a variable ("{v04}th" is wrong; "{v04} damage" fine).
- You may ADD `{w}{p}` pairs inside a `dlg` entry to split a long page into more pages (the window is small); you may
  add or move `{n}`. You may not drop, add or reorder any other token.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII plus ♪ ♥ ~ only: straight quotes `"` `'`,
`...`; no tabs inside the English, no Japanese or full-width characters, no `\uXXXX`. No literal newlines.

## Validate
Run `python -X utf8 tools/batches.py check <batch>` from the repo root and fix every reported id until it prints OK.
It checks ids, tokens, encodable characters and the wrapped width/lines per page.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese doesn't
  state; don't summarise or skip. Adapt wordplay so the joke still lands (no translator notes). Dialect/accents in the
  JP (Kansai merchants: でっか/まんな; old men: じゃ) -> give them a light English flavour, consistently.
- Speaker prefixes: JP `だいじん「...` -> `Minister: ...`. A line starting with 「 and no name -> just the line, no
  quote marks. Narration has no prefix.
- Names and terms exactly as in the glossary. Never abbreviate to fit: split pages (dlg) or rephrase; if it truly
  can't fit (menu/sys/name), keep the meaning and report `LONG: id`.
- Honorifics dropped; さま on the lord -> "my lord" / "sire" by register. Given name first.
- Punctuation: ‥ -> `...`, ！！ -> `!!`, ！？ -> `!?`, 〜 stretched vowel -> stretch the English word or use `~`.
- Names (form `name`): 8 characters max. Pun/parody names: keep the joke (FF parodies stay recognisable, e.g. a
  "Behemoth" pun stays a Behemoth pun). Food/spice names of generals: use the normal English spelling.

## Notes from earlier batches (binding)
- Terms: はんじゅくち = soft-boiled points; せんとうりょく = combat power; ないせいりょく = domestic power;
  しょうぐん えんごかい = General Placement Agency; なぞのびじょ = Mysterious Beauty; ゴニンジャー = Goninja;
  しようかいすう (eggs) = uses; かんじゅくプリンス = Hard-Boiled Prince; かんじゅくクイーン = Hard-Boiled Queen;
  かんじゅくだいまおう = Hard-Boiled Demon King (prefix "Demon King:"); かんじゅくだいまじょう = Hard-Boiled Demon
  Castle; してんのう = Four Heavenly Kings; だいしょうぐん = Grand General; はんじゅくぐん = Soft-Boiled Army;
  せいめいたい = Lifeform; いばらのとう = Tower of Thorns; しかいしゃ = Host; くろふく = Men in Black;
  ギャル = Gal(s); エッグマンナイト = Eggman Knight; はんじゅくちょうりメモ = "Soft-Boiled Cooking Notes" (end
  cards, always this form); episode previews: "Next time on Hanjuku Hero{n}Episode N: ...".
- Some {#n} tokens print a name (up to 8 chars) although the checker counts them as 0 wide: leave room.
- The checker flags letters "st/nd/rd/th" right after any token; if a word must continue after a {#n}, split it
  so the next fragment doesn't start with those letters.
- A JP line starting with は/が right after an inserted name: start the English with a space (" went home").

## Consistency
Never edit `glossary.md` or anything except your own output file. For a recurring name or term not in the glossary,
pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
