[繁體中文](README.md) | English

# AI Agent Notes

AI Agent Notes is a static website covering concepts, setup, and collaboration workflows for Claude, Codex, and other AI agent tools.

- Website: <https://wayhong0928.github.io/ai-agent-notes/>
- Source: <https://github.com/wayhong0928/ai-agent-notes>

**The site is in Traditional Chinese.** This page is the only English part.

## Building

Content lives in `docs/`; `build.py` generates the web pages. Edit `docs/*.md` first, build, check the output, then commit them together.

On Windows PowerShell, set the output encoding to UTF-8 when building, or the console's cp950 encoding will cause errors:

```powershell
$env:PYTHONIOENCODING='utf-8'; python build.py
```

```bash
python build.py
git add docs/ pages/ assets/index.json index.html
git commit
```

Install Python-Markdown before the first build:

```bash
python -m pip install markdown
```

## Directory structure

```text
.
├─ assets/
│  ├─ style.css       # Site-wide styles
│  ├─ site.js         # Navigation, filters, and checkbox behavior
│  └─ index.json      # Build output: search index
├─ docs/                   # Markdown content source
├─ pages/                  # Build output: page HTML
├─ build.py                # Static site builder and navigation definition
└─ index.html              # Build output: home page
```

## Markdown conventions

`build.py` uses the Python-Markdown extensions `extra`, `toc`, `sane_lists`, and `admonition`.

**Callouts**:

```markdown
!!! warning "標題"
    內容需縮排四個空格。

!!! tip "標題"
!!! note "標題"
!!! danger "標題"
```

The body of a callout must be indented four spaces.

**Checklists**:

```markdown
- [ ] 這一項會變成網頁上可以勾選的核取方塊
- [x] 預設打勾
```

Each `- [ ]` item becomes a checkbox on the page; `- [x]` starts checked. Checkbox state is stored in the browser's `localStorage`, so it only applies to that browser on that device and disappears when site data is cleared.

**Links between pages**: write relative links to `.md` files; the build converts them to `.html`.

```markdown
見[文獻回顧](literature.md)
```

**The H1 on each page is removed.** Page titles come from `NAV` in `build.py`, so the `# Title` at the top of a `.md` file is only for Obsidian.

## Pre-push check

```bash
# Check for mainland Chinese terms
grep -rnE "被試|數據收集|信息|回歸分析|結果表明|人工智能|用戶|(^|[^演])算法|數據庫|優化|場景|默認|受眾" docs/
```
