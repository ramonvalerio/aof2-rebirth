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
-- O slot do comando CMD (padrão $47 = Kohou do Ryo) é registrado a cada frame,
-- junto com "leitor": 1 se $1DF7E rodou neste frame.

local CMD = 0x47
local P1 = 0x109280
local READER = 0x1DF7E

local script_dir = debug.getinfo(1, "S").source:match("^@?(.*[/\\])") or ""
local out_dir = script_dir .. "..\\..\\build\\lua\\"
os.execute('mkdir "' .. out_dir .. '" 2>nul')
local out = assert(io.open(out_dir .. "command-trace.csv", "w"))
out:write("frame,estado,a69,defendido,dir270,bot270,dir271,bot271,leitor,passo,prazo,espera,pend218,a77\n")

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

local slot = P1 + 0xA10 + (CMD - 0x40) * 4

emu.registerafter(function()
  local f = emu.framecount()
  local b270, b271 = memory.readbyte(P1 + 0x270), memory.readbyte(P1 + 0x271)
  out:write(string.format("%d,%d,%02X,%d,%X,%X,%X,%X,%d,%04X,%d,%d,%04X,%d\n", f,
    memory.readbyte(P1 + 0x40), memory.readbyte(P1 + 0xA69),
    (memory.readbyte(P1 + 0x7C) % 16 == 3) and 1 or 0,
    b270 % 16, math.floor(b270 / 16), b271 % 16, math.floor(b271 / 16),
    ran and 1 or 0, memory.readword(slot), memory.readbyte(slot + 2), memory.readbyte(slot + 3),
    memory.readword(P1 + 0x218), memory.readbyte(P1 + 0xA77)))
  out:flush()
  ran = false
end)

while true do
  gui.text(4, 4, string.format("TRACE cmd %02X  estado %d  leitor %s", CMD,
    memory.readbyte(P1 + 0x40), ran and "sim" or "nao"))
  emu.frameadvance()
end
