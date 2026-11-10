# SPEC-076: HP+HK permitido no ar como regra global

## Comportamento

Soco forte + chute forte pode ser usado durante o salto por todos os
13 personagens jogáveis, incluindo Geese. Executa no ar o golpe próprio
de HP+HK de cada personagem, com suas poses, dano, hitstop e reação,
mas com propriedade alta de ataque aéreo ($4B20).
O comando no chão não muda. Sem custo novo de Spirit.

O limite nativo de um ataque aéreo por salto, bloqueios da reação e
aterrissagem continuam vigentes; não é cancelamento de outro ataque já
executado no salto. Os chutes aéreos isolados e uppercut LP+HP permanecem.

## Implementação

Patch global isolado `air-heavy-pair-kick`. O tradutor existente já emite
$270 alto=$60 para HP+HK. No ar, o leitor nativo chega a $3A/$3B; o hook
MOVE_RECORD distingue a combinação por ($270|$274)&$6000=$6000 e exige
marca aérea $60 bit4. Comando válido no ar seleciona cópia do registro do
HP+HK nativo ($34), indexada por personagem. Mantém o comando aéreo do
motor para preservar controle/física/trava do ataque aéreo, sem forçar
a postura de agachado do handler terrestre $1D65A.

Registros por personagem: $00C/$033/$058/$07F/$0A1/$0C8/$0E5/$10D/
$12F/$150/$171/$194/$1B1. Dados originais não são reescritos. Somente
$6A/$6B da cópia usa $4B20. A animação nativa de cada golpe é preservada,
incluindo os comandos de movimento que fazem parte de seu próprio golpe.
Não usa o mesmo sprite para o elenco nem acrescenta dano/caixas artificiais.

$3C0 marca essa variante enquanto executa; todo novo registro limpa a
marca. A pressão específica de LK aéreo do Ryo (SPEC-059) exclui essa
variante, pois o motor usa o mesmo comando aéreo $3A. Demais regras
compartilhadas de colisão/cross seguem as mesmas condições de antes.
A seleção global ocorre antes das customizações de HK aéreo do John,
que continuam sendo usadas somente com HK isolado, sem a combinação.

## Verificação

Build com 70 patches e hook_check aprovados. 900 cenários simulados
conferem personagem, chão/ar, comando, par/isolados e buffer; 13 cópias
comparadas byte a byte aos registros nativos (exceto propriedade alta);
build determinístico. Sem alteração dos registros do comando terrestre.

Confirmar no emulador HP+HK no salto com todos os personagens, ambos os
lados, colisão/guarda/aterrissagem, chão inalterado, um ataque por salto,
LK aéreo do Ryo e HK aéreo remapeado do John. Sem teste em partida.

Micky: a cópia aérea de HP+HK também recebe efeito de queda $15, acompanhando a alteração terrestre da SPEC-078; demais atributos preservados.
