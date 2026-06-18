(function () {
  "use strict";

  // CSS インジェクション（外部CSSファイル不要）
  var style = document.createElement("style");
  style.textContent = [
    "html.k-tr{opacity:0}",
    "html.k-tr-in{opacity:1;transition:opacity 0.32s ease}",
    "html.k-tr-out{opacity:0;transition:opacity 0.26s ease}",
  ].join("");
  document.head.appendChild(style);

  // 最初は不可視で開始
  document.documentElement.classList.add("k-tr");

  // フェードイン（DOMContentLoaded後、または即時）
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

  // bfcache から戻ったときもフェードイン
  window.addEventListener("pageshow", function (e) {
    if (e.persisted) {
      document.documentElement.classList.remove("k-tr-out");
      document.documentElement.classList.add("k-tr-in");
    }
  });

  // 内部リンクのクリックでフェードアウト → 遷移
  document.addEventListener("click", function (e) {
    var a = e.target.closest("a[href]");
    if (!a) return;
    var href = a.getAttribute("href");
    if (!href) return;
    // 外部リンク・アンカー・特殊スキームは除外
    if (href.charAt(0) === "#") return;
    if (/^(https?:|mailto:|tel:|javascript:)/.test(href)) return;
    if (a.target && a.target !== "_self") return;
    // 内部パスのみ処理
    if (href.charAt(0) !== "/") return;

    e.preventDefault();
    document.documentElement.classList.remove("k-tr-in");
    document.documentElement.classList.add("k-tr-out");
    setTimeout(function () {
      window.location.href = href;
    }, 280);
  });
})();
