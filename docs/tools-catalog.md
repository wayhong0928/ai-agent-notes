# 好用工具清單

> 查證日期：2026-09-19。stars／最後更新日期／license 都是這天用 GitHub API 即時查證的快照，之後會變動，請自己重查一次再決定要不要裝。

這頁收的是本站作者自己讀過、審查過的 Claude Code／Codex 官方文章、skill、plugin、MCP 與學習資源。目標是「精選」不是「收全」：能找到的相關 repo 遠不只這些，這裡只留下讀過原始碼、判斷過風險之後還願意留著的項目。想看完整清單，第 6 節的幾個 awesome-list 本身就是更大的入口。

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

## 4. MCP：只列推薦項目

MCP 的協定原理、安裝步驟、scope 與 OAuth 設定，還有 Windows 上的踩坑實錄，都寫在專篇[MCP 入門與實戰](mcp.md)，這裡不重複，只列額外兩個值得知道、但那篇沒收的項目。

| 項目 | 為什麼值得知道 | 維護狀態（截至 2026-09-19） |
|---|---|---|
| [ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) | 用 Chrome DevTools Protocol 讓代理檢查效能、console、網路請求，比純截圖驗收更深入 | 52,288★，最後 push 2026-09-18，Apache-2.0 |
| [modelcontextprotocol/inspector](https://github.com/modelcontextprotocol/inspector) | 官方除錯／視覺化工具，裝任何 MCP server 之前先用這個看它實際會呼叫哪些方法，等於幫第 1 節「安裝前審查」的第 2 步省力 | 10,913★，最後 push 2026-09-19，license 未標註 |

[MCP 入門與實戰第 9 節](mcp.md#9)已經收了 `upstash/context7`、`microsoft/playwright-mcp`、`github/github-mcp-server` 三個常用項目，這裡不重複列。另外 `MarkusPfundstein/mcp-obsidian`（透過 Obsidian Local REST API plugin 讀寫 vault）功能對 Obsidian 使用者很直接，但需要常駐 Obsidian 並在本機開一個 REST API port，屬於「功能對得上、但曝險面要自己權衡」的項目，不列入前兩項推薦。

## 5. 社群 Skill 與 Plugin

### 一般用途

| 項目 | 用途 | 維護狀態（截至 2026-09-19） | 備註 |
|---|---|---|---|
| [blader/humanizer](https://github.com/blader/humanizer) | 去 AI 感改寫，依 Wikipedia〈Signs of AI writing〉整理的判準 | 約 5.0 萬★，MIT，最後更新 2026-09-06 | 本站作者實際在用，中英文都適用 |
| [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) | 減少 LLM 寫程式時的過度工程化，強調外科手術式小改動與可驗證的完成標準 | 約 21.4 萬★，license 欄位為空（使用前自行確認），最後更新 2026-04-20 | 本站作者實際在用 |
| [wshobson/agents](https://github.com/wshobson/agents) | 跨 Claude Code／Codex／Cursor／OpenCode／Copilot 的多用途 plugin marketplace，agent／skill／command 種類齊全 | 39,789★，最後 push 2026-09-19，MIT | 規模大，建議先挑單一 agent／skill 讀過再裝，不要整包信任 |
| [github/spec-kit](https://github.com/github/spec-kit) | GitHub 官方的 Spec-Driven Development 工具包，把「先出規格再執行」流程化 | 137,848★，最後 push 2026-09-18，MIT | 跟「先出規格、再交給執行者」這種分工方式同構，即使不整套裝，讀它怎麼把規格寫成可驗證的格式也有參考價值 |

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
| [1weiho/open-slide](https://github.com/1weiho/open-slide) | 代理導向的網頁互動簡報框架 | 7,613★，最後 push 2026-09-17，MIT | 走互動網頁路線而非靜態投影片，跟本站另外整理的 Marp 簡報方法論剛好是對照組，觀察用途非急需 |

## 7. 看起來很熱門，但我們不推薦的

- **一鍵裝進十幾個 AI 工具設定目錄的合集**：這類 repo（例如 `affaan-m/ECC`、`msitarzewski/agency-agents`）的共通模式是安裝腳本會同時寫入 `.claude`／`.codex`／`.cursor`／`.gemini` 等一整排工具的設定目錄，還帶有會自動執行的 hooks，甚至要求裝一個「自動更新」的常駐程式。內容量大到不可能真的逐條審查完，等於直接違背第 1 節「先讀完再裝」的基本原則；「一次信任、持續自動更新、跨十幾個工具寫入」這種架構本身就是不必要的攻擊面，即使沒查到具體的惡意行為也一樣。這兩者的星數成長速度相對於功能範疇明顯偏快，值得對星數本身保持懷疑。
- **系統提示詞洩漏合集**——網路上流傳的一批 repo，內容是透過技術手段從其他商業 AI 產品「萃取」出來的系統提示詞。這類內容通常不是原廠授權公開的，維護者自己的授權條款只涵蓋他們的彙編排版工作，不代表洩漏內容本身可以自由使用；多數被萃取的產品服務條款也明文禁止這種萃取與散布。公開推薦這類資源等於間接為「洩漏他人系統提示詞」背書，有著作權與服務條款的灰色地帶風險，所以這裡不列名稱、不附連結。

## 資料來源

| 標記 | 來源 | URL |
|---|---|---|
| [1] | Six Million (Suspected) Fake Stars on GitHub（arXiv 2412.13459，ICSE '26） | <https://arxiv.org/abs/2412.13459> |

stars／最後 push 日期均為 2026-09-19 用 GitHub API（`gh api repos/<owner>/<repo>`）即時查證的快照。

延伸：[SKILL、Plugin、MCP 與 Subagent](extensions.md)｜[MCP 入門與實戰](mcp.md)｜[把教材做成 SKILL](skill-build.md)
