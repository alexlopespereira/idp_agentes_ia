# Exercício da Aula 8 — ia-8.1: grill-me para achar oportunidades para o Jev

Slide 33. Nos slides 30 a 32 você viu o **Jev**, da TypeSafe AI: um modelo
"System One" que **não gera texto**. Ele recebe um **estado** (um ticket, um
e-mail, um documento, um log) e **perguntas tipadas**, e devolve **decisões
estruturadas com confiança calibrada**, em 70 a 500 ms. Funciona como um "if
inteligente" dentro do seu código.

Neste exercício você não escreve código. Você deixa o agente te
**interrogar** (com o `/grill-me`, que você já usou no
[ia-3.2](Exercicios_Aula3.md#exercício-ia-32--grill-me-na-revisão-bibliográfica-da-dissertação))
sobre os projetos que você faz com IA, até achar onde o Jev entra de verdade.

**Prazo: o do calendário da turma.** O `autograde validar` avisa se a
submissão está atrasada.

Se você ainda não fez o setup (Python, Git, `gh`, CLI `autograde` e login
Google), volte para a [Parte 1 do tutorial da Aula 1](Exercicios_Aula1.md#parte-1--setup-uma-vez-no-semestre).

---

## O Jev em uma tabela

| | |
|---|---|
| **Entrada** | um estado (texto) e uma ou mais perguntas tipadas, avaliadas em paralelo numa chamada só |
| **Choice** | escolhe **uma opção de uma lista fechada** (área do ticket: `fiscal`, `ti`, `rh`) |
| **Score** | dá uma **nota numa escala ordenada** (urgência de 1 a 5) |
| **Noul** | dá a **probabilidade de uma afirmação ser verdadeira** ("o pedido tem prazo legal?") |
| **Saída** | a resposta no tipo pedido, **com confiança de 0 a 1**. Nunca quebra o formato |
| **Preço** (acesso antecipado, set/2026) | **US$ 0,042 por milhão de tokens de entrada**; saída gratuita |
| **Onde não usar** | chat, texto longo, resumo, redação, geração de código |

A boa prática do slide 32 vira regra de correção: **perguntas atômicas** (uma
decisão cada), **combinadas no seu código**, e **a confiança decide quando
pedir revisão humana**.

## A armadilha deste exercício

Tratar o Jev como "um LLM mais barato". Resumir um processo, responder o
cidadão, escrever a introdução da dissertação: nada disso é do Jev, porque
nada disso é uma **decisão**. O juiz reprova oportunidade que é geração de
texto disfarçada.

A segunda armadilha é a oportunidade genérica: "classificar e-mails" vale para
qualquer pessoa. Aqui cada oportunidade tem de sair de um **projeto seu**, pelo
nome, e dizer o que acontece **hoje** naquele ponto.

---

## Passo 1 — Onde rodar

Abra o agente **na pasta que reúne vários projetos que você faz com IA** (por
exemplo, `C:\Projects` ou `~/code`). O agente precisa enxergar os projetos
para perguntar sobre eles.

> **Alternativa:** se você não tem uma pasta que centralize os projetos, rode
> na pasta da sua **pesquisa de mestrado**. Nesse caso, o grill-me deve passar
> por mais de uma etapa da pesquisa (coleta, triagem, análise, avaliação).

A pasta não precisa ser repositório git. Os dois arquivos da entrega ficam na
**raiz** dela, e é dali que você roda o `autograde validar`.

> **O que sai da sua máquina:** o autograder envia ao backend e ao juiz LLM
> **só o conteúdo dos dois arquivos entregues**, não os seus projetos. Mas o
> **agente** lê o que estiver na pasta. Se ela tiver dado sensível (PII,
> credenciais), diga ao agente o que ele não deve abrir.

## Passo 2 — A skill

Se você fez o ia-3.2, ela já está instalada. Confira:

```bash
npx -y skills list -g
```

Se `grill-me` não aparecer:

```bash
# troque --agent pelo seu harness: claude-code, codex, opencode ou pi
npx -y skills add mattpocock/skills --skill grill-me --agent claude-code -g
```

## Passo 3 — A sessão

Peça ao agente, na raiz da pasta:

```text
/grill-me baseado em tudo que você sabe sobre mim e meus projetos executados
com a ajuda da IA, me ajude a identificar oportunidades para utilizar o JEV na
sua potencialidade para otimizar custos, destravar casos de uso que não eram
viáveis ou melhorar a qualidade das decisões que são ou poderiam ser delegadas
a LLMs.

Contexto sobre o Jev: não gera texto; recebe um estado e perguntas tipadas
(Choice = opção de lista fechada, Score = nota em escala ordenada, Noul =
probabilidade de uma afirmação ser verdadeira) e devolve decisões com
confiança calibrada, em 70-500 ms, a US$ 0,042 por milhão de tokens de
entrada, com saída gratuita. Não serve para chat, texto longo ou código.

Numere as perguntas Q01, Q02, ... e, quando uma resposta minha derrubar uma
decisão anterior, diga qual. Ao final, salve a sessão inteira em
grill-me-transcript.md e escreva jev-oportunidades.md nesta pasta.
```

O parágrafo de contexto importa: o agente provavelmente não conhece o Jev, e
sem ele vai propor o Jev para gerar texto.

Durante a sessão, responda com **fatos**: qual projeto, qual chamada de LLM
existe hoje, quantas vezes por dia ela roda, quanto custa, quem confere o
resultado. "Não sei" é uma resposta válida, desde que venha com como descobrir.

## Passo 4 — O que você entrega

```
<pasta dos seus projetos>/
├── grill-me-transcript.md    # a sessão: ≥ 12 perguntas numeradas, com as suas respostas
└── jev-oportunidades.md      # as oportunidades que a sessão produziu
```

### `grill-me-transcript.md`

- numere cada pergunta como **`Q1`, `Q2`, …** ou **`Q01`, `Q02`, …**, no
  começo da linha (pode ser heading `## Q01 — ...` ou negrito `**Q01**`);
- **no mínimo 12 perguntas**, cada uma com a sua resposta logo abaixo;
- **pelo menos 2 vezes**, uma pergunta **reabre uma decisão anterior**, e o
  transcript diz qual:

  > **Q09** — Na Q04 você quis usar o Jev para gerar o parecer do avaliador.
  > Parecer é texto. Isso ainda vale?
  > **R:** Não. Reviso a Q04: o Jev dá as notas por critério; o parecer
  > continua no LLM, e só para os casos em que a confiança ficar baixa.

### `jev-oportunidades.md`

**Pelo menos 3 oportunidades**, e o conjunto cobre **os três eixos** do slide:
**custo**, **destravar** (caso antes inviável) e **qualidade** (decisão
delegada a LLM). Para cada uma:

1. **Projeto e ponto de decisão:** qual projeto, qual decisão, o que acontece
   **hoje** ali (chamada de LLM, regra fixa, humano, ou nada);
2. **Estado:** o que entra na chamada;
3. **Perguntas tipadas:** cada uma com o tipo (`Choice`, `Score` ou `Noul`),
   as opções ou a escala;
4. **O que o código faz com a resposta:** o **limiar de confiança** e o que
   acontece abaixo dele (humano, LLM maior, fila de revisão), e como você vai
   calibrar esse limiar;
5. **A conta:** volume (chamadas por dia ou mês) × tokens de entrada ×
   preço, hoje e com o Jev. Para "destravar", a conta que mostra por que
   antes não dava (custo ou latência) e agora dá.

Feche com uma seção **Onde o Jev não entra**: pelo menos um ponto dos seus
projetos que parece candidato e não é, e por quê.

## Passo 5 — Validar e submeter

Da raiz da pasta:

```bash
autograde validar ia-8.1
```

O boletim mostra os critérios e depois faz **duas perguntas**, 15 pontos cada:

- **Qual oportunidade você implementaria primeiro**, e por que ela é do Jev e
  não de um LLM de fronteira nem de uma regra fixa (if/regex)? Diga o
  projeto, a pergunta tipada e o eixo.
- **Qual ideia de uso do Jev o grill-me derrubou ou mudou** (cite o `Qnn`), e
  o que estava errado nela.

Cada exercício aceita **10 tentativas por dia**, com 30 segundos entre elas, e
**a maior nota conta**.

---

## Como é a nota

| Critério | Peso | O que precisa |
|---|---:|---|
| `gh_autenticado` | 2 | `gh auth status` OK, na conta cadastrada no roster |
| `skill_grill_me_disponivel` | 3 | `grill-me` aparece no `skills list` |
| `transcript_existe` | 2 | `grill-me-transcript.md` na raiz |
| `transcript_12_perguntas` | 5 | ≥ 12 perguntas numeradas `Qn`/`Qnn` |
| `transcript_respostas_substantivas` | 10 | respostas concretas, sobre projetos seus, pelo nome (LLM avalia) |
| `transcript_revisa_decisoes` | 8 | ≥ 2 revisões de decisão anterior (LLM avalia) |
| `oportunidades_existe` | 2 | `jev-oportunidades.md` na raiz |
| `oportunidades_perguntas_tipadas` | 4 | `Choice`, `Score` ou `Noul` citados pelo menos 3 vezes |
| `oportunidades_adequacao_jev` | 12 | ≥ 3 decisões (não geração), tipo certo, perguntas atômicas, os 3 eixos, um "onde não entra" (LLM avalia) |
| `oportunidades_rastreavel` | 8 | cada oportunidade sai de um projeto seu e aparece no transcript (LLM avalia) |
| `oportunidades_confianca_fallback` | 6 | limiar de confiança, fallback e como calibrar (LLM avalia) |
| `oportunidades_conta_custo` | 8 | volume × tokens × preço em pelo menos duas oportunidades (LLM avalia) |
| perguntas na CLI | 30 | as duas perguntas acima, 15 cada (LLM avalia) |
| **Total** | **100** | |

## Se der errado

| sintoma no boletim | causa provável |
|---|---|
| `skill grill-me disponível` reprovado | a skill foi instalada em outro escopo ou para outro agente. `npx -y skills list -g` |
| `transcript_12_perguntas` reprovado | numeração fora do começo da linha, ou `Pergunta 1` em vez de `Q1` |
| `oportunidades_perguntas_tipadas` reprovado | os tipos em português ("escolha", "nota"). Use os nomes do Jev: `Choice`, `Score`, `Noul` |
| adequação baixa | alguma oportunidade gera texto, ou usa `Score` para categorias sem ordem |
| conta de custo baixa | faltou o volume, ou o preço foi lido por mil tokens em vez de por milhão |

## Fontes

- TypeSafe AI, Jev: <https://typesafe.ai> e <https://docs.typesafe.ai>
  (consultados em set/2026). Preço, latência e comparação de custo são da
  própria TypeSafe e podem mudar.
- Matt Pocock, skill `grill-me`: <https://github.com/mattpocock/skills>
