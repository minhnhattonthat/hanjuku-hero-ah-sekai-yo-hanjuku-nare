-- Warp: replace the first event script the game loads after boot (the opening crawl, id D3, ~frame 935 with
-- tools/routes/boot.txt) by script SCENE (0x00-0xFF). Hooks the loader at $04:8871, which reads $08D0.
--   emu.py ROM --route tools/routes/boot.txt --script tools/debug/warp.lua --var SCENE=0x34 --frames 3000 --mash 40
-- Optional: MSG=0xNN runs menu/system message NN (table $1F:B663) instead (not yet wired).
local done = false
L.on_exec(0x048871, 0x048871, function()
  if done or SCENE == nil then return end
  done = true
  emu.write(0x7E08D0, SCENE, emu.memType.snesMemory)
  L.log(string.format("warp: script %02X at frame %d", SCENE, L.frame))
end)
