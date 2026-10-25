# SPEC-056: Dash no primeiro frame da aterrissagem

- Patch global: `landing-dash`.
- Combina com `dash-snappy` (SPEC-011), detector de dois toques por bordas.
- Status: implementado; validação no emulador pendente.

O detector de dash só rodava no neutro/andar. Toques feitos pouco antes
da aterrissagem não eram reconhecidos e o estado de pulo ainda esperava
o fim de sua animação. Agora pode adiantar os dois toques no fim do salto
e iniciar dash na primeira atualização em que a física confirmar o chão.

## Implementação

Hook $1C6CA conserva a limpeza de $A68 bit 2 e $20 e chama o detector
$1CCDA somente nos estados de pulo 4/8 ou ataque 3 com normal aéreo
$2A/$2B/$3A/$3B. Mantém a janela de dois toques da SPEC-011 (16 frames).
Quando o detector completa os toques, guarda a direção física $213 e
abre uma janela de seis atualizações (~0,1 s) para aterrissar.

Hook $1B6E2, depois do handler do estado: decrementa essa janela e,
quando $60 bit 4 está limpo e $A68 bit 2 confirma aterrissagem, executa
$1BC84, que seleciona dash para frente/trás conforme o lado atual.
Não executa dash dentro da física, evitando que o restante do handler
do salto/ataque sobrescreva o novo estado.

Só aceita direção 4/8 e não dispara com cima/baixo segurado. Estado novo
de ataque, especial, defesa ou dano tem prioridade e descarta a intenção.
Normais aéreos ainda na transição de aterrissagem podem passar a dash;
não permite cancelar recuperação de especiais, hitstun ou blockstun.
Limpa $240 e $60 bit 7 como na aterrissagem nativa, sem alterar os cancels.
Conserva d0–d4/a0/a1 no hook após o estado e reproduz o desvio original
de $715(a5). O helper de física mantém o restante do cálculo original.

## RAM reservada por jogador

| Campo | Uso |
|---|---|
| $3AB | Direção pronta (4 esquerda / 8 direita) |
| $3AC | Frames restantes para aterrissar (6..0) |
| $3AD | Dash de aterrissagem ainda na fase inicial |
| $3AE | Detector já chamado pela física nesta atualização |

São bytes da faixa livre documentada pelo ram_scan ($39B–$3DE), após
$3A8/$3A9 de efeitos do Ryo e $3AA do orçamento de Zanretsuken. A intenção
é descartada ao executar, ao expirar ou ao entrar em estado incompatível.
Nenhum botão é guardado e nenhum comando especial é injetado.

## Validação

Build completo/isolado com SPEC-011 e destinos dos hooks. Testar no
emulador: pulo neutro/frente/trás → dash para ambos os lados; segundo toque
no frame de contato e até 6 atualizações antes; primeiro toque no ar e
segundo no chão; sem toques/diagonais/entrada expirada não há dash; golpe
aéreo → dash na aterrissagem; especiais/defesa/dano sem dash indevido;
P1/P2, lados trocados, cancels anteriores e dash normal preservados.

## Fluidez: contato em zero e movimento imediato

Ajuste após o usuário ainda perceber atraso, aproveitando o mesmo buffer:

- Com intenção ativa e estado válido de pulo/normal aéreo, altura inteira
  <=0 e velocidade vertical <=0 já confirmam o contato visual. Normaliza
  altura/velocidade vertical e marca aterrissagem, sem esperar altura
  negativa. Não antecipa contato na subida, em dano, defesa ou especial.
- Depois de iniciar o dash, chama $1BD34 na mesma atualização para definir
  velocidade horizontal antes da cópia de movimento para o sprite.
- Hook $1BD2C: somente com $3AD ativo no estado 16/17, ignora a trava dos
  quadros iniciais $A69 bit 6. Aguarda também a animação nova iniciar
  ($42 do sprite), para não interpretar flags antigas do salto. Limpa a
  marca na primeira fase de movimento. A pausa final e dashes comuns
  continuam originais; abandonar o dash limpa a marca após o estado.

Validação adicional: altura -1/0/+1 em subida/descida; bootstrap de
velocidade no mesmo fluxo; animação nova pendente/ativa, fase inicial/final,
interrupção do dash e ausência de mudanças em especiais. Build e casos
simulados passaram; a sensação de fluidez ainda precisa de teste ao vivo.

## Correção: ler dash também depois do contato, antes do fim da animação

O usuário relatou novo atraso. A leitura no ar ocorria em $1C6CA, mas o
estado de pulo $1C32A deixa de chamar essa física depois de limpar o bit
aéreo. Enquanto a animação de aterrissagem não acabava, também não entrava
no detector do neutro. Assim, um segundo toque dado logo depois do contato
podia ser ignorado até o fim da animação, apesar das melhorias de startup.

O hook após o estado agora também chama $1CCDA quando o personagem já
está no chão mas ainda no estado de pulo/normal aéreo. Isso preenche a
lacuna de leitura e pode completar a intenção e iniciar o dash na mesma
atualização. $3AE evita processar a mesma borda duas vezes quando a física
já leu o detector naquele frame; é limpo ao fim de toda atualização.
Não duplica a leitura nos estados de neutro/andar, que já têm detector.

Verificados os caminhos de leitura e a sequência toque-solta-toque sem
esperar estado neutro. A validação ao vivo ainda é necessária para medir
o intervalo entre contato visual e deslocamento no emulador do usuário.
