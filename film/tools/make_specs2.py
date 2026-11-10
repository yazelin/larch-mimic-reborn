"""第二批之後的 spec：重抽（motion.RETAKE）與接後半段（前半段最後 22 格當開頭）。
  python3 film/tools/make_specs2.py retake 0 3 …     改寫這幾段的 spec（舊成品改名 clip_v<n>.mp4 保留），換 seed
  python3 film/tools/make_specs2.py cont 11 14 …      為這幾段做後半段 film/h3/seg<NN>b/（前半段要已經選定可用）
每個指令都把產出的 spec 路徑印出來，給 run_h3.sh 的清單用。"""
import json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "film"))
from motion import RETAKE, RETAKE2, CONT_ACTION  # noqa: E402
CHEST_KEYS = {"mimic", "grandpa", "akou", "xiaosuo", "chests"}
NO_CHEST_DROP = ("None of the treasure chests", "Only the two hunters", "Only the girl hunter")

H3 = ROOT / "film/h3"
SEGS = json.load(open(ROOT / "film/segments.json"))
TAIL = 22  # h3_shot 接力支援 5/22/39 格


def retake(n):
    d = H3 / f"seg{n:02d}"
    if (d / "clip.mp4").exists():
        k = 1
        while (d / f"clip_v{k}.mp4").exists(): k += 1
        shutil.move(d / "clip.mp4", d / f"clip_v{k}.mp4")
    s = json.loads((d / "spec.json").read_text(encoding="utf-8"))
    cam, act, extra = (RETAKE2.get(n) or RETAKE[n]) if ROUND == 2 else RETAKE[n]
    s["shots"][0]["camera"], s["shots"][0]["action"] = cam, act
    s["constraints"] = [c for c in s["constraints"] if c not in extra and not any(c.startswith(k) for k in ("Exactly", "Only", "The whole", "The mimic stays", "It stays", "The map", "The red mimic", "Both", "The two hunters", "The girl hunter", "The island", "The market"))] + extra
    if not CHEST_KEYS & {x["key"] for x in s["subjects"]}:
        s["constraints"] = [c for c in s["constraints"] if not c.startswith(NO_CHEST_DROP)]
    s["seed"] = s["seed"] + 1000
    (d / "spec.json").write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
    return d / "spec.json"


def cont(n):
    a, b = H3 / f"seg{n:02d}", H3 / f"seg{n:02d}b"
    b.mkdir(exist_ok=True)
    clip = a / "clip.mp4"
    nf = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames",
                             "-of", "csv=p=0", str(clip)], capture_output=True, text=True).stdout.strip())
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(clip), "-vf", f"select=gte(n\\,{nf - TAIL})", "-vsync", "0",
                    "-c:v", "libx264", "-crf", "10", "-pix_fmt", "yuv420p", str(b / "tail22.mp4")], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(clip), "-vf", f"select=eq(n\\,{nf - 1})", "-vsync", "0", "-frames:v", "1",
                    str(b / "first.png")], check=True)
    s = json.loads((a / "spec.json").read_text(encoding="utf-8"))
    rest = round(SEGS[n]["secs"] - s["duration"] + TAIL / 24, 2)
    s["duration"] = max(rest, 4.0)
    s["first_clip"] = "tail22.mp4"
    s["seed"] = s["seed"] + 500
    act = CONT_ACTION.get(n) or s["shots"][0]["action"].replace("Starting from <Picture 1>,", "Continuing smoothly from <Picture 1>,", 1)
    s["shots"][0]["action"] = act + " The motion then slows and settles calmly toward the end."
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", str(s["duration"] + 1),
                    str(b / "silence.wav")], check=True)
    (b / "spec.json").write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
    return b / "spec.json"


ROUND = 2 if "--round2" in sys.argv else 1
if __name__ == "__main__":
    sys.argv = [a for a in sys.argv if a != "--round2"]
    fn = {"retake": retake, "cont": cont}[sys.argv[1]]
    for x in sys.argv[2:]: print(fn(int(x)))
