# SPEC-063: Especiais fortes com dois botões — custo global de Spirit

Uma versão forte de especial comum selecionada com dois botões consome
20% da capacidade máxima de Spirit. Com capacidade 120, desconta 24.
Versões fracas/médias conservam seus custos atuais. SUPER e DESPERATION
mantêm as regras próprias. Dois botões que selecionam uma versão fraca
(como o Kou'ouken atual) não recebem esse custo.

Implementação no patch global special-strength-by-button: o detector
registra em $3B3 se houve par de socos/chutes, pois $218 é apagado antes
do desconto. O snapshot, antes de remover a marca de $23F, exige comando em $20(a5)
$40–$47, versão forte $23F=$C0 e par registrado. Calcula unidades máximas
$256 / 5 (divisão inteira), substitui $241 uma vez e usa o desconto nativo.
Preserva d0/d1. O piso nativo de Spirit permanece: barra insuficiente não
bloqueia a execução e fica no mínimo nativo, sem valor negativo.

Não altera os atributos individuais de custo; portanto não conflita com
as versões novas dos personagens ou com o custo existente do Renbuken.
$3B3 é reinicializado em toda detecção e não conflita com target $3B2.

Para acomodar os blocos, o alocador usa alinhamento par (2 bytes, requisito
68000), aproveitando o espaço antes desperdiçado por alinhamento de 16.
A região reservada continua $FDDA0–$FFEFF; limites e conflitos seguem verificados.

Validação funcional em emulador pendente: fortes de King/Mr.Big/Kohou,
versões fracas/médias, Kou'ouken com par, supers, Spirit baixa e repetição.

Build completo aprovado com 57 patches e nenhum desvio externo para o meio dos hooks. Teste de consumo na partida ainda pendente.

Correção do consumo: o snapshot é chamado em $1D6C6, mas $230 só recebe
o novo comando em $1D6E2. O filtro agora lê $20(a5), já preparado por
$1D41E; assim não depende do golpe anterior. A regra global permanece
restrita a fortes com par. Verificados 72 cenários simulados do bloco de
custo, incluindo exclusões, máximos 60/100/120 e preservação de d0/d1.
Com máximo 120, o desconto é 24 unidades, usando a rotina nativa uma vez.
