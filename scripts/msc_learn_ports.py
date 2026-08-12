#!/usr/bin/env python3
"""学习冷门港口的 MSC 标准英文名。用国家名/关键词触发 autocomplete，收集所有匹配选项。"""
import json, sys, time, urllib.request, websocket

CDP_HTTP = "http://127.0.0.1:9222"

# (中文名, 搜索关键词) — 关键词用能触发 MSC autocomplete 的国家名或前缀
PORTS_TO_LEARN = [
    ("科佩尔", "SLOVENIA"),
    ("雷克索斯", "LEIXOES"),
    ("杰恩杰恩", "DJIBOUTI"),
    ("帝力", "TIMOR"),
    ("科林托", "CORINTO"),
    ("圣洛伦索", "SAN LORENZO"),
    ("莫因", "MOIN"),
    ("乔治敦", "GEORGETOWN"),
    ("伊基克", "IQUIQUE"),
    ("圣文森特", "SAN VICENTE"),
    ("阿卡胡特拉", "ACAJUTLA"),
    ("金贝", "KIMBE"),
    ("卡贝略", "CABELLO"),
    ("文塔纳斯", "VENTANAS"),
    ("利蒙", "LIMON"),
    ("瓦尼莫", "VANIMO"),
    ("金斯敦", "KINGSTON"),
    ("科尔特斯", "CORTES"),
    ("奥鲁湾", "ORO BAY"),
    ("圣胡安", "SAN JUAN"),
]

def wsurl():
    with urllib.request.urlopen(CDP_HTTP + "/json") as r:
        t = json.loads(r.read())
    return [x["webSocketDebuggerUrl"] for x in t if x.get("type") == "page"][0]

class CDP:
    def __init__(self):
        self.ws = websocket.create_connection(wsurl(), timeout=60)
        self.mid = 0
    def send(self, m, p=None):
        self.mid += 1
        self.ws.send(json.dumps({"id": self.mid, "method": m, "params": p or {}}))
        while True:
            r = json.loads(self.ws.recv())
            if r.get("id") == self.mid:
                if "error" in r: raise RuntimeError(f"{m}: {r['error']}")
                return r.get("result", {})
    def ev(self, js):
        r = self.send("Runtime.evaluate", {"expression": js, "returnByValue": True})
        if "exceptionDetails" in r: return None
        return r.get("result", {}).get("value")
    def close(self):
        try: self.ws.close()
        except: pass

def get_opts(cdp, placeholder):
    return cdp.ev(f"""(function(){{
      var a=document.querySelectorAll('input');var f=null;
      for(var i=0;i<a.length;i++){{if(a[i].placeholder==='{placeholder}')f=a[i]}}
      if(!f) return [];
      var p=f; while(p && !/msc-search-autocomplete/.test(p.className)){{p=p.parentElement}}
      if(!p) return [];
      var out=[];
      p.querySelectorAll('li').forEach(function(li){{
        var t=li.textContent.trim().replace(/\\s+/g,' ');
        if(t && t.length<80 && t!=='在地图上查看' && t!=='无结果') out.push(t);
      }});
      return out;
    }})()""")

def type_clear(cdp, txt):
    cdp.ev("""(function(){var a=document.querySelectorAll('input');var f=null;
      for(var i=0;i<a.length;i++){if(a[i].placeholder==='From (ports or countries)')f=a[i]} f.focus(); f.select(); return true})()""")
    cdp.send("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Delete", "code": "Delete"})
    cdp.send("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Delete", "code": "Delete"})
    time.sleep(0.3)
    cdp.send("Input.insertText", {"text": txt})
    time.sleep(3)

def main():
    cdp = CDP()
    cdp.send("Page.enable")
    cur = cdp.ev("location.href")
    if "schedule" not in cur:
        cdp.ev("location.href='https://www.msccargo.cn/zh-cn/schedule'")
        time.sleep(6)
    else:
        cdp.ev("location.reload()")
        time.sleep(6)
    dl = time.time() + 15
    while time.time() < dl:
        if cdp.ev("(function(){var a=document.querySelectorAll('input');for(var i=0;i<a.length;i++){if(a[i].placeholder==='From (ports or countries)')return true}return false})()"):
            break
        time.sleep(1)

    print("=== 冷门港口 MSC 标准英文名学习 ===")
    results = {}
    for cn, kw in PORTS_TO_LEARN:
        type_clear(cdp, kw)
        opts = get_opts(cdp, "From (ports or countries)") or []
        results[cn] = opts
        print(f"\n{cn} (搜'{kw}'):")
        for o in opts[:8]:
            print(f"   {o}")
        sys.stdout.flush()
    with open("learn_ports_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print("\n已保存 learn_ports_result.json")
    cdp.close()

if __name__ == "__main__":
    main()
