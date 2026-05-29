(function () {
  "use strict";

  var key = "kyoukai_null_state";
  var styleId = "kyoukai-null-infection-style";

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function readState() {
    var params = new URLSearchParams(window.location.search);
    if (params.get("reset_null") === "1") {
      window.localStorage.removeItem(key);
      window.history.replaceState(null, "", window.location.pathname);
    }

    try {
      return JSON.parse(window.localStorage.getItem(key) || "{}");
    } catch {
      return {};
    }
  }

  function levelName(value, collapsed) {
    if (collapsed || value >= 100) return "collapsed";
    if (value >= 75) return "heavy";
    if (value >= 50) return "medium";
    if (value >= 25) return "light";
    return "none";
  }

  function applyState() {
    var state = readState();
    var value = clamp(Number(state.globalInfection || state.collapseLevel || 0), 0, 100);
    var collapsed = Boolean(state.collapsed || state.maxReached || value >= 100);
    var level = levelName(value, collapsed);
    var root = document.documentElement;

    root.dataset.nullInfection = level;
    root.classList.toggle("ky-null-infected", level !== "none");
    root.classList.toggle("ky-null-infected-light", level === "light");
    root.classList.toggle("ky-null-infected-medium", level === "medium");
    root.classList.toggle("ky-null-infected-heavy", level === "heavy");
    root.classList.toggle("ky-null-collapsed", collapsed);
  }

  function installStyle() {
    if (document.getElementById(styleId)) return;
    var style = document.createElement("style");
    style.id = styleId;
    style.textContent = [
      ".ky-null-infected body::before{content:'';position:fixed;inset:0;z-index:9990;pointer-events:none;background:repeating-linear-gradient(90deg,rgba(255,0,153,.12) 0 2px,transparent 2px 24px),repeating-linear-gradient(0deg,rgba(0,247,255,.1) 0 1px,transparent 1px 17px);mix-blend-mode:screen;opacity:.18}",
      ".ky-null-infected-medium body::before{opacity:.28}",
      ".ky-null-infected-heavy body::before,.ky-null-collapsed body::before{opacity:.42;animation:kyNullJitter .38s steps(2,end) infinite}",
      ".ky-null-infected-medium body::after,.ky-null-infected-heavy body::after,.ky-null-collapsed body::after{content:'NO REFUND / 表示が保てません';position:fixed;z-index:9991;right:14px;top:14px;max-width:min(330px,calc(100vw - 28px));padding:9px 12px;border:3px solid #24002f;background:#fff600;color:#ff006a;font:900 12px/1.3 monospace;text-shadow:1px 1px 0 #fff;box-shadow:5px 5px 0 #00f7ff;transform:rotate(2deg);pointer-events:none}",
      ".ky-null-infected-heavy body{filter:saturate(1.35) contrast(1.08)}",
      ".ky-null-collapsed body{filter:saturate(1.8) contrast(1.28) hue-rotate(24deg)}",
      "@keyframes kyNullJitter{0%{transform:translate(0,0)}50%{transform:translate(3px,-2px)}100%{transform:translate(-2px,2px)}}"
    ].join("");
    document.head.appendChild(style);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      installStyle();
      applyState();
    });
  } else {
    installStyle();
    applyState();
  }

  window.addEventListener("storage", function (event) {
    if (event.key === key) applyState();
  });
  window.addEventListener("kyoukai:null-state", applyState);
})();
