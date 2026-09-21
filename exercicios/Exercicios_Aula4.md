# Exercícios da Aula 4 — ia-4.1, ia-4.2 e ia-4.3

Três laboratórios sobre **dar mãos, pernas e olhos a um agente** — e sobre
conferir o que ele fez:

- **ia-4.1** — o menor **servidor MCP** possível: ele expõe um arquivo seu como
  *resource*, e o host resume as suas notas sem você colar nada no chat.
- **ia-4.2** — um **jogo 2D** e um **teste E2E com Playwright** que controla o
  relógio em vez de esperá-lo.
- **ia-4.3** — um **repositório privado de artefatos** que governa o seu agente,
  instalado por `git clone` + **um** script idempotente — e desenhado numa
  entrevista em que quem decide a arquitetura é você.

**Prazo dos três: 18/10.**

**O ia-4.1 e o ia-4.2 não exigem repositório.** Não é preciso criar nada no
GitHub, nem sequer rodar `git init`: uma pasta comum na sua máquina basta. Quem
preferir versionar continua podendo — o autograder não olha. **O ia-4.3 é o
contrário**: o repositório *é* o entregável, e ele tem que ser **privado**. Os
três são **agnósticos de harness**: Claude Code, Codex, opencode, pi ou Amp,
nenhum critério pergunta qual você usou. Nenhum deles precisa de
`npx skills add` desta vez.

> A amarra de identidade continua de pé: o login Google diz quem você é e
> `gh auth status` confere a sua conta do GitHub contra o `github_username` do
> roster. Ou seja, o `gh` ainda precisa estar **autenticado** — o que não
> precisa existir é **repositório**.

Se você ainda não fez o setup (Python, Git, `gh`, CLI `autograde`, login
Google), volte para a [Parte 1 do tutorial da Aula 1](Exercicios_Aula1.md#parte-1--setup-uma-vez-no-semestre).

O fluxo de entrega é o de sempre — **de dentro da pasta do exercício**:

```bash
cd <diretório do exercício>
autograde validar ia-4.1     # mostra o boletim e pergunta se quer submeter
```

No ia-4.3, "o diretório do exercício" é o **clone do seu repositório de
artefatos** — é de lá que o `gh` e o `git` enxergam o repositório privado.

Você pode resubmeter quantas vezes quiser — **a maior nota conta**.

> ⚠️ **Rode o `autograde validar` fora do terminal do agente.** Nos três
> exercícios a CLI executa comandos de verdade na sua máquina (o seu cliente
> MCP, a sua suíte Playwright, o seu `gh` e o seu `git`) e manda a saída como
> evidência. Terminal de agente costuma mexer em PATH e em variáveis de
> ambiente.

---

## Exercício ia-4.1 — Ler o mundo: um servidor MCP de anotações pessoais

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
3. **Conecte ao host** (o slide pede Claude Desktop ou Claude Code; qualquer
   host que fale MCP serve) e peça
   **"resuma minhas notas"** — sem colar o conteúdo no chat.

### O que você entrega

Uma pasta chamada **`notas-mcp`** na sua máquina — não precisa ser repositório:

```
notas-mcp/
├── notas.md                 # as suas anotações — a fonte de verdade
├── servidor_mcp.py          # o servidor: um resource, transporte stdio
├── cliente_teste.py         # o cliente que exercita o protocolo e imprime o envelope
├── evidencia-mcp.json       # o envelope da última execução (gravado pelo cliente)
└── transcript-mcp.md        # a sessão do host resumindo as notas
```

> Os cinco arquivos ficam na **raiz da pasta** e os nomes batem exatamente,
> incluindo maiúsculas.
>
> **Este exercício é em Python.** O SDK TypeScript resolve o mesmo problema,
> mas a evidência que a CLI coleta é `python cliente_teste.py` — um cliente em
> Node não seria executado, e os 19 pontos da execução real ficariam de fora.

### Passo 1 — Crie a pasta

```bash
mkdir notas-mcp && cd notas-mcp
pip install "mcp>=2"      # SDK Python; em TypeScript: npm i @modelcontextprotocol/sdk
```

> Sem `git init` e sem `gh repo create`: o autograder lê os arquivos e roda os
> comandos **nesta pasta**, na sua máquina.

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

Rode **de dentro da pasta**, antes de validar:

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

A CLI roda, na sua máquina: `gh --version`, `gh auth status` e
**`python cliente_teste.py`** (com `python3` como alternativa). Não há mais
`gh repo view` — não há repo para consultar.

### Critérios do ia-4.1

| Critério | Peso | O que precisa |
|---|---:|---|
| `gh_autenticado` | 2 | `gh auth status` OK, na conta do roster |
| `notas_existe` | 2 | `notas.md` na raiz da pasta |
| `notas_5_linhas` | 3 | ≥ 5 linhas não vazias |
| `servidor_existe` | 2 | `servidor_mcp.py` na raiz |
| `servidor_registra_resource` | 6 | registra um **resource** |
| `servidor_transporte_stdio` | 3 | transporte stdio |
| `servidor_le_notas` | 3 | lê `notas.md` do disco |
| `cliente_existe` | 2 | `cliente_teste.py` na raiz |
| `cliente_usa_sdk_mcp` | 3 | fala MCP pelo SDK |
| `cliente_grava_evidencia` | 2 | grava `evidencia-mcp.json` |
| `mcp_envelope_stdio` | 5 | envelope com `"transporte": "stdio"` |
| `mcp_lista_resources` | 7 | `list_resources` devolveu ≥ 1 URI |
| `mcp_leu_conteudo` | 6 | `conteudo_chars` ≥ 100 |
| `mcp_sem_traceback` | 5 | o cliente rodou sem estourar exceção |
| `evidencia_existe` | 2 | `evidencia-mcp.json` na raiz |
| `evidencia_bate_com_notas` | 7 | a `primeira_linha` existe no `notas.md` |
| `transcript_existe` | 2 | `transcript-mcp.md` na raiz |
| `transcript_qualidade` | 8 | o host leu pelo servidor (LLM avalia) |
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

Uma pasta chamada **`snake-e2e`** — também sem exigência de repositório:

```
snake-e2e/
├── index.html               # o jogo inteiro: HTML + CSS + JS, um arquivo só
├── tests/
│   └── snake.spec.js        # a suíte E2E — este nome exato
├── evidencia-colisao.png     # o screenshot da colisão, gravado pela própria suíte
├── playwright.config.js     # o config do Playwright
├── package.json             # com @playwright/test em devDependencies
├── .gitignore               # opcional, se versionar: node_modules/, test-results/
└── E2E.md                   # o ciclo até o verde: o que quebrou e o que mudou
```

> **`tests/snake.spec.js`, em JavaScript.** Se você escrever em TypeScript, o
> autograder não acha o arquivo e você perde 19 pontos com a suíte verde.

### Passo 1 — Crie a pasta e instale o Playwright

```bash
mkdir snake-e2e && cd snake-e2e
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

> O slide resume o exercício; **este arquivo é o contrato do autograder**.
> `page.clock` continua obrigatório aqui, e `waitForTimeout` continua proibido
> — valem 10 dos 16 pontos do bloco de testes.

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

### Passo 4 — O screenshot da colisão

O enunciado pede **um screenshot de evidência mostrando o teste da colisão
exibindo o `#gameover`**. Ele não é um anexo tirado à mão: quem grava é a
suíte, no cenário da colisão, logo depois de o fim de jogo aparecer.

```js
await page.clock.runFor(ticks(16));
await expect(page.locator('#gameover')).toBeVisible();
await page.screenshot({ path: EVIDENCIA });   // evidencia-colisao.png na raiz
```

Três detalhes que decidem os 4 pontos:

- o arquivo se chama **`evidencia-colisao.png`** e fica na **raiz** da pasta —
  não em `test-results/`, que é onde o Playwright joga anexo por padrão;
- resolva o caminho a partir de `__dirname` (`path.join(__dirname, '..',
  'evidencia-colisao.png')`), senão ele cai onde quer que a suíte tenha sido
  chamada;
- é **a suíte** que precisa conter a chamada (`page.screenshot(` ou
  `toHaveScreenshot(`) — um print de tela colado na pasta passa em dois
  critérios e perde o terceiro.

Como o `autograde validar` roda a suíte **antes** de ler os artefatos, o PNG que
chega ao corretor é sempre o da rodada que acabou de acontecer.

### Passo 5 — `E2E.md` e validação

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
| `gh_autenticado` | 2 | `gh auth status` OK, na conta do roster |
| `jogo_existe` | 2 | `index.html` na raiz da pasta |
| `jogo_arquivo_unico` | 3 | sem `<script src>` e sem CSS externo |
| `jogo_placar` | 3 | elemento `#score` |
| `jogo_gameover` | 4 | elemento `#gameover` |
| `jogo_setas` | 4 | as quatro setas tratadas |
| `jogo_tick_automatico` | 4 | a cobra avança sozinha |
| `teste_existe` | 2 | `tests/snake.spec.js` |
| `teste_usa_clock` | 6 | ≥ 2 chamadas a `page.clock.` |
| `teste_sem_wait_timeout` | 4 | nenhum `.waitForTimeout(` |
| `teste_tres_cenarios` | 4 | ≥ 3 blocos `test(` |
| `screenshot_existe` | 2 | `evidencia-colisao.png` na raiz |
| `screenshot_e_png` | 1 | é um PNG de verdade, não um arquivo vazio |
| `teste_gera_screenshot` | 1 | a suíte contém `page.screenshot(` |
| `playwright_tres_verdes` | 12 | ≥ 3 testes passando |
| `playwright_sem_falha` | 7 | nada `failed`, nada `flaky`, navegador instalado |
| `reflexao_existe` | 2 | `E2E.md` na raiz |
| `reflexao_tamanho` | 2 | ≥ 5 linhas não vazias |
| `reflexao_qualidade` | 5 | relato específico e coerente com a suíte (LLM avalia) |
| pergunta 1 | 18 | a falha concreta — respondida na CLI |
| pergunta 2 | 12 | `page.clock` x `waitForTimeout` — respondida na CLI |
| **Total** | **100** | |

---

## Exercício ia-4.3 — Um repositório de artefatos para o seu agente

Nos dois exercícios anteriores você deu ao agente uma fonte de dados e um
verificador. Neste você trata do terceiro lado: **o que o agente leva consigo em
toda sessão, em qualquer projeto** — as instruções globais, as skills, os hooks,
os scripts. Hoje isso mora espalhado dentro de `~/.claude` ou `~/.agents`, não é
versionado, não vai junto para a próxima máquina e ninguém sabe dizer o que
mudou desde a semana passada.

O entregável é um **repositório GitHub privado** que concentre esses artefatos e
que se instale em dois passos: `git clone` e **um** script.

**A parte que vale mais não produz arquivo nenhum.** Antes de qualquer código,
você cola o prompt de apoio e o agente **entrevista você** sobre a arquitetura:
como organizar as pastas, o que é artefato e o que é gerador, o que migra do seu
setup de hoje e o que fica de fora. O prompt não diz em que linguagem escrever o
script nem como declarar os pacotes — quem decide isso é o **seu** agente,
olhando a **sua** máquina, e ele tem que defender a escolha. Se o agente propõe e
você só assina embaixo, o exercício não aconteceu: a entrega exige **duas
decisões em que você contrariou a recomendação dele**, com o motivo.

### A tarefa, em três etapas

1. **Prepare e entreviste.** Instale a skill de entrevista (`/grill-me` no
   Claude Code; uma skill de entrevista em `~/.agents/skills/` no Codex),
   confira `gh auth status`, e cole **na íntegra** a variante do seu harness em
   [`prompts/prompt-repo-artefatos-agentes.md`](../prompts/prompt-repo-artefatos-agentes.md).
   **Não deixe o agente escrever nenhum arquivo antes de vocês fecharem o
   desenho.**
2. **Construa o repositório.** Privado, com no mínimo: o arquivo de instruções
   globais do harness, skills, **exatamente dois** hooks (um `PreToolUse` que
   bloqueia escrita num caminho proibido, um `PostToolUse` que formata ou linta
   depois de uma edição) e o script de instalação — idempotente, com backup por
   timestamp e `--uninstall`.
3. **Prove que o script se comporta.** Rode-o **duas vezes seguidas** e depois
   com `--uninstall`, e guarde a saída bruta das três execuções.

### O que você entrega

O **clone do seu repositório privado**, na sua máquina. É de dentro dele que
você roda `autograde validar ia-4.3`:

```
<seu-repo>/
├── README.md                  # em pt-BR: como instalar, como desinstalar, e o limite do caminho
├── CLAUDE.md                  # ou AGENTS.md — as instruções globais do harness
├── ENTREVISTA.md              # o registro da entrevista + as duas divergências
├── evidencia-instalacao.txt   # a saída bruta das três execuções
├── install.<o que você escolher>   # o script único
├── hooks/…                    # os dois hooks, como arquivos versionados
└── skills/<nome>/SKILL.md     # pelo menos uma skill
```

> **Só conta o que está commitado.** O autograder lê a árvore com `git ls-files`,
> que não enxerga arquivo fora do commit. Faça `git add`/`git commit`/`git push`
> **antes** de validar.

O que é livre e o que é fixo:

| livre — você e o seu agente decidem | fixo — é o contrato do autograder |
|---|---|
| a linguagem do script e o mecanismo de instalação | o nome do script tem **`install`** nele (em inglês), e a extensão não é `.md`/`.txt`/`.rst` |
| como declarar os pacotes (ou não declarar) | as instruções globais se chamam **`CLAUDE.md`** ou **`AGENTS.md`**, com essas maiúsculas |
| a organização das pastas e o nome das skills | pelo menos um **`SKILL.md`** versionado |
| o harness (Claude Code ou Codex) e o SO | os dois hooks são **arquivos** versionados, com `hook` no caminho |
| o conteúdo das regras globais | `README.md`, `ENTREVISTA.md` e `evidencia-instalacao.txt`, com esses nomes exatos |

### Passo 1 — A entrevista, e o registro dela

Salve o registro em **`ENTREVISTA.md`**: cada pergunta que o agente fez, a
recomendação que veio junto e a sua resposta. No fim, uma seção com as **duas
decisões em que você contrariou a recomendação** — o que ele recomendou, o que
você escolheu, e o **porquê**. "Preferência pessoal" não é porquê; "não quero
versionar skill de terceiro que eu não controlo" é.

Um juiz LLM lê esse arquivo e responde a duas perguntas separadas: *isto foi uma
entrevista ou um relatório?* e *as duas divergências existem e estão
justificadas?* São 14 dos 100 pontos.

### Passo 2 — O repositório privado

```bash
gh repo create <nome> --private --source=. --push
gh repo view --json name,visibility,isPrivate     # "isPrivate": true
```

**Privado de verdade — e por isso o autograder não olha pelo GitHub.** O backend
não enxerga repositório privado de aluno (a API responde 404), então a evidência
do repositório vem da **sua** máquina: o `gh` e o `git` que rodam no seu
terminal, de dentro do clone, é que dizem que ele existe, que é privado e o que
há na árvore. Deixar o repositório público para "facilitar" perde 8 pontos e
contraria a restrição 1 do prompt.

**Nenhum segredo entra.** Repositório privado é clonado para outras máquinas,
entra em backup e vira público com um clique. O autograder reprova a árvore que
contiver `.env`, `credentials.json`, `id_rsa`, `*.pem`, `*.key`, `.npmrc` e
afins — `.env.example` não conta.

### Passo 3 — `evidencia-instalacao.txt`

Idempotência não se verifica lendo o script: verifica-se **rodando duas vezes e
olhando a segunda**. O arquivo tem três blocos, nesta ordem, cada um precedido
pela linha de comando que o gerou — prefixada por `$ ` ou pelo prompt do
PowerShell (`PS C:\…>`):

```
$ ./install.sh
[install] backup em ~/.claude/backups/2026-10-14T21-03-11
... 4 arquivo(s) alterado(s)

$ ./install.sh
[install] nada a salvar: nenhum arquivo sera alterado, backup nao criado
... 0 arquivo(s) alterado(s)

$ ./install.sh --uninstall
[uninstall] settings.json restaurado do backup
...
```

É saída **bruta**, copiada do terminal — não um resumo escrito depois. O juiz
LLM lê esse arquivo junto com o seu README e procura três coisas: a segunda
execução dizendo explicitamente que nada mudou, a terceira mostrando **o que**
foi restaurado, e coerência com o que o README promete. São 9 pontos, o maior
critério isolado do exercício.

### Passo 4 — Valide e responda as duas perguntas

```bash
cd <clone do seu repositório>
autograde validar ia-4.3
```

Não há arquivo de reflexão: as duas perguntas são feitas na CLI, na hora de
submeter, e valem 30 dos 100 pontos:

1. Por que o arquivo de settings do harness **não pode ser tratado como um
   dotfile qualquer**, symlinkado para o repositório. (É a pergunta de
   fechamento do slide — e a armadilha que o exercício existe para ensinar.)
2. O que o seu script verifica antes de escrever, para que a segunda execução
   não faça nada; e o que o `--uninstall` restaura — **e o que ele não consegue
   restaurar**.

A CLI roda, na sua máquina: `gh --version`, `gh auth status`,
`gh repo view --json name,visibility,isPrivate` e `git ls-files`. Os dois
últimos **sem nome de repositório**: eles leem o repo do diretório corrente, que
é por isso que você precisa validar de dentro do clone.

### Critérios do ia-4.3

| Critério | Peso | O que precisa |
|---|---:|---|
| `gh_autenticado` | 2 | `gh auth status` OK, na conta do roster |
| `repo_existe` | 3 | `gh repo view` devolve um repositório no diretório corrente |
| `repo_privado` | 8 | `"isPrivate": true` / `"visibility": "PRIVATE"` |
| `instrucoes_globais_versionadas` | 3 | `CLAUDE.md` ou `AGENTS.md` commitado |
| `script_instalacao` | 3 | um script versionado com `install` no nome |
| `skill_versionada` | 3 | pelo menos um `SKILL.md` |
| `dois_hooks` | 3 | dois arquivos versionados com `hook` no caminho |
| `sem_segredos` | 3 | nenhum arquivo com cara de segredo na árvore |
| `evidencia_existe` | 2 | `evidencia-instalacao.txt` na raiz |
| `evidencia_tres_execucoes` | 5 | três blocos, cada um com a sua linha de comando |
| `evidencia_uninstall` | 4 | a terceira execução é o `--uninstall` |
| `evidencia_idempotente` | 9 | a 2ª execução não mudou nada e a 3ª restaurou (LLM avalia) |
| `entrevista_existe` | 2 | `ENTREVISTA.md` na raiz |
| `entrevista_tamanho` | 2 | ≥ 20 linhas não vazias |
| `entrevista_qualidade` | 7 | foi entrevista, com decisões suas (LLM avalia) |
| `entrevista_duas_divergencias` | 7 | as duas divergências, com motivo (LLM avalia) |
| `readme_existe` | 1 | `README.md` na raiz |
| `readme_qualidade` | 3 | instalação em dois passos, desinstalação e o limite declarado |
| pergunta 1 | 18 | settings x dotfile — respondida na CLI |
| pergunta 2 | 12 | idempotência e o que o `--uninstall` não desfaz — na CLI |
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
Rode da raiz da pasta do exercício, e faça o seu cliente resolver o caminho do
servidor relativo ao próprio arquivo (`Path(__file__).parent`), não ao cwd.

**`screenshot_existe` zerado com o teste passando.** O Playwright grava
anexos em `test-results/`; o autograder lê **`evidencia-colisao.png` na raiz da
pasta**. Passe o caminho absoluto no `page.screenshot({ path: ... })`, montado a
partir de `__dirname`.

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

**`repo_existe` e `repo_privado` zerados com o repositório criado.** Os dois
comandos rodam **sem nome de repositório**: eles leem o remote do diretório
corrente. Validar de fora do clone (ou de uma pasta que não é repo git) zera os
11 pontos com o repositório intacto no GitHub. `cd` para dentro do clone e
confira com `gh repo view --json name,visibility,isPrivate`.

**Critério de árvore zerado com o arquivo no lugar.** `git ls-files` lista só o
que está **commitado**. Arquivo criado e não adicionado não existe para o
autograder — e é o caso mais comum com o `evidencia-instalacao.txt`, que você
gera por último. `git add -A && git commit && git push` antes de validar.

**`dois_hooks` zerado com os dois hooks funcionando.** O autograder procura
**dois caminhos versionados com `hook`** — arquivos. Hook declarado só como
string de comando dentro do fragmento de settings funciona no harness e não
passa aqui, de propósito: a restrição 9 do prompt pede dois hooks *como exemplos
que ensinam o formato*, e um comando inline não ensina formato a quem clonar.

**`script_instalacao` zerado com o script pronto.** Ou o nome está em português
(`instalar.ps1`), ou o que existe é um `INSTALL.md` explicando como instalar à
mão. O nome do arquivo precisa ter `install`, e a extensão não pode ser de
documento — nomes de arquivo em inglês é regra do próprio prompt.

**`evidencia_tres_execucoes` zerado com as três execuções no arquivo.** Faltou a
linha de comando prefixada: cada bloco começa com `$ ` (ou com o prompt do
PowerShell, `PS C:\…>`) seguido do comando. Sem esse prefixo o autograder não
tem como separar um bloco do outro.

**Os demais problemas** (403, 401, "Could not detect exercise from CWD",
submissão atrasada) estão na [Parte 7 do tutorial da Aula 1](Exercicios_Aula1.md#parte-7--quando-der-errado).
