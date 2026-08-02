# TAREFA: criar a skill de Claude Code `questoes-conceituais`

Crie uma **skill de Claude Code** que gera questões conceituais Verdadeiro/Falso a
partir de um documento de estudo **de qualquer tema**. Antes de escrever, invoque a
skill `write-a-skill` (se disponível) e siga a estrutura oficial de skills (SKILL.md
com frontmatter).

## Contexto e objetivo (por que a skill existe)
A skill é **agnóstica de domínio**: serve para qualquer disciplina ou assunto (uma aula,
um capítulo de livro, um artigo, uma documentação técnica, um manual). As questões treinam
o **nível 1 da taxonomia de Bloom (lembrança/reconhecimento)**: o aluno só reconhece se uma
afirmação sobre um conceito ensinado é verdadeira ou falsa — sem aplicar, analisar ou avaliar.
O **tema e o público-alvo são inferidos do próprio documento** (ou informados via `--dominio`),
e a heurística de relevância se ancora nesse tema.

## Estrutura de arquivos a criar
Em `.claude/skills/questoes-conceituais/`:
- `SKILL.md` — frontmatter com `name: questoes-conceituais`, uma `description` rica
  em gatilhos ("gerar questoes", "questoes verdadeiro/falso", "quiz conceitual",
  "questoes de lembranca/Bloom", "/questoes-conceituais"), e
  `argument-hint: "<arquivo> <quantidade> [--foco \"topicos\"] [--dominio \"tema/publico\"]"`.
- `README.md` — resumo humano: o que faz, como usar, exemplos, output, princípio de design.
- `examples/exemplo-saida.md` — um exemplo ilustrativo do formato de saída (marcado
  explicitamente como ilustrativo).

## Argumentos (extrair de $ARGUMENTS, aceitar texto livre)
- `<arquivo>` (obrigatório): caminho do documento de estudo (`.md`, `.txt`, `.pdf`) — o token
  que parece um caminho.
- `<quantidade>` (obrigatório): inteiro de questões; **default 10** se ausente.
- `--foco "topicos"` (opcional): conceitos/seções a priorizar nesta rodada.
- `--dominio "tema/publico"` (opcional): tema e público-alvo para ancorar a heurística de
  relevância (ex.: "biologia celular / estudantes de medicina", "direito tributário /
  concurseiros"). Se ausente, **inferir do conteúdo do documento**.
- Aceitar forma posicional (`capitulo3.md 20`) E linguagem natural ("gere 20 questões a
  partir de capitulo3.md"). Se o caminho não existir, checar typo óbvio e confirmar antes.

## NÚCLEO da skill: heurística de relevância (a decisão mais importante)
Regra fixa ao extrair conceitos, **ancorada no tema/público do documento** (inferido ou dado
via `--dominio`). Teste-mestre, parametrizado pelo domínio:

> *"Alguém que estuda este tema precisa **lembrar deste conceito** para raciocinar ou agir
> bem no domínio?"* Se sim → vira questão; se é trivia periférica → descarta.

O que conta como "conceito central" **depende do tema** — extraia as categorias abaixo do
próprio material, não de uma lista fixa.

**INCLUIR** (o que forma a espinha conceitual de qualquer tema):
- **Frameworks, modelos e metodologias** e suas características distintivas.
- **Princípios, leis e regras acionáveis** do domínio.
- **Definições de conceitos centrais** e termos técnicos (o vocabulário que estrutura o tema).
- **Relações causais e trade-offs** ("se X então Y", "A difere de B porque…").
- **Classificações, taxonomias e categorias** (tipos, níveis, camadas, fases).
- **Função/papel de componentes** — quando o ponto é **o que o componente faz / qual problema
  resolve**, não seu nome ou data.

> Exemplos de domínios distintos, só para calibrar a abrangência (não é lista fechada):
> num tema de *serviços públicos digitais* seriam Service Blueprint, princípio Once-Only,
> frontstage/backstage; em *biologia* seriam ciclo de Krebs, osmose, mitose vs meiose; em
> *finanças* seriam fluxo de caixa descontado, risco vs retorno, tipos de mercado. Adapte
> ao documento em mãos.

**EXCLUIR** (trivia — não gerar questão, em qualquer tema):
- **Datas específicas** — salvo quando a data **é** o conceito.
- **Nomes próprios como item de memorização** — só incluir quando associar **autor ↔
  contribuição** (ou **descobridor ↔ descoberta**) for o conceito ensinado.
- **Números/estatísticas pontuais** como fim em si.
- **Anedotas e exemplos ilustrativos** — importa o **princípio que ilustram**, não o exemplo.
- **Detalhes visuais/formatação** dos slides ou do documento.

## Restrição Bloom (obrigatória)
Somente lembrança/reconhecimento. As afirmações devem ser verificáveis **lendo o material**
— não exigir aplicar a caso novo, analisar, comparar cenários hipotéticos ou avaliar. Se
uma questão exige raciocínio além de reconhecer o conceito, reescrever ou descartar.

## Regras de redação das afirmações V/F
1. Balanceamento **~50/50** V/F, em ordem **embaralhada** (não agrupar V e depois F).
2. Cada afirmação isola **UM** conceito (nunca dois na mesma frase).
3. **Falsas = equívocos plausíveis**, não negações absurdas. Técnicas: trocar atributo entre
   dois conceitos do tema (dar a um modelo uma característica de outro); inverter relação
   causal/fronteira; generalizar indevidamente um caso particular. **Evitar** falsos óbvios
   ("O conceito X não existe").
4. Sem pistas artificiais: evitar "sempre/nunca/todos" que denunciem a resposta.
5. Português (BR) com **acentuação correta obrigatória** — acentos, til, cedilha. **Nunca**
   ASCII sem acento ("serviço" não "servico", "fricção" não "friccao"). *(Se o documento e o
   público forem de outro idioma, redigir no idioma do material.)*

## Formato de saída
Salvar `.md` **ao lado do documento fonte**: `<dir-do-fonte>/questoes-<nome-do-fonte>.md`.
Estrutura:
```markdown
# Questoes Conceituais (V/F) — <titulo do documento>

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
1. Resolver argumentos (caminho + quantidade + `--foco` + `--dominio`).
2. Ler o documento (Read; PDF via `pages`). Se `.pptx`/`.docx` não-textual falhar, avisar e
   sugerir converter para `.md`/`.pdf`.
3. **Identificar o tema/público** (do `--dominio` ou inferido do conteúdo) para ancorar a
   heurística.
4. Extrair conceitos candidatos pela heurística — lista MAIOR que N.
5. Selecionar os N mais relevantes para o tema (respeitar `--foco`).
6. Redigir 1 afirmação V/F por conceito, alternando V/F e distribuindo falsas como equívocos.
7. Montar o arquivo (questões + gabarito justificado), salvar no caminho-irmão.
8. Reportar: caminho salvo + resumo (tema detectado, N, quantas V/F, conceitos cobertos).

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
- Domínio ambíguo: se o documento misturar temas ou o tema não estiver claro, priorizar os
  conceitos mais recorrentes/estruturais e declarar no relatório qual tema foi assumido.
- Skills antigas (`skill.json` + `instructions.md`) NÃO registram como slash command no Claude
  Code atual; é preciso `SKILL.md` com frontmatter, e **reiniciar a sessão** para o comando aparecer.

Ao terminar, liste os arquivos criados e lembre que é preciso reiniciar a sessão do Claude
Code para o `/questoes-conceituais` aparecer.
