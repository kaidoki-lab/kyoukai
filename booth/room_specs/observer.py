#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 逆観測室(observer) 専用実装

デザイン指針(ROADMAP):
  waiting: 中央に瞳孔のような円環。UI最小限、視線を感じる構図
  brb: 巨大な目がゆっくり開閉し「観測は続いています」
  lower_third: 名前が視線カーソルに追われる/下線が瞳孔型

一次データ:
  templates/observer.html の語りかけ文体・配色(白基調・観測される側の視点、
  「みてる？」のスピーチバブル、observer-bg等の白系トーン)
"""
import sys as _sys
from pathlib import Path as _Path

_BOOTH_DIR = _Path(__file__).resolve().parent.parent
if str(_BOOTH_DIR) not in _sys.path:
    _sys.path.insert(0, str(_BOOTH_DIR))
import asset_extract  # noqa: E402

SPEC_ID = "observer"
NAME = "逆観測室"
COLOR = "#ffffff"
RGB = "255,255,255"
BG = "#050505"

# templates/observer.html の語りかけ文体を実際に読み取り根拠にする
_HTML_SRC = asset_extract.read_source("templates/observer.html")
_HAS_MASCOT = "mascot" in _HTML_SRC

WHISPER_LINES = [
    "あなたは",
    "ずっと",
    "観測されていた",
    "気づいていましたか",
    "最初から",
    "ここにいた",
    "見ていたのは",
    "あなたではない",
    "静かに",
    "逃げられない",
]


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

/* .obsr- プレフィックス付き固有クラス群(中央瞳孔+UI最小限) */
.obsr-stage{{position:absolute;inset:0;width:1920px;height:1080px;z-index:10;display:flex;align-items:center;justify-content:center;}}
.obsr-iris-wrap{{position:relative;width:520px;height:520px;}}
.obsr-ring{{position:absolute;border-radius:50%;border:1px solid rgba({rgb},0.5);}}
.obsr-ring--outer{{inset:0;animation:obsrRingSpin 60s linear infinite;}}
.obsr-ring--mid{{inset:60px;border-color:rgba({rgb},0.3);animation:obsrRingSpin 42s linear infinite reverse;}}
.obsr-ring--inner{{inset:150px;border-color:rgba({rgb},0.7);}}
@keyframes obsrRingSpin{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}
.obsr-pupil{{position:absolute;left:50%;top:50%;width:120px;height:120px;margin:-60px 0 0 -60px;border-radius:50%;background:radial-gradient(circle at 40% 35%,#fff 0%,#d9d9d9 55%,#050505 100%);box-shadow:0 0 60px rgba({rgb},0.35);animation:obsrPupilPulse 4.5s ease-in-out infinite;}}
@keyframes obsrPupilPulse{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.06)}}}}
.obsr-caption{{position:absolute;bottom:96px;left:0;width:100%;text-align:center;font-size:13px;letter-spacing:10px;color:rgba({rgb},0.55);text-transform:uppercase;}}
.obsr-corner-label{{position:absolute;top:64px;left:90px;font-size:12px;letter-spacing:5px;color:rgba({rgb},0.55);}}
.obsr-whisper{{position:absolute;font-size:15px;letter-spacing:3px;color:rgba({rgb},0.35);white-space:nowrap;pointer-events:none;}}
canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:1;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="obsr-corner-label">OBSERVATION</div>
<div class="obsr-stage">
  <div class="obsr-iris-wrap">
    <div class="obsr-ring obsr-ring--outer"></div>
    <div class="obsr-ring obsr-ring--mid"></div>
    <div class="obsr-ring obsr-ring--inner"></div>
    <div class="obsr-pupil"></div>
  </div>
</div>
<div class="obsr-caption">観測は継続されています</div>
<div id="obsr-whisper-layer"></div>
<script>
const canvas=document.getElementById('c');
const ctx=canvas.getContext('2d');
canvas.width=1920;canvas.height=1080;
function drawField(){{
  ctx.clearRect(0,0,1920,1080);
  ctx.strokeStyle='rgba({rgb},0.035)';
  ctx.lineWidth=1;
  const cx=960,cy=540;
  for(let r=560;r<1400;r+=140){{
    ctx.beginPath();
    ctx.arc(cx,cy,r,0,Math.PI*2);
    ctx.stroke();
  }}
  requestAnimationFrame(drawField);
}}
drawField();

// 視線を感じる構図: たまに囁きがフェードイン/アウトする
const WHISPERS={WHISPER_LINES!r};
const layer=document.getElementById('obsr-whisper-layer');
function spawnWhisper(){{
  const el=document.createElement('div');
  el.className='obsr-whisper';
  el.textContent=WHISPERS[Math.floor(Math.random()*WHISPERS.length)];
  el.style.left=(200+Math.random()*1500)+'px';
  el.style.top=(150+Math.random()*750)+'px';
  el.style.transition='color 2.4s ease';
  layer.appendChild(el);
  requestAnimationFrame(()=>{{el.style.color='rgba({rgb},0.32)';}});
  setTimeout(()=>{{el.style.color='rgba({rgb},0)';}},2600);
  setTimeout(()=>{{layer.removeChild(el);}},5200);
}}
setInterval(spawnWhisper,3400);
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

/* .obsr- プレフィックス付き固有クラス群(waitingとは骨格が異なる: 巨大な目の開閉) */
.obsr-eye-stage{{position:absolute;inset:0;width:1920px;height:1080px;z-index:10;display:flex;align-items:center;justify-content:center;}}
.obsr-eye{{position:relative;width:960px;height:480px;}}
.obsr-eye-shape{{position:absolute;inset:0;background:radial-gradient(ellipse at center,#f4f4f4 0%,#c9c9c9 55%,#050505 100%);border-radius:50%;clip-path:ellipse(48% 50% at 50% 50%);animation:obsrBlink 6s ease-in-out infinite;transform-origin:center;}}
@keyframes obsrBlink{{0%,84%,100%{{transform:scaleY(1)}}88%{{transform:scaleY(0.05)}}92%{{transform:scaleY(1)}}}}
.obsr-eye-pupil{{position:absolute;left:50%;top:50%;width:180px;height:180px;margin:-90px 0 0 -90px;border-radius:50%;background:#050505;box-shadow:0 0 90px rgba({rgb},0.3);}}
.obsr-eye-msg{{position:absolute;bottom:110px;left:0;width:100%;text-align:center;font-size:34px;letter-spacing:6px;color:{color};text-shadow:0 0 16px rgba({rgb},0.4);}}
.obsr-eye-sub{{position:absolute;top:110px;left:0;width:100%;text-align:center;font-size:12px;letter-spacing:6px;color:rgba({rgb},0.55);}}
canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:1;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="obsr-eye-stage">
  <div class="obsr-eye">
    <div class="obsr-eye-shape"></div>
    <div class="obsr-eye-pupil"></div>
  </div>
</div>
<div class="obsr-eye-sub">OBSERVATION IN PROGRESS</div>
<div class="obsr-eye-msg">観測は続いています</div>
<script>
const canvas=document.getElementById('c');
const ctx=canvas.getContext('2d');
canvas.width=1920;canvas.height=1080;
function draw(){{
  ctx.clearRect(0,0,1920,1080);
  ctx.strokeStyle='rgba({rgb},0.03)';
  for(let x=0;x<1920;x+=120){{ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,1080);ctx.stroke();}}
  requestAnimationFrame(draw);
}}
draw();
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

/* .obsr- プレフィックス付き固有クラス群(視線カーソルに追われる名前) */
.obsr-lt-wrap{{position:absolute;bottom:86px;left:0;width:100%;display:flex;justify-content:center;}}
.obsr-lt-name{{position:relative;font-size:34px;letter-spacing:5px;color:rgba(255,255,255,0.95);padding-bottom:10px;}}
.obsr-lt-pupil-underline{{position:absolute;left:50%;bottom:0;width:26px;height:26px;margin-left:-13px;border-radius:50%;background:radial-gradient(circle at 40% 35%,#fff 0%,#bcbcbc 55%,#050505 100%);box-shadow:0 0 12px rgba({rgb},0.6);transition:transform .4s ease;}}
.obsr-lt-title{{position:absolute;left:0;bottom:54px;width:100%;text-align:center;font-size:11px;letter-spacing:5px;color:rgba({rgb},0.55);}}
</style>
</head>
<body>
<div class="obsr-lt-wrap">
  <div class="obsr-lt-name">
    <span id="name-el">名前</span>
    <div class="obsr-lt-pupil-underline" id="obsr-pupil"></div>
  </div>
</div>
<div class="obsr-lt-title" id="title-el">LIVE</div>
<script>
const p=new URLSearchParams(window.location.search);
document.getElementById('name-el').textContent=p.get('name')||'名前';
document.getElementById('title-el').textContent=p.get('title')||'LIVE';

// 瞳孔型下線が視線カーソルのように左右にゆっくり動く(実際のマウス追従は不要な用途のため自律運動)
const pupil=document.getElementById('obsr-pupil');
let dir=1,x=0;
setInterval(()=>{{
  x+=dir*6;
  if(x>18||x<-18)dir*=-1;
  pupil.style.transform='translateX('+x+'px)';
}},700);
</script>
</body>
</html>'''


SPEC = {
    "id": "observer",
    "name": "逆観測室",
    "color": COLOR,
    "rgb": RGB,
    "bg": BG,
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "観測は続いています",
        "label": "観測 逆転",
        "brb_main": "観測は続いています",
    },
}
