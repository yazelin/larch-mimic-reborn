# -*- coding: utf-8 -*-
"""回憶 CG 選圖頁：把 art/cg/mem{1,2,3}{a,b}_v<n>.webp 縮成 1200 寬嵌進 HTML，輸出到指定路徑。
  python3 tools/pick_page.py 輸出.html
"""
import base64, glob, io, json, os, sys
from PIL import Image
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ITEMS = [
 ('mem1', '回憶 CG 1〈醒來的第一天〉', '寶箱怪在村口翻倒，長老把它扶正。', [
   '寶箱怪：醒來的第一天，我想站起來，才發現自己沒有腳。',
   '寶箱怪：能動的只有蓋子。蓋子一開一闔，身體就往前蹦一下。',
   '寶箱怪：我在村口翻倒了好幾次，最後是一個老爺爺把我扶正的。',
   '長老：你是剛醒的吧？島上的寶箱，有一半是你們一族。']),
 ('mem2', '回憶 CG 2〈第一次吃東西〉', '兔子湊近鎖扣聞，蓋子正要闔上。', [
   '寶箱怪：第三天，我開始覺得肚子餓。',
   '寶箱怪：一隻兔子跑過來聞我的鎖扣，我嚇了一跳，蓋子一闔，牠就不見了。',
   '寶箱怪：有點毛毛的，可是很飽。']),
 ('mem3', '回憶 CG 3〈明天再來〉', '黃昏，寶箱怪用蓋子敲一個睡著的族人。', [
   '寶箱怪：後來我把島上的寶箱一個一個找出來。每一個都是族人，每一個都在睡覺。',
   '寶箱怪：我每天去敲，一個敲三下。叫不醒，我就說一聲「明天再來」。',
   '寶箱怪：白天在村口曬太陽，晚上到海邊看海。就這樣過了一整個夏天。']),
]
ITEMS_APPLE = [
 ('mem2apple', '回憶 CG 2〈第一次吃東西〉蘋果版', '蘋果樹下，寶箱怪掀著蓋子發呆，一顆蘋果正要掉進箱子裡。兔子版不用了。', [
   '寶箱怪：第三天，我開始覺得肚子餓。',
   '寶箱怪：我在樹下張著蓋子發呆，一顆蘋果掉下來，剛好掉進箱子裡。',
   '寶箱怪：我嚇了一跳，蓋子一闔。……很甜。']),
]

def latest(name):
    fs = sorted(glob.glob(os.path.join(R, f'art/cg/{name}_v*.webp')), key=lambda f: int(f.rsplit('_v', 1)[1].split('.')[0]))
    return fs[-1] if fs else None

def uri(path):
    im = Image.open(path).convert('RGB'); im.thumbnail((1200, 1200)); b = io.BytesIO(); im.save(b, 'WEBP', quality=84)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

def card(key, title, desc, lines):
    opts = ''
    for v in 'ab':
        p = latest(key + v)
        lab = v.upper()
        img = f'<img src="{uri(p)}" alt="{title} {lab} 版" loading="lazy">' if p else '<div class="missing">這一版沒畫出來</div>'
        opts += f'<figure class="opt" data-v="{v}">{img}<figcaption><button type="button" class="pick" id="pick-{key}-{v}" data-k="{key}" data-v="{v}">選 {lab} 版</button></figcaption></figure>'
    ls = ''.join(f'<li>{l}</li>' for l in lines)
    return f'''<section class="cg" id="{key}">
<header><h2>{title}</h2><p class="desc">{desc}</p></header>
<ol class="lines">{ls}</ol>
<div class="opts">{opts}</div>
<div class="row"><button type="button" class="pick redo" id="pick-{key}-redo" data-k="{key}" data-v="redo">兩版都不行，重畫</button>
<span class="state" id="state-{key}">還沒選</span></div>
<label class="note-l" for="note-{key}">想改的地方（可以不寫）</label>
<textarea id="note-{key}" data-k="{key}" rows="2" placeholder="例如：長老的帽子顏色不對、寶箱怪的眼睛太小"></textarea>
</section>'''

HTML = '''<title>寶箱怪回憶 CG</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
/* 版面：單欄，每張 CG 一段；上面台詞、中間兩版並排、下面選擇與留言 */
:root{--bg:#fbf3ee;--surface:#fffaf6;--ink:#3b2a3f;--muted:#7d6a80;--accent:#d9577a;--accent-ink:#fff;--line:#ecd9de;--sel:#f6d5df;
--display:"Zen Maru Gothic","Noto Sans TC",system-ui,sans-serif;--body:"Noto Sans TC",system-ui,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#231a27;--surface:#2e2333;--ink:#f3e6ee;--muted:#b6a2b8;--accent:#f07c9c;--accent-ink:#2a1420;--line:#463849;--sel:#4a2c3b;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#231a27;--surface:#2e2333;--ink:#f3e6ee;--muted:#b6a2b8;--accent:#f07c9c;--accent-ink:#2a1420;--line:#463849;--sel:#4a2c3b;color-scheme:dark}
body{background:var(--bg);color:var(--ink);font-family:var(--body);font-size:15px;line-height:1.7;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:24px 48px}
main{max-width:1080px;margin:0 auto;display:flex;flex-direction:column;gap:32px}
h1{font-family:var(--display);font-size:1.7rem;margin:0;text-wrap:balance}
.intro p{margin:.4em 0;color:var(--muted);max-width:65ch}
.cg{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:20px;display:flex;flex-direction:column;gap:14px}
.cg h2{font-family:var(--display);font-size:1.25rem;margin:0}
.desc{margin:0;color:var(--muted)}
.lines{margin:0;padding-left:1.2em;color:var(--ink)}
.opts{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:14px}
.opt{margin:0;border:3px solid transparent;border-radius:14px;padding:6px;display:flex;flex-direction:column;gap:8px;min-width:0}
.opt img{border-radius:9px;display:block;width:100%;height:auto;cursor:zoom-in}
.opt.on{border-color:var(--accent);background:var(--sel)}
.missing{aspect-ratio:3/2;display:grid;place-items:center;color:var(--muted);border:1px dashed var(--line);border-radius:9px}
button.pick{font:inherit;font-weight:700;border:2px solid var(--accent);color:var(--accent);background:transparent;border-radius:999px;padding:6px 18px;cursor:pointer}
button.pick.on{background:var(--accent);color:var(--accent-ink)}
button.pick:focus-visible,textarea:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.row{display:flex;flex-wrap:wrap;gap:12px;align-items:center}
.state{color:var(--muted);font-size:.9rem}
.note-l{font-size:.9rem;color:var(--muted)}
textarea{font:inherit;color:var(--ink);background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:8px 10px;width:100%;box-sizing:border-box;resize:vertical}
#zoom{position:fixed;inset:0;background:rgba(20,10,20,.88);display:grid;place-items:center;padding:16px;z-index:20;cursor:zoom-out}
#zoom img{max-height:94vh;border-radius:8px}
.offline{color:var(--accent);font-weight:700}
</style>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@700&family=Noto+Sans+TC:wght@400;700&display=swap">
<main>
<div class="intro"><h1>轉生成寶箱怪的我：回憶 CG</h1>
<p>__INTRO__</p>
<p>點圖可以放大。</p><p class="offline" id="offline" hidden>這個畫面存不了選擇，請直接在對話裡告訴我。</p></div>
__CARDS__
</main>
<div id="zoom" hidden><img alt="放大的圖"></div>
<script>
(async()=>{
const z=document.getElementById('zoom');
document.querySelectorAll('.opt img').forEach(i=>i.onclick=()=>{z.querySelector('img').src=i.src;z.hidden=false});
z.onclick=()=>z.hidden=true;
const show=(k,v)=>{document.querySelectorAll(`#${k} .pick`).forEach(b=>b.classList.toggle('on',b.dataset.v===v));
 document.querySelectorAll(`#${k} .opt`).forEach(o=>o.classList.toggle('on',o.dataset.v===v));
 document.getElementById('state-'+k).textContent=v==='redo'?'已存：重畫':v?`已存：${v.toUpperCase()} 版`:'還沒選'};
const db=await claude.use('db');
if(!db){document.getElementById('offline').hidden=false;return}
const col=db.collection('picks');const cur={};
col.onSnapshot(s=>{s.docs.forEach(d=>{const x=d.data();cur[d.id]=x.choice;show(d.id,x.choice);const t=document.getElementById('note-'+d.id);if(t&&document.activeElement!==t&&x.note!=null)t.value=x.note})},()=>{});
const save=async k=>{const c=cur[k]||null;try{await col.doc(k).set({choice:c,note:document.getElementById('note-'+k).value,at:Date.now()});show(k,c)}catch(e){document.getElementById('state-'+k).textContent='沒存到，請再按一次'}};
document.querySelectorAll('button.pick').forEach(b=>b.onclick=()=>{cur[b.dataset.k]=b.dataset.v;show(b.dataset.k,b.dataset.v);save(b.dataset.k)});
document.querySelectorAll('textarea').forEach(t=>t.onchange=()=>save(t.dataset.k));
})();
</script>'''

out = sys.argv[1]
items = ITEMS_APPLE if 'apple' in sys.argv[2:] else ITEMS
intro = ('吃兔子改成吃蘋果，回憶 CG 2 重畫了兩版。選一版，或按「重畫」並寫下要改的地方。選了就存，不用另外送出。' if items is ITEMS_APPLE
         else '序章新加的三段回憶，每段一張 CG，各畫了兩版。每段選一版，或按「重畫」並寫下要改的地方。選了就存，不用另外送出。')
open(out, 'w').write(HTML.replace('__CARDS__', '\n'.join(card(*i) for i in items)).replace('__INTRO__', intro))
print(out, os.path.getsize(out))
