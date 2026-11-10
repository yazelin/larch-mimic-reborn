"""從上架版（白板 sw-intro／sw-ending ＋ tools/build_book.py 的繪本卡）照一條固定路線排出分鏡清單。
每張 CG 一鏡；台詞照順序掛在當時那張 CG 底下。
  python3 film/tools/storyboard.py            → film/storyboard.json，並下載各鏡 CG 到 film/cg/
路線（互動段落挑一條）：地圖回憶六個全看、蘋果接很多（2-6a）、招式第一回合砸地、第二回合衝撞、第三回合敲三下。
"""
import importlib.util, json, os, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CPS = 4.2  # larch-tts 中文每秒約幾個字（之後用實際配音長度取代）
GAP = 0.5  # 句與句之間的停頓秒數

spec = importlib.util.spec_from_file_location("bb", ROOT / "tools/build_book.py")
bb = importlib.util.module_from_spec(spec); sys.argv = ["x"]; spec.loader.exec_module(bb)
book = {n["id"]: n["data"] for n in bb.nodes}
board = json.load(open(ROOT / "film/src/board-main.json"))
bn = board.get("board", board)
bn = {n["id"]: n["data"] for n in (bn["nodes"] if "nodes" in bn else bn["board"]["nodes"])}

ROUTE = ["sw-intro", "bk-1a", "@knock:箱爺爺", "bk-1b",
         "bk-m-well", "bk-m-fire", "bk-m-cat", "bk-m-nook", "bk-m-pond", "bk-m-mill",
         "bk-2a", "@knock:阿扣", "bk-2b", "@knock:阿扣", "bk-2c", "@apple", "bk-2d1", "bk-2e",
         "bk-3a", "@knock:小鎖", "bk-3b", "@knock:小鎖", "bk-3c", "bk-4",
         "bk-5a", "bk-5r1", "bk-5y", "bk-5r2", "bk-5u", "bk-5r3", "bk-5o", "sw-ending"]
CHAPTER = {"sw-intro": "序章", "bk-1a": "第一章　村口", "bk-m-well": "插曲　島上的回憶", "bk-2a": "第二章　營地",
           "bk-3a": "第三章　遺跡", "bk-4": "第四章　騎火焰飛龍", "bk-5a": "第五章　雲端高台", "sw-ending": "尾聲"}
KNOCK_CG = {"箱爺爺": "book_1-4", "阿扣": "book_2-3", "小鎖": "book_3-2"}

media = json.load(open(ROOT / "assets/media.json"))
url2key = {v["url"]: k for k, v in media.items() if isinstance(v, dict) and "url" in v}


def key_of(url):
    if url in url2key: return url2key[url]
    m = re.search(r"\d+_(.+)\.\w+$", url or "")
    return m.group(1) if m else None


shots, chapter = [], ""
for step in ROUTE:
    if step in CHAPTER: chapter = CHAPTER[step]
    if step.startswith("@knock:"):
        who = step.split(":")[1]
        shots.append(dict(chapter=chapter, cg=KNOCK_CG[who], card=step, lines=[], note=f"互動：敲三下（{who}）。影片演寶箱怪用蓋子敲三下，配叩叩叩音效。"))
        continue
    if step == "@apple":
        shots.append(dict(chapter=chapter, cg="book_A-0", card=step, lines=[], note="互動：接蘋果。影片演蘋果一顆顆掉進寶箱怪的蓋子。"))
        continue
    d = book.get(step) or bn[step]
    cur = key_of(d.get("background"))
    for L in d.get("dialogueLines") or [{"speaker": d.get("speaker"), "text": d.get("text")}]:
        k = key_of(L.get("background")) if L.get("background") else None
        if k and k != cur: cur = k
        if not shots or shots[-1]["cg"] != cur or shots[-1]["card"].startswith("@"):
            shots.append(dict(chapter=chapter, cg=cur, card=step, lines=[], note=""))
        shots[-1]["lines"].append([L.get("speaker") or "", L.get("text") or ""])

(ROOT / "film/cg").mkdir(parents=True, exist_ok=True)
total = 0
for i, s in enumerate(shots, 1):
    s["no"] = i
    chars = sum(len(re.sub(r"[（）()「」……，。？！、：；\s]", "", t)) for _, t in s["lines"])
    secs = round(chars / CPS + GAP * len(s["lines"]) + 1.0, 1) if s["lines"] else 4.0
    s["chars"], s["secs"] = chars, secs
    s["clips"] = max(1, -(-int(secs * 10) // 110))  # 單支 ≤ 11 秒，超過就接力拆成幾支
    total += secs
    f = ROOT / "film/cg" / f"{s['cg']}.webp"
    if not f.exists():
        u = media[s["cg"]]["url"] if s["cg"] in media else None
        if u: f.write_bytes(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read())
json.dump(shots, open(ROOT / "film/storyboard.json", "w"), ensure_ascii=False, indent=1)
print(f"{len(shots)} 鏡，H3 共 {sum(s['clips'] for s in shots)} 支，估計片長 {total/60:.1f} 分鐘")
for s in shots:
    print(s["no"], s["chapter"], s["cg"], s["secs"], s["clips"], len(s["lines"]))
