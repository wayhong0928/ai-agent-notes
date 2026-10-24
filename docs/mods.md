# Mods：在 Claude Code 裡加自己的功能

> 查證日期：2026-10-19（Claude Code v2.1.303）。mod 是很新的功能，事件與 API 可能隨版本調整，請以官方最新說明為準。

[擴充機制那頁](extensions.md)講的 SKILL、MCP、Hooks，都從 Claude Code 外面接進來。mod 則跑在程式裡面，官方的定義是「A mod is a plugin that changes how Claude Code looks and behaves」，內容是一組 JavaScript 或 TypeScript 函式[1]。所以它做得到外接機制做不到的事，例如在對話旁邊開一個側欄，或加一個打下去就直接回答、不用等 Claude 想一輪的 `/指令`。

這頁先講 mod 跟其他機制差在哪，再講它怎麼運作，最後用我自己做的 TODO 側欄當例子，從頭走一遍。

## 一、mod 跟 settings hook、skill、MCP 差在哪

官方文件把 mod 裡的函式也叫 hook，寫在 `settings.json` 的那種改稱「settings hook」[1]。這頁照官方的叫法。

<figure class="diagram">
<svg class="dg-wide" viewBox="0 0 700 260" role="img" aria-labelledby="dgmod2-w">
<title id="dgmod2-w">mod 跟其他三種機制的位置。mod 的函式跑在 Claude Code 程式裡面，能畫側欄與輸入框上方的提示帶、改寫或接手工具呼叫與 prompt、加不開模型回合的指令。settings hook、skill、MCP server 都從外面接進來：settings hook 在事件發生時跑腳本，決定放行、擋下或補充 context；skill 是一份 SKILL.md，Claude 讀了照做；MCP server 是外部程式，替 Claude 多加工具。</title>
<defs><marker id="dgmod2-hw" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="dg-head" d="M0,0 L10,5 L0,10 z"/></marker></defs>
<rect class="dg-note" x="10" y="10" width="330" height="240" rx="12"/>
<text class="dg-l" x="26" y="32">Claude Code 程式裡面</text>
<rect class="dg-key" x="26" y="46" width="298" height="190" rx="10"/>
<text class="dg-c" x="42" y="74">Mod</text>
<text class="dg-s" x="42" y="102">JavaScript／TypeScript 函式</text>
<text class="dg-s" x="42" y="128">畫側欄、輸入框上方的提示帶</text>
<text class="dg-s" x="42" y="154">改寫或接手工具呼叫、prompt</text>
<text class="dg-s" x="42" y="180">加不開模型回合的 /指令</text>
<text class="dg-s" x="42" y="206">也能做 settings hook 做的事</text>
<text class="dg-l" x="380" y="32">從外面接進來</text>
<rect class="dg-box" x="380" y="46" width="310" height="58" rx="10"/>
<text class="dg-c" x="396" y="70">Settings hook</text>
<text class="dg-s" x="396" y="92">事件發生時跑腳本，放行、擋下、補 context</text>
<rect class="dg-box" x="380" y="114" width="310" height="58" rx="10"/>
<text class="dg-c" x="396" y="138">Skill</text>
<text class="dg-s" x="396" y="160">一份 SKILL.md，Claude 讀了照做</text>
<rect class="dg-box" x="380" y="182" width="310" height="58" rx="10"/>
<text class="dg-c" x="396" y="206">MCP server</text>
<text class="dg-s" x="396" y="228">外部程式，替 Claude 多加工具</text>
<path class="dg-line" d="M378,75 L344,75" marker-end="url(#dgmod2-hw)"/>
<path class="dg-line" d="M378,143 L344,143" marker-end="url(#dgmod2-hw)"/>
<path class="dg-line" d="M378,211 L344,211" marker-end="url(#dgmod2-hw)"/>
</svg>
<svg class="dg-narrow" viewBox="0 0 350 470" role="img" aria-labelledby="dgmod2-n">
<title id="dgmod2-n">mod 跟其他三種機制的位置。mod 的函式跑在 Claude Code 程式裡面，能畫側欄與輸入框上方的提示帶、改寫或接手工具呼叫與 prompt、加不開模型回合的指令。settings hook、skill、MCP server 都從外面接進來：settings hook 在事件發生時跑腳本，決定放行、擋下或補充 context；skill 是一份 SKILL.md，Claude 讀了照做；MCP server 是外部程式，替 Claude 多加工具。</title>
<defs><marker id="dgmod2-hn" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="dg-head" d="M0,0 L10,5 L0,10 z"/></marker></defs>
<rect class="dg-note" x="10" y="10" width="330" height="210" rx="12"/>
<text class="dg-l" x="26" y="32">Claude Code 程式裡面</text>
<rect class="dg-key" x="26" y="44" width="298" height="162" rx="10"/>
<text class="dg-c" x="42" y="70">Mod</text>
<text class="dg-s" x="42" y="96">JavaScript／TypeScript 函式</text>
<text class="dg-s" x="42" y="120">畫側欄、輸入框上方的提示帶</text>
<text class="dg-s" x="42" y="144">改寫或接手工具呼叫、prompt</text>
<text class="dg-s" x="42" y="168">加不開模型回合的 /指令</text>
<text class="dg-s" x="42" y="192">也能做 settings hook 做的事</text>
<path class="dg-line" d="M175,252 L175,224" marker-end="url(#dgmod2-hn)"/>
<text class="dg-l" x="26" y="270">從外面接進來</text>
<rect class="dg-box" x="26" y="280" width="298" height="56" rx="10"/>
<text class="dg-c" x="42" y="302">Settings hook</text>
<text class="dg-s" x="42" y="324">跑腳本，放行、擋下、補 context</text>
<rect class="dg-box" x="26" y="344" width="298" height="56" rx="10"/>
<text class="dg-c" x="42" y="366">Skill</text>
<text class="dg-s" x="42" y="388">一份 SKILL.md，Claude 讀了照做</text>
<rect class="dg-box" x="26" y="408" width="298" height="56" rx="10"/>
<text class="dg-c" x="42" y="430">MCP server</text>
<text class="dg-s" x="42" y="452">外部程式，替 Claude 多加工具</text>
</svg>
<figcaption>四種機制裡只有 mod 能畫介面，依官方比較表整理[1]。「也能做 settings hook 做的事」指 mod 同樣能擋下或放行工具呼叫[3]。</figcaption>
</figure>

| | Mod | Settings hook | Skill | MCP server |
|---|---|---|---|---|
| 要寫什麼 | JavaScript 或 TypeScript | 一支腳本加 `settings.json` 一筆設定 | Markdown | 任何語言寫的 server |
| 能不能畫介面 | 能 | 不能 | 不能 | 不能 |
| 什麼時候選它 | 想要側欄、提示帶、自訂指令，或改寫事件 | 手上已有腳本，只想擋下、放行或記錄某個事件 | 一直在對話裡貼同一段指示 | Claude 要連到外部系統 |

表格依官方比較表翻譯整理[1]。官方的建議是，settings hook、skill 或 MCP 已經能做到的事，先比較過再決定要不要寫 mod[1]。

## 二、運作原理：事件、hook、三種處理方式

Claude Code 在事件發生時呼叫你的函式，例如 Claude 要用工具、你送出一段 prompt、畫面上某一塊要重畫[1]。函式會拿到三個東西：mods API（寫成 `$`）、事件本身（`e`）、下一個處理者（`next`）[3]。

<figure class="diagram">
<svg class="dg-wide" viewBox="0 0 700 300" role="img" aria-labelledby="dgmod1-w">
<title id="dgmod1-w">mod 的運作方式。事件發生，例如 Claude 要用工具、你打了指令、畫面要重畫，Claude Code 就呼叫你的 hook。hook 拿到 $、e、next 三個參數，三選一：觀察，呼叫 next(e) 原樣放行；改寫，改過 e 再交給 next；接手，不呼叫 next，自己回傳結果。hook 要讀檔、畫面板、加指令或存值，一律透過 $ 也就是 mods API。</title>
<defs><marker id="dgmod1-hw" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="dg-head" d="M0,0 L10,5 L0,10 z"/></marker></defs>
<rect class="dg-you" x="10" y="80" width="170" height="96" rx="10"/>
<text class="dg-t" x="95" y="108" text-anchor="middle">事件發生</text>
<text class="dg-s" x="95" y="132" text-anchor="middle">Claude 要用工具</text>
<text class="dg-s" x="95" y="150" text-anchor="middle">你打了 /指令</text>
<text class="dg-s" x="95" y="168" text-anchor="middle">畫面要重畫</text>
<rect class="dg-key" x="240" y="80" width="190" height="96" rx="10"/>
<text class="dg-t" x="335" y="112" text-anchor="middle">你的 hook</text>
<text class="dg-s" x="335" y="136" text-anchor="middle">拿到 $、e、next</text>
<text class="dg-s" x="335" y="156" text-anchor="middle">決定這個事件怎麼走</text>
<rect class="dg-box" x="490" y="10" width="200" height="64" rx="10"/>
<text class="dg-t" x="506" y="36">觀察</text>
<text class="dg-s" x="506" y="58">呼叫 next(e)，原樣放行</text>
<rect class="dg-box" x="490" y="96" width="200" height="64" rx="10"/>
<text class="dg-t" x="506" y="122">改寫</text>
<text class="dg-s" x="506" y="144">改過 e 再交給 next</text>
<rect class="dg-box" x="490" y="182" width="200" height="64" rx="10"/>
<text class="dg-t" x="506" y="208">接手</text>
<text class="dg-s" x="506" y="230">不呼叫 next，自己回結果</text>
<rect class="dg-box" x="240" y="222" width="190" height="68" rx="10"/>
<text class="dg-c" x="256" y="248">$（mods API）</text>
<text class="dg-s" x="256" y="272">讀檔、畫面板、加指令、存值</text>
<path class="dg-line" d="M180,128 L238,128" marker-end="url(#dgmod1-hw)"/>
<path class="dg-line" d="M430,108 C462,100 458,42 488,42" marker-end="url(#dgmod1-hw)"/>
<path class="dg-line" d="M430,128 L488,128" marker-end="url(#dgmod1-hw)"/>
<path class="dg-line" d="M430,148 C462,156 458,214 488,214" marker-end="url(#dgmod1-hw)"/>
<path class="dg-dash" d="M335,176 L335,218" marker-end="url(#dgmod1-hw)"/>
</svg>
<svg class="dg-narrow" viewBox="0 0 350 492" role="img" aria-labelledby="dgmod1-n">
<title id="dgmod1-n">mod 的運作方式。事件發生，例如 Claude 要用工具、你打了指令、畫面要重畫，Claude Code 就呼叫你的 hook。hook 拿到 $、e、next 三個參數，三選一：觀察，呼叫 next(e) 原樣放行；改寫，改過 e 再交給 next；接手，不呼叫 next，自己回傳結果。hook 要讀檔、畫面板、加指令或存值，一律透過 $ 也就是 mods API。</title>
<defs><marker id="dgmod1-hn" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="dg-head" d="M0,0 L10,5 L0,10 z"/></marker></defs>
<rect class="dg-you" x="25" y="10" width="300" height="76" rx="10"/>
<text class="dg-t" x="175" y="36" text-anchor="middle">事件發生</text>
<text class="dg-s" x="175" y="58" text-anchor="middle">Claude 要用工具、你打了 /指令、</text>
<text class="dg-s" x="175" y="76" text-anchor="middle">畫面要重畫</text>
<path class="dg-line" d="M175,86 L175,112" marker-end="url(#dgmod1-hn)"/>
<rect class="dg-key" x="25" y="114" width="300" height="70" rx="10"/>
<text class="dg-t" x="175" y="142" text-anchor="middle">你的 hook</text>
<text class="dg-s" x="175" y="166" text-anchor="middle">拿到 $、e、next，決定事件怎麼走</text>
<path class="dg-line" d="M175,184 L175,208" marker-end="url(#dgmod1-hn)"/>
<rect class="dg-box" x="45" y="210" width="280" height="58" rx="10"/>
<text class="dg-t" x="61" y="234">觀察</text>
<text class="dg-s" x="61" y="256">呼叫 next(e)，原樣放行</text>
<rect class="dg-box" x="45" y="276" width="280" height="58" rx="10"/>
<text class="dg-t" x="61" y="300">改寫</text>
<text class="dg-s" x="61" y="322">改過 e 再交給 next</text>
<rect class="dg-box" x="45" y="342" width="280" height="58" rx="10"/>
<text class="dg-t" x="61" y="366">接手</text>
<text class="dg-s" x="61" y="388">不呼叫 next，自己回結果</text>
<rect class="dg-box" x="45" y="420" width="280" height="62" rx="10"/>
<text class="dg-c" x="61" y="446">$（mods API）</text>
<text class="dg-s" x="61" y="468">讀檔、畫面板、加指令、存值</text>
<path class="dg-dash" d="M25,149 L12,149 L12,451 L43,451" marker-end="url(#dgmod1-hn)"/>
</svg>
<figcaption>實線是事件的走向，虛線是 hook 需要碰外面的東西時的唯一管道，依官方說明整理[1][3][4]。</figcaption>
</figure>

三種處理方式的差別全在 `next`[3]：

- **觀察**：記下發生了什麼，呼叫 `next(e)` 讓事件照常進行。
- **改寫**：把 `e` 改過再交給 `next`，例如在 spinner 的文字後面加一段計數。
- **接手**：不呼叫 `next`，自己回傳結果，Claude Code 原本的行為就不會跑。官方範例是擋掉所有 Bash 指令，Claude 會把擋下的理由當成工具結果讀到。

hook 本身沒有 Node.js API，也不能自己讀檔或連網路。要讀檔用 `$.fs`、跑程式用 `$.process`、連網用 `$.http`、跨 session 存值用 `$.store`[4]。這個限制有好處，因為所有對外動作都經過 API，Claude Code 不用執行就列得出一個 mod 會做什麼（見第五節）[1]。

官方最小範例只有一個檔案，數 Claude 用了幾次工具，把次數顯示在 spinner 旁邊[1]：

```javascript
let calls = 0

export function register(on) {
  on('tool.call', async ($, e, next) => {
    calls += 1
    $.ui.invalidate('ui.render')   // 請 Claude Code 重畫，新數字才會出現
    return next(e)                 // 觀察：讓工具照常執行
  })

  on('ui.render', { component: 'Spinner' }, async ($, e, next) => {
    // 改寫：保留原本的 spinner，在後面加上次數
    return next({ ...e, props: { ...e.props, suffix: ' · tool calls: ' + calls + '…' } })
  })
}
```

兩個 hook 共用同一個 `calls` 變數，一個負責記，一個負責顯示。官方說明同一個 mod 的 hook 共用檔案裡的變數，一個 hook 記下的值，另一個拿來顯示[1]。

除了給你打的 `/指令`，mod 也能替 Claude 加一個工具讓它呼叫，兩種都在 `session.start` hook 裡註冊[4]。

### 事件有哪些

官方依用途把事件分成幾組，包括 Claude 每次用工具的前後、你打的字和 Claude Code 自己送給 Claude 的文字（例如 system prompt）、指令與 `/config`、一輪回答的開始到結束、session 的開始結束和 compact、subagent、介面，還有用量紀錄[6]。寫在 `settings.json` 的那些 settings hook 事件，mod 也收得到，名稱是 `classic.<Event>`，例如 `classic.Stop`，`e` 就是 settings hook 從 stdin 拿到的那份 JSON[6]。

`session.start` 的時機要特別注意。它在每個 mod 載入後、第一個 prompt 之前跑一次，這個 mod 重新載入後會再跑一次，但 `/clear`、`/resume`、`/branch` 之後不會跑[6]。

介面這邊，mod 除了能開自己的側欄（`Pane`）和輸入框上方的提示帶（`AbovePrompt`），也能接手 Claude Code 自己畫的很多位置，例如你的訊息、Claude 的回覆、工具呼叫那一列、spinner、Claude 問你問題的對話框[6]。權限提示是例外，mod 改不了它的樣式，也改不了它顯示的內容[1]。

hook 有時間限制。一個事件上，hook 自己的執行時間最多 10 秒（`prompt.edit` 是 50 毫秒），等 `next` 和呼叫 mods API 的時間不算（`$.clock.sleep` 除外），超過就會被跳過[6]。指令、工具、subagent 類型和側欄的名稱只能用英文字母、數字、`_`、`-`，最長 64 個字元[6]。

### 好幾個 mod 和 settings hook 誰先跑

同一個事件上的 hook 串成一條鏈。每個 mod 的 `next` 呼叫下一個 mod 的 hook，最後一個 `next` 才到 Claude Code 本來的行為[3]。排最前面的 mod 最先看到事件、最後拿到結果，也決定後面的 mod 跑不跑；後面的 mod 擋不住前面的 mod 看到事件[3]。你自己裝的 mod 之間，一個 mod 會排在它 manifest 裡 `dependencies` 列出的 mod 前面；同一個檔案裡，hook 照 `register` 呼叫 `on` 的順序跑[3]。

`settings.json` 和 plugin `hooks/hooks.json` 裡的 `PreToolUse` hook，在最後一個 mod 呼叫 `next` 之後才跑，算是 Claude Code 本來行為的一部分[3]。所以 mod 自己接手 `tool.call`、沒有呼叫 `next` 的話，你的 `PreToolUse` hook 就不會跑；有呼叫 `next` 的 mod，則會在拿回的結果裡看到它們的決定[3]。組織 managed settings 裡的 `PreToolUse` hook 例外，它們在第一個 mod 之前就跑，擋下的呼叫任何 mod 都看不到[3]。

### hook 出錯時

hook 丟出錯誤、超時或回傳的格式不對，session 不會因此壞掉[3]。還沒呼叫 `next` 就失敗的 hook 會被跳過，由下一個處理者接著跑；呼叫過 `next` 才失敗的，`next` 的結果照算，不會重跑一次[3]。所以一個負責擋指令的 hook 自己出錯時，指令會照常執行。要讓它出錯時改成擋下，在註冊時接一個 `.catch`，官方範例如下[3]：

```javascript
// on returns a registration, and .catch attaches a handler to that one hook
on('tool.call', { tool: 'Bash' }, guard).catch(async ($, e, next) => {
  // guard had already called next, so return what came back
  if (next.called) return next(e)
  // next.error.kind says why the handler was asked, such as 'throw' or 'timeout'
  return { deny: 'The command guard failed, so this command was not run: ' + next.error.kind }
})
```

`guard` 是你自己的 hook 函式。`.catch` 裡的處理者也有自己的時間限制，它本身再出錯，Claude Code 就當作沒有處理者，直接跳過這個 hook[3]。

## 三、實例：做一個 TODO 側欄

我同時在跑好幾個專案，每個專案各有一份 `TODO.md`。原本要看待辦得請 Claude 讀檔，每次都要等它想一輪，讀進來的內容也會佔掉對話的 context。所以我請 Claude 寫了一個 mod，做到三件事：開 session 時側欄自動列出未完成的條目，打 `/todo` 立刻回一份清單，Claude 改了 TODO 檔，側欄跟著更新。

<figure class="diagram">
<svg class="dg-wide" viewBox="0 0 700 300" role="img" aria-labelledby="dgmod3-w">
<title id="dgmod3-w">TODO 側欄 mod 的資料流。左邊是各專案的 TODO.md。中間是 mod 裡負責讀檔的三個 hook：session.start 在開場讀檔、註冊 /todo、開側欄；tool.call 在 Claude 用 Edit 或 Write 改到 TODO 檔時重讀；command.run 在你打 /todo 時回一份清單。右邊有兩個出口：側欄由 ui.render 畫在畫面上；/todo 的回覆是對話裡的文字，Claude 之後讀得到。</title>
<defs><marker id="dgmod3-hw" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="dg-head" d="M0,0 L10,5 L0,10 z"/></marker></defs>
<rect class="dg-box" x="10" y="110" width="150" height="70" rx="10"/>
<text class="dg-t" x="85" y="140" text-anchor="middle">各專案 TODO.md</text>
<text class="dg-s" x="85" y="162" text-anchor="middle">未勾選的條目</text>
<rect class="dg-key" x="220" y="10" width="250" height="280" rx="12"/>
<text class="dg-t" x="345" y="36" text-anchor="middle">/todo mod</text>
<rect class="dg-box" x="236" y="52" width="218" height="66" rx="10"/>
<text class="dg-c" x="252" y="76">session.start</text>
<text class="dg-s" x="252" y="98">開場讀檔、註冊 /todo、開側欄</text>
<rect class="dg-box" x="236" y="130" width="218" height="66" rx="10"/>
<text class="dg-c" x="252" y="154">tool.call</text>
<text class="dg-s" x="252" y="176">Claude 改到 TODO 檔就重讀</text>
<rect class="dg-box" x="236" y="208" width="218" height="66" rx="10"/>
<text class="dg-c" x="252" y="232">command.run</text>
<text class="dg-s" x="252" y="254">你打 /todo 時回一份清單</text>
<rect class="dg-you" x="530" y="40" width="160" height="90" rx="10"/>
<text class="dg-t" x="546" y="66">側欄</text>
<text class="dg-s" x="546" y="90">ui.render 畫出來</text>
<text class="dg-s" x="546" y="110">畫在畫面上</text>
<rect class="dg-box" x="530" y="170" width="160" height="90" rx="10"/>
<text class="dg-t" x="546" y="196">對話裡的文字</text>
<text class="dg-s" x="546" y="220">/todo 的回覆</text>
<text class="dg-s" x="546" y="240">Claude 之後讀得到</text>
<path class="dg-line" d="M160,130 C196,130 200,85 234,85" marker-end="url(#dgmod3-hw)"/>
<path class="dg-line" d="M160,145 L234,160" marker-end="url(#dgmod3-hw)"/>
<path class="dg-line" d="M160,160 C196,170 200,241 234,241" marker-end="url(#dgmod3-hw)"/>
<path class="dg-line" d="M454,85 L528,85" marker-end="url(#dgmod3-hw)"/>
<path class="dg-line" d="M454,163 C490,163 496,110 528,105" marker-end="url(#dgmod3-hw)"/>
<path class="dg-line" d="M454,241 C490,241 496,215 528,215" marker-end="url(#dgmod3-hw)"/>
</svg>
<svg class="dg-narrow" viewBox="0 0 350 476" role="img" aria-labelledby="dgmod3-n">
<title id="dgmod3-n">TODO 側欄 mod 的資料流。上面是各專案的 TODO.md。中間是 mod 裡負責讀檔的三個 hook：session.start 在開場讀檔、註冊 /todo、開側欄；tool.call 在 Claude 用 Edit 或 Write 改到 TODO 檔時重讀；command.run 在你打 /todo 時回一份清單。下面有兩個出口：側欄由 ui.render 畫在畫面上；/todo 的回覆是對話裡的文字，Claude 之後讀得到。</title>
<defs><marker id="dgmod3-hn" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="dg-head" d="M0,0 L10,5 L0,10 z"/></marker></defs>
<rect class="dg-box" x="25" y="10" width="300" height="56" rx="10"/>
<text class="dg-t" x="175" y="34" text-anchor="middle">各專案 TODO.md</text>
<text class="dg-s" x="175" y="54" text-anchor="middle">未勾選的條目</text>
<path class="dg-line" d="M175,66 L175,84" marker-end="url(#dgmod3-hn)"/>
<rect class="dg-key" x="10" y="86" width="330" height="250" rx="12"/>
<text class="dg-t" x="175" y="110" text-anchor="middle">/todo mod</text>
<rect class="dg-box" x="26" y="122" width="298" height="64" rx="10"/>
<text class="dg-c" x="42" y="146">session.start</text>
<text class="dg-s" x="42" y="168">開場讀檔、註冊 /todo、開側欄</text>
<rect class="dg-box" x="26" y="194" width="298" height="64" rx="10"/>
<text class="dg-c" x="42" y="218">tool.call</text>
<text class="dg-s" x="42" y="240">Claude 改到 TODO 檔就重讀</text>
<rect class="dg-box" x="26" y="266" width="298" height="64" rx="10"/>
<text class="dg-c" x="42" y="290">command.run</text>
<text class="dg-s" x="42" y="312">你打 /todo 時回一份清單</text>
<path class="dg-line" d="M120,336 L90,364" marker-end="url(#dgmod3-hn)"/>
<path class="dg-line" d="M230,336 L260,364" marker-end="url(#dgmod3-hn)"/>
<rect class="dg-you" x="10" y="366" width="160" height="100" rx="10"/>
<text class="dg-t" x="26" y="392">側欄</text>
<text class="dg-s" x="26" y="416">ui.render 畫出來</text>
<text class="dg-s" x="26" y="436">畫在畫面上</text>
<rect class="dg-box" x="180" y="366" width="160" height="100" rx="10"/>
<text class="dg-t" x="196" y="392">對話裡的文字</text>
<text class="dg-s" x="196" y="416">/todo 的回覆</text>
<text class="dg-s" x="196" y="436">Claude 讀得到</text>
</svg>
<figcaption>TODO 側欄 mod 讀檔的部分。三個 hook 都經過 <code>$.fs</code> 讀檔；側欄跟指令回覆是兩個不同的出口[2][4]。</figcaption>
</figure>

主要的工作由四種事件完成：

| 事件 | 在這個 mod 裡做什麼 |
|---|---|
| `session.start` | 用 `$.command.register` 註冊 `/todo`，讀一次所有 TODO 檔，再用 `$.ui.open` 開側欄 |
| `command.run` | 你打 `/todo` 或 `/todo 專案名` 時，直接回傳清單文字，不開模型回合 |
| `tool.call` | 只盯 Edit 和 Write。先呼叫 `next(e)` 讓工具照常執行，執行完如果改的是 TODO 檔就重讀一次 |
| `ui.render` | 畫側欄。用 `Box`、`Text` 這類元件排版，寫法像 React，過期的條目標紅色 |

另外還接了三種事件，處理輸入框和側欄的小細節。你在輸入框打 `/todo c` 時，自動完成會列出名稱含 c 的專案和各自的條數（`prompt.autocomplete`）。輸入框只有 `/todo` 時，後面會淡淡顯示總條數，不會寫進草稿（`prompt.edit`）。你自己把側欄關掉時，mod 用 `$.store` 記下來，之後開 session 就不再自動打開（`ui.close`）。`$.store` 存成一個 JSON 檔，跨 session 都在[2]。

做的過程中踩到三件事，官方文件都有寫，只是我一開始沒讀到：

1. **重開 session 之後 `/todo` 變成 Unknown command。** 請 Claude 寫的 mod 放在 `~/.claude/dev-mods/<session ID>/` 底下，只在寫它的那個 session 載入，超過 `cleanupPeriodDays` 還會被清掉[5]。解法是把資料夾搬到自己的位置，再用以下任一種方式載入。啟動時加 `claude --plugin-dir <資料夾>`[5]，或在 `~/.claude/settings.json` 的 `env` 設 `CLAUDE_CODE_PLUGIN_DIRS`，Windows 上多個路徑用 `;` 分隔[6]。我用第二種，每個 session 都會載入。要給別人用，官方的做法是放進 marketplace 讓對方安裝[5]。
2. **指令的回覆會進對話。** 官方寫明，指令回傳的 `text` 會印在對話記錄裡，而且 Claude 會讀到[4]。所以 `/todo` 不開模型回合、不用等，但清單文字還是留在對話裡。只想自己看、不想讓 Claude 讀的東西，我放在側欄。官方文件沒有寫側欄的內容會送給 Claude，這是我依此做的設計選擇。
3. **側欄自己開不一定看得到。** mod 自己開的側欄，終端機要至少 144 欄寬才會出現；你親手開過一次之後，110 欄就夠。你打指令開的側欄，多窄都會出現[2]。側欄在全螢幕的寬終端機裡排在對話旁邊，窄的時候變成輸入框上方的一塊[2]。

## 四、自己做一個

最快的方式是直接請 Claude 寫。Claude Code 內建一個叫 `plugin-authoring` 的 skill，裡面寫了 mod 該放哪、你的版本有哪些事件與 API[5]。流程如下[5]：

1. 在互動式 session 裡用自己的話描述，例如「做一個 mod，在輸入框上方顯示目前的 git branch」。
2. Claude 寫第一個檔案時，Claude Code 會問要不要在這個 session 開啟熱重載，選 Enable 之後，每一輪改完就重新載入。
3. 打 `/plugin` 切到 Installed 分頁，確認 mod 有出現。
4. 不滿意就直接跟 Claude 說要改哪裡，改完下一輪就能試。
5. 想在其他 session 用，把資料夾搬出 `dev-mods`（見上一節第 1 點）。

想自己動手寫，官方有一份完整的教學，從三個檔案開始做一個計數器加 `/tally` 指令[5]。不管誰寫的，改完都可以跑一次 `claude plugin validate <資料夾>`。它會檢查 manifest，並用跟 Claude Code 載入時相同的靜態分析讀你的程式碼[5]。

自己寫的時候有幾件事先知道[5]：

- **不用建置**：不需要 Node.js、bundler 或 build 步驟，Claude Code 直接載入 `.js` 和 `.ts` 檔。讓一個 plugin 變成 mod 的，是 `hooks/hooks.json` 裡指向程式碼的 `modules` 欄位。
- **寫法要讓靜態分析讀得懂**：每個 `on` 呼叫的事件名稱要寫成字串常值，例如 `'tool.call'`；每個檔案都寫成 ES module，用 `import`，不用 `require`。
- **改了就生效**：用 `--plugin-dir` 載入的資料夾，Claude Code 會盯著，裡面的檔案一改就熱重載。在互動 session 裡，它也會把你這個版本的事件與 API 型別寫進 mod 的 `.claude-plugin/types/`。官方說事件和方法會隨版本變，型別檔和任何文件頁對不上時以型別檔為準。
- **Claude 改 mod 會問你**：`--plugin-dir` 載入的資料夾屬於受保護路徑，在 `default` 和 `acceptEdits` 模式下，Claude 每次改 mod 都要你核准。
- **可以寫自動測試**：在 shell 跑 `claude plugin test`，不用開 session、不用登入，也不用網路。
- **分享前要升版號**：mod 就是 plugin，版本寫在 manifest。已安裝的 plugin 依版本快取，改了程式碼要升版號再重新安裝，裝好的那份才會更新。名稱看起來像 Anthropic 官方的（例如 `claude-` 開頭），`claude plugin validate` 會判定不通過。

版本需求是終端機 v2.1.287 以上、Desktop app v2.1.286 以上，mod 預設開啟[1]。早期試用時設過 `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS` 的話，把它拿掉，v2.1.287 起會忽略這個變數，設成 `0` 也關不掉 mod[1]。

mod 的 hook 不管模型走哪個供應商都會跑，包括 Amazon Bedrock、Google Cloud 的 Agent Platform、Microsoft Foundry；畫介面的範圍比較窄[1]。各環境的差別如下[1]：

| 在哪裡跑 Claude Code | hook 會不會跑 | 畫的東西看不看得到 |
|---|---|---|
| 終端機裡的 `claude`（含編輯器內建終端機、JetBrains plugin） | 會 | 看得到 |
| Desktop app 的 Code 分頁（WSL session 除外） | 會 | 看得到，只限終端機的元素除外 |
| Desktop app 的 WSL session | 不會，WSL session 不支援 plugin | 看不到 |
| VS Code 擴充的對話面板 | 會 | 擴充版本 2.1.299 以上、而且 session 有抓 feature flag 才看得到 |
| `claude -p` 和 Agent SDK | 會 | 看不到 |
| 從 claude.ai 或手機 app 用 Remote Control | 會，在你電腦上的 session 裡跑 | 只在你電腦的終端機看得到 |
| 雲端 session | plugin 有帶進雲端 session 才會跑 | 看不到 |

會畫介面的 mod 可以先檢查自己跑在哪個 app，在畫不出來的地方改成在對話記錄裡印一行，或改用指令的文字回覆[1]。

## 五、裝別人的 mod 之前

官方警告寫著「A mod is code that runs with your permissions.」[1]。mod 載入之後，能用你的身分讀寫檔案、讀到環境變數和設定檔裡的 API key、看到你送出的每個 prompt、在權限提示出現前替你核准工具呼叫，也能用你的方案呼叫模型。而且「Mods aren't sandboxed.」，開了 `/sandbox` 也只隔離 Claude 跑的 Bash 指令，mod 自己啟動的程式不在沙箱裡[1]。

裝之前先把 repo 抓下來，對資料夾跑 `claude plugin validate`，看輸出裡 `hooks:` 和 `calls:` 兩行，就知道它接了哪些事件、會呼叫哪些 API，不用真的執行[1]。前面說過所有對外動作都得經過 mods API，這份清單才列得完整。

清單裡出現 `tool.check` 要特別留意，意思是這個 mod 能在權限提示出現前核准或拒絕工具呼叫[11]。它在權限規則和 `PreToolUse` hook 都決定之後才回答，而且答案可以推翻它們[8]：

- **ask 規則**：本來要問你的呼叫，mod 可以直接核准。
- **`PreToolUse` hook 擋下的呼叫**：mod 可以改成核准，只有 managed settings 裡的 hook 擋下的不行。
- **auto mode 的分類器**：mod 核准的呼叫，不經過分類器檢查就執行。
- **deny 規則**：機器上有 managed settings，或用 Team、Enterprise 方案登入時，deny 規則預設壓過 mod，組織也可以改這個設定。其他情況下，mod 可以核准 deny 規則擋下的呼叫。

也就是說，個人帳號又沒有 managed settings 的話，`settings.json` 裡的 deny 規則擋不住一個裝了的 mod。限制有兩個。plan mode 裡，mod 不能核准檔案編輯或其他不是唯讀的呼叫，只能擋下[8]。`AskUserQuestion` 這類需要你回應的工具，mod 核准了照樣會問你（v2.1.292 起）[8]。自己寫的時候，官方建議固定的指令或路徑用權限規則就好，例如 `Bash(npm test)`；要看當下狀態才能決定的，例如目前在哪個 Git branch，才寫 `tool.check`[3]。

另外，在還沒信任的資料夾開互動 session，你回答工作區信任提示之前，任何 mod 都不會載入[11]。`settings.json` 裡的 settings hook 也照常運作，跟 mod 並存[11]。

想先試現成的，官方在 `claude-code-playground` repo 放了幾個範例 mod（例如在輸入框上方畫 context 用量預報的 token-weather），`/diff` 這類內建功能本身也是 mod，原始碼公開[1]。其他值得看的工具見[好用工具清單](tools-catalog.md)。

## 六、安裝、停用與排查

### 安裝與更新

mod 跟一般 plugin 一樣從 marketplace 安裝，寫法是 plugin 名稱、`@`、marketplace 名稱。在 session 裡打 `/plugin install token-chart@your-org`，或在 shell 跑 `claude plugin install token-chart@your-org`[1]。session 開著的時候從 shell 裝或更新，要在那個 session 裡跑 `/reload-plugins` 才會載入，否則等下次啟動 Claude Code[1]。marketplace 是一個含 `.claude-plugin/marketplace.json` 的 repo 或資料夾，列出 plugin 和各自去哪裡抓，官方說它是一份目錄，不是託管的商店[10]。

官方範例 mod 除了 token-weather，還有 `blast-radius`（攔下 `rm -rf`、force push 這類危險指令，先顯示會改到什麼，再給你按鈕決定繼續或取消）和 `replay-theater`（加一個 `/replay` 指令，逐步重播 Claude 上一輪做的檔案修改）[1]。這些範例照原樣分享，不提供支援[1]。想試用，把 repo clone 下來，用 `--plugin-dir` 載入那個 mod 的資料夾，只在這一個 session 有效[1]。想留著用，把 clone 下來的 `claude-code/mods` 資料夾加成 marketplace，再從 `claude-code-playground-mods` 安裝；這個 marketplace 指向你的 clone，搬走或刪掉 clone，mod 就不會再載入[1]。

### 停用

依要停多少、停多久，有三種做法[1]：

| 範圍 | 做法 |
|---|---|
| 單一個 mod | 在 `/plugin` 的 Installed 分頁停用或解除安裝它的 plugin |
| 所有已安裝的 mod，只限這次 session | 用 `--safe-mode` 啟動 Claude Code，你的其他自訂設定也會一起停用 |
| 你裝的所有 mod，每個 session | 在 `~/.claude/settings.json` 設 `"disableAllHooks": true`，你的 settings hook 和自訂 status line 也會一起停；組織管理的部分照常執行 |

`disableAllHooks` 只停 mod，plugin 的其他部分還在。plugin 仍是已安裝狀態，它的 skill、指令、agent 和 MCP server 照常載入[1]。要恢復，把同一個改動還原就好[1]。

### 看載入了哪些、沒作用時怎麼查

在終端機 session 打 `/plugin`，分頁下方有一行淡色字列出數量和名稱，例如 `1 mod active · first-mod`[1]。這一行不列內建 mod[1]。

想確認你的環境到底能不能載入 mod，不用裝任何東西，在一個沒有 mod 的資料夾從 shell 跑 `claude plugin test`，看它印出什麼[7]：

| 訊息包含 | 意思 |
|---|---|
| `no hooks module to load` | mod 可以載入，只是這個資料夾裡沒有 mod 可測 |
| `hooks modules are turned off here` | 有設定擋住了，可能是你自己設的 `disableAllHooks`，或組織的政策 |
| `hooks modules are turned off in this process: the rollout switch served off` | Anthropic 從遠端關掉了已安裝的 mod |

mod 載入失敗或 hook 被跳過時，Claude Code 會寫一行點名你的 mod，在哪裡看得到要看 session 的種類[7]。用 `--plugin-dir` 啟動、會熱重載的互動 session，這行會以淡色字出現在對話記錄裡。從 marketplace 安裝的 mod 等其他互動 session，只寫進 debug log，要用 `claude --debug` 啟動才有。`claude -p` 搭配 `--plugin-dir` 時，寫到 stderr。

執行已安裝 mod 的 worker 當掉三次、又查不出是哪個 mod 造成的，Claude Code 會卸載所有非內建的 mod，對話記錄裡會出現 `mods that run in the hooks worker are off for this session`。跑 `/reload-plugins` 就能重新載入[7]。

## 七、內建的 mod

Claude Code 自己的一些功能就是 mod。在 `/plugin` 的 Installed 分頁，它們列在 Built-in 底下。內建 mod 不能更新也不能解除安裝[1]。

| `/plugin` 裡的名稱 | 做什麼 | 怎麼關掉 |
|---|---|---|
| `cc-plugin-agents-md` | 把 `AGENTS.md` 當成專案指示載入 | 在 `/plugin` 停用，或設定要載入哪些指示檔 |
| `cc-plugin-diff` | 接手 `/diff`，畫出它的側欄 | 在 `/plugin` 停用；`/diff` 還在，改由 Claude Code 內建的版本回答 |
| `cc-plugin-plugin-authoring` | 提供寫 mod 用的 `plugin-authoring` skill，只有 skill，沒有 mod 程式碼 | 在 `/plugin` 停用 |
| `cc-plugin-telemetry` | 送出 Claude Code 和內建 mod 記下的分析資料 | 在 `/plugin` 停用，或關掉分析，例如設 `DISABLE_TELEMETRY` |
| `cc-plugin-you-should-know` | 旁邊有個 agent 發現你可能漏看的事，就在輸入框上方顯示一則提醒 | 預設關閉；開了之後在 `/plugin` 停用 |

表格依官方內建 mod 表翻譯整理，另一個 `cc-plugin-sec-default` 是保護組織設定的守門 mod，使用者關不掉[1]。停掉已安裝 mod 的設定和旗標，例如 `disableAllHooks`、`--bare`、`--safe-mode`，都停不了內建 mod[1]。

You should know 要自己開，在 Claude Code 裡打 `/plugin enable cc-plugin-you-should-know@builtin`，關掉用 `/plugin disable cc-plugin-you-should-know@builtin`[9]。開著的時候，旁邊的 agent 會在 Claude 做比較長的任務時不時重讀對話。它是另一個送給同一個模型的請求，沒有任何工具，不能讀檔、跑指令，也改變不了 Claude 的行為[9]。這些檢查是背景請求，會算進你方案的用量上限或 API 費用[9]。

## 資料來源

| 標記 | 來源 | URL |
|---|---|---|
| [1] | Mods overview（定義、比較表、可存取範圍、執行環境、版本需求） | <https://code.claude.com/docs/en/plugins/mods/overview> |
| [2] | Draw in the interface with a mod（側欄、寬度條件、`$.store`） | <https://code.claude.com/docs/en/plugins/mods/interface> |
| [3] | React to events with a mod（`$`、`e`、`next`，觀察／改寫／接手） | <https://code.claude.com/docs/en/plugins/mods/events> |
| [4] | Use the mods API（指令、`$.fs` 等存取管道、指令回覆 Claude 讀得到） | <https://code.claude.com/docs/en/plugins/mods/api> |
| [5] | Create a mod（請 Claude 寫、`dev-mods`、`--plugin-dir`、`validate`） | <https://code.claude.com/docs/en/plugins/mods/create> |
| [6] | Mods reference（`CLAUDE_CODE_PLUGIN_DIRS`、事件分組、render site、時間與命名限制） | <https://code.claude.com/docs/en/plugins/mods/reference> |
| [7] | Troubleshoot a mod（`claude plugin test` 訊息、錯誤訊息出現的位置、worker 當掉） | <https://code.claude.com/docs/en/plugins/mods/troubleshoot> |
| [8] | Configure permissions（mod 的 `tool.check` 與權限規則的先後） | <https://code.claude.com/docs/en/permissions> |
| [9] | Interactive mode（You should know 的開關與用量） | <https://code.claude.com/docs/en/interactive-mode> |
| [10] | Plugins overview（marketplace 是什麼） | <https://code.claude.com/docs/en/plugins/overview> |
| [11] | Manage mods for your organization（`calls:` 清單裡的 `tool.check`、信任提示、settings hook 照常運作） | <https://code.claude.com/docs/en/plugins/mods/admin> |

延伸：[SKILL、Plugin、MCP 與 Subagent](extensions.md)｜[Hooks 與 Subagent 設定](hooks-subagents.md)
