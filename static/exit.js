(() => {
  "use strict";

  window.KYOUKAI_ROOM = "exit";

  const scenes = {
    hall: {
      image: "/static/exit/exit_01_hall.png",
      pulse: ["44%", "57%"],
      choices: {
        a: { label: "ドア", value: 2 },
        b: { label: "穴", value: -1 },
        c: { label: "ぬいぐるみ", value: 1 }
      }
    },
    corner: {
      image: "/static/exit/exit_02_corner.png",
      pulse: ["56%", "42%"],
      choices: {
        a: { label: "左", value: -2 },
        b: { label: "右", value: 1 },
        c: { label: "窓", value: 3 }
      }
    },
    emergency: {
      image: "/static/exit/exit_03_emergency.png",
      pulse: ["50%", "40%"],
      choices: {
        a: { label: "EXIT", value: -3 },
        b: { label: "階段", value: 2 },
        c: { label: "壁", value: -1 }
      }
    },
    window: {
      image: "/static/exit/exit_04_window.png",
      pulse: ["58%", "33%"],
      choices: {
        a: { label: "窓", value: 1 },
        b: { label: "植木", value: -2 },
        c: { label: "奥", value: 2 }
      }
    },
    "hall-b": {
      image: "/static/exit/exit_01b_hall.png",
      pulse: ["39%", "70%"],
      choices: {
        a: { label: "ドア", value: -1 },
        b: { label: "穴", value: -3 },
        c: { label: "ぬいぐるみ", value: 2 }
      }
    },
    "corner-b": {
      image: "/static/exit/exit_02b_corner.png",
      pulse: ["51%", "48%"],
      choices: {
        a: { label: "左", value: 3 },
        b: { label: "右", value: -2 },
        c: { label: "窓", value: 1 }
      }
    },
    "emergency-b": {
      image: "/static/exit/exit_03b_emergency.png",
      pulse: ["50%", "43%"],
      choices: {
        a: { label: "EXIT", value: -1 },
        b: { label: "階段", value: 2 },
        c: { label: "壁", value: -3 }
      }
    },
    "window-b": {
      image: "/static/exit/exit_04b_window.png",
      pulse: ["61%", "45%"],
      choices: {
        a: { label: "窓", value: 1 },
        b: { label: "植木", value: -2 },
        c: { label: "奥", value: 3 }
      }
    }
  };

  const fragments = ["hall", "corner", "emergency", "window", "hall-b", "corner-b", "emergency-b", "window-b"];
  const whispers = ["みえてる？", "そこ？", "まだいる？", "でれない", "きこえる？", "こないで", "どこ？", "はやく"];
  const girlStates = ["run-a", "run-b", "look-back", "tired", "still", "stumble", "small", "far"];
  const SEGMENT_TOUCH_LIMIT = 5;
  const FULL_LOADER_FROM_STEP = 4;
  const loadingProgression = [0, 1, 3, 5, 7];
  const loadingImages = [
    "/static/exit/loading/loading_01.png",
    "/static/exit/loading/loading_02.png",
    "/static/exit/loading/loading_03.png",
    "/static/exit/loading/loading_04.png",
    "/static/exit/loading/loading_05.png",
    "/static/exit/loading/loading_06.png",
    "/static/exit/loading/loading_07.png",
    "/static/exit/loading/loading_08.png"
  ];
  const endings = [
    { id: "escape", label: "逃走成功" },
    { id: "backflow", label: "逆流" },
    { id: "loop", label: "再ループ" },
    { id: "collapse", label: "接続崩壊" },
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
  let connectionScore = 0;
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

  function sceneDelay(useFullLoader) {
    if (useFullLoader) return randomDelay();
    return Math.floor(320 + Math.random() * 260);
  }

  function randomBetween(min, max) {
    return min + Math.random() * (max - min);
  }

  function randomSpot(existingSpots) {
    for (let attempt = 0; attempt < 18; attempt += 1) {
      const spot = {
        left: randomBetween(8, 70),
        top: randomBetween(20, 78),
        width: randomBetween(18, 27),
        height: randomBetween(11, 18)
      };
      const centerX = spot.left + spot.width / 2;
      const centerY = spot.top + spot.height / 2;
      const tooClose = existingSpots.some((other) => {
        const otherX = other.left + other.width / 2;
        const otherY = other.top + other.height / 2;
        return Math.abs(centerX - otherX) < 22 && Math.abs(centerY - otherY) < 16;
      });
      if (!tooClose) return spot;
    }
    return {
      left: randomBetween(8, 70),
      top: randomBetween(20, 78),
      width: randomBetween(18, 27),
      height: randomBetween(11, 18)
    };
  }

  function randomizeHotspots(scene) {
    const placed = [];
    hotspots.forEach((button) => {
      const choice = scene.choices[button.dataset.hotspot];
      const label = choice?.label || "調べる";
      const spot = randomSpot(placed);
      placed.push(spot);
      button.dataset.hotspotName = label;
      button.setAttribute("aria-label", `${label}を調べる`);
      button.style.left = `${spot.left.toFixed(2)}%`;
      button.style.top = `${spot.top.toFixed(2)}%`;
      button.style.width = `${spot.width.toFixed(2)}%`;
      button.style.height = `${spot.height.toFixed(2)}%`;
    });
  }

  function showLoader() {
    loading = true;
    const girlState = girlStates[Math.floor(Math.random() * girlStates.length)];
    const progressionIndex = Math.min(Math.max(segmentStep - 1, 0), loadingProgression.length - 1);
    const loadingIndex = loadingProgression[progressionIndex];
    const loadingImage = loadingImages[loadingIndex] || "";
    const impossibleRate = Math.round(((progressionIndex + 1) / loadingProgression.length) * 100);
    boundary.classList.add("is-loading");
    loader.dataset.girl = girlState;
    loader.dataset.progress = String(progressionIndex + 1);
    loader.setAttribute("aria-hidden", "false");
    if (loaderArt) {
      if (loadingImage) {
        loaderArt.src = loadingImage;
        loaderArt.classList.add("is-visible");
      } else {
        loaderArt.removeAttribute("src");
        loaderArt.classList.remove("is-visible");
      }
    }
    loaderGirl?.setAttribute("data-state", girlState);
    if (loaderStatus) {
      loaderStatus.textContent = `脱出不可能 ${impossibleRate}%`;
    }
    bubble.classList.remove("is-visible");
    bubble.textContent = "";

    if (segmentStep >= 3) {
      bubble.textContent = whispers[Math.floor(Math.random() * whispers.length)];
      window.setTimeout(() => bubble.classList.add("is-visible"), 180);
    }
  }

  function hideLoader() {
    loading = false;
    boundary.classList.remove("is-loading");
    loader.setAttribute("aria-hidden", "true");
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
    if (connectionScore >= 8) return endings[0];
    if (connectionScore <= -8) return endings[1];
    if (Math.abs(connectionScore) <= 2) return endings[2];
    if (connectionScore < 5) return endings[3];
    return endings[4];
  }

  function showEnding(result) {
    boundary.classList.add("is-ended");
    ending.setAttribute("aria-hidden", "false");
    ending.dataset.result = result.id;
    endingTitle.textContent = `${result.label} / 観測不能`;
    window.dispatchEvent(new CustomEvent("kyoukai:exit-ending", {
      detail: {
        result: result.id
      }
    }));
  }

  function moveThrough(choiceId) {
    if (loading || boundary.classList.contains("is-ended")) return;
    const scene = scenes[currentScene] || scenes.hall;
    const choice = scene.choices[choiceId];
    if (!choice) return;

    connectionScore += choice.value;
    stepCount += 1;
    segmentStep += 1;
    const useFullLoader = segmentStep >= FULL_LOADER_FROM_STEP;
    loading = true;
    if (useFullLoader) {
      showLoader();
    } else {
      boundary.classList.remove("is-shifting");
      void boundary.offsetWidth;
      boundary.classList.add("is-shifting");
    }

    window.setTimeout(() => {
      currentScene = randomNextScene();
      renderScene();
      if (useFullLoader) {
        hideLoader();
      } else {
        loading = false;
      }
      const result = decideEnding();
      if (result) showEnding(result);
    }, sceneDelay(useFullLoader));
  }

  function randomNextScene() {
    const candidates = fragments.filter((fragment) => fragment !== currentScene);
    return candidates[Math.floor(Math.random() * candidates.length)] || "hall";
  }

  function restart() {
    currentScene = fragments[Math.floor(Math.random() * 4)];
    segmentStep = 0;
    boundary.classList.remove("is-ended");
    ending.setAttribute("aria-hidden", "true");
    renderScene();
  }

  hotspots.forEach((button) => {
    button.addEventListener("click", () => moveThrough(button.dataset.hotspot));
  });

  continueButton?.addEventListener("click", restart);

  renderScene();
})();
