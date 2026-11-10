# -*- coding: utf-8 -*-
"""繪本 UI 風格比較頁：同一張 CG、同一份介面結構，分別套「現行（黃昏軟糖）」「水彩 A（純 CSS）」「水彩 B（手繪素材）」。
作者在頁面上選一種、留話（存 db 的 uistyle 集合）。
  python3 tools/ui_style_page.py 輸出.html"""
import base64, io, os, sys, glob
from PIL import Image
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def uri(rel, w=1280, fmt='WEBP'):
    im = Image.open(os.path.join(R, rel)); im = im.convert('RGBA' if fmt == 'PNG' or im.mode == 'RGBA' else 'RGB'); im.thumbnail((w, w))
    b = io.BytesIO(); im.save(b, fmt, quality=82); return f'data:image/{fmt.lower()};base64,' + base64.b64encode(b.getvalue()).decode()

CG = {k: uri(f'art/cg/{k}_v1.webp') for k in ['b15', 'bookk1b', 'bookm1a', 'bookb1b_pulut']}
# 水彩 B 的素材（去背後的 PNG）；還沒產出就不出 B 欄
KIT = {}
for k in ('ui_panel', 'ui_tag', 'ui_btn', 'ui_btn_hot', 'ui_pill', 'ui_pill_hot'):
    p = f'art/ui/{k}.png'
    if os.path.exists(os.path.join(R, p)): KIT[k] = uri(p, 2000, 'PNG')
HAS_B = len(KIT) == 6

SPOTS = [('井', 39, 66, 1), ('火堆', 52, 73, 0), ('市集的貓', 60, 64, 0), ('岩縫', 48, 8, 0), ('池塘', 79, 47, 0), ('風車', 74, 12, 0), ('出發去營地', 27, 34, 2)]
def spots():
    o = ''
    for n, x, y, k in SPOTS:
        cls = 'spot seen' if k == 1 else 'spot go' if k == 2 else 'spot'
        o += f'<span class="{cls}" style="left:{x}%;top:{y}%">{"<i class=chk></i>" if k == 1 else ""}<em>{n}</em></span>'
    return o

DLG = lambda name, text: f'<div class="dlg"><span class="name"><em>{name}</em></span><p>{text}</p><i class="next"></i></div>'
SCREENS = [
 ('dialogue', '對話', '一般對話卡（1-5）。對話框是全作品共用的，3D 模式也會一起換。', 'b15', DLG('箱爺爺', '吵什麼……天亮了嗎？')),
 ('knock', '敲三下', '互動畫面：上方提示、光圈、「叩！」、下方三顆進度、略過。', 'bookk1b',
  '<div class="pill top"><em>點三下蓋子，叫醒箱爺爺</em></div><div class="ring" style="left:62%;top:42%"></div>'
  '<div class="knock" style="left:66%;top:16%">叩！</div><div class="dots"><b class="on"></b><b class="on"></b><b></b></div><div class="pill skip"><em>略過</em></div>'),
 ('map', '島上地圖', '地點標籤、看過的打勾、「出發去營地」、下方對話。', 'bookm1a', spots() + DLG('寶箱怪', '要去哪裡看看？')),
 ('battle', '高台選招式', '四個選項，第三回合「敲三下」最醒目。', 'bookb1b_pulut',
  '<div class="choices">'
  '<button class="ch"><span class="key">Y</span><em>蓋子砸地</em><small>旁邊的人都站不穩</small></button>'
  '<button class="ch"><span class="key">U</span><em>整箱衝撞</em><small>整個箱子撞過去</small></button>'
  '<button class="ch"><span class="key">I</span><em>躲進蓋子</em><small>闔緊蓋子，撬棍敲不進來</small></button>'
  '<button class="ch big"><span class="key">O</span><em>敲三下</em><small>四個寶箱一起敲</small></button></div>'
  + DLG('寶箱怪', '第 3 回合：要用哪一招？')),
]
STYLES = [('cur', '現行：黃昏軟糖')] + ([('wb', '水彩：手繪水彩素材')] if HAS_B else [('wa', '水彩 A：CSS 畫的水彩紙')])

def stage(style, cg, ov):
    return f'<figure class="opt" data-v="{style}"><div class="stage {style}"><img class="art" src="{CG[cg]}" alt=""><div class="ov">{ov}</div></div></figure>'

cards = ''
for key, title, desc, cg, ov in SCREENS:
    figs = ''.join(f'<div class="col"><h3>{lab}</h3>{stage(s, cg, ov)}</div>' for s, lab in STYLES)
    cards += f'<section class="card" id="{key}"><header><h2>{title}</h2><p>{desc}</p></header><div class="cols">{figs}</div></section>'

picks = ''.join(f'<button type="button" class="tog" data-v="{s}">{lab}</button>' for s, lab in STYLES)

KIT_CSS = ''
if HAS_B:
    # 九宮格：四邊的毛邊照原比例，只伸展中間。切片位置照素材量（像素），顯示寬度用 cqw 換算成同一個縮放比例
    KIT_CSS = f'''
.wb .ov{{font-family:var(--hand);color:#5a3f52}}
.wb .dlg,.wb .pill,.wb .spot,.wb .ch,.wb .dlg .name,.wb .key{{background:none;box-shadow:none;border-radius:0}}
.wb .dlg,.wb .pill,.wb .spot,.wb .ch,.wb .dlg .name{{border-width:0}}
.wb .dlg{{border-style:solid;border-image:url({KIT['ui_panel']}) 170 120 110 230 fill / 4.1cqw 2.9cqw 2.7cqw 5.6cqw stretch;padding:3.2cqw 4.2cqw 3cqw 5.6cqw;font-size:2.15cqw;letter-spacing:.05em;line-height:1.6;filter:drop-shadow(0 .5cqw .9cqw rgba(90,50,80,.2))}}
.wb .dlg .name{{border-style:solid;border-image:url({KIT['ui_tag']}) 80 140 fill / .7em 1.3em stretch;padding:.3em 1.1em;top:-1.9cqw;left:7cqw;color:#fff;font-size:1.6cqw;rotate:-2deg;text-shadow:0 0 .3em rgba(150,40,80,.35)}}
.wb .dlg .next{{border-top-color:#c97a9c}}
.wb .pill,.wb .spot{{border-style:solid;border-image:url({KIT['ui_pill']}) 40 60 fill / .5em .8em stretch;padding:.35em 1.2em}}
.wb .spot.go{{border-image-source:url({KIT['ui_pill_hot']});border-image-slice:60 80 fill;color:#fff;text-shadow:0 0 .3em rgba(150,40,80,.4)}}
.wb .spot.seen{{opacity:.72}}.wb .chk{{border-color:#8a6aa8}}
.wb .spot:nth-child(2n){{rotate:1.5deg}}.wb .spot:nth-child(2n+1){{rotate:-1.5deg}}
.wb .choices{{gap:1.4cqw}}
.wb .ch{{height:5cqw;box-sizing:border-box;border-style:solid;border-image:url({KIT['ui_btn']}) 40 60 40 200 fill / 1cqw 1.5cqw 1cqw 5cqw stretch;padding:0 2.2cqw 0 5cqw;gap:1.4cqw}}
.wb .ch.big{{border-image:url({KIT['ui_btn_hot']}) 60 80 60 300 fill / 1.05cqw 1.4cqw 1.05cqw 5.2cqw stretch;padding-left:5.2cqw;color:#fff;text-shadow:0 0 .3em rgba(150,40,80,.4)}}
.wb .ch:nth-child(2){{rotate:.5deg}}.wb .ch:nth-child(3){{rotate:-.4deg}}.wb .ch.big{{rotate:-.8deg}}
.wb .key{{width:3cqw;margin-left:-3.7cqw;color:#6a4a9a;font-family:var(--hand);font-weight:700;font-size:1.8cqw}}
.wb .ch.big .key{{margin-left:-3.35cqw;color:#d9688c}}
.wb .ch small{{color:#8a6f88}}.wb .ch.big small{{color:#fff5f8}}
.wb .dots b{{background:radial-gradient(circle at 45% 40%,#fffaf1 0 55%,#f3dde8 80%,#ddb8d4 100%);box-shadow:none;filter:url(#rough-s)}}
.wb .dots b.on{{background:radial-gradient(circle at 45% 40%,#ffb7cb 0 45%,#f590ae 72%,#c95f86 100%)}}
.wb .ring{{border:.3cqw solid rgba(255,250,240,.92);box-shadow:none;filter:url(#rough)}}
.wb .knock{{font-family:var(--hand);font-weight:700;color:#fff8ef;text-shadow:0 0 .15cqw #c75f86,0 .2cqw .5cqw rgba(150,60,100,.55)}}'''

HTML = '''<title>繪本介面風格</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Huninn&family=LXGW+WenKai+TC:wght@400;700&family=Noto+Sans+TC:wght@400;700&display=swap">
<style>
/* 版面：單欄；每種畫面一段，段內三種風格並排（窄螢幕直排）。最下面選一種、留話 */
:root{--bg:#fbf3ee;--surface:#fffaf6;--ink:#4a3560;--dim:#7b6696;--line:#ecd9de;--pink:#ff8fb1;--pink-d:#d9688c;--lav:#a98ce0;--lav-d:#7a56aa;
--ui:"Huninn","Noto Sans TC",system-ui,sans-serif;--hand:"LXGW WenKai TC","Huninn","Noto Sans TC",serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#231a27;--surface:#2e2333;--ink:#f3e6ee;--dim:#c2aed0;--line:#463849;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#231a27;--surface:#2e2333;--ink:#f3e6ee;--dim:#c2aed0;--line:#463849;color-scheme:dark}
body{background:var(--bg);color:var(--ink);font-family:"Noto Sans TC",system-ui,sans-serif;line-height:1.7;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:24px 56px}
main{max-width:1500px;margin:0 auto;display:flex;flex-direction:column;gap:30px}
h1{font-family:var(--ui);font-size:1.7rem;margin:0;text-wrap:balance}.intro p{color:var(--dim);margin:.3em 0;max-width:70ch}
.card{background:var(--surface);border:1px solid var(--line);border-radius:20px;padding:18px;display:flex;flex-direction:column;gap:12px}
.card h2{font-family:var(--ui);margin:0;font-size:1.2rem}.card header p{margin:.1em 0 0;color:var(--dim)}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,380px),1fr));gap:14px}.col{min-width:0}
.col h3{margin:0 0 6px;font-size:.95rem;font-weight:700;color:var(--dim)}
.opt{margin:0}
.stage{position:relative;width:100%;aspect-ratio:16/9;max-width:100%;border-radius:10px;overflow:hidden;container-type:inline-size;background:#000;cursor:zoom-in}
.art{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.ov{position:absolute;inset:0;pointer-events:none;font-family:var(--ui);color:#4a3560}
.ov em{font-style:normal;position:relative}
[hidden]{display:none!important}
#zoom{position:fixed;inset:0;background:rgba(20,10,20,.9);display:grid;place-items:center;padding:16px;z-index:20;cursor:zoom-out}
#zoom .stage{width:min(96vw,170vh);cursor:zoom-out}

/* ===== 現行：黃昏軟糖 ===== */
.pill{position:absolute;background:rgba(255,246,252,.92);border-radius:999px;padding:.35em 1.2em;font-size:2.1cqw;box-shadow:0 .35cqw 0 rgba(122,86,170,.35),inset 0 0 0 .25cqw #fff;letter-spacing:.06em;white-space:nowrap}
.pill.top{left:50%;top:4%;translate:-50% 0}.pill.skip{right:3%;bottom:4%;font-size:1.5cqw;opacity:.85}
.ring{position:absolute;width:30cqw;aspect-ratio:1;border-radius:50%;border:.5cqw solid #fff;translate:-50% -50%;box-shadow:0 0 2cqw #fff,inset 0 0 1.5cqw #fff8;opacity:.9}
.knock{position:absolute;font-size:5cqw;font-weight:900;color:#fff;text-shadow:0 .4cqw 0 var(--pink-d),0 0 1.5cqw #fff;rotate:-8deg}
.dots{position:absolute;left:50%;bottom:6%;translate:-50% 0;display:flex;gap:1.6cqw}.dots b{width:3.4cqw;aspect-ratio:1;border-radius:50%;background:rgba(255,246,252,.6);box-shadow:inset 0 0 0 .3cqw #fff,0 .3cqw 0 rgba(122,86,170,.35)}.dots b.on{background:var(--pink)}
.spot{position:absolute;translate:-50% -50%;background:rgba(255,246,252,.94);border-radius:999px;padding:.25em .95em;font-size:1.7cqw;color:#4a3560;box-shadow:0 .3cqw 0 rgba(122,86,170,.4),inset 0 0 0 .22cqw #fff;white-space:nowrap;display:flex;align-items:center;gap:.35em}
.spot.seen{opacity:.62}.spot.go{background:var(--pink);color:#fff;box-shadow:0 .35cqw 0 var(--pink-d),inset 0 0 0 .22cqw #fff8;font-size:1.9cqw}
.chk{width:.8em;height:.45em;border-left:.22em solid var(--lav-d);border-bottom:.22em solid var(--lav-d);rotate:-45deg;translate:0 -.15em;display:inline-block}
.dlg{position:absolute;left:6%;right:6%;bottom:5%;background:rgba(255,246,252,.88);border-radius:2.8cqw;padding:2.2cqw 3cqw 2.4cqw;font-size:2cqw;letter-spacing:.04em;box-shadow:0 .5cqw 1.5cqw rgba(74,53,96,.18)}
.dlg p{margin:0;position:relative}
.dlg .name{position:absolute;left:2.4cqw;top:-1.7cqw;background:var(--pink);color:#fff;border-radius:999px;padding:.15em 1.1em;font-size:1.5cqw;box-shadow:0 .3cqw 0 var(--pink-d)}
.dlg .next{position:absolute;right:2.6cqw;bottom:1.4cqw;width:0;height:0;border-left:.7cqw solid transparent;border-right:.7cqw solid transparent;border-top:.9cqw solid var(--pink-d)}
.choices{position:absolute;left:4%;top:9%;width:40%;display:flex;flex-direction:column;gap:1.3cqw}
.ch{all:unset;display:flex;align-items:center;gap:1.2cqw;background:rgba(255,246,252,.93);border-radius:999px;padding:1cqw 2cqw;font-size:2cqw;color:#4a3560;box-shadow:0 .4cqw 0 rgba(122,86,170,.35),inset 0 0 0 .25cqw #fff;position:relative}
.ch small{font-size:1.35cqw;color:#7b6696;margin-left:auto;position:relative}.ch.big{background:var(--pink);color:#fff;box-shadow:0 .45cqw 0 var(--pink-d),inset 0 0 0 .25cqw #fff8}.ch.big small{color:#fff}
.key{display:inline-grid;place-items:center;width:2.8cqw;aspect-ratio:1;border-radius:.7cqw;background:var(--lav);color:#fff;font-size:1.5cqw;box-shadow:0 .25cqw 0 var(--lav-d);position:relative;flex:none}
.ch.big .key{background:#fff;color:var(--pink-d);box-shadow:0 .25cqw 0 #ffd2df}

/* ===== 水彩 A：CSS 畫的水彩紙 =====
   紙面與色塊放在 ::before，套 SVG 擾動濾鏡做出手撕毛邊；字留在上層不變形。
   不用硬投影，改成淡淡的暈影；粉紫只刷在紙邊，像水彩往外暈。 */
.wa .ov{font-family:var(--hand);color:#5a3f52}
.wa .dlg,.wa .pill,.wa .spot,.wa .ch,.wa .dlg .name,.wa .key{background:none;box-shadow:none;border-radius:0}
.wa .dlg::before,.wa .pill::before,.wa .spot::before,.wa .ch::before,.wa .dlg .name::before,.wa .key::before{content:"";position:absolute;inset:0;z-index:-1;filter:url(#rough)}
.wa .dlg,.wa .pill,.wa .spot,.wa .ch,.wa .dlg .name,.wa .paper::before,.wa .dlg::before,.wa .pill::before,.wa .spot::before,.wa .ch::before{
 background:var(--grain),radial-gradient(120% 140% at 50% 45%,#fffaf1 0 58%,#f8e6ee 80%,#ecc9df 96%,#dcb2d2 100%);
 box-shadow:0 0 0 .12cqw rgba(176,120,160,.45),0 .6cqw 1.4cqw rgba(110,60,90,.16)}
.wa .dlg{padding:2.6cqw 3.6cqw 2.8cqw;font-size:2.15cqw;letter-spacing:.05em;line-height:1.6}
.wa .dlg .name{top:-2cqw;left:3cqw;padding:.25em 1.3em;font-size:1.6cqw;color:#fff;rotate:-2deg}
.wa .dlg .name::before,.wa .spot.go::before,.wa .ch.big::before,.wa .dots b.on{
 background:var(--grain),radial-gradient(130% 160% at 40% 40%,#ffb7cb 0 45%,#f590ae 72%,#e0789c 90%,#c95f86 100%);box-shadow:0 .4cqw .9cqw rgba(160,60,100,.22)}
.wa .dlg .next{border-top-color:#c97a9c;filter:url(#rough-s)}
.wa .pill{padding:.45em 1.5em}.wa .pill.top{rotate:-.6deg}
.wa .spot{padding:.3em 1.05em}.wa .spot:nth-child(2n){rotate:1.5deg}.wa .spot:nth-child(2n+1){rotate:-1.5deg}
.wa .spot.go{color:#fff}.wa .spot.seen{opacity:.7}
.wa .chk{border-color:#8a6aa8;filter:url(#rough-s)}
.wa .choices{gap:1.5cqw}
.wa .ch{padding:1.15cqw 2.4cqw 1.15cqw 1.6cqw}.wa .ch:nth-child(2){rotate:.5deg}.wa .ch:nth-child(3){rotate:-.4deg}
.wa .ch small{color:#8a6f88}.wa .ch.big{color:#fff;rotate:-.8deg}.wa .ch.big small{color:#fff5f8}
.wa .key{color:#fff;font-size:1.7cqw}
.wa .key::before{background:radial-gradient(circle at 45% 40%,#bba2e6 0 50%,#9b7fd2 80%,#7a5cb4 100%)}
.wa .ch.big .key{color:#d9688c}.wa .ch.big .key::before{background:radial-gradient(circle,#fffaf1 0 60%,#ffe2ea 100%)}
.wa .key>*{position:relative}
.wa .dots b{background:radial-gradient(circle at 45% 40%,#fffaf1 0 55%,#f3dde8 80%,#ddb8d4 100%);box-shadow:none;filter:url(#rough-s)}
.wa .ring{border:.3cqw solid rgba(255,250,240,.92);box-shadow:none;filter:url(#rough)}
.wa .knock{font-family:var(--hand);font-weight:700;color:#fff8ef;text-shadow:0 0 .15cqw #c75f86,0 .2cqw .5cqw rgba(150,60,100,.55)}
__KIT_CSS__

.pickbar{position:sticky;bottom:0;background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:14px 16px;display:flex;flex-direction:column;gap:10px;box-shadow:0 -6px 20px rgba(60,30,60,.08)}
.row{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.tog{font:inherit;font-weight:700;border:2px solid var(--lav);color:var(--lav-d);background:transparent;border-radius:999px;padding:5px 16px;cursor:pointer}
.tog.on{background:var(--lav);color:#fff}
.tog:focus-visible,textarea:focus-visible{outline:3px solid var(--pink);outline-offset:2px}
.state{color:var(--dim);font-size:.9rem}label{font-size:.9rem;color:var(--dim)}
textarea{font:inherit;color:var(--ink);background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:8px 10px;width:100%;box-sizing:border-box}
.off{color:var(--pink-d);font-weight:700}
</style>
<svg width="0" height="0" style="position:absolute" aria-hidden="true">
 <filter id="rough" x="-10%" y="-30%" width="120%" height="160%"><feTurbulence type="fractalNoise" baseFrequency="0.045" numOctaves="3" seed="7"/><feDisplacementMap in="SourceGraphic" scale="7" xChannelSelector="R" yChannelSelector="G"/></filter>
 <filter id="rough-s" x="-20%" y="-20%" width="140%" height="140%"><feTurbulence type="fractalNoise" baseFrequency="0.09" numOctaves="2" seed="3"/><feDisplacementMap in="SourceGraphic" scale="3"/></filter>
</svg>
<main><div class="intro"><h1>繪本介面風格</h1>
<p>同一張 CG、同一份介面結構，只換樣式。左邊是現在的「黃昏軟糖」，右邊是水彩版本。點圖可以放大。</p>
<p>__B_NOTE__</p>
<p class="off" id="off" hidden>這個畫面存不了回覆，請直接在對話裡告訴我。</p></div>
__CARDS__
<div class="pickbar"><div class="row"><strong>要用哪一種？</strong>__PICKS__<span class="state" id="st">還沒選</span></div>
<label for="note">想改的地方（可以不寫）</label><textarea id="note" rows="2" placeholder="例如：紙邊再毛一點、名牌改紫色、字再大一點"></textarea></div>
</main>
<div id="zoom" hidden></div>
<script>
const z=document.getElementById('zoom');
document.querySelectorAll('.opt .stage').forEach(s=>s.onclick=()=>{z.innerHTML='';z.appendChild(s.cloneNode(true));z.hidden=false});
z.onclick=()=>z.hidden=true;
(async()=>{
let cur=null;const st=document.getElementById('st'),note=document.getElementById('note');
const show=v=>{document.querySelectorAll('.pickbar .tog').forEach(b=>b.classList.toggle('on',b.dataset.v===v));st.textContent=v?'已存：'+document.querySelector('.pickbar .tog[data-v="'+v+'"]').textContent:'還沒選'};
const db=await claude.use('db');if(!db){document.getElementById('off').hidden=false;return}
const doc=db.collection('uistyle').doc('pick');
const save=async()=>{try{await doc.set({choice:cur,note:note.value,at:Date.now()});show(cur)}catch(e){st.textContent='沒存到，請再按一次'}};
document.querySelectorAll('.pickbar .tog').forEach(b=>b.onclick=()=>{cur=b.dataset.v;show(cur);save()});
note.onchange=save;
doc.onSnapshot(d=>{const x=d.data&&d.data();if(!x)return;cur=x.choice;show(cur);if(document.activeElement!==note&&x.note!=null)note.value=x.note},()=>{});
})();
</script>'''

GRAIN = "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='3' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 .45  0 0 0 0 .3  0 0 0 0 .4  0 0 0 .09 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>\")"
out = sys.argv[1]
html = (HTML.replace('__CARDS__', cards).replace('__PICKS__', picks).replace('__KIT_CSS__', KIT_CSS)
        .replace('__B_NOTE__', '水彩版用產圖模型畫的水彩紙卡、名牌色塊、選項色帶，去背後當介面底圖；四邊的毛邊照原比例，只拉長中間。字換成手寫感的楷體（霞鶩文楷）。用 CSS 硬做水彩紙的版本也試過，邊緣看起來還是方的，沒有放上來。' if HAS_B else '')
        .replace(':root{--bg', ':root{--grain:' + GRAIN + ';--bg', 1))
open(out, 'w').write(html)
print(out, os.path.getsize(out), 'B' if HAS_B else 'no B')
