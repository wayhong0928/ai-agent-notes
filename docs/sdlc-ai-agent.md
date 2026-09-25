# AI 代理時代的 SDLC

> 查證日期：2026-09-16（2026-09-25 補充 OpenSpec）。本頁只寫查得到出處或官方文件明講的做法，個人的 Claude Code 規則檔、派工制度、設定檔內容不在本頁範圍內；整理者自己的觀察會明確標示，不包裝成官方結論或研究結果。

[上一頁](sdlc-traditional.md)介紹的六個 SDLC 階段跟[開發實踐](dev-practices.md)介紹的 TDD、BDD、DDD 都沒有因為 AI 代理出現而消失：需求還是要分析，設計還是要做，程式碼還是要測試才能上線。改變的是每個階段花的力氣分布，以及風險出現的位置。

!!! note "整理者觀察"
    以下這句是整理者的推論，不是量化研究的結論：AI 代理讓打字寫程式這個動作本身變得更快，因此風險容易往前後兩端推，前端推向「有沒有把要做的事講清楚」，後端推向「有沒有人真的檢查過產出」。這裡沒有可靠研究支持「變快了多少」的具體數字，本頁也不會寫這類數字。如果只看到「AI 讓實作變快」就直接跳過需求跟驗證，反而是常見的翻車模式。

## 一、各階段對照表

| 階段 | AI 可以幫什麼 | 人一定要做的事 | 常見翻車點 |
|---|---|---|---|
| 需求 | 把模糊的需求整理成條列、幫忙想沒考慮到的邊界情況、寫成可以驗證的規格 | 決定要做什麼、為什麼要做、什麼東西算做完（範圍與優先順序永遠是人的決定） | 把 AI 順口寫出的規格當成使用者真正要的東西，沒回頭跟需求提出者確認 |
| 設計 | 提出架構選項、指出既有程式碼裡的模式、畫出可能的資料流 | 決定用哪個方案、承擔取捨的責任；官方建議先進入 plan mode，讓 AI 只探索、不動手改，產出一份詳細計畫再往下走[1] | 沒有先計畫就讓 AI 直接動手寫程式，可能做出解錯問題的程式碼[1] |
| 實作 | 大量寫程式、依既有慣例套用到多個檔案、平行處理彼此獨立的子任務 | 檢查改動範圍有沒有超出預期、決定要不要拆給不同工具分工（例如一方寫、另一方審） | 讓同一個沒有隔離上下文的對話一路做到底，錯誤累積在同一段脈絡裡，越改越亂[2] |
| 測試與驗證 | 產生測試案例、跑測試、比對輸出、找出明顯的邊界情況 | 決定驗收條件是什麼；先讓實作者自己跑過一次可重現的檢查（測試、建置），再交給乾淨上下文的審查者只看 diff 跟驗收條件、不看原始推理過程獨立複核[2] | AI 自己覺得「看起來做完了」就回報完成，沒有實際跑出證據；審查者找到的每一條建議都照單全收，變成過度工程[2] |
| 部署 | 準備部署腳本、產生變更紀錄、檢查上線前清單 | 對外的動作（真正推上正式環境、發送給使用者）一定要人確認，這是不可逆或高成本的行動 | 讓自動化流程在沒有人核准的情況下直接把改動送上正式環境 |
| 維護 | 讀懂舊程式碼、總結變更歷史、依既有慣例延續開發 | 把專案的事實與紅線寫進 CLAUDE.md／AGENTS.md，並在跨 session 銜接時把進度交代清楚 | 說明檔案越寫越長，重要規則反而被忽略；沒寫進說明檔的慣例，換一個 session 就要重新講一次[3] |

## 二、規格驅動開發（Spec-Driven Development，SDD）

### 是什麼

規格驅動開發是把「要做什麼、為什麼要做」寫成一份明確規格，再依規格產出技術計畫與可執行的任務清單，最後用一個收斂（convergence）步驟驗證實作是不是真的符合規格，不符合就回頭再對齊。這個定義來自 GitHub 官方的 `spec-kit` 專案，原文把核心精神講成「先決定 what 跟 why，再決定 how」（原文：Define what and why before deciding how to build it）[4]。`spec-kit` 把整個流程拆成幾個階段：Constitution（每個專案一次，訂出這個專案不變的原則）→ Specify（寫規格）→ Plan（技術計畫）→ Tasks（任務清單）→ Implement（實作）→ Converge（收斂，反覆進行直到實作與規格一致）[4]。

除了 `spec-kit`，[OpenSpec](https://github.com/Fission-AI/OpenSpec) 是另一個常見的 SDD 工具[11]；兩者都要在每個專案各自初始化，不是裝一次就對所有專案生效。

### 規格的定位：可執行的產出物，不是靜態文件

`spec-kit` 的方法論文件把它自己的指令定位成「把規格當成可執行的產出物，而不是靜態文件」（原文：The commands embody SDD principles by treating specifications as executable artifacts rather than static documents），同一份文件也把「規格與程式碼保持同步，因為程式碼是規格產生的」列為「Living Documentation」[5]。落在流程上的具體差別是：規格、計畫、任務清單在整個開發過程裡持續被拿出來對照，`spec-kit` 特別設計了收斂階段，把「檢查實作有沒有符合規格」變成流程裡的固定步驟，而不是交付前才臨時檢查一次[4]。

**整理者觀察**：這個差別，整理者認為本質上跟 TDD「先寫測試再寫程式碼」是同一種思路的不同層次——TDD 讓程式碼有一個自動可驗證的目標，SDD 讓整個開發過程有一個持續可對照的目標。這個類比是整理者自己下的，`spec-kit` 官方文件沒有這樣寫。

## 三、TDD、BDD、DDD 在 AI 代理流程裡的角色

### TDD：給 AI 一個能自動判斷對錯的目標

[開發實踐](dev-practices.md)介紹的 TDD，套進 AI 代理流程時價值特別明顯：先寫好測試案例，等於給 AI 一個不需要人一直盯著、自己就能跑出「對／錯」訊號的檢查點。Claude Code 官方 best practices 明確建議在提示詞裡先給出驗收案例，範例把「implement a function that validates email addresses」改寫成「write a validateEmail function. example test cases: user@example.com is true, invalid is false, user@.com is false. run the tests after implementing」[2]。官方也提到一種寫作者／審查者搭配模式：「你可以對測試做類似的事：讓一個 Claude 寫測試，另一個 Claude 寫程式碼去讓測試通過」（原文：You can do something similar with tests: have one Claude write tests, then another write code to pass them）[2]，這正是把 TDD 的紅燈綠燈循環拆給兩個獨立的執行者，避免同一個 AI 又寫測試又寫實作、又自己判定自己過關。

!!! note "整理者規則"
    測試不能為了通過而被 AI 隨意修改。如果 AI 判斷測試一直失敗是因為測試案例本身寫錯，正確的做法是把這個判斷提出來，經人核准後才調整測試內容，不能自己直接把判斷條件改鬆再回報通過。這條不是 best practices 頁面逐字寫的規則，是整理者從「驗證要看證據」延伸出的操作準則。

### BDD：Given-When-Then 直接當成規格與驗收條件

BDD 的 Given-When-Then 情境本身就是一份可以交給 AI 代理的規格：Given 段描述前提、When 段描述要實作的動作、Then 段就是驗收條件。把一段 Gherkin 情境直接貼進提示詞，AI 代理可以照著情境實作，再依 Then 段的內容自行檢查或讓另一個審查步驟檢查，不需要額外把驗收條件翻譯成別的格式。

### DDD：在 CLAUDE.md／AGENTS.md 裡寫清楚通用語言與上下文邊界

!!! note "整理者觀察"
    這一點目前查無官方文件把 DDD 跟 CLAUDE.md／AGENTS.md 直接連起來討論，以下是整理者依 DDD 概念與官方對 CLAUDE.md 用途的說明（放事實與紅線，見[擴充機制頁](extensions.md)）推出的觀察，不是引用自某篇公開文件的結論：一個專案如果已經用 DDD 切好了限界上下文，把每個上下文使用的通用語言、上下文之間的邊界寫進 CLAUDE.md 或 AGENTS.md，可以降低 AI 代理在不同模組之間把同一個詞用錯意思的機率（例如前面舉的「訂單」例子：AI 代理如果不知道銷售上下文跟物流上下文各自怎麼理解「訂單」，很容易把兩邊的欄位或邏輯混在一起）。這類邊界屬於「事實」而不是「程序」，符合官方對 CLAUDE.md 該放什麼內容的判準。

### 跟 SDD 的關係

`spec-kit` 官方沒有把 TDD、BDD 當成競爭方案，而是把規格當成主要產出物，TDD、BDD 則提供可以被直接執行、判斷對錯的驗收手段，兩者互補：SDD 決定「這個階段該對照什麼規格」，TDD／BDD 決定「這個規格具體怎麼變成一個可以自動判斷過或不過的檢查」。這個互補關係，`spec-kit` 官方說明沒有逐字寫出來，是整理者對照 SDD 的收斂階段跟 TDD／BDD 的驗證機制推出的觀察。

## 四、CI/CD 裡的 AI 代理

官方文件裡確實記載的兩個做法：

- **Claude Code GitHub Actions**：Anthropic 提供 `anthropics/claude-code-action@v1` 這個 GitHub Action，用 `/install-github-app` 可以快速裝好；裝好之後可以在 PR 或 issue 留言裡用觸發字 `@claude` 呼叫，讓 Claude 分析程式碼、實作變更、推送 commit；也可以不靠留言觸發，直接給一個 `prompt` 讓它在任何 GitHub 事件（包含排程）上自動執行，例如把 issue 轉成 PR，或在 PR 開啟時自動跑程式碼審查[6]。
- **Codex GitHub Action 與非互動模式**：OpenAI 官方範例使用 `openai/codex-action@v1`，底層是 `codex exec` 這個非互動執行方式，定位就是給 CI pipeline、pre-merge 檢查、排程任務用[7]。這個組合有幾個分開的設定要點：
    - **沙箱預設**：官方非互動模式文件寫的是「By default, `codex exec` runs in a read-only sandbox」（預設跑在唯讀沙箱裡）[7]。
    - **`sandbox` 參數**：GitHub Action 的 `sandbox` 輸入可選 `read-only`、`workspace-write`、`danger-full-access`；要讓它真的修改工作區內容，就是在這裡選 `workspace-write`[8]。
    - **`safety-strategy` 參數**：預設值是 `drop-sudo`，也就是跑 Codex 之前先移除 `sudo`；另一個選項 `unprivileged-user` 會搭配 `codex-user` 輸入，改用指定的非 root 帳號執行[8]。
    - **`chmod` 是排解權限錯誤，不是授權沙箱寫入**：移除 sudo 之後，Codex 可能因為檔案權限而改不動 repo 檔案，官方給的做法是事先放寬工作區權限（例如 `chmod -R g+rwX "$GITHUB_WORKSPACE"`）[8]。這跟上面的 `sandbox` 是兩件事。
    - **權限分工**：官方非互動模式範例把「執行 Codex 的那個 job」跟「真正開 PR 的那個 job」分開——跑 Codex 的 job 只有 `contents: read`，跑完只把 diff 當成 artifact 輸出；負責開 PR 的 job 有寫入權限，但拿不到 `OPENAI_API_KEY`[7]。

兩者的共同精神跟本站[Claude Code + Codex 協作](claude-codex.md)頁講的「一方寫、另一方審」一致：讓 AI 代理進到 CI 流程，不代表跳過原本的分支保護與審查機制，反而應該讓它照著既有的 PR 流程走，而不是繞過去直接改主線。

## 五、完整案例：檢查網站失效連結的腳本

以下走一遍一個小任務從需求到交付的完整過程，每一步標出人、Claude Code、Codex 各自的分工與驗收條件。

### 1. 需求

**人**：提出目標，「我想知道這個網站有哪些內部連結指到不存在的檔案」，並決定範圍：只檢查本站 `docs/` 底下的相對連結，不檢查外部網址。

**Claude Code**：把這句話整理成條列需求，回頭跟人確認：要不要檢查外部連結？找到失效連結要不要自動修？輸出格式要什麼樣？

**Codex**：這一步不需要 Codex。需求釐清是人跟 Claude Code 之間的來回確認，不涉及動手實作。

**驗收條件**：需求條列裡每一條都能被驗證（「範圍限定在 docs/ 內部相對連結」可以直接檢查程式有沒有處理到外部連結），而不是停留在「幫我看看連結」這種無法驗證的描述。

### 2. 規格

**人**：核准 Claude Code 整理出的範圍。

**Claude Code**：寫一份簡短規格：輸入（`docs/` 目錄）、輸出（一份表格，列出檔名、行號、連結文字、目標路徑、是否存在）、不處理的範圍（外部網址、圖片連結）、驗收條件（對一個刻意放了 3 個失效連結的測試目錄跑過，要抓出全部 3 個，不多報也不少報）。

**Codex**：這一步不需要 Codex。寫規格屬於 Claude Code 在這個分工裡的責任。

**驗收條件**：規格裡的「不處理的範圍」跟「驗收條件」都寫清楚，另一個人（或另一個 AI）光看規格就能判斷實作對不對，不用回頭問原作者在想什麼。

### 3. 計畫

**人**：決定要不要進 plan mode。官方建議在「不確定該用什麼作法、改動涉及多個檔案、或對要改的程式碼不熟悉」這三種情況下用 plan mode[9]；這個任務符合前兩項：一開始不確定要怎麼掃描與判斷連結是否有效，而且會建立、讀取多個檔案。

**Claude Code**：進 plan mode，只讀檔案、不動手改，列出計畫：用什麼語言寫（例如 Python）、怎麼掃描 Markdown 連結語法、怎麼判斷連結目標是否存在、要不要處理相對路徑跟錨點分開判斷；計畫裡明確寫出步驟 4 打算由 Claude Code 自己實作，還是改派 Codex 執行。

**Codex**：這一步不需要 Codex。計畫階段留在 Claude Code 的 plan mode 內完成，Codex 最多是計畫裡「要不要交給它」的討論對象，不實際動作。

**驗收條件**：計畫列出具體步驟跟會動到的檔案，人看完能判斷「這樣做對不對」，不是一段空泛的散文。

### 4. 實作

**人**：核准計畫，決定步驟 4 要不要改派 Codex 執行；不管哪種分工，都要求先寫測試案例再寫腳本本體。

**Claude Code**：依核准的計畫寫腳本；如果規格已經明確到可以自包含執行、不需要理解這個 vault 特有的規則，這一步也可以改派 Codex 執行，Claude Code 只需要把規格與驗收條件交給它（Claude 規劃、Codex 執行的分工模式）[10]。

**Codex**：若步驟 3 的計畫指定由 Codex 實作，這一步由 Codex 依規格與驗收條件寫腳本；若計畫指定留在 Claude Code，這一步不需要 Codex。兩種分工只能選一種，不是同一支腳本兩邊各寫一次。

**誰寫測試**：測試跟實作分開由不同執行者負責，對應官方那句「have one Claude write tests, then another write code to pass them」（讓一個 Claude 寫測試，另一個寫程式碼去讓測試通過，本頁前面已引用）[2]。所以如果腳本本體由 Codex 寫，測試案例就由 Claude Code 先寫好；如果腳本本體留給 Claude Code，測試案例就交給另一個乾淨上下文的 Claude Code 對話或 Codex 寫。不論哪種分工，寫測試的跟寫實作的不是同一個執行者。

**驗收條件（TDD 風格）**：在寫腳本本體之前，先寫好測試案例：對一個內建 3 個已知失效連結的測試目錄跑腳本，斷言輸出剛好列出這 3 個，且行號、檔名都對得上。這一步就是把 TDD「先寫測試」的做法套進這個案例：測試案例本身就是這支腳本的驗收條件，不用等腳本寫完才臨時想怎麼測。

### 5. 驗證

**人**：要求看實際執行輸出，不接受「應該沒問題」這句話。

**誰審查**：審查者不能是寫這段程式碼的那個執行者。兩種分工對應到：

| 步驟 4 的實作者 | 這一步的審查者 |
|---|---|
| Claude Code | 另一個乾淨上下文的 Claude Code 對話，或用 Codex 的唯讀審查指令（例如 `/codex:review`） |
| Codex | 乾淨上下文的 Claude Code |

不論哪種分工，審查者只看 diff 跟驗收條件，不看實作過程中的推理，重新跑一次測試案例，並額外測邊界情況（空目錄、沒有任何連結的檔案、連結指向自己）。

**驗收條件**：貼出實際測試輸出（通過／失敗各幾條）；審查者發現的問題只處理會影響正確性的部分，其餘瑣碎建議（例如變數命名風格）可以判斷後決定不修，但要講清楚跳過了什麼。

### 6. 交付

**人**：檢視最終的 diff 跟輸出範例，決定要不要真的把這支腳本排進 CI（例如接進前一節「CI/CD 裡的 AI 代理」講的排程任務，每天自動掃一次）；是否上線一定由人確認。

**Claude Code／Codex**：這一步不需要 AI 代理動作，交付與上線的決定是人的責任；如果人決定要接進 CI，可以請 Claude Code 或 Codex 協助寫排程設定檔，但那已經是另一輪「規格→實作→驗證」，不算這次案例的一部分。

**驗收條件**：排進 CI 前，先由人手動觸發執行一次，確認行為符合預期，再決定要不要交給排程自動執行；接上 CI 之後，第一次自動執行的結果也要有人看過，不是裝上去就假設它會一直正常運作。

## 六、敏捷式在 AI 代理時代的變化

!!! note "整理者觀察"
    這一節整段是整理者對照官方文件推出的觀察，不是某篇研究的結論，也沒有量化數字支持：敏捷式方法原本假設的瓶頸是「寫程式碼要花多少時間」，Sprint 的節奏、Kanban 的 WIP 控制，都是在管理人力這個稀缺資源。如果 AI 代理讓寫程式碼這個動作變快，瓶頸有可能移到「怎麼確認 AI 寫出來的東西是對的」，也就是驗證這一段。官方 best practices 裡反覆出現的主題確實是驗證：給 AI 一個能自己跑的檢查、用乾淨上下文的審查者、用證據而非斷言判斷是否完成[2]，但官方沒有把這個現象直接連到「敏捷式的瓶頸轉移」這個框架上，這個連結是整理者自己推的，也沒有可靠的量化研究支持「變快了多少」。

## 七、風險清單

| 風險 | 說明 | 避法 |
|---|---|---|
| 幻覺 API | AI 生成看起來合理但實際不存在的函式、參數或套件 | 要求 AI 附上文件連結或版本號，不確定就先查證，不要憑訓練記憶回答可查證的事實 |
| 過時文件 | AI 訓練資料的截止日期早於工具或函式庫的最新版本，引用的用法已經失效 | 對照官方文件的查證日期；本站[Claude Code + Codex 協作](claude-codex.md)頁列出多個「網路教學已失效」的實例可參考 |
| 秘密外洩 | AI 代理在對話、commit 或部署腳本裡不小心帶出金鑰、密碼 | 金鑰只放環境變數或密鑰管理服務，絕不寫進提示詞或程式碼；commit 前檢查 diff |
| 權限過大 | 讓 AI 代理在不必要的範圍內擁有寫入或執行權限 | 依任務範圍給最小權限，善用[權限模式與沙箱](agent-basics.md)的分級設計 |
| 自己驗自己 | 寫程式碼的 AI 代理同時審查自己的產出，容易帶著「我當初這樣想」去護航 | 換一個乾淨上下文的審查者，只看 diff 跟驗收條件，見[harness 頁](harness.md)的驗證分級 |

## 資料來源

| 標記 | 主張 | 來源 |
|---|---|---|
| [1][2][9] | Explore→Plan→Implement→Commit 四階段、plan mode 三種適用情境、驗證要看證據、寫測試再審查、對抗性審查 | [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) |
| [3] | CLAUDE.md 放事實不放程序 | [How Claude remembers your project](https://code.claude.com/docs/en/memory) |
| [4] | SDD 定義、工作流程階段 | [github/spec-kit](https://github.com/github/spec-kit) |
| [5] | 「規格是可執行的產出物，不是靜態文件」、Living Documentation | [spec-kit：spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md) |
| [6] | Claude Code GitHub Actions（action 名稱、觸發字、安裝指令） | [官方文件](https://code.claude.com/docs/en/github-actions) |
| [7] | `codex exec` 預設唯讀沙箱、CI 使用情境、Codex job 與開 PR job 的權限分工 | [Codex Non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode) |
| [8] | Codex GitHub Action 的 `sandbox`／`safety-strategy` 選項與 `chmod` 排解權限錯誤 | [Codex GitHub Action](https://learn.chatgpt.com/docs/github-action) |
| [10] | 分工模式詳見 | [Claude Code + Codex 協作](claude-codex.md) |
| [11] | OpenSpec：另一個 SDD 工具，每個專案各自執行 `openspec init` | [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) |
| — | SDD 與 TDD 的類比、DDD 在 CLAUDE.md 的應用、敏捷式瓶頸轉移的推論 | 整理者觀察，正文已標示，查無官方出處 |

延伸：[SDLC 與流程模型](sdlc-traditional.md)｜[開發實踐：TDD、BDD、DDD 與 SDD](dev-practices.md)｜[Claude Code + Codex 協作](claude-codex.md)｜[把 AI 代理的工作環境設計得可靠](harness.md)
