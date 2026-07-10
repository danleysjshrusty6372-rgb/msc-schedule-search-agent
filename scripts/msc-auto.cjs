#!/usr/bin/env node
/**
 * MSC Shipping Schedule Query — Auto Agent
 * 
 * Usage:
 *   node msc-auto.cjs "SHANGHAI" "ROTTERDAM"
 *   node msc-auto.cjs "上海" "汉堡"
 *   node msc-auto.cjs "SHANGHAI" "HAMBURG" --batch 3
 *
 * Features:
 *   - Single or multi-tab batch queries
 *   - Automatic Chinese-to-MSC name resolution via msc-ports.json
 *   - Cookie popup auto-handling
 *   - Full result extraction with screenshot
 *   - WeChat-ready output format
 */

const { execSync, spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// ─── Config ────────────────────────────────────────────
const CONFIG = {
  // xbrowser executable
  xb: path.join(process.env.USERPROFILE, '.qclaw', 'skills', 'xbrowser', 'scripts', 'xb.cjs'),
  // Port mapping
  portsFile: path.join(__dirname, 'msc-ports.json'),
  // MSC URL
  mscUrl: 'https://www.msccargo.cn/zh-cn/schedule',
  // Wait timings (ms) — tuned for reliability
  waits: {
    afterCookie: 1000,
    autocomplete: 2000,
    afterDropdownClick: 500,
    searchResult: 5000,
  },
  // Browser
  browser: 'default',
};

// ─── XB Runner ─────────────────────────────────────────
function xb(args, timeoutSec = 30) {
  const cmd = ['node', CONFIG.xb, 'run', '--browser', CONFIG.browser];
  if (timeoutSec > 10) cmd.push('--timeout', String(timeoutSec * 1000));
  cmd.push(...(typeof args === 'string' ? [args] : args));

  try {
    const r = execSync(cmd.join(' '), { encoding: 'utf8', timeout: timeoutSec * 1000, shell: 'powershell.exe' });
    return JSON.parse(r);
  } catch (e) {
    try { return JSON.parse(e.stdout || '{}'); }
    catch { return { ok: false, error: e.message, stdout: e.stdout }; }
  }
}

// ─── Port Resolution ──────────────────────────────────
const ports = JSON.parse(fs.readFileSync(CONFIG.portsFile, 'utf8')).ports;

function resolvePort(input) {
  input = input.trim();
  // Exact or partial match
  const match = ports.find(p =>
    p.mscName.toUpperCase().includes(input.toUpperCase()) ||
    p.name === input ||
    p.code.toUpperCase() === input.toUpperCase()
  );
  if (match) return match;
  // Try prefix
  const prefixMatch = ports.find(p =>
    p.mscName.split(',')[0].toUpperCase().includes(input.toUpperCase())
  );
  return prefixMatch || null;
}

// ─── Cookie Handler ────────────────────────────────────
function acceptCookies() {
  const r = xb(['eval', `(function(){var b=document.querySelectorAll('button');for(var i=0;i<b.length;i++){if(b[i].textContent.trim()==='接受所有 Cookie'){b[i].click();return true}}return false})()`], 10);
  return r?.data?.result?.result === true;
}

// ─── Single Route Query ────────────────────────────────
function queryRoute(fromMSC, toMSC, tabIndex = null) {
  const wt = CONFIG.waits;

  // Optional tab switch
  if (tabIndex !== null) {
    xb(['tab', String(tabIndex)], 5);
  }

  // Step 1: Accept Cookies
  acceptCookies();
  xb(['wait', String(wt.afterCookie)], 5);

  // Step 2: Get snapshot
  const snap1 = xb(['snapshot', '-i', '-c'], 10);
  if (!snap1?.data?.result?.refs) {
    return { error: 'Failed to get snapshot' };
  }
  const refs1 = snap1.data.result.refs;

  // Determine From field ref (skip "myMSC" button, find the textbox)
  let fromRef = null, toRef = null;
  for (const [k, v] of Object.entries(refs1)) {
    if (v.role === 'textbox' && v.name === 'From (ports or countries)') fromRef = k;
    if (v.role === 'textbox' && v.name === 'To (ports or countries)') toRef = k;
  }
  if (!fromRef) return { error: 'From field not found in snapshot' };

  // Step 3: Fill From — wait — click dropdown
  const b1 = xb(['batch',
    `snapshot -i -c`,
    `fill @${fromRef} '${fromMSC}'`,
    `wait ${wt.autocomplete}`,
    `snapshot -i -c`
  ], 15);

  // Find autocomplete option in the result
  let clickRef = null;
  try {
    const lastSnap = b1?.data?.result?.filter(r => r.command?.[0] === 'snapshot').pop();
    if (lastSnap?.result?.refs) {
      for (const [k, v] of Object.entries(lastSnap.result.refs)) {
        if (v.role === 'button' && v.name.toUpperCase().includes(fromMSC.toUpperCase().split(',')[0].trim())) {
          clickRef = k;
          break;
        }
      }
    }
  } catch (e) { /* skip */ }
  if (!clickRef) return { error: `From autocomplete not found for "${fromMSC}"` };
  xb(['click', `@${clickRef}`], 5);

  // Step 4: Get To field ref and fill
  const snap2 = xb(['snapshot', '-i', '-c'], 10);
  let toRef2 = null;
  try {
    const refs2 = snap2.data.result.refs;
    for (const [k, v] of Object.entries(refs2)) {
      if (v.role === 'textbox' && v.name === 'To (ports or countries)') toRef2 = k;
    }
  } catch (e) { /* skip */ }
  if (!toRef2) return { error: 'To field not found after From selection' };

  const b2 = xb(['batch',
    `snapshot -i -c`,
    `fill @${toRef2} '${toMSC}'`,
    `wait ${wt.autocomplete}`,
    `snapshot -i -c`
  ], 15);

  // Find To autocomplete
  let toClickRef = null;
  try {
    const lastSnap = b2?.data?.result?.filter(r => r.command?.[0] === 'snapshot').pop();
    if (lastSnap?.result?.refs) {
      for (const [k, v] of Object.entries(lastSnap.result.refs)) {
        if (v.role === 'button' && v.name.toUpperCase().includes(toMSC.toUpperCase().split(',')[0].trim())) {
          toClickRef = k;
          break;
        }
      }
    }
  } catch (e) { /* skip */ }
  if (!toClickRef) return { error: `To autocomplete not found for "${toMSC}"` };
  xb(['click', `@${toClickRef}`], 5);

  // Step 5: Find Search button and click
  const snap3 = xb(['snapshot', '-i', '-c'], 10);
  let searchRef = null;
  try {
    const refs3 = snap3.data.result.refs;
    for (const [k, v] of Object.entries(refs3)) {
      if (v.role === 'button' && v.name.includes('搜索船期表')) searchRef = k;
    }
  } catch (e) { /* skip */ }
  if (!searchRef) return { error: 'Search button not found (form may be incomplete)' };

  xb(['batch',
    `click @${searchRef}`,
    `wait ${wt.searchResult}`,
    `snapshot -i -c`
  ], 20);

  // Step 6: Extract results
  return extractResults();
}

// ─── Extract Results ───────────────────────────────────
function extractResults() {
  const r = xb(['eval', `JSON.stringify(Array.from(document.querySelectorAll('[class*=point-to-point-details__result]')).map((r,i)=>{var h=r.querySelectorAll('.data-heading');return {n:i+1,dep:h[0]?h[0].textContent.trim():'',arr:h[1]?h[1].textContent.trim():'',type:r.textContent.includes('直')?'Direct':(r.textContent.includes('中')?'Transship':'N/A')}}))`], 10);
  try {
    const data = JSON.parse(r?.data?.result?.result || '[]');
    return { count: data.length, data };
  } catch (e) {
    return { count: 0, data: [], error: e.message };
  }
}

// ─── Screenshot ────────────────────────────────────────
function takeScreenshot(name) {
  const r = xb(['screenshot', '--full'], 15);
  const path_ = r?.data?.result?.path || null;
  return path_;
}

// ─── Format Output ──────────────────────────────────────
function formatResults(from, to, result) {
  const lines = [];
  lines.push('🚢 **MSC 船期查询结果**');
  lines.push(`📍 **出发港：** ${from}`);
  lines.push(`📍 **目的港：** ${to}`);
  lines.push('');

  if (!result || result.count === 0) {
    lines.push('❌ 该路线暂无 MSC 直达或中转服务。');
    return lines.join('\n');
  }

  const direct = result.data.filter(d => d.type === 'Direct');
  const trans = result.data.filter(d => d.type === 'Transship');

  lines.push('━━━ **直达航线** ━━━');
  if (direct.length > 0) {
    lines.push(`共 **${direct.length}** 条直达`);
    lines.push('');
    lines.push('| # | 离港 | 到港 | 类型 |');
    lines.push('|---|------|------|:----:|');
    direct.forEach(d => lines.push(`| ${d.n} | ${d.dep} | ${d.arr} | ✅直达 |`));
  } else {
    lines.push('❌ 无直达服务');
  }

  if (trans.length > 0) {
    lines.push('');
    lines.push('━━━ **中转航线** ━━━');
    lines.push(`共 **${trans.length}** 条中转`);
    lines.push('');
    lines.push('| # | 离港 | 到港 | 类型 |');
    lines.push('|---|------|------|:----:|');
    trans.forEach(d => lines.push(`| ${d.n} | ${d.dep} | ${d.arr} | 🔄中转 |`));
  }

  lines.push('');
  if (direct.length > 0) lines.push(`⚡ **最快直达：** ${direct[0].dep} → ${direct[0].arr}`);
  if (trans.length > 0) lines.push(`⚡ **最快含中转：** ${trans[0].dep} → ${trans[0].arr}`);

  return lines.join('\n');
}

// ─── Main ──────────────────────────────────────────────
async function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.log(`
🚢 MSC Shipping Schedule Query — Auto Agent
Usage:
  node msc-auto.cjs <from_port> <to_port> [options]

Examples:
  node msc-auto.cjs "SHANGHAI" "ROTTERDAM"
  node msc-auto.cjs "上海" "汉堡"
  node msc-auto.cjs "青岛" "洛杉矶"

Options:
  --screenshot    Take full-page screenshot after query
  --tab N         Use specific browser tab (default: current)
  --open          Open MSC page first (use for fresh session)
`);
    process.exit(0);
  }

  const fromRaw = args[0];
  const toRaw = args[1];
  const doScreenshot = args.includes('--screenshot');
  const tabIdx = args.includes('--tab') ? parseInt(args[args.indexOf('--tab') + 1]) : null;
  const doOpen = args.includes('--open');

  // Resolve ports
  const fromPort = resolvePort(fromRaw);
  const toPort = resolvePort(toRaw);

  if (!fromPort) { console.error(`❌ 无法解析港口: ${fromRaw}`); process.exit(1); }
  if (!toPort) { console.error(`❌ 无法解析港口: ${toRaw}`); process.exit(1); }

  console.log(`🔍 查询 MSC 船期：${fromPort.mscName} → ${toPort.mscName}`);
  console.log(`   (${fromPort.code} → ${toPort.code})`);

  // Open page if needed
  if (doOpen) {
    console.log('📄 打开 MSC 页面...');
    xb(['open', CONFIG.mscUrl], 15);
  }

  // Run query
  console.log('⏳ 查询中...');
  const result = queryRoute(fromPort.mscName, toPort.mscName, tabIdx);

  const output = formatResults(fromPort.mscName, toPort.mscName, result);
  console.log('\n' + output + '\n');

  // Screenshot
  if (doScreenshot) {
    console.log('📸 截图...');
    const shot = takeScreenshot();
    if (shot) console.log(`📎 截图已保存: ${shot}`);
  }

  // Save result to workspace
  const ws = process.env.USERPROFILE + '/.qclaw/workspace';
  const ts = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  const fname = `msc-${fromPort.code}-${toPort.code}-${ts}.md`;
  const report = `# MSC 船期查询\n\n${output}\n\n---\n*查询时间: ${new Date().toISOString()}*\n`;
  fs.writeFileSync(path.join(ws, fname), report, 'utf8');
  console.log(`💾 已保存: ${fname}`);
}

main().catch(e => console.error('❌ 错误:', e.message));
