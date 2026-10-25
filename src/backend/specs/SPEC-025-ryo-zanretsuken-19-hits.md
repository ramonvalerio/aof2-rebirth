# SPEC-025: Ryo: Zanretsuken com 19 hits

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/characters/ryo/zanretsuken-19-hits` (mecanismo `charlib.multi_hit_block`, SPEC-027)
- **Combina com:** SPEC-013 (contador conta hits com o oponente preso)

## Comportamento desejado

O Zanretsuken acerta **19 socos** e o contador mostra **19 HIT COMBO**.

## Mapa de engenharia reversa

| Item | Valor |
|---|---|
| Comando | `$44` → handler `$1D4DC` → níveis `$01E` (forte), `$01F` (médio) |
| Animação | Seq `$8018`/`$8019` → `$414E` → anim `$14E`: 40 quadros de 2 frames (80 frames), **10 ciclos** de [comando + 3 peças de ataque] |
| Comandos do ciclo | `$DC xx yy` (`$1D3C2`): grava `$26E/$26F` do atacante = posição do oponente preso; `$DD 01` muda o efeito; `$E6` |
| Efeito `$08` (`$217CA`) | 1º acerto: oponente no estado `$19` (preso, reação `$1A`). Já em `$19`, o acerto seguinte não troca a reação |
| Hits extras | Byte 7 do golpe → `$247` (`$1D7C4`); com `$247 ≠ 0` o contato segue o caminho de vários hits (`$1CEC0` → `$1CFA0`) e `$21338` desconta 1 |
| Caixa de ataque | Filhos 5/6 do sprite; depois do acerto ficam com `$70` bit 7 ("já acertou") e só voltam se alguém limpar (SPEC-008) |

**Original:** 1 hit, porque a caixa nunca é rearmada e não há hits extras. O resto da animação só segura o oponente.

## Implementação

- **Dados (`$01E`, `$01F`):** byte 7 (hits extras) `0` → **18**. Dano por soco (bytes 0 e 1) `$28`/`$1E` → **`$02`** (19 × 2 = 38, perto do original).
- **Hook `$1C1DA`** (começo do estado de ataque, hook compartilhado `charlib.ATTACK_STATE`): Ryo com `$230 = $44`, depois do 1º contato (`$21B = 0`) e com `$247 > 0`: limpa o `$70` bit 7 dos filhos 5/6 uma vez por peça (quando o contador do quadro do sprite, `$56`, vale 1). Com `$247` em 0, para de rearmar: 1 + 18 = 19 hits.

## Pendências

- **Soltura:** ao fim, o estado `$19` solta o oponente com uma queda (`$1C8E0`: `$20A = $01`). Se isso contar como mais um hit, o total vira 20. Ajustar os hits extras para 17 nesse caso.
- **Versão fraca:** o 3º nível (`$020`) aponta para outra animação; não foi mudado.
- **Dano:** `$02` por soco é uma estimativa; ajustar se ficar fraco ou forte demais.

## Critérios de aceite

- [ ] Zanretsuken colado: 19 HIT COMBO
- [ ] O oponente fica preso até o fim e cai
- [ ] Dano total parecido com o original

## Correção: dano excessivo e limite de contatos

O usuário relatou dano excessivo intermitente com e sem defesa. Dois
problemas identificados no patch anterior:

- Só bytes 0/1 do golpe tinham sido reduzidos para 2. Bytes 2/3, copiados
  para $207 e usados em contatos defendidos, continuavam 10/8. Agora são
  1/1 nas versões $1E/$1F. É valor base; o motor mantém escala por vida,
  dificuldade e modificadores originais. 19 contatos têm base nominal 38
  em acerto ou 19 na defesa, não um teto absoluto de HP após escala.
- O rearmamento dependia somente de $247. Efeito $08 em $217F8/$21812
  remove retornos da pilha, pulando o decremento $21338 enquanto prende
  o alvo. Isso permite rearmar mais do que os 19 contatos previstos.
  O fim do hitstop também recoloca $56 em 1 ($1CA54), permitindo repetição.

Agora o Ryo reserva o byte $3AA (após som $3A8 e target combo $3A9) como
orçamento de contatos. Inicializa em 19 em SPECIAL_CHOSEN apenas para
$1E/$1F. HIT_SOUND desconta uma unidade por contato, defendido ou não,
antes da reação do defensor. Não depende de $21338. Não rearma no
hitstop nem após esgotar o contador. Uma caixa já enfileirada ou soltura
que conectar após zero tem $71/$248 zerados e o bônus $252 bit 0 limpo,
sem dano extra nem underflow do contador. Não altera vida diretamente.

O helper multi_hit_block ganhou budget opcional; chamadas sem budget
(incluindo Yuri) geram o mesmo código de antes. A duração e a animação
do Zanretsuken, os comandos e os outros golpes não são modificados.
A soltura e o total efetivo do contador visual ainda exigem teste em jogo.

Validação: builds completo/isolado, hooks; simular contatos além do limite,
reinício do golpe e comparar geração do helper para Yuri. No emulador,
repetir forte/fraco com defesa, sem defesa, no canto e após cancel;
confirmar ausência de dano excessivo e total de hits/dano estável.
