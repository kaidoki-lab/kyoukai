#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 台風ニュース(typhoon-news) 専用実装

デザイン指針(ROADMAP・方式B・画像同梱):
  waiting: 本体のニュース背景画像 typhoon-news/assets/typhoon-news-bg.png +
           速報帯+台風情報パネル(本体UI構成を移植)。情報帯の内側は暗くして
           待機画面として成立させる(配信画面が入る想起をさせない)。
  brb: 「放送は一時中断しています」お詫びテロップ+砂嵐(全部屋唯一のスタティック維持)
  lower_third: 報道テロップ形式(局ロゴ位置+2段帯)

一次データ:
  typhoon-news/assets/typhoon-news-bg.png(本体画像・asset_extract.copy_imageで同梱)
  typhoon-news/script.js のtyphoonPresets・速報帯構成(breaking-label/breaking-text/
  info-panel-layer/ticker-layer)をread_sourceで実読して踏襲する。
"""
import json
import sys as _sys
from pathlib import Path as _Path

_BOOTH_DIR = _Path(__file__).resolve().parent.parent
if str(_BOOTH_DIR) not in _sys.path:
    _sys.path.insert(0, str(_BOOTH_DIR))
import asset_extract  # noqa: E402

SPEC_ID = "typhoon-news"
NAME = "台風ニュース"
COLOR = "#ff0033"
RGB = "255,0,51"
BG = "#000010"

# typhoon-news/script.js のtyphoonPresetsを実読して踏襲する
_JS_SRC = asset_extract.read_source("typhoon-news/script.js")
_HAS_PRESETS = "typhoonPresets" in _JS_SRC

# 本体のtyphoonPresetsから代表1件を移植(waitingの情報パネルに使用)
PRESET = {
    "name": "後ほど連絡します",
    "number": "999",
    "pressure": 890,
    "wind": 65,
    "gust": 95,
    "direction": "北北西",
    "speed": 20,
    "ticker": "台風「後ほど連絡します」の影響で、全国的に荒天となる見込みです。気象庁は不要不急の返信を控えるよう呼びかけています。",
}

_PACK_ROOT = _BOOTH_DIR / "all-packs" / f"{NAME}_OBS素材パック"
_ASSET_REL_PATH = None


def _asset_path():
    """本体画像をこのパックのassets/へコピーし、相対パスを返す(初回のみ実行しキャッシュする)。"""
    global _ASSET_REL_PATH
    if _ASSET_REL_PATH is not None:
        return _ASSET_REL_PATH
    assets_dir = _PACK_ROOT / "01_waiting" / "assets"
    rel = asset_extract.copy_image(
        "typhoon-news/assets/typhoon-news-bg.png", SPEC_ID, assets_dir
    )
    _ASSET_REL_PATH = rel
    return rel


def waiting_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    img_rel = _asset_path()
    preset_js = json.dumps(PRESET, ensure_ascii=False)
    # L字レイアウト: 上部に速報帯、右に台風情報パネル、下部に速報テロップ帯。
    # 情報帯・速報帯の内側は暗くして「待機画面」として成立させる(配信画面ではない)。
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 待機画面</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:'Courier New',monospace;color:#fff;}}

/* .tpn- プレフィックス付き固有クラス群(速報帯+情報パネルのL字ニュース画面) */
.tpn-bg{{position:absolute;top:0;left:0;width:1920px;height:1080px;background-color:{bg};background-image:url('{img_rel}');background-repeat:no-repeat;background-position:center center;background-size:cover;z-index:1;}}
.tpn-bg-dim{{position:absolute;top:0;left:0;width:1920px;height:1080px;background:rgba(0,0,4,0.62);z-index:2;}}
.tpn-breaking{{position:absolute;top:0;left:0;width:1920px;display:flex;align-items:center;z-index:6;background:rgba(0,0,0,0.55);border-bottom:3px solid {color};}}
.tpn-breaking-label{{background:{color};color:#fff;font-size:24px;font-weight:bold;letter-spacing:6px;padding:18px 34px;}}
.tpn-breaking-text{{padding:18px 30px;font-size:26px;letter-spacing:2px;}}
.tpn-breaking-text b{{color:{color};}}
.tpn-panel{{position:absolute;top:150px;right:64px;width:460px;padding:30px 34px;background:rgba(4,0,2,0.72);border:1px solid rgba({rgb},0.4);border-radius:6px;z-index:6;}}
.tpn-panel-kicker{{font-size:12px;letter-spacing:4px;color:rgba({rgb},0.8);margin-bottom:10px;}}
.tpn-panel-title{{font-size:24px;margin-bottom:20px;letter-spacing:1px;}}
.tpn-panel dl{{display:grid;grid-template-columns:1fr auto;row-gap:14px;font-size:15px;}}
.tpn-panel dt{{opacity:0.65;letter-spacing:2px;}}
.tpn-panel dd{{text-align:right;font-size:18px;}}
.tpn-eye-title{{position:absolute;left:64px;top:220px;font-size:56px;font-weight:bold;letter-spacing:4px;line-height:1.3;text-shadow:0 4px 18px rgba(0,0,0,0.8);z-index:6;}}
.tpn-eye-title span{{display:block;}}
.tpn-caption{{position:absolute;bottom:150px;left:0;width:1920px;text-align:center;font-size:22px;letter-spacing:3px;z-index:6;background:rgba({rgb},0.14);padding:14px 0;}}
.tpn-ticker{{position:absolute;bottom:0;left:0;width:1920px;height:80px;background:{color};display:flex;align-items:center;overflow:hidden;z-index:6;}}
.tpn-ticker-track{{white-space:nowrap;font-size:24px;letter-spacing:1px;color:#fff;padding-left:1920px;animation:tpnScroll 24s linear infinite;}}
@keyframes tpnScroll{{0%{{transform:translateX(0);}}100%{{transform:translateX(-100%);}}}}
.tpn-rain-canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:3;pointer-events:none;}}
</style>
</head>
<body>
<div class="tpn-bg"></div>
<div class="tpn-bg-dim"></div>
<canvas class="tpn-rain-canvas" id="tpnRain"></canvas>
<header class="tpn-breaking">
  <div class="tpn-breaking-label">速報</div>
  <div class="tpn-breaking-text">大型で非常に強い台風「<b id="tpn-name">後ほど連絡します</b>」が接近中</div>
</header>
<div class="tpn-eye-title"><span id="tpn-eye1">後ほど</span><span id="tpn-eye2">連絡します</span></div>
<aside class="tpn-panel">
  <div class="tpn-panel-kicker">台風情報</div>
  <div class="tpn-panel-title">台風「<span id="tpn-name2">後ほど連絡します</span>」</div>
  <dl>
    <div><dt>台風番号</dt><dd>第<span id="tpn-number">999</span>号</dd></div>
    <div><dt>中心気圧</dt><dd><span id="tpn-pressure">890</span> hPa</dd></div>
    <div><dt>最大風速</dt><dd><span id="tpn-wind">65</span> m/s</dd></div>
    <div><dt>最大瞬間風速</dt><dd><span id="tpn-gust">95</span> m/s</dd></div>
    <div><dt>進行方向</dt><dd id="tpn-direction">北北西</dd></div>
    <div><dt>速度</dt><dd><span id="tpn-speed">20</span> km/h</dd></div>
  </dl>
</aside>
<div class="tpn-caption">待機中 ── まもなく配信を再開します</div>
<footer class="tpn-ticker">
  <div class="tpn-ticker-track" id="tpn-ticker-track"></div>
</footer>
<script>
const PRESET={preset_js};
document.getElementById('tpn-name').textContent=PRESET.name;
document.getElementById('tpn-name2').textContent=PRESET.name;
document.getElementById('tpn-number').textContent=PRESET.number;
document.getElementById('tpn-pressure').textContent=PRESET.pressure;
document.getElementById('tpn-wind').textContent=PRESET.wind;
document.getElementById('tpn-gust').textContent=PRESET.gust;
document.getElementById('tpn-direction').textContent=PRESET.direction;
document.getElementById('tpn-speed').textContent=PRESET.speed;
document.getElementById('tpn-ticker-track').textContent=PRESET.ticker+'\\u3000'+PRESET.ticker;

// 目玉タイトルの改行分割(本体splitNameForEye相当の簡略移植)
function splitName(name){{
  if(name.length<=5)return [name,''];
  const mid=Math.ceil(name.length/2);
  return [name.slice(0,mid),name.slice(mid)];
}}
const parts=splitName(PRESET.name);
document.getElementById('tpn-eye1').textContent=parts[0];
document.getElementById('tpn-eye2').textContent=parts[1];

// 荒天を示す薄い雨筋レイヤー(待機画面としての質感補強、砂嵐のような全画素書き換えではない)
(function(){{
  const cv=document.getElementById('tpnRain');
  const ctx=cv.getContext('2d');
  const W=1920,H=1080;
  cv.width=W;cv.height=H;
  const N=90;
  const drops=[];
  for(let i=0;i<N;i++){{
    drops.push({{x:Math.random()*W,y:Math.random()*H,len:20+Math.random()*30,speed:14+Math.random()*10}});
  }}
  function draw(){{
    ctx.clearRect(0,0,W,H);
    ctx.strokeStyle='rgba(200,210,255,0.18)';
    ctx.lineWidth=1.5;
    for(let i=0;i<drops.length;i++){{
      const d=drops[i];
      ctx.beginPath();
      ctx.moveTo(d.x,d.y);
      ctx.lineTo(d.x-4,d.y+d.len);
      ctx.stroke();
      d.y+=d.speed;
      d.x-=1.2;
      if(d.y>H){{d.y=-d.len;d.x=Math.random()*W;}}
    }}
    requestAnimationFrame(draw);
  }}
  draw();
}})();
</script>
</body>
</html>'''


def brb_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    # 唯一のスタティック(砂嵐)を専用実装として書き直す。ImageData全画素更新はこの部屋のbrbのみ許可。
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 放送中断</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:#000;overflow:hidden;font-family:'Courier New',monospace;color:#fff;}}

/* .tpn- プレフィックス付き固有クラス群(waitingとは骨格が異なる: 砂嵐+お詫びテロップの放送事故構図) */
canvas.tpn-static{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:1;}}
.tpn-brb-overlay{{position:absolute;inset:0;width:1920px;height:1080px;z-index:5;display:flex;flex-direction:column;align-items:center;justify-content:center;background:rgba(0,0,0,0.35);}}
.tpn-brb-bars{{width:100%;height:120px;background:repeating-linear-gradient(90deg,#fff 0 8%,#ffcc00 8% 16%,#00aaff 16% 24%,#ff0033 24% 32%,#000 32% 40%,#00cc55 40% 48%,#fff 48% 56%,#ffcc00 56% 64%,#00aaff 64% 72%,#ff0033 72% 80%,#000 80% 88%,#00cc55 88% 100%);opacity:0.18;margin-bottom:40px;}}
.tpn-brb-msg{{font-size:34px;letter-spacing:6px;background:rgba(0,0,0,0.7);padding:24px 48px;border:2px solid {color};}}
.tpn-brb-sub{{margin-top:22px;font-size:16px;letter-spacing:4px;color:rgba({rgb},0.8);}}
</style>
</head>
<body>
<canvas class="tpn-static" id="tpnStatic"></canvas>
<div class="tpn-brb-overlay">
  <div class="tpn-brb-bars"></div>
  <div class="tpn-brb-msg">放送は一時中断しています</div>
  <div class="tpn-brb-sub">しばらくお待ちください ── 台風情報は後ほど更新します</div>
</div>
<script>
// 砂嵐(ImageData全画素更新): 台風ニュースbrbのみ許可される唯一のスタティック演出
const cv=document.getElementById('tpnStatic');
const ctx=cv.getContext('2d');
const W=480,H=270; // 内部解像度を落として拡大表示(パフォーマンス確保)
cv.width=W;cv.height=H;
cv.style.imageRendering='pixelated';
const imgData=ctx.createImageData(W,H);
function drawStatic(){{
  const buf=imgData.data;
  for(let i=0;i<buf.length;i+=4){{
    const v=(Math.random()*255)|0;
    buf[i]=v;buf[i+1]=v;buf[i+2]=v;buf[i+3]=255;
  }}
  ctx.putImageData(imgData,0,0);
  requestAnimationFrame(drawStatic);
}}
drawStatic();
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

/* .tpn- プレフィックス付き固有クラス群(報道テロップ形式: 局ロゴ位置+2段帯) */
.tpn-lt-wrap{{position:absolute;bottom:70px;left:0;width:1920px;}}
.tpn-lt-row1{{display:flex;align-items:stretch;}}
.tpn-lt-logo{{width:80px;background:{color};display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:bold;letter-spacing:2px;color:#fff;}}
.tpn-lt-name{{flex:1;background:rgba(0,0,0,0.82);padding:16px 30px;font-size:32px;letter-spacing:3px;color:#fff;}}
.tpn-lt-row2{{background:rgba({rgb},0.85);padding:8px 30px 8px 110px;font-size:14px;letter-spacing:4px;color:#fff;}}
</style>
</head>
<body>
<div class="tpn-lt-wrap">
  <div class="tpn-lt-row1">
    <div class="tpn-lt-logo">KYK</div>
    <div class="tpn-lt-name" id="name-el">名前</div>
  </div>
  <div class="tpn-lt-row2" id="title-el">LIVE</div>
</div>
<script>
const p=new URLSearchParams(window.location.search);
document.getElementById('name-el').textContent=p.get('name')||'名前';
document.getElementById('title-el').textContent=p.get('title')||'LIVE';
</script>
</body>
</html>'''


SPEC = {
    "id": "typhoon-news",
    "name": "台風ニュース",
    "color": COLOR,
    "rgb": RGB,
    "bg": BG,
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "続報をお待ちください",
        "label": "速報 送信中",
        "brb_main": "速報を準備しています",
    },
}
