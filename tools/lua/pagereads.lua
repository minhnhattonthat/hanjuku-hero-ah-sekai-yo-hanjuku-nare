-- Log distinct (PC, ROM page) reads inside CPU ranges listed in RANGES (e.g. "0x178000-0x17FFFF,0x1FB000-0x1FFFFF").
-- Line: f<frame> pc=PPPPPP page=AAAA00 first=ADDR Y=.. X=.. DB=..
local seen = {}
for lo, hi in string.gmatch(RANGES, "(0x%x+)%-(0x%x+)") do
  L.on_read(tonumber(lo), tonumber(hi), function(addr, value)
    local s = emu.getState()
    local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
    local key = pc * 65536 + ((addr >> 8) & 0xFFFF)
    if seen[key] then return end
    seen[key] = true
    L.log(string.format("f%d pc=%06X page=%06X first=%06X X=%04X Y=%04X DB=%02X", L.frame, pc, addr & 0xFFFF00, addr,
      s["cpu.x"], s["cpu.y"], s["cpu.dbr"]))
  end)
end
