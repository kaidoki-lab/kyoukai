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
    { id: "observation", path: "/observation", label: "観測室", hint: "未ダ見テイナイ場所" },
    { id: "archive", path: "/archive", label: "残留域", hint: "記録反応アリ" },
    { id: "signal", path: "/signal", label: "音声室", hint: "音ノ反応" },
    { id: "hyougi", path: "/hyougi", label: "評議", hint: "声ノ反応" },
    { id: "exit", path: "/exit", label: "脱出室", hint: "出口反応" },
    { id: "null", path: "/null", label: "崩落域", hint: "崩レ反応" },
    { id: "outside", path: "/outside", label: "外部接続", hint: "外ノ気配ガアル" },
    { id: "support", path: "/support", label: "小さな箱", hint: "箱、アルネ" }
  ];

  const GUIDE_TARGET_ROOM_IDS = KYOUKAI_ROOMS.map((room) => room.id);

  const BASE_MESSAGES = [
    "微弱反応",
    "此処、鳴ル",
    "気配ガアル",
    "ソコ、見タヨ",
    "未確認"
  ];

  const RETURN_MESSAGES = [
    "戻レルヨ",
    "戻ッタネ",
    "帰還反応",
    "記録アリ"
  ];

  const VISITED_MESSAGES = [
    "ソコ、見タヨ",
    "歩行記録アリ",
    "気配ガ増エタ"
  ];

  const UNVISITED_MESSAGES = [
    "未ダ見テイナイ場所",
    "反応、薄イ",
    "奥ニアル",
    "未確認"
  ];

  const OUTSIDE_HINT_MESSAGES = [
    "外ノ気配ガアル",
    "外ニツナガル",
    "棚ノ気配",
    "外部接続"
  ];

  const SUPPORT_HINT_MESSAGES = [
    "箱、アルネ",
    "置ケル場所",
    "小サナ反応",
    "気配ガ残ル"
  ];

  const COMPLETE_MESSAGES = [
    "巡回済み",
    "記録あり",
    "まだ変わる"
  ];

  const DETECTION_MESSAGES = {
    default: ["反応アリ", "此処、触レル", "接続点", "開ク場所"],
    outside: ["外ノ気配ガアル", "外ニツナガル", "棚ノ気配", "外部接続"],
    support: ["箱、アルネ", "置ケル場所", "小サナ反応", "気配ガ残ル"],
    room: ["部屋反応", "奥ニアル", "入口反応", "未確認"],
    home: ["戻レルヨ", "帰還点", "記録地点"],
    external: ["外部接続", "外ノ気配", "遠イ反応"]
  };

  const MESSAGE_HIDE_MS = 3000;
  const AUTO_MESSAGE_DELAY_MS = 850;
  const MAX_MESSAGE_LENGTH = 18;
  const DETECTION_COOLDOWN_MS = 1600;
  const DESKTOP_OFFSET_X = 18;
  const DESKTOP_OFFSET_Y = 14;
  const MOBILE_OFFSET_X = 18;
  const MOBILE_OFFSET_Y = -72;

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
  let detectTimer = 0;

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

  function pickFromList(messages, key = STORAGE_KEYS.messageIndex) {
    const safeMessages = messages.map(truncateMessage);
    if (!safeMessages.length) return BASE_MESSAGES[0];
    const currentIndex = getNumber(key);
    const nextIndex = currentIndex % safeMessages.length;
    setNumber(key, currentIndex + 1);
    return safeMessages[nextIndex];
  }

  function pickGuideMessage(state, options = {}) {
    return pickFromList(getGuideMessagesByState(state, options));
  }

  function markHintSeen(message) {
    if (OUTSIDE_HINT_MESSAGES.includes(message)) setBoolean(STORAGE_KEYS.outsideHintSeen, true);
    if (SUPPORT_HINT_MESSAGES.includes(message)) setBoolean(STORAGE_KEYS.supportHintSeen, true);
  }

  function isDesktopPointer() {
    try {
      return window.matchMedia("(hover: hover) and (pointer: fine)").matches;
    } catch (_) {
      return false;
    }
  }

  function createGuideElement(state, desktopPointer) {
    const guide = document.createElement("aside");
    guide.className = `kyoukai-guide${desktopPointer ? " kyoukai-guide--cursor" : " kyoukai-guide--dock"}`;
    guide.setAttribute("aria-label", "境界探知機");

    const button = document.createElement("button");
    button.className = "kyoukai-guide__body";
    button.type = "button";
    button.setAttribute("aria-label", "境界探知機に触れる");
    button.innerHTML = `
      <span class="kyoukai-guide__probe" aria-hidden="true">
        <span class="kyoukai-guide__tail"></span>
        <span class="kyoukai-guide__ring"></span>
        <span class="kyoukai-guide__head">
          <span class="kyoukai-guide__core"></span>
          <span class="kyoukai-guide__needle"></span>
        </span>
        <span class="kyoukai-guide__charm"></span>
      </span>
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
    const message = options.message || pickGuideMessage(state, options);
    bubble.textContent = message;
    markHintSeen(message);
    guide.classList.add("kyoukai-guide--speaking");
    messageTimer = window.setTimeout(() => hideGuideMessage(guide), MESSAGE_HIDE_MS);
  }

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  function classifyTarget(element) {
    if (!element) return { type: "", key: "" };
    const target = element.closest?.("a, button, [data-guide-hint]");
    if (!target || target.classList?.contains("kyoukai-guide__body")) return { type: "", key: "" };

    const hint = target.getAttribute("data-guide-hint") || "";
    const rawHref = target.getAttribute("href") || target.getAttribute("data-href") || "";
    let href = rawHref;
    try {
      href = rawHref ? new URL(rawHref, window.location.href).href : "";
    } catch (_) {}

    const textKey = `${hint} ${rawHref} ${target.textContent || ""}`.toLowerCase();
    const hrefKey = String(href || rawHref).toLowerCase();
    let pathname = "";
    try {
      pathname = href ? new URL(href, window.location.href).pathname.replace(/\/+$/g, "") || "/" : "";
    } catch (_) {}
    const key = `${target.tagName}:${rawHref}:${hint}:${(target.textContent || "").trim().slice(0, 24)}`;

    if (textKey.includes("outside") || hrefKey.includes("/outside")) return { type: "outside", key };
    if (textKey.includes("support") || textKey.includes("ofuse") || hrefKey.includes("/support") || hrefKey.includes("ofuse.me")) {
      return { type: "support", key };
    }
    if (hrefKey.startsWith("http") && !hrefKey.includes(window.location.host.toLowerCase())) return { type: "external", key };
    if (pathname === "/" || hrefKey.includes("/index") || hrefKey.includes("/home")) return { type: "home", key };
    if (/(exit|observer|record|voice|archive|signal|observation|hyougi|null)/.test(textKey) || /(exit|observer|record|voice|archive|signal|observation|hyougi|null)/.test(hrefKey)) {
      return { type: "room", key };
    }
    return { type: "default", key };
  }

  function setReactionClass(guide, type) {
    ["react", "outside", "support", "room", "external", "home"].forEach((name) => {
      guide.classList.remove(`kyoukai-guide--${name}`);
    });
    if (!type) return;
    guide.classList.add("kyoukai-guide--react");
    if (type !== "default") guide.classList.add(`kyoukai-guide--${type}`);
  }

  function getDetectionMessage(type) {
    return pickFromList(DETECTION_MESSAGES[type] || DETECTION_MESSAGES.default);
  }

  function setupCursorGuide(guide, bubble, state) {
    let targetX = window.innerWidth * 0.5;
    let targetY = window.innerHeight * 0.5;
    let currentX = targetX;
    let currentY = targetY;
    let lastTargetKey = "";
    let lastDetectionAt = 0;
    let frameId = 0;

    function moveGuide() {
      const guideWidth = guide.offsetWidth || 56;
      const guideHeight = guide.offsetHeight || 56;
      const maxX = Math.max(8, window.innerWidth - guideWidth - 8);
      const maxY = Math.max(8, window.innerHeight - guideHeight - 8);
      currentX += (targetX - currentX) * 0.18;
      currentY += (targetY - currentY) * 0.18;
      const nextLeft = clamp(currentX + DESKTOP_OFFSET_X, 8, maxX);
      const nextTop = clamp(currentY + DESKTOP_OFFSET_Y, 8, maxY);
      guide.style.left = `${nextLeft}px`;
      guide.style.top = `${nextTop}px`;
      guide.classList.toggle("kyoukai-guide--bubble-left", nextLeft > window.innerWidth - 250);
      guide.classList.toggle("kyoukai-guide--bubble-up", nextTop > window.innerHeight - 92);
      frameId = window.requestAnimationFrame(moveGuide);
    }

    function updateDetection(event) {
      const element = document.elementFromPoint(event.clientX, event.clientY);
      const detected = classifyTarget(element);
      setReactionClass(guide, detected.type);

      if (!detected.type) {
        lastTargetKey = "";
        return;
      }

      const now = Date.now();
      if (detected.key !== lastTargetKey && now - lastDetectionAt > DETECTION_COOLDOWN_MS) {
        lastTargetKey = detected.key;
        lastDetectionAt = now;
        showGuideMessage(guide, bubble, state, { message: getDetectionMessage(detected.type) });
      }
    }

    function onMouseMove(event) {
      targetX = event.clientX;
      targetY = event.clientY;
      window.clearTimeout(detectTimer);
      detectTimer = window.setTimeout(() => updateDetection(event), 24);
    }

    window.addEventListener("mousemove", onMouseMove, { passive: true });
    window.addEventListener("pagehide", () => {
      window.cancelAnimationFrame(frameId);
      window.removeEventListener("mousemove", onMouseMove);
    }, { once: true });
    moveGuide();
  }

  function setupTouchGuide(guide, bubble, state) {
    const guideWidth = guide.offsetWidth || 52;
    const guideHeight = guide.offsetHeight || 52;
    let targetX = window.innerWidth - guideWidth - 12;
    let targetY = window.innerHeight - guideHeight - 72;
    let currentX = targetX;
    let currentY = targetY;
    let frameId = 0;
    let lastTargetKey = "";
    let lastDetectionAt = 0;

    guide.classList.add("kyoukai-guide--touch-follow");

    function moveGuide() {
      const maxX = Math.max(8, window.innerWidth - guideWidth - 8);
      const maxY = Math.max(8, window.innerHeight - guideHeight - 8);
      currentX += (targetX - currentX) * 0.14;
      currentY += (targetY - currentY) * 0.14;
      const nextLeft = clamp(currentX, 8, maxX);
      const nextTop = clamp(currentY, 8, maxY);
      guide.style.left = `${nextLeft}px`;
      guide.style.top = `${nextTop}px`;
      guide.classList.toggle("kyoukai-guide--bubble-left", nextLeft > window.innerWidth - 220);
      guide.classList.toggle("kyoukai-guide--bubble-up", nextTop > window.innerHeight - 116);
      frameId = window.requestAnimationFrame(moveGuide);
    }

    function updateDetection(clientX, clientY) {
      const detected = classifyTarget(document.elementFromPoint(clientX, clientY));
      setReactionClass(guide, detected.type);
      if (!detected.type) {
        lastTargetKey = "";
        return;
      }

      const now = Date.now();
      if (detected.key !== lastTargetKey && now - lastDetectionAt > DETECTION_COOLDOWN_MS) {
        lastTargetKey = detected.key;
        lastDetectionAt = now;
        showGuideMessage(guide, bubble, state, { message: getDetectionMessage(detected.type) });
      }
    }

    function follow(clientX, clientY) {
      targetX = clientX + MOBILE_OFFSET_X;
      targetY = clientY + MOBILE_OFFSET_Y;
      window.clearTimeout(detectTimer);
      detectTimer = window.setTimeout(() => updateDetection(clientX, clientY), 32);
    }

    function onPointerMove(event) {
      if (event.pointerType === "mouse" || event.pointerType === "pen") {
        follow(event.clientX, event.clientY);
      }
    }

    function onTouchMove(event) {
      const touch = event.touches[0];
      if (touch) follow(touch.clientX, touch.clientY);
    }

    window.addEventListener("pointermove", onPointerMove, { passive: true });
    window.addEventListener("touchstart", onTouchMove, { passive: true });
    window.addEventListener("touchmove", onTouchMove, { passive: true });
    window.addEventListener("pagehide", () => {
      window.cancelAnimationFrame(frameId);
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("touchstart", onTouchMove);
      window.removeEventListener("touchmove", onTouchMove);
    }, { once: true });
    moveGuide();
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

    const desktopPointer = isDesktopPointer();
    const elements = createGuideElement(state, desktopPointer);
    showGuide(elements.guide);

    if (desktopPointer) {
      setupCursorGuide(elements.guide, elements.bubble, state);
    } else {
      setupTouchGuide(elements.guide, elements.bubble, state);
    }

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
