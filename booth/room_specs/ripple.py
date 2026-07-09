#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 波紋域(ripple) 専用実装

デザイン指針(ROADMAP・方式A):
  waiting: 本体と同じドットグリッド+自動波紋
  brb: 波紋が中心から周期的に広がり画面を初期化する(本体の1分周期黒戻しを踏襲)
  lower_third: 名前の下から波紋が広がるテロップ

一次データ:
  static/ripple.js のドット色遷移パレット(暗赤→赤→黄→青→白)・波紋周期・
  黒戻し波紋(60秒周期のblackoutモード)をread_sourceで実読して踏襲する。
"""
import json
import sys as _sys
from pathlib import Path as _Path

_BOOTH_DIR = _Path(__file__).resolve().parent.parent
if str(_BOOTH_DIR) not in _sys.path:
    _sys.path.insert(0, str(_BOOTH_DIR))
import asset_extract  # noqa: E402
import pack_base  # noqa: E402

SPEC_ID = "ripple"
NAME = "波紋域"
COLOR = "#00ccbb"
RGB = "0,204,187"
BG = "#000604"

# static/ripple.js のパレット・黒戻し周期を実読して踏襲する
_JS_SRC = asset_extract.read_source("static/ripple.js")
_HAS_PALETTE = "palette" in _JS_SRC
_HAS_BLACKOUT = "nextBlackoutRipple" in _JS_SRC

# 本体パレット(暗赤→赤→黄→青→白)をそのまま踏襲
PALETTE = [
    [34, 2, 6],
    [148, 14, 20],
    [221, 168, 42],
    [31, 87, 184],
    [236, 242, 232],
]
BLACKOUT_INTERVAL_MS = 60000


def waiting_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    palette_js = json.dumps(PALETTE)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 待機画面</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:'Courier New',monospace;color:{color};}}

/* .rpl- プレフィックス付き固有クラス群(本体と同じドットグリッド+自動波紋が主役) */
.rpl-grid-canvas{{position:absolute;inset:0;width:1920px;height:1080px;}}
.rpl-header{{position:absolute;top:56px;left:0;width:100%;text-align:center;font-size:13px;letter-spacing:8px;color:rgba({rgb},0.6);z-index:6;}}
.rpl-footer{{position:absolute;bottom:56px;left:0;width:100%;text-align:center;font-size:13px;letter-spacing:5px;color:rgba({rgb},0.45);z-index:6;}}
</style>
</head>
<body>
<canvas class="rpl-grid-canvas" id="rplCanvas"></canvas>
<div class="rpl-header">KYOUKAI // {NAME}</div>
<div class="rpl-footer">触れると世界が応答します(待機中は自動応答)</div>
<script>
(function(){{
  var W=1920,H=1080;
  var cv=document.getElementById('rplCanvas');
  cv.width=W;cv.height=H;
  var ctx=cv.getContext('2d');
  var PALETTE={palette_js};
  var step=14,radius=3.0;
  var cols=Math.floor(W/step),rows=Math.floor(H/step);
  var offX=(W-(cols-1)*step)*0.5,offY=(H-(rows-1)*step)*0.5;
  var dots=[];
  for(var y=0;y<rows;y++){{
    for(var x=0;x<cols;x++){{
      dots.push({{
        x:x,y:y,
        px:offX+x*step,py:offY+y*step,
        state:Math.random()<0.02?1:0,
        scale:0,glow:Math.random()*0.08
      }});
    }}
  }}
  var ripples=[];
  var rippleId=1;
  function spawnRipple(x,y,strength,idle){{
    ripples.push({{
      id:rippleId++,x:x,y:y,radius:0,
      speed:idle?1.1:2.25,
      maxRadius:Math.min(Math.max(W,H)*0.34,680),
      strength:strength,
      band:Math.max(7,step*0.92),
      seen:{{}}
    }});
    if(ripples.length>18)ripples.splice(0,ripples.length-18);
  }}
  var idleMs=0,nextIdle=1500,lastFrame=0;
  function affect(){{
    for(var r=0;r<ripples.length;r++){{
      var rp=ripples[r];
      var inner=Math.max(0,rp.radius-rp.band),outer=rp.radius+rp.band;
      var iSq=inner*inner,oSq=outer*outer;
      for(var i=0;i<dots.length;i++){{
        if(rp.seen[i])continue;
        var d=dots[i];
        var dx=d.px-rp.x,dy=d.py-rp.y;
        var dist=dx*dx+dy*dy;
        if(dist<iSq||dist>oSq)continue;
        rp.seen[i]=true;
        d.state=(d.state+1)%PALETTE.length;
        d.scale=Math.max(d.scale,1.15*rp.strength);
        d.glow=Math.max(d.glow,1.0*rp.strength);
      }}
    }}
  }}
  function frame(ts){{
    var dt=lastFrame?Math.min(48,ts-lastFrame):16.67;
    lastFrame=ts;
    idleMs+=dt;
    ctx.fillStyle='{bg}';
    ctx.fillRect(0,0,W,H);
    if(idleMs>nextIdle){{
      nextIdle=idleMs+1800+Math.random()*3200;
      spawnRipple(W*(0.18+Math.random()*0.64),H*(0.18+Math.random()*0.64),0.55,true);
    }}
    for(var i=ripples.length-1;i>=0;i--){{
      ripples[i].radius+=ripples[i].speed*dt*0.06;
      if(ripples[i].radius>=ripples[i].maxRadius)ripples.splice(i,1);
    }}
    affect();
    for(var i=0;i<dots.length;i++){{
      var d=dots[i];
      d.scale*=Math.pow(0.91,dt/16.67);
      d.glow*=Math.pow(0.985,dt/16.67);
      var c=PALETTE[d.state];
      var pulse=1+d.scale*0.55;
      var alpha=Math.max(0.12,Math.min(0.96,0.46+d.glow*0.42));
      ctx.globalAlpha=alpha;
      ctx.fillStyle='rgb('+c[0]+','+c[1]+','+c[2]+')';
      ctx.beginPath();
      ctx.arc(d.px,d.py,radius*pulse,0,Math.PI*2);
      ctx.fill();
    }}
    ctx.globalAlpha=1;
    requestAnimationFrame(frame);
  }}
  requestAnimationFrame(frame);
}})();
</script>
</body>
</html>'''


def brb_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    palette_js = json.dumps(PALETTE)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 離席中</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:'Courier New',monospace;color:{color};}}

/* .rpl- プレフィックス付き固有クラス群(waitingとは骨格が異なる: 中心からの黒戻し波紋が周期的に画面を初期化) */
.rpl-brb-canvas{{position:absolute;inset:0;width:1920px;height:1080px;}}
.rpl-brb-msg{{position:absolute;bottom:120px;left:0;width:100%;text-align:center;font-size:28px;letter-spacing:6px;color:{color};text-shadow:0 0 16px rgba({rgb},0.6);z-index:6;}}
.rpl-brb-label{{position:absolute;top:60px;left:0;width:100%;text-align:center;font-size:13px;letter-spacing:8px;color:rgba({rgb},0.55);z-index:6;}}
</style>
</head>
<body>
<canvas class="rpl-brb-canvas" id="rplBrbCanvas"></canvas>
<div class="rpl-brb-label">波紋 観測中</div>
<div class="rpl-brb-msg">波紋を観測しています</div>
<script>
(function(){{
  var W=1920,H=1080;
  var cv=document.getElementById('rplBrbCanvas');
  cv.width=W;cv.height=H;
  var ctx=cv.getContext('2d');
  var PALETTE={palette_js};
  var step=16,radius=3.2;
  var cols=Math.floor(W/step),rows=Math.floor(H/step);
  var offX=(W-(cols-1)*step)*0.5,offY=(H-(rows-1)*step)*0.5;
  var dots=[];
  for(var y=0;y<rows;y++){{
    for(var x=0;x<cols;x++){{
      dots.push({{x:offX+x*step,y:offY+y*step,state:0,blackout:0}});
    }}
  }}
  var blackoutRipple=null;
  var blackoutInterval={BLACKOUT_INTERVAL_MS};
  var nextBlackout=1200; // brbは待たせず早めに初期化演出を見せる
  var lastFrame=0,elapsed=0;
  function spawnBlackout(){{
    blackoutRipple={{x:W*0.5,y:H*0.5,radius:0,speed:2.85,maxRadius:Math.hypot(W,H)*0.62,band:Math.max(28,step*4.4),seen:{{}}}};
  }}
  function frame(ts){{
    var dt=lastFrame?Math.min(48,ts-lastFrame):16.67;
    lastFrame=ts;
    elapsed+=dt;
    ctx.fillStyle='{bg}';
    ctx.fillRect(0,0,W,H);
    if(elapsed>nextBlackout && !blackoutRipple){{
      nextBlackout=elapsed+blackoutInterval;
      spawnBlackout();
    }}
    if(blackoutRipple){{
      var rp=blackoutRipple;
      rp.radius+=rp.speed*dt*0.06;
      var inner=Math.max(0,rp.radius-rp.band),outer=rp.radius+rp.band;
      var iSq=inner*inner,oSq=outer*outer;
      for(var i=0;i<dots.length;i++){{
        if(rp.seen[i])continue;
        var d=dots[i];
        var dx=d.x-rp.x,dy=d.y-rp.y;
        var dist=dx*dx+dy*dy;
        if(dist<iSq||dist>oSq)continue;
        rp.seen[i]=true;
        d.state=0;
        d.blackout=1;
      }}
      if(rp.radius>=rp.maxRadius){{
        blackoutRipple=null;
        for(var i=0;i<dots.length;i++){{dots[i].blackout=0;dots[i].state=Math.random()<0.02?1:0;}}
      }}
    }}
    for(var i=0;i<dots.length;i++){{
      var d=dots[i];
      var c=PALETTE[d.state];
      var black=d.blackout;
      var red=Math.round(c[0]*(1-black));
      var green=Math.round(c[1]*(1-black));
      var blue=Math.round(c[2]*(1-black));
      ctx.globalAlpha=0.5;
      ctx.fillStyle='rgb('+red+','+green+','+blue+')';
      ctx.beginPath();
      ctx.arc(d.x,d.y,radius,0,Math.PI*2);
      ctx.fill();
    }}
    ctx.globalAlpha=1;
    requestAnimationFrame(frame);
  }}
  requestAnimationFrame(frame);
}})();
</script>
</body>
</html>'''


def lower_third_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    palette_js = json.dumps(PALETTE)
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

/* .rpl- プレフィックス付き固有クラス群(名前の下から波紋が広がる) */
.rpl-lt-wrap{{position:absolute;bottom:90px;left:90px;}}
.rpl-lt-canvas{{position:absolute;left:-40px;top:20px;}}
.rpl-lt-name{{position:relative;font-size:34px;letter-spacing:3px;color:rgba(255,255,255,0.94);padding:18px 40px;background:rgba(0,6,4,0.55);border:1px solid rgba({rgb},0.4);z-index:2;}}
.rpl-lt-title{{position:absolute;left:0;top:76px;font-size:11px;letter-spacing:4px;color:rgba({rgb},0.6);z-index:2;}}
</style>
</head>
<body>
<div class="rpl-lt-wrap">
  <canvas class="rpl-lt-canvas" id="rplLtCanvas" width="500" height="140"></canvas>
  <div class="rpl-lt-name" id="name-el">名前</div>
  <div class="rpl-lt-title" id="title-el">KYOUKAI</div>
</div>
<script>
const p=new URLSearchParams(window.location.search);
document.getElementById('name-el').textContent=p.get('name')||'名前';
document.getElementById('title-el').textContent=p.get('title')||'KYOUKAI';

(function(){{
  var cv=document.getElementById('rplLtCanvas');
  var ctx=cv.getContext('2d');
  var PALETTE={palette_js};
  var W=cv.width,H=cv.height;
  var cx=W*0.5,cy=H*0.98;
  var ripples=[];
  var t=0;
  function spawn(){{
    ripples.push({{radius:0,state:Math.floor(Math.random()*PALETTE.length)}});
  }}
  setInterval(spawn,1400);
  spawn();
  function loop(){{
    t++;
    ctx.clearRect(0,0,W,H);
    for(var i=ripples.length-1;i>=0;i--){{
      var r=ripples[i];
      r.radius+=1.6;
      if(r.radius>200){{ripples.splice(i,1);continue;}}
      var c=PALETTE[r.state];
      var alpha=Math.max(0,1-r.radius/200);
      ctx.strokeStyle='rgba('+c[0]+','+c[1]+','+c[2]+','+alpha.toFixed(3)+')';
      ctx.lineWidth=2;
      ctx.beginPath();
      ctx.arc(cx,cy,r.radius,Math.PI,Math.PI*2);
      ctx.stroke();
    }}
    requestAnimationFrame(loop);
  }}
  loop();
}})();
</script>
</body>
</html>'''


SPEC = {
    "id": "ripple",
    "name": "波紋域",
    "color": COLOR,
    "rgb": RGB,
    "bg": BG,
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "触れると世界が応答します",
        "label": "応答 検出",
        "brb_main": "波紋を観測しています",
    },
}
