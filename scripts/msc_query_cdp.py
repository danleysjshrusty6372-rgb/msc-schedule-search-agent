#!/usr/bin/env python3
"""
MSC Shipping Schedule Query via CDP (Chrome DevTools Protocol).

Fully self-contained: auto-starts a headless debug Chrome if none is running.
Usage:
    python msc_query_cdp.py "上海" "汉堡"
    python msc_query_cdp.py "宁波" "布宜诺斯艾利斯"

Verified 2026-08: MSC schedule form uses Alpine.js (x-model). Dropdown selection
REQUIRES real CDP mouse events (Input.dispatchMouseEvent); JS-synthesized
PointerEvent/.click() do NOT work.
"""
import json, os, sys, time, subprocess, urllib.request, websocket

CDP_HTTP = "http://127.0.0.1:9222"
CDP_PORT = 9222
PROFILE_DIR = os.path.join(os.environ.get("TEMP", "/tmp"), "msc-cdp-profile")

# ─── 运行模式 ───────────────────────────────────────────
# 开发模式(默认): 输出完整过程日志，便于调试
# 生产模式(仅部署到其他设备后用): MSC_PROD=1 时只输出最终结果
import os as _os
DEV_MODE = _os.environ.get("MSC_PROD", "0") != "1"
def log(*args):
    """开发模式输出过程日志；生产模式静默。"""
    if DEV_MODE:
        print(*args)

PORTS = {
    # 中国
    "上海": "SHANGHAI, CHINA", "宁波": "NINGBO, CHINA", "深圳": "SHEKOU, CHINA",
    "蛇口": "SHEKOU, CHINA", "盐田": "YANTIAN, CHINA", "南沙": "NANSHA, CHINA",
    "青岛": "QINGDAO, CHINA", "天津": "TIANJINXINGANG, CHINA", "大连": "DALIAN, CHINA",
    "厦门": "XIAMEN, CHINA", "南京": "NANJING, CHINA", "福州": "FUZHOU, CHINA",
    "高雄": "KAOHSIUNG, TAIWAN",
    # 欧洲
    "鹿特丹": "ROTTERDAM, NETHERLANDS", "汉堡": "HAMBURG, GERMANY",
    "安特卫普": "ANTWERP, BELGIUM", "勒阿弗尔": "LE HAVRE, FRANCE",
    "热那亚": "GENOA, ITALY", "费利克斯托": "FELIXSTOWE, UNITED KINGDOM",
    "瓦伦西亚": "VALENCIA, SPAIN", "皮雷埃夫斯": "PIRAEUS, GREECE",
    "科佩尔": "KOPER, SLOVENIA", "雷克索斯": "LEIXOES, PORTUGAL",
    # 亚洲/中东
    "新加坡": "SINGAPORE", "釜山": "BUSAN, KOREA, REPUBLIC OF",
    "胡志明市": "HO CHI MINH CITY, VIETNAM",
    "横滨": "YOKOHAMA, JAPAN", "蒙德拉": "MUNDRA, INDIA",
    "杰贝阿里": "JEBEL ALI, UAE", "香港": "HONG KONG, CHINA",
    "帝力": "DILI, TIMOR-LESTE", "杰恩杰恩": "DJIBOUTI, DJIBOUTI",
    # 北美/加勒比/中美洲
    "洛杉矶": "LOS ANGELES, UNITED STATES", "长滩": "LONG BEACH, US",
    "西雅图": "SEATTLE, US", "纽约": "NEW YORK, US",
    "温哥华": "VANCOUVER, CANADA", "迈阿密": "MIAMI, US",
    "圣胡安": "SAN JUAN, PUERTO RICO", "金斯敦": "KINGSTON, JAMAICA",
    "卡贝略": "PUERTO CABELLO, VENEZUELA",
    "科林托": "CORINTO, NICARAGUA", "莫因": "MOIN, COSTA RICA",
    "利蒙": "PUERTO LIMON, COSTA RICA",
    "圣洛伦索": "SAN LORENZO, HONDURAS", "科尔特斯": "PUERTO CORTES, HONDURAS",
    "乔治敦": "GEORGETOWN, GUYANA", "阿卡胡特拉": "ACAJUTLA, EL SALVADOR",
    # 南美
    "桑托斯": "SANTOS, BRAZIL", "布宜诺斯艾利斯": "BUENOS AIRES, ARGENTINA",
    "蒙得维的亚": "MONTEVIDEO, URUGUAY", "巴拉那瓜": "PARANAGUA, BRAZIL",
    "里约热内卢": "RIO DE JANEIRO, BRAZIL",
    "伊基克": "IQUIQUE, CHILE", "圣文森特": "SAN VICENTE, CHILE",
    # 大洋洲/非洲
    "悉尼": "SYDNEY, AUSTRALIA", "墨尔本": "MELBOURNE, AUSTRALIA",
    "奥克兰": "AUCKLAND, NEW ZEALAND", "德班": "DURBAN, SOUTH AFRICA",
    "亚历山大": "ALEXANDRIA, EGYPT",
}

def resolve_port(name):
    name = name.strip()
    for k, v in PORTS.items():
        if k == name or name.upper() in v: return v
    return name.upper()

# ─── CDP Chrome auto-launch ─────────────────────────────
def ensure_chrome():
    """Return True if a CDP debug Chrome is reachable, else start one."""
    try:
        with urllib.request.urlopen(CDP_HTTP + "/json/version", timeout=3) as r:
            return True
    except Exception:
        pass
    # find chrome.exe (LOCALAPPDATA first, then standard paths)
    candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    chrome = next((c for c in candidates if os.path.exists(c)), None)
    if not chrome:
        raise RuntimeError("Chrome not found. Install Chrome or set cdp_url manually.")
    # clean any stale profile SingletonLock so Chrome starts fresh, then use a UNIQUE profile
    # (fixed profile + fixed port causes "Multiple targets not supported in headless mode")
    unique_profile = PROFILE_DIR + "-" + str(os.getpid())
    lock = os.path.join(unique_profile, "SingletonLock")
    if os.path.exists(lock):
        try: os.remove(lock)
        except Exception: pass
    subprocess.Popen([chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
                      "--window-size=1280,900",
                      "--remote-debugging-port", str(CDP_PORT), "--remote-allow-origins=*",
                      "--user-data-dir", unique_profile, "about:blank"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # wait for CDP endpoint
    for _ in range(15):
        time.sleep(1)
        try:
            with urllib.request.urlopen(CDP_HTTP + "/json/version", timeout=2) as r:
                return True
        except Exception:
            continue
    raise RuntimeError("Failed to start CDP Chrome on port %d" % CDP_PORT)

def wsurl():
    with urllib.request.urlopen(CDP_HTTP + "/json") as r:
        t = json.loads(r.read())
    for x in t:
        if x.get("type") == "page":
            return x["webSocketDebuggerUrl"]
    raise RuntimeError("no page target")

class CDP:
    def __init__(self):
        self.ws = websocket.create_connection(wsurl(), timeout=120)
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
        if "exceptionDetails" in r: raise RuntimeError(f"JS: {json.dumps(r['exceptionDetails'])[:300]}")
        return r.get("result", {}).get("value")
    def mouse_click(self, x, y):
        self.send("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": x, "y": y})
        self.send("Input.dispatchMouseEvent", {"type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1})
        self.send("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": 1})
    def close(self):
        try: self.ws.close()
        except: pass

def field_ready(cdp, placeholder):
    js = f"""(function(){{var a=document.querySelectorAll('input');
      for(var i=0;i<a.length;i++){{if(a[i].placeholder==='{placeholder}')return true}} return false}})()"""
    return cdp.ev(js)

def fill_and_select(cdp, placeholder, msc_name, wait_mult=1.0):
    """Type search term into field, then REAL-mouse-click the exact dropdown option.
    Uses dynamic polling (no fixed 3.5s sleep) for speed."""
    first = msc_name.split(",")[0].strip()
    cdp.ev(f"""(function(){{var a=document.querySelectorAll('input');var f=null;
      for(var i=0;i<a.length;i++){{if(a[i].placeholder==='{placeholder}')f=a[i]}} f.focus(); f.select(); return true}})()""")
    cdp.send("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Delete", "code": "Delete"})
    cdp.send("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Delete", "code": "Delete"})
    time.sleep(0.2)
    cdp.send("Input.insertText", {"text": first})
    # dynamic wait: poll for the dropdown option to appear (usually 1-2s)
    coord = None
    dl = time.time() + 6 * wait_mult
    while time.time() < dl:
        coord = cdp.ev(f"""(function(){{
          var target=null;
          document.querySelectorAll('li').forEach(function(li){{
            var t=li.textContent.trim().toUpperCase();
            if(t.indexOf('{first.upper()}')>=0 && t.indexOf('CODE')<0 && li.offsetParent!==null && !target) target=li;
          }});
          if(!target){{
            var p=document.querySelector('.msc-search-schedule__autocomplete')||document.querySelector('.msc-search-autocomplete--focused');
            if(p){{var lis=p.querySelectorAll('li'); for(var i=0;i<lis.length;i++){{if(lis[i].textContent.trim()&&lis[i].offsetParent!==null){{target=lis[i];break}}}}}}
          }}
          if(!target) return null;
          var r=target.getBoundingClientRect();
          return {{x:Math.round(r.left+r.width/2), y:Math.round(r.top+r.height/2), txt:target.textContent.trim().slice(0,40)}};
        }})()""")
        if coord:
            break
        time.sleep(0.5)
    if not coord:
        return "NO_OPTION_FOUND"
    cdp.mouse_click(coord["x"], coord["y"])
    time.sleep(0.6)
    val = cdp.ev(f"""(function(){{var a=document.querySelectorAll('input');
      for(var i=0;i<a.length;i++){{if(a[i].placeholder==='{placeholder}')return a[i].value}} return ''}})()""")
    return f"clicked {coord['txt']} @({coord['x']},{coord['y']}) → field='{val}'"

def format_results(from_raw, to_raw, res):
    """Human-readable markdown table from raw results."""
    lines = []
    lines.append(f"🚢 **MSC 船期查询结果**")
    lines.append(f"📍 **出发港：** {from_raw}")
    lines.append(f"📍 **目的港：** {to_raw}")
    lines.append("")
    if not res:
        lines.append("❌ 该路线暂无 MSC 直达或中转服务。")
        return "\n".join(lines)
    direct = [r for r in res if r.get("type") == "Direct"]
    trans = [r for r in res if r.get("type") == "Transship"]
    if direct:
        lines.append(f"━━━ **直达航线**（{len(direct)} 条）━━━")
        lines.append("| # | 离港 | 到港 | 类型 |")
        lines.append("|---|------|------|:----:|")
        for i, d in enumerate(direct, 1):
            lines.append(f"| {i} | {d['dep']} | {d['arr']} | ✅直达 |")
    else:
        lines.append("❌ 无直达服务")
    if trans:
        lines.append("")
        lines.append(f"━━━ **中转航线**（{len(trans)} 条）━━━")
        lines.append("| # | 离港 | 到港 | 类型 |")
        lines.append("|---|------|------|:----:|")
        for i, d in enumerate(trans, 1):
            lines.append(f"| {i} | {d['dep']} | {d['arr']} | 🔄中转 |")
    lines.append("")
    if direct:
        from datetime import datetime
        MONTHS = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,
                  "Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
        def parse_dep(s):
            # format: "Sun 16th Aug 2026"
            parts = s.split()
            if len(parts) >= 4:
                try:
                    day = int(''.join(ch for ch in parts[1] if ch.isdigit()))
                    return datetime(int(parts[3]), MONTHS.get(parts[2], 1), day)
                except Exception:
                    return None
            return None
        spans = []
        for d in direct:
            dep, arr = parse_dep(d.get("dep","")), parse_dep(d.get("arr",""))
            if dep and arr:
                spans.append((arr - dep).days)
        if spans:
            lines.append(f"⚡ **最快直达：** {min(spans)} 天")
    return "\n".join(lines)

def main():
    # 支持 --reuse: 复用当前已打开的 MSC 页面(不 reload)，批量时显著提速
    reuse = "--reuse" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        print("Usage: python msc_query_cdp.py <from_port> <to_port> [--reuse]")
        sys.exit(1)
    from_raw, to_raw = args[0], args[1]
    from_name = resolve_port(from_raw)
    to_name = resolve_port(to_raw)
    log(f"🔍 {from_raw} → {to_raw}  ({from_name} → {to_name})")
    log("▶ Ensuring CDP Chrome...")
    ensure_chrome()
    time.sleep(1)

    cdp = CDP()
    cdp.send("Page.enable")
    cur = cdp.ev("location.href")
    if "schedule" not in cur:
        cdp.ev("location.href='https://www.msccargo.cn/zh-cn/schedule'")
        time.sleep(6)
    elif not reuse:
        cdp.ev("location.reload()")
        time.sleep(6)
    # wait for form (shorter if reusing already-loaded page)
    dl = time.time() + 15
    while time.time() < dl:
        if field_ready(cdp, "From (ports or countries)"): break
        time.sleep(1)

    # cookie
    cdp.ev("""(function(){var b=document.querySelectorAll('button');
      for(var i=0;i<b.length;i++){var t=b[i].textContent.trim();
        if(t.indexOf('接受所有')>=0||t.indexOf('Accept all')>=0){b[i].click();return true}} return false})()""")
    time.sleep(1)

    log("  From:", fill_and_select(cdp, "From (ports or countries)", from_name))
    log("  To:  ", fill_and_select(cdp, "To (ports or countries)", to_name))

    sbtn_coord = cdp.ev("""(function(){
      var b=document.querySelectorAll('button');
      for(var i=0;i<b.length;i++){var t=b[i].textContent.trim();
        if(t.indexOf('搜索船期表')>=0){var r=b[i].getBoundingClientRect();return {x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2),disabled:b[i].disabled}}}
      return null;
    })()""")
    if sbtn_coord and not sbtn_coord.get("disabled"):
        cdp.mouse_click(sbtn_coord["x"], sbtn_coord["y"])
        log("  clicked search")
        # dynamic wait for results (up to 12s)
        dl = time.time() + 12
        while time.time() < dl:
            if cdp.ev("document.querySelectorAll('[class*=point-to-point-details__result]').length > 0"):
                break
            time.sleep(0.5)
    elif sbtn_coord and sbtn_coord.get("disabled"):
        log("  !! search button disabled - form incomplete")

    res = cdp.ev("""(function(){
      var items=document.querySelectorAll('[class*=point-to-point-details__result]');
      var out=[];
      for(var i=0;i<items.length;i++){
        var r=items[i], h=r.querySelectorAll('.data-heading');
        var dep=h[0]?h[0].textContent.trim():'', arr=h[1]?h[1].textContent.trim():'';
        var txt=r.textContent;
        out.push({n:i+1, dep:dep, arr:arr, type:txt.indexOf('直')>=0?'Direct':(txt.indexOf('中')>=0?'Transship':'N/A')});
      }
      return out;
    })()""")
    # 生产模式只输出最终结果
    print(format_results(from_raw, to_raw, res))
    cdp.close()

if __name__ == "__main__":
    main()
