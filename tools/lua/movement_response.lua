-- Mede resposta de andar/pular. Somente leitura; nao altera RAM ou input.
-- FBNeo: Game > Lua Scripting > New Lua Script Window > Browse > Run.
local script_dir = debug.getinfo(1, "S").source:match("^@?(.*[/\\])") or ""
local dir = script_dir .. "..\\..\\build\\lua\\"
os.execute('mkdir "' .. dir .. '" 2>nul')
local out = assert(io.open(dir .. "movement-response.csv", "w"))
out:write("frame,player,held,translated,x16,height16,vx16,vy16,state,sub,anim,frame_flags,event,response_frames,dash_ready,dash_window,dash_starting,dash_scanned,landing_flags\n")
local players, previous, pending, status = {0x109280, 0x109380}, {}, {}, {}
local frame = 0
local function signed32(address)
  local n = memory.readdword(address)
  return n >= 2147483648 and n - 4294967296 or n
end
local function has(n, bit) return math.floor(n / 2 ^ bit) % 2 == 1 end
while true do
  frame = frame + 1
  for i, p in ipairs(players) do
    local held = memory.readbyte(p + 0x68) % 16
    local x, height = signed32(p + 0x10), signed32(p + 0x18)
    local vx, vy = signed32(p + 0x20), signed32(p + 0x28)
    local state, sub = memory.readbyte(p + 0x40), memory.readbyte(p + 0x41)
    local old, event, elapsed = previous[i], "", ""
    -- Registra tambem tentativas bloqueadas; o estado mostra se podia agir.
    if old and held ~= old.held then
      if has(held, 0) and not has(old.held, 0) then
        pending[i] = {kind="jump", start=frame, x=old.x}
        event = "INPUT_JUMP"
      elseif not has(held, 0) and not has(held, 1) and (held == 4 or held == 8) then
        pending[i] = {kind=held == 8 and "right" or "left", start=frame, x=old.x}
        event = "INPUT_WALK_OR_TURN"
      end
    end
    local request = pending[i]
    if request then
      local moved = request.kind == "jump" and height > 0
        or request.kind == "right" and x > request.x
        or request.kind == "left" and x < request.x
      if moved then
        elapsed = frame - request.start
        event = event .. ":MOVED"
        status[i] = request.kind .. " | " .. elapsed .. " frames ate deslocar"
        pending[i] = nil
      elseif frame - request.start >= 30 then
        event = event .. ":BLOCKED_OR_TIMEOUT"
        status[i] = "Sem deslocamento em 30 frames; conferir estado"
        pending[i] = nil
      end
    end
    out:write(table.concat({frame, i, held, memory.readbyte(p + 0x270), x, height,
      vx, vy, state, sub, string.format("%04X", memory.readword(p + 0x6E)),
      string.format("%02X", memory.readbyte(p + 0xA69)), event, elapsed, memory.readbyte(p + 0x3AB), memory.readbyte(p + 0x3AC),
      memory.readbyte(p + 0x3AD), memory.readbyte(p + 0x3AE),
      memory.readbyte(p + 0xA68)}, ","), "\n")
    gui.text(4, 4 + (i - 1) * 10, "P" .. i .. " | " .. (status[i] or "aguardando direcional"))
    previous[i] = {held=held, x=x}
  end
  if frame % 60 == 0 then out:flush() end
  emu.frameadvance()
end
