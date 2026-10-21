-- Episode title card for any episode: run from a state just before the episode 1 card
-- (work/playtest/s_boot/0040.mss) with --var EP=9; sets the episode number $0308 before the card is built.
L.on_frame(function()
  if L.frame < 45 then emu.write(0x7E0308, EP or 1, emu.memType.snesMemory) end
end)
