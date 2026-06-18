(function () {
  "use strict";

  var desktopQuery = window.matchMedia("(min-width: 769px)");
  if (!desktopQuery.matches) return;

  var mount = document.querySelector("[data-rakuten-home-widget]");
  if (!mount) return;

  window.rakuten_design = "slide";
  window.rakuten_affiliateId = "54f69915.48152f01.54f69916.13ac2b57";
  window.rakuten_items = "ctsmatch";
  window.rakuten_genreId = "0";
  window.rakuten_size = "300x250";
  window.rakuten_target = "_blank";
  window.rakuten_theme = "gray";
  window.rakuten_border = "off";
  window.rakuten_auto_mode = "on";
  window.rakuten_genre_title = "off";
  window.rakuten_recommend = "on";
  window.rakuten_ts = "1781797224398";

  var script = document.createElement("script");
  script.type = "text/javascript";
  script.src = "https://xml.affiliate.rakuten.co.jp/widget/js/rakuten_widget.js?20230106";
  mount.appendChild(script);
})();
