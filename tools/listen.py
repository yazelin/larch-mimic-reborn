# -*- coding: utf-8 -*-
"""用 Gemini 代聽配樂：每首截前 90 秒、64k 單聲道，問固定清單，回 JSON。金鑰在 /home/ct/gemini/.env 的 NANOBANANA_GEMINI_API_KEY，不進 repo。
  python3 tools/listen.py 名字…   （讀 art/music_raw/<名字>.mp3）"""
import base64, json, os, subprocess, sys, tempfile, urllib.request
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = next(l.split('=', 1)[1].strip().strip('"') for l in open('/home/ct/gemini/.env') if l.startswith('NANOBANANA_GEMINI_API_KEY'))
sys.path.insert(0, os.path.join(R, 'tools'))
from music import TRACKS
Q = ('你是遊戲配樂審聽員。請只根據你聽到的聲音回答，用繁體中文，回 STRICT JSON：'
     '{"instruments":[聽到的樂器],"bpm_estimate":數字,"mood":"一句話","has_vocals":true/false,'
     '"matches_brief":0-10,"mismatch":"跟要求不一樣的地方，沒有就空字串","loopable":true/false}。要求是：')
for n in sys.argv[1:]:
    src = os.path.join(R, f'art/music_raw/{n}.mp3'); tmp = tempfile.mktemp(suffix='.mp3')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-t', '90', '-ac', '1', '-b:a', '64k', tmp], check=True)
    body = {'contents': [{'parts': [{'text': Q + TRACKS[n]}, {'inline_data': {'mime_type': 'audio/mp3', 'data': base64.b64encode(open(tmp, 'rb').read()).decode()}}]}],
            'generationConfig': {'responseMimeType': 'application/json'}}
    r = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={KEY}',
                               data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
    d = json.load(urllib.request.urlopen(r, timeout=180))
    print(n, d['candidates'][0]['content']['parts'][0]['text'].strip(), flush=True)
