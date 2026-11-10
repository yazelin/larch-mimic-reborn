"""試拍 3 鏡 x 2 seed：首幀裁成 1344x768、靜音音軌、h3_shot spec。
用法：python3 film/tools/make_test_specs.py  → film/test/<鏡>_s<n>/spec.json
"""
import json, subprocess
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
CG = ROOT / "art/cg"
OUT = ROOT / "film/test"
W, H = 1344, 768

STYLE = ("a 2D hand-drawn children's picture-book illustration in watercolor and colored pencil, soft warm dusk light "
         "with a pink-purple sky and warm yellow highlights, animated like gentle hand-drawn 2D animation that keeps the "
         "painted paper texture, soft outlines and colors of <Picture 1>")

MIMIC = ("the hero mimic, a red wooden treasure chest framed with pastel pink-purple metal bands and a square pink-purple "
         "latch on the front; it has no arms, no legs, no mouth and no face: only a pair of round cartoon eyes peeking out "
         "of the dark gap between the lid and the box")

SHOTS = {
    "t1_b11": dict(
        cg="b11b_v1.webp", duration=5.0, crop_y=None,
        setting="a cobblestone village entrance with a wooden signpost, a bench and flower beds at dusk",
        subjects=[
            {"key": "mimic", "desc": MIMIC},
            {"key": "elder", "desc": "the village elder, a blocky toy-like little man with orange hair and sideburns, a purple police cap with a gold badge and a blue uniform"},
        ],
        camera="The camera holds a static wide shot on a tripod.",
        action=("Starting from <Picture 1>, the mimic finishes its hop in mid-air on the left, lands on the cobblestones with a "
                "small bounce, and its lid flaps open and shut once as it hops one more short step toward the elder. "
                "Its eyes stay inside the gap under the lid. On the right, the elder finishes turning his head and upper body "
                "to the left, blinks twice in surprise, and lowers his raised hands to his sides. Grass in the foreground "
                "sways gently in the breeze."),
        constraints=["The mimic never grows arms, legs, a mouth or a face; it moves only by opening and closing its lid.",
                     "No text, letters or signs appear anywhere."],
    ),
    "t2_b27": dict(
        cg="b27a_v1.webp", duration=5.0, crop_y=None,
        setting="a grassy slope under a big apple tree near a campsite at dusk",
        subjects=[
            {"key": "akou", "desc": "Akou, a round chubby brown wooden treasure chest with gold bands, wearing a soft lavender nightcap with a white pompom; no arms, no legs, only round eyes in the gap under the lid"},
            {"key": "mimic", "desc": MIMIC + ", standing in the back"},
            {"key": "grandpa", "desc": "Grandpa Chest, a big dark-brown old treasure chest with white moss along its lid like a beard and thick white eyebrows over squinting eyes"},
        ],
        camera="The camera holds a static wide shot on a tripod.",
        action=("Starting from <Picture 1>, Akou has just rolled down the slope and bumps into the tree trunk; the whole chest "
                "rebounds a little and wobbles left and right twice before settling, its nightcap flopping. The apple tree "
                "shakes and three red apples drop from the branches, bounce on the grass and roll down the slope. A puff of "
                "dust drifts and fades. In the back, the mimic and Grandpa Chest stay in place and blink."),
        constraints=["None of the chests grows arms, legs, a mouth or a face.",
                     "Exactly three chests are in the shot for the whole clip.", "No text appears anywhere."],
    ),
    "t3_b43": dict(
        cg="b43a3_v1.webp", duration=6.0, crop_y=0.001,
        setting="high in the dusk sky above the sea, a small green island with a village, windmill and ruins far below",
        subjects=[
            {"key": "dragon", "desc": "a red-orange fire dragon with large wings, flying"},
            {"key": "chests", "desc": "four treasure-chest creatures stacked on the dragon's back: Grandpa Chest with a white moss beard in front, the hero mimic (red chest with pink-purple bands), Akou with a lavender nightcap, and little Xiao Suo on top with its lid shut tight; no arms, no legs"},
        ],
        camera="The camera slowly tracks along with the dragon, keeping it in the upper left, with a very slight push-in.",
        action=("Starting from <Picture 1>, the dragon glides forward and beats its wide wings down and up twice in a slow, "
                "steady rhythm. The four chests on its back sway gently with each wingbeat; the nightcap's pompom bounces. "
                "Far below, the clouds drift slowly past and the island slides a little toward the lower right. Sunlight "
                "glitters on the sea."),
        constraints=["Exactly four chests stay on the dragon's back for the whole clip; none falls off and no extra chest appears.",
                     "The dragon keeps two wings and one head.", "No text appears anywhere."],
    ),
}
SEEDS = [20261110, 20261111]


def first_frame(src, dst, crop_y):
    im = Image.open(src).convert("RGB")
    s = W / im.width
    im = im.resize((W, round(im.height * s)), Image.LANCZOS)
    if im.height < H:
        s2 = H / im.height
        im = im.resize((round(im.width * s2), H), Image.LANCZOS)
        x = (im.width - W) // 2
        im = im.crop((x, 0, x + W, H))
    else:
        y = round((crop_y or (im.height - H) / 2 / im.height) * im.height) if crop_y else (im.height - H) // 2
        y = max(0, min(y, im.height - H))
        im = im.crop((0, y, W, y + H))
    im.save(dst)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, d in SHOTS.items():
        for i, seed in enumerate(SEEDS):
            dd = OUT / f"{name}_s{i + 1}"
            dd.mkdir(exist_ok=True)
            first_frame(CG / d["cg"], dd / "first.png", d["crop_y"])
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
                            "-t", str(d["duration"] + 1), str(dd / "silence.wav")], check=True)
            spec = {
                "duration": d["duration"], "size": [W, H], "seed": seed, "steps": 14, "draft": True,
                "style": STYLE, "setting": d["setting"], "first_frame": "first.png",
                "subjects": d["subjects"],
                "audio": {"fixed": {"file": "silence.wav"}},
                "shots": [{"camera": d["camera"], "action": d["action"], "dialogue": []}],
                "constraints": d["constraints"],
                "soundscape": "Silence.", "music": "N/A",
            }
            (dd / "spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
            print(dd)


if __name__ == "__main__":
    main()
