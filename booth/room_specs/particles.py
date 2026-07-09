#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 粒子観測(particles) 専用実装

デザイン指針(ROADMAP・方式A):
  waiting: 本体と同じ粒子群(赤/青/黄の引力・反発シミュレーション)+
           観測レティクル(最も近い粒子を追う十字照準+座標表示)が主役
  brb: 粒子が一点に収束していく過程をループ
  lower_third: 名前の周囲を粒子が公転する

一次データ:
  static/particle-engine.js の粒子パラメータ・色をread_sourceで実読して踏襲する。
  BASE_PARAMS(attDist/repDist/attF/repF/maxSpd/conDist)、色は
  drawGroup既定値 r=rgb(255,55,55) b=rgb(55,148,255) y=rgb(255,220,30)。
"""
import json
import sys as _sys
from pathlib import Path as _Path

_BOOTH_DIR = _Path(__file__).resolve().parent.parent
if str(_BOOTH_DIR) not in _sys.path:
    _sys.path.insert(0, str(_BOOTH_DIR))
import asset_extract  # noqa: E402
import pack_base  # noqa: E402

SPEC_ID = "particles"
NAME = "粒子観測"
COLOR = "#4499ff"
RGB = "68,153,255"
BG = "#000408"

# static/particle-engine.js のBASE_PARAMS・色定義を実読して踏襲する
_JS_SRC = asset_extract.read_source("static/particle-engine.js")
_HAS_BASE_PARAMS = "BASE_PARAMS" in _JS_SRC
_HAS_ATTDIST = "attDist" in _JS_SRC

# 本体の色定義(drawGroup既定値)をそのまま踏襲
PARTICLE_COLORS = {
    "r": [255, 55, 55],
    "b": [55, 148, 255],
    "y": [255, 220, 30],
}


def waiting_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    colors_js = json.dumps(PARTICLE_COLORS)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 待機画面</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:'Courier New',monospace;color:{color};}}

/* .ptc- プレフィックス付き固有クラス群(粒子群+観測レティクルが主役) */
.ptc-stage{{position:absolute;inset:0;width:1920px;height:1080px;}}
.ptc-reticle-layer{{position:absolute;inset:0;width:1920px;height:1080px;z-index:5;pointer-events:none;}}
.ptc-header{{position:absolute;top:56px;left:64px;font-size:13px;letter-spacing:6px;color:rgba({rgb},0.7);z-index:6;}}
.ptc-coord{{position:absolute;top:56px;right:64px;font-size:13px;letter-spacing:2px;color:rgba({rgb},0.85);text-align:right;z-index:6;}}
.ptc-coord span{{display:block;}}
.ptc-footer{{position:absolute;bottom:56px;left:0;width:100%;text-align:center;font-size:13px;letter-spacing:6px;color:rgba({rgb},0.5);z-index:6;}}
</style>
</head>
<body>
<canvas class="ptc-stage" id="ptcCanvas"></canvas>
<canvas class="ptc-reticle-layer" id="ptcReticle"></canvas>
<div class="ptc-header">KYOUKAI // {NAME}</div>
<div class="ptc-coord" id="ptcCoord"><span>X: ----</span><span>Y: ----</span></div>
<div class="ptc-footer">観測レティクルが最も近い粒子を追跡しています</div>
<script>
// static/particle-engine.jsの引力・反発パラメータ(attDist/repDist/attF/repF/maxSpd)を移植したインライン実装
(function(){{
  var W=1920,H=1080;
  var stage=document.getElementById('ptcCanvas');
  stage.width=W;stage.height=H;
  var sctx=stage.getContext('2d');
  var COLORS={colors_js};
  var N=420;
  var pts=[];
  for(var i=0;i<N;i++){{
    var f=i/N;
    var t=f<0.4?'r':f<0.8?'b':'y';
    pts.push({{
      x:W*0.5+(Math.random()-0.5)*W*0.7,
      y:H*0.5+(Math.random()-0.5)*H*0.7,
      vx:(Math.random()-0.5)*0.6,
      vy:(Math.random()-0.5)*0.6,
      t:t,
      sz:t==='r'?2.6:t==='b'?2.0:2.2
    }});
  }}
  var attDist=90,repDist=24,attF=0.010,repF=0.075,maxSpd=1.5;
  function step(){{
    for(var i=0;i<pts.length;i++){{
      var a=pts[i],fx=0,fy=0;
      for(var j=0;j<pts.length;j+=3){{
        if(i===j)continue;
        var b=pts[j];
        var dx=b.x-a.x,dy=b.y-a.y;
        var d2=dx*dx+dy*dy;
        if(d2<1||d2>attDist*attDist)continue;
        var d=Math.sqrt(d2);
        if(d<repDist){{
          var f=repF*(1-d/repDist);
          fx-=(dx/d)*f;fy-=(dy/d)*f;
        }} else {{
          var f2=attF*(1-d/attDist);
          fx+=(dx/d)*f2;fy+=(dy/d)*f2;
        }}
      }}
      a.vx=(a.vx+fx)*0.96;a.vy=(a.vy+fy)*0.96;
      var spd=Math.sqrt(a.vx*a.vx+a.vy*a.vy);
      if(spd>maxSpd){{a.vx=a.vx/spd*maxSpd;a.vy=a.vy/spd*maxSpd;}}
      a.x+=a.vx;a.y+=a.vy;
      if(a.x<20){{a.x=20;a.vx=Math.abs(a.vx);}}
      if(a.x>W-20){{a.x=W-20;a.vx=-Math.abs(a.vx);}}
      if(a.y<20){{a.y=20;a.vy=Math.abs(a.vy);}}
      if(a.y>H-20){{a.y=H-20;a.vy=-Math.abs(a.vy);}}
    }}
  }}
  function draw(){{
    sctx.fillStyle='{bg}';
    sctx.fillRect(0,0,W,H);
    ['r','b','y'].forEach(function(type){{
      var c=COLORS[type];
      sctx.fillStyle='rgb('+c[0]+','+c[1]+','+c[2]+')';
      sctx.beginPath();
      for(var i=0;i<pts.length;i++){{
        var p=pts[i];
        if(p.t!==type)continue;
        sctx.moveTo(p.x+p.sz,p.y);
        sctx.arc(p.x,p.y,p.sz,0,Math.PI*2);
      }}
      sctx.fill();
    }});
  }}

  var reticle=document.getElementById('ptcReticle');
  reticle.width=W;reticle.height=H;
  var rctx=reticle.getContext('2d');
  var coordEl=document.getElementById('ptcCoord');
  var trackX=W*0.5,trackY=H*0.5;
  function nearestParticle(){{
    var best=null,bd=Infinity;
    for(var i=0;i<pts.length;i++){{
      var p=pts[i];
      var dx=p.x-trackX,dy=p.y-trackY;
      var d=dx*dx+dy*dy;
      if(d<bd){{bd=d;best=p;}}
    }}
    return best;
  }}
  var t=0;
  function drawReticle(){{
    t+=0.01;
    trackX=W*0.5+Math.cos(t*0.6)*W*0.32;
    trackY=H*0.5+Math.sin(t*0.9)*H*0.32;
    var target=nearestParticle();
    var rx=target?target.x:trackX, ry=target?target.y:trackY;
    rctx.clearRect(0,0,W,H);
    rctx.strokeStyle='rgba({rgb},0.85)';
    rctx.lineWidth=1.5;
    rctx.beginPath();
    rctx.moveTo(rx-26,ry);rctx.lineTo(rx-8,ry);
    rctx.moveTo(rx+8,ry);rctx.lineTo(rx+26,ry);
    rctx.moveTo(rx,ry-26);rctx.lineTo(rx,ry-8);
    rctx.moveTo(rx,ry+8);rctx.lineTo(rx,ry+26);
    rctx.stroke();
    rctx.strokeStyle='rgba({rgb},0.4)';
    rctx.beginPath();
    rctx.arc(rx,ry,36,0,Math.PI*2);
    rctx.stroke();
    coordEl.innerHTML='<span>X: '+rx.toFixed(1)+'</span><span>Y: '+ry.toFixed(1)+'</span>';
  }}

  function loop(){{
    step();
    draw();
    drawReticle();
    requestAnimationFrame(loop);
  }}
  loop();
}})();
</script>
</body>
</html>'''


def brb_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    bg = spec.get("bg", BG)
    colors_js = json.dumps(PARTICLE_COLORS)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{NAME} - 離席中</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{bg};overflow:hidden;font-family:'Courier New',monospace;color:{color};}}

/* .ptc- プレフィックス付き固有クラス群(waitingとは骨格が異なる: 収束ループ専用の中央集約構図) */
.ptc-brb-stage{{position:absolute;inset:0;width:1920px;height:1080px;}}
.ptc-brb-msg{{position:absolute;bottom:120px;left:0;width:100%;text-align:center;font-size:28px;letter-spacing:6px;color:{color};text-shadow:0 0 16px rgba({rgb},0.6);}}
.ptc-brb-label{{position:absolute;top:60px;left:0;width:100%;text-align:center;font-size:13px;letter-spacing:8px;color:rgba({rgb},0.55);}}
</style>
</head>
<body>
<canvas class="ptc-brb-stage" id="ptcBrbCanvas"></canvas>
<div class="ptc-brb-label">粒子 収束観測</div>
<div class="ptc-brb-msg">粒子が一点に収束しています</div>
<script>
(function(){{
  var W=1920,H=1080;
  var cv=document.getElementById('ptcBrbCanvas');
  cv.width=W;cv.height=H;
  var ctx=cv.getContext('2d');
  var COLORS={colors_js};
  var cx=W*0.5,cy=H*0.5;
  var N=300;
  var pts=[];
  function reset(){{
    pts=[];
    for(var i=0;i<N;i++){{
      var f=i/N;
      var t=f<0.4?'r':f<0.8?'b':'y';
      var ang=Math.random()*Math.PI*2;
      var rad=200+Math.random()*420;
      pts.push({{
        x:cx+Math.cos(ang)*rad,
        y:cy+Math.sin(ang)*rad,
        t:t,
        sz:t==='r'?2.6:t==='b'?2.0:2.2
      }});
    }}
  }}
  reset();
  var progress=0;
  function step(){{
    progress+=0.0032;
    if(progress>=1){{progress=0;reset();}}
    for(var i=0;i<pts.length;i++){{
      var p=pts[i];
      p.x+=(cx-p.x)*0.012;
      p.y+=(cy-p.y)*0.012;
    }}
  }}
  function draw(){{
    ctx.fillStyle='{bg}';
    ctx.fillRect(0,0,W,H);
    ctx.strokeStyle='rgba({rgb},'+(0.12+progress*0.3).toFixed(3)+')';
    ctx.lineWidth=1;
    ctx.beginPath();
    ctx.arc(cx,cy,10+progress*30,0,Math.PI*2);
    ctx.stroke();
    ['r','b','y'].forEach(function(type){{
      var c=COLORS[type];
      ctx.fillStyle='rgb('+c[0]+','+c[1]+','+c[2]+')';
      ctx.beginPath();
      for(var i=0;i<pts.length;i++){{
        var p=pts[i];
        if(p.t!==type)continue;
        ctx.moveTo(p.x+p.sz,p.y);
        ctx.arc(p.x,p.y,p.sz,0,Math.PI*2);
      }}
      ctx.fill();
    }});
  }}
  function loop(){{
    step();
    draw();
    requestAnimationFrame(loop);
  }}
  loop();
}})();
</script>
</body>
</html>'''


def lower_third_html(spec):
    color = spec.get("color", COLOR)
    rgb = spec.get("rgb", RGB)
    colors_js = json.dumps(PARTICLE_COLORS)
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

/* .ptc- プレフィックス付き固有クラス群(名前の周囲を粒子が公転する) */
.ptc-lt-wrap{{position:absolute;bottom:90px;left:90px;}}
.ptc-lt-orbit{{position:absolute;left:0;top:0;}}
.ptc-lt-name{{position:relative;font-size:34px;letter-spacing:3px;color:rgba(255,255,255,0.94);padding:18px 40px;background:rgba(0,4,8,0.55);border:1px solid rgba({rgb},0.4);z-index:2;}}
.ptc-lt-title{{position:absolute;left:0;top:76px;font-size:11px;letter-spacing:4px;color:rgba({rgb},0.6);z-index:2;}}
</style>
</head>
<body>
<div class="ptc-lt-wrap">
  <canvas class="ptc-lt-orbit" id="ptcOrbit" width="420" height="140"></canvas>
  <div class="ptc-lt-name" id="name-el">名前</div>
  <div class="ptc-lt-title" id="title-el">KYOUKAI</div>
</div>
<script>
const p=new URLSearchParams(window.location.search);
document.getElementById('name-el').textContent=p.get('name')||'名前';
document.getElementById('title-el').textContent=p.get('title')||'KYOUKAI';

(function(){{
  var cv=document.getElementById('ptcOrbit');
  var ctx=cv.getContext('2d');
  var COLORS={colors_js};
  var W=cv.width,H=cv.height;
  var cx=W*0.5,cy=H*0.5;
  var N=18;
  var pts=[];
  for(var i=0;i<N;i++){{
    var f=i/N;
    pts.push({{
      angle:f*Math.PI*2,
      radius:70+Math.random()*30,
      speed:0.006+Math.random()*0.008,
      t:i%3===0?'r':i%3===1?'b':'y',
      sz:2+Math.random()*1.4
    }});
  }}
  function loop(){{
    ctx.clearRect(0,0,W,H);
    for(var i=0;i<pts.length;i++){{
      var pt=pts[i];
      pt.angle+=pt.speed;
      var x=cx+Math.cos(pt.angle)*pt.radius;
      var y=cy+Math.sin(pt.angle)*pt.radius*0.42;
      var c=COLORS[pt.t];
      ctx.fillStyle='rgb('+c[0]+','+c[1]+','+c[2]+')';
      ctx.beginPath();
      ctx.arc(x,y,pt.sz,0,Math.PI*2);
      ctx.fill();
    }}
    requestAnimationFrame(loop);
  }}
  loop();
}})();
</script>
</body>
</html>'''


SPEC = {
    "id": "particles",
    "name": "粒子観測",
    "color": COLOR,
    "rgb": RGB,
    "bg": BG,
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "運動は意味の前にある",
        "label": "粒子 観測中",
        "brb_main": "粒子を観測しています",
    },
}
