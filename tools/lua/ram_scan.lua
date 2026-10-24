-- AOF2 Rebirth: mapa de uso da RAM de trabalho (para achar bytes realmente livres).
-- Para cada byte de $100000-$10F2FF registra se o valor MUDOU em algum momento
-- e o último valor visto. Gera:
--   build/lua/ram-changed.bin  1 bit por byte (1 = mudou durante o jogo)
--   build/lua/ram-values.bin   1 byte por byte (último valor lido)
-- Uso: carregar no FBNeo (Game > Lua Scripting) logo na tela de título e jogar
-- normalmente (seleção, várias lutas, vitória/derrota, continue). O resultado é
-- salvo a cada 10 segundos; espere uns segundos antes de fechar o emulador.

local script_dir = debug.getinfo(1, "S").source:match("^@?(.*[/\\])") or ""
local out_dir = script_dir .. "..\\..\\build\\lua\\"
os.execute('mkdir "' .. out_dir .. '" 2>nul')

local FIRST, LAST = 0x100000, 0x10F2FF
local CHUNK = 0x0800          -- bytes examinados por frame (varre tudo em ~30 frames)
local first_seen, last_seen, changed = {}, {}, {}
local pos, frames = FIRST, 0

local function save()
  local f = io.open(out_dir .. "ram-changed.bin", "wb")
  local g = io.open(out_dir .. "ram-values.bin", "wb")
  if not f or not g then return end
  for base = FIRST, LAST, 8 do
    local byte = 0
    for k = 0, 7 do
      if changed[base + k] then byte = byte + 2 ^ k end
    end
    f:write(string.char(byte))
  end
  for a = FIRST, LAST do g:write(string.char(last_seen[a] or 0)) end
  f:close(); g:close()
end

while true do
  for a = pos, math.min(pos + CHUNK - 1, LAST) do
    local v = memory.readbyte(a)
    local f0 = first_seen[a]
    if f0 == nil then first_seen[a] = v elseif v ~= f0 then changed[a] = true end
    last_seen[a] = v
  end
  pos = pos + CHUNK
  if pos > LAST then pos = FIRST end
  frames = frames + 1
  if frames % 600 == 0 then save() end
  gui.text(4, 4, "RAM SCAN | jogue normalmente | frames " .. frames)
  emu.frameadvance()
end
