(function () {
  const root = document.querySelector("[data-location-slug='altar']");
  if (!root) return;

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
    const slug = "altar";
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
    state.currentLocationId = "ALTAR";
    state.lastVisitedAt = new Date().toISOString();
    try {
      window.localStorage.setItem("kyoukai_city_state", JSON.stringify(state));
    } catch (_error) {
      // localStorage may be unavailable; the altar still renders without history.
    }
  }

  function bindDebugPoint() {
    const output = document.querySelector("[data-altar-debug-point]");
    const frame = document.querySelector(".altar-frame");
    if (!output || !frame) return;
    frame.addEventListener("click", (event) => {
      const rect = frame.getBoundingClientRect();
      const x = ((event.clientX - rect.left) / rect.width) * 100;
      const y = ((event.clientY - rect.top) / rect.height) * 100;
      output.textContent = `click: ${x.toFixed(1)}, ${y.toFixed(1)}`;
    });
  }

  writeVisit();
  bindDebugPoint();
})();
