-- AOF2 Rebirth: rastreio frame a frame do leitor de comandos do P1.
-- Serve para comparar neutro x blockstun: se o slot do comando avança e se o
-- especial fica pendente ($218).
-- Gera build/lua/command-trace.csv. Uso no FBNeo: Game > Lua Scripting >
-- New Lua Script Window > Browse > este arquivo > Run. Defenda um golpe e,
-- durante a defesa, faça o comando (ex.: Kohou, -> v v> + soco).
--
-- Campos (registro do jogador P1 = $109280):
--   $40   estado (1 neutro, 3 ataque, 6/7 reação: golpe ou defesa)
--   $A69  flags do quadro (bit 1 = o leitor de comandos roda na reação, $1C47C)
--   $7C   bits 0-3 = 3: o último contato foi defendido ($21872)
--   $270/$271  direções e botões traduzidos (seguros / recém-apertados)
--   $A10 + 4*(cmd - $40)  slot do comando: word = passo atual, byte = prazo
--   $218  especial pendente (bit 9/8/10 = marcas do botão)  $A77 = frames de vida
-- Os slots dos comandos de CMDS (Ryo: $40 Kou'ouken, $46 DESPERATION, $47
-- Kohou) são registrados a cada frame, junto com "leitor": 1 se $1DF7E rodou.
-- Lado: o leitor espelha ←/→ quando -$19E(jogador) != $47C(a5) ($1DFA4);
-- "olha" = bit 0 do $5E do sprite (1 = olhando para a direita).

local CMDS = { 0x40, 0x46, 0x47 }
local P1 = 0x109280
local READER = 0x1DF7E

local script_dir = debug.getinfo(1, "S").source:match("^@?(.*[/\\])") or ""
local out_dir = script_dir .. "..\\..\\build\\lua\\"
os.execute('mkdir "' .. out_dir .. '" 2>nul')
local out = assert(io.open(out_dir .. "command-trace.csv", "w"))
local head = "frame,estado,a69,defendido,dir270,bot270,dir271,bot271,leitor,id19e,lado47c,espelha,olha,x"
for _, c in ipairs(CMDS) do head = head .. string.format(",passo%02X,prazo%02X", c, c) end
out:write(head .. ",pend218,a77,vida,barra\n")

local ran = false
local function reg_a6()
  for _, name in ipairs({ "a6", "m68000.a6" }) do
    local ok, v = pcall(memory.getregister, name)
    if ok and v then return v end
  end
  return nil
end
memory.registerexec(READER, function()
  -- a6 do leitor é o jogador; só conta o P1 (sem leitura de registrador,
  -- conta qualquer chamada: o P2 também roda o leitor)
  local a6 = reg_a6()
  if a6 == nil or a6 % 0x1000000 == P1 then ran = true end
end)

local function slot(c) return P1 + 0xA10 + (c - 0x40) * 4 end

emu.registerafter(function()
  local f = emu.framecount()
  local b270, b271 = memory.readbyte(P1 + 0x270), memory.readbyte(P1 + 0x271)
  local id, side = memory.readword(P1 - 0x19E), memory.readword(0x10847C)
  local sprite = 0x108000 + memory.readbyte(P1 + 3) * 0x100
  local line = string.format("%d,%d,%02X,%d,%X,%X,%X,%X,%d,%04X,%04X,%d,%d,%d", f,
    memory.readbyte(P1 + 0x40), memory.readbyte(P1 + 0xA69),
    (memory.readbyte(P1 + 0x7C) % 16 == 3) and 1 or 0,
    b270 % 16, math.floor(b270 / 16), b271 % 16, math.floor(b271 / 16),
    ran and 1 or 0, id, side, (id ~= side) and 1 or 0,
    memory.readbyte(sprite + 0x5E) % 2, memory.readwordsigned(P1 + 0x10))
  for _, c in ipairs(CMDS) do
    line = line .. string.format(",%04X,%d", memory.readword(slot(c)), memory.readbyte(slot(c) + 2))
  end
  out:write(line .. string.format(",%04X,%d,%d,%d\n", memory.readword(P1 + 0x218),
    memory.readbyte(P1 + 0xA77), memory.readbyte(P1 + 0x6D), memory.readbyte(P1 + 0x224)))
  out:flush()
  ran = false
end)

while true do
  gui.text(4, 4, string.format("TRACE  estado %d  DESP passo %04X", memory.readbyte(P1 + 0x40),
    memory.readword(slot(0x46))))
  emu.frameadvance()
end
