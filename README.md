# AI Agent 筆記

「AI Agent 筆記」是一個靜態網站，用來整理 Claude、Codex 與 AI 代理工具的概念、設定與協作流程。

- 網站：<https://wayhong0928.github.io/ai-agent-notes/>
- 原始碼：<https://github.com/wayhong0928/ai-agent-notes>

## 建置方式

內容放在 `docs/`，網頁由 `build.py` 產生。建議流程是先修改 `docs/*.md`，再建置，確認產物後一併提交。

Windows PowerShell 建置時，請指定 UTF-8 輸出編碼，避免主控台的 cp950 編碼造成錯誤：

```powershell
$env:PYTHONIOENCODING='utf-8'; python build.py
```

```bash
python build.py
git add docs/ pages/ assets/index.json index.html
git commit
```

首次建置前需安裝 Python-Markdown：

```bash
python -m pip install markdown
```

## 目錄結構

```text
.
├─ assets/
│  ├─ style.css       # 全站樣式
│  ├─ site.js         # 導覽、篩選與核取方塊互動
│  └─ index.json      # 建置產物：搜尋索引
├─ docs/                   # Markdown 內容來源
├─ pages/                  # 建置產物：內頁 HTML
├─ build.py                # 靜態網站建置器與導覽定義
└─ index.html              # 建置產物：首頁
```

## Markdown 慣例

`build.py` 使用 Python-Markdown 的 `extra`、`toc`、`sane_lists`、`admonition` 擴充。

**提示框**：

```markdown
!!! warning "標題"
    內容需縮排四個空格。

!!! tip "標題"
!!! note "標題"
!!! danger "標題"
```

**可勾選的清單**：

```markdown
- [ ] 這一項會變成網頁上可以勾選的核取方塊
- [x] 預設打勾
```

勾選狀態存在瀏覽器的 `localStorage`，只在該裝置的該瀏覽器有效，清除網站資料就會消失。

**頁面之間的連結**：直接寫 `.md` 的相對連結，建置時會自動轉成 `.html`。

```markdown
見[文獻回顧](literature.md)
```

**每頁的 H1 會被移除**，標題統一由 `build.py` 的 `NAV` 提供，所以 `.md` 開頭的 `# 標題` 只是給 Obsidian 看的。

## 推送前檢查

```bash
# 檢查大陸用語
grep -rnE "被試|數據收集|信息|回歸分析|結果表明|人工智能|用戶|(^|[^演])算法|數據庫|優化|場景|默認|受眾" docs/
```
