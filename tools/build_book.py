# -*- coding: utf-8 -*-
"""把繪本（劇本/繪本.md）做成 Larch 卡片，寫進主線白板 main：序章後插一張「3D／繪本」選擇卡，繪本五章最後接共用的尾聲 sw-ending。
每句台詞帶自己那格的 CG（dialogueLines[i].background），一句換一張；卡片層 background 一定等於第一句的 CG（卡片層會蓋掉第一句）。
  python3 tools/build_book.py           只產出 book/book_nodes.json 讓人檢查
  python3 tools/build_book.py --push    讀白板、移除舊的繪本卡（id 開頭 bk-）、寫入新的（If-Match）"""
import json, os, sys, urllib.request
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PID = 'project-993a4982-d653-4f55-a511-5950e7fda343'
KEY = open(os.path.expanduser('~/.config/larch/key')).read().strip()
M = json.load(open(os.path.join(R, 'assets/media.json')))
CG = lambda k: M['book_' + k]['url']
BGM_EXPLORE = 'https://pub-4b20b43f5acf4dfaa3f6ab842daa51cf.r2.dev/2d3b0242-9a6d-4051-9825-46aa4efd064a/larch/project-993a4982-d653-4f55-a511-5950e7fda343/1794244624541_bgm-explore.mp3'
BGM_BATTLE = 'https://pub-4b20b43f5acf4dfaa3f6ab842daa51cf.r2.dev/2d3b0242-9a6d-4051-9825-46aa4efd064a/larch/project-993a4982-d653-4f55-a511-5950e7fda343/1794244627884_bgm-battle.mp3'
KNOCK = open(os.path.join(R, 'book/games/knock.html')).read()
APPLE = open(os.path.join(R, 'book/games/apple.html')).read()

nodes, edges = [], []
def pos(i):
    return {'x': 80 + (i % 8) * 300, 'y': 820 + (i // 8) * 220}

def dlg(nid, title, lines, bgm=None):
    """lines: [(CG 編號或 None, 講者, 台詞)]，CG 為 None 時沿用上一張"""
    dl = []
    for i, (cg, sp, tx) in enumerate(lines):
        L = {'id': f'{nid}-{i}', 'text': tx, 'speaker': sp}
        if sp == '旁白': L['narration'] = True
        if cg: L['background'] = CG(cg)
        dl.append(L)
    first = next(c for c, _, _ in lines if c)
    d = {'type': 'dialogue', 'title': title, 'text': lines[0][2], 'speaker': lines[0][1], 'background': CG(first),
         'stage': {'props': [], 'actors': []}, 'dialogueLines': dl, 'transition': 'fade', 'transitionMs': 400}
    if bgm: d.update({'bgm': bgm, 'bgmLoop': True, 'bgmVolume': 0.5})
    nodes.append({'id': nid, 'type': 'story', 'position': pos(len(nodes)), 'data': d})

def game(nid, title, html, writes, reads=()):
    nodes.append({'id': nid, 'type': 'story', 'position': pos(len(nodes)), 'data': {
        'type': 'miniGame', 'title': title, 'text': '', 'stage': {'actors': []}, 'miniGameHtml': f'<!-- {nid} -->\n' + html,
        'miniGameFrame': {'showTitle': False, 'showButton': False}, 'miniGameReadVars': list(reads), 'miniGameWriteVars': list(writes),
        'miniGameSkippable': False, 'miniGamePresentation': 'fullscreen'}})

def setv(nid, ops):
    nodes.append({'id': nid, 'type': 'story', 'position': pos(len(nodes)), 'data': {
        'type': 'setVariable', 'title': nid, 'text': '', 'stage': {'actors': []},
        'variableOps': [{'id': f'o{i}', 'kind': k, 'variable': v, 'value': val} for i, (k, v, val) in enumerate(ops)]}})

def edge(a, b, handle='right', cond=None):
    e = {'id': f'e-{a}-{b}-{handle}', 'source': a, 'target': b, 'sourceHandle': handle, 'targetHandle': 'left', 'animated': True}
    if cond: e['data'] = {'condition': cond}
    edges.append(e)

def chain(*ids):
    for a, b in zip(ids, ids[1:]): edge(a, b)

V = lambda var, op, val: {'kind': 'variable', 'variable': var, 'op': op, 'value': val}

# ---- 序章後的選擇 ----
nodes.append({'id': 'bk-mode', 'type': 'story', 'position': {'x': 80, 'y': 600}, 'data': {
    'type': 'choice', 'title': '要怎麼走這一趟', 'text': '要怎麼陪寶箱怪走這一趟？', 'speaker': '旁白', 'stage': {'actors': []},
    'background': M['cg_opening']['url'], 'choices': ['在島上自己走走（3D 冒險）', '翻開繪本，跟著故事走']}})

# ---- 第一章 村口 ----
dlg('bk-1a', '第一章　村口', [
    ('1-1', '寶箱怪', '長老！'),
    (None, '長老', '你也看到了吧。早上那幾個外地人，已經撬了市集後面兩箱，大家寄放在裡面的金幣全被拿走了。'),
    ('1-2', '長老', '你的族人睡得太沉，被撬開都不會醒。去把他們叫起來。'),
    (None, '長老', '你敲了一整個夏天，也許今天叫得起來。'),
    ('1-3', '長老', '箱爺爺就在村口告示牌旁邊。營地跟遺跡也各有一個。'),
    ('1-4', '旁白', '箱爺爺是村口最老的寶箱。蓋子上的木紋，比長老臉上的皺紋還多。'),
    (None, '寶箱怪', '（跟夏天的時候一樣，敲三下。）'),
], bgm=BGM_EXPLORE)
setv('bk-kt1', [('set', 'knock_target', '箱爺爺')])
game('bk-g1', '敲三下：箱爺爺', KNOCK, ['knock_ok'], ['knock_target'])
dlg('bk-1b', '箱爺爺醒了', [
    ('1-5', '箱爺爺', '吵什麼……天亮了嗎？'),
    (None, '寶箱怪', '有獵人上島了，在撬族人的蓋子，搶大家寄放的東西。'),
    ('1-6', '箱爺爺', '……這個聲音。這陣子每天都有人敲我三下，跟我講天氣、講蘋果。是你吧？'),
    (None, '寶箱怪', '你聽得到？'),
    ('1-7', '箱爺爺', '睡著的時候聽得到一點，就是醒不過來。被你敲了這麼久，一天比一天睡得淺，今天總算醒了。'),
    (None, '箱爺爺', '一個人醒著，很悶吧。'),
    (None, '寶箱怪', '……嗯。'),
    ('1-8', '箱爺爺', '先不說這個。我身上收的，是村子裡好幾代人交給我顧的東西，誰敢拿？'),
    ('1-9', '箱爺爺', '對了，蓋子不是只拿來走路的。往地上用力一砸，旁邊的人都站不穩。'),
    (None, '旁白', '寶箱怪學會了「蓋子砸地」。'),
    (None, '箱爺爺', '我跟你去。營地的阿扣睡最熟，先去叫他。'),
    ('M-0', '旁白', '去營地的路上，會經過好幾個寶箱怪很熟的地方。'),
    (None, '寶箱怪', '（要去哪裡看看？）'),
])
chain('bk-mode', 'bk-1a', 'bk-kt1', 'bk-g1', 'bk-1b')
edges[0]['sourceHandle'] = 'choice-1'  # bk-mode 選項二 → 繪本

# ---- 插曲 島上地圖 ----
MAP = [('井', 38, 60, 'well', 'M-1', [('寶箱怪', '我第一次看到自己的樣子，就是在這口井的水面上。'), ('寶箱怪', '紅色的箱子，一雙眼睛。我盯著看了很久，才相信那是我。'), ('箱爺爺', '我第一次照這口井的時候，還以為自己是一個便當盒。')]),
       ('火堆', 51, 58, 'fire', 'M-2', [('寶箱怪', '第一次起風的晚上，長老在這裡生火，叫我坐近一點。'), ('寶箱怪', '我說我是木頭做的，怕火。長老笑了很久，然後把我往後挪了一點。'), ('箱爺爺', '他小時候也這樣挪過我。他們一家都這樣。')]),
       ('市集的貓', 60, 64, 'cat', 'M-3', [('寶箱怪', '市集的貓很喜歡睡在我的蓋子上。'), ('寶箱怪', '我怕吵醒牠，一動也不敢動，結果等到天黑牠才走。'), ('箱爺爺', '那隻貓也睡過我。我睡著的時候，都是聽著牠打呼嚕。')]),
       ('岩縫', 48, 8, 'nook', 'M-4', [('寶箱怪', '下雨的時候，我都躲進這個岩縫。'), ('寶箱怪', '裡面那箱族人一直沒醒。我就對著他講話，講到雨停。'), ('箱爺爺', '岩縫裡那位很膽小，一緊張就往石頭縫裡鑽。')]),
       ('池塘', 79, 47, 'pond', 'M-5', [('寶箱怪', '我在這裡試過游泳。'), ('寶箱怪', '木頭會浮，所以我沒沉下去，只是翻過來，肚子朝天漂了一個下午。'), ('箱爺爺', '那你最後怎麼翻回來的？'), ('寶箱怪', '一隻青蛙跳到我身上，我就翻回來了。')]),
       ('風車', 74, 12, 'mill', 'M-6', [('寶箱怪', '午睡我都選風車底下。'), ('寶箱怪', '葉片的影子一下一下晃過去，比數羊還好睡。'), ('箱爺爺', '……下次換我睡那裡。')])]
nodes.append({'id': 'bk-map', 'type': 'story', 'position': pos(len(nodes)), 'data': {
    'type': 'choice', 'choiceStyle': 'map', 'title': '島上的回憶', 'text': '（要去哪裡看看？點地圖上的地點。）', 'speaker': '寶箱怪', 'stage': {'actors': []},
    'background': CG('M-0'), 'choices': [m[0] for m in MAP] + ['出發去營地'],
    'mapSpots': [{'x': x, 'y': y, 'hover': 'glow', 'label': 'tag', 'visibleCondition': V('seen_' + v, 'neq', True)} for _, x, y, v, _, _ in MAP]
                + [{'x': 27, 'y': 34, 'hover': 'lift', 'label': 'tag'}]}})
edge('bk-1b', 'bk-map')
for i, (name, x, y, v, cg, lines) in enumerate(MAP):
    dlg(f'bk-m-{v}', f'回憶：{name}', [(cg if j == 0 else None, sp, tx) for j, (sp, tx) in enumerate(lines)])
    setv(f'bk-sv-{v}', [('set', 'seen_' + v, True)])
    edge('bk-map', f'bk-m-{v}', f'choice-{i}'); chain(f'bk-m-{v}', f'bk-sv-{v}', 'bk-map')

# ---- 第二章 營地 ----
dlg('bk-2a', '第二章　營地', [
    ('2-1', '市集老闆', '那兩個獵人連我攤子底下的錢箱都翻了。'),
    (None, '市集老闆', '以前你天天擋在我攤子前面曬太陽，害我少做好幾筆生意。現在換你去顧大家了。'),
    ('2-2', '旁白', '營地裡，火焰飛龍趴在火堆旁打盹。旁邊有一個寶箱，蓋子被撬開了，裡面空空的。'),
    (None, '箱爺爺', '被撬開的這箱還在睡。睡著被撬，連自己少了什麼都不知道。'),
    (None, '寶箱怪', '阿扣呢？'),
    ('2-3', '旁白', '阿扣就在隔壁，蓋子跟著打呼一起一伏。'),
])
edge('bk-map', 'bk-2a', f'choice-{len(MAP)}')
setv('bk-kt2', [('set', 'knock_target', '阿扣')])
game('bk-g2a', '敲三下：阿扣（第一次）', KNOCK, ['knock_ok'], ['knock_target'])
dlg('bk-2b', '阿扣翻身', [
    ('2-3b', '阿扣', '……呼……再五分鐘……'),
    (None, '箱爺爺', '他睡最熟。再敲一次。'),
])
game('bk-g2b', '敲三下：阿扣（第二次）', KNOCK, ['knock_ok'], ['knock_target'])
dlg('bk-2c', '阿扣醒了', [
    ('2-4', '阿扣', '……嗯？'),
    (None, '寶箱怪', '阿扣，起來。隔壁那箱被撬了。'),
    (None, '阿扣', '我一直夢到有人敲我的蓋子，每次三下，敲完還說「明天再來」。'),
    (None, '阿扣', '原來不是夢。'),
    ('2-5', '阿扣', '……睡太久，肚子好餓。'),
    (None, '箱爺爺', '營地後面那棵蘋果樹，這陣子結得正多。'),
])
chain('bk-2a', 'bk-kt2', 'bk-g2a', 'bk-2b', 'bk-g2b', 'bk-2c')
game('bk-ga', '接蘋果', APPLE, ['apples'])
edge('bk-2c', 'bk-ga')
dlg('bk-2d1', '接到很多', [('2-6a', '阿扣', '吃飽了！現在我什麼都撞得倒。')])
dlg('bk-2d2', '接到很少', [('2-6b', '阿扣', '……先墊墊肚子就好。')])
edge('bk-ga', 'bk-2d1', cond=V('apples', 'gte', 5)); edge('bk-ga', 'bk-2d2')
dlg('bk-2e', '整箱衝撞', [
    ('2-7', '阿扣', '我睡覺翻身都會滾下坡。你試試看，整個箱子撞過去。'),
    (None, '旁白', '寶箱怪學會了「整箱衝撞」。'),
    (None, '阿扣', '他們往遺跡走了。我跟你去。'),
])
edge('bk-2d1', 'bk-2e'); edge('bk-2d2', 'bk-2e')

# ---- 第三章 遺跡 ----
dlg('bk-3a', '第三章　遺跡', [
    ('3-1', '旁白', '遺跡入口的大石頭被炸開了，碎石散了一地。'),
    (None, '箱爺爺', '連石頭都炸，這些人真的什麼都敢。'),
    ('3-2', '旁白', '遺跡最裡面的角落，有一個寶箱縮成一團，蓋子抖個不停。'),
    (None, '箱爺爺', '小鎖膽子小，敲輕一點。'),
])
setv('bk-kt3', [('set', 'knock_target', '小鎖')])
game('bk-g3a', '敲三下：小鎖（第一次）', KNOCK, ['knock_ok'], ['knock_target'])
dlg('bk-3b', '小鎖嚇到', [('3-2b', '小鎖', '（嗚……）'), (None, '箱爺爺', '太大力了。輕一點。')])
game('bk-g3b', '敲三下：小鎖（第二次）', KNOCK, ['knock_ok'], ['knock_target'])
dlg('bk-3c', '小鎖醒了', [
    ('3-3', '小鎖', '（蓋子抖個不停）走、走了嗎？'),
    (None, '寶箱怪', '小鎖，是我。'),
    (None, '小鎖', '他們剛剛就站在我前面。那隻史萊姆聞了我一下，又跳走了。'),
    ('3-4', '小鎖', '獵人說最大的寶藏在雲端高台上，要去那裡。'),
    (None, '小鎖', '雲端之門是通到雲上的門。雲上住著女神卡雅，她什麼都知道。'),
    (None, '寶箱怪', '高台那麼高，我們上不去。'),
    (None, '小鎖', '營地的火焰飛龍會載人。我們也算人吧？'),
    ('3-5', '阿扣', '算吧？我們會講話。'),
    (None, '箱爺爺', '會講話的箱子，就算人。'),
    ('3-6', '小鎖', '害怕的時候，就把蓋子闔緊。躲一下，就不痛了。'),
    (None, '旁白', '寶箱怪學會了「躲進蓋子」。'),
    ('3-7', '旁白', '三個族人都醒了。'),
    (None, '箱爺爺', '上去之前，我們一起敲三下，嚇他們一跳。'),
    (None, '旁白', '寶箱怪學會了「敲三下」。'),
])
chain('bk-2e', 'bk-3a', 'bk-kt3', 'bk-g3a', 'bk-3b', 'bk-g3b', 'bk-3c')

# ---- 第四章 騎火焰飛龍 ----
dlg('bk-4', '第四章　騎火焰飛龍', [
    ('4-1', '旁白', '火焰飛龍睜開一隻眼睛，看著四個寶箱。'),
    (None, '小鎖', '牠、牠會不會把我們當成點心？'),
    (None, '箱爺爺', '牠只吃烤魚。'),
    ('4-2', '旁白', '四個寶箱一個疊一個，爬上了龍背。'),
    (None, '阿扣', '誰踩到我的蓋子了？'),
    ('4-3', '旁白', '火焰飛龍拍了兩下翅膀，整座島一下子變得好小。'),
    (None, '阿扣', '我看到營地了！那個空空的箱子旁邊就是我家！'),
    (None, '小鎖', '（蓋子闔得緊緊的）我、我不看。'),
    (None, '寶箱怪', '（從這麼高的地方往下看，島上的寶箱一個一個，像撒在草地上的糖果。）'),
    ('4-4', '旁白', '雲端之門前，兩個獵人正在撬門上的石環。綠色的史萊姆縮在門邊。'),
])
edge('bk-3c', 'bk-4')

# ---- 第五章 雲端高台 ----
dlg('bk-5a', '第五章　雲端高台', [
    ('5-1', '少年獵人', '又一個寶箱。會自己走的。'),
    (None, '少女獵人', '會走的寶箱，裡面一定是好東西。'),
    (None, '寶箱怪', '把錢還回來。'),
    (None, '少年獵人', '撬開再說。'),
], bgm=BGM_BATTLE)
setv('bk-r1', [('set', 'round', 1)])
dlg('bk-5r1', '第一回合', [('5-2', '少年獵人', '別動，讓我撬一下就好！')])
dlg('bk-5r2', '第二回合', [('5-3', '少女獵人', '綁起來帶回船上！')])
dlg('bk-5r3', '第三回合', [('5-4', '少年獵人', '一起上！')])
nodes.append({'id': 'bk-5c', 'type': 'story', 'position': pos(len(nodes)), 'data': {
    'type': 'choice', 'title': '選招式', 'text': '第 {{round}} 回合：要用哪一招？', 'speaker': '寶箱怪', 'stage': {'actors': []},
    'background': CG('5-1'), 'choices': ['蓋子砸地', '整箱衝撞', '躲進蓋子', '敲三下'],
    'choiceConditions': [None, None, None, V('round', 'gte', 3)], 'hideUnavailableChoices': True}})
chain('bk-4', 'bk-5a', 'bk-r1', 'bk-5r1', 'bk-5c')
edge('bk-5r2', 'bk-5c'); edge('bk-5r3', 'bk-5c')
dlg('bk-5y', '蓋子砸地', [('5-Y', '少女獵人', '哇、地在晃！')])
dlg('bk-5u', '整箱衝撞', [('5-U', '少年獵人', '我的撬棍！')])
dlg('bk-5i', '躲進蓋子', [('5-I', '少年獵人', '好硬……手好麻。')])
setv('bk-rn', [('add', 'round', 1)])
for i, m in enumerate(['bk-5y', 'bk-5u', 'bk-5i']):
    edge('bk-5c', m, f'choice-{i}'); edge(m, 'bk-rn')
edge('bk-rn', 'bk-5r2', cond=V('round', 'eq', 2)); edge('bk-rn', 'bk-5r3')
dlg('bk-5o', '敲三下', [
    ('5-O', '旁白', '叩、叩、叩。四個寶箱一起敲下去，整座高台都在響。'),
    ('5-5', '少女獵人', '等一下，不打了。我們投降。'),
    (None, '少年獵人', '錢都在船上，我們還。'),
    (None, '寶箱怪', '那隻史萊姆呢？'),
    ('5-6', 'Pulut', '……我不是他們的。'),
    (None, 'Pulut', '我住在雲的上面，掉下來的時候被他們撿到。他們說幫他們找寶箱，就帶我回家。'),
    ('5-7', '寶箱怪', '（掉到一個不認識的地方，什麼都不會。我剛醒的時候也是這樣。）'),
    (None, '寶箱怪', '（那時候，是長老把我扶起來的。）'),
    (None, '寶箱怪', '我們幫你想辦法回去。'),
    (None, '少女獵人', '我們……其實不知道怎麼上雲。'),
    ('5-8', '旁白', '雲端之門亮了起來，門裡走出一個女孩。是住在雲上的女神，卡雅。'),
    (None, '卡雅', 'Pulut，找到你了。'),
    (None, '卡雅', '這扇門會把人送到雲上。你就是從它的縫掉下來的。'),
    (None, '卡雅', '謝謝你們顧著他。我帶他回家。'),
], bgm=BGM_EXPLORE)
edge('bk-5c', 'bk-5o', 'choice-3')
edge('bk-5o', 'sw-ending')

VARS = {'knock_ok': False, 'knock_target': '箱爺爺', 'apples': 0, 'round': 1, **{'seen_' + m[3]: False for m in MAP}}

if __name__ == '__main__':
    out = {'nodes': nodes, 'edges': edges, 'vars': VARS}
    json.dump(out, open(os.path.join(R, 'book/book_nodes.json'), 'w'), ensure_ascii=False, indent=1)
    n_lines = sum(len(n['data'].get('dialogueLines', [])) for n in nodes)
    print(len(nodes), 'nodes', len(edges), 'edges', n_lines, 'lines')
    ids = {n['id'] for n in nodes} | {'sw-ending', 'sw-world', 'sw-intro'}
    bad = [e for e in edges if e['source'] not in ids or e['target'] not in ids]
    print('dangling edges', bad)
    if '--push' in sys.argv:
        H = {'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        url = f'https://larch.ink/api/agent/projects/{PID}/boards/main'
        r = urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=120)
        etag = r.headers.get('ETag'); b = json.load(r); b = b.get('board', b)
        json.dump(b, open(os.path.join(R, f'snapshots/board-main-before-book-{etag.strip("W/").strip(chr(34))}.json'), 'w'), ensure_ascii=False)
        b['nodes'] = [n for n in b['nodes'] if not n['id'].startswith('bk-')] + nodes
        b['edges'] = [e for e in b['edges'] if not (e['source'].startswith('bk-') or e['target'].startswith('bk-')) and e['id'] != 'e-sw-intro-sw-world']
        b['edges'] += [{'id': 'e-sw-intro-bk-mode', 'source': 'sw-intro', 'target': 'bk-mode', 'sourceHandle': 'right', 'targetHandle': 'left', 'animated': True},
                       {'id': 'e-bk-mode-sw-world', 'source': 'bk-mode', 'target': 'sw-world', 'sourceHandle': 'choice-0', 'targetHandle': 'left', 'animated': True}]
        b['edges'] += edges
        body = {'name': b.get('name', '主線故事'), 'nodes': b['nodes'], 'edges': b['edges'], 'summary': '加入繪本模式：序章後選 3D 或繪本，繪本五章接共用尾聲'}
        req = urllib.request.Request(url, method='PUT', data=json.dumps(body).encode(), headers={**H, 'If-Match': etag})
        try:
            print('PUT', urllib.request.urlopen(req, timeout=300).status)
        except urllib.error.HTTPError as e:
            print('PUT', e.code, e.read()[:600])
