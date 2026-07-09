#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 極楽域(gokuraku) 専用実装

デザイン指針(ROADMAP・方式A・部屋専用の本体背景画像なしのためコードで表現):
  waiting: 引き出し棚をCSS gridで描画+スペクトルバーを棚に埋め込む
  brb: 引き出しが1つずつ開閉し音源番号が変わる(transform)
  lower_third: 引き出しラベル+音量バー内蔵

一次データ:
  static/images/entrances/entrance-gokuraku.png(参考のみ、同梱はしない)
外部画像・base64大画像埋め込みは禁止のため、棚・引き出し・スペクトルバーは
すべてCSS grid + Canvasで描画する。
"""
import json

SPEC_ID = "gokuraku"
NAME = "極楽域"
COLOR = "#ffaa44"
RGB = "255,170,68"
BG = "#040200"

DRAWER_ROWS = 4
DRAWER_COLS = 5

FRAGMENTS = [
    "引き出し 1", "── 開かない", "音響装置 起動", "記憶の収納",
    "奥へ続く", "扉 発見", "鍵 必要", "音が聞こえる",
    "── 何の音か", "極楽 ではない",
]

BRB_LINES = [
    "音源を調整しています",
    "引き出しを整理中",
    "奥への経路を確認中",
    "音響装置を再起動中",
    "記憶を参照しています",
]


def waiting_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    fragments_js = json.dumps(FRAGMENTS, ensure_ascii=False)
    drawers = []
    idx = 0
    for r in range(DRAWER_ROWS):
        for c in range(DRAWER_COLS):
            idx += 1
            drawers.append(
                f'<div class="gok-drawer" style="grid-row:{r+1};grid-column:{c+1};" data-idx="{idx}">'
                f'<canvas class="gok-drawer-spectrum" data-slot="{idx}" width="60" height="18"></canvas>'
                f'<span class="gok-drawer-num">{idx:02d}</span></div>'
            )
    drawers_html = ''.join(drawers)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 待機画面</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:'Courier New',monospace;color:{color};}}

/* .gok- プレフィックス付き固有クラス群(引き出し棚のCSS grid構成) */
.gok-label{{position:absolute;top:64px;left:0;width:100%;text-align:center;font-size:13px;letter-spacing:9px;color:rgba({rgb},0.6);z-index:6;text-transform:uppercase;}}
.gok-cabinet{{position:absolute;left:50%;top:50%;width:1200px;height:640px;margin:-320px 0 0 -600px;display:grid;grid-template-columns:repeat({DRAWER_COLS},1fr);grid-template-rows:repeat({DRAWER_ROWS},1fr);gap:14px;padding:20px;background:linear-gradient(180deg,#1a0f04,#0a0602);border:2px solid rgba({rgb},0.4);box-shadow:0 0 60px rgba({rgb},0.2) inset;}}
.gok-drawer{{position:relative;background:linear-gradient(180deg,rgba({rgb},0.14),rgba({rgb},0.04));border:1px solid rgba({rgb},0.45);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;transition:transform 0.4s ease;}}
.gok-drawer-spectrum{{width:60px;height:18px;}}
.gok-drawer-num{{font-size:11px;letter-spacing:2px;color:rgba({rgb},0.55);}}
.gok-fragment-log{{position:absolute;bottom:96px;left:0;width:100%;text-align:center;font-size:15px;letter-spacing:4px;color:rgba({rgb},0.65);z-index:6;min-height:24px;}}
canvas.gok-drawer-spectrum{{display:block;}}
</style>
</head>
<body>
<div class="gok-label">KYOUKAI // {NAME}</div>
<div class="gok-cabinet">{drawers_html}</div>
<div class="gok-fragment-log" id="gok-log">引き出し 1</div>
<script>
const FRAGMENTS={fragments_js};
const logEl=document.getElementById('gok-log');
function nextFragment(){{
  logEl.style.opacity='0';
  setTimeout(()=>{{
    logEl.textContent=FRAGMENTS[Math.floor(Math.random()*FRAGMENTS.length)];
    logEl.style.opacity='1';
  }},300);
}}
logEl.style.transition='opacity 0.3s ease';
setInterval(nextFragment,2800);

// 各引き出しのスペクトルバー(棚に埋め込み)
const bars=document.querySelectorAll('.gok-drawer-spectrum');
const ctxs=Array.from(bars).map(c=>c.getContext('2d'));
const heights=Array.from(bars).map(()=>Array.from({{length:10}},()=>Math.random()));
function drawSpectrum(){{
  ctxs.forEach((ctx,i)=>{{
    ctx.clearRect(0,0,60,18);
    const h=heights[i];
    for(let b=0;b<h.length;b++){{
      h[b]+=(Math.random()-0.5)*0.35;
      h[b]=Math.max(0.05,Math.min(1,h[b]));
      const barH=h[b]*16;
      ctx.fillStyle='rgba({rgb},'+(0.35+h[b]*0.5)+')';
      ctx.fillRect(b*6,18-barH,4,barH);
    }}
  }});
  requestAnimationFrame(drawSpectrum);
}}
drawSpectrum();
</script>
</body>
</html>'''


def brb_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    lines_js = json.dumps(BRB_LINES, ensure_ascii=False)
    drawers = ''.join(
        f'<div class="gok-brb-drawer" style="animation-delay:{i*0.35}s;"></div>'
        for i in range(5)
    )
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 離席中</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:'Courier New',monospace;color:{color};}}

/* .gok- プレフィックス付き固有クラス群(waitingとは骨格が異なる: 引き出しが1つずつ開閉するシーケンス構図) */
.gok-brb-stage{{position:absolute;inset:0;width:1920px;height:1080px;z-index:10;display:flex;flex-direction:column;align-items:center;justify-content:center;}}
.gok-brb-row{{display:flex;gap:24px;}}
.gok-brb-drawer{{width:140px;height:100px;background:linear-gradient(180deg,rgba({rgb},0.18),rgba({rgb},0.05));border:1px solid rgba({rgb},0.5);transform-origin:top center;animation:gokDrawerOpen 3.5s ease-in-out infinite;}}
@keyframes gokDrawerOpen{{0%,100%{{transform:translateY(0);}}30%{{transform:translateY(36px);}}60%{{transform:translateY(36px);}}}}
.gok-brb-num{{margin-top:56px;font-size:24px;letter-spacing:6px;color:{color};text-shadow:0 0 16px rgba({rgb},0.5);}}
.gok-brb-msg{{margin-top:24px;font-size:20px;letter-spacing:4px;color:{color};text-shadow:0 0 14px rgba({rgb},0.5);min-height:32px;opacity:0.85;}}
canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:1;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="gok-brb-stage">
  <div class="gok-brb-row">{drawers}</div>
  <div class="gok-brb-num" id="gok-num">音源番号 01</div>
  <div class="gok-brb-msg" id="gok-msg"></div>
</div>
<script>
const canvas=document.getElementById('c');
const ctx=canvas.getContext('2d');
canvas.width=1920;canvas.height=1080;
function draw(){{
  ctx.clearRect(0,0,1920,1080);
  ctx.fillStyle='rgba({rgb},0.02)';
  ctx.fillRect(0,0,1920,1080);
  requestAnimationFrame(draw);
}}
draw();

const numEl=document.getElementById('gok-num');
function cycleNum(){{
  const n=1+Math.floor(Math.random()*24);
  numEl.textContent='音源番号 '+String(n).padStart(2,'0');
}}
setInterval(cycleNum,3500);

const LINES={lines_js};
const msgEl=document.getElementById('gok-msg');
function showLine(){{
  msgEl.textContent=LINES[Math.floor(Math.random()*LINES.length)];
  msgEl.style.opacity='1';
  setTimeout(()=>{{msgEl.style.opacity='0';}},2200);
}}
msgEl.style.transition='opacity 0.5s ease';
setInterval(showLine,4000);
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
html,body{{width:1920px;height:1080px;background:transparent;overflow:hidden;font-family:'Courier New',monospace;}}

/* .gok- プレフィックス付き固有クラス群(引き出しラベル+音量バー内蔵テロップ) */
.gok-lt-frame{{position:absolute;bottom:80px;left:80px;display:flex;align-items:center;gap:0;background:linear-gradient(180deg,rgba({rgb},0.14),rgba({rgb},0.04));border:1px solid rgba({rgb},0.5);}}
.gok-lt-label{{padding:14px 18px;font-size:11px;letter-spacing:3px;color:rgba({rgb},0.6);border-right:1px solid rgba({rgb},0.4);}}
.gok-lt-name{{padding:14px 26px;font-size:32px;letter-spacing:3px;color:rgba(255,255,255,0.94);}}
.gok-lt-bars{{display:flex;align-items:flex-end;gap:3px;padding-right:18px;height:24px;}}
.gok-lt-bar{{width:4px;background:rgba({rgb},0.8);animation:gokLtBar 1.2s ease-in-out infinite;}}
.gok-lt-bar:nth-child(1){{height:40%;animation-delay:0s;}}
.gok-lt-bar:nth-child(2){{height:70%;animation-delay:.15s;}}
.gok-lt-bar:nth-child(3){{height:100%;animation-delay:.3s;}}
.gok-lt-bar:nth-child(4){{height:55%;animation-delay:.45s;}}
@keyframes gokLtBar{{0%,100%{{transform:scaleY(0.4);}}50%{{transform:scaleY(1);}}}}
.gok-lt-title{{position:absolute;left:80px;bottom:52px;font-size:11px;letter-spacing:4px;color:rgba({rgb},0.55);}}
</style>
</head>
<body>
<div class="gok-lt-frame">
  <div class="gok-lt-label">引出 03</div>
  <span class="gok-lt-name" id="name-el">名前</span>
  <div class="gok-lt-bars">
    <div class="gok-lt-bar"></div><div class="gok-lt-bar"></div><div class="gok-lt-bar"></div><div class="gok-lt-bar"></div>
  </div>
</div>
<div class="gok-lt-title" id="title-el">KYOUKAI</div>
<script>
const p=new URLSearchParams(window.location.search);
document.getElementById('name-el').textContent=p.get('name')||'名前';
document.getElementById('title-el').textContent=p.get('title')||'KYOUKAI';
</script>
</body>
</html>'''


SPEC = {
    "id": "gokuraku",
    "name": "極楽域",
    "color": COLOR,
    "rgb": RGB,
    "bg": BG,
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "奥への扉はまだ開いていません",
        "label": "音源 再生中",
        "brb_main": "音源を調整しています",
    },
}
