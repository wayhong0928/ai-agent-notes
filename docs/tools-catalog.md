# 好用工具清單

> 查證日期：2026-09-19（2026-09-25 補入 4 項，2026-10-03 補入 1 項，2026-10-08 補入 31 項、新增第 7、8 節，並把 open-slide 移到第 7 節更新，這幾列另外標註查證日期；2026-10-05 依來源更新 agentic-engineering-handbook 一列的內容描述）。stars／最後更新日期／license 都是各列查證當天的快照，之後會變動，請自己重查一次再決定要不要裝。

這頁收的是本站作者自己讀過、審查過的 Claude Code／Codex 官方文章、skill、plugin、MCP 與學習資源。目標是「精選」不是「收全」：能找到的相關 repo 遠不只這些，這裡只留下讀過原始碼、判斷過風險之後還願意留著的項目。2026-10-08 補入的項目，查的是 README、授權與關鍵的原始碼（網路行為、hook），沒有逐檔讀完全部程式碼。想看完整清單，第 6 節的幾個 awesome-list 本身就是更大的入口。

## 1. 怎麼用這份清單

**星數不是品質保證。** CMU 一篇研究〈Six Million (Suspected) Fake Stars on GitHub〉（arXiv 2412.13459，收錄於 ICSE '26）估計 GitHub 上有約六百萬顆疑似造假的星星；影響最廣的 2024 年 7 月，熱門 repo 中有 16.66%（3,499 個）出現刷星活動 [1]（這是論文 2025-09 修訂版 v2 的數字；2024-12 的 v1 寫的是 50 星以上 repo 的 15.84%）。一個 repo 星數高，只能證明「有很多帳號按過星」，不能證明「內容被很多人讀過、用過、審過」。這份清單裡凡是星數成長曲線明顯異常的項目，會在備註裡老實寫出來，不會因為星數高就跳過審查。

**安裝前的審查步驟（不分星數高低，每一項都要做）**：

1. 讀完整份 `SKILL.md` 或 plugin 的說明文件，不要只看 README 的安裝指令那一段。
2. 讀過它會執行的每一支腳本，確認它會讀寫哪些檔案、會不會呼叫網路、會不會要求你的帳密或 token。
3. 確認 license 與維護狀態——`null`／`NOASSERTION` 代表沒有偵測到標準授權條款，不能假設可以自由重製或散布；超過三個月沒更新的要多留意還有沒有人在維護。
4. 安裝方式鎖版本（鎖 commit hash 或 release tag），不要用 `npx <package> add` 這種每次都抓最新版、沒有版本鎖定的一鍵安裝指令——上游帳號或套件一旦被劫持，同一條指令下次就可能拉到惡意版本而你不會發現。

**靜態掃描器（例如 SkillSpector）能幫忙，但有極限，不能取代人工複核。** 本站作者實際在用 [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) 對新裝的 skill 跑掃描，但它至少有兩種已知的誤判模式：一是掃描沒有真的跑完就回傳一個嚇人的分數（曾經遇過某 skill 因為內容量大導致掃描中途觸發 runtime 限制、覆蓋率只有個位數百分比，仍然回傳「CRITICAL」）；二是把正常的 HTML 註解、或 `SKILL.md` 裡連到其他參考檔案的內部連結，誤判成 prompt injection 或「規避分析」。第 5 節的畫圖類 skill 審查筆記會給一個實際踩過這兩種誤判的例子。判斷原則：掃描分數是「要不要花時間去人工複核」的訊號，不是「能不能裝」的最終答案。

## 2. 官方文件與 harness 文章

每篇都用完整原文核對過核心觀點，不是憑標題猜的。

| 文章 | 核心觀點（一句話） | 信心 |
|---|---|---|
| [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices) | 給 Claude 一個能自己跑的驗證（測試／build／截圖），把「看起來做完」變成有 pass/fail 訊號；同一個誤解被糾正兩次以上就該清掉上下文重開，而不是繼續磨 | 高（讀完整正文） |
| [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)（Anthropic） | 最成功的實作用的是簡單、可組合的模式，不是複雜框架；先用最佳化過的單次呼叫，效果不夠才加多步驟架構 | 高（讀完整正文） |
| [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)（Anthropic） | 上下文是有限資源、邊際報酬遞減，重點是精選進入注意力的內容，不是寫更長的提示詞 | 高（讀完整正文） |
| [Harness Design for Long-Running Application Development](https://www.anthropic.com/engineering/harness-design-long-running-apps)（Anthropic） | 提出規劃／生成／評估三代理分離的架構，因為代理自評會系統性偏高分，分離角色比自評更可靠 | 中（摘要比對，未逐字核對全文細節） |
| [Codex Skills 官方指南](https://learn.chatgpt.com/docs/build-skills) | Skill 搜尋路徑分四層（專案／使用者／系統管理員／內建），格式與 Claude Code 的 SKILL.md 相容；原則是一個 skill 只做一件事 | 高（讀完整正文） |

## 3. 官方 Skill 與 Plugin

| 項目 | 用途 | 維護狀態（截至 2026-09-19） | 備註 |
|---|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | 官方 Agent Skills 公開範例倉庫，`skill-creator`、`claude-api` 等都出自這裡 | 177,055★，最後 push 2026-09-10，license NOASSERTION | license 未標註，重製前自己確認條款；本站作者部分在用（透過打包後的 marketplace 版本） |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | 官方 plugin marketplace 原始碼 | 36,480★，最後 push 2026-09-18，Apache-2.0 | 來路最清楚的安裝來源，裝這裡的 plugin 風險最低 |
| [openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc) | Codex 官方的 Claude Code plugin，讓 Claude Code 直接呼叫 Codex 做 review 或委派任務 | 33,317★，最後 push 2026-07-08，Apache-2.0 | 本站作者實際在用 |
| [anthropics/claude-cookbooks](https://github.com/anthropics/claude-cookbooks) | 官方 API 用法 cookbook，非 Claude Code 專用，但工具呼叫模式可參考 | 52,810★，最後 push 2026-09-18，MIT | 適合想直接用 API 而非 Claude Code 的讀者 |
| `claude-api` skill 的 `prompt-audit` 子指令（用法 `/claude-api prompt-audit`） | 檢查專案裡的 skill、CLAUDE.md、系統提示詞與工具描述，找出為舊模型寫、對新模型已經多餘或有害的寫法（例如當年為了觸發不足而加的強調語氣、一步一步照做的腳本），產出報告（附 `檔案:行號`、理由與信心等級）和一份建議 diff | Claude Code 內建，不用另外安裝（2026-09-25 在 Claude Code 2.1.282 查證） | 預設只提建議、不直接改檔，要在指令裡明講要套用才會動檔案；低信心的項目只列在報告裡，不放進 diff。官方介紹見 Anthropic 部落格[2]；完整規則在 skill 內附的 `shared/prompt-audit.md` |
| [feature-dev](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/feature-dev)（官方 marketplace） | 七階段功能開發：先了解需求、探索程式碼、問清細節、設計架構，再實作、審查、總結。過程中會平行派 2 到 3 個 code-explorer、2 到 3 個 code-architect、3 個 code-reviewer agent（三種都設 `model: sonnet`） | 隨官方 marketplace 更新（repo 37,534★，Apache-2.0，2026-10-08 查證） | 一次功能開發會派出七到九個 subagent，用量跟著增加；小改動不必走完七階段。已經習慣「先規劃、做完另外驗收」的人，流程大致重疊 |
| [frontend-design](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/frontend-design)（官方 marketplace） | 做前端時的視覺設計指引。README 寫目標是 "avoid generic AI aesthetics"；SKILL.md 本身講的是美感方向、字型，以及 "making choices that don't read as templated defaults" | 同上（2026-10-08 查證） | 只有一個 skill，沒有 hook、agent 或指令，風險面小。跟第 5 節的 UI UX Pro Max、Impeccable 同類，三個挑一個裝；想先試的話從這個開始，官方出品、內容最少 |
| [Claude Code Mods](https://code.claude.com/docs/en/plugins/mods/overview)（官方文件） | 一種新的 plugin：內容是 JavaScript／TypeScript 函式，跑在 Claude Code 程序裡。能畫側邊面板與輸入框上方的提示帶、加一個不經過 Claude 回合就執行的 `/指令`、旁觀或改寫工具呼叫 | 預設開啟：終端機 v2.1.287 起，Desktop app v2.1.286 起[3]（2026-10-08 查證） | 裝第三方 mod 前先讀官方的風險清單：mod 能讀寫你帳號碰得到的檔案、讀環境變數裡的 API key、在權限提示出現前替你核准工具呼叫、用你的方案呼叫模型，而且官方寫明 "Mods aren't sandboxed."。不用執行就能先看它會做什麼：把 repo 抓下來，對資料夾跑 `claude plugin validate`，看輸出的 `hooks:` 與 `calls:` 兩行。VS Code 擴充套件與 `claude -p` 也會跑 mod 的函式，只是看不到它畫的介面 |
| `cc-plugin-you-should-know`（Claude Code 內建 mod，功能名稱 You should know） | Claude 做較長的任務時，另外跑一個側邊 agent，發現你可能漏看的事，就在輸入框上方提示 | 2.1.287 加入，預設關閉，用 `/plugin enable cc-plugin-you-should-know@builtin` 開啟；changelog 註明 "for first-party sessions with telemetry on"（2026-10-08 查證） | 官方文件沒寫這個側邊 agent 會用掉多少額度 |

## 4. MCP

MCP 的協定原理、安裝步驟、scope 與 OAuth 設定，還有 Windows 上的踩坑實錄，都寫在專篇[MCP 入門與實戰](mcp.md)，這裡不重複，只列那篇沒收的項目：下表兩個是推薦項目，另外三個要帳號的搜尋與爬取服務放在本節最後。

| 項目 | 為什麼值得知道 | 維護狀態（截至 2026-09-19） |
|---|---|---|
| [ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) | 用 Chrome DevTools Protocol 讓代理檢查效能、console、網路請求，比純截圖驗收更深入 | 52,288★，最後 push 2026-09-18，Apache-2.0 |
| [modelcontextprotocol/inspector](https://github.com/modelcontextprotocol/inspector) | 官方除錯／視覺化工具，裝任何 MCP server 之前先用這個看它實際會呼叫哪些方法，等於幫第 1 節「安裝前審查」的第 2 步省力 | 10,913★，最後 push 2026-09-19，license 未標註 |

[MCP 入門與實戰第 9 節](mcp.md#9)已經收了 `upstash/context7`、`microsoft/playwright-mcp`、`github/github-mcp-server` 三個常用項目，這裡不重複列。另外 `MarkusPfundstein/mcp-obsidian`（透過 Obsidian Local REST API plugin 讀寫 vault）功能對 Obsidian 使用者很直接，但需要常駐 Obsidian 並在本機開一個 REST API port，屬於「功能對得上、但曝險面要自己權衡」的項目，不列入前兩項推薦。

### 網頁搜尋與爬取

Claude Code 內建 WebSearch、WebFetch，一般查資料用不到下面這幾個；需要指定搜尋引擎、整站爬取，或抓社群、電商等平台資料時再考慮。三個的完整功能都要註冊帳號。

| 項目 | 用途 | 維護狀態（2026-10-08 查證） | 費用與注意事項 |
|---|---|---|---|
| [brave/brave-search-mcp-server](https://github.com/brave/brave-search-mcp-server) | Brave 搜尋引擎的官方 MCP | 1,488★，最後 push 2026-10-05，MIT | 需要 Brave Search API key（`BRAVE_API_KEY`），到 brave.com/search/api 申請並選方案。README 沒寫價格，自己去官網看 |
| [firecrawl/firecrawl-mcp-server](https://github.com/firecrawl/firecrawl-mcp-server) | 網頁抓取、搜尋、整站爬取 | 7,569★，最後 push 2026-10-08，MIT | 用 npx 在本機跑要 `FIRECRAWL_API_KEY`；官方託管版的 scrape、search、parse 不用 key 但有速率限制，crawl、map、agent 仍要 key。按 credits 計費、有免費方案，價格會變，以官方定價頁為準 |
| [socialcrawl/mcp](https://github.com/socialcrawl/mcp) | 社群、電商、求職等多種平台資料 API 的 MCP | 26★，最後 push 2026-10-08，MIT | 註冊送 100 點免費 credits，實際查資料才扣點（standard 1 點、advanced 5 點、premium 10 點），查文件類的工具不用 key。星數很少、repo 2026-04 才建立，成熟度要自己評估 |

## 5. 社群 Skill 與 Plugin

### 一般用途

| 項目 | 用途 | 維護狀態（截至 2026-09-19） | 備註 |
|---|---|---|---|
| [blader/humanizer](https://github.com/blader/humanizer) | 去 AI 感改寫，依 Wikipedia〈Signs of AI writing〉整理的判準 | 約 5.0 萬★，MIT，最後更新 2026-09-06 | 本站作者實際在用，中英文都適用 |
| [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) | 減少 LLM 寫程式時的過度工程化，強調外科手術式小改動與可驗證的完成標準 | 約 21.4 萬★，license 欄位為空（使用前自行確認），最後更新 2026-04-20 | 本站作者實際在用 |
| [wshobson/agents](https://github.com/wshobson/agents) | 跨 Claude Code／Codex／Cursor／OpenCode／Copilot 的多用途 plugin marketplace，agent／skill／command 種類齊全 | 39,789★，最後 push 2026-09-19，MIT | 規模大，建議先挑單一 agent／skill 讀過再裝，不要整包信任 |
| [github/spec-kit](https://github.com/github/spec-kit) | GitHub 官方的 Spec-Driven Development 工具包，把「先出規格再執行」流程化 | 137,848★，最後 push 2026-09-18，MIT | 跟「先出規格、再交給執行者」這種分工方式同構，即使不整套裝，讀它怎麼把規格寫成可驗證的格式也有參考價值 |
| [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) | 另一個規格驅動開發（SDD）工具：寫程式前先跟 AI 對齊提案、規格、設計與任務清單，每項變更各自一個資料夾 | 70,307★，最後 push 2026-09-23，MIT（2026-09-25 查證） | npm 套件 `@fission-ai/openspec`，全域安裝一次；每個專案各自執行 `openspec init`，會建立 `openspec/` 資料夾，並在 `.claude/` 加上 skill 與 slash command（例如 `/opsx:propose`）。跟上一列 spec-kit 定位相近，挑一個用就好；官方 README 的安裝指令用 `@latest`，照第 1 節第 4 步改成鎖定版本 |
| [stablyai/orca](https://github.com/stablyai/orca)（官網 [onorca.dev](https://onorca.dev)） | 本機桌面 app（macOS／Windows／Linux），讓 Claude Code、Codex、OpenCode 等 CLI agent 各在自己的 git worktree 平行跑，集中在一個畫面監看；另有手機 app，可以看進度、收完成通知、補一句追問 | 77,922★，最後 push 2026-09-25，MIT（2026-09-25 查證） | 它不是模型，跑的是你自己已經登入的 CLI（官方文件原文：bring your own Claude, Codex, or OpenCode subscription），用量照算在你自己的訂閱，不會替你省額度。「不同 session 之間直接傳遞 context」在官方討論區 [#681](https://github.com/stablyai/orca/discussions/681) 是以提案（Ideas 分類）出現，README 沒有宣稱已經做到；維護者 2026-05-05 在同一串回覆已加入實驗性的 Agent Orchestration，官方文件寫明要先到 Settings → Experimental 開啟，做法是在 agent 之間傳任務規格和訊息，不是把整段對話 context 搬過去。打包版預設會送匿名使用統計，可以關掉（見官方 telemetry 文件）。repo 2026-03 才建立，半年累積近 7.8 萬★，照第 1 節的原則，星數不能當成審查過 |

### 整套開發工作流

這類 skill 集會接管「怎麼規劃、怎麼執行、怎麼驗收」的整個流程，兩套擇一，不要同時裝。

| 項目 | 用途 | 維護狀態（2026-10-08 查證） | 備註 |
|---|---|---|---|
| [obra/superpowers](https://github.com/obra/superpowers) | brainstorming、writing-plans、executing-plans、test-driven-development、subagent-driven-development 等 15 個 skill 組成的開發流程 | 296,615★，最後 push 2026-10-08，MIT | 已上架官方 plugin marketplace（`/plugin install superpowers@claude-plugins-official`），但內容是第三方寫的。裝了之後，開新對話、`/clear`、compact 之後，都會由 SessionStart hook 把 using-superpowers 這份 skill 全文注入對話；自己已經有開場注入的 hook 或一套規劃與驗收規則的話，兩邊的指示可能互相打架。brainstorming 的可選視覺功能預設從作者網站載入 logo，網址帶著 Superpowers 的版本號，設環境變數 `SUPERPOWERS_DISABLE_TELEMETRY` 可關 |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 工程實務 skill 集，README 原文 "Production-grade engineering skills for AI coding agents."，附 /spec、/plan、/build、/test、/review、/ship 等 9 個指令 | 103,215★，最後 push 2026-10-03，MIT | 把資深工程師的工作流程與品質關卡寫成 skill，適合想看「一套完整流程長什麼樣」的人先讀再挑 |

### 前端設計

跟第 3 節官方的 frontend-design 同類，三個挑一個裝。

| 項目 | 用途 | 維護狀態（2026-10-08 查證） | 備註 |
|---|---|---|---|
| [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 附一份本機可搜尋的設計資料庫：79 種 UI 風格（README 註明其中 50 種啟用）、192 組配色、74 組字型搭配、25 種圖表、22 種技術棧 | 134,004★，最後 push 2026-10-08，MIT | 沒有 hook。核心搜尋在本機；附帶的取背景圖腳本會連 Pexels，生 logo 的腳本要 Gemini 等服務的 API key，用到那些功能才會跑 |
| [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | 設計語言加指令，README 原文 "1 skill, 24 commands, live browser iteration, and 59 deterministic detector rules for AI-generated frontend design." | 78,497★，最後 push 2026-10-07，Apache-2.0 | 有 hook：`npx impeccable install` 會詢問要不要裝設計檢查 hook，預設是要。Claude Code 寫進 `.claude/settings.local.json`，之後每次編輯 UI 檔都跑偵測；第一次觸發時可能下載偵測引擎到 `~/.impeccable/bin/`。不想讓它改設定，安裝時選否 |

### 省 token

| 項目 | 用途 | 維護狀態（2026-10-08 查證） | 備註 |
|---|---|---|---|
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | 一份 SKILL.md，要 agent 只寫任務需要的程式碼。README 特別寫 "The rule was never "fewest tokens.""，驗證、錯誤處理、安全與無障礙都不能省 | 158,184★，最後 push 2026-10-08，MIT | README 的 -53% 程式碼、-45% token 等數字，是作者自己在 Claude Code 跑 39 個任務的 benchmark，屬作者自報。方向跟上面的 karpathy-skills 相近 |
| [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | 讓 agent 用「原始人式」短句回答，減少輸出 token；README 現在主打的是另一個 proxy 功能 | 110,511★，最後 push 2026-10-08，Apache-2.0 | README 開頭的 "33.2% fewer input tokens" 是 proxy 省下的輸入 token，不是說話風格的效果。說話風格的部分，README 自己的十題測試：直接叫模型 "Answer concisely." 輸出 4,334 個 token，`/caveman` 4,119，`/ultracave` 2,693，README 也寫 `/caveman` 在中位數上只比單純叫它簡潔多省 3%。說話風格這部分只省輸出，用量大頭在讀檔與上下文的人，從這裡省得有限 |

### 程式碼庫知識圖譜

把整個專案轉成圖譜，讓 agent 查圖譜而不是一直 grep。手上沒有大型程式碼庫的話用不到，要接手陌生的大 repo 時再看。

| 項目 | 用途 | 維護狀態（2026-10-08 查證） | 備註 |
|---|---|---|---|
| [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | 把專案裡的程式碼、文件、PDF、圖片、影片轉成可查詢的知識圖譜 | 124,848★，最後 push 2026-10-07，Apache-2.0 | 先裝 Python CLI（`uv tool install graphifyy`，套件名多一個 y），再用 `graphify install` 註冊成 skill。程式碼用 tree-sitter 在本機解析，不需 API key、不外傳；文件、PDF、圖片會送給你用的 AI 助手模型做語意抽取。README 開頭推的 graphify.com 是另一個商業雲端服務，用這個 repo 不需要它 |
| [Egonex-AI/Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) | Claude Code plugin，用多個 agent 分析整個專案，產生可互動的知識圖譜儀表板 | 85,581★，最後 push 2026-10-06，MIT | 原本在 Lum1104 帳號下，已轉到 Egonex-AI 組織，舊網址會自動導向。第一次 `/understand` 會分析整個專案，README 提醒大專案很耗 token；依 README 推得，分析時程式碼內容會經過你用的 coding agent 的模型；也可以改接 Ollama 等本機模型。做好的圖譜只要有 Node.js 就能開，不需要 LLM 或 API key |

### 學術研究工作流

這五個是用 Claude Code 做學術研究的整套設定。規則量大，建議挑個別做法參考，不要整包裝進自己的專案。

| 項目 | 用途 | 維護狀態（2026-10-08 查證） | 值得借的做法與注意事項 |
|---|---|---|---|
| [ericluo04/claude-academic-workflow](https://github.com/ericluo04/claude-academic-workflow) | 20 個 skill，涵蓋讀論文、文獻回顧、預先登記、投稿回覆，以及 did、iv、rdd、synthetic-control 等研究設計 | 25★，最後 push 2026-10-07，MIT（LICENSE 文末多一段致謝聲明，GitHub 因此顯示 NOASSERTION） | `bibcheck` 逐筆比對 `.bib` 與正式書目資料，抓年份錯、作者錯與 AI 編造的條目；`referee-response` 寫審查回覆信時，每一處宣稱的修改都先在稿件裡找到原文再標位置。README 註明 `review-paper` 不能拿來審別人的投稿 |
| [flonat/flonat-research](https://github.com/flonat/flonat-research) | 87 個 skill、15 個 agent、18 條規則、3 個 hook 的大型研究設定，Claude Code 與 Codex 都能用 | 146★，最後 push 2026-09-29，MIT | `code-paper-auditor` agent 會把論文裡每個數字對回產生它的程式碼與輸出檔。舊名 `claude-research`，網路上可能還有舊連結 |
| [gallantlab/literature-review-toolkit](https://github.com/gallantlab/literature-review-toolkit) | 讓 agent 照一份 `PLAYBOOK.md` 做文獻回顧的腳本組，需要 Python 3 與 xlsxwriter、python-docx | 18★，最後 push 2026-10-08，MIT | 可以裝成 Claude Code plugin；不裝的話，在請求裡點名那份 playbook 就好。README 寫明大部分程式碼與文件是 Claude 寫的 |
| [debug-zhuweijian/ai-research-toolkit](https://github.com/debug-zhuweijian/ai-research-toolkit) | 分七階段（找文獻、處理、分析、寫作、知識管理、簡報、流程串接）的研究工具組，串 paper-search、zotero、arxiv-latex、MinerU 等 MCP | 15★，最後 push 2026-06-14，MIT | 四個月沒更新。部分 MCP 預設用智譜 BigModel；MinerU 那條可能走 OpenXLab 的雲端 API，PDF 會不會上傳要自己確認 |
| [foundry-works/foundry-research](https://github.com/foundry-works/foundry-research) | Claude Code plugin，用 10 個 subagent 跑 Acquire → Read → Synthesize → Verify → Revise 五階段，產出研究報告 | 4★，最後 push 2026-05-05，MIT | README 一處寫 9 個、另一處寫 10 個 subagent，agents 資料夾實際是 10 個。跑一份報告會讀 20 到 30 篇全文 PDF，token 用量大 |

### 畫圖類 skill 審查筆記

以下四個是本站作者實際審查過原始碼、且經過第二輪獨立複核（換模型重新判斷，不是同一次審查自己再看一次）的畫圖類 skill。四者的觸發時機會互相衝突（都想搶「畫個流程圖／架構圖」這類請求），**同時只裝一個效果最好**，裝多個反而會有搶觸發的問題。

| Repo | 功能 | 複核後判定 | 關鍵發現 |
|---|---|---|---|
| [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | 40 種編輯風格架構／流程／資料圖，輸出單一自包含 HTML；可從 drawio／Mermaid／Excalidraw 匯入重繪 | 了解行為後可裝 | 會建立設定目錄、改寫自己的樣式指南、在專案裡寫一個標記檔、抓外部網站——但文件裡每一項都寫明「先徵得使用者同意」，首次使用會停下來問設定。靜態掃描器曾對它回報最高風險等級，但複核後確認那次是**掃描本身沒有跑完**（多數檔案還沒掃就先觸發執行限制），不是真的查出高風險內容；掃描器誤判 HTML 裡的排版順序註解為藏在圖裡的指令，也是同一次事件裡的另一個誤判 |
| [fredrick84823/fstack](https://github.com/fredrick84823/fstack)（僅 `skills/understanding/ascii` 子技能） | 中英混排的等寬字元圖，核心是用「顯示寬度」而非「字元數」算欄寬，解決中文字在等寬字型佔兩欄的對齊問題 | 可裝 | 四個裡風險面最小：稽核腳本只依賴 Python 標準函式庫，沒有對外部檔案或網路的相依；官方安裝法會把整個 repo 其餘 30 幾個技能一起裝進來，其中幾個會碰網路／外部帳號，建議只手動複製這一個子目錄 |
| [jasnell/opencode-skill-ascii-art-diagrams](https://github.com/jasnell/opencode-skill-ascii-art-diagrams) | 強制「規劃→畫圖→驗證」三階段流程的純 ASCII 圖，附機械化稽核腳本（檢查禁用字元、接點對齊、框寬一致） | 可裝，但觸發語氣很強勢 | 說明文字寫「必須在畫任何 ASCII 圖之前載入」，會蓋過上一項 fstack 的觸發權；不處理中文顯示寬度，中英混排時一樣會對齊失敗 |
| [HelioFernandes404/ascii-diagrams-skill](https://github.com/HelioFernandes404/ascii-diagrams-skill) | 基於一篇 CHI'24 論文分析真實 ASCII 圖整理出的 7 類樣式參考庫 | 內容乾淨，鎖版本手動複製即可裝，但目前輸給上一項 | 只有說明文件，沒有任何可執行腳本，風險面最小；輸的原因是**品質**不是安全——它沒有像 jasnell 那樣的稽核腳本，對不對齊全靠模型自己判斷。它自己 README 建議的一鍵安裝指令沒有鎖版本，屬於供應鏈風險，改用鎖定 commit 的手動複製可以繞開 |

!!! note "作者自己的決定：目前四個都先不裝"
    本站作者評估完後決定暫緩安裝，等真的需要時再照官方 plugin 方式裝最新版本，裝完再跟審查當時看過的版本比對差異——這是因為 `diagram-design` 這類會自我改寫內容的 skill，裝了之後版本會一直漂移，審查結果沒辦法一次定終身，重新核對比一次裝完就不管更划算。這不是說這四個不能裝，只是提醒：畫圖類 skill 挑一個裝、裝之前照第 1 節的步驟自己審一次，比照抄這張表的結論更可靠。

## 6. 學習資源

| 項目 | 內容 | 維護狀態（截至 2026-09-19） | 適合誰 |
|---|---|---|---|
| [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | 手工精選的 Claude Code 資源清單，公認的入口清單 | 54,285★，最後 push 2026-09-19，license NOASSERTION | 想看比本頁更全的清單時的第一站 |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 1000＋ agent skill 精選集，跨 Claude Code／Codex／Gemini CLI／Cursor | 34,581★，最後 push 2026-09-15，MIT | 找特定領域 skill 時的搜尋起點，裝之前仍要照第 1 節逐一審查 |
| [bojieli/ai-agent-book](https://github.com/bojieli/ai-agent-book) | 中文 AI Agent 原理書＋程式碼，涵蓋多代理系統設計的常見陷阱（例如同模型多樣本輸出容易同質化、不能當獨立意見） | 48,561★，最後 push 2026-09-19，Apache-2.0 | 想懂原理而不只是會用工具的中文讀者 |
| [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) | 從零拆解 Claude Code 底層運作原理的教學型迷你 harness | 77,152★，最後 push 2026-08-26，MIT | 想知其所以然、不滿足於「照著設定檔抄」的讀者 |
| [datawhalechina/hello-agents](https://github.com/datawhalechina/hello-agents) | 中文「從零構建智能體」教程，補 agent 通論知識 | 79,806★，最後 push 2026-09-18，license NOASSERTION | 跟上一項互補：一個講 Claude Code 本身，一個講 agent 通論；license 未標註，讀沒問題，要重製內容先自己確認 |
| [WenyuChiou/awesome-agentic-ai-zh](https://github.com/WenyuChiou/awesome-agentic-ai-zh) | 繁中／英／簡中三語的 agentic AI 學習地圖，240＋ 精選資源 | 7,084★，最後 push 2026-09-19，MIT | 對台灣讀者最友善的延伸閱讀入口 |
| [clayzhang-TW/claude-academic-workflow-zh](https://github.com/clayzhang-TW/claude-academic-workflow-zh) | 中文學術寫作＋Claude 工作流整理 | 74★，最後 push 2026-09-03，license NOASSERTION | 跟本站「用 Claude 做學術工作流」的定位最接近，適合交叉參考寫法；規模小、license 未標註，不建議未經自己審視就直接套用其規則 |
| [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) | Claude skill 清單，根目錄也直接收了約 30 個 skill 資料夾（artifacts-builder、mcp-builder、webapp-testing 等） | 76,699★，最後 push 2026-09-18（2026-10-08 查證） | 找 skill 時的另一個入口。README 宣稱 Apache-2.0，但 repo 沒有 LICENSE 檔，README 也說各 skill 授權不同，用之前逐個確認 |
| [the911fund/skill-of-skills](https://github.com/the911fund/skill-of-skills)（網站 [skills.911fund.io](https://skills.911fund.io)） | 自動更新的 AI coding 工具排行榜，收錄 skill、plugin、MCP server 等，依結構品質、星數成長、近期活躍度等訊號加權排名；README 由 GitHub Actions workflow 定時抓資料改寫，也可以接成 MCP server 查詢 | 62★，最後 push 2026-09-25，MIT（2026-09-25 查證） | 想掃一輪「最近有哪些工具」時的查詢起點。它是目錄，不是可以安裝的 skill；排名是自動算出的分數，不是人工審查結論（例如它的「Best of the Best」目前就收了本頁第 9 節不推薦的 `affaan-m/ECC`），從這裡找到的項目，裝之前仍要照第 1 節逐一審查。星數不多 |
| [keyuchen21/agentic-engineering-handbook](https://github.com/keyuchen21/agentic-engineering-handbook) | 英文的 agent 工程學習路線，分核心的 Phase 0–6（agent loop、MCP、context 與 skill、harness、coding agent、evals 與安全），另加進階的 Phase 7（agent 訓練與搜尋）[^fresh1]，每個階段列「先讀」「再讀」與一個實作練習，收錄 206 篇 OpenAI、Anthropic、Google 官方文章與社群資源[^fresh2] | 348★，最後 push 2026-09-22，MIT（2026-09-25 查證；內容描述 2026-10-05 更新） | 想有系統補官方文章時當閱讀清單用。本體是連結整理，Phase 0 的教學改寫自 `shareAI-lab/mini-claude-code`（README 有註明）。README 標的最後更新日是 2026-10-04，之後出的文章要自己補[^fresh3] |
| [amitshekhariitbhu/ai-system-design](https://github.com/amitshekhariitbhu/ai-system-design) | 英文的 LLM、RAG 與 AI agent 系統設計長篇教學，涵蓋推論伺服器、快取、路由、向量資料庫與 context 管理；〈Caching in AI〉分別解釋 KV Cache、Prompt Cache、Semantic Cache、Embedding Cache，提醒固定內容放在 prompt 開頭以便重用前綴 | 623★，最後 push 2026-10-03，Apache-2.0（2026-10-03 查證） | 想懂 prompt cache 為什麼沒命中、或準備 AI 系統設計面試的人，可當閱讀資料。repo 2026-09-25 才建立；作者是 Outcome School 創辦人，README 宣傳自家課程，延伸閱讀連結多導向自家部落格 |

## 7. 簡報、影片與圖表

這幾個都是讓 coding agent 寫程式碼產出視覺成品：簡報是 React 元件，影片是逐幀渲染的網頁，圖是單檔 HTML。

| 項目 | 用途 | 維護狀態（2026-10-08 查證） | 備註 |
|---|---|---|---|
| [open-slide/open-slide](https://github.com/open-slide/open-slide)（官網 [open-slide.dev](https://open-slide.dev)） | 給 coding agent 用的網頁簡報框架：每頁是 1920×1080 的 React 元件，可匯出靜態 HTML、PDF 與可編輯的 PPTX。內建 Claude Code skill，可以在 dev server 點元素留言，再用 `/apply-comments` 讓 agent 照留言改 | 9,083★，最後 push 2026-10-08，MIT；`@open-slide/core` 2.0.1（2026-09-27） | 原本在 `1weiho/open-slide`，已轉到 open-slide 組織。PPTX 是把頁面轉成原生文字方塊、形狀與圖片，版面不保證跟瀏覽器一模一樣。CLI 與 core 套件的原始碼沒有 postinstall，也查不到分析或遙測程式碼；會連 npm registry 檢查新版（沒找到關閉選項），svgl 與 Google Fonts 是 dev server 的代理路由，看路由設計應該是用到 logo、字型挑選時才連。dev server 沒加 `--host` 時，啟動畫面會提示 "use --host to expose"，預設只在本機（依 Vite 的預設行為推得）。SECURITY.md 還是 GitHub 範本，沒有漏洞通報管道。跟 Marp 這類 Markdown 投影片是兩條路線 |
| [remotion-dev/remotion](https://github.com/remotion-dev/remotion)（給 agent 的說明：[Prompting videos with coding agents](https://www.remotion.dev/docs/ai/coding-agents)） | 用 React 寫影片，一幀一幀渲染。官方原文 "Remotion works well with coding agents such as Claude Code, Codex, Kimi Code and OpenCode." | 62,483★，最後 push 2026-10-08；自訂的 Remotion License，GitHub 顯示 NOASSERTION | 不是 OSI 開源授權。依 2026-10-08 的 LICENSE.md：個人、3 人以下的營利組織、非營利組織可以免費用（含商用），其他公司要買 Company License；LICENSE 也預告 5.0 版授權會小幅調整 |
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | 把 HTML、CSS、媒體與可逐幀定位的動畫渲染成結果固定的 MP4，README 原文 "Write HTML. Render video. Built for agents." | 58,931★，最後 push 2026-10-08，Apache-2.0 | 需要 Node.js 22 以上與 FFmpeg。README 寫沒有按次渲染費，也沒有商用門檻。版本更新很快（2026-10-08 已是 v0.8.141） |
| [tt-a1i/archify](https://github.com/tt-a1i/archify) | 把想理解、規劃或分享的東西做成可互動的單檔 HTML 圖：架構圖、流程圖、時序圖、資料流等，可匯出 PNG | 79,661★，最後 push 2026-10-08，MIT | 以 skill 安裝（`npx skills add tt-a1i/archify -g`），這條指令不鎖版本，照第 1 節第 4 步自己處理。產出的 HTML 寄給別人，對方不用裝任何東西就能開。會定期抓一份固定的版本清單來提醒更新，README 寫伺服器收不到版本、專案資料與提示內容，設 `ARCHIFY_UPDATE_CHECK_DISABLED=1` 可關。觸發時機可能跟第 5 節的畫圖類 skill 重疊，挑一個裝 |

## 8. 本機語音轉錄與本機模型

錄音、訪談這類資料不想送上雲端時，可以全程在自己電腦處理。README 寫「完全離線」不代表沒有遙測，下表的網路行為是讀原始碼確認的，第一次用建議先斷網試。

| 項目 | 用途 | 維護狀態（2026-10-08 查證） | 網路行為與注意事項 |
|---|---|---|---|
| [kaixxx/noScribe](https://github.com/kaixxx/noScribe)（官網 [noscribe.de](https://noscribe.de)） | 訪談逐字稿，README 原文 "It runs completely locally on your computer" | 2,190★，最後 push 2026-10-06，GPL-3.0 | 程式碼裡看到的網路請求只有連 GitHub 查有沒有新版，把 `config.yml` 的 `check_for_update` 改成 false 就關掉了（README 沒寫，看程式碼得知）。第一次使用會不會另外下載模型沒查 |
| [chidiwilliams/buzz](https://github.com/chidiwilliams/buzz) | 一般用途的語音轉文字桌面 App，支援 Vulkan，內顯也能加速 | 21,882★，最後 push 2026-10-02，MIT | 預設送使用統計到 PostHog：每次啟動送出版本、語系、作業系統與 CPU 架構，附一組隨機安裝編號；程式碼裡只看到這一個事件，不含錄音內容。只能用環境變數 `BUZZ_DISABLE_TELEMETRY` 關（設任何值都會停用），設定畫面沒有開關，README 也沒提，寫在官方文件的 Preferences 頁。啟動時另外會查新版，1.4.5 起可用 `BUZZ_DISABLE_UPDATE_CHECK` 關。Windows 安裝檔沒有簽章 |
| [Zackriya-Solutions/meetily](https://github.com/Zackriya-Solutions/meetily) | 會議記錄：本機轉錄，再產生摘要 | 31,534★，最後 push 2026-09-15，MIT | 使用統計預設關閉，要自己到設定開。摘要可以選 Ollama（本機），也可以接 Claude、Groq、OpenRouter、OpenAI 等雲端服務；README 寫 "No data ever leaves your computer"，但摘要選了雲端模型，逐字稿就會送到那家。另有付費 PRO 版 |
| [thewh1teagle/vibe](https://github.com/thewh1teagle/vibe) | 離線轉錄桌面 App，也能接 Ollama 做摘要 | 7,719★，最後 push 2026-10-06，MIT | README 寫 "no data ever leaves your device"，但使用統計（Aptabase）預設開啟，官方發行版建置時有放入統計金鑰，所以下載的安裝檔預設會送（依原始碼與建置設定推得，沒有實裝驗證），設定的隱私頁可以關。送的內容有隨機安裝編號、App 與作業系統版本、檔案副檔名、音檔長度，失敗時含完整錯誤訊息 |
| [WEIFENG2333/VideoCaptioner](https://github.com/WEIFENG2333/VideoCaptioner) | 影片字幕：語音辨識、翻譯、上字幕 | 16,185★，最後 push 2026-09-12，GPL-3.0 | 免設定就能用的免費辨識引擎 `bijian`、`jianying`，看原始碼是把音訊上傳到 Bilibili 必剪與字節跳動剪映的雲端服務，README 沒有這項提醒。私人錄音可以考慮 README 列的 `faster-whisper` 或 `whisper-cpp` 引擎，但這兩個是否全程在本機，沒有追程式碼確認，第一次用請先斷網試 |

noScribe 與 VideoCaptioner 是 GPL-3.0：自己安裝使用沒有影響；要散布含它們程式碼的專案，就要依 GPL 釋出原始碼。

| 項目 | 用途 | 維護狀態（2026-10-08 查證） | 備註 |
|---|---|---|---|
| [ollama/ollama](https://github.com/ollama/ollama) | 本機跑開源模型的命令列工具與 API 服務 | 182,567★，最後 push 2026-10-08，MIT；最新 v0.40.1（2026-10-07） | 預設在 `127.0.0.1:11434` 提供 API，方便讓腳本或其他程式串接。GGUF 模型主要由內建的 llama.cpp 引擎執行；Apple Silicon 上另有 MLX 引擎，跑 safetensors 格式的模型 |
| [LM Studio](https://lmstudio.ai)（閉源） | 有圖形介面的本機模型 App，可以直接搜尋、下載 Hugging Face 上的模型 | 閉源，沒有 repo 數據；使用條款版本日期 2026-08-23 | 在 Mac、Windows、Linux 上用 llama.cpp 執行，Apple Silicon 另支援 MLX。MoE 模型可以在進階載入設定把專家權重放到 CPU（2025-08 的 v0.3.23 加入，選項名 "Force Model Expert Weights onto CPU"），顯示卡記憶體不夠時有用。官方 2025-07 宣布個人與工作使用都免費；現行條款寫部分功能可能收費 |

兩個可以並用：Ollama 給程式串接，LM Studio 拿來試新模型、調載入設定。

## 9. 看起來很熱門，但我們不推薦的

- **一鍵裝進十幾個 AI 工具設定目錄的合集**：這類 repo（例如 `affaan-m/ECC`、`msitarzewski/agency-agents`）的共通模式是安裝腳本會同時寫入 `.claude`／`.codex`／`.cursor`／`.gemini` 等一整排工具的設定目錄，還帶有會自動執行的 hooks，甚至要求裝一個「自動更新」的常駐程式。內容量大到不可能真的逐條審查完，等於直接違背第 1 節「先讀完再裝」的基本原則；「一次信任、持續自動更新、跨十幾個工具寫入」這種架構本身就是不必要的攻擊面，即使沒查到具體的惡意行為也一樣。這兩者的星數成長速度相對於功能範疇明顯偏快，值得對星數本身保持懷疑。
- **系統提示詞洩漏合集**——網路上流傳的一批 repo，內容是透過技術手段從其他商業 AI 產品「萃取」出來的系統提示詞。這類內容通常不是原廠授權公開的，維護者自己的授權條款只涵蓋他們的彙編排版工作，不代表洩漏內容本身可以自由使用；多數被萃取的產品服務條款也明文禁止這種萃取與散布。公開推薦這類資源等於間接為「洩漏他人系統提示詞」背書，有著作權與服務條款的灰色地帶風險，所以這裡不列名稱、不附連結。

## 資料來源

| 標記 | 來源 | URL |
|---|---|---|
| [1] | Six Million (Suspected) Fake Stars on GitHub（arXiv 2412.13459，ICSE '26） | <https://arxiv.org/abs/2412.13459> |
| [2] | Reducing cost and improving performance with Claude Platform（Anthropic 部落格，2026-09-08，介紹 `/claude-api prompt-audit`） | <https://claude.com/blog/reducing-cost-and-improving-performance-with-claude-platform> |
| [3] | Mods overview（Claude Code 官方文件，2026-10-08 查證，當時版本 v2.1.294） | <https://code.claude.com/docs/en/plugins/mods/overview> |

stars／最後 push 日期除另有標註外，均為 2026-09-19 用 GitHub API（`gh api repos/<owner>/<repo>`）即時查證的快照。2026-09-25 補入的 OpenSpec、Orca、skill-of-skills 三列，stars 與最後 push 用 [ungh.cc](https://ungh.cc) 的公開 GitHub 查詢 API（`/repos/<owner>/<repo>`）查，並跟 shields.io 的星數徽章交叉比對；license 對照 repo 裡的 LICENSE 檔。2026-10-03 補入的 ai-system-design 1 項，stars、最後 push 與建立日期用 [GitHub 公開 API](https://api.github.com/repos/amitshekhariitbhu/ai-system-design) 即時查證；license 對照 repo 裡的 LICENSE 檔，內容與限制對照 README 原文及其中的連結。2026-10-08 補入的各列與第 7、8 節，stars、最後 push 與建立日期用 GitHub API（`gh api repos/<owner>/<repo>`）即時查證，license 對照 repo 裡的 LICENSE 檔；功能說明對照 README 原文；網路行為、hook 與遙測另外讀了 repo 裡的程式碼確認，README 沒寫、只從程式碼得知的地方會註明；Claude Code Mods 與 You should know 對照官方文件與 changelog；LM Studio 對照官方文件、部落格與使用條款頁。

延伸：[SKILL、Plugin、MCP 與 Subagent](extensions.md)｜[MCP 入門與實戰](mcp.md)｜[把教材做成 SKILL](skill-build.md)

[^fresh1]: 2026-10-05 依官方原文更新，出處：<https://github.com/keyuchen21/agentic-engineering-handbook>
[^fresh2]: 2026-10-05 依官方原文更新，出處：<https://github.com/keyuchen21/agentic-engineering-handbook>
[^fresh3]: 2026-10-05 依官方原文更新，出處：<https://github.com/keyuchen21/agentic-engineering-handbook>
