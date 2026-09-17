# 開發實踐：TDD、BDD、DDD 與 SDD

> 查證日期：2026-09-16。本頁講的是「工程師寫程式當下」的具體做法，跟[上一頁](sdlc-traditional.md)講的「專案怎麼推進」是不同層次的問題：DDD 是一種設計方法，TDD、BDD 是開發與驗證的實踐，都可以放進瀑布式或敏捷式的任何一種流程裡使用，彼此也不互斥。這幾種方法跟 AI 代理怎麼搭配，留到[下一頁](sdlc-ai-agent.md)集中討論，這裡先把「原本是什麼」講清楚。

## 一、TDD：測試驅動開發

### 是什麼

測試驅動開發（Test-Driven Development，TDD）由 Kent Beck 在《Test-Driven Development: By Example》（Addison-Wesley，2002 年）中系統化整理，做法是先寫一個會失敗的測試，再寫剛好能讓它通過的程式碼，然後整理程式碼結構，三步反覆進行。Martin Fowler 把這個循環總結為「紅燈、綠燈、重構」（Red-Green-Refactor）：寫測試（紅燈，因為程式碼還不存在或還沒滿足）、寫功能程式碼讓測試通過（綠燈）、在測試保護下重構讓程式碼結構更好[1]。

### 核心做法

1. **紅燈**：針對下一個要加的功能，先寫一個測試，跑起來應該失敗（因為功能還沒實作）。
2. **綠燈**：寫出剛好能讓這個測試通過的程式碼，不多做，先求能動。
3. **重構**：在測試持續通過的前提下，把程式碼整理得更清楚，重複利用、消除重複。

Fowler 特別提醒最常見的失敗方式是省略第三步：只做紅燈綠燈、不重構，結果程式碼雖然有測試覆蓋，但結構會越改越亂[1]。

### 小例子

要實作一個檢查 email 格式是否有效的函式，TDD 的第一步先寫測試，而不是先寫函式本身：

```text
test: validateEmail("user@example.com") 應該回傳 true
test: validateEmail("invalid") 應該回傳 false
test: validateEmail("user@.com") 應該回傳 false
```

這三個測試一開始都會失敗（因為 `validateEmail` 還不存在），寫出最簡單能讓它們通過的實作，再回頭重構。

### 適合與不適合

適合：邏輯明確、輸入輸出關係容易寫成斷言的程式碼（工具函式、資料轉換、業務規則計算）。不適合：探索性很強、連自己都還不確定介面該長什麼樣的原型階段，先寫死測試反而會限制探索。

### 常見誤解

TDD 不是「先寫測試，之後再也不用改」，測試本身也需要跟著需求調整；TDD 也不等於「測試覆蓋率要 100%」，覆蓋率是副產品，不是目標本身。

## 二、ATDD：驗收測試驅動開發

驗收測試驅動開發（Acceptance Test-Driven Development，ATDD）把 TDD 的「先寫測試」往前推一層，讓客戶、開發者、測試者三個不同視角（Agile Alliance 稱為 three amigos）一起參與，用客戶能看懂的語言先寫好驗收條件，再依這份條件做開發。Agile Alliance 公開詞彙表把這個做法定義為「不同視角的團隊成員（客戶、開發、測試）合作，在對應功能實作之前先寫好驗收測試」[2]。

**整理者觀察**：ATDD 跟 BDD 常被放在一起討論，整理者的理解是兩者都把「先講清楚怎麼算做對，再動手做」往前推，差別在 ATDD 強調的是「跨角色共同定義驗收條件」這件事本身，BDD 則額外提供了一套具體的敘述格式（見下一節的 Given-When-Then）。這個對比沒有找到把兩者並列比較的官方出處，也沒有引用任一方對「源自 TDD」的正式宣稱，屬於整理者歸納。

## 三、BDD：行為驅動開發

### 是什麼

行為驅動開發（Behavior-Driven Development，BDD）由 Dan North 在 2006 年的文章〈Introducing BDD〉中提出，是對 TDD 的延伸：把「測試」改講成「行為」，讓不熟悉程式的人也看得懂測試在驗證什麼。BDD 引入的「Given-When-Then」敘述格式，受到 Eric Evans 在《Domain-Driven Design》裡提出的「通用語言」（ubiquitous language）概念影響，目標是讓開發者跟業務端的人使用同一套詞彙描述系統行為[3]。

### 核心做法：Given-When-Then 與 Gherkin

BDD 情境用三段式描述：**Given**（初始情境／前提條件）、**When**（觸發的動作）、**Then**（預期的結果）。Cucumber 這套工具把這個格式規範成「Gherkin」語法，官方定義的核心關鍵字包括 `Feature`、`Scenario`、`Given`、`When`、`Then`、`And`、`But`[4]。

### 小例子

```gherkin
Feature: 使用者登入
  Scenario: 帳號密碼正確
    Given 使用者在登入頁面
    When 輸入正確的帳號與密碼並送出
    Then 應該被導向到儀表板頁面
```

這段 Gherkin 情境同時是規格文件（給非工程師看），也可以當成可執行規格的輸入，但寫完情境不會自動變成能跑的測試：Cucumber 官方文件說明每一個步驟（Given／When／Then 那一行）還要另外對應一段「step definition」程式碼，Cucumber 執行時才會依序比對每個步驟、找到對應的 step definition 去執行[4]。沒有寫 step definitions，Gherkin 文字本身只是文件，不會自己跑起來。

### 適合與不適合

適合：需要跨角色（產品、業務、工程）對「系統該怎麼表現」達成共同理解的功能，尤其是牽涉複雜業務規則的情境。不適合：純技術性、內部實作細節的邏輯（例如某個排序邏輯的效能最佳化），寫成 Given-When-Then 反而是多繞一層。

### 常見誤解

BDD 常被誤會成「比 TDD 更高級」的替代品，實際上它是在 TDD 之上多加一層「用業務語言表達驗收條件」，兩者可以同時使用：BDD 情境描述行為，底層仍然可能有 TDD 風格的單元測試在驗證細節。

## 四、DDD：領域驅動設計

### 是什麼

領域驅動設計（Domain-Driven Design，DDD）由 Eric Evans 在《Domain-Driven Design: Tackling Complexity in the Heart of Software》（Addison-Wesley）提出，處理的問題是：軟體系統越複雜，程式碼裡用的詞彙跟業務端實際用的詞彙越容易脫節，脫節到一定程度，沒人能同時看懂程式碼又看懂業務邏輯。DDD 的解法分兩層：戰略設計（strategic design）決定系統要怎麼切成幾個各自獨立的範圍；戰術設計（tactical design）決定範圍內部的程式碼怎麼組織。官方的《DDD Reference》是 Evans 原書所有定義與模式的精簡版整理，額外補了三個原書沒收錄的模式[5]。

!!! note "這本書標 2003 還是 2004"
    兩種年份都看得到：出版方 Pearson／InformIT 的[書目頁](https://www.informit.com/store/domain-driven-design-tackling-complexity-in-the-heart-9780321125217)同時列出出版日期 Aug 20, 2003 與版權年 2004（ISBN 978-0-321-12521-7），而作者自己的網站 domainlanguage.com 在《DDD Reference》裡寫的是「Domain-Driven Design: Tackling Complexity in the Heart of Software, Addisson-Wesley 2004」，並稱之為「Eric Evans' 2004 book」[5]。本頁引用時以作者網站的寫法為準，不另外斷定哪一個才「對」。

### 核心術語

**戰略設計：**

- **通用語言（Ubiquitous Language）**：團隊（包含業務端與工程端）共同使用同一套詞彙描述領域，這套詞彙要直接反映在程式碼的類別與方法命名上，不是「業務講一套、程式碼寫另一套」。
- **限界上下文（Bounded Context）**：把系統切成幾個範圍，每個範圍內部的術語有明確、一致的意義，範圍之間即使用了同一個詞，也可能代表不同的東西，需要明確定義範圍之間怎麼轉換。

**戰術設計：**

- **實體（Entity）**：有獨立身分、會隨時間改變狀態，但身分本身不變的物件（例如「這張訂單」，即使內容改了還是同一張訂單）。
- **值物件（Value Object）**：沒有獨立身分，只由它的屬性值決定是不是同一個東西（例如「地址」，兩個內容一樣的地址視為相同）。
- **聚合（Aggregate）**：一組相關的實體與值物件被視為一個一致性邊界，對外只透過聚合根（Aggregate Root）存取，確保這組物件內部規則不會被繞過。

### 小例子：「訂單」領域的上下文切分

一個電商系統裡，「訂單」這個詞在不同範圍裡指的東西不完全一樣：在**銷售上下文**裡，訂單關心的是商品、數量、金額；在**物流上下文**裡，同一張訂單關心的是包裝、配送地址、預計到貨時間；在**財務上下文**裡，訂單關心的是發票、稅務、付款狀態。DDD 的做法不是硬把這三個關注點塞進同一個「訂單」類別，而是承認這是三個限界上下文，各自維護自己版本的「訂單」概念，上下文之間再定義清楚的轉換規則（例如銷售上下文的訂單確認後，怎麼轉換成物流上下文看得懂的出貨單）。

### 適合與不適合

適合：業務邏輯複雜、多個團隊或多個子系統共同維護同一個大型系統，命名混亂已經開始造成溝通成本。不適合：業務邏輯單純的小型專案或短期原型，套用整套戰略／戰術設計的成本會超過它解決的問題。

### 常見誤解

DDD 不等於「把程式碼裡的類別重新命名成業務詞彙」，命名一致只是通用語言的表面結果；真正的重點是限界上下文之間邊界要畫清楚，以及聚合要真正保護住一致性規則，不是叫什麼名字。

## 五、結對程式設計

結對程式設計（Pair Programming）是 XP 的核心實踐之一：兩位工程師共用一台電腦，一人寫程式（driver），一人即時檢視邏輯、想邊界情況（navigator），角色會互換，Agile Alliance 公開詞彙表用同一套 driver／navigator 說法描述這個分工[6]。目的是讓程式碼在寫出來的當下就被第二個人看過，減少事後才發現的錯誤與知識落在一個人身上的風險。

!!! note "整理者觀察：跟 AI 結對，跟兩個人結對不是同一件事"
    「跟 AI 結對」這個說法常被用來類比人類結對程式設計，但兩者有關鍵差異：傳統結對的 navigator 是另一個對業務脈絡有理解、能承擔責任的人；AI 助手就算即時給建議，也不對結果負責，也不必然理解專案的業務脈絡（除非脈絡寫進 CLAUDE.md／AGENTS.md 或當次提示詞裡）。這一點目前查無官方文件明確定義「AI 結對」的邊界，這裡標記為整理者觀察，不是引用自某篇公開文件的結論。

## 六、Code Review

Code Review（程式碼審查）指讓寫程式碼的人之外的另一人檢視這段程式碼。Google 公開的工程實務文件把 code review 的目的講得很直接：維持程式碼與產品的品質，審查者要看的面向包括設計、功能是否符合預期、複雜度、測試涵蓋是否足夠、命名、註解、風格、文件是否同步更新[7]。這個原則跟本站另一頁講的「做的人不驗自己的活」是同一個道理：換一個沒參與寫這段程式碼的人來看，才看得出寫的人自己看不出來的問題。

## 七、主幹開發

主幹開發（Trunk-Based Development）已經在[上一頁的 DevOps 與 CI/CD 一節](sdlc-traditional.md)介紹過，這裡只補一點：DORA 的研究支持的是「小批次修改、頻繁合併、快速的自動化測試」這組合跟交付表現有關，沒有把 Code Review 列為主幹開發的必要條件[8]。

!!! note "整理者觀察"
    以下是整理者的延伸推論，不是 DORA 報告的結論：主幹開發要讓大家敢頻繁合併，通常需要合併前有自動化測試把關（TDD 產出的測試提供了這種把關），也常見搭配合併時的 Code Review；但這只是常見的搭配做法，不是 DORA 研究證實的必要條件。

## 八、規格驅動開發（SDD，摘要）

規格驅動開發（Spec-Driven Development，SDD）是近年隨 AI 代理興起而被提出的做法，簡單說是先把「要做什麼、為什麼要做」寫成一份規格，再依規格產出技術計畫與任務清單，最後對照規格驗證實作是否吻合。規格在這套做法裡被當成什麼、完整的工作流程階段，留到[下一頁](sdlc-ai-agent.md)展開，因為 SDD 的實際價值主要體現在跟 AI 代理搭配使用的情境。

## 九、這幾種方法怎麼比較

| 方法 | 關注焦點 | 主要產出 | 誰參與 | 跟瀑布式／敏捷式怎麼搭配 |
|---|---|---|---|---|
| TDD | 程式碼的正確性，一次專注一個小單位 | 自動化測試＋通過測試的程式碼 | 工程師 | 可放進任一流程模型的實作階段，不限敏捷 |
| ATDD | 跨角色對驗收條件的共同理解 | 客戶語言寫的驗收條件 | 客戶、開發者、測試者 | 常見於敏捷框架，但概念本身不排斥瀑布式的需求階段 |
| BDD | 系統行為，用業務語言描述 | Given-When-Then 情境（要搭配 step definitions 才能執行） | 產品、業務、工程 | 敏捷框架中常見，適合搭配 Scrum 的使用者故事 |
| DDD | 業務領域的概念邊界與一致性 | 通用語言、限界上下文、聚合等設計產出 | 領域專家、架構師、工程師 | 屬於設計方法，可用在瀑布式的設計階段，也可用在敏捷式的持續設計中 |
| SDD | 把「要做什麼、為什麼」變成主要產出物 | 規格、技術計畫、任務清單 | 使用者／需求提出者、AI 代理、審查者 | 目前主要在 AI 代理輔助開發的情境下被提出，詳見下一頁 |

這五種方法不互斥，可以同時出現在同一個專案裡：用 DDD 切好領域邊界，在某個限界上下文內用 BDD 寫清楚對外行為，實作細節用 TDD 一步步逼近正確答案，AI 代理輔助開發時再用 SDD 把整個過程串起來。

## 資料來源

| 標記 | 主張 | 來源 |
|---|---|---|
| [1] | TDD 紅燈綠燈重構循環、常見失敗方式 | [Fowler：TestDrivenDevelopment](https://martinfowler.com/bliki/TestDrivenDevelopment.html) |
| — | TDD 出處 | Beck, K. (2002). *Test-Driven Development: By Example*. Addison-Wesley |
| [2] | ATDD 定義、three amigos | [Agile Alliance：What is ATDD?](https://agilealliance.org/glossary/atdd/) |
| — | ATDD 與 BDD 的差別對比 | 整理者觀察，正文已標示，查無並列比較兩者的官方出處 |
| [3] | BDD 起源、Given-When-Then 受 DDD 通用語言影響 | [Cucumber：History of BDD](https://cucumber.io/docs/bdd/history/) |
| [4] | Gherkin 關鍵字、語法、step definitions 才能執行 | [Cucumber：Gherkin 官方文件](https://cucumber.io/docs/gherkin/) |
| — | DDD 出處（出版年 2003／2004 的差異見正文說明） | Evans, E. *Domain-Driven Design: Tackling Complexity in the Heart of Software*. Addison-Wesley；作者網站寫 2004，見 [The DDD Reference](https://www.domainlanguage.com/ddd/reference/) |
| [5] | DDD Reference 說明 | [domainlanguage.com：The DDD Reference](https://www.domainlanguage.com/ddd/reference/) |
| [6] | 結對程式設計 driver／navigator 定義 | [Agile Alliance：Pair Programming](https://agilealliance.org/glossary/pair-programming/) |
| — | 跟 AI 結對的差異 | 整理者觀察，查無官方文件明確定義 |
| [7] | Code Review 目的與審查面向 | [Google：Engineering Practices（Code Review）](https://google.github.io/eng-practices/review/) |
| [8] | 主幹開發與交付表現關聯（不含 Code Review 必要性） | [DORA：Trunk-based development](https://dora.dev/capabilities/trunk-based-development/) |
| — | 主幹開發跟 TDD／Code Review 常見搭配（非必要條件） | 整理者觀察 |
| — | SDD 摘要 | [github/spec-kit README](https://github.com/github/spec-kit)，詳見[下一頁](sdlc-ai-agent.md) |

延伸：[SDLC 與流程模型](sdlc-traditional.md)｜[AI 代理時代的 SDLC](sdlc-ai-agent.md)
