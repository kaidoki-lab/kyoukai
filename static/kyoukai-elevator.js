(function () {
  const room = document.querySelector("[data-elevator-room]");
  const frames = Array.from(document.querySelectorAll("[data-door-frame]"));
  const sequence = ["4", "3", "2", "1"];

  if (!room || frames.length === 0) return;

  function showFrame(frameId) {
    frames.forEach((frame) => {
      frame.classList.toggle("is-active", frame.dataset.doorFrame === frameId);
    });
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

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    showFrame(sequence[sequence.length - 1]);
    room.dataset.doorState = "complete";
    return;
  }

  window.setTimeout(playDoorSequence, 180);
})();
