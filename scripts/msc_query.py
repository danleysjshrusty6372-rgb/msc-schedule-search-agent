#!/usr/bin/env python3
"""
MSC Shipping Schedule Query Helper for Hermes.

This script provides helper functions for querying MSC schedules
using Hermes browser tools. It's designed to be used within
execute_code() blocks.

Usage in execute_code:
    from msc_query import resolve_port, format_results
    
    port = resolve_port("上海")
    print(port)  # {"name": "上海", "mscName": "SHANGHAI, CHINA", "code": "CNSHA"}
"""

import json
import os

# Port mapping database
PORTS_FILE = os.path.join(os.path.dirname(__file__), '..', 'references', 'msc-ports.json')

def load_ports():
    """Load port mapping from JSON file."""
    with open(PORTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)['ports']

def resolve_port(user_input):
    """
    Resolve user input to MSC port name.
    
    Args:
        user_input: Chinese name, English name, or port code
    Returns:
        dict with name, mscName, code fields, or None if not found
    """
    ports = load_ports()
    user_input = user_input.strip().upper()
    
    for p in ports:
        if (p['mscName'].upper().startswith(user_input) or
            p['name'] == user_input or
            p['code'].upper() == user_input or
            p['mscName'].split(',')[0].upper().startswith(user_input)):
            return p
    
    # Try partial match on mscName
    for p in ports:
        if user_input in p['mscName'].upper():
            return p
    
    return None

def format_results(from_port, to_port, results):
    """
    Format query results into a readable markdown table.
    
    Args:
        from_port: dict with mscName, code
        to_port: dict with mscName, code
        results: list of dicts with dep, arr, type keys
    Returns:
        str: formatted markdown
    """
    lines = []
    lines.append('🚢 **MSC 船期查询结果**')
    lines.append(f'📍 **出发港：** {from_port["mscName"]} ({from_port["code"]})')
    lines.append(f'📍 **目的港：** {to_port["mscName"]} ({to_port["code"]})')
    lines.append('')
    
    if not results:
        lines.append('❌ 该路线暂无 MSC 直达或中转服务。')
        return '\n'.join(lines)
    
    direct = [r for r in results if r.get('type') == 'Direct']
    trans = [r for r in results if r.get('type') == 'Transship']
    
    if direct:
        lines.append('━━━ **直达航线** ━━━')
        lines.append(f'共 **{len(direct)}** 条直达')
        lines.append('')
        lines.append('| # | 离港 | 到港 | 类型 |')
        lines.append('|---|------|------|:----:|')
        for i, d in enumerate(direct, 1):
            lines.append(f'| {i} | {d["dep"]} | {d["arr"]} | ✅直达 |')
    else:
        lines.append('❌ 无直达服务')
    
    if trans:
        lines.append('')
        lines.append('━━━ **中转航线** ━━━')
        lines.append(f'共 **{len(trans)}** 条中转')
        lines.append('')
        lines.append('| # | 离港 | 到港 | 类型 |')
        lines.append('|---|------|------|:----:|')
        for i, d in enumerate(trans, 1):
            lines.append(f'| {i} | {d["dep"]} | {d["arr"]} | 🔄中转 |')
    
    lines.append('')
    if direct:
        lines.append(f'⚡ **最快直达：** {direct[0]["dep"]} → {direct[0]["arr"]}')
    if trans:
        lines.append(f'⚡ **最快含中转：** {trans[0]["dep"]} → {trans[0]["arr"]}')
    
    return '\n'.join(lines)

# JS snippet for extracting results from MSC page
EXTRACT_JS = """
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
"""

# JS snippet for dismissing cookie banner
COOKIE_JS = """
(function(){
  var b = document.querySelectorAll('button');
  for(var i=0; i<b.length; i++){
    if(b[i].textContent.trim().includes('接受') && b[i].textContent.trim().includes('Cookie')){
      b[i].click();
      return true;
    }
  }
  return false;
})()
"""

if __name__ == '__main__':
    # Test port resolution
    test_ports = ['上海', 'SHANGHAI', 'CNSHA', '汉堡', 'HAMBURG', '深圳', '洛杉矶']
    for tp in test_ports:
        result = resolve_port(tp)
        if result:
            print(f'{tp} → {result["mscName"]} ({result["code"]})')
        else:
            print(f'{tp} → ❌ Not found')
