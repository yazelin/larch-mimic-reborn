"""用 9333 Chrome 開 Larch 預覽分頁做真實點擊與截圖（小遊戲在 sandbox iframe 裡，只能送真實滑鼠事件）。
  python3 film/tools/cdp_preview.py <預覽網址> <輸出資料夾> 動作…
動作：wait:秒、shot:名字、click:x比例,y比例（相對整個視窗）、text:要找的字（在主文件點含這段字的按鈕）、close"""
import base64, json, sys, time, urllib.request
import websocket

url, out = sys.argv[1], sys.argv[2]
t = json.load(urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:9333/json/new?" + url, method="PUT")))
ws = websocket.create_connection(t["webSocketDebuggerUrl"], suppress_origin=True, timeout=120)
mid = 0


def send(method, **params):
    global mid
    mid += 1; ws.send(json.dumps({"id": mid, "method": method, "params": params}))
    while True:
        m = json.loads(ws.recv())
        if m.get("id") == mid: return m.get("result", {})


send("Page.enable"); send("Page.bringToFront")
send("Emulation.setDeviceMetricsOverride", width=1280, height=720, deviceScaleFactor=1, mobile=False)
send("Emulation.setFocusEmulationEnabled", enabled=True)
W, H = 1280, 720
for act in sys.argv[3:]:
    k, _, v = act.partition(":")
    if k == "wait": time.sleep(float(v))
    elif k == "shot":
        d = send("Page.captureScreenshot", format="jpeg", quality=70)["data"]
        open(f"{out}/{v}.jpg", "wb").write(base64.b64decode(d)); print("截圖", v)
    elif k == "click":
        x, y = (float(a) for a in v.split(",")); x, y = x * W, y * H
        for typ in ("mousePressed", "mouseReleased"):
            send("Input.dispatchMouseEvent", type=typ, x=x, y=y, button="left", clickCount=1)
        print("點", round(x), round(y))
    elif k == "text":
        r = send("Runtime.evaluate", expression=f"(()=>{{const b=[...document.querySelectorAll('button,[role=button],a')].find(e=>e.innerText.includes({json.dumps(v)}));if(!b)return null;const r=b.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]}})()", returnByValue=True)
        p = r.get("result", {}).get("value")
        if p:
            for typ in ("mousePressed", "mouseReleased"):
                send("Input.dispatchMouseEvent", type=typ, x=p[0], y=p[1], button="left", clickCount=1)
        print("找字", v, p)
    elif k == "close":
        urllib.request.urlopen(f"http://127.0.0.1:9333/json/close/{t['id']}")
