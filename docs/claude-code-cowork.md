# 同時使用 Claude Code 與 Claude Cowork

> 查證日期：2026-09-17。Cowork 正在被併進一般 Chat，不同方案看到的介面不一樣，請以你自己帳號畫面與官方最新說明為準。

Claude Code 與 Cowork 都是 Anthropic 自己的產品，底層甚至是同一套東西：官方明講「Cowork uses the same agentic architecture that powers Claude Code」[S1]，桌面版的 Cowork session 實際上就是由 Claude Code 執行的 [A5]。但「底層相同」不等於「工作內容互通」——**兩邊沒有檔案自動同步這回事**：雲端 session 跑在隔離沙箱裡，本機檔案只限於你在桌面版連接的資料夾 [S5][S4]。任務交接官方只有一條路，而且已經不開放新使用者 [S6]。共用的是帳號層的設定（connector、skill、plugin、額度），不是你手上這份工作；完整對照見下面的互通表。

所以這頁要回答兩件事：**你現在到底有沒有 Cowork 可以用**，以及在沒有自動互通的前提下，「同時使用」實務上長什麼樣子。想找 Cowork 搭 OpenAI Codex 的做法，那是另一個題目，見 [Claude Code + Codex 協作](claude-codex.md)。

## 第一步：先確認你的帳號是哪一種現況

2026-09 起 Anthropic 正在把 Cowork 併進一般 Chat，**分階段推出、不是一次全面生效**，所以讀者之間看到的畫面會不一樣。判斷方法是官方自己給的：

> 「If you're on a Pro or Max plan and your message box still shows "Chat" and "Cowork" options, you don't have it yet.」[S2]

打開 claude.ai 或桌面版，看訊息框：

| 你看到的 | 代表 | 這頁怎麼讀 |
|---|---|---|
| 訊息框還有 **Chat／Cowork** 兩個選項 | 尚未合併，Cowork 還是一個要手動切過去的獨立模式 | 下面提到「切到 Cowork」的步驟照做 |
| 沒有這兩個選項了 | 已經合併，**沒有獨立 Cowork 模式可切換**，原本限定 Cowork 才有的能力（本機檔案、瀏覽器、長時間代理工作）在任何對話都會自動用到 [S2] | 下面提到「切到 Cowork」的地方，改成「直接在一般對話裡講」 |

各方案的時程，官方目前的說法是：Pro 與 Max 先開始、在數週內推給既有與新使用者，**Team 與 Free 方案「隨後跟上」但尚未開始**，Enterprise 則是「管理員會在任何變動前至少 30 天收到通知」[S7][S2]。合併之後不能切回舊的分開模式，既有的 Cowork 任務、專案、connector、skill、artifact 與檔案會沿用，原本的 Cowork 任務也照舊打得開、可以繼續 [S2]。

**兩種現況有一件事是一樣的：Claude Code 不受影響。** 官方在合併公告裡特別寫了「The model picker and the "Code" tab are where they were」[S2]；桌面版 App 的三個分頁（Chat 對話、Cowork 長時間代理工作、Code 軟體開發）當中，這次動到的是前兩個 [A1]。

> **整理者說明**：也就是說，這頁後面所有牽涉 Claude Code 的步驟，不論你的帳號合併了沒有都一樣。會變的只有「Cowork 那一端要怎麼開」。Cowork 本身的方案門檻另見[付費區](paid-tier.md)。

## 兩邊各自擅長什麼（官方定位）

- **Claude Code**：桌面版 Code 分頁與終端機 CLI，面向軟體開發 [A1]。
- **Cowork**：面向一般知識工作——官方舉的例子是整理好的文件、歸檔的檔案、彙整過的研究，產出包含帶公式的 Excel、PowerPoint 與格式化文件 [S1]。

Dispatch 的官方路由規則把分界講得最直白：「Development tasks run in Claude Code; knowledge work runs in Cowork.」[S6] 官方另外舉例，會被導到 Code 的典型任務是修 bug、更新相依套件、跑測試、開 PR；**研究、文件編輯、試算表工作留在 Cowork** [A1]。

## 官方到底提供了什麼互通？查證結果

把「互通」拆開來看，答案不是全有也不是全無：

| 層面 | 現況 | 來源 |
|---|---|---|
| 執行架構 | 相同。Cowork 用的就是驅動 Claude Code 的那套 agent 架構，桌面版 Cowork session 由 Claude Code 執行 | [S1][A5] |
| Connectors | **共用**。用 claude.ai 帳號登入 Claude Code 後，你在 claude.ai 加的 connector 會自動出現在 Claude Code，`/mcp` 裡會標示來自 claude.ai | [A3] |
| Skills／Plugins | **部分共用**。在 claude.ai 帳號層啟用的會同步到兩邊；但只存在於本機 `~/.claude` 的不會給 Cowork | [A1][A2] |
| Artifacts | Claude Code 可以把產出發佈成 claude.ai 上的 artifact，`/artifacts` 能列出你擁有與別人分享給你的 artifact，並附加到當前 session | [A4] |
| 任務路由 | 有一條：Dispatch 會把開發任務丟給 Claude Code。但限制很重，見下一節 | [A1][S6] |
| 對話紀錄 | 在桌面版或 Cowork 開始／最近接續的 session，transcript 存在本機 `~/.claude` 裡，且預設不受一般保留期限清除 | [A7] |
| 用量額度 | 共用。Team／Enterprise 的每席位額度由 Claude chat、Claude Code、Cowork 共吃 | [A8] |
| **檔案** | **沒有自動互通機制。** 雲端 session 的執行環境是隔離沙箱，本機檔案只限於你在桌面版連接的資料夾 | [S5][S4] |
| **claude.ai Projects** | 查無「終端機 Claude Code session 可以掛上一個 claude.ai Project」的官方說明 | 整理者觀察，見下 |
| **記憶** | Cowork 與 chat 之間官方寫明共用記憶；Claude Code 這一端查無互通說明 | [S3] ＋ 整理者觀察 |

關於 Projects 與記憶這兩格，把查證過程寫清楚比較誠實：

- Anthropic 的 Agent SDK 工具參考裡確實有一個 `Projects` 工具，說明是「Reads and writes the claude.ai Project attached to the session」，方法包含讀、寫、搜尋 project 知識庫 [A9]。但**「session 附掛了一個 claude.ai Project」這個前提在哪些情況成立，官方文件沒有寫**；本次查證沒有找到任何一頁說終端機 session 可以指定掛上某個 claude.ai Project。
- Cowork 官方入門頁寫 Cowork 與 chat 有「shared memory」，chat 記得的事 Cowork 用得到，Cowork 任務裡出現的事也會回流到 chat [S3]。**但這條講的是 Cowork↔chat**；以 `code.claude.com` 官方文件全文比對，查不到任何「Claude Code 的 `CLAUDE.md` 或 auto memory 與 claude.ai 記憶互通」的說明 [A10]。

> **整理者觀察**：所以要給讀者的白話結論是——**帳號層的「設定」會跟著你走，手上這份「工作」不會**。Cowork 剛做完的報告，Claude Code 不會自己知道；你在 `CLAUDE.md` 裡定的專案規矩，Cowork 也不會讀到。這是從「文件裡查不到」推出的結論，不是官方發過的聲明。

## 唯一的官方任務路由：Dispatch（而且正在關門）

Dispatch 是住在 Cowork 分頁裡的一個常駐對話，你丟任務給它，它決定怎麼處理。一個任務會變成 Code session 有兩種路徑：你直接說「開一個 Claude Code session 修登入的 bug」，或者 Dispatch 自己判斷這是開發工作而生出一個 [A1]。生出來的 session 會出現在 Code 分頁側邊欄並標上 **Dispatch** 標記，跑完或需要你批准時手機會收到推播 [A1]。

這是本次查證找到的**唯一一個官方的、跨 Cowork 與 Claude Code 的任務交接機制**。但它的門檻要看清楚：

- 官方寫「This capability is in limited beta for Pro and Max plans on Claude Cowork」，且需要桌面版與手機版 App 同時具備 [S6]。
- 官方另外寫「**Dispatch isn't available to new users.** If you already use Dispatch, you can keep using it for now」[S6]。
- Claude Code 官方文件也寫 Dispatch 需要 Pro 或 Max，**Team 與 Enterprise 方案不提供** [A1]。

> **整理者觀察**：對現在才讀到這頁的多數人來說，Dispatch 實質上不是一個可以照做的選項——官方已經明說不開放新使用者。所以下面的工作流程不建立在 Dispatch 上，只當作「如果你剛好已經有，它會幫你自動分流」的補充。

## 檔案要怎麼從一邊交到另一邊

既然沒有自動互通，剩下的就是三條手動路。條件差很多：

**路徑一：桌面版連接的本機資料夾（推薦，也是唯一真正順手的一條）**
Cowork 在桌面上可以直接讀寫你的本機檔案，不需要手動上傳下載 [S3]。但條件很死：雲端 session 要碰到你連接的本機資料夾，**必須桌面 App 開著、而且該 session 是從桌面版啟動的**；App 一關，session 繼續跑但碰不到本機檔案 [S4]。本機檔案存取只限於你連接過的資料夾，每次本機工具呼叫都會比對你的權限 [S5]。合併後的新體驗也維持同樣條件：「Claude reaches your local files, the built-in browser, and computer use only while Claude Desktop is open」[S2]。

**路徑二：手動下載**
雲端 session 跟著你的 Claude 帳號走，產出可以在 session 裡預覽與下載 [S3]。沒有桌面版、或不想連接資料夾的人只能走這條：下載檔案 → 放進某個資料夾 → 讓 Claude Code 去讀。

**路徑三：Artifact（適合「給人看」的產出，不適合當資料交換）**
Claude Code 可以把 session 產出發佈成 claude.ai 上的 artifact，`/artifacts` 能列出你擁有與分享給你的 artifact，按 Enter 附加到當前 session，清單是從 claude.ai 帳號讀的 [A4]。Claude Code 的變更紀錄也顯示 Cowork session 一樣會用到 Artifact 工具與讀取 artifact [A6]。

> **整理者觀察**：把上面兩條拼起來，合理推論是「兩邊發佈的 artifact 落在同一個 claude.ai 帳號的 gallery，因此可以互相看到」。但**官方沒有一頁明講這件事**，請當推測。要確認只要一分鐘：在 Cowork（或合併後的對話）讓 Claude 做一個 artifact，然後在終端機 Claude Code 裡跑 `/artifacts`，看清單裡有沒有它。有就是通的，沒有就走路徑一或二。

## 實際工作流程：用同一個交換資料夾把兩邊接起來

這是本頁最推薦、也最不依賴 beta 功能的做法。**以下步驟除了標注來源的部分，都是整理者的操作建議，不是官方規範。** 情境假設是一份要交出去的季度報告：資料整理與文件產出交給 Cowork，需要可重跑、要版控的部分交給 Claude Code。

### 步驟

**1. 先在本機建一個交換資料夾。** 例如 `D:\handoff\2026-q3-report\`（macOS：`~/handoff/2026-q3-report/`）。重點是這個資料夾要獨立於你的正式專案目錄，出事只會髒一個資料夾。

**2. 打開桌面版 Claude，把這個資料夾連接給 Claude。**
- 還看得到 Chat／Cowork 選項的人：在訊息框切到 **Cowork**，再連接資料夾。
- 已經合併的人：直接在一般對話裡給 Claude 這個資料夾的存取權 [S2]。
- 不論哪一種，**桌面 App 要保持開著**，而且這個 session 要從桌面版開始 [S4]。

**3. 讓 Cowork 把產出「寫成檔案存進那個資料夾」，而不是只回在對話裡。** 這句要明講，例如：

```
把這批會議紀錄整理成一份報告草稿，直接寫成 D:\handoff\2026-q3-report\draft.md，
數據另外存成同一個資料夾裡的 data.csv。不要只在對話裡回給我。
```

理由是雲端 session 的檔案本來是存在你的 Claude 帳號裡，桌面 App 一關就碰不到本機檔案了 [S4]——落到本機磁碟才算真的交接完成。

**4. 用檔案總管確認檔案真的在那裡。** 這一步不要跳過，它是「Cowork 說它寫好了」與「檔案真的存在」之間唯一的驗證。

**5. 開終端機，讓 Claude Code 接手。**

```bash
cd D:\handoff\2026-q3-report
claude
```

或是留在原本的專案目錄、另外授權這個資料夾：

```bash
claude --add-dir D:\handoff\2026-q3-report
```

**6. 把「需要重跑、需要留紀錄」的部分交給 Claude Code。** 例如：把 `data.csv` 的清洗步驟寫成一支可重跑的腳本、替報告裡的數字加上驗算、`git init` 之後 commit 起來，之後每季只要換輸入檔就能重跑。這正是官方分界裡屬於 Code 的那一半 [S6]。

**7. 要回頭再讓 Cowork 修稿，就把結果寫回同一個資料夾**，再回到桌面版那個對話說「檔案更新了，接著改」。Cowork 讀得到，因為那是它連接過的資料夾 [S5]。

### 最小測試：確認這條路真的通

在做真正的工作之前，先花兩分鐘確認交接會成功。

在 Cowork（或合併後的對話）那端說：

```
在我連接的 handoff 資料夾裡建一個 handoff-test.md，內容只要寫今天的日期。
```

然後在終端機的 Claude Code 裡說：

```
讀 D:\handoff\2026-q3-report\handoff-test.md，回報它的內容，不要改任何東西。
```

- **讀得出日期** → 交換資料夾這條路通了，可以開始正式工作。
- **說找不到檔案** → 多半是 Cowork 把檔案寫進了雲端 session 而不是本機資料夾。回頭確認桌面 App 開著、session 是從桌面啟動的、而且那個資料夾確實連接過 [S4]。
- **沒有桌面版可用**（例如只有網頁版）→ 這條路走不通，改用手動下載（路徑二）。

### 沒有 Cowork 的人怎麼辦

Cowork 有方案門檻（見[付費區](paid-tier.md)），Team 與 Free 方案的合併也還沒開始 [S7]。如果你手上只有一般 Chat 與 Claude Code，這個工作流程的骨架照樣成立，只是第 2～3 步換成「在 Chat 裡整理、把結果貼進或下載到交換資料夾」。差別是要多幾次複製貼上，交接點沒有變。

## 不要期待的事（整理者觀察）

以下都是本次查證**沒有找到**官方支援的做法，寫出來是為了讓你不要浪費時間找：

- **Claude Code 不能呼叫 Cowork。** 查無任何 CLI 指令、旗標或 API 可以從 Claude Code 這一端開一個 Cowork 任務。目前有官方路由的方向只有一個，而且是反過來的（Dispatch → Code session），還不開放新使用者 [S6]。
- **`CLAUDE.md` 不會跟著到 Cowork。** Cowork 的 skill、plugin 與 connector 來自桌面版側邊欄的 **Customize**，透過 claude.ai 帳號同步，**官方明寫不讀 CLI 的 `~/.claude` 目錄** [A1][S1]。要讓 Cowork 遵守同一套專案規矩，得把規矩放進 Customize 或 Project 的指示，不能指望它讀你的 `CLAUDE.md`。
- **只存在於 `~/.claude/skills/` 的 skill，Cowork 與雲端 session 都吃不到**；要在那些 session 用，得先在 claude.ai 帳號啟用它 [A2]。反過來，claude.ai 上啟用的 skill 會被下載到終端機 session 的 `~/.claude/skills/synced/`，但官方對這些同步來的 skill 有額外限制，例如在你的機器上不執行它們的 `!` 指令 [A2]。
- **不要期待兩邊同時改同一個檔案。** 官方文件沒有針對這個情境的說明；*整理者建議*：交接時一次只讓一邊動檔案，或乾脆讓交換資料夾成為 git repo，改壞了隨時 `git diff` 看得出來、隨時還原。

## 怎麼選（整理者觀察）

| 你想做的事 | 建議 |
|---|---|
| 讀檔、整理、產出 Word／Excel／簡報類文件 | Cowork（或合併後的一般對話）[S1] |
| 需要重跑、需要版控、需要測試的處理 | Claude Code [S6] |
| 兩者都要，而且中間要交檔案 | 桌面版連接的交換資料夾（上面那套流程） |
| 只有網頁版、沒有桌面 App | 手動下載再交給 Claude Code；本機資料夾那條路需要桌面 App 開著 [S4] |
| 想讓系統自己決定任務丟哪邊 | Dispatch，但官方已明說不開放新使用者 [S6] |
| 想在對話裡看到 Claude Code 的產出 | 讓 Claude Code 發佈成 artifact，再從 claude.ai 開 [A4] |

## 資料來源（2026-09-17 查證）

| 標記 | URL | 用途 |
|---|---|---|
| A1 | code.claude.com/docs/en/desktop | 桌面版三個分頁；Dispatch 產生 Code session 的兩種路徑與 Pro/Max 限制；Cowork 的 skill／plugin／connector 來自 Customize、不讀 `~/.claude` |
| A2 | code.claude.com/docs/en/skills | Cowork 與雲端 session 不讀 `~/.claude/skills/`；claude.ai 同步 skill 的下載位置與額外限制 |
| A3 | code.claude.com/docs/en/mcp#use-mcp-servers-from-claude-ai | claude.ai 上的 connector 自動在 Claude Code 可用 |
| A4 | code.claude.com/docs/en/artifacts | Claude Code 發佈 artifact 到 claude.ai；`/artifacts` 列出擁有與分享的 artifact 並附加到 session |
| A5 | code.claude.com/docs/en/managed-settings | 桌面版 Cowork 的 session 由 Claude Code 執行；不同執行位置的政策讀取差異 |
| A6 | code.claude.com/docs/en/changelog | Cowork session 使用 Artifact 工具、讀取他人 artifact 的變更紀錄 |
| A7 | code.claude.com/docs/en/claude-directory | 桌面版／Cowork session 的 transcript 保存在本機 `~/.claude` 與其保留規則 |
| A8 | code.claude.com/docs/en/costs | Team／Enterprise 席位額度由 chat、Claude Code、Cowork 共用 |
| A9 | code.claude.com/docs/en/agent-sdk/typescript | `Projects` 工具定義：讀寫「附加在 session 上的 claude.ai Project」 |
| A10 | code.claude.com/docs/llms-full.txt | Claude Code 官方文件全文；用於比對記憶互通、Cowork 相關敘述的查證依據 |
| S1 | claude.com/docs/cowork/overview | Cowork 與 Claude Code 同一套 agent 架構；產出型態；Customize 來源、不讀 `~/.claude` |
| S2 | support.claude.com/en/articles/16761823-claude-cowork-and-chat-are-one-claude | 合併後如何判斷自己有沒有；Code 分頁不變；既有資料沿用；本機檔案需桌面 App 開著 |
| S3 | support.claude.com/en/articles/13345190-get-started-with-claude-cowork | 桌面直接讀寫本機檔案；雲端 session 跟著帳號、可預覽下載；與 chat 共用記憶 |
| S4 | support.claude.com/en/articles/15520349-use-claude-cowork-on-web-desktop-and-mobile | 雲端 session 存取本機資料夾的條件（桌面 App 開著、session 從桌面啟動） |
| S5 | support.claude.com/en/articles/14479288-claude-cowork-architecture-overview | 雲端沙箱與本機 VM 的隔離設計；本機檔案存取限於已連接資料夾並逐次比對權限 |
| S6 | support.claude.com/en/articles/13947068-dispatch | Dispatch 的 limited beta 狀態、Pro/Max 限制、不開放新使用者、開發任務走 Claude Code |
| S7 | claude.com/blog/cowork-is-now-claude | 合併推出順序：Pro/Max 先、Team 與 Free 隨後、Enterprise 至少 30 天前通知 |

註：A 系列為 Claude Code 官方文件（code.claude.com），S 系列為 Anthropic 產品文件、官方說明中心與官方部落格。

延伸：[Claude Code + Codex 協作](claude-codex.md)｜[Claude Code 接上 Obsidian](claude-code-obsidian.md)｜[付費區](paid-tier.md)｜[AI 介面比較總表](tools-compare.md)
