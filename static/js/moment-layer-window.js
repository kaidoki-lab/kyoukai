(function () {
  "use strict";

  var DEFAULT_CONFIG = {
    enabled: true,
    minDelay: 20000,
    maxDelay: 90000,
    chance: 0.3,
    cooldown: 60000,
    duration: 5000,
    soundDelay: 700,
    maxWindows: 1,
    useHtml2Canvas: false,
    debug: false
  };

  var state = {
    activeWindows: 0,
    audioEnabled: false,
    audioContext: null,
    lastRunAt: 0,
    timer: 0,
    zIndex: 2147481200
  };

  function mergeConfig() {
    var userConfig = window.MomentLayerWindowConfig || {};
    var config = {};
    Object.keys(DEFAULT_CONFIG).forEach(function (key) {
      config[key] = Object.prototype.hasOwnProperty.call(userConfig, key)
        ? userConfig[key]
        : DEFAULT_CONFIG[key];
    });
    return config;
  }

  var config = mergeConfig();

  function log() {
    if (!config.debug || !window.console) {
      return;
    }
    console.log.apply(console, ["[MomentLayerWindow]"].concat(Array.prototype.slice.call(arguments)));
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function randomBetween(min, max) {
    return min + Math.random() * (max - min);
  }

  function scheduleNext() {
    window.clearTimeout(state.timer);
    if (!config.enabled) {
      return;
    }
    var minDelay = Math.max(1000, Number(config.minDelay) || DEFAULT_CONFIG.minDelay);
    var maxDelay = Math.max(minDelay, Number(config.maxDelay) || DEFAULT_CONFIG.maxDelay);
    state.timer = window.setTimeout(tryTrigger, randomBetween(minDelay, maxDelay));
  }

  function tryTrigger() {
    var now = Date.now();
    var cooldown = Math.max(0, Number(config.cooldown) || DEFAULT_CONFIG.cooldown);
    var chance = clamp(Number(config.chance), 0, 1);
    var maxWindows = Math.max(1, Number(config.maxWindows) || DEFAULT_CONFIG.maxWindows);

    if (state.activeWindows >= maxWindows || now - state.lastRunAt < cooldown || Math.random() > chance) {
      scheduleNext();
      return;
    }

    state.lastRunAt = now;
    createWindow();
    scheduleNext();
  }

  function isUsableElement(element) {
    if (!(element instanceof HTMLElement)) {
      return false;
    }
    if (element.closest(".mlw-window")) {
      return false;
    }
    if (/^(SCRIPT|STYLE|LINK|META|HEAD|NOSCRIPT|IFRAME|CANVAS|VIDEO|AUDIO)$/.test(element.tagName)) {
      return false;
    }
    var rect = element.getBoundingClientRect();
    return rect.width >= 120 && rect.height >= 90 && rect.bottom > 0 && rect.right > 0;
  }

  function findSourceElement() {
    var selectors = [
      "main",
      "section",
      "article",
      "[class*='room']",
      "[class*='frame']",
      "[class*='shell']",
      "body"
    ];
    var candidates = [];
    selectors.forEach(function (selector) {
      Array.prototype.forEach.call(document.querySelectorAll(selector), function (element) {
        if (isUsableElement(element)) {
          candidates.push(element);
        }
      });
    });
    if (!candidates.length && isUsableElement(document.body)) {
      candidates.push(document.body);
    }
    if (!candidates.length) {
      return null;
    }
    candidates.sort(function (a, b) {
      var ar = a.getBoundingClientRect();
      var br = b.getBoundingClientRect();
      return (br.width * br.height) - (ar.width * ar.height);
    });
    var pool = candidates.slice(0, Math.min(6, candidates.length));
    return pool[Math.floor(Math.random() * pool.length)];
  }

  function sanitizeClone(root) {
    Array.prototype.forEach.call(root.querySelectorAll("[id]"), function (element) {
      element.removeAttribute("id");
    });
    Array.prototype.forEach.call(root.querySelectorAll("input, select, textarea, button, a"), function (element) {
      element.setAttribute("tabindex", "-1");
      element.setAttribute("aria-hidden", "true");
      if ("disabled" in element) {
        element.disabled = true;
      }
      if (element.tagName === "A") {
        element.removeAttribute("href");
      }
    });
    Array.prototype.forEach.call(root.querySelectorAll("script, iframe, canvas, video, audio"), function (element) {
      element.remove();
    });
  }

  function collectTextFragment(source) {
    var text = (source && source.innerText ? source.innerText : document.body.innerText || "")
      .replace(/\s+/g, " ")
      .trim();
    if (!text) {
      return "";
    }
    var start = Math.floor(Math.random() * Math.max(1, text.length - 32));
    return text.slice(start, start + 42);
  }

  function buildFallbackLayer() {
    var fragment = document.createElement("div");
    fragment.className = "mlw-fallback";
    var style = window.getComputedStyle(document.body);
    var baseColors = [
      style.backgroundColor,
      style.color,
      "#d8ddd4",
      "#303533",
      "#101312"
    ];
    for (var i = 0; i < 25; i += 1) {
      var swatch = document.createElement("span");
      swatch.style.setProperty("--mlw-swatch", baseColors[i % baseColors.length]);
      swatch.style.opacity = String(randomBetween(0.18, 0.68));
      fragment.appendChild(swatch);
    }
    return fragment;
  }

  function createCaptureLayer(width, height) {
    var source = findSourceElement();
    var wrapper = document.createElement("div");
    wrapper.className = "mlw-capture";
    wrapper.setAttribute("aria-hidden", "true");

    if (!source) {
      wrapper.appendChild(buildFallbackLayer());
      return { element: wrapper, source: null };
    }

    var rect = source.getBoundingClientRect();
    var clone = source.cloneNode(true);
    sanitizeClone(clone);
    wrapper.appendChild(clone);

    var scale = clamp(randomBetween(0.28, 0.48), 0.24, 0.56);
    var cropX = randomBetween(0, Math.max(0, rect.width * scale - width));
    var cropY = randomBetween(0, Math.max(0, rect.height * scale - height));

    wrapper.style.setProperty("--mlw-capture-width", Math.ceil(rect.width) + "px");
    wrapper.style.setProperty("--mlw-capture-height", Math.ceil(rect.height) + "px");
    wrapper.style.setProperty("--mlw-capture-scale", String(scale));
    wrapper.style.setProperty("--mlw-capture-left", Math.round(-cropX) + "px");
    wrapper.style.setProperty("--mlw-capture-top", Math.round(-cropY) + "px");

    return { element: wrapper, source: source };
  }

  function chooseGeometry() {
    var viewportWidth = window.innerWidth || document.documentElement.clientWidth || 1024;
    var viewportHeight = window.innerHeight || document.documentElement.clientHeight || 768;
    var isSmall = viewportWidth <= 640;
    var width = isSmall
      ? randomBetween(viewportWidth * 0.55, viewportWidth * 0.85)
      : randomBetween(220, 420);
    width = clamp(width, 180, Math.max(180, viewportWidth - 24));
    var height = clamp(width * randomBetween(0.52, 0.64), 116, Math.max(116, viewportHeight - 24));
    var margin = isSmall ? 12 : 22;
    var left = randomBetween(margin, Math.max(margin, viewportWidth - width - margin));
    var top = randomBetween(margin, Math.max(margin, viewportHeight - height - margin));

    return {
      width: Math.round(width),
      height: Math.round(height),
      left: Math.round(left),
      top: Math.round(top)
    };
  }

  function createWindow() {
    state.activeWindows += 1;

    var geometry = chooseGeometry();
    var shell = document.createElement("div");
    shell.className = "mlw-window";
    shell.dataset.phase = "1";
    shell.style.setProperty("--mlw-width", geometry.width + "px");
    shell.style.setProperty("--mlw-height", geometry.height + "px");
    shell.style.setProperty("--mlw-left", geometry.left + "px");
    shell.style.setProperty("--mlw-top", geometry.top + "px");
    shell.style.setProperty("--mlw-z-index", String(state.zIndex));
    state.zIndex += 1;

    var viewport = document.createElement("div");
    viewport.className = "mlw-viewport";
    var capture = createCaptureLayer(geometry.width, geometry.height);
    var noise = document.createElement("div");
    var skip = document.createElement("div");
    var text = document.createElement("div");

    noise.className = "mlw-noise";
    skip.className = "mlw-skip";
    text.className = "mlw-text-fragment";
    text.textContent = collectTextFragment(capture.source);

    viewport.appendChild(capture.element);
    viewport.appendChild(noise);
    viewport.appendChild(skip);
    if (text.textContent) {
      viewport.appendChild(text);
    }
    shell.appendChild(viewport);
    document.body.appendChild(shell);

    runPhases(shell);
  }

  function runPhases(shell) {
    var duration = Math.max(1200, Number(config.duration) || DEFAULT_CONFIG.duration);
    var phaseCount = 6;
    var phaseLength = duration / phaseCount;
    var timers = [];

    for (var phase = 2; phase <= phaseCount; phase += 1) {
      (function (nextPhase) {
        timers.push(window.setTimeout(function () {
          if (shell.isConnected) {
            shell.dataset.phase = String(nextPhase);
          }
        }, phaseLength * (nextPhase - 1)));
      })(phase);
    }

    timers.push(window.setTimeout(function () {
      freezeWindow(shell);
    }, duration));

    shell._mlwTimers = timers;
  }

  function freezeWindow(shell) {
    if (!shell.isConnected) {
      return;
    }
    shell.dataset.phase = "7";
    shell.classList.add("is-frozen");

    window.setTimeout(function () {
      playDelayedSound().finally(function () {
        fadeAndRemove(shell);
      });
    }, Math.max(0, Number(config.soundDelay) || DEFAULT_CONFIG.soundDelay));
  }

  function playDelayedSound() {
    return new Promise(function (resolve) {
      if (!state.audioEnabled) {
        resolve();
        return;
      }

      try {
        var AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) {
          resolve();
          return;
        }
        var context = state.audioContext || new AudioContext();
        state.audioContext = context;
        if (context.state === "suspended") {
          context.resume().catch(function () {});
        }

        var duration = 0.16;
        var sampleRate = context.sampleRate;
        var buffer = context.createBuffer(1, Math.floor(sampleRate * duration), sampleRate);
        var data = buffer.getChannelData(0);
        for (var i = 0; i < data.length; i += 1) {
          var envelope = 1 - i / data.length;
          data[i] = (Math.random() * 2 - 1) * envelope * 0.22;
        }

        var source = context.createBufferSource();
        var filter = context.createBiquadFilter();
        var gain = context.createGain();
        filter.type = "bandpass";
        filter.frequency.value = randomBetween(620, 1150);
        filter.Q.value = 7;
        gain.gain.setValueAtTime(0.0001, context.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.045, context.currentTime + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + duration);
        source.buffer = buffer;
        source.connect(filter);
        filter.connect(gain);
        gain.connect(context.destination);
        source.onended = resolve;
        source.start();
      } catch (error) {
        log("sound skipped", error);
        resolve();
      }
    });
  }

  function fadeAndRemove(shell) {
    if (!shell.isConnected) {
      state.activeWindows = Math.max(0, state.activeWindows - 1);
      return;
    }
    shell.classList.add("is-fading");
    window.setTimeout(function () {
      if (shell._mlwTimers) {
        shell._mlwTimers.forEach(window.clearTimeout);
      }
      shell.remove();
      state.activeWindows = Math.max(0, state.activeWindows - 1);
    }, 760);
  }

  function enableAudio() {
    state.audioEnabled = true;
    document.removeEventListener("pointerdown", enableAudio, true);
    document.removeEventListener("keydown", enableAudio, true);
  }

  function init() {
    config = mergeConfig();
    if (!config.enabled || document.documentElement.dataset.momentLayerWindow === "off") {
      return;
    }
    document.addEventListener("pointerdown", enableAudio, true);
    document.addEventListener("keydown", enableAudio, true);
    scheduleNext();
    log("ready", config);
  }

  window.momentLayerWindow = {
    trigger: function () {
      createWindow();
    },
    reschedule: function () {
      config = mergeConfig();
      scheduleNext();
    },
    destroy: function () {
      window.clearTimeout(state.timer);
      Array.prototype.forEach.call(document.querySelectorAll(".mlw-window"), function (element) {
        element.remove();
      });
      state.activeWindows = 0;
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
