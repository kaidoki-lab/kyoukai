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
    // リレー入力UI
    "#k-divine-relay-wrap{margin-top:0.9rem;border-top:1px solid rgba(70,130,170,0.15);padding-top:0.7rem}",
    "#k-divine-relay-label{color:#2a4050;font-size:0.6rem;letter-spacing:0.08em;margin-bottom:0.4rem}",
    "#k-divine-relay-row{display:flex;gap:0.4rem;align-items:center}",
    "#k-divine-relay-input{",
    "  flex:1;background:#000;border:1px solid rgba(70,130,170,0.35);",
    "  color:#8ab4c8;font-family:'Courier New',Courier,monospace;",
    "  font-size:clamp(0.75rem,1.3vw,0.9rem);padding:0.3rem 0.5rem;",
    "  outline:none;pointer-events:all;",
    "}",
    "#k-divine-relay-send{",
    "  background:none;border:1px solid rgba(70,130,170,0.35);",
    "  color:#5888a0;font-family:'Courier New',Courier,monospace;",
    "  font-size:0.75rem;padding:0.3rem 0.6rem;cursor:pointer;pointer-events:all;",
    "}",
    "#k-divine-relay-send:hover{background:rgba(70,130,170,0.1)}",
    "#k-divine-relay-done{color:#4a7a60;font-size:0.75rem;letter-spacing:0.06em;margin-top:0.4rem}",
  ].join("");
  document.head.appendChild(style);

  function buildTerminal(promptText) {
    var wrap = document.createElement("div");
    wrap.id = "k-divine-terminal";

    var hdr = document.createElement("div");
    hdr.id = "k-divine-hdr";
    hdr.textContent = "KYOUKAI://ADMIN";

    var body = document.createElement("div");
    body.id = "k-divine-body";

    var prompt = document.createElement("div");
    prompt.id = "k-divine-prompt";
    prompt.textContent = promptText || "> sys.voice —";

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
    return { wrap: wrap, body: body, text: text, cursor: cursor };
  }

  function typeText(textEl, str, cb) {
    textEl.textContent = "";
    var i = 0;
    var iv = setInterval(function () {
      textEl.textContent += str[i];
      i++;
      if (i >= str.length) { clearInterval(iv); if (cb) cb(); }
    }, 90);
  }

  function autoClose(wrap, delay) {
    setTimeout(function () {
      wrap.classList.remove("k-dv-in");
      wrap.classList.add("k-dv-out");
      setTimeout(function () { wrap.remove(); }, 500);
    }, delay);
  }

  function showVoice(voice) {
    var els = buildTerminal("> sys.voice —");
    sessionCount += 1;
    sessionStorage.setItem(SESSION_KEY, String(sessionCount));

    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        els.wrap.classList.add("k-dv-in");
        setTimeout(function () {
          typeText(els.text, voice, function () {
            autoClose(els.wrap, 3000);
          });
        }, 300);
      });
    });
  }

  function showRelay(received) {
    // 5回目：受け取ったメッセージを表示してから入力欄を出す
    var els = buildTerminal("> sys.relay —");
    sessionCount += 1;
    sessionStorage.setItem(SESSION_KEY, String(sessionCount));

    var intro = received
      ? "誰かが残していった\n\"" + received + "\""
      : "まだここには何も残されていない";

    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        els.wrap.classList.add("k-dv-in");
        els.wrap.style.pointerEvents = "auto";

        setTimeout(function () {
          typeText(els.text, intro, function () {
            // 入力欄を追加
            var relayWrap = document.createElement("div");
            relayWrap.id = "k-divine-relay-wrap";

            var label = document.createElement("div");
            label.id = "k-divine-relay-label";
            label.textContent = "> 何か残していく？";

            var row = document.createElement("div");
            row.id = "k-divine-relay-row";

            var input = document.createElement("input");
            input.id = "k-divine-relay-input";
            input.type = "text";
            input.maxLength = 40;
            input.placeholder = "ひとこと";

            var send = document.createElement("button");
            send.id = "k-divine-relay-send";
            send.type = "button";
            send.textContent = "→";

            var done = document.createElement("div");
            done.id = "k-divine-relay-done";
            done.style.display = "none";
            done.textContent = "受け取った";

            row.appendChild(input);
            row.appendChild(send);
            relayWrap.appendChild(label);
            relayWrap.appendChild(row);
            relayWrap.appendChild(done);
            els.body.appendChild(relayWrap);

            function submit() {
              var msg = input.value.trim();
              if (!msg) return;
              input.disabled = true;
              send.disabled = true;
              fetch("/api/divine-relay", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: msg }),
              }).then(function () {
                row.style.display = "none";
                done.style.display = "block";
                setTimeout(function () { autoClose(els.wrap, 0); }, 2000);
              }).catch(function () {
                autoClose(els.wrap, 0);
              });
            }

            send.addEventListener("click", submit);
            input.addEventListener("keydown", function (e) {
              if (e.key === "Enter") submit();
            });

            // 入力なしで 20 秒後に自動クローズ
            setTimeout(function () {
              if (!input.disabled) autoClose(els.wrap, 0);
            }, 20000);
          });
        }, 300);
      });
    });
  }

  function fetchAndShow() {
    if (sessionCount >= MAX_PER_SESSION) return;
    var isRelay = (sessionCount === MAX_PER_SESSION - 1); // 5回目（0-indexed で 4）

    if (isRelay) {
      fetch("/api/divine-relay")
        .then(function (r) { return r.json(); })
        .then(function (d) { showRelay(d.message || null); })
        .catch(function () { showRelay(null); });
    } else {
      var elapsed = Math.floor((Date.now() - startTime) / 1000);
      var hour = new Date().getHours();
      var url = "/api/divine-voice?visits=" + visits + "&hour=" + hour + "&elapsed=" + elapsed;
      fetch(url)
        .then(function (r) { return r.json(); })
        .then(function (d) { if (d.voice) showVoice(d.voice); })
        .catch(function () {});
    }
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
