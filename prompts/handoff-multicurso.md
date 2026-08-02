# Handoff — concluir a validação do multi-curso do autograder

Cole o bloco abaixo como primeira mensagem numa sessão nova do Claude Code,
com o cwd em `c:\Projects\idp` (ou o equivalente no outro host).

---

## Contexto

O autograder IDP passou a servir **dois cursos** contra a **mesma** Submissions Sheet:
Transformação Digital (ids sem prefixo: `1.1`) e Agentes de IA (ids com prefixo: `ia-1.1`).
A mudança já está implementada, testada, mergeada em `main` nos 5 repos e **deployada em
produção**. Falta **uma única verificação de ponta a ponta**, que está bloqueada por uma
credencial expirada.

### Como o multi-curso funciona (desenho, não improviso)

O curso é derivado do **prefixo do id do exercício** — `ia-1.1` → curso `ia`; sem prefixo →
curso `td`. Isso resolve três coisas de uma vez:

1. **Agregação.** `/me/grades` agrega por `exercicio`. Como os dois cursos têm um `1.1`,
   sem prefixo as notas do aluno se fundiriam. `ia-1.1` != `1.1` conserta isso sem tocar
   no rollup.
2. **Roteamento.** `EXERCISES_BASE_URL_<CURSO>` → `EXERCISES_BASE_URL` (fallback).
3. **Auditoria.** A coluna `curso` (T) da Sheet é *derivada* do prefixo, não digitada.

Módulos-chave: `autograde-idp-backend/app/curso.py` e o espelho
`autograde-idp/autograde_idp/curso.py`. **Os dois precisam concordar bit a bit** — se
divergirem, o CLI manda evidência sob um id que o backend não reconhece.

### Estado atual (tudo verificado)

- **5 repos** (`idp_governodigital`, `autograde-idp`, `autograde-idp-backend`,
  `assistente-aulas`, `idp_agentes_ia`) em `main`, sincronizados com `origin`, working
  tree limpo.
- **Testes verdes:** backend 346 passed, CLI 170 passed / 3 skipped, `ruff` limpo.
- **Deploy:** revisão `autograde-backend-00033-9g2`, imagem
  `gcr.io/autograde-314802/autograde-backend:f77a656`, com `EXERCISES_BASE_URL_IA`
  apontando pro `idp_agentes_ia`.
- **Roster** (`1MH-gPNiR7NIBxu4hv3rZ4gGLIG7TR_oWwtQ88Jk6r90`, aba `gid=1322786395`):
  a linha `alexlopespereira@gmail.com` foi mudada de `TD-2026-01` para **`IA-2026-02`**
  (célula `C2`) para permitir o teste. Os outros 29 alunos não foram tocados.
- **Submissions Sheet** (`1xnTuYIn8cGi0jGK_eLzcXgAJrRJdD7CqMR82wv0_Src`, aba `submissoes`):
  `S1` = `judge_degraded` (estava vazio, preenchi), `T1` = `Curso`.
- **Repo de teste do ia-1.1:** https://github.com/alexlopespereira/teste-ia-1-1
  (público, README não-vazio, 2 commits) — clone local em `c:\Projects\idp\teste\`.
- **CLI:** `autograde` 0.7.0 instalado, token válido em `~/.git-exercicios/`.

### O que já está PROVADO em produção

Três sondas trianguladas, todas contra o backend real:

| Sonda | Resultado | Prova |
|---|---|---|
| `autograde validar ia-1.1` | `502 github_unavailable` | Achou o YAML no `idp_agentes_ia`, passou o gate de turma, parou só na coleta do GitHub |
| `autograde validar ia-9.9` | `404 exercise_not_found` | Roteou pro repo do curso `ia` e corretamente não achou |
| `autograde validar 1.1` | `403 turma_not_eligible` | Id sem prefixo ainda carrega do `idp_governodigital`; gate rejeita pois a turma agora é IA |

### O que NÃO está provado

**A coluna `curso` (T) sendo escrita numa linha real da Sheet.** Só tem cobertura de teste
unitário. Exige uma submissão bem-sucedida.

---

## 🚨 BLOQUEIO — resolver primeiro

**O autograder está fora do ar para TODOS os alunos.** O `GITHUB_PAT` do backend retorna
**401**; qualquer submissão morre com `502 github_unavailable`.

**Não foi causado pelo deploy desta sessão.** O mesmo `github_collect_failed status=401`
já aparece nos logs da revisão `00031` em **2026-07-22T00:25**, e a revisão `00032` (no ar
desde 22/07) usava a **mesma versão do secret** que a atual (versão 3, criada 22/07
12:14:48 — 20 segundos antes de `00032` nascer). A API do GitHub está no ar (200 anônimo).

Rotação do PAT é ação do usuário (credencial). Comandos:

```bash
printf '%s' '<NOVO_PAT_CLASSIC_COM_ESCOPO_repo>' | \
  gcloud secrets versions add github-pat --data-file=- --project=autograde-314802

# necessário: `:latest` só é resolvido quando nasce uma revisão nova
gcloud run services update autograde-backend --region=southamerica-east1 \
  --project=autograde-314802 --update-secrets=GITHUB_PAT=github-pat:latest
```

Confirmar que destravou:

```bash
cd c:/Projects/idp/teste/teste-ia-1-1
printf 'x\n' | autograde validar ia-1.1
# esperado: boletim com notas — NÃO 502 github_unavailable
```

---

## TAREFA

Depois do PAT rotacionado:

1. **Criar e resolver** os repos dos exercícios restantes em `c:\Projects\idp\teste\`.
   Os specs estão em `c:\Projects\idp\idp_agentes_ia\exercicios\ia-1.{1,2,3,4}.yaml` —
   **leia-os**, não confie neste resumo:
   - `ia-1.2` — repo público + ≥1 PR com título descritivo + evidência `gh`.
   - `ia-1.3` — repo público + ≥1 commit + evidência `gh`.
   - `ia-1.4` — repo público + ≥1 PR **mergeado** + ≥2 commits + evidência `gh`.
   Um repo separado por exercício (o CLI avisa se o mesmo `repo_url` for reusado).
   O owner precisa bater com `github_username` do roster (`alexlopespereira`).

2. **Submeter os 4.** Cada exercício tem uma pergunta aberta corrigida por LLM; o CLI
   pede a resposta interativamente, mas `input_fn` lê de pipe:
   ```bash
   printf 'sua resposta aqui\n' | autograde validar ia-1.1 --auto-submit
   ```
   A resposta precisa explicar **com palavras próprias** ≥2 comandos (`git add`,
   `git commit`, `gh pr create`, `gh pr merge`…) — respostas evasivas são rejeitadas
   pelo juiz. Rate limit: 10/dia + cooldown de 30s por (email, exercício).

3. **Conferir a planilha.** Este é o ponto do exercício todo. Abrir a Submissions Sheet
   e confirmar, nas 4 linhas novas:
   - coluna `F` (`exercicio`) = `ia-1.1`…`ia-1.4` (COM prefixo);
   - coluna `T` (`curso`) = `ia`;
   - coluna `E` (`turma`) = `IA-2026-02`;
   - as linhas históricas de TD **não** foram afetadas.
   A Sheet é privada e o ADC do gcloud dá 403 (escopo insuficiente) — **use o Playwright
   MCP**, que funciona com o Chrome logado. Impersonar a service account é bloqueado pelo
   classificador; não tente contornar.

   Dica de Playwright no Google Sheets: `fill()` **não** commita (o editor ignora eventos
   sintéticos). O que funciona: `#t-name-box` para selecionar a célula → `press_key` de um
   caractere para abrir o editor → `browser_type` em `#waffle-rich-text-editor` com
   `slowly: true` e `submit: true`. Para *ler* sem editar, use `browser_evaluate` lendo
   `#t-formula-bar-input-container`.

4. **Corrigir o que aparecer** e retestar até passar.

5. **PR + merge** de qualquer correção, nos repos afetados.

## Ao terminar, reverter

- Voltar `C2` do roster para `TD-2026-01` (senão a conta do professor não submete
  exercícios de TD).
- Decidir o destino dos 4 repos `teste-ia-1-*` no GitHub (apagar ou manter).

## Pendências menores (não bloqueiam)

- `R1` da Submissions diz `perguntas_subjetivas`, mas o código grava `respostas_json`
  nessa coluna. Cosmético — o header é manual — mas está errado.
- `assistente-aulas` tem `disciplinas/agentes/v1/` untracked: deixado de fora de propósito
  porque tem 2 locks `~$*` (PowerPoint aberto) e duplicatas de rascunho.
- **Aluno em dois cursos continua impossível:** o roster tem `email` como chave única com
  uma única turma (`parse_roster` levanta `email duplicado`). Resolver exigiria a chave
  virar `(email, curso)` e o middleware de auth saber de qual curso é o request. Fora do
  escopo daquela mudança, mas é dívida conhecida.

## Regras de trabalho

- Verifique funcionalmente antes de afirmar que algo funciona — confirme o resultado
  realizado, não a intenção.
- Marque incerteza com `[FATO]` / `[INFERÊNCIA]` / `[SUPOSIÇÃO]` e termine com grau de
  confiança.
- Nunca peça ao usuário para rodar comandos git; execute você mesmo.
- Não versione segredos. O PAT nunca deve aparecer em commit, log ou output.
