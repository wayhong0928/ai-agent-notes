# 全站健檢報告（2026-10）

- 範圍與日期：index.html 與 docs/*.md 產生的 21 個 pages/*.html，共 22 頁；2026-10-05 檢查。重跑：`python scripts/site_health.py`
- 連結：內部 1099 個（含錨點與資源檔）、外部 163 個不重複網址；發現 46、修 1、確認不需修改 1、留給人工 44
- 手機版（375×812）：22 頁；溢出 3 頁、修 3、留給人工 0；修正後 0 頁溢出
- 無障礙：22 頁；發現 22、修 22、留給人工 0
- build：無錯誤、無輸出警告；產物與 commit 只差 `data-updated` 時間戳（沒有人手改 HTML）；發現 2、修 0、留給人工 2
- 外部連結數量核對：docs 內出現 217 次、140 個不重複網址；直接用正規式數 docs/*.md 原文也是 217 次、140 個，與腳本實際請求的網址一致
- 本次只動連結、標題層級、Markdown 跳脫與 CSS，沒有改文章文字；pages/*.html 全部由 build.py 重新產生

## 檢查方式

- 腳本：`scripts/site_health.py`。它把整個 repo 複製到暫存目錄再跑 build.py，工作目錄不會被改到；所有檢查都對暫存目錄的產出進行。
- 內部連結：解析每頁 HTML 的 `href`／`src`，確認檔案存在、`#錨點` 對得到目標頁的 `id`。另外檢查 Markdown 表格有沒有某一列欄數多於表頭（多出的欄會被 Python-Markdown 直接丟掉）。
- 外部連結：先 HEAD，失敗再 GET；逾時 15 秒；User-Agent 用一般 Chrome 的字串。分類為正常、404/410、跳到別的網域、逾時、403/429（需人工確認）、連線錯誤，以及「執行環境擋住」（見下）。`doi.org` 本來就是轉址服務，轉到出版社網域算正常。
- 手機版：Playwright（Chromium）以 375×812 開每一頁，比較 `document.documentElement.scrollWidth` 與 `window.innerWidth`，再找出右緣超出畫面、而且不在可捲動容器裡的最內層元素。
- 無障礙：同樣用 Playwright 開頁（1280×900），在亮色與暗色兩種 `prefers-color-scheme` 下檢查 html lang、img alt、標題跳級、連結文字、表單控制項名稱，以及每個有文字的元素實際算出來的文字色與背景色對比（一般文字 4.5:1，大字 3:1；背景由下往上合成，漸層底色也算）。
- build：一般執行 `python build.py` 看輸出；另外用 `python -W default build.py` 打開 Python 警告再跑一次；最後逐檔比對產物與 repo 裡的版本。

## 一、連結

內部連結：修正前 1091 個、修正後 1099 個（多出的 8 個是改成 h3 後新出現在「本頁目錄」裡的錨點），全部指得到存在的檔案與標題，沒有需要修的。另有 140 個連結指向的錨點是 Python-Markdown 依標題順序自動編的（`#_5`、`#42` 這類，中文標題沒有英數字可用時產生），目前都對得上，但前面增刪標題就會指錯，列在「留給人工」。

外部連結數量：docs 內出現 217 次、140 個不重複網址；直接用正規式數 docs/*.md 原文也是 217 次、140 個；樣板（build.py 產生的頁首、頁尾等處）另有 44 次、23 個不重複網址，全部正常。腳本實際請求 163 個不重複網址。

本次結果：403/429（需人工確認） 2、執行環境擋住 41、正常 118、跳到別的網域 1、連線錯誤 1（「跳到別的網域」等數字是修正後的重跑結果，已替換的連結不在其中）。

下表列出所有不是「正常」的連結，加上已修正的項目：

| 頁面（來源） | 連結 | 狀態 | 處置 |
|---|---|---|---|
| pages/harness.html（docs/harness.md:255） | https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code | 跳到別的網域：301 永久轉址 → claude.dev | **已替換**為 https://claude.dev/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code/ 。確認依據：(1) 轉址由 claude.com 自己以 301 發出；(2) 新頁標題與 H1 都是「A harness for every task: dynamic workflows in Claude Code」，和本站引用的篇名相同；(3) 新頁 canonical 就是這個網址。同一網址在 harness.md:24 的縮排程式碼區塊裡以純文字出現，不是連結，屬內文，沒有改 |
| docs/claude-codex.md:261、docs/claude-codex.md:98 | https://developers.openai.com/codex/cli/reference | 跳到別的網域：308 永久轉址 → learn.chatgpt.com/docs/developer-commands?surface=cli | 沒有替換，留給人工。新頁標題改成「Developer commands」，不能確定和原本的「Codex CLI reference」是同一份文件；而且 claude-codex.md:98 的內文已寫明「會轉址到 learn.chatgpt.com/docs/developer-commands」，換網址會讓這句說明失準 |
| docs/mcp.md:160 | https://modelcontextprotocol.io/introduction | 連線錯誤：腳本執行時連線被重設 | 不需修改。用 curl 重測回 200（站內轉址到 /docs/2026-07-28/getting-started/intro），判定為暫時性；第一次執行時同站的 /docs/concepts/transports 也出現過同樣狀況，重測正常 |
| docs/sdlc-traditional.md:155 | https://doi.org/10.1145/12944.12948 | 403/429（需人工確認）：DOI 解析到 dl.acm.org 後回 403 | 沒有修改，需人工確認。網站擋自動化請求（多為 Cloudflare 等防護），不算壞連結；請用瀏覽器開啟確認 |
| docs/tools-catalog.md:64 | https://github.com/stablyai/orca/discussions/681 | 403/429（需人工確認）（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/claude-codex.md:15、docs/claude-codex.md:260、docs/claude-codex.md:81 | https://github.com/openai/codex-plugin-cc/blob/main/README.md | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/claude-codex.md:202 | https://github.com/openai/codex-plugin-cc/issues/639 | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/claude-codex.md:202 | https://github.com/openai/codex-plugin-cc/issues/704 | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/claude-codex.md:226 | https://github.com/openai/codex-plugin-cc/blob/main/README.md#enabling-review-gate | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/claude-codex.md:275 | https://github.com/openai/codex-plugin-cc/issues | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/claude-codex.md:32 | https://github.com/openai/codex-plugin-cc/blob/main/README.md#requirements | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/claude-codex.md:66 | https://github.com/openai/codex-plugin-cc/blob/main/README.md#install | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/dev-practices.md:160、docs/sdlc-ai-agent.md:161、docs/tools-catalog.md:62 | https://github.com/github/spec-kit | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/mcp.md:166 | https://github.com/anthropics/claude-code/issues/46360 | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/mcp.md:167 | https://github.com/microsoft/playwright-mcp/issues/1540 | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/mcp.md:33 | https://github.com/upstash/context7 | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/sdlc-ai-agent.md:162 | https://github.com/github/spec-kit/blob/main/spec-driven.md | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/sdlc-ai-agent.md:167、docs/sdlc-ai-agent.md:27、docs/tools-catalog.md:63 | https://github.com/Fission-AI/OpenSpec | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/skill-build.md:153、docs/skill-build.md:227、docs/skill-build.md:347、docs/skill-build.md:7 | https://github.com/wayhong0928/mis-thesis-skills | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:108 | https://api.github.com/repos/amitshekhariitbhu/ai-system-design | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:18 | https://github.com/NVIDIA/SkillSpector | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:36 | https://github.com/anthropics/skills | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:37 | https://github.com/anthropics/claude-plugins-official | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:38 | https://github.com/openai/codex-plugin-cc | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:39 | https://github.com/anthropics/claude-cookbooks | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:48 | https://github.com/ChromeDevTools/chrome-devtools-mcp | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:49 | https://github.com/modelcontextprotocol/inspector | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:59 | https://github.com/blader/humanizer | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:60 | https://github.com/forrestchang/andrej-karpathy-skills | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:61 | https://github.com/wshobson/agents | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:64 | https://github.com/stablyai/orca | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:72 | https://github.com/cathrynlavery/diagram-design | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:73 | https://github.com/fredrick84823/fstack | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:74 | https://github.com/jasnell/opencode-skill-ascii-art-diagrams | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:75 | https://github.com/HelioFernandes404/ascii-diagrams-skill | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:84 | https://github.com/hesreallyhim/awesome-claude-code | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:85 | https://github.com/VoltAgent/awesome-agent-skills | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:86 | https://github.com/bojieli/ai-agent-book | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:87 | https://github.com/shareAI-lab/learn-claude-code | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:88 | https://github.com/datawhalechina/hello-agents | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:89 | https://github.com/WenyuChiou/awesome-agentic-ai-zh | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:90 | https://github.com/clayzhang-TW/claude-academic-workflow-zh | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:91 | https://github.com/1weiho/open-slide | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:92 | https://github.com/the911fund/skill-of-skills | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:93 | https://github.com/keyuchen21/agentic-engineering-handbook | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |
| docs/tools-catalog.md:94 | https://github.com/amitshekhariitbhu/ai-system-design | 執行環境擋住（github.com 回 403） | 沒有修改，需人工確認。這個雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址一律回 403，腳本無法判斷連結是否有效；請在一般網路環境重跑腳本 |


## 二、手機版溢出（375×812）

修正前 3 頁溢出，修正後 0 頁。

| 頁面 | 元素 | 處置 |
|---|---|---|
| pages/claude-code-obsidian.html（docs/claude-code-obsidian.md） | 行內 `<code>`：`.claude/agents/`（scrollWidth 475px，元素右緣 460px） | **已修**：assets/style.css 加 `.doc { overflow-wrap: break-word; }`，沒有空白可斷的長字串改成在字中換行；重測 scrollWidth = 375 |
| pages/claude-code-obsidian.html（docs/claude-code-obsidian.md） | 行內 `<code>`：`CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`（scrollWidth 475px，元素右緣 400px） | **已修**：assets/style.css 加 `.doc { overflow-wrap: break-word; }`，沒有空白可斷的長字串改成在字中換行；重測 scrollWidth = 375 |
| pages/hooks-subagents.html（docs/hooks-subagents.md） | 行內 `<code>`：`"${CLAUDE_PROJECT_DIR}/.claude/hooks/xxx.sh"`（scrollWidth 384px，元素右緣 384px） | **已修**：assets/style.css 加 `.doc { overflow-wrap: break-word; }`，沒有空白可斷的長字串改成在字中換行；重測 scrollWidth = 375 |
| pages/subagent.html（docs/subagent.md） | 行內 `<code>`：`CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS=1`（scrollWidth 384px，元素右緣 384px） | **已修**：assets/style.css 加 `.doc { overflow-wrap: break-word; }`，沒有空白可斷的長字串改成在字中換行；重測 scrollWidth = 375 |
| pages/subagent.html（docs/subagent.md） | 行內 `<code>`：`CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS=1`（scrollWidth 384px，元素右緣 384px） | **已修**：assets/style.css 加 `.doc { overflow-wrap: break-word; }`，沒有空白可斷的長字串改成在字中換行；重測 scrollWidth = 375 |

## 三、無障礙

| 頁面 | 問題 | 處置 |
|---|---|---|
| 全部 22 頁 | html lang、img alt、連結文字 | 沒有問題：每頁都有 `lang="zh-Hant"`；沒有缺 alt 的圖片；沒有「這裡」「點此」之類的連結文字 |
| pages/tools-compare.html（docs/tools-compare.md:27–83） | 標題跳級：h2「逐介面細節」下面直接接 8 個 h4（Claude Chat、Claude Desktop、Cowork、Claude Code、Claude Design、ChatGPT、ChatGPT Desktop、Codex） | **已修**：8 個 `####` 改成 `###`，文字不變。標題 id 沒有變（既有錨點照常可用）；副作用是這 8 個標題現在會出現在右側「本頁目錄」，字級與顏色變成 h3 樣式 |
| 全站（側欄分區標題、站名小字、麵包屑、頁尾、本頁目錄標題、首頁分區說明與編號） | 對比不足：亮色：`--ink-faint` #8b857a 在 #fbfaf7／#f3f1eb／#ffffff 上只有 3.24–3.66:1 | **已修**：`--ink-faint` 改 #706b62（同色相調暗），對比 4.61–5.29:1 |
| 全站（同上） | 對比不足：暗色：`--ink-faint` #857f74 在側欄 #1e1d1a 上 4.24:1、在面板 #1c1b18 上 4.33:1 | **已修**：暗色 `--ink-faint` 改 #8f8a7f，對比 4.62–5.31:1 |
| 有提示框的頁面 | 對比不足：提示框標題（warning／danger）用框線色 `--warn-rule` 當文字色：亮色 #d9a45b 對 #fdf3e7 只有 2.03:1；暗色 #a8763a 對 #2c231a 3.9:1；標題裡的 `<code>` 也一樣 | **已修**：新增文字專用的 `--warn-ink`（亮 #916222、暗 #b98240，對比 4.82／4.65:1），框線仍用 `--warn-rule` |
| 有提示框的頁面 | 對比不足：提示框標題（tip／note）用 `--ok-rule`：亮色 #7fa06f 對 #eef5ec 2.64:1；暗色 #5f7a52 對 #1e2a1e 3.13:1 | **已修**：新增 `--ok-ink`（亮 #58734c、暗 #779866，對比 4.76／4.6:1），框線不變 |
| 全站 | 對比不足：「跳到主要內容」連結（鍵盤 Tab 時出現）：暗色是白字 #fff 配 `--accent` #d9a173，2.26:1 | **已修**：文字色改 `var(--panel)`，亮色仍是白字（7.39:1），暗色變深色字（7.62:1） |

修正後重跑：對比不足 0 組、標題跳級 0、缺 alt 0、缺 lang 0。

## 四、build

| 項目 | 結果 | 處置 |
|---|---|---|
| `python build.py` | 結束碼 0，沒有警告或錯誤訊息 | — |
| `python -W default build.py` | 每讀一個來源檔出現一次 `ResourceWarning: unclosed file`：build.py 第 248 行的 `open(...).read()` 沒有關檔 | 不影響產物。沒有修改，留給人工 |
| 產物與 commit 比對 | 修正前：22 個檔只差 `data-updated="…"` 時間戳，其餘內容逐位元相同，沒有手改過的 HTML | 這次重新 build，時間戳已同步；成因在 build.py，留給人工（見下） |
| 修正後比對 | 23 個產物與工作目錄完全相同 | — |

## 留給人工

1. **外部連結：44 筆**（明細與各自的理由見第一節表格「處置」欄）。共通原則：找不到能確認是同一份文件的官方新網址就不替換；403/429 是網站擋機器人，不算壞連結，需要用瀏覽器確認。
2. **github.com 連結無法在這個環境檢查**：雲端執行環境的 GitHub 代理只開放本次作業的 repo，其餘 github.com 網址都回 403。這不是 GitHub 的回應，所以不能判定壞掉，也不能判定正常；請在一般網路環境執行 `python scripts/site_health.py --skip-browser` 重測。
3. **指向自動編號錨點的連結（140 個）**：目前都有效，但 `#_5` 這種 id 依標題出現順序產生，前面多一個或少一個中文標題就會整批位移、指到錯的段落。根治要在 build.py 設定 toc 的 `slugify`（例如保留中文字），屬於建置邏輯變更，而且會改掉所有現有錨點，需要人工決定。腳本的 JSON 輸出（`--json`）有完整清單。
4. **`data-updated` 時間戳每次提交都會落後**：build.py 用「來源檔最後一次 git 提交時間」當時間戳，但 HTML 是在提交前產生的，所以 commit 裡的 HTML 永遠記著上一次的時間，下一次任何人重建都會出現一批只有時間戳的變動。要改得改 build.py 的設計（例如改用檔案內容的雜湊判斷、或提交後再重建一次），超出這次可以自動修的範圍。腳本比對時已把這種差異和真正的內容差異分開。
5. **build.py 的 `ResourceWarning`**：改成 `with open(...) as f:` 即可，但這是建置程式碼，不在這次允許修改的範圍。

## 這次沒有檢查的部分

- 「soft 404」：網站回 200 但內容已經換成別的頁面，自動檢查看不出來。
- 滑鼠移過（hover）與鍵盤焦點狀態的對比只檢查了「跳到主要內容」連結；其他 hover 樣式沒有算。
- 手機版是在容器裡的 Chromium 跑的，系統中文字型是文泉驛正黑，不是 style.css 指定的思源黑體；字寬略有差異，所以溢出的修法用 `overflow-wrap`，不依賴特定字寬。
- 錯字與文章觀點不在本次範圍。
