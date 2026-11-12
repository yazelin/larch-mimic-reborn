# -*- coding: utf-8 -*-
"""把 ui/ 底下的介面寫進 Larch（REST PUT /projects/:id/interface）。先讀現有的 html 當 expectedHtml，寫完讀回比對。
  python3 tools/push_ui.py [title dialogue choices menu gallery l3d]"""
import json, os, sys, urllib.request
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PID = 'project-993a4982-d653-4f55-a511-5950e7fda343'
KEY = open(os.path.expanduser('~/.config/larch/key')).read().strip()
FILES = {'l3d': 'ui/l3d.css', 'title': 'ui/title.html', 'dialogue': 'ui/dialogue.html', 'choices': 'ui/choices.css', 'menu': 'ui/menu.css', 'gallery': 'ui/gallery.css'}
H = {'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
def get():
    r = urllib.request.Request(f'https://larch.ink/api/agent/projects/{PID}', headers=H)
    return ((lambda d: d.get('project', d))(json.load(urllib.request.urlopen(r, timeout=300))).get('settings') or {}).get('customInterfaces') or {}
cur = get()
for s in sys.argv[1:] or list(FILES):
    html = open(os.path.join(R, FILES[s])).read()
    body = {'surface': s, 'html': html, 'enabled': True, 'expectedHtml': (cur.get(s) or {}).get('html', ''), 'summary': f'介面 {s} 換成手繪水彩版'}
    r = urllib.request.Request(f'https://larch.ink/api/agent/projects/{PID}/interface', method='PUT', data=json.dumps(body).encode(), headers=H)
    try: print(s, urllib.request.urlopen(r, timeout=300).status)
    except urllib.error.HTTPError as e: print(s, e.code, e.read()[:300])
after = get()
for s in sys.argv[1:] or list(FILES):
    print(s, '讀回一致' if (after.get(s) or {}).get('html') == open(os.path.join(R, FILES[s])).read() else '不一致', (after.get(s) or {}).get('enabled'))
