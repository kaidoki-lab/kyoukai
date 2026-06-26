(function () {
  const shell = document.querySelector("[data-building-stage]");
  const entranceButton = document.querySelector("[data-building-entrance]");
  const elevatorDoor = document.querySelector("[data-elevator-door]");
  const timers = [];

  if (!shell || !entranceButton || !elevatorDoor) return;
  window.KYOUKAI_HOME_JOURNEY_READY = true;

  function showEntrance() {
    if (shell.dataset.buildingStage !== "building") return;
    shell.dataset.buildingStage = "zooming";
    window.setTimeout(() => {
      shell.dataset.buildingStage = "entrance";
      document.querySelector(".kyoukai-building-scene--full")?.setAttribute("aria-hidden", "true");
      document.querySelector(".kyoukai-building-scene--entrance")?.removeAttribute("aria-hidden");
    }, 560);
  }

  function enterElevator(event) {
    event?.preventDefault();
    if (shell.dataset.buildingStage === "entering") return;
    shell.dataset.buildingStage = "entering";
    window.setTimeout(() => {
      window.location.href = elevatorDoor.href;
    }, 360);
  }

  function scheduleAutoJourney() {
    timers.push(window.setTimeout(showEntrance, 760));
    timers.push(window.setTimeout(() => enterElevator(), 1840));
  }

  entranceButton.addEventListener("click", showEntrance);
  elevatorDoor.addEventListener("click", enterElevator);
  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof Element)) return;
    if (target.closest("[data-building-entrance]")) {
      showEntrance();
    }
  });
  scheduleAutoJourney();
})();
