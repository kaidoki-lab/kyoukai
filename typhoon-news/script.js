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
  },
  {
    name: "前向きに善処します",
    number: "996",
    pressure: 905,
    wind: 58,
    gust: 86,
    direction: "北東",
    speed: 18,
    verticalCopy: "善処だけが接近中。",
    mainCaption: "対応は未定",
    ticker: "台風「前向きに善処します」は、前向きな姿勢を保ったまま各地に接近しています。"
  },
  {
    name: "担当者不在",
    number: "995",
    pressure: 900,
    wind: 62,
    gust: 90,
    direction: "西北西",
    speed: 12,
    verticalCopy: "窓口が消えた暴風域。",
    mainCaption: "連絡網に乱れ",
    ticker: "台風「担当者不在」の影響で、各地の問い合わせ窓口に混乱が広がっています。"
  },
  {
    name: "一旦持ち帰ります",
    number: "994",
    pressure: 915,
    wind: 50,
    gust: 78,
    direction: "東",
    speed: 30,
    verticalCopy: "持ち帰ったまま北上。",
    mainCaption: "判断を持ち帰り",
    ticker: "台風「一旦持ち帰ります」は結論を伴わないまま東寄りに進んでいます。"
  },
  {
    name: "確認中です",
    number: "993",
    pressure: 895,
    wind: 64,
    gust: 92,
    direction: "北北東",
    speed: 22,
    verticalCopy: "確認だけが長引く。",
    mainCaption: "各地で確認中",
    ticker: "台風「確認中です」は現在も確認中です。気象庁は続報を待つよう呼びかけています。"
  },
  {
    name: "折り返します",
    number: "992",
    pressure: 920,
    wind: 48,
    gust: 72,
    direction: "南西",
    speed: 10,
    verticalCopy: "折り返し未確認。",
    mainCaption: "折り返しを待つ",
    ticker: "台風「折り返します」は折り返す見込みですが、現時点で折り返しは確認されていません。"
  },
  {
    name: "なるはやで",
    number: "991",
    pressure: 885,
    wind: 68,
    gust: 98,
    direction: "北西",
    speed: 35,
    verticalCopy: "速度だけが本気。",
    mainCaption: "なるはやで接近",
    ticker: "台風「なるはやで」は非常に速い速度で接近しています。各地で早めの判断が求められています。"
  },
  {
    name: "今向かってます",
    number: "990",
    pressure: 930,
    wind: 45,
    gust: 68,
    direction: "北",
    speed: 40,
    verticalCopy: "すでに遅れて接近。",
    mainCaption: "到着時刻は未定",
    ticker: "台風「今向かってます」は現在も向かっているとみられますが、到着時刻は不明です。"
  },
  {
    name: "既読だけつけます",
    number: "989",
    pressure: 908,
    wind: 57,
    gust: 84,
    direction: "西",
    speed: 16,
    verticalCopy: "返答なき暴風。",
    mainCaption: "既読被害が拡大",
    ticker: "台風「既読だけつけます」の接近により、各地で返信待ちの状態が続いています。"
  },
  {
    name: "また後で",
    number: "988",
    pressure: 918,
    wind: 52,
    gust: 76,
    direction: "東北東",
    speed: 19,
    verticalCopy: "後回しの雨雲。",
    mainCaption: "後で対応へ",
    ticker: "台風「また後で」は勢力を維持したまま後回しにされています。今後の情報に注意してください。"
  }
];

const captionPool = [
  "最大級の警戒を呼びかけ",
  "全国で様子見",
  "名前変更を検討",
  "もう遅い",
  "気象庁、沈黙",
  "対応は未定",
  "連絡網に乱れ",
  "折り返しを待つ"
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
  const breakChars = ["連", "に", "し", "持", "不", "中", "つ"];
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
