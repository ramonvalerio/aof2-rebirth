# ADR-0004: Força do especial marcada nos bits altos do comando ($218)

- **Status:** Aceita
- **Data:** 2026-10-23
- **Spec:** [SPEC-004](../specs/SPEC-004-special-strength-by-button.md)

## Contexto

A variante do especial (fraca/média/forte) é escolhida pela barra em `$1D53E`, no momento em que o golpe **executa**. O comando, porém, é **detectado** antes (`$1E102`) e pode esperar até 60 frames em `$218(a6)`. Nesse intervalo, o sinal de "botão forte" (`$271`) já foi recalculado. É preciso guardar a força no momento da detecção.

Opções avaliadas:

1. **Byte livre no registro do jogador**: os registros de P1/P2 ficam intercalados com outros objetos e são acessados por ponteiros com deslocamentos diferentes. A varredura não conseguiu provar que algum byte está livre.
2. **RAM de trabalho fora do registro**: mesmo problema, sem mapa confiável da RAM.
3. **Bits altos de `$218`**: os comandos usam só `$40–$4F`, e o executor (`$1D41E`) já mascara com `$7F`. Todos os leitores de `$218` foram revisados (ver SPEC-004).

## Decisão

Opção 3. O bit 9 marca "comando do jogador" e o bit 8 marca "botão forte". Comandos sem o bit 9 (IA) mantêm a regra original da barra. São dois hooks, `$1E102` e `$1D548`, cada um com seu bloco realocável.

## Consequências

- (+) Não precisa de RAM nova; a marca vive e morre junto com o comando.
- (+) O patch é independente da SPEC-002: só depende da semântica de `$271`, que já existe no jogo original.
- (−) Qualquer leitor futuro de `$218` precisa considerar os bits 8/9. Isso fica registrado na SPEC-004.
