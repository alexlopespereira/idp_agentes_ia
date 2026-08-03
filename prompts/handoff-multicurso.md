# Migração multi-curso do autograder — CONCLUÍDA E VALIDADA EM PRODUÇÃO

> Status: **validado de ponta a ponta em 2026-08-02.** Este documento era um handoff
> com trabalho pendente; virou o registro do que foi provado. Nada aqui exige ação.

## O desenho

O curso é derivado do **prefixo do id do exercício** — `ia-1.1` → curso `ia`; sem prefixo
→ curso `td`. Resolve três coisas de uma vez:

1. **Agregação.** `/me/grades` agrega por `exercicio`. Como os dois cursos têm um `1.1`,
   sem prefixo as notas do aluno se fundiriam num registro só, com a maior nota entre os
   cursos. `ia-1.1` != `1.1` conserta isso sem tocar no rollup.
2. **Roteamento.** `EXERCISES_BASE_URL_<CURSO>` → `EXERCISES_BASE_URL` (fallback).
3. **Auditoria.** A coluna `curso` (T) da Sheet é *derivada* do prefixo, não digitada.

Módulos: `autograde-idp-backend/app/curso.py` e o espelho
`autograde-idp/autograde_idp/curso.py`. **Os dois precisam concordar bit a bit** — se
divergirem, o CLI manda evidência sob um id que o backend não reconhece.

Uma Submissions Sheet única serve os dois cursos. A separação vem do prefixo do id, não
de planilhas separadas.

## Validação em produção (revisão `autograde-backend-00034-mfb`)

Quatro exercícios resolvidos, submetidos e conferidos na planilha:

| Exercício | Nota | Linha | col. E (turma) | col. T (curso) |
|---|---|---|---|---|
| `ia-1.1` | 99/100 | 305 | `IA-2026-02` | `ia` |
| `ia-1.2` | 99/100 | 306 | `IA-2026-02` | `ia` |
| `ia-1.3` | 100/100 | 307 | `IA-2026-02` | `ia` |
| `ia-1.4` | 99/100 | 308 | `IA-2026-02` | `ia` |

Repos de teste: `teste-ia-1-1` … `teste-ia-1-4` em github.com/alexlopespereira.

**A prova que importa** — `autograde notas` lista os dois cursos como entradas separadas:

```
1.1       | 110 | 5 tentativas   <- Transformação Digital, histórico
ia-1.1    |  99 | 1 tentativa    <- Agentes de IA, novo
```

Sem o prefixo, essas duas linhas teriam virado uma só, com nota 110 e 6 tentativas.

Sondas complementares: `ia-9.9` → `404 exercise_not_found` (roteou pro repo do curso `ia`
e não achou); `1.1` com turma IA → `403 turma_not_eligible` (id sem prefixo ainda carrega
do `idp_governodigital` e o gate de turma funciona).

## Como adicionar o próximo curso

1. Prefixo de 2–8 letras minúsculas (ex.: `ia`).
2. YAMLs nomeados com o id completo — `xx-1.1.yaml`, com `exercicio: "xx-1.1"` e o
   `turmas:` da turma nova.
3. `EXERCISES_BASE_URL_<PREFIXO>` em três lugares: `cloudbuild.yaml`,
   `.github/workflows/cloud-run-deploy.yml` e a tabela do `README.md` do backend.
4. Se reaproveitar exercício com evidência shell, registrar o id **qualificado** em
   `app/evidence/shell.py:_WHITELIST` e no `_GH_BASIC_IDS` do CLI. É explícito de
   propósito: um `xx-4.1` não herda por acidente a whitelist do `4.1` de TD.
5. Alunos no roster com a turma nova.
6. Header da coluna nova na Sheet, se houver — o writer só faz append, nunca escreve a
   linha 1.

## Armadilhas registradas

- **Deploy:** não rode `cloudbuild.yaml` sem passar as 4 substitutions
  (`_GOOGLE_OAUTH_CLIENT_ID`, `_ROSTER_URL`, `_SHEET_ID`, `_ROSTER_SHEET_ID`) — os
  defaults são `""` e o `--set-env-vars` **apaga** as envs. O caminho seguro é build
  isolado + `gcloud run deploy --image ... --update-env-vars=...`.
- **Secret:** `github-pat:latest` só é reresolvido quando **nasce uma revisão nova**.
  Adicionar a versão no Secret Manager não basta — precisa de um
  `gcloud run services update --update-secrets=GITHUB_PAT=github-pat:latest`.
- **PAT com `
` no fim** devolve 401. Use `printf '%s'`, nunca `echo`.
- **Playwright no Google Sheets:** `fill()` não commita (o editor ignora eventos
  sintéticos). Funciona: `#t-name-box` para selecionar → `press_key` de um caractere para
  abrir o editor → `browser_type` em `#waffle-rich-text-editor` com `slowly: true`.
  Para *ler* sem editar, `browser_evaluate` lendo `#t-formula-bar-input-container`.
- **ADC do gcloud dá 403 nas Sheets** (escopo insuficiente); impersonar a service account
  é bloqueado pelo classificador. Sobra o Playwright com o Chrome logado.

## Dívidas conhecidas (não bloqueiam)

- **Aluno em dois cursos é impossível.** O roster tem `email` como chave única com uma
  única turma — `parse_roster` levanta `email duplicado`. Resolver exigiria a chave virar
  `(email, curso)` e o middleware de auth saber de qual curso é o request.
- **Casing da coluna `curso`.** As linhas históricas foram preenchidas à mão com `TD`
  (maiúsculo); o código grava `td`/`ia` (minúsculo). Filtros que distinguem maiúsculas vão
  tratar `TD` e `td` como valores diferentes.
- **`R1` da Submissions** diz `perguntas_subjetivas`, mas o código grava `respostas_json`
  nessa coluna. Cosmético — o header é manual.
- **Repos de teste** `teste-ia-1-*` continuam públicos na conta; apagar quando não forem
  mais úteis.
