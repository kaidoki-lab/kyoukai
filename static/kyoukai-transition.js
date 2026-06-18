(function () {
  "use strict";

  var style = document.createElement("style");
  style.textContent = [
    // フェードイン（ページロード時）— 黒背景から明けるように見せる
    "html.k-tr{opacity:0;background:#000}",
    "html.k-tr-in{opacity:1;transition:opacity 0.36s ease}",
    // CRTシャットダウン
    // 1. 明るいオーバーレイが画面全体をフラッシュ
    // 2. 縦に潰れて細い光の線になる
    // 3. 線が黒に変わり、全画面に広がって暗転
    "#k-crt-overlay{",
    "  position:fixed;inset:0;z-index:2147483647;pointer-events:none;",
    "  background:#b8cfe0;",
    "  transform-origin:50% 50%;",
    "  will-change:transform,opacity;",
    "  animation:k-crt-off 0.82s ease-in forwards;",
    "}",
    "@keyframes k-crt-off{",
    "  0%  {opacity:0;   transform:scaleY(1);    background:#b8cfe0}",
    "  7%  {opacity:0.94;transform:scaleY(1);    background:#b8cfe0}",
    "  50% {opacity:0.94;transform:scaleY(0.05); background:#b8cfe0}",
    "  64% {opacity:1;   transform:scaleY(0.01); background:#b8cfe0}",
    "  71% {opacity:1;   transform:scaleY(0.01); background:#000}",
    "  80% {opacity:1;   transform:scaleY(1);    background:#000}",
    "  100%{opacity:1;   transform:scaleY(1);    background:#000}",
    "}",
  ].join("");
  document.head.appendChild(style);

  document.documentElement.classList.add("k-tr");

  function fadeIn() {
    requestAnimationFrame(function () {
      document.documentElement.classList.add("k-tr-in");
    });
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", fadeIn, { once: true });
  } else {
    fadeIn();
  }

  window.addEventListener("pageshow", function (e) {
    if (e.persisted) {
      var old = document.getElementById("k-crt-overlay");
      if (old) old.remove();
      document.documentElement.classList.add("k-tr-in");
    }
  });

  function crtNavigate(url) {
    if (document.getElementById("k-crt-overlay")) return;
    var overlay = document.createElement("div");
    overlay.id = "k-crt-overlay";
    document.body.appendChild(overlay);
    // 画面が暗転してから遷移（0.82s の 80% = 0.656s）
    setTimeout(function () { window.location.href = url; }, 700);
  }

  document.addEventListener("click", function (e) {
    var a = e.target.closest("a[href]");
    if (!a) return;
    var href = a.getAttribute("href");
    if (!href) return;
    if (href.charAt(0) === "#") return;
    if (/^(https?:|mailto:|tel:|javascript:)/.test(href)) return;
    if (a.target && a.target !== "_self") return;
    if (href.charAt(0) !== "/") return;

    e.preventDefault();
    crtNavigate(href);
  });
})();
