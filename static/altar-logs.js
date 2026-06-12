(function () {
  'use strict';

  const SEP = '— — — — — — —';

  function line(text, cls) {
    return [text, cls || null];
  }

  function buildLines(g, c) {
    const evo = c.evo || {};
    const organs = Array.isArray(c.organs) ? c.organs : [];
    const updatedAt = g.updated_at
      ? new Date(g.updated_at).toISOString().slice(11, 19)
      : '--:--:--';
    const isUnstable = Number(g.instability) > 20;
    const hasAggro   = Number(evo.AGGRO) > 20;

    const left = [
      line('OBSERVATION_LOG', 'alog--head'),
      line(SEP, 'alog--sep'),
      line('GENOME:PHASE_' + g.phase, 'alog--time'),
      line('変異累積 ' + g.mutation_count + '回', null),
      line('安定度 ' + g.stability + '%', null),
      line('不安定度 ' + g.instability, isUnstable ? 'alog--alert' : null),
      line(SEP, 'alog--sep'),
      line(c.species_id || 'U-??????', 'alog--time'),
      line(c.name || '未確認生命体', null),
      line('rarity:' + (c.rarity || '?'), null),
      line('danger:' + (c.danger || 0), null),
      line(SEP, 'alog--sep'),
      line('特性 ' + (g.dominant_trait || 'none'), null),
      line('変異型 ' + (g.last_mutation_type || 'none'),
           g.last_mutation_type && g.last_mutation_type !== 'none' ? 'alog--alert' : null),
      line('mood:' + (g.mood || '?'), null),
      line(SEP, 'alog--sep'),
      ...organs.map(o => line('organ:' + o, null)),
      line('core:' + (c.core || '?'), null),
    ];

    const right = [
      line('SYS_STATUS', 'alog--head'),
      line(SEP, 'alog--sep'),
      line('CALM ' + (evo.CALM || 0), null),
      line('AGGRO ' + (evo.AGGRO || 0), hasAggro ? 'alog--alert' : null),
      line('CURIOSITY ' + (evo.CURIOSITY || 0), null),
      line('DISTORTION ' + (evo.DISTORTION || 0), null),
      line(SEP, 'alog--sep'),
      line('observer ' + g.observer_count, null),
      line('noise ' + g.noise_level, null),
      line('[' + updatedAt + ']', 'alog--time'),
      line(SEP, 'alog--sep'),
      line('SIG:RX-09 待機中', null),
      line('境界域 未確定', null),
      line('感染 進行中', null),
      line('接続 不安定', null),
      line(SEP, 'alog--sep'),
      line('KY-SYS_OK', null),
    ];

    return { left, right };
  }

  function appendCopy(tapeEl, lines) {
    for (var i = 0; i < lines.length; i++) {
      var text = lines[i][0], cls = lines[i][1];
      var el = document.createElement('span');
      el.className = 'alog' + (cls ? ' ' + cls : '');
      el.textContent = text;
      tapeEl.appendChild(el);
    }
  }

  function fillTape(tapeEl, lines, panelH) {
    tapeEl.innerHTML = '';

    // Append copies until tape.scrollHeight >= 2 * panelH (measured from DOM)
    var safety = 0;
    do {
      appendCopy(tapeEl, lines);
      safety++;
    } while (tapeEl.scrollHeight < panelH * 2 && safety < 30);

    // Set --scroll-dist so animation scrolls exactly one "copy height"
    var half = Math.round(tapeEl.scrollHeight / 2);
    tapeEl.style.setProperty('--scroll-dist', '-' + half + 'px');
  }

  function init() {
    var leftEl  = document.getElementById('altarLogL');
    var rightEl = document.getElementById('altarLogR');
    if (!leftEl && !rightEl) return;

    // Only run on PC breakpoint (panels are fixed at >=1100px)
    if (window.innerWidth < 1100) return;

    // panels are position:fixed top:0 bottom:0, so height = viewport height
    var panelH = window.innerHeight || 1080;

    Promise.all([
      fetch('/api/genome').then(r => r.json()),
      fetch('/api/creature').then(r => r.json()),
    ]).then(function ([g, c]) {
      const { left, right } = buildLines(g, c);
      if (leftEl)  fillTape(leftEl,  left,  panelH);
      if (rightEl) fillTape(rightEl, right, panelH);
    }).catch(function () {
      // APIが落ちていても何もしない（パネルは空のまま）
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
