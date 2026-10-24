# Claude Code 設定總覽

> 查證日期：2026-10-19（安裝、設定檔細節、CLAUDE.md 與規則檔細節、auto memory、出問題怎麼查）；其餘 2026-10-05。方案與功能變動快，請以官方最新說明為準。

前面幾頁講的是[AI Agent 怎麼運作](agent-basics.md)、[各種擴充機制解決什麼問題](extensions.md)、[怎麼把工作環境設計得可靠](harness.md)——都是原理層。這頁換一個角度，只回答一個問題：**Claude Code 官方文件建議怎麼設定**。內容照官方文件的說法整理，不包含任何個人或特定專案的客製規則；你自己專案要怎麼寫，是另一回事，這頁只負責把官方定義的介面講清楚。

## 開始之前：安裝與第一次啟動

要用 Claude Code，需要 Claude 訂閱（Pro、Max、Team 或 Enterprise）、Claude Console 帳號，或透過支援的雲端供應商取得的使用權[10]。系統需求是 macOS 13.0 以上、Windows 10 1809 以上或 Windows Server 2019 以上、Ubuntu 20.04 以上，4 GB 以上記憶體，x64 或 ARM64 處理器，而且要連網[11]。

官方建議的原生安裝指令[10]：

```bash
# macOS、Linux、WSL
curl -fsSL https://claude.ai/install.sh | bash

# Windows PowerShell
irm https://claude.ai/install.ps1 | iex

# Windows CMD
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

原生安裝會在背景自動更新[10]。也可以用 `brew install --cask claude-code` 或 `winget install Anthropic.ClaudeCode` 安裝，但這兩種不會自動更新，要自己定期跑 `brew upgrade claude-code` 或 `winget upgrade Anthropic.ClaudeCode`[10]。裝完開一個新的終端機視窗跑 `claude --version`，印出版本號就是裝好了[10]。原生 Windows 上官方建議先裝 Git for Windows，Claude Code 才能用 Bash 工具；沒裝的話，Claude Code 改用 PowerShell 當 shell 工具[10]。

在任何專案資料夾開終端機，輸入 `claude` 就能啟動，第一次使用會要你登入[10]。進去之後打 `/help` 看可用指令，打 `/resume` 接續之前的對話；之後想換帳號或重新登入，在 session 裡打 `/login`[10]。

## 一、CLAUDE.md：放在哪、寫什麼

CLAUDE.md 依檔案位置分四層，載入順序由廣到窄；子目錄的 CLAUDE.md 不在啟動時載入，而是 Claude 讀到該子目錄底下的檔案時才動態載入[1]：

| 範圍 | 位置 | 用途 |
|---|---|---|
| 組織管理政策 | macOS `/Library/Application Support/ClaudeCode/CLAUDE.md`；Linux/WSL `/etc/claude-code/CLAUDE.md`；Windows `C:\Program Files\ClaudeCode\CLAUDE.md` | IT／DevOps 統一管理的組織規範 |
| 使用者層 | `~/.claude/CLAUDE.md` | 個人跨專案偏好 |
| 專案層 | `./CLAUDE.md` 或 `./.claude/CLAUDE.md` | 團隊共用，走版控 |
| 本機專案層 | `./CLAUDE.local.md` | 個人在這個專案的偏好，建議加進 `.gitignore` |

**這四層是全部串接進同一個上下文，不是互相覆蓋。** 從檔案系統根目錄往下排到目前工作目錄，越接近啟動目錄的檔案排在越後面（越晚被讀到）；同一層裡 `CLAUDE.local.md` 排在 `CLAUDE.md` 之後[1]。

官方對「該寫什麼」給了一句判準：「把 CLAUDE.md 當成你原本會重複解釋的內容寫下來」[1]。以下對照表出自 best practices 文件（節錄）[6]：

| 該放 | 不該放 |
|---|---|
| Claude 猜不到的 Bash 指令 | Claude 讀程式碼就能推出的東西 |
| 與預設不同的風格規則 | 標準語言慣例 |
| 測試指令與慣用測試工具 | 詳細 API 文件（改連結） |
| repo 禮節（分支命名、PR 慣例） | 常變動的資訊 |
| 專屬本專案的架構決策 | 長篇說明教學 |

篇幅上限：**官方建議每個 CLAUDE.md 檔案控制在 200 行以內**，理由是「檔案越長，越消耗上下文，模型遵從度也越低」[1]；判斷該不該留的問題是「拿掉這一行，模型會不會因此犯錯？」[6]答不出來就刪，或搬進[SKILL](extensions.md)。單檔硬上限是 4 MiB，超過會被整檔跳過不載入[1]。

`/init` 會分析程式庫自動生成一版 CLAUDE.md 起點；若已存在 CLAUDE.md，`/init` 改為建議增修而不覆寫，也會嘗試併入既有的 Cursor rules 或 Copilot rules[1]。CLAUDE.md 內可用 `@path/to/file` 語法匯入其他檔案（相對路徑以「引用它的那個檔案」為基準，可遞迴匯入，最深 4 層）；只是要在文字中「提到」某個路徑而不想觸發匯入，用反引號包起來即可[1]。

CLAUDE.md 和 auto memory（見第六節）在每次對話開始時都會載入，但 Claude 把它們當成 context，不是強制執行的設定[1]。指示寫得越具體、越精簡，Claude 遵守得越一致[1]。一定要擋下的動作，例如「不准改 `.env`」，寫在 CLAUDE.md 只是請求，不是保證，要用 `PreToolUse` hook 或權限規則才擋得住[1][17]。

### 載入與匯入的細節

- **子目錄的 CLAUDE.md 什麼時候載入**：Claude 讀取、寫入或編輯該子目錄裡的其他檔案時載入。用 Bash 對單一檔案跑 `cat`、`head` 這類算讀取的指令，也會觸發[1]。
- **從哪裡啟動，決定載入什麼**：從 repo 根目錄啟動，只載入根目錄的 CLAUDE.md，子目錄的等用到才載入；從子目錄啟動，載入那個目錄和它所有上層目錄的 CLAUDE.md[14]。`.claude/settings.json` 不會像 CLAUDE.md 那樣從上層目錄繼承[14]。
- **HTML 註解不佔 context**：CLAUDE.md 裡的區塊 HTML 註解（`<!-- maintainer notes -->`）在注入 context 前會被拿掉，可以拿來留給維護者看的備註；程式碼區塊裡的註解則保留[1]。
- **路徑有空格**：每個空格前面加反斜線。用引號包起來的路徑完全不會匯入，加不加反斜線都一樣[1]。
- **匯入不省 context**：匯入能幫你整理一份很長的檔案，但被匯入的檔案也在啟動時載入，context 成本沒有變少[1]。
- **外部匯入要你核准**：專案層的 CLAUDE.md 匯入了工作目錄以外的檔案，算外部匯入。Claude Code 第一次在一個專案遇到外部匯入，會跳對話框列出這些檔案；你拒絕的話，這些匯入保持停用，對話框也不會再出現[1]。
- **多個 git worktree**：被 gitignore 的 `CLAUDE.local.md` 只存在你建立它的那個 worktree。想在同一個 repo 的多個 worktree 共用個人指示，改成從家目錄匯入一個檔案[1]。
- **`--add-dir` 加進來的目錄**：預設不載入那些目錄裡的 CLAUDE.md。要載入，設環境變數 `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`[1]。
- **排除某些檔案**：`claudeMdExcludes` 設定可以依路徑或 glob 跳過特定的 CLAUDE.md，但組織的 managed CLAUDE.md 排除不掉[1]。
- **`/init` 的互動流程**：設 `CLAUDE_CODE_NEW_INIT=1` 之後，`/init` 會問你要建哪些東西，包括 CLAUDE.md、skill 和 hook[1][16]。

### 什麼時候該補進 CLAUDE.md、怎麼寫

官方列的時機有四個：Claude 第二次犯同一個錯、code review 抓到 Claude 本該知道的這個 codebase 的事、你在對話裡打了上次 session 打過的同一句糾正或說明、新隊友也需要同樣的背景才能上手[1]。內容只放每個 session 都該知道的事實，例如 build 指令、慣例、專案結構、「一律做 X」的規則。多步驟的程序，或只跟 codebase 某一塊有關的內容，改放 skill 或有 `paths` 的規則檔[1]。

寫法上官方的建議[1][6]：

- **寫到可以驗證**：寫「Use 2-space indentation」，不寫「Format code properly」；寫「Run npm test before committing」，不寫「Test your changes」。
- **用標題和條列分組**：整理過的段落比密密麻麻的長段好照著做。
- **不要互相矛盾**：兩條指示衝突時，Claude 可能隨便挑一條。
- **該放與不該放**：除了上面的對照表，開發環境的特殊狀況（例如必要的環境變數）該放，逐檔描述 codebase 則不該放。
- **強調要省著用**：某一條 Claude 一直跳過，只在那一行加「IMPORTANT」這類強調。強調的行太多，哪一行都不突出。
- **當成程式碼維護**：出問題時回頭看、定期修剪、改完觀察 Claude 的行為有沒有真的變。把 CLAUDE.md commit 進 git，讓團隊一起改。

大型 repo 還有兩點：CLAUDE.md 的修改跟其他文件修改一樣在 pull request 裡審；模型大改版之後重看一次，為了繞過舊模型限制而寫的指示，新模型可能已經不需要[14]。

想讓 Claude 檢查指示檔有沒有過時或矛盾的內容，在 session 裡跑 `/doctor prompt-audit`（v2.1.283 起）。它會列出發現和建議的修改，你叫它套用之前，檔案都不會動[1]。也可以在 CLAUDE.md 裡寫壓縮時要保留什麼，例如「When compacting, always preserve the full list of modified files and any test commands」[6]。

**只要工作目錄或其任何上層目錄有 `CLAUDE.md`（含 `.claude/CLAUDE.md`、`CLAUDE.local.md`），Claude Code 的行為就跟以前完全一樣：只讀 CLAUDE.md，不會去讀 AGENTS.md。** 這是 v2.1.277（2026-09-18 發布）之前唯一的行為，也是 v2.1.277 之後、有 CLAUDE.md 時的預設行為：若專案已經有 `AGENTS.md`（例如同時給 Codex 用）但還沒有 `CLAUDE.md`，官方原本建議建一個 `CLAUDE.md` 用 `@AGENTS.md` 匯入它，下面再加 Claude 專屬指示，這個做法現在仍然可用[1]。

!!! note "v2.1.277 起（2026-09-18）：專案完全沒有 CLAUDE.md 時，Claude Code 才會直接讀 AGENTS.md"
    官方 changelog 原文：「Added AGENTS.md support: in a project with no CLAUDE.md, Claude Code reads AGENTS.md instead; change it under "Project instructions" in `/config`」[^fresh1][9]。

    判定範圍是工作目錄本身加上它的所有上層目錄，官方原文：「Claude reads AGENTS.md only when you have no CLAUDE.md in your working directory or above it.」其中任何一層有 `CLAUDE.md`、`.claude/CLAUDE.md` 或 `CLAUDE.local.md`，就不會觸發讀取 `AGENTS.md`[1]。

    兩者都存在時，預設值 `claude-md-or-agents-md` 只讀 `CLAUDE.md`；要兩個都讀，得到 `/config` 把「Project instructions」改成 `claude-md-and-agents-md`（每個目錄先讀 `CLAUDE.md` 再讀 `AGENTS.md`，兩者都載入）。另外兩個選項是 `claude-md`（只讀 `CLAUDE.md`，等於關掉這個新功能）與 `managed-only`（只讀組織 managed CLAUDE.md 與 auto memory，連使用者層、專案層 `CLAUDE.md` 都不讀）[1]。

    使用者層 `~/.claude/CLAUDE.md`、組織的 managed CLAUDE.md、`.claude/rules/` 都不算進判定範圍，會跟 `AGENTS.md` 一起載入。子目錄裡的 `AGENTS.md`，只在 Claude 用 Read 工具讀到該子目錄底下的檔案、且那個子目錄自己沒有上述三種 `CLAUDE.md` 檔時才會載入。以前官方建議的 `@AGENTS.md` 匯入語法仍然可用，官方明講「Keeping the import never makes Claude read AGENTS.md twice」，不會被重複讀取[1]。

    因為 `CLAUDE.local.md` 也算數，在一個靠 `AGENTS.md` 的專案裡加一份 `CLAUDE.local.md` 放自己不 commit 的指示，Claude 就不會再替你讀 `AGENTS.md`[1]。`AGENTS.local.md`、`AGENTS.override.md` 和 `.agents/` 資料夾底下的東西都不讀[1]。

    想讓所有工具共用同一份 `AGENTS.md`，在旁邊的 `CLAUDE.md` 寫 `@AGENTS.md` 匯入，Claude 專屬的指示寫在匯入那行下面，Claude 會先讀匯入的檔案再讀其餘內容[1]。改用 symlink 有兩個限制。Windows 上建 symlink 要系統管理員權限或開發人員模式，所以 repo 有人用 Windows 時，官方建議用匯入；另外 Claude 能透過連結讀 `CLAUDE.md`，但 Edit 和 Write 工具不會寫穿 symlink[1]。從其他工具搬過來時，`/import` 會把 `AGENTS.md` 這類指示檔一次性附加到對應的 `CLAUDE.md`，也會帶過 MCP server、指令、subagent 和 skill[1]。

    不支援這個新行為的情況：v2.1.277 之前的版本；v2.1.281 之前版本上的部分 session（例如用 Amazon Bedrock，或停用了 telemetry）[^fresh2]；升級後的第一個 session（下一個 session 才生效）；設了 `disableAllHooks` 或 `allowManagedHooksOnly`，或在 `/plugin` 停用了內建的 `agents-md` plugin。這些情況下 `/config` 裡也不會出現「Project instructions」這個設定項[1]。

    **最小檢查步驟**：想確認自己目前讀的是哪個檔案，跑 `/config` 看「Project instructions」目前設什麼值；或看 session 開頭有沒有出現類似「no CLAUDE.md found; AGENTS.md loaded: ...」的提示行。直接讀取的 `AGENTS.md` 從 v2.1.280 起會列在 `/memory` 清單裡，跑 `/memory` 找它的路徑即可；v2.1.280 之前的版本 `/memory` 與 `/context` 都不會列出它，這時官方建議改問 Claude「你的 project instructions 寫什麼」來確認[^fresh3][1]。

## 二、`.claude/rules/`：把 CLAUDE.md 拆成主題檔

`.claude/rules/` 是把 CLAUDE.md 內容拆成多個主題檔的機制，適合大型專案：每個檔案專注一個主題，`.md` 檔會遞迴掃描子目錄。沒有 `paths` frontmatter 的 rule，會在啟動時整份載入，優先度跟 `.claude/CLAUDE.md` 相同；官方的區分方式是：全程都要在上下文裡的規則用 rules，不需要一直佔上下文、只在特定任務才用得到的工作方式則建議改用 skill[1]。

要把規則限定在特定檔案類型才生效，用 YAML frontmatter 的 `paths` 欄位：

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API Development Rules

- All API endpoints must include input validation
- Use the standard error response format
```

只有 Claude 用 Read、Write 或 Edit 工具處理符合 `paths` 模式的檔案時才會觸發載入這份規則[^fresh4]，不是每次工具呼叫都觸發[1]。使用者層 `~/.claude/rules/` 對每個專案都生效，且會在專案層 rule 之前先載入[1]。兩邊誰也不蓋過誰，使用者層和專案層的規則衝突時，Claude 可能照任一條做，所以要自己讓兩邊一致[1]。

`paths` 是 Claude Code 從規則檔讀的唯一欄位，其他欄位會被忽略，也不報錯[1]。它可以寫成 YAML 清單，也可以寫成逗號分隔的字串；frontmatter 的 YAML 解析失敗時，Claude Code 會忽略整段 frontmatter，把這份規則當成沒有 `paths` 的規則載入[1]。跟 CLAUDE.md 一樣，規則檔是 Claude 讀的指引，不是 Claude Code 強制執行的設定[18]。

規則要放在各目錄自己的 CLAUDE.md，還是集中寫成有 `paths` 的規則檔，官方的分法如下[14]：

| 做法 | 放在哪 | 什麼時候載入 | 適合 |
|---|---|---|---|
| 各目錄的 CLAUDE.md | 該目錄裡，跟程式碼放一起 | 從那個目錄啟動時，或用到時 | 各目錄的負責人自己維護慣例，指示跟著程式碼一起版控 |
| `.claude/rules/` 裡有 `paths` 的規則 | repo 根目錄的 `.claude/` | Claude 處理符合 `paths` 的檔案時 | 想把所有慣例集中一處，或同一條規則適用很多分散的路徑 |

!!! warning "已知限制：`paths` 在部分版本可能不生效"
    GitHub 上有多筆社群回報的 issue，指出 `paths` frontmatter 在特定版本、特定情境（例如使用者層 rule、或由 Write 觸發而非 Read 觸發時）不生效或行為跟文件描述不符。這些是社群回報的 bug 追蹤，不是官方文件本體的承諾內容；本站查證時（2026-09-16）未能確認這些 issue 目前的修復狀態對應到哪個確切版本號。如果你設定了 `paths` 卻發現規則沒被載入，先確認自己的版本號，再去查目前官方 issue tracker 的最新狀態，不要預設是自己語法寫錯了。

    官方 `docs/en/memory` 另外記載了幾個與 `paths` 相關、已標明修復版本的具體缺陷，可以拿來先對一下自己的版本號：symlink 路徑比對到 v2.1.198 才支援、無效的 glob pattern 曾在 v2.1.207 之前讓 Read 工具對該規則涵蓋的所有檔案失敗、`--setting-sources` 排除 `project` 時仍載入部分規則的問題到 v2.1.211 修正、brace 展開過多曾在 v2.1.217 之前讓 CLI 啟動卡住或崩潰[1]。這幾個是文件明確記載的修復點，跟上面列的社群 issue 是不同的兩份清單，沒有一一對應關係。

## 三、settings.json：五層優先序

官方定義的設定來源，由高到低共五層[2]：

| 優先序 | 來源 | 檔案 | 適合放 |
|---|---|---|---|
| 1（最高） | Managed settings | `managed-settings.json`／MDM／console 的 server-managed settings | 組織強制的安全政策，個人無法覆蓋（少數安全 key 例外） |
| 2 | Command line | `claude --settings '{...}'` | 只在這次啟動生效的臨時設定 |
| 3 | Project local | `.claude/settings.local.json` | 個人在這個專案的設定，自動排除版控 |
| 4 | Shared project | `.claude/settings.json` | 團隊共用，走版控 |
| 5（最低） | User | `~/.claude/settings.json` | 個人跨專案設定 |

「同一個 key 在多處出現，採用優先序最高那層的值」是一般規則，但**清單型 key 例外**：像 `permissions.allow` 這種清單，多處設定會**合併**而非互相覆蓋，每個檔案都可以各自新增規則[2]。少數安全性 key（例如 `disableClaudeAiConnectors`、`isolatePeerMachines`）則反過來，只要任一層設成更嚴格的值就會被採用，即使 managed 設定更寬鬆[2]。

幾個容易搞混的地方[2]：

- **路徑寫法**：`~/.claude` 指家目錄底下的 `.claude` 資料夾，只寫 `.claude` 指專案裡的那個。Windows 上 `~/.claude` 就是 `%USERPROFILE%\.claude`。想把家目錄這些檔案放到別處，設 `CLAUDE_CONFIG_DIR`，設定、session 紀錄和 plugin 都會改存到那裡。
- **檔案不會自己出現**：安裝 Claude Code 不會建立任何設定檔。第一次在 `/config` 改了存在使用者設定的選項（例如主題），才會寫出 `~/.claude/settings.json`；第一次在權限提示給了長期核准（例如對某個 Bash 指令選「Yes, and don't ask again」），才會寫出 `.claude/settings.local.json`。
- **第五個檔案 `~/.claude.json`**：這是 Claude Code 自己寫給自己用的，你不用改。裡面有登入狀態、MCP server 設定、各專案的狀態（例如信任決定），還有 `/config` 替你寫的全域設定。
- **local 檔怎麼避開版控**：Claude Code 第一次在一個還沒忽略它的 git repo 裡寫 `.claude/settings.local.json` 時，會把 `**/.claude/settings.local.json` 加進你的全域 git excludes 檔，之後每個 repo 都不會 commit 到它。自己手動建的檔，Claude Code 還沒寫過的話，要自己加進 `.gitignore`。
- **共用檔要 commit 才算共用**：`.claude/settings.json` 要 commit 進版控，隊友的 clone 和雲端 session 才拿得到。隊友想要個人例外，寫在自己的 `.claude/settings.local.json`，不用 commit。
- **`--settings` 只管這一次**：它蓋過專案與使用者設定檔裡同名的 key，沒寫到的 key 照用檔案裡的值。使用者設定檔能設的 key 它都能設，Managed 和全域 config 的 key 則不行。它只維持一個 session，不寫進任何檔案。`--model` 這類其他旗標只設定這次 session 的單一項目，不屬於五層堆疊。
- **環境變數不算一層**：例如 shell 匯出的 `ANTHROPIC_MODEL` 會蓋過任何檔案裡的 `model`，`ANTHROPIC_DEFAULT_MODEL` 則只在沒有檔案設定 `model` 時才生效。
- **改了什麼時候生效**：Claude Code 會盯著設定檔，一改就重新載入，多數修改不用重開就套用到目前的 session。有些 key 只在 session 開始時讀一次，改了要等下一個 session。
- **看實際載入了哪些**：在 Claude Code 裡跑 `/status`，Status 分頁的 Setting sources 一行會列出這次 session 載入的每個設定檔。
- **雲端 session**：只讀 repo 裡的 `.claude/settings.json`（session 只有一個 repo 時）。你電腦上的 `~/.claude/settings.json` 和 `.claude/settings.local.json` 都不會讀，因為兩個都留在你的電腦上，local 檔也不在 clone 裡。

## 四、權限：allow／ask／deny 與 permission mode

### 規則語法與評估順序

規則格式是 `Tool` 或 `Tool(specifier)`，例如：

```json
{
  "permissions": {
    "allow": ["Bash(npm run *)", "Bash(git commit *)"],
    "deny": ["Bash(git push *)"]
  }
}
```

**評估順序固定是 deny 先、再 ask、再 allow，同一順序內先比對到就先套用，規則寬窄不影響順序**[3]。這意味著一條寬的 deny 規則會擋掉所有符合的呼叫，就算另外寫了更精確的 allow 規則也開不了例外。官方也提醒 wildcard 位置：`*` 要放在子指令之後，`Bash(git log *)` 只允許 `git log` 系列指令，`Bash(git *)` 才是允許所有 git 指令[3]。

### permission mode：六種，`Shift+Tab` 只切三種

官方目前列出**六種** permission mode，不是坊間常聽到的四種；`Shift+Tab` 的預設循環只切換其中三種，其他模式要另外用旗標或設定啟用[4]。**Claude Code v2.1.283 起，終端機與 VS Code 互動 session 的內建起始模式是 `auto`**；更早的版本只有 Pro／Max／Team 方案是 `auto`，其他方案才是 `default`（Manual）[^fresh5][4]：

| 模式 | 說明 | 在 `Shift+Tab` 循環裡嗎 |
|---|---|---|
| `default`（UI 標示 Manual） | 只有讀取類動作（讀檔、Grep 等）不用問；其餘工具每次都會問，不是「第一次問完就自動放行」——除非你自己在提示框選過「Yes, and don't ask again」，那條規則才會存下來（存法依工具類型而異：Bash 指令與 WebFetch 網域是永久存進該 repo 的規則，檔案編輯只到這個 session 結束為止）[3] | 是（循環起點） |
| `acceptEdits` | 自動接受檔案編輯與常見檔案系統指令（`mkdir`、`mv` 等） | 是 |
| `plan` | 只讀檔、跑唯讀指令做研究，不編輯原始檔 | 是 |
| `auto` | 自動核准工具呼叫，背後由分類器模型做安全檢查 | auto mode 對目前 session 可用時才加入（官方列的方案條件已是所有方案）[^fresh6] |
| `dontAsk` | 原本會詢問的呼叫全部自動拒絕 | 不會，需另外設定 |
| `bypassPermissions` | 跳過權限詢問（含對 `.git`、`.claude` 等受保護路徑的寫入） | 預設不在循環裡，須先用旗標或設定啟用，啟用後插在 `plan` 之後 |

官方對 `bypassPermissions` 的警告原文：「Only use this mode in isolated environments like containers, VMs, or dev containers without internet access, where Claude Code cannot damage your host system.」[4] 更完整的 agent 迴圈與 Codex 沙箱模式對照，見[AI Agent 怎麼運作](agent-basics.md)第三節。

### sandbox：另一層 OS 層邊界

`/sandbox` 是 Claude Code 內建的 OS 層隔離，限制 Bash／PowerShell 指令的檔案系統與網路存取，跟 permission rules 是互補的兩層：permission rules 在工具執行前判斷「能不能用」，sandbox 是對「已經在執行的行程」做作業系統層的邊界，不管模型選擇跑什麼指令都會被擋下[5]。支援平台是 macOS（內建）與 Linux／WSL2（需裝 `bubblewrap` 與 `socat`），原生 Windows 不支援[5]。官方也提醒，靠 Bash 規則比對指令文字本身很脆弱（例如 deny `curl` 擋不住 `/usr/bin/curl`），真正的邊界要靠 sandbox 或 `WebFetch(domain:...)` 這類白名單機制[3][5]。

## 五、官方沒公開的東西：system prompt

**官方明確表示 system prompt 沒有公開全文。** 原文：「Claude Code's system prompt isn't published. To give Claude standing instructions, use CLAUDE.md files or the `--append-system-prompt` flag.」[2] 本頁不引用、也不轉述任何非官方管道流出的版本，只列官方公開、可以拿來調整 Claude 行為的介面：

| 方式 | 作用機制 | 適用情境 |
|---|---|---|
| **CLAUDE.md** | 以系統提示詞之後的一則訊息形式注入，不改動系統提示詞本身 | 想讓 Claude 一直記得專案慣例 |
| **`--append-system-prompt`** | 附加到系統提示詞尾端，不移除原有內容 | 啟動時加一次性補充指示 |
| **`--system-prompt`** | 完全取代預設系統提示詞 | 需要完全自訂角色，但要自己補齊工具指引與安全規則 |
| **Output styles** | 改變 Claude Code 給模型的預設指示，套用到每一次回應 | 想固定改變角色、語氣、輸出格式，且要重複用在多個 session |

自訂 output style 是一個放在 `~/.claude/output-styles`（使用者層）或 `.claude/output-styles`（專案層）的 Markdown 檔，`keep-coding-instructions: true` 決定要不要保留內建的軟體工程指示（預設不保留，適合完全換角色的情境，例如寫作助手）[7]。用 `--system-prompt` 完全取代時，預設工具是否保留、內建安全規則是否保留、環境背景資訊是否自動帶入，這三項都**不再自動維持，要自己補上**[8]。

## 六、auto memory：Claude 自己寫的筆記

CLAUDE.md 是你寫的，auto memory 是 Claude 依你的糾正和偏好自己寫的筆記，兩者都在每次對話開始時載入[1]：

| | CLAUDE.md | auto memory |
|---|---|---|
| 誰寫 | 你 | Claude |
| 內容 | 指示與規則 | 學到的事和模式 |
| 範圍 | 專案、使用者或組織 | 每個 repo 一份，同 repo 的 worktree 共用 |
| 載入 | 每個 session | 每個 session（前 200 行或 25KB） |
| 適合放 | 程式碼規範、工作流程、專案架構 | 你的偏好、你給 Claude 的糾正、從程式碼推不出來的專案背景 |

Claude 存的筆記分四類，寫在記憶檔 frontmatter 的 `type` 欄位：`user`（你的角色、專長、工作偏好）、`feedback`（你給的糾正和你認可的做法）、`project`（進行中的工作、期限、從程式碼或 git 紀錄推不出來的決定）、`reference`（專案外的資訊去哪裡找，例如 issue tracker 或 dashboard）[1]。從 codebase 推得出來的東西不存，例如架構、檔案路徑、除錯的修法；CLAUDE.md 已經寫的也不存。Claude 也不是每個 session 都存，它看這個資訊對之後的對話有沒有用來決定[1]。

- **存在哪**：每個專案一個資料夾，在 `~/.claude/projects/<project>/memory/`。`<project>` 從 git repo 推出來，同一個 repo 的所有 worktree 和子目錄共用一份；不在 git repo 裡就用專案根目錄[1]。裡面有一份 `MEMORY.md` 索引，每筆記憶一行，另外每筆記憶一個主題檔[1]。想換位置，在 `settings.json` 設 `autoMemoryDirectory`，值要是絕對路徑或以 `~/` 開頭[1]。
- **載入多少**：每次對話開始載入 `MEMORY.md` 的前 200 行或前 25KB，以先到者為準，超過的部分不載入[1]。`user_role.md` 這類主題檔啟動時不載入，Claude 需要時才用一般的檔案工具去讀[1]。索引超過上限時寫入照樣成功，但 Claude Code 會回錯誤要 Claude 重寫索引，因為超過的部分下次載入會被丟掉[1]。這個上限只管 `MEMORY.md`，CLAUDE.md 是 4 MiB 以內整份載入[1]。
- **只在這台電腦**：auto memory 不會跨機器或雲端環境共用。`MEMORY.md` 和主題檔會一直留著，直到你或 Claude 修改或刪除[1]。
- **開關**：本機 session 預設開啟。在 `/memory` 裡切換，會把 `autoMemoryEnabled` 存進 `~/.claude/settings.json`；只想對一個專案關掉，在那個專案的設定裡設 `autoMemoryEnabled`；也可以用環境變數 `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` 關掉[1]。背景 session，以及另一個 Claude Code session 啟動的 session（例如 Claude 用 Bash 工具跑 `claude`），這個開關只能關、不能再打開[1]。
- **看得到它在做什麼**：介面出現「Saved 2 memories」或「Recalled 2 memories」這類訊息，就是 Claude 正在寫入或讀取記憶資料夾[1]。記憶檔都是一般 Markdown，隨時可以改或刪；跑 `/memory` 選 auto memory 資料夾就能瀏覽[1]。`/memory` 也會列出使用者層和專案層所有 CLAUDE.md 的位置，包括還沒建立的[1]。
- **叫 Claude 記，和叫它寫進 CLAUDE.md 不一樣**：你說「記住一律用 pnpm」，Claude 會存進 auto memory。要寫進 CLAUDE.md，直接說「add this to CLAUDE.md」，或自己用 `/memory` 開檔改[1]。
- **subagent 不帶主對話的記憶**：主對話的 auto memory 不會載入 subagent，只有 fork 例外，因為 fork 繼承整段對話和 system prompt。subagent 用 `memory` 欄位開的 auto memory 是另一個資料夾[1]。

## 七、CLAUDE.md 沒照做時怎麼查

先跑 `/context`。它把目前 session 佔用 context 的東西分類列出來，包括 system prompt、工具、MCP 工具、自訂 subagent、記憶檔、skill 和對話訊息，可以先確認你的 CLAUDE.md、規則檔或 skill 說明到底有沒有載入[12]。啟動時該載入的 CLAUDE.md 和 `CLAUDE.local.md` 列在 Memory files 底下，不在那裡的 Claude 就看不到[1]。子目錄的 CLAUDE.md 是用到才載入，所以不會出現在 Memory files；它載入時終端機會出現一行 Loaded 和它的路徑。想測一份新的，從 shell 建檔，不要叫 Claude 寫，再請 Claude 讀那個子目錄裡的一個檔案[1]。

`/context` 確認載入了、Claude 還是不照某條指示做，問題多半出在寫法，不在有沒有載入[12]。指示模糊到有多種解讀、兩個檔案講法衝突、檔案長到每條規則分到的注意力變少，遵守度都會下降[12]。也要看看你的指示是不是跟 Claude Code 自己加的指引互相競爭[1]。

其他工具[12][16]：

| 工具 | 看什麼 |
|---|---|
| `/memory` | 使用者層和專案層記憶檔的位置，可以逐一開檔編輯，也能進 auto memory 資料夾和切換開關 |
| `/doctor` | 安裝狀態、無效的設定檔、沒用到的擴充、同一個目錄裡重名的 subagent，以及 commit 進 repo 的 CLAUDE.md 裡從 codebase 推得出來的內容，並提出修法 |
| `/status` | 目前生效的設定來源，包括有沒有 managed settings |
| `claude doctor` | 在終端機跑，不開 session，印出唯讀的安裝與設定診斷，用來找無效的設定檔 |

幾種常見狀況：

- **對話裡出現 Instruction file not loaded**：代表有一份存在的記憶檔沒載入，因為有讀取限制，例如某條 Read deny 規則涵蓋了它，或它在工作目錄以外、讀取被擋[15]。
- **想知道哪些檔案何時載入**：用 `InstructionsLoaded` hook 記錄每份 CLAUDE.md 和規則檔載入的時間與原因，查有 `paths` 的規則或子目錄裡延遲載入的檔案特別有用[1]。
- **subagent 不照 CLAUDE.md**：內建的 Explore 和 Plan 啟動時不載入 CLAUDE.md；自訂 subagent 跟主對話一樣載入，除非定義裡設了 `omitClaudeMd`[12]。
- **AGENTS.md 沒讀到**：最常見的原因是專案路徑上某處有 CLAUDE.md[1]。先跑 `claude --version` 確認 v2.1.277 以上，再跑 `/memory` 看清單裡有沒有它的路徑；v2.1.280 之前的版本，`/memory` 和 `/context` 不會列出直接讀取的 `AGENTS.md`[1]。
- **CLAUDE.md 太大**：超過 200 行會吃更多 context，遵守度也可能下降，超過 4 MiB 的檔案直接跳過[1]。每份都在建議長度內、加起來卻超過合計上限時，啟動時也會跳警告；每份 CLAUDE.md、規則檔和 `@path` 匯入都各算一份[1]。
- **懷疑是自己的設定造成的**：用 `claude --safe-mode` 啟動，停掉你的自訂設定再試。問題消失，就知道原因在被停掉的那些東西裡[12]。safe mode 仍會套用組織的 managed hook 和設定政策[12]。另一種做法是把 `CLAUDE_CONFIG_DIR` 指到一個全新的資料夾取代 `~/.claude`，再加 `--setting-sources user` 關掉 `.claude/settings.json`、CLAUDE.md、`.mcp.json` 這些專案設定[12]。

### 壓縮之後哪些還在

還沒打任何字之前，CLAUDE.md、auto memory、MCP 工具名稱和 skill 說明就已經載入 context[13]。

想知道自己的設定一開場佔了多少，跑 `/context`，會依類別列出目前實際的用量[13]。官方的示意圖用的是代表性數字，實際數字以這個指令為準[13]。

下面是一台機器上的單次讀數（Claude Code 2.1.310，以非互動的 `claude -p "/context"` 讀取）。一般設定的起始用量約 33.7k tokens；改用空的設定資料夾，並在沒有任何 CLAUDE.md 的目錄啟動，約 19k。互動 session 和專案目錄還會再加上專案的 CLAUDE.md 與 hook 注入的內容。這只是這台機器的讀數，別人的 CLAUDE.md、skill、MCP 設定不同，數字也會不同。

對話長了被壓縮（compact）時，各機制的下場不同[13]：

| 內容 | 壓縮之後 |
|---|---|
| 專案根目錄的 CLAUDE.md、沒有 `paths` 的規則檔 | 從磁碟重新注入 |
| auto memory | 從磁碟重新注入 |
| 有 `paths` 的規則檔 | 用到時重新載入 |
| 子目錄裡的 CLAUDE.md | 用到時重新載入 |

有 `paths` 的規則檔和子目錄的 CLAUDE.md，是在 Claude 讀寫觸發它們的檔案時進到對話紀錄的，所以壓縮時會跟其他內容一起被摘要掉。規則一定要撐過壓縮的話，拿掉它的 `paths`，或搬進專案根目錄的 CLAUDE.md[13]。壓縮後某條指示不見了，原因通常是它只在對話裡講過、在還沒重新載入的子目錄 CLAUDE.md 裡，或是一條之後還沒比對到檔案的 `paths` 規則。只在對話裡講的指示，要寫進 CLAUDE.md 才會留下來[1]。

## 本頁重點回顧

- CLAUDE.md 分四層、全部串接進上下文；官方判準是「拿掉這行會不會讓 Claude 犯錯」，答不出來就刪或搬進 skill。
- v2.1.277 起（2026-09-18），完全沒有 CLAUDE.md 的專案會直接讀 AGENTS.md；有 CLAUDE.md 就跟以前一樣不會去讀，`/config` 的「Project instructions」可以改成同時讀兩者。
- `.claude/rules/` 是拆分 CLAUDE.md 的機制，`paths` frontmatter 限定生效範圍，但有查無修復狀態的已知 bug，遇到規則沒生效先查版本號。
- settings.json 五層優先序，managed 最高、user 最低；清單型 key 是合併而非覆蓋。
- 權限規則永遠 deny 先評估；permission mode 有六種，`Shift+Tab` 只切三種。
- system prompt 官方未公開全文，只能透過 CLAUDE.md、`--append-system-prompt`、`--system-prompt`、output styles 這幾個公開介面間接調整。
- auto memory 是 Claude 自己寫的筆記，每次只載入 `MEMORY.md` 前 200 行或 25KB，只存在這台電腦。
- CLAUDE.md 沒照做，先跑 `/context` 確認有沒有載入；載入了還不照做，多半是寫法問題。只在對話裡講的指示，壓縮後可能不見。

## 資料來源

| 標記 | 來源 | URL |
|---|---|---|
| [1] | How Claude remembers your project（CLAUDE.md、`.claude/rules/`、`/init`、`@import`） | <https://code.claude.com/docs/en/memory> |
| [2] | Settings files and precedence（五層優先序、system prompt 未公開聲明） | <https://code.claude.com/docs/en/settings> |
| [3] | Configure permissions（allow/ask/deny 語法、評估順序、wildcard 警告） | <https://code.claude.com/docs/en/permissions> |
| [4] | Choose a permission mode（六種模式、`Shift+Tab` 循環規則） | <https://code.claude.com/docs/en/permission-modes> |
| [5] | Configure the sandboxed Bash tool（sandbox 模式、平台支援） | <https://code.claude.com/docs/en/sandboxing> |
| [6] | Best practices for Claude Code（CLAUDE.md 篇幅建議） | <https://code.claude.com/docs/en/best-practices> |
| [7] | Output styles（自訂 output style 格式） | <https://code.claude.com/docs/en/output-styles> |
| [8] | Modifying system prompts（Agent SDK，四種自訂方式比較表） | <https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts> |
| [9] | Claude Code changelog（v2.1.277，2026-09-18，AGENTS.md support） | <https://code.claude.com/docs/en/changelog> |
| [10] | Quickstart（帳號、安裝指令、更新、第一次啟動） | <https://code.claude.com/docs/en/quickstart> |
| [11] | Advanced setup（系統需求） | <https://code.claude.com/docs/en/setup> |
| [12] | Debug your configuration（`/context`、`/doctor`、`claude doctor`、safe mode） | <https://code.claude.com/docs/en/debug-your-config> |
| [13] | Explore the context window（開場載入什麼、壓縮後哪些還在） | <https://code.claude.com/docs/en/context-window> |
| [14] | Set up Claude Code in a monorepo or large codebase（啟動目錄、各目錄 CLAUDE.md 與規則檔的取捨） | <https://code.claude.com/docs/en/large-codebases> |
| [15] | Error reference（Instruction file not loaded） | <https://code.claude.com/docs/en/errors> |
| [16] | Commands（`/init`、`/memory`、`/doctor`） | <https://code.claude.com/docs/en/commands> |
| [17] | Extend Claude Code（指示是請求，hook 才是強制） | <https://code.claude.com/docs/en/features-overview> |
| [18] | Explore the .claude directory（規則檔是指引，不是強制設定） | <https://code.claude.com/docs/en/claude-directory> |

延伸：[AI Agent 怎麼運作](agent-basics.md)｜[SKILL、Plugin、MCP 與 Subagent](extensions.md)｜[Hooks 與 Subagent 設定](hooks-subagents.md)

[^fresh1]: 2026-10-05 依官方原文更新，出處：<https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md>
[^fresh2]: 2026-10-05 依官方原文更新，出處：<https://code.claude.com/docs/en/memory>
[^fresh3]: 2026-10-05 依官方原文更新，出處：<https://code.claude.com/docs/en/memory>
[^fresh4]: 2026-10-05 依官方原文更新，出處：<https://code.claude.com/docs/en/memory>
[^fresh5]: 2026-10-05 依官方原文更新，出處：<https://code.claude.com/docs/en/permission-modes>
[^fresh6]: 2026-10-05 依官方原文更新，出處：<https://code.claude.com/docs/en/permission-modes>
