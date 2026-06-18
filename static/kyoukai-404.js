(function () {
  "use strict";

  var KEY = "kyoukai_404_count";
  var NOISE = "░▒▓█▌▐▀▄╬╪╫▪▬►◄↕§▲▼╳╱";

  var count = 0;
  try { count = parseInt(localStorage.getItem(KEY) || "0", 10); if (isNaN(count)) count = 0; } catch (e) {}
  try { localStorage.setItem(KEY, String(count + 1)); } catch (e) {}

  var stage = Math.min(count, 5);
  var body  = document.querySelector(".k404-body");
  var block = document.getElementById("k404-block");
  var codeEl = document.getElementById("k404-code");
  var msgEl  = document.getElementById("k404-msg");

  if (stage >= 5) {
    body.classList.add("k404-gone");
    return;
  }

  body.classList.add("k404-s" + stage);

  // テキスト文字崩壊（stage 2+）
  function corrupt(text, ratio) {
    return text.split("").map(function (ch) {
      if (ch === " ") return ch;
      return Math.random() < ratio
        ? NOISE[Math.floor(Math.random() * NOISE.length)]
        : ch;
    }).join("");
  }

  if (stage >= 2 && codeEl) {
    var codeRatio = stage === 2 ? 0.22 : stage === 3 ? 0.55 : 0.82;
    codeEl.textContent = corrupt("404", codeRatio);
  }
  if (stage >= 2 && msgEl) {
    var msgOrig  = msgEl.dataset.original || msgEl.textContent;
    var msgRatio = stage === 2 ? 0.16 : stage === 3 ? 0.45 : 0.72;
    msgEl.textContent = corrupt(msgOrig, msgRatio);
  }

  // ランダム配置（毎ページ読み込みで移動）
  if (block) {
    var pad = 20;
    var maxX = Math.max(pad, window.innerWidth  - 380 - pad);
    var maxY = Math.max(pad, window.innerHeight - 200 - pad);
    block.style.left = Math.floor(Math.random() * maxX) + "px";
    block.style.top  = Math.floor(Math.random() * maxY) + "px";
  }

  // Stage 1: 一定間隔でチラつき
  if (stage === 1 && codeEl) {
    setInterval(function () {
      var orig  = "404";
      var chars = orig.split("");
      var idx   = Math.floor(Math.random() * chars.length);
      chars[idx] = NOISE[Math.floor(Math.random() * NOISE.length)];
      codeEl.textContent = chars.join("");
      setTimeout(function () { codeEl.textContent = orig; }, 110);
    }, 2400);
  }
})();
