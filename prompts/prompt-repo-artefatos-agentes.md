# Construindo um repositório de artefatos para agentes de IA

Material de apoio do **exercício ia-4.3**. Dois prompts, um por harness de execução. Escolha o da ferramenta que você tem instalada, cole na íntegra e responda à entrevista.

Os dois prompts levam ao mesmo destino: **um** repositório GitHub privado que governa globalmente o comportamento do seu agente, instalado por `git clone` seguido de **um** script. A arquitetura de dentro do repositório é sua — o agente vai entrevistá-lo para descobri-la, não para lhe entregar um template pronto.

**O script também é do agente, não do enunciado.** Nenhuma das duas variantes diz em que linguagem escrevê-lo, nem com que mecanismo declarar os pacotes: quem decide é o agente, olhando a máquina em que ele está rodando — e ele tem que defender a escolha na entrevista antes de escrever a primeira linha. Um prompt que já chegasse com `install.ps1` e `winget import` decididos transformaria em digitação o único lugar em que o exercício obriga alguém a projetar.

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
- o conteúdo das regras globais que eu quero impor.

RESTRIÇÕES RECOMENDADAS
1. Repositório PRIVADO, criado por você com `gh repo create --private` ao final.
2. Nenhum segredo, token, chave ou credencial entra no repositório. Repositório
   privado é clonado para outras máquinas, entra em backup e vira público com um
   clique.
3. Instalação = `git clone` + UM script. Nada de passos manuais além desses dois.
4. O SCRIPT É SEU PROBLEMA, NÃO MEU. Antes de escrevê-lo, inspecione esta máquina —
   sistema operacional, shell, gerenciadores de pacote já instalados, o que existe
   hoje no diretório de configuração do harness — e decida por conta própria a
   linguagem do script, o mecanismo de instalação e a forma de declarar os pacotes
   que ele instala. Depois me apresente a decisão com o porquê, as alternativas que
   você descartou e o que essa escolha NÃO entrega, e espere eu concordar ou
   discordar. No README, diga em uma frase o que o caminho escolhido dá e o que ele
   não dá: se não houver versão pinada nem rollback, ele é automação de instalação e
   NÃO reprodutibilidade — escreva isso com essas palavras.
5. Skills entram por LINK POR ENTRADA: `~/.claude/skills/<nome>` aponta para o
   diretório correspondente dentro do repositório (symlink, ou junction no Windows,
   que não exige privilégio de administrador). Nunca aponte o diretório PAI
   (`~/.claude/skills` inteiro) para o repositório, e nunca aponte para dentro dele
   um diretório que o harness limpa sozinho — cache, transcrição, snapshot. Se o
   sistema recusar links, caia para cópia e me diga que caiu.
6. Do meu setup atual, a única coisa que migra é o arquivo de instruções globais. As
   skills, os hooks e os scripts do repositório são novos, escritos por você como
   exemplos que ensinam o formato.
7. Configuração pré-existente é preservada, nunca destruída. O arquivo de instruções
   globais gerado pelo repositório deve IMPORTAR o arquivo local que eu já tiver, e o
   script faz backup com timestamp de tudo que tocar antes de tocar.
8. O script é idempotente — rodar de novo depois de cada `git pull` não pode ter
   efeito colateral — e oferece `--uninstall` que restaura o backup.
9. Exatamente dois hooks, como exemplos que ensinam o formato:
   - PreToolUse que bloqueia escrita em um caminho proibido;
   - PostToolUse que formata ou linta o arquivo após uma edição.
10. Todo o conteúdo que você escrever — README, comentários, regras — em português do
    Brasil. Nomes de arquivos e diretórios em inglês, porque são impostos pelo harness.

FORA DO ESCOPO
Sem CI. Sem script de verificação ou doctor. Não os proponha.

AO FINAL
Depois que eu confirmar o desenho, construa tudo, crie o repositório privado e faça o
primeiro push. Em seguida, ainda na raiz do repositório, produza os dois arquivos de
entrega do exercício:

- ENTREVISTA.md — o registro da entrevista: cada pergunta que você me fez, a
  recomendação que veio junto e a minha resposta. Marque explicitamente as DUAS
  decisões em que eu contrariei a sua recomendação, com o que você recomendou, o que
  eu escolhi e o motivo que eu dei.
- evidencia-instalacao.txt — a saída bruta de três execuções seguidas, uma por bloco,
  cada uma precedida da linha de comando que a gerou: o script (primeira vez), o
  script de novo (segunda vez, que não pode ter efeito colateral) e o script com
  --uninstall restaurando o backup.

Termine listando as extensões naturais que ficaram de fora — CI, pinagem de skills de
terceiros por rev e hash, sincronização entre máquinas — sem implementá-las.
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
- o conteúdo das regras globais que eu quero impor.

RESTRIÇÕES RECOMENDADAS
1. Repositório PRIVADO, criado por você com `gh repo create --private` ao final.
2. Nenhum segredo, token, chave ou credencial entra no repositório. Repositório
   privado é clonado para outras máquinas, entra em backup e vira público com um
   clique.
3. Instalação = `git clone` + UM script. Nada de passos manuais além desses dois.
4. O SCRIPT É SEU PROBLEMA, NÃO MEU. Antes de escrevê-lo, inspecione esta máquina —
   sistema operacional, shell, gerenciadores de pacote já instalados, o que existe
   hoje no diretório de configuração do harness — e decida por conta própria a
   linguagem do script, o mecanismo de instalação e a forma de declarar os pacotes
   que ele instala. Depois me apresente a decisão com o porquê, as alternativas que
   você descartou e o que essa escolha NÃO entrega, e espere eu concordar ou
   discordar. No README, diga em uma frase o que o caminho escolhido dá e o que ele
   não dá: se não houver versão pinada nem rollback, ele é automação de instalação e
   NÃO reprodutibilidade — escreva isso com essas palavras.
5. Skills de usuário do Codex vão para `~/.agents/skills/<nome>/SKILL.md`, e entram
   por LINK POR ENTRADA: `~/.agents/skills/<nome>` aponta para o diretório
   correspondente dentro do repositório (symlink, ou junction no Windows, que não
   exige privilégio de administrador). Nunca aponte o diretório PAI
   (`~/.agents/skills` inteiro) para o repositório. NÃO use `~/.codex/skills/`, que é
   reservado às skills embutidas (.system). Se o sistema recusar links, caia para
   cópia e me diga que caiu.
6. Do meu setup atual, a única coisa que migra é o arquivo de instruções globais. As
   skills, os hooks e os scripts do repositório são novos, escritos por você como
   exemplos que ensinam o formato.
7. Configuração pré-existente é preservada, nunca destruída. O arquivo de instruções
   globais gerado pelo repositório deve IMPORTAR o arquivo local que eu já tiver, e o
   script faz backup com timestamp de tudo que tocar antes de tocar.
8. O script é idempotente — rodar de novo depois de cada `git pull` não pode ter
   efeito colateral — e oferece `--uninstall` que restaura o backup.
9. Exatamente dois hooks, como exemplos que ensinam o formato:
   - PreToolUse que bloqueia escrita em um caminho proibido;
   - PostToolUse que formata ou linta o arquivo após uma edição.
10. Todo o conteúdo que você escrever — README, comentários, regras — em português do
    Brasil. Nomes de arquivos e diretórios em inglês, porque são impostos pelo harness.

FORA DO ESCOPO
Sem CI. Sem script de verificação ou doctor. Não os proponha.

AO FINAL
Depois que eu confirmar o desenho, construa tudo, crie o repositório privado e faça o
primeiro push. Em seguida, ainda na raiz do repositório, produza os dois arquivos de
entrega do exercício:

- ENTREVISTA.md — o registro da entrevista: cada pergunta que você me fez, a
  recomendação que veio junto e a minha resposta. Marque explicitamente as DUAS
  decisões em que eu contrariei a sua recomendação, com o que você recomendou, o que
  eu escolhi e o motivo que eu dei.
- evidencia-instalacao.txt — a saída bruta de três execuções seguidas, uma por bloco,
  cada uma precedida da linha de comando que a gerou: o script (primeira vez), o
  script de novo (segunda vez, que não pode ter efeito colateral) e o script com
  --uninstall restaurando o backup.

Termine listando as extensões naturais que ficaram de fora — CI, pinagem de skills de
terceiros por rev e hash, sincronização entre máquinas — sem implementá-las.
```

---

## Três armadilhas que valem comentário em aula

**O arquivo de settings é estado compartilhado com o agente, não um dotfile seu.** Claude Code e Codex reescrevem a própria configuração em runtime — o Claude Code por temp-file + rename, o que *substitui um symlink por um arquivo comum*. Symlinkar o settings para o repositório sobrevive até a primeira vez que o agente mexe nele: dali em diante o link virou arquivo, o repositório ficou para trás e ninguém foi avisado. É por isso que a saída para o settings é **merge idempotente**, não link e não cópia — e é exatamente essa a pergunta de fechamento do exercício.

**Symlink de entrada individual, nunca do diretório pai.** `~/.claude/skills/<nome>` apontando para o repositório é o formato suportado. Symlinkar `~/.claude/skills` inteiro já quebrou o carregamento de skills. E há diretórios que o harness limpa sozinho — caches, transcrições, snapshots —; apontar qualquer um deles para um repositório git significa perder arquivo.

**Automação de instalação não é reprodutibilidade, e o README tem que dizer qual das duas ele entrega.** Um script que chama o gerenciador de pacotes da máquina instala a versão que estiver no repositório do gerenciador naquele dia: sem hash pinado e sem rollback, duas máquinas instaladas com uma semana de diferença não ficam iguais. Isso não desqualifica o script — desqualifica chamá-lo de reprodutível. Os caminhos declarativos de verdade (nix com flakes, por exemplo) existem, custam mais, e a decisão de pagar ou não esse preço é do aluno; o que o exercício cobra é que a escolha esteja escrita.
