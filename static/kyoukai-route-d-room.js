(function () {
  "use strict";

  var scenario = window.KYOUKAI_SCENARIO;
  var roomId = window.KYOUKAI_ROOM;
  var routeDRooms = ["ripple", "colony", "dot-art", "matsuri", "namahage"];
  if (!scenario || routeDRooms.indexOf(roomId) === -1) return;

  function getTextList(eventData) {
    return (eventData.messages || eventData.conversation || []).map(function (line) {
      return typeof line === "string" ? line : line.text || "";
    }).filter(Boolean);
  }

  function roomRoot() {
    return document.querySelector(".colony-stage, .matsuri-frame, .namahage-frame, canvas, main") || document.body;
  }

  function ensureOverlay(root) {
    var overlay = document.querySelector(".scenario-line-overlay");
    if (overlay) return overlay;
    overlay = document.createElement("div");
    overlay.className = "scenario-line-overlay scenario-line-overlay--route-d";
    overlay.setAttribute("aria-live", "polite");
    document.body.append(overlay);
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
      timer = window.setTimeout(next, 2300);
    }

    overlay.addEventListener("click", next);
    next();
  }

  function makeButton(targetName) {
    var button = document.querySelector('[data-scenario-target="' + targetName + '"]');
    if (button) return button;
    button = document.createElement("button");
    button.type = "button";
    button.className = "route-d-object route-d-object--" + roomId.replace(/[^a-z0-9]/gi, "-");
    button.dataset.scenarioTarget = targetName;
    button.setAttribute("aria-label", targetName);
    document.body.append(button);
    return button;
  }

  function complete(eventData, targetName, root, target) {
    root.dataset.routeDEvent = "";
    document.documentElement.dataset.routeDActiveRoom = "";
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
    var target = makeButton(targetName);
    var requiredCount = Number(eventData.interaction && eventData.interaction.required_count || 1);
    var count = 0;
    if (!root || !target) return;

    target.classList.add("is-scenario-target");
    target.setAttribute("tabindex", target.getAttribute("tabindex") || "0");
    root.dataset.routeDReady = eventData.event_id;

    function run(event) {
      if (event) event.preventDefault();
      var latest = scenario.getActiveRoomEvent(roomId);
      if (!latest || latest.event_id !== eventData.event_id) return;
      if (count === 0) {
        scenario.setRoomEventActive(eventData.event_id);
        root.dataset.routeDEvent = eventData.event_id;
        document.documentElement.dataset.routeDActiveRoom = roomId;
        target.classList.add("is-active");
      }
      count += 1;
      target.dataset.routeDCount = String(count);
      root.dataset.routeDCount = String(count);
      if (count < requiredCount) return;
      target.removeEventListener("click", run);
      target.removeEventListener("keydown", runByKey);
      playLines(root, eventData, function () {
        complete(eventData, targetName, root, target);
      });
    }

    function runByKey(event) {
      if (event.key !== "Enter" && event.key !== " ") return;
      run(event);
    }

    target.addEventListener("click", run);
    target.addEventListener("keydown", runByKey);
  }

  function init() {
    var eventData = scenario.getActiveRoomEvent(roomId);
    if (!eventData) {
      var state = scenario.getState();
      var roomState = state.room_states && state.room_states[roomId];
      if (roomState === "post_route_d") document.documentElement.dataset.routeDTrace = roomId;
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
