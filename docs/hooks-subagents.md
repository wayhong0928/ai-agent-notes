# Hooks 與 Subagent 設定

> 查證日期：2026-09-16。方案與功能變動快，請以官方最新說明為準。

[SKILL、Plugin、MCP 與 Subagent](extensions.md)那頁把 Hooks 跟 Subagent 放進一張總表，講了它們各自解決什麼問題。這頁把兩者的實際設定方式攤開來講：事件有哪些、設定寫在哪個檔案、frontmatter 每個欄位實際的語意，以及一個可以直接照抄的最小範例。

## 一、Hooks：把「一定要發生」的事變成機制

### 事件清單

`settings.json` 的 `hooks` 底下可以掛的事件，依生命週期分組，官方 Hooks reference 目前列出約 33 種，這裡列常用的幾組[1]：

| 分組 | 事件 |
|---|---|
| 每個 session 一次 | `SessionStart`、`SessionEnd`、`Setup` |
| 每個回合 | `UserPromptSubmit`、`Stop`、`StopFailure` |
| 每次工具呼叫 | `PreToolUse`、`PostToolUse`、`PostToolUseFailure`、`PermissionRequest`、`PermissionDenied` |
| Agent 相關 | `SubagentStart`、`SubagentStop`、`TaskCreated`、`TaskCompleted` |
| 設定與環境 | `ConfigChange`、`FileChanged`、`CwdChanged`、`PreCompact`、`PostCompact` |

### 設定寫在哪裡、長什麼樣

Hooks 設定寫在 `settings.json`（使用者層 `~/.claude/settings.json` 或專案層 `.claude/settings.json`，見[Claude Code 設定總覽](official-config.md)的五層優先序）。`hooks` 是一個物件，key 是事件名稱，值是一個陣列，每個項目含 `matcher`（篩選何時觸發，可以是工具名、regex，或像 `SessionStart` 這種事件專屬的來源字串）與 `hooks`（真正要跑的處理器陣列）[1]。Handler 類型有五種：`command`（跑 shell 指令）、`http`（打 HTTP request）、`mcp_tool`（呼叫 MCP 工具）、`prompt`（送給 Claude 模型判斷）、`agent`（開一個 subagent）[1]。

### 官方範例：編輯完自動跑格式化

`code.claude.com/docs/en/hooks-guide` 的官方範例，`PostToolUse` 搭配 `Edit|Write` matcher，編輯完成後自動跑 Prettier：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
          }
        ]
      }
    ]
  }
}
```

這個範例可以直接照抄：把它貼進 `.claude/settings.json`，前提是專案已經裝了 `prettier` 且 `jq` 在 PATH 裡。想擋掉某個動作而不是事後處理，改用 `PreToolUse` 並讓腳本以 `exit 2` 結束——**`exit 2` 是唯一保證阻擋該動作的訊號**，官方原文：exit 0 依 JSON 輸出決定，exit 1 或 3 以上多數事件視為非阻擋性錯誤、動作照常進行，只有 exit 2 是「阻擋性錯誤，無論 JSON 輸出寫什麼都會阻擋」[1]。腳本用 `"${CLAUDE_PROJECT_DIR}/.claude/hooks/xxx.sh"` 這種寫法引用，`CLAUDE_PROJECT_DIR` 是官方保證會設定好的環境變數，指向 session 啟動時的專案根目錄，不受目前工作目錄影響[1]。

### 安全注意事項

- **Hooks 是使用者自訂的 shell 指令，以你的權限、在你的環境裡執行**——不是模型自己決定要不要跑，這正是它比 CLAUDE.md 指示更「決定性」的原因：官方原文「hooks are deterministic and guarantee the action happens」，對照 CLAUDE.md 指示是「advisory」[3]。也因此，寫錯的 hook 有真實的系統風險，不是頂多讓模型多囉唆一句。
- Hooks 在 subagent 內同樣生效：subagent 呼叫工具時，`PreToolUse`／`PostToolUse` 跟主線對話一樣觸發已設定的 hooks[1]。
- Managed policy 可以設 `allowManagedHooksOnly`，限制只跑組織管理來源的 hooks，使用者／專案／本機／plugin 的 hooks 全部被擋，而且使用者端的關閉開關對 managed hooks 無效[1]。
- 多個 hook 掛在同一個高頻事件（例如 `PreToolUse`）上會平行執行[1]；平行執行是否會拖慢回應速度，官方 Hooks reference 沒有說明，這裡不臆測。

## 二、Subagent：定義檔與欄位語意

### 放在哪裡

`.claude/agents/*.md`（專案層，適合團隊共用，走版控）或 `~/.claude/agents/*.md`（使用者層，跨你所有專案生效）；Plugin 也可以在自己的 `agents/` 目錄裡帶 subagent 定義[2]。

這頁只列欄位語意；`background` 實際怎麼換工具集、`isolation: worktree` 怎麼真的擋下越界指令、`SendMessage` 怎麼續問一個已完成的 subagent、多代理成本三層倍數怎麼算，見專篇[Subagent 入門與實戰](subagent.md)。

### frontmatter 欄位

只有 `name` 與 `description` 是必填，其餘全部可省略，省略時各自有預設行為：

| 欄位 | 必填 | 語意 |
|---|---|---|
| `name` | 是 | 唯一識別名（小寫字母＋連字號） |
| `description` | 是 | 決定 Claude 何時該把任務委派給這個 subagent |
| `tools` | 否 | 允許使用的工具白名單；**省略則繼承所有 subagent 可用的工具**，不是「什麼都不能用」 |
| `disallowedTools` | 否 | 要從可用工具裡移除的黑名單 |
| `model` | 否 | `sonnet`／`opus`／`haiku`／`fable`／完整 model ID（如 `claude-opus-5`）／`inherit`（繼承目前主線用的模型） |
| `permissionMode` | 否 | `default`／`acceptEdits`／`auto`／`dontAsk`／`bypassPermissions`／`plan`／`manual`，語意同[Claude Code 設定總覽](official-config.md)第四節的 permission mode |
| `maxTurns` | 否 | 最多跑幾個 agentic turn，超過就強制停止 |
| `skills` | 否 | 這個 subagent 啟動時預先載進上下文的 skill 清單 |
| `mcpServers` | 否 | 這個 subagent 可以使用的 MCP servers |
| `hooks` | 否 | 只在這個 subagent 生效範圍內的額外 hooks |
| `memory` | 否 | 持久記憶範圍：`user`／`project`／`local` |
| `isolation` | 否 | 設 `worktree` 讓這個 subagent 跑在獨立的 git worktree 裡 |
| `background` | 否 | 設 `true` 讓這個 subagent 在背景執行 |
| `omitClaudeMd` | 否 | 設 `true` 時啟動不載入 CLAUDE.md |
| `effort` | 否 | 推理強度：`low`／`medium`／`high`／`xhigh`／`max` |
| `color` | 否 | 顯示用顏色：`red`／`blue`／`green`／`yellow`／`purple`／`orange`／`pink`／`cyan` |
| `initialPrompt` | 否 | 這個 agent 被當成主線 session agent 執行時，自動當第一則使用者訊息送出 |
| `experimental` | 否 | 實驗性選項的 map（例如 `cacheTtl: 5m` 或 `1h`） |

範例（官方文件節錄）[2]：

```markdown
---
name: code-improver
description: Scans files and suggests improvements for readability, performance, and best practices
tools: Read, Grep, Glob
model: sonnet
memory: project
---

You are a code improvement specialist. For each issue you find, explain
the problem, show the current code, and provide an improved version.
```

這個定義檔本身只有 `Read`、`Grep`、`Glob` 三個工具，代表它連檔案都不能改，只能讀跟搜尋——`tools` 欄位一旦寫了，就是完整覆蓋預設清單，不是在預設清單上追加。

### 內建 agent 跟自訂 agent 的差別

官方內建幾種現成的 agent 類型，不用自己寫定義檔[2]：

| 內建 agent | 定位 |
|---|---|
| `Explore` | 唯讀工具（Write／Edit 被拒），跳過 CLAUDE.md 與 git status 以維持輕量，用於檔案發現與程式碼搜尋 |
| `Plan` | 唯讀工具，用於 plan mode 下的程式庫研究 |
| `general-purpose` | 所有 subagent 可用工具都開，用於需要探索＋修改、複雜推理、多步驟依賴的任務 |
| `claude` | 無法歸類到專門 agent 時的萬用選項 |
| `statusline-setup` | 設定 status line |
| `claude-code-guide` | 回答 Claude Code 功能問題 |

跟自訂 agent 的差別只在於：內建 agent 不需要你寫 `.claude/agents/*.md`，工具範圍與模型已經被官方先設定好；自訂 agent 則是你自己決定 `tools`、`model`、`permissionMode` 這些欄位，換取更精確地控制它能碰到什麼、用什麼模型跑。

## 三、各自適合解決什麼問題

**Hooks 適合**：某件事必須每次都發生，不能靠模型自己記得（格式化、擋下對敏感檔案的修改、session 結束時記一筆狀態）。**不適合**：需要模型判斷「這種情況要不要做」的事——hooks 的 `command` 類型本身不理解語意，只認腳本邏輯；需要模型判斷的情境該用 `prompt` 或 `agent` 類型的 hook，或乾脆交給 CLAUDE.md／skill。

**Subagent 適合**：任務會產生大量你不需要留在主線上下文裡的雜訊（搜尋結果、檔案內容、log）；想針對特定任務限制工具或權限；工作自成一體，可以只回傳摘要；不同類型的任務需要不同模型跑[2]。**不適合**：需要頻繁來回、逐步微調的任務——subagent 預設從零上下文開始（除非明確要求 fork 繼承上下文），來回討論的成本反而比留在主線更高；多個階段要共用大量上下文（規劃→實作→測試）的連續工作，也不適合硬拆成獨立 subagent[2]。

兩者也可以疊在一起用：hook 觸發一個 `agent` 類型的處理器，等於「機制保證會發生」加上「交給一個獨立視角判斷」，例如 `Stop` hook 掛一個驗證用的 subagent，任務結束前強制跑一次獨立審查。

## 本頁重點回顧

- Hooks 設定在 `settings.json`，`matcher` 篩觸發時機，`hooks` 陣列放實際處理器；五種 handler 類型裡 `command` 最常見。
- `exit 2` 是唯一保證阻擋動作的訊號，其他 exit code 大多視為非阻擋性錯誤。
- Subagent 定義檔只有 `name`／`description` 必填，`tools` 省略＝繼承全部工具、寫了＝完整覆蓋不是疊加。
- 內建 agent（Explore／Plan／general-purpose 等）省去自己寫定義檔的功夫，自訂 agent 換取更精確的工具與模型控制。
- Hooks 解決「必須每次發生」，Subagent 解決「需要獨立乾淨視角」，兩者可以疊加使用。

## 資料來源

| 標記 | 來源 | URL |
|---|---|---|
| [1] | Hooks reference（事件清單、設定格式、handler 類型、exit code 語意、安全注意事項） | <https://code.claude.com/docs/en/hooks> |
| [2] | Create custom subagents（frontmatter 欄位、內建 agent、使用建議） | <https://code.claude.com/docs/en/sub-agents> |
| [3] | Best practices for Claude Code（hooks 是 deterministic、CLAUDE.md 是 advisory） | <https://code.claude.com/docs/en/best-practices> |

延伸：[SKILL、Plugin、MCP 與 Subagent](extensions.md)｜[Claude Code 設定總覽](official-config.md)｜[把 AI 代理的工作環境設計得可靠](harness.md)
