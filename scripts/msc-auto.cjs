#!/usr/bin/env node
/**
 * MSC Shipping Schedule Query 鈥?Auto Agent
 * 
 * Usage:
 *   node msc-auto.cjs "SHANGHAI" "ROTTERDAM"
 *   node msc-auto.cjs "涓婃捣" "姹夊牎"
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

// 鈹€鈹€鈹€ Config 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
const CONFIG = {
  // xbrowser executable
  xb: path.join(process.env.USERPROFILE, '.qclaw', 'skills', 'xbrowser', 'scripts', 'xb.cjs'),
  // Port mapping
  portsFile: path.join(__dirname, 'msc-ports.json'),
  // MSC URL
  mscUrl: 'https://www.msccargo.cn/zh-cn/schedule',
  // Wait timings (ms) 鈥?tuned for reliability
  waits: {
    afterCookie: 1000,
    autocomplete: 2000,
    afterDropdownClick: 500,
    searchResult: 5000,
  },
  // Browser
  browser: 'default',
};

// 鈹€鈹€鈹€ XB Runner 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
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

// 鈹€鈹€鈹€ Port Resolution 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
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

// 鈹€鈹€鈹€ Cookie Handler 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
function acceptCookies() {
  const r = xb(['eval', `(function(){var b=document.querySelectorAll('button');for(var i=0;i<b.length;i++){if(b[i].textContent.trim()==='鎺ュ彈鎵€鏈?Cookie'){b[i].click();return true}}return false})()`], 10);
  return r?.data?.result?.result === true;
}

// 鈹€鈹€鈹€ Single Route Query 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
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

  // Step 3: Fill From 鈥?wait 鈥?click dropdown
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
      if (v.role === 'button' && v.name.includes('鎼滅储鑸规湡琛?)) searchRef = k;
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

// 鈹€鈹€鈹€ Extract Results 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
function extractResults() {
  const r = xb(['eval', `JSON.stringify(Array.from(document.querySelectorAll('[class*=point-to-point-details__result]')).map((r,i)=>{var h=r.querySelectorAll('.data-heading');return {n:i+1,dep:h[0]?h[0].textContent.trim():'',arr:h[1]?h[1].textContent.trim():'',type:r.textContent.includes('鐩?)?'Direct':(r.textContent.includes('涓?)?'Transship':'N/A')}}))`], 10);
  try {
    const data = JSON.parse(r?.data?.result?.result || '[]');
    return { count: data.length, data };
  } catch (e) {
    return { count: 0, data: [], error: e.message };
  }
}

// 鈹€鈹€鈹€ Screenshot 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
function takeScreenshot(name) {
  const r = xb(['screenshot', '--full'], 15);
  const path_ = r?.data?.result?.path || null;
  return path_;
}

// 鈹€鈹€鈹€ Format Output 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
function formatResults(from, to, result) {
  const lines = [];
  lines.push('馃殺 **MSC 鑸规湡鏌ヨ缁撴灉**');
  lines.push(`馃搷 **鍑哄彂娓細** ${from}`);
  lines.push(`馃搷 **鐩殑娓細** ${to}`);
  lines.push('');

  if (!result || result.count === 0) {
    lines.push('鉂?璇ヨ矾绾挎殏鏃?MSC 鐩磋揪鎴栦腑杞湇鍔°€?);
    return lines.join('\n');
  }

  const direct = result.data.filter(d => d.type === 'Direct');
  const trans = result.data.filter(d => d.type === 'Transship');

  lines.push('鈹佲攣鈹?**鐩磋揪鑸嚎** 鈹佲攣鈹?);
  if (direct.length > 0) {
    lines.push(`鍏?**${direct.length}** 鏉＄洿杈綻);
    lines.push('');
    lines.push('| # | 绂绘腐 | 鍒版腐 | 绫诲瀷 |');
    lines.push('|---|------|------|:----:|');
    direct.forEach(d => lines.push(`| ${d.n} | ${d.dep} | ${d.arr} | 鉁呯洿杈?|`));
  } else {
    lines.push('鉂?鏃犵洿杈炬湇鍔?);
  }

  if (trans.length > 0) {
    lines.push('');
    lines.push('鈹佲攣鈹?**涓浆鑸嚎** 鈹佲攣鈹?);
    lines.push(`鍏?**${trans.length}** 鏉′腑杞琡);
    lines.push('');
    lines.push('| # | 绂绘腐 | 鍒版腐 | 绫诲瀷 |');
    lines.push('|---|------|------|:----:|');
    trans.forEach(d => lines.push(`| ${d.n} | ${d.dep} | ${d.arr} | 馃攧涓浆 |`));
  }

  lines.push('');
  if (direct.length > 0) lines.push(`鈿?**鏈€蹇洿杈撅細** ${direct[0].dep} 鈫?${direct[0].arr}`);
  if (trans.length > 0) lines.push(`鈿?**鏈€蹇惈涓浆锛?* ${trans[0].dep} 鈫?${trans[0].arr}`);

  return lines.join('\n');
}

// 鈹€鈹€鈹€ Main 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
async function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.log(`
馃殺 MSC Shipping Schedule Query 鈥?Auto Agent
Usage:
  node msc-auto.cjs <from_port> <to_port> [options]

Examples:
  node msc-auto.cjs "SHANGHAI" "ROTTERDAM"
  node msc-auto.cjs "涓婃捣" "姹夊牎"
  node msc-auto.cjs "闈掑矝" "娲涙潐鐭?

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

  if (!fromPort) { console.error(`鉂?鏃犳硶瑙ｆ瀽娓彛: ${fromRaw}`); process.exit(1); }
  if (!toPort) { console.error(`鉂?鏃犳硶瑙ｆ瀽娓彛: ${toRaw}`); process.exit(1); }

  console.log(`馃攳 鏌ヨ MSC 鑸规湡锛?{fromPort.mscName} 鈫?${toPort.mscName}`);
  console.log(`   (${fromPort.code} 鈫?${toPort.code})`);

  // Open page if needed
  if (doOpen) {
    console.log('馃搫 鎵撳紑 MSC 椤甸潰...');
    xb(['open', CONFIG.mscUrl], 15);
  }

  // Run query
  console.log('鈴?鏌ヨ涓?..');
  const result = queryRoute(fromPort.mscName, toPort.mscName, tabIdx);

  const output = formatResults(fromPort.mscName, toPort.mscName, result);
  console.log('\n' + output + '\n');

  // Screenshot
  if (doScreenshot) {
    console.log('馃摳 鎴浘...');
    const shot = takeScreenshot();
    if (shot) console.log(`馃搸 鎴浘宸蹭繚瀛? ${shot}`);
  }

  // Save result to workspace
  const ws = process.env.USERPROFILE + '/.qclaw/workspace';
  const ts = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  const fname = `msc-${fromPort.code}-${toPort.code}-${ts}.md`;
  const report = `# MSC 鑸规湡鏌ヨ\n\n${output}\n\n---\n*鏌ヨ鏃堕棿: ${new Date().toISOString()}*\n`;
  fs.writeFileSync(path.join(ws, fname), report, 'utf8');
  console.log(`馃捑 宸蹭繚瀛? ${fname}`);
}

main().catch(e => console.error('鉂?閿欒:', e.message));
