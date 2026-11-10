# SPEC-075: John — HK aéreo com a animação da rasteira

## Regra

John é o personagem interno 8, confirmado por tools/lua/hitbox_viewer.lua
(NAMES[8]=John; NAMES[12]=Temjin). A implementação anterior usava 12 e não
alterava o John. Corrigidos o filtro e as poses; retirado o efeito em Temjin.
Constantes JOHN=8, LEE=5, TEMJIN=12 centralizadas em charlib.

- HK no ar sem baixo: chute usando animação/caixa da rasteira do John.
- Baixo+HK (inclusive diagonais) no ar: chute aéreo original do John.
- Baixo+HK no chão: rasteira original, sem alteração.

## Dados corretos

Rasteira: comando $39, registro $10F, animação $4B5. Aéreo anterior:
comando $3B, registro $111, animação $4B7. Não usa dados $196/$198/$6B4/
$6B6, que pertencem ao Temjin.

MOVE_RECORD exige JOHN=8, comando $3B e baixo solto. Registro exclusivo
usa todos os atributos da voadora forte do Ryo (registro $010), mantendo
somente a animação própria do John: dano-base 22, hitstop 10, efeito $0E,
reação 2, propriedade $4B20, chip/custo/hits extras zero. Animação $22D com poses/tempos nativos
da rasteira: comando/som $02B2 por 1 frame; $02B8 por 1; $02BA por 1;
$02BB ativa por 9; recuperações $02BA/$02B8/$02B2 por 8 cada; fim $02B2.
Lista de comandos copiada c70046ca0246043c02b2. Não há lançamento D2,
escrita em posição ou alteração da trajetória do salto. O motor mantém
trava de ataque aéreo, física e aterrissagem. Com baixo, usa o original.

Nenhum registro ou animação original de John/Temjin é reescrito. A mesma
correção de identidade foi aplicada ao Overdrive EX da SPEC-074.

## Verificação

Build e hook_check aprovados. Nome/ID comparados à tabela do projeto;
48 cenários simulados de personagem/comando/direcional aprovados;
$22D verificada com caixa ativa $02BB e sons da rasteira correta;
registros e ponteiros originais de John/Temjin preservados.

Confirmar na partida, após recarregar ROM: HK no alto mostra rasteira do
John; baixo+HK mostra o chute aéreo anterior; rasteira no chão normal;
colisão e recuperação sem travar. Ainda sem execução no emulador.

## Propriedades da voadora forte do Ryo

Registro exclusivo agora é 16160000000a0e004b20022d00000200: corresponde
byte a byte ao registro $010 do Ryo, exceto animação $22D do John em vez
$137 do Ryo. Portanto deixa de usar efeito de queda $15 e atributos de
dano/hitstop da rasteira. Poses, caixa e tempos da animação do John
permanecem; não transplanta a animação/caixa física da perna do Ryo.
Baixo+HK no ar continua original e a rasteira no chão também.

Build e hooks aprovados. Comparação de todos os bytes de atributos
(excluindo animação) contra a ROM final do Ryo e preservação do registro
$111 original do John aprovadas. Confirmar comportamento na partida.
