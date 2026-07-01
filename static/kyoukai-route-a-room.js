(function () {
  "use strict";

  var scenario = window.KYOUKAI_SCENARIO;
  var roomId = window.KYOUKAI_ROOM;
  if (!scenario || ["observation", "signal"].indexOf(roomId) === -1) return;

  function getTextList(eventData) {
    return (eventData.messages || eventData.conversation || []).map(function (line) {
      return typeof line === "string" ? line : line.text || "";
    }).filter(Boolean);
  }

  function ensureOverlay(root) {
    var overlay = root.querySelector(".scenario-line-overlay");
    if (overlay) return overlay;
    overlay = document.createElement("div");
    overlay.className = "scenario-line-overlay";
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
      timer = window.setTimeout(next, eventData.event_id === "route_a_room_signal_001" && index === lines.length ? 1200 : 2200);
    }

    overlay.addEventListener("click", next);
    next();
  }

  function playSignalCue() {
    var AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    try {
      var context = new AudioContext();
      var oscillator = context.createOscillator();
      var gain = context.createGain();
      oscillator.type = "triangle";
      oscillator.frequency.setValueAtTime(roomId === "signal" ? 180 : 260, context.currentTime);
      oscillator.frequency.exponentialRampToValueAtTime(roomId === "signal" ? 86 : 140, context.currentTime + 0.9);
      gain.gain.setValueAtTime(0.0001, context.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.12, context.currentTime + 0.04);
      gain.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + 1.1);
      oscillator.connect(gain);
      gain.connect(context.destination);
      oscillator.start();
      oscillator.stop(context.currentTime + 1.15);
      window.setTimeout(function () {
        context.close().catch(function () {});
      }, 1300);
    } catch (error) {
      console.warn("[KYOUKAI] scenario cue unavailable:", error);
    }
  }

  function pauseSignalVideo() {
    var video = document.getElementById("signalVideo");
    if (!video) return function () {};
    var wasPaused = video.paused;
    video.pause();
    return function () {
      if (!wasPaused) video.play().catch(function () {});
    };
  }

  function bindRoomEvent(eventData) {
    var targetName = eventData.interaction && eventData.interaction.target;
    if (!targetName) return;
    var target = document.querySelector('[data-scenario-target="' + targetName + '"]');
    var root = document.querySelector(".observation-room, .signal-room") || document.body;
    if (!target || !root) return;

    target.classList.add("is-scenario-target");
    target.setAttribute("tabindex", target.getAttribute("tabindex") || "0");
    target.setAttribute("role", target.getAttribute("role") || "button");
    root.dataset.routeAReady = eventData.event_id;

    function run(event) {
      if (event) event.preventDefault();
      var latest = scenario.getActiveRoomEvent(roomId);
      if (!latest || latest.event_id !== eventData.event_id) return;
      target.removeEventListener("click", run);
      target.removeEventListener("keydown", runByKey);
      root.dataset.routeAEvent = eventData.event_id;
      scenario.setRoomEventActive(eventData.event_id);
      var restore = roomId === "signal" ? pauseSignalVideo() : function () {};
      playSignalCue();
      playLines(root, eventData, function () {
        restore();
        root.dataset.routeAEvent = "";
        target.classList.remove("is-scenario-target");
        scenario.completeScenarioEvent(eventData.event_id, {
          interactionTarget: targetName,
          sequenceEventId: eventData.event_id,
        });
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
      if (roomState === "post_route_a") {
        document.documentElement.dataset.routeATrace = roomId;
      }
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
