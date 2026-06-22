(function () {
  const root = document.querySelector(".city-location");
  if (!root) return;

  const isSmall = () => window.matchMedia("(max-width: 768px)").matches;
  const hotspots = Array.from(document.querySelectorAll(".city-hotspot"));
  let ambientStarted = false;

  function applyHotspotPositions() {
    const mode = isSmall() ? "sp" : "pc";
    hotspots.forEach((hotspot) => {
      const x = hotspot.dataset[`${mode}X`];
      const y = hotspot.dataset[`${mode}Y`];
      const width = hotspot.dataset[`${mode}Width`];
      const height = hotspot.dataset[`${mode}Height`];
      hotspot.style.left = `${x}%`;
      hotspot.style.top = `${y}%`;
      hotspot.style.width = `${width}%`;
      hotspot.style.height = `${height}%`;
    });
  }

  function readState() {
    try {
      const raw = window.localStorage.getItem("kyoukai_city_state");
      const state = raw ? JSON.parse(raw) : {};
      return state && typeof state === "object" ? state : {};
    } catch (_error) {
      return {};
    }
  }

  function writeVisit() {
    const slug = root.dataset.locationSlug || "";
    const id = root.dataset.locationId || "";
    if (!slug) return;
    const state = readState();
    const visits = state.visits && typeof state.visits === "object" ? state.visits : {};
    visits[slug] = Number(visits[slug] || 0) + 1;
    const visitedLocations = Array.isArray(state.visited_locations)
      ? state.visited_locations
      : [];
    if (!visitedLocations.includes(slug)) {
      visitedLocations.push(slug);
    }
    state.visits = visits;
    state.visited_locations = visitedLocations;
    state.previousLocation = state.currentLocation || "";
    state.currentLocation = slug;
    state.currentLocationId = id;
    state.lastVisitedAt = new Date().toISOString();
    try {
      window.localStorage.setItem("kyoukai_city_state", JSON.stringify(state));
    } catch (_error) {
      // localStorage can be unavailable in strict browser modes; rendering should continue.
    }
  }

  function bindDebugPoint() {
    const output = document.querySelector("[data-city-debug-point]");
    if (!output) return;
    root.addEventListener("click", (event) => {
      const rect = root.getBoundingClientRect();
      const x = ((event.clientX - rect.left) / rect.width) * 100;
      const y = ((event.clientY - rect.top) / rect.height) * 100;
      output.textContent = `click: ${x.toFixed(1)}, ${y.toFixed(1)}`;
    });
  }

  function createNoiseBuffer(audioContext, seconds) {
    const sampleRate = audioContext.sampleRate;
    const buffer = audioContext.createBuffer(1, sampleRate * seconds, sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < data.length; i += 1) {
      data[i] = Math.random() * 2 - 1;
    }
    return buffer;
  }

  function createCrowdLayer(audioContext, output, options) {
    const source = audioContext.createBufferSource();
    const filter = audioContext.createBiquadFilter();
    const gain = audioContext.createGain();
    source.buffer = createNoiseBuffer(audioContext, options.duration);
    source.loop = true;
    filter.type = "bandpass";
    filter.frequency.value = options.frequency;
    filter.Q.value = options.q;
    gain.gain.value = options.gain;
    source.connect(filter);
    filter.connect(gain);
    gain.connect(output);
    source.start();
    return { source, filter, gain };
  }

  function createMurmur(audioContext, output, index) {
    const oscillator = audioContext.createOscillator();
    const filter = audioContext.createBiquadFilter();
    const gain = audioContext.createGain();
    oscillator.type = index % 2 ? "triangle" : "sine";
    oscillator.frequency.value = 120 + Math.random() * 110;
    filter.type = "lowpass";
    filter.frequency.value = 420 + Math.random() * 220;
    gain.gain.value = 0.0015 + Math.random() * 0.002;
    oscillator.connect(filter);
    filter.connect(gain);
    gain.connect(output);
    oscillator.start();

    window.setInterval(() => {
      const now = audioContext.currentTime;
      oscillator.frequency.linearRampToValueAtTime(95 + Math.random() * 150, now + 1.8);
      gain.gain.linearRampToValueAtTime(0.0005 + Math.random() * 0.004, now + 1.2);
    }, 1400 + index * 260);
  }

  function startAmbient() {
    if (ambientStarted) return;
    ambientStarted = true;

    const AudioContextConstructor = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextConstructor) return;

    try {
      const audioContext = new AudioContextConstructor();
      const master = audioContext.createGain();
      const compressor = audioContext.createDynamicsCompressor();
      master.gain.value = 0.055;
      compressor.threshold.value = -34;
      compressor.knee.value = 18;
      compressor.ratio.value = 8;
      master.connect(compressor);
      compressor.connect(audioContext.destination);

      createCrowdLayer(audioContext, master, {
        duration: 3,
        frequency: 280,
        q: 0.42,
        gain: 0.055,
      });
      createCrowdLayer(audioContext, master, {
        duration: 5,
        frequency: 760,
        q: 0.36,
        gain: 0.018,
      });
      createCrowdLayer(audioContext, master, {
        duration: 4,
        frequency: 1450,
        q: 0.22,
        gain: 0.006,
      });

      for (let i = 0; i < 9; i += 1) {
        createMurmur(audioContext, master, i);
      }
    } catch (_error) {
      ambientStarted = false;
    }
  }

  function bindAmbientStart() {
    window.addEventListener("pointerdown", startAmbient, { once: true, passive: true });
    window.addEventListener("keydown", startAmbient, { once: true });
  }

  applyHotspotPositions();
  writeVisit();
  bindDebugPoint();
  bindAmbientStart();
  window.addEventListener("resize", applyHotspotPositions, { passive: true });
})();
