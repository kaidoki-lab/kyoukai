(function () {
  "use strict";

  var scenario = window.KYOUKAI_SCENARIO;
  var roomId = window.KYOUKAI_ROOM;
  var routeCRooms = ["null", "ma", "particles"];
  if (!scenario || routeCRooms.indexOf(roomId) === -1) return;

  function getTextList(eventData) {
    return (eventData.messages || eventData.conversation || []).map(function (line) {
      return typeof line === "string" ? line : line.text || "";
    }).filter(Boolean);
  }

  function roomRoot() {
    return document.querySelector(".collapse-room, .ma-body, #stage") || document.body;
  }

  function ensureOverlay(root) {
    var overlay = root.querySelector(".scenario-line-overlay");
    if (overlay) return overlay;
    overlay = document.createElement("div");
    overlay.className = "scenario-line-overlay scenario-line-overlay--route-c";
    overlay.setAttribute("aria-live", "polite");
    root.append(overlay);
    return overlay;
  }

  function playLines(root, eventData, done) {
    var overlay = ensureOverlay(root);
    var lines = getTextList(eventData);
    var index = 0;
    var timer = 0;

    function cleanup() {
      overlay.removeEventListener("click", next);
      window.clearTimeout(timer);
    }

    function next() {
      if (index >= lines.length) {
        overlay.classList.remove("is-visible");
        cleanup();
        if (typeof done === "function") done();
        return;
      }
      overlay.textContent = lines[index];
      overlay.classList.add("is-visible");
      index += 1;
      window.clearTimeout(timer);
      timer = window.setTimeout(next, roomId === "ma" ? 2600 : 2300);
    }

    overlay.addEventListener("click", next);
    next();
  }

  function makeButton(targetName) {
    var button = document.querySelector('[data-scenario-target="' + targetName + '"]');
    if (button) return button;
    button = document.createElement("button");
    button.type = "button";
    button.className = "route-c-object";
    button.dataset.scenarioTarget = targetName;
    button.setAttribute("aria-label", targetName);
    document.body.append(button);
    return button;
  }

  function finish(eventData, targetName, root, target) {
    root.dataset.routeCEvent = "";
    target.classList.remove("is-scenario-target", "is-active");
    scenario.completeScenarioEvent(eventData.event_id, {
      interactionTarget: targetName,
      sequenceEventId: eventData.event_id
    });
  }

  function bindRoomEvent(eventData) {
    var targetName = eventData.interaction && eventData.interaction.target;
    if (!targetName) return;
    var root = roomRoot();
    var target = roomId === "ma"
      ? document.getElementById("maPanel") || document.body
      : makeButton(targetName);
    if (!root || !target) return;

    target.classList.add("is-scenario-target");
    target.setAttribute("tabindex", target.getAttribute("tabindex") || "0");
    target.setAttribute("role", target.getAttribute("role") || "button");
    root.dataset.routeCReady = eventData.event_id;

    function run(event) {
      if (event) event.preventDefault();
      var latest = scenario.getActiveRoomEvent(roomId);
      if (!latest || latest.event_id !== eventData.event_id) return;
      target.removeEventListener("click", run);
      target.removeEventListener("keydown", runByKey);
      root.dataset.routeCEvent = eventData.event_id;
      target.classList.add("is-active");
      scenario.setRoomEventActive(eventData.event_id);
      playLines(root, eventData, function () {
        finish(eventData, targetName, root, target);
      });
    }

    function runByKey(event) {
      if (event.key !== "Enter" && event.key !== " ") return;
      run(event);
    }

    target.addEventListener("click", run);
    target.addEventListener("keydown", runByKey);

    if (roomId === "ma") {
      window.setTimeout(run, 500);
    }
  }

  function init() {
    var eventData = scenario.getActiveRoomEvent(roomId);
    if (!eventData) {
      var state = scenario.getState();
      var roomState = state.room_states && state.room_states[roomId];
      if (roomState === "post_route_c") document.documentElement.dataset.routeCTrace = roomId;
      return;
    }
    bindRoomEvent(eventData);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
