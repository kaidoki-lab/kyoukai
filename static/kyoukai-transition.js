(function () {
  "use strict";

  var style = document.createElement("style");
  style.textContent = [
    // フェードイン（ページロード時）
    "html.k-tr{opacity:0}",
    "html.k-tr-in{opacity:1;transition:opacity 0.32s ease}",
    // CRTシャットダウン — 明るいオーバーレイが縦に潰れる
    "#k-crt-overlay{",
    "  position:fixed;inset:0;z-index:2147483647;pointer-events:none;",
    "  background:#b8cfe0;",
    "  transform-origin:50% 50%;",
    "  will-change:transform,opacity;",
    "  animation:k-crt-off 0.62s ease-in forwards;",
    "}",
    "@keyframes k-crt-off{",
    "  0%  {opacity:0;   transform:scaleY(1)   }",
    "  9%  {opacity:0.93;transform:scaleY(1)   }",
    "  46% {opacity:0.93;transform:scaleY(0.055)}",
    "  67% {opacity:1;   transform:scaleY(0.012)}",
    "  100%{opacity:0;   transform:scaleY(0.012)}",
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
    setTimeout(function () { window.location.href = url; }, 560);
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
