(function () {
  'use strict';

  const canvas = document.getElementById('rippleCanvas');
  const ctx = canvas.getContext('2d', { alpha: false });
  const palette = [
    [34, 2, 6],
    [148, 14, 20],
    [221, 168, 42],
    [31, 87, 184],
    [236, 242, 232],
  ];
  const rebelPalette = [
    [5, 5, 8],
    [17, 180, 156],
    [226, 36, 105],
  ];

  const state = {
    width: 0,
    height: 0,
    dpr: 1,
    step: 10,
    radius: 2.4,
    dots: [],
    ripples: [],
    rebelIndex: -1,
    pointerDown: false,
    lastSpawnX: 0,
    lastSpawnY: 0,
    idleMs: 0,
    lastFrame: 0,
    nextIdleRipple: 1500,
    nextBlackoutRipple: 60000,
    rippleId: 1,
    grid: new Map(),
  };

  class Ripple {
    constructor(x, y, strength, idle, mode) {
      this.id = state.rippleId++;
      this.x = x;
      this.y = y;
      this.mode = mode || 'color';
      this.radius = 0;
      this.speed = this.mode === 'blackout' ? 2.85 : idle ? 1.1 : 2.25 + Math.random() * 0.45;
      this.maxRadius = this.mode === 'blackout'
        ? Math.hypot(state.width, state.height) * 0.62
        : Math.min(Math.max(state.width, state.height) * (idle ? 0.34 : 0.62), 680);
      this.strength = strength;
      this.band = this.mode === 'blackout' ? Math.max(28, state.step * 4.4) : Math.max(7, state.step * 0.92);
      this.seen = new Set();
    }

    update(dt) {
      this.radius += this.speed * dt * 0.06;
      return this.radius < this.maxRadius;
    }
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function lerp(a, b, t) {
    return a + (b - a) * t;
  }

  function gridKey(x, y) {
    return x + ':' + y;
  }

  function chooseGrid() {
    const narrow = Math.min(window.innerWidth, window.innerHeight);
    if (narrow < 420) return { step: 9, radius: 2.25 };
    if (narrow < 820) return { step: 10, radius: 2.45 };
    return { step: 12, radius: 2.8 };
  }

  function resize() {
    const grid = chooseGrid();
    state.dpr = Math.min(window.devicePixelRatio || 1, 2);
    state.width = Math.max(1, Math.floor(window.innerWidth));
    state.height = Math.max(1, Math.floor(window.innerHeight));
    state.step = grid.step;
    state.radius = grid.radius;
    canvas.width = Math.floor(state.width * state.dpr);
    canvas.height = Math.floor(state.height * state.dpr);
    canvas.style.width = state.width + 'px';
    canvas.style.height = state.height + 'px';
    ctx.setTransform(state.dpr, 0, 0, state.dpr, 0, 0);
    buildDots();
  }

  function buildDots() {
    const dots = [];
    const grid = new Map();
    const cols = Math.max(1, Math.floor(state.width / state.step));
    const rows = Math.max(1, Math.floor(state.height / state.step));
    const offsetX = (state.width - (cols - 1) * state.step) * 0.5;
    const offsetY = (state.height - (rows - 1) * state.step) * 0.5;
    let rebelCandidate = 0;
    let bestNoise = -1;

    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        const px = offsetX + x * state.step;
        const py = offsetY + y * state.step;
        const centerBias = 1 - clamp(Math.hypot(px - state.width * 0.5, py - state.height * 0.5) / Math.min(state.width, state.height), 0, 1);
        const noise = centerBias + Math.random() * 0.26;
        if (noise > bestNoise && centerBias > 0.48) {
          bestNoise = noise;
          rebelCandidate = dots.length;
        }
        grid.set(gridKey(x, y), dots.length);
        dots.push({
          x,
          y,
          px,
          py,
          state: Math.random() < 0.015 ? 1 : 0,
          glow: Math.random() * 0.08,
          scale: 0,
          blackout: 0,
          rebelTone: 0,
          isRebelDot: false,
        });
      }
    }

    state.dots = dots;
    state.grid = grid;
    state.rebelIndex = rebelCandidate;
    if (dots[rebelCandidate]) dots[rebelCandidate].isRebelDot = true;
    state.ripples.length = 0;
  }

  function moveRebel() {
    const current = state.dots[state.rebelIndex];
    if (!current) return;
    const choices = [[1, 0], [-1, 0], [0, 1], [0, -1]];
    const pick = choices[(Math.random() * choices.length) | 0];
    const nextIndex = state.grid.get(gridKey(current.x + pick[0], current.y + pick[1]));
    if (nextIndex == null) return;
    current.isRebelDot = false;
    state.rebelIndex = nextIndex;
    const next = state.dots[nextIndex];
    next.isRebelDot = true;
    next.state = 0;
    next.scale = 0.2;
    next.glow = 0.22;
  }

  function pulseNeighbors(rebel) {
    for (let dy = -1; dy <= 1; dy++) {
      for (let dx = -1; dx <= 1; dx++) {
        const index = state.grid.get(gridKey(rebel.x + dx, rebel.y + dy));
        const dot = index == null ? null : state.dots[index];
        if (dot && !dot.isRebelDot && Math.random() < 0.68) {
          dot.state = (dot.state + 2) % palette.length;
          dot.scale = Math.max(dot.scale, 0.8);
          dot.glow = Math.max(dot.glow, 0.9);
        }
      }
    }
  }

  function rebelAction(dot) {
    dot.rebelTone = (dot.rebelTone + 1) % rebelPalette.length;
    dot.scale = Math.max(dot.scale, 0.35);
    dot.glow = Math.max(dot.glow, 0.28);
    if (Math.random() < 0.55) {
      setTimeout(function () {
        pulseNeighbors(dot);
      }, 120 + Math.random() * 180);
    }
    if (Math.random() < 0.34) moveRebel();
  }

  function spawnRipple(x, y, strength, idle, mode) {
    state.ripples.push(new Ripple(x, y, strength || 1, !!idle, mode));
    if (state.ripples.length > 18) state.ripples.splice(0, state.ripples.length - 18);
  }

  function spawnBlackoutRipple() {
    spawnRipple(state.width * 0.5, state.height * 0.5, 1, false, 'blackout');
  }

  function pointerPosition(event) {
    const rect = canvas.getBoundingClientRect();
    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    };
  }

  function onPointerDown(event) {
    event.preventDefault();
    const pos = pointerPosition(event);
    state.pointerDown = true;
    state.lastSpawnX = pos.x;
    state.lastSpawnY = pos.y;
    state.idleMs = 0;
    spawnRipple(pos.x, pos.y, 1.08, false);
  }

  function onPointerMove(event) {
    if (!state.pointerDown) return;
    event.preventDefault();
    const pos = pointerPosition(event);
    const dist = Math.hypot(pos.x - state.lastSpawnX, pos.y - state.lastSpawnY);
    state.idleMs = 0;
    if (dist >= state.step * 3.2) {
      state.lastSpawnX = pos.x;
      state.lastSpawnY = pos.y;
      spawnRipple(pos.x, pos.y, 0.86, false);
    }
  }

  function onPointerUp() {
    state.pointerDown = false;
  }

  function affectDots() {
    for (let r = 0; r < state.ripples.length; r++) {
      const ripple = state.ripples[r];
      const radius = ripple.radius;
      const inner = Math.max(0, radius - ripple.band);
      const outer = radius + ripple.band;
      const innerSq = inner * inner;
      const outerSq = outer * outer;

      for (let i = 0; i < state.dots.length; i++) {
        if (ripple.seen.has(i)) continue;
        const dot = state.dots[i];
        const dx = dot.px - ripple.x;
        const dy = dot.py - ripple.y;
        const distSq = dx * dx + dy * dy;
        if (distSq < innerSq || distSq > outerSq) continue;

        ripple.seen.add(i);
        if (ripple.mode === 'blackout') {
          dot.state = 0;
          dot.blackout = 1;
          dot.scale = Math.max(dot.scale, 0.38);
          dot.glow = 0;
          if (dot.isRebelDot) {
            dot.rebelTone = 0;
            if (Math.random() < 0.18) moveRebel();
          }
          continue;
        }

        if (dot.isRebelDot) {
          rebelAction(dot);
          continue;
        }

        dot.state = (dot.state + 1) % palette.length;
        dot.scale = Math.max(dot.scale, 1.15 * ripple.strength);
        dot.glow = Math.max(dot.glow, 1.0 * ripple.strength);
      }
    }
  }

  function drawDot(dot, dt) {
    dot.scale *= Math.pow(0.91, dt / 16.67);
    dot.glow *= Math.pow(0.985, dt / 16.67);
    dot.blackout *= Math.pow(0.996, dt / 16.67);
    if (state.idleMs > 900) dot.glow *= Math.pow(0.988, dt / 16.67);

    const color = dot.isRebelDot ? rebelPalette[dot.rebelTone] : palette[dot.state];
    const sink = clamp(state.idleMs / 9000, 0, 0.78);
    const pulse = 1 + dot.scale * 0.55;
    const alpha = clamp(0.46 + dot.glow * 0.42 - sink * 0.28, 0.12, 0.96);
    const black = clamp(dot.blackout, 0, 1);
    const red = Math.round(lerp(lerp(color[0], 3, sink), 0, black));
    const green = Math.round(lerp(lerp(color[1], 3, sink), 0, black));
    const blue = Math.round(lerp(lerp(color[2], 4, sink), 0, black));

    ctx.globalAlpha = alpha;
    ctx.fillStyle = 'rgb(' + red + ',' + green + ',' + blue + ')';
    ctx.beginPath();
    ctx.arc(dot.px, dot.py, state.radius * pulse, 0, Math.PI * 2);
    ctx.fill();
  }

  function drawRipples() {
    ctx.globalAlpha = 1;
    for (let i = 0; i < state.ripples.length; i++) {
      const ripple = state.ripples[i];
      const fade = 1 - ripple.radius / ripple.maxRadius;
      if (ripple.mode === 'blackout') {
        ctx.strokeStyle = 'rgba(0, 0, 0, ' + (0.4 * fade).toFixed(3) + ')';
        ctx.lineWidth = Math.max(10, state.step * 1.5);
      } else {
        ctx.strokeStyle = 'rgba(170, 18, 28, ' + (0.04 * fade).toFixed(3) + ')';
        ctx.lineWidth = 1;
      }
      ctx.beginPath();
      ctx.arc(ripple.x, ripple.y, ripple.radius, 0, Math.PI * 2);
      ctx.stroke();
    }
  }

  function frame(ts) {
    const dt = state.lastFrame ? Math.min(48, ts - state.lastFrame) : 16.67;
    state.lastFrame = ts;
    state.idleMs += dt;
    ctx.globalAlpha = 1;
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, state.width, state.height);

    if (state.idleMs > state.nextIdleRipple) {
      state.nextIdleRipple = state.idleMs + 1800 + Math.random() * 3200;
      spawnRipple(
        state.width * (0.18 + Math.random() * 0.64),
        state.height * (0.18 + Math.random() * 0.64),
        0.55,
        true
      );
    }
    if (ts > state.nextBlackoutRipple) {
      state.nextBlackoutRipple = ts + 60000;
      spawnBlackoutRipple();
    }

    for (let i = state.ripples.length - 1; i >= 0; i--) {
      if (!state.ripples[i].update(dt)) state.ripples.splice(i, 1);
    }

    affectDots();
    for (let i = 0; i < state.dots.length; i++) drawDot(state.dots[i], dt);
    drawRipples();
    requestAnimationFrame(frame);
  }

  window.addEventListener('resize', resize);
  window.addEventListener('orientationchange', function () {
    setTimeout(resize, 80);
  });
  canvas.addEventListener('pointerdown', onPointerDown, { passive: false });
  canvas.addEventListener('pointermove', onPointerMove, { passive: false });
  canvas.addEventListener('pointerup', onPointerUp);
  canvas.addEventListener('pointercancel', onPointerUp);
  canvas.addEventListener('contextmenu', function (event) {
    event.preventDefault();
  });

  resize();
  requestAnimationFrame(frame);
})();
