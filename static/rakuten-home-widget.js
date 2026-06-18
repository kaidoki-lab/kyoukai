(function () {
  "use strict";

  var desktopQuery = window.matchMedia("(min-width: 769px)");
  if (!desktopQuery.matches) return;

  var mount = document.querySelector("[data-rakuten-home-widget]");
  if (!mount) return;

  var widgetWidth = 300;
  var widgetHeight = 160;

  var iframe = document.createElement("iframe");
  iframe.title = "楽天広告";
  iframe.loading = "lazy";
  iframe.referrerPolicy = "no-referrer-when-downgrade";
  iframe.setAttribute("scrolling", "no");
  iframe.setAttribute("aria-label", "楽天広告");
  iframe.srcdoc = [
    "<!doctype html>",
    "<html lang=\"ja\">",
    "<head>",
    "<meta charset=\"utf-8\">",
    "<meta name=\"viewport\" content=\"width=" + widgetWidth + ", initial-scale=1\">",
    "<style>",
    "html,body{width:" + widgetWidth + "px;height:" + widgetHeight + "px;margin:0;overflow:hidden;background:#050505;}",
    "body{display:block;}",
    "a,img,iframe{max-width:" + widgetWidth + "px!important;}",
    "</style>",
    "</head>",
    "<body>",
    "<script type=\"text/javascript\">",
    "rakuten_design=\"slide\";",
    "rakuten_affiliateId=\"54f69915.48152f01.54f69916.13ac2b57\";",
    "rakuten_items=\"ctsmatch\";",
    "rakuten_genreId=\"0\";",
    "rakuten_size=\"300x160\";",
    "rakuten_target=\"_blank\";",
    "rakuten_theme=\"gray\";",
    "rakuten_border=\"off\";",
    "rakuten_auto_mode=\"on\";",
    "rakuten_genre_title=\"off\";",
    "rakuten_recommend=\"on\";",
    "rakuten_ts=\"1781800988556\";",
    "<\/script>",
    "<script type=\"text/javascript\" src=\"https://xml.affiliate.rakuten.co.jp/widget/js/rakuten_widget.js?20230106\"><\/script>",
    "</body>",
    "</html>"
  ].join("");

  mount.replaceChildren(iframe);

  function fitWidget() {
    var scale = Math.min(mount.clientWidth / widgetWidth, mount.clientHeight / widgetHeight);
    iframe.style.left = ((mount.clientWidth - widgetWidth * scale) / 2).toFixed(2) + "px";
    iframe.style.top = ((mount.clientHeight - widgetHeight * scale) / 2).toFixed(2) + "px";
    iframe.style.transform = "scale(" + scale.toFixed(4) + ")";
  }

  fitWidget();
  window.addEventListener("resize", fitWidget);
})();
