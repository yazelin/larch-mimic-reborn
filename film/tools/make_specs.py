"""從 film/segments.json ＋ film/motion.py 產出每段 H3 的 spec（第一批：每段前 11 秒）。
  python3 film/tools/make_specs.py   → film/h3/seg<NN>/spec.json（首幀、靜音、spec）
首幀：原本的 CG 讀 film/cg/<鍵>.webp，新補的讀 art/cg/film_<id>_v<最新>.webp；縮放後置中裁成 1344x768。"""
import glob, json, subprocess, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "film"))
from motion import CHARS, M  # noqa: E402

W, H, MAXD = 1344, 768, 11.0
STYLE = ("a 2D hand-drawn children's picture-book illustration in watercolor and colored pencil, soft warm light with pink-purple "
         "and warm yellow tones, animated like gentle hand-drawn 2D animation that keeps the painted paper texture, soft outlines "
         "and colors of <Picture 1>")
COMMON = ["None of the treasure chests ever grows arms, legs, a mouth or a face; chests move only by opening and closing their lids.",
          "The colors, light and painted style stay exactly as in <Picture 1> for the whole clip.",
          "No text, letters or signs appear anywhere.", "No extra characters appear."]


def frame_src(cg):
    if (ROOT / "film/cg" / f"{cg}.webp").exists(): return ROOT / "film/cg" / f"{cg}.webp"
    vs = sorted(glob.glob(str(ROOT / f"art/cg/film_{cg}_v*.webp")), key=lambda p: int(p.rsplit("_v", 1)[1].split(".")[0]))
    return Path(vs[-1])


def first_frame(src, dst):
    im = Image.open(src).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    im.crop((x, y, x + W, y + H)).save(dst)


segs = json.load(open(ROOT / "film/segments.json"))
out = []
for n, g in enumerate(segs):
    if g["mode"] != "h3": continue
    who, cam, act = M[n]
    d = ROOT / "film/h3" / f"seg{n:02d}"; d.mkdir(parents=True, exist_ok=True)
    first_frame(frame_src(g["cg"]), d / "first.png")
    dur = min(g["secs"], MAXD)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", str(dur + 1), str(d / "silence.wav")], check=True)
    spec = {"duration": dur, "size": [W, H], "seed": 20261111 + n, "steps": 14, "draft": True, "style": STYLE,
            "setting": "the scene shown in <Picture 1>", "first_frame": "first.png",
            "subjects": [{"key": k, "desc": CHARS[k]} for k in who],
            "audio": {"fixed": {"file": "silence.wav"}},
            "shots": [{"camera": cam, "action": act, "dialogue": []}],
            "constraints": COMMON, "soundscape": "Silence.", "music": "N/A"}
    (d / "spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    out.append(str(d / "spec.json"))
(ROOT / "film/h3/batch1.txt").write_text("\n".join(out))
print(len(out), "段")
