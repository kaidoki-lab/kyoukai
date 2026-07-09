#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 境界域(exit) 専用実装

デザイン指針(ROADMAP):
  waiting: ロード画面そのもの。プログレスバーが進んでは戻る
  brb: 通路の奥行き表現(遠近の枠が流れる)+接続メッセージ
  lower_third: 境界線をまたぐ二重枠のテロップ

一次データ: templates/exit.html のロード画面演出(exit-loader構成、Loading/signal unstable/connecting文言)
"""
import sys as _sys
from pathlib import Path as _Path

_BOOTH_DIR = _Path(__file__).resolve().parent.parent
if str(_BOOTH_DIR) not in _sys.path:
    _sys.path.insert(0, str(_BOOTH_DIR))
import asset_extract  # noqa: E402

SPEC_ID = "exit"
NAME = "境界域"
COLOR = "#aaaaaa"
RGB = "170,170,170"
BG = "#050505"

# templates/exit.html を実読込し、ロード演出の文言構成を確認した根拠
_EXIT_SRC = asset_extract.read_source("templates/exit.html")
assert "exit-loader" in _EXIT_SRC


def waiting_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 待機画面</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:'Courier New',monospace;color:{color};}}

/* .exit- プレフィックス付き固有クラス群(ロード画面そのもの) */
.exit-load-stage{{position:absolute;inset:0;width:1920px;height:1080px;z-index:10;display:flex;flex-direction:column;align-items:center;justify-content:center;}}
.exit-load-label{{font-size:13px;letter-spacing:10px;color:rgba({rgb},0.4);text-transform:uppercase;margin-bottom:40px;}}
.exit-load-bar-track{{width:900px;height:6px;background:rgba({rgb},0.12);position:relative;overflow:hidden;}}
.exit-load-bar-fill{{position:absolute;top:0;left:0;height:100%;width:0%;background:linear-gradient(to right,rgba({rgb},0.3),{color});box-shadow:0 0 16px rgba({rgb},0.4);}}
.exit-load-pct{{margin-top:22px;font-size:32px;letter-spacing:4px;color:rgba({rgb},0.8);}}
.exit-load-messages{{margin-top:32px;height:22px;font-size:12px;letter-spacing:5px;color:rgba({rgb},0.4);}}
.exit-load-frames{{position:absolute;inset:0;pointer-events:none;z-index:5;}}
.exit-load-frame{{position:absolute;border:1px solid rgba({rgb},0.1);}}
canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:1;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="exit-load-frames" id="exit-frames"></div>
<div class="exit-load-stage">
  <div class="exit-load-label">境界を越えようとしています</div>
  <div class="exit-load-bar-track"><div class="exit-load-bar-fill" id="exit-fill"></div></div>
  <div class="exit-load-pct" id="exit-pct">0%</div>
  <div class="exit-load-messages" id="exit-msg">Loading...</div>
</div>
<script>
const canvas=document.getElementById('c');
const ctx=canvas.getContext('2d');
canvas.width=1920;canvas.height=1080;
function drawStatic(){{
  ctx.fillStyle='rgba({rgb},0.01)';
  ctx.fillRect(0,0,1920,1080);
  requestAnimationFrame(drawStatic);
}}
drawStatic();

const framesWrap=document.getElementById('exit-frames');
const FRAME_COUNT=6;
const frameEls=[];
for(let i=0;i<FRAME_COUNT;i++){{
  const f=document.createElement('div');
  f.className='exit-load-frame';
  framesWrap.appendChild(f);
  frameEls.push(f);
}}
function layoutFrames(){{
  frameEls.forEach((f,i)=>{{
    const scale=0.2+i*0.16;
    const w=1920*scale, h=1080*scale;
    f.style.width=w+'px';
    f.style.height=h+'px';
    f.style.left=((1920-w)/2)+'px';
    f.style.top=((1080-h)/2)+'px';
  }});
}}
layoutFrames();

const fillEl=document.getElementById('exit-fill');
const pctEl=document.getElementById('exit-pct');
const msgEl=document.getElementById('exit-msg');
const MSGS=['Loading...','signal unstable...','connecting...','経路を再構築中','出口を探しています'];
let pct=0, dir=1;
function stepProgress(){{
  pct+=dir*(Math.random()*3+1);
  if(pct>=94){{dir=-1;pct=94;}}
  if(pct<=8 && dir<0){{dir=1;pct=8;}}
  fillEl.style.width=pct+'%';
  pctEl.textContent=Math.floor(pct)+'%';
}}
setInterval(stepProgress,220);
let mi=0;
setInterval(()=>{{mi=(mi+1)%MSGS.length;msgEl.textContent=MSGS[mi];}},1800);
</script>
</body>
</html>'''


def brb_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 離席中</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:'Courier New',monospace;color:{color};}}

/* .exit- プレフィックス付き固有クラス群(通路の奥行き表現。waitingとは全く異なる同心枠トンネル構成) */
.exit-tunnel{{position:absolute;inset:0;width:1920px;height:1080px;display:flex;align-items:center;justify-content:center;z-index:5;perspective:1200px;}}
.exit-tunnel-ring{{position:absolute;border:1px solid rgba({rgb},0.25);animation:exitTunnelMove 3.2s linear infinite;}}
@keyframes exitTunnelMove{{from{{transform:scale(0.05);opacity:0;}}30%{{opacity:1;}}to{{transform:scale(2.2);opacity:0;}}}}
.exit-connect-msg{{position:relative;z-index:6;text-align:center;}}
.exit-connect-main{{font-size:44px;letter-spacing:10px;color:rgba({rgb},0.85);text-shadow:0 0 30px rgba({rgb},0.3);}}
.exit-connect-sub{{margin-top:22px;font-size:12px;letter-spacing:6px;color:rgba({rgb},0.4);}}
canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:1;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="exit-tunnel" id="exit-tunnel">
  <div class="exit-connect-msg">
    <div class="exit-connect-main">境界を越えています</div>
    <div class="exit-connect-sub">出口はまだ見つかっていません</div>
  </div>
</div>
<script>
const canvas=document.getElementById('c');
const ctx=canvas.getContext('2d');
canvas.width=1920;canvas.height=1080;
function draw(){{
  ctx.fillStyle='rgba({rgb},0.02)';
  ctx.fillRect(0,0,1920,1080);
  requestAnimationFrame(draw);
}}
draw();

const tunnel=document.getElementById('exit-tunnel');
const RING_W=[900,700,520,360,220,100];
function spawnRing(){{
  const ring=document.createElement('div');
  ring.className='exit-tunnel-ring';
  const w=RING_W[Math.floor(Math.random()*RING_W.length)];
  ring.style.width=w+'px';
  ring.style.height=(w*0.56)+'px';
  ring.style.animationDuration=(2.6+Math.random()*1.2)+'s';
  tunnel.insertBefore(ring, tunnel.firstChild);
  setTimeout(()=>{{ if(ring.parentNode) ring.parentNode.removeChild(ring); }},4200);
}}
setInterval(spawnRing,260);
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

/* .exit- プレフィックス付き固有クラス群(境界線をまたぐ二重枠) */
.exit-double-frame{{position:absolute;bottom:74px;left:76px;padding:2px;animation:exitFrameIn .7s ease both;}}
@keyframes exitFrameIn{{from{{opacity:0;transform:translateX(-14px)}}to{{opacity:1;transform:translateX(0)}}}}
.exit-outer-border{{border:1px solid rgba({rgb},0.3);padding:6px;}}
.exit-inner-border{{border:1px solid rgba({rgb},0.6);padding:16px 26px;background:rgba(5,5,5,0.55);position:relative;}}
.exit-inner-border::before{{content:'';position:absolute;left:-9px;top:50%;width:16px;height:1px;background:rgba({rgb},0.5);}}
.exit-name{{font-size:30px;letter-spacing:4px;color:rgba(255,255,255,0.94);}}
.exit-title{{margin-top:10px;font-size:11px;letter-spacing:5px;color:rgba({rgb},0.55);}}
</style>
</head>
<body>
<div class="exit-double-frame">
  <div class="exit-outer-border">
    <div class="exit-inner-border">
      <div class="exit-name" id="name-el">名前</div>
      <div class="exit-title" id="title-el">KYOUKAI</div>
    </div>
  </div>
</div>
<script>
const p=new URLSearchParams(window.location.search);
document.getElementById('name-el').textContent=p.get('name')||'名前';
document.getElementById('title-el').textContent=p.get('title')||'KYOUKAI';
</script>
</body>
</html>'''


SPEC = {
    "id": "exit",
    "name": "境界域",
    "color": COLOR,
    "rgb": RGB,
    "bg": BG,
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "出口はまだ見つかっていません",
        "label": "接続中",
        "brb_main": "境界を越えています",
    },
}
