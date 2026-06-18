(function () {
  "use strict";

  var SESSION_KEY = "kyoukai_divine_count";
  var VISIT_KEY   = "kyoukai_visit_count";
  var MAX_PER_SESSION = 5;

  var visits = parseInt(localStorage.getItem(VISIT_KEY) || "0", 10);
  if (!sessionStorage.getItem("kyoukai_visit_counted")) {
    visits += 1;
    localStorage.setItem(VISIT_KEY, String(visits));
    sessionStorage.setItem("kyoukai_visit_counted", "1");
  }

  var sessionCount = parseInt(sessionStorage.getItem(SESSION_KEY) || "0", 10);
  if (sessionCount >= MAX_PER_SESSION) return;

  var startTime = Date.now();

  var style = document.createElement("style");
  style.textContent = [
    "#k-divine-terminal{",
    "  position:fixed;top:1.5rem;right:1.5rem;",
    "  width:min(42vw,480px);min-width:280px;",
    "  z-index:99999;pointer-events:none;",
    "  background:#02030a;",
    "  border:1px solid rgba(70,130,170,0.3);",
    "  box-shadow:0 0 28px rgba(30,80,140,0.18);",
    "  font-family:'Courier New',Courier,monospace;",
    "  opacity:0;transform:translateY(-10px);",
    "  transition:opacity 0.45s ease,transform 0.45s ease;",
    "}",
    "#k-divine-terminal.k-dv-in{opacity:1;transform:translateY(0)}",
    "#k-divine-terminal.k-dv-out{opacity:0;transform:translateY(-10px)}",
    "#k-divine-hdr{",
    "  padding:0.35rem 0.7rem;",
    "  border-bottom:1px solid rgba(70,130,170,0.18);",
    "  color:#2a4050;font-size:0.6rem;letter-spacing:0.12em;",
    "  display:flex;align-items:center;gap:0.4rem;",
    "}",
    "#k-divine-hdr::before{content:'●';color:rgba(70,130,170,0.45);font-size:0.45rem}",
    "#k-divine-body{padding:0.7rem 0.9rem 0.85rem}",
    "#k-divine-prompt{",
    "  color:#243540;font-size:0.6rem;letter-spacing:0.08em;margin-bottom:0.35rem;",
    "}",
    "#k-divine-text{",
    "  color:#8ab4c8;",
    "  font-size:clamp(1rem,1.8vw,1.3rem);",
    "  letter-spacing:0.1em;line-height:1.7;",
    "  white-space:pre-wrap;word-break:break-all;",
    "}",
    "#k-divine-cursor{",
    "  display:inline-block;width:0.5em;height:0.9em;",
    "  background:#5888a0;vertical-align:text-bottom;",
    "  margin-left:2px;",
    "  animation:k-dv-blink 1s step-end infinite;",
    "}",
    "@keyframes k-dv-blink{50%{opacity:0}}",
  ].join("");
  document.head.appendChild(style);

  function buildTerminal() {
    var wrap = document.createElement("div");
    wrap.id = "k-divine-terminal";

    var hdr = document.createElement("div");
    hdr.id = "k-divine-hdr";
    hdr.textContent = "KYOUKAI://ADMIN";

    var body = document.createElement("div");
    body.id = "k-divine-body";

    var prompt = document.createElement("div");
    prompt.id = "k-divine-prompt";
    prompt.textContent = "> sys.voice —";

    var text = document.createElement("span");
    text.id = "k-divine-text";

    var cursor = document.createElement("span");
    cursor.id = "k-divine-cursor";

    body.appendChild(prompt);
    body.appendChild(text);
    body.appendChild(cursor);
    wrap.appendChild(hdr);
    wrap.appendChild(body);
    document.body.appendChild(wrap);
    return { wrap: wrap, text: text, cursor: cursor };
  }

  function typeText(textEl, cursorEl, str, cb) {
    textEl.textContent = "";
    var i = 0;
    var iv = setInterval(function () {
      textEl.textContent += str[i];
      i++;
      if (i >= str.length) {
        clearInterval(iv);
        if (cb) cb();
      }
    }, 90);
  }

  function showVoice(voice) {
    var els = buildTerminal();

    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        els.wrap.classList.add("k-dv-in");
        setTimeout(function () {
          typeText(els.text, els.cursor, voice, function () {
            // タイプ完了後 3 秒でフェードアウト
            setTimeout(function () {
              els.wrap.classList.remove("k-dv-in");
              els.wrap.classList.add("k-dv-out");
              setTimeout(function () { els.wrap.remove(); }, 500);
            }, 3000);
          });
        }, 300);
      });
    });

    sessionCount += 1;
    sessionStorage.setItem(SESSION_KEY, String(sessionCount));
  }

  function fetchAndShow() {
    if (sessionCount >= MAX_PER_SESSION) return;
    var elapsed = Math.floor((Date.now() - startTime) / 1000);
    var hour = new Date().getHours();
    var url = "/api/divine-voice?visits=" + visits + "&hour=" + hour + "&elapsed=" + elapsed;
    fetch(url)
      .then(function (r) { return r.json(); })
      .then(function (d) { if (d.voice) showVoice(d.voice); })
      .catch(function () {});
  }

  function scheduleNext(count) {
    if (count >= MAX_PER_SESSION) return;
    var base = visits >= 3 ? 20 : visits >= 2 ? 25 : 30;
    var jitter = Math.floor(Math.random() * 25);
    var delay = (base + jitter) * 1000;

    setTimeout(function () {
      fetchAndShow();
      if (count + 1 < MAX_PER_SESSION) {
        setTimeout(function () { scheduleNext(count + 1); }, (60 + Math.floor(Math.random() * 30)) * 1000);
      }
    }, delay);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { scheduleNext(0); }, { once: true });
  } else {
    scheduleNext(0);
  }
})();
