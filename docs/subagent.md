# Subagent 入門與實戰

> 查證日期：2026-09-19。方案與功能變動快，請以官方最新說明為準。

[SKILL、Plugin、MCP 與 Subagent](extensions.md)那頁已經把 Subagent 放進六種擴充機制的總表比較過；[Hooks 與 Subagent 設定](hooks-subagents.md)整理過 frontmatter 每個欄位的語意與內建 agent 清單。這頁只挖 Subagent 這一項，把上面兩頁沒空間深入的部分補齊：官方文件實際定義的 18 個欄位（含前兩頁沒收錄的 `fable`／`background`／`omitClaudeMd`／`effort`／`initialPrompt`／`experimental` 六項）、`background` 欄位怎麼偷偷換掉工具清單、`isolation: worktree` 實際怎麼擋住越界的指令、`SendMessage` 怎麼續問一個已經跑完的 subagent，以及多代理協作真正的成本是多少倍。

## 1. Subagent 是什麼、什麼時候該用

官方原文把使用時機講得很直接：「Use one when a side task would flood your main conversation with search results, logs, or file contents you won't reference again: the subagent does that work in its own context and returns only the summary. Define a custom subagent when you keep spawning the same kind of worker with the same instructions.」[1] 白話說：一個側支任務如果會把主對話塞滿你不會再看第二次的搜尋結果、log、檔案內容，就該交給 subagent，讓它在自己的 context 裡做完，只把摘要帶回來；如果你發現自己一直在重複派同一種工人、給同一套指示，就該把它定義成一個可重複使用的自訂 subagent。

官方列出四個具體好處[1]：

- **保留 context**：把探索與實作留在自己的視窗，不進主對話
- **強制邊界**：限制某個 subagent 能用哪些工具
- **重複使用**：使用者層 subagent 可以跨專案共用
- **專門化行為**：針對特定領域寫聚焦的 system prompt

反過來，什麼時候不該用 subagent，[Hooks 與 Subagent 設定](hooks-subagents.md)第三節已經整理過官方的說法（需要頻繁來回微調、多階段共用大量 context 的任務不適合），這裡不重複。

!!! note "Subagent 只在一個 session 內生效"
    官方原文提醒範圍邊界：「Subagents work within a single session. To run many independent sessions in parallel and monitor them from one place, see background agents. For separate sessions that pass messages to each other, see cross-session messaging. For a coordinated team of sessions Claude spawns and supervises, see agent teams.」[1] 這頁只談「同一個 session 裡的 subagent」；agent view（`claude agents`）、agent teams、跨 session 傳訊是另外三個機制，本頁第 8 節簡單帶過，不是本頁重點。

## 2. 內建 agent

Claude Code 內建幾種不用自己寫定義檔的 agent[1]：

| 內建 agent | 模型 | 定位 |
|---|---|---|
| `Explore` | 繼承主對話的模型，在 Claude API 上最高只到 Opus | 唯讀，跳過 CLAUDE.md 與 git status 以維持輕量，用於檔案發現與程式碼搜尋 |
| `Plan` | 依[模型解析順序](#4-fable) | 唯讀，用於 plan mode 下的程式庫研究 |
| `general-purpose` | 同上 | 所有 subagent 可用工具都開，用於需要探索＋修改、複雜推理、多步驟依賴的任務 |
| `claude` | 同上 | 無法歸類到專門 agent 時的萬用選項，所有 subagent 可用工具都開；也是[背景 session](#8-agent-viewagent-teams-dynamic-workflows) 被派工時的預設 agent |
| `statusline-setup` | Sonnet | 設定 status line |
| `claude-code-guide` | Haiku | 回答 Claude Code 功能問題 |

內建 subagent 在互動 session 裡預設就註冊好，要限制它們[1]：

- 擋掉特定內建類型：把它加進 `permissions.deny`
- 完全不讓 Claude 委派給任何 subagent：直接擋 `Agent` 這個工具本身
- 只想拿掉 `Explore`／`Plan`：設環境變數 `CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS=1`（v2.1.198 起），Claude 會改成自己直接讀檔探索
- Agent SDK／非互動模式想拿掉全部內建類型、只用自己的：設 `CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS=1`

## 3. 自訂 agent：frontmatter 全欄位

`.claude/agents/*.md`（專案層）或 `~/.claude/agents/*.md`（使用者層）放一個 Markdown 檔，YAML frontmatter 只有 `name` 與 `description` 必填，官方文件實際列出的完整欄位如下[1]：

| 欄位 | 必填 | 語意 |
|---|---|---|
| `name` | 是 | 小寫字母＋連字號；不能含 `:`（保留給 plugin 範圍識別符如 `my-plugin:reviewer`）；Hook 收到這個值時欄位名是 `agent_type` |
| `description` | 是 | 決定 Claude 何時該委派給這個 subagent |
| `tools` | 否 | 允許工具的白名單；省略則繼承所有 subagent 可用工具；清單裡沒有任何一項解析得出實際工具時，subagent 通常直接拒絕啟動並報錯 |
| `disallowedTools` | 否 | 黑名單，從繼承或指定的清單裡移除；`Bash(git push *)` 這種帶條件的寫法會整個工具一起移除，不是只擋那個條件 |
| `model` | 否 | `sonnet`／`opus`／`haiku`／`fable`／完整 model ID（如 `claude-opus-5`）／`inherit`；省略則依[模型解析順序](#4-fable)決定 |
| `permissionMode` | 否 | `default`／`acceptEdits`／`auto`／`dontAsk`／`bypassPermissions`／`plan`／`manual`（`manual` 是 `default` 的別名，v2.1.200 起）；plugin 提供的 subagent 忽略這個欄位 |
| `maxTurns` | 否 | 最多跑幾個 agentic turn；到上限時輸出會標記為 partial，可以用 `SendMessage`[續問](#7-sendmessage)繼續 |
| `skills` | 否 | 啟動時預先載進 context 的 skill 清單 |
| `mcpServers` | 否 | 這個 subagent 可用的 MCP servers |
| `hooks` | 否 | 只在這個 subagent 生效範圍的額外 hooks |
| `memory` | 否 | 持久記憶範圍：`user`／`project`／`local` |
| `isolation` | 否 | 設 `worktree` 讓 subagent 跑在獨立 git worktree，細節見[第 6 節](#6-background-isolation-worktree) |
| `background` | 否 | 設 `true` 讓這個 subagent 即使 Claude 想立刻拿結果也留在背景執行；細節見[第 6 節](#6-background-isolation-worktree) |
| `omitClaudeMd` | 否 | 設 `true` 啟動時不載入使用者／專案／本機層的 CLAUDE.md（managed policy 檔仍會載入）；當這個 agent 被當成主線 session agent 執行（`--agent` 或 `agent` 設定）時，這個欄位會被忽略 |
| `effort` | 否 | 這個 subagent 啟用時的推理強度：`low`／`medium`／`high`／`xhigh`／`max`，覆蓋 session 的 effort 設定，預設繼承 session；可用等級依模型而定 |
| `color` | 否 | 顯示用顏色 |
| `initialPrompt` | 否 | 這個 agent 被當成主線 session agent 執行時，自動當作第一則使用者訊息送出，會被前置在使用者實際輸入的提示之前；會經過 command／skill 處理 |
| `experimental` | 否 | 實驗性選項的 map；目前唯一有效的鍵是 `cacheTtl`（`5m` 或 `1h`），決定這個 subagent 請求的 prompt cache 存活時間，只從 subagent 定義檔讀取這個欄位 |

`--agents` CLI 旗標接受 JSON，每個 agent 除了 `prompt`（對應 Markdown 檔的內文部分，等同 system prompt），只支援上表其中 15 個欄位：`description`、`tools`、`disallowedTools`、`model`、`permissionMode`、`mcpServers`、`hooks`、`maxTurns`、`skills`、`initialPrompt`、`memory`、`effort`、`background`、`omitClaudeMd`、`isolation`；`color` 與 `experimental` 只能寫在定義檔裡[1]。

!!! tip "`tools` 與 `disallowedTools` 同時設定時"
    官方原文：「If both are set, `disallowedTools` is applied first, then `tools` is resolved against the remaining pool. A tool listed in both is removed.」[1] 兩個欄位都接受 MCP server 層級的萬用寫法，`mcp__<server>` 或 `mcp__<server>__*` 代表整台伺服器的所有工具；`disallowedTools` 裡的 `mcp__*` 則會移除所有 MCP 工具。

!!! warning "frontmatter 寫錯會被靜默跳過，不是報錯給你看"
    `name` 以 `-` 開頭或含 `:`、有 `name` 沒 `description`、YAML 解析不出來，這三種情況 Claude Code 都是把整個檔案跳過、只寫進 debug log，不會在對話裡提醒你這個 subagent 沒生效。跑 `claude --debug` 才看得到；也可以先跑 `claude plugin validate` 對著 `.claude/agents` 或 `~/.claude/agents` 檢查[1]。

## 4. 模型怎麼選：`fable` 是什麼、解析順序

官方文件目前列出的 model alias 是 `sonnet`、`opus`、`haiku`、`fable` 四種，另外也接受完整 model ID 或 `inherit`[1]。官方文件對 `fable` 本身沒有進一步說明是什麼模型、定位是什麼。這裡只如實轉述欄位表裡列了這個值，不臆測。

Claude 呼叫 subagent 時，實際套用的模型依這個順序解析（由高到低）[1]：

1. 這次派工當下傳入的 `model` 參數
2. subagent 定義檔的 `model` frontmatter（`inherit` 代表用主線目前的模型）
3. `CLAUDE_CODE_SUBAGENT_MODEL` 環境變數（設成 model alias 或 model ID 時才生效）
4. 主線對話目前的模型

`CLAUDE_CODE_SUBAGENT_MODEL` 只是預設值，subagent 定義檔或派工當下傳的參數仍然優先。要讓每個 subagent（含內建的 Explore／Plan、teammate、workflow agent）都強制套用同一個模型，要另外設 `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1`（v2.1.257 起）；開啟後 Claude 連派工時都不能再指定模型，只有 fork、以及設了 `model: inherit` 的 skill-in-subagent 例外[1]。

## 5. 工具怎麼被過濾

Subagent 繼承主線對話可用的內建工具與 MCP 工具，但會經過兩層過濾[1]：

**第一層，不管 `tools` 欄位寫了什麼都會被拿掉的工具**：`Agent`（在委派深度已到上限時；fork 裡這個工具會保留在清單但實際呼叫會回錯誤）、`AskUserQuestion`、`EndConversation`、`EnterPlanMode`、`ExitPlanMode`（除非該 subagent 的 `permissionMode` 是 `plan`）、`ScheduleWakeup`、`TaskOutput`、`WaitForMcpServers`、`Workflow`。

**第二層只套用在背景執行的 subagent 身上**（背景是[預設值](#6-background-isolation-worktree)）。除了跟著第一層規則走的 `Agent` 與 `ExitPlanMode`，背景 subagent 只保留這些內建工具：`Read`、`Grep`、`Glob`、`Bash`、`PowerShell`、`Edit`、`Write`、`NotebookEdit`、`WebFetch`、`WebSearch`、`TodoWrite`、`Skill`、`ToolSearch`、`EnterWorktree`、`ExitWorktree`、`Monitor`、`TaskStop`、`SendMessage`、`Artifact`，加上要回報用的 `SubagentHandback`；MCP 工具則全部保留。其餘內建工具，就算寫在 `tools` 欄位裡也一樣被拿掉，同一份定義檔在前景跟背景會解析出不同的工具集，這個移除動作不會報錯，除非移除後 `tools` 清單完全解析不出任何工具[1]。

fork 會跳過這兩層過濾，直接拿到主線對話一模一樣的工具池[1]。

## 6. `background` 與 `isolation: worktree` 的實際行為

### background：subagent 到底在前景還是背景跑

官方原文定義兩者的差別：「Foreground subagents block the main conversation until complete. Permission prompts are passed through to you as they come up. Background subagents run concurrently while you continue working.」背景 subagent 遇到需要核准的工具呼叫時，會把提示浮到你的主 session 上並標明是哪個 subagent 在問；核准就讓它繼續，按 Esc 只拒絕那一次工具呼叫，不會連帶停掉整個 subagent[1]。

Claude 用 Agent 工具派 subagent 時，會依序檢查以下條件決定前景還是背景[1]：

1. 如果是某個 agent team teammate（in-process）自己派出的 subagent，一律跑前景；teammate 的定義檔若設了 `background: true` 會直接被拒絕派工
2. 你設了 `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`，一律跑前景
3. **fork mode 開啟時**（互動 session 預設就是開的）：一律跑背景，Claude 沒辦法要求前景
4. fork mode 關閉時：預設背景，只有 Claude 需要立刻拿到結果才跑前景；要讓某個 subagent 即使 Claude 想要結果也留在背景，就在它的 frontmatter 設 `background: true`

背景 subagent 的結果是以「完成通知」的形式，在之後的某一輪送回主線；如果你這時候問進度，Claude 只能回報「還在跑」，不能編造結果（v2.1.211 前偶爾會誤報未完成的結果）[1]。背景 subagent 可以在自己的回合結束後仍讓一個背景 Bash／PowerShell 指令繼續跑，指令結束時會收到通知[1]。

### isolation: worktree：怎麼真的擋住越界的指令

官方原文：「A subagent starts in the main conversation's current working directory... To give the subagent an isolated copy of the repository instead, set `isolation: worktree`.」[1] 設了之後，它的 Bash／PowerShell 指令都會被限制跑在自己的 worktree 裡：如果指令的工作目錄解析結果落到主 checkout（例如 worktree 目錄在 subagent 跑到一半時被刪掉），指令會直接失敗回錯誤，不是靜默放行（v2.1.203 前不會擋）[1]。

這個檢查涵蓋整個「你啟動 Claude Code 那個目錄所在的 repository」；如果你自己的 session 本身就跑在一個 linked worktree 裡，檢查範圍還會包含那個 worktree 連回去的主 checkout（v2.1.210 前只檢查啟動目錄本身）。針對 Bash 指令，Claude Code 另外檢查指令內容本身：擋掉會把 git 重導向到主 checkout 的指令，也會拒絕它無法從指令文字判斷出「裡面呼叫的 git 是否留在 worktree 內」的指令（例如指令名稱是執行時才算出來的）。PowerShell 只做工作目錄檢查，`Monitor` 工具走跟 Bash 一樣的雙重檢查[1]。worktree 用完會自動清掉，前提是 subagent 沒有做出任何改動（frontmatter 欄位表原文：「The worktree is automatically cleaned up if the subagent makes no changes」）[1]。

當主線對話自己就跑在一個 worktree 裡時，這套檢查同時套用在 session 本身和它派出的每一個 subagent，包括沒設 `isolation: worktree` 的[1]。

## 7. SendMessage 續問

官方工具參考裡對 `SendMessage` 的定義：「Sends a message to another agent: an agent team teammate, a subagent it resumes by agent ID or name, or one of your other Claude Code sessions, on this machine or beyond it.」[6] 續問一個已經跑完的 subagent，不需要重新開一次 Agent 呼叫：「When Claude sends a completed subagent a message with the `SendMessage` tool, the subagent resumes in the background without a new `Agent` invocation... The resumed run keeps the tool set from where the subagent first ran and can keep reading the prompt cache the original run warmed.」[1] 也就是說，續問時 subagent 沿用它第一次跑的時候是前景還是背景所決定的工具集，而且還能繼續吃到原本那次跑暖的 prompt cache，不是從零開始。

`SendMessage` 本身不需要開啟 agent teams 才能用，只有 `shutdown_request`、`plan_approval_response` 這種結構化的 team-protocol 訊息才需要[1]。一個有 `SendMessage` 工具的 subagent 自己也能發訊息續問別的 agent；在互動 session 裡，被續問的 agent 完成後會回報給續問它的那個 subagent，不是直接跳回你的主對話，續問的一方會等結果才結束自己的工作[1]。

subagent 要看到誰可以被 `SendMessage` 到，靠的是啟動時附帶的「sibling roster」（一則系統提醒，列出 `main` 跟這個 session 裡每一個有名字的 agent）。這則提醒只在該 subagent 的工具清單裡有 `SendMessage`、且至少有另一個 agent 已經有名字時才會出現，而且是啟動當下的快照，之後才取名的 agent 不會補進去（v2.1.206 起）[1]。

!!! note "同名保護"
    v2.1.199 起，`SendMessage` 會檢查一個名字現在是不是仍指向它先前接觸過的同一個 agent。如果有個新 agent 重用了舊名字（例如重新派的背景 agent 剛好取了一樣的名字），Claude Code 會拒絕送出而不是送錯對象，並且在錯誤裡告訴 Claude 這個名字現在指向誰，讓它改用當初拿到的 agent ID 重新定位。這個檢查只在目前這個對話裡有效，`/clear` 之後會重置[1]。

## 8. 其他多代理機制：agent view、agent teams 與 dynamic workflows

Subagent 只是 Claude Code 五種「同時處理多件事」的做法之一，官方對照表如下（翻譯自原文）[2]：

| 做法 | 給你什麼 | 什麼時候用 |
|---|---|---|
| Subagent | 一個 session 內委派的工人，在自己的 context 做側支任務，只回傳摘要 | 側支任務會把主對話塞滿你不會再看的搜尋結果、log、檔案內容 |
| Agent view（`claude agents`，研究預覽） | 一個畫面派工並監控多個跑在背景的 session | 有好幾個獨立任務要交出去，只想大致看狀態、需要時才介入 |
| Agent teams（實驗性，預設關閉） | 多個協調中的 session，共用任務清單與代理間訊息，由一個 lead 管理 | 想讓 Claude 把一個專案拆成幾塊、分派、並讓工人保持同步 |
| Projects（claude.ai/code 或桌面版，Pro／Max 公開 beta） | 一個持續進行的對話，Claude 自己開好幾條雲端平行 thread | 工作橫跨好幾天到幾週，希望電腦關機也繼續跑，只想講一次目標 |
| Dynamic workflows | 一支跑很多 subagent、互相交叉核對結果的腳本，處理一次對話輪不完的工作 | 任務大到超出手動協調的規模，或想要多方交叉驗證的結果 |

每一種底層的工人都是 Claude session；要接別的工具，一律透過 [MCP server](mcp.md)[2]。

### Workflow 工具與 dynamic workflows

Dynamic workflow 是一支由 Claude 寫出來、在背景由 runtime 執行的 JavaScript 腳本，一次協調多個 subagent，適合「單一對話輪協調不完」或「想把協調過程寫成可重跑的腳本」的任務，例如全庫規模的 bug 排查、500 個檔案的搬遷、需要互相核對來源的研究問題、或值得從多個角度分別起草再比較的高風險計畫[3]。

跟 subagent／skill／agent team 最本質的差異是「誰握著計畫」：subagent 跟 agent team 是 Claude（或 lead agent）逐輪決定下一步做什麼，中間結果留在 context window 裡；workflow 是把整個迴圈、分支邏輯、中間結果都搬進腳本本身，Claude 的 context 只看得到最終答案[3]。

內建的 `/deep-research` 就是一個現成的 workflow，會針對一個問題從多個角度平行搜尋、交叉核對來源、對每個論點投票，回傳一份已經濾掉沒通過交叉核對的引用報告[3]。要臨時把單一任務跑成 workflow，在提示裡加關鍵字 `ultracode`，或者直接用自己的話講「用 workflow 做」也算數；`/effort ultracode` 則是讓 Claude 對整個 session 裡每個像樣的任務都自動規劃 workflow[3]。

跑 workflow 前 Claude Code 通常會先問是否放行，這個提示會依權限模式而不同；在 `claude -p` 與 Agent SDK 裡完全不會跳出這個提示，改用一般的權限規則決定，其中最直接的是在 allow 規則裡放 `Workflow`（放行所有 workflow）或 `Workflow(<name>)`（只放行某個已存檔的 workflow）[3]。跑起來的 workflow 可以用 `/workflows` 監看每個階段的 agent 數、token 用量與經過時間[3]。這也是為什麼[第 5 節](#5)提到 `Workflow` 本身被第一層過濾器整批拿掉：subagent 不能自己再派一個 workflow。

!!! note "併發上限"
    一個 session 裡同時跑滿 20 個 subagent 時，再用 Agent 工具派下一個會直接失敗、報 `Concurrent subagent limit reached`，Claude 收到的錯誤訊息會註明不要重試；等執行中的數量降到門檻以下才能再派。要調整這個上限，設環境變數 `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`。啟用 ultracode 的 session 不受這個限制[1]。

## 9. 成本：三層倍數，不能互換引用

官方分析自家多代理研究系統時給過一個常被引用的數字，逐字如下：「In our data, agents typically use about 4× more tokens than chat interactions, and multi-agent systems use about 15× more tokens than chats.」[5] 也就是「一般聊天」對「單一 agent」對「多代理系統」，是 1 倍、約 4 倍、約 15 倍。15 倍的比較基準是一般聊天，不是單一 agent。

另一個常被搞混的數字來自完全不同的文件，官方原文：「Agent teams use approximately 7x more tokens than standard sessions when teammates run in plan mode, because each teammate maintains its own context window and runs as a separate Claude instance.」[4] 這個 7 倍限定在「teammate 跑 plan mode」這個情境，比較基準是標準 session，跟前面的 15 倍是兩篇不同文件、兩個不同系統、不同比較基準，**不可互換引用**。[把 AI 代理的工作環境設計得可靠](harness.md)第五節點出過同一組 4 倍／15 倍數字，這裡補上 agent teams 那個獨立的 7 倍，並且明講兩者不能混為一談。

官方給的省 token 建議跟這組倍數是同一個脈絡，摘要幾條跟 subagent 直接相關的[4]：

- 機械型 subagent 指定 `model: haiku`，架構決策才留給 Opus
- 把跑測試、抓文件、處理 log 這類冗長操作丟給 subagent，讓完整輸出留在 subagent 的 context，只帶摘要回主線
- agent team 要用 Sonnet 當 teammate、團隊人數盡量小、派工提示聚焦、工作做完就關掉 teammate

## 10. Codex 的對應設定

Codex 的 subagent 定義放在 TOML 檔：`~/.codex/agents/`（個人層）或 `.codex/agents/`（專案層），每個檔案定義一個自訂 agent。必填三個欄位：`name`、`description`、`developer_instructions`；也可以在同一個檔案裡帶其他 `config.toml` 支援的鍵，例如 `model`、`model_reasoning_effort`、`sandbox_mode`、`mcp_servers`、`skills.config`，省略的設定會從父層繼承[7]。

```toml
name = "pr_explorer"
description = "Read-only codebase explorer for gathering evidence before changes are proposed."
model = "gpt-5.6-luna"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = """
Stay in exploration mode.
Trace the real execution path, cite files and symbols, and avoid proposing fixes unless the parent agent asks for them.
Prefer fast search and targeted file reads over broad scans.
"""
```

Codex 內建三種現成 agent：`default`（萬用備援）、`worker`（專注實作與修復）、`explorer`（偏重程式庫探索的唯讀 agent）。自訂 agent 的檔名不一定要跟 `name` 欄位一致，但 `name` 才是真正的識別依據；如果自訂 agent 的名字跟內建 agent 撞名，自訂的優先[7]。

全域設定放在 `config.toml` 的 `[agents]` 區塊[7]：

| 欄位 | 型別 | 用途 |
|---|---|---|
| `agents.enabled` | boolean | 開關多代理工具，預設 `true` |
| `agents.max_concurrent_threads_per_session` | number | 限制同時開啟的派工執行緒數量（不含主 session）；舊版可用 `agents.max_threads` 這個別名 |
| `agents.default_subagent_model` | string | 派工預設模型 |
| `agents.default_subagent_reasoning_effort` | string | 派工預設推理強度 |
| `agents.interrupt_message` | boolean | agent 的回合被中斷時，要不要在它的 context 留一則模型看得到的中斷訊息，預設 `true` |

`model`／`model_reasoning_effort` 這兩項如果自訂 agent 檔案自己設定了，優先於派工當下傳入的值、`[agents]` 的預設值、跟父層 session 的值。Codex 的解析順序反過來是「檔案優先」，跟 Claude Code「派工參數優先於定義檔」剛好相反，這點在比較兩邊設計時容易搞混，這裡特別點出來[7]。

## 常見誤用

- **以為 `background: true` 只是換個執行位置，不影響工具**：第 5 節的第二層過濾器是實打實砍工具，同一份定義檔前景跑得動的工具，背景不一定跑得動；派工前若依賴某個內建工具（例如 `TodoWrite` 以外的規劃類工具），先查一遍它是否在背景保留清單裡。
- **把「多代理 15 倍」跟「agent team 7 倍」當同一件事引用**：第 9 節已經講過，比較基準跟系統都不同，官方沒有講過兩者可以互換。
- **拿 subagent 處理需要頻繁來回微調的任務**：[Hooks 與 Subagent 設定](hooks-subagents.md)已經提過，subagent 預設從零 context 開始，來回討論的成本比留在主線更高。
- **以為 `isolation: worktree` 只是「換個目錄」**：第 6 節列的雙重檢查（工作目錄＋指令內容）是真的會擋下指令並回錯誤，不是可有可無的建議性隔離。
- **忘記 workflow 是另一條路，不是 subagent 的加強版**：workflow 把計畫搬進腳本，跟 Claude 逐輪決定是不同的協調方式，規模到「一次對話輪協調不完」才值得換路，不是任務稍微複雜就該換。

## 資料來源

| 標記 | 來源 | URL |
|---|---|---|
| [1] | Create custom subagents | <https://code.claude.com/docs/en/sub-agents> |
| [2] | Run agents in parallel | <https://code.claude.com/docs/en/agents> |
| [3] | Orchestrate subagents at scale with dynamic workflows | <https://code.claude.com/docs/en/workflows> |
| [4] | Costs（Reduce token usage、Agent team token costs） | <https://code.claude.com/docs/en/costs> |
| [5] | How we built our multi-agent research system | <https://www.anthropic.com/engineering/multi-agent-research-system> |
| [6] | Tools reference（`SendMessage`／`ListAgents`） | <https://code.claude.com/docs/en/tools-reference> |
| [7] | Subagents（Codex） | <https://learn.chatgpt.com/docs/agent-configuration/subagents> |

延伸：[SKILL、Plugin、MCP 與 Subagent](extensions.md)｜[Hooks 與 Subagent 設定](hooks-subagents.md)｜[把 AI 代理的工作環境設計得可靠](harness.md)｜[AI Agent 怎麼運作](agent-basics.md)
