# Prompt: instalar Firstmate nativamente em outro host Windows

Instale o Firstmate (https://github.com/kunchenguid/firstmate) **nativamente neste Windows**, sem WSL.

Contexto importante: o upstream declara suporte só a macOS | Linux e não há nenhuma referência a Windows/MSYS nos ~116 scripts bash do repo. Mesmo assim ele funciona sob Git Bash, desde que duas condições não-óbvias sejam satisfeitas (itens 3 e 4 abaixo). Ambas falham em silêncio, e nenhuma delas é detectada pelo bootstrap do próprio Firstmate. Já validei esse caminho em outra máquina — siga os passos e valide cada um em vez de assumir.

Use o backend **herdr** (não tmux — tmux não existe nativamente no Windows).

## 1. Clonar

Clone em `C:\Projects\firstmate` (se já existir e estiver limpo, faça `git pull --ff-only` em vez de re-clonar).

## 2. Instalar dependências

Primeiro descubra o que já existe: `git`, `gh`, `node`, `npm`, `jq`, `python3`, `herdr`, `treehouse`, `no-mistakes`. Só instale o que faltar.

O conjunto exigido pelo backend herdr está no código, não no README:
- `bin/fm-backend.sh` → `fm_backend_required_tools()` → herdr precisa de `herdr jq treehouse`
- `bin/fm-bootstrap.sh` → `COMMON_TOOLS` → `node git gh no-mistakes gh-axi chrome-devtools-axi lavish-axi tasks-axi quota-axi`

Todos têm build para Windows. Métodos de instalação:

| Ferramenta | Como instalar no Windows |
|---|---|
| herdr | `irm https://herdr.dev/install.ps1 \| iex` (Windows é beta; precisa de protocolo 14+, ou seja 0.7.1+) |
| treehouse | `irm https://kunchenguid.github.io/treehouse/install.ps1 \| iex` (precisa suportar `treehouse get --lease`) |
| no-mistakes | veja o método Windows em https://kunchenguid.github.io/no-mistakes/start-here/installation/ — o `curl \| sh` do README é só mac/linux. Versão mínima **1.31.2** |
| jq | `winget install jqlang.jq` |
| git / gh / node | winget, se faltarem |
| os 5 pacotes `*-axi` | `npm install -g gh-axi chrome-devtools-axi lavish-axi tasks-axi quota-axi` (todos são `os=any`) |

Depois: rode `setup hooks` **apenas** em `gh-axi`, `chrome-devtools-axi` e `lavish-axi` (`tasks-axi` e `quota-axi` não têm esse passo). Avise o usuário que isso escreve na config global do Claude Code dele.

Garanta também `gh auth login` autenticado.

Instaladores adicionam ao PATH mas não à sessão atual — reexporte o PATH nos seus próprios comandos em vez de mandar o usuário reiniciar o terminal.

## 3. O primeiro bloqueador — symlinks

**Este é o passo que faz ou quebra a instalação, e o modo de falha é silencioso.**

Os locks do Firstmate são baseados em symlink, não em `mkdir`. Em `bin/fm-wake-lib.sh`, a função `fm_lock_try_create` faz `ln -s "$ownerdir" "$lockdir"` e valida o alvo do link; e `fm_lock_acquire_wait` é um `while ! fm_lock_try_acquire ...; do sleep 0.1; done`.

Consequência: sem symlink nativo, o `ln -s` do MSYS cria uma *cópia de diretório*, a validação falha, e o Firstmate **trava em loop infinito — sem erro, sem timeout, sem log**. Pior: `fm-bootstrap.sh` passa silencioso mesmo assim, porque só checa presença de ferramentas, nunca exercita um lock.

Para habilitar:

1. Teste primeiro — talvez já funcione:
   ```bash
   d=$(mktemp -d); cd "$d"; mkdir target
   MSYS=winsymlinks:nativestrict ln -s target link && [ -L link ] && echo OK || echo FALHOU
   ```
2. Se falhar com `Operation not permitted`, cheque o Developer Mode:
   ```powershell
   Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock'
   ```
   Se `AllowDevelopmentWithoutDevLicense` não for `1`, **peça ao usuário** para ativar — exige admin, você não consegue fazer sozinho. Ou pelas Configurações (Sistema → Para desenvolvedores → Modo de desenvolvedor), ou em PowerShell **como administrador**:
   ```powershell
   New-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock' `
     -Name AllowDevelopmentWithoutDevLicense -Value 1 -PropertyType DWord -Force
   ```
   Não precisa reiniciar — reteste o symlink logo depois.
3. Com o symlink funcionando, persista a variável:
   ```powershell
   [Environment]::SetEnvironmentVariable('MSYS','winsymlinks:nativestrict','User')
   ```

## 4. O segundo bloqueador — o shell dos panes do herdr

No Windows o herdr abre cada pane com o shell padrão do sistema (`%COMSPEC%`), que é o `cmd.exe`. O Firstmate inteiro é bash — os ~116 scripts, os hooks, o `bin/fm-session-start.sh` —, então um crewmate spawnado num pane `cmd.exe` não executa absolutamente nada. Isso é independente do item 3: dá para ter symlink nativo funcionando e ainda assim nenhum pane utilizável.

Aponte o herdr para o Git Bash no `config.toml` dele, em `%APPDATA%\herdr\config.toml` (sob Git Bash: `/c/Users/<usuario>/AppData/Roaming/herdr/config.toml`):

```toml
[terminal]
default_shell = "C:\\Program Files\\Git\\bin\\bash.exe"
```

Três detalhes que só aparecem na prática:

1. **É `bin\bash.exe`, não `usr\bin\bash.exe`.** O primeiro (~47 KB) é o wrapper que monta o ambiente MSYS; o segundo (~2,5 MB) é o bash cru e sobe sem o PATH esperado.
2. **`default_shell` aceita só nome ou caminho de executável, não linha de comando.** `"bash.exe -l"` ou `"C:\\Program Files\\Git\\bin\\bash.exe --login"` não funcionam. Escape as barras invertidas (`\\`) na string TOML.
3. **Não defina `shell_mode = "login"`.** No Windows isso dispara um fallback silencioso para `cmd.exe` e o `default_shell` acima é simplesmente ignorado (bug do herdr 0.7.x) — ou seja, a tentativa de "melhorar" a config desfaz a correção sem avisar. E é desnecessário: o `bin\bash.exe` do Git for Windows já monta o PATH do MSYS (`/usr/bin`, `/mingw64/bin`, coreutils) mesmo em shell não-login, ao contrário do macOS, onde é o login shell que faz esse setup.

Deixe um comentário no próprio `config.toml` registrando o item 3 — é o tipo de linha que alguém remove "limpando" a config e volta a quebrar tudo.

Depois de editar, recarregue e valide:

```bash
herdr server reload-config
herdr config check       # esperado: "config: ok"
```

`config: ok` só prova que o TOML é válido, **não** que o shell pegou; e panes já abertos mantêm o shell antigo, então valide num pane novo. A prova real é inspecionar o processo que segura o pane:

```bash
herdr pane current                        # pegue o pane_id, ex.: w1:p6
herdr pane process-info --pane <pane_id>  # devolve shell_pid
```

```powershell
Get-CimInstance Win32_Process -Filter "ProcessId = <shell_pid>" | Select-Object Name, CommandLine
```

Tem que voltar `bash.exe` com `CommandLine` igual a `"C:\Program Files\Git\bin\bash.exe"` (sem `-l`). Se voltar `cmd.exe`, uma das três armadilhas acima está ativa.

O binário do herdr fica em `%LOCALAPPDATA%\Programs\Herdr\bin` — reexporte esse caminho no PATH dos seus comandos, conforme o item 2.

## 5. Validar (não pule — instalar não é o mesmo que funcionar)

Rode tudo sob Git Bash, com `MSYS=winsymlinks:nativestrict` e o `treehouse` no PATH.

**a) Diagnóstico próprio do Firstmate.** Silêncio = tudo certo (é a semântica documentada no cabeçalho do script). Use detect-only para não mutar estado:
```bash
cd /c/Projects/firstmate
FM_BACKEND=herdr FM_BOOTSTRAP_DETECT_ONLY=1 bash bin/fm-bootstrap.sh
```
Qualquer linha `MISSING:` / `NEEDS_GH_AUTH` indica dependência pendente.

**b) Ciclo de lock real** — a prova de que o item 3 pegou. Faça sourcing de `bin/fm-wake-lib.sh` e exercite `fm_lock_try_acquire` → segunda tentativa deve ser **recusada** → `fm_lock_release` → readquirir deve funcionar. Se travar, o symlink não está ativo.

**c) Suíte de testes.** Os fixtures assumem `git` em `/usr/bin`, o que é falso no Git Bash (fica em `/mingw64/bin`). Sem corrigir, testes falham por motivo errado. Existe um override:
```bash
FM_TEST_BASE_PATH="/usr/bin:/bin:/usr/sbin:/sbin:/mingw64/bin" bash tests/fm-bootstrap.test.sh
```
Rode também `tests/fm-backend-herdr.test.sh`, `tests/fm-crew-state.test.sh`, `tests/fm-brief.test.sh`. Espere a grande maioria passando; os arquivos param no primeiro erro. Não persiga falhas de asserção de fixture — distinga isso de incompatibilidade real de plataforma antes de tentar consertar qualquer coisa.

## 6. Reporte no final

- O que já existia vs. o que você instalou, com versões
- Resultado de cada validação, com números reais de testes (não "passou")
- O que você **não** verificou. Em particular: um spawn end-to-end (worktree via treehouse + pane no herdr + crewmate de verdade) cria estado real — **pergunte antes** de fazer, não faça por conta

Ressalvas conhecidas a repassar ao usuário: `lsof` não existe no Git Bash, então `bin/fm-lock-lib.sh` nunca consegue provar que um lock foi abandonado (falha em modo seguro — trava em vez de corromper); o Windows do herdr é beta; o `config.toml` do item 4 vive fora do repositório, então nenhum `git pull` o protege e um `herdr update` pode reescrevê-lo — se os panes voltarem a subir em `cmd.exe`, reconfira o `default_shell` antes de investigar qualquer outra coisa; e como o upstream não testa Windows, um `git pull` futuro pode quebrar esse caminho sem aviso.
