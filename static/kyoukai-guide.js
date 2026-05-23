(() => {
  "use strict";

  const STORAGE_KEYS = {
    visitCount: "kyoukai_visit_count",
    seenGuide: "kyoukai_seen_guide",
    visitedRooms: "kyoukai_visited_rooms",
    lastRoom: "kyoukai_last_room"
  };

  const MESSAGES = [
    "また来たんだ",
    "ここ、少しずつ変わるよ",
    "見えるところだけが全部じゃない",
    "迷ったら、光ってるところを押してみて",
    "まだ見てない場所があるかも",
    "戻ってきたんだ",
    "ここから、いくつかの場所に行けるよ"
  ];

  const storage = (() => {
    try {
      const testKey = "__kyoukai_guide_test__";
      window.localStorage.setItem(testKey, "1");
      window.localStorage.removeItem(testKey);
      return window.localStorage;
    } catch (_) {
      return null;
    }
  })();

  let messageTimer = 0;
  let lastMessageIndex = -1;

  function readNumber(key) {
    if (!storage) return 0;
    const value = Number.parseInt(storage.getItem(key) || "0", 10);
    return Number.isFinite(value) ? Math.max(0, value) : 0;
  }

  function writeValue(key, value) {
    if (!storage) return;
    try {
      storage.setItem(key, value);
    } catch (_) {}
  }

  function readJson(key, fallback) {
    if (!storage) return fallback;
    try {
      const value = JSON.parse(storage.getItem(key) || "");
      return Array.isArray(fallback) && !Array.isArray(value) ? fallback : value;
    } catch (_) {
      return fallback;
    }
  }

  function getVisitCount() {
    return readNumber(STORAGE_KEYS.visitCount);
  }

  function incrementVisitCount() {
    const nextCount = getVisitCount() + 1;
    writeValue(STORAGE_KEYS.visitCount, String(nextCount));
    return nextCount;
  }

  function getCurrentRoom() {
    if (window.KYOUKAI_ROOM) return String(window.KYOUKAI_ROOM);
    if (document.body?.dataset?.monetizePage) return String(document.body.dataset.monetizePage);
    const path = window.location.pathname.replace(/^\/+|\/+$/g, "");
    return path || "home";
  }

  function rememberRoom(room) {
    writeValue(STORAGE_KEYS.lastRoom, room);
    const rooms = readJson(STORAGE_KEYS.visitedRooms, []);
    if (!rooms.includes(room)) {
      rooms.push(room);
      writeValue(STORAGE_KEYS.visitedRooms, JSON.stringify(rooms));
    } else if (storage && storage.getItem(STORAGE_KEYS.visitedRooms) === null) {
      writeValue(STORAGE_KEYS.visitedRooms, JSON.stringify(rooms));
    }
  }

  function shouldShowGuide(visitCount) {
    return visitCount >= 2;
  }

  function pickMessage() {
    if (MESSAGES.length === 1) return MESSAGES[0];
    let index = Math.floor(Math.random() * MESSAGES.length);
    if (index === lastMessageIndex) {
      index = (index + 1) % MESSAGES.length;
    }
    lastMessageIndex = index;
    return MESSAGES[index];
  }

  function createGuide() {
    const guide = document.createElement("aside");
    guide.className = "kyoukai-guide";
    guide.setAttribute("aria-label", "小さな案内人");

    const button = document.createElement("button");
    button.className = "kyoukai-guide__body";
    button.type = "button";
    button.setAttribute("aria-label", "案内人の声を聞く");
    button.innerHTML = `
      <svg viewBox="0 0 64 64" role="img" aria-hidden="true" focusable="false">
        <path class="kyoukai-guide__glow" d="M32 5 C45 5 58 17 58 32 C58 48 46 58 32 58 C17 58 6 47 6 32 C6 17 19 5 32 5 Z" />
        <path class="kyoukai-guide__shell" d="M32 10 C43 10 52 20 52 32 C52 45 43 53 32 53 C20 53 12 45 12 32 C12 20 21 10 32 10 Z" />
        <path class="kyoukai-guide__line" d="M20 24 C24 18 40 18 44 24" />
        <circle class="kyoukai-guide__eye" cx="25" cy="33" r="3.2" />
        <circle class="kyoukai-guide__eye" cx="39" cy="33" r="3.2" />
        <path class="kyoukai-guide__line" d="M26 43 C30 46 35 46 39 43" />
      </svg>
    `;

    const bubble = document.createElement("div");
    bubble.className = "kyoukai-guide__bubble";
    bubble.setAttribute("aria-live", "polite");

    guide.append(button, bubble);
    button.addEventListener("click", () => showGuideMessage(guide, bubble));
    return guide;
  }

  function showGuide(guide) {
    document.body.appendChild(guide);
    window.requestAnimationFrame(() => {
      guide.classList.add("kyoukai-guide--visible");
    });
    writeValue(STORAGE_KEYS.seenGuide, "true");
  }

  function hideGuideMessage(guide) {
    guide.classList.remove("kyoukai-guide--speaking");
  }

  function showGuideMessage(guide, bubble) {
    window.clearTimeout(messageTimer);
    bubble.textContent = pickMessage();
    guide.classList.add("kyoukai-guide--speaking");
    messageTimer = window.setTimeout(() => hideGuideMessage(guide), 3800);
  }

  function initGuide() {
    const room = getCurrentRoom();
    const visitCount = incrementVisitCount();
    rememberRoom(room);

    if (!shouldShowGuide(visitCount)) return;
    showGuide(createGuide());
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initGuide, { once: true });
  } else {
    initGuide();
  }
})();
