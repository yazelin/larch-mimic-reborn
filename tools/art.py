# -*- coding: utf-8 -*-
"""《轉生成寶箱怪的我》的圖：走 .11 codex-image-service，排隊規則照 ~/larch-wt-walks/buchan/cg_jobs.py（同一個 ~/.cache/cg_jobs 目錄）。
參考圖在 art/refs/（從遊戲裡拍的），產出放 art/cg/<名字>_v<n>.webp，旁邊存一份 .json 記提示詞與參考圖。
  python3 tools/art.py list
  python3 tools/art.py run 名字 [名字…]   （同時送出，排隊間隔照 ~/.cache/cg_jobs/interval）
"""
import io, json, os, sys, threading, time, urllib.request, base64
from PIL import Image

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(R, 'art/cg')
BASE = 'https://ching-tech.ddns.net/codex-image'
KEY = next(l.split('=', 1)[1].strip().strip('"') for l in open(os.path.expanduser('~/.bashrc')) if 'CODEX_IMAGE_KEY=' in l)
QUEUE = os.path.expanduser('~/.cache/cg_jobs')   # 跟 ~/larch-wt-walks/buchan/cg_jobs.py 共用同一個排隊目錄與規則（間隔 interval 秒、上限 max_inflight 張）


class C:
    @staticmethod
    def call(method, path, body=None):
        r = urllib.request.Request(BASE + path, method=method, data=json.dumps(body).encode() if body else None,
                                   headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'})
        with urllib.request.urlopen(r, timeout=120) as x: return json.loads(x.read())

    @staticmethod
    def _inflight():
        try: live = json.load(open(os.path.join(QUEUE, 'inflight.json')))
        except (OSError, ValueError): live = {}
        return {k: t for k, t in live.items() if os.path.exists(f"/proc/{k.split('-')[0]}") and time.time() - t < 1200}

    @staticmethod
    def _queue():
        import fcntl, uuid
        os.makedirs(QUEUE, exist_ok=True); tag = f'{os.getpid()}-{uuid.uuid4().hex}'
        while True:
            with open(os.path.join(QUEUE, 'lock'), 'w') as lk:
                fcntl.flock(lk, fcntl.LOCK_EX); live = C._inflight()
                try: cap = int(open(os.path.join(QUEUE, 'max_inflight')).read())
                except (OSError, ValueError): cap = 999
                if len(live) < cap:
                    try: gap = float(open(os.path.join(QUEUE, 'interval')).read())
                    except (OSError, ValueError): gap = 30
                    try: last = float(open(os.path.join(QUEUE, 'last')).read())
                    except (OSError, ValueError): last = 0
                    if last + gap > time.time(): time.sleep(last + gap - time.time())
                    open(os.path.join(QUEUE, 'last'), 'w').write(str(time.time()))
                    live[tag] = time.time(); json.dump(live, open(os.path.join(QUEUE, 'inflight.json'), 'w'))
                    return tag
            time.sleep(10)

    @staticmethod
    def _done(tag):
        import fcntl
        with open(os.path.join(QUEUE, 'lock'), 'w') as lk:
            fcntl.flock(lk, fcntl.LOCK_EX); live = C._inflight(); live.pop(tag, None)
            json.dump(live, open(os.path.join(QUEUE, 'inflight.json'), 'w'))

REF = {
    'mimic': ('art/refs/mimic.webp', '寶箱怪（主角）：紅色木頭寶箱，四邊包著粉紫色的金屬框，正面中間一個粉紫色方形鎖扣'),
    'boy': ('art/refs/hunter_boy.webp', '少年獵人：白色短髮，紅色短披肩，白色上衣、紅腰帶，深色長褲與靴子'),
    'girl': ('art/refs/hunter_girl.webp', '少女獵人：橘色長髮，紅色短披肩，白色上衣、紅腰帶，深色褲子與長靴'),
    'pulut': ('art/refs/pulut.webp', 'Pulut：圓滾滾的綠色小史萊姆，頭頂兩個小尖角，黑色圓眼睛'),
    'chest': ('art/refs/chest.webp', '族人（睡著的寶箱怪）：普通的棕色木頭寶箱，金色包邊'),
    'island': ('art/refs/island_aerial.webp', '島的樣子：草地小島，紅屋頂的村子、石拱門、圓滾滾的樹，海是藍紫色'),
    'village': ('art/refs/village.webp', '村口：石板路、路牌、木長椅、花圃，黃昏粉紫色天空'),
    'village_clean': ('art/refs/village_clean.webp', '村口：石板路、路牌、木長椅、花圃'),
}

S3D = '畫風：跟參考圖的遊戲畫面一致的 3D 玩具感低多邊形，圓潤柔軟的造型、乾淨的平滑上色、柔和的黃昏光，粉紫與暖黃的天空，像精緻的 3D 動畫電影宣傳圖。'
S2D = '畫風：2D 手繪繪本插畫，水彩加色鉛筆的質感，溫暖柔和、線條輕鬆，粉紫與暖黃的黃昏色調，像童書封面。角色造型照參考圖，但畫成手繪。'
NOTXT = '畫面裡沒有任何文字、字母、浮水印、標誌。'

KV = """作品《轉生成寶箱怪的我》的標題主視覺，橫幅 16:9。
畫面：黃昏的小島草地上，前景正中偏右是主角寶箱怪（照 Image 1：紅色寶箱、粉紫色金屬框與鎖扣），蓋子微微掀開一條縫，縫裡露出一雙圓圓亮亮的眼睛，好奇又有點緊張地往外看。
它身旁的草地上散著幾個睡著的棕色寶箱族人（照 Image 2），蓋子闔著，安安靜靜地睡著，旁邊飄著幾個小小的圓泡泡。
中景遠處的沙灘停著一艘小木船，兩個小小的獵人（Image 3 少年、Image 4 少女）正背著背包往島上走，少女的背包口探出一隻綠色小史萊姆（Image 5）。
背景是島上紅屋頂的村子與圓滾滾的樹（照 Image 6），更遠處的西北邊有一座高高的雲端高台，頂上一圈石環門。
畫面左上留一大塊乾淨的天空，之後要放標題字。"""

OPEN = """序章開場 CG，橫幅 16:9。
畫面：清晨柔和的光，草地上一個闔著的寶箱怪（照 Image 1：紅色寶箱、粉紫色金屬框與鎖扣），鏡頭貼近地面、從正面稍低的角度看它。
蓋子與箱身之間的縫裡露出一雙圓圓的眼睛，剛睡醒、帶著困惑，好像在想「我怎麼會在這裡」。
草葉上有露珠，背景是模糊的村口（照 Image 2）與粉紫色天空，景深淺，焦點在那雙眼睛。
整個畫面安靜、有一點神祕，也有一點可愛。"""

JOBS = {
    'kv_3d': dict(size='1536x1024', refs=['mimic', 'chest', 'boy', 'girl', 'pulut', 'island'], prompt=KV + '\n' + S3D + NOTXT),
    'kv_2d': dict(size='1536x1024', refs=['mimic', 'chest', 'boy', 'girl', 'pulut', 'island'], prompt=KV + '\n' + S2D + NOTXT),
    'open_3d': dict(size='1536x1024', refs=['mimic', 'village'], prompt=OPEN + '\n' + S3D + NOTXT),
    'open_2d': dict(size='1536x1024', refs=['mimic', 'village'], prompt=OPEN + '\n' + S2D + NOTXT),
}

EDIT = '這是精修編輯。Image 1 是要編輯的原圖，除了下面指定的地方，構圖、角色、顏色、光影、筆觸、背景一律保持不變。'
REF['kv_2d_v1'] = ('art/cg/kv_2d_v1.webp', '要編輯的原圖（標題主視覺 2D 版）')
REF['open_2d_v1'] = ('art/cg/open_2d_v1.webp', '要編輯的原圖（序章 CG 2D 版）')
REF['kv_2d'] = ('art/cg/kv_2d_v1.webp', '已定稿的標題主視覺，畫風、色調、寶箱怪與族人的畫法照它')

JOBS['kv_2d_fix'] = dict(size='1536x1024', refs=['kv_2d_v1'], prompt=EDIT + """
只改一個地方：前景紅色寶箱怪的蓋子右上角，粉紫色金屬框旁邊有一個像「0ℓ」的小白色記號，把它拿掉，那塊補成跟旁邊一樣的紅色木頭蓋子。
其他地方完全照原圖。""" + NOTXT)
JOBS['open_2d_fix'] = dict(size='1536x1024', refs=['open_2d_v1'], prompt=EDIT + """
只改一個地方：左上角天空裡飄著一顆淺藍紫色的水晶（下面有一小塊浮著的石頭），把水晶和那塊石頭整個拿掉，那裡補成跟旁邊一樣的粉紫色天空與雲。
其他地方完全照原圖，寶箱怪、眼睛、草地、露珠、村口都不動。""" + NOTXT)
JOBS['icon_2d'] = dict(size='1024x1024', refs=['kv_2d', 'mimic'], prompt="""作品圖示，正方形。
畫面正中是寶箱怪（照 Image 2 的造型：紅色寶箱、粉紫色金屬框與方形鎖扣），正面、稍微俯視，蓋子掀開一條縫，縫裡一雙圓圓亮亮的眼睛看著觀眾，有點好奇、有點可愛。
寶箱佔畫面大約七成，四周留一點邊，背景是平塗的柔和粉紫色到暖黃色的漸層，沒有其他東西，縮小到 64 像素也認得出是一個露出眼睛的寶箱。
畫風照 Image 1：2D 手繪繪本插畫，水彩加色鉛筆質感，線條清楚。""" + NOTXT)
JOBS['bg_intro_2d'] = dict(size='1536x1024', refs=['kv_2d', 'island', 'village_clean'], prompt="""序章對話卡的背景，橫幅 16:9，畫面裡沒有任何角色。
清晨的小島：前景是村口的草地與石板路（照 Image 3 的村口：路牌、木長椅、花圃），中景是紅屋頂的村子（照 Image 2），遠處的沙灘停著一艘沒看過的小木船，船帆收著。
天空是清晨淡淡的粉紫色與金色，海面反光。下面三分之一要放對話框，畫面重點放在上半與中段。
畫風照 Image 1：2D 手繪繪本插畫，水彩加色鉛筆質感，溫暖柔和。""" + NOTXT)
JOBS['bg_ending_2d'] = dict(size='1536x1024', refs=['kv_2d', 'chest', 'island'], prompt="""尾聲對話卡的背景，橫幅 16:9，畫面裡沒有人。
黃昏的海邊草坡：前景草地上散著幾個棕色寶箱族人（照 Image 2），蓋子都闔上了，安安靜靜地睡著。
遠處的海上，一艘小木船張著帆往夕陽的方向開走，船很小。島上紅屋頂的村子在右邊（照 Image 3）。
天空是溫暖的橘粉色漸漸變成紫色，第一顆星星亮了。整體安靜、溫柔。下面三分之一要放對話框。
畫風照 Image 1：2D 手繪繪本插畫，水彩加色鉛筆質感。""" + NOTXT)

REF['boy_face'] = ('art/refs/boy_face.webp', '少年獵人的臉與上半身（遊戲裡的 3D 模型近照）：白色蓬鬆短髮、綠色眼睛、清秀的少年臉，紅色短披肩、白色上衣、紅腰帶')
REF['girl_face'] = ('art/refs/girl_face.webp', '少女獵人的臉與上半身（遊戲裡的 3D 模型近照）：橘色高馬尾、瀏海、綠色大眼睛、清秀的少女臉，紅色短披肩、白色上衣、紅腰帶')
JOBS['kv_2d_face'] = dict(size='1536x1024', refs=['kv_2d_v1', 'boy_face', 'girl_face'], prompt=EDIT + """
改兩個地方，其他完全照原圖：
一、畫面中間偏左、沙灘上往前走的兩個獵人，臉畫得太模糊。把兩個人的臉重新畫清楚：
  - 前面白頭髮的少年照 Image 2：清秀的少年臉、綠色眼睛、表情得意又有點貪心，眼睛、眉毛、鼻子、嘴巴都畫得清楚。
  - 後面橘色馬尾的少女照 Image 3：清秀的少女臉、綠色大眼睛、表情興奮、嘴角上揚，五官清楚。
  - 兩個人的大小、位置、姿勢、走路的方向、衣服、背包、少女背包裡的綠色史萊姆都不變，只把臉與頭髮的細節畫好，畫風跟整張圖的手繪水彩一致。
二、前景紅色寶箱怪的蓋子右上角，粉紫色金屬框旁邊有一個像「0ℓ」的小白色記號，把它拿掉，那塊補成跟旁邊一樣的紅色木頭蓋子。""" + NOTXT)

REF['kv_2d_face'] = ('art/cg/kv_2d_face_v1.webp', '上一版標題主視覺：只參考構圖、畫風、色調、寶箱怪與族人的畫法；裡面兩個獵人的手畫錯了（多一隻手），不要照抄他們的手臂')
KV3 = """作品《轉生成寶箱怪的我》的標題主視覺，橫幅 16:9，構圖、畫風、色調照 Image 1。
前景正中偏右：主角寶箱怪（照 Image 2：紅色木頭寶箱、粉紫色金屬框與方形鎖扣），蓋子微微掀開一條縫，縫裡一雙圓圓亮亮的眼睛往外看。
它四周的草地上散著四、五個睡著的棕色寶箱族人（照 Image 3），蓋子闔著，旁邊飄著幾個小小的圓泡泡。
中景左邊的沙灘停著一艘小木船，兩個獵人從船邊沿著沙灘往右邊的村子走，身體朝畫面右側，臉看得清楚：
  - 前面是少年獵人（照 Image 4：白色蓬鬆短髮、綠色眼睛、紅色短披肩、白色上衣、紅腰帶、深色褲子與靴子），表情得意。
    他的身體只有兩條手臂：靠畫面左邊的那隻手在胸前抓著背包肩帶，靠畫面右邊的那隻手臂自然垂在身側、隨走路擺動。
  - 後面是少女獵人（照 Image 5：橘色高馬尾、綠色大眼睛、紅色短披肩、白色上衣、紅腰帶），表情興奮。
    她的身體只有兩條手臂：靠畫面左邊的那隻手在胸前抓著背包肩帶，靠畫面右邊的那隻手往前伸、食指指著遠處的村子。
    她的背包口探出一隻綠色小史萊姆（照 Image 6）。
  - 兩個人的手都畫清楚，每隻手五根手指，兩隻手各在身體自己那一側，手臂不交叉、不重疊。
背景是島上紅屋頂的村子、石拱門與圓滾滾的樹（照 Image 7），西北邊天空有一座浮在雲上的高台，頂上一圈石環門。
畫面左上留一大塊乾淨的天空，之後要放標題字。"""
JOBS['kv_2d_v3a'] = dict(size='1536x1024', refs=['kv_2d_face', 'mimic', 'chest', 'boy_face', 'girl_face', 'pulut', 'island'], prompt=KV3 + '\n' + S2D + NOTXT)
JOBS['kv_2d_v3b'] = dict(size='1536x1024', refs=['kv_2d_face', 'mimic', 'chest', 'boy_face', 'girl_face', 'pulut', 'island'], prompt=KV3 + '\n' + S2D + NOTXT)


# 回憶 CG（劇本/回憶.md，2026-11-10 定稿）
REF['open_final'] = ('art/cg/open_2d_fix_v1.webp', '已定稿的序章開場 CG：畫風、色調、筆觸、寶箱怪的畫法（蓋子縫裡露出一雙眼睛）照它')
REF['elder'] = ('art/refs/elder.webp', '長老（遊戲裡的 3D 模型）：方塊造型的玩具小人，戴藍色警帽、帽子正面一個金色徽章，橘色頭髮與鬢角，藍色制服')
MIMIC = '寶箱怪（照 Image 2）：紅色木頭寶箱，四邊粉紫色金屬框，正面中間一個粉紫色方形鎖扣。寶箱怪沒有手、沒有腳、沒有嘴巴，全身就是一個箱子，只有蓋子與箱身之間的縫裡露出一雙圓圓的眼睛（畫法照 Image 1）。'
MEM1 = """序章回憶 CG〈醒來的第一天〉，橫幅 16:9。
畫面：清晨，村口的草地與石板路旁。""" + MIMIC + """
寶箱怪側翻倒在草地上，箱子歪向一邊，蓋子的縫裡那雙眼睛轉成暈頭轉向的樣子。
長老（照 Image 3：方塊造型的小人、藍色警帽與金色徽章、橘色頭髮與鬢角、藍色制服，畫成手繪）站在寶箱怪旁邊，彎著腰，兩隻手扶著寶箱的側面，正把它推回直立。長老表情溫和、有點好笑。
背景照 Image 1 的村口：路牌、木長椅、花圃，遠處紅屋頂的房子，清晨淡粉紫與金色的天空。
畫面溫暖、有一點好笑。"""
MEM2 = """序章回憶 CG〈第一次吃東西〉，橫幅 16:9。
畫面：白天，陽光下的草地，鏡頭貼近地面。""" + MIMIC + """
一隻小白兔（白色的毛、耳朵內側粉紅色、圓圓的黑眼睛）站在寶箱怪正前面，鼻子湊近粉紫色的鎖扣在聞。
寶箱怪的蓋子正要往下闔，縫裡的眼睛睜得很大，嚇了一跳的樣子。兔子還沒發現。
草地上有小花，背景是模糊的圓滾滾的樹與藍天白雲，景深淺，焦點在兔子和眼睛。
畫面可愛、有一點緊張，沒有血、沒有被吃掉的畫面。"""
MEM3 = """序章回憶 CG〈明天再來〉，橫幅 16:9。
畫面：黃昏，海邊的草坡，遠處是海和快要落下的夕陽。""" + MIMIC + """
寶箱怪在畫面中間偏左，面對一個闔著蓋子的棕色寶箱族人（照 Image 4：普通的棕色木頭寶箱、金色包邊），寶箱怪身體往前傾，用自己的蓋子邊緣輕輕碰那個寶箱的蓋子，像在敲門。
那個棕色寶箱沒有任何反應，安安靜靜地睡著。草坡更遠的地方還散著兩、三個一樣睡著的棕色寶箱。
寶箱怪的影子被夕陽拉得很長。天空橘粉色漸漸變成紫色。
畫面安靜、有一點寂寞，也很溫柔。"""
for k, body, refs in [('mem1', MEM1, ['open_final', 'mimic', 'elder']),
                      ('mem2', MEM2, ['open_final', 'mimic']),
                      ('mem3', MEM3, ['open_final', 'mimic', 'chest'])]:
    for v in 'ab':
        JOBS[f'{k}{v}'] = dict(size='1536x1024', refs=refs, prompt=body + '\n' + S2D + '畫風照 Image 1。' + NOTXT)

# 2026-11-10 作者：吃兔子會撞「兔兔那麼可愛」的梗，回憶 CG 2 改成蘋果
MEM2_APPLE = """序章回憶 CG〈第一次吃東西〉，橫幅 16:9。
畫面：白天，陽光從樹葉間灑下來，一棵圓滾滾、結滿紅蘋果的蘋果樹下，鏡頭貼近地面、稍微仰角。""" + MIMIC + """
寶箱怪坐在蘋果樹下的草地上，蓋子往上掀開一條寬寬的縫，像在發呆曬太陽。
一顆紅蘋果正從樹枝上掉下來，就在蓋子的縫正上方，快要掉進箱子裡。
蓋子縫裡的眼睛往上看著那顆蘋果，睜得很大，嚇了一跳的樣子。
草地上還有一兩顆掉落的蘋果，有小花，背景是模糊的綠樹與藍天白雲，景深淺，焦點在蘋果和眼睛。
畫面可愛、溫暖、有一點好笑。畫面裡沒有任何動物。"""
for v in 'ab':
    JOBS[f'mem2apple{v}'] = dict(size='1536x1024', refs=['open_final', 'mimic'], prompt=MEM2_APPLE + '\n' + S2D + '畫風照 Image 1。' + NOTXT)


def b64(path):
    im = Image.open(os.path.join(R, path)).convert('RGB'); buf = io.BytesIO(); im.save(buf, 'PNG')
    return base64.b64encode(buf.getvalue()).decode()


def next_path(name):
    os.makedirs(OUT, exist_ok=True); n = 1
    while os.path.exists(os.path.join(OUT, f'{name}_v{n}.webp')): n += 1
    return os.path.join(OUT, f'{name}_v{n}.webp')


def run(name):
    j = JOBS[name]
    legend = '參考圖：' + '；'.join(f'Image {i + 1}＝{REF[k][1]}' for i, k in enumerate(j['refs'])) + '。'
    prompt = legend + '\n' + j['prompt'].strip()
    body = {'prompt': prompt, 'size': j['size'], 'quality': 'high', 'count': 1,
            'reference_images_base64': [b64(REF[k][0]) for k in j['refs']]}
    tag = C._queue()
    try:
        job = C.call('POST', '/v1/images/jobs', body)['id']; t0 = time.time()
        while True:
            time.sleep(15)
            st = C.call('GET', f'/v1/images/jobs/{job}')
            if st.get('status') == 'succeeded':
                data = urllib.request.urlopen(st['images'][0]['url'], timeout=120).read()
                out = next_path(name)
                Image.open(io.BytesIO(data)).save(out, 'WEBP', quality=92)
                json.dump({'job': job, 'prompt': prompt, 'refs': [REF[k][0] for k in j['refs']]},
                          open(out.replace('.webp', '.json'), 'w'), ensure_ascii=False, indent=1)
                print(f'{name}: OK {int(time.time() - t0)}s → {out}', flush=True); return
            if st.get('status') in ('failed', 'error'):
                print(f'{name}: FAILED {st.get("error")}', flush=True); return
    except Exception as e:
        print(f'{name}: 例外 {e!r}', flush=True)
    finally:
        C._done(tag)


if __name__ == '__main__':
    if sys.argv[1] == 'list':
        for k, j in JOBS.items(): print(k, j['size'], j['refs'])
    else:
        ts = [threading.Thread(target=run, args=(n,)) for n in sys.argv[2:]]
        for t in ts: t.start()
        for t in ts: t.join()
