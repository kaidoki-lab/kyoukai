/**
 * KYOUKAI Guide Intro v1.0
 * 初回訪問のみ表示するオープニング会話イベント。
 * 完了後に追従案内人(kyoukai-guide.js)を起動する。
 */
(() => {
  "use strict";

  const INTRO_DONE_KEY = "kyoukai_intro_done";
  const SKIP_DELAY_MS  = 2600;
  const CHAR_DELAY_MS  = 52;
  const VOICE_EVERY_N  = 3;

  // ── 会話テキスト（ここを変更するだけで内容が変わる） ──────────────────────
  const INTRO_TEXT = [
    "初めてですか？",
    "",
    "ここはKYOUKAIです。",
    "",
    "何かが起きている場所です。",
    "何があるかは、見てみないとわかりません。",
    "言葉で説明できない場所です。",
    "",
    "ゲームではありません。",
    "順番もありません。",
    "",
    "気になった場所を",
    "自由に観測してください。",
    "",
    "部屋によって少し違う体験があります。",
    "",
    "全部見る必要はありません。",
    "",
    "あなたが気になった場所から",
    "始めてください。",
  ].join("\n");

  // ── 音声合成パラメータ（Web Audio API / 音声ファイル不要） ──────────────
  // [基本周波数, 波形, 持続時間(sec), アタック(sec)]
  const VOICE_CONFIGS = [
    [275, "sine",     0.078, 0.005],
    [338, "triangle", 0.060, 0.004],
    [218, "sine",     0.098, 0.006],
    [376, "triangle", 0.068, 0.004],
    [258, "sine",     0.088, 0.005],
    [308, "triangle", 0.075, 0.004],
    [242, "sine",     0.105, 0.006],
    [356, "triangle", 0.062, 0.003],
  ];

  let _audioCtx = null;

  function getAudioCtx() {
    if (_audioCtx) {
      if (_audioCtx.state === "suspended") _audioCtx.resume().catch(() => {});
      return _audioCtx;
    }
    try {
      _audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    } catch (_) {
      return null;
    }
    return _audioCtx;
  }

  // 擬似言語音声 — 2〜3文字ごとに発音
  function playVoice() {
    const ctx = getAudioCtx();
    if (!ctx) return;

    const cfg = VOICE_CONFIGS[Math.floor(Math.random() * VOICE_CONFIGS.length)];
    const [baseFreq, waveType, baseDur, atk] = cfg;

    // Pitch 0.92〜1.08 / PlaybackRate 0.95〜1.05
    const pitch = 0.92 + Math.random() * 0.16;
    const rate  = 0.95 + Math.random() * 0.10;
    const freq  = baseFreq * pitch;
    const dur   = baseDur * rate;

    const osc    = ctx.createOscillator();
    const gain   = ctx.createGain();
    const filter = ctx.createBiquadFilter();

    filter.type            = "bandpass";
    filter.frequency.value = freq * 1.6;
    filter.Q.value         = 3.2;

    osc.type            = waveType;
    osc.frequency.value = freq;

    const now = ctx.currentTime;
    gain.gain.setValueAtTime(0, now);
    gain.gain.linearRampToValueAtTime(0.13, now + atk);
    gain.gain.exponentialRampToValueAtTime(0.001, now + dur);

    // わずかなピッチ変化で「話している」感を演出
    osc.frequency.setValueAtTime(freq, now);
    osc.frequency.linearRampToValueAtTime(freq * 0.965, now + dur);

    osc.connect(filter);
    filter.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + dur + 0.015);
  }

  // CRTノイズ — 案内人表示直後の効果音
  function playCrtNoise() {
    const ctx = getAudioCtx();
    if (!ctx) return;
    try {
      const bufLen = Math.ceil(ctx.sampleRate * 0.16);
      const buf    = ctx.createBuffer(1, bufLen, ctx.sampleRate);
      const data   = buf.getChannelData(0);
      for (let i = 0; i < bufLen; i++) data[i] = (Math.random() * 2 - 1) * 0.055;

      const src    = ctx.createBufferSource();
      src.buffer   = buf;

      const hpf    = ctx.createBiquadFilter();
      hpf.type     = "highpass";
      hpf.frequency.value = 2000;

      const gain   = ctx.createGain();
      const now    = ctx.currentTime;
      gain.gain.setValueAtTime(0.55, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.16);

      src.connect(hpf);
      hpf.connect(gain);
      gain.connect(ctx.destination);
      src.start(now);
    } catch (_) {}
  }

  // ── 案内人フィギュア HTML（既存CSSと共用） ─────────────────────────────
  function guideProbeHTML() {
    return `<button class="kyoukai-guide__body" type="button" tabindex="-1" aria-hidden="true">
      <span class="kyoukai-guide__probe" aria-hidden="true">
        <span class="kyoukai-guide__tail"></span>
        <span class="kyoukai-guide__ring"></span>
        <span class="kyoukai-guide__head">
          <span class="kyoukai-guide__core"></span>
          <span class="kyoukai-guide__needle"></span>
        </span>
        <span class="kyoukai-guide__charm"></span>
      </span>
    </button>`;
  }

  // ── オーバーレイ構築 ────────────────────────────────────────────────────
  function buildOverlay() {
    const el = document.createElement("div");
    el.className = "kgi-overlay";
    el.setAttribute("role", "dialog");
    el.setAttribute("aria-modal", "true");
    el.setAttribute("aria-label", "KYOUKAIへの案内");
    el.innerHTML = `
      <div class="kgi-stage">
        <div class="kgi-figure kyoukai-guide kyoukai-guide--dock" aria-hidden="true">
          ${guideProbeHTML()}
        </div>
        <div class="kgi-dialogue">
          <p class="kgi-dialogue__text" aria-live="polite"></p>
        </div>
        <div class="kgi-actions" aria-hidden="true">
          <button class="kgi-btn kgi-btn--primary" type="button">▶ 観測を始める</button>
          <button class="kgi-btn kgi-btn--skip" type="button" aria-label="会話をスキップ">スキップ</button>
        </div>
      </div>`;
    return el;
  }

  // ── タイプライター ──────────────────────────────────────────────────────
  function typeWriter(textEl, text, charDelay, onVoice, onDone) {
    let i = 0, charCount = 0, timer = 0;

    const cursor = document.createElement("span");
    cursor.className = "kgi-cursor";
    cursor.setAttribute("aria-hidden", "true");
    textEl.appendChild(cursor);

    function tick() {
      if (i >= text.length) {
        cursor.remove();
        onDone();
        return;
      }
      const ch = text[i++];
      textEl.insertBefore(document.createTextNode(ch), cursor);
      charCount++;
      if (ch !== "\n" && ch !== " " && charCount % VOICE_EVERY_N === 0) {
        onVoice();
      }
      timer = window.setTimeout(tick, ch === "\n" ? charDelay * 4 : charDelay);
    }

    tick();
    return () => window.clearTimeout(timer);
  }

  // ── GA4 ────────────────────────────────────────────────────────────────
  function trackEvent(name, params) {
    if (typeof window.trackKyoukaiEvent === "function") {
      window.trackKyoukaiEvent(name, params || {});
    } else if (typeof window.gtag === "function") {
      window.gtag("event", name, params || {});
    }
  }

  // ── 終了処理（完了 or スキップ） ────────────────────────────────────────
  function finishIntro(overlay, completed) {
    try { localStorage.setItem(INTRO_DONE_KEY, "1"); } catch (_) {}
    trackEvent(completed ? "guide_intro_complete" : "guide_intro_skip", {});

    overlay.classList.add("kgi-overlay--out");
    window.setTimeout(() => {
      overlay.remove();
      if (typeof window.__kyoukaiStartFollowGuide === "function") {
        window.__kyoukaiStartFollowGuide();
      }
    }, 540);
  }

  // ── メインInit ──────────────────────────────────────────────────────────
  function runIntro() {
    const overlay = buildOverlay();
    document.body.appendChild(overlay);

    const figure    = overlay.querySelector(".kgi-figure");
    const textEl    = overlay.querySelector(".kgi-dialogue__text");
    const actions   = overlay.querySelector(".kgi-actions");
    const startBtn  = overlay.querySelector(".kgi-btn--primary");
    const skipBtn   = overlay.querySelector(".kgi-btn--skip");

    trackEvent("guide_intro_show", {});

    // フェードイン
    requestAnimationFrame(() => {
      overlay.classList.add("kgi-overlay--in");
      window.setTimeout(() => {
        figure.classList.add("kgi-figure--in");
        playCrtNoise();
      }, 260);
    });

    // タイプライター開始
    let stopType = null;
    window.setTimeout(() => {
      stopType = typeWriter(textEl, INTRO_TEXT, CHAR_DELAY_MS, playVoice, () => {
        actions.classList.add("kgi-actions--in");
        actions.removeAttribute("aria-hidden");
        startBtn.focus();
      });
    }, 760);

    // スキップは2.6秒後に出現
    window.setTimeout(() => {
      skipBtn.classList.add("kgi-skip--visible");
    }, SKIP_DELAY_MS);

    startBtn.addEventListener("click", () => finishIntro(overlay, true));
    skipBtn.addEventListener("click", () => {
      if (stopType) stopType();
      finishIntro(overlay, false);
    });
  }

  // ── エントリー ──────────────────────────────────────────────────────────
  const introDone = (() => {
    try { return !!localStorage.getItem(INTRO_DONE_KEY); } catch (_) { return true; }
  })();

  // guide.js（defer/後続）が参照するフラグ
  window.__kyoukaiIntroPending = !introDone;

  if (!introDone) {
    // オーディオコンテキストを最初のインタラクションで確立しておく
    document.addEventListener("touchstart", getAudioCtx, { once: true, passive: true });
    document.addEventListener("pointerdown", getAudioCtx, { once: true, passive: true });

    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", runIntro, { once: true });
    } else {
      runIntro();
    }
  }
})();
