#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 棒入れ祭(matsuri) 専用実装

デザイン指針(ROADMAP・方式B・画像同梱):
  waiting: 本体素材(棒・穴・紙吹雪)を配置した祭り画面+奉納カウンタ
  brb: firework sparkが上がり続け「奉納の準備」
  lower_third: 祭り半纏風の縁取り+紙吹雪が散る

一次データ:
  static/images/matsuri/ の棒・穴・紙吹雪素材(asset_extract.ASSET_MAPで確定済み)
  static/matsuri.js の演出定数(DEPTH_MAX・メッセージ文言・紙吹雪カラーパレット)を踏襲
"""
import json
import sys as _sys
from pathlib import Path as _Path

_BOOTH_DIR = _Path(__file__).resolve().parent.parent
if str(_BOOTH_DIR) not in _sys.path:
    _sys.path.insert(0, str(_BOOTH_DIR))
import asset_extract  # noqa: E402

SPEC_ID = "matsuri"
NAME = "棒入れ祭"
COLOR = "#ffdd00"
RGB = "255,221,0"
BG = "#040200"

# static/matsuri.js の紙吹雪カラーパレットを踏襲
CONFETTI_COLORS = ["#e0c66a", "#d8483f", "#f4efe0", "#9bb15b"]

VOICE_MESSAGES = ["ヨイショ！", "ヨイショー！", "オイサ！", "エンヤ！", "ソレ！", "押せー！"]

BRB_LINES = [
    "奉納の準備をしています",
    "観衆が集まっています",
    "棒を準備中です",
    "奉納を再開します",
    "── 急いで",
]

_PACK_ROOT = _BOOTH_DIR / "all-packs" / f"{NAME}_OBS素材パック"
_ASSET_REL_PATHS = None

_SRC_FILES = [
    "static/images/matsuri/pole/06_pole_main.png",
    "static/images/matsuri/hole/10_hole_main.png",
    "static/images/matsuri/confetti/20_confetti_mix1.png",
    "static/images/matsuri/decoration/16_gohei.png",
]


def _asset_paths():
    """本体素材(棒・穴・紙吹雪・御幣)をこのパックのassets/へコピーし、相対パス辞書を返す。"""
    global _ASSET_REL_PATHS
    if _ASSET_REL_PATHS is not None:
        return _ASSET_REL_PATHS
    assets_dir = _PACK_ROOT / "01_waiting" / "assets"
    paths = {}
    for src in _SRC_FILES:
        rel = asset_extract.copy_image(src, SPEC_ID, assets_dir)
        key = _Path(src).stem
        paths[key] = rel
    _ASSET_REL_PATHS = paths
    return paths


def waiting_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    assets = _asset_paths()
    pole_rel = assets["06_pole_main"]
    hole_rel = assets["10_hole_main"]
    confetti_rel = assets["20_confetti_mix1"]
    gohei_rel = assets["16_gohei"]
    voices_js = json.dumps(VOICE_MESSAGES, ensure_ascii=False)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 待機画面</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:'Courier New',monospace;color:{color};}}

/* .mat- プレフィックス付き固有クラス群(祭り画面: 棒・穴・御幣・紙吹雪を配置) */
.mat-stage{{position:absolute;inset:0;width:1920px;height:1080px;background:radial-gradient(ellipse at 50% 30%,#1a1004 0%,{bg} 70%);}}
.mat-label{{position:absolute;top:64px;left:0;width:100%;text-align:center;font-size:13px;letter-spacing:9px;color:rgba({rgb},0.6);z-index:6;text-transform:uppercase;}}
.mat-hole{{position:absolute;left:50%;bottom:120px;width:260px;height:160px;margin-left:-130px;background:url('{hole_rel}') center/contain no-repeat;z-index:3;filter:drop-shadow(0 0 30px rgba({rgb},0.3));}}
.mat-pole{{position:absolute;left:50%;bottom:220px;width:120px;height:560px;margin-left:-60px;background:url('{pole_rel}') center/contain no-repeat;z-index:4;transform-origin:bottom center;animation:matPoleSway 2.6s ease-in-out infinite;}}
@keyframes matPoleSway{{0%,100%{{transform:rotate(-2deg);}}50%{{transform:rotate(2deg);}}}}
.mat-gohei{{position:absolute;top:120px;left:120px;width:100px;height:180px;background:url('{gohei_rel}') center/contain no-repeat;z-index:5;opacity:0.85;}}
.mat-gohei--right{{left:auto;right:120px;}}
.mat-counter{{position:absolute;top:64px;right:96px;font-size:12px;letter-spacing:3px;color:rgba({rgb},0.55);z-index:6;}}
.mat-voice-log{{position:absolute;bottom:80px;left:0;width:100%;text-align:center;font-size:26px;letter-spacing:6px;color:{color};z-index:6;min-height:36px;text-shadow:0 0 16px rgba({rgb},0.6);}}
.mat-confetti-layer{{position:absolute;inset:0;z-index:7;pointer-events:none;overflow:hidden;}}
.mat-confetti-piece{{position:absolute;top:-40px;width:26px;height:26px;background:url('{confetti_rel}') center/contain no-repeat;animation:matConfettiFall linear forwards;}}
@keyframes matConfettiFall{{0%{{transform:translateY(0) rotate(0deg);opacity:1;}}100%{{transform:translateY(1120px) rotate(360deg);opacity:0;}}}}
canvas.mat-spark-canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:2;pointer-events:none;}}
</style>
</head>
<body>
<div class="mat-stage"></div>
<canvas class="mat-spark-canvas" id="mat-spark"></canvas>
<div class="mat-label">FESTIVAL STANDBY</div>
<div class="mat-counter" id="mat-counter">奉納回数 0</div>
<div class="mat-gohei"></div>
<div class="mat-gohei mat-gohei--right"></div>
<div class="mat-hole"></div>
<div class="mat-pole"></div>
<div class="mat-voice-log" id="mat-voice"></div>
<div class="mat-confetti-layer" id="mat-confetti"></div>
<script>
const sparkCanvas=document.getElementById('mat-spark');
const sparkCtx=sparkCanvas.getContext('2d');
sparkCanvas.width=1920;sparkCanvas.height=1080;
let sparkParticles=[];
function spawnAmbientSpark(){{
  sparkParticles.push({{x:Math.random()*1920,y:1080,vx:(Math.random()-0.5)*1.2,vy:-2-Math.random()*2,life:60}});
}}
function drawAmbientSparks(){{
  sparkCtx.clearRect(0,0,1920,1080);
  sparkParticles.forEach(p=>{{
    p.x+=p.vx;p.y+=p.vy;p.life-=1;
    sparkCtx.globalAlpha=Math.max(0,p.life/60);
    sparkCtx.fillStyle='#ffcc55';
    sparkCtx.fillRect(p.x,p.y,2,2);
  }});
  sparkCtx.globalAlpha=1;
  sparkParticles=sparkParticles.filter(p=>p.life>0);
  requestAnimationFrame(drawAmbientSparks);
}}
drawAmbientSparks();
setInterval(spawnAmbientSpark,300);

const VOICES={voices_js};
const voiceEl=document.getElementById('mat-voice');
const counterEl=document.getElementById('mat-counter');
const confettiLayer=document.getElementById('mat-confetti');
let count=0;
function showVoice(){{
  voiceEl.textContent=VOICES[Math.floor(Math.random()*VOICES.length)];
  voiceEl.style.opacity='1';
  count+=1;
  counterEl.textContent='奉納回数 '+count;
  setTimeout(()=>{{voiceEl.style.opacity='0';}},1400);
}}
voiceEl.style.transition='opacity 0.4s ease';
setInterval(showVoice,2600);

function spawnConfetti(){{
  const piece=document.createElement('div');
  piece.className='mat-confetti-piece';
  piece.style.left=(Math.random()*100)+'%';
  const dur=2.2+Math.random()*1.6;
  piece.style.animationDuration=dur+'s';
  confettiLayer.appendChild(piece);
  setTimeout(()=>piece.remove(),(dur+0.3)*1000);
}}
setInterval(spawnConfetti,450);
</script>
</body>
</html>'''


def brb_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    lines_js = json.dumps(BRB_LINES, ensure_ascii=False)
    colors_js = json.dumps(CONFETTI_COLORS)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 離席中</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:'Courier New',monospace;color:{color};}}

/* .mat- プレフィックス付き固有クラス群(waitingとは骨格が異なる: 花火sparkが上がり続ける祭りの夜構図) */
.mat-brb-stage{{position:absolute;inset:0;width:1920px;height:1080px;z-index:10;display:flex;flex-direction:column;align-items:center;justify-content:center;}}
.mat-brb-lantern{{width:120px;height:150px;border-radius:60px 60px 20px 20px;background:radial-gradient(circle at 50% 40%,rgba({rgb},0.9),rgba(120,20,0,0.6));box-shadow:0 0 60px rgba({rgb},0.5);animation:matLanternGlow 2.8s ease-in-out infinite;}}
@keyframes matLanternGlow{{0%,100%{{opacity:0.7;}}50%{{opacity:1;}}}}
.mat-brb-msg{{margin-top:48px;font-size:30px;letter-spacing:5px;color:{color};text-shadow:0 0 18px rgba({rgb},0.6);min-height:40px;}}
canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:5;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="mat-brb-stage">
  <div class="mat-brb-lantern"></div>
  <div class="mat-brb-msg" id="mat-msg"></div>
</div>
<script>
const canvas=document.getElementById('c');
const ctx=canvas.getContext('2d');
canvas.width=1920;canvas.height=1080;
const COLORS={colors_js};
let sparks=[];
function spawnSpark(){{
  const cx=200+Math.random()*1520;
  const cy=900+Math.random()*100;
  const n=18+Math.floor(Math.random()*10);
  const color=COLORS[Math.floor(Math.random()*COLORS.length)];
  for(let i=0;i<n;i++){{
    const angle=(Math.PI*2*i)/n;
    const speed=2+Math.random()*4;
    sparks.push({{x:cx,y:cy,vx:Math.cos(angle)*speed,vy:Math.sin(angle)*speed-6,life:60,color}});
  }}
}}
function drawSparks(){{
  ctx.fillStyle='rgba(4,2,0,0.15)';
  ctx.fillRect(0,0,1920,1080);
  sparks.forEach(s=>{{
    s.x+=s.vx;s.y+=s.vy;s.vy+=0.12;s.life-=1;
    ctx.globalAlpha=Math.max(0,s.life/60);
    ctx.fillStyle=s.color;
    ctx.fillRect(s.x,s.y,3,3);
  }});
  ctx.globalAlpha=1;
  sparks=sparks.filter(s=>s.life>0);
  requestAnimationFrame(drawSparks);
}}
drawSparks();
setInterval(spawnSpark,900);
spawnSpark();

const LINES={lines_js};
const msgEl=document.getElementById('mat-msg');
function showLine(){{
  msgEl.textContent=LINES[Math.floor(Math.random()*LINES.length)];
  msgEl.style.opacity='1';
  setTimeout(()=>{{msgEl.style.opacity='0';}},2200);
}}
msgEl.style.transition='opacity 0.5s ease';
setInterval(showLine,4200);
</script>
</body>
</html>'''


def lower_third_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    colors_js = json.dumps(CONFETTI_COLORS)
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

/* .mat- プレフィックス付き固有クラス群(祭り半纏風の縁取り+紙吹雪が散るテロップ) */
.mat-lt-frame{{position:absolute;bottom:80px;left:80px;padding:16px 30px;background:linear-gradient(90deg,rgba(60,10,10,0.85),rgba(20,4,4,0.85));border:3px solid rgba({rgb},0.7);border-radius:2px;position:relative;overflow:visible;}}
.mat-lt-frame::before{{content:'';position:absolute;top:-6px;left:-6px;right:-6px;bottom:-6px;border:1px solid rgba({rgb},0.35);pointer-events:none;}}
.mat-lt-name{{font-size:32px;letter-spacing:3px;color:rgba(255,255,255,0.94);}}
.mat-lt-title{{position:absolute;left:80px;bottom:52px;font-size:11px;letter-spacing:4px;color:rgba({rgb},0.55);}}
.mat-lt-confetti-layer{{position:absolute;top:60px;left:80px;width:420px;height:120px;pointer-events:none;overflow:visible;}}
.mat-lt-confetti-piece{{position:absolute;top:-10px;width:8px;height:8px;animation:matLtFall linear forwards;}}
@keyframes matLtFall{{0%{{transform:translateY(0) rotate(0deg);opacity:1;}}100%{{transform:translateY(140px) rotate(280deg);opacity:0;}}}}
</style>
</head>
<body>
<div class="mat-lt-confetti-layer" id="mat-lt-confetti"></div>
<div class="mat-lt-frame">
  <span class="mat-lt-name" id="name-el">名前</span>
</div>
<div class="mat-lt-title" id="title-el">LIVE</div>
<script>
const p=new URLSearchParams(window.location.search);
document.getElementById('name-el').textContent=p.get('name')||'名前';
document.getElementById('title-el').textContent=p.get('title')||'LIVE';

const COLORS={colors_js};
const layer=document.getElementById('mat-lt-confetti');
function spawn(){{
  const piece=document.createElement('div');
  piece.className='mat-lt-confetti-piece';
  piece.style.left=(Math.random()*100)+'%';
  piece.style.background=COLORS[Math.floor(Math.random()*COLORS.length)];
  const dur=1.4+Math.random()*1.0;
  piece.style.animationDuration=dur+'s';
  layer.appendChild(piece);
  setTimeout(()=>piece.remove(),(dur+0.2)*1000);
}}
setInterval(spawn,600);
</script>
</body>
</html>'''


SPEC = {
    "id": "matsuri",
    "name": "棒入れ祭",
    "color": COLOR,
    "rgb": RGB,
    "bg": BG,
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "奉納は継続されています",
        "label": "奉納 進行中",
        "brb_main": "奉納の準備をしています",
    },
}
