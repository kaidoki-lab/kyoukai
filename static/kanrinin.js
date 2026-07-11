(function () {
  const LINKS = {
    ofuse: "https://ofuse.me/be78f6ed",
    booth: "https://voidscan.booth.pm/",
    crowdfunding: "https://motion-gallery.net/projects/kyoukai",
    // 消滅の鍵の遷移先。意図的に存在しないパスへ送り、グローバル404演出（templates/404.html, kyoukai-404.js）を発生させる。
    exit: "/kanrinin/deleted",
  };

  const SNS_LINKS = [
    { label: "X", href: "https://x.com/maro1523095" },
    { label: "TikTok", href: "https://www.tiktok.com/@kyoukai.archive?_r=1&_t=ZS-97a3TX3JqCO" },
    { label: "YouTube", href: "https://youtube.com/@hetayoko1109?si=tcc7YX7UgNNtLk8w" },
  ];

  const BELL_MESSAGES = [
    "……。",
    "少々お待ちください。",
    "管理人を呼んでいます。",
    "鍵を確認しています。",
    "現在、奥で処理中です。",
  ];

  // 本文は static/kanrinin-diary.json で管理する（コード変更なしで文章だけ更新できるようにするため）。
  const DIARY_DATA_URL = "/static/kanrinin-diary.json";
  let diaryPages = [];
  let currentDiaryIndex = 0;

  const eyeGap = document.getElementById("kanrininEyeGap");
  const messageEl = document.getElementById("kanrininMessage");
  const keyBoxModal = document.getElementById("keyBoxModal");
  const keyBoxModalClose = document.getElementById("keyBoxModalClose");
  const snsModal = document.getElementById("snsModal");
  const snsModalClose = document.getElementById("snsModalClose");
  const snsModalList = document.getElementById("snsModalList");
  const diaryModal = document.getElementById("diaryModal");
  const diaryClose = document.getElementById("diaryClose");
  const diaryCategoryEl = document.getElementById("diaryCategory");
  const diaryTitleEl = document.getElementById("diaryTitle");
  const diaryBodyEl = document.getElementById("diaryBody");
  const diaryPageCountEl = document.getElementById("diaryPageCount");
  const diaryPrevBtn = document.getElementById("diaryPrev");
  const diaryNextBtn = document.getElementById("diaryNext");
  const blackout = document.getElementById("kanrininBlackout");
  const redPhoneArea = document.getElementById("redPhoneArea");
  const managerPresence = document.getElementById("kanrininManagerPresence");

  let messageTimer = null;
  let revealTimer = null;
  let phoneTimer = null;
  let phoneAudio = null;
  let activePhoneEvent = null;
  let phoneRinging = false;
  let scenarioLineActive = false;
  let phoneAnswerLocked = false;
  const EYE_REVEAL_MS = 3000;
  const PHONE_CHECK_DELAY_MS = 20000;
  const PHONE_RESUME_DELAY_MS = 1500;

  function trackArea(area) {
    if (typeof window.trackKyoukaiEvent === "function") {
      window.trackKyoukaiEvent("kanrinin_area_click", { area });
    }
  }

  function showMessage(text, duration, options) {
    if (!messageEl) return;
    const config = options || {};
    window.clearTimeout(messageTimer);
    messageEl.textContent = "";
    messageEl.classList.toggle("kanrinin-message--dialogue", Boolean(config.speaker));
    if (config.speaker) {
      const speakerEl = document.createElement("span");
      speakerEl.className = "kanrinin-message__speaker";
      speakerEl.textContent = config.speaker;
      const textEl = document.createElement("span");
      textEl.className = "kanrinin-message__text";
      textEl.textContent = text;
      messageEl.append(speakerEl, textEl);
    } else {
      messageEl.textContent = text;
    }
    messageEl.classList.add("is-visible");
    if (duration !== 0) {
      messageTimer = window.setTimeout(() => {
        messageEl.classList.remove("is-visible");
        messageEl.classList.remove("kanrinin-message--dialogue");
      }, duration || 2600);
    }
  }

  function stopPhoneAudio() {
    if (!phoneAudio) return;
    phoneAudio.pause();
    phoneAudio.currentTime = 0;
    phoneAudio = null;
  }

  function playPhoneAudio(eventData) {
    stopPhoneAudio();
    const source = eventData?.phone_config?.ring_audio;
    if (!source) return;
    phoneAudio = new Audio(source);
    phoneAudio.loop = true;
    phoneAudio.volume = 0.36;
    phoneAudio.play().catch((error) => {
      console.warn("[KYOUKAI] red phone audio unavailable:", error);
      stopPhoneAudio();
    });
  }

  function normalizeLine(line) {
    if (!line) return null;
    if (typeof line === "string") return { text: line, speaker: "" };
    return { text: line.text || "", speaker: line.speaker || "" };
  }

  function playScenarioLines(lines, options) {
    const list = (Array.isArray(lines) ? lines : []).map(normalizeLine).filter((line) => line && line.text);
    const config = options || {};
    const autoAdvance = config.autoAdvance !== false;
    const speakerLabel = config.speakerLabel || "";
    let index = 0;
    let advanceTimer = null;
    scenarioLineActive = true;

    function cleanup() {
      window.clearTimeout(advanceTimer);
      document.removeEventListener("click", advance);
      document.removeEventListener("keydown", advanceByKey);
      scenarioLineActive = false;
    }

    function finish() {
      cleanup();
      if (typeof config.onComplete === "function") config.onComplete();
    }

    function showCurrent() {
      if (index >= list.length) {
        finish();
        return;
      }
      const line = list[index];
      showMessage(line.text, autoAdvance ? config.lineDuration || 2800 : 0, {
        speaker: speakerLabel || (!autoAdvance ? line.speaker : ""),
      });
      index += 1;
      window.clearTimeout(advanceTimer);
      if (autoAdvance) {
        advanceTimer = window.setTimeout(showCurrent, config.lineDuration || 2800);
      }
    }

    function advance(event) {
      if (event && redPhoneArea && event.target === redPhoneArea) return;
      window.clearTimeout(advanceTimer);
      showCurrent();
    }

    function advanceByKey(event) {
      if (event.key === "Escape") return;
      advance(event);
    }

    if (!list.length) {
      finish();
      return;
    }
    document.addEventListener("click", advance);
    document.addEventListener("keydown", advanceByKey);
    showCurrent();
  }

  function revealEye() {
    if (!eyeGap) return;
    eyeGap.classList.add("is-revealed");
    window.clearTimeout(revealTimer);
    revealTimer = window.setTimeout(() => {
      eyeGap.classList.remove("is-revealed");
    }, EYE_REVEAL_MS);
  }

  function openExternal(url) {
    window.open(url, "_blank", "noopener,noreferrer");
  }

  function openKeyBoxModal() {
    if (!keyBoxModal) return;
    keyBoxModal.classList.add("is-open");
    keyBoxModal.setAttribute("aria-hidden", "false");
  }

  function closeKeyBoxModal() {
    if (!keyBoxModal) return;
    keyBoxModal.classList.remove("is-open");
    keyBoxModal.setAttribute("aria-hidden", "true");
  }

  function openSnsModal() {
    if (!snsModal) return;
    if (snsModalList && !snsModalList.childElementCount) {
      SNS_LINKS.forEach((link) => {
        const item = document.createElement("li");
        const anchor = document.createElement("a");
        anchor.href = link.href;
        anchor.target = "_blank";
        anchor.rel = "noopener noreferrer";
        anchor.textContent = link.label;
        item.append(anchor);
        snsModalList.append(item);
      });
    }
    snsModal.classList.add("is-open");
    snsModal.setAttribute("aria-hidden", "false");
  }

  function closeSnsModal() {
    if (!snsModal) return;
    snsModal.classList.remove("is-open");
    snsModal.setAttribute("aria-hidden", "true");
  }

  function renderDiaryPage() {
    const page = diaryPages[currentDiaryIndex];
    if (!page) return;
    if (diaryCategoryEl) diaryCategoryEl.textContent = page.category;
    if (diaryTitleEl) diaryTitleEl.textContent = page.title;
    if (diaryBodyEl) diaryBodyEl.textContent = page.body;
    if (diaryPageCountEl) {
      diaryPageCountEl.textContent = `${currentDiaryIndex + 1} / ${diaryPages.length}`;
    }
    if (diaryPrevBtn) diaryPrevBtn.disabled = currentDiaryIndex === 0;
    if (diaryNextBtn) diaryNextBtn.disabled = currentDiaryIndex === diaryPages.length - 1;
  }

  function showDiaryModal() {
    if (!diaryModal) return;
    currentDiaryIndex = 0;
    renderDiaryPage();
    diaryModal.classList.add("is-open");
    diaryModal.setAttribute("aria-hidden", "false");
  }

  function mergeScenarioDiaryPages(basePages) {
    const scenarioPages = window.KYOUKAI_SCENARIO
      ? window.KYOUKAI_SCENARIO.getDiaryEntries()
      : [];
    const seen = new Set();
    return [...basePages, ...scenarioPages].filter((page) => {
      const key = page.entry_id || `${page.category}:${page.title}:${page.body}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  function openDiary() {
    if (diaryPages.length) {
      diaryPages = mergeScenarioDiaryPages(diaryPages);
      showDiaryModal();
      return;
    }
    if (diaryBodyEl) diaryBodyEl.textContent = "……読み込み中。";
    fetch(DIARY_DATA_URL)
      .then((response) => response.json())
      .then((data) => {
        const basePages = Array.isArray(data) ? data : [];
        diaryPages = mergeScenarioDiaryPages(basePages);
        showDiaryModal();
      })
      .catch(() => {
        diaryPages = [];
        if (diaryBodyEl) diaryBodyEl.textContent = "管理日誌を読み込めませんでした。";
      });
  }

  function closeDiary() {
    if (!diaryModal) return;
    diaryModal.classList.remove("is-open");
    diaryModal.setAttribute("aria-hidden", "true");
  }

  function nextDiaryPage() {
    if (currentDiaryIndex < diaryPages.length - 1) {
      currentDiaryIndex += 1;
      renderDiaryPage();
    }
  }

  function prevDiaryPage() {
    if (currentDiaryIndex > 0) {
      currentDiaryIndex -= 1;
      renderDiaryPage();
    }
  }

  function runAnnihilation() {
    window.clearTimeout(revealTimer);
    if (eyeGap) eyeGap.classList.add("is-revealed");
    showMessage("管理人が鍵を回しました。", 4000);
    trackArea("annihilation");
    window.setTimeout(() => {
      if (!blackout) {
        window.location.href = LINKS.exit;
        return;
      }
      blackout.classList.add("is-active");
      window.setTimeout(() => {
        window.location.href = LINKS.exit;
      }, 1500);
    }, 400);
  }

  function bindArea(id, handler) {
    const node = document.getElementById(id);
    if (!node) return;
    node.addEventListener("click", (event) => {
      if (scenarioLineActive && id !== "redPhoneArea") return;
      handler(event);
    });
  }

  bindArea("ofuseArea", () => {
    trackArea("ofuse");
    openExternal(LINKS.ofuse);
  });

  bindArea("boothArea", () => {
    trackArea("booth");
    openExternal(LINKS.booth);
  });

  bindArea("crowdfundingArea", () => {
    trackArea("crowdfunding");
    openExternal(LINKS.crowdfunding);
  });

  bindArea("snsArea", () => {
    trackArea("sns");
    openSnsModal();
  });

  bindArea("bellArea", () => {
    trackArea("bell");
    revealEye();
    const message = BELL_MESSAGES[Math.floor(Math.random() * BELL_MESSAGES.length)];
    showMessage(message);
  });

  bindArea("keyBoxArea", () => {
    trackArea("keybox");
    openKeyBoxModal();
  });

  bindArea("annihilationKeyArea", runAnnihilation);

  bindArea("noteArea", () => {
    trackArea("note");
    openDiary();
  });

  bindArea("amazonArea", () => {
    trackArea("amazon");
    const links = Array.isArray(window.KYOUKAI_OUTSIDE_AMAZON_LINKS)
      ? window.KYOUKAI_OUTSIDE_AMAZON_LINKS.filter(Boolean)
      : [];
    const url = links.length ? links[Math.floor(Math.random() * links.length)] : "https://www.amazon.co.jp/";
    window.open(url, "_blank", "noopener,noreferrer");
  });

  bindArea("rakutenArea", () => {
    trackArea("rakuten");
  });

  function setPhoneRinging(eventData) {
    activePhoneEvent = eventData;
    phoneRinging = Boolean(eventData);
    if (redPhoneArea) redPhoneArea.classList.toggle("is-ringing", phoneRinging);
    if (phoneRinging) {
      window.KYOUKAI_SCENARIO?.startPhoneRinging(eventData.event_id);
      playPhoneAudio(eventData);
      showMessage("赤い電話が鳴っている。", 5000);
    } else {
      stopPhoneAudio();
    }
  }

  function syncManagerPresence() {
    if (!managerPresence || !window.KYOUKAI_SCENARIO) return;
    const state = window.KYOUKAI_SCENARIO.getState();
    const visible = ["visible", "busy"].includes(state.manager_state);
    managerPresence.classList.toggle("is-visible", visible);
    managerPresence.classList.toggle("is-busy", state.manager_state === "busy");
  }

  function schedulePhoneCheck() {
    if (!redPhoneArea || !window.KYOUKAI_SCENARIO) return;
    const state = window.KYOUKAI_SCENARIO.getState();
    if (state.mode !== "scenario") return;
    if (window.KYOUKAI_SCENARIO.getManagerEvent("kanrinin")) return;
    window.KYOUKAI_SCENARIO.startPhoneWait();
    const elapsedSeconds = window.KYOUKAI_SCENARIO.getPhoneWaitSeconds();
    const isRouteEResume =
      state.active_route_id === "route_e" &&
      state.route_status?.route_e === "active" &&
      state.route_e_phone_completed !== true &&
      state.ending_completed !== true;
    const requiredDelayMs = isRouteEResume ? PHONE_RESUME_DELAY_MS : PHONE_CHECK_DELAY_MS;
    const remainingMs = Math.max(0, requiredDelayMs - elapsedSeconds * 1000);
    window.clearTimeout(phoneTimer);
    phoneTimer = window.setTimeout(() => {
      const nextEvent = window.KYOUKAI_SCENARIO.getNextPhoneEvent({
        roomStaySeconds: Math.max(requiredDelayMs / 1000, window.KYOUKAI_SCENARIO.getPhoneWaitSeconds()),
      });
      if (nextEvent) {
        setPhoneRinging(nextEvent);
      } else {
        phoneTimer = window.setTimeout(schedulePhoneCheck, 10000);
      }
    }, remainingMs);
  }

  bindArea("redPhoneArea", () => {
    trackArea("red-phone");
    if (!window.KYOUKAI_SCENARIO) return;
    if (scenarioLineActive) return;
    if (phoneAnswerLocked) return;
    if (!phoneRinging || !activePhoneEvent) {
      showMessage("電話は沈黙している。", 2400);
      return;
    }
    phoneAnswerLocked = true;
    const eventData = window.KYOUKAI_SCENARIO.acceptPhoneEvent(activePhoneEvent.event_id);
    if (!eventData) {
      phoneAnswerLocked = false;
      return;
    }
    setPhoneRinging(null);
    const isFinalPhone = eventData.event_id === "route_e_phone_001";
    playScenarioLines(eventData.conversation, {
      lineDuration: isFinalPhone ? 0 : 3000,
      autoAdvance: !isFinalPhone,
      speakerLabel: isFinalPhone ? eventData.caller_display_name || "記録なし" : "",
      onComplete: () => {
        window.KYOUKAI_SCENARIO.finishPhoneEvent(eventData.event_id);
        phoneAnswerLocked = false;
        if (isFinalPhone) {
          showMessage("最上階が開放されました。", 3200);
          return;
        }
        showMessage("受話器が、静かに戻った。", 2600);
      },
    });
  });

  document.addEventListener("kyoukai:scenario-notice", (event) => {
    if (!event.detail || !event.detail.message) return;
    event.preventDefault();
    showMessage(event.detail.message, 4200);
  });

  function runManagerReturnIfReady() {
    if (!window.KYOUKAI_SCENARIO) return false;
    const managerEvent = window.KYOUKAI_SCENARIO.getManagerEvent("kanrinin");
    if (!managerEvent) return false;
    const sequence = Array.isArray(managerEvent.manager_state_sequence)
      ? managerEvent.manager_state_sequence
      : ["visible"];
    const state = window.KYOUKAI_SCENARIO.getState();
    state.manager_state = sequence[1] || "visible";
    window.KYOUKAI_SCENARIO.saveState(state);
    syncManagerPresence();
    playScenarioLines(managerEvent.conversation, {
      lineDuration: 3200,
      onComplete: () => {
        const next = window.KYOUKAI_SCENARIO.getState();
        next.manager_state = sequence[sequence.length - 1] || "visible";
        window.KYOUKAI_SCENARIO.saveState(next);
        syncManagerPresence();
        window.KYOUKAI_SCENARIO.completeScenarioEvent(managerEvent.event_id, {
          sequenceEventId: managerEvent.event_id,
        });
        showMessage("上階の閉鎖が、一つだけ解かれた。", 3600);
      },
    });
    return true;
  }

  if (!runManagerReturnIfReady()) {
    schedulePhoneCheck();
  }

  document.addEventListener("kyoukai:scenario-state", syncManagerPresence);
  syncManagerPresence();

  window.addEventListener("pagehide", () => {
    window.clearTimeout(phoneTimer);
    if (window.KYOUKAI_SCENARIO) {
      const state = window.KYOUKAI_SCENARIO.getState();
      const routeEWaiting =
        state.final_route_available === true &&
        state.route_status?.route_e === "available" &&
        state.active_route_id === null &&
        state.ending_completed !== true;
      const routeEConversationIncomplete =
        state.route_status?.route_e === "active" &&
        state.active_route_id === "route_e" &&
        state.route_e_phone_completed !== true &&
        state.ending_completed !== true;
      if (!phoneRinging && (routeEWaiting || routeEConversationIncomplete)) {
        window.KYOUKAI_SCENARIO.resetPhoneWait?.();
      }
      if (routeEConversationIncomplete) {
        state.phone_state = "idle";
        state.active_phone_event_id = null;
        state.current_event = null;
        state.phone_wait_started_at = null;
        state.route_e_phone_answer_lock = false;
        state.top_floor_unlocked = false;
        window.KYOUKAI_SCENARIO.saveState(state);
      }
    }
    if (phoneRinging) window.KYOUKAI_SCENARIO?.cancelPhoneRinging();
    stopPhoneAudio();
  });

  if (keyBoxModalClose) {
    keyBoxModalClose.addEventListener("click", closeKeyBoxModal);
  }
  if (keyBoxModal) {
    keyBoxModal.addEventListener("click", (event) => {
      if (event.target === keyBoxModal) closeKeyBoxModal();
    });
  }

  if (snsModalClose) {
    snsModalClose.addEventListener("click", closeSnsModal);
  }
  if (snsModal) {
    snsModal.addEventListener("click", (event) => {
      if (event.target === snsModal) closeSnsModal();
    });
  }

  if (diaryClose) {
    diaryClose.addEventListener("click", closeDiary);
  }
  if (diaryModal) {
    diaryModal.addEventListener("click", (event) => {
      if (event.target === diaryModal) closeDiary();
    });
  }
  if (diaryPrevBtn) {
    diaryPrevBtn.addEventListener("click", prevDiaryPage);
  }
  if (diaryNextBtn) {
    diaryNextBtn.addEventListener("click", nextDiaryPage);
  }
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeDiary();
  });
})();
