# -*- coding: utf-8 -*-
"""《轉生成寶箱怪的我》的配樂：走 .11 的 gemini-web /api/music（做法照 ~/larch-handoff/tools/music.py），產完切循環、壓到 -16 LUFS。
網址讀環境變數 GEMINI_WEB_MUSIC_URL（沒設就從 ~/larch-eleven-minutes/art/music.py 讀），金鑰從 ~/.bashrc 的 GEMINI_IMAGE_KEY 讀，都不進 repo。
  python3 tools/music.py gen [名字…]   → art/music_raw/<名字>.mp3（不進 repo）
  python3 tools/music.py loop [名字…]  → assets/audio/bgm-<名字>.mp3
"""
import base64, importlib.util, json, os, re, ssl, subprocess, sys, threading, urllib.request
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW, OUT = os.path.join(R, 'art/music_raw'), os.path.join(R, 'assets/audio')
URL = os.environ.get('GEMINI_WEB_MUSIC_URL') or re.search(r"^URL = '([^']+)'", open(os.path.expanduser('~/larch-eleven-minutes/art/music.py')).read(), re.M).group(1)
CTX = ssl._create_unverified_context()   # 內網自簽憑證
# 共同核心：同一組樂器（木琴、撥弦、小鐘琴）讓整部聽起來是同一個島
CORE = 'marimba and pizzicato strings with a little glockenspiel, a playful hopping five-note motif, cozy toy-like island, a sleepy treasure chest monster'
TRACKS = {
    'title': f'Main title theme: {CORE}, warm woodwinds (flute and clarinet) carry the melody, curious and gently adventurous, sunset over a tiny island, 92 BPM, major key, instrumental, no vocals, loopable',
    'opening': f'Prologue: music box and soft celesta play the five-note motif slowly, then {CORE} joins quietly, a creature waking up confused in the morning, mysterious but cute, 76 BPM, instrumental, no vocals, loopable',
    'explore': f'Exploration: {CORE}, ukulele strumming and light hand percussion, cheerful wandering across meadows, ruins and a camp, bright and relaxed, 104 BPM, major key, instrumental, no vocals, loopable',
    'battle': f'Boss fight on a cloud plateau: {CORE} turned urgent, staccato brass, taiko and snare drums, fast pizzicato runs, playful but tense, not scary, 136 BPM, minor key, instrumental, no vocals, loopable',
    'ending': f'Ending: acoustic guitar and soft piano play the five-note motif tenderly, {CORE} far in the background, a ship sailing away, chests closing their lids to sleep again, warm and peaceful, 70 BPM, major key, instrumental, no vocals, loopable',
}


def key():
    for line in open(os.path.expanduser('~/.bashrc'), encoding='utf-8'):
        if line.startswith('export GEMINI_IMAGE_KEY='): return line.split('=', 1)[1].strip().strip('"')
    raise SystemExit('找不到 GEMINI_IMAGE_KEY')


def one(name, k, tries=4):
    os.makedirs(RAW, exist_ok=True)
    for n in range(tries):
        req = urllib.request.Request(URL, method='POST', data=json.dumps({'prompt': TRACKS[name], 'timeout': 720}).encode(),
                                     headers={'Content-Type': 'application/json', 'x-goog-api-key': k})
        try: d = json.load(urllib.request.urlopen(req, timeout=900, context=CTX))
        except Exception as e: print(f'{name} 第{n + 1}次 例外 {e!r}', flush=True); continue
        if d.get('success'):
            open(os.path.join(RAW, f'{name}.mp3'), 'wb').write(base64.b64decode(d['audio']))
            print(f"{name} 好了 {d.get('elapsed_seconds', 0):.0f} 秒", flush=True); return
        print(f"{name} 第{n + 1}次 失敗 {d.get('message') or d.get('error')}", flush=True)
    print(f'{name} 四次都失敗', flush=True)


def loop(name):
    spec = importlib.util.spec_from_file_location('tybgm', os.path.expanduser('~/larch-taoyuan/bgm.py'))
    B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
    src = os.path.join(RAW, f'{name}.mp3'); os.makedirs(OUT, exist_ok=True); out = os.path.join(OUT, f'bgm-{name}.mp3')
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout)
    B.LEN = min(90, int(dur) - 4)
    base, best = B.find_start(src), None
    for off in [0, .5, -.5, 1, -1, 1.5, -1.5, 2, -2]:
        s = max(0.0, base + off); B.make(src, s, out); z, d = B.seam_score(out)
        if best is None or abs(z) < abs(best[0]): best = (z, s, d)
        if abs(z) < 3: break
    z, s, d = best; B.make(src, s, out)
    print(f'{name} 原曲 {dur:.0f} 秒 → 循環 {d:.1f} 秒，從 {s:.0f} 秒起，接縫 z={z:+.1f}', flush=True)


def full(name):
    src = os.path.join(RAW, f'{name}.mp3'); out = os.path.join(OUT, 'full', f'{name}.mp3'); os.makedirs(os.path.dirname(out), exist_ok=True)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-af', f'loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=out:st={dur - 3:.2f}:d=3',
                    '-ar', '44100', '-b:a', '192k', out], check=True)
    print(f'{name} 完整版 {dur:.0f} 秒', flush=True)


if __name__ == '__main__':
    cmd, names = sys.argv[1], sys.argv[2:] or list(TRACKS)
    if cmd == 'gen':
        k = key(); ts = [threading.Thread(target=one, args=(n, k)) for n in names]
        for t in ts: t.start()
        for t in ts: t.join()
    else:
        for n in names: (full if cmd == 'full' else loop)(n)
