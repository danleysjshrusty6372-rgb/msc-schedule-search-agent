#!/usr/bin/env python3
"""
MSC skill 一键部署/自检脚本（换机器用）。

用法（Windows, git-bash 或 cmd）:
    python setup.py check      # 检查依赖
    python setup.py install    # 安装 websocket-client + 启动常驻 Chrome
    python setup.py test       # 跑一条测试航线验证

功能:
  - 检查 python、websocket-client、Chrome 是否就绪
  - 启动常驻 CDP Chrome（9222 端口）
  - 跑一条测试航线验证整体可用
"""
import os, sys, subprocess, time, urllib.request, shutil

PORT = 9222
CDP_HTTP = f"http://127.0.0.1:{PORT}"

def chrome_paths():
    cands = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    return [c for c in cands if os.path.exists(c)]

def check():
    print("=== MSC skill 依赖检查 ===")
    print(f"  Python: {sys.version.split()[0]}")
    try:
        import websocket
        print("  websocket-client: ✅")
    except ImportError:
        print("  websocket-client: ❌ 未安装 (运行: pip install websocket-client)")
    ch = chrome_paths()
    print(f"  Chrome: {'✅ ' + ch[0] if ch else '❌ 未找到'}")
    try:
        urllib.request.urlopen(CDP_HTTP + "/json/version", timeout=3)
        print(f"  CDP Chrome (port {PORT}): ✅ 已在运行")
    except Exception:
        print(f"  CDP Chrome (port {PORT}): ⏳ 未运行")
    return True

def launch_chrome():
    if not chrome_paths():
        print("❌ Chrome 未安装，无法启动。请先安装 Chrome。")
        return False
    # 已运行则跳过
    try:
        urllib.request.urlopen(CDP_HTTP + "/json/version", timeout=3)
        print(f"  CDP Chrome 已在运行 (port {PORT})，无需重复启动。")
        return True
    except Exception:
        pass
    profile = os.path.join(os.environ.get("TEMP", "/tmp"), "msc-cdp-profile")
    lock = os.path.join(profile, "SingletonLock")
    if os.path.exists(lock):
        try: os.remove(lock)
        except Exception: pass
    chrome = chrome_paths()[0]
    subprocess.Popen([chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
                      "--window-size=1280,900",
                      "--remote-debugging-port", str(PORT), "--remote-allow-origins=*",
                      "--user-data-dir", profile, "about:blank"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(15):
        time.sleep(1)
        try:
            urllib.request.urlopen(CDP_HTTP + "/json/version", timeout=2)
            print(f"  ✅ CDP Chrome 已启动 (port {PORT})")
            return True
        except Exception:
            continue
    print("❌ Chrome 启动失败。")
    return False

def install():
    print("=== 安装依赖 ===")
    try:
        import websocket
        print("  websocket-client: 已安装")
    except ImportError:
        print("  安装 websocket-client...")
        subprocess.run([sys.executable, "-m", "pip", "install", "websocket-client"],
                       check=True)
        print("  ✅ websocket-client 已安装")
    launch_chrome()
    return True

def test():
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "msc_query_cdp.py")
    print("=== 测试航线: 上海 → 汉堡 ===")
    if not launch_chrome():
        return False
    time.sleep(1)
    p = subprocess.run([sys.executable, script, "上海", "汉堡"],
                       capture_output=True, text=True, encoding="utf-8", timeout=90)
    print(p.stdout)
    if p.returncode != 0:
        print("stderr:", p.stderr[:500])
    return p.returncode == 0

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check":
        check()
    elif cmd == "install":
        install()
    elif cmd == "test":
        test()
    else:
        print("用法: python setup.py {check|install|test}")
