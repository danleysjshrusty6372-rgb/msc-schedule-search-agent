---
name: msc-schedule-search
description: |-
  Automate MSC (Mediterranean Shipping Company) container shipping schedule
  lookups via msccargo.cn — fills port fields, handles autocomplete dropdowns,
  clicks search, and extracts structured results. Supports 30+ ports with
  Chinese name resolution.
version: 2.0.0
platforms: [windows]
metadata:
  hermes:
    tags: [shipping, msc, schedule, browser-automation, logistics]
    category: productivity
---

# MSC Shipping Schedule Search Agent

> **极速船期查询** | 浏览器自动化 | 支持中英文港口名自动解析

## When to use

User wants to query MSC (地中海航运) shipping schedules between two ports —
e.g. "查一下上海到汉堡的船期" or "MSC schedule Shanghai to Rotterdam".

## Prerequisites

- Hermes browser tools available (`browser_navigate`, `browser_click`, `browser_type`, `browser_snapshot`, `browser_console`, `browser_vision`)
- Internet access to `www.msccargo.cn`

## Port name mapping

Always resolve user input to MSC's exact names before filling the form:

| 用户输入 | MSC 识别名称 | 港口代码 |
|---------|------------|:-------:|
| 上海 | `SHANGHAI, CHINA` | CNSHA |
| 宁波 | `NINGBO, CHINA` | CNNGB |
| 深圳/蛇口 | `SHEKOU, CHINA` | CNSHK |
| 青岛 | `QINGDAO, CHINA` | CNTAO |
| 天津 | `TIANJINXINGANG, CHINA` | CNTXG |
| 广州/南沙 | `NANSHA, CHINA` | CNNSA |
| 大连 | `DALIAN, CHINA` | CNDLC |
| 厦门 | `XIAMEN, CHINA` | CNXMN |
| 南京 | `NANJING, CHINA` | CNNKG |
| 福州 | `FUZHOU, CHINA` | CNFOC |
| 盐田 | `YANTIAN, CHINA` | CNYTI |
| 鹿特丹 | `ROTTERDAM, NETHERLANDS` | NLRTM |
| 汉堡 | `HAMBURG, GERMANY` | DEHAM |
| 安特卫普 | `ANTWERP, BELGIUM` | BEANR |
| 勒阿弗尔 | `LE HAVRE, FRANCE` | FRLEH |
| 热那亚 | `GENOA, ITALY` | ITGOA |
| 新加坡 | `SINGAPORE` | SGSIN |
| 釜山 | `BUSAN, KOREA, REPUBLIC OF` | KRPUS |
| 洛杉矶 | `LOS ANGELES, US` | USLAX |
| 长滩 | `LONG BEACH, US` | USLGB |
| 西雅图 | `SEATTLE, US` | USSEA |
| 桑托斯 | `SANTOS, BRAZIL` | BRSSZ |
| 布宜诺斯艾利斯 | `BUENOS AIRES, ARGENTINA` | ARBUE |
| 蒙得维的亚 | `MONTEVIDEO, URUGUAY` | UYMVD |
| 巴拉那瓜 | `PARANAGUA, BRAZIL` | BRPNG |
| 里约热内卢 | `RIO DE JANEIRO, BRAZIL` | BRRIO |
| 维多利亚 | `VITORIA, BRAZIL` | BRVII |
| **冷门偏港（训练新增）：** | | |
| 科佩尔 | `KOPER, SLOVENIA` | SIKOP |
| 雷克索斯 | `LEIXOES, PORTUGAL` | PTLEI |
| 杰恩杰恩 | `DJIBOUTI, DJIBOUTI` | DJJIB |
| 帝力 | `DILI, TIMOR-LESTE` | TLDIL |
| 科林托 | `CORINTO, NICARAGUA` | NICIO |
| 圣洛伦索 | `SAN LORENZO, HONDURAS` | HNSLO |
| 莫因 | `MOIN, COSTA RICA` | CRMOB ⚠️非CRMOI |
| 乔治敦 | `GEORGETOWN, GUYANA` | GYGEO |
| 伊基克 | `IQUIQUE, CHILE` | CLIQQ |
| 圣文森特 | `SAN VICENTE, CHILE` | CLSVE |
| 阿卡胡特拉 | `ACAJUTLA, EL SALVADOR` | SVAQJ |
| 卡贝略 | `PUERTO CABELLO, VENEZUELA` | VEPBL |
| 利蒙 | `PUERTO LIMON, COSTA RICA` | CRLIO |
| 金斯敦 | `KINGSTON, JAMAICA` | JMKIN |
| 科尔特斯 | `PUERTO CORTES, HONDURAS` | HNPCR |
| 圣胡安 | `SAN JUAN, PUERTO RICO` | PRSJU |
| 香港 | `HONG KONG, HONG KONG` | HKHKG |

⚠️ **冷门港口 MSC 代码注意**：以 MSC autocomplete 返回为准，可能与 UN/LOCODE 不同（如盐田 MSC 用 CNYTN 而非 CNYTI，莫因用 CRMOB 而非 CRMOI）。

⚠️ **注意：** 深圳必须用 SHEKOU（蛇口），南沙必须用 NANSHA，MSC 不认 Shenzhen/Guangzhou。洛杉矶完整名是 `LOS ANGELES, UNITED STATES`（USLAX）。

> 📁 完整港口映射见 `references/msc-ports.json`（60+ 港口）。金贝/文塔纳斯/瓦尼莫/奥鲁湾 不在 MSC 服务网络，无法查询。

## ✅ 已验证可用的自动化方式（关键！）

原 skill 的 `xbrowser` 依赖在 Hermes 上不可用。**已重写为纯 CDP（Chrome DevTools Protocol）脚本**并真实跑通，见 `scripts/msc_query_cdp.py`。

**核心发现（务必遵守）：**
1. **MSC 船期表单用的是 Alpine.js（`x-model`），不是 Vue。** JS 合成的 PointerEvent / `.click()` **不会**触发下拉选择。必须用 CDP **真实鼠标事件** `Input.dispatchMouseEvent`（mousePressed/mouseReleased）在选项坐标上点击。
2. **输入必须用 CDP `Input.insertText`**（真实键盘输入）触发 autocomplete 渲染，不能用 `input.value=` 赋值。
3. 每个港口字段填完要 **等待 3.5 秒** 让 autocomplete 下拉渲染。
4. From/To 下拉选项是 `li`，在 `.msc-search-schedule__autocomplete` 容器内。点击前先用 `getBoundingClientRect()` 取选项中心坐标。
5. 页面 URL 加载后会变成 `https://www.msccargo.cn/zh-cn/search-a-schedule`，表单仍正常。

### 启动 CDP 调试 Chrome（Windows）

```bash
# 手动启动带远程调试端口的 headless Chrome
# ⚠️ 必须加 --window-size=1280,900，否则默认 500px 宽度触发移动端布局，
#    From/To 字段位置/结构完全不同，导致字段填充失败(误报"无航线")
CHROME="$LOCALAPPDATA/Google/Chrome/Application/chrome.exe"
"$CHROME" --headless=new --disable-gpu --no-sandbox \
  --window-size=1280,900 \
  --remote-debugging-port=9222 --remote-allow-origins=* \
  --user-data-dir="$TEMP/msc-cdp-profile" about:blank
```

必须加 `--remote-allow-origins=*`，否则 WebSocket 连接被拒（403）。必须加 `--window-size=1280,900`，否则默认 500px 宽度触发移动端布局导致查询失败。

### 运行船期查询

```bash
python scripts/msc_query_cdp.py "上海" "汉堡"
python scripts/msc_query_cdp.py "宁波" "布宜诺斯艾利斯"
```

脚本会自动：解析港口→导航→处理 Cookie→填 From/To→真实鼠标点下拉→点搜索→提取结构化结果（含 Direct/Transship 类型）。

**推荐先启动常驻调试 Chrome**（用 terminal `background=true`，非 Python subprocess），脚本会自动连接：

```bash
CHROME="$LOCALAPPDATA/Google/Chrome/Application/chrome.exe"
"$CHROME" --headless=new --disable-gpu --no-sandbox \
  --window-size=1280,900 \
  --remote-debugging-port=9222 --remote-allow-origins=* \
  --user-data-dir="$TEMP/msc-cdp-profile" about:blank
```

⚠️ **Chrome 启动方式坑**：用 terminal `background=true` 启动常驻 Chrome 已验证可行。**不要**用 Python `subprocess.Popen` 启动——在系统已有大量 chrome 进程时会报 `Multiple targets are not supported in headless mode`。脚本内置的 `ensure_chrome()` 是 fallback，生产环境优先手动起常驻实例。

#### 开发模式 vs 生产模式

- **开发模式（当前默认）**：输出完整过程日志（港口解析、字段点击坐标、搜索状态），便于调试。无需环境变量。
- **生产模式**：仅当部署到其他设备后，设 `MSC_PROD=1` 才只输出最终结果表格，不输出过程日志。

```bash
# 开发模式（当前默认，无需环境变量）
python scripts/msc_query_cdp.py "上海" "汉堡"

# 生产模式（部署到其他设备后启用）
MSC_PROD=1 python scripts/msc_query_cdp.py "上海" "汉堡"
```

批量训练（20 条航线）用 `scripts/msc_train.py`，结果存 `scripts/train_results.json`。

### 若用 Hermes 自带 browser 工具

若 Hermes `browser_*` 工具可用，流程是导航→browser_type 填港口（等待 2-3s）→browser_snapshot 找下拉 li→browser_click 点击。若 browser_type/click 触发不了 Alpine 下拉，**改走上面的 CDP 脚本**（更可靠）。

## 🐛 排错速查表（2026-08 实测经验）

> 这些是实际踩过的坑。遇到问题时先查这里，避免重复调试。

| 症状 | 原因 | 解决 |
|------|------|------|
| **WebSocket 连接 403 Forbidden** | Chrome 未加 `--remote-allow-origins=*` | 启动命令必须带此 flag |
| **所有航线都误报"无航线" / From 字段填充后值空** | Chrome 默认 500px 宽度触发移动端布局，From/To 字段位置结构不同 | 启动 Chrome 必须加 `--window-size=1280,900`，验证 `window.innerWidth > 1000` |
| **Hermes browser_* 报 `Auto-launch failed: Chrome exited early`** | Hermes 浏览器后端无法自动启动 Chrome（gateway 重启后临时浏览器缓存被清） | 手动启动 CDP Chrome（见上文启动命令），`hermes config set browser.cdp_url http://127.0.0.1:9222`，或直接跑 CDP 脚本 |
| **填完港口下拉无反应 / 字段值被清空** | MSC 用 Alpine.js，JS 合成 PointerEvent / `.click()` 不触发 | 必须用 CDP `Input.dispatchMouseEvent`（mousePressed→mouseReleased）真实鼠标点击 |
| **输入"上海"填不进 / 下拉无结果** | 表单期望英文 MSC 名 + 需真实键盘事件 | 用 `Input.insertText` 输入英文名（如 SHANGHAI），等 3.5s |
| **From 字段值变成重复**（如 SHANGHAISHANGHAI） | 上一次残留值未清 | 填前先 `focus()` + `select()` + Delete 清空 |
| **下拉选项抓取到的是导航菜单**（MSC SHANGHAI HEAD OFFICE 等 `msc-navbar__item`） | 头部搜索框也有 `.msc-search-autocomplete` 类，与船期表表单混用 | 必须从 From/To input 的 placeholder 精确定位，再从 input 向上找 `.msc-search-schedule__autocomplete` 容器，取其中的 `li` |
| **搜索按钮 disabled** | From/To 未通过下拉正确选中 | 确认两个字段值都是完整名（含 CHINA/GERMANY + 港口代码），再点搜索 |
| **页面 URL 变了**（`/schedule` → `/search-a-schedule`） | MSC 正常重定向 | 表单仍可用，无需处理 |
| **结果提取为空** | 结果未渲染完（搜索后要等 7-8s） | 点搜索后 `time.sleep(8)` 再提取 |
| **港口匹配错**（如深圳→上海） | 深圳必须用 SHEKOU 而非 Shenzhen | 用 `references/msc-ports.json` 映射，深圳→SHEKOU, CHINA |
| **Chrome 端口被占用 / 连不上** | 残留调试实例 | 用 PowerShell 按 profile 目录杀进程再重启 |
| **pip 装包后仍 ImportError** | 装到了别的解释器 | 用 `python -m pip install`（确保和运行时同一 python） |

### 提速要点（本轮验证）

- **调试 Chrome 常驻**：启动一次 headless Chrome 后保持运行，后续查询无需重启，直接连 9222。
- **`--reuse` 页面复用**：批量/连续查询加 `--reuse` 跳过 reload，复用已加载页面 → 单条从 26.8s 降到 **6.1s**（4.4x 提速）。第一条负责加载页面，后续全部复用。
- **动态等待**：脚本已用轮询替代固定 sleep——autocomplete 下拉出现即点击（0.5s 间隔，最多 6s），搜索结果渲染即提取（最多 12s）。实测冷启动单条约 **13.2s**，reuse 单条 **6.1s**。
- **批量训练**：`python scripts/msc_train.py --reuse` 跑 20 条航线，结果存 `scripts/train_results.json`。
- **解析优先用脚本**：`resolve_port()` 已内置 46+ 港口映射，别手工拼 MSC 名。

### ⚠️ reuse 批量注意事项（训练实测）

- **单条查询 `--reuse` 100% 准确**：多次验证无误差。
- **超长批量（20 条连跑）有偶发竞争**：连续快速连接同一 CDP Chrome 偶发港口填充错位导致误判。已通过 train.py 每条间加 1.5s 间隔缓解，但对**冷门偏港**仍有偶发误报（如南沙→圣洛伦索 reuse 误报 8 中、实为无服务）。
- **权威训练用非 reuse 模式**：`python scripts/msc_train.py`（不带 --reuse）逐条 reload，12s/条，结果最准。reuse 模式（6s/条）适合快速概览。
- **批量后对"无航线"和"纯中转"结果单独复验**：用不带 `--reuse` 的单查确认（脚本"无直达"≠"无航线"，纯中转航线也输出结果）。
- **`--window-size=1280,900` 必须加**：否则 headless Chrome 默认 500px 触发移动端布局，所有航线误报"无航线"。

### 冷门偏港训练集（20 条）权威结果（2026-08 实测）

| # | 航线 | 结果 |
|---|------|------|
| 1 | 上海→科佩尔 | ✅ 9 直达 |
| 2 | 盐田→雷克索斯 | ✅ 8 中转 |
| 3 | 宁波→杰恩杰恩 | ✅ 4 中转 |
| 4 | 蛇口→帝力 | ℹ️ 无 MSC 服务 |
| 5 | 青岛→科林托 | ✅ 8 中转 |
| 6 | 南沙→圣洛伦索 | ℹ️ 无 MSC 服务 |
| 7 | 厦门→莫因 | ✅ 8 中转 |
| 8 | 上海→乔治敦 | ✅ 9 中转 |
| 9 | 天津→伊基克 | ✅ 8 中转 |
| 10 | 盐田→圣文森特 | ✅ 8 直达 |
| 11 | 宁波→阿卡胡特拉 | ✅ 2 中转 |
| 12 | 上海→金贝 | ℹ️ 无 MSC 服务 |
| 13 | 香港→卡贝略 | ✅ 10 中转 |
| 14 | 上海→文塔纳斯 | ℹ️ 无 MSC 服务 |
| 15 | 盐田→利蒙 | ℹ️ 无 MSC 服务 |
| 16 | 宁波→瓦尼莫 | ℹ️ 无 MSC 服务 |
| 17 | 南沙→金斯敦 | ✅ 8 中转 |
| 18 | 青岛→科尔特斯 | ✅ 8 中转 |
| 19 | 厦门→奥鲁湾 | ℹ️ 无 MSC 服务 |
| 20 | 天津→圣胡安 | ✅ 8 中转 |

⚠️ **注意**：金贝、文塔纳斯、瓦尼莫、奥鲁湾 这四个港口 MSC autocomplete 根本搜不到（不在 MSC 服务网络），对应的航线必然无服务。已学到的准确 MSC 名见下文港口映射。

## 港口映射解析（Python 辅助）

`scripts/msc_query.py` 提供港口解析 + 结果格式化辅助函数：

```python
from msc_query import resolve_port, format_results
port = resolve_port("上海")  # → {"name":"上海","mscName":"SHANGHAI, CHINA","code":"CNSHA"}
```

## Workflow

### Step 1: Navigate to MSC schedule page

```
browser_navigate(url="https://www.msccargo.cn/zh-cn/schedule")
```

Wait for page to load. The page uses Vue.js with a form containing From/To fields.

### Step 2: Dismiss Cookie consent banner

After page load, take a snapshot to find the cookie button:

```
browser_snapshot()
```

Look for a button with text "接受所有 Cookie" or similar consent button.
Click it:

```
browser_click(ref="@eN")  // where eN is the cookie accept button ref
```

If no cookie banner appears, skip this step.

### Step 3: Fill "From" port field

Take a snapshot to find the From input field:

```
browser_snapshot()
```

Find the textbox with label containing "From" (role=textbox, name contains "From").
Type the MSC port name (use the **MSC name column**, e.g. "SHANGHAI" or "SHANGHAI, CHINA"):

```
browser_type(ref="@eN", text="SHANGHAI")
```

Wait 2-3 seconds for autocomplete dropdown to appear (Vue.js autocomplete):

```
// Use browser_console to wait
browser_console(expression="await new Promise(r => setTimeout(r, 2500))")
```

Take a snapshot to find the autocomplete dropdown option:

```
browser_snapshot()
```

Look for a button/option containing the port name (e.g. "SHANGHAI" or "SHANGHAI, CHINA").
Click it:

```
browser_click(ref="@eN")  // autocomplete option
```

### Step 4: Fill "To" port field

After selecting From, the To field should become active. Take a snapshot:

```
browser_snapshot()
```

Find the textbox with label containing "To" (role=textbox, name contains "To").
Type the destination port:

```
browser_type(ref="@eN", text="HAMBURG")
```

Wait for autocomplete, then click the dropdown option:

```
browser_console(expression="await new Promise(r => setTimeout(r, 2500))")
browser_snapshot()
browser_click(ref="@eN")  // autocomplete option for To
```

### Step 5: Click Search button

Take a snapshot to find the search button:

```
browser_snapshot()
```

Look for a button with text "搜索船期表" or "Search Schedule".

```
browser_click(ref="@eN")  // search button
```

Wait for results to load (Vue.js rendering, ~5 seconds):

```
browser_console(expression="await new Promise(r => setTimeout(r, 5000))")
```

### Step 6: Extract results

Take a snapshot to read the results:

```
browser_snapshot(full=true)
```

Or use browser_console to extract structured data via JS:

```
browser_console(expression=`
  JSON.stringify(
    Array.from(document.querySelectorAll('[class*=point-to-point-details__result]')).map((r,i) => {
      var h = r.querySelectorAll('.data-heading');
      return {
        n: i+1,
        dep: h[0] ? h[0].textContent.trim() : '',
        arr: h[1] ? h[1].textContent.trim() : '',
        type: r.textContent.includes('直') ? 'Direct' : (r.textContent.includes('中') ? 'Transship' : 'N/A')
      };
    })
  )
`)
```

### Step 7: Format and deliver results

Format as a table:

```
🚢 **MSC 船期查询结果**
📍 **出发港：** SHANGHAI, CHINA (CNSHA)
📍 **目的港：** HAMBURG, GERMANY (DEHAM)

━━━ **直达航线** ━━━
共 **N** 条直达

| # | 离港 | 到港 | 类型 |
|---|------|------|:----:|
| 1 | Jul 10 | Aug 03 | ✅直达 |
```

## Pitfalls

- **Cookie banner blocks interaction:** The cookie consent banner overlays the form. MUST dismiss it before filling fields. If search button is disabled or fields don't respond, the cookie banner is likely still present.
- **Vue.js autocomplete requires wait:** After typing in a port field, wait 2-3 seconds for the Vue autocomplete dropdown. Clicking too early = no dropdown = empty search.
- **Autocomplete click must use correct element:** The autocomplete dropdown is a list of buttons/options. Click the one matching the FULL port name (e.g. "SHANGHAI, CHINA"). Partial matches may select wrong port.
- **MSC website may change:** Selectors and page structure can break. If snapshot doesn't show expected elements, take a `browser_vision` screenshot to inspect visually.
- **Chinese input may not work:** If the user says "上海", resolve to "SHANGHAI" before filling. The form autocomplete expects English MSC names, not Chinese.
- **Search button stays disabled:** This happens when From/To are not properly selected via autocomplete dropdown. Must click the dropdown option, not just type text.
- **Page may need reload:** If the page state is corrupted (e.g. previous failed query), navigate again to start fresh: `browser_navigate(url="https://www.msccargo.cn/zh-cn/schedule")`
- **Vue reactivity:** Do NOT use browser_console to set input values via JS (`input.value = ...`). This doesn't trigger Vue's v-model binding. Always use `browser_type` which fires proper input events.
- **Result extraction CSS selectors:** Results use class `point-to-point-details__result`. Departure/arrival dates are in `.data-heading` elements. Type detection checks for "直" (direct) or "中" (transship) characters.

## Quick reference: full automation in one flow

```python
# Use execute_code to run a Python automation script
# that calls browser tools programmatically
```

See `scripts/msc_query.py` for a ready-to-use Python helper that orchestrates the full query.

## References

- `references/msc-ports.json` — Full port mapping database (46+ ports)
- `scripts/msc_query_cdp.py` — **推荐**：可用的 CDP 自动化查询脚本（真实鼠标点击，已验证；支持 `--reuse` 提速）
- `scripts/msc_query.py` — 港口解析 + 结果格式化辅助函数
- `scripts/msc_train.py` — 批量训练脚本（`--reuse` 模式，20 条航线约 2 分钟）
- `scripts/setup.py` — 换机器一键部署/自检（check/install/test）
- `scripts/msc-auto.cjs` — Original OpenClaw/xbrowser version (reference only, not for Hermes)

## 🔧 换机器部署（打包迁移指南）

本 skill 目录**自包含**，所有运行文件都在 `msc-schedule-search/` 内，直接打包整个目录即可迁移。**不依赖 Hermes 内部任何外部文件。**

### 打包清单（整个目录打包）

```
msc-schedule-search/
├── SKILL.md                    ← skill 定义
├── references/
│   └── msc-ports.json          ← 港口映射（46+ 端口）
└── scripts/
    ├── msc_query_cdp.py        ← 核心查询脚本（主）
    ├── msc_query.py            ← 港口解析/格式化辅助
    ├── msc_train.py            ← 批量训练
    ├── setup.py                ← 一键部署/自检
    ├── msc-auto.cjs            ← 原版参考（可忽略）
    └── train_results.json      ← 训练结果记录
```

### 外部依赖（新机器需准备，不属于 skill 文件）

| 依赖 | 作用 | 安装 |
|------|------|------|
| **Python 3.9+** | 运行脚本 | 系统安装 |
| **websocket-client** (Python 库) | CDP WebSocket 通信 | `python -m pip install websocket-client` |
| **Google Chrome** | 浏览器自动化（headless CDP） | 系统安装 |

### 新机器部署步骤

```bash
# 1. 解压 skill 到 hermes skills 目录
# 2. 一键安装依赖 + 启动常驻 Chrome + 自检
python scripts/setup.py install   # 装 websocket-client + 启动 Chrome
python scripts/setup.py check     # 检查各项就绪
python scripts/setup.py test      # 跑"上海→汉堡"测试航线验证
# 3. 正常查询
python scripts/msc_query_cdp.py "上海" "汉堡"
```

⚠️ **注意**：`setup.py install` 用 `subprocess.Popen` 启动 headless Chrome。若系统已有大量 Chrome 进程导致启动失败（`Multiple targets` 错误），改用 SKILL.md 上文的 terminal `background=true` 命令手动启动常驻 Chrome。
