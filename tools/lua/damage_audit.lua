-- Auditoria de dano, somente leitura. Nao modifica a RAM do jogo.
-- FBNeo: Game > Lua Scripting > New Lua Script Window > Browse > Run.
-- Saida: build/lua/damage-audit.csv. Cada perda de vida gera uma linha.
local script_dir = debug.getinfo(1, "S").source:match("^@?(.*[/\\])") or ""
local out_dir = script_dir .. "..\\..\\build\\lua\\"
os.execute('mkdir "' .. out_dir .. '" 2>nul')
local out = assert(io.open(out_dir .. "damage-audit.csv", "w"))
out:write("frame,attacker,attacker_char,defender,defender_char,life_before,life_after,damage,guard,contact_cmd,attacker_cmd,attacker_anim,attacker_level,defender_state,damage71,guard_base248\n")
local players = {0x109280, 0x109380}
local previous = {}
local frame, last_line = 0, "DANO | aguardando contato"

while true do
  frame = frame + 1
  for defender, p in ipairs(players) do
    local life = memory.readword(p + 0x6C)
    local before = previous[defender]
    if before and life < before then
      local attacker = 3 - defender
      local a = players[attacker]
      local sprite = 0x108000 + memory.readbyte(a + 3) * 0x100
      local guard = memory.readbyte(p + 0x7C) % 16 == 3 and 1 or 0
      local damage = before - life
      local values = {
        frame, attacker, memory.readword(a + 0x62), defender,
        memory.readword(p + 0x62), before, life, damage, guard,
        string.format("%02X", memory.readword(p + 0xA6A)),
        string.format("%02X", memory.readword(a + 0x230)),
        string.format("%04X", memory.readword(a + 0x6E)),
        memory.readbyte(sprite + 0x5C), memory.readbyte(p + 0x40),
        memory.readbyte(p + 0x71), memory.readbyte(p + 0x248),
      }
      out:write(table.concat(values, ","), "\n")
      out:flush()
      last_line = string.format("P%d -> P%d | %d dano | %s | vida %d -> %d",
        attacker, defender, damage, guard == 1 and "DEFESA" or "ACERTO", before, life)
    end
    previous[defender] = life
  end
  gui.text(4, 4, last_line)
  emu.frameadvance()
end
