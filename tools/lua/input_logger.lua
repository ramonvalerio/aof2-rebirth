-- AOF2 Rebirth: gravador de input para diagnóstico (SPEC-002).
-- Grava em build/lua/input-log.csv, um registro por frame em que algo muda.
-- Uso no FBNeo: Game > Lua Scripting > New Lua Script Window > Browse > este arquivo > Run.

local script_dir = debug.getinfo(1, "S").source:match("^@?(.*[/\\])") or ""
local out_dir = script_dir .. "..\\..\\build\\lua\\"
os.execute('mkdir "' .. out_dir .. '" 2>nul')
local log_path = out_dir .. "input-log.csv"
local log = assert(io.open(log_path, "w"))

-- Endereços (ver SPEC-002). Jogador: P1 em $109280, P2 em $109380 (objeto de input em $109080/$109180).
local PLAYERS = {
  { name = "P1", base = 0x109280 },
  { name = "P2", base = 0x109380 },
}
local HOOK_ADDR = 0x1D87C        -- rotina original de input (patch: jmp)
local PATCH_ADDR = 0x0FE000      -- rotina nova do patch
local START_ADDR = 0x10832B      -- START recém-pressionado (a5+$32B)

-- Confirma se a P-ROM carregada é a do hack ($4EF9 = jmp).
local hook_word = memory.readword(HOOK_ADDR)
local hack_loaded = (hook_word == 0x4EF9)

-- Conta quantas vezes o jogo executa cada rotina por frame.
local calls = { hook = 0, patch = 0 }
if memory.registerexec then
  memory.registerexec(HOOK_ADDR, function() calls.hook = calls.hook + 1 end)
  memory.registerexec(PATCH_ADDR, function() calls.patch = calls.patch + 1 end)
end

log:write(string.format("# rom=%s hook_word=%04X hack_loaded=%s\n",
  tostring(emu.romname and emu.romname() or "?"), hook_word, tostring(hack_loaded)))
log:write("frame,joypad,hook_calls,patch_calls,start,"
  .. "p1_68_held,p1_69_press,p1_270_fire,p1_271_flags,p1_272_pend,p1_273_tmr,"
  .. "p2_68_held,p2_69_press,p2_270_fire,p2_271_flags,p2_272_pend,p2_273_tmr,"
  .. "p1_char,p1_height,p1_xvel,p1_facing,p1_air\n")

-- Especiais (SPEC-004): eventos gravados no instante em que o código executa.
--   DETECT  $1E10C  comando acabou de ser gravado em $218 (com as marcas bit9/bit8)
--   LEVEL   $1D548  entrada da escolha de nível (hook); $10(a5) = id base
--   CHOSEN  $1D676  nível/id escolhidos; $5C(a4) = nível, $10(a5) = id final
--   PROJ    $22A5C  criação do projétil; $23F = barra usada para o tamanho
-- O FBNeo não expõe os registradores ao Lua, então os campos são lidos do P1.
local A5 = 0x108000
local function special_event(tag)
  return function()
    local b = PLAYERS[1].base
    log:write(string.format("#EV %s frame=%d P1 cmd218=%04X id=%04X gauge224=%02X snap23f=%02X p270=%02X p271=%02X\n",
      tag, emu.framecount(),
      memory.readword(b + 0x218), memory.readword(A5 + 0x10),
      memory.readbyte(b + 0x224), memory.readbyte(b + 0x23F),
      memory.readbyte(b + 0x270), memory.readbyte(b + 0x271)))
    log:flush()
  end
end
if memory.registerexec then
  memory.registerexec(0x1E10C, special_event("DETECT"))
  memory.registerexec(0x1D548, special_event("LEVEL"))
  memory.registerexec(0x1D676, special_event("CHOSEN"))
  memory.registerexec(0x22A5C, special_event("PROJ"))
end

-- Física do P1 (SPEC-006): personagem $62, altura $18, vel. horizontal $30,
-- direção $5E bit0, no ar $60 bit4. Registrado a cada frame em que o P1 está no ar.
local function p1_physics()
  local b = PLAYERS[1].base
  return string.format("%d,%d,%d,%d,%d",
    memory.readword(b + 0x62), memory.readwordsigned(b + 0x18),
    memory.readwordsigned(b + 0x30), memory.readbyte(b + 0x5E) % 2,
    math.floor(memory.readbyte(b + 0x60) / 16) % 2)
end

local function pressed_buttons()
  local names = {}
  for k, v in pairs(joypad.get()) do
    if v == true or v == 1 then names[#names + 1] = k end
  end
  table.sort(names)
  return table.concat(names, "|")
end

local function player_fields(p)
  local b = p.base
  return string.format("%02X,%02X,%02X,%02X,%02X,%02X",
    memory.readbyte(b + 0x68), memory.readbyte(b + 0x69),
    memory.readbyte(b + 0x270), memory.readbyte(b + 0x271),
    memory.readbyte(b + 0x272), memory.readbyte(b + 0x273))
end

local last = ""
local lines = 0
while true do
  local pads = pressed_buttons()
  local phys = p1_physics()
  local state = string.format("%s,%d,%d,%02X,%s,%s,%s",
    pads, calls.hook, calls.patch, memory.readbyte(START_ADDR),
    player_fields(PLAYERS[1]), player_fields(PLAYERS[2]), phys)
  -- só registra quando algo muda (o contador de chamadas fica fora da comparação);
  -- a física entra na comparação, então todo frame no ar é registrado
  local key = pads .. player_fields(PLAYERS[1]) .. player_fields(PLAYERS[2]) .. phys
  if key ~= last then
    log:write(emu.framecount() .. "," .. state .. "\n")
    log:flush()
    last = key
    lines = lines + 1
  end
  gui.text(4, 4, string.format("REC %s | hack=%s | linhas=%d | hook/frame=%d",
    log_path:match("[^\\/]+$"), hack_loaded and "SIM" or "NAO", lines, calls.hook))
  calls.hook, calls.patch = 0, 0
  emu.frameadvance()
end
