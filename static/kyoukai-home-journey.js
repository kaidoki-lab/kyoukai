(function () {
  const shell = document.querySelector("[data-building-stage]");
  const entranceButton = document.querySelector("[data-building-entrance]");
  const elevatorDoor = document.querySelector("[data-elevator-door]");

  if (!shell || !entranceButton || !elevatorDoor) return;
  window.KYOUKAI_HOME_JOURNEY_READY = true;

  function showEntrance() {
    if (shell.dataset.buildingStage !== "building") return;
    shell.dataset.buildingStage = "zooming";
    window.setTimeout(() => {
      shell.dataset.buildingStage = "entrance";
      document.querySelector(".kyoukai-building-scene--full")?.setAttribute("aria-hidden", "true");
      document.querySelector(".kyoukai-building-scene--entrance")?.removeAttribute("aria-hidden");
      elevatorDoor.focus({ preventScroll: true });
    }, 560);
  }

  function enterElevator(event) {
    event.preventDefault();
    shell.dataset.buildingStage = "entering";
    window.setTimeout(() => {
      window.location.href = elevatorDoor.href;
    }, 360);
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
})();
