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
    | Hooks guide | https://code.claude.com/docs/en/hooks-guide | hook 限制、Stop hook 驗收範例 |
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

## 三之一、把原則變成可照做的範例

前面講的都是原則。這節把其中三條落到可以直接照抄的樣子（本節查證日期 2026-09-17）。這裡示範的是「原則怎麼落地」，各種機制本身怎麼設定、放在哪個資料夾，見[SKILL、Plugin、MCP 與 Subagent](extensions.md)，不在這裡重複。

每個範例都標示來源等級，請先看清楚標示再照抄：

- **【官方逐字】**：官方文件裡原封不動的句子或設定，本站只加中文說明。
- **【官方改寫】**：骨架與要素來自官方，中文句子是本站依它的結構改寫的，不是官方原文。
- **【整理者自創】**：官方沒有給這個角度的東西，是依前面的原則推出來的建議寫法，請當成建議而不是官方結論。

### 對應原則 2.1／2.2：派一個只看 diff 的驗收子代理

官方對這件事的描述是【官方逐字】：在乾淨子代理上下文裡跑的審查者「sees only the diff and the criteria you give it, not the reasoning that produced the change」，所以它是就結果本身作判斷[9]。

官方在同一節給出的派工範例，原文如下【官方逐字】[9]：

```text
Use a subagent to review the rate limiter diff against PLAN.md. Check that
every requirement is implemented, the listed edge cases have tests, and
nothing outside the task's scope changed. Report gaps, not style preferences.
```

官方也把這段話的結構講明了：派工時要點名三件事——要驗的東西（name the work to check）、拿什麼當驗收標準（the plan to check it against）、什麼才算一個問題（what counts as a finding）[9]。

依這三個要素改寫成中文範本，可以直接套用【官方改寫：要素來自官方，以下中文句子不是官方原文】：

```text
請開一個乾淨的子代理驗收下面這件事，只看結果，不要看我前面的討論過程。

要驗的東西：<這次改動的檔案或 diff>
驗收標準：<標準寫在哪，例如 PLAN.md、需求清單，或直接列在這裡的三條條件>

請逐條檢查：
1. 驗收標準裡的每一條是不是都真的做到了？做到的請指出在哪個檔案的哪一段。
2. 標準裡列出的邊界情況，有沒有對應的檢查或測試？
3. 有沒有改到這次任務範圍以外的東西？

只回報會影響正確性、或違反上述標準的缺口；風格與個人偏好不用回報。
```

最後一句對應原則 2.3：官方提醒，被要求找問題的審查者通常一定會找出問題來，所以要事先講明什麼才值得回報[9]。另外，如果只是要檢查改動有沒有 bug，官方說 Claude Code 內建的 `/code-review` 就是在乾淨的子代理裡審目前的 diff 並把發現帶回主線，不必自己寫這段提示詞[9]。

!!! note "沒有子代理功能的人怎麼照做"
    【官方改寫：分工來自官方，以下是中文轉述，不是官方原文】官方另外給了一組 Writer／Reviewer 的兩個對話分工：A 視窗負責實作，B 視窗只拿到「要看哪個檔案、要找哪一類問題」這兩件事，再把 B 的輸出貼回 A 去修[9]。重點不在有沒有 subagent 這個功能，而在於驗收的那個視角沒看過實作當下的推理過程——一般聊天視窗另開一個新對話一樣做得到。

### 對應原則 2.7：什麼樣的回報才算附了證據

官方講證據的那一句是【官方逐字】：「Have Claude show evidence rather than asserting success: the test output, the command it ran and what it returned, or a screenshot of the result.」[4] 三種形式講得很具體：測試輸出、跑了哪一行指令與它回傳了什麼、結果的截圖。

官方在同一節給的對照表，左邊是驗不了的問法，右邊是把驗收條件寫進去的問法【官方逐字，括號內為中文說明】[4]：

| 不夠格：無法驗證的交辦 | 夠格：自帶檢查的交辦 |
|---|---|
| implement a function that validates email addresses（實作一個驗 email 的函式） | write a validateEmail function. example test cases: user@example.com is true, invalid is false, user@.com is false. run the tests after implementing（附三組具體測資，實作完把測試跑一遍） |
| make the dashboard look better（把儀表板弄好看一點） | \[paste screenshot] implement this design. take a screenshot of the result and compare it to the original. list differences and fix them（附設計稿，做完截圖跟原稿比對，列出差異再修） |
| the build is failing（建置壞了） | the build fails with this error: \[paste error]. fix it and verify the build succeeds. address the root cause, don't suppress the error（貼上錯誤訊息，修完要驗證建置成功，而且要處理根因，不是把錯誤壓掉） |

把這張表反過來用，就是收到回報時該檢查的東西【整理者依上述官方原文歸納的清單，官方沒有直接給這份對照】：

- **不夠格的回報**：「已經修好了」「應該沒問題了」「我檢查過了」「都確認過沒問題」——這幾句話沒有任何一個你可以複驗的東西，它們是斷言不是證據。
- **夠格的回報要附三樣**：（一）跑了哪一行指令；（二）原封不動的輸出，不是它轉述的結論；（三）對照的基準是什麼——哪一份需求、哪一張設計稿、哪一個測試檔。三樣缺一樣，你就只能相信它，不能核對它。

官方補的理由值得記住：當沒有可以執行的檢查時，「看起來做完了」是模型唯一拿得到的訊號[4]。

### 對應第三節第 3 級：用 Stop hook 擋住「還沒驗證就說做完」

第三節第 3 級講 hook 當硬性關卡。要卡的如果是「宣稱完成」這件事，對應的事件不是編輯檔案前的 `PreToolUse`，而是 Claude 結束回應時觸發的 `Stop`【整理者說明：選哪個事件是本站依原則推出來的判斷，官方文件本身只寫 Stop hook 會在 Claude 結束回應時觸發[10]】。

官方給的最小範例，是用一個 prompt 型 hook 在收工前問模型「事情是不是真的都做完了」，回 `ok: false` 就把 `reason` 丟回去讓它繼續做【官方逐字】[10]：

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check if all tasks are complete. If not, respond with {\"ok\": false, \"reason\": \"what remains to be done\"}."
          }
        ]
      }
    ]
  }
}
```

如果要卡的是「到底有沒有真的跑過測試」，官方另給一個 agent 型 hook 的範例，它會實際去跑測試、看結果，再決定放不放行【官方逐字】[10]：

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "agent",
            "prompt": "Verify that all unit tests pass. Run the test suite and check the results. $ARGUMENTS",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

官方把這兩種 hook 的分工一句話講完：hook 收到的輸入資料本身就夠判斷時，用 prompt hook；需要對照程式碼實際狀態才判斷得出來時，用 agent hook[10]。這兩個範例跟 [extensions.md](extensions.md) 裡那個「擋掉敏感檔案編輯」的 hook 是不同用途：那個是用機制守住紅線，這兩個是用機制守住驗收。

!!! warning "三個官方講明的限制"
    【官方改寫：三條限制都出自官方文件，以下是中文轉述，不是官方逐字原文】

    - agent hook 官方標為實驗性（experimental），設定與行為可能改變，正式流程官方建議用 command hook[10]。
    - `Stop` hook 只要 Claude 結束回應就會觸發，不是只在任務完成時觸發；使用者按中斷時不會觸發[10]。
    - 連續阻擋八次而沒有進展之後，Claude Code 會覆蓋掉這個 Stop hook、讓回合結束[10]。

針對第三點，官方給的防呆寫法是在腳本開頭讀 `stop_hook_active` 欄位，已經是被自己擋下來續跑的那一輪就直接放行【官方逐字】[10]：

```bash
#!/bin/bash
INPUT=$(cat)
if [ "$(echo "$INPUT" | jq -r '.stop_hook_active')" = "true" ]; then
  exit 0  # Allow Claude to stop
fi
# ... rest of your hook logic
```

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
- 三個可照抄的落地範例：官方的驗收子代理派工提示詞（要驗什麼、拿什麼當標準、什麼才算問題）、「附證據」與「只說做完了」的正反對照、用 `Stop` hook 在收工前強制檢查的最小設定；每個範例都標示了是官方逐字、官方改寫，還是本站自創。
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
| [9] | Best practices for Claude Code（Add an adversarial review step：驗收子代理派工範例、Writer／Reviewer 分工） | <https://code.claude.com/docs/en/best-practices> |
| [10] | Automate actions with hooks（Stop hook 的 prompt／agent 範例、八次阻擋上限與 `stop_hook_active`） | <https://code.claude.com/docs/en/hooks-guide> |

延伸：[AI Agent 怎麼運作](agent-basics.md)｜[SKILL、Plugin、MCP 與 Subagent](extensions.md)
