(function () {
  const floorGroups = {
    "01": [
      { id: "kanrinin", name: "管理人室", label: "MGR", href: "/kanrinin", image: "/static/images/entrances/entrance-kanrinin.png", material: "door" },
    ],
    "02": [
      { id: "observation", name: "observation", label: "OBS", href: "/observation", image: "/static/images/entrances/entrance-observation.png", material: "mirror" },
      { id: "observer", name: "observer", label: "OBR", href: "/observer", image: "/static/images/entrances/entrance-observer.png", material: "shrine" },
      { id: "archive", name: "archive", label: "ARC", href: "/archive", image: "/static/images/entrances/entrance-archive.png", material: "box" },
    ],
    "03": [
      { id: "signal", name: "signal", label: "SIG", href: "/signal", image: "/static/images/entrances/entrance-signal.png", material: "speaker" },
      { id: "news", name: "news", label: "NEWS", href: "/typhoon-news/", image: "/static/images/entrances/news.png", material: "door" },
      { id: "daimyojin", name: "daimyojin", label: "DMJ", href: "/daimyojin", image: "/static/images/entrances/entrance-daimyojin.png", material: "shrine" },
    ],
    "04": [
      { id: "hyougi", name: "hyougi", label: "HYO", href: "/hyougi", image: "/static/images/entrances/entrance-hyougi.png", material: "paper" },
      { id: "gokuraku", name: "gokuraku", label: "GOK", href: "/gokuraku", image: "/static/images/entrances/entrance-gokuraku.png", material: "shrine" },
      { id: "exit", name: "exit", label: "EXT", href: "/exit", image: "/static/images/entrances/entrance-exit.png", material: "door" },
    ],
    "05": [
      { id: "null", name: "null", label: "NUL", href: "/null", image: "/static/images/entrances/entrance-null.png", material: "crack" },
      { id: "ma", name: "ma", label: "MA", href: "/ma", image: "/static/images/entrances/entrance-ma.png", material: "mirror" },
      { id: "particles", name: "particles", label: "PRT", href: "/particles", image: "/static/images/entrances/entrance-particles.png?v=20260625c", material: "mirror" },
    ],
    "06": [
      { id: "ripple", name: "ripple", label: "RPL", href: "/ripple", image: "/static/images/entrances/entrance-ripple.png?v=20260625b", material: "crack" },
      { id: "colony", name: "COLONY", label: "COL", href: "/colony", image: "/static/images/colony/entrance-colony.png", material: "crack" },
      { id: "dot-art", name: "dot-art", label: "DOT", href: "/dot-art", image: "/static/entrance-dot-art.png", material: "crack" },
    ],
  };
  const hallTracks = [
    "/static/bgm/bgm_home.mp3",
    "/static/bgm/bgm_exit.mp3",
    "/static/bgm/bgm_null.mp3",
    "/static/bgm/bgm_observer.mp3",
  ];
  const hallSoundVolume = 0.018;
  let hallNode = null;
  let hallTrackIndex = 0;
  let hallStarted = false;

  function createFallback(item) {
    const object = document.createElement("span");
    object.className = "entrance-object__fallback";
    object.dataset.material = item.material;

    const mark = document.createElement("span");
    mark.className = "entrance-object__mark";
    mark.textContent = item.name.slice(0, 2);
    object.append(mark);
    return object;
  }

  function createImage(item) {
    if (!item.image) return createFallback(item);
    const image = document.createElement("img");
    image.src = item.image;
    image.alt = "";
    image.loading = "lazy";
    image.decoding = "async";
    image.addEventListener("error", () => image.replaceWith(createFallback(item)), { once: true });
    return image;
  }

  function createEntrance(item) {
    const link = document.createElement("a");
    link.className = "entrance-object";
    link.href = item.href;
    link.dataset.entranceId = item.id;
    link.setAttribute("aria-label", `${item.name} ${item.label}`);

    const visual = document.createElement("span");
    visual.className = "entrance-object__visual";
    visual.append(createImage(item));

    const text = document.createElement("span");
    text.className = "entrance-object__text";

    const name = document.createElement("span");
    name.className = "entrance-object__name";
    name.textContent = item.name;

    const label = document.createElement("span");
    label.className = "entrance-object__label";
    label.textContent = item.label;

    text.append(name, label);
    link.append(visual, text);
    return link;
  }

  function renderFloor() {
    const shell = document.querySelector("[data-floor-number]");
    const strip = document.querySelector("[data-floor-entrance-strip]");
    if (!shell || !strip) return;

    const floorNumber = shell.dataset.floorNumber || "01";
    const items = floorGroups[floorNumber] || floorGroups["01"];
    strip.replaceChildren(...items.map(createEntrance));
  }

  function calibrateEntranceStrip(strip) {
    const cardWidth = Math.round(strip.clientWidth * 0.74);
    const edgeSpace = Math.max(0, Math.round((strip.clientWidth - cardWidth) / 2));
    strip.style.setProperty("--entrance-card-width", `${cardWidth}px`);
    strip.style.setProperty("--entrance-edge-space", `${edgeSpace}px`);
  }

  function getEntrances(strip) {
    return Array.from(strip.querySelectorAll(".entrance-object"));
  }

  function nearestEntranceIndex(strip) {
    const items = getEntrances(strip);
    const center = strip.scrollLeft + strip.clientWidth / 2;
    return items.reduce((nearest, item, index) => {
      const itemCenter = item.offsetLeft + item.offsetWidth / 2;
      const distance = Math.abs(itemCenter - center);
      if (!nearest || distance < nearest.distance) return { index, distance };
      return nearest;
    }, null)?.index ?? 0;
  }

  function snapEntranceIntoCenter(strip, index, behavior = "smooth") {
    const items = getEntrances(strip);
    const item = items[index];
    if (!item) return;

    const targetLeft = item.offsetLeft + item.offsetWidth / 2 - strip.clientWidth / 2;
    strip.scrollTo({ left: Math.max(0, targetLeft), behavior });
    item.classList.remove("is-snap-bump");
    void item.offsetWidth;
    item.classList.add("is-snap-bump");
  }

  function enableEntranceSnap() {
    const strip = document.querySelector("[data-floor-entrance-strip]");
    if (!strip) return;

    let timer = 0;
    let interactionStartIndex = 0;
    let interactionStartLeft = strip.scrollLeft;
    let isSnapping = false;

    calibrateEntranceStrip(strip);

    const rememberStart = () => {
      if (isSnapping) return;
      interactionStartIndex = nearestEntranceIndex(strip);
      interactionStartLeft = strip.scrollLeft;
    };

    const settle = () => {
      if (isSnapping) return;
      const items = getEntrances(strip);
      if (!items.length) return;

      const direction = Math.sign(strip.scrollLeft - interactionStartLeft);
      const nearestIndex = nearestEntranceIndex(strip);
      let targetIndex = nearestIndex;
      if (direction !== 0) {
        const nextIndex = Math.max(0, Math.min(items.length - 1, interactionStartIndex + direction));
        targetIndex = direction > 0
          ? Math.min(nearestIndex, nextIndex)
          : Math.max(nearestIndex, nextIndex);
      }

      isSnapping = true;
      snapEntranceIntoCenter(strip, targetIndex);
      window.setTimeout(() => {
        interactionStartIndex = targetIndex;
        interactionStartLeft = strip.scrollLeft;
        isSnapping = false;
      }, 360);
    };

    ["pointerdown", "touchstart", "wheel", "keydown"].forEach((eventName) => {
      strip.addEventListener(eventName, rememberStart, { passive: true });
    });

    strip.addEventListener("scroll", () => {
      window.clearTimeout(timer);
      timer = window.setTimeout(settle, 120);
    }, { passive: true });

    window.addEventListener("resize", () => {
      calibrateEntranceStrip(strip);
      snapEntranceIntoCenter(strip, nearestEntranceIndex(strip), "auto");
    }, { passive: true });

    requestAnimationFrame(() => snapEntranceIntoCenter(strip, nearestEntranceIndex(strip), "auto"));
  }

  function startHallSound() {
    if (hallStarted) return;
    hallStarted = true;
    document.documentElement.dataset.hallSound = "playing";
    hallNode = new Audio(hallTracks[hallTrackIndex]);
    hallNode.preload = "auto";
    hallNode.volume = hallSoundVolume;
    hallNode.addEventListener("ended", () => {
      hallTrackIndex = (hallTrackIndex + 1) % hallTracks.length;
      hallNode.src = hallTracks[hallTrackIndex];
      hallNode.play().catch(() => {});
    });
    hallNode.play().catch(() => {});
  }

  function stopHallSound() {
    document.documentElement.dataset.hallSound = "stopped";
    if (!hallNode) return;
    hallNode.pause();
    hallNode.currentTime = 0;
  }

  function bindHallSound() {
    ["pointerdown", "keydown", "touchstart"].forEach((eventName) => {
      document.addEventListener(eventName, startHallSound, { once: true, passive: true });
    });
    document.addEventListener("click", (event) => {
      const target = event.target;
      if (!(target instanceof Element)) return;
      if (target.closest("[data-floor-entrance-strip] .entrance-object")) {
        stopHallSound();
      }
    });
    window.addEventListener("pagehide", stopHallSound);
    window.KYOUKAI_HALL_SOUND = { start: startHallSound, stop: stopHallSound };
  }

  window.KYOUKAI_FLOOR_GROUPS = floorGroups;
  renderFloor();
  enableEntranceSnap();
  document.documentElement.dataset.hallSound = "ready";
  bindHallSound();
})();
