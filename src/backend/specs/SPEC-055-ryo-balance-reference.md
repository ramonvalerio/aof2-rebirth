# SPEC-055: Ryo como referência do balanceamento do elenco

- Escopo: auditoria do Ryo, sem alterar dano de outros personagens.
- Fonte: ROM gerada com todos os patches do manifest, em 25/10/2026.
- Status: referência técnica v1; validação de dano real e dos combos pendente.
- Extração: `python tools/damage_audit.py`, após `python tools/build_rom.py`.
- [Tabela completa dos 39 registros](characters/ryo/damage-audit.md).

## Referência aprovada

| Golpe | Acerto esperado na condição de teste | Defesa |
|---|---|---|
| Kou'ouken forte | 16 | 4 |
| Kou'ouken médio | 12 | 2 |
| Kou'ouken fraco | 8 | 2 |
| Kohou forte | 9 por hit, 18 total | 2 por hit, 4 total |
| Kohou fraco | 8, um hit | 2 |

Bases conferidas na ROM final: Kou'ouken 20/15/10 em acerto e 5/3/3 na
defesa; Kohou 11/10 em acerto e 3/2 na defesa. Conferem com SPEC-053/054.
São metas de referência, não dano fixo: a escala nativa permanece ativa.
Não substituir medições por uma multiplicação universal de 0,8.

## Normais: bases atuais auditadas

| Golpe | Base acerto | Base defesa |
|---|---:|---:|
| Soco fraco em pé | 8 | 0 |
| Soco forte perto / longe | 20 / 20 | 0 |
| Uppercut de dois socos | 12 | 0 |
| Soco fraco / forte agachado | 8 / 12 | 0 |
| Soco fraco / forte aéreo | 8 / 12 | 0 |
| Chute fraco em pé | 12 | 0 |
| Chute forte neutro (registro customizado) | 18 | 0 |
| Overhead | 12 | 0 |
| Chute forte para trás | 28 | 0 |
| Chute baixo de dois botões | 12 | 0 |
| Chute fraco / forte agachado | 10 / 20 | 0 |
| Chute fraco / forte aéreo | 12 / 22 | 0 |

O registro do chute forte neutro é escolhido em runtime por hook. O mapa
de comandos sozinho apontaria para o chute forte longe e daria um resultado
errado (28 em vez de 18). A ferramenta inclui o registro customizado.
O valor de dano não basta para comparar normais: startup, recuperação,
alcance, overhead, queda, juggle e cancel precisam compor a avaliação.

## Pendências antes de usar o Ryo como padrão fechado

1. **Kou'ouken aéreo:** tanto soco quanto chute ainda têm bases 32/18/8,
   defesa 7/5/3. O forte aéreo é maior que o terrestre (32 contra 20).
   SPEC-053 só balanceou o terrestre. Avaliar risco/altura/alcance antes
   de decidir se essa diferença é desejada. Versões médias não têm botão
   humano dedicado no mapeamento atual dessas variantes aéreas.
2. **Hien Shippuukyaku:** bases forte/médio/fraco 18/14/20, defesa 4/3/5.
   A fraca tem base por contato maior e startup encurtado; a forte tem
   extras 2 na tabela. É necessário medir quantos hits realmente conectam
   e o total, sem deduzir o total apenas dos extras.
3. **Renbuken:** base 12/0 por contato, quatro golpes na sequência e custo
   dinâmico de 20% (SPEC-017). Soma nominal de quatro bases: 48; o dano
   real depende dos contatos e da escala. Medir total e continuação em combo.
4. **Zanretsuken:** base 2/1 por contato, limite próprio de 19 contatos
   (SPEC-025 corrigida). Soma nominal máxima dessas bases: 38/19 antes
   de escala/bônus. Confirmar total real e soltura, sobretudo na defesa.
5. **SUPER Haoh:** base 68/22 e custo original 96 na tabela. Medir o dano
   final, chip letal e a vulnerabilidade especial da SPEC-051 separadamente.
6. **DESPERATION:** base 100/25, custo 96 e condições próprias. Não usar
   esse valor bruto como dano por soco de um normal ou como total medido.
7. **Arremesso:** registro nativo 38/9; a sequência/handler exige medição
   própria. Não classificar o segundo valor como chip praticável de arremesso.

Nenhum desses danos pendentes foi alterado nesta auditoria. As variantes
de falha $020/$025 não são versões fracas funcionais; o seletor usa a média
quando necessário. Evitar misturá-las à tabela de três versões jogáveis.

## Protocolo de medição e aprovação

Usar mesma ROM e patches, adversário, vida inicial e dificuldade. Registrar
lado/jogador, defesa em pé/agachada, versão, dano por contato e total.
Começar por testes espelhados Ryo contra Ryo; repetir com outros defensores
para identificar diferenças de escala/resistência. Repetir com vida alta,
intermediária e baixa e com P1/P2 trocados.

Script de apoio somente leitura: `tools/lua/damage_audit.lua`. No FBNeo,
abrir em Game > Lua Scripting > New Lua Script Window e executar. Grava
`build/lua/damage-audit.csv` e mostra a última perda de vida. Soma contatos
para obter o total de sequências; uma linha é uma perda de vida por frame,
não garantia de um único hit se dois contatos ocorrerem no mesmo frame.
O nível registrado do atacante pode ter mudado quando um projétil distante
acerta; anotar a versão testada. O script não foi validado ao vivo nesta auditoria.

Confirmar também soco forte e baixo forte → Kou'ouken, Renbuken → continuação,
uppercut → juggle, custo/risco e punição de especiais defendidos. O Ryo só
vira referência final após essas medições e aprovação dos danos pendentes.

## Como comparar os demais personagens

Comparar golpes de função equivalente, incluindo dano total, chip, hits,
startup/recuperação, alcance, queda, invulnerabilidade, custo e capacidade
de combo. Não copiar os mesmos números indiscriminadamente. Alterações de
um personagem têm patch/spec isolados; regras comuns ficam nas globais.
Começar pelo Ryo aprovado e alterar um personagem por vez, preservando
as mecânicas e registrando as mesmas condições de teste.
