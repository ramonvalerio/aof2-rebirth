-- AOF2 Rebirth: rastreio dos 5 pontos de execução do comando $48
-- (Mr. Karate / Takuma com START — Kohou).
--
-- Registra um breakpoint em cada ponto e grava build/lua/karate-kohou-trace.csv.
-- Uso no FBNeo: Game > Lua Scripting > New Lua Script Window > Browse > Run.
-- Selecione Takuma com START (P1) e execute o Kohou (↓↘→ + soco).
--
-- Pontos monitorados:
--   P1  $01DFC2  command_row: carrega linha de comandos do personagem
--   P2  $01E062  CMD_STEP: compara um passo da lista; monitora slot $48
--   P3  $01E0E0  keep_haoh: filtro do haoh-easy-input (pré-dispatch)
--   P4  $0F5DE2  complete: bloco karate-kohou — detecta $48 do Mr. Karate
--   P5  $01E102  grava $218=$48 (comando confirmado)
--   P6  $0F5E16  dispatch: chama handler de especial com golpe $023+força
--
-- Campos por linha:
--   frame, ponto, $62(char), $276(cor), $3DA(flag), d5(cmd), d0,
--   $218(pendente), $A77(vida cmd), $40(estado)

local P1_BASE  = 0x109280
local P2_BASE  = 0x109380

local POINTS = {
  { addr = 0x01DFC2, label = "P1_command_row" },
  { addr = 0x01E062, label = "P2_cmd_step"    },
  { addr = 0x01E0E0, label = "P3_keep_haoh"   },
  { addr = 0x0F5DE2, label = "P4_complete"    },
  { addr = 0x01E102, label = "P5_grava218"    },
  { addr = 0x0F5E16, label = "P6_dispatch"    },
}

local script_dir = debug.getinfo(1, "S").source:match("^@?(.*[/\\])") or ""
local out_dir = script_dir .. "..\\..\\build\\lua\\"
os.execute('mkdir "' .. out_dir .. '" 2>nul')
local out = assert(io.open(out_dir .. "karate-kohou-trace.csv", "w"))
out:write("frame,ponto,char62,cor276,flag3DA,cmd_d5,d0,pend218,a77,estado\n")

local function reg(name)
  local ok, v = pcall(memory.getregister, name)
  return (ok and v) or 0
end

local function a6_is_p1(a6)
  return a6 % 0x1000000 == P1_BASE
end

local hits = 0

for _, pt in ipairs(POINTS) do
  memory.registerexec(pt.addr, function()
    local a6 = reg("a6")
    if not a6_is_p1(a6) then return end

    local base = a6 % 0x1000000
    local char  = memory.readword(base + 0x62)
    local cor   = memory.readword(base + 0x276)
    local flag  = memory.readbyte(base + 0x3DA)
    local d5    = reg("d5") % 0x10000
    local d0    = reg("d0") % 0x10000
    local pend  = memory.readword(base + 0x218)
    local a77   = memory.readbyte(base + 0xA77)
    local est   = memory.readbyte(base + 0x40)

    local line = string.format("%d,%s,%d,%d,%d,%04X,%04X,%04X,%d,%d\n",
      emu.framecount(), pt.label,
      char, cor, flag, d5, d0, pend, a77, est)
    out:write(line)
    out:flush()
    hits = hits + 1
  end)
end

while true do
  gui.text(4, 4, string.format("$48 TRACE  hits=%d  char=%d  $218=%04X  estado=%d",
    hits,
    memory.readword(P1_BASE + 0x62),
    memory.readword(P1_BASE + 0x218),
    memory.readbyte(P1_BASE + 0x40)))
  emu.frameadvance()
end
