# Claude Code + Codex 協作

> 查證日期：2026-09-16。方案與功能變動快，請以官方最新說明為準。本頁只寫查得到出處或實際驗證過的做法，不誇大可行性；個人的 Claude Code 規則檔、派工制度、設定檔內容不在本頁範圍內。

網路上常見的教學把 Cowork 跟 Claude Code 混為一談，也常照抄已經失效的 `codex mcp-server` 設定。這頁把「哪些組合現在真的可行」講清楚，再給兩種確定可行的做法，最後列出已知的坑。

## 一、為什麼要讓兩個 agent 分工

同一個模型自己審查自己寫的東西，很容易帶著「我當初是這樣想的」去護航；就算換一次對話重跑，同一顆模型在相近提示詞下產生的意見也容易系統性地往同一個方向靠攏，稱不上真正獨立的第二意見。換一個不同公司、不同模型的 agent 來審查或交叉查證，才是比較站得住腳的獨立視角。分工還有另一個現實理由：把研究、審查、實作拆給不同工具做，省下自己一個個手動比對的時間，也能各自用各自比較便宜或比較快的模型跑該做的那一段。

以下四種組合，可行程度差很多，動手前先看這張表：

| 組合 | 現況 | 出處 |
|---|---|---|
| **Claude Code + Codex plugin**（`openai/codex-plugin-cc`） | 官方可行，OpenAI 官方 GitHub 組織發布，有完整安裝與操作文件 | [openai/codex-plugin-cc README](https://github.com/openai/codex-plugin-cc/blob/main/README.md) |
| **Claude Code 直接呼叫 Codex CLI**（`codex exec`） | 可行，不需要裝 plugin，本機裝好 Codex CLI 即可 | [Codex CLI 文件](https://learn.chatgpt.com/docs/codex/cli) |
| **Codex 透過 MCP 呼叫 `claude mcp serve`** | 實驗性，兩端各自公開的 MCP 介面湊得起來，但查無官方文件明載或認證這個組合；`claude mcp serve` 只開放 Claude Code 的工具層，不是把整個 Claude 模型或 agent loop 變成可委派的對象 | [Codex MCP client](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)、[Claude Code 作為 MCP server](https://code.claude.com/docs/en/mcp#use-claude-code-as-an-mcp-server) |
| **Cowork + Codex** | 目前查無官方支援、可直接照做的整合方式 | [Cowork 架構](https://support.claude.com/en/articles/14479288-claude-cowork-architecture-overview)、[Codex MCP server removal](https://learn.chatgpt.com/docs/mcp-server) |

後面的做法一、做法二只處理前兩種組合；第三種留在「已知的坑」一節簡單交代，第四種留在最後的 Cowork 段落說明為什麼接不上。

## 二、做法一：安裝 openai/codex-plugin-cc

這個 plugin 由 OpenAI 官方 GitHub 組織發布，透過本機的 Codex CLI 與 Codex App Server 執行，不是另一套獨立的引擎。

### 前置條件

- Node.js 18.18 以上。
- 本機能執行全域 `codex` CLI，且已完成登入（可用具 Codex 權益的 ChatGPT 帳號，或 OpenAI API key）。
- 能使用 Claude Code 的 plugin marketplace。

來源：[Plugin README（Requirements 一節）](https://github.com/openai/codex-plugin-cc/blob/main/README.md#requirements)

### 安裝步驟

在 Claude Code 對話框依序輸入：

```text
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
/codex:setup
```

若尚未安裝 Codex CLI，可讓 `/codex:setup` 協助安裝，或自己手動跑：

```bash
npm install -g @openai/codex
codex login
```

在 Claude Code 對話框裡執行 shell 指令，官方 README 用的寫法是在指令前面加一個驚嘆號：

```text
!codex login
```

裝完可以先跑一輪測試：

```text
/codex:review --background
/codex:status
/codex:result
```

來源：[Plugin README（Install 一節）](https://github.com/openai/codex-plugin-cc/blob/main/README.md#install)

### 8 個指令

| 指令 | 用途 | 適合情境 |
|---|---|---|
| `/codex:review` | 對目前未提交的變更、或跟 base branch 的差異，跑唯讀的一般 review，不改程式 | 想知道這次改動有沒有明顯 bug |
| `/codex:adversarial-review` | 唯讀挑戰實作方向、設計取捨、隱藏假設與失敗模式，可附加自訂焦點 | 上線前想確認某個高風險設計決策站不站得住腳，而不是找細節錯字 |
| `/codex:rescue` | 透過 `codex:codex-rescue` subagent 把 bug 調查、修復或延續任務交給 Codex，可選 model／effort | 想把一段任務整個交給 Codex 動手做，而不只是要意見 |
| `/codex:transfer` | 把目前 Claude Code session 匯出成 Codex thread，輸出 `codex resume <session-id>` | 想離開 Claude Code，換到 Codex CLI／App 用同一份 context 接著做 |
| `/codex:status` | 查看目前 repository 裡執行中或近期的 Codex 背景任務 | 派了背景任務想知道跑到哪了 |
| `/codex:result` | 讀取已完成任務的最終輸出，也可取得 session ID 回到 Codex 繼續 | 背景任務跑完要看結果 |
| `/codex:cancel` | 取消正在執行的 Codex 背景任務 | 派錯了或不想等了 |
| `/codex:setup` | 檢查 Codex CLI 是否安裝並完成登入，也可管理 review gate | 第一次裝好之後的健康檢查 |

來源：[Plugin README（Commands 一節）](https://github.com/openai/codex-plugin-cc/blob/main/README.md)

## 三、做法二：不裝 plugin，直接呼叫 `codex exec`

不想裝 plugin，或想更細緻控制每次呼叫，可以在 Claude Code 裡直接叫 shell 執行 `codex exec`。以下語法已在 codex-cli 0.154.0 的 `--help` 實際確認存在：

| 語法 | 作用 |
|---|---|
| `codex exec` | 非互動模式執行一次任務 |
| `-s read-only` / `-s workspace-write` / `-s danger-full-access` | 三段式 sandbox：唯讀／可在工作區內編輯與跑指令／完全不設防 |
| `-C <dir>` | 指定要在哪個目錄執行 |
| `--skip-git-repo-check` | 目標目錄不是 git repo 時，跳過檢查直接執行 |
| `-o` / `--output-last-message <file>` | 把最後一則訊息寫進指定檔案 |
| 從 stdin 讀 prompt（用 `-` 代表） | 把 prompt 內容用管線或重新導向餵進去，不用整段貼在指令列裡 |
| `--add-dir <dir>` | 額外授權 Codex 讀寫工作目錄以外的另一個目錄 |
| `codex --search`（全域旗標，要放在 `exec` 之前） | 開啟網路搜尋 |

來源：[Codex CLI reference](https://developers.openai.com/codex/cli/reference)（會轉址到 `learn.chatgpt.com/docs/developer-commands`）；`--add-dir` 與三段式 sandbox 另可見官方 [Codex sandboxing](https://learn.chatgpt.com/docs/sandboxing)。

**範例一：唯讀研究**（`-s read-only` 不會修改研究對象或專案裡的任何檔案，但 `-o` 仍會在你指定的路徑新增或覆寫 `report.md` 這一份輸出檔，這不算沙箱破例，是這個旗標本來的作用）：

終端機 Bash／macOS／Linux／Windows 的 Git Bash：

```bash
codex --search exec -s read-only -o report.md - < prompt.md
```

Windows PowerShell 沒有 `<` 這種重新導向語法，改用管線把檔案內容餵給 stdin：

```powershell
Get-Content prompt.md -Raw | codex exec --search -s read-only -o report.md -
```

在 Claude Code 對話框裡執行以上任一行，要在指令前加驚嘆號讓它當成 shell 指令直接跑（`!codex --search exec ...`），或者不加驚嘆號、直接用一般對話請 Claude 幫你執行，讓它自己呼叫 Bash 工具。

**範例二：可寫入的實作任務**（在指定目錄裡真的改檔案、跑指令）：

```bash
codex exec -s workspace-write -C ~/projects/demo "依 spec.md 裡的規格實作這個功能"
```

上面這兩行 PowerShell 管線寫法官方文件沒有給範例，是本站按 PowerShell 一般語法推出的通用寫法，不是官方逐字教學，用之前建議自己先跑一次確認行為符合預期。

## 四、分工模式

**Claude 規劃、Codex 執行**：先讓 Claude Code（或 `Plan`）把規格拆成可逐條驗證的條件，再把這份規格連同驗收條件交給 Codex 執行。適合規格已經明確、自包含、不需要理解特定專案脈絡規則的程式或腳本任務，例如「把這支腳本的輸出格式從 CSV 改成 JSON，欄位對照見附表」。

**一方寫、另一方審**：做的人不驗自己的活。Claude Code 寫完一段實作後，派 `/codex:review` 或 `/codex:adversarial-review` 讓 Codex 用乾淨的視角只看 diff 跟驗收條件審查，不要讓寫的那個 agent 自己審查自己。適合任何你要對外交付的變更，尤其是動到認證、資料寫入、金流這類高風險區塊。

**交叉查證**：同一個事實問題，讓 Claude 跟 Codex 各自查一次官方文件再比對答案。適合查證「某個 API 旗標存不存在」「某個功能哪個方案才能用」這類容易被訓練記憶誤導的問題。兩邊都查到同一個答案才比較有把握，分歧本身就是該進一步查證的訊號。

## 五、已知的坑

**a. 背景模式的 job 狀態可能跟 Codex 實際進度脫鉤**

用 `--background` 派出的任務，`/codex:status` 顯示的狀態有時跟 Codex 實際在做的事不同步。截至查證當下，`openai/codex-plugin-cc` 的 issue tracker 裡有多筆相關且仍開著的問題，例如 [#639](https://github.com/openai/codex-plugin-cc/issues/639)（`result`／`cancel` 對存在的任務回報「找不到任務」，被中止的 worker 卻仍顯示執行中）與 [#704](https://github.com/openai/codex-plugin-cc/issues/704)（worker 在寫入最終狀態前就掛掉，任務因此永遠顯示執行中）。

避法：短任務直接用同步模式（不加 `--background`）；真的要背景跑的長任務，任務完成的判定不能只看 `/codex:status` 顯示 completed，要另外直接檢查預期的輸出檔案是否存在、內容是否正確、更新時間是否在合理範圍內。

**b. 前景執行時間過長會被自動轉成背景**

Claude Code 的 Bash 工具預設前景逾時是 2 分鐘（120 秒），逾時的上限預設是 10 分鐘（600 秒），可以用環境變數 `BASH_MAX_TIMEOUT_MS` 調整，不是一個改不動的硬性天花板；逾時仍沒跑完時，Claude Code 不會中斷它，而是把它轉成背景執行，結果訊息會明確寫「在 120 秒逾時內沒有跑完，已轉入背景」，並給出任務 ID 與輸出檔案路徑。來源：[Claude Code Tools reference](https://code.claude.com/docs/en/tools-reference)。

這代表透過 `codex-plugin-cc` 轉發呼叫 Codex 時，即使沒有主動加 `--background`，只要單次呼叫超過這個時間，也會被 Bash 工具自動轉成背景執行；此時 agent 可能只回報「轉發完成」，字面上容易被誤讀成「Codex 已經做完」，但實際工作是否做完，仍要照上一條的做法核對輸出檔案。

**c. Codex sandbox 預設只能寫工作目錄**

`workspace-write` 模式預設只授權寫入啟動時所在的工作目錄。要讓 Codex 動到別的目錄，用 `-C <dir>` 直接指定要在哪個目錄執行，或用 `--add-dir <dir>` 額外授權工作目錄以外的另一個目錄（兩者皆已於 `--help` 確認存在）。

**d. 在 sandbox 裡讓 Codex 自己 `git init`，Windows 上可能整組壞掉**

這是實際在 Windows 上遇到的狀況，不是官方文件寫的行為：在 `workspace-write` 沙箱裡讓 Codex 自己執行 `git init`，產生的 `.git` 資料夾擁有者可能是沙箱帳號而不是目前的使用者，之後在沙箱外執行 git 指令時會因為「dubious ownership」而全部失敗。避法：git 的初始化交給人或在沙箱外的 Claude Code 做，不要讓 Codex 在沙箱內自己建 repo。

**e. `codex mcp-server` 已經移除**

舊版 Codex 曾提供 `codex mcp-server` 指令與獨立的 `codex-mcp-server` binary，OpenAI 現行文件已明載兩者皆已移除；現在的 `codex app-server` 是給圖形介面與整合程式用的 JSON-RPC server，官方明確說它不是 MCP server，不能拿來取代舊教學裡的 `codex mcp-server` 設定。網路上還能搜到的舊版 MCP 設定範例，照抄會直接失敗。來源：[Codex MCP server removal](https://learn.chatgpt.com/docs/mcp-server)。

**f. review gate 會讓兩邊互相呼叫、快速燒額度**

`/codex:setup --enable-review-gate` 可以讓 Claude 收尾前自動要求 Codex review，但官方 README 明白警告這可能形成長時間的 Claude／Codex 來回迴圈，快速消耗雙方額度，不適合無人看管的情境。來源：[Plugin README（Enabling review gate 一節）](https://github.com/openai/codex-plugin-cc/blob/main/README.md#enabling-review-gate)。

**g. Codex 預設不會自動讀你寫給 Claude 的 CLAUDE.md**

Claude Code 讀的是 `CLAUDE.md`，官方文件裡查無它會讀取 `AGENTS.md` 的說明；Codex 預設讀的是 `AGENTS.md`，依 `~/.codex` 全域到專案路徑逐層合併，越接近目前目錄優先權越高。來源：[How Claude remembers your project](https://code.claude.com/docs/en/memory)、[Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)。

這不代表兩邊只能各寫一份、內容永遠對不上，官方留了兩個共用做法：一是在 Codex 的 `~/.codex/config.toml` 設定 `project_doc_fallback_filenames`，把 `CLAUDE.md` 加進這個清單，讓 Codex 除了 `AGENTS.md` 之外也讀它；二是反過來在 Claude Code 的 `CLAUDE.md` 裡用 `@AGENTS.md` 這個匯入語法，把 `AGENTS.md` 的內容併進 Claude 讀到的 context。兩種做法都只解決「同一份內容要不要維護兩次」，不會改變預設行為本身；沒特別設定的情況下，用 `/codex:rescue` 或直接呼叫 `codex exec` 把任務交給 Codex 時，凡是 Codex 需要知道的專案脈絡（架構、紅線、命名慣例），還是要寫進當次的 prompt 裡，不能指望它自己去讀 CLAUDE.md。

## 六、Cowork 呢

截至查證日，查無 OpenAI 或 Anthropic 任何一方明確宣告支援 Cowork + Codex 的整合；這不代表技術上已經證明完全不可行，只代表目前沒有官方認證、可以照抄的做法。理由分三層：

1. Cowork 的 shell 跑在 Anthropic 管理的雲端 VM，或既有 Desktop 部署下的本機專用 Linux VM，兩者都不等於使用者主機的終端機，不會繼承主機上的 `codex` 執行檔、PATH 或登入狀態。來源：[Cowork architecture overview](https://support.claude.com/en/articles/14479288-claude-cowork-architecture-overview)。
2. Cowork 的自訂 connector 是 remote MCP，只能填入一個 Anthropic 雲端能連進去的 URL，而 OpenAI 目前沒有提供可以填進這個欄位的官方 Codex remote MCP endpoint；已移除的 `codex mcp-server` 也不是這裡能用的東西。來源：[Codex MCP server removal](https://learn.chatgpt.com/docs/mcp-server)。
3. Cowork 確實已經支援 plugin，部分本機 Cowork 情境下也能執行 plugin 內含的本機 MCP server，但查無 OpenAI 官方發布過一個給 Cowork 用的 Codex plugin。`openai/codex-plugin-cc` 的 README 明確把自己定位成給 Claude Code 用的 plugin，沒有保證能在 Cowork 正常運作。來源：[Use plugins in Claude](https://support.claude.com/en/articles/13837440-use-plugins-in-claude)。

想找 Cowork 跟 Codex 官方整合的教學，目前應該視為查無出處，不要照抄任何寫「在 Cowork 裡輸入指令呼叫本機 `codex exec`」的舊文章；有人自己動手拼出一套本機 MCP wrapper 也不是不可能，但那是自製實驗，不是本頁能保證的做法。

## 本頁重點回顧

- 四種組合裡，只有「Claude Code + Codex plugin」跟「Claude Code 直接呼叫 `codex exec`」現在確定可行；「Codex 透過 MCP 呼叫 `claude mcp serve`」是實驗性、只開放工具層；「Cowork + Codex」目前查無官方整合。
- 裝 plugin 走 `/plugin marketplace add` → `/plugin install` → `/reload-plugins` → `/codex:setup` 四步，8 個指令分工清楚：review／adversarial-review 唯讀審查，rescue 真的動手做，transfer 換到 Codex 環境接續。
- 不裝 plugin 也能直接用 `codex exec` 搭配 `-s`、`-C`、`--skip-git-repo-check`、`-o`、stdin、`--add-dir` 這幾個已確認的旗標。
- 三種分工模式各有適用情境：規格明確就規劃後交出去執行，高風險變更一定要讓另一個 agent 審查，容易被誤導的事實問題交叉查證。
- 七個坑裡最容易踩的是背景任務狀態脫鉤跟前景逾時自動轉背景，兩者都要靠檢查輸出檔案而非信任狀態訊息；Windows 上讓 Codex 自己 `git init` 也是實測會出事的地方；CLAUDE.md／AGENTS.md 各讀各的也有官方留的共用做法（`project_doc_fallback_filenames`、`@AGENTS.md` 匯入），不是只能維護兩份重複內容。

## 資料來源

| 來源 | URL |
|---|---|
| openai/codex-plugin-cc README | <https://github.com/openai/codex-plugin-cc/blob/main/README.md> |
| Codex CLI reference（`codex exec` 旗標） | <https://developers.openai.com/codex/cli/reference> |
| Codex CLI 文件 | <https://learn.chatgpt.com/docs/codex/cli> |
| Codex sandboxing | <https://learn.chatgpt.com/docs/sandboxing> |
| Codex MCP client | <https://learn.chatgpt.com/docs/extend/mcp?surface=cli> |
| Codex MCP server removal | <https://learn.chatgpt.com/docs/mcp-server> |
| Codex AGENTS.md（含 `project_doc_fallback_filenames`） | <https://learn.chatgpt.com/docs/agent-configuration/agents-md> |
| Claude Code 作為 MCP server | <https://code.claude.com/docs/en/mcp#use-claude-code-as-an-mcp-server> |
| Claude Code Tools reference（Bash 逾時、`BASH_MAX_TIMEOUT_MS`、自動轉背景） | <https://code.claude.com/docs/en/tools-reference> |
| How Claude remembers your project（`@AGENTS.md` 匯入語法） | <https://code.claude.com/docs/en/memory> |
| Cowork architecture overview | <https://support.claude.com/en/articles/14479288-claude-cowork-architecture-overview> |
| Use plugins in Claude | <https://support.claude.com/en/articles/13837440-use-plugins-in-claude> |
| openai/codex-plugin-cc Issues #639、#704 | <https://github.com/openai/codex-plugin-cc/issues> |

延伸：[AI 介面比較總表](tools-compare.md)｜[付費區](paid-tier.md)｜[把 AI 代理的工作環境設計得可靠](harness.md)
