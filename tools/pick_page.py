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
ITEMS_LORE = [
 ('lorea', 'CG A〈寶箱怪圖鑑〉', '開場科普的第一張：構造。', [
   '旁白：寶箱怪，住在這座島上的一種箱子。外表跟普通的寶箱一模一樣。',
   '旁白：蓋子是寶箱怪的嘴巴，也是腳。蓋子一開一闔，身體就往前蹦一下。',
   '旁白：眼睛長在蓋子和箱身之間的縫裡。蓋子一闔緊，眼睛就藏起來了。',
   '旁白：眼睛後面黑黑的，看不到底。吃進去的果子、青蛙，會在這裡慢慢消化掉。',
   '旁白：別人交給寶箱怪保管的東西，寶箱怪不會消化，會一直收好。只有放東西的那一家人來了，寶箱怪才會自己打開蓋子，把東西還給他們。',
   '旁白：寶箱怪大部分的時間都在睡覺。睡著的時候幾乎不用吃東西，一整年只要幾顆蘋果就夠了。']),
 ('loreb', 'CG B〈一百年前〉', '開場科普的第二張：由來。箱子就是後來轉生的那個，當時還沒有眼睛。', [
   '旁白：寶箱怪是怎麼來的？島上的老人說，一個箱子被人好好用了一百年，就會醒過來。',
   '旁白：島上的人一直把重要的東西放在箱子裡。所以醒過來的寶箱怪，也一直替大家顧著這些東西。',
   '旁白：睡著的寶箱怪，看起來就是一個普通的寶箱。']),
 ('endc', 'CG C〈打開蓋子〉', '尾聲最後一幕：長老敲三下，寶箱怪第一次自己打開蓋子。', [
   '旁白：寶箱怪第一次自己打開了蓋子。',
   '旁白：裡面有一頂舊舊的小藍帽、一封摺好的信、一顆圓圓的白石頭。',
   '長老：……這頂帽子是我小時候戴的。我還以為早就弄丟了。',
   '寶箱怪：……我會繼續幫你們顧著。']),
]
ITEMS_TRIBE = [
 ('tribe', '族人定稿', '繪本版要用的族人長相。左到右：寶箱怪（比例參考）、箱爺爺、阿扣、小鎖。選定後繪本的每張圖都照這張畫。', [
   '箱爺爺：最大最老，深棕色木頭，白青苔像鬍子，粗白眉毛，眼睛瞇著。',
   '阿扣：圓胖，淡藍色布睡帽，眼皮半垂，縫邊冒睡覺泡泡。',
   '小鎖：最小、顏色最淺，心形鎖扣，眼睛大大濕濕的。',
   'A 版：箱爺爺的鬍子長長垂到箱身，小鎖特別小。B 版：四個畫得比較大，箱爺爺鬍子短一點、蓋子掀比較開。']),
]

ITEMS_CH1 = [
 ('b11', '1-1〈長老！〉', '第一章第一張：寶箱怪蹦到長老面前，長老轉過頭。選定後 1-2（長老蹲下來）、1-3（長老指向箱爺爺）都從這張改。', [
   '寶箱怪：長老！',
   '長老：你也看到了吧。早上那幾個外地人，已經撬了市集後面兩箱，大家寄放在裡面的金幣全被拿走了。',
   'A 版：寶箱怪撞到長老身上，長老被推著、瞇眼笑。B 版：寶箱怪蹦在半空，長老嚇一跳轉頭。']),
]
ONE_CH1 = [
 ('b15', '1-5〈天亮了嗎？〉', '從 1-4 改：箱爺爺蓋子掀開一條縫，睡眼。', ['箱爺爺：吵什麼……天亮了嗎？']),
 ('b16', '1-6〈這個聲音〉', '從 1-4 改：箱爺爺眼睛睜大，盯著寶箱怪。', ['箱爺爺：……這個聲音。這陣子每天都有人敲我三下，跟我講天氣、講蘋果。是你吧？']),
 ('b17', '1-7〈很悶吧〉', '從 1-4 改：箱爺爺眼神變溫和。', ['箱爺爺：一個人醒著，很悶吧。']),
 ('b18', '1-8〈誰敢拿？〉', '從 1-4 改：蓋子「碰」一聲闔上，氣呼呼。', ['箱爺爺：我身上收的，是村子裡好幾代人交給我顧的東西，誰敢拿？']),
 ('b19', '1-9〈蓋子砸地〉', '從 1-4 改：箱爺爺跳起來，蓋子往地上一砸，塵土飛起來。', ['箱爺爺：往地上用力一砸，旁邊的人都站不穩。']),
]

ONE_CH1B = [
 ('b12', '1-2〈長老蹲下來〉', '從 1-1 B 改：長老蹲到跟寶箱怪一樣高，表情認真。', ['長老：你的族人睡得太沉，被撬開都不會醒。去把他們叫起來。']),
 ('b13', '1-3〈箱爺爺在那邊〉', '從 1-1 B 改：長老指向路牌旁邊的老寶箱。寶箱怪沒有轉頭去看，是臉朝前；要它轉頭就按重畫。', ['長老：箱爺爺就在村口告示牌旁邊。營地跟遺跡也各有一個。']),
]
ITEMS_MAP = [
 ('bm1', 'M-1〈井〉', '島上地圖的回憶：第一次在井的水面看到自己。', ['寶箱怪：我第一次看到自己的樣子，就是在這口井的水面上。', '箱爺爺：我第一次照這口井的時候，還以為自己是一個便當盒。'], 'ab'),
 ('bm2', 'M-2〈火堆〉', '長老把怕火的寶箱怪往後挪。第一次畫成往火的方向推，已經重畫；地上的拖痕是從火堆那邊過來的。長老身體往箱子傾，如果你看起來還是像在推，就按重畫。', ['寶箱怪：我說我是木頭做的，怕火。長老笑了很久，然後把我往後挪了一點。', '箱爺爺：他小時候也這樣挪過我。他們一家都這樣。'], 'cd'),
 ('bm3', 'M-3〈市集的貓〉', '貓睡在蓋子上，寶箱怪一動也不敢動。', ['寶箱怪：我怕吵醒牠，一動也不敢動，結果等到天黑牠才走。'], 'ab'),
 ('bm4', 'M-4〈岩縫〉', '下雨天躲在岩縫，對著裡面沒醒的族人講話。', ['寶箱怪：裡面那箱族人一直沒醒。我就對著他講話，講到雨停。'], 'ab'),
 ('bm5', 'M-5〈池塘〉', '劇本是翻過來、肚子朝天漂著。兩版都比較像泡在水裡；A 版鎖扣在下面，算是翻過來。兩版都不像就按重畫。', ['寶箱怪：木頭會浮，所以我沒沉下去，只是翻過來，肚子朝天漂了一個下午。', '寶箱怪：一隻青蛙跳到我身上，我就翻回來了。'], 'ab'),
 ('bm6', 'M-6〈風車〉', '風車底下午睡，葉片的影子晃過去。B 版眼睛閉著、影子掃在身上。', ['寶箱怪：葉片的影子一下一下晃過去，比數羊還好睡。', '箱爺爺：……下次換我睡那裡。'], 'ab'),
]

ITEMS_CH2 = [
 ('bm1', 'M-1〈井〉重畫', '你問「這不是箱爺吧?」：改成主角和箱爺爺一起照井，水面映出兩個箱子。', ['寶箱怪：紅色的箱子，一雙眼睛。我盯著看了很久，才相信那是我。', '箱爺爺：我第一次照這口井的時候，還以為自己是一個便當盒。'], 'cd'),
 ('bm2', 'M-2〈火堆〉重畫', '照你說的：長老站在火堆那邊，背對火，把寶箱怪往外推。', ['寶箱怪：我說我是木頭做的，怕火。長老笑了很久，然後把我往後挪了一點。'], 'ef'),
 ('b21', '2-1〈市集老闆〉', '第二章第一張。老闆在 3D 裡的樣子拍不到（被攤子擋住），照長老那套方塊小人畫成女老闆：髮髻、綠圍裙。腳邊是被撬開的空錢箱。', ['市集老闆：那兩個獵人連我攤子底下的錢箱都翻了。', '市集老闆：以前你天天擋在我攤子前面曬太陽，害我少做好幾筆生意。現在換你去顧大家了。'], 'ab'),
 ('b22', '2-2〈營地〉', '火焰飛龍在火堆旁打盹，被撬開的空箱，隔壁是睡著的阿扣。選定後 2-3～2-6（阿扣翻身、醒來、肚子餓、吃飽）都從這張改。', ['旁白：營地裡，火焰飛龍趴在火堆旁打盹。旁邊有一個寶箱，蓋子被撬開了，裡面空空的。', '箱爺爺：被撬開的這箱還在睡。睡著被撬，連自己少了什麼都不知道。'], 'ab'),
 ('b27', '2-7〈整箱衝撞〉', '阿扣從坡上滾下來撞在樹上，蘋果掉了一地；主角和箱爺爺在坡頂看。', ['阿扣：我睡覺翻身都會滾下坡。你試試看，整個箱子撞過去。', '旁白：寶箱怪學會了「整箱衝撞」。'], 'ab'),
]

ITEMS_CH34 = [
 ('b31', '3-1〈遺跡入口〉', '入口的大石頭被炸開，碎石散一地、還冒著煙。', ['旁白：遺跡入口的大石頭被炸開了，碎石散了一地。', '箱爺爺：連石頭都炸，這些人真的什麼都敢。'], 'ab'),
 ('b32', '3-2〈小鎖〉', '小鎖縮在角落發抖。選定後 3-2b～3-6（嚇得更緊、掀開一條縫、望向高台、阿扣和箱爺爺互看、示範闔蓋子）都從這張改。', ['旁白：遺跡最裡面的角落，有一個寶箱縮成一團，蓋子抖個不停。', '箱爺爺：小鎖膽子小，敲輕一點。'], 'ab'),
 ('b37', '3-7〈三個族人都醒了〉', '四個寶箱並排站在陽光裡。', ['旁白：三個族人都醒了。', '箱爺爺：上去之前，我們一起敲三下，嚇他們一跳。'], 'ab'),
 ('b43', '4-3〈騎火焰飛龍〉', '從高空往下看整座島。A 版龍背上只看得到三個，少了阿扣；B 版四個都在，但小鎖眼睛睜著（劇本是闔緊不敢看，選 B 的話我再改一次讓小鎖闔眼）。', ['旁白：火焰飛龍拍了兩下翅膀，整座島一下子變得好小。', '小鎖：（蓋子闔得緊緊的）我、我不看。'], 'ab'),
]

ONE_CH5 = [
 ('b52', '5-2〈第一回合〉', '從你選的高台圖改：少年舉著撬棍衝過來。', ['少年獵人：別動，讓我撬一下就好！']),
 ('b53', '5-3〈第二回合〉', '少女甩出繩子想套住寶箱怪。', ['少女獵人：綁起來帶回船上！']),
 ('b54', '5-4〈第三回合〉', '兩個獵人一起撲過來。', ['少年獵人：一起上！']),
 ('b5y2', '招式〈蓋子砸地〉', '主角砸地，獵人站不穩。（第一輪模型讓箱爺爺做動作，已重畫）', ['少女獵人：哇、地在晃！']),
 ('b5u2', '招式〈整箱衝撞〉', '主角撞過去，撬棍飛出去。', ['少年獵人：我的撬棍！']),
 ('b5i2', '招式〈躲進蓋子〉', '主角闔緊蓋子，撬棍敲上去彈開。', ['少年獵人：好硬……手好麻。']),
 ('b5o', '招式〈敲三下〉', '四個寶箱一起敲，獵人摀住耳朵跌坐。', ['旁白：叩、叩、叩。四個寶箱一起敲下去，整座高台都在響。']),
 ('b55', '5-5〈投降〉', '兩個獵人坐在地上舉手。', ['少女獵人：等一下，不打了。我們投降。', '少年獵人：錢都在船上，我們還。']),
 ('b56', '5-6〈Pulut〉', 'Pulut 從門邊探出頭。', ['Pulut：……我不是他們的。']),
 ('b572', '5-7〈我剛醒的時候也是這樣〉', '主角和 Pulut 面對面，左上角疊著長老扶起寶箱怪的回憶。', ['寶箱怪：（那時候，是長老把我扶起來的。）', '寶箱怪：我們幫你想辦法回去。']),
 ('b58', '5-8〈卡雅〉', '更正：繪本草稿寫「走出一隻狐狸」是我寫錯，看到模型代號 sw-fox 就猜是狐狸；3D 裡卡雅是女孩（粉紅頭髮、藍披風），這張照 3D 畫，劇本也改成「走出一個女孩」。', ['旁白：雲端之門後面，走出一個女孩。是住在門邊的卡雅。', '卡雅：雲端之門有一條縫。軟軟的身體擠得過去。', '卡雅：Pulut，你回得去。']),
]

def card_one(key, title, desc, lines):
    p = latest(key)
    img = f'<img src="{uri(p)}" alt="{title}" loading="lazy">' if p else '<div class="missing">沒畫出來</div>'
    ls = ''.join(f'<li>{l}</li>' for l in lines)
    return f'''<section class="cg" id="{key}">
<header><h2>{title}</h2><p class="desc">{desc}</p></header>
<ol class="lines">{ls}</ol>
<div class="opts"><figure class="opt" data-v="ok">{img}</figure></div>
<div class="row"><button type="button" class="pick" id="pick-{key}-ok" data-k="{key}" data-v="ok">這張可以</button>
<button type="button" class="pick redo" id="pick-{key}-redo" data-k="{key}" data-v="redo">要重畫</button>
<span class="state" id="state-{key}">還沒選</span></div>
<label class="note-l" for="note-{key}">想改的地方（可以不寫）</label>
<textarea id="note-{key}" data-k="{key}" rows="2" placeholder="例如：鬍子太長、眉毛方向不對"></textarea>
</section>'''

def latest(name):
    fs = sorted(glob.glob(os.path.join(R, f'art/cg/{name}_v*.webp')), key=lambda f: int(f.rsplit('_v', 1)[1].split('.')[0]))
    return fs[-1] if fs else None

def uri(path):
    im = Image.open(path).convert('RGB'); im.thumbnail((1200, 1200)); b = io.BytesIO(); im.save(b, 'WEBP', quality=84)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

def card(key, title, desc, lines, vs='ab'):
    opts = ''
    for v in vs:
        p = latest(key + v)
        lab = 'AB'[vs.index(v)]
        img = f'<img src="{uri(p)}" alt="{title} {lab} 版" loading="lazy">' if p else '<div class="missing">這一版沒畫出來</div>'
        opts += f'<figure class="opt" data-v="{lab.lower()}">{img}<figcaption><button type="button" class="pick" id="pick-{key}-{lab.lower()}" data-k="{key}" data-v="{lab.lower()}">選 {lab} 版</button></figcaption></figure>'
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
 document.getElementById('state-'+k).textContent=v==='redo'?'已存：重畫':v==='ok'?'已存：這張可以':v?`已存：${v.toUpperCase()} 版`:'還沒選'};
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
if 'ch2' in sys.argv[2:]:
    cards = [card(*i) for i in ITEMS_CH2 + ITEMS_CH34] + [card_one(*i) for i in ONE_CH5]
    intro = '上半：地圖回憶重畫的兩張、第二到四章的主圖，各兩版，選一版。下半：第五章十張，都從你在草圖選的高台圖改出來，每張按「這張可以」或「要重畫」。選了就存，不用另外送出。'
    open(out, 'w').write(HTML.replace('__CARDS__', '\n'.join(cards)).replace('__INTRO__', intro)); print(out, os.path.getsize(out)); sys.exit()
if 'map' in sys.argv[2:]:
    cards = [card_one(*i) for i in ONE_CH1B] + [card(*i) for i in ITEMS_MAP]
    intro = '第一章 1-2、1-3（從你選的 1-1 B 改出來），以及島上地圖的六段回憶。單張的按「這張可以」或「要重畫」，兩版的選一版。選了就存，不用另外送出。'
    open(out, 'w').write(HTML.replace('__CARDS__', '\n'.join(cards)).replace('__INTRO__', intro)); print(out, os.path.getsize(out)); sys.exit()
if 'ch1' in sys.argv[2:]:
    cards = [card(*i) for i in ITEMS_CH1] + [card_one(*i) for i in ONE_CH1]
    intro = '繪本第一章的圖。1-1 畫了兩版選一版；1-5 到 1-9 是從你選的 1-4 一次改出來的，每張按「這張可以」或「要重畫」。選了就存，不用另外送出。'
    open(out, 'w').write(HTML.replace('__CARDS__', '\n'.join(cards)).replace('__INTRO__', intro)); print(out, os.path.getsize(out)); sys.exit()
items = ITEMS_TRIBE if 'tribe' in sys.argv[2:] else ITEMS_APPLE if 'apple' in sys.argv[2:] else ITEMS_LORE if 'lore' in sys.argv[2:] else ITEMS
intro = ('繪本版的族人定稿畫了兩版。選一版，或按「重畫」並寫下要改的地方（例如某個族人的配件、大小）。選了就存，不用另外送出。' if items is ITEMS_TRIBE else '開場科普兩張、尾聲一張，各畫了兩版。每張選一版，或按「重畫」並寫下要改的地方。選了就存，不用另外送出。' if items is ITEMS_LORE else '吃兔子改成吃蘋果，回憶 CG 2 重畫了兩版。選一版，或按「重畫」並寫下要改的地方。選了就存，不用另外送出。' if items is ITEMS_APPLE
         else '序章新加的三段回憶，每段一張 CG，各畫了兩版。每段選一版，或按「重畫」並寫下要改的地方。選了就存，不用另外送出。')
open(out, 'w').write(HTML.replace('__CARDS__', '\n'.join(card(*i) for i in items)).replace('__INTRO__', intro))
print(out, os.path.getsize(out))
