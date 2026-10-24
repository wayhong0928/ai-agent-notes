# Checkpoints 與 `/rewind`：哪些能復原、哪些不能

> 查證日期：2026-10-24。方案與功能變動快，請以官方最新說明為準。

Claude 改壞了檔案、走錯方向，或對話拖太長，Claude Code 有一個內建的退路叫 checkpoint，用 `/rewind` 打開。它很好用，但只管 Claude 用檔案編輯工具改的東西，有幾種情況復原不了。這頁先講它怎麼運作，再列清楚哪些能復原、哪些要靠 Git，最後給幾個常見情境的操作順序。內容來自官方文件[1][2]，本站自己的整理會另外註明。

## 一、checkpoint 什麼時候建立、留多久

官方的說法是，Claude Code 會自動追蹤它的檔案編輯工具所做的修改，每次你送出一個會開始一輪的 prompt，就建立一個新的 checkpoint[1]。

- 檔案快照最多保留最近 100 個 checkpoint。較舊的 checkpoint 被丟掉時，沒有其他 checkpoint 還在用的快照檔會一併刪除，但每個檔案的第一份快照例外，VS Code 擴充套件要拿它當 session diff 的基準[1]。
- checkpoint 跟對話一起存，所以接續舊 session 之後還是可以 `/rewind`[1]。
- 快照有保存期限。Claude Code 的定期清理預設在 session 最後一次存快照之後約 30 天刪除它。想倒回快照已被清掉的 checkpoint，可能失敗並出現 `No files were restored`。想保留更久，調 `cleanupPeriodDays` 設定[1]。

## 二、怎麼打開 rewind 選單

跑 `/rewind`，或在輸入框是空的時候連按兩下 `Esc`[1]。`/rewind` 另有兩個別名，`/checkpoint` 和 `/undo`[2]。

輸入框裡已經有字的話，連按兩下 `Esc` 會變成清掉輸入，不會開選單。被清掉的文字會存進輸入歷史，離開選單之後按 `Up` 可以叫回來[1]。

## 三、選單裡的六個動作

選單會列出這個 session 裡你送過的 prompt。先選定要回到哪一點，再選動作[1]。

| 動作 | 做什麼 |
|---|---|
| Restore code and conversation | 程式碼和對話都退回那個時間點 |
| Restore conversation | 對話退回那則訊息，目前的程式碼保留 |
| Restore code | 還原檔案的修改，對話保留 |
| Summarize from here | 把這一點之後的對話壓成摘要，騰出 context window 空間 |
| Summarize up to here | 把這一點之前的對話壓成摘要，後面的訊息原樣保留 |
| Never mind | 回到訊息清單，什麼都不改 |

兩個還原程式碼的選項，只有在所選的 checkpoint 之後有被追蹤到的檔案修改時才會出現。沒有的話，選單只剩 Restore conversation、兩個 Summarize 和 Never mind[1]。

幾個操作細節[1]。

- 還原對話，或選了 Summarize from here 之後，被選中那則訊息的原文會放回輸入框，讓你重送或修改。選 Summarize up to here 則停在對話最後面，輸入框是空的。
- 兩個 Summarize 都會在對話裡留下一個 Summarized conversation 標記。
- Summarize 不會動磁碟上的檔案，原本的訊息還留在 session 紀錄裡，Claude 仍能參照細節。
- 想指定摘要的重點，用方向鍵停在某個 Summarize 選項上，在 add context (optional) 那一行打字再按 `Enter`。直接按該選項的數字鍵，就不帶指示立刻摘要。

Summarize 留在同一個 session 裡壓縮 context，像是指定範圍的 `/compact`。想分出另一條路試別的做法、又要保住原本的 session，官方建議改用 `/branch` 或 `claude --continue --fork-session`[1]。

## 四、哪些能復原、哪些不能

| 情況 | 能不能用 `/rewind` 復原 | 官方怎麼說 |
|---|---|---|
| Claude 用檔案編輯工具改的檔案 | 能 | 這是 checkpoint 追蹤的主要對象[1] |
| 一個 Claude 已經編輯過的檔案，之後被 Bash 指令改了 | 能 | Claude 在對話裡用檔案編輯工具改過某個檔之後，`/rewind` 會連同它之後被 Bash 指令做的修改一起還原[1] |
| 只被 Bash 指令改過、Claude 沒用編輯工具碰過的檔案 | 不能 | 不追蹤，檔案維持現狀，要還原就用 Git 這類版本控制[1] |
| 你自己在 Claude Code 外面改的檔案、其他同時開著的 session 做的修改 | 通常不能 | checkpoint 只追蹤目前 session 編輯過的檔案；剛好改到同一個檔案的情況除外[1] |
| subagent 做的修改 | 多半不能 | 見下方說明[1] |
| 符號連結（symlink）或硬連結（hard link）的檔案 | 不能 | 還原時會跳過，顯示 `Restored the code, but skipped N files`，跳過的檔案內容不變[1] |
| 你在 Claude 還在工作時中途送出的訊息 | 那則訊息本身沒有 checkpoint | 選單裡可能標成 No code restore，見下方說明[1] |

subagent 的部分，官方的說法是 subagent 用 Claude 的檔案編輯工具做修改，但 Claude Code 通常不會把這些修改記進你 session 的 checkpoint。還原得了多少，要看 subagent 怎麼跑[1]。

- 在前景執行的 forked skill（`context: fork`）改的是你自己這一輪的工作目錄，所以照常還原。
- 其他 subagent，包含在背景執行的 forked skill（這是預設）和背景執行的 `/code-review --fix`，只會還原 Claude 在你的對話裡已經編輯過的檔案，subagent 改到的其他檔案要用 Git 退。

中途送出的訊息，官方說 checkpoint 是替「開始一輪」的 prompt 建立的，所以這則訊息沒有自己的 checkpoint，Claude 讀到它之後做的修改，算在開始那一輪的 prompt 名下。要退掉這段修改，選開始那一輪的 prompt，再選 Restore code 或 Restore code and conversation。這會把整輪的檔案修改都還原，包含你的訊息送出之前的部分。選有標記的那則訊息，仍然可以用 Restore conversation，只退對話、檔案不動[1]。

想知道還原時跳過了哪些路徑，還原之前先用 `/debug` 開除錯紀錄，紀錄檔會列出每個被跳過的路徑[1]。

官方最後一句提醒值得照字面讀。Checkpoint 是給 session 內快速復原用的，要永久的版本歷史和協作，繼續用 Git 這類版本控制做 commit 和分支[1]。

## 五、幾個常見情境怎麼做

### Claude 改壞了，想回到改之前

1. 輸入框清空，連按兩下 `Esc`，或打 `/rewind`。
2. 選那個改壞的要求本身的那則 prompt。checkpoint 記的是每則 prompt 送出前的狀態，選它就回到那次修改之前[1]。
3. 想連對話一起退，選 Restore code and conversation。想保住對話、只把檔案退回去，選 Restore code。
4. 有還原對話時，那則 prompt 的原文會回到輸入框，可以改一改再送；只選 Restore code 時對話不動[1]。

### 倒回去之後直接關掉視窗

官方提醒，倒回去的訊息在你送下一個 prompt 之前就離開的話，可能會回來。要把它們再移掉，進同一個 session 跑 `/rewind`、選同一則 prompt、再選 Restore conversation。預防的做法是離開前先送 Claude 一個 prompt，因為 Claude Code 是把倒回後的對話連同這個 prompt 一起存下來。已經還原的檔案會維持還原後的樣子[1]。

### 不小心打了 `/clear`

同一個 Claude Code 程序裡跑過 `/clear` 的話，rewind 選單最上面會多一個 `/resume <session-id> (previous session)` 項目，選它就回到 `/clear` 之前的對話。這個項目在你離開 Claude Code 或接續別的 session 之前都在[1]。`/clear` 的說明本身也提到這個管道[2]。

### 除錯對話拖很長，想壓縮中段

選中段那一點的 Summarize from here，初始指示留著、後面冗長的來回壓成摘要。這是官方列的用途之一[1]。要補充摘要重點的做法見第三節。

### 想動檔案的 Bash 指令或 subagent 之前

這一條是本站的整理，不是官方規定。上面的表顯示，只被 Bash 指令或 subagent 動過的檔案不在 checkpoint 的保護範圍，所以讓 Claude 做這類事情之前，先確認工作目錄在 Git 裡、而且目前的狀態已經 commit，出事時才有地方退。

## 本頁重點回顧

- 每個開始一輪的 prompt 建一個 checkpoint，最多留最近 100 個，快照約 30 天後被清理。
- `/rewind` 或空輸入框時連按兩下 `Esc` 打開選單，有三個還原選項、兩個摘要選項和一個取消。
- 能退的是 Claude 用編輯工具改的檔案，以及這些檔案之後被 Bash 改的部分。只被 Bash 改的檔案、你自己改的、其他 session 改的、多數 subagent 改的、symlink 和 hard link，都要靠 Git。
- 倒回去之後離開前先送一個 prompt，否則被倒掉的訊息可能回來。
- Checkpoint 是 session 內的快速復原，不取代版本控制。

## 資料來源

| 標記 | 來源 | URL |
|---|---|---|
| [1] | Checkpointing（checkpoint 的建立與保留、`/rewind` 選單、限制） | <https://code.claude.com/docs/en/checkpointing> |
| [2] | Commands（`/rewind`、`/clear` 的說明與別名） | <https://code.claude.com/docs/en/commands> |

延伸：[新手指令速查](commands-cheatsheet.md)｜[Claude Code 設定總覽](official-config.md)｜[跨 session 接力：session_log](session-handoff.md)
