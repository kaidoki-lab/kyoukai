(function () {
  // 固定回数のカウントではなく、タップごとに少し進み、ときどきランダムで
  // 後退する積み上げ方式。
  // ゴール条件: 棒の当たり判定領域（.matsuri-pole-hit）の中心が、
  // 穴（.matsuri-hole）の中心に到達した深さ。
  // 当たり判定 top:5% height:8% → 中心9%／穴 top:-3% height:128% → 中心61%
  // 61 - 9 = 52。当たり判定や穴の位置を調整したら、この値も再計算する。
  const DEPTH_MAX = 52; // pole-stage の translateY% 上限
  const FORWARD_RANGE = [3, 7];
  const BACKWARD_RANGE = [2, 5];
  const FALLBACK_CHANCE = 0.3;

  const VOICE_TRACKS = [
    "/static/audio/matsuri/voices/yoi_01.mp3",
    "/static/audio/matsuri/voices/yoi_02.mp3",
    "/static/audio/matsuri/voices/oisa_01.mp3",
    "/static/audio/matsuri/voices/enya_01.mp3",
  ];
  const VOICE_MESSAGES = [
    "ヨイショ！",
    "ヨイショー！",
    "オイサ！",
    "エンヤ！",
    "ソレ！",
    "押せー！",
  ];
  const SFX_TRACKS = [
    "/static/audio/matsuri/sfx/wood_creak_01.mp3",
    "/static/audio/matsuri/sfx/wood_scrape_01.mp3",
    "/static/audio/matsuri/sfx/gakon_01.mp3",
  ];
  // ゴール（クライマックス）の瞬間だけ鳴らす花火音
  const CLIMAX_FIREWORK_TRACKS = [
    "/static/audio/matsuri/sfx/firework_handheld_01.mp3",
    "/static/audio/matsuri/sfx/firework_launch_01.mp3",
  ];
  const CHEER_TRACK = "/static/audio/matsuri/voices/cheer_far_01.mp3";
  const CONFETTI_SFX = "/static/audio/matsuri/sfx/confetti_01.mp3";
  const CLIMAX_MESSAGE = "ヨイショーー！！";
  const COMPLETE_MESSAGE = "奉納完了。";

  // 観客の歓声・拍手をランダムに流し続ける環境音ループ（途切れないよう重複再生を許容する）
  const CROWD_AMBIENT_TRACKS = [
    "/static/audio/matsuri/sfx/crowd_cheer_01.mp3",
    "/static/audio/matsuri/sfx/crowd_cheer_02.mp3",
    "/static/audio/matsuri/sfx/crowd_cheer_03.mp3",
    "/static/audio/matsuri/sfx/crowd_cheer_04.mp3",
  ];
  const CROWD_AMBIENT_VOLUME = 0.3;
  const CROWD_AMBIENT_GAP_MS = [900, 2600];
  const CROWD_AMBIENT_STREAMS = 3; // 同時に3本以上のループを独立に走らせ、重なりを作る
  let crowdAmbientStarted = false;
  const crowdAmbientTimers = [];

  const frame = document.getElementById("matsuriFrame");
  const poleStage = document.getElementById("matsuriPoleStage");
  const pole = document.getElementById("matsuriPole");
  const confettiLayer = document.getElementById("matsuriConfettiLayer");
  const messageEl = document.getElementById("matsuriMessage");
  const resetButton = document.getElementById("matsuriReset");
  const flashEl = document.getElementById("matsuriFlash");
  const impactEl = document.getElementById("matsuriImpactLines");

  let depth = 0;
  let isComplete = false;
  let messageTimer = null;

  function randomInRange([min, max]) {
    return min + Math.random() * (max - min);
  }

  function playAudio(src, volume) {
    if (!src) return;
    try {
      const node = new Audio(src);
      node.volume = typeof volume === "number" ? volume : 0.6;
      node.play().catch(() => {});
    } catch (e) {
      /* 音声未配置でも無視する */
    }
  }

  function playCrowdAmbientOnce(streamIndex) {
    // 前の音の終了を待たずに次を鳴らす。複数ストリームが独立に走るので、
    // タイミングがずれて瞬間的に重なる（同時開始ではない）。
    const src = CROWD_AMBIENT_TRACKS[Math.floor(Math.random() * CROWD_AMBIENT_TRACKS.length)];
    try {
      const node = new Audio(src);
      node.volume = CROWD_AMBIENT_VOLUME;
      node.play().catch(() => {});
    } catch (e) {
      /* 音声未配置でも無視する */
    }
    scheduleNextCrowdAmbient(streamIndex);
  }

  function scheduleNextCrowdAmbient(streamIndex) {
    const [min, max] = CROWD_AMBIENT_GAP_MS;
    const gap = min + Math.random() * (max - min);
    window.clearTimeout(crowdAmbientTimers[streamIndex]);
    crowdAmbientTimers[streamIndex] = window.setTimeout(() => playCrowdAmbientOnce(streamIndex), gap);
  }

  function startCrowdAmbient() {
    if (crowdAmbientStarted) return;
    crowdAmbientStarted = true;
    for (let i = 0; i < CROWD_AMBIENT_STREAMS; i += 1) {
      // 各ストリームをわずかにずらして開始し、同時にスタートしないようにする
      const startDelay = i * 350 + Math.random() * 300;
      window.setTimeout(() => playCrowdAmbientOnce(i), startDelay);
    }
  }

  function showMessage(text, duration) {
    if (!messageEl) return;
    window.clearTimeout(messageTimer);
    messageEl.textContent = text;
    messageEl.classList.add("is-visible");
    messageTimer = window.setTimeout(() => {
      messageEl.classList.remove("is-visible");
    }, duration || 1200);
  }

  function movePole() {
    if (!poleStage) return;
    poleStage.style.setProperty("--matsuri-pole-depth", `${depth}%`);
    poleStage.style.transform = `rotate(var(--matsuri-pole-tilt)) translateY(${depth}%)`;
    poleStage.classList.remove("is-shaking");
    // restart animation
    void poleStage.offsetWidth;
    poleStage.classList.add("is-shaking");
  }

  function shakeScreen() {
    if (!frame) return;
    frame.classList.remove("is-screen-shaking");
    void frame.offsetWidth;
    frame.classList.add("is-screen-shaking");
    window.setTimeout(() => frame.classList.remove("is-screen-shaking"), 220);
  }

  function spawnConfetti(count) {
    if (!confettiLayer) return;
    const colors = ["#e0c66a", "#d8483f", "#f4efe0", "#9bb15b"];
    for (let i = 0; i < count; i += 1) {
      const piece = document.createElement("span");
      piece.className = "matsuri-confetti-piece";
      piece.style.left = `${Math.random() * 100}%`;
      piece.style.background = colors[Math.floor(Math.random() * colors.length)];
      const duration = 1.6 + Math.random() * 1.4;
      piece.style.animationDuration = `${duration}s`;
      piece.style.animationDelay = `${Math.random() * 0.4}s`;
      confettiLayer.appendChild(piece);
      window.setTimeout(() => piece.remove(), (duration + 0.5) * 1000);
    }
  }

  function trackEvent(name, params) {
    if (typeof window.trackKyoukaiEvent === "function") {
      window.trackKyoukaiEvent(name, params || {});
    }
  }

  function runClimax() {
    isComplete = true;
    trackEvent("matsuri_climax");
    showMessage(CLIMAX_MESSAGE, 1800);
    shakeScreen();
    spawnConfetti(36);
    playAudio(CHEER_TRACK, 0.5);
    playAudio(CONFETTI_SFX, 0.5);
    playAudio(CLIMAX_FIREWORK_TRACKS[Math.floor(Math.random() * CLIMAX_FIREWORK_TRACKS.length)], 0.6);

    if (flashEl) {
      flashEl.classList.remove("is-active");
      void flashEl.offsetWidth;
      flashEl.classList.add("is-active");
    }
    if (impactEl) {
      impactEl.classList.remove("is-active");
      void impactEl.offsetWidth;
      impactEl.classList.add("is-active");
    }
    if (frame) {
      frame.classList.add("is-motion-blur");
      window.setTimeout(() => frame.classList.remove("is-motion-blur"), 350);
    }

    window.setTimeout(() => {
      showMessage(COMPLETE_MESSAGE, 4000);
    }, 1900);

    if (pole) pole.disabled = true;
    if (resetButton) resetButton.hidden = false;
  }

  function handleTap() {
    if (isComplete) return;

    const isFallback = Math.random() < FALLBACK_CHANCE;
    if (isFallback) {
      depth -= randomInRange(BACKWARD_RANGE);
    } else {
      depth += randomInRange(FORWARD_RANGE);
    }
    depth = Math.max(0, Math.min(DEPTH_MAX, depth));

    movePole();
    shakeScreen();

    if (Math.random() < 0.35) spawnConfetti(4);

    const voiceIndex = Math.floor(Math.random() * VOICE_TRACKS.length);
    playAudio(VOICE_TRACKS[voiceIndex], 0.55);
    showMessage(VOICE_MESSAGES[Math.floor(Math.random() * VOICE_MESSAGES.length)]);

    if (Math.random() < 0.6) {
      playAudio(SFX_TRACKS[Math.floor(Math.random() * SFX_TRACKS.length)], 0.45);
    }

    trackEvent("matsuri_tap", { depth, isFallback });

    if (depth >= DEPTH_MAX) {
      window.setTimeout(runClimax, 150);
    }
  }

  function resetMatsuri() {
    depth = 0;
    isComplete = false;
    if (pole) pole.disabled = false;
    if (poleStage) {
      poleStage.style.setProperty("--matsuri-pole-depth", "0%");
      poleStage.style.transform = "rotate(var(--matsuri-pole-tilt)) translateY(0)";
    }
    if (resetButton) resetButton.hidden = true;
    if (messageEl) messageEl.classList.remove("is-visible");
    trackEvent("matsuri_reset");
  }

  if (pole) {
    pole.addEventListener("click", handleTap);
  }
  if (resetButton) {
    resetButton.addEventListener("click", resetMatsuri);
  }

  ["pointerdown", "keydown", "touchstart"].forEach((eventName) => {
    document.addEventListener(eventName, startCrowdAmbient, { once: true, passive: true });
  });
  window.addEventListener("pagehide", () => {
    crowdAmbientTimers.forEach((timer) => window.clearTimeout(timer));
  });
})();
