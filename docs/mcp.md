# MCP 入門與實戰

> 查證日期：2026-09-19。方案與功能變動快，請以官方最新說明為準。

[SKILL、Plugin、MCP 與 Subagent](extensions.md)那頁已經把四種擴充機制放進同一張表比較過。這頁只挖 MCP 這一項：它到底是什麼、怎麼在五分鐘內裝好第一個、scope 跟認證怎麼設，以及裝完之後怎麼確認它真的在運作，而不是「設定寫對了、但其實沒連上」。

## 1. MCP 是什麼

MCP（Model Context Protocol）官方的定義是「an open-source standard for connecting AI applications to external systems」，並且用了一個好記的比喻：它是 AI 應用程式的 USB-C 埠，一種標準化的外接方式，不屬於任何一家公司的專屬協定 [1]。

一個 MCP server 對外提供三種原語：

- **tools**：可以執行的動作
- **resources**：可以讀取的資料
- **prompts**：預先設計好的提示樣板

這三種原語的分工，[extensions.md](extensions.md#mcp)已經整理過對應範例，這裡不重複。

**連線方式（transport）目前有兩種現行標準**[2]：

| Transport | 運作方式 |
|---|---|
| stdio | client 啟動一個子行程，透過標準輸入輸出、以換行分隔的 JSON-RPC 訊息通訊，適合本機工具 |
| Streamable HTTP | 每則訊息是對單一 MCP endpoint 的 HTTP POST，回覆用一般 JSON 物件或該次請求專屬的 SSE 串流，適合遠端伺服器 |

還有一種**獨立的舊式 HTTP+SSE transport，已經正式列入棄用**。MCP 2026-07-28 版規格的 changelog 寫明：「Reclassify the HTTP+SSE transport (deprecated since protocol version 2025-03-26) as Deprecated under the feature lifecycle policy... Migrate to Streamable HTTP.」也就是說它早在 2025-03-26 版就已經軟性棄用，2026-07-28 版才正式進入受「至少 12 個月棄用期」保護的 Deprecated 清單，目前還沒到 Removed，但新設定不該再選它 [3]。對應到 Claude Code，`claude mcp add --transport sse` 指令仍然存在，官方文件寫明「The SSE (Server-Sent Events) transport is deprecated. Use HTTP servers instead, where available.」舊 server 還相容，但新設定一律建議用 `--transport http` [4]。

!!! note "host／client／server 三層術語，這裡沒有逐字查證官方定義"
    MCP 官方 introduction 頁沒有逐字定義 host／client／server 這三層術語，只點出「AI applications like Claude or ChatGPT can connect to data sources... tools... and workflows」這種連接關係，也就是應用程式（host，內含 client）連到外部 server。精確的逐字定義在 `architecture` 頁，本次查證沒有逐字讀過那頁，這裡先用上面這個整理過的說法，不掛官方逐字引用的信心等級。

## 2. 五分鐘裝好第一個

以 [context7](https://github.com/upstash/context7)（遠端 HTTP，免安裝任何本機依賴）做示範，官方文件裡 Claude Code 的遠端連法是這一條 [16]：

```bash
claude mcp add --scope user --header "Authorization: Bearer YOUR_API_KEY" --transport http context7 https://mcp.context7.com/mcp
```

三步驟裝好、驗證：

1. **執行 add 指令**。官方原文提醒：「`claude mcp add` confirms a successful add by printing an `Added ...` line」。這只代表設定寫進去了，**不代表連得上** [5]。
2. **跑 `claude mcp list`**，確認狀態變成 `✔ Connected`。第一次連線如果要下載套件（例如本機 stdio 型的伺服器），官方提示大意是：`npx` 還在下載套件時，可能先顯示 `✘ Failed to connect`，等一下重跑就會變成 `✔ Connected`，不用當成裝壞了 [6]。
3. **進 session 實際叫 Claude 呼叫一次工具**，而不是只看連線狀態就收工。工具呼叫在輸出裡會標上伺服器名稱與動作名，這是確認「答案真的來自這個 MCP 工具、不是 Claude 憑記憶回答」的關鍵一步。MCP 只解決「有沒有真的東西可以查」，不保證代理不會答錯或選錯工具 [6][14]。

連不上的時候，先用 `claude mcp get <name>` 看詳細狀態；HTTP 伺服器可以額外用 `curl -I <url>` 手動戳一次（PowerShell 要用 `curl.exe`，不是被別名成 `Invoke-WebRequest` 的 `curl`），stdio 伺服器則直接在終端機手動跑一次同樣的指令，看是缺 Node.js、缺瀏覽器，還是漏了 `--` 分隔符導致指令被錯誤解析 [6]。不想留著的話 `claude mcp remove <name>` 即可移除 [5]。

context7 的 API key 是**選填**。同一份官方文件在另一個客戶端（OpenClaw）的段落寫「This works without an API key at the anonymous rate limit」，Claude Code 的段落本身沒有提到匿名存取；不過兩者連的是同一個伺服器端點，整理者實測把上面指令裡的 `--header` 那段拿掉、只留 `claude mcp add --transport http context7 https://mcp.context7.com/mcp`，`claude mcp get context7` 一樣顯示 `✔ Connected`，只是走匿名速率限制；要拿到更高的速率限制、或存取私有 repository，才需要去 context7.com/dashboard 申請 key，照官方寫法用 `--header "Authorization: Bearer YOUR_API_KEY"` 帶進去 [16]。

## 3. scope 怎麼選

`claude mcp add` 有三層 scope，差在存放位置跟誰看得到 [5]：

| Scope | 存放位置 | 誰看得到 | 用途 |
|---|---|---|---|
| `local`（預設） | `~/.claude.json` 內該專案的條目 | 只有你、只有這個專案 | 個人開發用、不想進版控的憑證 |
| `project` | 專案根目錄 `.mcp.json` | clone 這個 repo 的每個人 | 團隊共用，建議進版控 |
| `user` | `~/.claude.json` 頂層 `mcpServers` | 只有你、跨所有專案 | 個人常用工具 |

官方建議把 `project` scope 的 `.mcp.json` 進版控：「Check `.mcp.json` into version control so everyone on your team gets the same MCP tools and services.」團隊成員第一次啟動時會被要求核准（畫面顯示 `⏸ Pending approval`），核准清單可以用 `claude mcp reset-project-choices` 重置 [5]。

同名伺服器在多層都有設定時，官方原文講得很明確：「When the same server is defined in more than one place, Claude Code connects to it once, using the definition from the highest-precedence source. The entire server entry from that source is used; fields are not merged across scopes.」優先序由高到低是 local → project → user → plugin 提供的 server → claude.ai connector；組織用 `managedMcpServers` 推送的設定又高於以上所有層級（v2.1.259 起）[5]。

## 4. OAuth 認證

Claude Code 會在伺服器回應 `401`／`403` 時判定它需要認證，`claude mcp list` 的狀態欄會顯示 `! Needs authentication`。互動模式下用 `/mcp` 選那台伺服器、按「Authenticate」會開瀏覽器完成登入，憑證存進系統 keychain（macOS）或憑證檔（其他平台）[5]。

命令列版本（v2.1.186 起）可以直接跑：

```bash
claude mcp login <name>
```

沒有瀏覽器的環境（SSH、WSL、headless 主機）加 `--no-browser`，指令會印出授權網址，手動貼到瀏覽器完成登入再貼回終端機。伺服器如果不支援 Dynamic Client Registration，也可以用 `--client-id`／`--client-secret`／`--callback-port` 帶進事先登記好的 OAuth 憑證 [5]。

## 5. MCP 的成本與限制

裝 MCP 不是零成本，這裡列三件常被忽略的事。

**多裝幾台伺服器，context 成本不大，但不是零**：官方原文「Tool search keeps MCP context usage low by deferring tool definitions until Claude needs them. Only tool names and server instructions load at session start, so adding more MCP servers has minimal impact on your context window.」也就是說，每台伺服器完整的工具定義要等 Claude 真的需要時才載入，開場只佔工具名稱和伺服器說明。官方也說沒有「每台伺服器最多幾個工具」的固定上限，實際限制是你的 context 預算。Tool search 預設就是開啟的，例外是用自訂 `ANTHROPIC_BASE_URL`（非官方主機）、設了 `ENABLE_TOOL_SEARCH=false`、或少數雲端平台上的舊模型，這些情況會改成開場就載入全部工具定義，這時候裝太多伺服器才會明顯吃掉 context。用不到的伺服器還是建議移除，這是整理者的建議，不是官方原文 [5][6]。

**單次工具輸出與逾時各有各的上限**：`MAX_MCP_OUTPUT_TOKENS` 是單次 MCP 工具輸出的 token 上限，預設 25,000，超過 10,000 會先跳警告；超過上限又沒有圖片內容時，Claude Code 會把結果存成檔案，對話裡改顯示檔案路徑。`MCP_TOOL_TIMEOUT` 是單次工具呼叫的逾時設定，跟輸出上限是各自獨立的環境變數，沒設定時預設約 28 小時；也可以在 `.mcp.json` 裡替單一伺服器加 `timeout` 欄位（單位毫秒），只對那台伺服器生效 [5]。

**Claude.ai Free 方案限 1 個自訂 connector**：完整對照表見[免付費區](free-tier.md)，這裡不重複；規劃工作流程前先確認帳號方案，免費帳號想同時接文獻庫、雲端硬碟、資料庫這類多 connector 需求會卡在這一條。

## 6. MCP 還是 Skill：什麼時候該用哪個

這題[extensions.md](extensions.md)已經給過決策清單，這裡只抽最相關的一條判準：「需要接觸目前工具箱之外的東西嗎？（例如查公司內部資料庫、讀 Google Drive 裡的檔案）需要 → MCP」[14]。反過來說，如果 Claude 現有的 Read/Write/Bash/WebFetch 已經涵蓋得了，就不需要 MCP，寫成 Skill 或 CLAUDE.md 規則就夠了。

!!! tip "MCP 不解決幻覺"
    裝了 MCP 不代表代理就不會答錯。extensions.md 提醒過這個常見誤用：「MCP 只解決『有沒有真的東西可以查』的問題，代理仍然可能查了卻答錯，或者選錯了要查的工具」。接上文獻庫之後，還是要核對它真的引用了查到的內容，不是引用了憑空生成的內容 [14]。

## 7. 安全

`code.claude.com/docs/en/mcp` 頁面在「Find and build MCP servers」段落有明文警告：「Verify you trust each server before connecting it. Servers that fetch external content can expose you to prompt injection risk.」[6]

`code.claude.com/docs/en/security` 的 MCP 安全專節講得更直白：「Claude Code allows users to configure Model Context Protocol (MCP) servers... We encourage either writing your own MCP servers or using MCP servers from providers that you trust... Anthropic reviews connectors against its listing criteria before adding them to the Anthropic Directory, **but does not security-audit or manage any MCP server**.」重點是最後一句：收錄進 Anthropic Directory 只代表通過上架審核標準，**不是安全掛保證** [15]。

同一頁針對 prompt injection 給了五點「跟不信任內容互動」的建議：核准前先看指令、不要把不信任內容直接 pipe 給 Claude、關鍵檔案的改動要人工核對、跟外部 web 服務互動時考慮用虛擬機隔離、發現可疑行為用 `/feedback` 回報 [15]。這些建議不是專門寫給 MCP，但「會爬外部內容的 server 就是常見的注入來源」這句直接點名了愛爬網頁、讀外部文件的工具型 MCP server。

權限規則的寫法是 `mcp__<servername>__<toolname>`；來自 plugin 打包的 MCP server 語法更長，是 `mcp__plugin_<plugin-name>_<server-name>__<tool-name>`（非英數字元一律換成底線）。這個語法同時適用於 `settings.json` 的權限規則、Skill 的 `allowed-tools` 清單、Subagent 定義檔的 `tools` 欄位、Hook 的 matcher [6]。

!!! note "怎麼審查一個 MCP server：整理者歸納，不是官方 checklist"
    官方沒有給一份「MCP server 安全審查」專頁，以下是綜合官方分散片段拼出來的判準，信心中等，不是單一頁面的逐字引用：(1) 是不是自己寫的、或來自你信任的來源；(2) 會不會爬外部內容（高風險的 prompt injection 來源）；(3) 用 `mcp__<server>__<tool>` 規則做最小權限，不要整台伺服器全部工具都放行；(4) 進版控前先用 `modelcontextprotocol/inspector` 這類官方除錯工具看它實際會呼叫哪些方法。

## 8. Windows 踩坑實錄

先把最容易誤傳的說法結清：**官方現行教學不需要 `cmd /c` 包裝**。逐字搜尋 `code.claude.com/docs/en/mcp` 與 `mcp-quickstart` 全文，都沒有出現「cmd /c」這個寫法；官方 quickstart 明講「`claude mcp add` works the same in every shell, including PowerShell and Command Prompt」，教學範例就是直接裸跑：

```bash
claude mcp add playwright -- npx -y @playwright/mcp@latest
```

跨 PowerShell、cmd.exe、Git Bash 都一樣，不需要額外包一層 `cmd /c` [4][6]。

`cmd /c` 這個包裝法只出現在網路上流傳的社群 workaround，通常是遇到某些 npx 套件在 Windows 裸跑失敗時才會被拿出來用。而它剛好會撞上一個 Git Bash（MSYS）特有的坑：

- **症狀**：手動組出 `claude mcp add playwright -- cmd /c npx -y @playwright/mcp@... --cdp-endpoint ...` 這種指令後，`claude mcp get` 會顯示連線逾時，`Args` 欄位裡看到的不是預期的 `/c`，而是 `C:/`。
- **成因**：GitHub Issue #46360（2026-04-10 回報，官方 closed as not planned）記錄了這個問題。Git Bash（MSYS 環境）在把參數傳給非 MSYS 的原生 Windows 執行檔時，會自動把看起來像絕對 Unix 路徑的 `/c` 轉成 Windows 路徑 `C:/`，寫進 `~/.claude.json` 的 `args` 因此變成 `["C:/", "npx", ...]` 而不是 `["/c", "npx", ...]` [7]。本機在 2026-09-19 用一個會印出 `argv` 的 Node 腳本重現過同樣的行為：不設環境變數時 `/c` 被轉成 `C:/`，設定 `MSYS_NO_PATHCONV=1` 後 `/c` 才原樣傳遞，症狀與 GitHub issue 描述完全對得上。
- **兩種解法**：
    1. 改用 PowerShell 或 `cmd.exe` 執行這條 `claude mcp add` 指令，避開 MSYS 的路徑轉換。
    2. 留在 Git Bash 的話，指令前面加 `MSYS_NO_PATHCONV=1` 關掉自動轉換。
    3. 官方最終認定這個 issue 不修，記錄的繞法是改用 `node` 直接指到 `node_modules/@playwright/mcp/cli.js`，整個繞開 `cmd.exe` [7]。

!!! note "另一個獨立問題：cmd.exe 包裝本身也可能打斷 stdio"
    `microsoft/playwright-mcp` 的 Issue #1540 記錄了一個不同的失敗模式：即使手動修正好 `/c` 被轉換的問題，`cmd.exe /c npx` 這個組合在 stdio transport 下仍可能失敗，因為 `npx.cmd` 這個批次檔包裝會打斷 stdio 需要的 stdin/stdout pipe 繼承。這條只透過 WebSearch 摘要取得，沒有逐字讀過原 issue 全文核對細節，信心中等 [8]。

**檢查習慣**：不管是裸跑 `npx` 還是手動包了 `cmd /c`，裝完都養成跑一次 `claude mcp get <name>` 看 `Args` 欄位的習慣。這是唯一能直接看到「Claude Code 實際上會執行的指令長什麼樣」的地方，比等連線逾時才回頭查快得多。

## 9. 推薦清單

**這頁範例本尊，2026-09-19 即時查證的 star 數與最後 push 日期**[18]：

| Repo | 數據 | 用途 |
|---|---|---|
| `upstash/context7` | 62,183★，最後 push 2026-09-18，MIT | 本頁第 2 節的遠端 HTTP 範例，查最新版套件文件 |
| `microsoft/playwright-mcp` | 37,284★，最後 push 2026-09-18，Apache-2.0 | 本頁第 8 節的官方安裝範例，瀏覽器自動化 |
| `github/github-mcp-server` | 33,043★，最後 push 2026-09-16，MIT | 官方 GitHub MCP server |

另外兩個跟本站其他頁重疊、直接連過去就好，不重複整理：

- **Obsidian vault**：`coddingtonbear/obsidian-local-rest-api` 這個 Obsidian 社群 plugin 內建 MCP server，完整設定步驟與 TLS 憑證處理見[Claude Code 接上 Obsidian vault](claude-code-obsidian.md#cmcp-server-claude-obsidian-vault) [19]。
- **官方 reference servers**：`modelcontextprotocol/servers` monorepo（90,453★，最後 push 2026-09-03）收了 filesystem 等官方範例伺服器，多數功能已被上面更成熟的獨立 repo 取代 [20]。

### Codex 的 MCP 設定

Codex 也能當 MCP client，設定放在 `~/.codex/config.toml`（使用者層，套用到所有 repo），受信任的專案也可以用專案層 `.codex/config.toml`。指令跟 Claude Code 很像：

```bash
codex mcp add <name> --env VAR=VALUE -- <stdio 啟動指令>
```

遠端 Streamable HTTP 伺服器改用 `--url`。`config.toml` 裡 stdio 型用 `[mcp_servers.<name>]` 搭配 `command`／`args`／`env`／`cwd`；HTTP 型用 `url`／`auth`（`oauth` 或 `chatgpt`）／`bearer_token_env_var`／`http_headers`。狀態檢查用 `codex mcp list`、OAuth 登入用 `codex mcp login <name>`，TUI 內也有 `/mcp`。這份 `config.toml` 是 ChatGPT 桌面版、Codex CLI、IDE 擴充共用的同一份設定，改一次三邊都能用 [11][12]。

需要注意的是**舊版 `codex mcp-server` 指令與獨立的 `codex-mcp-server` binary 已經被移除**，現在的 `codex app-server` 也不是 MCP server、不能拿來取代舊教學裡的設定，這件事[AI 介面比較總表](tools-compare.md#6-codex-mcp-server)已經寫過完整脈絡，這裡不重複 [13]。

## 資料來源

| 標記 | 來源 | URL |
|---|---|---|
| [1] | What is the Model Context Protocol (MCP)? | <https://modelcontextprotocol.io/introduction> |
| [2] | MCP Transports Overview（2026-07-28 版規格） | <https://modelcontextprotocol.io/docs/concepts/transports> |
| [3] | MCP 2026-07-28 版 Changelog（SSE 正式列入 Deprecated） | <https://modelcontextprotocol.io/specification/2026-07-28/changelog> |
| [4] | Connect Claude Code to tools via MCP（`claude mcp add` 完整參考） | <https://code.claude.com/docs/en/mcp> |
| [5] | 同上（scope 優先序、`.mcp.json`、OAuth、token 上限） | <https://code.claude.com/docs/en/mcp> |
| [6] | Connect to MCP servers（quickstart，官方安裝範例、故障排除步驟） | <https://code.claude.com/docs/en/mcp-quickstart> |
| [7] | GitHub Issue #46360：Windows `claude mcp add` 把 `/c` 轉成 `C:/` | <https://github.com/anthropics/claude-code/issues/46360> |
| [8] | GitHub Issue #1540（`microsoft/playwright-mcp`）：`cmd.exe /c npx` 在 stdio transport 下的獨立失敗模式 | <https://github.com/microsoft/playwright-mcp/issues/1540> |
| [11] | Model Context Protocol（Codex，官方頁面） | <https://learn.chatgpt.com/docs/extend/mcp?surface=cli> |
| [12] | 同上（`codex mcp add`、config.toml 格式、狀態檢查指令） | <https://learn.chatgpt.com/docs/extend/mcp?surface=cli> |
| [13] | Codex MCP server 移除公告 | <https://learn.chatgpt.com/docs/mcp-server> |
| [14] | SKILL、Plugin、MCP 與 Subagent（本站既有頁） | `extensions.md`（本站內部） |
| [15] | Security（Claude Code 官方安全頁） | <https://code.claude.com/docs/en/security> |
| [16] | context7 官方文件（Claude Code 安裝指令、API key 選填說明） | <https://context7.com/docs/resources/all-clients> |
| [18] | `gh api repos/<owner>/<repo>`（即時 stars／pushed_at，2026-09-19 查證） | GitHub API |
| [19] | Claude Code 接上 Obsidian vault（本站既有頁） | `claude-code-obsidian.md`（本站內部） |
| [20] | `gh api repos/modelcontextprotocol/servers`（即時查證） | GitHub API |

延伸：[SKILL、Plugin、MCP 與 Subagent](extensions.md)｜[AI 介面比較總表](tools-compare.md)｜[Claude Code 接上 Obsidian vault](claude-code-obsidian.md)｜[免付費區](free-tier.md)
