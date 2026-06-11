(() => {
  const node = document.querySelector("[data-external-signal]");
  const startButton = document.querySelector("[data-signal-start]");
  const status = document.querySelector("[data-signal-status]");
  const log = document.querySelector("[data-signal-log]");
  const exit = document.querySelector("[data-signal-exit]");
  const twomiLink = document.querySelector("[data-twomi-link]");
  if (!node || !startButton || !status || !log || !exit) return;

  const wait = (milliseconds) => new Promise((resolve) => {
    window.setTimeout(resolve, milliseconds);
  });

  const setLog = (...lines) => {
    log.replaceChildren(...lines.map((line) => {
      const paragraph = document.createElement("p");
      paragraph.textContent = line;
      return paragraph;
    }));
  };

  const track = (eventName, params = {}) => {
    if (typeof window.gtag === "function") {
      window.gtag("event", eventName, params);
    }
  };

  startButton.addEventListener("click", async () => {
    startButton.disabled = true;
    startButton.textContent = "通信中";
    status.textContent = "接続処理";
    node.dataset.phase = "contact";
    track("external_persona_start", { source_page: "/external-signal" });

    setLog("外部人格：……聞こえています。", "こちらでは、あなたの輪郭だけが見えます。");
    await wait(2100);
    setLog("外部人格：名前は、接続してから決めてもいいです。", "外部人格：もう少しだけ、話せますか。");
    await wait(2500);
    status.textContent = "通信障害";
    setLog("警告：境界外ノイズが増加しています。", "外部人格：待って。まだ、あなたのことを――");
    await wait(1800);
    node.dataset.phase = "lost";
    status.textContent = "接続維持不可";
    setLog("映像途絶", "通信の続きは外部側に残されています。");
    exit.hidden = false;
    startButton.textContent = "通信終了";
  });

  twomiLink?.addEventListener("click", () => {
    track("affiliate_outbound_click", {
      affiliate_provider: "A8",
      destination: "Twomi",
      source_page: "/external-signal",
    });
    fetch("/api/signal-click", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      keepalive: true,
      body: JSON.stringify({
        slot_name: "twomi_external_persona",
        signal_id: 27395002,
        provider: "A8",
      }),
    }).catch(() => {});
  });
})();
