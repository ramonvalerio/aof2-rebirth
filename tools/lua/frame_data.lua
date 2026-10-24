-- AOF2 Rebirth: medidor de frame data do P1 (SPEC-007).
-- Grava em build/lua/frame-data.csv uma linha por golpe do P1.
-- Uso no FBNeo: Game > Lua Scripting > New Lua Script Window > Browse > este arquivo > Run.
--
-- Estrutura usada (engenharia reversa):
--   jogador P1 = $109280, P2 = $109380
--   $6E(jogador)  id da animação atual (troca = golpe novo)
--   $A69(jogador) flags do quadro atual (bit 7 = quadro final da animação: golpe/reação acabou)
--   objeto de sprite = $108000 + byte($3 do jogador) * $100
--   filhos do sprite = ids nos bytes $2..$9; filho = $108000 + id * $100
--   caixa do filho = long em $72 (0 = sem caixa); filhos 5 e 6 = caixa de ataque
--   projétil criado em $22A5C
--
-- Colunas (frames contados a partir do 1º frame do golpe = 0):
--   startup      frames antes da 1ª caixa de ataque (1º frame ativo = startup + 1)
--   active       frames com caixa de ataque
--   recovery     frames da última caixa até o P1 poder agir
--   total        duração até o P1 poder agir
--   proj         frame em que o projétil é criado
--   hit          frame em que a vida do P2 caiu
--   p2_free      frame em que o P2 voltou a poder agir
--   advantage    p2_free - total  (+ = P1 age primeiro)

local script_dir = debug.getinfo(1, "S").source:match("^@?(.*[/\\])") or ""
local out_dir = script_dir .. "..\\..\\build\\lua\\"
os.execute('mkdir "' .. out_dir .. '" 2>nul')
local out = assert(io.open(out_dir .. "frame-data.csv", "w"))
out:write("start_frame,char,anim,startup,active,recovery,total,proj,hit,p2_free,advantage\n")

local RAM = 0x108000
local P1, P2 = 0x109280, 0x109380
local P2_HEALTH = P2 + 0x6D
local PROJ = 0x22A5C
local ATTACK_CHILDREN = { 5, 6 }
local MAX_FRAMES = 180

local function anim_ended(p) return memory.readbyte(p + 0xA69) >= 0x80 end

local function attack_box_on(p)
  local sprite = RAM + memory.readbyte(p + 3) * 0x100
  for _, c in ipairs(ATTACK_CHILDREN) do
    local child = memory.readbyte(sprite + 2 + c)
    if child ~= 0 and memory.readdword(RAM + child * 0x100 + 0x72) ~= 0 then return true end
  end
  return false
end

local cur, last_anim = nil, memory.readword(P1 + 0x6E)
local status = "aguardando golpe do P1..."

local function finish()
  if not cur then return end
  local first, lastb = cur.first, cur.last
  local active = first and (lastb - first + 1) or nil
  local recovery = (lastb and cur.total) and (cur.total - lastb - 1) or nil
  local adv = (cur.p2_free and cur.total) and (cur.p2_free - cur.total) or nil
  local function s(v) return v and tostring(v) or "" end
  out:write(string.format("%d,%d,%04X,%s,%s,%s,%s,%s,%s,%s,%s\n", cur.start, cur.char, cur.anim,
    s(first), s(active), s(recovery), s(cur.total), s(cur.proj), s(cur.hit), s(cur.p2_free), s(adv)))
  out:flush()
  status = string.format("anim %04X: startup=%s ativo=%s recup=%s total=%s vant=%s",
    cur.anim, s(first), s(active), s(recovery), s(cur.total), s(adv))
  cur = nil
end

memory.registerexec(PROJ, function()
  if cur and not cur.proj then cur.proj = emu.framecount() - cur.start end
end)

while true do
  local f = emu.framecount()
  local anim = memory.readword(P1 + 0x6E)
  if anim ~= last_anim and not anim_ended(P1) then
    finish()
    cur = { start = f, anim = anim, char = memory.readword(P1 + 0x62),
            health = memory.readbyte(P2_HEALTH), p2_anim = memory.readword(P2 + 0x6E) }
  end
  last_anim = anim

  if cur then
    local t = f - cur.start
    if attack_box_on(P1) then
      cur.first = cur.first or t
      cur.last = t
    end
    if not cur.hit and memory.readbyte(P2_HEALTH) < cur.health then cur.hit = t end
    if not cur.total and t > 0 and anim_ended(P1) then cur.total = t end
    -- P2 troca de animação (reação de hit/block) e depois chega ao quadro final
    if not cur.p2_busy and memory.readword(P2 + 0x6E) ~= cur.p2_anim then cur.p2_busy = true end
    if cur.p2_busy and not cur.p2_free and anim_ended(P2) then cur.p2_free = t end
    if (cur.total and (cur.p2_free or not cur.p2_busy) and t > cur.total + 2) or t > MAX_FRAMES then
      finish()
    end
  end

  gui.text(4, 4, "FRAME DATA | " .. status)
  emu.frameadvance()
end
