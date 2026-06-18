(function () {
  "use strict";

  var style = document.createElement("style");
  style.textContent = [
    // フェードイン（ページロード時）
    "html.k-tr{opacity:0}",
    "html.k-tr-in{opacity:1;transition:opacity 0.32s ease}",
    // CRTシャットダウン（退場時）— body を縦方向に圧縮
    "html.k-tr-out body{",
    "  animation:k-crt-off 0.44s ease-in forwards;",
    "  transform-origin:50% 50%;",
    "  will-change:transform,filter,opacity;",
    "}",
    "@keyframes k-crt-off{",
    "  0%  {transform:scaleY(1);   filter:brightness(1);              opacity:1}",
    "  18% {transform:scaleY(1);   filter:brightness(3.2);            opacity:1}",
    "  46% {transform:scaleY(0.06);filter:brightness(4) saturate(0.1);opacity:1}",
    "  66% {transform:scaleY(0.02);filter:brightness(5.5);            opacity:1}",
    "  100%{transform:scaleY(0.02);filter:brightness(0);              opacity:0}",
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
      document.documentElement.classList.remove("k-tr-out");
      document.documentElement.classList.add("k-tr-in");
    }
  });

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
    document.documentElement.classList.remove("k-tr-in");
    document.documentElement.classList.add("k-tr-out");
    setTimeout(function () {
      window.location.href = href;
    }, 430);
  });
})();
