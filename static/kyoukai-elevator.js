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
  const floors = [
    { number: "01", href: "/floor/01", label: "FLOOR" },
    { number: "02", href: "/floor/02", label: "FLOOR" },
    { number: "03", href: "/floor/03", label: "FLOOR" },
    { number: "04", href: "/floor/04", label: "FLOOR" },
    { number: "05", href: "/floor/05", label: "FLOOR" },
  ];

  if (!room || frames.length === 0 || !cabin || !floorNumber || !enterButton || !upButton || !downButton) return;

  function showFrame(frameId) {
    frames.forEach((frame) => {
      frame.classList.toggle("is-active", frame.dataset.doorFrame === frameId);
    });
  }

  function updateFloor(index) {
    const nextIndex = Math.max(0, Math.min(floors.length - 1, index));
    const floor = floors[nextIndex];
    cabin.dataset.floorIndex = String(nextIndex);
    floorNumber.textContent = floor.number;
    enterButton.dataset.floorHref = floor.href;
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

  upButton.addEventListener("click", () => {
    updateFloor(Number(cabin.dataset.floorIndex || 0) + 1);
  });

  downButton.addEventListener("click", () => {
    updateFloor(Number(cabin.dataset.floorIndex || 0) - 1);
  });

  enterButton.addEventListener("click", () => {
    const href = enterButton.dataset.floorHref;
    if (href) window.location.href = href;
  });

  updateFloor(0);

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    showFrame(sequence[sequence.length - 1]);
    room.dataset.doorState = "complete";
    return;
  }

  window.setTimeout(playDoorSequence, 180);
})();
