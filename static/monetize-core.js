(function () {
  function config() {
    return window.KYOUKAI_MONETIZE_LINKS || {};
  }

  function appendText(parent, tagName, className, text) {
    const element = document.createElement(tagName);
    element.className = className;
    element.textContent = text;
    parent.appendChild(element);
    return element;
  }

  function createLink(item) {
    const link = document.createElement("a");
    link.className = "ky-outside-item";
    link.href = item.href || "#";

    if (item.target) {
      link.target = item.target;
    }

    if (item.rel) {
      link.rel = item.rel;
    }

    appendText(link, "span", "ky-outside-item__label", item.label || "OUTSIDE");
    appendText(link, "span", "ky-outside-item__body", item.body || "");

    if (item.disclosure) {
      appendText(link, "small", "ky-outside-item__disclosure", item.disclosure);
    }

    return link;
  }

  function renderOutsidePage() {
    const target = document.querySelector("[data-monetize-list]");
    if (!target) return;

    const data = config();
    const sections = Array.isArray(data.sections) ? data.sections : [];
    target.replaceChildren();

    sections.forEach((section) => {
      const shell = document.createElement("section");
      shell.className = "ky-outside-section";
      shell.dataset.section = section.id || "";

      const head = document.createElement("header");
      appendText(head, "span", "ky-outside-section__id", section.id || "node");
      appendText(head, "h2", "ky-outside-section__title", section.title || "OUTSIDE");
      appendText(head, "p", "ky-outside-section__note", section.note || "");
      shell.appendChild(head);

      const list = document.createElement("div");
      list.className = "ky-outside-section__list";
      (Array.isArray(section.items) ? section.items : []).forEach((item) => {
        if (item && item.href) {
          list.appendChild(createLink(item));
        }
      });
      shell.appendChild(list);
      target.appendChild(shell);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", renderOutsidePage, { once: true });
  } else {
    renderOutsidePage();
  }
})();
