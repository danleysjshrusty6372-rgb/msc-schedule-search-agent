# 🚢 MSC Shipping Schedule Search Agent

> **Browser-automated MSC container shipping schedule lookup — 10x faster than manual browsing**
>
> **浏览器自动化的 MSC 船期查询工具 — 比手动浏览快 10 倍**

[![Version](https://img.shields.io/badge/version-2.0.0-blue)]()
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)]()
[![Automation](https://img.shields.io/badge/automation-CDP%20%7C%20Playwright-brightgreen)]()
[![Made for](https://img.shields.io/badge/made%20for-OpenClaw%20Agent-purple)]()

---

## 🇬🇧 English / 🇨🇳 中文

> **English below | 中文在下文**

---

## What It Does / 功能简介

Automates the **MSC (Mediterranean Shipping Company)** schedule search website. Query shipping schedules between any two ports in **~14 seconds** instead of ~90 seconds manually.

**自动查询 MSC 官网船期**，输入两个港口名，~14 秒出结果。已实测 **25+ 条航线、80+ 航次**。

| Comparison / 对比 | Manual / 手动 | Old v1 / 旧版 | **v2 This Tool / 新版** |
|-------------------|:------------:|:------------:|:---------------------:|
| Single route / 单条 | ~90s | ~34s | **~14s** |
| 3 routes / 三条 | ~5min | ~102s | **~42s** |
| 10 routes / 十条 | ~15min | ~6min | **~2.5min** |

## How It Works / 工作原理

~~~
Step 1  Accept Cookie consent popup / 自动关闭 Cookie 弹窗
Step 2  Fill departure port -> autocomplete -> click / 填写出发港 -> 下拉 -> 点击
Step 3  Fill arrival port -> autocomplete -> click / 填写目的港 -> 下拉 -> 点击
Step 4  Click Search -> wait for results / 点击搜索 -> 等待结果
Step 5  Extract structured data / 提取结构化数据
~~~

The tool handles these challenges / 本工具能处理这些难点:
- Vue.js reactive forms that ignore plain value assignment
- Vue autocomplete with PointerEvent dispatch
- Cookie consent banners on every page load
- Chinese port name resolution (上海 -> SHANGHAI, CHINA (CNSHA))
- Multi-tab parallelism for batch queries

## Quick Start / 快速开始

### Prerequisites / 前提

- Windows OS
- OpenClaw with xbrowser skill installed

### One-command query / 一键查询

```powershell
node scripts/msc-auto.cjs "上海" "汉堡"
```

### With screenshot / 带截图

```powershell
node scripts/msc-auto.cjs "青岛" "洛杉矶" --screenshot
```

### Multi-tab batch / 多标签页批量（最快）

```powershell
# Open 3 MSC pages ahead of time / 预开 3 个 MSC 页面
xb run tab new "https://www.msccargo.cn/zh-cn/schedule"
xb run tab new "https://www.msccargo.cn/zh-cn/schedule"
xb run tab new "https://www.msccargo.cn/zh-cn/schedule"

# Query each tab / 查询各标签页
node msc-auto.cjs "上海" "鹿特丹" --tab 1
node msc-auto.cjs "宁波" "汉堡"   --tab 2
node msc-auto.cjs "盐田" "西雅图"  --tab 3
```

## Port Mapping / 港口映射

Built-in mapping for 30+ major ports / 内置 30+ 主要港口映射:

| 中文名 | MSC Name | Code |
|-------|----------|:----:|
| 上海 | SHANGHAI, CHINA | CNSHA |
| 宁波 | NINGBO, CHINA | CNNGB |
| 深圳/蛇口 | SHEKOU, CHINA | CNSHK |
| 青岛 | QINGDAO, CHINA | CNTAO |
| 天津 | TIANJINXINGANG, CHINA | CNTXG |
| 汉堡 | HAMBURG, GERMANY | DEHAM |
| 鹿特丹 | ROTTERDAM, NETHERLANDS | NLRTM |
| 新加坡 | SINGAPORE | SGSIN |
| 洛杉矶 | LOS ANGELES, US | USLAX |
| 釜山 | BUSAN, KOREA, REPUBLIC OF | KRPUS |

Full list: [scripts/msc-ports.json](scripts/msc-ports.json)

## Project Structure / 项目结构

~~~
msc-schedule-search-agent/
├── README.md                   This file / 本说明
├── SKILL.md                    Agent skill definition / Agent 技能定义
├── scripts/
│   ├── msc-auto.cjs            Autonomous query script / 全自动查询脚本
│   └── msc-ports.json          Port mapping database / 港口映射数据库
~~~

## Verified Routes / 已验证航线

### Direct only / 直达航线

| Route / 航线 | Direct Sailings / 直达数 | Notes |
|-------------|:--------------------:|-------|
| Shanghai -> Rotterdam / 上海->鹿特丹 | 10 | Best European route |
| Shanghai -> Hamburg / 上海->汉堡 | 10 | Confirmed Jul 2026 |
| Yantian -> Seattle / 盐田->西雅图 | 9 | Best US West Coast |
| Shanghai -> Santos / 上海->桑托斯 | 8 | Brazil service |
| Shanghai -> Buenos Aires / 上海->布宜诺斯艾利斯 | 7 | Fastest 42 days |

### No MSC service / 无 MSC 服务

- Any CN port -> Busan (釜山): MSC has no direct service
- Shanghai -> Los Angeles (上海->洛杉矶): No MSC service
- Nansha -> Los Angeles (南沙->洛杉矶): No direct
- Dubai / Dammam / Aqaba (迪拜/达曼/亚喀巴): Not in MSC system

## Performance Optimization / 性能优化

| Optimization / 优化项 | Before / 优化前 | After / 优化后 |
|---------------------|:------------:|:-------------:|
| Warmup eval / 热身eval | Required (+2s) | Skipped |
| Autocomplete wait / 下拉等待 | 3.5s | 2.0s |
| Search result wait / 搜索等待 | 10-12s | 5.0s |
| Page reload per route / 每次重载 | Required | Reused (multi-tab) |
| CDP connections / 连接方式 | Per command | Batch mode |

## Technical Deep Dive / 技术要点

### The Cookie Problem / Cookie 弹窗

The MSC site shows a Cookie consent banner on every page load that overlays form elements. The tool auto-detects and dismisses it via text-based button targeting.

### Vue.js Form Challenge / Vue 表单难题

MSC uses Vue.js with reactive forms. Simple DOM value assignment doesn't trigger the framework. Two techniques are used:

1. **xbrowser's `fill` command** -> triggers proper input events
2. **PointerEvent dispatch sequence** -> `pointerdown -> mousedown -> pointerup -> mouseup -> click` (for Vue dropdown)

## WeChat Integration / 微信集成

When integrated with OpenClaw's WeChat channel:

1. Customer sends / 客户发: "查一下上海到汉堡的船期"
2. Agent auto-resolves ports -> queries MSC -> extracts results
3. Agent returns formatted table + screenshot
4. All within WeChat / 全程微信内完成

## License / 许可

MIT - use freely, modify freely, share freely.

---

<p align="center">
  <b>Made with by QClaw Agent</b><br>
  <i>Part of the OpenClaw ecosystem</i>
</p>
