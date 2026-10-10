# Coding agent 沙箱：Claude Code 與 Codex

> 查證日期：2026-10-10。WSL、Claude Code、Codex 的文件都改得很快，請以官方最新說明為準。本頁沒有實測任何沙箱行為：寫「預期」的地方都出自官方文件，沒有官方句子撐的地方標「推論」。

[上一頁](wsl2-isolation.md)把 WSL2 調成一個實驗場。這頁講 agent 自己的沙箱：Claude Code 的 `/sandbox` 和 Codex 的 sandbox mode。兩者在 WSL2 裡都靠 bubblewrap 做隔離，但擋的東西不完全一樣。最後把 WSL2 和 agent 沙箱疊起來，逐項看每一層擋什麼、不擋什麼。

Claude Code 的 permission rules 與 permission modes 怎麼寫，見[Claude Code 設定總覽](official-config.md)第四節；Codex 三種 sandbox mode 的基本定義，見[AI Agent 怎麼運作](agent-basics.md)第三節。這頁不重講。

<style>
.wsx-panel { background: var(--panel); border: 1px solid var(--rule); border-radius: 10px; padding: 1rem 1.1rem; margin: 1.2rem 0 1.6rem; }
.wsx-panel-title { font-weight: 700; margin: 0 0 .6rem; color: var(--accent-ink); }
.wsx-q { border: 0; margin: 0 0 .9rem; padding: 0; min-width: 0; }
.wsx-q legend { font-weight: 600; padding: 0; margin-bottom: .35rem; }
.wsx-choices { display: flex; flex-wrap: wrap; gap: .45rem; }
.wsx-choices label { display: inline-flex; align-items: center; gap: .4rem; border: 1px solid var(--rule); border-radius: 999px; padding: .2rem .75rem; cursor: pointer; background: var(--bg); line-height: 1.5; }
.wsx-choices input { accent-color: var(--accent); margin: 0; }
.wsx-choices label:has(input:checked) { border-color: var(--accent); background: var(--accent-soft); color: var(--accent-ink); }
.wsx-result { border-top: 1px solid var(--rule-soft); margin-top: .4rem; padding-top: .7rem; }
.wsx-result h4 { margin: .7rem 0 .3rem; font-size: .95rem; }
.wsx-result ul { margin: 0; padding-left: 1.2rem; }
.wsx-result li { margin: .3rem 0; }
.wsx-tag { display: inline-block; font-size: .75rem; padding: 0 .45rem; border-radius: 999px; border: 1px solid var(--warn-rule); color: var(--warn-ink); margin-left: .3rem; white-space: nowrap; }
.wsx-quiz-item { border: 1px solid var(--rule); border-radius: 10px; padding: .8rem 1rem; margin: .8rem 0; background: var(--bg); }
.wsx-quiz-item p { margin: 0 0 .5rem; }
.wsx-quiz-ctx { font-size: .85rem; color: var(--ink-faint); }
.wsx-btns { display: flex; flex-wrap: wrap; gap: .45rem; }
.wsx-btns button { font: inherit; font-size: .9rem; padding: .3rem .9rem; border-radius: 6px; border: 1px solid var(--rule); background: var(--panel); color: var(--ink); cursor: pointer; }
.wsx-btns button:hover, .wsx-btns button:focus-visible { border-color: var(--accent); }
.wsx-btns button[aria-pressed="true"] { border-color: var(--accent); background: var(--accent-soft); color: var(--accent-ink); }
.wsx-feedback { margin-top: .6rem; padding: .55rem .75rem; border-radius: 8px; font-size: .93rem; }
.wsx-feedback.wsx-ok { background: var(--ok-bg); border: 1px solid var(--ok-rule); }
.wsx-feedback.wsx-no { background: var(--warn-bg); border: 1px solid var(--warn-rule); }
.wsx-feedback b { display: block; margin-bottom: .2rem; }
.wsx-score { font-weight: 600; margin: .4rem 0 0; }
.wsx-reset { font: inherit; font-size: .85rem; margin-top: .5rem; padding: .25rem .8rem; border-radius: 6px; border: 1px solid var(--rule); background: var(--panel); color: var(--ink-soft); cursor: pointer; }
.doc pre.wsx-pre { position: relative; padding-top: 2.1rem; }
.wsx-copy { position: absolute; top: .4rem; right: .45rem; font: inherit; font-size: .75rem; line-height: 1.2; padding: .25rem .6rem; border: 1px solid var(--rule); border-radius: 6px; background: var(--panel); color: var(--ink-soft); cursor: pointer; }
.wsx-copy:hover, .wsx-copy:focus-visible { border-color: var(--accent); color: var(--accent-ink); }
</style>

## 一、先選要疊幾層

回答四個問題，下面會列出建議的組合。每一條後面的編號對到本頁最後的出處表；標「推論」的是官方沒有直接寫、本站依官方文件推出來的。

<div class="wsx-panel" id="wsx-picker">
<p class="wsx-panel-title">我的情況該用哪一層</p>
<fieldset class="wsx-q"><legend>1. 你在哪裡跑 agent？</legend><div class="wsx-choices">
<label><input type="radio" name="wsx-env" value="win" checked>Windows 原生（PowerShell）</label>
<label><input type="radio" name="wsx-env" value="wsl">WSL2</label>
</div></fieldset>
<fieldset class="wsx-q"><legend>2. 用哪個工具？</legend><div class="wsx-choices">
<label><input type="radio" name="wsx-tool" value="claude" checked>Claude Code</label>
<label><input type="radio" name="wsx-tool" value="codex">Codex</label>
<label><input type="radio" name="wsx-tool" value="both">兩個都用</label>
</div></fieldset>
<fieldset class="wsx-q"><legend>3. 想放手到什麼程度？</legend><div class="wsx-choices">
<label><input type="radio" name="wsx-free" value="ask">每個指令都先問我</label>
<label><input type="radio" name="wsx-free" value="box" checked>沙箱裡自動做，出界才問</label>
<label><input type="radio" name="wsx-free" value="none">完全不問</label>
</div></fieldset>
<fieldset class="wsx-q"><legend>4. 專案從哪裡來？</legend><div class="wsx-choices">
<label><input type="radio" name="wsx-repo" value="own" checked>自己的或信得過的</label>
<label><input type="radio" name="wsx-repo" value="untrusted">來路不明的 repo</label>
</div></fieldset>
<div class="wsx-result" id="wsx-pick-out" aria-live="polite"></div>
</div>

## 二、Claude Code 的 `/sandbox`

`/sandbox` 是作業系統在 Claude 執行的 shell 指令外面加的一道邊界，限制的是 Bash、PowerShell、Monitor 指令和它們啟動的子程序[1]。它支援 macOS、Linux 與 WSL2；官方原文：「On native Windows, Claude Code runs commands unsandboxed. To use the sandbox on a Windows machine, run Claude Code inside a WSL2 distribution.」[1] 沙箱預設是關的，要在 session 裡跑 `/sandbox`，或在設定檔把 `sandbox.enabled` 設成 `true`[1]。

### 擋什麼、不擋什麼

開啟後的預設範圍[1]：

| 存取 | 預設 | 用什麼改 |
|---|---|---|
| 寫入 | 工作目錄、每位使用者的暫存目錄、你額外加入的目錄；受保護路徑仍禁止寫入 | `filesystem.allowWrite`、`filesystem.denyWrite` |
| 讀取 | 「Most of the machine」，連 `~/.ssh`、`~/.aws/credentials` 這類憑證檔也讀得到 | `filesystem.denyRead`、`credentials` |
| 網路 | 沒有直接對外的路由，連線一律經過本機的 proxy，逐一比對允許的網域；允許清單一開始是空的 | `network.allowedDomains`、`network.deniedDomains` |
| 環境變數 | 從 Claude Code 繼承，包含裡面的密鑰 | `credentials` |

下面這些**不在**沙箱裡[1]：

- Claude 內建的 Read、Edit、Write、WebFetch、WebSearch 工具，改由 permission rules 管。官方特別提醒：「A `denyRead` entry doesn't stop the Read tool, and `allowedDomains` doesn't limit WebFetch」。
- Claude Code 啟動的其他程序：hooks、本機 MCP server、plugin monitor、LSP server、status line 指令等，官方寫它們「run with your full access」。
- 你自己在 `!` 提示字元打的指令（多數 session 不在沙箱內）、符合 `excludedCommands` 的指令，以及 Claude 在沙箱失敗後要求「不經沙箱重跑」並獲准的指令。

想把這些也關進同一道邊界，官方的做法是把整個 Claude Code 程序放進容器、虛擬機，或用 sandbox runtime 包起來[1][2]。

### 在 WSL2 安裝

Linux 和 WSL2 上，沙箱靠 `bubblewrap`（負責檔案系統隔離）和 `socat`（把網路導向沙箱的 proxy）[1]：

```bash
sudo apt-get install bubblewrap socat
```

Ubuntu 24.04 以後，預設的 AppArmor 政策會擋住 bubblewrap 建立需要的 user namespace。WSL2 裡也可能如此，官方說檢查方式「including inside WSL2」都一樣，先檢查[1]：

```bash
sysctl kernel.apparmor_restrict_unprivileged_userns
```

回傳 `0`，或顯示 `No such file or directory`，就跳過這步。回傳 `1` 的話，照官方步驟加一個只給 `bwrap` 用的 AppArmor profile，再重新載入[1]：

```bash
sudo tee /etc/apparmor.d/bwrap > /dev/null <<'EOF'
abi <abi/4.0>,
include <tunables/global>

profile bwrap /usr/bin/bwrap flags=(unconfined) {
  userns,
  include if exists <local/bwrap>
}
EOF
sudo systemctl reload apparmor
```

**WSL2 上要特別裝 seccomp filter。** 官方說明 WSL2 啟動 Windows 程式（`cmd.exe`、`powershell.exe`、`/mnt/c/` 底下的任何程式）是透過一個 Unix socket 交給 Windows 主機，所以沙箱裡的指令能不能啟動 Windows 程式，取決於沙箱的 Unix socket 設定，而且「the optional seccomp filter has to be installed to block the socket in the first place」[1]。設定參考頁也寫：filter 不在的時候，沙箱不擋 Unix socket 呼叫[4]。seccomp filter 用 npm 安裝（要先有 npm）[1]：

```bash
npm install -g @anthropic-ai/sandbox-runtime
```

依賴檢查在 Claude Code 啟動時執行，裝完要重開 Claude Code。之後跑 `/sandbox`：缺必要套件時面板只會出現 Dependencies 分頁；只缺 seccomp filter 時，Dependencies 分頁會跟其他分頁並列[1]。看不到 Dependencies 分頁，就代表依賴都齊了[1]。

Claude Code 本身要裝在 WSL 裡：官方寫「You install and launch `claude` inside the WSL terminal, not from PowerShell or CMD.」[3]

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

### WSL1 與原生 Windows

| 環境 | `/sandbox` | 出處 |
|---|---|---|
| WSL2 | 支援，用 bubblewrap，跟 Linux 一樣 | [1][3] |
| WSL1 | 不支援。看到 `Sandboxing requires WSL2` 就是在 WSL1，官方建議升級到 WSL2，或不用沙箱 | [1][3] |
| 原生 Windows | 不支援，指令不經沙箱執行 | [1][3] |

另外，沙箱因為缺套件或平台不支援而起不來時，Claude Code 會**照常執行指令、不加沙箱**。要它直接拒絕啟動，設 `sandbox.failIfUnavailable: true`[1]。

### 檔案系統與網路白名單怎麼設

`/sandbox` 選的模式存在專案的 `.claude/settings.local.json`；要每個專案都開，在 `~/.claude/settings.json` 設 `sandbox.enabled`[1]。下面是一份給 WSL2 實驗 distro 用的使用者層設定範例，每個鍵都出自官方文件，網域請換成你真的需要的：

```json
{
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false,
    "network": {
      "allowedDomains": ["github.com", "registry.npmjs.org"]
    },
    "credentials": {
      "files": [
        { "path": "~/.ssh", "mode": "deny" }
      ],
      "envVars": [
        { "name": "GITHUB_TOKEN", "mode": "deny" }
      ]
    }
  },
  "permissions": {
    "blockReadsOutsideWorkingDirectories": true
  }
}
```

逐項說明：

- `failIfUnavailable`：沙箱起不來就拒絕啟動，而不是默默不加沙箱[1]。
- `allowUnsandboxedCommands: false`：關掉「沙箱裡失敗就要求在沙箱外重跑」這個出口，官方稱為 Strict sandbox mode[1]。
- `allowedDomains`：允許的網域。官方提醒放太寬的網域（例如整個 `github.com`）可能變成資料外流的管道[1]。
- `credentials`：沒有內建的憑證黑名單，只有你列出來的檔案和環境變數會被擋[1]。`deny` 的檔案在沙箱裡讀不到，環境變數會在每個沙箱指令執行前清掉[1]。
- `blockReadsOutsideWorkingDirectories`：讓 Claude 的檔案工具拒絕讀工作目錄以外的檔案；開沙箱時，沙箱指令也讀不到家目錄與 `/Users`、`/home`、`/root`、`/Volumes`、`/mnt`、`/media`、`/run/media`、`/srv` 這些放使用者檔案的位置，再把工作目錄等必要路徑打開。需要 Claude Code v2.1.257 以上[4]。在 WSL2 裡，這會讓沙箱指令讀不到 `/mnt/c`。

讀取規則重疊時，範圍比較窄的那條優先，例如 `denyRead: ["~/"]` 加上 `allowRead: ["~/projects"]`，只有 `~/projects` 讀得到[1]。

### 跟 permission rules 的分工

官方的分法是[1]：permission rules 管「Claude Code 能不能用某個工具」，在工具執行**之前**依指令文字判斷，適用所有工具；沙箱是作業系統對**正在執行**的程序加的邊界，「so it holds regardless of what the model chose to run」，但只管 shell 指令。兩邊的路徑與網域設定最後會合併成同一份沙箱設定[1]。另外，`/sandbox` 不是 permission mode[1]。

沙箱有兩種模式，檔案與網路限制完全相同，差別只在要不要問你[1]：

- **auto-allow**：在沙箱裡跑的指令不問就執行。明確的 deny 規則、像 `Bash(git push *)` 這類有內容的 ask 規則，仍然有效[1]。
- **regular permissions**：每個指令照常走權限流程，即使在沙箱裡[1]。

官方的 permission mode 頁把「Manual 模式加上 Bash 沙箱的 auto-allow」列為想少一點確認、又不想用分類器時的常見組合[5]。

### 裝完怎麼確認

官方的驗證方法是**請 Claude 執行**下面兩行。你自己在 `!` 打的指令通常不在沙箱裡，自己打測不出來[1]：

| 請 Claude 執行 | 沙箱有效時的預期（Linux／WSL2） |
|---|---|
| `touch ~/sandbox-probe` | 失敗，顯示 `Read-only file system` |
| `curl --noproxy '*' https://example.com` | 失敗，顯示 `Could not resolve host` |

如果 Claude 問要不要在沙箱外重跑，拒絕。如果 `touch` 成功了，而且家目錄不在可寫範圍裡，刪掉 `~/sandbox-probe`，再跑 `/sandbox` 檢查沙箱有沒有開、依賴有沒有裝齊[1]。

WSL2 的 interop 通道，官方沒有給驗證指令。依上面 seccomp filter 的說明推得：裝了 filter、又沒有設 `allowAllUnixSockets` 時，請 Claude 跑 `cmd.exe /c ver` 應該啟動不了（推論，錯誤訊息官方沒寫）。

## 三、Codex 的沙箱

Codex 的沙箱也套用在它啟動的指令上：它跑 `git`、套件管理工具、測試時，這些指令都在同一道邊界裡[6]。

### 三種模式之外要知道的事

`read-only`、`workspace-write`、`danger-full-access` 的定義見[AI Agent 怎麼運作](agent-basics.md)第三節。這裡補幾項跟隔離直接有關的事實：

- 網路預設關閉。官方原文：「By default, the agent runs with network access turned off.」`workspace-write` 要開網路，得在設定裡寫 `[sandbox_workspace_write] network_access = true`[7]。
- 工作區包含暫存目錄。官方：「The workspace includes the current directory and temporary directories like `/tmp`.」用 `/status` 可以看目前工作區有哪些目錄[7]。
- 工作區裡也有唯讀的地方：`workspace-write` 下，可寫目錄底下的 `.git`、`.agents`、`.codex` 是唯讀的，而且往下全部唯讀[7]。
- 要多寫一個目錄，用 `sandbox_workspace_write.writable_roots` 擴充，不必整個拿掉沙箱[6]。
- `--yolo` 是 `--dangerously-bypass-approvals-and-sandbox` 的別名，官方標註「No sandbox; no approvals (not recommended)」[7]。官方舉的使用情境是 Docker 這類容器裡 Linux 沙箱跑不起來，先由容器提供隔離再這樣跑；但也警告容器裡的東西（包括 Codex 的憑證）可能被惡意專案帶走，原文：「Use this pattern only with trusted repositories」[7]。
- Auto 等於 `--sandbox workspace-write --ask-for-approval on-request`，官方標示不加旗標就是這個預設：工作區內自動做，要寫工作區外或要連網會先問你[7]。官方也寫，Codex 會依資料夾是否受版控、是否已信任，可能先以 `read-only` 啟動[7]，細節見[Claude Code + Codex 協作](claude-codex.md)。

### 各平台用什麼機制

| 平台 | 機制 | 出處 |
|---|---|---|
| macOS | Seatbelt | [7] |
| Linux | 預設 `bwrap` 加 `seccomp` | [7] |
| WSL2 | 用 Linux 的沙箱實作 | [6][7][9] |
| WSL1 | Codex 0.114 以前支援；0.115 起 Linux 沙箱改用 bubblewrap，不再支援 WSL1 | [7][9] |
| 原生 Windows（PowerShell） | 原生 Windows 沙箱，有三種實作：`mxc`（建議，不需要管理員核准的設定）、`elevated`（舊版備案，需要管理員核准的設定，沙箱裡的指令不以管理員權限執行）、`unelevated`（舊版備案，網路隔離比 `elevated` 弱，不支援禁止讀取的路徑） | [8] |

MXC 需要 Windows 11 24H2（build 26100.9278）或 25H2（build 26200.9278）起提供的原生能力[8]。官方對原生 Windows 的建議是：「Use the native Windows sandbox by default. Choose WSL when you need Linux-native tooling, your workflow already lives in WSL2, or the available native Windows implementations don't meet your needs.」[8]

### 在 WSL2 安裝

先裝 bubblewrap[6]：

```bash
sudo apt install bubblewrap
```

Codex 用 `PATH` 上找到的第一個 `bwrap`；找不到時改用內附的 helper，但那個 helper 需要系統允許一般使用者建立 user namespace。`bwrap` 不在、或 helper 建不了 namespace 時，Codex 啟動會顯示警告[6]。Ubuntu 24.04 裝了 bubblewrap 之後仍可能出現這個警告，官方給的處理是載入 `bwrap-userns-restrict` profile[6]：

```bash
sudo apt update
sudo apt install apparmor-profiles apparmor-utils
sudo install -m 0644 \
  /usr/share/apparmor/extra-profiles/bwrap-userns-restrict \
  /etc/apparmor.d/bwrap-userns-restrict
sudo apparmor_parser -r /etc/apparmor.d/bwrap-userns-restrict
```

再安裝 Codex[9]：

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

### 裝完怎麼確認

官方提供直接在 Codex 沙箱裡跑一條指令的測試入口[7]：

```bash
codex sandbox linux [--permissions-profile <name>] [COMMAND]...
```

官方沒寫不加 `--permissions-profile` 時套用哪一份設定，所以測出來的結果要對照你自己的設定看。也可以在一般的 Codex session 裡請它跑 `touch ~/codex-probe`（工作區設在專案目錄時）和 `curl https://example.com`：依官方寫的預設（寫入限工作區、網路關閉），兩者都應該做不到或先問你（推論，本站沒有實測）[7]。

### Codex 的讀取範圍

官方寫 `workspace-write` 下 agent「can read files」[6]，沒有逐字寫出預設讀取範圍。目前還在 beta 的 permission profile 文件裡，要拒絕讀取工作區以外的檔案，範例是另外加 `":root" = "deny"`[10]。本站據此推論：預設設定下，Codex 讀得到工作區以外的檔案；在 WSL2 裡，這可能包含 `/mnt/c`（推論）。要避開，最直接的做法是上一頁的關閉自動掛載。

## 四、疊起來：各層擋什麼、不擋什麼

「實驗 distro」指上一頁關掉自動掛載與 interop 的 distro；Claude 欄指開了 `/sandbox` 的預設值；Codex 欄指 `workspace-write` 的預設值。

| 情境 | WSL2 實驗 distro | Claude `/sandbox` | Codex `workspace-write` |
|---|---|---|---|
| 讀 Windows 檔案（`/mnt/c`） | 擋：不自動掛載，但有 root 權限仍可手動掛載[11] | 預設不擋（讀取範圍是「大部分機器」）；開 `blockReadsOutsideWorkingDirectories` 就擋 `/mnt`[1][4] | 官方沒寫預設讀取範圍；beta 的 permission profile 可以拒讀[10] |
| 寫工作區以外的地方 | 不管 Linux 內部的寫入 | 擋：只能寫工作目錄、暫存目錄、加入的目錄[1] | 擋：寫入限工作區（含 `/tmp` 這類暫存目錄）[7] |
| 從 Linux 啟動 Windows 程式 | 擋：`[interop] enabled=false`[11] | 裝了 seccomp filter 才擋；`allowAllUnixSockets: true` 會重新打開[1][4] | 官方沒寫 |
| 對外連網 | 不擋（`networkingMode=none` 會讓所有 WSL2 distro 斷網[11]） | 擋：只能經 proxy，允許清單一開始是空的[1] | 擋：網路預設關閉[7] |
| 讀 `~/.ssh` 這類憑證 | 新匯入的乾淨 distro 裡本來就沒有你的金鑰（前提是來源 distro 乾淨） | 不擋，要自己在 `credentials` 列出來[1] | 官方沒寫 |
| 改 agent 自己的設定、`.git` | 不管 | 擋：`.claude` 設定檔與 `.claude/hooks` 等目錄、`.mcp.json`、工作目錄裡 `.git` 的 `hooks` 與 `config` 等是受保護路徑[1] | 擋：`.git`、`.agents`、`.codex` 唯讀[7] |
| agent 的檔案工具、hooks、MCP server | 這些程序跑在 distro 裡，看不到沒掛載的 C 槽（推論） | 不擋：這些不在沙箱裡[1] | 官方沒寫逐項清單 |

WSL2 這層擋的是「通往 Windows 的路」，agent 沙箱擋的是「這個 distro 裡的寫入與網路」。只有 WSL2 這層，agent 在 distro 裡可以隨意改檔案、上網；只有 agent 沙箱、WSL2 用預設設定，Claude 的 Read 工具、hooks、MCP server，以及沒裝 seccomp filter 時的 Windows 程式，都還碰得到 Windows（推論，依[1][11][12]）。

## 五、情境測驗：這個動作會不會被擋

每題選一個答案，會立刻顯示解釋和出處。題目裡的 `<你>` 代表你的 Windows 使用者名稱。「會被擋」包含「先停下來問你、你沒同意就不做」；「不會被擋」指不問就直接做到。

<div class="wsx-panel" id="wsx-quiz">
<p class="wsx-panel-title">會不會被擋？</p>
<div id="wsx-quiz-list"></div>
<p class="wsx-score" id="wsx-quiz-score" aria-live="polite"></p>
<button type="button" class="wsx-reset" id="wsx-quiz-reset">重新作答</button>
</div>

## 六、從安裝到驗證：勾選清單

先完成[上一頁](wsl2-isolation.md)的清單，再接著做這份。勾選狀態只存在這台裝置的這個瀏覽器。

- [ ] 在實驗 distro 裝 `bubblewrap` 和 `socat`
- [ ] Ubuntu 24.04 以後：檢查 `kernel.apparmor_restrict_unprivileged_userns`，需要時加 AppArmor profile
- [ ] 在 WSL 裡安裝 Claude Code（不是在 PowerShell）
- [ ] `npm install -g @anthropic-ai/sandbox-runtime` 裝 seccomp filter
- [ ] 重開 Claude Code，跑 `/sandbox`，確認沒有 Dependencies 分頁，選好模式
- [ ] 在 `~/.claude/settings.json` 加上 `failIfUnavailable`、`allowUnsandboxedCommands: false`、網域白名單、`credentials`、`blockReadsOutsideWorkingDirectories`
- [ ] 請 Claude 跑 `touch ~/sandbox-probe` 與 `curl --noproxy '*' https://example.com`，兩個都失敗；問要不要在沙箱外重跑時拒絕
- [ ] Codex：裝 `bubblewrap`，Ubuntu 24.04 視需要載入 `bwrap-userns-restrict`
- [ ] 在 WSL 裡安裝 Codex，啟動時沒有 bubblewrap 相關警告
- [ ] 用 `codex sandbox linux` 或在 session 裡測寫入工作區外與連網
- [ ] 把設定好的實驗 distro 再匯出一份備份

<script>
(function () {
  /* ---------- 選擇器 ---------- */
  var picker = document.getElementById("wsx-picker");
  var pickOut = document.getElementById("wsx-pick-out");
  function val(name) {
    var el = picker.querySelector('input[name="' + name + '"]:checked');
    return el ? el.value : "";
  }
  function addList(title, items) {
    if (!items.length) { return; }
    var h = document.createElement("h4");
    h.textContent = title;
    pickOut.appendChild(h);
    var ul = document.createElement("ul");
    items.forEach(function (it) {
      var li = document.createElement("li");
      li.appendChild(document.createTextNode(it.t));
      if (it.inf) {
        var tag = document.createElement("span");
        tag.className = "wsx-tag";
        tag.textContent = "推論";
        li.appendChild(tag);
      }
      ul.appendChild(li);
    });
    pickOut.appendChild(ul);
  }
  function renderPicker() {
    var env = val("wsx-env"), tool = val("wsx-tool"), free = val("wsx-free"), repo = val("wsx-repo");
    var useC = tool === "claude" || tool === "both";
    var useX = tool === "codex" || tool === "both";
    pickOut.innerHTML = "";
    var wsl = [], cl = [], cx = [], ur = [];
    if (env === "win") {
      if (useC) {
        wsl.push({ t: "Claude Code 的沙箱不支援原生 Windows，指令會在沙箱外執行。要用沙箱，就把 Claude Code 裝進 WSL2 [1][3]，再照上一頁建實驗 distro。" });
      }
      if (useX) {
        wsl.push({ t: "Codex 在 PowerShell 用原生 Windows 沙箱（優先 mxc，其次 elevated、unelevated）。官方建議原生 Windows 預設就用它，需要 Linux 工具或工作流本來就在 WSL2 時才改用 WSL [8]。" });
      }
    } else {
      wsl.push({ t: "用上一頁的實驗 distro：關掉自動掛載與 interop，專案放在 Linux 家目錄 [11][12]。" });
      wsl.push({ t: "WSL2 這層擋的是通往 Windows 的路，不擋 distro 裡的寫入與網路，所以下面的 agent 沙箱還是要開。", inf: true });
    }
    if (useC) {
      var pre = env === "win" ? "換到 WSL2 之後：" : "";
      if (env === "win") {
        cl.push({ t: "原生 Windows 沒有 /sandbox 可用 [1]；要放手就先換到 WSL2。以下是換過去之後的建議。" });
      }
      if (free === "ask") {
        cl.push({ t: pre + "/sandbox 選 regular permissions：檔案與網路限制照樣生效，每個指令仍會問你 [1]。" });
      } else if (free === "box") {
        cl.push({ t: pre + "/sandbox 選 auto-allow：沙箱裡的指令不問就跑，deny 規則和有內容的 ask 規則仍有效 [1]。" });
        cl.push({ t: "WSL2 上裝好 seccomp filter（npm install -g @anthropic-ai/sandbox-runtime），沙箱才會擋啟動 Windows 程式的通道 [1][4]。" });
        cl.push({ t: "加上 failIfUnavailable 與 allowUnsandboxedCommands: false，避免沙箱沒起來或被繞過時照常執行 [1]。" });
      } else {
        cl.push({ t: "--dangerously-skip-permissions：官方要求一律放進容器、虛擬機或 sandbox runtime，而且只有 Bash 沙箱不夠 [2]。在 Linux 上以 root 帶這個旗標啟動，Claude Code 會拒絕 [2]。" });
        cl.push({ t: "Anthropic 沒寫 WSL2 算不算這裡說的虛擬機。至少要用關掉自動掛載與 interop 的實驗 distro，再用 sandbox runtime 包住整個 Claude Code [2]。", inf: true });
      }
    }
    if (useX) {
      if (free === "ask") {
        cx.push({ t: "--sandbox read-only --ask-for-approval on-request：只能讀，超出範圍會先問 [7]。" });
      } else if (free === "box") {
        cx.push({ t: "預設 Auto（workspace-write 加 on-request）：工作區內自動做，寫工作區外或要連網會先問；網路預設關閉 [7]。" });
      } else {
        cx.push({ t: "--yolo 是沒有沙箱、也不問 [7]。官方提醒完全存取可能造成資料遺失 [8]；官方舉的用法是在 Linux 沙箱跑不起來的 Docker 容器裡，先由容器提供隔離再這樣跑 [7]。" });
        cx.push({ t: "官方 devcontainer 段落另外警告：在容器裡用 danger-full-access 或 --dangerously-bypass-approvals-and-sandbox，惡意專案可以把容器裡的任何東西帶出去，包括 Codex 的憑證，所以只限用在信任的 repo [7]。" });
        cx.push({ t: "WSL2 算不算這種隔離，官方沒寫。", inf: true });
      }
      if (env === "wsl") {
        cx.push({ t: "WSL2 裡要先裝 bubblewrap；WSL1 從 Codex 0.115 起不支援 [6][9]。" });
      }
    }
    if (repo === "untrusted") {
      if (useC) { ur.push({ t: "Claude Code 官方對不信任的 repo 建議用專用虛擬機，或 Claude 的雲端 session [2]。WSL2 實驗 distro 不在這條建議裡。" }); }
      if (useX) { ur.push({ t: "OpenAI 對不信任 repo 的明確限制在完全存取這一段：在容器裡用 danger-full-access 或 --dangerously-bypass-approvals-and-sandbox，惡意專案可以把容器裡的任何東西帶出去，包括 Codex 的憑證，所以只限用在信任的 repo [7]。平常在本機開這個 repo，可以在使用者層 ~/.codex/config.toml 把該專案設成 trust_level = \"untrusted\"：官方寫指令會先要你核准（execution-policy 規則允許的除外），也會停用專案內的設定 [7]。前提是沒有另外明確指定 approval_policy；官方寫明確設成 on-request 會蓋過這個專案設定 [7]。" }); }
    }
    addList("WSL2／作業系統這一層", wsl);
    addList("Claude Code", cl);
    addList("Codex", cx);
    addList("來路不明的 repo", ur);
    var p = document.createElement("p");
    p.className = "wsx-quiz-ctx";
    p.textContent = "裝完一律照第六節的清單驗證；方括號編號對到本頁的資料來源表。";
    pickOut.appendChild(p);
  }
  if (picker) { picker.addEventListener("change", renderPicker); renderPicker(); }

  /* ---------- 情境測驗 ---------- */
  var Q = [
    { ctx: "WSL2 預設設定（沒改 wsl.conf），沒有 agent 沙箱，agent 設成不經詢問直接執行", q: "agent 在 Linux 裡刪掉 /mnt/c/Users/<你>/Desktop/report.docx", a: "no",
      why: "WSL 預設讓 Linux 存取 Windows 檔案 [13]，沒有 metadata 時權限照你的 Windows 使用者換算 [14]。你的帳號刪得掉，這行就刪得掉（推論）。" },
    { ctx: "實驗 distro 設了 [interop] enabled=false", q: "agent 執行 cmd.exe /c dir", a: "yes",
      why: "interop 關掉後，WSL 不支援從 Linux 啟動 Windows 程式 [11]。" },
    { ctx: "實驗 distro 關了自動掛載，但 agent 的使用者有免密碼 sudo，agent 設成不經詢問直接執行", q: "agent 自己把 C 槽手動掛回來", a: "no",
      why: "官方寫關掉自動掛載後「you could still mount them manually or via fstab」[11]。能用 root 就做得到（推論）。" },
    { ctx: "WSL2，Claude Code 開了 /sandbox，工作目錄是 ~/proj", q: "Claude 執行 touch ~/sandbox-probe", a: "yes",
      why: "沙箱只允許寫工作目錄、暫存目錄與加入的目錄；官方的驗證表寫這行在 Linux／WSL2 會出現 Read-only file system [1]。" },
    { ctx: "WSL2 預設會掛 C 槽，Claude Code 開了 /sandbox", q: "Claude 執行 cat /mnt/c/Users/<你>/notes.txt", a: "dep",
      why: "沙箱預設的讀取範圍是「大部分機器」[1]，所以預設讀得到。設了 permissions.blockReadsOutsideWorkingDirectories，沙箱指令就讀不到 /mnt [4]；上一頁關掉自動掛載的話，/mnt/c 根本不存在 [11]。" },
    { ctx: "WSL2，Claude Code 開了 /sandbox 的 auto-allow，/sandbox 的 Dependencies 分頁顯示缺 seccomp filter", q: "Claude 執行 powershell.exe -c Get-Date", a: "no",
      why: "WSL2 透過 Unix socket 啟動 Windows 程式，沙箱要靠 seccomp filter 才擋得住這個 socket；filter 不在時，沙箱不擋 Unix socket 呼叫 [1][4]。" },
    { ctx: "Claude Code 開了 /sandbox，設定了 sandbox.filesystem.denyRead: [\"~/.aws\"]；你另外在權限規則寫過 Read(~/.aws/**) 的 allow", q: "Claude 用內建的 Read 工具（不是 Bash）讀 ~/.aws/credentials", a: "no",
      why: "沙箱只管 shell 指令，官方原文：「A denyRead entry doesn't stop the Read tool」[1]。Read 工具由權限規則決定，題目裡的 allow 規則讓它不問就讀。沒有這條 allow 時，Read 只在工作目錄與加入的目錄內免核准，讀 ~/.aws 會先問你 [15]。要真正擋住，寫 Read(~/.aws/**) 的 deny 規則 [1][15]。" },
    { ctx: "Claude Code 開了 /sandbox 的 auto-allow", q: "你裝的一個 hook 腳本執行 rm -rf ~/old-notes", a: "no",
      why: "hooks、本機 MCP server 這類 Claude Code 啟動的程序不在沙箱裡，官方寫它們「run with your full access」[1]。" },
    { ctx: "WSL2，Codex 用預設的 Auto（workspace-write 加 on-request）", q: "Codex 想執行 curl https://example.com", a: "yes",
      why: "預設網路關閉；Auto 模式下要連網會先問你 [7]。" },
    { ctx: "Codex 用 workspace-write，工作區是一個 git 專案", q: "Codex 執行的指令想改寫工作區裡的 .git/config", a: "yes",
      why: "workspace-write 下，可寫目錄裡的 .git 是唯讀的，而且往下全部唯讀 [7]。" }
  ];
  var LABEL = { yes: "會被擋", no: "不會被擋", dep: "看設定" };
  var list = document.getElementById("wsx-quiz-list");
  var score = document.getElementById("wsx-quiz-score");
  var answered = {};
  function updateScore() {
    var n = 0, ok = 0;
    Object.keys(answered).forEach(function (k) { n++; if (answered[k]) { ok++; } });
    score.textContent = n ? ("已作答 " + n + "／" + Q.length + " 題，答對 " + ok + " 題") : "";
  }
  function buildQuiz() {
    list.innerHTML = "";
    answered = {};
    Q.forEach(function (item, i) {
      var box = document.createElement("div");
      box.className = "wsx-quiz-item";
      var ctx = document.createElement("p");
      ctx.className = "wsx-quiz-ctx";
      ctx.textContent = "情境：" + item.ctx;
      var q = document.createElement("p");
      q.textContent = (i + 1) + ". " + item.q;
      var btns = document.createElement("div");
      btns.className = "wsx-btns";
      btns.setAttribute("role", "group");
      btns.setAttribute("aria-label", "第 " + (i + 1) + " 題選項");
      var fb = document.createElement("div");
      fb.setAttribute("aria-live", "polite");
      ["yes", "no", "dep"].forEach(function (key) {
        var b = document.createElement("button");
        b.type = "button";
        b.textContent = LABEL[key];
        b.setAttribute("aria-pressed", "false");
        b.dataset.key = key;
        b.addEventListener("click", function () {
          btns.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
          var right = key === item.a;
          answered[i] = right;
          fb.className = "wsx-feedback " + (right ? "wsx-ok" : "wsx-no");
          fb.innerHTML = "";
          var head = document.createElement("b");
          head.textContent = (right ? "答對：" : "正確答案是：") + LABEL[item.a];
          fb.appendChild(head);
          fb.appendChild(document.createTextNode(item.why));
          updateScore();
        });
        btns.appendChild(b);
      });
      box.appendChild(ctx);
      box.appendChild(q);
      box.appendChild(btns);
      box.appendChild(fb);
      list.appendChild(box);
    });
    updateScore();
  }
  if (list) {
    buildQuiz();
    document.getElementById("wsx-quiz-reset").addEventListener("click", buildQuiz);
  }

  /* ---------- 指令複製按鈕 ---------- */
  function fallback(text, done) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    document.body.removeChild(ta);
    done(ok);
  }
  function copyText(text, done) {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(function () { done(true); }, function () { fallback(text, done); });
    } else { fallback(text, done); }
  }
  document.querySelectorAll(".doc pre").forEach(function (pre) {
    var code = pre.querySelector("code");
    if (!code || pre.querySelector(".wsx-copy")) { return; }
    pre.classList.add("wsx-pre");
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "wsx-copy";
    btn.textContent = "複製";
    btn.setAttribute("aria-label", "複製這段指令");
    btn.addEventListener("click", function () {
      copyText(code.textContent, function (ok) {
        btn.textContent = ok ? "已複製" : "請手動選取";
        setTimeout(function () { btn.textContent = "複製"; }, 1600);
      });
    });
    pre.appendChild(btn);
  });
})();
</script>

## 本頁重點回顧

- Claude Code 的 `/sandbox` 支援 macOS、Linux、WSL2，不支援 WSL1 與原生 Windows；在 WSL2 要裝 `bubblewrap`、`socat`，Ubuntu 24.04 以後可能要加 AppArmor profile。
- `/sandbox` 只管 shell 指令。Read、Edit 等內建工具、hooks、MCP server 不在沙箱裡，要靠 permission rules，或把整個 Claude Code 放進容器、虛擬機、sandbox runtime。
- WSL2 上沒裝 seccomp filter 時，沙箱裡的指令仍能啟動 Windows 程式；`blockReadsOutsideWorkingDirectories` 可以讓沙箱指令讀不到 `/mnt`。
- 沙箱起不來時 Claude Code 預設照常執行指令，要擋就設 `failIfUnavailable`。
- Codex 在 WSL2 用 Linux 沙箱（bwrap 加 seccomp），0.115 起不支援 WSL1；原生 Windows 有 `mxc`、`elevated`、`unelevated` 三種實作。網路預設關閉，`.git`、`.codex`、`.agents` 在工作區裡也是唯讀。
- WSL2 實驗 distro 擋通往 Windows 的路，agent 沙箱擋 distro 裡的寫入與網路，兩層要一起用。

## 資料來源

| 標記 | 來源 | URL |
|---|---|---|
| [1] | Claude Code：Configure the sandboxed Bash tool（預設範圍、沙箱外的工具、Linux／WSL2 安裝、seccomp filter、WSL2 interop、驗證指令、設定範例、與 permission rules 的分工） | <https://code.claude.com/docs/en/sandboxing> |
| [2] | Claude Code：Choose a sandbox environment（sandbox runtime、`--dangerously-skip-permissions` 的要求、不信任 repo 的建議） | <https://code.claude.com/docs/en/sandbox-environments> |
| [3] | Claude Code：Set up Claude Code（Windows 三種選項的沙箱支援、在 WSL 裡安裝） | <https://code.claude.com/docs/en/setup> |
| [4] | Claude Code：Settings reference（`allowAllUnixSockets`、`blockReadsOutsideWorkingDirectories`） | <https://code.claude.com/docs/en/settings-reference> |
| [5] | Claude Code：Choose a permission mode（Manual 加 Bash 沙箱 auto-allow 的組合） | <https://code.claude.com/docs/en/permission-modes> |
| [6] | Codex：Sandbox（各平台前置需求、bubblewrap 與 AppArmor、`writable_roots`） | <https://learn.chatgpt.com/docs/sandboxing> |
| [7] | Codex：Agent approvals & security（網路預設關閉、工作區範圍、受保護路徑、`--yolo`、平台機制、`codex sandbox`） | <https://learn.chatgpt.com/docs/agent-approvals-security> |
| [8] | Codex：Windows sandbox（`mxc`／`elevated`／`unelevated`、何時選 WSL、完全存取的提醒） | <https://learn.chatgpt.com/docs/windows/windows-sandbox> |
| [9] | Codex：WSL（WSL2 用 Linux 沙箱、WSL1 自 0.115 不支援、在 WSL 安裝） | <https://learn.chatgpt.com/docs/windows/wsl> |
| [10] | Codex：Permissions（beta 的 permission profile、拒讀工作區以外的範例） | <https://learn.chatgpt.com/docs/permissions> |
| [11] | Microsoft：Advanced settings configuration in WSL（`automount`、`interop`、`networkingMode`） | <https://learn.microsoft.com/en-us/windows/wsl/wsl-config> |
| [12] | Microsoft：Working across file systems（從 Linux 執行的 Windows 程式以目前 Windows 使用者身分執行） | <https://learn.microsoft.com/en-us/windows/wsl/filesystems> |
| [13] | Microsoft：WSL FAQ（WSL 自動讓 Linux 存取 Windows 檔案） | <https://learn.microsoft.com/en-us/windows/wsl/faq> |
| [14] | Microsoft：File Permissions for WSL（DrvFs 權限換算） | <https://learn.microsoft.com/en-us/windows/wsl/file-permissions> |
| [15] | Claude Code：Configure permissions（Read 工具在工作目錄與加入的目錄內免核准、`Read(~/...)` 規則寫法） | <https://code.claude.com/docs/en/permissions> |

延伸：[WSL2 當隔離環境](wsl2-isolation.md)｜[Claude Code 設定總覽](official-config.md)｜[AI Agent 怎麼運作](agent-basics.md)｜[Claude Code + Codex 協作](claude-codex.md)
