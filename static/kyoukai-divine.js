(function () {
  "use strict";

  var SESSION_KEY = "kyoukai_divine_count";
  var VISIT_KEY   = "kyoukai_visit_count";
  var MAX_PER_SESSION = 2;

  // 訪問回数をカウントアップ（セッション跨ぎ）
  var visits = parseInt(localStorage.getItem(VISIT_KEY) || "0", 10);
  if (!sessionStorage.getItem("kyoukai_visit_counted")) {
    visits += 1;
    localStorage.setItem(VISIT_KEY, String(visits));
    sessionStorage.setItem("kyoukai_visit_counted", "1");
  }

  var sessionCount = parseInt(sessionStorage.getItem(SESSION_KEY) || "0", 10);
  if (sessionCount >= MAX_PER_SESSION) return;

  var startTime = Date.now();

  // スタイルを注入
  var style = document.createElement("style");
  style.textContent = [
    "#k-divine-overlay{",
    "  position:fixed;inset:0;z-index:99999;",
    "  background:rgba(0,0,0,0.82);",
    "  display:flex;align-items:center;justify-content:center;",
    "  pointer-events:none;",
    "  opacity:0;transition:opacity 0.6s ease;",
    "}",
    "#k-divine-overlay.k-divine-in{opacity:1}",
    "#k-divine-overlay.k-divine-out{opacity:0}",
    "#k-divine-text{",
    "  color:#d8e8f0;",
    "  font-size:clamp(1.8rem,5vw,3.2rem);",
    "  font-family:'Courier New',Courier,monospace;",
    "  letter-spacing:0.12em;",
    "  text-align:center;",
    "  text-shadow:0 0 24px rgba(160,210,240,0.6);",
    "  max-width:80vw;",
    "  line-height:1.5;",
    "}",
  ].join("");
  document.head.appendChild(style);

  function buildOverlay() {
    var overlay = document.createElement("div");
    overlay.id = "k-divine-overlay";
    var text = document.createElement("div");
    text.id = "k-divine-text";
    overlay.appendChild(text);
    document.body.appendChild(overlay);
    return { overlay: overlay, text: text };
  }

  function typeText(el, str, cb) {
    el.textContent = "";
    var i = 0;
    var iv = setInterval(function () {
      el.textContent += str[i];
      i++;
      if (i >= str.length) {
        clearInterval(iv);
        if (cb) cb();
      }
    }, 80);
  }

  function showVoice(voice) {
    var els = buildOverlay();

    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        els.overlay.classList.add("k-divine-in");
        typeText(els.text, voice, function () {
          // タイプ完了後 2.4 秒でフェードアウト
          setTimeout(function () {
            els.overlay.classList.remove("k-divine-in");
            els.overlay.classList.add("k-divine-out");
            setTimeout(function () {
              els.overlay.remove();
            }, 700);
          }, 2400);
        });
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
    // 初回: リピーターほど早く（最短30秒、最長90秒）
    var base = visits >= 3 ? 30 : visits >= 2 ? 45 : 70;
    var jitter = Math.floor(Math.random() * 25);
    var delay = (base + jitter) * 1000;

    setTimeout(function () {
      fetchAndShow();
      // 2回目があるなら 90〜150 秒後
      if (count + 1 < MAX_PER_SESSION) {
        scheduleNext(count + 1);
      }
    }, delay);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { scheduleNext(0); }, { once: true });
  } else {
    scheduleNext(0);
  }
})();
