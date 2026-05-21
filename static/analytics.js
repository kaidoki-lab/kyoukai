(function () {
  const CONFIG_URL = "/api/site-config";
  const GA_ID_PATTERN = /^G-[A-Z0-9]+$/i;

  function loadScript(src) {
    const script = document.createElement("script");
    script.async = true;
    script.src = src;
    document.head.appendChild(script);
  }

  function startAnalytics(measurementId) {
    const gaMeasurementId = String(measurementId || "").trim();
    if (!GA_ID_PATTERN.test(gaMeasurementId)) return;

    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function gtag() {
      window.dataLayer.push(arguments);
    };

    loadScript("https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(gaMeasurementId));
    window.gtag("js", new Date());
    window.gtag("config", gaMeasurementId, {
      page_location: window.location.href,
      page_path: window.location.pathname + window.location.search,
      send_page_view: true
    });
  }

  fetch(CONFIG_URL, { cache: "no-store" })
    .then((response) => (response.ok ? response.json() : null))
    .then((config) => {
      if (!config || !config.analytics) return;
      startAnalytics(config.analytics.gaMeasurementId);
    })
    .catch(() => {});
})();
