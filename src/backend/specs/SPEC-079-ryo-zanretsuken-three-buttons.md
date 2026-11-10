# SPEC-079 — Ryo: Zanretsuken com três versões

## Comportamento

Mantém o comando direcional do Zanretsuken e seleciona a versão pelos socos:

| Botões | Versão | Final |
|---|---|---|
| Soco fraco | Fraca | Animação do soco forte neutro |
| Soco forte | Forte | Gancho original do Zanretsuken |
| Dois socos | EX | Animação do trás + chute forte, lançando em juggle e com estalo pesado |

O EX custa 20% da barra máxima de Spirit, conforme a regra global de especiais com dois botões. O lançamento acontece somente no último acerto do EX; defesa e KO seguem os tratamentos globais. O adversário lançado pode receber novos golpes no ar.

## Implementação

Patch `characters/ryo/zanretsuken-three-buttons`, executado antes de `zanretsuken-19-hits`. A versão fraca conserva a sequência curta e recebe o final 0x23A. A forte mantém a sequência e o gancho nativos. O EX usa a sequência forte com final 0x23B, baseado no trás + chute forte nativo 0x132.

O marcador 0x3C2 distingue as versões. O reconhecimento do último passo aceita dois socos sem disputar com o uppercut universal. Os novos finais encerram o modo nativo de golpes extras; não são rearmados pelo patch de multihit. Permanecem a proteção contra dano excessivo e o limite de contatos da SPEC-025. Os valores de dano por contato não foram alterados nesta mudança.

## Verificação

Build da ROM com validação dos bytes originais e montagem dos blocos; inspeção das sequências e dos finais; seleção de botões verificada por simulação. Verificação de desvios para o interior dos hooks e de espaços em branco. Validação de animação, contatos e juggle em partida permanece pendente.

## Correção do final EX

O final 0x23B usa os quadros e poses do trás + chute forte (0x132), não o chute forte neutro. No acerto sem defesa, fixa o som de impacto 0x140 e marca o efeito no defensor (bit 7 de 0x24B). O despacho de reação usa essa marca e o comando de origem 0xA6A, evitando depender da animação/comando atual do atacante quando a reação é processada.

O EX limita a sequência anterior a 18 contatos e reserva um contato para o final, mantendo o teto de 19. Ao entrar no final, libera esse único contato e rearma as caixas; o final não participa do rearmamento repetido do multihit. O comando DE encerra os golpes extras e DD00 remove a reação anterior antes da pancada final. Defesa e KO preservam os caminhos nativos.

Verificação adicional: `python tools/check_ryo_zanretsuken.py` executa 66 casos de marcação/som e reação atrasada, cobrindo 12 defensores, defesa e KO. A inicialização nativa da reação é substituída por um retorno nesse teste; não equivale a uma partida. Juggle usa subida vertical 8 e gravidade -0,25, com hurtbox aérea global. Custo EX permanece em 20%.

## Som de impacto do Hien Shippuukyaku

Referência final solicitada: o som dos hits do Hien Shippuukyaku, ID 0x0140 (E7 0140 na lista nativa 0x533BC). No Zanretsuken EX, esse som é aplicado no contato final sem defesa em 0xA5E do defensor, como nos patches de som do Kohou e Kou'ouken. O evento de movimento do chute continua C7 0172. Foi removido C7 0140, que tocava na animação mesmo sem acerto e não substituía o som do impacto. Juggle, animação, custo e demais versões permanecem iguais.

## Correção da identificação do final na sequência

A causa confirmada do som incorreto era a comparação com 0x6E do ator. O Zanretsuken mantém 0x414E nesse campo enquanto a sequência avança; a rotina nativa 0x4A8E troca 0x54 do sprite para 0x23B ao chegar ao final EX. A condição anterior, exigindo 0x6E = 0x23B, não reconhecia o último contato.

O som e o marcador de juggle agora identificam o final por 0x54 do sprite do atacante. A reserva do último contato e a exclusão dos finais do rearmamento repetido também usam a animação do sprite. O som escolhido continua sendo 0x0140, usado pelo Hien Shippuukyaku.

O teste de regressão executa a troca nativa de sequência da ROM construída, mantendo 0x6E = 0x414E. Depois executa a cadeia completa de contato a partir de 0x2248E e o seletor de áudio 0x21E34. O Hien e o Zanretsuken EX enviam uma única chamada com 0x0140 para 0x9BA, onde a saída de hardware é interceptada no teste. A ROM anterior falhou nessa mesma comparação para o Zanretsuken EX. A audição em partida continua pendente.
