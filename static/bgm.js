/**
 * KYOUKAI BGM Engine
 * 各部屋のBGMをGenomeの状態に応じたエフェクトで変化させる共通エンジン
 *
 * 使い方（各テンプレートに追記）:
 *   <script>window.KYOUKAI_ROOM = 'home';</script>
 *   <script src="/static/bgm.js"></script>
 *
 * BGMファイルは /static/bgm/bgm_{room}.mp3 に置く
 * 対応部屋: home / observation / archive / exit / null
 */
(function () {
  'use strict';

  var ROOM      = (window.KYOUKAI_ROOM || 'home');
  var BGM_SRC   = '/static/bgm/bgm_' + ROOM + '.mp3';
  var POLL_MS   = 8000; // Genome取得間隔

  /* ── 状態 ─────────────────────────────── */
  var ctx         = null;
  var audioBuf    = null;
  var source      = null;
  var isPlaying   = false;
  var isMuted     = false;
  var pauseOffset = 0;
  var startedAt   = 0;
  var initialized = false;

  /* ── ノード (initAudio後に確定) ─────────── */
  var masterGain   = null;
  var lpFilter     = null;
  var hpFilter     = null;
  var waveshaper   = null;
  var reverbNode   = null;
  var dryGain      = null;
  var wetGain      = null;
  var tremoloGain  = null;
  var tremoloLFO   = null;
  var tremoloDepth = null;

  /* ── UI ───────────────────────────────── */
  var btn = null;

  /* ======================================================
   *  ユーティリティ
   * ==================================================== */
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

  /** インパルスレスポンスをプログラムで生成（外部ファイル不要のリバーブ） */
  function makeImpulse(duration, decay) {
    var rate = ctx.sampleRate;
    var len  = Math.floor(rate * duration);
    var buf  = ctx.createBuffer(2, len, rate);
    for (var c = 0; c < 2; c++) {
      var ch = buf.getChannelData(c);
      for (var i = 0; i < len; i++) {
        ch[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, decay);
      }
    }
    return buf;
  }

  /** ディストーション曲線 */
  function makeDistCurve(amount) {
    var n    = 256;
    var out  = new Float32Array(n);
    var a    = Math.max(0, amount);
    for (var i = 0; i < n; i++) {
      var x  = (i * 2) / n - 1;
      out[i] = (Math.PI + a) * x / (Math.PI + a * Math.abs(x));
    }
    return out;
  }

  /* ======================================================
   *  AudioContextとノードグラフの初期化
   * ==================================================== */
  function initAudio() {
    if (initialized) return;
    initialized = true;

    ctx = new (window.AudioContext || window.webkitAudioContext)();

    /* マスターゲイン */
    masterGain = ctx.createGain();
    masterGain.gain.value = 0.72;

    /* ローパスフィルター（こもり・深度） */
    lpFilter = ctx.createBiquadFilter();
    lpFilter.type = 'lowpass';
    lpFilter.frequency.value = 18000;
    lpFilter.Q.value = 0.8;

    /* ハイパスフィルター（攻撃性・鋭さ） */
    hpFilter = ctx.createBiquadFilter();
    hpFilter.type = 'highpass';
    hpFilter.frequency.value = 30;
    hpFilter.Q.value = 0.5;

    /* ディストーション（腐食・暴力性） */
    waveshaper = ctx.createWaveShaper();
    waveshaper.curve = makeDistCurve(0);
    waveshaper.oversample = '2x';

    /* リバーブ（柔らかさ・残響） */
    reverbNode = ctx.createConvolver();
    reverbNode.buffer = makeImpulse(2.8, 2.2);

    /* ドライ / ウェット（リバーブ量制御） */
    dryGain = ctx.createGain();
    dryGain.gain.value = 1.0;
    wetGain = ctx.createGain();
    wetGain.gain.value = 0.0;

    /* トレモロ（視線・揺れ） */
    tremoloGain  = ctx.createGain();
    tremoloGain.gain.value = 1.0;
    tremoloLFO   = ctx.createOscillator();
    tremoloLFO.type = 'sine';
    tremoloLFO.frequency.value = 1.2;
    tremoloDepth = ctx.createGain();
    tremoloDepth.gain.value = 0.0; // 初期: tremolo無効

    tremoloLFO.connect(tremoloDepth);
    tremoloDepth.connect(tremoloGain.gain);
    tremoloLFO.start();

    /*
     * シグナルチェーン:
     * [source]
     *   → lpFilter → hpFilter → waveshaper → tremoloGain
     *     → dryGain  ─────────────────────────── masterGain → destination
     *     → reverbNode → wetGain ─────────────── masterGain → destination
     */
    dryGain.connect(masterGain);
    wetGain.connect(masterGain);
    reverbNode.connect(wetGain);
    masterGain.connect(ctx.destination);
  }

  /** 新しいsourceノードをグラフに接続 */
  function connectSource(src) {
    src.connect(lpFilter);
    lpFilter.connect(hpFilter);
    hpFilter.connect(waveshaper);
    waveshaper.connect(tremoloGain);
    tremoloGain.connect(dryGain);
    tremoloGain.connect(reverbNode);
    src.loop = true;
  }

  /* ======================================================
   *  BGMファイルの読み込み
   * ==================================================== */
  function loadBuffer() {
    return fetch(BGM_SRC)
      .then(function (res) {
        if (!res.ok) return Promise.reject('not found');
        return res.arrayBuffer();
      })
      .then(function (ab) {
        return ctx.decodeAudioData(ab);
      })
      .then(function (buf) {
        audioBuf = buf;
        return true;
      })
      .catch(function () {
        return false;
      });
  }

  /* ======================================================
   *  再生 / 停止
   * ==================================================== */
  function play() {
    if (!initialized) initAudio();
    var resume = ctx.state === 'suspended' ? ctx.resume() : Promise.resolve();
    return resume.then(function () {
      if (isPlaying) return;
      var doPlay = function () {
        var offset = audioBuf ? pauseOffset % audioBuf.duration : 0;
        source = ctx.createBufferSource();
        source.buffer = audioBuf;
        connectSource(source);
        source.start(0, offset);
        startedAt = ctx.currentTime - offset;
        isPlaying = true;
        updateUI();
      };
      if (audioBuf) {
        doPlay();
        return;
      }
      loadBuffer().then(function (ok) {
        if (ok) doPlay();
      });
    });
  }

  function pause() {
    if (!isPlaying || !source) return;
    pauseOffset = ctx.currentTime - startedAt;
    source.stop();
    source.disconnect();
    source = null;
    isPlaying = false;
    updateUI();
  }

  /* ======================================================
   *  Genome状態 → エフェクト反映
   * ==================================================== */
  function applyEffects(g) {
    if (!initialized || !ctx) return;

    var T    = ctx.currentTime;
    var RAMP = 3.0; // 3秒スムーズ遷移

    var phase  = clamp(Number(g.phase)              || 0, 0, 3);
    var soft   = clamp(Number(g.trait_softness)     || 0, 0, 1);
    var aggr   = clamp(Number(g.trait_aggression)   || 0, 0, 1);
    var corr   = clamp(Number(g.trait_corruption)   || 0, 0, 1);
    var gaze   = clamp(Number(g.trait_gaze)         || 0, 0, 1);
    var dist   = clamp(Number(g.trait_distance)     || 0, 0, 1);
    var instab = clamp(Number(g.audio_instability)  || 0, 0, 1);
    var drift  = clamp(Number(g.phase_drift)        || 0, 0, 1);

    /* ── ローパス: phase↑ / distance↑ でこもる ─── */
    var lpFreq = clamp(18000 - phase * 2400 - dist * 5000 + aggr * 1400, 250, 20000);
    lpFilter.frequency.exponentialRampToValueAtTime(lpFreq, T + RAMP);

    /* ── ハイパス: aggression↑ で鋭くなる ──────── */
    var hpFreq = clamp(30 + aggr * 280, 20, 900);
    hpFilter.frequency.exponentialRampToValueAtTime(hpFreq, T + RAMP);

    /* ── ディストーション: corruption + aggression ─ */
    waveshaper.curve = makeDistCurve(corr * 110 + aggr * 55);

    /* ── リバーブ量: softness + phase ──────────── */
    var wet = clamp(soft * 0.38 + phase * 0.07, 0, 0.72);
    var dry = clamp(1.0 - wet * 0.55, 0.3, 1.0);
    wetGain.gain.linearRampToValueAtTime(wet, T + RAMP);
    dryGain.gain.linearRampToValueAtTime(dry, T + RAMP);

    /* ── トレモロ: gaze（視線の揺れ） ──────────── */
    tremoloLFO.frequency.linearRampToValueAtTime(
      clamp(0.6 + gaze * 4.5, 0.1, 8), T + RAMP
    );
    tremoloDepth.gain.linearRampToValueAtTime(gaze * 0.22, T + RAMP);

    /* ── デチューン: instability + drift ────────── */
    if (source) {
      var sign   = Math.random() < 0.5 ? 1 : -1;
      var cents  = sign * (instab * 55 + drift * 28);
      source.detune.linearRampToValueAtTime(cents, T + RAMP);
    }

    /* ── グリッチ: 瞬間的な音量ブリップ ────────── */
    if (instab > 0.38 && Math.random() < (instab - 0.38) * 0.18) {
      var vol = masterGain.gain.value;
      masterGain.gain.setValueAtTime(vol * (Math.random() * 0.25 + 0.05), T);
      masterGain.gain.linearRampToValueAtTime(vol, T + 0.13);
    }
  }

  /* ======================================================
   *  Genomeポーリング
   * ==================================================== */
  function pollGenome() {
    fetch('/api/genome', { cache: 'no-store' })
      .then(function (r) { return r.json(); })
      .then(applyEffects)
      .catch(function () {});
  }

  /* ======================================================
   *  UIボタン（右下固定・最小限デザイン）
   * ==================================================== */
  function createButton() {
    var b = document.createElement('button');
    b.id = 'kyoukai-bgm-btn';
    b.setAttribute('aria-label', 'BGM');
    b.setAttribute('type', 'button');
    b.style.cssText = [
      'position:fixed',
      'bottom:14px',
      'right:14px',
      'z-index:9998',
      'background:rgba(0,0,0,0.62)',
      'color:#5ecfad',
      'border:1px solid rgba(94,207,173,0.22)',
      'border-radius:2px',
      'font-family:monospace',
      'font-size:10px',
      'letter-spacing:0.1em',
      'padding:4px 9px',
      'cursor:pointer',
      'opacity:0.38',
      'transition:opacity 0.2s, color 0.2s',
      'pointer-events:auto'
    ].join(';');
    b.addEventListener('mouseenter', function () { b.style.opacity = '0.88'; });
    b.addEventListener('mouseleave', function () {
      b.style.opacity = (isPlaying && !isMuted) ? '0.48' : '0.28';
    });
    b.addEventListener('click', onBtnClick);
    document.body.appendChild(b);
    return b;
  }

  function updateUI() {
    if (!btn) return;
    if (isPlaying && !isMuted) {
      btn.textContent = '音 ▮▮';
      btn.style.color = '#7fffd4';
      btn.style.opacity = '0.48';
    } else {
      btn.textContent = '音 ▶';
      btn.style.color = '#4a9a7a';
      btn.style.opacity = '0.28';
    }
  }

  function onBtnClick() {
    if (!initialized) initAudio();
    if (!isPlaying) {
      isMuted = false;
      play();
    } else {
      isMuted = !isMuted;
      var target = isMuted ? 0 : 0.72;
      masterGain.gain.linearRampToValueAtTime(target, ctx.currentTime + 0.55);
      updateUI();
    }
  }

  /* ======================================================
   *  ブート
   * ==================================================== */
  function boot() {
    btn = createButton();
    updateUI();

    /* 最初のユーザーインタラクションで自動再生（ブラウザポリシー対策） */
    function onFirst() {
      document.removeEventListener('click',   onFirst);
      document.removeEventListener('keydown', onFirst);
      document.removeEventListener('touchstart', onFirst);
      if (!isPlaying) play();
    }
    document.addEventListener('click',      onFirst, { once: true });
    document.addEventListener('keydown',    onFirst, { once: true });
    document.addEventListener('touchstart', onFirst, { once: true });

    /* Genomeポーリング開始 */
    pollGenome();
    setInterval(pollGenome, POLL_MS);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
