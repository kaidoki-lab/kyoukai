(function () {
  const room = document.querySelector("[data-elevator-room]");
  const frames = Array.from(document.querySelectorAll("[data-door-frame]"));
  const cabin = document.querySelector("[data-floor-index]");
  const floorNumber = document.querySelector("[data-floor-number]");
  const enterButton = document.querySelector("[data-floor-enter]");
  const upButton = document.querySelector("[data-floor-up]");
  const downButton = document.querySelector("[data-floor-down]");
  const sequence = ["4", "3", "2", "1"];
  const floors = [
    { number: "01", href: "/observation", label: "OBS" },
    { number: "02", href: "/observer", label: "OBR" },
    { number: "03", href: "/archive", label: "ARC" },
    { number: "04", href: "/signal", label: "SIG" },
    { number: "05", href: "/hyougi", label: "HYO" },
    { number: "06", href: "/gokuraku", label: "GOK" },
    { number: "07", href: "/exit", label: "EXT" },
    { number: "08", href: "/null", label: "NUL" },
    { number: "09", href: "/daimyojin", label: "DMJ" },
    { number: "10", href: "/ma", label: "MA" },
    { number: "11", href: "/particles", label: "PRT" },
    { number: "12", href: "/ripple", label: "RPL" },
    { number: "13", href: "/dot-art", label: "DOT" },
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
    enterButton.setAttribute("aria-label", `${floor.number} ${floor.label}へ`);
  }

  function playDoorSequence() {
    room.dataset.doorState = "playing";
    sequence.forEach((frameId, index) => {
      window.setTimeout(() => {
        showFrame(frameId);
        if (index === sequence.length - 1) {
          room.dataset.doorState = "complete";
        }
      }, index * 240);
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
