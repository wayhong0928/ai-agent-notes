# SKILL、Plugin、MCP 與 Subagent

> 查證日期：2026-09-16。方案與功能變動快，請以官方最新說明為準。

看懂[代理迴圈](agent-basics.md)之後，下一個常見的卡點是：SKILL、Plugin、MCP、Subagent、Hooks，這幾個詞經常混著用，但它們解決的問題完全不同。這頁先用一張精簡的支援矩陣對照六種擴充機制，再逐一給解決什麼問題、最小範例跟常見誤用，最後給一份「該用哪一種」的決策清單。

## 一、六種機制支援矩陣

「✅」代表官方文件明確查證到支援；「⚠️」代表有限制、有條件，或官方文件本身說法不一致；「❌」代表官方文件裡沒有查到對應機制，不是本站主觀認定不支援。Claude.ai 一欄把 Chat（一般對話）與 Cowork（本機或雲端 VM 裡的知識工作代理）合併標示，因為官方文件裡這兩者能碰到的機制常常不一樣，差異細節與完整來源標記在下方「一之二」逐項說明。

| 機制 | Claude Code | Codex | Claude.ai（Chat／Cowork） |
|---|:---:|:---:|:---:|
| CLAUDE.md／AGENTS.md | ✅ | ✅ | ⚠️近似機制 |
| SKILL | ✅ | ✅ | ✅需開code exec |
| MCP | ✅本機＋遠端 | ✅ | ⚠️僅遠端 |
| Subagent | ✅ | ✅ | ⚠️僅Cowork |
| Plugin | ✅ | ✅ | ⚠️說法不一 |
| Hooks | ✅ | ✅ | ⚠️僅Cowork執行 |

## 一之二、每種機制解決什麼問題、什麼時候載入、放在哪裡

- **CLAUDE.md／AGENTS.md**：解決「讓代理每次啟動都知道專案的事實與規矩，不用每次重講一遍」；啟動時整份載入，全程留在上下文裡；放在專案根目錄或 `~/.claude/`（Claude Code），`~/.codex/`＋專案路徑逐層（Codex）。Claude Code 讀 `CLAUDE.md`[1]（v2.1.277 起，2026-09-18，專案完全沒有 CLAUDE.md 時也會直接讀 AGENTS.md；有 CLAUDE.md 就跟以前一樣不讀，細節見[Claude Code 設定總覽](official-config.md)[25]）；Codex 讀 `AGENTS.md`，逐層合併，越接近目前目錄優先權越高[2]；Claude.ai 沒有 CLAUDE.md 這個檔案機制，但 Projects 的 Project instructions 用途類似：都能讓一組指示套用到之後每一次對話，只是載入方式與作用範圍不同（Project instructions 是整個 Project 的設定，不是依檔案路徑逐層載入）；Cowork 另有跨 session 的 Global instructions，跟針對單一本機資料夾的 Folder instructions[15][16]。
- **SKILL**：解決「把一套會重複用到的程序、檢查清單變成隨需載入的知識，不佔用平時的上下文」；只有 Claude 判斷相關、或使用者手動叫用時才載入完整內容；放在 `.claude/skills/<name>/SKILL.md`（專案或個人層）。Claude Code 支援[3]；Codex 遵循「open agent skills standard」[4]；Claude.ai 需另外開啟 code execution[5]。
- **MCP**：解決「讓代理連上外部工具與資料（文獻庫、資料庫、雲端硬碟），不必自己捏造答案」；設定好之後，工具定義預設延後載入，代理實際要用某個工具時才載入細節[1]；放在 `.mcp.json`（專案層）／`~/.claude.json`（使用者層，Claude Code），`codex mcp` 管理（Codex）。Claude Code 支援本機＋遠端[6]；Codex「continues to support external MCP servers」[7]；Claude.ai 僅遠端 connector，Free 帳號限 1 個自訂連接[8]。
- **Subagent**：解決「需要一個獨立、乾淨的視角處理某件事，不污染主線對話的上下文」；主線判斷該任務適合委派時，另開一個獨立上下文執行；放在 `.claude/agents/<name>.md`（Claude Code），`~/.codex/agents/` 或 `.codex/agents/` 的 TOML 檔（Codex）。Claude Code 支援[9]；Codex 支援[10]；Claude.ai 分開看：Cowork 官方公開有 sub-agent coordination，會把複雜工作拆成小任務、平行協調多個工作流；一般 Chat／Projects 查無使用者可自訂的通用 subagent 介面（Research 功能內部用 lead agent 加 subagents，但那是內部架構，不是使用者自己能設定的機制）[16][17][22]。
- **Plugin**：解決「把 SKILL、Subagent、Hooks、MCP 設定打包成一個可安裝、可分享、可版控的單位」；安裝後在啟動時載入其中的元件；需要 `.claude-plugin/plugin.json`，其餘元件目錄放在 plugin 根目錄（Claude Code），Codex／ChatGPT 共用「Plugins 目錄」發佈機制[11]。Claude Code 支援[11]；Codex 側的 skill 可打包成 plugin 發佈[4]；Claude.ai 官方文件目前說法不一致：較新的 Help Center 文章說付費方案（Pro／Max／Team／Enterprise）可以在 Web Chat、Claude Desktop 的 Chat 分頁、Cowork 安裝並使用 plugin；但另一份官方 Cowork 開發文件仍寫「不在 Chat 使用」。即使 Chat 能裝 plugin，裡面包的 subagent 跟 hooks 也只在 Cowork 執行，Chat 裡會顯示成灰階[17][18][19][20]。
- **Hooks**：解決「把『一定要做到』的檢查變成機制強制執行，而不是寫在說明檔裡靠模型自己記得」；對應事件觸發時（例如編輯檔案前、session 結束時）自動執行；放在 `settings.json` 的 `hooks` 欄位（Claude Code），`hooks.json` 或 `config.toml` 的 `[hooks]`（Codex）。Claude Code 支援[12]；Codex「Hooks are an extensibility framework for Codex」[13]；Claude.ai 分開看：Cowork 可以執行 plugin 裡包的 hooks；一般 Chat 不執行，畫面上會顯示成灰階。Enterprise 另有一套「inference hooks」，是組織端把推論內容送去自己的端點做核准／拒絕政策判斷的合規機制，跟這裡講的生命週期 hooks 不是同一件事，一句話帶過即可[17][21]。

!!! warning "2026-09-16 起：Chat／Cowork 的界線正在消失（Pro／Max 分階段推出中）"
    上表把 Claude.ai 分成 Chat 與 Cowork 兩欄，是依官方文件目前的寫法整理的。但官方已公告兩者正在合併成同一個體驗：Pro／Max 帳號分階段收到（同方案帳號時間點也不同），收到之後不再有獨立 Cowork 模式可切換，上表裡「⚠️ 只在 Cowork 執行、Chat 裡顯示灰階」這類限制對這些帳號會失效，變成同一個對話視窗、能力視需要自動啟用。Team／Free 官方說「即將推出」但目前尚未開始，Enterprise 變動前會提前至少 30 天通知、目前維持現狀——這些帳號適用的仍是上表原本的區分。查證來源與時程細節見 [tools-compare.md](tools-compare.md) 開頭的說明 [23][24]。

## 二、每種機制的最小範例與常見誤用

### CLAUDE.md／AGENTS.md：專案事實與紅線

官方定義的分工是：「把 CLAUDE.md 當成你原本會重複解釋的內容寫下來」[1]。放事實，不是放程序；一旦某一段變成一套步驟而不是一條事實，就該搬進 SKILL。

一個研究專案的骨架（`AGENTS.md` 換成 `CLAUDE.md` 一樣適用）：

```markdown
# 專案：資料分析報告

## 這個資料夾是什麼
- `data/raw/` 原始資料，禁止修改
- `data/clean/` 清理後的資料
- `scripts/` 分析腳本

## 絕對不要做的事
- 不要修改 `data/raw/` 底下的任何檔案
- 不要生成任何沒有依據的統計數字，算不出來就說算不出來
```

**常見誤用**：把「Claude 讀程式碼就能自己推得出的東西」也寫進去，或者把一套多步驟的檢查流程整段塞進 CLAUDE.md。官方的判斷標準很直接：拿掉這一行，模型會不會因此犯錯？答不出來的行，就是灌水，該刪或該搬進 SKILL[14]。

### SKILL：隨需載入的程序

一個 SKILL 就是一個資料夾裡的 `SKILL.md`，YAML frontmatter 必須從檔案第一行開始：

```yaml
---
name: check-broken-links
description: 掃描專案裡所有 Markdown 連結，找出指向不存在檔案的失效連結。
  當使用者要求「檢查連結」「找失效連結」時使用。
---

# 檢查失效連結

對指定的目錄執行以下步驟：
1. 搜尋所有 .md 檔案裡的連結語法
2. 逐一比對連結目標是否存在
3. 輸出表格：檔名、行號、連結文字、目標路徑、是否存在
```

呼叫方式來自資料夾名稱，不是 frontmatter 裡的 `name` 欄位：存在 `.claude/skills/check-broken-links/SKILL.md`，就用 `/check-broken-links` 叫用，或讓 Claude 依 `description` 自己判斷要不要用[3]。

**常見誤用**：把 `description` 寫得太籠統（例如只寫「檢查文件」），代理判斷不出什麼時候該用；或者把整份參考資料塞進 `SKILL.md` 本體，官方建議本體控制在 500 行以內，細節另外放進 `reference.md` 用連結引用，需要時才載入[3]。

### MCP：接上外部工具

在 Claude Code 專案根目錄放一個 `.mcp.json`：

```json
{
  "mcpServers": {
    "example": {
      "type": "http",
      "url": "https://mcp.example.com/mcp"
    }
  }
}
```

這個檔案建議一起進版本控制，讓團隊每個人都接到同一組工具[6]。Codex 側用 `codex mcp` 指令管理連接的外部 MCP server[7]。

**常見誤用**：以為裝了 MCP 就不會有幻覺答案。MCP 只解決「有沒有真的東西可以查」的問題，代理仍然可能查了卻答錯，或者選錯了要查的工具，接上文獻庫之後還是要核對它真的引用了查到的內容，不是引用了憑空生成的內容。

想知道 `claude mcp add` 的完整用法、scope 怎麼選、OAuth 認證，以及 Windows 上常見的 `cmd /c` 誤區與 Git Bash 踩坑，見專篇[MCP 入門與實戰](mcp.md)。

### Subagent：獨立乾淨的視角

`.claude/agents/` 底下的一個定義檔，只有 `name` 與 `description` 是必填：

```markdown
---
name: code-improver
description: 掃描檔案並針對可讀性、效能、最佳實務提出改善建議
tools: Read, Grep, Glob
model: sonnet
---

You are a code improvement specialist. For each issue you find, explain
the problem, show the current code, and provide an improved version.
```

官方建議適合用 subagent 的情境：任務會產生大量你不需要留在主線的雜訊（搜尋結果、檔案內容）；想針對特定任務限制工具權限；工作自成一體，可以只回傳摘要[9]。

**常見誤用**：拿 subagent 處理需要頻繁來回微調的任務。官方明講，subagent 預設從零上下文開始，來回討論的成本反而更高；這種情境該留在主線對話，或者用 SKILL 讓主線自己套用同一套程序[9]。

### Plugin：打包分享

`plugin.json` 只有 `name` 是必填：

```json
{
  "name": "my-research-kit",
  "description": "研究工作的檢查與整理工具組",
  "version": "1.0.0"
}
```

**容易踩的坑**：只有 `plugin.json` 放在 `.claude-plugin/` 資料夾裡，`skills/`、`agents/`、`hooks/` 都要放在 plugin 根目錄，不能一起塞進 `.claude-plugin/`[11]。

### Hooks：機制強制，不是文字提醒

官方一句話講完 Hooks 存在的理由：「hooks are deterministic, CLAUDE.md instructions are advisory」[14]。說明檔裡的規則只是建議，模型可能因為疏忽或上下文太滿而沒照做；真正不能妥協的規矩要用會強制擋下動作的機制卡住。

官方範例：擋掉對敏感檔案的編輯，`.claude/hooks/protect-files.sh` 判斷路徑，命中就用 `exit 2` 擋下（`exit 2` 是唯一保證阻擋的訊號，其他 exit code 大多視為非阻擋性錯誤，動作照常進行）：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protect-files.sh" }
        ]
      }
    ]
  }
}
```

**常見誤用**：把本來該用 Hooks 卡住的規矩，寫成 CLAUDE.md 裡的一句「請不要修改 xxx」。文字提醒在上下文夠乾淨時通常有效，但不是保證；真正不可退讓的邊界要靠機制，不能只靠模型記得。

## 三、該用哪一種：決策清單

依序問自己這幾個問題：

1. **這是一條事實還是一套程序？** 事實（這個專案是什麼、有什麼紅線）→ CLAUDE.md／AGENTS.md。程序（一套會重複執行的檢查或步驟）→ SKILL。
2. **需要接觸目前工具箱之外的東西嗎？**（例如查公司內部資料庫、讀 Google Drive 裡的檔案）需要 → MCP。
3. **這個任務會製造大量你不需要看到的雜訊，或者需要獨立不受污染的視角嗎？** 是 → Subagent。
4. **這件事必須每次都發生，不能靠模型自己記得嗎？** 是 → Hooks。
5. **上面幾樣東西累積到值得跨專案重複使用，或想分享給別人嗎？** 是 → 打包成 Plugin。

不確定的時候，先從最輕的做起：一條規則先寫進 CLAUDE.md，發現自己在重複貼同一段指示三次以上，才升級成 SKILL；SKILL 累積到五個以上、且想分享時，才打包成 Plugin。

想知道這些機制在 `settings.json` 裡具體怎麼寫、權限規則怎麼設，見[Claude Code 設定總覽](official-config.md)；想看 Hooks 與 Subagent 更完整的設定範例與陷阱，見[Hooks 與 Subagent 設定](hooks-subagents.md)（這兩頁本站尚未寫，連結先放著）。

## 資料來源

| 標記 | 來源 | URL |
|---|---|---|
| [1] | How Claude remembers your project（CLAUDE.md、MCP 工具定義延後載入） | <https://code.claude.com/docs/en/memory> |
| [2] | AGENTS.md（Codex，讀取順序與合併規則） | <https://learn.chatgpt.com/docs/agent-configuration/agents-md> |
| [3] | Extend agents with skills（SKILL.md 結構、呼叫方式） | <https://code.claude.com/docs/en/skills> |
| [4] | Build skills（Codex/ChatGPT Skills 與 Plugins 關係） | <https://learn.chatgpt.com/docs/build-skills> |
| [5] | What are skills（Claude Chat 的 Skills 可用性） | <https://support.claude.com/en/articles/12512176-what-are-skills> |
| [6] | Claude Code MCP 官方文件（`.mcp.json`、`~/.claude.json` 範例） | <https://code.claude.com/docs/en/mcp> |
| [7] | Codex MCP server 支援說明 | <https://learn.chatgpt.com/docs/mcp-server> |
| [8] | Get started with custom connectors using remote MCP（Claude Chat 免費帳號限 1 個） | <https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp> |
| [9] | Create custom subagents（Claude Code） | <https://code.claude.com/docs/en/sub-agents> |
| [10] | Subagents（Codex，TOML 設定） | <https://learn.chatgpt.com/docs/agent-configuration/subagents> |
| [11] | Plugins reference（Claude Code plugin.json、目錄結構限制） | <https://code.claude.com/docs/en/plugins-reference> |
| [12] | Hooks reference（Claude Code） | <https://code.claude.com/docs/en/hooks> |
| [13] | Hooks（Codex） | <https://learn.chatgpt.com/docs/hooks> |
| [14] | Best practices for Claude Code（CLAUDE.md 精簡判準、hooks 是決定性的） | <https://code.claude.com/docs/en/best-practices> |
| [15] | How can I create and manage projects?（Claude.ai Project instructions） | <https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects> |
| [16] | Get started with Claude Cowork（Global／Folder instructions、sub-agent coordination） | <https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork> |
| [17] | Use plugins in Claude（Chat／Cowork 的 plugin、subagent、hooks 可用範圍） | <https://support.claude.com/en/articles/13837440-use-plugins-in-claude> |
| [18] | Manage plugins for your organization（plugin 出現在 Chat 與 Cowork 的官方原文） | <https://support.claude.com/en/articles/13837433-manage-plugins-for-your-organization> |
| [19] | Use Claude Cowork on web, desktop, and mobile（Cowork 不限桌面版） | <https://support.claude.com/en/articles/15520349-use-claude-cowork-on-web-desktop-and-mobile> |
| [20] | Install plugins（Cowork 開發文件，仍寫「不在 Chat 使用」，跟 [17][18] 說法不一致） | <https://claude.com/docs/cowork/guide/plugins> |
| [21] | Inference hooks overview（Enterprise 合規機制，跟生命週期 hooks 不同性質） | <https://support.claude.com/en/articles/16059458-inference-hooks-overview> |
| [22] | How we built our multi-agent research system（Research 功能內部的 lead agent／subagents 架構） | <https://www.anthropic.com/engineering/multi-agent-research-system> |
| [23] | Cowork is now Claude（Cowork 與 Chat 合併公告，2026-09-16） | <https://claude.com/blog/cowork-is-now-claude> |
| [24] | Claude Cowork and chat are one Claude（合併現況：各方案推出時程） | <https://support.claude.com/en/articles/16761823-claude-cowork-and-chat-are-one-claude> |
| [25] | Claude Code changelog（v2.1.277，2026-09-18，AGENTS.md support） | <https://code.claude.com/docs/en/changelog> |

延伸：[AI Agent 怎麼運作](agent-basics.md)｜[把 AI 代理的工作環境設計得可靠](harness.md)
