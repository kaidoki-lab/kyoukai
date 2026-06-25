(function () {
  const entranceItems = [
    {
      id: "observation",
      name: "observation",
      label: "観測する",
      href: "/observation",
      image: "/static/images/entrances/entrance-observation.png",
      expectedImage: "/static/images/entrances/entrance-observation.png",
      material: "mirror",
      status: "active",
    },
    {
      id: "observer",
      name: "observer",
      label: "会う",
      href: "/observer",
      image: "/static/images/entrances/entrance-observer.png",
      expectedImage: "/static/images/entrances/entrance-observer.png",
      material: "shrine",
      status: "active",
    },
    {
      id: "archive",
      name: "archive",
      label: "記録を見る",
      href: "/archive",
      image: "/static/images/entrances/entrance-archive.png",
      expectedImage: "/static/images/entrances/entrance-archive.png",
      material: "box",
      status: "active",
    },
    {
      id: "signal",
      name: "signal",
      label: "聞く",
      href: "/signal",
      image: "/static/images/entrances/entrance-signal.png",
      expectedImage: "/static/images/entrances/entrance-signal.png",
      material: "speaker",
      status: "active",
    },
    {
      id: "news",
      name: "news",
      label: "台風ニュース",
      href: "/typhoon-news/",
      image: "/static/images/entrances/news.png",
      expectedImage: "/static/images/entrances/news.png",
      material: "door",
      status: "active",
    },
    {
      id: "external-signal",
      name: "外部信号",
      label: "受ける",
      href: "/external-signal",
      image: "",
      expectedImage: "/static/images/entrances/entrance-external-signal.png",
      material: "window",
      status: "legacy",
    },
    {
      id: "daimyojin",
      name: "daimyojin",
      label: "占う",
      href: "/daimyojin",
      image: "/static/images/entrances/entrance-daimyojin.png",
      expectedImage: "/static/images/entrances/entrance-daimyojin.png",
      material: "shrine",
      status: "active",
    },
    {
      id: "hyougi",
      name: "hyougi",
      label: "読む",
      href: "/hyougi",
      image: "/static/images/entrances/entrance-hyougi.png",
      expectedImage: "/static/images/entrances/entrance-hyougi.png",
      material: "paper",
      status: "active",
    },
    {
      id: "gokuraku",
      name: "gokuraku",
      label: "入る",
      href: "/gokuraku",
      image: "/static/images/entrances/entrance-gokuraku.png",
      expectedImage: "/static/images/entrances/entrance-gokuraku.png",
      material: "shrine",
      status: "active",
    },
    {
      id: "exit",
      name: "exit",
      label: "出口を探す",
      href: "/exit",
      image: "/static/images/entrances/entrance-exit.png",
      expectedImage: "/static/images/entrances/entrance-exit.png",
      material: "door",
      status: "active",
    },
    {
      id: "null",
      name: "null",
      label: "崩す",
      href: "/null",
      image: "/static/images/entrances/entrance-null.png",
      expectedImage: "/static/images/entrances/entrance-null.png",
      material: "crack",
      status: "active",
    },
    {
      id: "outside",
      name: "OUTSIDE",
      label: "外を見る",
      href: "/outside",
      image: "",
      expectedImage: "/static/images/entrances/entrance-outside.png",
      material: "window",
      status: "legacy",
    },
    {
      id: "ma",
      name: "ma",
      label: "沈む",
      href: "/ma",
      image: "/static/images/entrances/entrance-ma.png",
      expectedImage: "/static/images/entrances/entrance-ma.png",
      material: "mirror",
      status: "active",
    },
    {
      id: "particles",
      name: "particles",
      label: "覗く",
      href: "/particles",
      image: "/static/images/entrances/entrance-particles.png?v=20260625c",
      expectedImage: "/static/images/entrances/entrance-particles.png",
      material: "mirror",
      status: "active",
    },
    {
      id: "ripple",
      name: "ripple",
      label: "触れる",
      href: "/ripple",
      image: "/static/images/entrances/entrance-ripple.png?v=20260625b",
      expectedImage: "/static/images/entrances/entrance-ripple.png",
      material: "crack",
      status: "active",
    },
  ];

  function createFallback(item) {
    const object = document.createElement("span");
    object.className = "entrance-object__fallback";
    object.dataset.material = item.material;

    const mark = document.createElement("span");
    mark.className = "entrance-object__mark";
    mark.textContent = item.name.slice(0, 2);

    object.append(mark);
    return object;
  }

  function createImage(item) {
    if (!item.image) return createFallback(item);

    const image = document.createElement("img");
    image.src = item.image;
    image.alt = "";
    image.loading = "lazy";
    image.decoding = "async";
    image.addEventListener("error", () => {
      image.replaceWith(createFallback(item));
    }, { once: true });
    return image;
  }

  function createEntrance(item) {
    const link = document.createElement("a");
    link.className = "entrance-object";
    link.href = item.href;
    link.dataset.entranceId = item.id;
    link.dataset.status = item.status;
    link.setAttribute("aria-label", `${item.name} - ${item.label}`);

    const visual = document.createElement("span");
    visual.className = "entrance-object__visual";
    visual.append(createImage(item));

    const text = document.createElement("span");
    text.className = "entrance-object__text";

    const name = document.createElement("span");
    name.className = "entrance-object__name";
    name.textContent = item.name;

    const label = document.createElement("span");
    label.className = "entrance-object__label";
    label.textContent = item.label;

    text.append(name, label);
    link.append(visual, text);
    return link;
  }

  function nearestEntrance(strip) {
    const items = Array.from(strip.querySelectorAll(".entrance-object"));
    const center = strip.scrollLeft + strip.clientWidth / 2;
    return items.reduce((nearest, item) => {
      const itemCenter = item.offsetLeft + item.offsetWidth / 2;
      const distance = Math.abs(itemCenter - center);
      if (!nearest || distance < nearest.distance) return { item, distance };
      return nearest;
    }, null)?.item;
  }

  function enableSnapBump() {
    const strip = document.querySelector("[data-entrance-strip]");
    if (!strip) return;

    let timer = 0;
    const bump = () => {
      const item = nearestEntrance(strip);
      if (!item) return;
      item.classList.remove("is-snap-bump");
      void item.offsetWidth;
      item.classList.add("is-snap-bump");
    };

    strip.addEventListener("scroll", () => {
      window.clearTimeout(timer);
      timer = window.setTimeout(bump, 120);
    }, { passive: true });
  }

  function renderEntrances() {
    const strip = document.querySelector("[data-entrance-strip]");
    if (!strip) return;

    strip.replaceChildren();
    entranceItems
      .filter((item) => item.status === "active")
      .forEach((item) => strip.append(createEntrance(item)));
  }

  window.KYOUKAI_ENTRANCE_ITEMS = entranceItems;
  renderEntrances();
  enableSnapBump();
})();
