"""照台詞把整部片剪起來（片長由配音決定）。
  python3 film/tools/assemble.py            → film/out/轉生成寶箱怪的我_1080p.mp4
1. 畫面：每段 H3（seg<NN>/clip.mp4，有後半段就接 seg<NN>b 並去掉重疊的 22 格），對到台詞秒數：短了放慢（最多 1.35 倍，再不夠停在最後一格）、長了裁掉；
   沒有 H3 成品或 4 秒以下的段用 CG 慢慢推近。1344x768 放大到 1920x1080。
2. 聲音：配音照 timeline 的秒數排（句間 0.35 秒）；敲三下段與「叩、叩、叩」放敲擊音效；配樂依章節，台詞期間壓低。
3. 字幕（霞鶩文楷）＋片尾 AI 生成標示，最後響度 -16 LUFS。"""
import json, subprocess, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "film/out"; (OUT / "seg").mkdir(parents=True, exist_ok=True)
SR, FPS, W, H = 48000, 24, 1920, 1080
GAP, LEAD, TAIL22 = 0.35, 0.3, 22
SEGS = json.load(open(ROOT / "film/segments.json"))
TL = json.load(open(ROOT / "film/voice/timeline.json"))
BY = {}
for j in TL: BY.setdefault(j["shot"], []).append(j)
FONT_DIR = ROOT / "film/fonts"
BGM = {"序章": "bgm-opening", "第一章　村口": "bgm-explore", "插曲　島上的回憶": "bgm-explore", "第二章　營地": "bgm-explore",
       "第三章　遺跡": "bgm-explore", "第四章　騎火焰飛龍": "bgm-explore", "第五章　雲端高台": "bgm-battle", "尾聲": "bgm-ending"}
SB = {s["no"]: s for s in json.load(open(ROOT / "film/storyboard.json"))}
END_SECS = 6.0


def sh(*a): subprocess.run(a, check=True)


def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                        capture_output=True, text=True).stdout)


def still(cg):
    p = ROOT / "film/cg" / f"{cg}.webp"
    if p.exists(): return p
    vs = sorted((ROOT / "art/cg").glob(f"film_{cg}_v*.webp"), key=lambda x: int(x.stem.rsplit("_v", 1)[1]))
    return vs[-1]


SCALE = f"scale={W}:-2:flags=lanczos,crop={W}:{H},setsar=1,fps={FPS}"


def render_seg(n, g, dst):
    secs = g["secs"]
    d = ROOT / "film/h3" / f"seg{n:02d}"
    if g["mode"] == "h3" and (d / "clip.mp4").exists():
        parts = [d / "clip.mp4"]
        if (ROOT / "film/h3" / f"seg{n:02d}b/clip.mp4").exists(): parts.append(ROOT / "film/h3" / f"seg{n:02d}b/clip.mp4")
        if len(parts) == 2:
            src = OUT / "seg" / f"{n:02d}_join.mp4"
            sh("ffmpeg", "-y", "-v", "error", "-i", str(parts[0]), "-i", str(parts[1]), "-filter_complex",
               f"[1:v]trim=start_frame={TAIL22},setpts=PTS-STARTPTS[b];[0:v][b]concat=n=2:v=1:a=0[v]", "-map", "[v]",
               "-c:v", "libx264", "-crf", "14", str(src))
        else:
            src = parts[0]
        cd = dur(src); f = min(max(secs / cd, 1.0), 1.35)
        vf = f"setpts={f:.4f}*PTS,{SCALE},tpad=stop_mode=clone:stop_duration={max(0, secs - cd * f) + 0.5:.2f},trim=duration={secs:.3f}"
        sh("ffmpeg", "-y", "-v", "error", "-i", str(src), "-an", "-vf", vf, "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(dst))
    else:
        nfr = int(round(secs * FPS))
        vf = (f"scale={W * 2}:-2:flags=lanczos,crop={W * 2}:{H * 2},zoompan=z='1+0.06*on/{nfr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
              f"d={nfr}:s={W}x{H}:fps={FPS},setsar=1")
        sh("ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(still(g["cg"])), "-vf", vf, "-frames:v", str(nfr),
           "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(dst))


def load(p, vol=1.0):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32) * vol


def put(buf, x, t):
    i = int(t * SR); j = min(len(buf), i + len(x)); buf[i:j] += x[:j - i]


def ass_time(t): return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def main():
    starts, t = [], 0.0
    for g in SEGS: starts.append(t); t += g["secs"]
    total = t + END_SECS
    # 1. 畫面
    lst = []
    for n, g in enumerate(SEGS):
        dst = OUT / "seg" / f"{n:02d}.mp4"
        render_seg(n, g, dst); lst.append(f"file '{dst}'")
        print("畫面", n, g["cg"], g["mode"], g["secs"], flush=True)
    endv = OUT / "seg" / "end.mp4"
    sh("ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=0x1d1822:s={W}x{H}:r={FPS}:d={END_SECS}", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(endv))
    lst.append(f"file '{endv}'")
    (OUT / "list.txt").write_text("\n".join(lst))
    sh("ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(OUT / "list.txt"), "-c", "copy", str(OUT / "video.mp4"))
    # 2. 聲音
    voice = np.zeros(int(total * SR) + SR, np.float32); sfx = voice.copy(); speak = np.zeros_like(voice, bool)
    knock = load(ROOT / "assets/audio/sfx_knock1.mp3")
    subs = []
    for n, g in enumerate(SEGS):
        t = starts[n] + LEAD
        lines = BY.get(g["shot"], [])
        if not g["lines"] and SB[g["shot"]]["card"].startswith("@knock"):
            v = 0.5 if "小鎖" in SB[g["shot"]]["card"] else 1.0
            for k in range(3): put(sfx, knock * v, starts[n] + 0.6 + 0.42 * k)
        for i in g["lines"]:
            j = lines[i - 1]; x = load(ROOT / "film/voice" / j["file"])
            if j["text"].startswith("叩、叩、叩"):
                loud = 1.0 if "四個寶箱" in j["text"] else 0.8
                for k in range(3): put(sfx, knock * loud, t + 0.05 + 0.42 * k)
                if "四個寶箱" in j["text"]:
                    for k in range(3): put(sfx, knock * 0.6, t + 0.08 + 0.42 * k)
            put(voice, x, t); a = int(t * SR); speak[a:a + len(x)] = True
            sp = "" if j["role"] == "旁白" else j["role"]
            subs.append((t, t + len(x) / SR + 0.25, sp, j["text"]))
            t += len(x) / SR + GAP
    bgm = np.zeros_like(voice); ch_ranges = []
    for n, g in enumerate(SEGS):
        ch = SB[g["shot"]]["chapter"]
        if not ch_ranges or ch_ranges[-1][0] != ch: ch_ranges.append([ch, starts[n], starts[n] + g["secs"]])
        else: ch_ranges[-1][2] = starts[n] + g["secs"]
    ch_ranges[-1][2] = total
    for ch, a, b in ch_ranges:
        m = load(ROOT / "assets/audio" / f"{BGM[ch]}.mp3"); need = int((b - a) * SR)
        m = np.tile(m, need // len(m) + 1)[:need]
        fade = int(1.0 * SR); env = np.ones(need, np.float32); env[:fade] = np.linspace(0, 1, fade); env[-fade:] = np.linspace(1, 0, fade)
        put(bgm, m * env, a)
    duck = np.where(speak, 0.12, 0.30).astype(np.float32)
    k = int(0.4 * SR); duck = np.convolve(duck, np.ones(k, np.float32) / k, mode="same")
    mix = voice + sfx * 0.9 + bgm * duck
    mix = np.clip(mix, -1, 1).astype(np.float32)
    (OUT / "mix.f32").write_bytes(mix.tobytes())
    sh("ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", str(OUT / "mix.f32"),
       "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(SR), str(OUT / "mix.wav"))
    # 3. 字幕與片尾
    ass = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "", "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
           "Style: Sub,LXGW WenKai TC,54,&H00FFFFFF,&H00FFFFFF,&H00402433,&H80000000,0,0,0,0,100,100,1,0,1,3.2,1.2,2,120,120,62,1",
           "Style: End,LXGW WenKai TC,52,&H00F2E8EF,&H00F2E8EF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,5,160,160,0,1",
           "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for a, b, sp, tx in subs:
        name = f"{{\\c&H00D6A6F2&}}{sp}{{\\c&H00FFFFFF&}}　" if sp else ""
        ass.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Sub,,0,0,0,,{name}{tx}")
    e0 = total - END_SECS
    credit = ("轉生成寶箱怪的我\\N\\N影像：MiniMax H3（AI 生成）　插圖：AI 生成\\N配音：larch-tts（AI 生成）　音效：Larch 內建音效\\N"
              "改編自 Larch 官方範例《Pulut 大冒險 3D》")
    ass.append(f"Dialogue: 0,{ass_time(e0 + 0.3)},{ass_time(total)},End,,0,0,0,,{{\\fad(600,600)}}{credit}")
    (OUT / "subs.ass").write_text("\n".join(ass), encoding="utf-8")
    final = OUT / "轉生成寶箱怪的我_1080p.mp4"
    sh("ffmpeg", "-y", "-v", "error", "-i", str(OUT / "video.mp4"), "-i", str(OUT / "mix.wav"),
       "-vf", f"subtitles={OUT / 'subs.ass'}:fontsdir={FONT_DIR}", "-map", "0:v", "-map", "1:a",
       "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", str(final))
    print("完成", final, round(dur(final), 1), "秒")


if __name__ == "__main__":
    main()
