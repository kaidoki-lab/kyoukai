#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 卵部屋(fukashitsu) 専用実装

デザイン指針(ROADMAP・方式B・画像同梱):
  waiting: 本体画像 static/images/fukashitsu/fukashitsu-room-9x16.png +
           卵部分に粒子の明滅(本体と同じパステル色設計)+計器3種(栄養/酸素/温度)
  brb: 卵の鼓動がゆっくり続く
  lower_third: 卵形の丸枠テロップ(淡いパステル)

一次データ:
  static/images/fukashitsu/fukashitsu-room-9x16.png(本体画像・asset_extract.copy_imageで同梱)
  static/fukashitsu.js のパステル色遷移(getColors): 栄養(赤)は[255,210→55,210→55]、
  酸素(青)は[210→55,225→148,255]、温度(黄)は[255,245→220,220→30]へ進捗に応じて変化する。
"""
import json
import sys as _sys
from pathlib import Path as _Path

_BOOTH_DIR = _Path(__file__).resolve().parent.parent
if str(_BOOTH_DIR) not in _sys.path:
    _sys.path.insert(0, str(_BOOTH_DIR))
import asset_extract  # noqa: E402

SPEC_ID = "fukashitsu"
NAME = "卵部屋"
COLOR = "#ffaacc"
RGB = "255,170,204"
BG = "#050003"

# static/fukashitsu.js のgetColors()を実読して踏襲する
_JS_SRC = asset_extract.read_source("static/fukashitsu.js")
_HAS_GET_COLORS = "getColors" in _JS_SRC

# パステル基準色(進捗50%地点の色として利用)
PASTEL_RED = [255, 132, 132]
PASTEL_BLUE = [132, 186, 255]
PASTEL_YELLOW = [255, 232, 125]

INSTRUMENT_LABELS = ["栄養", "酸素", "温度"]

BRB_LINES = [
    "卵を観察しています",
    "温度を維持中です",
    "栄養を補給しています",
    "孵化を待っています",
    "── もうすぐです",
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
        "static/images/fukashitsu/fukashitsu-room-9x16.png", SPEC_ID, assets_dir
    )
    _ASSET_REL_PATH = rel
    return rel


def waiting_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    img_rel = _asset_path()
    colors_js = json.dumps({"r": PASTEL_RED, "b": PASTEL_BLUE, "y": PASTEL_YELLOW})
    # 孵化装置ビュー: 中央に本体画像(縦長)+その上に卵型の粒子明滅レイヤー、
    # 左右に計器パネル3種を縦に並べる(栄養/酸素/温度)。
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 待機画面</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:'Courier New',monospace;color:{color};}}

/* .fks- プレフィックス付き固有クラス群(孵化装置ビュー: 中央画像+卵形粒子明滅+左右計器パネル) */
.fks-bg{{position:absolute;top:0;left:0;width:1920px;height:1080px;background-color:{bg};background-image:url('{img_rel}');background-repeat:no-repeat;background-position:center center;background-size:auto 1080px;z-index:1;}}
.fks-bg-fade-left{{position:absolute;top:0;left:0;width:30%;height:100%;background:linear-gradient(to right,{bg} 0%,rgba(0,0,0,0) 100%);z-index:2;}}
.fks-bg-fade-right{{position:absolute;top:0;right:0;width:30%;height:100%;background:linear-gradient(to left,{bg} 0%,rgba(0,0,0,0) 100%);z-index:2;}}
.fks-header{{position:absolute;top:44px;left:0;width:100%;text-align:center;font-size:13px;letter-spacing:8px;color:rgba({rgb},0.75);z-index:6;}}
.fks-egg-canvas{{position:absolute;left:50%;top:50%;width:520px;height:640px;margin:-320px 0 0 -260px;z-index:5;}}
.fks-panel{{position:absolute;top:220px;width:300px;padding:24px;background:rgba(10,0,6,0.5);border:1px solid rgba({rgb},0.3);border-radius:16px;z-index:6;}}
.fks-panel--left{{left:64px;}}
.fks-panel--right{{right:64px;}}
.fks-gauge{{margin-bottom:22px;}}
.fks-gauge:last-child{{margin-bottom:0;}}
.fks-gauge-label{{font-size:12px;letter-spacing:4px;margin-bottom:8px;opacity:0.8;}}
.fks-gauge-bar{{width:100%;height:14px;border-radius:7px;background:rgba(255,255,255,0.08);overflow:hidden;}}
.fks-gauge-fill{{height:100%;border-radius:7px;transition:width 0.6s ease;}}
.fks-caption{{position:absolute;bottom:56px;left:0;width:100%;text-align:center;font-size:14px;letter-spacing:5px;color:rgba({rgb},0.65);z-index:6;}}
</style>
</head>
<body>
<div class="fks-bg"></div>
<div class="fks-bg-fade-left"></div>
<div class="fks-bg-fade-right"></div>
<div class="fks-header">KYOUKAI // {NAME}</div>
<canvas class="fks-egg-canvas" id="fksEgg" width="260" height="320"></canvas>
<div class="fks-panel fks-panel--left">
  <div class="fks-gauge">
    <div class="fks-gauge-label">栄養</div>
    <div class="fks-gauge-bar"><div class="fks-gauge-fill" id="gauge-r" style="background:rgb({PASTEL_RED[0]},{PASTEL_RED[1]},{PASTEL_RED[2]});width:40%;"></div></div>
  </div>
  <div class="fks-gauge">
    <div class="fks-gauge-label">酸素</div>
    <div class="fks-gauge-bar"><div class="fks-gauge-fill" id="gauge-b" style="background:rgb({PASTEL_BLUE[0]},{PASTEL_BLUE[1]},{PASTEL_BLUE[2]});width:55%;"></div></div>
  </div>
</div>
<div class="fks-panel fks-panel--right">
  <div class="fks-gauge">
    <div class="fks-gauge-label">温度</div>
    <div class="fks-gauge-bar"><div class="fks-gauge-fill" id="gauge-y" style="background:rgb({PASTEL_YELLOW[0]},{PASTEL_YELLOW[1]},{PASTEL_YELLOW[2]});width:62%;"></div></div>
  </div>
  <div class="fks-gauge">
    <div class="fks-gauge-label">孵化予測</div>
    <div class="fks-gauge-bar"><div class="fks-gauge-fill" id="gauge-x" style="background:rgba({rgb},0.7);width:28%;"></div></div>
  </div>
</div>
<div class="fks-caption">孵化まで観測を継続します</div>
<script>
(function(){{
  var cv=document.getElementById('fksEgg');
  var ctx=cv.getContext('2d');
  var W=cv.width,H=cv.height;
  var cx=W*0.5,cy=H*0.5;
  var COLORS={colors_js};
  var N=140;
  var pts=[];
  function eggPoint(){{
    var a=Math.random()*Math.PI*2;
    var rx=W*0.36,ry=H*0.40;
    // 卵形: 下部を膨らませ上部をすぼめる
    var yShape=Math.sin(a)>=0?ry*1.12:ry*0.86;
    return {{
      x:cx+Math.cos(a)*rx*(0.3+Math.random()*0.7),
      y:cy+Math.sin(a)*yShape*(0.3+Math.random()*0.7)
    }};
  }}
  for(var i=0;i<N;i++){{
    var p=eggPoint();
    var f=i/N;
    var t=f<0.34?'r':f<0.67?'b':'y';
    pts.push({{x:p.x,y:p.y,t:t,phase:Math.random()*Math.PI*2,sz:1.6+Math.random()*1.8}});
  }}
  var t=0;
  function draw(){{
    t+=0.02;
    ctx.clearRect(0,0,W,H);
    // 卵の輪郭(淡いガイド)
    ctx.strokeStyle='rgba({rgb},0.18)';
    ctx.lineWidth=2;
    ctx.beginPath();
    ctx.ellipse(cx,cy,W*0.36,H*0.40,0,0,Math.PI*2);
    ctx.stroke();
    for(var i=0;i<pts.length;i++){{
      var p=pts[i];
      var glow=0.4+0.6*Math.abs(Math.sin(t+p.phase));
      var c=COLORS[p.t];
      ctx.globalAlpha=glow;
      ctx.fillStyle='rgb('+c[0]+','+c[1]+','+c[2]+')';
      ctx.beginPath();
      ctx.arc(p.x,p.y,p.sz,0,Math.PI*2);
      ctx.fill();
    }}
    ctx.globalAlpha=1;
    requestAnimationFrame(draw);
  }}
  draw();
}})();

// 計器ゲージがゆっくり揺れながら推移する(常時観測中を表現)
function jitterGauge(id,base){{
  var el=document.getElementById(id);
  if(!el)return;
  setInterval(function(){{
    var v=Math.max(15,Math.min(92,base+(Math.random()-0.5)*10));
    el.style.width=v+'%';
  }},2600);
}}
jitterGauge('gauge-r',40);
jitterGauge('gauge-b',55);
jitterGauge('gauge-y',62);
jitterGauge('gauge-x',28);
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

/* .fks- プレフィックス付き固有クラス群(waitingとは骨格が異なる: 中央の鼓動する卵1つのみのシンプル構図) */
.fks-brb-stage{{position:absolute;inset:0;width:1920px;height:1080px;display:flex;flex-direction:column;align-items:center;justify-content:center;}}
.fks-brb-egg{{width:280px;height:360px;border-radius:50% 50% 50% 50% / 58% 58% 42% 42%;background:radial-gradient(circle at 40% 32%,rgba({rgb},0.55),rgba({rgb},0.12) 70%);box-shadow:0 0 60px rgba({rgb},0.35);animation:fksHeartbeat 3.4s ease-in-out infinite;}}
@keyframes fksHeartbeat{{0%,100%{{transform:scale(1);}}45%{{transform:scale(1.05);}}55%{{transform:scale(0.99);}}}}
.fks-brb-msg{{margin-top:48px;font-size:26px;letter-spacing:5px;color:{color};text-shadow:0 0 16px rgba({rgb},0.5);min-height:36px;opacity:0.9;}}
.fks-brb-glow-canvas{{position:absolute;left:50%;top:50%;width:340px;height:420px;margin:-210px 0 0 -170px;z-index:2;pointer-events:none;}}
</style>
</head>
<body>
<div class="fks-brb-stage">
  <canvas class="fks-brb-glow-canvas" id="fksBrbGlow" width="340" height="420"></canvas>
  <div class="fks-brb-egg"></div>
  <div class="fks-brb-msg" id="fks-msg"></div>
</div>
<script>
const LINES={lines_js};
const msgEl=document.getElementById('fks-msg');
function showLine(){{
  msgEl.textContent=LINES[Math.floor(Math.random()*LINES.length)];
  msgEl.style.opacity='1';
  setTimeout(()=>{{msgEl.style.opacity='0';}},2600);
}}
msgEl.style.transition='opacity 0.6s ease';
setInterval(showLine,4400);

// 卵の鼓動に同期する淡いパステル明滅リング(本体の鼓動ギミックを支えるCanvas演出)
(function(){{
  const cv=document.getElementById('fksBrbGlow');
  const ctx=cv.getContext('2d');
  const W=cv.width,H=cv.height,cx=W/2,cy=H/2;
  let t=0;
  function draw(){{
    t+=0.02;
    ctx.clearRect(0,0,W,H);
    const pulse=0.5+0.5*Math.sin(t*1.05);
    ctx.strokeStyle='rgba({rgb},'+(0.15+pulse*0.25).toFixed(3)+')';
    ctx.lineWidth=3;
    ctx.beginPath();
    ctx.ellipse(cx,cy,150+pulse*14,190+pulse*16,0,0,Math.PI*2);
    ctx.stroke();
    requestAnimationFrame(draw);
  }}
  draw();
}})();
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

/* .fks- プレフィックス付き固有クラス群(卵形の丸枠テロップ、淡いパステル) */
.fks-lt-egg{{position:absolute;bottom:70px;left:80px;padding:22px 46px;border-radius:50% 50% 50% 50% / 65% 65% 35% 35%;background:linear-gradient(180deg,rgba({rgb},0.28),rgba({rgb},0.08));border:2px solid rgba({rgb},0.55);box-shadow:0 0 26px rgba({rgb},0.3);display:flex;align-items:center;}}
.fks-lt-name{{font-size:32px;letter-spacing:3px;color:rgba(255,255,255,0.95);}}
.fks-lt-title{{position:absolute;left:96px;bottom:44px;font-size:11px;letter-spacing:4px;color:rgba({rgb},0.7);}}
</style>
</head>
<body>
<div class="fks-lt-egg">
  <span class="fks-lt-name" id="name-el">名前</span>
</div>
<div class="fks-lt-title" id="title-el">KYOUKAI</div>
<script>
const p=new URLSearchParams(window.location.search);
document.getElementById('name-el').textContent=p.get('name')||'名前';
document.getElementById('title-el').textContent=p.get('title')||'KYOUKAI';
</script>
</body>
</html>'''


SPEC = {
    "id": "fukashitsu",
    "name": "卵部屋",
    "color": COLOR,
    "rgb": RGB,
    "bg": BG,
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "孵化まで観測を継続します",
        "label": "孵化 観測中",
        "brb_main": "卵を観察しています",
    },
}
