(() => {
  const BOUNDARY_IMAGE_SRC = "/static/images/external-boundary.png";
  const CONNECTING_DURATION = 2000;
  const LEAVING_DURATION = 950;
  const CANCELLED_DURATION = 720;
  const CHOICE_TEXT = "追いかけますか？";
  const LEAVING_TEXT = "境界外へ移動します";
  const CANCELLED_TEXT = "接続を中断しました";

  const node = document.querySelector("[data-external-signal]");
  const hotspot = document.querySelector("[data-boundary-hotspot]");
  const command = document.querySelector("[data-boundary-command]");
  const commandText = document.querySelector("[data-command-text]");
  const followLink = document.querySelector("[data-follow-boundary]");
  const cancelButton = document.querySelector("[data-cancel-boundary]");
  const status = document.querySelector("[data-boundary-status]");
  if (!node || !hotspot || !command || !commandText || !followLink || !cancelButton || !status) {
    return;
  }

  const AFFILIATE_URL = node.dataset.affiliateUrl || followLink.href;
  const wait = (milliseconds) => new Promise((resolve) => {
    window.setTimeout(resolve, milliseconds);
  });

  const track = (eventName, params = {}) => {
    if (typeof window.trackKyoukaiEvent === "function") {
      window.trackKyoukaiEvent(eventName, params);
    } else if (typeof window.gtag === "function") {
      window.gtag("event", eventName, params);
    }
  };

  const setState = (state) => {
    node.dataset.state = state;
  };

  const setOptionsDisabled = (disabled) => {
    cancelButton.disabled = disabled;
    followLink.setAttribute("aria-disabled", String(disabled));
  };

  const hideCommand = () => {
    command.classList.remove("is-visible");
    command.hidden = true;
  };

  const showCommand = () => {
    commandText.textContent = CHOICE_TEXT;
    command.hidden = false;
    command.classList.add("is-visible");
    setOptionsDisabled(false);
    followLink.focus({ preventScroll: true });
  };

  const resetBoundary = () => {
    hideCommand();
    commandText.textContent = CHOICE_TEXT;
    status.textContent = "";
    setOptionsDisabled(false);
    setState("idle");
    hotspot.disabled = false;
  };

  hotspot.addEventListener("click", async () => {
    if (node.dataset.state !== "idle") return;

    hotspot.disabled = true;
    status.textContent = "境界外信号を追跡しています";
    track("signal_hotspot_click", { source_page: "/external-signal" });
    setState("connecting");
    track("external_boundary_start", {
      source_page: "/external-signal",
      boundary_image: BOUNDARY_IMAGE_SRC,
    });
    track("external_connection_start", {
      source_page: "/external-signal",
      boundary_image: BOUNDARY_IMAGE_SRC,
    });

    await wait(CONNECTING_DURATION);
    status.textContent = "";
    setState("choice");
    showCommand();
    track("external_connection_choice_show", { source_page: "/external-signal" });
  });

  cancelButton.addEventListener("click", async () => {
    if (node.dataset.state !== "choice") return;

    setOptionsDisabled(true);
    commandText.textContent = CANCELLED_TEXT;
    status.textContent = CANCELLED_TEXT;
    setState("cancelled");
    track("external_boundary_cancel", { source_page: "/external-signal" });
    track("external_connection_cancel", { source_page: "/external-signal" });

    await wait(CANCELLED_DURATION);
    resetBoundary();
  });

  followLink.addEventListener("click", async (event) => {
    event.preventDefault();
    if (node.dataset.state !== "choice") return;

    setOptionsDisabled(true);
    commandText.textContent = LEAVING_TEXT;
    status.textContent = "接続を追跡しています";
    setState("leaving");
    track("affiliate_outbound_click", {
      affiliate_provider: "A8",
      destination: "Twomi",
      source_page: "/external-signal",
    });
    track("external_connection_follow", {
      affiliate_provider: "A8",
      destination: "Twomi",
      source_page: "/external-signal",
    });
    fetch("/api/signal-click", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      keepalive: true,
      body: JSON.stringify({
        slot_name: "twomi_external_boundary",
        signal_id: 27395002,
        provider: "A8",
      }),
    }).catch(() => {});

    await wait(LEAVING_DURATION);
    window.location.assign(AFFILIATE_URL);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && node.dataset.state === "choice") {
      cancelButton.click();
    }
  });
})();
