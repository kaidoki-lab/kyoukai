(function () {
  const CONFIG_URL = "/api/site-config";
  const GA_ID_PATTERN = /^G-[A-Z0-9]+$/i;

  // KYOUKAI共通イベント送信関数。
  // GA4が未起動でも安全に呼べる（gtag未定義時は何もしない）。
  window.trackKyoukaiEvent = function (eventName, params) {
    if (typeof window.gtag !== "function") return;
    const payload = Object.assign({}, params || {}, {
      page_path: window.location.pathname,
      page_title: document.title,
      timestamp: new Date().toISOString()
    });
    window.gtag("event", eventName, payload);
  };

  function loadScript(src) {
    const script = document.createElement("script");
    script.async = true;
    script.src = src;
    document.head.appendChild(script);
  }

  function fireRoomEnterEvent() {
    // window.KYOUKAI_ROOM は各ページのインラインscriptで設定済み（bgm.js / kyoukai-guide.js と共通利用）
    const room = typeof window.KYOUKAI_ROOM === "string" ? window.KYOUKAI_ROOM.trim() : "";
    if (!room || room === "central") return;
    window.trackKyoukaiEvent("room_enter_" + room, {
      room_name: room,
      room_type: "public_room"
    });
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

    fireRoomEnterEvent();
  }

  fetch(CONFIG_URL, { cache: "no-store" })
    .then((response) => (response.ok ? response.json() : null))
    .then((config) => {
      if (!config || !config.analytics) return;
      startAnalytics(config.analytics.gaMeasurementId);
    })
    .catch(() => {});
})();
