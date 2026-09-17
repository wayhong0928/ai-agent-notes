# 跨 session 接力：session_log

> 查證日期：2026-09-16。方案與功能變動快，請以官方最新說明為準。

[AI Agent 怎麼運作](agent-basics.md)第二節講過，上下文視窗會滿，滿了之後 Claude Code 會自動壓縮或忘記較早的細節。這頁講的是同一個問題的另一面：**一個對話（session）結束之後，下一個對話怎麼知道上次做到哪裡**。這是官方機制（`SessionStart` hook）加上使用者自己設計的紀律（怎麼寫這個 log、什麼時候補）合起來解決的問題，兩者要分開看，這頁會逐段標明哪部分是官方保證、哪部分是整理者自己的做法。

## 一、問題是什麼

長期用一個代理型工具做同一個專案，會遇到兩種情況：

1. 一次對話因為上下文滿了、你自己關掉、或工具重啟而結束，下一次開新對話時，模型完全不記得上一次做到哪、決定了什麼、還剩什麼沒做。
2. 就算同一個對話還開著，官方文件也建議在「不相關的兩個任務之間」用 `/clear` 主動重置上下文，理由是舊的失敗嘗試會污染後續判斷[2]——但重置之後一樣要面對「這個新對話怎麼接得上進度」的問題。

如果每次都要重新跟模型解釋一遍「這個專案在做什麼、上次做到哪、還有什麼要做」，等於每次都要重講一次，這正是 CLAUDE.md 想省下來的那種重複解釋，只是對象換成了「進度」而不是「事實」。

## 二、官方機制：`SessionStart` hook

Claude Code 的 Hooks 系統裡有一個 `SessionStart` 事件，會在**每個 session 開始或恢復時**觸發，`matcher` 可以進一步分辨這次啟動的來源：`startup`（全新啟動）、`resume`（接續之前的對話）、`clear`（`/clear` 之後）、`compact`（自動壓縮之後）、`fork`[1]。

這個事件有一個特別的地方：多數 hook 事件的 plain-text stdout 只會寫進除錯 log，模型看不到；但 `SessionStart`（連同 `UserPromptSubmit`、`UserPromptExpansion`、`PostModelSwitch`，共四個事件）是例外，**它的 plain-text stdout 會被當成上下文加進去，模型看得到也能據此行動**[1]。也可以用 JSON 輸出的 `hookSpecificOutput.additionalContext` 欄位達到同樣效果，寫法更明確：

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "這裡放要注入的文字"
  }
}
```

`hookEventName` 是必填欄位，值要對應觸發這支 hook 的事件名稱（這裡是 `SessionStart`）；漏了這個欄位，官方範例的行為不保證成立。

用一個最小範例串起來，`.claude/settings.json` 裡註冊一支腳本，session 啟動時執行：

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/inject-log.sh"
          }
        ]
      }
    ]
  }
}
```

腳本本身只要把想給模型看的文字印到 stdout 就會被接住，不需要額外處理 JSON：

```bash
#!/bin/bash
# inject-log.sh —— 印出 session_log 最新幾筆，SessionStart 會把這段 stdout 當成上下文
echo "=== 上次進度（session_log.md 最新 3 筆） ==="
awk '/^## /{c++} c<=3' "$CLAUDE_PROJECT_DIR/session_log.md"
```

到這裡為止，`SessionStart` 事件本身、它能分辨的觸發來源、stdout 會被當成上下文這三件事，都是官方 Hooks reference 直接記載的機制[1]。機制本身**不規定**你要注入什麼內容——那是下一節要講的部分。

## 三、整理者做法：`session_log.md` 怎麼寫

以下是本站整理者自己設計、用來配合上面那個官方機制的一套紀律，**不是官方建議的固定格式**，Claude Code 官方文件並沒有規定「進度紀錄該長什麼樣子」。這裡示範的是一種可行的做法，不是唯一做法；路徑與專案名稱全部是虛構的示例。

### 檔案放哪、長什麼樣

在專案根目錄放一個 `session_log.md`，最新的一筆永遠寫在檔案**頂部**，方便 hook 腳本只抓前幾筆而不用讀完整個檔案：

```markdown
# session_log.md

## 2026-09-15 完成資料清理腳本
- 寫好 `scripts/clean_data.py`，跑過一次 `data/raw/2026Q3.csv`，輸出到 `data/clean/`
- 待辦：清理後的欄位命名還沒跟報告樣板對齊，下次先做這個

## 2026-09-12 專案啟動
- 建立資料夾結構：`data/raw/`、`data/clean/`、`scripts/`
- 確認原始資料來源與欄位定義
```

### 三個動作串起整個循環

1. **開場**：Claude 看到 `SessionStart` 注入的內容之後，先用一到兩句話跟你確認「上次做到哪、這次要接著做什麼」，再開始處理新指令。這一步值得寫進專案的 CLAUDE.md，作為固定要求，例如：「開場先用 1–2 句話報告上次進度，再處理指令」——這句提醒本身放在 CLAUDE.md 裡，就只是 advisory（模型可能因為上下文太滿而忘記遵守），如果想要它保證發生，要靠更強的機制，例如在 `UserPromptSubmit` 上再掛一個檢查[3]。
2. **工作中**：正常做事，不用每一步都寫 log。
3. **收尾**：每次完成一件「有意義的工作」（一個功能、一次修復、一個決策），就在 `session_log.md` **頂部**補一筆，而不是等到整個對話結束才一次補完——對話可能因為上下文滿了而被自動壓縮，官方原文對自動壓縮的描述是「preserves important code and decisions while freeing space」，觸發時「Claude summarizes what matters most, including code patterns, file states, and key decisions」[2]，講的是摘要保留重點，不是東西會不見；但只存在對話裡、沒寫進 `session_log.md` 的進度細節，一旦被摘要掉就無法從摘要精確重建，這是整理者自己的推論提醒，不是官方文件的說法。

### 為什麼要放在頂部、而不是尾端

`SessionStart` 注入的內容也會佔用新 session 的上下文，如果 `session_log.md` 越寫越長，`hook` 腳本又抓整個檔案，等於每次開新對話就先吃掉一大段上下文。把最新進度放在頂部，hook 腳本只抓前幾筆（例如前 3 筆），檔案本身可以無限累積歷史記錄，但每次真正注入的量是固定的一小段——這是配合[把 AI 代理的工作環境設計得可靠](harness.md)裡「說明檔太長，重要規則反而會被忽略」這條原則做的設計選擇，不是官方對 `session_log.md` 格式的要求，因為官方根本沒有這個檔案的格式規定。

## 四、這個機制解決了什麼、沒解決什麼

解決了：下一個 session 開場就知道「上次做到哪」，不用你自己重講一遍，也不用模型憑空猜。

沒解決：如果某一輪工作做完卻忘記補 `session_log.md`，這個機制不會自動幫你記得——`SessionStart` 只保證「session 開始時會注入某段內容」，內容夠不夠新、夠不夠準，取決於你有沒有紀律地在收尾時更新它。想把「必須補一筆」也變成機制保證而非自覺遵守，理論上可以在 `Stop` hook 上加一道檢查（比對本回合有沒有寫檔動作、`session_log.md` 的 mtime 有沒有更新），但這已經超出「注入進度」這件事本身，屬於進一步的自動化設計，本頁不展開。

## 本頁重點回顧

- 問題：上下文有限、對話會中斷或被主動 `/clear`，下一個 session 預設不知道上次做到哪。
- 官方機制：`SessionStart` hook 在 session 開始或恢復時觸發，能分辨 `startup`／`resume`／`clear`／`compact`／`fork` 來源，且是少數 stdout 會被當成上下文注入的事件之一。
- 整理者做法（非官方規定）：進度記在 `session_log.md` 頂部、hook 腳本只抓最新幾筆、開場報告進度、收尾即時補記——這套紀律是為了配合官方機制、同時避免說明檔越養越大而設計的，不是 Claude Code 文件裡寫的標準做法。
- 這個機制解決「不用重講進度」，不解決「有沒有紀律去記」；後者要嘛靠自覺，要嘛再疊加一層機制去檢查。

## 資料來源

| 標記 | 來源 | URL |
|---|---|---|
| [1] | Hooks reference（`SessionStart` 事件、`matcher` 的來源分類、stdout 注入上下文的例外規則、`additionalContext` 欄位、`CLAUDE_PROJECT_DIR`） | <https://code.claude.com/docs/en/hooks> |
| [2] | Best practices for Claude Code（`/clear` 的使用時機、上下文被壓縮時可能遺失的內容） | <https://code.claude.com/docs/en/best-practices> |
| [3] | Best practices for Claude Code（hooks 是 deterministic、CLAUDE.md 指示是 advisory） | <https://code.claude.com/docs/en/best-practices> |

延伸：[AI Agent 怎麼運作](agent-basics.md)｜[Hooks 與 Subagent 設定](hooks-subagents.md)｜[把 AI 代理的工作環境設計得可靠](harness.md)
