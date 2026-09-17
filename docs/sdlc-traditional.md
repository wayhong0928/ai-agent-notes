# SDLC 與流程模型

> 查證日期：2026-09-16。本頁整理業界既有的流程模型與官方公開文件，個人觀察會明確標示「整理者觀察」，跟有出處的主張分開看。

軟體開發生命週期（Software Development Life Cycle，SDLC）指的是一套把「做一個軟體」拆成幾個階段的做法：先搞清楚要做什麼，再決定怎麼做，動手寫，檢查對不對，交出去給人用，之後還要一直維護。把這些階段明確拆開的用意，是讓進度可以被檢查、流程可以被重複執行；不同的流程模型只是對「這幾個階段要怎麼排、能不能重疊、要不要反覆走幾次」給出不同答案。

!!! note "整理者觀察：為什麼不直接開始寫"
    以下是整理者的經驗歸納，不是引用自研究或官方文件：直接打開編輯器開始寫，卡關往往不出在程式碼本身，而是「要做什麼」還沒講清楚；等寫到一半才發現方向錯了，砍掉重來的代價通常比先把需求想清楚高。這句話沒有可引用的量化研究支持，讀者可以當成一個看待 SDLC 的角度，不是被證實的通則。

## 一、SDLC 六個階段在做什麼

不管套用哪種流程模型，底下這六件事大致都要做到，只是順序、重疊程度、反覆次數不同：

| 階段 | 在做什麼 | 主要產出 | 誰負責 | 常見失誤 |
|---|---|---|---|---|
| 需求分析 | 弄清楚使用者要解決什麼問題、系統要滿足哪些條件 | 需求文件、使用者故事、驗收條件 | 產品經理、業務分析師、客戶代表 | 只記錄「使用者說的話」，沒挖出真正的問題；需求寫得太模糊，沒辦法拿來驗收 |
| 設計 | 決定系統的架構、模組怎麼切、資料怎麼存 | 架構圖、資料庫設計、介面規格 | 系統架構師、資深工程師 | 設計脫離真實限制（效能、預算、既有系統相容性）；過度設計，為還沒發生的需求預留一層複雜度 |
| 實作 | 把設計寫成可以執行的程式碼 | 原始碼、單元測試 | 工程師 | 直接開始寫，沒對照設計文件；程式碼能跑但沒人看得懂，也沒測試 |
| 測試 | 確認程式碼符合需求、沒有明顯缺陷 | 測試報告、缺陷清單 | 測試工程師、QA | 只測「正常路徑」，沒測邊界情況；測試在最後才補，來不及影響設計 |
| 部署 | 把系統交付到使用者能用到的環境 | 部署腳本、上線紀錄 | 維運工程師、DevOps | 手動部署步驟沒寫下來，換人做就出錯；沒有回滾（rollback）計畫 |
| 維護 | 上線後修錯、加新功能、因應環境變化調整 | 修補紀錄、版本紀錄 | 全體工程團隊 | 沒人接手舊系統的知識；文件沒跟著程式碼更新，後來的人看不懂為什麼這樣寫 |

## 二、瀑布式、V 模型、螺旋模型、迭代增量開發

這四種是比較早出現、以「怎麼把上面六個階段排成一條路徑」為核心問題的流程模型。

### 2.1 瀑布式（Waterfall）

瀑布式把六個階段排成一條單向的線：需求分析做完才進設計，設計做完才進實作，依序往下走，原則上不回頭。這個單向階段結構就是下面 Royce 論文 Figure 2 畫出來的樣子。

整理者觀察（以下適用場合與缺點沒有單一出處，是整理者歸納）：這種做法適合需求一開始就能講清楚、之後基本不會變的專案，例如某些政府採購案、硬體結合軟體的專案（改需求的成本極高，甚至涉及實體零件）；缺點是一旦晚期才發現需求理解錯了，回頭修改的代價非常大。

!!! note "Royce 1970 年的論文常被誤讀"
    瀑布式常被追溯到 Winston Royce 1970 年的論文，但論文本身沒有主張純單向的流程。畫出單向流程圖（Figure 2）之後，Royce 緊接著寫這種實作方式「risky and invites failure」（有風險、容易失敗，印刷頁 329）。下一頁的兩張圖是一組對照：Figure 3 的圖說用「希望」的語氣說反覆互動只侷限在相鄰步驟（Hopefully, the iterative interaction between the various phases is confined to successive steps），Figure 4 的圖說隨即指出實際上做不到（Unfortunately, for the process illustrated, the design iterations are never confined to the successive steps）。論文後段五項修正建議的第三項，標題直接寫「STEP 3: DO IT TWICE」（印刷頁 334），建議先用模擬或試作版做過一次，再做正式交付的版本。來源：Royce, W. W. (1970). Managing the Development of Large Software Systems. *Proceedings, IEEE WESCON*, 1–9；引文見重印版印刷頁 329、330、334，全文 328–338（[原始 PDF](https://cse.msu.edu/~cse435/Homework/HW3/royce1970.pdf)，密西根州立大學課程網站公開重印版）。

### 2.2 V 模型

國際軟體測試資格認證委員會（ISTQB）的官方詞彙表把 V 模型定義為：「循序式的軟體開發生命週期模型，描述從商業需求規格到交付的各個主要開發階段，與從驗收測試到元件測試的各個測試層級之間，一對一的對應關係」（原文：A sequential software development lifecycle model describing a one-for-one relationship between major phases of software development from business requirements specification to delivery, and corresponding test levels from acceptance testing to component testing）[^istqb]。同一機構的 Foundation Level 教材也把 V 模型與瀑布式並列，當成「循序式開發模型」的兩個例子[^istqb]。

**整理者說明**：這種一對一的對應關係可以畫成一個 V 字——左半邊由上往下是開發階段，右半邊由下往上是對應的測試層級——「V 模型」這個名稱看起來也是這麼來的；不過這個圖形化的畫法不在上面的官方定義裡，這裡是整理者為了方便理解而補的說明。這樣安排的用意是每個開發階段都先想好「將來要怎麼驗證這一階段做對了」：寫需求時就先想好驗收測試要測什麼，設計架構時就先想好整合測試要測什麼，測試計畫因此跟著設計同步定案，不用等程式寫完才臨時想怎麼測。

整理者觀察：適合的場合跟瀑布式接近（需求穩定、重視可預測的驗證流程，例如醫療器材、航太軟體），代價也一樣，早期沒發現的需求誤解要等到後面才會浮現。

[^istqb]: 定義原文出自 [ISTQB Glossary](https://glossary.istqb.org/en_US/term/v-model) 的 V-model 詞條（en_US，version 2）；該頁為動態載入，定義文字取自其後端 API <https://api.glossary.istqb.org/v1/terms/v-model>。循序式開發模型的並列出自 ISTQB. *Certified Tester Foundation Level Syllabus v4.0.1*，2.1.1 節（PDF 第 25 頁）：「Examples of SDLC models include: sequential development models (e.g., waterfall model, V-model)…」<https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf>。另注意德國政府的 V-Modell XT（<https://download.gsb.bund.de/BundesCIO/V-Modell_XT_Bund/V-Modell%20XT%20Bund-2.0-HTML/index.html>）是一套可裁剪、可反覆執行的公部門流程模型，名稱相近但規格比教科書式的 V 模型複雜得多，兩者不宜直接畫上等號。

### 2.3 螺旋模型（Spiral Model）

螺旋模型由 Barry Boehm 提出，同名論文先於 1986 年 8 月刊在《ACM SIGSOFT Software Engineering Notes》[^boehm1986]，1988 年 5 月在《IEEE Computer》刊出較常被引用的版本[^boehm1988]。跟瀑布式的單向線不同，螺旋模型把整個開發流程畫成一圈一圈往外擴的螺旋，每一圈都重複四個動作：訂出這一圈的目標與限制、辨識並評估風險、開發並驗證這一圈的產出（可能是原型、可能是部分系統）、規劃下一圈。核心主張是「風險決定這一圈該做多少工作、該做到多細」：風險高的地方多做原型、多驗證，風險低的地方可以直接照傳統的線性方式往下走。Boehm 在 2000 年的 SEI 特別報告裡，把螺旋模型定義成一種「風險驅動的流程模型產生器」（原文：The spiral development model is a risk-driven process model generator，該報告 1.2 節、印刷頁 3）[^boehm2000]：不同專案的風險狀況不同，跑出來的實際流程也不同，不是每個專案套的都是同一種固定順序。

[^boehm1986]: Boehm, B. (1986). A spiral model of software development and enhancement. *ACM SIGSOFT Software Engineering Notes*, 11(4), 14–24. <https://doi.org/10.1145/12944.12948>
[^boehm1988]: Boehm, B. (1988). A spiral model of software development and enhancement. *IEEE Computer*, 21(5), 61–72. <https://doi.org/10.1109/2.59>
[^boehm2000]: Boehm, B.（Hansen, W. J. 編）(2000). *Spiral Development: Experience, Principles, and Refinements*（Special Report CMU/SEI-2000-SR-008）. Carnegie Mellon University／SEI. [報告頁](https://www.sei.cmu.edu/library/spiral-development-experience-principles-and-refinements-spiral-development-workshop-february-9-2000/)、[PDF 全文](https://www.sei.cmu.edu/documents/5439/2000_003_001_13655.pdf)

### 2.4 迭代與增量開發

迭代開發（iterative development）跟增量開發（incremental development）常常一起講，但講的是兩件不同的事：迭代指的是同一部分功能反覆修正、一輪比一輪更完整；增量指的是把整個系統拆成一塊一塊，一塊一塊交付，先交出來的那塊可以先讓使用者用。兩者合在一起，就是「先交付一小塊夠用的功能，用了之後的回饋拿來修正下一塊要做什麼」，這正是後面敏捷式方法的基礎精神。跟瀑布式、V 模型的差異在於：後者假設一開始就能把全部需求想清楚，前者承認想不清楚是常態，用反覆交付去逐步逼近正確答案。

## 三、敏捷式與 Scrum

敏捷式（Agile）是一組共同的價值觀與原則，具體怎麼落地要看採用哪一套做法：Scrum、XP 是明確的敏捷框架，Kanban 官方把自己定位成最佳化價值流動的「策略」（strategy）而非框架，三者的定位層級不完全一樣，但都常見於敏捷式的實務脈絡裡，詳見以下各節。

### 3.1 Agile Manifesto 四大價值

2001 年，17 位軟體開發者在猶他州的一次聚會上共同發表了《敏捷軟體開發宣言》（Manifesto for Agile Software Development），提出四大價值（原文附中譯，中譯採直譯，「over」譯為「重於」）：

| 原文 | 中譯 |
|---|---|
| Individuals and interactions over processes and tools | 個人與互動，重於流程與工具 |
| Working software over comprehensive documentation | 可用的軟體，重於詳盡的文件 |
| Customer collaboration over contract negotiation | 與客戶合作，重於合約談判 |
| Responding to change over following a plan | 回應變化，重於遵循計畫 |

宣言本身特別註明：右邊列的項目不是沒有價值，只是左邊的項目價值更高。來源：[Manifesto for Agile Software Development](https://agilemanifesto.org/)（另有[十二項原則](https://agilemanifesto.org/principles.html)，本頁不逐條列出，感興趣可直接看原文）。

### 3.2 Scrum：職責歸屬、事件、產出物

Scrum 是一套敏捷框架，規則寫在官方的《The Scrum Guide》，目前引用版本是 2020 年 11 月版[^scrum2020]。

**三項職責歸屬（accountabilities，合稱 Scrum Team）：**

2020 年版把 Scrum Team 內部的分工從「角色（roles）」改稱為「職責歸屬（accountabilities）」，強調的是每個人對什麼結果負責，而不是一個固定的職稱標籤：

- **開發者（Developers）**：每個 Sprint 負責產出可用增量（Increment）的人。
- **產品負責人（Product Owner）**：對最大化產品價值負責，管理產品待辦清單（Product Backlog），決定要做什麼、先做什麼。
- **Scrum Master**：建立並維護 Scrum 的運作方式，教練團隊、排除障礙，並協助組織理解 Scrum。2020 年版的原句是「Scrum Masters are true leaders who serve the Scrum Team and the larger organization」（Scrum Master 是服務 Scrum 團隊與更大的組織的真正領導者）[^scrum2020]。

**五個事件（Events）：Sprint 本身也是一個事件，是容納其餘四個正式事件的容器：**

| 事件 | 內容 |
|---|---|
| Sprint | 固定長度、一個月以內的時間盒，所有工作都在裡面完成，也是容納其餘四個事件的容器 |
| Sprint Planning | 啟動 Sprint，訂出 Sprint Goal 並選出這個 Sprint 要做的工作 |
| Daily Scrum | 每天 15 分鐘，開發者檢視朝 Sprint Goal 的進度並調整計畫 |
| Sprint Review | 向利害關係人展示成果並討論後續調整 |
| Sprint Retrospective | 團隊反思這個 Sprint 的做法，找出下一步要怎麼改善 |

**三個產出物（Artifacts）與各自的承諾（Commitment）：**

| 產出物 | 承諾 |
|---|---|
| Product Backlog（產品待辦清單） | Product Goal：產品的長期目標 |
| Sprint Backlog（Sprint 待辦清單） | Sprint Goal：這個 Sprint 唯一的目標 |
| Increment（增量） | Definition of Done：這塊產出要符合的品質標準 |

「承諾」是 2020 年版新增的概念。官方修訂說明給的理由是這些承諾「exist to bring transparency and focus toward the progress of each artifact」（為每個產出物的進展帶來透明度與聚焦）[^scrumrev]；指南本文的說法則是「These commitments exist to reinforce empiricism and the Scrum values for the Scrum Team and their stakeholders」（強化經驗主義與 Scrum 價值觀）[^scrum2020]。

[^scrum2020]: Schwaber, K., & Sutherland, J. (2020). *The Scrum Guide*. <https://scrumguides.org/scrum-guide.html>
[^scrumrev]: Scrum Guides. Revision History（2020 年版修訂說明）. <https://scrumguides.org/revisions.html>

### 3.3 Kanban

官方《Kanban Guide》（2025 年 5 月版）把 Kanban 定義為「最佳化價值流動的策略」（a strategy for optimizing the flow of value through a process），關注的重點是持續的工作流動，跟 Scrum 那種固定時間盒的衝刺是不同的節奏設計。Kanban 由三個互相搭配的做法組成：定義並視覺化工作流程（畫出工作從開始到完成要經過哪些狀態）、主動管理流程中的項目、持續改善流程本身。在製品（Work in Progress，WIP）的控制是核心機制之一，官方原文要求「團隊成員必須明確控制工作流程裡從開始到完成之間的項目數量」（Kanban system members must explicitly control the number of work items in a workflow from started to finished），但控制的具體形式由團隊自行決定，不一定要是每個階段各自訂一個數字上限，也可以是團隊認可的其他視覺化控制方式。官方另外訂出四個必須追蹤的流動指標：WIP（已開始未完成的項目數）、產出量（單位時間完成的項目數）、項目年齡（項目已經開始但還沒完成的時間）、週期時間（項目從開始到完成的時間）。來源：[Kanban Guide 2025.5](https://kanbanguides.org/the-kanban-guide/2025.5/)。

### 3.4 XP 極限編程（摘要）

極限編程（Extreme Programming，簡稱 XP）由 Kent Beck 在《Extreme Programming Explained: Embrace Change》（Addison-Wesley，1999 年初版；2004 年與 Cynthia Andres 合著第二版）中提出，是一套把敏捷價值觀落實到工程實務細節的具體做法，包含測試先行、持續整合、結對程式設計、重構、簡單設計、共同擁有程式碼等一系列實踐。這幾項實踐的詳細做法（尤其測試先行，也就是 TDD 的起點）留到下一頁[開發實踐：TDD、BDD、DDD 與 SDD](dev-practices.md)展開，這裡只點出 XP 在 SDLC 光譜上的位置：它跟 Scrum 一樣屬於明確的敏捷框架，講的是工程師寫程式當下該怎麼做；Scrum 講的是團隊怎麼安排工作節奏；Kanban 則是官方定位為策略層級的做法，三者處理的問題不完全一樣。Agile Alliance 的公開詞彙表把 XP 列為「在軟體開發工程實務上規範最具體的敏捷框架」，列出的實踐包含 Pair Programming（結對程式設計）、Test-First Programming（測試先行）、Continuous Integration（持續整合）、Incremental Design（漸進式設計）等項目[^xpaa]。

[^xpaa]: Agile Alliance. What is Extreme Programming (XP)? <https://agilealliance.org/glossary/xp/>

## 四、DevOps 與 CI/CD

DevOps 是開發（Development）與維運（Operations）合流的做法，目標是縮短「寫完程式」到「安全上線」之間的距離。落實 DevOps 常會提到三個容易混用的詞：

- **持續整合（Continuous Integration，CI）**：Martin Fowler 的定義是團隊每個成員至少每天把自己的修改整合進主線一次，每次整合都由自動化建置（含測試）驗證，儘快抓出整合上的錯誤[^ci]。前提是程式碼本身要有夠完整的自動化測試（self-testing code），沒有測試，CI 就只是「常常把可能壞掉的東西合併進主線」。
- **持續交付（Continuous Delivery，CD）**：軟體隨時維持在「可以被部署到正式環境」的狀態，但不代表每次修改都真的會被部署上去，交付與部署是兩件事[^cd]。
- **持續部署（Continuous Deployment）**：每一次通過流程的修改都自動被部署到正式環境，一天可能發生很多次部署。持續部署是持續交付的進一步實踐，持續交付是持續部署的前提，但持續交付不強制要求持續部署[^cd]。

支撐 CI 的一個常見版本控制作法是**主幹開發（trunk-based development）**：開發者共同在一條主線（trunk）上工作，避免長期存在的功能分支，官方說法是團隊成員至少每 24 小時要合併回主幹一次[^tbd]。Google 主導的 DevOps 研究計畫 DORA 把主幹開發列為跟軟體交付表現相關的能力之一，2016 到 2017 年的研究發現同時採用主幹開發與 CI 的團隊，交付速度、穩定性等表現通常較好[^dora]。

[^ci]: Fowler, M. (2006, updated). Continuous Integration. <https://martinfowler.com/articles/continuousIntegration.html>
[^cd]: Fowler, M. Continuous Delivery. <https://martinfowler.com/bliki/ContinuousDelivery.html>
[^tbd]: Trunk Based Development. <https://trunkbaseddevelopment.com/>
[^dora]: DORA. Trunk-based development. <https://dora.dev/capabilities/trunk-based-development/>

## 五、安全開發：NIST SSDF

美國國家標準與技術研究院（NIST）在《SP 800-218：Secure Software Development Framework（SSDF）》裡，把安全開發實務整理成四個高層次的實踐群組[^ssdf]：

| 群組 | 縮寫 | NIST 原文說明 |
|---|---|---|
| Prepare the Organization（準備好組織） | PO | 確保組織的人員、流程、技術，已經準備好在組織層級執行安全的軟體開發 |
| Protect the Software（保護軟體） | PS | 保護軟體的所有元件，不被竄改或未授權存取 |
| Produce Well-Secured Software（產出足夠安全的軟體） | PW | 透過安全的開發實務，讓每次發布的軟體只帶有最少的安全性弱點 |
| Respond to Vulnerabilities（回應弱點） | RV | 找出軟體發布後殘留的弱點，妥善回應，並避免類似弱點未來再發生 |

SSDF 不規定用哪種流程模型（瀑布式或敏捷式都可以套），只規定在整個生命週期裡，安全這件事要在哪些節點被處理到。截至查證日，正式版仍是 SP 800-218（SSDF v1.1）；NIST 已於 2025-12-17 公開 SP 800-218 Rev. 1（SSDF v1.2）的初版公開草案，尚未定案[^ssdfdraft]。

[^ssdf]: NIST. Secure Software Development Framework (SSDF). <https://csrc.nist.gov/projects/ssdf>；完整規格見 [NIST SP 800-218](https://csrc.nist.gov/pubs/sp/800/218/final)。
[^ssdfdraft]: NIST. SP 800-218 Rev. 1 (Initial Public Draft). <https://csrc.nist.gov/pubs/sp/800/218/r1/ipd>；發布清單見 <https://csrc.nist.gov/projects/ssdf/publications>。

## 六、流程模型比較與怎麼選

| 模型 | 需求變動彈性 | 交付頻率 | 適合場合 | 主要風險 |
|---|---|---|---|---|
| 瀑布式 | 低 | 一次性交付 | 需求穩定、法規或硬體限制多 | 晚期發現需求誤解，修正成本極高 |
| V 模型 | 低 | 一次性交付 | 對驗證流程要求嚴謹（醫療、航太） | 跟瀑布式相同，且前期投入更多在測試計畫 |
| 螺旋模型 | 中，依風險決定 | 依風險分圈交付原型或子系統 | 高風險、高不確定性的大型專案 | 需要有能力持續辨識與評估風險的人，管理成本較高 |
| Scrum | 高 | 每個 Sprint（固定長度，一個月以內） | 需求會隨回饋調整、產品方向需要驗證 | 團隊自律要求高，Sprint 節奏被打斷會影響效果 |
| Kanban | 高 | 持續交付，沒有固定節奏 | 工作型態偏向持續進來的請求（維運、支援） | 沒有明確定義 WIP 怎麼控制，流動效果就會打折 |
| DevOps／CI/CD | 高 | 可到每次修改即部署 | 已有足夠自動化測試與部署基礎 | 自動化測試不足時，等於加快把錯誤送上線的速度 |

怎麼選，一個粗略的判斷順序：需求已經確定、之後幾乎不會變、涉及實體或高成本變更（例如硬體整合）→ 偏向瀑布式或 V 模型；需求會隨著做出來的東西而調整、想儘早拿到使用者回饋 → 偏向 Scrum 或 Kanban；專案本身風險高、不確定性大到需要先做實驗才知道怎麼繼續 → 螺旋模型的精神值得參考（不一定要照搬整套流程）；不管選哪種流程模型，只要團隊有能力做到頻繁、可靠的整合與部署，DevOps／CI/CD 的實務都值得疊加上去，它處理的是「怎麼把已經寫好的程式碼安全送上線」，跟「怎麼安排開發階段」是兩個不同的問題，可以同時採用。

## 資料來源

| 主張 | 來源 |
|---|---|
| SDLC 六階段拆解 | 整理者依業界通用拆法歸納，非逐字引用單一出處，屬於常識性架構而非個人推論 |
| 瀑布式的單向階段結構 | Royce 1970 論文 Figure 2（印刷頁 329 前一頁的圖，圖說：Implementation steps to develop a large computer program for delivery to a customer） |
| 瀑布式的適用場合與缺點 | 整理者觀察，正文已標示，無單一出處 |
| Royce 1970 論文原文（含頁碼） | Royce, W. W. (1970). *Proceedings, IEEE WESCON*, 1–9；重印版印刷頁 328–338，引文見 329、330、334 頁，原始 PDF：<https://cse.msu.edu/~cse435/Homework/HW3/royce1970.pdf> |
| V 模型定義（開發階段與測試層級一對一對應） | [ISTQB Glossary：V-model](https://glossary.istqb.org/en_US/term/v-model)（定義原文取自 <https://api.glossary.istqb.org/v1/terms/v-model>）、[ISTQB CTFL Syllabus v4.0.1](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf) 2.1.1 節 |
| V 字圖形畫法、V 模型的適用場合 | 整理者說明／整理者觀察，正文已標示，官方定義未涵蓋 |
| 螺旋模型論文出處（1986、1988） | Boehm, B. (1986). *ACM SIGSOFT Software Engineering Notes*, 11(4), 14–24. <https://doi.org/10.1145/12944.12948>；Boehm, B. (1988). *IEEE Computer*, 21(5), 61–72. <https://doi.org/10.1109/2.59> |
| 「風險驅動的流程模型產生器」原句 | [Boehm (2000), CMU/SEI-2000-SR-008](https://www.sei.cmu.edu/library/spiral-development-experience-principles-and-refinements-spiral-development-workshop-february-9-2000/) 1.2 節、印刷頁 3（[PDF](https://www.sei.cmu.edu/documents/5439/2000_003_001_13655.pdf)） |
| Agile Manifesto 四大價值、十二項原則 | [agilemanifesto.org](https://agilemanifesto.org/)、[principles.html](https://agilemanifesto.org/principles.html) |
| Scrum 職責歸屬／事件／產出物（2020 版） | [The Scrum Guide](https://scrumguides.org/scrum-guide.html)、[下載頁](https://scrumguides.org/download) |
| 承諾（commitments）新增的理由 | [Scrum Guides 修訂說明](https://scrumguides.org/revisions.html)、[The Scrum Guide](https://scrumguides.org/scrum-guide.html) |
| Kanban 定義、WIP 控制原文、流動指標 | [Kanban Guide 2025.5](https://kanbanguides.org/the-kanban-guide/2025.5/) |
| XP 起源 | Beck, K. (1999). *Extreme Programming Explained: Embrace Change*. Addison-Wesley（書籍原文無公開全文可逐字核對） |
| XP 實踐清單 | [Agile Alliance：What is Extreme Programming (XP)?](https://agilealliance.org/glossary/xp/) |
| 持續整合定義 | [Fowler：Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html) |
| 持續交付／持續部署差異 | [Fowler：Continuous Delivery](https://martinfowler.com/bliki/ContinuousDelivery.html) |
| 主幹開發定義 | [trunkbaseddevelopment.com](https://trunkbaseddevelopment.com/) |
| 主幹開發與交付表現的關聯 | [DORA：Trunk-based development](https://dora.dev/capabilities/trunk-based-development/) |
| NIST SSDF 四個實踐群組（v1.1 正式版） | [NIST：SSDF 專案頁](https://csrc.nist.gov/projects/ssdf)、[NIST SP 800-218](https://csrc.nist.gov/pubs/sp/800/218/final) |
| NIST SSDF v1.2 公開草案狀態 | [SP 800-218 Rev.1 IPD](https://csrc.nist.gov/pubs/sp/800/218/r1/ipd)、[SSDF 發布清單](https://csrc.nist.gov/projects/ssdf/publications) |

延伸：[開發實踐：TDD、BDD、DDD 與 SDD](dev-practices.md)｜[AI 代理時代的 SDLC](sdlc-ai-agent.md)
