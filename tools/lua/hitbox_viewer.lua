-- AOF2 Rebirth: visualizador de caixas e frame data ao vivo (P1 e P2).
-- Uso no FBNeo: Game > Lua Scripting > New Lua Script Window > Browse > este arquivo > Run.
--
-- Cores das caixas:
--   azul      corpo / hurtbox (filhos 2, 3, 4)
--   vermelho  ataque / hitbox ativa (filhos 5, 6)
--   cinza     ataque que já acertou ($70 bit 7: não acerta de novo até ser rearmada)
--   amarelo   outras caixas do personagem (filhos 0, 1, 7)
--   laranja   caixas de objetos fora dos jogadores (projéteis, efeitos)
--   branco    cruz = posição do jogador ($10, $14)
--
-- Barra de frames (últimos 80 frames, o mais novo à direita), por jogador:
--   azul escuro  livre (neutro / pode agir)
--   verde        startup (golpe começou, sem caixa de ataque ainda)
--   vermelho     ativo (caixa de ataque presente)
--   azul claro   recovery (depois da última caixa, até a animação acabar)
--   amarelo      apanhando / defendendo (hitstun / blockstun)
--   roxo         hitstop (congelado no contato)
--
-- Teclas (no teclado do PC):
--   F1  liga/desliga as caixas      F2  liga/desliga o painel de dados
--   F3  liga/desliga a barra de frames
--   setas  ajuste fino da posição das caixas na tela (se ficarem deslocadas)
--
-- Estrutura usada (engenharia reversa, ver SPEC-007 / SPEC-008):
--   jogador P1 = $109280, P2 = $109380; objeto n = $108000 + n * $100
--   câmera: X = word $1080A0, Y = word $1080A4 ($4940: tela = mundo - câmera)
--   tela: x = X - câmera X; y = 224 - (Y - câmera Y)   (Y do mundo cresce para cima)
--   sprite do jogador = objeto byte($3); filhos = ids nos bytes $2..$9 do sprite
--   caixa do filho: $72 long (0 = sem caixa), retângulo $76 esq, $78 dir,
--   $7A cima, $7C baixo; $70 bit 0 = ligada, bit 7 = já acertou
--   $6E anim, $A69 >= $80 = quadro final, $230 golpe atual, $62 personagem,
--   $6D vida, $224 barra de espírito, $21B = 0 depois do contato,
--   $247 hits extras, $41/$43 subestado e contador (2 = hitstop)

local RAM = 0x108000
local CAM_X, CAM_Y = 0x1080A0, 0x1080A4
local PLAYERS = {
  { name = "P1", base = 0x109280, panel_x = 4 },
  { name = "P2", base = 0x109380, panel_x = 200 },
}
local NAMES = { "Ryo", "Robert", "Eiji", "Jack", "Lee", "King", "Micky", "John",
                "Mr.Big", "Takuma", "Yuri", "Temjin", "Geese" }

local COLOR = {
  hurt     = { fill = 0x3070FF40, line = 0x3070FFFF },
  attack   = { fill = 0xFF202050, line = 0xFF2020FF },
  spent    = { fill = 0x80808040, line = 0xA0A0A0FF },
  other    = { fill = 0xFFE02030, line = 0xFFE020FF },
  object   = { fill = 0xFF900040, line = 0xFF9000FF },
}
local PHASE_COLOR = {
  free     = 0x203060FF,
  startup  = 0x20C040FF,
  active   = 0xFF2020FF,
  recovery = 0x60B0FFFF,
  stun     = 0xFFE020FF,
  hitstop  = 0xB040FFFF,
}
local BAR_LEN = 80

local show_boxes, show_panel, show_bar = true, true, true
local adj_x, adj_y = 0, 0

local function rb(a) return memory.readbyte(a) end
local function rw(a) return memory.readword(a) end
local function rws(a) return memory.readwordsigned(a) end

local function to_screen(x, y)
  return x - rws(CAM_X) + adj_x, 224 - (y - rws(CAM_Y)) + adj_y
end

local function sprite_of(p) return RAM + rb(p + 3) * 0x100 end

-- retângulo de tela de um objeto com caixa, ou nil
local function box_of(o)
  if rb(o + 0x70) % 2 == 0 or memory.readdword(o + 0x72) == 0 then return nil end
  local x1, y1 = to_screen(rws(o + 0x76), rws(o + 0x7A))
  local x2, y2 = to_screen(rws(o + 0x78), rws(o + 0x7C))
  return { math.min(x1, x2), math.min(y1, y2), math.max(x1, x2), math.max(y1, y2),
           spent = rb(o + 0x70) >= 0x80 }
end

-- filhos do jogador: { [n] = id do objeto }
local function children(p)
  local sprite, out = sprite_of(p), {}
  for c = 0, 7 do
    local id = rb(sprite + 2 + c)
    if id ~= 0 then out[c] = id end
  end
  return out
end

local function has_attack_box(p)
  local ch = children(p)
  for _, c in ipairs({ 5, 6 }) do
    if ch[c] and box_of(RAM + ch[c] * 0x100) then return true end
  end
  return false
end

local function anim_ended(p) return rb(p + 0xA69) >= 0x80 end
local function in_hitstop(p) return rb(p + 0x41) == 2 and rb(p + 0x43) > 0 end

-- ---------------------------------------------------------------- frame data
-- estado por jogador: fase do frame atual, contadores do golpe atual e o
-- resumo do último golpe (startup/ativo/recovery/vantagem)
local st = {}
for i, P in ipairs(PLAYERS) do
  st[i] = { bar = {}, last_anim = rw(P.base + 0x6E), move = nil, summary = "",
            last_health = rb(P.base + 0x6D), stunned = false }
end

local function other(i) return i == 1 and 2 or 1 end

local function update(i)
  local P, s = PLAYERS[i], st[i]
  local p = P.base
  local anim = rw(p + 0x6E)
  local health = rb(p + 0x6D)
  local attacking = has_attack_box(p)

  -- apanhou: vida caiu ou entrou em hitstop sem caixa de ataque própria
  if health < s.last_health then s.stunned = true end
  s.last_health = health

  if anim ~= s.last_anim and not anim_ended(p) then
    -- animação nova: golpe novo (se não está apanhando)
    if s.move and not s.move.closed then s.move.closed = true end
    if not s.stunned then
      s.move = { anim = anim, id = rw(p + 0x230), t = 0, startup = nil, last = nil }
    end
  end
  s.last_anim = anim

  local phase = "free"
  local m = s.move
  if in_hitstop(p) then
    phase = "hitstop"
  elseif s.stunned then
    phase = "stun"
    if anim_ended(p) then s.stunned = false end
  elseif m and not m.closed then
    m.t = m.t + 1
    if attacking then
      m.startup = m.startup or (m.t - 1)
      m.last = m.t
      phase = "active"
    elseif m.last then
      phase = "recovery"
    else
      phase = "startup"
    end
    if anim_ended(p) then
      m.closed = true
      m.total = m.t
      if m.startup then
        m.active = m.last - m.startup
        m.recovery = m.total - m.last
        s.summary = string.format("startup %d  ativo %d  recup %d  total %d",
          m.startup, m.active, m.recovery, m.total)
        s.pending_adv = { at = emu.framecount() }
      end
      phase = "free"
    end
  end

  -- vantagem: frames entre este jogador ficar livre e o outro ficar livre
  local o = st[other(i)]
  if s.pending_adv and o.stunned == false and not in_hitstop(PLAYERS[other(i)].base)
     and (not o.move or o.move.closed) then
    local adv = s.pending_adv.at - emu.framecount()
    s.summary = s.summary .. string.format("  vant %+d", adv)
    s.pending_adv = nil
  elseif s.pending_adv and emu.framecount() - s.pending_adv.at > 120 then
    s.pending_adv = nil
  end

  table.insert(s.bar, phase)
  if #s.bar > BAR_LEN then table.remove(s.bar, 1) end
  s.phase = phase
end

-- ---------------------------------------------------------------- desenho
local function draw_rect(r, c)
  gui.box(r[1], r[2], r[3], r[4], c.fill, c.line)
end

local function draw_player_boxes(p)
  local ch = children(p)
  for c = 0, 7 do
    if ch[c] then
      local r = box_of(RAM + ch[c] * 0x100)
      if r then
        local color
        if c >= 2 and c <= 4 then color = COLOR.hurt
        elseif c == 5 or c == 6 then color = r.spent and COLOR.spent or COLOR.attack
        else color = COLOR.other end
        draw_rect(r, color)
      end
    end
  end
  local x, y = to_screen(rws(p + 0x10), rws(p + 0x14))
  gui.line(x - 4, y, x + 4, y, 0xFFFFFFFF)
  gui.line(x, y - 4, x, y + 4, 0xFFFFFFFF)
end

-- caixas de objetos que não são filhos dos jogadores (projéteis etc.)
local function draw_objects()
  local mine = {}
  for _, P in ipairs(PLAYERS) do
    mine[rb(P.base + 3)] = true
    for _, id in pairs(children(P.base)) do mine[id] = true end
  end
  for id = 0x10, 0xFF do
    if not mine[id] then
      local o = RAM + id * 0x100
      if rw(o) ~= 0 then
        local r = box_of(o)
        if r and r[3] - r[1] < 320 and r[4] - r[2] < 240 then draw_rect(r, COLOR.object) end
      end
    end
  end
end

local function draw_panel(i)
  local P, s = PLAYERS[i], st[i]
  local p = P.base
  local x = P.panel_x
  local char = rw(p + 0x62)
  local lines = {
    string.format("%s %s  vida %d  barra %d", P.name, NAMES[char] or ("#" .. char),
      rb(p + 0x6D), rw(p + 0x224)),
    string.format("anim %04X  golpe %03X  fase %s", rw(p + 0x6E), rw(p + 0x230), s.phase or "-"),
    string.format("sub %02X cont %02X  contato %s  hits+ %d", rb(p + 0x41), rb(p + 0x43),
      rb(p + 0x21B) == 0 and "sim" or "nao", rb(p + 0x247)),
  }
  if s.move and not s.move.closed then
    lines[#lines + 1] = string.format("frame %d", s.move.t)
  end
  if s.summary ~= "" then lines[#lines + 1] = s.summary end
  for n, l in ipairs(lines) do gui.text(x, 8 + (n - 1) * 8, l, 0xFFFFFFFF) end
end

local function draw_bar(i)
  local s = st[i]
  local y = 200 + (i - 1) * 7
  local x0 = 160 - BAR_LEN * 2
  gui.text(x0 - 14, y - 1, PLAYERS[i].name, 0xFFFFFFFF)
  for n, ph in ipairs(s.bar) do
    local x = x0 + (n - 1) * 4
    gui.box(x, y, x + 2, y + 4, PHASE_COLOR[ph], PHASE_COLOR[ph])
  end
end

local function draw_legend()
  local items = { { "corpo", COLOR.hurt.line }, { "ataque", COLOR.attack.line },
                  { "ja acertou", COLOR.spent.line }, { "outra", COLOR.other.line },
                  { "objeto", COLOR.object.line } }
  local x = 4
  for _, it in ipairs(items) do
    gui.box(x, 216, x + 4, 220, it[2], it[2])
    gui.text(x + 6, 215, it[1], 0xFFFFFFFF)
    x = x + 8 + #it[1] * 4 + 6
  end
end

-- ---------------------------------------------------------------- teclas
local prev_keys = {}
local function pressed(keys, k) return keys[k] and not prev_keys[k] end

local function handle_keys()
  local keys = input.get()
  if pressed(keys, "F1") then show_boxes = not show_boxes end
  if pressed(keys, "F2") then show_panel = not show_panel end
  if pressed(keys, "F3") then show_bar = not show_bar end
  if pressed(keys, "left") then adj_x = adj_x - 1 end
  if pressed(keys, "right") then adj_x = adj_x + 1 end
  if pressed(keys, "up") then adj_y = adj_y - 1 end
  if pressed(keys, "down") then adj_y = adj_y + 1 end
  prev_keys = keys
end

-- jogadores válidos: o sprite do jogador aponta para um objeto em uso
local function in_fight()
  for _, P in ipairs(PLAYERS) do
    local c = rw(P.base + 0x62)
    if c < 1 or c > 13 or rb(P.base + 3) == 0 then return false end
  end
  return true
end

emu.registerafter(function()
  if not in_fight() then return end
  for i = 1, #PLAYERS do update(i) end
end)

gui.register(function()
  handle_keys()
  if not in_fight() then return end
  if show_boxes then
    draw_objects()
    for _, P in ipairs(PLAYERS) do draw_player_boxes(P.base) end
    draw_legend()
  end
  if show_panel then
    for i = 1, #PLAYERS do draw_panel(i) end
    if adj_x ~= 0 or adj_y ~= 0 then
      gui.text(120, 190, string.format("ajuste %+d,%+d", adj_x, adj_y), 0xFFFF00FF)
    end
  end
  if show_bar then
    for i = 1, #PLAYERS do draw_bar(i) end
  end
end)

while true do emu.frameadvance() end
