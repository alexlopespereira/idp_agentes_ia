# Exercícios da Aula 3 — ia-3.1 e ia-3.2

Dois laboratórios sobre **conduzir um agente**, não sobre escrever código à mão:

- **ia-3.1** — o script **Ralph**: um laço autônomo que trabalha sozinho até a suíte de testes ficar verde.
- **ia-3.2** — a skill **/grill-me**: uma sessão de perguntas que arranca de você as decisões da revisão bibliográfica da sua dissertação.

**Prazo dos dois: 04/10.**

## Qualquer um dos quatro harnesses

Estes exercícios rodam em **Claude Code, Codex, opencode ou pi**, e nenhum critério pergunta qual você usou. O que torna isso possível é o instalador de skills:

```bash
npx -y skills add <repositório> --skill <nome> --agent <harness>
```

Ele grava a skill em `~/.agents/skills/<nome>/` e a liga ao diretório do seu agente — os quatro leem de lá. Os valores de `--agent` são `claude-code`, `codex`, `opencode` e `pi`.

> **Instale as skills por esse comando, não pelo `/plugin` do Claude Code.** O `/plugin` só existe num dos quatro harnesses e grava num lugar que o autograder não consegue inspecionar. O `npx skills add` funciona nos quatro e é verificável — o autograder confere com `skills list`.

Se você ainda não fez o setup (Python, Git, `gh`, CLI `autograde`, login Google), volte para a [Parte 1 do tutorial da Aula 1](Exercicios_Aula1.md#parte-1--setup-uma-vez-no-semestre).

O fluxo de entrega é o mesmo de sempre:

```bash
cd <diretório do exercício>
autograde validar ia-3.1     # mostra o boletim e pergunta se quer submeter
```

> O **ia-3.1** exige repositório no GitHub: lá o repo é parte do que se avalia. O **ia-3.2** não exige — rode de dentro da pasta onde estão os arquivos, versionada ou não.

Você pode resubmeter quantas vezes quiser — **a maior nota conta**.

---

## Exercício ia-3.1 — Do CSV ao gráfico com o script Ralph

### A tarefa, em três etapas

1. **Join.** Junte `vendas.csv` e `lojas.csv` por `id_loja`, tratando as 3 vendas órfãs e a loja sem vendas. Entregue o **inner join** com o nome **`vendas_lojas.csv`**.
2. **Pivot.** A partir de `vendas_lojas.csv`, produza **`pivot_receita.csv`** — receita por região × mês.
3. **Gráfico.** Uma página estática **`index.html`** com um gráfico da receita mensal por região e um parágrafo de conclusão de ≥ 300 caracteres (pode ser gerado por IA).

**O requisito do exercício é como você chega lá:** escreva um `prd.json` e deixe o **script Ralph** construir o pipeline. Você conduz o loop; o agente escreve o código.

### Valores de conferência

Anote — é com eles que você sabe que acertou antes de submeter:

| | |
|---|---|
| Linhas do inner join | **420** |
| Receita total | **R$ 931.274,06** |
| Região líder | **Sudeste, R$ 265.077,49** |

### O que você entrega

Um repositório **público** chamado **`ralph-lab`** no seu usuário do GitHub:

```
ralph-lab/
├── scripts/ralph/
│   ├── ralph.sh                # o laço, baixado do upstream
│   ├── CLAUDE.md               # o prompt que o laço injeta a cada iteração
│   ├── prd.json                # a memória externa (gerada pela skill /ralph)
│   └── progress.txt            # o log de progresso, escrito pelo próprio laço
├── ralph-run.log               # a saída da execução, não vazia
├── tests/                      # os testes que definem "pronto" (test_*.py)
├── vendas_lojas.csv            # o inner join — 420 linhas
├── pivot_receita.csv           # o pivot região × mês
└── index.html                  # gráfico + parágrafo de conclusão
```

> **Os três entregáveis ficam na RAIZ do repo**, não em `data/` e `web/`. O caminho tem que bater exatamente, incluindo maiúsculas. Onde mora o código que o agente escreveu é escolha sua — o autograder não olha.
>
> **O `prd.json` fica em `scripts/ralph/`.** O `ralph.sh` resolve tudo relativo a si mesmo (`SCRIPT_DIR`), então é lá que ele procura o PRD e escreve o `progress.txt`. Quem inventar outro layout quebra o próprio loop antes de perder ponto.

### Passo 1 — Crie o repo e baixe os dados

```bash
gh repo create ralph-lab --public --clone
cd ralph-lab
mkdir -p tests scripts/ralph

curl -sSL -o vendas.csv https://raw.githubusercontent.com/alexlopespereira/idp_agentes_ia/main/exercicios/aula3/data/vendas.csv
curl -sSL -o lojas.csv  https://raw.githubusercontent.com/alexlopespereira/idp_agentes_ia/main/exercicios/aula3/data/lojas.csv
```

Leia a [descrição dos dados](aula3/data/README.md) antes de continuar — inclusive a seção **"Armadilhas pedagógicas"**. Elas são propositais:

- `vendas.csv` — 423 linhas (`id_venda, data, id_loja, categoria, unidades, receita_brl`), **3 delas com `id_loja=999`, que não existe**;
- `lojas.csv` — 8 linhas (`id_loja, nome_loja, regiao, uf, gerente`), e **a loja 108 (Batel/PR) não teve venda nenhuma**.

### Passo 2 — Instale as skills do Ralph

Duas skills: **`/prd`** escreve o documento de requisitos, **`/ralph`** converte esse documento no `prd.json` que o laço consome.

```bash
# troque --agent pelo seu harness: claude-code, codex, opencode ou pi
npx -y skills add snarktank/ralph --skill prd --skill ralph --agent opencode
```

Confira com `npx -y skills list -g` — é exatamente o que o autograder vai rodar.

### Passo 3 — Baixe o laço

O `ralph.sh` **não vem junto com as skills**: ele é um script de 113 linhas que você baixa e coloca no repo.

```bash
curl -sSL -o scripts/ralph/ralph.sh   https://raw.githubusercontent.com/snarktank/ralph/main/ralph.sh
curl -sSL -o scripts/ralph/CLAUDE.md  https://raw.githubusercontent.com/snarktank/ralph/main/CLAUDE.md
chmod +x scripts/ralph/ralph.sh
```

Ele também precisa do **`jq`** instalado (`sudo apt install jq`, `brew install jq`).

**Se você usa Claude Code ou Amp**, o script já funciona como está.

**Se você usa Codex, opencode ou pi**, precisa acrescentar o seu ramo: na linha 32 há uma validação que só aceita `amp` e `claude`, e logo abaixo o `if` que invoca o agente. O contrato é sempre o mesmo — rodar o agente **sem interação**, alimentando-o com o conteúdo do `CLAUDE.md`, e capturar a saída:

```bash
if [[ "$TOOL" == "amp" ]]; then
  OUTPUT=$(cat "$SCRIPT_DIR/prompt.md" | amp --dangerously-allow-all 2>&1 | tee /dev/stderr) || true
else
  OUTPUT=$(claude --dangerously-skip-permissions --print < "$SCRIPT_DIR/CLAUDE.md" 2>&1 | tee /dev/stderr) || true
fi
```

Cada harness tem seu modo não-interativo (`codex exec`, `opencode run`, `pi -p`…) — descubra o do seu com `--help` e teste **uma** invocação na mão antes de soltar o laço.

### Passo 4 — Escreva o PRD e rode o laço

```
/prd            → cria tasks/prd-<feature>.md a partir de perguntas
/ralph          → converte esse arquivo em prd.json
```

Mova o `prd.json` para `scripts/ralph/prd.json`. Ele é a memória que sobrevive entre iterações — cada iteração começa com contexto limpo, e o que persiste é o arquivo. Precisa dizer, no mínimo:

- **o que construir**: join por `id_loja` salvo em `vendas_lojas.csv`, pivot região × mês em `pivot_receita.csv`, `index.html` com gráfico;
- **o critério de pronto**: a suíte `pytest` inteira verde, com pelo menos 4 casos — linhas do join, receita total, forma do pivot, gráfico na página;
- **as restrições**: não apagar linhas problemáticas dos CSVs de origem, não inventar dados, ler `receita_brl` como número.

> Um `prd.json` esquelético não conduz loop nenhum — o autograder cobra ≥ 100 palavras.

Então rode, **da raiz do repo**:

```bash
./scripts/ralph/ralph.sh --tool opencode 10 2>&1 | tee ralph-run.log
```

O `10` é o limite de iterações. O `tee` grava em **`ralph-run.log` na raiz** — commite esse arquivo, é a evidência de que o laço rodou. O laço para sozinho quando o agente emite `<promise>COMPLETE</promise>`.

Quando o loop travar ou estourar o limite, **o ajuste é no `prd.json`, não no código**. Foi isso que você veio praticar.

### Passo 5 — O formato exato das saídas

**`vendas_lojas.csv`** — o inner join, **420 linhas de dados**. Quais colunas de `lojas.csv` você carrega é escolha sua, mas **mantenha o nome `receita_brl`**: é a coluna que o autograder soma (R$ 931.274,06, tolerância de R$ 0,50).

**`pivot_receita.csv`** — receita por região × mês, com este cabeçalho **exato**:

```csv
regiao,2026-01,2026-02,2026-03,2026-04,2026-05,2026-06
Centro-Oeste,...,...,...,...,...,...
Nordeste,...,...,...,...,...,...
Sudeste,...,...,...,...,...,...
Sul,...,...,...,...,...,...
```

- 4 linhas de dados + 1 de cabeçalho, 7 colunas.
- Ponto como separador decimal, 2 casas (`265077.49`), **sem** `R$` e **sem** separador de milhar.
- A soma de todas as células numéricas tem que dar **931274.06** (tolerância de R$ 0,50).

**`index.html`** — uma página com um elemento de gráfico (`<canvas>`, `<svg>`, Chart.js, Plotly, D3, ECharts, Vega…) e um `<p>` de conclusão com **pelo menos 300 caracteres**.

**`tests/test_*.py`** — pelo menos **4 testes** passando.

### Passo 6 — Valide e responda as duas perguntas

```bash
autograde validar ia-3.1
```

**Não há arquivo de reflexão neste exercício.** A reflexão é perguntada na CLI, na hora de submeter — você responde de improviso. São duas perguntas, valendo 30 dos 100 pontos:

1. Como você conduziu o loop: o que entrou no `prd.json` como critério de pronto, o que o agente errou numa iteração, e o que você mudou para destravá-lo.
2. Como o seu pipeline tratou cada uma das duas armadilhas dos dados, e quem ficou de fora do relatório por causa disso.

Anote os números **enquanto o loop roda**. O `ralph-run.log` guarda isso para você.

A CLI roda, na sua máquina: `gh --version`, `gh auth status`, `gh repo view`, **`python -m pytest -q --tb=no`** (com `python3` como alternativa) e **`npm exec -y skills -- list`** nos dois escopos.

> ⚠️ **Se o seu `pytest` vive dentro de um virtualenv, ative o venv antes de chamar `autograde validar`.** A CLI executa o `pytest` do ambiente em que ela está rodando: fora do venv, o comando não acha os testes e os 8 pontos de `pytest_verde` viram zero mesmo com a suíte verde no seu terminal. Rode **de dentro do diretório do repo** e **fora do terminal do agente**.

### Critérios do ia-3.1

| Critério | Peso | O que precisa |
|---|---:|---|
| `repo_existe` | 2 | o repo existe no seu usuário |
| `repo_publico` | 2 | visibilidade = public |
| `repo_nome_ralph_lab` | 1 | o repo se chama `ralph-lab` |
| `gh_autenticado` | 2 | `gh auth status` OK na sua máquina |
| `gh_repo_view_ok` | 1 | `gh repo view` funciona no repo |
| `skill_prd_disponivel` | 2 | a skill `/prd` aparece no `skills list` |
| `skill_ralph_disponivel` | 2 | a skill `/ralph` aparece no `skills list` |
| `ralph_sh_versionado` | 2 | o `ralph.sh` está versionado |
| `prd_json_existe` | 2 | `scripts/ralph/prd.json` |
| `prd_json_substantivo` | 4 | `prd.json` com ≥ 100 palavras |
| `log_ralph_nao_vazio` | 3 | `ralph-run.log` na raiz, não vazio |
| `tests_existem` | 2 | ≥ 1 arquivo `tests/test_*.py` |
| `pytest_verde` | 8 | `pytest` com ≥ 4 testes passando e nenhum falhando |
| `join_existe` | 2 | `vendas_lojas.csv` na raiz |
| `join_420_linhas` | 5 | 420 linhas de dados |
| `join_receita_total` | 5 | soma de `receita_brl` = 931274.06 (± 0,50) |
| `pivot_existe` | 2 | `pivot_receita.csv` na raiz |
| `pivot_cabecalho` | 3 | cabeçalho exato `regiao,2026-01…2026-06` |
| `pivot_forma_4x6` | 3 | 4 linhas de dados × 7 colunas |
| `pivot_total_confere` | 5 | soma das células = 931274.06 (± 0,50) |
| `web_existe` | 2 | `index.html` na raiz |
| `web_tem_grafico` | 4 | elemento de gráfico na página |
| `web_tem_conclusao` | 3 | `<p>` de conclusão com 300+ caracteres |
| `sem_segredos_versionados` | 3 | nenhum `.env`, `.pem`, `credentials.json`… no repo |
| pergunta 1 | 18 | como você conduziu o loop — respondida na CLI |
| pergunta 2 | 12 | como tratou as anomalias — respondida na CLI |
| **Total** | **100** | |

---

## Exercício ia-3.2 — Grill-me na revisão bibliográfica da dissertação

A skill **/grill-me** faz o contrário do que um assistente costuma fazer: em vez de responder, ela **pergunta**. O objetivo é transformar *desconhecido desconhecido* em *conhecido desconhecido* — descobrir as decisões da sua revisão que você ainda não tinha percebido que precisava tomar.

Cada aluno aprofunda a revisão bibliográfica da **própria dissertação de mestrado**, usando o grill-me para transformar um recorte vago num protocolo de revisão defensável.

> **Este exercício não exige repositório nenhum.** É avaliado **só com evidência local**: a CLI lê os arquivos e roda os comandos na sua máquina, e o autograder não consulta a API do GitHub. Basta uma pasta com os quatro arquivos nos caminhos certos — versionada ou não, pública ou privada, com o nome que você quiser. Você não precisa publicar pesquisa em andamento. Quem já mantém a dissertação num repo pode continuar; o autograder simplesmente não olha.
>
> Em compensação, seja claro sobre o que sai da sua máquina: o **conteúdo** dos quatro arquivos entregues é enviado ao backend e ao juiz LLM para ser avaliado. Não coloque nos artefatos nada que você não queira que seja processado assim.

### A tarefa, em três etapas

1. **Instalar** o grill-me.
2. **Interrogar**: rodar `/grill-me` sobre o tema da sua dissertação até fechar **pergunta de pesquisa, construtos, bases, strings de busca, janela temporal e critérios de inclusão/exclusão**.
3. **Gerar o artefato**: no prompt do grill-me, peça que ao final sejam produzidos o **protocolo de revisão** e a **matriz de literatura**.

### O que você entrega

```
<sua pasta de trabalho>/
├── grill-me-transcript.md           # a sessão: ≥ 16 perguntas numeradas, com as suas respostas
├── revisao/
│   ├── protocolo-revisao.md         # o protocolo, gerado ao final da sessão
│   └── matriz-literatura.csv        # ≥ 15 referências, 9 colunas, separador ";"
└── REVISAO.md                       # sua reflexão
```

### Passo 1 — Instale a skill

```bash
mkdir -p dissertacao-revisao/revisao   # o nome da pasta é seu; não precisa ser um repo
cd dissertacao-revisao

# troque --agent pelo seu harness: claude-code, codex, opencode ou pi
npx -y skills add mattpocock/skills --skill grill-me --agent codex
```

Não precisa de comprovante: o autograder confere a disponibilidade rodando `skills list` na sua máquina. Confira você também, antes de submeter:

```bash
npx -y skills list -g
```

### Passo 2 — Rode a sessão e salve o transcript

Peça o `/grill-me` sobre a **revisão bibliográfica da sua dissertação** e salve tudo em **`grill-me-transcript.md`, na raiz da sua pasta de trabalho**.

Regras de formato — o autograder conta as perguntas:

- numere cada pergunta como **`Q1`, `Q2`, …** ou **`Q01`, `Q02`, …** (tanto faz, desde que seja no começo da linha; pode ser um heading `## Q1 — ...` ou negrito `**Q1**`);
- **no mínimo 16 perguntas**;
- **cada pergunta tem a sua resposta logo abaixo**. Resposta é decisão: "tanto faz", "você decide", "ok" não contam;
- **pelo menos 3 vezes**, uma pergunta deve **reabrir uma decisão anterior** — e o transcript deve dizer qual:

  > **Q09** — Você disse na Q03 que só usaria Scopus. Isso ainda vale?
  > **R:** Não vale mais. Reviso a Q03: passo a incluir também a SciELO, pelo motivo que apareceu na Q04.

Esse vaivém é o ponto do exercício: uma *design tree*, não um questionário.

### Passo 3 — O protocolo e a matriz

Peça ao grill-me, ao final da sessão, que escreva os dois artefatos em `revisao/`.

**`revisao/protocolo-revisao.md`** precisa cobrir os seis pontos — em qualquer arranjo de seções, com os títulos que o agente escolher:

- a **pergunta de pesquisa**, em uma frase;
- os **construtos** que você vai medir ou rastrear;
- as **bases** onde vai buscar;
- as **strings de busca** de verdade, com operadores booleanos — não uma descrição em prosa do que você pretende buscar;
- a **janela temporal** e o motivo do corte;
- os **critérios de inclusão e exclusão**, aplicáveis por outra pessoa sem te consultar.

O juiz avalia o protocolo **à luz do transcript**: as decisões registradas ali têm que aparecer na sessão, e não surgir do nada depois.

**`revisao/matriz-literatura.csv`**, separador **`;`**, com este cabeçalho **exato** e **pelo menos 15 linhas** de referências:

```csv
autor;ano;titulo;base;tipo_estudo;construto;achado;lacuna;relacao_com_pergunta
```

> Use `;` porque títulos de artigo têm vírgula. Se o seu editor salvar com vírgula, o critério do cabeçalho falha.

### Passo 4 — `REVISAO.md` e validação

De 5 a 10 linhas sobre **o que a sessão revelou que você não sabia que não sabia**: nomeie uma coisa concreta que você não tinha considerado, e ligue-a a uma pergunta específica (`Qnn`). Elogio à ferramenta não conta.

Não há nada para commitar aqui — este exercício não exige repositório. Rode de dentro da pasta onde estão os quatro arquivos:

```bash
autograde validar ia-3.2
```

A pergunta de reflexão da CLI vale 30 dos 100 pontos: **qual pergunta do grill-me mais mudou o seu recorte, e qual decisão anterior ela derrubou** — citando o `Qnn`.

### Critérios do ia-3.2

| Critério | Peso | O que precisa |
|---|---:|---|
| `gh_autenticado` | 2 | `gh auth status` OK na sua máquina, na conta cadastrada no roster |
| `skill_grill_me_disponivel` | 3 | a skill `grill-me` aparece no `skills list` |
| `transcript_existe` | 2 | `grill-me-transcript.md` na raiz |
| `transcript_16_perguntas` | 8 | ≥ 16 perguntas numeradas `Qn`/`Qnn` |
| `transcript_respostas_substantivas` | 12 | respostas que são decisões (LLM avalia) |
| `transcript_revisa_decisoes` | 12 | ≥ 3 revisões de decisão anterior (LLM avalia) |
| `protocolo_existe` | 2 | `revisao/protocolo-revisao.md` |
| `protocolo_qualidade` | 8 | os 6 pontos cobertos, defensável e rastreável ao transcript (LLM avalia) |
| `matriz_existe` | 2 | `revisao/matriz-literatura.csv` |
| `matriz_colunas` | 5 | cabeçalho exato, separador `;` |
| `matriz_15_referencias` | 6 | ≥ 15 linhas de dados |
| `reflexao_existe` | 1 | `REVISAO.md` |
| `reflexao_tamanho` | 2 | ≥ 5 linhas não vazias |
| `reflexao_qualidade` | 5 | reflexão específica (LLM avalia) |
| reflexão na CLI | 30 | qual pergunta mudou o recorte (LLM avalia) |
| **Total** | **100** | |

---

## Quando der errado

**`skill_*_disponivel` zerado com a skill funcionando no seu agente.** Você provavelmente instalou pelo `/plugin` do Claude Code, que grava num lugar que o `skills list` não lê. Reinstale com `npx -y skills add` e confira com `npx -y skills list -g`. O comando precisa de `npm` no PATH e de rede na primeira execução.

**`pytest_verde` zerado e você jura que os testes passam.** A CLI roda `python -m pytest` e `python3 -m pytest` a partir do diretório do repo, no ambiente em que a própria CLI está rodando. Se o seu `pytest` só existe dentro de um venv, **ative o venv antes** de chamar `autograde validar`.

**O `ralph.sh` morre com "Invalid tool".** É a validação da linha 32: o upstream só aceita `amp` e `claude`. Acrescente o seu harness ali e no `if` do laço — Passo 3.

**O laço roda mas o agente não acha o PRD.** O `ralph.sh` procura `prd.json` **ao lado de si mesmo**, em `scripts/ralph/`. Se você deixou na raiz do repo, mova.

**Critério de arquivo zerado com o arquivo no lugar.** O caminho tem que bater exatamente, incluindo maiúsculas: `REVISAO.md`, não `Revisao.md`; `pivot_receita.csv` **na raiz**, não em `data/`; `ralph-run.log` na raiz, não em `logs/`.

**`join_420_linhas` dando 423.** Você entregou o left join a partir de `vendas.csv` — as 3 vendas com `id_loja=999` continuam lá. São R$ 8.120,00 de receita que o inner join deixa de fora.

**`join_receita_total` falhando com a forma certa.** Provavelmente você renomeou a coluna. O autograder soma a coluna chamada `receita_brl` — se ela virou `receita` ou `valor`, não há o que somar.

**`pivot_total_confere` fora por poucos centavos.** A tolerância é de R$ 0,50 no total. Arredonde só na hora de escrever o CSV, não a cada soma parcial.

**Os demais problemas** (403, 401, "Could not detect exercise from CWD", submissão atrasada) estão na [Parte 7 do tutorial da Aula 1](Exercicios_Aula1.md#parte-7--quando-der-errado).
