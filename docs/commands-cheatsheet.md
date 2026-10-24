# 新手指令速查

> 查證日期：2026-10-24。指令常隨版本增減，請以官方最新說明為準。

Claude Code 的斜線指令很多，新手不需要全記。這頁照「現在想做什麼」分組，只挑最常用的，並把 `/model`、`/effort`、`/compact` 這幾個影響效果與用量的指令講清楚。完整清單以官方文件為準[1]。

在輸入框打 `/` 會跳出選單，可以邊打邊篩。指令只有放在訊息開頭才會被辨識[1]。

## 一、第一次用

| 指令 | 做什麼 |
|---|---|
| `/init` | 替專案產生起始的 CLAUDE.md |
| `/memory` | 查看與編輯 CLAUDE.md 和 auto memory |
| `/mcp` | 管理 MCP 伺服器的連線 |
| `/permissions` | 設定允許、詢問、拒絕哪些工具動作（別名 `/allowed-tools`） |
| `/config` | 開設定介面（別名 `/settings`） |

設定檔與 CLAUDE.md 的載入規則見[Claude Code 設定總覽](official-config.md)。

## 二、做事的過程中

| 指令 | 做什麼 |
|---|---|
| `/plan` | 進入規劃模式，先討論做法再動手 |
| `/model` | 換模型，見下一節 |
| `/effort` | 調整思考力度，見下一節 |
| `/context` | 看目前 context 的用量與分類；全螢幕模式下加 `all` 會展開收合的明細 |
| `/compact` | 把到目前為止的對話壓成摘要，騰出 context 空間 |
| `/btw` | 順口問一個旁支問題 |

官方把這六個歸在「During a task」[1]。

## 三、`/model`：換模型

跑 `/model` 不帶參數會開選單。選單裡按 `Enter` 會把這個模型存成之後新 session 的預設，按 `s` 則只換目前這個 session。`/model <名稱>` 的效果等同於按 `Enter`[1][2]。

模型別名有 `default`、`best`、`fable`、`sonnet`、`opus`、`haiku`、`sonnet[1m]`、`opus[1m]`、`opusplan`。在 Anthropic API 上，`opus` 指向 Opus 5.5，`sonnet` 指向 Sonnet 5.5，`haiku` 指向 Haiku 5.5[2]。

同一件事有好幾個地方可以設，官方列的優先順序由高到低是[2]。

1. session 中跑 `/model`
2. 啟動時加 `claude --model`
3. 環境變數 `ANTHROPIC_MODEL`
4. 設定檔
5. 環境變數 `ANTHROPIC_DEFAULT_MODEL`

想確認現在用的是哪個模型，跑 `/status`[2]。

## 四、`/effort`：調思考力度

Effort 控制 Claude 回答前想多深。等級由低到高是 `low`、`medium`、`high`、`xhigh`、`max`，也可以用 `auto` 清掉已存的設定[1][2]。`max` 只在目前的 session 有效，用環境變數 `CLAUDE_CODE_EFFORT_LEVEL` 設定的除外[1][2]。

預設是 `high`，但 Opus 5.5、Sonnet 5.5 和 Haiku 5.5 的預設是 `medium`，Opus 4.7 是 `xhigh`；組織也可以另設預設值[2]。

官方的選擇建議如下[2]。

| 等級 | 適合 |
|---|---|
| `low` | 簡短的來回，或像改名這樣的小修改 |
| `medium` | 範圍清楚的日常工作 |
| `high` | 正確性重要的任務，或修 bug |
| `xhigh` | 需要更深的推理，代價是更多 token |
| `max` | 很難的問題。官方提醒可能報酬遞減，也容易想太多 |

設定的來源有三個，優先順序是明確指定（環境變數 `CLAUDE_CODE_EFFORT_LEVEL`、`--effort`、`/effort`）、設定檔、模型預設[2]。只想讓單一回合想深一點，可以在 prompt 裡寫 `ultrathink`[2]。目前的 effort 會顯示在 session 的標頭，`/effort status` 也能查[1][2]。

## 五、`/compact`：壓縮對話

跑 `/compact` 會把對話摘要成較短的版本，騰出 context。可以加一段指示決定摘要的重點，例如 `/compact focus on the auth bug fix`[1][3]。

壓縮之後哪些內容還在、哪些會消失，見[Claude Code 設定總覽](official-config.md)的「壓縮之後哪些還在」。想知道現在用了多少 context，先跑 `/context`[3]。

`/compact` 和 `/clear` 不一樣。`/clear` 開一段全新的對話（別名 `/reset`、`/new`），想在同一段對話裡釋出空間，官方的建議是改用 `/compact`[1]。只想壓縮某一段，可以用 `/rewind` 選單裡的 Summarize 選項，見[Checkpoints 與 /rewind](checkpoints-rewind.md)。

## 六、同時跑多件事

| 指令 | 做什麼 |
|---|---|
| `/tasks` | 查看背景任務 |
| `/background` | 把目前的工作丟到背景 |
| `/batch` | 把一件大工作拆成多個平行的單元 |

這三個在官方分組裡屬於「Run work in parallel」[1]。

## 七、交付之前

| 指令 | 做什麼 |
|---|---|
| `/diff` | 看這次改了什麼 |
| `/code-review` | 審查目前的修改，也可以指定 PR 編號、分支或路徑（`/review` 是它的別名）[1] |
| `/security-review` | 針對目前分支的修改做安全審查 |

## 八、換 session、接續工作

| 指令 | 做什麼 |
|---|---|
| `/clear` | 清空對話，開始新的一段 |
| `/resume` | 接續先前的 session（別名 `/continue`） |
| `/branch` | 從目前的對話分出一條支線 |
| `/fork` | 另開一個分身接著做 |
| `/teleport` | 把雲端的 session 帶回本機 |
| `/remote-control` | 讓別的裝置遠端操控這個 session |

## 九、出狀況的時候

| 指令 | 做什麼 |
|---|---|
| `/rewind` | 退回之前的 checkpoint（別名 `/checkpoint`、`/undo`），見[Checkpoints 與 /rewind](checkpoints-rewind.md) |
| `/doctor` | 檢查安裝與設定有沒有問題 |
| `/debug` | 開除錯紀錄 |
| `/feedback` | 回報問題 |

## 本頁重點回顧

- 在輸入框打 `/` 看選單，指令要放在訊息開頭。
- 這頁依工作階段分成第一次用、做事過程、平行、交付前、換 session、出狀況六組，分法參考官方，`/config` 是本頁自己放進第一組的。
- `/model` 按 `Enter` 存成預設，按 `s` 只換這個 session。
- `/effort` 由 `low` 到 `max`，`max` 只在該 session 有效（環境變數設定的除外）；預設多數是 `high`，Opus 5.5、Sonnet 5.5、Haiku 5.5 是 `medium`。
- `/compact` 可以帶一段重點指示；`/context` 看用量；`/rewind` 退回 checkpoint。

## 資料來源

| 標記 | 來源 | URL |
|---|---|---|
| [1] | Commands（指令清單、分組與別名） | <https://code.claude.com/docs/en/commands> |
| [2] | Model configuration（模型別名、優先順序、effort） | <https://code.claude.com/docs/en/model-config> |
| [3] | Context window（`/context`、`/compact`） | <https://code.claude.com/docs/en/context-window> |

延伸：[Checkpoints 與 /rewind](checkpoints-rewind.md)｜[Claude Code 設定總覽](official-config.md)｜[跨 session 接力：session_log](session-handoff.md)
