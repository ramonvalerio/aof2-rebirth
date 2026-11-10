# SPEC-078: Micky — HP+HK derruba e encadeia após HP perto

Soco forte + chute forte passa a derrubar: registro $0E5 (comando $34)
efeito $00 → $15, queda de rasteira. Dano 12, hitstop 16, animação $427,
alcance e custo zero permanecem. A cópia aérea global SPEC-076 recebe o
mesmo efeito, preservando a consistência da variante. A regra geral de
normais contra alvos já no ar permanece a da SPEC-012.

Soco forte perto ($23) pode ser cancelado em HP+HK após acerto real,
com adversário vivo. Não habilita cancel em erro ou defesa. Usa o buffer
nativo de hitstop, máscara $60 no byte alto de $270/$274, normal_chain_block
e saída $1C0BA, como os chains de Ryo/Robert. Não amplia caixas nem move
lutadores. A continuação precisa estar em alcance, sem custo adicional.

Patch isolado `characters/micky/close-hp-heavy-pair-chain`, com identificação
MICKY=7 centralizada. Insere guarda de defesa/vida antes do helper comum.
O Burning Upper EX e seu projétil em juggle não mudam.

Build com 72 patches e hook_check aprovados. 192 cenários simulados de
personagem/comando/acerto/vida/defesa/par/buffer aprovados; efeito $15
verificado no registro terrestre e na cópia aérea. Testar em partida
HP perto → HP+HK, queda no contato, defesa/erro, variante aérea e Burning
Upper em três versões. Sem execução no emulador nesta revisão.
