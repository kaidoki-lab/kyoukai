const state = {
  socket: null,
  genome: null,
  creature: null,
  summary: null,
  impulse: 0,
  lastMutationEventId: 0,
  lastPhaseUpEventId: 0,
  contaminationTimer: null,
  observationStartedAt: Date.now(),
  audio: {
    context: null,
    timer: null,
    enabled: false,
  },
};

const elements = {
  facility: document.querySelector("#facility"),
  connectionStatus: document.querySelector("#connectionStatus"),
  observerCount: document.querySelector("#observerCount"),
  observerCountInline: document.querySelector("#observerCountInline"),
  phase: document.querySelector("#phase"),
  stability: document.querySelector("#stability"),
  mutationLevel: document.querySelector("#mutationLevel"),
  mutationCount: document.querySelector("#mutationCount"),
  mutationCountInline: document.querySelector("#mutationCountInline"),
  instability: document.querySelector("#instability"),
  noiseLevel: document.querySelector("#noiseLevel"),
  tempo: document.querySelector("#tempo"),
  mood: document.querySelector("#mood"),
  eventBand: document.querySelector("#eventBand"),
  dominantTrait: document.querySelector("#dominantTrait"),
  lastMutation: document.querySelector("#lastMutation"),
  phaseDrift: document.querySelector("#phaseDrift"),
  silentObservation: document.querySelector("#silentObservation"),
  boundaryPressure: document.querySelector("#boundaryPressure"),
  audioInstability: document.querySelector("#audioInstability"),
  visualInstability: document.querySelector("#visualInstability"),
  lastAction: document.querySelector("#lastAction"),
  audioParams: document.querySelector("#audioParams"),
  observationActive: document.querySelector("#observationActive"),
  signalPing: document.querySelector("#signalPing"),
  logList: document.querySelector("#logList"),
  form: document.querySelector("#actionForm"),
  input: document.querySelector("#actionInput"),
  audioToggle: document.querySelector("#audioToggle"),
  signalsList: document.querySelector("#signalsList"),
  contaminationOverlay: document.querySelector("#contaminationOverlay"),
  contaminationText: document.querySelector("#contaminationText"),
  contaminationLink: document.querySelector("#contaminationLink"),
  creature: document.querySelector("#creature"),
  bodyShape: document.querySelector("#bodyShape"),
  core: document.querySelector("#core"),
  organLeft: document.querySelector("#organLeft"),
  organRight: document.querySelector("#organRight"),
  organCrown: document.querySelector("#organCrown"),
  organTail: document.querySelector("#organTail"),
  creatureName: document.querySelector("#creatureName"),
  creatureSpecies: document.querySelector("#creatureSpecies"),
  creaturePanelName: document.querySelector("#creaturePanelName"),
  creatureBranch: document.querySelector("#creatureBranch"),
  creatureVariant: document.querySelector("#creatureVariant"),
  creatureCore: document.querySelector("#creatureCore"),
  creatureShell: document.querySelector("#creatureShell"),
  creatureOrgansText: document.querySelector("#creatureOrgansText"),
  creatureDanger: document.querySelector("#creatureDanger"),
  turbulence: document.querySelector("#turbulence"),
  displace: document.querySelector("#displace"),
  totalVisits: document.querySelector("#totalVisits"),
};

function setText(element, value) {
  if (element) element.textContent = value;
}

function connect() {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  state.socket = new WebSocket(`${protocol}://${window.location.host}/ws`);

  state.socket.addEventListener("open", () => {
    setText(elements.connectionStatus, "接続中");
    elements.connectionStatus?.classList.add("live");
  });

  state.socket.addEventListener("message", (event) => {
    const payload = JSON.parse(event.data);
    if (payload.type !== "genome") return;
    const configuredSignals = (payload.affiliate_panel || []).filter(isConfiguredSignal);
    renderGenome(payload.genome, payload.genome_summary || payload.genome.genome_summary || {});
    renderCreature(payload.creature);
    renderSignalsPanel((payload.affiliate_panel || []).filter((signal) => !signal.is_affiliate));
    renderSignalBanners(configuredSignals, payload.genome, payload.genome_summary || {});
    const configuredPopups = (payload.affiliate_popup || []).filter(isConfiguredSignal);
    if (configuredPopups.length) {
      state.pendingPopupSignals = configuredPopups;
    }
  });

  state.socket.addEventListener("close", () => {
    setText(elements.connectionStatus, "切断");
    elements.connectionStatus?.classList.remove("live");
    window.setTimeout(connect, 1500);
  });
}

function isConfiguredSignal(signal) {
  return signal?.is_affiliate && signal?.affiliate_provider === "A8" && !String(signal.url || "").includes("YOUR_A8_CODE");
}

function renderGenome(genome, summary) {
  const previousAction = state.genome?.last_action;
  const previousMutation = state.genome?.last_mutation_type;
  state.genome = genome;
  state.summary = summary;

  setText(elements.observerCount, genome.observer_count);
  setText(elements.observerCountInline, genome.observer_count);
  setText(elements.phase, genome.phase);
  setText(elements.stability, genome.stability);
  setText(elements.mutationLevel, genome.mutation_level);
  setText(elements.mutationCount, genome.mutation_count ?? 0);
  setText(elements.mutationCountInline, genome.mutation_count ?? 0);
  setText(elements.instability, summary.instability ?? 0);
  setText(elements.noiseLevel, genome.noise_level);
  setText(elements.tempo, genome.tempo);
  setText(elements.mood, genome.mood);
  setText(elements.dominantTrait, (summary.dominant_trait || "none").toUpperCase());
  setText(elements.lastMutation, (summary.current_mutation || genome.last_mutation_type || "none").toUpperCase());
  setText(elements.phaseDrift, genome.phase_drift ?? 0);
  setText(elements.silentObservation, genome.silent_observation ?? 0);
  setText(elements.boundaryPressure, genome.boundary_pressure ?? 0);
  setText(elements.audioInstability, genome.audio_instability ?? 0);
  setText(elements.visualInstability, genome.visual_instability ?? 0);
  setText(elements.lastAction, genome.last_action || "-");
  setText(elements.audioParams, `${summary.audio_mode || "baseline"} / tempo ${genome.tempo} / noise ${genome.noise_level}`);
  document.querySelector("#signalsSection")?.setAttribute("data-phase", String(genome.phase));
  renderObservationRuntime(genome, summary);
  renderStatStates(genome, summary);

  const mutation = summary.current_mutation || genome.last_mutation_type || "none";
  const trait = summary.dominant_trait || "none";
  document.body.dataset.mood = genome.mood;
  document.body.dataset.trait = trait;
  document.body.dataset.mutation = mutation;
  document.body.dataset.phase = String(genome.phase);
  setClassGroup(document.body, "phase-", `phase-${genome.phase}`);
  setClassGroup(document.body, "trait-", `trait-${trait}`);
  setClassGroup(document.body, "mutation-", `mutation-${mutation.replaceAll("_", "-")}`);

  updateCreature(genome, summary);
  renderLogs(genome.log_history || [], genome.noise_level, genome.phase_drift ?? 0);

  const eventId = summary.mutation_event_id ?? genome.mutation_event_id ?? 0;
  if (eventId !== state.lastMutationEventId && eventId > 0) {
    state.lastMutationEventId = eventId;
    triggerMutationFlash(mutation);
  } else if ((previousAction !== genome.last_action && genome.last_action) || previousMutation !== genome.last_mutation_type) {
    triggerMutationFlash(mutation, 520);
  }

  const phaseUpId = genome.phase_up_event_id ?? 0;
  if (phaseUpId !== state.lastPhaseUpEventId && phaseUpId > 0) {
    state.lastPhaseUpEventId = phaseUpId;
    triggerPhaseUpFlash();
  }

  setText(elements.totalVisits, genome.total_visits ?? 0);

  if (state.audio.enabled) scheduleBioSound();
}

function updateCreature(genome, summary) {
  if (!elements.facility || !elements.bodyShape || !elements.core) return;
  const softness = genome.trait_softness ?? 0;
  const aggression = genome.trait_aggression ?? 0;
  const gaze = genome.trait_gaze ?? 0;
  const distance = genome.trait_distance ?? 0;
  const corruption = genome.trait_corruption ?? 0;
  const phaseHue = (176 + genome.phase * 22 + (genome.phase_drift ?? 0) * 2 + corruption) % 360;
  const instability = summary.instability ?? 100 - genome.stability;
  const saturation = Math.min(98, 48 + genome.mutation_level + genome.boundary_pressure / 2 + corruption);
  const light = Math.max(34, 70 - genome.noise_level / 3 + softness / 8);
  const breath = Math.max(0.95, 5.25 - genome.tempo / 42);
  const shake = Math.min(16, instability / 9 + genome.noise_level / 18 + aggression / 8);
  const displacement = 2 + genome.mutation_level / 5 + genome.noise_level / 16 + corruption / 5;
  const noiseFrequency = 0.01 + genome.noise_level / 760 + genome.observer_count / 1200 + corruption / 3000;

  elements.facility.style.setProperty("--noise-opacity", String(Math.min(0.42, 0.08 + genome.noise_level / 240 + corruption / 420)));
  elements.facility.style.setProperty("--shake", `${shake}px`);
  elements.facility.style.setProperty("--shake-x", `${Math.sin(phaseHue / 18) * shake}px`);
  elements.facility.style.setProperty("--shake-y", `${Math.cos(phaseHue / 21) * shake * 0.45}px`);
  elements.facility.style.setProperty("--breath", `${breath}s`);
  elements.facility.style.setProperty("--phase-hue", `${phaseHue}`);
  elements.facility.style.setProperty("--core-scale", String(0.9 + gaze / 90 + genome.phase_drift / 180));
  elements.bodyShape.style.fill = `hsl(${phaseHue} ${saturation}% ${light}%)`;
  elements.core.style.fill = `hsl(${(phaseHue + 38 + gaze) % 360} 92% ${Math.max(56, light)}%)`;
  elements.bodyShape.style.transform = `rotate(${(genome.phase - 1) * 2 + genome.phase_drift / 12}deg) scale(${Math.max(0.86, 1 - distance / 120)})`;
  if (elements.creature) elements.creature.style.animationDuration = `${breath}s`;
  elements.turbulence?.setAttribute("baseFrequency", String(noiseFrequency));
  elements.displace?.setAttribute("scale", String(displacement));
}

const bodyPlanPaths = {
  larva_soft: "M130 42 C172 42 207 82 207 132 C207 189 176 224 130 224 C84 224 53 189 53 132 C53 82 88 42 130 42 Z",
  spiked_predator: "M130 30 L151 58 L188 47 L184 88 L221 108 L190 134 L204 184 L158 181 L130 232 L102 181 L56 184 L70 134 L39 108 L76 88 L72 47 L109 58 Z",
  tentacled: "M130 54 C178 54 203 88 194 130 C186 166 207 204 177 221 C154 235 148 201 130 201 C112 201 106 235 83 221 C53 204 74 166 66 130 C57 88 82 54 130 54 Z",
  rift_serpent: "M80 52 C156 31 218 72 190 125 C172 159 116 141 107 177 C101 203 135 221 164 203 C142 235 91 235 66 200 C39 162 82 139 114 129 C153 116 173 77 80 52 Z",
  raptor: "M125 35 C174 43 204 83 191 124 C219 140 215 184 174 180 C159 215 104 226 83 190 C51 184 49 142 78 126 C60 78 84 42 125 35 Z",
  many_eyed: "M130 38 C184 38 217 81 217 131 C217 188 181 226 130 226 C79 226 43 188 43 131 C43 81 76 38 130 38 Z",
  cathedral_throat: "M130 35 C179 35 214 72 214 122 C214 181 181 229 130 229 C79 229 46 181 46 122 C46 72 81 35 130 35 Z M89 156 C111 136 149 136 171 156 C157 189 104 189 89 156 Z",
  void_leviathan: "M44 130 C74 43 180 31 216 93 C244 142 196 209 125 226 C152 190 147 155 112 150 C84 146 62 159 44 130 Z",
  amorphous: "M127 43 C169 24 214 69 202 112 C239 153 194 229 143 213 C102 246 33 203 60 153 C23 107 77 34 127 43 Z",
  eye_cathedral: "M130 25 C166 61 198 52 214 101 C192 119 205 168 175 201 C150 188 119 237 88 204 C108 174 54 164 47 117 C82 112 78 62 130 25 Z",
  halo_titan: "M130 26 C189 26 229 75 229 132 C229 197 188 238 130 238 C72 238 31 197 31 132 C31 75 71 26 130 26 Z M84 76 C110 57 151 57 176 76",
};

function renderCreature(creature) {
  if (!creature || creature.available === false) return;
  state.creature = creature;
  const bodyPlan = String(creature.body_plan || creature.silhouette || "larva_soft");
  const branch = String(creature.branch || "none");
  const variant = String(creature.variant || "normal");
  const danger = Number(creature.danger || 0);
  const organs = Array.isArray(creature.organs) ? creature.organs : [];
  const path = bodyPlanPaths[bodyPlan] || bodyPlanPaths.larva_soft;

  elements.bodyShape?.setAttribute("d", path);
  setText(elements.creatureName, creature.name || "Unknown Organism");
  setText(elements.creatureSpecies, creature.species_id || "U-00000000");
  setText(elements.creaturePanelName, creature.name || "Unknown Organism");
  setText(elements.creatureBranch, branch.toUpperCase());
  setText(elements.creatureVariant, variant.toUpperCase());
  setText(elements.creatureCore, creature.core || "unknown");
  setText(elements.creatureShell, creature.shell || "unknown");
  setText(elements.creatureOrgansText, organs.slice(0, 3).join(" / ") || "none");
  setText(elements.creatureDanger, danger);

  document.body.dataset.creatureBranch = branch;
  document.body.dataset.creatureVariant = variant;
  if (elements.facility) {
    elements.facility.dataset.bodyPlan = bodyPlan;
    elements.facility.style.setProperty("--creature-danger", String(Math.min(1, danger / 40)));
  }

  const organText = organs.join(" ").toLowerCase();
  elements.organLeft?.classList.toggle("is-active", /wing|antenna|tentacle|antler|spike|crown/.test(organText));
  elements.organRight?.classList.toggle("is-active", /wing|antenna|tentacle|antler|spike|crown/.test(organText));
  elements.organCrown?.classList.toggle("is-active", /crown|antler|halo|eye/.test(organText) || branch === "attention");
  elements.organTail?.classList.toggle("is-active", /tentacle|spine|limb|asymmetry/.test(organText) || branch === "chaos");
}

function renderObservationRuntime(genome, summary) {
  const sessionSeconds = Math.floor((Date.now() - state.observationStartedAt) / 1000);
  const seconds = Math.max(0, Math.floor(Number(genome.stay_time || 0)) + sessionSeconds);
  const hours = String(Math.floor(seconds / 3600)).padStart(3, "0");
  const minutes = String(Math.floor((seconds % 3600) / 60)).padStart(2, "0");
  const secs = String(seconds % 60).padStart(2, "0");
  setText(elements.observationActive, `${hours}:${minutes}:${secs}`);
  const ping = Math.max(7, Math.round(120 - Number(genome.stability || 0) + Number(summary.instability || 0)));
  setText(elements.signalPing, `signal ping ${ping}ms`);
}

function renderStatStates(genome, summary) {
  const stateMap = [
    [elements.phaseDrift, genome.phase_drift, ["signal", 20, 55]],
    [elements.stability, 100 - Number(genome.stability || 0), ["stable", 18, 48]],
    [elements.mutationLevel, genome.mutation_level, ["stable", 3, 8]],
    [elements.mutationCount, genome.mutation_count, ["stable", 2, 7]],
    [elements.noiseLevel, genome.noise_level, ["stable", 35, 70]],
    [elements.instability, summary.instability, ["stable", 35, 68]],
    [elements.audioInstability, genome.audio_instability, ["stable", 35, 70]],
    [elements.visualInstability, genome.visual_instability, ["stable", 35, 70]],
    [elements.observerCount, genome.observer_count, ["signal", 3, 12]],
    [elements.silentObservation, genome.silent_observation, ["signal", 12, 36]],
    [elements.boundaryPressure, genome.boundary_pressure, ["stable", 35, 70]],
    [elements.tempo, Math.abs(Number(genome.tempo || 60) - 60), ["stable", 28, 65]],
  ];

  stateMap.forEach(([element, rawValue, labels]) => {
    if (!element) return;
    const value = Number(rawValue || 0);
    const status = value >= labels[2] ? "critical" : value >= labels[1] ? "warning" : labels[0];
    element.parentElement?.setAttribute("data-status", status);
  });
}

function setClassGroup(element, prefix, nextClass) {
  [...element.classList].forEach((className) => {
    if (className.startsWith(prefix)) element.classList.remove(className);
  });
  element.classList.add(nextClass);
}

function triggerMutationFlash(mutationType, duration = 920) {
  if (!elements.facility || !elements.eventBand) return;
  elements.facility.style.setProperty("--impulse", "1");
  elements.facility.dataset.event = mutationType;
  document.body.classList.add("mutation-flash");
  elements.eventBand.classList.add("event-active");
  if (state.audio.enabled && state.audio.context) playMutationAccent(mutationType);
  if (state.pendingPopupSignals?.length) {
    showContaminationOverlay(state.pendingPopupSignals[0]);
    state.pendingPopupSignals = [];
  }
  window.setTimeout(() => {
    elements.facility.style.setProperty("--impulse", "0");
    document.body.classList.remove("mutation-flash");
    elements.eventBand.classList.remove("event-active");
  }, duration);
}

function triggerPhaseUpFlash(duration = 1400) {
  document.body.classList.add("phase-up-flash");
  if (elements.eventBand) elements.eventBand.classList.add("event-active");
  window.setTimeout(() => {
    document.body.classList.remove("phase-up-flash");
    if (elements.eventBand) elements.eventBand.classList.remove("event-active");
  }, duration);
}

function showContaminationOverlay(signal) {
  if (!elements.contaminationOverlay || !elements.contaminationText || !elements.contaminationLink) return;
  window.clearTimeout(state.contaminationTimer);
  elements.contaminationText.textContent = signal.signal_text || "";
  elements.contaminationLink.href = signal.url || "#external-signal";
  if (signal.is_affiliate) {
    elements.contaminationLink.target = "_blank";
    elements.contaminationLink.rel = "nofollow sponsored noopener";
  } else {
    elements.contaminationLink.removeAttribute("target");
    elements.contaminationLink.removeAttribute("rel");
  }
  elements.contaminationLink.textContent = signal.label ? `${signal.label} / 未接続` : "未確認接続 / 未接続";
  elements.contaminationOverlay.classList.add("visible");
  elements.contaminationOverlay.setAttribute("aria-hidden", "false");
  state.contaminationTimer = window.setTimeout(() => {
    elements.contaminationOverlay.classList.remove("visible");
    elements.contaminationOverlay.setAttribute("aria-hidden", "true");
  }, 5200);
}

function renderSignalsPanel(signals) {
  if (!elements.signalsList) return;
  const section = document.querySelector("#signalsSection");
  if (!signals.length) {
    if (section) section.style.display = "none";
    return;
  }
  if (section) section.style.display = "";
  elements.signalsList.replaceChildren(
    ...signals.map((sig) => {
      const item = document.createElement("a");
      item.className = "signal-entry";
      item.href = sig.url || "#external-signal";
      item.setAttribute("aria-label", "外部信号枠。広告コードは未挿入です。");
      if (sig.is_affiliate) {
        item.target = "_blank";
        item.rel = "nofollow sponsored noopener";
      }
      item.addEventListener("click", (event) => {
        trackSignalClick(sig.slot_name || "signals_panel", sig);
        if (!sig.is_affiliate) event.preventDefault();
      });
      const label = document.createElement("span");
      label.className = "signal-entry-label";
      label.textContent = sig.signal_text || sig.label || "外部信号";
      const tag = document.createElement("span");
      tag.className = "signal-entry-tag";
      tag.textContent = `phase ${sig.trigger_phase ?? 0}`;
      item.append(label, tag);
      return item;
    }),
  );
}

function renderSignalBanners(signals, genome, summary) {
  const slots = document.querySelectorAll("[data-signal-slot]");
  if (!slots.length) return;
  const phase = Number(genome?.phase || 0);
  const mutation = summary?.current_mutation || genome?.last_mutation_type || "none";
  const isMidnight = new Date().getHours() >= 2 && new Date().getHours() < 4;

  slots.forEach((slot, index) => {
    const slotName = slot.dataset.signalSlot || "room_corner";
    const signal = chooseSignalForSlot(signals, slotName, index);
    slot.dataset.phase = String(phase);
    slot.dataset.mutation = mutation;
    slot.classList.toggle("signal-midnight", isMidnight);

    if (!signal) {
      slot.innerHTML = `<span>SIGNAL DETECTED</span><strong>${phase >= 2 ? "noise only" : "--- --- ---"}</strong>`;
      if (slot.matches("a")) {
        slot.href = "#external-signal";
        slot.removeAttribute("target");
        slot.removeAttribute("rel");
      }
      return;
    }

    if (slot.classList.contains("room-signal-poster")) {
      slot.href = signal.url || "#external-signal";
      if (signal.is_affiliate) {
        slot.target = "_blank";
        slot.rel = "nofollow sponsored noopener";
      }
      slot.innerHTML = `
        <span class="poster-kicker">PR / SIGNAL</span>
        <strong>${signal.label || "OBSERVATION NODE"}</strong>
        <small>${signal.signal_text || "external signal"}</small>
      `;
      slot.onclick = () => trackSignalClick(slotName, signal);
      return;
    }

    slot.innerHTML = `
      <span>${slotSignalLabel(slotName, isMidnight)}</span>
      <button type="button" data-signal-id="${signal.id}" data-provider="${signal.affiliate_provider || "none"}">
        ${signal.signal_text || signal.label || "SIGNAL DETECTED"}
      </button>
      ${signal.disclosure ? `<small>${signal.disclosure}</small>` : ""}
    `;
    const button = slot.querySelector("button");
    button?.addEventListener("click", () => {
      trackSignalClick(slotName, signal);
      if (signal.is_affiliate && signal.url) {
        window.open(signal.url, "_blank", "noopener,noreferrer");
      }
    });
  });
}

function chooseSignalForSlot(signals, slotName, index) {
  if (!signals.length) return null;
  return signals.find((signal) => signal.slot_name === slotName) || null;
}

function slotSignalLabel(slotName, isMidnight) {
  if (isMidnight) return "深夜受信物";
  return {
    left_terminal_bottom: "SIGNAL DETECTED",
    right_monitor_inner: "観測補助装置",
    crt_bottom: "境界外接続",
    room_corner: "未確認媒体",
  }[slotName] || "外部信号";
}

function trackSignalClick(slotName, signal) {
  const payload = {
    slot_name: slotName,
    signal_id: signal.id,
    provider: signal.affiliate_provider || "none",
    timestamp: new Date().toISOString(),
  };
  fetch("/api/signal-click", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }).catch(() => {});
}

function renderLogs(logs, noiseLevel, phaseDrift) {
  if (!elements.logList) return;
  const humanFragments = [
    "まだ見てる？",
    "反応した",
    "近づいてる",
    "さっきより静か",
    "見返してきた",
  ];
  const visibleLogs = logs.slice(0, 36);
  if (visibleLogs.length && Number(noiseLevel || 0) + Number(phaseDrift || 0) > 18) {
    const fragmentIndex = (Number(noiseLevel || 0) + Number(phaseDrift || 0)) % humanFragments.length;
    visibleLogs.splice(2, 0, `[handwritten] ${humanFragments[fragmentIndex]}`);
  }
  elements.logList.replaceChildren(
    ...visibleLogs.map((log, index) => {
      const item = document.createElement("li");
      if (log.includes("SIGNAL")) {
        item.classList.add("log-signal");
      }
      item.textContent = shouldDisturbLog(index, noiseLevel, phaseDrift) ? disturbText(log) : log;
      return item;
    }),
  );
}

function shouldDisturbLog(index, noiseLevel, phaseDrift) {
  return noiseLevel > 28 && (index + phaseDrift) % 6 === 3;
}

function disturbText(text) {
  const marks = ["*", ":", "_"];
  return text
    .split("")
    .map((letter, index) => (index % 11 === 0 ? `${letter}${marks[index % marks.length]}` : letter))
    .join("");
}

async function sendAction(action) {
  const normalizedAction = String(action || "").trim();
  if (!normalizedAction) return;

  if (state.socket && state.socket.readyState === WebSocket.OPEN) {
    state.socket.send(JSON.stringify({ type: "action", action: normalizedAction }));
    return;
  }

  setText(elements.connectionStatus, "HTTP観測");
  renderLogs([`[queued] ${normalizedAction}`, ...(state.genome?.log_history || [])], state.genome?.noise_level || 0, state.genome?.phase_drift || 0);

  try {
    const response = await fetch("/api/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: normalizedAction }),
    });
    if (!response.ok) throw new Error(`action failed: ${response.status}`);
    const payload = await response.json();
    if (payload.type === "genome" && payload.genome) {
      renderGenome(payload.genome, payload.genome_summary || payload.genome.genome_summary || {});
      renderCreature(payload.creature);
    }
  } catch (error) {
    setText(elements.connectionStatus, "未接続");
    renderLogs([`[local only] ${normalizedAction}`, "[warn] action endpoint unreachable", ...(state.genome?.log_history || [])], state.genome?.noise_level || 0, state.genome?.phase_drift || 0);
  }
}

async function fetchCreature() {
  try {
    const response = await fetch("/api/creature", { cache: "no-store" });
    if (!response.ok) return;
    renderCreature(await response.json());
  } catch {
    // Observation can still run with the base organism if the creature bridge is unavailable.
  }
}

function startAudio() {
  if (!state.audio.context) state.audio.context = new AudioContext();
  state.audio.enabled = !state.audio.enabled;
  elements.audioToggle?.classList.toggle("live", state.audio.enabled);
  setText(elements.audioToggle, state.audio.enabled ? "止" : "音");
  if (state.audio.enabled) {
    scheduleBioSound();
  } else {
    window.clearTimeout(state.audio.timer);
  }
}

function scheduleBioSound() {
  window.clearTimeout(state.audio.timer);
  if (!state.audio.enabled || !state.genome || !state.audio.context) return;
  playBioPulse();
  const genome = state.genome;
  const mode = state.summary?.audio_mode || "baseline";
  const intervalScale = {
    softTone: 1.22,
    hardPulse: 0.72,
    singleTone: 1.06,
    farShell: 1.36,
    glitchSkin: 0.86,
    phaseDelay: 1.12,
    lowGrowth: 1.62,
  }[mode] || 1;
  const interval = Math.max(150, (60000 / genome.tempo) * intervalScale);
  const jitter = genome.noise_level * 9 + (100 - genome.stability) * 5 + (genome.audio_instability ?? 0) * 8;
  state.audio.timer = window.setTimeout(scheduleBioSound, interval + Math.random() * jitter);
}

function playBioPulse() {
  const context = state.audio.context;
  const genome = state.genome;
  const oscillator = context.createOscillator();
  const companion = context.createOscillator();
  const gain = context.createGain();
  const filter = context.createBiquadFilter();
  const mode = state.summary?.audio_mode || "baseline";
  const wobble = (Math.random() - 0.5) * ((100 - genome.stability) + (genome.audio_instability ?? 0)) * 0.75;
  const modePitch = {
    softTone: -18,
    hardPulse: 24,
    singleTone: 42,
    farShell: -26,
    glitchSkin: 16,
    phaseDelay: 8,
    lowGrowth: -34,
  }[mode] || 0;
  const base = 84 + genome.phase * 28 + genome.mutation_level * 0.8 + (genome.trait_softness ?? 0) * 0.35 + modePitch + wobble;

  oscillator.type = mode === "glitchSkin" || (genome.trait_corruption ?? 0) > 10 || genome.noise_level > 38 ? "triangle" : "sine";
  companion.type = mode === "hardPulse" || (genome.trait_aggression ?? 0) > 8 ? "square" : "sine";
  oscillator.frequency.setValueAtTime(base, context.currentTime);
  companion.frequency.setValueAtTime(base * (mode === "singleTone" ? 1 : 1.5), context.currentTime);
  filter.type = mode === "farShell" ? "lowpass" : "bandpass";
  filter.frequency.setValueAtTime(Math.max(90, 360 + genome.stability * 6 - genome.noise_level * 3), context.currentTime);
  filter.Q.setValueAtTime(0.6 + (genome.trait_corruption ?? 0) / 30, context.currentTime);
  gain.gain.setValueAtTime(0.0001, context.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.035, context.currentTime + 0.04);
  gain.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + 0.32 + (genome.trait_softness ?? 0) / 220);

  oscillator.connect(filter);
  companion.connect(filter);
  filter.connect(gain);
  gain.connect(context.destination);
  oscillator.start();
  companion.start();
  oscillator.stop(context.currentTime + 0.45);
  companion.stop(context.currentTime + 0.45);
}

function playMutationAccent(mutationType) {
  const context = state.audio.context;
  const oscillator = context.createOscillator();
  const gain = context.createGain();
  const pitch = {
    soft_bloom: 220,
    distorted_pulse: 96,
    gaze_lock: 330,
    distant_shell: 72,
    noise_skin: 150,
    phase_slip: 260,
    silent_growth: 55,
  }[mutationType] || 180;

  oscillator.type = mutationType === "distorted_pulse" || mutationType === "noise_skin" ? "sawtooth" : "sine";
  oscillator.frequency.setValueAtTime(pitch, context.currentTime);
  gain.gain.setValueAtTime(0.0001, context.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.06, context.currentTime + 0.03);
  gain.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + 0.7);
  oscillator.connect(gain);
  gain.connect(context.destination);
  oscillator.start();
  oscillator.stop(context.currentTime + 0.75);
}

elements.form?.addEventListener("submit", (event) => {
  event.preventDefault();
  const action = elements.input?.value || "";
  if (!action.trim()) return;
  sendAction(action);
  elements.input.value = "";
});

elements.audioToggle?.addEventListener("click", startAudio);

renderLogs(["[boot] observation terminal wake", "[boot] genome socket opening", "[wait] signal ping --"], 0, 0);
fetchCreature();
connect();
