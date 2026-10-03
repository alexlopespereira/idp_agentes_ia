# Exercícios da Aula 6 — ia-6.1 e ia-6.2

Dois laboratórios sobre a sua dissertação, a partir do fork do
[TemplateLatexIDP](https://github.com/alexlopespereira/TemplateLatexIDP):

- **ia-6.1** — a **dissertação dummy**: o template preenchido com os seus dados,
  dois parágrafos em cada capítulo, citações, figura, tabela e três obras suas
  no `.bib`, compilado em `main.pdf`. É o setup do trabalho que você vai
  escrever de verdade depois.
- **ia-6.2** — o **mapa da contribuição científica**, feito com a skill
  `/wayfinder`: um mapa de decisões nas Issues do GitHub, com um ticket de
  pesquisa (o agente investiga sozinho) e um de *grilling* (o agente pergunta,
  você decide) resolvidos. Pode ser no fork do ia-6.1 **ou num repositório
  privado seu**.

**Prazo dos dois: o do calendário da turma** (o `autograde validar` avisa se a
submissão está atrasada).

**O autograder não olha o GitHub por você.** Tudo é medido **de dentro do
clone**, na sua máquina, com o seu `gh` autenticado — por isso o `autograde
validar` tem que rodar na raiz do repositório. O ia-6.1 exige o fork (que o
GitHub obriga a ser público, como o template); o ia-6.2 aceita **qualquer
repositório seu, público ou privado**: nem o autograder nem o professor
precisam de acesso a ele. O nome é livre: pode renomear para o título da
pesquisa.

Se você ainda não fez o setup (Python, Git, `gh`, CLI `autograde`, login
Google), volte para a [Parte 1 do tutorial da Aula 1](Exercicios_Aula1.md#parte-1--setup-uma-vez-no-semestre).

```bash
cd <raiz do seu fork>
autograde validar ia-6.1     # mostra o boletim e pergunta se quer submeter
```

Você pode resubmeter quantas vezes quiser — **a maior nota conta**.

> ⚠️ **Rode o `autograde validar` fora do terminal do agente.** Nos dois
> exercícios a CLI roda um verificador em Python na sua máquina (ele lê as
> fontes `.tex` e o `main.pdf`, ou as suas Issues) e manda a saída como
> evidência. Terminal de agente costuma mexer em PATH e em variáveis de
> ambiente.

---

## Exercício ia-6.1 — Sua primeira dissertação dummy

Slides 30 a 34. O objetivo não é escrever a dissertação: é ter, no fim da
aula, **o esqueleto da sua dissertação compilando** — com os seus dados, no
formato do IDP, com cada recurso que você vai usar (citação, figura, tabela,
referência) funcionando uma vez.

### A armadilha deste exercício

O template **já vem** com figura, tabela, citação longa, citação indireta,
13 obras no `.bib` e um `main.pdf` pronto. Um fork que ninguém mexeu tem tudo
que o slide 34 lista. Por isso **o autograder mede a diferença em relação ao
template**, não a presença:

- a figura e a tabela que contam são **as suas** — o `\label` não pode ser o
  `fig:exemplo`/`tab:exemplo` do template;
- as 3 obras que contam são chaves que **o template não tem**;
- os parágrafos que contam são **os seus** — o texto de instrução do template
  ("Na primeira página da parte textual...") não conta;
- o `main.pdf` tem que ser **recompilado** por você: o autograder lê o título
  gravado nos metadados do PDF e compara com o `\titulo{}` do seu
  `config/dados.tex`.

Pode apagar a figura, a tabela e as citações de exemplo, ou deixá-las: elas só
não contam a seu favor.

### Passo 1 — O fork

1. No GitHub, **Fork** do `alexlopespereira/TemplateLatexIDP` para a sua conta.
2. Clone o **seu** fork e entre nele:

   ```bash
   gh repo clone <seu-usuario>/<seu-fork>
   cd <seu-fork>
   ```

3. Instale uma distribuição LaTeX **com o biber**: MiKTeX (Windows), MacTeX
   (macOS) ou TeX Live (Linux). Confira com `latexmk -v` e `biber -v`.

### Passo 2 — O prompt do slide 33

Dentro da pasta do fork, cole no seu agente (Claude Code, Codex...) o prompt do
slide 33, com os **seus** dados no item 2. O repositório tem um `CLAUDE.md` com
regras que o agente vai seguir — duas delas importam aqui:

- **"Nunca invente referências bibliográficas."** O prompt pede 3 referências.
  O agente vai (ou deveria) parar e pedir as obras a você. Dê obras que você já
  tem — as da revisão do ia-3.2 servem — e **confira cada uma numa fonte
  externa** (DOI, página do periódico, texto oficial da lei). É a pergunta 2.
- **"Não escreva conteúdo acadêmico do zero."** O texto dummy é um esqueleto
  descartável; diga isso ao agente se ele recusar.

### Passo 3 — O que precisa estar no fork

| Onde | O quê |
|---|---|
| `config/dados.tex` | título provisório, seu nome, orientador, programa, cidade e ano — **sem** nenhum valor de exemplo ("Título do trabalho", "Nome Completo do Autor", "Termo 1."...). Banca ainda não definida? Escreva "a definir", não deixe o exemplo |
| `main.tex` | `\documentclass[mestrado]{idp}` (ou `doutorado`) |
| `capitulos/01` a `05` | 2 parágrafos seus em cada um |
| `pretextual/resumo.tex` e `abstract.tex` | preenchidos (≥ 60 palavras cada) |
| um capítulo | uma citação direta longa no ambiente `citacao`, com `\parencite` dentro, de uma obra sua |
| um capítulo | uma citação indireta (`\citeonline`, `\parencite`) de uma obra sua |
| `referencias.bib` | 3 obras suas, **todas citadas** no texto; nenhuma `\cite` sem entrada |
| um capítulo | uma `figure` e uma `table`, cada uma com `\caption`, `\label`, `\fonte{}` e um `\ref` para ela no texto |
| `main.pdf` | compilado **depois** da última edição |

### Passo 4 — Compile, commite e faça push

```bash
latexmk -pdf main.tex
git add -A
git commit -m "ia-6.1: dissertacao dummy"
git push
```

"Entregue o `main.pdf`" quer dizer: **commitado e no GitHub**. O autograder
roda `git status` e confere que o branch não está `ahead` do `origin` e que não
há alteração em `main.pdf`, `main.tex`, `config/`, `capitulos/`, `pretextual/`
ou `referencias.bib` fora do commit.

### Passo 5 — Valide e responda as duas perguntas

```bash
autograde validar ia-6.1
```

As duas perguntas são feitas na CLI e valem 30 dos 100 pontos:

1. Você escreveu `\cite{chave}` e a obra apareceu em ABNT nas Referências.
   **Explique o caminho**: o que pdflatex, biber e latexmk fazem, em que ordem,
   e por que é preciso compilar mais de uma vez.
2. O `CLAUDE.md` proíbe inventar referências e o prompt pede 3. **Como o seu
   agente lidou com isso, e como você verificou** que as 3 obras existem e que
   os dados estão certos? Pedir ao próprio agente para confirmar não conta como
   verificação.

A CLI roda, na sua máquina: `gh --version`, `gh auth status`,
`gh repo view --json name,isFork,parent,hasIssuesEnabled`,
`git status --porcelain=v1 --branch` e um verificador em `python -c` (com
`python3` como alternativa) que lê as fontes e o `main.pdf`.

### Critérios do ia-6.1

| Critério | Peso | O que precisa |
|---|---:|---|
| `gh_autenticado` | 2 | `gh auth status` OK, na conta do roster |
| `e_um_fork` | 2 | o repositório é um fork |
| `fork_do_template` | 2 | fork do `TemplateLatexIDP` |
| `fontes_e_pdf_commitados` | 3 | nada de `main.pdf` e fontes fora do commit |
| `push_feito` | 3 | branch com upstream e sem `[ahead N]` |
| `dados_sem_valores_de_exemplo` | 5 | nenhum valor de exemplo em `config/dados.tex` |
| `classe_mestrado` | 3 | `\documentclass[mestrado]{idp}` (ou doutorado) |
| `pdf_existe` | 2 | `main.pdf` é um PDF |
| `pdf_nao_e_o_do_template` | 3 | não é o `main.pdf` que veio no fork |
| `pdf_compilado_com_seus_dados` | 5 | título nos metadados do PDF = `\titulo{}` do `dados.tex` |
| `pdf_atualizado` | 4 | `main.pdf` mais novo que todo `.tex` e o `.bib` |
| `cinco_capitulos_dois_paragrafos` | 6 | 2 parágrafos seus (≥ 20 palavras) em cada capítulo |
| `resumo_preenchido` | 2 | resumo seu |
| `abstract_preenchido` | 2 | abstract seu |
| `citacao_direta_longa` | 3 | ambiente `citacao` com `\cite` de obra sua |
| `citacao_indireta` | 2 | `\cite` de obra sua fora do `citacao` |
| `tres_obras_suas` | 5 | 3 chaves novas no `.bib`, citadas no texto |
| `nenhuma_citacao_orfa` | 2 | toda `\cite` tem entrada no `.bib` |
| `figura_completa` | 3 | figura sua com caption, fonte e label referenciado |
| `tabela_completa` | 3 | tabela sua com caption, fonte e label referenciado |
| `texto_e_da_sua_pesquisa` | 8 | o esqueleto é da sua pesquisa, não genérico (LLM avalia) |
| pergunta 1 | 15 | o caminho da `\cite` — respondida na CLI |
| pergunta 2 | 15 | a verificação das referências — respondida na CLI |
| **Total** | **100** | |

---

## Exercício ia-6.2 — O mapa da sua tese com o `/wayfinder`

Slide 35. A skill `wayfinder` (do repositório de skills de Matt Pocock) planeja
um trabalho grande demais para um prompt como um **mapa de decisões** nas
Issues do GitHub: uma issue-mapa com o destino, as decisões já tomadas e o que
ainda está nebuloso, e tickets filhos que resolvem uma incerteza cada. Há
tipos de ticket; dois importam aqui:

- **research** — a incerteza tem resposta no mundo (literatura, bases de
  dados). O agente investiga **sozinho** (AFK) e fecha o ticket com a
  resolução e as fontes.
- **grilling** — a incerteza é uma **decisão sua** (recorte, método,
  contribuição). O agente pergunta **uma coisa por vez**, com a resposta que
  recomenda, e **você responde** (HITL). O ticket fecha com a decisão.

O que ainda não dá para formular como pergunta fica em **"Not yet specified"**
no mapa — e só vira ticket quando outra decisão o deixar claro.

### O que você entrega

Tudo num **repositório seu no GitHub, público ou privado**:

| Onde | O quê |
|---|---|
| `contexto-pesquisa.md` (raiz do repositório) | o estado da sua pesquisa — tema, problema, o que já está decidido, o que está em aberto — e **uma pergunta de aprofundamento sobre impacto científico**, numa linha que termina com `?` |
| Issues do repositório | 1 issue-mapa (`wayfinder:map`) com Destination, Decisions so far e Not yet specified |
| Issues do repositório | ≥ 1 ticket `wayfinder:research` e ≥ 1 `wayfinder:grilling`, filhos do mapa |
| Issues do repositório | 1 de cada **fechado com a resolução registrada em comentário** |
| o mapa | "Decisions so far" com link (`#N`) para os tickets fechados |

### Passo 1 — Escolha e prepare o repositório

**Público ou privado, você escolhe.** O plano da dissertação não precisa ficar
aberto: o verificador lê as Issues com o **seu** `gh` (que enxerga os seus
repositórios privados) e manda o conteúdo junto com a submissão. A nota sai
igual nos dois casos.

- **Público — o fork do ia-6.1.** Use o próprio fork. Não dá para torná-lo
  privado: o GitHub não deixa fork de repositório público ser privado.
- **Privado — um repositório novo.** De dentro do clone do ia-6.1, crie uma
  cópia privada e aponte o `gh` para ela:

  ```bash
  gh repo create <seu-usuario>/<nome-privado> --private --source . --remote privado --push
  gh repo set-default <seu-usuario>/<nome-privado>
  ```

  O fork continua no remote `origin` para o ia-6.1. Valide o ia-6.1 **antes**
  de trocar o default — ou volte com `gh repo set-default <seu-usuario>/<seu-fork>`
  —, porque ele confere que o repositório do `gh` é o fork. Um repositório
  privado vazio, só para o mapa, também serve: basta o `contexto-pesquisa.md`
  na raiz do clone.

Depois:

1. **Habilite as Issues.** Fork nasce com Issues desligadas:
   *Settings → General → Features → Issues*. Repositório novo já nasce com
   elas ligadas. Sem Issues o Wayfinder não tem onde escrever.
2. **Aponte o `gh` para o repositório certo.** Se o clone tem mais de um
   remote (o `upstream` do template, ou o fork e a cópia privada), rode:

   ```bash
   gh repo set-default <seu-usuario>/<seu-repo>
   ```

   Sem isso o `gh` pode criar e ler Issues **no template** ou no repositório
   errado.
3. **Instale a skill e as que ela chama** (como na Aula 3, troque o harness):

   ```bash
   npx -y skills add mattpocock/skills --skill wayfinder --skill grilling \
     --skill domain-modeling --skill research --agent claude-code
   ```

### Passo 2 — `contexto-pesquisa.md`

Escreva você — é o "destino" do slide. Pode reaproveitar o que saiu do
grill-me do ia-3.2. A pergunta de aprofundamento é **uma** e é sobre
**contribuição** (o que tornaria o trabalho citável), não operacional ("que
ferramenta usar?"). Commite e faça push.

### Passo 3 — O mapa

No agente, dentro do clone: `/wayfinder` com o `contexto-pesquisa.md` como
ponto de partida. Deixe o mapa ter pelo menos um ticket de research (ex.:
estado da arte da pergunta, bases de dados) e um de grilling (ex.: recorte,
método, tipo de contribuição).

### Passo 4 — Resolva os dois tickets

**Uma sessão por ticket.** Na de grilling, responda de verdade: é o único lugar
do exercício em que o juiz procura **as suas** respostas — e procura pelo menos
um ponto em que você discordou ou corrigiu o agente. Ao fechar cada ticket, o
Wayfinder escreve a resolução em comentário e atualiza o mapa; confira que
"Decisions so far" ganhou uma linha com o link de cada um.

### Passo 5 — Valide e responda as duas perguntas

```bash
autograde validar ia-6.2
```

O verificador lê as suas Issues com o seu `gh` e grava na raiz do clone um
`wayfinder-export.json` com o mapa e os tickets — é esse arquivo, enviado com
a submissão, que os juízes leem; por isso o repositório pode ser privado. Ele
é **regravado a cada `validar`**: editar à mão não adianta. Não precisa
commitá-lo (pode pôr no `.gitignore`).

1. Por que research é resolvido pelo agente sozinho e grilling só com você?
   Dê um exemplo do seu mapa em que **a sua resposta** mudou o rumo que o
   agente recomendava.
2. O que ficou em "Not yet specified"? Escolha um item: por que ele **ainda
   não** virou ticket, e que resolução o faria virar um?

A CLI roda, na sua máquina: `gh --version`, `gh auth status`,
`gh repo view --json name,visibility,hasIssuesEnabled` e um coletor em
`python -c` (com `python3` como alternativa) que chama `gh issue list` e
`gh api graphql` (as sub-issues do mapa). A visibilidade só fica registrada:
não conta ponto.

### Critérios do ia-6.2

| Critério | Peso | O que precisa |
|---|---:|---|
| `gh_autenticado` | 2 | `gh auth status` OK, na conta do roster |
| `issues_habilitadas` | 2 | Issues ligadas no repositório |
| `contexto_existe` | 2 | `contexto-pesquisa.md` na raiz |
| `contexto_tem_pergunta` | 2 | uma linha terminando em `?` |
| `contexto_bom` | 5 | tema e recorte, decidido × em aberto, uma pergunta de contribuição (LLM avalia) |
| `mapa_criado` | 4 | issue com rótulo `wayfinder:map` |
| `mapa_tem_destino` | 2 | seção Destination preenchida |
| `mapa_tem_nao_especificado` | 3 | seção Not yet specified preenchida |
| `mapa_registra_decisoes` | 5 | Decisions so far aponta para ≥ 2 tickets fechados |
| `mapa_bom` | 6 | destino específico, decisões afirmativas com link, névoa real (LLM avalia) |
| `tem_ticket_de_pesquisa` | 5 | ≥ 1 `wayfinder:research` |
| `tem_ticket_de_grilling` | 5 | ≥ 1 `wayfinder:grilling` |
| `tickets_ligados_ao_mapa` | 4 | ≥ 2 tickets filhos do mapa (sub-issue, ou "Part of #N") |
| `pesquisa_resolvida` | 4 | research fechado com comentário de resolução (≥ 300 caracteres) |
| `grilling_resolvido` | 4 | grilling fechado com comentário de resolução (≥ 300 caracteres) |
| `resolucao_de_pesquisa` | 7 | conclusão, fontes identificáveis, fato × inferência (LLM avalia) |
| `resolucao_de_grilling` | 8 | diálogo, respostas suas, uma divergência, decisão final (LLM avalia) |
| pergunta 1 | 15 | research × grilling, com exemplo seu — respondida na CLI |
| pergunta 2 | 15 | o "Not yet specified" — respondida na CLI |
| **Total** | **100** | |

---

## Quando der errado

**`e_um_fork` / `fork_do_template` zerados.** Você clonou o template direto, em
vez do seu fork, ou baixou o `.zip`. Confira com
`gh repo view --json isFork,parent`. Se o trabalho já está feito num clone do
template: faça o fork no GitHub, `git remote set-url origin <url do fork>` e
`git push`.

**`pdf_compilado_com_seus_dados` zerado com o PDF compilado.** O título dos
metadados do PDF vem do `\titulo{}` pelo hyperref. Se você mudou o `dados.tex`
depois de compilar, recompile. Se o título tem comando LaTeX dentro
(`\emph{...}`), o texto gravado no PDF pode sair diferente — deixe o título em
texto puro.

**`pdf_atualizado` zerado.** Algum `.tex` ou o `.bib` foi salvo depois do último
`latexmk`. Recompile, commite e faça push de novo. Depois de um `git clone` ou
`git checkout` as datas dos arquivos mudam: recompile antes de validar.

**`push_feito` zerado.** `git status` mostra `[ahead N]`: falta o `git push`.
Ou o branch não tem upstream: `git push -u origin main`.

**`cinco_capitulos_dois_paragrafos` zerado com o texto escrito.** Parágrafo é
um bloco separado por **linha em branco**, com pelo menos 20 palavras, fora de
figura, tabela, citação longa e lista. Dois blocos colados sem linha em branco
são um parágrafo só. Parágrafo de instrução do template não conta.

**`tres_obras_suas` zerado.** As três chaves precisam estar no `.bib` **e** ser
citadas no texto dos capítulos. Chave do template (`abnt6023`, `sa1971`...) não
conta.

**`figura_completa` / `tabela_completa` zerados.** Dentro do ambiente precisam
estar `\caption`, `\label` e `\fonte{}`; o **primeiro** `\label` tem que ser
chamado por um `\ref` no texto; e não pode terminar em `:exemplo`.

**ia-6.2 zerado inteiro com o mapa no GitHub.** O `gh` está lendo outro
repositório — quase sempre o template, pelo remote `upstream`, ou o fork
quando o mapa está na cópia privada. Rode `gh issue list` na raiz do clone: se
não aparecem as suas issues, `gh repo set-default <seu-usuario>/<seu-repo>`.

**`e_um_fork` zerado no ia-6.1 depois do ia-6.2 privado.** O `gh` está
apontando para a cópia privada. `gh repo set-default <seu-usuario>/<seu-fork>`
e valide o ia-6.1 de novo (a maior nota conta).

**`pesquisa_resolvida` / `grilling_resolvido` zerados com o ticket fechado.** O
ticket tem que ter um **comentário** com a resolução (≥ 300 caracteres). Fechar
pelo botão, sem comentário, não registra decisão nenhuma.

**`tickets_ligados_ao_mapa` zerado.** Os tickets não são sub-issues do mapa.
Na issue-mapa, *Create sub-issue → Add existing issue*, ou escreva
`Part of #<número do mapa>` no corpo de cada ticket.

**Os demais problemas** (403, 401, submissão atrasada) estão na
[Parte 7 do tutorial da Aula 1](Exercicios_Aula1.md#parte-7--quando-der-errado).
