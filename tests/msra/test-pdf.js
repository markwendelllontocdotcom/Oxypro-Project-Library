// MSRA Log tests: node tests/msra/<file> [planner's MSL .xlsx]. Needs: npm install exceljs@4.4.0 xlsx@0.18.5 jspdf@2.5.1 jspdf-autotable@3.8.4
const A = JSON.parse(require('fs').readFileSync(__dirname + '/../../build/msra-assets.json', 'utf8'));
const fs = require('fs'), XLSX = require('xlsx');
const { jsPDF } = require('jspdf'); const at = require('jspdf-autotable'); (at.applyPlugin || at.default && at.default.applyPlugin || (() => {}))(jsPDF);
const src = ['core.js', 'xlsx.js', 'pdf.js'].map(f => fs.readFileSync(__dirname + '/../../src/msra/' + f, 'utf8')).join('\n').replace('__MSRA_STD__', A.std);
const M = new Function('loadScript', 'saveFile', 'MSV', 'msProj', 'msFontsReady', 'MS_LOGO', 'msFileBase', 'LIBS', 'MS_FONT_B64', 'toast', src + '; return { msNewLog, msParseMsl, msMatch, msBuildPdf };')();
const p = { no: 'P122', name: 'The Borough', code: 'DXB-243', levels: 'B+G+5P+17F+Roof', area: 'Plot No. JVC17TCP001B, Jumeirah Village Circle, Al Barsha South Fourth, Dubai', client: 'MIRFA | ICONIC', leadConsultant: 'na', mepConsultant: 'Federal Engineering Consultants', mainContractor: 'IndoGulf Contracting Company Llc' };
const log = M.msNewLog(p, 'std');
const st = ['A', 'B', 'C', 'UR', 'E', 'n/a', 'D'];
log.items.slice(0, 12).forEach((it, i) => { it.plan = '2026-10-' + String(20 + i).padStart(2, '0'); if (i < 8) { it.sub = '2026-10-' + String(12 + i).padStart(2, '0'); it.ret = '2026-10-' + String(20 + i).padStart(2, '0'); it.st = st[i % 7]; it.fin = st[i % 7]; it.ref = 'OXY-BRH-MS-' + String(i + 1).padStart(3, '0'); it.b = 'U-' + (100 + i); } });
log.items[2].rem = 'Resubmit with the revised duct insulation data sheet and the updated shop drawing reference for the basement extract ducts';
const b64 = f => fs.readFileSync(f).toString('base64');
const doc = M.msBuildPdf(jsPDF, log, p, { r: A.osr, b: A.osb }, 'data:image/png;base64,' + A.logo, '00');
fs.writeFileSync(__dirname + '/test.pdf', Buffer.from(doc.output('arraybuffer')));
console.log('pages', doc.getNumberOfPages());
