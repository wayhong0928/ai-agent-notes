# Projects 功能

> 查證日期：2026-09-19。這頁在寫的當下經過兩位查證者交叉核對，發現[免付費區](free-tier.md)與[付費區](paid-tier.md)先前寫的「Free 沒有 Projects」是錯的，已經回頭更正，見第 4 節。方案與功能變動很快，請以官方最新說明為準。

「Projects」這個詞，2026-09 這幾週在 Claude 生態裡同時指兩層東西：一個是 claude.ai 用了很久的知識庫型 Projects，另一個是 2026-09 剛在 Claude Code 上線的新版 beta。官方文件把兩者定位成同一條功能線的新舊版本，這點第 1 節先講清楚，免得跟[AI 介面比較總表](tools-compare.md)或[Claude Code + Cowork](claude-code-cowork.md)的分類方式搞混。

## 1. 現在有幾種「Projects」

先講結論：**是同一條功能線的新舊兩版，正在交接，不是兩個獨立產品。**

官方 Claude Code 文件在講新版 Projects 跟既有功能的關係時，明白把 claude.ai chat／Cowork 那個「先前的 Projects 體驗」跟新版擺在一起比較，原文：「Projects in claude.ai chat and Cowork: the earlier Projects experience, which groups conversations and reference files without threads or a coordinator. Those projects keep working as they do today **until the redesigned experience reaches them**。」[C1] 舊版目前照常運作，但官方講的方向很明確：新版最終會取代舊版，不是兩條永遠並行的產品線。

| | 舊版 Projects（claude.ai chat／Cowork） | 新版 Projects（beta，先從 Claude Code 推出） | Claude Code 本機的「專案」 |
|---|---|---|---|
| 是什麼 | 自成一體的知識庫＋對話歷史 [S1] | 一個協調對話，Claude 拆出多個雲端 thread 平行處理工作 [C1] | `CLAUDE.md` 分層＋`.claude/` 設定＋auto memory，不是一個「產品功能」，是本機運作機制 [C2] |
| 現在能不能用 | 全方案可用（含 Free，上限 5 個），見第 4 節 | 公開 beta，僅 Pro／Max，分階段推出 | 只要在用 Claude Code 就自動存在，沒有方案門檻問題 |
| 跟另外兩種的關係 | 會被新版逐步取代，官方沒給時間表 [C1] | 會載入所在 repository 的 `CLAUDE.md`，見第 6 節 [C1] | 新版 Projects 的每個 thread 都會讀它，但**不會**讀你本機的 CLAUDE.md 或本機 auto memory [C1] |

第 2–4 節講舊版，第 5 節講 Claude Code 本機的「專案」概念，第 6 節講新版 beta。

## 2. 舊版 claude.ai Projects 能放多少東西

Projects 讓你建立自成一體的工作空間，各自有獨立的對話歷史與知識庫，可以上傳文件、文字、程式碼給該 Project 底下所有對話共用 [S1]。

- **單檔上限**：知識庫檔案每檔 30MB，數量本身沒有寫死上限，但總量受 context window 容量限制 [S5]。這跟一般對話直接上傳檔案是兩組不同的限制，一般對話上傳單檔可以到 500MB、單次對話最多 20 檔 [S5]，Project 知識庫的 30MB 限制只管「長期放在 Project 裡當共用情境」的檔案。
- **RAG 模式，只有付費方案有**：知識庫內容接近 context window 上限時，官方會自動切換成 RAG（Retrieval-Augmented Generation）模式，原文「expand capacity by up to 10x while maintaining response quality」[S1]。**這個擴充只對 Pro／Max／Team／Enterprise 開放**，Free 帳號的 Project 知識庫沒有這層擴充，滿了就是滿了。

!!! note "跟一般對話上傳檔案的差異，記一句話就好"
    一般對話上傳檔案是「這次對話用一次」；Project 知識庫是「這個 Project 底下每一次新對話都看得到」。要長期重複用同一批文獻或規範，才值得放進 Project，不然直接在對話裡貼檔案更快。

## 3. Project instructions 怎麼寫

在 Project 的知識庫區塊可以設定「Set project instructions」，官方原文：「Claude will use these instructions for all the chats within the project.」[S2]

**跟帳號層級疊加的關係**：帳號層級的「Instructions for Claude」＋ Project instructions ＋ 所選 Style，三層會一起套用在 Project 裡的每一則回覆上 [S3]。沒有查到官方明確講清楚三層衝突時誰蓋過誰，這題只能標記部分查無。

**字數上限，老實講查無**：本次查證沒有在官方頁面看到「舊版 Project instructions 上限幾個字」的逐字說明；網路上流傳的「約 8,000 字元」對不到任何官方原文，不建議當成確定數字引用。倒是新版 beta Projects 的 Project instructions 有明確數字，官方原文「up to 16,000 characters」[C1]，但那是第 6 節講的新版，不能拿來當舊版的答案。

## 4. 各方案差異：Free 可以用，上限 5 個

!!! warning "2026-09-19 更正：本站先前寫「Free 沒有 Projects」是錯的"
    這頁與[免付費區](free-tier.md)、[付費區](paid-tier.md)原本都寫「Free 沒有 Projects」。經過兩位查證者各自直接讀 claude.com/pricing 與官方說明文章後確認：**Free 帳號可以用 Projects，最多建立 5 個**。開放時間查無，官方沒有寫是哪一天開始的。

| 方案 | Projects 可用性 |
|---|---|
| Free | ✅ 最多 5 個（claude.com/pricing 原文「Up to 5」；support 文章原文「Free users can create a maximum of five projects」）[P1][S1] |
| Pro | ✅ 無限量，且知識庫接近上限時可用 RAG 擴充容量 [P1][S1] |
| Max | ✅ 同 Pro [S1] |
| Team | ✅ 另有分享與協作管理 [S1][S2] |
| Enterprise | ✅ 同 Team [S1][S2] |

分享與協作僅 Team／Enterprise 開放：可用信箱單一分享，也可貼上信箱清單批次分享；權限分「Can view」（唯讀）與「Can edit」（可改指示、管理知識庫、管理成員）兩級 [S1][S2]。

## 5. Claude Code 本機的「專案」是另一套邏輯

Claude Code 側講的「專案」，不是 claude.ai 那種產品功能，是靠 `CLAUDE.md` 分層＋`.claude/` 設定＋auto memory 這三件事撐起來的本機運作機制 [C2]。完整的分層規則、`.claude/rules/*.md` 怎麼拆檔、auto memory 四種類型，[官方設定總覽](official-config.md)已經寫過，這裡不重複。

**跟 claude.ai Projects 之間，目前查無官方同步機制。** `code.claude.com/docs/en/memory` 全文沒有提到 claude.ai Projects；社群這邊把「串接 claude.ai Project 到 Claude Code」明確列為尚未實現的 feature request（GitHub issue #2511、#64779）[GH1][GH2]，也有第三方工具 `claudesync` 想自己搭橋，但那是非官方的社群方案。這題不寫成「兩者永遠獨立」比較誠實，因為官方已經表態新版 Projects 最終會取代舊版（見第 1 節）；取代之後兩邊會不會互通，本次查證沒有找到答案，只能標記查無。

## 6. 新版 Projects beta：先從 Claude Code 推出

新版是一個「協調型」對話：丟任務進去，Claude 會拆出多個 thread，每個 thread 是一個獨立的雲端 session（cloud session），在自己的 branch 上跑，關掉筆電也能繼續執行。官方原文：「A project is one ongoing conversation where Claude coordinates a stream of related work for you.」[C1]

**每個新 thread 會自動載入什麼、不會載入什麼**：

| 項目 | 單一 repository 的 project | 多個 repository 的 project |
|---|---|---|
| `CLAUDE.md` | 啟動時載入 | 每個 repository 的都載入 |
| Skills、agents、commands（`.claude/` 底下） | 載入 | 每個 repository 的都載入 |
| Plugins（`.claude/settings.json` 啟用的） | 載入 | 每個 repository 的都載入，衝突時以 Project settings 的設定為準 |
| Permission 規則、hooks、`env`（`.claude/settings.json`） | 套用到該 thread | **不套用**（改由多個 repository 上層目錄的設定決定，沒有單一 repository 的檔案可讀）[C1] |

原文明確切這條線：「Threads don't pick up anything from the Claude Code setup on your own machine.」[C1] 這句話只吃 repo 裡版控的 `CLAUDE.md`／skills／plugins，不吃你本機的 `~/.claude/CLAUDE.md` 或本機 auto memory。但**不是只認 `CLAUDE.md`**：在 claude.ai 帳號層啟用的 skills，同樣會載入每個新 thread，跟 repo 裡的 skills 是兩條獨立的來源 [C1]。

**方案限制與推出順序**：目前只開放 Pro／Max，且是分階段推送，官方原文：「Projects are in public beta on Pro and Max plans and rolling out gradually, **starting with accounts that have used cloud sessions and don't have existing projects in claude.ai chat or Cowork**. They aren't available on Team or Enterprise plans yet.」[C1] 這句話交代了三件事：新版目前只給還沒有舊版 Projects 的帳號、之後會擴大到 Team／Enterprise、也會擴大到 chat 與 Cowork，不會永遠只綁在 Claude Code。

**Project instructions 與 Project memory**：Project instructions 上限 16,000 字元，每個新 thread 與協調對話都會收到 [C1]；Project memory 是 Claude 自己寫的筆記（需求、決策、雷點），每個 thread 啟動時讀索引檔 `MEMORY.md`，跟 Claude Code 本機的 auto memory 是分開機制，只是都用 `MEMORY.md` 這個命名概念 [C1][C2]。

**不能碰什麼**：thread 只能動 GitHub repository，以及使用者上傳到 project 的檔案／資料夾／Google Drive 資料夾，官方原文：「not on files or tools that exist only on your machine」[C1]。本機資料庫、VPN 後面的服務都碰不到。

## 7. 跟 ChatGPT Projects、NotebookLM 比一比

| | claude.ai Projects（舊版） | ChatGPT Projects | NotebookLM |
|---|---|---|---|
| 能放什麼 | 檔案＋project instructions [S1][S2] | 檔案＋instructions，指示只在該 project 生效並蓋過全域自訂指示（信心中，WebSearch 摘要）[O1] | 「來源」：文件、網頁、影音等 |
| 免費方案能不能用 | ✅ 上限 5 個 [P1][S1] | 部分開放，但檔案數上限比付費方案低（信心中，數字未能對到官方逐字稿，不建議照抄）[O1] | Standard 層 50 個來源／notebook（信心高）[G1] |
| 容量擴充機制 | 付費方案接近上限時切 RAG，最多擴充 10 倍 [S1] | 查無對應機制的官方逐字說明 | 沒有擴充機制，是硬性的來源數量上限（依方案 50–600 個）[G1] |
| 是否保證只依上傳內容回答 | 查無官方逐字保證；RAG 模式講的是「擴充容量」不是「限定只用這些資料」 | 查無官方逐字保證 | 官方原文「the model uses the sources you upload to answer your questions」，信心高 [G2] |

ChatGPT 這欄的數字信心普遍偏低，官方頁面本次查證兩次都回傳 403，只能靠搜尋引擎的摘要交叉核對，不是直接讀到逐字原文。讀者要拿這幾個數字去做重要決定前，建議自己再查一次官方頁面。

## 8. Cowork 併入 Chat 之後，Project 多了什麼

2026-09-16 Cowork 併入 Chat 的公告裡，Projects 被重新定義成「在每一段對話裡都能用」，官方原文（出自 support 文章，不是部落格）：「Projects: Keep files, instructions, and context together for related work. **Projects work in every conversation.**」[S4]

實際差異：合併前，本機資料夾讀寫是 Cowork 分頁的專屬能力，要先切分頁才能用；合併後，「In Claude Desktop, give Claude access to a folder on your computer so it can read, organize, and create files there.」[S4] 一般對話本身就能碰本機資料夾，不必再切到獨立的 Cowork 模式。

**這個轉變的關鍵是「誰決定要不要動用」**：不是使用者手動切換分頁才觸發，而是 Claude 在一般對話裡自己判斷這次任務要不要用到本機檔案、connector 或其他原本限定 Cowork 才有的能力。已授權的資料夾範圍不變，但觸發方式從「使用者手動切模式」變成「Claude 自行判斷」，在意本機檔案安全的人要知道這個行為轉變，細節與逐步操作見[Claude Code + Cowork 並用](claude-code-cowork.md)。

rollout 狀態：Pro／Max 分階段推送，「More plans will follow soon, and Enterprise admins will hear from us at least 30 days before anything changes.」[B1]

## 資料來源（2026-09-19 查證）

| 標記 | URL | 用途 |
|---|---|---|
| S1 | support.claude.com/en/articles/9517075-what-are-projects | 舊版 Projects 總覽、RAG 模式、Free 上限 5 個 |
| S2 | support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects | 建立/管理、Project instructions 入口、記憶分離、Team/Enterprise 分享權限 |
| S3 | support.claude.com/en/articles/10185728-understanding-claude-s-personalization-features | Instructions／Project instructions／Style 疊加關係 |
| S4 | support.claude.com/en/articles/16761823-claude-cowork-and-chat-are-one-claude | 合併後 Projects「work in every conversation」定義、本機資料夾存取 |
| S5 | support.claude.com/en/articles/8241126-upload-files-to-claude | Project 知識庫 30MB/檔上限；一般對話上傳 500MB/檔對照 |
| P1 | claude.com/pricing | 方案功能表，Free「Up to 5」逐字 |
| C1 | code.claude.com/docs/en/claude-projects | 新版 Projects beta 完整機制：thread、CLAUDE.md/skills/plugins 載入規則、16,000 字元上限、方案限制、與舊版關係 |
| C2 | code.claude.com/docs/en/memory | Claude Code CLAUDE.md 分層、auto memory 機制 |
| B1 | claude.com/blog/cowork-is-now-claude | Cowork／Chat 合併公告，分階段推出時程 |
| GH1 | github.com/anthropics/claude-code/issues/2511 | 「連接 claude.ai Projects 到 Claude Code」feature request（尚未實現） |
| GH2 | github.com/anthropics/claude-code/issues/64779 | 同上，另一則 issue |
| O1 | help.openai.com「Projects in ChatGPT」等（WebSearch 摘要，官方頁面本次 WebFetch 回傳 403） | ChatGPT Projects 指示範圍、方案別檔案數（信心中～低） |
| G1 | support.google.com/gemininotebook/answer/16213268 | NotebookLM 各方案來源數量上限 |
| G2 | support.google.com/notebooklm/answer/16215270 | 單一來源上限、只依來源回答的官方敘述 |

延伸：[免付費區](free-tier.md)｜[付費區](paid-tier.md)｜[AI 介面比較總表](tools-compare.md)｜[Claude Code + Cowork 並用](claude-code-cowork.md)｜[Claude Code 設定總覽](official-config.md)
