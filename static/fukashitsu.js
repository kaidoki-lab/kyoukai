(function () {
  'use strict';

  const MAX_PRESSES = 10;

  const KEY_RED    = 'kyoukai_fuka_red';
  const KEY_BLUE   = 'kyoukai_fuka_blue';
  const KEY_YELLOW = 'kyoukai_fuka_yellow';
  const KEY_FISH   = 'kyoukai_has_fish';

  // --- 状態 ---
  function getCount(key) { return parseInt(localStorage.getItem(key) || '0', 10); }
  function incCount(key) { localStorage.setItem(key, getCount(key) + 1); }
  function hasEgg()      { return localStorage.getItem(KEY_FISH) === '1'; }
  function setEgg()      { localStorage.setItem(KEY_FISH, '1'); }

  function isComplete() {
    return getCount(KEY_RED) >= MAX_PRESSES
        && getCount(KEY_BLUE) >= MAX_PRESSES
        && getCount(KEY_YELLOW) >= MAX_PRESSES;
  }

  // --- DOM ---
  const frame      = document.querySelector('.fuka-frame');
  const bgEl       = document.querySelector('.fuka-bg');
  const collectBtn = document.getElementById('fukaCollectBtn');

  // --- 卵キャンバスとパーティクルエンジン ---
  const eggCanvas = document.createElement('canvas');
  eggCanvas.className = 'fuka-egg-canvas';
  frame.insertBefore(eggCanvas, frame.querySelector('.fuka-collect-btn'));

  function sizeEggCanvas() {
    const fw = frame.offsetWidth;
    const fh = frame.offsetHeight;
    eggCanvas.width  = Math.round(fw * 0.76);
    eggCanvas.height = Math.round(fh * 0.61);
  }
  sizeEggCanvas();

  function lerp(a, b, t) { return Math.round(a + (b - a) * t); }

  function getColors() {
    const rT = Math.min(getCount(KEY_RED)    / MAX_PRESSES, 1);
    const bT = Math.min(getCount(KEY_BLUE)   / MAX_PRESSES, 1);
    const yT = Math.min(getCount(KEY_YELLOW) / MAX_PRESSES, 1);
    return {
      r: [255,                   lerp(210, 55,  rT), lerp(210, 55,  rT)],
      b: [lerp(210, 55,  bT),   lerp(225, 148, bT), 255                ],
      y: [255,                   lerp(245, 220, yT), lerp(220, 30,  yT)],
    };
  }

  const engine = new ParticleObservationEngine(eggCanvas, {
    background:    'transparent',
    noAutoResize:  true,
    observerEffect: false,
    count:         160,
    getColors,
  });

  // collapsingフェーズをスキップ
  engine.onPhaseChange = function (phase) {
    if (phase === 'collapsing') this._advance();
  };

  // リサイズ時も卵サイズを維持
  window.addEventListener('resize', () => {
    sizeEggCanvas();
    engine._spawn();
  });

  engine.start();

  // --- ボタン処理 ---
  let actionBtns = [];

  const BUTTON_CONFIG = [
    { key: KEY_RED,    x: 22, y: 88, w: 22, h: 14, label: '栄養' },
    { key: KEY_BLUE,   x: 50, y: 88, w: 22, h: 14, label: '酸素' },
    { key: KEY_YELLOW, x: 78, y: 88, w: 22, h: 14, label: '温度' },
  ];

  function onButtonPress(cfg) {
    if (hasEgg()) return;
    incCount(cfg.key);
    if (isComplete()) {
      setTimeout(() => {
        if (collectBtn) collectBtn.classList.add('is-visible');
      }, 400);
    }
  }

  function createButtons() {
    BUTTON_CONFIG.forEach((cfg) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'fuka-action-btn';
      btn.style.left   = (cfg.x - cfg.w / 2) + '%';
      btn.style.top    = (cfg.y - cfg.h / 2) + '%';
      btn.style.width  = cfg.w + '%';
      btn.style.height = cfg.h + '%';
      btn.setAttribute('aria-label', cfg.label);
      btn.addEventListener('click', () => onButtonPress(cfg));
      frame.appendChild(btn);
      actionBtns.push(btn);
    });
  }

  function onCollect() {
    setEgg();
    if (collectBtn) collectBtn.classList.remove('is-visible');

    // パーティクル停止・フェードアウト
    engine.stop();
    eggCanvas.classList.add('is-hidden');
    actionBtns.forEach(b => b.classList.add('is-hidden'));

    // 背景を取り出し後の画像に切り替え
    if (bgEl) bgEl.classList.add('is-collected');
  }

  // --- 隠しリセット（上部パネルを7回タップ）---
  function setupHiddenReset() {
    let tapCount = 0;
    let tapTimer = null;
    const hitArea = document.createElement('div');
    hitArea.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:10%;z-index:999;';
    frame.appendChild(hitArea);
    hitArea.addEventListener('click', () => {
      tapCount++;
      clearTimeout(tapTimer);
      if (tapCount >= 7) {
        tapCount = 0;
        [KEY_RED, KEY_BLUE, KEY_YELLOW, KEY_FISH].forEach(k => localStorage.removeItem(k));
        setTimeout(() => location.reload(), 300);
        return;
      }
      tapTimer = setTimeout(() => { tapCount = 0; }, 3000);
    });
  }

  // --- 初期化 ---
  function init() {
    createButtons();
    setupHiddenReset();
    if (collectBtn) collectBtn.addEventListener('click', onCollect);

    if (hasEgg()) {
      engine.stop();
      eggCanvas.classList.add('is-hidden');
      actionBtns.forEach(b => b.classList.add('is-hidden'));
      if (bgEl) bgEl.classList.add('is-collected');
    } else if (isComplete()) {
      if (collectBtn) collectBtn.classList.add('is-visible');
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
