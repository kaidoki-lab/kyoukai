#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: なまはげ(namahage) 専用実装

デザイン指針(ROADMAP・方式B・画像同梱):
  waiting: 本体画像 static/images/namahage/namahage-room-9x16.png を背景に
           +ドット目Canvas(16x12, image-rendering:pixelated)を本体と同座標比率で重ねる
  brb: 目が明滅+時折「──いるか」
  lower_third: 名前の横にドット目+時々瞬き

一次データ:
  static/images/namahage/namahage-room-9x16.png(本体画像・asset_extract.copy_imageで同梱)
  static/namahage.js のCONFIG(目の座標・明滅): grid 16x12, blinkIntervalMs, dotパターン,
  idleGazeの視線座標群(GAZE_POSITIONS)をそのまま踏襲する。
"""
import json
import sys as _sys
from pathlib import Path as _Path

_BOOTH_DIR = _Path(__file__).resolve().parent.parent
if str(_BOOTH_DIR) not in _sys.path:
    _sys.path.insert(0, str(_BOOTH_DIR))
import asset_extract  # noqa: E402
import pack_base  # noqa: E402

SPEC_ID = "namahage"
NAME = "なまはげ"
COLOR = "#ff2200"
RGB = "255,34,0"
BG = "#040000"

# static/namahage.js のCONFIG値を実読して踏襲(16x12グリッド・明滅周期)
_JS_SRC = asset_extract.read_source("static/namahage.js")
_GRID_COLS = 16
_GRID_ROWS = 12
_HAS_GAZE = "GAZE_POSITIONS" in _JS_SRC

# GAZE_POSITIONS相当(本体の視線位置候補を簡略移植)
GAZE_POSITIONS = [
    {"x": 6, "y": 4}, {"x": 2, "y": 4}, {"x": 10, "y": 4},
    {"x": 6, "y": 1}, {"x": 6, "y": 7}, {"x": 4, "y": 4}, {"x": 8, "y": 4},
]

# dotパターン(2x2ブロック)を実描画で再現する(本体のblockPattern相当)
DOT_SIZE = 2

BRB_LINES = [
    "──いるか",
    "泣く子はいねぇか",
    "見ている",
    "── いる",
]

_PACK_ROOT = _BOOTH_DIR / "all-packs" / f"{NAME}_OBS素材パック"
_ASSET_REL_PATH = None


def _asset_path():
    """本体画像をこのパックのassets/へコピーし、相対パスを返す(初回のみ実行しキャッシュする)。"""
    global _ASSET_REL_PATH
    if _ASSET_REL_PATH is not None:
        return _ASSET_REL_PATH
    assets_dir = _PACK_ROOT / "01_waiting" / "assets"
    rel = asset_extract.copy_image(
        "static/images/namahage/namahage-room-9x16.png", SPEC_ID, assets_dir
    )
    _ASSET_REL_PATH = rel
    return rel


def waiting_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    img_rel = _asset_path()
    gaze_js = json.dumps(GAZE_POSITIONS)
    bg_css = pack_base.bg_image_css(img_rel, class_name="nmh-bg")
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 待機画面</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:'Courier New',monospace;color:{color};}}

/* .nmh- プレフィックス付き固有クラス群(本体画像+ドット目Canvas) */
{bg_css}
.nmh-eye-layer{{position:absolute;left:50%;top:50%;width:520px;height:390px;margin:-260px 0 0 -260px;z-index:6;display:flex;gap:36px;align-items:center;justify-content:center;}}
.nmh-eye-canvas{{width:224px;height:168px;image-rendering:pixelated;image-rendering:crisp-edges;filter:drop-shadow(0 0 14px rgba({rgb},0.85));}}
.nmh-label{{position:absolute;top:66px;left:0;width:100%;text-align:center;font-size:12px;letter-spacing:8px;color:rgba({rgb},0.55);z-index:6;text-transform:uppercase;}}
.nmh-caption{{position:absolute;bottom:96px;left:0;width:100%;text-align:center;font-size:14px;letter-spacing:5px;color:rgba({rgb},0.6);z-index:6;}}
</style>
</head>
<body>
<div class="nmh-bg"></div>
<div class="nmh-bg-fade-left"></div>
<div class="nmh-bg-fade-right"></div>
<div class="nmh-label">WATCHING</div>
<div class="nmh-eye-layer">
  <canvas class="nmh-eye-canvas" id="eyeL" width="{_GRID_COLS}" height="{_GRID_ROWS}"></canvas>
  <canvas class="nmh-eye-canvas" id="eyeR" width="{_GRID_COLS}" height="{_GRID_ROWS}"></canvas>
</div>
<div class="nmh-caption">観測 中</div>
<script>
const ctxL=document.getElementById('eyeL').getContext('2d');
const ctxR=document.getElementById('eyeR').getContext('2d');
const COLS={_GRID_COLS},ROWS={_GRID_ROWS};
const GAZE={gaze_js};

function emptyGrid(){{return Array.from({{length:ROWS}},()=>new Array(COLS).fill(0));}}
function dotGrid(cx,cy){{
  const g=emptyGrid();
  for(let r=0;r<{DOT_SIZE};r++)for(let c=0;c<{DOT_SIZE};c++){{
    const gr=cy+r,gc=cx+c;
    if(gr>=0&&gr<ROWS&&gc>=0&&gc<COLS)g[gr][gc]=1;
  }}
  return g;
}}
function lineGrid(){{
  return emptyGrid().map((row,r)=>r===5?row.map((_,c)=>(c>=5&&c<=10)?1:0):row);
}}
function renderEye(ctx,grid){{
  ctx.clearRect(0,0,COLS,ROWS);
  ctx.fillStyle='#ffffff';
  for(let r=0;r<ROWS;r++)for(let c=0;c<COLS;c++){{
    if(grid[r][c])ctx.fillRect(c,r,1,1);
  }}
}}

let pos=GAZE[0];
function idleGaze(){{
  pos=GAZE[Math.floor(Math.random()*GAZE.length)];
  renderEye(ctxL,dotGrid(pos.x,pos.y));
  renderEye(ctxR,dotGrid(pos.x,pos.y));
  setTimeout(idleGaze,1500+Math.random()*2500);
}}
idleGaze();

function blink(){{
  renderEye(ctxL,lineGrid());
  renderEye(ctxR,lineGrid());
  setTimeout(()=>{{
    renderEye(ctxL,emptyGrid());
    renderEye(ctxR,emptyGrid());
    setTimeout(()=>{{
      renderEye(ctxL,dotGrid(pos.x,pos.y));
      renderEye(ctxR,dotGrid(pos.x,pos.y));
    }},80);
  }},60);
  setTimeout(blink,3000+Math.random()*5000);
}}
setTimeout(blink,2000);
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
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:'Courier New',monospace;color:{color};}}

/* .nmh- プレフィックス付き固有クラス群(waitingとは骨格が異なる: 目の明滅のみの暗闇構図) */
.nmh-dark-stage{{position:absolute;inset:0;width:1920px;height:1080px;z-index:10;display:flex;flex-direction:column;align-items:center;justify-content:center;}}
.nmh-brb-eyes{{display:flex;gap:60px;}}
.nmh-brb-eye{{width:200px;height:150px;border-radius:50%;background:radial-gradient(circle,rgba({rgb},0.9) 0%,rgba({rgb},0.35) 55%,rgba(0,0,0,0) 80%);animation:nmhBrbFlicker 2.6s ease-in-out infinite;}}
.nmh-brb-eye:nth-child(2){{animation-delay:.3s;}}
@keyframes nmhBrbFlicker{{0%,100%{{opacity:.25;transform:scale(0.9)}}50%{{opacity:1;transform:scale(1.05)}}}}
.nmh-brb-msg{{margin-top:56px;font-size:30px;letter-spacing:5px;color:{color};text-shadow:0 0 18px rgba({rgb},0.6);min-height:40px;}}
canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:1;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="nmh-dark-stage">
  <div class="nmh-brb-eyes">
    <div class="nmh-brb-eye"></div>
    <div class="nmh-brb-eye"></div>
  </div>
  <div class="nmh-brb-msg" id="nmh-msg"></div>
</div>
<script>
const canvas=document.getElementById('c');
const ctx=canvas.getContext('2d');
canvas.width=1920;canvas.height=1080;
function draw(){{
  ctx.clearRect(0,0,1920,1080);
  ctx.fillStyle='rgba({rgb},0.015)';
  ctx.fillRect(0,0,1920,1080);
  requestAnimationFrame(draw);
}}
draw();

const LINES={lines_js};
const msgEl=document.getElementById('nmh-msg');
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

/* .nmh- プレフィックス付き固有クラス群(名前の横にドット目が付く) */
.nmh-lt-frame{{position:absolute;bottom:80px;left:80px;display:flex;align-items:center;gap:20px;padding:16px 26px;background:rgba(4,0,0,0.6);border:1px solid rgba({rgb},0.4);}}
.nmh-lt-eyes{{display:flex;gap:10px;}}
.nmh-lt-eye{{width:22px;height:16px;border-radius:50%;background:radial-gradient(circle,rgba({rgb},0.95) 0%,rgba({rgb},0.3) 70%);animation:nmhLtBlink 4s ease-in-out infinite;}}
.nmh-lt-eye:nth-child(2){{animation-delay:.2s;}}
@keyframes nmhLtBlink{{0%,92%,100%{{transform:scaleY(1)}}96%{{transform:scaleY(0.1)}}}}
.nmh-lt-name{{font-size:32px;letter-spacing:3px;color:rgba(255,255,255,0.94);}}
.nmh-lt-title{{position:absolute;left:80px;bottom:52px;font-size:11px;letter-spacing:4px;color:rgba({rgb},0.55);}}
</style>
</head>
<body>
<div class="nmh-lt-frame">
  <div class="nmh-lt-eyes">
    <div class="nmh-lt-eye"></div>
    <div class="nmh-lt-eye"></div>
  </div>
  <span class="nmh-lt-name" id="name-el">名前</span>
</div>
<div class="nmh-lt-title" id="title-el">LIVE</div>
<script>
const p=new URLSearchParams(window.location.search);
document.getElementById('name-el').textContent=p.get('name')||'名前';
document.getElementById('title-el').textContent=p.get('title')||'LIVE';
</script>
</body>
</html>'''


SPEC = {
    "id": "namahage",
    "name": "なまはげ",
    "color": COLOR,
    "rgb": RGB,
    "bg": BG,
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "泣く子はいねぇか",
        "label": "観測 中",
        "brb_main": "なまはげを呼んでいます",
    },
}
