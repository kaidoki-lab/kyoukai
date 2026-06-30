(function () {
  const room = document.querySelector("[data-elevator-room]");
  const frames = Array.from(document.querySelectorAll("[data-door-frame]"));
  const cabin = document.querySelector("[data-floor-index]");
  const floorNumber = document.querySelector("[data-floor-number]");
  const enterButton = document.querySelector("[data-floor-enter]");
  const upButton = document.querySelector("[data-floor-up]");
  const downButton = document.querySelector("[data-floor-down]");
  const sequence = ["4", "3", "2", "1"];
  const doorFrameIntervalMs = 740;
  const scenario = window.KYOUKAI_SCENARIO;
  const building = window.KYOUKAI_BUILDING || { rooms: [], initialScenarioFloors: 3 };
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

  if (!room || frames.length === 0 || !cabin || !floorNumber || !enterButton || !upButton || !downButton) return;

  function floorKey(floor) {
    return String(floor).padStart(2, "0");
  }

  function getRooms() {
    return scenario ? scenario.getRooms() : [];
  }

  function getFloors() {
    const maxRoomFloor = getRooms().reduce((max, item) => Math.max(max, item.floor), 1);
    const maxFloor = Math.max(maxRoomFloor, Number(building.initialScenarioFloors || 3));
    return Array.from({ length: maxFloor }, (_, index) => {
      const floor = index + 1;
      const number = floorKey(floor);
      const locked = scenario ? !scenario.canEnterFloor(number) : false;
      return {
        number,
        display: floor === 1 ? "M" : number,
        href: `/floor/${number}`,
        label: locked ? "LOCKED" : "FLOOR",
        locked,
      };
    });
  }

  function showFrame(frameId) {
    frames.forEach((frame) => {
      frame.classList.toggle("is-active", frame.dataset.doorFrame === frameId);
    });
  }

  function updateFloor(index) {
    const floors = getFloors();
    const nextIndex = Math.max(0, Math.min(floors.length - 1, index));
    const floor = floors[nextIndex];
    cabin.dataset.floorIndex = String(nextIndex);
    floorNumber.textContent = floor.display || floor.number;
    enterButton.dataset.floorHref = floor.href;
    enterButton.disabled = Boolean(floor.locked);
    enterButton.classList.toggle("is-locked", Boolean(floor.locked));
    enterButton.setAttribute("aria-label", `${floor.label} ${floor.number}`);
  }

  function playDoorSequence() {
    room.dataset.doorState = "playing";
    sequence.forEach((frameId, index) => {
      window.setTimeout(() => {
        showFrame(frameId);
        if (index === sequence.length - 1) {
          room.dataset.doorState = "complete";
        }
      }, index * doorFrameIntervalMs);
    });
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

  upButton.addEventListener("click", () => {
    updateFloor(Number(cabin.dataset.floorIndex || 0) + 1);
  });

  downButton.addEventListener("click", () => {
    updateFloor(Number(cabin.dataset.floorIndex || 0) - 1);
  });

  enterButton.addEventListener("click", () => {
    const floors = getFloors();
    const floor = floors[Number(cabin.dataset.floorIndex || 0)];
    if (floor && floor.locked) return;
    const href = enterButton.dataset.floorHref;
    if (href) window.location.href = href;
  });

  document.addEventListener("kyoukai:scenario-state", () => {
    updateFloor(Number(cabin.dataset.floorIndex || 0));
  });

  updateFloor(0);
  document.documentElement.dataset.hallSound = "ready";
  ["pointerdown", "keydown", "touchstart"].forEach((eventName) => {
    document.addEventListener(eventName, startHallSound, { once: true, passive: true });
  });
  window.addEventListener("pagehide", stopHallSound);
  window.KYOUKAI_HALL_SOUND = { start: startHallSound, stop: stopHallSound };

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    showFrame(sequence[sequence.length - 1]);
    room.dataset.doorState = "complete";
    return;
  }

  window.setTimeout(playDoorSequence, 180);
})();
