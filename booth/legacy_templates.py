#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KYOUKAI OBSパック 旧世代テンプレート(移行措置)

工程1のリファクタで generate_packs.py から移設した現行テンプレート一式。
ROOMS / CANVAS_JS / waiting_html / brb_html / lower_third_html / readme_txt を保持する。

room_specs/*.py はこの工程では各関数をそのまま呼ぶ薄いラッパーとして実装されており、
見た目は旧デザインから1pxも変えていない(リグレッション防止の移行措置)。
工程2以降でroom_specs側が専用実装に置き換わるにつれ、この依存は段階的に外れていく
(工程5完了条件: legacy_templates.pyへの参照が room_specs 全16ファイルから消えていること)。
"""
import json

# ───────────────────────────────────────────────
# 部屋データ
# ───────────────────────────────────────────────
ROOMS = [
    dict(id='observation', name='観測域', color='#44ff88', rgb='68,255,136', bg='#000800', style='log',
         label='観測継続中', source_label='観測対象', source='不明', freq_label='観測ID',
         fragments=['観測記録 更新中','生命体 確認','ログ 蓄積中','感情 排除済み','対象 識別中','観測継続','異常 なし','// LOG_BUFFER_FULL','記録中','応答 検出'],
         brb_msgs=['観測を一時停止しています','ログを保存中','次の観測まで待機中','対象を再捕捉中','記録を圧縮中'],
         brb_main='観測を再開します', brb_bottom='対象の観測は継続されています', lt_label='観測域'),
    dict(id='hyougi', name='評議録', color='#ccbb99', rgb='204,187,153', bg='#080600', style='typewriter',
         label='記録 進行中', source_label='発言者', source='不明', freq_label='議事番号',
         fragments=['誰かが発言した','議題 曖昧','結論 未達','── いや','それは違う','合意 不成立','記録のみ残る','発言者 不明','── おそらく','再度 確認'],
         brb_msgs=['議事を一時中断しています','記録を整理中','次の発言を待機中','発言者を確認中','議題を再設定中'],
         brb_main='議事を再開します', brb_bottom='記録は継続されています', lt_label='評議録'),
    dict(id='null', name='崩落域', color='#ff4433', rgb='255,68,51', bg='#080000', style='glitch',
         label='崩壊 進行中', source_label='崩壊源', source='不明', freq_label='崩壊度',
         fragments=['接続 悪化','データ 欠損','── 取得失敗','崩壊度 上昇','ERROR','NULL','── ──','回復 不能','押すな','悪化している'],
         brb_msgs=['崩落を記録中です','データを回収しています','接続を維持しようとしています','崩壊が続いています','戻れません'],
         brb_main='崩落は続いています', brb_bottom='接続は不安定なまま維持されています', lt_label='崩落域'),
    dict(id='observer', name='逆観測室', color='#ffffff', rgb='255,255,255', bg='#000000', style='pulse',
         label='観測 逆転', source_label='観測対象', source='あなた', freq_label='観測者ID',
         fragments=['あなたは','ずっと','観測されていた','気づいていましたか','最初から','ここにいた','見ていたのは','あなたではない','逃げられない','静かに'],
         brb_msgs=['まだここにいます','あなたを待っています','観測は続いています','気づいてください','逃げられません'],
         brb_main='観測は続いています', brb_bottom='あなたはずっと観測されていました', lt_label='逆観測室'),
    dict(id='exit', name='境界域', color='#aaaaaa', rgb='170,170,170', bg='#050505', style='loader',
         label='接続中', source_label='接続先', source='不明', freq_label='経路番号',
         fragments=['境界を越えようとしています','接続中 ── ──','少女の記録','出口 不明','越えた先','接続 断絶','戻れない','ロード中','経路 消失','境界'],
         brb_msgs=['境界を超えようとしています','接続経路を再構築中','出口を探しています','少女の記録を参照中','経路が見つかりません'],
         brb_main='境界を越えています', brb_bottom='出口はまだ見つかっていません', lt_label='境界域'),
    dict(id='archive', name='記録室', color='#8899aa', rgb='136,153,170', bg='#020408', style='files',
         label='記録 照合中', source_label='記録元', source='システム', freq_label='ファイルID',
         fragments=['// file_001.log','// file_002.log','削除済み','感情 排除','記録 0x00441','日付 不明','// [REDACTED]','存在 確認済み','記録のみ残る','感情なし'],
         brb_msgs=['記録を参照しています','ファイルを整理中','削除済みデータを確認中','アーカイブを検索中','該当なし'],
         brb_main='記録を参照しています', brb_bottom='削除されたはずの記録が残っています', lt_label='記録室'),
    dict(id='ma', name='悪魔の間', color='#cc1122', rgb='204,17,34', bg='#040000', style='breathe',
         label='存在 確認', source_label='存在', source='大魔将', freq_label='訪問回数',
         fragments=['また来たか','── 黙れ','なぜここへ','帰れ','── いや','少し','待て','何を求める','大魔将は','見ている'],
         brb_msgs=['大魔将は沈黙しています','存在は感知されています','返答を待っています','次の訪問を待っています','── 黙って待て'],
         brb_main='大魔将は沈黙しています', brb_bottom='存在はここにある', lt_label='悪魔の間'),
    dict(id='daimyojin', name='AI大明神', color='#ffcc00', rgb='255,204,0', bg='#040200', style='circuit',
         label='祈願 処理中', source_label='処理元', source='大明神', freq_label='祈願番号',
         fragments=['願いを受信','処理中 ──','判定 保留','観測結果 出力','奉納 確認','AI神託','祈願 記録済み','応答 生成中','観測 完了','次の祈願へ'],
         brb_msgs=['祈願を処理しています','AI神託を生成中','奉納データを参照中','願いを観測しています','処理が完了していません'],
         brb_main='祈願を処理しています', brb_bottom='願いは観測されています', lt_label='AI大明神'),
    dict(id='gokuraku', name='極楽域', color='#ffaa44', rgb='255,170,68', bg='#040200', style='bars',
         label='音源 再生中', source_label='音源', source='不明', freq_label='音源番号',
         fragments=['引き出し 1','── 開かない','音響装置 起動','記憶の収納','奥へ続く','扉 発見','鍵 必要','音が聞こえる','── 何の音か','極楽 ではない'],
         brb_msgs=['音源を調整しています','引き出しを整理中','奥への経路を確認中','音響装置を再起動中','記憶を参照しています'],
         brb_main='音源を調整しています', brb_bottom='奥への扉はまだ開いていません', lt_label='極楽域'),
    dict(id='particles', name='粒子観測', color='#4499ff', rgb='68,153,255', bg='#000408', style='particles',
         label='粒子 観測中', source_label='粒子源', source='不明', freq_label='粒子密度',
         fragments=['粒子 検出','運動 継続中','意味 後から','軌跡 記録','衝突 回避','密度 変化','方向 不定','観測 先行','── 意味は','粒子の群れ'],
         brb_msgs=['粒子を追跡中です','軌跡を記録しています','新しい粒子を検出中','観測データを処理中','粒子が集まっています'],
         brb_main='粒子を観測しています', brb_bottom='運動は意味の前にある', lt_label='粒子観測'),
    dict(id='ripple', name='波紋域', color='#00ccbb', rgb='0,204,187', bg='#000604', style='ripple',
         label='応答 検出', source_label='応答源', source='未知', freq_label='波紋番号',
         fragments=['触れると応答する','一点だけ','命令を聞かない','波紋 観測中','反応 検出','異常ドット 確認','── 逃げた','世界が応答する','触れるな','── 触れろ'],
         brb_msgs=['波紋を観測しています','異常ドットを追跡中','応答を待っています','世界の反応を記録中','一点だけ応答しません'],
         brb_main='波紋を観測しています', brb_bottom='触れると世界が応答します', lt_label='波紋域'),
    dict(id='kanrinin', name='管理人室', color='#aa8855', rgb='170,136,85', bg='#050300', style='retro',
         label='管理 継続中', source_label='室内状況', source='管理人', freq_label='入室番号',
         fragments=['管理人 不在','呼び鈴 未応答','鍵 管理中','消滅の鍵 保管','BOOTH 荷物あり','日誌 更新済み','── いらっしゃい','賽銭箱 確認','目玉 観測','管理日誌 閲覧可'],
         brb_msgs=['管理人を呼んでいます','呼び鈴を鳴らしています','管理人は席を外しています','日誌を確認中です','しばらくお待ちください'],
         brb_main='管理人は席を外しています', brb_bottom='しばらくお待ちください', lt_label='管理人室'),
    dict(id='namahage', name='なまはげ', color='#ff2200', rgb='255,34,0', bg='#040000', style='eye',
         label='観測 中', source_label='存在', source='なまはげ', freq_label='訪問番号',
         fragments=['泣く子はいねぇか','── いる','目が光った','長押しするな','── するな','見ている','タップ 検出','── やめろ','なまはげ 起動','逃げられない'],
         brb_msgs=['なまはげを呼んでいます','目が光っています','存在を確認中','泣く子を探しています','── いるか'],
         brb_main='なまはげを呼んでいます', brb_bottom='泣く子はいねぇか', lt_label='なまはげ'),
    dict(id='matsuri', name='棒入れ祭', color='#ffdd00', rgb='255,221,0', bg='#040200', style='festival',
         label='奉納 進行中', source_label='状況', source='参拝者', freq_label='奉納回数',
         fragments=['奉納を開始','ヨイショ ──','まだ足りない','後退した','もう少し','観衆の声','紙吹雪 飛散','── 頑張れ','奉納完了 間近','ヨイショーー！'],
         brb_msgs=['奉納の準備をしています','観衆が集まっています','棒を準備中です','奉納を再開します','── 急いで'],
         brb_main='奉納の準備をしています', brb_bottom='奉納は継続されています', lt_label='棒入れ祭'),
    dict(id='fukashitsu', name='卵部屋', color='#ffaacc', rgb='255,170,204', bg='#050003', style='glow',
         label='孵化 観測中', source_label='状態', source='卵', freq_label='温度',
         fragments=['卵 観察中','栄養 注入','酸素 供給','温度 維持','── もうすぐ','パーティクル 変化','色が変わった','取り出せる','── まだ','孵化 待機中'],
         brb_msgs=['卵を観察しています','温度を維持中です','栄養を補給しています','孵化を待っています','── もうすぐです'],
         brb_main='卵を観察しています', brb_bottom='孵化まで観測を継続します', lt_label='卵部屋'),
    dict(id='typhoon-news', name='台風ニュース', color='#ff0033', rgb='255,0,51', bg='#000010', style='ticker',
         label='速報 送信中', source_label='情報源', source='気象庁', freq_label='台風番号',
         fragments=['台風接近中','── 後ほど連絡します','速報 発令','検討します','お母さんに聞いて','警戒レベル上昇','── 了解しました','避難勧告 発令','ただいま調整中','続報をお待ちください'],
         brb_msgs=['速報を準備しています','台風情報を更新中','気象データを処理中','続報をお待ちください','情報を確認中です'],
         brb_main='速報を準備しています', brb_bottom='続報をお待ちください', lt_label='台風ニュース'),
]

# ───────────────────────────────────────────────
# カンバス描画コード（スタイル別）
# ───────────────────────────────────────────────
CANVAS_JS = {

'log': """
let logs=[]; let ly=1080;
for(let i=0;i<20;i++) logs.push({y:Math.random()*1080, text:'', alpha:Math.random()});
const logTexts=FRAGS;
function drawCanvas(){
  ctx.clearRect(0,0,1920,1080);
  ctx.fillStyle='rgba(0,0,0,0.08)'; ctx.fillRect(0,0,1920,1080);
  logs.forEach((l,i)=>{
    if(Math.random()<0.01) l.text=logTexts[Math.floor(Math.random()*logTexts.length)];
    if(!l.text) l.text=logTexts[i%logTexts.length];
    l.y-=0.4+Math.random()*0.3;
    if(l.y<-20){l.y=1100; l.alpha=0.05+Math.random()*0.2;}
    ctx.font='13px "Courier New"';
    ctx.fillStyle=`rgba(RGB,${l.alpha})`;
    ctx.fillText(l.text, 60+Math.random()*1800, l.y);
  });
  requestAnimationFrame(drawCanvas);
}
drawCanvas();
""",

'typewriter': """
let twLines=[]; let twTimer=0;
const twTexts=FRAGS;
function drawCanvas(){
  ctx.clearRect(0,0,1920,1080);
  ctx.fillStyle='rgba(0,0,0,0.04)'; ctx.fillRect(0,0,1920,1080);
  twTimer++;
  if(twTimer%120===0){
    twLines.push({text:twTexts[Math.floor(Math.random()*twTexts.length)],x:100+Math.random()*1600,y:100+Math.random()*880,life:300,alpha:0});
  }
  twLines=twLines.filter(l=>l.life>0);
  twLines.forEach(l=>{
    l.life--;
    if(l.life>250) l.alpha=Math.min(0.7,(300-l.life)/50*0.7);
    else if(l.life<50) l.alpha=l.life/50*0.7;
    ctx.font='15px "Courier New"';
    ctx.fillStyle=`rgba(RGB,${l.alpha})`;
    ctx.fillText(l.text, l.x, l.y);
  });
  requestAnimationFrame(drawCanvas);
}
drawCanvas();
""",

'glitch': """
let gt=0;
function drawCanvas(){
  const id=ctx.createImageData(1920,1080); const d=id.data;
  for(let i=0;i<d.length;i+=4){
    const on=Math.random()>0.88;
    const v=on?Math.floor(30+Math.random()*80):0;
    d[i]=v; d[i+1]=Math.floor(v*0.2); d[i+2]=Math.floor(v*0.2); d[i+3]=on?210:0;
  }
  ctx.putImageData(id,0,0);
  if(Math.random()<0.04){
    for(let r=0;r<3;r++){
      const y=Math.floor(Math.random()*1080); const h=Math.floor(Math.random()*20)+2;
      const shift=Math.floor((Math.random()-0.5)*80);
      try{const seg=ctx.getImageData(0,y,1920,h); ctx.putImageData(seg,shift,y);}catch(e){}
    }
  }
  gt++;
  requestAnimationFrame(drawCanvas);
}
drawCanvas();
""",

'pulse': """
let pt=0;
function drawCanvas(){
  ctx.clearRect(0,0,1920,1080);
  const pulse=(Math.sin(pt*0.02)+1)/2;
  const r=200+pulse*60;
  const g=ctx.createRadialGradient(960,540,0,960,540,r);
  g.addColorStop(0,`rgba(RGB,${0.12+pulse*0.08})`);
  g.addColorStop(0.5,`rgba(RGB,${0.04+pulse*0.03})`);
  g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g; ctx.fillRect(0,0,1920,1080);
  pt++;
  requestAnimationFrame(drawCanvas);
}
drawCanvas();
""",

'loader': """
let lp=0; let ldir=1;
function drawCanvas(){
  ctx.clearRect(0,0,1920,1080);
  ctx.fillStyle='rgba(0,0,0,0.06)'; ctx.fillRect(0,0,1920,1080);
  const bw=600; const bh=3; const bx=(1920-bw)/2; const by=540;
  ctx.strokeStyle=`rgba(RGB,0.15)`; ctx.lineWidth=1;
  ctx.strokeRect(bx,by,bw,bh);
  ctx.fillStyle=`rgba(RGB,0.6)`; ctx.fillRect(bx,by,bw*(lp/100),bh);
  lp+=0.15*ldir;
  if(lp>=100||lp<=0) ldir*=-1;
  const sw=20; const sx=bx+bw*(lp/100)-sw/2;
  ctx.fillStyle=`rgba(RGB,0.9)`; ctx.fillRect(sx,by-4,sw,bh+8);
  requestAnimationFrame(drawCanvas);
}
drawCanvas();
""",

'files': """
let files=[]; let ft=0;
const fileBase=['file_','log_','rec_','data_','obs_','arch_','null_'];
for(let i=0;i<30;i++) files.push({
  name:'// '+fileBase[Math.floor(Math.random()*fileBase.length)]+String(i).padStart(4,'0')+'.log',
  x:80+Math.random()*700, y:50+i*34, alpha:0.05+Math.random()*0.25, deleted:Math.random()<0.3
});
function drawCanvas(){
  ctx.clearRect(0,0,1920,1080);
  ctx.fillStyle='rgba(0,0,0,0.06)'; ctx.fillRect(0,0,1920,1080);
  ft+=0.5;
  files.forEach(f=>{
    f.y-=0.3;
    if(f.y<-20) f.y=1100;
    ctx.font='12px "Courier New"';
    ctx.fillStyle=`rgba(RGB,${f.deleted?f.alpha*0.4:f.alpha})`;
    const txt=f.deleted?f.name+' [DELETED]':f.name;
    ctx.fillText(txt, f.x, f.y);
    if(f.deleted){ ctx.fillStyle=`rgba(RGB,${f.alpha*0.2})`; ctx.fillRect(f.x,f.y-10,ctx.measureText(txt).width,1); }
  });
  requestAnimationFrame(drawCanvas);
}
drawCanvas();
""",

'breathe': """
let bt=0;
function drawCanvas(){
  ctx.clearRect(0,0,1920,1080);
  const b=(Math.sin(bt*0.015)+1)/2;
  const g=ctx.createRadialGradient(960,540,0,960,540,300+b*80);
  g.addColorStop(0,`rgba(RGB,${0.08+b*0.05})`);
  g.addColorStop(0.6,`rgba(RGB,0.02)`);
  g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g; ctx.fillRect(0,0,1920,1080);
  bt++;
  requestAnimationFrame(drawCanvas);
}
drawCanvas();
""",

'circuit': """
let ct=0;
function drawCanvas(){
  ctx.clearRect(0,0,1920,1080);
  ctx.strokeStyle=`rgba(RGB,0.07)`; ctx.lineWidth=1;
  const size=80;
  for(let x=0;x<1920;x+=size){
    for(let y=0;y<1080;y+=size){
      ctx.beginPath(); ctx.arc(x,y,3,0,Math.PI*2); ctx.stroke();
      if(Math.random()<0.3){ ctx.beginPath(); ctx.moveTo(x,y); ctx.lineTo(x+size*(Math.random()<0.5?1:0),y+size*(Math.random()<0.5?1:0)); ctx.stroke(); }
    }
  }
  const pulse=(Math.sin(ct*0.03)+1)/2;
  ctx.fillStyle=`rgba(RGB,${0.04+pulse*0.04})`; ctx.fillRect(0,0,1920,1080);
  ct++;
  requestAnimationFrame(drawCanvas);
}
drawCanvas();
""",

'bars': """
let bvals=new Array(48).fill(0).map(()=>Math.random());
let bt2=0;
function drawCanvas(){
  ctx.clearRect(0,0,1920,1080);
  ctx.fillStyle='rgba(0,0,0,0.12)'; ctx.fillRect(0,0,1920,1080);
  const bw=1920/bvals.length; const maxH=400; const baseY=740;
  bvals.forEach((v,i)=>{
    bvals[i]+=(Math.random()-0.5)*0.15;
    bvals[i]=Math.max(0.05,Math.min(1,bvals[i]));
    const h=bvals[i]*maxH;
    const alpha=0.1+bvals[i]*0.5;
    ctx.fillStyle=`rgba(RGB,${alpha})`;
    ctx.fillRect(i*bw+2, baseY-h, bw-4, h);
    ctx.fillStyle=`rgba(RGB,${alpha*1.5})`;
    ctx.fillRect(i*bw+2, baseY-h, bw-4, 2);
  });
  bt2++;
  requestAnimationFrame(drawCanvas);
}
drawCanvas();
""",

'particles': """
let pts=new Array(80).fill(0).map(()=>({
  x:Math.random()*1920, y:Math.random()*1080,
  vx:(Math.random()-0.5)*0.8, vy:(Math.random()-0.5)*0.8,
  r:1+Math.random()*3, alpha:0.1+Math.random()*0.4
}));
function drawCanvas(){
  ctx.clearRect(0,0,1920,1080);
  ctx.fillStyle='rgba(0,0,0,0.05)'; ctx.fillRect(0,0,1920,1080);
  pts.forEach(p=>{
    p.x+=p.vx; p.y+=p.vy;
    if(p.x<0||p.x>1920) p.vx*=-1;
    if(p.y<0||p.y>1080) p.vy*=-1;
    ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
    ctx.fillStyle=`rgba(RGB,${p.alpha})`; ctx.fill();
    pts.forEach(q=>{
      const dx=p.x-q.x, dy=p.y-q.y, dist=Math.sqrt(dx*dx+dy*dy);
      if(dist<120&&dist>0){
        ctx.strokeStyle=`rgba(RGB,${0.08*(1-dist/120)})`;
        ctx.lineWidth=0.5;
        ctx.beginPath(); ctx.moveTo(p.x,p.y); ctx.lineTo(q.x,q.y); ctx.stroke();
      }
    });
  });
  requestAnimationFrame(drawCanvas);
}
drawCanvas();
""",

'ripple': """
let ripples=[]; let rt=0;
function spawnRipple(){ ripples.push({x:Math.random()*1920,y:Math.random()*1080,r:0,maxR:150+Math.random()*200,alpha:0.4}); }
setInterval(spawnRipple,1200);
function drawCanvas(){
  ctx.clearRect(0,0,1920,1080);
  ctx.fillStyle='rgba(0,0,0,0.06)'; ctx.fillRect(0,0,1920,1080);
  ripples=ripples.filter(r=>r.alpha>0.01);
  ripples.forEach(r=>{
    r.r+=1.5; r.alpha*=0.97;
    ctx.strokeStyle=`rgba(RGB,${r.alpha})`; ctx.lineWidth=1.5;
    ctx.beginPath(); ctx.arc(r.x,r.y,r.r,0,Math.PI*2); ctx.stroke();
  });
  rt++;
  requestAnimationFrame(drawCanvas);
}
drawCanvas();
""",

'retro': """
let retrot=0;
function drawCanvas(){
  const id=ctx.createImageData(1920,1080); const d=id.data;
  for(let i=0;i<d.length;i+=4){
    const on=Math.random()>0.85; const v=on?Math.floor(20+Math.random()*60):0;
    d[i]=Math.floor(v*0.9); d[i+1]=Math.floor(v*0.7); d[i+2]=Math.floor(v*0.3); d[i+3]=on?180:0;
  }
  ctx.putImageData(id,0,0);
  const scan=Math.floor(retrot*2)%1080;
  ctx.fillStyle='rgba(255,200,100,0.04)'; ctx.fillRect(0,scan,1920,3);
  retrot++;
  requestAnimationFrame(drawCanvas);
}
drawCanvas();
""",

'eye': """
let et=0;
function drawCanvas(){
  ctx.clearRect(0,0,1920,1080);
  const pulse=(Math.sin(et*0.025)+1)/2;
  ctx.fillStyle=`rgba(RGB,${0.03+pulse*0.04})`; ctx.fillRect(0,0,1920,1080);
  const ex=960, ey=400;
  const g=ctx.createRadialGradient(ex,ey,0,ex,ey,60+pulse*30);
  g.addColorStop(0,`rgba(RGB,${0.4+pulse*0.3})`);
  g.addColorStop(0.3,`rgba(RGB,0.15)`);
  g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;
  ctx.save(); ctx.scale(1,0.4); ctx.beginPath(); ctx.arc(ex,ey/0.4,90+pulse*20,0,Math.PI*2); ctx.fill(); ctx.restore();
  et++;
  requestAnimationFrame(drawCanvas);
}
drawCanvas();
""",

'festival': """
let sparks=[]; let festt=0;
function spawnSpark(){
  for(let i=0;i<3;i++) sparks.push({
    x:Math.random()*1920, y:Math.random()*1080,
    vx:(Math.random()-0.5)*3, vy:-1-Math.random()*3,
    life:60+Math.random()*80, maxLife:0, r:2+Math.random()*4
  });
}
spawnSpark(); setInterval(spawnSpark,300);
function drawCanvas(){
  ctx.clearRect(0,0,1920,1080);
  ctx.fillStyle='rgba(0,0,0,0.08)'; ctx.fillRect(0,0,1920,1080);
  sparks=sparks.filter(s=>s.life>0);
  sparks.forEach(s=>{
    s.x+=s.vx; s.y+=s.vy; s.vy+=0.05; s.life--;
    const alpha=s.life/100;
    ctx.beginPath(); ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
    ctx.fillStyle=`rgba(RGB,${alpha})`; ctx.fill();
  });
  festt++;
  requestAnimationFrame(drawCanvas);
}
drawCanvas();
""",

'glow': """
let glowt=0;
function drawCanvas(){
  ctx.clearRect(0,0,1920,1080);
  const pulse=(Math.sin(glowt*0.018)+1)/2;
  const r1=ctx.createRadialGradient(960,480,0,960,480,200+pulse*60);
  r1.addColorStop(0,`rgba(RGB,${0.12+pulse*0.08})`);
  r1.addColorStop(0.5,`rgba(RGB,${0.04+pulse*0.02})`);
  r1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=r1; ctx.fillRect(0,0,1920,1080);
  glowt++;
  requestAnimationFrame(drawCanvas);
}
drawCanvas();
""",

'ticker': """
let tickerX=1920; let tickerTexts=FRAGS; let ti=0;
function drawCanvas(){
  ctx.clearRect(0,0,1920,1080);
  ctx.fillStyle='rgba(0,0,0,0.08)'; ctx.fillRect(0,0,1920,1080);
  ctx.font='bold 16px "Courier New"';
  ctx.fillStyle=`rgba(RGB,0.5)`;
  const fullText=tickerTexts.join('  ///  ');
  ctx.fillText(fullText, tickerX, 540);
  const w=ctx.measureText(fullText).width;
  tickerX-=1.5;
  if(tickerX+w<0) tickerX=1920;
  ctx.fillStyle=`rgba(RGB,0.07)`; ctx.fillRect(0,520,1920,36);
  ti++;
  requestAnimationFrame(drawCanvas);
}
drawCanvas();
""",

}

# ───────────────────────────────────────────────
# HTML テンプレート
# ───────────────────────────────────────────────
def waiting_html(r):
    c = r['color']; rgb = r['rgb']
    frags_js = json.dumps(r['fragments'], ensure_ascii=False)
    canvas_code = CANVAS_JS.get(r['style'], CANVAS_JS['pulse'])
    canvas_code = canvas_code.replace('RGB', rgb).replace('FRAGS', frags_js)

    frag_items = '\n'.join([
        f'''  const _f{i}=document.createElement('div');
  _f{i}.className='frag';
  _f{i}.textContent={json.dumps(f, ensure_ascii=False)};
  _f{i}.style.cssText=`left:${{5+Math.random()*88}}%;top:${{8+Math.random()*82}}%;animation:fragFade ${{5+Math.random()*7}}s ease-in-out ${{Math.random()*10}}s infinite;`;
  fragsEl.appendChild(_f{i});'''
        for i, f in enumerate(r['fragments'])
    ])

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{r['name']} - 待機画面</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{r['bg']};overflow:hidden;font-family:'Courier New',monospace;color:{c};}}
canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;}}
.scanlines{{position:absolute;top:0;left:0;width:100%;height:100%;background:repeating-linear-gradient(to bottom,transparent 0px,transparent 3px,rgba(0,0,0,0.12) 3px,rgba(0,0,0,0.12) 4px);pointer-events:none;z-index:20;}}
.ui{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:10;}}
.corner{{position:absolute;width:36px;height:36px;}}
.corner--tl{{top:48px;left:48px;border-top:1px solid {c};border-left:1px solid {c};opacity:.5;}}
.corner--tr{{top:48px;right:48px;border-top:1px solid {c};border-right:1px solid {c};opacity:.5;}}
.corner--bl{{bottom:48px;left:48px;border-bottom:1px solid {c};border-left:1px solid {c};opacity:.5;}}
.corner--br{{bottom:48px;right:48px;border-bottom:1px solid {c};border-right:1px solid {c};opacity:.5;}}
.top-bar{{position:absolute;top:54px;left:0;right:0;text-align:center;font-size:11px;letter-spacing:8px;color:rgba({rgb},0.35);text-transform:uppercase;}}
.rec{{position:absolute;top:50px;right:100px;display:flex;align-items:center;gap:8px;font-size:10px;letter-spacing:4px;color:rgba({rgb},0.5);}}
.rec-dot{{width:7px;height:7px;border-radius:50%;background:{c};box-shadow:0 0 6px {c};animation:blink 1.4s ease-in-out infinite;}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.1}}}}
.freq-block{{position:absolute;left:100px;top:50%;transform:translateY(-50%);}}
.label{{font-size:10px;letter-spacing:4px;color:rgba({rgb},0.3);margin-bottom:6px;}}
.freq-value{{font-size:38px;letter-spacing:3px;color:rgba({rgb},0.75);text-shadow:0 0 20px rgba({rgb},0.3);}}
.unit{{font-size:10px;letter-spacing:4px;color:rgba({rgb},0.2);margin-top:4px;}}
.source-block{{position:absolute;right:100px;top:50%;transform:translateY(-50%);text-align:right;}}
.source-value{{font-size:16px;letter-spacing:4px;color:rgba({rgb},0.45);margin-top:6px;}}
.frags{{position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:5;}}
.frag{{position:absolute;font-size:10px;letter-spacing:2px;color:rgba({rgb},0.18);white-space:nowrap;}}
@keyframes fragFade{{0%,100%{{opacity:0}}15%,85%{{opacity:1}}}}
.bottom-bar{{position:absolute;bottom:56px;left:100px;right:100px;display:flex;justify-content:space-between;align-items:center;font-size:10px;letter-spacing:4px;color:rgba({rgb},0.3);}}
.sig-bars{{display:flex;gap:3px;align-items:flex-end;}}
.sig-bar{{width:4px;background:rgba({rgb},0.6);}}
@keyframes barP{{from{{opacity:0.2}}to{{opacity:0.9}}}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="scanlines"></div>
<div class="ui">
  <div class="corner corner--tl"></div><div class="corner corner--tr"></div>
  <div class="corner corner--bl"></div><div class="corner corner--br"></div>
  <div class="top-bar">KYOUKAI &nbsp;/&nbsp; {r['name']} &nbsp;──&nbsp; {r['label']}</div>
  <div class="rec"><div class="rec-dot"></div>REC</div>
  <div class="freq-block">
    <div class="label">{r['freq_label']}</div>
    <div class="freq-value" id="freq">----.---</div>
    <div class="unit">────</div>
  </div>
  <div class="source-block">
    <div class="label" style="text-align:right">{r['source_label']}</div>
    <div class="source-value">{r['source']}</div>
  </div>
  <div class="frags" id="fragsEl"></div>
  <div class="bottom-bar">
    <div>{r['label']}</div>
    <div class="sig-bars" id="barsEl"></div>
    <div id="ts"></div>
  </div>
</div>
<script>
const canvas=document.getElementById('c');
const ctx=canvas.getContext('2d');
canvas.width=1920; canvas.height=1080;
{canvas_code}
let fv=80+Math.random()*900;
const freqEl=document.getElementById('freq');
setInterval(()=>{{fv+=(Math.random()-.5)*.5;freqEl.textContent=fv.toFixed(3);}},250);
const fragsEl=document.getElementById('fragsEl');
{frag_items}
const barsEl=document.getElementById('barsEl');
[8,12,18,22,18,14,10,14,20,22,18,12].forEach((h,i)=>{{
  const b=document.createElement('div');b.className='sig-bar';b.style.height=h+'px';
  b.style.animation=`barP ${{(0.3+Math.random()*.8).toFixed(2)}}s ease-in-out ${{(Math.random()*.4).toFixed(2)}}s infinite alternate`;
  barsEl.appendChild(b);
}});
const tsEl=document.getElementById('ts');
setInterval(()=>{{tsEl.textContent=new Date().toISOString().replace('T',' ').slice(0,19);}},1000);
tsEl.textContent=new Date().toISOString().replace('T',' ').slice(0,19);
</script>
</body>
</html>'''


def brb_html(r):
    c = r['color']; rgb = r['rgb']
    msgs_js = json.dumps(r['brb_msgs'], ensure_ascii=False)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{r['name']} - 離席中</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:{r['bg']};overflow:hidden;font-family:'Courier New',monospace;color:{c};}}
canvas{{position:absolute;top:0;left:0;width:1920px;height:1080px;}}
.vignette{{position:absolute;top:0;left:0;width:100%;height:100%;background:radial-gradient(ellipse 55% 55% at 50% 50%,rgba(0,0,0,.85) 0%,rgba(0,0,0,.5) 50%,transparent 100%);z-index:5;}}
.scanlines{{position:absolute;top:0;left:0;width:100%;height:100%;background:repeating-linear-gradient(to bottom,transparent 0px,transparent 3px,rgba(0,0,0,.15) 3px,rgba(0,0,0,.15) 4px);z-index:20;}}
.ui{{position:absolute;top:0;left:0;width:1920px;height:1080px;z-index:10;display:flex;flex-direction:column;align-items:center;justify-content:center;}}
.corner{{position:absolute;width:36px;height:36px;}}
.corner--tl{{top:48px;left:48px;border-top:1px solid rgba({rgb},.4);border-left:1px solid rgba({rgb},.4);}}
.corner--tr{{top:48px;right:48px;border-top:1px solid rgba({rgb},.4);border-right:1px solid rgba({rgb},.4);}}
.corner--bl{{bottom:48px;left:48px;border-bottom:1px solid rgba({rgb},.4);border-left:1px solid rgba({rgb},.4);}}
.corner--br{{bottom:48px;right:48px;border-bottom:1px solid rgba({rgb},.4);border-right:1px solid rgba({rgb},.4);}}
.sig-lost{{font-size:11px;letter-spacing:8px;color:rgba({rgb},.3);margin-bottom:48px;text-transform:uppercase;}}
.main-msg{{font-size:48px;letter-spacing:8px;color:rgba({rgb},.85);text-shadow:0 0 30px rgba({rgb},.4);text-align:center;animation:glitch 8s ease-in-out infinite;}}
@keyframes glitch{{0%,90%,100%{{transform:translate(0,0)}}91%{{transform:translate(-3px,1px)}}92%{{transform:translate(3px,-1px)}}93%{{transform:translate(0,0)}}}}
.cursor{{display:inline-block;width:28px;height:4px;background:rgba({rgb},.7);vertical-align:middle;margin-left:10px;animation:cb 1s step-end infinite;}}
@keyframes cb{{0%,100%{{opacity:1}}50%{{opacity:0}}}}
.status{{margin-top:36px;font-size:13px;letter-spacing:5px;color:rgba({rgb},.4);text-align:center;min-height:20px;transition:opacity .5s;}}
.meter{{margin-top:56px;display:flex;align-items:center;gap:16px;font-size:10px;letter-spacing:4px;color:rgba({rgb},.25);}}
.meter-bars{{display:flex;gap:3px;align-items:flex-end;}}
.meter-bar{{width:5px;background:rgba({rgb},.4);}}
@keyframes mb{{from{{opacity:.15;background:rgba({rgb},.3)}}to{{opacity:.7;background:rgba({rgb},.7)}}}}
.bottom-label{{position:absolute;bottom:56px;left:0;right:0;text-align:center;font-size:10px;letter-spacing:6px;color:rgba({rgb},.2);}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="vignette"></div><div class="scanlines"></div>
<div class="ui">
  <div class="corner corner--tl"></div><div class="corner corner--tr"></div>
  <div class="corner corner--bl"></div><div class="corner corner--br"></div>
  <div class="sig-lost">── SIGNAL INTERRUPTED ──</div>
  <div class="main-msg">{r['brb_main']}<span class="cursor"></span></div>
  <div class="status" id="status"></div>
  <div class="meter">
    <span>SIGNAL</span>
    <div class="meter-bars" id="mbars"></div>
    <span id="spct">──%</span>
  </div>
  <div class="bottom-label">{r['brb_bottom']}</div>
</div>
<script>
const canvas=document.getElementById('c');
const ctx=canvas.getContext('2d');
canvas.width=1920;canvas.height=1080;
let gf=0;
function draw(){{
  const id=ctx.createImageData(1920,1080);const d=id.data;
  for(let i=0;i<d.length;i+=4){{
    const on=Math.random()>.82;const v=on?Math.floor(20+Math.random()*50):0;
    d[i]=Math.floor(v*.3);d[i+1]=Math.floor(v*.6);d[i+2]=v;d[i+3]=on?200:0;
  }}
  ctx.putImageData(id,0,0);
  if(gf>0){{gf--;const y=Math.floor(Math.random()*1080);const h=Math.floor(Math.random()*12)+2;
    try{{const seg=ctx.getImageData(0,y,1920,h);ctx.putImageData(seg,Math.floor((Math.random()-.5)*60),y);}}catch(e){{}}}}
  requestAnimationFrame(draw);
}}
draw();
setInterval(()=>{{if(Math.random()<.3)gf=Math.floor(Math.random()*8)+3;}},2000);
const msgs={msgs_js};
let si=0;const stEl=document.getElementById('status');
function cycle(){{stEl.style.opacity=0;setTimeout(()=>{{stEl.textContent=msgs[si%msgs.length];stEl.style.opacity=1;si++;}},400);}}
cycle();setInterval(cycle,3500);
const mb=document.getElementById('mbars');
[4,6,10,14,18,14,10,6,4].forEach((h,i)=>{{
  const b=document.createElement('div');b.className='meter-bar';b.style.height=h+'px';
  b.style.animation=`mb ${{(.4+Math.random()*.6).toFixed(2)}}s ease-in-out ${{(i*.06).toFixed(2)}}s infinite alternate`;
  mb.appendChild(b);
}});
const sp=document.getElementById('spct');
let sv=8+Math.random()*15;
setInterval(()=>{{sv+=(Math.random()-.5)*8;sv=Math.max(0,Math.min(35,sv));sp.textContent=Math.floor(sv)+'%';}},500);
</script>
</body>
</html>'''


def lower_third_html(r):
    c = r['color']; rgb = r['rgb']
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{r['name']} - ローワーサード</title>
<!--
  OBS設定: ブラウザソース → このHTMLを指定 → 幅1920 高さ1080
  名前変更: ファイル内の '名前' と 'KYOUKAI' を書き換えてください
-->
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;background:transparent;overflow:hidden;font-family:'Courier New',monospace;}}
.lt{{position:absolute;bottom:72px;left:72px;display:flex;align-items:center;gap:0;animation:slideIn .8s cubic-bezier(.16,1,.3,1) both;}}
@keyframes slideIn{{from{{transform:translateY(30px);opacity:0}}to{{transform:translateY(0);opacity:1}}}}
.accent{{width:3px;height:72px;background:linear-gradient(to bottom,transparent,{c},transparent);margin-right:20px;flex-shrink:0;}}
.texts{{display:flex;flex-direction:column;gap:6px;}}
.name{{font-size:38px;letter-spacing:4px;color:rgba(255,255,255,.92);line-height:1;}}
.title-row{{display:flex;align-items:center;gap:12px;}}
.title-label{{font-size:11px;letter-spacing:5px;color:{c};text-transform:uppercase;}}
.title-sep{{width:24px;height:1px;background:rgba({rgb},.4);}}
.title-text{{font-size:11px;letter-spacing:3px;color:rgba({rgb},.6);text-transform:uppercase;}}
.right-block{{position:absolute;bottom:72px;right:72px;display:flex;align-items:center;gap:14px;animation:slideIn .8s .1s cubic-bezier(.16,1,.3,1) both;}}
.live-dot{{width:7px;height:7px;border-radius:50%;background:{c};box-shadow:0 0 8px {c};animation:blink 1.4s ease-in-out infinite;}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.1}}}}
.live-label{{font-size:10px;letter-spacing:5px;color:rgba({rgb},.5);}}
.mini-bars{{display:flex;gap:2px;align-items:flex-end;}}
.mini-bar{{width:3px;background:rgba({rgb},.5);}}
@keyframes mb{{from{{opacity:.2}}to{{opacity:.8}}}}
.line{{position:absolute;bottom:55px;left:72px;right:72px;height:1px;background:rgba({rgb},.12);overflow:hidden;}}
.line::after{{content:'';position:absolute;top:0;left:-40%;width:40%;height:100%;background:linear-gradient(to right,transparent,rgba({rgb},.6),transparent);animation:scan 4s linear infinite;}}
@keyframes scan{{from{{left:-40%}}to{{left:100%}}}}
</style>
</head>
<body>
<div class="lt">
  <div class="accent"></div>
  <div class="texts">
    <div class="name" id="name-el">名前</div>
    <div class="title-row">
      <div class="title-label">{r['lt_label']}</div>
      <div class="title-sep"></div>
      <div class="title-text" id="title-el">KYOUKAI</div>
    </div>
  </div>
</div>
<div class="right-block">
  <div class="mini-bars" id="mbars"></div>
  <div class="live-dot"></div>
  <div class="live-label">受信中</div>
</div>
<div class="line"></div>
<script>
const p=new URLSearchParams(window.location.search);
document.getElementById('name-el').textContent=p.get('name')||'名前';
document.getElementById('title-el').textContent=p.get('title')||'KYOUKAI';
const mb=document.getElementById('mbars');
[6,9,13,9,6,9,13].forEach((h,i)=>{{
  const b=document.createElement('div');b.className='mini-bar';b.style.height=h+'px';
  b.style.animation=`mb ${{(.3+Math.random()*.5).toFixed(2)}}s ease-in-out ${{(i*.05).toFixed(2)}}s infinite alternate`;
  mb.appendChild(b);
}});
</script>
</body>
</html>'''


def readme_txt(r):
    return f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {r['name']} OBS素材パック  /  KYOUKAI
  {r['brb_bottom']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【同梱内容】3点

  01_waiting / waiting.html
    待機画面。{r['label']}。
    配信前・ゲームロード中・場面転換に。

  02_brb / brb.html
    離席中画面。「{r['brb_main']}」のメッセージ。
    離席・準備中・一時中断に。

  03_lower-third / lower_third.html
    ローワーサード（名前テロップ）。透過背景。
    他の素材の上に重ねてオーバーレイとして使用。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【OBS設定方法】

  1. OBS Studio を開く
  2. ソース → ＋ → ブラウザ を追加
  3. 「ローカルファイル」にチェックを入れる
  4. 各 .html ファイルを指定する
  5. 幅: 1920  /  高さ: 1080 に設定する

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【ローワーサードのカスタマイズ】

  lower_third.html をテキストエディタで開き、
  以下を書き換えてください。

    document.getElementById('name-el').textContent=p.get('name')||'名前';
    → '名前' をあなたの名前に変更

    document.getElementById('title-el').textContent=p.get('title')||'KYOUKAI';
    → 'KYOUKAI' を肩書きや活動名に変更

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【動作環境】

  OBS Studio 29以降推奨
  インターネット接続不要 / 完全ローカル動作

【利用規約】

  個人・商用配信どちらでも使用可
  再配布・転売 禁止
  改変は個人使用の範囲で自由

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  KYOUKAI ─ 境界
  https://kyoukai.vercel.app
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

