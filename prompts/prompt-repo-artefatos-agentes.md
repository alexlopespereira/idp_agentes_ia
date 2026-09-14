# Construindo um repositório de artefatos para agentes de IA

Material de apoio. Dois prompts, um por harness de execução. Escolha o da ferramenta que você tem instalada, cole na íntegra e responda à entrevista.

Os dois prompts levam ao mesmo destino: **um** repositório GitHub privado que governa globalmente o comportamento do seu agente, instalado por `git clone` seguido de **um** script. A arquitetura de dentro do repositório é sua — o agente vai entrevistá-lo para descobri-la, não para lhe entregar um template pronto.

---

## Pré-requisitos

**Variante 1 (Claude Code)** — a skill `grill-me` instalada em `~/.claude/skills/` ou `~/.agents/skills/`. Confira digitando `/grill-me` no Claude Code: se o comando não existir, instale antes.

**Variante 2 (Codex)** — uma skill de entrevista instalada em **`~/.agents/skills/`**. Esse é o diretório de skills de usuário do Codex; `~/.codex/skills/` é reservado às skills embutidas (`.system`) e não deve ser usado. Para instalar à mão:

```bash
mkdir -p ~/.agents/skills/grilling
# grave o conteúdo da skill em ~/.agents/skills/grilling/SKILL.md
```

Verifique com `/skills` dentro do Codex antes de seguir.

**Ambas** — `gh` autenticado (`gh auth status`) e `git` configurado.

---

## Variante 1 — para executar no **Claude Code**

```text
Use a skill /grill-me para conduzir esta tarefa. Não escreva um único arquivo antes de
me entrevistar e antes de eu confirmar que chegamos a um entendimento comum.

OBJETIVO
Criar um repositório GitHub PRIVADO que concentre os artefatos que direcionam o
trabalho dos agentes de IA na minha máquina, e que seja instalado por um `git clone`
seguido da execução de UM script. O repositório serve a UM harness, escolhido por mim
durante a entrevista, e não precisa guardar compatibilidade com nenhum outro.

Artefatos que o repositório deve conter, no mínimo:
- o arquivo de instruções globais do harness (CLAUDE.md ou AGENTS.md de nível usuário);
- skills;
- hooks;
- scripts.

O QUE VOCÊ DEVE ME PERGUNTAR
A arquitetura é minha decisão, não sua. Entreviste-me sobre ela livremente: como
organizar as pastas, o que é artefato e o que é gerador, quanto do meu contexto atual
migra para o repositório, o que fica de fora. Ofereça opções concretas com uma
recomendação sua em cada pergunta, e espere minha resposta antes de avançar.

Pergunte também, obrigatoriamente:
- qual harness o repositório vai governar (Claude Code ou Codex);
- qual o meu sistema operacional;
- quais artefatos eu já tenho hoje — pode ser nenhum;
- o conteúdo das regras globais que eu quero impor;
- no Windows, como quero declarar os pacotes a instalar (ofereça as opções
  apropriadas e me deixe escolher).

RESTRIÇÕES RECOMENDADAS
1. Repositório PRIVADO, criado por você com `gh repo create --private` ao final.
2. Nenhum segredo, token, chave ou credencial entra no repositório. Repositório
   privado é clonado para outras máquinas, entra em backup e vira público com um
   clique.
3. Instalação = `git clone` + UM script. Nada de passos manuais além desses dois.
4. Em Linux e macOS, o caminho declarativo é home-manager standalone com flakes.
   O nix gera o arquivo de settings do harness por inteiro — ele é dono do arquivo.
5. No Windows não há nix. O script faz um merge IDEMPOTENTE do fragmento de settings
   com o que já existe. Diga explicitamente, no README do repositório, que o caminho
   Windows é automação de instalação e NÃO reprodutibilidade: sem hash pinado, sem
   rollback.
6. Configuração pré-existente é preservada, nunca destruída. O arquivo de instruções
   globais gerado pelo repositório deve IMPORTAR o arquivo local que eu já tiver, e o
   script faz backup com timestamp de tudo que tocar antes de tocar.
7. O script é idempotente — rodar de novo depois de cada `git pull` não pode ter
   efeito colateral — e oferece `--uninstall` que restaura o backup.
8. Exatamente dois hooks, como exemplos que ensinam o formato:
   - PreToolUse que bloqueia escrita em um caminho proibido;
   - PostToolUse que formata ou linta o arquivo após uma edição.
9. Todo o conteúdo que você escrever — README, comentários, regras — em português do
   Brasil. Nomes de arquivos e diretórios em inglês, porque são impostos pelo harness.

FORA DO ESCOPO
Sem CI. Sem script de verificação ou doctor. Não os proponha.

AO FINAL
Depois que eu confirmar o desenho, construa tudo, crie o repositório privado e faça o
primeiro push. Termine listando as extensões naturais que ficaram de fora — CI com
`nix flake check`, pinagem de skills de terceiros por rev e hash, sincronização entre
máquinas — sem implementá-las.
```

---

## Variante 2 — para executar no **Codex**

```text
Use a skill de entrevista instalada em ~/.agents/skills/ para conduzir esta tarefa.
Não escreva um único arquivo antes de me entrevistar e antes de eu confirmar que
chegamos a um entendimento comum.

OBJETIVO
Criar um repositório GitHub PRIVADO que concentre os artefatos que direcionam o
trabalho dos agentes de IA na minha máquina, e que seja instalado por um `git clone`
seguido da execução de UM script. O repositório serve a UM harness, escolhido por mim
durante a entrevista, e não precisa guardar compatibilidade com nenhum outro.

Artefatos que o repositório deve conter, no mínimo:
- o arquivo de instruções globais do harness (AGENTS.md ou CLAUDE.md de nível usuário);
- skills;
- hooks;
- scripts.

O QUE VOCÊ DEVE ME PERGUNTAR
A arquitetura é minha decisão, não sua. Entreviste-me sobre ela livremente: como
organizar as pastas, o que é artefato e o que é gerador, quanto do meu contexto atual
migra para o repositório, o que fica de fora. Ofereça opções concretas com uma
recomendação sua em cada pergunta, e espere minha resposta antes de avançar.

Pergunte também, obrigatoriamente:
- qual harness o repositório vai governar (Codex ou Claude Code);
- qual o meu sistema operacional;
- quais artefatos eu já tenho hoje — pode ser nenhum;
- o conteúdo das regras globais que eu quero impor;
- no Windows, como quero declarar os pacotes a instalar (ofereça as opções
  apropriadas e me deixe escolher).

RESTRIÇÕES RECOMENDADAS
1. Repositório PRIVADO, criado por você com `gh repo create --private` ao final.
2. Nenhum segredo, token, chave ou credencial entra no repositório. Repositório
   privado é clonado para outras máquinas, entra em backup e vira público com um
   clique.
3. Instalação = `git clone` + UM script. Nada de passos manuais além desses dois.
4. Em Linux e macOS, o caminho declarativo é home-manager standalone com flakes.
   O nix gera o arquivo de configuração do harness por inteiro — ele é dono do arquivo.
5. No Windows não há nix. O script faz um merge IDEMPOTENTE do fragmento de
   configuração com o que já existe. Diga explicitamente, no README do repositório,
   que o caminho Windows é automação de instalação e NÃO reprodutibilidade: sem hash
   pinado, sem rollback.
6. Configuração pré-existente é preservada, nunca destruída. O arquivo de instruções
   globais gerado pelo repositório deve IMPORTAR o arquivo local que eu já tiver, e o
   script faz backup com timestamp de tudo que tocar antes de tocar.
7. O script é idempotente — rodar de novo depois de cada `git pull` não pode ter
   efeito colateral — e oferece `--uninstall` que restaura o backup.
8. Skills de usuário do Codex vão para `~/.agents/skills/<nome>/SKILL.md`. NÃO use
   `~/.codex/skills/`, que é reservado às skills embutidas (.system).
9. Exatamente dois hooks, como exemplos que ensinam o formato:
   - PreToolUse que bloqueia escrita em um caminho proibido;
   - PostToolUse que formata ou linta o arquivo após uma edição.
10. Todo o conteúdo que você escrever — README, comentários, regras — em português do
    Brasil. Nomes de arquivos e diretórios em inglês, porque são impostos pelo harness.

FORA DO ESCOPO
Sem CI. Sem script de verificação ou doctor. Não os proponha.

AO FINAL
Depois que eu confirmar o desenho, construa tudo, crie o repositório privado e faça o
primeiro push. Termine listando as extensões naturais que ficaram de fora — CI com
`nix flake check`, pinagem de skills de terceiros por rev e hash, sincronização entre
máquinas — sem implementá-las.
```

---

## Duas armadilhas que valem comentário em aula

**O arquivo de settings é estado compartilhado com o agente, não um dotfile seu.** Claude Code e Codex reescrevem a própria configuração em runtime — o Claude Code por temp-file + rename, o que *substitui um symlink por um arquivo comum*. É por isso que a restrição 4 entrega o arquivo inteiro ao nix em vez de symlinká-lo, e por isso que no Windows a saída é merge idempotente, não cópia.

**Symlink de entrada individual, nunca do diretório pai.** `~/.claude/skills/<nome>` apontando para o repositório é o formato suportado. Symlinkar `~/.claude/skills` inteiro já quebrou o carregamento de skills. E há diretórios que o harness limpa sozinho — caches, transcrições, snapshots —; apontar qualquer um deles para um repositório git significa perder arquivo.
