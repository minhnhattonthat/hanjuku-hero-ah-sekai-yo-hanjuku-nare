-- Log each battle-message fetch ($03:CCE5): frame and message index $E0 (16-bit).
L.on_exec(0x03CCE5, 0x03CCE5, function()
  local lo = emu.read(0x7E00E0, emu.memType.snesMemory)
  local hi = emu.read(0x7E00E1, emu.memType.snesMemory)
  L.log(string.format("f%d E0=%04X", L.frame, hi * 256 + lo))
end)
