(function () {
  function items() {
    return window.KYOUKAI_OUTSIDE_ITEMS || {};
  }

  function itemGrid() {
    return Array.isArray(window.KYOUKAI_OUTSIDE_GRID) ? window.KYOUKAI_OUTSIDE_GRID : [];
  }

  function amazonLinks() {
    return Array.isArray(window.KYOUKAI_OUTSIDE_AMAZON_LINKS)
      ? window.KYOUKAI_OUTSIDE_AMAZON_LINKS.filter(Boolean)
      : [];
  }

  function randomOutsideLink() {
    const links = amazonLinks();
    if (!links.length) return "#";
    return links[Math.floor(Math.random() * links.length)];
  }

  function normalizeSlotId(value, fallback) {
    return String(value || fallback || "outside_slot")
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "") || "outside_slot";
  }

  function destinationType(item) {
    if (!item) return "unknown";
    if (item.randomAmazon) return "amazon";
    const href = String(item.href || "").toLowerCase();
    if (href.includes("ofuse.me")) return "ofuse";
    if (href.startsWith("http")) return "external";
    return "internal";
  }

  function slotType(item) {
    const destination = destinationType(item);
    if (destination === "amazon") return "amazon";
    if (destination === "ofuse") return "support";
    return destination;
  }

  function applyTrackingAttributes(link, item, id) {
    link.dataset.kyoukaiEvent = "outside_slot_click";
    link.dataset.slotId = normalizeSlotId(item && item.label, id);
    link.dataset.slotType = slotType(item);
    link.dataset.slotLabel = item && item.label || id || "OUTSIDE OBJECT";
    link.dataset.destinationType = destinationType(item);
  }

  function trackOutsideSlotClick(event) {
    const link = event.currentTarget;
    if (!link || typeof window.gtag !== "function") return;
    window.gtag("event", "outside_slot_click", {
      slot_id: link.dataset.slotId || "",
      slot_type: link.dataset.slotType || "",
      slot_label: link.dataset.slotLabel || "",
      destination_type: link.dataset.destinationType || ""
    });
  }

  function prepareRandomLink(event) {
    const link = event.currentTarget;
    if (!link) return;
    link.href = randomOutsideLink();
  }

  function slotPercent(slot, axis, size) {
    const base = axis === "x" || axis === "width" ? 1055 : 1024;
    return `${(slot[axis] / (size || base)) * 100}%`;
  }

  function applyLinkAttributes(link, item) {
    link.href = item.href || "#";
    if (item.target) link.target = item.target;
    if (item.rel) link.rel = item.rel;
    link.setAttribute("aria-label", item.label || "OUTSIDE OBJECT");
  }

  function createFallback(item, id) {
    const fallback = document.createElement("span");
    fallback.className = "outside-icon__fallback";
    fallback.textContent = item.shortLabel || item.label || id || "EMPTY";
    return fallback;
  }

  function createIcon(id, options) {
    const data = items()[id];
    const element = document.createElement(data && (data.randomAmazon || data.href) ? "a" : "span");
    element.className = "outside-icon";
    element.dataset.outsideIconId = id || "";

    if (!data) {
      element.classList.add("outside-icon--empty");
      element.appendChild(createFallback({ shortLabel: "EMPTY" }, id));
      return element;
    }

    if (data.randomAmazon) {
      element.dataset.outsideRandom = "amazon";
      element.setAttribute("aria-label", (data.label || "OUTSIDE OBJECT") + " / random external connection");
      element.href = "#outside-random";
      element.rel = "sponsored";
      applyTrackingAttributes(element, data, id);
      element.addEventListener("pointerdown", prepareRandomLink);
      element.addEventListener("mousedown", prepareRandomLink);
      element.addEventListener("touchstart", prepareRandomLink, { passive: true });
      element.addEventListener("focus", prepareRandomLink);
      element.addEventListener("click", prepareRandomLink);
      element.addEventListener("click", trackOutsideSlotClick);
    } else if (element.tagName === "A") {
      applyLinkAttributes(element, data);
      applyTrackingAttributes(element, data, id);
      element.addEventListener("click", trackOutsideSlotClick);
    }

    const image = document.createElement("img");
    image.className = "outside-icon__image";
    image.alt = "";
    image.loading = "lazy";
    image.src = data.icon || "";
    image.addEventListener("error", function () {
      image.remove();
      if (!element.querySelector(".outside-icon__fallback")) {
        element.prepend(createFallback(data, id));
      }
    }, { once: true });
    element.appendChild(image);

    const label = document.createElement("span");
    label.className = "outside-icon__label";
    label.textContent = data.shortLabel || data.label || id;
    element.appendChild(label);

    if (options && options.withDisclosure && data.disclosure) {
      const disclosure = document.createElement("small");
      disclosure.className = "outside-icon__disclosure";
      disclosure.textContent = data.disclosure;
      element.appendChild(disclosure);
    }

    return element;
  }

  function fallbackSlots() {
    return [
      { index: 1, x: 66, y: 78, width: 178, height: 169 },
      { index: 2, x: 260, y: 78, width: 178, height: 169 },
      { index: 3, x: 454, y: 78, width: 178, height: 169 },
      { index: 4, x: 648, y: 78, width: 178, height: 169 },
      { index: 5, x: 66, y: 313, width: 178, height: 169 },
      { index: 6, x: 260, y: 313, width: 178, height: 169 },
      { index: 7, x: 454, y: 313, width: 178, height: 169 },
      { index: 8, x: 648, y: 313, width: 178, height: 169 },
      { index: 9, x: 66, y: 548, width: 178, height: 169 },
      { index: 10, x: 260, y: 548, width: 178, height: 169 },
      { index: 11, x: 454, y: 548, width: 178, height: 169 },
      { index: 12, x: 648, y: 548, width: 178, height: 169 },
      { index: 13, x: 66, y: 783, width: 178, height: 169 },
      { index: 14, x: 260, y: 783, width: 178, height: 169 },
      { index: 15, x: 454, y: 783, width: 178, height: 169 },
      { index: 16, x: 648, y: 783, width: 178, height: 169 }
    ];
  }

  async function loadSlotData() {
    try {
      const response = await fetch("/static/outside/vending_slots.json");
      if (!response.ok) throw new Error("slot data unavailable");
      return response.json();
    } catch (_error) {
      return {
        template_size: { width: 1055, height: 1024 },
        slots: fallbackSlots()
      };
    }
  }

  async function renderGrid() {
    const target = document.querySelector("[data-outside-grid]");
    if (!target) return;

    const slotData = await loadSlotData();
    const templateWidth = slotData.template_size && slotData.template_size.width || 1055;
    const templateHeight = slotData.template_size && slotData.template_size.height || 1024;
    const slots = Array.isArray(slotData.slots) ? slotData.slots : fallbackSlots();

    target.replaceChildren();
    slots.slice(0, 16).forEach((slot, index) => {
      const id = itemGrid()[index];
      const cell = document.createElement("div");
      cell.className = "outside-vending__cell";
      cell.dataset.slot = String(index + 1).padStart(2, "0");
      cell.style.left = slotPercent(slot, "x", templateWidth);
      cell.style.top = slotPercent(slot, "y", templateHeight);
      cell.style.width = slotPercent(slot, "width", templateWidth);
      cell.style.height = slotPercent(slot, "height", templateHeight);

      if (id) {
        cell.appendChild(createIcon(id, { withDisclosure: true }));
      } else {
        cell.appendChild(createIcon(null));
      }

      target.appendChild(cell);
    });
  }

  function hydrateSingleIcons() {
    document.querySelectorAll("[data-outside-icon]").forEach((target) => {
      const id = target.getAttribute("data-outside-icon");
      const icon = createIcon(id, {
        withDisclosure: target.hasAttribute("data-outside-disclosure")
      });
      target.replaceChildren(icon);
    });
  }

  async function render() {
    await renderGrid();
    hydrateSingleIcons();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", render, { once: true });
  } else {
    render();
  }
})();
