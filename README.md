# 🚢 MSC Shipping Schedule Search Agent

> **Browser-automated MSC container shipping schedule lookup — 10x faster than manual browsing**

[![Version](https://img.shields.io/badge/version-3.0.0-blue)]()
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)]()
[![Automation](https://img.shields.io/badge/automation-CDP%20%7C%20Playwright-brightgreen)]()

---

## 🆕 Hermes Agent 版本（推荐）

本仓库已适配 **Hermes Agent**，原 xbrowser 依赖重写为纯 CDP（Chrome DevTools Protocol）脚本，详见 `SKILL.md`。

**核心文件：**
- `SKILL.md` — 完整指南（港口表 60+、排错速查、冷门偏港训练结果、换机器部署说明）
- `scripts/msc_query_cdp.py` — 核心查询脚本（真实鼠标点击 Alpine.js 下拉，支持 `--reuse` 提速）
- `scripts/setup.py` — 换机器一键部署/自检（`check`/`install`/`test`）
- `scripts/msc_train.py` — 批量训练脚本
- `references/msc-ports.json` — 60+ 港口映射

**快速开始（Hermes）：**
```bash
python scripts/setup.py install   # 装 websocket-client + 启动常驻 Chrome
python scripts/setup.py check     # 检查就绪
python scripts/msc_query_cdp.py "上海" "科佩尔"   # 查询
```

> 新机器仅需 2 个外部依赖：`websocket-client` (pip) + Google Chrome。

---

## ✨ What It Does

This tool automates the **MSC (Mediterranean Shipping Company)** schedule search website, allowing you to query shipping schedules between any two ports in **~6-14 seconds** — compared to **~90 seconds** doing it manually.

> **Real-world results:** 40+ routes queried, 150+ individual sailings extracted, all with full automation.

## 📊 Performance

| Comparison | Manual | Old v1 Automation | **v2 Automation** |
|-----------|:-----:|:----------------:|:-----------------:|
| Single route | ~90s | ~34s | **~14s** 🔥 |
| 3 routes | ~5min | ~102s | **~42s** 🔥 |
| 10 routes | ~15min | ~6min | **~2.5min** 🔥 |


## 🧠 How It Works

```
┌─ Step 1 ─────────────────────────────────────┐
│  🍪 Auto-dismiss Cookie consent popup         │
├─ Step 2 ─────────────────────────────────────┤
│  ✏️ Fill departure port → autocomplete → tap  │
├─ Step 3 ─────────────────────────────────────┤
│  ✏️ Fill arrival port → autocomplete → tap    │
├─ Step 4 ─────────────────────────────────────┤
│  🔍 Click Search → wait for Vue.js to render  │
├─ Step 5 ─────────────────────────────────────┤
│  📊 Extract structured results (JSON/MD)      │
└───────────────────────────────────────────────┘
```

The tool uses **xbrowser** (CDP/Playwright-based) to control a real Chromium browser. It handles:

- ✅ **Vue.js reactive forms** — Properly triggers v-model bindings
- ✅ **Vue autocomplete dropdowns** — PointerEvent dispatch for Angular-like components
- ✅ **Cookie consent banners** — Auto-dismisses on page load
- ✅ **Chinese port names** — Built-in mapping (上海 → SHANGHAI, CHINA (CNSHA))
- ✅ **Multi-tab parallelism** — Pre-load 3 MSC tabs for batch queries

## 🚀 Quick Start

### Prerequisites

- Windows OS (Chrome for Testing managed by xbrowser)
- [OpenClaw](https://openclaw.ai) with xbrowser skill installed

### One-command Query

```powershell
node scripts/msc-auto.cjs "上海" "汉堡"
```

### With Screenshot

```powershell
node scripts/msc-auto.cjs "青岛" "洛杉矶" --screenshot
```

### Multi-tab Batch (fastest)

```powershell
# Open 3 MSC pages ahead of time
xb run tab new "https://www.msccargo.cn/zh-cn/schedule"
xb run tab new "https://www.msccargo.cn/zh-cn/schedule"
xb run tab new "https://www.msccargo.cn/zh-cn/schedule"

# Query each tab
node msc-auto.cjs "上海" "鹿特丹" --tab 1
node msc-auto.cjs "宁波" "汉堡"   --tab 2
node msc-auto.cjs "盐田" "西雅图"  --tab 3
```

## 🗺️ Port Mapping

Built-in mapping for **30+ major ports**:

| Your Input | MSC Name | Code |
|-----------|----------|:----:|
| 上海 | SHANGHAI, CHINA | CNSHA |
| 宁波 | NINGBO, CHINA | CNNGB |
| 深圳/蛇口 | SHEKOU, CHINA | CNSHK |
| 汉堡 | HAMBURG, GERMANY | DEHAM |
| 鹿特丹 | ROTTERDAM, NETHERLANDS | NLRTM |
| 洛杉矶 | LOS ANGELES, US | USLAX |
| 新加坡 | SINGAPORE | SGSIN |

Full mapping in [`scripts/msc-ports.json`](scripts/msc-ports.json).

## 📦 Project Structure

```
msc-schedule-search-agent/
├── SKILL.md                    ← Agent skill definition
├── README.md                   ← This file
├── scripts/
│   ├── msc-auto.cjs            ← Autonomous query script
│   └── msc-ports.json          ← Port name mapping database
└── docs/
    └── architecture.md         ← Technical deep dive
```

## 📱 WeChat Integration

When integrated with OpenClaw's WeChat channel, the flow is fully automated:

1. Customer sends "查一下上海到汉堡的船期" on WeChat
2. Agent auto-resolves ports → queries MSC → extracts results
3. Agent sends back formatted table + screenshot to customer
4. All within the WeChat conversation — no app switching needed

## 📊 Verified Routes

### 🔥 High-frequency direct routes

| From → To | Direct Sailings | Notes |
|----------|:--------------:|-------|
| Shanghai → Rotterdam | **10** | Best European route |
| Shanghai → Hamburg | **10** | Confirmed July 2026 |
| Yantian → Seattle | **9** | Best US West Coast |
| Shanghai → Santos | **8** | Brazil service |
| Shanghai → Buenos Aires | **7** | Fastest 42 days |
| Ningbo → Buenos Aires | 4 | With transshipment |
| Shekou → Montevideo | 3 | Uruguay service |

### ❌ No MSC service

| Route | Issue |
|-------|-------|
| Any CN port → Busan | MSC has no direct service |
| Shanghai → Los Angeles | No MSC service |
| Nansha → Los Angeles | No direct |
| Dubai / Dammam / Aqaba | Not in MSC system |

## ⚡ Technical Highlights

### Why this is fast

| Optimization | Before | After |
|-------------|:-----:|:-----:|
| Warmup eval | Required (2s) | **Skipped** |
| Autocomplete wait | 3.5s | **2.0s** |
| Search result wait | 10-12s | **5.0s** |
| Page reload per route | Required | **Reused** (if multi-tab) |
| xb CDP connections | Per command | **Batch mode** (reuse) |

### The Cookie Problem

The MSC site shows a **Cookie consent banner** on every page load that overlays the form elements. The tool auto-detects and dismisses it using text-based button targeting — no hardcoded refs needed.

### Vue.js Form Challenge

MSC uses Vue.js with reactive forms. Simple DOM value assignment doesn't trigger the framework. Two techniques are used:
- **xbrowser's `fill` command** → triggers proper input events (works for text entry)
- **PointerEvent dispatch sequence** → `pointerdown→mousedown→pointerup→mouseup→click` (works for Vue dropdown selection)

## ⚠️ Caveats

1. **MSC website may change** — selectors and page structure can break; run a test query first
2. **Rate limiting** — MSC doesn't block, but be reasonable (query in batches of 5-10)
3. **Window focus** — The browser tab must remain visible; minimize at your own risk
4. **Port names** — Must match MSC's autocomplete exactly; the mapping database helps

## 🛠️ Development

```bash
# Test a single route
node scripts/msc-auto.cjs "上海" "汉堡" --open

# Test port resolution
node -e "const p=require('./scripts/msc-ports.json');console.log(p.ports.length+' ports loaded')"
```

## 🤝 Contributing

PRs welcome! Particularly:
- Additional port mappings
- Support for other shipping lines (Maersk, CMA CGM, COSCO)
- Improved error recovery

## 📄 License

MIT — use freely, modify freely, share freely.

---

<p align="center">
  <b>Made with ⚡ by QClaw Agent</b><br>
  <i>Part of the OpenClaw ecosystem</i>
</p>
