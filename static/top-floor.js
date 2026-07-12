(function () {
  "use strict";

  const scenario = window.KYOUKAI_SCENARIO;
  const room = document.querySelector("[data-top-floor-room]");
  const keyholeButton = document.querySelector("[data-top-floor-keyhole]");
  const messageEl = document.querySelector("[data-top-floor-message]");
  const returnLink = document.querySelector("[data-top-floor-return]");
  const MESSAGE_MS = 2600;
  const REPEAT_COOLDOWN_MS = 1300;
  let messageTimer = 0;
  let interactionLock = false;
  let lastRepeatAt = 0;

  function showMessage(text, duration = MESSAGE_MS) {
    if (!messageEl || !text) return;
    window.clearTimeout(messageTimer);
    messageEl.textContent = text;
    messageEl.classList.add("is-visible");
    messageTimer = window.setTimeout(() => {
      messageEl.classList.remove("is-visible");
    }, duration);
  }

  function canUseTopFloor(state) {
    return Boolean(
      state &&
      state.mode === "scenario" &&
      state.active_route_id === "route_e" &&
      state.route_status?.route_e === "active" &&
      state.route_e_phone_completed === true &&
      state.top_floor_unlocked === true &&
      state.ending_completed !== true
    );
  }

  function hasAnnihilationKey(state) {
    return Boolean(scenario?.hasAnnihilationKey?.(state));
  }

  function saveState(mutator) {
    if (!scenario) return null;
    const state = scenario.getState();
    mutator(state);
    return scenario.saveState(state);
  }

  function ensureKeyholeState(state) {
    if (state.top_floor_keyhole_completed === true) return "completed";
    if (state.keyhole_state === "processing") return hasAnnihilationKey(state) ? "ready" : "waiting_for_key";
    if (hasAnnihilationKey(state)) return "ready";
    if (["available", "waiting_for_key", "ready"].includes(state.keyhole_state)) return state.keyhole_state;
    return "available";
  }

  function syncVisuals(state) {
    if (!room || !keyholeButton) return;
    const active = canUseTopFloor(state);
    room.dataset.routeE = active ? "active" : "locked";
    room.dataset.keyholeState = active ? state.keyhole_state || "inactive" : "inactive";
    keyholeButton.disabled = !active || state.keyhole_state === "processing" || state.top_floor_keyhole_completed === true;
    keyholeButton.setAttribute("aria-disabled", keyholeButton.disabled ? "true" : "false");
  }

  function enterTopFloor() {
    if (!scenario) return null;
    let state = scenario.getState();
    if (!canUseTopFloor(state)) {
      syncVisuals(state);
      return state;
    }

    if (state.top_floor_entered !== true) {
      scenario.completeScenarioEvent("route_e_top_floor_enter_001", { sequenceEventId: "route_e_top_floor_enter_001" });
      state = scenario.getState();
    }

    state = saveState((next) => {
      next.top_floor_entered = true;
      next.route_e_stage = next.route_e_stage === "route_e_top_floor_unlocked" ? "top_floor_entered" : next.route_e_stage;
      next.top_floor_keyhole_active = true;
      next.keyhole_interaction_lock = false;
      next.keyhole_state = ensureKeyholeState(next);
    });

    showMessage("最上階", 2200);
    syncVisuals(state);
    return state;
  }

  function markReady() {
    const state = saveState((next) => {
      next.keyhole_state = "ready";
      next.top_floor_keyhole_active = true;
      next.keyhole_interaction_lock = false;
    });
    scenario?.completeScenarioEvent("route_e_keyhole_ready_001", { interactionTarget: "top-floor-keyhole" });
    syncVisuals(state || scenario?.getState());
    startAnnihilationKeyUse();
  }

  function markWaitingWithoutKey(state) {
    scenario?.completeScenarioEvent("route_e_keyhole_touch_without_key_001", {
      interactionTarget: "top-floor-keyhole",
    });
    const next = saveState((current) => {
      current.keyhole_touched = true;
      current.keyhole_touched_without_key = true;
      current.keyhole_state = "waiting_for_key";
      current.top_floor_keyhole_active = true;
      current.keyhole_interaction_lock = false;
    });
    syncVisuals(next || state);
  }

  function touchKeyhole() {
    if (!scenario || interactionLock) return;
    let state = scenario.getState();
    if (!canUseTopFloor(state) || state.top_floor_keyhole_completed === true) return;
    if (state.keyhole_state === "processing") return;
    interactionLock = true;

    if (hasAnnihilationKey(state)) {
      markReady();
      interactionLock = false;
      return;
    }

    if (state.keyhole_touched_without_key === true) {
      const now = Date.now();
      if (now - lastRepeatAt > REPEAT_COOLDOWN_MS) {
        lastRepeatAt = now;
        showMessage("反応はありません。", 1800);
      }
      interactionLock = false;
      return;
    }

    showMessage("形は合っている。", 2100);
    window.setTimeout(() => {
      showMessage("ここには、まだ何もありません。", 2400);
      state = scenario.getState();
      markWaitingWithoutKey(state);
      interactionLock = false;
    }, 850);
  }

  function startAnnihilationKeyUse() {
    document.dispatchEvent(new CustomEvent("kyoukai:route-e-keyhole-ready", {
      detail: { room_id: "top-floor", event_id: "route_e_keyhole_ready_001" },
    }));
    if (typeof window.onKeyholeReady === "function") window.onKeyholeReady();
  }

  window.KYOUKAI_ROUTE_E_TOP_FLOOR = {
    enterTopFloor,
    touchKeyhole,
    startAnnihilationKeyUse,
  };

  keyholeButton?.addEventListener("click", touchKeyhole);
  returnLink?.addEventListener("click", (event) => {
    const state = scenario?.getState();
    if (state?.keyhole_state !== "processing") return;
    event.preventDefault();
  });

  document.addEventListener("kyoukai:scenario-state", (event) => {
    syncVisuals(event.detail || scenario?.getState());
  });

  enterTopFloor();
})();
