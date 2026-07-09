#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 悪魔の間(ma) 専用実装

デザイン指針(ROADMAP・方式A、画像なし):
  waiting: 呼吸する赤い光をコードで再現+計器なし
  brb: 光が呼吸し沈黙のセリフが間欠表示
  lower_third: 紋様付き黒枠+名前が赤い刻印風

一次データ:
  static/ma.js の会話データ(CONVS)・沈黙がちな話者「大魔将」の口調
  (「……帰れ。」「長居はするな。」等、間を強く意識した台詞)を演出言語として踏襲。
  アセット画像は流用せず、コードのみで「呼吸する背景」を表現する(ASSET_MAP上もma:[])。
"""
import json
import sys as _sys
from pathlib import Path as _Path

_BOOTH_DIR = _Path(__file__).resolve().parent.parent
if str(_BOOTH_DIR) not in _sys.path:
    _sys.path.insert(0, str(_BOOTH_DIR))
import asset_extract  # noqa: E402

SPEC_ID = "ma"
NAME = "悪魔の間"
COLOR = "#cc1122"
RGB = "204,17,34"
BG = "#040000"

# static/ma.js の台詞データを実読し、「沈黙」「間」を強く感じさせる短句のみを抽出して踏襲する
_JS_SRC = asset_extract.read_source("static/ma.js")
_HAS_CONVS = "CONVS" in _JS_SRC

SILENCE_LINES = [
    "……帰れ。",
    "長居はするな。",
    "……少しだけ、暇だった。",
    "闇とはな、恐ろしいものではない。",
    "ただ、静かなのだ。",
    "待っていたわけでは、ない。",
    "……ゆっくりしていけ。",
    "貴様は物好きだな。",
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

/* .ma- プレフィックス付き固有クラス群(計器なし・呼吸する光のみ) */
.ma-void{{position:absolute;inset:0;width:1920px;height:1080px;z-index:5;}}
.ma-glow-core{{position:absolute;left:50%;top:50%;width:640px;height:640px;margin:-320px 0 0 -320px;border-radius:50%;background:radial-gradient(circle,rgba({rgb},0.5) 0%,rgba({rgb},0.14) 45%,rgba(0,0,0,0) 72%);animation:maBreathe 5.2s ease-in-out infinite;}}
@keyframes maBreathe{{0%,100%{{transform:scale(0.85);opacity:0.55}}50%{{transform:scale(1.12);opacity:0.95}}}}
.ma-sigil{{position:absolute;left:50%;top:50%;width:360px;height:360px;margin:-180px 0 0 -180px;border:1px solid rgba({rgb},0.35);border-radius:50%;animation:maSigilSpin 40s linear infinite;}}
.ma-sigil::before,.ma-sigil::after{{content:'';position:absolute;inset:34px;border:1px solid rgba({rgb},0.22);border-radius:50%;}}
.ma-sigil::after{{inset:70px;border-color:rgba({rgb},0.15);}}
@keyframes maSigilSpin{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}
.ma-label{{position:absolute;top:70px;left:0;width:100%;text-align:center;font-size:13px;letter-spacing:10px;color:rgba({rgb},0.4);text-transform:uppercase;}}
.ma-silence-line{{position:absolute;bottom:110px;left:0;width:100%;text-align:center;font-size:20px;letter-spacing:3px;color:rgba({rgb},0.0);transition:color 2s ease;}}
canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:1;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="ma-label">KYOUKAI // {NAME} // 存在確認</div>
<div class="ma-void">
  <div class="ma-glow-core"></div>
  <div class="ma-sigil"></div>
</div>
<div class="ma-silence-line" id="ma-silence"></div>
<script>
const canvas=document.getElementById('c');
const ctx=canvas.getContext('2d');
canvas.width=1920;canvas.height=1080;
let t=0;
function draw(){{
  ctx.clearRect(0,0,1920,1080);
  const breathe=(Math.sin(t)+1)/2;
  ctx.fillStyle='rgba({rgb},'+(0.02+breathe*0.02)+')';
  ctx.fillRect(0,0,1920,1080);
  t+=0.012;
  requestAnimationFrame(draw);
}}
draw();

// 台詞は「大魔将」の沈黙がちな口調を踏襲し、長い無言のあとに短く現れる
const LINES={json.dumps(SILENCE_LINES, ensure_ascii=False)};
const silenceEl=document.getElementById('ma-silence');
function showSilenceLine(){{
  silenceEl.textContent=LINES[Math.floor(Math.random()*LINES.length)];
  silenceEl.style.color='rgba({rgb},0.5)';
  setTimeout(()=>{{silenceEl.style.color='rgba({rgb},0)';}},2600);
}}
setInterval(showSilenceLine,7000);
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

/* .ma- プレフィックス付き固有クラス群(waitingとは骨格が異なる: 光の呼吸+間欠セリフのみの中央構図) */
.ma-brb-stage{{position:absolute;inset:0;width:1920px;height:1080px;z-index:10;display:flex;flex-direction:column;align-items:center;justify-content:center;}}
.ma-brb-glow{{position:absolute;left:50%;top:50%;width:900px;height:900px;margin:-450px 0 0 -450px;border-radius:50%;background:radial-gradient(circle,rgba({rgb},0.42) 0%,rgba({rgb},0.1) 50%,rgba(0,0,0,0) 75%);animation:maBrbBreathe 6.4s ease-in-out infinite;}}
@keyframes maBrbBreathe{{0%,100%{{transform:scale(0.8);opacity:0.5}}50%{{transform:scale(1.18);opacity:1}}}}
.ma-brb-msg{{position:relative;z-index:10;font-size:30px;letter-spacing:4px;color:{color};text-shadow:0 0 24px rgba({rgb},0.7);min-height:44px;text-align:center;}}
.ma-brb-sub{{position:relative;z-index:10;font-size:12px;letter-spacing:6px;color:rgba({rgb},0.4);margin-top:24px;}}
canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:1;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="ma-brb-stage">
  <div class="ma-brb-glow"></div>
  <div class="ma-brb-msg" id="ma-brb-msg">大魔将は沈黙しています</div>
  <div class="ma-brb-sub">存在はここにある</div>
</div>
<script>
const canvas=document.getElementById('c');
const ctx=canvas.getContext('2d');
canvas.width=1920;canvas.height=1080;
let t=0;
function draw(){{
  ctx.clearRect(0,0,1920,1080);
  const breathe=(Math.sin(t)+1)/2;
  ctx.fillStyle='rgba({rgb},'+(0.015+breathe*0.03)+')';
  ctx.fillRect(0,0,1920,1080);
  t+=0.01;
  requestAnimationFrame(draw);
}}
draw();

const LINES={json.dumps(SILENCE_LINES, ensure_ascii=False)};
const msgEl=document.getElementById('ma-brb-msg');
setInterval(()=>{{
  msgEl.style.opacity='0';
  setTimeout(()=>{{
    msgEl.textContent=LINES[Math.floor(Math.random()*LINES.length)];
    msgEl.style.opacity='1';
  }},600);
}},5500);
msgEl.style.transition='opacity 0.6s ease';
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

/* .ma- プレフィックス付き固有クラス群(紋様付き黒枠+刻印風の名前) */
.ma-lt-frame{{position:absolute;bottom:80px;left:80px;padding:20px 34px;background:rgba(4,0,0,0.72);border:1px solid rgba({rgb},0.5);box-shadow:inset 0 0 0 1px rgba({rgb},0.15),0 0 20px rgba({rgb},0.25);}}
.ma-lt-frame::before{{content:'';position:absolute;inset:6px;border:1px dashed rgba({rgb},0.25);pointer-events:none;}}
.ma-lt-name{{position:relative;font-size:32px;letter-spacing:4px;color:{color};text-shadow:0 0 2px #000,0 0 14px rgba({rgb},0.6);}}
.ma-lt-title{{position:absolute;left:80px;bottom:54px;font-size:11px;letter-spacing:5px;color:rgba({rgb},0.55);}}
</style>
</head>
<body>
<div class="ma-lt-frame">
  <span class="ma-lt-name" id="name-el">名前</span>
</div>
<div class="ma-lt-title" id="title-el">KYOUKAI</div>
<script>
const p=new URLSearchParams(window.location.search);
document.getElementById('name-el').textContent=p.get('name')||'名前';
document.getElementById('title-el').textContent=p.get('title')||'KYOUKAI';
</script>
</body>
</html>'''


SPEC = {
    "id": "ma",
    "name": "悪魔の間",
    "color": COLOR,
    "rgb": RGB,
    "bg": BG,
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "存在はここにある",
        "label": "存在 確認",
        "brb_main": "大魔将は沈黙しています",
    },
}
