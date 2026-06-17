(() => {
  "use strict";

  window.KYOUKAI_ROOM = "exit";

  const scenes = {
    hall: {
      image: "/static/exit/exit_01_hall.png",
      pulse: ["44%", "57%"],
      choices: {
        a: { label: "ドア", value: 2, spot: [42, 29, 20, 16] },
        b: { label: "穴", value: -1, spot: [31, 74, 23, 14] },
        c: { label: "ぬいぐるみ", value: 1, spot: [64, 60, 22, 15] }
      }
    },
    corner: {
      image: "/static/exit/exit_02_corner.png",
      pulse: ["56%", "42%"],
      choices: {
        a: { label: "左奥", value: -2, spot: [14, 32, 25, 16] },
        b: { label: "右奥", value: 1, spot: [56, 45, 25, 16] },
        c: { label: "壁の装飾", value: 3, spot: [60, 72, 25, 16] }
      }
    },
    emergency: {
      image: "/static/exit/exit_03_emergency.png",
      pulse: ["50%", "40%"],
      choices: {
        a: { label: "EXIT", value: -3, spot: [29, 19, 26, 15] },
        b: { label: "階段", value: 2, spot: [35, 42, 25, 16] },
        c: { label: "壁の亀裂", value: -1, spot: [64, 66, 24, 17] }
      }
    },
    window: {
      image: "/static/exit/exit_04_window.png",
      pulse: ["58%", "33%"],
      choices: {
        a: { label: "窓", value: 1, spot: [10, 52, 26, 17] },
        b: { label: "植木", value: -2, spot: [47, 25, 23, 15] },
        c: { label: "奥の景色", value: 2, spot: [66, 60, 25, 17] }
      }
    },
    "hall-b": {
      image: "/static/exit/exit_01b_hall.png",
      pulse: ["39%", "70%"],
      choices: {
        a: { label: "ドア", value: -1, spot: [39, 28, 22, 16] },
        b: { label: "穴", value: -3, spot: [32, 73, 23, 15] },
        c: { label: "ぬいぐるみ", value: 2, spot: [62, 59, 23, 16] }
      }
    },
    "corner-b": {
      image: "/static/exit/exit_02b_corner.png",
      pulse: ["51%", "48%"],
      choices: {
        a: { label: "左奥", value: 3, spot: [15, 32, 25, 16] },
        b: { label: "右奥", value: -2, spot: [57, 47, 24, 16] },
        c: { label: "壁の装飾", value: 1, spot: [62, 73, 24, 16] }
      }
    },
    "emergency-b": {
      image: "/static/exit/exit_03b_emergency.png",
      pulse: ["50%", "43%"],
      choices: {
        a: { label: "EXIT", value: -1, spot: [29, 19, 26, 15] },
        b: { label: "階段", value: 2, spot: [35, 42, 25, 16] },
        c: { label: "壁の亀裂", value: -3, spot: [64, 66, 24, 17] }
      }
    },
    "window-b": {
      image: "/static/exit/exit_04b_window.png",
      pulse: ["61%", "45%"],
      choices: {
        a: { label: "窓", value: 1, spot: [10, 52, 26, 17] },
        b: { label: "植木", value: -2, spot: [47, 25, 23, 15] },
        c: { label: "奥の景色", value: 3, spot: [66, 60, 25, 17] }
      }
    }
  };

  const fragments = ["hall", "corner", "emergency", "window", "hall-b", "corner-b", "emergency-b", "window-b"];
  const whispers = ["みえてる？", "そこ？", "まだいる？", "でれない", "きこえる？", "こないで", "ちがう", "おそい", "まって", "ここじゃない"];
  const girlStates = ["run-a", "run-b", "look-back", "tired", "still", "stumble", "small", "far"];
  const SEGMENT_TOUCH_LIMIT = 5;
  const endings = [
    { id: "passage", label: "接続通過" },
    { id: "backflow", label: "逆流接続" },
    { id: "reconnect", label: "再接続" },
    { id: "boundary-collapse", label: "境界崩壊" },
    { id: "drift", label: "漂流継続" }
  ];

  const boundary = document.querySelector(".exit-boundary");
  const stage = document.querySelector(".exit-stage");
  const sceneImage = document.querySelector(".exit-scene");
  const loader = document.querySelector(".exit-loader");
  const loaderArt = document.querySelector(".exit-loader__art");
  const loaderGirl = document.querySelector(".exit-loader__girl");
  const loaderStatus = document.querySelector(".exit-loader__status");
  const bubble = document.querySelector(".exit-loader__bubble");
  const ending = document.querySelector(".exit-ending");
  const endingTitle = document.querySelector(".exit-ending__title");
  const continueButton = document.querySelector(".exit-ending__continue");
  const hotspots = Array.from(document.querySelectorAll("[data-hotspot]"));

  let currentScene = pickInitialScene();
  let routeScore = 0;
  let stepCount = 0;
  let segmentStep = 0;
  let loading = false;

  function pickInitialScene() {
    try {
      const params = new URLSearchParams(window.location.search);
      const requested = params.get("scene");
      if (requested && scenes[requested]) return requested;
    } catch (_) {}
    return fragments[Math.floor(Math.random() * 4)];
  }

  function randomDelay() {
    return Math.floor(1200 + Math.random() * 1600);
  }

  function randomizeHotspots(scene) {
    hotspots.forEach((button) => {
      const choice = scene.choices[button.dataset.hotspot];
      const label = choice?.label || "調べる";
      const spot = choice?.spot || [38, 42, 24, 16];
      button.dataset.hotspotName = label;
      button.setAttribute("aria-label", `${label}を調べる`);
      button.style.left = `${spot[0]}%`;
      button.style.top = `${spot[1]}%`;
      button.style.width = `${spot[2]}%`;
      button.style.height = `${spot[3]}%`;
    });
  }

  function girlStateForStep(step) {
    if (step <= 1) return "run-a";
    if (step === 2) return "run-b";
    if (step === 3) return "run-b";
    if (step === 4) return "tired";
    if (step === 5) return "look-back";
    return girlStates[Math.min(girlStates.length - 1, Math.floor(Math.random() * girlStates.length))];
  }

  function loaderLineForStep(step) {
    if (step % 3 === 1) return "Loading...";
    if (step % 3 === 2) return "Connecting...";
    return "Signal unstable...";
  }

  function showLoader() {
    loading = true;
    const girlState = girlStateForStep(segmentStep);
    const progressionIndex = Math.min(Math.max(segmentStep - 1, 0), 5);
    const driftRate = Math.min(99, 12 + segmentStep * 13);
    boundary.classList.add("is-loading");
    loader.dataset.girl = girlState;
    loader.dataset.progress = String(progressionIndex + 1);
    loader.setAttribute("aria-hidden", "false");
    if (loaderArt) {
      loaderArt.removeAttribute("src");
      loaderArt.classList.remove("is-visible");
    }
    loaderGirl?.setAttribute("data-state", girlState);
    if (loaderStatus) {
      loaderStatus.textContent = `border signal ${String(driftRate).padStart(2, "0")}%`;
    }
    loader.querySelector("[data-loader-primary]").textContent = loaderLineForStep(segmentStep);
    bubble.classList.remove("is-visible");
    bubble.textContent = "";

    if (segmentStep === 3) {
      bubble.textContent = "みえてる？";
    } else if (segmentStep === 5) {
      bubble.textContent = "こないで";
    } else if (segmentStep >= 6 && Math.random() < 0.72) {
      bubble.textContent = whispers[Math.floor(Math.random() * whispers.length)];
    }

    if (bubble.textContent) {
      window.setTimeout(() => bubble.classList.add("is-visible"), 180);
    }
  }

  function hideLoader() {
    loading = false;
    boundary.classList.remove("is-loading");
    loader.setAttribute("aria-hidden", "true");
    loaderArt?.classList.remove("is-visible");
    loaderArt?.removeAttribute("src");
    bubble.classList.remove("is-visible");
  }

  function renderScene() {
    const scene = scenes[currentScene] || scenes.hall;
    stage.dataset.scene = currentScene;
    stage.style.setProperty("--exit-pulse-x", scene.pulse[0]);
    stage.style.setProperty("--exit-pulse-y", scene.pulse[1]);
    sceneImage.src = scene.image;
    randomizeHotspots(scene);
    boundary.classList.remove("is-shifting");
    void boundary.offsetWidth;
    boundary.classList.add("is-shifting");
    window.dispatchEvent(new CustomEvent("kyoukai:exit-scene", {
      detail: {
        scene: currentScene,
        steps: stepCount
      }
    }));
  }

  function decideEnding() {
    if (segmentStep < SEGMENT_TOUCH_LIMIT) return null;
    if (routeScore >= 8) return endings[0];
    if (routeScore <= -8) return endings[1];
    if (Math.abs(routeScore) <= 2) return endings[2];
    if (routeScore < 5) return endings[3];
    return endings[4];
  }

  function showEnding(result) {
    boundary.classList.add("is-ended");
    ending.setAttribute("aria-hidden", "false");
    ending.dataset.result = result.id;
    endingTitle.textContent = `${result.label} / 観測不能`;
    window.dispatchEvent(new CustomEvent("kyoukai:exit-ending", {
      detail: {
        result: result.id,
        routeScore
      }
    }));
  }

  function moveThrough(choiceId) {
    if (loading || boundary.classList.contains("is-ended")) return;
    const scene = scenes[currentScene] || scenes.hall;
    const choice = scene.choices[choiceId];
    if (!choice) return;

    routeScore += choice.value;
    stepCount += 1;
    segmentStep += 1;
    window.KYOUKAI_EXIT_ROUTE_SCORE = routeScore;
    showLoader();

    window.setTimeout(() => {
      currentScene = randomNextScene();
      renderScene();
      hideLoader();
      const result = decideEnding();
      if (result) showEnding(result);
    }, randomDelay());
  }

  function randomNextScene() {
    const candidates = fragments.filter((fragment) => fragment !== currentScene);
    return candidates[Math.floor(Math.random() * candidates.length)] || "hall";
  }

  function restart() {
    currentScene = fragments[Math.floor(Math.random() * 4)];
    routeScore = 0;
    stepCount = 0;
    segmentStep = 0;
    window.KYOUKAI_EXIT_ROUTE_SCORE = routeScore;
    loading = false;
    boundary.classList.remove("is-ended");
    boundary.classList.remove("is-loading");
    ending.setAttribute("aria-hidden", "true");
    loader.setAttribute("aria-hidden", "true");
    renderScene();
  }

  hotspots.forEach((button) => {
    button.addEventListener("click", () => moveThrough(button.dataset.hotspot));
  });

  continueButton?.addEventListener("click", restart);

  renderScene();
})();
