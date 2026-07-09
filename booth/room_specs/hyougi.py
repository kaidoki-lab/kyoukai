#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 評議録(hyougi) 専用実装

デザイン指針(ROADMAP):
  waiting: 縦書き風の議事断片が浮かぶ和紙質感、中央に議題番号
  brb: 何も書かれない議事用紙に時折「──」だけが打たれる
  lower_third: 毛筆風の縦線+発言者札のような名札

一次データ: templates/hyougi.html の配色・文体(評議記録の断片文体、暗色+琥珀トーン)
落とし穴対応: writing-mode:vertical-rl はChromium(OBS)では動くがフォント次第で崩れるため、
  等幅フォールバック('MS Mincho', 'Courier New', monospace)を明示指定する。
"""
import json
import sys as _sys
from pathlib import Path as _Path

_BOOTH_DIR = _Path(__file__).resolve().parent.parent
if str(_BOOTH_DIR) not in _sys.path:
    _sys.path.insert(0, str(_BOOTH_DIR))
import asset_extract  # noqa: E402

SPEC_ID = "hyougi"
NAME = "評議録"
COLOR = "#ccbb99"
RGB = "204,187,153"
BG = "#080600"

# templates/hyougi.html を実読込し、配色(琥珀系グラデーション背景)を確認した根拠
_HYOUGI_SRC = asset_extract.read_source("templates/hyougi.html")
assert "hyougi-room-body" in _HYOUGI_SRC

_VERTICAL_FONT = "'MS Mincho', 'Yu Mincho', 'Courier New', monospace"

FRAGMENTS = [
    "誰かが発言した",
    "議題は曖昧なままだ",
    "── いや、それは違う",
    "結論はまだ出ていない",
    "合意は不成立である",
    "記録のみが残る",
    "発言者は不明のままだ",
    "── おそらく、そうだろう",
    "再度確認を求める",
    "議事は継続する",
]


def waiting_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    frags_js = json.dumps(FRAGMENTS, ensure_ascii=False)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 待機画面</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;overflow:hidden;font-family:{_VERTICAL_FONT};color:{color};
  background:radial-gradient(circle at 50% 44%,rgba(255,220,160,0.10),transparent 40%),{bg};}}

/* .hyo- プレフィックス付き固有クラス群(縦書き議事断片+和紙質感+中央議題番号) */
.hyo-washi{{position:absolute;inset:0;width:1920px;height:1080px;background:
  repeating-linear-gradient(115deg,rgba(255,255,255,0.012) 0 2px,transparent 2px 6px),
  repeating-linear-gradient(25deg,rgba(255,255,255,0.01) 0 2px,transparent 2px 7px);
  z-index:1;}}
.hyo-columns{{position:absolute;inset:0;width:1920px;height:1080px;z-index:5;display:flex;flex-direction:row-reverse;justify-content:center;gap:64px;padding:90px 60px;}}
.hyo-col{{writing-mode:vertical-rl;text-orientation:mixed;font-size:22px;letter-spacing:6px;line-height:2.4;color:rgba({rgb},0.5);opacity:0;animation:hyoRise 9s ease-in-out infinite;}}
@keyframes hyoRise{{0%,100%{{opacity:0;transform:translateY(20px)}}10%,80%{{opacity:1;transform:translateY(0)}}90%{{opacity:0}}}}
.hyo-center{{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);z-index:6;text-align:center;}}
.hyo-center-num{{writing-mode:vertical-rl;font-size:64px;letter-spacing:14px;color:rgba({rgb},0.85);text-shadow:0 0 24px rgba({rgb},0.2);}}
.hyo-center-label{{margin-top:18px;font-size:12px;letter-spacing:8px;color:rgba({rgb},0.4);}}
.hyo-footer{{position:absolute;bottom:56px;left:0;right:0;text-align:center;font-size:11px;letter-spacing:6px;color:rgba({rgb},0.32);z-index:6;}}
canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:0;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="hyo-washi"></div>
<div class="hyo-columns" id="hyo-columns"></div>
<div class="hyo-center">
  <div class="hyo-center-num" id="hyo-num">議題　第〇〇号</div>
  <div class="hyo-center-label">記録 進行中</div>
</div>
<div class="hyo-footer">記録は継続されています</div>
<script>
const canvas=document.getElementById('c');
const ctx=canvas.getContext('2d');
canvas.width=1920;canvas.height=1080;
function drawGrain(){{
  ctx.fillStyle='rgba({rgb},0.008)';
  for(let i=0;i<60;i++){{
    ctx.fillRect(Math.random()*1920,Math.random()*1080,1,1);
  }}
  requestAnimationFrame(drawGrain);
}}
drawGrain();

const FRAGS={frags_js};
const colWrap=document.getElementById('hyo-columns');
const COLS=6;
for(let i=0;i<COLS;i++){{
  const col=document.createElement('div');
  col.className='hyo-col';
  col.textContent=FRAGS[i%FRAGS.length];
  col.style.animationDelay=(i*1.4)+'s';
  colWrap.appendChild(col);
}}
setInterval(()=>{{
  const col=colWrap.children[Math.floor(Math.random()*COLS)];
  col.textContent=FRAGS[Math.floor(Math.random()*FRAGS.length)];
}},3000);

const numEl=document.getElementById('hyo-num');
let n=1;
setInterval(()=>{{
  n=(n%99)+1;
  numEl.textContent='議題　第'+String(n).padStart(2,'0')+'号';
}},8000);
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
html,body{{width:1920px;height:1080px;overflow:hidden;font-family:{_VERTICAL_FONT};color:{color};
  background:radial-gradient(circle at 50% 44%,rgba(255,220,160,0.06),transparent 40%),{bg};}}

/* .hyo- プレフィックス付き固有クラス群(白紙の議事用紙に時折「──」だけが打たれる。waitingとは全く異なる単一用紙構成) */
.hyo-paper{{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:640px;height:880px;background:linear-gradient(180deg,rgba(30,26,18,0.5),rgba(10,8,4,0.7));border:1px solid rgba({rgb},0.22);box-shadow:0 0 60px rgba(0,0,0,0.6),inset 0 0 60px rgba(0,0,0,0.4);z-index:5;}}
.hyo-paper-mark{{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);writing-mode:vertical-rl;font-size:46px;letter-spacing:24px;color:rgba({rgb},0.5);opacity:0;animation:hyoMark 4s ease-in-out infinite;}}
@keyframes hyoMark{{0%,60%{{opacity:0}}68%,88%{{opacity:0.8}}100%{{opacity:0}}}}
.hyo-paper-label{{position:absolute;top:32px;left:0;right:0;text-align:center;font-size:11px;letter-spacing:8px;color:rgba({rgb},0.35);text-transform:uppercase;}}
.hyo-footer{{position:absolute;bottom:56px;left:0;right:0;text-align:center;font-size:11px;letter-spacing:6px;color:rgba({rgb},0.3);z-index:6;}}
canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:0;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="hyo-paper">
  <div class="hyo-paper-label">議事 一時中断</div>
  <div class="hyo-paper-mark">── ──</div>
</div>
<div class="hyo-footer">記録は継続されています</div>
<script>
const canvas=document.getElementById('c');
const ctx=canvas.getContext('2d');
canvas.width=1920;canvas.height=1080;
function draw(){{
  ctx.fillStyle='rgba({rgb},0.006)';
  ctx.fillRect(0,0,1920,1080);
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
html,body{{width:1920px;height:1080px;background:transparent;overflow:hidden;font-family:{_VERTICAL_FONT};}}

/* .hyo- プレフィックス付き固有クラス群(毛筆風の縦線+発言者札) */
.hyo-fuda{{position:absolute;bottom:70px;left:80px;display:flex;align-items:flex-end;gap:20px;animation:hyoFudaIn .7s ease both;}}
@keyframes hyoFudaIn{{from{{opacity:0;transform:translateY(20px)}}to{{opacity:1;transform:translateY(0)}}}}
.hyo-brush-line{{width:4px;height:150px;background:linear-gradient(to bottom,transparent,{color} 20%,{color} 80%,transparent);}}
.hyo-fuda-plate{{writing-mode:vertical-rl;background:linear-gradient(160deg,rgba(28,22,14,0.92),rgba(10,8,4,0.88));border:1px solid rgba({rgb},0.4);padding:20px 14px;box-shadow:0 10px 24px rgba(0,0,0,0.5);}}
.hyo-fuda-name{{font-size:30px;letter-spacing:6px;color:rgba(255,246,224,0.94);}}
.hyo-fuda-title{{margin-top:14px;font-size:12px;letter-spacing:4px;color:rgba({rgb},0.6);}}
</style>
</head>
<body>
<div class="hyo-fuda">
  <div class="hyo-brush-line"></div>
  <div class="hyo-fuda-plate">
    <span class="hyo-fuda-name" id="name-el">名前</span>
    <span class="hyo-fuda-title" id="title-el">KYOUKAI</span>
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
    "id": "hyougi",
    "name": "評議録",
    "color": COLOR,
    "rgb": RGB,
    "bg": BG,
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "記録は継続されています",
        "label": "記録 進行中",
        "brb_main": "議事 一時中断",
    },
}
