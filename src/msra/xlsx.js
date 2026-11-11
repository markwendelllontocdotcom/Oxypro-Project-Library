/* ---------- MSRA Log: Excel workbook in the template's layout (ExcelJS) ---------- */
const MS_FONT = 'Calibri';
const MS_LIBS = { exceljs: 'https://cdnjs.cloudflare.com/ajax/libs/exceljs/4.4.0/exceljs.min.js', autotable: 'https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.4/jspdf.plugin.autotable.min.js' };
const MS_ARGB = c => 'FF' + c.replace('#', '').toUpperCase();
const MS_THIN = { style: 'thin', color: { argb: 'FF000000' } };
const MS_BOX = { top: MS_THIN, left: MS_THIN, bottom: MS_THIN, right: MS_THIN };
const msColPx = w => Math.trunc(w * 7 + 5);       // Excel column width (characters of the default Calibri 11) to pixels
let msMctx = null;
function msTextPx(text, pt, bold) {
  if (typeof document === 'undefined') return String(text).length * pt * 96 / 72 * (bold ? 0.6 : 0.56);
  if (!msMctx) msMctx = document.createElement('canvas').getContext('2d');
  msMctx.font = `${bold ? '700 ' : ''}${pt * 96 / 72}px Carlito, Calibri, Arial, sans-serif`;
  return msMctx.measureText(String(text)).width;
}
function msLines(text, pt, px, bold) {
  let n = 0;
  for (const para of String(text || '').split(/\n/)) {
    const words = para.split(/\s+/).filter(Boolean); if (!words.length) { n++; continue; }
    let line = '';
    n++;
    for (const w of words) { const t = line ? line + ' ' + w : w; if (msTextPx(t, pt, bold) <= px || !line) line = t; else { n++; line = w; } }
  }
  return Math.max(1, n);
}
// the rows' fixed 30 pt height, or more when a title or remark needs a third line in Calibri
function msRowPt(it) {
  const lines = Math.max(msLines(it.t, 10, msColPx(70.71) - 8), msLines(it.rem, 10, msColPx(34.29) - 8), msLines(it.ref, 10, msColPx(30.71) - 8), msLines(it.b, 10, msColPx(12.71) - 8));
  return lines <= 2 ? 30 : Math.ceil(lines * 12.75 + 3);
}
const msXDate = iso => { const d = msDay(iso); return d == null ? null : new Date(d * 86400000); };
const msNum = v => /^\d+(\.\d+)?$/.test(String(v).trim()) ? Number(v) : v;
function msF(cell, o) {
  if (o.font) cell.font = { name: MS_FONT, size: 10, color: { argb: 'FF000000' }, ...o.font };
  if (o.fill) cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: MS_ARGB(o.fill) } };
  if (o.al) cell.alignment = o.al;
  if (o.box) cell.border = MS_BOX;
  if (o.fmt) cell.numFmt = o.fmt;
}
function msStatusCF(ws, ref, first) {
  const rules = [['UR', `LEFT(TRIM(${first}),2)="UR"`]].concat(['A', 'B', 'C', 'D', 'E'].map(k => [k, `LEFT(TRIM(${first}),1)="${k}"`])).concat([['n/a', `LOWER(TRIM(${first}))="n/a"`]]);
  ws.addConditionalFormatting({ ref, rules: rules.map(([k, f]) => ({ type: 'expression', formulae: [f], stopIfTrue: true, style: { fill: { type: 'pattern', pattern: 'solid', bgColor: { argb: MS_ARGB(MS_FILL[k]) } }, font: { bold: true, color: { argb: 'FF000000' } } } })) });
}
// Excel's column width (characters) in pixels, as Excel itself counts them (Calibri 11)
const msXPx = w => Math.trunc(((256 * w + 18) / 256) * 7);
const MS_LOG_W = [5.71, 12.71, 70.71, 30.71, 15.71, 15.71, 15.71, 15.71, 15.71, 15.71, 15.71, 15.71, 34.29, 13.71, 9.14, 68.57, 9.14];
// thin outer border round a block of cells, keeping the borders the cells already have
function msBoxRange(ws, r1, c1, r2, c2) {
  for (let r = r1; r <= r2; r++) for (let c = c1; c <= c2; c++) {
    const cell = ws.getCell(r, c), b = { ...(cell.border || {}) };
    if (r === r1) b.top = MS_THIN; if (r === r2) b.bottom = MS_THIN; if (c === c1) b.left = MS_THIN; if (c === c2) b.right = MS_THIN;
    cell.border = b;
  }
}
// an image centred in a box of cells (pixels at 100 %), anchored to the cell its top left corner falls in
function msImageIn(ws, id, w, h, r1, c1, r2, c2, pad) {
  const colPx = c => msXPx(ws.getColumn(c).width || 8.43), rowPx = r => (ws.getRow(r).height || 15) * 4 / 3;
  let bw = 0, bh = 0; for (let c = c1; c <= c2; c++) bw += colPx(c); for (let r = r1; r <= r2; r++) bh += rowPx(r);
  const k = Math.min(1, (bw - 2 * pad) / w, (bh - 2 * pad) / h), W = w * k, H = h * k;
  let x = (bw - W) / 2, y = (bh - H) / 2, c = c1, r = r1;
  while (c < c2 && x >= colPx(c)) { x -= colPx(c); c++; }
  while (r < r2 && y >= rowPx(r)) { y -= rowPx(r); r++; }
  ws.addImage(id, { tl: { nativeCol: c - 1, nativeColOff: Math.round(x * 9525), nativeRow: r - 1, nativeRowOff: Math.round(y * 9525) }, ext: { width: W, height: H }, editAs: 'oneCell' });
}
function msPage(ws, area, titles) {
  ws.pageSetup = { paperSize: 9, orientation: 'landscape', fitToPage: true, fitToWidth: 1, fitToHeight: 0, margins: { left: 0.25, right: 0.25, top: 0.5, bottom: 0.5, header: 0.3, footer: 0.3 }, ...(area ? { printArea: area } : {}), ...(titles ? { printTitlesRow: titles } : {}) };
}
/* one discipline log; returns the rows the summary and the master list point at */
function msXlsxLog(wb, logos, log, d, matText, proj) {
  const ws = wb.addWorksheet(d.code, { views: [{ state: 'frozen', xSplit: 0, ySplit: 12, topLeftCell: 'A13', zoomScale: 85, zoomScaleNormal: 85 }], properties: { outlineLevelCol: 1 } });
  MS_LOG_W.forEach((w, i) => { ws.getColumn(i + 1).width = w; });
  const P = ws.getColumn(16); P.outlineLevel = 1; P.hidden = true;
  for (let r = 1; r <= 11; r++) ws.getRow(r).height = r === 8 ? 5.1 : 20.1;
  ws.getRow(12).height = 30;
  const head = msHeadRows(log, proj);
  // row 1: the project across A:J (white Arial on black) and LEGENDS
  ws.mergeCells('A1:J1'); const t = ws.getCell('A1'); t.value = head.title;
  const troom = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10].reduce((a, c) => a + msXPx(MS_LOG_W[c - 1]), 0) - 16;
  let tsize = 14; while (tsize > 9 && msTextPx(head.title, tsize, true) * 1.08 > troom) tsize -= 0.5;   // Arial runs a little wider than Calibri
  msF(t, { font: { name: 'Arial', size: tsize, bold: true, color: { argb: 'FFFFFFFF' } }, fill: '#000000', al: { horizontal: 'center' } });
  for (let c = 1; c <= 10; c++) { const cell = ws.getCell(1, c); cell.border = { ...(cell.border || {}), bottom: MS_THIN, ...(c === 1 ? { left: MS_THIN } : {}), ...(c === 10 ? { right: MS_THIN } : {}) }; }
  ws.mergeCells('K1:M1'); const lg = ws.getCell('K1'); lg.value = 'LEGENDS'; msF(lg, { font: { size: 12, bold: true }, fill: '#FFFFFF', al: { horizontal: 'center', vertical: 'middle' } });
  msBoxRange(ws, 1, 11, 1, 13);
  // rows 2 to 7: the project block (label in A, ": value" in C), each row boxed
  const vroom = msXPx(70.71) - 10;
  for (let i = 0; i < 6; i++) {
    const r = 2 + i, b = head.rows[i];
    if (b) {
      const a = ws.getCell(r, 1), c = ws.getCell(r, 3); a.value = b.label; c.value = ': ' + b.value;
      let size = 11; while (size > 8 && msTextPx(c.value, size, true) > vroom) size -= 0.5;
      msF(a, { font: { size: 11, bold: true } }); msF(c, { font: { size, bold: true } });
    }
    msBoxRange(ws, r, 1, r, 3);
  }
  // the logo boxes: Client, Consultant, Main Contractor, Subcontractor (names in row 2, logos in rows 3-5), rows 6-7 under them one blank area
  const boxes = [[4, 4], [5, 6], [7, 8], [9, 10]];
  MS_LOGO_BOX.forEach(([k, label], i) => {
    const [c1, c2] = boxes[i];
    if (c2 > c1) ws.mergeCells(2, c1, 2, c2);
    const l = ws.getCell(2, c1); l.value = label; msF(l, { font: { size: 11 }, al: { horizontal: 'center', vertical: 'middle' } });
    ws.mergeCells(3, c1, 5, c2); msF(ws.getCell(3, c1), { al: { horizontal: 'center', vertical: 'middle' } });
    const img = logos[k]; if (img) msImageIn(ws, img.id, img.w, img.h, 3, c1, 5, c2, 6);
  });
  ws.mergeCells(6, 4, 7, 10);
  msBoxRange(ws, 2, 4, 7, 10);
  // the legends: code in K, meaning in L:M
  MS_LEGEND.forEach(([k, txt], i) => {
    const r = 2 + i, c = ws.getCell(r, 11); c.value = k; msF(c, { font: { size: 14, bold: true }, fill: MS_FILL[k], al: { horizontal: 'center', vertical: 'middle' }, box: true });
    ws.mergeCells(r, 12, r, 13); const x = ws.getCell(r, 12); x.value = txt; msF(x, { font: { size: 12 }, al: { horizontal: 'left', vertical: 'middle' } });
    msBoxRange(ws, r, 12, r, 13);
  });
  // rows 9 and 10: date, the log's title and the code counter
  ws.mergeCells('A9:A10'); const da = ws.getCell('A9'); da.value = 'Date:'; msF(da, { font: { size: 11, bold: true }, al: { horizontal: 'center' } });
  ws.mergeCells('B9:B10'); const db = ws.getCell('B9'); db.value = { formula: 'TODAY()', result: new Date(msToday() * 86400000) }; msF(db, { font: { size: 11, bold: true }, al: { horizontal: 'center' }, fmt: '[$-409]d/mmm/yyyy;@' });
  msBoxRange(ws, 9, 1, 10, 2);
  ws.mergeCells('C9:E10'); const lt = ws.getCell('C9'); lt.value = `${d.name} METHOD STATEMENT SUBMITTAL LOG`;
  const lroom = msXPx(70.71) + msXPx(30.71) + msXPx(15.71) - 16; let lsize = 14; while (lsize > 10 && msTextPx(lt.value, lsize, true) > lroom) lsize -= 0.5;
  msF(lt, { font: { size: lsize, bold: true }, al: { horizontal: 'center', vertical: 'middle' } });
  msBoxRange(ws, 9, 3, 10, 5);
  const items = msItemsOf(log, d.code), cnt = msCounts(items);
  const f9 = ws.getCell('F9'); f9.value = 'CODE'; const f10 = ws.getCell('F10'); f10.value = 'Total';
  [f9, f10].forEach(c => msF(c, { font: { size: 14, bold: true }, fill: '#FFFFFF', al: { horizontal: 'center', vertical: 'middle' }, box: true }));
  MS_COUNTED.forEach((k, i) => {
    const h = ws.getCell(9, 7 + i); h.value = k; msF(h, { font: { size: 14, bold: true }, fill: MS_FILL[k], al: { horizontal: 'center', vertical: 'middle' }, box: true });
    const v = ws.getCell(10, 7 + i); v.value = { formula: `COUNTIF($L$15:$L$10000,"${k}")`, result: cnt[k] }; msF(v, { font: { size: 14, bold: true }, fill: '#FFFFFF', al: { horizontal: 'center', vertical: 'middle' }, box: true, fmt: '0' });
  });
  const m9 = ws.getCell('M9'); m9.value = 'TOTAL'; msF(m9, { font: { size: 14, bold: true }, fill: '#FFFFFF', al: { horizontal: 'center', vertical: 'middle' }, box: true });
  const m10 = ws.getCell('M10'); m10.value = { formula: 'SUM(G10:L10)', result: cnt.sub }; msF(m10, { font: { size: 14, bold: true }, fill: '#FFFFFF', al: { horizontal: 'center', vertical: 'middle' }, box: true, fmt: '0' });
  // headers
  const H = ['SN', 'Unifier Ref. Number', 'Method Statement Title', 'Method Statement Reference No.', 'Rev.', 'Discipline', 'Planned Submission Date'];
  H.forEach((h, i) => { ws.mergeCells(11, i + 1, 12, i + 1); ws.getCell(11, i + 1).value = h; });
  ws.mergeCells('H11:K11'); ws.getCell('H11').value = 'Method Statement Status';
  ['Submitted Date', 'Return Date', 'Review Period (in days)', 'Status'].forEach((h, i) => { ws.getCell(12, 8 + i).value = h; });
  ws.mergeCells('L11:L12'); ws.getCell('L11').value = 'Final Status'; ws.mergeCells('M11:M12'); ws.getCell('M11').value = 'Remark';
  for (let r = 11; r <= 12; r++) for (let c = 1; c <= 13; c++) msF(ws.getCell(r, c), { font: { size: r === 12 && c >= 8 && c <= 11 ? 10 : 11, bold: true }, fill: '#F8CBAD', al: { horizontal: 'center', vertical: 'middle', wrapText: true }, box: true });
  if (matText) { const p11 = ws.getCell('P11'); p11.value = "Related Material Submittal(s) [MSL Ref - Item as per Planner's Log]"; msF(p11, { font: { size: 10, bold: true }, fill: '#DDEBF7', al: { vertical: 'middle', wrapText: true } }); const p10 = ws.getCell('P10'); p10.value = 'MATERIAL LINKS - helper column (not printed)'; msF(p10, { font: { size: 11, bold: true }, fill: '#DDEBF7', al: { horizontal: 'center' } }); }
  // banners and items
  const banner = (r, text, fill) => { ws.mergeCells(r, 1, r, 13); const c = ws.getCell(r, 1); c.value = text; msF(c, { font: { size: 11, bold: true }, fill, al: { horizontal: 'center', vertical: 'middle' } }); for (let k = 1; k <= 13; k++) ws.getCell(r, k).border = MS_BOX; ws.getRow(r).height = 30; };
  banner(13, d.name, '#D9D9D9');
  let r = 14, no = 0; const rows = {};
  for (const st of ['I', 'T']) {
    banner(r, MS_STAGE[st], '#FCE4D6'); r++;
    const list = items.filter(it => it.s === st); rows[st] = [r, r + list.length - 1];
    for (const it of list) {
      no++;
      const vals = [no, it.b, it.t, it.ref, msNum(it.rev), d.code, msXDate(it.plan), msXDate(it.sub), msXDate(it.ret), null, it.st, it.fin, it.rem];
      vals.forEach((v, i) => {
        const c = ws.getCell(r, i + 1);
        if (i === 9) c.value = { formula: `IF(OR($H${r}="",$I${r}=""),"",$I${r}-$H${r})`, result: msReview(it) === '' ? '' : msReview(it) };
        else if (v !== '' && v != null) c.value = v;
        const center = ![2, 12].includes(i);
        msF(c, { font: { size: 10, ...(i === 7 || i === 8 ? { color: { argb: 'FF0000FF' } } : {}) }, al: { horizontal: center ? 'center' : undefined, vertical: 'middle', wrapText: true }, box: true, fmt: i >= 6 && i <= 8 ? 'd-mmm-yy' : undefined });
      });
      if (matText) { const c = ws.getCell(r, 16); c.value = matText(it); msF(c, { font: { size: 10, color: { argb: 'FF0000FF' } } }); }
      ws.getRow(r).height = msRowPt(it);
      it._row = r; r++;
    }
  }
  const last = r - 1;
  msStatusCF(ws, 'K15:L10000', 'K15');
  ws.addConditionalFormatting({ ref: 'G15:G500', rules: [
    { type: 'expression', formulae: ['AND(ISNUMBER($G15),$H15="",$G15<TODAY())'], stopIfTrue: true, style: { fill: { type: 'pattern', pattern: 'solid', bgColor: { argb: 'FFFFC7CE' } }, font: { color: { argb: 'FF9C0006' } } } },
    { type: 'expression', formulae: ['AND(ISNUMBER($G15),$H15="",$G15>=TODAY(),$G15-TODAY()<=7)'], stopIfTrue: true, style: { fill: { type: 'pattern', pattern: 'solid', bgColor: { argb: 'FFFFEB9C' } }, font: { color: { argb: 'FF9C5700' } } } }] });
  ws.dataValidations.add(`K15:L${last + 200}`, { type: 'list', allowBlank: true, formulae: ['"A,B,C,D,E,UR,n/a"'], showErrorMessage: true, errorTitle: 'Status', error: 'Choose A, B, C, D, E, UR or n/a' });
  ws.autoFilter = `A12:M${Math.max(last, 13)}`;
  msPage(ws, `A1:M${last}`, '11:12');
  return { last, rows };
}
function msXlsxSummary(ws, logoId, log, info) {
  [5.71, 28.29, 12.57, 12.57, 13.71, 11.43, 11.43, 11.43, 11.43, 11.43, 12.57, 15.71, 30.71].forEach((w, i) => { ws.getColumn(i + 1).width = w; });
  ws.getColumn(3).hidden = true; ws.getColumn(5).hidden = true;
  ws.getRow(1).height = 15.75; ws.getRow(2).height = 15.75;
  const pv = msProjTitle(log);
  const a1 = ws.getCell('A1'); a1.value = `PROJECT : ${pv}`; msF(a1, { font: { size: 12, bold: true } });
  const a2 = ws.getCell('A2'); a2.value = 'METHOD STATEMENT OVERALL SUMMARY'; msF(a2, { font: { size: 12, bold: true } });
  const a3 = ws.getCell('A3'); a3.value = 'DATE:'; msF(a3, { font: { size: 10, bold: true }, al: { horizontal: 'left' } });
  const b3 = ws.getCell('B3'); b3.value = { formula: 'TODAY()', result: new Date(msToday() * 86400000) }; msF(b3, { font: { size: 10, bold: true }, al: { horizontal: 'left' }, fmt: 'd/mmm/yy' });
  const head = ['SN', 'Method Statements', 'Planned MS', 'Total MS', 'MS Submitted', "A' Status", "B' Status", "C' Status", "D' Status", "E' Status", 'Under Review', 'To Be Submitted\n (including resubmissions)', 'Remarks'];
  const table = (top, title, st) => {
    ws.mergeCells(top, 1, top, 13); const b = ws.getCell(top, 1); b.value = title; msF(b, { font: { size: 11, bold: true, color: { argb: 'FFFFFFFF' } }, fill: '#1F4E78', al: { horizontal: 'center' }, box: true });
    for (let c = 1; c <= 13; c++) ws.getCell(top, c).border = MS_BOX;
    head.forEach((h, i) => { ws.mergeCells(top + 1, i + 1, top + 2, i + 1); const c = ws.getCell(top + 1, i + 1); c.value = h; const k = ['A', 'B', 'C', 'D', 'E', 'UR'][i - 5]; msF(c, { font: { size: 11, bold: true }, fill: k ? MS_FILL[k] : '#F8CBAD', al: { horizontal: 'center', vertical: 'middle', wrapText: true }, box: true }); ws.getCell(top + 2, i + 1).border = MS_BOX; });
    ws.getRow(top + 1).height = 21.95; ws.getRow(top + 2).height = 21.95;
    const r0 = top + 3;
    MS_DISC.forEach((d, i) => {
      const r = r0 + i, x = info[d.code], c = msCounts(msItemsOf(log, d.code, st));
      const [a, z] = st ? x.rows[st] : [15, x.last]; const has = z >= a;
      const v = (col, val) => { const cell = ws.getCell(r, col); cell.value = val; msF(cell, { font: { size: 10 }, al: { horizontal: col === 2 ? 'left' : 'center' }, box: true, fmt: col >= 5 && col <= 12 && !st ? '0' : undefined }); };
      v(1, i + 1); v(2, d.sum);
      v(3, { formula: `D${r}`, result: c.total });
      v(4, has ? { formula: `COUNT(${d.code}!A${a}:A${z})`, result: c.total } : 0);
      if (!st) {
        v(5, { formula: `${d.code}!M10`, result: c.sub });
        MS_COUNTED.forEach((k, j) => v(6 + j, { formula: `${d.code}!${'GHIJKL'[j]}10`, result: c[k] }));
        v(12, { formula: `D${r}-(E${r}-(H${r}+I${r}))`, result: c.toSubOverall });
      } else {
        v(5, has ? { formula: `COUNTA(${d.code}!$L$${a}:$L$${z})`, result: c.filled } : 0);
        MS_COUNTED.forEach((k, j) => v(6 + j, has ? { formula: `COUNTIF(${d.code}!$L$${a}:$L$${z},"${k}")`, result: c[k] } : 0));
        v(12, { formula: `(D${r}-E${r})+H${r}+I${r}`, result: c.toSubSection });
      }
      v(13, null);
    });
    const tr = r0 + 7, tot = msCounts(log.items.filter(it => !st || it.s === st));
    ws.mergeCells(tr, 1, tr, 2); const tl = ws.getCell(tr, 1); tl.value = 'TOTAL'; msF(tl, { font: { size: 11, bold: true }, fill: '#D9E1F2', al: { horizontal: 'center' }, box: true }); ws.getCell(tr, 2).border = MS_BOX;
    const res = [tot.total, tot.total, st ? tot.filled : tot.sub, tot.A, tot.B, tot.C, tot.D, tot.E, tot.UR, st ? tot.toSubSection : tot.toSubOverall];
    for (let c = 3; c <= 13; c++) { const cell = ws.getCell(tr, c), L = String.fromCharCode(64 + c), k = ['A', 'B', 'C', 'D', 'E', 'UR'][c - 6]; if (c < 13) cell.value = { formula: `SUM(${L}${r0}:${L}${r0 + 6})`, result: res[c - 3] }; msF(cell, { font: { size: 10, bold: true }, fill: k ? MS_FILL[k] : '#D9E1F2', al: { horizontal: 'center' }, box: true, fmt: !st && c >= 5 && c <= 12 ? '0' : undefined }); }
  };
  table(4, 'OVERALL', ''); table(16, 'INSTALLATION METHOD STATEMENTS', 'I'); table(28, 'TESTING & COMMISSIONING METHOD STATEMENTS', 'T');
  msPage(ws, 'A1:M15');
  ws.addImage(logoId, { tl: { nativeCol: 11, nativeColOff: 198120, nativeRow: 0, nativeRowOff: 0 }, ext: { width: 195.5, height: 57.6 }, editAs: 'oneCell' });
}
function msXlsxMaster(wb, log, info) {
  const ws = wb.addWorksheet('MS Master List', { state: 'hidden', views: [{ state: 'frozen', ySplit: 36, topLeftCell: 'A37' }] });
  [5.71, 10.29, 12.57, 8, 16, 66.29, 27.43, 11.43, 14.86, 14.86, 14.86, 11.43, 10.29, 10.29, 12.71, 12.29, 15.14].forEach((w, i) => { ws.getColumn(i + 1).width = w; });
  ws.getRow(1).height = 15.75; ws.getRow(2).height = 15.75;
  const pv = msProjTitle(log);
  const a1 = ws.getCell('A1'); a1.value = pv; msF(a1, { font: { size: 12, bold: true } });
  const a2 = ws.getCell('A2'); a2.value = 'METHOD STATEMENT MASTER LIST - ALL DISCIPLINES (LIVE-LINKED TO DISCIPLINE LOGS)'; msF(a2, { font: { size: 12, bold: true } });
  const p2 = ws.getCell('P2'); p2.value = 'DATE:'; msF(p2, { font: { size: 10, bold: true } });
  const q2 = ws.getCell('Q2'); q2.value = { formula: 'TODAY()', result: new Date(msToday() * 86400000) }; msF(q2, { font: { size: 10, bold: true }, fmt: 'd/mmm/yy' });
  const NAVY = '#1F4E78', white = { color: { argb: 'FFFFFFFF' } };
  const block = (top, title, stage) => {
    ws.mergeCells(top, 1, top, 17); const b = ws.getCell(top, 1); b.value = title; msF(b, { font: { size: 11, bold: true, ...white }, fill: NAVY, al: { horizontal: 'center', vertical: 'middle', wrapText: true }, box: true });
    const hr = top + 1; ws.getRow(hr).height = 30;
    const heads = ['SN', 'Code', 'Discipline', '', '', '', 'Total MS', 'Submitted', 'A', 'B', 'C', 'D', 'E', 'UR', 'Not Submitted', 'Overdue', '% Approved (A+B)'];
    ws.mergeCells(hr, 3, hr, 6);
    heads.forEach((h, i) => { const c = ws.getCell(hr, i + 1); if (h) c.value = h; const k = ['A', 'B', 'C', 'D', 'E', 'UR'][i - 8]; msF(c, { font: { size: 10, bold: true, ...(k ? {} : white) }, fill: k ? MS_FILL[k] : NAVY, al: { horizontal: 'center', vertical: 'middle', wrapText: true }, box: true }); });
    const crit = stage ? `,$C$37:$C$1000,"${stage}"` : '';
    MS_DISC.forEach((d, i) => {
      const r = hr + 1 + i; ws.mergeCells(r, 3, r, 6);
      const its = msItemsOf(log, d.code, stage === 'Installation' ? 'I' : stage === 'T&C' ? 'T' : ''), c = msCounts(its), prog = its.map(msProgress);
      const set = (col, v, o = {}) => { const cell = ws.getCell(r, col); cell.value = v; msF(cell, { font: { size: col === 3 ? 11 : 10 }, al: { horizontal: col === 3 ? 'left' : 'center' }, box: true, ...o }); };
      set(1, i + 1); set(2, d.code); set(3, d.name); [4, 5, 6].forEach(cc => { ws.getCell(r, cc).border = MS_BOX; });
      set(7, { formula: `COUNTIFS($B$37:$B$1000,$B${r}${crit})`, result: its.length });
      set(8, { formula: `COUNTIFS($B$37:$B$1000,$B${r},$J$37:$J$1000,">0"${crit})`, result: its.filter(it => it.sub).length });
      MS_COUNTED.forEach((k, j) => set(9 + j, { formula: `COUNTIFS($B$37:$B$1000,$B${r},$N$37:$N$1000,"${k}"${crit})`, result: c[k] }));
      set(15, { formula: `COUNTIFS($B$37:$B$1000,$B${r},$P$37:$P$1000,"Not Submitted"${crit})`, result: prog.filter(x => x === 'Not Submitted').length });
      set(16, { formula: `COUNTIFS($B$37:$B$1000,$B${r},$P$37:$P$1000,"Overdue"${crit})`, result: prog.filter(x => x === 'Overdue').length });
      set(17, { formula: `IF(G${r}=0,0,(I${r}+J${r})/G${r})`, result: its.length ? (c.A + c.B) / its.length : 0 }, { fmt: '0.0%' });
    });
    const tr = hr + 8; ws.mergeCells(tr, 1, tr, 6);
    const tl = ws.getCell(tr, 1); tl.value = 'TOTAL'; msF(tl, { font: { size: 11, bold: true }, fill: '#D9E1F2', al: { horizontal: 'center' }, box: true });
    for (let c = 7; c <= 17; c++) {
      const L = String.fromCharCode(64 + c), cell = ws.getCell(tr, c), k = ['A', 'B', 'C', 'D', 'E', 'UR'][c - 9];
      cell.value = c === 17 ? { formula: `IF(G${tr}=0,0,(I${tr}+J${tr})/G${tr})` } : { formula: `SUM(${L}${hr + 1}:${L}${hr + 7})` };
      msF(cell, { font: { size: 10, bold: true }, fill: k ? MS_FILL[k] : '#D9E1F2', al: { horizontal: 'center' }, box: true, fmt: c === 17 ? '0.0%' : undefined });
    }
  };
  block(3, 'OVERALL', ''); block(14, 'INSTALLATION METHOD STATEMENTS', 'Installation'); block(25, 'TESTING & COMMISSIONING METHOD STATEMENTS', 'T&C');
  const LH = ['SN', 'Discipline', 'Stage', 'Log No.', 'Unifier Ref. Number', 'Method Statement Title', 'Method Statement Reference No.', 'Rev.', 'Planned Submission Date', 'Submitted Date', 'Return Date', 'Review Period (days)', 'Status', 'Final Status', 'Remark', 'Progress', 'Link'];
  ws.getRow(36).height = 42;
  LH.forEach((h, i) => { const c = ws.getCell(36, i + 1); c.value = h; msF(c, { font: { size: 10, bold: true, color: { argb: 'FFFFFFFF' } }, fill: NAVY, al: { horizontal: 'center', vertical: 'middle', wrapText: true }, box: true }); });
  let r = 37;
  for (const d of MS_DISC) for (const st of ['I', 'T']) for (const it of msItemsOf(log, d.code, st)) {
    const lr = it._row, L = (col, x) => ({ formula: `IF(${d.code}!${col}${lr}="","",${d.code}!${col}${lr})`, result: x === '' || x == null ? '' : x });
    const vals = [{ formula: 'ROW()-36', result: r - 36 }, d.code, st === 'I' ? 'Installation' : 'T&C', { formula: `${d.code}!A${lr}`, result: null }, L('B', it.b), L('C', it.t), L('D', it.ref), L('E', msNum(it.rev)), L('G', msXDate(it.plan)), L('H', msXDate(it.sub)), L('I', msXDate(it.ret)), L('J', msReview(it)), L('K', it.st), L('L', it.fin), L('M', it.rem),
      { formula: `IF(OR(N${r}="A",N${r}="B"),"Approved",IF(N${r}="E","For Record",IF(N${r}="UR","Under Review",IF(OR(N${r}="C",N${r}="D"),"Resubmission Required",IF(J${r}<>"","Submitted",IF(AND(ISNUMBER(I${r}),I${r}<TODAY()),"Overdue","Not Submitted"))))))`, result: msProgress(it) },
      { formula: `HYPERLINK("#'${d.code}'!A${lr}","Go to ${d.code} row ${lr}")`, result: `Go to ${d.code} row ${lr}` }];
    vals.forEach((v, i) => { const c = ws.getCell(r, i + 1); c.value = v; msF(c, { font: i === 16 ? { size: 10, underline: true, color: { argb: 'FF0563C1' } } : { size: 10 }, al: { horizontal: [5, 14, 16].includes(i) ? undefined : 'center', vertical: 'middle', wrapText: i === 5 }, box: true, fmt: i >= 8 && i <= 10 ? 'd/mmm/yy' : undefined }); });
    ws.getRow(r).height = Math.max(18, Math.ceil(msLines(it.t, 10, msColPx(66.29) - 8) * 13.7 + 3));
    r++;
  }
  const last = Math.max(37, r - 1);
  ws.autoFilter = `A36:Q${last}`;
  msStatusCF(ws, 'M37:N1000', 'M37');
  ws.addConditionalFormatting({ ref: 'P37:P1000', rules: [['Overdue', '#FF0000'], ['Resubmission Required', '#FFC7CE'], ['Under Review', '#FFEB9C'], ['Approved', '#C6EFCE'], ['For Record', '#DDEBF7'], ['Submitted', '#D9E1F2']].map(([t, c]) => ({ type: 'expression', formulae: [`TRIM($P37)="${t}"`], stopIfTrue: true, style: { fill: { type: 'pattern', pattern: 'solid', bgColor: { argb: MS_ARGB(c) } }, font: { bold: true, color: { argb: 'FF000000' } } } })) });
}
function msXlsxMsl(wb, log) {
  const msl = log.msl, ws = wb.addWorksheet('MSL Ref', { state: 'hidden', views: [{ state: 'frozen', ySplit: 8, topLeftCell: 'A9' }] });
  [11.43, 11.43, 10.29, 80, 12.57, 18.29, 12.57, 34.29].forEach((w, i) => { ws.getColumn(i + 1).width = w; });
  const pv = msProjTitle(log);
  const put = (a, v, o) => { const c = ws.getCell(a); c.value = v; msF(c, o || {}); return c; };
  put('A1', 'MATERIAL SUBMITTAL - PLANNED SUBMISSION DATES (BASIS FOR MOS PLANNED DATES)', { font: { size: 12, bold: true } });
  put('A2', pv, { font: { size: 12, bold: true } });
  put('A3', `Source: ${msl.file}${msl.sheet ? ` ('${msl.sheet}')` : ''}, uploaded ${msFmt(msl.uploaded)}. Planned MOS dates are typed in the discipline logs; the Library's "Fill empty planned dates" uses these material dates and the lags below.`);
  put('A4', 'Installation MOS - days after the FIRST related material submittal'); put('F4', msl.lagI, { font: { color: { argb: 'FF0000FF' } }, fill: '#FFFF00', al: { horizontal: 'center' } }); put('G4', 'Default for INSTALLATION method statements - per project allowance');
  put('A5', 'Testing & Commissioning MOS - days after the LAST related material submittal'); put('F5', msl.lagT, { font: { color: { argb: 'FF0000FF' } }, fill: '#FFFF00', al: { horizontal: 'center' } }); put('G5', 'Default for T&C method statements - per project allowance');
  put('A6', 'Planned MOS dates that fall on a Sunday move to the Monday. Column G counts how many MOS rows reference each material - 0 means no MOS covers it.');
  for (const a of ['A3', 'A4', 'A5', 'A6', 'G4', 'G5']) msF(ws.getCell(a), { font: { size: 10 } });
  ws.getRow(1).height = 15.75; ws.getRow(2).height = 15.75; ws.getRow(8).height = 30;
  ['MSL Ref', 'Discipline', 'Planner SN', "Material Item Description (as per Planner's Log)", 'Lead Type', 'Planned Submission Date (Planner)', 'No. of Linked MOS', 'Remarks'].forEach((h, i) => put(ws.getCell(8, i + 1).address, h, { font: { size: 10, bold: true }, fill: '#F8CBAD', al: { horizontal: 'center', vertical: 'middle', wrapText: true }, box: true }));
  const cnt = new Map(); for (const it of log.items) for (const k of it.m) cnt.set(k, (cnt.get(k) || 0) + 1);
  msl.items.forEach((m, i) => {
    const r = 9 + i;
    const vals = [m.k, m.d, msNum(m.sn), m.desc, m.lead, msXDate(m.date), { formula: MS_CODES.map(c => `COUNTIF(${c}!$P$15:$P$500,"*"&$A${r}&"*")`).join('+'), result: cnt.get(m.k) || 0 }, m.rem];
    vals.forEach((v, j) => { const c = ws.getCell(r, j + 1); if (v !== '' && v != null) c.value = v; msF(c, { font: { size: 10 }, al: { horizontal: j === 3 || j === 7 ? undefined : 'center', vertical: 'middle', wrapText: j === 3 }, box: true, fmt: j === 5 ? 'd-mmm-yy' : undefined }); });
  });
  const last = 8 + msl.items.length;
  ws.autoFilter = `A8:H${Math.max(last, 9)}`;
  ws.addConditionalFormatting({ ref: `G9:G${Math.max(last, 9)}`, rules: [{ type: 'cellIs', operator: 'equal', formulae: ['0'], style: { fill: { type: 'pattern', pattern: 'solid', bgColor: { argb: 'FFFFC7CE' } }, font: { bold: true, color: { argb: 'FF9C0006' } } } }] });
}
/* the workbook: Summary, the seven logs, then the hidden MSL Ref and MS Master List (the template's order) */
async function msBuildXlsx(ExcelJS, log, proj, logoB64, company) {
  const wb = new ExcelJS.Workbook();
  wb.creator = 'Oxypro Project Library'; wb.created = new Date(); wb.calcProperties = { fullCalcOnLoad: true };
  const logoId = wb.addImage({ base64: logoB64, extension: 'png' });
  // the sheet heads' logo boxes: the project's client, consultant and main contractor from the library, and Oxypro
  const logos = { oxy: { id: logoId, w: 195.5, h: 57.6 } };
  for (const k of ['client', 'consultant', 'contractor']) { const l = company && company[k]; if (l) logos[k] = { id: wb.addImage({ base64: l.data.split(',')[1], extension: 'png' }), w: l.w, h: l.h }; }
  const summary = wb.addWorksheet('Summary');   // first sheet, filled after the logs so it can point at their rows
  const msl = log.msl, mats = msl ? new Map(msl.items.map(m => [m.k, m.desc])) : null;
  const matText = msl ? it => it.m.map(k => `${k} ${mats.get(k) || ''}`.trim()).join('; ') : null;
  const items = log.items.map(it => ({ ...it }));
  const L = { ...log, items };
  const info = {};
  for (const d of MS_DISC) info[d.code] = msXlsxLog(wb, logos, L, d, matText, proj);
  msXlsxSummary(summary, logoId, L, info);
  if (msl) msXlsxMsl(wb, L);
  msXlsxMaster(wb, L, info);
  wb.views = [{ activeTab: 0, firstSheet: 0, visibility: 'visible' }];
  return wb.xlsx.writeBuffer();
}
async function msSaveXlsx() {
  await msFontsReady();
  await loadScript(MS_LIBS.exceljs);
  const buf = await msBuildXlsx(window.ExcelJS, MSV.log, msProj(), MS_LOGO.split(',')[1], await msLogos(msProj()));
  await saveFile(msFileBase() + '.xlsx', new Blob([buf], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));
}
