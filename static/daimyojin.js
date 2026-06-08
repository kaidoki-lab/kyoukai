(function () {
  const room = document.querySelector(".daimyojin-room");
  const titleEl = document.querySelector("[data-oracle-title]");
  const messageEl = document.querySelector("[data-oracle-message]");
  const noteEl = document.querySelector("[data-oracle-note]");
  const statusEl = document.querySelector("[data-oracle-status]");
  const starsEl = document.querySelector("[data-oracle-stars]");
  const button = document.querySelector("[data-oracle-button]");
  const caret = document.querySelector("[data-oracle-caret]");

  if (!room || !titleEl || !messageEl || !noteEl || !statusEl || !starsEl || !button) return;

  const fortuneData = [
    ["段ボール運", 5, "開ける予定のない箱が、少しだけ気になります。", "中身はたぶん今じゃなくても大丈夫です。"],
    ["冷蔵庫の奥運", 3, "奥にある容器が、今日だけ存在感を出します。", "開けるなら換気を先に。"],
    ["半額シール運", 4, "近づいた瞬間に、誰かも同じ棚を見ています。", "迷ったら負けです。"],
    ["靴下運", 2, "片方だけ妙に強い主張をします。", "左右が違っても、足は進みます。"],
    ["レシート運", 3, "不要な紙ほど財布の奥で長生きします。", "捨てる前に一度だけ見返してください。"],
    ["エレベーター運", 4, "押した階に行くだけなのに、少し儀式めきます。", "開く扉を信じすぎないでください。"],
    ["Wi-Fi運", 2, "棒は立っていますが、心は離席しています。", "再接続は祈りの一種です。"],
    ["充電運", 5, "差したつもりのケーブルが、今日は本当に差さっています。", "珍しい祝福です。"],
    ["自販機運", 3, "押したボタンの隣が少し光って見えます。", "温かい方を選ぶと記録が揺れます。"],
    ["ゴミ出し運", 4, "袋を結ぶ音がやけに神聖です。", "収集日を疑った時点で半分勝ちです。"],
    ["カレー運", 5, "二日目の気配が、鍋の底から上がっています。", "温め直しは小さな復活祭です。"],
    ["ティッシュ運", 2, "最後の一枚が思ったより早く来ます。", "箱の裏に次の箱はありません。"],
    ["コンビニ入店運", 3, "自動ドアが少しだけ早くあなたを認識します。", "入店音に返事をしないでください。"],
    ["リモコン運", 1, "近くにあるのに見つかりません。", "座った瞬間、身体の下から出ます。"],
    ["玄関の鍵運", 4, "閉めた記憶と閉めた事実が別々に存在します。", "一度だけ戻れば十分です。"],
    ["賞味期限運", 3, "数字は読めますが、判断は少し濁ります。", "匂いに聞くのは最終手段です。"],
    ["洗濯物運", 5, "干すタイミングだけが妙に合います。", "靴下は最後に一つ増えます。"],
    ["寝落ち運", 2, "続きを見るつもりが、別の夢を再生します。", "再生履歴はあなたを覚えています。"],
    ["通知運", 4, "どうでもいい通知だけ、妙に堂々と届きます。", "大事な通知は少し遅れて来ます。"],
    ["電子レンジ運", 3, "残り3秒で止めるかどうかが問われます。", "神託はまだ温まりきっていません。"],
    ["観測運", 5, "見ているつもりが、見られている側に寄ります。", "観測点は一歩だけ後ろです。"],
    ["外部信号運", 4, "関係ない音が、妙に合図っぽく聞こえます。", "受信しても返信しないでください。"],
    ["未確認接続運", 3, "繋がっていないものが、少しだけ繋がるふりをします。", "確認しすぎると接続名が変わります。"],
    ["崩壊回避運", 4, "落ちそうなものが、今日はぎりぎり留まります。", "支えているのは仕様ではなく気分です。"],
    ["境界運", 5, "こちら側とあちら側の線が、薄く点滅します。", "踏まなくても靴底に残ります。"],
    ["祭壇運", 3, "賽銭箱が何も言わずにこちらを見ています。", "入れても入れなくても記録されます。"],
    ["記録室運", 4, "しまったものの場所だけが妙に鮮明です。", "取り出すと少し違う名前になっています。"],
    ["接続待ち運", 2, "読み込み中の輪が、輪であることに満足しています。", "待つほど意味は薄くなります。"],
    ["ノイズ運", 5, "聞き取れない部分だけが今日は正確です。", "静かにすると余計に混ざります。"],
    ["404運", 1, "探しているページはありませんが、気配はあります。", "戻るボタンが小さく光ります。"],
    ["湯気運", 3, "熱いものが一瞬だけ未来を隠します。", "冷めたらただの飲み物です。"],
    ["傘運", 4, "持っていると降らず、置いてくると空が考えます。", "折りたたみは小さな結界です。"],
    ["机の角運", 2, "近づくほど角が角らしくなります。", "避けた記憶だけを持ち帰ってください。"],
  ].map(([category, stars, message, note]) => ({ category, stars, message, note }));

  const statuses = ["受信中...", "神託生成中...", "演算中...", "文字化け補正中...", "おみくじ機再起動中..."];
  let lastIndex = -1;
  let typingTimer = 0;
  let audioContext = null;
  let lastTickAt = 0;

  function getAudioContext() {
    const AudioCtor = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtor) return null;
    if (!audioContext) audioContext = new AudioCtor();
    if (audioContext.state === "suspended") audioContext.resume().catch(() => {});
    return audioContext;
  }

  function playTypeTick(index) {
    const now = performance.now();
    if (index % 2 !== 0 || now - lastTickAt < 42) return;
    const context = getAudioContext();
    if (!context || context.state !== "running") return;

    lastTickAt = now;
    const osc = context.createOscillator();
    const gain = context.createGain();
    osc.type = "square";
    osc.frequency.setValueAtTime(760 + Math.random() * 120, context.currentTime);
    gain.gain.setValueAtTime(0.0001, context.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.035, context.currentTime + 0.006);
    gain.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + 0.045);
    osc.connect(gain);
    gain.connect(context.destination);
    osc.start();
    osc.stop(context.currentTime + 0.052);
  }

  function pickFortune() {
    if (fortuneData.length < 2) return fortuneData[0];
    let index = Math.floor(Math.random() * fortuneData.length);
    if (index === lastIndex) index = (index + 1 + Math.floor(Math.random() * (fortuneData.length - 1))) % fortuneData.length;
    lastIndex = index;
    return fortuneData[index];
  }

  function setStars(count) {
    const stars = Array.from(starsEl.querySelectorAll("span"));
    stars.forEach((star) => star.classList.remove("is-lit"));
    stars.forEach((star, index) => {
      window.setTimeout(() => {
        star.classList.toggle("is-lit", index < count);
      }, 90 * index + 120);
    });
  }

  function typeText(text, onComplete) {
    window.clearInterval(typingTimer);
    messageEl.textContent = "";
    caret?.classList.remove("is-visible");

    let index = 0;
    typingTimer = window.setInterval(() => {
      messageEl.textContent = text.slice(0, index);
      if (text[index - 1] && !/\s/.test(text[index - 1])) playTypeTick(index);
      index += 1;
      if (index > text.length) {
        window.clearInterval(typingTimer);
        caret?.classList.add("is-visible");
        onComplete?.();
      }
    }, window.matchMedia("(max-width: 768px), (orientation: portrait)").matches ? 64 : 54);
  }

  function runOracle() {
    const fortune = pickFortune();
    const isMobile = window.matchMedia("(max-width: 768px), (orientation: portrait)").matches;
    const status = statuses[Math.floor(Math.random() * statuses.length)];

    button.disabled = true;
    room.classList.add("is-receiving");
    statusEl.textContent = status;
    titleEl.textContent = `今日の${fortune.category}`;
    noteEl.textContent = "";
    setStars(0);

    window.setTimeout(() => {
      room.classList.remove("is-receiving");
      setStars(fortune.stars);
      noteEl.textContent = `> 補足の一言\n${fortune.note}`;
      statusEl.textContent = "神託をお伝えします...";

      const starLine = "★★★★★".slice(0, fortune.stars) + "☆☆☆☆☆".slice(0, 5 - fortune.stars);
      const text = isMobile
        ? `神託をお伝えします...\n\n今日の${fortune.category}\n${starLine}\n\n${fortune.message}\n\n${fortune.note}`
        : fortune.message;

      typeText(text, () => {
        window.setTimeout(() => {
          button.disabled = false;
        }, 1000);
      });
    }, 680 + Math.floor(Math.random() * 360));
  }

  button.addEventListener("pointerdown", getAudioContext);
  button.addEventListener("click", runOracle);
  window.addEventListener("load", () => window.setTimeout(runOracle, 260), { once: true });
})();
