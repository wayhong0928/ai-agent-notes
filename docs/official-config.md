# Claude Code 設定總覽

> 查證日期：2026-09-16。方案與功能變動快，請以官方最新說明為準。

前面幾頁講的是[AI Agent 怎麼運作](agent-basics.md)、[各種擴充機制解決什麼問題](extensions.md)、[怎麼把工作環境設計得可靠](harness.md)——都是原理層。這頁換一個角度，只回答一個問題：**Claude Code 官方文件建議怎麼設定**。內容照官方文件的說法整理，不包含任何個人或特定專案的客製規則；你自己專案要怎麼寫，是另一回事，這頁只負責把官方定義的介面講清楚。

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

**只要工作目錄或其任何上層目錄有 `CLAUDE.md`（含 `.claude/CLAUDE.md`、`CLAUDE.local.md`），Claude Code 的行為就跟以前完全一樣：只讀 CLAUDE.md，不會去讀 AGENTS.md。** 這是 v2.1.277（2026-09-18 發布）之前唯一的行為，也是 v2.1.277 之後、有 CLAUDE.md 時的預設行為：若專案已經有 `AGENTS.md`（例如同時給 Codex 用）但還沒有 `CLAUDE.md`，官方原本建議建一個 `CLAUDE.md` 用 `@AGENTS.md` 匯入它，下面再加 Claude 專屬指示，這個做法現在仍然可用[1]。

!!! note "v2.1.277 起（2026-09-18）：專案完全沒有 CLAUDE.md 時，Claude Code 才會直接讀 AGENTS.md"
    官方 changelog 原文：「Added AGENTS.md support: in a project with no CLAUDE.md, Claude Code reads AGENTS.md instead; change it under "Project instructions" in `/config` (not yet on Bedrock, Vertex or Foundry)」[9]。

    判定範圍是工作目錄本身加上它的所有上層目錄，官方原文：「Claude reads AGENTS.md only when you have no CLAUDE.md in your working directory or above it.」其中任何一層有 `CLAUDE.md`、`.claude/CLAUDE.md` 或 `CLAUDE.local.md`，就不會觸發讀取 `AGENTS.md`[1]。

    兩者都存在時，預設值 `claude-md-or-agents-md` 只讀 `CLAUDE.md`；要兩個都讀，得到 `/config` 把「Project instructions」改成 `claude-md-and-agents-md`（每個目錄先讀 `CLAUDE.md` 再讀 `AGENTS.md`，兩者都載入）。另外兩個選項是 `claude-md`（只讀 `CLAUDE.md`，等於關掉這個新功能）與 `managed-only`（只讀組織 managed CLAUDE.md 與 auto memory，連使用者層、專案層 `CLAUDE.md` 都不讀）[1]。

    使用者層 `~/.claude/CLAUDE.md`、組織的 managed CLAUDE.md、`.claude/rules/` 都不算進判定範圍，會跟 `AGENTS.md` 一起載入。子目錄裡的 `AGENTS.md`，只在 Claude 用 Read 工具讀到該子目錄底下的檔案、且那個子目錄自己沒有上述三種 `CLAUDE.md` 檔時才會載入。以前官方建議的 `@AGENTS.md` 匯入語法仍然可用，官方明講「Keeping the import never makes Claude read AGENTS.md twice」，不會被重複讀取[1]。

    不支援這個新行為的情況：v2.1.277 之前的版本；不會向 Anthropic 抓 feature flag 的環境（例如用 Amazon Bedrock、Vertex、Foundry 等第三方供應商，或停用了 telemetry）；升級後的第一個 session（下一個 session 才生效）；設了 `disableAllHooks` 或 `allowManagedHooksOnly`，或在 `/plugin` 停用了內建的 `agents-md` plugin。這些情況下 `/config` 裡也不會出現「Project instructions」這個設定項[1]。

    **最小檢查步驟**：想確認自己目前讀的是哪個檔案，跑 `/config` 看「Project instructions」目前設什麼值；或看 session 開頭有沒有出現類似「no CLAUDE.md found; AGENTS.md loaded: ...」的提示行。直接讀取的 `AGENTS.md` 不會出現在 `/memory` 或 `/context` 的 Memory files 清單裡（除非是被 `CLAUDE.md` 用 `@AGENTS.md` 匯入進去的），這時官方建議改問 Claude「你的 project instructions 寫什麼」來確認[1]。

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

只有 Claude 讀到符合 `paths` 模式的檔案時才會觸發載入這份規則，不是每次工具呼叫都觸發[1]。使用者層 `~/.claude/rules/` 對每個專案都生效，且會在專案層 rule 之前先載入[1]。

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

官方目前列出**六種** permission mode，不是坊間常聽到的四種；`Shift+Tab` 的預設循環只切換其中三種，其他模式要另外用旗標或設定啟用[4]。**Pro／Max／Team 方案的內建起始模式是 `auto`**，其他方案的內建起始模式才是 `default`（Manual）[4]：

| 模式 | 說明 | 在 `Shift+Tab` 循環裡嗎 |
|---|---|---|
| `default`（UI 標示 Manual） | 只有讀取類動作（讀檔、Grep 等）不用問；其餘工具每次都會問，不是「第一次問完就自動放行」——除非你自己在提示框選過「Yes, and don't ask again」，那條規則才會存下來（存法依工具類型而異：Bash 指令與 WebFetch 網域是永久存進該 repo 的規則，檔案編輯只到這個 session 結束為止）[3] | 是（循環起點） |
| `acceptEdits` | 自動接受檔案編輯與常見檔案系統指令（`mkdir`、`mv` 等） | 是 |
| `plan` | 只讀檔、跑唯讀指令做研究，不編輯原始檔 | 是 |
| `auto` | 自動核准工具呼叫，背後由分類器模型做安全檢查 | 只有這個功能對你的方案可用時才加入 |
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

## 本頁重點回顧

- CLAUDE.md 分四層、全部串接進上下文；官方判準是「拿掉這行會不會讓 Claude 犯錯」，答不出來就刪或搬進 skill。
- v2.1.277 起（2026-09-18），完全沒有 CLAUDE.md 的專案會直接讀 AGENTS.md；有 CLAUDE.md 就跟以前一樣不會去讀，`/config` 的「Project instructions」可以改成同時讀兩者。
- `.claude/rules/` 是拆分 CLAUDE.md 的機制，`paths` frontmatter 限定生效範圍，但有查無修復狀態的已知 bug，遇到規則沒生效先查版本號。
- settings.json 五層優先序，managed 最高、user 最低；清單型 key 是合併而非覆蓋。
- 權限規則永遠 deny 先評估；permission mode 有六種，`Shift+Tab` 只切三種。
- system prompt 官方未公開全文，只能透過 CLAUDE.md、`--append-system-prompt`、`--system-prompt`、output styles 這幾個公開介面間接調整。

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

延伸：[AI Agent 怎麼運作](agent-basics.md)｜[SKILL、Plugin、MCP 與 Subagent](extensions.md)｜[Hooks 與 Subagent 設定](hooks-subagents.md)
