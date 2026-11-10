# -*- coding: utf-8 -*-
"""繪本版整頁草圖：真的圖＋黃昏軟糖介面疊上去，作者在頁面上切 A/B、留話（存 db 的 mockups 集合）。
  python3 tools/mock_page.py 輸出.html"""
import base64, io, os, sys, json
from PIL import Image
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def uri(rel, w=1280, fmt='WEBP'):
    im = Image.open(os.path.join(R, rel)); im = im.convert('RGBA' if fmt == 'PNG' or im.mode == 'RGBA' else 'RGB'); im.thumbnail((w, w))
    b = io.BytesIO(); im.save(b, fmt, quality=82); return f'data:image/{fmt.lower()};base64,' + base64.b64encode(b.getvalue()).decode()
A = {k: uri(f'art/cg/{k}_v1.webp') for k in ['bookk1a','bookk1b','bookm1a','bookm1b','bookb1a','bookb1b','booka1']}
SP = {}
for k in ('sprite_mimic_open', 'sprite_apple'):
    p = f'art/sprites/{k}.png'
    if os.path.exists(os.path.join(R, p)): SP[k] = uri(p, 420, 'PNG')
MAP_SPOTS = {  # 地點標籤位置（百分比），兩版圖各自量
 'a': [('井',39,66,1),('火堆',52,73,0),('市集的貓',60,64,0),('岩縫',48,8,0),('池塘',79,47,0),('風車',74,12,0),('出發去營地',27,34,2)],
 'b': [('井',52,66,1),('火堆',59,72,0),('市集的貓',68,63,0),('岩縫',58,8,0),('池塘',80,45,0),('風車',80,10,0),('出發去營地',26,36,2)]}
def spots(v):
    out = ''
    for name, x, y, kind in MAP_SPOTS[v]:
        cls = 'spot seen' if kind == 1 else 'spot go' if kind == 2 else 'spot'
        out += f'<span class="{cls}" style="left:{x}%;top:{y}%">{"<i class=chk></i>" if kind==1 else ""}{name}</span>'
    return out
SCREENS = [
 ('knock', '敲三下', '第一章：寶箱怪站在睡著的箱爺爺面前。每點一下畫面輕輕震一下、跳出「叩」、下面亮一顆；點滿三下換成箱爺爺睜眼那張（1-5），再進對話。',
  {'a': A['bookk1a'], 'b': A['bookk1b']},
  '''<div class="pill top">點三下蓋子，叫醒箱爺爺</div>
<div class="ring" style="left:62%;top:42%"></div><div class="ring r2" style="left:62%;top:42%"></div>
<div class="knock" style="left:66%;top:16%">叩！</div>
<div class="dots"><b class="on"></b><b class="on"></b><b></b></div>
<div class="pill skip">略過</div>'''),
 ('map', '島上的回憶（地圖）', '插曲：點地點看回憶，看過的打勾、變淡；「出發去營地」是粉紅色，按了就接第二章。地點與標籤位置照圖上的建築擺。',
  {'a': A['bookm1a'], 'b': A['bookm1b']}, None),
 ('apple', '接蘋果', '第二章：阿扣肚子餓。左右移動寶箱怪、張開蓋子接蘋果，20 秒。接到時跳「+1」，上面是軟糖計分泡泡。',
  {'a': A['booka1']}, None),
 ('battle', '高台選招式', '第五章：三回合，每回合先演獵人的動作再選招式；第三回合才出現「敲三下」（粉紅色、最強）。選了換那一招的 CG 與台詞。',
  {'a': A['bookb1a'], 'b': A['bookb1b']},
  '''<div class="choices">
<button class="ch"><span class="key">Y</span>蓋子砸地<small>旁邊的人都站不穩</small></button>
<button class="ch"><span class="key">U</span>整箱衝撞<small>整個箱子撞過去</small></button>
<button class="ch"><span class="key">I</span>躲進蓋子<small>闔緊蓋子，撬棍敲不進來</small></button>
<button class="ch big"><span class="key">O</span>敲三下<small>四個寶箱一起敲</small></button></div>
<div class="dlg"><span class="name">寶箱怪</span>第 3 回合：要用哪一招？</div>'''),
]
def apple_overlay():
    m = f'<img class="mimic" src="{SP["sprite_mimic_open"]}" alt="寶箱怪">' if 'sprite_mimic_open' in SP else '<div class="mimic ph">寶箱怪小圖畫好後放這裡</div>'
    ap = SP.get('sprite_apple')
    apples = ''.join(f'<img class="ap" style="left:{x}%;top:{y}%;width:{w}%" src="{ap}" alt="">' for x, y, w in [(30,30,5),(55,48,5.5),(72,22,5),(41,64,5.5)]) if ap else ''
    return f'<div class="pill top">接到 7 顆・剩 12 秒</div>{apples}<div class="plus" style="left:44%;top:60%">+1</div>{m}'
def stage(key, imgs, overlay):
    first = sorted(imgs)[0]
    ov = {'map': lambda: '<div class="dlg"><span class="name">寶箱怪</span>要去哪裡看看？</div>', 'apple': apple_overlay}.get(key, lambda: overlay)()
    layers = ''.join(f'<div class="art" data-v="{v}" {"hidden" if v != first else ""}><img src="{src}" alt="">{spots(v) if key=="map" else ""}</div>' for v, src in sorted(imgs.items()))
    return f'<div class="stage">{layers}<div class="ov">{ov}</div></div>'
cards = ''
for key, title, desc, imgs, overlay in SCREENS:
    tog = ''.join(f'<button type="button" class="tog" id="tog-{key}-{v}" data-k="{key}" data-v="{v}">{v.upper()} 版圖</button>' for v in sorted(imgs)) if len(imgs) > 1 else ''
    cards += f'''<section class="card" id="{key}"><header><h2>{title}</h2><p>{desc}</p></header>{stage(key, imgs, overlay)}
<div class="row">{tog}<button type="button" class="tog ok" id="ok-{key}" data-k="{key}" data-v="ok">這樣可以</button><span class="state" id="st-{key}">還沒回覆</span></div>
<label for="note-{key}">想改的地方</label><textarea id="note-{key}" data-k="{key}" rows="2" placeholder="例如：標籤太小、計分泡泡移到右上、這張圖改用 B 版"></textarea></section>'''
HTML = '''<title>繪本整頁草圖</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Huninn&family=Noto+Sans+TC:wght@400;700&display=swap">
<style>
/* 版面：單欄；每個互動一張 16:9 舞台，真的圖＋黃昏軟糖介面疊上去，下面切 A/B 與留話 */
:root{--bg:#fbf3ee;--surface:#fffaf6;--ink:#4a3560;--dim:#7b6696;--line:#ecd9de;--pink:#ff8fb1;--pink-d:#d9688c;--lav:#a98ce0;--lav-d:#7a56aa;--glass:rgba(255,246,252,.88);--ui:"Huninn","Noto Sans TC",system-ui,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#231a27;--surface:#2e2333;--ink:#f3e6ee;--dim:#c2aed0;--line:#463849;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#231a27;--surface:#2e2333;--ink:#f3e6ee;--dim:#c2aed0;--line:#463849;color-scheme:dark}
body{background:var(--bg);color:var(--ink);font-family:"Noto Sans TC",system-ui,sans-serif;line-height:1.7;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:24px 56px}
main{max-width:1100px;margin:0 auto;display:flex;flex-direction:column;gap:34px}
h1{font-family:var(--ui);font-size:1.7rem;margin:0}.intro p{color:var(--dim);margin:.3em 0;max-width:65ch}
.card{background:var(--surface);border:1px solid var(--line);border-radius:20px;padding:18px;display:flex;flex-direction:column;gap:12px}
.card h2{font-family:var(--ui);margin:0;font-size:1.25rem}.card header p{margin:.2em 0 0;color:var(--dim)}
.stage{position:relative;width:100%;aspect-ratio:16/9;max-width:100%;border-radius:12px;overflow:hidden;container-type:inline-size;background:#000}
.art,.art img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.ov{position:absolute;inset:0;pointer-events:none;font-family:var(--ui);color:#4a3560}
.pill{position:absolute;background:rgba(255,246,252,.92);border-radius:999px;padding:.35em 1.2em;font-size:2.1cqw;box-shadow:0 .35cqw 0 rgba(122,86,170,.35),inset 0 0 0 .25cqw #fff;letter-spacing:.06em;white-space:nowrap}
.pill.top{left:50%;top:4%;translate:-50% 0}.pill.skip{right:3%;bottom:4%;font-size:1.5cqw;opacity:.85}
.ring{position:absolute;width:30cqw;aspect-ratio:1;border-radius:50%;border:.5cqw solid #fff;translate:-50% -50%;box-shadow:0 0 2cqw #fff,inset 0 0 1.5cqw #fff8;opacity:.9}.ring.r2{width:38cqw;opacity:.35}
.knock{position:absolute;font-size:5cqw;font-weight:900;color:#fff;text-shadow:0 .4cqw 0 var(--pink-d),0 0 1.5cqw #fff;rotate:-8deg}
.dots{position:absolute;left:50%;bottom:6%;translate:-50% 0;display:flex;gap:1.6cqw}.dots b{width:3.4cqw;aspect-ratio:1;border-radius:50%;background:rgba(255,246,252,.6);box-shadow:inset 0 0 0 .3cqw #fff,0 .3cqw 0 rgba(122,86,170,.35)}.dots b.on{background:var(--pink)}
.spot{position:absolute;translate:-50% -50%;background:rgba(255,246,252,.94);border-radius:999px;padding:.25em .95em;font-family:var(--ui);font-size:1.7cqw;color:#4a3560;box-shadow:0 .3cqw 0 rgba(122,86,170,.4),inset 0 0 0 .22cqw #fff;white-space:nowrap;display:flex;align-items:center;gap:.35em}
.spot.seen{opacity:.62}.spot.go{background:var(--pink);color:#fff;box-shadow:0 .35cqw 0 var(--pink-d),inset 0 0 0 .22cqw #fff8;font-size:1.9cqw}
.chk{width:.8em;height:.45em;border-left:.22em solid var(--lav-d);border-bottom:.22em solid var(--lav-d);rotate:-45deg;translate:0 -.15em;display:inline-block}
.dlg{position:absolute;left:6%;right:6%;bottom:5%;background:var(--glass);border-radius:2.8cqw;padding:2.2cqw 3cqw 2.4cqw;font-size:2cqw;letter-spacing:.04em;box-shadow:0 .5cqw 1.5cqw rgba(74,53,96,.18)}
.dlg .name{position:absolute;left:2.4cqw;top:-1.7cqw;background:var(--pink);color:#fff;border-radius:999px;padding:.15em 1.1em;font-size:1.5cqw;box-shadow:0 .3cqw 0 var(--pink-d)}
.choices{position:absolute;left:4%;top:9%;width:40%;display:flex;flex-direction:column;gap:1.3cqw}
.ch{all:unset;display:flex;align-items:center;gap:1.2cqw;background:rgba(255,246,252,.93);border-radius:999px;padding:1cqw 2cqw;font-family:var(--ui);font-size:2cqw;color:#4a3560;box-shadow:0 .4cqw 0 rgba(122,86,170,.35),inset 0 0 0 .25cqw #fff}
.ch small{font-size:1.35cqw;color:#7b6696;margin-left:auto}.ch.big{background:var(--pink);color:#fff;box-shadow:0 .45cqw 0 var(--pink-d),inset 0 0 0 .25cqw #fff8}.ch.big small{color:#fff}
.key{display:inline-grid;place-items:center;width:2.8cqw;aspect-ratio:1;border-radius:.7cqw;background:var(--lav);color:#fff;font-size:1.5cqw;box-shadow:0 .25cqw 0 var(--lav-d)}
.ch.big .key{background:#fff;color:var(--pink-d);box-shadow:0 .25cqw 0 #ffd2df}
.mimic{position:absolute;left:38%;bottom:4%;width:17%;filter:drop-shadow(0 .6cqw .4cqw rgba(60,40,30,.25))}.mimic.ph{background:#fff8;border-radius:1cqw;padding:2cqw;font-size:1.4cqw;text-align:center}
.ap{position:absolute;filter:drop-shadow(0 .3cqw .3cqw rgba(0,0,0,.15))}
.plus{position:absolute;font-size:3.4cqw;font-weight:900;color:#fff;text-shadow:0 .35cqw 0 var(--pink-d)}
.row{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.tog{font:inherit;font-weight:700;border:2px solid var(--lav);color:var(--lav-d);background:transparent;border-radius:999px;padding:5px 16px;cursor:pointer}
.tog.on{background:var(--lav);color:#fff}.tog.ok{border-color:var(--pink);color:var(--pink-d)}.tog.ok.on{background:var(--pink);color:#fff}
.tog:focus-visible,textarea:focus-visible{outline:3px solid var(--pink);outline-offset:2px}
.state{color:var(--dim);font-size:.9rem}label{font-size:.9rem;color:var(--dim)}
textarea{font:inherit;color:var(--ink);background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:8px 10px;width:100%;box-sizing:border-box}
.off{color:var(--pink-d);font-weight:700}
</style>
<main><div class="intro"><h1>繪本整頁草圖</h1>
<p>四種互動用繪本真的會用的圖，疊上「黃昏軟糖」介面排出來的樣子。有兩版圖的可以切換看；整體可以就按「這樣可以」，想改哪裡寫在下面，選了就存。</p>
<p>這是靜態的樣子，不會動。敲三下的光圈、蘋果掉落、打中的特效，做的時候才加。</p><p class="off" id="off" hidden>這個畫面存不了回覆，請直接在對話裡告訴我。</p></div>
__CARDS__</main>
<script>
(async()=>{
const show=(k,art,ok)=>{document.querySelectorAll('#'+k+' .art').forEach(a=>a.hidden=a.dataset.v!==art&&document.querySelectorAll('#'+k+' .art').length>1);
 document.querySelectorAll('#'+k+' .tog').forEach(b=>b.classList.toggle('on',(b.dataset.v==='ok')?!!ok:b.dataset.v===art));
 document.getElementById('st-'+k).textContent=(ok?'已存：這樣可以':'已存')+(art?'（'+art.toUpperCase()+' 版圖）':'')};
const cur={};
document.querySelectorAll('.card').forEach(c=>{const k=c.id;const arts=[...c.querySelectorAll('.art')];cur[k]={art:arts.length>1?arts[0].dataset.v:'a',ok:false}});
document.querySelectorAll('.tog').forEach(b=>b.addEventListener('click',()=>{const k=b.dataset.k;if(b.dataset.v==='ok')cur[k].ok=!cur[k].ok;else cur[k].art=b.dataset.v;
 document.querySelectorAll('#'+k+' .art').forEach(a=>a.hidden=a.dataset.v!==cur[k].art&&document.querySelectorAll('#'+k+' .art').length>1);
 document.querySelectorAll('#'+k+' .tog').forEach(x=>x.classList.toggle('on',(x.dataset.v==='ok')?cur[k].ok:x.dataset.v===cur[k].art));save(k)}));
document.querySelectorAll('textarea').forEach(t=>t.addEventListener('change',()=>save(t.dataset.k)));
const db=await claude.use('db'); if(!db){document.getElementById('off').hidden=false;return}
const col=db.collection('mockups');
async function save(k){try{await col.doc(k).set({art:cur[k].art,ok:cur[k].ok,note:document.getElementById('note-'+k).value,at:Date.now()});show(k,cur[k].art,cur[k].ok)}catch(e){document.getElementById('st-'+k).textContent='沒存到，請再按一次'}}
window.save=save;
col.onSnapshot(s=>s.docs.forEach(d=>{const x=d.data();if(!cur[d.id])return;cur[d.id]={art:x.art||cur[d.id].art,ok:!!x.ok};show(d.id,cur[d.id].art,cur[d.id].ok);const t=document.getElementById('note-'+d.id);if(t&&document.activeElement!==t&&x.note!=null)t.value=x.note}),()=>{});
})();
</script>'''
out = sys.argv[1]
open(out, 'w').write(HTML.replace('__CARDS__', cards))
print(out, os.path.getsize(out), 'sprites', list(SP))
