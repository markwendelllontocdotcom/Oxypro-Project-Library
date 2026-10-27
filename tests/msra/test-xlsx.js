// MSRA Log tests: node tests/msra/<file> [planner's MSL .xlsx]. Needs: npm install exceljs@4.4.0 xlsx@0.18.5 jspdf@2.5.1 jspdf-autotable@3.8.4
const A = JSON.parse(require('fs').readFileSync(__dirname + '/../../build/msra-assets.json', 'utf8'));
const fs = require('fs'), XLSX = require('xlsx'), ExcelJS = require('exceljs');
const src = ['core.js', 'xlsx.js'].map(f => fs.readFileSync(__dirname + '/../../src/msra/' + f, 'utf8')).join('\n').replace('__MSRA_STD__', A.std);
const M = new Function('loadScript', 'saveFile', 'MSV', 'msProj', 'msFontsReady', 'MS_LOGO', 'msFileBase', src + '; return { msNewLog, msParseMsl, msMatch, msBuildXlsx, MS_STD, msStandardItems };')();
const p = { no: 'P122', name: 'The Borough', code: 'DXB-243', levels: 'B+G+5P+17F+Roof', area: 'Plot No. JVC17TCP001B, Jumeirah Village Circle, Al Barsha South Fourth, Dubai', client: 'MIRFA | ICONIC', leadConsultant: 'na', mepConsultant: 'Federal Engineering Consultants', mainContractor: 'IndoGulf Contracting Company Llc' };
const log = M.msNewLog(p, 'std');
// an MSL
const wbm = XLSX.read(fs.readFileSync(process.argv[2]), { type: 'buffer', cellDates: true });
const parsed = M.msParseMsl(wbm.SheetNames.map(n => ({ name: n, rows: XLSX.utils.sheet_to_json(wbm.Sheets[n], { header: 1, raw: true, defval: '' }) })));
const byStd = new Map(); for (const r of parsed.items) for (const i of M.msMatch(r).idx) { if (!byStd.has(i)) byStd.set(i, []); byStd.get(i).push(r.k); }
log.items.forEach(it => { it.m = byStd.get(it.x) || []; });
log.msl = { file: 'The Borough_Material_Submittal_Log.xlsx', sheet: parsed.sheets.join(', '), uploaded: '2026-10-27', lagI: 14, lagT: 14, items: parsed.items };
// some statuses and dates
const st = ['A', 'B', 'C', 'UR', 'E', 'n/a', 'D'];
log.items.slice(0, 12).forEach((it, i) => { it.plan = '2026-10-' + String(10 + i).padStart(2, '0'); if (i < 8) { it.sub = '2026-10-' + String(12 + i).padStart(2, '0'); it.ret = '2026-10-' + String(20 + i).padStart(2, '0'); it.st = st[i % 7]; it.fin = st[i % 7]; it.ref = 'OXY-BRH-MS-' + String(i + 1).padStart(3, '0'); it.b = 'U-' + (100 + i); } });
log.items[2].rem = 'Resubmit with the revised duct insulation data sheet and the updated shop drawing reference for the basement extract ducts';
log.items.push({ ...log.items[0], id: 'zz1', d: 'ELE', s: 'I', t: 'Installation of BOH, FOH, Landscape & Façade Light Fixtures incl. Aircraft Warning Lights and Lighting Control Panels for the Podium Levels', m: [], plan: '', sub: '', ret: '', st: '', fin: '', rem: '', x: undefined });
M.msBuildXlsx(ExcelJS, log, p, A.logo).then(buf => { fs.writeFileSync(__dirname + '/test.xlsx', Buffer.from(buf)); console.log('written', buf.byteLength); }).catch(e => { console.error(e); process.exit(1); });
