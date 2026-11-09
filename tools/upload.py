# -*- coding: utf-8 -*-
"""把素材傳上 Larch 媒體庫（REST POST /media），結果記在 assets/media.json（名字 → {id,url}），已傳過的跳過。
金鑰在 ~/.config/larch/key，不進 repo。  python3 tools/upload.py 檔案:名字:分類 …"""
import base64, json, mimetypes, os, sys, time, urllib.request
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PID = 'project-993a4982-d653-4f55-a511-5950e7fda343'
KEY = open(os.path.expanduser('~/.config/larch/key')).read().strip()
DB = os.path.join(R, 'assets/media.json')
db = json.load(open(DB)) if os.path.exists(DB) else {}
MIME = {'.webp': 'image/webp', '.png': 'image/png', '.mp3': 'audio/mpeg', '.jpg': 'image/jpeg'}
for arg in sys.argv[1:]:
    path, name, cat = arg.split(':')
    if name in db: print(name, '已傳過', db[name]['url']); continue
    ext = os.path.splitext(path)[1]
    body = {'name': name + ext, 'mimeType': MIME[ext], 'base64': base64.b64encode(open(os.path.join(R, path), 'rb').read()).decode(), 'category': cat}
    for n in range(3):
        try:
            req = urllib.request.Request(f'https://larch.ink/api/agent/projects/{PID}/media', method='POST', data=json.dumps(body).encode(),
                                         headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
            a = json.load(urllib.request.urlopen(req, timeout=300))['asset']
            db[name] = {'id': a['id'], 'url': a['url']}; json.dump(db, open(DB, 'w'), ensure_ascii=False, indent=1)
            print(name, 'OK', a['id']); break
        except Exception as e:
            print(name, f'第{n+1}次', repr(e)[:200]); time.sleep(10)
