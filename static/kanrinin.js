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

  let messageTimer = null;
  let revealTimer = null;
  const EYE_REVEAL_MS = 3000;

  function trackArea(area) {
    if (typeof window.trackKyoukaiEvent === "function") {
      window.trackKyoukaiEvent("kanrinin_area_click", { area });
    }
  }

  function showMessage(text, duration) {
    if (!messageEl) return;
    window.clearTimeout(messageTimer);
    messageEl.textContent = text;
    messageEl.classList.add("is-visible");
    messageTimer = window.setTimeout(() => {
      messageEl.classList.remove("is-visible");
    }, duration || 2600);
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

  function openDiary() {
    if (diaryPages.length) {
      showDiaryModal();
      return;
    }
    if (diaryBodyEl) diaryBodyEl.textContent = "……読み込み中。";
    fetch(DIARY_DATA_URL)
      .then((response) => response.json())
      .then((data) => {
        diaryPages = Array.isArray(data) ? data : [];
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
    node.addEventListener("click", handler);
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
