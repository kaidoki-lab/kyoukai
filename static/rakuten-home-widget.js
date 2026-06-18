(function () {
  "use strict";

  var desktopQuery = window.matchMedia("(min-width: 769px)");
  if (!desktopQuery.matches) return;

  var mount = document.querySelector("[data-rakuten-home-widget]");
  if (!mount) return;

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
    "<meta name=\"viewport\" content=\"width=300, initial-scale=1\">",
    "<style>",
    "html,body{width:300px;height:250px;margin:0;overflow:hidden;background:#050505;}",
    "body{display:block;}",
    "a,img,iframe{max-width:300px!important;}",
    "</style>",
    "</head>",
    "<body>",
    "<script type=\"text/javascript\">",
    "rakuten_design=\"slide\";",
    "rakuten_affiliateId=\"54f69915.48152f01.54f69916.13ac2b57\";",
    "rakuten_items=\"ctsmatch\";",
    "rakuten_genreId=\"0\";",
    "rakuten_size=\"300x250\";",
    "rakuten_target=\"_blank\";",
    "rakuten_theme=\"gray\";",
    "rakuten_border=\"off\";",
    "rakuten_auto_mode=\"on\";",
    "rakuten_genre_title=\"off\";",
    "rakuten_recommend=\"on\";",
    "rakuten_ts=\"1781797224398\";",
    "<\/script>",
    "<script type=\"text/javascript\" src=\"https://xml.affiliate.rakuten.co.jp/widget/js/rakuten_widget.js?20230106\"><\/script>",
    "</body>",
    "</html>"
  ].join("");

  mount.replaceChildren(iframe);
})();
