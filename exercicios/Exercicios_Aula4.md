# Exercícios da Aula 4 — ia-4.1 e ia-4.2

Dois laboratórios sobre **dar mãos, pernas e olhos a um agente** — e sobre
conferir o que ele fez:

- **ia-4.1** — o menor **servidor MCP** possível: ele expõe um arquivo seu como
  *resource*, e o host resume as suas notas sem você colar nada no chat.
- **ia-4.2** — um **jogo 2D** e um **teste E2E com Playwright** que controla o
  relógio em vez de esperá-lo.

**Prazo dos dois: 18/10.**

Os dois exercícios exigem **repositório público no GitHub**, e os dois são
**agnósticos de harness**: Claude Code, Codex, opencode, pi ou Amp — nenhum
critério pergunta qual você usou. Nenhum deles precisa de `npx skills add`
desta vez.

Se você ainda não fez o setup (Python, Git, `gh`, CLI `autograde`, login
Google), volte para a [Parte 1 do tutorial da Aula 1](Exercicios_Aula1.md#parte-1--setup-uma-vez-no-semestre).

O fluxo de entrega é o de sempre — **de dentro do diretório do repositório**:

```bash
cd <diretório do exercício>
autograde validar ia-4.1     # mostra o boletim e pergunta se quer submeter
```

Você pode resubmeter quantas vezes quiser — **a maior nota conta**.

> ⚠️ **Rode o `autograde validar` fora do terminal do agente.** Nos dois
> exercícios a CLI executa comandos de verdade na sua máquina (o seu cliente
> MCP, a sua suíte Playwright) e manda a saída como evidência. Terminal de
> agente costuma mexer em PATH e em variáveis de ambiente.

---

## Exercício ia-4.1 — Ler o mundo: um servidor MCP de recursos

O slide pede o **menor servidor MCP possível**: uma primitiva só, e a menos
glamourosa das três — `resource`, não `tool`. Nada é executado em seu nome; o
host apenas **lê**.

O que se aprende aqui não é a API do SDK. É a diferença entre *"o modelo
recebeu o texto"* e *"o modelo tem acesso à fonte"*.

### A tarefa, em três etapas

1. **Escreva `notas.md`** com 5 a 10 linhas de anotações **suas** de verdade —
   da aula, do trabalho, do que for.
2. **Implemente o servidor** que registra esse arquivo como *resource* (SDK
   Python ou TypeScript), com transporte **stdio**.
3. **Conecte ao host** (Claude Code, Claude Desktop, VS Code, Codex…) e peça
   **"resuma minhas notas"** — sem colar o conteúdo no chat.

### O que você entrega

Um repositório **público** chamado **`notas-mcp`** no seu usuário do GitHub:

```
notas-mcp/
├── notas.md                 # as suas anotações — a fonte de verdade
├── servidor_mcp.py          # o servidor: um resource, transporte stdio
├── cliente_teste.py         # o cliente que exercita o protocolo e imprime o envelope
├── evidencia-mcp.json       # o envelope da última execução (gravado pelo cliente)
└── transcript-mcp.md        # a sessão do host resumindo as notas
```

> Os cinco arquivos ficam na **raiz** do repo e os nomes batem exatamente,
> incluindo maiúsculas.
>
> **Este exercício é em Python.** O SDK TypeScript resolve o mesmo problema,
> mas a evidência que a CLI coleta é `python cliente_teste.py` — um cliente em
> Node não seria executado, e os 19 pontos da execução real ficariam de fora.

### Passo 1 — Crie o repo

```bash
gh repo create notas-mcp --public --clone
cd notas-mcp
pip install "mcp>=2"      # SDK Python; em TypeScript: npm i @modelcontextprotocol/sdk
```

### Passo 2 — O servidor

O esqueleto tem umas 20 linhas. O que o autograder confere:

- registra um **resource** (`@mcp.resource(...)`, ou `list_resources` +
  `read_resource` no servidor de baixo nível, ou `registerResource` no SDK TS);
- roda com transporte **stdio**;
- **lê `notas.md` do disco** — quem colar o texto das notas dentro do código
  perde o ponto, e perde o exercício junto.

> **Leia o arquivo dentro da função do resource, não no import.** É isso que
> separa um recurso de um texto colado: a cada leitura, o host recebe a versão
> atual do arquivo. Se você ler uma vez no topo do módulo, criou uma colagem
> com passos extras.

### Passo 3 — O cliente de teste e o envelope

O autograder não tem como conectar um host à sua máquina, então **quem prova
que o protocolo funcionou é um cliente que você escreve**: ele sobe o seu
servidor por stdio, chama `list_resources`, chama `read_resource` e imprime
este envelope JSON — que também é gravado em `evidencia-mcp.json`:

```json
{
  "transporte": "stdio",
  "servidor": "notas-mcp",
  "resources": ["notas://minhas-notas"],
  "resource_lido": "notas://minhas-notas",
  "conteudo_chars": 1171,
  "conteudo_linhas": 9,
  "primeira_linha": "# Anotações — Agentes de IA (MCDIA/IDP)"
}
```

Regras do envelope — **é o contrato do exercício**:

| campo | o que tem que ser |
|---|---|
| `transporte` | literalmente `"stdio"` |
| `resources` | a lista devolvida por `list_resources`, com pelo menos **uma URI com esquema** (`notas://…`, `file:///…`, o que você escolher) |
| `conteudo_chars` | o tamanho do que voltou do `read_resource` — precisa ser **≥ 100** |
| `primeira_linha` | a primeira linha não vazia do conteúdo lido, **igualzinha** a como ela aparece no `notas.md` |

A `primeira_linha` é o que amarra tudo: o autograder a extrai do
`evidencia-mcp.json` e exige que ela exista **dentro do `notas.md` entregue**.
É assim que se prova que o conteúdo atravessou o protocolo em vez de ter sido
inventado pelo cliente.

- Serialize com `ensure_ascii=False` — acento escapado em `\uXXXX` não bate com
  o arquivo.
- Escolha uma primeira linha sem aspas e sem barra invertida; o JSON escapa
  esses caracteres e a comparação falha por um detalhe bobo.

Rode **de dentro do repo**, antes de validar:

```bash
python cliente_teste.py
```

### Passo 4 — Conecte ao host e salve o transcript

Registre o servidor no seu host e peça o resumo. Em Claude Code, por exemplo:

```bash
claude mcp add notas-mcp -s local -- python servidor_mcp.py
claude mcp list      # notas-mcp: ... - ✔ Connected
```

Depois, na sessão: *"liste os recursos MCP do servidor notas-mcp, leia
`notas://minhas-notas` e resuma minhas notas"*.

Salve a sessão em **`transcript-mcp.md`**. Um juiz LLM lê esse arquivo **junto
com o seu `notas.md`** e responde a uma pergunta só: *o host leu pelo servidor,
ou o aluno colou o texto?* Então o transcript precisa mostrar:

- o host **acessando o recurso** (a listagem, a leitura da URI, o nome do
  servidor) — e não você colando o conteúdo;
- uma resposta que fala do **conteúdo real** do seu `notas.md`, com coisas que
  só existem lá;
- qual servidor e qual URI foram lidos, de modo que outra pessoa saiba o que
  entrou no contexto.

Qualquer host serve, e qualquer formato serve (colagem da tela, log
estruturado, captura em texto).

### Passo 5 — Valide e responda as duas perguntas

```bash
autograde validar ia-4.1
```

**Não há arquivo de reflexão neste exercício** — as duas perguntas são feitas
na CLI, na hora de submeter, e valem 30 dos 100 pontos:

1. Por que expor as notas como *resource* é diferente de colar o texto no
   prompt, nos três eixos do slide: **escala, atualização e auditoria**.
2. Dos três ataques da aula — *tool poisoning*, *rug pull*, *typosquatting* —
   qual atingiria alguém que instalasse um servidor como o seu, e que
   **mitigação** você adotaria.

A CLI roda, na sua máquina: `gh --version`, `gh auth status`, `gh repo view` e
**`python cliente_teste.py`** (com `python3` como alternativa).

### Critérios do ia-4.1

| Critério | Peso | O que precisa |
|---|---:|---|
| `repo_existe` | 2 | o repo existe no seu usuário |
| `repo_publico` | 2 | visibilidade = public |
| `repo_nome_notas_mcp` | 1 | o repo se chama `notas-mcp` |
| `gh_autenticado` | 2 | `gh auth status` OK, na conta do roster |
| `gh_repo_view_ok` | 1 | `gh repo view` funciona no repo |
| `notas_existe` | 2 | `notas.md` na raiz |
| `notas_5_linhas` | 3 | ≥ 5 linhas não vazias |
| `servidor_existe` | 2 | `servidor_mcp.py` na raiz |
| `servidor_registra_resource` | 6 | registra um **resource** |
| `servidor_transporte_stdio` | 3 | transporte stdio |
| `servidor_le_notas` | 3 | lê `notas.md` do disco |
| `cliente_existe` | 2 | `cliente_teste.py` na raiz |
| `cliente_usa_sdk_mcp` | 3 | fala MCP pelo SDK |
| `cliente_grava_evidencia` | 2 | grava `evidencia-mcp.json` |
| `mcp_envelope_stdio` | 4 | envelope com `"transporte": "stdio"` |
| `mcp_lista_resources` | 6 | `list_resources` devolveu ≥ 1 URI |
| `mcp_leu_conteudo` | 5 | `conteudo_chars` ≥ 100 |
| `mcp_sem_traceback` | 4 | o cliente rodou sem estourar exceção |
| `evidencia_existe` | 2 | `evidencia-mcp.json` na raiz |
| `evidencia_bate_com_notas` | 4 | a `primeira_linha` existe no `notas.md` |
| `transcript_existe` | 2 | `transcript-mcp.md` na raiz |
| `transcript_qualidade` | 6 | o host leu pelo servidor (LLM avalia) |
| `sem_segredos_versionados` | 3 | nenhum `.env`, `.pem`, `credentials.json`… |
| pergunta 1 | 18 | resource x colagem — respondida na CLI |
| pergunta 2 | 12 | ataque e mitigação — respondida na CLI |
| **Total** | **100** | |

---

## Exercício ia-4.2 — Jogo 2D e teste E2E com Playwright

O jogo é o pretexto. O exercício é o **verificador**.

É a ponte entre dois pedaços da aula que parecem desconexos: o Playwright MCP
(slide 24) e os quatro mecanismos de *test-time compute* (slide 30). "Busca e
revisão" — escreve, roda o teste, lê o erro, corrige — é o mecanismo que o
agente de código usa, e o ganho dele **é limitado pela qualidade do
verificador**. Um teste que espera 3 segundos e torce não verifica nada. Um
teste que controla o relógio verifica.

### A tarefa, em três etapas

1. **Construa o jogo** — Snake clássico, HTML/CSS/JS puro, **um só arquivo**:
   - grade fixa; a cobra avança sozinha a cada tick e muda de direção pelas
     setas, **sem giro de 180°**;
   - comer a maçã: **+1 no placar e +1 segmento**; nova maçã em célula livre;
   - colisão com parede ou com o próprio corpo = fim de jogo: exibe
     **`#gameover`** e **congela o placar**.
2. **Teste ponta a ponta com Playwright** — três cenários, no mínimo: placar
   inicia em 0 · comer a maçã incrementa · colisão exibe `#gameover` e congela
   o placar. Use **`page.clock`** para adiantar o tempo. **Nenhum
   `waitForTimeout`.**
3. **Feche o ciclo** — rodar até 100% verde e **explicar cada falha
   corrigida**.

### O que você entrega

Um repositório **público** chamado **`snake-e2e`**:

```
snake-e2e/
├── index.html               # o jogo inteiro: HTML + CSS + JS, um arquivo só
├── tests/
│   └── snake.spec.js        # a suíte E2E — este nome exato
├── playwright.config.js     # o config do Playwright
├── package.json             # com @playwright/test em devDependencies
├── .gitignore               # node_modules/, test-results/, playwright-report/
└── E2E.md                   # o ciclo até o verde: o que quebrou e o que mudou
```

> **`tests/snake.spec.js`, em JavaScript.** Se você escrever em TypeScript, o
> autograder não acha o arquivo e você perde 16 pontos com a suíte verde.

### Passo 1 — Crie o repo e instale o Playwright

```bash
gh repo create snake-e2e --public --clone
cd snake-e2e
npm init -y
npm i -D @playwright/test
npx playwright install chromium     # baixa o navegador; sem isso a suíte nem roda
```

### Passo 2 — O jogo, com determinismo de propósito

O que o autograder confere no `index.html`: os elementos **`#score`** e
**`#gameover`**, as **quatro setas** (`ArrowUp`/`ArrowDown`/`ArrowLeft`/
`ArrowRight`), um **relógio** (`setInterval`, `setTimeout` ou
`requestAnimationFrame`) e **nenhum `<script src=...>` nem CSS externo** — é
"um arquivo só" para valer.

> **Determinismo é decisão de projeto do JOGO, não do teste.** Se a primeira
> maçã cai num lugar aleatório a cada carga, você não consegue afirmar "4 ticks
> e o placar vira 1" — e acaba escrevendo um teste que espia o estado interno
> por `page.evaluate`, que é o oposto de um teste ponta a ponta. Semeie o PRNG
> e fixe a primeira maçã num ponto conhecido, à frente da cabeça. O autograder
> não cobra o como; cobra o resultado.

### Passo 3 — Os testes: controlar o tempo, não esperá-lo

```js
test.beforeEach(async ({ page }) => {
  await page.clock.install();   // ANTES do goto: o setInterval nasce na carga
  await page.goto(JOGO);
});

test('comer a maçã soma 1 no placar', async ({ page }) => {
  await page.clock.runFor(4 * TICK);         // 4 ticks, e não 600 ms de espera
  await expect(page.locator('#score')).toHaveText('1');
});
```

Dois critérios carregam o peso do bloco (10 dos 16 pontos): **`page.clock`
presente** e **`.waitForTimeout(` ausente**. Dá para ter a suíte verde e perder
os dois — verde por espera cega é exatamente o que o exercício quer eliminar.

### Passo 4 — `E2E.md` e validação

De 5 linhas para cima, sobre **o ciclo até o verde**: qual cenário quebrou,
qual valor apareceu no lugar do esperado, e o que você mudou — o jogo ou a
asserção. Um juiz LLM lê esse arquivo **junto com a sua suíte** e confere se o
relato bate com o teste entregue. "Deu erro e eu corrigi" não conta.

```bash
autograde validar ia-4.2
```

A CLI roda, na sua máquina:
**`npm exec -y playwright -- test --reporter=line`** (o mesmo que
`npx playwright test`, com o `npm` que está na allowlist). O timeout é de 300 s.

As duas perguntas da CLI valem 30 dos 100 pontos:

1. Uma **falha concreta** que a sua suíte pegou, e o que você mudou — o jogo ou
   a asserção — com o porquê.
2. Por que `page.clock` em vez de `waitForTimeout`: o que muda no tempo da
   suíte e na confiança que um verde merece.

### Critérios do ia-4.2

| Critério | Peso | O que precisa |
|---|---:|---|
| `repo_existe` | 2 | o repo existe no seu usuário |
| `repo_publico` | 2 | visibilidade = public |
| `repo_nome_snake_e2e` | 1 | o repo se chama `snake-e2e` |
| `gh_autenticado` | 2 | `gh auth status` OK, na conta do roster |
| `gh_repo_view_ok` | 1 | `gh repo view` funciona no repo |
| `jogo_existe` | 2 | `index.html` na raiz |
| `jogo_arquivo_unico` | 3 | sem `<script src>` e sem CSS externo |
| `jogo_placar` | 3 | elemento `#score` |
| `jogo_gameover` | 4 | elemento `#gameover` |
| `jogo_setas` | 4 | as quatro setas tratadas |
| `jogo_tick_automatico` | 4 | a cobra avança sozinha |
| `teste_existe` | 2 | `tests/snake.spec.js` |
| `teste_usa_clock` | 6 | ≥ 2 chamadas a `page.clock.` |
| `teste_sem_wait_timeout` | 4 | nenhum `.waitForTimeout(` |
| `teste_tres_cenarios` | 4 | ≥ 3 blocos `test(` |
| `playwright_tres_verdes` | 10 | ≥ 3 testes passando |
| `playwright_sem_falha` | 6 | nada `failed`, nada `flaky`, navegador instalado |
| `reflexao_existe` | 2 | `E2E.md` na raiz |
| `reflexao_tamanho` | 2 | ≥ 5 linhas não vazias |
| `reflexao_qualidade` | 3 | relato específico e coerente com a suíte (LLM avalia) |
| `sem_segredos_versionados` | 3 | nenhum `.env`, `.pem`, `credentials.json`… |
| pergunta 1 | 18 | a falha concreta — respondida na CLI |
| pergunta 2 | 12 | `page.clock` x `waitForTimeout` — respondida na CLI |
| **Total** | **100** | |

---

## Quando der errado

**`ModuleNotFoundError: No module named 'mcp.server.fastmcp'`.** Você está no
SDK Python **2.x**, onde o `FastMCP` virou `MCPServer`:
`from mcp.server.mcpserver import MCPServer`. Código de tutorial antigo é 1.x —
ou porte o import, ou fixe `pip install "mcp<2"`. O autograder aceita os dois.

**`InitializeResult object has no attribute 'serverInfo'`.** Mesma troca de
versão, do lado do cliente: no 2.x o campo é `server_info` (snake_case).

**O envelope sai junto com log do servidor.** Normal, e não reprova: a CLI
concatena o *stderr* no *stdout* antes de mandar, e por isso o autograder
procura os campos do envelope por regex, não fazendo `json.loads` da saída
inteira. O que **não** pode é o cliente estourar exceção — `Traceback` na saída
zera 4 pontos.

**`evidencia_bate_com_notas` falhando com tudo no lugar.** A `primeira_linha`
do envelope tem que aparecer *literalmente* dentro do `notas.md`. As duas
causas comuns: `json.dumps` sem `ensure_ascii=False` (acento vira `ç`) e
uma primeira linha com aspas ou barra invertida, que o JSON escapa.

**`mcp_*` zerado com o cliente funcionando.** A CLI roda `python
cliente_teste.py` **no diretório de onde você chamou `autograde validar`**.
Rode da raiz do repo, e faça o seu cliente resolver o caminho do servidor
relativo ao próprio arquivo (`Path(__file__).parent`), não ao cwd.

**`playwright_sem_falha` zerado com "browserType.launch".** Faltou
`npx playwright install chromium`. O navegador não vem com o pacote.

**`teste_sem_wait_timeout` zerado e não há espera nenhuma no teste.** O
autograder procura a **chamada** `.waitForTimeout(` — inclusive comentada.
Falar sobre ela em prosa ("nenhum waitForTimeout aqui") não custa ponto;
deixar a linha comentada, sim.

**A suíte fica verde mas lenta.** Quase sempre é `page.clock.install()` depois
do `goto`: o `setInterval` do jogo já nasceu com o relógio real, e os `expect`
passam porque *esperaram de verdade* dentro do auto-waiting. Verde por tempo
real é o bug que este exercício existe para você enxergar — compare o tempo da
suíte antes e depois de mover o `install()`.

**Um teste quebra porque o placar veio 2 e você esperava 1.** Se a sua segunda
maçã cai no caminho da cobra, o placar legitimamente passa de 1 antes da
parede. O erro está na asserção, não no jogo: o requisito diz que o placar
**congela**, não quanto ele vale. Leia o placar na hora da morte e compare com
ele mesmo depois de mais N ticks.

**Critério de arquivo zerado com o arquivo no lugar.** O caminho bate
exatamente, incluindo maiúsculas: `E2E.md`, não `e2e.md`; `tests/snake.spec.js`,
não `tests/snake.spec.ts`; `evidencia-mcp.json` na raiz.

**Os demais problemas** (403, 401, "Could not detect exercise from CWD",
submissão atrasada) estão na [Parte 7 do tutorial da Aula 1](Exercicios_Aula1.md#parte-7--quando-der-errado).
