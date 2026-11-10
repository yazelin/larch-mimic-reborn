"""選角試聽：每個角色 2–3 個候選音色，各唸一句劇中台詞，存到 film/audition/<角色>__<voice>.mp3，並量基頻中位數（判斷男女聲）。
走 .11 larch-tts-bridge（不動上架的 Larch 專案）。慈祥長者 Kind-hearted_Elder 標 male 實際是女聲，不列入男性長輩。"""
import concurrent.futures as cf, json, os, subprocess, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "film/audition"; OUT.mkdir(parents=True, exist_ok=True)
KEY = open(os.path.expanduser("~/.config/larch-tts/key")).read().strip()
Z = "Chinese (Mandarin)_"
CAST = {
    "旁白": ("寶箱怪大部分的時間都在睡覺。睡著的時候幾乎不用吃東西，一整年只要幾顆蘋果就夠了。", "calm",
             [Z + "Radio_Host", Z + "Lyrical_Voice", Z + "Wise_Women"]),
    "寶箱怪": ("後來我把島上的寶箱一個一個找出來。每一個都是族人，每一個都在睡覺。", "neutral",
              [Z + "Gentle_Youth", Z + "Pure-hearted_Boy", Z + "Sincere_Adult"]),
    "長老": ("……你醒了啊。從我爺爺的爺爺那時候就在用你，總算等到你醒了。", "happy",
            [Z + "Humorous_Elder", "ttv-voice-2026102118233626-JAIJKfvR", "Larch_Mandarin_Dad"]),
    "箱爺爺": ("先不說這個。我身上收的，是村子裡好幾代人交給我顧的東西，誰敢拿？", "angry",
              [Z + "Humorous_Elder", "ttv-voice-2026102118233626-JAIJKfvR", "Larch_Mandarin_Uncle"]),
    "阿扣": ("我一直夢到有人敲我的蓋子，每次三下，敲完還說「明天再來」。", "neutral",
            [Z + "Cute_Spirit", Z + "Straightforward_Boy", Z + "Southern_Young_Man"]),
    "小鎖": ("他們剛剛就站在我前面。那隻史萊姆聞了我一下，又跳走了。", "fearful",
            [Z + "BashfulGirl", Z + "Soft_Girl", "Larch_Mandarin_Child"]),
    "市集老闆": ("以前你天天擋在我攤子前面曬太陽，害我少做好幾筆生意。現在換你去顧大家了。", "neutral",
              [Z + "Warm-HeartedAunt", Z + "Kind-hearted_Antie"]),
    "少年獵人": ("這座島寶箱超多，隨便撬都有錢。", "happy",
              [Z + "Unrestrained_Young_Man", Z + "Straightforward_Boy"]),
    "少女獵人": ("會走的寶箱，裡面一定是好東西。", "happy",
              [Z + "Crisp_Girl", Z + "ExplorativeGirl", "Arrogant_Miss"]),
    "Pulut": ("我住在雲的上面，掉下來的時候被他們撿到。他們說幫他們找寶箱，就帶我回家。", "sad",
              [Z + "Cute_Spirit", "Larch_Mandarin_Child"]),
    "卡雅": ("謝謝你們顧著他。我帶他回家。", "calm",
            [Z + "Wise_Women", Z + "Sweet_Lady", Z + "Lyrical_Voice"]),
}


def tts(text, voice, emotion, dst):
    if dst.exists(): return
    body = json.dumps({"text": text, "voice": voice, "format": "mp3", "emotion": emotion}).encode()
    req = urllib.request.Request("http://192.168.11.11:8072/tts", data=body, method="POST",
                                 headers={"Content-Type": "application/json", "X-API-Key": KEY})
    dst.write_bytes(urllib.request.urlopen(req, timeout=300).read())


def f0(path):
    """用 ffmpeg 轉 16k wav 後以自相關估基頻中位數（Hz）。男聲約 85–180，女聲約 165–300。"""
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32)
    hz = []
    for i in range(0, len(x) - 640, 320):
        fr = x[i:i + 640]
        if np.sqrt((fr ** 2).mean()) < 500: continue
        fr = fr - fr.mean(); ac = np.correlate(fr, fr, "full")[639:]
        lo, hi = 16000 // 400, 16000 // 60
        k = lo + int(np.argmax(ac[lo:hi]))
        if ac[k] > 0.3 * ac[0]: hz.append(16000 / k)
    return round(float(np.median(hz))) if hz else None


jobs = []
for role, (text, emo, voices) in CAST.items():
    for v in voices:
        jobs.append((role, text, emo, v, OUT / f"{role}__{v.replace(Z, '').replace(' ', '_')}.mp3"))
with cf.ThreadPoolExecutor(3) as ex:
    futs = {ex.submit(tts, t, v, e, d): (r, v, d) for r, t, e, v, d in jobs}
    for f in cf.as_completed(futs):
        r, v, d = futs[f]
        try: f.result()
        except Exception as e: print("失敗", r, v, e)
res = []
for r, t, e, v, d in jobs:
    if d.exists():
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(d)],
                                   capture_output=True, text=True).stdout or 0)
        res.append(dict(role=r, voice=v, file=d.name, text=t, emotion=e, secs=round(dur, 2), f0=f0(d), chars=len(t)))
json.dump(res, open(OUT / "audition.json", "w"), ensure_ascii=False, indent=1)
for x in res: print(x["role"], x["voice"].replace(Z, ""), x["secs"], "秒", x["f0"], "Hz")
