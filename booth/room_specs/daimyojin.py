#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: AI大明神(daimyojin) 専用実装

デザイン指針(ROADMAP・方式B・画像同梱):
  waiting: 本体画像 static/images/daimyojin/daimyojin_pc.webp +祈願札の発光
  brb: おみくじ筒が回り「祈願 処理中」の札が揺れる
  lower_third: 神社の木札(絵馬)型テロップ(CSS border-radius+疑似要素の紐)

一次データ:
  static/images/daimyojin/daimyojin_pc.webp(本体画像・asset_extract.copy_imageで同梱)
  templates/daimyojin.html の祈願UI(文言・演出言語)

reviewer指摘対応(2026-07-09): 管理人室と同一テンプレートの色違いになっていたため、
「祈願処理装置」らしい画面へ再設計する。waitingは中央画像を避け右寄せ配置とし、
祈願札が縦にスクロールして流れ落ちる処理ログ+左側に回路グリッド+大きな祈願番号の
明滅表示という装置然としたレイアウトにする。brbはおみくじ筒回転をやめ、
円環プログレスリングが回転する「処理中」表現に変更(揺れアニメは管理人室側に譲る)。
"""
import json
import sys as _sys
from pathlib import Path as _Path

_BOOTH_DIR = _Path(__file__).resolve().parent.parent
if str(_BOOTH_DIR) not in _sys.path:
    _sys.path.insert(0, str(_BOOTH_DIR))
import asset_extract  # noqa: E402
import pack_base  # noqa: E402

SPEC_ID = "daimyojin"
NAME = "AI大明神"
COLOR = "#ffcc00"
RGB = "255,204,0"
BG = "#040200"

PRAYER_FRAGMENTS = [
    "願いを受信", "処理中 ──", "判定 保留", "観測結果 出力",
    "奉納 確認", "AI神託", "祈願 記録済み", "応答 生成中",
    "観測 完了", "次の祈願へ",
]

BRB_LINES = [
    "祈願を処理しています",
    "AI神託を生成中",
    "奉納データを参照中",
    "願いを観測しています",
    "処理が完了していません",
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
        "static/images/daimyojin/daimyojin_pc.webp", SPEC_ID, assets_dir
    )
    _ASSET_REL_PATH = rel
    return rel


def waiting_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    img_rel = _asset_path()
    fragments_js = json.dumps(PRAYER_FRAGMENTS, ensure_ascii=False)
    # 装置画面のレイアウト: 右側に本体画像(画面全体ではなく右38%に寄せる)、
    # 左側に回路グリッド+縦流れ祈願札ログ+巨大祈願番号という「処理装置のコンソール」構成。
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 待機画面</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:'Courier New',monospace;color:{color};}}

/* .dmj- プレフィックス付き固有クラス群(祈願処理装置のコンソール構成: 左=処理パネル/右=本体画像) */
.dmj-console-grid{{position:absolute;top:0;left:0;width:62%;height:100%;background-image:linear-gradient(rgba({rgb},0.08) 1px,transparent 1px),linear-gradient(90deg,rgba({rgb},0.08) 1px,transparent 1px);background-size:48px 48px;z-index:1;}}
.dmj-portrait{{position:absolute;top:0;right:0;width:38%;height:100%;background-image:url('{img_rel}');background-size:cover;background-position:center center;background-repeat:no-repeat;z-index:2;}}
.dmj-portrait-edge{{position:absolute;top:0;right:38%;width:180px;height:100%;background:linear-gradient(90deg,{bg} 0%,rgba(0,0,0,0) 100%);z-index:3;}}
.dmj-header{{position:absolute;top:44px;left:60px;font-size:13px;letter-spacing:9px;color:rgba({rgb},0.6);z-index:6;text-transform:uppercase;}}
.dmj-shingou{{position:absolute;top:120px;left:60px;font-size:120px;font-weight:bold;letter-spacing:6px;color:{color};text-shadow:0 0 24px rgba({rgb},0.6);z-index:6;line-height:1;}}
.dmj-shingou-caption{{position:absolute;top:250px;left:64px;font-size:12px;letter-spacing:4px;color:rgba({rgb},0.5);z-index:6;}}
.dmj-scroll-window{{position:absolute;top:340px;left:60px;width:900px;height:560px;overflow:hidden;border-top:1px solid rgba({rgb},0.35);border-bottom:1px solid rgba({rgb},0.35);z-index:6;}}
.dmj-scroll-track{{position:absolute;top:0;left:0;width:100%;}}
.dmj-scroll-item{{padding:14px 4px;font-size:17px;letter-spacing:3px;color:rgba({rgb},0.7);border-bottom:1px dashed rgba({rgb},0.15);}}
.dmj-scroll-item.is-active{{color:{color};text-shadow:0 0 10px rgba({rgb},0.5);}}
canvas.dmj-scan-canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:5;pointer-events:none;mix-blend-mode:screen;}}
</style>
</head>
<body>
<div class="dmj-console-grid"></div>
<div class="dmj-portrait"></div>
<div class="dmj-portrait-edge"></div>
<canvas class="dmj-scan-canvas" id="dmj-scan"></canvas>
<div class="dmj-header">KYOUKAI // {NAME} // 処理コンソール</div>
<div class="dmj-shingou" id="dmj-shingou">0001</div>
<div class="dmj-shingou-caption">祈願番号</div>
<div class="dmj-scroll-window">
  <div class="dmj-scroll-track" id="dmj-track"></div>
</div>
<script>
// 縦スキャンライン(装置の走査光)
const scanCanvas=document.getElementById('dmj-scan');
const scanCtx=scanCanvas.getContext('2d');
scanCanvas.width=1920;scanCanvas.height=1080;
let scanY=0;
function drawScan(){{
  scanCtx.clearRect(0,0,1920,1080);
  const grad=scanCtx.createLinearGradient(0,scanY-60,0,scanY+60);
  grad.addColorStop(0,'rgba({rgb},0)');
  grad.addColorStop(0.5,'rgba({rgb},0.10)');
  grad.addColorStop(1,'rgba({rgb},0)');
  scanCtx.fillStyle=grad;
  scanCtx.fillRect(0,scanY-60,1200,120);
  scanY=(scanY+2)%1200;
  requestAnimationFrame(drawScan);
}}
drawScan();

// 祈願番号の明滅カウントアップ
const shingouEl=document.getElementById('dmj-shingou');
let shingouN=1;
setInterval(()=>{{
  shingouN+=1;
  shingouEl.textContent=String(shingouN).padStart(4,'0');
  shingouEl.style.opacity='0.3';
  setTimeout(()=>{{shingouEl.style.opacity='1';}},120);
}},2400);
shingouEl.style.transition='opacity 0.15s ease';

// 祈願ログが縦にスクロールして流れ落ちる処理ウィンドウ
const FRAGMENTS={fragments_js};
const track=document.getElementById('dmj-track');
const ITEM_H=48;
const VISIBLE=12;
function buildInitial(){{
  for(let i=0;i<VISIBLE+2;i++){{
    const div=document.createElement('div');
    div.className='dmj-scroll-item';
    div.textContent=FRAGMENTS[Math.floor(Math.random()*FRAGMENTS.length)];
    track.appendChild(div);
  }}
}}
buildInitial();
let offset=0;
function tick(){{
  offset+=1;
  track.style.transform='translateY(-'+offset+'px)';
  if(offset>=ITEM_H){{
    offset=0;
    track.removeChild(track.firstElementChild);
    const div=document.createElement('div');
    div.className='dmj-scroll-item';
    div.textContent=FRAGMENTS[Math.floor(Math.random()*FRAGMENTS.length)];
    track.appendChild(div);
    track.style.transform='translateY(0)';
  }}
  const items=track.querySelectorAll('.dmj-scroll-item');
  items.forEach((el,i)=>el.classList.toggle('is-active',i===Math.floor(VISIBLE/2)));
  requestAnimationFrame(tick);
}}
tick();
</script>
</body>
</html>'''


def brb_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    lines_js = json.dumps(BRB_LINES, ensure_ascii=False)
    # brb: おみくじ筒回転+札揺れをやめ、円環プログレスリングが回転する
    # 「装置が演算し続けている」構図に変更(揺れ演出は管理人室側のみで使用)。
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 離席中</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:'Courier New',monospace;color:{color};}}

/* .dmj- プレフィックス付き固有クラス群(waitingとも異なる構図: 円環プログレスリングが回転する処理待機画面) */
.dmj-brb-stage{{position:absolute;inset:0;width:1920px;height:1080px;z-index:10;display:flex;flex-direction:column;align-items:center;justify-content:center;}}
.dmj-ring-wrap{{position:relative;width:420px;height:420px;}}
.dmj-ring{{position:absolute;inset:0;border-radius:50%;border:6px solid transparent;border-top-color:rgba({rgb},0.85);border-right-color:rgba({rgb},0.35);animation:dmjRingSpin 2.2s linear infinite;}}
.dmj-ring--inner{{inset:60px;border-width:3px;border-top-color:rgba({rgb},0.5);border-left-color:rgba({rgb},0.2);animation-duration:3.4s;animation-direction:reverse;}}
@keyframes dmjRingSpin{{0%{{transform:rotate(0deg);}}100%{{transform:rotate(360deg);}}}}
.dmj-ring-center{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:34px;letter-spacing:5px;color:{color};text-shadow:0 0 18px rgba({rgb},0.6);}}
.dmj-brb-caption{{margin-top:48px;font-size:16px;letter-spacing:8px;color:rgba({rgb},0.6);text-transform:uppercase;}}
.dmj-brb-msg{{margin-top:20px;font-size:22px;letter-spacing:4px;color:{color};text-shadow:0 0 14px rgba({rgb},0.5);min-height:32px;opacity:0.85;}}
canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:1;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="dmj-brb-stage">
  <div class="dmj-ring-wrap">
    <div class="dmj-ring"></div>
    <div class="dmj-ring dmj-ring--inner"></div>
    <div class="dmj-ring-center">祈願</div>
  </div>
  <div class="dmj-brb-caption">PROCESSING</div>
  <div class="dmj-brb-msg" id="dmj-msg"></div>
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

const LINES={lines_js};
const msgEl=document.getElementById('dmj-msg');
function showLine(){{
  msgEl.textContent=LINES[Math.floor(Math.random()*LINES.length)];
  msgEl.style.opacity='1';
  setTimeout(()=>{{msgEl.style.opacity='0';}},2200);
}}
msgEl.style.transition='opacity 0.5s ease';
setInterval(showLine,3800);
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

/* .dmj- プレフィックス付き固有クラス群(絵馬型テロップ: 五角形+紐) */
.dmj-ema{{position:absolute;bottom:80px;left:80px;width:420px;padding:22px 28px 26px;background:linear-gradient(180deg,#fdf6df 0%,#f4e6b8 100%);border:3px solid rgba({rgb},0.6);clip-path:polygon(0 14%,50% 0,100% 14%,100% 100%,0 100%);box-shadow:0 0 24px rgba({rgb},0.4);}}
.dmj-ema::before{{content:'';position:absolute;top:-40px;left:50%;width:3px;height:40px;margin-left:-1.5px;background:linear-gradient(180deg,rgba({rgb},0.7),rgba({rgb},0.15));}}
.dmj-ema-title{{font-size:12px;letter-spacing:5px;color:#8a5a10;margin-bottom:8px;text-align:center;}}
.dmj-ema-name{{font-size:32px;letter-spacing:3px;color:#5a1a10;font-family:'Yu Mincho','Hiragino Mincho ProN',serif;text-align:center;}}
</style>
</head>
<body>
<div class="dmj-ema">
  <div class="dmj-ema-title" id="title-el">KYOUKAI</div>
  <div class="dmj-ema-name" id="name-el">名前</div>
</div>
<script>
const p=new URLSearchParams(window.location.search);
document.getElementById('name-el').textContent=p.get('name')||'名前';
document.getElementById('title-el').textContent=p.get('title')||'KYOUKAI';
</script>
</body>
</html>'''


SPEC = {
    "id": "daimyojin",
    "name": "AI大明神",
    "color": COLOR,
    "rgb": RGB,
    "bg": BG,
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "願いは観測されています",
        "label": "祈願 処理中",
        "brb_main": "祈願を処理しています",
    },
}
