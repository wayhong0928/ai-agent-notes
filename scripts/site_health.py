#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全站健檢：連結、手機版溢出、無障礙、build 是否乾淨。
用法：python scripts/site_health.py [--skip-external] [--skip-browser] [--json 檔案]
需求：pip install markdown requests playwright
      （第一次用 Playwright 需要 python -m playwright install chromium）

做法：
  1. 把整個 repo 複製到暫存目錄，在那裡跑 build.py，工作目錄不會被改到。
     產出跟工作目錄裡的 pages/*.html、index.html 比對。
  2. 內部連結與錨點：解析暫存目錄的 HTML，逐一確認檔案與 id 存在。
  3. 外部連結：從 docs/*.md 產生的內文收集，先 HEAD、失敗再 GET，逾時 15 秒。
     另外直接用正規式數 docs/*.md 裡的外部連結，兩個數字必須一致。
  4. 用 Playwright 開每一頁：375x812 檢查水平溢出；1280x900 在亮色與暗色
     模式下檢查 lang、img alt、標題跳級、連結文字、文字對比。
結束碼：0 沒有需要修的問題；1 有（外部連結的結果不影響結束碼，因為會隨時間變動）。
"""
import argparse
import collections
import concurrent.futures
import fnmatch
import html.parser
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
TIMEOUT = 15
# DOI 與 Handle 本來就是轉址服務，轉到出版社網域是正常行為
RESOLVERS = {"doi.org", "dx.doi.org", "hdl.handle.net"}
# 雲端執行環境的 GitHub 代理只開放指定的 repo，其餘回 403 並帶這段文字；
# 這不是 GitHub 本身的回應，歸類為「執行環境擋住」
ENV_BLOCK_MARKER = b"not enabled for this session"
MOBILE = {"width": 375, "height": 812}
DESKTOP = {"width": 1280, "height": 900}
VAGUE_LINK_TEXT = {"這裡", "这里", "點此", "點這裡", "按此", "按這裡", "此處", "此連結", "連結",
                   "here", "click here", "click", "link", "this link", "more", "read more"}
# build 產物：比對時只看這些
BUILD_OUTPUTS = ["index.html", "pages/*.html", "*.html", "assets/index.json"]
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".obsidian"}


# ---------------------------------------------------------------- 共用

def rel(path, base=ROOT):
    return os.path.relpath(path, base).replace(os.sep, "/")


def strip_code(md_text):
    """把 fenced code block 與行內 code 換成等長空白，保留行號。"""
    out, fence = [], None
    for line in md_text.split("\n"):
        m = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
                fence = None
            out.append("")
            continue
        if m:
            fence = m.group(1)
            out.append("")
            continue
        out.append(re.sub(r"(`+)(.+?)\1", lambda x: " " * len(x.group(0)), line))
    return "\n".join(out)


URL_BODY = r"(?:[^\s()<>]|\([^\s()<>]*\))+"
MD_LINK_PATTERNS = [
    re.compile(r"\]\(\s*<?(https?://" + URL_BODY + r")>?"),     # [text](url)、![alt](url)
    re.compile(r"(?<![\]\(])<(https?://[^>\s]+)>"),           # <url>
    re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?(https?://[^\s>]+)>?", re.M),  # [id]: url
    re.compile(r"(?:href|src)=\"(https?://[^\"]+)\""),          # 內嵌 HTML
]


def md_external_links(md_text):
    """直接從 Markdown 原文數外部連結（略過程式碼），回傳 [(行號, url)]。"""
    text = strip_code(md_text)
    found = []
    for pat in MD_LINK_PATTERNS:
        for m in pat.finditer(text):
            line = text.count("\n", 0, m.start(1)) + 1
            found.append((line, m.group(1).replace("&amp;", "&")))
    return sorted(found)


def md_line_of(md_path, needles):
    """在 Markdown 原文找第一個含有 needle 的連結位置，回傳行號（找不到回傳 None）。"""
    try:
        lines = open(md_path, encoding="utf-8").read().split("\n")
    except OSError:
        return None
    for needle in needles:
        for i, line in enumerate(lines, 1):
            if "(" + needle in line or "<" + needle in line or '"' + needle in line:
                return i
    return None


class PageParser(html.parser.HTMLParser):
    """收集一頁的 id、連結（含是否在 article.doc 內）與 lang。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []          # (href, in_article, text)
        self.resources = []      # (src, in_article)
        self._article_depth = 0
        self._depth = 0
        self._cur = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in ("br", "img", "input", "meta", "link", "hr", "source", "wbr"):
            self._depth += 1
        if tag == "article" and "doc" in (a.get("class") or "").split():
            self._article_depth = self._depth
        for key in ("id",):
            if a.get(key):
                self.ids.add(a[key])
        if tag == "a" and a.get("name"):
            self.ids.add(a["name"])
        in_article = bool(self._article_depth)
        if tag == "a" and a.get("href") is not None:
            self._cur = [a["href"], in_article, ""]
            self.links.append(self._cur)
        if tag in ("img", "script", "source", "iframe") and a.get("src"):
            self.resources.append((a["src"], in_article))
        if tag == "link" and a.get("href"):
            self.resources.append((a["href"], in_article))

    def handle_endtag(self, tag):
        if tag == "a":
            self._cur = None
        if tag not in ("br", "img", "input", "meta", "link", "hr", "source", "wbr"):
            if self._article_depth and self._depth == self._article_depth and tag == "article":
                self._article_depth = 0
            self._depth -= 1

    def handle_data(self, data):
        if self._cur is not None:
            self._cur[2] += data


def parse_page(path):
    p = PageParser()
    p.feed(open(path, encoding="utf-8").read())
    p.links = [(h, ia, " ".join(t.split())) for h, ia, t in p.links]
    return p


# ---------------------------------------------------------------- 1. build

def copy_repo(dst):
    def ignore(_d, names):
        return [n for n in names if n in SKIP_DIRS - {".git"}]
    shutil.copytree(ROOT, dst, ignore=ignore, symlinks=True)


def output_files(base):
    files = set()
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            r = rel(os.path.join(dirpath, name), base)
            if any(fnmatch.fnmatch(r, pat) and (pat != "*.html" or "/" not in r)
                   for pat in BUILD_OUTPUTS):
                files.add(r)
    return files


def check_build(tmp):
    result = {"returncode": None, "stdout_warnings": [], "python_warnings": [],
              "identical": [], "timestamp_only": [], "different": [], "missing": [], "extra": []}
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    before = {r: open(os.path.join(ROOT, r), "rb").read() for r in output_files(ROOT)}
    # 1) 一般執行
    proc = subprocess.run([sys.executable, "build.py"], cwd=tmp, capture_output=True,
                          text=True, encoding="utf-8", env=env)
    result["returncode"] = proc.returncode
    for line in (proc.stdout + proc.stderr).splitlines():
        s = line.strip()
        if not s or s.startswith(("✓", "[ok]")) or s == "完成。":
            continue
        result["stdout_warnings"].append(s)
    # 2) 打開 Python 警告再跑一次（不影響產物）
    proc2 = subprocess.run([sys.executable, "-W", "default", "build.py"], cwd=tmp,
                           capture_output=True, text=True, encoding="utf-8", env=env)
    warn = collections.Counter()
    for line in proc2.stderr.splitlines():
        m = re.search(r"(\w+Warning): (.*?)(?: name='[^']*')?(?: mode=.*)?$", line)
        if m:
            warn[f"{m.group(1)}: {re.sub(r'<_io.*', 'unclosed file（open() 沒有關閉）', m.group(2))}"] += 1
    result["python_warnings"] = [f"{k}（{v} 次）" for k, v in warn.items()]

    after = {r: open(os.path.join(tmp, r), "rb").read() for r in output_files(tmp)}
    norm = lambda b: re.sub(rb'data-updated="\d+"', b'data-updated=""', b)
    for r in sorted(set(before) | set(after)):
        if r not in after:
            result["extra"].append(r)
        elif r not in before:
            result["missing"].append(r)
        elif before[r] == after[r]:
            result["identical"].append(r)
        elif norm(before[r]) == norm(after[r]):
            result["timestamp_only"].append(r)
        else:
            a = before[r].decode("utf-8", "replace").splitlines()
            b = after[r].decode("utf-8", "replace").splitlines()
            first = next((i for i, (x, y) in enumerate(zip(a, b)) if norm(x.encode()) != norm(y.encode())),
                         min(len(a), len(b)))
            result["different"].append({"file": r, "line": first + 1})
    return result


# ---------------------------------------------------------------- 2. 內部連結

def page_source(page_rel, in_article):
    """把產出頁對回來源檔：article 內文來自 docs/*.md，其餘來自 build.py 樣板。"""
    if page_rel.startswith("pages/") and in_article:
        return "docs/" + os.path.basename(page_rel)[:-5] + ".md"
    if page_rel.startswith("pages/") or page_rel == "index.html":
        return "build.py（樣板）"
    return page_rel


def html_pages(base):
    pages = ["index.html"]
    pages += sorted("pages/" + f for f in os.listdir(os.path.join(base, "pages")) if f.endswith(".html"))
    pages += sorted(f for f in os.listdir(base) if f.endswith(".html") and f != "index.html")
    return [p for p in pages if os.path.exists(os.path.join(base, p))]


def check_internal(tmp):
    parsed = {p: parse_page(os.path.join(tmp, p)) for p in html_pages(tmp)}
    ids_cache = {}

    def ids_of(path):
        if path not in ids_cache:
            ids_cache[path] = parse_page(path).ids if path.endswith(".html") else set()
        return ids_cache[path]

    problems, checked, anchors = [], 0, []
    for page, p in parsed.items():
        page_abs = os.path.join(tmp, page)
        for href, in_article, text in p.links:
            if re.match(r"^(?:[a-z][a-z0-9+.-]*:|//)", href, re.I):
                continue
            checked += 1
            path, _, frag = href.partition("#")
            target = page_abs if not path else os.path.normpath(
                os.path.join(os.path.dirname(page_abs), urllib.parse.unquote(path)))
            if os.path.isdir(target):
                target = os.path.join(target, "index.html")
            src = page_source(page, in_article)
            issue = None
            if not target.startswith(tmp + os.sep) and target != tmp:
                issue = "指到網站目錄外"
            elif not os.path.exists(target):
                issue = "檔案不存在"
            elif frag and urllib.parse.unquote(frag) not in ids_of(target):
                issue = f"錨點 #{frag} 不存在"
            if frag and not issue and re.fullmatch(r"_?\d+", urllib.parse.unquote(frag)):
                anchors.append({"page": page, "source": src, "href": href, "text": text,
                                "target": rel(target, tmp)})
            if issue:
                line = None
                if src.startswith("docs/"):
                    md_href = re.sub(r"\.html(?=$|#)", ".md", href)
                    line = md_line_of(os.path.join(ROOT, src), [md_href, href])
                problems.append({"page": page, "source": src + (f":{line}" if line else ""),
                                 "href": href, "text": text, "issue": issue})
        for src_url, in_article in p.resources:
            if re.match(r"^(?:[a-z][a-z0-9+.-]*:|//)", src_url, re.I):
                continue
            checked += 1
            target = os.path.normpath(os.path.join(os.path.dirname(page_abs),
                                                   urllib.parse.unquote(src_url.split("#")[0].split("?")[0])))
            if not os.path.exists(target):
                problems.append({"page": page, "source": page_source(page, in_article),
                                 "href": src_url, "text": "（資源）", "issue": "檔案不存在"})
    return {"checked": checked, "problems": problems, "numeric_anchors": anchors,
            "table_overflow": check_md_tables()}


def check_md_tables():
    """表格列的欄數多於表頭時，Python-Markdown 會直接丟掉多出來的欄，
    常見原因是儲存格裡有沒跳脫的 |。回傳 [(來源, 表頭欄數, 該列欄數)]。"""
    split = lambda line: re.split(r"(?<!\\)\|", line.strip().strip("|"))
    out = []
    for name in sorted(os.listdir(DOCS)):
        if not name.endswith(".md"):
            continue
        lines = strip_code(open(os.path.join(DOCS, name), encoding="utf-8").read()).split("\n")
        header = None
        for i, line in enumerate(lines):
            if header is None:
                if (i + 1 < len(lines) and "|" in line
                        and re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$", lines[i + 1])):
                    header = len(split(line))
                continue
            if "|" not in line or not line.strip():
                header = None
                continue
            n = len(split(line))
            if n > header and not re.match(r"^\s*\|?\s*:?-{3,}", line):
                out.append({"source": f"docs/{name}:{i + 1}", "header": header, "cells": n})
    return out


# ---------------------------------------------------------------- 3. 外部連結

def collect_external(tmp):
    """回傳 (docs 內文的連結出現清單, 樣板與手寫頁的連結出現清單, 直接數 Markdown 的清單)。"""
    in_docs, other = [], []
    for page in html_pages(tmp):
        p = parse_page(os.path.join(tmp, page))
        for href, in_article, text in p.links:
            if re.match(r"^https?://", href, re.I):
                (in_docs if in_article and page.startswith("pages/") else other).append(
                    {"page": page, "url": href, "text": text,
                     "source": page_source(page, in_article)})
        for src_url, in_article in p.resources:
            if re.match(r"^https?://", src_url, re.I):
                (in_docs if in_article and page.startswith("pages/") else other).append(
                    {"page": page, "url": src_url, "text": "（資源）",
                     "source": page_source(page, in_article)})
    raw = []
    for name in sorted(os.listdir(DOCS)):
        if name.endswith(".md"):
            text = open(os.path.join(DOCS, name), encoding="utf-8").read()
            raw += [{"source": f"docs/{name}:{ln}", "url": u} for ln, u in md_external_links(text)]
    # 補上行號
    by_file = collections.defaultdict(list)
    for r in raw:
        f, ln = r["source"].rsplit(":", 1)
        by_file[(f, r["url"])].append(ln)
    used = collections.Counter()
    for item in in_docs:
        key = (item["source"], item["url"])
        lines = by_file.get(key) or []
        i = used[key]
        if i < len(lines):
            item["source"] += ":" + lines[i]
        used[key] += 1
    return in_docs, other, raw


_host_locks = collections.defaultdict(lambda: threading.Semaphore(2))
_tls = threading.local()


def host_key(url):
    h = (urllib.parse.urlsplit(url).hostname or "").lower()
    return h[4:] if h.startswith("www.") else h


def probe(url):
    import requests
    if not hasattr(_tls, "s"):
        _tls.s = requests.Session()
        _tls.s.headers.update({"User-Agent": USER_AGENT,
                               "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
        # 不送 Accept-Language：有些 API 遇到沒有的語系會回 404（例如 ISTQB 詞彙表）
    s = _tls.s
    target = url.split("#")[0]
    res = {"url": url, "method": None, "status": None, "final": None, "error": None,
           "redirects": [], "env_blocked": False}
    with _host_locks[host_key(url)]:
        for method in ("HEAD", "GET"):
            res["method"] = method
            try:
                r = s.request(method, target, allow_redirects=True, timeout=TIMEOUT, stream=True)
                body = r.raw.read(2048, decode_content=True) if r.status_code == 403 else b""
                r.close()
                res.update(status=r.status_code, final=r.url, error=None,
                           redirects=[h.status_code for h in r.history],
                           env_blocked=ENV_BLOCK_MARKER in body)
                if r.status_code < 400:
                    break
            except requests.exceptions.ProxyError as e:
                res.update(status=None, final=None, error="proxy: " + str(e)[:120])
            except requests.exceptions.Timeout:
                res.update(status=None, final=None, error="timeout")
            except requests.exceptions.RequestException as e:
                res.update(status=None, final=None, error=type(e).__name__ + ": " + str(e)[:120])
    res["category"] = classify(res)
    return res


def classify(r):
    if r["env_blocked"]:
        return "執行環境擋住"
    if r["error"] == "timeout":
        return "逾時"
    if r["error"] and r["error"].startswith("proxy"):
        return "執行環境擋住"
    if r["error"]:
        return "連線錯誤"
    if r["status"] in (404, 410):
        return "404/410"
    if r["status"] in (403, 429):
        return "403/429（需人工確認）"
    if r["status"] >= 400:
        return f"其他狀態碼"
    if host_key(r["final"]) != host_key(r["url"]) and host_key(r["url"]) not in RESOLVERS:
        return "跳到別的網域"
    return "正常"


def check_external(tmp, workers=16):
    in_docs, other, raw = collect_external(tmp)
    occurrences = in_docs + other
    urls = sorted({o["url"] for o in occurrences})
    results = {}
    with concurrent.futures.ThreadPoolExecutor(workers) as ex:
        for res in ex.map(probe, urls):
            results[res["url"]] = res
    docs_counter = collections.Counter(o["url"] for o in in_docs)
    raw_counter = collections.Counter(o["url"] for o in raw)
    return {
        "docs_occurrences": len(in_docs), "docs_unique": len(docs_counter),
        "raw_md_occurrences": len(raw), "raw_md_unique": len(raw_counter),
        "count_mismatch": {"only_rendered": sorted((docs_counter - raw_counter).elements()),
                           "only_raw": sorted((raw_counter - docs_counter).elements())},
        "other_occurrences": len(other),
        "checked_unique": len(results),
        "occurrences": occurrences, "results": results,
    }


# ---------------------------------------------------------------- 4. 瀏覽器檢查

JS_OVERFLOW = r"""
() => {
  const iw = window.innerWidth, sw = document.documentElement.scrollWidth;
  const out = {iw, sw, offenders: []};
  if (sw <= iw) return out;
  const clipped = (el) => {
    for (let p = el.parentElement; p && p !== document.body && p !== document.documentElement; p = p.parentElement) {
      const s = getComputedStyle(p);
      if (s.overflowX !== 'visible' || s.position === 'fixed') return true;
    }
    return false;
  };
  const desc = (el) => {
    let d = el.tagName.toLowerCase();
    if (el.id) d += '#' + el.id;
    if (el.classList.length) d += '.' + [...el.classList].join('.');
    return d;
  };
  const hits = new Map();  // 元素 → 右緣位置
  for (const el of document.body.querySelectorAll('*')) {
    const s = getComputedStyle(el);
    if (s.position === 'fixed' || s.display === 'none') continue;
    const r = el.getBoundingClientRect();
    if (r.width > 0 && r.right > iw + 0.5 && !clipped(el)) hits.set(el, r.right);
  }
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    if (!n.textContent.trim() || !n.parentElement) continue;
    const range = document.createRange(); range.selectNodeContents(n);
    for (const r of range.getClientRects()) {
      if (r.right > iw + 0.5 && !clipped(n.parentElement) &&
          getComputedStyle(n.parentElement).position !== 'fixed') {
        hits.set(n.parentElement, Math.max(r.right, hits.get(n.parentElement) || 0)); break;
      }
    }
  }
  const els = [...hits.keys()];
  const deepest = els.filter(el => !els.some(o => o !== el && el.contains(o)));
  for (const el of deepest.slice(0, 12)) {
    out.offenders.push({el: desc(el), parent: el.parentElement ? desc(el.parentElement) : '',
                        right: Math.round(hits.get(el)), text: (el.textContent || '').trim().slice(0, 80)});
  }
  return out;
}
"""

JS_A11Y = r"""
() => {
  const desc = (el) => {
    let d = el.tagName.toLowerCase();
    if (el.id) d += '#' + el.id;
    if (el.classList.length) d += '.' + [...el.classList].join('.');
    return d;
  };
  const res = {lang: document.documentElement.getAttribute('lang'), imgs: [], headings: [],
               links: [], unnamed: []};
  for (const img of document.querySelectorAll('img')) {
    if (!img.hasAttribute('alt')) res.imgs.push(img.getAttribute('src'));
  }
  let prev = 0, prevText = '';
  for (const h of document.querySelectorAll('h1,h2,h3,h4,h5,h6')) {
    const lv = +h.tagName[1];
    const text = h.textContent.trim().replace(/\s+/g, ' ').slice(0, 60);
    if (prev && lv > prev + 1) res.headings.push({from: 'h' + prev, to: 'h' + lv, prevText, text});
    prev = lv; prevText = text;
  }
  for (const a of document.querySelectorAll('a[href]')) {
    const name = (a.getAttribute('aria-label') || a.textContent || '').trim().replace(/\s+/g, ' ');
    const alt = [...a.querySelectorAll('img[alt]')].map(i => i.alt).join(' ').trim();
    res.links.push({text: name || alt, href: a.getAttribute('href')});
  }
  for (const el of document.querySelectorAll('input:not([type=hidden]),select,textarea,button')) {
    const id = el.id;
    const labelled = el.getAttribute('aria-label') || el.getAttribute('aria-labelledby') ||
      el.getAttribute('title') || el.closest('label') ||
      (id && document.querySelector('label[for="' + CSS.escape(id) + '"]')) ||
      (el.tagName === 'BUTTON' && el.textContent.trim());
    if (!labelled) {
      const ctx = (el.closest('li,p,div') || el.parentElement);
      res.unnamed.push({el: desc(el), type: el.type || '', context: ctx ? ctx.textContent.trim().replace(/\s+/g, ' ').slice(0, 40) : ''});
    }
  }
  return res;
}
"""

JS_CONTRAST = r"""
() => {
  const parse = (c) => {
    const m = c.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number);
    return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1];
  };
  const over = (top, bottom) => {
    const a = top[3];
    return [0, 1, 2].map(i => top[i] * a + bottom[i] * (1 - a)).concat([1]);
  };
  const lum = (c) => {
    const ch = c.slice(0, 3).map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); });
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2];
  };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const hex = (c) => '#' + c.slice(0, 3).map(v => Math.round(v).toString(16).padStart(2, '0')).join('');
  const desc = (el) => {
    let d = el.tagName.toLowerCase();
    if (el.classList.length) d += '.' + [...el.classList].join('.');
    let p = el.parentElement, ctx = '';
    while (p && p !== document.body) {
      if (p.id || p.classList.length) { ctx = p.tagName.toLowerCase() + (p.id ? '#' + p.id : '') + (p.classList.length ? '.' + [...p.classList].join('.') : ''); break; }
      p = p.parentElement;
    }
    return ctx ? ctx + ' ' + d : d;
  };
  // 由下往上合成背景；遇到漸層時把漸層裡的每個顏色都當成可能的背景
  const backgrounds = (el) => {
    const layers = [];
    for (let p = el; p; p = p.parentElement) {
      const s = getComputedStyle(p);
      const grads = s.backgroundImage.includes('gradient') ?
        (s.backgroundImage.match(/rgba?\([^)]+\)/g) || []).map(parse).filter(c => c[3] > 0) : [];
      layers.push({bg: parse(s.backgroundColor), grads});
      if (parse(s.backgroundColor)[3] >= 1) break;
    }
    let bases = [[255, 255, 255, 1]];
    for (const L of layers.reverse()) {
      bases = bases.map(b => L.bg[3] > 0 ? over(L.bg, b) : b);
      if (L.grads.length) bases = bases.concat(...L.grads.map(g => bases.map(b => over(g, b))));
    }
    return bases;
  };
  const out = [];
  for (const el of document.body.querySelectorAll('*')) {
    const hasText = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (!hasText) continue;
    const s = getComputedStyle(el);
    if (s.display === 'none' || s.visibility === 'hidden') continue;
    if (el.closest('[aria-hidden="true"]')) continue;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    const size = parseFloat(s.fontSize), bold = parseInt(s.fontWeight) >= 700;
    const large = size >= 24 || (size >= 18.66 && bold);
    const need = large ? 3 : 4.5;
    const fgRaw = parse(s.color);
    for (const bg of backgrounds(el)) {
      const fg = fgRaw[3] < 1 ? over(fgRaw, bg) : fgRaw;
      const cr = ratio(fg, bg);
      if (cr < need) {
        out.push({el: desc(el), fg: hex(fg), bg: hex(bg), ratio: Math.round(cr * 100) / 100, need,
                  text: [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join('').trim().slice(0, 30)});
      }
    }
  }
  return out;
}
"""


def check_browser(tmp, chromium=None):
    from playwright.sync_api import sync_playwright
    pages = html_pages(tmp)
    mobile, a11y, contrast = [], [], collections.OrderedDict()
    with sync_playwright() as pw:
        kw = {"executable_path": chromium} if chromium else {}
        browser = pw.chromium.launch(**kw)
        for page_rel in pages:
            url = "file://" + os.path.join(tmp, page_rel)
            # 手機版。不開 is_mobile：手機模式會自動縮小頁面去塞下過寬的內容，
            # innerWidth 跟著變大，反而量不到溢出
            ctx = browser.new_context(viewport=MOBILE, device_scale_factor=2, has_touch=True)
            pg = ctx.new_page()
            pg.goto(url, wait_until="load")
            pg.wait_for_timeout(150)
            ov = pg.evaluate(JS_OVERFLOW)
            mobile.append({"page": page_rel, **ov})
            ctx.close()
            # 無障礙（桌機寬度，亮色＋暗色）
            for scheme in ("light", "dark"):
                ctx = browser.new_context(viewport=DESKTOP, color_scheme=scheme)
                pg = ctx.new_page()
                pg.goto(url, wait_until="load")
                pg.wait_for_timeout(150)
                if scheme == "light":
                    info = pg.evaluate(JS_A11Y)
                    a11y.append({"page": page_rel, **info})
                for c in pg.evaluate(JS_CONTRAST):
                    key = (scheme, c["el"], c["fg"], c["bg"])
                    item = contrast.setdefault(key, {**c, "scheme": scheme, "pages": []})
                    if page_rel not in item["pages"]:
                        item["pages"].append(page_rel)
                ctx.close()
        browser.close()

    a11y_problems = []
    for info in a11y:
        p = info["page"]
        if not info["lang"]:
            a11y_problems.append({"page": p, "kind": "html 缺 lang", "detail": ""})
        for src in info["imgs"]:
            a11y_problems.append({"page": p, "kind": "img 缺 alt", "detail": src})
        for h in info["headings"]:
            a11y_problems.append({"page": p, "kind": "標題跳級",
                                  "detail": f"{h['from']}「{h['prevText']}」→ {h['to']}「{h['text']}」"})
        for l in info["links"]:
            t = l["text"].strip().lower()
            if not t:
                a11y_problems.append({"page": p, "kind": "連結沒有文字", "detail": l["href"]})
            elif t in VAGUE_LINK_TEXT:
                a11y_problems.append({"page": p, "kind": "連結文字不具體", "detail": f"「{l['text']}」→ {l['href']}"})
        for u in info["unnamed"]:
            a11y_problems.append({"page": p, "kind": "表單控制項沒有名稱",
                                  "detail": f"{u['el']}（{u['type']}）：{u['context']}"})
    return {"mobile": mobile, "a11y": a11y_problems, "contrast": list(contrast.values())}


# ---------------------------------------------------------------- 輸出

def md_escape(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def print_report(r):
    out = []
    w = out.append
    b = r["build"]
    w("## build")
    w(f"- build.py 結束碼：{b['returncode']}；輸出中的警告／錯誤：{len(b['stdout_warnings'])} 則")
    for s in b["stdout_warnings"]:
        w(f"  - {s}")
    w(f"- 打開 Python 警告（-W default）時：{'、'.join(b['python_warnings']) or '無'}")
    w(f"- 產物與工作目錄一致：{len(b['identical'])} 個；只差 data-updated 時間戳：{len(b['timestamp_only'])} 個；"
      f"內容不同：{len(b['different'])} 個；工作目錄缺少：{len(b['missing'])}；多出：{len(b['extra'])}")
    for d in b["different"]:
        w(f"  - 內容不同：{d['file']}（第 {d['line']} 行起）")
    for f in b["timestamp_only"]:
        w(f"  - 只差時間戳：{f}")

    i = r["internal"]
    w("\n## 內部連結")
    w(f"- 檢查 {i['checked']} 個內部連結與資源，問題 {len(i['problems'])} 個")
    if i["problems"]:
        w("\n| 頁面 | 來源 | 連結 | 文字 | 問題 |\n|---|---|---|---|---|")
        for p in i["problems"]:
            w(f"| {p['page']} | {p['source']} | `{md_escape(p['href'])}` | {md_escape(p['text'])} | {p['issue']} |")
    w(f"- Markdown 表格列的欄數多於表頭（多的內容不會顯示）：{len(i['table_overflow'])} 列")
    for t in i["table_overflow"]:
        w(f"  - {t['source']}：表頭 {t['header']} 欄、這一列 {t['cells']} 欄")
    if i["numeric_anchors"]:
        w(f"- 依標題順序自動編號的錨點（#_5、#42 這類，標題增刪後會指錯）：{len(i['numeric_anchors'])} 個")

    e = r.get("external")
    if e:
        w("\n## 外部連結")
        w(f"- docs 內文的外部連結：出現 {e['docs_occurrences']} 次、不重複 {e['docs_unique']} 個；"
          f"直接數 docs/*.md 原文：出現 {e['raw_md_occurrences']} 次、不重複 {e['raw_md_unique']} 個")
        if e["count_mismatch"]["only_rendered"] or e["count_mismatch"]["only_raw"]:
            w(f"  - 數字不一致：只在產出頁 {e['count_mismatch']['only_rendered']}；只在原文 {e['count_mismatch']['only_raw']}")
        w(f"- 樣板與手寫頁的外部連結：出現 {e['other_occurrences']} 次")
        w(f"- 實際請求的不重複網址：{e['checked_unique']} 個")
        cats = collections.Counter(v["category"] for v in e["results"].values())
        w("- 分類：" + "、".join(f"{k} {v}" for k, v in sorted(cats.items())))
        bad = [v for v in e["results"].values() if v["category"] != "正常"]
        if bad:
            where = collections.defaultdict(list)
            for o in e["occurrences"]:
                where[o["url"]].append(o["source"])
            w("\n| 狀態 | 網址 | 結果 | 出現位置 |\n|---|---|---|---|")
            for v in sorted(bad, key=lambda x: (x["category"], x["url"])):
                detail = v["error"] or f"{v['method']} {v['status']}"
                if v["final"] and v["final"] != v["url"].split("#")[0]:
                    detail += f"（轉址 {'/'.join(map(str, v['redirects']))}）→ {v['final']}"
                w(f"| {v['category']} | {md_escape(v['url'])} | {md_escape(detail)} | "
                  f"{'、'.join(sorted(set(where[v['url']])))} |")

    br = r.get("browser")
    if br:
        over = [m for m in br["mobile"] if m["sw"] > m["iw"]]
        w("\n## 手機版（375×812）")
        w(f"- 檢查 {len(br['mobile'])} 頁，水平溢出 {len(over)} 頁")
        for m in over:
            w(f"- {m['page']}：scrollWidth {m['sw']} > {m['iw']}")
            for o in m["offenders"]:
                w(f"  - `{o['el']}`（在 `{o['parent']}` 內，右緣 {o['right']}px）：{md_escape(o['text'])}")
        w("\n## 無障礙")
        w(f"- 結構問題 {len(br['a11y'])} 個")
        if br["a11y"]:
            w("\n| 頁面 | 問題 | 細節 |\n|---|---|---|")
            for a in br["a11y"]:
                w(f"| {a['page']} | {a['kind']} | {md_escape(a['detail'])} |")
        w(f"- 對比不足的組合 {len(br['contrast'])} 個（相同元素、顏色合併計算）")
        if br["contrast"]:
            w("\n| 模式 | 元素 | 文字色 | 背景色 | 對比 | 需要 | 範例文字 | 頁數 |\n|---|---|---|---|---|---|---|---|")
            for c in sorted(br["contrast"], key=lambda c: (c["scheme"], c["ratio"])):
                w(f"| {c['scheme']} | `{md_escape(c['el'])}` | {c['fg']} | {c['bg']} | {c['ratio']} | "
                  f"{c['need']} | {md_escape(c['text'])} | {len(c['pages'])} |")
    print("\n".join(out))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skip-external", action="store_true", help="不請求外部連結")
    ap.add_argument("--skip-browser", action="store_true", help="不跑 Playwright（手機版與無障礙）")
    ap.add_argument("--chromium", help="指定 Chromium 執行檔路徑")
    ap.add_argument("--json", help="把完整結果寫成 JSON")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    results = {}
    with tempfile.TemporaryDirectory(prefix="site-health-") as tmp_root:
        tmp = os.path.join(tmp_root, "site")
        copy_repo(tmp)
        results["build"] = check_build(tmp)
        results["internal"] = check_internal(tmp)
        if not args.skip_external:
            results["external"] = check_external(tmp)
        if not args.skip_browser:
            results["browser"] = check_browser(tmp, args.chromium)

    print_report(results)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=1)

    br = results.get("browser") or {}
    failing = (results["build"]["returncode"] != 0 or results["build"]["different"]
               or results["internal"]["problems"] or results["internal"]["table_overflow"]
               or any(m["sw"] > m["iw"] for m in br.get("mobile", []))
               or br.get("a11y") or br.get("contrast"))
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
