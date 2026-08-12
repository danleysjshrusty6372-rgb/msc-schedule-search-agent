#!/usr/bin/env python3
"""MSC 强化学习训练：批量跑 20 条训练航线，验证准确度与速度。"""
import sys, os, time, subprocess, json

# 训练航线 (from, to) — 冷门偏港测试集
ROUTES = [
    ("上海", "科佩尔"),
    ("盐田", "雷克索斯"),
    ("宁波", "杰恩杰恩"),
    ("蛇口", "帝力"),
    ("青岛", "科林托"),
    ("南沙", "圣洛伦索"),
    ("厦门", "莫因"),
    ("上海", "乔治敦"),
    ("天津", "伊基克"),
    ("盐田", "圣文森特"),
    ("宁波", "阿卡胡特拉"),
    ("上海", "金贝"),
    ("香港", "卡贝略"),
    ("上海", "文塔纳斯"),
    ("盐田", "利蒙"),
    ("宁波", "瓦尼莫"),
    ("南沙", "金斯敦"),
    ("青岛", "科尔特斯"),
    ("厦门", "奥鲁湾"),
    ("天津", "圣胡安"),
]

SCRIPT = os.path.join(os.path.dirname(__file__), "msc_query_cdp.py")

def normalize(port):
    """把"深圳盐田"、"广州南沙"等组合名拆成脚本认识的别名。"""
    aliases = {
        "深圳盐田": "盐田", "广州南沙": "南沙",
    }
    return aliases.get(port, port)

def run_route(frm, to, reuse=False):
    f1, f2 = normalize(frm), normalize(to)
    cmd = [sys.executable, SCRIPT, f1, f2]
    if reuse:
        cmd.append("--reuse")
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          timeout=90)
    elapsed = time.time() - t0
    out = proc.stdout.strip()
    # 判断是否成功：结果表格里有"直达航线"或"中转航线"，或无服务提示
    if "直达航线" in out or "中转航线" in out:
        # 分别统计直达/中转条数
        import re
        m = re.search(r"直达航线.*?（(\d+) 条）", out)
        m2 = re.search(r"中转航线.*?（(\d+) 条）", out)
        parts = []
        if m: parts.append(f"{m.group(1)}直")
        if m2: parts.append(f"{m2.group(1)}中")
        if parts:
            status = "✅ " + "/".join(parts)
        else:
            status = "✅ 有航线"
    elif "暂无 MSC" in out:
        status = "ℹ️ 无航线"
    else:
        status = "❌ 异常: " + out[:100]
    return elapsed, status

def main():
    # 批量用 --reuse：第一条加载页面，后续全部复用 → 显著提速
    reuse = "--reuse" in sys.argv
    results = []
    print(f"{'#':<3}{'航线':<28}{'结果':<12}{'耗时'}")
    print("-" * 55)
    for i, (f, t) in enumerate(ROUTES, 1):
        try:
            elapsed, status = run_route(f, t, reuse=reuse)
        except subprocess.TimeoutExpired:
            elapsed, status = 90, "❌ 超时"
        except Exception as e:
            elapsed, status = 0, f"❌ {str(e)[:60]}"
        results.append((f, t, status, elapsed))
        print(f"{i:<3}{f} → {t:<18}{status:<12}{elapsed:.1f}s")
        sys.stdout.flush()
        # 页面状态稳定间隔：避免连续快速连接同一 CDP Chrome 导致状态竞争/漂移
        if i < len(ROUTES):
            time.sleep(1.5)
    # 汇总
    ok = sum(1 for r in results if r[2].startswith("✅"))
    no = sum(1 for r in results if r[2].startswith("ℹ️"))
    bad = sum(1 for r in results if r[2].startswith("❌"))
    total_time = sum(r[3] for r in results)
    print("-" * 55)
    print(f"总计: {len(results)} 条 | ✅{ok} 有航线 | ℹ️{no} 无航线 | ❌{bad} 异常")
    print(f"总耗时 {total_time:.1f}s, 平均 {total_time/len(results):.1f}s/条")
    # 保存明细
    with open(os.path.join(os.path.dirname(__file__), "train_results.json"), "w", encoding="utf-8") as f:
        json.dump([{"from": r[0], "to": r[1], "result": r[2], "time": round(r[3], 1)} for r in results],
                  f, ensure_ascii=False, indent=1)
    print("明细已保存到 train_results.json")

if __name__ == "__main__":
    main()
