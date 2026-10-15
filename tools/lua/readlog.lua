-- Log each distinct PC that reads CPU range RLO..RHI (first hit per PC), with registers. --var RLO=0x1FCE40 --var RHI=0x1FCF90
local seen = {}
L.on_read(RLO, RHI, function(addr, value)
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  if seen[pc] then return end
  seen[pc] = true
  L.log(string.format("f%d pc=%06X read %06X=%02X A=%04X X=%04X Y=%04X DB=%02X D=%04X", L.frame, pc, addr, value,
    s["cpu.a"], s["cpu.x"], s["cpu.y"], s["cpu.dbr"], s["cpu.d"]))
end)
