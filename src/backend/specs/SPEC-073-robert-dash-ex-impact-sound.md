# SPEC-073: Robert — estalo forte no chute final do EX de dash

O segundo acerto de frente, frente + dois chutes toca o som pesado $0140,
o mesmo estalo usado no Hien e no Kohou forte do Ryo. A rasteira inicial
conserva seu som. Na defesa, mantém o som de bloqueio original.

Patch isolado `characters/robert/dash-ex-impact-sound`, HIT_SOUND após a
cópia nativa. Exige atacante Robert, comando $31 e estágio EX $3BE=3,
com contato não defendido ($7C & $F !=3). Só troca $A5E do defensor.
HK normal avulso, outros golpes/personagens, dano, Spirit e juggle não
mudam. A marca é limpa no próximo registro pela SPEC-071.

Build com 67 patches, assembler e hook_check aprovados. Conferência do
som no emulador pendente: segundo hit estala, primeiro e defesa mantêm
som original, HK posterior avulso não herda o efeito.
