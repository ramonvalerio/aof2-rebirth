# SPEC-082: "REBIRTH" na tela de título

- Patch global: `title-rebirth`.
- Altera P-ROM (hook) e S-ROM (`056-s1.s1`, tiles da camada fix).
- Status: implementado e conferido no FBNeo (MVS, título com ficha);
  validação na MiSTer pendente.

A tela de título ("PUSH 1P START BUTTON") passa a mostrar **REBIRTH** logo
abaixo de "FIGHTING", na fonte dos nomes do retrato da seleção de personagem.

## Fonte

Os nomes do retrato da seleção ("RYO", "ROBERT"...) são uma tira de sprites
em $65C9–$65FF da C-ROM: serifada itálica, degradê dourado (índices 1–13) e
contorno azul (14). As letras foram recortadas dessa tira: R de RYO, E de LEE,
B e I de BIG, T de TAKUMA (o de ROBERT tem o braço esquerdo sobre o R) e H de
JOHN. Cada nome tem o próprio degradê horizontal; o degradê foi refeito na
palavra inteira (escuro nas pontas, claro no centro). Resultado: 119×16 px,
guardado como texto em `patch.py` (`ART`).

## Exibição

Camada fix, que fica sobre os sprites do logo. 15×2 células de 8×8 em
coluna 10, linhas 17–18 (x = 72, y = 120 na tela de 304×224).

- **Tiles:** 30 tiles fix vazios da S-ROM: $31D–$31F, $41B–$41F, $4D8–$4DF,
  $DF0–$DF3, $FBB–$FBF e $FFA–$FFE. Ficam fora das fontes em uso e da área de
  kana/kanji, e não são a posição de "espaço" de nenhuma fonte ($x20/$x40).
  Medição com `registerwrite` em $3C0000/$3C0002 (attract, título, seleção,
  instruções e luta, depois do boot da BIOS): 404 tiles fix usados, nenhum
  desses 30.
- **Paleta:** fix 15, que já é a paleta dos nomes (mesmas cores, mesmos
  índices). Nenhuma paleta é alterada.
- **Escrita:** hook em $157DE, a rotina de cada frame da tela de título
  (`move.w #$90,d0 / jsr $41BE`). Depois do texto original, enfileira na fila
  de textos do VBlank (-$5F8(a5), trava -$5F4(a5), executor $0FD8) um registro
  com: cmd 2 (VRAMMOD = $20), cmd 1 parâmetro 3 (palavras com contagem 15),
  e, para cada linha, cmd 3 (VRAMADDR) + cmd 7 (15 palavras $F000|tile);
  cmd 0 encerra. Ao sair do título o jogo limpa a camada fix, e o texto some.

## Build

`patchlib.RomData(file, offset, expect, new)` grava bytes em outros arquivos
do romset, com conferência dos bytes originais e detecção de conflito, como
os dados da P-ROM. O `.neo` da MiSTer precisa levar também a S-ROM do zip.

## Validação

FBNeo: título com ficha mostra REBIRTH sob o logo; a tela seguinte
(instruções) não tem restos. Testar na MiSTer, inclusive em modo console
(AES), cuja tela de título pode seguir outro caminho de código, e em região
japonesa.
