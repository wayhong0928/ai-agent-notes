/* 研究方法知識網絡 —— 共用互動 */
(function () {
  "use strict";

  /* 主題切換（localStorage 可能被封鎖，一律包 try/catch） */
  function readTheme() {
    try { return localStorage.getItem("rm-theme"); } catch (e) { return null; }
  }
  function writeTheme(v) {
    try { localStorage.setItem("rm-theme", v); } catch (e) { /* 忽略 */ }
  }
  function readVisited(slug) {
    try {
      var raw = localStorage.getItem("rm-visited:" + slug);
      if (raw === null) { return null; }
      var value = Number(raw);
      return Number.isFinite(value) && value > 0 ? value : null;
    } catch (e) {
      return null;
    }
  }
  function writeVisited(slug, value) {
    try { localStorage.setItem("rm-visited:" + slug, String(value)); } catch (e) { /* 忽略 */ }
  }
  /* 以「日」為單位比較更新時間，避免同一天內多次瑣碎修改重複觸發已更新徽章
     （用本機時區的年/月/日，不是 UTC，貼近使用者對「今天」的認知） */
  function dayNumber(unixSeconds) {
    var d = new Date(unixSeconds * 1000);
    return d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate();
  }
  function addUpdateBadge(link) {
    if (link.querySelector(".rm-update-badge")) { return; }
    var badge = document.createElement("span");
    badge.className = "rm-update-badge";
    badge.textContent = "更新";
    badge.title = "自上次瀏覽後已更新";
    link.appendChild(badge);
  }
  function installUpdateStyles() {
    var style = document.createElement("style");
    style.textContent =
      ".rm-update-badge{display:inline-block;margin-inline-start:.45em;padding:.05em .38em;" +
      "border-radius:999px;background:#b54708;color:#fff;font-size:.7em;font-weight:700;" +
      "line-height:1.45;vertical-align:.1em}" +
      ".rm-update-note{margin:.75rem 0 1.25rem;padding:.65rem .85rem;border-inline-start:.25rem solid #b54708;" +
      "background:rgba(181,71,8,.1);font-size:.92rem}";
    document.head.appendChild(style);
  }
  var saved = readTheme();
  if (saved === "dark" || saved === "light") {
    document.documentElement.setAttribute("data-theme", saved);
  }
  var btn = document.createElement("button");
  btn.className = "themebtn";
  btn.type = "button";
  btn.setAttribute("aria-label", "切換淺色／深色");
  function paint() {
    var cur = document.documentElement.getAttribute("data-theme");
    var dark = cur === "dark" || (!cur && window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches);
    btn.textContent = dark ? "☀" : "☾";
  }
  btn.addEventListener("click", function () {
    var cur = document.documentElement.getAttribute("data-theme");
    var dark = cur === "dark" || (!cur && window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches);
    var next = dark ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    writeTheme(next);
    paint();
  });
  document.addEventListener("DOMContentLoaded", function () {
    /* 掛在 body 而非 #sidenav：.sidenav 手機版有 transform，會讓內部的
       position: fixed 子元素改吃 .sidenav 當定位基準，導致收合時按鈕消失。
       視覺上仍用 CSS 座標對齊到導覽列右上角，效果一樣，只是 DOM 位置不同。 */
    document.body.appendChild(btn);
    paint();
  });

  document.addEventListener("DOMContentLoaded", function () {

    /* 手機版導覽開合 */
    var toggle = document.getElementById("navtoggle");
    var nav = document.getElementById("sidenav");
    if (toggle && nav) {
      toggle.addEventListener("click", function () {
        nav.classList.toggle("open");
      });
      nav.addEventListener("click", function (e) {
        if (e.target.tagName === "A") { nav.classList.remove("open"); }
      });
    }

    /* 側欄區塊：預設全部展開，使用者可自行手動收合 */
    var navSections = nav ? nav.querySelectorAll(".navsec") : [];
    function setSectionExpanded(sec, expanded) {
      sec.classList.toggle("collapsed", !expanded);
      var sectionToggle = sec.querySelector(".navsec-toggle");
      if (sectionToggle) { sectionToggle.setAttribute("aria-expanded", expanded ? "true" : "false"); }
    }
    navSections.forEach(function (sec, index) {
      var heading = sec.querySelector("h2");
      if (!heading) { return; }
      var sectionToggle = document.createElement("button");
      var list = sec.querySelector("ul");
      sectionToggle.type = "button";
      sectionToggle.className = "navsec-toggle";
      sectionToggle.textContent = heading.textContent;
      if (list) {
        list.id = list.id || "navsec-list-" + index;
        sectionToggle.setAttribute("aria-controls", list.id);
      }
      heading.textContent = "";
      heading.appendChild(sectionToggle);
      setSectionExpanded(sec, true);
      sectionToggle.addEventListener("click", function () {
        var filterInput = document.getElementById("navfilter");
        if (filterInput && filterInput.value.trim() !== "") { return; }
        setSectionExpanded(sec, sec.classList.contains("collapsed"));
      });
    });
    if (nav) {
      try {
        var savedScroll = sessionStorage.getItem("rm-sidenav-scroll");
        if (savedScroll !== null && Number.isFinite(Number(savedScroll))) {
          nav.scrollTop = Number(savedScroll);
        }
      } catch (e) { /* 忽略 */ }
      nav.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", function () {
          try { sessionStorage.setItem("rm-sidenav-scroll", String(nav.scrollTop)); } catch (e) { /* 忽略 */ }
        });
      });
    }

    /* 對照來源檔更新時間與這個瀏覽器的上次瀏覽時間 */
    var updateLinks = document.querySelectorAll("#sidenav a[data-slug][data-updated]");
    var hasUpdateMarker = false;
    updateLinks.forEach(function (link) {
      var slug = link.getAttribute("data-slug");
      var updated = Number(link.getAttribute("data-updated"));
      var visited = readVisited(slug);
      if (visited !== null && Number.isFinite(updated) && dayNumber(updated) > dayNumber(visited)) {
        addUpdateBadge(link);
        hasUpdateMarker = true;
      }
    });

    var article = document.querySelector("article.doc[data-updated]");
    if (article) {
      var currentLink = document.querySelector("#sidenav li.active a[data-slug]");
      var currentSlug = currentLink ? currentLink.getAttribute("data-slug") : null;
      var articleUpdated = Number(article.getAttribute("data-updated"));
      var articleVisited = currentSlug ? readVisited(currentSlug) : null;
      if (articleVisited !== null && Number.isFinite(articleUpdated) && dayNumber(articleUpdated) > dayNumber(articleVisited)) {
        var lede = article.querySelector(".lede");
        if (lede) {
          var note = document.createElement("p");
          note.className = "rm-update-note";
          note.textContent = "這一頁自你上次瀏覽後已有更新。";
          lede.insertAdjacentElement("afterend", note);
          hasUpdateMarker = true;
        }
      }
      if (currentSlug) {
        writeVisited(currentSlug, Math.floor(Date.now() / 1000));
      }
    }
    if (hasUpdateMarker) { installUpdateStyles(); }

    /* 側欄篩選 */
    var filter = document.getElementById("navfilter");
    if (filter) {
      filter.addEventListener("input", function () {
        var q = filter.value.trim().toLowerCase();
        if (q !== "") {
          navSections.forEach(function (sec) {
            if (!sec.hasAttribute("data-filter-collapsed")) {
              sec.setAttribute("data-filter-collapsed", sec.classList.contains("collapsed") ? "true" : "false");
            }
          });
        }
        var items = nav.querySelectorAll(".navsec li");
        items.forEach(function (li) {
          var t = (li.textContent || "").toLowerCase();
          li.classList.toggle("hide", q !== "" && t.indexOf(q) === -1);
        });
        nav.querySelectorAll(".navsec").forEach(function (sec) {
          var any = sec.querySelectorAll("li:not(.hide)").length > 0;
          sec.style.display = any ? "" : "none";
          if (q !== "" && any) {
            setSectionExpanded(sec, true);
          } else if (q === "") {
            var wasCollapsed = sec.getAttribute("data-filter-collapsed");
            if (wasCollapsed !== null) {
              setSectionExpanded(sec, wasCollapsed !== "true");
              sec.removeAttribute("data-filter-collapsed");
            }
          }
        });
      });
    }

    /* 首頁卡片篩選 */
    var home = document.getElementById("homefilter");
    if (home) {
      home.addEventListener("input", function () {
        var q = home.value.trim().toLowerCase();
        document.querySelectorAll(".card").forEach(function (c) {
          var t = (c.textContent || "").toLowerCase();
          c.classList.toggle("hide", q !== "" && t.indexOf(q) === -1);
        });
        document.querySelectorAll(".mapsec").forEach(function (sec) {
          var any = sec.querySelectorAll(".card:not(.hide)").length > 0;
          sec.style.display = any ? "" : "none";
        });
      });
    }

    /* 右側目錄的目前位置標示 */
    var toc = document.getElementById("toc");
    if (toc && "IntersectionObserver" in window) {
      var links = {};
      toc.querySelectorAll("a[href^='#']").forEach(function (a) {
        links[decodeURIComponent(a.getAttribute("href").slice(1))] = a;
      });
      var heads = document.querySelectorAll(".doc h2[id], .doc h3[id]");
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          var a = links[en.target.id];
          if (!a) { return; }
          if (en.isIntersecting) {
            Object.keys(links).forEach(function (k) { links[k].classList.remove("here"); });
            a.classList.add("here");
          }
        });
      }, { rootMargin: "0px 0px -72% 0px", threshold: 0 });
      heads.forEach(function (h) { io.observe(h); });
    }

    /* 檢查清單狀態記在本機（僅此瀏覽器，清除網站資料就沒了） */
    var key = "rm-chk:" + location.pathname.split("/").pop();
    var boxes = document.querySelectorAll("li.chk input[type=checkbox]");
    if (boxes.length) {
      var state = [];
      try { state = JSON.parse(localStorage.getItem(key) || "[]"); } catch (e) { state = []; }
      boxes.forEach(function (b, i) {
        if (state[i]) { b.checked = true; }
        b.addEventListener("change", function () {
          var s = [];
          boxes.forEach(function (x) { s.push(x.checked ? 1 : 0); });
          try { localStorage.setItem(key, JSON.stringify(s)); } catch (e) { /* 忽略 */ }
        });
      });
    }
  });
})();
