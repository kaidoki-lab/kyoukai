(function () {
  const ICON_BASE = "/static/outside/icons/";
  const ICONS = [
    "item_01.png",
    "item_02.png",
    "item_03.png",
    "item_04.png",
    "item_05.png",
    "item_06.png",
    "item_07.png",
    "item_08.png",
    "item_09.png",
    "item_10.png",
    "item_11.png",
    "item_12.png",
    "item_13.png",
    "item_14.png",
    "item_15.png",
    "item_16.png"
  ];
  const MESSAGES = [
    "signal found...",
    "outside connected...",
    "external trace...",
    "connection confirmed...",
    "boundary open..."
  ];
  const BLOCKED_SELECTOR = [
    "a",
    "button",
    "input",
    "textarea",
    "select",
    "iframe",
    "video",
    ".hotspot",
    ".kyoukai-guide",
    ".ky-monetize-route",
    ".signal-tv-screen",
    ".signal-channel-hit",
    ".signal-audio-hit",
    ".archive-card",
    ".archive-rack-hit",
    ".collapse-dpad",
    ".exit-point"
  ].join(",");

  function links() {
    return Array.isArray(window.KYOUKAI_OUTSIDE_AMAZON_LINKS)
      ? window.KYOUKAI_OUTSIDE_AMAZON_LINKS.filter(Boolean)
      : [];
  }

  function randomItem(list) {
    return list[Math.floor(Math.random() * list.length)];
  }

  function rand(min, max) {
    return min + Math.random() * (max - min);
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function currentRoom() {
    return String(window.KYOUKAI_ROOM || document.body.className || location.pathname || "unknown");
  }

  function hotspotCount() {
    const width = window.innerWidth || 1024;
    const height = window.innerHeight || 768;
    if (width < 560 || height < 520) return Math.random() < 0.72 ? 1 : 2;
    return 1 + Math.floor(Math.random() * 3);
  }

  function isBlockedAt(x, y) {
    const probes = [
      [x, y],
      [x - 22, y],
      [x + 22, y],
      [x, y - 22],
      [x, y + 22]
    ];
    return probes.some(([px, py]) => {
      const element = document.elementFromPoint(px, py);
      return Boolean(element && element.closest(BLOCKED_SELECTOR));
    });
  }

  function pickPosition(existing) {
    const width = window.innerWidth || 1024;
    const height = window.innerHeight || 768;
    const marginX = clamp(width * 0.08, 32, 96);
    const marginY = clamp(height * 0.1, 42, 104);

    for (let attempt = 0; attempt < 70; attempt += 1) {
      const x = rand(marginX, width - marginX);
      const y = rand(marginY, height - marginY);
      const tooClose = existing.some((spot) => Math.hypot(spot.x - x, spot.y - y) < 105);
      if (!tooClose && !isBlockedAt(x, y)) return { x, y };
    }

    return {
      x: rand(width * 0.14, width * 0.86),
      y: rand(height * 0.18, height * 0.82)
    };
  }

  function showToast(x, y, text) {
    const toast = document.createElement("div");
    toast.className = "outside-hotspot-toast";
    toast.textContent = text;
    toast.style.left = `${clamp(x + 14, 12, window.innerWidth - 224)}px`;
    toast.style.top = `${clamp(y - 42, 12, window.innerHeight - 58)}px`;
    document.body.appendChild(toast);
    window.setTimeout(() => toast.remove(), 1200);
  }

  function openRandomConnection(button) {
    const pool = links();
    if (!pool.length || button.dataset.connecting === "true") return;
    button.dataset.connecting = "true";
    button.classList.add("is-connecting");

    const rect = button.getBoundingClientRect();
    const target = randomItem(pool);
    showToast(rect.left + rect.width / 2, rect.top + rect.height / 2, randomItem(MESSAGES));

    window.setTimeout(() => {
      window.location.href = target;
    }, 850);
  }

  function createHotspot(position) {
    const button = document.createElement("button");
    const image = document.createElement("img");
    const mark = document.createElement("span");
    const size = rand(window.innerWidth < 620 ? 20 : 24, window.innerWidth < 620 ? 31 : 39);

    button.type = "button";
    button.className = "outside-hotspot";
    button.setAttribute("aria-label", "outside connection");
    button.style.left = `${position.x}px`;
    button.style.top = `${position.y}px`;
    button.style.setProperty("--outside-hotspot-size", `${size}px`);
    button.style.setProperty("--outside-hotspot-opacity", String(rand(0.24, 0.46).toFixed(2)));
    button.style.setProperty("--outside-hotspot-rotation", `${rand(-8, 8).toFixed(1)}deg`);

    image.className = "outside-hotspot__image";
    image.src = ICON_BASE + randomItem(ICONS);
    image.alt = "";
    image.loading = "lazy";
    mark.className = "outside-hotspot__mark";
    mark.textContent = "PR";
    button.appendChild(image);
    button.appendChild(mark);
    button.addEventListener("click", () => openRandomConnection(button));
    return button;
  }

  function renderHotspots() {
    if (document.querySelector(".outside-hotspot-layer")) return;
    if (document.body.dataset.outsideHotspots === "off") return;
    if (location.pathname === "/outside" || currentRoom().indexOf("outside") >= 0) return;
    if (!links().length) return;

    const layer = document.createElement("div");
    const positions = [];
    layer.className = "outside-hotspot-layer";
    layer.setAttribute("aria-hidden", "false");

    for (let index = 0; index < hotspotCount(); index += 1) {
      const position = pickPosition(positions);
      positions.push(position);
      layer.appendChild(createHotspot(position));
    }

    document.body.appendChild(layer);
  }

  function scheduleRender() {
    window.setTimeout(renderHotspots, 360);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", scheduleRender, { once: true });
  } else {
    scheduleRender();
  }
})();
