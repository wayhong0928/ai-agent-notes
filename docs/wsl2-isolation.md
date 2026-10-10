# WSL2 當隔離環境

> 查證日期：2026-10-10。WSL、Claude Code、Codex 的文件都改得很快，請以官方最新說明為準。本頁沒有實測任何隔離行為：寫「預期」的地方都出自官方文件，沒有官方句子撐的地方標「推論」。

想讓 Claude Code 或 Codex 放手做事，又怕它動到主機，很多人的第一個念頭是「丟進 WSL2 就好」。這頁先說明 WSL2 預設並沒有把 Linux 和 Windows 隔開，再把一個獨立的實驗 distro 調成比較封閉的狀態，最後講備份與還原。agent 自己的沙箱（Claude Code 的 `/sandbox`、Codex 的 sandbox mode）放在下一頁[Coding agent 沙箱](agent-sandbox.md)；還不確定自己需要哪幾層，可以先用那頁的[選擇器](agent-sandbox.md#一先選要疊幾層)。

## 一、WSL2 是什麼

WSL（Windows Subsystem for Linux）讓你在 Windows 上直接跑 Linux 發行版（distro，例如 Ubuntu）。WSL2 用一台由 Windows 代管的輕量虛擬機跑真正的 Linux 核心，Microsoft 的說法是「WSL2 runs Linux distributions as isolated containers inside the managed VM」[2]：每個 distro 是這台虛擬機裡的一個獨立容器，所有 distro 共用同一台虛擬機。

家用版可以用。Microsoft FAQ 原文：「WSL 2 is available on all Desktop SKUs where WSL is available, including Windows 10 Home and Windows 11 Home.」WSL2 需要兩個 Windows 功能：「Virtual Machine Platform」（Hyper-V 的子集）和「Windows Subsystem for Linux」[3]。

下一頁的兩個 agent 沙箱都只支援 WSL2，不支援 WSL1（出處見該頁），所以本頁一律以 WSL2 為準。

## 二、WSL2 跟 Windows 的邊界在哪

Microsoft 在 FAQ 列了 WSL 跟一般虛擬機不一樣的地方，其中幾條就是本頁要處理的邊界[3]：

- 「WSL automatically gives file access to Windows files.」
- 「Windows paths are appended to your path by default」
- 「WSL can run Windows executables from Linux」
- 「WSL users have full access to their Linux instances.」

這些預設是為了讓兩邊好整合。下表逐條列出預設開著的通道：

| 通道 | 預設 | 實際上代表什麼 | 怎麼關 |
|---|---|---|---|
| Windows 磁碟掛在 `/mnt/c` | 開：`[automount] enabled=true`，C 槽掛在 `/mnt/c`[4] | 沒有啟用 metadata 時（預設沒有），Linux 端看到的檔案權限是「把 Windows 使用者的有效權限換算成 rwx」[6] | `/etc/wsl.conf` 設 `[automount] enabled=false`；官方提醒關掉後「you could still mount them manually or via `fstab`」[4] |
| interop：從 Linux 啟動 Windows 程式 | 開：`[interop] enabled=true`[4] | 這樣啟動的 Windows 程式「Run as the active Windows user」，會出現在工作管理員裡[5] | `[interop] enabled=false`。另有一行暫時關閉的指令，但只在這次 session 有效，下次開又會恢復[5] |
| Windows 的 PATH 併進 Linux 的 `$PATH` | 開：`appendWindowsPath=true`[4] | 在 Linux 裡直接打 `notepad.exe` 這類名稱就叫得到 | `[interop] appendWindowsPath=false`[4] |
| 網路 | NAT[7] | 從 Linux 用主機 IP 可以連到 Windows 上跑的服務；mirrored 模式下甚至可以用 `127.0.0.1` 連[7] | `.wslconfig` 的 `networkingMode`，設成 `none` 會讓 WSL 網路斷線[4]。注意這是全域設定，見下表 |
| 從 Windows 看 Linux 檔案 | 開 | 在檔案總管網址列輸入 `\\wsl$` 就看得到每個 distro 的根目錄[5] | 本頁不處理；這是 Windows 那一側的存取 |

!!! warning "推論：預設 WSL2 裡的 agent，碰得到的 Windows 檔案大致等於你自己的帳號"
    上表前兩列合起來看（`/mnt/c` 權限照 Windows 使用者換算、Windows 程式以目前使用者身分執行），在沒改設定的 WSL2 裡讓 agent 不受限地跑指令，它能動到的 Windows 檔案範圍，大致就是你 Windows 帳號能動到的範圍。這是本站依 Microsoft 文件推出來的結論，Microsoft 沒有用這句話寫過。

### `.wslconfig` 和 `wsl.conf` 差在哪

兩個設定檔名字很像，管的範圍不同[4]：

| | `.wslconfig` | `wsl.conf` |
|---|---|---|
| 位置 | Windows 端的 `%UserProfile%\.wslconfig` | 每個 distro 裡的 `/etc/wsl.conf` |
| 範圍 | 所有 WSL2 distro 共用（官方：「General settings that apply to all of WSL」） | 只影響這一個 distro |
| 管什麼 | 虛擬機的記憶體、CPU、網路模式等 | 自動掛載、interop、預設使用者、systemd 等 |

要把「某一個實驗 distro」關起來，用的是 `wsl.conf`。`.wslconfig` 的網路設定會一起影響你平常用的 distro；把 `networkingMode` 設成 `none` 也會讓 agent 連不到它自家的 API（推論：Claude Code、Codex 都要連網才能跟模型溝通）。Microsoft 也建議改 `.wslconfig` 時優先用開始功能表裡的「WSL Settings」，不要手改檔案[4]。

改完設定要等 distro 完全停下來再啟動才會生效。官方說關掉所有該 distro 的視窗後通常要約 8 秒；想馬上生效可以用 `wsl --terminate <distro 名稱>` 立刻停掉那個 distro[4]。

## 三、安裝與確認版本

前提是 Windows 10 version 2004（Build 19041）以上，或 Windows 11[1]。用「以系統管理員身分執行」開 PowerShell：

```powershell
wsl --install
```

這行會開啟需要的 Windows 功能並安裝 Ubuntu，完成後要重新開機[1]。用 `wsl --install` 新裝的 distro 預設就是 WSL2[1]。重開機後確認版本：

```powershell
wsl -l -v
```

輸出會列出每個 distro 的名稱、狀態與 WSL 版本[8]。如果 VERSION 欄是 1，用 `wsl --set-version <distro 名稱> 2` 轉成 WSL2[1]；Microsoft 提醒轉換可能很花時間，也可能失敗，專案大的話先備份[8]。

## 四、用一個獨立 distro 當實驗場

平常寫作業、放 SSH 金鑰的那個 distro，不要拿來給 agent 放手做。另外開一個專門的 distro，玩壞了直接刪掉重建，主要的工作環境不受影響。WSL 允許同時裝很多個 distro[1]，但它們跑在同一台虛擬機裡[2]，`.wslconfig` 的設定一起套用[4]，用 `wsl --mount` 掛上的實體磁碟也會出現在所有 WSL2 distro 裡[8]。所以這裡說的「獨立」，是檔案系統和 `wsl.conf` 各自一份，不是各自一台虛擬機。

### 步驟 1：從乾淨的 distro 複製一份

`wsl --export` 匯出的是整個 distro 的快照[8]，`wsl --import` 再把它匯入成一個新名字的 distro[8]。以下假設你的 `Ubuntu` 是剛裝好的乾淨狀態，要匯入的新 distro 叫 `agent-lab`。Microsoft 的範例會先建好要存放 distro 的資料夾[9]：

```powershell
mkdir D:\wsl\base
mkdir D:\wsl\agent-lab
wsl --export Ubuntu D:\wsl\base\ubuntu-clean.tar
wsl --import agent-lab D:\wsl\agent-lab D:\wsl\base\ubuntu-clean.tar
wsl -d agent-lab
```

!!! warning "快照會整包帶走裡面的東西"
    匯出的是整個 distro 的快照。如果來源 distro 已經放了 SSH 金鑰、雲端服務的登入資訊或私人專案，匯入的 `agent-lab` 裡也會有一份。這種情況改用 `wsl --list --online` 找一個還沒裝過的 distro 安裝成乾淨的底[8]，再拿它來匯出。

### 步驟 2：建一般使用者

用 `--import` 匯入的 distro，預設以 root 登入[9]。先建一個一般使用者給 agent 用。Microsoft 的範例是 CentOS，下面是 Ubuntu 的寫法：

```bash
adduser xiaoming
usermod -aG sudo xiaoming
```

建立時設好密碼。建議不要把這個使用者設成免密碼 sudo（推論：agent 能直接 sudo，就能把下一步的設定改回去）。

### 步驟 3：用產生器寫 `wsl.conf`

勾選你要關掉的通道，下方會即時產生 `/etc/wsl.conf` 的內容和對應的代價。目前還是 root 的話，用 `nano /etc/wsl.conf` 之類的編輯器打開。檔案裡原本就有內容的話（例如 `[boot]` 段），保留原有段落，只新增或修改產生器列出的這幾段；整份覆蓋可能把 systemd 之類的設定一起拿掉，下一頁的 `sudo systemctl reload apparmor` 就可能失敗（推論）。

<style>
.wsx-panel { background: var(--panel); border: 1px solid var(--rule); border-radius: 10px; padding: 1rem 1.1rem; margin: 1.2rem 0 1.6rem; }
.wsx-panel-title { font-weight: 700; margin: 0 0 .6rem; color: var(--accent-ink); }
.wsx-opt { display: flex; gap: .55rem; align-items: flex-start; margin: .35rem 0; line-height: 1.6; cursor: pointer; }
.wsx-opt input { margin-top: .35rem; accent-color: var(--accent); flex: none; }
.wsx-user { display: flex; flex-wrap: wrap; gap: .5rem; align-items: center; margin: .7rem 0 .2rem; }
.wsx-user input { font: inherit; font-family: var(--mono); padding: .25rem .5rem; border: 1px solid var(--rule); border-radius: 6px; background: var(--bg); color: var(--ink); width: 11rem; max-width: 100%; }
.wsx-hint { font-size: .85rem; color: var(--ink-faint); margin: .2rem 0 0; }
.wsx-hint.wsx-bad { color: var(--warn-ink); }
.wsx-cost { margin: .6rem 0 0; padding-left: 1.2rem; font-size: .92rem; }
.wsx-cost li { margin: .25rem 0; }
.doc pre.wsx-pre { position: relative; padding-top: 2.1rem; }
.wsx-copy { position: absolute; top: .4rem; right: .45rem; font: inherit; font-size: .75rem; line-height: 1.2; padding: .25rem .6rem; border: 1px solid var(--rule); border-radius: 6px; background: var(--panel); color: var(--ink-soft); cursor: pointer; }
.wsx-copy:hover, .wsx-copy:focus-visible { border-color: var(--accent); color: var(--accent-ink); }
</style>

<div class="wsx-panel" id="wsx-gen">
<p class="wsx-panel-title">wsl.conf 產生器</p>
<label class="wsx-opt"><input type="checkbox" data-wsx="automount" checked><span>不自動掛載 Windows 磁碟（<code>[automount] enabled=false</code>）</span></label>
<label class="wsx-opt"><input type="checkbox" data-wsx="fstab"><span>也不處理 <code>/etc/fstab</code>（<code>[automount] mountFsTab=false</code>）</span></label>
<label class="wsx-opt"><input type="checkbox" data-wsx="interop" checked><span>不能從 Linux 啟動 Windows 程式（<code>[interop] enabled=false</code>）</span></label>
<label class="wsx-opt"><input type="checkbox" data-wsx="winpath" checked><span>不把 Windows 的 PATH 併進來（<code>[interop] appendWindowsPath=false</code>）</span></label>
<label class="wsx-opt"><input type="checkbox" data-wsx="user" checked><span>設定預設使用者（<code>[user] default=</code>）</span></label>
<div class="wsx-user"><label for="wsx-username">使用者名稱</label><input type="text" id="wsx-username" value="xiaoming" autocomplete="off" spellcheck="false"></div>
<p class="wsx-hint" id="wsx-userhint">要先用步驟 2 建好這個使用者。</p>
<pre><code id="wsx-out"></code></pre>
<p class="wsx-panel-title">這樣設的代價</p>
<ul class="wsx-cost" id="wsx-cost"></ul>
</div>

<script>
(function () {
  var root = document.getElementById("wsx-gen");
  if (!root) { return; }
  var out = document.getElementById("wsx-out");
  var cost = document.getElementById("wsx-cost");
  var nameInput = document.getElementById("wsx-username");
  var hint = document.getElementById("wsx-userhint");
  var COST = {
    automount: "Linux 裡看不到 C 槽。要把 Windows 的檔案放進來，從檔案總管開 \\\\wsl$\\agent-lab 再複製進去。官方提醒仍可手動掛載或透過 fstab 掛載[4]。",
    fstab: "/etc/fstab 裡宣告的其他檔案系統（例如網路磁碟）也不會在啟動時掛上[4]。",
    interop: "不能從 Linux 叫 Windows 程式。Claude Code 登入時可能開不了 Windows 的瀏覽器（推論），官方給的備案是按 c 複製登入網址，再把瀏覽器顯示的登入碼貼回終端機[12]。",
    winpath: "Linux 的 $PATH 裡不會有 Windows 的路徑。Claude Code 的安裝疑難頁在 nvm 情境下建議不要關這個，因為會叫不到 Windows 執行檔[12]；在實驗 distro 裡，叫不到正是目的。",
    user: "開啟這個 distro 時會用這個使用者登入，不再是 root。"
  };
  function checked(k) {
    var el = root.querySelector('input[data-wsx="' + k + '"]');
    return !!(el && el.checked);
  }
  function render() {
    var name = (nameInput.value || "").trim();
    var okName = /^[a-z_][a-z0-9_-]{0,31}$/.test(name);
    nameInput.disabled = !checked("user");
    hint.className = "wsx-hint" + (checked("user") && !okName ? " wsx-bad" : "");
    hint.textContent = !checked("user") ? "不設定的話，匯入的 distro 會用 root 登入。" :
      (okName ? "要先用步驟 2 建好這個使用者。" : "Linux 使用者名稱請用小寫英文、數字、底線或連字號，開頭不要用數字。");
    var lines = [];
    if (checked("user")) { lines.push("[user]", "default=" + (okName ? name : "xiaoming"), ""); }
    if (checked("automount") || checked("fstab")) {
      lines.push("[automount]");
      if (checked("automount")) { lines.push("enabled=false"); }
      if (checked("fstab")) { lines.push("mountFsTab=false"); }
      lines.push("");
    }
    if (checked("interop") || checked("winpath")) {
      lines.push("[interop]");
      if (checked("interop")) { lines.push("enabled=false"); }
      if (checked("winpath")) { lines.push("appendWindowsPath=false"); }
      lines.push("");
    }
    while (lines.length && lines[lines.length - 1] === "") { lines.pop(); }
    out.textContent = lines.length ? lines.join("\n") : "# 沒有勾選任何項目，wsl.conf 維持預設";
    cost.innerHTML = "";
    ["automount", "fstab", "interop", "winpath", "user"].forEach(function (k) {
      if (checked(k)) {
        var li = document.createElement("li");
        li.textContent = COST[k];
        cost.appendChild(li);
      }
    });
    if (!cost.children.length) {
      var li = document.createElement("li");
      li.textContent = "全部維持預設：這個 distro 跟平常的 WSL2 一樣，看得到 Windows 檔案、叫得到 Windows 程式。";
      cost.appendChild(li);
    }
  }
  root.addEventListener("change", render);
  nameInput.addEventListener("input", render);
  render();
})();
</script>

### 步驟 4：重開這個 distro 讓設定生效

回到 PowerShell：

```powershell
wsl --terminate agent-lab
wsl -d agent-lab
```

### 步驟 5：確認有效

在 `agent-lab` 裡逐行執行。右邊是依官方文件推得的預期，本站沒有實測：

| 指令 | 預期 | 依據 |
|---|---|---|
| `whoami` | 顯示你設的使用者，不是 `root` | `[user] default`[4] |
| `ls /mnt/c` | 看不到 Windows 的檔案 | `automount` 關掉後不會自動掛載[4] |
| `notepad.exe` | 啟動不了 Windows 程式 | interop 關掉會擋下啟動 Windows 程式[4] |

!!! danger "這一層擋得住意外，擋不住有 root 權限的程式"
    `/etc/wsl.conf` 是 distro 裡的一個檔案，Microsoft 也寫明關掉自動掛載後仍可手動掛載[4]。能用 root 權限的程式就能把它改回去或自己掛載（推論）。所以這一層只能讓 agent 預設碰不到 Windows，還要配合下一頁的 agent 沙箱一起用。

## 五、備份與還原

Microsoft FAQ 說，備份或搬移 distro 最好的方法就是 `wsl --export` 和 `wsl --import`[3]。把實驗 distro 調好、還沒讓 agent 動之前，先匯出一份：

```powershell
mkdir D:\wsl\backup
wsl --export agent-lab D:\wsl\backup\agent-lab-clean.tar
```

要還原時，建議先匯入成另一個名字，確認沒問題再處理舊的：

```powershell
wsl --import agent-lab-restore D:\wsl\agent-lab-restore D:\wsl\backup\agent-lab-clean.tar
wsl -d agent-lab-restore
```

進去後先跑 `whoami`。匯入的 distro 預設以 root 登入[9]，如果顯示 root，檢查 `/etc/wsl.conf` 的 `[user]` 是否還在。確認新的那份可以用，再刪掉舊的：

```powershell
wsl --unregister agent-lab
```

!!! danger "`--unregister` 刪了就回不來"
    官方原文：「Once unregistered, all data, settings, and software associated with that distribution will be permanently lost.」[8] 執行前確認備份檔存在，而且你剛才已經從它還原成功過一次。

## 六、檔案放 Linux 那邊，還是放 `/mnt/c`

| | 放 Linux 檔案系統（例如 `~/code/proj`） | 放 Windows 磁碟（`/mnt/c/...`） |
|---|---|---|
| 速度 | Microsoft 建議在 Linux 命令列工作時把檔案放這裡，速度最快[5] | WSL2 跨作業系統存取檔案比 WSL1 慢[2]；Claude Code 在這種路徑搜尋可能回傳比較少的結果[10]；Codex 文件也說會比較慢[11] |
| 權限 | 一般 Linux 權限 | 預設沒有 metadata，權限照 Windows 使用者換算；這時 `chmod` 只有一個作用：拿掉所有寫入權限會讓 Windows 檔案變成「唯讀」[6]。Codex 文件也提到放 Linux 家目錄會少一些 symlink 與權限問題[11] |
| 隔離 | 實驗 distro 關掉自動掛載後，在這裡工作的 agent 預設碰不到 Windows 檔案（依[4]） | 專案本身就在 Windows 磁碟上，agent 改專案就是直接改 Windows 檔案（推論） |
| 從 Windows 開 | 檔案總管輸入 `\\wsl$`[5] | 原本的 Windows 路徑 |

Microsoft、Anthropic、OpenAI 三方文件的方向一致：給 agent 用的專案放在 Linux 檔案系統裡，速度比較快，也配合得上前面關掉自動掛載的設定。

## 七、從安裝到驗證：勾選清單

勾選狀態只存在這台裝置的這個瀏覽器。

- [ ] 用系統管理員 PowerShell 跑 `wsl --install`，重新開機
- [ ] `wsl -l -v` 確認 VERSION 是 2
- [ ] 確認來源 distro 是乾淨的，匯出成 tar
- [ ] `wsl --import` 建立 `agent-lab`
- [ ] 在 `agent-lab` 裡建一般使用者（不設免密碼 sudo）
- [ ] 用產生器寫好 `/etc/wsl.conf`
- [ ] `wsl --terminate agent-lab` 後重新進入
- [ ] `whoami`、`ls /mnt/c`、`notepad.exe` 三個檢查都符合預期
- [ ] 把調好的 `agent-lab` 匯出一份備份
- [ ] 專案放在 `agent-lab` 的家目錄底下，不放 `/mnt/c`
- [ ] 接著到[下一頁](agent-sandbox.md)裝 agent 的沙箱

<script>
(function () {
  function copyText(text, done) {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done, function () { fallback(text, done); });
    } else { fallback(text, done); }
  }
  function fallback(text, done) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    document.body.removeChild(ta);
    done(ok);
  }
  document.querySelectorAll(".doc pre").forEach(function (pre) {
    if (pre.querySelector(".wsx-copy")) { return; }
    var code = pre.querySelector("code");
    if (!code) { return; }
    pre.classList.add("wsx-pre");
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "wsx-copy";
    btn.textContent = "複製";
    btn.setAttribute("aria-label", "複製這段指令");
    btn.addEventListener("click", function () {
      copyText(code.textContent, function (ok) {
        btn.textContent = ok === false ? "請手動選取" : "已複製";
        setTimeout(function () { btn.textContent = "複製"; }, 1600);
      });
    });
    pre.appendChild(btn);
  });
})();
</script>

## 本頁重點回顧

- WSL2 用一台代管的虛擬機跑 Linux，所有 distro 共用這台虛擬機；家用版也能用。
- 預設的 WSL2 會把 C 槽掛在 `/mnt/c`、允許從 Linux 啟動 Windows 程式、把 Windows 的 PATH 併進來，這些通道都要自己關。
- 關的方法是在實驗 distro 的 `/etc/wsl.conf` 設 `[automount] enabled=false` 與 `[interop] enabled=false`、`appendWindowsPath=false`；`.wslconfig` 是全域設定，會影響所有 distro。
- 有 root 權限的程式改得回這些設定，所以這一層要跟 agent 的沙箱一起用。
- 用 `wsl --export`／`wsl --import` 備份與還原；`wsl --unregister` 會永久刪除。
- 給 agent 的專案放在 Linux 檔案系統，速度比較快，也配合得上關掉自動掛載的設定。

## 資料來源

| 標記 | 來源 | URL |
|---|---|---|
| [1] | Install WSL（安裝前提、`wsl --install`、預設 WSL2、`--set-version`） | <https://learn.microsoft.com/en-us/windows/wsl/install> |
| [2] | Comparing WSL Versions（WSL2 架構、跨作業系統檔案效能） | <https://learn.microsoft.com/en-us/windows/wsl/compare-versions> |
| [3] | WSL FAQ（家用版支援、與一般 VM 的差異、備份建議） | <https://learn.microsoft.com/en-us/windows/wsl/faq> |
| [4] | Advanced settings configuration in WSL（`wsl.conf`、`.wslconfig`、8 秒規則、`networkingMode`） | <https://learn.microsoft.com/en-us/windows/wsl/wsl-config> |
| [5] | Working across file systems（檔案放哪裡、`\\wsl$`、從 Linux 執行 Windows 工具、暫時關 interop） | <https://learn.microsoft.com/en-us/windows/wsl/filesystems> |
| [6] | File Permissions for WSL（DrvFs 權限換算、`chmod` 行為） | <https://learn.microsoft.com/en-us/windows/wsl/file-permissions> |
| [7] | Accessing network applications with WSL（NAT、mirrored 模式） | <https://learn.microsoft.com/en-us/windows/wsl/networking> |
| [8] | Basic commands for WSL（`-l -v`、`--export`、`--import`、`--unregister`、`--mount`） | <https://learn.microsoft.com/en-us/windows/wsl/basic-commands> |
| [9] | Import any Linux distribution to use with WSL（匯入預設 root、預先建資料夾） | <https://learn.microsoft.com/en-us/windows/wsl/use-custom-distro> |
| [10] | Claude Code Troubleshooting（WSL 跨檔案系統搜尋結果變少） | <https://code.claude.com/docs/en/troubleshooting> |
| [11] | Codex：WSL（`/mnt/c` 較慢、放 Linux 家目錄） | <https://learn.chatgpt.com/docs/windows/wsl> |
| [12] | Claude Code Troubleshoot installation（WSL2 登入貼登入碼、`appendWindowsPath` 的提醒） | <https://code.claude.com/docs/en/troubleshoot-install> |

延伸：[Coding agent 沙箱：Claude Code 與 Codex](agent-sandbox.md)｜[Claude Code 設定總覽](official-config.md)｜[AI Agent 怎麼運作](agent-basics.md)
