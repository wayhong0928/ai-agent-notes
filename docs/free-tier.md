# 免付費區

> 查證日期：2026-09-16。方案與功能變動快，請以官方最新說明為準。

免費帳號能做的事，比多數人想的多一些，但也有幾個明確做不到的邊界。這頁只講「不花錢能做到哪裡」；需要付費才能解鎖的部分，見[付費區](paid-tier.md)；不確定該用哪個介面，先看[AI 介面比較總表](tools-compare.md)。

## Claude Free 能用什麼

| 功能 | 狀態 | 備註 |
|---|---|---|
| Claude Chat（網頁／手機） | ✅ | 一般對話，Free 就有 [S3][S15] |
| Artifacts | ✅ | 不是付費限定，Free 就能產生可互動內容 [S3] |
| 網路搜尋 | ✅ | Free 即有 [S3] |
| Skills | ✅ | 需要另外開啟 code execution [S9][S9b] |
| Memory | ✅ 預設開啟 | Free／Pro／Max 都預設開，Team／Enterprise 要管理員開 [S10] |
| Connectors（remote MCP） | ⚠️ 限 1 個自訂 connector | Pro 起數量更多但官方未列確切上限 [S12] |
| Projects | ❌ | Free 沒有這個功能 [S3][S4] |
| Research | ❌ | 官方明寫僅付費方案（Pro/Max/Team/Enterprise）[S14] |
| Cowork | ❌ | 免費帳號完全不能用；官方已公告 Cowork 併入一般 Chat 的新體驗會擴及 Free 方案，但目前只是「即將推出」，尚未開始 [S21][S26] |
| Claude Code | ❌ | Free 沒有，Pro 起才有，見[付費區](paid-tier.md) [S1] |

## ChatGPT Free 能用什麼

| 功能 | 狀態 | 備註 |
|---|---|---|
| ChatGPT 網頁版／手機 App | ✅ | [A2 §1] |
| Desktop App（Chat／Work／Codex 三種模式） | ✅ | 官方明說桌面 App 對所有方案（含 Free）開放 Chat、Work、Codex [O3][O7] |
| Projects | ✅ 5 檔／專案 | 檔案數上限比付費方案低（Plus 25 檔、Pro 40 檔）[O17] |
| Canvas | ✅ | 功能與付費方案一致 [O18] |
| 網路搜尋 | ✅ | 未公開確切次數上限 [O20] |
| Deep Research | ✅ 輕量版 | 額度比 Plus／Pro 少 [O21] |
| Connectors／Apps | ⚠️ 僅內建 App，不能加自訂 connector 或 MCP | Plus 起才有 Developer Mode 可加自訂 MCP [O22] |
| Memory | ✅ 預設開啟 | [O24] |
| 檔案上傳 | ⚠️ 512MB／檔，但頻率約 3 次／天 | Plus 約 80 次／3 小時，Pro 幾乎無限 [O19] |
| Codex | ✅ 可用，但各介面深淺不同 | 見下方專節 |

### Free／Go 帳號用 Codex 要注意的地方

官方對 Free／Go 帳號能不能用 Codex，本身在不同文件上出現過落差：定價頁把 Free（$0）與 Go（$8）都列為 Codex 的方案，文案分別是「探索 Codex 在小型程式任務上的能力」「用 Codex 處理輕量程式任務」；但 Codex CLI 所在的 GitHub 專案 README，登入建議文字只列出 Plus、Pro、Business、Edu、Enterprise，沒有提到 Free／Go。查證後確認官方並沒有真的排除 Free／Go。GitHub README 那段文字是「建議」用語，沒有寫「僅限」，屬於列舉不完整，不是禁止規定；桌面 App 的官方頁面也明確把 Codex 分頁列為所有方案（含 Free）都能用的功能 [A2 §0][A2b 題5]。

!!! note "看到「Codex 只有付費方案能用」這種舊教學，先查一次現況"
    這條資訊的性質是「官方文件彼此打過架，後來查證確認是舊文件沒跟上」，不是單純的功能限制。教學網站或部落格如果還在講 Free／Go 不能用 Codex，很可能是抄了那份沒更新的 GitHub README。

## 兩個免費帳號可行的工作流程

### 流程一：Claude Free + 手動貼上文獻摘要

Claude Free 沒有 Projects，沒辦法把一批文獻或寫作規範固定成一個持久的知識庫，每次新對話都要重新提供脈絡。可行的做法：

1. 把要討論的文獻摘要、規範或前一輪結論整理成一段文字，貼在對話開頭當「這次要用的脈絡」。
2. 一次只處理一個具體問題（例如「幫我比較這三篇的研究方法差異」），不要指望它記得上一次對話。
3. 需要長期保留脈絡時，把重要結論另外存到自己的筆記檔案裡，不要依賴 Claude 的記憶。Free 雖然有 Memory 預設開啟 [S10]，但那是跨對話的一般偏好記憶，不是 Projects 等級、可掛文件的知識庫。

### 流程二：ChatGPT Free 桌面 App 的 Codex 分頁做小型程式任務

1. 安裝統一版 ChatGPT Desktop App，登入 Free 帳號，切到 Codex 分頁 [O7]。
2. 針對範圍明確、單一檔案或小型腳本的任務下指令（例如「幫我寫一個整理 CSV 的 Python 腳本」），不要一次丟整個大型專案，因為 Free 帳號的定位就是「quick coding tasks」[O1]。
3. Codex 依 sandbox mode 決定能不能直接讀寫本機檔案與執行指令，第一次使用時注意它問你的權限確認，不要看到「建議」就一律同意 [O25]。

## 免費版常見的坑

!!! warning "Connectors 只能接 1 個"
    Claude Free 的自訂 connector（remote MCP）上限是 1 個，不是「先接看看，之後再加」。如果你的工作流程需要同時接文獻管理器、雲端硬碟、資料庫，免費帳號會卡在這裡，得先想清楚優先接哪一個 [S12]。

!!! warning "ChatGPT Free 的 Projects 只有 5 個檔案額度"
    比 Plus（25 檔）少很多，一個真實的研究專案很容易超過 5 個檔案。超過額度不是報錯就是要你砍舊檔案，開工前先盤點要放幾份檔案 [O17]。

!!! warning "Claude Code、Cowork 完全不能用免費帳號"
    這兩個經常被搞混的功能都需要付費方案（Pro 起）。免費帳號想找「本機讀寫檔案」「跨檔批次處理」的功能，會發現無論怎麼設定都用不到，因為不是設定錯了，是方案本身沒開放 [S1][S21]。（2026-09-16 官方公告 Cowork 正併入一般 Chat，但 Free 方案官方說法是「即將推出」，查證當下尚未開始，這條限制暫時還成立 [S26]）

!!! tip "檔案上傳有頻率上限，不是只看檔案大小"
    ChatGPT Free 的單檔大小上限雖然跟付費方案一樣是 512MB，但每天大概只能上傳 3 次；Claude Free 的檔案上傳沒有另外標注頻率限制，但受單次對話最多 20 檔、圖片與 PDF 頁數等其他上限影響 [O19][S16]。

## 資料來源（2026-09-16 查證）

| 標記 | URL | 用途 |
|---|---|---|
| S1 | support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan | Claude Code 方案門檻 |
| S3 | claude.com/pricing | 各方案功能總覽 |
| S4 | support.claude.com/en/articles/11049762-choose-a-claude-plan | 方案選擇指南 |
| S9 | support.claude.com/en/articles/12512180-use-skills-in-claude | Skills 使用方式 |
| S9b | support.claude.com/en/articles/12512176-what-are-skills | Skills 方案可用性 |
| S10 | support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context | Memory 各方案預設開關 |
| S12 | support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp | Free 自訂 connector 限 1 個 |
| S14 | support.claude.com/en/articles/11088861-use-research-on-claude | Research 僅付費方案 |
| S15 | support.claude.com/en/articles/8114487-what-interfaces-can-i-use-to-access-claude | 官方介面總覽 |
| S16 | support.claude.com/en/articles/8241126-upload-files-to-claude | 檔案上傳大小/數量限制 |
| S21 | support.claude.com/en/articles/13345190-get-started-with-claude-cowork | Cowork 免費帳號不可用 |
| S26 | support.claude.com/en/articles/16761823-claude-cowork-and-chat-are-one-claude | Cowork／Chat 合併現況：各方案推出時程 |
| O1 | learn.chatgpt.com/docs/pricing | Free/Go 的 Codex 定位文案 |
| O3 | OpenAI 官方 X 貼文（經二次來源引述） | Desktop app 全方案含 Free 可用 Codex |
| O7 | learn.chatgpt.com/docs/app | 統一版 Desktop app 分頁切換 |
| O17 | help.openai.com「Using Projects in ChatGPT」等（WebSearch 摘要） | Projects 各方案檔案數上限 |
| O18 | help.openai.com「What is the canvas feature」等（WebSearch 摘要） | Canvas 各方案可用性 |
| O19 | help.openai.com 檔案上傳相關文章（WebSearch 摘要，未能精確定位單一文號） | 檔案大小/頻率上限 |
| O20 | help.openai.com Free tier FAQ（WebSearch 摘要） | Free 網路搜尋無公開次數上限 |
| O21 | help.openai.com Deep Research 相關文章（WebSearch 摘要） | Deep Research 各方案額度差異 |
| O22 | help.openai.com/en/articles/11487775-connectors-in-chatgpt；12003714 | Connectors 各方案差異 |
| O24 | help.openai.com「Memory FAQ」（WebSearch 摘要） | Memory 各方案預設開關 |
| O25 | learn.chatgpt.com/docs/sandboxing | Codex sandbox 三模式 |

延伸：[AI 介面比較總表](tools-compare.md)｜[付費區](paid-tier.md)
