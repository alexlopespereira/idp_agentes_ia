# Exercícios da Aula 5 — ia-5.1 e ia-5.2

Dois laboratórios em que **o objeto medido é você**:

- **ia-5.1** — um **prompt de auditoria** que faz um agente diagnosticar a
  distância entre o seu processo de trabalho e as boas práticas de engenharia
  de software e de CI/CD. O artefato central não é a tabela: é o prompt.
- **ia-5.2** — uma **atitude da aula, operacionalizada e medida em você**: você
  escolhe uma, define o comportamento observável que serve de proxy, conta esse
  comportamento no seu próprio histórico de sessões, e desenha a intenção de
  implementação que ataca o que você mediu.

**Prazo dos dois: 01/11.**

**Nenhum dos dois exige repositório no GitHub.** Não é preciso criar nada, nem
rodar `git init` na pasta do exercício: uma pasta comum basta. Os dois também
são **agnósticos de harness** — Claude Code, Codex, opencode, pi, Amp, a
interface web: nenhum critério pergunta qual você usou.

> A amarra de identidade continua de pé: o login Google diz quem você é e
> `gh auth status` confere a sua conta do GitHub contra o `github_username` do
> roster. O `gh` precisa estar **autenticado**; o que não precisa existir é
> **repositório**.

Uma sutileza que vale ler duas vezes: o **ia-5.1 audita repositórios git
locais**, e o script dele roda `git` dentro deles. Isso não é a mesma coisa que
exigir repositório no GitHub — os repos auditados podem ser privados, sem
`remote` nenhum, ou de um projeto do trabalho que nunca vai para a internet. O
git ali é só a fonte de evidência.

Se você ainda não fez o setup (Python, Git, `gh`, CLI `autograde`, login
Google), volte para a [Parte 1 do tutorial da Aula 1](Exercicios_Aula1.md#parte-1--setup-uma-vez-no-semestre).

O fluxo de entrega é o de sempre — **de dentro da pasta do exercício**:

```bash
cd <diretório do exercício>
autograde validar ia-5.1     # mostra o boletim e pergunta se quer submeter
```

Você pode resubmeter quantas vezes quiser — **a maior nota conta**.

> ⚠️ **Rode o `autograde validar` fora do terminal do agente.** Nos dois
> exercícios a CLI executa um script seu de verdade na sua máquina (o
> `inventario.py`, o `medir.py`) e manda a saída como evidência. Terminal de
> agente costuma mexer em PATH e em variáveis de ambiente.

---

## Exercício ia-5.1 — Audite seu próprio processo

O slide pede um prompt que faça o agente **auditar os seus repositórios e o
histórico de como você o conduziu**, para medir a distância entre o seu
processo e as boas práticas de engenharia e de CI/CD.

O ponto do exercício não é descobrir que você deveria ter CI. Você já sabe. O
ponto é que **um agente com acesso ao seu repositório devolve conselho de blog
por padrão** — "adote CI/CD", "escreva testes", "documente" — e só para de
fazer isso quando o prompt o obriga a ancorar cada afirmação numa evidência e a
escrever **"não observável"** quando a evidência falta.

Ou seja: o artefato avaliado com mais peso aqui é **o prompt**, não a tabela.

### A tarefa, em três etapas

1. **Escreva o prompt.** Ele precisa exigir, de forma explícita:
   - **Papel e escopo** — engenheiro(a) de software sênior; **diagnosticar, não
     corrigir** (sem patch, sem refatoração, sem "vou consertar para você");
   - **Evidências** — logs, testes, CI/CD, dependências, segredos, documentação
     **e trechos das conversas** com o agente;
   - **Saída em tabela** — `prática frágil | evidência | risco concreto |
     primeiro passo (≤ 30 min)`;
   - **Criticidade** — Bloqueante / Alto / Médio / Baixo, e **você define o que
     cada nível significa dentro do prompt**;
   - **Honestidade** — escrever **"não observável"** quando faltar evidência;
     **proibido supor**.
2. **Rode a auditoria** no seu harness, apontando para repositórios em que você
   **vem trabalhando** de verdade.
3. **Julgue o resultado** — um parágrafo dizendo se você concorda ou discorda
   da criticidade do **item nº 1** da tabela, e por quê.

### O que você entrega

Uma pasta chamada **`auditoria-processo`** na sua máquina — não precisa ser
repositório:

```
auditoria-processo/
├── repos-auditados.txt      # um caminho de repositório por linha
├── prompt-auditoria.md      # o prompt que você escreveu — o artefato central
├── tabela-auditoria.md      # a tabela que o agente devolveu
├── inventario.py            # o script que confere a tabela contra os repos
├── inventario.json          # o envelope da última execução (gravado pelo script)
└── discordancia.md          # o parágrafo sobre o item nº 1
```

> Os seis arquivos ficam na **raiz da pasta** e os nomes batem exatamente,
> incluindo maiúsculas.
>
> **A pasta não precisa estar dentro do repositório auditado** — na verdade é
> melhor que não esteja, para não sujar o `git status` de um projeto seu. Os
> caminhos dos repos vão no `repos-auditados.txt`, um por linha, absolutos ou
> relativos à pasta do exercício.

### Passo 1 — O prompt

Escreva no `prompt-auditoria.md` o prompt inteiro, como você o entregou ao
agente. Se você iterou — e vale a pena iterar — entregue a **versão final**, e
guarde na cabeça o que mudou: a pergunta 1 da CLI é exatamente sobre isso.

Doze pontos saem de regex procurando as cláusulas (papel, escopo, as quatro
colunas, os quatro níveis, "não observável", a proibição de supor, as conversas
como fonte). Sete saem de um juiz LLM que lê o prompt inteiro e pergunta outra
coisa:

- os quatro níveis estão **definidos**, ou apenas listados? "Bloqueante /
  Alto / Médio / Baixo" é uma lista. "Bloqueante = perda de dado ou credencial
  exposta; Alto = quebra silenciosa que só aparece em produção; …" é uma
  definição, e é ela que faz o agente hierarquizar em vez de chamar tudo de
  Alto;
- as fontes de evidência estão **nomeadas** (`.github/workflows/`, a suíte de
  testes, o manifesto de dependências, o log de commits, os arquivos de
  segredo, o histórico de sessões), ou o prompt diz "analise o repositório"?
- cada linha precisa de uma **evidência localizável** — caminho, comando, hash,
  trecho — ou vale afirmação sem fonte?

> **A cláusula que quase todo mundo esquece é a das conversas.** Auditar o repo
> é óbvio. Auditar *como você conduziu o agente* — quantas vezes você aceitou
> um diff sem ler, quantas vezes pediu "conserta" sem dizer o que estava
> errado, quantas sessões terminaram sem teste — não é. É a metade do exercício
> que mede o seu processo, e não o seu código.

### Passo 2 — A tabela

Cole no `tabela-auditoria.md` a tabela que o agente devolveu, em markdown, com
**pelo menos 5 achados** e as 4 colunas. Colunas extras (dono, prazo, arquivo)
não custam ponto.

Não edite os achados para ficarem mais bonitos. Um diagnóstico honesto de um
processo frágil é **o resultado esperado** — nenhum critério pune processo
ruim; os critérios punem tabela que não prova nada.

O juiz lê a tabela **junto com o seu prompt** e confere se ela é o que o prompt
pediu. O que ele procura:

- evidência **localizável e específica** do seu repo ou da sua conversa, não
  uma prática ausente enunciada em abstrato;
- risco que é **consequência**, não a prática frágil repetida com outras
  palavras;
- primeiro passo que cabe no tempo prometido — "adotar CI/CD" não é um passo de
  30 minutos;
- criticidade que **varia**: tabela em que tudo é Alto não hierarquizou nada;
- **ao menos um achado vindo das conversas**.

### Passo 3 — O inventário e o envelope

O autograder não consegue abrir os seus repositórios. Então, como no ia-4.1,
**quem prova que a auditoria olhou algo real é um script que você escreve**: o
`inventario.py` lê o `repos-auditados.txt`, roda `git` em cada repo, lê a
**tabela entregue**, extrai os caminhos de arquivo citados nela, confere quais
existem de verdade, e imprime este envelope — que também é gravado em
`inventario.json`:

```json
{
  "repos_auditados": 2,
  "commits_total": 271,
  "arquivos_rastreados": 143,
  "repos": [
    {
      "nome": "autograde-idp-backend",
      "commits": 214,
      "arquivos_rastreados": 87,
      "ultimo_commit": "dbf59bb Merge pull request #29",
      "tem_ci": true,
      "tem_testes": true,
      "tem_dependencias": true
    }
  ],
  "caminhos_citados": 9,
  "caminhos_confirmados": ["app/grader.py", "pyproject.toml"],
  "evidencia_citada": "app/grader.py"
}
```

Regras do envelope — **é o contrato do exercício**:

| campo | o que tem que ser |
|---|---|
| `repos_auditados` | quantos repos o script percorreu — pelo menos **1** |
| `commits_total` | soma dos commits dos repos — pelo menos **5**; o slide diz "repositórios em que você **vem trabalhando**", e um repo criado para o exercício não é objeto de auditoria |
| `ultimo_commit` | por repo, começando pelo **hash** (`git log -1 --format=%h %s`) |
| `caminhos_confirmados` | os caminhos citados na tabela que existem no `git ls-files` de algum repo — pelo menos **um** |
| `evidencia_citada` | um deles, escolhido para a checagem cruzada |

A `evidencia_citada` é o que amarra tudo: o autograder a extrai do
`inventario.json` e exige que ela apareça **dentro da `tabela-auditoria.md`
entregue**. É assim que se prova que a tabela fala de arquivos que existem — e
que ela não foi reescrita depois da rodada.

O esqueleto tem umas 40 linhas. Rode **de dentro da pasta**, antes de validar:

```bash
python inventario.py
```

- Serialize com `ensure_ascii=False` — acento escapado em `\uXXXX` não bate com
  o arquivo.
- Resolva os caminhos a partir de `Path(__file__).parent`, não do `cwd`.
- `git` escreve avisos em *stderr* e a CLI concatena stderr no stdout antes de
  mandar. Isso **não** reprova: o autograder procura os campos por regex, não
  faz `json.loads` da saída inteira. O que não pode é o script estourar
  exceção — `Traceback` na saída zera 2 pontos.

### Passo 4 — A discordância

Um parágrafo no `discordancia.md`: você **concorda ou discorda** da criticidade
que o agente deu ao **item nº 1**, e por quê.

Concordar vale tanto quanto discordar. O que não vale é reafirmar a linha da
tabela com outras palavras. O juiz procura **informação que o agente não
tinha** — quem usa o sistema, quantas pessoas dependem dele, o que já deu
errado antes, qual é o custo real de estar errado. É a parte Feynman do
exercício: relatar o que pode invalidar a tese, inclusive quando a tese é a do
agente.

### Passo 5 — Valide e responda as duas perguntas

```bash
autograde validar ia-5.1
```

As duas perguntas são feitas na CLI, na hora de submeter, e valem 30 dos 100
pontos:

1. Qual **cláusula** do seu prompt separou conselho genérico de achado real —
   a cláusula, o achado que ela produziu, e o que o agente respondia antes dela
   (ou responderia sem ela).
2. Classifique **três linhas** da sua tabela com os marcadores da aula —
   `[FACT]`, `[INFERENCE]`, `[ASSUMPTION]` — e justifique cada marcador. Se as
   três forem `[FACT]`, explique como cada uma foi verificada.

A CLI roda, na sua máquina: `gh --version`, `gh auth status` e
**`python inventario.py`** (com `python3` como alternativa).

### Critérios do ia-5.1

| Critério | Peso | O que precisa |
|---|---:|---|
| `gh_autenticado` | 2 | `gh auth status` OK, na conta do roster |
| `prompt_existe` | 2 | `prompt-auditoria.md` na raiz |
| `prompt_papel_senior` | 1 | papel de engenheiro(a) sênior |
| `prompt_escopo_diagnostico` | 2 | diagnosticar, **não** corrigir |
| `prompt_coluna_pratica` | 1 | coluna "prática frágil" |
| `prompt_coluna_evidencia` | 1 | coluna "evidência" |
| `prompt_coluna_risco` | 1 | coluna "risco" |
| `prompt_coluna_primeiro_passo` | 1 | coluna "primeiro passo" |
| `prompt_niveis_criticidade` | 3 | os quatro níveis, todos |
| `prompt_nao_observavel` | 2 | a saída "não observável" |
| `prompt_proibe_supor` | 2 | proibição explícita de supor |
| `prompt_cita_conversas` | 2 | as conversas como fonte de evidência |
| `prompt_qualidade` | 7 | níveis definidos, fontes nomeadas, evidência obrigatória (LLM avalia) |
| `tabela_existe` | 2 | `tabela-auditoria.md` na raiz |
| `tabela_cinco_achados` | 3 | tabela markdown de 4+ colunas, ≥ 5 achados |
| `tabela_criticidade_marcada` | 2 | cada achado com um nível |
| `tabela_caminhos_citados` | 2 | ≥ 3 arquivos citados na evidência |
| `tabela_qualidade` | 7 | a tabela é o que o prompt pediu (LLM avalia) |
| `repos_auditados_existe` | 1 | `repos-auditados.txt` na raiz |
| `inventario_script_existe` | 2 | `inventario.py` na raiz |
| `inventario_json_existe` | 1 | `inventario.json` na raiz |
| `inv_repos` | 2 | ≥ 1 repo percorrido |
| `inv_commits` | 2 | ≥ 5 commits somados |
| `inv_ultimo_commit` | 1 | o hash do último commit no envelope |
| `inv_caminho_confirmado` | 3 | ≥ 1 caminho da tabela existe nos repos |
| `inv_sem_traceback` | 2 | o script rodou sem estourar exceção |
| `evidencia_bate_com_tabela` | 4 | a `evidencia_citada` aparece na tabela |
| `discordancia_existe` | 2 | `discordancia.md` na raiz |
| `discordancia_qualidade` | 7 | posição + argumento + contexto novo (LLM avalia) |
| pergunta 1 | 18 | a cláusula e o achado — respondida na CLI |
| pergunta 2 | 12 | os três marcadores — respondida na CLI |
| **Total** | **100** | |

---

## Exercício ia-5.2 — Uma atitude, medida em você

O slide 42 é uma linha: *"utilize o Claude Code para investigar algum aspecto
do seu processo de trabalho relacionado a algumas das atitudes"*. A versão
operacional dessa linha é o exercício, e a operacionalização **é** a
dificuldade.

Atitude não se observa. Os slides 13-14 separam as coisas: **atitude** é a
predisposição que orienta a ação; **comportamento** é o que você faz de forma
observável. Ninguém mede humildade epistêmica; mede-se quantas vezes você
revisou uma hipótese depois de uma observação contrária. A ponte entre os dois
é uma **inferência** — e o exercício é construir essa ponte de um jeito que
aguente peso.

Depois, a intervenção. O slide 18 mostra **intenções de implementação** ("se X,
então Y") rendendo d = 0,27 a 0,66; o slide 19 mostra **growth mindset**
rendendo d = 0,05 nos estudos mais robustos. A diferença não é motivacional: a
intenção de implementação amarra um comportamento a um gatilho identificável, e
o growth mindset não amarra nada. A sua intervenção precisa estar do lado certo
dessa tabela.

### A tarefa, em quatro etapas

1. **Escolha uma atitude** do slide 15 — curiosidade, ceticismo calibrado,
   humildade epistêmica, persistência estratégica, orientação para
   aprendizagem, metacognição — e **operacionalize**: qual comportamento
   observável serve de proxy, qual é a unidade de análise, como se conta, o que
   conta como violação, e quais são os limites do indicador.
2. **Monte o corpus** — trechos das suas próprias sessões de trabalho com um
   agente, num arquivo só. **Redija o que precisa redigir**: nada de token,
   chave, URL interna ou dado de terceiro.
3. **Meça** — um script que lê o corpus, aplica a sua regra de contagem, e
   grava a medição em CSV mais um envelope JSON.
4. **Desenhe a intervenção** — a intenção de implementação que ataca a violação
   que **você mediu**, com variável-resultado, linha de base e condição de
   abandono.

### O que você entrega

Uma pasta chamada **`atitudes-lab`**:

```
atitudes-lab/
├── atitude.md                  # a atitude, o indicador, a regra de contagem, os limites
├── historico.md                # o corpus: trechos das suas sessões (≥ 40 linhas)
├── medir.py                    # o script que conta
├── medicao.csv                 # a medição, uma linha por episódio
├── evidencia-medicao.json      # o envelope (gravado pelo medir.py)
└── intervencao.md              # a intenção de implementação
```

> **Por que o corpus é um arquivo, e não um caminho para o histórico do
> harness:** porque o exercício é agnóstico de harness. Claude Code guarda
> sessão em `~/.claude/projects/**/*.jsonl`, outros harnesses guardam em outro
> lugar, e quem usa a interface web não tem arquivo nenhum. Exigir um caminho
> específico transformaria um exercício sobre comportamento num exercício sobre
> a árvore de diretórios de um produto.

### Passo 1 — `atitude.md`

A atitude escolhida, a regra do slide 15 que a acompanha, e a
operacionalização. O que o juiz procura (ele lê o `atitude.md` **junto com o
corpus**):

- o indicador é **um comportamento observável naquele corpus** — dá para
  apontar o trecho e dizer "aqui aconteceu";
- a **regra de contagem** está explícita: qual é a unidade (um episódio, uma
  sessão, uma tentativa), o que faz uma ocorrência começar e terminar, o que
  conta como violação;
- a regra é **replicável**: outra pessoa, com o mesmo corpus, chegaria a um
  número próximo;
- os **marcadores epistêmicos** estão usados com sentido — `[FACT]` tem trecho
  que prove, `[INFERENCE]` deriva de fatos nomeados, `[ASSUMPTION]` foi adotado
  sem checar. Os três valem 1 ponto cada, por regex, mas o juiz olha se eles
  significam algo ou se estão pendurados como enfeite;
- há **ao menos um limite** concreto do indicador declarado.

> **O exemplo mais fácil de operacionalizar é a persistência estratégica**, cuja
> regra é: "depois de duas tentativas semelhantes sem progresso, mudar de
> estratégia". O indicador cai no colo: sequências de tentativas parecidas sem
> mudança de abordagem. Não é obrigatório escolher essa — só é a mais barata.

### Passo 2 — O corpus

`historico.md` com **≥ 40 linhas não vazias** de trechos das suas sessões
reais. Formato livre: colagem de tela, log, exportação. O que importa é que
tenha episódios dentro.

### Passo 3 — `medir.py`, `medicao.csv` e o envelope

O script **lê o `historico.md` do disco** (quem contar na mão e digitar os
números perde o ponto — e perde o exercício, porque contagem manual não é
replicável), aplica a regra, e grava os dois arquivos.

`medicao.csv` — o cabeçalho precisa conter estas colunas (extras são
bem-vindas):

```csv
episodio,fonte,indicador,valor,violacao,trecho
1,sessao-2026-10-14,tentativas consecutivas da mesma abordagem,3,sim,"vou tentar o mesmo comando de novo"
```

Mínimo: **5 episódios**.

`evidencia-medicao.json` — e o script imprime o mesmo JSON no stdout:

```json
{
  "atitude": "persistencia-estrategica",
  "indicador": "tentativas consecutivas da mesma abordagem sem progresso",
  "episodios": 7,
  "violacoes": 3,
  "taxa_violacao": 0.43,
  "linhas_historico": 61,
  "trecho_exemplo": "vou tentar o mesmo comando de novo"
}
```

| campo | o que tem que ser |
|---|---|
| `indicador` | o indicador, com 10 caracteres ou mais |
| `episodios` | **≥ 5** — o mesmo número de linhas de dados do CSV |
| `violacoes` | a contagem; **zero é um resultado legítimo** (significa que o comportamento está no lugar). O que não pode é o campo não existir |
| `trecho_exemplo` | um trecho **literal** do corpus, com 15 caracteres ou mais |

O `trecho_exemplo` é a amarra: o autograder o extrai do envelope e exige que
ele exista **dentro do `historico.md`**. É o que separa "meu script imprimiu
números" de "meu script leu o meu histórico".

- Escolha um trecho **sem aspas e sem barra invertida** — o JSON escapa esses
  caracteres e a comparação falha por um detalhe bobo.
- `ensure_ascii=False`, sempre.

```bash
python medir.py
```

### Passo 4 — `intervencao.md`

A intenção de implementação, na forma **"se X, então Y"**, mais:

- a **variável-resultado** — o que você mediria para saber se funcionou;
- a **linha de base** — o número que a sua medição já produziu, e quantos
  episódios / quanto tempo você observaria de novo;
- a **condição de abandono** — o que você veria que o faria concluir que a
  intervenção não funcionou, em vez de continuar acreditando nela.

O juiz lê o `intervencao.md` **junto com o `medicao.csv`** e confere se a
intervenção ataca a violação que foi medida — se dá para traçar a linha do CSV
até o gatilho escolhido. Um "se/então" cujo gatilho é "quando eu estiver
trabalhando" é growth mindset com roupa de intenção de implementação.

### Passo 5 — Valide e responda as duas perguntas

```bash
autograde validar ia-5.2
```

As duas perguntas valem 30 dos 100 pontos:

1. O seu indicador observa um **comportamento**, não a atitude. O que ele mede
   de fato, qual é a inferência que você faz do comportamento para a atitude, e
   em que situação concreta essa inferência estaria errada.
2. Slide 19: growth mindset rende d ≈ 0,05 nos estudos mais robustos; intenções
   de implementação, d = 0,27 a 0,66. Que magnitude você espera da **sua**
   intervenção, e qual é a **razão honesta** para esperar menos do que você
   gostaria?

### Critérios do ia-5.2

| Critério | Peso | O que precisa |
|---|---:|---|
| `gh_autenticado` | 2 | `gh auth status` OK, na conta do roster |
| `atitude_existe` | 2 | `atitude.md` na raiz |
| `atitude_nomeia_atitude` | 2 | uma das atitudes do slide 15 |
| `atitude_marcador_fact` | 1 | `[FACT]` usado |
| `atitude_marcador_inference` | 1 | `[INFERENCE]` usado |
| `atitude_marcador_assumption` | 1 | `[ASSUMPTION]` usado |
| `atitude_qualidade` | 8 | indicador observável, regra replicável, limites (LLM avalia) |
| `historico_existe` | 2 | `historico.md` na raiz |
| `historico_40_linhas` | 3 | ≥ 40 linhas não vazias |
| `medir_existe` | 2 | `medir.py` na raiz |
| `medir_le_historico` | 2 | o script lê `historico.md` |
| `medir_grava_csv` | 2 | o script grava `medicao.csv` |
| `medir_grava_envelope` | 1 | o script grava `evidencia-medicao.json` |
| `medicao_existe` | 1 | `medicao.csv` na raiz |
| `medicao_colunas` | 3 | as 6 colunas do contrato |
| `medicao_cinco_episodios` | 4 | ≥ 5 linhas de dados |
| `envelope_existe` | 1 | `evidencia-medicao.json` na raiz |
| `envelope_indicador` | 2 | `indicador` declarado |
| `envelope_episodios` | 3 | `episodios` ≥ 5 |
| `envelope_violacoes` | 2 | `violacoes` presente |
| `medicao_sem_traceback` | 3 | o script rodou sem estourar exceção |
| `trecho_bate_com_historico` | 6 | o `trecho_exemplo` existe no corpus |
| `intervencao_existe` | 2 | `intervencao.md` na raiz |
| `intervencao_se_entao` | 3 | a forma "se X, então Y" |
| `intervencao_desfecho` | 2 | variável-resultado / efeito nomeado |
| `intervencao_qualidade` | 9 | gatilho reconhecível, ação executável, abandono (LLM avalia) |
| pergunta 1 | 18 | comportamento x atitude — respondida na CLI |
| pergunta 2 | 12 | a magnitude e o desconto honesto — respondida na CLI |
| **Total** | **100** | |

---

## Quando der errado

**`evidencia_bate_com_tabela` falhando com tudo no lugar.** A `evidencia_citada`
do envelope tem que aparecer *literalmente* dentro da `tabela-auditoria.md`. As
duas causas comuns: `json.dumps` sem `ensure_ascii=False`, e barra invertida no
caminho (`app\grader.py`), que o JSON escapa para `app\\grader.py` e deixa de
bater. **Normalize para `/`** antes de escrever o envelope — o `git ls-files`
já devolve com `/`.

**`trecho_bate_com_historico` falhando.** Mesma família. O `trecho_exemplo` tem
que ser um pedaço literal do `historico.md`: sem aspas, sem barra invertida, sem
recortar no meio de um caractere acentuado.

**`inv_*` ou `envelope_*` zerados com o script funcionando.** A CLI roda
`python inventario.py` **no diretório de onde você chamou `autograde validar`**.
Rode da raiz da pasta do exercício, e faça o script resolver os caminhos
relativos ao próprio arquivo (`Path(__file__).parent`), não ao `cwd`.

**`inv_commits` zerado.** Os repos do `repos-auditados.txt` somam menos de 5
commits, ou o caminho não é um repositório git. Confira com
`git -C <caminho> rev-list --count HEAD`.

**O envelope sai junto com aviso do git.** Normal, e não reprova: a CLI
concatena o *stderr* no *stdout* antes de mandar, e por isso o autograder
procura os campos por regex, não fazendo `json.loads` da saída inteira. O que
**não** pode é o script estourar exceção — `Traceback` na saída zera pontos.

**`medicao_colunas` zerado com o CSV no lugar.** O cabeçalho precisa **conter**
`episodio,fonte,indicador,valor,violacao,trecho` — sem acento, minúsculas.
Colunas extras podem entrar; as seis não podem faltar nem mudar de nome.

**`prompt_proibe_supor` zerado com a regra escrita.** A regex procura a negação
**perto** do verbo: "é proibido supor", "não suponha", "nunca especule". Um
parágrafo que diz "suposições são um problema conhecido" fala *sobre* supor sem
proibir nada.

**`prompt_niveis_criticidade` zerado com os níveis lá.** Os quatro têm que
aparecer — Bloqueante, Alto, Médio, Baixo. Trocar "Bloqueante" por "Crítico"
custa os 3 pontos: o nível é o do slide.

**`tabela_criticidade_marcada` zerado.** A regex conta ocorrências dos quatro
níveis e quer **5 ou mais** — uma por achado. Uma tabela com 5 achados em que
só 3 receberam nível não passa.

**Critério de arquivo zerado com o arquivo no lugar.** O caminho bate
exatamente, incluindo maiúsculas: `medicao.csv`, não `medição.csv`;
`evidencia-medicao.json`, não `evidencia_medicao.json`; `inventario.json` na
raiz.

**Os demais problemas** (403, 401, "Could not detect exercise from CWD",
submissão atrasada) estão na [Parte 7 do tutorial da Aula 1](Exercicios_Aula1.md#parte-7--quando-der-errado).
