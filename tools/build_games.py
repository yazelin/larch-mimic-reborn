# -*- coding: utf-8 -*-
"""繪本小遊戲（手繪水彩版）：從模板產出 book/games/knock.html、apple.html，素材網址取自 assets/media.json。
  python3 tools/build_games.py
敲三下：背景是該場景的 CG（箱爺爺 1-4、阿扣 2-3、小鎖 3-2），點畫面裡睡著的那個寶箱三下就成功，寫 knock_ok，0.9 秒後自動接下一張。
         哪個族人由變數 knock_target 決定（箱爺爺／阿扣／小鎖），播放器在 larch:init 帶進來；沒帶就是箱爺爺。
接蘋果：背景是營地後面的蘋果樹（A-0），左右移動寶箱怪接蘋果 20 秒，寫 apples。"""
import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open(os.path.join(R, 'assets/media.json')))
U = lambda k: M[k]['url']

# 每個族人：背景 CG、要點的寶箱在畫面上的位置（中心 x、y 與寬，百分比；照各張 CG 量的）
TARGETS = {
    '箱爺爺': {'bg': U('book_1-4'), 'x': 62, 'y': 47, 'w': 34, 'tip': '點三下箱爺爺的蓋子', 'ok': '箱爺爺的蓋子動了一下。'},
    '阿扣': {'bg': U('book_2-3'), 'x': 82, 'y': 58, 'w': 22, 'tip': '點三下阿扣的蓋子', 'ok': '阿扣的蓋子動了一下。'},
    '小鎖': {'bg': U('book_3-2'), 'x': 89, 'y': 62, 'w': 14, 'tip': '輕輕點三下小鎖的蓋子', 'ok': '小鎖的蓋子動了一下。'},
}

COMMON_CSS = """
@import url("https://fonts.googleapis.com/css2?family=LXGW+WenKai+TC:wght@400;700&display=swap");
:root{--ink:#5a3f52;--rose:#e0789c;--rose-d:#b9577c;--hand:"LXGW WenKai TC","Huninn","Noto Sans TC",serif}
html,body{margin:0;height:100%;background:#2a1f2a;font-family:var(--hand);overflow:hidden;user-select:none;-webkit-user-select:none;color:var(--ink)}
#fill{position:fixed;inset:-40px;width:calc(100% + 80px);height:calc(100% + 80px);object-fit:cover;filter:blur(24px) brightness(.8);pointer-events:none}
#stage{position:fixed;left:50%;top:50%;translate:-50% -50%;width:min(100vw,177.78vh);aspect-ratio:16/9;overflow:hidden;container-type:size}
#bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.pill{position:absolute;white-space:nowrap;padding:.55em 1.7em;font-size:clamp(13px,4.6cqh,28px);letter-spacing:.08em;
  border-style:solid;border-width:0;border-image:url("__PILL__") 40 60 fill / 12px 18px stretch;filter:drop-shadow(0 5px 8px rgba(90,50,80,.28))}
#tip{left:50%;top:5%;translate:-50% 0;rotate:-.6deg}
#skip{right:2.5%;bottom:3.5%;font:inherit;font-size:clamp(12px,3.4cqh,20px);color:var(--ink);background:none;cursor:pointer;padding:.45em 1.4em}
#skip:hover,#skip:focus-visible{color:var(--rose-d);outline:none}
"""

KNOCK = """<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>敲三下</title>
<style>__COMMON__
#hit{position:absolute;translate:-50% -50%;aspect-ratio:1;cursor:pointer;touch-action:manipulation;border-radius:50%}
#ring{position:absolute;inset:-8%;pointer-events:none;opacity:.85}
#ring circle{fill:none;stroke:#fffaf3;stroke-width:3.2;stroke-linecap:round;filter:url(#rough)}
#ring .c2{stroke-width:1.6;opacity:.6}
.kn{position:absolute;font-weight:700;font-size:clamp(26px,12cqh,78px);color:#fffaf3;pointer-events:none;
  text-shadow:0 0 .05em var(--rose-d),0 .05em .02em var(--rose-d),0 .1em .25em rgba(150,60,100,.55)}
#dots{position:absolute;left:50%;bottom:7%;translate:-50% 0;display:flex;gap:3.8cqh}
#dots b{width:8.5cqh;height:8.5cqh;background:url("__DOT__") center/contain no-repeat;filter:drop-shadow(0 3px 5px rgba(90,50,80,.25));transition:transform .2s}
#dots b.on{background-image:url("__DOT_ON__");transform:scale(1.08)}
#veil{position:absolute;inset:0;background:radial-gradient(60% 60% at 50% 50%,rgba(255,250,240,0),rgba(255,250,240,.0));pointer-events:none;transition:background .5s}
#veil.done{background:radial-gradient(60% 60% at 50% 50%,rgba(255,246,236,.35),rgba(255,246,236,.0))}
</style></head><body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true">
 <filter id="rough"><feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="3" seed="4"/><feDisplacementMap in="SourceGraphic" scale="4"/></filter>
 <filter id="rough-s"><feTurbulence type="fractalNoise" baseFrequency="0.09" numOctaves="2" seed="3"/><feDisplacementMap in="SourceGraphic" scale="3"/></filter>
</svg>
<img id="fill" alt=""><div id="stage"><img id="bg" alt="">
<div id="veil"></div>
<div id="hit" role="button" tabindex="0" aria-label="敲蓋子"><svg id="ring" viewBox="0 0 100 100"><circle cx="50" cy="50" r="44"/><circle class="c2" cx="51" cy="49" r="40"/></svg></div>
<div class="pill" id="tip"></div>
<div id="dots"><b></b><b></b><b></b></div>
<button class="pill" id="skip" type="button">略過</button></div>
<script>
var T=__TARGETS__,cfg=T['箱爺爺'],name='箱爺爺',need=3,hits=0,done=false;
var bg=document.getElementById('bg'),hit=document.getElementById('hit'),ring=document.getElementById('ring'),tip=document.getElementById('tip'),
    dots=[].slice.call(document.querySelectorAll('#dots b')),stage=document.getElementById('stage');
function apply(n){if(T[n]){name=n;cfg=T[n]}bg.src=cfg.bg;document.getElementById('fill').src=cfg.bg;hit.style.left=cfg.x+'%';hit.style.top=cfg.y+'%';hit.style.width=cfg.w+'%';tip.textContent=cfg.tip}
apply('箱爺爺');
ring.animate([{transform:'scale(1)',opacity:.85},{transform:'scale(1.08)',opacity:.45},{transform:'scale(1)',opacity:.85}],{duration:1600,iterations:Infinity});
function knock(){if(done)return;hits++;
 var k=document.createElement('div');k.className='kn';k.textContent='叩！';
 var r=hit.getBoundingClientRect(),sr=stage.getBoundingClientRect();k.style.left=(r.left-sr.left+r.width*(.55+Math.random()*.2))+'px';k.style.top=(r.top-sr.top-r.height*.05)+'px';stage.appendChild(k);
 k.animate([{opacity:0,transform:'translateY(10px) rotate(-8deg) scale(.8)'},{opacity:1,transform:'translateY(-6px) rotate(-8deg) scale(1.05)',offset:.25},{opacity:0,transform:'translateY(-40px) rotate(-8deg)'}],{duration:700}).onfinish=function(){k.remove()};
 bg.animate([{transform:'translate(0,0)'},{transform:'translate(-4px,2px)'},{transform:'translate(3px,-2px)'},{transform:'translate(0,0)'}],{duration:160});
 ring.animate([{transform:'scale(.92)',opacity:1},{transform:'scale(1.45)',opacity:0}],{duration:600});
 dots.forEach(function(b,i){b.classList.toggle('on',i<hits)});
 if(hits>=need)setTimeout(function(){finish(true)},350)}
function finish(ok){if(done&&ok)return;done=true;document.getElementById('veil').classList.add('done');ring.style.display='none';
 tip.textContent=ok?cfg.ok:'';
 parent.postMessage({type:'larch:set',name:'knock_ok',value:!!ok},'*');
 setTimeout(function(){parent.postMessage({type:'larch:complete',result:ok?'woke':'skipped'},'*')},900)}
hit.addEventListener('pointerdown',function(e){e.preventDefault();knock()});
hit.addEventListener('keydown',function(e){if(e.code==='Space'||e.code==='Enter'){e.preventDefault();knock()}});
addEventListener('keydown',function(e){if(e.target===document.body&&(e.code==='Space'||e.code==='Enter')){e.preventDefault();knock()}});
document.getElementById('skip').onclick=function(){finish(false)};
addEventListener('message',function(e){var d=e.data;if(d&&d.type==='larch:init'){var v=d.values||d.variables||{};if(v.knock_target)apply(String(v.knock_target))}});
parent.postMessage({type:'larch:ready'},'*');
</script></body></html>"""

APPLE = """<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>接蘋果</title>
<style>__COMMON__
#hud{left:50%;top:4%;translate:-50% 0}
#mimic{position:absolute;bottom:3%;width:16%;translate:-50% 0;filter:drop-shadow(0 8px 6px rgba(60,40,30,.3));pointer-events:none}
.ap{position:absolute;width:5.2%;translate:-50% -50%;pointer-events:none;filter:drop-shadow(0 3px 3px rgba(0,0,0,.18))}
.plus{position:absolute;font-weight:700;font-size:clamp(20px,9cqh,56px);color:#fffaf3;pointer-events:none;
  text-shadow:0 0 .05em var(--rose-d),0 .05em .02em var(--rose-d),0 .1em .25em rgba(150,60,100,.55)}
#start{left:50%;top:50%;translate:-50% -50%;font:inherit;font-size:clamp(15px,6cqh,34px);color:#fff;background:none;cursor:pointer;
  border-image:url("__HOT__") 60 80 fill / 14px 20px stretch;text-shadow:0 0 .35em rgba(150,40,80,.45);padding:.6em 2em}
#start[hidden]{display:none}
#help{left:50%;top:64%;translate:-50% 0;font-size:clamp(12px,3.6cqh,22px)}
#help[hidden]{display:none}
</style></head><body>
<img id="fill" src="__BG__" alt=""><div id="stage"><img id="bg" src="__BG__" alt="">
<div class="pill" id="hud">接到 0 顆・剩 20 秒</div>
<img id="mimic" src="__MIMIC__" alt="寶箱怪">
<button class="pill" id="start" type="button">開始接蘋果</button>
<div class="pill" id="help">滑鼠、手指左右移動，或按 ← →</div>
<button class="pill" id="skip" type="button">略過</button></div>
<script>
var stage=document.getElementById('stage'),mimic=document.getElementById('mimic'),hud=document.getElementById('hud'),APPLE='__APPLE__';
var x=50,keys={},apples=[],got=0,left=20,running=false,last=0,spawnT=0;
function place(){mimic.style.left=x+'%'}place();
function setX(clientX){var r=stage.getBoundingClientRect();x=Math.max(8,Math.min(92,(clientX-r.left)/r.width*100));place()}
document.addEventListener('pointermove',function(e){if(running)setX(e.clientX)});
document.addEventListener('pointerdown',function(e){if(running)setX(e.clientX)});
addEventListener('keydown',function(e){keys[e.code]=true});addEventListener('keyup',function(e){keys[e.code]=false});
function spawn(){var a=document.createElement('img');a.src=APPLE;a.className='ap';var o={el:a,x:10+Math.random()*80,y:-6,v:22+Math.random()*16};
 a.style.left=o.x+'%';a.style.top=o.y+'%';stage.appendChild(a);apples.push(o)}
function plus(px){var p=document.createElement('div');p.className='plus';p.textContent='+1';p.style.left=px+'%';p.style.top='68%';p.style.translate='-50% 0';stage.appendChild(p);
 p.animate([{opacity:1,transform:'translateY(0)'},{opacity:0,transform:'translateY(-50px)'}],{duration:650}).onfinish=function(){p.remove()}}
function tick(t){if(!running)return;var dt=Math.min(.05,(t-last)/1000||0);last=t;left-=dt;
 if(keys.ArrowLeft||keys.KeyA){x=Math.max(8,x-60*dt);place()}if(keys.ArrowRight||keys.KeyD){x=Math.min(92,x+60*dt);place()}
 spawnT-=dt;if(spawnT<=0){spawn();spawnT=.55+Math.random()*.4}
 for(var i=apples.length-1;i>=0;i--){var o=apples[i];o.y+=o.v*dt;o.el.style.top=o.y+'%';
  if(o.y>82&&o.y<92&&Math.abs(o.x-x)<7){got++;plus(o.x);mimic.animate([{transform:'scaleY(1)'},{transform:'scaleY(.9)'},{transform:'scaleY(1)'}],{duration:180});o.el.remove();apples.splice(i,1)}
  else if(o.y>104){o.el.remove();apples.splice(i,1)}}
 hud.textContent='接到 '+got+' 顆・剩 '+Math.max(0,Math.ceil(left))+' 秒';
 if(left<=0)return end();requestAnimationFrame(tick)}
function end(){running=false;apples.forEach(function(o){o.el.remove()});apples=[];hud.textContent='接到 '+got+' 顆！';
 parent.postMessage({type:'larch:set',name:'apples',value:got},'*');setTimeout(function(){parent.postMessage({type:'larch:complete',result:String(got)},'*')},1200)}
document.getElementById('start').onclick=function(){this.hidden=true;document.getElementById('help').hidden=true;running=true;last=performance.now();requestAnimationFrame(tick)};
document.getElementById('skip').onclick=function(){if(running){left=0}else{parent.postMessage({type:'larch:set',name:'apples',value:0},'*');parent.postMessage({type:'larch:complete',result:'0'},'*')}};
parent.postMessage({type:'larch:ready'},'*');
</script></body></html>"""

common = COMMON_CSS.replace('__PILL__', U('ui_pill'))
os.makedirs(os.path.join(R, 'book/games'), exist_ok=True)
open(os.path.join(R, 'book/games/knock.html'), 'w').write(
    KNOCK.replace('__COMMON__', common).replace('__DOT__', U('ui_dot')).replace('__DOT_ON__', U('ui_dot_on')).replace('__TARGETS__', json.dumps(TARGETS, ensure_ascii=False)))
open(os.path.join(R, 'book/games/apple.html'), 'w').write(
    APPLE.replace('__COMMON__', common).replace('__HOT__', U('ui_pill_hot')).replace('__BG__', U('book_A-0'))
    .replace('__MIMIC__', U('sprite_mimic_open')).replace('__APPLE__', U('sprite_apple')))
for f in ('knock', 'apple'):
    print(f, os.path.getsize(os.path.join(R, f'book/games/{f}.html')))
