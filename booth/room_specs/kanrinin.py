#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 管理人室(kanrinin) 専用実装

デザイン指針(ROADMAP・方式B・画像同梱):
  waiting: 受付カウンターの本体画像+呼び鈴・鍵ボックスの発光ポイント
  brb: 「席を外しています」札が揺れる+目玉がうっすら透ける演出(本体ギミック踏襲)
  lower_third: 宿帳/ネームプレート風(真鍮質感=グラデーション+内側シャドウ)

一次データ:
  static/images/kanrinin/kanrinin-room-9x16.png(本体画像・asset_extract.copy_imageで同梱)
  static/kanrinin.css の領域定義(.red-phone-area = 呼び鈴, .kanrinin-eye-gap = 目玉の覗き穴)

reviewer指摘対応(2026-07-09): AI大明神と同一テンプレートの色違いになっていたため、
「受付窓口」らしい画面へ再設計する。上部に本体画像(帯状)、下部にフロントカウンター
UI(宿帳ページがめくれる+鍵ボックスの格子グリッド+呼び鈴カウンター)という
受付デスク視点の構成にする。brbは揺れる立て札演出をこの部屋に残し、
目玉の透けはCanvasベースのvignette明滅として差別化する。
"""
import json
import sys as _sys
from pathlib import Path as _Path

_BOOTH_DIR = _Path(__file__).resolve().parent.parent
if str(_BOOTH_DIR) not in _sys.path:
    _sys.path.insert(0, str(_BOOTH_DIR))
import asset_extract  # noqa: E402

SPEC_ID = "kanrinin"
NAME = "管理人室"
COLOR = "#aa8855"
RGB = "170,136,85"
BG = "#050300"

DIARY_LINES = [
    "── 本日、来訪者なし",
    "呼び鈴 3回 応答なし",
    "鍵ボックス 施錠確認済み",
    "BOOTH荷物 受領済み",
    "消滅の鍵 保管中",
    "目玉 異常なし",
    "賽銭箱 確認済み",
    "── いらっしゃい、と書きかけてやめた",
]

KEY_SLOT_COUNT = 12

BRB_LINES = [
    "管理人を呼んでいます",
    "呼び鈴を鳴らしています",
    "管理人は席を外しています",
    "日誌を確認中です",
    "しばらくお待ちください",
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
        "static/images/kanrinin/kanrinin-room-9x16.png", SPEC_ID, assets_dir
    )
    _ASSET_REL_PATH = rel
    return rel


def waiting_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    img_rel = _asset_path()
    diary_js = json.dumps(DIARY_LINES, ensure_ascii=False)
    key_slots = ''.join(
        f'<div class="kan-keyslot" data-slot="{i}"></div>' for i in range(KEY_SLOT_COUNT)
    )
    # 受付フロント構成: 上部38%を本体画像の帯にし、下部62%をカウンターデスク
    # (宿帳ページ+鍵ボックス格子+呼び鈴カウンター)に割く。
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 待機画面</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:'Courier New',monospace;color:{color};}}

/* .kan- プレフィックス付き固有クラス群(受付フロント構成: 上部=室内帯画像/下部=カウンターデスク) */
.kan-photo-band{{position:absolute;top:0;left:0;width:1920px;height:412px;background-image:url('{img_rel}');background-size:cover;background-position:center 20%;background-repeat:no-repeat;z-index:1;}}
.kan-photo-fade{{position:absolute;top:320px;left:0;width:1920px;height:92px;background:linear-gradient(180deg,rgba(0,0,0,0) 0%,{bg} 100%);z-index:2;}}
.kan-header{{position:absolute;top:36px;left:60px;font-size:13px;letter-spacing:9px;color:rgba({rgb},0.75);z-index:6;text-transform:uppercase;text-shadow:0 2px 6px rgba(0,0,0,0.8);}}
.kan-desk{{position:absolute;top:412px;left:0;width:1920px;height:668px;background:linear-gradient(180deg,#0e0906,#050300);border-top:2px solid rgba({rgb},0.4);z-index:3;display:flex;}}
.kan-diary-pane{{width:900px;height:100%;padding:56px 60px;position:relative;border-right:1px solid rgba({rgb},0.25);}}
.kan-diary-page{{background:linear-gradient(180deg,#e4d2aa,#d9c491);color:#241705;padding:36px 40px;min-height:420px;box-shadow:0 10px 30px rgba(0,0,0,0.5);font-family:'Yu Mincho','Hiragino Mincho ProN',serif;}}
.kan-diary-title{{font-size:14px;letter-spacing:4px;opacity:0.7;margin-bottom:18px;}}
.kan-diary-line{{font-size:20px;line-height:2.1;min-height:44px;}}
.kan-keybox-pane{{width:520px;height:100%;padding:56px 40px;}}
.kan-keybox-title{{font-size:12px;letter-spacing:4px;color:rgba({rgb},0.6);margin-bottom:18px;}}
.kan-keybox-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;width:440px;}}
.kan-keyslot{{width:96px;height:60px;background:linear-gradient(180deg,rgba({rgb},0.14),rgba({rgb},0.04));border:1px solid rgba({rgb},0.4);position:relative;}}
.kan-keyslot::after{{content:'';position:absolute;top:50%;left:50%;width:6px;height:6px;margin:-3px 0 0 -3px;border-radius:50%;background:rgba({rgb},0.5);}}
.kan-keyslot.is-lit::after{{background:#ffcc55;box-shadow:0 0 10px rgba(255,204,85,0.9);}}
.kan-bell-pane{{width:500px;height:100%;padding:56px 40px;border-left:1px solid rgba({rgb},0.25);}}
.kan-bell-title{{font-size:12px;letter-spacing:4px;color:rgba({rgb},0.6);margin-bottom:18px;}}
.kan-bell-icon{{width:88px;height:88px;margin:0 auto 20px;border-radius:50%;background:radial-gradient(circle,rgba(255,60,40,0.85),rgba(120,10,0,0.15));box-shadow:0 0 24px rgba(255,60,40,0.5);animation:kanBellIdle 2.6s ease-in-out infinite;}}
@keyframes kanBellIdle{{0%,100%{{opacity:0.5;}}50%{{opacity:0.9;}}}}
.kan-bell-counter{{text-align:center;font-size:38px;letter-spacing:3px;color:{color};}}
.kan-bell-counter-label{{text-align:center;font-size:11px;letter-spacing:3px;color:rgba({rgb},0.55);margin-top:8px;}}
canvas.kan-dust-canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:5;pointer-events:none;}}
</style>
</head>
<body>
<div class="kan-photo-band"></div>
<div class="kan-photo-fade"></div>
<canvas class="kan-dust-canvas" id="kan-dust"></canvas>
<div class="kan-header">RECEPTION DESK</div>
<div class="kan-desk">
  <div class="kan-diary-pane">
    <div class="kan-diary-page">
      <div class="kan-diary-title">管理日誌</div>
      <div class="kan-diary-line" id="kan-diary-line">── 本日、来訪者なし</div>
    </div>
  </div>
  <div class="kan-keybox-pane">
    <div class="kan-keybox-title">鍵ボックス</div>
    <div class="kan-keybox-grid" id="kan-keybox">{key_slots}</div>
  </div>
  <div class="kan-bell-pane">
    <div class="kan-bell-title">呼び鈴</div>
    <div class="kan-bell-icon"></div>
    <div class="kan-bell-counter" id="kan-bell-count">000</div>
    <div class="kan-bell-counter-label">応答なし回数</div>
  </div>
</div>
<script>
// 天井から差し込む微細な埃(受付の静けさを表現するCanvas演出)
const dustCanvas=document.getElementById('kan-dust');
const dustCtx=dustCanvas.getContext('2d');
dustCanvas.width=1920;dustCanvas.height=1080;
let dust=Array.from({{length:36}},()=>({{x:Math.random()*1920,y:Math.random()*412,vy:0.15+Math.random()*0.3,r:1+Math.random()*1.5}}));
function drawDust(){{
  dustCtx.clearRect(0,0,1920,1080);
  dustCtx.fillStyle='rgba(255,240,210,0.5)';
  dust.forEach(d=>{{
    d.y+=d.vy;
    if(d.y>412){{d.y=0;d.x=Math.random()*1920;}}
    dustCtx.beginPath();
    dustCtx.arc(d.x,d.y,d.r,0,Math.PI*2);
    dustCtx.fill();
  }});
  requestAnimationFrame(drawDust);
}}
drawDust();

// 宿帳ページの1行がめくれるように差し替わる
const DIARY={diary_js};
const diaryEl=document.getElementById('kan-diary-line');
function nextDiaryLine(){{
  diaryEl.style.transform='rotateX(90deg)';
  setTimeout(()=>{{
    diaryEl.textContent=DIARY[Math.floor(Math.random()*DIARY.length)];
    diaryEl.style.transform='rotateX(0deg)';
  }},260);
}}
diaryEl.style.transition='transform 0.26s ease';
diaryEl.style.transformOrigin='top center';
setInterval(nextDiaryLine,3200);

// 鍵ボックスの格子が1マスずつランダムに点灯する
const slots=document.querySelectorAll('.kan-keyslot');
function litRandomSlot(){{
  slots.forEach(s=>s.classList.remove('is-lit'));
  const idx=Math.floor(Math.random()*slots.length);
  slots[idx].classList.add('is-lit');
}}
setInterval(litRandomSlot,1400);
litRandomSlot();

// 呼び鈴の応答なしカウンターが増え続ける
const bellCountEl=document.getElementById('kan-bell-count');
let bellCount=0;
setInterval(()=>{{
  bellCount+=1;
  bellCountEl.textContent=String(bellCount).padStart(3,'0');
}},2600);
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

/* .kan- プレフィックス付き固有クラス群(waitingとは骨格が異なる: 揺れる立て札+vignette明滅の目玉) */
.kan-brb-stage{{position:absolute;inset:0;width:1920px;height:1080px;z-index:10;display:flex;flex-direction:column;align-items:center;justify-content:center;}}
.kan-brb-sign{{padding:20px 44px;background:linear-gradient(180deg,#2a1c0e,#140c04);border:2px solid rgba({rgb},0.6);color:{color};font-size:28px;letter-spacing:6px;box-shadow:0 0 30px rgba({rgb},0.3);animation:kanSignSway 3.2s ease-in-out infinite;transform-origin:top center;}}
@keyframes kanSignSway{{0%,100%{{transform:rotate(-2.5deg);}}50%{{transform:rotate(2.5deg);}}}}
.kan-brb-msg{{margin-top:36px;font-size:20px;letter-spacing:4px;color:{color};text-shadow:0 0 14px rgba({rgb},0.5);min-height:32px;opacity:0.85;}}
canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;}}
canvas#kan-brb-bg{{z-index:1;}}
canvas#kan-brb-eye{{z-index:9;pointer-events:none;}}
</style>
</head>
<body>
<canvas id="kan-brb-bg"></canvas>
<canvas id="kan-brb-eye"></canvas>
<div class="kan-brb-stage">
  <div class="kan-brb-sign">席を外しています</div>
  <div class="kan-brb-msg" id="kan-msg"></div>
</div>
<script>
const bgCanvas=document.getElementById('kan-brb-bg');
const bgCtx=bgCanvas.getContext('2d');
bgCanvas.width=1920;bgCanvas.height=1080;
function draw(){{
  bgCtx.clearRect(0,0,1920,1080);
  bgCtx.fillStyle='rgba({rgb},0.02)';
  bgCtx.fillRect(0,0,1920,1080);
  requestAnimationFrame(draw);
}}
draw();

// 目玉がvignette状にうっすら透ける明滅(本体kanrinin.cssの.kanrinin-eye-gapギミックを踏襲)
const eyeCanvas=document.getElementById('kan-brb-eye');
const eyeCtx=eyeCanvas.getContext('2d');
eyeCanvas.width=1920;eyeCanvas.height=1080;
let eyeT=0;
function drawEye(){{
  eyeCtx.clearRect(0,0,1920,1080);
  const cycle=(eyeT%320)/320;
  const reveal=cycle>0.82?(cycle-0.82)/0.18:0;
  if(reveal>0){{
    const grad=eyeCtx.createRadialGradient(960,420,10,960,420,140);
    grad.addColorStop(0,'rgba({rgb},'+(0.5*reveal)+')');
    grad.addColorStop(0.7,'rgba({rgb},'+(0.15*reveal)+')');
    grad.addColorStop(1,'rgba({rgb},0)');
    eyeCtx.fillStyle=grad;
    eyeCtx.beginPath();
    eyeCtx.ellipse(960,420,140,84,0,0,Math.PI*2);
    eyeCtx.fill();
  }}
  eyeT+=1;
  requestAnimationFrame(drawEye);
}}
drawEye();

const LINES={lines_js};
const msgEl=document.getElementById('kan-msg');
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

/* .kan- プレフィックス付き固有クラス群(宿帳/真鍮ネームプレート風テロップ) */
.kan-lt-frame{{position:absolute;bottom:80px;left:80px;display:flex;align-items:center;gap:0;background:linear-gradient(180deg,#d8c48c 0%,#a9873f 45%,#7c611f 100%);border:1px solid #5c4416;box-shadow:inset 0 2px 4px rgba(255,255,255,0.4),inset 0 -3px 6px rgba(0,0,0,0.45),0 6px 14px rgba(0,0,0,0.5);border-radius:2px;}}
.kan-lt-label{{padding:14px 18px;font-size:11px;letter-spacing:3px;color:#3a2a0c;border-right:1px solid rgba(60,40,10,0.4);}}
.kan-lt-name{{padding:14px 26px;font-size:32px;letter-spacing:3px;color:#241705;text-shadow:0 1px 0 rgba(255,255,255,0.3);}}
.kan-lt-title{{position:absolute;left:80px;bottom:52px;font-size:11px;letter-spacing:4px;color:rgba({rgb},0.55);}}
</style>
</head>
<body>
<div class="kan-lt-frame">
  <div class="kan-lt-label">宿帳</div>
  <span class="kan-lt-name" id="name-el">名前</span>
</div>
<div class="kan-lt-title" id="title-el">LIVE</div>
<script>
const p=new URLSearchParams(window.location.search);
document.getElementById('name-el').textContent=p.get('name')||'名前';
document.getElementById('title-el').textContent=p.get('title')||'LIVE';
</script>
</body>
</html>'''


SPEC = {
    "id": "kanrinin",
    "name": "管理人室",
    "color": COLOR,
    "rgb": RGB,
    "bg": BG,
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "しばらくお待ちください",
        "label": "管理 継続中",
        "brb_main": "管理人は席を外しています",
    },
}
