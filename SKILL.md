# 馃殺 MSC 鑸规湡鏌ヨ Agent Skill

> **鏋侀€熻埞鏈熸煡璇?* | 鍩轰簬 xbrowser 娴忚鍣ㄨ嚜鍔ㄥ寲 | 鏀寔鍗曟潯 & 鎵归噺澶歍ab骞惰

## 馃搵 姒傝堪

閫氳繃 MSC 涓浗瀹樼綉 (msccargo.cn) 鏌ヨ浠绘剰涓ょ偣闂寸殑鑸规湡淇℃伅銆傚埄鐢?**xbrowser** 鐨?CDP 娴忚鍣ㄨ嚜鍔ㄥ寲鑳藉姏锛屽疄鐜版瘮鎵嬪姩鎿嶄綔蹇?**5~10 鍊?* 鐨勯珮鏁堟煡璇€?
## 鈿?鎬ц兘鍩哄噯

| 鎸囨爣 | 鏃ф柟妗?(v1) | 鏂版柟妗?(v2) | 鎻愬崌 |
|------|:----------:|:----------:|:----:|
| 鍗曟潯璺嚎 | ~34s | **~14s** | **2.4x** 馃敟 |
| 3 鏉¤矾绾匡紙3 tab 閫愭潯锛?| ~102s | **~42s** | **2.4x** 馃敟 |
| 鐑韩 eval | 鉁?蹇呴』 | 鉂?**璺宠繃** | -2s/鏉?|
| 椤甸潰鍔犺浇 | 姣忔潯閲嶅紑 | **棰勫埗 tab** | -5s/鏉?|
| autocomplete 绛夊緟 | 3.5s | **2.0s** | -1.5s/娆?|
| 鎼滅储缁撴灉绛夊緟 | 10~12s | **5.0s** | -6s/鏉?|

## 馃敡 鎶€鏈師鐞?
### 鏍稿績鍙戠幇

1. **xb `fill` 鍘熺敓瑙﹀彂 Vue 鍝嶅簲寮?* 鈥?鏃犻渶澶嶆潅 eval JS锛寈b 鐨?fill 鍛戒护鐩存帴瑙﹀彂 Vue v-model
2. **xb eval 鏃犻渶鐑韩** 鈥?闀?eval 閰嶅悎 `--timeout 29000` 鐩存帴璺戯紝涓嶉渶瑕佸厛鎵ц鐭?eval
3. **PointerEvent 浠呭湪涓嬫媺鐐瑰嚮鏃堕渶瑕?* 鈥?xb 鐨?`click @ref` 瀵规櫘閫氭寜閽敓鏁堬紝浣?Vue 涓嬫媺鑿滃崟闇€瑕?PointerEvent 搴忓垪
4. **batch 淇濇寔 ref 鏂伴矞** 鈥?`xb run batch "cmd1" "cmd2" ...` 鍦ㄥ悓涓€娆?CDP 杩炴帴涓墽琛岋紝ref 涓嶈繃鏈?5. **椤甸潰鍙鐢?* 鈥?鎼滅储瀹屾垚鍚庡彲鍦ㄥ悓涓€椤甸潰淇敼 From/To 閲嶆柊鏌ワ紝鏃犻渶閲嶆柊鍔犺浇

### 鎿嶄綔鍘熺悊鍥?
```
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?                   MSC 鑸规湡鏌ヨ娴佺▼                        鈹?鈹溾攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹? 1. 馃崻 澶勭悊 Cookie 寮圭獥  (eval)                          鈹?鈹? 2. 鉁忥笍 fill From 瀛楁   鈫?wait 2s 鈫?click 涓嬫媺閫夐」       鈹?鈹? 3. 鉁忥笍 fill To 瀛楁     鈫?wait 2s 鈫?click 涓嬫媺閫夐」       鈹?鈹? 4. 馃攳 click 鎼滅储鎸夐挳   鈫?wait 5s                        鈹?鈹? 5. 馃搳 extract 缁撴灉     鈫?杈撳嚭琛ㄦ牸+鎴浘                   鈹?鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?```

## 馃彈锔?鏋舵瀯鏂规

### 鏂规 A锛氬崟璺嚎鏌ヨ锛堥粯璁わ級

```bash
Step 1: 鎵撳紑椤甸潰锛堜粎棣栨闇€瑕侊級
xb run open "https://www.msccargo.cn/zh-cn/schedule"

Step 2: 澶勭悊 Cookie
xb run eval "(function(){/* 鐐瑰嚮鎺ュ彈鎵€鏈?Cookie */})()"

Step 3: fill From + autocomplete
xb run batch "snapshot" "fill @e33 'SHANGHAI'" "wait 2000" "snapshot" "click @e61"

Step 4: fill To + autocomplete + Search + 绛夊緟缁撴灉
xb run batch "snapshot" "fill @e34 'HAMBURG'" "wait 2000" "snapshot" "click @e61" "wait 500" "snapshot" "click @e16" "wait 5000" "snapshot"

Step 5: 鎻愬彇缁撴灉
xb run eval "JSON.stringify(/* 鎻愬彇缁撴灉 */)"
```

### 鏂规 B锛氬鏉¤矾绾挎壒閲忔煡璇紙棰勫埗澶?tab锛?
```
棰勫紑 3 涓?MSC Tab锛坥pen 脳 3 娆★級鈫?Tab 1 Route A 鈫?Tab 2 Route B 鈫?Tab 3 Route C

姣忎釜 Tab 鐙珛鎵ц鏂规 A 鐨?Step 2~5
鐪佸幓 Step 1 鐨勯〉闈㈠姞杞芥椂闂达紙~5s/tab锛?```

### 鏂规 C锛氫竴鏉?eval 鎵归噺鏌ワ紙绱у噾妯″紡锛?
灏嗗鏉¤矾绾垮悎骞跺湪涓€涓?eval 涓墽琛岋紝鍒╃敤 JS 鍐呴儴 `setTimeout` 鏇夸唬澶氭 xb 璋冪敤銆? 
鈿狅笍 娉ㄦ剰锛氬璺嚎鎬昏鏃堕棿闇€ 鈮?29000ms锛岄€傚悎 2~3 鏉＄煭璺嚎銆?
## 馃寠 娓彛鍚嶇О鏄犲皠

### 涓浗涓昏娓彛

| 鐢ㄦ埛杈撳叆 | MSC 璇嗗埆鍚嶇О | 娓彛浠ｇ爜 | 璇存槑 |
|---------|------------|:-------:|------|
| 涓婃捣 | `SHANGHAI, CHINA` | CNSHA | 鉁?|
| 瀹佹尝 | `NINGBO, CHINA` | CNNGB | 鉁?|
| 娣卞湷 | **`SHEKOU, CHINA`** | CNSHK | 鈿狅笍 涓嶈兘鐢?Shenzhen |
| 闈掑矝 | `QINGDAO, CHINA` | CNTAO | 鉁?|
| 澶╂触 | `TIANJINXINGANG, CHINA` | CNTXG | 鉁?|
| 骞垮窞/鍗楁矙 | **`NANSHA, CHINA`** | CNNSA | 鈿狅笍 涓嶈兘鐢?Guangzhou |
| 澶ц繛 | `DALIAN, CHINA` | CNDLC | 鉁?|
| 鍘﹂棬 | `XIAMEN, CHINA` | CNXMN | 鉁?|
| 鍗椾含 | `NANJING, CHINA` | CNNKG | 鉁?|
| 绂忓窞 | `FUZHOU, CHINA` | CNFOC | 鉁?|
| 鐩愮敯 | `YANTIAN, CHINA` | CNYTI | 鉁?|
| 铔囧彛 | `SHEKOU, CHINA` | CNSHK | 鉁?|

### 鍥介檯涓昏娓彛

| 鐢ㄦ埛杈撳叆 | MSC 璇嗗埆鍚嶇О | 娓彛浠ｇ爜 | 璇存槑 |
|---------|------------|:-------:|------|
| 楣跨壒涓?| `ROTTERDAM, NETHERLANDS` | NLRTM | 鉁?|
| 姹夊牎 | `HAMBURG, GERMANY` | DEHAM | 鉁?|
| 瀹夌壒鍗櫘 | `ANTWERP, BELGIUM` | BEANR | 鉁?|
| 鍕掗樋寮楀皵 | `LE HAVRE, FRANCE` | FRLEH | 鉁?|
| 鐑偅浜?| `GENOA, ITALY` | ITGOA | 鉁?|
| 鏂板姞鍧?| `SINGAPORE` | SGSIN | 鉁?|
| 閲滃北 | `BUSAN, KOREA, REPUBLIC OF` | KRPUS | 鈿狅笍 涓浗鈫掗嚋灞?MSC 鏃犵洿杈?|
| 娲涙潐鐭?| `LOS ANGELES, US` | USLAX | 鈿狅笍 浠呴潚宀涙湁鐩磋揪 |
| 闀挎哗 | `LONG BEACH, US` | USLGB | 鉁?|
| 妗戞墭鏂?| `SANTOS, BRAZIL` | BRSSZ | 鉁?|
| 甯冨疁璇烘柉鑹惧埄鏂?| `BUENOS AIRES, ARGENTINA` | ARBUE | 鉁?|
| 钂欏緱缁寸殑浜?| `MONTEVIDEO, URUGUAY` | UYMVD | 鉁?|
| 宸存媺閭ｇ摐 | `PARANAGUA, BRAZIL` | BRPNG | 鉁?|
| 閲岀害鐑唴鍗?| `RIO DE JANEIRO, BRAZIL` | BRRIO | 鉁?|
| 杩嫓 | `JEBEL ALI, DUBAI` | AEJEA | 鈿狅笍 MSC 鏈壘鍒?|
| 杈炬浖 | `DAMMAM, SAUDI ARABIA` | SADMM | 鈿狅笍 MSC 鏈壘鍒?|
| 浜氬杸宸?| `AQABA, JORDAN` | JOAQB | 鈿狅笍 MSC 鏈壘鍒?|

## 馃洜锔?鎵ц鍛戒护鍙傝€?
### xb 宸ュ叿璺緞

```powershell
$XB = "$env:USERPROFILE\.qclaw\skills\xbrowser\scripts\xb.cjs"
node $XB run --browser default <commands>
```

### 鍛戒护琛屽弬鑰?
| 鍛戒护 | 璇存槑 | 绀轰緥 |
|------|------|------|
| `open <url>` | 鎵撳紑椤甸潰 | `open "https://www.msccargo.cn/zh-cn/schedule"` |
| `tab new <url>` | 鏂版爣绛鹃〉 | `tab new "https://www..."` |
| `tab <n>` | 鍒囨崲鏍囩椤?| `tab 0` |
| `tab` | 鍒楀嚭鎵€鏈夋爣绛鹃〉 | `tab` |
| `close` | 鍏抽棴褰撳墠鏍囩椤?| `close` |
| `snapshot -i -c` | DOM 蹇収 | `snapshot -i -c` |
| `fill @eN <text>` | 濉叆鏂囨湰 | `fill @e33 'SHANGHAI'` |
| `click @eN` | 鐐瑰嚮鍏冪礌 | `click @e61` |
| `wait <ms>` | 绛夊緟姣 | `wait 2000` |
| `eval <js>` | 鎵ц JS | `eval "document.title"` |
| `batch "c1" "c2"` | 椤哄簭鎵ц | 瑙佷笂鏂?|
| `screenshot --full` | 鍏ㄩ〉鎴浘 | `screenshot --full` |

### --timeout 璇存槑

- 鍚?`wait` 鐨勯暱 batch 蹇呴』璁?`--timeout 29000`锛堟渶澶у€硷級
- eval 涔熼』璁撅紙鍚﹀垯 10000ms 榛樿鍙兘瓒呮椂锛?
### Cookie 澶勭悊

```powershell
# 鏂规硶 1锛歺b batch锛堥渶瑕佸厛 snapshot 鎵惧埌 Cookie 鎸夐挳 @e64锛?xb run batch "click @e64" "wait 1000"

# 鏂规硶 2锛歟val锛堟帹鑽愶紝鏇村彲闈狅級
xb run eval "(function(){var b=document.querySelectorAll('button');for(var i=0;i<b.length;i++){if(b[i].textContent.trim()==='鎺ュ彈鎵€鏈?Cookie'){b[i].click();return true}}return false})()"
```

### 鎻愬彇缁撴灉

```javascript
// 缁撴灉瀹瑰櫒閫夋嫨鍣?document.querySelectorAll('[class*=point-to-point-details__result]')

// 姣忔潯缁撴灉瀛楁
result.querySelectorAll('.data-heading')  // 鏃ユ湡銆佽埞鑸剁瓑
result.querySelectorAll('[class*=mobile-title]')  // 瀛楁鏍囩
```

### 鎴浘

```powershell
node $XB run --browser default screenshot --full
Copy-Item "~/.agent-browser/tmp/screenshots/*.png" "workspace/"
```

## 鉁?宸查獙璇佺殑璺嚎璁板綍

鎵€鏈夊凡鏌ヨ璺嚎鐨勫畬鏁磋褰曡 `msc-schedule-records.md`銆?
### 鏃犵洿杈捐矾绾?
| 璺嚎 | 缁撴灉 |
|------|:----:|
| 澶╂触鈫掗嚋灞?| 鉂?鏃犵洿杈?|
| 铔囧彛鈫掗嚋灞?| 鉂?鏃犵洿杈?|
| 涓婃捣鈫掗嚋灞?| 鉂?鏃犵洿杈?|
| 瀹佹尝鈫掗嚋灞?| 鉂?鏃犵洿杈?|
| 鍗楁矙鈫掓礇鏉夌煻 | 鉂?鏃犵洿杈?|
| 澶╂触鈫掓礇鏉夌煻 | 鉂?鏃犵洿杈?|
| 涓婃捣鈫掓礇鏉夌煻 | 鉂?鏃犵洿杈撅紙鏃?MSC 鏈嶅姟锛?|
| 杩嫓/杈炬浖/浜氬杸宸?| 鉂?MSC 绯荤粺鏈壘鍒?|
| 闈掑矝鈫掑竷瀹滆鏂壘鍒╂柉 | 鉂?鏃犵洿杈?|

### 鏈夌洿杈捐矾绾匡紙鐑棬锛?
| 鍑衡啋鍏?| 鐩磋揪鏁?| 澶囨敞 |
|-------|:-----:|------|
| 涓婃捣鈫掗箍鐗逛腹 | **10** 馃敟 | 鏈€浼樻娲茶埅绾?|
| 涓婃捣鈫掓眽鍫?| **10** 馃敟 | 鏈€鏂版煡璇?|
| 鐩愮敯鈫掕タ闆呭浘 | **9** 馃敟 | 缇庤タ鏈€浼?|
| 涓婃捣鈫掓鎵樻柉 | 8 | 鍗楃編宸磋タ |
| 瀹佹尝鈫掑竷瀹滆鏂壘鍒╂柉 | 4 | 鍗楃編闃挎牴寤?|
| 瀹佹尝鈫掗箍鐗逛腹 | 閮ㄥ垎鐩磋揪 | 鍚腑杞?|
| 铔囧彛鈫掕挋寰楃淮鐨勪簹 | 3 | 涔屾媺鍦?|
| 闈掑矝鈫掑反鎷夐偅鐡?| 2 | 宸磋タ |
| 涓婃捣鈫掑竷瀹滆鏂壘鍒╂柉 | 7 | 鏈€蹇?42 澶?|
| 闈掑矝鈫掓礇鏉夌煻 | 閮ㄥ垎鐩磋揪 | 娲涙潐鐭跺敮涓€鐩磋揪 |

## 馃摫 寰俊瀹㈡埛鏌ヨ娴佺▼

褰撶敤鎴烽€氳繃寰俊鏌ヨ鑸规湡鏃讹細

```
1. 瑙ｆ瀽涓や釜娓彛鍚?鈫?鏌ユ槧灏勮〃
2. 鎵ц鏂规 A锛堝崟鏉℃煡璇級
3. 鎴浘缁撴灉椤甸潰
4. 杈撳嚭瀹屾暣琛ㄦ牸锛堢洿杈?涓浆锛屾湁涓浆娓爣娉級
5. 鍙戦€佽〃鏍?鎴浘缁欏鎴?```

### 杈撳嚭妯℃澘

```
馃殺 MSC 鑸规湡鏌ヨ缁撴灉
馃搷 鍑哄彂娓細涓婃捣锛圕NSHA锛?馃搷 鐩殑娓細姹夊牎锛圖EHAM锛?馃搮 鏌ヨ鏃ユ湡锛?026/07/10

鈹佲攣鈹佲攣鈹?鐩磋揪鑸嚎锛堝叡 N 鏉★級鈹佲攣鈹佲攣鈹?| # | 绂绘腐 | 鍒版腐 | 鑸▼ |
|---|------|------|:----:|
| 1 | Jul 10 | Aug 23 | 44澶?|
...

鉂?鏃犵洿杈炬椂锛氳璺嚎鏆傛棤 MSC 鐩磋揪鏈嶅姟
```

## 鈿狅笍 甯歌闂 & 鎺掗殰

### 1. Cookie 寮圭獥闃婚殧
**鐥囩姸**锛氳〃鍗曞瓧娈?fill 鍚庢棤 autocomplete锛孲earch 鎸夐挳涓€鐩?disabled  
**瑙ｅ喅**锛氬厛杩?Cookie 鍐嶆搷浣溿€傛瘡娆￠〉闈?reload 鍚?Cookie 寮圭獥閮戒細閲嶆柊鍑虹幇

### 2. ref 澶辨晥
**鐥囩姸**锛歺b 鎶?"鍏冪礌寮曠敤宸插け鏁?  
**鍘熷洜**锛欴OM 鍙樻洿锛堝 Cookie 寮圭獥娑堝け鍚?ref 閲嶇紪鍙凤級  
**瑙ｅ喅**锛氬湪鍚屼竴涓?batch 涓敤 `snapshot` 鑾峰彇鏈€鏂?ref 鍐嶆搷浣?
### 3. Search 鎸夐挳 disabled
**鍘熷洜**锛欶rom/To 蹇呴』浠庝笅鎷夎彍鍗曢€夋嫨锛屼粎 fill 鏂囨湰涓嶅瑙﹀彂 Vue 鍝嶅簲  
**瑙ｅ喅**锛氱瓑 autocomplete 鍑虹幇鍚庯紝蹇呴』 click 涓嬫媺閫夐」

### 4. eval 瓒呮椂 / Unknown error
**鍘熷洜**锛歟val 榛樿 timeout 10000ms 涓嶅  
**瑙ｅ喅**锛氬姞 `--timeout 29000`

### 5. 闀?eval 鎶?SyntaxError
**鍘熷洜**锛歅owerShell 瑙ｆ瀽鍛戒护鏃跺 `$`銆乣?`銆乣;` 绛夌鍙锋湁姝т箟  
**瑙ｅ喅**锛氱敤 IIFE 鍖呰 `(function(){...})()`锛屾垨鏀圭敤 xb batch 鍒嗘鎵ц

## 馃搨 鏂囦欢缁撴瀯

```
skills/msc-schedule-search/
鈹溾攢鈹€ SKILL.md                      鈫?鏈枃浠?鈹斺攢鈹€ scripts/                      鈫?鑷姩鍖栬剼鏈紙鍙€夛級
    鈹斺攢鈹€ msc-auto.cjs              鈫?涓€鏉″懡浠よ嚜鍔ㄦ煡浠绘剰璺嚎
```

## 馃敆 鐩稿叧璧勬簮

- [MSC 鑸规湡鏌ヨ瀹樼綉](https://www.msccargo.cn/zh-cn/schedule)
- [xbrowser Skill](~/.qclaw/skills/xbrowser/SKILL.md)
- [MSC 鏌ヨ璁板綍](~/.qclaw/workspace/msc-schedule-records.md)
