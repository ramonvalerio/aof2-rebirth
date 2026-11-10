# SPEC-080 — Prioridade global dos DESPERATION

## Regra

Todos os DESPERATION possuem invencibilidade durante sua execução, incluindo preparação e recuperação. Golpes normais, especiais, SUPER, agarrões e DESPERATION corporais não interrompem nem causam dano a quem está executando um DESPERATION.

A exceção é o projétil de outro DESPERATION, que pode atingir o personagem. Quando dois projéteis DESPERATION colidem, ambos se dissipam, independentemente de tamanho ou força. Contra projétil comum ou SUPER, o projétil DESPERATION prevalece.

A regra termina quando o personagem sai do ataque ou muda de comando, inclusive ao fintar o DESPERATION. Não altera dano, custo de Spirit ou requisitos de ativação.

## Implementação

Patch global `desperation-priority`. Identifica os registros de DESPERATION dos 12 personagens que possuem esse golpe, também sem depender da marca de input humano. Guarda marcador em `$3C3` e comando em `$3C4` do ator. A proteção exige estado de ataque 3 e comando atual igual ao guardado.

Projéteis recebem marca em `$80`, inicializada em toda criação, conservando sua identidade após o dono voltar ao neutro. O filtro de colisão em `$F6B98` trata simetricamente os dois lados e rejeita somente contatos contra caixas de corpo protegidas. Não consome nem desliga caixas de ataque. O patch de hurtbox de juggle disponibiliza uma caixa de corpo nas poses invulneráveis para permitir a exceção dos projéteis DESPERATION, mantendo o filtro para os demais ataques.

A disputa nativa de projéteis em `$22DA2` recebe a prioridade e o empate. A validação de agarrões em `$1DC14` recusa defensor protegido. A finta da SPEC-067 continua funcionando: saída do ataque encerra a proteção, sem depender de apagar um marcador a cada quadro.

## Verificação

- Build com bytes originais conferidos, montagem e ausência de conflito entre patches.
- `python tools/check_desperation_priority.py`: 164 casos executando código 68000 com Unicorn, cobrindo os dois lados, preparação de versões, marcadores inativos, troca de estado/comando, ciclo do projétil, prioridade/empate, imunidade a agarrão e preservação de caixas de ataque.
- `python tools/hook_check.py` e `git diff --check`.
- Validação visual e partidas no emulador permanecem pendentes.
