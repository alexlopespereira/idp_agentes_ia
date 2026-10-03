---
layout: default
title: Rotulação cega no terminal
---

# Rotulação cega no terminal

O comando [`scripts/onda5w_leitura_cega.py`](scripts/onda5w_leitura_cega.py)
mostra, para cada item, somente as mensagens até o `Output` alvo e registra
o julgamento humano em um checkpoint privado. A validação dos votos e o
fechamento da dupla leitura estão em
[`scripts/onda5v_dupla_leitura.py`](scripts/onda5v_dupla_leitura.py).
O código não contém conversas reais, IDs de origem ou votos. Não inclui
modelo de IA nem envia dados a serviços externos.

Requisitos: Python 3.9+ em macOS ou Linux; para contextos longos, `less` no
terminal. Esta versão usa `fcntl` e `termios`, portanto não roda no Python
nativo do Windows. Nesse sistema, use WSL ou outro ambiente Linux autorizado
a receber os dados. Não coloque corpus de pesquisa em serviço de nuvem ou
neste repositório público.

## Teste com dados sintéticos

Na raiz do repositório:

```sh
python3 -m scripts.onda5w_leitura_cega demo data/demo
python3 -m scripts.onda5w_leitura_cega ler data/demo/fila_sintetica.json --leitor teste
```

`data/` é ignorado pelo Git. O comando `demo` cria três diálogos inventados;
ele não prepara nem substitui uma fila de pesquisa.

## Ler uma fila privada

Receba o JSON da fila por canal aprovado e guarde-o fora do repositório,
em diretório acessível apenas ao leitor (`0700`), com arquivo `0600`.
Cada leitor precisa ter sua própria cópia da **mesma** fila e usar um nome
distinto. Por exemplo:

```sh
python3 -m scripts.onda5w_leitura_cega ler /caminho/privado/fila.json --leitor leitor_a
```

O programa grava `leitura_leitor_a.json` ao lado da fila após cada voto e
retoma desse checkpoint. Não compartilhe o checkpoint nem os rótulos de um
leitor com o outro antes de ambos terminarem. Para uma dupla leitura real,
use contas ou dispositivos separados; duas pastas na mesma conta, por si,
não impedem acesso cruzado.

No menu, `r` rotula ou revisa, `n`/`p` navegam, `g` vai ao próximo pendente,
`s` pausa e `q` sai. Um contexto extenso abre no paginador: setas navegam,
`/` busca e `q` volta ao voto. O item e a ordem são cegos quanto a qualquer
previsão de modelo. O voto distingue resposta avaliável de não avaliável;
para a primeira, registra o pedido anterior de referência (`M1`, `M2`, …),
falha observável e, quando necessário, subtipo e justificativa.

Após duas leituras completas, copie **somente por canal aprovado** os dois
checkpoints para uma mesma pasta privada com uma cópia idêntica da fila e rode:

```sh
python3 -m scripts.onda5w_leitura_cega desempatar /caminho/privado/fila.json --leitor-a leitor_a --leitor-b leitor_b
```

O fechamento preserva os votos originais e pede decisão explícita para cada
divergência. Filas e checkpoints são dados sensíveis: não os adicione ao Git,
não os envie como issue e não publique os resultados de células pequenas.
