#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 記録室(archive) 専用実装

デザイン指針(ROADMAP):
  waiting: ファイル棚のグリッド。カードが差し替わる
  brb: 「照合中」のファイルカードが1枚ずつめくれる
  lower_third: インデックスカード/ラベルシール風

一次データ: templates/archive.html の記録フォーマット(日付・ID・内容、カルテラック風カード演出)
"""
import json
import sys as _sys
from pathlib import Path as _Path

_BOOTH_DIR = _Path(__file__).resolve().parent.parent
if str(_BOOTH_DIR) not in _sys.path:
    _sys.path.insert(0, str(_BOOTH_DIR))
import asset_extract  # noqa: E402

SPEC_ID = "archive"
NAME = "記録室"
COLOR = "#8899aa"
RGB = "136,153,170"
BG = "#020408"

# templates/archive.html を実読込し、カード形式(archive-card-meta: 日付/ID/内容)を確認した根拠
_ARCHIVE_SRC = asset_extract.read_source("templates/archive.html")
assert "archive-card-meta" in _ARCHIVE_SRC

FILE_RECORDS = [
    {"id": "0x00441", "date": "20XX-??-??", "body": "削除済みデータ。復元不能。"},
    {"id": "0x00442", "date": "20XX-??-??", "body": "感情 排除。記録のみ残る。"},
    {"id": "0x00443", "date": "不明", "body": "存在 確認済み。詳細は[REDACTED]。"},
    {"id": "0x00444", "date": "20XX-??-??", "body": "アーカイブ照合 中。該当なし。"},
    {"id": "0x00445", "date": "不明", "body": "file_001.log ── 参照履歴あり。"},
    {"id": "0x00446", "date": "20XX-??-??", "body": "記録元: システム。改変痕跡なし。"},
]


def waiting_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    records_js = json.dumps(FILE_RECORDS, ensure_ascii=False)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 待機画面</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:Consolas,'Courier New',monospace;color:{color};}}

/* .arc- プレフィックス付き固有クラス群(ファイル棚グリッド) */
.arc-shelf-wrap{{position:absolute;inset:0;width:1920px;height:1080px;z-index:10;padding:70px 90px;}}
.arc-shelf-title{{font-size:13px;letter-spacing:7px;color:rgba({rgb},0.55);text-transform:uppercase;margin-bottom:28px;text-align:center;}}
.arc-shelf-grid{{display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(2,1fr);gap:28px;height:840px;}}
.arc-card{{position:relative;border:1px solid rgba({rgb},0.28);background:linear-gradient(150deg,rgba({rgb},0.05),rgba(0,0,0,0.3));padding:22px;display:flex;flex-direction:column;justify-content:space-between;opacity:0.15;transform:scale(0.94);transition:opacity .5s ease,transform .5s ease;}}
.arc-card.arc-card-active{{opacity:1;transform:scale(1);border-color:rgba({rgb},0.6);box-shadow:0 0 24px rgba({rgb},0.12);}}
.arc-card-id{{font-size:12px;letter-spacing:2px;color:rgba({rgb},0.5);}}
.arc-card-date{{font-size:10px;letter-spacing:2px;color:rgba({rgb},0.3);margin-top:4px;}}
.arc-card-body{{font-size:14px;line-height:1.7;color:rgba({rgb},0.82);margin-top:14px;}}
.arc-card-tag{{position:absolute;top:14px;right:16px;font-size:9px;letter-spacing:3px;color:rgba({rgb},0.4);}}
.arc-footer{{position:absolute;bottom:56px;left:90px;right:90px;display:flex;justify-content:space-between;font-size:10px;letter-spacing:4px;color:rgba({rgb},0.35);}}
canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:1;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="arc-shelf-wrap">
  <div class="arc-shelf-title">KYOUKAI ARCHIVE // カルテラック照合中</div>
  <div class="arc-shelf-grid" id="arc-grid"></div>
  <div class="arc-footer">
    <div>記録 照合中</div>
    <div id="arc-clock"></div>
  </div>
</div>
<script>
const canvas=document.getElementById('c');
const ctx=canvas.getContext('2d');
canvas.width=1920;canvas.height=1080;
function drawDust(){{
  ctx.fillStyle='rgba({rgb},0.02)';
  ctx.fillRect(0,0,1920,1080);
  for(let i=0;i<40;i++){{
    ctx.fillStyle='rgba({rgb},'+(0.02+Math.random()*0.04)+')';
    ctx.fillRect(Math.random()*1920,Math.random()*1080,1,1);
  }}
  requestAnimationFrame(drawDust);
}}
drawDust();

const RECORDS={records_js};
const grid=document.getElementById('arc-grid');
const SLOTS=6;
let assigned=[];
for(let i=0;i<SLOTS;i++){{
  const card=document.createElement('div');
  card.className='arc-card';
  grid.appendChild(card);
  assigned.push(RECORDS[i%RECORDS.length]);
}}
function renderCard(i){{
  const card=grid.children[i];
  const rec=assigned[i];
  card.innerHTML=`<div class="arc-card-tag">FILE</div><div class="arc-card-id">${{rec.id}}</div><div class="arc-card-date">${{rec.date}}</div><div class="arc-card-body">${{rec.body}}</div>`;
}}
for(let i=0;i<SLOTS;i++) renderCard(i);
function cycleSlot(){{
  const i=Math.floor(Math.random()*SLOTS);
  const card=grid.children[i];
  card.classList.remove('arc-card-active');
  setTimeout(()=>{{
    assigned[i]=RECORDS[Math.floor(Math.random()*RECORDS.length)];
    renderCard(i);
    card.classList.add('arc-card-active');
  }},450);
}}
[...grid.children].forEach((c,i)=>setTimeout(()=>c.classList.add('arc-card-active'),i*140));
setInterval(cycleSlot,1800);

const clockEl=document.getElementById('arc-clock');
function tick(){{clockEl.textContent=new Date().toISOString().replace('T',' ').slice(0,19);}}
tick();setInterval(tick,1000);
</script>
</body>
</html>'''


def brb_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    records_js = json.dumps(FILE_RECORDS, ensure_ascii=False)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 離席中</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:Consolas,'Courier New',monospace;color:{color};}}

/* .arc- プレフィックス付き固有クラス群(単一カードが1枚ずつめくれる骨格。waitingのグリッドとは別構成) */
.arc-flip-stage{{position:absolute;inset:0;width:1920px;height:1080px;z-index:10;display:flex;align-items:center;justify-content:center;perspective:1800px;}}
.arc-flip-card{{width:560px;height:400px;position:relative;transform-style:preserve-3d;animation:arcFlip 3.6s ease-in-out infinite;border:1px solid rgba({rgb},0.35);background:linear-gradient(150deg,rgba({rgb},0.06),rgba(0,0,0,0.35));padding:32px;display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 0 40px rgba({rgb},0.1);}}
@keyframes arcFlip{{0%,40%{{transform:rotateY(0deg)}}50%{{transform:rotateY(90deg)}}60%,100%{{transform:rotateY(0deg)}}}}
.arc-flip-id{{font-size:14px;letter-spacing:3px;color:rgba({rgb},0.6);}}
.arc-flip-status{{font-size:12px;letter-spacing:5px;color:rgba({rgb},0.42);text-transform:uppercase;margin-top:20px;}}
.arc-flip-body{{font-size:17px;line-height:1.9;color:rgba({rgb},0.86);margin-top:24px;}}
.arc-flip-footer{{position:absolute;bottom:56px;left:0;right:0;text-align:center;font-size:11px;letter-spacing:6px;color:rgba({rgb},0.3);}}
canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:1;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="arc-flip-stage">
  <div class="arc-flip-card" id="arc-card">
    <div class="arc-flip-status">照合中</div>
    <div class="arc-flip-id" id="arc-id"></div>
    <div class="arc-flip-body" id="arc-body"></div>
  </div>
</div>
<div class="arc-flip-footer">削除されたはずの記録が残っています</div>
<script>
const canvas=document.getElementById('c');
const ctx=canvas.getContext('2d');
canvas.width=1920;canvas.height=1080;
function draw(){{
  ctx.fillStyle='rgba({rgb},0.015)';
  ctx.fillRect(0,0,1920,1080);
  requestAnimationFrame(draw);
}}
draw();

const RECORDS={records_js};
let ri=0;
const idEl=document.getElementById('arc-id');
const bodyEl=document.getElementById('arc-body');
function setRecord(){{
  const rec=RECORDS[ri%RECORDS.length];
  idEl.textContent=rec.id+' / '+rec.date;
  bodyEl.textContent=rec.body;
  ri++;
}}
setRecord();
setInterval(setRecord,3600);
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
html,body{{width:1920px;height:1080px;background:transparent;overflow:hidden;font-family:Consolas,'Courier New',monospace;}}

/* .arc- プレフィックス付き固有クラス群(インデックスカード/ラベルシール風) */
.arc-index-card{{position:absolute;bottom:76px;left:76px;width:520px;padding:18px 24px;background:linear-gradient(150deg,rgba(240,238,230,0.92),rgba(220,218,208,0.86));border:1px solid rgba(40,40,36,0.3);box-shadow:0 14px 30px rgba(0,0,0,0.4);transform:rotate(-1.2deg);animation:arcCardIn .6s ease both;}}
@keyframes arcCardIn{{from{{opacity:0;transform:rotate(-1.2deg) translateY(20px)}}to{{opacity:1;transform:rotate(-1.2deg) translateY(0)}}}}
.arc-index-tab{{position:absolute;top:-14px;left:24px;padding:3px 14px;background:rgba({rgb},0.85);color:#020408;font-size:10px;letter-spacing:3px;}}
.arc-index-name{{font-size:26px;letter-spacing:2px;color:#191915;margin-top:8px;}}
.arc-index-sep{{width:100%;height:1px;background:rgba(40,40,36,0.25);margin:10px 0;}}
.arc-index-title{{font-size:11px;letter-spacing:4px;color:#5c5c54;text-transform:uppercase;}}
</style>
</head>
<body>
<div class="arc-index-card">
  <div class="arc-index-tab">FILE COPY</div>
  <div class="arc-index-name" id="name-el">名前</div>
  <div class="arc-index-sep"></div>
  <div class="arc-index-title" id="title-el">KYOUKAI</div>
</div>
<script>
const p=new URLSearchParams(window.location.search);
document.getElementById('name-el').textContent=p.get('name')||'名前';
document.getElementById('title-el').textContent=p.get('title')||'KYOUKAI';
</script>
</body>
</html>'''


SPEC = {
    "id": "archive",
    "name": "記録室",
    "color": COLOR,
    "rgb": RGB,
    "bg": BG,
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "削除されたはずの記録が残っています",
        "label": "記録 照合中",
        "brb_main": "照合中",
    },
}
