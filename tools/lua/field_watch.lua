-- AOF2 Rebirth: vigia campos dos registros dos jogadores que mudam raramente.
-- Serve para achar estados como o "rosto machucado": campos que sobem quando o
-- personagem apanha e voltam a zero no início do round.
-- Gera build/lua/field-watch.csv: frame,jogador,offset,antes,depois,vida_p1,vida_p2
-- (no máximo MAX_EVENTS mudanças por byte; campos que mudam toda hora são ignorados)
-- Uso: carregar no FBNeo (Game > Lua Scripting) e jogar uma luta com pelo menos
-- 2 rounds, apanhando até o rosto ficar machucado.

local script_dir = debug.getinfo(1, "S").source:match("^@?(.*[/\\])") or ""
local out_dir = script_dir .. "..\\..\\build\\lua\\"
os.execute('mkdir "' .. out_dir .. '" 2>nul')
local out = assert(io.open(out_dir .. "field-watch.csv", "w"))
out:write("frame,player,offset,before,after,life_p1,life_p2\n")

local PLAYERS = { { name = "P1", base = 0x109280 }, { name = "P2", base = 0x109380 } }
local SIZE = 0xA80          -- campos do registro do jogador (até $A7F)
local MAX_EVENTS = 24
local last, events = {}, {}

for _, p in ipairs(PLAYERS) do
  last[p.name], events[p.name] = {}, {}
  for o = 0, SIZE - 1 do
    last[p.name][o] = memory.readbyte(p.base + o)
    events[p.name][o] = 0
  end
end

local frames = 0
while true do
  local f = emu.framecount()
  local l1, l2 = memory.readword(0x109280 + 0x6C), memory.readword(0x109380 + 0x6C)
  for _, p in ipairs(PLAYERS) do
    local lp, ev = last[p.name], events[p.name]
    for o = 0, SIZE - 1 do
      local v = memory.readbyte(p.base + o)
      if v ~= lp[o] then
        if ev[o] < MAX_EVENTS then
          out:write(string.format("%d,%s,%03X,%02X,%02X,%d,%d\n", f, p.name, o, lp[o], v, l1, l2))
        end
        ev[o] = ev[o] + 1
        lp[o] = v
      end
    end
  end
  frames = frames + 1
  if frames % 60 == 0 then out:flush() end
  gui.text(4, 4, "FIELD WATCH | frames " .. frames)
  emu.frameadvance()
end
