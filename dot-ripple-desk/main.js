(function () {
  'use strict';

  var STORAGE_KEY = 'dot-ripple-desk-settings-v1';
  var canvas = document.getElementById('stage');
  var ctx = canvas.getContext('2d', { alpha: false });
  var panel = document.getElementById('settingsPanel');
  var toggle = document.getElementById('settingsToggle');
  var closePanel = document.getElementById('closePanel');
  var saveButton = document.getElementById('saveSettings');
  var resetButton = document.getElementById('resetView');

  var themes = {
    classic: {
      bg: [3, 3, 5],
      dots: [[42, 4, 9], [190, 18, 24], [234, 178, 44], [38, 102, 214], [242, 245, 235]],
      ripple: [205, 34, 44],
    },
    neon: {
      bg: [1, 2, 8],
      dots: [[12, 18, 34], [0, 238, 255], [255, 42, 198], [128, 255, 74], [255, 247, 92]],
      ripple: [0, 238, 255],
    },
    pastel: {
      bg: [18, 18, 26],
      dots: [[43, 41, 56], [245, 163, 174], [172, 207, 255], [211, 199, 255], [255, 230, 181]],
      ripple: [245, 163, 174],
    },
    monochrome: {
      bg: [0, 0, 0],
      dots: [[18, 18, 18], [72, 72, 72], [126, 126, 126], [188, 188, 188], [242, 242, 242]],
      ripple: [220, 220, 220],
    },
    sunset: {
      bg: [10, 4, 12],
      dots: [[30, 9, 24], [142, 28, 57], [232, 95, 44], [120, 50, 169], [255, 198, 92]],
      ripple: [232, 95, 44],
    },
  };

  var defaults = {
    theme: 'classic',
    dotSize: 4,
    dotGap: 10,
    rippleSpeed: 1,
    rippleStrength: 1,
    autoRipple: true,
    autoFrequency: 1.4,
    trailAmount: 0.08,
    brightness: 1,
    rebelDot: true,
    fpsLimit: 60,
  };

  var settings = loadSettings();
  var state = {
    width: 1,
    height: 1,
    dpr: 1,
    dots: [],
    grid: new Map(),
    ripples: [],
    rippleId: 1,
    rebelIndex: -1,
    pointerDown: false,
    lastSpawnX: 0,
    lastSpawnY: 0,
    lastFrame: 0,
    frameCarry: 0,
    autoTimer: 0,
  };

  function loadSettings() {
    try {
      var saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
      return Object.assign({}, defaults, saved);
    } catch (error) {
      return Object.assign({}, defaults);
    }
  }

  function saveSettingsNow() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
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

  function activeTheme() {
    return themes[settings.theme] || themes.classic;
  }

  function scaled(value) {
    return value * (window.innerWidth < 560 ? 0.9 : 1);
  }

  function resize() {
    state.dpr = Math.min(window.devicePixelRatio || 1, 2);
    state.width = Math.max(1, Math.floor(window.innerWidth));
    state.height = Math.max(1, Math.floor(window.innerHeight));
    canvas.width = Math.floor(state.width * state.dpr);
    canvas.height = Math.floor(state.height * state.dpr);
    canvas.style.width = state.width + 'px';
    canvas.style.height = state.height + 'px';
    ctx.setTransform(state.dpr, 0, 0, state.dpr, 0, 0);
    buildDots();
    paintBackground(true);
  }

  function buildDots() {
    var dots = [];
    var grid = new Map();
    var gap = clamp(scaled(Number(settings.dotGap)), 6, 20);
    var maxDots = state.width < 560 ? 6000 : 15000;
    var cols = Math.max(1, Math.floor(state.width / gap));
    var rows = Math.max(1, Math.floor(state.height / gap));

    while (cols * rows > maxDots) {
      gap += 1;
      cols = Math.max(1, Math.floor(state.width / gap));
      rows = Math.max(1, Math.floor(state.height / gap));
    }

    var offsetX = (state.width - (cols - 1) * gap) * 0.5;
    var offsetY = (state.height - (rows - 1) * gap) * 0.5;
    var best = -1;
    var rebel = 0;

    for (var y = 0; y < rows; y++) {
      for (var x = 0; x < cols; x++) {
        var px = offsetX + x * gap;
        var py = offsetY + y * gap;
        var centerBias = 1 - clamp(Math.hypot(px - state.width * 0.5, py - state.height * 0.5) / Math.min(state.width, state.height), 0, 1);
        var noise = centerBias + Math.random() * 0.25;
        if (noise > best && centerBias > 0.46) {
          best = noise;
          rebel = dots.length;
        }
        grid.set(gridKey(x, y), dots.length);
        dots.push({
          gx: x,
          gy: y,
          x: px,
          y: py,
          colorIndex: Math.random() < 0.02 ? 1 : 0,
          size: 1,
          targetSize: 1,
          glow: Math.random() * 0.06,
          lastReacted: 0,
          special: false,
          rebelTone: 0,
          delayed: 0,
        });
      }
    }

    state.dots = dots;
    state.grid = grid;
    state.rebelIndex = rebel;
    if (settings.rebelDot && dots[rebel]) dots[rebel].special = true;
    state.ripples.length = 0;
  }

  function Ripple(x, y, strength, automatic) {
    this.id = state.rippleId++;
    this.x = x;
    this.y = y;
    this.radius = 0;
    this.speed = (1.65 + Math.random() * 0.35) * Number(settings.rippleSpeed);
    this.maxRadius = Math.min(Math.max(state.width, state.height) * (automatic ? 0.38 : 0.65), 760);
    this.strength = Number(strength || 1);
    this.band = Math.max(7, Number(settings.dotGap) * 0.95);
    this.seen = new Set();
  }

  Ripple.prototype.update = function (dt) {
    this.radius += this.speed * dt * 0.06;
    return this.radius < this.maxRadius;
  };

  function spawnRipple(x, y, strength, automatic) {
    state.ripples.push(new Ripple(x, y, strength, automatic));
    if (state.ripples.length > 24) state.ripples.splice(0, state.ripples.length - 24);
  }

  function moveRebel() {
    var current = state.dots[state.rebelIndex];
    if (!current) return;
    var choices = [[1, 0], [-1, 0], [0, 1], [0, -1]];
    var pick = choices[(Math.random() * choices.length) | 0];
    var nextIndex = state.grid.get(gridKey(current.gx + pick[0], current.gy + pick[1]));
    if (nextIndex == null) return;
    current.special = false;
    state.rebelIndex = nextIndex;
    var next = state.dots[nextIndex];
    next.special = true;
    next.targetSize = Math.max(next.targetSize, 1.25);
    next.glow = Math.max(next.glow, 0.5);
  }

  function reactNeighbors(dot) {
    for (var dy = -1; dy <= 1; dy++) {
      for (var dx = -1; dx <= 1; dx++) {
        var index = state.grid.get(gridKey(dot.gx + dx, dot.gy + dy));
        var near = index == null ? null : state.dots[index];
        if (near && !near.special && Math.random() < 0.62) {
          near.colorIndex = (near.colorIndex + 2) % activeTheme().dots.length;
          near.targetSize = Math.max(near.targetSize, 1.75);
          near.glow = Math.max(near.glow, 0.85);
        }
      }
    }
  }

  function rebelReact(dot, now) {
    var roll = Math.random();
    dot.lastReacted = now;
    dot.targetSize = Math.max(dot.targetSize, 1.18);
    dot.glow = Math.max(dot.glow, roll < 0.25 ? 1.2 : 0.35);

    if (roll < 0.22) {
      dot.rebelTone = activeTheme().dots.length - 1;
      dot.delayed = now + 180;
    } else if (roll < 0.48) {
      reactNeighbors(dot);
    } else if (roll < 0.68) {
      moveRebel();
    } else if (roll < 0.82) {
      dot.colorIndex = 0;
    }
  }

  function affectDots(now) {
    var theme = activeTheme();
    for (var r = 0; r < state.ripples.length; r++) {
      var ripple = state.ripples[r];
      var inner = Math.max(0, ripple.radius - ripple.band);
      var outer = ripple.radius + ripple.band;
      var innerSq = inner * inner;
      var outerSq = outer * outer;

      for (var i = 0; i < state.dots.length; i++) {
        if (ripple.seen.has(i)) continue;
        var dot = state.dots[i];
        var dx = dot.x - ripple.x;
        var dy = dot.y - ripple.y;
        var distSq = dx * dx + dy * dy;
        if (distSq < innerSq || distSq > outerSq) continue;
        ripple.seen.add(i);

        if (settings.rebelDot && dot.special) {
          rebelReact(dot, now);
          continue;
        }

        dot.colorIndex = (dot.colorIndex + 1) % theme.dots.length;
        dot.targetSize = Math.max(dot.targetSize, 1 + 0.62 * ripple.strength * Number(settings.rippleStrength));
        dot.glow = Math.max(dot.glow, 0.72 * ripple.strength * Number(settings.rippleStrength));
        dot.lastReacted = now;
      }
    }

    for (var d = 0; d < state.dots.length; d++) {
      var delayed = state.dots[d];
      if (delayed.delayed && now > delayed.delayed) {
        delayed.delayed = 0;
        delayed.colorIndex = delayed.rebelTone % theme.dots.length;
      }
    }
  }

  function paintBackground(force) {
    var bg = activeTheme().bg;
    if (force || Number(settings.trailAmount) <= 0.001) {
      ctx.globalAlpha = 1;
      ctx.fillStyle = 'rgb(' + bg[0] + ',' + bg[1] + ',' + bg[2] + ')';
    } else {
      ctx.globalAlpha = clamp(1 - Number(settings.trailAmount), 0.55, 1);
      ctx.fillStyle = 'rgb(' + bg[0] + ',' + bg[1] + ',' + bg[2] + ')';
    }
    ctx.fillRect(0, 0, state.width, state.height);
    ctx.globalAlpha = 1;
  }

  function drawDots(dt) {
    var theme = activeTheme();
    var baseRadius = Number(settings.dotSize) * 0.5;
    var brightness = Number(settings.brightness);

    for (var i = 0; i < state.dots.length; i++) {
      var dot = state.dots[i];
      dot.size = lerp(dot.size, dot.targetSize, 0.16);
      dot.targetSize = lerp(dot.targetSize, 1, 0.08);
      dot.glow *= Math.pow(0.982, dt / 16.67);

      var color = theme.dots[dot.colorIndex % theme.dots.length];
      var alpha = clamp((0.42 + dot.glow * 0.46) * brightness, 0.08, 1);
      var radius = baseRadius * dot.size;
      var red = Math.round(clamp(color[0] * brightness, 0, 255));
      var green = Math.round(clamp(color[1] * brightness, 0, 255));
      var blue = Math.round(clamp(color[2] * brightness, 0, 255));

      ctx.globalAlpha = alpha;
      ctx.fillStyle = 'rgb(' + red + ',' + green + ',' + blue + ')';
      ctx.beginPath();
      ctx.arc(dot.x, dot.y, radius, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  function drawRipples() {
    var theme = activeTheme();
    for (var i = 0; i < state.ripples.length; i++) {
      var ripple = state.ripples[i];
      var fade = 1 - ripple.radius / ripple.maxRadius;
      var alpha = 0.045 * fade * Number(settings.brightness);
      ctx.strokeStyle = 'rgba(' + theme.ripple[0] + ',' + theme.ripple[1] + ',' + theme.ripple[2] + ',' + alpha.toFixed(3) + ')';
      ctx.lineWidth = 1 + ripple.strength;
      ctx.beginPath();
      ctx.arc(ripple.x, ripple.y, ripple.radius, 0, Math.PI * 2);
      ctx.stroke();
    }
  }

  function updateAuto(dt) {
    if (!settings.autoRipple) return;
    state.autoTimer += dt;
    var every = 1000 / clamp(Number(settings.autoFrequency), 0.2, 5);
    if (state.autoTimer >= every) {
      state.autoTimer = 0;
      spawnRipple(
        state.width * (0.08 + Math.random() * 0.84),
        state.height * (0.08 + Math.random() * 0.84),
        0.55 + Math.random() * 0.28,
        true
      );
    }
  }

  function frame(now) {
    var dt = state.lastFrame ? Math.min(60, now - state.lastFrame) : 16.67;
    state.lastFrame = now;
    state.frameCarry += dt;
    var minFrame = 1000 / Number(settings.fpsLimit || 60);
    if (state.frameCarry < minFrame) {
      requestAnimationFrame(frame);
      return;
    }
    dt = state.frameCarry;
    state.frameCarry = 0;

    paintBackground(false);
    updateAuto(dt);

    for (var i = state.ripples.length - 1; i >= 0; i--) {
      if (!state.ripples[i].update(dt)) state.ripples.splice(i, 1);
    }

    affectDots(now);
    drawDots(dt);
    drawRipples();
    requestAnimationFrame(frame);
  }

  function pointerPos(event) {
    var rect = canvas.getBoundingClientRect();
    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    };
  }

  function onPointerDown(event) {
    event.preventDefault();
    var pos = pointerPos(event);
    state.pointerDown = true;
    state.lastSpawnX = pos.x;
    state.lastSpawnY = pos.y;
    spawnRipple(pos.x, pos.y, 1, false);
  }

  function onPointerMove(event) {
    if (!state.pointerDown) return;
    event.preventDefault();
    var pos = pointerPos(event);
    var dist = Math.hypot(pos.x - state.lastSpawnX, pos.y - state.lastSpawnY);
    var threshold = Math.max(22, Number(settings.dotGap) * 3);
    if (dist >= threshold) {
      state.lastSpawnX = pos.x;
      state.lastSpawnY = pos.y;
      spawnRipple(pos.x, pos.y, 0.82, false);
    }
  }

  function onPointerUp() {
    state.pointerDown = false;
  }

  function resetView() {
    buildDots();
    paintBackground(true);
  }

  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(function () {});
    } else {
      document.exitFullscreen().catch(function () {});
    }
  }

  function openSettings(open) {
    var next = open == null ? !panel.classList.contains('is-open') : !!open;
    panel.classList.toggle('is-open', next);
    panel.setAttribute('aria-hidden', next ? 'false' : 'true');
  }

  function bindControl(id, key, parser, onChange) {
    var el = document.getElementById(id);
    var valueLabel = document.querySelector('[data-value-for="' + id + '"]');
    if (!el) return;
    el.value = settings[key];
    if (el.type === 'checkbox') el.checked = !!settings[key];
    function refresh() {
      var value = el.type === 'checkbox' ? el.checked : parser ? parser(el.value) : el.value;
      settings[key] = value;
      if (valueLabel) valueLabel.textContent = value;
      if (onChange) onChange(value);
      saveSettingsNow();
    }
    el.addEventListener('input', refresh);
    el.addEventListener('change', refresh);
    if (valueLabel) valueLabel.textContent = settings[key];
  }

  function initControls() {
    bindControl('themeSelect', 'theme', String, function () { paintBackground(true); });
    bindControl('dotSize', 'dotSize', Number);
    bindControl('dotGap', 'dotGap', Number, resize);
    bindControl('rippleSpeed', 'rippleSpeed', Number);
    bindControl('rippleStrength', 'rippleStrength', Number);
    bindControl('autoFrequency', 'autoFrequency', Number);
    bindControl('trailAmount', 'trailAmount', Number);
    bindControl('brightness', 'brightness', Number);
    bindControl('fpsLimit', 'fpsLimit', Number);
    bindControl('autoRipple', 'autoRipple', Boolean);
    bindControl('rebelDot', 'rebelDot', Boolean, resetView);
  }

  toggle.addEventListener('click', function () { openSettings(); });
  closePanel.addEventListener('click', function () { openSettings(false); });
  saveButton.addEventListener('click', saveSettingsNow);
  resetButton.addEventListener('click', resetView);
  canvas.addEventListener('pointerdown', onPointerDown, { passive: false });
  canvas.addEventListener('pointermove', onPointerMove, { passive: false });
  canvas.addEventListener('pointerup', onPointerUp);
  canvas.addEventListener('pointercancel', onPointerUp);
  canvas.addEventListener('contextmenu', function (event) { event.preventDefault(); });
  window.addEventListener('resize', resize);
  window.addEventListener('orientationchange', function () { setTimeout(resize, 120); });
  window.addEventListener('keydown', function (event) {
    if (event.target && /input|select|textarea/i.test(event.target.tagName)) return;
    if (event.key === 'f' || event.key === 'F') toggleFullscreen();
    if (event.key === 's' || event.key === 'S') openSettings();
    if (event.key === 'r' || event.key === 'R') resetView();
    if (event.code === 'Space') {
      event.preventDefault();
      settings.autoRipple = !settings.autoRipple;
      document.getElementById('autoRipple').checked = settings.autoRipple;
      saveSettingsNow();
    }
    if (event.key === 'Escape') openSettings(false);
  });

  initControls();
  resize();
  requestAnimationFrame(frame);
})();
