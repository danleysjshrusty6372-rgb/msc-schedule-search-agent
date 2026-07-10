# 🚢 MSC 船期查询 Agent Skill

> **极速船期查询** | 基于 xbrowser 浏览器自动化 | 支持单条 & 批量多Tab并行

## 📋 概述

通过 MSC 中国官网 (msccargo.cn) 查询任意两点间的船期信息。利用 **xbrowser** 的 CDP 浏览器自动化能力，实现比手动操作快 **5~10 倍** 的高效查询。

## ⚡ 性能基准

| 指标 | 旧方案 (v1) | 新方案 (v2) | 提升 |
|------|:----------:|:----------:|:----:|
| 单条路线 | ~34s | **~14s** | **2.4x** 🔥 |
| 3 条路线（3 tab 逐条） | ~102s | **~42s** | **2.4x** 🔥 |
| 热身 eval | ✅ 必须 | ❌ **跳过** | -2s/条 |
| 页面加载 | 每条重开 | **预制 tab** | -5s/条 |
| autocomplete 等待 | 3.5s | **2.0s** | -1.5s/次 |
| 搜索结果等待 | 10~12s | **5.0s** | -6s/条 |

## 🔧 技术原理

### 核心发现

1. **xb `fill` 原生触发 Vue 响应式** — 无需复杂 eval JS，xb 的 fill 命令直接触发 Vue v-model
2. **xb eval 无需热身** — 长 eval 配合 `--timeout 29000` 直接跑，不需要先执行短 eval
3. **PointerEvent 仅在下拉点击时需要** — xb 的 `click @ref` 对普通按钮生效，但 Vue 下拉菜单需要 PointerEvent 序列
4. **batch 保持 ref 新鲜** — `xb run batch "cmd1" "cmd2" ...` 在同一次 CDP 连接中执行，ref 不过期
5. **页面可复用** — 搜索完成后可在同一页面修改 From/To 重新查，无需重新加载

### 操作原理图

```
┌──────────────────────────────────────────────────────────┐
│                    MSC 船期查询流程                        │
├──────────────────────────────────────────────────────────┤
│  1. 🍪 处理 Cookie 弹窗  (eval)                          │
│  2. ✏️ fill From 字段   → wait 2s → click 下拉选项       │
│  3. ✏️ fill To 字段     → wait 2s → click 下拉选项       │
│  4. 🔍 click 搜索按钮   → wait 5s                        │
│  5. 📊 extract 结果     → 输出表格+截图                   │
└──────────────────────────────────────────────────────────┘
```

## 🏗️ 架构方案

### 方案 A：单路线查询（默认）

```bash
Step 1: 打开页面（仅首次需要）
xb run open "https://www.msccargo.cn/zh-cn/schedule"

Step 2: 处理 Cookie
xb run eval "(function(){/* 点击接受所有 Cookie */})()"

Step 3: fill From + autocomplete
xb run batch "snapshot" "fill @e33 'SHANGHAI'" "wait 2000" "snapshot" "click @e61"

Step 4: fill To + autocomplete + Search + 等待结果
xb run batch "snapshot" "fill @e34 'HAMBURG'" "wait 2000" "snapshot" "click @e61" "wait 500" "snapshot" "click @e16" "wait 5000" "snapshot"

Step 5: 提取结果
xb run eval "JSON.stringify(/* 提取结果 */)"
```

### 方案 B：多条路线批量查询（预制多 tab）

```
预开 3 个 MSC Tab（open × 3 次）→ Tab 1 Route A → Tab 2 Route B → Tab 3 Route C

每个 Tab 独立执行方案 A 的 Step 2~5
省去 Step 1 的页面加载时间（~5s/tab）
```

### 方案 C：一条 eval 批量查（紧凑模式）

将多条路线合并在一个 eval 中执行，利用 JS 内部 `setTimeout` 替代多次 xb 调用。  
⚠️ 注意：多路线总计时间需 ≤ 29000ms，适合 2~3 条短路线。

## 🌊 港口名称映射

### 中国主要港口

| 用户输入 | MSC 识别名称 | 港口代码 | 说明 |
|---------|------------|:-------:|------|
| 上海 | `SHANGHAI, CHINA` | CNSHA | ✅ |
| 宁波 | `NINGBO, CHINA` | CNNGB | ✅ |
| 深圳 | **`SHEKOU, CHINA`** | CNSHK | ⚠️ 不能用 Shenzhen |
| 青岛 | `QINGDAO, CHINA` | CNTAO | ✅ |
| 天津 | `TIANJINXINGANG, CHINA` | CNTXG | ✅ |
| 广州/南沙 | **`NANSHA, CHINA`** | CNNSA | ⚠️ 不能用 Guangzhou |
| 大连 | `DALIAN, CHINA` | CNDLC | ✅ |
| 厦门 | `XIAMEN, CHINA` | CNXMN | ✅ |
| 南京 | `NANJING, CHINA` | CNNKG | ✅ |
| 福州 | `FUZHOU, CHINA` | CNFOC | ✅ |
| 盐田 | `YANTIAN, CHINA` | CNYTI | ✅ |
| 蛇口 | `SHEKOU, CHINA` | CNSHK | ✅ |

### 国际主要港口

| 用户输入 | MSC 识别名称 | 港口代码 | 说明 |
|---------|------------|:-------:|------|
| 鹿特丹 | `ROTTERDAM, NETHERLANDS` | NLRTM | ✅ |
| 汉堡 | `HAMBURG, GERMANY` | DEHAM | ✅ |
| 安特卫普 | `ANTWERP, BELGIUM` | BEANR | ✅ |
| 勒阿弗尔 | `LE HAVRE, FRANCE` | FRLEH | ✅ |
| 热那亚 | `GENOA, ITALY` | ITGOA | ✅ |
| 新加坡 | `SINGAPORE` | SGSIN | ✅ |
| 釜山 | `BUSAN, KOREA, REPUBLIC OF` | KRPUS | ⚠️ 中国→釜山 MSC 无直达 |
| 洛杉矶 | `LOS ANGELES, US` | USLAX | ⚠️ 仅青岛有直达 |
| 长滩 | `LONG BEACH, US` | USLGB | ✅ |
| 桑托斯 | `SANTOS, BRAZIL` | BRSSZ | ✅ |
| 布宜诺斯艾利斯 | `BUENOS AIRES, ARGENTINA` | ARBUE | ✅ |
| 蒙得维的亚 | `MONTEVIDEO, URUGUAY` | UYMVD | ✅ |
| 巴拉那瓜 | `PARANAGUA, BRAZIL` | BRPNG | ✅ |
| 里约热内卢 | `RIO DE JANEIRO, BRAZIL` | BRRIO | ✅ |
| 迪拜 | `JEBEL ALI, DUBAI` | AEJEA | ⚠️ MSC 未找到 |
| 达曼 | `DAMMAM, SAUDI ARABIA` | SADMM | ⚠️ MSC 未找到 |
| 亚喀巴 | `AQABA, JORDAN` | JOAQB | ⚠️ MSC 未找到 |

## 🛠️ 执行命令参考

### xb 工具路径

```powershell
$XB = "$env:USERPROFILE\.qclaw\skills\xbrowser\scripts\xb.cjs"
node $XB run --browser default <commands>
```

### 命令行参考

| 命令 | 说明 | 示例 |
|------|------|------|
| `open <url>` | 打开页面 | `open "https://www.msccargo.cn/zh-cn/schedule"` |
| `tab new <url>` | 新标签页 | `tab new "https://www..."` |
| `tab <n>` | 切换标签页 | `tab 0` |
| `tab` | 列出所有标签页 | `tab` |
| `close` | 关闭当前标签页 | `close` |
| `snapshot -i -c` | DOM 快照 | `snapshot -i -c` |
| `fill @eN <text>` | 填入文本 | `fill @e33 'SHANGHAI'` |
| `click @eN` | 点击元素 | `click @e61` |
| `wait <ms>` | 等待毫秒 | `wait 2000` |
| `eval <js>` | 执行 JS | `eval "document.title"` |
| `batch "c1" "c2"` | 顺序执行 | 见上文 |
| `screenshot --full` | 全页截图 | `screenshot --full` |

### --timeout 说明

- 含 `wait` 的长 batch 必须设 `--timeout 29000`（最大值）
- eval 也须设（否则 10000ms 默认可能超时）

### Cookie 处理

```powershell
# 方法 1：xb batch（需要先 snapshot 找到 Cookie 按钮 @e64）
xb run batch "click @e64" "wait 1000"

# 方法 2：eval（推荐，更可靠）
xb run eval "(function(){var b=document.querySelectorAll('button');for(var i=0;i<b.length;i++){if(b[i].textContent.trim()==='接受所有 Cookie'){b[i].click();return true}}return false})()"
```

### 提取结果

```javascript
// 结果容器选择器
document.querySelectorAll('[class*=point-to-point-details__result]')

// 每条结果字段
result.querySelectorAll('.data-heading')  // 日期、船舶等
result.querySelectorAll('[class*=mobile-title]')  // 字段标签
```

### 截图

```powershell
node $XB run --browser default screenshot --full
Copy-Item "~/.agent-browser/tmp/screenshots/*.png" "workspace/"
```

## ✅ 已验证的路线记录

所有已查询路线的完整记录见 `msc-schedule-records.md`。

### 无直达路线

| 路线 | 结果 |
|------|:----:|
| 天津→釜山 | ❌ 无直达 |
| 蛇口→釜山 | ❌ 无直达 |
| 上海→釜山 | ❌ 无直达 |
| 宁波→釜山 | ❌ 无直达 |
| 南沙→洛杉矶 | ❌ 无直达 |
| 天津→洛杉矶 | ❌ 无直达 |
| 上海→洛杉矶 | ❌ 无直达（无 MSC 服务） |
| 迪拜/达曼/亚喀巴 | ❌ MSC 系统未找到 |
| 青岛→布宜诺斯艾利斯 | ❌ 无直达 |

### 有直达路线（热门）

| 出→入 | 直达数 | 备注 |
|-------|:-----:|------|
| 上海→鹿特丹 | **10** 🔥 | 最优欧洲航线 |
| 上海→汉堡 | **10** 🔥 | 最新查询 |
| 盐田→西雅图 | **9** 🔥 | 美西最优 |
| 上海→桑托斯 | 8 | 南美巴西 |
| 宁波→布宜诺斯艾利斯 | 4 | 南美阿根廷 |
| 宁波→鹿特丹 | 部分直达 | 含中转 |
| 蛇口→蒙得维的亚 | 3 | 乌拉圭 |
| 青岛→巴拉那瓜 | 2 | 巴西 |
| 上海→布宜诺斯艾利斯 | 7 | 最快 42 天 |
| 青岛→洛杉矶 | 部分直达 | 洛杉矶唯一直达 |

## 📱 微信客户查询流程

当用户通过微信查询船期时：

```
1. 解析两个港口名 → 查映射表
2. 执行方案 A（单条查询）
3. 截图结果页面
4. 输出完整表格（直达+中转，有中转港标注）
5. 发送表格+截图给客户
```

### 输出模板

```
🚢 MSC 船期查询结果
📍 出发港：上海（CNSHA）
📍 目的港：汉堡（DEHAM）
📅 查询日期：2026/07/10

━━━━━ 直达航线（共 N 条）━━━━━
| # | 离港 | 到港 | 航程 |
|---|------|------|:----:|
| 1 | Jul 10 | Aug 23 | 44天 |
...

❌ 无直达时：该路线暂无 MSC 直达服务
```

## ⚠️ 常见问题 & 排障

### 1. Cookie 弹窗阻隔
**症状**：表单字段 fill 后无 autocomplete，Search 按钮一直 disabled  
**解决**：先过 Cookie 再操作。每次页面 reload 后 Cookie 弹窗都会重新出现

### 2. ref 失效
**症状**：xb 报 "元素引用已失效"  
**原因**：DOM 变更（如 Cookie 弹窗消失后 ref 重编号）  
**解决**：在同一个 batch 中用 `snapshot` 获取最新 ref 再操作

### 3. Search 按钮 disabled
**原因**：From/To 必须从下拉菜单选择，仅 fill 文本不够触发 Vue 响应  
**解决**：等 autocomplete 出现后，必须 click 下拉选项

### 4. eval 超时 / Unknown error
**原因**：eval 默认 timeout 10000ms 不够  
**解决**：加 `--timeout 29000`

### 5. 长 eval 报 SyntaxError
**原因**：PowerShell 解析命令时对 `$`、`?`、`;` 等符号有歧义  
**解决**：用 IIFE 包装 `(function(){...})()`，或改用 xb batch 分段执行

## 📂 文件结构

```
skills/msc-schedule-search/
├── SKILL.md                      ← 本文件
└── scripts/                      ← 自动化脚本（可选）
    └── msc-auto.cjs              ← 一条命令自动查任意路线
```

## 🔗 相关资源

- [MSC 船期查询官网](https://www.msccargo.cn/zh-cn/schedule)
- [xbrowser Skill](~/.qclaw/skills/xbrowser/SKILL.md)
- [MSC 查询记录](~/.qclaw/workspace/msc-schedule-records.md)
