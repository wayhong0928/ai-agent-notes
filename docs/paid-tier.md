# 付費區

> 查證日期：2026-09-16。方案與功能變動快，請以官方最新說明為準。

這頁列出需要 Pro 以上、或者非得用 Claude Code／Codex 才做得到的功能。每項都標最低方案，並說明「為什麼免費帳號或純聊天介面做不到」。多數答案落在六個原因裡：能不能碰**本機檔案**、能不能**執行指令**、能不能讓 **skill 自動觸發**、能不能派出**subagent**、能不能掛 **hooks**、以及要不要 **Claude Code + Codex 協作**。免費帳號能做到的部分，見[免付費區](free-tier.md)；不確定該用哪個介面，先看[AI 介面比較總表](tools-compare.md)。

## 一個常見錯誤要先更正

網路上流傳「Claude Code 僅 Team／Enterprise 可用」的說法是錯的。官方有兩篇獨立文件分別對應 Pro/Max 與 Team/Enterprise，都明確寫「included」：Pro 與 Max 方案「現在都能用 Claude on the web、桌面、手機版**以及 Claude Code**，共用同一個訂閱」；Team 方案「每個席位都內含 Claude Code」。差別只在額度怎麼計算：Pro/Max 是跟 Chat 共用的訂閱額度，Team 是每席位額度，Enterprise 則分「usage-based（純按 API 用量計費）」與「seat-based（沿用 Team 式席位額度）」兩種 [S1][S2]。

## 功能對照：最低方案與為什麼

| 功能 | 最低方案 | 為什麼要 Claude Code／Codex 或付費方案才做得到 |
|---|---|---|
| 讀寫本機檔案、執行終端指令 | Claude Code：Pro 起（或純 API key 按量付費）；Codex：CLI/IDE 全方案，含 Free／Go，但官方文件對 CLI 端的說法目前不完全一致，細節見[免付費區的說明](free-tier.md#freego-codex) | Chat／ChatGPT 網頁版的「執行程式碼」是雲端沙盒工具，不會碰到你電腦上的檔案；只有 Claude Code 與 Codex CLI／IDE 是真的在本機終端跑，這是**本機檔案**與**執行指令**這兩個原因 [S7] |
| Projects（Claude） | Pro | Free 沒有 Projects，無法把文獻、規範、教授回饋做成持久知識庫 [S3][S4] |
| Research（Claude） | Pro | 官方明寫「Research is available for users with paid Claude plans」[S14] |
| Cowork | Pro | 需要本機或雲端 VM 執行環境，免費帳號完全不能用；2026-09-16 起官方正把 Cowork 併入一般 Chat，Pro／Max 帳號分階段收到新體驗，收到之後不必再特地切到 Cowork 模式 [S21][S26] |
| Claude Design | Pro（research preview，Enterprise 需管理員手動開啟） | 需要獨立的畫布編輯環境，目前仍是研究預覽階段功能 [S22] |
| Subagent（Task tool） | 跟著 Claude Code 存取權走，Pro 起 | Subagent 需要獨立的系統提示詞與工具限制，只存在於 Claude Code 這套 agent 架構裡，這是**subagent**這個原因 [S17] |
| Hooks | 跟著 Claude Code 存取權走，Pro 起 | Hooks 是在 Claude Code 特定事件（例如寫檔前、對話結束）自動觸發的機制，聊天介面沒有這種生命週期事件可以掛，這是**hooks**這個原因 [S18] |
| Plugins（含 Skill 打包發佈） | 跟著 Claude Code 存取權走，Pro 起；Codex Plugins 全方案不分級 | Claude Code 的 Plugin 可以把 skill 設成依任務描述自動觸發，不必每次手動貼指示，這是**skill 自動觸發**這個原因；Codex 側的 Plugin／Skill 機制則不分方案 [S19][O29] |
| Routines／Dispatch（排程、手機發任務給 Desktop） | Pro（research preview） | 排程需要背景執行環境，手機端 Dispatch 需要桌面版保持連線代為執行，這兩者都超出純聊天介面的能力範圍 [S7] |
| ChatGPT Work | 首波 Pro／Enterprise／Edu，Plus／Business 隨後滾動上線 | 跨 App、跨檔案的多步驟自動化，需要能連續執行數小時的 agent 環境 [O11] |
| Codex 更高額度、更快模型 | Pro（$100 起） | Free／Go 的 Codex 只到「輕量程式任務」等級，複雜任務需要更高額度與更快模型 [O1] |

## Claude Code 也能用 API 按量付費，不一定要訂閱

除了 Pro／Max／Team／Enterprise 這幾種訂閱方案，Claude Code 也支援純用 Anthropic API key 按量計費：設定好 `ANTHROPIC_API_KEY` 之後就直接用 API 費率計費，不吃訂閱額度，也不需要先辦訂閱 [S23]。這對只想偶爾跑一下 Claude Code、不想固定月費的人是另一條路，但要注意：純 API key 不含 claude.ai 網頁版的 Chat 存取，訂閱與 API 是分開計費的兩套權限 [S23b]。

## Claude Code + Codex 協作，只需要一段先知道

Claude Code 和 Codex 可以互相搭配：OpenAI 官方 GitHub 組織發布了一個給 Claude Code 用的 `codex-plugin-cc` plugin，裝好之後能在 Claude Code 裡直接叫 Codex 幫你做唯讀 review（`/codex:review`）、挑戰設計決策（`/codex:adversarial-review`）、接手修 bug（`/codex:rescue`），或是把整個 session 轉交給 Codex 繼續（`/codex:transfer`）。這條路需要本機裝好 Codex CLI 並完成登入，且走的是「Claude Code 主持任務、Codex 支援」的分工，跟反過來讓 Codex 呼叫 Claude 是兩件不同難度的事。完整安裝步驟、指令列表與現況查證，見[Claude Code + Codex 協作](claude-codex.md)（該頁另外撰寫）。

## 資料來源（2026-09-16 查證）

| 標記 | URL | 用途 |
|---|---|---|
| S1 | support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan | Claude Code 於 Pro/Max 的可用性、額度共用說明 |
| S2 | support.claude.com/en/articles/11845131-use-claude-code-with-your-team-or-enterprise-plan | Claude Code 於 Team/Enterprise 的可用性 |
| S3 | claude.com/pricing | 各方案功能總覽 |
| S4 | support.claude.com/en/articles/11049762-choose-a-claude-plan | 方案選擇指南 |
| S7 | code.claude.com/docs/en/overview | Claude Code 五種 surface 官方總覽、Dispatch/Routines 提及處 |
| S14 | support.claude.com/en/articles/11088861-use-research-on-claude | Research 僅付費方案 |
| S17 | code.claude.com/docs/en/sub-agents | Claude Code subagent 官方文件 |
| S18 | code.claude.com/docs/en/hooks-guide | Claude Code hooks 官方文件 |
| S19 | code.claude.com/docs/en/plugins | Claude Code plugins 官方文件 |
| S21 | support.claude.com/en/articles/13345190-get-started-with-claude-cowork | Cowork 方案可用性 |
| S26 | support.claude.com/en/articles/16761823-claude-cowork-and-chat-are-one-claude | Cowork／Chat 合併現況：各方案推出時程 |
| S22 | anthropic.com/news/claude-design-anthropic-labs | Claude Design 方案可用性、research preview 狀態 |
| S23 | support.claude.com/en/articles/12304248-manage-api-key-environment-variables-in-claude-code | 純 API key 跑 Claude Code 的計費機制 |
| S23b | support.claude.com/en/articles/9876003-i-have-a-paid-claude-subscription-pro-max-team-or-enterprise-plans-why-do-i-have-to-pay-separately-to-use-the-claude-api-and-console | 訂閱與 API/Console 各自獨立計費 |
| O1 | learn.chatgpt.com/docs/pricing | Codex 各方案定價與定位文案 |
| O11 | openai.com/index/chatgpt-for-your-most-ambitious-work/（WebSearch 摘要） | ChatGPT Work 各方案上線順序 |
| O29 | learn.chatgpt.com/docs/build-skills | Codex/ChatGPT Skills、Plugins 關係 |

延伸：[免付費區](free-tier.md)｜[AI 介面比較總表](tools-compare.md)｜[Claude Code + Codex 協作](claude-codex.md)
