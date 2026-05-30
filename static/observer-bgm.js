(function () {
  "use strict";

  var audio = null;
  var started = false;

  function ensureAudio() {
    if (audio) return audio;
    audio = new Audio("/static/bgm/bgm_observer.mp3");
    audio.loop = true;
    audio.preload = "auto";
    audio.volume = 0.09;
    return audio;
  }

  function startObserverBgm() {
    if (started) return;
    started = true;
    ensureAudio().play().catch(function () {
      started = false;
    });
  }

  function boot() {
    ensureAudio();
    document.addEventListener("click", startObserverBgm, { once: true });
    document.addEventListener("touchstart", startObserverBgm, { once: true });
    document.addEventListener("keydown", startObserverBgm, { once: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
