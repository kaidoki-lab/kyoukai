const typhoonPresets = [
  {
    name: "後ほど連絡します",
    number: "999",
    pressure: 890,
    wind: 65,
    gust: 95,
    direction: "北北西",
    speed: 20,
    verticalCopy: "史上最悪クラスのネーミング。",
    mainCaption: "最大級の警戒を呼びかけ",
    ticker: "台風「後ほど連絡します」の影響で、全国的に荒天となる見込みです。気象庁は不要不急の返信を控えるよう呼びかけています。"
  },
  {
    name: "検討します",
    number: "998",
    pressure: 910,
    wind: 55,
    gust: 80,
    direction: "北西",
    speed: 15,
    verticalCopy: "結論の出ない暴風域。",
    mainCaption: "全国で様子見",
    ticker: "台風「検討します」は勢力を維持したまま北上しています。関係機関は判断の先送りに警戒しています。"
  },
  {
    name: "お母さんに聞いて",
    number: "997",
    pressure: 880,
    wind: 70,
    gust: 100,
    direction: "北",
    speed: 25,
    verticalCopy: "判断不能の大型台風。",
    mainCaption: "名前だけで避難開始",
    ticker: "気象庁は台風「お母さんに聞いて」への厳重な警戒を呼びかけています。各地で確認待ちが続いています。"
  }
];

const captionPool = [
  "最大級の警戒を呼びかけ",
  "全国で様子見",
  "名前変更を検討",
  "もう遅い",
  "気象庁、沈黙"
];

const countStarts = {
  pressure: 940,
  wind: 30,
  gust: 50
};

const params = new URLSearchParams(window.location.search);
const requestedName = params.get("name");
const selectedPreset =
  typhoonPresets.find((preset) => preset.name === requestedName) ||
  typhoonPresets[Math.floor(Math.random() * typhoonPresets.length)];

function setText(selector, value) {
  document.querySelectorAll(selector).forEach((node) => {
    node.textContent = value;
  });
}

function splitNameForEye(name) {
  if (name.length <= 5) {
    return [name, ""];
  }

  const midpoint = Math.ceil(name.length / 2);
  const breakChars = ["連", "に", "し"];
  const breakIndex = breakChars
    .map((char) => name.indexOf(char, 2))
    .find((index) => index > 0);

  const index = breakIndex || midpoint;
  return [name.slice(0, index), name.slice(index)];
}

function animateCount(element, from, to, duration = 1200) {
  const start = performance.now();
  const difference = to - from;

  function step(now) {
    const elapsed = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - elapsed, 3);
    element.textContent = Math.round(from + difference * eased).toLocaleString("ja-JP");

    if (elapsed < 1) {
      requestAnimationFrame(step);
    }
  }

  requestAnimationFrame(step);
}

function applyPreset(preset) {
  setText('[data-field="name"]', preset.name);
  setText('[data-field="number"]', preset.number);
  setText('[data-field="direction"]', preset.direction);
  setText('[data-field="speed"]', preset.speed);
  setText('[data-field="verticalCopy"]', preset.verticalCopy);
  setText("[data-main-caption]", preset.mainCaption);
  setText("[data-ticker]", preset.ticker);
  setText("[data-ticker-clone]", `${preset.ticker}　${preset.ticker}`);

  const [firstLine, secondLine] = splitNameForEye(preset.name);
  setText('[data-eye-line="first"]', firstLine);
  setText('[data-eye-line="second"]', secondLine);

  ["pressure", "wind", "gust"].forEach((key) => {
    const element = document.querySelector(`[data-count="${key}"]`);
    if (element) {
      animateCount(element, countStarts[key], preset[key]);
    }
  });
}

function rotateCaptions(preset) {
  const caption = document.querySelector("[data-main-caption]");
  const captions = Array.from(new Set([preset.mainCaption, ...captionPool]));
  let index = 0;

  setInterval(() => {
    index = (index + 1) % captions.length;
    caption.textContent = captions[index];
  }, 3600);
}

function triggerLightning() {
  const layer = document.querySelector(".lightning-layer");
  if (!layer) {
    return;
  }

  layer.classList.remove("is-flashing");
  void layer.offsetWidth;
  layer.classList.add("is-flashing");

  const nextDelay = 3000 + Math.random() * 5000;
  window.setTimeout(triggerLightning, nextDelay);
}

function randomizeTickerDuration() {
  const ticker = document.querySelector(".ticker-track");
  if (!ticker) {
    return;
  }

  const lengthFactor = Math.max(selectedPreset.ticker.length / 48, 1);
  ticker.style.animationDuration = `${24 * lengthFactor}s`;
}

applyPreset(selectedPreset);
rotateCaptions(selectedPreset);
randomizeTickerDuration();
window.setTimeout(triggerLightning, 1600 + Math.random() * 2200);
