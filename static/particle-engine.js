// particle-engine.js
// 粒子生成構造体観測システム — コアエンジン (最適化版)
// PHASE1-7 | KYOUKAI Edition

(function (global) {
  'use strict';

  const TWO_PI = Math.PI * 2;

  // ══════════════════════════════════════════════════════════
  //  空間グリッド — nearby() は出力バッファを受け取る (GCゼロ)
  // ══════════════════════════════════════════════════════════

  class SpatialGrid {
    constructor(cs) {
      this.cs   = cs;
      this.data = new Map();
    }
    clear() { this.data.clear(); }
    _k(x, y) {
      return (Math.floor(x / this.cs) * 73856093) ^ (Math.floor(y / this.cs) * 19349663);
    }
    insert(p) {
      const k = this._k(p.x, p.y);
      let c = this.data.get(k);
      if (!c) this.data.set(k, c = []);
      c.push(p);
    }
    // out: 呼び出し元が渡す再利用バッファ
    nearby(x, y, r, out) {
      out.length = 0;
      const cs = this.cs;
      const cx = Math.floor(x / cs), cy = Math.floor(y / cs);
      const rc = Math.ceil(r / cs);
      for (let dx = -rc; dx <= rc; dx++) {
        for (let dy = -rc; dy <= rc; dy++) {
          const c = this.data.get((cx + dx) * 73856093 ^ (cy + dy) * 19349663);
          if (c) for (let i = 0; i < c.length; i++) out.push(c[i]);
        }
      }
    }
  }

  // ══════════════════════════════════════════════════════════
  //  定数
  // ══════════════════════════════════════════════════════════

  const PHASES = ['forming', 'structured', 'stable', 'collapsing', 'reforming'];

  const DUR = {
    forming:    [18, 26],
    structured: [12, 20],
    stable:     [10, 16],
    collapsing: [7,  12],
    reforming:  [15, 24],
  };

  const BASE_PARAMS = {
    attDist:  80,
    repDist:  22,
    attF:   0.010,
    repF:   0.075,
    maxSpd:   1.5,
    conDist: 120,
  };

  // サイクルごとに回転するフラクタルアトラクタ生成器
  function makeFractalTarget(angle) {
    const cos  = Math.cos(angle),                sin  = Math.sin(angle);
    const cos2 = Math.cos(angle + Math.PI / 3),  sin2 = Math.sin(angle + Math.PI / 3);
    function rot(c, s, x, y) {
      const dx = x - 0.5, dy = y - 0.5;
      return [0.5 + dx * c - dy * s, 0.5 + dx * s + dy * c];
    }
    const r0 = rot(cos, sin, 0.50, 0.08), r1 = rot(cos, sin, 0.06, 0.92), r2 = rot(cos, sin, 0.94, 0.92);
    const rvx = [r0[0], r1[0], r2[0]], rvy = [r0[1], r1[1], r2[1]];
    const b0 = rot(cos2, sin2, 0.50, 0.08), b1 = rot(cos2, sin2, 0.06, 0.92), b2 = rot(cos2, sin2, 0.94, 0.92);
    const bvx = [b0[0], b1[0], b2[0]], bvy = [b0[1], b1[1], b2[1]];
    return function (id, type) {
      const vx = type === 'b' ? bvx : rvx, vy = type === 'b' ? bvy : rvy;
      let x = 0.5, y = 0.5, seed = (id + 1) * 2654435761;
      for (let i = 0; i < 12; i++) {
        seed = (seed * 1664525 + 1013904223) >>> 0;
        const v = seed % 3;
        x = (x + vx[v]) * 0.5; y = (y + vy[v]) * 0.5;
      }
      return [x, y];
    };
  }

  // ══════════════════════════════════════════════════════════
  //  エンジン
  // ══════════════════════════════════════════════════════════

  class ParticleObservationEngine {
    constructor(canvas, opts) {
      opts = opts || {};
      this.cv   = canvas;
      this.ctx  = canvas.getContext('2d');
      this.opts = opts;

      const mob = (window.innerWidth < 768) || /Mobi|Android/i.test(navigator.userAgent);
      this.N    = opts.count != null ? opts.count : (mob ? 500 : 1800);
      this.par  = Object.assign({}, BASE_PARAMS, opts.params);
      this.pts  = [];

      // グリッドはattDist基準のセルサイズ (physicsで使う方が多いため小さく)
      this.gridPhy = new SpatialGrid(this.par.attDist + 10);
      this.gridCon = new SpatialGrid(this.par.conDist + 10);

      // フェーズ
      this.pi     = 0;
      this.phase  = PHASES[0];
      this.pTimer = 0;
      this.pDur   = this._dur();
      this.cycle  = 0;
      this.stOver = 0;

      // 形成中心
      this.fcx = 0.5;
      this.fcy = 0.5;

      // フラクタルアトラクタ
      this._fractalAngle = 0;
      this._fractalFn    = makeFractalTarget(0);

      // 観測者
      this.mx  = -1;
      this.my  = -1;
      this.obt = 0;

      // アニメーション
      this.animId   = null;
      this.lastTs   = 0;
      this.fps      = 60;
      this._fb      = [];

      // クリック散開
      this._clicks  = [];

      // 接続線 2フレームに1回更新
      this._conTick  = 0;
      this._conLines = { rrN: [], rrF: [], bbN: [], bbF: [], yyA: [], xxA: [] };

      // GCゼロ: 近傍バッファ再利用
      this._nbuf = [];

      // イベントハンドラ
      this._rz = () => this._resize();
      this._mm = e => {
        const r = canvas.getBoundingClientRect();
        this.mx = e.clientX - r.left;
        this.my = e.clientY - r.top;
      };
      this._tm = e => {
        if (e.touches[0]) {
          const r = canvas.getBoundingClientRect();
          this.mx = e.touches[0].clientX - r.left;
          this.my = e.touches[0].clientY - r.top;
        }
      };
      this._pd = e => {
        const r = canvas.getBoundingClientRect();
        this._clicks.push({ x: e.clientX - r.left, y: e.clientY - r.top, t: performance.now() });
      };

      if (!opts.noAutoResize) window.addEventListener('resize', this._rz);
      canvas.addEventListener('pointerdown', this._pd);
      if (opts.observerEffect !== false) {
        canvas.addEventListener('mousemove', this._mm);
        canvas.addEventListener('touchmove', this._tm, { passive: true });
      }

      this._resize();
      this._spawn();
    }

    // ── 初期化 ─────────────────────────────────────────────

    _resize() {
      if (this.opts.noAutoResize) return;
      this.cv.width  = window.innerWidth;
      this.cv.height = window.innerHeight;
    }

    _rnd(a, b) { return a + Math.random() * (b - a); }

    _dur() {
      const d = DUR[PHASES[this.pi]];
      return this._rnd(d[0], d[1]);
    }

    _spawn() {
      const w = this.cv.width, h = this.cv.height;
      const cx = w * this.fcx, cy = h * this.fcy;
      const spread = Math.min(w, h) * 0.38;
      const n = this.N;

      // 赤40% 青40% 黄20%
      const types = new Uint8Array(n);   // 0=r 1=b 2=y
      for (let i = 0; i < n; i++) {
        const f = i / n;
        types[i] = f < 0.4 ? 0 : f < 0.8 ? 1 : 2;
      }
      for (let i = n - 1; i > 0; i--) {
        const j = (Math.random() * (i + 1)) | 0;
        const tmp = types[i]; types[i] = types[j]; types[j] = tmp;
      }

      this.pts = Array.from({ length: n }, (_, id) => {
        const t = ['r', 'b', 'y'][types[id]];
        return {
          id,
          t,
          x:  cx + this._rnd(-spread, spread),
          y:  cy + this._rnd(-spread, spread),
          vx: this._rnd(-0.5, 0.5),
          vy: this._rnd(-0.5, 0.5),
          sz: t === 'r' ? this._rnd(2.0, 3.4) :
              t === 'b' ? this._rnd(1.4, 2.6) :
                          this._rnd(1.6, 2.8),
        };
      });
    }

    // ── フェーズ ────────────────────────────────────────────

    _advance() {
      this.pi    = (this.pi + 1) % PHASES.length;
      this.phase = PHASES[this.pi];
      this.pTimer = 0;
      this.pDur  = this._dur();

      if (this.phase === 'reforming') {
        this.fcx = this._rnd(0.2, 0.8);
        this.fcy = this._rnd(0.2, 0.8);
      }
      if (this.phase === 'forming') {
        this.cycle++;
        this._evolve();
      }
      if (typeof this.onPhaseChange === 'function') this.onPhaseChange(this.phase);
    }

    _evolve() {
      const nudge = (v, lo, hi) =>
        Math.max(lo, Math.min(hi, v + (Math.random() - 0.5) * 0.16 * (hi - lo)));
      const p = this.par;
      p.attDist  = nudge(p.attDist,   45, 140);
      p.repDist  = nudge(p.repDist,   12,  50);
      p.attF     = nudge(p.attF,   0.003, 0.022);
      p.repF     = nudge(p.repF,   0.020, 0.150);
      p.maxSpd   = nudge(p.maxSpd,  0.5,  3.2);
      p.conDist  = nudge(p.conDist,  60,  210);
      // グリッド再生成
      this.gridPhy = new SpatialGrid(p.attDist + 10);
      this.gridCon = new SpatialGrid(p.conDist + 10);
      // フラクタル回転（サイクルごとに別の向きになる）
      this._fractalAngle += this._rnd(0.25, 0.85);
      this._fractalFn = makeFractalTarget(this._fractalAngle);
    }

    // ── 物理 ───────────────────────────────────────────────

    _physics(dt) {
      const pts   = this.pts;
      const par   = this.par;
      const grid  = this.gridPhy;
      const nbuf  = this._nbuf;
      const phase = this.phase;
      const w     = this.cv.width, h = this.cv.height;
      const tcx   = w * this.fcx, tcy = h * this.fcy;
      const n     = pts.length;

      grid.clear();
      for (let i = 0; i < n; i++) grid.insert(pts[i]);

      const attrMul  = phase === 'collapsing' ? 0.02 : phase === 'reforming' ? 0.45 : 1.0;
      const hasBurst = this._clicks.length > 0;

      const repDist  = par.repDist,  repDist2  = repDist  * repDist;
      const attDist  = par.attDist,  attDist2  = attDist  * attDist;
      const repF     = par.repF;
      const attF     = par.attF;
      const maxSpd   = par.maxSpd;

      for (let ai = 0; ai < n; ai++) {
        const a = pts[ai];
        let fx = 0, fy = 0;

        grid.nearby(a.x, a.y, attDist, nbuf);
        const nb = nbuf.length;

        const mass = a.t === 'r' ? 3.0 : a.t === 'b' ? 1.0 : 1.5;

        for (let ni = 0; ni < nb; ni++) {
          const b = nbuf[ni];
          if (b === a) continue;
          const dx = b.x - a.x, dy = b.y - a.y;
          const d2 = dx * dx + dy * dy;
          if (d2 < 0.01 || d2 > attDist2) continue;
          const d = Math.sqrt(d2);

          if (d2 < repDist2) {
            const f = (repF * (1 - d / repDist)) / mass;
            fx -= (dx / d) * f;
            fy -= (dy / d) * f;
          } else if (attrMul > 0) {
            let f = (attF * (1 - d / attDist) * attrMul) / mass;
            if (a.t === 'r') f *= 1.6;
            if (a.t === 'b') {
              fx += (-dy / d) * f * 0.28;
              fy += ( dx / d) * f * 0.28;
            }
            fx += (dx / d) * f;
            fy += (dy / d) * f;
          }
        }

        // フェーズ固有
        if (phase === 'forming' || phase === 'reforming') {
          const str = phase === 'reforming' ? 0.0010 : 0.0004;
          fx += (tcx - a.x) * str;
          fy += (tcy - a.y) * str;
        }

        // フラクタル引力 — 粒子ごとのシェルピンスキー目標位置へ引き寄せる
        // 形成中心(fcx, fcy)を基準に配置するため、リフォーム後も追従する
        if (phase === 'forming' || phase === 'structured' || phase === 'stable') {
          const progress = Math.min(1, this.pTimer / Math.max(1, this.pDur * 0.55));
          const pulse    = 0.75 + Math.sin(this.pTimer * 1.4 + a.id * 0.011) * 0.25;
          const fractalStr =
            phase === 'stable'     ? 0.0065 :
            phase === 'structured' ? 0.0030 :
                                     0.0006 * progress;

          // フラクタル位置を動的計算（サイクルごとに角度が変わる）
          const [ftx, fty] = this._fractalFn(a.id, a.t);

          // 画面内に収まる範囲でフラクタルをスケール・センタリング
          const fscale = Math.min(w, h) * 0.62;
          const tx = w * this.fcx + (ftx - 0.5) * fscale;
          const ty = h * this.fcy + (fty - 0.5) * fscale;

          fx += (tx - a.x) * fractalStr * pulse;
          fy += (ty - a.y) * fractalStr * pulse;
        }

        if (phase === 'collapsing') {
          const rand = a.t === 'y' ? 2.8 : a.t === 'b' ? 1.0 : 0.30;
          fx += (Math.random() - 0.5) * rand;
          fy += (Math.random() - 0.5) * rand;
          const ox = a.x - tcx, oy = a.y - tcy;
          const od = Math.sqrt(ox * ox + oy * oy) || 1;
          fx += (ox / od) * 0.12;
          fy += (oy / od) * 0.12;
        }

        if ((phase === 'stable' || phase === 'structured') && a.t === 'y' && Math.random() < 0.012) {
          fx += (Math.random() - 0.5) * 1.4;
          fy += (Math.random() - 0.5) * 1.4;
        }

        if (phase === 'stable' && a.t === 'y') {
          const excess = Math.max(0, this.stOver - 4);
          if (excess > 0 && Math.random() < 0.006 * excess) {
            fx += (Math.random() - 0.5) * (2.5 + excess * 0.5);
            fy += (Math.random() - 0.5) * (2.5 + excess * 0.5);
          }
        }

        // PHASE6: 黄→追従 / 赤青→反発
        if (this.opts.observerEffect !== false && this.mx >= 0) {
          const ox = a.x - this.mx, oy = a.y - this.my;
          const od = Math.sqrt(ox * ox + oy * oy) || 1;
          const reach = 110 + this.obt * 0.18;
          if (od < reach) {
            const str = (1 - od / reach) * (0.55 + this.obt * 0.005);
            if (a.t === 'y') {
              fx -= (ox / od) * str * 1.8;
              fy -= (oy / od) * str * 1.8;
            } else {
              fx += (ox / od) * str;
              fy += (oy / od) * str;
            }
          }
        }

        // クリック散開
        for (let ci = 0; ci < this._clicks.length; ci++) {
          const ck = this._clicks[ci];
          const ox = a.x - ck.x, oy = a.y - ck.y;
          const od = Math.sqrt(ox * ox + oy * oy) || 1;
          if (od < 240) {
            const sf = (1 - od / 240) * 12;
            fx += (ox / od) * sf;
            fy += (oy / od) * sf;
          }
        }

        // 積分
        const damp = a.t === 'r' ? 0.92 : a.t === 'b' ? 0.97 : 0.985;
        a.vx = (a.vx + fx * dt) * damp;
        a.vy = (a.vy + fy * dt) * damp;

        const spd = Math.sqrt(a.vx * a.vx + a.vy * a.vy);
        const cap = hasBurst ? maxSpd * 5 : phase === 'collapsing' ? maxSpd * 2.8 : maxSpd;
        if (spd > cap) { a.vx = (a.vx / spd) * cap; a.vy = (a.vy / spd) * cap; }

        a.x += a.vx;
        a.y += a.vy;

        const mg = 18;
        if (a.x < mg)     { a.x = mg;     a.vx =  Math.abs(a.vx) * 0.7; }
        if (a.x > w - mg) { a.x = w - mg; a.vx = -Math.abs(a.vx) * 0.7; }
        if (a.y < mg)     { a.y = mg;     a.vy =  Math.abs(a.vy) * 0.7; }
        if (a.y > h - mg) { a.y = h - mg; a.vy = -Math.abs(a.vy) * 0.7; }
      }
    }

    // ── 接続線収集 (2フレームに1回) ─────────────────────────

    _collectConnections() {
      const pts   = this.pts;
      const par   = this.par;
      const grid  = this.gridCon;
      const nbuf  = this._nbuf;
      const phase = this.phase;
      const n     = pts.length;
      const cl    = this._conLines;

      // 接続用グリッド構築
      grid.clear();
      for (let i = 0; i < n; i++) grid.insert(pts[i]);

      // バケット初期化
      cl.rrN.length = 0; cl.rrF.length = 0;
      cl.bbN.length = 0; cl.bbF.length = 0;
      cl.yyA.length = 0; cl.xxA.length = 0;

      const conDist  = par.conDist;
      const cd2      = conDist * conDist;
      const half2    = cd2 * 0.25;
      const step     = this.fps < 25 ? 4 : this.fps < 38 ? 2 : 1;

      for (let i = 0; i < n; i += step) {
        const a = pts[i];
        grid.nearby(a.x, a.y, conDist, nbuf);
        const nb = nbuf.length;

        for (let ni = 0; ni < nb; ni++) {
          const b = nbuf[ni];
          if (b.id <= a.id) continue;
          const dx = b.x - a.x, dy = b.y - a.y;
          const d2 = dx * dx + dy * dy;
          if (d2 > cd2) continue;

          const near = d2 < half2;
          if      (a.t === 'r' && b.t === 'r') (near ? cl.rrN : cl.rrF).push(a.x, a.y, b.x, b.y);
          else if (a.t === 'b' && b.t === 'b') (near ? cl.bbN : cl.bbF).push(a.x, a.y, b.x, b.y);
          else if (a.t === 'y' || b.t === 'y') cl.yyA.push(a.x, a.y, b.x, b.y);
          else                                  cl.xxA.push(a.x, a.y, b.x, b.y);
        }
      }
    }

    // ── 描画 ───────────────────────────────────────────────

    _draw() {
      const ctx   = this.ctx;
      const pts   = this.pts;
      const phase = this.phase;
      const n     = pts.length;
      const w     = this.cv.width, h = this.cv.height;

      if (this.opts.background === 'transparent') {
        ctx.clearRect(0, 0, w, h);
      } else {
        ctx.fillStyle = this.opts.background || '#000';
        ctx.fillRect(0, 0, w, h);
      }

      // 接続線アルファ
      let ca = 0;
      if      (phase === 'structured') ca = 0.40 * Math.min(1, this.pTimer / 6);
      else if (phase === 'stable')     ca = 0.55;
      else if (phase === 'collapsing') ca = 0.44 * Math.max(0, 1 - this.pTimer / this.pDur);
      else if (phase === 'reforming')  ca = 0.14 * Math.min(1, this.pTimer / 8);

      if (phase === 'stable' && this.stOver > 4) {
        ca *= Math.max(0.10, 1 - (this.stOver - 4) * 0.07);
      }

      // 接続線描画 (キャッシュ済みバケットを使用)
      if (ca > 0.02 && this.fps > 16) {
        const cl = this._conLines;

        const batch = (lines, r, g, b, lw, alpha) => {
          if (!lines.length || alpha < 0.005) return;
          ctx.strokeStyle = `rgba(${r},${g},${b},${alpha.toFixed(3)})`;
          ctx.lineWidth   = lw;
          ctx.beginPath();
          for (let i = 0; i < lines.length; i += 4) {
            ctx.moveTo(lines[i], lines[i + 1]);
            ctx.lineTo(lines[i + 2], lines[i + 3]);
          }
          ctx.stroke();
        };

        const _c = this.opts.getColors ? this.opts.getColors() : null;
        const rC = _c ? _c.r : [255,  55,  55];
        const bC = _c ? _c.b : [ 55, 148, 255];
        const yC = _c ? _c.y : [255, 215,  20];
        batch(cl.rrN, rC[0], rC[1], rC[2], 0.9, ca * 0.85);
        batch(cl.rrF, rC[0], rC[1], rC[2], 0.5, ca * 0.38);
        batch(cl.bbN, bC[0], bC[1], bC[2], 0.6, ca * 0.70);
        batch(cl.bbF, bC[0], bC[1], bC[2], 0.4, ca * 0.30);
        batch(cl.yyA, yC[0], yC[1], yC[2], 0.4, ca * 0.48);
        batch(cl.xxA, 155, 155, 155, 0.3, ca * 0.15);
      }

      // 粒子描画 — 色グループごとに1回の fill() (N→3回に削減)
      const drawGroup = (type, color) => {
        ctx.fillStyle = color;
        ctx.beginPath();
        for (let i = 0; i < n; i++) {
          const p = pts[i];
          if (p.t !== type) continue;
          ctx.moveTo(p.x + p.sz, p.y);
          ctx.arc(p.x, p.y, p.sz, 0, TWO_PI);
        }
        ctx.fill();
      };

      const _dc = this.opts.getColors ? this.opts.getColors() : null;
      drawGroup('r', _dc ? `rgb(${_dc.r[0]},${_dc.r[1]},${_dc.r[2]})` : 'rgb(255,55,55)');
      drawGroup('b', _dc ? `rgb(${_dc.b[0]},${_dc.b[1]},${_dc.b[2]})` : 'rgb(55,148,255)');
      drawGroup('y', _dc ? `rgb(${_dc.y[0]},${_dc.y[1]},${_dc.y[2]})` : 'rgb(255,220,30)');
    }

    // ── フレームループ ──────────────────────────────────────

    _frame(ts) {
      const el = ts - this.lastTs;
      this.lastTs = ts;

      if (el > 0 && el < 500) {
        this._fb.push(1000 / el);
        if (this._fb.length > 30) this._fb.shift();
        let sum = 0;
        for (let i = 0; i < this._fb.length; i++) sum += this._fb[i];
        this.fps = sum / this._fb.length;
      }

      const dt    = Math.min(el / 16.67, 3.0);
      const dtSec = el / 1000;

      this.pTimer += dtSec;
      if (this.mx >= 0) this.obt += dtSec;

      // クリックバッファ掃除
      if (this._clicks.length) {
        this._clicks = this._clicks.filter(c => ts - c.t < 300);
      }

      // フェーズ遷移
      if (this.pTimer >= this.pDur) this._advance();

      if (this.phase === 'stable') {
        this.stOver += dtSec;
        if (this.stOver > 14) { this.stOver = 0; this._advance(); }
      } else {
        this.stOver = 0;
      }

      this._physics(dt);

      // 接続線は2フレームに1回収集
      this._conTick = (this._conTick + 1) % 2;
      if (this._conTick === 0) this._collectConnections();

      this._draw();

      this.animId = requestAnimationFrame(ts => this._frame(ts));
    }

    // ── 公開API ────────────────────────────────────────────

    start() {
      this.lastTs = performance.now();
      this.animId = requestAnimationFrame(ts => this._frame(ts));
      return this;
    }

    stop() {
      if (this.animId) cancelAnimationFrame(this.animId);
      window.removeEventListener('resize', this._rz);
      this.cv.removeEventListener('pointerdown', this._pd);
      this.cv.removeEventListener('mousemove', this._mm);
      this.cv.removeEventListener('touchmove', this._tm);
    }

    setCount(n) {
      this.N = n;
      this._spawn();
    }

    setParam(key, val) {
      this.par[key] = val;
      if (key === 'conDist') this.gridCon = new SpatialGrid(val + 10);
      if (key === 'attDist') this.gridPhy = new SpatialGrid(val + 10);
    }

    setObsEffect(on) {
      this.opts.observerEffect = on;
      if (!on) { this.mx = -1; this.my = -1; }
    }
  }

  global.ParticleObservationEngine = ParticleObservationEngine;

})(window);
