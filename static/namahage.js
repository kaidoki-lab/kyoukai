(function () {
  "use strict";

  // ---------- 設定値（マジックナンバーを散在させない） ----------
  const CONFIG = {
    grid: { cols: 16, rows: 12 },
    idleIntervalMs: [1500, 4000],
    blinkIntervalMs: [3000, 8000],
    blinkStepMs: { toLine: 60, blank: 80, toDot: 60 },
    gyoroSwitchMs: [80, 180],
    gyoroDurationMs: [800, 2000],
    smileDurationMs: [500, 1500],
    frownDurationMs: [500, 1000],
    heartDurationMs: [600, 1500],
    surprisedDurationMs: [300, 600],
    trackingUpdateMs: 110,
    tapTrackingHoldMs: 1000,
    longPressMs: 600,
    rapidClickWindowMs: 2000,
    rapidClickFrownThreshold: 3,
    rapidClickBlackoutThreshold: 6,
    idleAfterMs: [10000, 30000],
    clickWeights: {
      smile: 0.25,
      surprised: 0.2,
      glaring: 0.2,
      frown: 0.15,
      mismatch: 0.1,
      heart: 0.07,
      hidden: 0.03,
    },
    reducedMotion: false,
  };

  const ROWS = CONFIG.grid.rows;
  const COLS = CONFIG.grid.cols;

  // ---------- 目パターン ----------
  // 16x12 のグリッド。0=透明 / 1=白ドット。
  function emptyGrid() {
    return Array.from({ length: ROWS }, () => new Array(COLS).fill(0));
  }

  function setPoints(grid, points) {
    points.forEach(([r, c]) => {
      if (r >= 0 && r < ROWS && c >= 0 && c < COLS) grid[r][c] = 1;
    });
    return grid;
  }

  function blockPattern(cx, cy, size) {
    const grid = emptyGrid();
    for (let r = 0; r < size; r += 1) {
      for (let c = 0; c < size; c += 1) {
        const gr = cy + r;
        const gc = cx + c;
        if (gr >= 0 && gr < ROWS && gc >= 0 && gc < COLS) grid[gr][gc] = 1;
      }
    }
    return grid;
  }

  const PATTERNS = {
    blank: () => emptyGrid(),
    dot: (cx, cy) => blockPattern(cx, cy, 2),
    largeDot: (cx, cy) => blockPattern(cx, cy, 4),
    line: () => setPoints(emptyGrid(), [[5, 5], [5, 6], [5, 7], [5, 8], [5, 9], [5, 10]]),
    smile: () => setPoints(emptyGrid(), [
      [7, 4], [8, 5], [9, 6], [9, 7], [9, 8], [9, 9], [8, 10], [7, 11],
    ]),
    frown: () => setPoints(emptyGrid(), [
      [5, 4], [4, 5], [3, 6], [3, 7], [3, 8], [3, 9], [4, 10], [5, 11],
    ]),
    heart: () => setPoints(emptyGrid(), [
      [3, 6], [3, 7], [3, 9], [3, 10],
      [4, 5], [4, 6], [4, 7], [4, 8], [4, 9], [4, 10], [4, 11],
      [5, 5], [5, 6], [5, 7], [5, 8], [5, 9], [5, 10], [5, 11],
      [6, 6], [6, 7], [6, 8], [6, 9], [6, 10],
      [7, 7], [7, 8], [7, 9],
      [8, 8],
    ]),
    question: () => setPoints(emptyGrid(), [
      [2, 6], [2, 7], [2, 8], [3, 9], [4, 9], [5, 8], [6, 7], [7, 7], [9, 7],
    ]),
    exclamation: () => setPoints(emptyGrid(), [
      [2, 7], [2, 8], [3, 7], [3, 8], [4, 7], [4, 8], [5, 7], [5, 8], [6, 7], [6, 8], [9, 7], [9, 8],
    ]),
    cross: () => setPoints(emptyGrid(), [
      [3, 5], [4, 6], [5, 7], [6, 8], [7, 9], [8, 10],
      [3, 10], [4, 9], [5, 8], [6, 7], [7, 6], [8, 5],
    ]),
    spiral: () => setPoints(emptyGrid(), [
      [4, 7], [3, 8], [4, 9], [5, 10], [6, 9], [6, 8], [6, 7], [5, 6], [4, 6],
    ]),
  };

  // 待機時の安全な視線位置候補（dotの左上座標, グリッド内に収まる範囲）
  const GAZE_POSITIONS = [
    { x: 6, y: 4, label: "center" },
    { x: 2, y: 4, label: "left" },
    { x: 10, y: 4, label: "right" },
    { x: 6, y: 1, label: "up" },
    { x: 6, y: 7, label: "down" },
    { x: 4, y: 4, label: "centerLeft" },
    { x: 8, y: 4, label: "centerRight" },
    { x: 1, y: 1, label: "outerUpLeft" },
    { x: 11, y: 1, label: "outerUpRight" },
  ];

  const GYORO_POSITIONS = [
    { x: 1, y: 1 }, { x: 11, y: 1 }, { x: 1, y: 7 }, { x: 11, y: 7 },
    { x: 6, y: 4 }, { x: 3, y: 4 }, { x: 9, y: 4 },
  ];

  // ---------- DOM ----------
  const frame = document.getElementById("namahageFrame");
  const canvasLeft = document.getElementById("namahageEyeLeft");
  const canvasRight = document.getElementById("namahageEyeRight");
  const debugEl = document.getElementById("namahageDebug");

  if (!frame || !canvasLeft || !canvasRight) return;

  const ctxLeft = canvasLeft.getContext("2d");
  const ctxRight = canvasRight.getContext("2d");

  const params = new URLSearchParams(window.location.search);
  const debugMode = params.get("debug") === "1";

  CONFIG.reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---------- 状態 ----------
  const state = {
    leftMode: "dot",
    rightMode: "dot",
    leftPos: { x: 6, y: 4 },
    rightPos: { x: 6, y: 4 },
    isLocked: false, // 特殊演出中は通常追従・まばたきを止める
  };

  const timers = new Set();
  function setT(fn, ms) {
    const id = window.setTimeout(() => {
      timers.delete(id);
      fn();
    }, ms);
    timers.add(id);
    return id;
  }
  function clearAllTimers() {
    timers.forEach((id) => window.clearTimeout(id));
    timers.clear();
  }
  function randRange([min, max]) {
    return min + Math.random() * (max - min);
  }
  function pick(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
  }

  function renderEye(ctx, mode, pos) {
    ctx.clearRect(0, 0, COLS, ROWS);
    const factory = PATTERNS[mode] || PATTERNS.dot;
    const grid = mode === "dot" || mode === "largeDot" ? factory(pos.x, pos.y) : factory();
    ctx.fillStyle = "#ffffff";
    for (let r = 0; r < ROWS; r += 1) {
      for (let c = 0; c < COLS; c += 1) {
        if (grid[r][c]) ctx.fillRect(c, r, 1, 1);
      }
    }
  }

  function render() {
    renderEye(ctxLeft, state.leftMode, state.leftPos);
    renderEye(ctxRight, state.rightMode, state.rightPos);
    if (debugMode) renderDebug();
  }

  function renderDebug() {
    if (!debugEl) return;
    debugEl.hidden = false;
    debugEl.textContent =
      `mode L:${state.leftMode} R:${state.rightMode}\n` +
      `pos L:${state.leftPos.x},${state.leftPos.y} R:${state.rightPos.x},${state.rightPos.y}\n` +
      `locked:${state.isLocked} clicks:${clickTimestamps.length}\n` +
      `longPress:${longPressActive}`;
  }

  function setBoth(mode, pos) {
    state.leftMode = mode;
    state.rightMode = mode;
    if (pos) {
      state.leftPos = pos;
      state.rightPos = pos;
    }
    render();
  }

  // ---------- まばたき ----------
  function blink() {
    if (state.isLocked) return;
    const doLeft = true;
    const doRight = Math.random() > 0.15 ? true : false; // 低確率で片目だけ
    const seq = [
      { mode: "line", delay: 0 },
      { mode: "blank", delay: CONFIG.blinkStepMs.toLine },
      { mode: "line", delay: CONFIG.blinkStepMs.toLine + CONFIG.blinkStepMs.blank },
      { mode: "dot", delay: CONFIG.blinkStepMs.toLine + CONFIG.blinkStepMs.blank + CONFIG.blinkStepMs.toDot },
    ];
    seq.forEach((step) => {
      setT(() => {
        if (state.isLocked) return;
        if (doLeft) state.leftMode = step.mode;
        if (doRight) state.rightMode = step.mode;
        render();
      }, step.delay);
    });
    scheduleBlink();
  }

  function scheduleBlink() {
    const interval = CONFIG.reducedMotion
      ? randRange(CONFIG.blinkIntervalMs) * 1.6
      : randRange(CONFIG.blinkIntervalMs);
    setT(blink, interval);
  }

  // ---------- 待機時の視線移動 ----------
  function idleGaze() {
    if (state.isLocked) return;
    const pos = pick(GAZE_POSITIONS);
    state.leftMode = "dot";
    state.rightMode = "dot";
    state.leftPos = pos;
    state.rightPos = Math.random() < 0.15
      ? pick(GAZE_POSITIONS) // 低確率で左右別方向
      : pos;
    render();
    scheduleIdleGaze();
  }

  function scheduleIdleGaze() {
    const interval = CONFIG.reducedMotion
      ? randRange(CONFIG.idleIntervalMs) * 1.5
      : randRange(CONFIG.idleIntervalMs);
    setT(idleGaze, interval);
  }

  // ---------- ギョロギョロ ----------
  function gyoro() {
    if (CONFIG.reducedMotion) return;
    state.isLocked = true;
    const duration = randRange(CONFIG.gyoroDurationMs);
    const endAt = Date.now() + duration;

    function step() {
      if (Date.now() >= endAt) {
        state.leftPos = { x: 6, y: 4 };
        state.rightPos = { x: 6, y: 4 };
        state.leftMode = "dot";
        state.rightMode = "dot";
        render();
        state.isLocked = false;
        return;
      }
      state.leftMode = "dot";
      state.rightMode = "dot";
      state.leftPos = pick(GYORO_POSITIONS);
      state.rightPos = pick(GYORO_POSITIONS);
      render();
      setT(step, randRange(CONFIG.gyoroSwitchMs));
    }
    step();
  }

  // ---------- 表情演出（クリック・特殊イベント共通） ----------
  function showExpression(mode, durationRange, after) {
    state.isLocked = true;
    setBoth(mode);
    const duration = Array.isArray(durationRange) ? randRange(durationRange) : durationRange;
    setT(() => {
      state.isLocked = false;
      setBoth("dot", { x: 6, y: 4 });
      if (typeof after === "function") after();
    }, duration);
  }

  function showSurprised() {
    state.isLocked = true;
    setBoth("largeDot", { x: 5, y: 2 });
    setT(() => {
      state.isLocked = false;
      setBoth("dot", { x: 6, y: 4 });
    }, randRange(CONFIG.surprisedDurationMs));
  }

  function showHeart() {
    state.isLocked = true;
    const variant = Math.random();
    if (variant < 0.5) {
      setBoth("heart");
    } else {
      // 片目だけ／遅れて表示
      state.leftMode = "heart";
      state.rightMode = "dot";
      render();
      setT(() => {
        state.rightMode = "heart";
        render();
      }, 150);
    }
    setT(() => {
      state.isLocked = false;
      setBoth("dot", { x: 6, y: 4 });
    }, randRange(CONFIG.heartDurationMs));
  }

  function showMismatch() {
    state.isLocked = true;
    state.leftMode = "dot";
    state.leftPos = pick(GAZE_POSITIONS);
    state.rightMode = "dot";
    state.rightPos = pick(GAZE_POSITIONS);
    render();
    setT(() => {
      state.isLocked = false;
      setBoth("dot", { x: 6, y: 4 });
    }, randRange(CONFIG.smileDurationMs));
  }

  function hideEyes() {
    state.isLocked = true;
    setBoth("blank");
    setT(() => {
      state.isLocked = false;
      setBoth("dot", { x: 6, y: 4 });
    }, 800);
  }

  function triggerClickReaction() {
    const weights = CONFIG.clickWeights;
    const roll = Math.random();
    let acc = 0;
    const order = ["smile", "surprised", "glaring", "frown", "mismatch", "heart", "hidden"];
    for (const key of order) {
      acc += weights[key];
      if (roll <= acc) {
        applyReaction(key);
        return;
      }
    }
    applyReaction("smile");
  }

  function applyReaction(key) {
    switch (key) {
      case "smile":
        showExpression("smile", CONFIG.smileDurationMs);
        break;
      case "surprised":
        showSurprised();
        break;
      case "glaring":
        gyoro();
        break;
      case "frown":
        showExpression("frown", CONFIG.frownDurationMs);
        break;
      case "mismatch":
        showMismatch();
        break;
      case "heart":
        showHeart();
        break;
      case "hidden":
        hideEyes();
        break;
      default:
        break;
    }
  }

  // ---------- 連続クリック ----------
  const clickTimestamps = [];
  function registerClick() {
    const now = Date.now();
    clickTimestamps.push(now);
    while (clickTimestamps.length && now - clickTimestamps[0] > CONFIG.rapidClickWindowMs) {
      clickTimestamps.shift();
    }
    if (clickTimestamps.length >= CONFIG.rapidClickBlackoutThreshold) {
      clickTimestamps.length = 0;
      state.isLocked = true;
      setBoth("blank");
      setT(() => {
        state.leftMode = "dot";
        state.leftPos = { x: 6, y: 4 };
        render();
      }, 500);
      setT(() => {
        state.rightMode = "dot";
        state.rightPos = { x: 6, y: 4 };
        state.isLocked = false;
        render();
      }, 700);
      return true;
    }
    if (clickTimestamps.length >= CONFIG.rapidClickFrownThreshold) {
      showExpression("frown", CONFIG.frownDurationMs);
      return true;
    }
    return false;
  }

  // ---------- 長押し ----------
  let longPressTimer = null;
  let longPressActive = false;
  let longPressSeqTimers = [];

  function clearLongPressSeq() {
    longPressSeqTimers.forEach((id) => {
      window.clearTimeout(id);
      timers.delete(id);
    });
    longPressSeqTimers = [];
  }

  function startLongPress(x, y) {
    longPressTimer = setT(() => {
      longPressActive = true;
      state.isLocked = true;
      const lookPos = posFromClientPoint(x, y);
      setBoth("dot", lookPos);
      longPressSeqTimers.push(setT(() => {
        setBoth("largeDot", lookPos);
        longPressSeqTimers.push(setT(() => {
          setBoth("blank");
          longPressSeqTimers.push(setT(() => {
            setBoth(Math.random() < 0.5 ? "smile" : "heart");
          }, 120));
        }, 150));
      }, 120));
    }, CONFIG.longPressMs);
  }

  function endLongPress() {
    if (longPressTimer) {
      window.clearTimeout(longPressTimer);
      timers.delete(longPressTimer);
      longPressTimer = null;
    }
    clearLongPressSeq();
    if (longPressActive) {
      longPressActive = false;
      state.isLocked = false;
      setBoth("dot", { x: 6, y: 4 });
    }
  }

  // ---------- カーソル / タップ追従 ----------
  function posFromClientPoint(clientX, clientY) {
    const rect = frame.getBoundingClientRect();
    const nx = (clientX - rect.left) / rect.width; // 0..1
    const ny = (clientY - rect.top) / rect.height;
    // 安全なグリッド範囲: x 1..12, y 1..8
    const x = Math.max(1, Math.min(12, Math.round(nx * 13)));
    const y = Math.max(1, Math.min(8, Math.round(ny * 9)));
    // 中央付近に近づいたら寄り目気味に（左右で少しずらす）
    return { x, y };
  }

  let lastTrackTime = 0;
  function handlePointerMove(event) {
    if (state.isLocked || longPressActive) return;
    const now = Date.now();
    if (now - lastTrackTime < CONFIG.trackingUpdateMs) return;
    lastTrackTime = now;
    const pos = posFromClientPoint(event.clientX, event.clientY);
    state.leftMode = "dot";
    state.rightMode = "dot";
    state.leftPos = pos;
    state.rightPos = pos;
    render();
    scheduleReturnToIdle();
  }

  let returnIdleTimer = null;
  function scheduleReturnToIdle() {
    if (returnIdleTimer) {
      window.clearTimeout(returnIdleTimer);
      timers.delete(returnIdleTimer);
    }
    returnIdleTimer = setT(() => {
      if (!state.isLocked) {
        state.leftPos = { x: 6, y: 4 };
        state.rightPos = { x: 6, y: 4 };
        render();
      }
    }, 1000);
  }

  function handleTouchStart(event) {
    if (state.isLocked) return;
    const touch = event.touches && event.touches[0];
    if (!touch) return;
    const pos = posFromClientPoint(touch.clientX, touch.clientY);
    state.leftMode = "dot";
    state.rightMode = "dot";
    state.leftPos = pos;
    state.rightPos = pos;
    render();
    setT(() => {
      if (!state.isLocked) {
        state.leftPos = { x: 6, y: 4 };
        state.rightPos = { x: 6, y: 4 };
        render();
      }
    }, CONFIG.tapTrackingHoldMs);
  }

  // ---------- 放置演出 ----------
  let lastInteractionAt = Date.now();
  function noteInteraction() {
    lastInteractionAt = Date.now();
  }

  function idleAfterCheckLoop() {
    setT(() => {
      const elapsed = Date.now() - lastInteractionAt;
      const threshold = randRange(CONFIG.idleAfterMs);
      if (elapsed >= threshold && !state.isLocked && !CONFIG.reducedMotion) {
        runIdleAfterEffect();
        lastInteractionAt = Date.now();
      }
      idleAfterCheckLoop();
    }, 4000);
  }

  function runIdleAfterEffect() {
    const effects = [
      () => setBoth("line"),
      () => { state.leftMode = "blank"; render(); },
      () => { state.rightMode = "blank"; render(); },
      () => setBoth("dot", pick(GAZE_POSITIONS)),
      () => setBoth("dot", { x: 6, y: 7 }),
    ];
    state.isLocked = true;
    pick(effects)();
    setT(() => {
      state.isLocked = false;
      setBoth("dot", { x: 6, y: 4 });
    }, 1200);
  }

  // ---------- イベント登録 ----------
  let pointerDownAt = null;
  frame.addEventListener("pointerdown", (event) => {
    noteInteraction();
    pointerDownAt = { x: event.clientX, y: event.clientY, time: Date.now() };
    startLongPress(event.clientX, event.clientY);
  });

  frame.addEventListener("pointerup", () => {
    noteInteraction();
    const wasLongPress = longPressActive;
    endLongPress();
    if (!wasLongPress && pointerDownAt && Date.now() - pointerDownAt.time < CONFIG.longPressMs) {
      if (!registerClick()) {
        triggerClickReaction();
      }
    }
    pointerDownAt = null;
  });

  frame.addEventListener("pointermove", (event) => {
    if (event.pointerType === "mouse") {
      noteInteraction();
      handlePointerMove(event);
    }
  });

  frame.addEventListener("touchstart", (event) => {
    noteInteraction();
    handleTouchStart(event);
  }, { passive: true });

  frame.addEventListener("pointerleave", () => {
    if (!state.isLocked) {
      setT(() => {
        if (!state.isLocked) {
          state.leftPos = { x: 6, y: 4 };
          state.rightPos = { x: 6, y: 4 };
          render();
        }
      }, 1000);
    }
  });

  window.addEventListener("pagehide", () => {
    clearAllTimers();
  });

  // ---------- 初期化 ----------
  render();
  scheduleIdleGaze();
  scheduleBlink();
  idleAfterCheckLoop();
  if (debugMode && frame) frame.classList.add("is-debug");
})();
