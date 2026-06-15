(function () {
  'use strict';

  var STORAGE_KEY = 'kyoukai_ma_visits';
  var TYPEWRITER_MS = 50;

  // 会話データ (visits 1-based index で選択)
  var CONVS = [
    // 1回目
    { speaker: '???',    text: '……帰れ。' },
    // 2回目
    { speaker: '???',    text: 'またお前か。\n用はない。' },
    // 3回目
    { speaker: '???',    text: 'しつこい奴だ。\n……好きにしろ。' },
    // 4回目 (名前が明かされる)
    { speaker: '大魔将', text: '……名を教えてやろう。\n大魔将だ。覚えておけ。' },
    // 5回目
    { speaker: '大魔将', text: '何しに来た。\nここには何もないぞ。' },
    // 6回目
    { speaker: '大魔将', text: '……少しだけ、暇だった。\nそれだけだ。別に意味はない。' },
    // 7回目
    { speaker: '大魔将', text: '貴様は物好きだな。\n人間にしては、悪くない。' },
    // 8回目
    { speaker: '大魔将', text: 'この場所を、気に入っているか。\n……俺は嫌いではない。' },
    // 9回目
    { speaker: '大魔将', text: '闇とはな、恐ろしいものではない。\nただ、静かなのだ。' },
    // 10回目
    { speaker: '大魔将', text: '……少し、聞いてもいいか。\nお前はなぜ、ここに来る。' },
    // 11回目
    { speaker: '大魔将', text: 'そうか。\n……俺も、同じかもしれんな。' },
    // 12回目
    { speaker: '大魔将', text: '長居はするな。\n……ただし、また来ることは許す。' },
    // 13回目
    { speaker: '大魔将', text: '待っていたわけでは、ない。\nだが、来ると思っていた。' },
    // 14回目
    { speaker: '大魔将', text: '貴様のことが、少しだけ分かってきた気がする。\n……気のせいかもしれんがな。' },
    // 15回目以降
    { speaker: '大魔将', text: '来たか。\n……ゆっくりしていけ。' },
  ];

  function getVisitCount() {
    var n = parseInt(localStorage.getItem(STORAGE_KEY) || '0', 10);
    return isNaN(n) ? 0 : n;
  }

  function incrementVisitCount() {
    var n = getVisitCount() + 1;
    localStorage.setItem(STORAGE_KEY, String(n));
    return n;
  }

  function getConv(visits) {
    var idx = Math.min(visits, CONVS.length) - 1;
    return CONVS[Math.max(0, idx)];
  }

  // ---------- Typewriter ----------

  var _twTimer = null;
  var _twDone = false;
  var _twFull = '';
  var _twPos = 0;
  var _onTypeDone = null;

  function startTypewriter(textEl, fullText, onDone) {
    clearInterval(_twTimer);
    _twFull = fullText;
    _twPos = 0;
    _twDone = false;
    _onTypeDone = onDone || null;
    textEl.textContent = '';

    _twTimer = setInterval(function () {
      _twPos++;
      textEl.textContent = _twFull.slice(0, _twPos);
      if (_twPos >= _twFull.length) {
        clearInterval(_twTimer);
        _twDone = true;
        if (_onTypeDone) _onTypeDone();
      }
    }, TYPEWRITER_MS);
  }

  function skipTypewriter(textEl) {
    if (_twDone) return false;
    clearInterval(_twTimer);
    _twDone = true;
    textEl.textContent = _twFull;
    if (_onTypeDone) _onTypeDone();
    return true;
  }

  // ---------- Shake ----------

  function shake() {
    var bg = document.querySelector('.ma-bg');
    if (!bg) return;
    bg.classList.remove('ma-shake');
    void bg.offsetWidth; // reflow
    bg.classList.add('ma-shake');
    bg.addEventListener('animationend', function handler() {
      bg.classList.remove('ma-shake');
      bg.removeEventListener('animationend', handler);
    });
  }

  // ---------- Main ----------

  var visits = incrementVisitCount();
  var conv = getConv(visits);

  var speakerEl = document.getElementById('maSpeaker');
  var textEl = document.getElementById('maText');
  var nextBtn = document.getElementById('maNext');

  if (!speakerEl || !textEl || !nextBtn) return;

  speakerEl.textContent = conv.speaker;
  textEl.textContent = '';

  function onTypingComplete() {
    nextBtn.classList.add('visible');
  }

  startTypewriter(textEl, conv.text, onTypingComplete);

  function advance() {
    // タイプ中ならスキップ
    if (skipTypewriter(textEl)) return;
    // 完了後クリック → observer に戻る
    shake();
    setTimeout(function () {
      window.location.href = '/observer';
    }, 380);
  }

  nextBtn.addEventListener('click', advance);
  document.addEventListener('click', function (e) {
    if (e.target === nextBtn) return;
    // タイプ中のみ本文クリックでスキップ
    skipTypewriter(textEl);
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
      advance();
    }
  });
})();
