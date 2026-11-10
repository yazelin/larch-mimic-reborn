"""把影片配好的台詞語音傳上 Larch 媒體庫，做成 角色|台詞 → voiceUrl 對照表（film/voice/voice_map.json）。
另外補配影片路線沒走到的兩句分支台詞（接蘋果很少、選躲進蓋子）。
  python3 film/tools/push_voice.py
之後 tools/build_book.py（繪本卡）與 --push 時的序章、尾聲共用卡會讀這張表掛 voiceUrl。
上傳照 tools/upload.py 的 REST 做法；Larch 寫入整個帳號共用限流（約 12 次後 429，等 Retry-After）。"""
import base64, json, os, time, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PID = "project-993a4982-d653-4f55-a511-5950e7fda343"
KEY = open(os.path.expanduser("~/.config/larch/key")).read().strip()
TTS_KEY = open(os.path.expanduser("~/.config/larch-tts/key")).read().strip()
DB = ROOT / "assets/media.json"
VO = ROOT / "film/voice"
CAST = json.load(open(ROOT / "film/cast.json"))
EXTRA = [("阿扣", "……先墊墊肚子就好。", "sad", "x_2-6b.mp3"), ("少年獵人", "好硬……手好麻。", "sad", "x_5-I.mp3")]


def tts(text, voice, emo, dst):
    if dst.exists() and dst.stat().st_size: return
    req = urllib.request.Request("http://192.168.11.11:8072/tts", method="POST",
                                 data=json.dumps({"text": text, "voice": voice, "format": "mp3", "emotion": emo}).encode(),
                                 headers={"Content-Type": "application/json", "X-API-Key": TTS_KEY})
    dst.write_bytes(urllib.request.urlopen(req, timeout=300).read())


def upload(path, name, db):
    if name in db: return db[name]["url"]
    body = {"name": name + ".mp3", "mimeType": "audio/mpeg", "category": "voice",
            "base64": base64.b64encode(path.read_bytes()).decode()}
    for n in range(8):
        try:
            req = urllib.request.Request(f"https://larch.ink/api/agent/projects/{PID}/media", method="POST", data=json.dumps(body).encode(),
                                         headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
            a = json.load(urllib.request.urlopen(req, timeout=300))["asset"]
            db[name] = {"id": a["id"], "url": a["url"]}
            json.dump(db, open(DB, "w"), ensure_ascii=False, indent=1)
            return a["url"]
        except urllib.error.HTTPError as e:
            wait = int(e.headers.get("Retry-After") or 30) + 2 if e.code == 429 else 15
            print(name, e.code, f"等 {wait} 秒", flush=True); time.sleep(wait)
    raise RuntimeError("上傳失敗 " + name)


lines = json.load(open(VO / "timeline.json"))
items = [(j["role"], j["text"], VO / j["file"]) for j in lines]
for role, text, emo, fn in EXTRA:
    tts(text, CAST[role], emo, VO / fn)
    items.append((role, text, VO / fn))
db = json.load(open(DB)) if DB.exists() else {}
vmap = {}
for i, (role, text, path) in enumerate(items, 1):
    vmap[f"{role}|{text}"] = upload(path, "vo_" + path.stem, db)
    if i % 10 == 0: print(i, "/", len(items), flush=True)
json.dump(vmap, open(VO / "voice_map.json", "w"), ensure_ascii=False, indent=1)
print("完成", len(vmap), "句")
