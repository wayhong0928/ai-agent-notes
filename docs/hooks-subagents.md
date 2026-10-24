# Hooks 與 Subagent 設定

> 查證日期：2026-10-19（Hooks 細節、Subagent 位置優先序）；其餘 2026-10-05。方案與功能變動快，請以官方最新說明為準。

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

不是每個事件都能用 `exit 2` 擋。官方逐事件列了一張對照表，能擋的有 16 個：`UserPromptSubmit`、`UserPromptExpansion`、`PreToolUse`、`PostToolBatch`、`SubagentStop`、`TaskCreated`、`TaskCompleted`、`Stop`、`TeammateIdle`、`ConfigChange`、`WorktreeCreate`、`WorktreeRemove`、`PreCompact`、`PreModelSwitch`、`Elicitation`、`ElicitationResult`。其他事件回 `exit 2` 不會擋下任何東西。`PostToolUse` 只會把 stderr 交給 Claude，因為工具已經跑完了；`PermissionRequest` 不認 `exit 2`，要拒絕得改用 JSON 的 `decision` 物件[1]。這些事件在終端機、IDE 擴充、桌面 app 和雲端 session 裡都一樣會觸發[1]。

<figure class="diagram">
<svg class="dg-wide" viewBox="0 0 700 320" role="img" aria-labelledby="dghk-w">
<title id="dghk-w">Hooks 事件在一個 session 裡的觸發時間點。SessionStart 之後，一個用到工具的回合依序是 UserPromptSubmit、PreToolUse、執行工具、PostToolUse、Stop；PreToolUse 回傳 exit 2 會擋下這次呼叫，呼叫成功後才觸發 PostToolUse，失敗時改觸發 PostToolUseFailure；session 結束時觸發 SessionEnd。</title>
<defs><marker id="dghk-hw" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="dg-head" d="M0,0 L10,5 L0,10 z"/></marker></defs>
<rect class="dg-you" x="10" y="28" width="140" height="46" rx="10"/>
<text class="dg-c" x="80" y="56" text-anchor="middle">SessionStart</text>
<rect class="dg-you" x="580" y="28" width="110" height="46" rx="10"/>
<text class="dg-c" x="635" y="56" text-anchor="middle">SessionEnd</text>
<path class="dg-dash" d="M150,51 L578,51"/>
<text class="dg-l" x="364" y="42" text-anchor="middle">一個 session</text>
<path class="dg-line" d="M80,74 L80,138" marker-end="url(#dghk-hw)"/>
<path class="dg-line" d="M645,140 L645,76" marker-end="url(#dghk-hw)"/>
<rect class="dg-key" x="10" y="140" width="140" height="50" rx="10"/>
<text class="dg-c" x="80" y="170" text-anchor="middle">UserPromptSubmit</text>
<rect class="dg-key" x="180" y="140" width="110" height="50" rx="10"/>
<text class="dg-c" x="235" y="170" text-anchor="middle">PreToolUse</text>
<rect class="dg-box" x="320" y="140" width="100" height="50" rx="10"/>
<text class="dg-t" x="370" y="170" text-anchor="middle">執行工具</text>
<rect class="dg-key" x="450" y="140" width="120" height="50" rx="10"/>
<text class="dg-c" x="510" y="163" text-anchor="middle">PostToolUse</text>
<text class="dg-l" x="510" y="181" text-anchor="middle">（呼叫成功時）</text>
<rect class="dg-key" x="600" y="140" width="90" height="50" rx="10"/>
<text class="dg-c" x="645" y="170" text-anchor="middle">Stop</text>
<path class="dg-line" d="M150,165 L178,165" marker-end="url(#dghk-hw)"/>
<path class="dg-line" d="M290,165 L318,165" marker-end="url(#dghk-hw)"/>
<path class="dg-line" d="M420,165 L448,165" marker-end="url(#dghk-hw)"/>
<path class="dg-line" d="M570,165 L598,165" marker-end="url(#dghk-hw)"/>
<rect class="dg-note" x="180" y="86" width="230" height="36" rx="8"/>
<text class="dg-l" x="295" y="109" text-anchor="middle">腳本回傳 exit 2 就擋下這次呼叫</text>
<path class="dg-line" d="M235,140 L235,124" marker-end="url(#dghk-hw)"/>
<path class="dg-line" d="M510,190 C510,236 235,236 235,192" marker-end="url(#dghk-hw)"/>
<text class="dg-l" x="372" y="244" text-anchor="middle">下一次工具呼叫</text>
<path class="dg-line" d="M645,190 C645,300 80,300 80,192" marker-end="url(#dghk-hw)"/>
<text class="dg-l" x="362" y="296" text-anchor="middle">下一個回合</text>
</svg>
<svg class="dg-narrow" viewBox="0 0 350 500" role="img" aria-labelledby="dghk-n">
<title id="dghk-n">Hooks 事件在一個 session 裡的觸發時間點。SessionStart 之後，一個用到工具的回合依序是 UserPromptSubmit、PreToolUse、執行工具、PostToolUse、Stop；PreToolUse 回傳 exit 2 會擋下這次呼叫，呼叫成功後才觸發 PostToolUse，失敗時改觸發 PostToolUseFailure；session 結束時觸發 SessionEnd。</title>
<defs><marker id="dghk-hn" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="dg-head" d="M0,0 L10,5 L0,10 z"/></marker></defs>
<rect class="dg-you" x="40" y="10" width="180" height="40" rx="10"/>
<text class="dg-c" x="130" y="35" text-anchor="middle">SessionStart</text>
<path class="dg-line" d="M130,50 L130,78" marker-end="url(#dghk-hn)"/>
<rect class="dg-key" x="40" y="80" width="180" height="44" rx="10"/>
<text class="dg-c" x="130" y="107" text-anchor="middle">UserPromptSubmit</text>
<path class="dg-line" d="M130,124 L130,148" marker-end="url(#dghk-hn)"/>
<rect class="dg-key" x="40" y="150" width="180" height="44" rx="10"/>
<text class="dg-c" x="130" y="177" text-anchor="middle">PreToolUse</text>
<rect class="dg-note" x="234" y="148" width="80" height="48" rx="8"/>
<text class="dg-l" x="274" y="168" text-anchor="middle">exit 2</text>
<text class="dg-l" x="274" y="186" text-anchor="middle">擋下呼叫</text>
<path class="dg-line" d="M220,172 L232,172" marker-end="url(#dghk-hn)"/>
<path class="dg-line" d="M130,194 L130,218" marker-end="url(#dghk-hn)"/>
<rect class="dg-box" x="40" y="220" width="180" height="44" rx="10"/>
<text class="dg-t" x="130" y="247" text-anchor="middle">執行工具</text>
<path class="dg-line" d="M130,264 L130,288" marker-end="url(#dghk-hn)"/>
<rect class="dg-key" x="40" y="290" width="180" height="44" rx="10"/>
<text class="dg-c" x="130" y="309" text-anchor="middle">PostToolUse</text>
<text class="dg-l" x="130" y="326" text-anchor="middle">（呼叫成功時）</text>
<path class="dg-line" d="M40,312 L22,312 L22,172 L38,172" marker-end="url(#dghk-hn)"/>
<text class="dg-l" x="14" y="242" text-anchor="middle" transform="rotate(-90 14 242)">下一次工具呼叫</text>
<path class="dg-line" d="M130,334 L130,358" marker-end="url(#dghk-hn)"/>
<rect class="dg-key" x="40" y="360" width="180" height="44" rx="10"/>
<text class="dg-c" x="130" y="387" text-anchor="middle">Stop</text>
<path class="dg-line" d="M220,382 L326,382 L326,102 L222,102" marker-end="url(#dghk-hn)"/>
<text class="dg-l" x="338" y="300" text-anchor="middle" transform="rotate(-90 338 300)">下一個回合</text>
<path class="dg-line" d="M130,404 L130,438" marker-end="url(#dghk-hn)"/>
<rect class="dg-you" x="40" y="440" width="180" height="40" rx="10"/>
<text class="dg-c" x="130" y="465" text-anchor="middle">SessionEnd</text>
</svg>
<figcaption>常用的幾個 hook 事件在一個用到工具的回合裡的觸發時間點。工具呼叫前觸發 PreToolUse，腳本回傳 exit 2 會擋下這次呼叫；呼叫成功後觸發 PostToolUse，失敗時改觸發 PostToolUseFailure[1]。</figcaption>
</figure>

### 設定寫在哪裡、長什麼樣

Hooks 設定寫在 `settings.json`（使用者層 `~/.claude/settings.json` 或專案層 `.claude/settings.json`，見[Claude Code 設定總覽](official-config.md)的五層優先序）。`hooks` 是一個物件，key 是事件名稱，值是一個陣列，每個項目含 `matcher`（篩選何時觸發，可以是工具名、regex，或像 `SessionStart` 這種事件專屬的來源字串）與 `hooks`（真正要跑的處理器陣列）[1]。Handler 類型有五種：`command`（跑 shell 指令）、`http`（打 HTTP request）、`mcp_tool`（呼叫 MCP 工具）、`prompt`（送給 Claude 模型判斷）、`agent`（開一個 subagent）[1]。

除了這兩個設定檔，hook 一共可以放在七個地方[1]：

| 位置 | 生效範圍 | 能不能分享 |
|---|---|---|
| `~/.claude/settings.json` | 你所有的專案 | 不行，只在你的電腦上 |
| `.claude/settings.json` | 單一專案 | 可以，能 commit 進 repo |
| `.claude/settings.local.json` | 單一專案 | 不行，Claude Code 把設定存進這個檔時會設成 gitignore |
| Managed policy settings | 整個組織 | 可以，由管理員控制 |
| Plugin 的 `hooks/hooks.json` | plugin 啟用期間 | 可以，跟 plugin 一起打包 |
| Skill frontmatter | skill 被叫用後，到 session 結束 | 可以，寫在 skill 檔裡 |
| Subagent frontmatter | 那個 subagent 執行期間 | 可以，寫在 subagent 檔裡 |

雲端 session 不讀你本機的 `~/.claude/settings.json`[1]。各層的 hook 是疊加的，user、project、local 各自加進自己的 hook，不會把 managed 的 hook 蓋掉；同一個 handler 在好幾個設定檔都寫了，也只跑一次[1]。

在 Claude Code 裡輸入 `/hooks`，會開一個唯讀畫面列出目前所有 hook。想移除就得從設定檔刪掉那一筆，官方沒有「留著設定、只停用其中一個」的做法。直接改設定檔，通常會被檔案監看自動讀進去[1]。

### matcher、`if` 與各種 handler 的細節

- **matcher 怎麼判讀**：`"*"`、`""` 或不寫，代表全部符合。只用到字母、數字、`_`、`-`、空白、`,`、`|` 的，當成精確字串比對，所以 `Edit|Write` 只比對這兩個工具。含有其他字元就當成 JavaScript 正規表示式，而且不錨定頭尾，例如 `^Notebook` 會比對所有名稱以 Notebook 開頭的工具[1]。matcher 區分大小寫[4]。
- **MCP 工具要加 `.*`**：MCP 工具的名稱格式是 `mcp__<server>__<tool>`。想比對某個 server 的全部工具，要寫 `mcp__memory__.*`；只寫 `mcp__memory` 的話，裡面全是精確比對用的字元，會被當成一個完整工具名，結果什麼都比對不到[1]。
- **不支援 matcher 的事件**：`UserPromptSubmit`、`Stop`、`PostToolBatch` 這類事件每次都觸發，寫了 matcher 也會被默默忽略。`SessionStart` 的 matcher 比對的是 session 怎麼開始的，值有 `startup`、`resume`、`clear`、`compact`、`fork`[1]。
- **`if` 欄位**：寫在 handler 裡，內容是一條權限規則，像 `"Bash(git *)"` 或 `"Edit(*.ts)"`。只能寫一條，沒有 `&&`、`||` 或清單語法，條件不只一個就拆成好幾個 handler。官方說 `if` 只是盡力而為的過濾，真正要硬性允許或拒絕，應該交給權限系統[1]。
- **逾時預設**：`command`、`http`、`mcp_tool` 是 600 秒，`prompt` 30 秒，`agent` 60 秒。掛在 `UserPromptSubmit` 上的前三種例外，預設只有 30 秒[1]。
- **`agent` handler 還是實驗功能**，行為和設定以後可能會改，正式流程官方建議用 `command`[4]。
- **`prompt` handler**：模型回 `"ok": true` 就放行。掛在 `Stop` 或 `SubagentStop` 上時，不放行的 `reason` 會回送給 Claude 讓它接著做；如果同時回 `"impossible": true`，表示這個條件永遠達不到，Claude Code 就讓它停下[4]。
- **`http` handler**：光靠狀態碼擋不了，非 2xx 或連不上都只算非阻擋性錯誤。要擋就回 2xx，body 裡放帶決定欄位的 JSON[1]。
- **背景執行**：`command` hook 設 `"async": true` 會在背景跑，不擋住 Claude[1]。`/goal` 指令是內建捷徑，等於開一個只在這個 session 有效、用 prompt 判斷的 `Stop` hook[1]。

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

這個範例可以直接照抄：把它貼進 `.claude/settings.json`，前提是專案已經裝了 `prettier` 且 `jq` 在 PATH 裡。想擋掉某個動作而不是事後處理，改用 `PreToolUse` 並讓腳本以 `exit 2` 結束——**`exit 2` 是唯一保證阻擋該動作的訊號**，官方原文：exit 0 依 JSON 輸出決定，exit 1 或 3 以上時，stdout 若沒有有效 JSON，多數事件視為非阻擋性錯誤、動作照常進行（若有通過驗證的 JSON，則忽略 exit code、由 JSON 決定結果）[^fresh1]，只有 exit 2 是「阻擋性錯誤，無論 JSON 輸出寫什麼都會阻擋」[1]。腳本用 `"${CLAUDE_PROJECT_DIR}/.claude/hooks/xxx.sh"` 這種寫法引用，`CLAUDE_PROJECT_DIR` 是官方保證會設定好的環境變數，指向 session 啟動時的專案根目錄，不受目前工作目錄影響[1]。

### 官方範例：擋下 `rm -rf`

Hooks reference 的範例，`matcher` 先限縮到 Bash 工具，`if` 再限縮到符合 `rm *` 的子指令，兩個條件都符合才會啟動腳本，像 `npm test` 這種指令就不會多開一個程序[1]：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(rm *)",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.sh",
            "args": []
          }
        ]
      }
    ]
  }
}
```

```bash
#!/bin/bash
# .claude/hooks/block-rm.sh
COMMAND=$(jq -r '.tool_input.command')

if echo "$COMMAND" | grep -q 'rm -rf'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Destructive command blocked by hook"
    }
  }'
else
  exit 0  # no decision; normal permission flow applies
fi
```

腳本存成 `.claude/hooks/block-rm.sh` 之後要 `chmod +x`，而且 `jq` 要在 PATH 裡[1]。這個腳本走的是 JSON 那條路，`exit 0` 再印出 `permissionDecision: "deny"`，沒有用 `exit 2`。官方另外提供 Windows PowerShell 版，matcher 寫成 `Bash|PowerShell`，因為一條 `if` 規則只對得上一種工具，兩個工具各配一個 handler[1]。

### 輸入、exit code 與 JSON 輸出

- **輸入**：command hook 從 stdin 收到 JSON。每個事件都有 `session_id`、`cwd`、`hook_event_name`，`PreToolUse` 另外帶 `tool_name`、`tool_input`、`tool_use_id`[1]。
- **`exit 2` 時**：隨著阻擋送出的訊息是 stderr。這時就算印了 JSON，裡面的欄位也翻不了案，連 `permissionDecision: "allow"` 都放不過去[1]。
- **`exit 0` 時**：多數事件的 stdout 只寫進 debug log，對話紀錄裡看不到。例外是 `UserPromptSubmit`、`UserPromptExpansion`、`SessionStart`、`PostModelSwitch` 四個事件，它們的純文字 stdout 會變成 Claude 看得到的上下文。另外，hook 以 `exit 0` 結束時，Claude 完全看不到它的 stderr[1]。
- **兩種做法擇一**：一個 hook 要嘛只用 exit code 表達，要嘛 `exit 0` 再印 JSON。選 JSON 的話，stdout 只能有那個 JSON 物件[1]。JSON 前面多印了別的字，或把 `permissionDecision` 放在最外層、沒放進 `hookSpecificOutput`，JSON 都不會生效[4]。
- **決定欄位依事件而不同**：`UserPromptSubmit`、`PostToolUse`、`Stop`、`SubagentStop`、`ConfigChange`、`PreCompact` 等事件用最外層的 `decision: "block"` 加 `reason`；`PreToolUse` 用 `hookSpecificOutput.permissionDecision`；`PermissionRequest` 用 `decision.behavior`[1]。
- **`continue: false`**：hook 跑完後 Claude 整個停止處理，而且優先於任何事件專屬的決定欄位[1]。

### PreToolUse 的決定與權限規則

- `permissionDecision` 有四個值。`deny` 擋下這次呼叫，`ask` 跳出確認，`defer` 讓工具之後再接著執行，`allow` 跳過權限確認。好幾個 `PreToolUse` hook 回的決定不一樣時，優先序是 `deny` > `defer` > `ask` > `allow`。用 `exit 2` 擋下的效果跟 `deny` 一樣，Claude 會把 stderr 當成拒絕理由[1]。
- `allow` 也有跳不過的確認，包括任何權限模式都不會自動核准的動作、從網路路徑讀檔，以及 `AskUserQuestion`、`ExitPlanMode`（這兩個要搭配 `updatedInput`）[1]。
- `defer` 只在加了 `-p` 的非互動模式有效，互動 session 會記一筆警告後忽略。而且 Claude 那一回合只呼叫一個工具時才有效，同時呼叫好幾個就會被忽略[1]。
- hook 的決定繞不過權限規則。符合的 deny 規則照樣擋，符合的 ask 規則照樣跳確認，就算 hook 回的是 `allow` 也一樣[5]。反過來，hook 回 `deny` 在每一種權限模式都有效，`bypassPermissions` 或 `--dangerously-skip-permissions` 底下也擋得住。設定檔和 plugin 裡的 hook 只能收緊權限，不能放寬到權限規則允許的範圍之外[4]。
- 有一個例外。你安裝的 [mod](mods.md) 如果處理 `tool.check`，可以核准被你的 `PreToolUse` hook 擋下的呼叫，除非那個 hook 寫在 managed settings 裡[4]。
- **hook 壞掉時預設不擋**。逾時的 `command`、`http`、`mcp_tool` hook 不會擋下工具呼叫；多數事件上，腳本路徑打錯或腳本當掉，動作也照樣執行。想讓它失敗時改成擋下，在 `command` 或 `http` hook 加 `"onFailure": "block"`（預設是 `"continue"`，需要 v2.1.295 以上）[1]。設好一個管控用的 hook 後，第一次執行要留意有沒有跳出錯誤提示，`settings.json` 裡的路徑打錯，代表這個 hook 從來沒跑過[1]。
- `PreToolUse` 只在 Claude 呼叫工具時觸發。你在 prompt 裡用 `@` 引用的檔案，預設不經過任何工具就直接加進來，hook 管不到[1]。`PostToolUse` 觸發時工具已經跑完，沒辦法復原[4]。

### 幾個事件的特別行為

- **`Stop`**：Claude 每次回應結束都會觸發，不只在任務完成時，使用者手動中斷則不觸發[4]。回 `decision: "block"` 可以不讓 Claude 停下，但連續擋了 8 次，下一次就會被強制放行；Claude 只要呼叫一次工具，計數就歸零，想調高上限可以設環境變數 `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`。輸入裡的 `stop_hook_active` 是 `true`，表示這一輪本來就是被 stop hook 擋回來繼續做的[1]。
- **`SessionStart`**：每個 session 都會跑，所以要寫得快。只支援 `command` 和 `mcp_tool` 兩種 handler；只想加上下文的話，直接印純文字就好，不必組 JSON[1]。[跨 session 接力](session-handoff.md)那頁就是用這個機制。

### 安全注意事項

- **Hooks 是使用者自訂的 shell 指令，以你的權限、在你的環境裡執行**——不是模型自己決定要不要跑，這正是它比 CLAUDE.md 指示更「決定性」的原因：官方原文「hooks are deterministic and guarantee the action happens」，對照 CLAUDE.md 指示是「advisory」[3]。也因此，寫錯的 hook 有真實的系統風險，不是頂多讓模型多囉唆一句。
- Hooks 在 subagent 內同樣生效：subagent 呼叫工具時，`PreToolUse`／`PostToolUse` 跟主線對話一樣觸發已設定的 hooks[1]。
- Managed policy 可以設 `allowManagedHooksOnly`，限制只跑組織管理來源的 hooks，使用者／專案／本機／plugin 的 hooks 全部被擋，而且使用者端的關閉開關對 managed hooks 無效[1]。
- 多個 hook 掛在同一個高頻事件（例如 `PreToolUse`）上會平行執行[1]；平行執行是否會拖慢回應速度，官方 Hooks reference 沒有說明，這裡不臆測。一個 hook 回了 `deny`，同時觸發的其他 hook 還是會跑完[4]。
- 暫時關掉所有 hook，在設定檔寫 `"disableAllHooks": true`。寫在個人或專案設定檔時，會關掉 user、project、local 和 plugin 的 hook，也會停掉你自己裝的 mod，但 managed hooks 照跑[6]。最後生效的是依設定優先序算出來的值，所以專案 `.claude/settings.json` 裡的 `false` 會蓋過你 user 設定裡的 `true`；想不管專案怎麼設、只在這一次執行關掉，用 `--settings '{"disableAllHooks": true}'`[1]。
- **工作區信任**：互動 session 在你接受這個資料夾的信任對話框之前，所有設定檔裡的 hook 都先不跑，連你自己的 `~/.claude/settings.json` 也一樣。`-p` 和 SDK session 不會跳這個對話框，直接把資料夾當成已信任，所以 repo 裡 commit 的 hook 會在你從沒信任過的資料夾裡執行。要對不是自己寫的 repo 跑 `claude -p`，先看過它的 `.claude/` 設定檔，或用 `--bare` 啟動，或用 `--settings '{"disableAllHooks": true}'` 關掉那次執行的 hook[1]。
- 寫 hook 腳本時，不要盲目相信輸入資料，shell 變數一律加引號寫成 `"$VAR"`，並檢查檔案路徑裡有沒有 `..`，擋掉路徑穿越[1]。
- 除錯時用 `claude --debug-file <path>` 把 log 寫到指定位置，或用 `claude --debug` 啟動，再去看 `~/.claude/debug/<session-id>.txt`[1]。

## 二、Subagent：定義檔與欄位語意

### 放在哪裡

`.claude/agents/*.md`（專案層，適合團隊共用，走版控）或 `~/.claude/agents/*.md`（使用者層，跨你所有專案生效）；Plugin 也可以在自己的 `agents/` 目錄裡帶 subagent 定義[2]。

好幾個地方有同名的 subagent 時，Claude Code 用優先順序高的那一個[2]：

| 位置 | 生效範圍 | 優先順序 |
|---|---|---|
| Managed settings | 整個組織 | 1（最高） |
| `--agents` CLI 旗標 | 這次 session | 2 |
| `.claude/agents/` | 目前專案 | 3 |
| `~/.claude/agents/` | 你所有的專案 | 4 |
| Plugin 的 `agents/` 目錄 | plugin 啟用的地方 | 5（最低） |

基於安全考量，plugin 帶來的 subagent 不支援 `hooks`、`mcpServers`、`permissionMode` 三個 frontmatter 欄位，從 plugin 載入時這三個欄位會被忽略[2]。

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
| [4] | Automate actions with hooks（prompt／agent hook、權限模式、疑難排解） | <https://code.claude.com/docs/en/hooks-guide> |
| [5] | Configure permissions（hook 決定不能繞過權限規則） | <https://code.claude.com/docs/en/permissions> |
| [6] | All settings（`disableAllHooks` 各層的作用範圍） | <https://code.claude.com/docs/en/settings-reference> |

延伸：[SKILL、Plugin、MCP 與 Subagent](extensions.md)｜[Claude Code 設定總覽](official-config.md)｜[把 AI 代理的工作環境設計得可靠](harness.md)

[^fresh1]: 2026-10-05 依官方原文更新，出處：<https://code.claude.com/docs/en/hooks>
