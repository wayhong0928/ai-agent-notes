#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 docs/*.md 產生 pages/*.html。
用法：python3 build.py
需求：pip install markdown
"""
import os
import re
import json
import html
import subprocess
import markdown
from markdown.extensions.toc import slugify_unicode

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")
PAGES = os.path.join(ROOT, "pages")
SITE_URL = "https://wayhong0928.github.io/ai-agent-notes/"
REPO_URL = "https://github.com/wayhong0928/ai-agent-notes"

# (檔名, 標題, 一句話說明)
NAV = [
    ("先搞懂工具", [
        ("tools-compare", "AI 介面比較總表", "Claude Code、Claude Chat、Claude Desktop、Codex、ChatGPT Desktop 一張表看懂"),
        ("free-tier", "免付費區", "不付錢也做得到的 AI 輔助工作流程"),
        ("paid-tier", "付費區", "需要 Pro 以上或 Claude Code／Codex 才能做到的功能"),
        ("projects", "Projects 功能", "舊版知識庫、新版 beta、Claude Code 本機專案，三種「Projects」分清楚"),
    ]),
    ("AI Agent 原理", [
        ("agent-basics", "AI Agent 怎麼運作", "代理迴圈、工具呼叫與上下文"),
        ("extensions", "SKILL、Plugin、MCP 與 Subagent", "四種擴充機制各自解決什麼問題"),
        ("subagent", "Subagent 入門與實戰", "frontmatter 全欄位、background／isolation: worktree 實際行為、SendMessage 續問、多代理成本"),
        ("mcp", "MCP 入門與實戰", "五分鐘裝好第一個、scope／OAuth 怎麼選、Windows 踩坑實錄"),
        ("tools-catalog", "好用工具清單", "精選審查過的官方文章、skill、plugin、MCP 與學習資源"),
        ("harness", "把 AI 代理的工作環境設計得可靠", "官方 harness 原則、驗證分級、多代理成本"),
    ]),
    ("實戰協作", [
        ("claude-codex", "Claude Code + Codex 協作", "官方 plugin、直接呼叫 CLI、Cowork 的現況"),
        ("skill-build", "把教材做成 SKILL", "安裝版與手動版的實作紀錄"),
        ("claude-code-obsidian", "Claude Code 接上 Obsidian", "四條路徑、官方 CLI 與 MCP 的取捨"),
        ("claude-code-cowork", "Claude Code + Cowork 並用", "帳號現況判斷、檔案交接工作流程、Dispatch 現況"),
    ]),
    ("軟體開發流程 SDLC", [
        ("sdlc-traditional", "SDLC 與流程模型", "瀑布式、V 模型、螺旋模型、敏捷式各階段在做什麼"),
        ("dev-practices", "開發實踐：TDD、BDD、DDD 與 SDD", "寫程式時的具體方法，以及它們和 AI 代理怎麼搭配"),
        ("sdlc-ai-agent", "AI 代理時代的 SDLC", "規格、計畫、實作、驗證、交付各階段的 AI 分工"),
    ]),
    ("官方建議設定", [
        ("official-config", "Claude Code 設定總覽", "CLAUDE.md、rules、settings、權限怎麼寫"),
        ("hooks-subagents", "Hooks 與 Subagent 設定", "自動化檢查與子代理定義"),
        ("session-handoff", "跨 session 接力：session_log", "讓下一個對話接得上進度"),
    ]),
    ("隔離與沙箱", [
        ("wsl2-isolation", "WSL2 當隔離環境", "WSL2 跟 Windows 的邊界、實驗用 distro、備份與還原"),
        ("agent-sandbox", "Coding agent 沙箱：Claude Code 與 Codex", "/sandbox 與 Codex 沙箱怎麼裝、各層擋什麼、裝完怎麼確認"),
    ]),
    ("關於", [
        ("about", "關於這個網站", "定位、查證原則與更新紀錄"),
    ]),
]

SLUG_TITLE = {}
FLAT = []
for _sec, items in NAV:
    for slug, title, desc in items:
        SLUG_TITLE[slug] = title
        FLAT.append((slug, title, desc))


_UPDATED_CACHE = {}


def source_updated(src):
    """取得來源檔最後一次 Git 提交的 Unix 時間戳。

    未安裝 Git、指令失敗或檔案尚無提交紀錄時，改用檔案的
    mtime。結果會在單次建置期間快取，避免每次產生側欄都重複查詢。
    """
    if src in _UPDATED_CACHE:
        return _UPDATED_CACHE[src]

    rel = os.path.relpath(src, ROOT).replace(os.sep, "/")
    updated = None
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", rel],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        value = result.stdout.strip()
        if result.returncode == 0 and value.isdigit():
            updated = int(value)
    except (OSError, subprocess.TimeoutExpired):
        pass

    if updated is None:
        updated = int(os.stat(src).st_mtime)
    _UPDATED_CACHE[src] = updated
    return updated


def nav_html(active, prefix=""):
    out = ['<nav class="sidenav" id="sidenav" aria-label="全站導覽">']
    out.append(f'<a class="brand" href="{prefix}index.html"><span class="brand-mark">◈</span>'
               f'<span class="brand-text">AI Agent<br><small>筆記</small></span></a>')
    out.append('<div class="navsearch"><input type="search" id="navfilter" '
               'placeholder="篩選頁面…" aria-label="篩選頁面"></div>')
    for sec, items in NAV:
        out.append(f'<div class="navsec"><h2>{sec}</h2><ul>')
        for slug, title, _d in items:
            cls = ' class="active"' if slug == active else ""
            updated = source_updated(os.path.join(DOCS, slug + ".md"))
            out.append(f'<li{cls}><a href="{prefix}pages/{slug}.html" '
                       f'data-title="{title}" data-slug="{slug}" '
                       f'data-updated="{updated}">{title}</a></li>')
        out.append("</ul></div>")
    out.append("</nav>")
    return "\n".join(out)


TEMPLATE = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}｜AI Agent 筆記</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>&#128218;</text></svg>">
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<a class="skip" href="#main">跳到主要內容</a>
<button class="navtoggle" id="navtoggle" aria-label="開啟導覽">☰</button>
{nav}
<div class="wrap">
<main id="main">
<p class="crumb"><a href="../index.html">首頁</a> ／ {section}</p>
<article class="doc" data-updated="{updated}">
{body}
</article>
<nav class="pager">{pager}</nav>
<footer class="foot">
<p>這是個人整理筆記，不是官方文件；工具與方案變動很快，請以官方最新說明為準。</p>
<p><a href="../pages/about.html">關於這個網站</a>　·　<a href="{repo}">GitHub</a></p>
</footer>
</main>
<aside class="toc" id="toc"><h2>本頁目錄</h2>{toc}</aside>
</div>
<script src="../assets/site.js"></script>
{legacy}</body>
</html>
"""


SEC_DESC = {
    "先搞懂工具": "Claude、ChatGPT、Codex 各種介面差在哪、免費能做到哪裡",
    "AI Agent 原理": "代理怎麼運作、擴充機制是什麼",
    "實戰協作": "多個 AI 工具怎麼分工",
    "軟體開發流程 SDLC": "傳統開發流程，以及 AI 代理加入後的變化",
    "官方建議設定": "只整理官方文件的建議寫法",
    "隔離與沙箱": "讓 agent 放手做事之前，WSL2 與沙箱怎麼疊、怎麼驗",
    "關於": "網站定位與更新紀錄",
}

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Agent 筆記</title>
<meta name="description" content="Claude、Codex 與 AI 代理工具的整理筆記">
<link rel="canonical" href="{site_url}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>&#128218;</text></svg>">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<a class="skip" href="#main">跳到主要內容</a>
<button class="navtoggle" id="navtoggle" aria-label="開啟導覽">☰</button>
{nav}
<div class="wrap solo">
<main id="main">

<header class="hero">
<span class="tag">Claude ／ Codex ／ AI Agent</span>
<h1>AI Agent 筆記</h1>
<p>Claude、Codex 與 AI 代理工具的整理筆記</p>
</header>

<div class="notice">
<b>閱讀前請先注意</b>
<p>這是個人整理筆記，不是官方文件；工具與方案變動很快，每頁標註查證日期，請以官方最新說明為準。</p>
</div>

<div class="homesearch">
<input type="search" id="homefilter" placeholder="搜尋主題…（例如：Codex、MCP、Hooks）" aria-label="搜尋主題">
</div>

{sections}

<footer class="foot">
<p>這是個人整理筆記，不是官方文件；工具與方案變動很快，請以官方最新說明為準。</p>
<p><a href="pages/about.html">關於這個網站</a>　·　<a href="{repo}">GitHub</a>　·　最後更新：2026-09</p>
</footer>

</main>
</div>
<script src="assets/site.js"></script>
</body>
</html>
"""


def build_index():
    parts = []
    for i, (sec, items) in enumerate(NAV, start=1):
        cards = []
        for slug, title, desc in items:
            cards.append(f'<a class="card" href="pages/{slug}.html">'
                         f'<h3>{title}</h3><p>{desc}</p></a>')
        parts.append(
            f'<section class="mapsec"><h2><span class="num">{i:02d}</span>{sec}</h2>'
            f'<p class="secdesc">{SEC_DESC.get(sec, "")}</p>'
            f'<div class="cards">{"".join(cards)}</div></section>')
    out = INDEX_TEMPLATE.format(nav=nav_html(None, prefix=""), sections="\n".join(parts),
                                site_url=SITE_URL, repo=REPO_URL)
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(out)
    print("  ✓ index.html")


def section_of(slug):
    for sec, items in NAV:
        for s, _t, _d in items:
            if s == slug:
                return sec
    return ""


# 2026-10 錨點改由標題文字決定（slugify_unicode）。舊網址 #_5 這類自動編號錨點
# 靠 reports/anchor-map.json 的對照，在每頁內嵌一小段 JS 轉到新錨點。
ANCHOR_MAP = os.path.join(ROOT, "reports", "anchor-map.json")


def legacy_anchor_script(slug, body):
    if not os.path.exists(ANCHOR_MAP):
        return ""
    rows = json.load(open(ANCHOR_MAP, encoding="utf-8")).get(slug, [])
    ids = set(re.findall(r'\sid="([^"]*)"', body))
    m = {}
    for r in rows:
        if r["old"] == r["new"] or r["old"] in ids:
            continue
        if r["new"] not in ids:
            print("  ! %s：舊錨點 #%s 的對照目標 #%s 已不存在（標題改過？）" % (slug, r["old"], r["new"]))
            continue
        m[r["old"]] = r["new"]
    if not m:
        return ""
    data = json.dumps(m, ensure_ascii=False, separators=(",", ":"))
    return ("<script>(function(){var m=%s;function f(){var h=decodeURIComponent(location.hash.slice(1));"
            "if(h&&m[h]&&!document.getElementById(h)){var n=m[h];history.replaceState(null,\"\",\"#\"+encodeURIComponent(n));"
            "var g=function(){var e=document.getElementById(n);if(e)e.scrollIntoView();};"
            "document.readyState===\"complete\"?g():addEventListener(\"load\",g);}}"
            "f();addEventListener(\"hashchange\",f);})();</script>\n" % data)


def build():
    os.makedirs(PAGES, exist_ok=True)
    md = markdown.Markdown(extensions=["extra", "toc", "sane_lists", "admonition"],
                           extension_configs={"toc": {"toc_depth": "2-3",
                                                  "slugify": slugify_unicode}})
    for i, (slug, title, desc) in enumerate(FLAT):
        src = os.path.join(DOCS, slug + ".md")
        if not os.path.exists(src):
            print("  ! 缺少", src)
            continue
        md.reset()
        text = open(src, encoding="utf-8").read()
        # 移除 Markdown 檔開頭的 H1（HTML 由樣板統一呈現）
        text = re.sub(r"\A#\s+.*\n", "", text)
        body = md.convert(text)
        # 內部連結：docs/*.md → 同目錄的 *.html
        body = re.sub(r'href="(?!https?:|#|\.\./)([A-Za-z0-9\-_]+)\.md(#[^"]*)?"',
                      lambda m: 'href="%s.html%s"' % (m.group(1), m.group(2) or ""), body)
        body = f"<h1>{title}</h1>\n<p class='lede'>{desc}</p>\n" + body
        # 讓 - [ ] 變成可勾選
        body = body.replace("<li>[ ] ", '<li class="chk"><input type="checkbox"> ')
        body = body.replace("<li>[x] ", '<li class="chk"><input type="checkbox" checked> ')
        prev_ = FLAT[i - 1] if i > 0 else None
        next_ = FLAT[i + 1] if i < len(FLAT) - 1 else None
        pager = ""
        if prev_:
            pager += f'<a class="prev" href="{prev_[0]}.html">← {prev_[1]}</a>'
        if next_:
            pager += f'<a class="next" href="{next_[0]}.html">{next_[1]} →</a>'
        toc = md.toc.replace('<div class="toc">', '<div class="toc-body">')
        out = TEMPLATE.format(title=title, desc=html.escape(desc, quote=True),
                              nav=nav_html(slug, prefix="../"), body=body,
                              toc=toc, pager=pager, section=section_of(slug),
                              legacy=legacy_anchor_script(slug, body),
                              updated=source_updated(src), canonical=SITE_URL + "pages/" + slug + ".html",
                              repo=REPO_URL)
        with open(os.path.join(PAGES, slug + ".html"), "w", encoding="utf-8") as f:
            f.write(out)
        print("  ✓", slug + ".html")

    # 給首頁搜尋用的索引
    idx = [{"slug": s, "title": t, "desc": d, "section": section_of(s)} for s, t, d in FLAT]
    with open(os.path.join(ROOT, "assets", "index.json"), "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    build()
    build_index()
    print("完成。")
