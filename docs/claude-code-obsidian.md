# Claude Code 接上 Obsidian vault

> 查證日期：2026-09-17。方案與功能變動快，請以官方最新說明為準。

Obsidian 的 vault 本質上就是「你電腦上的一個資料夾」，裡面是一堆 Markdown 檔案，加上一個 `.obsidian` 設定目錄 [B1]。而 Claude Code 本來就是在本機終端機跑、會直接讀寫檔案的工具 [A1]。所以這件事的答案比多數人想的簡單：**大部分情況你不需要任何外掛，把 vault 資料夾交給 Claude Code 就成了**。MCP server 與 Obsidian 社群 plugin 是用來補「純檔案系統做不到的那幾件事」，不是入場券。

這頁按「先能動、再加值」的順序寫：路徑 A 是最小可行、零安裝；路徑 B～D 各自解決一個 A 做不到的問題。每一節都附可以照抄的步驟，A 那節另外附一個確認串接成功的最小測試。

## 官方有沒有專門支援？查證結果：沒有

先把這題結清，才不會有人繼續找不存在的官方文件。

- 抓 `code.claude.com/docs/llms-full.txt`（Claude Code 官方文件全文，約 9.3 MB）做全文比對，**「Obsidian」出現 0 次**；同一份文件裡「Notion」出現 8 次（作為 MCP server 範例）[A2]。也就是說官方確實會點名特定第三方工具，只是沒點到 Obsidian。
- *（整理者的查證紀錄）* 另外以 `site:code.claude.com Obsidian` 做站內搜尋，回傳的全是不相關的一般文件頁，沒有任何 Obsidian 相關頁面。

> **整理者觀察**：綜合上面兩項查證，**Anthropic 官方沒有任何 Obsidian 專屬整合、專屬文件或官方 plugin**。這是從「文件裡查不到」推出的結論，不是官方發過的聲明。

下面所有做法用到的官方機制都是通用機制（工作目錄、`--add-dir`、MCP），Obsidian 這一端的東西則來自 Obsidian 官方或社群。

## 路徑 A：把 vault 當成工作目錄（零安裝，先做這個）

### 為什麼可行

Claude Code 的檔案存取範圍就是「工作目錄＋你額外授權的目錄」。官方提供三種加目錄的方式：啟動時的 `--add-dir <path>` 旗標、session 中的 `/add-dir` 指令、以及設定檔裡的 `permissions.additionalDirectories` [A3]。vault 沒有任何特殊格式，Markdown 就是 Markdown。

### 步驟（照抄即可）

**做法一：直接進 vault 開工**（最單純，適合「這次就是要整理筆記」）

```bash
cd /path/to/YourVault
claude
```

**做法二：留在原本的專案，另外授權 vault**（適合「一邊寫程式一邊記筆記」）

```bash
claude --add-dir /path/to/YourVault
```

或在 session 中途才想加：

```
/add-dir /path/to/YourVault
```

**做法三：寫進設定檔，每次都生效**——在 `~/.claude/settings.json`：

```json
{
  "permissions": {
    "additionalDirectories": ["/path/to/YourVault"]
  }
}
```

### 三種做法的差別（官方明講，容易踩）

`--add-dir` / `/add-dir` 加進來的目錄，除了檔案存取權，還會載入該目錄的 `.claude/skills/`、`.claude/commands/`、`.claude/agents/`；但 `permissions.additionalDirectories` 列的目錄**只給檔案存取權，不載入任何設定** [A3]。另外，`--add-dir` 目錄的 `CLAUDE.md` 預設**不會**被讀，要另外設 `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` 才會 [A3]。

> **整理者說明**：如果你想在 vault 裡放一份 `CLAUDE.md` 來規定「筆記怎麼寫、frontmatter 有哪些欄位」，最省事的是**做法一**（`cd` 進 vault 再開 Claude Code），因為那時 vault 就是主工作目錄，`CLAUDE.md` 自然會被讀到。用做法二的話記得補那個環境變數。

Windows 使用者另一個官方注意事項：`--add-dir`、`/add-dir` 與 `additionalDirectories` 會**拒絕網路路徑**（UNC share、`/net/<host>` automount），Windows 上請改用對應好的磁碟機代號 [A4]。vault 放在 NAS 上的人會直接撞到這條。

### 最小測試：確認真的串上了

隨便挑一篇有 frontmatter 的筆記，然後對 Claude Code 說：

```
讀 /path/to/YourVault/某篇筆記.md，只回報它 frontmatter（--- 之間的 YAML）裡有哪些欄位跟值，不要改任何東西。
```

- **回報得出欄位名稱** → 路徑與讀取權限都正確，串接成功。
- **說找不到檔案或沒有權限** → 路徑打錯，或是你用了做法二／三但路徑沒對上（注意 Windows 反斜線與空白字元）。
- **回報的欄位跟你在 Obsidian 裡看到的對不上** → 你讀到的可能是另一個同名檔案，用完整絕對路徑再試一次。

想順便驗寫入權限，再加一句：「在這篇筆記的 frontmatter 加一個 `test_by: claude` 欄位。」確認完記得叫它刪掉。Obsidian 的 properties 就是存成筆記最上方、以 `---` 前後包住的 YAML 區塊，欄位名與值之間是「冒號＋一個空格」，同一篇筆記裡欄位名不可重複 [B2]——這是驗證寫入格式正不正確的官方標準。

### 用這條路要注意的事

以下除了標注來源的，都是**整理者的操作建議**，不是官方規範：

- **`.obsidian/` 不要讓 Claude 亂動。** 這個資料夾放的是該 vault 的 Obsidian 設定，位於 vault 根目錄，而且因為開頭是點，多數作業系統預設隱藏 [B1]。*整理者建議*：在 `~/.claude/settings.json` 的 `permissions.deny` 加一條 `Edit` 規則擋掉 `**/.obsidian/**`，或至少在 vault 的 `CLAUDE.md` 裡寫明「不要修改 `.obsidian/`」。壞掉的 `.obsidian` 會讓外掛設定、主題、workspace 佈局一起出事。
- **Obsidian 正開著同一個檔案時。** *整理者觀察*：Obsidian 的編輯器持有記憶體中的版本，Claude Code 從檔案系統改檔，兩邊可能互相蓋掉。實務上請在讓 Claude 動某篇筆記前先把該分頁關掉，或改完之後才切回 Obsidian。官方文件對「外部程式編輯正開啟中的檔案」沒有專門說明，這點請當成經驗法則，不是保證。
- **有開 Obsidian Sync 的話，衝突有官方機制可依靠。** 同一檔案在兩台裝置各自被改過就會產生衝突；Markdown 檔的衝突 Obsidian Sync 會用 Google 的 diff-match-patch 演算法自動合併，從 1.9.7 起也可以改成「建立衝突檔案」讓你自己決定，這個設定是**逐裝置**的 [B3]。*整理者建議*：要讓 Claude Code 大量改筆記之前，把該裝置切成「建立衝突檔案」，比事後從自動合併的重複段落裡撿回來輕鬆。
- **wikilink 與 Markdown link 是兩套語法。** *整理者建議*：Claude 預設寫的是標準 Markdown 的 `[文字](路徑.md)`，如果你的 vault 習慣用 `[[筆記名]]`，請在 vault 的 `CLAUDE.md` 裡明文規定用 wikilink，否則產出的連結在 Obsidian 的關係圖譜裡不會被算成連結。同理，frontmatter 裡的內部連結依官方說明必須用引號包起來 [B2]。
- **改檔名／搬檔案不要用 `mv`。** *整理者建議*：純檔案系統的移動不會更新別篇筆記裡指向它的 wikilink。要搬要改名，用下面路徑 B 的官方 CLI，或回 Obsidian 介面操作。
- **先備份或先 commit。** *整理者建議*：vault 只要是 git repo，你就隨時能 `git diff` 看 Claude 到底改了什麼、隨時能還原。這是這整頁最划算的一個習慣。

## 路徑 B：補上 Obsidian 官方 CLI（處理「Obsidian 才知道的事」）

*整理者觀察*：路徑 A 的盲點是，Claude Code 看到的是檔案，不是 Obsidian——改名不會更新別篇筆記裡的反向連結、抓不到「今天的日記該建在哪」、不知道你裝了哪些外掛。

Obsidian 官方從 **1.12 版安裝檔（1.12.7 以上）** 起內建 command line interface，官方說法是「Anything you can do in Obsidian you can do from the command line」，涵蓋日記、檔案操作、搜尋、任務、標籤、properties、外掛、主題、workspace、同步、發佈等 30 多組指令；使用時 Obsidian 必須是開著的 [B4]。

**啟用步驟**（官方）[B4]：

1. Settings → General
2. 開啟 **Command line interface**
3. 依提示完成註冊（Windows 用 terminal redirector；macOS 建立 `/usr/local/bin/obsidian` symlink；Linux 把執行檔複製到 `~/.local/bin/obsidian`）

裝好之後 Claude Code 用 Bash 工具就能直接呼叫。想知道有哪些指令，讓它跑 [G1]：

```bash
obsidian help
```

社群 plugin 作者也把這條當成推薦搭配：Claude Code 用 CLI 開日記、搬檔案改名並自動更新連結、搜尋 vault [G1]。

> **整理者建議**：把「改名／搬檔案一律走 `obsidian` CLI，不要用 `mv`」寫進 vault 的 `CLAUDE.md`。這是路徑 A 最常見的資料損壞來源，一句話就能擋掉。

## 路徑 C：MCP server（讓 Claude 透過 Obsidian 本身操作 vault）

適合「Claude Code 跑在別的目錄、甚至別台機器，但要碰 vault」，或是你要的是 Obsidian 的搜尋／指令面板而不只是檔案內容。

### 目前找得到、還在維護的選項

| 專案 | 型態 | 最後更新 | 狀態與注意事項 |
|---|---|---|---|
| `coddingtonbear/obsidian-local-rest-api` | Obsidian 社群 plugin，**內建 MCP server** | 2026-08-31 [G2] | 目前最推薦。官方 README 直接寫「Claude Code 有原生 HTTP MCP 支援」並給出指令 [G3]。約 2.9k stars、3 個開放 issue [G2] |
| `MarkusPfundstein/mcp-obsidian` | 獨立 Python MCP server，需搭配上面那個 plugin | 2026-08-31 [G4] | 仍在維護、約 4.4k stars，但**開放 issue 有 101 個** [G4]，且 README 自述只支援 `mcp >=1.1.0,<2.0.0`、與 mcp 2.0+ 不相容 [G5] |
| `iansinnott/obsidian-claude-code-mcp` | Obsidian plugin，內建 WebSocket MCP server | **2025-06-27** [G6] | **已逾一年未更新**，19 個開放 issue。*整理者觀察*：它的功能定位（`/ide` 自動探索）與路徑 D 的 Claude Code IDE 高度重疊，而後者維護較新，因此不建議新裝 |

> **整理者觀察**：2025 年那一波「先裝 local REST API plugin，再裝一個獨立 MCP server 去接它」的兩層架構，現在大致過時了——`obsidian-local-rest-api` 自己就內建 MCP server，少一層就少一層壞。除非你有特別理由（例如需要 `mcp-obsidian` 獨有的某個工具），否則直接用下面的設定。另外 GitHub 上還有若干小型 fork 與變體（例如 `obsidian-mcp-router`），星數個位數、未經廣泛使用，這頁不列入推薦。

### 設定步驟：`obsidian-local-rest-api` 內建 MCP（照抄即可）

1. Obsidian → Settings → Community plugins → Browse，搜尋並安裝 **Local REST API**，啟用它 [G3]。
2. 到 Settings → Local REST API 複製你的 **API key** [G3]。
3. 在終端機跑（把 `<your-api-key>` 換掉）[G3]：

```bash
claude mcp add --transport http obsidian https://127.0.0.1:27124/mcp/ \
  --header "Authorization: Bearer <your-api-key>"
```

或改成手寫 `.mcp.json` [G3]：

```json
{
  "mcpServers": {
    "obsidian": {
      "type": "http",
      "url": "https://127.0.0.1:27124/mcp/",
      "headers": {
        "Authorization": "Bearer <your-api-key>"
      }
    }
  }
}
```

4. **處理 TLS 憑證**（*整理者觀察*：多數人會卡在這一步）。這個 plugin 啟動時自簽一張憑證，官方 README 給兩條路：到 `https://127.0.0.1:27124/obsidian-local-rest-api.crt` 下載並信任該憑證，或把 client 設成對 `127.0.0.1` 跳過 TLS 驗證。README 另外給了一條它自己標明為 insecure 的替代方案——在 Settings → Local REST API 開啟 HTTP server，改連 `http://127.0.0.1:27123/mcp/` [G3]。

**最小測試**：`/mcp` 看 `obsidian` 這台有沒有連上，再叫 Claude 用 MCP 工具列出 vault 根目錄的檔案。連不上通常就是第 4 步的憑證問題。

> **整理者提醒**：這個 API key 是你整個 vault 的讀寫金鑰。不要把它寫進會進版控的 `.mcp.json`（專案根目錄的那份通常會被 commit），用 `claude mcp add --scope user` 或改放使用者層設定比較安全。這是操作建議，不是官方要求。

## 路徑 D：Obsidian 社群 plugin（在 Obsidian 裡直接用 Claude Code）

前面三條都是「Claude Code 去找 vault」。這條反過來：**在 Obsidian 視窗裡就能用 Claude Code**。以下全部來自 Obsidian 官方社群 plugin 目錄，不是 Anthropic 官方產品。

| Plugin | 作者 | 做什麼 | 現況 |
|---|---|---|---|
| **Claudian** | Yishen Tu | 把 Claude Code、Codex、Grok、Opencode 等 agent CLI 嵌進 vault，vault 直接成為 agent 的工作目錄，支援 inline 編輯與 diff 預覽、slash command、檔案／資料夾 mention、MCP | 目前生態系裡最成熟的一個：官方目錄顯示 210 萬次下載、v2.2.7、5 天前更新；GitHub 約 15.4k stars、2026-09-17 仍有 push [G7][G8]。需桌面版、Obsidian v1.13.0+、且本機至少裝好一套 agent CLI [G7] |
| **Claude Code IDE** | petersolopov | 在 Obsidian 裡跑一個 WebSocket MCP server，Claude Code 的 `/ide` 選單會自動出現 Obsidian；連上後 Claude Code 看得到你開著的檔案與選取範圍 | 官方目錄顯示 1.6 萬次下載、v0.2.5、4 個月前更新；GitHub 2026-06-04 最後 push、0 開放 issue [G9][G1]。**刻意做成唯讀**：只分享選取內容與開啟中的檔名，不寫檔也不執行程式；綁 `127.0.0.1`、每 session 隨機 token [G1] |
| **Claude Code Skills** | p3nguln5 | 在筆記裡選字、右鍵挑一個 skill，回應串流到側邊欄 | 官方目錄顯示 2000 次下載、v1.0.5、4 個月前更新 [G10]。*整理者觀察*：以下載數與更新頻率看，規模明顯小於上面兩個。需本機已安裝並登入 Claude Code CLI（`claude` 要在 PATH 上）、僅桌面版、Obsidian 1.7.2+ [G10] |

Claude Code IDE 的作者自己把定位講得很清楚：**Claude Code 本來就能直接讀寫 vault 裡的檔案，這個 plugin 補的是反方向的「編輯器上下文」**——你現在開著哪篇、選了哪一段 [G1]。也就是說它跟路徑 A 是疊加關係，不是取代關係。

> **整理者觀察**：三個的取向完全不同。想「在 Obsidian 裡跟 agent 對話、讓它改筆記」選 Claudian；已經習慣在終端機用 Claude Code、只是希望它知道你在看哪篇，選 Claude Code IDE（而且它唯讀，風險最低）；Claude Code Skills 適合已經把自己的寫作規則做成 skill 的人。三個都是社群作品，Anthropic 不背書也不支援。

## Claude Cowork 能不能直接讀寫本機 vault？

這題的答案比預期複雜，分兩層：

**第一層：Cowork 執行指令與程式碼的環境是隔離的，不是你的本機終端機。** 官方寫「Shell commands and code Claude writes run inside that environment. Isolation protects your computer」[A5]。所以「叫 Cowork 跑一段 script 掃描我的 vault」這種用法**不成立**。

**第二層（這是會被漏掉的例外）：Cowork 桌面版有官方的本機資料夾連接機制。** 官方明寫「On desktop, Claude can read from and write to your local files without manual uploads or downloads」[A5]，另一篇的條件講得更死：雲端 session 要碰到你連接的本機資料夾，必須**桌面 App 開著、而且該 session 是從桌面版啟動的**；App 一關，session 繼續跑但碰不到本機檔案 [A6]。連接的方式是在訊息框選 Cowork，再連接你要它工作的資料夾；權限有 Manual／Auto／Skip 三種模式 [A6]。

**所以結論是**：Cowork 的確可以透過「連接本機資料夾」讀寫 vault 目錄下的 Markdown 檔，但**沒有任何 Obsidian 專屬支援**——`code.claude.com` 全文 0 次 Obsidian [A2]；*整理者查證紀錄*：本次讀過的兩篇 Cowork 官方說明頁 [A5][A6] 也完全沒提到 Obsidian 或任何筆記軟體。對 Cowork 而言 vault 就是一個普通資料夾。

> **整理者觀察**：能連，不代表好用。Cowork 碰不到本機終端機，等於路徑 B 的 Obsidian 官方 CLI 完全用不上——改名不更新連結、開不了日記。加上「桌面 App 必須開著」這個限制，實務上要對 vault 做有結構的整理，Claude Code 仍然是比 Cowork 合適的工具。這段是操作判斷，不是官方說法。

## 怎麼選（整理者觀察）

| 你想做的事 | 建議路徑 |
|---|---|
| 讓 AI 幫忙整理／改寫／彙整既有筆記 | A（必要時加 git 版控） |
| 會涉及改名、搬檔案、開日記 | A ＋ B |
| Claude Code 跑在別的專案目錄，偶爾要查筆記 | A 的做法二，或 C |
| 想在 Obsidian 視窗裡直接對話 | D（Claudian） |
| 在終端機用 Claude Code，但想讓它知道你在看哪篇 | A ＋ D（Claude Code IDE） |
| 手機上／不想開終端機 | 目前沒有好答案；Cowork 需要桌面 App 開著 [A6] |

## 資料來源（2026-09-17 查證）

| 標記 | URL | 用途 |
|---|---|---|
| A1 | code.claude.com/docs/en/overview | Claude Code 在終端機／IDE／桌面／瀏覽器執行、讀寫檔案與執行指令的定位 |
| A2 | code.claude.com/docs/llms-full.txt | Claude Code 官方文件全文；全文比對「Obsidian」0 次、「Notion」8 次的依據 |
| A3 | code.claude.com/docs/en/permissions#additional-directories-grant-file-access-not-configuration | `--add-dir`／`/add-dir`／`permissions.additionalDirectories` 三者差異、CLAUDE.md 需環境變數才載入 |
| A4 | code.claude.com/docs/en/changelog | `--add-dir` 拒絕 UNC／網路路徑、Windows 需用磁碟機代號 |
| A5 | support.claude.com/en/articles/13345190-get-started-with-claude-cowork | Cowork 指令與程式碼在隔離環境執行；桌面版可讀寫本機檔案 |
| A6 | support.claude.com/en/articles/15520349-use-claude-cowork-on-web-desktop-and-mobile | Cowork 本機資料夾連接的條件（桌面 App 需開著、session 需從桌面啟動）與權限模式 |
| B1 | obsidian.md/help/manage-vaults | vault 即檔案系統資料夾；`.obsidian` 設定資料夾位置與隱藏特性 |
| B2 | obsidian.md/help/properties | Obsidian properties 即筆記頂端 YAML；語法規則與內部連結需加引號 |
| B3 | obsidian.md/help/sync/troubleshoot | Obsidian Sync 衝突成因、diff-match-patch 自動合併、兩種衝突處理選項 |
| B4 | obsidian.md/help/cli | Obsidian 官方 CLI：版本需求、啟用步驟、各平台註冊方式、指令範圍 |
| G1 | github.com/petersolopov/obsidian-claude-ide | Claude Code IDE plugin 的安裝步驟、唯讀設計、安全機制、搭配 Obsidian CLI 的建議 |
| G2 | api.github.com/repos/coddingtonbear/obsidian-local-rest-api | 該 repo 最後 push 時間、未封存、stars／開放 issue 數 |
| G3 | github.com/coddingtonbear/obsidian-local-rest-api（README） | 內建 MCP server 端點、`claude mcp add` 指令、`.mcp.json` 範例、TLS 憑證處理與 HTTP 替代方案 |
| G4 | api.github.com/repos/MarkusPfundstein/mcp-obsidian | 該 repo 最後 push 時間、stars、101 個開放 issue |
| G5 | github.com/MarkusPfundstein/mcp-obsidian（README） | 設定方式、Python 版本需求、與 mcp 2.0+ 不相容的自述 |
| G6 | api.github.com/repos/iansinnott/obsidian-claude-code-mcp | 最後 push 為 2025-06-27、開放 issue 數（判定為停滯的依據） |
| G7 | community.obsidian.md/plugins/realclaudian | Claudian 的官方目錄資訊：作者、版本、更新時間、下載數、需求 |
| G8 | api.github.com/repos/yishentu/claudian | Claudian 的 stars 與最後 push 時間 |
| G9 | community.obsidian.md/plugins/claude-code-ide | Claude Code IDE 的官方目錄資訊：作者、版本、更新時間、下載數 |
| G10 | community.obsidian.md/plugins/claude-code-skills | Claude Code Skills 的官方目錄資訊與執行需求 |

註：A 系列為 Anthropic 官方文件，B 系列為 Obsidian 官方說明，G 系列為 GitHub 專案與 Obsidian 社群 plugin 目錄（社群作品，Anthropic 與 Obsidian 官方均不背書）。

延伸：[SKILL、Plugin、MCP 與 Subagent](extensions.md)｜[Claude Code 設定總覽](official-config.md)｜[付費區](paid-tier.md)
