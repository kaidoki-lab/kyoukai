#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 観測域(observation) 専用実装

デザイン指針(ROADMAP):
  waiting: 観測ログ端末。画面全体が流れるログテーブル+観測カウンタ
  brb: ログが停止し「記録は継続」の静止カーソルが明滅、時折1行だけ追記される
  lower_third: 端末プロンプト風 `> 名前 _`(カーソル明滅)

一次データ:
  static/space.css の配色(--sp-mono, --sp-muted, --sp-cyan等の端末的トーン)
  data/kyoukai_world.md の観測ログ文体(「感情を排した観測記録」「観測対象は訪問者である可能性」)
"""
import json
import sys as _sys
from pathlib import Path as _Path

_BOOTH_DIR = _Path(__file__).resolve().parent.parent
if str(_BOOTH_DIR) not in _sys.path:
    _sys.path.insert(0, str(_BOOTH_DIR))
import asset_extract  # noqa: E402

SPEC_ID = "observation"
NAME = "観測域"
COLOR = "#44ff88"
RGB = "68,255,136"
BG = "#000800"

# static/space.css から実際に読み取った端末的トーンの配色(コメントで根拠を残す)
# --sp-mono: Consolas, "Courier New", monospace / --sp-muted: #738066 / --sp-cyan: #b7c2a0
_CSS_SRC = asset_extract.read_source("static/space.css")
_MONO_FONT = 'Consolas, "Courier New", monospace' if '--sp-mono' in _CSS_SRC else "'Courier New', monospace"

# data/kyoukai_world.md の観測ログ文体を踏襲した断片(感情を排した観測記録)
LOG_LINES = [
    "生命体を確認。反応あり。",
    "感情は排除済み。記録のみ残る。",
    "対象を識別中 ── 一致率不明。",
    "観測は継続する。中断予定なし。",
    "ログバッファ更新。異常なし。",
    "対象は訪問者である可能性がある。",
    "応答を検出。解析中。",
    "座標を再取得。ずれあり。",
    "観測を開始した。終了予定は未定義。",
    "何かを感じさせるが、それは記録に残らない。",
]

BRB_LINES = [
    "記録は継続されています",
    "対象を再捕捉中",
    "ログを保存しています",
    "観測は止まっていません",
]


def waiting_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    lines_js = json.dumps(LOG_LINES, ensure_ascii=False)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 待機画面</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:{_MONO_FONT};color:{color};}}

/* .obs- プレフィックス付き固有クラス群 */
.obs-terminal{{position:absolute;inset:0;width:1920px;height:1080px;z-index:10;padding:64px 90px;display:flex;flex-direction:column;}}
.obs-terminal-head{{display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid rgba({rgb},0.28);padding-bottom:18px;margin-bottom:10px;}}
.obs-terminal-title{{font-size:15px;letter-spacing:6px;color:rgba({rgb},0.7);text-transform:uppercase;}}
.obs-counter{{font-size:13px;letter-spacing:3px;color:rgba({rgb},0.4);}}
.obs-log-table{{flex:1;overflow:hidden;position:relative;margin-top:8px;}}
.obs-log-row{{position:absolute;left:0;width:100%;display:flex;gap:28px;font-size:15px;letter-spacing:1px;padding:5px 0;white-space:nowrap;}}
.obs-log-row .obs-log-idx{{width:70px;color:rgba({rgb},0.35);flex-shrink:0;}}
.obs-log-row .obs-log-ts{{width:190px;color:rgba({rgb},0.32);flex-shrink:0;}}
.obs-log-row .obs-log-text{{color:rgba({rgb},0.82);}}
.obs-footer{{display:flex;justify-content:space-between;align-items:center;border-top:1px solid rgba({rgb},0.2);padding-top:16px;margin-top:10px;font-size:11px;letter-spacing:4px;color:rgba({rgb},0.35);}}
.obs-footer .obs-cursor{{display:inline-block;width:10px;height:16px;background:{color};margin-left:6px;vertical-align:-3px;animation:obsBlink 1.1s step-end infinite;}}
@keyframes obsBlink{{0%,100%{{opacity:1}}50%{{opacity:0}}}}
.obs-scan{{position:absolute;inset:0;pointer-events:none;z-index:20;background:repeating-linear-gradient(to bottom,transparent 0px,transparent 3px,rgba(0,0,0,0.14) 3px,rgba(0,0,0,0.14) 4px);}}
canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:1;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="obs-terminal">
  <div class="obs-terminal-head">
    <div class="obs-terminal-title">KYOUKAI OBSERVATION LOG // {NAME}</div>
    <div class="obs-counter" id="obs-count">OBS_ID 000000</div>
  </div>
  <div class="obs-log-table" id="obs-table"></div>
  <div class="obs-footer">
    <div>観測継続中<span class="obs-cursor"></span></div>
    <div id="obs-clock"></div>
  </div>
</div>
<div class="obs-scan"></div>
<script>
const canvas=document.getElementById('c');
const ctx=canvas.getContext('2d');
canvas.width=1920;canvas.height=1080;
function drawGrid(){{
  ctx.clearRect(0,0,1920,1080);
  ctx.strokeStyle='rgba({rgb},0.05)';
  ctx.lineWidth=1;
  for(let x=0;x<1920;x+=64){{ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,1080);ctx.stroke();}}
  for(let y=0;y<1080;y+=64){{ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(1920,y);ctx.stroke();}}
}}
drawGrid();

const LINES={lines_js};
const table=document.getElementById('obs-table');
const ROWS=13;
const rowH=32;
let entries=[];
let idx=1;
function makeRow(text){{
  const row=document.createElement('div');
  row.className='obs-log-row';
  const ts=new Date().toISOString().replace('T',' ').slice(0,19);
  row.innerHTML=`<span class="obs-log-idx">#${{String(idx).padStart(5,'0')}}</span><span class="obs-log-ts">${{ts}}</span><span class="obs-log-text">${{text}}</span>`;
  idx++;
  return row;
}}
for(let i=0;i<ROWS;i++){{
  const el=makeRow(LINES[i%LINES.length]);
  el.style.top=(i*rowH)+'px';
  table.appendChild(el);
  entries.push(el);
}}
function scrollLog(){{
  entries.forEach(el=>{{
    const t=parseFloat(el.style.top)-rowH;
    el.style.top=t+'px';
  }});
  if(parseFloat(entries[0].style.top)<=-rowH){{
    const old=entries.shift();
    table.removeChild(old);
    const newEl=makeRow(LINES[Math.floor(Math.random()*LINES.length)]);
    newEl.style.top=(parseFloat(entries[entries.length-1].style.top)+rowH)+'px';
    table.appendChild(newEl);
    entries.push(newEl);
  }}
}}
setInterval(scrollLog,1400);

const countEl=document.getElementById('obs-count');
let cv=Math.floor(Math.random()*900000);
setInterval(()=>{{cv+=Math.floor(Math.random()*7);countEl.textContent='OBS_ID '+String(cv).padStart(6,'0');}},900);

const clockEl=document.getElementById('obs-clock');
function tick(){{clockEl.textContent=new Date().toISOString().replace('T',' ').slice(0,19);}}
tick();setInterval(tick,1000);
</script>
</body>
</html>'''


def brb_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    lines_js = json.dumps(BRB_LINES, ensure_ascii=False)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 離席中</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:{_MONO_FONT};color:{color};}}

/* .obs- プレフィックス付き固有クラス群(waitingとは骨格が異なる: 左寄せ端末停止画面) */
.obs-halt-frame{{position:absolute;inset:0;width:1920px;height:1080px;z-index:10;display:flex;align-items:center;padding-left:140px;}}
.obs-halt-panel{{width:1180px;border-left:2px solid rgba({rgb},0.4);padding-left:48px;}}
.obs-halt-label{{font-size:12px;letter-spacing:8px;color:rgba({rgb},0.4);margin-bottom:26px;text-transform:uppercase;}}
.obs-halt-line{{font-size:15px;letter-spacing:1px;color:rgba({rgb},0.28);padding:4px 0;text-decoration:line-through;text-decoration-color:rgba({rgb},0.15);}}
.obs-halt-current{{font-size:26px;letter-spacing:2px;color:rgba({rgb},0.85);margin:22px 0;min-height:34px;}}
.obs-halt-cursor{{display:inline-block;width:16px;height:30px;background:{color};margin-left:8px;vertical-align:-6px;animation:obsHaltBlink 1s step-end infinite;box-shadow:0 0 14px {color};}}
@keyframes obsHaltBlink{{0%,100%{{opacity:1}}50%{{opacity:0}}}}
.obs-halt-footer{{margin-top:36px;font-size:11px;letter-spacing:5px;color:rgba({rgb},0.3);}}
canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:1;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="obs-halt-frame">
  <div class="obs-halt-panel">
    <div class="obs-halt-label">LOG HALTED</div>
    <div id="obs-history"></div>
    <div class="obs-halt-current">記録は継続されています<span class="obs-halt-cursor"></span></div>
    <div class="obs-halt-footer">対象の観測は継続されています</div>
  </div>
</div>
<script>
const canvas=document.getElementById('c');
const ctx=canvas.getContext('2d');
canvas.width=1920;canvas.height=1080;
let t=0;
function draw(){{
  ctx.clearRect(0,0,1920,1080);
  ctx.strokeStyle='rgba({rgb},0.04)';
  for(let x=0;x<1920;x+=90){{ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,1080);ctx.stroke();}}
  t+=0.003;
  requestAnimationFrame(draw);
}}
draw();

const LINES={lines_js};
const historyEl=document.getElementById('obs-history');
for(let i=0;i<3;i++){{
  const d=document.createElement('div');
  d.className='obs-halt-line';
  d.textContent=LINES[i%LINES.length];
  historyEl.appendChild(d);
}}
setInterval(()=>{{
  if(Math.random()<0.4){{
    const d=document.createElement('div');
    d.className='obs-halt-line';
    d.textContent=LINES[Math.floor(Math.random()*LINES.length)];
    historyEl.appendChild(d);
    if(historyEl.children.length>4) historyEl.removeChild(historyEl.firstChild);
  }}
}},4200);
</script>
</body>
</html>'''


def lower_third_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - ローワーサード</title>
<!--
  OBS設定: ブラウザソース → このHTMLを指定 → 幅1920 高さ1080
  名前変更: ?name=&title= のURLパラメータで指定してください
-->
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:transparent;overflow:hidden;font-family:{_MONO_FONT};}}

/* .obs- プレフィックス付き固有クラス群(端末プロンプト風) */
.obs-prompt{{position:absolute;bottom:80px;left:80px;display:flex;align-items:baseline;gap:14px;padding:14px 22px;background:rgba(0,10,4,0.5);border:1px solid rgba({rgb},0.35);animation:obsPromptIn .6s ease both;}}
@keyframes obsPromptIn{{from{{opacity:0;transform:translateX(-16px)}}to{{opacity:1;transform:translateX(0)}}}}
.obs-prompt-chevron{{font-size:30px;color:{color};text-shadow:0 0 10px {color};}}
.obs-prompt-name{{font-size:30px;letter-spacing:3px;color:rgba(255,255,255,0.94);}}
.obs-prompt-cursor{{display:inline-block;width:14px;height:26px;background:{color};margin-left:4px;vertical-align:-4px;animation:obsPCursor 1s step-end infinite;}}
@keyframes obsPCursor{{0%,100%{{opacity:1}}50%{{opacity:0}}}}
.obs-prompt-sub{{position:absolute;left:80px;bottom:52px;font-size:11px;letter-spacing:4px;color:rgba({rgb},0.55);}}
</style>
</head>
<body>
<div class="obs-prompt">
  <span class="obs-prompt-chevron">&gt;</span>
  <span class="obs-prompt-name" id="name-el">名前</span>
  <span class="obs-prompt-cursor"></span>
</div>
<div class="obs-prompt-sub" id="title-el">KYOUKAI</div>
<script>
const p=new URLSearchParams(window.location.search);
document.getElementById('name-el').textContent=p.get('name')||'名前';
document.getElementById('title-el').textContent=p.get('title')||'KYOUKAI';
</script>
</body>
</html>'''


SPEC = {
    "id": "observation",
    "name": "観測域",
    "color": COLOR,
    "rgb": RGB,
    "bg": BG,
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "対象の観測は継続されています",
        "label": "観測継続中",
        "brb_main": "記録は継続されています",
    },
}
