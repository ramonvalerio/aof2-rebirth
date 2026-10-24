-- AOF2 Rebirth: registro de quedas (por que o oponente caiu).
-- Grava em build/lua/knockdown-log.csv uma linha por jogador sempre que um
-- dos campos abaixo muda (golpe novo, acerto, reação, hitstop...).
-- Uso no FBNeo: Game > Lua Scripting > New Lua Script Window > Browse > este arquivo > Run.
-- Na tela aparece o nº do frame; anote o frame em que a queda aconteceu.
-- Tecla M (teclado): grava uma linha "MARCA" no arquivo, no frame atual.
--
-- Campos (engenharia reversa, ver specs):
--   $6E   animação do golpe/sequência     $54 do sprite: animação tocando agora
--   $230  comando do golpe atual          $40/$41 estado/subestado (2 = hitstop)
--   $43   contador do hitstop             $247 hits extras restantes
--   $20A  efeito de acerto do golpe       $3F flags (bit 2 = tonto/dizzy)
--   $6D   vida                            $224 barra (byte alto)
--   $268  (provável) pode ser acertado no ar  $7C bits 0-3 (3 = estado no ar, $21872)
--   $10 x  $18 altura  $30 vel. x  $28 vel. y (long)  $38 gravidade

local script_dir = debug.getinfo(1, "S").source:match("^@?(.*[/\\])") or ""
local out_dir = script_dir .. "..\\..\\build\\lua\\"
os.execute('mkdir "' .. out_dir .. '" 2>nul')
local out = assert(io.open(out_dir .. "knockdown-log.csv", "w"))
out:write("frame,player,char,life,anim,sprite_anim,cmd,state,sub,hitstop,extra_hits,effect,flags3f,flags60,spirit,juggle268,c7c,x,height,vx,vy,gravity\n")

local RAM = 0x108000
local PLAYERS = { { "P1", 0x109280 }, { "P2", 0x109380 } }

local function snapshot(p)
  local sprite = RAM + memory.readbyte(p + 3) * 0x100
  return {
    memory.readword(p + 0x62),
    memory.readbyte(p + 0x6D),
    string.format("%04x", memory.readword(p + 0x6E)),
    string.format("%04x", memory.readword(sprite + 0x54)),
    string.format("%02x", memory.readword(p + 0x230)),
    memory.readbyte(p + 0x40),
    memory.readbyte(p + 0x41),
    memory.readbyte(p + 0x43),
    memory.readbyte(p + 0x247),
    string.format("%02x", memory.readbyte(p + 0x20A)),
    string.format("%02x", memory.readbyte(p + 0x3F)),
    string.format("%02x", memory.readbyte(p + 0x60)),
    memory.readbyte(p + 0x224),
    memory.readbyte(p + 0x268),
    string.format("%02x", memory.readbyte(p + 0x7C)),
    memory.readwordsigned(p + 0x10),
    memory.readwordsigned(p + 0x18),
    memory.readwordsigned(p + 0x30),
    memory.readdword(p + 0x28),
    memory.readwordsigned(p + 0x38),
  }
end

local last = {}
local frame = 0
local m_was_down = false

local function on_frame()
  frame = frame + 1
  for _, pl in ipairs(PLAYERS) do
    local name, p = pl[1], pl[2]
    local s = table.concat(snapshot(p), ",")
    if s ~= last[name] then
      out:write(frame, ",", name, ",", s, "\n")
      last[name] = s
    end
  end
  local ok, keys = pcall(input.get)
  if not ok then keys = nil end
  local m_down = keys and (keys.M or keys.m) and true or false
  if m_down and not m_was_down then
    out:write(frame, ",MARCA\n")
    out:flush()
  end
  m_was_down = m_down
  gui.text(4, 4, "QUEDAS | frame " .. frame .. " | M = marcar")
  if frame % 60 == 0 then out:flush() end
end

while true do
  on_frame()
  emu.frameadvance()
end
