'use strict';
(function () {

// ── 定数 ──────────────────────────────────────────────────────────────────
const LW = 390, LH = 844;          // 論理サイズ (9:16)
const CELL = 5, DOT = 4;           // セル=5px (ドット4px + 隙間1px)
const GR = 118;                    // 地面の行番号 (GR*CELL = 590px)

// ── Canvas ────────────────────────────────────────────────────────────────
const cv = document.getElementById('dotHanabiCanvas');
const ctx = cv.getContext('2d');
let SC = 1; // 表示スケール

function resize() {
  const ar = LW / LH;
  if (window.innerWidth / window.innerHeight < ar) {
    cv.width = window.innerWidth;
    cv.height = Math.round(window.innerWidth / ar);
  } else {
    cv.height = window.innerHeight;
    cv.width = Math.round(window.innerHeight * ar);
  }
  SC = cv.width / LW;
}
resize();
window.addEventListener('resize', () => { resize(); initTown(); });

// ドットを描画 (グリッド座標)
function dot(gx, gy, color, alpha) {
  if (alpha === undefined) alpha = 1;
  if (alpha <= 0.01) return;
  const px = Math.round(gx * CELL * SC);
  const py = Math.round(gy * CELL * SC);
  const sz = Math.max(1, Math.round(DOT * SC));
  if (px > cv.width || py > cv.height || px < -sz || py < -sz) return;
  ctx.globalAlpha = Math.min(1, alpha);
  ctx.fillStyle = color;
  ctx.fillRect(px, py, sz, sz);
  ctx.globalAlpha = 1;
}

// 16進カラーを暗く
function dimHex(hex, f) {
  if (!hex || !hex.startsWith('#') || hex.length < 7) return hex || '#000';
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return 'rgb(' + Math.round(r * f) + ',' + Math.round(g * f) + ',' + Math.round(b * f) + ')';
}

// ── 星 ───────────────────────────────────────────────────────────────────
const STARS = [];
for (let i = 0; i < 90; i++) {
  STARS.push({
    gx: Math.random() * 77,
    gy: 1 + Math.random() * 88,
    phase: Math.random() * Math.PI * 2,
    bright: 0.1 + Math.random() * 0.65
  });
}
function drawStars(t) {
  for (const s of STARS) {
    const a = s.bright * (0.5 + 0.5 * Math.sin(t * 0.0009 + s.phase));
    dot(s.gx, s.gy, '#ffffff', a);
  }
}

// ── 町 ───────────────────────────────────────────────────────────────────
let townDots = [];
let blastKilled = new Set();
let damageLevel = 0;

// 上からの割合に応じた破壊閾値 (0=不壊, 1-9=damageLevel以上で消去)
function calcDT(fracFromTop) {
  if (fracFromTop < 0.18) return 1;
  if (fracFromTop < 0.38) return 2;
  if (fracFromTop < 0.58) return 4;
  if (fracFromTop < 0.75) return 6;
  if (fracFromTop < 0.90) return 8;
  return 0;
}

// 矩形ビルを townDots に追加
function addRect(x, y, w, h, edgeC, opts) {
  opts = opts || {};
  const ic = opts.inner || dimHex(edgeC, 0.3);
  const wc = opts.win;
  const ws = opts.ws || 3, wh = opts.wh || 3;
  for (let dy = 0; dy < h; dy++) {
    const thresh = calcDT(dy / h);
    for (let dx = 0; dx < w; dx++) {
      const edge = dx === 0 || dx === w - 1 || dy === 0;
      let c = edge ? edgeC : ic;
      if (wc && !edge && (dx % ws) === 1 && ((dy + 1) % wh) === 0) c = wc;
      townDots.push({ gx: x + dx, gy: y + dy, color: c, dt: thresh });
    }
  }
}

// 枠のみ (看板フレーム)
function addFrame(x, y, w, h, c, thresh) {
  for (let dx = 0; dx <= w; dx++) {
    townDots.push({ gx: x + dx, gy: y, color: c, dt: thresh });
    townDots.push({ gx: x + dx, gy: y + h, color: c, dt: thresh });
  }
  for (let dy = 1; dy < h; dy++) {
    townDots.push({ gx: x, gy: y + dy, color: c, dt: thresh });
    townDots.push({ gx: x + w, gy: y + dy, color: c, dt: thresh });
  }
}

// 塔 (細い、クロスビーム付き)
function addTower(x, groundY, h) {
  for (let dy = 0; dy < h; dy++) {
    const frac = dy / h;
    const thresh = calcDT(frac);
    const w = frac < 0.55 ? 1 : frac < 0.8 ? 2 : 3;
    for (let dx = 0; dx < w; dx++) {
      townDots.push({ gx: x + dx, gy: groundY - h + dy, color: '#0088ff', dt: thresh });
    }
    if (dy % 8 === 4 && dy > 0 && dy < h - 3) {
      const span = Math.ceil(frac * 4) + 1;
      for (let bx = -span; bx < 0; bx++) {
        townDots.push({ gx: x + bx, gy: groundY - h + dy, color: '#44aaff', dt: thresh });
      }
      for (let bx = w; bx <= w + span; bx++) {
        townDots.push({ gx: x + bx, gy: groundY - h + dy, color: '#44aaff', dt: thresh });
      }
    }
  }
  // 頂部の赤ランプ
  townDots.push({ gx: x, gy: groundY - h, color: '#ff0000', dt: 1, blink: true });
}

// 三角屋根の神社
function addShrine(baseX, groundY) {
  const bh = 10, bw = 10;
  addRect(baseX, groundY - bh, bw, bh, '#ff8800', { win: '#ffff66', ws: 3, wh: 3 });
  addFrame(baseX + 1, groundY - 7, 5, 3, '#ffff00', 1);
  // 三角屋根
  for (let dy = 0; dy < 7; dy++) {
    const half = 6 - dy;
    const lx = baseX - 1 + (7 - half);
    const rx = baseX + bw - (7 - half);
    for (let gx = lx; gx <= rx; gx++) {
      const edge = gx === lx || gx === rx || dy === 0;
      townDots.push({ gx, gy: groundY - bh - 7 + dy, color: edge ? '#ffbb00' : dimHex('#ffbb00', 0.5), dt: 1 });
    }
  }
}

// 多層搭 (中華風)
function addPagoda(baseX, groundY) {
  const tiers = [
    { w: 2,  h: 4, c: '#ffee00', dt: 1 },
    { w: 5,  h: 3, c: '#00dd66', dt: 1 },
    { w: 8,  h: 3, c: '#00bb44', dt: 2 },
    { w: 10, h: 4, c: '#009933', dt: 3 },
    { w: 12, h: 5, c: '#007722', dt: 5 },
    { w: 14, h: 4, c: '#005511', dt: 0 },
  ];
  let y = groundY;
  for (let t = tiers.length - 1; t >= 0; t--) {
    const { w, h, c } = tiers[t];
    const thresh = tiers[t].dt;
    y -= h;
    const x = baseX + Math.floor((14 - w) / 2);
    for (let dy = 0; dy < h; dy++) {
      for (let dx = 0; dx < w; dx++) {
        const edge = dx === 0 || dx === w - 1 || dy === 0;
        townDots.push({ gx: x + dx, gy: y + dy, color: edge ? c : dimHex(c, 0.45), dt: thresh });
      }
    }
    if (t > 0 && t < tiers.length - 1) {
      townDots.push({ gx: x - 1, gy: y, color: c, dt: thresh });
      townDots.push({ gx: x + w, gy: y, color: c, dt: thresh });
    }
  }
}

// 観覧車
function addFerrisWheel(cx, cy, r) {
  const steps = Math.ceil(2 * Math.PI * r * 2.8);
  const seen = new Set();
  // リング
  for (let i = 0; i < steps; i++) {
    const a = (i / steps) * Math.PI * 2;
    const gx = Math.round(cx + r * Math.cos(a));
    const gy = Math.round(cy + r * Math.sin(a));
    const key = gx + ',' + gy;
    if (!seen.has(key)) {
      seen.add(key);
      townDots.push({ gx, gy, color: '#ff4400', dt: 4 });
    }
  }
  // スポーク (8本)
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * Math.PI * 2;
    for (let s = 1; s <= r; s++) {
      const f = s / r;
      const gx = Math.round(cx + r * f * Math.cos(a));
      const gy = Math.round(cy + r * f * Math.sin(a));
      const key = gx + ',' + gy;
      if (!seen.has(key)) {
        seen.add(key);
        townDots.push({ gx, gy, color: '#cc3300', dt: 3 });
      }
    }
  }
  // 中心
  for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) {
    townDots.push({ gx: cx + dx, gy: cy + dy, color: '#ffcc00', dt: 5 });
  }
  // ゴンドラ (8つ)
  const gondolaColors = ['#ffff00', '#00ffff', '#ff88ff', '#88ff88', '#ff8800', '#00aaff', '#ffffff', '#ff4488'];
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * Math.PI * 2;
    const gx = Math.round(cx + r * Math.cos(a));
    const gy = Math.round(cy + r * Math.sin(a));
    townDots.push({ gx, gy, color: gondolaColors[i], dt: 2 });
    townDots.push({ gx: gx + 1, gy: gy + 1, color: gondolaColors[i], dt: 2 });
  }
  // 支柱
  for (let dy = 0; dy <= 6; dy++) {
    townDots.push({ gx: cx - 1 - dy, gy: cy + r + dy, color: '#ff4400', dt: 2 });
    townDots.push({ gx: cx + 1 + dy, gy: cy + r + dy, color: '#ff4400', dt: 2 });
  }
  // 台座
  for (let dx = -3; dx <= 3; dx++) {
    townDots.push({ gx: cx + dx, gy: cy + r + 7, color: '#cc3300', dt: 0 });
  }
}

// 鳥居
function addTorii(x, groundY, w) {
  const h = 11;
  // 横桁 (2本)
  for (let dx = 0; dx < w; dx++) {
    townDots.push({ gx: x + dx, gy: groundY - h,     color: '#ff2200', dt: 1 });
    townDots.push({ gx: x + dx, gy: groundY - h + 2, color: '#dd1100', dt: 2 });
  }
  // 柱 (左右2本ずつ)
  for (let dy = 3; dy < h; dy++) {
    const frac = dy / h;
    const thresh = frac > 0.65 ? 0 : 2;
    townDots.push({ gx: x,         gy: groundY - h + dy, color: '#ff2200', dt: thresh });
    townDots.push({ gx: x + 1,     gy: groundY - h + dy, color: '#cc1100', dt: thresh });
    townDots.push({ gx: x + w - 2, gy: groundY - h + dy, color: '#ff2200', dt: thresh });
    townDots.push({ gx: x + w - 1, gy: groundY - h + dy, color: '#cc1100', dt: thresh });
  }
}

// 看板用テキストの代わりにドットパターンで最低限の文字表現
function addTextDots(x, y, label, c, thresh) {
  // 簡易ドットフォント: カタカナ/漢字1文字を3×5ドットで表現
  // ここでは判別可能な最低限のパターンだけ定義
  const patterns = {
    'P': [[1,1,1],[1,0,1],[1,1,1],[1,0,0],[1,0,0]],
    '薬': [[0,1,0],[1,1,1],[0,1,0],[1,1,1],[1,0,1]],
    '♨': [[1,0,1],[1,1,1],[0,1,0],[1,1,1],[0,1,0]],
    '寿': [[1,1,1],[0,1,0],[1,1,1],[0,1,0],[1,1,1]],
    '神': [[0,1,0],[1,1,1],[0,1,0],[0,1,1],[0,1,0]],
    '社': [[1,1,0],[0,1,1],[1,1,0],[0,0,1],[0,1,1]],
  };
  const pat = patterns[label];
  if (!pat) return;
  for (let dy = 0; dy < pat.length; dy++) {
    for (let dx = 0; dx < pat[dy].length; dx++) {
      if (pat[dy][dx]) townDots.push({ gx: x + dx, gy: y + dy, color: c, dt: thresh });
    }
  }
}

function initTown() {
  townDots = [];
  blastKilled = new Set();

  // 地面
  for (let gx = 0; gx < 78; gx++) {
    townDots.push({ gx, gy: GR,     color: '#443322', dt: 0 });
    townDots.push({ gx, gy: GR + 1, color: '#332211', dt: 0 });
  }

  // ── 左エリア ──────────────────────────────────────────────────────
  addShrine(0, GR);                                              // 神社A字屋根

  addRect(1, GR - 9, 5, 9, '#cc00cc', { win: '#ff88ff', ws: 2, wh: 3 }); // P駐車場
  addFrame(2, GR - 9, 3, 3, '#ff44ff', 1);
  addTextDots(3, GR - 8, 'P', '#ff88ff', 1);

  addRect(5, GR - 13, 5, 13, '#ff3377', { win: '#ff99bb', ws: 2, wh: 3 }); // ピンクビル
  addFrame(6, GR - 8, 3, 3, '#ff66aa', 1);

  addRect(8, GR - 8, 4, 8, '#7733ff', { win: '#bb88ff', ws: 2, wh: 3 });

  addRect(10, GR - 13, 8, 13, '#ff6600', { win: '#ffdd44', ws: 3, wh: 3 }); // 神社ビル
  addFrame(11, GR - 8, 5, 3, '#ffcc00', 1);
  addTextDots(12, GR - 7, '神', '#ffff00', 1);
  addTextDots(15, GR - 7, '社', '#ffff00', 1);

  addRect(13, GR - 10, 5, 10, '#00aacc', { win: '#88eeff', ws: 2, wh: 3 });

  // ── 中央左 ──────────────────────────────────────────────────────
  addRect(16, GR - 15, 6, 15, '#00bb99', { win: '#88ffee', ws: 3, wh: 3 });

  addRect(19, GR - 18, 4, 18, '#ff9900', { win: '#ffdd88', ws: 2, wh: 3 }); // 縦長ビル

  addRect(22, GR - 27, 8, 27, '#ffaa00', { win: '#ffff66', ws: 3, wh: 3, inner: dimHex('#ffaa00', 0.25) }); // ホテルA (最大)
  addFrame(23, GR - 18, 5, 6, '#ff8800', 2);

  addRect(29, GR - 20, 6, 20, '#0044ff', { win: '#88aaff', ws: 3, wh: 3 });
  addFrame(30, GR - 12, 4, 4, '#4488ff', 2);

  addRect(34, GR - 17, 7, 17, '#9900cc', { win: '#dd88ff', ws: 3, wh: 3 }); // カラオケ
  addFrame(35, GR - 12, 5, 5, '#ff00ff', 2);

  // ── 中央 (鑑賞のメインピース) ───────────────────────────────────
  addPagoda(36, GR);
  // 土台プラットフォーム
  for (let dx = 35; dx < 51; dx++) {
    townDots.push({ gx: dx, gy: GR - 4, color: '#003311', dt: 0 });
    townDots.push({ gx: dx, gy: GR - 3, color: '#002208', dt: 0 });
  }

  addTorii(49, GR, 11);

  addRect(50, GR - 14, 9, 14, '#ff5500', { win: '#ffcc44', ws: 3, wh: 3 }); // 温泉館
  addFrame(51, GR - 9, 6, 4, '#ff8800', 2);
  // ♨ ドット
  for (let dx = 0; dx < 3; dx++) {
    townDots.push({ gx: 53 + dx, gy: GR - 8, color: '#ffff00', dt: 1 });
    townDots.push({ gx: 53 + dx, gy: GR - 6, color: '#ffff00', dt: 1 });
  }
  townDots.push({ gx: 52, gy: GR - 7, color: '#ffff00', dt: 1 });
  townDots.push({ gx: 56, gy: GR - 7, color: '#ffff00', dt: 1 });

  // ── 中央右 ──────────────────────────────────────────────────────
  addTower(56, GR, 41);                                          // アンテナ塔 (最高)

  addRect(58, GR - 22, 8, 22, '#5500cc', { win: '#aa88ff', ws: 3, wh: 3 }); // ホテルB
  addFrame(59, GR - 16, 6, 7, '#8800ff', 3);

  addRect(61, GR - 17, 6, 17, '#0099cc', { win: '#44ddff', ws: 3, wh: 3 });

  addRect(63, GR - 14, 5, 14, '#884400', { win: '#ffbb44', ws: 2, wh: 3 });

  // ── 右エリア ──────────────────────────────────────────────────
  addFerrisWheel(70, GR - 15, 9);                               // 観覧車

  addRect(64, GR - 13, 7, 13, '#cc1100', { win: '#ff8866', ws: 3, wh: 3 }); // 赤ビル
  addFrame(65, GR - 8, 5, 3, '#ff4400', 2);
  addTextDots(66, GR - 7, '薬', '#ffff44', 1);

  addRect(71, GR - 10, 6, 10, '#aa5500', { win: '#ffaa44', ws: 2, wh: 3 });

  addRect(74, GR - 8, 4, 8, '#cc3300', {});

  // 追加小ビル (密度アップ)
  addRect(9, GR - 6, 3, 6, '#334455', {});
  addRect(15, GR - 7, 3, 7, '#446655', {});
  addRect(20, GR - 5, 3, 5, '#553300', {});
  addRect(27, GR - 9, 3, 9, '#003355', {});
  addRect(42, GR - 5, 5, 5, '#335500', {});
  addRect(44, GR - 9, 3, 9, '#224400', {});
  addRect(47, GR - 6, 3, 6, '#443300', {});
  addRect(56, GR - 7, 3, 7, '#002244', {});
  addRect(67, GR - 8, 4, 8, '#440022', {});
  addRect(77, GR - 6, 2, 6, '#332200', {});
}

initTown();

// ドットの可視判定
function isVisible(d) {
  if (blastKilled.has(Math.round(d.gx) + ',' + Math.round(d.gy))) return false;
  if (d.dt > 0 && damageLevel >= d.dt) return false;
  return true;
}

function drawTown() {
  for (const d of townDots) {
    if (!isVisible(d)) continue;
    dot(d.gx, d.gy, d.color);
  }
}

// ── 水面反射 ──────────────────────────────────────────────────────────────
function drawReflection(projectiles, particles) {
  const waterStart = GR + 3;
  const waterDepth = 38;

  // 町の反射
  for (const d of townDots) {
    if (!isVisible(d) || d.gy >= GR) continue;
    const ry = 2 * GR - d.gy + 3;
    const dist = ry - waterStart;
    if (dist < 0 || dist > waterDepth) continue;
    dot(d.gx, ry, d.color, (1 - dist / waterDepth) * 0.3);
  }

  // 花火・爆発パーティクルの反射
  for (const p of particles) {
    if (p.gy >= GR || p.isFlash) continue;
    const ry = 2 * GR - p.gy + 3;
    const dist = ry - waterStart;
    if (dist < 0 || dist > waterDepth) continue;
    dot(p.gx, ry, p.color, p.alpha * 0.22 * (1 - dist / waterDepth));
  }

  // 落下爆弾の反射
  for (const proj of projectiles) {
    if (proj.phase !== 'falling' || !proj.bombDots) continue;
    for (const bd of proj.bombDots) {
      const ry = 2 * GR - bd.gy + 3;
      const dist = ry - waterStart;
      if (dist < 0 || dist > waterDepth) continue;
      dot(bd.gx, ry, bd.color, 0.28 * (1 - dist / waterDepth));
    }
  }
}

// ── カメラ ────────────────────────────────────────────────────────────────
const cam = { scale: 1, phase: 'idle', timer: 0 };

function updateCam() {
  if (cam.phase === 'zoomOut') {
    cam.scale += (0.52 - cam.scale) * 0.065;
    cam.timer++;
    if (cam.timer > 55) { cam.phase = 'hold'; cam.timer = 0; }
  } else if (cam.phase === 'hold') {
    cam.timer++;
    if (cam.timer > 20) { cam.phase = 'zoomIn'; cam.timer = 0; }
  } else if (cam.phase === 'zoomIn') {
    cam.scale += (1 - cam.scale) * 0.07;
    if (Math.abs(cam.scale - 1) < 0.004) { cam.scale = 1; cam.phase = 'idle'; }
  }
}

function applyCamera() {
  if (Math.abs(cam.scale - 1) < 0.003) return;
  const ox = cv.width * 0.5;
  const oy = cv.height * 0.72;
  ctx.translate(ox, oy);
  ctx.scale(cam.scale, cam.scale);
  ctx.translate(-ox, -oy);
}

// ── 花火・爆弾 ─────────────────────────────────────────────────────────────
let projectiles = [];
let particles = [];
let shotCount = 0;
let bombCount = 0;
let firstBombCamUsed = false;

const FW_PALETTES = [
  ['#ff4444', '#ff8888'],
  ['#ff8800', '#ffcc44'],
  ['#ffff00', '#ffff99'],
  ['#44ff88', '#aaffdd'],
  ['#44ffff', '#aaffff'],
  ['#4488ff', '#88bbff'],
  ['#ff44ff', '#ffaaff'],
  ['#ffffff', '#ccccff'],
  ['#ff88cc', '#ffddee'],
  ['#ff6600', '#ffaa66'],
];

function launch() {
  const isBomb = shotCount >= 2 && Math.random() < 0.40;
  const gx = 7 + Math.random() * 64;
  const apexY = 10 + Math.random() * 52;
  const pal = FW_PALETTES[Math.floor(Math.random() * FW_PALETTES.length)];

  projectiles.push({
    gx,
    gy: GR - 2,
    apexY,
    isBomb,
    speed: 0.55 + Math.random() * 0.45,
    c1: pal[0], c2: pal[1],
    trail: [],
    phase: 'rising',
    pauseTimer: 0,
    bombDots: null,
  });
  shotCount++;
}

// 爆発 (放射状ドット)
function createBurst(gx, gy, c1, c2) {
  const numRays = 20 + Math.floor(Math.random() * 12);
  const radius = 9 + Math.random() * 7;
  for (let i = 0; i < numRays; i++) {
    const angle = (i / numRays) * Math.PI * 2 + (Math.random() - 0.5) * 0.25;
    const r = radius * (0.7 + Math.random() * 0.3);
    const steps = Math.ceil(r * 1.4);
    for (let s = 0; s < steps; s++) {
      const f = s / steps;
      let c;
      if (f < 0.2) c = '#ffffff';
      else if (f < 0.55) c = c1;
      else c = c2;
      particles.push({
        gx: gx + r * f * Math.cos(angle),
        gy: gy + r * f * Math.sin(angle),
        vx: r * 0.017 * Math.cos(angle),
        vy: r * 0.017 * Math.sin(angle),
        gravity: 0.012,
        color: c,
        alpha: 1,
        age: 0,
        maxAge: 55 + Math.random() * 45,
      });
    }
  }
}

// 爆弾シルエット (丸爆弾+導火線)
function createBombShape(cx, cy) {
  const dots = [];
  const r = 3;
  for (let dy = -r; dy <= r; dy++) {
    for (let dx = -r; dx <= r; dx++) {
      const dist2 = dx * dx + dy * dy;
      if (dist2 > r * r + 0.5) continue;
      const isEdge = dist2 >= (r - 0.9) * (r - 0.9);
      dots.push({ ox: dx, oy: dy, color: isEdge ? '#555555' : '#111111' });
    }
  }
  // 導火線
  dots.push({ ox: 1, oy: -r - 1, color: '#888888' });
  dots.push({ ox: 2, oy: -r - 2, color: '#888888' });
  dots.push({ ox: 3, oy: -r - 2, color: '#ffaa00' });  // 火花
  return dots;
}

// 着弾
function bombImpact(gx, gy) {
  // 爆破半径 (爆弾数が増えると広くなる)
  const blastR = 5 + Math.min(bombCount * 0.6, 8);
  for (const d of townDots) {
    const dist = Math.sqrt((d.gx - gx) * (d.gx - gx) + (d.gy - gy) * (d.gy - gy));
    if (dist <= blastR) {
      blastKilled.add(Math.round(d.gx) + ',' + Math.round(d.gy));
    }
  }
  // グローバル破壊レベル更新
  damageLevel = Math.min(9, Math.floor(damageLevel + 1));
  // 爆発パーティクル
  const debrisColors = ['#ff4400', '#ff8800', '#ffcc00', '#ff2200', '#ff6600', '#ffee00', '#cc3300'];
  for (let i = 0; i < 90; i++) {
    const angle = Math.random() * Math.PI * 2;
    const speed = 0.7 + Math.random() * 3.8;
    particles.push({
      gx, gy,
      vx: speed * Math.cos(angle),
      vy: speed * Math.sin(angle) - 1.8,
      gravity: 0.08,
      color: debrisColors[Math.floor(Math.random() * debrisColors.length)],
      alpha: 1, age: 0, maxAge: 40 + Math.random() * 50,
    });
  }
  // 衝撃波リング
  for (let i = 0; i < 20; i++) {
    const angle = (i / 20) * Math.PI * 2;
    particles.push({
      gx, gy, vx: 3 * Math.cos(angle), vy: 3 * Math.sin(angle),
      gravity: 0, color: '#ffffff',
      alpha: 1, age: 0, maxAge: 10,
    });
  }
  // フラッシュ
  particles.push({
    gx: gx - 12, gy: gy - 12,
    vx: 0, vy: 0, gravity: 0, color: '#ffffff',
    alpha: 1, age: 0, maxAge: 5,
    isFlash: true, fw: 24, fh: 24,
  });
  bombCount++;
}

// ── アップデート ────────────────────────────────────────────────────────────
function update() {
  updateCam();

  // 射体の更新
  for (let i = projectiles.length - 1; i >= 0; i--) {
    const p = projectiles[i];

    if (p.phase === 'rising') {
      p.gy -= p.speed;
      // 軌跡ドット (3フレームに1回)
      if (Math.round(p.gy * 4) % 3 === 0) {
        p.trail.push({ gx: p.gx, gy: p.gy, alpha: 1 });
      }
      for (let j = p.trail.length - 1; j >= 0; j--) {
        p.trail[j].alpha -= 0.09;
        if (p.trail[j].alpha <= 0) p.trail.splice(j, 1);
      }

      if (p.gy <= p.apexY) {
        p.gy = p.apexY;
        if (p.isBomb) {
          p.phase = 'pause';
          p.pauseTimer = 0;
          p.bombDots = createBombShape(p.gx, p.gy);
          // 初回爆弾カメラ演出
          if (!firstBombCamUsed) {
            firstBombCamUsed = true;
            cam.phase = 'zoomOut';
            cam.timer = 0;
          }
        } else {
          createBurst(p.gx, p.gy, p.c1, p.c2);
          projectiles.splice(i, 1);
        }
      }

    } else if (p.phase === 'pause') {
      p.pauseTimer++;
      if (p.pauseTimer > 28) {
        p.phase = 'falling';
        p.fallSpeed = 0.4;
      }

    } else if (p.phase === 'falling') {
      p.fallSpeed = Math.min(p.fallSpeed + 0.06, 3.5);
      p.gy += p.fallSpeed;
      if (p.bombDots) {
        for (const bd of p.bombDots) {
          bd.gx = p.gx + bd.ox;
          bd.gy = p.gy + bd.oy;
        }
      }
      if (p.gy >= GR - 3) {
        bombImpact(p.gx, GR - 1);
        projectiles.splice(i, 1);
        // カメラをズームインへ
        if (cam.phase === 'zoomOut' || cam.phase === 'hold') {
          cam.phase = 'zoomIn';
          cam.timer = 0;
        }
      }
    }
  }

  // パーティクル更新
  for (let i = particles.length - 1; i >= 0; i--) {
    const p = particles[i];
    p.gx += p.vx;
    p.gy += p.vy;
    p.vy += p.gravity;
    p.vx *= 0.97;
    p.age++;
    p.alpha = 1 - p.age / p.maxAge;
    if (p.age >= p.maxAge) particles.splice(i, 1);
  }
}

// ── 描画 ─────────────────────────────────────────────────────────────────
function draw(t) {
  ctx.clearRect(0, 0, cv.width, cv.height);
  ctx.save();
  applyCamera();

  // 星
  drawStars(t);

  // 町
  drawTown();

  // 水面反射
  drawReflection(projectiles, particles);

  // 軌跡
  for (const p of projectiles) {
    for (const tr of p.trail) {
      dot(tr.gx, tr.gy, p.c1, tr.alpha);
    }
    // 先端
    if (p.phase === 'rising') {
      dot(p.gx, p.gy, '#ffffff');
    } else if ((p.phase === 'pause' || p.phase === 'falling') && p.bombDots) {
      for (const bd of p.bombDots) {
        dot(bd.gx, bd.gy, bd.color);
      }
    }
  }

  // パーティクル
  for (const p of particles) {
    if (p.isFlash) {
      ctx.globalAlpha = p.alpha * 0.7;
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(
        Math.round(p.gx * CELL * SC), Math.round(p.gy * CELL * SC),
        Math.round(p.fw * CELL * SC), Math.round(p.fh * CELL * SC)
      );
      ctx.globalAlpha = 1;
    } else {
      dot(p.gx, p.gy, p.color, p.alpha);
    }
  }

  // アンテナ赤ランプ (点滅)
  if (Math.floor(t * 0.001) % 2 === 0) {
    dot(56, GR - 41, '#ff0000');
  }

  ctx.restore();

  // ヒントテキスト (最初の5秒)
  if (shotCount === 0 && t < 5000) {
    const alpha = t < 3000 ? 1 : 1 - (t - 3000) / 2000;
    ctx.globalAlpha = alpha * 0.65;
    ctx.fillStyle = '#ffffff';
    ctx.font = Math.round(11 * SC) + 'px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('タップで花火を打ち上げる', cv.width * 0.5, cv.height * 0.15);
    ctx.globalAlpha = 1;
  }
}

// ── メインループ ────────────────────────────────────────────────────────────
function loop(t) {
  if (cv.width === 0) resize(); // プレビュー環境で innerWidth=0 のときの自己修復
  update();
  draw(t);
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

// ── 入力 ─────────────────────────────────────────────────────────────────
function onTap(e) {
  e.preventDefault();
  launch();
}
cv.addEventListener('click', onTap);
cv.addEventListener('touchend', onTap, { passive: false });

})();
