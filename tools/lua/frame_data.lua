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
out:write("start_frame,char,anim,move_id,button,startup,active,recovery,total,proj,hit,p2_free,advantage\n")

local push = assert(io.open(out_dir .. "pushback.csv", "w"))
push:write("hit_frame,t,p1_anim,p2_anim,p1_x,p2_x,distance,p1_vx_px,p2_vx_px,p1_attack_box,p2_body_boxes,p2_flag70,p2_health,p1_atk_x1,p1_atk_x2,p1_atk_y1,p1_atk_y2,p2_body_x1,p2_body_x2,p2_body_y1,p2_body_y2,overlap\n")

local RAM = 0x108000
local P1, P2 = 0x109280, 0x109380
local P2_HEALTH = P2 + 0x6D
local PROJ = 0x22A5C
local CHOSEN = 0x1D676          -- especial: versão/força já escolhidas (SPEC-004)
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

-- caixas de corpo do P2 (filhos 2, 3, 4) com caixa ativa
local function body_boxes(p)
  local sprite = RAM + memory.readbyte(p + 3) * 0x100
  local n = 0
  for c = 2, 4 do
    local child = memory.readbyte(sprite + 2 + c)
    if child ~= 0 and memory.readdword(RAM + child * 0x100 + 0x72) ~= 0 then n = n + 1 end
  end
  return n
end

-- recuo: a partir de cada acerto no P2, 60 frames de posição/velocidade/caixas,
-- independente de cancel (continua durante o especial)
-- retângulo de mundo de um filho ($76 esq, $78 dir, $7A cima, $7C baixo; $70 bit0 = ativo)
local function child_rect(p, c)
  local sprite = RAM + memory.readbyte(p + 3) * 0x100
  local child = memory.readbyte(sprite + 2 + c)
  if child == 0 then return nil end
  local o = RAM + child * 0x100
  if memory.readdword(o + 0x72) == 0 then return nil end
  return { memory.readwordsigned(o + 0x76), memory.readwordsigned(o + 0x78),
           memory.readwordsigned(o + 0x7C), memory.readwordsigned(o + 0x7A) }
end

local function union(rects)
  local u = nil
  for _, r in ipairs(rects) do
    if r then
      if not u then u = { r[1], r[2], r[3], r[4] } else
        u[1] = math.min(u[1], r[1]); u[2] = math.max(u[2], r[2])
        u[3] = math.min(u[3], r[3]); u[4] = math.max(u[4], r[4])
      end
    end
  end
  return u
end

local function rect_str(r) return r and string.format("%d,%d,%d,%d", r[1], r[2], r[3], r[4]) or ",,," end

local hit_at, last_health = nil, memory.readbyte(P2_HEALTH)
local function log_pushback(f)
  local h = memory.readbyte(P2_HEALTH)
  if h < last_health and (not hit_at or f - hit_at > 60) then hit_at = f end
  last_health = h
  if hit_at and f - hit_at <= 60 then
    local x1, x2 = memory.readwordsigned(P1 + 0x10), memory.readwordsigned(P2 + 0x10)
    local atk = union({ child_rect(P1, 5), child_rect(P1, 6) })
    local body = union({ child_rect(P2, 2), child_rect(P2, 3), child_rect(P2, 4) })
    local overlap = ""
    if atk and body then
      overlap = (atk[1] <= body[2] and atk[2] >= body[1] and atk[3] <= body[4] and atk[4] >= body[3]) and "1" or "0"
    end
    push:write(string.format("%d,%d,%04X,%04X,%d,%d,%d,%d,%d,%d,%d,%02X,%d", hit_at, f - hit_at,
      memory.readword(P1 + 0x6E), memory.readword(P2 + 0x6E), x1, x2, x2 - x1,
      memory.readwordsigned(P1 + 0x20), memory.readwordsigned(P2 + 0x20),
      attack_box_on(P1) and 1 or 0, body_boxes(P2), memory.readbyte(P2 + 0x70), h)
      .. "," .. rect_str(atk) .. "," .. rect_str(body) .. "," .. overlap .. "\n")
    push:flush()
  end
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
  out:write(string.format("%d,%d,%04X,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n", cur.start, cur.char, cur.anim,
    cur.move_id and string.format("%03X", cur.move_id) or "", cur.button or "", s(first), s(active), s(recovery), s(cur.total), s(cur.proj), s(cur.hit), s(cur.p2_free), s(adv)))
  out:flush()
  status = string.format("anim %04X %s: startup=%s ativo=%s recup=%s total=%s vant=%s",
    cur.anim, cur.button or "", s(first), s(active), s(recovery), s(cur.total), s(adv))
  cur = nil
end

-- botão do especial: marcas da SPEC-004 em $218 do P1 (bit 9 = jogador, bit 8 = forte)
local tag = nil
memory.registerexec(CHOSEN, function()
  local cmd = memory.readword(P1 + 0x218)
  if cmd == 0 then return end
  local button = "barra"
  if math.floor(cmd / 0x200) % 2 == 1 then
    button = (math.floor(cmd / 0x100) % 2 == 1) and "forte" or "fraco"
  end
  tag = { frame = emu.framecount(), button = button, move_id = memory.readword(RAM + 0x10) }
end)

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
    if tag and f - tag.frame <= 2 then
      cur.button, cur.move_id = tag.button, tag.move_id
    end
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

  log_pushback(f)
  gui.text(4, 4, "FRAME DATA | " .. status)
  emu.frameadvance()
end
