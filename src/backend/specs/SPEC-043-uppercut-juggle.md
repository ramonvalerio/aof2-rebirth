# SPEC-043: Uppercut anti-aéreo com continuação de combo

- **Status:** Implementado; validação de jogabilidade pendente no emulador.
- **Patch global:** `patches/global/uppercut-juggle`.

## Comportamento

O uppercut de soco fraco + soco forte (C+D no layout atual), ao acertar
um adversário no ar, lança o defensor verticalmente e o mantém vulnerável
ao golpe seguinte. Substitui a queda alta com grito por poses de impacto
aéreo sem comando de voz. Vale para todos os personagens, incluindo chefes.

O efeito só começa contra alvo vivo, acima do chão, fora de tontura e
fora de defesa. Acertos no chão, KO, outros golpes e o último hit do
Renbuken seguem as regras dos seus patches. O uppercut é identificado pelo
comando ($24 ou $26), não pela animação compartilhada com o Renbuken.

## Implementação

Hook em `$21344` antes do despacho de efeitos. No caminho original, repõe
`moveq #0,d0 / bclr #7,$24B(a6)` e retorna a `$2134C`.
No juggle, remove os dois retornos da pilha, como os efeitos especiais do
jogo (por exemplo `$217F8`), chama `$20604` com reação aérea `$21` e troca
a animação por uma cópia própria. Evita o segundo despacho via `$205F2`.

Animações `$781–$78F`, originalmente vazias: três poses de impacto aéreo
por personagem, com durações 36+3+3 frames e quadro final. São dados novos;
as animações de outros golpes não são alteradas. As peças vêm das reações
`$21` da tabela `$20662`, incluindo Mr. Big e Geese (14/15).

Hook em `$1C520` mantém a reação depois do fim da animação enquanto o alvo
está vivo, acima do chão e com uma das animações `$781–$78F`. Executa a
física original `$1C6CA` a cada frame, permitindo a aterrissagem. Não libera
controle no ar só porque os 42 frames acabaram. Outro acerto troca a
animação e passa a aplicar a reação do novo golpe; ao tocar o chão, segue
o encerramento original. A identificação usa `$6E`, sem adicionar RAM.

Campos existentes do defensor usados; nenhum campo livre novo:

| Campo | Uso |
|---|---|
| `$6E` | Animação própria `$780 + personagem` |
| `$3F` bit 7, `$70` bits 7/0 | Limpos para tirar queda/invulnerabilidade |
| `$60` bit 4 | Marca de estado aéreo |
| `$268` | 1, como no efeito `$0B` do Kohou; inibe desvios de reação |
| `$20`, `$30`, `$34` | Movimento horizontal e atrito zerados |
| `$28` jogador e sprite | Velocidade vertical inicial +6 em 16.16 |
| `$38` | Gravidade -0,5 por frame (`$FF80`, convertida pelo motor) |
| `$24B` | Efeito consumido |

A altura inicial é preservada. A janela real depende da altura do acerto,
alcance, recuperação do atacante e do próximo golpe. Não garante que todos
os golpes alcancem o alvo. O patch de special cancel existente pode ajudar
a emendar um especial; o patch novo também pode ser selecionado sozinho.

## Validação

### Correção: ataques bloqueados depois de voltar ao neutro

O retorno do juggle pelo fim da reação ($1C520) não atravessava a rotina
normal de aterrissagem $1C374, que limpa $240 e $60 bit 7. O executor
$1D808 recusa ataques enquanto esse bit está ligado, mas andar continua
possível. Além disso, a liberação com altura exatamente zero podia deixar
$60 bit 4 ativo, pois $1C6CA só limpa a marca aérea quando a altura fica
negativa.

Agora, apenas para a animação própria do juggle e defensor vivo que já
chegou ao chão, limpa $240 e os bits 7/4 de $60, zera altura, velocidades
e atrito antes de seguir a saída original. O juggle continua enquanto a
altura é positiva; KO e outras reações seguem o caminho original.
Não injeta botões ou comandos pendentes e não altera cancels/buffers.
Validar andar e atacar imediatamente no neutro depois do uppercut,
incluindo defensor que estava atacando no ar antes do acerto.

Build com todos os patches, build isolado e inspeção de destinos de hooks.
Aprovação em jogo ainda necessária:

- Uppercut perto e longe contra pulo, com P1/P2 e ambos os lados.
- Continuar com normal/especial e confirmar contador de combo sem intervalo.
- Conferir caixas vulneráveis, pouso, retorno ao neutro e ausência de grito.
- Repetir para todo o elenco, incluindo chefes; ajustar tempo/altura se preciso.
- Acertos no chão, defesa, tontura, KO e Renbuken sem regressões.

Extensão Ryo: segundo acerto do Kohou forte usa a mesma reação de juggle, com break LP+LK conforme SPEC-062. Uppercut global permanece com seus filtros anteriores.

Kohou forte: segundo contato usa poses de queda nativas em $791–$79F e sobe reto a 8 px/frame; terceiro sem break derruba normalmente. A mecânica original do uppercut mantém $781–$78F e 6 px/frame. Ver SPEC-062.

Atualização Kohou: velocidade vertical do defensor é 12 px/frame para acompanhar a subida do Ryo até o terceiro contato perto do ápice (SPEC-062). Uppercut global permanece em 6.

Hien forte automático: segundo contato $43 com estágio 3 entra diretamente no despacho de juggle $21344, a 8/-0,25. O flip do Ryo não altera mais a reação do adversário; ver SPEC-064.

Restauração Hien manual: retirado $43 do despacho de juggle automático. Hien só relança ao consumir LP+LK no segundo acerto (SPEC-064). Kohou e uppercut preservados.
