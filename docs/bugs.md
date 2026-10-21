# Bugs

Tick `- [x] (fixed in <build>)` once re-checked from the cited state.

## 2026-10-21 playtest - hanjuku_en.sfc sha1 888a0584b9bf
Evidence: `work/playtest/ev/s_castle/NNNN.png|.sheetK.png|.<state>`, presses in `log.tsv`.

- [x] step 0028-0034 - text - Recruit audition, candidate intro - the 3 stat lines under each "My name is X." are garbage glyphs - "HP  st 39P f)T" st zX / bEgnpst 6P ztbtst 5P / hEgNEgst 4G"
- [x] step 0036-0037 - text - Dismiss list, general info panel - Egg value garbage ("zX" no egg, "r"" for Chevre/Cocotte); Generals status shows "Egg none" (step 0054)
- [x] step 0018 - text - Fortify confirm - Yes/No window covers the end of the line - "Almamoon Castle, e"
- [x] step 0088 - text - field map castle Stats window - name past right border, space missing - "AlmamoonCastle"
- [x] step 0056 - text - Main Menu > Castles > status - space missing - "AlmamoonCastle"
- [x] step 0059 - text - System sub-menu - last letter on window border - "Sound Mode"
- [x] step 0069 - text - Training result box - 3rd line over bottom border of 2-line box - "Bravo! ...I'd like to say, / but with that skill, real / combat would be rough..." (not a bug: fits, JP also 3 lines)
- [x] step 0077 - text - field map Pause box - word too wide, "e" on border - "Pause"
- [x] step 0034 - wording - audition hire line reads as talking to Endive - "Leave it to me, Endive!"
- [x] step 0017 - wording - Fortify side panel - "Best is / Cocotte / General."
- [x] step 0017, 0055 - wording - castle list level glued to name - "Almamoon2" (kept: 8-letter castle names fill the field before the code-drawn level)
- [x] step 0036 vs 0049 - wording - stat labels differ: "War / Rule / Pay" vs "Combat / Domestic / Wage" (kept: small windows are 7 tiles wide)
- [x] step 0049 - wording - Generals status hobby label - "Fun Snacking" (kept: 3-tile label before the hobby)
- [x] step 0050 - wording - Generals status page 2 singular label over list - "Card Diehard / Diehard / Landswim" (kept: label column 4 tiles)
- [x] step 0013 - wording - Troops quantity help - "Left/right: digit: / up/down: its value!"
- [x] step 0075 - wording - All done confirm - "Acceptable?"
- [x] step 0021, 0074 - text - monthly command menu right-column cursor covers left word end - "Merchan", "Main Mer" (labels Shop / Menu, max 7 tiles like the JP)
- [x] step 0025 - text - audition stage backdrop kanji logo still Japanese - "半熟英雄" (kept as art, D5)

## 2026-10-21 playtest - hanjuku_en.sfc sha1 888a0584b9bf
Evidence: `work/playtest/ev/s_map/NNNN.png|.sheetK.png|.<state>`, presses in `log.tsv`.

- [x] step 0057-0058 - text - battle general command menu - all 3 command labels garbage (state RAM from JP rom?) - "f)T゛EjLp / N"Ff゛ / ftNneP"
- [x] step 0061-0064 - text - egg monster command menu - 3rd entry garbage - "Old Nuke / Ultimate / f)T゛, =n゛a1"
- [x] step 0062, 0065 - text - enemy (Mint) command window during monster fight - garbage - "TpR゛N / =pTpR゛N / f)T゛EjLp"
- [x] step 0064 - text - battle message - inserted target name garbage, line breaks before "'s" - "It exploded over HtX / 's head!"
- [x] step 0061-0067 - text - egg monster chosen as "Iron #8", battle messages call it MoonBuff - "Egg Monster MoonBuff  is born!"
- [x] step 0039, 0050 - text - castle Stats/info pop-up - no space, name cut at frame - "NacumeraCastl", "KikandonCast"
- [x] step 0069 - text - map pause box too narrow - "Pause"
- [x] step 0077, 0079 - text - monthly report / merchant stage backdrop JP logo graphic - "半熟英雄" (kept as art, D5)
- [x] step 0062-0067 - wording - two spaces after inserted names in battle messages - "Beets  attacks!", "MoonBuff  fell in glory!"
- [x] step 0062, 0065 - wording - unclear who "Beets" is - "Beets  attacks!"
- [x] step 0065-0066 - wording - quote marks drawn as JP closing mark at both ends - "”Weekly special~!!! *Click*...”"
- [x] step 0042-0043 - wording - cards screen: same description for every card, count mismatch, ambiguous stat row - "Cards left:3", "Battle card.", "Egg Pick Egg4" ('Picks left:' = JP card select N more; 'Battle card.' is the JP text for every battle card)

## 2026-10-21 playtest - hanjuku_en.sfc sha1 888a0584b9bf
Evidence: `work/playtest/ev/s_boot/NNNN.png|.sheetK.png|.<state>`, presses in `log.tsv`.

- [x] step 0041 - text - Episode 1 title card - episode title all Japanese (graphics) - "第1話 黒きたまごは危険な香り"
- [x] step 0033-0034 - text - tutorial battle speech bubble - lines cut off at bubble edge - "Hit A while the bar's bl" / "Red bar? Pressing's no"
- [x] step 0064 - text - map Stats window - castle name no space, runs past right border - "AlmamoonCastle"
- [x] step 0012, 0014, 0017, 0042, 0045, 0047, 0048, 0051, 0055, 0058 - text - green dialogue box (stage scenes) - 4th line drawn on the box's bottom border - "burden for my young / lord..." (not a bug: the box has 4 rows, JP uses 4-line pages)
- [x] step 0004-0005 - text - scrolling prologue - stale/overlapping rows flash at top/bottom edges - "Not even the legendary" over "A hero took up the" (same in the JP rom)
- [x] step 0050 - wording - Queen scene - ungrammatical - "It's a perfect! Hard-boiled! Black egg!"
- [x] step 0054 - wording - Queen scene - lights were just turned up - "Queen: Oh, you can bring the lights back up now!"
- [x] step 0068 - wording - general stats window - "Fun" label for hobby - "Fun Budo" (kept: 3-tile label before the hobby)
- [x] step 0076 - wording - castle-stormed popup - romanization check - "Nacumera Castle Stormed!" (ナキューメラ, kept)
- [x] step 0001 - wording - title menu - no space - "NEWGAME" (original art, same in JP)
- [x] step 0044 - wording - throne room - "You there! Who are you!!"
- [x] step 0055 - text - Minister line - JP closing quote both sides - "the ”egg” handed down"

## 2026-10-21 playtest - hanjuku_en.sfc sha1 888a0584b9bf
Evidence: `work/playtest/ev/s_credits/NNNN.png|.sheetK.png|.<state>`, presses in `log.tsv`.

- [x] step 0025-0026 - text - final end screen after credits - end graphic Japanese - "めでたし めでたし" ('And they lived / happily ever after.')
- [x] step 0001-0025 - text - curtain-call stage backdrop - Japanese graphics on banners/marquee - "祝 半熟 終了!!" / "おわり～!!" (banners HOORAY, marquee END!!)
- [x] step 0015-0016, 0021-0023 - text - credits box 4-line pages - 4th line on bottom border - "cranny, all the waaay...!" (not a bug: 4-row box)
- [x] step 0010 - text - credits, background graphics quote - opening quote drawn as closing glyph - "...But ”hate” can mean love."
- [x] step 0015 - wording - credits roles look swapped (Uematsu "Sound effects!") - "Minister: Sound effects! Nobuo Uematsuuu!" (faithful: JP says so)
- [x] step 0003 - wording - credits Tokita - typo? - "Hava nice love!" (faithful: JP ハヴァ ナイス ラヴ)
- [x] step 0015 - wording - credits Uematsu - fragment - "My work for this game. Please listen to this melody that touches the heart."
- [x] step 0002-0012 - wording - role wraps after "Minister:" - "Minister: Character / Graphics!"

## 2026-10-21 playtest - hanjuku_en.sfc sha1 888a0584b9bf
Evidence: `work/playtest/ev/s_end2/NNNN.png|.sheetK.png|.<state>`, presses in `log.tsv`.

- [x] step 0008 - text - Soft-Boiled Cooking Notes page - word split across lines - "The Last One... Hard-Boile / d God Boiled"
- [x] step 0005 - wording - Boiled scene - redundant - "the strength to stand strong"
