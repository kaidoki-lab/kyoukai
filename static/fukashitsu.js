(function () {
  'use strict';

  const DOT = 3;
  const MAX_PRESSES = 10; // 各ボタンこれだけ押すと完成

  // localStorage キー
  const KEY_RED    = 'kyoukai_fuka_red';
  const KEY_BLUE   = 'kyoukai_fuka_blue';
  const KEY_YELLOW = 'kyoukai_fuka_yellow';
  const KEY_FISH   = 'kyoukai_has_fish';

  // 卵グリッド（新背景：4列×5行 = 20個）
  // 上部パネル占有分を除いた卵エリア y:12%〜78%
  const EGG_POSITIONS = [
    { id: 0,  x: 18, y: 16 }, { id: 1,  x: 38, y: 16 }, { id: 2,  x: 62, y: 16 }, { id: 3,  x: 82, y: 16 },
    { id: 4,  x: 18, y: 29 }, { id: 5,  x: 38, y: 29 }, { id: 6,  x: 62, y: 29 }, { id: 7,  x: 82, y: 29 },
    { id: 8,  x: 18, y: 42 }, { id: 9,  x: 38, y: 42 }, { id: 10, x: 62, y: 42 }, { id: 11, x: 82, y: 42 },
    { id: 12, x: 18, y: 56 }, { id: 13, x: 38, y: 56 }, { id: 14, x: 62, y: 56 }, { id: 15, x: 82, y: 56 },
    { id: 16, x: 18, y: 69 }, { id: 17, x: 38, y: 69 }, { id: 18, x: 62, y: 69 }, { id: 19, x: 82, y: 69 },
  ];

  // 卵を3色ゾーンに割り当て
  const ZONES = {
    red:    [0, 4, 8, 12, 16, 1],
    blue:   [5, 6, 9, 10, 13, 14],
    yellow: [2, 3, 7, 11, 15, 17, 18, 19],
  };

  // 各色のパレット（生物的・気持ち悪い系）
  const PALETTES = {
    red:    ['#6b0000', '#8b0000', '#aa1111', '#5a0000', '#cc1a00', '#3d0000'],
    blue:   ['#00006b', '#001a8b', '#0033aa', '#000050', '#0055cc', '#000033'],
    yellow: ['#5c4a00', '#7a6400', '#998000', '#3d3000', '#b89900', '#292000'],
  };

  // 高密度シェイプ（共通。press数で段階的に表示）
  const BASE_SHAPE = [
    // コア（中心部）
    [3,3],[3,4],[3,5],[3,6],[3,7],
    [4,2],[4,3],[4,4],[4,5],[4,6],[4,7],[4,8],
    [5,1],[5,2],[5,3],[5,4],[5,5],[5,6],[5,7],[5,8],[5,9],
    [6,1],[6,2],[6,3],[6,4],[6,5],[6,6],[6,7],[6,8],[6,9],
    [7,1],[7,2],[7,3],[7,4],[7,5],[7,6],[7,7],[7,8],[7,9],
    [8,2],[8,3],[8,4],[8,5],[8,6],[8,7],[8,8],
    [9,3],[9,4],[9,5],[9,6],[9,7],
    // 突起・触手
    [0,5],[1,4],[1,5],[1,6],[2,4],[2,5],[2,6],
    [4,0],[5,0],[6,0],[7,0],
    [4,10],[5,10],[6,10],[7,10],
    [10,4],[10,5],[10,6],[11,4],[11,5],[11,6],
    // 細部
    [2,3],[2,7],[8,1],[8,9],[3,2],[3,8],
    [1,3],[1,7],[0,4],[0,6],
    [9,2],[9,8],[10,3],[10,7],[11,3],[11,7],
  ];

  // press数に応じてシェイプのどこまで表示するか
  function getVisibleCells(pressCount) {
    if (pressCount <= 0) return [];
    const ratio = Math.min(pressCount / MAX_PRESSES, 1);
    const count = Math.ceil(BASE_SHAPE.length * ratio);
    return BASE_SHAPE.slice(0, count);
  }

  // --- 状態 ---
  function getCount(key)  { return parseInt(localStorage.getItem(key) || '0', 10); }
  function incCount(key)  { localStorage.setItem(key, getCount(key) + 1); }
  function hasFish()      { return localStorage.getItem(KEY_FISH) === '1'; }
  function setFish()      { localStorage.setItem(KEY_FISH, '1'); }

  function isComplete() {
    return getCount(KEY_RED) >= MAX_PRESSES
        && getCount(KEY_BLUE) >= MAX_PRESSES
        && getCount(KEY_YELLOW) >= MAX_PRESSES;
  }

  // --- DOM ---
  const frame      = document.querySelector('.fuka-frame');
  const canvas     = document.getElementById('fukaCanvas');
  const ctx        = canvas ? canvas.getContext('2d') : null;
  const messageEl  = document.getElementById('fukaMessage');
  const badge      = document.getElementById('fukaBadge');
  const collectBtn = document.getElementById('fukaCollectBtn');

  let msgTimer = null;

  function showMessage(text, duration) {
    if (!messageEl) return;
    clearTimeout(msgTimer);
    messageEl.textContent = text;
    messageEl.classList.add('is-visible');
    if (duration) msgTimer = setTimeout(() => messageEl.classList.remove('is-visible'), duration);
  }

  // --- Canvas ---
  function resizeCanvas() {
    if (!canvas || !frame) return;
    canvas.width  = frame.offsetWidth;
    canvas.height = frame.offsetHeight;
  }

  // --- ドット描画（丸・四角ミックス）---
  function drawDot(x, y, i, color) {
    if (!ctx) return;
    ctx.fillStyle = color;
    if (i % 2 === 0) {
      const r = (DOT - 1) / 2;
      ctx.beginPath();
      ctx.arc(x + r, y + r, r, 0, Math.PI * 2);
      ctx.fill();
    } else {
      ctx.fillRect(x, y, DOT - 1, DOT - 1);
    }
  }

  function drawLifeOnEgg(eggId, color, pressCount, palette, t) {
    const pos   = EGG_POSITIONS[eggId];
    const cells = getVisibleCells(pressCount);
    if (!pos || !cells.length || !ctx) return;

    const W  = canvas.width;
    const H  = canvas.height;
    const cx = (pos.x / 100) * W;
    const cy = (pos.y / 100) * H;

    const maxRow = Math.max(...BASE_SHAPE.map(([r]) => r));
    const maxCol = Math.max(...BASE_SHAPE.map(([, c]) => c));

    const breathX = Math.sin(t * 0.7 + eggId * 1.1) * 1.5;
    const breathY = Math.cos(t * 0.5 + eggId * 0.8) * 1.5;
    const ox = cx - ((maxCol + 1) * DOT) / 2 + breathX;
    const oy = cy - ((maxRow + 1) * DOT) / 2 + breathY;

    ctx.save();
    cells.forEach(([row, col], i) => {
      const flicker = 0.65 + Math.sin(t * 4.0 + i * 0.9 + eggId * 2.3) * 0.35;
      ctx.globalAlpha = Math.max(0.2, flicker);
      const c = palette[i % palette.length];
      drawDot(ox + col * DOT, oy + row * DOT, i, c);
    });
    ctx.restore();
  }

  // --- メインループ ---
  function drawAll(t) {
    if (!ctx || !canvas) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const red    = getCount(KEY_RED);
    const blue   = getCount(KEY_BLUE);
    const yellow = getCount(KEY_YELLOW);

    if (red === 0 && blue === 0 && yellow === 0) return;

    ZONES.red.forEach(id    => drawLifeOnEgg(id, 'red',    red,    PALETTES.red,    t));
    ZONES.blue.forEach(id   => drawLifeOnEgg(id, 'blue',   blue,   PALETTES.blue,   t));
    ZONES.yellow.forEach(id => drawLifeOnEgg(id, 'yellow', yellow, PALETTES.yellow, t));
  }

  function startLoop() {
    let t = 0;
    setInterval(() => {
      t += 0.06;
      drawAll(t);
    }, 80);
  }

  // --- ボタン処理 ---
  const BUTTON_CONFIG = [
    {
      key: KEY_RED, label: '栄養', color: 'red',
      x: 17, y: 88, w: 22, h: 14,
      messages: ['栄養を送った。','何かが増えている。','赤い何かが育っている。'],
    },
    {
      key: KEY_BLUE, label: '酸素', color: 'blue',
      x: 50, y: 88, w: 22, h: 14,
      messages: ['酸素を送った。','動きが出てきた。','青いものが広がっている。'],
    },
    {
      key: KEY_YELLOW, label: '温度', color: 'yellow',
      x: 83, y: 88, w: 22, h: 14,
      messages: ['温度を上げた。','温かくなっている。','黄色い膜が形成されている。'],
    },
  ];

  function onButtonPress(cfg) {
    if (hasFish()) { showMessage('すでに稚魚を取り出した。', 2000); return; }

    incCount(cfg.key);
    const count = getCount(cfg.key);
    const msgs  = cfg.messages;
    showMessage(msgs[Math.floor(Math.random() * msgs.length)], 2000);

    if (isComplete()) {
      setTimeout(() => {
        showMessage('生命が完成した。\n取り出すことができる。');
        if (collectBtn) collectBtn.classList.add('is-visible');
      }, 600);
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
    });
  }

  function onCollect() {
    setFish();
    if (collectBtn) collectBtn.classList.remove('is-visible');
    if (badge) badge.classList.add('is-visible');
    showMessage('稚魚を取り出した。\nどこかに連れて行ける気がする。');
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
        [KEY_RED, KEY_BLUE, KEY_YELLOW, KEY_FISH, 'kyoukai_fuka_state'].forEach(k => localStorage.removeItem(k));
        showMessage('リセットしました。', 1500);
        setTimeout(() => location.reload(), 1600);
        return;
      }
      tapTimer = setTimeout(() => { tapCount = 0; }, 3000);
    });
  }

  // --- 初期化 ---
  function init() {
    createButtons();
    setupHiddenReset();
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    if (collectBtn) collectBtn.addEventListener('click', onCollect);

    if (hasFish()) {
      if (badge) badge.classList.add('is-visible');
      showMessage('すでに稚魚を取り出した。', 3000);
    } else if (isComplete()) {
      showMessage('生命が完成した。\n取り出すことができる。');
      if (collectBtn) collectBtn.classList.add('is-visible');
    }

    startLoop();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
