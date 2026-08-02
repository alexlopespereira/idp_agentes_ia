# TAREFA: criar a skill de Claude Code `questoes-conceituais`

Crie uma **skill de Claude Code** que gera questões conceituais Verdadeiro/Falso a
partir de um documento de aula. Antes de escrever, invoque a skill `write-a-skill`
(se disponível) e siga a estrutura oficial de skills (SKILL.md com frontmatter).

## Contexto de domínio (por que a skill existe)
É para um curso de **Transformação Digital no setor público (Brasil)**. As questões
treinam o **nível 1 da taxonomia de Bloom (lembrança/reconhecimento)**: o aluno só
reconhece se uma afirmação sobre um conceito ensinado é verdadeira ou falsa — sem
aplicar, analisar ou avaliar. O público-alvo é gestor público.

## Estrutura de arquivos a criar
Em `.claude/skills/questoes-conceituais/`:
- `SKILL.md` — frontmatter com `name: questoes-conceituais`, uma `description` rica
  em gatilhos ("gerar questoes", "questoes verdadeiro/falso", "quiz conceitual",
  "questoes de lembranca/Bloom", "/questoes-conceituais"), e
  `argument-hint: "<arquivo-aula> <quantidade> [--foco \"topicos\"]"`.
- `README.md` — resumo humano: o que faz, como usar, exemplos, output, princípio de design.
- `examples/exemplo-saida.md` — um exemplo ilustrativo do formato de saída (marcado
  explicitamente como ilustrativo).

## Argumentos (extrair de $ARGUMENTS, aceitar texto livre)
- `<arquivo-aula>` (obrigatório): caminho do documento (`.md`, `.txt`, `.pdf`) — o token
  que parece um caminho.
- `<quantidade>` (obrigatório): inteiro de questões; **default 10** se ausente.
- `--foco "topicos"` (opcional): conceitos a priorizar.
- Aceitar forma posicional (`aula03.md 20`) E linguagem natural ("gere 20 questões a
  partir de aula03.md"). Se o caminho não existir, checar typo óbvio e confirmar antes.

## NÚCLEO da skill: heurística de relevância (a decisão mais importante)
Regra fixa ao extrair conceitos. Teste-mestre: *"Um gestor público precisa **lembrar
deste conceito** para tomar melhores decisões de desenho de serviço?"* Se sim → vira
questão; se é trivia → descarta.

**INCLUIR** (relevante p/ administração pública):
- Frameworks/metodologias e suas características distintivas (PDCA, RUP, Scrum, Service
  Blueprint, Lean Startup, COBIT, ITIL…).
- Princípios/regras acionáveis (Once-Only, mandato API, linha de visibilidade, linha de
  interação, design universal, governo como plataforma).
- Definições de conceitos centrais (frontstage/backstage, entropia em serviços,
  omnichannel, evidências físicas, intangibilidade, As-Is vs To-Be).
- Relações causais e trade-offs ("se X então Y", "A difere de B porque…").
- Classificações/taxonomias (níveis Bronze/Prata/Ouro da Conta gov.br, camadas do
  blueprint, matriz de Rumsfeld).
- Função/papel de componentes de governo (CIN, login gov.br, PagTesouro, Notifica gov.br)
  — quando o ponto é **o que o componente faz / qual problema resolve**.

**EXCLUIR** (fatos irrelevantes — não gerar questão):
- Datas específicas (1984, 2002…) — salvo quando a data **é** o conceito.
- Nomes próprios como item de memorização (Shostack, Deming, Bezos…) — só incluir quando
  associar **autor ↔ contribuição** for o conceito ensinado.
- Números/estatísticas pontuais (36 milhões, 90%…) como fim em si.
- Anedotas/exemplos ilustrativos (Spa do Vinho, o engraxate…) — importa o **princípio que
  ilustram**, não o exemplo.
- Detalhes visuais/formatação de slides.

## Restrição Bloom (obrigatória)
Somente lembrança/reconhecimento. As afirmações devem ser verificáveis **lendo o material**
— não exigir aplicar a caso novo, analisar, comparar cenários hipotéticos ou avaliar. Se
uma questão exige raciocínio além de reconhecer o conceito, reescrever ou descartar.

## Regras de redação das afirmações V/F
1. Balanceamento **~50/50** V/F, em ordem **embaralhada** (não agrupar V e depois F).
2. Cada afirmação isola **UM** conceito (nunca dois na mesma frase).
3. **Falsas = equívocos plausíveis**, não negações absurdas. Técnicas: trocar atributo entre
   dois conceitos (dar ao Cascata algo do Espiral); inverter relação causal/fronteira (pôr o
   backstage acima da linha de visibilidade); generalizar indevidamente um caso. **Evitar**
   "O PDCA não existe" (falso óbvio).
4. Sem pistas artificiais: evitar "sempre/nunca/todos" que denunciem a resposta.
5. Português (BR) com **acentuação correta obrigatória** — acentos, til, cedilha. **Nunca**
   ASCII sem acento ("serviço" não "servico", "fricção" não "friccao").

## Formato de saída
Salvar `.md` **ao lado do documento fonte**: `<dir-do-fonte>/questoes-<nome-do-fonte>.md`.
Estrutura:
```markdown
# Questoes Conceituais (V/F) — <titulo da aula>

> Fonte: `<caminho>`
> Nivel Bloom: 1 (lembranca) · Tipo: Verdadeiro/Falso · Total: <N> (<n_V> V / <n_F> F)
> Gerado em: <AAAA-MM-DD>

## Questoes
1. ( ) <afirmacao>
...
---
## Gabarito
| # | Resposta | Conceito | Justificativa |
|---|----------|----------|---------------|
| 1 | V | <conceito> | <por que é verdadeira, 1 linha> |
| 2 | F | <conceito> | <qual é o correto, 1 linha> |
```
Cada falsa cita, no gabarito, **qual seria o correto**.

## Procedimento (ReAct) que a SKILL.md deve instruir
1. Resolver argumentos (caminho + quantidade + `--foco`).
2. Ler o documento (Read; PDF via `pages`). Se `.pptx`/`.docx` não-textual falhar, avisar e
   sugerir converter para `.md`/`.pdf`.
3. Extrair conceitos candidatos pela heurística — lista MAIOR que N.
4. Selecionar os N mais relevantes (respeitar `--foco`).
5. Redigir 1 afirmação V/F por conceito, alternando V/F e distribuindo falsas como equívocos.
6. Montar o arquivo (questões + gabarito justificado), salvar no caminho-irmão.
7. Reportar: caminho salvo + resumo (N, quantas V/F, conceitos cobertos).

## Checklist (Definition of Done) a incluir na SKILL.md
- [ ] Nº de questões == quantidade solicitada.
- [ ] Nenhuma exige aplicação/análise (só reconhecimento).
- [ ] Nenhuma testa data/nome/estatística como fim em si.
- [ ] ~50/50 V/F embaralhado.
- [ ] Cada falsa tem correção no gabarito.
- [ ] Arquivo salvo em `<dir-fonte>/questoes-<nome>.md` e caminho reportado.

## Gotchas a documentar na SKILL.md
- `.pptx` não é texto puro: Read pode falhar → preferir `.md`/`.pdf`, avisar em vez de inventar.
- Não alucinar conceitos: toda afirmação (V ou F) deriva de algo **presente** no documento;
  uma falsa é um equívoco sobre um conceito que **está** no material, não inventado.
- Quantidade > conceitos disponíveis: gerar quantas der com qualidade e avisar — não inflar
  com trivia para bater o número.
- Skills antigas (`skill.json` + `instructions.md`) NÃO registram como slash command no Claude
  Code atual; é preciso `SKILL.md` com frontmatter, e **reiniciar a sessão** para o comando aparecer.

Ao terminar, liste os arquivos criados e lembre que é preciso reiniciar a sessão do Claude
Code para o `/questoes-conceituais` aparecer.
