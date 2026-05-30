(() => {
  "use strict";

  window.KYOUKAI_ROOM = "exit";

  const scenes = {
    hall: {
      image: "/static/exit/exit_01_hall.png",
      pulse: ["44%", "57%"],
      choices: {
        a: { next: "emergency-b", value: 2 },
        b: { next: "window", value: -1 },
        c: { next: "corner", value: 1 }
      }
    },
    corner: {
      image: "/static/exit/exit_02_corner.png",
      pulse: ["56%", "42%"],
      choices: {
        a: { next: "window-b", value: -2 },
        b: { next: "hall-b", value: 1 },
        c: { next: "emergency", value: 3 }
      }
    },
    emergency: {
      image: "/static/exit/exit_03_emergency.png",
      pulse: ["50%", "40%"],
      choices: {
        a: { next: "corner-b", value: -3 },
        b: { next: "hall", value: 2 },
        c: { next: "window", value: -1 }
      }
    },
    window: {
      image: "/static/exit/exit_04_window.png",
      pulse: ["58%", "33%"],
      choices: {
        a: { next: "hall-b", value: 1 },
        b: { next: "emergency", value: -2 },
        c: { next: "corner", value: 2 }
      }
    },
    "hall-b": {
      image: "/static/exit/exit_01b_hall.png",
      pulse: ["39%", "70%"],
      choices: {
        a: { next: "window", value: -1 },
        b: { next: "corner", value: -3 },
        c: { next: "emergency-b", value: 2 }
      }
    },
    "corner-b": {
      image: "/static/exit/exit_02b_corner.png",
      pulse: ["51%", "48%"],
      choices: {
        a: { next: "hall", value: 3 },
        b: { next: "window-b", value: -2 },
        c: { next: "emergency", value: 1 }
      }
    },
    "emergency-b": {
      image: "/static/exit/exit_03b_emergency.png",
      pulse: ["50%", "43%"],
      choices: {
        a: { next: "hall-b", value: -1 },
        b: { next: "corner", value: 2 },
        c: { next: "window-b", value: -3 }
      }
    },
    "window-b": {
      image: "/static/exit/exit_04b_window.png",
      pulse: ["61%", "45%"],
      choices: {
        a: { next: "emergency", value: 1 },
        b: { next: "hall", value: -2 },
        c: { next: "corner-b", value: 3 }
      }
    }
  };

  const fragments = ["hall", "corner", "emergency", "window", "hall-b", "corner-b", "emergency-b", "window-b"];
  const whispers = ["みえてる？", "そこ？", "まだいる？", "でれない", "きこえる？", "こないで"];
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
  const bubble = document.querySelector(".exit-loader__bubble");
  const ending = document.querySelector(".exit-ending");
  const endingTitle = document.querySelector(".exit-ending__title");
  const continueButton = document.querySelector(".exit-ending__continue");
  const hotspots = Array.from(document.querySelectorAll("[data-hotspot]"));

  let currentScene = pickInitialScene();
  let connectionScore = 0;
  let stepCount = 0;
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
    return Math.floor(500 + Math.random() * 1500);
  }

  function showLoader() {
    loading = true;
    boundary.classList.add("is-loading");
    loader.setAttribute("aria-hidden", "false");
    bubble.classList.remove("is-visible");
    bubble.textContent = "";

    if (stepCount >= 2) {
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
    if (connectionScore >= 8) return endings[0];
    if (connectionScore <= -8) return endings[1];
    if (stepCount >= 10 && Math.abs(connectionScore) <= 2) return endings[2];
    if (stepCount >= 12 && connectionScore < 5) return endings[3];
    if (stepCount >= 8) return endings[4];
    return null;
  }

  function showEnding(result) {
    boundary.classList.add("is-ended");
    ending.setAttribute("aria-hidden", "false");
    ending.dataset.result = result.id;
    endingTitle.textContent = result.label;
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
    showLoader();

    window.setTimeout(() => {
      currentScene = choice.next;
      renderScene();
      hideLoader();
      const result = decideEnding();
      if (result) showEnding(result);
    }, randomDelay());
  }

  function restart() {
    currentScene = fragments[Math.floor(Math.random() * 4)];
    connectionScore = 0;
    stepCount = 0;
    boundary.classList.remove("is-ended");
    ending.setAttribute("aria-hidden", "true");
    showLoader();
    window.setTimeout(() => {
      renderScene();
      hideLoader();
    }, randomDelay());
  }

  hotspots.forEach((button) => {
    button.addEventListener("click", () => moveThrough(button.dataset.hotspot));
  });

  continueButton?.addEventListener("click", restart);

  showLoader();
  window.setTimeout(() => {
    renderScene();
    hideLoader();
  }, randomDelay());
})();
