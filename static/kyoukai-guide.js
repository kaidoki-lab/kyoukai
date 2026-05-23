(() => {
  "use strict";

  const STORAGE_KEYS = {
    visitCount: "kyoukai_visit_count",
    seenGuide: "kyoukai_seen_guide",
    visitedRooms: "kyoukai_visited_rooms",
    lastRoom: "kyoukai_last_room",
    previousRoom: "kyoukai_previous_room",
    returnedToTopCount: "kyoukai_returned_to_top_count",
    outsideHintSeen: "kyoukai_outside_hint_seen",
    supportHintSeen: "kyoukai_support_hint_seen",
    messageIndex: "kyoukai_guide_message_index",
    debug: "kyoukai_guide_debug"
  };

  const GUIDE_STORAGE_KEYS = Object.values(STORAGE_KEYS);

  const KYOUKAI_ROOMS = [
    { id: "observation", path: "/observation", label: "観測室", hint: "見てるだけじゃない場所もある" },
    { id: "archive", path: "/archive", label: "残留域", hint: "残ってるものを見てもいいよ" },
    { id: "signal", path: "/signal", label: "音声室", hint: "音がする場所がある" },
    { id: "hyougi", path: "/hyougi", label: "評議", hint: "声が集まる場所がある" },
    { id: "exit", path: "/exit", label: "脱出室", hint: "外に出る道があるよ" },
    { id: "null", path: "/null", label: "崩落域", hint: "崩れてる場所も残ってる" },
    { id: "outside", path: "/outside", label: "外部接続", hint: "外につながる場所もあるよ" },
    { id: "support", path: "/support", label: "小さな箱", hint: "小さな箱が置いてある" }
  ];

  const GUIDE_TARGET_ROOM_IDS = KYOUKAI_ROOMS.map((room) => room.id);

  const BASE_MESSAGES = [
    "また来たんだ",
    "ここ、少しずつ変わるよ",
    "見えるところだけが全部じゃない",
    "まだ見てない場所があるかも"
  ];

  const RETURN_MESSAGES = [
    "戻ってきたんだ",
    "そこ、見てきたんだ",
    "次は別の場所も見えるかも",
    "ここに戻ると、少しだけ変わるよ"
  ];

  const VISITED_MESSAGES = [
    "そこ、見たんだ",
    "だいぶ歩いたね",
    "気配が少し増えた"
  ];

  const UNVISITED_MESSAGES = [
    "まだ見てない場所がある",
    "光ってるところ、残ってるよ",
    "別の入口も、たぶんある"
  ];

  const OUTSIDE_HINT_MESSAGES = [
    "外につながる場所もあるよ",
    "外の棚を見てもいいよ",
    "ここから外のものが少し入ってくる"
  ];

  const SUPPORT_HINT_MESSAGES = [
    "小さな箱が置いてある",
    "見るだけでもいい箱がある",
    "見た人の気配が、少し残る"
  ];

  const COMPLETE_MESSAGES = [
    "ひととおり見たみたい",
    "だいたい覚えたよ",
    "まだ変わるかもしれない"
  ];

  const MESSAGE_HIDE_MS = 3800;
  const AUTO_MESSAGE_DELAY_MS = 850;
  const MAX_MESSAGE_LENGTH = 34;

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

  function getSearchParams() {
    try {
      return new URLSearchParams(window.location.search || "");
    } catch (_) {
      return new URLSearchParams("");
    }
  }

  function safeGet(key) {
    if (!storage) return null;
    try {
      return storage.getItem(key);
    } catch (_) {
      return null;
    }
  }

  function safeSet(key, value) {
    if (!storage) return;
    try {
      storage.setItem(key, String(value));
    } catch (_) {}
  }

  function safeRemove(key) {
    if (!storage) return;
    try {
      storage.removeItem(key);
    } catch (_) {}
  }

  function getNumber(key) {
    const value = Number.parseInt(safeGet(key) || "0", 10);
    if (!Number.isFinite(value) || value < 0) {
      safeSet(key, "0");
      return 0;
    }
    return value;
  }

  function setNumber(key, value) {
    const nextValue = Number.isFinite(value) && value > 0 ? Math.floor(value) : 0;
    safeSet(key, String(nextValue));
  }

  function getBoolean(key) {
    return safeGet(key) === "true";
  }

  function setBoolean(key, value) {
    safeSet(key, value ? "true" : "false");
  }

  function getJsonArray(key) {
    const rawValue = safeGet(key);
    if (!rawValue) return [];
    try {
      const parsed = JSON.parse(rawValue);
      if (Array.isArray(parsed)) return parsed.filter((item) => typeof item === "string");
    } catch (_) {}
    safeSet(key, "[]");
    return [];
  }

  function setJsonArray(key, value) {
    const uniqueValues = Array.from(new Set(Array.isArray(value) ? value.filter((item) => typeof item === "string") : []));
    safeSet(key, JSON.stringify(uniqueValues));
  }

  function resetGuideStorage() {
    GUIDE_STORAGE_KEYS.forEach(safeRemove);
  }

  function isGuideDebug(params = getSearchParams()) {
    if (params.get("guideDebug") === "1") return true;
    return getBoolean(STORAGE_KEYS.debug);
  }

  function getRoomFromPath(pathname) {
    const cleanPath = (pathname || "/").replace(/\/+$/g, "") || "/";
    if (cleanPath === "/" || cleanPath === "/index.html" || cleanPath === "/home.html") return "top";
    if (cleanPath === "/observation") return "observation";
    const match = KYOUKAI_ROOMS.find((room) => cleanPath === room.path || cleanPath.endsWith(`${room.id}.html`));
    return match ? match.id : "unknown-page";
  }

  function getCurrentRoomId() {
    if (window.KYOUKAI_ROOM === "home") return "top";
    if (typeof window.KYOUKAI_ROOM === "string" && window.KYOUKAI_ROOM.trim()) {
      const roomId = window.KYOUKAI_ROOM.trim();
      return roomId === "observation" || GUIDE_TARGET_ROOM_IDS.includes(roomId) ? roomId : "unknown-page";
    }
    const roomFromPath = getRoomFromPath(window.location.pathname);
    if (roomFromPath !== "unknown-page") return roomFromPath;
    if (document.body?.dataset?.monetizePage === "outside") return "outside";
    return roomFromPath;
  }

  function getVisitedRooms() {
    return getJsonArray(STORAGE_KEYS.visitedRooms);
  }

  function getUnvisitedRooms(visitedRooms = getVisitedRooms()) {
    return KYOUKAI_ROOMS.filter((room) => !visitedRooms.includes(room.id));
  }

  function incrementVisitCount() {
    const nextCount = getNumber(STORAGE_KEYS.visitCount) + 1;
    setNumber(STORAGE_KEYS.visitCount, nextCount);
    return nextCount;
  }

  function updateRoomVisit(currentRoomId) {
    const previousLastRoom = safeGet(STORAGE_KEYS.lastRoom) || "";
    safeSet(STORAGE_KEYS.previousRoom, previousLastRoom);
    safeSet(STORAGE_KEYS.lastRoom, currentRoomId);

    const visitedRooms = getVisitedRooms();
    if (!visitedRooms.includes(currentRoomId)) {
      visitedRooms.push(currentRoomId);
      setJsonArray(STORAGE_KEYS.visitedRooms, visitedRooms);
    } else {
      setJsonArray(STORAGE_KEYS.visitedRooms, visitedRooms);
    }

    return {
      previousRoom: previousLastRoom,
      visitedRooms
    };
  }

  function updateReturnToTop(currentRoomId, previousRoom, visitedRooms) {
    const cameBackToTop = currentRoomId === "top" && Boolean(previousRoom) && previousRoom !== "top" && visitedRooms.length > 0;
    if (!cameBackToTop) return false;
    setNumber(STORAGE_KEYS.returnedToTopCount, getNumber(STORAGE_KEYS.returnedToTopCount) + 1);
    return true;
  }

  function shouldShowGuide(visitCount) {
    return visitCount >= 2;
  }

  function getGuideState() {
    const params = getSearchParams();
    if (params.get("guideReset") === "1") {
      resetGuideStorage();
    }

    const currentRoomId = getCurrentRoomId();
    const visitCount = incrementVisitCount();
    const visitUpdate = updateRoomVisit(currentRoomId);
    const returnedToTop = updateReturnToTop(currentRoomId, visitUpdate.previousRoom, visitUpdate.visitedRooms);
    const visitedRooms = getVisitedRooms();
    const unvisitedRooms = getUnvisitedRooms(visitedRooms);

    return {
      currentRoomId,
      previousRoom: visitUpdate.previousRoom,
      lastRoom: currentRoomId,
      visitCount,
      visitedRooms,
      unvisitedRooms,
      returnedToTop,
      returnedToTopCount: getNumber(STORAGE_KEYS.returnedToTopCount),
      outsideHintSeen: getBoolean(STORAGE_KEYS.outsideHintSeen),
      supportHintSeen: getBoolean(STORAGE_KEYS.supportHintSeen),
      debug: isGuideDebug(params),
      reset: params.get("guideReset") === "1"
    };
  }

  function truncateMessage(message) {
    return message.length > MAX_MESSAGE_LENGTH ? message.slice(0, MAX_MESSAGE_LENGTH) : message;
  }

  function getGuideMessagesByState(state, options = {}) {
    if (state.returnedToTop && options.auto) return RETURN_MESSAGES;
    if (state.unvisitedRooms.length === 0) return COMPLETE_MESSAGES;
    if (state.visitedRooms.filter((roomId) => GUIDE_TARGET_ROOM_IDS.includes(roomId)).length >= 3) {
      return VISITED_MESSAGES.concat(UNVISITED_MESSAGES);
    }

    const messages = [];
    const supportUnvisited = state.unvisitedRooms.some((room) => room.id === "support");
    const outsideUnvisited = state.unvisitedRooms.some((room) => room.id === "outside");

    if (state.returnedToTop) messages.push(...RETURN_MESSAGES);
    if (supportUnvisited && (!state.supportHintSeen || !options.auto)) messages.push(...SUPPORT_HINT_MESSAGES);
    if (outsideUnvisited && (!state.outsideHintSeen || !options.auto)) messages.push(...OUTSIDE_HINT_MESSAGES);
    if (state.unvisitedRooms.length > 0) {
      messages.push(...UNVISITED_MESSAGES);
      const roomHint = state.unvisitedRooms.find((room) => room.id !== "support" && room.id !== "outside")?.hint;
      if (roomHint) messages.push(roomHint);
    }
    if (state.visitedRooms.length > 1) messages.push(...VISITED_MESSAGES);
    messages.push(...BASE_MESSAGES);
    return messages;
  }

  function pickGuideMessage(state, options = {}) {
    const messages = getGuideMessagesByState(state, options).map(truncateMessage);
    if (!messages.length) return BASE_MESSAGES[0];
    const currentIndex = getNumber(STORAGE_KEYS.messageIndex);
    const nextIndex = currentIndex % messages.length;
    setNumber(STORAGE_KEYS.messageIndex, currentIndex + 1);
    return messages[nextIndex];
  }

  function markHintSeen(message) {
    if (OUTSIDE_HINT_MESSAGES.includes(message)) setBoolean(STORAGE_KEYS.outsideHintSeen, true);
    if (SUPPORT_HINT_MESSAGES.includes(message)) setBoolean(STORAGE_KEYS.supportHintSeen, true);
  }

  function createGuideElement(state) {
    const guide = document.createElement("aside");
    guide.className = "kyoukai-guide";
    guide.setAttribute("aria-label", "小さな案内人");

    const button = document.createElement("button");
    button.className = "kyoukai-guide__body";
    button.type = "button";
    button.setAttribute("aria-label", "案内人に触れる");
    button.innerHTML = `
      <svg viewBox="0 0 64 64" role="img" aria-hidden="true" focusable="false">
        <path class="kyoukai-guide__aura" d="M32 3 C47 3 61 16 61 32 C61 49 47 61 32 61 C15 61 3 48 3 32 C3 15 16 3 32 3 Z" />
        <path class="kyoukai-guide__glow" d="M32 5 C45 5 58 17 58 32 C58 48 46 58 32 58 C17 58 6 47 6 32 C6 17 19 5 32 5 Z" />
        <path class="kyoukai-guide__shell" d="M32 10 C43 10 52 20 52 32 C52 45 43 53 32 53 C20 53 12 45 12 32 C12 20 21 10 32 10 Z" />
        <path class="kyoukai-guide__wing kyoukai-guide__wing--left" d="M17 27 C7 23 7 13 18 12 C23 17 23 23 17 27 Z" />
        <path class="kyoukai-guide__wing kyoukai-guide__wing--right" d="M47 27 C57 23 57 13 46 12 C41 17 41 23 47 27 Z" />
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
    button.addEventListener("click", () => showGuideMessage(guide, bubble, state));
    return { guide, bubble };
  }

  function showGuide(guide) {
    document.body.appendChild(guide);
    window.requestAnimationFrame(() => {
      guide.classList.add("kyoukai-guide--visible");
    });
    setBoolean(STORAGE_KEYS.seenGuide, true);
  }

  function hideGuideMessage(guide) {
    guide.classList.remove("kyoukai-guide--speaking");
  }

  function showGuideMessage(guide, bubble, state, options = {}) {
    window.clearTimeout(messageTimer);
    const message = pickGuideMessage(state, options);
    bubble.textContent = message;
    markHintSeen(message);
    guide.classList.add("kyoukai-guide--speaking");
    messageTimer = window.setTimeout(() => hideGuideMessage(guide), MESSAGE_HIDE_MS);
  }

  function logGuideState(state) {
    if (!state.debug) return;
    console.log("[KYOUKAI guide]", {
      visitCount: state.visitCount,
      currentRoomId: state.currentRoomId,
      previousRoom: state.previousRoom,
      lastRoom: state.lastRoom,
      visitedRooms: state.visitedRooms,
      unvisitedRooms: state.unvisitedRooms.map((room) => room.id),
      returnedToTopCount: state.returnedToTopCount,
      outsideHintSeen: state.outsideHintSeen,
      supportHintSeen: state.supportHintSeen,
      reset: state.reset
    });
  }

  function initKyoukaiGuide() {
    const state = getGuideState();
    logGuideState(state);

    if (!shouldShowGuide(state.visitCount)) return;

    const elements = createGuideElement(state);
    showGuide(elements.guide);

    if (state.returnedToTop) {
      window.setTimeout(() => showGuideMessage(elements.guide, elements.bubble, state, { auto: true }), AUTO_MESSAGE_DELAY_MS);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initKyoukaiGuide, { once: true });
  } else {
    initKyoukaiGuide();
  }
})();
