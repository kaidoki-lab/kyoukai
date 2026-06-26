(function () {
  "use strict";

  const canvas = document.getElementById("colonyCanvas");
  const messageLayer = document.querySelector("[data-colony-messages]");
  const stage = document.querySelector(".colony-stage");
  if (!canvas || !messageLayer || !stage) return;

  const ctx = canvas.getContext("2d", { alpha: true });
  const ants = [];
  const splats = [];
  const messages = [];
  const routes = [];
  const MAX_ANTS = 100;
  const RARE_MESSAGE = "ありがとう。アリだけに。";
  const state = {
    width: 0,
    height: 0,
    dpr: 1,
    lastTime: 0,
    nextSpawnAt: 0,
    routeSeed: Math.random() * 1000,
  };
  window.KYOUKAI_COLONY_DEBUG = { ants, splats, messages, state };

  function random(min, max) {
    return min + Math.random() * (max - min);
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function wrapAngle(angle) {
    while (angle > Math.PI) angle -= Math.PI * 2;
    while (angle < -Math.PI) angle += Math.PI * 2;
    return angle;
  }

  function resize() {
    const rect = canvas.getBoundingClientRect();
    state.width = Math.max(1, rect.width);
    state.height = Math.max(1, rect.height);
    state.dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(state.width * state.dpr);
    canvas.height = Math.round(state.height * state.dpr);
    ctx.setTransform(state.dpr, 0, 0, state.dpr, 0, 0);
    buildRoutes();
  }

  function buildRoutes() {
    routes.length = 0;
    for (let i = 0; i < 4; i += 1) {
      routes.push({
        id: i,
        baseY: state.height * random(0.16, 0.86),
        amplitude: state.height * random(0.035, 0.12),
        phase: random(0, Math.PI * 2),
        frequency: random(1.1, 2.4),
        drift: random(-0.00004, 0.00004),
        direction: Math.random() < 0.5 ? 0 : Math.PI,
      });
    }
  }

  function routePoint(route, x, time) {
    const nx = x / Math.max(1, state.width);
    const y = route.baseY
      + Math.sin(nx * Math.PI * 2 * route.frequency + route.phase + time * route.drift) * route.amplitude
      + Math.sin(nx * Math.PI * 5 + route.phase * 0.7 + time * route.drift * 2) * route.amplitude * 0.24;
    return clamp(y, 8, state.height - 8);
  }

  function makeAnt(fromEdge) {
    const route = routes[Math.floor(Math.random() * routes.length)] || { id: 0, direction: 0 };
    const edge = fromEdge || Math.floor(random(0, 4));
    let x = random(0, state.width);
    let y = random(0, state.height);
    let angle = route.direction + random(-0.28, 0.28);

    if (edge === 0) {
      x = random(-16, -4);
      y = routePoint(route, 0, performance.now());
      angle = random(-0.45, 0.45);
    } else if (edge === 1) {
      x = random(state.width + 4, state.width + 16);
      y = routePoint(route, state.width, performance.now());
      angle = Math.PI + random(-0.45, 0.45);
    } else if (edge === 2) {
      x = random(0, state.width);
      y = random(-16, -4);
      angle = Math.PI / 2 + random(-0.65, 0.65);
    } else {
      x = random(0, state.width);
      y = random(state.height + 4, state.height + 16);
      angle = -Math.PI / 2 + random(-0.65, 0.65);
    }

    return {
      x,
      y,
      angle,
      speed: random(0.15, 0.6),
      size: random(1.9, 4.8),
      routeId: route.id,
      routeWeight: random(0.35, 0.9),
      wander: random(0.002, 0.012),
      turnRate: random(0.012, 0.036),
      gait: random(0, Math.PI * 2),
      alive: true,
    };
  }

  function seedAnts() {
    const initialCount = Math.floor(random(5, 11));
    for (let i = 0; i < initialCount; i += 1) {
      const ant = makeAnt();
      ant.x = random(0, state.width);
      ant.y = random(0, state.height);
      ants.push(ant);
    }
  }

  function scheduleSpawn(now) {
    state.nextSpawnAt = now + random(3000, 8000);
  }

  function updateDebugAttributes() {
    stage.dataset.antCount = String(ants.length);
    stage.dataset.splatCount = String(splats.length);
    stage.dataset.messageCount = String(messages.length);
    const visibleAnt = ants.find((ant) => (
      ant.x >= 0 && ant.x <= state.width && ant.y >= 0 && ant.y <= state.height
    ));
    if (visibleAnt) {
      stage.dataset.firstAntX = visibleAnt.x.toFixed(1);
      stage.dataset.firstAntY = visibleAnt.y.toFixed(1);
    }
  }

  function spawnAnts(now) {
    if (now < state.nextSpawnAt || ants.length >= MAX_ANTS) return;
    const count = Math.min(MAX_ANTS - ants.length, Math.floor(random(1, 4)));
    for (let i = 0; i < count; i += 1) ants.push(makeAnt());
    scheduleSpawn(now);
  }

  function updateAnt(ant, dt, now) {
    const route = routes[ant.routeId % routes.length];
    if (route) {
      const targetY = routePoint(route, clamp(ant.x, 0, state.width), now);
      const desiredAngle = Math.atan2((targetY - ant.y) * ant.routeWeight, Math.cos(route.direction) * 90);
      const routeAngle = route.direction === 0 ? desiredAngle : Math.PI - desiredAngle;
      ant.angle += wrapAngle(routeAngle - ant.angle) * ant.turnRate;
    }

    ant.gait += dt * 0.006;
    ant.angle += Math.sin(ant.gait + state.routeSeed) * ant.wander * dt * 0.18;
    if (Math.random() < 0.006) ant.angle += random(-0.18, 0.18);

    const step = ant.speed * dt * 0.06;
    ant.x += Math.cos(ant.angle) * step;
    ant.y += Math.sin(ant.angle) * step;

    const margin = 28;
    if (ant.x < -margin) ant.x = state.width + margin * 0.5;
    if (ant.x > state.width + margin) ant.x = -margin * 0.5;
    if (ant.y < -margin) ant.y = state.height + margin * 0.5;
    if (ant.y > state.height + margin) ant.y = -margin * 0.5;
  }

  function dot(x, y, r, color, alpha) {
    ctx.globalAlpha = alpha;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
  }

  function drawAnt(ant) {
    const scale = ant.size;
    const ca = Math.cos(ant.angle);
    const sa = Math.sin(ant.angle);
    const sideX = -sa;
    const sideY = ca;

    function local(px, py, radius, alpha) {
      dot(
        ant.x + ca * px * scale + sideX * py * scale,
        ant.y + sa * px * scale + sideY * py * scale,
        radius,
        "rgb(7, 7, 6)",
        alpha,
      );
    }

    local(0.55, 0, Math.max(0.55, scale * 0.18), 0.72);
    local(0, 0, Math.max(0.6, scale * 0.2), 0.78);
    local(-0.55, 0, Math.max(0.68, scale * 0.24), 0.82);
    if (scale > 3.1) {
      local(-0.04, -0.45, 0.42, 0.45);
      local(-0.04, 0.45, 0.42, 0.45);
    }
  }

  function makeSplat(x, y, antSize) {
    const dots = [];
    const count = Math.floor(random(3, 9));
    for (let i = 0; i < count; i += 1) {
      const angle = random(0, Math.PI * 2);
      const spread = random(0.2, antSize * 1.5);
      dots.push({
        dx: Math.cos(angle) * spread,
        dy: Math.sin(angle) * spread,
        r: random(0.55, 1.4),
        color: Math.random() < 0.45 ? "rgb(18, 13, 11)" : "rgb(78, 14, 13)",
      });
    }
    const life = random(3000, 6000);
    splats.push({ x, y, dots, life, maxLife: life });
  }

  function showRareMessage(x, y) {
    const node = document.createElement("span");
    node.className = "colony-message";
    node.textContent = RARE_MESSAGE;
    messageLayer.append(node);
    messages.push({ x, y: y - 10, text: RARE_MESSAGE, life: 1000, maxLife: 1000, node });
  }

  function crushAt(clientX, clientY) {
    const rect = canvas.getBoundingClientRect();
    const x = clientX - rect.left;
    const y = clientY - rect.top;
    const radius = clamp(Math.min(state.width, state.height) * 0.035, 12, 24);
    let nearest = null;
    let best = radius * radius;

    ants.forEach((ant, index) => {
      const dx = ant.x - x;
      const dy = ant.y - y;
      const dist = dx * dx + dy * dy;
      if (dist <= best) {
        best = dist;
        nearest = { ant, index };
      }
    });

    if (!nearest) return;
    ants.splice(nearest.index, 1);
    makeSplat(nearest.ant.x, nearest.ant.y, nearest.ant.size);
    if (Math.random() < 0.005) showRareMessage(nearest.ant.x, nearest.ant.y);
  }

  function updateSplats(dt) {
    for (let i = splats.length - 1; i >= 0; i -= 1) {
      const splat = splats[i];
      splat.life -= dt;
      if (splat.life <= 0) splats.splice(i, 1);
    }
  }

  function drawSplats() {
    splats.forEach((splat) => {
      const alpha = clamp(splat.life / splat.maxLife, 0, 1) * 0.56;
      splat.dots.forEach((part) => {
        dot(splat.x + part.dx, splat.y + part.dy, part.r, part.color, alpha);
      });
    });
  }

  function updateMessages(dt) {
    for (let i = messages.length - 1; i >= 0; i -= 1) {
      const message = messages[i];
      message.life -= dt;
      const t = clamp(message.life / message.maxLife, 0, 1);
      message.node.style.opacity = String(t * 0.72);
      message.node.style.transform = `translate(-50%, -100%) translateY(${(1 - t) * -8}px)`;
      message.node.style.left = `${message.x}px`;
      message.node.style.top = `${message.y}px`;
      if (message.life <= 0) {
        message.node.remove();
        messages.splice(i, 1);
      }
    }
  }

  function frame(now) {
    if (!state.lastTime) state.lastTime = now;
    const dt = Math.min(50, now - state.lastTime);
    state.lastTime = now;

    ctx.clearRect(0, 0, state.width, state.height);
    ants.forEach((ant) => updateAnt(ant, dt, now));
    drawSplats();
    ants.forEach(drawAnt);
    updateSplats(dt);
    updateMessages(dt);
    spawnAnts(now);
    updateDebugAttributes();

    window.requestAnimationFrame(frame);
  }

  canvas.addEventListener("pointerdown", (event) => {
    crushAt(event.clientX, event.clientY);
  }, { passive: true });

  window.addEventListener("resize", resize, { passive: true });
  resize();
  seedAnts();
  scheduleSpawn(performance.now());
  window.requestAnimationFrame(frame);
})();
