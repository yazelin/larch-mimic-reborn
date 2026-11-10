"""4-3 重拍（作者：seed1 變色、seed2 翅膀在抖）：滑翔、慢拍一次、鎖顏色；DMAD 與 14 步各 2 seed。"""
import json, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "film/test/t3_b43_s2"
base = json.loads((SRC / "spec.json").read_text(encoding="utf-8"))
base["shots"][0]["camera"] = "The camera glides slowly alongside the dragon at the same speed, keeping it in the upper left of the frame; the framing stays steady."
base["shots"][0]["action"] = ("Starting from <Picture 1>, the dragon glides calmly forward with both wings spread wide and held steady. "
    "Midway through the clip it makes one slow, smooth downstroke with both wings and then spreads them wide again, "
    "the wing membranes staying sharp and clear. The four chests on its back rise and settle gently once with that "
    "wingbeat; the nightcap's pompom bobs. Far below, the clouds drift slowly past and the island slides a little "
    "toward the lower right. Sunlight glitters softly on the sea.")
base["constraints"] = base["constraints"] + [
    "The colors, the warm dusk light and the pink-purple sky stay exactly as in <Picture 1> for the whole clip.",
    "The wings move smoothly and slowly, with no trembling or flicker."]
for tag, extra in [("dmad", {"draft": True}), ("full", {"draft": False, "steps": 14})]:
    for i, seed in enumerate([20261112, 20261113]):
        d = ROOT / f"film/test/r_b43_{tag}_s{i+1}"
        d.mkdir(exist_ok=True)
        for f in ("first.png", "silence.wav"):
            shutil.copy(SRC / f, d / f)
        s = dict(base, seed=seed, **extra)
        if not s.get("draft"): s.pop("draft", None)
        (d / "spec.json").write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
        print(d / "spec.json")
