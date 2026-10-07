# 關於這個網站

這是個人整理筆記，不是官方文件；工具與方案變動很快，每頁標註查證日期，請以官方最新說明為準

## 更新紀錄

| 日期 | 內容 |
|---|---|
| 2026-09-16 | 建立網站骨架 |
| 2026-09-19 | **新頁**：[Projects 功能](projects.md)、[Claude Code + Cowork 並用](claude-code-cowork.md)、[Claude Code 接上 Obsidian](claude-code-obsidian.md)。**擴充**：[AI 介面比較總表](tools-compare.md)新增「ChatGPT 一般對話 vs Codex」一節；[Claude Code × Codex](claude-codex.md)補上 workspace 信任判斷；[Harness](harness.md)補三組範例。**更正**：Claude Free 其實可以用 Projects（上限 5 個），先前寫成沒有，[免付費區](free-tier.md)、[付費區](paid-tier.md)已修正；Cowork 併入一般對話屬於分階段推出，相關頁面都加上說明。**排版**：[AI 介面比較總表](tools-compare.md)與[擴充機制比較](extensions.md)的大表拆成精簡總表加逐項說明；SDLC 三頁的引用格式統一。**新增**：[Claude Code 設定總覽](official-config.md)補上 v2.1.277 起讀取 AGENTS.md 的規則說明。新頁：[MCP 入門與實戰](mcp.md)。新頁：[好用工具清單](tools-catalog.md)。新頁：[Subagent 入門與實戰](subagent.md)。 |
| 2026-09-25 | **擴充**：[好用工具清單](tools-catalog.md)補入 4 項：官方 Skill 區加上 `claude-api` skill 內建的 `/claude-api prompt-audit`；社群 Skill 區加上 OpenSpec 與 Orca；學習資源區加上 skill-of-skills 工具目錄與 agentic-engineering-handbook 學習路線，各列附 2026-09-25 查證數字與來源。[AI 代理時代的 SDLC](sdlc-ai-agent.md)的規格驅動開發一節補上 OpenSpec。 |
| 2026-10-03 | **擴充**：[好用工具清單](tools-catalog.md)學習資源區補入 `amitshekhariitbhu/ai-system-design` 系統設計閱讀資料，附 2026-10-03 查證數字與來源，並註明 repo 建立日期、作者自家課程與部落格連結的限制。 |
| 2026-10-06 | **更新**：依 Claude 2026-10-06 的 Cowork 變動（Pro／Max 新任務一律在雲端執行，讀寫本機資料夾要桌面版開著、session 從桌面版開始），改寫[AI 介面比較總表](tools-compare.md)、[Claude Code + Cowork 並用](claude-code-cowork.md)、[Projects 功能](projects.md)、[付費區](paid-tier.md)、[免付費區](free-tier.md)、[Claude Code 接上 Obsidian](claude-code-obsidian.md)、[Claude Code + Codex 協作](claude-codex.md)、[SKILL、Plugin、MCP 與 Subagent](extensions.md)的相關段落，各處附查證日期與官方出處。Team／Enterprise 的 chat 與 Cowork 現況，官方部落格與說明頁寫法不同，以 2026-10-05 更新的說明頁為準。 |
| 2026-10-07 | **更新**：依官方說明頁 10-06 晚間的修訂重查[AI 介面比較總表](tools-compare.md)與[Claude Code + Cowork 並用](claude-code-cowork.md)：Cowork 任務改用「Download task data」加 `/port-task-data` 帶到 Claude Code；雲端 session 讀本機資料夾的條件補上排程任務（[Claude Code 接上 Obsidian](claude-code-obsidian.md)同步補上）；補上 Chrome 側邊欄入口。**更正**：Codex 方案依官方定價頁重查，[免付費區](free-tier.md)、[付費區](paid-tier.md)、[AI 介面比較總表](tools-compare.md)改成 Free／Go 只列桌面 App、CLI 與 IDE 擴充從 Plus 起；先前寫 Free／Go 也能用 CLI 沒有根據。 |
