(function () {
  'use strict';

  const canvas = document.getElementById('dotArtCanvas');
  const ctx = canvas.getContext('2d', { alpha: false });
  const soundButton = document.querySelector('[data-sound-toggle]');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const config = {
    colors: ['#ffffff', '#ff3b30', '#ffd60a', '#64d2ff', '#ff5ac8', '#a8ff3e'],
    fireInterval: 90,
    samePointerCollisionDelay: 0.13,
    maxBulletsMobile: 200,
    maxBulletsDesktop: 400,
    maxExplosions: reducedMotion ? 60 : 100,
    maxParticles: reducedMotion ? 260 : 680,
    maxMarks: 420,
    maxSounds: 16,
  };

  const state = {
    width: 1,
    height: 1,
    dpr: 1,
    bulletId: 1,
    bullets: [],
    explosions: [],
    particles: [],
    marks: [],
    pointers: new Map(),
    lastFrame: 0,
    hintAlpha: 1,
    hasFired: false,
    audioContext: null,
    activeSounds: 0,
    soundEnabled: localStorage.getItem('dot-collision-art-sound') !== 'off',
  };

  class Bullet {
    constructor(x, y, velocityX, velocityY, color, sourceEdge, pointerId, createdAt) {
      this.id = state.bulletId++;
      this.x = x;
      this.y = y;
      this.previousX = x;
      this.previousY = y;
      this.radius = bulletRadius();
      this.velocityX = velocityX;
      this.velocityY = velocityY;
      this.color = color;
      this.sourceEdge = sourceEdge;
      this.pointerId = pointerId;
      this.createdAt = createdAt;
      this.collisionDelay = config.samePointerCollisionDelay;
      this.alive = true;
    }
  }

  class Explosion {
    constructor(x, y, color, type) {
      this.x = x;
      this.y = y;
      this.age = 0;
      this.duration = reducedMotion ? 0.15 : 0.2 + Math.random() * 0.14;
      this.startRadius = 3;
      this.maxRadius = type === 'bullet' ? bulletRadius() * 6.2 : bulletRadius() * 4.7;
      this.flashRadius = type === 'bullet' ? bulletRadius() * 2.6 : bulletRadius() * 1.9;
      this.color = color;
      this.type = type;
    }
  }

  class Particle {
    constructor(x, y, color, power) {
      const angle = Math.random() * Math.PI * 2;
      const speed = (58 + Math.random() * 132) * power;
      this.x = x;
      this.y = y;
      this.velocityX = Math.cos(angle) * speed;
      this.velocityY = Math.sin(angle) * speed;
      this.radius = 1.8 + Math.random() * 3.7;
      this.color = color;
      this.age = 0;
      this.duration = 0.26 + Math.random() * 0.36;
      this.alpha = 1;
    }
  }

  class Mark {
    constructor(x, y, color, type) {
      this.x = x;
      this.y = y;
      this.radius = bulletRadius() * (0.75 + Math.random() * 0.75);
      this.color = color;
      this.alpha = type === 'wall' ? 0.34 : 0.3;
      this.age = 0;
      this.duration = 10 + Math.random() * 50;
      this.type = type;
    }
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function shortSide() {
    return Math.min(state.width, state.height);
  }

  function bulletRadius() {
    return clamp(shortSide() * 0.012, 5, 10);
  }

  function bulletSpeed() {
    return shortSide() / 0.8;
  }

  function maxBullets() {
    return Math.min(state.width, state.height) < 720 ? config.maxBulletsMobile : config.maxBulletsDesktop;
  }

  function hexToRgb(hex) {
    return {
      r: parseInt(hex.slice(1, 3), 16),
      g: parseInt(hex.slice(3, 5), 16),
      b: parseInt(hex.slice(5, 7), 16),
    };
  }

  function rgbToHex(rgb) {
    const part = (value) => clamp(Math.round(value), 0, 255).toString(16).padStart(2, '0');
    return '#' + part(rgb.r) + part(rgb.g) + part(rgb.b);
  }

  function averageColor(a, b) {
    const ca = hexToRgb(a);
    const cb = hexToRgb(b);
    return rgbToHex({ r: (ca.r + cb.r) / 2, g: (ca.g + cb.g) / 2, b: (ca.b + cb.b) / 2 });
  }

  function randomColor() {
    return config.colors[(Math.random() * config.colors.length) | 0];
  }

  function viewportSize() {
    const viewport = window.visualViewport;
    return {
      width: Math.max(1, Math.floor(viewport ? viewport.width : window.innerWidth)),
      height: Math.max(1, Math.floor(viewport ? viewport.height : window.innerHeight)),
    };
  }

  function scaleObject(object, scaleX, scaleY) {
    object.x *= scaleX;
    object.y *= scaleY;
    if ('previousX' in object) object.previousX *= scaleX;
    if ('previousY' in object) object.previousY *= scaleY;
  }

  function resize() {
    const oldWidth = state.width;
    const oldHeight = state.height;
    const size = viewportSize();
    state.width = size.width;
    state.height = size.height;
    state.dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.floor(state.width * state.dpr);
    canvas.height = Math.floor(state.height * state.dpr);
    canvas.style.width = state.width + 'px';
    canvas.style.height = state.height + 'px';
    ctx.setTransform(state.dpr, 0, 0, state.dpr, 0, 0);

    if (oldWidth > 1 && oldHeight > 1) {
      const scaleX = state.width / oldWidth;
      const scaleY = state.height / oldHeight;
      state.bullets.forEach((item) => scaleObject(item, scaleX, scaleY));
      state.explosions.forEach((item) => scaleObject(item, scaleX, scaleY));
      state.particles.forEach((item) => scaleObject(item, scaleX, scaleY));
      state.marks.forEach((item) => scaleObject(item, scaleX, scaleY));
    }
  }

  function pointerPosition(event) {
    const rect = canvas.getBoundingClientRect();
    return {
      x: clamp(event.clientX - rect.left, 0, state.width),
      y: clamp(event.clientY - rect.top, 0, state.height),
    };
  }

  function nearestEdge(x, y) {
    const distances = [
      ['top', y],
      ['bottom', state.height - y],
      ['left', x],
      ['right', state.width - x],
    ];
    distances.sort((a, b) => a[1] - b[1]);
    return distances[0][0];
  }

  function spawnBulletFromPointer(pointerId, x, y) {
    if (state.bullets.length >= maxBullets()) return false;
    const edge = nearestEdge(x, y);
    const radius = bulletRadius();
    const speed = bulletSpeed();
    let bulletX = x;
    let bulletY = y;
    let velocityX = 0;
    let velocityY = 0;

    if (edge === 'top') {
      bulletY = radius;
      velocityY = speed;
    } else if (edge === 'bottom') {
      bulletY = state.height - radius;
      velocityY = -speed;
    } else if (edge === 'left') {
      bulletX = radius;
      velocityX = speed;
    } else {
      bulletX = state.width - radius;
      velocityX = -speed;
    }

    bulletX = clamp(bulletX, radius, state.width - radius);
    bulletY = clamp(bulletY, radius, state.height - radius);
    state.bullets.push(new Bullet(bulletX, bulletY, velocityX, velocityY, randomColor(), edge, pointerId, performance.now() / 1000));
    state.hasFired = true;
    playFire(edge);
    return true;
  }

  function ensureAudio() {
    if (!state.soundEnabled) return;
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    if (!state.audioContext) state.audioContext = new AudioContext();
    if (state.audioContext.state === 'suspended') state.audioContext.resume();
  }

  function playPop(type) {
    if (!state.soundEnabled || !state.audioContext || state.activeSounds >= config.maxSounds) return;
    const audio = state.audioContext;
    const now = audio.currentTime;
    const oscillator = audio.createOscillator();
    const gain = audio.createGain();
    const crowd = clamp(state.activeSounds / config.maxSounds, 0, 1);
    const base = type === 'bullet' ? 175 : 135;
    const variance = 1 + (Math.random() * 0.16 - 0.08);
    const duration = type === 'bullet' ? 0.14 : 0.1;

    state.activeSounds += 1;
    oscillator.type = type === 'bullet' ? 'triangle' : 'sine';
    oscillator.frequency.setValueAtTime(base * variance, now);
    oscillator.frequency.exponentialRampToValueAtTime(base * 0.68 * variance, now + duration);
    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.linearRampToValueAtTime(0.055 * (1 - crowd * 0.55), now + 0.018);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);
    oscillator.connect(gain);
    gain.connect(audio.destination);
    oscillator.start(now);
    oscillator.stop(now + duration + 0.02);
    oscillator.addEventListener('ended', () => {
      state.activeSounds = Math.max(0, state.activeSounds - 1);
      oscillator.disconnect();
      gain.disconnect();
    }, { once: true });
  }

  function playFire(edge) {
    if (!state.soundEnabled || !state.audioContext || state.activeSounds >= config.maxSounds) return;
    const audio = state.audioContext;
    const now = audio.currentTime;
    const oscillator = audio.createOscillator();
    const gain = audio.createGain();
    const crowd = clamp(state.activeSounds / config.maxSounds, 0, 1);
    const edgeOffset = edge === 'top' || edge === 'bottom' ? 24 : -12;
    const base = 390 + edgeOffset;
    const variance = 1 + (Math.random() * 0.12 - 0.06);
    const duration = 0.055;

    state.activeSounds += 1;
    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(base * variance, now);
    oscillator.frequency.exponentialRampToValueAtTime(base * 1.28 * variance, now + duration);
    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.linearRampToValueAtTime(0.026 * (1 - crowd * 0.55), now + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);
    oscillator.connect(gain);
    gain.connect(audio.destination);
    oscillator.start(now);
    oscillator.stop(now + duration + 0.015);
    oscillator.addEventListener('ended', () => {
      state.activeSounds = Math.max(0, state.activeSounds - 1);
      oscillator.disconnect();
      gain.disconnect();
    }, { once: true });
  }

  function addExplosion(x, y, color, type) {
    state.explosions.push(new Explosion(x, y, color, type));
    if (state.explosions.length > config.maxExplosions) state.explosions.splice(0, state.explosions.length - config.maxExplosions);

    const particleCount = type === 'bullet'
      ? (reducedMotion ? 6 + ((Math.random() * 4) | 0) : 10 + ((Math.random() * 9) | 0))
      : (reducedMotion ? 4 + ((Math.random() * 3) | 0) : 7 + ((Math.random() * 7) | 0));
    const loadFactor = state.particles.length > config.maxParticles * 0.72 ? 0.45 : 1;
    for (let i = 0; i < Math.floor(particleCount * loadFactor); i++) {
      state.particles.push(new Particle(x, y, color, type === 'bullet' ? 1.85 : 1.25));
    }
    if (state.particles.length > config.maxParticles) state.particles.splice(0, state.particles.length - config.maxParticles);

    state.marks.push(new Mark(x, y, color, type));
    if (state.marks.length > config.maxMarks) state.marks.splice(0, state.marks.length - config.maxMarks);
    playPop(type);
  }

  function onPointerDown(event) {
    event.preventDefault();
    ensureAudio();
    const pos = pointerPosition(event);
    spawnBulletFromPointer(event.pointerId, pos.x, pos.y);
    state.pointers.set(event.pointerId, { x: pos.x, y: pos.y, lastFire: performance.now(), lastX: pos.x, lastY: pos.y });
    canvas.setPointerCapture?.(event.pointerId);
  }

  function onPointerMove(event) {
    const pointer = state.pointers.get(event.pointerId);
    if (!pointer) return;
    event.preventDefault();
    const now = performance.now();
    const pos = pointerPosition(event);
    const moved = Math.hypot(pos.x - pointer.lastX, pos.y - pointer.lastY);
    pointer.x = pos.x;
    pointer.y = pos.y;
    if (now - pointer.lastFire >= config.fireInterval && moved >= bulletRadius() * 1.8) {
      if (spawnBulletFromPointer(event.pointerId, pos.x, pos.y)) {
        pointer.lastFire = now;
        pointer.lastX = pos.x;
        pointer.lastY = pos.y;
      }
    }
  }

  function onPointerEnd(event) {
    state.pointers.delete(event.pointerId);
    canvas.releasePointerCapture?.(event.pointerId);
  }

  function checkWallCollision(bullet) {
    if (!bullet.alive) return;
    let hit = false;
    let x = bullet.x;
    let y = bullet.y;

    if (bullet.sourceEdge === 'top' && bullet.y + bullet.radius >= state.height) {
      hit = true;
      y = state.height - bullet.radius;
    } else if (bullet.sourceEdge === 'bottom' && bullet.y - bullet.radius <= 0) {
      hit = true;
      y = bullet.radius;
    } else if (bullet.sourceEdge === 'left' && bullet.x + bullet.radius >= state.width) {
      hit = true;
      x = state.width - bullet.radius;
    } else if (bullet.sourceEdge === 'right' && bullet.x - bullet.radius <= 0) {
      hit = true;
      x = bullet.radius;
    }

    if (!hit) return;
    bullet.x = x;
    bullet.y = y;
    bullet.alive = false;
    addExplosion(x, y, bullet.color, 'wall');
  }

  function shouldSkipPair(a, b, now) {
    return a.pointerId === b.pointerId
      && a.sourceEdge === b.sourceEdge
      && now - Math.max(a.createdAt, b.createdAt) < Math.max(a.collisionDelay, b.collisionDelay);
  }

  function buildSpatialHash() {
    const cellSize = bulletRadius() * 7;
    const hash = new Map();
    for (let i = 0; i < state.bullets.length; i++) {
      const bullet = state.bullets[i];
      if (!bullet.alive) continue;
      const cellX = Math.floor(bullet.x / cellSize);
      const cellY = Math.floor(bullet.y / cellSize);
      const key = cellX + ':' + cellY;
      if (!hash.has(key)) hash.set(key, []);
      hash.get(key).push(bullet);
    }
    return { hash, cellSize };
  }

  function checkBulletCollisions(now) {
    const { hash, cellSize } = buildSpatialHash();
    const checked = new Set();
    const offsets = [-1, 0, 1];

    for (const bullet of state.bullets) {
      if (!bullet.alive) continue;
      const cellX = Math.floor(bullet.x / cellSize);
      const cellY = Math.floor(bullet.y / cellSize);
      for (const ox of offsets) {
        for (const oy of offsets) {
          const neighbors = hash.get((cellX + ox) + ':' + (cellY + oy));
          if (!neighbors) continue;
          for (const other of neighbors) {
            if (!other.alive || other.id === bullet.id) continue;
            const low = Math.min(bullet.id, other.id);
            const high = Math.max(bullet.id, other.id);
            const pairKey = low + ':' + high;
            if (checked.has(pairKey)) continue;
            checked.add(pairKey);
            if (shouldSkipPair(bullet, other, now)) continue;

            const dx = other.x - bullet.x;
            const dy = other.y - bullet.y;
            const radiusSum = bullet.radius + other.radius;
            if (dx * dx + dy * dy <= radiusSum * radiusSum) {
              bullet.alive = false;
              other.alive = false;
              addExplosion((bullet.x + other.x) / 2, (bullet.y + other.y) / 2, averageColor(bullet.color, other.color), 'bullet');
            }
          }
        }
      }
    }
  }

  function updateBullets(dt) {
    const minDiameter = bulletRadius() * 2;
    const maxMove = bulletSpeed() * dt;
    const safeDistance = minDiameter * 0.5;
    const steps = Math.max(1, Math.ceil(maxMove / safeDistance));
    const subDelta = dt / steps;

    for (let step = 0; step < steps; step++) {
      for (const bullet of state.bullets) {
        if (!bullet.alive) continue;
        bullet.previousX = bullet.x;
        bullet.previousY = bullet.y;
        bullet.x += bullet.velocityX * subDelta;
        bullet.y += bullet.velocityY * subDelta;
        checkWallCollision(bullet);
      }
      checkBulletCollisions(performance.now() / 1000);
    }
  }

  function updateTimed(list, dt, updater) {
    for (let i = list.length - 1; i >= 0; i--) {
      const item = list[i];
      item.age += dt;
      updater(item, dt);
      if (item.age >= item.duration) list.splice(i, 1);
    }
  }

  function update(dt) {
    updateBullets(dt);
    updateTimed(state.explosions, dt, () => {});
    updateTimed(state.particles, dt, (particle, subDt) => {
      particle.x += particle.velocityX * subDt;
      particle.y += particle.velocityY * subDt;
      particle.velocityX *= Math.pow(0.08, subDt);
      particle.velocityY *= Math.pow(0.08, subDt);
      particle.alpha = 1 - particle.age / particle.duration;
    });
    updateTimed(state.marks, dt, (mark) => {
      mark.alpha *= Math.pow(0.998, dt * 60);
    });
    for (let i = state.bullets.length - 1; i >= 0; i--) {
      if (!state.bullets[i].alive) state.bullets.splice(i, 1);
    }
    if (state.hasFired) state.hintAlpha = Math.max(0, state.hintAlpha - dt * 1.6);
  }

  function drawBackground() {
    ctx.globalAlpha = 1;
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, state.width, state.height);
  }

  function drawMarks() {
    for (const mark of state.marks) {
      const fade = 1 - mark.age / mark.duration;
      ctx.globalAlpha = mark.alpha * fade;
      ctx.fillStyle = mark.color;
      ctx.beginPath();
      if (mark.type === 'wall') {
        ctx.ellipse(mark.x, mark.y, mark.radius * 1.4, mark.radius * 0.55, 0, 0, Math.PI * 2);
      } else {
        ctx.arc(mark.x, mark.y, mark.radius, 0, Math.PI * 2);
      }
      ctx.fill();
    }
  }

  function drawBullets() {
    for (const bullet of state.bullets) {
      ctx.globalAlpha = 0.22;
      ctx.strokeStyle = bullet.color;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(bullet.x, bullet.y, bullet.radius + 2, 0, Math.PI * 2);
      ctx.stroke();
      ctx.globalAlpha = 0.96;
      ctx.fillStyle = bullet.color;
      ctx.beginPath();
      ctx.arc(bullet.x, bullet.y, bullet.radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.globalAlpha = 0.62;
      ctx.strokeStyle = 'rgba(0, 0, 0, 0.5)';
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }
  }

  function drawExplosions() {
    for (const explosion of state.explosions) {
      const t = clamp(explosion.age / explosion.duration, 0, 1);
      const ease = 1 - Math.pow(1 - t, 2);
      const radius = explosion.startRadius + (explosion.maxRadius - explosion.startRadius) * ease;
      if (t < 0.22 && !reducedMotion) {
        ctx.globalAlpha = (1 - t / 0.22) * 0.76;
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(explosion.x, explosion.y, explosion.flashRadius * (1 + t * 1.2), 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = (1 - t) * (reducedMotion ? 0.38 : 0.56);
      ctx.fillStyle = explosion.color;
      ctx.beginPath();
      ctx.arc(explosion.x, explosion.y, radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.globalAlpha = (1 - t) * 0.44;
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(explosion.x, explosion.y, radius * 0.62, 0, Math.PI * 2);
      ctx.stroke();
    }
  }

  function drawParticles() {
    for (const particle of state.particles) {
      const t = clamp(particle.age / particle.duration, 0, 1);
      ctx.globalAlpha = particle.alpha * (1 - t * 0.2);
      ctx.fillStyle = particle.color;
      ctx.beginPath();
      ctx.arc(particle.x, particle.y, particle.radius * (1 - t * 0.72), 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function drawHint() {
    if (state.hintAlpha <= 0) return;
    ctx.globalAlpha = state.hintAlpha * 0.55;
    ctx.fillStyle = '#ffffff';
    ctx.font = '13px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('上下左右を触ってください', state.width * 0.5, state.height * 0.5);
  }

  function draw() {
    drawBackground();
    drawMarks();
    drawBullets();
    drawExplosions();
    drawParticles();
    drawHint();
    ctx.globalAlpha = 1;
  }

  function frame(timestamp) {
    const dt = state.lastFrame ? Math.min((timestamp - state.lastFrame) / 1000, 0.033) : 0.016;
    state.lastFrame = timestamp;
    update(dt);
    draw();
    requestAnimationFrame(frame);
  }

  function updateSoundButton() {
    soundButton.setAttribute('aria-pressed', state.soundEnabled ? 'true' : 'false');
  }

  soundButton.addEventListener('click', (event) => {
    event.preventDefault();
    state.soundEnabled = !state.soundEnabled;
    localStorage.setItem('dot-collision-art-sound', state.soundEnabled ? 'on' : 'off');
    if (state.soundEnabled) ensureAudio();
    updateSoundButton();
  });

  window.addEventListener('resize', resize);
  window.visualViewport?.addEventListener('resize', resize);
  window.visualViewport?.addEventListener('scroll', resize);
  window.addEventListener('orientationchange', () => window.setTimeout(resize, 80));
  canvas.addEventListener('pointerdown', onPointerDown, { passive: false });
  canvas.addEventListener('pointermove', onPointerMove, { passive: false });
  canvas.addEventListener('pointerup', onPointerEnd);
  canvas.addEventListener('pointercancel', onPointerEnd);
  canvas.addEventListener('contextmenu', (event) => event.preventDefault());

  updateSoundButton();
  resize();
  requestAnimationFrame(frame);
})();
