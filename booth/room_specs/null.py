#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 崩落域(null) 専用実装

デザイン指針(ROADMAP):
  waiting: 画面自体が傾き・崩れる。UI部品がずり落ちる演出
  brb: 画面が周期的に崩壊→再構築を繰り返す(行ズレグリッチ強化)
  lower_third: 名前の文字が時々欠落・復元するテロップ

一次データ:
  static/kyoukai-404.js の文字崩壊演出(NOISE文字集合・corrupt()のratio刻み・stage概念)
  templates/null.html の崩壊度UI(未使用時のフォールバック文言含む)
"""
import json
import sys as _sys
from pathlib import Path as _Path

_BOOTH_DIR = _Path(__file__).resolve().parent.parent
if str(_BOOTH_DIR) not in _sys.path:
    _sys.path.insert(0, str(_BOOTH_DIR))
import asset_extract  # noqa: E402

SPEC_ID = "null"
NAME = "崩落域"
COLOR = "#ff4433"
RGB = "255,68,51"
BG = "#080000"

# static/kyoukai-404.js から実際に読み取った崩壊演出の根拠(NOISE文字集合をそのまま踏襲)
_JS_SRC = asset_extract.read_source("static/kyoukai-404.js")
NOISE_CHARS = "░▒▓█▌▐▀▄╬╪╫▪▬►◄↕§▲▼╳╱" if "NOISE" in _JS_SRC else "#"

FRAGMENTS = [
    "接続 悪化",
    "データ 欠損",
    "── 取得失敗",
    "崩壊度 上昇",
    "ERROR",
    "NULL",
    "── ──",
    "回復 不能",
    "座標 消失",
    "悪化している",
]

BRB_LINES = [
    "崩落を記録中です",
    "データを回収しています",
    "接続を維持しようとしています",
    "崩壊が続いています",
    "戻れません",
]


def waiting_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    frag_js = json.dumps(FRAGMENTS, ensure_ascii=False)
    noise_js = json.dumps(NOISE_CHARS, ensure_ascii=False)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 待機画面</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:'Courier New',monospace;color:{color};}}

/* .null- プレフィックス付き固有クラス群(傾き崩落レイアウト) */
.null-tilt-root{{position:absolute;inset:0;width:1920px;height:1080px;z-index:10;transform-origin:50% 40%;animation:nullTiltDrift 9s ease-in-out infinite;}}
@keyframes nullTiltDrift{{0%{{transform:rotate(0deg) translateY(0)}}30%{{transform:rotate(-0.6deg) translateY(4px)}}55%{{transform:rotate(0.3deg) translateY(-3px)}}80%{{transform:rotate(-0.2deg) translateY(2px)}}100%{{transform:rotate(0deg) translateY(0)}}}}
.null-panel{{position:absolute;border:1px solid rgba({rgb},0.35);background:rgba(20,0,0,0.35);padding:22px 28px;}}
.null-panel--title{{top:70px;left:90px;width:560px;}}
.null-panel--status{{top:70px;right:90px;width:340px;text-align:right;}}
.null-panel--fragments{{bottom:130px;left:90px;width:900px;height:280px;overflow:hidden;}}
.null-panel--gauge{{bottom:130px;right:90px;width:340px;}}
.null-code{{font-size:120px;letter-spacing:6px;color:{color};text-shadow:0 0 22px rgba({rgb},0.6);}}
.null-sub{{font-size:14px;letter-spacing:5px;color:rgba({rgb},0.55);margin-top:8px;}}
.null-status-label{{font-size:12px;letter-spacing:4px;color:rgba({rgb},0.55);}}
.null-status-value{{font-size:22px;margin-top:6px;color:{color};}}
.null-frag-line{{font-size:16px;letter-spacing:1px;color:rgba({rgb},0.75);padding:4px 0;white-space:nowrap;}}
.null-gauge-bar{{width:100%;height:10px;background:rgba({rgb},0.12);margin-top:10px;position:relative;overflow:hidden;}}
.null-gauge-fill{{position:absolute;left:0;top:0;bottom:0;width:20%;background:{color};box-shadow:0 0 12px {color};}}
.null-slip{{position:absolute;pointer-events:none;}}
canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:1;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="null-tilt-root" id="null-root">
  <div class="null-panel null-panel--title">
    <div class="null-code" id="null-code">404</div>
    <div class="null-sub">COLLAPSE STANDBY</div>
  </div>
  <div class="null-panel null-panel--status">
    <div class="null-status-label">崩壊度</div>
    <div class="null-status-value" id="null-degree">12%</div>
  </div>
  <div class="null-panel null-panel--fragments" id="null-frag-panel"></div>
  <div class="null-panel null-panel--gauge">
    <div class="null-status-label">構造維持率</div>
    <div class="null-gauge-bar"><div class="null-gauge-fill" id="null-gauge"></div></div>
  </div>
</div>
<script>
const canvas=document.getElementById('c');
const ctx=canvas.getContext('2d');
canvas.width=1920;canvas.height=1080;
const NOISE={noise_js};
function drawStatic(){{
  ctx.clearRect(0,0,1920,1080);
  ctx.fillStyle='rgba({rgb},0.03)';
  for(let i=0;i<40;i++){{
    const x=Math.random()*1920,y=Math.random()*1080,w=Math.random()*120+20,h=1;
    ctx.fillRect(x,y,w,h);
  }}
  requestAnimationFrame(drawStatic);
}}
drawStatic();

const FRAGMENTS={frag_js};
const fragPanel=document.getElementById('null-frag-panel');
function corrupt(text,ratio){{
  return text.split('').map(ch=>{{
    if(ch===' ')return ch;
    return Math.random()<ratio?NOISE[Math.floor(Math.random()*NOISE.length)]:ch;
  }}).join('');
}}
const rows=[];
for(let i=0;i<8;i++){{
  const d=document.createElement('div');
  d.className='null-frag-line';
  d.textContent=FRAGMENTS[i%FRAGMENTS.length];
  fragPanel.appendChild(d);
  rows.push(d);
}}
setInterval(()=>{{
  const row=rows[Math.floor(Math.random()*rows.length)];
  const base=FRAGMENTS[Math.floor(Math.random()*FRAGMENTS.length)];
  row.textContent=corrupt(base,0.35);
  setTimeout(()=>{{row.textContent=base;}},600);
}},1300);

const codeEl=document.getElementById('null-code');
setInterval(()=>{{
  const orig='404';
  const chars=orig.split('');
  const idx=Math.floor(Math.random()*chars.length);
  chars[idx]=NOISE[Math.floor(Math.random()*NOISE.length)];
  codeEl.textContent=chars.join('');
  setTimeout(()=>{{codeEl.textContent=orig;}},150);
}},2600);

const degreeEl=document.getElementById('null-degree');
const gaugeEl=document.getElementById('null-gauge');
let deg=12;
setInterval(()=>{{
  deg=(deg+Math.floor(Math.random()*9)-2+100)%100;
  degreeEl.textContent=deg+'%';
  gaugeEl.style.width=(100-deg)+'%';
}},1800);

// UI部品がずり落ちる演出(パネルごとに個別のドリフト)
const panels=document.querySelectorAll('.null-panel');
panels.forEach((p,i)=>{{
  let offset=0;
  setInterval(()=>{{
    offset=(offset+Math.random()*3-1);
    offset=Math.max(-6,Math.min(6,offset));
    p.style.transform=`translate(${{offset}}px, ${{Math.abs(offset)*0.6}}px)`;
  }},1500+i*200);
}});
</script>
</body>
</html>'''


def brb_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    lines_js = json.dumps(BRB_LINES, ensure_ascii=False)
    noise_js = json.dumps(NOISE_CHARS, ensure_ascii=False)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 離席中</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:'Courier New',monospace;color:{color};}}

/* .null- プレフィックス付き固有クラス群(waitingとは骨格が異なる: 中央崩壊→再構築サイクル) */
.null-collapse-stage{{position:absolute;inset:0;width:1920px;height:1080px;z-index:10;display:flex;flex-direction:column;align-items:center;justify-content:center;}}
.null-collapse-msg{{font-size:42px;letter-spacing:6px;text-align:center;color:{color};text-shadow:0 0 20px rgba({rgb},0.6);}}
.null-collapse-sub{{font-size:14px;letter-spacing:5px;color:rgba({rgb},0.55);margin-top:26px;}}
.null-rows{{position:absolute;top:0;left:0;width:100%;height:100%;z-index:5;pointer-events:none;}}
.null-glitch-row{{position:absolute;left:0;width:100%;height:4px;background:rgba({rgb},0.5);opacity:0;}}
canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:1;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="null-rows" id="null-rows"></div>
<div class="null-collapse-stage" id="null-stage">
  <div class="null-collapse-msg" id="null-msg">崩落を記録中です</div>
  <div class="null-collapse-sub">構造は再構築フェーズに入っています</div>
</div>
<script>
const canvas=document.getElementById('c');
const ctx=canvas.getContext('2d');
canvas.width=1920;canvas.height=1080;
const NOISE={noise_js};
let phase=0; // 0=stable 1=collapsing 2=rebuilding
function draw(){{
  ctx.clearRect(0,0,1920,1080);
  const alpha=phase===1?0.09:0.02;
  ctx.fillStyle='rgba({rgb},'+alpha+')';
  const n=phase===1?70:15;
  for(let i=0;i<n;i++){{
    ctx.fillRect(Math.random()*1920,Math.random()*1080,Math.random()*160+10,2);
  }}
  requestAnimationFrame(draw);
}}
draw();

const LINES={lines_js};
const msgEl=document.getElementById('null-msg');
const stageEl=document.getElementById('null-stage');
const rowsWrap=document.getElementById('null-rows');
const glitchRows=[];
for(let i=0;i<18;i++){{
  const r=document.createElement('div');
  r.className='null-glitch-row';
  r.style.top=(Math.random()*1080)+'px';
  rowsWrap.appendChild(r);
  glitchRows.push(r);
}}

function collapseCycle(){{
  phase=1;
  stageEl.style.transform='scale(0.96) translateY(-6px)';
  glitchRows.forEach(r=>{{
    r.style.opacity=String(Math.random()*0.5+0.2);
    r.style.top=(Math.random()*1080)+'px';
    r.style.transform=`translateX(${{Math.random()*40-20}}px)`;
  }});
  msgEl.textContent=LINES[Math.floor(Math.random()*LINES.length)];
  setTimeout(()=>{{
    phase=2;
    stageEl.style.transform='scale(1) translateY(0)';
    glitchRows.forEach(r=>{{r.style.opacity='0';}});
  }},1100);
  setTimeout(()=>{{phase=0;}},2200);
}}
setInterval(collapseCycle,4000);
stageEl.style.transition='transform 0.6s ease';
</script>
</body>
</html>'''


def lower_third_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    noise_js = json.dumps(NOISE_CHARS, ensure_ascii=False)
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
html,body{{width:1920px;height:1080px;background:transparent;overflow:hidden;font-family:'Courier New',monospace;}}

/* .null- プレフィックス付き固有クラス群(文字が欠落・復元するテロップ) */
.null-lt-frame{{position:absolute;bottom:78px;left:80px;padding:16px 26px;background:rgba(8,0,0,0.55);border:1px solid rgba({rgb},0.4);clip-path:polygon(0 0,96% 0,100% 30%,100% 100%,4% 100%,0 70%);animation:nullLtIn .5s ease both;}}
@keyframes nullLtIn{{from{{opacity:0;transform:translateY(10px) skewX(-2deg)}}to{{opacity:1;transform:translateY(0) skewX(0)}}}}
.null-lt-name{{font-size:32px;letter-spacing:2px;color:{color};text-shadow:0 0 12px rgba({rgb},0.5);}}
.null-lt-title{{position:absolute;left:80px;bottom:52px;font-size:11px;letter-spacing:4px;color:rgba({rgb},0.55);}}
</style>
</head>
<body>
<div class="null-lt-frame">
  <span class="null-lt-name" id="name-el">名前</span>
</div>
<div class="null-lt-title" id="title-el">LIVE</div>
<script>
const p=new URLSearchParams(window.location.search);
const origName=p.get('name')||'名前';
const origTitle=p.get('title')||'LIVE';
const nameEl=document.getElementById('name-el');
const titleEl=document.getElementById('title-el');
nameEl.textContent=origName;
titleEl.textContent=origTitle;

const NOISE={noise_js};
function corrupt(text,ratio){{
  return text.split('').map(ch=>{{
    if(ch===' ')return ch;
    return Math.random()<ratio?NOISE[Math.floor(Math.random()*NOISE.length)]:ch;
  }}).join('');
}}
setInterval(()=>{{
  nameEl.textContent=corrupt(origName,0.3);
  setTimeout(()=>{{nameEl.textContent=origName;}},350);
}},3200);
</script>
</body>
</html>'''


SPEC = {
    "id": "null",
    "name": "崩落域",
    "color": COLOR,
    "rgb": RGB,
    "bg": BG,
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "構造は再構築フェーズに入っています",
        "label": "崩壊 進行中",
        "brb_main": "崩落を記録中です",
    },
}
