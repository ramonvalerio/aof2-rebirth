# Specs das mecânicas globais

Regras que valem para o elenco inteiro. Dano, comandos e exceções de um
lutador pertencem às [specs de personagem](../README.md), conforme ADR-0005.
Os patches globais são aplicados antes dos patches de personagem.

| Patch | Regra e spec |
|---|---|
| `crossup-close-pressure` | [Cross global: anula afastamento do hit](../SPEC-060-crossup-close-pressure.md) |
| `landing-dash` | [Dash imediato ao aterrissar](../SPEC-056-landing-dash.md) |
| `controls-4button-layout` | [Controles: A/B chutes, C/D socos, A+C arremesso, C+D uppercut, B+D chute baixo, START provoca](../SPEC-002-controls-4button-layout.md) |
| `free-special-moves` | [Especiais não gastam barra (SUPER e DESPERATION mantêm o custo)](../SPEC-003-free-special-moves.md) |
| `special-strength-by-button` | [Força do especial pelo botão (fraco = barra vermelha, forte = barra cheia)](../SPEC-004-special-strength-by-button.md) |
| `spirit-charge-abc` | [Carregar a barra exige A+B+C segurados juntos](../SPEC-005-spirit-charge-abc.md) |
| `special-cancel-input-buffer` | [Special cancel global (chão e ar) e buffer de comandos de 12 frames](../SPEC-008-special-cancel-input-buffer.md) |
| `dash-snappy` | [Dash ágil: sem quadros parados e dois toques sem precisar passar pelo neutro](../SPEC-011-dash-snappy.md) |
| `no-knockdown-normals` | [Golpe normal não derruba (só tontura e especiais)](../SPEC-012-no-knockdown-normals.md) |
| `hit-counter` | [Contador de combo na tela (N HIT COMBO) com a fonte do HUD](../SPEC-013-hit-counter.md) |
| `persistent-bruises` | [Rosto machucado continua nos rounds seguintes da mesma luta](../SPEC-014-persistent-bruises.md) |
| `rush-specials-true-combo` | [Especiais de sequência (Renbuken etc.) com todos os hits em combo](../SPEC-015-rush-specials-true-combo.md) |
| `jump-instant` | [Pulo sai na hora e não anda antes de pular (todo o elenco)](../SPEC-023-jump-instant.md) |
| `projectile-ignores-attacks` | [Projétil não é dissipado ao receber golpe (só some ao acertar ou contra outro projétil)](../SPEC-038-projectile-ignores-attacks.md) |
| `blockstun-command-buffer` | [Direcionais de especial durante a defesa; botão somente ao executar](../SPEC-042-blockstun-command-buffer.md) |
| `uppercut-juggle` | [Uppercut anti-aéreo permite continuar o combo (global)](../SPEC-043-uppercut-juggle.md) |
| `low-health-super-guard-pain` | [Vida até 32: defender SUPER abre 24 frames de punição em cheap KO](../SPEC-051-low-health-super-guard-pain.md) |
| `directional-only-special-buffer` | [Buffer direcional na defesa e recuperação, preservando todos os cancels](../SPEC-052-directional-only-special-buffer.md) |

## Interações documentadas

- [Resposta ao andar/pular (SPEC-058)](../SPEC-058-movement-response.md):
  remove a marca de parada restante no pulo e fornece diagnóstico de
  latência interna de movimento, sem mudar velocidade de andar.

- Buffer direcional (SPEC-052) acrescenta leitura na defesa/recuperação de
  especiais; preserva cancels e chains de normais (SPEC-008/042).
- Uppercut (SPEC-043) abre juggle global; sua aterrissagem remove a trava
  de ataques. Não altera os danos específicos do Ryo nas SPEC-053/054.
- SUPER defendido com vida <=32 (SPEC-051), se não matar, abre 24 frames
  de vulnerabilidade na animação de cheap KO. Chip letal continua matando.
- A regra de normais sem queda (SPEC-012) admite efeitos explícitos de
  rasteira nos patches de King, Micky, Eiji e Robert; consultar suas specs.
- Força por botão (SPEC-004) registra pares para as escolhas de três
  versões de King/Mr. Big/Ryo/Robert/Takuma; cada comando tem spec isolada.

Validações de build não substituem os testes de jogabilidade indicados em
cada spec. Os patches não documentam como confirmado o que falta testar.

- [Fortes com dois botões: custo de 20%](../SPEC-063-two-button-strong-spirit-cost.md)

- [Juggle atingível no alto](../SPEC-065-juggle-air-hurtbox.md)
