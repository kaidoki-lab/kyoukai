(function () {
  "use strict";

  var desktopQuery = window.matchMedia("(min-width: 769px)");
  if (!desktopQuery.matches) return;

  var layer = document.querySelector("[data-altar-electric]");
  if (!layer) return;

  var paths = [
    ["7%", "20%", "12%", -6], ["14%", "34%", "13%", 83], ["20%", "27%", "12%", -8],
    ["30%", "13%", "14%", 88], ["37%", "18%", "12%", 2], ["47%", "20%", "15%", -1],
    ["55%", "23%", "12%", 88], ["64%", "18%", "12%", 86], ["76%", "18%", "13%", -8],
    ["87%", "28%", "13%", 84], ["92%", "45%", "15%", 84], ["18%", "55%", "14%", -2],
    ["30%", "55%", "12%", 2], ["43%", "52%", "12%", 88], ["53%", "54%", "12%", 88],
    ["64%", "52%", "12%", 82], ["72%", "59%", "16%", -1], ["82%", "61%", "14%", -3],
    ["11%", "76%", "14%", 2], ["26%", "83%", "12%", -4], ["38%", "82%", "12%", 0],
    ["50%", "79%", "15%", -1], ["62%", "80%", "12%", 88], ["73%", "78%", "16%", 0],
    ["84%", "76%", "13%", 85], ["92%", "70%", "12%", 84]
  ];

  function rand(min, max) {
    return min + Math.random() * (max - min);
  }

  function spawnBolt() {
    var path = paths[Math.floor(Math.random() * paths.length)];
    var bolt = document.createElement("span");
    bolt.className = "altar-electric-bolt";
    bolt.style.setProperty("--bolt-x", path[0]);
    bolt.style.setProperty("--bolt-y", path[1]);
    bolt.style.setProperty("--bolt-w", path[2]);
    bolt.style.setProperty("--bolt-r", (path[3] + rand(-5, 5)).toFixed(2) + "deg");
    bolt.style.setProperty("--branch-r", rand(-32, -16).toFixed(2) + "deg");
    bolt.style.setProperty("--bolt-d", Math.round(rand(320, 720)) + "ms");
    bolt.style.setProperty("--bolt-o", rand(0.52, 0.92).toFixed(2));
    layer.appendChild(bolt);

    window.setTimeout(function () {
      bolt.remove();
    }, 900);
  }

  function schedule() {
    var burst = Math.random() > 0.72 ? 2 : 1;
    for (var i = 0; i < burst; i += 1) {
      window.setTimeout(spawnBolt, i * rand(70, 170));
    }
    window.setTimeout(schedule, rand(780, 2400));
  }

  window.setTimeout(schedule, rand(600, 1400));
})();
