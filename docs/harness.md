# 把 AI 代理的工作環境設計得可靠

> 查證日期：2026-09-16。方案與功能變動快，請以官方最新說明為準。

前兩頁講的是[代理怎麼運作](agent-basics.md)跟[各種擴充機制解決什麼問題](extensions.md)。這頁講的是另一件事：當你把一個資料夾交給 Claude Code 或 Codex 這類代理型工具之後，怎麼把它的工作環境設計得讓人放心，什麼工作該交給誰、產出怎麼驗、說明檔為什麼不能越寫越長。這些道理來自官方對自己「harness」的說明，不是特定工具的操作手冊。

## 一、什麼是 harness

官方文件把 Claude Code 稱為一種 agentic harness，但沒有給出教科書式的定義，是描述性用法：圍繞模型的**工具、上下文管理與執行環境**這三件事合起來，構成模型實際做事的框架[1]。模型本身只負責推理，harness 決定它能看到什麼、能碰到什麼、每一步做完之後誰來檢查。

這對一般使用者有一個直接含意：同一個模型，換一套環境設計，產出的可靠度可以差很多。真正該花心思設計的是流程本身：這件事要不要獨立開一個乾淨視角、做完之後誰來驗、什麼事情該用機制卡住而不是用文字提醒，比起怎麼下更好的提示詞更值得花時間。

!!! note "本頁的官方權威來源（查證日期 2026-09-16）"
    以下每一條論點都能在這張表對應到原文，不是憑印象轉述：

    | 來源 | URL | 用途 |
    |---|---|---|
    | How Claude Code works | https://code.claude.com/docs/en/how-claude-code-works | harness 自我定義 |
    | Best practices | https://code.claude.com/docs/en/best-practices | 驗證、失敗模式、subagent |
    | Sub-agents | https://code.claude.com/docs/en/sub-agents | model/effort 解析順序 |
    | Memory | https://code.claude.com/docs/en/memory | CLAUDE.md 與 MEMORY.md 上限 |
    | Skills | https://code.claude.com/docs/en/skills | progressive disclosure |
    | Hooks guide | https://code.claude.com/docs/en/hooks-guide | hook 限制 |
    | A Harness for Every Task | https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code | 動態 workflow |
    | Effective harnesses for long-running agents | https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents | 長跑任務結構 |
    | Effective context engineering | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | context 經濟學 |
    | Building effective agents | https://www.anthropic.com/engineering/building-effective-agents | 複雜度判準 |
    | Writing tools for agents | https://www.anthropic.com/engineering/writing-tools-for-agents | 工具設計 |
    | Multi-agent research system | https://www.anthropic.com/engineering/multi-agent-research-system | 平行化的代價 |

## 二、七個讓工作環境可靠的原則

### 2.1 做事的人不該驗收自己的活

官方講驗證用的子代理（verification subagent）時直接寫：做這件事的模型，不該是替它打分的模型。原因很直覺，一份東西是自己寫的，自己審查時很容易帶著「我當初是這樣想的」去護航，看不出盲點[2]。

### 2.2 驗收官只看結果，不看你怎麼想的

延續上一條，官方進一步要求：負責審查的子代理只應該看到 diff（實際改動了什麼）與驗收條件，看不到產生這份改動的推理過程。理由是推理過程會把審查者帶偏，如果驗收官事先知道「作者當時是這樣考慮的」，很容易順著這個邏輯去確認，而不是獨立判斷結果對不對[2]。

### 2.3 驗收找到的問題不必照單全收

官方特別提醒：只要你要求審查者去找問題，它就一定會找出問題來，而且會一直找下去。如果每一條都要求修正，結果就是不斷疊加複雜度（over-engineering）。真正該處理的，是會影響正確性、會影響你原本需求的發現；其餘瑣碎的建議，可以判斷後決定不修，但要講清楚跳過了什麼、為什麼[2]。

### 2.4 讓子代理去探索，不要污染主線對話

官方把上下文隔離列為子代理最核心的價值，並明講「探索型」子代理存在的理由，就是把搜尋、掃描檔案這類會產生大量雜訊的過程，擋在主線對話之外[3]。你跟 AI 討論一件事該怎麼做的那個對話視窗，不需要看到它翻找了幾十個檔案的過程，只需要看到它找到的結論。

### 2.5 說明檔案太長，重要規則反而會被忽略

官方逐字寫過：一份臃腫的專案說明檔（Claude Code 裡是 CLAUDE.md，Codex 裡是 AGENTS.md）會讓模型忽略真正重要的指令，並建議逐行自問，這一行拿掉，模型會不會因此犯錯。拿不出答案的行，就是灌水，該刪或該搬到只在需要時才載入的 skill 裡（skill 的分工見[SKILL、Plugin、MCP 與 Subagent](extensions.md)）[4]。

### 2.6 該強制的事交給機制，不要只寫進說明檔

官方一句話講完這條邊界：hooks are deterministic, CLAUDE.md instructions are advisory[5]。意思是，說明檔裡的規則只是「建議」，模型有可能因為疏忽或上下文太滿而沒照做；真正不能妥協的規矩（例如某個資料夾禁止修改），要用會強制擋下動作的機制去卡，不能只靠寫在說明檔裡祈禱模型記得。

### 2.7 拿出證據，不要只說「做完了」

官方要求 show evidence rather than asserting success，並指出一個容易被忽略的處境：當沒有可以直接執行的檢查時，「看起來做完了」其實是模型唯一拿得到的訊號，它自己也分不清「真的做完」跟「看起來做完」[4]。這也是為什麼「已經改好了」這句話本身不構成證據，附上實際跑出來的結果、或請另一個乾淨視角核對過，才算數。

!!! tip "兩個技術性補充"
    子代理回報時，官方建議濃縮成大約一千到兩千 token 的摘要交還給主線對話，而不是把整個過程搬回去，這跟原則 2.4 是同一個道理，細節留在子代理那邊，主線只要結論[3]。另外，選擇要用哪個模型、要花多少推理力度時，派工當下明講的參數，優先於子代理定義檔裡寫死的設定，優先於環境變數，優先於主線對話當下用的模型，愈靠近這次任務現場的指定，權重愈高[3]。

## 三、驗證的四種力度

官方把驗證的強度分成四級，由弱到強[4]：

1. **寫在提示詞裡的驗收條件**，最基本，但也最容易被模型自己「已經做到」的錯覺蓋過去。
2. **用 `/goal` 設定持續驗證的目標條件**，讓工作進行中就不斷回頭核對是否偏離目標，不是等到最後才驗。這一級在實務上常被忽略，因為它需要事前多花一步設定，不像其他三級那樣自然而然會用到。
3. **用 hook 當硬性關卡**，不管模型自己覺得做完了沒有，機制到了那一步就是會擋下來檢查，對應原則 2.6。
4. **第二意見子代理互相駁斥**，兩個獨立視角各自作答，答案一致就收，分歧本身就是最有價值的訊號，代表這裡有需要人判斷的模糊地帶。

四級不是互斥的，愈重要的產出，愈值得疊加使用多級。

## 四、動態 harness 與靜態規則表：一組取捨

官方另一篇文章主張的方向，是讓模型在執行當下自己決定要不要開子代理、要隔離到什麼程度、該用哪個模型，也就是模型當場就依照眼前這個任務，即時寫出一套適合它的工作方式，而不是套用一份固定不變的清單[6]。

這跟「事先把規則寫成一張固定的表，任務來了就照表操作」是兩種相反的路線。固定表格的好處是可預測、可以事後稽核，不用依賴模型當下判斷力夠不夠；代價是遇到表格沒設想到的情境，就會被硬套進去，反而做出奇怪的選擇。兩種路線沒有絕對的對錯，是看你更在意「可預測」還是「能應變」。

這條取捨還牽出官方列出的一個失敗模式：同一件事被反覆糾正、模型還是一直錯在同樣的地方。官方的處置方式是把這段對話清掉重開，理由是錯誤的理解已經污染了這整段上下文，愈往下修正，愈是在錯誤的地基上疊加新內容[4]。這跟「再多解釋一次、再多給一個例子」是不同方向的處置，值得知道這個選項存在。

## 五、多代理協作不是免費的

官方分析自家的多代理研究系統時提到兩個代價：依 Anthropic 當時的資料，一個代理（agent）跑一項任務，token 用量大約是一般聊天的四倍；讓多個代理一起協作（multi-agent），token 用量則大約是一般聊天的十五倍，這個十五倍是跟一般聊天比，不是跟單一代理比。而且大多數任務裡，真正能平行拆開、彼此不互相依賴的子任務，其實比研究類任務少[7]。

這條的含意是：不是每個工作都值得拆成好幾個代理同時做。一個任務值得平行處理的前提是，它真的能拆成幾塊互不依賴的子任務，如果拆出來的幾塊其實要先後接力、還要互相對照，拆開平行反而只是多花好幾倍成本，得到差不多的結果。

## 六、說明檔案的篇幅上限

延續原則 2.5，官方對兩份常駐說明檔給出具體數字：

- **CLAUDE.md（或 Codex 的 AGENTS.md）**：建議控制在 200 行以內[8]。
- **長期記憶檔（MEMORY.md 這類 auto memory 機制）**：官方訂出硬上限，200 行或 25 KB，兩個門檻先到哪個就在哪個卡住，超過的部分不會被載入[8]。

這裡有一個容易被忽略的計算陷阱：如果你的記憶條目習慣寫得偏長，行數上限可能永遠碰不到，反而是位元組數先超標。假設每則記憶平均落在兩百位元組上下的密度，25 KB 除以每則約 200 位元組，大約等於 125 則，就會先撞上這道牆，而不是等到兩百行才被截斷。換句話說，記憶檔案該不該精簡，不能只數有幾行，要抓出真正先觸頂的是哪一個門檻。

## 七、給一般使用者的實際做法

把前面六節收斂成幾件真的做得到的事：

1. **驗收另開一個乾淨對話**。請 AI 改完一件事之後，不要在同一個對話裡追問「你改得對嗎」，它會順著剛才的思路護航自己。開一個新對話，只給它驗收條件（例如「檢查有沒有失效連結、檢查格式是否一致」），不給它原本的討論過程。
2. **要求它貼出證據，不要接受「已完成」這句話**。改完之後，問它「你怎麼確認改對了」，要它給出實際比對的結果，而不是一句斷言。
3. **CLAUDE.md 或 AGENTS.md 只放事實與紅線，寫長了就搬進 skill**。一旦你發現說明檔裡某一段其實是一套步驟而不是一條事實，那一段就該獨立成[skill](extensions.md)。
4. **同一個錯誤被你糾正兩次以上還是沒改對，就換一個乾淨對話重新交代，不要在原地繼續解釋第三次**。這代表這段對話的理解已經歪掉，再解釋只是往歪掉的地基上疊。
5. **不是每件事都值得拆成多個子代理同時做**。先問這個任務真的能拆成互不依賴的幾塊嗎，拆不開的話，平行處理只是花更多成本換差不多的結果。
6. **高風險的判斷（會直接影響最終決定的內容、不可逆的操作），值得多要一次第二意見**，讓兩個獨立回答互相對照，分歧的地方就是你該親自拍板的地方。

## 本頁重點回顧

- harness 是圍繞模型的工具、上下文管理與執行環境，不是模型本身的推理能力。
- 七個可靠性原則：做事的人不驗自己、驗收官只看結果不看推理、找到的問題不必照單全收、探索交給子代理別污染主線、說明檔太長規則會被忽略、該強制的事交給機制、拿證據而非斷言。
- 驗證力度分四級，愈重要的產出愈該疊加使用。
- 動態即時決定 vs 事先寫死規則，是可預測與能應變之間的取捨，沒有標準答案。
- 多代理協作不是免費的，只有真的能拆開的任務才值得平行處理。
- 說明檔案與記憶檔都有篇幅上限，記憶檔真正先觸頂的常常是位元組數而不是行數。

## 資料來源

| 標記 | 來源 | URL |
|---|---|---|
| [1] | How Claude Code works | <https://code.claude.com/docs/en/how-claude-code-works> |
| [2] | Best practices for Claude Code（對抗性審查一節） | <https://code.claude.com/docs/en/best-practices> |
| [3] | Create custom subagents | <https://code.claude.com/docs/en/sub-agents> |
| [4] | Best practices for Claude Code（驗證、失敗模式） | <https://code.claude.com/docs/en/best-practices> |
| [5] | Hooks reference | <https://code.claude.com/docs/en/hooks> |
| [6] | A Harness for Every Task | <https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code> |
| [7] | How we built our multi-agent research system（4 倍／15 倍 token 用量對照） | <https://www.anthropic.com/engineering/multi-agent-research-system> |
| [8] | How Claude remembers your project（CLAUDE.md、MEMORY.md 篇幅上限） | <https://code.claude.com/docs/en/memory> |

延伸：[AI Agent 怎麼運作](agent-basics.md)｜[SKILL、Plugin、MCP 與 Subagent](extensions.md)
