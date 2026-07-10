# 馃殺 MSC Shipping Schedule Search Agent

> **Browser-automated MSC container shipping schedule lookup 鈥?10x faster than manual browsing**

[![Version](https://img.shields.io/badge/version-2.0.0-blue)]()
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)]()
[![Automation](https://img.shields.io/badge/automation-CDP%20%7C%20Playwright-brightgreen)]()
[![Made for](https://img.shields.io/badge/made%20for-OpenClaw%20Agent-purple)]()

---

## 鉁?What It Does

This tool automates the **MSC (Mediterranean Shipping Company)** schedule search website, allowing you to query shipping schedules between any two ports in **~14 seconds** 鈥?compared to **~90 seconds** doing it manually.

> **Real-world results:** 25+ routes queried, 80+ individual sailings extracted, all with full automation.

## 馃搳 Performance

| Comparison | Manual | Old v1 Automation | **v2 Automation** |
|-----------|:-----:|:----------------:|:-----------------:|
| Single route | ~90s | ~34s | **~14s** 馃敟 |
| 3 routes | ~5min | ~102s | **~42s** 馃敟 |
| 10 routes | ~15min | ~6min | **~2.5min** 馃敟 |


## 馃 How It Works

```
鈹屸攢 Step 1 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹? 馃崻 Auto-dismiss Cookie consent popup         鈹?鈹溾攢 Step 2 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹? 鉁忥笍 Fill departure port 鈫?autocomplete 鈫?tap  鈹?鈹溾攢 Step 3 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹? 鉁忥笍 Fill arrival port 鈫?autocomplete 鈫?tap    鈹?鈹溾攢 Step 4 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹? 馃攳 Click Search 鈫?wait for Vue.js to render  鈹?鈹溾攢 Step 5 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹? 馃搳 Extract structured results (JSON/MD)      鈹?鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?```

The tool uses **xbrowser** (CDP/Playwright-based) to control a real Chromium browser. It handles:

- 鉁?**Vue.js reactive forms** 鈥?Properly triggers v-model bindings
- 鉁?**Vue autocomplete dropdowns** 鈥?PointerEvent dispatch for Angular-like components
- 鉁?**Cookie consent banners** 鈥?Auto-dismisses on page load
- 鉁?**Chinese port names** 鈥?Built-in mapping (涓婃捣 鈫?SHANGHAI, CHINA (CNSHA))
- 鉁?**Multi-tab parallelism** 鈥?Pre-load 3 MSC tabs for batch queries

## 馃殌 Quick Start

### Prerequisites

- Windows OS (Chrome for Testing managed by xbrowser)
- [OpenClaw](https://openclaw.ai) with xbrowser skill installed

### One-command Query

```powershell
node scripts/msc-auto.cjs "涓婃捣" "姹夊牎"
```

### With Screenshot

```powershell
node scripts/msc-auto.cjs "闈掑矝" "娲涙潐鐭? --screenshot
```

### Multi-tab Batch (fastest)

```powershell
# Open 3 MSC pages ahead of time
xb run tab new "https://www.msccargo.cn/zh-cn/schedule"
xb run tab new "https://www.msccargo.cn/zh-cn/schedule"
xb run tab new "https://www.msccargo.cn/zh-cn/schedule"

# Query each tab
node msc-auto.cjs "涓婃捣" "楣跨壒涓? --tab 1
node msc-auto.cjs "瀹佹尝" "姹夊牎"   --tab 2
node msc-auto.cjs "鐩愮敯" "瑗块泤鍥?  --tab 3
```

## 馃椇锔?Port Mapping

Built-in mapping for **30+ major ports**:

| Your Input | MSC Name | Code |
|-----------|----------|:----:|
| 涓婃捣 | SHANGHAI, CHINA | CNSHA |
| 瀹佹尝 | NINGBO, CHINA | CNNGB |
| 娣卞湷/铔囧彛 | SHEKOU, CHINA | CNSHK |
| 姹夊牎 | HAMBURG, GERMANY | DEHAM |
| 楣跨壒涓?| ROTTERDAM, NETHERLANDS | NLRTM |
| 娲涙潐鐭?| LOS ANGELES, US | USLAX |
| 鏂板姞鍧?| SINGAPORE | SGSIN |

Full mapping in [`scripts/msc-ports.json`](scripts/msc-ports.json).

## 馃摝 Project Structure

```
msc-schedule-search-agent/
鈹溾攢鈹€ SKILL.md                    鈫?Agent skill definition
鈹溾攢鈹€ README.md                   鈫?This file
鈹溾攢鈹€ scripts/
鈹?  鈹溾攢鈹€ msc-auto.cjs            鈫?Autonomous query script
鈹?  鈹斺攢鈹€ msc-ports.json          鈫?Port name mapping database
鈹斺攢鈹€ docs/
    鈹斺攢鈹€ architecture.md         鈫?Technical deep dive
```

## 馃摫 WeChat Integration

When integrated with OpenClaw's WeChat channel, the flow is fully automated:

1. Customer sends "鏌ヤ竴涓嬩笂娴峰埌姹夊牎鐨勮埞鏈? on WeChat
2. Agent auto-resolves ports 鈫?queries MSC 鈫?extracts results
3. Agent sends back formatted table + screenshot to customer
4. All within the WeChat conversation 鈥?no app switching needed

## 馃搳 Verified Routes

### 馃敟 High-frequency direct routes

| From 鈫?To | Direct Sailings | Notes |
|----------|:--------------:|-------|
| Shanghai 鈫?Rotterdam | **10** | Best European route |
| Shanghai 鈫?Hamburg | **10** | Confirmed July 2026 |
| Yantian 鈫?Seattle | **9** | Best US West Coast |
| Shanghai 鈫?Santos | **8** | Brazil service |
| Shanghai 鈫?Buenos Aires | **7** | Fastest 42 days |
| Ningbo 鈫?Buenos Aires | 4 | With transshipment |
| Shekou 鈫?Montevideo | 3 | Uruguay service |

### 鉂?No MSC service

| Route | Issue |
|-------|-------|
| Any CN port 鈫?Busan | MSC has no direct service |
| Shanghai 鈫?Los Angeles | No MSC service |
| Nansha 鈫?Los Angeles | No direct |
| Dubai / Dammam / Aqaba | Not in MSC system |

## 鈿?Technical Highlights

### Why this is fast

| Optimization | Before | After |
|-------------|:-----:|:-----:|
| Warmup eval | Required (2s) | **Skipped** |
| Autocomplete wait | 3.5s | **2.0s** |
| Search result wait | 10-12s | **5.0s** |
| Page reload per route | Required | **Reused** (if multi-tab) |
| xb CDP connections | Per command | **Batch mode** (reuse) |

### The Cookie Problem

The MSC site shows a **Cookie consent banner** on every page load that overlays the form elements. The tool auto-detects and dismisses it using text-based button targeting 鈥?no hardcoded refs needed.

### Vue.js Form Challenge

MSC uses Vue.js with reactive forms. Simple DOM value assignment doesn't trigger the framework. Two techniques are used:
- **xbrowser's `fill` command** 鈫?triggers proper input events (works for text entry)
- **PointerEvent dispatch sequence** 鈫?`pointerdown鈫抦ousedown鈫抪ointerup鈫抦ouseup鈫抍lick` (works for Vue dropdown selection)

## 鈿狅笍 Caveats

1. **MSC website may change** 鈥?selectors and page structure can break; run a test query first
2. **Rate limiting** 鈥?MSC doesn't block, but be reasonable (query in batches of 5-10)
3. **Window focus** 鈥?The browser tab must remain visible; minimize at your own risk
4. **Port names** 鈥?Must match MSC's autocomplete exactly; the mapping database helps

## 馃洜锔?Development

```bash
# Test a single route
node scripts/msc-auto.cjs "涓婃捣" "姹夊牎" --open

# Test port resolution
node -e "const p=require('./scripts/msc-ports.json');console.log(p.ports.length+' ports loaded')"
```

## 馃 Contributing

PRs welcome! Particularly:
- Additional port mappings
- Support for other shipping lines (Maersk, CMA CGM, COSCO)
- Improved error recovery

## 馃搫 License

MIT 鈥?use freely, modify freely, share freely.

---

<p align="center">
  <b>Made with 鈿?by QClaw Agent</b><br>
  <i>Part of the OpenClaw ecosystem</i>
</p>
