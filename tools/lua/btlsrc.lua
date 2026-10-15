-- Battle-text printer ($03:CD1B loop head): log distinct source pointers [$F4] that still point at the ORIGINAL
-- Japanese battle text in bank $17 ($17:9708-$17:FE8E), with the return address on the stack.
local seen = {}
local m = emu.memType.snesMemory
L.on_exec(0x03CD1E, 0x03CD1E, function()
  local p = emu.read(0x7E00F4, m) + emu.read(0x7E00F5, m) * 256
  local b = emu.read(0x7E00F6, m)
  local s = emu.getState()
  local y = s["cpu.y"]
  if b == 0x17 and p >= 0x9708 and y == 0 and not seen[p] then
    seen[p] = true
    local sp = s["cpu.sp"]
    local r1 = emu.read(sp + 1, m) + emu.read(sp + 2, m) * 256
    L.log(string.format("f%d src=17:%04X ret=%04X", L.frame, p, r1))
  end
end)
