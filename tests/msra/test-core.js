// MSRA Log tests: node tests/msra/<file> [planner's MSL .xlsx]. Needs: npm install exceljs@4.4.0 xlsx@0.18.5 jspdf@2.5.1 jspdf-autotable@3.8.4
const A = JSON.parse(require('fs').readFileSync(__dirname + '/../../build/msra-assets.json', 'utf8'));
const fs = require('fs'), XLSX = require('xlsx');
const code = fs.readFileSync(__dirname + '/../../src/msra/core.js', 'utf8').replace('__MSRA_STD__', A.std);
const M = new Function(code + '; return { MS_STD, msParseMsl, msMatch, msTitleCase, msTokens, msCounts };')();
function grids(file) {
  const wb = XLSX.read(fs.readFileSync(file), { type: 'buffer', cellDates: true });
  return wb.SheetNames.filter(n => !(wb.Workbook && wb.Workbook.Sheets && (wb.Workbook.Sheets.find(s => s.name === n) || {}).Hidden)).map(n => ({ name: n, rows: XLSX.utils.sheet_to_json(wb.Sheets[n], { header: 1, raw: true, defval: '' }) }));
}
for (const f of process.argv.slice(2)) {
  const g = grids(f); const r = M.msParseMsl(g);
  console.log('###', f, 'sheets', r.sheets, 'items', r.items.length);
  const byD = {}; r.items.forEach(x => byD[x.d] = (byD[x.d] || 0) + 1); console.log(byD);
  let unc = 0;
  for (const x of r.items) {
    const m = M.msMatch(x);
    const titles = m.idx.map(i => M.MS_STD.items[i][1] + ':' + M.MS_STD.items[i][2].slice(0, 50));
    if (!m.idx.length) unc++;
    console.log(x.k.padEnd(7), (x.date || '').padEnd(10), x.desc.slice(0, 50).padEnd(50), m.score.toFixed(2), m.via || '-', '=>', titles.join(' | ').slice(0, 160), x.rem || '');
  }
  console.log('uncovered', unc);
}
