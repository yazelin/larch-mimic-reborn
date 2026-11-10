# -*- coding: utf-8 -*-
"""公開站（GitHub Pages，repo 根目錄）：產生 index.html 與 site/img/。
圖：繪本 CG 取自 art/book/（選圖對照 art/book/selection.json）、族人定稿取自 art/refs/、標題主視覺與序章 CG 從 Larch 媒體庫抓回本機（assets/media.json）。
配樂直接用 assets/audio/。頁尾三件套用 promo-footer skill 套上。
  python3 tools/build_site.py
文字規則：照實寫，「我」只用在作者真的做的事；引號只放查得到的原話。"""
import json, os, urllib.request
from PIL import Image
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(R, 'site/img')
os.makedirs(IMG, exist_ok=True)
M = json.load(open(os.path.join(R, 'assets/media.json')))
MARKET = 'https://larch.ink/play/market/12cc23dc-9e1b-428b-9067-0c79d3d32071'
REPO = 'https://github.com/yazelin/larch-mimic-reborn'

def save(src, name, w=1400):
    out = os.path.join(IMG, name + '.webp')
    im = Image.open(src).convert('RGBA' if name.startswith('ui_') or name.startswith('c_') else 'RGB')
    im.thumbnail((w, w)); im.save(out, quality=82, method=6)
    return f'site/img/{name}.webp'

def fetch(key, name, w=1600):
    tmp = os.path.join(IMG, f'_{name}.src')
    if not os.path.exists(tmp):
        req = urllib.request.Request(M[key]['url'], headers={'User-Agent': 'Mozilla/5.0'})
        open(tmp, 'wb').write(urllib.request.urlopen(req, timeout=120).read())
    p = save(tmp, name, w); os.remove(tmp); return p

KV = fetch('kv_title_v3', 'kv', 1920)  # 遊戲 titleCoverImage 用的是 v3；v1 獵人臉是糊的
LORE = fetch('cg_lore_a', 'lore', 1400)
OPEN = fetch('cg_opening', 'opening', 1400)
SHOT3D = save(os.path.join(R, 'art/screenshots/4-wake-grandpa.webp'), 'shot_3d', 1400)
BOOK = lambda k, w=1400: save(os.path.join(R, f'art/book/{k}.webp'), 'b_' + k.replace('-', '_'), w)
UI = {k: save(os.path.join(R, f'art/ui/{k}.png'), k, 2000) for k in ('ui_panel', 'ui_tag', 'ui_pill', 'ui_pill_hot')}
CAST = [
    ('寶箱怪', 'art/refs/tribe_mimic.webp', '長老家倉庫裡用了一百年的箱子，醒過來變成寶箱怪。整個夏天島上只有它醒著，每天去敲族人的蓋子，一個敲三下。'),
    ('箱爺爺', 'art/refs/tribe_grandpa.webp', '村口最老的寶箱，白青苔像鬍子。身上收著村子裡好幾代人交給他顧的東西。'),
    ('阿扣', 'art/refs/tribe_akou.webp', '營地的寶箱，睡最熟，戴一頂淡藍色睡帽。睡覺翻身會滾下坡。'),
    ('小鎖', 'art/refs/tribe_xiaosuo.webp', '遺跡裡最小的寶箱，心形鎖扣，膽子很小。害怕的時候就把蓋子闔緊。'),
]
CAST_IMG = [(n, save(os.path.join(R, p), 'c_' + str(i), 700), t) for i, (n, p, t) in enumerate(CAST)]
GALLERY = [
    ('1-1', '寶箱怪', '長老！'),
    ('1-7', '箱爺爺', '一個人醒著，很悶吧。'),
    ('M-3', '寶箱怪', '我怕吵醒牠，一動也不敢動，結果等到天黑牠才走。'),
    ('M-5', '寶箱怪', '木頭會浮，所以我沒沉下去，只是翻過來，肚子朝天漂了一個下午。'),
    ('2-3', '旁白', '阿扣就在隔壁，蓋子跟著打呼一起一伏。'),
    ('2-7', '阿扣', '我睡覺翻身都會滾下坡。你試試看，整個箱子撞過去。'),
    ('3-3', '小鎖', '（蓋子抖個不停）走、走了嗎？'),
    ('3-5', '箱爺爺', '會講話的箱子，就算人。'),
    ('4-3', '小鎖', '（蓋子闔得緊緊的）我、我不看。'),
    ('5-O', '旁白', '叩、叩、叩。四個寶箱一起敲下去，整座高台都在響。'),
    ('5-7', '寶箱怪', '（那時候，是長老把我扶起來的。）'),
    ('5-8', '卡雅', 'Pulut，找到你了。'),
]
GAL = [(BOOK(k, 1200), sp, tx, k) for k, sp, tx in GALLERY]
MODE_BOOK = BOOK('1-5')
MUSIC = [('標題', 'bgm-title'), ('序章', 'bgm-opening'), ('島上探索', 'bgm-explore'), ('高台對決', 'bgm-battle'), ('尾聲', 'bgm-ending')]

gal_html = '\n'.join(f'''<figure class="frame"><img src="{src}" alt="繪本 {k}" loading="lazy" width="1200" height="800">
<figcaption><span class="who">{sp}</span>{tx}</figcaption></figure>''' for src, sp, tx, k in GAL)
cast_html = '\n'.join(f'''<article class="who-card"><img src="{src}" alt="{n}" loading="lazy"><h3>{n}</h3><p>{t}</p></article>''' for n, src, t in CAST_IMG)
music_html = '\n'.join(f'''<li><span>{n}</span><audio controls preload="none" src="assets/audio/{f}.mp3"></audio></li>''' for n, f in MUSIC)

HTML = f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>轉生成寶箱怪的我</title>
<meta name="description" content="Larch 第四屆創作者挑戰作品。轉生成一個用了一百年的箱子，叫醒睡著的族人，把上島搶東西的冒險隊趕走。可以在 3D 小島上走，也可以翻開手繪繪本讀完整個故事。">
<meta property="og:title" content="轉生成寶箱怪的我"><meta property="og:image" content="https://yazelin.github.io/larch-mimic-reborn/{KV}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=LXGW+WenKai+TC:wght@400;700&display=swap">
<style>
:root{{--paper:#fbf3ea;--paper2:#f6e6ec;--ink:#4f3848;--dim:#86708c;--rose:#e0789c;--rose-d:#b9577c;--hand:"LXGW WenKai TC","Noto Serif TC",serif}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;color:var(--ink);font-family:var(--hand);font-size:18px;line-height:1.85;
  background:radial-gradient(120% 80% at 50% 0%,#fffaf2 0,var(--paper) 45%,var(--paper2) 100%)}}
a{{color:var(--rose-d)}}
img{{max-width:100%;height:auto;display:block}}
.wrap{{max-width:1080px;margin:0 auto;padding-inline:max(18px,env(safe-area-inset-left))}}
.hero{{position:relative;min-height:min(86vh,760px);display:grid;align-items:end;overflow:hidden}}
.hero>img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:60% 55%}}
.hero::after{{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(251,243,234,0) 45%,rgba(251,243,234,.92) 92%,var(--paper) 100%)}}
.hero .in{{position:relative;z-index:1;padding-block:0 42px}}
h1{{margin:0;font-size:clamp(40px,7vw,86px);line-height:1.1;color:#fffaf3;letter-spacing:.04em;
  text-shadow:0 0 .04em var(--rose-d),0 0 .04em var(--rose-d),0 .05em .02em var(--rose-d),0 .1em .25em rgba(150,60,100,.55)}}
h1 small{{display:block;font-size:.55em;letter-spacing:.14em}}
.quote{{margin:.6em 0 1.1em;font-size:clamp(18px,2.2vw,24px);color:var(--ink);max-width:36em}}
.btns{{display:flex;flex-wrap:wrap;gap:14px}}
.btn{{display:inline-block;text-decoration:none;color:var(--ink);padding:.6em 1.8em;font-size:19px;letter-spacing:.1em;
  border-style:solid;border-width:0;border-image:url("{UI['ui_pill']}") 40 60 fill / 12px 18px stretch;filter:drop-shadow(0 5px 8px rgba(90,50,80,.22))}}
.btn.hot{{border-image-source:url("{UI['ui_pill_hot']}");border-image-slice:60 80 fill;color:#fff;text-shadow:0 0 .35em rgba(150,40,80,.45)}}
.btn:hover,.btn:focus-visible{{translate:0 -2px}}
section{{padding-block:56px}}
h2{{font-size:clamp(26px,3.4vw,36px);margin:0 0 .7em;letter-spacing:.08em;color:var(--rose-d);text-wrap:balance}}
.panel{{padding:46px 52px 38px 70px;border-style:solid;border-width:0;border-image:url("{UI['ui_panel']}") 170 120 110 230 fill / 60px 42px 38px 80px stretch;
  filter:drop-shadow(0 10px 18px rgba(90,50,80,.16))}}
.panel p{{margin:.4em 0;max-width:40em}}
.modes{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:28px}}
.mode img{{border-radius:6px;box-shadow:0 0 0 6px #fffdf8,0 10px 22px -8px rgba(90,50,80,.4)}}
.mode h3{{margin:.9em 0 .2em;font-size:23px}}
.mode p{{margin:0;color:var(--ink)}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr));gap:26px}}
.frame{{margin:0;background:#fffdf8;padding:9px 9px 14px;box-shadow:0 0 0 1px rgba(176,120,160,.22),0 10px 18px -8px rgba(90,50,80,.35)}}
.frame:nth-child(3n+1){{rotate:-.7deg}}.frame:nth-child(3n+2){{rotate:.5deg}}
.frame figcaption{{font-size:16px;line-height:1.6;padding:10px 4px 0}}
.who{{display:inline-block;color:#fff;font-size:13px;letter-spacing:.1em;padding:.1em .9em;margin-right:.5em;vertical-align:.1em;
  border-style:solid;border-width:0;border-image:url("{UI['ui_tag']}") 80 140 fill / 8px 14px stretch}}
.cast{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:24px}}
.who-card{{text-align:center}}
.who-card img{{width:100%;aspect-ratio:1;object-fit:cover;border-radius:50%;box-shadow:0 0 0 6px #fffdf8,0 8px 18px -6px rgba(90,50,80,.35)}}
.who-card h3{{margin:.7em 0 .1em;font-size:22px}}
.who-card p{{margin:0;font-size:16px;color:var(--dim)}}
.music{{list-style:none;margin:0;padding:0;display:grid;gap:12px}}
.music li{{display:flex;flex-wrap:wrap;align-items:center;gap:12px 18px}}
.music span{{min-width:6em}}
.music audio{{width:min(100%,420px)}}
.notes p{{max-width:44em}}
.notes ul{{margin:.4em 0;padding-left:1.3em;max-width:44em}}
footer.site{{padding-block:40px 120px;text-align:center;color:var(--dim);font-size:15px}}
@media (max-width:640px){{.panel{{padding:34px 30px 26px 48px;border-image-width:40px 28px 26px 52px}} body{{font-size:17px}}}}
@media (prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}
</style></head><body>
<header class="hero"><img src="{KV}" alt="轉生成寶箱怪的我 標題圖：海邊的草坡上一個紅色寶箱，蓋子縫裡露出一雙眼睛">
<div class="wrap in"><h1><small>轉生成</small>寶箱怪的我</h1>
<p class="quote">「我從來沒想過，轉生成寶箱怪這種事，會發生在我身上。」</p>
<div class="btns"><a class="btn hot" href="{MARKET}">到 Larch 玩</a><a class="btn" href="#book">看繪本片段</a><a class="btn" href="{REPO}">原始碼與製作紀錄</a></div></div></header>

<main>
<section class="wrap" id="story"><h2>故事</h2><div class="panel">
<p>在這座島上，一個箱子被人好好用了一百年，就會醒過來，變成寶箱怪。島民把重要的東西交給寶箱怪保管，寶箱怪替大家顧著，兩邊一起過了很久的日子。</p>
<p>你轉生成長老家倉庫裡的那個箱子。族人一睡就是好幾年，整個夏天只有你醒著。直到岸邊停了一艘船，兩個獵人帶著史萊姆 Pulut 上島，開始撬開寶箱，搶走大家寄放的東西。</p>
<p>去村口、營地、遺跡把族人叫醒，騎上火焰飛龍到雲端高台，把冒險隊趕走。</p>
</div></section>

<section class="wrap" id="modes"><h2>兩種玩法</h2><div class="modes">
<div class="mode"><img src="{SHOT3D}" alt="3D 版：寶箱怪在村口叫醒箱爺爺" loading="lazy"><h3>在 3D 小島上自己走</h3>
<p>WASD 移動、空白鍵跳、E 對話與叫醒。島上六個地方藏著寶箱怪剛轉生時的回憶，26 個寶箱都是族人。一輪大約 10～12 分鐘。</p></div>
<div class="mode"><img src="{MODE_BOOK}" alt="繪本版：箱爺爺被敲醒" loading="lazy"><h3>翻開繪本，跟著故事走</h3>
<p>52 張手繪插圖，一句台詞換一張。中間有敲三下、島上地圖、接蘋果、高台選招式四個小互動。不用在 3D 裡走動也能讀完整個故事，手機請轉成橫的。</p></div>
</div></section>

<section class="wrap" id="book"><h2>繪本片段</h2><div class="gallery">
{gal_html}
</div></section>

<section class="wrap" id="cast"><h2>島上的寶箱們</h2><div class="cast">
{cast_html}
</div></section>

<section class="wrap" id="music"><h2>配樂</h2><ul class="music">
{music_html}
</ul></section>

<section class="wrap notes" id="making"><h2>怎麼做的</h2><div class="panel">
<p>這是 Larch 第四屆創作者挑戰（主題：神秘小島）的參賽作品，從 Larch 官方 3D 範例《Pulut 大冒險 3D》改作。3D 場景、模型與角色盡量沿用官方範例，主要換掉劇情：玩家從冒險者變成島上的原住民寶箱怪。</p>
<ul>
<li>劇情、台詞方向與每一張圖的取捨由林亞澤決定；圖都是在選圖頁上從兩版裡挑出來，或逐張確認過的。</li>
<li>2D 插圖用 AI 產圖，同一個場景的各格都從選定的主圖一次改出來，不拿上一格再改。配樂用 AI 生成，再切成循環版。</li>
<li>Larch 卡片、3D 場景事件、介面與小遊戲由 Claude Code 透過 Larch 的 MCP 工具寫進專案。</li>
<li>繪本模式是因為有玩家留言說 3D 不適合、希望有純劇情模式，才把整個故事做成繪本。</li>
</ul>
<p>劇本、設計紀錄與工具都在 <a href="{REPO}">GitHub</a>。文字與原創素材採 CC BY-NC 4.0，工具程式碼採 MIT；範例的場景、模型與內建素材權利屬於 Larch。</p>
</div></section>
</main>
<footer class="site"><p>轉生成寶箱怪的我．林亞澤</p></footer>
</body></html>'''
open(os.path.join(R, 'index.html'), 'w').write(HTML)
tot = sum(os.path.getsize(os.path.join(IMG, f)) for f in os.listdir(IMG))
print('index.html', len(HTML), 'site/img', len(os.listdir(IMG)), 'files', round(tot / 1e6, 1), 'MB')
