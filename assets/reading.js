/* 閱讀追蹤頁：從側邊選單列出全站頁面，勾選讀過的頁面。
   紀錄只存在這個瀏覽器的 localStorage，鍵名前綴取自 #reading 的 data-site，
   同一網域下的其他站不會互相覆蓋。三個站共用這支檔案，改的時候三份一起改。 */
(function () {
  var box = document.getElementById("reading");
  if (!box) { return; }
  var SITE = box.getAttribute("data-site") || "site";
  var KEY = SITE + "-read";
  var UIKEY = SITE + "-read-ui";
  var SKIP = (box.getAttribute("data-skip") || "").split("|").filter(Boolean);

  function load(k) {
    try { return JSON.parse(localStorage.getItem(k) || "{}") || {}; } catch (e) { return {}; }
  }
  function save(k, v) {
    try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* 瀏覽器封鎖儲存時只是記不住 */ }
  }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;" }[c];
    });
  }
  function day(sec) {
    var d = new Date(sec * 1000);
    return d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2);
  }
  /* 跟 site.js 一樣以「日」比較，同一天內的修改不算讀後更新 */
  function dayNumber(sec) {
    var d = new Date(sec * 1000);
    return d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate();
  }

  var groups = [];
  document.querySelectorAll("#sidenav .navsec").forEach(function (sec) {
    var h = sec.querySelector("h2");
    var name = h ? h.textContent.trim() : "";
    if (SKIP.indexOf(name) >= 0) { return; }
    var items = [];
    sec.querySelectorAll("a[data-slug]").forEach(function (a) {
      items.push({ slug: a.getAttribute("data-slug"), title: a.getAttribute("data-title") || a.textContent.trim(),
                   href: a.getAttribute("href"), updated: Number(a.getAttribute("data-updated")) || 0 });
    });
    if (items.length) { groups.push({ name: name, items: items }); }
  });

  var ui = load(UIKEY);
  var filter = ui.filter || "unread";
  var group = ui.group || "all";
  var query = "";

  box.innerHTML =
    '<div class="rd-sum" id="rd-sum"></div>' +
    '<div class="rd-ctl"><div class="rd-seg" role="group" aria-label="顯示哪些頁面" id="rd-filter">' +
    '<button type="button" data-f="unread">還沒讀</button><button type="button" data-f="stale">讀後有更新</button>' +
    '<button type="button" data-f="read">讀過</button><button type="button" data-f="all">全部</button></div>' +
    '<input type="search" id="rd-q" placeholder="搜尋標題…" aria-label="搜尋標題"></div>' +
    '<div id="rd-list"></div>';

  function render() {
    var log = load(KEY);
    var q = query.trim().toLowerCase();
    var tot = 0, rd = 0, cards = "", list = "";
    groups.forEach(function (g, gi) {
      var gt = 0, gr = 0, rows = "";
      g.items.forEach(function (it) {
        var t = log[it.slug] || 0;
        var stale = !!t && it.updated && dayNumber(it.updated) > dayNumber(t / 1000);
        gt++; if (t) { gr++; }
        if (group !== "all" && group !== String(gi)) { return; }
        if (filter === "unread" && t) { return; }
        if (filter === "read" && !t) { return; }
        if (filter === "stale" && !stale) { return; }
        if (q && it.title.toLowerCase().indexOf(q) < 0) { return; }
        rows += '<li class="' + (t ? "is-read" : "") + '"><input type="checkbox" data-slug="' + esc(it.slug) + '"' + (t ? " checked" : "") +
          ' aria-label="' + esc(it.title) + ' 讀過"><span class="rd-t"><a href="' + esc(it.href) + '">' + esc(it.title) + "</a>" +
          (stale ? '<span class="rd-tag">讀後有更新</span><button type="button" class="rd-again" data-slug="' + esc(it.slug) + '">重讀完了</button>' : "") +
          '</span><span class="rd-meta">更新 ' + (it.updated ? day(it.updated) : "不明") + (t ? "<br>勾選 " + day(t / 1000) : "") + "</span></li>";
      });
      tot += gt; rd += gr;
      cards += '<button type="button" class="rd-card" data-g="' + gi + '" aria-pressed="' + (group === String(gi)) + '"><b>' + esc(g.name) +
        '</b><span>還沒讀 ' + (gt - gr) + "／共 " + gt + '</span><i class="rd-bar"><i style="width:' + (gt ? gr / gt * 100 : 0) + '%"></i></i></button>';
      if (rows) { list += "<h2>" + esc(g.name) + '</h2><ul class="rd-list">' + rows + "</ul>"; }
    });
    document.getElementById("rd-sum").innerHTML =
      '<button type="button" class="rd-card rd-all" data-g="all" aria-pressed="' + (group === "all") + '"><b>全站</b><span>還沒讀 ' + (tot - rd) + "／共 " + tot +
      '</span><i class="rd-bar"><i style="width:' + (tot ? rd / tot * 100 : 0) + '%"></i></i></button>' + cards;
    var empty = { unread: "這些頁面都讀過了。", stale: "沒有讀過之後又更新的頁面。", read: "還沒有勾選任何頁面。", all: "沒有符合的頁面。" }[filter];
    document.getElementById("rd-list").innerHTML = list || '<p class="rd-empty">' + (q ? "沒有符合「" + esc(query) + "」的頁面。" : empty) + "</p>";
    document.querySelectorAll("#rd-filter button").forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-f") === filter));
    });
  }
  function mark(slug, on) {
    var log = load(KEY);
    if (on) { log[slug] = Date.now(); } else { delete log[slug]; }
    save(KEY, log);
  }
  function saveUi() { save(UIKEY, { filter: filter, group: group }); }

  var listEl = document.getElementById("rd-list");
  listEl.addEventListener("change", function (e) {
    if (!e.target.matches("input[type=checkbox]")) { return; }
    mark(e.target.getAttribute("data-slug"), e.target.checked);
    render();
  });
  listEl.addEventListener("click", function (e) {
    if (!e.target.matches(".rd-again")) { return; }
    mark(e.target.getAttribute("data-slug"), true);
    render();
  });
  document.getElementById("rd-sum").addEventListener("click", function (e) {
    var b = e.target.closest(".rd-card");
    if (!b) { return; }
    group = b.getAttribute("data-g");
    saveUi(); render();
  });
  document.getElementById("rd-filter").addEventListener("click", function (e) {
    var b = e.target.closest("button");
    if (!b) { return; }
    filter = b.getAttribute("data-f");
    saveUi(); render();
  });
  document.getElementById("rd-q").addEventListener("input", function (e) { query = e.target.value; render(); });

  /* 匯出／匯入：換瀏覽器或換電腦時搬紀錄，匯入是合併，同一頁取較晚的勾選時間 */
  var msg = document.getElementById("rd-io-msg");
  var exp = document.getElementById("rd-export");
  var imp = document.getElementById("rd-import");
  var file = document.getElementById("rd-file");
  if (exp) {
    exp.addEventListener("click", function () {
      var blob = new Blob([JSON.stringify({ app: "reading-tracker", site: SITE, version: 1,
        exported: new Date().toISOString(), read: load(KEY) }, null, 1)], { type: "application/json" });
      var a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "reading-" + SITE + "-" + day(Date.now() / 1000) + ".json";
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
      if (msg) { msg.textContent = "已匯出。"; }
    });
  }
  if (imp && file) {
    imp.addEventListener("click", function () { file.click(); });
    file.addEventListener("change", function () {
      var f = file.files[0];
      if (!f) { return; }
      var r = new FileReader();
      r.onload = function () {
        try {
          var d = JSON.parse(r.result);
          if (d.app !== "reading-tracker" || d.site !== SITE) { throw new Error("這個檔案不是本站閱讀追蹤匯出的"); }
          var log = load(KEY), n = 0;
          Object.keys(d.read || {}).forEach(function (k) {
            var v = d.read[k];
            if (typeof v === "number" && v > (log[k] || 0)) { log[k] = v; n++; }
          });
          save(KEY, log);
          if (msg) { msg.textContent = "已匯入，合併了 " + n + " 筆。"; }
          render();
        } catch (err) {
          if (msg) { msg.textContent = "匯入失敗：" + err.message; }
        }
        file.value = "";
      };
      r.readAsText(f, "utf-8");
    });
  }

  render();
})();
