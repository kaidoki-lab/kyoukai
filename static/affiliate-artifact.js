(function () {
  const DISCLOSURE_TEXT = "PR / Amazon\u30a2\u30bd\u30b7\u30a8\u30a4\u30c8\u30ea\u30f3\u30af\u3092\u542b\u307f\u307e\u3059";
  const ASSOCIATE_TEXT = "Amazon\u306e\u30a2\u30bd\u30b7\u30a8\u30a4\u30c8\u3068\u3057\u3066\u3001KYOUKAI\u306f\u9069\u683c\u8ca9\u58f2\u306b\u3088\u308a\u53ce\u5165\u3092\u5f97\u3066\u3044\u307e\u3059\u3002";
  const DEFAULT_LABEL = "\u6f02\u7740\u7269";
  const DEFAULT_NOTE = "\u5916\u90e8\u63a5\u7d9a";
  const PORT_TEXT = "UNKNOWN PORT";
  const AMAZON_ARIA_LABEL = "Amazon\u30a2\u30bd\u30b7\u30a8\u30a4\u30c8\u30ea\u30f3\u30af\u3092\u958b\u304f";

  function getAmazonConfig() {
    const config = window.KYOUKAI_AFFILIATE_LINKS || {};
    return config.amazon || {};
  }

  function hasUsableUrl(value) {
    if (typeof value !== "string" || value.trim() === "") {
      return false;
    }

    try {
      const url = new URL(value.trim(), window.location.href);
      return url.protocol === "https:" || url.protocol === "http:";
    } catch (_) {
      return false;
    }
  }

  function appendTextElement(parent, tagName, className, text) {
    const element = document.createElement(tagName);
    element.className = className;
    element.textContent = text;
    parent.appendChild(element);
  }

  function renderAmazonArtifact(mount, amazon) {
    const slot = mount.dataset.affiliateSlot || "";
    const url = typeof amazon[slot] === "string" ? amazon[slot].trim() : "";

    mount.replaceChildren();
    mount.hidden = true;

    if (amazon.enabled !== true || !hasUsableUrl(url)) {
      return false;
    }

    const label = mount.dataset.affiliateLabel || DEFAULT_LABEL;
    const note = mount.dataset.affiliateNote || DEFAULT_NOTE;
    const variant = mount.dataset.affiliateVariant || slot || "artifact";
    const link = document.createElement("a");
    const disclosure = document.createElement("span");

    link.className = "external-artifact-link external-artifact-link--" + variant;
    link.href = url;
    link.target = "_blank";
    link.rel = "sponsored noopener noreferrer";
    link.setAttribute("aria-label", AMAZON_ARIA_LABEL);

    appendTextElement(link, "span", "external-artifact-light", "");
    appendTextElement(link, "span", "external-artifact-port", PORT_TEXT);
    appendTextElement(link, "span", "external-artifact-core", note);
    appendTextElement(link, "span", "external-artifact-sub", label);

    mount.appendChild(link);
    disclosure.className = "external-artifact-pr";
    disclosure.textContent = DISCLOSURE_TEXT;
    mount.appendChild(disclosure);
    mount.hidden = false;
    return true;
  }

  function revealSiteDisclosure(renderedCount) {
    document.querySelectorAll("[data-affiliate-disclosure]").forEach((element) => {
      if (renderedCount > 0) {
        element.textContent = ASSOCIATE_TEXT;
        element.hidden = false;
      } else {
        element.hidden = true;
      }
    });
  }

  function init() {
    const amazon = getAmazonConfig();
    let renderedCount = 0;

    document.querySelectorAll('[data-affiliate-artifact="amazon"]').forEach((mount) => {
      if (renderAmazonArtifact(mount, amazon)) {
        renderedCount += 1;
      }
    });

    revealSiteDisclosure(renderedCount);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
