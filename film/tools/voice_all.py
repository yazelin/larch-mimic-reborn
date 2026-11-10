"""全劇配音：照 film/storyboard.json 的順序，每句用 film/cast.json 的聲音配音，量實際秒數。
  python3 film/tools/voice_all.py   → film/voice/<鏡>_<句>.mp3、film/voice/timeline.json
規則：句首括號是舞台指示（例「（蓋子闔得緊緊的）我、我不看。」）不唸；整句在括號裡是內心獨白，去掉括號照唸、語氣放平靜。
走 .11 larch-tts-bridge；已存在的音檔不重配（要重配就刪檔）。"""
import concurrent.futures as cf, hashlib, json, os, re, subprocess, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "film/voice"; OUT.mkdir(parents=True, exist_ok=True)
KEY = open(os.path.expanduser("~/.config/larch-tts/key")).read().strip()
CAST = json.load(open(ROOT / "film/cast.json"))
SB = json.load(open(ROOT / "film/storyboard.json"))
DEFAULT_EMO = {"旁白": "calm", "長老": "calm", "卡雅": "calm"}
# 依劇情指定語氣（台詞開頭幾個字 → emotion）
EMO = {
    "長老！": "surprised", "你也看到了吧": "sad", "吵什麼": "angry", "……這個聲音": "surprised", "你聽得到？": "surprised",
    "一個人醒著，很悶吧": "sad", "……嗯。": "sad", "先不說這個": "angry", "我第一次照這口井": "happy",
    "他小時候也這樣挪過我": "happy", "……下次換我睡那裡": "happy", "那兩個獵人連我攤子": "angry",
    "……呼……再五分鐘": "calm", "……嗯？": "surprised", "原來不是夢": "happy", "……睡太久，肚子好餓": "sad",
    "吃飽了！": "happy", "連石頭都炸": "angry", "嗚……": "fearful", "太大力了": "calm", "走、走了嗎？": "fearful",
    "他們剛剛就站在我前面": "fearful", "牠、牠會不會": "fearful", "牠只吃烤魚": "calm", "誰踩到我的蓋子了": "angry",
    "我看到營地了！": "happy", "我、我不看": "fearful", "又一個寶箱": "surprised", "會走的寶箱": "happy",
    "把錢還回來": "angry", "撬開再說": "happy", "別動，讓我撬": "angry", "綁起來帶回船上": "angry", "一起上！": "angry",
    "哇、地在晃！": "fearful", "我的撬棍！": "surprised", "好硬……手好麻": "sad", "等一下，不打了": "fearful",
    "錢都在船上": "sad", "……我不是他們的": "sad", "我住在雲的上面": "sad", "我們……其實不知道": "sad",
    "Pulut，找到你了": "happy", "謝謝你們顧著他": "happy", "少了三枚": "angry", "……在我鞋子裡": "sad",
    "我們要睡了": "calm", "你敲三下，我們就起來": "calm", "嗯。": "happy", "跟夏天的時候一樣，只有我醒著": "sad",
    "可是現在，我知道": "happy", "……？": "surprised", "我就猜你在海邊": "happy", "……這頂帽子是我小時候": "sad",
    "……我會繼續幫你們顧著": "happy", "他們在撬我們家的人": "fearful", "大家快醒醒！": "fearful",
    "這座島寶箱超多": "happy", "Pulut，聞一下": "happy", "咦，這不是我家倉庫": "surprised", "……你醒了啊": "happy",
    "我嚇了一跳，蓋子一闔": "happy", "我住在雲": "sad",
    # 內心獨白照內容給語氣（作者：內心獨白要配、有情緒可以用）
    "掉到一個不認識的地方": "sad", "那時候，是長老把我扶起來的": "sad", "從這麼高的地方往下看": "happy",
    "跟夏天的時候一樣，敲三下": "calm",
    # 第二輪：作者「有情緒可以使用」，原本用預設語氣的句子逐句補
    "我從來沒想過": "surprised", "醒來的第一天": "surprised", "我在村口翻倒了好幾次": "happy",
    "原來島上的人早就知道": "happy", "第三天，我開始覺得肚子餓": "sad", "我在樹下張著蓋子發呆": "surprised",
    "我每天去敲": "sad", "白天在村口曬太陽": "sad", "今天早上，我在村口曬太陽": "surprised",
    "他們走到市集後面": "angry", "有獵人上島了": "fearful", "睡著的時候聽得到一點": "happy",
    "對了，蓋子不是只拿來走路的": "happy", "我跟你去": "happy", "我說我是木頭做的": "happy",
    "市集的貓很喜歡": "happy", "我怕吵醒牠": "happy", "那隻貓也睡過我": "happy", "裡面那箱族人一直沒醒": "sad",
    "我在這裡試過游泳": "happy", "木頭會浮": "happy", "那你最後怎麼翻回來的": "surprised",
    "一隻青蛙跳到我身上": "happy", "午睡我都選風車底下": "happy", "葉片的影子": "happy",
    "以前你天天擋在我攤子前面": "happy", "被撬開的這箱還在睡": "sad", "阿扣呢？": "fearful",
    "阿扣，起來": "fearful", "我一直夢到有人敲我的蓋子": "surprised", "營地後面那棵蘋果樹": "happy",
    "我睡覺翻身都會滾下坡": "happy", "他們往遺跡走了": "happy", "小鎖膽子小": "calm", "小鎖，是我": "calm",
    "獵人說最大的寶藏": "fearful", "高台那麼高": "sad", "營地的火焰飛龍會載人": "happy",
    "算吧？我們會講話": "happy", "會講話的箱子": "happy", "害怕的時候，就把蓋子闔緊": "calm",
    "上去之前，我們一起敲三下": "happy", "我們幫你想辦法回去": "happy", "大家的東西都拿回來了": "happy",
}


# 沒有可唸的字的句子，配音改唸替代（字幕照原文）
# 影片版改字（作者 2026-11-10：「顧著」的著唸不出輕聲要避開；單一個「嗯」很怪，改成「是啊」之類）。字幕與配音一起改。
TEXT_SUB = {
    "島上的人一直把重要的東西放在箱子裡。所以醒過來的寶箱怪，也一直替大家顧著這些東西。": "島上的人一直把重要的東西放在箱子裡。所以醒過來的寶箱怪，也一直替大家保管這些東西。",
    "謝謝你們顧著他。我帶他回家。": "謝謝你們照顧他。我帶他回家。",
    "……我會繼續幫你們顧著。": "……我會繼續幫你們顧好。",
    "……嗯。": "……是啊。",
}
SAY_SUB = {"……？": "嗯？",
           # 配音把「縫」唸成二聲，換同音字「奉」唸四聲（作者 2026-11-10 標）
           "這扇門會把人送到雲上。你就是從它的縫掉下來的。": "這扇門會把人送到雲上。你就是從它的奉掉下來的。"}  # 沒有可唸的字，配音唸「嗯？」，字幕照原文
EMO_SUB = {"嗯？": "surprised", "……是啊。": "sad", "謝謝你們照顧他。我帶他回家。": "happy", "……我會繼續幫你們顧好。": "happy"}


def clean(text):
    t = text.strip()
    if t in SAY_SUB: return SAY_SUB[t], False
    m = re.match(r"^（[^）]*）(.+)$", t)
    if m and m.group(1).strip(): return m.group(1).strip(), False  # 舞台指示＋台詞
    m = re.match(r"^（(.+)）$", t)
    if m: return m.group(1).strip(), True  # 整句內心獨白
    return t, False


def emotion(role, text, inner):
    if text in EMO_SUB: return EMO_SUB[text]
    if text in EMO: return EMO[text]  # 完全相同的句子優先（「嗯。」與「……嗯。」語氣不同）
    t = text.lstrip("…")
    for k, e in EMO.items():
        if t.startswith(k.lstrip("…")): return e
    if inner: return "calm"
    return DEFAULT_EMO.get(role, "neutral")


def tts(text, voice, emo, dst):
    if dst.exists() and dst.stat().st_size > 0: return
    body = json.dumps({"text": text, "voice": voice, "format": "mp3", "emotion": emo}).encode()
    req = urllib.request.Request("http://192.168.11.11:8072/tts", data=body, method="POST",
                                 headers={"Content-Type": "application/json", "X-API-Key": KEY})
    dst.write_bytes(urllib.request.urlopen(req, timeout=300).read())


jobs = []
for s in SB:
    for i, (role, text) in enumerate(s["lines"]):
        text = TEXT_SUB.get(text, text)
        say, inner = clean(text)
        emo = emotion(role, say, inner)
        h = hashlib.md5(f"{CAST[role]}|{emo}|{say}".encode()).hexdigest()[:6]
        jobs.append(dict(shot=s["no"], idx=i, role=role, text=text, say=say, inner=inner, emotion=emo,
                         voice=CAST[role], file=f"{s['no']:02d}_{i:02d}_{h}.mp3"))
print(len(jobs), "句")
fails = []
with cf.ThreadPoolExecutor(int(os.environ.get("LANES", "3"))) as ex:
    futs = {ex.submit(tts, j["say"], j["voice"], j["emotion"], OUT / j["file"]): j for j in jobs}
    for n, f in enumerate(cf.as_completed(futs), 1):
        try: f.result()
        except Exception as e: fails.append(futs[f]["file"]); print("失敗", futs[f]["file"], e)
        if n % 20 == 0: print(n, "/", len(jobs), flush=True)
for j in jobs:
    p = OUT / j["file"]
    j["secs"] = round(float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                           capture_output=True, text=True).stdout or 0), 2) if p.exists() else None
json.dump(jobs, open(OUT / "timeline.json", "w"), ensure_ascii=False, indent=1)
ok = [j for j in jobs if j["secs"]]
print(f"完成 {len(ok)}/{len(jobs)} 句，台詞總長 {sum(j['secs'] for j in ok)/60:.1f} 分鐘；失敗 {len(fails)}")
# 清掉語氣或台詞改過後留下的舊音檔
keep = {j["file"] for j in jobs} | {"timeline.json"}
old = [p for p in OUT.iterdir() if p.name not in keep]
for p in old: p.unlink()
print("清掉舊音檔", len(old))
