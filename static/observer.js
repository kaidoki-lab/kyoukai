(() => {
  const mascot = document.getElementById("mascot");
  const bubble = document.getElementById("speechBubble");
  const room = document.querySelector(".observer-room");
  const sprite = document.getElementById("mascotSprite");
  const dailyWord = document.getElementById("dailyWord");
  const outsideBox = document.getElementById("outsideBox");
  const roomHotspots = [...document.querySelectorAll("[data-room-hotspot]")];
  const floorBackY = () => window.innerHeight * 0.595;
  const floorFrontY = () => window.innerHeight * 0.9;
  const homeY = () => window.innerHeight * 0.72;
  const floorLeft = (y) => {
    const t = depthT(y);
    return window.innerWidth * (0.36 - t * 0.32);
  };
  const floorRight = (y) => {
    const t = depthT(y);
    return window.innerWidth * (0.64 + t * 0.32);
  };

  const idleLines = [
    "\u307f\u3066\u308b\uff1f",
    "\u307e\u305f\u304d\u305f\uff1f",
    "\u3053\u3053\u3060\u3088",
    "\u304d\u3087\u3046\u3082\u3044\u308b\u3088",
    "\u2026\u2026\uff1f"
  ];
  const boxLines = [
    "\u307e\u3060\u898b\u306a\u3044\u3067",
    "\u3042\u3052\u306a\u3044\u3067\u307b\u3057\u3044\u306a",
    "\u305d\u308c\u306f\u307e\u3060\u6574\u7406\u3067\u304d\u3066\u306a\u3044\u3088",
    "\u3053\u308c\u306f\u5916\u306e\u7bb1",
    "\u3044\u307e\u306f\u305d\u3063\u3068\u3057\u3066"
  ];
  const boxOpenLines = [
    "\u304d\u3087\u3046\u306f\u958b\u3044\u305F",
    "\u5916\u306b\u3064\u306a\u304C\u308B\u304B\u3082",
    "\u7bb1\u304c\u5c11\u3057\u3060\u3051\u958b\u3044\u305F"
  ];
  const dailyWords = [
    "\u304d\u3087\u3046\u3082\u3001\u90e8\u5c4b\u306f\u3072\u3089\u3044\u3066\u308b",
    "\u307e\u305F\u6765\u305f\uff1f",
    "\u3053\u3053\u3001\u3042\u3063\u305f\u304b\u3044\u306d",
    "\u898b\u3066\u308b\u306e\u3001\u3053\u3063\u3061\u304b\u3082",
    "\u7bb1\u306f\u307e\u3060\u5bdd\u3066\u308b",
    "\u304d\u3087\u3046\u306f\u9759\u304b\u306a\u65e5",
    "\u3042\u3057\u305f\u3082\u3001\u3044\u308b\u304b\u3082"
  ];
  const reverseLines = [
    "\u305d\u3063\u3061\uff1f",
    "\u307f\u3048\u3066\u308b\uff1f",
    "\u305d\u3053\u306b\u3044\u308b\uff1f",
    "\u2026\u2026\uff1f",
    "\u307e\u305f\u304d\u305f\u306d"
  ];
  const hotspotLines = [
    "\u306a\u306b\u304b\u3042\u308b",
    "\u3053\u3063\u3061\u884c\u304f",
    "\u3061\u3087\u3063\u3068\u898b\u308b",
    "\u3053\u308c\u304b\u306a",
    "\u307f\u3064\u3051\u305f"
  ];

  const state = {
    mouse: { x: window.innerWidth / 2, y: window.innerHeight / 2 },
    pos: { x: window.innerWidth / 2, y: homeY() },
    target: { x: window.innerWidth / 2, y: homeY() },
    home: { x: window.innerWidth / 2, y: homeY() },
    phase: 1,
    cursorReactions: 0,
    adReactions: 0,
    startedAt: performance.now(),
    lastMouseMoveAt: 0,
    awareUntil: 0,
    ignoreUntil: 0,
    tappingUntil: 0,
    nextNoticeAt: performance.now() + 1600,
    nextIdleStepAt: performance.now() + 4200,
    nextTiltAt: performance.now() + 3600,
    nextAdTapAt: performance.now() + 12000,
    nextRoamAt: performance.now() + 1600,
    roamingUntil: 0,
    lastWalkFrameAt: 0,
    frame: "idle",
    walkFlip: false,
    idleFlip: false,
    tapFlip: false,
  };

  const spriteFallbacks = {
    piko: {
      idle: "piko_trimmed/idle_1",
      idle2: "piko_trimmed/idle_2",
      walk1: "piko_trimmed/walk_1",
      walk2: "piko_trimmed/walk_2",
      lookLeft: "piko_trimmed/look_left",
      lookRight: "piko_trimmed/look_right",
      look: "piko_trimmed/idle_2",
      tilt: "piko_trimmed/tilt",
      tap1: "piko_trimmed/tap_1",
      tap2: "piko_trimmed/tap_2",
      tap: "piko_trimmed/tap_1"
    },
    flash: { idle: "flash_idle", walk1: "flash_walk1", walk2: "flash_walk2", look: "flash_look", tilt: "flash_tilt", tap: "flash_tap" },
    bear: { idle: "bear_idle", walk1: "bear_walk1", walk2: "bear_walk2", look: "bear_look", tilt: "bear_tilt", tap: "bear_tap" },
    gif: { idle: "gif_idle", walk1: "gif_walk1", walk2: "gif_walk2", look: "gif_idle", tilt: "gif_tilt", tap: "gif_tap" },
  };

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function depthT(y) {
    return clamp((y - floorBackY()) / (floorFrontY() - floorBackY()), 0, 1);
  }

  function scaleForY(y) {
    return 0.56 + depthT(y) * 0.58;
  }

  function boundaryYForX(x) {
    const points = [
      [0.00, 0.58],
      [0.18, 0.54],
      [0.32, 0.55],
      [0.43, 0.45],
      [0.54, 0.55],
      [0.72, 0.60],
      [1.00, 0.62],
    ];
    const nx = clamp(x / window.innerWidth, 0, 1);
    for (let i = 0; i < points.length - 1; i += 1) {
      const [x1, y1] = points[i];
      const [x2, y2] = points[i + 1];
      if (nx >= x1 && nx <= x2) {
        const t = (nx - x1) / (x2 - x1);
        return window.innerHeight * (y1 + (y2 - y1) * t);
      }
    }
    return window.innerHeight * 0.62;
  }

  function clampToFloor(point) {
    const minY = Math.max(floorBackY(), boundaryYForX(point.x));
    const y = clamp(point.y, minY, floorFrontY());
    return {
      x: clamp(point.x, floorLeft(y), floorRight(y)),
      y,
    };
  }

  function pick(list) {
    return list[Math.floor(Math.random() * list.length)];
  }

  function genomeKey() {
    const key = room?.dataset.genome || "flash";
    return spriteFallbacks[key] ? key : "flash";
  }

  function setSpriteFrame(action) {
    if (!sprite) return;
    const set = spriteFallbacks[genomeKey()];
    const name = set[action] || set.idle;
    const next = `/static/observer/assets/sprites/${name}.png`;
    if (sprite.getAttribute("src") !== next) sprite.setAttribute("src", next);
    state.frame = action;
  }

  function setIdleFrame() {
    state.idleFlip = !state.idleFlip;
    setSpriteFrame(state.idleFlip ? "idle" : "idle2");
  }

  function showBubble(text, duration = 2200) {
    bubble.textContent = text;
    bubble.classList.remove("hidden");
    window.clearTimeout(showBubble.timer);
    showBubble.timer = window.setTimeout(() => bubble.classList.add("hidden"), duration);
  }

  function setLook(dx, dy) {
    mascot.classList.remove("look-left", "look-right", "look-up", "look-front");
    if (state.phase >= 4) {
      mascot.classList.add("look-front");
    } else if (Math.abs(dx) > Math.abs(dy) && dx < -16) {
      mascot.classList.add("look-left");
      if (!mascot.classList.contains("walking")) setSpriteFrame("lookLeft");
    } else if (Math.abs(dx) > Math.abs(dy) && dx > 16) {
      mascot.classList.add("look-right");
      if (!mascot.classList.contains("walking")) setSpriteFrame("lookRight");
    } else if (dy < -24) {
      mascot.classList.add("look-up");
    } else {
      mascot.classList.add("look-front");
    }
  }

  function setPhase(next) {
    if (next === state.phase) return;
    state.phase = next;
    mascot.classList.remove("phase-1", "phase-2", "phase-3", "phase-4");
    mascot.classList.add(`phase-${next}`);
    showBubble(pick(reverseLines), 2400);
  }

  function updatePhase(now) {
    const elapsed = (now - state.startedAt) / 1000;
    if (elapsed > 70 || state.cursorReactions > 40 || state.adReactions > 3) setPhase(4);
    else if (elapsed > 44 || state.cursorReactions > 26 || state.adReactions > 2) setPhase(3);
    else if (elapsed > 20 || state.cursorReactions > 12 || state.adReactions > 0) setPhase(2);
  }

  function scheduleNotice(now) {
    state.nextNoticeAt = now + 180 + Math.random() * 520;
    state.awareUntil = now + 1600 + Math.random() * 1400;
  }

  function scheduleIdleStep(now) {
    const stepX = (Math.random() < 0.5 ? -1 : 1) * (44 + Math.random() * 96);
    const stepY = (Math.random() - 0.42) * 44;
    state.home = clampToFloor({ x: state.home.x + stepX, y: state.home.y + stepY });
    state.roamingUntil = now + 2200;
    mascot.classList.add("stepping");
    state.walkFlip = !state.walkFlip;
    setSpriteFrame(state.walkFlip ? "walk1" : "walk2");
    window.setTimeout(() => mascot.classList.remove("stepping"), 620);
    state.nextIdleStepAt = now + 5200 + Math.random() * 7600;
  }

  function hotspotTarget(element) {
    const rect = element.getBoundingClientRect();
    return clampToFloor({
      x: rect.left + rect.width * 0.5,
      y: rect.bottom + 24,
    });
  }

  function randomFloorTarget() {
    const y = window.innerHeight * (0.62 + Math.random() * 0.24);
    return clampToFloor({
      x: window.innerWidth * (0.22 + Math.random() * 0.58),
      y,
    });
  }

  function sendTo(point, now, line) {
    state.home = clampToFloor(point);
    state.roamingUntil = now + 3600;
    state.nextRoamAt = now + 4600 + Math.random() * 5200;
    state.awareUntil = 0;
    state.ignoreUntil = now + 900;
    mascot.classList.add("stepping");
    if (line) showBubble(line, 1800);
  }

  function scheduleRoam(now) {
    if (roomHotspots.length && Math.random() < 0.68) {
      sendTo(hotspotTarget(pick(roomHotspots)), now, Math.random() < 0.42 ? pick(hotspotLines) : "");
    } else {
      sendTo(randomFloorTarget(), now, "");
    }
  }

  function scheduleTilt(now) {
    mascot.classList.add("tilting");
    setSpriteFrame("tilt");
    window.setTimeout(() => {
      mascot.classList.remove("tilting");
      setSpriteFrame("idle");
    }, 900);
    state.nextTiltAt = now + 4800 + Math.random() * 8600;
  }

  function boxTarget() {
    if (!outsideBox) return { x: window.innerWidth * 0.64, y: homeY() };
    const rect = outsideBox.getBoundingClientRect();
    return clampToFloor({
      x: rect.left - 54,
      y: rect.bottom + 40,
    });
  }

  function triggerBoxTap(now) {
    state.adReactions += 1;
    state.tappingUntil = now + 3000;
    state.nextAdTapAt = now + 18000 + Math.random() * 19000;
    mascot.classList.add("tapping");
    setSpriteFrame("tap");
    outsideBox?.classList.add("box-attention");
    window.setTimeout(() => outsideBox?.classList.remove("box-attention"), 1700);
    window.setTimeout(() => showBubble(pick(boxLines), 2300), 650);
  }

  function chooseTarget(now) {
    const mouseDx = state.mouse.x - state.pos.x;
    const mouseDy = state.mouse.y - state.pos.y;
    let next = { ...state.home };

    if (now < state.tappingUntil) {
      setSpriteFrame(Math.floor(now / 320) % 2 === 0 ? "tap1" : "tap2");
      return boxTarget();
    }

    mascot.classList.remove("tapping");

    if (state.phase >= 3 && now > state.ignoreUntil && Math.random() < 0.08) {
      state.ignoreUntil = now + 1400 + Math.random() * 1600;
    }

    const noticing = now < state.awareUntil && now > state.ignoreUntil;
    if (noticing) {
      const strength = state.phase === 1 ? 0.7 : state.phase === 2 ? 0.84 : state.phase === 3 ? 0.62 : 0.36;
      next = clampToFloor({
        x: state.pos.x + clamp(mouseDx * strength, -260, 260),
        y: state.pos.y + clamp(mouseDy * (state.phase >= 4 ? 0.18 : 0.36), -108, 130),
      });
    } else if (state.phase >= 4) {
      if (state.frame !== "idle" && state.frame !== "idle2" && now > state.roamingUntil) setSpriteFrame("idle");
      next = now < state.roamingUntil ? { ...state.home } : clampToFloor({ x: window.innerWidth / 2, y: homeY() });
    } else if (state.frame !== "tilt") {
      if (state.frame !== "idle" && state.frame !== "idle2") setSpriteFrame("idle");
    }

    return next;
  }

  function tick() {
    const now = performance.now();
    updatePhase(now);

    if (now > state.nextNoticeAt) scheduleNotice(now);
    if (now > state.nextRoamAt && now > state.tappingUntil) scheduleRoam(now);
    if (now > state.nextIdleStepAt && state.phase < 4 && now > state.tappingUntil) scheduleIdleStep(now);
    if (now > state.nextTiltAt && now > state.tappingUntil) scheduleTilt(now);
    if (now > state.nextAdTapAt && state.phase >= 2) triggerBoxTap(now);

    state.target = chooseTarget(now);
    const lag = state.phase >= 4 ? 0.06 : 0.12;
    const dxToTarget = state.target.x - state.pos.x;
    const dyToTarget = state.target.y - state.pos.y;
    state.pos.x += dxToTarget * lag;
    state.pos.y += dyToTarget * lag;

    const moving = Math.hypot(dxToTarget, dyToTarget) > 10 && now > state.tappingUntil && !mascot.classList.contains("tilting");
    mascot.classList.toggle("walking", moving);
    if (moving && now - state.lastWalkFrameAt > 210) {
      state.walkFlip = !state.walkFlip;
      setSpriteFrame(state.walkFlip ? "walk1" : "walk2");
      state.lastWalkFrameAt = now;
    }

    mascot.style.left = `${Math.round(state.pos.x)}px`;
    mascot.style.top = `${Math.round(state.pos.y)}px`;
    mascot.style.setProperty("--mascot-scale", scaleForY(state.pos.y).toFixed(3));
    mascot.style.zIndex = String(20 + Math.round(depthT(state.pos.y) * 30));

    const dx = state.mouse.x - state.pos.x;
    const dy = state.mouse.y - state.pos.y;
    if (now < state.awareUntil && now > state.ignoreUntil) setLook(dx, dy);
    else setLook(0, 0);
  }

  function spriteIdleLoop() {
    if (performance.now() > state.tappingUntil && !mascot.classList.contains("tilting") && !mascot.classList.contains("stepping") && !mascot.classList.contains("walking")) {
      setIdleFrame();
    }
    setTimeout(spriteIdleLoop, 520);
  }

  function blinkLoop() {
    mascot.classList.add("blink");
    setTimeout(() => mascot.classList.remove("blink"), 120);
    setTimeout(blinkLoop, 1800 + Math.random() * 4300);
  }

  function bubbleLoop() {
    if (performance.now() > state.tappingUntil) {
      const lines = state.phase >= 3 ? reverseLines : idleLines;
      showBubble(pick(lines), 1700 + Math.random() * 1200);
    }
    setTimeout(bubbleLoop, 6200 + Math.random() * 9000);
  }

  window.addEventListener("mousemove", (event) => {
    state.mouse.x = event.clientX;
    state.mouse.y = event.clientY;
    state.lastMouseMoveAt = performance.now();
    if (performance.now() > state.nextNoticeAt - 400) {
      state.cursorReactions += 1;
    }
    state.awareUntil = performance.now() + 1800;
  }, { passive: true });

  window.addEventListener("resize", () => {
    state.home = clampToFloor({ x: state.home.x, y: homeY() });
    state.pos = clampToFloor(state.pos);
  });

  outsideBox?.addEventListener("mouseenter", () => {
    state.nextAdTapAt = performance.now() + 450;
    state.awareUntil = performance.now() + 2200;
  });

  outsideBox?.addEventListener("click", (event) => {
    if (Math.random() >= 0.01) {
      event.preventDefault();
      showBubble(pick(boxLines), 2200);
      triggerBoxTap(performance.now());
    } else {
      showBubble(pick(boxOpenLines), 900);
    }
  });

  roomHotspots.forEach((hotspot) => {
    hotspot.addEventListener("mouseenter", () => {
      state.awareUntil = performance.now() + 1400;
    });
    hotspot.addEventListener("click", () => {
      sendTo(hotspotTarget(hotspot), performance.now(), pick(hotspotLines));
    });
  });

  setInterval(tick, 100);
  if (dailyWord) dailyWord.textContent = pick(dailyWords);
  setSpriteFrame("idle");
  setTimeout(spriteIdleLoop, 520);
  setTimeout(blinkLoop, 700);
  setTimeout(bubbleLoop, 1300);
})();
