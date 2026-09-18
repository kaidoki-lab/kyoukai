(function () {
  "use strict";

  var player = null;
  var duration = 0;
  var started = false;
  var hintEl = null;
  var playerWrap = null;

  function getVideoId() {
    return playerWrap ? playerWrap.getAttribute("data-video-id") || "" : "";
  }

  function hideHint() {
    if (hintEl && !hintEl.classList.contains("is-hidden")) {
      hintEl.classList.add("is-hidden");
    }
  }

  function refreshDuration() {
    if (!player || typeof player.getDuration !== "function") return;
    var d = player.getDuration();
    if (d && d > 0) {
      duration = d;
    }
  }

  function onPlayerReady() {
    refreshDuration();
  }

  function onPlayerStateChange(event) {
    if (window.YT && event && event.data === window.YT.PlayerState.PLAYING) {
      refreshDuration();
      started = true;
      hideHint();
    }
  }

  // 初回タップは再生開始のみを行う(iOS/Androidの自動再生制限対策)。
  // PLAYING を確認して以降はシークを許可する。
  function jump(key) {
    if (!player) return;

    if (!started) {
      if (typeof player.playVideo === "function") {
        player.playVideo();
      }
      flashPad(key);
      return;
    }

    if (!duration) {
      refreshDuration();
    }

    if (duration > 0 && typeof player.seekTo === "function") {
      player.seekTo((duration * key) / 10, true);
    }

    if (
      window.YT &&
      typeof player.getPlayerState === "function" &&
      player.getPlayerState() !== window.YT.PlayerState.PLAYING &&
      typeof player.playVideo === "function"
    ) {
      player.playVideo();
    }

    flashPad(key);
  }

  function flashPad(key) {
    var pad = document.querySelector('.seekpad-pad[data-key="' + key + '"]');
    if (!pad) return;
    pad.classList.add("is-hit");
    window.setTimeout(function () {
      pad.classList.remove("is-hit");
    }, 60);
  }

  function keyToNumber(rawKey) {
    if (typeof rawKey !== "string" || rawKey.length !== 1) return null;
    if (rawKey < "0" || rawKey > "9") return null;
    return Number(rawKey);
  }

  window.onYouTubeIframeAPIReady = function () {
    playerWrap = document.querySelector(".seekpad-player-wrap");
    hintEl = document.getElementById("seekpad-hint");
    var videoId = getVideoId();

    if (!window.YT || !window.YT.Player) {
      return;
    }

    try {
      player = new window.YT.Player("player", {
        videoId: videoId,
        playerVars: {
          playsinline: 1,
          rel: 0,
          controls: 1
        },
        events: {
          onReady: onPlayerReady,
          onStateChange: onPlayerStateChange
        }
      });
    } catch (err) {
      player = null;
    }
  };

  function bindPads() {
    var pads = document.querySelectorAll(".seekpad-pad");
    pads.forEach(function (pad) {
      pad.addEventListener("pointerdown", function () {
        var key = Number(pad.getAttribute("data-key"));
        jump(key);
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (!playerWrap) {
      playerWrap = document.querySelector(".seekpad-player-wrap");
    }
    if (!hintEl) {
      hintEl = document.getElementById("seekpad-hint");
    }
    bindPads();
  });

  document.addEventListener("keydown", function (e) {
    var num = keyToNumber(e.key);
    if (num === null) return;
    e.preventDefault();
    jump(num);
  });
})();
