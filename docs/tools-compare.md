# AI 介面比較總表

> 查證日期：2026-09-16。方案與功能變動快，請以官方最新說明為準。

Claude 與 ChatGPT／Codex 加起來有五種以上的介面，名字又常常互相借用（Cowork、Work、Codex 分頁、Codex App……），第一次接觸很容易搞錯。這頁先用一張精簡表對照八種常見介面，細節放進表格下方的逐介面說明，再挑出最容易搞混的六組單獨說明。每一格背後都有來源，標記沿用查證文件的原始編號（`S`＝Claude 官方來源、`O`＝ChatGPT／Codex 官方來源、`X`＝補充查證來源），對照表列在頁尾；查無明確資料的格子直接寫「查無」，不用推測填補。

## 主表：介面 × 方案

「✅」可用、「❌」不可用、「⚠️」有限制或需額外條件、「？」查無或官方文件互相矛盾。這裡只列最關鍵的三個判斷維度，完整說明（跑在哪裡、Skill／Plugin／MCP 細節、適合場景）在表格下方的「逐介面細節」，來源標記也都在那裡。

| 介面 | 本機讀寫 | 執行指令 | 最低方案 |
|---|:---:|:---:|---|
| Claude Chat | ❌ | ⚠️沙盒 | Free |
| Claude Desktop（Chat 分頁） | ❌ | ⚠️同上 | 依分頁 |
| Cowork | ✅ | ✅隔離VM | Pro 起 |
| Claude Code | ✅ | ✅ | Pro／API |
| Claude Design | ？ | ？ | Pro 起 |
| ChatGPT | ❌ | ？ | Free |
| ChatGPT Desktop | ⚠️視分頁 | ⚠️視分頁 | Free 起 |
| Codex | ⚠️視環境 | ✅視模式 | Free／Go |

!!! warning "2026-09-16 起：Cowork 正在併入一般 Chat（分階段推出，尚未全面生效）"
    Claude 官方公告 Cowork 與一般 Chat 正在合併成同一個體驗，**是分階段推出，不是已經全面生效**：Pro／Max 帳號正在逐步收到（即使同方案，不同帳號收到的時間點也不一樣），Team／Free 官方說「即將推出」但目前尚未開始，Enterprise 在變動前會提前至少 30 天通知、目前維持現狀不變。合併後的體驗裡沒有獨立的「Cowork 模式」可切換，原本只有 Cowork 才有的檔案操作、任務、connector、skill 能力，在任何一段對話裡都能自動用到，由 Claude 自己判斷要不要動用。上面表格裡「Cowork」這一列，對還沒收到新體驗的帳號仍然照原樣運作；已經收到新體驗的帳號，請把這一列的能力直接理解成「一般對話多了這些能力」，不是找不到 Cowork 分頁就是設定錯了 [S25][S26][S27]。

## 逐介面細節

#### Claude Chat（網頁／手機）
- 跑在哪裡：Anthropic 雲端伺服器 [S7]
- 讀寫本機檔案：❌ 不能 [S7]
- 執行指令／程式碼：⚠️ 只有雲端的 code execution 沙盒工具，不是本機終端 [S7]
- Skill／Plugin／MCP：Skill✅／Plugin⚠️（付費方案可在網頁版 Chat 使用，但官方文件說法不一致，見[擴充機制比較](extensions.md)）[S24]／MCP（remote）✅ 免費帳號限 1 個自訂 connector [S9b][S12]
- 最低方案：Free 即可 [S3][S15]
- 適合做什麼：問答、腦力激盪、潤飾文字

#### Claude Desktop（Chat 分頁）
- 跑在哪裡：本機安裝的殼，Chat 分頁內容仍跑在雲端 [S7]
- 讀寫本機檔案：❌ Chat 分頁本身不行 [S7]
- 執行指令／程式碼：⚠️ 同 Chat，雲端沙盒 [S7]
- Skill／Plugin／MCP：同 Claude Chat，另可加本機 MCP（desktop extensions）[S13]
- 最低方案：Free 可用 Chat 分頁；Cowork／Code 分頁要付費方案 [S3][S7]
- 適合做什麼：一個 App 內同時裝 Chat／Cowork／Code

#### Cowork（Desktop 第三分頁／web／mobile beta）
- 跑在哪裡：預設是雲端 VM，既有 Desktop 部署也可能用本機專用 Linux VM [X4]
- 讀寫本機檔案：✅ 本機或雲端 VM 內讀寫，需 Claude Desktop 保持開啟連線 [S21][X4]
- 執行指令／程式碼：✅ 隔離 VM 內可跑 shell／程式碼，但不等於主機終端，不能叫它直接跑主機上的 `codex exec` [X4]
- Skill／Plugin／MCP：Skill✅／Plugin✅（可包含在主機執行的 local MCP server）／MCP（remote connector）✅ [S9b][X4]
- 最低方案：Pro 起，免付費帳號完全不可用 [S21]
- 適合做什麼：整理檔案、做報表、寄信、跨應用文書工作

#### Claude Code（CLI／Desktop Code 分頁／網頁／IDE）
- 跑在哪裡：CLI／IDE 擴充／Desktop 本機；claude.ai/code 是 Anthropic 管理的雲端 VM [S7][S8]
- 讀寫本機檔案：✅ CLI／IDE／Desktop 可讀寫本機；網頁版是雲端 VM 內的 repo，不是使用者本機磁碟 [S7][S8]
- 執行指令／程式碼：✅ 本機終端指令（CLI／IDE／Desktop）[S1]
- Skill／Plugin／MCP：Skill✅／Plugin✅／MCP（本機＋remote）✅／Subagent✅／Hooks✅ [S9b][S17][S18][S19][S20]
- 最低方案：Free 沒有；Pro 起，也能純用 API key 按量付費、不吃訂閱額度 [S1][S23]
- 適合做什麼：跨檔批次處理、程式開發、可重跑流程

#### Claude Design（canvas 設計工具）
- 跑在哪裡：？查無：官方說明沒提到跑在本機還是雲端 [S22]
- 讀寫本機檔案：？查無 [S22]
- 執行指令／程式碼：？查無 [S22]
- Skill／Plugin／MCP：？查無：官方說明沒列出 Skill／Plugin／MCP 支援 [S22]
- 最低方案：Free 未提及；Pro 起（research preview）；Enterprise 預設關閉，需管理員手動開啟 [S22]
- 適合做什麼：對著畫面拖拉調整產出設計稿、原型、投影片、one-pager，而不是純寫 prompt [S22]

#### ChatGPT（網頁／手機）
- 跑在哪裡：OpenAI 雲端伺服器 [O10]
- 讀寫本機檔案：❌ 不能 [O10]
- 執行指令／程式碼：？查無：本次查證沒有涵蓋 ChatGPT 網頁版程式碼執行工具的細節
- Skill／Plugin／MCP：Connectors／Apps✅（Free 僅內建 App，Plus 起可加自訂 MCP）[O22]
- 最低方案：Free 即可 [A2 §1]
- 適合做什麼：問答、寫作、Deep Research

#### ChatGPT Desktop（統一版，含 Chat／Work／Codex 分頁）
- 跑在哪裡：本機殼；Chat／Work 跑在雲端，Codex 分頁依 sandbox 設定可在本機執行 [O7]
- 讀寫本機檔案：⚠️ Codex 分頁依 sandbox mode 可讀寫本機；Chat／Work 分頁不行 [O25]
- 執行指令／程式碼：⚠️ Codex 分頁依 sandbox mode（read-only／workspace-write／danger-full-access）[O25]
- Skill／Plugin／MCP：Codex 分頁：AGENTS.md✅／Skill✅／Plugin✅／Subagent✅，全方案不分級 [O28][O29][O30]
- 最低方案：Free 即可，官方明說方案層級含 Free [O3][O7]；但功能是分批推出，不保證每個帳號當下都已經看得到 [A2b 題2]
- 適合做什麼：一個 App 打通聊天、知識工作 agent、程式碼 agent

#### Codex（CLI／IDE／cloud）
- 跑在哪裡：CLI／IDE 擴充在本機；cloud（chatgpt.com/codex）是 OpenAI 雲端 sandbox 內的 repo checkout [O25][O26]
- 讀寫本機檔案：CLI／IDE 可讀寫本機；cloud 是雲端 checkout，不是使用者本機磁碟 [O25]
- 執行指令／程式碼：✅ 依 sandbox mode 決定要不要先問過你 [O25]
- Skill／Plugin／MCP：AGENTS.md✅／Skill✅／Plugin✅／Subagent✅，全方案不分級；也能當 MCP client 接外部服務 [O28][O29][O30][X6]
- 最低方案：Free／Go 可用，但不同介面深淺不一，官方文件之間曾出現矛盾（見下方第三、五組）[A2 §0][A2b 題5]
- 適合做什麼：本機 repo 互動、CI/CD 腳本、雲端長跑任務

## 最容易搞混的六組

### 1. Claude Desktop 的 Chat 分頁 vs Cowork／Code 分頁
同一個 App 裡的三個分頁，能碰到的東西差很多。Chat 分頁本質上就是網頁版包進桌面殼，不能碰本機檔案；要讀寫本機檔案，得切到 Cowork 或 Code 分頁 [S7]。看到「我在用 Claude Desktop」這句話，不能直接假設它能動你的檔案，要先問清楚是哪個分頁。**但這個「三分頁」的說法只適用還沒收到新體驗的帳號**：2026-09-16 起 Pro／Max 帳號正分階段收到 Cowork 併入 Chat 的合併體驗，收到之後 Chat 分頁本身就能碰本機檔案，不必再切分頁 [S26]。

### 2. Cowork vs Claude Code
兩者共用底層的 agent 架構，但任務導向完全不同：Cowork 面向一般知識工作（整理檔案、做報表、跨應用程式），Claude Code 面向程式碼與可重跑的批次流程 [S21]。官方也特別強調，Cowork 不是 Claude Code CLI 的另一個名字 [X4]。

### 3. ChatGPT Desktop 的 Codex 分頁 vs Codex CLI
兩者功能幾乎等價，共用同一顆引擎與認證機制，差別只在你在哪個視窗操作：Codex 分頁在統一版 ChatGPT Desktop App 裡，CLI 是獨立的終端機視窗 [O15]。

### 4. ChatGPT（一般對話）vs Codex：兩者不是同一種工具

Chat 適合快速問答與一般討論（官方說明裡「quick question」一詞出自開新對話的 Quick chat 按鈕說明，這裡借來形容用途，不是官方對 Chat 的正式定位），不開資料夾，也不碰本機檔案，最多只能叫用雲端的 code execution 沙盒工具跑一次性程式碼，那個執行環境跟你的電腦無關，也留不下可持續操作的 repository。Codex（不管是 CLI、IDE 擴充、雲端版，還是 ChatGPT Desktop App 裡的 Codex 分頁）則是拿來處理 repository：寫程式、除錯、跑測試指令、審查變更 [O7]。

本機檔案存取上兩者差很多：Chat 不行（官方頁面沒有逐字寫「Chat 不能碰本機檔案」，這是從「開本機資料夾只在 Work／Codex 提供」推得的整理者觀察）；「本機環境（local environment）」這個具名功能，官方文件明寫只在 ChatGPT Desktop App 的 Codex 視圖裡可以設定與使用，CLI／IDE 擴充則是直接操作你電腦上的資料夾、專案層設定放在該資料夾的 `.codex` 內 [O31]。（Desktop App 裡另外還有一個 Work 分頁也能開本機資料夾，但它面向的是長時間、多步驟、跨 App 的知識工作任務，跟 Chat／Codex 是三種不同定位，這裡不展開；此點官方頁面 WebFetch 一度回傳 403，只能用搜尋摘要佐證，信心中等 [O32]。）

執行指令方面：Chat 沒有終端機，只有雲端沙盒裡的一次性程式碼執行；Codex 依 sandbox mode（`read-only`／`workspace-write`／`danger-full-access`）決定能不能寫檔、跑指令、要不要先問過你再動作，細節見上方「逐介面細節」的 Codex 小節 [O25]。

怎麼選：只是想問問題、討論、潤飾文字 → Chat 就夠；要動到程式碼、跑測試、審查 diff、處理 repository（不管本機還是雲端）→ Codex，依手邊環境挑 CLI、IDE 擴充、桌面版分頁或雲端版本。

### 5. Codex 桌面 App 已經併入 ChatGPT Desktop（2026-07-09）
Codex 原本有獨立的桌面 App（macOS 2026 年 2 月上線、Windows 3 月 4 日上線），但已於 2026-07-09 併入統一版 ChatGPT Desktop App。「Codex Desktop app」作為獨立產品現在已經不存在，只是那個統一 App 裡的一個分頁；查到教別人「去下載獨立 Codex App」的舊教學，已經過時 [X1][X2][O7][A2b 題1]。

### 6. `codex mcp-server` 教學已失效
舊版 Codex 曾提供 `codex mcp-server` 指令與獨立的 `codex-mcp-server` binary，但 OpenAI 現行文件已明載兩者都已移除。現在的 `codex app-server` 是給圖形介面與整合程式用的 JSON-RPC server，官方明確說它不是 MCP server，不能拿來取代舊教學裡的 `codex mcp-server` 設定 [X5][X6]。網路上還能搜到的舊版設定檔範例，直接照抄會失敗。

## 怎麼選

- 只是想討論、腦力激盪、潤飾一段文字 → Claude Chat 或 ChatGPT 網頁版。
- 想做一般辦公自動化（整理檔案、寄信、跨工具彙整），不想碰終端機 → Claude（Pro／Max 已收到合併體驗的帳號直接在一般對話做；尚未收到的帳號切到 Cowork 分頁 [S26]）或 ChatGPT Desktop 裡的 Work 分頁。
- 需要讀寫本機檔案、跨檔案批次處理、要版本控制 → Claude Code 或 Codex CLI／IDE 擴充。
- 想丟一個長跑任務、不想守在螢幕前，或要處理你本機沒有的 repo → claude.ai/code（Claude Code on the web）或 Codex cloud。
- 想做視覺化設計、原型、投影片 → Claude Design（仍是 research preview，Pro 起）。
- 只有免費帳號、想先試試程式碼代理 → ChatGPT Free／Go 裡的 Codex（尤其桌面 App 內最明確可用）；Claude Code 免費帳號完全用不到，見[免付費區](free-tier.md)。

## 資料來源（2026-09-16 查證）

| 標記 | URL | 用途 |
|---|---|---|
| S1 | support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan | Claude Code 於 Pro/Max 的可用性 |
| S3 | claude.com/pricing | 五種方案功能總覽 |
| S7 | code.claude.com/docs/en/overview | Claude Code 五種 surface 官方總覽 |
| S8 | code.claude.com/docs/en/claude-code-on-the-web | claude.ai/code 雲端 session 的可用性與限制 |
| S9b | support.claude.com/en/articles/12512176-what-are-skills | Skills 方案可用性 |
| S12 | support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp | Remote MCP 自訂 connector 方案別數量限制 |
| S13 | support.claude.com/en/articles/11725091-when-to-use-desktop-and-web-connectors | Remote vs local connector 差異 |
| S15 | support.claude.com/en/articles/8114487-what-interfaces-can-i-use-to-access-claude | 官方介面總覽 |
| S17 | code.claude.com/docs/en/sub-agents | Claude Code subagent 官方文件 |
| S18 | code.claude.com/docs/en/hooks-guide | Claude Code hooks 官方文件 |
| S19 | code.claude.com/docs/en/plugins | Claude Code plugins 官方文件 |
| S20 | code.claude.com/docs/en/mcp | Claude Code 連接 MCP 官方文件 |
| S21 | support.claude.com/en/articles/13345190-get-started-with-claude-cowork | Cowork 方案可用性、本機檔案存取 |
| S22 | anthropic.com/news/claude-design-anthropic-labs | Claude Design 方案可用性、research preview 狀態 |
| S23 | support.claude.com/en/articles/12304248-manage-api-key-environment-variables-in-claude-code | 純 API key 跑 Claude Code 的計費機制 |
| S24 | support.claude.com/en/articles/13837440-use-plugins-in-claude | Claude.ai／Cowork 使用 plugin 的方案與介面 |
| S25 | claude.com/blog/cowork-is-now-claude | Cowork 與 Chat 合併公告（2026-09-16） |
| S26 | support.claude.com/en/articles/16761823-claude-cowork-and-chat-are-one-claude | 合併現況：各方案推出時程、分階段推出說明 |
| S27 | support.claude.com/en/articles/13455879-use-claude-cowork-on-team-and-enterprise-plans | Team／Enterprise 維持現狀不變 |
| O3 | OpenAI 官方 X 貼文（2026-07-09 ChatGPT Work 發布，經二次來源引述） | Desktop app 全方案含 Free 可用 Chat/Work/Codex |
| O7 | learn.chatgpt.com/docs/app | 統一版 Desktop app 的分頁切換方式 |
| O10 | 業界慣例類推（未找到 OpenAI 專門說明此點的頁面） | API key 不含網頁 Chat 存取（信心中偏低） |
| O15 | learn.chatgpt.com/docs/ide | Codex IDE 擴充與 CLI 的關係 |
| O22 | help.openai.com/en/articles/11487775-connectors-in-chatgpt；12003714 | Connectors/Apps/MCP 各方案差異 |
| O25 | learn.chatgpt.com/docs/sandboxing | Codex sandbox 三模式定義 |
| O26 | learn.chatgpt.com/docs/cloud | Codex cloud 運作方式 |
| O28 | learn.chatgpt.com/docs/agent-configuration/agents-md | AGENTS.md 讀取順序與上限 |
| O29 | learn.chatgpt.com/docs/build-skills | Codex/ChatGPT Skills 定義 |
| O30 | learn.chatgpt.com/docs/agent-configuration/subagents | Codex subagents 設定方式 |
| O31 | developers.openai.com/codex/environments/local-environment | 「本機環境」只在 Codex 視圖可用 |
| O32 | help.openai.com/en/articles/20001275-chatgpt-work-and-codex | Work 也能開本機資料夾（WebFetch 403，改用搜尋摘要，信心中等） |
| X1 | openai.com/index/introducing-the-codex-app/ | Codex 獨立桌面 App 上線時間 |
| X2 | openai.com/index/chatgpt-for-your-most-ambitious-work/ | ChatGPT Work 發布、Codex App 併入時間 |
| X4 | support.claude.com/en/articles/14479288-claude-cowork-architecture-overview | Cowork 實際執行位置（雲端 VM／本機 Linux VM） |
| X5 | learn.chatgpt.com/docs/mcp-server | Codex MCP server 移除公告 |
| X6 | github.com/openai/codex/blob/main/codex-rs/app-server/README.md | Codex App Server 定位說明 |

延伸：[免付費區](free-tier.md)｜[付費區](paid-tier.md)｜[Claude Code + Codex 協作](claude-codex.md)
