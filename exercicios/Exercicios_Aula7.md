# Exercício da Aula 7 — ia-7.1: cooldown de pacotes

Slide 46. Em **31 de março de 2026**, uma conta de mantenedor do **axios**
(mais de 70 milhões de downloads por semana) foi usada para publicar as
versões `1.14.1` e `0.30.4`. Elas traziam uma dependência nova,
`plain-crypto-js@4.2.1`, cujo `postinstall` instalava um trojan de acesso
remoto no Windows, no macOS e no Linux. **As versões ficaram cerca de 3 horas
no npm** antes de serem retiradas.

O **cooldown** (em inglês, *minimum release age*) é a defesa mais barata
contra esse tipo de ataque: o gerenciador de pacotes se recusa a instalar
qualquer versão publicada há menos de N dias. Ataques assim costumam ser
detectados e removidos em horas, então um atraso de dias deixa o problema para
quem instalou primeiro.

**Cenário:** a sua equipe usa **npm** no frontend, **pnpm** no monorepo e
**uv** na API Python. **Meta: nenhuma versão com menos de 7 dias entra no
projeto.**

**Prazo: o do calendário da turma.** O `autograde validar` avisa se a
submissão está atrasada.

Se você ainda não fez o setup (Python, Git, `gh`, CLI `autograde` e login
Google), volte para a [Parte 1 do tutorial da Aula 1](Exercicios_Aula1.md#parte-1--setup-uma-vez-no-semestre).

---

## A armadilha deste exercício

Os três gerenciadores têm a mesma ideia com **três grafias e três unidades**:

| gerenciador | versão mínima | arquivo | chave | unidade |
|---|---|---|---|---|
| npm | **11.10** | `.npmrc` | `min-release-age` | **dias** |
| pnpm | **10.16** | `pnpm-workspace.yaml` | `minimumReleaseAge` | **minutos** |
| uv | **0.9.17** | `uv.toml` ou `[tool.uv]` do `pyproject.toml` | `exclude-newer` | **duração** (`"7 days"`, `"1 week"`, `"P7D"`) |

Dois erros passam **em silêncio**, sem nenhuma mensagem de erro:

- **A unidade errada.** `minimumReleaseAge: 7` no pnpm é um cooldown de **7
  minutos**. O arquivo parece certo, o pnpm aceita, e o axios malicioso
  (3 horas no ar) teria sido instalado.
- **A ferramenta velha.** O npm anterior à 11.10 lê `min-release-age=7` do
  `.npmrc`, devolve `7` no `npm config get` e **não aplica nada**. A única
  pista é um aviso: `npm warn Unknown project config "min-release-age"`.

No uv, cuidado com a **data fixa**. O `exclude-newer` também aceita uma data
(`"2026-09-17T00:00:00Z"`), mas aí o resolvedor fica congelado naquele dia: daqui
a um mês você continua sem ver nada publicado depois de 17/09. Cooldown é uma
**duração**, que anda com o calendário.

O autograder converte cada valor para dias e só aceita **exatamente 7**.

---

## Passo 1 — As ferramentas

```bash
npm --version     # precisa ser >= 11.10
pnpm --version    # precisa ser >= 10.16
uv --version      # precisa ser >= 0.9.17
```

Se o npm for anterior à 11.10:

```bash
npm install -g npm@latest
```

> O npm 12 exige Node **24.15 ou mais novo** (ou 22.22+). Se o seu Node for
> mais antigo, o npm 12 instala mas reclama a cada comando. Ou atualize o Node,
> ou fique no npm 11: `npm install -g npm@11`, que já traz o
> `min-release-age`.

O pnpm e o uv **não são conferidos pelo autograder**: ele só lê os arquivos.
Mas os arquivos não servem para nada com a ferramenta antiga, então atualize:
`npm install -g pnpm@latest` e `uv self update` (ou `pip install -U uv`).

## Passo 2 — A pasta do exercício

Crie uma pasta só para o exercício. Não precisa ser repositório git.

```bash
mkdir cooldown-lab
cd cooldown-lab
```

Num projeto de verdade cada arquivo moraria na raiz do projeto dele (o
`.npmrc` no frontend, o `pnpm-workspace.yaml` no monorepo, o `uv.toml` na
API). Aqui os três ficam juntos, na raiz da pasta, porque é dali que o
`autograde validar` lê.

## Passo 3 — Tarefa 1: configurar

Crie os três arquivos na raiz de `cooldown-lab`, **um por gerenciador**:

- `.npmrc` para o npm;
- `pnpm-workspace.yaml` para o pnpm;
- `uv.toml` para o uv. Se preferir, use a seção `[tool.uv]` de um
  `pyproject.toml`.

Em cada um, configure o cooldown de 7 dias **na unidade daquele
gerenciador** (veja a tabela acima). Pode pedir ajuda ao agente, mas confira a
conta: a pergunta "quantos minutos têm 7 dias?" é exatamente onde ele erra
quando você não pede para ele mostrar o cálculo.

Confira que as ferramentas leem o que você escreveu:

```bash
npm config get min-release-age          # 7, e SEM o aviso "Unknown project config"
pnpm config get minimumReleaseAge       # 10080
echo httpx | uv pip compile -          # resolve sem erro de parse no uv.toml
```

> **Não abra exceção curinga.** `minimumReleaseAgeExclude: ["*"]` no pnpm ou
> `exclude-newer-package` com `*` no uv é desligar o cooldown com outro nome,
> e o autograder desconta.

## Passo 4 — Tarefas 2 e 3: as perguntas

As duas tarefas escritas são as **perguntas** que o `autograde validar` faz no
terminal. Responda cada uma **em até 3 linhas**:

- **Tarefa 2, justificar:** por que o cooldown de 7 dias teria barrado as
  versões maliciosas do axios?
- **Tarefa 3, avaliar:** cite um custo que o cooldown traz para a equipe e o
  que você faria para conviver com ele.

## Passo 5 — Validar e submeter

Da raiz de `cooldown-lab`:

```bash
autograde validar ia-7.1
```

O boletim mostra cada critério e depois faz as duas perguntas. Ao final ele
pergunta se você quer submeter.

> ⚠️ **Rode fora do terminal do agente.** A CLI roda o `npm` e um verificador
> em Python na sua máquina. Terminal de agente costuma mexer em PATH, e o npm
> que o autograder encontra pode não ser o que você atualizou.

Cada exercício aceita **10 tentativas por dia**, com 30 segundos entre elas, e
**a maior nota conta**. Um `validar` que chega a responder as perguntas já
gasta uma tentativa, mesmo sem submeter.

---

## Como é a nota

| bloco | pontos | o que conta |
|---|---|---|
| identidade | 2 | `gh auth status` bate com o seu usuário do roster |
| os arquivos | 6 | `.npmrc`, `pnpm-workspace.yaml` e o `exclude-newer` do uv existem |
| npm | 22 | 7 dias no `.npmrc` (10), npm ≥ 11.10 (6), `npm config get` devolve 7 (3) e sem o aviso `Unknown config` (3) |
| pnpm | 18 | chave no `pnpm-workspace.yaml` (4) e 7 dias em minutos (14) |
| uv | 18 | duração, não data fixa (6), e 7 dias (12) |
| exceção | 4 | nenhuma exceção curinga |
| perguntas | 30 | tarefas 2 e 3, 15 cada, corrigidas por um juiz LLM |

**Total: 100.**

## Se der errado

| sintoma no boletim | causa provável |
|---|---|
| `npm >= 11.10` reprovado | `npm --version` antigo, ou o terminal está achando outro npm. Rode `npm --version` no mesmo terminal do `autograde` |
| `o npm reconhece a chave` reprovado | mesmo caso: o npm antigo lê a chave, mas avisa que não a conhece |
| `npm config get ... devolve 7` reprovado | o `.npmrc` não está na pasta onde você rodou o `validar`, ou a linha está comentada |
| `pnpm: ... 7 dias` reprovado | a unidade: o pnpm conta em **minutos** |
| `uv: ... duração, não uma data fixa` reprovado | você escreveu uma data no `exclude-newer` |
| `exclude-newer declarado` reprovado | falta o `uv.toml`, ou o `exclude-newer` está fora da seção `[tool.uv]` do `pyproject.toml` |

## Fontes

- DepsGuard, "Dependency cooldown": <https://depsguard.com/cooldown>
- npm Docs, configuração `min-release-age`:
  <https://docs.npmjs.com/cli/v12/using-npm/config/>
- pnpm, `minimumReleaseAge`:
  <https://pnpm.io/settings/dependency-resolution>
- uv, `exclude-newer`: <https://docs.astral.sh/uv/reference/settings/#exclude-newer>
- Microsoft Security Blog, "Mitigating the Axios npm supply chain compromise"
  (01/04/2026)
