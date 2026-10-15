-- Log distinct PCs writing byte value VAL (or VAL2) to WRAM between frames FROM..TO, with registers.
--   --var VAL=0x88 [--var VAL2=0xA3] --var FROM=2200 --var TO=2300
local seen = {}
L.on_write(0x7E0000, 0x7FFFFF, function(addr, value)
  if L.frame < FROM or L.frame > TO then return end
  if value ~= VAL and value ~= (VAL2 or -1) then return end
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  local key = pc * 256 + value
  if seen[key] then return end
  seen[key] = true
  L.log(string.format("f%d pc=%06X wrote %06X=%02X X=%04X Y=%04X DB=%02X D=%04X", L.frame, pc, addr, value,
    s["cpu.x"], s["cpu.y"], s["cpu.dbr"], s["cpu.d"]))
end)
