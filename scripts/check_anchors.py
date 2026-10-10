#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查站內錨點：解析 pages/*.html 與根目錄的 *.html，確認每個站內 #錨點 都對得到目標頁的 id，
並列出還指向舊式自動編號 id（#_5、#42 這類）的連結。
用法：python3 scripts/check_anchors.py（兩項都是 0 才回傳 0）
"""
import os
import re
import sys
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HREF_RE = re.compile(r'href="([^"]*)"')
ID_RE = re.compile(r'\sid="([^"]*)"')
AUTO_RE = re.compile(r'^(_\d+|\d+(_\d+)?)$')


def html_files():
    files = [f for f in os.listdir(ROOT) if f.endswith(".html")]
    files += [os.path.join("pages", f) for f in os.listdir(os.path.join(ROOT, "pages"))
              if f.endswith(".html")]
    return sorted(files)


def main():
    files = html_files()
    ids = {}
    for f in files:
        text = open(os.path.join(ROOT, f), encoding="utf-8").read()
        ids[os.path.normpath(f)] = set(ID_RE.findall(text))
    total, broken, auto = 0, [], []
    for f in files:
        text = open(os.path.join(ROOT, f), encoding="utf-8").read()
        for href in HREF_RE.findall(text):
            if "#" not in href or re.match(r'^[a-z]+:', href):
                continue
            path, frag = href.split("#", 1)
            frag = unquote(frag)
            if not frag:
                continue
            target = os.path.normpath(os.path.join(os.path.dirname(f), path)) if path else os.path.normpath(f)
            total += 1
            if target not in ids:
                continue  # 檔案不存在不歸本腳本管（site_health.py 會抓）
            if frag not in ids[target]:
                broken.append((f, href))
            if AUTO_RE.match(frag):
                auto.append((f, href))
    print("站內錨點連結：%d 個" % total)
    print("對不到目標 id：%d 個" % len(broken))
    for f, h in broken:
        print("  %s → %s" % (f, h))
    print("指向自動編號 id：%d 個" % len(auto))
    for f, h in auto:
        print("  %s → %s" % (f, h))
    return 1 if broken or auto else 0


if __name__ == "__main__":
    sys.exit(main())
