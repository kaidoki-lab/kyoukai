(function () {
  const STORAGE_KEY = "kyoukai_drift_flags";
  const ROOM_FLAGS = {
    "/": "visited_home",
    "/signal": "visited_signal",
    "/archive": "visited_archive",
    "/null": "visited_null",
    "/outside": "visited_outside",
  };
  const DRIFT_CLASSES = {
    visited_null: "drift-from-null",
    visited_outside: "drift-from-outside",
    visited_signal: "drift-from-signal",
  };

  function readFlags() {
    try {
      const value = window.localStorage.getItem(STORAGE_KEY);
      return value ? JSON.parse(value) || {} : {};
    } catch (_) {
      return {};
    }
  }

  function writeFlags(flags) {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(flags));
    } catch (_) {}
  }

  function sendFlagEvent(flagName) {
    if (typeof window.gtag !== "function") return;
    window.gtag("event", "kyoukai_drift_flag_set", {
      flag_name: flagName,
      page_path: window.location.pathname,
    });
  }

  function setFlag(flags, flagName) {
    if (!flagName || flags[flagName] === true) return false;
    flags[flagName] = true;
    sendFlagEvent(flagName);
    return true;
  }

  function classifyPath() {
    const path = window.location.pathname.replace(/\/+$/, "") || "/";
    return Object.prototype.hasOwnProperty.call(ROOM_FLAGS, path) ? path : "";
  }

  function addBodyClass(name) {
    document.body?.classList.add(name);
    document.documentElement?.classList.add(name);
  }

  function addArchiveFragment() {
    const target = document.querySelector(".archive-room-status") || document.querySelector(".archive-info");
    if (!target || document.querySelector("[data-drift-fragment]")) return;
    const fragment = document.createElement("span");
    fragment.className = "drift-fragment drift-fragment--archive";
    fragment.dataset.driftFragment = "signal";
    fragment.textContent = "受信記録の欠片が混入しています";
    target.append(fragment);
  }

  function bindTouchFlags(flags, path) {
    if (path === "/null") {
      document.addEventListener("click", (event) => {
        const target = event.target?.closest?.(".collapse-room, .ky-monetize-route--collapse");
        if (!target) return;
        const next = readFlags();
        if (setFlag(next, "touched_null")) writeFlags(next);
      }, { passive: true });
    }

    if (path === "/outside") {
      document.addEventListener("click", (event) => {
        const target = event.target?.closest?.(".outside-room, .outside-core-body a");
        if (!target) return;
        const next = readFlags();
        if (setFlag(next, "touched_outside")) writeFlags(next);
      }, { passive: true });
    }
  }

  function applyDrift(previousFlags, path) {
    if (path === "/" && previousFlags.visited_null) {
      addBodyClass(DRIFT_CLASSES.visited_null);
    }

    if (path === "/archive" && previousFlags.visited_signal) {
      addBodyClass(DRIFT_CLASSES.visited_signal);
      addArchiveFragment();
    }

    if (path === "/signal" && previousFlags.visited_outside) {
      addBodyClass(DRIFT_CLASSES.visited_outside);
    }
  }

  function boot() {
    const path = classifyPath();
    if (!path) return;

    const flags = readFlags();
    const previousFlags = Object.assign({}, flags);
    const now = new Date().toISOString();

    if (!flags.first_seen_at) flags.first_seen_at = now;
    flags.last_seen_at = now;
    setFlag(flags, ROOM_FLAGS[path]);
    writeFlags(flags);

    document.documentElement.dataset.driftFlags = "active";
    if (document.body) document.body.dataset.driftFlags = "active";
    applyDrift(previousFlags, path);
    bindTouchFlags(flags, path);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
