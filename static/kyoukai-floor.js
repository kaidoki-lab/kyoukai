(function () {
  const scenario = window.KYOUKAI_SCENARIO;
  const building = window.KYOUKAI_BUILDING || { roomsPerFloor: 5, rooms: [] };
  const roomsPerFloor = Number(building.roomsPerFloor || 5);
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
    object.dataset.material = item.material || "door";

    const mark = document.createElement("span");
    mark.className = "entrance-object__mark";
    mark.textContent = (item.name || "??").slice(0, 2);
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

  function createEmptySlot(slot) {
    const object = document.createElement("span");
    object.className = "entrance-object entrance-object--empty";
    object.dataset.slot = String(slot);

    const visual = document.createElement("span");
    visual.className = "entrance-object__visual";
    visual.append(createFallback({ name: "--", material: "door" }));

    const text = document.createElement("span");
    text.className = "entrance-object__text";
    const name = document.createElement("span");
    name.className = "entrance-object__name";
    name.textContent = "VACANT";
    const label = document.createElement("span");
    label.className = "entrance-object__label";
    label.textContent = `SLOT ${slot}`;
    text.append(name, label);
    object.append(visual, text);
    return object;
  }

  function createEntrance(item) {
    const locked = scenario ? !scenario.canEnterRoom(item.id) : false;
    const state = scenario ? scenario.getState() : {};
    const isTarget = state.current_target_room_id === item.id;
    const link = document.createElement(locked ? "span" : "a");
    link.className = "entrance-object";
    link.dataset.entranceId = item.id;
    link.dataset.floor = String(item.floor);
    link.dataset.slot = String(item.slot);
    link.classList.toggle("is-locked", locked);
    link.classList.toggle("is-scenario-target", isTarget);
    if (isTarget) link.dataset.scenarioTarget = "current";
    if (locked) {
      link.setAttribute("role", "link");
      link.setAttribute("aria-disabled", "true");
    } else {
      link.href = item.href;
    }
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
    label.textContent = locked ? "LOCKED" : item.label;

    text.append(name, label);
    link.append(visual, text);
    return link;
  }

  function roomsForFloor(floorNumber) {
    const floor = Number(floorNumber);
    const floors = scenario ? scenario.groupRoomsByFloor() : {};
    const fromScenario = floors[String(floor).padStart(2, "0")] || [];
    if (fromScenario.some((item) => item && item.topFloorOnly)) {
      return fromScenario.filter(Boolean);
    }
    return Array.from({ length: roomsPerFloor }, (_, index) => fromScenario[index] || null);
  }

  function renderFloor() {
    const shell = document.querySelector("[data-floor-number]");
    const strip = document.querySelector("[data-floor-entrance-strip]");
    if (!shell || !strip) return;

    const floorNumber = shell.dataset.floorNumber || "01";
    const isFloorLocked = scenario ? !scenario.canEnterFloor(floorNumber) : false;
    shell.dataset.floorState = isFloorLocked ? "locked" : "open";
    const items = roomsForFloor(floorNumber).map((item, index) => (
      item && !isFloorLocked ? createEntrance(item) : createEmptySlot(index + 1)
    ));
    strip.replaceChildren(...items);
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

  document.addEventListener("kyoukai:scenario-state", renderFloor);
  window.KYOUKAI_FLOOR_GROUPS = scenario ? scenario.groupRoomsByFloor() : {};
  renderFloor();
  enableEntranceSnap();
  document.documentElement.dataset.hallSound = "ready";
  bindHallSound();
})();
