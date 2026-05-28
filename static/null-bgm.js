(function () {
  "use strict";

  var audio = null;
  var started = false;

  function ensureAudio() {
    if (audio) return audio;
    audio = new Audio("/static/bgm/bgm_null.mp3");
    audio.loop = true;
    audio.preload = "auto";
    audio.volume = 0.16;
    return audio;
  }

  function startNullBgm() {
    if (started) return;
    started = true;
    ensureAudio().play().catch(function () {
      started = false;
    });
  }

  function boot() {
    ensureAudio();
    document.addEventListener("click", startNullBgm, { once: true });
    document.addEventListener("touchstart", startNullBgm, { once: true });
    document.addEventListener("keydown", startNullBgm, { once: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
