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
